# Literature interoperability · plan r3

**Status: amended after round 1 on 2026-11-15. Delegated plan ruling pending.** This
plan covers #193 part 5 and the dates step of part 4. The cross-milestone
partition has one home, the
[literature-identity plan §1.1](../../literature-identity/notes/literature-identity-plan.md#11-partition-of-issue-193).
Expanded from r1 (SHA-256
`a287b667dfc9c0077d97d7dbc5dd565fbeb16ae9ad622a9de8b1e92284c6ea7a`).
This is framework development. Acceptance measures the runtime contracts below.
[Round 1](../001-panel.md) reviewed r2. This revision addresses the retained
findings. The reviewers' responses bind the r2 snapshot.

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

Apply the [literature-identity plan §0](../../literature-identity/notes/literature-identity-plan.md#0-binding-design-rules) and the six project design rules by name in every phase spec.

- **Projections are recorded.** Each projection and rebinding gets a record
  bound to the bytes it consumed. Never a silent fallback.
- **Includes stay as they are.** Their rules (standalone-valid, no nesting,
  confined paths) stay as written, and LX1 projects them; it does not relax
  them.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #193 part 5, baseline refusals | At the review base, extraction guards includes in `_cmd_extract` and checks temporal admission in `project`. Witness path intake guards includes in `_witness_inputs` and `_composition_lineage`. Direct intake uses the model-byte loader. `compose` refuses reference populations. Include admission rules live in the representation format. | LX1–LX4 |
| #193 part 5, Proposal 1–4 and criteria | Flattened extraction, flattened witnesses, reference populations as fixed inputs, checking/extraction split, end-to-end fixture, digest chain, clear refusals | LX1–LX4 |
| #193 part 4, "Folded in: dates" | Date roles say which date they are. The check is advisory, and missing or conflicting dates are unresolved. A 2026 paper with a 2019 parent passes. The PINN edge is reported with both works and dates | LX4 |
| [#95](https://github.com/vasiloglou/gnd-public/issues/95), closed | The includes contract as shipped | LX1, LX2 |
| [LI0 result](../../literature-identity/003-phase-LI0.md) | Preserve legacy model serialization and witness compatibility | LX1, LX2 |
| [LI1 carryover](../../literature-identity/006-phase-LI1.md#open-questions) | Measure the friction between the fidelity and composition evidence layouts and record a disposition | LX4 |
| [LI2 result](../../literature-identity/010-phase-LI2.md) | Preserve candidate cross-source identity verification | LX3 |
| [LI5 result](../../literature-identity/024-phase-LI5.md) | Use public lineage input and output contracts for the advisory date comparison, including the PINN regression | LX4 |

## 2. Contracts

- **LX1.** Reuse the path-aware include resolver and its element origins. The
  proposed `gnd-flattening/1` record binds root bytes, include IDs and bytes, and
  the canonical projected model. Origin addresses cover imported elements,
  root elements, anonymous constraints and attachments. Verify projection
  identity after serialization and bind the record and projected bytes into
  the extraction artifact index.
- **LX2.** Witness and replay consume LX1's projection and verification path.
  The certificate binds the flattening record and identifies the model origin
  of the elements its nodes use. Replay verifies model origin separately from
  fact provenance. Cover path-based production and replay including a
  reference-free composition record. Preserve the selected include-free wire
  bytes. The phase spec identifies direct byte routes that stay guarded.
- **LX3.** Use the existing declared-reference binder. Candidate rows may
  survive validation using catalog entities, including via explicit renaming.
  Keep catalog rows outside source renaming, deduplication and lineage. Bind
  catalog digests in the composition record and verify them in check and
  witness consumers. Preserve LI2 resolution checks among candidate sources.
  LX3 owns mixed reference and candidate provenance in composed witnesses.
  Validate the catalog in isolation before validating candidate rows against
  it. A catalog that depends on candidate rows is invalid. The phase spec
  pins the order relative to manifest binding and the existing LI2 checks.
- **LX4.** A checking model shares the pinned extraction vocabulary and adds
  temporal constraints. Define a versioned rebind record with both roots,
  shared vocabulary, extraction index and population digests. Verify it
  before checking the rebound population. The example-level advisory report
  compares a named publication date role on directed builds-on edges in the
  fixture's lineage data. Use the false PINN candidate edge as a diagnostic
  input without admitting it as a supported lineage path. The date report
  retains both work IDs and reported dates. Unavailable, conflicting or
  differently qualified dates in the selected role stay unresolved.

  Run fidelity against the same document evidence as composition. Count
  additional materialized copies of the document, extraction population and
  sidecar by route. The LX4 phase result records the measured counts and
  either adopts a shared example layout verified by both readers or names
  the specific incompatibility and the owner and target for further work.

## 3. Dependencies and readiness

Review base `befea8f1`. LI0–LI5 are merged, as recorded in the
[literature-identity close](../../literature-identity/035-milestone-close.md).
D6 permits this milestone after LI0. Round 1 reviewed r2. LX specifications and implementation are pending.

| Phase | Prerequisite | Next action after plan gate |
|---|---|---|
| LX1 | LI0 merged | Prepare LX1 spec and corpus |
| LX2 | LX1 projection and LI0 model wire | Prepare LX2 spec after LX1 |
| LX3 | LX2 witness origins and LI2 resolution contract | Prepare LX3 spec after LX2 in the ordered walk |
| LX4 | LX1–LX3 results, LI1 public fixtures and LI5 lineage route | Prepare integration spec and public fixture |

## 4. Acceptance criteria

| ID | Observable result |
|---|---|
| LX1.a | Extraction over two pinned includes exits 0. The bundle validates against the original root and every mapped address resolves to its source. Exercise an anonymous constraint and root attachment. |
| LX1.b | Independently change root, included file, flat model and record bytes. Bundle verification exits 3 and identifies the stale input in each case. Rewrite both flat model and record consistently with each other but inconsistently with the pinned root. Re-resolution refuses that forgery. Through extraction, exercise confined-path and standalone-validity refusals. |
| LX1.c | Include-free artifact index and bundle bytes equal their pre-LX1 control with the same paths, inputs and version. |
| LX2.a | Produce and replay a witness over the LX1 model, with and without a reference-free composition record. Exercise root and include origins and refuse a fabricated origin. |
| LX2.b | A changed include yields exit 3 and `binding-stale` on replay. Existing include-free certificates continue to replay and the selected producer bytes match the pre-change control. |
| LX3.a | Compose two sources against a pinned catalog. A candidate fact refers to the catalog and an explicit rename onto a catalog identity verifies. Candidate population and source lineage exclude reference rows. The reference-free record bytes equal their pre-LX3 control. |
| LX3.b | Refuse a reference catalog with a key conflict or a dependency on candidate rows. Mutate catalog bytes with candidate and composition output bytes fixed. Compose refuses the stale declaration and check, witness and replay refuse the stale binding, each in its documented band. Independently mutate a candidate source and the composition record in the routes that consume them. Preserve LI2's refusal of an unjustified cross-source join. |
| LX3.c | Witness and replay one proof with a catalog-backed node and a candidate-backed node. The certificate verifies both their fact provenance and their model origins. Swap origin kinds in both directions, or forge a catalog binding, with candidate bytes fixed. Each replay refuses. |
| LX4.a | Use a separate checking root that pins the extraction vocabulary and adds a temporal constraint. A discriminating temporal control proves checking evaluates it. Mutate the rebind record, checking root, shared pin and rebound population one at a time. Verification refuses each before evaluating the added constraint or running the advisory report. |
| LX4.b | The 2026-to-2019 edge passes. The candidate PINN 2019-to-2021 edge yields an advisory naming both works, dates and the role compared. A conflicting date, missing date or alternative-role-only date yields unresolved. A second date role with an opposite ordering cannot substitute for publication. Check exit and violation counts and the witness result are identical with the advisory stage omitted. |
| LX4.c | A single fixture ties the two pinned includes, extraction, declared catalog, catalog-assisted resolution, composition, rebind and checking root, advisory report, witness and replay together. Run each valid stage with exit 0. Verify each chain link in the next table and assert the §7 refusal matrix. Record the LI1 layout decision from §2. |

The LX4 spec names each wire field and exit diagnostic. Verify these links
with independent mutations so matching two fabricated values cannot pass.

| Link | Verification boundary | Mutation |
|---|---|---|
| Include bytes → root and flat record | Include resolver and flattening verification | Change one pinned include |
| Flat record and projected wire → extraction bundle | Bundle consumer | Change the record or flat wire independently |
| Extraction evidence and resolved candidate input → composition | Source intake and integration rebind | Change document, sidecar or candidate population bytes |
| Catalog files → composition and witness | Compose and downstream check, witness and replay | Change a catalog with candidate bytes fixed |
| Extraction vocabulary and checking model → population rebind | Checking route before evaluation | Change the checking root, pin or rebind record |
| Composed population and its record → witness and replay | Witness and replay input binding | Change population or record bytes |
| Witness certificate → replay result | Replay verifier | Forge model origin or swap the fact origin kind |

Each phase spec pins boundary-specific refusal precedence and an input with two
defects that can distinguish the order. Where equivalent errors make a runtime
test inconclusive, use the project's source-order control.

## 5. Surfaces

The representation format owns flattening and origin rules, the witness
contract owns replay bindings, and the composition reference owns fixed
catalog rules. The documents guide owns the model split and rebind contract and
demonstrates the supported flow. The public example's guide owns the advisory
date report semantics and links to the lineage contract.

## 6. Implementability and risks

- The include resolver already supplies source and flattened addresses. LX1
  must verify that the serializer preserves or correctly maps those addresses.
- Verify bindings over the actual bytes consumed. Re-resolve pinned inputs
  at the downstream trust boundary to detect post-extraction changes.
- Witness composition currently expects candidate lineage for base nodes.
  LX2 establishes model origin verification over a reference-free composition.
  LX3 extends composition lineage to distinguish reference-backed nodes and
  verifies both provenance kinds.
- Bind the reference context apart from candidate output. Use a stale catalog
  control even when candidate output bytes remain identical.
- Choose a named publication date role for LX4 and test ambiguity explicitly.

## 7. Unsupported combinations

Exercise these controls at the named route. The phase specs pin the exact
messages in the current exit band. The diagnostic names the rejected
combination or forbidden field.

| Boundary | Combination | Exit |
|---|---|---|
| LX1 extract | Include with nested includes | 3 |
| LX1 extract | Include declaring reference populations | 3 |
| LX1 extract | Unattended included source, including a source with incompatible unattended metadata after relabelling | 3 |
| LX4 extract | Temporal constraint on the extraction root | 3 |

Include and extraction rules keep their existing homes. Generic temporal
extraction and support for nested or unattended includes are deferred.

## 8. Execution protocol

Apply the [literature-identity protocol](../../literature-identity/notes/literature-identity-plan.md#8-execution-approval-and-review-protocol)
and the project hook. The maintained panel is the plan and close instrument,
with at least four valid responses required by the project. The plan-review budget is at most two rounds. If a second round is selected,
apply the documented convergence ratio and same-seat trend before any further
review work. The
`literature-interop auto` invocation delegates exact-byte milestone rulings.
Panel invocation needs scoped authorization. Phase specs use the corpus-first
default for wire formats, validation predicates and exit codes.

## 9. Verification

Select direct tests plus focused consumers under the default lane filters.
Apply the project structure guard list, component check and Ruff gate. Pin
exact commands and bounded-input controls in each spec.

| Phase | Initial consumer selection |
|---|---|
| LX1 | `test_mc1_model_includes.py`, `test_extract_cli.py`, `test_extract_manifest.py`, `test_extract_projection.py` |
| LX2 | `test_witness_composition.py`, `test_public_replay_admission.py`, `test_mc1_model_includes.py`, `test_li0_witness_wire.py` |
| LX3 | `test_composition.py`, `test_composition_example.py`, `test_witness_composition.py` and affected reference and resolution controls |
| LX4 | New `test_lx4_literature_interop.py` covers the fixture, rebind and advisory cases. Existing `test_li5_lineage.py`, `test_public_temporal_canonical_counterexamples.py` and `test_composition_example.py` cover adjacent contracts. |

## 10. Owner decisions

| ID | Question | Proposal |
|---|---|---|
| X1 | One flattening record format shared by extract and witness | Yes, one home in the representation format |
| X2 | Is the date check advisory or deontic? | Advisory first, as #193 asks |
| X3 | Which phase owns mixed catalog and candidate witness provenance? | LX3 after LX2 establishes model-origin verification. |
| X4 | Where does the LI1 evidence-layout carryover land? | LX4 records a measured disposition on the fixture |
