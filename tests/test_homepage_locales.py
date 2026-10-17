"""Cover literal extraction, static language delivery and unrelated markup preservation."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from homepage_locales import localized_homepage, _Document, _ui_strings

APP = (ROOT / 'site/app.js').read_text()
TEMPLATE = (ROOT / 'site/index.html').read_text()
ORIGIN = 'https://awesomerea.org'


def nodes(html, tag):
    return [node for node in _Document(html).nodes if node['tag'] == tag]


def content(html, node):
    return html[node['inner']:node['close']]


def fixture():
    website = {'@type': 'WebSite', '@id': ORIGIN + '/#website', 'name': 'Original identity',
               'url': ORIGIN + '/', 'inLanguage': ['en', 'zh-CN']}
    page = {'@type': 'CollectionPage', '@id': ORIGIN + '/#collection', 'url': ORIGIN + '/',
            'name': 'English home', 'description': 'English intro', 'inLanguage': 'en',
            'isPartOf': {'@id': ORIGIN + '/#website'},
            'mainEntity': {'@type': 'ItemList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Research', 'url': ORIGIN + '/papers/#paper-example'}]}}
    schema = json.dumps({'@context': 'https://schema.org', '@graph': [website, page]})
    return f'''<!doctype html><html lang="en"><head>
<title>Old title</title><link rel="canonical" href="{ORIGIN}/">
<meta name="description" content="Old description"><meta property="og:title" content="Old">
<meta property="og:description" content="Old"><meta property="og:locale" content="en_US">
<meta property="og:url" content="{ORIGIN}/"><meta name="twitter:title" content="Old">
<meta name="twitter:description" content="Old"><meta property="og:image:alt" content="Old">
<link rel="stylesheet" href="styles.css?v=abc"><link rel="icon" href="./favicon.svg">
<script type="application/ld+json">{schema}</script><script src="app.js?v=abc" defer></script>
<script>window.neverExecuted = "preserved";</script></head><body>
<h1 data-i18n="collectionTitle">Old <span>title</span></h1>
<input data-i18n-placeholder="searchPlaceholder" data-i18n-aria="searchLabel" placeholder="old" aria-label="old">
<a data-locale-path="papers" href="/papers/?sort=year#paper-example">Papers</a>
<a data-locale-path="resources" data-locale-fragment="game" href="/resources/">Games</a>
<a href="/resources/#case">Case</a><a href="#catalog">Local</a>
<a href="https://example.org/papers/#external">External</a><a href="catalog.json?v=abc" download>JSON</a>
<img src="images/preview.png"><video poster="poster.png"></video>
<select id="language-select"><option value="en" selected>English</option><option value="zh">简体中文</option></select>
</body></html>'''


class HomepageLocaleTests(unittest.TestCase):
    def test_real_template_translates_every_existing_marker(self):
        for lang in ('en', 'zh'):
            with self.subTest(language=lang):
                html = localized_homepage(TEMPLATE, APP, lang)
                strings = _ui_strings(APP)[lang]
                for node in _Document(html).nodes:
                    attrs = node['attrs']
                    if 'data-i18n' in attrs:
                        self.assertEqual(content(html, node), strings[attrs['data-i18n']])
                    if 'data-i18n-placeholder' in attrs:
                        self.assertEqual(attrs['placeholder'], strings[attrs['data-i18n-placeholder']])
                    if 'data-i18n-aria' in attrs:
                        self.assertEqual(attrs['aria-label'], strings[attrs['data-i18n-aria']])
                self.assertEqual(nodes(html, 'html')[0]['attrs']['lang'], 'zh-CN' if lang == 'zh' else 'en')
                # Static localization does not replace data/build placeholders or SVG content.
                self.assertIn('{{RESOURCE_COUNT}}', html)
                original_svg = re.search(r'<svg class="symbol-bank"[\s\S]*?</svg>', TEMPLATE)[0]
                self.assertIn(original_svg, html)

    def test_metadata_schema_and_asset_routes(self):
        original = fixture(); html = localized_homepage(original, APP, 'zh')
        self.assertEqual(content(html, nodes(html, 'title')[0]), _ui_strings(APP)['zh']['pageTitle'])
        meta = {n['attrs'].get('name') or n['attrs'].get('property'): n['attrs']['content'] for n in nodes(html, 'meta')}
        self.assertEqual(meta['og:locale'], 'zh_CN')
        self.assertEqual(meta['og:url'], ORIGIN + '/zh/')
        self.assertEqual(meta['description'], _ui_strings(APP)['zh']['pageDescription'])
        self.assertEqual(meta['twitter:description'], meta['description'])
        links = [n['attrs'] for n in nodes(html, 'link')]
        self.assertEqual([n['href'] for n in links if n.get('rel') == 'canonical'], [ORIGIN + '/zh/'])
        self.assertEqual({n['hreflang']: n['href'] for n in links if n.get('rel') == 'alternate'},
                         {'en': ORIGIN + '/', 'zh-CN': ORIGIN + '/zh/', 'x-default': ORIGIN + '/'})
        self.assertIn('href="/styles.css?v=abc"', html)
        self.assertIn('src="/app.js?v=abc"', html)
        self.assertIn('src="/images/preview.png"', html)
        self.assertIn('poster="/poster.png"', html)
        self.assertIn('href="/catalog.json?v=abc"', html)
        self.assertIn('<script>window.neverExecuted = "preserved";</script>', html)
        before = json.loads(content(original, next(n for n in nodes(original, 'script') if n['attrs'].get('type') == 'application/ld+json')))
        after = json.loads(content(html, next(n for n in nodes(html, 'script') if n['attrs'].get('type') == 'application/ld+json')))
        self.assertEqual(before['@graph'][0], after['@graph'][0])
        page = after['@graph'][1]
        self.assertEqual((page['url'], page['@id'], page['inLanguage']), (ORIGIN + '/zh/', ORIGIN + '/zh/#collection', 'zh-CN'))
        self.assertEqual(page['mainEntity']['itemListElement'][0]['url'], ORIGIN + '/zh/papers/#paper-example')
        self.assertEqual(page['mainEntity']['itemListElement'][0]['name'], _ui_strings(APP)['zh']['directoryPapers'])

    def test_navigation_fragments_and_selected_language(self):
        html = localized_homepage(fixture(), APP, 'zh')
        hrefs = [n['attrs'].get('href') for n in nodes(html, 'a')]
        self.assertIn('/zh/papers/?sort=year#paper-example', hrefs)
        self.assertIn('/zh/resources/#case', hrefs)
        self.assertIn('/zh/resources/#game', hrefs)
        self.assertIn('#catalog', hrefs)
        self.assertIn('https://example.org/papers/#external', hrefs)
        options = {n['attrs']['value']: n['attrs'] for n in nodes(html, 'option')}
        self.assertNotIn('selected', options['en']); self.assertIn('selected', options['zh'])
        english = localized_homepage(html, APP, 'en')
        self.assertIn('href="/resources/#case"', english)
        self.assertNotIn('/zh/resources/#case', english)

    def test_output_is_deterministic_and_idempotent(self):
        for lang in ('en', 'zh'):
            once = localized_homepage(fixture(), APP, lang)
            self.assertEqual(once, localized_homepage(fixture(), APP, lang))
            self.assertEqual(once, localized_homepage(once, APP, lang))

    def test_literal_parser_handles_comments_quotes_and_escapes(self):
        source = r'''const UI = {"en": {/* note */ "value": 'it\'s \\ literal \u4e2d',},
        // language
        "zh": {"value": "中文 \uD83D\uDE00",},};
        throw new Error("must not execute");'''
        values = _ui_strings(source)
        self.assertEqual(values['en']['value'], "it's \\ literal 中")
        self.assertEqual(values['zh']['value'], '中文 😀')

    def test_nonliteral_values_duplicates_and_missing_keys_fail(self):
        invalid = [APP.replace('"Language"', 'getLanguage()', 1),
                   APP.replace('"Language"', '`Language`', 1),
                   APP.replace('"Language"', '"Lang" + "uage"', 1),
                   APP.replace('"en": {', '"en": {"pageTitle":"duplicate",', 1),
                   APP.replace('"searchLabel":', '"renamedSearchLabel":', 2)]
        for source in invalid:
            with self.subTest(source=source[:40]):
                with self.assertRaises(ValueError): localized_homepage(fixture(), source, 'zh')
        with self.assertRaises(ValueError): localized_homepage(fixture(), APP, 'fr')
        with self.assertRaises(ValueError): localized_homepage(fixture().replace('rel="canonical"', 'rel="other"'), APP, 'zh')

    def test_translation_html_cannot_introduce_executable_markup(self):
        source = APP.replace("'逆向工程资源合集<span class=\"title-dot\" aria-hidden=\"true\">.</span>'", "'<img src=x onerror=alert(1)>'")
        with self.assertRaises(ValueError): localized_homepage(fixture(), source, 'zh')
        source = APP.replace('"searchLabel": "搜索精选资源"', '"searchLabel": "A \\\"quoted\\\" label"')
        html = localized_homepage(fixture(), source, 'zh')
        self.assertEqual(nodes(html, 'input')[0]['attrs']['aria-label'], 'A "quoted" label')
        self.assertIn('aria-label="A &quot;quoted&quot; label"', html)

    def test_noscript_internal_links_keep_their_explicit_language(self):
        en = '<em>Browse</em> <a href="/papers/#paper-example">papers</a> <a href="/zh/" lang="zh-CN">中文</a>'
        zh = '<em>浏览</em><a href="/zh/papers/#paper-example">论文</a><a href="/" lang="en">English</a>'
        source = APP.replace('"en": {', '"en": {"noscriptNote":' + json.dumps(en) + ',').replace(
            '"zh": {', '"zh": {"noscriptNote":' + json.dumps(zh) + ',')
        original = fixture().replace('</body>', '<noscript><p data-i18n="noscriptNote">Old <a href="/papers/">link</a></p></noscript></body>')
        for lang, expected in [('en', en), ('zh', zh)]:
            html = localized_homepage(original, source, lang)
            paragraph = next(n for n in nodes(html, 'p') if n['attrs'].get('data-i18n') == 'noscriptNote')
            self.assertEqual(content(html, paragraph), expected)
            self.assertEqual(html, localized_homepage(html, source, lang))
        for unsafe in ['//example.org/', '/%2fexample.org/', '/\\example.org/', 'https://example.org/',
                       '/papers/" onclick="alert(1)', '/papers/" target="_blank',
                       '//example.org/" href="/papers/']:
            bad = APP.replace('"zh": {', '"zh": {"noscriptNote":' + json.dumps('<a href="' + unsafe + '">bad</a>') + ',')
            with self.subTest(href=unsafe), self.assertRaises(ValueError):
                localized_homepage(original, bad, 'zh')


if __name__ == '__main__':
    unittest.main()
