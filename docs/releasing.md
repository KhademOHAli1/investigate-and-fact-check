# Release process

1. Update `VERSION`, skill `metadata.version`, Claude plugin version, any declared marketplace version, and changelog together.
2. Run `python3 tools/validate.py` and `python3 -m unittest discover -s tests -v`.
3. Run `python3 tools/build_dist.py`; inspect the five ZIPs in `dist/` and their `SHA256SUMS`. Publish the files for the intended version, not older artifacts left in that directory.
4. Commit and tag the checked revision. Push the branch and tag.
5. Create a GitHub release and upload the ZIPs and checksums. The validation workflow should pass for the published revision.
6. Record directory submissions in `docs/distribution.md`. Distinguish a submitted listing from an accepted or searchable listing.

Each skill ZIP includes the same methodology, templates, Python helpers and supporting package, and MIT license. The variants are `codex`, `claude`, `mistral-vibe`, and `agent-skills`. The Codex ZIP retains `agents/openai.yaml`; the other skill variants omit that vendor-specific UI file. The Claude plugin ZIP includes `.claude-plugin/plugin.json`, the canonical skill, README, license, and supporting documentation. `SHA256SUMS` contains one checksum for each of these five archives.

The generic bundle serves other Agent Skills clients using their documented discovery locations. Keep [harness installation documentation](agent-harnesses.md) and the [validation matrix](compatibility.md) aligned with checks actually performed. A successful archive build is not evidence of runtime activation in another client.

Packaging tests extract each bundle outside the checkout and run both Python entrypoints with `--help`. Keep all sibling `casekit/` modules in the installed skill; copying only `case.py` is insufficient. No generated case data or local paths belong in a release. The builder rejects recognizable case trees, databases, checkpoint archives, and filled reusable CSV templates within public input directories.

Archives use stable file ordering and a fixed ZIP timestamp. This makes the release artifacts reproducible from an identical working tree. SHA-256 checksums establish integrity relative to the published checksum file; they are not a publisher signature.
