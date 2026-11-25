---
milestone: induction-skill
station: "phase-IS1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-IS1
date: 2026-11-25
source_base: 1e6083f3554e785aa994422c837fda874d74d1e6
source_subject: 8727886c
gates:
  - command: "uv run pytest -q -p no:randomly tests/test_packaged_skills.py tests/test_verification_fixes.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_marketplace_plugins.py tests/test_public_agents_skill_table.py tests/test_public_packaged_invocation_guards.py tests/test_public_packaged_command_help.py tests/test_public_workflow_claim_routes.py tests/test_public_packaged_import_skill_routes.py tests/test_skill_prose_sync.py tests/test_solve_successors.py tests/test_ik6_skill_census.py tests/test_ik_close.py tests/test_ik6_walk.py tests/test_schema_sync.py tests/test_judge_fact_types_skill.py tests/test_model_multivalued_skill.py tests/test_induce_skill.py"
    exit: "1, then 0"
    output: "1 failed, 982 passed, 1 deselected in 363.61s (0:06:03); the failure was the scaffold reference closure over the retained review links, then 90 passed after the declared retention edit"
  - command: "uv run pytest -q <the structure guards of project.md>"
    exit: "1, then 0"
    output: "1 failed, 871 passed, 2 deselected in 288.16s (0:04:48); the same scaffold case, then 90 passed"
  - command: "uv run ruff check; uv run --group docs zensical build --strict; uv run python tools/check_docs.py site; uv run gnd install --symlink --project --force; uv run gnd doctor --project"
    exit: 0
    output: "ruff: All checks passed!; docs build: finished, no issues; check_docs: 19545 local links/assets/anchors checked, exit 0; install and doctor: exit 0"
  - command: "uv run pytest -q -p no:randomly -m distribution tests/test_public_built_inventory.py"
    exit: 0
    output: "17 passed in 20.78s"
    note: "the owner-selected lane D20 (o), run once at the gate and recorded separately"
  - command: "ruling: delegated (auto=true) approved notes/phase-IS1-spec.md r4 sha256 c1620d12e50991f25f671570064208c28652a21f33ff365f030f8b9be7098bed"
    exit: "n/a -- ruling"
    output: "spec r4 approved with D21 to D23; recorded in the spec's section 13"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or the milestone close"
  reason: "the broad historical lanes are outside IS1's impact closure"
evidence:
  - path: .gnd-planning/milestones/induction-skill/notes/phase-IS1-spec.md
    sha256: 34c5ae689f98153452f31978a6403b5ae0034e1bdb0358bed6551d02030ee8b0
  - path: .gnd-planning/milestones/induction-skill/notes/induction-skill-plan.md
    sha256: 46e8e6c82d34dd6ca5b61abeebdc0c58fc9860671f08be7580a9a28d1834b0e7
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/c0-owner-reaction.txt
    sha256: 32b3b9f53a2920fd42f9d3a6516ed4035ed7b37e230e57c7a60056ae77ce1e24
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/regressions-red.txt
    sha256: d99fadff07861395a27af8f74777f20da3cf0704d49c4e0b88a633c4ecb0b574
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/gate.txt
    sha256: 0fe20fd3b44759e325ff0ee6fc2c6936ab83cddac2cbe862e2849425c06a3592
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/gate-after-r1.txt
    sha256: 36eef13038f77e01241d49b34010aca37910a6cbbf7269cf5ab007965a50e888
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/gate-final.txt
    sha256: 48d67c9b8ff8a1e5a21fcae40110403db272dc34c3c80ee7df64577d34ebbfcf
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/review-r1-repairs.txt
    sha256: b2f0877ba92c71f0dbf245e62e4e3b5a30fa6c1ec9b87c93c6a922757b5aff68
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/review-r1-mutations.py
    sha256: f8c09a1dd72dc1dbcd0f9a4fc66e2b30e3de10c63e07923e6bb920b3633c397f
  - path: .gnd-planning/milestones/induction-skill/evidence/IS1/review-r2-repairs.txt
    sha256: 3635f44b695c7035c8792a79272b3ca7e3378978851a71b940ecdb26c81f1403
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.md
    sha256: 83568598e8aa87a3bc0951649177a4a267cb29ac0787e06ef9b26798a083b07a
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/FINDINGS.md
    sha256: e7dd025a7791d96f734941c39452e4248a496c7bc324231a7bafd1b4e35e9643
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/review.md
    sha256: e74ea4f75acd8d9e373e91999de4a0b159ccf4b9c01d41ee51709760e8832179
  - path: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/FINDINGS.md
    sha256: c0e7e2e7145e3e01b4e4a5a07db91b64ab3a00ce6963037dacf7a9db03a62202
  - path: src/gnd/skills/gnd-induce/SKILL.md
    sha256: fc071e0e7631eb1614603e4a861c68be07ac0ac1cd6568cd28f768d13be042b0
  - path: tests/test_induce_skill.py
    sha256: cc406f960bc124be49439952e294e2f74d7ee27815dcfddba8659c13957c811e
  - path: src/gnd/skills/gnd-orm-core/references/labels.schema.json
    sha256: f3b90f9f1654a3246858c2c28e3ac60f08ed0485182594a7aaef9c7d8deeecf8
