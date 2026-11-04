# Phase MG1: public rendering of derivation rules

**Status: r3, approved by the owner 2026-11-03 `(s1)`.** Implementation has
not started.

`(s1)` Owner approval, 2026-11-03, quoted: "Approve MG1 spec", in answer to
"Approve the MG1 spec r3 with its decisions as proposed?". Approved bytes:
SHA-256 `4cddaa525a9da4d237fa863f6c3af45dd162cddb286be87e46c299cc60fce87c`
(before this tag), the same bytes recorded in the plan gate
([001-plan-gate.md](../001-plan-gate.md)). Rulings: approval instrument prose;
no spec review panel beyond the two plan rounds; D1 (a), D2 (a), D3 (a), D4
(a), D5 (a) as proposed; D6 and D7 as already settled. The plan was approved
`(a1)` the same day.

## Provenance

- Plan: [model-growth-guardrails-plan.md](model-growth-guardrails-plan.md) r2,
  §2.1 and §4 MG1.
- Source: [issue #72](https://github.com/vasiloglou/gnd-public/issues/72)
  (GR-T9).
- Inspection baseline: `1446f90` (main after PR #79).
- r1 was read in plan review round 1 as SHA-256
  `d44bf94e68556bc4095d3291175bafb89b75f55343e27d8d40b8cafc8cd73dc6`; see the
  [round-1 disposition](plan-review-r1-disposition.md). r2 applies themes A,
  B, C, K, M, N, O, Q, R, S (T5 cases) and W at the owner's direction `(p1)`
  (quoted in the plan header). r2 was read in the confirmation round as
  SHA-256 `553724f84783b224b71bb9f9f26362f46271151f5059737c0abfdb8b782ce4cf`;
  see the [round-2 disposition](plan-review-r2-disposition.md). r3 applies
  theme R2-C (and R2-H's pin and inventory rows) under the declared stop rule,
  with no further round. **r3 bytes carry no review opinion.**
- `(p1)` rules theme B: the existing path-input crash is fixed here.

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Issue #72 "Asked for" | A public, deterministic renderer of derivation rules in GND's controlled language | Design: `gnd.api.verbalize_rules` |
| Issue #72 | Covers body atoms with bindings, negated atoms, comparisons, sibling clauses, declared aggregates, head projection | Reuse of `_derivation_cnl`; T2 construct floors |
| Issue #72 | A construct that cannot be expressed is reported, not rendered partially | `prose-rule` status; every other fallback shown unreachable by T4b |
| Issue #72 "Why" | GND's text is authoritative; a caller's copy must not drift | MG-R2; T3 parity against the full model verbalization |
| Plan MG-R1 | Existing digest-bound verbalizations unchanged | T7 recorded before/after table |
| Plan MG-R5 | Disclosure site table covers the new callable | `api:verbalize_rules` row; T8 |
| Plan MG-R6 | Layering and query policy | Reads through `ModelIndex`; T9 |
| Plan MG-R7 | Anonymity | T10 |
| Plan MG-R8 | Provenance never overstated | Not applicable: the renderer emits no provenance (argued below) |
| Theme B `(p1)` | `render_model_verbalization(path)` crashes on structured aggregates | Design: coerce once; T1b |
| Round 1 themes A, C, K, M, N, O, Q, R | repairs | as tagged `(r1-X)` below |

## Standing rules bound to this phase

1. **Totality:** `verbalize_rules` follows `gnd.api`'s conventions `(r1-K)`.
   A `Model` argument is re-validated with `validate_model_object`
   (`verbalize_population.py:28`), as `_run_verbalize` does
   (`api.py:833-834`); failure returns `exit_code` 3 `(r2-C)`. A
   `fact_types` argument that is not `None` or a list or tuple of `str`
   raises `TypeError`, as `api.check` does for argument types
   (`checking_service.py:55-61`). A model path that does not load, or loads
   and fails validation, returns `exit_code` 3. An id naming no fact type, or
   naming one without a `derivation_rule`, returns `exit_code` 3 with the id
   in the message. T5.
2. **Input cap bounds the algorithm:** one pass per selected rule. T11 counts
   **fact-type visits** and **`ModelIndex` constructions** on a generated
   model with 2,000 derived fact types: visits ≤ 2,000 + number selected;
   index constructions = 1 `(r1-Q)`.
3. **Validation order:** argument type (`TypeError`), then model load and
   validation (3), then ids (3), then rendering. T5's two-fault case pins it.
4. **One walk:** the renderer adds no second traversal. Classification has one
   branch (`prose-rule`); every other fallback is unreachable for validated
   models (T4b). `render_rule_verbalizations` passes a collector through
   `_derivation_cnl`, `_guarded_atom` and `_guarded_term` (default `None`,
   output unchanged) that records any fallback reached, and raises
   `VerbalizationError` instead of returning text when one was (T4c)
   `(r2-C)`.
5. **One home:** the rule grammar stays in `_derivation_cnl`. The reference
   page cites it and does not restate it.
6. **Measurement over argument:** parity is a recorded before/after digest
   table (T7), not a claim about suites.

MG-R3 and MG-R4 do not apply: no evolve path is touched. MG-R8 does not
apply: the renderer reads rules and writes no provenance.

## Goal

`gnd.api.verbalize_rules(model)` returns a payload with `exit_code` 0 and one
entry per derived fact type in stable id order. A structured rule has
`status: "rendered"` and `text` equal to `line_text(_derivation_cnl(rule,
model))`. In that fact type's line of `render_model_verbalization(model)`,
the text appears immediately after `This fact type is derived: ` and is
followed by ` Admission depends on `, ` Values of every role are redacted`,
or ` reading=`.
A prose rule has `status: "unsupported"` with reason `prose-rule` and no
`text`. `render_model_verbalization(path)` no longer crashes on structured
aggregates, and its output for every input that did not crash at `1446f90` is
byte-identical. The MG1 gate in §Tests exits 0.

## Design

### `src/gnd/model_verbalization.py` (about +45 lines, 1 line changed)

**Theme B fix.** In `render_model_verbalization`, the fact-type loop passes
the raw `model` argument to `_fact_type_cnl` (`:570`). When that argument is
a path, `analyze_declared_aggregate` calls `.get` on a string
(`_validation.py:1113`). The call passes `loaded` instead. Measured at
`1446f90`: 23 of the 118 corpus models crash when rendered by path; none
crashes when passed as a loaded `Model`.

**New public function**, in the same module so the grammar keeps one home:

```python
def render_rule_verbalizations(
    model: Model | str | Path,
    *,
    fact_types: Sequence[str] | None = None,
) -> tuple[RuleVerbalization, ...]: ...

@dataclass(frozen=True)
class RuleVerbalization:
    fact_type: str
    status: Literal["rendered", "unsupported"]
    text: str | None                 # None exactly when status == "unsupported"
    reason: Literal["prose-rule"] | None   # None exactly when status == "rendered"
```

`__all__` gains `RuleVerbalization` and `render_rule_verbalizations`. The
function coerces once with `_coerce_model`, builds one `ModelIndex`, iterates
`iter_fact_types_shared()` `(r1-O)`, and calls `_derivation_cnl(rule,
loaded)` for each structured rule.

**Fallback branches, settled `(r1-C)`.** Every partial-rendering or raising
path in `_derivation_cnl` and its helpers, with what validation does about it,
measured by mutating one rule in `bookrec/complete.orm.yaml` (the unmutated
control loads) and calling `load_model`:

| Branch (file:line at `1446f90`) | Mutation (each against its own nearest-valid control, which loads) | `load_model` |
|---|---|---|
| `_fact_type_cnl`, string `derivation_rule` (`:119-124`) | none: valid today, 19 corpus rules | **accepts** → reason `prose-rule` |
| `_guarded_atom`, non-dict atom (`:167-168`) | `body[0] = "x"` (control: `body` unchanged) | refused |
| `_guarded_atom` → `atom_bind`, missing or non-dict `bind` (renders `ft()`) | `bind` removed; `bind: "x"`; `bind: {}` (control: `bind` unchanged) | refused (each) |
| `_guarded_atom`, `binds` not a dict (`:170-171`) | — | **dead code**: `atom_bind` always returns a dict (`atoms.py:30-43`); no case `(r2-C)` |
| `_derivation_cnl`, non-dict `aggregate` (`:195`) | `aggregate: "sum"` on a rule that has a valid aggregate (control: unchanged) | refused |
| `_derivation_cnl`, `analysis is None or issue` (`:197-212`) | — | refused by `semantic:aggregate-shape`, `-function`, `-of-unbound` (`_validation.py:3863-3889`); 41 corpus aggregate clauses, 0 unanalyzable |
| `_guarded_term`, dict or list term (`:163`) | `where: [{left: {"x": 1}, …}]`; `[1]` (control: `where: [{left: "$u", operator: "!=", right: "$b"}]`, which loads) | refused; refused |
| `_derivation_cnl`, non-dict `where` item (`:185-189`; raises `AttributeError`) | `where: ["x"]` (same control) | refused |
| `_guarded_term`, `date_add` unpack (`:158`) | three `args`, on `tests/fixtures/pyrel-rules-calendar/clinic.orm.json` (model version 3; bookrec is version 2 and refuses all temporal syntax), against the same rule with two `args` as control | refused |
| `_derivation_cnl`, non-dict or missing `head` (`:191-193`) | `head: "x"`; `head` removed (renders `derive ()`) | refused; refused |

Each T4b case asserts that the refusal's path names the mutated element, so a
refusal for an unrelated reason fails the case.

Only `prose-rule` is reachable through a validated model. A loaded `Model`
holds mutable dicts, so an in-memory model can be changed after validation:
`verbalize_rules` re-validates it (rule 1), and `render_rule_verbalizations`
raises `VerbalizationError` through the collector (rule 4) when called
directly on such a model. `render_model_verbalization` keeps its behavior on
invalid in-memory models (out of scope). Root keys copied into
clauses are reported at `/derivation_rule/<key>`; with only `prose-rule`
reachable, the path is always `/derivation_rule`.

**Root `aggregate` with `clauses` (D6, pinned).** Valid (a model built from
`tests/fixtures/pyrel-rules-derivations/orders.orm.json` by splitting one
aggregate rule's body into two clauses loads), absent from the corpus. The
evaluator walks `iter_derivation_clauses`, which copies the root aggregate
into each clause (`extensions.py:1651`), so aggregation is per clause. The
rendering repeats the aggregate in each disjunct, which says the same thing.
Expected: `rendered`, text unchanged from today. T13.

### `src/gnd/api.py` (about +40 lines)

```python
def verbalize_rules(
    model: str | os.PathLike[str] | Model,
    *,
    fact_types: Sequence[str] | None = None,
) -> dict[str, Any]: ...
```

Payload, schema `gnd-rule-verbalization/1` `(r1-K)`:

```json
{
  "schema": "gnd-rule-verbalization/1",
  "exit_code": 0,
  "model_id": "bookrec",
  "rules": [
    {"fact_type": "book_is_blocked_for", "status": "rendered",
     "text": "when ... , derive (...)"},
    {"fact_type": "ft_legacy", "status": "unsupported", "reason": "prose-rule",
     "path": "/derivation_rule"}
  ]
}
```

A refusal is `{"schema": ..., "exit_code": 3, "error": {"kind": "input",
"message": ...}}`, the shape `_run_verbalize` returns (`api.py:817-818`),
written as a module-level helper rather than reusing that closure. `exit_code`
stays 0 when some rules are unsupported (D2). `fact_types=None` selects every
derived fact type; a given list keeps the stable id order, ignores
duplicates, and `[]` returns an empty `rules` list. `__all__` appends
`"verbalize_rules"` (MG1's name precedes CT2's `"compose"` `(r1-N)`).

### `src/gnd/rule-verbalization.schema.json` (new, about 50 lines)

Closed schema for the payload. The `reason` enum is `["prose-rule"]`, and a
test asserts it equals the dataclass literal.

### `src/gnd/disclosure.py` (1 line)

`api:verbalize_rules` joins the `value-free` rows (D3).

### Docs

`docs/reference/rule-verbalization.md` (new) and a row in
`docs/reference/python-api.md`, whose count line (`:9`, "nine functions")
becomes ten `(r1-N)`. A new Unreleased entry in `docs/release-notes.md`; the
earlier entry at `:56` is not edited. Full sweep in MG6.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Return type | (a) a payload dict with `exit_code`, the convention of `validate`, `check` and `verbalize`; (b) a bare `str`: cannot carry per-rule status | **Ruled `(s1)`: (a)** |
| D2 | Exit when some rules are unsupported | (a) 0, reported per rule; (b) 3 for the call: one prose rule would hide all others | **Ruled `(s1)`: (a)** |
| D3 | Disclosure row | (a) `value-free`: model content; (b) `site`: customer mode would withhold rule constants the caller already holds | **Ruled `(s1)`: (a)** |
| D4 | CLI surface | (a) API only, as asked; (b) `gnd verbalize --rules`: a CLI leaf, RF1 pins, a disclosure row, no requested use | **Ruled `(s1)`: (a)** |
| D5 | Selector name | (a) `fact_types=`: rules are keyed by the derived fact type; (b) `rule_ids=`: GND has no separate rule id | **Ruled `(s1)`: (a)** |
| D6 | Root `aggregate` with `clauses` | Settled by reading the evaluator (above): per-clause aggregation, text unchanged | pinned, T13 |
| D7 | Theme B | Ruled `(p1)`: fix in MG1 | fixed |

## Tests

New file `tests/test_rule_verbalization.py` unless noted.

| # | Case | Expected |
|---|---|---|
| T1 | `bookrec/complete.orm.yaml` as a loaded `Model` | `exit_code` 0; one entry per derived fact type, stable id order |
| T1b | The same model and `tests/fixtures/v62-phase4/models/aggregates.orm.yaml` by path, through both `render_model_verbalization` and `verbalize_rules` | no exception; output equal to the loaded-`Model` call |
| T2 | Corpus `(r1-M)`: every `*.orm.yaml` and `*.orm.json` under `src/gnd/examples` and `tests` that `load_model` accepts | floors asserted: ≥ 118 models with rules, ≥ 301 rules, ≥ 19 prose; clause floors body ≥ 408, negate ≥ 117, where ≥ 81, aggregate ≥ 41, rules with `clauses` ≥ 97; each construct's marker (`no `, comparison operator, `aggregate `, `; or `) appears in some text |
| T3 | Same corpus `(r1-A)` | for each rendered rule, its fact-type line (assembled at `model_verbalization.py:569-574`) contains `"This fact type is derived: " + text` followed immediately by one of ` Admission depends on `, ` Values of every role are redacted`, ` reading=` |
| T3b | Mutation control | T3's predicate rejects `text[:-1]` for every rendered rule |
| T3c | A rule with a **variable** named `$u` + U+0007 (constants are JSON-escaped by `_canonical`, so they cannot exercise `line_text`) `(r2-C)` | `text` contains `\x07` and not the raw character; T3 passes |
| T3d | A derived fact type with `depends_on`, and one with `redact: true` (both validate) | T3 passes through ` Admission depends on ` and ` Values of every role are redacted` respectively |
| T4 | A fixture with a prose rule | `unsupported`, `prose-rule`, `/derivation_rule`, no `text` |
| T4b | Each mutation in the fallback table | `load_model` raises `ModelValidationError` whose path names the mutated element; its control loads |
| T4c | Each T4b mutation applied in place to a loaded `Model` | `verbalize_rules` returns `exit_code` 3 with no `rules`; `render_rule_verbalizations` raises `VerbalizationError`; no partial text in either |
| T5 | `fact_types=["no_such"]` (3); a non-derived id (3); `fact_types="ft_x"` (`TypeError`); `[1]` (`TypeError`); missing path (3); existing invalid model (3); an in-memory `Model` mutated after loading (3); `TypeError` argument plus missing path (`TypeError`, order); subset `[b, a]` (both, stable order); `[a, a]` (one entry); `[]` (empty `rules`) | as stated |
| T6 | `__all__` pins: `tests/test_public_api.py:16`, `tests/test_v61_phase2_api.py:38-39`, `tests/test_public_runtime.py:52`, `tests/test_why_not_near_misses_public.py:225` (asserts `DisclosureRefused` last; becomes membership plus the new tail), and `tools/run_public_acceptance.py:373` (stale at `1446f90`, missing `DisclosureRefused`; brought current and recorded) `(r2-H)` | updated to append `verbalize_rules` (appended in merge order relative to the successor's `compose`) |
| T6b | `src/gnd/rule-verbalization.schema.json` registered in `tests/support/runtime_schema_inventory.py` and `tests/test_public_built_inventory.py` | `tests/test_conformance_payload.py` exits 0 `(r2-H)` |
| T7 | Before/after `(r1-R)`: SHA-256 of `render_model_verbalization` for every T2 model **both loaded and by path** `(r2-C)`, and of `gnd evolve preview` output for every evolve fixture, recorded at `1446f90` and after, in `evidence/MG1/parity.json` | loaded: identical; by path: identical for every model that rendered at `1446f90`, and equal to the loaded render for the 23 that crashed (listed) |
| T8 | `tests/test_disclosure_mode.py` total-table check | exit 0 with the new row; fails without it |
| T9 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py` | exit 0, no new allow-list row |
| T10 | Anonymity scan over files added since `1446f90` | exit 0 |
| T11 | 2,000 generated derived fact types, run with `fact_types=None` and with all 2,000 ids reversed and duplicated `(r2-C)` | fact-type visits ≤ 2,000 + number of ids given; one `ModelIndex` construction; same output both ways |
| T12 | Schema: payload validates; a reason outside the enum fails; enum equals the literal | as stated |
| T13 | The root-aggregate-with-clauses fixture of D6 | `rendered`; the aggregate clause appears in each disjunct |

### Verification selection `(r1-N)`

```
uv run pytest -q tests/test_rule_verbalization.py tests/test_public_api.py \
  tests/test_v61_phase2_api.py tests/test_public_runtime.py \
  tests/test_why_not_near_misses_public.py tests/test_disclosure_mode.py \
  tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py \
  tests/test_model_evolution.py tests/test_evolution_conformance.py \
  tests/test_evolve_loading.py tests/test_evolve_references.py \
  tests/test_public_evolution_drift_readers.py tests/test_public_evolution_legacy_readers.py \
  tests/test_public_evolution_version_graph.py tests/test_public_legacy_evolution.py \
  tests/test_conformance_payload.py tests/test_public_built_inventory.py
```

plus the recovery-verify tests, listed by name at implementation before the
first run, and T7's recorded table.

## Out of scope for this phase

- Rendering rules from a population or a witness; any change to rule
  semantics or wording.
- A CLI command (D4).
- Object-type `derivation_rule` (refused by validation, D-P1.1).

## Size

About 100 source lines, 450 test lines, one schema, one reference page.

## Approval instrument

This prose. No fixture corpus is authored first.

## Implementation findings

Recorded as found, 2026-11-03. The approved text above is not edited.

- **F1, refutes the fallback table's `date_add` row.** Validation refuses any
  temporal term in a derivation rule, not only a malformed one: a well-formed
  two-argument `date_add` in a `where` operand is refused with "temporal terms
  are supported only in guarded comparison operands". No valid two-argument
  control exists. T4b uses the well-formed form against the unmutated rule
  (`$r > $last`) as control. A well-formed `date_add` placed in a loaded
  `Model` renders completely ("(30 calendar days after $last)"), so it is
  not a partial rendering: `verbalize_rules` refuses it through
  re-validation (exit 3), and `render_rule_verbalizations` renders it. T4c
  uses the malformed three-argument form, which the collector refuses, and a
  separate case pins the well-formed behavior.
- **F2, refutes the spec's evolve-preview parity row (T7).** T7 asks for
  digests of `gnd evolve preview` output for every evolve fixture. Evolve
  calls `render_model_verbalization` with loaded models only
  (`evolve/service.py:1323-1324,1634-1639,1751,1938-1943`), and the loaded
  render is byte-identical for all 282 corpus models
  (`evidence/MG1/parity-after.json` against `parity-before.json`). The
  evolve suites in the gate run unchanged. No separate evolve-preview digest
  table was captured.
- **F3.** The collector also covers a `where` that is not a list, a `head`
  that is missing, empty or not a mapping, `fn` terms whose `args` is not a
  list, and an empty `bind`. Each such guard returns early only when a
  collector is passed. With the default `None` the existing expressions run
  unchanged, so an invalid in-memory model still behaves in
  `render_model_verbalization` as before (out of scope).
- **F4.** The disclosure page's surface table is generated
  (`tests/test_disclosure_docs.py`). Adding the row re-pastes one table line.
- **F5.** `tools/run_public_acceptance.py:373` lacked `DisclosureRefused` at
  `1446f90`, as round 2 reported. It now lists both names.
- **F6, refutes T9's "no new allow-list row" in part.** The RF6 model-query
  allow-list and its attribute-get metric are unchanged (both RF6 metric
  tests pass with no edit). `tests/test_rf6_query_policy.py` also keeps a
  syntax census of every dynamic subscript and `.get` in `src`, annotations
  included. MG1 adds 13 occurrences there: 12 annotations and the lookup
  `derived[identifier]`. Following the repository's pattern, they are
  registered as a counted successor,
  `evidence/MG1/dynamic-query-successor.json`, appended to
  `DYNAMIC_SUCCESSORS` in `tests/support/pyrel_application_successors.py`
  (6,902 distinct rows, 8,626 occurrences).
- **F7.** The first gate run reported exit 0 through a `tail` pipe while
  pytest reported 2 failures (the F6 census). The recorded gate exit is taken
  from pytest itself.
- **F8, review dispositions** ([phase-MG1-claude-review.md](phase-MG1-claude-review.md)).
  Each finding was reproduced before it was believed.
  - R-F1 (hardening; refutes rule 4's "the collector refuses every partial
    rendering"): reproduced. An atom without `fact_type`, mutated into a
    loaded `Model`, rendered `when None(book = $b) …` as `rendered`. **Fixed:**
    `render_rule_verbalizations` re-validates a `Model` argument with
    `validate_model_object` and raises `VerbalizationError`; the collector
    stays as a second guard. Regression `test_review_f1_…` (6 cases) failed
    before the fix (6 failed) and passes after. The well-formed `date_add`
    case now pins that re-validation refuses it and that the collector alone
    renders it without flagging (F1 above is narrowed accordingly).
  - R-F2 (completeness): reproduced; mutant H survived. **Fixed:**
    `test_review_f2_…` calls the collector directly for every in-memory
    mutation plus an unanalyzable aggregate; with mutant H applied it fails
    (1 failed), restored it passes.
  - R-F3 (completeness): **fixed** by asserting `model_id` and the id in both
    refusal messages.
  - R-F4 (completeness): **recorded.** Validation reports only the whole-rule
    path (`$.fact_types[i].derivation_rule`) for 9 of 11 mutations, so T4b
    asserts that path; the control/mutant pairing isolates the cause.
  - R-F5 (completeness): **fixed** with `test_review_f5_…`, which counts walks
    over `iter_fact_types_shared` (exactly 1) beside T11's render count.
  - R-F6 (hardening): **fixed.** `verbalize_rules` maps only load-time
    exceptions (`ModelValidationError`, `ModelLoadError`, `OSError`) and
    `VerbalizationError` to exit 3; any other exception propagates.
    `test_review_f6_…` failed before the fix and passes after.
