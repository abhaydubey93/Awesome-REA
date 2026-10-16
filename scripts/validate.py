#!/usr/bin/env python3
"""Validate catalog data, benchmark snapshots, local Markdown links and generated READMEs."""
import datetime as dt
import html
import ipaddress
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from build_readme import CATEGORIES, RELATIONSHIPS, TARGETS
from catalog import ROOT, RESOURCE_FILES
from localization import read_localizations, validate_localizations
from source_scope import read_scope, validate_scope
from validate_papers import validate_papers


RESOURCE_FIELDS = {
    'id', 'name', 'url', 'category', 'relationship', 'description_en',
    'description_zh', 'evidence_url', 'verified_at', 'verification', 'requirements', 'targets', 'kind',
}
BENCHMARK_FIELDS = {
    'id', 'full_name', 'url', 'category', 'stars', 'stars_display',
    'stars_precision', 'observed_at', 'description_zh', 'mechanisms',
    'evidence_urls', 'license', 'license_notes', 'created_at', 'pushed_at',
    'readme_blob_sha',
}
BENCHMARK_CATEGORIES = {
    'upstream_tool', 'distribution_reference', 'direct_catalog',
    'adjacent_catalog', 'official_skill_reference', 'workflow_product',
    'mature_re_tool', 'agent_re_tool',
}
IGNORED_DIRS = {'.git', 'node_modules', 'dist', 'output', '.cache', '.wrangler', '.venv', 'venv', '__pycache__'}


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def string_list(value):
    return isinstance(value, list) and bool(value) and all(nonempty_string(item) for item in value)


def public_https_error(value):
    """Offline URL-shape check; public reachability is checked separately."""
    if not isinstance(value, str) or any(character.isspace() for character in value):
        return 'must be an HTTPS URL without whitespace'
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        parsed.port
    except ValueError:
        return 'has an invalid URL authority or port'
    if parsed.scheme != 'https' or not host or parsed.username or parsed.password:
        return 'must be a public HTTPS URL without embedded credentials'
    host = host.rstrip('.').lower()
    if host == 'localhost' or host.endswith(('.localhost', '.local', '.internal', '.invalid', '.test', '.example')):
        return 'must not name a local or reserved host'
    try:
        if not ipaddress.ip_address(host).is_global:
            return 'must not use a non-public IP address'
    except ValueError:
        # inet_aton recognizes legacy numeric IPv4 forms without resolving DNS.
        # Reject them even when global so consumers cannot reinterpret the host.
        try:
            socket.inet_aton(host)
        except OSError:
            pass  # An ordinary hostname, rather than a numeric IPv4 literal.
        except ValueError:
            return 'has an invalid hostname'
        else:
            return 'must use canonical dotted-decimal IPv4 notation'
        if '.' not in host:
            return 'must use a public hostname'
    return None


def parse_iso(value, require_time=False):
    if not isinstance(value, str):
        raise ValueError('expected an ISO date or timestamp')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) and not require_time:
        return dt.datetime.combine(dt.date.fromisoformat(value), dt.time(), dt.timezone.utc)
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamps must include a timezone')
    return parsed.astimezone(dt.timezone.utc)


def normalized_url(value):
    parsed = urlsplit(value)
    path = parsed.path.rstrip('/')
    if parsed.hostname and parsed.hostname.lower() == 'github.com':
        parts = path.split('/')
        parts[:3] = [part.lower() for part in parts[:3]]
        path = '/'.join(parts)
    return parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, parsed.fragment


