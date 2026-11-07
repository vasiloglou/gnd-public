# Phase FU2: population header integrity (issues 115, 116)

## 1. Status

**Owner-decided (2026-11-07); approval pending on the red tests.** The
owner ruled D1-D4 over r1 (commit 1842579c) with "Approve as proposed",
answering "How do you rule on FU2's decisions D1–D4?". Under D1 the test
file lands red before any source edit, and implementation waits for the
owner's approval of it. `auto=false`. Prior status (r1): "Draft r1,
awaiting the owner gate."

## 2. Provenance

- Plan r3 §4 FU2, completion predicate 2; §9 FU2 row; §6 first risk row.
- Issue 115 (RC5 review T5): `model_copy` bypasses the producer invariant.
- Issue 116 (RC5 spec F2): the reference binder drops `label`.
- Plan review P3 (`model_construct`) and P4 (digests, witness binding).
- Base: main `12daa5b7` (FU1 merged).

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan FU2-C1 | validated construction and `model_copy` cannot produce a producer without `tool-output`; `model_construct` in or out by decision, with a case either way | M1, T1, T2, T3 (D3) |
| plan FU2-C2 | `label` survives `_combine_validated_populations` and `bind_population`; the candidate's label wins; a conflicting-labels case; the combined content digest change pinned; the witness candidate binding pinned unchanged | M2, T4-T7 |
| plan FU2-C3 | digests unchanged where `label` is unset; where set, every recorded digest that moves is listed before code | §6 digest survey, T6, V3 |
| plan §9 FU2 row | new FU2 tests + `tests/test_rc5_tool_output.py tests/test_population_load.py` | V2 |
| §0 rule 1 (frozen variants) | no report's bytes change | §6 survey, V3 |
| §0 rule 2 (measure) | both defects reproduced before code | §5 probes; T1, T4 red first |
| §0 rule 3 (shims) | no name moves or retires | n/a: M1 adds an override, M2 adds a key |
| §0 rule 4 (one home) | the fix lands in `population.py` and the binder | M1, M2 |
| §0 rule 5 (size) | pause past 1.5 × (20 source, 80 test lines) | §10 |
| §6 risk "a recorded digest moves" | listed before code; full suite | §6 survey, V3 |
| §7 out of scope | GR-D4, GR-T17, new report versions | §9 |
| FU1 record | nothing inherited (FU1-O1 concerns derivation rows) | — |
| AGENTS.md | component index; layers map unchanged | V6 |

## 4. Goal

No `Population` reachable through validated construction or `model_copy`
carries a `producer` unless its `source` is `tool-output`, and a population
combined with its references keeps the candidate's `label`.

## 5. Probes (2026-11-07, `12daa5b7`)

- **115.** `Population(model='m', source='tool-output', producer='x').model_copy(update={'source': 'fixture'})`
  → `fixture x`; `Population(model='m', source='fixture').model_copy(update={'producer': 'y'})`
  → `fixture y`; `update={'producer': ''}` → `''`. No error in any.
  `Population.model_construct(source='fixture', producer='z')` → built, no
  error.
- **Exposure of 115.** `check` refuses any population without a matching
  validation marker. A `model_copy` that changes `source` or `producer`
  changes the content digest, so the marker no longer matches and `check`
  refuses it too (`UnvalidatedPopulationError`, exit 70, measured for
  `model_construct` and for an unstamped population). The broken pair is
  therefore reachable only by in-process consumers that dump or read the
  header without checking. No source caller updates `source` or `producer`:
  the two `Population.model_copy` callers update `facts` only
  (`extensions.py:2711`, `witness/why_not.py:274`).
- **116.** `tests/fixtures/reference-corpus/dispatch`, its candidate with
  `label: violating`, through `bind_references` and `bind_population` →
  `candidate.label == 'violating'`, `combined.label is None`. The binder
  builds the header without `label` (`model/__init__.py:697-704`), and
  `_combine_validated_populations` does not read it
  (`population.py:495-506`).

## 6. Design

**Reuse table** (searched 2026-11-07 at `12daa5b7`:
`components_index.py search "population producer invariant copy"`,
`"reference binder combined population label"`).

| Capability | Found | Decision |
|---|---|---|
| the producer invariant | `Population._producer_names_tool_output` (`population.py:159`), callable on an instance (probe: raises the same `ValueError` on a bad copy) | **reuse** on the copy; no second statement of the rule |
| the combined header | the binder's header dict and `_combine_validated_populations` | **adapt**: carry `label` the way RC5 carried `producer` |
| the content digest | `values._content_digest`, which already covers `label` | **reuse** unchanged |

**M1. `population.py`, about 10 lines (D2 (a)).** `Population` overrides
`model_copy`: it calls the parent and, when `update` is given, runs
`_producer_names_tool_output` on the copy before returning it, so a bad
pair raises the same `ValueError` message construction raises (as a
`ValueError`, not a pydantic `ValidationError`, because no field validation
ran). A copy without `update` is returned unchanged: it cannot alter the
pair. Private attributes (the validation marker) are kept, as today.

**M2. Binder and combiner, about 4 lines.** The binder's header gains
`**({"label": candidate.label} if candidate.label is not None else {})`,
beside `producer`. `_combine_validated_populations` passes
`label=header.get("label")`. Reference populations' labels are ignored, as
their `source` and `producer` are: the candidate's header is the combined
header.

**Digest survey (FU2-C3, before code).** `values._content_digest` dumps
every field except `warnings`, so `label` is already in it (`'label': None`
when unset). Effects:

- `label` unset: the combined header is unchanged, so the combined content
  digest is byte-identical (T6).