---

# Phase IS1: the induction skill, its routes and its pins

## What shipped

A new packaged skill, **`gnd-induce`**, the seventeenth workflow skill and the
nineteenth packaged one. It runs the induction loop through skill prompts:
- `gnd measure --labels` scores a model's rules against host labels;
- `gnd discover` proposes rules that hold in one population;
- `gnd export ilp` with `gnd import ilp-rules` round-trips a learner the user
  names, with GND re-checking the coverage claim;
- `gnd export ilp --target amie` with `gnd import mined-rules` handles a rule miner (D22);
- `gnd check` re-checks a population after an apply.

Every proposal goes to `gnd-model-evolve`; the skill never applies one. It
asks the user for the audit actor, never takes it from git, and never answers
as its own `llm` learner (D21). `gnd discover --families fact-type` groups go
to the two judge skills (D23).

| Surface | Change |
|---|---|
| `src/gnd/skills/gnd-induce/SKILL.md` | the skill, 183 lines: eight one-home refusals (R-a to R-h), one reactions table, seven fenced `gnd` lines |
| `gnd-orm-core` | a workflow-index row, a Reference-index row and the vendored `references/labels.schema.json` (D3), named in "Canonical schemas" |
| `gnd-export`, `gnd-dev-session`, `gnd-solve`, `gnd-model-evolve` | one route sentence each (D17 (o)); no frozen skill changed |
| `.claude/skills/gnd-induce`, `.codex/skills/gnd-induce` | generated by `gnd install --symlink --project --force` |
| `AGENTS.md`, `docs/agents/index.md` | one row each |
| pins | `tests/test_packaged_skills.py` (names, files, link graph, routing rows, record route, denial), `tests/test_doctor_uninstall.py` (link maps), `tests/test_public_packaged_invocation_guards.py` (`export` and `import` grouped, D9; the per-skill count), `tests/test_schema_sync.py` (the label schema), `tests/test_public_distribution.py` (19) |
| `tests/test_induce_skill.py` | new: T8, T13, T14, T17 and this skill's T7 (command paths and full option names) |

Commits, in order: `af309176` (the delegated ruling), `a7b2f24b` (the pins, red
alone), `86961531` (the skill without the docs rows), `983a23b0` (the rows),
`2eb6478d` (review round 1 repairs), `9ded3368` (round 1 retained),
`8727886c` (round 2 repairs and round 2 retained).

## Gate output (verbatim)

From [gate-final.txt](evidence/IS1/gate-final.txt):

