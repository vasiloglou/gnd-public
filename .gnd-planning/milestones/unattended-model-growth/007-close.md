---
milestone: unattended-model-growth
station: close
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: close
date: 2026-11-09
source_base: "dd3c35a5 (main after PR 151)"
gate:
  command: "bash .gnd-planning/milestones/unattended-model-growth/evidence/close/close-gate.sh"
  exit: 0
  output: "4237 passed, 42 deselected in 961.09s (0:16:01); pytest exit 0; 310 tutorial blocks passed; strict build finished; 15232 local links/assets/anchors checked; ruff All checks passed!"
  note: "the union of the UG1 to UG4 phase gates and their impact closures (107 modules, listed in the script), the full tutorial run, the strict site build, the link check and ruff, over the closing tree with the close fixes"
parity:
  command: "uv run python .gnd-planning/milestones/unattended-model-growth/evidence/close/capture_parity.py OUT.json, from a checkout of each tree"
  result: "6d7b5327 vs ad454305: 596 common rows, 0 differ; 12 rows only on ad454305 (UG3's six new fixture models, two formats each)"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "the broad historical lanes are outside the milestone's impact closure"
evidence: 
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/unattended-model-growth-plan.md, sha256: 17eb714d302486ab85a79a43b3ba3ca6a547253d56e5c598e6f791d9ad816092}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/close-review-reader-1.md, sha256: 5d55353e35093b2ff83d965a246e452780e4396a3d718bc12937fa4fc3ec3de0}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/close-review-reader-2.md, sha256: 016a5024cf40735158ef99ab68f6323b69982889ee1ff57e6893593ea25b6392}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/close-review-reader-3.md, sha256: b831fc233be037ba1aa284b1ce5defb2b7a790a32013db5a3379fecd68749e32}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/close-review-reader-4.md, sha256: ac4f773fbfb8ee8ccf1e66fa70e76fea08e9d0199a946a624f260c8de4607bc9}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/ug4-issue-followups.md, sha256: a1cf1543cf3662574d259d6a083f6973c7ad713ec40a8d398cc0e9068dcb24a9}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/close/close-gate.sh, sha256: 08882b2607a4e613ff2cb23b754aeb118c1c10aece0e49bf50de33bc89358000}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/close/close-gate.txt, sha256: cc3489b9ad09187331555b1afd6d301b05d284e7f3e354f3aec4902793ba7c95}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/close/capture_parity.py, sha256: c2ccb0f351cb08e7247d60ecf2e23dd2412c94783d89f4f2aca02dfed058d072}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/close/parity-6d7b5327.json, sha256: 4de308e586e858a16bb7d831369e6a55929e6ee52ad16487816f8fb02435a7ea}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/close/parity-ad454305.json, sha256: c80b4a49974eadfd5680c8d8d1463b9009f0e1375cef0ca57a9bb548af4c587a}
  - {path: src/gnd/evolve/policy.py, sha256: 8f7782e7e559c68c06df76c867b69a9b1f2a2db072bb786104e7af95337ee619}
  - {path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md, sha256: 5a8a1bbb90cec546f88bc169ac7400aad045d510c93434f5fbe858469eab0f2d}
  - {path: src/gnd/skills/gnd-orm-core/references/representation-format.md, sha256: 19b3ea8bcceaf673abb1af082d968a2236965d7c0438eae28efe2a23283a0320}
  - {path: src/gnd/skills/gnd-model-from-text/references/unattended-growth.md, sha256: 6f217fc641801b9ad188ddbb7b7bb2ea796f889b2eaafc121c6e9e05d387545d}
  - {path: src/gnd/skills/gnd-model-from-text/SKILL.md, sha256: e92c9ec88221a0f4686b724b624c3628074783346ebc6a0f16b1c480932b3331}
  - {path: src/gnd/skills/gnd-model-evolve/SKILL.md, sha256: 2d9a26acbbe113395c94a77e9dc2380581ec8e21ca12e46c37537849b3be9e80}
  - {path: docs/agents/evolve.md, sha256: 236a6851524112a1d93099c06515ca7e95967a44ba37229609e87ddbc5b68b0d}
  - {path: docs/agents/model-from-text.md, sha256: 74becdec7e168d6a16b836e232398af5a20a6e154414b3b09cc33f8c051a9ca9}
  - {path: docs/how-to/grow-a-model.md, sha256: dc246f2d2737d6466e9802d0160c0ecb1bc996bc087b34b7c8a740e87cc0970a}
  - {path: docs/reference/evolve-policy.md, sha256: 67bab363448f6e069e947de7e47d655a085518e3f55f6b05df4304292883481a}
  - {path: docs/release-notes.md, sha256: 3a6316addd0b9b39cd0c936c8d3e851bf09f5c8cc47adf0d02002a12cc622ddb}
  - {path: tests/test_evolve_population_check.py, sha256: 78c77d7f4a3e9e78bb50fd1727cde08e0503daadcf52b505cfb5be0390eae838}
  - {path: tests/test_evolve_source_document.py, sha256: 9166a7d53413c7f7b368f5e1ad6aaf7653a61c12fa6647e478a6b3a550226876}
  - {path: tests/test_unattended_span_coverage.py, sha256: 46e17355a3266ea0bc3d7ba34c0e9222c5e4e03164eb2aa0bbff075bd98521d5}
