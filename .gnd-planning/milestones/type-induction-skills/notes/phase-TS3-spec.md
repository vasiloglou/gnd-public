# Phase TS3 spec: the `gnd-judge-fact-types` skill

## 1. Status

**r1, draft, awaiting the owner gate.** `auto=false`. Drafted 2026-11-05 on
the owner's "go ahead" typed in this session after the TS2 merge. That
go-ahead selects drafting only; it approves no bytes. No implementation file
has been created. The gate rules §7 D1–D9, including the paid recorded run
(D1, plan TS-D6), which is ruled here or not at all.

## 2. Provenance

- Plan: [type-induction-skills-plan.md](type-induction-skills-plan.md) r1,
  approved `(a1)` 2026-11-05 without plan review; §0, §2.3, §4 TS3, §5, §6,
  §9 TS3 row, §10 TS-D5, TS-D6, TS-D11.
- TS2: [record](../003-phase-TS2.md) and [spec r1](phase-TS2-spec.md), merged
  by PR #89 as `b4ef8cbf`. TS2's D7 `(a2)` moved vendoring the two schemas to
  this phase, "beside the first skill that links them".
- Base: main at `b4ef8cbfee048351f7d6bac7704b21cdaf93bcb5`. Read there:
  - the contract the skill consumes: `docs/reference/discover.md` "Type
    evidence" and "Type judgements" (`:176-290`);
    `src/gnd/type-evidence.schema.json`; `src/gnd/type-judgements.schema.json`;
  - the packaged-skill surface: `src/gnd/skills/` (16 skills, 65 tracked
    files); `gnd-orm-core/SKILL.md` workflow index and "Canonical schemas";
  - the pins: `tests/test_packaged_skills.py:19-22,62-67,178-206`,
    `test_verification_fixes.py:17-18`, `test_install.py:51`,
    `test_doctor_uninstall.py:47,96-134`, `test_marketplace_plugins.py:25`,
    `test_development_scaffold.py:141`, `test_public_built_inventory.py:315-321`,
    `test_public_distribution.py:315`, `test_release_acceptance.py:77`,
    `test_public_packaged_invocation_guards.py:131-134`,
    `test_schema_sync.py` (three `SCHEMA_PAIRS`), `test_public_agents_skill_table.py`,
    `test_skill_prose_sync.py`, `test_public_workflow_claim_routes.py`;
  - the two skill censuses: `tests/test_ik6_skill_census.py` (reads git at a
    pinned commit) and `tests/test_il6_skill_census.py` (reads `git ls-files`
    live and asserts 65; §6.4);
  - the recorder precedent: `tools/record_skill_sessions.py` (bound to the
    PL18 gate record and the course example);
  - the unexecuted IS1 spec ([phase-IS1-spec.md](../../induction-skill/notes/phase-IS1-spec.md)
    §6.2–§6.3), whose pin table this spec re-measures rather than copies.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan O1, §2.3, TS3 heading | a packaged skill turns an evidence file and the model into a duplicates judgements file | §6.1, §6.2 |
| Plan TS3-C1, O11, O12 | ships, installs, AGENTS.md row, every pin moved as one decision | §6.4; T1–T7 |
| Plan TS3-C2, TS-R6 | handoff names `gnd discover ... --duplicate-judgements` and `gnd evolve preview`, never `apply`; route test | §6.2 step 6; T8, T9 |
| Plan TS3-C3, TS-R5, O6 | forbids reading the population; states the disclosure rule; prose test | §6.2 steps 1, 5; T10 |
| Plan TS3-C4, TS-D6 | a recorded run whose judgements file the CLI accepts and whose verdicts match an answer key held apart from the skill's inputs | §6.5, §6.6; T13–T15; D1, D2 |
| Plan §2.3 decision rules | origin equal → duplicate; high pair overlap → duplicate; equal signature alone is no evidence; thin evidence → ask the user | §6.3; D3 |
| Plan TS-R8 | links from the installer only | §6.4; T12 |
| Plan TS-D5, TS2 D7 `(a2)` | vendor both schemas into `gnd-orm-core/references` here | §6.4; T11; D5 |
| Plan §6 "skill-count pins collide with IS1" | re-measure counts on main at spec time; record the literal moved | §6.4 (measured at `b4ef8cbf`) |
| Plan §9 TS3 row | "Skill ships and routes; recorded run accepted"; the named pin files plus `tests/test_judge_fact_types_skill.py` | §8 ledger |
| TS2 record, boundary | "No skill exists yet. The judgements files in the tests are written by hand" | discharged for duplicates by §6.5; shapes stays TS4 |
| TS2 record, open questions | P1, P2, §2.2 group key: plan repairs at the close | carried, not owned |
| TS1, TS2 records | CT4 DateTime kind, YAML and UTF-16 tracebacks | carried to maintenance, not owned |

