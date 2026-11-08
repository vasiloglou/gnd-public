---
milestone: unattended-model-growth
station: "phase-UG1"
skill: "process-phase (repository development, not a gnd-solve station over a domain model)"
scope: phase-UG1
date: 2026-11-07
gate:
  command: "uv run pytest -q tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_growth_guidance.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_growth_example.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_digest_helpers.py --tb=short --junitxml=<scratch>/ug1-junit.xml; uv run ruff check tests/test_unattended_model_growth_acceptance.py"
  exit: 0
  output: "273 passed in 42.23s; All checks passed!"
  base: "12daa5b7 (src and tools unchanged since)"
selection:
  - {obligation: "T1 to T14 acceptance replay through the CLI", disposition: run, command: "the gate above", exit: 0}
  - {obligation: "T-src: no change under src or tools", disposition: run, command: "git diff --stat 12daa5b7..HEAD -- src tools; git status --porcelain -- src tools", exit: 0, note: "both empty"}
  - {obligation: "T-anon: downstream-name scan", disposition: run, command: "scratch script importing FORBIDDEN, CONTROL and _hits from tests/test_why_not_anonymity.py over the scope below", exit: 0, note: "0 hits over 16 inputs; positive control found its plant. Method deviation approved by the owner 2026-11-07, see Anonymity scan"}
  - {obligation: "mutation checks (admit-all, refuse-all policy)", disposition: run, note: "scratch plugins, not committed; results below"}
  - {obligation: "phase-diff review", disposition: run, note: "one reviewer, Codex CLI; notes/phase-UG1-codex-review.md"}
  - {obligation: "full default lane, distribution lane, changed --strict", disposition: cadence, note: "not selected: UG1 changes no imported code and adds no component; changed --strict is vacuous for UG1 (plan)"}
evidence:
  - {path: tests/test_unattended_model_growth_acceptance.py, sha256: 91c83bd59bd1148105465a09f2cd9302c89ad6b3b83bd89c8304c95703973122}
  - {path: tests/fixtures/unattended-model-growth/round-1.txt, sha256: 563072eca999eb6bf9506277f787572c50d8450f64a3eda38bea04ef5a0b04f0}
  - {path: tests/fixtures/unattended-model-growth/round-2.txt, sha256: 0a8023005e3a1afe5f2e2ad774ec3a83223ce28cbb0b2cb39990207171b166c6}
  - {path: tests/fixtures/unattended-model-growth/round-3.txt, sha256: bbc7887d1d9adbb19dcf2690d8652052af84492e8d26a274b7995c9045628bd9}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG1-codex-review.md, sha256: 7e760d0e67aee7b39dffba10ce51b5e3ce354f41e8c66678a54b4673554a4e6f}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/ug1-issue-dispositions.md, sha256: a7c0038d512f477f9944734a3e961b049f7770c2f89952eebbfa673db1f5b4a8}
  - {path: "junit report of the gate run (scratch, not committed)", sha256: b15ae470bed0668b06bbb4ff27475a2b1ddf4ac65887b483a3ac73d123bc1b41}
---

# Claim

UG1 is implemented as tests and fixtures only: 23 test instances (T1 to T14) drive
`gnd validate --document`, `gnd evolve preview` and `gnd evolve apply` through the CLI over
three growth rounds of one model. Every case passes on the shipped bytes; no source or tool
file changed. The spec (r1.3, `b3a4fda4`) was approved by the owner at its gate, read as
"approve as written" (recorded in the spec's status paragraph). `auto=false`.

## Gate output

`273 passed in 42.23s` (nine modules, 23 of them new), ruff clean. The new file is 683
lines against the 550 to 650 estimate; the overage is the per-case `_assert_refused` /
`_apply_breaking` plumbing the review round asked for.

## Mutation checks (author, scratch plugins, not committed)

An admit-all additive policy fails 10 of the 23 tests, every refusal case among them. A
refuse-all policy fails T1, T12 and the shared fixture, so the T4 to T7 controls are not
exercised by it (it fails earlier, at the shared fixture). After review repair, two
further throwaway mutants were run and both fail: T14 re-pointed at the seed span (fails the
new canary-span assertion) and T1 with round 1's shape groups emptied (fails the added
fact-type set assertion).

## Acceptance matrix

Verdicts: `met`, `met with deviation`, `met (output shape only)`, `open`, `inspected`
(prose; cannot fail). Cited ids are test function names in
`tests/test_unattended_model_growth_acceptance.py` unless a file is named; the check that each
passed is mechanical (below).

