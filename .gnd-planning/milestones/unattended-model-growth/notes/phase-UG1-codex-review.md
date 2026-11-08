# UG1 phase diff: Codex CLI review (one reviewer)

2026-11-07. Instrument: one reviewer in a different tool, selected by the owner
("Codex CLI"): `codex exec --ephemeral --model gpt-6.1-sol` at reasoning effort
`xhigh`, `--sandbox read-only`, prompt on stdin, repository read-only. This is
**one reviewer, not a panel**. Subject: `git diff b3a4fda4..ffacc133`.

**This file was edited from the reviewer's output in one way:** the operator's
absolute worktree path was replaced by `<repo>/` (the review-and-record
sanitization rule). Nothing else in the "Reviewer output" section is changed.

**What the reviewer could not do.** Under the read-only sandbox it had no
writable temporary directory: its run of the nine-module gate reported
`74 passed, 199 setup errors`, and all 23 UG1 instances failed in setup. Its
verification of the new tests was by reading and by in-memory reproduction
through the CLI seams; it did not run the suite or the mutation checks. Ruff
passed for it.

## Reviewer output (verbatim, path sanitized)

1. **blocking — [test_unattended_model_growth_acceptance.py:669](<repo>/tests/test_unattended_model_growth_acceptance.py:669), claims 1/6.** T14’s validation leg does not trigger a refusal. It tampers `customer`, whose span cites `source.txt`, but supplies only `canary.txt`. Reproduced through the real CLI with in-memory file-read seams: **exit 0, issues `[]`**. The test never checks that exit. Also, none of its six canary-document excerpts contains `DOC_CANARY`; the positive control checks only `ROW_CANARY`. **Fix:** cite an excerpt containing the document token, tamper that span, and assert exit 3 plus its exact issue/path before scanning disclosure.

2. **blocking — [test_unattended_model_growth_acceptance.py:660](<repo>/tests/test_unattended_model_growth_acceptance.py:660), claim 2.** T14 checks only that `policy_issues` is nonempty. Unlike other policy refusals, it never checks the cell or operation index. Its rename apply at line 667 also lacks an exit-code assertion, so successful publication would not itself fail this test. **Fix:** use `_assert_refused` for both operations and assert apply exits 3 with the expected cell/index.

3. **blocking — [test_unattended_model_growth_acceptance.py:364](<repo>/tests/test_unattended_model_growth_acceptance.py:364), claim 1.** Spec §8 T4 requires adding **uniqueness** to `loan_has_due_date` with `--populated`; this case adds **mandatory**. Control (b), at lines 378–383, also changes the constraint’s role and provenance rather than placing the same constraint on a newly added fact type. **Fix:** use a valid uniqueness constraint and preserve its payload across controls, changing only the intended population/host condition.

4. **hardening — [test_unattended_model_growth_acceptance.py:215](<repo>/tests/test_unattended_model_growth_acceptance.py:215), claims 3/4.** Round one’s control is `all(... for group in shape_matches)`, which accepts `[]`. Reconstructed the real reports (`[2, 1, 0]` groups), replaced only round one’s report with `[]`, and executed T1’s shape assertions: **passed**. **Fix:** assert the expected round-one added fact IDs/groups before checking their empty `existing` lists.

5. **nit — [test_unattended_model_growth_acceptance.py:31](<repo>/tests/test_unattended_model_growth_acceptance.py:31).** `CONTRACT` and `BASE_COMMIT` are unused; AST inspection found zero reads of either. **Fix:** remove them. No dead imports or helpers found.

## Claims checked and found true

- **5:** T9 and T12 explicitly pin O14/O20 as deviations.
- **7, within the reviewed scope:** requested `src/`/`tools/` diff-stat and status checks were empty; fixtures are neutral; no downstream application, `_sha256*` helper, network, credential, or `.env` access found.
- **8, by inspection:** `grown_base` is copied per test; no order, clock, cwd, hardcoded machine-path, or temporary-path reuse defect found.
- All T cases use `run_main`; none is service-only. Admit-all/refuse-all extremes encounter contradictory exit assertions. Round two checks the exact existing fact, and final validation supplies all four documents.

## Could not do

The nine-module gate reported **74 passed, 199 setup errors** because the sandbox provides no writable temporary directory. All 23 UG1 instances failed during setup, so full replay and mutation-suite execution remain unverified. Ruff passed. No repository files were changed.
## Dispositions (author, after reproduction)

All five findings were reproduced against the code before being accepted, and
all are defects in the new test file (none in shipped behavior). Fixes landed in
the commit that carries this file.

| Finding | Reproduced | Fix | Red before the fix |
|---|---|---|---|
| 1 (blocking) T14 validation leg tampered the seed's `customer` span, whose document was not supplied: exit 0, no issue | yes: `object_types[0]` is the seed `customer` citing `source.txt`; T14 supplied only `canary.txt` | tamper the added `widget` span (its excerpt now contains the document canary), assert exit 3 and the issue path `$.object_types[id=widget].provenance.spans[0]` | a throwaway copy re-pointed at `object_types[0]` fails at the new canary-span assertion; the original assertions passed it |
| 2 (blocking) T14 refusals checked only that `policy_issues` was non-empty; the rename `apply` exit was not asserted | yes: read at the cited lines | both previews go through `_assert_refused` (cells `constraint.populated.add`, `fact_types.rename`); the rename `apply` asserts exit 3 and the cell in stderr | by reading: the removed assertions could not fail on a published rename |
| 3 (blocking) T4 added `mandatory`, not the spec's `uniqueness`; control (b) changed the constraint type | yes: spec §8 T4 says uniqueness | `uniqueness` on role `due_date` of `loan_has_due_date` (round 1 already has `uniqueness` on `loan`, so this is a distinct constraint), and `uniqueness` on `loan` of the added `borrower_holds_loan` in control (b) | n/a (spec conformance); all T4 assertions pass with the corrected payload and the refusal still names the cell |
| 4 (hardening) round-1 control `all(...)` accepts `[]` | yes: reproduced by the reviewer and understood from the code | assert the union of added fact types in round 1's groups equals `{loan_has_due_date, borrower_holds_laptop}` before the `existing == []` check | a throwaway copy with round 1's groups set to `[]` fails T1 (`set() == {...}`); the original passed it |
| 5 (nit) `CONTRACT`, `BASE_COMMIT` unused | yes | removed | n/a |

The reviewer's claims 5, 7 and 8 held as it states; its claim 6 (positive
control) is repaired by finding 1's fix. Its note that "admit-all/refuse-all
extremes encounter contradictory exit assertions" is a by-reading statement; the
author's own mutation runs are in the phase record.
