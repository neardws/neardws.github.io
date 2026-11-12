"""Offline checks for the installed dependencies and the site's citation JSON."""

from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from scholarly import scholarly

import main as crawler


class DependencyCompatibilityTests(unittest.TestCase):
    def test_scholarly_bibtex_uses_the_installed_v1_api(self):
        """Exercise scholarly's BibDatabase/dumps integration, not just pip metadata."""
        publication = {
            "container_type": "Publication",
            "filled": True,
            "bib": {
                "pub_type": "article",
                "bib_id": "xu2026example",
                "title": "A citation compatibility example",
                "author": "Xincao Xu",
                "year": "2026",
            },
        }

        bibtex = scholarly.bibtex(publication)
        database = bibtexparser.loads(bibtex)

        self.assertIsInstance(database, BibDatabase)
        self.assertEqual(len(database.entries), 1)
        self.assertEqual(database.entries[0]["ENTRYTYPE"], "article")
        self.assertEqual(database.entries[0]["ID"], "xu2026example")
        self.assertEqual(database.entries[0]["title"], "A citation compatibility example")


class CitationDataTests(unittest.TestCase):
    def generate(self, profile, output_dir):
        """Only replace Scholar requests; use the real installed module and writer."""
        scholar_id = "example-scholar-id"
        author = {"scholar_id": scholar_id}

        def fill_author(target, sections):
            target.update(deepcopy(profile))
            return target

        before = datetime.now().timestamp()
        with (
            patch.object(crawler.scholarly, "search_author_id", return_value=author) as search,
            patch.object(crawler.scholarly, "fill", side_effect=fill_author) as fill,
            redirect_stdout(StringIO()),
        ):
            crawler.generate_citation_data(scholar_id, output_dir=output_dir)
        after = datetime.now().timestamp()

        search.assert_called_once_with(scholar_id)
        fill.assert_called_once_with(
            author, sections=["basics", "indices", "counts", "publications"]
        )
        self.assertEqual(
            {path.name for path in output_dir.iterdir()},
            {"gs_data.json", "gs_data_shieldsio.json"},
        )
        data_text = (output_dir / "gs_data.json").read_text(encoding="utf-8")
        data = json.loads(data_text)
        badge = json.loads(
            (output_dir / "gs_data_shieldsio.json").read_text(encoding="utf-8")
        )
        updated = datetime.fromisoformat(data["updated"]).timestamp()
        self.assertLessEqual(before, updated)
        self.assertLessEqual(updated, after)
        return data, badge, data_text

    def test_generates_site_and_shields_json_with_unicode_and_publication_ids(self):
        profile = {
            "name": "许新操",
            "citedby": 35,
            "cites_per_year": {2025: 12, 2026: 23},
            "publications": [
                {
                    "author_pub_id": "example-scholar-id:first-paper",
                    "num_citations": 30,
                    "bib": {"title": "协同感知与信息融合"},
                },
                {
                    "author_pub_id": "example-scholar-id:second-paper",
                    "num_citations": 5,
                    "bib": {"title": "Edge inference"},
                },
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "new" / "results"
            data, badge, text = self.generate(profile, output_dir)

        self.assertEqual(data["name"], profile["name"])
        self.assertEqual(data["citedby"], 35)
        self.assertEqual(data["cites_per_year"], {"2025": 12, "2026": 23})
        self.assertEqual(
            data["publications"],
            {publication["author_pub_id"]: publication for publication in profile["publications"]},
        )
        self.assertEqual(
            data["publications"]["example-scholar-id:first-paper"]["num_citations"],
            30,
        )
        self.assertIn("许新操", text)
        self.assertIn("协同感知与信息融合", text)
        self.assertEqual(badge, {"schemaVersion": 1, "label": "citations", "message": "35"})

    def test_preserves_empty_publications_and_zero_citations(self):
        profile = {"name": "New Author", "citedby": 0, "publications": []}

        with tempfile.TemporaryDirectory() as directory:
            data, badge, _ = self.generate(profile, Path(directory))

        self.assertEqual(data["citedby"], 0)
        self.assertEqual(data["publications"], {})
        self.assertEqual(badge, {"schemaVersion": 1, "label": "citations", "message": "0"})


class _Response:
    def __init__(self, status_code, text="", content=None):
        self.status_code = status_code
        self.text = text
        self.content = text.encode("utf-8") if content is None else content


class ScholarBlockGuardTests(unittest.TestCase):
    def _navigator(self):
        return crawler.scholarly._Scholarly__nav

    def _guard(self, response):
        nav = self._navigator()
        saved = (
            nav._get_page,
            nav._session1.get,
            nav.pm1._handle_captcha2,
            nav.pm1._get_webdriver,
        )
        webdriver_calls = []
        nav.pm1._handle_captcha2 = lambda *args, **kwargs: webdriver_calls.append("captcha")
        nav.pm1._get_webdriver = lambda *args, **kwargs: webdriver_calls.append("webdriver")
        nav._session1.get = lambda *args, **kwargs: response
        crawler.install_fail_fast_scholar_guards(pause_seconds=0)
        return nav, saved, webdriver_calls

    def _restore(self, nav, saved):
        nav._get_page, nav._session1.get, nav.pm1._handle_captcha2, nav.pm1._get_webdriver = saved

    def test_automated_query_403_fails_fast_without_a_browser_or_long_sleep(self):
        sorry = (
            "<html><title>Sorry...</title><body>"
            "your computer or network may be sending automated queries"
            "</body></html>"
        )
        nav, saved, webdriver_calls = self._guard(_Response(403, text=sorry))
        started = time.monotonic()
        try:
            with self.assertRaises(crawler.ScholarAccessError) as raised:
                nav._get_page("https://scholar.google.com/citations?user=example")
        finally:
            self._restore(nav, saved)
        self.assertLess(time.monotonic() - started, 2)
        self.assertIn("automated-query block", str(raised.exception))
        self.assertIn("not bypassing it", str(raised.exception))
        self.assertTrue(raised.exception.blocked)
        self.assertEqual(webdriver_calls, [])

    def test_captcha_page_is_not_handed_to_the_solver(self):
        nav, saved, webdriver_calls = self._guard(
            _Response(200, text='<html><div id="gs_captcha_ccl"></div></html>')
        )
        try:
            with self.assertRaises(crawler.ScholarAccessError) as raised:
                nav._get_page("https://scholar.google.com/citations?user=example")
        finally:
            self._restore(nav, saved)
        self.assertIn("not solving it", str(raised.exception))
        self.assertTrue(raised.exception.blocked)
        self.assertEqual(webdriver_calls, [])

    def test_dos_challenge_is_not_retried_inside_scholarly(self):
        nav, saved, webdriver_calls = self._guard(
            _Response(200, text='<html><div class="rc-doscaptcha-body"></div></html>')
        )
        try:
            with self.assertRaises(crawler.ScholarAccessError) as raised:
                nav._get_page("https://scholar.google.com/citations?user=example")
        finally:
            self._restore(nav, saved)
        self.assertIn("not solving it", str(raised.exception))
        self.assertEqual(webdriver_calls, [])
        self.assertTrue(raised.exception.blocked)

    def test_schedule_is_one_direct_fetch(self):
        self.assertEqual([strategy for strategy, _timeout in crawler.ATTEMPTS], ["direct"])
        self.assertFalse(hasattr(crawler, "_free_proxy_generator"))
        self.assertFalse(hasattr(crawler, "fetch_proxy_candidates"))
        self.assertFalse(hasattr(crawler, "PROXY_LIST_URLS"))


class BlockStopsTheRunTests(unittest.TestCase):
    """A Scholar refusal must not start another request or a proxy."""

    MULTI_ROUTE_SCHEDULE = (("direct", 30), ("direct", 30), ("free_proxy", 120))

    def setUp(self):
        self._pause = crawler.SCHOLAR_REQUEST_PAUSE
        crawler.SCHOLAR_REQUEST_PAUSE = 0

    def tearDown(self):
        crawler.SCHOLAR_REQUEST_PAUSE = self._pause

    def test_blocked_outcome_does_not_start_a_later_attempt(self):
        calls = []

        def runner(scholar_id, strategy, timeout, output_dir):
            calls.append((strategy, timeout))
            return "blocked", "Google Scholar refused the request (HTTP 403); not bypassing it"

        with patch.object(crawler, "ATTEMPTS", self.MULTI_ROUTE_SCHEDULE):
            outcome = crawler.run_fetch("example-scholar-id", runner=runner)

        self.assertEqual(outcome, "blocked")
        self.assertEqual(calls, [("direct", 30)])

    def test_other_failure_does_not_start_a_later_attempt_or_proxy(self):
        calls = []

        def runner(scholar_id, strategy, timeout, output_dir):
            calls.append(strategy)
            return "failed", "timed out after 30s"

        with patch.object(crawler, "ATTEMPTS", self.MULTI_ROUTE_SCHEDULE):
            outcome = crawler.run_fetch("example-scholar-id", runner=runner)

        self.assertEqual(outcome, "failed")
        self.assertEqual(calls, ["direct"])

    def test_child_process_body_refuses_a_proxy_strategy_without_requesting(self):
        nav = crawler.scholarly._Scholarly__nav
        calls = []
        original = nav._session1.get
        nav._session1.get = lambda *args, **kwargs: calls.append(args) or (_ for _ in ()).throw(
            AssertionError("request")
        )
        try:
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(SystemExit) as raised:
                    crawler._attempt("example-scholar-id", "free_proxy", directory)
                status = (Path(directory) / crawler.STATUS_NAME).read_text(encoding="utf-8")
        finally:
            nav._session1.get = original
        self.assertEqual(raised.exception.code, 2)
        self.assertTrue(status.startswith("blocked\n"))
        self.assertIn("free_proxy", status)
        self.assertEqual(calls, [])

    def test_non_direct_schedule_makes_no_request(self):
        def runner(scholar_id, strategy, timeout, output_dir):
            raise AssertionError(f"runner invoked for {strategy}")

        with patch.object(crawler, "ATTEMPTS", (("free_proxy", 120), ("direct", 30))):
            outcome = crawler.run_fetch("example-scholar-id", runner=runner)

        self.assertEqual(outcome, "blocked")

    def _run_real_attempt_against(self, response):
        from scholarly import ProxyGenerator

        nav = crawler.scholarly._Scholarly__nav
        saved = (nav._get_page, nav._session1.get)
        calls = []

        def record_get(url, timeout=None, **kwargs):
            calls.append(url)
            return response

        nav._session1.get = record_get

        def runner(scholar_id, strategy, timeout, output_dir):
            try:
                crawler.execute_attempt(scholar_id, output_dir)
            except crawler.ScholarAccessError as exc:
                return ("blocked" if exc.blocked else "failed"), str(exc)
            return "success", ""

        try:
            with (
                patch.object(crawler.requests, "get", side_effect=AssertionError("proxy list")),
                patch.object(
                    crawler.scholarly,
                    "use_proxy",
                    side_effect=AssertionError("route change"),
                ),
                patch.object(
                    ProxyGenerator,
                    "SingleProxy",
                    side_effect=AssertionError("single proxy"),
                ),
                patch.object(
                    ProxyGenerator,
                    "FreeProxies",
                    side_effect=AssertionError("free proxies"),
                ),
                patch.object(crawler, "ATTEMPTS", self.MULTI_ROUTE_SCHEDULE),
            ):
                outcome = crawler.run_fetch("example-scholar-id", runner=runner)
        finally:
            nav._get_page, nav._session1.get = saved
        return outcome, calls

    def test_automated_query_403_does_not_send_another_request_or_use_a_proxy(self):
        sorry = (
            "<html><title>Sorry...</title><body>"
            "your computer or network may be sending automated queries"
            "</body></html>"
        )
        outcome, calls = self._run_real_attempt_against(_Response(403, text=sorry))
        self.assertEqual(outcome, "blocked")
        self.assertEqual(len(calls), 1)
        self.assertIn("scholar.google.com", calls[0])
        self.assertNotIn("free-proxy-list", calls[0])
        self.assertNotIn("sslproxies", calls[0])

    def test_429_and_captcha_each_stop_after_the_refusing_response(self):
        for response in (
            _Response(429, text="slow down"),
            _Response(200, text='<html><div id="gs_captcha_ccl"></div></html>'),
            _Response(200, text='<html><div class="rc-doscaptcha-body"></div></html>'),
        ):
            with self.subTest(status=response.status_code, body=response.text[:40]):
                outcome, calls = self._run_real_attempt_against(response)
                self.assertEqual(outcome, "blocked")
                self.assertEqual(len(calls), 1)
                self.assertIn("scholar.google.com", calls[0])


class PublicationGuardTests(unittest.TestCase):
    def write_valid(self, directory, citedby=35):
        data = {
            "name": "许新操",
            "scholar_id": "example-scholar-id",
            "citedby": citedby,
            "updated": "2026-11-10 16:07:03.595769",
            "publications": {
                "example-scholar-id:first-paper": {
                    "author_pub_id": "example-scholar-id:first-paper",
                    "num_citations": citedby,
                    "bib": {"title": "协同感知与信息融合"},
                }
            },
        }
        badge = {"schemaVersion": 1, "label": "citations", "message": str(citedby)}
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "gs_data.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        (directory / "gs_data_shieldsio.json").write_text(json.dumps(badge), encoding="utf-8")
        return data

    def test_check_accepts_consistent_files_and_rejects_a_mismatched_badge(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_valid(directory)
            crawler.assert_citation_files_ready(directory)
            badge_path = Path(directory) / "gs_data_shieldsio.json"
            badge_path.write_text(
                json.dumps({"schemaVersion": 1, "label": "citations", "message": "0"}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                crawler.assert_citation_files_ready(directory)

    def test_check_rejects_untransformed_publication_list(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_valid(directory)
            data_path = Path(directory) / "gs_data.json"
            data = json.loads(data_path.read_text(encoding="utf-8"))
            data["publications"] = list(data["publications"].values())
            data_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                crawler.assert_citation_files_ready(directory)

    def test_publish_pushes_only_ready_files_to_a_local_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results = root / "results"
            bare = root / "remote.git"
            self.write_valid(results, citedby=36)
            subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True)
            crawler.publish_citation_files(results, str(bare))
            published = subprocess.run(
                ["git", "--git-dir", str(bare), "show", "google-scholar-stats:gs_data.json"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(json.loads(published.stdout)["citedby"], 36)
            badge = subprocess.run(
                ["git", "--git-dir", str(bare), "show", "google-scholar-stats:gs_data_shieldsio.json"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(json.loads(badge.stdout)["message"], "36")

            data_path = results / "gs_data.json"
            data_path.write_text("{", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                crawler.publish_citation_files(results, str(bare))
            again = subprocess.run(
                ["git", "--git-dir", str(bare), "show", "google-scholar-stats:gs_data.json"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(json.loads(again.stdout)["citedby"], 36)

    def test_failed_fetch_keeps_existing_results_and_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory) / "results"
            self.write_valid(results, citedby=520)
            sentinel = (results / "gs_data.json").read_text(encoding="utf-8")
            previous = os.getcwd()
            os.chdir(directory)
            try:
                calls = []

                def fail(scholar_id, strategy, timeout, output_dir):
                    calls.append(strategy)
                    return "blocked", "Google Scholar refused the request (HTTP 403); not bypassing it"

                with (
                    patch.dict(os.environ, {"GOOGLE_SCHOLAR_ID": "example-scholar-id"}),
                    patch.object(crawler, "_run_attempt", side_effect=fail),
                    patch.object(
                        crawler,
                        "ATTEMPTS",
                        [("direct", 1), ("direct", 1), ("free_proxy", 1)],
                    ),
                ):
                    with self.assertRaises(SystemExit) as raised:
                        crawler.main([])
                self.assertEqual(calls, ["direct"])
            finally:
                os.chdir(previous)
            self.assertEqual(raised.exception.code, 1)
            self.assertEqual((results / "gs_data.json").read_text(encoding="utf-8"), sentinel)

    def test_successful_attempt_moves_files_without_publishing(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            os.chdir(directory)
            try:
                def succeed(scholar_id, strategy, timeout, output_dir):
                    self.write_valid(output_dir, citedby=7)
                    return "success", ""

                with (
                    patch.dict(os.environ, {"GOOGLE_SCHOLAR_ID": "example-scholar-id"}),
                    patch.object(crawler, "_run_attempt", side_effect=succeed),
                ):
                    crawler.main([])
            finally:
                os.chdir(previous)
            ready = json.loads((Path(directory) / "results" / "gs_data.json").read_text(encoding="utf-8"))
            self.assertEqual(ready["citedby"], 7)


if __name__ == "__main__":
    unittest.main()
