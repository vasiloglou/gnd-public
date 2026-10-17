---
milestone: transition-check-performance
station: milestone-close
skill: n/a -- repository development close
scope: milestone-close
date: 2026-10-17
gate:
  command: "local replay of .github/workflows/development.yml at main 2689ab3 plus the main-CI repair ceed100 (see CI replay)"
  exit: 0
  output: "main 2689ab3 plus repair ceed100 (PR #31): 3.11 full 14937 passed; 3.13 full 14937 passed; 3.11 release acceptance 10 passed"
slow_cadence:
  command: uv run pytest -q -ra
  trigger: part of the CI replay above (full suite on 3.11 and 3.13)
  reason: the close replays the repository's own CI locally, because cloud CI is not a required check
---

# Claim

The milestone is complete. All five PRs are merged to `main` at `2689ab3`: #26 (plan
review and approval), #27 (TP0), #28 (TP1), #29 (TP2) and #30 (TP3, including the
CI fix-up `cea184c`). Four local close readers each returned **close-with-carryovers**,
with no blocking finding. Merge decisions were the owner's.

## Completion predicates (plan r5)

| # | Predicate | Evidence |
|---|---|---|
| 1 | The reporter's anonymized workload and the `course` control are committed, with a baseline | [002](002-phase-TP0.md), `tests/fixtures/transition_cost/`, `evidence/TP0/` |
| 2 | Every default-path result is byte-identical after each phase | TP0–TP3 digests and `evidence/close/digests.json` equal the TP0 file. Re-run on the final `main` code. Limit (close reader 1, R1-C2): CLI and batch runs are subprocesses, so their branch traces are not captured; `course` has no declared-post surface |
| 3 | ModelIndex key paths are bounded, other dumps do not increase, and edits get fresh indexes | 540 → 26; `model_dumps_other` stays at 457; [003](003-phase-TP1.md) |
| 4 | Removed copies have guard tests; nodes fall by at least 50% | 2,760,394 → 115,294; frozen-row runs; [004](004-phase-TP2.md) |
| 5 | Receipts: 25 → 19 checker runs, identical reports, named refusals | `evidence/close/receipt_replay.json` (on `main`): 25 vs 19, `payloads_identical: true`; [005](005-phase-TP3.md) |
| 6 | Wall time reported against the ~44% ceiling, with its limits | See below |
| 7 | Gates, reviews, docs, question sweep; PRs; owner acceptance separate | This record. The PRs were merged by the owner |

## Results

| Reporter replay (13 calls) | TP0 baseline | Final `main` |
|---|---|---|
| `checker_runs` | 25 | 25 by default, **19 with receipts** |
| `model_index_key_paths` | 540 | **26** |
| `model_dumps_other` | 457 | 457 |
| `deepcopy_nodes` | 2,760,394 | **115,294** |

**Wall time, against the planned ceiling of about 44%.** Close reader 4 interleaved the TP0 code, the default path on `main`, and `main` with receipts, each in fresh processes:

- **Default path:** about **−33%**.
- **With receipts:** about **−42%**.
- **Profiled calls,** which do not vary with machine load: 80.5 M → 38.7 M → 33.6 M (−52%, then −58%).

These numbers are reliable only within one interleaved run. The same machine drifted about 2.7× between sessions on 2026-10-17, so medians from separate runs are not compared.

**The largest remaining cost is extension calculation.** It costs about the same as before (about 5 s profiled), but is now about 42% of replay time. Its recursive `freeze` walk is not counted by `deepcopy_nodes`. That work is deferred, with TP4.

## After the TP3 record: the CI fix-up `cea184c`

A local replay of the repository's CI, run before merging, found 11 failures introduced by TP1–TP3 that the per-phase test selections had missed. **Refuted premise (close reader 3, F3):** the phase records said the focused gates plus the affected consumers "cover the touched homes". They did not, because the source-successor pins and the counted query policy sit outside those selections. Commit `cea184c`:

- reads fact types through ModelIndex in `check_with_receipt`. That fixes 5 query-policy failures. `src/gnd/api.py` is now SHA-256 `daba38fc…`, not the `e6b87892…` bound in [005](005-phase-TP3.md); this record binds the final file.
- records six intended definition changes in the shared registry `compiled-snapshot-obligations/evidence/CI/source-successors.json`. It adds five RF6b rows, and extends the RF4 `_run_check` row in place, which is the only update the registry allows. **Disclosure (close reader 3, F2):** that file is pinned by `compiled-snapshot-obligations/007` at `961dc221…`, and is now `c64487d8…`. Close reader 2 confirmed that every new row's `before` matches the code at `2d1ff4d`, so no older drift is hidden.

## CI replay

