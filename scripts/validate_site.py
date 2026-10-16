#!/usr/bin/env python3
"""Check generated canonical pages, structured data, local links and ownership files."""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'dist'
ORIGIN = 'https://awesomerea.org'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.canonicals, self.ids, self.schemas, self.alternates = [], [], [], [], []
        self.noindex, self.lang, self.json_script = False, None, None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        assert len(values) == len(attrs), f'Duplicate HTML attributes on {tag}'
        if tag == 'html':
            self.lang = values.get('lang')
        if values.get('id'):
            self.ids.append(values['id'])
        if tag in ('a', 'link') and values.get('href'):
            self.links.append(values['href'])
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

    def handle_endtag(self, tag):
        if tag == 'script' and self.json_script is not None:
            self.schemas.append(json.loads(self.json_script))
            self.json_script = None


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


def main():
    urls = [element.text for element in ET.parse(OUTPUT / 'sitemap.xml').findall('{*}url/{*}loc')]
    assert urls and len(urls) == len(set(urls)), 'Duplicate or empty sitemap'
    for url in urls:
        parsed = urlsplit(url)
        assert parsed.netloc == 'awesomerea.org' and parsed.scheme == 'https' and not parsed.query and not parsed.fragment
        path = OUTPUT / parsed.path.lstrip('/') / 'index.html'
        text = path.read_text()
        assert not re.search(r'\{\{[A-Z_]+\}\}', text), f'Unresolved template in {parsed.path}'
        page = Page(text)
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
    assert Page((OUTPUT / '404.html').read_text()).noindex, '404 must be noindex'
    assert (OUTPUT / 'llms.txt').read_text().startswith('# '), 'llms.txt must contain Markdown'
    assert re.fullmatch(r'[a-f0-9]{32}\n?', (OUTPUT / 'indexnow.txt').read_text()), 'Invalid public ownership proof'
    print(f'Validated {len(urls)} canonical HTML pages, language alternatives, JSON-LD, local links and discovery files.')


if __name__ == '__main__':
    main()
