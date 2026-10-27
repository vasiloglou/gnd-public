---
milestone: ilp-learners
station: phase-IL1
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IL1
date: 2026-10-27
gate:
  command: "uv run pytest -q -p no:randomly <the IL1 file list, evidence/IL1/gate-files.txt>"
  exit: 0
  output: "673 passed, 19 deselected in 41.83s"
  note: >-
    The literal gate of spec §8: the direct IL1 tests (tests/test_ilp_learners.py)
    and the plan §9 impact closure (the IK5 corpus, the IK6 walk, the IK close
    test, the RF1 CLI goldens, RF5 commands, the layer map, the architecture
    test, the RF6 census, the built inventory and schema sync). The live lane
    ran separately under the scratch SWI and Popper venv: 3 passed. Ruff clean.
post_merge:
  note: >-
    Merging main (cba51bc) brought the carried-defects RF6 successor in at the
    same chain position. The IL1 delta was re-chained after it: same rows, new
    predecessor and hash, totals 6582 distinct rows and 8250 occurrences. The
    gate above was rerun on the merged tree with the same result, 673 passed,
    19 deselected; final-gate.txt keeps the pre-merge output.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IL1's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL1-spec.md
    sha256: 24471087446e282740272317a57a9d06cf584955ff40b9b874c0b817af4302f3
  - path: .gnd-planning/milestones/ilp-learners/notes/phase-IL1-agent-review.md
    sha256: 53eeea7b5ca3e42b494413ce5f5f14862f55768a82bedc43e49381e087482275
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/gate-files.txt
    sha256: 62c8a86be17d2e4536aff2c95008d153e17e764ca052f43693238d4266d6f915
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/final-gate.txt
    sha256: 19f3b7becba530faf74af4a585dc1396f2e8415547386680c5b63adb0aeb93ae
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/review-brief.md
    sha256: 3e4c836485f4051cb792712412d224f262dbe3e1aa5356c7b2c890896e7ca3bb
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/run_popper.py
    sha256: fc34cd834b1023c5849aa3ffc5bcb995a460590147325ad7d172b3dc421e89ef
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/dynamic-query-successor.json
    sha256: 7ea8941e536f008d025486b260f5900788fccf637c9edf79ce8eab3ee1dc1128
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/requirements.in
    sha256: f545374d976299ff98de698171b6826d27bfa2eb9cfaecfe24474914511a6afa
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/requirements.lock
    sha256: 7e0ccf68c9c7488356a5d58f958d47b77258f22351d59b02b220b3c4af2ad2ca
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-1/outcome.json
    sha256: 8631e83aa5e75706669ce71223f5fee78e9289c6bda515b533385019a5b3bf8d
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-2/outcome.json
    sha256: bdf91fbda32756bc1963b4df09f8f25559ef4fa041a8c1673a2926c82283a11f
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-3/outcome.json
    sha256: 50c0ab02643c618c8ea46ae4c9e298c1fb58507bae76c5d32eeadaa1a066e406
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-3/program.pl
    sha256: 53988e12d988c61b8a0e876eeec59bb7192546d48b847716ace5828a3d8120e4
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-3/run.json
    sha256: c2816a3435454fecc53259032d7979a957f9251c1d0e98324c4ff059fac96373
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-3/proposal.json
    sha256: defbeaf0fd62103066cdb42fbf29b8b17b9b2ee9484ec01e72c982432704b02d
  - path: .gnd-planning/milestones/ilp-learners/evidence/IL1/live/invocation-3/import-report.json
    sha256: 442e96a368ed520fa04f4812d19061302a7739e29e4833f1001961600f64d131
  - path: tests/fixtures/ilp_learners/il1/escapes.json
    sha256: 1ab38d18e6484f28f54d1167751eea5ad0495de85052925acb1d407ba19f15cc
  - path: tests/fixtures/ilp_learners/il1/joins.json
    sha256: e284be0c75331a512ebc1cfc906921527e65997ccf7fc78cb0994fe354a01462
  - path: tests/fixtures/induced_knowledge/ik5-corpus/expected.json
    sha256: 76931cd3890b0c7f652c625f26354b4bcfcf8d618c32798103a386a37233fc85
