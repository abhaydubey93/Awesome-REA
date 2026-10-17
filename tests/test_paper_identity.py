"""Keep identifier-free proceedings records bound to reviewed publisher evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import bibtex_text, scholarly_article
from validate import public_https_error
from validate_papers import validate_papers


def publisher_paper():
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text())[0])
    record.update(id='paper-publisher-fixture', title='Publisher identity fixture',
                  title_zh='出版方标识测试记录', year=2022, publication_date='2022-08',
                  date_precision='month', venue='USENIX Security 2022',
                  publication_status='conference-paper', arxiv_id=None, doi=None,
                  arxiv_version_reviewed=None, first_arxiv_date=None,
                  url='https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski',
                  pdf_url='https://www.usenix.org/system/files/sec22-scharnowski.pdf')
    record['evidence_urls'] = [record['url'], record['pdf_url']]
    return record


def errors_for(records):
    errors = []
    validate_papers(records, errors, url_check=public_https_error)
    return errors


class PaperIdentityTests(unittest.TestCase):
    def test_published_record_keeps_null_identifiers_in_citations_and_schema(self):
        record = publisher_paper()
        self.assertEqual(errors_for([record]), [])
        citation = bibtex_text(record)
        self.assertTrue(citation.startswith('@inproceedings{'))
        self.assertNotIn('doi =', citation)
        self.assertNotIn('eprint =', citation)
        self.assertIn(record['url'], citation)
        for language in ('en', 'zh'):
            article = scholarly_article(record, language)
            self.assertNotIn('identifier', article)
            self.assertEqual(article['@id'], record['url'])

    def test_unpublished_and_unreviewed_publication_profiles_are_rejected(self):
        for status in ('preprint', 'conference-accepted', 'journal-article'):
            with self.subTest(status=status):
                record = publisher_paper()
                record['publication_status'] = status
                self.assertTrue(errors_for([record]))
        for landing in (
            'https://example.org/paper',
            'https://zenodo.org/records/6499215',
            'https://github.com/fuzzware-fuzzer/fuzzware',
            'https://www.usenix.org/conference/woot18/presentation/kleber',
        ):
            record = publisher_paper()
            record['url'] = landing
            record['evidence_urls'][0] = landing
            self.assertTrue(errors_for([record]))

    def test_hosts_credentials_ports_and_url_suffixes_cannot_expand_profile(self):
        valid = publisher_paper()
        for field in ('url', 'pdf_url'):
            url = valid[field]
            for malformed in (
                url.replace('https://', 'http://'),
                url.replace('www.usenix.org', 'www.usenix.org.example.com'),
                url.replace('www.usenix.org', 'user@www.usenix.org'),
                url.replace('www.usenix.org', 'www.usenix.org:443'),
                url + '?download=1', url + '#paper', url + '/',
            ):
                with self.subTest(field=field, url=malformed):
                    record = deepcopy(valid)
                    record[field] = malformed
                    record['evidence_urls'] = [record['url'], record['pdf_url']]
                    self.assertTrue(errors_for([record]))

    def test_final_pdf_year_presenter_and_exact_evidence_must_match(self):
        for field, value in (
            ('pdf_url', 'https://www.usenix.org/system/files/usenixsecurity22-scharnowski.pdf'),
            ('pdf_url', 'https://www.usenix.org/system/files/sec21-scharnowski.pdf'),
            ('pdf_url', 'https://www.usenix.org/system/files/sec22-another.pdf'),
            ('year', 2021),
        ):
            record = publisher_paper()
            record[field] = value
            record['evidence_urls'] = [record['url'], record['pdf_url']]
            self.assertTrue(errors_for([record]))
        for evidence in ([], [publisher_paper()['url']], [publisher_paper()['pdf_url']],
                         [publisher_paper()['url'] + '?source=1', publisher_paper()['pdf_url']]):
            record = publisher_paper()
            record['evidence_urls'] = evidence
            self.assertTrue(errors_for([record]))

    def test_invalid_fields_fail_without_crashing_or_bypassing_existing_checks(self):
        for field in ('url', 'pdf_url', 'evidence_urls', 'year', 'doi', 'arxiv_id'):
            for value in (None, False, '', [], {}):
                if field in ('doi', 'arxiv_id') and value is None:
                    continue
                with self.subTest(field=field, value=value):
                    record = publisher_paper()
                    record[field] = value
                    self.assertTrue(errors_for([record]))
        record = publisher_paper()
        record['arxiv_version_reviewed'] = 'v1'
        self.assertTrue(errors_for([record]))
        record = publisher_paper()
        record['runtime_tested'] = True
        self.assertTrue(errors_for([record]))

    def test_duplicate_publisher_identity_and_existing_catalog_stay_checked(self):
        first = publisher_paper()
        second = deepcopy(first)
        second['id'] = 'paper-second-fixture'
        self.assertTrue(any('duplicate canonical paper URL' in error
                            for error in errors_for([first, second])))
        existing = json.loads((ROOT / 'data/papers.json').read_text())
        self.assertEqual(errors_for(existing), [])


if __name__ == '__main__':
    unittest.main()
