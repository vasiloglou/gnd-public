---
milestone: why-not-near-misses
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=false, not a gnd-solve station"
scope: NM-close
date: 2026-11-02
source_base: 33c260e
gate:
  command: "see evidence/close/close-gate.txt (the cumulative NM1-NM4 gate, the wider consumer suite, the distribution-lane api pin, the docs gates and ruff on the changed product files)"
  exit: 0
  output: "1257 passed (milestone suite); 1415 passed, 1 failed then passed on rerun (consumer suite); distribution api pin 1 passed; 256 tutorial blocks; strict build; 12774 links; installed docs; ruff clean"
  note: >-
    Run over the closing tree, after every close-review fix. The broad default
    suite was started on the owner's selection ("Run it locally") and stopped
    unfinished after about 49 minutes on the owner's direction to open and
    merge without waiting; see Boundary. In the consumer suite one wall-clock
    test (test_timeout_escalates_term_to_kill_and_awaits_descendants, elapsed
    under 0.4 s) failed once and passed on three reruns and a full-file rerun
    (26 passed); the milestone's process.py change only masks output after
    the child ends. The reruns are in the same evidence file.
evidence:
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/close/close-gate.txt
    sha256: 9b7e0071d7561a697bd8246ec3753e1667787d0959d0c355106cfcec78b620b1
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/close/fidelity-three-modes.txt
    sha256: 3a986c92d5f9057c4de8a224eb453e26fd984c4d5b0b57e58817e28bd2c1338e
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/close/fidelity_three_modes.py
    sha256: 74823057db0427287f5a9c02d47c045dea873174c77dc0a030a67dc40866ed66
  - path: .gnd-planning/milestones/why-not-near-misses/notes/close-review-reader-1.md
    sha256: caa697030546f1bbc2f917eea4124d6a230a75212357a4c9cb471307ce6be7b0
  - path: .gnd-planning/milestones/why-not-near-misses/notes/close-review-reader-2.md
    sha256: 096d990285a01b1ffc21f93678f3ebda559aeb9e6add42353b858f74566d889f
  - path: .gnd-planning/milestones/why-not-near-misses/notes/close-review-reader-3.md
    sha256: 417dcaaadfdf87af64f4381eba0ac878f0d6ba7a332d179f9333c3917dcc18bc
  - path: .gnd-planning/milestones/why-not-near-misses/notes/close-review-reader-4.md
    sha256: d9dabbc2c103e745438a5cb455bfcb4ac3ee57d6d0e85d72e1578b23a7706988
  - path: .gnd-planning/milestones/why-not-near-misses/notes/why-not-near-misses-plan.md
    sha256: bf6c6ca097cb524dca082d7f1c75d5f93fea036ffabf120c19548e5eed9b9b37
  - path: src/gnd/disclosure.py
    sha256: 697526215e6326be3d27192ec91eca2e02bbfd16f6fb64fbf9295a3c5083acbe
  - path: src/gnd/witness/why_not.py
    sha256: 18220ef96a69895548c2a1c90571a4333a71e5fe72f135f84b92da0e1e64ddf4
  - path: src/gnd/witness/view.py
    sha256: e7361b120d32ae86155418d5954fb400d0981bb9e90eaf9bbee24678f4ad3d9f
  - path: src/gnd/witness/service.py
    sha256: b952b03e08df545d72c4de1c53828c1a0752647a5eebb1a770a1f46d19796d6b
  - path: src/gnd/api.py
    sha256: 9231ad93016ea96df4cc2dbd38c29f0a2f76d9f92e82e7abdc7095554e4f8c9a
  - path: src/gnd/cli.py
    sha256: 29f63bad901cb5b32f0b60f7cb10994e7b2e3e62c1502135bb5b346f75921808
  - path: src/gnd/why-not.schema.json
    sha256: 6a43565feb923eac97e89ad44a9c62268d92dca1ab454544b84517c189393756
  - path: docs/reference/why-not.md
    sha256: 53b41c14010b17468590b22ea2fc4e63019f3ca6e929925f8aa28e48512cfbb4
  - path: docs/reference/disclosure.md
    sha256: cf056b80f689e40ecd28d95065f86da8a26038e173ddba7326fcece09294e65b
  - path: docs/release-notes.md
    sha256: 2691d628fd71ba4ff58cb4c5f7ed3260499569507d801b920f21e0bce8893722
  - path: tests/test_disclosure_mode.py
    sha256: e611d73aaa9ec78090a341d186697b0692677e6c27e7ba52ecff3e19783792b1
  - path: tests/test_v61_phase2_api.py
    sha256: 1648e06cac9bd1c2ab5b7d01bdf7e22fbc7b67493ffc9a571be7caba19750532
  - path: tests/test_public_runtime.py
    sha256: 2fec3e9f868484151d9ea7199c52ed0ec179f47ba40a568b7240ef01c41fc7f9
  - path: tests/support/pyrel_application_successors.py
    sha256: 7bc2e1141dce13a9470028ed4ea29e7f20a95ecaa5432a38062c2ad924c7fe91
