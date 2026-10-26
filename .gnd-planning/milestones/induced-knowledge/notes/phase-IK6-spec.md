# IK6 — end-to-end example, docs, integration

## 1. Status

**r1, awaiting owner review.** No implementation exists. Nothing in this file is
approved. Implementation starts only after the owner rules on §7 and approves
these bytes.

## 2. Provenance

- **Plan:** r4 (SHA-256 `8afbdcbd…cd51a`), §4 IK6, §9 IK6 row, completion
  predicate 6.
- **Base commit B:** `705ad94` (`main`, after PR #42). IK4 and IK5 are merged
  (DAG `{IK4, IK5} → IK6 → close`), and so are IK4-Q2 (PR #43) and IK5-Q1
  (PR #42).
- **Harvest:** one local reader agent read every record (001–009), every phase
  spec, both plan-review dispositions and the agent-review dispositions. The
  author spot-checked its key claims against the files (IK1-Q2 and IK5-Q5 open;
  `gnd-export` has no ILP mention; `gnd-codegen` never changed).
- **Feasibility:** the author ran the whole walk on a scratch copy of the IK5
  corpus at B. Each step exits 0: validate, `measure --labels`, `discover`,
  `export ilp`, `import ilp-rules`, and two `evolve preview` runs (§12).
- **Review:** none has run over these bytes.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| A public anonymized walk exits 0 at every step: labels → measure → discover and learn → evolve preview | plan §4 IK6-C1; predicate 6 | §6 the walk page; T1 |
| Its outputs match committed goldens | IK6-C1; r1 theme F | §6 goldens; T2 |
| Docs, gnd-orm-core references and affected skills updated (gnd-extract, gnd-model-evolve, gnd-codegen, gnd-orm-core) | IK6-C2 | §6 skills and docs; T5 |
| A committed skill-surface census: each packaged skill file, changed or not, and why | IK6-C2; R4-F10 | §6 census; T4 |
| A new test asserts every packaged skill file appears in the census exactly once | IK6-C2 (p2) | T4 |
| Twin identity stays checked by the existing skill sync tests | IK6-C2 | impact list |
| API and CLI pins, RF5 entry points, closed lanes and layers, RF6 ceiling, RF layering and source scans | IK6-C3 | T6 |
| The installed-candidate check for new entry points | IK6-C3; no phase has run it | T7 |
| `api.__all__` and signature pins if public names were added | plan §5 | T6 (IK4 and IK5 added none; verified, not assumed) |
| `docs/` guide and release notes | plan §3 docs home; never touched by a phase | §6 docs |
| IK1-Q2: annotations in text-format `gnd diff` | `002:272`, target "IK6 docs/integration or milestone close" | IK6-D6 |
| IK5-Q5: a real Popper run | `007:229`, "owner's call; IK6 or later" | IK6-D3, IK6-D7 |
| IK4Q2-D3: lift IK5's `references` export refusal "IK6 or later" | `phase-IK4-Q2-spec.md:100` | out of scope (§9); the walk's model is reference-free |
| Census gaps the harvest found: gnd-codegen never edited; gnd-export lacks `export ilp`; gnd-dev-session shows only `measure --populations`; IK1-C5 named gnd-extract *references*, only its `SKILL.md` changed | harvest, §F | §6 skills |
| Standing rules 1–6 | IK-R9 | §4 |
| Privacy: synthetic, anonymized fixtures; no downstream names | IK-R10, IK-R11 | §6 example; T3 |
| No learner in a required lane | plan §7; IK5-D12 | IK6-D3 |

**Inherited, not IK6's** (milestone close; this phase must not claim them):
IK1-Q4, IK1-Q5, IK2-Q2, IK2-Q3, IK2-Q5, IK3-Q2..Q4, IK4-Q3, IK4-Q4, IK5-Q2..Q4,
IK5-Q6, IK4-Q2-Q1, IK4-Q2-Q2, IK4-Q2-R1, and the close protocol itself.
Separately owned: IK1-Q3 (binds only if IK6 bumps the version; it does not),
IK3-Q1, IK3-Q5, and IK4-Q5. IK4-Q5's failing test stays excluded from gates.

## 4. Standing rules bound to this phase

| Rule | Application |
|---|---|
| 1 Totality | The census test parses one committed Markdown table. It refuses a duplicate, a missing or an unknown path by name. No new user-facing loader. |
| 2 Input cap vs algorithm | No new GND work path. The stand-in learner (IK6-D3) is example code: its search is bounded by the example's fixed size and is not a GND command. Argued inapplicable beyond that. |
| 3 Validation order | Unchanged; no command changes. |
| 4 One walk | **The page is the walk.** The tutorial runner executes the page's blocks, and the golden test runs that same page, never a second script. |
| 5 One home | The contract pages (`measure-labels.md`, `discover.md`, `ilp-bridge.md`, `evolution-contract.md`) stay normative. The walk page links them and restates no contract. |
| 6 Measurement | The walk was run at B before this spec (§12). The goldens are captured from real runs, never retyped. |

## 5. Goal

A reader copies one example out of the installed package and runs a single
page. On that page they:
1. score an existing rule against labelled batches (`gnd measure --labels`);
2. discover candidate constraints from a clean batch (`gnd discover`);
3. export the labelled batches for a rule learner, run a learner, and bring its
   rules back (`gnd export ilp`, then `gnd import ilp-rules`);
4. preview both proposals in `gnd evolve`.

Every step exits as the page says, with output the page shows. One step is a
deliberate refusal, explained: a learner claim GND does not reproduce. Nothing
is admitted; admission stays the reader's reviewed act.

## 6. Design

### The example (IK6-D2)

- **Home:** `src/gnd/examples/refunds/`. It ships in the wheel like the other
  examples.
- **Domain:** a shop's refund requests. The data is synthetic and names no real
  organization.
- **Model:** `model.orm.yaml`. YAML, not JSON, so IK4-Q2-Q1 cannot arise. It
  declares no reference populations, because IK5 refuses them.
  - object types: refund, customer, an integer amount, and a manager;
  - fact types: amount, customer, approver, plus one more that discovery can
    find something about;
  - one declared deontic rule for `measure` to score.
- **Batches:** about eight populations under `batches/`. An auditor labelled
  each one `clean` (positive) or `flagged` (negative).
- **Labels:** `labels.json`, a class-mode manifest (`gnd-labels/1`). It binds
  the model and every batch by SHA-256.
- **Values:** Integer, String and Boolean only. No redacted roles. The facts
  bound is respected. All are IK5 export constraints.
- **Learned rule:** the batches are built so that one guarded rule separates
  them. For example: a refund over a threshold has an approver.
- **README:** the example has a short `README.md`, like `expense/README.md`.

### The learn step (IK6-D3)

`refunds/stand_in_learner.py` is the example's own program, not a GND command
and not Popper.
- **Input:** `neutral.json` from `gnd export ilp --target neutral`.
- **Search:** it enumerates a fixed, small clause space: one atom with one
  integer comparison, and two-atom joins. It keeps clauses that cover some
  flagged batch and no clean batch.
- **Output:** a greedy cover, written as `learned.clauses.json`
  (`gnd-ilp-clauses/1`) and `learned.run.json` (`gnd-ilp-run/1`). The coverage
  is the script's own claim, bound to E and to the clauses' digest.
- **Determinism:** fixed ordering throughout, no randomness, and no dependency
  beyond the standard library.

The page says plainly that it is a stand-in, why one is used, and that
`gnd import ilp-rules` re-checks every claim. It links the ILP bridge page for
real learners. A real Popper run stays IK5-Q5 (IK6-D7).

### The page (IK6-D1, IK6-D4)

- **Home:** `docs/tutorials/learn-rules.md`, "Learn rules from labelled data".
  It goes in the Tutorials nav.
- **Runner:** the page joins `tools/run_tutorials.py` as a new group,
  `induced`. That group is added to `test_documented_learning_path` and to both
  wheel-domain lists (`tools/check_installed_docs.py` and its test).
- **Blocks:** each step is a `<!-- gnd-run expect=N output=stdout|stderr -->`
  block with its checked output block. All steps run in the offline lane.

| Step | Command | Exit |
|---|---|---|
| 0 | copy `gnd/examples/refunds` out of the installed package; `gnd validate model.orm.yaml` | 0 |
| 1 | `gnd measure model.orm.yaml --labels labels.json --out measure.json`, read the agreement cells | 0 |
| 2 | `gnd discover model.orm.yaml batches/<clean>.yaml --out discovered.json --report discover-report.json --actor reader --requested-at <fixed>` | 0 |
| 3 | `gnd export ilp model.orm.yaml --labels labels.json --target neutral --out ilp` | 0 |
| 4 | `python refunds/stand_in_learner.py ilp learned` | 0 |
| 5 | `gnd import ilp-rules ... --target neutral --out learned.proposal.json --requested-at <fixed>` | 0 |
| 6 | the same import with a run record that over-claims one batch (a committed `overclaimed.run.json`) | **3**, `coverage-mismatch`, explained |
| 7 | `gnd evolve preview` of `discovered.json` | 0 |
| 8 | `gnd evolve preview` of `learned.proposal.json` | 0 |

- **Prose around each step:** a plain-English sentence for each rule; what the
  cells mean; why step 6 is refused and how GND caught it (it re-evaluated the
  clause and compared sets); and what preview shows. It ends with "what this
  does not establish": coverage agreement is necessary, not sufficient, and
  nothing is admitted.
- **No PyRel.** The page needs no runtime beyond GND. PyRel is not mentioned
  except as an optional link, if at all.

### Goldens (IK6-D4)

- **Stdout:** the page's output blocks pin each step's stdout, through the
  runner's existing comparison.
- **Written files:** `tests/test_ik6_walk.py` runs the page with the runner into
  a temporary directory. It then compares each written file's SHA-256 with
  `tests/fixtures/induced_knowledge/ik6-walk/goldens.json`. The files:
  - `measure.json`;
  - `discovered.json` and `discover-report.json`;
  - `ilp/export.json` (E);
  - `learned.clauses.json` and `learned.run.json`;
  - `learned.proposal.json`;
  - both preview payloads.

  The run directory is normalized to `<run>`, as the runner already does.
- **Repeatability:** the test runs the page twice, with different
  `PYTHONHASHSEED` values, and requires identical digests.

### Skill-surface census (IK6-D5)

- **Home:** `.gnd-planning/milestones/induced-knowledge/skill-census.md`.
- **Rows:** one per file under `src/gnd/skills/` (65 at B, measured at
  execution time). Each row gives:
  - the path;
  - whether the milestone changed it (`IK1`…`IK6`, or `no`);
  - why, or why no change was needed.
- **Test:** `tests/test_ik6_skill_census.py`. It reads `git ls-files
  src/gnd/skills` and the table, and asserts every packaged file appears
  exactly once. A duplicate, missing or unknown path fails by name. It also
  checks that each `changed` cell names a phase.

**Skill edits proposed for IK6** (each minimal, "edits only where behaviour
changed"):

| File | Edit |
|---|---|
| `gnd-export/SKILL.md` | one line: `gnd export ilp` is the ILP bridge, documented elsewhere, not a Lean or Soufflé export |
| `gnd-dev-session/SKILL.md` (line 228) | name `gnd measure MODEL --labels MANIFEST` beside `--populations` |
| `gnd-codegen/SKILL.md` | one line: tool docstrings carry an object type's description `summary` (IK1) |
| `gnd-extract/references/extraction-contract.md` | inspect; add one line only if it states the vocabulary text without IK1's description keys |
| gnd-orm-core, gnd-model-evolve | inspect only; changed in IK1, IK2, IK4, IK5 and IK4-Q2 |

Each edit's pin sites are counted at execution time. They include the packaged
skill inventories (`test_packaged_skills.py`, `test_verification_fixes.py`,
`test_public_built_inventory.py`), the binding-prose tokens and the skill twin
sync.

### Docs beyond the page (IK6-D8)

- `docs/release-notes.md`: one unreleased entry naming the milestone's commands
  and the walk.
- `docs/guides/synthetic-data.md` (or the closest guide): a pointer to the
  page.
- **Reference pages:** `docs/reference/measure-labels.md`, `discover.md` and
  `ilp-bridge.md` each gain a "see it end to end" link.

### Controls (IK6-C3)

| Control | How it is run |
|---|---|
| API pins | `test_public_api.py`, which also checks `api.__all__` is unchanged |
| CLI pins | the `test_rf1_*pins.py` files; no command changes, so no golden moves |
| RF5 entry points | every `test_rf5_*.py` |
| Closed lanes, layers, RF layering and source scans | `test_gnd_arch.py`, `test_rf8_structure.py`, every `test_rf*.py` |
| RF6 ceiling | `test_rf6_*.py`; no model-read change, so no successor entry |
| Installed candidate | `uv run python tools/check_installed_docs.py --out <scratch>`, which builds both wheel origins, installs each and runs every tutorial group, `induced` included. Run once, its `results.json` retained as evidence. It is a slow lane, not a test. |

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IK6-D1 | Approval instrument and checkpoint | **Prose plus checkpoint C1:** approve this spec, then build the example and the runnable page first, run them for real, and show the rendered page with real output before the skills, census and other docs. Matches the owner's checkpoint practice. **Corpus-first:** a fixture corpus with narrated outcomes. It does not fit: the outputs are existing commands' outputs, and the page is the narration. | prose + C1 checkpoint |
| IK6-D2 | The example's domain and home | **New `refunds` example** in `src/gnd/examples/`: synthetic, readable, and shipped in the wheel. **Reuse the IK5 test corpus:** cheaper, but it is a test fixture whose cases exist to fail. | new `refunds` example |
| IK6-D3 | What does "learn" run? | **(a) A stand-in learner script** in the example: deterministic, standard library only, labelled as not Popper. **(b) Committed hand-authored clauses:** no learning happens on the page. **(c) Real Popper:** needs an install; cannot be a required lane (plan §7). | (a); (c) stays IK5-Q5 |
| IK6-D4 | Goldens | **Page output blocks plus a file-digest golden**, run twice with different `PYTHONHASHSEED`. **Output blocks only:** files unpinned. | both |
| IK6-D5 | Census home and the skill edits | **Milestone directory**, with the test above; the four edits in §6. **`docs/development/`:** public, but it is a milestone artifact. | milestone directory; the §6 edits |
| IK6-D6 | IK1-Q2, text-format diff annotations | **Close:** not part of the walk, and it moves RF1 CLI goldens. **IK6:** small, but widens the phase. | milestone close |
| IK6-D7 | IK5-Q5, a real Popper run | **Stays open; owner's call.** Installing Popper was declined (D13 (a)). An optional, non-required page box could show it later. **Now:** needs an install. | stays open |
| IK6-D8 | Docs beyond the page | **Release-notes entry, one guide pointer, three reference links.** **Only the page:** the plan names release notes and a guide. | as proposed |
| IK6-D9 | Base and branch | `claude/ik6-end-to-end` from B = `705ad94` | as stated |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | the page through `run_tutorials.py`, group `induced` | every block's exit and output match; step 6 exits 3 |
| T2 | the written files against `ik6-walk/goldens.json`, twice with different `PYTHONHASHSEED` | equal digests, both runs |
| T3 | privacy: example and page text contain no absolute path, no downstream name and no raw host data; the proposals' induction blocks carry opaque batch ids only | pass |
| T4 | the census: every `git ls-files src/gnd/skills` path once; a seeded duplicate, a missing row and an unknown path each fail by name | pass; three negative cases fail |
| T5 | skill edits: twin sync and inventories pass; each edited line present | pass |
| T6 | the IK6-C3 controls in §6 | pass |
| T7 | the installed-candidate run | both origins pass, `induced` included; `results.json` retained |
| T8 | the stand-in learner, run directly: two runs give byte-identical clause and run files | equal |

**Branch walk:**
- every page step: T1 for exit and output, T2 for written files;
- the refusal branch: step 6 in T1;
- the census test's three refusal branches: T4;
- installed versus checkout origin: T7.

**Verification selection:**
- **Direct:** `tests/test_ik6_walk.py`, `tests/test_ik6_skill_census.py`, and
  `tests/test_documentation_tutorials.py -k induced`.
- **Impact:**
  - all of `tests/test_documentation_tutorials.py` and
    `tests/test_tutorial_output_blocks.py`;
  - the docs link and nav tests;
  - `test_release_docs.py`;
  - `test_packaged_skills.py`, `test_skill_prose_sync.py`,
    `test_public_binding_prose.py`, `test_public_built_inventory.py`,
    `test_public_distribution_runtime.py` and `test_verification_fixes.py`;
  - `test_public_api.py`;
  - every `test_rf*.py` and `test_gnd_arch.py`;
  - `test_ilp_bridge.py`, `test_discover.py`, `test_measure_labels.py` and
    `test_evolve_references.py`.
- **Slow lane, run once:** T7.
- **Excluded:** IK4-Q5's red test.
- **Selection rule:** reduced v6.3. The broad lane is `cadence`.

## 9. Out of scope for this phase

- every close item listed in §3;
- lifting IK5's `references` export refusal (IK4Q2-D3);
- a real learner run, or any learner in a required lane;
- admitting or confirming any proposal;
- new commands, formats or exits;
- the milestone-close record and its four-reviewer review.

## 10. Size

About 10 source lines (runner group, wheel-domain lists). The rest:
- the example: a model, about 8 batches, a manifest, the learner script of about
  120 lines, and a README;
- the page: about 200 lines;
- two tests: about 150 lines;
- the census: about 70 rows;
- about 10 lines of skill and docs edits.

## 11. Approval instrument

Proposed in IK6-D1: this prose, then checkpoint C1. At C1 the owner sees the
rendered page with real output before the rest lands. Changing a C1 output
after the owner reacts is a page edit, not an approval change, unless it moves
an exit.

## 12. Implementability sweep (author inspection, not review)

| Requirement | Finding |
|---|---|
| The walk exits 0 at B | Run on a scratch copy of the IK5 corpus: `validate` 0; `measure --labels` 0 (cells printed); `discover` 0 (proposal written); `export ilp` 0; `import ilp-rules` 0; both `evolve preview` runs 0. |
| A deliberate import refusal | `coverage-mismatch` exists and exits 3 (IK5 corpus cases). |
| Runnable pages with checked output | `tools/run_tutorials.py` runs `gnd-run` blocks, compares shown output, and normalizes the run directory. |
| Installed-candidate check | `tools/check_installed_docs.py` builds two wheels, installs each and runs every runner group. A new group is covered once it is listed. |
| The example ships | examples under `src/gnd/examples/` are in the wheel; the check asserts named domains, so `refunds` is added there. |
| Determinism | Discover and import take `--requested-at`; discover takes `--actor`. Previews of these proposals carry no path (IK4-Q2 T6 golden). Measure and discover reports: whether they contain paths is checked at implementation; the runner normalizes `<run>`. |
| Census countable | `git ls-files src/gnd/skills` gives 65 files at B. |
| Wheel payload cap | `check_installed_docs.py` asserts a payload under 12 MiB. The example adds well under 100 KiB; the current payload is measured at implementation. |