```text
IS1 final gate, run 2026-11-25 in a clean clone at the commit below (macOS, Python 3.14).
8727886cf16d1bae95750bbc411de074048aacea
$ uv run pytest -q -p no:randomly <spec gate files>
1 failed, 982 passed, 1 deselected in 363.61s (0:06:03)
$ uv run pytest -q <project structure guards, project.md>
1 failed, 871 passed, 2 deselected in 288.16s (0:04:48)
$ uv run ruff check
All checks passed!
$ uv run --group docs zensical build --strict
Build finished in 2.55s
$ uv run python tools/check_docs.py site
19545 local links/assets/anchors checked
exit 0
$ uv run gnd install --symlink --project --force && uv run gnd doctor --project
exit 0
$ uv run pytest -q -p no:randomly -m distribution tests/test_public_built_inventory.py   # D20 (o)
17 passed in 20.78s

The one failure in both pytest runs was tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap: the retained review.md files of rounds 1 and 2 carried repository-relative links that do not resolve from their folder. After the declared retention edit to both review.md files (a link prefix, and one quoted example), in the same clone:
$ uv run pytest -q tests/test_development_scaffold.py
90 passed, 1 deselected in 68.10s (0:01:08)
```

The red controls (spec section 5), each in a clean clone of the IS1 base, are
in [regressions-red.txt](evidence/IS1/regressions-red.txt):
- control 1, the pins alone over the pre-IS1 tree: 49 failures over the eight
  inventory files, and T16 (the distribution lane) 7 failures;
- control 2, the whole change but the two docs rows: T5 and T17 fail. Git
  history holds that tree as `86961531`.

## Measured criteria

| Criterion | Evidence | Result |
|---|---|---|
| IS1-C1 frontmatter | `test_every_packaged_skill_frontmatter_reads_back` | holds |
| IS1-C2 every inventory pin moves, red first | control 1; the gate | holds |
| IS1-C3 routing rows, record route, denial | five `ROUTING_MATRIX` rows whose triggers and boundaries are absent at the base; `RECORD_ROUTES`; the denials map | holds; round 2 F8 found the matrix passes when only the handoff link changes (residual IS1-Q2) |
| IS1-C4 one home per refusal | `test_t8_each_refusal_is_said_once_and_only_in_gnd_induce`, counting visible occurrences | holds; round 2 F7 found a refusal hidden in a link-definition title still counts (IS1-Q2) |
| IS1-C5 the fenced lines pass the guards (D9) | the invocation and help-option tests; `test_t7_*` | holds for the seven lines; the global guard's gaps are IS1-Q1 |
| IS1-C6 the IK census unchanged | `tests/test_ik6_skill_census.py`, unedited | holds: D8 was already discharged on main |
| IS1-C7 AGENTS.md and the agents index, docs build | T5, T17; the docs build and link check | holds |
| IS1-C8 checkpoint C0 before the skill text | a private mockup page; the owner's answer "Keep them apart" ([receipt](evidence/IS1/c0-owner-reaction.txt)) | holds |
| IS1-C9 no frozen skill differs from the base | T13, with a seeded clone | holds |
| D21 never the `llm` learner | R-b; `test_t8_the_llm_learner_is_named_and_the_skill_stops` | holds as text; round 2 F9: a reversal that keeps the keywords passes (IS1-Q2) |

## Adversarial review

One reviewer, Codex through the review helper, in two rounds. One reviewer is
one reviewer.

- **Round 1** ([review](notes/reviews/phase-IS1-r1/review.md),
  [ledger](notes/reviews/phase-IS1-r1/FINDINGS.md)), over the IS1 diff:
  twelve findings, all reproduced.
  - Five were blocking, in the skill's own text:
    - discovery handed off by `EMITTED`, missing fact-type proposals;
    - the miner import was called partial;
    - `inducer` was put in the run record;
    - the class-mode prerequisite and the neutral fallback were missing;
    - four overclaims, among them "Popper has not run".
  - Six were hardening, in the tests; one was completeness (T16 and the T17
    commit order).
  - All were fixed in `2eb6478d` with failing-first tests, except the global
    guard's part of F9 (IS1-Q1). Fourteen of fifteen reviewer mutations now
    fail; the fifteenth, a valid heading with trailing spaces, correctly
    passes ([repairs](evidence/IS1/review-r1-repairs.txt)).
- **Round budget**, declared before round 2: one more round over the repair
  diff, then stop.
