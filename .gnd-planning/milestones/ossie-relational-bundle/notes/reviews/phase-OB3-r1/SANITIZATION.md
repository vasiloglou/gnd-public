# Sanitization of the retained reviewer output

On 2026-11-24, after the review, two retained files were edited under the project.md rule on
retained reviewer output, with `review_tool.py sanitize`. Codex wrote absolute paths into its
answer and its log. Each absolute path was replaced by a placeholder, and a header saying so was
prepended. Nothing else was changed.

| File | Before (sha256) | After (sha256, bytes) |
|---|---|---|
| `review.md` | `607d402f7212e41e60d7ea9b9de4d22d0477d283b4aeca55d606fbe89ffe4b93` (bound by `run.json`) | `d90fe2009507c11d4349a61d6527c4e71fa3fd94f384b1d52cfff112587f8dc1`, 5120 |
| `review.log` | not recorded before sanitizing | `6a4d9532d2178a938f249cff64143fa299be5f182c04c3f30bf0197c960eb118`, 380476 |

**Effect on digests.** `run.json` still records the before digest of `review.md` and was not edited.
