# Codex

The canonical folder is a native Agent Skill. It includes `agents/openai.yaml` for its title, icon, default prompt, and automatic invocation policy.

## Install through Codex

Ask the built-in installer:

```text
$skill-installer install https://github.com/KhademOHAli1/investigate-and-fact-check/tree/v1.0.0/skills/investigate-and-fact-check
```

Restart Codex if the new skill does not appear in its skill picker.

## Manual installation

From a checked-out release, copy the entire skill into a user-level skills directory:

```sh
mkdir -p ~/.agents/skills
test ! -e ~/.agents/skills/investigate-and-fact-check && \
  cp -R skills/investigate-and-fact-check ~/.agents/skills/investigate-and-fact-check
```

For a shared project installation, use `.agents/skills/investigate-and-fact-check/` within that project. Older Codex installations may use `~/.codex/skills`; follow the paths documented by the version you use. The commands above refuse an existing destination so an installed revision is not silently replaced.

## Invoke

```text
Use $investigate-and-fact-check to verify this claim: [claim].
Give the exact proposition, verdict, confidence with reasons,
decisive evidence, counterevidence, and remaining uncertainty.
```

The skill can also activate when a request matches its description. It declares no additional tool dependencies or pre-approved tool access. Current research requires browsing or other sources supplied by the user; without access, the assessment must state the gap.

## Sources and test status

See OpenAI's [skill catalog and installation example](https://github.com/openai/skills) and [Build skills](https://learn.chatgpt.com/docs/build-skills). Documentation reviewed on 12 November 2026. Local metadata and script tests do not establish installation acceptance in every Codex surface.
