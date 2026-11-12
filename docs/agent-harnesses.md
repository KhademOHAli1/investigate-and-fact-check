# Other Agent Skills harnesses

The `investigate-and-fact-check-agent-skills-v1.1.0.zip` release is a vendor-neutral Agent Skills bundle. Extract it and keep the entire `investigate-and-fact-check/` folder together. It contains `SKILL.md`, references, templates, and the optional Python case tools. OpenAI-specific UI metadata is omitted.

The same directory can be installed in a client that implements the [Agent Skills format](https://agentskills.io/specification). A native skill install does not supply browsing, shell access, Python, or permission to publish. The client controls those capabilities.

## Shared project installation

Gemini CLI, GitHub Copilot, Cursor, and OpenCode currently document `.agents/skills/` as a project discovery location. From the directory where the ZIP was extracted, copy into the intended project:

```sh
mkdir -p /path/to/project/.agents/skills
test ! -e /path/to/project/.agents/skills/investigate-and-fact-check && \
  cp -R investigate-and-fact-check /path/to/project/.agents/skills/investigate-and-fact-check
```

The guard preserves an existing installation. For an update, review and replace the old skill folder so removed files do not linger. A cloned repository uses `skills/investigate-and-fact-check` as the copy source.

On Windows, extract the ZIP with Explorer and copy the folder into the project's `.agents\skills\` directory, or use PowerShell:

```powershell
$skillDestination = 'C:\path\to\project\.agents\skills\investigate-and-fact-check'
if (Test-Path $skillDestination) { throw 'An installation already exists at this destination.' }
New-Item -ItemType Directory -Force (Split-Path $skillDestination) | Out-Null
Copy-Item -Recurse .\investigate-and-fact-check $skillDestination
```

## Client-specific locations

Each location below contains an `investigate-and-fact-check/` subdirectory. Choose one location per scope to avoid duplicate entries.

| Client | Native project location | Native personal location | Shared alias |
| --- | --- | --- | --- |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` | `.agents/skills/` and `~/.agents/skills/` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` | `.agents/skills/` and `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` | `.agents/skills/` and `~/.agents/skills/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` | `.agents/skills/` and `~/.agents/skills/` |

Gemini CLI lists discovered skills with `/skills list` and may ask for activation consent. Its `.agents/skills/` alias takes precedence within the same scope. [Gemini CLI discovery and activation](https://geminicli.com/docs/cli/skills/).

Copilot's available locations vary by surface. A repository skill is the suitable starting point for cloud agents; a personal local installation does not automatically become available in a cloud sandbox. [GitHub Copilot skill locations and surfaces](https://docs.github.com/en/copilot/concepts/customizations/agent-skills).

Cursor discovers project skills at startup and provides a `/` skill picker. Local user skills require the documented sync route for cloud use; project skills can travel with the repository. [Cursor skill discovery](https://cursor.com/docs/skills).

OpenCode discovers directory skills under its project and global sources, including the shared aliases. Ask it to use `investigate-and-fact-check`; its skill tool loads the instructions when relevant. [OpenCode discovery and loading](https://opencode.ai/docs/skills/).

## Run the bundled tools

When Python 3.10+ and local command execution are available, run the helper by its installed path. For a shared project installation:

```sh
python3 .agents/skills/investigate-and-fact-check/scripts/case.py --help
python3 .agents/skills/investigate-and-fact-check/scripts/evidence_manifest.py --help
```

On Windows use the equivalent `python` command. The case tool's local operations use only Python's standard library. Network connectors are explicit optional commands. Keep generated case folders outside the installed reusable skill.

Try a supplied numeric claim first and check that the agent cites the supplied evidence and states any unavailable checks. See the [worked example](../examples/focused-fact-check.md) and [case-tool reference](../skills/investigate-and-fact-check/references/case-tools.md).

## Validation scope

The installation paths above were checked against official documentation on 12 November 2026. This release tests portable structure and runs the tools from extracted archives outside the repository. Gemini CLI, Copilot, Cursor, and OpenCode activation and model behavior have not been exercised in those clients. Consult [compatibility and validation](compatibility.md) for the current evidence.
