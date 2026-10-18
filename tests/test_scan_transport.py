"""Transport changes must preserve evidence and avoid counting deferred metadata."""
import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scan_sources import run_scan

BODY = b'# Example\n\n## Usage\nRead a public protocol trace.\n'
OID = hashlib.sha1(b'blob ' + str(len(BODY)).encode() + b'\0' + BODY).hexdigest()
QUERY = 'topic:reverse-engineering is:public fork:false archived:false'


def repository():
    return {'id': 42, 'full_name': 'example/protocol',
            'html_url': 'https://github.com/example/protocol', 'private': False,
            'visibility': 'public', 'archived': False, 'fork': False,
            'description': 'A protocol analysis tool', 'topics': ['protocol-analysis'],
            'stargazers_count': 3, 'default_branch': 'main',
            '_metadata_observed_at': '2026-10-18T12:00:00Z'}


class API:
    def __init__(self):
        self.readme_calls = 0

    def json(self, path, search=False):
        if search:
            return {'items': [repository()], 'total_count': 1, 'incomplete_results': False}
        self.readme_calls += 1
        return {'type': 'file', 'path': 'README.md', 'sha': OID, 'size': len(BODY),
                'html_url': repository()['html_url'] + '/blob/main/README.md',
                'encoding': 'base64', 'content': base64.b64encode(BODY).decode()}


class Transport:
    batch_size = 8

    def __init__(self, status):
        self.status = status

    def fetch_batch(self, repositories):
        return {r['id']: {'status': self.status, 'repository': repository(), 'content': BODY,
                         'metadata': {'path': 'README.md', 'sha': OID, 'size': len(BODY),
                                      'commit_oid': 'a' * 40,
                                      'html_url': repository()['html_url'] + '/blob/' + 'a' * 40 + '/README.md'}}
                for r in repositories}


class ScanTransportTests(unittest.TestCase):
    def scan(self, status, *, api=None, transport=None, target=1):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'scan.json'
            args = SimpleNamespace(target=target, workers=1, requests_per_second=1,
                                   max_pages=1, candidate_buffer=0, seed_curated=False,
                                   seed_papers=False, queries=[QUERY], output=output)
            api = api or API()
            with contextlib.redirect_stdout(io.StringIO()):
                code = run_scan(api, args, readme_transport=transport or Transport(status))
            return code, json.loads(output.read_text()), api

    def test_graphql_reads_have_real_hashes_and_no_fabricated_rest_request(self):
        code, document, api = self.scan('ok')
        self.assertEqual(code, 0)
        self.assertEqual(api.readme_calls, 0)
        record = document['resources'][0]
        self.assertEqual(record['readme_sha256'], hashlib.sha256(BODY).hexdigest())
        self.assertEqual(record['readme_commit_sha'], 'a' * 40)
        self.assertEqual(record['readme_transport'], 'github-graphql-blob')
        self.assertNotIn('readme_api_url', record)
        self.assertEqual(record['matched_queries'], [QUERY])
        self.assertNotIn(BODY.decode(), json.dumps(document))

    def test_fallback_performs_a_real_rest_read(self):
        code, document, api = self.scan('fallback')
        self.assertEqual((code, api.readme_calls), (0, 1))
        self.assertIn('readme_api_url', document['resources'][0])
        self.assertNotIn('readme_transport', document['resources'][0])

    def test_backpressure_stays_pending_without_rest_escape_or_false_failure(self):
        for status in ('retry', 'deferred'):
            with self.subTest(status=status):
                code, document, api = self.scan(status)
                self.assertEqual((code, api.readme_calls), (1, 0))
                self.assertEqual(document['resources'], [])
                self.assertEqual(document['failures'], [])
                self.assertEqual(document['meta']['status'], 'in-progress')
                self.assertEqual(document['meta']['unattempted_candidates'], 1)

    def test_ineligible_metadata_never_counts_as_a_readme_attempt(self):
        code, document, api = self.scan('rejected')
        self.assertEqual((code, api.readme_calls), (1, 0))
        self.assertEqual(document['meta']['attempted_readme_scans'], 0)
        self.assertEqual(document['meta']['unattempted_candidates'], 1)

    def test_later_backpressure_suppresses_earlier_sibling_rest_fallback(self):
        class TwoAPI(API):
            def json(self, path, search=False):
                if not search:
                    return super().json(path, search)
                second = {**repository(), 'id': 43, 'full_name': 'example/second',
                          'html_url': 'https://github.com/example/second'}
                return {'items': [repository(), second], 'total_count': 2, 'incomplete_results': False}

        class Mixed(Transport):
            def fetch_batch(self, repositories):
                result = super().fetch_batch(repositories)
                result[43]['status'] = 'deferred'
                return result

        code, document, api = self.scan('fallback', api=TwoAPI(), transport=Mixed('fallback'), target=2)
        self.assertEqual((code, api.readme_calls), (1, 0))
        self.assertEqual(document['meta']['attempted_readme_scans'], 0)
        self.assertEqual(document['meta']['status'], 'in-progress')

    def test_verified_but_nontext_blob_is_a_recorded_failed_read(self):
        class Nontext(Transport):
            def fetch_batch(self, repositories):
                result = super().fetch_batch(repositories)
                content = ('\ufffd' * 30).encode()
                for row in result.values():
                    row['content'] = content
                    row['metadata'].update(size=len(content), sha=hashlib.sha1(
                        b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest())
                return result

        code, document, api = self.scan('ok', transport=Nontext('ok'))
        self.assertEqual((code, api.readme_calls), (1, 0))
        self.assertEqual(document['meta']['successful_readme_scans'], 0)
        self.assertEqual(document['failures'][0]['reason'], 'nontext-readme')

    def test_frontier_recovers_historical_query_without_counting_a_new_request(self):
        import search_frontier as frontier
        import scan_sources
        approved = ['topic:reverse-engineering']
        state = frontier.new_frontier(until='2026-10-18T00:00:00Z', approved_queries=approved)
        request = frontier.next_request(state)
        repo = {**repository(), 'created_at': '2026-10-01T00:00:00Z'}
        old_run = '2026-10-18T01:00:00Z'
        frontier.record_response(state, request, {'items': [repo], 'total_count': 1,
                                 'incomplete_results': False}, observed_at=old_run, run_id=old_run)
        cache = scan_sources.ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as directory:
            output = Path(directory) / 'scan.json'
            args = SimpleNamespace(target=1, workers=1, requests_per_second=1, max_pages=1,
                                   candidate_buffer=0, seed_curated=False, seed_papers=False,
                                   queries=[QUERY], output=output)
            api = API()
            with contextlib.redirect_stdout(io.StringIO()), patch.object(api, 'json', side_effect=AssertionError('No HTTP query expected')):
                code = run_scan(api, args, readme_transport=Transport('ok'),
                                frontier=(state, Path(directory) / 'frontier.json', approved))
            document = json.loads(output.read_text())
            self.assertEqual(code, 0)
            self.assertEqual(document['meta']['current_run']['query_count'], 0)
            self.assertEqual(document['meta']['queries'][0]['run_id'], old_run)
            self.assertEqual(document['resources'][0]['matched_queries'], [request['query']])
            self.assertIsNotNone(state['candidates']['42']['checkpoint_sha256'])
            # A newer acknowledged frontier cannot silently skip evidence in an older source file.
            with self.assertRaisesRegex(ValueError, 'absent from this scan checkpoint'):
                run_scan(api, args, readme_transport=Transport('ok'),
                         frontier=(state, Path(directory) / 'frontier.json', approved))


if __name__ == '__main__':
    unittest.main()
