# Sanitization of the retained reviewer output

On 2026-11-24, after the review, two retained files were edited under the project.md rule on
retained reviewer output, with `review_tool.py sanitize`. Codex wrote absolute paths into its
answer and its log. Each absolute path was replaced by a placeholder, and a header saying so was
prepended. In `review.log`, the account name in the owner column of four `ls -l` lines was also
replaced by `<user>`, by hand. Nothing else was changed.

| File | Before (sha256) | After (sha256, bytes) |
|---|---|---|
| `review.md` | `88049c0c6b2423365cdf0071ec5a4d8ce8357119258cfd7fc6987dae02f0560a` (bound by `run.json`) | `c9c596d718f6556b5a7fb269769bec7d01085201c4558555ed62e2c7c0cef6e1`, 5092 |
| `review.log` | not recorded before sanitizing | `3dccc7ccb401a3fbcba85065132d3fd05e4c9f529353eae05adc7d66898dcb57`, 556302 |

**Effect on digests.** `run.json` still records the before digest of `review.md` and was not edited.