---

# Why-not near-misses -- milestone close

**Status: closed under auto=false. The owner authorized merging on
2026-11-02 (see Owner acceptance at the end).** This record states the close.
It does not publish or certify anything.

## What the milestone shipped

Issue #70 (GR-T8) asked, for an empty join in why-not, for the join variables
and a few values from each side that differ only by case, whitespace or
punctuation. The owner added a deployment-level disclosure mode `(o1)`.

- **Near-misses** ([reference](../../../docs/reference/why-not.md)). Every
  atom blocker carries `near_miss_count`, `near_miss_truncated` and up to five
  `near_misses` pairs: a binding that reached the step and a row of the
  blocker's fact type that agrees on every bound role once strings are
  normalized (NFKC, casefold, delete punctuation, collapse whitespace).
  Matching stays exact; status, blocker, counts, `work` and exits are
  unchanged. The search has its own inspection ceiling and truncates; it never
  fails a request. Schema `gnd-why-not/2`.
- **Disclosure mode** ([reference](../../../docs/reference/disclosure.md),
  [how-to](../../../docs/how-to/disclosure-mode.md)). `GND_DISCLOSURE` or the
  root `--disclosure`, tighten-only: `internal` returns raw values without
  per-call flags, `customer` withholds them and refuses raw requests (exit 3,
  `DisclosureRefused` in the API), unset is as at `33c260e`. Child processes
  receive `GND_DISCLOSURE=customer` only under `customer`. Every CLI leaf and
  public API callable has a row in `gnd.disclosure.SURFACES`, pasted into the
  reference page and checked against the code.
- **The spelling-gap loop:** `quoted_claims/spelling-gap.pop.json`, a
  how-to section, and the packaged `disclosure` example.

Records: [NM1](001-phase-NM1.md), [NM2](002-phase-NM2.md),
[NM3](003-phase-NM3.md), [NM4](004-phase-NM4.md). Commits `acfb9ae` (NM1),
`2f96c17` (NM2 red harness), `23e4a99` (NM2), `9fe2685` (NM3 red corpus),
`420114e` (NM3), `eb9839a` (NM4), and this close.

## Completion predicates

| # | Predicate | Result |
|---|---|---|
| 1 | oracle agreement, recorded floor, lowered-cap containment, exactness, search-off parity | holds (NM1 T-rows). Reader 1's differential fuzz (1,500 seeds, 3,000 runs) found one display mismatch (F1, a spelling inside one binding); docs fixed, kernel residual below |
| 2 | own cap, never fails, unreachable at default limits, literal counter tests | holds (NM1). The shared ceiling across clauses is now stated in the reference (reader 1 F2) |
| 3 | total disclosure table, live rows, customer withholds and refuses, internal raw, unset parity, ambient isolation, children get only customer | holds, with the close additions: `fidelity` in three modes gives one digest (NM2-Q2, `evidence/close/fidelity-three-modes.txt`); a nested in-process invocation can no longer clear an enclosing `customer` (reader 2 F2); the tutorial runner's scrub is now tested (reader 4 finding 3). Real `souffle`/`lake` runs and agent-backed `exp run`/`solve`/review were not exercised |
| 4 | `/2` on CLI and API, schema tie, normative section, how-to runs | holds (NM3). The tie-break wording is corrected at close (reader 4 finding 1) |
| 5 | every page dispositioned, new pages registered and executed, docs gates, checkpoints seen | holds (NM4; DC1, DC1b, DC2 seen) |
| 6 | gates, reviews, sweep, PR | holds: four phase gates and this close gate, phase reviews, four close readers, the sweep below and the PR. Owner acceptance is separate |

## Close review (four local readers, NM-D9)

Reports: [reader 1](notes/close-review-reader-1.md) (near-miss correctness),
[reader 2](notes/close-review-reader-2.md) (disclosure as a security control),
[reader 3](notes/close-review-reader-3.md) (protocol, evidence, records),
[reader 4](notes/close-review-reader-4.md) (test falsifiability, docs
accuracy). All four approve; no blocking finding.

