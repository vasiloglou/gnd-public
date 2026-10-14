# Phase PL1 independent review

- Reviewer: one Claude subagent (same model family as the author); read-only
  except this file.
- Date: 2026-10-14
- HEAD: `814d5d6ccdc2bf80692561249b9a4d8d39bb21a0` (branch `codex/pyrel-agent-loop`)
- Reviewed bytes: the uncommitted working tree against HEAD, scoped to the PL1
  files named in the review task. `git diff HEAD | shasum -a 256` was taken
  three times because the author kept editing during the review:
  - `bec5744e5f37589bc2d8a2fd1547543259889a90c14f8ce64667d007372215d9` at start
    (14 files, 158+/117-);
  - `65cca4dbf6d9e01e87473840493acb92afb175987ccd9d637b4795da48bdf9b5` after
    `tests/test_rf7_structure.py` gained two `rules_in_pyrel.py` allowlist
    lines (PL2 scope);
  - `d0880373596e0263d1d4d4a9cd922c6af9c0b9f8c2424ea9a17f567569e1926f` at
    write time (163+/117-). Untracked PL2/PL3 files (`rules_in_pyrel.py`,
    `stand_in_agent.py`, `tests/test_rules_in_pyrel.py`,
    `tests/test_pyrel_stand_in_sessions.py`, `docs/assets/applications/*.txt`,
    PL2/PL3 specs) appeared mid-review and are NOT covered here.
- Spec: `notes/phase-PL1-spec.md`; plan sections 0, 2, 6 read.

## Measurements

| Check | Result |
|---|---|
| Default lane, affected files (13 test modules) | 213 passed, 2 failed: F1 (new) and `test_rf7_structure.py::test_complete_routing_and_dirty_controls` (pre-existing, fails at HEAD on `src/gnd/population_shape.py`, unrelated to PL1) |
| `pyrel_oracle` lane (`test_bookrec_pyrel_application.py`, `test_expense_pyrel_application.py`, `test_pyrel_proposal_check.py`, `test_pyrel_native_seam.py`) with `tutorials/runtimes/.venv` | 75 passed |
| `tools/run_tutorials.py --group bookrec` offline / pyrel | 51 / 59 blocks, exit 0 |
| `--group expense` offline / pyrel | 35 / 45 blocks, exit 0 |
| `--group runtime-pyrel --lane pyrel` | 13 blocks, exit 0 |
| Chapter 4 flow in a scratch dir: `gnd codegen` → `copytree(project, expense-native, dirs_exist_ok=True)` → `gnd conformance` → `gnd codegen` again → generated smoke test → `app.py report` (gnd backend) | 0 / copied / 0 (integrity 0, currency 0) / 0 with "preserved authored extension architecture.contract.yaml" / 3 passed / 0 |
| `ruff check` over the changed and new source/test files | 2 errors (F6) |

## Findings

### F1 — `test_check_proposal_validation_order_is_pinned` goes red (blocking, high)

`tests/test_pyrel_proposal_check.py:62-69` pins the order of markers inside
`inspect.getsource(applications.check_proposal)`; one marker is the literal
`'explicit native interpreter'`. The diff moves that string out of
`check_proposal` into `_interpreter()` (`src/gnd/export/applications.py:99-113`),
so `source.index(...)` raises.

Scenario: any default `uv run pytest` run → one failure in the default gate.
Reproduced:

```
uv run pytest -q tests/test_pyrel_proposal_check.py::test_check_proposal_validation_order_is_pinned
E   ValueError: substring not found     (positions = [source.index(marker) ...])
```

Passes at HEAD (verified with `git stash`). Spec §8 does not list this test,
so the "authored red first" instrument missed it. The pin exists to enforce
standing rule 3 (interpreter resolution before any `_capture`); the fix is to
replace the marker with `_interpreter(` (keeps the order assertion meaningful)
rather than delete the row. Class: blocking (red default gate).

### F2 — Runner inherits a host `GND_PYREL_PYTHON`; new test fails in a reader-shaped shell (hardening, medium)

