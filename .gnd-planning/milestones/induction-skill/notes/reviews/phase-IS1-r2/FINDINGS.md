# Findings ledger: phase-IS1-r2

One row per finding the review returned, under the reviewer's own id. Fill every cell:

- Reproduced: yes or no. A finding is believed only once it is reproduced against the bytes.
- Class: blocking, hardening or completeness, assigned here, not by the reviewer
  (review-convergence.md).
- Disposition: fixed, deferred, rejected or open.
- Repaired at: for a fixed finding, the commit or tag that holds the repaired bytes. Those
  bytes are unreviewed until a later round reads them; `review_tool.py status` says which.
- Notes: the regression test for a fixed finding, the target for a deferred one, the reason
  for a rejected one.

If the review returned no findings, replace the table with the line: No findings.

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| codex F1 | the Score sentence gives class-mode cells to expected-state reports | yes: `docs/reference/measure-labels.md`, schema 4 has the synth cell table, schema 5 the six counts | blocking | fixed | the IS1 record's commit | `test_t8_the_description_and_summary_claim_only_what_gnd_writes` gains two assertions, red on the old text (evidence/IS1/review-r2-repairs.txt); the skill now says the cells differ by mode and links the reference |
| codex F2 | "its files are what any learner reads" is wrong for the neutral export | yes: `ilp-bridge.md`, Export: neutral writes only `neutral.json` and `export.json` | blocking | fixed | the IS1 record's commit | same test, red on the old text |
| codex F3 | the description says "every result" goes to review; the summary test misses a restored Score section | yes for the description; yes for the test | blocking (description); hardening (test) | fixed (description); deferred (test) | the IS1 record's commit | description assertion added, red on the old text. The line-break-spanning forbidden phrase is a residual of the test (IS1 record, Boundary) |
| codex F4 | the actor guard accepts `--actor=operator` and an import with no `--actor` | yes, by reading `_induce_snippets` and the test | hardening | deferred | — | residual: per-command actor assertion; target: the next change to `tests/test_induce_skill.py` (IS1 record, Open questions IS1-Q2) |
| codex F5 | a second labelled export in place of the miner's passes; tilde fences are not scanned | yes | hardening | deferred | — | residual: bind the `amie` target to its export line; the tilde-fence gap is round-1 F9's global deferral (IS1-Q1, IS1-Q2) |
| codex F6 | a commented-out table passes; extra reaction rows are filtered out; pipeless tables are rejected | yes, by reading `tables()` and the reactions test | hardening | deferred | — | residual (IS1-Q2) |
| codex F7 | a refusal moved into a link-definition title still counts; a fenced heading is accepted, `## Learn ##` rejected | yes, by reading `visible()` and `section()` | hardening | deferred | — | residual (IS1-Q2) |
| codex F8 | changing only the Hand off link passes; a titled link escapes the label matcher | yes | hardening | deferred | — | residual (IS1-Q2) |
| codex F9 | keyword tests accept reversals that keep their keywords | yes | hardening | deferred | — | residual; the honest limit of sentence tests (spec section 8) applies (IS1-Q2) |
| codex F10 | the path, install and identity matchers miss `/workspace`, non-ASCII paths, `pip3 --isolated install`, `${USER}` | yes, by reading the three patterns | hardening | deferred | — | residual (IS1-Q2) |
| codex F11 | the evidence runner restores the supplied baseline and labels any failure CAUGHT | yes, by reading `review-r1-mutations.py` | completeness | deferred | — | the recorded outcomes were independently reproduced by the reviewer (round 2, "What I verified"); the script's defect is stated beside them in evidence/IS1/review-r1-repairs.txt |

## Stop rule (round 2)

Self-inflicted findings, introduced by the round-1 repair: F1 (its new Score wording), F4,
F6, F7, F8, F9, F10 and F11, eight of eleven (0.73 > 0.5). F2 and the description half of
F3 predate round 1; F5 is half new (the miner line) and half the deferred global gap. The
stop rule holds and the budget said no round 3: the three blocking text findings are fixed
with failing-first assertions, and the eight hardening and completeness findings are carried
as residuals in the IS1 record. The repaired skill bytes carry no review opinion.
