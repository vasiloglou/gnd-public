# IL6 — Comparison walk, docs, integration

## 1. Status

**r1 approved, 2026-10-28** (§12). `auto=false`. Implementation follows
corpus-first (IL6-D11).

**Base:** `claude/il6`, branched from `main` at `860e651` (PR #61, IL4,
merged). Every adapter phase is merged: IL1 to IL5 and IL4 are on `main`.

**What the gate decides:**
- IL6-D1 to IL6-D4: the walk's form, where its replayed learner outputs
  live, which invocations it shows, and how the comparison table is made;
- IL6-D5 and IL6-D6: two questions earlier phases targeted at IL6 (RIPPER's
  variability, IL3-Q3; a second AMIE run, IL4-Q4);
- IL6-D7 to IL6-D11: the docs scope, a checkpoint, the skill census, the
  installed-candidate check and the approval instrument.

## 2. Provenance

- **Plan:** [ilp-learners-plan.md](ilp-learners-plan.md) r3, owner-approved
  in [`001-plan-gate.md`](../001-plan-gate.md). Sections used: completion
  predicate 6; §0 (IL-R1 to IL-R11); §3; §4 "IL6" (IL6-C1 to C3) and
  "Carried limitations"; §5; §7; §9's IL6 row and its every-phase controls.
- **Prior records,** each read in full for what it hands to IL6:
  - [`002-phase-IL1.md`](../002-phase-IL1.md): three Popper invocations;
    invocation 1 is the run of record (`rendering-rejected`); 2 and 3 were
    owner-ruled; IL1-Q6 (reproducibility) targets "IL6 or a later
    evaluation phase";
  - [`003-phase-IL2.md`](../003-phase-IL2.md): ILASP invocation 1,
    `refused:empty-antecedent`; IL2-Q2 (the bias amendment) targets "IL6 or a
    later evaluation phase";
  - [`004-phase-IL5.md`](../004-phase-IL5.md): `claude` invocation 1,
    `admitted`;
  - [`005-phase-IL3.md`](../005-phase-IL3.md): RIPPER invocation 1,
    `admitted` at 4/5; IL3-Q3 targets IL6;
  - [`006-phase-IL4.md`](../006-phase-IL4.md): AMIE invocation 1 on the
    staffing fixture, `refused:does-not-hold`; IL4-Q4 targets IL6; IL4-D4
    (o): "IL6's AMIE row uses this fixture".
- **The IK6 walk, inspected at `860e651`:**
  - `docs/how-to/learn-rules-commands.md` is a commands page whose
    `<!-- gnd-run expect=N -->` blocks `tools/run_tutorials.py` runs in a
    fresh folder (group `induced`); it starts by copying the packaged
    `gnd/examples/refunds` out of the installed package;
  - `tests/test_ik6_walk.py` pins every written file's SHA-256 under two
    hash seeds (T2), scans pages and outputs for paths and downstream names
    (T3), and IK6's T7 ran the groups under both installed wheel origins;
  - `tests/test_ik6_skill_census.py` and the IK skill census: one row per
    packaged skill file (65), with the phases that changed it.