| Finding | Severity | Disposition |
|---|---|---|
| R1-F1 a sample can show `1` where the binding was introduced as `1.0` | hardening | docs fixed; kernel change residual (display only) |
| R1-F2 the inspection ceiling is shared by the whole request | completeness | docs fixed |
| R1-F3 whitespace is `str.split()`'s, wider than Unicode's | hardening | docs fixed |
| R2-F1 customer mode also confirms an exact match through status, exit and step counts | completeness | docs fixed; NM-R6's "one signal" noted as superseded in the plan close note |
| R2-F2 a nested value-free invocation cleared an enclosing `customer` | hardening | fixed in `disclosure.invocation`; regression red on the old line, green after |
| R2-F3 the threat model did not name program-running arguments | hardening | docs fixed |
| R3-H1 the NM4 record cites the amended-away 8bc5039 | hardening | the NM4 commit is `eb9839a`; 8bc5039 was amended 28 s later, changing only the record, README and gate file. The census result holds at `eb9839a` (reader 3 re-ran it) |
| R3-H2 the NM3 red corpus `9fe2685` was staged after implementation | hardening | accepted and stated: corpus-first rests on `corpus-red.txt`, which reader 3 reproduced (75 failures) |
| R3-H3 approval-before-code is not git-evidenced for NM1 and NM4; pre-tag approval digests are uncheckable | hardening | accepted and stated: those approvals share commits with the code, so the order rests on the records' quoted approvals |
| R3-C1 open questions need dispositions | completeness | the sweep below |
| R3-C2 predicates 3 and 6 partly evidenced | completeness | fidelity three-mode run added; the rest stated in Boundary |
| R3-C3 stale plan lines | completeness | plan close note appended |
| R3-C4 commit-grammar slips | hardening | accepted; history is not rewritten. The close commit follows the grammar |
| R3-C5 `tests/support/pyrel_application_successors.py` not digest-bound | completeness | bound in this record's evidence |
| R4-1 the tie rule example was wrong | hardening | docs fixed: the projection whose canonical encoding comes first |
| R4-2 `test_t15` is a tautology | hardening | test now also requires every case group to be used; the comment states the discharge is the named tests |
| R4-3 the runner scrub mutation survived | hardening | fixed by a test that fails with the scrub entry removed |
| R4-4 one test asserts on the golden | completeness | accepted (anchored by T5 and `test_public_why_not` T1) |
| R4-5 release-note wording on children | completeness | fixed |
| Close gate: `test_public_all_is_exact` failed | regression | NM3 added `DisclosureRefused` to `gnd.api.__all__` and updated `test_public_api.py` only; the pins in `test_v61_phase2_api.py` and the distribution-lane `test_public_runtime.py` are updated |

## Question sweep

| ID | Question | Disposition |
|---|---|---|
| NM1-Q1 | representative wording | resolved in NM3 docs, corrected at close (R4-1) |
| NM1-Q2 | `samples` first-seen vs `near_misses` minimum | resolved: NM3 D3 (a), documented |
| NM1-Q3 | flag-on census over the WN2 goldens | resolved: NM3 T1 |
| NM2-Q1 | `doccheck` every-mode | resolved: NM4 D1 (a) |
| NM2-Q2 | `fidelity` in three modes | resolved: `evidence/close/fidelity-three-modes.txt`, one digest in all three |
| NM2-Q3 | RF1 goldens no longer reproduce from a fresh capture | deferred to a maintenance pass (owner) |
| NM3-Q1 | installed-docs command needs `--out` | resolved in the plan close note |
| NM4-Q1 | bound the IK census at its milestone's end | deferred to a maintenance pass (owner) |
| R1-F1 residual | compare every spelling that met a binding | deferred (display only) |
| O14 | reporter acceptance | note posted on issue #70 on the owner's approval; acceptance is the reporter's, after merge |

## Boundary -- what the milestone does NOT establish

- **The broad default suite did not finish.** It ran about 49 minutes and was
  stopped on the owner's direction; no result is claimed. The close gate
  covers the milestone's tests and their consumers.
- **Not exercised:** real `souffle` and `lake` toolchains, Lean compile, and
  real agents for `exp run`, `solve` and review under each mode.
- **Customer mode is a lock for forwarded arguments, a guard in-process.**
  Status, exit codes and counts still confirm exact matches (documented).
- **Each review is one reader**; the four close readers read `eb9839a`. The
  close fixes carry no review opinion.
- **One load-sensitive timing test** failed once in the close gate and
  passed on every rerun; it is recorded as a flake, not as fixed.
- **Ruff** reports no finding on the changed product files; the
  `.gnd-planning` helper scripts and files outside the milestone carry
  pre-existing or unlinted findings.

## Merge with main

None needed: main has not moved since the base `33c260e`.

## Owner acceptance

2026-11-02, by the owner, in the session that ran this close: "yes", in
answer to "Shall I go ahead with all five steps, merge included?" (stop the
broad suite, run the focused close gate, write this record, commit, push and
open the PR, merge if the gate passes). It authorizes merging the PR that
carries this record; it does not certify or publish anything, and the
deferred questions above stay open.
