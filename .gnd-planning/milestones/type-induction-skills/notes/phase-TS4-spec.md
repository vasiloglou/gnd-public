# Phase TS4 spec: the `gnd-model-multivalued` skill

## 1. Status

**r1, delegated approval (auto=true) `(d4)` 2026-11-05** (SHA-256 of the r1
bytes before this mark:
`2add491ba0677eba5dbc5945d2df98fa127c23dcf5f5e43f53aa9a098c5c385e`).
Authorization: the owner invoked `process-milestone type-induction-skills
auto` in this session; this is the coordinating agent's ruling under that
delegation, not an owner reading of the spec. Scope: TS4 as written; D2–D6
ruled as proposed after the §8 implementability sweep. Instrument: this prose
(D6); no spec panel. Budget: the two paid runs of D1 and nothing else.
Compatibility: no `gnd` output changes (TS-R1). Paid calls are outside auto:
the owner answered the separate question "What do you authorize?" with "TS4
run + TS3 re-run (Recommended)", i.e. two paid Claude Code runs with Sonnet
5.5, about $1 in all (D1, owner-ruled). No implementation file existed at r1.

## 2. Provenance

- Plan: [type-induction-skills-plan.md](type-induction-skills-plan.md) r1,
  approved `(a1)`; §0, §2.3 `gnd-model-multivalued`, §4 TS4, §5, §6, §9 TS4
  row, §10 TS-D3, TS-D6, TS-D11.
- TS2 record (refuted premise P2: a `functional` shapes verdict can never be
  accepted, so a shapes file holds `many-to-many` or `skip` only) and
  `docs/reference/discover.md` "Type judgements".
- TS3 [record](../004-phase-TS3.md) and [spec](phase-TS3-spec.md): D8 (the
  recorder gains a TS4 entry), D7 (the multi-valued route waits for TS4),
  open questions TS3-Q1 (shared turn loop) and TS3-Q3 (re-record TS3).
