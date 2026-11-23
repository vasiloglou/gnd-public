# reviewed-vocabulary-growth · close results

Measured 2026-11-23 on `main` at `f7fad6a1`, which holds pull request 239
(VG1, `7952ee9e`) and pull request 240 (VG2–VG5, `8fea6da5`). These are the
results the close review reads beside plan r5
(`notes/reviewed-vocabulary-growth-plan.md`) and the delta
(`notes/close-delta.md`). This file is not the close record.

## Phases

| Phase | Issue | Record | Focused lane at its record | Review (one reviewer each, Codex read-only) |
|---|---|---|---|---|
| VG1 | 221 | `002-phase-VG1.md` | 413 passed, laptop and beast-3 | 2 findings, fixed (`7e235d4a`) |
| VG3 | 222 | `003-phase-VG3.md` | 334 passed | 2 findings, fixed (`01b76996`) |
| VG2 | 218 | `004-phase-VG2.md` | 435 passed | 4 points: 2 fixed (`53280cba`), 2 overclaims in the brief corrected |
| VG4 | 222 | `005-phase-VG4.md` | 437 passed | 1 finding, fixed (`18411c92`) |
| VG5 | all | `006-phase-VG5.md` | 49 passed | 2 findings, fixed (`0fc30381`) |

VG3 ran before VG2: VG2, VG4 and VG5 change `evolve/service.py` or
`unattended-growth.md`, and the roadmap placed GO1 of growth-round-outcomes
between VG1 and them (plan §3). VG3 changes neither file. Each spec was
approved by delegated ruling under the owner's
`process-milestone reviewed-vocabulary-growth auto` of 2026-11-23.

## Exit gates on `main` at `f7fad6a1`

| Gate | Result |
|---|---|
| union of the five focused lanes and the files the phases added to them (26 files) | `1365 passed in 332.67s`, exit 0 |
| guard block, `tests/test_release_text.py`, `tests/test_gate_guard_list.py` | `715 passed, 2 deselected in 167.68s`, exit 0 |
| `uv run ruff check src tests tools` | `All checks passed!`, exit 0 |
| `uv run ruff check` | `All checks passed!`, exit 0 (red when the plan was written, plan H27) |
| `python3 scripts/components_index.py changed --base origin/main --strict` | `0 file(s) differ; 0 to fix`, exit 0 |
| `tests/test_ir3_pyrel_includes.py` | `5 failed, 30 passed`: known red, red on `main` at `1f403b07` before this milestone (RP3's `EXACT_FLOAT` line is absent from IR3's goldens); a separate fix is proposed to the owner |

## Goal predicates

| Predicate (plan r5) | Evidence | Status |
|---|---|---|
| VG1: the supertype map is built a number of times independent of the model's size | VG1 T9: 48 builds at 300 and 600 extra value types (184,876 at 300 before) | met |
| VG1: doubling 1,000 to 2,000 extra types costs at most 3 times, four shapes | VG1 T11; beast-3 sweep 2.08–2.19 | met |
| VG1: 1,000 extra object types check in under 10 s, each shape | VG1 T3–T7; beast-3 0.42–1.19 s (base 2.4 s to over 120 s) | met |
| VG1: every report unchanged | VG1 T1 (407 loadable models, every walk against its base body), T10 (existing focused files and goldens); sweep verdicts equal at every size | met |
| VG2: a constraint proposal written as the growth document says is admitted by `gnd evolve` | VG2 T1 (preview, apply, validate with documents) | met |
| VG2: rule D-12 and the growth document say the same | VG2 T3 (the code's admitted set against the three pages) | met |
| VG3: the #222 root validates; included elements keep their fields; U2–U8 apply to owned elements | VG3 T1–T4, T9 | met |
| VG3: D13 and D14 as ruled | VG3 T5, T9, R1-F1 | met |
| VG3: one `INCLUDE` line per include, the prefix on included diagnostics | VG3 T6, T8, T11 | met (text output only, D5 (a)) |
| VG4: the root grows through preview, apply and finalize; included elements read-only; the first round declares the first document | VG4 T1–T3 | met |
| VG5: one packaged example runs the whole path; the pages describe it; replies drafted | VG5 T1–T5; `notes/issue-replies.md` | met; replies not posted |
| close items: green gates above; the component check; a close review on D8's instrument | this file; the close record | the review runs over this bundle |

## Open questions raised in the records

| Question | Raised in | Disposition |
|---|---|---|
| `ModelIndex`'s cache key admits two models whose values differ; readers other than the VG1 tables still read the first model's rows | `002-phase-VG1.md` | carried: a maintenance pass, the owner to file |
| a subtype chain hundreds of types deep stays slow (44.6 s at 800) | plan D12; `002-phase-VG1.md` | carried: successor question, figures recorded |
| `gnd judgments check` runs the checker twice | plan D10 | carried: successor question |
| VG1-D5: does the witness oracle's walk need a table | `002-phase-VG1.md` | closed: `gnd verify` measured 0.40 s at 1,000 |
| `remap_issues` finds the composed address by a pattern over addresses it writes | `003-phase-VG3.md` | carried: a maintenance pass, if the owner wants one |
| U1's first-document rule | `003-phase-VG3.md` | closed by `005-phase-VG4.md` |
| the evolve exit classifier maps refusals by message text | `004-phase-VG2.md` | carried: a maintenance pass, if the owner wants one |
| a census of every CLI route against include roots | `006-phase-VG5.md` | carried: a maintenance pass, if the owner wants one |
| the five red IR3 PyRel tests | `003-phase-VG3.md` (known red) | carried: the separate fix proposed to the owner |
| MC1 T22's timing test flaked twice | `005-phase-VG4.md` | carried: a maintenance pass |
| the stale lines of `project.md` (D11) | plan D11 | carried: the owner's, outside a phase; the lint line is now true |
| posting the three replies | plan §5 | carried: the owner's |
| the spec-level open questions of plan §10 (VG1 table home, VG3 origin route and line text, VG4 D6 home) | plan §10 | closed by VG1-D1, VG3-D1, VG3-D2, VG4-D2 |
