# Literature interoperability · plan r1 (outline)

**Status: outline draft, 2026-11-14. Not reviewed and not approved.** This
plan covers #193 part 5 and the dates step of part 4. The cross-milestone
partition has one home, the
[literature-identity plan §1.1](../../literature-identity/notes/literature-identity-plan.md#11-partition-of-issue-193).
Phases are actionable outlines, and none has a spec yet. The plan review is
held until this milestone starts (literature-identity D9).

## Goal and completion predicates

A shared vocabulary pinned through includes, a catalog of known entities held
as a reference population, extraction, composition, `gnd check` and a
witnessed query all run on one end-to-end fixture. Digests chain from the
vocabulary through to the witness. Each combination that stays unsupported
refuses with a message naming that combination.

- **LX1.** `gnd extract` accepts an include-bearing model through a recorded,
  digest-bound flattened projection. The flattening record maps each element
  to the include it came from.
- **LX2.** `gnd witness` and `gnd replay` accept the same flattened model.
  Certificates name elements by their origin.
- **LX3.** `gnd compose` accepts a model with reference populations, and
  treats the reference rows as fixed inputs that are not themselves composed.
  Candidate rows may refer to the entities they define.
- **LX4.** A documented checking-model/extraction-model split runs: the
  checking model includes the extraction vocabulary and adds constraints that
  extraction never evaluates, temporal ones among them. An advisory date-order
  check on lineage edges runs beside a real extraction.

## 0. Binding design rules

As in the literature-identity plan §0.

- **Projections are recorded.** Each projection and rebinding gets a record
  bound to the bytes it consumed. Never a silent fallback.
- **Includes stay as they are.** Their rules (standalone-valid, no nesting,
  confined paths) stay as written, and LX1 projects them; it does not relax
  them.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #193 part 5, "In 0.3.1 these refuse one another" | `guard_path` in `extract/service.py:110-116`. `guard_bytes` in `witness/service.py:28-31`. Composition refusal in `composition.py:225-227`. Include restrictions in `representation-format.md:1755-1759`. `require_non_temporal` in extract. All confirmed at `ecd12986` on 2026-11-14 | LX1–LX4 |
| #193 part 5, Proposal 1–4 and criteria | Flattened extraction, flattened witnesses, reference populations as fixed inputs, checking/extraction split, end-to-end fixture, digest chain, clear refusals | LX1–LX4 |
| #193 part 4, "Folded in: dates" | Date roles say which date they are. The check is advisory, and missing or conflicting dates are unresolved. A 2026 paper with a 2019 parent passes. The PINN edge is reported with both works and dates | LX4 |
| [#95](https://github.com/vasiloglou/gnd-public/issues/95), closed | The includes contract as shipped | LX1, LX2 |
| literature-identity LI2 | The resolution record, which the LX3 catalog may assist | LX3 |

## 2–3. Contract sketch and dependencies

- **LX1** adapts `model.loading` (include composition) and `extract.service`,
  and emits a `gnd-flattening/1` record. Extraction bundles bind the record's
  digest.
- **LX2** adapts `witness.io.intake` and `witness.service`. It depends on LX1's
  record and on literature-identity LI0's `model_wire`.
- **LX3** adapts `model.composition` and `model.loading.bind_population`. It is
  independent of LX1 and LX2.
- **LX4** needs LX1. Its date-check fixtures come from literature-identity LI1.

Start condition: LI0 is merged. LX3 may start any time. The
[literature-identity D6](../../literature-identity/notes/literature-identity-plan.md#10-owner-decisions-and-open-questions)
decision decides whether this milestone runs alongside LI1–LI5.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| LX1 | Extraction over a two-include fixture exits 0. The flattening record names each element's origin. A changed include makes the bundle stale. Nested or unattended includes keep their existing refusals |
| LX2 | Witness and replay over the LX1 fixture exit 0. Each certificate node carries an element origin. A changed include is `binding-stale` |
| LX3 | Compose with a reference catalog exits 0. A reference row never appears in the composed population as a source fact. Renaming onto a reference identity is verified. A conflicting catalog refuses |
| LX4 | The checking model evaluates a temporal constraint that the extraction model omits. The date check reports the PINN edge as advisory with both dates. A missing date is unresolved, never a violation. The end-to-end fixture chains its digests |

## 5–9. Surfaces, risks, protocol, verification

- **Surfaces.** The representation-format includes section, the composition
  reference, the documents guide and the witness contract each gain one home
  sentence per new combination.
- **Risks.**
  - A flattening could change element identity. Control: the origin is
    recorded.
  - A reference catalog could be read as composed data. Control: lineage
    excludes reference rows.
  - Date semantics could drift. Control: each date role is named.
- **Protocol.** As in the literature-identity plan §8. The plan review runs
  when this milestone starts.
- **Verification.** Each spec names its focused lane. Each phase's spec
  selects its consumers from `test_extract_*`, `test_witness_composition.py`,
  `test_composition*.py` and the include-loading tests.

## 7. Deferred and out of scope

- **Includes.** Nested includes, includes that declare reference populations,
  and relabelling an unattended model to make it importable (#193 part 6).
- **Temporal extraction.** Temporal support inside extraction is out of
  scope. LX4 keeps temporal constraints in the checking model.

## 10. Owner decisions

| ID | Question | Proposal |
|---|---|---|
| X1 | One flattening record format shared by extract and witness | Yes, one home in the representation format |
| X2 | Is the date check advisory or deontic? | Advisory first, as #193 asks |
| X3 | Is the order of LX3 within the milestone free? | Yes. It shares no files with LX1 and LX2 |
