# Sanitization of the retained reviewer output

On 2026-11-24, after the review and before publication, two retained files were edited under the
project.md rule on retained reviewer output. Codex wrote absolute paths into its answer and its log.
Each absolute path was replaced by a placeholder, and a header saying so was prepended. Nothing else
was changed.

| File | Before (sha256, bytes) | After (sha256, bytes) |
|---|---|---|
| `review.md` | `e3407a134a02cf1f4942812b26a55652f15665b347af02a4eeda78980a1a479f`, 3269 | `f8272abfba9eaa08b4760c98674a9a27dcce3cd346da4a6b6602a61d1a308c92`, 3287 |
| `review.log` | `2f91f72958de7269061a06211d3abd10398f3fa415558647e56f988b0297755f`, 370557 | `50930e4be4a1d5dc76c80187e5b5d11f3d28c9ec4e99d453c74c9b9631cfac87`, 366733 |

**Effect on digests.** `run.json` still records the before digest of `review.md` (`review_sha256`), and
it was not edited, so it binds the reviewer's original bytes. The phase record cites the after digest.
