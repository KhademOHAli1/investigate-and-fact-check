# Changelog

## 1.1.0 - 2026-11-12

- Add optional persistent case workspaces with stable IDs, preserved originals, linked claim/source/evidence records, and cross-record validation.
- Record collection runs and duplicate observations without treating repeated sources as independent corroboration.
- Add complete case checkpoints, safe restoration into a new directory, and generated Markdown/JSON/CSV outputs.
- Add explicitly invoked certificate-transparency and public GitHub repository adapters, including bounded requests and labeled cache provenance.
- Import selected Recon-ng JSON/CSV exports as unverified leads without installing Recon-ng.
- Add a generic Agent Skills package and installation documentation for Gemini CLI, GitHub Copilot, Cursor, and OpenCode.
- Keep runtime helpers dependency-free, with original MIT-licensed code and the existing standalone manifest helper retained.

## 1.0.1 - 2026-11-12

- Keep Git checkouts on LF line endings across platforms for consistent release inputs.
- Accept standard line-ending variants in packaging metadata checks after Windows CI exposed an overly strict assertion.
- The investigation workflow and evidence helper are unchanged from 1.0.0.

## 1.0.0 - 2026-11-12

- Initial public release of the investigation, fact-checking, media verification, and publication review workflow.
- Supporting references, reusable case templates, and Python evidence-manifest helper.
- Native skill packages and installation documentation for Codex, Claude, and Mistral Vibe.
- MIT license, Claude plugin metadata, reproducible release packaging, and continuous validation.
- Clarified the method-source list's provenance and removed unsupported product declarations from OpenAI metadata.
