"""Reject inventory inflation, unsupported review claims and unsafe evidence/mappings."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from case_coverage import read_case_coverage, validate_case_coverage
from validate import public_https_error
import review_pr


PIN = 'a' * 40
REPOSITORY = 'https://github.com/example/cases'
FILE = REPOSITORY + '/blob/' + PIN + '/README.md'
RESOURCES = [
    {'id': 'example-list', 'kind': 'collection', 'url': REPOSITORY},
    {'id': 'example-case', 'kind': 'case-study', 'url': 'https://github.com/example/project'},
]


def fixture():
    def entry(identifier, unit, state='pending'):
        linked = state == 'already-curated'
        return {'id': identifier, 'unit_id': unit, 'collection_id': 'one',
                'title': 'Example case', 'collection_urls': [FILE],
                'reported_source_urls': ['https://github.com/example/project'],
                'state': state, 'review_level': 'catalog-mapped' if linked else 'inventory-only',
                'reviewed_at': '2026-01-01', 'reason_en': 'Bounded source review.', 'reason_zh': '有限范围的来源核查。',
                'primary_evidence_urls': ['https://github.com/example/project'] if linked else [],
                'catalog_matches': [{'catalog': 'resource', 'id': 'example-case', 'kind': 'case-study', 'scope': 'full'}] if linked else []}
    return {
        'schema_version': 1, 'reviewed_at': '2026-01-01', 'catalog_revision': PIN,
        'runtime_reproduced': False, 'project_identity_resolution': 'incomplete',
        'collections': [{'id': 'one', 'repository_url': REPOSITORY, 'commit': PIN,
                         'entry_count': 3, 'catalog_resource_id': 'example-list',
                         'source_files': [{'path': 'README.md', 'url': FILE, 'git_blob_sha': 'b' * 40,
                                           'sha256': 'c' * 64, 'bytes': 50}]}],
        'entries': [entry('one:first', 'one:first'), entry('one:alias', 'one:first'),
                    entry('one:covered', 'one:covered', 'already-curated')],
        'aliases': [{'unit_id': 'one:first', 'occurrence_ids': ['one:first', 'one:alias'],
                     'basis_en': 'Same reported subject.', 'basis_zh': '相同报告对象。', 'evidence_urls': [FILE]}],
        'counts': {'occurrences': 3, 'inventory_units': 2, 'alias_merges': 1,
                   'occurrences_by_state': {'already-curated': 1, 'pending': 2},
                   'units_by_state': {'already-curated': 1, 'pending': 1},
                   'primary_reviewed_units': 0, 'catalog_linked_occurrences': 1,
                   'distinct_resource_ids': 1, 'distinct_paper_ids': 0, 'unique_projects': None},
    }


class CaseCoverageTests(unittest.TestCase):
    def errors(self, value):
        errors = []
        validate_case_coverage(value, RESOURCES, [], errors, url_check=public_https_error)
        return errors

    def test_valid_inventory_keeps_project_count_unknown(self):
        self.assertEqual(self.errors(fixture()), [])

    def test_count_grains_and_boolean_counts_are_rejected(self):
        for key, value in [('inventory_units', 3), ('unique_projects', 2), ('distinct_resource_ids', True)]:
            with self.subTest(key=key):
                document = fixture(); document['counts'][key] = value
                self.assertTrue(self.errors(document))
        document = fixture(); document['counts']['units_by_state']['already-curated'] = True
        self.assertTrue(self.errors(document))

    def test_alias_members_and_states_must_be_explicit(self):
        for mutation in ('missing', 'wrong-member', 'inconsistent-state', 'unrelated-evidence'):
            with self.subTest(mutation=mutation):
                document = fixture()
                if mutation == 'missing': document['aliases'] = []
                elif mutation == 'wrong-member': document['aliases'][0]['occurrence_ids'][1] = 'one:missing'
                elif mutation == 'inconsistent-state': document['entries'][1]['state'] = 'insufficient-evidence'
                else: document['aliases'][0]['evidence_urls'] = ['https://example.org/unrelated']
                self.assertTrue(self.errors(document))

    def test_partial_or_unreviewed_match_cannot_claim_full_coverage(self):
        for field, value in [('scope', 'partial'), ('scope', 'related'), ('id', 'missing'), ('kind', 'tool')]:
            document = fixture(); document['entries'][2]['catalog_matches'][0][field] = value
            self.assertTrue(self.errors(document))
        document = fixture(); document['entries'][2]['review_level'] = 'inventory-only'
        self.assertTrue(self.errors(document))

    def test_primary_review_needs_primary_sources_and_never_implies_runtime(self):
        document = fixture(); document['entries'][0]['review_level'] = 'primary-source-reviewed'
        self.assertTrue(self.errors(document))
        document = fixture(); document['runtime_reproduced'] = True
        self.assertTrue(self.errors(document))
        document = fixture(); document['entries'][2]['primary_evidence_urls'] = ['https://example.org/unrelated']
        self.assertTrue(self.errors(document))

    def test_private_paths_and_malformed_url_arrays_fail_safely(self):
        document = fixture(); document['entries'][0]['reason_en'] = '/' + 'Users' + '/example/review'
        self.assertTrue(self.errors(document))
        for key in ('reported_source_urls', 'collection_urls', 'primary_evidence_urls'):
            document = fixture(); document['entries'][0][key] = None
            self.assertTrue(self.errors(document))

    def test_source_pins_and_public_url_boundary(self):
        for url in [REPOSITORY + '/blob/main/README.md', FILE + '?ref=main',
                    REPOSITORY + '/blob/' + PIN + '/../main/README.md',
                    'https://example.org/README.md', 'https://localhost/readme']:
            with self.subTest(url=url):
                document = fixture(); document['entries'][0]['collection_urls'] = [url]
                self.assertTrue(self.errors(document))
        document = fixture(); document['entries'][0]['reported_source_urls'] = ['https://name:secret@example.org/']
        self.assertTrue(self.errors(document))
        document = fixture(); document['collections'][0]['source_files'][0]['git_blob_sha'] = 'invalid'
        self.assertTrue(self.errors(document))

    def test_collection_counts_ids_and_unknown_fields(self):
        for mutation in ('count', 'duplicate-id', 'raw-body', 'bad-type'):
            document = fixture()
            if mutation == 'count': document['collections'][0]['entry_count'] = 4
            elif mutation == 'duplicate-id': document['entries'][1]['id'] = 'one:first'
            elif mutation == 'raw-body': document['entries'][0]['readme_body'] = 'Do not publish full source.'
            else: document['entries'][0]['state'] = []
            self.assertTrue(self.errors(document))

    def test_strict_loader_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data'; path.mkdir()
            (path / 'case-coverage.json').write_text('{"schema_version": 1, "schema_version": 2}')
            with self.assertRaises(ValueError): read_case_coverage(directory)

    def test_trusted_reviewer_fetches_only_changed_json(self):
        document = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'data').mkdir()
            values = {review_pr.CATALOGS[0]: RESOURCES, review_pr.CATALOGS[1]: [], 'data/papers.json': []}
            for filename, value in values.items(): (root / filename).write_text(json.dumps(value))
            with patch.object(review_pr, 'ROOT', root), patch.object(review_pr, 'content_at', return_value=json.dumps(document)) as fetch:
                errors = []
                contents = review_pr.load_review_contents('example/repo', PIN, 'mock', [], {review_pr.CASE_COVERAGE}, errors)
                self.assertEqual(errors, [])
                fetch.assert_called_once_with('example/repo', review_pr.CASE_COVERAGE, PIN, 'mock')
                self.assertEqual(review_pr.review_data(contents, {review_pr.CASE_COVERAGE})[0], [])
        with patch.object(review_pr, 'api') as api:
            with self.assertRaises(ValueError): review_pr.content_at('example/repo', 'scripts/untrusted.py', PIN, 'mock')
            api.assert_not_called()


if __name__ == '__main__':
    unittest.main()
