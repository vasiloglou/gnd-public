# Phase LI0 · witness intake for version-1 models · spec r2

## 1. Status

**Owner-decided (2026-11-15).** The owner approved r2 at SHA-256 `a8015970…106f9`
([002](../002-phase-LI0-spec-gate.md)), ruled D1–D4 as proposed, chose no
spec review, and gave the go-ahead. Implementation is in progress.
`auto=false`.

## 2. Provenance

- **Source.** Derived from [plan r3](literature-identity-plan.md), SHA-256
  `5ad5b74485a442a8e9fa09ed59c28a4463b812a4119ea6f2959c56cdda7c90de`, which
  the owner approved on 2026-11-15. The sections used are §2 LI0, §3, §4
  (W1–W3) and §9. The other source is
  [#193 part 9](https://github.com/vasiloglou/gnd-public/issues/193).
- **Review.** No review has run over this spec. The two plan-panel rounds
  reviewed plan r1 and r2 only.
- **Baseline.** `ecd12986`.
- **Revisions.**
  - r1, 2026-11-14: first draft.
  - `(p2)`/`(p3)` edits, 2026-11-15: carried plan-review findings into D1, W3
    and T10/T11.
  - r2, 2026-11-15: completes the step-1 contract. It binds the approved
    plan, adds the verification-selection ledger and records the
    implementability sweep (§12). It also corrects T4's equality after a
    measured finding.
- None of these bytes carries a review opinion.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #193 part 9, criterion 1 | A version-1 fixture produces a witness and replays it | T1, T2 |
| #193 part 9, criterion 2 | A regression test covers the serialization path | T4, T9 |
| #193 part 9, "Expected" | An unsupported version-1 case names its fix instead of a bare `input-invalid` | §6 "Refusals", T6 |
| Plan r3 W1 | A version-1 model and a model without `model_id`, at versions 1 and 2, witness (exit 0) and replay (exit 0) | T1, T2, T3 |
| Plan r3 W2 | `why-not` on the same inputs exits 0 with its derivation result | T5 |
| Plan r3 W3 | Round trip over the committed fixture models. Golden digests from `ecd12986` for certificate bytes and for legacy-repr and canonical identities, including models without `model_id` and models with reference populations and no operations | T4, T7, T11 |
| Plan r3 §2 LI0 | One home for default omission. The global `Model` hooks are excluded because they feed `values._model_digest` | §6, D1, T9, T10, T11 |
| Plan r3 §9 LI0 row | Focused lane plus the named consumers | §8 ledger |
| Plan r3 §0 | Six standing rules, ModelIndex, layers | §4 |
| Plan r3 §8 | Spec gate, focused gate plus guard list, `ruff`, independent diff review, refactoring review, record | §8 ledger, §11 |
| Project hook | Guard list, lint, component index `changed --strict` | §8 ledger |

## 4. Standing rules bound to this phase

1. **Totality.** `model_wire` takes a loaded `gnd.documents.Model`, never
   arbitrary JSON. Its output enters the unchanged total reader `intake`. T8
   gives `produce_witness` a model whose wire document contains NaN, deep
   nesting and a long integer literal. It must return exit 3 with no
   traceback.
2. **Input-bounded work.** The projection is one `model_dump` plus two key
   removals: linear, and already performed today. It adds no step that grows
   with the input, so no new time-bound test is needed. The existing witness
   byte ceilings still apply.
3. **Validation order.** Unchanged: include guard, then structure, then load.
   T6 shows that an include-bearing model still reports its `include:` reason.
4. **One walk per policy.** One function serves both dump sites. T9 asserts
   that no `model.model_dump(` call is left under `src/gnd/witness/`.
5. **One home per contract.**
   - **Default omission.** It keeps two homes, with no third. The existing
     `Model` hooks omit `reference_populations`, `includes` and
     `fact_type_constraints`. `model_wire` adds only the two omissions that
     witness intake needs, and it is not a general serializer.
   - **Witness contract.** It stays in the `gnd-export` witness reference, and
     no wire field changes.
6. **Measurement.** D1 was settled by reading the identity code, and the
   liveness experiment below confirms it. The T4 equality was set by
   measurement (§12).

ModelIndex and family dispatch are not touched. The layer map is unchanged.

## 5. Goal

`gnd witness MODEL POP --targets T --raw --out W` exits 0 on a valid
version-1 model, and so does `gnd replay MODEL POP W`. Both exit 0 on a model
with no `model_id`, at versions 1 and 2. `gnd why-not` exits 0 on the same
inputs. Certificate bytes for already-accepted inputs, and the legacy-repr and
canonical identities of every fixture model, equal golden digests generated at
`ecd12986`.

## 6. Design

**`src/gnd/witness/io.py`**, about 20 added lines, adds:

```python
def model_wire(model: Model) -> dict[str, Any]:
    """The authored-shape document of a loaded model, for re-entry into intake.

    Start from ``model.model_dump(mode="json", exclude={"warnings"})``, which
    already applies the Model hooks (no empty ``reference_populations``,
    ``includes`` or ``fact_type_constraints``). Then remove the two loader
    defaults that witness intake would otherwise refuse: ``model_id`` when it
    is None, and ``operations`` when it is empty.
    """
```

- The function sits beside `population_wire`, the existing projection of the
  same kind.
- `source`, `deontic_notes` and `rejected_proposals` stay as dumped. Empty
  values of these are accepted at every version today, and T4 shows it. This
  is D2.
- `gnd.documents.Model` is not edited (D1).

**Dump sites replaced.** At each one, the call
`model.model_dump(mode="json", exclude={"warnings"})` becomes
`model_wire(model)`:

- `src/gnd/witness/producer.py:197` (`produce_witness`);
- `src/gnd/witness/service.py:252` (the why-not path).

**Not changed.** These paths re-serialize nothing, because they parse raw
bytes:

- replay through `service.replay_result`, which passes the parsed document
  `md` to `replay_witness`;
- the Soufflé export (`export/souffle.py` `admit`);
- the Lean export (`export/lean.py`).

T2 confirms the replay case.

**Refusals.** No new reason code. The issue's "names the fix" expectation is
met because no valid version-1 case stays unsupported. T6 pins that reason
ordering is unchanged.

**Layering.** `witness.io` already imports the model layer. No new edge, and
`tools/gnd_layers.json` is unchanged.

**Components.** `witness` components gain one symbol. The index entry
covering `src/gnd/witness/io.py` is re-read and updated in the same commit.

## 7. Decisions

| ID | Question | Readings | Cost | Ruling |
|---|---|---|---|---|
| D1 | Where the two extra omissions live | (a) `model_wire` in `witness/io.py`. (b) Extend the `gnd.documents.Model` hooks everywhere | Under (b), `values._model_digest` (`values.py:193`) hashes `Model.model_dump`, and `model_identity_matches` (`values.py:328`) compares it with pinned identities. So (b) would move every legacy identity of a model without `model_id` | **Proposed: (a).** Ruled (a) `(o)` 2026-11-15 |
| D2 | Omit an empty `source: {}` as well? | Keep it, or omit it as an unauthored default | No exit difference. The schema accepts it today, and T4 shows all 224 fixtures round-trip with it kept | **Proposed: keep.** Ruled keep `(o)` 2026-11-15 |
| D3 | Approval instrument | Prose plus golden digests committed red-first, or a separate narrated corpus | See §11 | **Proposed: prose plus goldens.** Ruled prose plus goldens `(o)` 2026-11-15 |
| D4 | Diff review instrument | One reviewer in a different tool (shared default), or the panel | The plan sets no per-phase panel. A panel costs a six-seat run | **Proposed: one reviewer (Codex).** Ruled one reviewer (Codex) `(o)` 2026-11-15 |

### Experiment recorded before it runs

- **Measures:** on a scratch branch, apply reading (b) and run T11 and the
  focused lane.
- **Liveness:** reading the source predicts that T11 goes red for at least
  one model without `model_id`. If it stays green, the source argument for D1
  is refuted, and that is recorded as a refuted premise and returned to the
  owner.
- **Cannot measure:** consumers outside this repository.

## 8. Tests and verification-selection ledger

The tests are in `tests/test_li0_witness_wire.py`. The fixtures are in
`tests/fixtures/li0/`:

- `grandparent-v1.orm.yaml` and `grandparent-v2.orm.yaml`;
- the two variants without `model_id`;
- `population.json` and `targets.json`;
- `golden.json`.

`golden.json` is generated at `ecd12986` and committed **before** any source
edit. The tests that depend on the fix are committed red at that point.

| # | Case | Expected |
|---|---|---|
| T1 | Version-1 grandparent model with `model_id`: `gnd witness --raw --out` | exit 0, certificate written (red at baseline: exit 3) |
| T2 | `gnd replay` of T1's certificate | exit 0 |
| T3 | Same model without `model_id`, at versions 1 and 2: witness, then replay | exit 0 and exit 0, for each version (red at baseline) |
| T4 | Every loadable `tests/fixtures/**/*.orm.yaml` without includes: `load_model`, then `model_wire`, then `load_model_bytes`. Compare `model_dump(mode="json", exclude={"warnings"})` before and after | all equal. The test reports how many it walked, with a floor of 200. Baseline: 224 of 285 files |
| T5 | `gnd why-not --fact-type` on T1's model and both T3 models | exit 0, `mode` is `rule` (red at baseline: exit 3) |
| T6 | An include-bearing model through `gnd witness` | exit 3 with the existing `include:` reason, unchanged |
| T7 | Certificates for the version-2 inputs of `test_witness_composition.py` and the v7.1 witness corpus | SHA-256 equal to `golden.json` |
| T8 | `produce_witness` with a model whose wire document holds NaN, 70-deep nesting and a 200-digit integer | exit 3 result, no exception escapes |
| T9 | Source scan: no `model.model_dump(` call under `src/gnd/witness/` | passes |
| T10 | For each `allOf` conditional in `orm-meta.schema.json` keyed on an optional section (`operations`, `reference_populations`, `includes`, `fact_type_constraints`), `model_wire` of a model with that section empty omits the key | passes |
| T11 | `values._model_digest` and `model_identity` of every T4 model, of the two models without `model_id`, and of the 9 fixture models with reference populations | equal to `golden.json` |

**Branch walk.** The projection has two omission branches. Each is covered on
its own and together:

| Case | `model_id` | `operations` |
|---|---|---|
| T1 | present | empty, removed |
| T3, version 1 | null, removed | empty, removed |
| T4, version-2+ fixtures that declare operations | — | kept |

A wrongly removed non-empty `operations` fails T4.

**Ledger.**

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| W1–W3, T1–T11 | run | `uv run pytest -q tests/test_li0_witness_wire.py --tb=short`, exit 0 | `witness/io.py`, `producer.py`, `service.py`, `tests/fixtures/li0/`, `orm-meta.schema.json`, all fixture models | Direct tests of every criterion | Any change to those files or to `documents.py`/`values.py` |
| Witness, replay and why-not consumers | run | `uv run pytest -q tests/test_witness_composition.py tests/test_public_why_not.py tests/test_public_replay_admission.py tests/test_public_optional_value_witness.py tests/test_public_v71_witness_corpus.py tests/test_why_not_kernel.py --tb=short`, exit 0 | The two dump sites and every caller of `produce_witness` and why-not | These are the modules that reach the changed call sites | A changed witness, why-not or replay module |
| Structure guards (project hook) | run | the guard-list command in `project.md`, exit 0 | Repository structure, layers, skill manifests | Required for any change outside `.gnd-planning/` | Always run |
| Lint | run | `uv run ruff check`, exit 0 | Whole repository | Project gate | Always run |
| Component index | run | `python3 scripts/components_index.py changed --base ecd12986 --strict`, exit 0 | Changed modules | Project gate | Always run |
| Soufflé and Lean exports | inherit | Not executed by this phase. They parse raw bytes (§6) and no export module changes | `export/souffle.py`, `export/lean.py` | No changed input reaches them | A change to either export module |
| Evidence, census, native and provider lanes | cadence | `uv run pytest -q -m "evidence or census"` at the milestone-close lane | Historical bytes | Outside this phase's acceptance claim. The goldens cover the bytes this phase could move | Owner request |

## 9. Out of scope for this phase

- Any wire or reason-code change to witness, replay or why-not.
- Any edit to `gnd.documents.Model` or `values.py`.
- Include-bearing models in witness. That is literature-interop LX2.
- Temporal models.
- Upgrading models.
- Any change to the meta-schema's version rule.
- The pre-existing date-to-string effect of the JSON hop on YAML-authored
  provenance dates (§12). It is recorded, not changed.

## 10. Size

About 20 source lines and 220 test lines, plus six fixture files.

## 11. Approval instrument

Proposed (D3): **this prose, plus golden digests committed red-first.**

- **Why not a full narrated corpus.** The phase changes an exit-code contract,
  from exit 3 to exit 0 on version-1 inputs, so the project's default would
  be a corpus first. But the phase adds no serialized format, and its expected
  outputs are byte digests and exit codes, not narratable stories.
- **What stands in for it.** The goldens and the red tests are committed
  before any source edit, which serves the same purpose. They are the T1, T3
  and T5 exits at baseline and the T7 and T11 digests.

The owner rules D1–D4 and gives the go-ahead at this gate.

## 12. Implementability sweep, 2026-11-15

These measurements were taken on the baseline tree, read-only, with no
implementation file written.

- **Version-1 reload.** With `operations` and a null `model_id` removed from
  the dump, both version-1 fixtures reload. The `operations → version 2–5`
  rule in the `allOf` no longer applies.
- **The T4 round trip.**
  - **Python equality:** removing those two keys from every loadable fixture
    without includes gives 223 of 224 equal reloads.
  - **The exception:** `rof3-model-identity/models/dates-and-text.orm.yaml`.
    A YAML-authored provenance date loads as `datetime.date` and comes back
    as a string after the JSON hop.
  - **Why the JSON form is the right test:** witness intake has the same
    effect today, and it does not change verdicts.
  - **Result in JSON form:** comparing `model_dump(mode="json")`, all 224 are
    equal. T4 uses that form.
- **The `allOf` conditionals.** There are four: `operations`,
  `reference_populations`, `includes` and `fact_type_constraints` (T10).
- **Reproduction.** The baseline exits are recorded in plan r3 §9. They are
  T1, T3 and T5 red at exit 3 and the version-2 controls at exit 0.
- **Fixture counts.** 9 of the 224 fixtures have reference populations (T11).