## 4. Standing rules, bound

- **TS-R1 (default parity):** TS3 changes no module under `src/gnd` other
  than skill files. The two vendored schemas are copies, not read by the
  runtime. No `gnd` output can change; T16 confirms by running the TS2 file
  unchanged.
- **TS-R2 (the CLI decides nothing):** the skill decides; the CLI is
  untouched. The skill's rules (§6.3) are prose for an agent, not code.
- **TS-R3 (digest binding):** the skill writes `evidence_sha256` over the
  evidence file's raw bytes (§6.2 step 5); the recorded run proves the CLI
  accepts what it writes (T14).
- **TS-R4 (induction proposes):** the skill never applies; its handoff ends
  at `gnd evolve preview` (T8).
- **TS-R5 (disclosure):** the skill reads the model and the evidence only;
  the recorded workspace holds no population file (§6.5), so the run cannot
  read one. Rationales cite group ids, fact type ids and counts, never a
  value (T10, T15).
- **TS-R6 (skills write only their judgements file):** prose rule plus the
  recorded workspace diff: after the run, only the judgements file is new
  (T15).
- **TS-R7 (layering, query policy, anonymity, approval):** no `src/gnd`
  module, so no lane or RF6 change. No downstream application is named
  (T17 reuses the IK6 walk's anonymity patterns). `auto=false`.
- **TS-R8 (installer-owned links):** §6.4; T12.
- **Standing rule 1 (totality):** inapplicable to prose; the recorder (§6.6)
  is total over its declared inputs: every run writes a results row,
  including a failed one.
- **Standing rule 2 (algorithm bound):** inapplicable; no new algorithm.
- **Standing rule 3 (validation order):** the skill's procedure states its
  refusals in order (§6.2 steps 1–3), before any verdict.
- **Standing rule 4 (one walk):** inapplicable; no policy over element kinds.
- **Standing rule 5 (one home):** the judgements format's normative home
  stays `docs/reference/discover.md` and the runtime schema; the skill links
  them and copies no rule. Its decision rules (§6.3) have one home, the
  skill; T9 checks each appears once in the packaged tree.
- **Standing rule 6 (measure):** every pin in §6.4 was measured at
  `b4ef8cbf`; the after-values are fixed by measurement at implementation.
- **Failure class "a declared branch with no case":** each refusal and each
  decision rule in §6.2–§6.3 names its test; the fixture (§6.5) has one
  group per rule, including the ask branch.
- **Failure class "a rule made unfalsifiable by its fixtures":** the answer
  key is fixed in this spec (§6.5) before any run; the ask branch is checked
  by the absence of the judgements file after the first turn, not by
  reading the agent's prose.
- **Failure class "a single reviewer mistaken for a panel":** the record
  says "one reviewer is one reviewer".

## 5. Goal

A user with a model and one type-evidence file asks their agent to judge the
duplicates. The agent, following `gnd-judge-fact-types`, reads the evidence
and the model, never the population, decides `distinct` or `duplicate of X`
for every eligible group, asks the user when the evidence cannot decide,
writes a `duplicates` judgements file that `gnd discover` accepts, and hands
off to `gnd discover --duplicate-judgements` and `gnd evolve preview`.

## 6. Design

### 6.1 Files

- `src/gnd/skills/gnd-judge-fact-types/SKILL.md` (new, about 170 lines),
  one file.
- `src/gnd/skills/gnd-orm-core/references/type-evidence.schema.json` and
  `type-judgements.schema.json` (new, vendored copies; D5).
- `src/gnd/skills/gnd-orm-core/SKILL.md`: one workflow-index row, two
  Reference-index rows, and the "Canonical schemas" paragraph reworded for
  the two vendored-from-runtime copies (D5).
- `tools/record_judge_sessions.py` (new, about 150 lines; D8).
- `tests/fixtures/type-judgements/round-two/` (new; D2): `model.orm.yaml`,
  `items.population.json`, `answer-key.json`, `README.md`.
- The recording under
  `.gnd-planning/milestones/type-induction-skills/evidence/TS3/recording/`.
- `tests/test_judge_fact_types_skill.py` (new, about 200 lines).
- Pin edits (§6.4), AGENTS.md row, `docs/agents/index.md` row.

### 6.2 The skill's procedure

Frontmatter `name: gnd-judge-fact-types`; the description names the trigger
("judge whether induced fact-type groups duplicate existing fact types"),
the input (an evidence file from `gnd discover --type-evidence` and the
model), the output (a `duplicates` judgements file) and what it is not
(multi-valued groups; applying anything; reading the population).

1. **Inputs and the population rule.** Read the model and the evidence file.
   Never open, list or ask for the population, even when it is in the
   directory; everything the judgement may use is in the evidence. If the
   user offers values, do not write them into the file.
2. **Refuse before judging.** Stop and tell the user, writing nothing, when:
   the evidence's `format` is not `gnd-type-evidence/1`; its
   `model_sha256` is not the SHA-256 of the model file given; or
   `truncated_groups` is above 0 (the CLI refuses that evidence, TS2 D5).
3. **Eligible groups.** Exactly the groups with status `proposed`,
   `shape_match` or `over_budget`, in evidence order. If there are none, say
   so and write nothing. `multi_valued` groups are not this skill's; say they
   need a `shapes` file (TS4 adds the skill and its route).
4. **Decide each group** by the rules of §6.3, in order. A group the rules
   cannot decide is put to the user as a question naming its id, its counts
   and its candidates. **No file is written until every eligible group has a
   verdict.**
5. **Write the file** at the path the user names (default
   `duplicates.judgements.json` beside the evidence; never over an existing
   file): `format: gnd-type-judgements/1`, `kind: duplicates`,
   `evidence_sha256` computed over the evidence file's raw bytes
   (`shasum -a 256` or `sha256sum`; never over a re-serialized copy),
   `judge: {skill: gnd-judge-fact-types, agent: <the agent or model name>}`,
   and one verdict per eligible group with `group`, `generic`, `verdict`,
   `of` (only on `duplicate`) and a `rationale` of one or two sentences that
   cites group ids, fact type ids, readings from the model and counts from
   the evidence, never an attribute name or value. The vendored schema is
   linked; its rules are not restated.
6. **Hand off.** Give the user the command to run, with the same model,
   population, `--min-support` and disclosure setting that produced the
   evidence:
   `gnd discover MODEL POPULATION --families fact-type --type-evidence-in EVIDENCE --duplicate-judgements JUDGEMENTS --out proposal.json --report report.json --actor ACTOR --requested-at TIMESTAMP`,
   then `gnd evolve preview MODEL proposal.json --workspace WORKSPACE --records RECORDS --out preview.json --policy additive`
   (the options `gnd evolve preview --help` lists at `b4ef8cbf`). Exit 3
   means a verdict or the binding was refused: read the message, fix the
   judgements file, never edit the evidence. Admission is the user's
   reviewed `gnd evolve apply` through
   [gnd-model-evolve](../gnd-model-evolve/SKILL.md); this skill never
   applies a proposal and never touches git.

### 6.3 Decision rules (one home: the skill)

For each eligible group, over its candidates:

- **R1, origin.** A candidate whose `origin.same_attribute` is true:
  `duplicate` of that candidate. (`distinct` would be refused, TS2 D4.)
- **R2, full pair overlap.** Otherwise, a candidate whose `overlap.pairs` is
  at least 90% of the group's distinct pairs (`rows - exact_repeats`):
  `duplicate` of it; when two qualify, the higher overlap, then the first.
- **R3, no shared facts.** Otherwise, when every candidate with a non-null
  `overlap.pairs` has 0 and none has a true `same_attribute`: `distinct`.
  The rationale says the verdict rests on the absence of shared facts, which
  review at `gnd evolve preview` can overturn (a synonym attribute with
  disjoint entities would pass here).
- **R4, ask.** Anything else (a partial pair overlap; only `null` overlaps,
  so no candidate is comparable): ask the user. Readings may inform the
  question; **an equal signature alone is evidence neither way.**
- When `show_values` is true, the attribute value may inform the judgement
  but may not appear in the file unless the user asks for it under a mode
  that allows values.

The 90% line is a skill convention, not a CLI rule (TS-R2); D3.

### 6.4 Pins and routes (measured at `b4ef8cbf`)

| Pin | At base | After (fixed by measurement) |
|---|---|---|
| `test_packaged_skills.EXPECTED_SKILL_NAMES`, `== 16`, the test name `..._fifteen_named_skills` and its "fifteen/sixteenth" message | 16 | 17; the name and message state no spelled-out number and cite this plan |
| `EXPECTED_SKILL_FILES` / `EXPECTED_SKILL_FILE_COUNT` in `test_packaged_skills`, `test_verification_fixes`, `test_install`, `test_doctor_uninstall` | 65 | 68 (skill + two schemas) |
| `EXPECTED_RELATIVE_LINKS`, `EXPECTED_RELATIVE_LINK_COUNT` | 212 | measured |
| `ROUTING_MATRIX` | 9 rows | plus `gnd-orm-core → ../gnd-judge-fact-types/SKILL.md` and `gnd-judge-fact-types → ../gnd-model-evolve/SKILL.md`, regexes matching only the new sentences |
| `RECORD_ROUTES`; the denials map | 14; 7 | plus `'gnd-judge-fact-types/SKILL.md': 'never touches git'`; plus `'never applies a proposal'` |
| `test_doctor_uninstall` name set, both link maps | 16 | 17 |
| `test_install.EXPECTED_SKILL_NAMES` | 16 | 17 |
| `test_marketplace_plugins:25`, `test_development_scaffold:141` | 16 | 17 |
| `test_public_built_inventory:315-321` (distribution lane) | 65 / 16 | 68 / 17 |
| `test_public_distribution:315`, `test_release_acceptance:77` (distribution lane, not run, §8) | 16 | 17 |
| `test_public_packaged_invocation_guards.MEASURED_SNIPPETS_PER_SKILL`, `MEASURED_EXECUTABLE_SNIPPETS` | 10 skills; 29 | plus `'gnd-judge-fact-types': n`; measured. `discover` and `evolve` already parse; `GROUPED_COMMANDS` unchanged |
| `test_schema_sync.py` | 3 pairs | a separate case for the two runtime-canonical copies (D5), with the docstring stating the exception |
| `test_il6_skill_census.py` | `git ls-files` live, `== 65` | pinned to the ilp-learners close merge `7818be1be242896420991b456f22144a9bf4768e` for `ls-files` and `log`, dropping the uncommitted-edit credit (D4) |
| `test_ik6_skill_census.py` | pinned at `33827e2` | unchanged |

`test_public_distribution_runtime.py` (59 files, 177 links) is already stale
at base and in the distribution lane; TS3 does not touch it.

`.claude/skills/gnd-judge-fact-types` and `.codex/skills/gnd-judge-fact-types`
come from `uv run gnd install --symlink --project --force`, then `git add`.

Routes (D7): the `gnd-orm-core` workflow-index row ("the fact-type family's
evidence must be judged for duplicates" / "a `duplicates` judgements file;
it never reads the population and never applies a proposal"); AGENTS.md row
by the installer workflow; `docs/agents/index.md` row ("Judge induced
fact-type duplicates | `gnd-judge-fact-types` | `duplicates` judgements file
| `gnd discover --duplicate-judgements`, `gnd evolve preview` | 3 a refused
verdict"). Out-routes in the skill: `gnd-model-evolve`; `gnd-orm-core`
references `provenance-and-modality.md` and the two vendored schemas.

### 6.5 Fixture and answer key (D2)

`tests/fixtures/type-judgements/round-two/`: the second round of a generic
`item_has_attribute` (Item, AttributeName, AttributeValue), after one
applied induction. The model holds:

- `item_has_attribute_induced_0`, applied from the attribute `size` in round
  one, with `provenance.induced_from` naming it and its reading renamed by
  review ("Item has Size");
- `item_has_colour` (Item, Colour), a hand-modelled binary over a string
  value type.

The population (attribute names are canaries in no model text) gives four
eligible groups above `--min-support`:

| Group | Attribute | Evidence shape | Expected verdict | Rule |
|---|---|---|---|---|
| A | `size` again | `shape_match` with `induced_0`, `same_attribute` true | `duplicate` of `item_has_attribute_induced_0` | R1 |
| B | colour data under another name | `proposed`; pairs with `item_has_colour` equal to all its pairs | `duplicate` of `item_has_colour` | R2 |
| C | a new attribute | `shape_match` with `induced_0`, `same_attribute` false, every pair overlap 0 | `distinct` | R3 |
| D | another name | `proposed`; pairs with `item_has_colour` about half its pairs | asked; the scripted answer makes it `distinct` | R4 |

`answer-key.json` holds `{group id: verdict, of}` for A–D. It lives only in
the fixture directory and is never copied into the recording workspace. The
group ids are fixed when the fixture's evidence is first computed and are
recorded in the key.

### 6.6 The recorded run (D1, D6, D8)

`tools/record_judge_sessions.py --authorized-by GATE --model NAME --out DIR`:

1. Builds the evidence: `gnd discover` over the fixture, unset mode, no
   `--show-values`, with `--type-evidence`.
2. Copies into a fresh workspace only `model.orm.yaml` and `evidence.json`.
   The plugin directory holds only `.claude-plugin` and `src/gnd/skills`,
   as `record_skill_sessions.py` does.
3. Runs Claude Code (`claude --print --plugin-dir ... --permission-mode
   acceptEdits --model NAME`) with declared turns:
   T1 `/gnd:gnd-judge-fact-types model.orm.yaml evidence.json`;
   T2, declared before the run: "Group D is a different attribute from
   every candidate: distinct. Write the file." After T1 it records whether a
   judgements file exists.
4. Keeps the stream-json per turn, redacted with the existing helpers
   (imported, not copied), the workspace's file list before and after, the
   judgements file, and `results.json`.
5. Checks, outside the agent, and writes each into `results.json`:
   no judgements file after T1 (R4 asked); one after T2; schema-valid;
   `gnd discover ... --duplicate-judgements` over the real population exits
   0; verdicts equal the answer key; `gnd evolve preview --policy additive`
   exits 0; no canary attribute name in any kept file; no `evolve apply` and
   no population path in any tool call; only the judgements file is new.
6. Refuses to start without `--authorized-by` naming this phase's gate
   record. It never retries silently: every run is kept.

The run is one paid session on the owner's Claude Code account, made only
under D1's ruling. The test file replays the committed recording offline;
no test calls a model.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 (plan TS-D6) | Recorded run | (a) one run with a model named here, paid, on the owner's account, authorized by this gate; (b) prose pins only: TS3-C4 recorded "not met" | (a), model `sonnet` (Claude Sonnet 5.5) unless the owner names another; one run, kept whatever it shows |
| D2 | Fixture home (refuted premise P3) | (a) TS3 authors `tests/fixtures/type-judgements/round-two/` with its answer key; TS5's how-to reuses it; (b) wait for TS5, as TS3-C4's "TS5 fixture" says: TS3 would then precede its own input | (a) |
| D3 | Decision rules and the 90% line | (a) R1–R4 as §6.3; (b) never ask, always decide: fewer turns, but a partial overlap becomes a guess | (a) |
| D4 | The live IL6 census | (a) pin `test_il6_skill_census.py`'s git reads to `7818be1` (the ilp-learners close merge), as IK6 already is; (b) add rows to the closed milestone's `skill-census.md`: edits a closed record; (c) retire the test | (a) |
| D5 | Vendored schema direction | (a) the runtime files stay canonical; the `gnd-orm-core` copies are vendored, with their own sync case and the paragraph reworded; (b) move the runtime files under `src/gnd/schema/` and make the skill copies canonical, as `SCHEMA_PAIRS` does: touches TS1/TS2 code paths, docs links and the wheel inventory | (a) |
| D6 | Disclosure of the recorded run | (a) unset mode without `--show-values`: value-free evidence, the strictest case; (b) `internal`: the judge sees names | (a) |
| D7 | Sibling routes | (a) the `gnd-orm-core` row, AGENTS.md and `docs/agents/index.md` only; the multi-valued route waits for TS4, since a link to a skill that does not exist fails; (b) also a `gnd-model-evolve` sentence | (a) |
| D8 | Recorder | (a) a new `tools/record_judge_sessions.py` importing the redaction helpers, which TS4 extends with its own entry; (b) generalize `record_skill_sessions.py`: touches a tool pinned to the PL18 gate | (a) |
| D9 | Approval instrument | (a) this prose, with §6.5's answer key as the narrated expected outcome; (b) a committed corpus first | (a) |

## 8. Tests and verification selection

| # | File | Case | Expected |
|---|---|---|---|
| T1 | `test_packaged_skills.py` | frontmatter reads back; names, files, links, counts; the two routing rows; `RECORD_ROUTES`; denials; orm-core indexes every skill | red before the skill (control); pass after |
| T2 | `test_verification_fixes.py` | file set and count | red before; pass after |
| T3 | `test_install.py`, `test_doctor_uninstall.py`, `test_development_scaffold.py` | 17 names, 68 files, link maps, scaffold count | red before; pass after |
| T4 | `test_public_agents_skill_table.py` | AGENTS.md row | red before the row; pass after |
| T5 | `test_marketplace_plugins.py` | 17 | red before; pass after |
| T6 | `test_public_packaged_invocation_guards.py`, `test_public_packaged_command_help.py` | per-skill count; every `gnd` snippet parses and its options exist | count red before; pass after |
| T7 | `test_il6_skill_census.py` | pinned (D4); its seeded-fault cases still fail by name | red with the skill and the unpinned test; pass after |
| T8 | `test_judge_fact_types_skill.py` | the handoff names `--duplicate-judgements` and `gnd evolve preview`; the skill has no `gnd evolve apply` line; "never applies a proposal" | pass; a seeded copy with an apply line fails |
| T9 | same | R1–R4 each appear once in the packaged tree, only in this skill; "No file is written until every eligible group has a verdict" appears | pass; a seeded second copy fails by name |
| T10 | same | the population rule and the no-value rationale rule appear; step 2's three refusals appear | pass |
| T11 | `test_schema_sync.py` | each vendored copy is byte-identical to its runtime file | pass; a one-byte edit fails |
| T12 | installer | `uv run gnd install --symlink --project --force`; `uv run gnd doctor --project` | exit 0 each |
| T13 | `test_judge_fact_types_skill.py` | the fixture: its evidence (computed in the test) gives groups A–D with the §6.5 statuses, candidates and overlaps, and the answer key's ids | pass; this is the check that the key matches the data |
| T14 | same | the committed recording: `results.json` rows all true; the judgements file binds the evidence the test recomputes; `gnd discover` over the fixture with it exits 0; preview exits 0; verdicts equal the key | pass; a key with one verdict flipped fails |
| T15 | same | the recording's kept files hold no canary name; no tool call names the population or `evolve apply`; only the judgements file is new | pass; a seeded canary fails |
| T16 | `test_discover_type_judgements.py` | unchanged | 73 passed (TS-R1) |
| T17 | `test_judge_fact_types_skill.py` | no absolute path, run directory or downstream name in the skill or the recording (patterns imported from `test_ik6_walk.py`) | pass; a seeded path fails |
| T18 | docs | `uv run zensical build --strict`; `uv run python tools/check_docs.py site` | no issues; exit 0 |

Honest limit: T8–T10 check sentences, which cannot fail when an agent
ignores them. T14–T15 are evidence for one run, one model and four groups.

### Selection ledger

| Obligation | Disposition | Command or evidence | Input boundary | Invalidation |
|---|---|---|---|---|
| TS3-C1..C3; T1–T12, T16, T17 | run | gate command 1 | `src/gnd/skills`, `tests`, AGENTS.md, `docs/agents/index.md`, `.claude/skills`, `.codex/skills` | any change there |
| TS3-C4; T13–T15 | run | gate command 1 over the committed recording; the recording itself once, under D1 | the fixture, the recording, `tools/record_judge_sessions.py` | any fixture or skill change after the recording: the recording is then stale and the record says so |
| T18 | run | gate commands 2, 3 | `docs/`, AGENTS.md | any docs change |
| distribution-lane pins | `test_public_built_inventory.py` run once at the gate; `test_public_distribution.py:315`, `test_release_acceptance.py:77` edited, run at the close | `uv run pytest -q -m distribution tests/test_public_built_inventory.py` | built wheel | any packaged file change |
| full suite, broad historical lanes | not run; cadence: the close | none | all | an edit outside the listed paths |

Proposed gate:

```text
uv run pytest -q tests/test_packaged_skills.py tests/test_verification_fixes.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_marketplace_plugins.py tests/test_public_agents_skill_table.py tests/test_public_packaged_invocation_guards.py tests/test_public_packaged_command_help.py tests/test_public_workflow_claim_routes.py tests/test_public_packaged_import_skill_routes.py tests/test_skill_prose_sync.py tests/test_solve_successors.py tests/test_ik6_skill_census.py tests/test_il6_skill_census.py tests/test_schema_sync.py tests/test_discover_type_judgements.py tests/test_judge_fact_types_skill.py
uv run zensical build --strict
uv run python tools/check_docs.py site
uv run gnd install --symlink --project --force
uv run gnd doctor --project
```

### Implementability sweep

| Requirement | Can some implementation meet it as written? |
|---|---|
| The skill computes `evidence_sha256` correctly | Yes: a shell digest of the file; T14 checks the CLI accepted it. |
| R4 is observable without reading prose | Yes: the file's absence after T1 is a filesystem fact. |
| Group C is `shape_match` with `same_attribute` false | Yes: TS1's origin rule compares the group's digest with the fact type's `induced_from`; in unset mode digests are present (D6). |
| Group B is `proposed`, not `shape_match` | Yes: `item_has_colour`'s Colour value type differs from the generic value type, so the signatures differ. T13 confirms before the run. |
| The run cannot read the population | Yes: it is not in the workspace or the plugin directory. The agent could still search the disk; T15 scans tool calls for the fixture path. |
| TS3-C4 "over the TS5 fixture" | Not as written: TS5 comes after TS3. Refuted premise P3; D2. |
| The 17th-skill slot | IS1 (approved, unexecuted) competes for it; if it lands first, the counts here rebase on main and the record states the literal moved. |
| The IL6 census | Not without D4: adding any skill file fails it. |

## 9. Out of scope for TS3

- `gnd-model-multivalued`, the `shapes` route and its recording (TS4).
- The how-to, `discover.md` amendments and release notes (TS5).
- Any change to `gnd discover`, its schemas' content or its exits.
- Recording more than one run or more than one model.
- Plan repairs P1, P2, P3 and the §2.2 key (the close).

## 10. Size

About 170 lines of skill prose; one orm-core row, two reference rows and a
reworded paragraph; two vendored schemas; about 150 lines of recorder; a
fixture of four files; about 200 lines of new test; about 70 lines of pin
edits across 12 test files. No `src/gnd` module changes.

## 11. Approval instrument

Prose (D9). The owner approves this spec, the §6.5 answer key and D1–D9; D1
also authorizes the one paid run with the model it names.

## 12. Implementation findings

None yet.
