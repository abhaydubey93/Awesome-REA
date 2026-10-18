#!/usr/bin/env python3
"""Bounded, data-only checkpoint orchestration for the scheduled README scanner."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time
import zipfile
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from review_pr import parse_json, private_json_locations
from scan_sources import GitHub, QUERIES, load_resume, run_scan
from validate import validate_source_index

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = 'source-scan.yml'
ARTIFACT = 'readme-scan-checkpoint'
MAX_BYTES = 128 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
NEW_SUCCESSES = 300
SCAN_SECONDS = 38 * 60
RECORD_FIELDS = set('archived category classification_origin classification_reference_ids classification_engine_version '
                    'description_capture_policy description_en description_language description_omission description_origin '
                    'description_zh description_zh_status discovery_methods full_name id license matched_queries '
                    'metadata_observed_at name observed_at pushed_at readme_api_url readme_bytes readme_content_git_sha '
                    'readme_git_sha readme_git_sha_matches_content readme_heading_count readme_integrity_review readme_lines '
                    'readme_path readme_sha256 readme_signals readme_url requirements scan_status seed_paper_ids '
                    'seed_paper_references seed_reference_ids stars targets topics updated_at url verification'.split())
FAILURE_FIELDS = set('full_name http_status id observed_at reason scan_status url'.split())
META_FIELDS = set('attempted_readme_scans classification_engine_version classification_policy completed_at current_run '
                  'description_policy discovered_repository_ids failed last_checkpoint_at limitations limits method '
                  'queries readme_heading_count_policy requested_successful_scans resume_history resume_observation_policy '
                  'resume_observations schema_version seed_observations started_at status successful_readme_scans '
                  'target_reached unattempted_candidates unique_repos unique_repos_policy checkpoint_reconciliations'.split())


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def read_snapshot(path):
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError('Checkpoint must be a bounded regular JSON file')
    raw = path.read_bytes()
    document = parse_json(raw.decode('utf-8'))
    if not isinstance(document, dict) or set(document) != {'meta', 'resources', 'failures'}:
        raise ValueError('Checkpoint contains unexpected top-level fields')
    if not isinstance(document['meta'], dict) or set(document['meta']) - META_FIELDS:
        raise ValueError('Checkpoint contains unexpected metadata fields')
    for field, allowed in (('resources', RECORD_FIELDS), ('failures', FAILURE_FIELDS)):
        if not isinstance(document[field], list) or any(not isinstance(row, dict) or set(row) - allowed for row in document[field]):
            raise ValueError('Checkpoint contains unexpected record fields')
    if private_json_locations(document):
        raise ValueError('Checkpoint contains credential-like text or a personal path; values withheld')
    _, fingerprint = load_resume(path)
    if any(type(document['meta'].get(key)) is not int for key in counts(document)):
        raise ValueError('Checkpoint counters must be integers')
    errors = []
    validate_source_index(document, errors, allow_incomplete=True)
    if errors:
        raise ValueError('Checkpoint failed source-index structure validation')
    return document, fingerprint


def known_ids(document):
    return set(document['meta'].get('discovered_repository_ids', ())) | {
        row['id'] for row in document['resources'] + document.get('failures', [])}


def reconcile(canonical, previous, canonical_sha, previous_sha):
    """Keep unique successful evidence and pending identities, without inventing a scan run."""
    if previous is None:
        return copy.deepcopy(canonical), {'mode': 'canonical', 'canonical_sha256': canonical_sha}
    canonical_rows = {r['id']: r for r in canonical['resources'] + canonical.get('failures', [])}
    previous_rows = {r['id']: r for r in previous['resources'] + previous.get('failures', [])}
    all_names = {}
    for row in [*previous_rows.values(), *canonical_rows.values()]:
        name = row['full_name'].casefold()
        if name in all_names and all_names[name] != row['id']:
            raise ValueError('Different repository IDs claim the same name; retain both inputs for review')
        all_names[name] = row['id']
    replaced = [{'id': identifier, 'canonical_record_sha256': digest(canonical_rows[identifier]),
                 'checkpoint_record_sha256': digest(row)} for identifier, row in previous_rows.items()
                if identifier in canonical_rows and canonical_rows[identifier] != row]
    # The published snapshot can fully supersede a checkpoint only if no success or pending ID is lost.
    covered = (known_ids(previous) <= known_ids(canonical)
               and set(previous_rows) <= set(canonical_rows)
               and all(canonical_rows[r['id']]['scan_status'] == 'readme-scanned' for r in previous['resources']))
    if covered:
        return copy.deepcopy(canonical), {
            'mode': 'canonical-covers-checkpoint', 'canonical_sha256': canonical_sha,
            'checkpoint_sha256': previous_sha, 'checkpoint_counts': counts(previous), 'superseded': replaced,
            'checkpoint_observation_counts': {key: len(previous['meta'].get(key, []))
                                              for key in ('queries', 'seed_observations', 'resume_observations')},
            'checkpoint_current_run': previous['meta'].get('current_run')}
    records, failures, names, superseded = [], [], {}, []
    for identifier in dict.fromkeys([*previous_rows, *canonical_rows]):
        old, published = previous_rows.get(identifier), canonical_rows.get(identifier)
        selected = published or old
        if old and published:
            if old['scan_status'] == 'readme-scanned' and published['scan_status'] == 'failed':
                selected = old
            if old != published:
                superseded.append({'id': identifier, 'selected': 'canonical' if selected is published else 'checkpoint',
                                   'canonical_record_sha256': digest(published), 'checkpoint_record_sha256': digest(old),
                                   'canonical_status': published['scan_status'], 'checkpoint_status': old['scan_status']})
        name = selected['full_name'].casefold()
        if name in names and names[name] != identifier:
            raise ValueError('Different repository IDs claim the same name; retain both inputs for review')
        names[name] = identifier
        (records if selected['scan_status'] == 'readme-scanned' else failures).append(copy.deepcopy(selected))
    meta = copy.deepcopy(previous['meta'])
    previous_run = meta.pop('current_run', None)
    # Deduplicate identical observations; retain both histories, including original run IDs.
    for field in ('queries', 'seed_observations', 'resume_observations', 'resume_history'):
        values, seen = [], set()
        for item in previous['meta'].get(field, []) + canonical['meta'].get(field, []):
            fingerprint = digest(item)
            if fingerprint not in seen:
                values.append(copy.deepcopy(item)); seen.add(fingerprint)
        meta[field] = values
    ids = sorted(known_ids(canonical) | known_ids(previous), key=lambda value: int(value[5:]))
    receipt = {'mode': 'union', 'reconciled_at': now(), 'canonical_sha256': canonical_sha,
               'checkpoint_sha256': previous_sha, 'canonical_counts': counts(canonical),
               'checkpoint_counts': counts(previous), 'canonical_current_run': canonical['meta'].get('current_run'),
               'checkpoint_current_run': previous_run, 'superseded': superseded}
    meta.setdefault('checkpoint_reconciliations', []).append(receipt)
    meta.update(discovered_repository_ids=ids, unique_repos=len(ids), successful_readme_scans=len(records),
                failed=len(failures), attempted_readme_scans=len(records) + len(failures),
                unattempted_candidates=len(ids) - len(records) - len(failures),
                requested_successful_scans=len(records), target_reached=True,
                status='in-progress', completed_at=None, last_checkpoint_at=now())
    return {'meta': meta, 'resources': records, 'failures': failures}, receipt


def counts(document):
    return {key: document['meta'][key] for key in ('successful_readme_scans', 'failed', 'attempted_readme_scans',
                                                   'unique_repos', 'unattempted_candidates')}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


class ActionsAPI:
    def __init__(self, repository, token, deadline=None):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid repository identity')
        self.repository, self.token, self.deadline = repository, token, deadline

    def get(self, suffix, *, archive=False):
        remaining = 30 if self.deadline is None else min(30, self.deadline - time.monotonic())
        if remaining <= 0:
            raise ValueError('Checkpoint restore reached its time bound')
        request = Request('https://api.github.com/repos/' + self.repository + '/' + suffix, headers={
            'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Awesome-REA-scheduled-scan'})
        try:
            response = build_opener(NoRedirect()).open(request, timeout=remaining)
        except HTTPError as error:
            location, code = error.headers.get('Location', ''), error.code
            error.close()
            parsed = urlsplit(location)
            trusted_blob = (parsed.hostname or '').endswith(('.blob.core.windows.net', '.actions.githubusercontent.com'))
            if not archive or code not in (301, 302, 303, 307, 308) or parsed.scheme != 'https' or not trusted_blob or parsed.username or parsed.password:
                raise ValueError('GitHub Actions API request failed; response withheld') from None
            # Signed artifact URLs are fetched without the GitHub token and never logged or persisted.
            remaining = 30 if self.deadline is None else min(30, self.deadline - time.monotonic())
            if remaining <= 0:
                raise ValueError('Checkpoint restore reached its time bound')
            response = build_opener(NoRedirect()).open(Request(location), timeout=remaining)
        with response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('GitHub Actions response exceeds the size bound')
        return raw if archive else parse_json(raw.decode('utf-8'))


def select_checkpoint(api, branch, current_run, current_attempt=1):
    workflow = api.get('actions/workflows/' + WORKFLOW)
    workflow_id = workflow['id']
    if not 1 <= current_attempt <= 10:
        raise ValueError('Run-attempt history exceeds the restore bound')
    prior_attempts = [api.get(f'actions/runs/{current_run}/attempts/{attempt}')
                      for attempt in range(current_attempt - 1, 0, -1)]
    for page in range(1, 11):
        response = api.get('actions/workflows/' + WORKFLOW + '/runs?' + urlencode({
            'branch': branch, 'status': 'completed', 'per_page': 100, 'page': page}))
        runs = response['workflow_runs']
        for run in (prior_attempts if page == 1 else []) + runs:
            if ((run.get('id') == current_run and run.get('run_attempt', 0) >= current_attempt)
                    or run.get('status') != 'completed'
                    or run.get('workflow_id') != workflow_id or run.get('head_branch') != branch
                    or run.get('event') not in ('schedule', 'workflow_dispatch')
                    or run.get('head_repository', {}).get('full_name') != api.repository):
                continue
            artifacts = api.get(f"actions/runs/{run['id']}/artifacts?per_page=100")
            matches = [item for item in artifacts['artifacts']
                       if item.get('name') == ARTIFACT + '-' + str(run['run_attempt'])]
            if len(matches) > 1:
                raise ValueError('Ambiguous checkpoint artifacts in a trusted run')
            if not matches:
                continue
            artifact = matches[0]
            if artifact.get('expired') or not 0 < artifact.get('size_in_bytes', 0) <= MAX_BYTES:
                raise ValueError('Latest checkpoint expired or exceeds bounds; inspect before restarting')
            if artifact.get('workflow_run', {}).get('id') != run['id']:
                raise ValueError('Checkpoint artifact is not bound to its selected run')
            return run, artifact
        if len(runs) < 100:
            return None
    raise ValueError('Checkpoint search reached its history bound; inspect before restarting')


def unpack_checkpoint(raw, artifact, run, directory):
    expected = artifact.get('digest', '')
    if expected != 'sha256:' + hashlib.sha256(raw).hexdigest():
        raise ValueError('Artifact archive digest is missing or mismatched')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if len(entries) != 2 or {e.filename for e in entries} != {'checkpoint.json', 'receipt.json'}:
            raise ValueError('Checkpoint archive must contain exactly two named JSON files')
        for entry in entries:
            mode = entry.external_attr >> 16
            bound = MAX_RECEIPT_BYTES if entry.filename == 'receipt.json' else MAX_BYTES
            if (entry.is_dir() or stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0, stat.S_IFREG)
                    or entry.flag_bits & 1 or not 0 < entry.file_size <= bound):
                raise ValueError('Checkpoint archive contains an unsafe or oversized member')
        receipt_raw, snapshot = archive.read('receipt.json'), archive.read('checkpoint.json')
    receipt = parse_json(receipt_raw.decode('utf-8'))
    if (receipt.get('schema_version') != 1 or receipt.get('run_id') != run['id']
            or receipt.get('run_attempt') != run['run_attempt'] or receipt.get('workflow_id') != run['workflow_id']
            or receipt.get('source_commit') != run['head_sha']
            or receipt.get('checkpoint_sha256') != hashlib.sha256(snapshot).hexdigest()):
        raise ValueError('Checkpoint receipt provenance does not match the trusted run')
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'checkpoint.json'
    path.write_bytes(snapshot)
    document, fingerprint = read_snapshot(path)
    if receipt.get('counts') != counts(document):
        raise ValueError('Checkpoint receipt counts do not match the data')
    return document, fingerprint


def scanner_child(seed, output):
    document, fingerprint = read_snapshot(seed)
    token = os.environ.get('GH_TOKEN', '')
    if not token:
        raise ValueError('The ephemeral GitHub token is unavailable')
    args = SimpleNamespace(target=len(document['resources']) + NEW_SUCCESSES, workers=4,
                           requests_per_second=2, max_pages=3, candidate_buffer=50,
                           seed_curated=True, seed_papers=True, queries=QUERIES, output=output)
    return run_scan(GitHub(token, 2), args, document, fingerprint)


def orchestrate(directory):
    started_clock = time.monotonic()
    repository, branch = os.environ['GITHUB_REPOSITORY'], os.environ['DEFAULT_BRANCH']
    if os.environ.get('GITHUB_REF') != 'refs/heads/' + branch:
        raise ValueError('Scheduled scans run only from the default branch')
    run_id, source = int(os.environ['GITHUB_RUN_ID']), os.environ['GITHUB_SHA']
    if not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('Invalid source revision')
    directory.mkdir(parents=True, exist_ok=True)
    receipt = {'schema_version': 1, 'run_id': run_id, 'run_attempt': int(os.environ['GITHUB_RUN_ATTEMPT']), 'source_commit': source,
               'started_at': now(), 'new_success_limit': NEW_SUCCESSES, 'scan_seconds': SCAN_SECONDS}
    canonical, canonical_sha = read_snapshot(ROOT / 'data/source-index.json')
    previous, previous_sha = None, None
    api = ActionsAPI(repository, os.environ['GH_TOKEN'], deadline=started_clock + 180)
    receipt['workflow_id'] = api.get('actions/workflows/' + WORKFLOW)['id']
    selected = select_checkpoint(api, branch, run_id, receipt['run_attempt'])
    if selected:
        run, artifact = selected
        previous, previous_sha = unpack_checkpoint(api.get(f"actions/artifacts/{artifact['id']}/zip", archive=True),
                                                   artifact, run, directory / 'restored')
        receipt['restored_run_id'], receipt['restored_artifact_id'] = run['id'], artifact['id']
    # Inputs are already validated and privacy checked. Preserve both on reconciliation ambiguity.
    try:
        seed, reconciliation = reconcile(canonical, previous, canonical_sha, previous_sha)
    except ValueError:
        write_json(directory / 'review/canonical-input.json', canonical)
        if previous is not None:
            write_json(directory / 'review/previous-input.json', previous)
        raise
    seed_path, checkpoint = directory / 'seed.json', directory / 'checkpoint/checkpoint.json'
    write_json(seed_path, seed)
    seed, _ = read_snapshot(seed_path)
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    # Retain the validated seed even if a runner stops before the child's first atomic save.
    checkpoint.write_bytes(seed_path.read_bytes())
    receipt['reconciliation'], receipt['retained_counts'] = reconciliation, counts(seed)
    child = subprocess.Popen([sys.executable, __file__, '--child', '--seed', str(seed_path), '--output', str(checkpoint)],
                             cwd=ROOT, start_new_session=True)
    try:
        code = child.wait(timeout=max(1, SCAN_SECONDS - (time.monotonic() - started_clock)))
        outcome = 'target-reached' if code == 0 else 'partial'
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL); child.wait()
        outcome, code = 'time-budget', 124
    final, fingerprint = read_snapshot(checkpoint)
    old = {r['id']: r for r in seed['resources'] + seed['failures']}
    new = {r['id']: r for r in final['resources'] + final['failures']}
    if any(new.get(identifier) != value for identifier, value in old.items()) or not known_ids(seed) <= known_ids(final):
        raise ValueError('Scanner changed or lost retained evidence')
    added = len(final['resources']) - len(seed['resources'])
    if not 0 <= added <= NEW_SUCCESSES:
        raise ValueError('Scanner exceeded the new-success bound')
    receipt.update(completed_at=now(), outcome=outcome, scanner_exit_code=code,
                   new_successful_scans=added, counts=counts(final), checkpoint_sha256=fingerprint,
                   target_reached=added == NEW_SUCCESSES)
    write_json(directory / 'checkpoint/receipt.json', receipt)
    if (directory / 'checkpoint/receipt.json').stat().st_size > MAX_RECEIPT_BYTES:
        raise ValueError('Checkpoint receipt exceeds the restore bound')
    write_json(directory / 'summary.json', receipt)
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
        stream.write('checkpoint_ready=true\n')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
        stream.write(f'## Scheduled README discovery\n\nNew successful README reads: **{added} / {NEW_SUCCESSES}**. '
                     f"Retained total: **{len(final['resources'])}**, failures: **{len(final['failures'])}**. "
                     f'Outcome: **{outcome}**.\n\nThe artifact is unreviewed discovery evidence. '
                     'Published catalog and source-index files were not changed.\n')
    return 0 if code == 0 else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / '.cache/scheduled-source-scan')
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--seed', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--output', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        return scanner_child(args.seed, args.output) if args.child else orchestrate(args.directory)
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, RecursionError):
        # Never print exception values from remote JSON, signed URLs, response bodies or credentials.
        print('Scheduled scan stopped: checkpoint, provenance, privacy or API validation failed. No publication was made.', flush=True)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
