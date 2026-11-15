# Phase LI0 · witness intake for version-1 models · spec r1

## 1. Status

**Draft, awaiting the plan gate and then this spec's owner gate (2026-11-14).**
No implementation has started. `auto=false`.

## 2. Provenance

- **Source.** Derived from [plan r1](literature-identity-plan.md) §§2, 4 and 9
  (LI0, W1–W3) and from [#193 part 9](https://github.com/vasiloglou/gnd-public/issues/193).
- **Review.** No review has run over this spec. The plan review requested on
  2026-11-14 reviews the plan only. A plan-review opinion is not an opinion
  over these bytes.
- **Baseline.** `ecd12986`.
- **Repairs, 2026-11-15.** This spec follows plan r2 (`(p2)` tags). Round 1
  of the plan panel found that `gnd.documents.Model` already omits some empty
  defaults. A new projection beside them would be a third home for that rule.
  D1 below is re-argued on that basis. W3's "unchanged" now means equal to
  golden digests committed from the baseline. These repaired bytes carry no
  review opinion.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #193 part 9, criterion 1 | A version-1 fixture produces a witness and replays it | §6 design, T1 and T2 |
| #193 part 9, criterion 2 | A regression test covers the serialization path | T4 |
| #193 part 9, "Expected" | An unsupported version-1 case names its fix instead of a bare `input-invalid` | §6 "Refusals", T6 |
| Plan §9, local reproduction | A model without `model_id` witnesses at any version | T3 |
| Plan §9, local reproduction | `why-not` shares the dump site | T5 |
| Plan W3 | Witness bytes for inputs already supported are unchanged | T7 |
| Project hook | Guard list, lint and component index check | §8 gate |

## 4. Standing rules bound to this phase

1. **Totality.** `model_wire` takes a loaded `gnd.documents.Model`, not
   arbitrary JSON. Its output then goes through the unchanged total reader
   `intake`. T8 hands intake hostile JSON to show that reader still refuses
   at 3.
2. **Input-bounded work.** The projection is linear in the model document. It
   adds no step that depends on the input's size beyond one shallow copy. No
   new time-bound test is needed. The existing witness byte ceilings still
   apply.
3. **Validation order.** Unchanged: guard, then structure, then load. T6 pins
   that an include-bearing model still reports its `include:` reason before
   any version question.
4. **One walk per policy.** One function serves both dump sites. Its name and
   home are in §6. `tests/test_li0_witness_wire.py` asserts that no
   `model.model_dump(` call stays in `src/gnd/witness/`.
5. **One home per contract.** The witness contract stays in the `gnd-export`
   witness reference. This phase changes no wire field, so no document
   changes beyond a release note.
6. **Measurement.** Measure the global alternative, omitting empty
   `operations` and null `model_id` in `Model`'s own serializer, before
   choosing (§7 D1). The measurement is recorded below before it runs.

## 5. Goal

`gnd witness MODEL POP --targets T --raw --out W` exits 0 on a valid
version-1 model, and so does `gnd replay MODEL POP W`. Both exit 0 on a model
with no `model_id`, at versions 1 and 2. `gnd why-not` exits 0 on the same
inputs. Witness bytes for every input that was already accepted are unchanged.

## 6. Design

The design below is reading (a) of D1. Under reading (b), the same two
omissions move into `gnd.documents.Model`'s existing hooks, and the two dump
sites stay unchanged. `(p2)`

**`src/gnd/witness/io.py`**, about 20 added lines, adds:

```python
def model_wire(model: Model) -> dict[str, Any]:
    """The authored-shape document of a loaded model, for re-entry into intake.

    Omit loader defaults that the meta-schema would refuse or that the
    author did not write: ``model_id`` when None, and ``operations`` when
    empty. Keep every other field exactly as ``Model.model_dump(mode="json",
    exclude={"warnings"})`` gives it.
    """
```

- The function sits beside `population_wire`, the existing projection of the
  same kind.
- `deontic_notes` and `rejected_proposals` stay as dumped. Their empty lists
  are accepted at every version today, and T4 confirms that.

**Dump sites replaced.** At each one, the call
`model.model_dump(mode="json", exclude={"warnings"})` becomes
`model_wire(model)`:

- `src/gnd/witness/producer.py:197`;
- `src/gnd/witness/service.py:252`, the why-not path.

Three paths need no change, because they parse raw bytes: replay through
`service.replay_result` (it passes `md`), the Soufflé export (`admit`) and the
Lean export. T2 confirms the replay case.

**Refusals.** No new reason code. A model the projection cannot carry is
still `input-invalid`. The issue's "names the fix" expectation is met because
no valid version-1 case stays unsupported. T6 includes an include-bearing
model to show that reason ordering is unchanged.

**Layering.** `witness.io` already imports the model layer. No new edge, and
`tools/gnd_layers.json` is unchanged.

## 7. Decisions

| ID | Question | Readings | Cost |
|---|---|---|---|
| D1 | Where the default-omission rule lives | (a) `model_wire` in `witness/io.py`. (b) Extend the existing omission hooks in `gnd.documents.Model` (`model_dump`, which drops `reference_populations`, and `_omit_empty_include_fields`) to omit null `model_id` and empty `operations` everywhere | (b) keeps one home but can move digests over dumps elsewhere. The `operations` comment in `documents.py` promises byte identity for version-1 documents. Under (a), `model_wire` must call the existing hooks and add only the two witness-specific omissions, with a test that lists every omission. Recommend (b) if the measurement below moves nothing, otherwise (a) `(p2)` |
| D2 | Should `model_wire` also omit an empty `source: {}`? | Keep it, since the schema accepts it today, or omit it as an unauthored default | No difference in exit code. Keeping it is the smaller change |

### Experiment recorded before it runs

- **Measures:** apply reading (b) on a scratch branch and run the focused
  lane plus the structure guard list. Any red test is a digest or byte
  dependency on the current dump.
- **Cannot measure:** consumers outside this repository.
- **Liveness:** one test must go red with (b) for a known dependency, or the
  experiment shows no dependency inside the lane. Either result is recorded.
- **Limit:** it decides D1 only for in-repository consumers.

## 8. Tests

The file is `tests/test_li0_witness_wire.py`, with its fixtures under
`tests/fixtures/li0/`.

| # | Case | Expected |
|---|---|---|
| T1 | Version-1 grandparent model with `model_id`: `gnd witness --raw --out` | exit 0, certificate written |
| T2 | Replay of T1's certificate | exit 0 |
| T3 | Same model without `model_id`, at versions 1 and 2: witness, then replay | exit 0 and exit 0, for each version |
| T4 | Round trip: every loadable `tests/fixtures/**/*.orm.yaml` without includes, with `load` then `model_wire` then `load_model_bytes`, gives an equal `model_dump` | all equal. The test reports how many fixtures it walked, with a floor of 200. The baseline count on 2026-11-14 is 224 loadable models without includes, out of 285 files |
| T5 | `gnd why-not --fact-type` on T1 and T3 | exit 0, `mode` is `rule` |
| T6 | An include-bearing model through witness | the existing `include:` reason, exit 3, unchanged |
| T7 | Witness certificates for the version-2 inputs in `test_witness_composition.py` and the v7.1 witness corpus | equal to golden SHA-256 digests in `tests/fixtures/li0/golden.json`, generated at `ecd12986` and committed before the change `(p2)` |
| T10 | Every version-gated default in the `allOf` of `orm-meta.schema.json` is omitted when empty | passes `(p2)` |
| T8 | `intake` with hostile JSON (NaN, deep nesting, a long integer) | exit 3, no traceback |
| T9 | Source scan: no `model.model_dump(` left under `src/gnd/witness/` | passes |

**Branch walk.**

- The projection has two omission branches, null `model_id` and empty
  `operations`. T1 covers `operations` alone, and T3 covers both together.
- A version-2 model that has operations keeps them. T4 covers this through
  the version-2+ fixtures that declare operations.

**Gate.**

```bash
uv run pytest -q tests/test_li0_witness_wire.py tests/test_witness_composition.py tests/test_public_why_not.py tests/test_public_replay_admission.py tests/test_public_optional_value_witness.py tests/test_public_v71_witness_corpus.py --tb=short
```

Also run the structure guard list from the project hook, `uv run ruff check`
and `python3 scripts/components_index.py changed --base main --strict`.

## 9. Out of scope for this phase

- Any wire or reason-code change to witness, replay or why-not.
- Include-bearing models in witness. That is literature-interop LX2.
- Temporal models.
- Upgrading models.
- Any change to the meta-schema's version rule.

## 10. Size

About 20 source lines and 150 test lines, plus three small fixture files.

## 11. Approval instrument

This prose. The fixtures are small and their expected exits are in §8, so no
separate corpus is needed.
