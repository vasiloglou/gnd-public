Retained text of the reader's report, from its final message (its harness refused the scratch write). Local paths read `<repo>`, `<scratch>`.

# Close reader 3: UG1 matrix and UG4 docs, skill and follow-ups (predicates 1, 4, 5)

Subject: `<repo>` at `dd3c35a5` (main, branch `claude/ug-close`). Nothing in `<repo>` was edited. Scratch work is in `<scratch>/close-r3/`: `e2e/`, `anon.py`, `drift.py`, `induced.py`, `issues.txt`. The harness refused the Write to `<scratch>/close-r3/report.md` ("Subagents should return findings as text"), so this message is the whole report.

## Verdict: approve-with-fixes

The shipped loop works end to end with shipped commands (my scratch run below). The docs and skill agree with the CLI and the contract. The anonymity scan is clean. Two blocking findings are text-only: the milestone files misstate the GitHub state of the issues, and the #74 follow-up misses a U5 deviation that PR 150 shipped after UG4 was drafted. Fix both in the close record and the follow-ups note before the owner acts on them.

## Findings

### Blocking

**R3-F1 (blocking): the milestone files say no issue is closed, but 74, 75 and 76 are closed.**
- Where:
  - `<repo>/.gnd-planning/milestones/unattended-model-growth/README.md:15` ("UG4 ... not merged ... No issue is closed."), `:38` ("not merged"), `:52-53` ("Until then no code is written").
  - `notes/ug1-issue-dispositions.md:7-15` ("Posted 2026-11-08 ... No issue was closed").
  - `notes/ug4-issue-followups.md:6-8`, which assumes the owner may still close each issue.
- Check run: `gh issue view N --json comments,closedAt,stateReason` and `gh api repos/vasiloglou/gnd-public/issues/N/comments`.
- Observed:
  - #74, #75 and #76 are CLOSED (COMPLETED), closed at 2026-11-08T14:44:50Z, :53Z and :55Z.
  - Each of the three got an earlier comment at the moment it was closed: 6722886413, 6722886778, 6722887188. Each earlier comment ends with a "Closed by the owner's decision, from the UG1 acceptance replay ..." line.
  - The set the note records (6725035181 and the others, posted 17:59Z) is a second, near-duplicate post. So each closed issue carries the disposition twice.
  - #104 is OPEN with one comment.
  - UG4 is merged (PR 151, `dd3c35a5`).
- Fix:
  - Correct the README status and "Next action".
  - In the close record, state the observed closures and the 14:44Z comment set as facts, without saying who acted.
  - Retitle the #74 and #76 follow-ups as comments on closed issues. Only #104 is left for the owner to close.

