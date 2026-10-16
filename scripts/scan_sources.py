#!/usr/bin/env python3
"""Discover public GitHub RE repositories and actually read/hash each accepted README.

Uses only the Python standard library and an existing gh login. Authentication
stays in memory and is sent only to api.github.com. No repository code is run.
"""
from __future__ import annotations

import argparse
import base64
import copy
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import datetime as dt
import hashlib
from functools import lru_cache
import json
from pathlib import Path
import re
import subprocess
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'data/source-index.json'
QUERY_BASES = [
    '"reverse engineering" in:name,description',
    'topic:reverse-engineering',
    'topic:binary-analysis',
    'topic:ghidra',
    'topic:ida-plugin',
    'topic:frida',
    'topic:decompiler',
    'topic:disassembler',
    'topic:firmware-analysis',
    'topic:android-reverse-engineering',
    'topic:apk-analysis',
    'topic:game-reversing',
    'topic:game-decompilation',
    'topic:decompilation',
    'topic:javascript-deobfuscation',
    'topic:deobfuscation',
    'topic:protocol-analysis',
    'topic:binary-diffing',
    'topic:radare2',
    'topic:reversing',
    'topic:reverse-engineering-tools',
    'topic:il2cpp',
    'topic:jadx',
    'topic:binwalk',
    'topic:unpacking',
    'topic:memory-forensics',
    'topic:malware-analysis',
    'topic:ghidra-plugin',
    'topic:idapro',
    'topic:frida-script',
    'topic:wasm topic:reverse-engineering',
    '"firmware" "analysis" in:description',
    '"protocol" "reverse engineering" in:description',
    '"deobfuscator" in:name,description',
    '"disassembler" in:name,description',
    '"decompiler" in:name,description',
]
QUERIES = [query + ' is:public fork:false archived:false' for query in QUERY_BASES]
MAX_README_BYTES = 8 * 1024 * 1024
MAX_API_BYTES = 12 * 1024 * 1024


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


class ScanError(Exception):
    def __init__(self, reason, status=None):
        super().__init__(reason)
        self.reason, self.status = reason, status


class APIOnlyRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        if urlsplit(new_url).scheme != 'https' or urlsplit(new_url).hostname != 'api.github.com':
            raise ScanError('refused-non-github-api-redirect', code)
        return super().redirect_request(request, fp, code, message, headers, new_url)


class GitHub:
    def __init__(self, token, requests_per_second=12):
        self._token = token
        self._lock = threading.Lock()
        self._next_request = 0.0
        self._next_search = 0.0
        self._pause_until = 0.0
        self._interval = 1.0 / requests_per_second
        self.rate = {}

    def _throttle(self, search):
        with self._lock:
            current = time.monotonic()
            slot = max(current, self._next_request, self._pause_until,
                       self._next_search if search else 0)
            self._next_request = slot + self._interval
            if search:
                self._next_search = slot + 2.1
        while time.monotonic() < slot:
            time.sleep(min(5, slot - time.monotonic()))
        # A later response may have announced a shared secondary-limit pause.
        while True:
            with self._lock:
                delay = self._pause_until - time.monotonic()
            if delay <= 0:
                break
            time.sleep(min(5, delay))

    def _record_headers(self, headers):
        resource = headers.get('X-RateLimit-Resource')
        if resource:
            with self._lock:
                self.rate[resource] = {
                    'remaining': int(headers.get('X-RateLimit-Remaining', 0)),
                    'limit': int(headers.get('X-RateLimit-Limit', 0)),
                    'reset': int(headers.get('X-RateLimit-Reset', 0)),
                }

    def get(self, path, accept='application/vnd.github+json', search=False):
        url = 'https://api.github.com' + path
        if not path.startswith('/') or urlsplit(url).hostname != 'api.github.com':
            raise ScanError('invalid-api-endpoint')
        for attempt in range(4):
            self._throttle(search)
            request = Request(url, headers={
                'Authorization': 'Bearer ' + self._token,
                'Accept': accept,
                'X-GitHub-Api-Version': '2022-11-28',
                'User-Agent': 'Awesome-REA-source-index',
            })
            try:
                # Each worker owns its request/connection; redirects cannot send credentials elsewhere.
                with build_opener(APIOnlyRedirect()).open(request, timeout=30) as response:
                    self._record_headers(response.headers)
                    content = response.read(MAX_API_BYTES + 1)
                    if len(content) > MAX_API_BYTES:
                        raise ScanError('api-response-too-large')
                    return content
            except HTTPError as error:
                self._record_headers(error.headers)
                status = error.code
                body = error.read(4096).decode('utf-8', errors='replace').lower()
                retry_header = error.headers.get('Retry-After')
                remaining = error.headers.get('X-RateLimit-Remaining')
                reset = error.headers.get('X-RateLimit-Reset')
                error.close()
                limited = status == 429 or (status == 403 and (
                    remaining == '0' or 'rate limit' in body or retry_header))
                if limited and attempt < 3:
                    if remaining == '0' and reset:
                        pause = max(1, int(reset) - time.time() + 1)
                    else:
                        pause = float(retry_header) if retry_header and retry_header.isdigit() else 60
                    with self._lock:
                        self._pause_until = max(self._pause_until, time.monotonic() + pause)
                    print(f'RATE_LIMIT resource={"search" if search else "core"} retry_seconds={int(pause)}', flush=True)
                    continue
                if status in {500, 502, 503, 504} and attempt < 3:
                    time.sleep(min(5, 2 ** attempt))
                    continue
                raise ScanError('http-' + str(status), status) from None
            except (URLError, TimeoutError, OSError):
                if attempt < 3:
                    time.sleep(min(5, 2 ** attempt))
                    continue
                raise ScanError('network-failure') from None
        raise ScanError('retry-limit')

    def json(self, path, search=False):
        try:
            return json.loads(self.get(path, search=search))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ScanError('invalid-api-json') from None


