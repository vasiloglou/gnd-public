# Guarded rule clauses · plan r1

**Status — draft r1, 2026-11-15. Not reviewed, not approved.** No plan review
has run over these bytes: the owner has not selected a review instrument for
this milestone. The project bar for plan review is the maintained GND review
panel. Default `auto=false`; every phase and spec waits for its owner gate.

## Goal and completion predicates

Let a guarded rule use the clause language derivation clauses already have, so
a business statement such as "unless", "one of these values" or "either form is
acceptable" is one rule, not a helper fact type plus a rule
([#195](https://github.com/vasiloglou/gnd-public/issues/195)).

- **GC1.** `{operator: in | not in, left: <term>, right: [<literal>, ...]}`
  validates in `guarded_comparison` and `term_comparison`, evaluates as set
  membership with typed identity, and verbalizes as one sentence.
- **GC2.** A guarded rule may carry `negate` (atoms that must be absent) and
  `where` (term comparisons) beside `antecedent`, with derivation-clause
  semantics, safety and the stratification argument recorded.
- **GC3.** A consequent `any_of: [<consequent>, ...]` over today's four forms
  holds when at least one alternative holds, and a violation lists each
  alternative's unmet atoms.
- **Every form** passes a differential test against its equivalent
  derivation-helper encoding over generated populations, and
  `gnd synth --guarded-cases` produces a failing and a passing case for it.
- **GC4.** Exporters translate or refuse each new form with a named reason,
  normative docs and the bookrec guarded-rules chapter teach the three forms,
  and an installed-candidate smoke runs the issue's three retail examples.
- Closure maps every issue acceptance bullet to a recorded criterion.

## 0. Binding design rules

Apply the six design rules of the
[project hook](../../../../.codex/skills/process-phase/references/project.md)
by name in each spec. In particular:

1. **Totality.** New schema arms and adapter code are total over arbitrary
   JSON: a non-list `right` for `in`, an empty list, nested `any_of`, a
   `negate` that is not a list. Hostile-input tests per phase.
2. **Cap the algorithm.** Membership is a set lookup, not a scan per binding;
   negation is one anti-join per negated atom over an identity index; `any_of`
   evaluation is linear in alternatives times bindings. Each phase ships a
   time-bound test over the layer it adds and charges the existing work
   counters.
3. **Validation order.** New structural refusals slot into the existing
   guarded block (`model/_validation.py` registration order) at a stated
   position, pinned by source-order assertion.
4. **One walk.** `_iter_guarded_atoms` and `_iter_guarded_consequent_terms`
   learn the new sites (negated atoms, `where` terms, `any_of` alternatives)
   once, so every existing guarded check (term refs, role claims, literal
   domains, binding types, grounding) covers them without per-site copies.
5. **One home.** `representation-format.md` "Guarded constraints" owns the
   syntax and semantics; constraint-reference, verbalization-patterns, CLI and
   docs pages cite it. The stale guarded row in constraint-reference (no
   `exists`) is corrected in GC1.
6. **Measure.** The differential test against helper encodings decides any
   disputed semantics (unknown propagation, duplicate witnesses, negation over
   an uncovered relation).

Use ModelIndex and `constraint_families.FAMILIES` dispatch, keep branch
evidence identities, register new refusal and unchecked scopes in
`branches.py`, keep the layer allowance at zero, and run the issue-171 guard
list in every phase gate.

## 1. Scope, sources and authority

Baseline `ecd12986` (GND 0.3.1, tag-only). Framework development: an
experiment-claim census cannot measure runtime coverage of rule syntax.

| Source and location | Obligation or constraint | Phase and gate |
|---|---|---|
| #195 Summary item 3 | `in` / `not in` with a list-of-literals right side in `term_comparison` and `guarded_comparison` | GC1 I1–I4 |
| #195 Summary item 1 | `negate` and `where` beside `antecedent` with derivation-clause semantics | GC2 N1–N4 |
| #195 Summary item 2 | `any_of` consequent over the four existing forms | GC3 A1–A4 |
| #195 Acceptance bullet 1 | Schema validation, differential test against the helper encoding over generated populations, one-sentence verbalization | GC1–GC3, each criterion 1–3 |
| #195 Acceptance bullet 2 | `negate` follows derivation stratification | GC2 N2 |
| #195 Acceptance bullet 3 | `any_of` violations list each alternative's unmet atoms | GC3 A3 |
| #195 Acceptance bullet 4 | `gnd synth --guarded-cases` yields a failing and a passing case per new form | GC1 I4, GC2 N4, GC3 A4 |
| #195 "Why not a derived fact type" | Verbalization and `--rule-ids` feedback describe the business rule, not a helper | GC1–GC3 verbalization criteria, GC4 smoke |
| [Guarded-rule-workflows close](../../guarded-rule-workflows/006-milestone-close.md) | `--guarded-diagnostics` v16 count and first-empty-prefix semantics; literal-domain lint | GC2 N3, GC3 A3 |
| [Guarded-rule-authoring plan](../../guarded-rule-authoring/notes/guarded-rule-authoring-plan.md) | Existing guarded synth manifest `gnd-guarded-cases/1` and its refusal reasons | GC1–GC3 synth criteria |
| Project hook, CONTRIBUTING, AGENTS.md | Owner gates, focused gates plus guard list, Ruff, component index, topic PRs | All phases and close |

## 2. Contract proposal and product behavior

**GC1 · membership.** New schema def `membership_comparison`
`{operator: "in" | "not in", left: term, right: literal_list}`; `literal_list`
is a non-empty array (proposed cap 1,024) of scalar, date or duration literals
of one primitive kind. `guarded_comparison` and `term_comparison` become
`oneOf` the current shape and this one. The shared `comparison_operator` enum
is **not** extended, so value-comparison and dynamic rules are unchanged.
Semantics: `in` holds when the left value is typed-identical to some list
member; `not in` when it is identical to none; an unknown or non-comparable
left value gives the same unknown/`term:values-not-comparable` outcome as `=`.
Because `term_comparison` is shared, derivation `where` gains membership too
(decision D1).

**GC2 · antecedent `negate` and `where`.** A guarded rule may add
`negate: [atom, ...]` and `where: [term_comparison, ...]`. A binding of the
positive antecedent survives when every `where` holds and no negated atom
matches. Safety: every variable in a negated atom or `where` term is bound by a
positive antecedent atom (reuse the `derivation-negate-unbound` rule).
Stratification: a guarded rule produces no facts, so negating any fact type,
derived or asserted, reads a completed extension; the issue's condition holds
by construction and the spec records that argument plus a test that negates a
derived fact type. A negated atom over an uncovered or unavailable relation
makes the binding unknown, never a silent survivor. Disconnected negated atoms
are refused as positive ones are. `--guarded-diagnostics` counts bindings after
`negate`/`where`; the first-empty index still refers to positive atoms
(decision D3).

**GC3 · `any_of`.** `consequent: {any_of: [c1, c2, ...]}`, two or more
alternatives, each one of the four existing forms (no nesting). Per binding:
holds if any alternative holds; otherwise unknown if any is unknown; otherwise
violated. Each alternative is grounded independently against the antecedent
plus its own `exists` atoms. Violations carry, per alternative, its index and
its unmet atoms or failing comparison, on an opt-in report surface (decision
D4). Messages and verbalization read "at least one of: …".

## 3. Dependencies and artifact homes

GC1 first: it is self-contained and GC2's `where` and GC3's `exists.where`
reuse it. GC2 and GC3 are independent of each other and touch overlapping
files (`semantic_adapter.py`, `semantic_ir.py`, `correspondence.py`,
`checker/_core.py`, `model/_validation.py`), so they run in sequence, GC2 then
GC3. GC4 depends on all three.

| Capability | Existing home and decision |
|---|---|
| Schema | Adapt canonical `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`, copy to `src/gnd/schema/`, held by `tests/test_schema_sync.py` |
| Validation | Adapt the guarded block in `src/gnd/model/_validation.py`; reuse `_rule_derivation_negate_unbound` logic and the guarded atom/term walks |
| Structural shape and scope | Adapt `universe._family_implemented_guarded` and `_family_scope_guarded`; register scopes in `branches.py` |
| Adapter and IR | Adapt `semantic_adapter._family_adapt_guarded` and `IRConstraint` with `negate`, `where`, `alternatives` fields |
| Term comparison | Adapt `terms.compare_terms` (one home for membership), reused by `checker._compare`, `synth/guarded._where_holds` and `extensions` where filters |
| Evaluation | Adapt `semantic_spec.guarded_result` (reference) and `correspondence._indexed_guarded_*` (production); reuse `extensions._apply_negation` identity anti-join |
| Messages and verbalization | Adapt `verbalize.guarded_message`, `model_verbalization._guarded_cnl`; reuse `_derivation_cnl` negate/where wording |
| Synth | Adapt `synth/guarded_cases.build_pair` and `COMPARISON_PAIRS` |
| Exports | GC4: `export/pyrel_rules.py`, `pyrel_runtime.py`, `lean.py`, `ossie_formulas.py` |

Component consult (`dev/components/`, `scripts/components_index.py search
guarded comparison` and `search term comparison membership`) found
`semantics.snapshot_spec`, `semantics.temporal_guards`, `check.service` and the
`semantic_adapter` / `checker._core` term helpers, and no existing membership
or guarded-negation component, so every row above is adapt, not new. Index
review was not run for this plan; each phase spec repeats the consult and runs
`components_index.py changed --base main --strict` before its PR.

## 4. Phases, deliverables and named criteria

| Order | Phase | Acceptance criteria |
|---|---|---|
| 1 | **GC1 · membership** | I1 schema and validation accept `in`/`not in` in guarded and term comparisons and refuse empty, oversize, mixed-kind and non-literal lists; value-comparison and dynamic rules still refuse them. I2 reference and production evaluators agree; typed identity (bool vs number, date vs string) and unknown left values tested. I3 differential test: each `in` rule against its helper encoding (a value fact type plus a derivation union) over generated populations yields identical verdicts and offending bindings. I4 one-sentence verbalization and `--guarded-cases` failing/passing pair for `in` and `not in`. |
| 2 | **GC2 · antecedent negate/where** | N1 schema, safety and disconnection refusals; the walks cover negated atoms and `where` terms. N2 stratification argument recorded and tested with a negated derived fact type; uncovered negated relation yields unchecked, not pass. N3 production and reference evaluators agree, `--guarded-diagnostics` counts post-filter bindings, and the differential test against the `negate`/`where` helper encoding matches. N4 verbalization reads as one sentence ("…, unless …") and synth produces a failing and a passing case, including one that passes only because the negated atom is present. |
| 3 | **GC3 · any_of** | A1 schema and validation (≥2 alternatives, no nesting, per-alternative grounding). A2 three-valued evaluation agrees across evaluators; differential test against the union-helper encoding. A3 violation report lists each alternative's index and unmet atoms or failing comparison on the selected surface. A4 verbalization and a synth pair per alternative shape. |
| 4 | **GC4 · exports, docs, smoke** | E1 PyRel rules and runtime translate or refuse each form with a named `ProfileRefusal`; Lean and Ossie refuse with named reasons; existing exports byte-stable. E2 normative docs, bookrec chapter 8 and CLI reference updated, with the "Why not a derived fact type" helper patterns shown as the before. E3 installed-candidate smoke of the issue's three retail rules plus the `exists` control. |

## 5. Documentation, skill and compatibility surfaces

`representation-format.md` owns syntax and semantics; `constraint-reference.md`
(guarded row, operators), `verbalization-patterns.md`, `docs/reference/cli.md`,
`docs/bookrec/08-guarded-rules.md`, `docs/reference/rule-check-report.md` (if
GC3 changes the wire) and the packaged model-authoring skills cite it. Existing
models and reports keep their bytes: every change is additive, and a model not
using the new forms validates, checks and exports identically.

## 6. Risks and required controls

- **Operator leakage.** Extending the shared enum would make `in` legal in
  value-comparison and dynamic rules that cannot evaluate it. Control: a
  separate def and negative schema tests on those sites.
- **Silent negation over missing data.** An anti-join over an uncovered
  relation passes everything. Control: coverage required; tested unchecked.
- **Two evaluators drift.** The reference (`semantic_spec`) and production
  (`correspondence`) paths both change. Control: every evaluation test runs
  both, and the differential test compares against a third encoding.
- **Unknown propagation in `any_of`.** "Any unknown → unknown" versus "pass if
  one holds" matters for exit bands. Control: fixture with one true and one
  unknown alternative (expect pass) and one false plus one unknown (expect
  unchecked).
- **Synth search blow-up.** Alternatives and negations multiply search states.
  Control: existing `search-limit` reason and a time-bound test.

## 7. Out of scope

Nested `any_of`, `any_of` in the antecedent, aggregates in guarded rules,
membership against a fact type (only literal lists), extending `in` to value
comparisons or dynamic rules, Souffle export of guarded rules, why-not for
guarded rules, publication, certification and dev-tools changes.

## 8. Execution, approval and review protocol

`process-phase` per phase: spec and owner gate, implementation, focused
verification with the guard list and Ruff, independent diff and refactoring
review (one reviewer in a different tool), phase record, topic PR, separate
owner merge authorization. Plan review and milestone close use the maintained
GND review panel when the owner selects it. Close needs four phase records,
differential-test outputs, synth manifests, the smoke transcript and an
issue-to-criterion sweep.

## 9. Per-phase verification story

| Phase | Focused lane and affected consumers |
|---|---|
| GC1 | New `tests/test_guarded_membership.py` plus `test_model_guarded.py`, `test_public_guarded_consequent_matrix.py`, `test_derivation_rule.py`, `test_synth_guarded_cases.py`, `test_rule_verbalization.py`, `test_schema_sync.py`, guard list |
| GC2 | New `tests/test_guarded_antecedent_negate.py` plus guarded corpus, semantic join, diagnostics, baseline, derivation stratification consumers, guard list |
| GC3 | New `tests/test_guarded_any_of.py` plus consequent matrix, rule IDs, diagnostics, report schema, guard list |
| GC4 | `tests/test_pyrel_rules*.py`, Lean/Ossie export tests, docs link checks, installed-candidate smoke, guard list |

Exact commands are fixed in each phase spec. Historical evidence/census lanes
and certification are not selected.

## 10. Owner decisions and open questions

| ID | Question | Proposal | Status |
|---|---|---|---|
| D1 | Should derivation `where` also gain `in`/`not in`, since `term_comparison` is shared? | Yes: one definition, one evaluator, and the helper-encoding test benefits | Proposed |
| D2 | Spelling of the negative operator | `"not in"` as the issue writes it (with a space); no `nin` alias | Proposed |
| D3 | Diagnostics when `negate`/`where` empty the bindings | Count after filters; first-empty index stays positive-atom only; add no new field in GC2 | Proposed |
| D4 | Where `any_of` per-alternative violation detail lives | Additive object on guarded verdicts under `--guarded-diagnostics` (new report version 17), default report unchanged | Proposed |
| D5 | Exporter policy for new forms | PyRel translates `in`, `negate`, `where`; refuses `any_of` until a PyRel disjunction pattern is measured; Lean and Ossie refuse | Proposed, GC4 spec |
| D6 | Plan review instrument and `auto` delegation | Owner to select; project bar is the maintained panel | Open |
