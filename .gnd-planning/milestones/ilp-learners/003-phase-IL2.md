---
milestone: ilp-learners
station: phase-IL2
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IL2
date: 2026-10-27
gate:
  command: "uv run pytest -q -p no:randomly <the IL2 file list, evidence/IL2/gate-files.txt>"
  exit: 0
  output: "766 passed, 20 deselected in 47.77s"
  note: >-
    The literal gate of spec §8: the direct IL2 tests (tests/test_ilp_asp.py)
    and the plan §9 impact closure (the IL1 and IK5 bridge tests, the IK6
    walk, the IK close test, the RF1 CLI goldens, RF5 commands, the layer
    map, the architecture test, the RF6 census, the built inventory and
    schema sync). The live lane ran separately with the scratch clingo
    5.8.2: 1 passed. Ruff clean on the export package, the IL tests and
    the evidence script.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IL2's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL2-spec.md
    sha256: 0495f191a185d8276b7e67db0da6080ec674e4ba3f25f552122be8ea440bbd4c
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL2-agent-review.md
    sha256: b42030d1f41bf676e5a88c148ac8f6470a0aaf5354b23760ffd215fcca398d35
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/gate-files.txt
    sha256: ac2163b2a26b0233e780704870360e869ec98d7c907d061627db1dda0b977036
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/final-gate.txt
    sha256: 3df4c9e5f8cd1adba7842cd02e4922891081a127455b78e9916580b8ef2f2af1
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/review-brief.md
    sha256: 055767801b5453a4fad0e2b8d5be89d771015eae830bfd3832f9f14b0eddc92e
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/run_ilasp.py
    sha256: dc3052e0ea36e068bab5c5b882a52d307811dc9f103a5e2bda151f43b0f7831d
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/dynamic-query-successor.json
    sha256: b0aeae579096eba04917818ea164c546e2bd583c82bc498b46bea8c1582acbf8
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/download.json
    sha256: cec3285d90dfbabf8006bdcde4ea5e3ccf0a0b35e4f02132286fffdb1c3dbe7b
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/probe/ilasp-help.txt
    sha256: e040a5c07144b5b26315d91d33142e554b89f016a2ee80a786cb1e58977c28b6
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/probe/ilasp-otool-L.txt
    sha256: 433a7c85bda2817833ccc505c99a3be0f4758681c9743caf8a76363a849f62fd
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/probe/ilasp-version.txt
    sha256: e18bbcfaa96457e0ca3b487f3bda20a6cfe2393415f220e8fe4eb84c5dd982b8
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/probe/toy-unsat.stdout.txt
    sha256: 340797a0a7c06ff7fe05739f71710d9adee54fb03c0d1c343b9678144d3ec934
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/probe/toy.stdout.txt
    sha256: 16897d353abaf094ea1f73e3dd885a2e262edbadf6367e3a1a88cb0b5b9d3e08
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/probe/toy-unsat.las
    sha256: 2022ab548097b9ada9c962adf048de7a59643316586232e30ab838b356c5f0da
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/probe/toy.las
    sha256: fe0a47767a73a8aaf084a920c2ab6cb3bd16b05e236c969ce156eb92bf440b51
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/live/invocation-1/hypothesis.las
    sha256: 980756ff90d0e7fa358e9c8242a2396e3da9ef734e1f88e53799ecc9ebd6e50f
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/live/invocation-1/import-stderr.txt
    sha256: 5db251385abb6bcbee68e45d30a75f3d60d1f1a94adcd7ecd40447a3860c7064
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/live/invocation-1/outcome.json
    sha256: 1de6448477056b5d203a07e838a0146b34b7a2916d1e3dc8dfbce80e5ad10a10
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/live/invocation-1/raw-stderr.txt
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/live/invocation-1/raw-stdout.txt
    sha256: 1892cde7b410da6907fe5c073ccab4490f0d3844a1d89f6299bdfefa6a6691cc
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL2/live/invocation-1/run.json
    sha256: 0b459640a613923cff8011c1cdda0af841b69923845f6f16835fe06c170bb65f
  - path: tests/fixtures/ilp_learners/il2/hypotheses.json
    sha256: 708dc608685d99b4ce920c2478f7d3fb98f8b0c2a3c50f74554c13ce4c697b14
  - path: tests/fixtures/ilp_learners/il2/expected/orders/export.json
    sha256: 03d3cf157e1fe3d5d614511492afadc638412cdc7d591f0463bee2b2c2b3dc37
  - path: tests/fixtures/ilp_learners/il2/expected/refunds/export.json
    sha256: 1acb801053b0491a86a393bcce88f482a7431ca62051c9bb6c13f3eab7228a5e
  - path: tests/fixtures/ilp_learners/il2/expected/orders/ilasp/task.las
    sha256: 16f8a3d817025afa53dde1fe4141013d6eff5595716b82cb41e6e01ebc07c32e
  - path: tests/fixtures/ilp_learners/il2/expected/refunds/ilasp/task.las
    sha256: e5f0f9413ed0618578927d095c35e64af6ce94dd1ae116fb60c72c49b8a665c4