`tools/run_tutorials.py:126-134` builds `env = os.environ.copy()` and pops
`PYTHONPATH`, `PYTHONHOME`, `PYTEST_*`, but not `GND_PYREL_PYTHON`. Lines
150-153 set the variable only for `block_lane == 'pyrel'`; offline blocks
therefore see whatever the developer's shell exported. `docs/pyrel-apps.md`
Set up now instructs exactly that export.

Scenario: developer has followed Set up (or has `GND_PYREL_PYTHON` in their
profile) and runs the default suite → the new assertion in
`tests/test_pyrel_tutorial_experience.py:93` (`assert "GND_PYREL_PYTHON" not in
os.environ` in an offline block) fails. Reproduced:

```
GND_PYREL_PYTHON=/nonexistent/python uv run pytest -q \
  tests/test_pyrel_tutorial_experience.py::test_native_block_receives_explicit_base_python
→ AssertionError at run_pages(...) == 2  (block 2 exited 1)
```

Product consequence today is nil (no offline block consumes the variable),
but PL-R1 says the runner "supplies `GND_PYREL_PYTHON`"; it should also be the
only supplier. Popping it in the same loop as `PYTHONPATH` makes the test
deterministic and the lane semantics exact. Class: hardening.

### F3 — `test_source_twins_in_the_checkout_match_the_installed_copies` asserts nothing (completeness, low)

`tests/test_ready_projects.py:49-55`: `installed.relative_to(installed.parents[3])`
assumes both launchers sit at the same depth. For `bookrec/app.py`,
`parents[3]` is `src`, the computed source equals `installed` and the branch is
skipped; for `expense/project/app.py`, `parents[3]` is `gnd`, the computed path
is `src/examples/expense/project/app.py`, which does not exist, so the branch is
skipped. Verified with a one-line Python probe (exists: False / same object:
True). The test passes vacuously in every install mode. Fix the depth with
`files('gnd')` as the anchor, or drop the test.

### F4 — Spec §8 oracle row not implemented (completeness, low)

Spec §8 says the two `pyrel_oracle` tests "add `--format json` (one case drops
`--pyrel-python` and sets the env)". Both files
(`tests/test_bookrec_pyrel_application.py:26`,
`tests/test_expense_pyrel_application.py:33`) keep `--pyrel-python` in every
case. `test_variable_reaches_the_native_child` uses `sys.executable`, so the
env → real PyRel → accepted verdict path is exercised only by the runner pages
(it passed there: 8 + 10 pyrel blocks). No pytest would fail if the env
fallback stopped reaching a real interpreter; the runner would. Record the
deviation or add the one case.

### F5 — Branch table gaps and the whitespace edge (completeness, low)

Branches walked for `_interpreter` (None+unset, None+empty, None+valid,
None+relative, None+missing, explicit+valid, explicit+invalid, explicit wins
over env) all have a test that fails if the branch is wrong. CLI gaps:

- expense `--format text` with `--backend gnd` (exit 2) is untested; only the
  bookrec twin is (`test_pyrel_interpreter_env.py:118-120`).
- expense `--format json` under pyrel is covered only in the `pyrel_oracle`
  lane.
- `GND_PYREL_PYTHON=" "` passes the CLI pre-check (`not os.environ.get(...)` is
  False for whitespace) and reaches the seam: probe gives exit 70,
  `Policy check: NOT RUN (RuntimeError: explicit native interpreter is
  unavailable)`, no traceback, no file read. Same for a directory (`/tmp`), a
  relative path, and `--pyrel-python ""`. This satisfies the totality rule;
  the usage exit 2 is reserved for the truly unset case. Acceptable; noted so
  nobody later "fixes" it into a crash.

### F6 — ruff RUF100 on both launchers (hardening, low)

`src/gnd/examples/bookrec/app.py:13` and
`src/gnd/examples/expense/project/app.py:13` carry `# noqa: E402`; E402 is not
enabled in this project's ruff config, so `uv run ruff check` reports two
`RUF100 Unused noqa directive` errors on new files. Remove the directives.

