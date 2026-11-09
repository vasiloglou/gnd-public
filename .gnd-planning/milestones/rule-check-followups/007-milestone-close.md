---
milestone: rule-check-followups
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=false, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-08
source_base: 859b852d
gate:
  command: "~/fu-shards/fu-shards.sh close-859b852d 859b852d on beast-3: the full default lane, six round-robin shards, at main 859b852d"
  exit: "1 (the 2 pre-existing uv-pin errors and 1 failure introduced on main by PR 135)"
  output: "main 859b852d: 18164 passed, 1 failed, 2 errors; merge base 6651e5a4: 2 errors; the one new failure is not this milestone's"
  note: >-
    Plan section 9's close row: the full suite against the merge-base record
    (main 6651e5a4, evidence/FU1/full-suite-main-6651e5a4.txt). Main also
    merged other milestones' PRs in that range (report-output-fidelity,
    rule-check-release, PR 135), so the comparison is of the observed
    failing-test sets, not of this milestone's commits alone. This close's
    own changes are planning text and one regenerated component-index page.
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "not selected at this close; the broad historical lanes are outside the milestone's impact closure"
evidence:
  - path: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md
    sha256: bf08412eb4cfad1954e26f96dfaa4084d95013bc5c772ef1d2d4f34bbab4dcfc
  - path: .gnd-planning/milestones/rule-check-followups/001-plan.md
    sha256: c4553023c0885759296ae4c64d886130ca0654ba49af4cacb06b0b9037db1fb0
  - path: .gnd-planning/milestones/rule-check-followups/002-phase-FU1.md
    sha256: 4d82ac98c004c33ac6ee9072061e4766815f024d3c981373a540b4aaeb88aae6
  - path: .gnd-planning/milestones/rule-check-followups/003-phase-FU2.md
    sha256: bc62e22381bf35e979553a2f41810f641773f66e496d9ed763eb36441d7fafef
  - path: .gnd-planning/milestones/rule-check-followups/004-phase-FU3.md
    sha256: 0c4ba9f6222eb14b79c010396a6580b5c20034bdc0ad78851a0042bad3b86146
  - path: .gnd-planning/milestones/rule-check-followups/005-phase-FU4.md
    sha256: 40cb1777d11c750e541edff142a9e0ec7aff3e9b46e69bb603bbfa3771f70377
  - path: .gnd-planning/milestones/rule-check-followups/006-phase-FU5.md
    sha256: 5e5503caf3f4374997dd3197d1be6b8487e6d3ab1bfc76e4a3e5df83372bd48b
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU1/full-suite-main-6651e5a4.txt
    sha256: 7c5d2cca18cf62b9478c41897e5a863116a0fba5c4cadfc2a5b9b010ebc4a9b7
  - path: .gnd-planning/milestones/rule-check-followups/evidence/close/full-suite-close-859b852d.txt
    sha256: 02881c09779c61236429d9d58028be5729fc64e71247d064992381c1631955f8
  - path: .gnd-planning/milestones/rule-check-followups/evidence/close/issue-states.txt
    sha256: 30dcdb9bcc0de92a8e51709517016a07c6d4a38f997628e0d7d228ff8d0b1b2d
  - path: .gnd-planning/milestones/rule-check-followups/notes/close-codex-review.md
    sha256: f42190cfc9125ed35fd87dbd7721954c5d7fbe886ca5e41e41edc4b4a2301a1c
  - path: .gnd-planning/milestones/rule-check-followups/evidence/close/fu1-o1-probe.txt
    sha256: 1fd4a45160b29c863a26ba3ca8f678f44a42af4d5880582cee835fd29829948a
---

# Claim

