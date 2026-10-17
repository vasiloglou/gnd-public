> Retained verbatim except that mutant labels which could be read as downstream milestone IDs are written MU-prefixed.

# Milestone-close review, reader 3 of 4: transition-check-performance (issue #24)

- **Lens:** protocol compliance, record integrity and anonymity.
- **Subject:** origin/main at `2689ab3` (merge of PR #30). Files were read from a `git archive` of that commit. Hashes were computed with SHA-256 from those bytes, and from `git show <commit>:<path>` for historical checks.
- **Read:** AGENTS.md; process-phase SKILL.md and references (review-and-record, spec-note-contract, standing-rules, review-convergence); the whole milestone directory (README, plan r5, records 001 to 005, every note and evidence list); PROJECT.md §transition-check-performance; commits 359d230 to cea184c; PRs #25 to #30.
- **Not done:** no tests were run, because a concurrent suite run owns that. One reader is one reader.

## What I confirmed

- **The approval chain for the plan and TP0 is intact.**
  - Plan r5 at `fbcf938` hashes to `01fae9d8…aca3`, and TP0 spec r5 hashes to `2165ada0…1e3b`. Both match 001-plan-gate.md exactly.
  - The approval was committed in 15944ee, before the TP0 implementation in 369f161.
  - 001 records the owner's own words ("go on with all of them") and `auto=false`, and it lists what was *not* approved.
- **Every phase has all five steps:** spec, recorded owner approval with a SHA-256, implementation, one independent local diff reader (the record says "one reviewer is one reviewer"), a refactoring review argued from what the phase touched, and a record with verbatim gate summaries and evidence hashes.
- **Where an implementer ran, the reviewer was independent of it.** Codex CLI implemented TP2 and TP3, and a separate local reader reviewed each diff.
- **No approval appears invented.** The quoted owner words for TP1 to TP3 are "approved", "TP2 approved" and "approve TP3".
- **Every evidence hash in records 002 to 005 matched its file at the record's own commit** (77 entries; 369f161, 0b87e91, dc39e4b and a33334a respectively). The mismatches on main are listed in the hash table below. All but one come from later phases editing the same file. The exception is TP3's `api.py` (F1).
- **The gate files hold exactly the summary lines the frontmatter quotes.** Lint reads "All checks passed!" in all four phases. The consumer-gate files match the records: 249 + 564, 249 + 564 and 291 + 564.
- **These deviations are disclosed in spec findings, records or retained reviews:**
  - the hang-guard amendment from 120 s to 600 s (TP1 finding 5, the 003 boundary, and the test comment);
  - the dropped `load_population` decorator (TP1 finding 8, 003);
  - the TP2 T2 guard type (TP2 finding 2);
  - both Codex-reported TP3 spec gaps (TP3 findings 1 and 2);
  - TP3's B1 blocking fix and the consumer regression (findings 4 and 5);
  - the one sanitization of each retained review (`MU10`).
- **PRs #26 to #30 were merged by the owner's account.** Nothing was pushed directly to main.
- **The anonymity sweep found no downstream names.** It covered the milestone directory, `tests/fixtures/transition_cost/`, `tools/measure_transition_cost.py`, the four `test_tp*`/workload test files, `tests/_tp2_freeze_plugin.py`, `src/gnd/api.py`, the docs touched by TP3, and PROJECT.md. It searched for:
  - every token that the anonymization commit 07075d4 removed (downstream repository, application and uv-cache names);
  - the downstream workspace label;
  - session-request IDs in the issue's own form;
  - home paths, the local username and the email.

  All of these returned 0 hits. The only hits for the account name are the public GitHub owner inside the issue #24 links. The fixture's string fields are `expense`, `sum`, `amount`, neutral role names, `urn:gnd-fixture:steps@1` and `Sealed step programs.`.

## Hash table: entries that differ on main (all others match main)

| Record | Path | Recorded (at record commit) | Main `2689ab3` | Cause |
|---|---|---|---|---|
| 002 TP0 | tools/measure_transition_cost.py | 42e2aada… (= 369f161) | 0a2d74e9… | TP3 edit (in 005, matches) |
| 002 TP0 | tests/test_transition_cost_workload.py | 6596d219… (= 369f161) | e620f7a3… | TP1 hang guard (in 003, matches) |
| 003 TP1 | src/gnd/model_index.py | a395ded6… (= 0b87e91) | c820a107… | TP2 (in 004, matches) |
| 003 TP1 | src/gnd/checker/_core.py | fe3bfeb2… (= 0b87e91) | 886892aa… | TP2 (in 004, matches) |
| 003 TP1 | src/gnd/api.py | 003f11fc… (= 0b87e91) | daba38fc… | TP3, then cea184c |
| 005 TP3 | src/gnd/api.py | e6b87892… (= a33334a) | **daba38fc…** | **cea184c, after the record. No record covers it** |
| (other milestone) compiled-snapshot-obligations/007-ci-integration.md | evidence/CI/source-successors.json | 961dc221… | **c64487d8…** | **cea184c** |

## Findings

| ID | Class | Severity | Finding | Evidence | Required for close |
|---|---|---|---|---|---|
| F1 | blocking (close-record precondition) | medium-high | **The TP3 fix-up cea184c is invisible to the milestone record.** It landed after 005 was written. It changed `src/gnd/api.py`: `check_with_receipt` now reads fact types through `ModelIndex…iter_fact_types_shared()`. It also edited the shared source-successor ledger. The record still binds `api.py` to e6b87892, and main is daba38fc. The commit message is the only account of the 11 failures, the local CI replay that found them, and the 7 failures it calls "also fail on main". No record retains the replay output or a focused-gate run, receipt replay or digest parity on the final bytes. The commit's closing line names 005, but 005 is unchanged. | `git show cea184c`; hash table; grep of the milestone directory for "local CI", "cea184c" and "pre-existing" (TP1's two rf6 failures only) | The close record names cea184c and states what failed and why. It binds `api.py` at daba38fc. It retains the CI replay summary with each failing node id. It re-runs and records, at `2689ab3`: the TP3 focused gate, `receipt_replay.py` (25 to 19, payloads identical) and the default digests against TP0. |
| F2 | hardening | medium | **cea184c rewrote another milestone's pinned evidence.** `compiled-snapshot-obligations/evidence/CI/source-successors.json` is pinned at 961dc221… in that milestone's 007 record and in its review note, and it is now c64487d8…. Beyond appending five RF6b rows, the commit replaced an existing RF4 row's `after` hashes and extended its `reason`. That is in tension with TP-R6 ("Preserve existing records and evidence") and with the reader's own docstring ("historical evidence is immutable", `tests/support/rf9_ci_sources.py:1`). The file is the only successor ledger, hard-coded by path, so some edit was needed. The problem is that it went undisclosed in any record. | `git log` of that file (381187e, cea184c); `rf9_ci_sources.py:6` | Disclose the cross-milestone edit in the close record. Either append a discharge note under the 007 pin, or state that it is superseded and cite the new hash. Open a row for the ledger's home (below). |
| F3 | hardening | medium | **Refuted premise: the per-phase affected-consumer selections did not cover the touched homes.** Records 003, 004 and 005 give the slow-cadence reason "focused gate plus N affected-consumer tests cover the touched homes". 003 also claims the RF1/RF2/RF6/RF7 pins pass. Yet TP1 and TP2 changed six pinned definitions with no successor row, and TP3 broke the counted query policy. Only a full local replay at the stack tip caught this (11 failures). | cea184c message and diff; 003/004/005 frontmatter | Record it as a refuted premise, with an open-questions row naming the repair. The repair: when `src/gnd` changes, add the RF9 source-successor pins and `test_rf6_query_policy` to the affected-consumer selection (the verification-selection reference, or the milestone's successor). |
| F4 | hardening | medium | **The TP1 to TP3 approval hashes cannot be verified from history.** No commit holds a spec version matching TP1 `531f8016…`, TP2 `a6cf8f35…` or TP3 `8f842c6f…`, because each spec first appears in the same commit as its implementation (0b87e91, dc39e4b, a33334a). Spec-before-code ordering therefore rests on the record's word. TP1's `red.txt` adds partial support. By contrast, the plan and TP0 approvals verify exactly. I found nothing suggesting an approval was invented. | `git log --all` on each spec | The close record states this limit. For later milestones, commit the spec at its gate, as was done for TP0. |
| F5 | hardening | low-medium | **Post-approval deviations were decided by the session, with no recorded owner ratification.** All of them are disclosed, but none carries an owner mark: (a) TP0 D5, which the owner ruled at 120 s in 001, became 600 s in TP1; (b) TP3 gaps 1 and 2 (the anchored mint route, and the unvalidated-marker route) say only "flagged to the owner in the session report"; (c) the TP1 `load_population` decorator was dropped against the approved §6 table; (d) the TP2 T2 guard type changed. The approved expected values were unchanged in every case. | TP1 findings 5 and 8; TP2 finding 2; TP3 findings 1 and 2; 001 | Add owner-ratification rows to the sweep. The owner rules on each, or accepts all of them together. |
| F6 | hardening | low | **Anonymity labels are inconsistent.** Only mutant label 10 was rewritten (`MU10`) "so it cannot be read as a downstream milestone ID". Labels M1 to M13 remain in the TP0, TP2 and TP3 reviews. Plan reviewer R3-02 had already shown that the bare label `M3` collides with a downstream milestone identifier, and MU3 appears in all three reviews. R3-02 also asked the owner to decide whether the in-repo milestone name cited in plan lines 70, 133, 155 and 360 is acceptable. The disposition fixed only the shorthand and records no owner ruling on the name. No downstream repository, application or dataset name was found. | the review notes; plan-review-r1-reader-3 R3-02; disposition line 51 | The owner rules on whether the M-labels and the in-repo milestone name need redaction. Apply one consistent rule to all retained reviews. Any rewrite is declared in each file's header. |
| F7 | completeness | low | **Status text is stale.** The README says "draft r5 … not approved" and "First phase spec … awaiting owner review". PROJECT.md says the plan "awaits owner approval". The plan header still says "Plan approval, phase execution, implementation and publication have not occurred". | README lines 6–9; PROJECT.md lines 88–97; plan line 6 | Repair at close, since plan repairs belong to the close. |
| F8 | completeness | low | **Two TP1 spec findings disagree with the retained evidence.** Finding 3 gives "421 + 564" consumer tests where the record and evidence say 249 + 564. Finding 4 gives an A/B of 6.93 s to 4.86 s, where the record says 4.01 s to 2.81 s and `ab_scope.txt` says no_scope 4.006 s and scope 2.812 s. The −30% figure agrees in both. | phase-TP1-spec findings 3 and 4; evidence/TP1 | Note at close which figures are authoritative (the evidence files). |
| F9 | completeness | low | **Two plan §5 obligations were never harvested.** (a) A release-note line for TP1 and TP2 is owed at close; `docs/release-notes.md` mentions only receipts. (b) The TP3 spec was to check whether `gnd-dev-session` mentions transition pre-state checks, and it never did. A grep finds no pre-state mention. That skill's "receipts" are judgment receipts, a different concept with the same name. | plan §5; TP3 spec §3; `git diff 2d1ff4d 2689ab3 -- docs/release-notes.md` | Add the release-note line. Record the skill check result, and optionally a sentence that tells the two receipt concepts apart. |
| F10 | completeness | low | **Reproducibility and verbatim-declaration gaps.** TP2's full gate (88 passed) ran before the review successor; only the TP2 file was re-run afterwards. This is disclosed. TP2 and TP3 committed only `review-mutants.txt`, not the script, while TP0 and TP1 committed both. The TP1 and TP2 retained reviews have no header saying whether they are verbatim (TP1 uses `$S` placeholders). | evidence listings; review headers | Optional. Record these as boundaries at close. |
| F11 | completeness | low | **Known reds are asserted, not proven, in the records.** "7 failures that also fail on main" appears only in cea184c's commit message. Only TP1's two `test_rf6_query_policy` failures were proven, against a clean HEAD in the TP1 review. The uv `.gitignore` release-acceptance quirk appears in no milestone file. | grep of the milestone directory | The close record lists all 7 node ids. It proves each one red at the milestone base `2d1ff4d`, in a throwaway checkout, and at `2689ab3`. It describes the uv quirk and gives it an owner. |

No other blocking finding survived. A cleaner close record discharges F1, and none of the findings shows a wrong result, an invented approval or a downstream-name leak.

## What the close record must contain

1. **Citations:** 001 to 005 by path and hash, plus a cea184c addendum (F1) with the final `api.py` hash and the successor-ledger edit (F2).
2. **Final evidence at `2689ab3`:**
   - parity digests equal to TP0 on the default path, and the counters (key paths 26, `model_dumps_other` 457, deep-copy nodes 115,294, checker runs 25, or 19 with receipts);
   - wall time against the ~44% ceiling (closing predicate 6): TP1 −30% and TP2 −8.4% (≈ −35% together) from in-process A/B runs, and TP3 −10% sequential. Wall time is evidence only.
3. **The four close readers' reports and their disposition.**
4. **A refuted premise (F3)** with its repair row.
5. **The open-questions sweep below**, each row with an owner.
6. **Carryovers:**
   - O8, TP4 (request 4 and the two related session requests), goes to a named successor milestone. That milestone must reconcile `structured_extension_view(previous=…, refresh=…)` with CR-01.
   - O13, downstream acceptance, goes to the reporter after merge.
7. **The 7 pre-existing main failures** with node ids and proof (F11), and the uv `.gitignore` release-acceptance quirk.
8. **Plan and status repairs (F7)**, the release-note line (F9a) and the skill check (F9b).
9. **Boundaries carried forward:**
   - receipts are in-process, default options and pre-state only;
   - shared rows are protected only by a docstring plus tests;
   - concurrent model mutation is unsupported;
   - TP1's intermittent failure has one cause not established;
   - the import proof can be re-run only where the bundle exists;
   - every reader is one reader.

## Proposed open-questions sweep

| # | Question | Source | Proposed disposition | Owner |
|---|---|---|---|---|
| Q1 | TP4: incremental evaluation, request 4 and the two related session requests | plan TP4, O8 | Carry over to a named successor milestone | GND owner, who names the milestone |
| Q2 | Downstream application acceptance | O13 | Carry over; outside GND | Issue #24 reporter |
| Q3 | H1: `receipt.report` is a mutable `CheckReport` | 005; TP3 finding 6 | Accept as boundary, or freeze in the successor | GND owner |
| Q4 | H2: a pre-run that raises leads to two checker attempts | 005 | Accept as boundary (non-reusable path) | GND owner |
| Q5 | C1: no reference-population receipt test | 005 | Hardening in the successor milestone | Successor milestone |
| Q6 | `_run_check_raw` ignores `evaluator` on the anchored route; TP3 works around it | 005 refactoring review | Deferred refactor with a named target (successor or a code-refactoring milestone) | GND owner |
| Q7 | Underscore name for `ModelIndex.iter_fact_types_shared` (TP2 F3) | 004 | Rename with an alias and shim entry per AGENTS.md, or accept the docstring contract | GND owner |
| Q8 | An exception delivered by a signal during semantic-rule evaluation is reported as a "defective rule" | TP1 finding 6 | Open a framework issue; predates the milestone | Framework maintainer |
| Q9 | 7 failures on main that predate the milestone, including the two `test_rf6_query_policy` dynamic-inventory tests | cea184c; TP1 review | Prove at `2d1ff4d` and `2689ab3`, list the node ids, open an issue | GND owner |
| Q10 | uv `.gitignore` release-acceptance quirk | close (caller-supplied; not in any record) | Record the reproduction and assign it to a release-readiness item | GND owner |
| Q11 | The successor ledger lives in another milestone's evidence and is rewritten in place | F2 | Name a home for the living ledger, append-only, with a successor milestone as target | Successor or code-refactoring milestone |
| Q12 | Per-phase selection misses the source-successor and query-policy pins | F3 (refuted premise) | Add both to the affected-consumer selection whenever `src/gnd` changes | Owner of the process-phase verification-selection reference |
| Q13 | Owner ratification of the post-approval deviations (D5 600 s; TP3 gaps 1 and 2; TP1 decorator; TP2 T2 guard) | F5 | Owner ratifies or rejects each | GND owner |
| Q14 | Anonymity: the M-number mutant labels and the in-repo milestone name | F6; R3-02 | Owner rules; apply one rule with declared sanitization | GND owner |
| Q15 | Unverifiable TP1 to TP3 approval hashes | F4 | Record the limit; commit specs at their gate from now on | GND owner |
| Q16 | TP1 intermittent failure, first cause not established | TP1 finding 5 | Carry as boundary; reopen if it recurs at 600 s | GND owner |
| Q17 | Release-note line for TP1 and TP2; the `gnd-dev-session` pre-state check | plan §5; F9 | Discharge in the close PR | Close author |
| Q18 | Stale status text in the README, PROJECT.md and the plan header | F7 | Discharge in the close PR (plan repair at close) | Close author |

## Verdict

**close-with-carryovers.** The condition is a close record that discharges F1 (document cea184c and re-run the TP3 gate, receipt replay and parity on `2689ab3`), discloses F2 and records F3 as a refuted premise. It must also carry Q1 to Q18 with the owners shown.