---

# Unattended model growth -- milestone close

**Claim.** The open parts of issues 74, 75, 76 and 104 are built and documented. Issue 104
item 5's second option is built: `gnd evolve --policy additive --check-population FILE` admits a
`proposed` + `deontic` constraint on a populated fact type that the supplied population
satisfies, relative to that file (UG2). A growth round declares its own source document through
`gnd evolve`, and `gnd validate --document` counts the spans it did not re-hash, with
`--require-documents` to fail closed (UG3). The packaged skill and the docs describe the shipped
loop, with one home per statement (UG4). Flag-free validate and evolve outputs are
byte-identical across the milestone's code PRs (the parity table). The close review found one
blocking defect, fixed here with regressions.

**Authority.** Plan r1.2 approved by the owner at the plan gate (2026-11-07, [001-plan.md](001-plan.md)).
Every phase spec was approved by the owner (`auto=false`), quoted in each spec's status line.
The close was requested by the owner on 2026-11-09, quoted: "close the milestone too". The
close review instrument is UG-D1 (a): four local readers, with the maintained six-seat panel
stated as the project's bar and not run. **Owner acceptance of this close, and the merge of its
pull request, are the owner's and pending.**

## Phase records

| Phase | Record | Merged | Phase gate |
|---|---|---|---|
| plan | [001-plan.md](001-plan.md) | PR 123 (`b5fda4fd`) | plan review, four local readers |
| UG1 acceptance replay (test-only) | [002-phase-UG1.md](002-phase-UG1.md) | PR 123; dispositions marked posted in PR 139 | as recorded |
| UG2 population-checked admission | [003-phase-UG2.md](003-phase-UG2.md) | PR 147 (`5c6a0c5f`) | 2071 passed |
| UG3a span counts, `--require-documents` | [004-phase-UG3a.md](004-phase-UG3a.md) | PR 149 (`ad454305`) | 4007 passed |
| UG3b `source-document` operation | [005-phase-UG3b.md](005-phase-UG3b.md) | PR 149 (`ad454305`) | 4007 passed |
| UG4 documentation and dispositions | [006-phase-UG4.md](006-phase-UG4.md) | PR 151 (`dd3c35a5`) | 501 passed, docs gates |
| close fixes | this record | branch `claude/ug-close` | the close gate |

Each phase diff had one independent reviewer (Codex CLI); **one reviewer is one reviewer**, and
none of the phase reviews was a panel.

## Completion predicates (plan "Problem and completion predicates")

