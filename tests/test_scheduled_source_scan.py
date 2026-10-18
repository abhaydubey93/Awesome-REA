"""Scheduled discovery must retain evidence without promoting partial scans."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scheduled_source_scan as scheduled
from validate import validate_source_index


def record(identifier, *, failed=False, name=None):
    name = name or f'example/repository-{identifier}'
    result = {'id': f'scan-{identifier}', 'full_name': name, 'url': 'https://github.com/' + name,
              'scan_status': 'failed' if failed else 'readme-scanned', 'observed_at': '2026-10-18T00:00:00Z'}
    if failed:
        result.update(reason='http-404', http_status=404)
    else:
        result.update(verification='automated-readme-scan', readme_url='https://github.com/' + name + '#readme',
                      readme_sha256='a' * 64, readme_bytes=42, targets=[], stars=0)
    return result


def snapshot(success=(1,), failed=(), pending=(), status='complete'):
    known = sorted(set(success) | set(failed) | set(pending))
    return {'meta': {'schema_version': 1, 'status': status, 'queries': [],
                     'successful_readme_scans': len(success), 'failed': len(failed),
                     'attempted_readme_scans': len(success) + len(failed),
                     'unique_repos': len(known), 'unattempted_candidates': len(known) - len(success) - len(failed),
                     'requested_successful_scans': len(success),
                     'discovered_repository_ids': [f'scan-{i}' for i in known]},
            'resources': [record(i) for i in success], 'failures': [record(i, failed=True) for i in failed]}


def run(identifier=12, attempt=1, **changes):
    return {'id': identifier, 'run_attempt': attempt, 'workflow_id': 42, 'status': 'completed',
            'head_branch': 'main', 'event': 'schedule', 'head_repository': {'full_name': 'example/catalog'},
            'head_sha': 'b' * 40, **changes}


def artifact(identifier=12, attempt=1, **changes):
    return {'id': 73, 'name': scheduled.ARTIFACT + '-' + str(attempt), 'expired': False,
            'size_in_bytes': 500, 'workflow_run': {'id': identifier}, **changes}


class FakeAPI:
    repository = 'example/catalog'

    def __init__(self, runs, artifacts, attempts=None):
        self.runs, self.artifacts, self.attempts, self.calls = runs, artifacts, attempts or {}, []

    def get(self, path):
        self.calls.append(path)
        if path == 'actions/workflows/source-scan.yml':
            return {'id': 42}
        if '/attempts/' in path:
            return self.attempts[int(path.rsplit('/', 1)[-1])]
        if '/runs?' in path:
            return {'workflow_runs': self.runs}
        if '/artifacts?' in path:
            identifier = int(path.split('/')[2])
            return {'artifacts': self.artifacts.get(identifier, [])}
        raise AssertionError(path)


class ReconciliationTests(unittest.TestCase):
    def test_canonical_only_if_all_successes_and_pending_ids_are_covered(self):
        published, checkpoint = snapshot((1, 2), pending=(3,)), snapshot((1,), pending=(4,))
        merged, receipt = scheduled.reconcile(published, checkpoint, 'c', 'p')
        self.assertEqual(receipt['mode'], 'union')
        self.assertEqual(scheduled.known_ids(merged), {'scan-1', 'scan-2', 'scan-3', 'scan-4'})
        self.assertEqual(merged['meta']['successful_readme_scans'], 2)
        self.assertEqual(merged['meta']['unattempted_candidates'], 2)
        covered, receipt = scheduled.reconcile(published, snapshot((1,), pending=(3,)), 'c', 'p')
        self.assertEqual(receipt['mode'], 'canonical-covers-checkpoint')
        self.assertEqual(covered, published)

    def test_union_preserves_unpublished_objects_and_prefers_success_to_failure(self):
        canonical = snapshot((1, 2), failed=(3,), pending=(5,))
        previous = snapshot((1, 3, 4), failed=(2,), pending=(6,))
        previous['resources'][0]['stars'] = 10
        before = copy.deepcopy(previous)
        merged, receipt = scheduled.reconcile(canonical, previous, 'c', 'p')
        self.assertEqual(previous, before)
        self.assertEqual({r['id'] for r in merged['resources']}, {'scan-1', 'scan-2', 'scan-3', 'scan-4'})
        self.assertEqual(merged['failures'], [])
        self.assertEqual(next(r for r in merged['resources'] if r['id'] == 'scan-4'), previous['resources'][2])
        self.assertEqual(next(r for r in merged['resources'] if r['id'] == 'scan-1'), canonical['resources'][0])
        self.assertEqual(len(receipt['superseded']), 3)
        self.assertEqual(merged['meta']['attempted_readme_scans'], 4)
        self.assertEqual(merged['meta']['unattempted_candidates'], 2)
        self.assertNotIn('current_run', merged['meta'])
        self.assertEqual(merged['meta']['status'], 'in-progress')

    def test_observation_union_retains_old_run_identity_and_deduplicates(self):
        first, second = snapshot((1,)), snapshot((1, 2))
        observation = {'query': 'example', 'status': 'ok', 'run_id': 'old'}
        first['meta']['queries'] = [observation]
        second['meta']['queries'] = [observation, {'query': 'other', 'status': 'ok', 'run_id': 'new'}]
        second['meta']['current_run'] = {'run_id': 'new', 'new_successful_readme_scans': 1}
        merged, receipt = scheduled.reconcile(first, second, 'c', 'p')
        self.assertEqual(merged['meta']['queries'], second['meta']['queries'])
        self.assertEqual(receipt['checkpoint_current_run'], second['meta']['current_run'])
        self.assertNotIn('current_run', merged['meta'])

    def test_reassigned_names_are_detected_even_in_superseded_versions(self):
        canonical, previous = snapshot((1, 2)), snapshot((1, 3))
        previous['resources'][0]['full_name'] = canonical['resources'][1]['full_name']
        with self.assertRaisesRegex(ValueError, 'same name'):
            scheduled.reconcile(canonical, previous, 'c', 'p')

    def test_partial_checkpoint_is_not_publishable_by_default(self):
        doc = snapshot(range(1, 1502), status='in-progress')
        errors = []; validate_source_index(doc, errors)
        self.assertTrue(any('incomplete checkpoint' in e for e in errors))
        errors = []; validate_source_index(doc, errors, allow_incomplete=True)
        self.assertEqual(errors, [])
        self.assertEqual(doc['meta']['status'], 'in-progress')


class SelectionTests(unittest.TestCase):
    def test_only_same_workflow_default_branch_and_repository_are_trusted(self):
        invalid = [run(15, event='pull_request'), run(14, head_repository={'full_name': 'fork/catalog'}),
                   run(13, workflow_id=99), run(11, head_branch='feature')]
        api = FakeAPI(invalid + [run()], {12: [artifact()]})
        selected, _ = scheduled.select_checkpoint(api, 'main', 20)
        self.assertEqual(selected['id'], 12)
        self.assertEqual(len([c for c in api.calls if '/artifacts?' in c]), 1)

    def test_failed_terminal_runs_with_valid_checkpoints_are_resumable(self):
        api = FakeAPI([run(conclusion='failure')], {12: [artifact()]})
        self.assertIsNotNone(scheduled.select_checkpoint(api, 'main', 20))

    def test_rerun_resumes_previous_attempt_instead_of_losing_its_increment(self):
        api = FakeAPI([run(10)], {12: [artifact(12)]}, attempts={1: run(12)})
        selected, _ = scheduled.select_checkpoint(api, 'main', 12, 2)
        self.assertEqual((selected['id'], selected['run_attempt']), (12, 1))

    def test_expired_newest_checkpoint_stops_instead_of_silently_starting_over(self):
        api = FakeAPI([run()], {12: [artifact(expired=True)]})
        with self.assertRaisesRegex(ValueError, 'expired'):
            scheduled.select_checkpoint(api, 'main', 20)


def archive_bytes(document, *, member_name='checkpoint.json', symlink=False, duplicate=False, overrides=None):
    raw = json.dumps(document).encode()
    receipt = {'schema_version': 1, 'run_id': 12, 'run_attempt': 1, 'workflow_id': 42,
               'source_commit': 'b' * 40, 'checkpoint_sha256': hashlib.sha256(raw).hexdigest(),
               'counts': scheduled.counts(document), **(overrides or {})}
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo(member_name)
        if symlink:
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(info, raw)
        archive.writestr('receipt.json', json.dumps(receipt))
        if duplicate:
            archive.writestr('extra.json', '{}')
    return stream.getvalue()


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.doc = snapshot(range(1, 1502), status='in-progress')

    def unpack(self, raw, **changes):
        item = artifact(digest='sha256:' + hashlib.sha256(raw).hexdigest(), **changes)
        return scheduled.unpack_checkpoint(raw, item, run(), self.directory)

    def test_valid_partial_archive_retains_counts_and_status(self):
        restored, _ = self.unpack(archive_bytes(self.doc))
        self.assertEqual(restored, self.doc)

    def test_paths_links_unknown_members_and_provenance_mismatch_are_rejected(self):
        for options in ({'member_name': '../checkpoint.json'}, {'symlink': True}, {'duplicate': True},
                        {'overrides': {'run_id': 99}}, {'overrides': {'run_attempt': 2}},
                        {'overrides': {'workflow_id': 99}}, {'overrides': {'source_commit': 'c' * 40}},
                        {'overrides': {'checkpoint_sha256': 'f' * 64}}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.unpack(archive_bytes(self.doc, **options))

    def test_digest_size_and_private_payload_are_rejected_without_echoing_values(self):
        raw = archive_bytes(self.doc)
        with self.assertRaisesRegex(ValueError, 'digest'):
            scheduled.unpack_checkpoint(raw, artifact(digest='sha256:' + '0' * 64), run(), self.directory)
        with patch.object(scheduled, 'MAX_BYTES', 100), self.assertRaises(ValueError):
            self.unpack(raw)
        token = 'gh' + 'p_' + 'a' * 36
        self.doc['resources'][0]['description_en'] = token
        with self.assertRaises(ValueError) as raised:
            self.unpack(archive_bytes(self.doc))
        self.assertNotIn(token, str(raised.exception))

    def test_unknown_record_fields_and_inconsistent_counts_are_not_trusted(self):
        self.doc['resources'][0]['readme_body'] = 'must not enter an artifact'
        with self.assertRaisesRegex(ValueError, 'unexpected record'):
            self.unpack(archive_bytes(self.doc))
        del self.doc['resources'][0]['readme_body']
        self.doc['meta']['failed'] = 42
        with self.assertRaises(ValueError):
            self.unpack(archive_bytes(self.doc))


class WorkflowTests(unittest.TestCase):
    def test_schedule_permissions_upload_scope_and_bounds(self):
        text = (scheduled.ROOT / '.github/workflows/source-scan.yml').read_text()
        self.assertIn("cron: '17 0,8,16 * * *'", text)
        self.assertIn('timezone: America/Los_Angeles', text)
        self.assertIn('contents: read', text); self.assertIn('actions: read', text)
        self.assertNotIn(': write', text); self.assertNotIn('pull_request', text)
        self.assertIn('timeout-minutes: 45', text)
        self.assertIn("steps.scan.outputs.checkpoint_ready == 'true'", text)
        self.assertIn('checkpoint/checkpoint.json', text)
        self.assertNotIn('path: .cache/', text.split('name: Preserve validated incremental checkpoint')[1].split('name: Preserve validated inputs')[0])
        self.assertEqual(scheduled.NEW_SUCCESSES, 300)
        self.assertLess(scheduled.SCAN_SECONDS, 45 * 60)


class RuntimeBoundaryTests(unittest.TestCase):
    def test_signed_artifact_request_drops_authorization_and_rechecks_deadline(self):
        calls = []
        token = 'ephemeral-test-value'

        class Opener:
            def open(self, request, timeout):
                calls.append((request, timeout))
                if len(calls) == 1:
                    raise HTTPError(request.full_url, 302, 'redirect',
                                    {'Location': 'https://example.blob.core.windows.net/artifact?signature=fixture'}, io.BytesIO())
                return io.BytesIO(b'archive bytes')

        with patch.object(scheduled, 'build_opener', return_value=Opener()), patch.object(scheduled.time, 'monotonic', side_effect=[10, 20]):
            result = scheduled.ActionsAPI('example/catalog', token, deadline=50).get('actions/artifacts/73/zip', archive=True)
        self.assertEqual(result, b'archive bytes')
        self.assertEqual(calls[0][0].get_header('Authorization'), 'Bearer ' + token)
        self.assertIsNone(calls[1][0].get_header('Authorization'))
        calls.clear()
        with patch.object(scheduled, 'build_opener', return_value=Opener()), patch.object(scheduled.time, 'monotonic', side_effect=[10, 51]):
            with self.assertRaisesRegex(ValueError, 'time bound'):
                scheduled.ActionsAPI('example/catalog', token, deadline=50).get('actions/artifacts/73/zip', archive=True)
        self.assertEqual(len(calls), 1)

    def test_timeout_waits_for_child_and_retains_only_valid_partial_checkpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root / 'data').mkdir()
            canonical = snapshot(range(1, 1502))
            scheduled.write_json(root / 'data/source-index.json', canonical)
            environment = {'GITHUB_REPOSITORY': 'example/catalog', 'DEFAULT_BRANCH': 'main',
                           'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '20', 'GITHUB_RUN_ATTEMPT': '1',
                           'GITHUB_SHA': 'd' * 40, 'GH_TOKEN': 'ephemeral-test-value',
                           'GITHUB_OUTPUT': str(root / 'outputs'), 'GITHUB_STEP_SUMMARY': str(root / 'summary')}
            process = SimpleNamespace(pid=1234)
            waits = []

            def launch(command, **kwargs):
                self.assertNotIn(environment['GH_TOKEN'], ' '.join(command))
                self.assertTrue(kwargs['start_new_session'])
                path = Path(command[command.index('--output') + 1])
                partial = snapshot(range(1, 1503), pending=(1503,), status='in-progress')
                scheduled.write_json(path, partial)
                return process

            def wait(timeout=None):
                waits.append(timeout)
                if len(waits) == 1:
                    raise subprocess.TimeoutExpired('scanner', timeout)
                return -15

            process.wait = wait
            with patch.dict(os.environ, environment), patch.object(scheduled, 'ROOT', root), \
                    patch.object(scheduled, 'ActionsAPI', return_value=FakeAPI([], {})), \
                    patch.object(scheduled.subprocess, 'Popen', side_effect=launch), \
                    patch.object(scheduled.os, 'killpg') as stop:
                result = scheduled.orchestrate(root / 'run')
            self.assertEqual(result, 1)
            stop.assert_called_once_with(1234, scheduled.signal.SIGTERM)
            self.assertEqual(len(waits), 2)
            receipt = json.loads((root / 'run/checkpoint/receipt.json').read_text())
            self.assertEqual(receipt['outcome'], 'time-budget')
            self.assertEqual(receipt['new_successful_scans'], 1)
            self.assertFalse(receipt['target_reached'])
            final = json.loads((root / 'run/checkpoint/checkpoint.json').read_text())
            self.assertEqual(final['meta']['status'], 'in-progress')
            self.assertEqual((root / 'outputs').read_text(), 'checkpoint_ready=true\n')
            self.assertNotIn(environment['GH_TOKEN'], json.dumps(receipt))
            self.assertEqual(json.loads((root / 'data/source-index.json').read_text()), canonical)


if __name__ == '__main__':
    unittest.main()
