# GC3 · Disjunctive guarded consequents · draft r1

The [milestone plan](guarded-rule-clauses-plan.md) supplies A1 through A4
and D4. GC3 starts after GC2's completion record.

## Contract and selected predicates

| Criterion | Contract | Evidence |
|---|---|---|
| A1 | A guarded consequent may have `any_of` with two or more alternatives. Each alternative has one of the existing comparison, fact, absence or exists forms. Nested disjunction is invalid. Alternative scopes share positive antecedent variables. An exists branch may introduce local variables. | Schema rejection for nesting and arity, semantic rejection of references or bindings leaking across alternatives. |
| A2 | Evaluate alternatives separately for each surviving binding. Any true alternative makes the binding true. With no true alternative, any unknown makes it unknown. All-false is a violation. An exists alternative retains its own coverage and undefined-candidate precedence. A shared work ceiling applies across evaluation. | Public verdicts and direct reference verdicts on three-valued cases, plus a covered, decidable 200-case seed differential against a semiderived union. Both pass and fail must occur. |
| A3 | Default reports retain their field set. Version 17 applies to opt-in guarded diagnostics for models with any_of. Each violating binding has an ordered entry per alternative with its index and reason. Reasons include false comparison, missing required fact, present forbidden fact, missing exists atom, and no joint witness. | Opt-in payload schema validation and exact failure detail cases. Assert legacy v16 output on an unchanged model. |
| A4 | The guarded sentence states at least one alternative must hold. Guarded-cases v1 generates active fail and pass for representative reachable disjunctions containing all four alternative forms. | One-sentence CNL and run/check both manifest cases. |

## Standing rules

1. **Totality.** Admit alternative arrays under the schema and validate
   alternative payloads through the same single-form guards. Unbound and
   malformed alternatives get named refusals.
2. **Cap the algorithm.** Prepare relation indices once per alternative
   under the common budget. Bound total rows prepared and binding evaluations.
   A work-limit outcome is unchecked and keeps a distinct reason.
3. **Validation order.** Keep reference and role-claim checks before the
   grounding and type checks. Alternative path prefixes identify the selected
   subobject. Existing single-form refusals keep order and identity.
4. **One walk.** The shared guarded walks enumerate consequent shapes and
   alternate-local terms. Compute each exists branch with a separate local scope.
5. **One home.** Define the syntax and three-valued composition in the Guarded
   constraints section of representation-format. Rule-check-report owns v17
   field details.
6. **Measure.** Measure the new evaluation and projection instead of assuming
   that a union, independently joined exists atoms, and any_of always agree.
   Assert work-limit and undefined cases independently of helper parity.

## Verification

Run the new disjunction corpus, guarded membership and antecedent-filter
corpora, public guarded/evaluator/diagnostic tests, the temporal legacy gate,
synthesis, CNL and schema synchronization. Run the affected exporters with
explicit unsupported-form boundaries, the issue #171 guard list, lint,
and the component index. Phase-diff review uses Claude Code per the owner's
selection. The exact verification ledger and delegated corpus gate precede
implementation.

- Initial corpus and focused lane use `uv run pytest -q tests/test_guarded_disjunction.py --tb=short`
  and the GC2 focused suite with `test_public_guarded_consequent_matrix.py`
  and `test_rc1_rule_ids.py` added.
- Repeat the explicit GC2 exporter and #171 guard commands, Ruff, and
  `python3 scripts/components_index.py changed --base main --strict`.

The component consult for “guarded consequent disjunction” found the shared
atom and term walks in model validation and the existing snapshot guarded
specification. Adapt those and the registered guarded implementation;
no external component was selected.
