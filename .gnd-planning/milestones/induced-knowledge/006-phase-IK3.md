---
milestone: induced-knowledge
station: phase-IK3
skill: "n/a -- repository development via process-phase, not a gnd-solve station over a domain model"
scope: phase-IK3
date: 2026-10-25
gate:
  command: "uv run pytest -q -p no:randomly <the IK3 file list, evidence/IK3/gate-files.txt>"
  exit: 0
  output: "4360 passed, 66 deselected, 1 warning in 736.13s (0:12:16)"
  note: >-
    Direct IK3 tests (tests/test_measure_labels.py: the approved 32-case
    corpus, the implementation tests T1, T2, T5, T7, T8 and the review
    regressions) plus the impact closure: every tests/test_rf*.py,
    test_gnd_arch.py, every test naming measure, the measurement schema,
    redaction, the CLI or capability pages or the docs nav, and the
    packaging inventories. test_incremental_performance.py is excluded (its
    hashability test fails on main too, IK4-Q5).
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside IK3's impact closure; the reduced v6.3 selection was run"
evidence:
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK3/gate-files.txt
    sha256: a7690b684544148095cf04eb1f18a01c97b9f9ee87ee8e3073212f9a4692bdde
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK3/final-gate.txt
    sha256: fe115154541a7d577dbf81147675569e7b83d47ed3cbd840d775adb93e931da3
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK3/corpus-red.txt
    sha256: b83646de5dfe5158559848be3b570f71c5af00abae18dc90b756e143907ed02d
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK3/build_ik3_corpus.py
    sha256: 80c0d7e41ff0abf883e37454786541df8499aac9ac9b2de0289fd8791d79690c
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK3/build_dynamic_successor.py
    sha256: f60384ef362a628521e9d024cbda06a21e374614ee45592c0e85f648e629155f
  - path: .gnd-planning/milestones/induced-knowledge/evidence/IK3/dynamic-query-successor.json
    sha256: c37d893dc6fb2f69160308341d66241355a47703d4741715cb5e1385b7c44ac4
  - path: tests/fixtures/induced_knowledge/ik3-corpus/cases.json
    sha256: 1f99d536b29e885a567bf311b7e0fe49ea874ca87c30eed070aa4d2f6e84a5db
  - path: tests/fixtures/induced_knowledge/ik3-corpus/expected.json
    sha256: 3743d39b472ae8848a08a6915cbf92885546d3aae478c0714dfbe6a38f9c492f
  - path: tests/fixtures/induced_knowledge/ik3-corpus/README.md
    sha256: c9e8661f985cfef6f50822f13f233651b400470cbed609f117bd18da5645c763
  - path: .gnd-planning/milestones/induced-knowledge/notes/phase-IK3-agent-review.md
    sha256: 65980d5ad091b0b16b358598f3bf1f3c0b7f63b6cbe0e0f8f16a78dc3862580a
---

# Phase IK3 — measuring host-labelled populations

**Claim.** IK3-C1 to C4 hold on the evidence below, under the owner rulings in
spec §13 (IK3-D1..D7) and §14 (corpus findings C-F1..C-F6). `gnd measure MODEL
--labels MANIFEST` measures the checker over populations a host labelled
itself:
- **expected-state mode** scores per-constraint labels with the synth path's
  own row builder (report schema 4, exit 6 on a checker defect);
- **class mode** counts, per rule, fired and silent populations of each class
  (report schema 5, exit 0 whatever the agreement).

## What shipped

- **Manifest** `gnd-labels/1`: `src/gnd/labels.schema.json` (closed), read by
  `gnd.measure.labels`.
  - the read is capped at 1 MiB, non-blocking and no-follow, and goes through
    the RF7 JSON policy, then the schema, then a whitespace check;
  - refs (`id:` or positional, for id-less constraints only) are bound through
    `ModelIndex`, and every constraint must be labelled (D4);
  - every label must be consistent with the cell table;
  - populations are inspected component by component (a link anywhere is
    74), read once through `safefs.read_regular_bounded`, digest-checked, then
    loaded from the same bytes. Identical (path, digest) pairs are checked
    once.
- **Class scorer** `gnd.measure.agreement`: six counts per rule with decided
  denominators. Its docstring is the one home of the cell definitions.
- **Report:** the synth per-constraint loop became `report._score_rows`, shared
  by both paths. `build_labelled_report` emits v4/v5 with a `labels` block in
  place of the synth-only header. v4 defect rows omit `sidecar` and `seed`
  (C-F1) and add `population_id` (review R4).
- **Schema:** `measurement.schema.json` gains the v4 and v5 variants. The v1–3
  requirements moved into a conditional branch unchanged; the reviewer found
  them equivalent under single-key mutation.
- **Redaction** keeps schema 4 and 5, attaches its metadata to both, and
  registers exit 66.
- **CLI:** exactly one of `--populations` and `--labels` (64, enforced in the
  handler, I-F1). `--promote` is refused with `--labels` (64). `_cmd_measure`
  is unchanged (I-F3).
- **Registration:**
  - two lane homes, RF1 measure goldens, the RF6 census delta, schema
    inventories;
  - the contract page `docs/reference/measure-labels.md`, CLI and capability
    rows, a nav entry and a guide pointer.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:randomly <IK3 file list; evidence/IK3/gate-files.txt>