def validate_resources(records, errors):
    ids, urls = set(), set()
    for index, record in enumerate(records):
        where = f'resource[{index}]'
        if not isinstance(record, dict):
            errors.append(f'{where}: must be an object')
            continue
        where = f"resource {record.get('id', index)!r}"
        missing = RESOURCE_FIELDS - record.keys()
        if missing:
            errors.append(f"{where}: missing fields {', '.join(sorted(missing))}")
            continue
        invalid_strings = False
        for field in RESOURCE_FIELDS - {'requirements', 'targets'}:
            if not nonempty_string(record[field]):
                errors.append(f'{where}.{field}: must be a nonempty string')
                invalid_strings = True
        if invalid_strings:
            continue
        if not string_list(record['targets']):
            errors.append(f'{where}.targets: use a nonempty list of target labels')
        elif len(set(record['targets'])) != len(record['targets']) or not set(record['targets']) <= set(TARGETS):
            errors.append(f'{where}.targets: use unique labels from ' + ', '.join(TARGETS))
        identifier = record['id']
        if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier):
            errors.append(f'{where}.id: use a lowercase hyphenated slug')
        elif identifier in ids:
            errors.append(f'{where}: duplicate id')
        else:
            ids.add(identifier)
        for field in ('url', 'evidence_url'):
            problem = public_https_error(record[field])
            if problem:
                errors.append(f'{where}.{field}: {problem}')
        if 'additional_evidence_urls' in record:
            if not string_list(record['additional_evidence_urls']):
                errors.append(f'{where}.additional_evidence_urls: use a nonempty list of source URLs')
            else:
                for evidence in record['additional_evidence_urls']:
                    problem = public_https_error(evidence)
                    if problem:
                        errors.append(f'{where}.additional_evidence_urls: {problem}')
        if public_https_error(record['url']) is None:
            canonical = normalized_url(record['url'])
            if canonical in urls:
                errors.append(f'{where}: duplicate canonical URL')
            urls.add(canonical)
        if record['category'] not in CATEGORIES:
            errors.append(f"{where}: unknown category {record['category']!r}")
        if record['kind'] not in {'project', 'tool', 'integration', 'case-study', 'collection', 'documentation', 'learning-resource', 'research'}:
            errors.append(f"{where}: unknown resource kind {record['kind']!r}")
        if record['relationship'] not in RELATIONSHIPS:
            errors.append(f"{where}: unknown relationship {record['relationship']!r}")
        if record['verification'] != 'source-reviewed':
            errors.append(f'{where}.verification: use source-reviewed; runtime evidence belongs in a lab receipt')
        if not (nonempty_string(record['requirements']) or string_list(record['requirements'])):
            errors.append(f'{where}.requirements: use a nonempty string or list of nonempty strings')
        try:
            reviewed = parse_iso(record['verified_at'])
            if reviewed > dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1):
                errors.append(f'{where}.verified_at: review date is in the future')
        except (ValueError, TypeError):
            errors.append(f'{where}.verified_at: invalid ISO date or timezone-aware timestamp')


