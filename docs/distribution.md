# Distribution and directory submissions

Canonical source: [KhademOHAli1/investigate-and-fact-check](https://github.com/KhademOHAli1/investigate-and-fact-check).

This page records public submission outcomes. A submission or pull request is not an accepted listing, security audit, or platform endorsement.

| Destination | Route | Status |
| --- | --- | --- |
| GitHub | Public repository and [releases](https://github.com/KhademOHAli1/investigate-and-fact-check/releases) | Published under MIT |
| Agent Skill Exchange | [Submission PR #157](https://github.com/agentskillexchange/skills/pull/157) | Submitted; awaiting maintainer review |
| The Skills Directory | [Submission PR #16](https://github.com/theskillsdirectory/skills/pull/16) | Submitted; awaiting maintainer review |
| Claude Skills Registry | [Source-intake issue #446](https://github.com/majiayu000/claude-skill-registry-core/issues/446) | Submitted; awaiting maintainer review |
| AgentSkill.sh | [Repository import](https://agentskill.sh/submit) | Repository scan found the skill but failed to import; direct-file fallback returned Server Error |
| OmniSkill | [Repository import](https://omniskill.online/) | Attempted; the service returned a network / malformed JSON error |
| skills.sh | [Installation-based discovery](https://skills.sh/docs/faq) | Skills CLI 1.8.1 successfully installed the public repository in an isolated project; public listing not confirmed |
| AwesomeSkills | [Submit form](https://www.awesomeskills.dev/en/submit) | Not submitted; the form's Turnstile challenge prevented submission |

Directory requirements were reviewed on 12 November 2026. Curated lists that require established community usage, minimum stars, or an older repository are deferred until the project meets those conditions.

The two contribution PRs package the valid initial 1.0.0 skill. Version 1.0.1 fixes repository line-ending handling and a Windows packaging-test assertion; it does not change the investigation workflow or evidence helper. The registry intake includes its scanner result: one skill passed with a catalog-description-length warning. This is a registry-specific schema preference, not a claim of platform certification. No signup, paid placement, or email outreach was performed.
