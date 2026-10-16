#!/usr/bin/env python3
"""Notify IndexNow of the deployed owned-site sitemap; dry run unless --submit."""
import argparse
import json
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://awesomerea.org'
ENDPOINT = 'https://api.indexnow.org/indexnow'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true', help='Verify live ownership and sitemap, then submit their canonical URLs')
    args = parser.parse_args()
    # This is intentionally public ownership proof, not an account credential.
    key = (ROOT / 'site/indexnow.txt').read_text().strip()
    if not re.fullmatch(r'[a-f0-9]{32}', key):
        raise ValueError('Invalid public IndexNow verification key')
    sitemap = (ROOT / 'dist/sitemap.xml').read_bytes()
    urls = [element.text for element in ET.fromstring(sitemap).findall('{*}url/{*}loc')]
    if not urls or len(urls) > 10000 or len(urls) != len(set(urls)):
        raise ValueError('Sitemap URL count or uniqueness is invalid')
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc != 'awesomerea.org' or parsed.query or parsed.fragment:
            raise ValueError('Only canonical HTTPS URLs on the owned domain may be submitted')
    payload = {'host': 'awesomerea.org', 'key': key, 'keyLocation': ORIGIN + '/indexnow.txt', 'urlList': urls}
    if not args.submit:
        print(f'Dry run: {len(urls)} canonical URLs; use --submit after deployment.')
        return 0
    for path, expected in [('/indexnow.txt', key.encode()), ('/sitemap.xml', sitemap.strip())]:
        with urlopen(Request(ORIGIN + path, headers={'User-Agent': 'AwesomeREA-IndexNow/1.0'}), timeout=30) as response:
            body = response.read(2_000_000).strip()
            if response.status != 200 or body != expected:
                raise ValueError('The live verification file or sitemap differs from this build; deploy before submitting')
    request = Request(ENDPOINT, data=json.dumps(payload).encode(), method='POST', headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'AwesomeREA-IndexNow/1.0'})
    try:
        with urlopen(request, timeout=30) as response:
            status = response.status
    except HTTPError as error:
        print(f'IndexNow returned HTTP {error.code}; submission was not accepted.')
        return 1
    print(f'IndexNow HTTP {status}: {len(urls)} URLs submitted. ' + ('Key validation pending. ' if status == 202 else '') + 'Receipt does not confirm indexing.')
    return 0 if status in (200, 202) else 1


if __name__ == '__main__':
    raise SystemExit(main())
