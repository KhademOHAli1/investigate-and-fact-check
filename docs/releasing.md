# Release process

1. Update `VERSION`, skill `metadata.version`, Claude plugin version, any declared marketplace version, and changelog together.
2. Run `python3 tools/validate.py` and `python3 -m unittest discover -s tests -v`.
3. Run `python3 tools/build_dist.py`; inspect `dist/` and its `SHA256SUMS`.
4. Commit and tag the checked revision. Push the branch and tag.
5. Create a GitHub release and upload the ZIPs and checksums. The validation workflow should pass for the published revision.
6. Record directory submissions in `docs/distribution.md`. Distinguish a submitted listing from an accepted or searchable listing.

Each skill ZIP includes the same methodology, templates, helper, and MIT license. The Codex ZIP retains `agents/openai.yaml`; Claude and Mistral ZIPs omit that vendor-specific UI file. The Claude plugin ZIP includes `.claude-plugin/plugin.json`, the canonical skill, README, and license. No case data or local paths belong in a release.

Archives use stable file ordering and a fixed ZIP timestamp. This makes the release artifacts reproducible from an identical working tree. SHA-256 checksums establish integrity relative to the published checksum file; they are not a publisher signature.
