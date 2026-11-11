# Guarded rule authoring · close outcome

The runtime candidate is `618141de9975c4ef30871a979532654267a15de6`
on [draft PR #190](https://github.com/vasiloglou/gnd-public/pull/190).
The [approved plan](../001-plan-gate.md) followed two standard-panel
rounds with five complete valid reviewers each. Its
[close amendments](guarded-rule-authoring-plan.md#close-amendments--2026-11-11)
resolve the comparison binding language and the directed pair option.

| Plan criterion | Observed gate |
|---|---|
| GA1 / A1–A3 / [GR-D8](https://github.com/vasiloglou/gnd-public/issues/179) | The [phase record](../003-phase-GA1.md) shows active fail/warning and active pass for atom, absence, exists and comparison. A mixed model with an unserved rule still emits mandatory and ring violation cases. The shipped example produces four guarded examples and 15 ordinary populations. Scoped measure scores all 15 with zero checker defects. Full-model measure refuses the digest at exit 3. The installed repeated-variable guard keeps one binding on both cases and no other findings. |
| GA2 / B1–B3 / [GR-D10](https://github.com/vasiloglou/gnd-public/issues/181) | The [phase record](../005-phase-GA2.md) pins ordered class support, first omitted ordinals, marker scope and missing or ambiguous classifications. The cross-class near miss has 1 violation in 21 distinct outgoing edges. The same-class near miss has 1 in 22. Both name the original `ft0#20` row and now confirm that witness with the checker. The marked and all-inside controls pass. The installed guarded proposal passes evolve preview. |
| GA3 / C1–C3 / [GR-D11](https://github.com/vasiloglou/gnd-public/issues/182) | The [phase record](../007-phase-GA3.md) shows exact typed literal mapping in all four positions, the shared-predicate `area:cli` rule, and three supports of 1/1. The category rule reaches two body bindings and one head pair. Incorrect support or a false head pair leaves the proposal absent. The per-rule and aggregate preflight controls reject one below the required bound and pass at equality. The unchanged export goldens pass. |
| Installation | The [installed receipt](../evidence/GA3/installed-smoke.json) binds the candidate, wheel, lock, inputs and nine CLI results. The [replay](../evidence/GA3/installed-smoke-replay.md) installs the optional synth extra offline. The smoke ran from scratch directories with isolated Python module resolution and the installed package under its own environment prefix. |
| Independent phase review | [GA1](phase-GA1-codex-review.md) and [GA2](phase-GA2-codex-review.md) requested changes. Their phase records reproduce and disposition every finding. [GA3](phase-GA3-codex-review.md) found no reproducible defect in the reviewed AMIE diff. Each reviewer read one public candidate. Current-runtime verification below covers the review repairs and the missing-extra refusal found by the installed smoke. |

## Question sweep and boundaries

The predecessor's three deferred issues are implemented under their
reviewed current scope. Generated examples exercise the authored guard
and do not establish intended policy. The first case generator serves
asserted scalar shapes without existential filters. It reports bounded
search refusals and records unrelated findings. The existing ordinary
measure contract remains bound to its scoped model. Joined discovery
requires explicit roles and complete functional endpoint classification.
Typed AMIE import uses its existing token alphabet and the new aggregate
limit applies to all mined inputs, including variable-only rules.
The AMIE fixture is in capture format. Live miner execution and external
publication are outside the delegated milestone. Proposals remain advisory.

## Current-runtime verification

Use the repository's development dependencies with the synth extra.
Run the union of the affected workflow and compatibility tests, using the
candidate source tree and the offline wheel cache.

```sh
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" python -m pytest -q \
  tests/test_synth_guarded_cases.py tests/test_synth_conforming.py \
  tests/test_synth_expectation_independence.py tests/test_synth_mutate.py \
  tests/test_measure_coverage.py tests/test_synth_false_pass_quarantine.py \
  tests/test_discover_guarded_join.py tests/test_discover.py \
  tests/test_ilp_amie_constants.py tests/test_ilp_amie.py tests/test_ih1_counting.py \
  tests/test_ih2_ownref.py tests/test_ilp_learners.py tests/test_public_guarded_consequent_matrix.py \
  tests/test_guarded_diagnostics.py tests/test_rule_edition_comparison.py \
  tests/test_rf1_cli_pins.py tests/test_rf1_layering.py tests/test_rf5_commands.py \
  tests/test_rf6_query_policy.py tests/test_query_budget_headroom.py \
  tests/test_development_scaffold.py -p no:cacheprovider --tb=short
```

The candidate wheel was also installed in a base-only environment. Guarded
synth returned exit 5 and the synth-extra installation hint, with the
output root absent. Ruff passed on the changed source and test files.

The current-runtime union exited 0 with
`1023 passed, 5 deselected in 230.89s (0:03:50)`. The repository's
default marker filter excluded the five tests. The strict component check
against the predecessor merge exited 0 with no stale or unassigned
entries to fix. Its two reread notices concerned the existing synth
subsystem description and the ILP service description. Both still describe
their actual dependencies and operation.
