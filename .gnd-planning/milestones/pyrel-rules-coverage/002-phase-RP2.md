---
milestone: pyrel-rules-coverage
station: "phase-RP2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RP2
date: 2026-11-21
gates:
  - command: "uv run pytest -q tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short"
    exit: 0
    output: "218 passed, 198 deselected in 16.84s"
  - command: "uv run pytest -q -m pyrel_oracle tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py --tb=short"
    exit: 0
    output: "128 passed, 36 deselected in 237.07s (0:03:57)"
    note: "opted in by the owner for this milestone (plan §8); baseline at 8c909013 was 110 passed"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 107.10s (0:01:47)"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "uv run ruff check"
    exit: 1
    output: "Found 198 errors."
    note: "known red, proven at the base 92cd5c9b in a throwaway worktree: the same 198 errors, all in dev-tools-delivered skill scripts (.claude/.codex skills/{process-phase,components,dev-handoff}/scripts), which this repository does not edit (project.md)"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the unchanged broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP2-spec.md
    sha256: d3772935a73b707b9e756a6f5addcddd6674757ffaeb4131971ff5f429d7dc2d
  - path: src/gnd/export/pyrel_rules.py
    sha256: 4fcbdfed4bfc6bd5fab6da4a65f915e77c8ae2fb886f0a1b364e47d9ca30f654
  - path: src/gnd/export/emit.py
    sha256: 9b7c78fbee6b1213347022704de5218ac662ee7fc2679651a3338b9af51f5286
  - path: src/gnd/commands/export.py
    sha256: cfafa284b490e3305f631f75036b11e7531e5aa9d495a83e9138008bf74b8644
  - path: tests/test_rp2_anchored.py
    sha256: 1eab19333ca2d3c7d063afe20d1d237f8a707143d51f5496d5682ecd4128e8fe
  - path: tests/test_pyrel_rules.py
    sha256: 2de4d990c67ad806078ada52e324fe5a22af2c19049b313d0fe613b54aa2f77b
  - path: tests/fixtures/pyrel-rules-coverage/rp2/anchored-only.orm.json
    sha256: fe4eeec8ce640acca14e8dd660b69f39fab434cd5d506b07d3a730dc95948084
  - path: tests/fixtures/pyrel-rules-coverage/rp2/anchored-deontic.orm.json
    sha256: 74096f3c852f2c6dd1785fbd1e073008214e7b6985fd86b68f67ce961a473f58
  - path: tests/fixtures/pyrel-rules-coverage/rp2/full.population.json
    sha256: 4d4bf2f86d3f8d30f52e8a08db2ac53cbf657a35a8a2cb56fbd042dafb4ff1ba
  - path: tests/fixtures/pyrel-rules-coverage/rp2/empty.population.json
    sha256: 0eb7ec7b25185e8d348bba8c6ddde655efd25c0933459b41f7caea93eaba2754
  - path: docs/runtimes/pyrel.md
    sha256: 78e50f2054a7f647c6240627a84ed1946bb9f7755d583b14dddd17ecdc5777aa
  - path: docs/explanation/rules-as-pyrel.md
    sha256: 567fee8a6e009e831afb81b89cf78ec5f2eaa9a572fd6ad9761a1bd46dc3676d
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.md
    sha256: 6720518b4d03879d99221bba2d9d25459953bcc91cf24175b26c0baf97d72d1b
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/BRIEF.md
    sha256: ac8f642af7aa2da4df88a79d3b7402f57da619cdf456d83154ead9b60177efc9
  - path: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/FINDINGS.md
    sha256: e16e503b68291d637a13b95d6bebe94ab5d818380a33c30a3cc282187f79e6d9
---

# Claim

RP2's criteria C1–C8 hold at these bytes. Both rules programs list every
anchored constraint by id as not checked, with a reason, and compile none
of them. On the twelve gold populations of the flat literature model the
DuckDB program agrees with `gnd check` (exit 4) through the extended
comparator, whose negative control fails as it must.

## What shipped

- `export/pyrel_rules.py`: the fact-scoped family walk lists `anchored` in
  `model.unchecked` with `_ANCHORED_REASON`; every not-checked row carries a
  `reason` (textual: `textual rule: <expression>`), and the DuckDB report
  prints `<id>  not checked  (<reason>)`, byte-identical for textual rules.
  The LQP program gains `not_checked()` and `lqp_report(problems)` (exit 1,
  else 4 for a listed must-rule, else 0, D5); `--compile` lists them first.
  `render(..., not_checked_ids=)` returns the listed ids; `render_report`
  wraps it. The body keeps the name `render` so the RF6 dynamic-query
  inventory, historical evidence of another milestone, is unchanged.