All five phases of rule-check-followups (FU1-FU5) are on main, each with an
owner-approved spec, a record with verbatim focused-gate output, one
independent reviewer and an owner-merged PR (121, 126, 128, 129, 134).
Completion predicates 1, 3, 4, 5 and 7 hold on main by the evidence the
phase records bind and this sweep. Predicate 2 holds only for copies of
validated populations, and predicate 6's open-state clause no longer holds
for issue 112, which another milestone closed; plan §11 proposes both
qualifications for the owner's close ruling (review K1, K2). At main 859b852d the full default lane fails the two pre-existing uv-pin
errors and one test that PR 135 (outside this milestone) broke after FU5
merged; it is recorded below and goes to a separate fix by owner ruling.

## Phases

| Phase | Issues | Record | Focused gate | Review (one reviewer, Codex) | PR, merge |
|---|---|---|---|---|---|
| FU1 | 113 | [002](002-phase-FU1.md) | 108 passed | `revise`, 2 findings: R1 fixed, R2 deferred (FU1-O1) | 121, 12daa5b7 |
| FU2 | 115, 116 | [003](003-phase-FU2.md) | 79 passed | `revise`, 2 findings, both fixed | 126, 1e63aeb5 |
| FU3 | 119 | [004](004-phase-FU3.md) | 46 passed | `revise`, 5 findings: R2 fixed, R1 boundary, R3-R5 wording | 128, df5753bf |
| FU4 | 117 | [005](005-phase-FU4.md) | 24 passed | `revise`, 7 findings: R1, R2, R6, R7 fixed; R3, R5 boundaries; R4 not reproduced | 129, 6ed86d90 |
| FU5 | 114 | [006](006-phase-FU5.md) | 2540 passed | `revise`, 1 finding, fixed | 134, 0e093158 |

## Completion predicates

| # | Predicate (plan) | Evidence | Holds |
|---|---|---|---|
| 1 | a version-7 report with `term:*`-unchecked derivations validates; no report's bytes change | FU1 corpus and gate; the schema is byte-identical to main's own fix (PR 122) after the FU1 merge amendment | yes |
| 2 | a combined or reference-bound population keeps its `label`; no copy carries `producer` without `source: tool-output` | FU2 T1-T3 | **qualified**: holds for copies of validated populations. `Population.model_construct(model='m', source='fixture', producer='x', facts={}).model_copy()` keeps `fixture x` (reproduced at the close, review K1): `model_construct` is unvalidated and a copy without `update` is not revalidated (FU2 boundary). Plan §11 row 2 |
| 3 | under `--rule-ids`, a failing `acyclic` ring over an exact-term derived fact type lists the pairs the checker judged, pinned by a corpus case | FU3 corpus `fu3-derived-ring` | yes, for `acyclic`; the combined variants have no case (FU3 boundary) |
| 4 | the two timing tests no longer fail under the six-shard run, without loosening beyond the ruling | FU4 T5 (120 passed under load) and mutants | yes, at the loads measured (FU4 boundary) |
| 5 | the cycle helpers are retired or kept per RF-D5 | FU5: retired by owner ruling, negative import tests | yes |
| 6 | issues 111 and 112 stay open, split out; this milestone does not close them | 111 open; 112 closed on 2026-11-08 by the report-output-fidelity milestone (PRs 124, 127), not by this one (evidence/close/issue-states.txt) | **qualified**: this milestone closed neither; the open-state clause is superseded for 112 by its external closure (review K2). Plan §11 row 3 |
| 7 | approved spec, verbatim focused gate and one independent reviewer per phase; the close disposes every open question and closes the delivered issues | the five records; the sweep below; issues 113-117 and 119 closed (evidence/close/issue-states.txt) | yes |

## Gate output (verbatim)

Full default lane, six shards on beast-3, at main 859b852d:

    shard0: 2286 passed, 263 deselected                  shard exit=0
    shard1: 2285 passed, 98 deselected, 2 errors         shard exit=1
    shard2: 1 failed, 3294 passed, 77 deselected         shard exit=1
    shard3: 2879 passed, 127 deselected, 1 warning       shard exit=0
    shard4: 3172 passed, 104 deselected                  shard exit=0
    shard5: 4248 passed, 129 deselected                  shard exit=0
    total: 18164 passed, 1 failed, 2 errors
    failing list sha256 049f48f52bf719061d2dabeaa60ee75df43421013f5d9346a754997850a1a8a6
    comm -13 base.fail close.fail: tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_cmd_transition]
    comm -23 base.fail close.fail: empty

