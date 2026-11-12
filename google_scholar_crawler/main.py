"""Fetch Google Scholar citation data for the homepage.

Google Scholar intermittently blocks GitHub runner IPs. scholarly 1.5.1 then
either sleeps 60–120s after a second HTTP 403, or opens a browser and waits
up to a week for a person to solve a captcha. Either way the job's hard
timeout kills the process and the real status never reaches the log.

This script therefore:

* fails an attempt immediately on HTTP 403/429, the automated-query block,
  or a captcha/DOS challenge, and does not solve captchas or launch a browser,
* retries a direct fetch once, then tries free proxies whose addresses are
  parsed from the current proxy-list table headers,
* validates the result and writes the JSON files only after a fully
  successful fetch, so a failed run never replaces good data with empty data.
"""

import json
import multiprocessing as mp
import os
from datetime import datetime
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

import requests
from lxml import html as lxml_html
from scholarly import DOSException, ProxyGenerator, scholarly

SECTIONS = ['basics', 'indices', 'counts', 'publications']
# (strategy, hard timeout in seconds) for each attempt, in order.
# Fail-fast blocks return in about a second; the caps only cover a slow but
# healthy fetch or a handful of dead proxies. Worst case stays under the
# workflow's 15-minute job timeout.
ATTEMPTS = [('direct', 50), ('direct', 50), ('free_proxy', 120), ('free_proxy', 120)]
RETRY_DELAY = 15
OUTPUT_FILES = ('gs_data.json', 'gs_data_shieldsio.json')
# sslproxies.org now 301s to the SSL list. free-proxy 1.3 still reads column 6
# as "Https"; on the live table that column is "Last Checked", so https=True
# rejects every row. Fetch the pages ourselves and key off the header names.
PROXY_LIST_URLS = (
    'https://www.sslproxies.org/',
    'https://free-proxy-list.net/ssl-proxy.html',
    'https://free-proxy-list.net/',
)
PROXY_LIST_TIMEOUT = 15
PROXY_TEST_TIMEOUT = 3
MAX_PROXY_CANDIDATES = 10
_PROXY_ADDRESS = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})$')
_HTTPS_YES = {'yes', 'true'}


class ScholarAccessError(RuntimeError):
    """Scholar refused or challenged this attempt. The caller does not evade it."""


def validate_author(author):
    if not isinstance(author, dict) or not author.get('name'):
        raise ValueError('Scholar returned no author name (likely a captcha/blocked page)')
    if not isinstance(author.get('citedby'), int):
        raise ValueError(f"Scholar returned invalid citation count: {author.get('citedby')!r}")
    if not isinstance(author.get('publications'), list):
        raise ValueError('Scholar returned no publication list')


def write_json(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
    tmp.replace(path)


def generate_citation_data(scholar_id, output_dir='results'):
    author = scholarly.search_author_id(scholar_id)
    scholarly.fill(author, sections=SECTIONS)
    validate_author(author)
    author['updated'] = str(datetime.now())
    author['publications'] = {v['author_pub_id']: v for v in author['publications']}
    print(json.dumps(author, indent=2, ensure_ascii=False))

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'gs_data.json', author)
    write_json(output_dir / 'gs_data_shieldsio.json', {
        'schemaVersion': 1,
        'label': 'citations',
        'message': str(author['citedby']),
    })


def _normalize_header(text):
    return ' '.join(text.lower().split())


def _header_index(headers, *names):
    for name in names:
        if name in headers:
            return headers.index(name)
    return None


