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

Treat these as separate verification levels:

1. **Local checks pass:** Python 3.12 imports, dependency consistency, BibTeX
   compatibility, and deterministic JSON generation work locally.
2. **CI checks pass:** the same checks pass on the configured GitHub runner. A
   push/PR run skips the live fetch and publishing job by design.
3. **Live data updates:** a scheduled/page-build/manual run completes the fetch
   and publish steps, and the output branch contains valid JSON with a new
   `updated` timestamp. Scholar blocking or network failures can still prevent
   this even if both offline checks pass.
