# Sanitization of the retained panel output

On 2026-11-10, after finalization and at the owner's direction ("Sanitize, note
it"), one retained file was edited under the project.md rule on retained
reviewer output. Nothing else in `panel-run/` was changed.

| File | Before (sha256, bytes) | After (sha256, bytes) |
|---|---|---|
| `panel-run/reviewers/codex/stderr` | `9ed6efc62badab208c3830d6e2ea8d1564c71f2fbfe9c0fedc78732534da1205`, 62107 | `69a32627ba2fcad79b5d1b24378dff7fd7449a814042013d886a3daa19d80a89`, 61384 |

**The edit.** Codex echoed its working directory, the disposable panel
worktree in the session scratchpad, seven times. Each occurrence of that
path was replaced by `<panel-tree>`, and a five-line header saying so was
prepended. The operator's username had already been redacted to `***` by the
panel's capture layer, so the retained bytes never held it. No other retained
file contains a scratch, temporary or home path.

**Effect on digests.** `panel-run/run.json` and
`panel-run/reviewers/codex/envelope.json` still record the "before" digest,
and they were not edited, so the run digest (`b2e21cbe…c162`) and the
canonical synthesis digest that finalize reported (`3c55be06…8e64`,
recomputed after the edit) are unchanged. Re-running `gnd review finalize`
over the committed run now refuses, as measured on 2026-11-10: `review
evidence reviewers/codex/stderr sha256 identity changed`. The committed
PANEL-REVIEW.md is the output of the finalization that ran before the edit,
over the "before" bytes above. The stderr is Codex's tool
transcript, not its response: `response.json` and `stdout`, which carry the
review the synthesis used, are untouched.
