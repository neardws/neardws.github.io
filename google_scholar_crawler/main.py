"""Fetch Google Scholar citation data for the homepage.

Google Scholar intermittently blocks GitHub runner IPs: it then serves a
captcha/consent page (scholarly fails with ``'NoneType' object has no
attribute 'text'``) or scholarly backs off until the job times out.  This
script therefore:

* runs every attempt in a child process with a hard timeout,
* retries a few times directly, then through scholarly's FreeProxies,
* validates the result and writes the JSON files only after a fully
  successful fetch, so a failed run never replaces good data with empty data.
"""

import json
import multiprocessing as mp
import os
from datetime import datetime
from pathlib import Path
import shutil
import sys
import tempfile
import time

from scholarly import ProxyGenerator, scholarly

SECTIONS = ['basics', 'indices', 'counts', 'publications']
# (strategy, hard timeout in seconds) for each attempt, in order.
# Total worst case (~11 min) stays inside the workflow's 15-minute job timeout.
ATTEMPTS = [('direct', 120), ('direct', 120), ('free_proxy', 180), ('free_proxy', 180)]
RETRY_DELAY = 15
OUTPUT_FILES = ('gs_data.json', 'gs_data_shieldsio.json')


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


def _attempt(scholar_id, strategy, output_dir):
    """Child-process body: configure the connection and fetch once."""
    scholarly.set_timeout(30)
    scholarly.set_retries(2)
    if strategy == 'free_proxy':
        pg = ProxyGenerator()
        if not pg.FreeProxies(timeout=5, wait_time=60):
            raise RuntimeError('no working free proxy found')
        scholarly.use_proxy(pg, pg)
    generate_citation_data(scholar_id, output_dir)


def _run_attempt(scholar_id, strategy, timeout, output_dir):
    ctx = mp.get_context('fork')
    proc = ctx.Process(target=_attempt, args=(scholar_id, strategy, output_dir))
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        proc.kill()
        proc.join()
        print(f'  timed out after {timeout}s')
        return False
    return proc.exitcode == 0


def set_output(name, value):
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a', encoding='utf-8') as fh:
            fh.write(f'{name}={value}\n')


def main():
    scholar_id = os.environ.get('GOOGLE_SCHOLAR_ID')
    if not scholar_id:
        print('ERROR: GOOGLE_SCHOLAR_ID is not set')
        sys.exit(1)

    results = Path('results')
    for i, (strategy, timeout) in enumerate(ATTEMPTS, 1):
        print(f'Attempt {i}/{len(ATTEMPTS)} ({strategy}, timeout {timeout}s)', flush=True)
        with tempfile.TemporaryDirectory() as tmp:
            if _run_attempt(scholar_id, strategy, timeout, tmp):
                results.mkdir(parents=True, exist_ok=True)
                for name in OUTPUT_FILES:
                    shutil.move(os.path.join(tmp, name), results / name)
                print('Citation data fetched successfully.')
                set_output('updated', 'true')
                return
        if i < len(ATTEMPTS):
            time.sleep(RETRY_DELAY)

    # Exit non-zero so the publish step is skipped and the previously published
    # gs_data.json on google-scholar-stats is left untouched.
    print('::error::Google Scholar fetch failed on every attempt (likely blocked); '
          'previously published citation data is kept.')
    set_output('updated', 'false')
    sys.exit(1)


if __name__ == '__main__':
    main()
