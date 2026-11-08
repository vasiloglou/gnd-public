---
milestone: rule-check-followups
station: phase-FU2
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-FU2
date: 2026-11-07
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_fu2_*.py tests/test_rc5_tool_output.py tests/test_population_load.py"
  exit: 0
  output: "79 passed"
  note: >-
    The plan section 9 FU2 row (V2), at 95803eae. The mutants, the RF guard
    files, the component index check (V6) and the sharded full default
    suite against main 6651e5a4's failure list (V1/V3) are in the body.
evidence:
  - path: src/gnd/population.py
    sha256: d78d63e270ba0108d44501c38db3bfa1c23cedf8c2de11484d581c2ac66fb3e8
  - path: src/gnd/model/__init__.py
    sha256: 6191993b9d0c0e9b8db4337cabfbddcec1e9890b348300cc38acc4df54698665
  - path: tests/test_fu2_population_header.py
    sha256: acaa0f329b64aa8f0855e29544ae1e69eb7ad8535df2c828b2193209e744eac4
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: e629f0a348a1c7b03ac6ab1dc637eee10b6ec6c43e531bd2a4ed630200def901
  - path: dev/components/COMPONENTS.md
    sha256: 8de25c7285226d81ba3a1b00e4f5083aa4f8773b01ec7016dee154c1e4d32d89
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU2-spec.md
    sha256: 18006acd015bdfc1a8d6b1aa7d0c9f2a55d8e9373019af57f5d88bf784b4b1a2
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU2-codex-review.md
    sha256: 01fa7ea89b3bffd78f88d64f97b5ced4a816b176e9164286d48100dfb9366fc8
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU2/full-suite-fu2-10265ddf.txt
    sha256: 73cb9cba517f38e897777880290193e0e535d7e860269b324564e16674916474
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU2/full-suite-fu2-95803eae.txt
    sha256: b7a0b3c025b957387b0d283a1f4cf5fc58496b3980740b7c145ca5b1a0172c3d
---

# Claim

At 95803eae, no `Population` reached through validated construction or
`model_copy` carries a `producer` unless its `source` is `tool-output` and
the producer is a 1-200 character string (issue 115), and a population
combined with its references keeps the candidate's `label` (issue 116).
`model_construct` stays unvalidated (D3), and `check` refuses its output.
No report's bytes changed; the full default suite's failure list equals
main's.

## What shipped

- **M1** `src/gnd/population.py`: `Population.model_copy` re-runs the
  producer validator on the copy whenever `update` is given; the
  validator now also requires a string (review R1).
- **M2** the reference binder's header (`src/gnd/model/__init__.py`) and
  `_combine_validated_populations` carry the candidate's `label`; reference
  labels are ignored, as their `source` and `producer` are.
- **Tests** `tests/test_fu2_population_header.py` (approved red at
  e3a0ec54): T1-T8, 13 cases with the R1 successor.
- **Guard bookkeeping**: the RC5 successor row for `bind_population` in
  `compiled-snapshot-obligations/evidence/CI/source-successors.json` is
  chained to the new body; component index entries `model.loading` and
  `model.population_loading` updated and regenerated.

## Gate output (verbatim)

V2, at 95803eae:

    uv run pytest -q -p no:cacheprovider tests/test_fu2_*.py tests/test_rc5_tool_output.py tests/test_population_load.py
    79 passed in 1.53s

FU2 tests at each stage (`uv run pytest -q tests/test_fu2_population_header.py`):

    e3a0ec54 (red, approved):              8 failed, 4 passed
    10265ddf (M1, M2):                     12 passed
    mutant, M1 removed:                     4 failed, 8 passed
    mutant, binder half only:               4 failed, 8 passed
    mutant, combiner half only:             3 failed, 9 passed
    R1 successor case before its fix:       1 failed, 12 passed
    95803eae:                              13 passed

RF guard files, at 95803eae:

    ls tests/test_rf*.py | xargs uv run pytest -q -p no:cacheprovider
    2396 passed in 185.39s (0:03:05)

V6, component index:

    python3 scripts/components_index.py changed --base 12daa5b7 --strict
    changed against 12daa5b7 (12daa5b): 12 file(s) differ; 0 to fix, 0 warning(s), 7 to reread
    exit=0

The 7 rereads are the subsystem entries whose members `model.loading` or
`model.population_loading` changed (check, synth, codegen, conformance,
measure, evolve, recovery); each was read beside the diff and is still
accurate: FU2 changes no subsystem's role.

V3, full default lane, six round-robin shards on beast-3:

    fu2  10265ddf: 17828 passed, 3 failed, 2 errors; shards exit 0,0,0,1,1,1
    fu2b 95803eae: 17832 passed, 2 errors; shards exit 0,0,0,0,0,1
    failing list at 95803eae: sha256 8261732b98e252d1e17e491a8480080bafd2434fbd17f8a503aad8390ea9c20a (equal to main 6651e5a4's)

The first run's three failures were guards, repaired in 95803eae (spec
I4): the RF6 verbatim-body pin of `bind_population`, and two RF6
query-policy inventory tests that counted a `Mapping[str, Any]`
annotation. The 2 errors are the `tests/test_public_optional.py` uv-version
pins. Evidence: `evidence/FU2/full-suite-*.txt`.

## Criteria

| Criterion | Result |
|---|---|
| FU2-C1 | T1 (a)-(e): each copy that would break the pair raises; T2: valid copies succeed and a plain copy keeps its marker; T3: `model_construct` builds a bad pair, has no marker, and `check` exits 70 (D3) |
| FU2-C2 | T4, T5: the candidate's label survives `bind_population` and wins over a reference's; T8: the combiner reads it; T6: the labelled combined digest is pinned and differs from the unlabelled one; T7: the witness candidate binding equals the value pinned at 12daa5b7 |
| FU2-C3 | T6: the unlabelled combined digest equals the value at 12daa5b7; the RF1 content-digest golden is unchanged (in the RF guard run); the failing list equals main's |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 12daa5b7 10265ddf`, disposition `revise`, two findings, both
reproduced and fixed: [phase-FU2-codex-review.md](notes/phase-FU2-codex-review.md).
R1 (hardening): a copy could set a list producer; the validator requires a
string, successor case T1 (e). R2: the README was stale. The later repairs
(f9792dac, 95803eae) carry no review opinion.

## Refactoring review

None needed. M1 reuses the one producer validator instead of restating
it, and M2 follows the binder's existing pattern for `producer`. The phase
exposed that the binder builds the combined header by hand, field by field,
which is how `label` was lost; a shared "candidate header" helper would
remove that class of bug, but the binder and the loader read different
inputs (a `Population` and a document), and with two callers and five
fields it would add an indirection for little gain.

## Boundary: what this phase does NOT establish

- `model_construct` is unvalidated (D3); T3 pins only that `check` refuses
  its output. In-process code that reads a constructed population's header
  without checking can still see a bad pair.
- Field types other than the producer are not re-validated on copy
  (spec §9), e.g. `update={'source': 'bogus'}`.
- The Codex review covered 10265ddf; f9792dac and 95803eae were checked
  by the gates above, not re-reviewed.

## Open questions

| Row | Question | Owner / target |
|---|---|---|
| FU2-O1 (spec I5) | Plan §0 rule 5: the test file is 194 lines against the 120-line stop line, and the pause for the owner did not happen at the red-test gate. Accept the size, or trim the tests? | owner, before merge |