- **Round 2** ([review](notes/reviews/phase-IS1-r2/review.md),
  [ledger](notes/reviews/phase-IS1-r2/FINDINGS.md)), over `983a23b0..` (the
  repairs): eleven findings, all reproduced.
  - Three were blocking text, fixed in `8727886c` with assertions that failed
    first ([repairs](evidence/IS1/review-r2-repairs.txt)): the measure cells
    by mode, the neutral export's contents, and "every result" in the
    description.
  - Eight are test-strength and evidence findings.
  - Eight of eleven were introduced by the round-1 repair (0.73 > 0.5). The
    stop rule held: no round 3, and the eight are residuals (IS1-Q2).
- **The repaired skill bytes of `8727886c` carry no review opinion.**

## Refactoring review

**None executed.** One refactor was seen and deferred.
`tests/test_packaged_skills.py` pins the link graph as a chain of
per-milestone unions: MC3, MC4, RN0, GC4, LX2, VG5, and now SI1 and IS1.
Each milestone appends a set and a count. That chain is how SI1's edge went
unpinned while the file stayed on the structure-guard list: a new edge needs
someone to append it, and nothing fails until the whole graph is compared.
Regenerating `EXPECTED_RELATIVE_LINKS` as one literal, with a short
provenance table, would end the chain. It touches every milestone's pin
history, so it is IS1-Q3, not this phase's. The skill itself adds no module,
and the sibling edits are one sentence each.

## Boundary -- what this phase does NOT establish

- That an agent following `gnd-induce` reaches the right result. The tests
  read sentences, and a sentence test cannot fail when an agent ignores the
  sentence (spec section 8). IS2's recordings are the partial evidence of
  behaviour.
- That the tests catch every legal edit that breaks the text: round 2 lists
  eight kinds that still pass (IS1-Q2).
- A review opinion over `8727886c`'s skill bytes.
- Any learner run; no learner was installed or run.
- Linux, an installed wheel beyond the D20 lane, or the broad lanes.
- The full default lane: it was not run at this gate (spec ledger, cadence
  row). `tests/test_public_distribution.py:317` is edited and runs at the
  milestone close.

## Open questions

| Id | Question | Target |
|---|---|---|
| IS1-Q1 | The global invocation guard predates IS1 and binds every skill. It has a floor of 29 against 41 measured snippets, matches long options by substring (so an abbreviation passes), and scans backtick fences only | repository maintenance; an issue on the owner's word |
| IS1-Q2 | The test-strength residuals of round 2, F3 (test) and F4 to F10: per-command actor assertions, the miner's export line, table and comment visibility, link-definition titles, the handoff link, keyword reversals, the path, install and identity patterns | the next change to `tests/test_induce_skill.py`, at the latest IS2 |
| IS1-Q3 | Regenerate `EXPECTED_RELATIVE_LINKS` as one literal, ending the per-milestone union chain | repository maintenance |
| IS1-Q4 | SI1 (seeded-routes-and-identifiers, `8acc7b29`) merged with `tests/test_packaged_skills.py` red, although that file is on the structure-guard list; IS1 pinned the edge (finding F1 below) | the seeded-routes-and-identifiers close sweep |
| IS1-Q5 | The evidence runner `review-r1-mutations.py` restores the supplied baseline and labels any failure CAUGHT (round 2 F11); the recorded outcomes were reproduced independently | stated beside the evidence; no later use |

## Refuted premises

- **Plan section 2 and spec section 6.1: "the Popper branch is unproven on the
  refunds example".** `docs/reference/ilp-bridge.md`, "Comparing the learners",
  records three Popper 5.0.1 runs over refunds; run 3 admitted one clause.
  The skill now says the reference records them. Plan repair: at the milestone
  close.
- **Spec section 6.1: "six fenced `gnd` lines".** Measured seven: the miner's
  export is its own line. Fixed by measurement, as the spec allows.
- **Spec section 6.2: "15 new edges".** Measured 15 for IS1, plus one SI1 edge
  main had left unpinned (implementation finding F1: main was red on
  `test_every_relative_skill_link_resolves_inside_the_resource_tree` at the
  base, reproduced in a clean clone of `1e6083f3`).
- **Round 1's first T8 and T17 tests** passed on edits that reversed what they
  guard. They were replaced; see the review section.