def validate_benchmarks(records, errors):
    ids, names, urls = set(), set(), set()
    for index, record in enumerate(records):
        where = f'benchmark[{index}]'
        if not isinstance(record, dict):
            errors.append(f'{where}: must be an object')
            continue
        where = f"benchmark {record.get('full_name', index)!r}"
        missing = BENCHMARK_FIELDS - record.keys()
        if missing:
            errors.append(f"{where}: missing fields {', '.join(sorted(missing))}")
            continue
        identifier = record['id']
        if type(identifier) is not int or identifier <= 0:
            errors.append(f'{where}.id: must be a positive GitHub repository ID')
        elif identifier in ids:
            errors.append(f'{where}: duplicate repository ID')
        else:
            ids.add(identifier)
        name = record['full_name']
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name):
            errors.append(f'{where}.full_name: expected owner/repository')
        elif name.casefold() in names:
            errors.append(f'{where}: duplicate repository name')
        else:
            names.add(name.casefold())
        for field in ('description_zh', 'stars_display', 'license_notes'):
            if not nonempty_string(record[field]):
                errors.append(f'{where}.{field}: must be a nonempty string')
        problem = public_https_error(record['url'])
        if problem:
            errors.append(f'{where}.url: {problem}')
        else:
            canonical = normalized_url(record['url'])
            if canonical in urls:
                errors.append(f'{where}: duplicate canonical URL')
            urls.add(canonical)
            if isinstance(name, str) and record['url'].rstrip('/').casefold() != f'https://github.com/{name}'.casefold():
                errors.append(f'{where}.url: does not match full_name')
        if not isinstance(record['category'], str) or record['category'] not in BENCHMARK_CATEGORIES:
            errors.append(f'{where}: unknown benchmark category')
        if type(record['stars']) is not int or record['stars'] < 0:
            errors.append(f'{where}.stars: must be a nonnegative integer')
        if not isinstance(record['stars_precision'], str) or record['stars_precision'] not in {'exact', 'rounded'}:
            errors.append(f'{where}.stars_precision: expected exact or rounded')
        elif record['stars_precision'] == 'exact' and isinstance(record['stars_display'], str):
            if record['stars_display'].replace(',', '').strip() != str(record['stars']):
                errors.append(f'{where}: exact stars and stars_display disagree')
        elif record['stars_precision'] == 'rounded' and isinstance(record['stars_display'], str):
            if not re.fullmatch(r'\d+(?:\.\d+)?[kKmM]?', record['stars_display'].strip()):
                errors.append(f'{where}: rounded display must be numeric with an optional k or m suffix')
        if not string_list(record['mechanisms']):
            errors.append(f'{where}.mechanisms: expected a nonempty list of strings')
        if not string_list(record['evidence_urls']):
            errors.append(f'{where}.evidence_urls: expected a nonempty list of HTTPS URLs')
        else:
            for url in record['evidence_urls']:
                problem = public_https_error(url)
                if problem:
                    errors.append(f'{where}.evidence_urls: {problem}: {url}')
        if record['license'] is not None and not nonempty_string(record['license']):
            errors.append(f'{where}.license: expected text or null for unknown')
        if not isinstance(record['readme_blob_sha'], str) or not re.fullmatch(r'[0-9a-f]{40}', record['readme_blob_sha']):
            errors.append(f'{where}.readme_blob_sha: expected a 40-character lowercase SHA')
        times = {}
        for field in ('observed_at', 'created_at', 'pushed_at'):
            try:
                times[field] = parse_iso(record[field], require_time=True)
            except (ValueError, TypeError):
                errors.append(f'{where}.{field}: invalid timezone-aware ISO timestamp')
        if len(times) == 3:
            if not times['created_at'] <= times['pushed_at'] <= times['observed_at']:
                errors.append(f'{where}: timestamps must satisfy created_at <= pushed_at <= observed_at')
            if times['observed_at'] > dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1):
                errors.append(f'{where}.observed_at: snapshot is in the future')


