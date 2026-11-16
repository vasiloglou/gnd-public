# LX2 · model origins in witnesses and replay

Status: delegated approval (auto=true), 2026-11-15. See [006](../006-phase-LX2-spec-gate.md).

## Provenance

The [r4 milestone plan](literature-interop-plan.md), approved in
[003](../003-plan-gate.md), supplies the LX2 scope. The
[LX1 record](../005-phase-LX1.md) supplies the rooted resolver, canonical
flat model and origin bytes. The
[LI0 record](../../literature-identity/003-phase-LI0.md) supplies the existing
legacy re-entry and identity controls. This spec has no independent review.

## Obligations

| Source | Requirement | Evidence |
|---|---|---|
| LX2.a | Produce and replay using the LX1 flattening, with and without a reference-free composition record. Distinguish fact and model origins. | T1–T5 |
| LX2.b | Stale include replay is exit 3 with `binding-stale`. Legacy v1/v2 proofs and producer bytes retain their existing contracts. | T5, T7 |
| Plan §7 | Keep direct authored include bytes guarded where no trusted root exists. | T6 |
| Plan §§0, 2 and 5 | Shared bounded origin producer, exact binding and one normative contract. | Design and T8 |
| Plan §§3, 6 and X3 | Give LX3 stable model origins before it adds reference-backed composition provenance. | D2, T3 |
| Plan §9 | Direct and focused witness, replay, schema and include consumers, plus structural and lint gates. | Verification ledger |

## Standing rules

- **Totality.** Apply the existing witness byte, list, nesting, numeric and
  structural gates before graph traversal. Compare caller flat/record
  artifacts as bounded opaque bytes. T8 exercises malformed and oversized
  inputs at both boundaries.
- **Input-bounded work.** Build one fact-origin map from the resolver's
  existing origin list, then visit each proof node once. T8 times the
  added layer and hits the stamped certificate byte ceiling.
- **Validation order.** Freeze the order between syntax, flat binding,
  composition binding and proof checking. Pair stale and forged data in T5.
- **One policy walk.** Model origins use one lookup by fact-type identity
  for base and rule nodes and by rule fact-type identity for comparisons.
- **One normative home.** The witness contract owns certificate v3 and
  replay exits. It cites the representation format for the existing
  flattening record and origin semantics.
- **Measure representation.** Preserve the selected legacy wire bytes and
  confirm v3 runtime/JSON Schema behavior on actual certificates. T4, T7
  and T8 exercise the independent validator and semantic mutations.

## Goal

Run `gnd witness ROOT POP --targets TARGETS --raw --out CERT` and
`gnd replay ROOT POP CERT --raw` on the authentic include model, with or
without a reference-free `--composition RECORD`. Both commands exit 0 on the
valid fixture. Replay independently checks model origin, occurrence origin,
composition lineage and the existing inference work limits.

## Design

| Capability | Searches | Reuse or adaptation |
|---|---|---|
| Read and bind include roots, flat bytes and origin metadata | `model pinned includes flatten projection addresses`, `path resolved vocabulary record provenance`, and `rg 'flatten_model\|_authored_sha256' src/gnd` | Reuse `model.loading`, `model.document` and LX1's `flatten_model`, plus the descriptor-bound artifact reader. |
| Produce and independently replay grounded witness | `witness replay certificate producer canonical binding`, `grounded proof origin verified graph` | Adapt `witness.service`, `witness.schema`, `witness.produce` and `witness.replay`. Preserve the existing proof extraction and evaluator. |
| Bind candidate population to source facts | `rg '_composition_lineage\|lineage_index' src/gnd` | Reuse the existing composition record reader and source index. Its v2 record already binds authored root and candidate bytes. |

### CLI path boundary

Witness and replay accept optional paired `--flat-model PATH` and
`--flattening-record PATH`. The model positional argument remains the
authored root. Both supplied paths must bind to that root's re-derived
LX1 artifacts. One option alone is usage exit 64. If the options are
omitted, derive the same bindings from the rooted model in memory. A flat
artifact presented as the root cannot establish an origin binding. The
ordinary include-free routes preserve their certificate and API signatures.

Use the resolved root's model and population coordinates to verify a
supplied reference-free composition record, then pass the canonical flat
document to the existing witness intake. Relative references, where
admitted by the standalone witness route, retain the authored-root
coordinate. The composed reference-catalog route stays under LX3's gate.
The unrooted model-document intake and why-not preserve their guards.

### Wire and replay

Certificate v3 binds the LX1 flattening record by its unprefixed lower-case
SHA-256. The binding has the v1 fields plus `flattening_sha256` and uses
`composition_sha256` only on the composed route. V1 and v2 retain their
existing exact keys and version restrictions. A v3 node adds a
`model_origin` object with the exact LX1 origin keys:

