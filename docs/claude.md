# Claude installation

The Claude edition uses the same investigation method, references, templates, and Python helper as the canonical skill. Its `SKILL.md` uses standard Agent Skills frontmatter. No Claude-specific tool allow-list or automatic shell command is required. [Claude's skill format documentation](https://code.claude.com/docs/en/skills).

## Claude Code: install the skill

From the repository root, for a first-time personal installation:

```sh
mkdir -p ~/.claude/skills
test ! -e ~/.claude/skills/investigate-and-fact-check && \
  cp -R skills/investigate-and-fact-check ~/.claude/skills/investigate-and-fact-check
```

For a shared project, use `.claude/skills/` instead. Start Claude Code in the intended project and invoke:

```text
/investigate-and-fact-check Check this claim against its original source: …
```

Personal and project installations are documented by [Claude Code](https://code.claude.com/docs/en/skills). When updating an existing installation, replace the previous skill folder so removed files do not linger.

## Claude Code: install the plugin

This repository also provides a Claude Code plugin and a small self-hosted marketplace. In Claude Code:

```text
/plugin marketplace add KhademOHAli1/investigate-and-fact-check
/plugin install investigate-and-fact-check@investigation-skills
```

The plugin's command includes its namespace:

```text
/investigate-and-fact-check:investigate-and-fact-check Check this claim: …
```

Choose either the personal skill installation or the plugin to avoid duplicate entries. The marketplace is maintained by this project; availability through it does not imply an Anthropic directory listing or endorsement. [Marketplace installation and command names](https://code.claude.com/docs/en/plugin-marketplaces).

For local development, `claude --plugin-dir .` loads the repository as a plugin. Its manifest is `.claude-plugin/plugin.json`; the skill stays under `skills/`, outside that metadata folder. Validate from the repository root with `claude plugin validate .`. [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference).

## Claude chat and Desktop

Use the Claude release ZIP. It contains one `investigate-and-fact-check/` folder, with `SKILL.md` and the supporting files inside. In an account where custom Skills are available, enable code execution and add the ZIP under **Customize > Skills**. Enable it, start a new task, and ask Claude to use Investigate and Fact Check. Check account and workspace availability in [Claude's custom-skill instructions](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

## Claude API

Upload the complete skill folder or ZIP through the Skills API. The returned skill ID is supplied as a custom skill in the Messages API's `container`, with code execution enabled. Use the current [API guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide) for the SDK-specific request, supported models, and version pinning.

The skill does not supply browsing. API code-execution containers have no internet access; live checks require a separately available search/fetch tool or supplied originals. Install/upload separately where required, rather than assuming every Claude surface shares an installation. [Runtime and cross-surface constraints](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## Validation scope

Platform instructions were checked against official documentation on 2026-11-12. Packaging checks establish file structure; they do not establish model accuracy, source access, or editorial readiness. See the release notes for checks actually executed. A useful first check is a supplied numeric claim where the expected result can be recomputed, followed by a claim with inaccessible evidence that should remain unresolved.