4360 passed, 66 deselected, 1 warning in 736.13s (0:12:16)
$ uv run ruff check <changed .py files>
All checks passed!
```

Also run during the phase:
- **Corpus:** committed red at `9dd59af` (30 failed, 3 passed by design). All
  32 cases pass on the implementation.
- **First gate at `572bc52`:** 2530 passed. Its file list had lost every file
  the git-grep selection should have added (zsh does not word-split a
  variable), so it covered 51 files, without `test_measure_labels.py`. The
  list was rebuilt for the gate above.
- **Review regressions:** all seven fail on a copy of `572bc52`'s source and
  pass after the fixes. The over-cap test is coverage: it passes on both.
- **RF1 goldens:** captured on Python 3.14 and spliced for `gnd measure` only.
  The usage line was checked to be identical on 3.12, 3.13 and 3.14 once the
  argparse group was removed (I-F1).

## Criteria

| Criterion | Result | Tests |
|---|---|---|
| C1 | met | T1 (schema bounds, including the 10,000 bound against the schema directly, C-F3), T2 hostile manifests E4–E24 and C3–C5 with named causes, R1–R3 |
| C2 | met | X1: `per_constraint` equals the committed movie/faker synth report except the two C-F2 fields; E2 defect parity; the reviewer found parity on 19 more models |
| C3 | met | C1, C2 (the control and the wrong rule), N1; vacuous and unchecked kept out of denominators |
| C4 | met | the synth measure suites pass unchanged, and the reviewer found JSON, text and exits byte-identical; work at or under P × (1 + C) on N1 (R5 counts real checker runs) |

No bound was moved after implementation.

## Adversarial review

One local reviewer agent read `git diff 9dd59af 572bc52`. **One reviewer is one
reviewer.**
- **Found:** no blocking defect in scoring, binding, class cells or the synth
  path. Five fixed:
  - R1, hardening: a FIFO hangs the reader;
  - R2, hardening: links through intermediate directories, and a
    check-then-open race;
  - R3, hardening: a bare `KeyError`;
  - R4, hardening: defects named by path only;
  - R5, completeness: an arithmetic work counter.
- **Recorded:** R6 as I-F2 (a refuted spec claim) and R7 as C-F7 (a harness
  fix to an approved test, for owner ratification).
- **Accepted or deferred:** R8–R10.

The report is kept verbatim, with its disposition, in
[phase-IK3-agent-review.md](notes/phase-IK3-agent-review.md).

## Refactoring review

**Refactors EXECUTED:**
- **One row builder.** The synth path's per-constraint loop was extracted
  verbatim into `_score_rows` and is shared by both paths. The synth payload is
  unchanged, so expected-state parity is structural, not argued.
- **One safe-read seam.** Population reads use the existing
  `safefs.read_regular_bounded` instead of a second containment check.

**Seen but deferred:**
- **IK3-Q5:** the labels and synth handlers each carry a nested `fail()` with
  the same redaction projection. Merging them would touch the RF5-pinned
  `_cmd_measure`.

## Boundary — what this phase does NOT establish

- One reviewer is one reviewer; the broad lanes were not run (`slow_cadence`).
- **Labels are the host's claim.** GND checks shape, binding and consistency,
  not truth.
- **The evidence excerpts carry population facts** under the model's
  redaction policy, as on the synth path (I-F2).
- **Under a redacting model,** refusals after the model loads report
  `[REDACTED INSTANCE DETAIL]` rather than their cause (review R8, as on the
  synth path).
- **Effective size:** the 1 MiB manifest cap holds about 8,000 class-mode
  entries; the 10,000-population bound cannot be reached (C-F3).
- **The RF1 measure goldens** were captured on Python 3.14 only; the usage line
  was checked by hand on 3.12 and 3.13.
- **Pre-existing red:** `test_prepared_policy_rechecks_live_hashability`
  (IK4-Q5).

## Open questions

| ID | Question | Target |
|---|---|---|
| IK3-Q1 | The checker reports `role-unresolved` with a wrong message on an opaque-value mandatory cell (C-F5) | checker follow-up |
| IK3-Q2 | Case-insensitive file systems accept alias path spellings, so results depend on the host (R9) | owner ruling; milestone close |
| IK3-Q3 | A constraint-free model cannot be measured in expected-state mode (`minProperties: 1`) (R9) | owner ruling; milestone close |
| IK3-Q4 | The "model changed while it was read" branch has no failing case (R10) | milestone close |
| IK3-Q5 | Merge the two measure `fail()` closures (refactoring review) | after RF5 shim retirement |
| C-F7 | Ratify the X1 harness fix (expected answer unchanged) | owner, now |

## Refuted premises

- **"The report repeats only population ids and digests" (spec §3, the IK-R11
  row).** v4 evidence must equal the synth row, which carries population facts.
  IK-R11 governs induction evidence; redaction governs this output (I-F2).
- **"The work counter bounds the work" (first implementation).** As first
  written it was arithmetic, so its ceiling check could not fire. It now counts
  real checker runs (R5).
