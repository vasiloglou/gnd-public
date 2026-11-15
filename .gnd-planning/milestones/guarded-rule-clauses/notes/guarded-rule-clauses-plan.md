# Guarded rule clauses · plan r3 with close audit amendment

**Status — r3, 2026-11-15.** The owner selected the Standard
GND review panel for plan and close and delegated approval rulings with
`auto=true`. Both reviews and the final amendments are recorded in
[the review disposition](plan-review-disposition.md).

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
  holds when at least one alternative holds, and the opt-in diagnostics report
  gives a failure reason for each alternative of a violated rule.
- **Every form** passes a differential test over covered, decidable generated
  populations and explicit fixtures for applicable unknown outcomes. Guarded
  synthesis produces a failing and a passing case for representative reachable
  shapes, including the issue examples. For GC1, an exhaustive finite domain with only one reachable verdict yields
  a named refusal.
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
   learn the new sites (negated atoms, `where` terms, membership list members, `any_of` alternatives)
   once, so every existing guarded check (term refs, role claims, literal
   domains, binding types, grounding) covers them without per-site copies.
5. **One home.** `representation-format.md` "Guarded constraints" owns the
   syntax and semantics; constraint-reference, verbalization-patterns, CLI and
   docs pages cite it. The stale guarded row in constraint-reference (no
   `exists`) is corrected in GC1.
6. **Measure.** On covered, decidable populations, compare verdicts and the
   set of offending bindings projected onto the shared business variables
   using canonical ORM identity. Each fixed-seed sample has at least 200
   populations, including satisfied and violated controls. Assert coverage of
   every predicate read, availability of every comparison used, consistency of
   covered derived claims, and an active binding wherever the case is meant to
   exercise one. Use semiderived helper relations or assert the consistency of
   supplied derived claims. For GC2, compare an emptied native guard with a
   vacuous helper as zero active bindings and assert each public verdict
   separately. For undefined terms, missing coverage, and exhausted work,
   assert expected outcomes directly on both evaluator paths.

Use ModelIndex and `constraint_families.FAMILIES` dispatch, keep branch
evidence identities, register new refusal and unchecked scopes in
`branches.py`, keep the layer allowance at zero, and run the issue-171 guard
list in every phase gate.

## 1. Scope, sources and authority

Baseline `ecd12986` (GND 0.3.1, tag-only). Framework development: an
experiment-claim census cannot measure runtime coverage of rule syntax.

| Source and location | Obligation or constraint | Phase and gate |
|---|---|---|
| #195 Summary item 3 | `in` / `not in` with a list-of-literals right side in `term_comparison` and `guarded_comparison` | GC1 I1–I5 |
| #195 Summary item 1 | `negate` and `where` beside `antecedent` with derivation-clause semantics | GC2 N1–N4 |
| #195 Summary item 2 | `any_of` consequent over the four existing forms | GC3 A1–A4 |
| #195 Acceptance bullet 1 | Schema validation, differential test against the helper encoding over generated populations, one-sentence verbalization | GC1 I1–I4, GC2 N1–N4, GC3 A1–A4 |
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
from one membership domain. `guarded_comparison` and `term_comparison` become
`oneOf` the current shape and this one. The shared `comparison_operator` enum
is **not** extended, so value-comparison and dynamic rules are unchanged.
Semantics use a canonical, kind-tagged membership key compiled once per list.
Boolean and numeric identities are distinct. Integer, Float and Number share
an exact numeric domain. Date literals normalize to calendar dates and
duration literals to day counts, with tags distinct from raw strings and
numbers. Validation refuses a statically incompatible kind. An unavailable
left term or a runtime kind mismatch yields unchecked rather than a true
`not in` result. Preserve existing equality paths. Establish singleton parity
only for comparable inputs on which the existing equality uses the same
identity contract. D1 covers all existing sites below.

| Comparison site | GC1 contract |
|---|---|
| Guarded top-level consequent | Membership enabled through indexed, temporal and reference evaluation |
| Guarded `exists.where` | Membership enabled through its term filter and guarded synthesis |
| Ordinary, aggregate-bearing and headless `derivation_rule.where` | Membership enabled through derivation extension filters |
| `derivation_clause.where`, `derivation_headed_clause.where` | Membership enabled through derivation extension filters |
| Value comparison and dynamic rule | Existing operator restrictions remain |
| Exporter profiles receiving any of these forms | Explicit refusal from GC1 wherever translation is unavailable, including PyRel rules/runtime, Lean, Ossie and Soufflé paths that consume the form |