---

# Phase IL2 — the ILASP adapter, its closed ASP reader, and a real ILASP run

**Claim.** IL2-C1 to C4 hold on the evidence below, under:
- the owner gate in spec §13 (IL2-D1..D11, IL2-Q1);
- the IL2-D12 (a) ruling (a scratch Python 3.10 for ILASP), spec §14;
- the ruling that invocation 1 is recorded as is, with IL2-F7 a recorded
  result, spec §14;
- the IL2-D13 (a) and IL2-D14 (a) rulings from the review, spec §14.

**The headline.** In invocation 1, a real ILASP 4.4.1 learned this from GND's
refunds export in 123.7 s:

```
wrong :- gt_t_amount(V1,500).
```

GND refused it: `refused:empty-antecedent`, exit 3. The rule names only the
comparison, so there is no antecedent atom for a guarded constraint. Its
meaning is right: clingo, evaluating it independently over the task, covers
harbor, market, airport and station, the four weeks Popper's IL1 rule
covers. This is IL2-F7, a property of the rendering, and the owner ruled it
a recorded result rather than a defect to amend.

## What shipped

- **`gnd.export.ilp_asp`** (new, export lane):
  - `render` writes `ilasp/task.las`. The background is the comparison
    definitions only: per integer type, `dom_t` rules over the predicates,
    `thr_t` facts from IL1's threshold selection, and `gt_t`/`lt_t` rules.
    Then the `#constant`s, `#modeh(wrong)`, one `#modeb` per predicate
    (without the example argument) and per comparison, `#maxv(4)`, and one
    `#pos`/`#neg` context per labelled example, ids `e<i>`.
  - It refuses as `unrepresentable`: a string with a control character
    other than a newline, and (IL2-D14) an integer outside clingo's 32-bit
    range.
  - `extract_hypothesis` takes every non-blank line after ILASP's last
    `%%` line (IL2-F5, then IL2-F8).
  - `parse_hypothesis` is a closed, capped reader to `gnd-ilp-clauses/1`:
    11 named refusals, `unparsable` with line and column for everything
    else (including what clingo reads differently, IL2-F9, and bare
    symbolic constants, IL2-D13), and `wrong :- body.` threaded to
    `wrong(X) :- body'`.
- **The registry entry `ilasp`** (`method: ilp-ilasp`, run-record learner
  `ilasp`, adapter version 1, `boolean_strings` false). Check 9 now refuses a
  quoted `"true"`/`"false"` on a boolean role for this entry only (IL2-D13).
- **IL2-D8 in `ilp_popper`:** threshold names the renderer never writes
  (leading zeros, `m0`, `m` with a leading zero) are `unparsable`.
- **Shared homes in `gnd.export.ilp`** (step 5): `observed_integers`,
  `COMPARISON_NAME`, `refusal_name`.
- **Surfaces:** both CLI `choices` tuples and both schema `target` enums add
  `ilasp` within `/1`; `docs/reference/ilp-bridge.md` gains the ILASP
  section; `tools/gnd_layers.json` assigns the module.
- **The evidence script** `evidence/IL2/run_ilasp.py`: ILASP under
  `run_bounded_process` (600 s wall clock, 10 s grace, output caps), clingo
  as the independent coverage evaluator, fixed import arguments, path
  sanitization, and `--complete-retained` for IL2-F6.

**Goldens that moved:** 9 RF1 CLI goldens (the export and import help and
exit files, and the two `target` actions of `cli/tree.json`, patched in
place, IL2-F3). Every IK5, IK6 and IL1 golden and every Popper rendering is
byte-identical. The approved corpus answer for `k4-symbolic` changed by the
IL2-D13 ruling; the case keeps its prior answer.