The merge base 6651e5a4 failed only the two `tests/test_public_optional.py`
uv-version pins (sha256 8261732b...9c20a). The one new failure is an RF5
body-identity pin on `gnd.cli._cmd_transition`, which PR 135 (9ff471a7,
merged after FU5) changed without an RF5 body successor:

    uv run pytest -q -p no:cacheprovider "tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged"
    at 859b852d: 1 failed, 115 passed
    at c104644d (main before PR 135): 116 passed

None of this milestone's files is involved. The FU5 known red
(`test_development_scaffold.py`) passes at 859b852d.

Component index, whole milestone:

    python3 scripts/components_index.py changed --base 6651e5a4 --strict
    before regenerating: fail: stale or missing: dev/components/modules/_root.md
    after python3 scripts/components_index.py write:
    changed against 6651e5a4 (6651e5a): 403 file(s) differ; 0 to fix, 0 warning(s), 10 to reread
    exit=0
    with this close's own files added: 408 file(s) differ; 0 to fix, 0 warning(s), 10 to reread

After main merged PR 138 (ROF4), which regenerated the same page, the
merge of main into this branch took main's page; `write` reproduces it
byte for byte and `components_index.py --check` exits 0, so the close PR
no longer changes it. The stale page predates this close and is not this milestone's: line drift
in `output.py` and the model-identity module from other milestones (PR 135
noted it). The regenerated page changes line numbers only. Of the 10
rereads, the seven subsystem entries over `model.loading` were reread at
FU2 and `checker.evaluate` with `subsystem.check` at FU5, each recorded
accurate; `infra.output`, `export.verification` and
`cli.checking_command` changed through other milestones' files and are
theirs.

FU1-O1 probe (evidence/close/fu1-o1-probe.txt), the v70-phase4 case
`P02-opaque-claimed` at 859b852d:

    gnd check positive.orm.yaml p02.pop.json --format json                        exit 4, version 7,  derivation unchecked opaque-value, no findings, 0 schema errors
    gnd check positive.orm.yaml p02.pop.json --format json --rule-ids             exit 4, version 15, derivation unchecked opaque-value, no findings, 0 schema errors
    gnd check positive.orm.yaml p02.pop.json --format json --admission            exit 4, version 10, derivation unchecked derived-unknown [derived-extension-unresolved], 0 schema errors
    gnd check positive.orm.yaml p02.pop.json --format json --admission --rule-ids exit 64 (usage)

## Close review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only),
selected by the owner in place of the plan's panel bar, over this record's
draft, the amended plan, the phase records, the README, the cited evidence
and the code. Disposition `revise`, 6 findings (K1-K3 blocking, K4 and K5
completeness, K6 hardening), all accurate; K1 was reproduced. K1 and K2
qualify predicates 2 and 6 (proposed plan §11 rows 2 and 3); K3 marks the
plan amendments as proposed pending the owner's close ruling; K4 lists the
phase boundaries individually; K5 updates the README; K6 retains the issue
states as evidence. Retained verbatim with the triage in
[close-codex-review.md](notes/close-codex-review.md). The corrected record
was not re-reviewed.

## Open-questions sweep