- **Stale public text found** (author inspection):
  - `docs/reference/ilp-bridge.md` "What the bridge does not establish":
    "The Popper rendering has not been run against a real Popper";
  - `docs/reference/capabilities.md`: "Popper adapter untested against a real
    Popper"; names `export ilp`, `import ilp-rules` only;
  - `docs/reference/cli.md`: rows name `--target popper` only, no
    `mined-rules`;
  - `docs/release-notes.md`: the bridge only;
  - `src/gnd/skills/gnd-export/SKILL.md` and
    `src/gnd/skills/gnd-model-evolve/SKILL.md` (plan §5's two pin sites):
    name `gnd import ilp-rules` only.

## 3. Obligations — inline harvest

| Obligation | Source | Discharged in |
|---|---|---|
| One public anonymized walk replays every adapter's committed run of record and exits as recorded at every step | completion 6; IL6-C1 | §6 walk; T1, T5 |
| The comparison table is a golden; labelled columns: outcome, clauses proposed, import exit, first refusal and its clause index, clauses not evaluated, clauses admitted | IL6-C1 | §6 table; T4 |
| AMIE has its own unlabelled row: rules mined, rules admitted, first refusal | IL6-C1; completion 6 | §6 table; T4 |
| An adapter with no output shows its outcome and empty counts, including `not run (D8)` | IL6-C1 (p2) | Popper invocation 1 (`none`); T4. No `not run (D8)` row exists: D8 was ruled and IL5 ran |
| `ilp-bridge.md` has one section per adapter with its fragment table and refusal names | IL6-C2 | already true for every adapter; T6 checks it |
| `cli.md`, `capabilities.md`, release notes updated | IL6-C2 | §6 docs; T6 |
| The skill census extended, with a check per row; the two pin sites inspected | IL6-C2; §5 | §6 census; T7 |
| API and CLI pins, RF5 entry points, closed-lane and layer checks, RF6 ceiling, installed candidate | IL6-C3; §9 | T8, T9 |
| IL3-Q3 (RIPPER variability before IL6 reads one run) | 005 | IL6-D5 |
| IL4-Q4 (a second AMIE run with `-enstd -minc 1`) | 006 | IL6-D6 |
| IL1-Q6, IL2-Q2 ("IL6 or a later evaluation phase") | 002, 003 | §9: a later evaluation phase |
| The walk runs the refunds example "through every adapter", but AMIE's run is on the staffing fixture | completion 6 vs IL4-D4 (o) | AMIE section on staffing; plan repair at close (IL4-Q5) |
| IL-R1 to IL-R11 and IK-R1 to IK-R12 | §0 | §4 |

## 4. Rules bound to IL6

**Standing rules.**

| Rule | Binding |
|---|---|
| 1 Totality | No new reader. The walk feeds committed learner outputs to the existing readers. |
| 2 Algorithm bound | Unchanged: the imports' own bounds. |
| 3 Validation order | Unchanged. |
| 4 One walk | **One table definition**, in `tools/ilp_comparison.py`, read by the test and by the docs check; the docs table is generated, never retyped. |
| 5 One home | The comparison table's home is `docs/reference/ilp-bridge.md` "Comparing the learners"; the walk links to it. |
| 6 Measurement | The walk's exits come from running it (T1); the table's rows come from the committed evidence and are checked against the walk (T5). |

**Plan rules (IL-R).**

| Rule | Binding |
|---|---|
| IL-R1 | No learner enters any dependency; the walk runs no learner. |
| IL-R2 | Only IL6-D6 (a), if ruled, runs a learner: AMIE invocation 2 through `evidence/IL4/run_amie.py`, unchanged but for the settings constant. |
| IL-R3 | The walk calls the existing commands only. |
| IL-R4 | The table reports GND's import results and the learner's own counts side by side, each labelled with where it came from. |
| IL-R5 | No new download (the AMIE jar is already verified in scratch). |
| IL-R6 | Unchanged. |
| IL-R7 | No wire or golden change outside this spec's list. |
| IL-R8 | The walk reads the refunds example and the staffing fixture only. |
| IL-R9 | Each table row names its invocation and whether it is the run of record; extra rows only for owner-ruled invocations. IL6-D6 (a) fixes its outcome before the run (§6). |
| IL-R10 | T3 scans the shipped outputs, the new page and the walk's written files. |
| IL-R11 | Unchanged; the table shows all-or-nothing outcomes as recorded. |

## 5. Goal

A reader can run one page that takes the refunds example through every
adapter's real, committed learner output and sees each import exit exactly as
it did in its phase. One generated table, kept in `ilp-bridge.md`, compares
the learners. The reference pages, the release notes and the two skill pin
sites describe what the milestone actually shipped.

## 6. Design

### The walk: `docs/how-to/compare-ilp-learners.md` (IL6-D1 (a))

A new commands page in a new `run_tutorials` group, `learners`. It runs in a
fresh folder and copies the packaged example, as the IK6 page does. For each
adapter, in plan order (Popper, ILASP, LLM, rules, AMIE):
1. `gnd export ilp --target T` (the export the learner read; for AMIE,
   `--population` over the staffing fixture);
2. the committed learner output and run record, already in the copied
   example (IL6-D2);
3. the import with the phase's fixed arguments but `--format text`, with
   `expect=` set to the recorded `import_exit`, and its real output shown.

Popper's run of record printed no program, so its section shows the export
and states the outcome; invocations 2 and 3 follow as their own rows
(IL6-D3). Each refusal shown gets its reason and how GND caught it, in one or
two sentences beside the block. A second, short page section explains the
table.

### The replayed outputs (IL6-D2 (a))

Each run of record's learner output and run record is copied byte for byte
into the packaged examples:

| Adapter | Source (evidence) | Shipped as |
|---|---|---|
| Popper inv. 1 | none (no program) | none |
| Popper inv. 3 | `IL1/live/invocation-3/program.pl`, `run.json` | `examples/refunds/learners/popper/` |
| ILASP | `IL2/live/invocation-1/hypothesis.las`, `run.json` | `examples/refunds/learners/ilasp/` |
| LLM (`claude`) | `IL5/live/invocation-1/answer.json`, `run.json` | `examples/refunds/learners/llm/` |
| rules (RIPPER) | `IL3/live/invocation-1/ruleset.txt`, `run.json` | `examples/refunds/learners/rules/` |
| AMIE | `IL4/live/invocation-1/rules.txt`, `reported.json`; the fixture's `model.orm.yaml`, `population.yaml` | `examples/staffing/` and `examples/staffing/learners/amie/` |

T3 asserts each shipped file equals its evidence file byte for byte. The
built wheel and sdist inventories gain these files.

### The comparison table (IL6-D4 (a))

`tools/ilp_comparison.py` reads each listed invocation's committed
`outcome.json` and learner output and writes
`tests/fixtures/ilp_learners/il6/comparison.json` and the Markdown table in
`ilp-bridge.md`. Definitions:
- **clauses proposed:** the clauses in the learner output, as the target's
  own reader parses them; `—` when there is no output;
- **first refusal, clause index:** the refusal name and index from the
  retained import stderr;
- **clauses not evaluated:** for a refusal at clause *k* of *n*, *n − k − 1*;
  0 when admitted; `—` when there is nothing to import;
- **clauses admitted:** the proposal's constraints; 0 when refused;
- **AMIE:** rules mined (lines in `rules.txt`), rules admitted, first refusal
  and rule index; plus, labelled as GND's, how many of the mined rules hold
  (from the import's own count, recomputed by the tool through
  `ilp_amie.count`).
Every row also names the adapter, learner and version, input, invocation,
whether it is the run of record, and "single run".

**Expected rows, fixed before the tool (the corpus, IL6-D11):**

| Adapter | Inv. | Record | Outcome | Proposed | Exit | First refusal | Not evaluated | Admitted |
|---|---|---|---|---|---|---|---|---|
| popper | 1 | yes | `rendering-rejected` / `none` | — | — | — | — | — |
| popper | 2 | no (ruled) | `completed` / `none` | — | — | — | — | — |
| popper | 3 | no (ruled) | `completed` / `admitted` | 1 | 0 | — | 0 | 1 |
| ilasp | 1 | yes | `completed` / `refused:empty-antecedent` | 1 | 3 | `empty-antecedent`, 0 | 0 | 0 |
| llm (claude) | 1 | yes | `completed` / `admitted` | 1 | 0 | — | 0 | 1 |
| rules (wittgenstein) | 1 | yes | `completed` / `admitted` | 1 | 0 | — | 0 | 1 |

| Adapter | Inv. | Record | Outcome | Rules mined | Hold (GND) | Admitted | First refusal |
|---|---|---|---|---|---|---|---|
| amie | 1 | yes | `completed` / `refused:does-not-hold` | 8 | 2 | 0 | `does-not-hold`, rule 0 |

If IL6-D6 (a) is ruled, an `amie 2` row is added with its outcome fixed
before the run (below).

### IL6-D6 (a): AMIE invocation 2, if ruled

`run_amie.py --invocation 2` with `SETTINGS = ("-maxad", "3", "-mins", "1",
"-enstd", "-minc", "1")`, everything else as invocation 1; the script's
`SETTINGS` becomes per-invocation so invocation 1's T9 stays bound to its
own argv. **Expected, stated before the run:** `termination: completed`;
AMIE prints only rules of standard confidence 1, which on the fixture are
rules 2 and 3 of invocation 1 (20/20 and 5/5), so `import: admitted`, 2
rules, with body sizes reported and `body_size_agrees` true. Any other
outcome is recorded as found.

### Docs (IL6-D7 (a))

- `ilp-bridge.md`: the "Comparing the learners" section (the generated
  table); a "live runs" sentence per adapter section linking its phase's
  outcome; the stale "has not been run against a real Popper" line
  replaced by what the runs did and did not show.
- `cli.md`: rows for `--target ilasp|rules|amie`, `--population`, and
  `gnd import mined-rules`.
- `capabilities.md`: the ILP row names all five targets and both imports,
  and drops the stale Popper caveat.
- `release-notes.md`: one entry for the milestone's user-visible additions.
- `docs/tutorials/learn-rules.md`: unchanged (IL6-D7 (a)).

### Skill census and pin sites (IL6-D9 (a))

`.gnd-planning/milestones/ilp-learners/skill-census.md`, one row per
packaged skill file against this milestone's base (the parent of the first
IL1 commit), with `tests/test_il6_skill_census.py` asserting each file
appears once and each changed cell equals git, as IK6's census does. The
two pin sites are edited: `gnd-export/SKILL.md` names the five targets and
`gnd import mined-rules`; `gnd-model-evolve/SKILL.md` names mined-rules
proposals beside ilp-rules ones.

