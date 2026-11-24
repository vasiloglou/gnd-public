# Sanitization of the retained reviewer output

On 2026-11-24, after the review, two retained files were edited under the project.md rule on
retained reviewer output, with `review_tool.py sanitize`. Codex wrote absolute paths into its
answer and its log. Each absolute path was replaced by a placeholder, and a header saying so was
prepended. Nothing else was changed. The log still quotes the author line of the repository's
own `pyproject.toml`, which is already public there.

| File | Before (sha256) | After (sha256, bytes) |
|---|---|---|
| `review.md` | `f1a1b819a2ffa0d02979ea7867e5f6b3e5313f6f2f9f8fbd25eedd767fe8e6d4` (bound by `run.json`) | `78f774e204c57c6eb13ead4379bf2ad78eeceadf7662d11c94a71876ae79fd67`, 5882 |
| `review.log` | not recorded before sanitizing | `ed73114c14118316b68885021f220abfb9f954a10bbe52f3138d448ff46d5067`, 299852 |

**Effect on digests.** `run.json` still records the before digest of `review.md` and was not edited.
