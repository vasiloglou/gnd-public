# Phase RC6: documentation of the rule-check workflow

## 1. Status

**Owner-approved (2026-11-06); implementation in progress.** The owner
ruled the step-2 asks over r1 (sha256 `722aa10f…`, commit f6e8a833),
answering "How do you rule on RC6's decisions D1-D6?" with "Approve all as
proposed" (o, 2026-11-06). D4: the approval instrument is this spec, then a
rendered checkpoint before the record. `auto=false`. Prior status (r1):
"Draft, awaiting the owner gate (process-phase step 2)."

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r6,
  sha256 `6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138`,
  approved ([005-plan.md](../005-plan.md)). Completion predicate 6: "the
  rule-check workflow is documented end to end, with a worked example that
  runs under a named test".
- Phases documented: RC1 (`--rule-ids`, `remedy`, version 15), RC2 (acyclic
  extent), RC3 (`--baseline`), RC4 (`--allow-vacuous`), RC5 (`tool-output`).
  Records 006-010. Base: main at `4232d233`.
- Owner feedback on documentation (session memory): business tutorial pages
  show skill prompts and plain results, not commands or Python; user-visible
  work is shown at checkpoints before it is finished.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan §4 RC6 | constraint reference (`remedy`) | M3 |
| plan §4 RC6 | report reference (version 15, `novelty`, `baseline`, `allow_vacuous`) | M4 |
| plan §4 RC6 | population format (source) | done in RC5 (`population-format.md`); M5 links it |
| plan §4 RC6 | CLI help | done in RC1, RC3, RC4 (pinned successors); M5 adds the CLI task-index rows |
| plan §4 RC6 | a how-to: adopting rules on existing data with `--baseline`, worked on a synthetic component graph | M1, M2 |
| plan §4 RC6 gate | `uv run pytest -q tests/test_documentation_tutorials.py` runs the how-to's commands and compares exit codes and key output lines | V2 |
| plan §5 | `gnd-orm-core` constraint reference; report schema descriptions | M3, M4 |
| plan §6 | (none specific) | — |
| RC1-RC5 records, boundaries | what each phase does not establish (version 15 only for the plain snapshot arm; refusals; one reviewer) | stated in M4's limits section |
| project docs gates (NM4 record) | `tools/run_tutorials.py`, `zensical build --strict`, `tools/check_docs.py site`; installed-docs check when an example ships | V2-V4 |
| AGENTS.md | component index for any new module (none expected) | V6 |

## 4. Standing rules bound to this phase

- **Measure, don't assert (6).** Every command and output line on the page
  is executed by the tutorial runner; no output is typed by hand.
- **Frozen variants (7).** Documentation only; the example is data. No
  source file changes, so no report variant can move.

## 5. Goal

A developer wiring `gnd check` into CI on a project that already has
violations can follow one page, end to end, and see each feature do its job:
declared ids and remedies in the output, every loop edge listed, a baseline
that fails the build only for new violations, vacuous rules accepted while
their data is missing, and the population labelled as tool output.

## 6. Design

**M1. Example `src/gnd/examples/rule_check/` (D2), shipped like the other
how-to examples.** `model.orm.yaml`: a component graph with four rules, each
with an `id` and a `remedy`: no import loops (`acyclic`), no component in the
`legacy` area (guarded), every component has an owner (deontic mandatory), and
every release-tagged component ships in a release (left vacuous at first).
`base.population.yaml` (the saved state on main) and `head.population.yaml`
(the change under review), both `source: tool-output` with a `producer`.
Small enough to read: about 12 components; head adds one new loop and fixes
one old edge.

**M2. How-to page `docs/how-to/adopt-rules-with-a-baseline.md` (D1, D3).**
Shape of the existing how-tos (compose-documents): a short story, "Files on
GitHub", a figure, then steps with runnable blocks and their real output:

1. Copy the example; read the rules (`gnd check ... --rule-ids` text: each
   failing rule by its id, with its remedy).
2. Why one run is not enough: a plain check of head fails on violations the
   project already had.
3. Turn on the baseline: `--baseline base.population.yaml`: the new loop is
   `new`, the old violations `standing`, the fixed edge `resolved`, exit 1
   only for the new loop; the JSON `baseline` block.
4. Fix the new loop (an edited head) → exit 0, nothing new.
5. A rule shipped before its data: `--allow-vacuous` exits 0 and still lists
   the vacuous rule.
6. What CI should run, in one line, and what each exit code means.
7. Limits: what version 15 covers and refuses (temporal, redaction,
   reference models; derivation models under `--baseline`), positional keys.

One figure (D3): the head's graph with each violation marked new, standing
or resolved, drawn as SVG in `docs/assets/applications/`.

**M3. Constraint reference.** `gnd-orm-core/references/constraint-reference.md`:
`remedy` in the common fields, beside `rationale` (what to do vs why the rule
exists), with the 1-2000 bound.

