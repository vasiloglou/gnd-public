# Phase UG1: Acceptance replay and issue disposition

## 1. Status line

**Spec gate `(o2)`, 2026-11-07: approved as written.** Asked "Do you approve
the UG1 spec at its gate?" (options: approve as written; amend; approve with
T1's final `validate` kept to three documents), the owner replied, quoted:
"yes". Read as approval of r1.3 as written, four `--document` arguments in T1
(the first option), including UG1-D1 to UG1-D4 as proposed and the §11 gate.
Approved bytes: r1.3 at `b3a4fda4`, sha256 `30835b56…`; only this paragraph was
added after. It authorizes implementing UG1 (tests, fixtures, drafted
dispositions) and nothing else: no source change, no issue closed or commented
on, no merge. The phase record and the review of the phase diff follow
implementation.

Superseded status text, kept for provenance: **Draft r1.3, awaiting this spec's
owner gate.** Not approved. The
plan was approved at its gate on 2026-11-07 ([001-plan.md](../001-plan.md), plan
r1.2); that approval does not extend to this spec. Implementable only after the
owner approves this spec's gate. No code written. `auto=false`. Plan review
round 1 (four local readers) read r1.1 of this spec (SHA-256 `e7523244…`); its
repairs were applied in r1.2 (see
[plan-review-r1-disposition.md](plan-review-r1-disposition.md)). r1.3 is r1.2
re-read in full by its author against the repository (helper names, messages,
gate test files) with the status wording and §12 as its only changes; no review
opinion exists over r1.2 or r1.3. The owner's plan-decision rulings of
2026-11-07 (plan §10: UG-D2 (b), UG-D3 (c), UG-D9 (b), others as proposed) are
mirrored below.

## 2. Provenance

Derived from [the plan](unattended-model-growth-plan.md) r1.2 (approved at the
plan gate, [001-plan.md](../001-plan.md); reviewed once as r1.1), sections 2.1
and 4 (UG1), the obligations harvested there, and the planning-time probes
described in its opening section. Baseline `12daa5b7`. The owner's
plan-decision rulings (relayed, tagged `(o1)`, 2026-11-07) are in plan §10.
They do not approve this spec: no spec-gate decision exists. Review round 1 is
advisory, not `(p)` approval. When a ruling arrives it is written at its site
with a tag and date.

## 3. Obligations (the step 0 harvest)

