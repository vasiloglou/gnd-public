---
milestone: include-root-routes
station: "milestone close"
skill: process-milestone
scope: milestone-close
date: 2026-11-21
gates:
  - command: "uv run pytest -q tests/test_include_root_close.py tests/test_ir1_judgments_includes.py tests/test_ir2_flatten.py tests/test_ir3_pyrel_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_mc1_model_includes.py tests/test_mc1_census.py tests/test_public_v71_judgment_successor_guards.py tests/test_public_v71_full_judgments.py tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_extract_cli.py tests/test_public_extract_boundary.py tests/test_rf1_semantic_pins.py tests/test_rf1_cli_pins.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_pyrel_rules.py tests/test_pyrel_rules_calendar.py tests/test_pyrel_learning_path.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_release_text.py tests/test_gate_guard_list.py --tb=short"
    exit: 0
  - command: "uv run ruff check src tests tools"
    exit: 0
  - command: "uv run ruff check"
    exit: 1
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
  - command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/include-root-routes/close-review-request.json --out panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/include-root-routes/notes/include-root-routes-plan.md sha256 46f30cad657f54bfe758b6fa1a965ea78de734016cf6927ef41a1b52bbf2dcdc"
    exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/include-root-routes/notes/include-root-routes-plan.md
    commit: 0e1b7fb6
    sha256: 46f30cad657f54bfe758b6fa1a965ea78de734016cf6927ef41a1b52bbf2dcdc
  - path: .gnd-planning/milestones/include-root-routes/001-plan-gate.md
    sha256: b74d5aef5810968012e3998e845aba96f03bab9a8de6c68d82939222e060697a
  - path: .gnd-planning/milestones/include-root-routes/002-phase-IR1.md
    sha256: f575dce59bde3e80924ab71756983e108de0c222d50cc02c742e445023497c3b
  - path: .gnd-planning/milestones/include-root-routes/003-phase-IR2.md
    sha256: f8763f809ed75a203e7616e9b4e8d51438b893d2c27954a838b4235e9b6de01d
  - path: .gnd-planning/milestones/include-root-routes/004-phase-IR3.md
    sha256: e98ec9e803f4b241b2b5af2ffd3bc3c08536e02160a47b223ecf874fc11f9517
  - path: .gnd-planning/milestones/include-root-routes/notes/issue-replies.md
    sha256: 0aeeb54848986e4b2c7881322551e1e6804ed3877e3008add19ead24d63c71f9
  - path: .gnd-planning/milestones/include-root-routes/notes/close-results.md
    commit: 0e1b7fb6
    sha256: ffe76465ee6239f27d4e312d61ea833c68e6ee4899b088f3a15ac245896515d0
  - path: .gnd-planning/milestones/include-root-routes/notes/close-delta.md
    commit: 0e1b7fb6
    sha256: aef599ea7e6d58ee3f0b219dfaeaf0423ab9e3d60b5cd348770fb52c242f0b16
  - path: .gnd-planning/milestones/include-root-routes/evidence/close-review/PANEL-REVIEW.md
    sha256: f09ce567b5a7441cb57e8d513502ccc4fa6375511c104053e66c75cc83d8fe61
  - path: .gnd-planning/milestones/include-root-routes/evidence/close-review/disposition.md
    sha256: adc09d3260a464d71f2a3d3405df8ea840bb7e0128ce4b7926408daaf394c308
  - path: src/gnd/model/_includes.py
    commit: 0e1b7fb6
    sha256: 5d94814e8be5e8c9a17831892661f3f245bb0124a6d221f33a9ae3255073cd94
  - path: tests/test_include_root_close.py
    commit: 0e1b7fb6
    sha256: f793867f856954eb3e133974e55743d07836b109a0fb100a8e6ff69f2a762e44
---

# Claim

