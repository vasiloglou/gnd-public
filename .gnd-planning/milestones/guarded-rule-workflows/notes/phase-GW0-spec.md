# GW0 · Guarded rule diagnostics · draft r1

**Awaiting owner review.** Implementation requires the plan and GW0 spec gates.

## 2. Provenance

[Plan r3](guarded-rule-workflows-plan.md) §§0–6 and 8–10,
[GR-D12](https://github.com/vasiloglou/gnd-public/issues/183),
the [correction to GR-D8](https://github.com/vasiloglou/gnd-public/issues/179#issuecomment-6805758864),
and the [RC4 vacuity spec](../../rule-check-adoption/notes/phase-RC4-spec.md).
Baseline `793618f1`. Independent review has yet to run on these bytes.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| #183, Asked for, first bullet | Count the antecedent bindings for each guarded verdict | E1, M1–M2, T1/T3 |
| #183, Asked for, second bullet | Identify the first atom where populated relations yield no binding | E2, M1–M2, T2/T3 |
| #183, Asked for, third bullet | Validate declared role and type domains at literal binding sites, including the consequent typo | E3, M3, T4–T6 |
| RC3 and RC4, plan §4 E4 | Preserve existing report variants, refusal precedence and vacuity behavior | M1–M2/M4, T3/T7 |
| Plan §§0, 5–6 and 8 | Bound work and reads, run focused gates and independent review, update schema/docs/index | §§4, 6, 8 and 11 |

## 4. Standing rules bound to GW0

1. **Totality belongs to the function, not the caller.** Keep model and
   population reads in their capped loaders. The new validation rule must
   tolerate arbitrary JSON shapes under `semantic_validate`, including
   malformed atom and value-constraint structures (T6).
2. **An input cap bounds the document, not the algorithm.** Track the first
   empty prefix inside the existing join with constant additional state.
   Retain the existing reference-route work limit and verify overhead on
   the plain route, which has no reference-join limit. Index declared
   value domains once per model and memoize per typed literal and effective
   domain. Test high fanout and hostile many-literal validation (T8).
3. **Validation order is part of the design.** Pin CLI conflicts before I/O
   and existing checker precedence before diagnostic projection. Invalid
   references keep the existing structural findings. Domain validation
   follows its prerequisite rules and skips unresolved domains (T3/T6/T7).
4. **A policy governing N element kinds is enforced by one walk over all N.**
   Use `_iter_guarded_atoms` for all four binding sites (T4/T5).
5. **Normative prose has exactly one home.** The rule-check report reference
   owns the diagnostic wire. The ORM constraint reference owns the static
   domain rule. CLI and skill surfaces link to them (T7).
6. **Resolve contested representation questions by measurement.** Pin
   distinct versus duplicated join witnesses and a second atom that has
   eligible rows on its own but eliminates the prefix (T1/T2).

## 5. Goal

The opt-in check emits a numeric count for a completed antecedent evaluation
and explicit unknown metadata for an unavailable one. In the populated
no-match reproduction, check exits 0 under the proposed compatibility policy
and emits count zero with the first empty-prefix index. Validate exits 0 with
a located warning for either misspelt atom literal on an otherwise valid model.
Existing check failures and indeterminate cases retain their exit bands.

## 6. Design

| Capability | Searches and inspected evidence | Reuse |
|---|---|---|
| Guarded prefix and binding count | `components_index.py search guarded antecedent bindings`, `components_index.py search snapshot decision witness`; inspected the indexed join and scope selection | Adapt `check.snapshot_decision`; reuse existing typed identity, join and work counters |
| Guarded verdict projection | Same searches, then inspected `checker/_core.py`, `checker/_reports.py` and `payloads.py` | Adapt `checker.evaluate` and `checker.reports`; reuse `check.service` |
| Literal validation | `components_index.py search model validate constraint`, `components_index.py search value domain type role`; inspected `model/_validation.py`, the constraint reference and `semantic_spec.value_cell_state` | Adapt `model.validation`; reuse `model.query_index` and the existing scalar/domain semantics |

**M1 · Antecedent evaluation (about 45–75 source lines).** Extend the private
`_indexed_guarded_bindings(constraint: IRConstraint, snapshot: SnapshotIR, work: ReferenceJoinWork | None = None)`
result with the optional first empty-prefix index. Record it in declared
antecedent order when the running join first becomes empty. Preserve later
checks for an invalid atom or unavailable relation. Publish it only when all
antecedent relations are covered, available and populated. Use the size of
the canonical distinct binding set already returned by the join. An
available covered empty relation yields count zero with a null index.
Unknown evaluation or omitted coverage yields null for both. A complete
antecedent join can retain a known count when its consequent is undecided.
Scope selection, unknown precedence, witness selection and exit behavior
continue through the existing decision path. Carry the count and index
through `CorrespondedFinding` and `ProjectedFinding` as optional integers,
including any cached or detached projection used by the selected surface.
The formatter must never be the source of diagnostic metadata.

**M2 · Rule-check report (about 65–100 source lines and schema).** Propose
`gnd check MODEL POPULATION --guarded-diagnostics --format json`. It implies
`--rule-ids` and uses the same supported plain snapshot scope and usage
checks. Keep `--baseline` and `--allow-vacuous` behavior when combined.
Propose wire version 16, derived from the version-15 shape. Require one
`guarded_antecedent` object on every guarded verdict in that version. The
object has exactly `binding_count` and `first_empty_atom_index`, each a
nonnegative integer or null. The index is zero based and may be non-null
only if the count is zero. Example:

```json
{"guarded_antecedent":{"binding_count":0,"first_empty_atom_index":1}}
```

Other verdict families omit the object. Route only the selected report
through the new schema branch, and show the same count and index (or
unavailable state) in text. Carry the fields from the authoritative result
without an additional join. Preserve redaction and existing unsupported
route refusals. Validate both new schema output and historical report input.

**M3 · Model validation (about 80–130 source lines).** Add
`_rule_guarded_literal_domain(doc: dict[str, Any]) -> list[ValidationIssue]`
in `src/gnd/model/_validation.py` and register it once after the current
semantic rules. Use `_iter_guarded_constraints`, `_iter_guarded_atoms` and
the existing atom bind decoder. Resolve the named fact role through
ModelIndex. Index declared `value` constraints by exact role and relevant
object type using the same scope semantics as value evaluation, including a
reference value type when applicable. A role-scoped constraint on a
different role supplies no evidence. Respect typed enumeration identity
and range bounds, including disjoint and open-ended ranges. Issue one
`semantic:guarded-literal-outside-domain` warning at each definitively excluded
binding path, citing the restricting constraint references. Each applicable
domain is tested independently, and any definitive exclusion suffices.
Variables, unresolved roles and malformed or undecidable domains do not
produce an exclusion for that domain. Cover both modalities as diagnostics.
Use current scalar and range helpers without a reverse layer import. If
needed, move only shared scalar predicates to their allowed lower-level home
and keep the existing identity aliases. Set an explicit bounded-work
policy for many distinct literal/domain pairs in the gated spec, including
observable behavior if the limit is reached.

**M4 · Docs and compatibility.** Put the wire and supported routes in
`docs/reference/rule-check-report.md` and the static domain semantics in the
ORM constraint reference. Update CLI help and affected component entries.
Existing no-flag JSON and text retain their shape and bands, apart from the
intentional model warning on affected literals.

## 7. Decisions

| ID | Proposed ruling | Consequence |
|---|---|---|
| D1 | Keep zero-bindings over populated sources as `pass` and add structured diagnostic evidence | Check retains band 0 for that rule. Changing it to `vacuous` would change the default band and the effect of `--allow-vacuous`. |
| D2 | Use a new opt-in report version on the current plain rule-check scope | Consumers can adopt the field without sending expanded rows to existing strict version-15 readers. Extending other check routes requires their own evidence and wire contracts. |
| D3 | Warn for definitive declared-domain exclusion on either modality | Existing models remain loadable and the author sees the exact bad site. Treating it as an error would make existing models fail admission with exit 3. |
| D4 | Select a validation work limit and observable exhaustion rule | The budget must bound domain membership and range work without silently treating a skipped check as a clean result. Set the number and expected output before implementation. |

## 8. Tests

| ID | Case | Expected result |
|---|---|---|
| T1 | `tests/test_guarded_diagnostics.py` (new), active atom/absence/exists/comparison outcomes, with duplicate paths to one distinct binding and distinct bindings sharing a value | Count matches the evaluated binding set for pass, fail and warning. Bands retain their existing meanings. |
| T2 | Same file, first atom misses on a literal, later atom has rows but empties the join, and multiple later prefixes stay empty | Count 0, first index 0 or the first later index, respectively, with exit 0 for an otherwise clean check. |
| T3 | Same file and `tests/test_rc4_allow_vacuous.py`, empty covered relation, omitted coverage, refused source and complete antecedent with undecided consequent, plus an injected work limit at the private evaluator seam | Covered-empty gives 0 with null index. Unavailable antecedent gives null/null. Consequent-only unknown can retain the known count. Existing vacuity and unchecked bands hold. |
| T4 | `tests/test_model_guarded.py`, both issue typos plus an existential atom and a known good control | Validate exits 0 with one located warning per excluded literal and zero for the good control. |
| T5 | Same file, role-local scope, reference-type and object-type scope, deontic and alethic domains, ranges and boolean versus number | Exact exclusions only, with valid and unrelated role controls silent. |
| T6 | Same file, malformed input, undeclared role, variable, non-scalar value and undecidable domain | Existing invalid inputs keep their refusal. No spurious exclusion or internal validator error. |
| T7 | New diagnostics file plus RC1/RC3/RC4 controls, report schema, rule ID, plain and baseline JSON/text, invalid CLI combinations and unsupported routes | New output validates, old report controls retain their shape and band, CLI misuse exits 64 and unsupported models retain exit 3. |
| T8 | New diagnostics file and model guarded tests, synthetic join and validation stress, with instrumented work counts and a bounded timeout set in the gated spec | No new report join. Exhaustion is visible and work is bounded at the selected ceiling. |

Proposed focused gate under the default lane:

```sh
uv run pytest -q tests/test_guarded_diagnostics.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_public_semantic_guarded_join.py tests/test_public_guarded_consequent_matrix.py tests/test_rc1_rule_ids.py tests/test_rc3_baseline.py tests/test_rc4_allow_vacuous.py --tb=short
```

Run affected Ruff, layer and component-index checks. Record verbatim
results plus report, schema and fixture digests. GW2 owns the combined
installed-candidate smoke.

## 9. Out of scope for GW0

Edition comparison, generated examples, discovery, mined imports, and
changes to dev-tools. The draft diagnostic wire is for the plain rule-check
surface. The model validation finding applies through the shared validator.

## 10. Size

Estimate 190–305 runtime lines, 60–100 schema/docs lines and 220–350
test/fixture lines. Record actual size and any revised work budget in the
phase record.

## 11. Approval instrument

Owner decision on this spec and its four decision rows, including the
exact work-budget rule, after the reviewed plan gate. Phase execution then
requires the focused gates, independent diff and refactoring reviews,
and the phase record.
