---
milestone: pyrel-agent-loop
station: phase-PL1
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL1
date: 2026-10-14
source_base: 814d5d6
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_pyrel_interpreter_env.py tests/test_ready_projects.py tests/test_pyrel_tutorial_experience.py tests/test_pyrel_proposal_check.py tests/test_documentation_tutorials.py tests/test_pyrel_learning_path.py tests/test_tutorial_output_blocks.py tests/test_pyrel_applications_install.py tests/test_expense_tutorial.py tests/test_bookrec_tutorial.py"
  exit: 0
  output: "230 passed, 7 deselected in 48.66s"
native_gate:
  command: "GND_TUTORIAL_PYREL_PYTHON=$PWD/tutorials/runtimes/.venv/bin/python uv run pytest -q -p no:cacheprovider -m pyrel_oracle tests/test_bookrec_pyrel_application.py tests/test_expense_pyrel_application.py tests/test_pyrel_proposal_check.py"
  exit: 0
  output: "60 passed, 21 deselected in 179.71s"
tutorials:
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group bookrec --lane pyrel", exit: 0, output: "59 tutorial blocks passed"}
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group expense --lane pyrel", exit: 0, output: "45 tutorial blocks passed"}
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel", exit: 0, output: "13 tutorial blocks passed"}
  - {command: "uv run python tools/run_tutorials.py --group bookrec; --group expense", exit: 0, output: "51 and 35 tutorial blocks passed"}
  - {command: "uv run --group docs zensical build --strict && uv run python tools/check_docs.py site", exit: 0, output: "No issues found; 7535 local links/assets/anchors checked"}
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL1-spec.md"}
  - {"path": ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL1-claude-review.md"}
---
# Phase PL1: readable commands and one-copy projects

Spec: [notes/phase-PL1-spec.md](notes/phase-PL1-spec.md), delegated approval
(auto=true) under the owner's default plan approval. Implemented and verified on
2026-10-14.

## What landed

- `src/gnd/export/applications.py`: `_interpreter()` resolves the PyRel
  interpreter from the argument or `GND_PYREL_PYTHON`; both entry points take
  `native_python=None`.
- Example CLIs: `--pyrel-python` optional with the same fallback and a usage
  error naming the variable; `--format` defaults to text under `--backend pyrel`.
- Launchers `bookrec/app.py` and `expense/project/app.py`; ready folder
  `expense/project/` with byte twins of the extension, contract, model and seed.
- `tools/run_tutorials.py`: pyrel-lane blocks receive `GND_PYREL_PYTHON`; the
  runner no longer puts the PyRel interpreter first on `PATH`, and it drops a
  host `GND_PYREL_PYTHON` from the block environment.
- Pages: every command on the three pages is `python <project>/app.py ...` or
  `gnd ...` with `--backend pyrel`; the Expense install loop is one copy; Set up
  exports `PATH` and `GND_PYREL_PYTHON` once.

Measured: codegen over the one-copy Expense project is idempotent (second run
"0 written, 1 skipped", contract preserved) and `gnd conformance` exits 0.

## Review

One reviewer is one reviewer: a single Claude subagent (same model family),
report retained verbatim in `notes/phase-PL1-claude-review.md`. Verdict:
revise. Findings and dispositions:

| # | Class | Finding | Disposition |
|---|---|---|---|
| F1 | blocking | `test_check_proposal_validation_order_is_pinned` red: marker string moved into `_interpreter()` | fixed: marker is now `_interpreter(`; the order pin still proves interpreter resolution precedes the first read |
| F2 | hardening | runner inherited a host `GND_PYREL_PYTHON` into offline blocks | fixed: popped with `PYTHONPATH`; reproduced red first with `GND_PYREL_PYTHON=/nonexistent/python` |
| F3 | completeness | checkout-twin test asserted nothing | fixed: compares the two launchers against `src/gnd/examples/...` by relative path |
| F4 | completeness | spec row "one oracle case uses the env var" not implemented | fixed: the `advisory` case in `tests/test_bookrec_pyrel_application.py` drops `--pyrel-python` and sets the variable |
| F5 | completeness | expense `--format text` under `gnd` untested; whitespace value reaches the seam and is refused cleanly | test added for the former; the latter recorded as intended behavior |
| F6 | hardening | unused `noqa` on both launchers | removed; ruff clean on every new file |

Pre-existing: `tests/test_rf7_structure.py::test_complete_routing_and_dirty_controls`
fails at `main` (`src/gnd/population_shape.py`), inherited from the previous
milestone's close record; not touched here.

## Refactoring review

None needed beyond what the phase touched: the two CLIs now share the same
argparse post-check pattern and the seam has one interpreter resolver; no
further duplication was created or found in the files this phase edited.

## Boundary

The reason text for a missing interpreter is prefixed by the exception type
(`RuntimeError: no PyRel interpreter: ...`), as every seam reason is. Pages
changed only in their commands; their prose is PL5. Block counts are unchanged
at 59 and 45. The `--format` default changes the pyrel-backend output of the
example CLIs for callers that omitted the flag; JSON stays available.

## Open questions

None new. PL-Q1 (`--format` default) is settled as (b) by this phase.