def parse_proxy_list_html(content):
    """Return ``http://ip:port`` addresses for rows marked HTTPS.

    Header names are read from the table, so a column inserted before Https
    does not make every row look non-HTTPS. Rows that are not HTTPS, or that
    do not have an IPv4 address and port, are omitted.
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
    document = lxml_html.fromstring(content)
    tables = document.xpath('//*[@id="list"]//table') or document.xpath('//table')
    if not tables:
        raise ValueError('proxy list page has no table')
    rows = tables[0].xpath('.//tr')
    if len(rows) < 2:
        raise ValueError('proxy list table has no data rows')
    headers = [_normalize_header(cell.text_content()) for cell in rows[0].xpath('./th|./td')]
    combined_index = _header_index(headers, 'ip:port')
    ip_index = _header_index(headers, 'ip address', 'ip')
    port_index = _header_index(headers, 'port')
    https_index = _header_index(headers, 'https', 'ssl')
    if combined_index is None and (ip_index is None or port_index is None):
        raise ValueError(f'proxy list headers are not recognized: {headers}')

    addresses = []
    for row in rows[1:]:
        cells = [' '.join(cell.text_content().split()) for cell in row.xpath('./td')]
        if not cells:
            continue
        if https_index is not None:
            if https_index >= len(cells) or cells[https_index].lower() not in _HTTPS_YES:
                continue
        candidate = None
        if combined_index is not None and combined_index < len(cells):
            if _PROXY_ADDRESS.match(cells[combined_index]):
                candidate = cells[combined_index]
        if candidate is None and ip_index is not None and port_index is not None:
            if ip_index < len(cells) and port_index < len(cells):
                candidate = f'{cells[ip_index]}:{cells[port_index]}'
        if candidate and _PROXY_ADDRESS.match(candidate) and f'http://{candidate}' not in addresses:
            addresses.append(f'http://{candidate}')
    return addresses


def fetch_proxy_candidates(urls=PROXY_LIST_URLS, get=None, timeout=PROXY_LIST_TIMEOUT):
    """Load HTTPS proxy addresses from the first page that yields any."""
    getter = requests.get if get is None else get
    errors = []
    for url in urls:
        try:
            response = getter(url, timeout=timeout)
        except requests.RequestException as exc:
            errors.append(f'{url}: {exc.__class__.__name__}')
            print(f'  proxy list {url} failed: {exc}', flush=True)
            continue
        status = getattr(response, 'status_code', None)
        if status != 200:
            errors.append(f'{url}: HTTP {status}')
            print(f'  proxy list {url} returned HTTP {status}', flush=True)
            continue
        try:
            found = parse_proxy_list_html(response.content)
        except ValueError as exc:
            errors.append(f'{url}: {exc}')
            print(f'  proxy list {url} could not be parsed: {exc}', flush=True)
            continue
        print(f'  proxy list {url} yielded {len(found)} https candidates', flush=True)
        if found:
            return found
        errors.append(f'{url}: 0 https candidates')
    detail = '; '.join(errors) if errors else 'no pages configured'
    raise RuntimeError(f'no https proxy candidates parsed ({detail})')


def _free_proxy_generator(max_candidates=MAX_PROXY_CANDIDATES, candidates=None):
    """Pick a free proxy that scholarly can open a session with.

    Candidates are tested against ProxyGenerator's own check (httpbin), not
    against a captcha. A proxy that fails the check is skipped.
    """
    if candidates is None:
        candidates = fetch_proxy_candidates()
    ordered = list(candidates)
    random.shuffle(ordered)
    tested = 0
    for proxy in ordered[:max_candidates]:
        tested += 1
        pg = ProxyGenerator()
        pg._TIMEOUT = PROXY_TEST_TIMEOUT
        try:
            if pg.SingleProxy(http=proxy, https=proxy):
                print(f'  using free proxy {proxy}', flush=True)
                return pg
            print(f'  proxy {proxy} rejected', flush=True)
        except Exception as exc:  # broken proxies raise all sorts of errors
            print(f'  proxy {proxy} failed: {exc}', flush=True)
    raise RuntimeError(
        f'no working free proxy found (tested {tested} of {len(candidates)} candidates)')


def _navigator():
    return scholarly._Scholarly__nav


def install_fail_fast_scholar_guards(pause_seconds=1.0):
    """Replace scholarly's page fetch so a block is reported, not waited out."""
    nav = _navigator()

    def _get_page(pagerequest, premium=False):
        del premium  # both sessions would only repeat the same blocked IP
        if pause_seconds:
            time.sleep(pause_seconds)
        timeout = nav._TIMEOUT
        try:
            response = nav._session1.get(pagerequest, timeout=timeout)
        except requests.RequestException as exc:
            raise ScholarAccessError(
                f'Google Scholar request failed: {exc.__class__.__name__}: {exc}') from exc
        text = response.text or ''
        try:
            has_captcha = nav._requests_has_captcha(text)
        except DOSException as exc:
            raise ScholarAccessError(
                'Google Scholar returned a DOS/captcha challenge; not solving it') from exc
        if has_captcha:
            raise ScholarAccessError(
                f'Google Scholar returned a captcha (HTTP {response.status_code}); not solving it')
        automated = 'automated queries' in text.lower()
        if response.status_code in (403, 429) or automated:
            reason = 'automated-query block' if automated else 'refused the request'
            raise ScholarAccessError(
                f'Google Scholar {reason} (HTTP {response.status_code}); not bypassing it')
        if response.status_code != 200:
            raise ScholarAccessError(
                f'Google Scholar returned HTTP {response.status_code}')
        return text

    nav._get_page = _get_page
    return nav


def _attempt(scholar_id, strategy, output_dir):
    """Child-process body: configure the connection and fetch once."""
    try:
        scholarly.set_timeout(20)
        scholarly.set_retries(1)
        if strategy == 'free_proxy':
            pg = _free_proxy_generator()
            # Pass it as the secondary too, otherwise scholarly calls the broken
            # FreeProxies() itself for the secondary generator.
            scholarly.use_proxy(pg, pg)
        install_fail_fast_scholar_guards()
        generate_citation_data(scholar_id, output_dir)
    except Exception as exc:
        # Exit without a traceback so a later successful attempt is not buried
        # under GitHub's error annotations. The reason is still printed.
        print(f'  {strategy} failed: {exc}', flush=True)
        sys.exit(1)


def _run_attempt(scholar_id, strategy, timeout, output_dir):
    ctx = mp.get_context('fork')
    proc = ctx.Process(target=_attempt, args=(scholar_id, strategy, output_dir))
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        proc.kill()
        proc.join()
        print(f'  timed out after {timeout}s', flush=True)
        return False
    return proc.exitcode == 0


