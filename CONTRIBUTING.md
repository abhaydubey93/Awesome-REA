# Contributing to Awesome Reverse Engineering Anything

Help keep this collection useful, well organized, and current. Contributions can add a project, tool, case study, integration, related collection, or reference; correct an entry; or improve its category and description.

## Suggest a resource

Use the resource issue template or submit a pull request with:

- **Name and original URL** — prefer the project maintainer's repository or website.
- **Resource type** — project, tool, integration, case study, collection, documentation, learning resource, or research.
- **Target area** — Website, Game, App, Binary, or Firmware; multiple areas are allowed.
- **Short description** — explain what the resource provides in your own words.
- **Relevant conditions** — include platform, license, release, or external-tool requirements when they affect the description.

Check the existing collection before adding a duplicate. A resource does not need a minimum number of Stars. Prefer original, maintained projects over copied forks. Claims about REA integration should be supported by the project's own documentation.

## Update the catalog

Curated records live in `data/rea-resources.json` and `data/tool-resources.json`. Keep the English and Chinese descriptions concise. Use `kind` for the resource type and `targets` for its application areas; these are different dimensions. The website's translated names and requirements are in `site/translations.zh-CN.json`.

Record a primary source and review date. `source-reviewed` means documentation was checked; it does not claim that the project was installed, audited, or reproduced. The larger `data/source-index.json` is an automated repository index and retains its separate provenance.

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 scripts/build_site.py
node --check site/app.js
```

Use `python3 scripts/check_links.py` for live source checks. Rate limits and temporary network failures are reported separately from confirmed missing links.

## Suggest a research paper

Use the [paper submission form](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml). Include the canonical paper page or DOI, its publication status, the reverse-engineering task it studies, and links to author-provided code or data where available. An accessible paper does not imply that its benchmark or evaluation service is public.

Bibliographic records live in `data/papers.json`, separately from the tool catalog and automated scan index. For a pull request, follow an existing record and preserve the original title and full author names. Supply English and Chinese titles, summaries, relevance and limitations; distinguish preprints, conference acceptance, published proceedings and journal articles. Journal articles use `journal-article` and export as BibTeX `@article`; the journal title belongs in `venue`. Record only the verified date precision: never invent a publication day or conference date. Keep `runtime_tested` false unless the catalog schema and independent reproduction evidence are explicitly extended. Run `python3 scripts/validate_papers.py`, regenerate both READMEs, then run `python3 scripts/build_production.py`.

Use a verified paper DOI or arXiv identifier whenever available. Never substitute a software or dataset DOI for a paper identifier. A published conference paper without either may use a reviewed publisher identity: the initial supported profile is a canonical USENIX Security presentation URL and its matching final `secYY-presenter.pdf`, with the same publication year and both exact URLs in `evidence_urls`. Other publisher profiles require a separate validator review. Preprints and accepted-but-unpublished papers still require a paper identifier. URL matching records an auditable source-review contract; reviewers must verify the actual publication, authors, date and PDF.

## Reconstruction cases

Cases may use REA, other agents, or independent reverse-engineering tools. Use `independent-reconstruction` for a documented reconstruction project with no established REA connection, and `reconstruction-cases` as its category. The `targets` describe the actual Website, Game, App, Binary or Firmware domain. Identify author-reported results, incomplete behavior, platform limits and required original assets. Keep a pinned public source where possible; never include proprietary target binaries or private captures.

## Review and publication

Pull requests receive a [rule-based review](docs/automation.md) from trusted base-branch code. It checks catalog structure, duplicates, source fields, and common privacy mistakes without executing contributor code. Maintainers review resource relevance and factual claims. Passing automation does not automatically approve or merge a contribution.

The protected `main` branch requires the `validate` and `review` checks before merging, including for administrators. After changes reach `main`, the connected Cloudflare Pages project runs the collection checks and publishes the website. See the [website maintenance guide](docs/website.md).

Do not include credentials, private account details, personal filesystem paths, proprietary binaries, raw private captures, or licensed Font Awesome Pro files in the public repository. Original contributions use the repository's MIT license; linked resources retain their own licenses.