def validate_source_index(document, errors):
    if not isinstance(document, dict) or not isinstance(document.get('meta'), dict) or not isinstance(document.get('resources'), list):
        errors.append('Source index must contain meta and resources.')
        return 0
    meta, records = document['meta'], document['resources']
    if meta.get('status') != 'complete':
        errors.append('Source index is an incomplete checkpoint; finish the scan before publication.')
    if meta.get('successful_readme_scans') != len(records) or len(records) <= 1500:
        errors.append('Source index must retain more than 1,500 successful scans and matching counts.')
    failures = document.get('failures', [])
    if not isinstance(failures, list):
        errors.append('Source index failures must be an array.')
        failures = []
    if meta.get('failed') != len(failures):
        errors.append('Source index failure count does not match the recorded failures.')
    if meta.get('attempted_readme_scans') != len(records) + len(failures):
        errors.append('Source index attempted count must equal successful plus failed scans.')
    ids, urls, names = set(), set(), set()
    for index, record in enumerate(records):
        where = f'source index record {index}'
        if not isinstance(record, dict):
            errors.append(f'{where}: expected an object')
            continue
        for field, seen in [('id', ids), ('url', urls), ('full_name', names)]:
            value = record.get(field)
            if not nonempty_string(value) or value.casefold() in seen:
                errors.append(f'{where}: missing or duplicate {field}')
            else:
                seen.add(value.casefold())
        if record.get('scan_status') != 'readme-scanned' or record.get('verification') != 'automated-readme-scan':
            errors.append(f'{where}: preserve automated scan labels')
        for field in ('url', 'readme_url'):
            if public_https_error(record.get(field)):
                errors.append(f'{where}: invalid public {field}')
        if record.get('url') != 'https://github.com/' + str(record.get('full_name', '')):
            errors.append(f'{where}: repository URL and full_name disagree')
        if not re.fullmatch(r'[0-9a-f]{64}', str(record.get('readme_sha256', ''))):
            errors.append(f'{where}: missing README SHA-256')
        if type(record.get('readme_bytes')) is not int or record['readme_bytes'] <= 0:
            errors.append(f'{where}: missing positive README byte count')
        targets = record.get('targets')
        if not isinstance(targets, list) or any(target not in TARGETS for target in targets):
            errors.append(f'{where}: invalid automatic target labels')
        if type(record.get('stars')) is not int or record['stars'] < 0:
            errors.append(f'{where}: stars must be a nonnegative snapshot count')
        try:
            parse_iso(record.get('observed_at'), require_time=True)
        except (ValueError, TypeError):
            errors.append(f'{where}: invalid scan timestamp')

    failed_ids = set()
    for index, failure in enumerate(failures):
        if not isinstance(failure, dict) or not nonempty_string(failure.get('id')):
            errors.append(f'source index failure {index}: expected an object with a source ID')
            continue
        identifier = failure['id'].casefold()
        if identifier in failed_ids:
            errors.append(f'source index failure {index}: duplicate source ID')
        if identifier in ids:
            errors.append(f'source index failure {index}: source ID also has a successful scan')
        failed_ids.add(identifier)

    def nonnegative_integer(value):
        return type(value) is int and value >= 0

    # Legacy snapshots retain discovery counts without an ID ledger. Do not
    # invent identities for their historical unattempted candidates.
    if 'discovered_repository_ids' in meta:
        ledger = meta['discovered_repository_ids']
        if (not isinstance(ledger, list)
                or any(not isinstance(identifier, str) or not re.fullmatch(r'scan-[0-9]+', identifier)
                       for identifier in ledger)):
            errors.append('Source index discovery ledger must be an array of scan IDs.')
        else:
            known = set(ledger)
            if len(known) != len(ledger):
                errors.append('Source index discovery ledger contains duplicate IDs.')
            attempted_ids = [entry.get('id') for entry in records + failures if isinstance(entry, dict)]
            if any(not isinstance(identifier, str) or not re.fullmatch(r'scan-[0-9]+', identifier)
                   for identifier in attempted_ids):
                errors.append('Source index attempted repositories must have valid scan IDs.')
            elif not set(attempted_ids).issubset(known):
                errors.append('Source index attempted IDs must be present in the discovery ledger.')
            if not nonnegative_integer(meta.get('unique_repos')) or meta['unique_repos'] != len(known):
                errors.append('Source index unique repository count must match the discovery ledger.')
            if (not nonnegative_integer(meta.get('unattempted_candidates'))
                    or meta['unattempted_candidates'] != len(known) - len(records) - len(failures)):
                errors.append('Source index unattempted count must equal known IDs minus attempted repositories.')

    if 'current_run' in meta:
        run = meta['current_run']
        if not isinstance(run, dict):
            errors.append('Source index current_run must be an object.')
        else:
            for retained_key, new_key, total in (
                    ('retained_successful_readme_scans', 'new_successful_readme_scans', len(records)),
                    ('retained_failed_readme_scans', 'new_failed_readme_scans', len(failures))):
                retained, added = run.get(retained_key), run.get(new_key)
                if not nonnegative_integer(retained) or not nonnegative_integer(added):
                    errors.append(f'Source index current_run {retained_key}/{new_key} must be nonnegative integers.')
                elif retained + added != total:
                    errors.append(f'Source index current_run {retained_key} plus {new_key} does not match the snapshot total.')
            for observations_key, offset_key, count_key in (
                    ('queries', 'query_start_index', 'query_count'),
                    ('seed_observations', 'seed_observation_start_index', 'seed_observation_count')):
                observations = meta.get(observations_key, [])
                offset, count = run.get(offset_key), run.get(count_key)
                if (not isinstance(observations, list) or not nonnegative_integer(offset)
                        or not nonnegative_integer(count)):
                    errors.append(f'Source index current_run {offset_key}/{count_key} needs valid counters and an observation array.')
                elif offset + count != len(observations):
                    errors.append(f'Source index current_run {offset_key} plus {count_key} does not match {observations_key}.')
            if 'requested_new_successful_scans' in run:
                target, retained = meta.get('requested_successful_scans'), run.get('retained_successful_readme_scans')
                requested = run['requested_new_successful_scans']
                if (not nonnegative_integer(target) or not nonnegative_integer(retained)
                        or not nonnegative_integer(requested) or requested != max(0, target - retained)):
                    errors.append('Source index current_run requested new successes do not match the combined target.')
            if 'readme_queue_candidates' in run:
                queued = run['readme_queue_candidates']
                successes, failed = run.get('new_successful_readme_scans'), run.get('new_failed_readme_scans')
                if (not nonnegative_integer(queued) or not nonnegative_integer(successes)
                        or not nonnegative_integer(failed) or queued < successes + failed):
                    errors.append('Source index current_run README queue must cover all new attempted repositories.')
    return len(records)


