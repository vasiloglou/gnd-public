# Phase FU5: cycle helpers (issue 114)

## 1. Status

**r2 (2026-11-08): D1 ruled (a), retire now; D2, D3 and the §6 design
await the owner.** The owner ruled D1 (b), "Keep until release", over r1
(commit e311c829). That ruling rested on r1's P1, which the Codex review
showed false (R1): `v0.1.0` contains RF6, so RF-D5's release trigger has
occurred. r2 corrected P1-P4 and put D1 again with the true facts; the
owner then ruled (a), "Retire them now". The r1 ruling is retained below
as history. `auto=false`: no code before D2, D3 and §6 are approved.
§5's probe deleted the helpers in the working tree and was reverted. V2
at 53637ed8 with no code change: 2531 passed in 528.45s.

## 2. Provenance

- Plan r3 §4 FU5 (FU5-C1), §9 row FU5, FD5 (ruled as proposed: "retire
  `_dfs_cycle` and `_ring_component_violations`; keep `_find_cycle` only if
  a test outside the checker family needs it, else retire it and its
  test"); completion predicate 5 ("retired or explicitly kept, per RF-D5").
- Issue 114; RC2 spec F2 and the RC2 record's refactoring review.
- code-refactoring plan RF-D5 (`notes/code-refactoring-plan.md:504`):
  "Shims stay at least until the first public release after RF6.
  Retiring them is a later, separately approved phase." Shim inventory
  rows `notes/shim-inventory.md:755-757`.
- Base: main `6ed86d90` (FU4 merged).

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| FU5-C1 | per FD5 | D1, then M1-M3 |
| FU5-C1 | name the live guards that bind the helpers | §5 (all 15 failures, 6 files) |
| FU5-C1 | historical baselines and evidence stay byte-identical | M2 reads a new successor record; no historical file is edited |
| FU5-C1 | retirement is an explicit successor or exemption for the three names | M2 |
| FU5-C1 | a negative test that the retired imports fail | T2 |
| RF-D5 / AGENTS.md | retirement after the first public release after RF6, in a separately approved phase | **D1** (trigger not met, §5) |
| predicate 5 | retired or explicitly kept | D1 either way |
| plan §0 rule 3 | shims follow AGENTS.md and RF-D5 | D1 |
| plan §0 rule 5 | stop past 1.5 times the estimate (about -90 source, -10 test lines) | §10, D3 |
| §9 row | guard suites + `tests/test_checker_families.py` | V2 |
| AGENTS.md | component index; allowance count stays zero | V6 |

## 4. Goal

The three helpers that lost their last production caller in RC2 are
either retired with every guard told so explicitly, or kept with the
reason recorded.

## 5. Probe (2026-11-08, `6ed86d90`)

**P1 (r2; r1's P1 was false, review R1). The RF-D5 trigger has
occurred.** The only release, `v0.1.0` (published 2026-10-12, source
`75eda93f`), contains RF6a and RF6b: `git log v0.1.0` lists `a3f35a6d
docs(rf6a)` and `10608c47 docs(rf6b): Close the model and checker package
split`, and the tagged tree holds the RF6b package
(`src/gnd/checker/_core.py`, `__init__.py:128` re-exporting
`_find_cycle`). So "the first public release after RF6" exists, and RF-D5
now allows retirement in a separately approved phase; FU5 is that phase
if the owner approves it. r1 reached the opposite conclusion from a
mistaken ancestry check (it tested an FU2 commit, not an RF6 one).
`pyproject.toml` says 0.2.0, unreleased.

**P2. Importability.** All three names are importable from `gnd.checker`
in `v0.1.0` (the RF6b package; review R2 corrected r1's "a module"), so a
v0.1.0 user could import them; they are underscore-private and documented
nowhere public.

**P3. Callers.** No production path reaches the three-helper cluster
(they call each other: `_find_cycle` calls `_dfs_cycle`, `_core.py:1315`;
`_ring_component_violations` calls `_find_cycle`, `:1377`; review R3). One
test:
`tests/test_checker_families.py:206` (`_find_cycle`, checker family). No
test outside the checker family uses `_find_cycle`, so FD5 retires all
three.

**P4. What deleting them breaks.** Deleting the bodies
(`checker/_core.py:1296-1380`), the three `__module__` lines and the three
re-exports (`checker/__init__.py:101, 129, 184`), 91 lines, then running
every `tests/test_rf*.py` plus `tests/test_checker_families.py`: 15 failed,
2516 passed.

| Guard | Fails | Why |
|---|---|---|
| `test_rf6_packages.py::test_all_predecessor_import_bindings_and_metadata` | 1 | the frozen import baseline expects 230 `gnd.checker` bindings, the three included |
| `test_rf6_packages.py::test_original_definition_body_is_verbatim[...]` | 3 | the RF6b definition baseline pins each body |
| `test_rf6_query_policy.py` (inventory complete and live; duplicate row refused) | 2 | `_dfs_cycle`'s `graph.get(node, ())` is a counted dynamic query site |
| `support/rf9_ci_sources.coupling_sites` via `test_rf9_ci_repairs.py` (1), `test_rf4_peripheral.py` graph tests (6), `test_rf3_core.py` (1) | 8 | `compatibility-private-sites.json` lists the three re-exports, and the accounting refuses a listed alias that no longer exists |
| `test_checker_families.py::test_find_cycle_helper_names_members` | 1 | the helper's own test |

The dynamic-query guard already has a counted-removal successor,
`dynamic-query-successor.json` (`tests/test_rf6_query_policy.py:129-160`),
that can remove `_dfs_cycle`'s row; the import baseline, the definition
baseline and the compatibility private sites have no retirement mechanism
(review R4).

## 6. Design (if D1 is "retire")

**Reuse table** (searched 2026-11-08: `grep -rn "retire" tests/support
tests/test_rf*.py`; `compiled-snapshot-obligations/evidence/CI/`).

| Capability | Found | Decision |
|---|---|---|
| a successor record beside immutable evidence | `compiled-snapshot-obligations/evidence/CI/source-successors.json`, read by `support/rf9_ci_sources` (used by RC5, FU2) | **adapt**: a sibling `retired-names.json`, same home and reader module |
| graph algorithms | `gnd.graphs` (`infra.graphs`) | already the production path; nothing to move |

- **M1 source (about -91 lines).** Delete the three bodies, their
  `__module__` lines and re-exports; drop `graphlib`'s import if it becomes
  unused.
- **M2 retirement record (about +35 test-support lines).**
  `retired-names.json` lists `gnd.checker._find_cycle`, `_dfs_cycle`,
  `_ring_component_violations`, each with the issue, this phase and the
  owner's ruling. `support/rf9_ci_sources` gains one reader. Each of the
  three guard families without a mechanism subtracts exactly the listed
  names: the import baseline (230 becomes 227 live, the frozen file
  unchanged), the definition baseline rows, and the compatibility private
  sites. The dynamic-query row for `_dfs_cycle` is removed through the
  existing `dynamic-query-successor.json` (review R4). A listed name that is still importable fails the guard,
  so the record cannot hide a live binding.
- **M3 tests (about -10 / +15 lines).** Delete
  `test_find_cycle_helper_names_members`; add T2.
- Shim inventory rows 755-757 get a "retired in FU5" note, with the
  table rows kept (it is a planning note, not a guard).

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 (r2) | RF-D5's trigger has occurred (P1). Retire the three helpers now, as FD5 ruled, or keep them anyway until a later release? | **Ruled (o, 2026-11-08): (a), retire now** ("Retire them now"). Proposal was **(a) retire now**: FD5 ruled retirement, RF-D5 now permits it in a separately approved phase, and no production path uses them. Cost: §6, about +40 test-side lines (one dynamic-query successor row; a retirement record for the other three guard families). (b) Keep: an explicit deferral by owner choice, not by RF-D5; the shim inventory rows are annotated with it and issue 114 stays open |
| D1 (r1, history) | as r1 put it: "RF-D5's trigger (a public release after RF6) has not happened. Retire now, or keep the helpers until that release?" | **Ruled (o, 2026-11-08): (b), keep until the release** ("Keep until release"). Superseded: the premise was false (P1, review R1). |
| D2 | If (a): where the retirement record lives | `compiled-snapshot-obligations/evidence/CI/retired-names.json`, beside the existing successor record |
| D3 | If (a): the stop rule. The plan's -10 test lines did not foresee the retirement plumbing (about +35 support, net about +40 test-side lines) | accept the size as stated here; the stop line is measured against these numbers |
| D4 | Review over the spec | none; no spec review was run (the owner's ruling named D1 only) |

## 8. Tests and verification ledger (if D1 is "retire")

| T | Case | Expected |
|---|---|---|
| T1 | the 15 guard cases of P4 | pass, each subtracting exactly the retired names |
| T2 | `from gnd.checker import _find_cycle` (and the other two); `gnd.checker._core` likewise | `ImportError` / `AttributeError` |
| T3 | a retired name re-added to `gnd.checker` while still listed | the import-baseline guard fails |
| T4 | an unlisted binding deleted | still fails, as `test_deleted_binding_is_observed` does today |

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V2 | plan §9 row | run | `ls tests/test_rf*.py tests/test_checker_families.py \| xargs uv run pytest -q` |
| V3 | full suite vs base | run, sharded on beast-3 | failure list equal to the base's (sha256 `8261732b…`) |
| V5 | Codex review of the diff | run | `notes/phase-FU5-codex-review.md` |
| V6 | component index | run | `components_index.py changed --base 6ed86d90 --strict` |

If D1 is "keep", the phase edits only planning text (this spec, the
record, the shim inventory note) and V2 runs to show nothing moved.

## 9. Out of scope

Retiring any other shim; the RF-D5 rule itself; a release.

## 10. Size

Plan estimate: about -90 source, -10 test lines. If D1 is "retire":
-91 source, about +40 test-side lines (the dynamic-query guard reuses its
successor, review R4); D3 asks for that figure as the new basis.

## 11. Findings

- **FU5-O1 (withdrawn in r2).** r1 recorded FD5's premise as refuted; it
  was not. FD5's premise (a release after RF6) holds.

- **I1 (r1, withdrawn).** r1 said the shim inventory needs no edit. The
  plan says FU5 touches it (§5), and `tests/test_rf2_helpers.py` reads only
  RF2 rows, so the three RF6b rows can be annotated either way D1 goes
  (review R5).
- **I2 (Codex review of r1, 2026-11-08).** Disposition `block`, R1-R7;
  [review](phase-FU5-codex-review.md). R1 (blocking) reproduced: `git
  ls-tree v0.1.0 src/gnd/checker/` lists `_core.py`; `git log v0.1.0`
  lists the RF6a and RF6b commits. R2-R5 corrected above; R6 (no record
  yet) and R7 (README) follow D1.
