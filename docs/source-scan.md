# Automated source index

The [source index](../data/source-index.json) is a separate discovery layer from the curated catalog. Its records are **automated README scans**, not individually reviewed recommendations.

Initial completed snapshot: **1,600 distinct repository READMEs**, retrieved between 2026-10-16 01:34:02 and 01:37:38 UTC. The 29 queries discovered 2,020 unique candidates; 1,611 were attempted, 11 failed (10 HTTP 404 responses and one empty README), and 409 were not attempted after reaching the target. The successful scan read 16,525,491 bytes and produced 1,596 distinct content hashes. Different repositories can carry identical README content.

Latest incremental batch: **400 new successful README scans** from 405 attempts, completed on 2026-10-16 at 07:15:17 UTC. The index now retains **2,000 successful scans** and **16 failed attempts**. All original 1,600 records and 11 failures remain unchanged. The batch added 32 previously unscanned curated repositories and used 10 focused technology/reverse-engineering search queries. The combined scan records contain 20,426,367 README bytes and 1,996 distinct content hashes.

The current ID-backed discovery population contains 2,180 repositories, with 164 not attempted. The original 409 unattempted candidates had no saved identity list; they are not added to this union unless rediscovered. Their original counts are retained in `meta.resume_history`, alongside the original snapshot hash. `meta.current_run` records the new batch separately.

The authoritative counts and collection window are in the index's `meta` object. `successful_readme_scans` counts distinct public GitHub repositories whose README content was actually retrieved, decoded, inspected for document features, and SHA-256 hashed. Search result totals, discovered candidates, missing READMEs, and failed requests are not included in that number.

## Collection scope

The scan retains **2,000 repository records** as discovery evidence. A separate [scope review](../data/source-scope.json) excludes **21 clearly unrelated results** from collection browsing, leaving **1,979 browsable repositories**. These exclusions cover biological sequencing, financial analysis, personal profiles, language-research question classification, chart digitization, a UI animation, ordinary Bluetooth repair, general application utilities, original educational games, and unrelated development tooling. The original scan, source descriptions, and successful-scan count remain unchanged.

Each exclusion is keyed by the stable source ID and records its decision, bilingual reason, review date, exact scanned README SHA-256, and matching README URL. The [scope helper](../scripts/source_scope.py) validates those bindings and annotates generated records with `scope_status: excluded` and `scope_review`; it does not delete scan evidence. If a source snapshot changes, its scope decision must be reviewed again before reuse.

The remaining 1,979 entries have not all received individual relevance or functionality review. They are a discovery collection, separate from the **96 curated, source-reviewed resources**. Missing target tags alone do not justify exclusion: the unclassified records include game decompilations, language decompilers, and hardware protocol research. Scope decisions are also separate from licensing, safety, and REA compatibility judgments.

## What was scanned

Queries cover reverse engineering, binary analysis, Ghidra, IDA, Frida, decompilers, disassemblers, firmware analysis, Android, game reconstruction, JavaScript deobfuscation, protocol analysis and related tools. Every executed query, page, result count, timestamp and incomplete-result flag is recorded. Repositories are deduplicated by GitHub's numeric repository ID; private repositories, forks and archived repositories are excluded.

The scanner performs a real [Get a repository README](https://docs.github.com/en/rest/repos/contents#get-a-repository-readme) request for each candidate it attempts. It records the README's URL, Git blob identifier, SHA-256 digest, byte count, line count, a bounded heading count and detected installation/usage/requirements/example/license sections. Full README bodies are discarded rather than republished. No code, installers, binaries, tests or commands from a repository are executed.

Repository descriptions remain in their original upstream language in `data/source-index.json`. For historical schema compatibility, `description_en` holds that source text even when it is not English, while `description_zh` mirrors it with status `not-translated`. The separate [localization files](../data/locales/README.md) supply English and Simplified Chinese descriptions for the website. Its generated source index retains the original in `description_original` and marks the derived descriptions as AI-assisted translations. Translation does not verify a repository's claims, safety, or compatibility.

These descriptions derive from attributed upstream text, not independent editorial reviews. The heading statistic counts distinct heading-like lines up to a cap of six; six means at least six, and no heading text is retained. Upstream content keeps its own license; the index does not relicense it.

## Read the labels correctly

- `readme-scanned` means an actual readable, nonempty README was retrieved successfully.
- `automated-readme-scan` does not mean manually reviewed, installed, tested, secure, licensed for reuse or integrated with REA.
- Targets and categories use repository metadata after removing URLs and separating MCP from network-protocol signals. Main tool functions take precedence over secondary game or firmware topics. Canonical matches in the curated catalog can add explicit target tags and a primary category; classification_origin and classification_reference_ids identify these cross-references. This is not a review of the full scanned repository or a REA compatibility claim. An empty target list means insufficient metadata.
- Stars and license identifiers are GitHub metadata snapshots. A license identifier is not a review of a project's complete licensing terms.
- `failures` records attempted repositories that did not produce a successful README scan. `unattempted_candidates` records the discovered candidates left over after reaching the requested successful-scan target.

The curated `source-reviewed` records remain in [rea-resources.json](../data/rea-resources.json) and [tool-resources.json](../data/tool-resources.json). Promotion from this source index requires a separate human or agent editorial review under the [contribution rules](../CONTRIBUTING.md).

## Reproduce a scan

Use Python 3.10 or newer and an already authenticated GitHub CLI:

```sh
python3 scripts/scan_sources.py --target 1600 --workers 16 --requests-per-second 12
```

The default output is `data/source-index.json`. Use `--output` to write another snapshot. The script keeps authentication in process memory, sends it only to `api.github.com`, and refuses redirects that would send it elsewhere. It never writes or logs the credential.

## Continue without replacing earlier evidence

Use a different output path for an incremental batch. For example, continue from the current 2,000-record snapshot toward 2,400 successful reads:

```sh
python3 scripts/scan_sources.py --resume data/source-index.json --output .cache/source-index-next.json --target 2400 --seed-curated --workers 32 --requests-per-second 12 --candidate-buffer 100
```

The scanner preserves earlier record objects, hashes, timestamps, failed attempts, and query observations. It skips previously attempted IDs, adds a persisted `discovered_repository_ids` ledger, and records per-run counts and provenance. Curated GitHub references can be seeded before search; they pass the same public/non-fork/non-archived eligibility gates. Seed observations are separate from search-query evidence.

Repeat `--query 'topic:javascript topic:reverse-engineering'` to supply focused search bases instead of the defaults; the public/non-fork/non-archived gates are appended automatically. The exact ordered plan and executed queries are in `meta.current_run.query_plan` and `meta.queries`. An interrupted checkpoint can be resumed to a different output path without re-reading its completed sources.

Before replacing the canonical snapshot, add both-language descriptions for every new ID, review clear scope mismatches, regenerate both repository directories, and run validation. An in-progress checkpoint is not publishable. The source index keeps upstream text and original evidence; translation and scope decisions remain separate.

Search calls are spaced by at least 2.1 seconds; README requests share a bounded request rate and a worker limit. HTTP rate-limit responses trigger a shared wait and retry, and progress checkpoints are saved after each 100 attempted READMEs. GitHub limits each search to at most 1,000 results, so the scanner uses distinct topical queries and records its pagination limits. See [GitHub search behavior](https://docs.github.com/en/rest/search/search#about-search) and [REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

This is not a complete census of reverse engineering software. Search vocabulary, repository metadata, star ordering, API availability and the configured scan budget affect coverage. README URLs may change later; hashes and Git blob identifiers preserve the identity of the observed content. A successful scan is a starting point for investigation, not a product recommendation.