**M4. Report reference page `docs/reference/rule-check-report.md`.** Version
15 field by field: `address`, `addressing`, `remedy`, `novelty`,
`row_novelty`, `baseline` (each count), `allow_vacuous`; the acyclic extent
rows and message; the exit bands under `--baseline` and `--allow-vacuous`;
the refusals and their rule ids; how `gnd coverage` treats a version-15
report. Linked from `formats.md` ("Consume the right report").

**M5. Index rows and navigation.** `docs/reference/cli.md`: rows for
`--rule-ids`, `--baseline`, `--allow-vacuous`; `zensical.toml`: the how-to and
the reference page; `formats.md`: a link to the population format's
`tool-output`.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Audience and form of the how-to | **a developer how-to with real commands and output**: the reader is someone wiring a CI gate (as the requester is), not a business reader, so the business-page rule (skill prompts, no commands) does not apply. The story and the figure lead; commands follow **Ruled (o, 2026-11-06): as proposed.** |
| D2 | Where the example's files live | **shipped under `src/gnd/examples/rule_check/`**, copied by the page's first block, like the other how-tos (also checked by the installed-docs check) **Ruled (o, 2026-11-06): as proposed.** |
| D3 | A figure | one SVG of the head graph with new / standing / resolved marked **Ruled (o, 2026-11-06): as proposed.** |
| D4 | Approval instrument | **the spec, then a rendered checkpoint**: before the record, the page is rendered and shown to the owner (session memory: show user-visible work at a checkpoint); no corpus, since the runner already pins every command and output **Ruled (o, 2026-11-06): as proposed.** |
| D5 | Who writes the page | the driving agent, in the house style of the existing how-tos; Fable is reserved for business tutorial pages (session memory), which this is not **Ruled (o, 2026-11-06): as proposed.** |
| D6 | Review over the spec bytes | none; the phase review reads the page against the code **Ruled (o, 2026-11-06): as proposed.** |

## 8. Tests and verification ledger

| # | Obligation | Disposition | Command or evidence | Invalidation |
|---|---|---|---|---|
| V1 | base record | run before any edit | `uv run pytest -q tests/test_documentation_tutorials.py` at `4232d233` | a new base |
| V2 | plan §9 RC6 row | run | `uv run pytest -q tests/test_documentation_tutorials.py` (runs the new page's blocks, exit codes and output) | any page or example edit |
| V3 | docs build and links | run | `uv run python tools/run_tutorials.py docs/how-to/adopt-rules-with-a-baseline.md && uv run zensical build --strict && uv run python tools/check_docs.py site` | any docs edit |
| V4 | shipped example | run | `uv run pytest -q tests/test_documentation_tutorials.py -k installed` and the packaged-example tests that list example domains | example edits |
| V5 | full suite | run, sharded on beast-3 (examples are package data) | failure set equal to the base's | any edit after the run |
| V6 | component index | run at record time | `components_index.py changed --base 4232d233 --strict` | any edit |
| V7 | broad lanes | cadence: not run | milestone close if selected | owner request |

## 9. Out of scope for this phase

New features or flags; changing any output to suit the page; a business
tutorial for the same workflow; the milestone close.

## 10. Size

Plan estimate: about 400 documentation lines and 60 test lines; rule 8
pauses past 600 or 90. This design: about 250 lines for the how-to, 120 for
the report reference, 15 for the constraint reference and index rows, an
example of about 80 data lines and one SVG; tests are the runner's own (the
page's blocks), plus at most the example-domain list.

## 11. Approval instrument

Proposed (D4): this spec, then a rendered checkpoint of the how-to and the
report reference before the phase record.

## Implementability sweep (step 1, author inspection)

- Every behaviour the page shows exists on main at `4232d233` (RC1-RC5).
- The tutorial runner executes `sh` blocks and compares exit codes and
  shown output, with the run directory normalized (`tools/run_tutorials.py`).
- A shipped example is already the pattern (`composition`, `growth`), with
  an installed-docs check that lists example domains.

## Checkpoint (D4)

The how-to and the report reference were built (`zensical build --strict`),
served locally and shown rendered to the owner, with the figure, at
3f47cf01. The owner answered "Do the rendered RC6 pages look right?" with
"Looks good, continue" (o, 2026-11-06).

## Implementation findings (step 3, recorded as found)

- **I1.** The tutorial runner runs blocks under `pipefail`, so the JSON
  block piped through a filter exits with `gnd`'s code (1), not the
  filter's; the page says so.
- **I2.** `tests/test_plan_app_docs.py` holds how-to pages to at most 90
  words per paragraph; the introduction was split.
- **I3.** The page is a new runner group, `rule-check`, in
  `tools/run_tutorials.py`.
