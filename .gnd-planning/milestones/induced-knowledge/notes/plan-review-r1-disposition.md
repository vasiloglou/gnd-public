# Plan review — round 1 disposition

2026-10-23. Owner-selected instrument (plan D7, selected 2026-10-23 in reply
to the review question): **four local reviewer agents**, as in the preceding
milestone. The selection names the instrument only; it does not approve plan or
spec bytes or authorize implementation.

## Subjects and limits

Reviewed plan r1 SHA-256:
`26fa91632e5ee637b1949ad4e8dd6ba25daac57180280328e3d04c1e050a1814`.
Supporting IK1 spec SHA-256:
`f79d6375630e8706a9a3fe88af7669b3f0a81fcbb446ec0e1d55d4df22b8cec0`.
Inspection HEAD: `0e2ba79` on `claude/induced-knowledge-plan`.

Retained exact snapshots: [plan](../evidence/plan-review-r1/induced-knowledge-plan.md)
and [IK1 spec](../evidence/plan-review-r1/phase-IK1-spec.md); their line citations
are the reviewers'. [Manifest](../evidence/plan-review-r1/manifest.json) records
snapshot and reader-note digests.

Each reviewer started with fresh context, received the subject digests and a
different lens, verified both digests, and read the complete plan/spec and the
relevant sources. All four ran concurrently as local model agents, not humans or
a provider panel. This is the selected advisory plan instrument, not the
different-harness adversarial diff review required during implementation. No
paid tools, credentials or native lanes were used; reader 2 ran read-only probes
and left two temporary YAML files in the session scratchpad, outside the
repository. Opinions are static readings of the named bytes.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| [1](plan-review-r1-reader-1.md) | semantics and admission safety | request-changes | 5 | 2 | 1 |
| [2](plan-review-r1-reader-2.md) | implementability, homes and layers | request-changes | 2 | 3 | 3 |
| [3](plan-review-r1-reader-3.md) | protocol, authority, compatibility, privacy | approve-with-fixes | 0 | 3 | 6 |
| [4](plan-review-r1-reader-4.md) | measurability and reproducibility | request-changes | 5 | 3 | 2 |

Reader notes retain the returned substantive text with local headings added.

## Coordinator reproduction

Each blocking/high finding was checked against the reviewed bytes and code at
`0e2ba79`:

| Finding | Check | Result |
|---|---|---|
| R1-F1 | `evolve/service.py:203–208` `_constraints()` reads only constraint lists; `_reports.py` `has_alethic_fail` counts any derivation `fail` | reproduced |
| R1-F2 / R4-F1 | provenance-and-modality.md D-03 table: deontic violation → `warning`, exit unaffected; plan L36–37 "exit 0 for that constraint" | reproduced |
| R4-F2 / R1-F5 | `synth/provenance.py` `ExpectedState{ground_truth, expected_verdict}`; plan L122–124 offers no ground-truth source for class labels | reproduced |
| R4-F3 | `measure/report.py:290–300` already emits `false_pass`, `expected_nonpass`, `false_fail`, `satisfied` | reproduced |
| R2-F1 | `extract/projection.py:43–54` `_ALLOWED_KEYWORDS` lacks `description` | reproduced |
| R2-F2 | `anchors.vocabulary_digest` differs with and without `description`; `diff.py:280–282` raises `diff:vocabulary-mismatch` | reproduced (probe printed `False`) |
| R1-F3, R1-F6, R4-F4, R4-F5, R4-F7 | definitional gaps in the reviewed text; confirmed by reading the cited lines | reproduced as documented gaps |

No finding was refuted. Medium/low findings are accepted on their citations.

## Findings grouped by repair