**R3-F2 (blocking): the #74 follow-up and the matrix miss a second U5 deviation shipped by PR 150.**
- Where:
  - `notes/ug4-issue-followups.md:17-35` (#74: "Nothing in this issue's scope is open"; it repeats only the common-sense deviation by reference).
  - `002-phase-UG1.md:61,64`: the matrix row "74 span on every fact and constraint: met" and the deviation row for `common-sense` only.
- Check run:
  - `git show 42a34aca` (PR 150, issue 148, on main via `39246a93`): `_rule_unattended` now exempts an `induced` constraint that carries a `provenance.induction` block from U5.
  - The new representation-format U5 row, gnd-model-from-text `SKILL.md:107` and `grow-a-model.md:346-348` all state the new exemption.
  - `uv run pytest tests/test_unattended_mode.py -k induc` gives 2 passed.
- Observed: on main, issue 74's ask "every ... constraint cites a source span" now has two documented exemptions, not one. The posted and closed #74 comment and the drafted follow-up name only `common-sense`. The UG4 branch merged PR 150 (`ab6beff7`) but did not refresh the follow-up.
- Fix:
  - Add one sentence to the #74 follow-up: "Since PR 150 (issue 148), an `induced` constraint from `gnd discover` cites its `provenance.induction` block in place of a span (U5); spans it does carry are still checked."
  - In the close matrix delta, make row 74 "met with deviation (common-sense, induced)", citing `tests/test_unattended_mode.py::test_issue148_induced_cites_its_induction_block_in_place_of_a_span`.
  - The UG1 record is historical; do not edit it.

### Hardening

**R3-F3 (hardening): the follow-ups still carry the placeholder "this phase's PR".**
- Where: `notes/ug4-issue-followups.md:7-8,14,34,40-41,57`.
- Check run: `git log --first-parent dd3c35a5`.
- Observed: the PR is #151, merged.
- Fix: replace the placeholder with "PR 151".

**R3-F4 (hardening): the #104 follow-up and the procedure narrow the modify case.**
- Where: `notes/ug4-issue-followups.md:51` and `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md:289` both say "a strengthening-only change".
- Check run: read the contract.
- Observed: `evolution-contract.md:298-300` clears a `constraint.populated.modify` "whose differing keys all strengthen, weaken or are admitted". So a modify that mixes strengthening and weakening is also clearable. The drafts say less than what shipped.
- Fix: write "a change that strengthens one (weakening keys may accompany it)", or drop the clause and cite "Population check".

**R3-F5 (hardening): the additive guarantee and the span rule are stated without their qualifiers in three places.**
- Check run: `git grep -n -i "interpretable|invalidate|earlier facts|only adds|..." -- docs src/gnd/skills`, then reading each hit.
- Observed:
  - `docs/how-to/grow-a-model.md:8-12`: the intro says a new constraint on held facts would change their meaning and "GND checks that for you", with no "facts it can see" and no `--check-population` exception. The page does qualify it later, at :129-134 and :268-274.
  - `docs/agents/model-from-text.md:26-27`: "cites a span of its source text for every claim, which `gnd validate` checks". This ignores the `common-sense` and `induced` exemptions, and spans are re-hashed only for supplied documents.
  - `docs/reference/evolve-policy.md:39` ("The guarantee's condition"): `apply` must repeat `--policy` and `--populated`. It leaves out `--check-population`, which only appears at :59-60.
  - Every other statement of the guarantee is qualified: gnd-model-evolve SKILL.md:125-139, agents/evolve.md:37-43, the contract :229-231 and :339, and unattended-growth.md:84-87.
- Fix: add short qualifiers ("that GND can see", "except `common-sense` and `induced` constraints", "and any `--check-population`"), each linking its home.

**R3-F6 (hardening): matrix row 76 cites tests that do not check readings or reference modes.**
- Where: `002-phase-UG1.md:70`.
- Check run: read `test_t1_three_round_replay_exits_zero_at_every_step` and T13.
- Observed: both assert only the `fact_type` ids in `shape_matches`. Issue 76 also asks for "compatible reference modes, and their readings". Those are asserted at service level in `tests/test_evolve_shape_matches.py` (`test_t2_an_add_shaped_like_an_existing_fact_type`, `test_t2_reordered_roles_match_and_carry_readings`), which the row does not cite. My scratch preview shows `references` and `reading` present.
- Fix: cite those two tests in the close matrix delta.

**R3-F7 (hardening): some test assertions are vacuous or weak.**
- Where:
  - `tests/test_unattended_growth_guidance.py:173` asserts a property of the fixture (`customer` has no `subtype_of`), not of the policy result. The line is vacuous; the test itself is not, because :172 asserts the policy.
  - `tests/test_unattended_model_growth_acceptance.py:683` (`assert seen and all(isinstance(...))`) is always true. It is harmless; :682 does the work.
  - `_drift` (`test_unattended_growth_guidance.py:238-254`) checks option names and literal choices, not a full parse.
- Observed: a bare option in prose is checked against the union of the three commands' options, so a span like "`apply` takes `--shape-report`" would pass. Running `_drift` over the other UG4 pages (scratch `drift.py`) found no real drift; its only hits were options of other commands, which are false positives.
- Fix: delete or replace :173 with an assertion on the candidate. Optionally, check bare options in a sentence that names `apply` against `apply`'s parser.

### Completeness

**R3-F8 (completeness): no committed test runs the loop the procedure now prescribes.**
- Where:
  - `tests/test_unattended_model_growth_acceptance.py:144-151,184-192`: the replay `_round` still declares each document out of band (`_declare`), the path the procedure now calls earlier behavior.
  - Predicate 1's replay passes, but it demonstrates the pre-UG3 loop.
- Observed: each shipped piece is pinned in its own phase file (`test_evolve_source_document.py`, `test_evolve_population_check.py`, `test_unattended_mode.py`). Nothing composes them.
- Check run: in `<scratch>/close-r3/e2e/`, the scratch host `host.py` built proposals with `gnd.evolve` models. Round A was one `source-document` add followed by an object type and a fact type citing the new document:

  | Step | Command (abridged) | Observed |
  |---|---|---|
  | Validate the candidate, both documents supplied | `gnd validate CANDIDATE --document source.txt --document round-a.txt --require-documents` | exit 0 |
  | Validate, new document left out | same without `--document round-a.txt` | exit 3, `2 of 12 source spans were not re-hashed ... [unattended:spans-unchecked]`; without the flag, exit 0 plus one warning |
  | Preview | `gnd evolve preview ... --policy additive --shape-report` | exit 0; `affected: source.documents[...]`; `shape-group ... existing -` |
  | Apply | `gnd evolve apply ... --policy additive` | exit 0, `conformance-exit: 0` |
  | Validate the published model | `gnd validate MODEL --document ... --require-documents` | exit 0 |

  Round B added a new uniqueness constraint on the round-A fact type, named with `--populated`:

  | Step | Observed |
  |---|---|
  | Preview without `--check-population` | `constraint.populated.add` |
  | Preview with a violating file | still refused; detail ends `; population: warning` |
  | Preview with a clean file | `population-admitted: 0 ...` |
  | Apply without the option | `--check-population differs from the reviewed preview` |
  | Apply with `--shape-report` | exit 64 |
  | Apply with the same options | exit 0 |

  So a host can follow the procedure using only shipped commands. The one non-command step, writing the proposal JSON, is the host's by design ("The CLI does not propose changes"), and the format is in the contract.
- Fix: add one composed case to the acceptance file (a T15), or cite the per-phase corpus cases in the close matrix as the evidence for O14 and O20 being met.

**R3-F9 (completeness): the source-document locator is attributed to different issues on different pages.**
- Where: `docs/release-notes.md:67` ("(issue 104)") and `README.md:36` ("(issue 104)"), but `ug4-issue-followups.md:12,27-32` claims it as #74's open item, and the UG1 matrix row is "74/104".
- Fix: write "issues 74 and 104" in the release note and the README line.

## Claims checked and found true

- **Every ask has a matrix row.** I read the issue bodies with `gh issue view`. Every ask of #74 (four bullets), #75 (three refusals plus "named in the preview claim, apply cannot publish"), #76 and #104 (items 1 to 5, both options) has a row in `002-phase-UG1.md:59-78`.
- **Every "met" cites an executable result.** Each "met" row names a test that resolves and passes on main.
  - `uv run pytest tests/test_unattended_model_growth_acceptance.py tests/test_unattended_growth_guidance.py tests/test_unattended_mode.py`: 117 passed.
  - The cited service-level tests, `tests/test_evolve_additive_policy.py::test_t1_one_case_per_matrix_cell` and `::test_t2_each_strengthening_item_is_refused`, exist: 37 passed.
  - "Inspected" rows (104-3, 104-4) are labelled as prose, not "met".
- **The open rows are now shipped.** The matrix rows marked open (O14, O20, 76 host action, 104-5 second option) are shipped on main: UG3a's `--require-documents` and counts, UG3b's `source-document` locator, the reference's "Acting on a shape match", and UG2's `--check-population`. The follow-ups table maps each one, except the R3-F2 gap.
- **The CLI matches every page.** `gnd validate --help`, `gnd evolve preview --help` and `gnd evolve apply --help` match the reference, both SKILL.md files, `cli.md:20,49-50`, `evolve-policy.md` and the how-to. `apply` has no `--shape-report` (exit 64, observed). `--check-population` requires `--policy additive`. `--require-documents` is a no-op on a plain model (exit 0, observed) and exits 3 with no `--document` (observed).
- **Each statement has one home.**
  - The contract holds the policy, the population check and the locator: "Additive policy", "Population check", "Stable locators" and "EvolutionOperation".
  - `representation-format.md#unattended-source` holds U1 to U8 and the counts.
  - `unattended-growth.md` holds the procedure.
  - The other pages link to these homes. The anchors resolve: `## Unattended source` at :640, `## Calendar-day terms (v7.1)` at :1617, and the contract headings `### Stable locators`, `### Additive policy` and `#### Population check`.
- **The follow-ups match the contract.** The #74 text matches: the warning condition is per span, there is a schema_version 3 operation, the cells are `source_document.modify` and `source_document.delete`, and GND 0.2.0 refuses such a proposal (contract :195-199). The #104 text matches contract :296-337 on the conditions and on exit 11 for a changed file, except R3-F4. The #76 text matches `unattended-growth.md:61-74`.
- **The #74 condition matches the CLI.** "Runs that re-hash every span, runs without `--document`, and models without the mode are unchanged" holds: no `--document` gives exit 0 with `warnings: []`. I did not rerun UG4 review finding 5's case of a declared document that no span cites, but the follow-up's condition is now per span, as that finding asked.
- **No downstream name.** The anonymity scan used `FORBIDDEN`, `CONTROL` and `_digests` from `tests/test_why_not_anonymity.py` (scratch `anon.py`). It covered every file in the milestone directory, the 11 UG4 docs, skill and test files, and every commit message since `12daa5b7`. Result: 0 hits, and the positive control fired. The only tracker-label occurrence is the plan-review snapshot, already raised as UG-Q7.
- **The phase records match what they claim.**
  - The UG4 record's UG4-C5 hit list matches `git grep` on main.
  - The UG4 review's five dispositions are reflected in the text: apply options at :55-57, wrapped spans and fences in the guard at :195-219, the scoped refusal at :76-83, the how-to's sample-rows sentence at :272-274, and the #74 per-span condition.
  - The UG1 record's T12 and T9 comments were updated to name UG3 and are accurate.
- **The six guard mutations bite.** `test_ug4_the_guard_can_fail` covers six distinct mutations, and each is reported.

## Categories with no finding

- **CLI contradictions:** none. Every command and option on the UG4 pages exists with the stated spelling and choices.
- **Procedure followability:** none. The loop runs end to end with shipped commands (R3-F8 records only the missing committed test).
- **Anonymity:** none.
