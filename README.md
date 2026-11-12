<p align="center"><img src="skills/investigate-and-fact-check/assets/icon.svg" width="88" alt="Investigation and verification icon"></p>

# Investigate & Fact-Check

**A portable, open-source skill for public-interest investigations, fact-checking, and OSINT.**

[![License: MIT](https://img.shields.io/badge/License-MIT-167d76.svg)](LICENSE)
[![Validation](https://github.com/KhademOHAli1/investigate-and-fact-check/actions/workflows/validate.yml/badge.svg)](https://github.com/KhademOHAli1/investigate-and-fact-check/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/KhademOHAli1/investigate-and-fact-check)](https://github.com/KhademOHAli1/investigate-and-fact-check/releases)

Turn a claim into a traceable assessment: inspect original evidence, test alternative explanations, distinguish independent sources, and explain what remains unknown. Use a focused check for a narrow question or a full evidence register for a substantial investigation.

This repository contains one complete skill, its templates and references, a local evidence-manifest helper, and distribution packages for Codex, Claude, and Mistral. The methodology stays the same across platforms; the installation instructions and optional UI metadata differ.

## Install

Download a versioned ZIP from [Releases](https://github.com/KhademOHAli1/investigate-and-fact-check/releases/latest), or clone the repository:

```sh
git clone --branch v1.0.1 https://github.com/KhademOHAli1/investigate-and-fact-check.git
cd investigate-and-fact-check
```

| Platform | Package / installation | Guide |
| --- | --- | --- |
| Codex | Native Agent Skill, including OpenAI UI metadata | [Codex](docs/codex.md) |
| Claude Code | Native Agent Skill or repository plugin | [Claude](docs/claude.md) |
| Claude web / Desktop | Upload the Claude skill ZIP where custom Skills are available | [Claude](docs/claude.md) |
| Mistral Vibe Code | Native Agent Skill | [Mistral](docs/mistral.md) |
| Mistral Vibe Work | Skill editor with supporting files | [Mistral](docs/mistral.md) |

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
- **Five reference modules:** investigation method, OSINT playbook, evidence and source security, editorial review, and original method sources.
- **Twelve templates:** case brief; claim, source, evidence, search, correction, timeline, entity, and hypothesis logs; media verification; right of reply; and investigation report. An icon asset is also included.
- **Evidence helper:** create and compare local SHA-256 baselines using Python's standard library.

The skill distinguishes observation, assertion, inference, and unknowns. It treats repeated reporting from one origin as one evidence stream, keeps contrary evidence, and requires authorization for external contact or publication. It does not grant browsing tools, establish authenticity from a hash, or replace accountable editorial and legal judgment.

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

Release builds produce three self-contained skill ZIPs, a Claude plugin ZIP, and `SHA256SUMS`. Build timestamps and ordering are fixed so identical source produces identical archives. [Release process](docs/releasing.md) describes the checks.

Validation covers file structure, local links, metadata, packaging, and the evidence helper's behavior. Platform documentation was checked on 12 November 2026. A native Codex CLI invocation was exercised with synthetic evidence. Claude and Mistral runtime activation remain untested; see [compatibility and validation](docs/compatibility.md).

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md). Reproducible bug reports, improvements to source handling, and carefully scoped platform fixes are welcome. Keep real evidence and confidential source material out of issues and pull requests. Report security issues using [SECURITY.md](SECURITY.md).

## License and attribution

[MIT](LICENSE), copyright 2026 Ali ([KhademOHAli1](https://github.com/KhademOHAli1)). The original skill was supplied by the maintainer and adapted for this public release. [Method sources](skills/investigate-and-fact-check/references/method-sources.md) credits the external guidance behind the editorial synthesis. Linked publications, trademarks, and third-party tools retain their own rights. This is an independent community project.
