# RC2 diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin (codex-cli 0.163.0), 141,692 tokens, exit 0.
- Reviewed bytes: `git diff c5fe86bb cbcd0e86 -- src tests tools` (implementation commit cbcd0e86; corpus commit 9130e93d inside the range).
- The reviewer ran in a read-only sandbox. It reports running sampled graph checks of its own; it did not run the repository's suites. The output below is unedited and contains no local path; the trailing "codex exit=0" line is the driver's, not the reviewer's.

## Reviewer output (verbatim)

```text
DISPOSITION: block

ID: Q1
SEVERITY: high
LOCATION: src/gnd/checker/_core.py:363
QUOTE: pairs = ring_pairs(constraint, adapted.snapshot)
PROBLEM: The checker evaluates ring rules with all fact types treated as covered, but this call uses the original coverage. With the `two-groups` facts and `covers: []`, version 7 reports a failed cycle; version 15 keeps that single cycle row and message instead of listing all four in-group edges.
FIX: Read pairs from the same effective-coverage snapshot the checker evaluates, and add this input to the corpus.

ID: Q2
SEVERITY: medium
LOCATION: src/gnd/model/_validation.py:3636
QUOTE: outgoing = {node: sorted(dependencies[node] & set(dependencies)) for node in sorted(dependencies)}
PROBLEM: Rebuilding `set(dependencies)` for every node makes this formerly linear preparation quadratic. A model with thousands of independent derived heads incurs repeated full-set construction; the small random graphs in T8 do not reveal it.
FIX: Construct the node set once before the comprehension.

ID: Q3
SEVERITY: low
LOCATION: src/gnd/checking_service.py:486
QUOTE: if verdict.verdict == "fail" and verdict.constraint_type == "ring"
PROBLEM: A failing `asymmetric` or `intransitive` rule also triggers `acyclic_extents`, which recalculates derivations and adapts the snapshot despite having no acyclic extent. A large derivation model with only a failing asymmetric rule pays for that extra pass.
FIX: Filter for the two acyclic variants before calling `acyclic_extents`.

ID: Q4
SEVERITY: low
LOCATION: tests/test_rc2_acyclic_extent.py:210
QUOTE: from gnd.model import _derivation_components
PROBLEM: T8 claims to check every retired SCC caller, but never calls `_derivation_cycles`. For two mutually recursive heads, that function could return no group and T8 would still pass.
FIX: Assert `_derivation_cycles` results on a derivation document containing a cycle.

CONFIRMED: C2 holds for the covered corpus: adding its disjoint cycle preserves the existing edge rows.
CONFIRMED: The version-7 path does not call the new extent computation; the extracted pair logic is unchanged by inspection.
CONFIRMED: C4’s 2,047-edge fixture produced 780 extent rows and the specified group sizes in under 0.5 seconds.
CONFIRMED: The shared Tarjan walk matched independent SCC membership on 4,000 sampled graphs and the retired PyRel output order on 2,900 sampled graphs.
CONFIRMED: For covered corpus inputs, version-15 text takes its message from the version-15 payload.
codex exit=0
```

## Triage (driving agent, 2026-11-06)

Every finding was reproduced before it was believed. Each fix carries a
regression test in `tests/test_rc2_acyclic_extent.py`, run against the pre-fix
code and observed failing for the stated reason.

| ID | Class | Reproduced | Disposition |
|---|---|---|---|
| Q1 | blocking | yes: `two-groups` with `covers: []` gave exit 1 with the single row `['a', 'b', 'a']` and the version-7 message under `--rule-ids` | fixed: the coverage widening `_evaluate_constraint` applied moves unchanged into `correspondence.evaluation_snapshot`, which the checker and `acyclic_extents` both call (one home, no second copy). Regression `test_q1_extent_reads_the_coverage_the_checker_evaluates`, red before the fix |
| Q2 | hardening | yes: 20,000 independent heads took 4.2 s in `_derivation_components` | fixed: the node set is built once. Regression `test_q2_derivation_components_preparation_is_linear` (bound 1 s), red before the fix |
| Q3 | hardening | yes: a failing `asymmetric` rule adapted a second snapshot | fixed: `acyclic_extents` returns before any derivation or snapshot work unless an asked ref is an acyclic ring rule. Regression `test_q3_no_extent_pass_without_an_acyclic_rule`, red before the fix |
| Q4 | completeness (test gap) | yes: T8 never called `_derivation_cycles` | closed: `test_q4_derivation_cycles_keeps_its_groups` (two-node cycle, self-loop, a downstream head excluded). It passes before and after, as it should: there was no defect, only no case that could catch one |

The fixes were not re-reviewed.