All three mandatory phases of include-root-routes have their records and
green gates. The milestone's exit gates exited 0 at `0e1b7fb6` (union lane
1169 passed; guard block 715 passed; ruff over `src tests tools`; component
index), and the panel-light close review exited 0 with six of six seats. The
close is ruled by **delegated approval (auto=true)** over plan r6.

## Gate output (verbatim)

Union of the phase lanes, widened by the close-repair file and
`tests/test_mc1_census.py` because `compose` changed:

    1169 passed, 83 deselected in 152.42s (0:02:32)
    exit=0

Guard block with `tests/test_release_text.py` and `tests/test_gate_guard_list.py`:

    715 passed, 2 deselected in 98.86s (0:01:38)
    exit=0

    uv run ruff check src tests tools
    All checks passed!
    exit=0

    uv run ruff check
    [*] 10 fixable with the `--fix` option (154 hidden fixes can be enabled with the `--unsafe-fixes` option).
    exit=1

The whole-repository red is in dev-tools-delivered scripts under `.claude/`
and `.codex/`, added by the dev-tools sync `541e3e33` (PR 219) and red on
`185ccaca`; this milestone changes none of those files. By amendment (c2)
it is recorded, not gated (ruling below).

    python3 scripts/components_index.py changed --base origin/main --strict
    changed against origin/main (260c433): 96 file(s) differ; 0 to fix, 0 warning(s), 12 to reread
    exit=0

The 12 `reread` entries were read beside the diff (see `004-phase-IR3.md`)
and still describe their code. The 83 deselected cases are the default lane
filter's opt-in lanes; none ran.

Close review, panel light, over plan r5 with `notes/close-results.md` and
`notes/close-delta.md` at `f48659b1`: exit 0, `run_sha256`
`f3218632ec79a4a22da5d9b96f3e61b6ddea79e12228422b93a5dd1ffff9a47b`,
`quorum-established`, six of six successes; finalize exit 0 with 5 agreed
groups, 5 divergent views and 7 fixes
([disposition](evidence/close-review/disposition.md)).

## Close ruling

Delegated approval (auto=true), 2026-11-21. Authorization: the owner's
`/process-milestone include-root-routes auto` in this session, with the
owner's choice of the GND panel light for the close review. This is the
driving agent's ruling, not the owner's reading of the artifacts.

    approved: milestone include-root-routes closed over plan r6,
    sha256 46f30cad657f54bfe758b6fa1a965ea78de734016cf6927ef41a1b52bbf2dcdc,
    with the close amendments (c1) and (c2) of its section 11.

The ruling includes amendment (c2) to the close predicate: the lint gate is
`uv run ruff check src tests tools`, and the whole-repository command's
pre-existing red is recorded and carried. Five of the six close reviewers
raised this; the amendment changes what the close claims, not what any
code does, and the residual is carried to its owner below.

## Phases

| Phase | Record | Result |
|---|---|---|
| IR1 | [002-phase-IR1.md](002-phase-IR1.md) | `gnd judgments check` judges an include root, temporal or not |
| IR2 | [003-phase-IR2.md](003-phase-IR2.md) | `gnd flatten` writes the flat model and its record, temporal roots included |
| IR3 | [004-phase-IR3.md](004-phase-IR3.md) | `gnd export pyrel` exports an include root in all three modes and records the flattening |

## Goal predicates

| Predicate (plan r6) | Evidence | Status |
|---|---|---|
| IR1: judges an include root, temporal or not, as `gnd check` composes it | IR1 T1, T2; `test_judgments_mechanical_report_equals_gnd_check` (model digest, verdicts, reference binding equal) | met |
| IR1: receipts bind the root's sha256; pins bind every include | IR1 T3, T4; pins mandatory (`model/_includes.py:61-77`) | met |
| IR2: any include root written as flat model and record by `gnd flatten` | IR2 T1, T2 | met |
| IR3: all three export modes accept an include root through its flat model | IR3 T1, T3, T4 | met; under `--rules` the interop roots then stop at the anchored constraint, as their flat models do |
| IR3: digests recorded; a re-pinned include changes them | IR3 T4, T5 | met |
| every unsupported combination refuses with a message naming it | IR1 T6, T13; IR2 T3–T5, T12; IR3 T2, T7; the close-repair cases for unencodable paths and orphan attachments | met after the `compose` repair |
| close items: replies drafted; panel-light close review | `notes/issue-replies.md`; this record | met; the replies are not posted |

