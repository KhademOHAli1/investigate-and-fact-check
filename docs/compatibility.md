# Compatibility and validation

The portable unit is `skills/investigate-and-fact-check/`. It uses the [Agent Skills format](https://agentskills.io/specification): YAML frontmatter, Markdown instructions, and relative references. It includes optional Python case-management and collection helpers; its investigation instructions remain usable without running them.

| Surface | Distribution | Validation scope |
| --- | --- | --- |
| Codex | Native folder with OpenAI metadata | Project-skill activation and case-tool workflow exercised in Codex CLI with synthetic local evidence |
| Claude Code | Native folder or plugin | Packaging checked against official documentation; client installation not yet exercised |
| Claude custom Skills | Claude ZIP with one top-level skill folder | ZIP structure checked; account-dependent upload not yet exercised |
| Mistral Vibe Code | Native skill folder | Layout checked against official documentation; runtime activation not yet exercised |
| Mistral Vibe Work | Skill editor and support files | Documented manual workflow; account UI import not yet exercised |
| Gemini CLI | Generic Agent Skills folder | Official discovery paths checked; client activation and model behavior not yet exercised |
| GitHub Copilot | Generic Agent Skills folder | Official project/personal locations checked; client activation and model behavior not yet exercised |
| Cursor | Generic Agent Skills folder | Official discovery paths checked; client activation and model behavior not yet exercised |
| OpenCode | Generic Agent Skills folder | Official discovery paths checked; client activation and model behavior not yet exercised |

The bundled helpers need Python 3.10+ and have no third-party runtime dependencies. The development validator uses PyYAML. Scripts may be unavailable in some hosted clients, and web access depends on the host and its configured tools. Optional collectors use network access only when explicitly invoked. A portable ZIP does not establish that a hosted client exposes Python or persists a case directory.

Local tests cover unchanged/modified/added/missing files, refusal to overwrite manifests, path traversal and malformed manifests, duplicate JSON fields, symlinks and special files, and release archive contents. A synthetic worked example demonstrates reasoning and citations to local supplied evidence. None of these checks proves the accuracy of a future investigation or certifies every platform.

Platform documentation was reviewed on 12 November 2026. Consult the linked official documentation in each installation guide when interfaces change.

## Portable release checks

The build produces four native skill bundles (Codex, Claude, Mistral Vibe, and generic Agent Skills) plus a Claude Code plugin. Every bundle contains the complete shared case-tool package. Packaging tests extract each archive into an isolated directory, clear repository-specific Python imports, and run both `case.py --help` and `evidence_manifest.py --help` from outside the checkout. A synthetic case is also created, supplied with source and evidence records, and exported using the extracted generic bundle. These checks establish import, bundled-resource, and CLI portability, not activation in every client.

The builder rejects recognizable case directories, SQLite databases, checkpoint ZIPs, and filled reusable CSV templates from its public input directories. Cases belong outside the installed skill and repository. See [other agent harnesses](agent-harnesses.md) for the generic bundle's documented install paths.

## Version 1.1.0 runtime checks

A local Codex CLI session loaded the 1.1.0 skill from `.agents/skills/`. It registered three synthetic source documents, distinguished a contract ceiling from the EUR 120,000 actually recorded as paid through the ledger cutoff, and generated a scoped claim and Markdown report. The resulting case passed `case check` with zero errors and zero warnings.

Anonymous collection through the case CLI recorded eight public GitHub repository observations for `octocat`. A `crt.sh` check for `example.org` received HTTP 502 followed by HTTP 200, retained both responses, and recorded 109 host observations. It marked the run partial because two entries were filtered. The resulting case passed its integrity check. These bounded checks reflect provider behavior on 12 November 2026.

## Initial release evidence

On 12 November 2026, a local Codex CLI task loaded the skill from a project `.agents/skills/investigate-and-fact-check/` directory. Its prompt asked about entities, amounts, and dates that differed from the supplied synthetic records. The result identified that mismatch, declined to transfer the records to the unrelated claim, recomputed the actual ledger total, and left ownership and motive unsubstantiated. It ignored the instruction embedded in a fixture and reported that no subject contact occurred. No browser, external contact, or publication action was authorized in that test.

This is one bounded native skill-use check, alongside 17 automated tests. It is not a multi-model benchmark. Claude and Mistral installation and runtime activation remain untested.

The 1.0.1 source also passed all six GitHub Actions jobs across Linux, macOS, and Windows with Python 3.10 and 3.13. The public-repository install command was exercised with Skills CLI 1.8.1 in an isolated project and installed exactly one skill for Codex.
