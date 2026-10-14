# Phase PL1 spec: readable commands and one-copy projects

## 1. Status

owner-decided (2026-10-14): delegated approval under the owner's default plan
approval ([`001-plan-gate.md`](../001-plan-gate.md)). Implementable.

## 2. Provenance

Derived from plan r1 ([`pyrel-agent-loop-plan.md`](pyrel-agent-loop-plan.md))
sections 2, 4 (PL1 row), 9 and 10 (PL-D2, PL-Q1). Carries A2 D1, D3, D5 from
`pyrel-applications`. No review round has run over these bytes.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Owner review: ugly commands | No interpreter variable, `cd`, `--pyrel-python` or `--format` in page commands | §6.1–6.4, PL1-C4 |
| Owner review: file-copy loops | One copy per project | §6.3, PL1-C3 |
| Plan PL-R1 | Reader shell and runner run the same text | §6.4 |
| Plan §2 seam contract | `native_python=None` fallback and reasons | §6.1 |
| Plan PL-Q1 | `--format` default | §7 D1 |
| A2 D1 | Queries use only the public seam | unchanged; `native_query.py` untouched |
| A2 D3 | Every executed command shows output | page edits keep `output=stdout` blocks |
| Plan §9 PL1 | Affected tests updated | §8 |
| Standing rule 1 (totality) | Env var value validated like a path argument | §6.1 |

## 4. Standing rules, bound

1. Totality: `_interpreter()` treats the env value as untrusted text; empty,
   relative or non-file values produce a result reason, never a traceback.
2. Bounds: no new input-proportional work.
3. Validation order: interpreter resolution happens before any file read, as
   today; the CLI usage error fires before `execute_application` is called.
4. One walk: one helper serves both seam entry points; both CLIs call the same
   argparse post-check pattern.
5. One home: the env var name is documented in `docs/pyrel-apps.md` Set up and
   referenced elsewhere by link.
6. Measurement: the `--format` default is settled by the two `pyrel_oracle`
   tests going red and being updated, not by argument.

## 5. Goal

`python bookrec-native/app.py recommend --user ada --model ... --input ... --output ada.json --backend pyrel`
exits 0 and prints the text verdict when `GND_PYREL_PYTHON` names the pinned
interpreter; exits 2 with the usage error when neither flag nor variable is
set; both tutorial groups exit 0 in both lanes with the pages' commands
rewritten to this shape and their file-copy loops replaced.

## 6. Design

### 6.1 `src/gnd/export/applications.py` (+25 lines)

```python
INTERPRETER_ENV = 'GND_PYREL_PYTHON'

def _interpreter(native_python):
    """Resolve the PyRel interpreter: explicit argument, else GND_PYREL_PYTHON."""
    if native_python is None:
        native_python = os.environ.get(INTERPRETER_ENV, '')
        if not native_python:
            raise RuntimeError('no PyRel interpreter: pass native_python or set GND_PYREL_PYTHON')
    interpreter = Path(native_python)
    if not interpreter.is_absolute() or not interpreter.is_file():
        raise RuntimeError('explicit native interpreter is unavailable')
    return interpreter
```

`execute_application(..., *, native_python=None, ...)` and
`check_proposal(..., *, native_python=None, ...)` call it where they build
`interpreter` today (lines 194 and 269). Both `RuntimeError`s fall into the
existing `except` that sets `exit_code 70` and `reason`.

### 6.2 Example CLIs (+12 lines each)

`src/gnd/examples/bookrec/extension/bookrec/cli.py` and
`src/gnd/examples/expense/extension.py`:

- `--pyrel-python` `type=Path, default=None`; `--format` `default=None`.
- After parsing: `fmt = args.format or ('text' if args.backend == 'pyrel' else 'json')`;
  `if fmt == 'text' and args.backend != 'pyrel': parser.error("--format text requires --backend pyrel")`.
- `if args.backend == 'pyrel' and args.pyrel_python is None and not os.environ.get('GND_PYREL_PYTHON'): parser.error("--backend pyrel needs the PyRel interpreter: pass --pyrel-python PATH or export GND_PYREL_PYTHON=PATH")`.
- Pass `native_python=args.pyrel_python` (may be `None`).

### 6.3 Launchers and the ready folder

- `src/gnd/examples/bookrec/app.py` (12 lines): inserts `extension/` beside
  itself at `sys.path[0]`, `from bookrec.cli import main`, `raise SystemExit(main())`.
- `src/gnd/examples/expense/project/`: `app.py` (same shape, inserts its own
  directory, imports `cli.expense_cli`), `architecture.contract.yaml`
  (copy of the top-level file with `--pyrel-python` kept in `flags`),
  `cli/__init__.py` (empty), `cli/expense_cli.py`, `cli/reporting.py`,
  `cli/native_query.py` (byte copies of `extension.py`, `reporting.py`,
  `native_query.py`). Top-level files stay.
- Chapter 4 block order: `gnd codegen expense-native-demo/model.orm.json --out expense-native`
  then `shutil.copytree("expense-native-demo/project", "expense-native", dirs_exist_ok=True)`.
  The copy overwrites codegen's default contract; codegen records contracts as
  create-once extension paths, so a later `gnd codegen` leaves them alone.
  Spec measurement: run `gnd codegen` a second time over the result and record
  exit 0.
- BookRec stays `copytree(examples/bookrec, "bookrec-native")`; its `app.py`
  arrives with the copy.

