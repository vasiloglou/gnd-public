---
milestone: pyrel-agent-loop
station: phase-PL14
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PL14
date: 2026-10-14
source_base: da71d7b
gate:
  command: "uv run pytest -q -p no:cacheprovider -m \"pyrel_oracle or not pyrel_oracle\" tests/test_pyrel_rules_calendar.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py"
  exit: 0
  output: "261 passed in 203.09s (0:03:23)"
offline_gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf8_structure.py tests/test_rf7_structure.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf6_query_policy.py tests/test_rf9_repairs.py tests/test_rf6_packages.py tests/test_rf3_core.py tests/test_public_pyrel_export_runtime_support.py tests/test_documentation_tutorials.py"
  exit: 1
  output: "5 failed, 915 passed; the same 5 inherited failures listed in 013-phase-PL13a.md"
tutorials:
  - {command: "GND_TUTORIAL_PYREL_PYTHON=... uv run python tools/run_tutorials.py --group runtime-pyrel --lane pyrel", exit: 0, output: "16 tutorial blocks passed"}
  - {command: "uv run python tools/run_tutorials.py --group runtime-pyrel", exit: 0, output: "6 tutorial blocks passed"}
  - {command: "uv run --group docs zensical build --strict", exit: 0, output: "No issues found"}
evidence:
  - {path: "src/gnd/export/pyrel_rules.py", sha256: "a3a9369c085ad81b0598b7f864db083c46bca3dd05075c37fa1cd2c5832690d3"}
  - {path: "tests/test_pyrel_rules_calendar.py", sha256: "244cb7236a0da17a3edbd38a0c6d1d15c2123b95ae2304a2ab1f699368f4793d"}
  - {path: "tests/test_pyrel_rules_families.py", sha256: "98867418c121b42fd3fff502096701dcf768620a78a8884e857e777ac22629cb"}
  - {path: "tests/fixtures/pyrel-rules-calendar/expected.json", sha256: "d71ce2f55071105a36d9b71f52b64468082b7d1ed3f2bd728a9ed00034acaccb"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL14-spec.md", sha256: "6700adb7f3e5314350dd314e9ed2f7c4be682fe0fc4ed8785e192fccb777c830"}
  - {path: ".gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL14-claude-review.md", sha256: "1472270641fd1781ea2c9b902e398ca5d834480abcbd655195d5a2851781c574"}
  - {path: "docs/runtimes/pyrel.md", sha256: "f9bbfaf03f715817ec96cebaa201b7a670ce2073dbf1fcbee307c35b5b799e59"}
checkpoints:
  - "C4, shown to the owner on 2026-10-14: https://claude.ai/artifact/EkbVZmyETE8aFJvpnUSiPU (clinic refill dates and the dispatch catalogue, real runs)"
---
# Phase PL14: dates and reference populations in the PyRel rules programs

Spec: [notes/phase-PL14-spec.md](notes/phase-PL14-spec.md), delegated approval
(auto=true) with post-review amendments A1–A6 in its §12. Checkpoint C4 (above)
showed the phase on the clinic and dispatch examples before this record.

## What landed

- **Dates.** Date roles are PyRel `Date` fields and Duration roles are Integer
  days.
  - Cells are checked strictly (`YYYY-MM-DD` Gregorian days; durations from 0
    to 1,000,000), in facts and instance rosters alike.
  - Dates are loaded as `datetime.date` and printed back as ISO strings.
- **Date literals.** Strict ISO strings facing a Date, tagged `{date}` and
  `{duration_days}` literals, and Date ranges and allowed lists all render as
  dates.
- **Guarded comparisons** may use `date_add`/`date_sub`, rendered as
  `std_date.add/subtract(x, days(n))`, and Integer arithmetic.
  - A bindings listing runs first.
  - The report applies GND's rules: a computed date outside years 1–9999, or
    more than 10,000 date calculations, leaves the rule not checked (exit 4
    when alethic).
  - The date arithmetic runs only when there are bindings.
- **Refused by name:** DateTime, nested date terms, malformed date literals,
  and the float tier.
- **Reference populations.**
  - Bound at export with GND's `bind_references`, so tamper, missing-file,
    identity, ownership and declaration errors are refused with exit 3.
  - Embedded in the program, with each file and its SHA-256 in the header.
  - A candidate that names an owned fact type is refused (exit 3).
  - Reference facts, instances and covers are merged.
- **Corpora:**
  - `tests/fixtures/pyrel-rules-calendar/` holds 2 models and 14 populations,
    with `expected.json` from GND.
  - `refonly/` is the harvest's bug case.
  - `review/` holds 19 review reproductions.
- **Docs:** `docs/runtimes/pyrel.md` lists dates and references and their
  refusals.

## Bug fixed

Before PL14, `gnd export pyrel --rules` ignored `reference_populations`. On a
reference-only dispatch model, GND accepts the seed (exit 0) while the program
reported violations (exit 1). Now pinned by
`test_reference_facts_are_read_by_rules_and_derivations`, which fails on the
pre-PL14 code.

## Measured

- **Agreement:** the DuckDB program agrees with `gnd.api.check` on status,
  witness and exit for:
  - all 14 calendar populations;
  - the shipped `dispatch` and `release` seed and repaired populations (dates,
    references and recursion together);
  - the reference-only model;
  - 14 review reproductions.
- **LQP compile counts:** clinic 8, workload 1, dispatch 6.
- **Probes (harvest):**
  - PyRel `std.datetime.date.add/subtract` agree with GND on leap days;
  - DuckDB silently computes year-10000 dates inside comparisons, which is why
    the report decides the range itself.

## Mutation run

13 mutants, M61–M74, over date lowering, ranges, limits, cell checks and
references.
- 12 were killed at first.
- M73 (reference covers not merged) survived. A test for a mandatory rule over
  a reference-owned fact type was added, and M73 is now killed.

All 13 are killed (session scratchpad `pl14/mutants5.out`). The run came before
the review repairs. Of the review regression tests, 16 failed on the pre-review
code and pass now (`pl14/prefix-review-tests.out`). The pre-PL14 run of the
calendar tests failed 28 of 28 (`pl14/prefix-tests.out`).

## Review

One reviewer is one reviewer: a single Claude subagent, same model family. Its
report is retained verbatim in `notes/phase-PL14-claude-review.md`. Verdict:
REVISE. All findings were reproduced first with a replay of the reviewer's 80
cases (`pl14/replay.py`). After the repairs, every case agrees with GND or is
refused by name, except F5.

| # | Finding | Triage | Disposition |
|---|---|---|---|
| F1 | an empty Date side crashes (NULL + INTERVAL) | blocking | fixed (A1): the bindings listing first, then arithmetic only with bindings; `review/N2`, `N3`, `Z2` |
| F2 | loose Date literal parsing | blocking | fixed (A2): strict dates only; malformed ones are dropped from allowed lists (as GND) and refused by name elsewhere; `review/J3`, `J4`, `D7`, `G`, `G2`, `H2` |
| F3 | rosters not validated | blocking | fixed (A3); `review/K0`–`K6` |
| F4 | declaration-level reference refusals exit 70 | hardening | fixed (A4); `review/R7` |
| F5 | Integer arithmetic beyond DECIMAL(38) crashes | hardening | boundary: exit 70 is never a verdict, and the same bound as PL13b F7 |
| F6 | spec order and derivation literal text | completeness | spec amended (A4, A5); code binds before lowering |
| F7 | LQP header silent on date rules | completeness | header amended (A6) |
| F8 | test gaps | completeness | `E2`, `E3` (unchecked alone), the F1–F4 cases, and a cleaner tamper test added |

## Refuted premises

- **Spec §5:** "an untagged ISO literal facing a Date in a derivation `where`
  is a date". GND's validator refuses it.
- **The harvest's reading of `fromisoformat`:** it was taken as a strict check.
  Python 3.11+ accepts `20240229`, so the program uses a regex before it.

## Refactoring review

Executed:
- `_literal` is the one home for typed literals: atoms, comparisons, ranges
  and allowed lists.
- `_roster_types` and `check_cell` give one validation for facts and rosters.
- `model.raw_primitive` keeps the model's own types (Date, Duration) beside the
  PyRel type, in one place.

Seen but deferred: `_expr` (derivation terms) and `_operand` (requirement
terms) are two renderers for terms. Unifying them belongs with PL12-Q1 in PL15.

## Boundary

- The LQP `--connection` path is still not run on an engine (PL12-Q2).
- An engine would report a date rule GND leaves unchecked as broken; the header
  says so.
- **Refused by name:** DateTime, the float tier, `avg`, nested date terms, and
  malformed date literals outside allowed lists (GND compares those as text).
- Integer results beyond DECIMAL(38) stop the program with exit 70.
- References are embedded at export; a changed reference file needs a new
  export, and the header says so.

## Open questions

| # | Question | Target |
|---|---|---|
| PL12-Q1 | One lowering for the checker runtime and the rules programs (and one term renderer) | PL15 |
| PL12-Q2 | Run the LQP version on a RelationalAI engine | owner (engine and credentials) |
| PL13b-Q1 | Accept repeated facts where no rule depends on multiplicity | PL16, if needed |
| PL13b-Q3 | Exact Float arithmetic and the float tier | after PL19; no example needs it |
| PL14-Q1 | GND prints JSON for date models even with `--format text` | checker issue, outside this milestone |
