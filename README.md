<p align="center"><img src="skills/investigate-and-fact-check/assets/icon.svg" width="88" alt="Investigation and verification icon"></p>

# Investigate & Fact-Check

**A portable, open-source skill for public-interest investigations, fact-checking, and OSINT.**

[![License: MIT](https://img.shields.io/badge/License-MIT-167d76.svg)](LICENSE)
[![Validation](https://github.com/KhademOHAli1/investigate-and-fact-check/actions/workflows/validate.yml/badge.svg)](https://github.com/KhademOHAli1/investigate-and-fact-check/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/KhademOHAli1/investigate-and-fact-check)](https://github.com/KhademOHAli1/investigate-and-fact-check/releases)

Turn a claim into a traceable assessment: inspect original evidence, test alternative explanations, distinguish independent sources, and explain what remains unknown. Use a focused check for a narrow question or a full evidence register for a substantial investigation.

This repository contains one complete skill, its templates and references, and optional local case tools for persistent records, evidence registration, provenance logs, collection, checkpoints, and reports. Packages are available for Codex, Claude, Mistral, and other Agent Skills clients. The methodology stays the same across platforms; the installation instructions and optional UI metadata differ.

## Install

Download a versioned ZIP from [Releases](https://github.com/KhademOHAli1/investigate-and-fact-check/releases/latest), or clone the repository:

```sh
git clone --branch v1.1.0 https://github.com/KhademOHAli1/investigate-and-fact-check.git
cd investigate-and-fact-check
```

| Platform | Package / installation | Guide |
| --- | --- | --- |
| Codex | Native Agent Skill, including OpenAI UI metadata | [Codex](docs/codex.md) |
| Claude Code | Native Agent Skill or repository plugin | [Claude](docs/claude.md) |
| Claude web / Desktop | Upload the Claude skill ZIP where custom Skills are available | [Claude](docs/claude.md) |
| Mistral Vibe Code | Native Agent Skill | [Mistral](docs/mistral.md) |
| Mistral Vibe Work | Skill editor with supporting files | [Mistral](docs/mistral.md) |
| Gemini CLI, GitHub Copilot, Cursor, OpenCode | Generic `agent-skills` bundle in a documented skills directory | [Other harnesses](docs/agent-harnesses.md) |

For clients supported by the community Skills CLI:

```sh
npx skills add KhademOHAli1/investigate-and-fact-check --skill investigate-and-fact-check
```

The CLI is a separate third-party tool. Inspect its installation plan and choose your client. No API keys or paid services are required by this skill itself. Research capabilities depend on the tools available in your client.

## Try it

In Codex:

```text
Use $investigate-and-fact-check to verify this claim: [exact claim].
Start with the original record, check material counterevidence, and give
a verdict with confidence, citations, and unresolved questions.
```

In Claude Code, invoke `/investigate-and-fact-check` when installed directly, or the namespaced command described in the [Claude guide](docs/claude.md) when installed as a plugin. In other clients, ask to use the skill by name.

More examples:

- “Verify whether these figures show a 20% increase. Check the denominator, period, inflation adjustment, and source table.”
- “Assess the origin, location, and date of this video separately from the caption's allegation.”
- “Review this draft investigation claim by claim. Identify unsupported wording and draft precise right-of-reply questions.”

See the [synthetic worked example](examples/focused-fact-check.md) for a complete, locally reproducible check.

## What is included

- **Four modes:** focused fact-check, media verification, full investigation, and publication review.
- **Reference modules:** investigation method, OSINT playbook, evidence and source security, editorial review, original method sources, and the case-tool and connector guides.
- **Twelve templates:** case brief; claim, source, evidence, search, correction, timeline, entity, and hypothesis logs; media verification; right of reply; and investigation report. An icon asset is also included.
- **Evidence helper:** create and compare local SHA-256 baselines using Python's standard library.
- **Case workspaces:** persistent records and stable IDs, preserved originals, linked sources/evidence/claims, duplicate detection, and cross-record checks.
- **Repeatable work:** structured collection runs, complete case checkpoints, and CSV/JSON/Markdown exports.
- **Optional collection:** certificate-transparency and public GitHub repository adapters, plus a local Recon-ng JSON/CSV importer. Collected rows remain unverified leads.

The skill distinguishes observation, assertion, inference, and unknowns. It treats repeated reporting from one origin as one evidence stream, keeps contrary evidence, and requires authorization for external contact or publication. It does not establish authenticity from a hash or replace accountable editorial and legal judgment. The local case tools use Python 3.10+ and its standard library. Network adapters run only when explicitly invoked.

## Persistent case tools

Keep investigation data in a separate case directory. The commands below work from a repository checkout; an installed skill contains the same `scripts/` directory.

```sh
CASE_TOOL=skills/investigate-and-fact-check/scripts/case.py
python3 "$CASE_TOOL" case init /path/to/my-case --title "Public-interest investigation"
python3 "$CASE_TOOL" source add --case /path/to/my-case \
  --locator https://example.com/original --name "Original record"
python3 "$CASE_TOOL" evidence add --case /path/to/my-case \
  --file /path/to/original.pdf --source-id S001 --method local-file
python3 "$CASE_TOOL" case check /path/to/my-case
python3 "$CASE_TOOL" case report /path/to/my-case --output /path/to/case-report.md
```

Evidence registration copies the original into the case, calculates its hash, and records its source and collection method. Repeated bytes can share stored content while retaining separate observations. Case checks find broken references, missing or changed originals, and other consistency problems. They do not decide whether a claim is true.

See [Case tools](skills/investigate-and-fact-check/references/case-tools.md) for claims, entities, exports, checkpoints, restore, and exit codes. See [Source connectors](skills/investigate-and-fact-check/references/source-connectors.md) for request limits, cache provenance, required inputs, and importing Recon-ng data.

```sh
python3 "$CASE_TOOL" collect list
python3 "$CASE_TOOL" collect run --case /path/to/my-case \
  --adapter certificate-transparency --input example.com
python3 "$CASE_TOOL" recon import --case /path/to/my-case \
  --file /path/to/recon-export.json
```

The importer reads supplied data without installing or running Recon-ng. It preserves the export and records selected domain, host, and repository rows as leads. Missing original provenance stays unknown. Reports retain contrary evidence and unresolved questions; collection success never assigns a supported verdict.

## Evidence manifest

Use Python 3.10 or newer. Keep the manifest outside the evidence directory; the helper refuses existing outputs, symlinks, and special files.

```sh
python3 skills/investigate-and-fact-check/scripts/evidence_manifest.py create \
  --root /path/to/evidence --output /path/to/evidence-manifest.json
python3 skills/investigate-and-fact-check/scripts/evidence_manifest.py verify \
  --root /path/to/evidence --manifest /path/to/evidence-manifest.json
```

Exit codes: `0` for successful creation or a match, `1` for a mismatch, `2` for invalid input or a filesystem error. A matching digest establishes equality with that baseline. Protect the baseline separately and retain a collection log.

## Development and validation

```sh
python3 -m pip install -r requirements-dev.txt
python3 tools/validate.py
python3 -m unittest discover -s tests -v
python3 tools/build_dist.py
```

Release builds produce four self-contained skill ZIPs (Codex, Claude, Mistral Vibe, generic Agent Skills), a Claude plugin ZIP, and `SHA256SUMS`. Build timestamps and ordering are fixed so identical source produces identical archives. [Release process](docs/releasing.md) describes the checks.

Validation covers the case workflow, evidence integrity, connector failure paths, and execution from each extracted package. A native Codex CLI run registered synthetic evidence and produced a case report. Claude, Mistral, and the other documented harnesses were checked at the package and installation-guide level. See [compatibility and validation](docs/compatibility.md).

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md). Reproducible bug reports, improvements to source handling, and carefully scoped platform fixes are welcome. Keep real evidence and confidential source material out of issues and pull requests. Report security issues using [SECURITY.md](SECURITY.md).

## License and attribution

[MIT](LICENSE), copyright 2026 Ali ([KhademOHAli1](https://github.com/KhademOHAli1)). The original skill was supplied by the maintainer and adapted for this public release. [Method sources](skills/investigate-and-fact-check/references/method-sources.md) credits the external guidance behind the editorial synthesis. The workspace and modular-collection design was informed by studying [Recon-ng](https://github.com/lanmaster53/recon-ng); the case tools are an original implementation and contain no vendored Recon-ng code. Linked publications, trademarks, and third-party tools retain their own rights. This is an independent community project.