```json
{
  "origin": "includes[components]",
  "original_address": "$.fact_types[0]",
  "composed_address": "$.fact_types[0]",
  "element_id": "component_uses_component"
}
```

Proof-side `base.origin` and composed `base.sources` remain separate.
A comparison node uses the declaring rule fact type's origin. The replay
path supplies independently derived origins from the authenticated root.
A structurally valid forged model origin gives proof-invalid exit 1, just
as a forged base fact coordinate does. Wrong bound bytes or a v3 proof
presented without its needed resolved root context yield `binding-stale`,
exit 3. Arbitrary malformed documents retain the existing input-invalid
exit 3, and budget refusal retains exit 4. Recompute certificate budget
after stamping provenance.

Shape changes apply in the two shipped witness certificate schema copies and
the embedded certificate definition of the witness result schema. Retain
the v1/v2 validation rules. Existing redacted results retain closed
metadata selection. Raw views retain v3 origins on the same bounded route.

### Refusal order

The CLI checks option pairing. Replay parses the certificate before the
path service authenticates root, includes, flat bytes and record. Bind
composition to the same root and population before kernel replay compares
digests and semantic origins. The independently checked proof graph follows
only after current binding. Tests pair a stale input with valid-schema
forged provenance, and a malformed certificate with stale input.

## Decisions

| ID | Proposed ruling | Status |
|---|---|---|
| D1 | New v3 fence for model provenance, keeping v1/v2 exact wire. | Delegated approval (auto=true), 2026-11-15 |
| D2 | Keep model provenance entirely separate from candidate/reference fact origins and composition source rows. | Delegated approval (auto=true), 2026-11-15 |
| D3 | Use optional paired CLI artifact paths with root-derived defaults, avoiding a temporal extraction dependency for LX4's checking root. Keep existing public Python wrapper signatures. | Delegated approval (auto=true), 2026-11-15 |
| D4 | Use the LX1 fixture verbatim for base witnesses and an LX2 successor retaining both pins plus an owned derived fact type to exercise proof nodes from both ownership kinds. | Delegated approval (auto=true), 2026-11-15 |

## Tests and verification

| ID | Observable check |
|---|---|
| T1 | Extract the original two-include LX1 fixture. Produce and replay a v3 base witness using the actual artifact paths. Both commands exit 0. |
| T2 | Add an owned root derivation in a separate successor fixture. Assert base/rule origins from both root and include, then independently forge a model origin or a base origin and assert exit 1. |
| T3 | Run through existing composition entry points behind a reference-free record. Verify composition digest and per-fact source coordinates. Forge a source coordinate with model origins fixed and expect exit 1. |
| T4 | Round-trip v3 through raw view, CLI certificate parsing, both certificate schemas and result schema. Reject unknown and missing model-origin fields. |
| T5 | Replace a flat file or record while keeping authenticated root fixed. Separate controls change a pinned include, update a valid authored root/pins under an old witness, and pair stale binding with a valid-schema forged origin. Replay exits 3 with binding-stale. |
| T6 | Direct byte intake on authored include declarations retains the existing refusal. Unpaired CLI paths exit 64. Include-free roots cannot opt into model origins by presenting arbitrary files. |
| T7 | Compare pinned v1 and v2 produced bytes, replay pre-change v1/v2 certificates, and validate existing redaction and work limits. |
| T8 | Exercise malformed/deep certificates and capped flat/record files. Run a predeclared time-bound origin walk and cap refusal after stamps. |

| Gate | Disposition | Command and impact |
|---|---|---|
| Direct and consumers | Run, expect 0 | `uv run pytest -q tests/test_lx2_witness_flattening.py tests/test_witness_composition.py tests/test_public_replay_admission.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_li0_witness_wire.py tests/test_lx1_flattening.py --tb=short`. Pin any additionally affected witness-view and schema consumers after source inventory. |
| Structure, lint and component index | Run | Project guard list, whole-tree Ruff, changed-file Ruff with retained baseline comparison if needed, and `python3 scripts/components_index.py changed --base <LX2-base> --strict`. |
| Broad historical, reserved and certification lanes | Cadence | Select only under their documented triggers. Current wire controls discharge the declared local compatibility claims. |

## Phase boundary

LX2 proves include-root witness and replay and the model-origin axis for
reference-free composition. LX3 owns catalog-backed composition and mixed
fact provenance. LX4 owns checking-model rebinding and the full public
example. Other include-bearing routes retain their admission policy.

## Size

Estimate 210 Python source lines, 200 schema/test and fixture lines, and
affected documentation and generated component catalog entries.

## Approval instrument

Corpus-first. Planned entry point `tests/fixtures/lx2-witness-flattening/README.md`,
with expected outputs in a separate answer file. Commit the named red tests
and corpus before runtime changes. Independent phase-diff review is a
separate gate.