@lru_cache(maxsize=1)
def curated_references():
    """Use explicit curated target tags; do not infer REA compatibility."""
    result = {}
    primary = {
        'core': 'reverse-engineering', 'related-lists': 'reverse-engineering',
        'native-analysis': 'native-analysis', 'dynamic-analysis': 'dynamic-analysis',
        'dotnet': 'managed-code', 'android': 'android', 'firmware': 'firmware',
        'game-analysis': 'game-analysis', 'web-analysis': 'web-analysis',
        'javascript-electron': 'web-analysis', 'binary-libraries': 'native-analysis',
        'binary-diffing': 'native-analysis', 'webassembly': 'web-analysis',
    }
    for filename in ('rea-resources.json', 'tool-resources.json'):
        path = ROOT / 'data' / filename
        if not path.exists():
            continue
        for record in json.loads(path.read_text(encoding='utf-8')):
            parsed = urlsplit(record['url'])
            parts = parsed.path.strip('/').split('/')
            if parsed.hostname != 'github.com' or len(parts) < 2:
                continue
            key = '/'.join(parts[:2]).casefold()
            value = result.setdefault(key, {'targets': set(), 'category': None, 'ids': []})
            value['targets'].update(record.get('targets', []))
            value['ids'].append(record['id'])
            # A scoped page may support a target domain without defining a repository's main purpose.
            if len(parts) == 2 and record['category'] in primary and value['category'] is None:
                value['category'] = primary[record['category']]
    return result