| # | Predicate | Result |
|---|---|---|
| 1 | every ask of 74, 75, 76, 104 has a matrix row; each `met` cites an executable result; the three-round replay passes | holds (UG1). Close delta below: row 74 is "met with deviation" for two exemptions (`common-sense`, and `induced` since PR 150); row 76's readings and reference modes are cited to `tests/test_evolve_shape_matches.py` (R3-F6); the rows marked open at UG1 are met by UG2 and UG3, cited below |
| 2 | 104 item 5 second option built, with apply re-checking and a failing case | holds after the close repair of the subject rule (R1-F1): a constraint hosted on a fact type also ranges over what it reaches. UG2 corpus C01 to C11c, regressions R1 to R9 and the close regressions |
| 3 | a round declares its document through `evolve`; unattended validation can fail closed; defaults unchanged | holds (UG3 corpus A1 to A6b, B1 to B8; parity table). The walked locations are object types, fact types, constraints and sample rows; spans on operations and obligations are neither checked nor counted, now stated (R2-F1, UG-close-Q2) |
| 4 | docs and skill say the final state in one home each, including acting on a shape match | holds (UG4), with the close qualifiers (R3-F4, R3-F5) |
| 5 | each issue has a drafted, evidence-citing disposition; the agent closes nothing | holds: [ug1-issue-dispositions.md](notes/ug1-issue-dispositions.md) (posted) and [ug4-issue-followups.md](notes/ug4-issue-followups.md) (drafted, not posted). No agent in this milestone's records closed an issue; the tracker state is observed below |
| 6 | focused gates, independent reviews, refactoring reviews, records per phase; a close gate; owner acceptance separate | holds; owner acceptance pending |