| Theme | Findings | Proposed repair (r2) | Needs owner ruling |
|---|---|---|---|
| A. Admission safety | R1-F1, R1-F7, R1-F8, R3-F4 | IK5 emits only `guarded` constraints (gated by D-12), never `derivation_rule`; define `induced`+`confirmed` with a required `reviewed_in` (as `imported`), and refuse `provenance.induction` under other sources; delete the `sample` option at L132; induction evidence uses repository-relative or opaque ids and value digests, never host paths or raw values | **D8** (IK5 output form), **D9** (confirmation path) |
| B. Discovery soundness | R1-F2, R1-F3, R1-F4, R2-F8, R4-F1, R4-F5 | Soundness predicate: per emitted constraint ref, report verdict `pass` and support > 0 (vacuous never emitted). Discovery evaluates against the whole closed-world population (not per fact type) and states the honest memory bound (one ≤10 MiB population in memory). IK4 spec must fix, before code, a closed entailment-suppression catalogue that is modality-blind, canonical frequency form, and per-family support numerator/denominator; drop "confidence" for discovery | none beyond spec gate |
| C. IK3 labels | R1-F5, R4-F2, R4-F3 | Two label modes. (1) per-constraint `ExpectedState` reuses the existing truth table unchanged; (2) host class labels (e.g. right/wrong) use a **new** agreement scorer with fixed cells — fired-on-negative, fired-on-positive, silent-on-negative, silent-on-positive, plus vacuous and unchecked counted separately — each with numerator and denominator. Remove the claim that numerators/denominators are new for the existing report | **D10** (accept second scorer) |
| D. ILP faithfulness | R1-F6, R4-F6 | Declare a closed clause-to-`guarded` fragment with per-construct semantics (polarity mapping, NAF, aggregates, closed-world rosters, typing); refuse constructs outside it. Coverage check compares **sets** of example ids, with vacuous counted explicitly; coverage agreement is stated as necessary, not sufficient. Recorded learner fixtures bind the exported bytes digest and learner name/version; determinism observed as a committed golden digest across two runs with different `PYTHONHASHSEED` | none beyond D4/D8 |
| E. IK1 design | R2-F1, R2-F2, R2-F3, R2-F4, R2-F5, R3-F2, R3-F3, R3-F7, R3-F8, R4-F7, R4-F8, R4-F9 | Expose descriptions through the constraint-blind extraction vocabulary, not the projection schema; decide the vocabulary digest (exclude `description`, which changes no existing digest because no current model has one); diff wire: bump to `gnd-diff/2` only when `annotations` present, or bump always — rule required; update `report.schema.json` embedded diff copy, redaction, diff.reference.md and the RF1 mutation anchor together; cap at 512 to match `_neutralize` (or render outside it); extend `BlastRadiusEntry.surface` and evolution-contract.md; T7 names fixtures and pins SHA-256 values computed at `a22ccde` for verbalization, codegen, conformance, projection, vocabulary, diff and evolve preview; T2 boundary cases (1 and 512 chars) and a positive-only discriminator; reorder spec sections; add the representation-format.md and gnd-extract skill rows; re-estimate size | **D11** (vocabulary digest), **D12** (diff wire version), IK1-D1 revised |
| F. Plan protocol | R2-F6, R2-F7, R3-F1, R3-F5, R3-F6, R3-F9, R4-F4, R4-F10 | PR #35 described as proposed (open) with IK1 as fallback owner of request 2 if it is not merged; name lanes/RF5 entry-point registration and RF6 ceiling in §3 and IK6-C3; DAG becomes IK2 → IK4, IK3 → IK5, IK1 sequenced with IK2 for shared files; disposition rows for the 1,880 host constraints (migration via discovery output, no import obligation) and the "without it" fallbacks (no migration of host sidecars); record D7 as owner-selected; every numeric bound (work counters, pair cap, counterexample cap, manifest cap, near-miss rule) fixed in its phase spec before implementation and never moved after measurement; observable exits/goldens for IK2-C3, IK4-C4, IK6-C1, IK6-C2 | **D13**: the source issue names a downstream application in public — owner may edit the issue text; the plan never repeats the name |

## Convergence budget (declared before any round two)

Self-inflicted ratio for round 1: 0 / 35 (first round over first draft).
Severity ceiling: high (four findings). Same-seat counts: 8 / 8 / 9 / 10.

Budget: one repair revision (r2) after owner rulings on D8–D13, then **at most
one** confirmation round by the same four lenses, restricted to whether the
reproduced blocking findings above are resolved. Stop rule exactly as in
`.codex/skills/process-phase/references/review-convergence.md`: stop when the
self-inflicted ratio exceeds one half or same-seat counts are flat-to-rising for
two consecutive rounds while severity falls. Remaining design questions after
that move into phase specs, where the code is the instrument.

## Current status

Plan r1 is **not approved** and not ready for approval: 12 blocking findings
across three lenses, all reproduced. No plan or spec bytes were amended in this
round; the r1 files equal their snapshots. D1–D6 remain open. D7 is
owner-selected. New proposed decisions D8–D13 are listed above for the owner.
No implementation, phase activation, merge or certification is authorized.

Next action: owner rulings on the proposed repairs and D8–D13; then r2 and the
bounded confirmation round.