def prose_only(text):
    """Remove fenced/indented code while retaining line numbers."""
    lines, fence_char, fence_length = [], None, 0
    for line in text.splitlines(keepends=True):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence_char:
            if match and match[1][0] == fence_char and len(match[1]) >= fence_length:
                fence_char = None
            lines.append('\n' if line.endswith('\n') else '')
        elif match:
            fence_char, fence_length = match[1][0], len(match[1])
            lines.append('\n' if line.endswith('\n') else '')
        elif line.startswith(('    ', '\t')):
            lines.append('\n' if line.endswith('\n') else '')
        else:
            lines.append(line)
    return ''.join(lines)


def markdown_anchors(text):
    prose = prose_only(text)
    anchors = set(re.findall(r'<[A-Za-z][^>]*\b(?:id|name)=["\']([^"\']+)["\']', prose))
    counts = {}
    lines = prose.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+\s*)?$', line)
        heading = match[1] if match else None
        if heading is None and index + 1 < len(lines) and re.fullmatch(r' {0,3}(?:=+|-+)\s*', lines[index + 1]) and line.strip():
            heading = line.strip()
        if heading is None:
            continue
        heading = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', heading)
        heading = html.unescape(re.sub(r'<[^>]+>', '', heading))
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f'{slug}-{count}')
    return anchors


