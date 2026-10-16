# Resource catalog format

`rea-resources.json` and `tool-resources.json` contain the records rendered into both READMEs. They are arrays of objects with these required fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable lowercase slug, unique across both files |
| `name` | Upstream project or resource name |
| `url` | Canonical public destination |
| `category` | Task or tool family |
| `kind` | Resource type: project, tool, integration, case-study, collection, documentation, learning-resource, or research |
| `targets` | One or more browsing domains: `website`, `game`, `app`, `binary`, `firmware`; these describe task fit, not verified REA integration |
| `relationship` | Relationship to REA, independent integration, foundation, or learning |
| `description_en` / `description_zh` | Original practical descriptions |
| `evidence_url` | Primary source supporting the description |
| `additional_evidence_urls` | Optional supporting documentation, release, or package-metadata URLs; these are validated and included in link checks |
| `verified_at` | ISO date or timestamp of source review |
| `verification` | `source-reviewed`; not a runtime compatibility claim |
| `requirements` | Platform, engine, release, license, or input prerequisites |

Inspect available categories and relationships with `python3 scripts/catalog.py --json`. Source review dates are snapshots; upstream requirements may change. A documentation link on `main` may describe functionality that is not in a released package; keep that distinction in the description or requirements.

`benchmarks.json` is a separate repository comparison dataset. Star counts are observations at `observed_at`, not a live ranking, quality score, or predicted growth rate. The comparison notes explain the population and limitations.

`papers.json` is a separate bibliography, rendered into the [English paper directory](https://awesomerea.org/papers/), [Chinese paper directory](https://awesomerea.org/zh/papers/), and both READMEs. The bibliography is counted separately from the repository scans. Some papers also appear in the curated collection, so paper and curated totals must not be added as unique entries. Records preserve original titles and author names, publication venue and status, date precision, DOI/arXiv identifiers, public primary sources, bilingual summaries and scope limitations. Chinese titles are translations. A preprint is labeled as such; an open paper does not imply an open dataset or evaluation service. Code links require an author-provided source. Review dates describe bibliography checks, not publication dates or reproduced results.

Search the bibliography with `python3 scripts/catalog.py --papers --target website`, add a query such as `interaction`, or use `--language zh` for Chinese output. `--json` returns matching source records for tools and agents. Paper search is separate from `--source-index` and the default curated-resource search.

`source-index.json` contains the separate automated discovery index: 2,500 distinct repository READMEs were retrieved and hashed. It preserves collection queries, successful and failed counts, source URLs, README hashes, timestamps, metadata, and automatic topic labels. Upstream descriptions remain unchanged in this source snapshot. See the [scan method](../docs/source-scan.md).

The [repository locales](locales/README.md) provide derived English and Simplified Chinese descriptions for all 2,500 records. The website build combines these files with the source index and retains the upstream text as `description_original` in its generated data. New or changed source records also require locale updates. Translation helps browse the collection; it does not verify upstream claims or promote a record to `source-reviewed`.

[source-scope.json](source-scope.json) records evidence-bound scope exclusions without deleting successful scans. The website and [bilingual GitHub directory](../docs/repositories/README.md) omit excluded records from browsing. The downloadable full index keeps all scan records and the exclusion reasons; the separate curated catalog contains only curated entries.
