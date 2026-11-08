# Phase FU5: cycle helpers (issue 114)

## 1. Status

**Approved (2026-11-08): helpers kept until the release RF-D5 names.**
The owner ruled D1 (b) over r1 (commit e311c829) with "Keep until
release", answering "Keep the cycle helpers until the next release, or
retire them now?". D2 and D3 are moot; D4 (no spec review) follows the
proposal. `auto=false`. Prior status: "Draft r1, blocked on D1." §5's
probe deleted the helpers in the working tree and was reverted.

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

**P1. The RF-D5 trigger is not met.** The only release is `v0.1.0`
(2026-10-12, source `75eda93f`, the RF1 merge); RF6 landed after it
(records `code-refactoring/011-phase-RF6a.md`, `012-phase-RF6b.md`).
`pyproject.toml` says 0.2.0, unreleased. FD5's own proposal text named
"RF-D5's later approved phase, after the first public release", so its
premise is refuted (FU5-O1).

**P2. Importability.** `gnd.checker._find_cycle` existed in `v0.1.0`
(then a module, `src/gnd/checker.py`), so a v0.1.0 user could import it;
it is underscore-private and documented nowhere public.

**P3. Callers.** No production caller of any of the three. One test:
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

None of these guards has a retirement mechanism today.

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
- **M2 retirement record (about +45 test-support lines).**
  `retired-names.json` lists `gnd.checker._find_cycle`, `_dfs_cycle`,
  `_ring_component_violations`, each with the issue, this phase and the
  owner's ruling. `support/rf9_ci_sources` gains one reader. Each of the
  four guards in P4 subtracts exactly the listed names: the import baseline
  (230 becomes 227 live, the frozen file unchanged), the definition
  baseline rows, the compatibility private sites, and the dynamic query
  inventory row. A listed name that is still importable fails the guard,
  so the record cannot hide a live binding.
- **M3 tests (about -10 / +15 lines).** Delete
  `test_find_cycle_helper_names_members`; add T2.
- Shim inventory rows 755-757 get a "retired in FU5" note, with the
  table rows kept (it is a planning note, not a guard).

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | RF-D5's trigger (a public release after RF6) has not happened. Retire now, or keep the helpers until that release? | **(b) keep them until the release**: it is your standing rule, the gain is 91 dead lines, and retiring now costs a new retirement mechanism across 6 guard files for three private names. FU5 then records the kept helpers and their trigger, issue 114 stays open for the post-release retirement phase, and predicate 5 is met by "explicitly kept". (a) Retire now: waive RF-D5's release trigger for these three underscore-private names (a v0.1.0 user could import `_find_cycle`), with §6 as designed **Ruled (o, 2026-11-08): (b), keep until the release** ("Keep until release", answering "Keep the cycle helpers until the next release, or retire them now?"). |
| D2 | If (a): where the retirement record lives | `compiled-snapshot-obligations/evidence/CI/retired-names.json`, beside the existing successor record |
| D3 | If (a): the stop rule. The plan's -10 test lines did not foresee the retirement plumbing (about +45 support, net about +50 test-side lines) | accept the size as stated here; the stop line is measured against these numbers |
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
-91 source, about +50 test-side lines; D3 asks for that figure as the
new basis.

## 11. Findings

- **FU5-O1 (refuted premise, P1).** FD5 assumed RF-D5's release trigger;
  it has not fired. Recorded for the close.

- **I1 (D1 (b), 2026-11-08).** The phase edits planning text only. The
  shim inventory needs no edit: its rows for the three names
  (`code-refactoring/notes/shim-inventory.md:755-757`) already give
  "RF-D5" as the retirement, and `tests/test_rf2_helpers.py` parses that
  file, so it is left byte-identical. Issue 114 stays open, retargeted to
  the first retirement phase after a public release.
