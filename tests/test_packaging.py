"""Check the released artifact contents and their reproducibility."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_dist", REPOSITORY / "tools" / "build_dist.py")
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
SKILL = "investigate-and-fact-check"


class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "first"
        cls.artifacts = BUILDER.build(REPOSITORY, cls.output)
        cls.version = (REPOSITORY / "VERSION").read_text().strip()

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def _archive(self, variant):
        return zipfile.ZipFile(self.output / f"{SKILL}-{variant}-v{self.version}.zip")

    def _assert_links_exist(self, archive, prefix):
        names = set(archive.namelist())
        for name in names:
            if not name.startswith(prefix) or not name.endswith(".md"):
                continue
            content = archive.read(name).decode("utf-8")
            # Inline Markdown links, including the ![] form used for the icon.
            for target in re.findall(r"\]\(([^)]+)\)", content):
                target = target.strip().split(' "', 1)[0].strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
                exists = resolved in names or any(item.startswith(resolved + "/") for item in names)
                self.assertTrue(exists, f"Broken link in {name}: {target}")

    def test_skill_archives_are_complete_and_vendor_scoped(self):
        canonical = REPOSITORY / "skills" / SKILL
        expected = {
            p.relative_to(canonical).as_posix()
            for p in BUILDER._public_files(canonical)
        } | {"LICENSE"}
        license_bytes = (REPOSITORY / "LICENSE").read_bytes()
        for variant in BUILDER.VARIANTS:
            with self.subTest(variant=variant), self._archive(variant) as archive:
                actual = {name.removeprefix(f"{SKILL}/") for name in archive.namelist()}
                expected_variant = expected if variant == "codex" else {name for name in expected if not name.startswith("agents/")}
                self.assertEqual(expected_variant, actual)
                self.assertEqual(license_bytes, archive.read(f"{SKILL}/LICENSE"))
                entrypoint = archive.read(f"{SKILL}/SKILL.md").decode("utf-8")
                self.assertIn(f"name: {SKILL}", entrypoint.splitlines())
                self.assertRegex(entrypoint, r"(?m)^description: .+")
                self.assertIn("license: MIT", entrypoint.splitlines())
                self.assertEqual(variant == "codex", f"{SKILL}/agents/openai.yaml" in archive.namelist())
                for name in archive.namelist():
                    relative = name.removeprefix(f"{SKILL}/")
                    if relative != "LICENSE":
                        self.assertEqual((canonical / relative).read_bytes(), archive.read(name))
                self._assert_links_exist(archive, f"{SKILL}/")

    def test_plugin_archive_is_self_contained(self):
        with self._archive("claude-plugin") as archive:
            names = set(archive.namelist())
            manifest = json.loads(archive.read(f"{SKILL}/.claude-plugin/plugin.json"))
            self.assertEqual(SKILL, manifest["name"])
            self.assertEqual(self.version, manifest["version"])
            self.assertEqual("MIT", manifest["license"])
            self.assertIn(f"{SKILL}/README.md", names)
            self.assertIn(f"{SKILL}/skills/{SKILL}/SKILL.md", names)
            self.assertIn(f"{SKILL}/skills/{SKILL}/scripts/evidence_manifest.py", names)
            self.assertFalse(any("/agents/" in name for name in names))
            self.assertNotIn(f"{SKILL}/.claude-plugin/marketplace.json", names)
            self._assert_links_exist(archive, f"{SKILL}/")

    def test_archive_paths_and_metadata_are_safe(self):
        for artifact in self.artifacts:
            if artifact.suffix != ".zip":
                continue
            with self.subTest(artifact=artifact.name), zipfile.ZipFile(artifact) as archive:
                self.assertEqual(sorted(archive.namelist()), archive.namelist())
                self.assertEqual(len(archive.namelist()), len(set(archive.namelist())))
                for entry in archive.infolist():
                    path = PurePosixPath(entry.filename)
                    self.assertFalse(path.is_absolute())
                    self.assertNotIn("..", path.parts)
                    self.assertEqual(SKILL, path.parts[0])
                    self.assertEqual(BUILDER.ARCHIVE_TIME, entry.date_time)
                    self.assertEqual(0o100644, entry.external_attr >> 16)
                    self.assertFalse(any(part in {"tests", "__pycache__", ".git", "dist"} for part in path.parts))
                    hidden_parts = [part for part in path.parts if part.startswith(".")]
                    self.assertIn(hidden_parts, ([], [".claude-plugin"]))

    def test_repeated_builds_have_identical_bytes_and_checksums(self):
        second = Path(self.temporary.name) / "second"
        repeated = BUILDER.build(REPOSITORY, second)
        self.assertEqual({p.name for p in self.artifacts}, {p.name for p in repeated})
        for artifact in self.artifacts:
            self.assertEqual(artifact.read_bytes(), (second / artifact.name).read_bytes())
        sums = (self.output / "SHA256SUMS").read_text().splitlines()
        self.assertEqual(len(BUILDER.VARIANTS) + 1, len(sums))
        for line in sums:
            digest, filename = line.split("  ", 1)
            self.assertEqual(digest, hashlib.sha256((self.output / filename).read_bytes()).hexdigest())

    def test_extracted_tools_run_without_repository_imports(self):
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        isolated = Path(self.temporary.name).resolve() / "outside-checkout"
        isolated.mkdir()
        for variant in (*BUILDER.VARIANTS, "claude-plugin"):
            with self.subTest(variant=variant), self._archive(variant) as archive:
                extracted = Path(self.temporary.name).resolve() / f"extracted-{variant}"
                archive.extractall(extracted)
                root = extracted / SKILL
                if variant == "claude-plugin":
                    root = root / "skills" / SKILL
                for entrypoint in ("case.py", "evidence_manifest.py"):
                    result = subprocess.run(
                        [sys.executable, str(root / "scripts" / entrypoint), "--help"],
                        cwd=isolated, env=environment, capture_output=True, text=True,
                        encoding="utf-8", timeout=15,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("usage:", result.stdout.lower())

    def test_build_refuses_case_data_in_public_inputs(self):
        copied = Path(self.temporary.name) / "public-input-check"
        shutil.copytree(REPOSITORY, copied, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__", ".venv"))
        assets = copied / "skills" / SKILL / "assets"
        for relative, content in (
            ("case.sqlite3", b"not a real database"),
            ("checkpoint.zip", b"not a real archive"),
            ("case-records.json", b'{"case": {}, "records": {}}'),
            ("renamed-evidence.dat", b"SQLite format 3\x00rest"),
            ("originals/source.txt", b"private investigation material"),
            ("source-ledger.csv", b"source_id,stable_locator\nS001,https://example.com/real-case-record\n"),
        ):
            with self.subTest(relative=relative):
                path = assets / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                previous = path.read_bytes() if path.exists() else None
                path.write_bytes(content)
                try:
                    with self.assertRaisesRegex(ValueError, "must not be bundled"):
                        BUILDER.build(copied, copied / "dist")
                finally:
                    if previous is None:
                        path.unlink()
                    else:
                        path.write_bytes(previous)

    def test_generic_archive_can_create_and_export_a_case(self):
        isolated = Path(self.temporary.name).resolve() / "generic-case-smoke"
        isolated.mkdir()
        with self._archive("agent-skills") as archive:
            archive.extractall(isolated / "installed")
        entrypoint = isolated / "installed" / SKILL / "scripts" / "case.py"
        case = isolated / "synthetic-case"
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)

        def run(*arguments):
            result = subprocess.run(
                [sys.executable, str(entrypoint), *map(str, arguments)],
                cwd=isolated, env=environment, capture_output=True, text=True,
                encoding="utf-8", timeout=15,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            return json.loads(result.stdout)

        self.assertEqual("ready", run("case", "init", case, "--title", "Synthetic package smoke")["status"])
        source = run("source", "add", "--case", case, "--locator", "https://example.com/synthetic", "--origin-group", "fixture")
        original = isolated / "supplied.txt"
        original.write_text("Synthetic evidence supplied for a package test.\n", encoding="utf-8")
        evidence = run("evidence", "add", "--case", case, "--source-id", source["source_id"], "--file", original)
        self.assertEqual(source["source_id"], evidence["source_id"])
        self.assertEqual("exported", run("case", "export", case, "--output", isolated / "export")["status"])
        exported = json.loads((isolated / "export" / "case-records.json").read_text(encoding="utf-8"))
        self.assertEqual(evidence["evidence_id"], exported["records"]["evidence"][0]["evidence_id"])
        self.assertTrue((isolated / "export" / "source-ledger.csv").is_file())


if __name__ == "__main__":
    unittest.main()