| Row | Obligation (source) | Discharged in this spec |
|---|---|---|
| O1 | Steps 3 to 7 unattended, cited, `proposed`, `deontic` (104-1; plan O1) | T1 (round 1 carries uniqueness, mandatory, value type `Date`, all `proposed`/`deontic`); matrix row 104-1 is **met (output shape only)**: T1 hand-builds the elements, so it shows the output is admissible, not that the procedure produces it (the procedure's executable guard is `tests/test_unattended_growth_guidance.py`) |
| O2 | Round, consolidation round, what additive admits (104-2) | T1 round 3 (new subtype admitted); T6 (link on an existing type refused); matrix |
| O3 | Many-document checks, prose (104-3) | matrix row marked **inspected, not executable** (§6.3) |
| O4 | One reply shape (104-4) | matrix row: **inspected**; the shape's executable guard is `tests/test_unattended_growth_guidance.py`, re-run in the gate |
| O5 | Constraints travel with their fact type (104-5 first option) | T1 round 1; T4 control |
| O6 | Item 5 second option | matrix row **open**, owner ruled UG-D2 (b) (build, UG2); T4 shows the refusal today and is the case UG2 must later turn into an admission for a clean population |
| O7 | Span on every fact and constraint (74) | T1 final `validate --document`; T9, T10; deviation row for `common-sense` (T8c) |
| O8 | Nothing auto-confirmed (74) | T8a, T8b |
| O9 | Header records mode, no human, digests (74) | T8d (header rule), T1 |
| O10 | Validation rejects `confirmed`/`user-supplied` (74) | T8a, T8b |
| O11 | `--policy additive` refusals (75) | T2 to T7 for rename, delete, `object_types.modify` and the populated-constraint cells; the replaced reference scheme and the strengthened constraint on a populated fact type have no new CLI case: the matrix cites the existing nodes (the reference-scheme MODIFY case and `test_t2_each_strengthening_item_is_refused` in `tests/test_evolve_additive_policy.py`, and its one-case-per-matrix-cell table test), resolved to node ids at record time |
| O12 | Refusal named in the preview, apply cannot publish (75) | T2 and T3 (preview names; `apply` driven with the blast-radius digest exits 3, model bytes unchanged) for breaking refusals; T4 and T6 (non-breaking: `apply` exits 3 directly) |
| O13 | Structural duplicate-shape report (76) | T1 round 2 (a match naming the existing fact type) and round 1 (the `existing == []` control); T13 (a shape match leaves the exit 0; `apply` rebuilds the report). T11 is the validation-order case, not a shape case |
| O17 | Shape-match handling is the host's (76) | out of this phase; UG4 |
| O18 | Issue dispositions are the owner's | §6.4 drafts, not posted |
| O20 | Document declaration across rounds | T12 (both directions) |
| UG-R1 | Defaults do not move | T13 |

## 4. The standing rules, bound to this phase

| Rule | Discharge |
|---|---|
| UG-R1 defaults do not move | UG1 changes no source file; T13 shows the same proposal exits differently only because of `--policy`; a source diff in this phase is a failure of UG1-C5 |
| UG-R2 nothing confirms | T8a/T8b show the refusals; UG1 adds no writer of provenance |
| UG-R3 evidence licenses, a human admits | not applicable: no admission path is added |
| UG-R4 one walk, one home | the tests exercise `additive_policy_issues` through the CLI only; they restate no matrix cell: each asserts the cell name the contract gives, citing the contract section in a comment, not copying a table |
| UG-R5 digest-bound | not applicable: no new digest. T7 exercises the existing option-mismatch exit |
| UG-R6 disclosure | T14 asserts no document text and no sample value in any refusal message the replay triggers |
| UG-R7 totality, cost | the new test file adds no consumer of untrusted input; it calls shipped, already-total commands. Time-bound test not applicable (no new algorithm) |
| UG-R8 layering, query policy | tests only; `tools/gnd_layers.json` untouched; the layering and RF6 tests are in the gate to show it |
| UG-R9 installer links | not applicable: no packaged skill changes |
| UG-R10 anonymity | fixture documents use a neutral equipment-loan domain; T-anon is the record-time scan |
| UG-R11 approval and protection | spec gate precedes code; PR; no merge |
| Project rule 1 totality | the test helpers read fixture bytes the test authored; argued inapplicable |
| Project rule 2 cap bounds the document, not the algorithm | no new algorithm; the existing time-bound test for the unattended rules stays in the gate |
| Project rule 3 validation order | T11 pins the order `validate` states: model issues first, documents read only after the model validates; and the exit-18-before-policy order stays covered by the existing `test_t1c` |
| Project rule 4 one walk for N kinds | T2 (rename) and T3 (delete) run over **both** object types and fact types, and T5 over a spanning constraint, so a per-kind copy would show as a missing case |
| Project rule 5 prose has one home | the matrix cites the contract; it restates no normative sentence |
| Project rule 6 measure, do not argue | the whole phase: the issues' asks are measured on shipped bytes |
| Fixtures discriminate (project failure class) | T5 puts one populated and one new fact type under one spanning constraint, which separates "any subject populated" from "every subject populated"; T6 uses an *unpopulated* existing type, so a refusal cannot be blamed on population |

## 5. Goal

On shipped bytes at the phase's base commit, a three-round, three-document
replay through the CLI exits 0 at each `validate --document`, each
`evolve preview --policy additive --shape-report` and each `evolve apply`; every
refusal case exits as stated in §8 and names the cell or rule the contract
gives it; each of the plan's acceptance-matrix rows has a verdict backed by a
test result, an inspection marked as such, or the word **open**; no file under
`src/` or `tools/` changes.

## 6. Design

### 6.1 Reuse

The component index (`dev/components/`, `scripts/components_index.py`) exists
(plan UG-Q6). UG1 adds no module, so `components_index.py changed --base main
--strict` is vacuous here. Reuse by reading:

| Capability | Found | Decision |
|---|---|---|
| Build a service, a proposal, an additive preview | `tests/test_evolve_additive_policy.py` (`_service`, `_proposal(before_text, ops, *, artifacts, proposal_id)`, `_preview`, `_op`, `_element`, `_cli_workspace`, `_preview_argv`, `_apply_argv`), `tests/test_model_evolution.py::_service` | reuse by import, as `test_unattended_growth_guidance.py` already does with `import test_evolve_additive_policy as policy` (reader-verified: importing does not re-collect its tests). Note `_cli_workspace` rewrites `model.orm.yaml` on each call and `_proposal` defaults to one `proposal_id`; the replay builds its own workspace once (§6.2) |
| Quote to span translator for a reply | `tests/test_unattended_growth_guidance.py` (`_span`, `_translate`) | reuse by import (UG1-D1 (a)); reader 2 verified (b) is unnecessary |
| A CLI invocation with exit code and stdout | `tests/support/cli_runner.py::run_main` | reuse |
| Conforming unattended model | `tests/fixtures/unattended/conforming.orm.yaml` (declares `source.txt`, a customer/order model) | reuse as the replay's seed. Its own spans cite `source.txt`, so the final `validate` passes that file as a fourth `--document` (else the seed's spans are not re-hashed: the O14 gap), and T1 asserts the exact `--document` argument list |
| Tutorial-style growth example | `src/gnd/examples/growth/`, `tools/build_growth_example.py` | not reused: it is not an unattended model and has two rounds; recorded so a reader does not think the replay duplicates it |