- `export/emit.py` and `commands/export.py`: the rules success line appends
  `; N rule(s) are not checked (listed in the program)` when N > 0; with
  none, and in the checker export, the line keeps its bytes (RP2-D1).
- `tests/test_pyrel_rules.py`: the shared comparator maps a `not checked`
  line and an `unchecked` verdict to `(rule, 'not checked', null)`, and now
  also reads GND's unchecked or vacuous derivation verdicts.
- Docs: `docs/runtimes/pyrel.md` (one home of the list) and
  `docs/explanation/rules-as-pyrel.md`.

## Gate output (verbatim)

    218 passed, 198 deselected in 16.84s
    128 passed, 36 deselected in 237.07s (0:03:57)
    679 passed, 2 deselected in 107.10s (0:01:47)
    All checks passed!
    Found 198 errors.            (uv run ruff check; known red, see gates)

## Criteria, measured

| Criterion | Test | Result |
|---|---|---|
| C1 | `test_anchored_models_render` (8), `test_quantity_fixture_passes_anchored_and_stops_on_its_value_rules` | pass |
| C2 | `test_anchored_ids_are_listed_and_never_compiled` | pass |
| C3 | `test_gold_populations_agree_with_gnd` (12, oracle) | pass, exit 4 both |
| C4 | `test_textual_reason_keeps_the_printed_line`; existing `textual` review cases (oracle) | pass |
| C5 | `test_success_line_counts_the_listed_rules`, `..._without_listed_rules_is_unchanged`, `test_checker_export_success_line_is_unchanged` | pass |
| C6 | comparator change; `test_negative_control_a_dropped_anchored_id_disagrees` (oracle) | pass |
| C7 | `test_lqp_report_lists_the_rules_and_bands_a_must_rule_four`, `test_lqp_compile_prints_the_not_checked_rules` (oracle) | pass |
| C8 | `test_anchored_over_an_empty_fact_list_is_still_not_checked` (oracle), and the deontic case | pass |

## Implementation findings

1. The shared comparator ignored `report['derivations']`, so five gold
   populations whose derivation is not in `covers` disagreed on the
   comparator's side while program and GND agreed (both print the
   derivation as not checked). Fixed in the comparator.
2. The first version of that fix used `report.get('derivations', [])`; GND
   reports `None` for a model without derivations, and 33 oracle tests
   failed with `TypeError`. Fixed with `or []`; the rerun is the gate above.
3. Renaming `render`'s body to `render_report` reddened
   `test_rf6_query_policy` (its counted inventory is keyed by function
   name). Kept the name, added a keyword out-parameter instead.

## Review

One reviewer is one reviewer: Codex (read-only, through the review
helper, `notes/reviews/phase-RP2-r1/`), verdict APPROVE, no findings. It
verified the 17 file digests, the anchored listing, textual byte identity,
the success lines, LQP precedence, the negative control and the 21
original corpus finding sets, and that eleven checker programs and three
Ossie bundles keep their baseline bytes. It could not run DuckDB or PyRel
compilation (sandbox), so its verification of the oracle tests is by
reading; the oracle lane above is the executed evidence. `review.log`
(machine paths) is not retained.

## Refactoring review

Executed: the not-checked line had one hard-coded shape for textual rules;
it now prints a `reason` held on the row, the one home for that text, which
both programs and both kinds use. Behaviour-preserving for textual rules
(C4). Nothing else in what RP2 touched needs change; the out-parameter on
`render` is a workaround for an inventory keyed by function name, not a
structure worth changing in this milestone.

## Boundary — what this phase does NOT establish

- No RelationalAI engine ran; the LQP program's enforcement is unverified.
  RP2-C7 runs its report function with the engine call absent.
- Agreement is with `gnd check` without a sidecar. With `--anchors` and
  `--document`, GND decides anchored rules and the programs do not.
- The comparator now covers unchecked and vacuous derivations only;
  derivation failures are still compared in `test_pyrel_rules_derivations`.
- `uv run ruff check` over the whole tree stays red (known, pre-existing).

## Open questions

None new. Plan §10's RP1 questions remain for RP1.
