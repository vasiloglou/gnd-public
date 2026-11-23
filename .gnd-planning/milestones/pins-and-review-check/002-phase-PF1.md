---
milestone: pins-and-review-check
station: "phase-PF1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-PF1
date: 2026-11-23
gate:
  command: "uv run pytest -q tests/test_inventory_pin_home.py tests/test_packaged_skills.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_gate_guard_list.py --tb=short"
  exit: 0
  output: "241 passed in 45.56s"
  base: "04945d39 (PR 248 head: main a0270591 plus planning files)"
gates:
  - {name: "structure and inventory guards (project.md block, now with the four PF1 files)", command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_inventory_pin_home.py --tb=short", exit: 0, output: "866 passed, 2 deselected in 264.38s (0:04:24)"}
  - {name: "lint, plan form", command: "uv run ruff check src tests tools", exit: 0, output: "All checks passed!"}
  - {name: "lint, whole repository", command: "uv run ruff check", exit: 0, output: "All checks passed!"}
  - {name: "component index", command: "python3 scripts/components_index.py changed --base 04945d39 --strict", exit: 0, output: "changed against 04945d39 (04945d3): 22 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"}
  - {name: "T5, distribution lane, recorded once", command: "uv run pytest -q -m distribution tests/test_public_built_inventory.py --tb=short", exit: 0, output: "17 passed in 14.93s"}
  - {name: "guard tests on the version floor and head", command: "uv run -q --isolated --no-project --python 3.11 --with pytest python -m pytest -q -p no:cacheprovider --noconftest tests/test_inventory_pin_home.py (and --python 3.13)", exit: 0, output: "py3.11: 3 passed in 2.60s / py3.13: 3 passed in 2.63s"}
  - {name: "D1 baseline, default lane at the base, beast-3, six shards", command: "uv run pytest -q --tb=line -p no:cacheprovider <tests/test_*.py, NR%6==i>", exit: 1, output: "20077 passed, 19 failed, 2 errors, 13 skipped (sum of six shards)"}
selection:
  - {obligation: "PF1-C1..C4, T1-T4", disposition: run, command: "the gate above and the guard block"}
  - {obligation: "PF1-C5, D1 baseline", disposition: run, note: "beast-3, uv 0.13.x and Python 3.13, not the CI pin; failures listed below"}
  - {obligation: "T5", disposition: run, note: "once, distribution lane, not a gate"}
  - {obligation: "broad lanes (evidence, census), certification", disposition: cadence, note: "not selected: no explicit owner request"}
evidence:
  - {path: tests/test_inventory_pin_home.py, sha256: baa30ed6a5961376f0a0b7c13fe6dd86b15364154e2363f651dc39f1fe581985}
  - {path: tests/test_install.py, sha256: 9fbbb5d182efb1f216cf340b0dac6ab4aeb2bc0affbc9e921758403aaf8a02f8}
  - {path: tests/test_doctor_uninstall.py, sha256: 95964bc20e62394655ad629badbea316d4ca163fef5d82a8bd220e706d493f99}
  - {path: tests/test_verification_fixes.py, sha256: 0f88507ab2a9d84dd37add178320f14587ba2758153dec5e8962706f9b5e2bcf}
  - {path: tests/test_public_built_inventory.py, sha256: ac6cba98edf0aa5766a6251ea081683b66f04076c19107b6192b70f25c8f8cd7}
  - {path: .codex/skills/process-phase/references/project.md, sha256: 108f227dbd18635b725576b050e118e9adaa6ffa3c6e5393f85aadc4a5e6b749}
  - {path: .gnd-planning/milestones/pins-and-review-check/notes/phase-PF1-spec.md, sha256: 9b02046bf9f712c19f51e2166d9b10b4a26af30c711e1dd146fad222e556b83d}
  - {path: .gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/review.md, sha256: f89a90de3f77acc81d74b687152e9c0dd677fea9d9dc7ebe65d4cc7ab7a5188c}
  - {path: .gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r2/review.md, sha256: bf0462e7b24ca3d80bef745e45056a05544a791f7ef3e766b686bff09d8c69d4}
---

# Claim

The packaged-skill inventory (`EXPECTED_SKILL_FILE_COUNT`,
`EXPECTED_SKILL_NAMES`, `EXPECTED_SKILL_FILES`) is now defined only in
`tests/test_packaged_skills.py`. `tests/test_install.py`,
`tests/test_doctor_uninstall.py` and `tests/test_verification_fixes.py`
import it. The last pinned 70 files and failed 5 of 13 tests on `main`; it
passes. `tests/test_inventory_pin_home.py` fails when any test module binds
one of the names, in any scope and by any binding construct of the language
reference, other than by importing it unrenamed from the home. The four
files are in the guard block of both `project.md` copies.

Authority: plan r1, owner approval of 2026-11-23 (`001-plan.md`); spec r1,
owner approval of 2026-11-23 (spec §12), which was also the go-ahead to
implement. One change is outside the spec's listed homes,
`tests/test_public_built_inventory.py` (commit `c1ecb8c1`), and waits for the
owner's ruling. Not merged; merge needs the owner.

## Named criteria

| Criterion | Result |
|---|---|
| PF1-C1 one home | T1 `test_the_inventory_has_one_home` passes on the tree. Against the base it reports all three files (shown in the session by running the guard over `git show HEAD:<file>` at `04945d39`). Gate |
| PF1-C2 a planted copy fails | T2 `test_the_guard_sees_every_binding_form`: 34 binding sources reported (37 on Python 3.12+), 10 non-binding sources not. Gate |
| PF1-C3 guard block | both `project.md` copies name the four files and are byte-identical; `tests/test_gate_guard_list.py` passes inside the gate. Gate |
| PF1-C4 nothing removed | collected nodes unchanged: `test_install.py` 91, `test_doctor_uninstall.py` 80, `test_gate_guard_list.py` 3 (174, as H7), `test_verification_fixes.py` 13; all pass. Gate |
| PF1-C5 baseline reds | listed below |

## Baseline (D1), the reds that are not inventory copies

Default lane at `04945d39` on beast-3, six shards: 20,077 passed, 19 failed,
2 errors, 13 skipped. The 2 errors are the known pair in
`tests/test_public_optional.py`. Five failures are
`tests/test_verification_fixes.py`, repaired here. The other 14 also fail
locally on the PF1 head (14 failed, 1,077 passed, 13 skipped over their five
files). PF1 touches none of their files, so they are red on `main`. They are
reported, not repaired (D1):

| File | Failing | First assertion |
|---|---|---|
| `tests/test_guarded_clause_exports.py` | `test_existing_export_bytes_are_stable` | an export digest changed |
| `tests/test_ir3_pyrel_includes.py` | T3 rules modes (4 parameters), `test_T6_include_free_programs_are_byte_identical` | `(0, 0) == (3, 3)`; `duckdb-small-flat` |
| `tests/test_rf1_pin_harness.py` | `test_mutation_table_rows_of_their_own` | |
| `tests/test_rf4_peripheral.py` | `test_graph_targets`, `test_graph_predicate_is_live` (5) | a lazy import `gnd.extract.flatten_service` → `gnd.install`, line 25, outside the layer map |
| `tests/test_rf5_handler_pins.py` | `test_original_handler_bytes[install]` | the install handler's pinned bytes differ |

None is in the guard block, which is how they stayed red unnoticed: the same
cause as PR 247's.

## Review

Instrument: the review helper, one reviewer in a different tool (Codex,
`codex exec --sandbox read-only`, reasoning high), as plan D3 rules. **One
reviewer is one reviewer; this is not a panel.** Two rounds, the budget.

- **Round 1** (`notes/reviews/phase-PF1-r1/`, brief over `c1ecb8c1`):
  CHANGES_REQUESTED. F1 a walrus in a default argument, F2 `for`, `with`,
  `match` and `def` names, both missed by the guard; F3 a bare annotation
  after the import reported as a copy; F4 two more inline `18`s. F1–F3
  reproduced and fixed in `02c6bef1` with a case each; all six reproductions
  fail on the round-0 guard. F4 is completeness, deferred (open questions).
  The reviewer judged `c1ecb8c1` "functionally correct".
- **Round 2** (`notes/reviews/phase-PF1-r2/`, brief over `02c6bef1`):
  CHANGES_REQUESTED. Function and lambda parameters, type parameters, and
  one good alias excusing a renamed alias in the same import. All three
  reproduced and fixed in `1d0628c7` with cases that fail on the round-1
  guard.

**The round-2 repair carries no review opinion.** The budget is spent; under
the bounded convergence rules the next instrument is the tests, not a third
round. Both rounds' findings were reproduced before they were believed.
Both `review.md` files and logs were sanitized for local paths by the
helper, and round 2's `diff.patch` by the same replacement; each sanitized
`review.md` says so at its top.

## Refactoring review

None needed beyond the phase itself, argued from what it touched. The phase
is the refactor: three copies of a pin became imports of an existing home,
in the form `tests/test_public_built_inventory.py` already used. The guard
reads source with `ast`, which the repository already uses for source scans
(`tests/test_rf7_structure.py` and the layer map). No test helper module was
added, because nothing else needs the binding walk yet. Seen and deferred:
the inline counts of F4 (open questions).

## Implementation findings and deviations

From the spec's findings section: the baseline above; `tests/test_install.py`
called its copy "Duplicated deliberately", and the import keeps that intent
(an added file fails the home once) while removing the drift; an inline
literal is a copy a name guard cannot see (`c1ecb8c1`, outside the listed
homes); the first guard enumerated statement types, and two review rounds
showed that was the wrong axis.

## Open questions

| # | Question | Next owner |
|---|---|---|
| OQ1 | `tests/test_public_built_inventory.py` (`c1ecb8c1`) is outside spec §3's homes. Keep it, or drop the commit | the owner, before this pull request merges |
| OQ2 | Inline restatements of the skill count remain: `tests/test_development_scaffold.py:200` and `tests/test_marketplace_plugins.py:25` (`== 18`). No name guard can see them | the owner: a maintenance pass, or the close of this milestone |
| OQ3 | 14 tests in five files are red on `main` (table above), not inventory copies | the owner: a maintenance pass; `tests/test_rf4_peripheral.py` reports a layer-map violation in `src/` |

## Boundary -- what this result did NOT establish

- That no test restates the inventory: the guard sees bindings of three names,
  not inline literals (OQ2).
- That the round-2 repair is free of a further miss: it has no review.
- The red tests of OQ3: listed, not diagnosed beyond their first assertion.
- The baseline ran on beast-3's uv and Python, not the CI pin.
- No merge, release or publication. PF2 is not started.