### 6.2 Module by module

**`tests/test_unattended_model_growth_acceptance.py`** (new, about 550 to 650 lines).
Exact surface:

- fixtures dir `tests/fixtures/unattended-model-growth/` with three plain
  UTF-8 documents `round-1.txt`, `round-2.txt`, `round-3.txt` (neutral
  equipment-loan prose). Document 1 carries every sentence round 1 cites: a
  loan's due date "exactly one", a borrower holding a laptop, and the
  reference-scheme sentences; document 2 carries a second sentence restating the
  due-date shape; document 3 carries "a staff borrower is a kind of borrower".
  Every cited quote occurs exactly once in its document (`_span` asserts
  uniqueness). Entities need `reference`, so round 1 also adds the value types
  `loan_id`, `borrower_id`, `laptop_tag`, and `borrower` is an entity so round 3
  can name it in `subtype_of`. No generated digests are committed; the test
  computes them with `support.digests.sha256_bytes` (a local `_sha256`,
  `_sha256_bytes` or `_sha256_file` fails `tests/test_digest_helpers.py`).
- `_declare(model_path, raw, label)`: appends `{sha256, label}` to
  `source.documents` **in the model file**, outside `evolve`, the O20
  workaround, named so the dependence is visible. Round 1's document is
  declared too (the seed declares only `source.txt`).
- `_round(ws, n, ops, *, populated=())`: one workspace for the whole replay;
  per round a distinct `proposal_id`, a per-round preview path (reusing one
  `--out` exits 11), absolute model, proposal and out paths (relative paths
  resolve against the process cwd and exit 74 outside the workspace) or
  `run_main(cwd=…)`, and `expected_model_sha256` recomputed from the currently
  published model text. It asserts the exit **before** reading the preview, and
  returns the preview path and exit.
- `_apply_breaking(...)`: a rename or delete preview is `breaking`, so `apply`
  prompts for the exact `blast_radius.report_sha256` on stdin; the helper
  monkeypatches `builtins.input` to return it (or to raise `EOFError`, which
  exits 11 "breaking evolution requires exact blast radius acceptance"). Without
  this the exit is environment-dependent (11 on EOF, 74 under pytest capture,
  a hang on a tty).
- A `_assert_refused(preview_path, cell, index)` helper used by every refusal
  case: the preview file exists, `policy_issues` is non-null with the expected
  cell and operation index, and stderr contains `additive policy refused`. An
  exit 3 alone is not evidence: candidate-validation failures also exit 3.
- tests T1 to T14 of §8.

No new public function, no source module. Estimated 0 source lines, 550 to 650
test lines, about 40 fixture lines.

