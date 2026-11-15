# Literature depth and revision · plan r1 (outline)

**Status: outline draft, 2026-11-14. Not reviewed and not approved.** This
plan covers #193 parts 6, 7 and 8 and defers part 10. The cross-milestone
partition has one home, the
[literature-identity plan §1.1](../../literature-identity/notes/literature-identity-plan.md#11-partition-of-issue-193).
Phases are actionable outlines. This milestone is blocked until
literature-identity LI2 and LI4 are recorded. LD1's extraction step also needs
literature-interop LX1. The plan review is held until this milestone starts.

## Goal and completion predicates

Worked examples answer detailed scientific competency questions. A replayable
multipass reading workflow records what was read and what is still unknown.
A semantic revision, such as an identity split or a refined predicate,
invalidates exactly the dependent reviews and derived claims.

- **LD1.** Three examples answer four predeclared questions each:
  - physical dynamics;
  - molecular and statistical physics;
  - algorithms.

  Each example has source-backed positive answers and questions marked
  unanswerable on purpose. Experiment-centered evaluation facts carry dataset
  version, split, metric, units, baseline, configuration and uncertainty
  where the source states them.
- **LD2** (conditional on LD1 findings). The quantity support LD1 shows is
  needed: unit recognizers and dimension checks for anchored quantities, the
  distinction between percent and percentage points, and exact decimal values
  in witnesses.
- **LD3.** A provider-neutral run manifest and a reference host workflow meet
  #193 part 7 criteria 1–7. The coverage states are "not found in inspected
  text", "source unavailable", "not applicable" and "explicitly denied". An
  absence claim that goes beyond the closed-world reading needs a declared
  closure, a coverage record and a measured extractor recall.
- **LD4.** A dependency manifest and a semantic migration recipe meet #193
  part 8 criteria 1–7, with the whale identity split as the end-to-end case.
- **LD5.** A verdict on a derived claim binds to its supporting assertions,
  resolution decisions, rule definition and resolution edition. It is
  revalidated when any of these change. Rejecting one support never removes
  a claim that has another valid support.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #193 part 6, Proposal and criteria 1–7 | Three areas, a competency-question table, experiment facts, taxonomy as data versus subtypes, every enforced constraint with a purpose and a negative fixture, no quota | LD1 |
| #193 part 6, "Folded in: quantities" | The recognizers in `anchors.py:370-417`. The witness Float refusal in `witness-contract.md:16-27`. Extraction requires every role (`extract/projection.py:245-264`), so optional measurement parts become separate facts | LD2 |
| #193 part 7, Proposal and criteria 1–7, "Folded in: absence claims" | Passes with purpose and stopping rules. Coverage states. Denominators keep refusals and omissions. `applicable.json` describes the model, not what was read | LD3 |
| #193 part 8, Proposal and criteria 1–7, "Folded in: verdicts on derived claims" | Dependency manifest, migration recipe, additive versus reviewed evolution, edition comparison only within its scope. Judgments target supplied occurrences today (`judgments.py:125-133,527-537`) | LD4, LD5 |
| [#104](https://github.com/vasiloglou/gnd-public/issues/104), #75, #78 | The unattended growth procedure, the additive policy and extraction guidelines as shipped | LD1, LD3, LD4 |

## 2–3. Contract sketch and dependencies

- **LD1** is a pattern and example phase. Its checking models use the current
  includes. Extraction against a shared vocabulary needs LX1.
- **LD2** is a runtime phase opened only by an LD1 finding.
- **LD3** builds on `gnd extract` bundles, the unattended-growth contract,
  `gnd fidelity` and LI4's assertion records.
- **LD4** reuses `gnd evolve` operations, impact preview and the
  composition, judgment and resolution receipts from LI2 and LI4.
- **LD5** may need a new judgment target kind for derived rows. Its spec
  decides between that and an example-level binding.

Phase dependencies:

| Phase | Needs |
|---|---|
| LD1 | LI4 |
| LD2 | LD1 |
| LD3 | LD1, LI4 |
| LD4 | LI2, LI4, and integrates LI5 and LD1 |
| LD5 | LD4 |

## 4. Phases

| Phase | Outline criteria |
|---|---|
| LD1 | Per area: positive answers backed by sources, questions marked unanswerable, a complexity result never shown without its assumptions, no direct comparison across metrics or splits, a label change that keeps identity, and missing information kept as unknown |
| LD2 | A unit mismatch is detected. Percent and percentage points are distinct. An exact decimal survives witness and replay. A Float value outside the supported range is still refused, with a named reason |
| LD3 | An unchanged stage replays with no producer call. A fact that only the methods section states is recovered by the targeted pass. An absent methods section is reported as unavailable. Every open question is resolved, retained or superseded. A new vocabulary element triggers a revisit of earlier documents. Refusals stay in the denominators |
| LD4 | The whale split invalidates every dependent false path and leaves unrelated results unchanged. A predicate definition change makes its reviews stale. An ambiguous mapping cannot be assigned arbitrarily. Prior snapshots replay. A missing dependency blocks any claim that the release is current |
| LD5 | A verdict bound to a derived claim goes stale when its rule or its resolution edition changes. A claim with two supports survives the rejection of one of them |

## 5–9. Surfaces, risks, protocol, verification

- **Surfaces.** The literature worked-example section started in
  literature-identity, the documents guide, the unattended-growth reference,
  the evolution guide and the judgment contract. Each normative rule has one
  home.
- **Risks.**
  - The examples could be padded with textbook knowledge. Control: a
    fixture shows that missing information stays unknown.
  - The coverage record could be read as truth about absence. Control:
    stronger absence claims are opt-in.
  - A migration could overwrite evidence. Control: snapshots are retained.
- **Protocol.** As in the literature-identity plan §8. The plan review runs
  when this milestone starts.

## 7. Deferred and out of scope

| Item | Revisit when |
|---|---|
| #193 part 10 · aggregate certificates with membership completeness (P2) | A host needs certified counts. Criteria are carried from the issue: an omitted member is refused, a duplicate member is refused, an empty group is certified, changed inputs invalidate, and size limits refuse clearly |
| A universal physics ontology, or a quota of constraints or subtypes | Never. #193 "Not proposed" |

## 10. Owner decisions

| ID | Question | Proposal |
|---|---|---|
| P1 | Does LD2 open only on an LD1 finding? | Yes, as #193 part 6 says |
| P2 | LD5 as a runtime judgment target or an example-level binding | Decide in the LD5 spec, after LD4 |
| P3 | Part 10 in this milestone | No. Deferred, with its criteria carried |