### Notes (not findings against PL1)

- `tests/test_rf7_structure.py::test_complete_routing_and_dirty_controls` fails
  at HEAD on `src/gnd/population_shape.py`; not introduced here.
- Untracked, out-of-scope paths sit in the tree: `.agents/skills/`,
  `.claude/launch.json`, `.playwright-mcp/`,
  `.gnd-planning/milestones/pyrel-applications/evidence/PA6/installed-artifacts.zip`
  (4 MB). None are PL1 bytes; none should ride in the PL1 commit.
- `docs/development/documentation.md:46-47` correctly states that a `python`
  fence in the pyrel lane runs under the PyRel interpreter. That is a latent
  reader/runner inequivalence (PL-R1) for `python` fences marked `lane=pyrel`,
  but today all 18 such fences in the two app pages are `sh`, and
  `docs/runtimes/pyrel.md`'s python fences only read JSON. Content work (PL5)
  should keep it that way.

## Checked and found sound

1. Callers: every call to `execute_application`/`check_proposal` in `src/`
   and `tests/` passes `native_python` by keyword or omits it;
   `test_pyrel_application_guards.py` checks only signature membership.
2. Child boundary: `_child` allowlist unchanged (`PATH`, `LANG`, `LC_*`,
   `TMPDIR`, `TEMP`, `TMP`, `SystemRoot`); `GND_PYREL_PYTHON` is read nowhere
   except the two CLIs and `_interpreter` (grep over `src/`, `tools/`).
3. `--format` default: every `-m bookrec.cli` / `-m cli.expense_cli` consumer
   in docs, tests, tools uses the gnd backend (json unchanged). The only
   pyrel-backend JSON consumers are the two oracle tests, now passing
   `--format json`; `test_bookrec_cli_proposal_text_output` passes
   `--format text` explicitly. No `.github` consumer.
4. Ready folder: `project/architecture.contract.yaml` is byte-identical to the
   top-level contract; smoke rows run as `[sys.executable, -c, SHIM,
   "cli.expense_cli", ...]` with `cwd=project root` (`src/gnd/archsmoke.py:323-325`),
   which the `cli/` layout satisfies. Chapter 4 reproduction above: conformance
   0, second codegen 0 and idempotent, generated smoke test green.
5. Validation order: in both entry points `_interpreter()` runs after the
   output-exists check and before the first `_capture`; the CLI usage error
   fires after argparse and before `execute_application`, with no file read.
6. Runner: all 8 `lane=pyrel` blocks in `docs/runtimes/pyrel.md` name
   `"${GND_TUTORIAL_PYREL_PYTHON:?...}"`; no page relied on bare `python`
   being PyRel. `test_native_block_receives_explicit_base_python` still asserts
   `sys.executable == native` for a python fence, `PATH[0]` is the GND
   interpreter dir, and `GND_PYREL_PYTHON == native`; it would fail if the
   PATH prepend returned or the export were dropped.
7. Docs: no `GND_TUTORIAL_`, `(cd `, `--format text` or `--pyrel-python` in
   any command of the three pages (the troubleshooting rows mention
   `--pyrel-python` only as the alternative to the export). Set up exports
   `PATH` on the line before the first bare `python`. The
   `documentation.md` paragraph matches `run_tutorials.py:150-153`.
8. Wheel: `uv_build` packages everything under `src/gnd`;
   `tools/accept_pyrel_applications_install.py:35-38` rglobs
   `examples/bookrec` and `examples/expense`, so the new files become required
   automatically; `test_candidate_resources_match_source` passes; the ready
   folder adds 44 KB against the 12 MiB cap.

## Verdict

**Revise.** One blocking item: F1 turns the default gate red and is a
one-line marker update (`'explicit native interpreter'` → `'_interpreter('`)
that the spec's §8 list should have carried. F2 is a hardening change of
similar size that removes a reader-shell false failure. F3–F6 are completeness
and lint items that can land in the same repair round. Product behavior,
pages, both lanes and the oracle lane are otherwise verified green.
