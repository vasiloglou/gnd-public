# Sanitization of the retained reviewer output

On 2026-11-25, after the review, two retained files were edited under the project.md rule on
retained reviewer output, with `review_tool.py sanitize`. Codex wrote absolute paths into its
answer and its log. Each absolute path was replaced by a placeholder, and a header saying so was
prepended. In `review.log`, the account name in the owner column of eight `ls -l` lines was also
replaced by `<user>`, by hand. Nothing else was changed.

| File | Before (sha256) | After (sha256, bytes) |
|---|---|---|
| `review.md` | `af859815c4ee6dce9781321e6675bd48ba46e42684ea43840cb0b802fe939f4b` (bound by `run.json`) | `659df7052c2c31cb57859494a09afb161e28894f8c28493c327d788ab2e50431`, 4882 |
| `review.log` | not recorded before sanitizing | `fbfb607ff3259a3620361a8d9da23b4a336052cbf1df9f7ee9e43339c594537d`, 612710 |

**Effect on digests.** `run.json` still records the before digest of `review.md` and was not edited.