### The checkpoint (IL6-D8 (a))

Once the walk page and the table first run green, and before the docs sweep
and the review, an Artifact page shows the owner the table and each
adapter's walk step with its real output and refusal explanation. Work
continues after the owner's reaction.

## 7. Decisions

| ID | Decision | Options and cost | Proposed |
|---|---|---|---|
| IL6-D1 | The walk's form | **(a) A new commands page,** `docs/how-to/compare-ilp-learners.md`, group `learners`, real output shown; the IK6 page and its goldens untouched. **(b) Extend the IK6 commands page,** which moves its 11 pinned digests and makes one page carry two stories | (a) |
| IL6-D2 | Where the replayed outputs live | **(a) Shipped in the packaged examples** (`refunds/learners/<target>/`, `staffing/`), byte-equal to the evidence, so an installed GND can run the page; the wheel grows by a few KB. **(b) Read from `.gnd-planning` evidence,** which an installed package does not have: the page would run only from a checkout | (a) |
| IL6-D3 | Which invocations | **(a) Each run of record, plus owner-ruled later invocations as marked rows** (Popper 2 and 3; AMIE 2 if D6 (a)). **(b) Runs of record only:** Popper's row is then a rendering failure and the table shows no real Popper import | (a) |
| IL6-D4 | The table | **(a) Generated** by `tools/ilp_comparison.py` from committed evidence into a JSON golden and the `ilp-bridge.md` section; the expected rows of §6 committed first. **(b) Hand-written** Markdown with a test, which can drift | (a) |
| IL6-D5 | IL3-Q3: RIPPER's variability | **(a) Report, don't measure:** every row says "single run, reproducibility not measured"; the rules row adds IL3-F5's note. **(b) Measure** N reruns, which needs a ruling per run and a measurement design | (a) |
| IL6-D6 | IL4-Q4: AMIE invocation 2 with `-enstd -minc 1` | **(a) Run it** (about 0.05 s of mining), outcome fixed above, reported beside invocation 1: the table then has one real AMIE admission. **(b) Don't:** AMIE's only row is a refusal | (a) |
| IL6-D7 | Docs scope | **(a) Reference pages, CLI, capabilities and release notes;** the business tutorial unchanged. **(b) Also a plain-English "which learner found what" section on the tutorial,** written to the tutorial style; more owner review | (a) |
| IL6-D8 | A checkpoint | **(a) Show the table and walk as an Artifact page** once they run green, before the docs sweep. **(b) None** | (a) |
| IL6-D9 | Skill census | **(a) A milestone census and test as IK6's,** and edits at the two pin sites. **(b) Extend the IK census file,** which belongs to a closed milestone | (a) |
| IL6-D10 | Installed candidate | `uv build` into scratch, install each wheel origin into a fresh venv, run the `learners` and `induced` groups with `GND_TUTORIAL_PYTHON`, as IK6's T7. No upload or publication | as stated |
| IL6-D11 | Approval instrument | **Corpus-first** for the table (§6's expected rows committed as the golden, red, before the tool); **the walk's recorded exits** are taken from each `outcome.json` before the page is written; no spec panel | as stated |

## 8. Tests

New files: `tests/test_il6_walk.py`, `tests/test_il6_skill_census.py`.
Fixtures: `tests/fixtures/ilp_learners/il6/`.

| ID | Case | Expected |
|---|---|---|
| T1 | the `learners` group runs (`tools/run_tutorials.py`) | every block exits as its `expect=`; shown outputs equal real output |
| T2 | the walk's written files under `PYTHONHASHSEED` 0 and 1 | digests equal the golden |
| T3 | shipped outputs equal their evidence files; no absolute path, user name or downstream name in the page, the shipped files or the written files | pass |
| T4 | `tools/ilp_comparison.py` output equals `comparison.json` and the `ilp-bridge.md` table | pass |
| T5 | each row's import exit and first refusal equal the walk's and the `outcome.json`'s | pass |
| T6 | docs: every registry target in `cli.md`, `capabilities.md` and `ilp-bridge.md`; one section per adapter naming its refusals; no stale "not been run against a real Popper" | pass |
| T7 | the census: every packaged skill file once; changed cells equal git since the milestone base | pass; seeded faults fail by name |
| T8 | the plan's controls: RF1 CLI pins, RF5, layering, arch, RF6, built inventory, schema sync, the API pins | pass |
| T9 | installed candidate (IL6-D10) | both wheel origins pass `learners` and `induced` |
| T10 | (if IL6-D6 (a)) AMIE invocation 2 replays, as IL4's T9 | pass |

**Gate command:** IL4's gate file list plus the two new test files and
`tests/test_ik6_walk.py`; T9 is run once and recorded, as IK6's T7 was.

## 9. Out of scope for this phase

- measuring any learner's reproducibility (IL1-Q6, IL3-Q3 under D5 (a)) or
  amending a rendering (IL2-Q2): a later evaluation phase;
- the plan repairs (IL3-Q4, IL4-Q5) and the open-question sweep: milestone
  close;
- IL4-Q1 and IL4-Q2 (subtype joins, model binding): close;
- a packaged induction skill (IK6-Q1); any learner in CI; publication.

## 10. Size

Estimate: ~120 lines for `tools/ilp_comparison.py`; ~220 lines of tests; the
walk page ~200 lines; ~12 shipped files; docs edits ~80 lines; the census
~70 rows.

## 11. Approval instrument

IL6-D11.

## 12. Owner gate record

**Owner ruling, 2026-10-28:** "go on with your recs", given in reply to the
draft r1 summary (SHA-256
`b124055cf1c7b45e739321e1e9c8649437448cdd67989c6a59a4be8fb8d1222f`) that
named each proposal. Every decision is ruled as proposed:

| ID | Ruling |
|---|---|
| IL6-D1 | (a) (o) a new commands page, group `learners` |
| IL6-D2 | (a) (o) outputs shipped in the packaged examples |
| IL6-D3 | (a) (o) runs of record plus owner-ruled invocations, marked |
| IL6-D4 | (a) (o) generated table, expected rows committed first |
| IL6-D5 | (a) (o) report, don't measure |
| IL6-D6 | (a) (o) AMIE invocation 2, outcome fixed in §6 before the run |
| IL6-D7 | (a) (o) reference pages, CLI, capabilities, release notes |
| IL6-D8 | (a) (o) an Artifact checkpoint before the docs sweep |
| IL6-D9 | (a) (o) a milestone census and test; the two pin sites edited |
| IL6-D10 | (o) as stated |
| IL6-D11 | (o) corpus-first; no spec panel |

The ruling authorizes exactly one learner run: AMIE invocation 2 under
IL6-D6 (a).

## Implementability notes (author, before the gate)

- **The walk's exits.** T9 of each phase replays its import from the
  committed bytes on `main` today (IL4's gate ran them), so each recorded
  exit is reproducible by the current code. The page uses `--format text`
  where the evidence used `--format json`; only the shown output differs,
  not the exit.
- **Popper invocations 2 and 3** used adapters 2 and 3; the walk's export
  must be the current Popper rendering, which is adapter 3's. Invocation 2's
  `none` needs no import, so only invocation 3 is replayed.
- **The LLM run record** binds the `neutral` export (`binds="neutral"`); the
  walk exports `--target neutral` before that import.
- **Shipping into `src/gnd/examples/`** changes the built inventories and
  may change the RF6 census only if Python files are added; none are.
