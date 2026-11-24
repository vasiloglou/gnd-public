# Sanitization of the retained reviewer output

On 2026-11-24, after the review, two retained files were edited under the project.md rule on
retained reviewer output. Codex wrote absolute paths into its answer and its log. Each absolute path was
replaced by a placeholder, and a header saying so was prepended. Nothing else was changed.

| File | Before (sha256, bytes) | After (sha256, bytes) |
|---|---|---|
| `review.md` | `50e188ef9302c5992a6de9ed1dc047bcaf5717aa1554cdb7b9bfc4f00de0af8b`, 6461 | `8ecc9256423dc0158b32c834b64a0157f3ec9641ab0dbeeff46d9c9469824c93`, 5828 |
| `review.log` | `8408cb429ee77ad39fbb5d4b6d664f75c35243aaf43e6c7c6bf9e9a8bae813b6`, 362695 | `62114185b5ee347ea2e5e9388b122fcba883cc2888f782f70ad34935407af7fb`, 353122 |

**Effect on digests.** `run.json` still records the before digest of `review.md` and was not edited.