**Matrix delta (UG1 rows marked open, now met):** 74 unchecked spans: UG3 A2a to A5
(`tests/test_unattended_span_coverage.py`); 74/104 a round declares its document: UG3 B1
(`tests/test_evolve_source_document.py`); 76 what the host does with a match: the procedure's
"Acting on a shape match" (prose, inspected); 104 item 5 second option: UG2 C01
(`tests/test_evolve_population_check.py`). No committed test composes these into one loop
(R3-F8); close reader 3 ran the composed loop end to end in scratch with shipped commands only
(reader 3's report, R3-F8 tables).

**Tracker state, observed 2026-11-09.** Issues 74, 75 and 76 are closed as completed
(2026-11-08 14:44:50, :53 and :55 UTC), each with a disposition comment posted at closing and a
second, near-identical one at 17:59 UTC; issue 104 is open. The UG1 dispositions note and record
004 say "No issue was closed" and "Issue 74 is not commented on or closed"; those statements were
wrong when written (R4-F2) and are corrected here, not edited in place.

## Close review (four local readers, UG-D1 (a))

[Reader 1](notes/close-review-reader-1.md) (UG2 admission), [reader 2](notes/close-review-reader-2.md)
(UG3 as a security control), [reader 3](notes/close-review-reader-3.md) (UG1 matrix, UG4 docs and
dispositions), [reader 4](notes/close-review-reader-4.md) (protocol, evidence, records). Reader 1:
reject (one blocking finding; approve-with-fixes once fixed). Readers 2 to 4: approve-with-fixes.
Every finding was reproduced or checked by the author before it was dispositioned. Reader 2's
longer report was not retained; its final message is.

| Finding | Class | Disposition |
|---|---|---|
| R1-F1 a fact-type-hosted constraint's subjects were its host alone; a host-scoped object-type `value` or a foreign `role_ref` was admitted on data it never checked, and in the flag-free MG2 walk on an empty host | blocking | fixed: `ConstraintSubjects.of` adds the host to the reach the model-hosted rule computes; the contract's "Populated" paragraph generalised; plan close note `(c1)`. Three regressions fail on `dd3c35a5` (`test_close_r1_f1_*`, measured) |
| R1-F2 a deeply nested YAML population takes super-linear time before band 3 | hardening | deferred, UG-close-Q1 (the shared ruamel loader; owner) |
| R1-F3 eligibility halves and the missing-host arm untested | completeness | eligibility: `test_close_r1_f3_*` (three cases); the missing-host arm stays untested (accepted) |
| R2-F1 spans on operations and obligations are neither checked nor counted | hardening | documented in "Unattended source"; UG-close-Q2 (owner: extend U7 and the walk, or refuse such spans) |
| R2-F2 a near-miss mode spelling makes `--require-documents` a no-op | hardening | accepted residual: the flag is defined as a no-op outside the mode, and the near-miss already warns (`semantic:unattended-u1`) |
| R2-F3 a proposal that changes nothing exits 70 (`BlastRadiusReport` min_length) | hardening | deferred, UG-close-Q3: the class predates UG3 (a no-op element modify on `5c6a0c5f` too) |
| R2-F4 an unreadable `--document` on a redacted model emits an unprojected payload | hardening | carried as UG3-Q1 |
| R2-F5 `--document` refusals on redacted or reference models now projected, outside UG-R1's carve-out | completeness | stated in the release notes and the plan close note; 108 of the 114 differing payloads were schema-invalid before |
| R2-F6 two counting rows had no count assertion | completeness | `test_close_r2_f6_*` |
| R2-F7 the label and `before` digest checks masked by later layers | completeness | `test_close_r2_f7_*` (two cases) |
| R2-F8 "No operation reorders the list" was wrong for delete then add | completeness | contract reworded; `test_close_r2_f8_*` |
| R2-F9 duplicate digests pass U1 | informational | UG3-Q2, owner |
| R3-F1 / R4-F2 milestone files misstate the tracker | blocking (text) | corrected here, in the README and in the follow-ups note |
| R3-F2 #74 follow-up missed PR 150's `induced` exemption | blocking (text) | follow-up sentence added; matrix delta above |
| R3-F3 "this phase's PR" placeholders | hardening | replaced by PR 151 |
| R3-F4 "strengthening-only" narrower than the contract | hardening | the contract's words in the procedure and the #104 follow-up |
| R3-F5 three unqualified statements | hardening | qualified: `grow-a-model.md` intro, `docs/agents/model-from-text.md`, `evolve-policy.md` "The guarantee's condition" |
| R3-F6 row 76 cites ids-only tests | hardening | matrix delta cites `tests/test_evolve_shape_matches.py` |
| R3-F7 weak assertions; the guard checks bare options against the union | hardening | accepted: the two assertions predate the milestone and their tests assert elsewhere; the guard's union check is a stated limit |
| R3-F8 no committed composed-loop test | completeness | accepted, with the per-phase corpus citations and reader 3's scratch run |
| R3-F9 issue attribution of the locator | completeness | "issues 74 and 104" in the release note and README |
| R4-F1 README status stale | blocking | rewritten |
| R4-F3 code before recorded approval | blocking (disclosure) | disclosed below |
| R4-F4 `002` edited after its commit; no open-questions sections in `001`, `002` | hardening | noted; their open questions are swept below |
| R4-F5 commit-message deviations | hardening | accepted, listed below; history is not rewritten. This close commit puts the record path before the trailer |
| R4-F6 elided gate commands; junit digests not checkable | hardening | this close gate lists every module in a committed script; the phase junit digests describe scratch files and are not checkable from history |
| R4-F7 `006` cites 5 of 11 changed files; the PR 150 merge into UG4 unreviewed | hardening | the UG4 files are cited by digest in this record's evidence; the close gate runs over the merged bytes |
| R4-F8 four cited digests differ on main | completeness | parity section below |
| R4-F9 one-reviewer statement placement | hardening | boundary below |
| R4-F10 fixes without a pre-fix-failing regression | hardening | listed below |
| R4-F11 UG2-Q3 has no target milestone | hardening | swept below |
| R4-F12 `gnd doctor --project` exit 11 | hardening | measured in the main checkout too (exit 11, 6 collisions): machine-local link receipts, not this milestone; UG4-Q1 to the owner, local |
| R4-F13 plan text departures | completeness | plan close note `(c1)` |
| R4-F14 close record name | completeness | `007-close.md`, scope `close`, consistent with `001-plan.md`; S18 to the owner |
| R4-F15 `002`'s skill field | completeness | noted |
| R4-F16 close evidence untracked | completeness | committed with this record |

**Disclosure (R4-F3).** "No code before recorded spec approval" held for the UG2 and UG3 spec
gates, each committed with no source change before the first source edit. UG3 part A's code
(`747c1ba5`) was committed before the corpus approval was written into the spec (`2dea8a81`); the
owner's "Approve the corpus" came first in the conversation, but the repository does not show
it. In UG1, UG2's corpus gate and UG4, the ruling and the work landed in the same commit, so
git cannot show the order.

**Commit-message deviations (R4-F5):** the plan and UG1 commits use scope
`unattended-model-growth`; `1b8540d5` has no body; `b3a4fda4` names its record mid-body; in
`8e7819a1`, `a06d1f6f` and `c56781b6` the record path follows the Co-Authored-By line, so git
does not parse the trailer; twelve subjects exceed 65 characters with their prefix.

**Fixes without a pre-fix-failing regression (R4-F10):** UG1 findings 2 and 3; UG3 finding 6
(fails on the old code structurally, for missing seams); UG2 finding 9 (passes before, declared);
UG4 findings 1, 3, 4, 5 (prose); the close's text fixes.

## Close gate

| Command | Result |
|---|---|
| `bash evidence/close/close-gate.sh` (107 modules, listed in the script) | `4237 passed, 42 deselected in 961.09s (0:16:01)`, pytest exit 0; `310 tutorial blocks passed`; build finished; `15232 local links/assets/anchors checked`; ruff `All checks passed!`; script exit 0 (`evidence/close/close-gate.txt`) |
| the first run, before the close fixes | `4227 passed, 42 deselected in 966.69s`; 310 tutorial blocks; strict build; 15232 links; ruff: one unused `noqa` in the capture script, fixed |
| close regressions on `dd3c35a5` (before the fix) | R1-F1's three cases fail (`assert [] == ['constraint.populated.add']`) |
| anonymity: UG1's digest-set method over the milestone diff and commit messages | 0 hits; positive control found (readers 3 and 4, and the author) |

## Parity (UG-R1)

`capture_parity.py` ran `gnd validate --format json|text` over every tracked `*.orm.yaml`,
`gnd validate --document` over the MG5 fixture, the growth example's two rounds (preview with
the tutorial's flags and without a policy, apply of round 1) and the bookrec genre preview, in
checkouts of `6d7b5327` (main before PR 147) and `ad454305` (main after PR 149). Result: 596 rows
on both, **0 differ**; 12 rows exist only on `ad454305` (UG3's six new fixture models).
`evidence/close/parity-6d7b5327.json`, `evidence/close/parity-ad454305.json`. The plan named
`12daa5b7`; about twenty unrelated PRs merged after it, so the base was moved to the merge parent
of the first code PR (plan close note `(c1)`). PR 150 (not this milestone) changed U5 after
`ad454305`; reader 2 found that it breaks no UG3 guarantee. Reader 2's wider run (2240 validate
runs) found the R2-F5 correction and nothing else.

**Cited digests that no longer match main (R4-F8):** `001`'s plan file (status-only edits after
`314dc019`, declared); `002`'s acceptance replay (UG3b's comment-only T12 change) and the
dispositions note (marked posted); `004`'s `_unattended.py` (PR 150). The current-byte claims
rest on this close gate.