## Plan repair

Plan r6 (sha256 `46f30cad…dcdc`) carries every repair in §11 with its tag,
prior wording quoted from r4 (`1e419a88`) and the record that raised it:
five `(c1)` rows (the IR2 lane, the IR2 command inventories, the PyRel page,
the IR3 homes, the component-index step) and three `(c2)` rows (the
`flatten_service` home, the close predicate, the §9 lint row). The repaired
bytes carry no review opinion.

## Refuted premises

- Plan r4 §9 named no CLI pin file for IR2, and no inventory homes for a new
  command (`003-phase-IR2.md`).
- Plan r4 §5 named `docs/agents/export-and-review.md` as the PyRel page
  (`004-phase-IR3.md`).
- Plan r4's close predicate assumed a green whole-repository ruff; it was red
  on `main` before the milestone began.
- IR3-D2 (a): `pyrel_runtime.py` is embedded in every program (`004-phase-IR3.md`).

## Open-questions sweep

Every record in this milestone was re-read.

| Question | Raised in | Disposition |
|---|---|---|
| `gnd check` is superlinear in the number of object types (`universe._denoting_types` → `resolve_reference_value_type` → `model_queries._supertype_parents`; 266 s at 1,000 extra types) | `002-phase-IR1.md` | **carried**: owner to file an issue; a separate maintenance fix, not a milestone of this roadmap |
| whole-repository ruff red in dev-tools-delivered scripts | `002-phase-IR1.md`; close review | **carried**: owner, to be fixed in the dev-tools source and re-synced, or excluded in `pyproject.toml` by an owner policy ruling |
| `compose` raised `UnicodeEncodeError` for an unencodable include path | `004-phase-IR3.md`; close review | **closed** by `0e1b7fb6` (`include:path` on every route; `tests/test_include_root_close.py`) |
| a flat model written outside the root's folder cannot bind its references | `003-phase-IR2.md` | **retired** as an accepted residual: `gnd flatten` warns, and `gnd check` then exits 3 |
| the assertion-admission example copies the model alone and refuses include roots | `002-phase-IR1.md`; plan H11 | **carried** to literature-host-interfaces LH3 |
| `gnd exp` session judgments refuse include roots | plan §7 | **retired**: out of scope by the plan |
| IR2's `--out` folder rule | `001-plan-gate.md` | **closed** by IR2-D2 in `notes/phase-IR2-spec.md` §7 |
| IR3-C3's single expected outcome | `001-plan-gate.md` | **closed** by IR3-D5 in `notes/phase-IR3-spec.md` §7 |
| the PyRel `--rules` programs stop at the anchored constraint for the interop roots | `004-phase-IR3.md` | **carried** to pyrel-rules-coverage RP2, which owns it |

## Refactoring review

Each phase record carries its own section. IR1 and IR3 executed one
behaviour-preserving refactor each (`bytes_declare_includes`,
`gnd.export.include_roots`); IR2 argued none needed. No refactor was
deferred, so no open-questions row is owed for one.

## Boundary -- what this result did NOT establish

- This is local completion. Nothing is merged, released or published, and
  the issue replies are not posted; each needs the owner.
- No exported PyRel program was run; the opt-in lanes did not run.
- One reviewer reviewed each phase diff; the fixes after each phase review
  and after the close review carry no review opinion. Round 2 of the plan
  review had a bare quorum of three, two of them sharing one CLI.
- The panel is advisory. Its quorum counts successes, not quality.
- The checker's superlinear cost in object types is unchanged.
