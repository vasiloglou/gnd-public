# Literature interoperability · plan r4

**Status: r4, 2026-11-15. See the [delegated plan gate](../003-plan-gate.md).** This
plan covers #193 part 5 and the dates step of part 4. The cross-milestone
partition has one home, the
[literature-identity plan §1.1](../../literature-identity/notes/literature-identity-plan.md#11-partition-of-issue-193).
Expanded from r1 (SHA-256
`a287b667dfc9c0077d97d7dbc5dd565fbeb16ae9ad622a9de8b1e92284c6ea7a`).
This is framework development. Acceptance measures the runtime contracts below.
[Round 1](../001-panel.md) reviewed r2
(`dc0b3fd0f1dfea5f6a299fc6a12e8cf2d0d77452c6e67a0c46761515c1d14573`).
[Round 2](../002-panel.md) reviewed r3
(`0d7b4b18ea96f8f942dbafdaae144d5cc6490a17efcd4e39bcb869f3ddbb915e`).
Round 2 met the four-reviewer requirement and triggered the convergence
stop. The r4 amendments below carry the round-2 dispositions.

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
  the extraction artifact index. Omit flattening fields from the include-free
  wire.
- **LX2.** Witness and replay consume LX1's projection and verification path.
  The certificate binds the flattening record and identifies the model origin
  of the elements its nodes use. Replay verifies model origin separately from
  fact provenance. Cover path-based production and replay including a
  reference-free composition record. Preserve the selected include-free wire
  bytes. When the path route receives flat and record bytes, both producer
  and replay verify them against the resolved root. Direct byte routes with
  no trusted include root stay guarded.
- **LX3.** Use the existing declared-reference binder. Candidate rows may
  survive validation using catalog entities, including via explicit renaming.
  Keep catalog rows outside source renaming, deduplication and lineage. Bind
  catalog digests in the composition record and verify them in check,
  witness and replay. Omit catalog bindings on the reference-free wire.
  The composed check evaluates the candidate against the catalog once.
  Preserve LI2 resolution checks among candidate sources.
  LX3 owns mixed reference and candidate provenance in composed witnesses.
  Validate the catalog in isolation before validating candidate rows against
  it. A catalog that depends on candidate rows is invalid. The phase spec
  pins the order relative to manifest binding and the existing LI2 checks.
- **LX4.** Extract and verify each source with the extraction root. Rebind
  each verified source population and its anchor evidence to a checking
  root with the same include IDs and digests and the same catalog bindings
  in this fixture. The checking root adds temporal constraints. The
  example's versioned rebind record binds both roots, include and catalog
  identities, extraction index, document, old and rebound populations and
  anchor evidence. Keep candidates separate from the catalog.

  Validate the rebinds before composing the sources on the checking root.
  Compose, check, witness and replay all use the checking root and the
  composition output bound to it. The example verifies the rebinds and
  records the resulting composition, check and witness digests in its
  integration manifest. Pair matching reference and composition inputs
  at the existing product boundaries. The example's manifest verifies the
  cross-stage chain.

  Run a separate, optional `gnd.examples.literature.interop dates` example
  step after composition. Reuse the LI5 relation vocabulary and chainable
  relation policy for candidate edges as inputs. The public fixture records
  the two work IDs for each proposed chainable edge before admission, so
  the rejected PINN edge can be diagnosed without becoming an admitted
  lineage edge. Non-chainable edges are outside the report denominator.
  A missing or unresolved work link yields unresolved. A fixture-side
  publication-date table uses work ID, publication-role label, value and
  precision. Compare known years at equal precision, allowing equality.
  Missing, conflicting, mixed-precision and other-role-only inputs yield
  unresolved. The report binds its candidate-edge and date-input bytes,
  which stay separate from the product check and witness inputs.

  Run fidelity against the same document evidence as composition. Count
  additional materialized copies of the document, extraction population and
  sidecar by route. The LX4 phase result records the measured counts and
  either adopts a shared example layout verified by both readers or names
  the specific incompatibility and the owner and target for further work.

## 3. Dependencies and readiness

Review base `befea8f1`. LI0–LI5 are merged, as recorded in the
[literature-identity close](../../literature-identity/035-milestone-close.md).
D6 permits this milestone after LI0. The plan gate records the bounded review outcome. LX specs and implementation
have their own gates.

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
| LX2.a | Produce and replay a witness over the LX1 model, with and without a reference-free composition record. Exercise root and include origins. Independently forge a model origin and a fact provenance coordinate, keeping the other axis fixed. Refuse a substituted flat document with pinned root and record fixed. |
| LX2.b | A changed include yields exit 3 and `binding-stale` on replay. Existing include-free certificates continue to replay and the selected producer bytes match the pre-change control. |
| LX3.a | Compose two sources against a pinned catalog. A candidate fact refers to the catalog and an explicit rename onto a catalog identity verifies. Candidate population and source lineage exclude reference rows. A composed check evaluates a constraint whose outcome distinguishes evaluation with the catalog from evaluation of the candidate alone. The reference-free record bytes equal their pre-LX3 control. |
| LX3.b | Refuse a reference catalog with a key conflict or a dependency on candidate rows. Mutate catalog bytes with candidate and composition output bytes fixed. Compose refuses the stale declaration and check, witness and replay refuse the stale binding, each in its documented band. Independently mutate a candidate source and the composition record in the routes that consume them. Keep the valid catalog pin fixed when forging the record's catalog binding. Preserve LI2's refusal of an unjustified cross-source join. |
| LX3.c | Witness and replay one proof with a catalog-backed node and a candidate-backed node. The certificate verifies both their fact provenance and their model origins. With candidate bytes fixed, separately swap catalog to candidate, swap candidate to catalog, forge the catalog binding and forge the model origin. Each replay refuses. |
| LX4.a | Use a separate checking root that pins the extraction vocabulary and adds a temporal constraint. A discriminating temporal control proves checking evaluates it. Mutate the rebind record, either root, an include pin, an extraction index or a rebound source population one at a time. Verification refuses before evaluating the added constraint or running the advisory report. Also attempt a fresh rebind to a separately valid checking root with different vocabulary pins or a different valid catalog. Each mismatch refuses. |
| LX4.b | A public fixture edge from a 2026 work to a 2019 work passes, and a same-year edge passes. The candidate PINN 2019-to-2021 edge yields the fixture's one advisory and names both works, dates and the publication role. Unknown work, conflicting date, missing date, mixed precision and alternative-role-only cases yield unresolved. Check exit and violation counts and the witness result are identical when the separate dates invocation is omitted. |
| LX4.c | A single fixture ties the two pinned includes, extraction, source rebind to the checking root, declared catalog, catalog-assisted resolution, composition, check, advisory report, witness and replay together in the order in §2. Run each valid stage with exit 0. Verify each chain link in the next table and assert the §7 refusal matrix. Record the LI1 layout decision from §2. |

The LX4 spec names each wire field and exit diagnostic. Verify these links
with independent mutations so matching two fabricated values cannot pass.

| Link | Verification boundary | Mutation |
|---|---|---|
| Include bytes → root and flat record | Include resolver and flattening verification | Change one pinned include |
| Flat record and projected wire → extraction bundle | Bundle consumer | Change the record or flat wire independently |
| Flat document and flattening record → witness | Producer and replay | Substitute the flat document while retaining its root and record |
| Verified extraction and checking inputs → rebind | Example's source rebind verification before composition | Change the extraction index, document, anchor evidence, either root or source population |
| Rebound candidate and resolution input → composition | Source intake and example integration manifest | Change the rebound source or resolution evidence with the published bindings fixed |
| Catalog files → composition and witness | Compose and downstream check, witness and replay | Change a catalog with candidate bytes fixed |
| Composed population and its record → witness and replay | Witness and replay input binding | Change population or record bytes |
| Witness certificate → replay result | Replay verifier | Forge model origin or swap the fact origin kind |
| Candidate lineage edges and qualified work dates → advisory output | Optional example report and integration verification | Change one reported date or its input role with the retained input bindings fixed |

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
| LX1 extract and LX4 fixture | Temporal constraint on the extraction root | 3 |
| LX2 direct witness/replay intake | Authored include-bearing bytes without a trusted resolved root | 3 |
| LX3 check | Explicit anchors or reference override combined with composition's own bound context | Existing invalid-input band |

Include and extraction rules keep their existing homes. Generic temporal
extraction and support for nested or unattended includes are deferred.

## 8. Execution protocol

Apply the [literature-identity protocol](../../literature-identity/notes/literature-identity-plan.md#8-execution-approval-and-review-protocol)
and the project hook. The maintained panel is the plan and close instrument,
with at least four valid responses required by the project. The two-round
plan-review budget is exhausted. The recorded convergence decision in
[002](../002-panel.md) moves the work to implementation and verification. The
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


## 11. Round 2 amendment

The preceding r3 text is retained in the [review snapshot](../evidence/plan-r2/reviewed-plan.txt).
Round 2 repairs affect the LX2–LX4 contracts and acceptance controls in
§§2, 4 and 7, with the absent-field compatibility rule recorded in §2.
LX4 now rebinds each verified source before composition and uses one checking
root from composition through replay. Temporal extraction refusal is exercised
at LX1 and again in the integrated fixture. The date report uses fixture-side
work dates and runs separately from product checking. The [review record](../002-panel.md)
records the remaining review boundaries and the convergence arithmetic.
