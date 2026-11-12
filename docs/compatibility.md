# Compatibility and validation

The portable unit is `skills/investigate-and-fact-check/`. It uses the [Agent Skills format](https://agentskills.io/specification): YAML frontmatter, Markdown instructions, and relative references. It does not require a particular model or install a research tool.

| Surface | Distribution | Validation scope |
| --- | --- | --- |
| Codex | Native folder with OpenAI metadata | Native project-skill invocation exercised in Codex CLI with synthetic local evidence; metadata, links, and helper checked locally |
| Claude Code | Native folder or plugin | Packaging checked against official documentation; client installation not yet exercised |
| Claude custom Skills | Claude ZIP with one top-level skill folder | ZIP structure checked; account-dependent upload not yet exercised |
| Mistral Vibe Code | Native skill folder | Layout checked against official documentation; runtime activation not yet exercised |
| Mistral Vibe Work | Skill editor and support files | Documented manual workflow; account UI import not yet exercised |

The helper needs Python 3.10+. It has no third-party runtime dependencies. The development validator uses PyYAML. Scripts may be unavailable in some hosted clients, and web access depends on the host and its configured tools.

Local tests cover unchanged/modified/added/missing files, refusal to overwrite manifests, path traversal and malformed manifests, duplicate JSON fields, symlinks and special files, and release archive contents. A synthetic worked example demonstrates reasoning and citations to local supplied evidence. None of these checks proves the accuracy of a future investigation or certifies every platform.

Platform documentation was reviewed on 12 November 2026. Consult the linked official documentation in each installation guide when interfaces change.

## Initial release evidence

On 12 November 2026, a local Codex CLI task loaded the skill from a project `.agents/skills/investigate-and-fact-check/` directory. Its prompt asked about entities, amounts, and dates that differed from the supplied synthetic records. The result identified that mismatch, declined to transfer the records to the unrelated claim, recomputed the actual ledger total, and left ownership and motive unsubstantiated. It ignored the instruction embedded in a fixture and reported that no subject contact occurred. No browser, external contact, or publication action was authorized in that test.

This is one bounded native skill-use check, alongside 17 automated tests. It is not a multi-model benchmark. Claude and Mistral installation and runtime activation remain untested.
