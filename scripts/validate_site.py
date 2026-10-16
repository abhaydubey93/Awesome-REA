#!/usr/bin/env python3
"""Check generated canonical pages, structured data, local links and ownership files."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from build_manifest import read_build_manifest
from build_paper_pages import bibtex_text
from validate_papers import read_papers

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
ORIGIN = 'https://awesomerea.org'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.canonicals, self.ids, self.schemas, self.alternates = [], [], [], [], []
        self.noindex, self.lang, self.json_script = False, None, None
        self.paper_ids, self.paper_texts, self.paper_links = [], {}, {}
        self.current_paper = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        assert len(values) == len(attrs), f'Duplicate HTML attributes on {tag}'
        if tag == 'html':
            self.lang = values.get('lang')
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'article' and 'data-paper-id' in values:
            assert self.current_paper is None, 'Nested paper articles are invalid'
            identifier = values['data-paper-id']
            assert values.get('id') == identifier, 'Paper fragment and data-paper-id differ'
            self.paper_ids.append(identifier)
            self.paper_texts[identifier], self.paper_links[identifier] = [], []
            self.current_paper = identifier
        if tag in ('a', 'link') and values.get('href'):
            self.links.append(values['href'])
            if self.current_paper:
                self.paper_links[self.current_paper].append(values['href'])
        if tag == 'link' and values.get('rel') == 'canonical':
            self.canonicals.append(values.get('href'))
        if tag == 'link' and values.get('rel') == 'alternate' and values.get('hreflang'):
            self.alternates.append((values['hreflang'], values['href']))
        if tag == 'meta' and values.get('name') == 'robots' and 'noindex' in values.get('content', ''):
            self.noindex = True
        if tag == 'script' and values.get('type') == 'application/ld+json':
            self.json_script = ''

    def handle_data(self, data):
        if self.json_script is not None:
            self.json_script += data
        elif self.current_paper:
            self.paper_texts[self.current_paper].append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.json_script is not None:
            self.schemas.append(json.loads(self.json_script))
            self.json_script = None
        if tag == 'article':
            self.current_paper = None


def structured_checks(value):
    if isinstance(value, list):
        for child in value:
            structured_checks(child)
    elif isinstance(value, dict):
        if value.get('@type') == 'ItemList':
            assert value['numberOfItems'] == len(value['itemListElement']), 'Structured item count mismatch'
        assert 'aggregateRating' not in value, 'Do not misrepresent stars as ratings'
        for child in value.values():
            structured_checks(child)


def schema_entities(value, type_name):
    if isinstance(value, list):
        for item in value:
            yield from schema_entities(item, type_name)
    elif isinstance(value, dict):
        if value.get('@type') == type_name:
            yield value
        for item in value.values():
            yield from schema_entities(item, type_name)


def validate_paper_outputs(output, pages, source_papers=None):
    """Bind both rendered bibliographies and every citation to the source JSON."""
    output = Path(output)
    source_papers = read_papers(ROOT) if source_papers is None else source_papers
    built = json.loads((output / 'papers.json').read_text(encoding='utf-8'))
    assert built == source_papers, 'Built papers.json differs from the source bibliography'
    expected = {paper['id']: paper for paper in built}
    assert len(expected) == len(built), 'Duplicate built paper IDs'
    catalog = json.loads((output / 'catalog.json').read_text(encoding='utf-8'))
    assert catalog['meta']['paper_count'] == len(expected), 'Catalog paper count differs from the bibliography'
    statuses = {'conference-paper': ('Conference paper', '会议论文'),
                'conference-accepted': ('Conference accepted', '会议已接收'),
                'preprint': ('Preprint', '预印本')}
    normalize = lambda text: ' '.join(text.split())
    for route, language in (('/papers/', 'en'), ('/zh/papers/', 'zh')):
        assert route in pages, f'Paper route is missing from the sitemap: {route}'
        page = pages[route]
        assert len(page.paper_ids) == len(expected) and set(page.paper_ids) == set(expected), f'Paper DOM coverage mismatch: {route}'
        listings = list(schema_entities(page.schemas, 'ItemList'))
        assert len(listings) == 1, f'Expected one paper ItemList: {route}'
        items = listings[0]['itemListElement']
        assert listings[0]['numberOfItems'] == len(expected), f'Paper ItemList source count mismatch: {route}'
        assert items == [
            {'@type': 'ListItem', 'position': position, 'url': ORIGIN + route + '#' + identifier,
             'item': {'@id': expected[identifier]['url']}}
            for position, identifier in enumerate(page.paper_ids, 1)
        ], f'Paper ItemList differs from visible paper order or identities: {route}'
        articles = list(schema_entities(page.schemas, 'ScholarlyArticle'))
        by_url = {article.get('@id'): article for article in articles}
        assert len(articles) == len(by_url) == len(expected) and set(by_url) == {p['url'] for p in built}, f'ScholarlyArticle coverage mismatch: {route}'
        for identifier in page.paper_ids:
            paper = expected[identifier]
            article = {
                '@type': 'ScholarlyArticle', '@id': paper['url'], 'url': paper['url'],
                'name': paper['title'], 'headline': paper['title'], 'alternateName': paper['title_zh'],
                'author': [{'@type': 'Person', 'name': name} for name in paper['authors']],
                'description': paper[f'description_{language}'],
                'creativeWorkStatus': statuses[paper['publication_status']][0],
                'isPartOf': {'@type': 'CreativeWork', 'name': paper['venue']},
                'encoding': {'@type': 'MediaObject', 'encodingFormat': 'application/pdf', 'contentUrl': paper['pdf_url']},
            }
            if paper.get('publication_date'):
                article['datePublished'] = paper['publication_date']
            identifiers = [
                {'@type': 'PropertyValue', 'propertyID': label, 'value': paper[field]}
                for field, label in (('doi', 'DOI'), ('arxiv_id', 'arXiv')) if paper.get(field)
            ]
            if identifiers:
                article['identifier'] = identifiers
            assert by_url[paper['url']] == article, f'ScholarlyArticle fields differ from source: {identifier} ({language})'
            text = normalize(' '.join(page.paper_texts[identifier]))
            phrases = [paper['title_zh'] if language == 'zh' else paper['title'],
                       '; '.join(paper['authors']), paper['venue'], statuses[paper['publication_status']][language == 'zh'],
                       paper[f'description_{language}'], paper[f'scope_limitations_{language}'], paper[f'why_fits_{language}'],
                       paper['date_basis_zh' if language == 'zh' else 'date_basis'],
                       paper['metadata_notes_zh' if language == 'zh' else 'metadata_notes']]
            if language == 'zh':
                phrases.append(paper['title'])
            assert all(normalize(phrase) in text for phrase in phrases), f'Visible paper text differs from source: {identifier} ({language})'
            links = {paper['url'], paper['pdf_url'], *paper['evidence_urls'], f'/papers/citations/{identifier}.bib'}
            links.update(paper[field] for field in ('code_url', 'project_url') if paper.get(field))
            assert links <= set(page.paper_links[identifier]), f'Visible paper source or citation link missing: {identifier} ({language})'
    citations = output / 'papers' / 'citations'
    assert {path.name for path in citations.glob('*.bib')} == {identifier + '.bib' for identifier in expected}, 'BibTeX file coverage differs from the bibliography'
    entries = []
    for paper in built:
        entry = bibtex_text(paper)
        assert (citations / (paper['id'] + '.bib')).read_text(encoding='utf-8') == entry, f'BibTeX content differs from source: {paper["id"]}'
        entries.append(entry)
    bibliography = '% Generated from source-reviewed metadata. Author names retain their listed order without inferred surname parsing.\n\n' + ''.join(entry + '\n' for entry in entries)
    assert (output / 'papers' / 'references.bib').read_text(encoding='utf-8') == bibliography, 'Combined BibTeX differs from the source bibliography'


def main():
    urls = [element.text for element in ET.parse(OUTPUT / 'sitemap.xml').findall('{*}url/{*}loc')]
    assert urls and len(urls) == len(set(urls)), 'Duplicate or empty sitemap'
    pages = {}
    for url in urls:
        parsed = urlsplit(url)
        assert parsed.netloc == 'awesomerea.org' and parsed.scheme == 'https' and not parsed.query and not parsed.fragment
        path = OUTPUT / parsed.path.lstrip('/') / 'index.html'
        text = path.read_text()
        assert not re.search(r'\{\{[A-Z_]+\}\}', text), f'Unresolved template in {parsed.path}'
        page = Page(text)
        pages[parsed.path] = page
        assert page.canonicals == [url] and not page.noindex, f'Canonical/indexing mismatch: {parsed.path}'
        assert not [key for key, count in Counter(page.ids).items() if count > 1], f'Duplicate HTML IDs: {parsed.path}'
        assert page.schemas, f'Missing structured data: {parsed.path}'
        for schema in page.schemas:
            structured_checks(schema)
        if parsed.path != '/':
            english = parsed.path.removeprefix('/zh') if parsed.path.startswith('/zh/') else parsed.path
            expected = {'en': ORIGIN + english, 'zh-CN': ORIGIN + '/zh' + english, 'x-default': ORIGIN + english}
            assert len(page.alternates) == 3 and dict(page.alternates) == expected, f'Incorrect reciprocal language alternatives: {parsed.path}'
        assert page.lang == ('zh-CN' if parsed.path.startswith('/zh/') else 'en')
        for link in page.links:
            target = urlsplit(link)
            if target.netloc not in ('', 'awesomerea.org') or target.scheme not in ('', 'https'):
                continue
            local = OUTPUT / unquote(target.path).lstrip('/') if target.path.startswith('/') else path.parent / unquote(target.path)
            if not target.path:
                local = path
            if local.is_dir():
                local /= 'index.html'
            assert local.is_file(), f'Missing local link on {parsed.path}: {link}'
    validate_paper_outputs(OUTPUT, pages)
    assert Page((OUTPUT / '404.html').read_text()).noindex, '404 must be noindex'
    assert (OUTPUT / 'llms.txt').read_text().startswith('# '), 'llms.txt must contain Markdown'
    assert re.fullmatch(r'[a-f0-9]{32}\n?', (OUTPUT / 'indexnow.txt').read_text()), 'Invalid public ownership proof'
    read_build_manifest(OUTPUT)
    print(f'Validated {len(urls)} canonical HTML pages, paper/source/citation coverage, language alternatives, JSON-LD, local links and the deployment manifest.')


if __name__ == '__main__':
    main()
