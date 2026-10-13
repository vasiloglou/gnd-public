# CS1 independent adversarial review one

Reviewed current runtime working diff against `b57046f`, including the new
untracked `src/gnd/compiled_obligations.py`. Read-only production inspection;
temporary public probes ran with `UV_CACHE_DIR=/tmp/gnd-review-one-uv uv run python`.
No provider or certification invocation.

## Verdict

No reproduced runtime blocker. One minor public-interface hardening issue and
additional discriminating regression suggestions remain.

## Reproduced hardening issue

`src/gnd/checker/_core.py:2052–2065` accepts arbitrary truthy values for the new
`compiled_operations` option. With the admitted nonnumeric issue fixture,
`checker.check(model, population, compiled_operations='false')` adds 23 compiled
rows. `api.check` rejects this input with TypeError instead. Because this new mode
asserts standing implications, consistently reject non-booleans at its public
entry points. Suggested test: direct checker and batch calls with `'false'`,
`1`, and `None` must reject rather than activate/disable through truthiness.
This is hardening rather than a blocker for correctly typed calls.

## Focused probe evidence

- Indexed matching with pairs `(x,a),(y,a)` and A(a=1) accepted B(1,1) but rejected
  B(1,True): typed identity and repeated-role conjunction preserved.
- The same matching consumes four role-cell visits; WorkBudget(3) raised
  CompiledWorkLimit rather than returning partial offending rows.
- Removing `var_filtered_compare` coverage from the admitted numeric fixture
  produced an unchecked `filter_compare.pre_numeric` row with
  `compiled-obligation-uncovered`. Overall band was 1 because other authored
  obligations still failed, demonstrating stronger-failure precedence.
- Removing `role_is_numeric` coverage produced the same explicit compiled
  unchecked row and overall band 4.
- Replacing `role_is_numeric` with an admitted opaque derived-rule declaration
  produced `compiled-obligation-unavailable` for the numeric compiled obligation
  and overall band 4, rather than inferring absence from an opaque rule.

## Regression suggestions and boundaries

The shared matcher preserves the previous same-required-row conjunction. The
snapshot composer uses effective relations, makes coverage and unavailable
derivations explicit, and invalidates narrower projection/Phase1 evidence.
The service composes after its actual anchored evaluator; API/CLI occurrence
admission combinations are expressly refused. Dynamic-derived eligibility is
now explicitly ruled on in the CS1 spec and is no longer a plan ambiguity.

Retain automated controls for typed int/bool/string distinctions, repeated roles,
both coverage sides, budget exhaustion, opaque rules, and exact-term-unavailable
derived heads. Include the dynamic-derived entry case in the snapshot matrix
with its documented exclusion from walk agreement. No exact-term-unavailable
probe or anchored/reference probe was run by this reviewer; those remain test
suggestions, not observed failures. The broader CS1 corpus is being authored by
the owning agent; this review does not claim that corpus is already complete.

## Bounded repair follow-up

Reviewed the two identified repairs without production edits. The checker and
batch entry points now reject non-booleans before reading inputs. The composer
now recompiles the current operation declarations using the shared compiler and
effect index, without mutating the historical loaded side table. The redaction
policy also consumes that same current compiled-entry helper, keeping updated
locators and witness suppression aligned.

Ran:

```text
UV_CACHE_DIR=/tmp/gnd-review-one-uv UV_PROJECT_ENVIRONMENT=/private/tmp/gnd-issue16-audit/venv uv run --no-sync --python 3.11 pytest -q tests/test_compiled_snapshot_obligations.py::test_low_level_activation_is_boolean tests/test_compiled_snapshot_obligations.py::test_current_operation_edits_do_not_reuse_stale_compilation --tb=short
```

Result: **4 passed in 0.07s**, exit 0. The valid operation modality mutation now
produces a deontic warning rather than reusing its earlier alethic compilation;
the three invalid activation inputs consistently raise TypeError at both lower
public entry points. No blocking finding remains from this review. These checks
establish the bounded repairs only; no additional review round is requested.
