# Pins and the review check · plan r1

**Status: r1, 2026-11-23, draft. Not reviewed, not approved.** No review
instrument has read these bytes. Approval is recorded only in a plan-gate
record, which does not exist yet.

This plan takes the work that three merged pull requests listed as not done:

- [PR 235](https://github.com/vasiloglou/gnd-public/pull/235) added the rule
  "General solutions, not pattern-matched ones" and a standing review claim.
  It notes that no review round had run with the new claim.
- [PR 246](https://github.com/vasiloglou/gnd-public/pull/246) synced dev-tools
  `cecebc6`, which moved that check into the shared review brief and
  `standing-rules.md`. It notes the same gap: "No review round has been run
  here with the new brief."
- [PR 247](https://github.com/vasiloglou/gnd-public/pull/247) raised the
  packaged-skill file count from 70 to 71 in two test files. It notes that
  the count is still three separate literals in three files, and that
  `tests/test_install.py` is not in the guard list, which is why its five
  failures went unnoticed on `main`.

Reading for this plan found a fourth copy that PR 247 missed:
`tests/test_verification_fixes.py` still pins 70 files and a 70-file set, and
5 of its 13 tests fail on `main` at `7c4439dd` (H12).

No GitHub issue was filed for any of these. The pull request texts are the
sources.

## Goal and completion predicates

A new packaged skill file changes one pin, and a red install or uninstall
test cannot sit unnoticed on `main`. The standing review check has evidence
for whether it finds code fitted to its examples.

- **PF1.** The packaged-skill inventory (file count, skill names, file set)
  is defined once, in `tests/test_packaged_skills.py`.
  `tests/test_install.py`, `tests/test_doctor_uninstall.py` and
  `tests/test_verification_fixes.py` (red on `main` today) import it, as
  `tests/test_public_built_inventory.py` already does. The three files are in
  the structure and inventory guard block of `project.md`. A guard test fails
  when another test file defines the inventory again.
- **PF2.** A recorded calibration: the review helper's default brief, with no
  `--claim`, run over a small corpus of diffs. Some diffs contain planted
  pattern-matched code, and others make the same change correctly. The
  record states how many planted defects the reviewer reported with a
  breaking input, and how many false findings it gave on the correct diffs.

The milestone is closed when both phases have records and the close record
cites green focused gates, the guard block, `uv run ruff check`, the
component-index check and a close review on the instrument D3 selects.

## 0. Binding design rules

- **R0.1 One home per pin.** A value the tests pin lives in one file; other
  files import it. No phase copies a literal to make a test pass.
- **R0.2 Dev-tools files are not edited here.** The review brief,
  `standing-rules.md` and `review_tool.py` come from dev-tools
  (`.devtools.toml`). PF2 measures them and reports. A change they need goes
  to dev-tools as a proposal and comes back by a sync.
- **R0.3 No check is weakened.** PF1 moves pins and adds guards; it removes no
  assertion.
- **R0.4 A calibration states its limits before it runs** (spec-note
  contract, "An experiment, recorded before it runs"). The answer key is kept
  apart from what the reviewer reads.

The project's standing rules (`project.md`) and "General solutions, not
pattern-matched ones" (`AGENTS.md`) bind both phases.

## 1. Scope, sources and authority

"Observed" means read or run at `7c4439dd` (`main`) on 2026-11-23.

| # | Source | Obligation | Kind | Phase |
|---|---|---|---|---|
| H1 | PR 247, "Not established" | the count is three literals in three test files | inherited | PF1 |
| H2 | `tests/test_packaged_skills.py:19`, `tests/test_install.py:51`, `tests/test_doctor_uninstall.py:47` | `EXPECTED_SKILL_FILE_COUNT = 71` is defined in all three | observed | PF1 |
| H3 | `tests/test_packaged_skills.py:22`, `tests/test_install.py:56`, `tests/test_doctor_uninstall.py:52` | `EXPECTED_SKILL_NAMES` is defined in all three | observed | PF1 |
| H4 | `tests/test_public_built_inventory.py:11-14` | already imports `EXPECTED_SKILL_FILE_COUNT` and `EXPECTED_SKILL_FILES` from `test_packaged_skills` | observed | PF1 reuses the pattern |
| H5 | PR 247; `project.md`, "Structure and inventory guards, issue 171" | `tests/test_install.py` is not in the guard block; neither is `tests/test_doctor_uninstall.py` | observed | PF1 |
| H6 | `tests/test_gate_guard_list.py` | reads the guard block; the block may grow; both copies of `project.md` must agree | observed | PF1 |
| H7 | run on 2026-11-23 | `tests/test_install.py`, `tests/test_doctor_uninstall.py` and `tests/test_gate_guard_list.py` pass at `7c4439dd`: 174 passed in 52 s | observed | PF1 baseline |
| H8 | PR 235 and PR 246, "Not established" | no review round has run with the standing check | inherited | PF2 |
| H9 | `standing-rules.md`, "Code fitted to its examples" | the rule's one home for a review round; a finding names the breaking input | observed | PF2 |
| H10 | `review_tool.py brief --help`, `run --help` | `brief --subject {close,phase,plan,pr,spec}`, optional `--claim`; `run --reviewer {codex,claude}` | observed | PF2 |
| H12 | `tests/test_verification_fixes.py:17-18`; run on 2026-11-23 | defines its own `EXPECTED_SKILL_FILES` (70 files, without `count-witness-contract.md`) and `EXPECTED_SKILL_FILE_COUNT = 70`. `uv run pytest -q tests/test_verification_fixes.py`: 5 failed, 8 passed. It is in the default lane and not in the guard block | observed | PF1 |
| H13 | `tests/test_public_distribution_runtime.py:1`, `:14`, `:21` | `EXPECTED_SKILL_FILE_COUNT = 59` in the `distribution` lane; its docstring says it pins "exact installed-distribution originals", a released wheel's bytes, not the current tree | observed by reading | PF1 decides (D5) |
| H11 | `AGENTS.md`, "General solutions, not pattern-matched ones" | reviewers build a legal input the tests lack and run it | observed | PF2 |

Component index: `project.md` says this repository has no component index
for the shared skills' purposes, but `dev/components/` exists and other plans
search it. PF1 adds no module and PF2 adds evidence only, so neither needs a
search. The pre-PR index check still runs.

## 2. Contract proposal and product behavior

Neither phase changes a `gnd` command, a packaged skill or a record format.

### PF1 — one inventory pin, guarded

- `tests/test_install.py`, `tests/test_doctor_uninstall.py` and
  `tests/test_verification_fixes.py` import the inventory names they use
  (`EXPECTED_SKILL_FILE_COUNT`, `EXPECTED_SKILL_NAMES`,
  `EXPECTED_SKILL_FILES`) from `test_packaged_skills`. Their own definitions
  go, and the 5 failures of H12 turn green by the import, not by a new
  literal.
- A guard test reads every `tests/*.py` file with `ast` and fails when a file
  other than `tests/test_packaged_skills.py` assigns one of the inventory
  names at module level.
- The three files join the guard block in both copies of `project.md`.
- The distribution-lane copy (H13) pins a released wheel, not the tree. The
  guard test lists it as the one allowed exception, by path, with that
  reason (D5).
- First step, before any edit: one run of the default lane at the phase base,
  on beast-3. Any other red file is listed in the record. If it is red because
  of a duplicated pin, PF1 repairs it under R0.1. Otherwise it is a finding
  reported to the owner, not repaired here (D1).

### PF2 — does the standing check find what it is for

- A corpus of small diffs on scratch branches, each against `main`: about
  four with planted pattern-matched code (a regular expression over YAML or
  Markdown structure, a special case naming one fixture's id, a string split
  over a path, a fix that widens a pattern) and about four controls that make
  the same change with the parser or helper the repository already has.
- Each diff gets a brief from `review_tool.py brief --subject pr` with no
  `--claim`, and one run with a reviewer in a different tool (D2).
- Grading against the answer key: a planted defect counts as found only when
  the review names a breaking input, as `standing-rules.md` requires. On a
  control, a finding about fitted code counts as a false finding.
- The record states the counts and their limits: a small corpus, one
  reviewer, planted defects written by the same assistant that grades them.
  A miss that the brief's wording explains becomes a proposal to dev-tools
  (R0.2), drafted and not sent.

## 3. Dependencies and artifact homes

| Phase | Needs | Homes it changes |
|---|---|---|
| PF1 | plan gate | `tests/test_install.py`, `tests/test_doctor_uninstall.py`, `tests/test_verification_fixes.py`, a new `tests/test_inventory_pin_home.py`, `.codex/skills/process-phase/references/project.md` and its `.claude` twin, `tests/test_gate_guard_list.py` only if its listed set grows |
| PF2 | plan gate; D2 ruled | `.gnd-planning/milestones/pins-and-review-check/evidence/PF2/` only. Scratch branches are deleted after the run, and their diffs are kept as evidence files |

PF1 and PF2 share no file and can run in either order. PF1 is first because
it is cheaper and needs no paid call.

Other writers. `project.md` is owned by this repository and edited by any
session that changes the gate rules. PF1 touches only the guard block.

## 4. Phases

| Phase | Criteria | Inherited residuals |
|---|---|---|
| PF1 | **PF1-C1** `EXPECTED_SKILL_FILE_COUNT`, `EXPECTED_SKILL_NAMES` and `EXPECTED_SKILL_FILES` are assigned at module level only in `tests/test_packaged_skills.py`, apart from the exception D5 rules. **PF1-C2** the guard test fails on a scratch copy of a test file that assigns either name again, and passes on the tree. **PF1-C3** the guard block names `tests/test_install.py`, `tests/test_doctor_uninstall.py` and `tests/test_verification_fixes.py`, and `tests/test_gate_guard_list.py` passes. **PF1-C4** no test is removed: 174 tests over the three files of H7 and 13 in `tests/test_verification_fixes.py` before, the same after, all passing (the 5 of H12 included), plus the new guard file. **PF1-C5** the baseline run's red files, if any, are listed with what was done about each | H1, H5 |
| PF2 | **PF2-C1** the corpus, its answer key and each brief are committed before any reviewer runs. **PF2-C2** every diff has a review or a recorded failure to run. **PF2-C3** the record states planted found (with a breaking input), planted missed, and false findings on controls, with the limits of R0.4. **PF2-C4** each miss names the brief sentence it bears on, or says none does | H8 |

Each phase also runs the guard block, `uv run ruff check`, a review of its
diff by the instrument D3 selects, and its record.

## 5. Documentation, skill and compatibility surfaces

- No packaged skill, `gnd` command or user document changes.
- `project.md` changes in both copies; `tests/test_gate_guard_list.py`
  holds them equal.
- Release notes: no entry. Both phases change only tests, planning and
  evidence.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| The guard test is itself a pattern match over source text | it reads module-level assignments with `ast` (`AGENTS.md`); PF1-C2 runs it on a planted copy |
| The guard block gets slower | the three files add about 60 s to a block of about two minutes (H7, H12); the plan gate accepts or refuses that cost |
| The baseline run finds many red files and PF1 grows | PF1 repairs only duplicated pins; anything else is listed for the owner (D1) |
| PF2 grades its own planted defects | the answer key is written before the runs; the record states the limit |
| PF2 changes the delivered brief by hand | R0.2: a change goes to dev-tools |
| Paid reviewer calls | PF2 runs about eight; D2 sets the reviewer and the count |

## 7. Out of scope

- Changing the review brief, `standing-rules.md` or `review_tool.py` here
  (R0.2).
- A full review of the existing tree for pattern-matched code. PF2 measures
  the check; it does not apply it to old code.
- Other duplicated test constants beyond the skill inventory, unless the
  baseline run shows one red.
- Making cloud CI a required status check.

## 8. Execution, approval and review protocol

- Default `auto=false`. The owner approves the plan, then each phase spec,
  before any code.
- Each phase: spec, owner gate, change, focused gates, diff review (D3),
  record, commit. One pull request for the milestone, or one per phase if
  the owner prefers. Merge stays with the owner.
- Before the pull request:
  `python3 scripts/components_index.py changed --base origin/main --strict`
  exits 0.

## 9. Per-phase verification

| Phase | Focused lane | Expected |
|---|---|---|
| PF1 | `uv run pytest -q tests/test_inventory_pin_home.py tests/test_packaged_skills.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_gate_guard_list.py --tb=short` | exit 0 |
| PF2 | no code; the evidence directory and its answer key | the record's counts |
| all | the guard block of `project.md`, `uv run ruff check` | exit 0 |

`tests/test_public_built_inventory.py` imports the inventory too, but it is
in the `distribution` lane (`pytestmark`), which the default lane excludes.
PF1 runs it once with `-m distribution` and records the result, without
making it a gate.

## 10. Owner decisions and open questions

All rows are proposals until the plan gate rules them.

| ID | Question | Proposed |
|---|---|---|
| D1 | PF1 baseline: run the whole default lane once on beast-3 before editing, and list (not repair) red files that are not pins | yes; about ten minutes on beast-3, no paid call |
| D2 | PF2 reviewer and size: (a) `codex`, about eight diffs, one run each; (b) `codex` and `claude`, both on every diff, to compare; (c) skip PF2 until a real phase review runs with the brief | (a). (b) doubles the cost for a comparison nobody asked for; (c) leaves PR 235's and PR 246's gap open |
| D3 | Plan, phase and close review instrument. `project.md` sets the panel as the bar for plan and close review | the owner's call. For a test-only milestone of two small phases, one reviewer in a different tool (the review helper) is proposed for every step, if the owner waives the panel for this milestone |
| D4 | One pull request or one per phase | one per phase: PF1 is ready long before PF2's evidence, and it repairs a red file on `main` |
| D5 | The distribution-lane pin of 59 files (H13): (a) an allowed exception, named by path with its reason; (b) import the current inventory, which changes what that lane asserts about a released wheel | (a). It describes released bytes; (b) would make it assert something else |

Open questions carried into the specs: PF1, none beyond D1 and D5 (the copies
were found by reading every module-level assignment of the three names under
`tests/`: H2, H3, H12, H13); PF2, the exact corpus and the wording that
counts as "names a breaking input".
