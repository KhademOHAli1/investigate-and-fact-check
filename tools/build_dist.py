#!/usr/bin/env python3
"""Build reproducible, self-contained skill and Claude plugin archives."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import stat
import zipfile


SKILL_NAME = "investigate-and-fact-check"
ARCHIVE_TIME = (2020, 1, 1, 0, 0, 0)
VARIANTS = ("codex", "claude", "mistral-vibe")


def _public_files(directory: Path) -> list[Path]:
    """Select regular public files, refusing links and special filesystem entries."""
    result = []
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ValueError(f"Refusing symlink in release input: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Refusing non-regular release input: {path}")
        result.append(path)
    return result


def _write_zip(destination: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=ARCHIVE_TIME)
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(repository: Path, output_dir: Path) -> list[Path]:
    """Build all release files, using VERSION and LICENSE from repository."""
    repository = repository.resolve()
    version = (repository / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        raise ValueError("VERSION must be a semantic version such as 1.0.0")
    license_bytes = (repository / "LICENSE").read_bytes()
    skill_dir = repository / "skills" / SKILL_NAME
    if not (skill_dir / "SKILL.md").is_file():
        raise ValueError(f"Missing skill entrypoint: {skill_dir / 'SKILL.md'}")
    skill_files = {
        path.relative_to(skill_dir).as_posix(): path.read_bytes()
        for path in _public_files(skill_dir)
    }
    # The repository license is authoritative even if a bundled copy is stale.
    skill_files["LICENSE"] = license_bytes
    output_dir.mkdir(parents=True, exist_ok=True)
    built = []
    for variant in VARIANTS:
        files = {
            f"{SKILL_NAME}/{name}": content
            for name, content in skill_files.items()
            if variant == "codex" or not name.startswith("agents/")
        }
        destination = output_dir / f"{SKILL_NAME}-{variant}-v{version}.zip"
        _write_zip(destination, files)
        built.append(destination)

    plugin_files = {
        f"{SKILL_NAME}/skills/{SKILL_NAME}/{name}": content
        for name, content in skill_files.items()
        if not name.startswith("agents/")
    }
    for name in ("README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", "VERSION"):
        plugin_files[f"{SKILL_NAME}/{name}"] = (repository / name).read_bytes()
    for directory in ("docs", "examples", "adapters"):
        base = repository / directory
        if base.exists():
            for path in _public_files(base):
                plugin_files[f"{SKILL_NAME}/{path.relative_to(repository).as_posix()}"] = path.read_bytes()
    manifest = repository / ".claude-plugin" / "plugin.json"
    if not manifest.is_file() or manifest.is_symlink():
        raise ValueError("Claude plugin manifest must be a regular .claude-plugin/plugin.json file")
    plugin_files[f"{SKILL_NAME}/.claude-plugin/plugin.json"] = manifest.read_bytes()
    plugin_destination = output_dir / f"{SKILL_NAME}-claude-plugin-v{version}.zip"
    _write_zip(plugin_destination, plugin_files)
    built.append(plugin_destination)

    sums = output_dir / "SHA256SUMS"
    sums.write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in sorted(built)),
        encoding="utf-8",
    )
    return [*built, sums]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    repository = Path(__file__).resolve().parents[1]
    parser.add_argument("--output", type=Path, default=repository / "dist", help="Output directory (default: dist/)")
    arguments = parser.parse_args()
    try:
        for path in build(repository, arguments.output):
            print(path)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Build failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
