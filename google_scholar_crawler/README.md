# Citation crawler

The crawler targets Python 3.12 on Ubuntu 24.04. `requirements.in` pins direct
dependencies and `requirements.txt` locks their complete dependency graph.
`scholarly==1.5.1` needs the v1 `bibtexparser.bibdatabase` API, so keep
`bibtexparser==1.4.3` unless scholarly and its integration checks are upgraded
together. Installing successfully or passing `pip check` alone does not verify
that Python APIs are compatible.

To validate in a clean Python 3.12 virtual environment, from this directory:

```sh
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -v
```

The tests use the real installed dependencies for import and BibTeX checks, and
mock only Google Scholar requests for deterministic citation generation. They
check `gs_data.json` (including the publication-ID mapping used by the website)
and `gs_data_shieldsio.json`. They do not contact Google Scholar or require a
secret.

After deliberate dependency upgrades, regenerate the lock from the repository
root with [uv](https://docs.astral.sh/uv/), then rerun the checks above and CI:

```sh
uv pip compile --python-version 3.12 --python-platform x86_64-unknown-linux-gnu \
  google_scholar_crawler/requirements.in \
  --output-file google_scholar_crawler/requirements.txt \
  --no-header --no-emit-index-url
```

`Get Citation Data` runs offline validation for relevant pushes and pull
requests. Scheduled runs, page builds, and manual runs on `main` also fetch
Google Scholar using the `GOOGLE_SCHOLAR_ID` repository secret and publish both
JSON files to `google-scholar-stats`. Only that publishing job has repository
write permission.

A direct fetch that receives HTTP 403/429, Google's automated-query page, or a
captcha stops that attempt immediately. Captchas are not solved and no browser
is launched. The run then tries one more direct fetch and, if Scholar is still
refusing the runner, free HTTPS proxies. `free-proxy` 1.3 still treats table
column 6 as the Https flag; the live list's column 6 is "Last Checked", which
made every candidate look non-HTTPS. The crawler reads the Https column by its
header instead. Proxy addresses are tested with scholarly's own connectivity
check. If every attempt fails, the job exits non-zero, prints the block, and
does not push. `python main.py --publish-results` also refuses files whose
author, citation count, publication ids, and Shields badge disagree, so a bad
fetch cannot replace `google-scholar-stats`.

Treat these as separate verification levels:

1. **Local checks pass:** Python 3.12 imports, dependency consistency, BibTeX
   compatibility, and deterministic JSON generation work locally.
2. **CI checks pass:** the same checks pass on the configured GitHub runner. A
   push/PR run skips the live fetch and publishing job by design.
3. **Live data updates:** a scheduled/page-build/manual run completes the fetch
   and publish steps, and the output branch contains valid JSON with a new
   `updated` timestamp. An automated-query block, captcha, or proxy-list
   failure still leaves the previous branch untouched even if both offline
   checks pass.
