#!/usr/bin/env python3
"""Validate portable metadata, release consistency, and local resource links."""

import csv
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/investigate-and-fact-check"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    version = (ROOT / "VERSION").read_text().strip()
    require(re.fullmatch(r"\d+\.\d+\.\d+", version), "Invalid VERSION")
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    require(text.startswith("---\n"), "Missing frontmatter")
    metadata = yaml.safe_load(text.split("---", 2)[1])
    name = metadata.get("name", "")
    require(name == SKILL.name and len(name) <= 64 and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), "Invalid skill name")
    require(isinstance(metadata.get("description"), str) and 1 <= len(metadata["description"]) <= 1024, "Invalid description")
    if "compatibility" in metadata:
        require(isinstance(metadata["compatibility"], str) and 1 <= len(metadata["compatibility"]) <= 500, "Invalid compatibility")
    require(metadata.get("license") == "MIT", "Missing MIT license metadata")
    require(isinstance(metadata.get("metadata"), dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in metadata["metadata"].items()), "Metadata must map strings to strings")
    require(metadata["metadata"].get("version") == version, "Skill version differs from VERSION")
    require((SKILL / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes(), "Bundled license differs")
    interface = yaml.safe_load((SKILL / "agents/openai.yaml").read_text())["interface"]
    require(25 <= len(interface["short_description"]) <= 64, "Invalid OpenAI short description")
    require(f"${name}" in interface["default_prompt"], "OpenAI default prompt must name the skill")
    for field in ("icon_small", "icon_large"):
        require((SKILL / interface[field]).is_file(), f"Missing {field}")
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    require(plugin["name"] == name and plugin["version"] == version, "Claude plugin metadata differs")
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    require(any(p["name"] == name for p in marketplace["plugins"]), "Marketplace does not declare plugin")
    for relative in ("scripts/case.py", "scripts/casekit/__init__.py", "scripts/casekit/store.py", "scripts/casekit/connectors.py"):
        require((SKILL / relative).is_file(), f"Missing bundled case-tool component: {relative}")
    for path in sorted((SKILL / "scripts").rglob("*.py")):
        compile(path.read_text(encoding="utf-8"), str(path.relative_to(SKILL)), "exec")

    links = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in {".git", "dist", ".venv"} for part in path.parts):
            continue
        body = path.read_text(encoding="utf-8")
        for raw in re.findall(r"\]\(([^)\s]+)(?:\s+[^)]*)?\)", body):
            target = urlsplit(raw)
            if target.scheme or not target.path:
                continue
            resolved = (path.parent / unquote(target.path)).resolve()
            require(resolved.is_relative_to(ROOT), f"Link escapes repository in {path.relative_to(ROOT)}: {raw}")
            require(resolved.exists(), f"Broken link in {path.relative_to(ROOT)}: {raw}")
            links += 1
    templates = list((SKILL / "assets").glob("*.csv"))
    for path in templates:
        with path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream))
        require(rows and len(rows[0]) == len(set(rows[0])) and all(rows[0]), f"Invalid CSV header: {path.name}")
        require(all(not any(row) or len(row) == len(rows[0]) for row in rows[1:]), f"Inconsistent CSV columns: {path.name}")
        require(not any(any(value.strip() for value in row) for row in rows[1:]), f"Reusable CSV template contains case records: {path.name}")
    print(f"Validated {name} v{version}: metadata, {links} local links, {len(templates)} CSV templates, and licenses.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, SyntaxError, yaml.YAMLError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        sys.exit(1)
