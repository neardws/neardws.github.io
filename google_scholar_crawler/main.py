"""Fetch Google Scholar citation data for the homepage.

Google Scholar intermittently blocks GitHub runner IPs. scholarly 1.5.1 then
either sleeps 60–120s after a second HTTP 403, or opens a browser and waits
up to a week for a person to solve a captcha. Either way a hard timeout used
to kill the process before the real status reached the log.

This script therefore:

* requests Scholar directly, once,
* fails that request immediately on HTTP 403/429, the automated-query block,
  or a captcha/DOS challenge, and does not solve captchas or launch a browser,
* ends the whole run on that refusal: no further Scholar request and no
  change of network route,
* validates the result and writes the JSON files only after a fully
  successful fetch, so a failed run never replaces good data with empty data.
"""

import json
import multiprocessing as mp
import os
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import requests
from scholarly import DOSException, scholarly

SECTIONS = ['basics', 'indices', 'counts', 'publications']
# One direct fetch. A refusal ends the run; there is no second attempt and
# no proxy route. The hard cap only bounds a hung socket. A healthy fetch is
# a few seconds, and a block returns as soon as the HTTP response arrives.
ATTEMPTS = [('direct', 60)]
OUTPUT_FILES = ('gs_data.json', 'gs_data_shieldsio.json')
STATUS_NAME = '.fetch_status'
SCHOLAR_REQUEST_PAUSE = 1.0


class ScholarAccessError(RuntimeError):
    """Scholar did not return a profile page.

    ``blocked`` is true for an access refusal (HTTP 403/429, automated-query
    page, captcha, or DOS challenge). The fetch run stops either way and does
    not switch routes.
    """

    def __init__(self, message, blocked):
        super().__init__(message)
        self.blocked = blocked


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


def _navigator():
    return scholarly._Scholarly__nav


def install_fail_fast_scholar_guards(pause_seconds=None):
    """Replace scholarly's page fetch so a block is reported, not waited out."""
    nav = _navigator()
    if pause_seconds is None:
        pause_seconds = SCHOLAR_REQUEST_PAUSE

    def _get_page(pagerequest, premium=False):
        del premium  # a second session would be another route around the block
        if pause_seconds:
            time.sleep(pause_seconds)
        timeout = nav._TIMEOUT
        try:
            response = nav._session1.get(pagerequest, timeout=timeout)
        except requests.RequestException as exc:
            raise ScholarAccessError(
                f'Google Scholar request failed: {exc.__class__.__name__}: {exc}',
                blocked=False,
            ) from exc
        text = response.text or ''
        try:
            has_captcha = nav._requests_has_captcha(text)
        except DOSException as exc:
            raise ScholarAccessError(
                'Google Scholar returned a DOS/captcha challenge; not solving it',
                blocked=True,
            ) from exc
        if has_captcha:
            raise ScholarAccessError(
                f'Google Scholar returned a captcha (HTTP {response.status_code}); not solving it',
                blocked=True,
            )
        automated = 'automated queries' in text.lower()
        if automated or response.status_code in (403, 429):
            reason = 'automated-query block' if automated else 'refused the request'
            raise ScholarAccessError(
                f'Google Scholar {reason} (HTTP {response.status_code}); not bypassing it',
                blocked=True,
            )
        if response.status_code != 200:
            raise ScholarAccessError(
                f'Google Scholar returned HTTP {response.status_code}',
                blocked=False,
            )
        return text

    nav._get_page = _get_page
    return nav


def execute_attempt(scholar_id, output_dir):
    """Fetch once, directly. Raises ScholarAccessError when Scholar refuses."""
    scholarly.set_timeout(20)
    scholarly.set_retries(1)
    install_fail_fast_scholar_guards()
    generate_citation_data(scholar_id, output_dir)


def _write_status(output_dir, kind, detail):
    Path(output_dir, STATUS_NAME).write_text(f'{kind}\n{detail}', encoding='utf-8')


def _attempt(scholar_id, strategy, output_dir):
    """Child-process body. A non-direct strategy performs no request."""
    if strategy != 'direct':
        detail = f'refusing non-direct strategy {strategy!r}'
        _write_status(output_dir, 'blocked', detail)
        print(f'  {detail}', flush=True)
        sys.exit(2)
    try:
        execute_attempt(scholar_id, output_dir)
    except ScholarAccessError as exc:
        _write_status(output_dir, 'blocked' if exc.blocked else 'failed', str(exc))
        print(f'  direct failed: {exc}', flush=True)
        sys.exit(2 if exc.blocked else 1)
    except Exception as exc:
        _write_status(output_dir, 'failed', str(exc))
        print(f'  direct failed: {exc}', flush=True)
        sys.exit(1)
    _write_status(output_dir, 'success', '')


def _run_attempt(scholar_id, strategy, timeout, output_dir):
    """Return ``(outcome, detail)`` where outcome is success, blocked, or failed."""
    ctx = mp.get_context('fork')
    proc = ctx.Process(target=_attempt, args=(scholar_id, strategy, output_dir))
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        proc.kill()
        proc.join()
        print(f'  timed out after {timeout}s', flush=True)
        return 'failed', f'timed out after {timeout}s'
    status_path = Path(output_dir, STATUS_NAME)
    if not status_path.is_file():
        return 'failed', f'fetch process exited {proc.exitcode} without a status'
    kind, _, detail = status_path.read_text(encoding='utf-8').partition('\n')
    if kind == 'success' and proc.exitcode == 0:
        return 'success', ''
    if kind == 'blocked':
        return 'blocked', detail
    return 'failed', detail or f'fetch process exited {proc.exitcode}'


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


def run_fetch(scholar_id, runner=None):
    """Fetch directly. A refusal or any other failure ends the run.

    ``runner`` returns ``(outcome, detail)``. ``outcome`` is ``success``,
    ``blocked``, or ``failed``. Anything other than success returns before a
    later attempt, including a configured proxy attempt, can start. The
    default runner is looked up at call time so tests can replace it.
    """
    if runner is None:
        runner = _run_attempt
    results = Path('results')
    for index, (strategy, timeout) in enumerate(ATTEMPTS, 1):
        if strategy != 'direct':
            print('::error::Refusing a non-direct citation fetch. '
                  'Previously published citation data is kept.', flush=True)
            set_output('updated', 'false')
            return 'blocked'
        print(f'Attempt {index}/{len(ATTEMPTS)} (direct, timeout {timeout}s)', flush=True)
        with tempfile.TemporaryDirectory() as tmp:
            outcome, detail = runner(scholar_id, strategy, timeout, tmp)
            if outcome == 'success':
                results.mkdir(parents=True, exist_ok=True)
                for name in OUTPUT_FILES:
                    shutil.move(os.path.join(tmp, name), results / name)
                print('Citation data fetched successfully.', flush=True)
                set_output('updated', 'true')
                return 'success'
            if outcome == 'blocked':
                print(f'::error::Google Scholar refused the fetch: {detail} '
                      'The run stops without another request or a route change. '
                      'Previously published citation data is kept.', flush=True)
            else:
                print(f'::error::Google Scholar fetch failed: {detail} '
                      'The run stops without another request or a route change. '
                      'Previously published citation data is kept.', flush=True)
            set_output('updated', 'false')
            return outcome if outcome in ('blocked', 'failed') else 'failed'
    print('::error::Google Scholar fetch did not run. '
          'Previously published citation data is kept.', flush=True)
    set_output('updated', 'false')
    return 'failed'


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

    if run_fetch(scholar_id) != 'success':
        sys.exit(1)


if __name__ == '__main__':
    main()
