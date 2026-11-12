# Contributing

Open an issue for a substantive methodology change before investing in a large rewrite. Small corrections and narrowly scoped fixes can go straight to a pull request.

1. Edit the canonical skill in `skills/investigate-and-fact-check/`. Keep platform instructions in `docs/`.
2. Explain the concrete scenario and the resulting improvement. For factual guidance, cite an inspected original source and its date or version.
3. Add a behavioral test when changing the Python helper or release packaging. Use synthetic fixtures; do not add real investigations, credentials, or personal information.
4. Run the validation commands in the README. Describe what was tested and what remains untested.

Keep the skill portable. Avoid vendor-specific tool names in the shared workflow, preserve authorization boundaries, and distinguish native skill support from ordinary prompt use. Do not claim that model output is verified simply because a second model agrees.

By contributing, you agree to license your contribution under the repository's MIT license. Do not copy third-party manuals or paywalled material into the repository.
