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

## Review and publication

Pull requests receive a [rule-based review](docs/automation.md) from trusted base-branch code. It checks catalog structure, duplicates, source fields, and common privacy mistakes without executing contributor code. Maintainers review resource relevance and factual claims. Passing automation does not automatically approve or merge a contribution.

The protected `main` branch requires the `validate` and `review` checks before merging, including for administrators. After changes reach `main`, the connected Cloudflare Pages project runs the collection checks and publishes the website. See the [website maintenance guide](docs/website.md).

Do not include credentials, private account details, personal filesystem paths, proprietary binaries, raw private captures, or licensed Font Awesome Pro files in the public repository. Original contributions use the repository's MIT license; linked resources retain their own licenses.
