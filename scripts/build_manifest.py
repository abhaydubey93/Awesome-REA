"""Record deterministic hashes of public deployment files, without environment data."""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

MANIFEST_NAME = 'build-manifest.json'
HTML_NORMALIZATION = 'strip-cloudflare-web-analytics-v1'
CONTROL_FILES = {'CNAME', '.nojekyll', '_headers', '_redirects'}
FONT_SUFFIXES = {'.woff', '.woff2', '.ttf', '.otf', '.eot'}
PRIVATE_NAMES = re.compile(r'(?i)^(?:\.env(?:\..*)?|credentials?(?:[.-].*)?|secrets?(?:[.-].*)?)$')
EMPTY_SCRIPT = re.compile(r'<script\b[^>]*>\s*</script>\s*', re.I)


class _ScriptAttributes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attributes = []

    def handle_starttag(self, tag, attributes):
        if tag == 'script':
            self.attributes = attributes


def normalized_html_bytes(content: bytes) -> bytes:
    """Ignore only Cloudflare's recognized empty analytics script injection.

    Page markup, text, structured data, asset revisions, and other scripts remain
    byte-sensitive. Unexpected attributes or inline code are never discarded.
    """
    text = content.decode('utf-8')

    def remove_beacon(match):
        parser = _ScriptAttributes()
        parser.feed(match[0])
        attrs = dict(parser.attributes)
        allowed = {'src', 'defer', 'integrity', 'data-cf-beacon', 'crossorigin'}
        if len(attrs) != len(parser.attributes) or set(attrs) - allowed or 'data-cf-beacon' not in attrs:
            return match[0]
        source = urlsplit(attrs.get('src') or '')
        if (source.scheme == 'https' and source.netloc == 'static.cloudflareinsights.com'
                and (source.path == '/beacon.min.js' or source.path.startswith('/beacon.min.js/'))):
            return ''
        return match[0]

    return EMPTY_SCRIPT.sub(remove_beacon, text).encode('utf-8')


def html_digest(content: bytes) -> str:
    return hashlib.sha256(normalized_html_bytes(content)).hexdigest()


def collect_manifest(site_dir: Path) -> dict:
    """Hash deployable public output; reject private files before reading them."""
    root = Path(site_dir)
    if not root.is_dir():
        raise ValueError('Deployment output directory is missing; build the site first')
    files = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if relative == MANIFEST_NAME or relative in CONTROL_FILES:
            continue
        if path.is_symlink():
            raise ValueError('Deployment output must not contain symbolic links')
        if (any(part.startswith('.') or part in {'node_modules', '__pycache__'} for part in path.relative_to(root).parts)
                or PRIVATE_NAMES.fullmatch(path.name)
                or path.suffix.lower() in {'.pem', '.key', '.p12', '.pfx'}):
            raise ValueError('Private or development-only files must not be in deployment output')
        if not path.is_file() or path.suffix.lower() in FONT_SUFFIXES:
            continue
        content = path.read_bytes()
        item = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
        if path.suffix.lower() == '.html':
            item['html_sha256'] = html_digest(content)
        files[relative] = item
    if 'index.html' not in files or 'sitemap.xml' not in files:
        raise ValueError('Deployment manifest requires a built homepage and sitemap')
    return {
        'schema_version': 1,
        'algorithm': 'sha256',
        'html_normalization': HTML_NORMALIZATION,
        'files': files,
    }


def manifest_bytes(manifest: dict) -> bytes:
    return (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def write_build_manifest(site_dir: Path) -> dict:
    """Call after the build has written all public pages, assets, and sitemap."""
    manifest = collect_manifest(site_dir)
    (Path(site_dir) / MANIFEST_NAME).write_bytes(manifest_bytes(manifest))
    return manifest


def read_build_manifest(site_dir: Path, *, verify_files: bool = True) -> dict:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Build manifest contains duplicate JSON keys')
            result[key] = value
        return result

    try:
        manifest = json.loads((Path(site_dir) / MANIFEST_NAME).read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    except (OSError, json.JSONDecodeError):
        raise ValueError('Build manifest is missing or invalid; rebuild the site') from None
    if (not isinstance(manifest, dict) or set(manifest) != {'schema_version', 'algorithm', 'html_normalization', 'files'}
            or type(manifest.get('schema_version')) is not int or manifest.get('schema_version') != 1 or manifest.get('algorithm') != 'sha256'
            or manifest.get('html_normalization') != HTML_NORMALIZATION or not isinstance(manifest.get('files'), dict)):
        raise ValueError('Unsupported build manifest schema')
    for name, item in manifest['files'].items():
        path = PurePosixPath(name)
        if (not name or path.is_absolute() or '..' in path.parts or '\\' in name
                or not isinstance(item, dict) or set(item) != ({'sha256', 'bytes', 'html_sha256'} if path.suffix.lower() == '.html' else {'sha256', 'bytes'})
                or type(item.get('bytes')) is not int or item['bytes'] < 0
                or not isinstance(item.get('sha256'), str) or not re.fullmatch(r'[a-f0-9]{64}', item['sha256'])
                or ('html_sha256' in item and (not isinstance(item['html_sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', item['html_sha256'])))):
            raise ValueError('Invalid public file entry in build manifest')
    if verify_files and manifest != collect_manifest(site_dir):
        raise ValueError('Build manifest differs from local output; rebuild before publishing or submitting')
    return manifest