## Question sweep

| ID | Question | Disposition |
|---|---|---|
| UG-Q1 | evolve lane may call the checker | resolved (UG2; layering and arch gates pass) |
| UG-Q2 | option and flag names | resolved (`--check-population`, `--require-documents`) |
| UG-Q3 | how the population arrives | resolved (UG2-D1, D2: one option, one file) |
| UG-Q4 | census of `tests/` | resolved (answered at plan review) |
| UG-Q5 | schema versions for the locator | resolved (UG3-D10 (a): version 3 only; proposals and records) |
| UG-Q6 | `project.md` component-index contradiction | deferred to the owner (maintainer); phases applied the `dev/components/` reading |
| UG-Q7 | downstream tracker labels | deferred to the owner |
| O15 / MG3-Q2 | ADD/DELETE-only proposal fails `BlastRadiusReport` | carried, not owned (and see UG-close-Q3) |
| MG-close rows | model-growth-guardrails sweep rows | carried to the owners that close assigned |
| O16 / UG-D4 | subtype links carry no status | resolved: ruled (a), stated |
| PR1-D1, PR1-D2 | exit for a changed population; strict flag on a plain model | resolved (11; no-op) |
| PR1-H5 | verbatim plan-gate message and re-confirmation | accepted: relayed, recorded in `001-plan.md` |
| PR1-C7 | UG4-C4 has no executable result | accepted: inspected |
| PR1-SR | no confirmation round on plan r1.2 | accepted residual: r1.2 carries no review opinion |
| UG2-Q1 | `popvalidate.py` `OverflowError` on huge integers for a Float role | deferred to a maintenance fix (owner); UG2 maps it at its own boundary |
| UG2-Q2 | `_evolve_service_exit` maps by message substring | deferred to a refactoring pass on `cli_service.py` (owner); UG3's two messages carry only validated hex |
| UG2-Q3 / UG1 refactor | UG1's test file imports private helpers | deferred to a test-helper maintenance pass (owner); not blocking |
| UG3-Q1 / R2-F4 | unprojected error payload for an unreadable `--document` | deferred to a maintenance fix (owner) |
| UG3-Q2 / R2-F9 | U1 accepts a digest declared twice | deferred to the owner: refusing it changes validation of existing unattended models |
| UG3-Q3 | `validate --document` walks spans twice | deferred: refactoring candidate, accepted cost (linear, capped) |
| UG4-Q1 / R4-F12 | stale local link receipts (doctor exit 11) | owner, local |
| UG4-FU | follow-ups drafted, not posted | owner (UG-D0, UG4-D2 (a)) |
| UG-D0 | owner closes the issues | 74, 75, 76 closed; 104 open, the owner's |
| UG-close-Q1 / R1-F2 | deep YAML nesting in a population is slow before band 3 | new; deferred to a maintenance fix of the shared loader (owner) |
| UG-close-Q2 / R2-F1 | spans on operations and obligations are not checked or counted | new; owner: extend U7 and the walk, or refuse them in the mode |
| UG-close-Q3 / R2-F3 | a no-op proposal exits 70 | new; deferred to a maintenance fix (owner), pre-existing class |
| UG-close-Q4 | the checker scopes a hosted constraint to its host (`universe._scope_fact_types`), so a hosted `value` with a foreign `role_ref` is evaluated over the host only | new; the policy now refuses it on populated data (R1-F1); the checker's scope is outside this milestone (owner) |
| S10 to S17 | plan-text departures | repaired in the plan close note `(c1)`, or recorded there |
| S18 | close record name | chosen `007-close.md`; the owner confirms |

## Refuted premises

- The policy's subject rule covered model-hosted constraints only; fact-type-hosted ones reach
  further (R1-F1). Repaired.
- UG-R1's base `12daa5b7` could not isolate the milestone; repaired to `6d7b5327`/`ad454305`.
- "No operation reorders the list" (UG3 contract text) was false for delete then add (R2-F8).
- "No issue is closed" (README, UG1 dispositions, record 004) was false since 2026-11-08.

## Boundary -- what the milestone does NOT establish

- **Owner acceptance of this close and its merge are pending.** No release, publication or
  certification is claimed.
- **Each phase review was one reader**; the four close readers read `dd3c35a5`. The close fixes
  carry no review opinion.
- The maintained six-seat panel did not run for the plan or the close (UG-D1 (a)).
- The broad historical lanes (`-m "evidence or census"`) did not run.
- `--check-population` admits relative to the supplied file; a span proves an excerpt exists,
  not that it supports the claim; a shape match is a candidate, never a verdict.
- `gnd doctor --project` exits 11 on this machine for local link receipts.