- `label` set: the combined content digest moves from the digest of a
  `None` label to the digest of the candidate's label. This digest is an
  in-process marker: its consumers are the validation stamp
  (`population.py:204, 244`), the `api` check receipt (`api.py:224, 248`,
  an in-memory object) and `verbalize_population.py:150` (a comparison of
  two in-process values). One recorded set exists:
  `tests/fixtures/rf1-pins/goldens/helpers/sha256_hex_gnd.population__content_digest.json`
  pins the digest of each shipped example population as loaded. Loading is
  unchanged (the loader already passes `label`), so it cannot move; its
  test is in V2b. No other recorded population content digest was found in
  `tests/fixtures` or `docs`; the full suite (V3) is the check.
- The witness candidate binding (`witness_input_identity`) hashes the
  original candidate, not the combined population
  (`witness/producer.py:202`), so it does not move (T7).
- The model digest does not involve populations.
- No report carries a population's `label`; no report's bytes change.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **tests-first, red**: the case table in §8 lands as a committed red test file before any source edit, and the owner approves it, as FU1's corpus was approved. FU2 is a validation predicate, so prose alone is not proposed; there is no serialized format to put in a fixture corpus beyond the existing reference fixture **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU2's decisions D1–D4?"). |
| D2 | How does a copy keep the invariant? | **(a) re-run the invariant on every `model_copy` with `update`** (M1): one statement of the rule, any field update covered. (b) refuse `update` keys `source` and `producer`: narrower, still allows nothing bad, but a second rule to keep in step **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU2's decisions D1–D4?"). |
| D3 | `model_construct` | **out of scope**, with a case: it is pydantic's documented unvalidated constructor, and T3 pins that a population built this way with a bad pair has no validation marker and `check` refuses it. Overriding it would change a pydantic contract other code may rely on **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU2's decisions D1–D4?"). |
| D4 | Review over the spec bytes | none; the diff gets the Codex review **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU2's decisions D1–D4?"). |

## 8. Tests and verification ledger

New file `tests/test_fu2_population_header.py`.

| T | Case | Expected | Red before code? |
|---|---|---|---|
| T1 | `model_copy(update=...)` producing (a) `fixture` + producer, (b) producer on `fixture`, (c) empty producer, (d) a 201-character producer | each raises `ValueError` with construction's message | yes |
| T2 | `model_copy` that keeps a valid pair: no update; `update={'facts': ...}` on a `tool-output` population; `update={'source': 'fixture', 'producer': None}` | returns the copy; the marker is kept when content is unchanged (no update) | no (non-regression) |
| T3 | `model_construct(source='fixture', producer='z', ...)` (D3) | builds; `matches_validation_marker` is false; `api.check` exit 70, `UnvalidatedPopulationError` | no (pins the boundary) |
| T4 | the dispatch candidate with `label: violating`, through `bind_population` | `combined.label == 'violating'` | yes |
| T5 | conflicting labels: candidate `violating`, a reference `conforming`; and candidate unset, reference `conforming` | combined `violating`; combined `None` | first yes, second no |
| T6 | combined content digest | unset label: equal to the digest before the change (recomputed from a header without `label`); set label: equal to `_content_digest` of the combined population and different from the unset-label digest | set: yes |
| T7 | witness candidate binding for a labelled candidate with references | `witness_input_identity` equal before and after (computed from the candidate) | no (pins it unchanged) |
| T8 | `_combine_validated_populations` directly, header with `label` | result carries it (RC5 T3's route) | yes |

Mutants to run at implementation: M1 removed (T1 red); M2's binder half
alone and combiner half alone (T4 red each).

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V1 | merge-base record | inherited: the base suite at `6651e5a4` and FU1's run at `9f938f48` | `evidence/FU1/full-suite-*.txt`; the merged tree `12daa5b7` differs only by FU1 and PR 122 |
| V2 | plan §9 FU2 row | run | `uv run pytest -q tests/test_fu2_*.py tests/test_rc5_tool_output.py tests/test_population_load.py` |
| V2b | impact closure | run | tests that import `bind_population`, `_combine_validated_populations`, `witness_input_identity`, or call `model_copy` on a population |
| V3 | full suite vs base | run, sharded on beast-3 | failure set equal to the base's (`8261732b…`) |
| V6 | component index | run at record time | `components_index.py changed --base 12daa5b7 --strict` |

## 9. Out of scope

Issues 111 and 112 (split out); `model_construct` (D3); validating other
field types on copy, e.g. `update={'source': 'bogus'}` (the invariant
covers the pair only; field types are pydantic's); any report change.

## 10. Size

Plan estimate: about 20 source and 80 test lines. This spec: about 14
source lines (M1 10, M2 4) and about 100 test lines. Stop rule: pause past
30 source or 120 test lines.

## Implementability sweep (author inspection)

- M1: the validator is callable on an instance (probe), and `model_copy`
  is a public pydantic method that can be overridden with the same
  signature; the two source callers pass `facts` only, which T2 keeps
  working.
- M2: the binder already conditionally adds `producer`; `label` follows the
  same shape. `_combine_validated_populations` has one caller.
- T7: `witness_input_identity` is importable and computed before binding.

## Red tests (2026-11-07, at `12daa5b7` plus this file)

`tests/test_fu2_population_header.py`, 12 cases: **8 failed, 4 passed**,
exactly as §8's "red before code?" column says. Failing: T1 (a)-(d)
("DID NOT RAISE"), T4 and T5 candidate-wins (`combined.label` is `None`),
T6 (the labelled combined digest equals the unlabelled one, `da473037…`),
T8. Passing: T2, T3, T5 unset-candidate, T7. The two pinned values (the
unlabelled combined digest and the labelled candidate's witness identity)
were measured at `12daa5b7`. T5 relabels a copy of the dispatch reference
in `tmp_path` and updates its declared sha256; the committed fixture is
untouched.
