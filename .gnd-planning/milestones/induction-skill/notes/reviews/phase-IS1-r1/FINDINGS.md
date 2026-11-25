# Findings ledger: phase-IS1-r1

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
| codex F1 | `EMITTED 0` can come with a written fact-type proposal; the judges need `--type-evidence` | yes: `--out` is written whenever anything is proposed, and fact types are counted under `FACT TYPES` (`docs/reference/discover.md`, `src/gnd/discover/output.py:184`) | blocking | fixed | 2eb6478d | `test_t8_discovery_hands_off_by_the_written_file_not_by_emitted`, red on the old text |
| codex F2 | the miner import is all-or-nothing, not a kept subset | yes: `gnd import mined-rules --help` says "Admission is all-or-nothing" | blocking | fixed | 2eb6478d | `test_t8_the_miner_import_is_all_or_nothing`, red on the old text |
| codex F3 | `inducer` is the proposal's provenance field, not the run record's | yes: `docs/reference/ilp-bridge.md:242`; the run record has `learner` | blocking | fixed | 2eb6478d | `test_t8_the_handoff_names_the_proposal_inducer_not_a_run_record_field`, red on the old text |
| codex F4 | a learner needs a class-mode manifest; the fallback export is `--target neutral` | yes: `ilp-bridge.md:33`, `:113` | blocking | fixed | 2eb6478d | `test_t8_a_learner_needs_a_class_mode_manifest_and_falls_back_to_neutral`, red on the old text |
| codex F5 | the description calls a report a proposal; measure prints more cells; Popper has run; "four commands"; "every reference in gnd-orm-core" | yes: the bridge's "Comparing the learners" table lists three Popper runs, run 3 admitted; `gnd measure --help` | blocking | fixed | 2eb6478d | `test_t8_the_description_and_summary_claim_only_what_gnd_writes`, red on the old text. Refutes the plan's and spec's "unproven" Popper premise (IS1 record) |
| codex F6 | the route tests accept swapped judge links | yes: swapping the links passed 20 route tests | hardening | fixed | 2eb6478d | `test_t8_each_skill_link_label_names_its_destination`, `test_t8_the_fact_type_family_routes_each_kind_to_its_judge`; the swap now fails 2 (evidence/IS1/review-r1-repairs.txt) |
| codex F7 | one-home counts files, so a second copy or a comment passes | yes: both mutations passed | hardening | fixed | 2eb6478d | `test_t8_each_refusal_is_said_once_and_only_in_gnd_induce`, `test_t8_a_repeat_in_the_same_file_and_a_hidden_copy_are_both_caught`; both mutations now fail |
| codex F8 | reversed LLM, handoff and reactions instructions pass | yes: each passed | hardening | fixed | 2eb6478d | exact-sentence and exact-rows tests; all three mutations now fail |
| codex F9 | the invocation checks miss a missing command and accept an abbreviated option; the global floor is 29 of 41; tilde fences are not scanned | yes: the mined-rules swap passed 277 cases; `--fam` would pass the substring test | hardening | fixed for gnd-induce; deferred for the global guard | 2eb6478d | gnd-induce: `test_t7_the_skill_documents_exactly_its_command_paths`, `test_t7_every_option_is_a_full_option_name_of_its_command`; both mutations now fail. The global guard's floor, substring option match and backtick-only fences predate IS1 and bind every skill: deferred to repository maintenance, an issue on the owner's word |
| codex F10 | the section reader breaks on a trailing space; T17 accepts a fenced row and `gnd checker` | yes | hardening | fixed | 2eb6478d | heading regex tolerates trailing blanks; T17 parses tables outside fences and compares the command cell in full; both T17 mutations now fail, and the trailing-space heading now passes |
| codex F11 | a fixed actor, `git var`, `pip3 install` and `/srv/...` pass | yes: each passed | hardening | fixed | 2eb6478d | `test_t7_every_actor_is_the_placeholder`, broadened `INSTALLS`, `GIT_IDENTITY` and `ANY_ABSOLUTE` with seeded positive cases; all four mutations now fail |
| codex F12 | T16 has no control-1 red; T17 was committed with its row | yes | completeness | fixed | 2eb6478d | T16 run under control 1 (7 failed) appended to evidence/IS1/regressions-red.txt; history split so 86961531 holds T17 without the row and 983a23b0 adds it |

## Round budget (declared before round 2, 2026-11-25)

Round 1 returned 12 findings, all reproduced: 5 blocking (the skill's own text), 6
hardening (test strength), 1 completeness. Round 2 runs once, over the repair diff
(base 983a23b0, the commit before the repair), with the same reviewer. After round 2 the
review stops: anything it raises is fixed if blocking and reproduced, and otherwise
recorded as a residual in the IS1 record. No round 3. Stop rule: if more than half of
round 2's findings are self-inflicted (defects the repair introduced), the next
instrument is the record, not another review.
