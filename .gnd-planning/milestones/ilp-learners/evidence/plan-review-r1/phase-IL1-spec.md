# IL1 — Learner registry and a real Popper run

## 1. Status

**Draft r1, awaiting plan approval and then this phase's owner gate.** Nothing
is implemented, installed or run. IL1-D3 (the install commands) must be ruled
before any install.

## 2. Provenance

- Plan: [ilp-learners-plan.md](ilp-learners-plan.md) r1, §2 "The learner
  registry", §4 IL1. The plan is a draft with no review opinion and no approval.
- Inherited: IK5 spec (`../../induced-knowledge/notes/phase-IK5-spec.md`) §6
  and IK5-D12, IK5-D13; record `../../induced-knowledge/007-phase-IK5.md`;
  close record `../../induced-knowledge/012-milestone-close.md` (rows IK5-Q5,
  IK5-Q2, IK6 join space).
- Owner answers recorded in the plan §1 (o), 2026-10-27: four adapters; one
  live run per adapter, Popper included.
- Source inspected at `63f7f1f`: `src/gnd/export/ilp_service.py`
  (`LEARNER`, `_prepare`, `_read_clauses`), `src/gnd/export/ilp_popper.py`
  (`render`, `_unquote`, `parse_program`), `src/gnd/export/ilp.py`
  (`export_tree`), `pyproject.toml` markers.

## 3. Obligations — inline harvest

| Obligation | Source | Discharged in |
|---|---|---|
| IL1-C1: one registry, no learner-name branch, IK5/IK6/RF1 goldens byte-identical | plan §4 | §6 registry; T1, T2 |
| IL1-C2: unknown target exits 64; learner mismatch exits 3 | plan §4 | §6 CLI; T3 |
| IL1-C3: SWI octal escapes; malformed escape exits 3 with line and column | plan §4; IK5-Q2 | §6 parser; T4 |
| IL1-C4: one recorded live Popper run over the IK6 refunds export | plan §4; IK5-Q5; D2 (o) | §6 live run; T6 (live) |
| IL1-C5: a joining clause imports and re-checks | plan §4; 012 "IK6 join space" | T5 |
| IK2 residual: does real learner output fit the induction block without loss | IK2 spec §15 via IK5 spec §3 | §6 live run, record question 3 |
| IL-R1: no learner is a dependency | plan §0 | T7 |
| IL-R2: live runs are scratch evidence, `live` marker | plan §0 | §6 live run; T6 |
| IL-R5: licence recorded | plan §0 | §6 live run, record |
| IL-R7: IK5 wires and goldens unchanged | plan §0 | T1, T2 |
| IK5-D12 (o): no GND command runs a learner | IK5 spec §7 | kept unless plan D3 rules (b) |

## 4. Standing rules bound to IL1

| Rule | Binding |
|---|---|
| 1 Totality | The changed loader is the Popper program parser's quoted-atom reader. Octal escapes are read with a bounded digit count; every malformed form is exit 3, never a traceback (T4 hostile cases). The registry adds no loader. |
| 2 Algorithm bound | No new work proportional to input; `_unquote` stays linear in the token. The live run is bounded by `run_bounded_process` limits fixed in §6. |
| 3 Validation order | Unchanged: the IK5 import order. The registry lookup replaces the `target == "popper"` test at the same point, pinned by the existing source-order assertions. |
| 4 One walk | One registry consulted by export, clause reading and learner binding; no per-learner branch remains (T2 source scan). |
| 5 One home | `docs/reference/ilp-bridge.md` stays the normative home; the registry description is added there only. |
| 6 Measurement | Golden bytes decide C1; the live run is recorded as evidence and decides nothing about a gate. |

## 5. Goal

`gnd export ilp --target popper` and `gnd import ilp-rules --target
{popper,neutral}` exit and write exactly as at `63f7f1f` on every IK5 and IK6
fixture, now through one registry. The Popper parser accepts SWI octal escapes.
A real Popper run over the IK6 refunds export is recorded with its versions, its
raw output and the import's exit and report.

## 6. Design

### Registry (`src/gnd/export/ilp_learners.py`, new, ~60 lines)

```python
@dataclass(frozen=True)
class Learner:
    target: str                      # the --target spelling
    learner: str | None              # required run-record learner.name; None for "neutral"
    method: str                      # IK2 method token: f"ilp-{target}"
    render: Callable[[dict[str, Any]], dict[str, bytes]] | None
    parse: Callable[[str], dict[str, Any]] | None   # None: the input is gnd-ilp-clauses/1 JSON
    contract: Literal["labelled-clauses"]

LEARNERS: Mapping[str, Learner]      # "popper", "neutral"; sorted by target
EXPORT_TARGETS: tuple[str, ...]      # targets with render is not None
IMPORT_TARGETS: tuple[str, ...]      # every target
def learner(target: str) -> Learner  # KeyError is an internal error (argparse already refused)
```

- `ilp_service.LEARNER` is removed. At `63f7f1f` no module or test outside
  `ilp_service.py` names it (checked by `grep -rn "LEARNER\b" src tests tools`),
  and it is not in `ilp_service.__all__`.
