# GC1 · Set membership in comparisons · draft r3

**Status — awaiting owner review, 2026-11-15.** Implementable once the plan
gate and this spec's owner gate are recorded. No code is written before then.

## 2. Provenance

[Plan r3](guarded-rule-clauses-plan.md) §§0–6 and 8–10, issue
[#195](https://github.com/vasiloglou/gnd-public/issues/195) Summary item 3 and
Acceptance bullets 1 and 4. Baseline `ecd12986`. The linked plan has a Standard panel review disposition. This spec has its
own delegated approval gate.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| #195 Summary 3 | `in` / `not in` in `term_comparison` and `guarded_comparison`, right side a list of literals | M1–M3, T1–T3 |
| #195 Acceptance 1 | Validates against `orm-meta.schema.json`; same semantics as the helper encoding by differential test over generated populations; one-sentence verbalization | M1, M5, T1, T5, T6 |
| #195 Acceptance 4 | `--guarded-cases` produces a failing and a passing case | M6, T7 |
| Plan §6 operator leakage | Value comparison and dynamic rules still refuse membership | M1, T1 |
| Plan §0 rule 5 | Fix the stale guarded row in `constraint-reference.md` | M7 |
| Plan D1, D2 | Derivation `where` gains membership; spelling `"not in"` | M1, M3, T4 |

## 4. Standing rules bound to GC1

1. **Totality.** `_family_adapt_guarded`, the derivation `where` adapter and
   `_guarded_term` accept arbitrary JSON for `right`: object, nested list,
   empty list, 1,025 items, `NaN`, a variable string inside the list. Each
   yields a validation finding or `_ShapeError`, never a traceback (T2).
2. **Cap the algorithm.** The list is converted once per rule into a frozen
   set of typed keys at adapt time; evaluation is one lookup per binding. T8
   checks 10,000 bindings against a 1,024-item list under a bounded time and
   charges one work unit per lookup.
3. **Validation order.** The new `semantic:membership-list` rule runs inside
   the guarded block after `semantic:guarded-term-ref` and before
   `semantic:guarded-comparison-type`, and in the derivation where analysis
   before `semantic:term-comparison-type`; pinned by source-order assertion
   (T2).
4. **One walk.** `_iter_guarded_consequent_terms` yields each list member as a
   literal term, so the literal-domain lint and binding-type checks cover them
   without a copy (T3). Resolve each member against the left variable's role
   and declared value domain. Pin the member's warning path.
5. **One home.** `representation-format.md` "Guarded constraints" and the
   derivation `where` subsection own the operator; `constraint-reference.md`
   and `verbalization-patterns.md` cite it.
6. **Measure.** T6 compares covered, decidable cases and their projected
   offending bindings. T5 pins typed identity, runtime kind mismatch, and
   unavailable operands directly in each applicable evaluator.

## 5. Goal

A model whose guarded or derivation comparison uses `in` / `not in` with a
non-empty literal list in one membership domain passes `gnd validate` (exit 0); the same
operator in a value comparison or dynamic rule is refused (exit 3). `gnd check`
returns the same verdicts and projected offending bindings as the helper
encoding over generated covered, decidable populations. Pin unchecked and
validation refusal separately, preserving existing models and comparison
operators.

## 6. Design

| Capability | Searches | Decision |
|---|---|---|
| Membership evaluation | `components_index.py search guarded comparison`, `search term comparison membership` | Use a tagged membership identity shared across comparison adapters. Preserve legacy scalar comparison behavior. |
| Schema | `git grep comparison_operator` | Adapt; new defs, shared enum untouched |
| Synth pairs | `search guarded cases` | Adapt `synth/guarded_cases.py` |

**M1 · Schema (canonical, then vendored copy).** New defs:

```json
"membership_operator": {"enum": ["in", "not in"]},
"literal_list": {
  "type": "array", "minItems": 1, "maxItems": 1024,
  "items": {"oneOf": [{"$ref": "#/$defs/scalar"},
                      {"$ref": "#/$defs/date_literal"},
                      {"$ref": "#/$defs/duration_literal"}]}
},
"membership_comparison": {
  "type": "object", "required": ["operator", "left", "right"],
  "additionalProperties": false,
  "properties": {"operator": {"$ref": "#/$defs/membership_operator"},
                 "left": {"$ref": "#/$defs/term"},
                 "right": {"$ref": "#/$defs/literal_list"}}
}
```

`guarded_comparison` and `term_comparison` become
`{"oneOf": [<current object>, {"$ref": "#/$defs/membership_comparison"}]}`.
The `scalar` def (checked at `ecd12986`) also admits a `$name` variable
string, so the schema alone cannot refuse a variable member; M2 does.
`comparison_operator` is unchanged.

**M2 · Validation (`model/_validation.py`, ~60–90 lines).** New rule
`semantic:membership-list`: list members are literals of one membership domain
(no variables, no function terms), compatible with the left term's primitive
under `_guarded_primitives_compatible`; duplicates (by typed identity) are a
warning, not an error. Extend `_iter_guarded_consequent_terms` and the
`exists.where` walk to yield list members.

**M3 · Adapter and IR (`semantic_adapter.py`, `semantic_ir.py`, ~50–80
lines).** Accept `in` / `not in` beside `(*_ORDERING, "=", "!=")` at both
guarded sites and the derivation `where` adapter. Represent the right side as
a new `IROperand` kind `literal_set` holding a `frozenset` of canonical typed
keys plus the ordered original literals for messages.

**M4 · Evaluation (`terms.py`, `checker/_core.py`, `semantic_spec.py`,
`correspondence.py`, `extensions.py`, ~60–100 lines).** `compare_terms` gains
the two operators for term filters. The guarded reference and indexed
paths and the temporal guarded evaluator also follow the shared membership key contract. Tag Boolean,
numeric, raw text, calendar date and day-count duration keys. The literal
format admits only integral `duration_days`; compare exact day counts. Numeric
renderings share exact value identity. Use typed runtime context for temporal
terms and retain unknown for unavailable or incompatible values. Legacy
equality paths retain their behavior. T5 demonstrates both comparable
singleton parity and the Boolean/number, date/string, number/string and
duration/number cases. Static mismatches are refused and dynamic mismatches
are unchecked. Preserve existing invalid-model refusal IDs and paths;
schema branch explanations may include the new membership arm.

**M5 · Messages and verbalization (`verbalize.py`, `model_verbalization.py`,
~20–40 lines).** Words: `in` → "is one of", `not in` → "is none of", list
rendered as `"A", "S"` in declared order. Example: "If a question mentions
'active customers', some filter on Customer status uses a literal that is one
of 'A', 'S'."

**M6 · Synth (`synth/guarded_cases.py`, ~30–50 lines).** For a membership
comparison, the paired search uses legal values both inside and outside the set. Cover
direct comparisons and the issue's `exists.where` shape. A proven exhaustive
domain with one reachable verdict returns the existing `no-failing-case`
or `no-passing-case` reason. T7 demonstrates both with the Boolean domain
`[true, false]`. The existing
bounded search outcome remains available when the search cannot prove
exhaustion. Manifest stays `gnd-guarded-cases/1`.

**M7 · Docs.** Syntax and semantics in `representation-format.md`; operator
rows in `constraint-reference.md` (and correct its guarded row to list
`exists`), and the verbalization pattern.

**M8 · Export boundary.** Ship named refusals wherever a selected exporter
would otherwise interpret an unsupported GC1 operator, including membership
in derivation filters. Cover PyRel rules/runtime, Lean, Ossie and any
affected Soufflé dispatch.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Derivation `where` gains membership (plan D1) | Excluding it needs a second, guarded-only comparison def, two homes for one operator | Include |
| D2 | `"not in"` spelling (plan D2) | A one-token alias (`nin`, `not_in`) is easier to type; the issue writes `not in` | `"not in"` only |
| D3 | List cap | 1,024 covers glossary code lists; a larger cap only raises adapt-time cost | 1,024 |
| D4 | Mixed `Integer`/`Float` members | Numeric members compare by exact value today under `=`; refusing them breaks `in [1, 1.5]` | Allow numeric mixing, refuse other mixes |
| D5 | Duplicate members | Error would refuse harmless glossary copies | Warning `semantic:membership-duplicate` |

## 8. Tests

| ID | File and case | Expected |
|---|---|---|
| T1 | `tests/test_guarded_membership.py` (new): valid `in`/`not in` in guarded comparison, `exists.where`, derivation `where` (every schema site inventoried in plan §2); the same operator in `value_comparison` and `dynamic_rule` | validate exit 0 for the first three, exit 3 with the schema finding for the last two |
| T2 | Same file: empty list, 1,025 items, nested list, object, variable member, function-term member, `NaN`, mixed string/number; source-order assertion for the new rule | exit 3 with `semantic:membership-list` or the schema finding; no traceback |
| T3 | Same file: list member outside a declared value domain | `semantic:guarded-literal-outside-domain` warning at the member's path |
| T4 | Same file plus `tests/test_derivation_rule.py`: derivation `where: [{operator: in}]` | derived extension equals the union-of-clauses encoding |
| T5 | Same file: `1` vs `1.0` vs `true`, Date, duration and temporal function membership, the cross-kind cases above and unknown left, through reference, indexed and temporal routes as applicable | matching comparable singleton values agree with the equivalent typed equality. Cross-kind runtime comparisons are unchecked, static mismatches are refused, and legacy equality remains stable |
| T6 | Same file, differential: for the issue's `active_means_a_or_s` rule and two `not in` rules, generate ≥200 covered, decidable populations with a fixed seed. Compare with a same-domain semiderived unary membership witness and a guarded `atom` consequent for `in` or `absence` for `not in`. Assert both pass and fail and the plan §0 coverage preconditions | identical verdicts and canonically projected offending binding sets on every generated population |
| T7 | `tests/test_synth_guarded_cases.py`: `--guarded-cases` over models with `in` and `not in` | reachable direct and existential rules yield both cases. An exhausted finite domain yields a named refusal. The v1 manifest validates |
| T8 | `tests/test_guarded_membership.py`: 10,000 bindings × 1,024 members | include one-time list compilation and 10,000 lookups within a 5-second reference-worktree bound; charge compilation and each lookup |
| T9 | `tests/test_rule_verbalization.py` / model verbalization test | one sentence per rule, words as in M5 |
| T10 | Targeted exporter suite and the membership test module | unsupported guarded, existential, and derivation memberships are refused explicitly without a traceback. Existing forms retain their output |

Proposed focused gate:

```sh
uv run pytest -q tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_guarded_consequent_matrix.py tests/test_public_semantic_guarded.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short
```

plus the complete [issue #171 guard list](https://github.com/vasiloglou/gnd-public/issues/171), the targeted exporter checks in `tests/test_pyrel_rules.py`,
`tests/test_pyrel_rules_derivations.py`, `tests/test_public_pyrel_export_runtime_support.py`,
`tests/test_public_lean_export_successors.py`, `tests/test_ossie_export.py`,
and `tests/test_public_souffle_successors.py`, `uv run ruff check`, the layer check and
`python3 scripts/components_index.py changed --base main --strict`.

## 9. Out of scope for GC1

Antecedent `negate`/`where` (GC2), `any_of` (GC3), exporter translations (GC4),
membership against a fact type.

## 10. Size

Estimate 220–360 runtime lines, 60–90 schema/docs lines, 250–400 test lines.

## 11. Approval instrument

Use a corpus-first gate for public validation and findings. Before runtime
implementation, record the delegated ruling over this spec and the initial red
fixture expectations, including each comparison site, unsupported export and
the finite-domain synthesis outcome.