def classify(repo):
    topics = {topic.lower() for topic in repo.get('topics', [])}
    description = re.sub(r'https?://[^\s<>]+', ' ', repo.get('description') or '', flags=re.I)
    name = repo['full_name'].lower()
    purpose = (name + ' ' + description).lower()
    text = ' '.join([purpose, *topics])
    targets = set()
    managed = bool(topics & {'csharp', 'c-sharp', 'managed-code', 'ilspy', 'dnspy'} or
                   any(t == 'dotnet' or t.startswith('dotnet-') for t in topics) or
                   re.search(r'(?<![\w./-])\.net\b|\bdotnet\b|\bcsharp\b|\bc-sharp\b|\bcil\b|\bilspy\b|\bdnspy\b', text))
    android = bool(re.search(r'\bandroid\b|\bapk\b|\bjadx\b|\bdex\b', text))
    native = bool(topics & {'binary-analysis', 'binary-diffing', 'ghidra', 'ida-plugin', 'idapro',
                           'frida', 'radare2', 'rizin', 'disassembler', 'memory-forensics', 'debugger'} or
                  re.search(r'\bbinar(?:y|ies)\b|\bdisassembl|\bghidra\b|\bida\b|\bradare2\b|\brizin\b|\bcutter\b|\bx64dbg\b|\bgdb\b|\blldb\b|\belf\b|\bmach-o\b|\bnative\b|\bassembly\b|\bx86\b|\bx64\b|\barm(?:32|64)?\b|\bavr\b|\brisc-v\b|\briscv\b|\bmips\b', text))
    native_primary = bool(re.search(r'\bbinar(?:y|ies)\b|\bdisassembl|\bghidra\b|\bida\b|\bradare2\b|\brizin\b|\bcutter\b|\bx64dbg\b|\bgdb\b|\blldb\b|\bassembly\b|\bx86\b|\bx64\b|\barm(?:32|64)?\b|\bavr\b|\brisc-v\b|\briscv\b|\bmips\b', purpose))
    dynamic = bool(topics & {'frida', 'frida-script', 'memory-forensics', 'debugger'} or
                   re.search(r'\bdebugger\b|\binstrument(?:ation|able)\b', purpose))
    web_explicit = bool(topics & {'javascript-deobfuscation', 'web-reversing', 'website-clone',
                                  'web-scraping', 'browser', 'mitmproxy', 'openapi', 'swagger', 'rest-api'} or
                        re.search(r'\bwebsite\b|\bweb-site\b|\bbrowser\b|\belectron\b|\brest[- ]apis?\b|\bmitmproxy\b|\bweb\b|javascript.{0,30}(?:deobfuscat|decompil)|(?:deobfuscat|decompil).{0,30}javascript', purpose))
    if web_explicit or (topics & {'webassembly', 'wasm'} and not native_primary):
        targets.add('website')
    if topics & {'game-reversing', 'game-decompilation', 'il2cpp', 'unity-reverse-engineering', 'galgame', 'visual-novel'} or re.search(r'\bgames?\b|\bunity\b|\bunreal\b|\bplaystation\b|\btouhou\b|\bgamecube\b|\bvisual novel\b', text):
        targets.add('game')
    if managed or android or re.search(r'\bios\b|\bipados\b|\belectron\b|\bmobile\b|\bdesktop\b|\bapp(?:lication)?s?\b|java[- ](?:bytecode|decompiler)', text):
        targets.add('app')
    if re.search(r'\bfirmware\b|\bbinwalk\b|\bunblob\b|\buefi\b|\bbios\b', text):
        targets.add('firmware')
    if native:
        targets.add('binary')
    # Model Context Protocol is an agent interface, not evidence of network-protocol analysis.
    network_text = re.sub(r'model[\s-]*context[\s-]*protocol|\bmodelcontextprotocol\b|\bmcp\b', ' ', text)
    network = bool(topics & {'protocol-analysis', 'protocol-analyser', 'packet-analysis', 'pcap', 'wireshark', 'mitmproxy', 'network-forensics'} or
                   re.search(r'\bpcap\b|\bwireshark\b|\bnetwork[- ]protocol\b|\bprotocol[- ](?:analy|revers)|\brest[- ]apis?\b', network_text))
    collection = bool(topics & {'awesome', 'awesome-list', 'awesome-lists', 'references'} or
                      re.search(r'\b(?:collection|list|reference)\b', purpose))
    if managed:
        category = 'managed-code'
    elif native_primary:
        category = 'dynamic-analysis' if dynamic else 'native-analysis'
    elif collection:
        category = 'reverse-engineering'
    elif android:
        category = 'android'
    elif 'firmware' in targets:
        category = 'firmware'
    elif 'game' in targets:
        category = 'game-analysis'
    elif network:
        category = 'protocol-analysis'
    elif 'website' in targets:
        category = 'web-analysis'
    elif dynamic:
        category = 'dynamic-analysis'
    elif native:
        category = 'native-analysis'
    else:
        category = 'reverse-engineering'
    reference = curated_references().get(name)
    origin = 'automatic-metadata'
    reference_ids = []
    if reference:
        targets.update(reference['targets'])
        category = reference['category'] or category
        origin = 'curated-cross-reference'
        reference_ids = reference['ids']
    return sorted(targets), category, origin, reference_ids