- `_prepare` calls `learner(target).render`; `_read_clauses` calls
  `learner(target).parse` and otherwise reads JSON; `method` comes from the
  entry.
- The CLI `choices=` for both commands come from `EXPORT_TARGETS` and
  `IMPORT_TARGETS`. Help text and `--help` goldens are unchanged because the
  sets are unchanged.
- Layer map: `gnd.export.ilp_learners` in the `export` lane.

### Octal escapes (`ilp_popper._unquote`, ~10 lines)

SWI writes a code point as `\` + 1–7 octal digits + `\`. The reader accepts
exactly that form after the existing `x` hex form, with the same Unicode-scalar
check. A missing closing `\`, more than 7 digits, or a non-scalar value is exit
3 `unparsable: line L, column C: …`.

### Live run (`evidence/IL1/run_popper.py`, evidence only)

- **Environment:** a scratch directory outside the repository, holding a
  virtual environment with Popper and the system tools it needs (SWI-Prolog,
  clingo). Exact install commands and versions: IL1-D3.
- **Steps:** `gnd export ilp` over the IK6 refunds model and manifest →
  Popper on `popper/` under `run_bounded_process` (wall-clock limit IL1-D4) →
  the printed program saved verbatim → a `gnd-ilp-run/1` run record written by
  the script from Popper's output, with `coverage` computed by evaluating the
  program in SWI over `bk.pl` (the learner's claim, which GND then checks) →
  `gnd import ilp-rules --target popper`.
- **Retained:** the program, the run record, the import report, tool versions,
  licence (IL-R5), and the script's exit. Relative paths only.
- **Record questions:** (1) does Popper accept the rendering; (2) does the
  output parse and import, or which named refusal; (3) does every learned clause
  fit the induction block without loss (the IK2 residual).
- **A failure is a result.** If Popper rejects the rendering or the import
  refuses, the record says why. A fix in the adapter (rendering or parser) is
  in scope, with a test, under IK-R12 if it moves a bound. A fix outside the
  adapter is carried.
- **Test:** `tests/test_ilp_live.py`, marked `live`, skipped by name when
  Popper is absent; never in the default gate.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IL1-D1 | Approval instrument | **Corpus-first:** escape cases and registry-equivalence goldens written first. **Prose:** this spec's tables; the goldens already exist from IK5/IK6 | prose, plus the T4 escape corpus |
| IL1-D2 | Keep `ilp_service.LEARNER` | **Remove:** it has no outside user and is not exported. **Alias** in the shim inventory: protects an unseen external import at the cost of a shim row | remove |
| IL1-D3 | Install commands for the live run | Named at this gate before any install, e.g. a scratch `uv venv` with `pip install popper-ilp` at a pinned version plus SWI-Prolog and clingo from a package manager; the owner rules the exact list | **open (owner)** |
| IL1-D4 | Live-run limits | wall clock 600 s, output cap 16 MiB, fixed before the run (IK-R12) | as stated |
| IL1-D5 | Base and branch | `claude/il1-learner-registry` from B = main at the gate | named at the gate |

## 8. Tests

| ID | File | Case | Expected |
|---|---|---|---|
| T1 | `tests/test_ilp_bridge.py` (existing) | the whole IK5 corpus | unchanged pass |
| T1b | `tests/test_ik6_walk.py`, RF1 CLI golden tests (existing) | IK6 walk; `export`/`import` CLI goldens | unchanged pass, byte-identical |
| T2 | `tests/test_ilp_learners.py` (new) | registry contents; `ilp_service.py` source has no `"popper"` literal outside the registry import | pass |
| T3 | same | `--target bogus` on export and import | exit 64; a run record naming another learner | exit 3 `learner-mismatch` |
| T4 | same | `'\001\'`, `'\101\'`, `'\7\'`, `'\12345670\'` (8 digits), `'\101'` (unclosed), `'\4000000\'` (beyond Unicode), `'\154000\'` (surrogate range) | the first three parse; the rest exit 3 `unparsable` with line and column |
| T5 | same | a clause joining two fact types through a shared variable over the IK6 refunds fixture | exit 0, a valid proposal |
| T6 | `tests/test_ilp_live.py` (new, `live`) | the live run | evidence only |
| T7 | same as T2 | `pyproject.toml` dependencies and optional groups name no learner (`popper`, `ilasp`, `fastlas`, `clingo`, `swipl`, `amie`, `imodels`, `corels`) | pass |

Gate command, exact file list fixed at execution:
`uv run pytest -q -p no:randomly tests/test_ilp_bridge.py tests/test_ilp_learners.py <IK6 walk and RF1 CLI golden files> <layer and RF5 controls>`.

## 9. Out of scope for this phase

- every adapter other than Popper and `neutral`;
- a GND command that runs a learner (plan D3);
- reference-bearing exports (plan D7);
- changes to any wire format or the fragment.

## 10. Size

Estimate: ~80 source lines, ~150 test lines, one evidence script of ~120 lines.

## 11. Approval instrument

Prose, with the T4 escape cases written before the parser change (IL1-D1).