LINK_PATTERN = re.compile(r'\]\(\s*(<[^>\n]+>|(?:\\.|[^\s()]|\([^()\n]*\))+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
REFERENCE_PATTERN = re.compile(r'^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)', re.MULTILINE)
HTML_LINK_PATTERN = re.compile(r'<[A-Za-z][^>]*?\b(?:href|src)=["\']([^"\']+)["\']', re.IGNORECASE)


def document_links(text):
    prose = prose_only(text)
    # Inline code is not a rendered link; retain its newlines for diagnostics.
    prose = re.sub(r'(`+)([^\n]*?)\1', lambda match: ' ' * len(match[0]), prose)
    for pattern in (LINK_PATTERN, REFERENCE_PATTERN, HTML_LINK_PATTERN):
        for match in pattern.finditer(prose):
            destination = html.unescape(match[1].strip('<>'))
            yield destination, prose.count('\n', 0, match.start()) + 1


def validate_markdown(root, errors):
    documents = [path for path in root.rglob('*.md')
                 if not any(part in IGNORED_DIRS for part in path.relative_to(root).parts)]
    anchors = {}
    for path in documents:
        text = path.read_text(encoding='utf-8')
        for destination, line in document_links(text):
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue
            where = f'{path.relative_to(root)}:{line}'
            local = unquote(parsed.path).replace('\\ ', ' ')
            target = (root / local.lstrip('/') if local.startswith('/') else path.parent / local).resolve() if local else path
            if not target.is_relative_to(root.resolve()):
                errors.append(f'{where}: local link escapes repository: {destination}')
                continue
            if not target.exists():
                errors.append(f'{where}: missing local link target: {destination}')
                continue
            fragment = unquote(parsed.fragment)
            if not fragment:
                continue
            if target.is_dir():
                target = target / 'README.md'
                if not target.exists():
                    errors.append(f'{where}: directory fragment has no README target: {destination}')
                    continue
            if target.suffix.lower() in {'.md', '.markdown'}:
                if target not in anchors:
                    anchors[target] = markdown_anchors(target.read_text(encoding='utf-8'))
                if fragment.removeprefix('user-content-') not in anchors[target]:
                    errors.append(f'{where}: missing Markdown anchor: {destination}')
            elif target.suffix.lower() in {'.html', '.htm'}:
                ids = set(re.findall(r'\b(?:id|name)=["\']([^"\']+)["\']', target.read_text(encoding='utf-8')))
                if fragment not in ids:
                    errors.append(f'{where}: missing HTML anchor: {destination}')
            elif re.fullmatch(r'L\d+(?:-L\d+)?', fragment):
                bounds = [int(value) for value in re.findall(r'\d+', fragment)]
                count = len(target.read_text(encoding='utf-8').splitlines())
                if not 1 <= bounds[0] <= bounds[-1] <= count:
                    errors.append(f'{where}: source line anchor is out of range: {destination}')
            else:
                errors.append(f'{where}: cannot validate fragment on this local file type: {destination}')
    return len(documents)


def read_array(path, errors):
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        errors.append(f'{path.relative_to(ROOT)}: cannot read JSON: {error}')
        return []
    if not isinstance(value, list) or not value:
        errors.append(f'{path.relative_to(ROOT)}: expected a nonempty JSON array')
        return []
    return value


def main():
    errors = []
    records = [record for path in RESOURCE_FILES for record in read_array(path, errors)]
    benchmarks = read_array(ROOT / 'data/benchmarks.json', errors)
    papers = read_array(ROOT / 'data/papers.json', errors)
    validate_papers(papers, errors, url_check=public_https_error)
    validate_resources(records, errors)
    validate_benchmarks(benchmarks, errors)
    scanned = 0
    index_path = ROOT / 'data/source-index.json'
    if index_path.exists():
        try:
            index_document = json.loads(index_path.read_text())
        except (OSError, ValueError):
            errors.append('Source index could not be read as JSON.')
        else:
            scanned = validate_source_index(index_document, errors)
            source_records = index_document.get('resources') if isinstance(index_document, dict) else None
            if (isinstance(source_records, list)
                    and all(isinstance(record, dict) and isinstance(record.get('id'), str)
                            for record in source_records)):
                try:
                    validate_localizations(source_records, read_localizations(ROOT), errors)
                except (OSError, ValueError):
                    errors.append('Repository localizations could not be read as valid JSON.')
                try:
                    validate_scope(source_records, read_scope(ROOT), errors)
                except (OSError, ValueError):
                    errors.append('Source-scope data could not be read as valid JSON.')
    count = validate_markdown(ROOT, errors)
    for script in ('build_readme.py', 'build_repository_index.py'):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script), '--check'],
                                cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append((result.stderr or result.stdout).strip() or f'{script}: generated content check failed.')
    if errors:
        print(f'Validation failed with {len(errors)} issue(s):', file=sys.stderr)
        for error in errors:
            print(f'- {error}', file=sys.stderr)
        return 1
    print(f'Validated {len(records)} curated resources, {len(papers)} research papers, {scanned} scanned sources, {len(benchmarks)} benchmark snapshots, {count} Markdown files, both generated catalogs, and the bilingual repository index.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