---

# Phase IL1 — the learner registry, the join check, SWI escapes and a real Popper run

**Claim.** IL1-C1 to C5 hold on the evidence below, under:
- the owner gate in spec §13 (IL1-D1..D9);
- the IL1-F1 ruling (drop the neutral learner check) and the IL1-F2 ruling
  (accept SWI's LGPL libgmp for local use), both in spec §14;
- amendments IL1-A1 (spec §15) and IL1-A2 (spec §16), each approved by the
  owner on 2026-10-27 before its code changed.

**The headline.** In invocation 3, a real Popper (v5.0.1, commit 578a4e2)
learned the refunds tutorial's rule from GND's export:

```prolog
wrong(V0):- f_refund_amount(V0,V1,V2),gt_t_amount__500(V2).
```

Popper scored it at precision and recall 1.00. SWI over `bk.pl` and GND's
checker over the population both cover the same four examples. `gnd import
ilp-rules` admitted it as one guarded constraint, "amount at most 500"
(induced, proposed, deontic, support 4/4). Getting there took two rendering
amendments, each owner-approved, and three recorded runs.

## What shipped

- **`gnd.export.ilp_learners`** (new). One `Learner` entry per `--target`,
  in declaration order: renderer, parser, the run record's learner name, the
  `method` token, the contract, and its own `adapter_version` (IL1-F8).
  `ilp_service` consults it and names no learner. The command modules keep
  literal `choices=` tuples (RF5), and T2 pins them and both schema enums to
  the registry.
- **Check 9b, `type-confused-join`** (`ilp_rewrite.check_join_types`, D12
  (o), D13 (o)). A named variable's sites, including a declared comparison's
  type, must have intersecting ancestor closures (`ilp.type_closures`, from
  `ModelIndex.supertype_closure`). The import always passes the closures.
- **SWI escapes in Popper text** (`ilp_popper`). Octal `\NNN\` (1 to 7
  digits) and, after review finding 7, every form SWI 10.0.2's `writeq`
  writes: `\a \b \v \f \r`, `\xN\`. Refusals are `unparsable` with a line
  and column; one helper builds them all (the executed refactor).
- **`extract_program`** reads Popper v5.0.1's stderr log (IL1-F4): the first
  run of rules after the last solution banner, prefixes stripped (anchored
  after review finding 4a).
- **The Popper rendering, adapter version 3** (IL1-A1, IL1-A2):
  - `bk.pl` is grouped by predicate;
  - each comparison against an observed integer value is a unary threshold
    predicate (`gt`, `lt`; at most 32 values per type, ranked selection),
    written as ground facts over the exported values it holds for;
  - thresholds that hold for no value are omitted;
  - `bias.pl` lists them, with no binary comparison and no
    `magic_value_type`;
  - the parser maps a threshold atom back to the declared binary comparison,
    so checks 5 and 9b apply unchanged.

  The neutral target stays at adapter version 1.
- **The evidence script** `evidence/IL1/run_popper.py`. It runs Popper under
  `run_bounded_process` with all six limits, has SWI evaluate coverage
  independently, imports with fixed arguments and sanitizes paths. The
  install is a hash-pinned lock in a scratch prefix.

**Goldens that moved, all by owner amendment:**
- the X1 Popper export tree;
- in `expected.json`, E for the Popper target and I2's provenance digests;
- the `export_sha256` field of 19 IK5 run records.

No IK5 exit code or refusal changed. No IK5 case became `type-confused-join`.
The neutral target, the IK6 walk and the RF1 goldens are unchanged.

## Gate output (verbatim)

From `evidence/IL1/final-gate.txt` (the scratch path replaced by `<scratch>`):

```
$ uv run pytest -q -p no:randomly $(cat .gnd-planning/milestones/ilp-learners/evidence/IL1/gate-files.txt)
673 passed, 19 deselected in 41.83s
exit 0
$ GND_IL1_SWIPL=<scratch>/SWI-Prolog.app/Contents/MacOS/swipl GND_IL1_POPPER_PYTHON=<scratch>/venv/bin/python uv run pytest -q -p no:randomly -m live tests/test_ilp_learners.py
3 passed, 50 deselected in 0.45s
exit 0
$ uv run ruff check src/gnd/export tests/test_ilp_learners.py .gnd-planning/milestones/ilp-learners/evidence/IL1/run_popper.py
All checks passed!
exit 0
```

Every regression test for a review fix was observed red against `ed54e65`
before its fix, and A2-T3 and A2-T4 were observed red against adapter 2's
code (spec §16).

## The three recorded runs

| Invocation | Rendering | Termination | Import | What it settled |
|---|---|---|---|---|
| 1, **the run of record** | IK5 (adapter 1) | `rendering-rejected` (exit 1, 18.0 s) | `none` | v5.0.1 has no magic values, so a binary comparison's constant is unbound and arithmetic raises (IL1-F7) |
| 2 | adapter 2: rule-defined thresholds | `completed` (1.2 s), `NO SOLUTION` | `none` | the crash is gone, but clingo grounds the rules with no atoms and Popper bans every threshold; its pointless-relation query also sees them all as equivalent (IL1-F9, closed by review finding 2) |
| 3 | adapter 3: ground-fact thresholds | `completed` (1.2 s) | `admitted` | the headline above |

T9 replays all three from their committed bytes in the default gate. For
invocation 3 that includes the import, the normalized report and the
proposal's bytes.

**The spec's three live-run questions** (§6), answered by invocation 3:
1. **Does Popper accept the rendering?** Adapter 3: yes. Adapters 1 and 2: no
   (rows above).
2. **Does the output parse and import?** Yes: exit 0, admitted.
3. **Does every learned clause fit the induction block without loss (the IK2
   residual)?** For this one clause, yes. Its `provenance.induction` carries
   the inducer, the method, the examples, support 4/4 and the export,
   clauses and run digests. One clause is one clause.

## Criteria

| Criterion | Result |
|---|---|
| IL1-C1 registry | holds: T2, T3 (the fake entry reaches the tree, method and learner check), T3b; the service has no learner literal |
| IL1-C2 join check | holds: T5 J1–J4, T5b, T5c, T5e, T5f, A1-T5 (a threshold of another integer type). T5d's neutral learner rule was dropped by the IL1-F1 ruling |
| IL1-C3 escapes | holds: T4, T4b, and test_r7 over every escape form SWI 10.0.2 writes, recorded in the review |
| IL1-C4 live run | holds: invocation 1 is the run of record, with one termination and one import value; T9 replays it, and invocations 2 and 3 are reported beside it |
| IL1-C5 join space | holds: T11, a stand-in learner join candidate that imports with exit 0 |

## Refactoring review

**Executed:**
- **One `unparsable` refusal** (`b906749`). The Popper parser built the same
  "unparsable: line L, column C" error in five places, and the threshold
  mapping reached into the parser class for it. One module helper now builds
  it. Messages are unchanged, and the gate is green.

**Seen and deferred** (open questions below):
- the service does not enforce `Learner.exports` (review finding 6);
- `Learner.contract` has one value, so it is a field no code path varies on
  yet.

IL2 adds the second real adapter, which is where both become real
decisions.

**Not refactored, argued:**
- **`ilp.ADAPTER_VERSION`** now means only the neutral target's version. It
  stays as the default of `export_tree` so that IK5's imports of
  `export_tree` keep working; the registry carries every target's actual
  version.
- **`_threshold_rows`** re-reads the neutral facts that `build_neutral` has
  just written. It is a second pass over in-memory data, not a second
  definition of anything. Its single consumer is `render`.

## Boundary — what this phase does NOT establish

- **One reviewer is one reviewer.**
  - The adversarial review was one local agent over `git diff 5576a4e ed54e65`.
  - It did not run Popper or the full suite.
  - The amendment-2 code and the refactor carry no review opinion.
- **Reproducibility is not measured.** Each invocation is a single run.
  Invocation 3's success is one run of one learner on one eight-example
  tutorial dataset.
- **Rule quality is not established.** Invocation 3 shows that the bridge
  carries a real learner's output end to end. It says nothing about whether
  Popper finds good rules on other data, or about the threshold selection's
  effect on larger domains (above 32 values, rules can only use the selected
  thresholds).
- **Meaning is preserved only over the exported values.** A threshold's
  ground facts equal its comparison only over the values in the export. The
  import re-checks coverage with GND's own comparison over the population, so
  an admitted clause's coverage is GND's, not the facts'.
- **Popper's other settings are not covered.** Only the settings in spec §6
  were exercised; noise, recursion, `direction` and predicate invention were
  not.
- **The infix comparison gap stays open.** An infix comparison across two
  integer types is admitted while the same comparison written as a predicate
  is refused (review finding 3). IK5 behaved the same way.
- **The neutral target accepts any learner name** (the IL1-F1 residual).
- **Spec T6 is a deviation.** It named `tests/test_ilp_live.py`, which does
  not exist. The live checks are in `tests/test_ilp_learners.py` under the
  `live` marker (A1-T2, A2-T3, A2-T4), and the runs are the evidence script.
- **SWI-Prolog's LGPL libgmp** is accepted for local scratch use only
  (IL1-F2); nothing is distributed.
- **The broad historical lane did not run** (`slow_cadence`).

## Open questions

| ID | Question | Origin | Target |
|---|---|---|---|
| IL1-Q1 | Should an infix comparison take part in check 9b like a declared comparison predicate? It changes IK5 behaviour | review finding 3 | IL4, which owns the join check's next call |
| IL1-Q2 | Should the service refuse a non-exporting entry, and should `contract` vary? | review finding 6; refactoring review | IL2, the second real adapter |
| IL1-Q3 | Should the threshold parser refuse names the renderer never writes (leading zeros, `m0`, values outside the export's set)? | review finding 5 | IL2 |
| IL1-Q4 | `extract_program` stops at the first non-rule line inside a solution block, without reporting the truncation | review finding 4b | ilp-learners close |
| IL1-Q5 | Missing tests: T5c's pair count, and a `type_closures` subtype test | review finding 8 | ilp-learners close |
| IL1-Q6 | Is Popper's success reproducible, and does it hold on a larger domain? | boundary | IL6 or a later evaluation phase |
| IL1-Q7 | The plan's §9 IL1 row says "goldens unchanged except listed C2 cases"; the amendments moved IK5 goldens (refuted premise 2) | this record | repair the plan at milestone close |

**Carried rows discharged:** IK5-Q5 (a real Popper run, and whether its
output fits the IK2 block) and IK5-Q2 (SWI octal escapes) are answered here.

## Refuted premises

1. **"Every IK5 golden is unchanged except type-confused clauses" with a
   neutral learner check** (spec §5 against IL1-C2). It is false: 13 approved
   neutral imports would turn exit 3. Killed by IL1-F1 against the IK5 corpus,
   and resolved by the owner dropping the check.
2. **The plan's "goldens unchanged except listed C2 cases" for IL1** (plan
   §9). It is false once the live run demanded rendering amendments; IL1-A1
   and IL1-A2 moved IK5 goldens by owner ruling. Repair: IL1-Q7.
3. **"The IK5 Popper rendering works with a real Popper"** (open since
   IK5-D13). It is false for v5.0.1: invocation 1 (IL1-F7).
4. **"A rule-defined threshold that fails on an unbound argument is safe for
   Popper"** (IL1-A1's design). It is false: Popper's clingo grounding and
   its pointless-relation query both need ground facts. Killed by invocation
   2 and review finding 2.
