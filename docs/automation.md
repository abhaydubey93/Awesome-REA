# Repository automation

The repository validates changes in CI and posts a rule-based review on pull requests. It does not automatically approve or merge contributions.

## Pull request review

`Automated PR review` uses the trusted base branch's reviewer. It retrieves selected JSON files as data from the exact PR commit and checks schema, duplicate IDs and URLs, source records, bilingual coverage, scope decisions, target labels, dates, and benchmark consistency. Source-index, localization, and scope changes are checked together against unchanged dependencies from the trusted base. Automated source scans retain a separate status from curated resources.

The reviewer also checks added patch text for common credential patterns, personal absolute paths, private configuration, raw output, and licensed font files. Reports identify the file and problem without repeating suspected secrets. Pattern checks are a backstop, not a complete secret audit.

The job can write a review comment but does not check out or run the contributor's code, fetch contributor-provided external links, approve the PR, or merge it. Code and workflow changes remain subject to maintainer review. Reviews are attached to a specific head commit. Every run revalidates the data; a repeated run updates the existing bot review and preserves the current check result.

## Continuous integration

`Catalog checks` runs on pushes and PRs. It validates curated data and local Markdown links, checks generated README sections and the bilingual repository directory, builds the collection website, and checks JavaScript syntax. The workflow has read-only repository permissions.

The `main` branch requires the GitHub Actions `validate` and `review` checks, an up-to-date branch, and a pull request before merging. These rules also apply to administrators; force pushes and branch deletion are disabled. No human approval count is imposed, and the bot's review comment is not an approval. Use a feature branch and merge after the required checks pass.

The localization path was exercised in [PR #2](https://github.com/reacher-z/Awesome-REA/pull/2): valid data passed, an intentionally missing Chinese description failed both jobs, and restored data passed. Rerunning the reviewer updated the same head-specific bot review.

`Source links` runs weekly and on manual request. It distinguishes confirmed missing links from rate limits and inconclusive network responses.

## Website delivery

See [website building and publishing](website.md) for the static build and hosting setup. Production uses the public source repository while optional Font Awesome Pro assets are supplied through the licensed deployment path. Pro fonts, credentials, private configuration, raw analysis output, and deployment bundles are excluded from the public repository.

The production build command runs `scripts/build_production.py`. It stops deployment if catalog validation or JavaScript syntax validation fails. Cloudflare's existing Git connection builds each change to `main` and creates PR previews; no deployment API token is stored in this repository.
