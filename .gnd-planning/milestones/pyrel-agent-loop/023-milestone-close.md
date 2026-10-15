---
milestone: pyrel-agent-loop
station: milestone-close
skill: process-milestone
scope: milestone-close
date: 2026-10-15
source_base: a9a2f08
gate:
  command: "local replay of .github/workflows/development.yml and docs.yml plus tools/accept_pyrel_applications_install.py, in a clean worktree of ea7b337 (the close readers' fixes); later commits checked by focused suites"
  exit: 1
  output: "candidate 0; full suite (Python 3.11) 8 failed, 14882 passed: the 7 that also fail on origin/main plus one timing-noise failure that passed 3 of 3 alone; installed 10 passed; docs 207 blocks, strict build, 10380 links; install acceptance complete"
evidence:
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/close-reading-one.md", sha256: "c6045d7cb91b51659e95f3b9bd54ab93e27da9fce569688ce9f09c8a67402160"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/close-reading-two.md", sha256: "65729a07a07226f561ceda0fa292a2d4e6a5396ff0b37277c405df97dd135909"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/close-reading-three.md", sha256: "4755de5e0645bbcb07f670dd33afe3be766dded86e61d8a66eecb38bb9c7164d"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/close-reading-four.md", sha256: "a11359e22ac5258ebdff9406a287339c148acbd59209d603a61d6a738b0c64b6"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/022-owner-decisions-close.md", sha256: "26dc5107270823df190cf8b9748d6684f25b854596eab4dd67b10095439aacae"}
---
# Milestone close: PyRel agent loop

**The effective plan.** The plan r1 (`notes/pyrel-agent-loop-plan.md`),
amendment A1 (`notes/plan-amendment-a1.md`) and the owner's decisions (records
012 and 022).

**Records:**
- the phases PL1–PL6 under r1: 002, 003, 004, 006, 007–010;
- the phases PL12–PL18 under A1: 011, 013–017, 020, 021;
- the recording gates: 005, 018, 019;
- the owner decisions: 012, 022.

**PL7–PL11 never ran.** Record 012 reordered the work, and PL18 took over their
page obligations.

## What the milestone shipped

- **The generated PyRel programs.** `gnd export pyrel --rules duckdb|lqp`
  states every constraint family, derived fact, date, reference and operation
  plan as PyRel. The DuckDB version runs locally and agrees with GND's checker
  on every corpus and recorded plan. The LQP version is compiled and counted,
  not run on an engine (owner ruling, 012).
- **Five plan apps** (course, clinic, access, trip, lease) on one shared core,
  with GND and PyRel backends, a `rules` command, and feedback that names the
  rule, the facts and the rule's PyRel line.
- **Recordings:**
  - 125 real model runs (Claude Code Haiku and default; Llama 3.1 8B, Gemma
    3 4B, Llama 3.2 3B);
  - four `gnd-model-from-text` sessions;
  - two `gnd-model-evolve` sessions.

  Every run is kept and bound by a SHA-256 manifest, and every discarded launch
  is disclosed.
- **GSD-style docs:**
  - two tutorials and four how-to pages;
  - two explanation pages, saying that PyRel is optional and how a rule becomes
    a check;
  - replays rendered from the recordings, each with its failures explained;
  - links to the source files.

## Completion predicates (plan r1)

| # | Verdict | Evidence |
|---|---|---|
| 1 Readable commands | MET WITH RESIDUAL (owner ruling CD1) | The new pages meet it. BookRec ch. 7 and Expense ch. 4 do not, and carry to PL18-Q1; record 002's claim is corrected in 022 |
| 2 One copy per project | MET WITH RESIDUAL | close-reading-one: one `copytree` or `gnd codegen` plus one `copytree`, and conformance exits 0. The experiment setup still copies two files |
| 3 Rules three ways | MET | close-reading-one C1; the agreement test is green |
| 4 The agent loop, twice | MET (owner ruling CD2) | The stand-in half: close-reading-one C3. The Claude Code half: the course tutorial's recorded skill sessions and the 50 Claude plan-app runs; Codex on the two older chapters |
| 5 Skills shown in place | MET WITH RESIDUAL | The recap tables cover steps 2, 3, 5 and 7; the skill steps are paraphrased, not cited by heading |
| 6 Gates green | MET WITH RESIDUAL | The local CI below; its only failures also fail on origin/main |

## Close review

Four independent local readers, one lens each, each with fresh context. All are
the same model family; no vendor diversity is claimed. Their reports are
retained in `notes/close-reading-one..four.md`.

| Reader | Blocking findings | Disposition |
|---|---|---|
| One (the r1 predicates) | predicate 1 not met on the older chapters; predicate 4's Claude Code half | owner rulings CD1 and CD2 (022) |
| Two (the A1 obligations and the question ledger) | none | hardening rows carried below |
| Three (evidence and honesty) | the git user's email and handle in the evolve recordings | redacted, recorded in the manifest, leak searches widened, test added (b0e7af9) |
| Four (a newcomer following the pages) | the install could not run the new pages; step 8's `cd` left the shell in the wrong folder | fixed (ea7b337); step 8 replayed in one shell |

Hardening findings handled at the close:
- terms explained inline: DuckDB, the two programs, Snowflake's status;
- source links warn that includes render only on the docs site;
- the evolve README and the runs page corrected;
- gate 018 amended for its two discarded launches.

## Local CI on the merged bytes

