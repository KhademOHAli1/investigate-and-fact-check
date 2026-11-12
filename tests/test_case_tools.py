"""Behavioral tests for persistent case records and portable case snapshots."""

from __future__ import annotations

import csv
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/investigate-and-fact-check/scripts"
sys.path.insert(0, str(SCRIPTS))
from casekit import Case, CaseError


class CaseToolTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.case = Case.create(self.root / "case", "Synthetic case")
        self.file = self.root / "record.txt"
        self.file.write_bytes(b"Synthetic original.\n")

    def tearDown(self):
        self.temporary.cleanup()

    def source(self, **kwargs):
        return self.case.add_source("https://example.test/record", **kwargs)

    def evidence(self, **kwargs):
        source = self.source()
        return self.case.add_evidence(self.file, source["source_id"], "test/1", **kwargs)

    def mutate(self, record_id, field, value):
        with closing(sqlite3.connect(self.case.path / "case.sqlite3")) as connection, connection:
            payload = json.loads(connection.execute("SELECT payload FROM records WHERE id=?", (record_id,)).fetchone()[0])
            payload[field] = value
            connection.execute("UPDATE records SET payload=? WHERE id=?", (json.dumps(payload), record_id))

    def test_reopen_preserves_records_and_monotonic_ids(self):
        first = self.source()
        reopened = Case(self.case.path)
        second = reopened.add_source("https://example.test/other")
        self.assertEqual("S001", first["source_id"])
        self.assertEqual("S002", second["source_id"])
        self.assertEqual([first, second], reopened.read_records("sources"))
        self.assertEqual(2, reopened.status()["counts"]["sources"])
        with self.assertRaises(FileExistsError):
            Case.create(self.case.path, "Must not replace")

    def test_byte_dedup_keeps_observations_and_original_unchanged(self):
        first = self.evidence()
        second_source = self.case.add_source("https://different.test/repeated")
        second = self.case.add_evidence(self.file, second_source["source_id"], "test/2")
        self.assertNotEqual(first["evidence_id"], second["evidence_id"])
        self.assertEqual(first["relative_file_path"], second["relative_file_path"])
        self.assertEqual(first["evidence_id"], second["duplicate_of"])
        self.assertNotEqual(first["source_id"], second["source_id"])
        self.assertEqual(1, len(list((self.case.path / "originals").iterdir())))
        self.assertEqual(self.file.read_bytes(), (self.case.path / first["relative_file_path"]).read_bytes())
        self.assertEqual(hashlib.sha256(self.file.read_bytes()).hexdigest(), first["sha256"])
        self.assertEqual("", first["retrieved_at_utc"])
        self.assertEqual("ok", self.case.check()["status"])

    def test_claim_references_and_source_independence_stay_explicit(self):
        first_source = self.source(origin_group="one-origin")
        second_source = self.case.add_source("https://mirror.test/record", origin_group="different-label", derived_from_source_ids=[first_source["source_id"]])
        first = self.case.add_evidence(self.file, first_source["source_id"], "test/1")
        second = self.case.add_evidence(self.file, second_source["source_id"], "test/1")
        claim = self.case.add_claim("Synthetic assertion", support=[first["evidence_id"], second["evidence_id"]], verdict="Supported")
        self.assertEqual(["different-label", "one-origin"], claim["origin_groups"])
        self.assertTrue({"dependent_sources", "limited_corroboration", "duplicate_support_bytes"}.issubset(w["code"] for w in self.case.check()["warnings"]))
        unresolved = self.case.add_claim("A question without evidence")
        self.assertEqual("Unresolved", unresolved["verdict"])
        with self.assertRaises(CaseError):
            self.case.add_claim("Bad reference", support=["E999"])

    def test_changed_and_missing_originals_are_detected(self):
        evidence = self.evidence()
        stored = self.case.path / evidence["relative_file_path"]
        stored.write_bytes(b"Changed bytes.\n")
        self.assertIn("changed_original", {x["code"] for x in self.case.check()["errors"]})
        stored.unlink()
        self.assertIn("missing_or_unsafe_original", {x["code"] for x in self.case.check()["errors"]})

    def test_dangling_references_time_errors_and_dependency_cycles(self):
        first = self.source()
        second = self.case.add_source("https://example.test/second", derived_from_source_ids=[first["source_id"]])
        evidence = self.case.add_evidence(self.file, first["source_id"], "test/1")
        claim = self.case.add_claim("Claim", support=[evidence["evidence_id"]])
        self.mutate(first["source_id"], "derived_from_source_ids", [second["source_id"]])
        self.mutate(claim["claim_id"], "contradicting_evidence_ids", ["E999"])
        self.mutate(evidence["evidence_id"], "retrieved_at_utc", "yesterday")
        codes = {x["code"] for x in self.case.check()["errors"]}
        self.assertTrue({"source_dependency_cycle", "dangling_reference", "invalid_timestamp"}.issubset(codes))

    def test_entities_and_leads_retain_duplicate_observations(self):
        entity = self.case.add_entity("Example Ltd", "company", "registry:123")
        duplicate = self.case.add_entity("Example Limited", "company", "registry:123")
        self.assertEqual(entity["entity_id"], duplicate["duplicate_of"])
        evidence = self.evidence()
        relation = self.case.add_relationship(entity["entity_id"], "documented_name_variant", duplicate["entity_id"], [evidence["evidence_id"]])
        lead = self.case.add_lead("domain", "example.test", evidence["evidence_id"], evidence["source_id"])
        duplicate_lead = self.case.add_lead("domain", "example.test", evidence["evidence_id"], evidence["source_id"])
        self.assertEqual(lead["lead_id"], duplicate_lead["duplicate_of"])
        self.assertEqual("unverified", lead["verification_status"])
        self.assertEqual("R001", relation["relationship_id"])
        self.assertEqual("ok", self.case.check()["status"])

    def test_runs_record_real_outcomes_and_redact_credentials(self):
        run = self.case.start_run("fixture/1", {"token": "do-not-store", "nested": {"Authorization": "Bearer abc"}, "url": "https://user:pass@example.test/path?api_key=hidden&term=public"}, ["example.test"])
        self.assertEqual("running", run["status"])
        final = self.case.finish_run(run["run_id"], "partial", {"evidence_ids": [], "requests": [{"status": 429}]}, "Bearer sensitive")
        stored = json.dumps(self.case.read_records("runs"))
        for forbidden in ("do-not-store", "hidden", "sensitive", "user:pass", '"Bearer abc"'):
            self.assertNotIn(forbidden, stored)
        self.assertEqual("partial", final["status"])
        self.assertEqual(429, final["outputs"]["requests"][0]["status"])
        with self.assertRaises(CaseError):
            self.case.finish_run(run["run_id"], "succeeded", {})

    def test_report_is_deterministic_escapes_untrusted_text_and_keeps_contrary_evidence(self):
        evidence = self.evidence()
        self.case.add_claim('<script>alert("x")</script> ![remote](https://bad.test/image)', support=[evidence["evidence_id"]], contradict=[evidence["evidence_id"]], unresolved_question="Need an independent record")
        first, second = self.root / "first.md", self.root / "second.md"
        self.case.report(first)
        self.case.report(second)
        content = first.read_text()
        self.assertEqual(content, second.read_text())
        self.assertIn("&lt;script&gt;", content)
        self.assertNotIn("<script>", content)
        self.assertNotIn("![remote](", content)
        self.assertIn("Contrary evidence: E001", content)
        self.assertIn("Unresolved", content)
        with self.assertRaises(FileExistsError):
            self.case.report(first)

    def test_exports_preserve_json_and_template_headers(self):
        self.case.add_source("local:record", name="=UNTRUSTED()")
        output = self.root / "export"
        self.case.export(output)
        payload = json.loads((output / "case-records.json").read_text())
        self.assertEqual("=UNTRUSTED()", payload["records"]["sources"][0]["public_name_or_protected_code"])
        with (output / "source-ledger.csv").open(newline="") as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual("'=UNTRUSTED()", row["public_name_or_protected_code"])
        template = ROOT / "skills/investigate-and-fact-check/assets/source-ledger.csv"
        self.assertEqual(template.read_text().strip(), (output / "source-ledger.csv").read_text().splitlines()[0])
        with self.assertRaises(FileExistsError):
            self.case.export(output)

    def test_complete_checkpoint_restores_evidence_config_and_id_state(self):
        evidence = self.evidence()
        self.case.add_claim("A scoped claim", contradict=[evidence["evidence_id"]])
        (self.case.path / "analysis" / "notes.txt").write_text("Synthetic analysis")
        (self.case.path / "derivatives" / "ocr.txt").write_text("Derivative")
        archive = self.root / "checkpoint.zip"
        self.case.checkpoint(archive)
        restored = Case.restore(archive, self.root / "restored")
        self.assertEqual(self.case.metadata, restored.metadata)
        self.assertEqual(self.case.read_records("evidence"), restored.read_records("evidence"))
        self.assertEqual("Synthetic analysis", (restored.path / "analysis/notes.txt").read_text())
        self.assertEqual("Derivative", (restored.path / "derivatives/ocr.txt").read_text())
        self.assertEqual("S002", restored.add_source("new:record")["source_id"])
        self.assertEqual("ok", restored.check()["status"])
        with self.assertRaises(CaseError):
            Case.restore(archive, restored.path)
        with self.assertRaises(CaseError):
            self.case.checkpoint(self.case.path / "bad.zip")

    def test_checkpoint_refuses_changed_registered_evidence(self):
        evidence = self.evidence()
        (self.case.path / evidence["relative_file_path"]).write_bytes(b"Tampered record")
        archive = self.root / "invalid.zip"
        with self.assertRaisesRegex(CaseError, "integrity checks failed"):
            self.case.checkpoint(archive)
        self.assertFalse(archive.exists())

    def test_restore_rejects_traversal_and_tampered_artifacts_without_leaving_case(self):
        archive = self.root / "evil.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("../outside.txt", "bad")
        with self.assertRaises(CaseError):
            Case.restore(archive, self.root / "not-created")
        self.assertFalse((self.root / "outside.txt").exists())
        self.evidence()
        original = self.root / "original.zip"
        self.case.checkpoint(original)
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(archive, "w") as dest:
            for item in source.infolist():
                data = b"tampered" if item.filename.startswith("originals/") else source.read(item.filename)
                dest.writestr(item, data)
        with self.assertRaises(CaseError):
            Case.restore(archive, self.root / "not-created")
        self.assertFalse((self.root / "not-created").exists())

    def test_registration_refuses_symlink_and_invalid_time(self):
        link = self.root / "linked.txt"
        try:
            link.symlink_to(self.file)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable")
        source = self.source()
        with self.assertRaises(CaseError):
            self.case.add_evidence(link, source["source_id"], "test/1")
        with self.assertRaises(CaseError):
            self.case.add_evidence(self.file, source["source_id"], "test/1", retrieved_at_utc="2026-11-12")

    def test_cli_creates_and_reopens_case_from_an_unrelated_directory(self):
        path = self.root / "cli-case"
        result = subprocess.run([sys.executable, str(SCRIPTS / "case.py"), "case", "init", str(path), "--title", "CLI fixture"], cwd=self.root, text=True, capture_output=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("ready", json.loads(result.stdout)["status"])
        result = subprocess.run([sys.executable, str(SCRIPTS / "case.py"), "case", "check", str(path)], cwd=self.root, text=True, capture_output=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("ok", json.loads(result.stdout)["status"])


if __name__ == "__main__":
    unittest.main()
