"""Derive internal bibliography/catalog links without changing scan assertions."""
from __future__ import annotations

from collections import defaultdict
import re
from urllib.parse import urlsplit


def github_repository(value: str, *, artifact: bool = False) -> str | None:
    """Return an exact GitHub repository identity, never infer mirrors or owners."""
    if not isinstance(value, str) or any(character.isspace() for character in value):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme != 'https' or parsed.netloc.casefold() != 'github.com':
        return None
    parts = parsed.path.removeprefix('/').removesuffix('/').split('/')
    if len(parts) < 2 or any(part in ('', '.', '..') for part in parts):
        return None
    if len(parts) > 2 and (not artifact or parts[2] not in ('tree', 'blob') or len(parts) < 4):
        return None
    owner, repository = parts[:2]
    repository = re.sub(r'\.git$', '', repository, flags=re.I)
    if (not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?', owner)
            or not re.fullmatch(r'[A-Za-z0-9_.-]+', repository)
            or repository in ('.', '..') or '%' in parsed.path or '\\' in parsed.path):
        return None
    return f'{owner}/{repository}'.casefold()


def related_entry(kind: str, record: dict) -> dict:
    identifier = record['id']
    pattern = r'paper-[a-z0-9]+(?:-[a-z0-9]+)*' if kind == 'paper' else r'[a-z0-9]+(?:-[a-z0-9]+)*'
    if not isinstance(identifier, str) or not re.fullmatch(pattern, identifier):
        raise ValueError('Related entries require valid catalog identifiers')
    title_en = record['title'] if kind == 'paper' else record['name']
    title_zh = record['title_zh'] if kind == 'paper' else record.get('name_zh', title_en)
    if any(not isinstance(title, str) or not title.strip() for title in (title_en, title_zh)):
        raise ValueError('Related entries require bilingual display titles')
    route = 'papers' if kind == 'paper' else 'resources'
    return {
        'kind': kind, 'id': identifier, 'title_en': title_en, 'title_zh': title_zh,
        'href_en': f'/{route}/#{identifier}', 'href_zh': f'/zh/{route}/#{identifier}',
        'match_basis': 'bibliography-artifact-repository' if kind == 'paper' else 'curated-canonical-repository',
    }


def with_artifact_links(records: list[dict], papers: list[dict], resources: list[dict],
                        diagnostics: list[str] | None = None) -> list[dict]:
    """Project links from reviewed canonical sources; seed IDs are corroboration."""
    by_repository = defaultdict(dict)
    for paper in papers:
        if paper.get('verification') != 'source-reviewed':
            continue
        for field in ('code_url', 'project_url'):
            repository = github_repository(paper.get(field), artifact=True)
            if repository:
                key = ('paper', paper['id'])
                entry = by_repository[repository].setdefault(key, related_entry('paper', paper))
                entry.setdefault('artifact_fields', []).append(field)
    for resource in resources:
        if resource.get('verification') != 'source-reviewed':
            continue
        repository = github_repository(resource.get('url'))
        if repository:
            by_repository[repository][('curated', resource['id'])] = related_entry('curated', resource)

    result = []
    for original in records:
        record = dict(original)
        record.pop('related_entries', None)
        repository = github_repository(record.get('url'))
        name_repository = github_repository('https://github.com/' + str(record.get('full_name', '')))
        matches = by_repository.get(repository, {}) if repository and repository == name_repository else {}
        if matches:
            # Fresh nested objects keep the caller's data and sibling records independent.
            record['related_entries'] = [
                {**entry, **({'artifact_fields': sorted(set(entry['artifact_fields']))}
                            if 'artifact_fields' in entry else {})}
                for _, entry in sorted(matches.items(), key=lambda item: (item[0][0] != 'paper', item[0][1]))
            ]
        if diagnostics is not None:
            for identifier in record.get('seed_paper_ids', []):
                if isinstance(identifier, str) and ('paper', identifier) not in matches:
                    diagnostics.append(f"{record['id']}: a seed paper has no exact bibliography repository match.")
        result.append(record)
    return result