**GC2 · antecedent `negate` and `where`.** Positive atoms bind variables. A
filter can prove exclusion by a definite false `where` or a matching negated
atom. Otherwise an undefined comparison or negated relation with unavailable
or uncovered rows makes the binding unknown. A ground negated atom is a
global existence probe, including the shipped-order example. Every variable
of a negated atom or comparison must occur in a positive atom. Positive and
negative atoms read the existing effective view for constraints. For a
fully derived relation this is the covered claim, with derivation consistency
reported separately. A semiderived relation uses its effective calculated
rows. Missing coverage cannot prove an absence. Guarded tests add no facts
or derivation dependency edges. Pin a consistent covered claim, an inconsistent
covered claim showing both independent verdicts, and an uncovered derived
relation. Preserve refusal for an independently unstratifiable derivation. A
determinate filter-empty guard has zero active bindings and a vacuous verdict.
A first-empty index continues to describe only a positive join prefix. In
particular the index is absent when filters alone eliminate the bindings. A
covered empty negated relation never enters the positive any-empty test.
Count only definite survivors. If an unknown binding remains after exclusion,
the guarded verdict is unchecked before reporting violations.

**GC3 · `any_of`.** Each alternative is an `atom`, `comparison`, `absence`
or `exists` consequent and may use the comparison forms shipped in GC1.
There are at least two alternatives and nesting is refused. Each alternative
can read the antecedent bindings and its own local `exists` bindings. Per
binding, a true alternative wins over a data-unknown alternative. When no
alternative holds, an unknown alternative makes the result unchecked.
Each alternative uses its existing consequent semantics. In an `exists`
alternative an undefined candidate keeps its existing precedence over a
concrete witness. A true sibling can still decide the disjunction.
Exhausting the shared work budget records unchecked through the existing
limit path. A definite violation provides the alternative's index and a reason
on opt-in diagnostics, including an unmet atom, a false comparison, or a
failed joint witness when all atoms match individually.

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
| Term comparison | Share membership key semantics across guarded scalar evaluation, term filters and the independent synthesis oracle. Retain existing equality paths. |
| Evaluation | Adapt `semantic_spec.guarded_result` (reference) and `correspondence._indexed_guarded_*` (production); reuse `extensions._apply_negation` identity anti-join |
| Messages and verbalization | Adapt `verbalize.guarded_message`, `model_verbalization._guarded_cnl`; reuse `_derivation_cnl` negate/where wording |
| Synth | Adapt `synth/guarded_cases.build_pair` and `COMPARISON_PAIRS` |
| Exports | GC1 pins named refusals across membership consumers. GC2 and GC3 protect their new shapes when admitted. GC4 exercises the final translate-or-refuse matrix. |

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
| 1 | **GC1 · membership** | I1 schema and validation accept `in`/`not in` in guarded and term comparisons and refuse empty, oversize, mixed nonnumeric kinds and non-literal lists; value-comparison and dynamic rules still refuse them. I2 reference and production evaluators agree; typed identity (bool vs number, date vs string) and unknown left values tested. I3 differential test: `in` with an atom and `not in` with an absence of the derived membership witness, using otherwise identical active bindings over generated populations yields identical verdicts and offending bindings. I4 one-sentence verbalization, v1 synth pairs for reachable cases, and a named refusal when a proven finite domain forces one verdict. I5 exporter containment for guarded, existential and derivation membership. |
| 2 | **GC2 · antecedent negate/where** | N1 schema, safety and disconnection refusals; the walks cover negated atoms and `where` terms. N2 stratification argument recorded and tested with a negated derived fact type; uncovered negated relation yields unchecked, not pass. N3 production and reference evaluators agree, `--guarded-diagnostics` counts post-filter bindings, filter-only emptiness is vacuous with no first-empty positive prefix, and the covered/decidable helper differential matches after binding projection. Test active unknown filters separately. N4 verbalization reads as one sentence ("…, unless …") and synth produces a failing and a passing case, with one satisfying active binding and one excluded binding that would otherwise violate. |
| 3 | **GC3 · any_of** | A1 schema and validation (≥2 alternatives, no nesting, per-alternative grounding). A2 three-valued evaluation agrees across evaluators, including joint existential witnesses, undefined candidates, and work exhaustion. Compare covered, decidable cases against the union helper. A3 violation report lists each alternative's index and failure reason on the selected surface and pins bytes and report version for models without the new forms. A4 one-sentence verbalization and a synth pair per reachable alternative shape. |
| 4 | **GC4 · exports, docs, smoke** | E1 PyRel rules and runtime translate or refuse each form with a named `ProfileRefusal`; Lean, Ossie and affected Soufflé paths explicitly refuse unsupported forms; existing exports remain byte-stable. E2 normative docs, bookrec chapter 8, report reference and CLI reference updated, with the "Why not a derived fact type" helper patterns shown as the before. E3 installed-candidate smoke of active customer membership, the shipped-code exception, and delivered alternatives plus the existing test-account `exists` control. The GC4 spec pins the issue #195 fixtures, expected pass/fail verdicts, one-sentence verbalization checks, and `--rule-ids` feedback naming the original rule for each form. |