- Base: main at `1668a58ebea71c4ddc090552d3708cd9c1c181bc` (PR #90 merge):
  17 packaged skills, 68 tracked skill files, 218 relative links.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan O2, §2.3, TS4 heading | a packaged skill, a variant of the `rai-orm-from-schema` conventions, turns the `multi_valued` groups of an evidence file into a `shapes` judgements file | §6.1–§6.3 |
| Plan TS4-C1 (as TS3-C1), O11, O12 | ships, installs, AGENTS.md row, every pin moved as one decision | §6.4; T1–T7 |
| Plan TS4-C2 (as TS3-C2), TS-R6 | handoff names `gnd discover ... --shape-judgements` and `gnd evolve preview`, never `apply`; route test | §6.2 step 5; T8 |
| Plan TS4-C3 (as TS3-C3), TS-R5, O6 | forbids reading the population; states the disclosure rule; prose test | §6.2 steps 1, 4; T10 |
| Plan TS4-C4 | states its relation to `rai-orm-from-schema` (the convention borrowed; `gnd import rai-orm` unchanged) and links the spanning-uniqueness reference instead of copying it | §6.2 "Convention"; T11 |
| Plan TS4-C5, TS-D6 | a recorded run over the fixture's multi-valued attribute yields `many-to-many`, accepted by the CLI, preview exits 0 | §6.5, §6.6; T13–T15; D1 |
| Plan §2.3 "`functional` only when the user confirms the extra values are errors, which then routes to fixing the population" | refuted by TS2 P2 (no `functional` verdict exists): the confirmed-errors answer becomes `skip` plus the instruction to fix the population | §6.3 S4; refuted premise P4 (§12) |
| Plan §2.3 "states that the spanning uniqueness carries no functional claim" | one sentence in the skill | §6.2; T11 |
| TS3 D7 `(a3)` | the multi-valued route from `gnd-judge-fact-types` waits for TS4 | §6.4 (one sentence, one link, one routing row) |
| TS3 D8 `(a3)`, TS3-Q1 | TS4 extends `record_judge_sessions.py`, reusing its loop, no third copy | §6.6; D5 |
| TS3-Q3 | re-record TS3 over its current bytes, now owner-authorized | §6.7; D1 |
| Plan §6 "skill-count pins" | re-measure counts on main at spec time; record the literal moved | §6.4 (measured at `1668a58e`) |
| Plan §9 TS4 row | "TS3 pins plus `tests/test_model_multivalued_skill.py`" | §8 |
| Carried | P1–P3 plan repairs, §2.2 key (close); CT4 DateTime, YAML/UTF-16 tracebacks, `test_rf7_structure.py` red at base (maintenance); TS3-Q2 (CLI owner) | not owned |

## 4. Standing rules, bound

- **TS-R1:** no `src/gnd` module changes; only skill prose. T16 runs the TS2
  file unchanged.
- **TS-R2:** the skill decides; its rules are prose. The 10% and 90% lines
  are skill conventions, not CLI rules.
- **TS-R3:** the skill writes `evidence_sha256` over raw bytes; the recording
  proves the CLI accepts it (T14).
- **TS-R4:** handoff ends at `gnd evolve preview` (T8).
- **TS-R5:** the workspace holds no population; rationales carry no value
  and, when values are hidden, no number standing alone (the TS3 F1 lesson).
- **TS-R6:** only the judgements file is new and every input is unchanged
  (per-file SHA-256, T15).
- **TS-R7:** no module, no lane, no RF6 change; no downstream name (T17).
- **TS-R8:** links from the installer (T12).
- **Standing rules 1–6:** as TS3 §4: totality of the recorder (every run
  writes `results.json`); no algorithm; refusals stated in order before any
  verdict; no policy walk; one home per rule (T9: S1–S4 appear only in this
  skill); every pin measured.
- **"A declared branch with no case":** S1–S4 each have a fixture group; the
  ask branch is observed as the file's absence after turn 1.
- **"One reviewer mistaken for a panel":** the record says "one reviewer is
  one reviewer".

## 5. Goal

A user with a model and one type-evidence file asks their agent how to model
the multi-valued attributes. The agent, following `gnd-model-multivalued`,
reads the evidence and the model, never the population, decides
`many-to-many` or `skip` for every `multi_valued` group, asks when the
evidence cannot decide, writes a `shapes` judgements file the CLI accepts, and
hands off to `gnd discover --shape-judgements` and `gnd evolve preview`.

## 6. Design

### 6.1 Files

- `src/gnd/skills/gnd-model-multivalued/SKILL.md` (new, about 130 lines).
- `src/gnd/skills/gnd-judge-fact-types/SKILL.md`: step 2's `multi_valued`
  sentence links the new skill (TS3 D7).
- `src/gnd/skills/gnd-orm-core/SKILL.md`: one workflow-index row; the two
  vendored-schema rows name both skills.
- `tools/record_judge_sessions.py`: per-skill fixture, canaries, skill path,
  gate and turns; the loop unchanged (D5).
- `tests/fixtures/type-judgements/multi-valued/` (new; D2): `model.orm.yaml`,
  `items.population.json`, `answer-key.json`, `README.md`.
- Recordings: `evidence/TS4/recording/` and `evidence/TS3/recording-2/`.
- `tests/test_model_multivalued_skill.py` (new); TS3's test gains the
  re-recording check (§6.7).
- Pins (§6.4), AGENTS.md row, `docs/agents/index.md` row, installer links.

### 6.2 The skill's procedure

Frontmatter `name: gnd-model-multivalued`; the description names the trigger
(model the multi-valued groups of the fact-type family), the input, the
output (`shapes` judgements file) and what it is not (duplicates, authoring,
applying, reading the population).

**Convention (TS4-C4).** The `rai-orm-from-schema` dialect's schema-to-ORM
convention reads a junction table, whose rows pair two keys and neither key
alone is unique, as one many-to-many fact type with a uniqueness spanning
both roles. A generic attribute row ("an item has an attribute with a
value") where an entity holds several values is the same shape. This skill
applies that convention to evidence; `gnd import rai-orm` is unchanged and
the skill imports nothing. The spanning uniqueness is linked in
`constraint-reference.md` "Internal uniqueness", not copied; it says each
pair is recorded once and states nothing functional.

1. **Inputs, population rule** (as TS3): model and evidence; never the
   population; user-offered values never go into the file.
2. **Refuse before judging** (as TS3): wrong `format`, `model_sha256` not
   the model's digest, `truncated_groups` above 0.
3. **Eligible groups:** exactly `multi_valued`, in evidence order; none →
   say so, write nothing. `proposed`, `shape_match`, `over_budget` belong to
   `gnd-judge-fact-types` (linked).
4. **Decide** each by §6.3; no file until every eligible group has a
   verdict. **Write** `shapes.judgements.json` (default, never over an
   existing file): `kind: shapes`, raw-byte `evidence_sha256`, `judge.skill`
   `gnd-model-multivalued`, one verdict per group with `group`, `generic`,
   `verdict` (`many-to-many` or `skip`), no `of`, a one- or two-sentence
   rationale citing ids, model words and the rule; when `show_values` is
   false, no number standing alone in `agent` or a rationale.
5. **Hand off:** `gnd discover MODEL POPULATION --families fact-type
   --type-evidence-in EVIDENCE --shape-judgements JUDGEMENTS --out ...
   --report ... --actor ... --requested-at ...`, then `gnd evolve preview
   ... --policy additive`; the exit-3 guidance as TS3 (reword, stop on
   `judge.skill`, new evidence on stale data). Never applies, never touches
   git.

### 6.3 Decision rules (one home: this skill)

For each `multi_valued` group, over its candidates; "distinct pairs" is
`rows - exact_repeats`:

- **S1, already induced.** A candidate whose `origin.generic` is the group's
  `generic` and `origin.same_attribute` is true: `skip`; the attribute is
  already modelled by that fact type. The CLI refuses `many-to-many` there.
- **S2, already held.** Otherwise, a candidate whose `overlap.pairs` is at
  least 90% of the distinct pairs: `skip`, naming it; its facts are already
  modelled (a shapes file has no `duplicate`).
- **S3, junction convention.** Otherwise, when `truncated` is 0, no
  candidate has `overlap.pairs` above 0, and at least one entity in ten has
  several values (`multi.entities × 10 ≥ support`): `many-to-many`. Exact
  repeats become the uniqueness's counterexamples and are said, not
  counted, in the rationale.
- **S4, ask.** Anything else: a partial pair overlap; truncated candidates;
  or fewer than one entity in ten with several values, which may be entry
  errors. The answer is the verdict: `many-to-many`; or `skip`, and when the
  user says the extra values are errors, tell them to correct the
  population and make new evidence, since a shapes file cannot declare the
  attribute functional.

`signature_equal` is false for every `multi_valued` candidate (the family
computes no signature for those groups) and is evidence neither way. `null`
overlaps do not block S3: such a candidate's other role is not of the
value's kind, so it cannot hold these pairs (D3).

### 6.4 Pins and routes (measured at `1668a58e`)

| Pin | At base | After |
|---|---|---|
| `test_packaged_skills` names, files, links | 17 / 68 / 218 | 18 / 69 / measured |
| `ROUTING_MATRIX` | TS3 rows | plus `gnd-orm-core → gnd-model-multivalued`, `gnd-model-multivalued → gnd-model-evolve`, `gnd-judge-fact-types → gnd-model-multivalued` |
| `RECORD_ROUTES`; denials | TS3 entries | plus `'gnd-model-multivalued/SKILL.md': 'never touches git'`; `'never applies a proposal'` |
| `test_verification_fixes`, `test_install`, `test_doctor_uninstall` (names, both link maps), `test_marketplace_plugins:25`, `test_development_scaffold:141` | 17 / 68 | 18 / 69 |
| `test_public_built_inventory:315-321` (distribution, run once) | 68 / 17 | 69 / 18 |
| `test_public_distribution:315`, `test_release_acceptance:77` (distribution, edited, run at close) | 17 | 18 |
| `test_public_packaged_invocation_guards.MEASURED_SNIPPETS_PER_SKILL` | 11 skills | plus `'gnd-model-multivalued': n`, measured |
| `test_development_scaffold:178` (218) | 218 | measured |
| IL6, IK6 censuses | pinned | unchanged |

Routes: orm-core row ("the fact-type family's evidence has `multi_valued`
groups to model" / "a `shapes` judgements file …; it never reads the
population and never applies a proposal"); AGENTS.md by the installer
workflow; `docs/agents/index.md` row ("Model multi-valued induced attributes
| `gnd-model-multivalued` | `shapes` judgements file | `gnd discover
--shape-judgements`, `gnd evolve preview` | 3 a refused verdict").

### 6.5 Fixture and answer key (D2)

`tests/fixtures/type-judgements/multi-valued/`, round two of
`item_has_attribute` over 24 items after one applied many-to-many induction.
The model has `item_has_attribute_induced_0` ("Item is tagged
AttributeValue", `induced_from` naming round one's attribute, digest
`a1f80da9…`, measured from a real round-one run) and a hand-modelled
`item_has_label` (Item, Label), each with a spanning uniqueness. Measured on
a prototype (scratch, unset mode):

| Group | Attribute | Evidence | Verdict | Rule |
|---|---|---|---|---|
| g0 | `tag-m5q1` | multi 24 of 24; `induced_0` origin `same_attribute` true | `skip` | S1 |
| g1 | `alias-m5q2` | multi 24 of 24; `item_has_label` holds every pair | `skip` | S2 |
| g2 | `role-m5q3` | multi 12 of 24; one exact repeat; no shared pair | `many-to-many` | S3 |
| g3 | `code-m5q4` | multi 1 of 24; no shared pair | asked; scripted "entry error" → `skip` | S4 |

With these verdicts `gnd discover --shape-judgements` exits 0 (one proposal,
support 36 of 37; `judged_skip` 3) and preview `--policy additive` exits 0.

### 6.6 The recorder (D5)

`record_judge_sessions.py` keeps one loop. Each `SKILLS` entry declares its
fixture, canaries, skill path, accepted gate (spec heading and mark), turns
and agreement. The TS4 entry: T1 `/gnd:gnd-model-multivalued model.orm.yaml
evidence.json`; T2 "In group g3 the one item's second value is an entry
error: skip it, and the population will be fixed. Write the file." The ten
checks are unchanged. `--authorized-by` for either entry may name this spec
once its mark records D1.

### 6.7 The TS3 re-recording (D1)

After TS4's review fixes, one run of the `judge-fact-types` entry, unchanged
turns, into `evidence/TS3/recording-2/`; the first recording is kept as
history. If every check holds, the TS3 test binds `recording-2` (current
skill bytes) and keeps a check that `recording/` stays intact; if not, the
failure is recorded and T14 stays on the first recording.

## 7. Decisions

| ID | Question | Readings | Proposal |
|---|---|---|---|
| D1 (TS-D6) | Paid runs | (a) one TS4 run and one TS3 re-run, Sonnet 5.5, owner-authorized; (b) TS4 only; (c) none | (a), owner's answer quoted in §1 |
| D2 | Fixture home | (a) a new `multi-valued/` fixture; TS3's stays byte-identical, so its recording still binds; (b) extend `round-two/`: one fixture for TS5, but TS3's evidence and recording break | (a); TS5 decides how its how-to joins them |
| D3 | `null` overlaps and S3 | (a) do not block (the candidate cannot hold these pairs); (b) ask, as TS3 R3: every entity type with only differently-typed fact types would always be asked | (a) |
| D4 | The 10% line | (a) S3 needs one entity in ten with several values, else ask; (b) any multi entity → many-to-many: a single entry error is then proposed as a shape | (a) |
| D5 | Recorder | (a) extend the TS3 recorder by entries (TS3 D8), loop unchanged; TS3-Q1 stays at two copies; (b) merge both recorders: edits the PL18-pinned tool | (a) |
| D6 | Approval instrument | (a) prose with §6.5's key; (b) corpus first | (a) |

## 8. Tests and verification selection

| # | File | Case | Expected |
|---|---|---|---|
| T1–T7 | TS3's pin files | 18 names, 69 files, links, routes, records, denials, snippets, scaffold, marketplace | red before the skill; pass after |
| T8 | `test_model_multivalued_skill.py` | handoff names `--shape-judgements` and `gnd evolve preview`; no fenced apply; every sentence naming apply denies it | pass; seeded apply line fails |
| T9 | same | S1–S4 key clauses appear only in this skill; "No file is written until" | pass; seeded copy fails |
| T10 | same | population rule, three refusals, no-number rule | pass |
| T11 | same | the convention paragraph names `rai-orm-from-schema`, says `gnd import rai-orm` is unchanged, links `constraint-reference.md`, says "states nothing functional" | pass |
| T12 | installer | install, doctor | exit 0; `current=18` |
| T13 | same | the fixture's evidence gives §6.5's statuses, multis, overlaps and origins; no canary in model or evidence | pass |
| T14 | same | the recording: every check true; binds the recomputed evidence; discover 0; preview 0; verdicts equal the key; flipped key fails | pass |
| T15 | same | no canary, no population or apply call in the recording; only the judgements file new | pass; seeded canary fails |
| T16 | `test_discover_type_judgements.py` | unchanged | pass |
| T17 | same | no absolute path or downstream name | pass |
| T18 | `test_judge_fact_types_skill.py` | re-recording bound (§6.7) | pass |
| T19 | docs | zensical strict; check_docs | exit 0 |

Gate command 1 is TS3's list plus `tests/test_model_multivalued_skill.py`;
commands 2–5 as TS3 (zensical, check_docs, install, doctor); the
distribution inventory once; ruff. Full default lane and the other
distribution files: the close.

### Implementability sweep

| Requirement | Met as written? |
|---|---|
| Fixture statuses and overlaps | Yes: measured on the prototype (§6.5), not reasoned (the TS3 I1 lesson). |
| S1 observable | Yes: `origin.same_attribute` true on g0; the CLI refuses `many-to-many` there. |
| S2 distinct from S3 | Yes: g1 overlap 48 of 48; g2 0. |
| S4 observable | Yes: file absent after turn 1. |
| Recorded `many-to-many` accepted | Yes: prototype exit 0, preview exit 0. |
| Plan's `functional` route | Not as written (P2): `skip` plus "fix the population" (P4). |
| TS3 re-run binds current bytes | Yes if run after every edit to `gnd-judge-fact-types/SKILL.md` (§6.7). |

## 9. Out of scope

The how-to, `discover.md` amendments and release notes (TS5); any CLI
change; shapes beyond binary many-to-many; more than the two authorized runs.

## 10. Size

About 130 skill lines, 40 recorder lines, a four-file fixture, 200 test
lines, pin edits across 12 files.

## 11. Approval instrument

Prose (D6), delegated.

## 12. Implementation findings

- **P4 (plan §2.3, refuted premise):** the skill cannot write `functional`;
  TS2 removed it (P2). The plan's "routes to fixing the population" is kept
  as S4's instruction with a `skip` verdict.
- **I1 (§6.5, after review F3):** the fixture gains g4 (`note-m5q5`, every
  item two values, `item_has_label` holding half its pairs): S4 by partial
  overlap, scripted answer `skip`. Without it no group exercised S3's
  no-overlap clause. The four approved verdicts are unchanged; the key adds
  g4, and the scripted second turn answers g4 as well. With the five
  verdicts discover exits 0 (`judged_skip` 4) and preview exits 0.
- **I2 (§6.3, after review F1, F2):** a `null` overlap on a candidate whose
  other role is redacted now stops S3 (D3 narrowed, not reversed); S1 reads
  the induced fact type's uniqueness and routes a single-role one to
  `gnd-model-evolve` or a corrected population.
- **I3 (§6.4):** links 218 → 228, not "measured nine": S1's new route
  cites `gnd-model-evolve` a second time.
- **I4 (§6.6, after review F4):** `no_population_access` also fails on any
  tool path outside the workspace and plugin copy, or any input naming the
  repository or home directory. It applies to the TS3 re-recording too.
