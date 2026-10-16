"""Load and validate the repository description localization layer."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LOCALE_FILES = tuple(f'data/locales/repositories-{part}.json' for part in (1, 2, 3))


def read_localizations(root=ROOT):
    translations = {}
    for filename in LOCALE_FILES:
        path = root / filename
        if not path.exists():
            continue
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f'{filename}: duplicate JSON key')
                result[key] = value
            return result
        entries = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        if not isinstance(entries, dict):
            raise ValueError(f'{filename}: expected an object keyed by resource ID')
        overlap = translations.keys() & entries.keys()
        if overlap:
            raise ValueError(f'{filename}: duplicate localization IDs')
        translations.update(entries)
    return translations


def validate_localizations(records, translations, errors):
    expected = {record['id'] for record in records}
    if set(translations) != expected:
        errors.append(f'Repository localization coverage: {len(expected - set(translations))} missing and {len(set(translations) - expected)} unknown IDs.')
    for record in records:
        identifier = record['id']
        entry = translations.get(identifier)
        if not isinstance(entry, dict):
            errors.append(f'{identifier}: localization must be an object')
            continue
        allowed = {'description_en', 'description_zh', 'english_retains_name', 'technical_only'}
        if set(entry) - allowed:
            errors.append(f'{identifier}: unknown localization fields')
        for flag in ('english_retains_name', 'technical_only'):
            if flag in entry and not isinstance(entry[flag], bool):
                errors.append(f'{identifier}: {flag} must be a boolean')
        for field in ('description_en', 'description_zh'):
            value = entry.get(field)
            if not isinstance(value, str):
                errors.append(f'{identifier}: missing localized {field}')
            elif record.get('description_en') and not value.strip():
                errors.append(f'{identifier}: empty localized {field}')
            elif not record.get('description_en') and value:
                errors.append(f'{identifier}: preserve an empty upstream description')
        english = entry.get('description_en', '')
        chinese = entry.get('description_zh', '')
        if isinstance(english, str) and re.search(r'[\u4e00-\u9fff]', english):
            # Names and explicitly quoted non-English identifiers may be retained.
            if entry.get('english_retains_name') is not True:
                errors.append(f'{identifier}: English description contains untranslated Chinese; mark a retained proper name explicitly if intentional.')
        if isinstance(chinese, str) and record.get('description_en') and not re.search(r'[\u4e00-\u9fff]', chinese):
            if entry.get('technical_only') is not True:
                errors.append(f'{identifier}: Chinese description needs translation or an explicit technical-only exception.')


def localized_records(records, translations):
    result = []
    for original in records:
        record = dict(original)
        entry = translations.get(record['id'])
        if entry:
            record['description_original'] = record.get('description_en', '')
            record['description_en'] = entry.get('description_en', record['description_original'])
            record['description_zh'] = entry.get('description_zh', '')
            record['description_language'] = 'bilingual'
            record['description_zh_status'] = 'translated'
            record['description_localization'] = 'ai-assisted-translation'
        result.append(record)
    return result