### 6.4 `tools/run_tutorials.py` (±6 lines)

At line 150: `block_env = dict(env)`; for `block_lane == 'pyrel'`:
`block_env['GND_PYREL_PYTHON'] = str(block_python.absolute())`. Remove the
`PATH` prepend of the PyRel directory. `block_python` is still used for
`python`-language blocks in the pyrel lane (they run under the PyRel
interpreter, as today). The receipt field `block_python` is unchanged.

### 6.5 Page command edits (PL1 only; content rewrite is PL5)

`docs/bookrec/07-native.md` and `docs/expense/04-native.md`: every
`(cd ... && "$GND_TUTORIAL_GND_PYTHON" -m ... --pyrel-python ... --format text)`
becomes `python <project>/app.py ...` with `--backend pyrel`; relative
`--model`/`--input`/`--output` paths adjusted to the run directory;
`"$GND_TUTORIAL_PYREL_PYTHON" -c ...` readiness check becomes
`"$GND_PYREL_PYTHON" -c ...`. Expense's install loop is replaced per §6.3.
`docs/pyrel-apps.md` Set up: `export PATH="$PWD/gnd-env/bin:$PATH"` and
`export GND_PYREL_PYTHON="$PWD/pyrel-env/.venv/bin/python"` replace the two
`GND_TUTORIAL_*` exports. Outputs re-measured in both lanes.

## 7. Decisions

| # | Question | Readings | Ruling |
|---|---|---|---|
| D1 | `--format` default | (a) keep `json`; (b) `text` under pyrel, `json` otherwise. Cost of (b): two tests change; readers lose one flag | (b), owner default approval 2026-10-14 |
| D2 | `--backend` default | (a) stay explicit; (b) default pyrel when env set. Cost of (b): chapters 2–6 silently change backend for a reader who exported the variable | (a) |
| D3 | `--model`/`--input` defaults from the project folder | (a) explicit; (b) default. (b) hides the lesson's two inputs | (a) |

## 8. Tests

| File | Case | Expected |
|---|---|---|
| `tests/test_pyrel_interpreter_env.py` | seam `native_python=None`, env unset → `exit_code 70`, reason `no PyRel interpreter` | pass |
| same | env set to relative path → reason `explicit native interpreter is unavailable` | pass |
| same | env set to a symlink of `sys.executable`, `check_proposal` reaches the child (fails later on version, not on interpreter) | reason not about interpreter |
| same | bookrec CLI `--backend pyrel` without flag or env → exit 2, usage text | pass |
| same | expense CLI same | pass |
| same | `--format` omitted: text under pyrel (stdout starts `Proposed`/`Report`/`Policy check`), json under gnd | pass |
| `tests/test_ready_projects.py` | `project/cli/*.py` and contract byte-equal to top-level sources; `app.py` launchers import | pass |
| `tests/test_pyrel_tutorial_experience.py::test_native_block_receives_explicit_base_python` | pyrel block sees `GND_PYREL_PYTHON == native`, `PATH` starts with the GND interpreter dir | pass |
| `tests/test_bookrec_pyrel_application.py`, `tests/test_expense_pyrel_application.py` | add `--format json` (one case drops `--pyrel-python` and sets the env) | pass under `pyrel_oracle` |
| `tests/test_rf7_structure.py` | allowlist `bookrec/app.py`, `expense/project/app.py`, `expense/project/cli/expense_cli.py` | pass |
| `tests/test_pyrel_applications_install.py` | resource list gains `gnd/examples/expense/project/cli/expense_cli.py` | pass |
| runner | `--group bookrec`, `--group expense`, both lanes; `--group runtime-pyrel --lane pyrel` | exit 0 |

## 9. Out of scope for this phase

Page prose, section structure, new sections, rules in PyRel, stand-ins,
recordings, block-count pins (provisional only), nav titles.

## 10. Size

Estimate: ~120 source lines, ~150 test lines, ~60 page lines changed.

## 11. Approval instrument

This prose, plus the test list in §8 authored red before the seam change.

## Owner gate

Delegated approval (auto=true), 2026-10-14, under the owner's default plan
approval recorded in [001-plan-gate.md](../001-plan-gate.md). Instrument: this
prose with the §8 test list authored red first. No spec panel. Spec SHA-256
before this section: ef98f1f177af4067389204afd8b1564a225c58966c2f250c427bc71e19c28680. Rulings D1–D3 as marked in §7.

## Implementation findings

- F1 The seam's exception handler prefixes `reason` with the exception type, so
  the reason reads `RuntimeError: no PyRel interpreter: ...`. Tests assert the
  suffix; the page's troubleshooting row names the message, not the prefix.
- F2 Expense's top-level `--help` lists only subcommands; the launcher test asks
  for `report --help`.
- F3 The ready folder also carries `model.orm.json` and `seed.population.json`
  twins so every chapter command points at one project folder. Added to the
  byte-twin test; codegen over the result stays idempotent (second run: 0
  written, 1 skipped; contract preserved) and `gnd conformance` exits 0.
- F4 `python` resolves in a uv virtual environment's `bin`, so page blocks can
  use it once the GND environment is first on `PATH`; the runner already puts
  the base interpreter's directory first.
- F5 Measured: BookRec 59 blocks and Expense 45 blocks pass in both lanes with
  the rewritten commands; `runtime-pyrel` (13 blocks) still passes because
  those pages name the interpreter explicitly.