| Ask (issue, item) | Verdict | Evidence |
|---|---|---|
| 74 span on every fact and constraint | met | `test_t1_three_round_replay_exits_zero_at_every_step`, `test_t9_a_tampered_span_is_found_only_when_its_document_is_supplied`, `test_t10_a_span_naming_an_undeclared_document_is_refused` |
| 74 nothing auto-confirmed; validation rejects confirmed and human sources | met | `test_t8a_a_confirmed_element_is_refused`, `test_t8b_a_human_source_is_refused` |
| 74 header records mode, no reviewer, digests | met | `test_t8d_the_header_names_no_reviewer_and_at_least_one_document`, T1 |
| 74 common-sense may cite a library entry | met with deviation | `test_t8c_only_common_sense_may_cite_a_library_entry_instead_of_a_span` (documented deviation, pinned) |
| 74 span on an unsupplied document is checked | open | O14 gap pinned by `test_t9_a_tampered_span_is_found_only_when_its_document_is_supplied` (omitted document exits 0); UG3 (ii) |
| 74/104 a round declares its own new document | open | O20 gap pinned by `test_t12_declaring_a_document_inside_a_round_is_refused_but_before_it_is_admitted`; UG3 (i) |
| 75 additive refusals for rename, delete, subtype link, populated constraints | met | `test_t2_rename_is_refused_and_apply_cannot_publish`, `test_t3_delete_is_refused_for_both_kinds`, `test_t4_a_constraint_on_a_populated_fact_type_is_refused`, `test_t5_a_spanning_constraint_needs_every_existing_subject_unpopulated`, `test_t6_a_subtype_link_on_an_existing_type_is_refused`; replaced reference scheme and strengthening at service level: `test_t1_one_case_per_matrix_cell`, `test_t2_each_strengthening_item_is_refused` in `tests/test_evolve_additive_policy.py` |
| 75 refusal named in preview; apply cannot publish; options must repeat | met | `test_t2_rename_is_refused_and_apply_cannot_publish`, `test_t4_a_constraint_on_a_populated_fact_type_is_refused`, `test_t7_apply_repeats_the_previews_options`, `test_t13_the_same_rename_is_admitted_without_the_flag_and_refused_with_it` |
| 75/others: refusal text carries no document text or sample value | met | `test_t14_no_document_text_or_sample_value_in_what_the_replay_reports` (canaries with a positive control) |
| 76 structural duplicate-shape report | met | `test_t1_three_round_replay_exits_zero_at_every_step` (round 2 names `loan_has_due_date`; round 1 `existing == []`), T13 |
| 76 what the host does with a match | open | out of scope; UG4 |
| 104-1 steps 3 to 7 unattended, cited, proposed, deontic | met (output shape only) | T1; the procedure's own guard is `tests/test_unattended_growth_guidance.py` |
| 104-2 round, consolidation round, what additive admits | met | T1 round 3 (subtype admitted), `test_t6_a_subtype_link_on_an_existing_type_is_refused` |
| 104-3 many-document checks table | inspected | prose in the growth guidance; cannot fail |
| 104-4 one reply shape | inspected | prose; executable guard `tests/test_unattended_growth_guidance.py`, in the gate |
| 104-5 first option: constraints travel with their fact type | met | T1 round 1, T4 control (b) |
| 104-5 second option: admit a clean-population constraint on a populated fact type | open | T4 shows today's refusal; UG2 must turn it into an admission (UG-D2 (b)) |
| validation order: model issues before document issues | met | `test_t11_model_issues_come_first_and_documents_are_read_only_for_a_valid_model` |

Mechanical node-id check (throwaway script, not committed): every id cited above resolves to
a test in the gate's junit report (digest in the front matter) and every instance of it
passed.

## Anonymity scan (T-anon)

Method deviation from spec §8, approved by the owner on 2026-11-07 ("Yes, record it"). The spec
asked for a pattern file kept outside the repository with its path in an environment variable.
No such file exists, either in this repository or in the owner's other checked-out repositories.
The scan instead reuses the digest set the repository already commits in
`tests/test_why_not_anonymity.py` (sha256
`33d12db551dd601a6c9efc7186909ee3663ed6b522cca065fd9a608154acff53`): 7 SHA-256 digests of the
normalized forbidden names and their separator-stripped forms, so no name is written anywhere.
Before scanning, the author confirmed that the set contains the digests of both names in the
owner's standing anonymity rule. The scan used a throwaway script, not committed.

- Scope (16 inputs): every file added or modified since `12daa5b7` (14 files: the milestone
  directory, the new test file and the three fixtures), every commit message since `12daa5b7`, and
  the PR 123 body. After this record was committed, the scan was run again over that commit's
  message.
- Result: **0 hits.**
- Positive control: the test's own control token, planted in a temporary copy of one scope file,
  was found. The control token is absent from the scope.

## Review

Instrument: one reviewer in a different tool (Codex CLI, selected by the owner), prompt on
stdin, repository read-only, reasoning effort xhigh. **One reviewer is one reviewer; this is not
a panel.** It could not run the suite (no writable temp dir under the read-only sandbox), so
its test verification was by reading. Findings are retained in
[phase-UG1-codex-review.md](notes/phase-UG1-codex-review.md) with their dispositions: three
blocking (T14's validation leg never tripped, T14's refusals unnamed, T4's constraint type) and
one hardening (round-1 control accepted an empty report) and one nit, all reproduced and
repaired in this phase; none was rejected. Claims the reviewer checked and found true: O14/O20
pinned as deviations; `src/` and `tools/` unchanged; neutral fixtures; no downstream name, `_sha256*`
helper, network, credential or `.env` use; per-test copies of the shared fixture; every case is
CLI-level.

## Refactoring review

What this phase revealed about existing structure: the new file imports private helpers from
two existing test modules (UG1-D1 (a), ruled as proposed). That is a coupling the next phase
inherits; moving `_span`/`_translate` to `tests/support/` would remove it. Not executed here
(it touches existing tests, outside UG1's test-only scope); deferred to the owner's choice.

## Boundary

- No source, tool, schema or documentation file changed; no issue closed or commented on; the
  drafted dispositions are text for the owner. PR 123 stays open; merge needs the owner.
- UG2, UG3 and UG4 specs are not drafted and not approved.
- Open owner questions carried: UG-Q6 (component-index statement in `project.md`), UG-Q7
  (tracker labels).
