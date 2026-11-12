"""Observable integrity and input-boundary checks for the optional local helper."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "skills" /
          "investigate-and-fact-check" / "scripts" / "evidence_manifest.py")


class EvidenceManifestTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        # Resolve OS temporary-directory aliases; the helper rejects symlink parents.
        self.case = Path(self.temporary.name).resolve()
        self.root = self.case / "originals"
        self.root.mkdir()
        (self.root / "a.txt").write_bytes(b"Original evidence\n")
        (self.root / "nested").mkdir()
        (self.root / "nested" / "caf\u00e9.txt").write_bytes(b"nested\n")
        self.manifest = self.case / "manifest.json"

    def invoke(self, expected, *arguments):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        payload = json.loads(result.stdout if result.stdout else result.stderr)
        return payload

    def create(self):
        return self.invoke(0, "create", "--root", self.root,
                           "--output", self.manifest)

    def verify(self, expected=0, manifest=None, root=None):
        return self.invoke(expected, "verify", "--root", root or self.root,
                           "--manifest", manifest or self.manifest)

    def write_bad_manifest(self, payload):
        bad = self.case / "invalid.json"
        bad.write_text(json.dumps(payload), encoding="utf-8")
        return bad

    def make_symlink(self, path, target, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlinks unavailable or not permitted: {error}")

    def test_create_and_verify_preserves_originals(self):
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.create()["files"], 2)
        result = self.verify()
        self.assertEqual(result["status"], "match")
        self.assertEqual(result["files_expected"], 2)
        self.assertEqual(result["files_present"], 2)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_refuses_existing_manifest_without_changing_it(self):
        self.create()
        before = self.manifest.read_bytes()
        self.invoke(2, "create", "--root", self.root,
                    "--output", self.manifest)
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_refuses_manifest_inside_evidence_root(self):
        output = self.root / "manifest.json"
        self.invoke(2, "create", "--root", self.root, "--output", output)
        self.assertFalse(output.exists())

    def test_detects_modified_bytes_of_the_same_length(self):
        self.create()
        (self.root / "a.txt").write_bytes(b"Altered! evidence\n")
        self.assertEqual(len(b"Altered! evidence\n"), len(b"Original evidence\n"))
        self.assertEqual(self.verify(1)["modified"], ["a.txt"])

    def test_detects_added_and_missing_files(self):
        self.create()
        (self.root / "b.txt").write_bytes(b"new\n")
        (self.root / "nested" / "caf\u00e9.txt").unlink()
        result = self.verify(1)
        self.assertEqual(result["added"], ["b.txt"])
        self.assertEqual(result["missing"], ["nested/caf\u00e9.txt"])
        self.assertEqual(result["modified"], [])

    def test_refuses_evidence_symlink(self):
        self.create()
        self.make_symlink(self.root / "linked", self.manifest)
        self.verify(2)

    def test_refuses_manifest_symlink(self):
        self.create()
        link = self.case / "manifest-link"
        self.make_symlink(link, self.manifest)
        self.verify(2, manifest=link)

    def test_refuses_evidence_root_symlink(self):
        self.create()
        link = self.case / "root-link"
        self.make_symlink(link, self.root, directory=True)
        self.verify(2, root=link)

    def test_refuses_unsafe_manifest_paths(self):
        self.create()
        for name in ("../outside", "/absolute", "nested/../a.txt",
                     "nested\\a.txt", "./a.txt", "x//a.txt", "C:/a.txt"):
            with self.subTest(path=name):
                payload = json.loads(self.manifest.read_text(encoding="utf-8"))
                payload["files"][0]["path"] = name
                self.verify(2, manifest=self.write_bad_manifest(payload))

    def test_refuses_duplicate_json_keys(self):
        bad = self.case / "duplicate-keys.json"
        bad.write_text('{"schema_version":1,"schema_version":1}',
                       encoding="utf-8")
        self.verify(2, manifest=bad)

    def test_refuses_duplicate_manifest_paths(self):
        self.create()
        payload = json.loads(self.manifest.read_text(encoding="utf-8"))
        payload["files"].append(payload["files"][0])
        self.verify(2, manifest=self.write_bad_manifest(payload))

    def test_refuses_empty_evidence_directory(self):
        empty = self.case / "empty"
        empty.mkdir()
        self.invoke(2, "create", "--root", empty,
                    "--output", self.case / "empty.json")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes unavailable")
    def test_refuses_special_files(self):
        self.create()
        try:
            os.mkfifo(self.root / "fifo")
        except OSError as error:
            self.skipTest(f"Named pipe creation unavailable: {error}")
        self.verify(2)


if __name__ == "__main__":
    unittest.main()