def set_output(name, value):
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a', encoding='utf-8') as fh:
            fh.write(f'{name}={value}\n')


def assert_citation_files_ready(output_dir):
    """Refuse to publish missing, empty, or inconsistent citation files."""
    output_dir = Path(output_dir)
    data_path = output_dir / 'gs_data.json'
    badge_path = output_dir / 'gs_data_shieldsio.json'
    if not data_path.is_file() or not badge_path.is_file():
        raise ValueError(f'missing {OUTPUT_FILES[0]} or {OUTPUT_FILES[1]} in {output_dir}')
    data = json.loads(data_path.read_text(encoding='utf-8'))
    badge = json.loads(badge_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('gs_data.json must be an object')
    name = data.get('name')
    if not isinstance(name, str) or not name.strip():
        raise ValueError('gs_data.json has no author name')
    if not isinstance(data.get('scholar_id'), str) or not data.get('scholar_id'):
        raise ValueError('gs_data.json has no scholar_id')
    citedby = data.get('citedby')
    if not isinstance(citedby, int) or citedby < 0:
        raise ValueError(f'gs_data.json has invalid citedby: {citedby!r}')
    updated = data.get('updated')
    if not isinstance(updated, str) or not updated.strip():
        raise ValueError('gs_data.json has no updated timestamp')
    datetime.fromisoformat(updated)
    publications = data.get('publications')
    if not isinstance(publications, dict):
        raise ValueError('gs_data.json publications must be an object keyed by author_pub_id')
    for key, publication in publications.items():
        if not isinstance(publication, dict) or publication.get('author_pub_id') != key:
            raise ValueError(f'publication {key!r} is missing a matching author_pub_id')
    if badge != {'schemaVersion': 1, 'label': 'citations', 'message': str(citedby)}:
        raise ValueError('gs_data_shieldsio.json does not match citedby')


def publish_citation_files(results_dir, remote_url):
    """Commit the two JSON files and push them to ``google-scholar-stats``.

    The remote is updated only after ``assert_citation_files_ready`` accepts
    the files. The push URL is not written to stdout.
    """
    if not remote_url:
        raise ValueError('publish remote URL is empty')
    results_dir = Path(results_dir)
    assert_citation_files_ready(results_dir)
    commands = [
        ['git', 'init'],
        ['git', 'config', '--local', 'user.name', 'github-actions[bot]'],
        ['git', 'config', '--local', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', '--local', 'commit.gpgsign', 'false'],
        ['git', 'add', 'gs_data.json', 'gs_data_shieldsio.json'],
        ['git', 'commit', '-m', 'Updated Citation Data'],
        ['git', 'push', remote_url, 'HEAD:google-scholar-stats', '--force'],
    ]
    for command in commands:
        subprocess.run(command, cwd=results_dir, check=True)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ['--check-results']:
        if len(argv) != 2:
            print('ERROR: --check-results requires a results directory', flush=True)
            sys.exit(2)
        try:
            assert_citation_files_ready(argv[1])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f'::error::Refusing to publish citation data: {exc}', flush=True)
            sys.exit(1)
        print('Citation JSON is ready to publish.', flush=True)
        return
    if argv[:1] == ['--publish-results']:
        if len(argv) != 3:
            print('ERROR: --publish-results requires a results directory and a remote URL', flush=True)
            sys.exit(2)
        try:
            publish_citation_files(argv[1], argv[2])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f'::error::Refusing to publish citation data: {exc}', flush=True)
            sys.exit(1)
        except subprocess.CalledProcessError as exc:
            print(f'::error::Publishing citation JSON failed (git exit {exc.returncode}).', flush=True)
            sys.exit(exc.returncode or 1)
        print('Citation JSON published.', flush=True)
        return

    scholar_id = os.environ.get('GOOGLE_SCHOLAR_ID')
    if not scholar_id:
        print('ERROR: GOOGLE_SCHOLAR_ID is not set', flush=True)
        sys.exit(1)

    results = Path('results')
    for i, (strategy, timeout) in enumerate(ATTEMPTS, 1):
        print(f'Attempt {i}/{len(ATTEMPTS)} ({strategy}, timeout {timeout}s)', flush=True)
        with tempfile.TemporaryDirectory() as tmp:
            if _run_attempt(scholar_id, strategy, timeout, tmp):
                results.mkdir(parents=True, exist_ok=True)
                for name in OUTPUT_FILES:
                    shutil.move(os.path.join(tmp, name), results / name)
                print('Citation data fetched successfully.', flush=True)
                set_output('updated', 'true')
                return
        if i < len(ATTEMPTS):
            time.sleep(RETRY_DELAY)

    # Exit non-zero so the publish step is skipped and the previously published
    # gs_data.json on google-scholar-stats is left untouched.
    print('::error::Google Scholar fetch failed on every attempt (likely blocked); '
          'previously published citation data is kept.', flush=True)
    set_output('updated', 'false')
    sys.exit(1)


if __name__ == '__main__':
    main()
