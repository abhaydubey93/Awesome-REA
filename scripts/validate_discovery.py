#!/usr/bin/env python3
"""Check the built site's crawlable routes, metadata, languages, and source coverage."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"
ORIGIN = "https://awesomerea.org"


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.meta, self.ids, self.resources, self.graphs = [], {}, set(), [], []
        self.language = None
        self.h1 = 0
        self.in_json = False
        self.json_parts = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.language = attrs.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "link":
            self.links.append(attrs)
        if tag == "meta":
            self.meta[attrs.get("name") or attrs.get("property")] = attrs.get("content", "")
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if "data-resource-id" in attrs:
            self.resources.append(attrs["data-resource-id"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_json = True
            self.json_parts = []

    def handle_data(self, data):
        if self.in_json:
            self.json_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_json:
            self.graphs.append(json.loads("".join(self.json_parts)))
            self.in_json = False


def main():
    sitemap = ET.parse(OUTPUT / "sitemap.xml")
    urls = [node.text for node in sitemap.findall("{*}url/{*}loc")]
    assert len(urls) == len(set(urls)), "Duplicate sitemap URLs"
    documents = {}
    for url in urls:
        parsed = urlsplit(url)
        assert parsed.scheme + "://" + parsed.netloc == ORIGIN, url
        assert not parsed.query and not parsed.fragment, url
        path = OUTPUT / parsed.path.lstrip("/") / "index.html"
        assert path.is_file(), f"Sitemap route does not exist: {url}"
        page = Document(path.read_text())
        documents[url] = page
        assert page.h1 == 1, f"Expected one H1: {url}"
        assert page.meta.get("description"), f"Missing description: {url}"
        assert not {"noindex", "nosnippet", "none"}.intersection(
            page.meta.get("robots", "").lower().replace(",", " ").split()), url
        canonical = [link.get("href") for link in page.links if link.get("rel") == "canonical"]
        assert canonical == [url], f"Canonical mismatch: {url}"
        assert page.language == ("zh-CN" if parsed.path.startswith("/zh/") else "en"), url
        assert page.graphs, f"No structured metadata: {url}"
        for document in page.graphs:
            assert document.get("@context") == "https://schema.org", url
            for entity in document.get("@graph", []):
                if entity.get("@type") == "ItemList":
                    elements = entity["itemListElement"]
                    assert entity["numberOfItems"] == len(elements), url
                    assert [e["position"] for e in elements] == list(range(1, len(elements) + 1)), url
                    for item in elements:
                        destination = urlsplit(item["url"])
                        if destination.fragment and item["url"].startswith(url + "#"):
                            assert unquote(destination.fragment) in page.ids, item["url"]
    for url, page in documents.items():
        for link in page.links:
            if link.get("rel") != "alternate" or "hreflang" not in link:
                continue
            other = documents.get(link["href"])
            assert other is not None, f"Language alternative absent from sitemap: {url}"
            assert any(item.get("rel") == "alternate" and item.get("href") == url for item in other.links), url
    records = json.loads((OUTPUT / "catalog.json").read_text())["resources"]
    expected = {r["id"] for r in records}
    for path in ("/resources/", "/zh/resources/"):
        page = documents[ORIGIN + path]
        assert len(page.resources) == len(expected) and set(page.resources) == expected, path
    robots = RobotFileParser()
    robots.parse((OUTPUT / "robots.txt").read_text().splitlines())
    for bot in ("Googlebot", "bingbot", "OAI-SearchBot", "PerplexityBot"):
        assert all(robots.can_fetch(bot, url) for url in urls), f"Robots blocks {bot}"
    assert ORIGIN + "/sitemap.xml" in (robots.site_maps() or []), "Missing sitemap declaration"
    assert (OUTPUT / "llms.txt").is_file(), "Missing optional catalog index"
    assert len(urls) == len(list(OUTPUT.rglob("index.html"))), "A generated page is absent from the sitemap"
    print(f"Discovery checks passed: {len(urls)} canonical pages, reciprocal languages, {len(records)} static curated entries per language, JSON-LD, and crawler permissions.")


if __name__ == "__main__":
    main()
