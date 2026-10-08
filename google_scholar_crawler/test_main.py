"""Offline checks for the installed dependencies and the site's citation JSON."""

from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime
from io import StringIO
import json
from pathlib import Path
import tempfile
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


if __name__ == "__main__":
    unittest.main()
