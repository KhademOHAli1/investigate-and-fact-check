"""Collector output must remain traceable evidence and unverified leads."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "skills/investigate-and-fact-check/scripts"
sys.path.insert(0, str(SCRIPTS))
from casekit.integration import import_recon, run_collection
from casekit.store import Case


def artifact(name="page-1.json", data=b'{"original":true}', cached=False, source_url="https://api.github.com/users/example/repos?page=1"):
    return SimpleNamespace(
        name=name, data=data, source_url=source_url,
        retrieved_at_utc="2026-11-01T10:00:00Z", observed_at_utc="2026-11-12T10:00:00Z",
        http_status=200, from_cache=cached, content_type="application/json",
        sha256=hashlib.sha256(data).hexdigest(),
    )


def result(raw=None, status="succeeded", adapter="github-repositories", observations=None):
    raw = artifact() if raw is None else raw
    return SimpleNamespace(
        adapter=adapter, status=status, input_value="example", artifacts=[raw],
        observations=observations if observations is not None else [
            {"kind": "repository", "value": "https://github.com/example/project", "artifact_name": raw.name,
             "origin_module": adapter, "provenance_status": "api-observation", "limitations": "Public metadata only"}
        ],
        requests=[{"url": raw.source_url, "status_code": 200, "from_cache": raw.from_cache}],
        limitations=["Discovery is not verification"], error="",
    )


class CollectionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve() / "case"
        Case.create(self.root, "Synthetic collection")

    def tearDown(self):
        self.temporary.cleanup()

    def test_collection_links_raw_response_run_and_unverified_leads(self):
        response = result()
        with patch("casekit.integration.collect", return_value=response):
            registered = run_collection(self.root, "github-repositories", "example")
        case = Case(self.root)
        self.assertEqual("succeeded", registered["status"])
        self.assertEqual(1, len(registered["evidence_ids"]))
        self.assertEqual(1, len(registered["lead_ids"]))
        evidence = case.read_records("evidence")[0]
        lead = case.read_records("leads")[0]
        run = case.read_records("runs")[0]
        self.assertEqual(registered["run_id"], evidence["run_id"])
        self.assertEqual(evidence["evidence_id"], lead["evidence_id"])
        self.assertEqual("2026-11-01T10:00:00Z", evidence["retrieved_at_utc"])
        self.assertEqual(hashlib.sha256(response.artifacts[0].data).hexdigest(), evidence["sha256"])
        self.assertEqual([], case.read_records("claims"))
        self.assertIn("Unverified", lead["limitations"])
        self.assertIn("requests", json.dumps(run))

    def test_repeated_cached_bytes_keep_separate_observations_and_original_time(self):
        with patch("casekit.integration.collect", return_value=result(artifact(cached=True))):
            first = run_collection(self.root, "github-repositories", "example")
            second = run_collection(self.root, "github-repositories", "example")
        self.assertNotEqual(first["evidence_ids"], second["evidence_ids"])
        case = Case(self.root)
        self.assertEqual(2, len(case.read_records("leads")))
        for evidence in case.read_records("evidence"):
            self.assertEqual("2026-11-01T10:00:00Z", evidence["retrieved_at_utc"])
            self.assertIn("Cached bytes", evidence["context_and_limitations"])
        self.assertEqual(1, len({item["relative_file_path"] for item in case.read_records("evidence")}))

    def test_failed_provider_does_not_create_claims_and_records_failure(self):
        response = result(status="failed")
        response.artifacts = []
        response.observations = []
        response.error = "Rate limited; retry later"
        with patch("casekit.integration.collect", return_value=response):
            registered = run_collection(self.root, "github-repositories", "example")
        case = Case(self.root)
        self.assertEqual("failed", registered["status"])
        self.assertEqual([], case.read_records("claims"))
        self.assertEqual([], case.read_records("evidence"))
        self.assertIn("failed", json.dumps(case.read_records("runs")))

    def test_import_preserves_export_with_unknown_original_provenance(self):
        raw = artifact(name="recon-export.json", source_url="")
        response = result(raw, adapter="recon-ng-import")
        response.observations[0]["provenance_status"] = "original-retrieval-unknown"
        with patch("casekit.integration.parse_recon_export", return_value=response):
            registered = import_recon(self.root, Path(self.temporary.name) / "input.json")
        case = Case(self.root)
        self.assertEqual(1, len(registered["lead_ids"]))
        self.assertTrue(case.read_records("sources")[0]["stable_locator"].startswith("recon-ng-export:sha256:"))
        self.assertIn("unknown", case.read_records("leads")[0]["limitations"])

    def test_malformed_adapter_cannot_escape_staging_and_run_is_failed(self):
        response = result(artifact(name="../escape.json"))
        with patch("casekit.integration.collect", return_value=response):
            with self.assertRaises(ValueError):
                run_collection(self.root, "github-repositories", "example")
        self.assertEqual([], Case(self.root).read_records("evidence"))
        self.assertIn("failed", json.dumps(Case(self.root).read_records("runs")))


if __name__ == "__main__":
    unittest.main()