### 6.3 The acceptance matrix and the drafted dispositions

Written into the phase record `NNN-phase-UG1.md` at record time (not before
the tests run), one row per ask: ask, issue and item, verdict
(`met` / `met with deviation` / `open` / `inspected`), evidence (a test node id
and its result, or the file and section inspected), and the deviation or gap
in a sentence. A verdict `met` without a test node id is refused by the
reviewer, and the check is mechanical: at record time a throwaway script (not
committed) collects the cited node ids, runs them with a junit report whose
digest goes in the record, and fails if a cited id does not exist or did not
pass. Prose-only items (104-3 the checks table, 104-4 the reply shape's
prose) are `inspected` and say they cannot fail.

Drafted dispositions, one per issue 74, 75, 76, 104, are written to
`notes/ug1-issue-dispositions.md`: a short comment citing the matrix, naming
what is met, what is open and which milestone phase owns it. They are text for
the owner to post. UG1 posts nothing and closes nothing. They name no
downstream application.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| UG1-D1 | Where the shared helpers live | (a) import from the two existing test modules (no churn; couples the new file to their private names); (b) move `_span`/`_translate` to `tests/support/`: touches an existing test, but a cleaner import | open; proposal (a); reader 2 verified collection does not leak, so (b) is unnecessary |
| UG1-D2 | CLI or service level | CLI (`run_main`) for every case that asserts an exit code, because the exit is the claim; there is no service-level case: CLI `apply` already finalizes, and the second O20 round was run at CLI level by two readers | open; proposal as stated |
| UG1-D3 | A failing replay case | (a) record it as an implementation finding, route it to the owner, change no source in UG1; (b) fix in UG1: breaks UG1-C5 and hides a shipped defect inside an acceptance phase | open; proposal (a) |
| UG1-D4 | Whether T12 pins the refusal text | (a) pin exit 3 and the message `declared operations do not equal the canonical candidate model`: UG3 (i) is ruled (UG-D9 (b)), so when it ships it must edit this test knowingly; (b) pin only exit 3 | open; proposal (a), with a comment naming UG-D9 |

## 8. Tests

File `tests/test_unattended_model_growth_acceptance.py`, all through the CLI
unless marked service level. "Exit" is the process exit. The cell names are the
ones in the evolution contract "Additive policy" and the rule ids are the
ones in `representation-format.md` "Unattended source".