## Gate output (verbatim)

From `evidence/IL2/final-gate.txt`, at `3f34325` (the scratch path replaced
by `<scratch>`):

```
$ uv run pytest -q -p no:randomly $(cat .gnd-planning/milestones/ilp-learners/evidence/IL2/gate-files.txt)
766 passed, 20 deselected in 47.77s
exit 0
$ GND_IL2_CLINGO_PYTHON=<scratch>/il1-live/venv/bin/python uv run pytest -q -p no:randomly -m live tests/test_ilp_asp.py
1 passed, 89 deselected in 0.53s
exit 0
$ uv run ruff check src/gnd/export tests/test_ilp_asp.py tests/test_ilp_learners.py .gnd-planning/milestones/ilp-learners/evidence/IL2/run_ilasp.py
All checks passed!
exit 0
```

Every regression test for a review fix was observed red against `bf15642`
(18 failed, 13 passed), and the IL2-D13/D14 tests against `58704ed`'s code
(7 failed, 1 passed), before their fixes.

## The run of record

| Invocation | Termination | Import | What it settled |
|---|---|---|---|
| 1, **the run of record** | `completed` (123.7 s by ILASP's own timing; the process record was lost, IL2-F6) | `refused:empty-antecedent` | ILASP accepts the rendering; it prefers the lone comparison, which GND's fragment refuses (IL2-F7) |

T9 replays it from its committed bytes in the default gate: E, the
extraction, the import's exit and its refusal line. The null process record
is accepted only for invocation 1 and only with the IL2-F6 note.

**The spec's three live-run questions** (§6):
1. **Does ILASP accept the rendering?** Yes.
2. **Does the hypothesis parse and import?** It parses; the checker refuses
   it as `empty-antecedent`.
3. **Does clingo's coverage agree with GND's?** GND computed none, because
   the clause was refused before support. clingo's covered set equals GND's
   for Popper's equivalent rule.

## Criteria

| Criterion | Result |
|---|---|
| IL2-C1 ASP golden | holds: T1 (refunds and the IK5 X1 model, `PYTHONHASHSEED` 0 and 1, byte-identical), T1b (background is comparisons only, contexts without the example argument, `#modeb` arity = arity − 1, thresholds = IL1's selection) |
| IL2-C2 reader | holds: T3 (the fixture hypothesis to its clause JSON), T4 (one case per refusal name, 11), T4b (`not` and aggregates reach the checker's names), T5 (one case per constants row), T6 and the R cases (totality and caps), T12 (both doc tables pinned to the reader) |
| IL2-C3 shared binding | holds: T3 admits through the shared checker with `method: ilp-ilasp`; T7 (`learner-mismatch`, `coverage-mismatch`); T8 (`type-confused-join`) |
| IL2-C4 live run | holds: the licence was recorded (spec §12) and ruled (IL2-D1) before the download; invocation 1 has one termination and one import value; T9 replays it |

**Plan §9's IL2 row** ("ASP golden; per-construct refusals; replayed live
record", affecting "new adapter tests; RF1 CLI goldens; schema enums"): T1,
T4 and T9 respectively; the RF1 goldens moved as listed; T2 pins the enums.

## Review

One local reviewer agent read `git diff 65fd6df bf15642`
([review note](notes/phase-IL2-agent-review.md)). It found 1 blocking, 6
hardening and 4 completeness findings, all reproduced. The blocker
(IL2-F8: the extractor dropped learned constraints, and the clingo
cross-check saw the same truncated text) and 8 others were fixed with
regressions; findings 2 and 6's export half became IL2-D13 and IL2-D14 and
were implemented as ruled. Finding 5's off-threshold constant is a boundary
row.

## Refactoring review

**Executed** (spec §14, "Step 5"), behavior-preserving, behind the gate above:
1. **`observed_integers`:** the per-type integer collection was written out
   in both `ilp_popper._threshold_rows` and `ilp_asp._domains`.
2. **`COMPARISON_NAME`:** the comparison-name regex was written out in both
   readers.
3. **`refusal_name`:** learner-agnostic, so it moved out of the ILASP adapter.

**Not refactored, argued:** IL1's `evidence/IL1/run_popper.py` keeps its own
copy of the refusal parse; it is retained evidence cited by digest in the
IL1 record.

**Carried from IL1:** IL1-Q2's two halves were re-targeted by IL2-D7:
non-exporting entries to IL5, `contract` variation to IL4. IL2's entry
exports and uses `labelled-clauses`, so neither became real here.

## Boundary — what this phase does NOT establish

- **One reviewer is one reviewer.**
  - The adversarial review was one local agent over `git diff 65fd6df bf15642`.
  - It did not run ILASP or the full suite.
  - The fixes, the IL2-D13/D14 code and the step 5 refactors carry no review
    opinion.
- **No admitted ILASP rule.** The one run produced a rule GND refuses.
  IL2 shows the bridge carries ILASP's output to a named verdict, not that
  ILASP's rules are admitted on this data.
- **Reproducibility is not measured.** Invocation 1 is a single run.
- **The process record of invocation 1 was lost** (IL2-F6). `completed` rests
  on the retained output: ILASP's closing `%% Total` block, 123.7 s below
  the 600 s wall clock, and output far below the caps. The exit status was
  not observed.
- **No learner timeout.** ILASP 4.4.1 has no timeout option, so
  `learner-timeout` is unreachable; the wall clock is the only limit (IL2-D3
  (a)).
- **An off-threshold comparison constant** (`gt_t_amount(V,501)` when 501 is
  not a rendered threshold) has no ASP meaning, and the reader cannot see the
  export to refuse it. Only a run record whose coverage comes from an
  independent evaluator, as `run_ilasp.py`'s does, refuses it
  (`coverage-mismatch`).
- **ILASP's other settings are not covered.** Only the spec §6 settings ran:
  no `-nc`, no noise, no other `--version`.
- **The ILASP binary runs on a scratch, non-framework CPython 3.10** through a
  framework-path shim (IL2-D12 (a)). Nothing about Homebrew's build is
  established.
- **Licences.** ILASP is used for non-commercial research by the owner's
  ruling (IL2-D1); nothing is distributed or committed from it.
- **Spec §6 listed 8 moved goldens; 9 moved** (IL2-F3).
- **The broad historical lane did not run** (`slow_cadence`).

## Open questions

| ID | Question | Origin | Target |
|---|---|---|---|
| IL2-Q1 | The Popper reader reads a bare `true` as the string `"true"`, while the Popper renderer writes a boolean bare | spec §7, ruled to carry | ilp-learners close |
| IL2-Q2 | Should the ILASP bias require each comparison variable to occur in a predicate atom (amendment IL2-A1, adapter 2, a second run)? | IL2-F7; the owner ruled invocation 1 as is | IL6 or a later evaluation phase |
| IL2-Q3 | Should the import hand the export's thresholds to the ASP reader, so an off-threshold constant is refused without an independent evaluator? | review finding 5 | ilp-learners close |
| IL2-Q4 | IL-R9's learner-timeout clause assumes every learner has one; ILASP 4.4.1 does not | IL2-F5, refuted premise 4 | repair the plan at milestone close |
| IL1-Q2 | (carried) the non-exporting refusal and `contract` variation | IL2-D7 | IL5 and IL4 |

**Carried rows discharged:** IL1-Q3 (the Popper threshold parser now refuses
names the renderer never writes, IL2-D8; out-of-set values stay in IL1's
boundary). IL1 refuted premise 4 is answered by the ground `thr_` facts and
domain-bound rules, which ILASP accepted.

## Refuted premises

1. **"The macOS ILASP binary is self-contained"** (spec §12 and IL2-D2). It
   is false: it links a Homebrew Python 3.10 framework (IL2-F4). Resolved by
   IL2-D12 (a).
2. **"The hypothesis is printed before ILASP's first `%%` line"** (spec §6).
   It is false: the timing block comes first (IL2-F5, the probe).
3. **"A learned constraint is refused `asp-constraint`"** (IL2-F5's own
   claim). It was false until IL2-F8: the corrected extractor still dropped
   every non-`wrong` line.
4. **"The learner has its own timeout below the wall clock"** (plan IL-R9).
   It is false for ILASP 4.4.1. Repair: IL2-Q4.
5. **"Binding the comparison's variable through `dom_t` keeps ILASP's rule
   inside GND's fragment"** (the spec §6 rendering design). It is false:
   ILASP's cheapest rule is the comparison alone (IL2-F7). Carried as IL2-Q2.
