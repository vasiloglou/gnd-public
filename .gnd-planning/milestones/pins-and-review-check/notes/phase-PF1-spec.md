# Phase PF1 · one home for the packaged-skill inventory · spec r1

## 1. Status

**Draft r1, 2026-11-23, awaiting the plan gate and then its own owner gate.**
No test file changes before both.

## 2. Provenance

- Derives from [plan r1](pins-and-review-check-plan.md): Goal (PF1), R0.1,
  R0.3, §1 H1–H7, H12, H13, §2 PF1, §4 PF1-C1 to C5, §9 PF1 lane, §10 D1, D4,
  D5.
- Sources: [PR 247](https://github.com/vasiloglou/gnd-public/pull/247), "Not
  established".
- Code read at `7c4439dd` (`main`). No review has read these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| H1, H2, H3, H12 | the inventory is defined in four default-lane files | §6 "Imports"; T1 |
| H5, H12 | three files are missing from the guard block | §6 "Guard block"; T4 |
| H12 | 5 tests fail on `main` | §6 "Imports"; T3 |
| H13, D5 | the distribution-lane pin of a released wheel | §6 "The exception"; T2 |
| D1 | baseline run before any edit | §6 "Baseline"; record |
| PF1-C1 | names assigned only in `test_packaged_skills.py`, apart from D5's exception | T1 |
| PF1-C2 | the guard fails on a planted copy | T2 |
| PF1-C3 | guard block names the three files; `test_gate_guard_list.py` passes | T4 |
| PF1-C4 | no test is removed; all pass | T3 |
| PF1-C5 | red files from the baseline are listed | record |

## 4. The standing rules, bound to this phase

- **R0.1 One home per pin.** The three names live in
  `tests/test_packaged_skills.py`; T1 holds it.
- **R0.3 No check weakened.** Every `assert` that reads the names stays; only
  the definition moves. T3 compares test counts before and after.
- **General solutions (`AGENTS.md`).** The guard reads Python source with
  `ast`, not a regular expression, and it looks at the assigned name, not at
  the literal 71. A copy with another value or another shape (a `frozenset(...)`
  call, a set literal, an annotated assignment) is caught. T2 plants each.
- **Totality, caps, validation order, one walk, measurement.** The guard reads
  the repository's own test files, a bounded and trusted input; the rules on
  hostile input are inapplicable. One walk: one `ast` pass per file, checking
  all three names together.

## 5. Goal

`uv run pytest -q tests/test_inventory_pin_home.py tests/test_packaged_skills.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_gate_guard_list.py --tb=short`
exits 0, where `tests/test_verification_fixes.py` exits 1 today. The guard
block in `project.md` names the three files, and the guard block command
exits 0.

## 6. Design

### Baseline (D1), before any edit

Run the default lane once at the phase base on beast-3 (memory: scratch
commit, bundle, six shards, about ten minutes). Record every failing node id.
A file red because it copies the inventory is repaired here. Any other red
file is listed in the record and reported, not repaired.

### Imports

| File | Today | After |
|---|---|---|
| `tests/test_install.py` | `EXPECTED_SKILL_FILE_COUNT = 71` (`:51`), `EXPECTED_SKILL_NAMES = frozenset(...)` (`:56`) | `from test_packaged_skills import EXPECTED_SKILL_FILE_COUNT, EXPECTED_SKILL_NAMES` |
| `tests/test_doctor_uninstall.py` | the same two names (`:47`, `:52`) | the same import |
| `tests/test_verification_fixes.py` | `EXPECTED_SKILL_FILES` (70 files, `:17`), `EXPECTED_SKILL_FILE_COUNT = 70` (`:18`) | `from test_packaged_skills import EXPECTED_SKILL_FILE_COUNT, EXPECTED_SKILL_FILES` |

The import form is the one `tests/test_public_built_inventory.py:11` already
uses, so it resolves the same way under the repository's pytest
configuration. Before the edit the spec's implementer checks that each local
set equals the imported one apart from the AC1 file; a difference other than
that file stops the phase for a ruling.

### The guard: `tests/test_inventory_pin_home.py` (new, about 50 lines)

```python
HOME = "tests/test_packaged_skills.py"
NAMES = frozenset({"EXPECTED_SKILL_FILE_COUNT", "EXPECTED_SKILL_NAMES", "EXPECTED_SKILL_FILES"})
#: A pin of released bytes, not of the tree (plan D5).
EXCEPTIONS = {"tests/test_public_distribution_runtime.py": "pins a released wheel's inventory"}

def module_level_pins(source: str) -> set[str]:
    """Names in NAMES bound at module level by Assign, AnnAssign or AugAssign."""

def test_the_inventory_has_one_home() -> None: ...
def test_the_guard_sees_every_assignment_form() -> None: ...  # T2
```

`module_level_pins` walks `ast.parse(source).body` and reads every target of
`ast.Assign`, `ast.AnnAssign` and `ast.AugAssign`, including tuple targets.
An `AugAssign` in the home itself (`EXPECTED_SKILL_FILES |= {...}`,
`test_packaged_skills.py:49`) is allowed, because the home may build its own
value. An import is not an assignment.

### Guard block

`project.md`, both copies, "Structure and inventory guards, issue 171": the
one command line gains `tests/test_install.py tests/test_doctor_uninstall.py
tests/test_verification_fixes.py tests/test_inventory_pin_home.py`.
`tests/test_gate_guard_list.py` already accepts a growing block; its
`ISSUE_171_GUARDS` set does not change.

### The exception (D5)

`tests/test_public_distribution_runtime.py` keeps its 59. The guard names it
in `EXCEPTIONS` with the reason. An exception whose file no longer exists
fails the guard, so a stale exception cannot linger.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| PF1-D1 | Where the guard lives | (a) a new file; (b) a test in `test_packaged_skills.py`. Same exit codes; (a) keeps the home file's job to defining the inventory | (a) |
| PF1-D2 | Whether the guard also catches `EXPECTED_RELATIVE_LINK_COUNT` copies | (a) no: no copy exists in the default lane; (b) yes: wider, and `test_public_distribution_runtime.py:22` would need a second exception | (a) |

Plan D1 and D5 are ruled at the plan gate.

## 8. Tests

| ID | File, case | Expected |
|---|---|---|
| T1 | `test_inventory_pin_home.py::test_the_inventory_has_one_home` over the tree | passes; fails before the import change (it finds four files) |
| T2 | `test_the_guard_sees_every_assignment_form`: source strings with `X = 1`, `X: int = 1`, `X, Y = 1, 2`, `X |= {"a"}`, a nested `def` that assigns `X` (not module level), and `from test_packaged_skills import X` | the first four report X; the last two do not. A stale `EXCEPTIONS` path fails |
| T3 | `tests/test_install.py`, `tests/test_doctor_uninstall.py`, `tests/test_verification_fixes.py` | all pass; node counts equal before and after (H7: 174 over three files; 13 in the third) |
| T4 | `tests/test_gate_guard_list.py` and the guard block command | exit 0 |
| T5 | `uv run pytest -q -m distribution tests/test_public_built_inventory.py`, once, recorded | recorded; not a gate |

## 9. Out of scope for this phase

- The review-check calibration (PF2).
- Other duplicated constants in tests (PF1-D2).
- Any change under `src/`.

## 10. Size

About 60 test lines added, about 80 removed (two `frozenset` literals of 18
names and one of 70 files). Two lines in each copy of `project.md`.

## 11. Approval instrument

This prose.