| ID | Case | Expected |
|---|---|---|
| T1 | Three rounds over the seed. Round 1 (doc 1, declared first): add `laptop`, `borrower`, `loan` (entities with their value types), value type `due_date` (`Date`), fact types `loan_has_due_date` (loan, due_date; `uniqueness` and `mandatory`) and `borrower_holds_laptop` (borrower, laptop), a closed-list value constraint, all `proposed`/`deontic`, each citing a span. Round 2 (doc 2, declared first): add `loan_is_due_on` (loan, due_date), restating the signature of `loan_has_due_date` with a different reading. Round 3 (doc 3, declared first): add `staff_borrower` with `subtype_of: borrower`. Each round: `validate --document`, `preview --policy additive --shape-report`, `apply`. After round 3, `validate` with exactly four `--document` arguments (the three round documents and `source.txt`) | every step exit 0; each preview has `policy == "additive"` and `policy_issues == []` (without `--policy` the key is absent, so a dropped flag would otherwise pass); round 1's `shape_matches` has `existing == []` (the control: every added fact type gets a group, so a non-empty group alone proves nothing); round 2's group has `existing` naming `loan_has_due_date`; round 3 has `shape_matches == []`, kept only to show a passed flag (`[]`) differs from an absent key; the final `validate` was invoked with exactly those four arguments |
| T2 | Rename an object type and, separately, a fact type (one populated via `--populated`, one unpopulated), on the post-round-3 model | preview exit 3; the `_assert_refused` checks with `object_types.rename` / `fact_types.rename`; the preview file is still written; `apply` driven through `_apply_breaking` with the preview's digest exits 3, stderr names the cell, model bytes unchanged; a second run with EOF stdin exits 11 (pinned, with the reason) |
| T3 | Delete an unreferenced object type (`staff_borrower`) and an unreferenced fact type (`borrower_holds_laptop`) | exit 3; `object_types.delete`, `fact_types.delete` via `_assert_refused`. The elements are unreferenced on purpose: deleting a referenced element fails candidate validation with exit 3 and no cell. `apply` as in T2 |
| T4 | Add a `uniqueness` to `loan_has_due_date` after it is `--populated`; and once with `sample_population` rows (which need `sample_spans`, rule u6, or the candidate fails validation first) | exit 3, `constraint.populated.add` via `_assert_refused`. Controls: (a) the same constraint on the **same** fact type without `--populated` exits 0 (isolates population from everything else); (b) the same constraint on a fact type the same proposal adds exits 0. `apply` of the refused preview exits 3 directly (non-breaking) naming the cell |
| T5 | A `subset` constraint over (a) one populated existing fact type and one new fact type (populated operand on each side, both orders); (b) two new fact types; (c) one populated existing and one unpopulated existing fact type | (a) exit 3 `constraint.populated.add`; (b) exit 0; (c) exit 3. (c) separates "every existing subject populated" from "any populated": a policy refusing only when all existing subjects are populated admits (c) |
| T6 | Set `subtype_of` on an existing, *unpopulated* object type | exit 3, `object_types.modify`; the rule is the `object_types.modify` allow-list (the matrix cell) and `unattended-growth.md`, not a sentence in the contract; the same proposal without `--policy` exits 0 |
| T7 | `apply` repeating a different `--policy` / omitting `--populated` | exit 3 in both directions (option mismatch), stderr naming the option |
| T8a | Unattended model whose constraint has `status: confirmed` | `validate` exit 3, rule `semantic:unattended-u2` |
| T8b | Constraint with `source: user-supplied` (and one `explicit`) | exit 3, `semantic:unattended-u3` |
| T8c | `common-sense` constraint with `library_entry` and no span, alongside a `llm-inferred` one with no span | the first passes, the second exits 3 `semantic:unattended-u5`: the documented deviation, pinned |
| T8d | (1) Header with `reviewer` not `none`; (2) header with empty `documents` | two separate cases so neither masks the other; each exit 3, `semantic:unattended-u1` |
| T9 | Parametrized over one element per round: tamper the span's `excerpt_sha256` (not the document bytes, which gives `unattended:document-undeclared`). Each paired with a run that omits that round's document | tampered, all documents supplied: exit 3, `unattended:excerpt-mismatch` at the element's path, for rounds 1, 2 and 3; omitted document: exit 0 (the O14 deviation, recorded as pinned); `validate` with no `--document`: exit 0 |
| T10 | A span naming an undeclared document | exit 3, `semantic:unattended-u7` |
| T11 | An invalid model plus a document that would also be refused | exit 3 reporting the model's issue; no issue whose rule starts with the exact prefix `unattended:` (model-rule ids are `semantic:unattended-uN`, so a substring check misfires) |
| T12 | O20 through the CLI: (a) round candidate appends a new document to `source.documents` **and** adds an element citing it; (b) the same element addition with the document declared in the model before the round, after an earlier round was applied (CLI `apply` finalizes) and a second declare-then-round | (a) exit 3, message `declared operations do not equal the canonical candidate model`; (b) preview and apply exit 0, `policy_issues == []` |
| T13 | The T2 rename proposal previewed **without** `--policy`: measured on the shipped bytes (plan review) | preview exit 0, `breaking is True`, `policy` and `policy_issues` keys absent; with `--policy additive` exit 3; `apply` of the policy-free preview prompts for the digest (exit 11 on EOF through `_apply_breaking`). A shape match leaves the preview exit 0 and `apply` rebuilds the report. No alternative band is accepted: the assertion must be able to fail |
| T14 | Disclosure: distinct canary tokens placed in a document sentence and in a `sample_population` row; scan stderr, every `policy_issues[].detail`, the `validate` messages and the preview with the five model-carrying keys removed (`before_model`, `candidate_model`, `proposal`, `verbalization`, `blast_radius`, which embed model and sample text by design; the existing disclosure test does the same) | no canary present. Document text never appears in the preview, only digests |
| T-anon | A record-time scan, not a committed test (a test would have to contain the names): the pattern file lives outside the repository (path in an environment variable) and the record carries only its digest and the count. Scope: the milestone directory including `notes/ug1-issue-dispositions.md`, `tests/` additions, commit messages and the PR body. A positive control: the same scan finds a planted name in a temporary copy | zero hits in scope; the positive control finds its plant |
| T-src | `git diff --name-only 12daa5b7...HEAD -- src tools` and `git status --porcelain -- src tools` | both empty (the base is named; uncommitted and untracked files count) |