| Item | Raised | Disposition |
|---|---|---|
| FU1-O1: `derivation_verdict_v15` admits `derived-unknown` with no findings; the shape the runtime builds (one `derived-extension-unresolved` finding) is refused there | 002 (review R2) | **accepted residual, owner ruling 2026-11-08** ("Accept as residual"): the probe reached the real shape only on the version-10 `--admission` route, which validates; version 15 refuses `--admission`, and versions 7 and 15 report the case as `opaque-value`. One case (boundary) |
| FU2-O1: FU2's test file over the size stop line | 003 | resolved: accepted by the owner's merge of PR 126 |
| FU3-O1: plan §3 says FU3 reuses FU1's fixtures (refuted, spec P2) | 004 | resolved: plan repaired, §3 and §11 |
| FU5 size over the stop line (+75 against +60) | 006 | resolved: owner accepted ("Accept, finish FU5") |
| FU5-O2: the base known red in `test_development_scaffold.py` (RR1 record's broken link) | 006 | resolved on main by a18b7deb (PR 137, rule-check-release); the test passes in the close's full run at 859b852d |
| Issue 111 (repr model digest) | plan, FD1 | split out (FD1); open, in the report-output-fidelity milestone |
| Issue 112 (projected JSON in text output) | plan, FD2 | split out (FD2); closed by report-output-fidelity (PRs 124, 127) |
| Delivered issues 113, 114, 115, 116, 117, 119 | milestone scope | resolved: all six closed on GitHub, each within seconds of its phase PR's merge (`gh issue view` output retained in evidence/close/issue-states.txt, 2026-11-09); 114 also carries a comment pointing to the FU5 record |
| `test_rf5_commands.py` `_cmd_transition` body pin, red on main since PR 135 | this close | not this milestone's; owner ruling "Record it, fix separately" |
| The two `tests/test_public_optional.py` uv-pin errors | every full run since rule-check-adoption RC2 | carried: environment pins, not this milestone's; present at the merge base |
| FU2 boundaries: `model_construct` unvalidated; other field types (e.g. `source: bogus`) not revalidated on copy | 003 | accepted residual; the first qualifies predicate 2 (above) |
| FU3 boundaries: combined variants such as `acyclic-intransitive`; derivations over derivations, clause or fixpoint rules and `semiderived` rings have no corpus case | 004 | accepted residual; predicate 3 names `acyclic` over an exact-term derived fact type only |
| FU4 boundaries: the ratio bound guards a quadratic walk only; a flake remains possible at unmeasured loads; an erroring process listing has no case (rests on `check=True`) | 005 | accepted residual |
| FU5 boundaries: the guard checks the facade and home module only, not a third-module re-export; a v0.1.0 user of the three private names breaks on upgrade | 006 | accepted residual; the names were documented nowhere public |
| Repairs after each phase review carry no review opinion | 002-006 | accepted residual (boundary below) |

## Plan repair

One refuted premise named a plan repair: FU3-O1 (spec P2). The close
review added two predicate qualifications (K1: predicate 2; K2: predicate
6). All three are written into plan §11 with the prior wording kept, as
**proposed** amendments that take effect with the owner's close ruling;
the amended plan is bound above by sha256. FU5's r1 refuted
premise (FU5-O1) was withdrawn in its spec r2 and needs no plan change.

## Refuted premises

- FU1's record disposes review R2 with "no route emits `derived-unknown`
  on a derivation row". One does: `extensions.py:2522-2530` builds an
  unchecked `derived-unknown` derivation verdict with
  `derived-extension-unresolved` findings, and the `--admission` route
  carries it in version 10, which validates. The FU1-O1 probe above shows
  the version-7 and version-15 routes report the same case as
  `opaque-value`, and version 15 refuses `--admission`.

## Boundary: what this close does NOT establish

- Each phase had one reviewer, and so did this close; the project's panel
  bar ran over nothing in this milestone. Repairs after each review carry
  no review opinion.
- The FU1-O1 probe is one fixture case; it shows no version-7 or
  version-15 route reached, not that none exists.
- The broad lanes (`slow_cadence`) did not run.
- GitHub issue states are as observed on 2026-11-09 (evidence/close/issue-states.txt).
- Merge of this close, which is the owner's close ruling over the record and the plan §11 amendments, is the owner's.

## Owner rulings at the close

- Close review instrument: "One reviewer (Codex)" (2026-11-08), waiving
  the plan's panel bar for the close, as RF-D0 did for the plan.
- FU1-O1: "Accept as residual".
- The `_cmd_transition` RF5 pin broken on main by PR 135: "Record it, fix
  separately" -- not fixed in this close.
