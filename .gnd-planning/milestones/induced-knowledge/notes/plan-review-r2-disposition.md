# Plan review — round 2 (confirmation) disposition

2026-10-23. Instrument: the same four owner-selected local reviewer agents
(D7), with the same four lenses, as the single confirmation round declared in
the [round-1 disposition](plan-review-r1-disposition.md). The owner instructed
this round after accepting the round-1 repairs and the proposed answers for
D8–D13. Running the round does not approve any bytes.

## Subjects

| Artifact | SHA-256 |
|---|---|
| Plan r2 | `d1a40a89eecad01e7e4dc72e969beb4c548297c1967df0d268c6776c18207c85` |
| IK1 spec r2 | `4f4cb8b580c680e5523d6cf1f4a4752abe3d76099a19c713620c51e8e5d3cac1` |

- Commit: `b554f3f`.
- Snapshots: [plan](../evidence/plan-review-r2/induced-knowledge-plan.md) and
  [spec](../evidence/plan-review-r2/phase-IK1-spec.md).
- The [manifest](../evidence/plan-review-r2/manifest.json) records the snapshot
  and reader-note digests.
- All four readers verified both digests.

Each reader was restricted to two questions: whether round-1 findings in their
lens are resolved, and whether r2 introduced defects. They could also raise
blocking findings against unchanged text.

The run disclosure:
- No files were written by readers.
- No paid tools or credentials were used.
- Reader 2 ran `python -I` probes.
- Everything else was static reading.

## Opinions

| Reader | Lens | Verdict | New findings | r2-introduced | Blocking |
|---|---|---|---|---|---|
| [1](plan-review-r2-reader-1.md) | semantics, admission | approve-with-fixes | 5 | 5 | 1 |
| [2](plan-review-r2-reader-2.md) | implementability, layers | approve-with-fixes | 4 | 4 | 0 |
| [3](plan-review-r2-reader-3.md) | protocol, authority, privacy | request-changes | 6 | 5 | 1 |
| [4](plan-review-r2-reader-4.md) | measurability | approve-with-fixes | 4 | 4 | 1 |

## Round-1 blocking findings: resolution

| Round-1 | Status after r2 |
|---|---|
| R1-F1 derivation rules ungated | resolved (readers 1) |
| R1-F2 / R4-F1 exit 0 ≠ holds | resolved (1, 4) |
| R1-F3 entailment suppression | partially resolved; candidate-vs-candidate redundancy open (C1-F4) |
| R1-F5 / R4-F2 IK3 truth table | resolved; class-cell denominators still to define (reader 4 residual) |
| R1-F6 ILP faithfulness | partially resolved; polarity mapping ill-formed (C1-F1), vacuous rule open (C1-F2) |
| R2-F1 projection allowlist | resolved (2) |
| R2-F2 diff vocabulary mismatch | resolved (2) |
| R4-F4 deferred bounds | resolved by IK-R12 (4) |
| R4-F5 support definitions | resolved (4) |
| R4-F7 unnamed T7 baseline | resolved in naming; baseline commit wrong (C4-F1) and commands unlisted (C4-F3) |

Ten of twelve round-1 blocking findings are resolved. The other two (R1-F3,
R1-F6) are partially resolved.

## Coordinator reproduction of new blocking and medium findings

| Finding | Check | Result |
|---|---|---|
| C1-F1 polarity mapping ill-formed | representation-format.md "Guarded constraints": antecedent is a conjunction of positive atoms; consequent is one of atom/comparison/absence/exists | reproduced |
| C3-F1 = C4-F1 baseline at `a22ccde` vs merge #35 first | PR #35 commit `9137bd7` changes `_constraint_cnl` for `allowed` value constraints; `full_vocabulary.orm.yaml` contains them | reproduced (same defect, two readers) |
| C2-F1 = C4-F2 escaped description truncated | `_neutralize("'"*300)` contains "more characters" | reproduced (probe printed `True`) |
| C2-F2 `oneOf` breaks an existing test | `tests/test_conformance_payload.py:652` indexes `$defs.diff_reference_report.properties.command` | reproduced |
| C3-F2 D12 reading not offered as a single proposal | round-1 disposition theme E: "bump … only when annotations present, or bump always — rule required" | reproduced; the coordinator selected the first reading when writing r2 |
| C1-F3 `reviewed_in` is self-asserted; `imported` is not an admission precedent | `_enforce_d12` refuses non-llm-inferred/non-user-supplied sources; `reviewed_in` is a non-empty string | accepted on citations |

## Convergence: stop rule

The round was computed, not estimated, using the rule declared before it in
the round-1 disposition and `review-convergence.md`.

- **Self-inflicted ratio:** 18 r2-introduced / 19 new findings = **0.95**. This
  exceeds one half, so **the stop rule is met**.
- **Same-seat counts, round 1 → 2:**

  | Reader | Round 1 | Round 2 |
  |---|---|---|
  | 1 | 8 | 5 |
  | 2 | 8 | 4 |
  | 3 | 9 | 6 |
  | 4 | 10 | 4 |

  Counts are falling.
- **Severity ceiling:** still high, from two distinct defects, both in r2-written
  text.

**Decision under the declared budget: plan review stops.** No third round is
run. Round 2 shows the review is now measuring the r2 repair text, not the plan's
design. The remaining defects are textual and precise, and their fixes are named
by the readers.

## Proposed r3 text repairs (not yet applied)

These would be applied without a further review round. Amended bytes carry no
review opinion.

