# Mistral installation

The Mistral Vibe edition is a native Agent Skills bundle. It retains the investigation instructions, references, templates, and evidence helper. Mistral documents native support in both [Vibe Code](https://docs.mistral.ai/vibe/code/cli/skills) and [Vibe Work](https://docs.mistral.ai/vibe/work/skills).

## Vibe Code

From the repository root, for a first-time personal installation:

```sh
mkdir -p ~/.vibe/skills
test ! -e ~/.vibe/skills/investigate-and-fact-check && \
  cp -R skills/investigate-and-fact-check ~/.vibe/skills/investigate-and-fact-check
```

For a shared project, place the folder under `.vibe/skills/` in a trusted project. Mistral also supports `.agents/skills/`. If the skill does not appear in an active session, run `/reload`. Invoke it with:

```text
/investigate-and-fact-check Verify this statement using its original context: …
```

Use a single installation location to avoid duplicates. When updating, replace the previous skill folder. Vibe's `allowed-tools` metadata is not a permission boundary; available tools and permissions belong to the active agent. [Discovery, invocation, and permission behavior](https://docs.mistral.ai/vibe/code/cli/skills).

## Vibe Work

With a Mistral account that has Work access:

1. Open the Work tab at [Mistral](https://chat.mistral.ai), then **Context > Skills > New Skill**.
2. Set the title to **Investigate and Fact Check**, use the description from `SKILL.md`, and paste the skill instructions into the `SKILL.md` field.
3. Attach the `references/`, `assets/`, and `scripts/` directories while preserving their relative paths. The links in the instructions depend on those paths.
4. Create and enable the skill. In a new task, invoke `/investigate-and-fact-check` if that is the name shown in the picker, or ask Work to use **Investigate and Fact Check**.

The editor can attach files and folders. Confirm that every supporting file is present; account or workspace limits may apply. A ZIP release is a portable bundle, not a claim that Work provides ZIP import. [Work skill editor and supporting resources](https://docs.mistral.ai/vibe/work/skills), [first-skill quickstart](https://docs.mistral.ai/getting-started/quickstarts/vibe-work/create-first-skill).

## Le Chat or a plain Mistral chat/API client

If your interface does not expose native Skills, use [the standalone chat prompt](../adapters/mistral-chat-prompt.md) in an instruction field or the first message. This fallback is a compact prompt adapter. It does not install a skill, load the reference library on demand, create tools, or execute the Python helper. Attach the relevant originals yourself and enable available research tools where appropriate.

The current Mistral documentation labels its previous Chat surface as legacy and describes Work and Code as separate surfaces. Follow the native route above when it is available. [Mistral Work skill documentation](https://docs.mistral.ai/vibe/work/skills).

## Validation scope

Platform instructions were checked against official documentation on 2026-11-12. Documented format compatibility and a successful ZIP build do not prove runtime activation or answer quality. See release notes for executed checks. Test activation, reference loading, citations to inspected originals, and an unresolved-evidence case in your installed client before relying on it for publication work.