## 5. Documentation, skill and compatibility surfaces

`representation-format.md` owns syntax and semantics; `constraint-reference.md`
(guarded row, operators), `verbalization-patterns.md`, `docs/reference/cli.md`,
`docs/bookrec/08-guarded-rules.md` and the packaged model-authoring skills cite it.
The public report reference owns diagnostics fields and conditional report
versions. A model using none of the new forms validates, checks and exports
identically, including its existing default and diagnostics report bytes.

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
comparisons or dynamic rules, Soufflé translation of guarded rules, why-not for
guarded rules, publication, certification and dev-tools changes.

## 8. Execution, approval and review protocol

`process-phase` per phase: spec and owner gate, implementation, focused
verification with the [issue #171 guard list](https://github.com/vasiloglou/gnd-public/issues/171) and Ruff, independent diff and refactoring
review (one reviewer in a different tool), phase record, topic PR, separate
owner merge authorization. Plan review and milestone close use the maintained
GND review panel when the owner selects it. Close needs four phase records,
differential-test outputs, synth manifests, the smoke transcript and an
issue-to-criterion sweep.

## 9. Per-phase verification story

| Phase | Focused lane and affected consumers |
|---|---|
| GC1 | New `tests/test_guarded_membership.py` plus `test_model_guarded.py`, `test_public_guarded_consequent_matrix.py`, `test_derivation_rule.py`, `test_synth_guarded_cases.py`, `test_rule_verbalization.py`, `test_schema_sync.py`, affected PyRel, Lean, Ossie and Soufflé exporter tests, guard list |
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
| D3 | Diagnostics when `negate`/`where` empty the bindings | Count after filters; document v16 for this new case and omit first-empty index when the positive join was populated | Proposed |
| D4 | Where `any_of` per-alternative violation detail lives | Guarded diagnostics use v17 when the checked model contains `any_of`; default report shape and v16 diagnostics for existing models keep their current version | Proposed |
| D5 | Exporter policy for new forms | PyRel translates `in`, `negate`, `where`; refuses `any_of` until a PyRel disjunction pattern is measured; Lean and Ossie refuse | Proposed, GC4 spec |
| D6 | Plan review instrument and `auto` delegation | Owner selected the Standard GND review panel for plan and close and delegated this milestone's approval rulings | Selected |


## 11. Close audit amendment, 2026-11-15

This section supersedes the D1–D5 proposals in §10 for the close audit.
The r3 wording and the original gate are retained above and in commit
`e13e6926` respectively. The implementation evidence is the phase records
and the [close audit](close-candidate.md).

- **D1 and D2.** GC1 delivered shared guarded and derivation membership
  using the spelling `not in` for the negative operator.
- **D3 and D4.** GC2 counts definite survivors and reserves the
  first-empty index for the positive antecedent. GC3 adds version 17
  per-alternative failure details on the plain opt-in diagnostics route.
- **D5.** The prior proposal says “PyRel translates `in`, `negate`,
  `where`; refuses `any_of` until a PyRel disjunction pattern is measured;
  Lean and Ossie refuse.” The GC4 record specifies the measured readable
  PyRel scalar fragment, the embedded checker's named refusals, and the
  finite and Ossie profile dispositions. The installed issue smoke uses
  GND's native checker. The shipped-code policy has a compliant vacuous
  result when its exception applies.
- **D6.** The owner-selected Standard instrument covers the plan and close.
  The separate Claude Code step covers each of the four phase diffs.