`.github/workflows/development.yml` was replayed locally: one Mac, `uv` 0.10.10 as pinned
by CI, both interpreters run on that same machine. The replays below were made before
and after the merges.

| Target | Result |
|---|---|
| Stack tip `a33334a`, before the fix-up | 18 failed / 14,919 passed, on both 3.11 and 3.13. 11 of the failures came from this milestone and were fixed in `cea184c`; 7 also failed on `main` |
| `main` `2689ab3`, after the merges | The 7 pre-existing failures remain, plus the `uv` `.gitignore` release-acceptance quirk. The replay was stopped once a repair existed |
| **`main` `2689ab3` + repair `ceed100`** ([PR #31](https://github.com/vasiloglou/gnd-public/pull/31)) | Build: pass. **3.11 full: 14,937 passed, 0 failed. 3.13 full: 14,937 passed, 0 failed.** 3.11 release acceptance: 10 passed. Separately on the repair branch: release acceptance 10 passed. The docs job passed earlier at the stack tip (207 tutorial blocks, strict build, 10,383 links) |

The repair is separate maintenance, requested by the owner. Its causes predate this
milestone, apart from the census rows TP3 added, which are listed in it. It is recorded in
`.gnd-planning/maintenance/2026-10-17-main-ci-repair/` on its own branch, and #31 must be
merged for `main` to pass CI. Sweep rows 11 and 12 move to that repair.

## Close review

Four local readers reviewed `main` at `2689ab3`
([1](notes/close-reading-1.md), [2](notes/close-reading-2.md),
[3](notes/close-reading-3.md), [4](notes/close-reading-4.md)). Each reader is one
reader, not a panel. All four returned **close-with-carryovers**, and none found
anything blocking.

| Reader | Lens | Key confirmation |
|---|---|---|
| 1 | correctness across phases | No cached container reaches a caller. A receipt reused 3 times matches a fresh transition. Reference-bearing models mint the same payload |
| 2 | code and compatibility | Default callers are unchanged. The registry rows are honest. It found the stale acceptance pin (fixed here) |
| 3 | records and protocol | Every phase has its full chain. No approval was invented. 77 evidence hashes match at their record commits. No downstream names |
| 4 | performance claims | Every counter and the parity reproduce exactly on `main`. The wall-time split is given above |

Fixed in this close PR:

- `tools/run_public_acceptance.py` asserted the old 7-name `api.__all__` (reader 2, F1).
- The release note for TP1 and TP2 was owed (reader 3).
- Stale status text in the README and PROJECT.md (readers 3 and 4).
- The receipt replay was regenerated on `main` (reader 4, H1).

A note on labels in the review notes: tags such as `M3` or `MU10` are reviewers' own mutant and measurement labels. They do not refer to any project's milestones. Earlier notes are left byte-stable, because the phase records pin their hashes.

## Owner decisions (ratified)

These deviations from approved specs were decided by the session and disclosed in each spec's findings section (close reader 3, F5). **The owner ratified all four on 2026-10-17 ("ratify").** None changes an approved result.

| Item | Deviation |
|---|---|
| TP0 D5 | Hang guard raised from 120 s to 600 s, after a reproduced timeout under concurrent load |
| TP1 §6 | The `load_population` decorator was dropped as redundant: `load_population_bytes`, whose scope covers it, is the only caller |
| TP2 T2 | The frozen guard uses `dict`/`list` subclasses instead of `MappingProxyType`, which changed results |
| TP3 §6 | Anchored models, unvalidated populations and pre-runs that raise take the normal `api.check` route and get non-reusable receipts. These were the two gaps Codex found |

## Open-questions sweep

| # | Question / carryover | Disposition, owner |
|---|---|---|
| 1 | Request 4: incremental evaluation and session objects, plus the reporter's two related session requests (TP4) | Carried to a successor milestone. Extension calculation is now the largest cost. Framework maintainer |
| 2 | Downstream acceptance (O13) | Carried to the reporter, who should measure on their own workload |
| 3 | Receipt report is mutable: editing `receipt.report` changes a later transition (TP3 H1; close reader 1, R1-H1) | Open. Proposed: keep a private copy or a digest, and check it at use. Framework maintainer, next milestone |
| 4 | A pre-run that raises during minting leads to two checker attempts (TP3 H2) | Open, low. Framework maintainer |
| 5 | No reference-population receipt test (TP3 C1; close reader 1, R1-C1) | Open, completeness. Probes found no defect. Framework maintainer |
| 6 | `_run_check_raw` ignores its `evaluator` hook on the anchored route | Open, refactor candidate. Framework maintainer |
| 7 | Internal accessor `iter_fact_types_shared` has no underscore and now has a reader in `api.py` (TP2 F3; close reader 2, F5) | Open, naming. Framework maintainer |
| 8 | `index_scope` and `scoped` are public names: an outer caller-held scope could accept a receipt after an operations-only edit, harmless today (close reader 1, R1-H2) | Open, low. Framework maintainer |
| 9 | `CheckReceipt` keeps dataclass equality and repr: `hash` raises, and `repr` is about 190 KB (close reader 2, F4) | Open, low. Framework maintainer |
| 10 | Signal-delivered exceptions during rule evaluation are reported as a "defective rule" (TP1 finding 6) | Open; predates this milestone. Framework maintainer |
| 11 | 7 failures that already fail on `main` (source pins and structure tests), including the 3 annotation-only TP3 census rows (close reader 2, F3) | Repaired in [PR #31](https://github.com/vasiloglou/gnd-public/pull/31) (owner-requested maintenance); verified 0 failures on both interpreters |
| 12 | `uv build` writes `.gitignore` into the candidate folders, failing release acceptance on `main` too | Repaired in PR #31; release acceptance 10 passed |
| 13 | The per-phase selection missed the pin and policy suites (F3, refuted premise) | Closed by this record. Future phases include `test_rf4/rf6/rf7/rf9*` in their impact closure |
| 14 | No interleaved A/B mode in the measurement tool for end-to-end gains (close reader 4, H3) | Open, completeness. Successor milestone |
| 15 | TP2's "TP1+TP2 −35%" chains two A/Bs (close reader 4, H2) | Closed by the interleaved figures above |
| 16 | The TP3 spec's `gnd-dev-session` check was not done | Checked during the close: `gnd-dev-session` documents transition walks inside sessions (schema 4/5 feedback), which never use receipts, and receipts are opt-in. No skill change is needed |
| 17 | TP1–TP3 approval hashes cannot be checked from history, because each spec was first committed with its code (close reader 3, F4) | Recorded. Future phases commit the approved spec before implementation |
| 18 | Unexplained intermittent gate failure during TP1 (TP1 finding 5) | Not reproduced again; closed as not established |

## Evidence hashes

[
  {"path": "src/gnd/api.py", "sha256": "daba38fcd38a30f255c687d153fb11981d10f474b61121480f44a87daf88fe4d"},
  {"path": "src/gnd/transition.py", "sha256": "d3883314bfe0101cbd8925d9efd32d6d79d1cdf8abe8894c5302d3c2f47a5302"},
  {"path": "src/gnd/model_index.py", "sha256": "c820a107ee8591e561c05745c863af9afcc6c095eeced5913e3027ea6ea8f540"},
  {"path": "tools/measure_transition_cost.py", "sha256": "0a2d74e9fc47d5a1abf6ce6d7c9e2687be214d27ed4e014c24b1bb3edf42645f"},
  {"path": "tools/run_public_acceptance.py", "sha256": "69682892d3905d3dc65588246d5f8339ac9159bbc283534444c59e32dae55b11"},
  {"path": "docs/release-notes.md", "sha256": "9e8681ca95e1d65c237ee6e483bd648278d85412cda894c24122eb563d792908"},
  {"path": ".gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json", "sha256": "c64487d837f6714b894a21872dbcec9df8a21874ad72c4fbd1edcfc649b402fa"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/close-reading-1.md", "sha256": "efb13c44c6b2222d9a789ce471a0e98c3508eb285febdd6af93bf30364203215"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/close-reading-2.md", "sha256": "6b374563e94e113e9bdd308e67dd16f40b26870a3e14e0dd2e4a9f36024bf145"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/close-reading-3.md", "sha256": "71b126abe06edbff68f042c0ed2785a4640d280de481ee4dc85d03e62ffe8726"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/close-reading-4.md", "sha256": "ddcf54a2c7ab88d92ce5c930141d04865c5c0e2254ebce0f1684228eaa30ce0d"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/close/counters.json", "sha256": "8754858f42cd2824a6e3887002d52e6b2f9c96ef6187c05c2087b0a7ce76a4f9"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/close/digests.json", "sha256": "d736d4d75fd82b7c5fd42102515d6b43eb21946326eaa3ebfd6a5223a1d4ca1c"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/close/milestone-tests-main.txt", "sha256": "9d76f58dfb80d2ad892e9f31f192771337f384747218072d862f6b143b1ebbce"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/close/receipt_replay.json", "sha256": "54d23cd997d835278d6fb2cbab47ef854cc650f1a5bca39aaedc2540a6fad1d6"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/close/timings.json", "sha256": "891bf23727ae37ab2496087ce36aa9940453c8405092d31a068e2fcadb35c788"}
]
