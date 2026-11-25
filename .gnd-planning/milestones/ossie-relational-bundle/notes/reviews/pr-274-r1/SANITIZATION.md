# Sanitization of the retained reviewer output

On 2026-11-25, after the review, `review.md` and `review.log` were edited with
`review_tool.py sanitize`: each absolute path was replaced by a placeholder and
a header saying so was prepended. In `review.log`, the account name in two
lines was also replaced by `<user>`, by hand. Nothing else was changed.
`run.json` still records the digest of the original `review.md`.

Two lines of the log still contain the text `/Users/`. They are the
reviewer's own search patterns, not paths.
