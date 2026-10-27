# Round 2, reader 2 -- implementability, pins and homes

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`; quoted Markdown link syntax is escaped as `]\(`; headings demoted
one level.

## Digest check
Both digests match:
- `evidence/plan-review-r2/induction-skill-plan.md.snapshot`: 7329cbd2…c3df
- `evidence/plan-review-r2/phase-IS1-spec.md.snapshot`: f81590b0…f938

The `notes/` working copies have the same line counts (454 and 329).

**Verdict: approve-with-fixes**

The spec's edits now come within one regex of a green gate. The one remaining blocking item takes a single-token fix.

## Probe
- `git clone --local` of `0c777e3` into `<scratch>/repo`. I built the spec as written:
  - `gnd-induce/SKILL.md` with the five fenced `gnd` lines, R-a..R-h, the out-route sentences, and the record link;
  - the vendored `labels.schema.json`;
  - the five sibling route sentences, plus the orm-core index row and Reference index row;
  - every §6.3 pin, including D9, `test_public_built_inventory.py:306-312` and both doctor link maps;
  - the AGENTS.md row and the `docs/agents/index.md` row;
  - installer links (`git add`ed), then a commit.
- I did not implement the D8 census pin. My round-1 probe already showed that a pinned variant passes.
- Results:
  - **Gate line 1** (all 17 existing files): 675 passed, 8 failed. 6 of the failures are the unchanged census (this is the intended Control 2 red). The other 2 are N1 and N3 below.
  - **Measured:** 13 new link edges, 224 link occurrences, 67 files, 17 names, 35 snippets (5 from gnd-induce).
  - **Install and doctor:** `gnd install --symlink --project --force` exited 0. `gnd doctor --project` exited 0 with current=17.
  - **Docs:** `uv run --offline --group docs zensical build --strict` reported "No issues found". `tools/check_docs.py site` checked 11417 links.
  - **Distribution lane** (`-m distribution`, built_inventory + distribution_runtime): 36 passed.
  - **Skill-reading tests outside the gate:** 14 files (contributor_preparation, guarded_corpus, acceptance_controls, release_docs, pull_request_policy, plan_app_docs, gnd_arch, …) gave 329 passed. 5 more files gave 127 passed.

## Round-1 status

| Finding | Status | Evidence (spec / plan snapshot lines) |
|---|---|---|
| R2-F1 R-g one-home | resolved | spec 136-141 (the git denial left the set and is pinned by `RECORD_ROUTES`, 198); the probe found every R-a..R-h sentence exactly once in the tree |
| R2-F2 missing pins | resolved | spec 206-217 lists every literal. In the probe, no pin failure remains |
| R2-F3 planning-tree links | resolved | the probe's full `check_document_references` walk finds only the 2 `ilp-learners/evidence/plan-review-r2/*.md` links. Snapshots are `.snapshot` (D19, plan 445) |
| R2-F4 D9 | resolved | spec 219 and plan 435 make D9 mandatory and correct the cost text. The help-option test passes on all 5 lines, including `[--families …]` |
| R2-F5 help test in gate | resolved | spec 254 and 286 |
| R2-F6 lanes and docs command | resolved | spec 98, 258, 279-281, 286, 296 |
| R2-F7 routing regexes | partially resolved | spec 173-196: the sentences now exist and the regexes are tied to them, but one regex cannot match (N1) |
| R2-F8 orm-core table row | resolved in shape | spec 162 and T18 (265). Its cell meanings do not fit the columns (N7) |
| R2-F9 D3 home | mostly resolved | spec 168-171 and 221, plan 233 and 429. The module docstring still conflicts (N8) |
| R2-F10 T9 red-first | resolved | spec 88-94, 220 and 256, plan 434: two controls, full 40-hex SHA, census read by `git show`, `test_t5` kept |
| R2-F11 small items | resolved | spec 19-20 (30 measured), plan 414 (cites `--help`), T17 (264) |

## New findings

- **R2-N1** (blocking; high confidence; self-inflicted): the trigger regex `Every proposal goes to gnd-model-evolve` (spec 193) can never match.
  - `ROUTING_MATRIX` also asserts that the source contains `]\(../gnd-model-evolve/SKILL.md)`, so the sentence has to carry a Markdown link. The routing text then reads "Every proposal goes to [gnd-model-evolve]\(…".
  - The spec wrote the link in words ("gnd-model-evolve, linked as …"), and the regex was written against those words.
  - Reproduced: `test_each_phase4_route_names_its_trigger_and_its_authority_boundary[gnd-induce->gnd-model-evolve]` fails "expected to match 'Every proposal goes to gnd-model-evolve'".
  - The other three new rows pass.
  - Fix: use `Every proposal goes to \[?`?gnd-model-evolve`, or just `Every proposal goes to`. More generally, write regexes against the rendered link form.

- **R2-N2** (completeness; high confidence; self-inflicted): spec 171, 185 and 210 say "14 new edges". Measured: 13.
  - `RELATIVE_LINK_RE` (`test_packaged_skills.py:26`) only captures `]\(../…)`.
  - The orm-core Reference index links `references/labels.schema.json` with no `../`, so that row adds neither an edge nor an occurrence.
  - Occurrences go from 211 to 224.
  - Fix: "plus 13 edges", and drop "the 14th new edge".

- **R2-N3** (hardening; high confidence; self-inflicted, because r2 put this file in the gate): the gate cannot exit 0 on this branch as long as `test_reference_closure_and_declared_bootstrap` stays red.
  - The cause is outside this milestone: 2 broken `plan-review-r1-disposition.md` links in `.gnd-planning/milestones/ilp-learners/evidence/plan-review-r2/` (merged from main). This milestone's own files are clean.
  - It also weakens Control 1: `test_development_scaffold.py` is already red at baseline, so its red under the pin edits shows nothing.
  - Fix:
    - the ledger names this case as inherited, or makes its repair on main a prerequisite;
    - Control 1 and Control 2 evidence are recorded per test id (for example `test_twins_modes_and_generated_links`), not per file.

- **R2-N4** (hardening; medium confidence; self-inflicted): the ledger's claim (spec 281) that "the ordinary gate covers every file that reads the skill inventory" is false.
  - `tests/test_contributor_preparation.py` (`check_current`) globs every `src/gnd/skills/*/SKILL.md`, requires a tracked symlink for each in both roots, and link-checks every skill `.md`. It is directly affected by IS1.
  - `test_guarded_corpus.py` and `test_acceptance_controls.py` also walk the tree.
  - All of them pass on the probe.
  - Fix: add `test_contributor_preparation.py` to gate line 1, and narrow the claim to the files listed.

- **R2-N5** (hardening; medium confidence; self-inflicted): D8's pin is "after #50 and #51 land" (plan 434). That conflicts with D17 (o), "IS1 may land at any time" (plan 443, spec 7), and with disposition theme H, which named only the docs-gaps PR (#50).
  - If #51 (IK5-Q5) is slow or never merges, IS1 is blocked.
  - Fix: name the commit as the merge of the last IK-scoped change that touches `src/gnd/skills` or `skill-census.md`, and state which of #50 and #51 qualify.
  - Also require that the pin and the T13 base are commits reachable from main. The repository uses merge commits, so this is satisfiable.

- **R2-N6** (completeness; high confidence; self-inflicted): two control and lane mismatches.
  - T17 (264) says "control 2 red", but §5 Control 2 (92-94) names only T5 and T9. T17 is a new test, so "unchanged" cannot apply to it. Say T17 is committed before the `docs/agents/index.md` row, or drop its red claim.
  - The D20 lane command (296) also runs `test_public_distribution_runtime.py`, while D20 (plan 446, spec 279) names only `test_public_built_inventory.py`. Align them; both pass.

- **R2-N7** (hardening; medium confidence; self-inflicted): the orm-core row's cells (spec 162) do not match the index columns, which are "Workflow | Enter it when | The claim it emits — and what it never does".
  - Cell 2 as written is a claim ("Scores rules…; host labels are the host's claim").
  - Cell 3 is "Routing only; …", which is the index intro's phrase and not a claim.
  - T18 only checks the trailing pipe, so it would pass.
  - Fix: make cell 2 a trigger (for example "host labels must be scored, rules discovered, or a learner round-tripped"). Make cell 3 "evolve proposals of induced, proposed, advisory constraints, plus measure and discover reports; host labels are the host's claim. It never applies an induced rule". Re-tie the two regexes to those cells.

- **R2-N8** (completeness; medium confidence; pre-existing doctrine): `tests/test_schema_sync.py`'s module docstring says "edit the CANONICAL copy (src/gnd/skills/gnd-orm-core/references/) … never the other way around". orm-core's "Canonical schemas" paragraph says "The two `.schema.json` files…", which is already stale: there are three, counting `steps`.
  - "A docstring note" on the new case (spec 221) leaves the module docstring contradicting D3.
  - Fix: amend the module docstring alongside the report.schema.json asymmetry note, and reword the paragraph's count when the exception sentence is added.

- **R2-N9** (completeness; low confidence; self-inflicted, and closer to reader 1's lens): R-h (spec 137) says the skill never copies host values into a file it writes. The Popper exception in R-b and the learner rule (131, 147-149) has the skill write a `gnd-ilp-run/1` record.
  - That record holds the covered example ids (`ilp-run.schema.json` `coverage[].covered`), and those come from the host populations.
  - Fix: either state that example ids are not "host values" for R-h, or name the run record as R-h's one exception.

Not findings (confirmed):
- 13 new edges resolve inside the tree.
- No `FROZEN_SKILLS` member is touched. `FROZEN_SKILL_BASELINE` is computed at import, so the existing frozen check is vacuous and T13 adds real coverage.
- `ABSOLUTE` and `DOWNSTREAM` are importable from `test_ik6_walk.py`.
- `test_t5`'s strings survive the sibling edits.
- The spec's "077f46e..45c8603 changes nothing under src/tests/tools/docs/AGENTS.md" is verified empty.
- Effect of the inherited baseline failure: it does affect the proposed gate (N3). Nothing else in the gate depends on it.

Self-inflicted findings: 8 of 9 (N1–N7 and N9). Only N8 comes from pre-existing doctrine. Severity has fallen: 1 blocking, against 4 in round 1.
