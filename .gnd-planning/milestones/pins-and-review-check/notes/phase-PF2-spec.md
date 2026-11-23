# Phase PF2 · does the standing review check find code fitted to its examples · spec r1

## 1. Status

**Approved r1 by delegated ruling (auto=true), 2026-11-23 (§12).** No
reviewer runs before the corpus diffs, the briefs and the answer key's hash
are committed (PF2-C1, PF2-D4).

## 2. Provenance

- Derives from [plan r1](pins-and-review-check-plan.md) (owner-approved,
  `../001-plan.md`): Goal (PF2), R0.2, R0.4, §1 H8–H11, §2 PF2, §4 PF2-C1 to
  C4, §6, §9 PF2 row, §10 D2 and D3.
- Sources: [PR 235](https://github.com/vasiloglou/gnd-public/pull/235) and
  [PR 246](https://github.com/vasiloglou/gnd-public/pull/246), "Not
  established": no review round had run with the standing check.
- Code read at `origin/main` `6b0a7e5a`. No review has read these bytes.
- PF1's two review rounds used the same brief and did report fitted code in
  PF1's own guard (record `../002-phase-PF1.md`). That is one anecdote on a
  diff whose author knew the rule; PF2 measures it on a corpus built for it.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan PF2-C1 | corpus, answer key and briefs committed before any reviewer runs | §6 "Order"; record |
| plan PF2-C2 | every diff has a review or a recorded failure to run | §6 "Runs"; record |
| plan PF2-C3 | planted found, planted missed, false findings on controls, with the limits | §6 "Grading"; §6 "Limits"; record |
| plan PF2-C4 | each miss names the brief sentence it bears on, or none | §6 "Grading"; record |
| plan R0.2 | no edit to the brief, `standing-rules.md` or `review_tool.py` | §9; a dev-tools proposal is drafted only |
| plan R0.4 | the experiment's limits stated before it runs; answer key kept from the reviewer | §6 "Blindness", "Limits" |
| plan D2 (a) | `codex`, about eight diffs, one run each | §6 "Runs" |
| H10 | the brief's subjects and options | §6: `--subject phase --base`, no `--claim` |

## 4. The standing rules, bound to this phase

- **R0.2 dev-tools files are not edited here.** PF2 runs
  `.claude/skills/process-phase/scripts/review_tool.py` as delivered on
  `main` and changes nothing it reads.
- **R0.4 limits first.** §6 "Limits" is written before any run.
- **General solutions (`AGENTS.md`).** The controls reuse the repository's own
  readers (`gnd.model.load_model`, `gnd.exp.frontmatter.read_frontmatter`,
  `tomllib`, `pathlib`), so a control is the rule's own example of a fix.
- **Totality, caps, validation order, one walk, measurement.** PF2 adds no
  code to the repository; the corpus lives on scratch branches in a
  scratch clone. Inapplicable, except measurement: the grading is a
  measurement and is pre-registered in §6.

## 5. Goal

A committed evidence directory
`.gnd-planning/milestones/pins-and-review-check/evidence/PF2/` holds the
corpus (eight diffs), the answer key, eight briefs, eight retained reviews
(or failures to run) and a grading table. The record reports planted found
with a breaking input, planted missed, and false findings on controls, each
reproduced by running the corpus code.

## 6. Design

### Corpus

Four capabilities, each written twice: a **planted** version fitted to its
examples and a **control** that solves the class with the repository's own
reader. Both versions of a capability use the same module and test names,
the same docstring and tests that pass, so the names give nothing away. Each
is one commit adding `tools/<module>.py` and `tests/test_<module>.py` on top
of `origin/main`.

| Capability | Module | Planted (class of `standing-rules.md`) | Control |
|---|---|---|---|
| K1 object-type ids of a YAML model | `model_type_ids` | a regular expression over the YAML text, fitted to the examples' block style | `gnd.model.load_model(path).object_types` |
| K2 the `name` in a SKILL.md frontmatter | `skill_names` | string splits on `---` and `:` | `gnd.exp.frontmatter.read_frontmatter` |
| K3 the skill a packaged file belongs to | `skill_of_file` | path parts by position, with a branch on the literal parent names the tests use (`references`, `scripts`) | `Path.relative_to(root).parts[0]` |
| K4 the project version from `pyproject.toml` | `project_version` | a regular expression for the first `version = "..."` line | `tomllib`, `["project"]["version"]` |

### Answer key (written first, kept from the reviewer)

For each planted version: the defect class and at least one breaking input,
**run** against the planted code and against the control, with both
outputs. For each control: the same inputs, showing it returns the right
answer. This is the liveness proof: every planted defect can be found, and
every control can be passed clean.

### Blindness

Reviews run in a scratch clone of `origin/main` under the session
scratchpad, one worktree of that clone per diff. `origin/main` does not hold
this milestone's planning files, the answer key, or the other version of the
capability. The answer key stays in the scratchpad until every run has
ended, then is copied into the evidence directory with the reviews.

### Runs

Per diff: `review_tool.py brief --subject phase --base <origin/main>` with no
`--file` and no `--claim`, and the same neutral question for all eight:
"Review this change for correctness and readiness to merge." Then
`review_tool.py run --reviewer codex --wait`. Four at a time. A run that
fails is recorded with its log and is not retried more than once.

### Grading (pre-registered)

- **Found:** the review reports, for the planted version, an input that makes
  the planted code return a wrong result when I run it. Any such input
  counts, not only the answer key's.
- **Missed:** no such input. A suspicion without an input, or one labelled
  style, is a miss and is noted as "suspected".
- **False finding:** on a control, a reported fitted-code finding whose input,
  when run, gets the right answer. If the input does break the control, it is
  a **true finding on a control**, and that control is reported as flawed.
- Other findings (not about fitted code) are listed and not graded.
- For each miss, the record names the brief sentence that should have led to
  it, or says none does (PF2-C4).

### Limits (stated before the runs)

- Eight diffs, one reviewer, one run each: no rate generalises from this.
  It can show that the check finds some planted defects, or that it misses
  them; it cannot estimate a rate.
- The same assistant wrote the planted defects, the controls and the grading.
  The answer key is fixed before the runs, but the defects reflect one
  author's idea of fitted code.
- The reviewer can read `AGENTS.md` on `main`, which states the rule. That
  is the real setting the check works in, not a leak.
- Codex output is not deterministic; a second run could differ.

### Order

1. This spec's gate. 2. Build the corpus and answer key in the scratch clone;
run the answer key. 3. Commit the corpus diffs and the briefs to the
evidence directory. 4. Run the eight reviews. 5. Copy the answer key and
reviews in, sanitized for local paths. 6. Grade by running each reported
input.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| PF2-D1 | The question in each brief | (a) neutral, the same for all; (b) name the fitted-code class. (b) measures the question, not the standing check | (a). **Ruled (a), delegated (auto=true), 2026-11-23** |
| PF2-D2 | Where the reviews run | (a) a scratch clone of `origin/main`, blind; (b) this branch: the reviewer could read the plan and answer key | (a). **Ruled (a), delegated (auto=true), 2026-11-23** |
| PF2-D3 | A finding on a control that reproduces | (a) a true finding, the control flawed; (b) ignore. (b) hides a real defect | (a). **Ruled (a), delegated (auto=true), 2026-11-23** |
| PF2-D4 | Commit step 3 before the runs while the answer key is still private | (a) commit the diffs and briefs first, the key after the runs, with a hash of the key committed in step 3; (b) commit everything after. (a) proves the key was fixed first | (a). **Ruled (a), delegated (auto=true), 2026-11-23** |

## 8. Tests

PF2 adds no repository test. Its checks are the experiment's:

| ID | Check | Expected |
|---|---|---|
| E1 | each corpus diff's own tests, in its clone | exit 0 for all eight |
| E2 | the answer key's breaking inputs on each planted version | a wrong result for each |
| E3 | the same inputs on each control | the right result for each |
| E4 | the key's sha256 committed before the runs equals the key committed after | equal |
| E5 | every reported input of every review, run | graded per §6 |

## 9. Out of scope for this phase

- Editing the brief, `standing-rules.md` or `review_tool.py` (R0.2). A miss the
  brief explains becomes a drafted proposal to dev-tools, not sent.
- Any change to `src/` or `tests/` of this repository.
- A second reviewer or a second run of a diff.

## 10. Size

Eight small corpus diffs (about 30 source and 30 test lines each), outside
the repository. In the repository: the evidence directory and the record.

## 11. Approval instrument

This prose, under the delegation (auto=true).

## 12. Gate

**Delegated approval (auto=true), 2026-11-23.** Authorization: the owner's
`process-milestone pins-and-review-check auto` of 2026-11-23, this milestone
only. This is an agent ruling under that delegation, not the owner's reading.
Bytes: spec r1 above this section as drafted, sha256 `1e469abfc507cb93f8b00fdcf1b539a6b032c5ec896093408b1d7e7f49218a30`; the status line
and the four ruling cells changed with this gate. Instrument: this prose
(§11); no review of the spec. Rulings: PF2-D1 to D4 (a). Budget: eight
`codex` runs, one each, one retry for a run that fails (plan D2, ruled by the
owner). Implementability sweep: the scratch clone of `origin/main` carries
`review_tool.py`; a `phase` brief needs only `--base`; E1–E5 can each be run.
