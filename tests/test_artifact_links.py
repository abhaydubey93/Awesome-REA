"""Offline checks for evidence boundaries and internal artifact navigation."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from artifact_links import github_repository, with_artifact_links
from build_browse_pages import repository_card


def source(**changes):
    return {'id': 'scan-1', 'name': 'Owner/Project', 'full_name': 'Owner/Project',
            'url': 'https://github.com/Owner/Project', 'description_en': '', 'description_zh': '',
            'verification': 'automated-readme-scan', 'readme_sha256': 'a' * 64, **changes}


def paper(**changes):
    return {'id': 'paper-example', 'title': 'Example research', 'title_zh': '示例研究',
            'verification': 'source-reviewed', 'code_url': 'https://github.com/owner/project',
            'project_url': None, **changes}


def resource(**changes):
    return {'id': 'example-tool', 'name': 'Example tool', 'name_zh': '示例工具',
            'url': 'https://github.com/owner/project', 'verification': 'source-reviewed', **changes}


class ArtifactLinkTests(unittest.TestCase):
    def test_repository_identity_rejects_guessed_or_unsafe_matches(self):
        for url in ('https://github.com/Owner/Project', 'https://GITHUB.COM/owner/project.git/'):
            self.assertEqual(github_repository(url), 'owner/project')
        for url in ('https://github.com/owner/project/blob/main/README.md',
                    'https://github.com/owner/project/tree/main'):
            self.assertEqual(github_repository(url, artifact=True), 'owner/project')
            self.assertIsNone(github_repository(url))
        for url in ('https://owner.github.io/project/', 'https://gitlab.com/owner/project',
                    'https://github.com.evil.test/owner/project', 'https://secret@github.com/owner/project',
                    'http://github.com/owner/project', 'javascript:alert(1)',
                    'https://github.com:443/owner/project', 'https://github.com/owner/../project',
                    'https://github.com/owner%2Fother/project', 'https://github.com//owner/project',
                    'https://github.com/owner/project/issues/1'):
            with self.subTest(url=url):
                self.assertIsNone(github_repository(url, artifact=True))

    def test_reviewed_artifact_links_work_without_seed_fields_and_preserve_inputs(self):
        records, papers = [source()], [paper()]
        before = copy.deepcopy((records, papers))
        result = with_artifact_links(records, papers, [])
        self.assertEqual((records, papers), before)
        self.assertEqual({k: v for k, v in result[0].items() if k != 'related_entries'}, records[0])
        self.assertEqual(result[0]['description_en'], '')
        self.assertEqual(result[0]['verification'], 'automated-readme-scan')
        self.assertEqual(result[0]['related_entries'][0]['href_zh'], '/zh/papers/#paper-example')

    def test_duplicate_fields_deduplicate_and_input_order_does_not_change_links(self):
        papers = [paper(project_url='https://github.com/owner/project/tree/main'),
                  paper(id='paper-another')]
        resources = [resource()]
        result = with_artifact_links([source()], papers, resources)
        self.assertEqual(result, with_artifact_links([source()], list(reversed(papers)), resources))
        entries = result[0]['related_entries']
        self.assertEqual([(r['kind'], r['id']) for r in entries],
                         [('paper', 'paper-another'), ('paper', 'paper-example'), ('curated', 'example-tool')])
        self.assertEqual(entries[1]['artifact_fields'], ['code_url', 'project_url'])
        self.assertEqual(with_artifact_links(result, papers, resources), result)

    def test_seed_only_references_do_not_guess_repository_transfers(self):
        diagnostics = []
        result = with_artifact_links([source(seed_paper_ids=['paper-example', 'paper-unknown'])],
                                     [paper(code_url='https://github.com/old-owner/project')], [], diagnostics)
        self.assertNotIn('related_entries', result[0])
        self.assertEqual(len(diagnostics), 2)

    def test_mirrors_nested_curated_guides_and_unreviewed_sources_do_not_link(self):
        resources = [resource(url='https://gitlab.com/owner/project',
                              additional_evidence_urls=['https://github.com/owner/project']),
                     resource(id='guide', url='https://github.com/owner/project/blob/main/README.md'),
                     resource(id='unreviewed', verification='automated-readme-scan')]
        self.assertNotIn('related_entries', with_artifact_links([source()],
                         [paper(verification='automated-readme-scan')], resources)[0])
        self.assertNotIn('related_entries', with_artifact_links([source(full_name='Different/Repository')],
                         [paper()], [resource()])[0])

    def test_static_cards_use_localized_same_tab_links_and_escape_titles(self):
        row = with_artifact_links([source()], [paper(title='<script>research</script>')], [resource()])[0]
        for language, prefix, label in (('en', '', 'Related research'), ('zh', '/zh', '相关研究')):
            rendered = repository_card(row, language, False)
            self.assertIn(f'href="{prefix}/papers/#paper-example"', rendered)
            self.assertIn(f'href="{prefix}/resources/#example-tool"', rendered)
            self.assertIn(label, rendered)
            self.assertIn('No description supplied' if language == 'en' else '上游仓库未提供项目简介', rendered)
            self.assertNotIn('<script>research</script>', rendered)
            self.assertNotRegex(rendered, r'class="source-related-link"[^>]*target=')
        row['related_entries'][0]['href_en'] = 'https://example.com/#paper-example'
        with self.assertRaises(ValueError):
            repository_card(row, 'en', False)


if __name__ == '__main__':
    unittest.main()
