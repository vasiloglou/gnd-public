# Reader 4 — measurability, falsifiability and reproducibility

Reviewed plan SHA-256 `26fa91632e5ee637b1949ad4e8dd6ba25daac57180280328e3d04c1e050a1814`
and IK1 spec SHA-256 `f79d6375630e8706a9a3fe88af7669b3f0a81fcbb446ec0e1d55d4df22b8cec0`
— both match (verified with shasum at `0e2ba79`).

**Verdict: request-changes** within the measurability/falsifiability/reproducibility lens.

Scope: full plan (294 lines) and spec (115 lines); standing-rules.md;
spec-note-contract §8; `measure/truth.py`, `score.py`, `report.py`,
`measurement.schema.json`, `synth/provenance.py`, `population.py:69/507`,
`evolve/service.py` `_surface_index`, orm-meta `object_type`, `codegen/docstrings.py`,
provenance-and-modality.md, `tests/test_model_verbalization.py`, the near-cap
scaling fixture. No tests run; issue not fetched.

## Findings

- **R4-F1** (blocking, high): Plan L36–37 and IK4-C1 (L190) say every candidate
  passes `gnd check` ("exit 0 for that constraint"). Candidates are emitted deontic
  (L132); provenance-and-modality.md:110 makes a deontic violation a `warning` with
  exit unaffected, and `gnd check` exits per population, not per constraint. A wrong
  discoverer emitting a violated candidate still exits 0, and vacuous/no-subject
  candidates are undefined. Fix: require verdict `pass` on each emitted constraint
  ref in the check report and state whether `vacuous` candidates are emitted.
- **R4-F2** (blocking, high): IK3 labels carry "per-constraint expected verdicts or
  a population class" (L122–124), but `classify` needs an `ExpectedState` with both
  `ground_truth` and `expected_verdict` (provenance.py:142–144; score.py:212), and
  the false-pass denominator `expected_nonpass` counts over ground truth
  (measurement.schema.json:531–534). Where host ground truth comes from, and how a
  class label maps to each constraint's ground truth, is unstated; the "same cells"
  and their denominators are undefined for host labels.
- **R4-F3** (hardening, medium): IK3-C2 "numerators and denominators reported" and
  L126 (new fields under a new report version) ignore that the current report
  already publishes them (report.py:297; schema 529–550). The criterion passes
  vacuously; the planned report version has no testable field delta.
- **R4-F4** (blocking, medium): Bounds deferred until after results: IK4-C3 (L192)
  and IK3-C3 (L186) time bounds without ceiling, work counter or fixture shape; D6
  pair "capped count" (L290); counterexample bound (L116, L133); manifest cap (L184);
  "near-miss" (L134) with no rule. Repository precedent fixes deterministic
  `maximum_work` counters in advance (tests/fixtures/public-aggregate-near-cap-scaling.json).
- **R4-F5** (blocking, medium): Support/confidence (L116, L131–133; IK-R2 L57) have
  no per-family numerator/denominator (mandatory over instances vs tuples,
  subset/exclusion over pairs); confidence is trivially 1 for emitted candidates and
  undefined for ILP. IK-R2's "exact and reproducible" cannot be checked against an
  independent oracle.
- **R4-F6** (hardening, medium): IK5-C3 (L199) "coverage equality" does not say
  counts or example-id sets; equal counts can hide different covered sets. Recorded
  learner fixtures (L277) are not bound to exported bytes or a learner name/version,
  so hand-written "learner output" passes; the solver-free lane shows GND-internal
  consistency, not round-trip fidelity. IK5-C1 "deterministic" lacks an observation
  (e.g. committed golden digest across two runs with varied PYTHONHASHSEED).
- **R4-F7** (blocking, medium): T7 (spec L99) compares to an unnamed "baseline" and
  names no codegen/conformance fixtures; the existing "byte stable" test compares two
  renders by the same code (tests/test_model_verbalization.py:82–89). A T7 written
  that way passes when output changes for description-less models. Name fixtures
  (e.g. tests/fixtures/models/full_vocabulary.orm.yaml) and pin SHA-256 values
  computed at `a22ccde`.
- **R4-F8** (completeness, medium): Predicate 1 (L25–26) and IK-R3 require "every
  rendered output" unchanged; IK1-C3 (L173) and T7 cover only
  verbalization/codegen/conformance. Extraction projection bytes, `diff` JSON for
  two description-less models (new `annotations`) and evolve preview output are
  unpinned; a diff that always emits `annotations: []` passes every IK1 test.
- **R4-F9** (hardening, low): T2's invalid cases already fail today
  (`additionalProperties: false`, orm-meta.schema.json:164); only the valid case
  discriminates. The 1- and 2,000-char boundaries promised at spec L26–27 are not in
  T2 (maxLength 200 would pass); spec L38 cites "T5's 2,000-char case" absent from
  T5 (L97); T1 (L93) passes on a no-op.
- **R4-F10** (completeness, low): IK6-C1 (L203) has no exit/count (only §9 L263
  "exits 0"); IK6-C2 "skill-surface census" (L204) undefined; IK2-C3 "reports …
  unchanged" (L180) names no golden although tests/test_public_coverage_goldens.py
  exists; IK4-C4 "entailed" (L193) has no named decision procedure.

## Reasons supporting the verdict

- IK4's headline correctness predicate cannot fail for the modality the plan
  assigns candidates (F1).
- IK3 cells lack a ground-truth source for host labels, so denominators are
  undefined (F2).
- Several ceilings are deferred — the known post-hoc-threshold failure class (F4).
- IK1 is mostly sound: criteria and tests map both ways (C1→T1/T2, C2→T3–T6,
  C3→T7, C4→T8/T9) with concrete exits, but byte-identity is not yet anchored to
  committed digests (F7, F8).

## Limits

Static reading; no reproduction by execution. ILP learner output formats,
`gnd.process` bounds and `rai_import.py` not checked. Within IK1, discrimination
was code-checked only for T2.