| Stage | Result |
|---|---|
| candidate | exit 0: wheel and sdist, the comparison wheel rebuilt from the sdist, SHA256SUMS verified |
| full suite, Python 3.11 | 8 failed, 14882 passed. 7 also fail on origin/main (listed below). `test_guarded_corpus::test_connected_three_atom_join_meets_the_declared_bound` failed its own timing-stability check (relative spread 0.22 against a limit of 0.30 on a 1.9x ratio); it passed 3 of 3 alone and is unchanged by the branch |
| Python 3.13 | the full suite ran at a1d9452 (021); the same set failed, nothing specific to 3.13 |
| installed | 10 passed, against the candidate copied without hidden files, as `actions/upload-artifact` delivers it |
| docs | 207 tutorial blocks, strict build with no issues, 10380 links |
| install acceptance (`tools/accept_pyrel_applications_install.py`) | complete: a fresh wheel, `plan_apps` included |

Commits after ea7b337 (b0e7af9 and the close records) change recordings, tests,
recorders' leak searches, one docs page and planning notes. They were checked
with the plan-app, replay, recording and docs suites (111 passed), the strict
build and `check_docs` (10380 links). The reference-closure test was rerun in a
clean worktree of the final commit (below).

The failures that also fail on origin/main (a9a2f08), run the same way:
- `test_rf1_pin_harness::test_mutation_table_rows_of_their_own`
- `test_rf7_structure::test_complete_routing_and_dirty_controls`
- `test_rf6_query_policy::test_dynamic_candidate_inventory_is_complete_and_live`
- `test_rf6_query_policy::test_dynamic_duplicate_inventory_row_is_refused`
- `test_rf6_packages::test_original_definition_body_is_verbatim[gnd.checker.check]`
- `test_rf4_peripheral::test_moved_algorithm_preserves_base_body[gnd.api:_run_check_raw]`
- `test_rf4_peripheral::test_current_successor_body_and_import_controls_are_live`

## Open questions carried forward

Every row from records 011–021, swept by close reader two. Each now has a
target; none is closed silently.

| # | Question | Target |
|---|---|---|
| PL12-Q1 (residual) | The checker runtime (`pyrel_runtime.py`, `applications.py`) still lowers rules separately from `pyrel_rules.py` | next PyRel milestone |
| PL12-Q2 | Run the LQP version on a RelationalAI engine | owner (engine and credentials); compile-only accepted in 012 |
| PL13b-Q1 | Accept repeated facts where no rule depends on multiplicity, as GND does; no example needed it | next PyRel milestone |
| PL13b-Q3 | Exact Float arithmetic and the float-tier functions (still refused by name) | next PyRel milestone |
| PL13a-Q2, PL13b-Q2, PL14-Q1, PL15-Q1, PL18-Q3 | GND checker bugs seen on the way (exit 70 on a Float at an exclusive bound, aggregate semiderived exit 70, reference-fed derived heads in plans, `gnd validate` through a symlink, "derived origin lineage missing") | GND checker issues |
| PL15-Q3 | Witness order for acyclic and uniqueness in later states | next PyRel milestone, if a recording needs it |
| PL16-Q1, PL18-Q2 | Model fidelity: clinic refills and their day, the trip budget totals, course `no_retake` while enrolled | example models, next docs milestone |
| PL16-Q2, PL17-Q1 | A machine-readable verdict file from the generated program, and a structured event log from the apps | next PyRel milestone |
| PL17-Q2 | Re-record with the type-neutral template and project-only settings | owner, if the docs need it |
| PL18-Q1 | Per-skill How-to pages; move BookRec ch. 7 and Expense ch. 4 to Reference (with CD1's predicate 1 residual) | next docs milestone |
| PL18-Q5, PL18-Q6 | `gnd evolve` should fill the digests itself; the evolve skill should give the proposal format in full | GND and skill update |
| A1 work limits | A fixpoint row limit and an aggregate group limit, each refused by name (A1 :410-412). Only the 500-step cap and the 1 MiB input cap exist | next PyRel milestone |
| A1 GitHub render check | `gh api markdown` over the new pages: the `--8<--` includes print as text on GitHub | next docs milestone |
| A1 PL7 items | `recommend_book`/`approve_expense` operations for BookRec and Expense; generalizing `tools/openrouter_gateway.py`; retiring `rules_in_pyrel.py` | next docs milestone |
| A1 capability matrix | Not every listed capability appears in an example (ring, cardinality and value range in Course; xor and equality in Clinic; v4 references) | next docs milestone |
| A1-D4, A1-D5, the one-prompt Quickstart | Not ruled by the owner; the Quickstart was withdrawn under delegation (PL18 A3) | owner |
| `_expr` / `_operand` | The two term renderers in `pyrel_rules.py` remain separate (016) | next PyRel milestone |

## Refuted premises

- **PL16 spec: "the PL17 recordings show the skill doing it live".** PL17 ran
  bots with no tools. The skill sessions were recorded in PL18, for Course only.
- **PL12: `--explain`.** It became `--rules duckdb|lqp`.

## Boundary

- **Not on an engine.** The LQP program has not run on a RelationalAI engine,
  and Snowflake execution is not yet supported by gnd export.
- **Not cherry-picked, but not a rate.** The recordings are small (5 runs per
  model and app) and kept whole. They do not measure a success rate.
- **Earlier phase records hash their own phase's bytes.** Later phases changed
  some of those files; this record and 021 describe the merged bytes.
- **Untracked files** in `src/gnd/examples/bookrec/` and at the root predate the
  milestone and are not in git (owner ruling CD3).
