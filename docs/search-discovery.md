# Search discovery

The collection serves the same public HTML to people and crawlers. The repository directory, curated catalog, paper bibliography and collection notes are available without JavaScript, in English and Simplified Chinese. The homepage links to each directory; structured data describes the visible content. The sitemap contains canonical HTML URLs. Source-review dates are not reused as page-modification timestamps.

`robots.txt` allows crawling. A genuine HTTP 404 handles missing pages. `llms.txt` is an optional plain-text navigation file; it is not an indexing requirement or a ranking guarantee. Google says ordinary search indexing and snippet eligibility are the prerequisites for its AI search features. See [Google's AI features guidance](https://developers.google.com/search/docs/appearance/ai-features) and the [llms.txt proposal](https://llmstxt.org/).

After a production deployment:

1. Check the live sitemap, canonical URLs, language alternates, public JSON and a deliberately missing URL.
2. Submit `https://awesomerea.org/sitemap.xml` in the verified Google Search Console property. Use URL Inspection to distinguish discovered, crawled, indexed and requested-for-indexing states. Do not equate submission with inclusion.
3. Run `python3 scripts/submit_indexnow.py` to preview the canonical URL batch, then `python3 scripts/submit_indexnow.py --submit`. The command first checks that the live sitemap and public ownership file match this build. It only submits awesomerea.org URLs. A 200 means receipt; a 202 means key validation is pending. Neither confirms indexing. See the [IndexNow protocol](https://www.indexnow.org/documentation).

`site/indexnow.txt` is intentionally public domain-ownership proof. It is not an account password, API credential or login token. Google DNS verification records belong in the domain's DNS configuration, not in source code. Search Console accounts, private analytics, DNS account identifiers and credentials must never be committed.

The public GitHub README links to the website and the full bilingual bibliography. A domain verification key does not authorize submitting GitHub URLs as owned-site URLs. Search rankings, citations and stars must be reported from observed results, never inferred from metadata or crawler user-agent tests.
