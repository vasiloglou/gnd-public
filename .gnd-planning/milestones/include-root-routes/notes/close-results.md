# include-root-routes · close results

Measured 2026-11-21 at `90ac280c` (branch `claude/include-root-routes`, base
`main` at `260c4337`). **Superseded in part after the close review**: the
close record `005-milestone-close.md` carries the final gates, the repairs
and the final dispositions; the rows below are kept as the review read them. These are the results the close review reads beside
plan r5 (`notes/include-root-routes-plan.md`) and the delta
(`notes/close-delta.md`). This file is not the close record.

## Phases

| Phase | Record | Focused lane at its record | Review (one reviewer each, Codex read-only) |
|---|---|---|---|
| IR1 | `002-phase-IR1.md` | exit 0, 669 passed | 1 finding, fixed (`6867be3c`) |
| IR2 | `003-phase-IR2.md` | exit 0, 382 passed | 3 findings, fixed (`1311ae6d`) |
| IR3 | `004-phase-IR3.md` | exit 0, 388 passed | 1 finding, fixed (`6aacb928`) |

Each phase's corpus was committed red before its code: IR1 17 cases
(`40d3265b`, `1e419a88`), IR2 15 (`68e426ca`), IR3 29 (`1c5c0f66`).

## Exit gates at `90ac280c`

| Gate | Result |
|---|---|
| union of the three focused lanes (19 files) | `1158 passed, 81 deselected in 150.11s`, exit 0 |
| guard block, `tests/test_release_text.py`, `tests/test_gate_guard_list.py` | `715 passed, 2 deselected in 102.63s`, exit 0 |
| `uv run ruff check src tests tools` | `All checks passed!`, exit 0 |
| `uv run ruff check` | exit 1, known red: dev-tools scripts under `.claude/` and `.codex/`, unchanged by this milestone and red on `main` |
| `python3 scripts/components_index.py changed --base origin/main --strict` | `0 to fix, 0 warning(s), 12 to reread`, exit 0 |

The 81 deselected cases are the default lane filter's exclusions
(`pyrel_oracle` and the other opt-in lanes); none ran.

## Goal predicates

| Predicate (plan r5, Goal) | Evidence | Status |
|---|---|---|
| IR1: `gnd judgments check` accepts an include root, temporal or not, and judges the composed model | IR1 T1 (temporal root, exit 0), T2 (direct equals flat) | met |
| IR1: receipts bind the root's sha256; pins bind every include | T3, T4; pins are mandatory (`model/_includes.py:61-77`) | met |
| IR2: any include root can be written as a flat model and record by `gnd flatten` | IR2 T1 (temporal root), T2 (check parity) | met |
| IR3: `gnd export pyrel` in all three modes accepts an include root through its flat model | IR3 T1, T3, T4 | met; under `--rules` both interop roots then stop at the anchored constraint, as their flat models do (RP2 not merged) |
| IR3: the program records the record digest and every pin; a re-pinned include changes it | T4, T5 | met |
| every combination that stays unsupported refuses with a message naming it | IR1 T6, IR2 T3–T5 and T12, IR3 T2, T7 and F1 | met, with the `compose` encoding gap below |
| close: replies drafted for #217 and #214 | `notes/issue-replies.md` | drafted, not posted |
| close: panel-light close review | this review | pending |

## Open questions from the records, proposed dispositions

| Question | Raised in | Proposed |
|---|---|---|
| `gnd check` is superlinear in object-type count (`universe._denoting_types` → `resolve_reference_value_type` → `model_queries._supertype_parents`) | `002-phase-IR1.md`; IR1 spec i1 | carried: a new issue and a separate fix; owner to file |
| whole-repository ruff red in dev-tools-delivered scripts | `002-phase-IR1.md` | carried to the dev-tools source (or an exclusion in `pyproject.toml`, a repository policy change) |
| `compose` raises `UnicodeEncodeError` instead of `include:path` for an unencodable include path, on every route | `004-phase-IR3.md` | carried: a separate fix in `model/_includes.py:compose`, rule 1 |
| a flat model written outside the root's folder cannot bind its references | `003-phase-IR2.md` boundary | accepted residual; `gnd flatten` says so on stderr |
| the assertion-admission example copies the model alone and refuses include roots | `002-phase-IR1.md` boundary; plan H11 | carried to literature-host-interfaces LH3 |
| `gnd exp` session judgments keep refusing include roots | plan §7 | accepted residual, out of scope |
| IR2's `--out` folder rule (plan-gate open question) | `001-plan-gate.md` | closed by IR2-D2 (`003-phase-IR2.md`) |
| IR3-C3's single outcome (plan-gate open question) | `001-plan-gate.md` | closed by IR3-D5 (`004-phase-IR3.md`) |