| ID | Repair |
|---|---|
| P-1 (C3-F1/C4-F1) | Capture T7's baseline at IK1's actual base commit, named at the IK1 spec gate after PR #35's disposition. Do not use `a22ccde`. |
| P-2 (C1-F1, C1-F2) | IK5 mapping by body rewriting: one body literal moves into the consequent. A negated comparison becomes `comparison`; an atom becomes `absence`. The fragment is limited to positive-atom bodies; NAF and aggregates are refused by name. A vacuous verdict counts as *not covered* and is reported separately. |
| P-3 (C1-F3) | `induced`+`confirmed` is allowed only as a status change of an existing `proposed` induced constraint, with `reviewed_in`. Discover/import output may not carry `reviewed_in`, with a refusal test. Remove the `imported` "precedent" wording. |
| P-4 (C2-F1/C4-F2) | Render descriptions escaped but **uncapped** (bounded by the 512-character schema cap times the worst-case escape factor). Add a hostile 512-character case to T3. |
| P-5 (C2-F2) | Keep closed top-level `properties` with optional `annotations`, plus `if`/`then` on `schema_version`. No top-level `oneOf`. |
| P-6 (C3-F3) | Restore D1–D6 cost readings from r1. Tag every r2 change, including D2's "confirmed only per D9", D6, IK-R8 and IK-O9–O12. Correct the "untagged = unchanged" claim. |
| P-7 (C3-F4, C3-F5) | Record the budget wording once. Cite round-1 disposition commit `642cade` for the owner acceptance. |
| P-8 (C4-F3, C4-F4) | List the exact argv, the hashed artefact and the normalization for each of T7's seven outputs. Remap T12 to C3. Mark C5's reference clause review-only, or add a link check. |
| P-9 (C1-F4, C1-F5, C2-F3, C2-F4, reader-4 residuals) | Candidate-vs-candidate redundancy rule and `[1,1]` wording, settled in the IK4 spec under IK-R12. State that `vocabulary_digest` no longer identifies the vocabulary text, with a test. Update constraint-reference.md:47 and representation-format.md:272. Name the shim docstring. Define class-cell denominators in the IK3 spec. |

## Owner decision required

**D12 authority (C3-F2).** The owner accepted "the proposed answers for D8–D13".
For D12 the round-1 disposition offered two readings. The coordinator chose
"v2 only when annotations are present" while writing r2, and r2 recorded that as
owner-accepted. That record is not established by the owner's words. The owner
needs to confirm that reading, or choose "always v2". Until then D12 is
**coordinator-selected, pending owner confirmation**.

## Status

- Plan r2 and IK1 spec r2 are not approved.
- Plan review is closed by its stop rule after two rounds.
- The P-1 to P-9 text repairs and the D12 confirmation are pending owner
  direction.
- D1–D6 remain open.
- No implementation, phase activation, merge or certification is authorized.

## Owner direction and r3 (appended 2026-10-23)

On 2026-10-23 the owner did two things:
- **Confirmed D12** as "`gnd-diff/2` only when annotations are present". That
  resolves C3-F2: D12 is now owner-confirmed, no longer a coordinator selection.
- **Directed repairs P-1..P-9** to be applied as plan r3 and IK1 spec r3, with
  no further review round, and pushed to PR 36.

The r3 artifacts:

| Artifact | SHA-256 |
|---|---|
| Plan r3 | `e0c15f8efab530a1d10f8d9aa3622bb8420f623d6315512f4d8da330beacc003` |
| IK1 spec r3 | `8114bf6cf29f8f1dd201751460c0486d63dafd3e6318478185c4273d8b4e3299` |

Changes are tagged `(p2)`. **r3 bytes carry no review opinion.** No reader has
seen them, and the stop rule closed plan review.

Where each repair landed:

| Repair | Where applied |
|---|---|
| P-1 | IK1 base commit B named at the IK1 gate after PR #35's disposition. Plan predicate 1, IK-R3, IK1-C4, §9; spec §6 baseline capture, IK1-D4. |
| P-2 | IK5 body-rewriting mapping, positive-atom fragment, refusals by name, and vacuous = not covered. Plan §2 Request 5, IK5-C2, IK5-C3. |
| P-3 | Confirmation only as a `proposed`→`confirmed` status change. Discover/import output may not carry `reviewed_in`. The `imported` wording is withdrawn. Plan predicate 2, §2 Request 6, IK2-C2, D9. |
| P-4 | `neutralize_text` (escape without cap), one escape walk, and a hostile 512-character test. Plan §2 Request 1, sweep; spec §§4, 6, T3, T13. |
| P-5 | Closed `properties`, an `enum` version, and `if`/`then`/`else`; no `oneOf`. Spec §6 Diff, T10; plan sweep. |
| P-6 | r1 D1–D6 costs restored. Untagged r2 rewordings tagged. The "untagged = unchanged" claim corrected. |
| P-7 | Budget has one home (round-1 disposition), with the round-2 widening recorded. Acceptance cites `642cade`. |
| P-8 | Seven-row command, artefact and normalization table. T12 remapped to C3. C5's reference clause is review-only. |
| P-9 | Class-cell denominators in IK3-C3; candidate redundancy and `[1,1]` wording in IK4-C5; the vocabulary-digest identity consequence and its docs (`constraint-reference.md:47`, `representation-format.md:272`); the shim docstring. |

The round-2 [manifest](../evidence/plan-review-r2/manifest.json) digests this disposition as committed in `73a76ad`, before this appended section; it is left unchanged as the record of that round.