Every declared branch has a case that can fail it: each exit-3 row has a
control that exits 0 (T4, T5, T6, T8c, T13), so a policy that refuses
everything fails a control, and a policy that admits everything fails a
refusal. Coverage is counted per branch: T2 and T3 each cover both object-type
and fact-type locators; T8a to T8d cover U1, U2, U3, U5 and U7, while U4, U6
and U8 are covered by `tests/test_unattended_mode.py`, which is in the gate.
U4, U6 and U8 are not re-proved here (stated, not hidden).

**UG1-Q1 is answered by measurement** (two readers, 2026-11-07): rename without
`--policy` previews with exit 0 and `breaking: true`; with `--policy additive`
exit 3; `apply` of the policy-free breaking preview needs the digest (11 on EOF).
T13 pins exactly that.

## 9. Out of scope for this phase

Any change under `src/` or `tools/`; the population-checked admission (UG2);
declaring a document inside a proposal (UG3); fail-closed span coverage (UG3);
documentation edits (UG4); posting or closing any issue; reproducing
`tests/test_unattended_mode.py` and `tests/test_evolve_additive_policy.py`
cases that already pass; any live or paid model call; issues 73, 77, 78, 95.

## 10. Size

Estimate at write time: 0 source lines; about 550 to 650 test lines (the
guidance test is 191 lines for five tests); about 40 fixture lines; one
drafted-disposition note of about 60 lines. Measured at record time.

## 11. Approval instrument

This prose. No corpus authored first. The owner's gate is on §5 (goal), §8
(cases and exits) and §7 (decisions). Review instrument for the phase diff:
one reviewer in a different tool, prompt on stdin, per `project.md`; a single
reviewer is not called a panel. Several of T2 to T10 repeat cells that
`tests/test_evolve_additive_policy.py` and `tests/test_unattended_mode.py`
already prove at service level; the CLI-level restatement, exit codes included,
is the point of UG1.

Focused gate (proposed, to be fixed when the spec is approved):

```bash
uv run pytest -q tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_growth_guidance.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_growth_example.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_digest_helpers.py --tb=short
uv run ruff check tests/test_unattended_model_growth_acceptance.py
```

UG-Q4 is answered: no default-lane census pins the `tests/` listing; the
only `tests/test_*.py` glob is `tests/test_digest_helpers.py`, which is in the
gate.

## 12. Questions for the spec gate, and one plan-reading note

What the owner is asked to rule here, in the form the gate takes:

1. **Approve §5 (goal), §8 (cases and exits) and §7 (decisions)** as written, or
   amend. Nothing else is asked.
2. **UG1-D1 to UG1-D4** carry proposals only ((a), CLI-level, record-and-route,
   pin the message). Approving the spec approves those proposals; any other
   reading is the owner's to name.
3. **Gate command.** §11's focused gate is proposed, to be fixed when the spec is
   approved. It runs 9 test modules; a run of the eight existing ones at this
   spec's drafting passed (`250 passed in 32.16s`, 2026-11-07, no source touched). That run does not exercise
   the new file, which does not exist.

Plan-reading note. Plan criterion UG1-C1 says the final model validates with
`--document` "over all three documents". The seed `conforming.orm.yaml` also
declares `source.txt`, and a span whose document is not supplied is not
re-hashed (the O14 gap, pinned in T9). This spec therefore reads UG1-C1 as the
three round documents **plus** `source.txt` (four `--document` arguments, T1).
That is a refinement the plan's text permits; if the owner wants the plan's
wording kept literally, T1's final `validate` drops the fourth argument and the
seed's own spans go unchecked, which the spec would then say. The plan is not
edited (its approved bytes stand).