def scan_readme(api, repo):
    path = '/repos/' + repo['full_name'] + '/readme'
    ref = repo.get('default_branch')
    if ref:
        path += '?' + urlencode({'ref': ref})
    try:
        metadata = api.json(path)
        if not isinstance(metadata, dict) or metadata.get('type') != 'file':
            raise ScanError('not-a-readme-file')
        if metadata.get('size', 0) > MAX_README_BYTES:
            raise ScanError('readme-too-large')
        if metadata.get('encoding') == 'base64' and isinstance(metadata.get('content'), str):
            try:
                content = base64.b64decode(re.sub(r'\s', '', metadata['content']), validate=True)
            except ValueError:
                raise ScanError('invalid-readme-encoding') from None
        else:
            content = api.get(path, accept='application/vnd.github.raw+json')
        if not content:
            raise ScanError('empty-readme')
        if len(content) > MAX_README_BYTES:
            raise ScanError('readme-too-large')
        text = content.decode('utf-8', errors='replace')
        if text.count('\x00') > 0 or text.count('\ufffd') > max(20, len(text) // 50):
            raise ScanError('nontext-readme')
        # These are automatic document features, not endorsements or compatibility claims.
        headings = []
        for match in re.finditer(r'^#{1,6}\s+(.+?)\s*#*\s*$', text, re.MULTILINE):
            title = re.sub(r'\s+', ' ', match[1]).strip()[:80]
            if title and title not in headings:
                headings.append(title)
            if len(headings) == 6:
                break
        signals = []
        for label, pattern in [
            ('installation', r'(?im)^#{1,6}\s*.*(?:install|setup|getting.started|安装)'),
            ('usage', r'(?im)^#{1,6}\s*.*(?:usage|quick.start|how.to|使用|用法)'),
            ('requirements', r'(?im)^#{1,6}\s*.*(?:requirements|prerequisites|dependenc|依赖|环境要求)'),
            ('examples', r'(?im)^#{1,6}\s*.*(?:examples|demo|tutorial|示例|教程)'),
            ('license-section', r'(?im)^#{1,6}\s*.*(?:licen[sc]e|copyright|许可)'),
        ]:
            if re.search(pattern, text):
                signals.append(label)
        targets, category, classification_origin, classification_reference_ids = classify(repo)
        description = repo.get('description') or ''
        record = {
            'id': 'scan-' + str(repo['id']),
            'name': repo['full_name'],
            'full_name': repo['full_name'],
            'url': repo['html_url'],
            'description_en': description,
            'description_zh': description,
            'description_language': 'upstream-original',
            'description_zh_status': 'not-translated',
            'description_origin': 'github-repository-description',
            'topics': repo.get('topics', []),
            'stars': repo.get('stargazers_count', 0),
            'license': (repo.get('license') or {}).get('spdx_id'),
            'archived': repo.get('archived', False),
            'updated_at': repo.get('updated_at'),
            'pushed_at': repo.get('pushed_at'),
            'metadata_observed_at': repo['_metadata_observed_at'],
            'observed_at': now(),
            'readme_url': metadata.get('html_url') or repo['html_url'] + '#readme',
            'readme_path': metadata.get('path'),
            'readme_git_sha': metadata.get('sha'),
            'readme_sha256': hashlib.sha256(content).hexdigest(),
            'readme_bytes': len(content),
            'readme_lines': len(text.splitlines()),
            'readme_heading_count': len(headings),
            'readme_signals': signals,
            'readme_api_url': 'https://api.github.com' + path,
            'scan_status': 'readme-scanned',
            'verification': 'automated-readme-scan',
            'requirements': 'See upstream requirements; not manually reviewed.',
            'targets': targets,
            'category': category,
            'classification_origin': classification_origin,
            'classification_reference_ids': classification_reference_ids,
            'matched_queries': repo['_matched_queries'],
            'discovery_methods': repo.get('_discovery_methods', ['github-search']),
        }
        if repo.get('_seed_reference_ids'):
            record['seed_reference_ids'] = repo['_seed_reference_ids']
        return record, None
    except ScanError as error:
        return None, {
            'id': 'scan-' + str(repo['id']), 'full_name': repo['full_name'],
            'url': repo['html_url'], 'observed_at': now(),
            'scan_status': 'failed', 'reason': error.reason,
            'http_status': error.status,
        }


def save(output, meta, records, failures, complete=False):
    meta = copy.deepcopy(meta)
    checkpoint = now()
    attempted = len(records) + len(failures)
    known_ids = meta.get('discovered_repository_ids', [])
    attempted_ids = [record['id'] for record in records + failures]
    if (len(known_ids) != len(set(known_ids)) or len(set(attempted_ids)) != attempted
            or not set(attempted_ids).issubset(known_ids)):
        raise ValueError('Inconsistent repository discovery accounting')
    meta.update({
        'unique_repos': len(known_ids),
        'attempted_readme_scans': attempted,
        'successful_readme_scans': len(records),
        'failed': len(failures),
        'unattempted_candidates': len(known_ids) - attempted,
        'target_reached': len(records) >= meta['requested_successful_scans'],
        'completed_at': checkpoint if complete else None,
        'last_checkpoint_at': checkpoint,
        'status': 'complete' if complete else 'in-progress',
    })
    run = meta['current_run']
    run.update({
        'completed_at': checkpoint if complete else None,
        'status': meta['status'],
        'query_count': len(meta['queries']) - run['query_start_index'],
        'seed_observation_count': len(meta.get('seed_observations', [])) - run['seed_observation_start_index'],
        'new_successful_readme_scans': len(records) - run['retained_successful_readme_scans'],
        'new_failed_readme_scans': len(failures) - run['retained_failed_readme_scans'],
    })
    document = {'meta': meta, 'resources': records, 'failures': failures}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(output)


def load_resume(path):
    """Validate retained evidence before any authentication or network access."""
    raw = path.read_bytes()
    document = json.loads(raw)
    if not isinstance(document, dict):
        raise ValueError('Resume snapshot must be an object')
    meta, records, failures = document.get('meta'), document.get('resources'), document.get('failures', [])
    if not isinstance(meta, dict) or not isinstance(records, list) or not isinstance(failures, list):
        raise ValueError('Resume snapshot requires meta, resources, and failures')
    if not isinstance(meta.get('queries'), list):
        raise ValueError('Resume snapshot must retain its query observations')
    identifiers, names = set(), set()
    for entries, status in ((records, 'readme-scanned'), (failures, 'failed')):
        for record in entries:
            if not isinstance(record, dict) or record.get('scan_status') != status:
                raise ValueError('Invalid retained scan status')
            identifier, name = record.get('id'), record.get('full_name')
            if not isinstance(identifier, str) or not re.fullmatch(r'scan-[0-9]+', identifier):
                raise ValueError('Resume snapshot contains an invalid repository ID')
            if identifier in identifiers or not isinstance(name, str) or not name or name.casefold() in names:
                raise ValueError('Resume snapshot contains duplicate or missing repository identities')
            identifiers.add(identifier)
            names.add(name.casefold())
    if (meta.get('successful_readme_scans') != len(records) or meta.get('failed') != len(failures)
            or meta.get('attempted_readme_scans') != len(identifiers)):
        raise ValueError('Resume snapshot scan counts do not match retained evidence')
    known = meta.get('discovered_repository_ids')
    if known is not None:
        if (not isinstance(known, list) or any(not isinstance(value, str) or not re.fullmatch(r'scan-[0-9]+', value) for value in known)
                or len(set(known)) != len(known) or not identifiers.issubset(known)
                or meta.get('unique_repos') != len(known)
                or meta.get('unattempted_candidates') != len(known) - len(identifiers)):
            raise ValueError('Resume snapshot discovery ID ledger is inconsistent')
    elif (not isinstance(meta.get('unique_repos'), int) or meta['unique_repos'] < len(identifiers)
          or meta.get('unattempted_candidates') != meta['unique_repos'] - len(identifiers)):
        raise ValueError('Legacy resume snapshot candidate counts are inconsistent')
    return document, hashlib.sha256(raw).hexdigest()


def initial_meta(args, started):
    return {
        'schema_version': 1,
        'classification_engine_version': 2,
        'started_at': started,
        'completed_at': None,
        'requested_successful_scans': args.target,
        'queries': [],
        'method': 'Public, non-fork, non-archived GitHub repository discovery through search and optional curated-reference metadata lookups, followed by an actual authenticated GET of each repository README. README bytes are decoded, analyzed for document features, SHA-256 hashed and discarded.',
        'description_policy': 'Repository descriptions remain in their original upstream language. description_zh mirrors the same text and is explicitly not a translation. No LLM-written description or individual manual review is claimed.',
        'readme_heading_count_policy': 'Count of distinct heading-like lines encountered, capped at six; a count of six means at least six. Heading text is not retained.',
        'classification_policy': 'Automatic labels use repository names, URL-stripped descriptions and explicit topics, with primary-function precedence. Canonical repository matches can add curated target tags and a primary category; classification_origin and classification_reference_ids identify that cross-reference. Labels do not establish REA compatibility. Empty targets mean insufficient metadata.',
        'limits': {
            'workers': args.workers, 'requests_per_second': args.requests_per_second,
            'search_interval_seconds': 2.1, 'max_readme_bytes': MAX_README_BYTES,
            'max_pages_per_query': args.max_pages, 'per_page': 100,
        },
        'limitations': [
            'Automated README scanning is distinct from the curated source-reviewed catalog.',
            'No repository code, binaries, installers, tests or linked commands are executed.',
            'Search membership and README availability do not establish quality, safety, licensing permission, REA compatibility, or successful operation.',
            'Stars, topics, license identifiers and timestamps come from GitHub repository metadata and are snapshots.',
            'Upstream repository descriptions are attributed source text, not original editorial summaries. README text is not retained.',
            'Repositories without a readable nonempty README, oversized README files and failed requests do not count as successful sources.',
            'Search results are relevance-limited by queries, sorted by stars within each query, and capped by GitHub pagination; this is not an exhaustive census.',
            'README URLs can change after collection; content hashes and Git blob identifiers record the observed bytes.',
        ],
    }


def run_scan(api, args, resumed=None, resume_sha256=None):
    """Extend evidence without refreshing or retrying any retained repository."""
    started = now()
    fresh_meta = initial_meta(args, started)
    records = list(resumed['resources']) if resumed else []
    failures = list(resumed.get('failures', [])) if resumed else []
    retained_successes, retained_failures = len(records), len(failures)
    attempted_ids = {record['id'] for record in records + failures}
    retained_names = {record['full_name'].casefold() for record in records + failures}
    meta = copy.deepcopy(resumed['meta']) if resumed else fresh_meta
    known_ids = set(meta.get('discovered_repository_ids', attempted_ids))
    if resumed:
        prior = {key: copy.deepcopy(meta.get(key)) for key in (
            'started_at', 'completed_at', 'last_checkpoint_at', 'status',
            'requested_successful_scans', 'unique_repos', 'attempted_readme_scans',
            'successful_readme_scans', 'failed', 'unattempted_candidates', 'limits', 'method',
        )}
        prior.update({'source_sha256': resume_sha256, 'query_count': len(meta['queries']),
                      'candidate_ids_retained': 'discovered_repository_ids' in meta,
                      'known_repository_ids': len(known_ids)})
        if 'current_run' in meta:
            prior['run'] = copy.deepcopy(meta['current_run'])
        meta.setdefault('resume_history', []).append(prior)
        meta['requested_successful_scans'] = args.target
        meta['limits'] = fresh_meta['limits']
    meta['method'] = fresh_meta['method']
    meta['unique_repos_policy'] = ('Distinct persisted repository IDs from retained attempts and discovery observations. '
                                   'Historical count-only unattempted candidates are not added to this union unless rediscovered; '
                                   'their original counts remain in resume_history.')
    meta['current_run'] = {
        'run_id': started, 'started_at': started, 'completed_at': None,
        'mode': 'resume' if resumed else 'fresh', 'query_start_index': len(meta['queries']),
        'retained_successful_readme_scans': retained_successes,
        'retained_failed_readme_scans': retained_failures,
        'requested_new_successful_scans': max(0, args.target - retained_successes),
        'readme_queue_candidates': 0, 'seed_curated': args.seed_curated,
        'query_plan': list(args.queries),
    }
    candidates, candidate_names, exhausted = {}, set(), set()
    meta.setdefault('seed_observations', [])
    meta['current_run']['seed_observation_start_index'] = len(meta['seed_observations'])
    candidate_goal = max(0, args.target - retained_successes) + args.candidate_buffer

    def checkpoint(complete=False):
        meta['discovered_repository_ids'] = sorted(known_ids, key=lambda value: int(value[5:]))
        meta['current_run']['readme_queue_candidates'] = len(candidates)
        save(args.output, meta, records, failures, complete)

    def add_candidate(repo, observed_at, query=None, seed_ids=None):
        if repo.get('private') is not False or repo.get('fork') or repo.get('archived'):
            return 'ineligible'
        identifier = 'scan-' + str(repo['id'])
        known_ids.add(identifier)
        if identifier in attempted_ids:
            return 'retained-attempt'
        if identifier not in candidates:
            name = repo['full_name'].casefold()
            if name in retained_names or name in candidate_names:
                return 'name-collision'
            candidate = dict(repo)
            candidate.update({'_metadata_observed_at': observed_at, '_matched_queries': [], '_discovery_methods': []})
            candidates[identifier] = candidate
            candidate_names.add(name)
        candidate = candidates[identifier]
        if query is not None:
            if query not in candidate['_matched_queries']:
                candidate['_matched_queries'].append(query)
            if 'github-search' not in candidate['_discovery_methods']:
                candidate['_discovery_methods'].append('github-search')
        if seed_ids is not None:
            candidate['_seed_reference_ids'] = list(seed_ids)
            if 'curated-reference' not in candidate['_discovery_methods']:
                candidate['_discovery_methods'].append('curated-reference')
        return 'candidate'

    print(f'START target={args.target} retained_success={retained_successes} retained_failed={retained_failures}', flush=True)
    checkpoint()
    if args.seed_curated:
        for name, reference in sorted(curated_references().items()):
            if name in retained_names:
                continue
            entry = {'full_name': name, 'observed_at': now(), 'run_id': started,
                     'method': 'curated-repository-reference', 'reference_ids': list(reference['ids'])}
            try:
                repo = api.json('/repos/' + quote(name, safe='/'))
                entry['status'] = add_candidate(repo, entry['observed_at'], seed_ids=reference['ids'])
                if entry['status'] != 'ineligible':
                    entry['repository_id'] = 'scan-' + str(repo['id'])
            except ScanError as error:
                entry.update({'status': 'failed', 'reason': error.reason, 'http_status': error.status})
            meta['seed_observations'].append(entry)
        print(f'SEEDS_COMPLETE observations={len(meta["seed_observations"]) - meta["current_run"]["seed_observation_start_index"]} new_readme_candidates={len(candidates)}', flush=True)
        checkpoint()
    for page in range(1, args.max_pages + 1):
        if len(candidates) >= candidate_goal:
            break
        for query in args.queries:
            if query in exhausted:
                continue
            entry = {'query': query, 'page': page, 'per_page': 100, 'observed_at': now(), 'run_id': started}
            params = urlencode({'q': query, 'per_page': 100, 'page': page, 'sort': 'stars', 'order': 'desc'})
            try:
                result = api.json('/search/repositories?' + params, search=True)
                items = result.get('items', [])
                entry.update({'status': 'ok', 'total_count': result.get('total_count'),
                              'returned': len(items), 'incomplete_results': result.get('incomplete_results', False)})
                skipped_attempted, skipped_names = 0, 0
                for repo in items:
                    outcome = add_candidate(repo, entry['observed_at'], query=query)
                    skipped_attempted += outcome == 'retained-attempt'
                    skipped_names += outcome == 'name-collision'
                entry.update({'retained_attempts_skipped': skipped_attempted, 'name_collisions_skipped': skipped_names})
                if len(items) < 100 or page * 100 >= min(result.get('total_count', 0), 1000):
                    exhausted.add(query)
            except ScanError as error:
                entry.update({'status': 'failed', 'reason': error.reason, 'http_status': error.status})
            meta['queries'].append(entry)
            new_queries = len(meta['queries']) - meta['current_run']['query_start_index']
            print(f'DISCOVERY new_queries={new_queries} new_readme_candidates={len(candidates)} known_repositories={len(known_ids)} page={page}', flush=True)
            if new_queries % 5 == 0:
                checkpoint()
            if len(candidates) >= candidate_goal:
                break
        if len(candidates) >= candidate_goal:
            break
    print(f'DISCOVERY_COMPLETE known_repositories={len(known_ids)} new_readme_candidates={len(candidates)}; starting actual README GETs', flush=True)
    checkpoint()
    source = iter(candidates.values())
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {}
        for _ in range(min(args.workers, max(0, args.target - len(records)))):
            repo = next(source, None)
            if repo is not None:
                pending[pool.submit(scan_readme, api, repo)] = repo
        while pending:
            completed, _ = wait(pending, return_when=FIRST_COMPLETED)
            for future in completed:
                repo = pending.pop(future)
                try:
                    record, failure = future.result()
                except Exception as error:
                    record, failure = None, {
                        'id': 'scan-' + str(repo['id']), 'full_name': repo['full_name'],
                        'url': repo['html_url'], 'observed_at': now(),
                        'scan_status': 'failed', 'reason': 'worker-' + type(error).__name__,
                        'http_status': None,
                    }
                result = record or failure
                if result['id'] in attempted_ids:
                    raise ValueError('Duplicate repository attempt')
                attempted_ids.add(result['id'])
                (records if record else failures).append(result)
                new_attempts = len(records) + len(failures) - retained_successes - retained_failures
                if new_attempts % 100 == 0:
                    print(f'README_PROGRESS success={len(records)} failed={len(failures)} new_attempts={new_attempts}', flush=True)
                    checkpoint()
                if len(records) + len(pending) < args.target:
                    following = next(source, None)
                    if following is not None:
                        pending[pool.submit(scan_readme, api, following)] = following
    # Keep the prior snapshot as an unchanged prefix; order only the new evidence.
    records[retained_successes:] = sorted(records[retained_successes:], key=lambda record: (-record['stars'], record['full_name'].casefold()))
    failures[retained_failures:] = sorted(failures[retained_failures:], key=lambda record: record['full_name'].casefold())
    checkpoint(complete=True)
    reached = len(records) >= args.target
    print(f'COMPLETE successful_readme_scans={len(records)} failed={len(failures)} unique_repos={len(known_ids)} target_reached={reached}', flush=True)
    return 0 if reached else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=int, default=1600, help='Combined number of successfully read README sources to seek')
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--requests-per-second', type=float, default=12)
    parser.add_argument('--candidate-buffer', type=int, default=400)
    parser.add_argument('--max-pages', type=int, default=5, help='Pages per query; GitHub permits at most 10')
    parser.add_argument('--resume', type=Path, help='Retain an existing complete snapshot or progress checkpoint')
    parser.add_argument('--seed-curated', action='store_true', help='Discover missing curated GitHub repositories before search candidates')
    parser.add_argument('--query', action='append', help='Ordered search base; repeat to replace defaults. Public/non-fork/non-archived gates are always added.')
    parser.add_argument('--output', type=Path, help='Output snapshot; defaults to .cache/source-index-next.json when resuming')
    args = parser.parse_args()
    if (args.target < 1 or not 1 <= args.workers <= 32 or not 1 <= args.max_pages <= 10
            or not 0 < args.requests_per_second <= 14 or args.candidate_buffer < 0):
        parser.error('target must be positive, workers 1..32, max-pages 1..10, requests-per-second (0,14], and candidate-buffer nonnegative')
    if args.query and any(not value.strip() for value in args.query):
        parser.error('query bases must be nonempty')
    args.queries = [value.strip() + ' is:public fork:false archived:false' for value in args.query] if args.query else QUERIES
    args.output = args.output or (ROOT / '.cache/source-index-next.json' if args.resume else DEFAULT_OUTPUT)
    resumed, resume_sha256 = None, None
    if args.resume:
        if args.resume.resolve() == args.output.resolve():
            parser.error('resume input and output must be different paths to preserve the source snapshot')
        try:
            resumed, resume_sha256 = load_resume(args.resume)
        except (OSError, ValueError, TypeError, KeyError):
            print('Resume snapshot could not be read or has inconsistent identities/counts.', flush=True)
            return 2
        if len(resumed['resources']) >= args.target:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(args.resume.read_bytes())
            print(f'ALREADY_COMPLETE successful_readme_scans={len(resumed["resources"])} target={args.target}; snapshot copied without new requests', flush=True)
            return 0
    token_result = subprocess.run(['gh', 'auth', 'token'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    token = token_result.stdout.decode().strip()
    if token_result.returncode or not token:
        print('An existing authenticated gh login is required.', flush=True)
        return 2
    api = GitHub(token, args.requests_per_second)
    del token, token_result
    return run_scan(api, args, resumed, resume_sha256)


if __name__ == '__main__':
    raise SystemExit(main())
