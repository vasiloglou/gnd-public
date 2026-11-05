# Type induction skills

r1, 2026-11-04. **Draft, awaiting the owner's plan gate.** Milestone:
`type-induction-skills`. Phase prefix `TS`.
Sources: the [composition-and-type-induction close](../../composition-and-type-induction/007-milestone-close.md)
question sweep (CT-close-Q1, CT-close-Q2), its CT4 record ruling D5
([005-phase-CT4.md](../../composition-and-type-induction/005-phase-CT4.md)),
and the owner's rulings on those two questions, relayed to this planning
session on 2026-11-04 (below, `(o0)`).
Inspection baseline: `549ebb9`, the tip of
`claude/process-milestone-composition` (PR #86, **open, not merged**). This
plan is based on that branch, not on main, because the code it changes
(`src/gnd/discover/types.py`) exists only there. TS1 does not start until
PR #86 merges; its spec then rebases onto the merge commit and re-reads the
cited lines (TS-D1).
Plan authorship is not approval. No phase has a spec approval; no code is
written. `auto=false`.

**Revision history and owner rulings.**

- **`(o0)` 2026-11-04, relayed, not quoted.** The owner reviewed the CT close's
  open questions and ruled that (1) the fact-type family's duplicate detection
  should move to a skill, a semantic duplicate judge (answers CT-close-Q1), and
  (2) modelling multi-valued attributes should be done by a skill that is a
  variant of the `rai-orm-from-schema` dialect skill, proposing for example a
  many-to-many fact type with a spanning uniqueness instead of a failing
  single-role uniqueness (answers CT-close-Q2). The ruling reached this
  session through the session that started it; the owner's exact words are
  not in the repository, and the plan gate should quote them (TS-D0).
  It approves no bytes.
- **r1:** first draft. No review has run over it.

## Problem and completion predicates

**Duplicates (CT-close-Q1).** `gnd discover --families fact-type` reports a
group as a shape match, and does not propose it, when an existing fact type
has the same role players under `gnd.refscheme.role_player_signature`
(`discover/types.py`, `existing` and `match`). Every group from one generic
fact type has the same players (the entity type and the generic value
type), so once one induced fact type is applied, every later group from that
generic fact type is a shape match. The family proposes once per generic
fact type across runs. A signature says two fact types *could* hold the same
facts; it cannot say they *mean* the same thing.

**Multi-valued attributes (CT-close-Q2).** A group in which some entity has
several distinct values is counted `multi_valued` and not proposed (CT4 D5),
because the single-role uniqueness the induced envelope sits on would fail.
Such an attribute (tags, phone numbers, authors) is a legitimate many-to-many
fact type with a uniqueness spanning both roles; today nothing proposes it.

**The split the owner ruled.** Judgement moves to skills; the CLI stays
deterministic. The CLI supplies evidence (signatures, attribute digests,
readings, row and overlap counts), reads a skill's written verdicts as a
digest-bound input, checks them against the data, and renders the evolve
operations. It never decides meaning.

The milestone can close when:

1. `gnd discover --families fact-type --type-evidence EVIDENCE` writes a
   value-free `gnd-type-evidence/1` file listing every group the family
   formed (proposed, shape-matched, multi-valued, below support, mixed type,
   redacted), with the deterministic evidence named in §2.1. `--out` and
   `--report` bytes are identical with and without the option (TS1).
2. `gnd discover ... --duplicate-judgements J` and `--shape-judgements S`
   read verdicts bound by digest to one evidence file, refuse stale,
   incomplete, contradicted or value-leaking verdicts (exit 3, nothing
   written), and render: a group judged `distinct` is proposed even when its
   signature matches; one judged `duplicate` is reported against the named
   fact type even when its signature does not match; a multi-valued group
   judged `many-to-many` is proposed as a binary fact type with a uniqueness
   spanning both roles. Every rendered proposal passes
   `gnd evolve preview --policy additive` (exit 0) and applies (TS2).
3. Packaged skill `gnd-judge-fact-types` turns an evidence file and the model
   into a duplicate-judgements file, reading no population and printing no
   value the mode forbids (TS3).
4. Packaged skill `gnd-model-multivalued`, a variant of the
   `rai-orm-from-schema` dialect's schema-to-ORM conventions, turns the
   multi-valued groups of an evidence file into a shape-judgements file (TS4).
5. Without the three new options, every `gnd discover` output, with or
   without `--families fact-type`, is byte-identical to `549ebb9` (or the
   PR #86 merge commit) by a recorded table, except stated usage lines
   (TS1, TS2; TS-R1).
6. A how-to walks one generic fact type through two rounds (one applied
   induction, then a distinct attribute, a duplicate and a multi-valued
   attribute) with both skills; docs gates exit 0 (TS5).
7. Focused gates, independent diff reviews, the question sweep and a PR are
   recorded. Owner acceptance is separate.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| TS-R1: The deterministic family keeps its default | Without `--type-evidence`, `--duplicate-judgements` and `--shape-judgements`, the family groups, matches by role-player signature, counts `multi_valued` and writes exactly what it writes at the baseline. The seven default families are untouched. Parity is a recorded before/after table over the CT4 parity cases plus the IK4 table, captured with the CT4 script. |
| TS-R2: The CLI decides nothing semantic | Evidence is computed; verdicts are read. The CLI never infers "same meaning". Where a verdict and the data disagree (a `functional` verdict on a multi-valued group, a `duplicate` of a fact type the entity does not play), the CLI refuses, it does not repair. |
| TS-R3: Verdicts are digest-bound evidence | A judgements file names the SHA-256 of the evidence file's raw bytes, which binds the model and population digests the evidence names. A different digest, a missing group, an extra group or a repeated group exits 3 before anything is written. Judgements are inputs the caller writes, so their digest is over raw bytes (CT-R4). |
| TS-R4: Induction proposes; review admits | Every rendered constraint keeps `source: induced`, `status: proposed`, `modality: deontic`. A judged proposal adds `provenance.judgement` naming the evidence and judgements digests, the verdict and the skill that wrote it. Admission is a reviewed `gnd evolve apply`. No row moves. |
| TS-R5: Disclosure | Evidence is value-free: digests, counts, opaque row ids, model ids and model readings. The raw attribute value appears only as `values_allowed(--show-values)` decides, the CT4 rule, and never under `customer`. A judgement's free-text `rationale` is refused (exit 3) when it contains any raw attribute value of the population and the mode does not allow values, so a skill cannot launder a value through prose. The skills read the evidence file and the model, never the population. |
| TS-R6: Skills judge, they do not write models | Both skills write only their judgements file. They never edit the model, the evidence or a proposal, and never run `gnd evolve apply`. The handoff is `gnd discover` with the judgements, then `gnd evolve preview`. |
| TS-R7: Layering, query policy, anonymity, approval | New code in lane `discover` (`tools/gnd_layers.json`), zero new allowances. Model reads through `ModelIndex`; RF6 counted reads stay under their ceiling, measured in each spec. Downstream applications unnamed. `auto=false`. |
| TS-R8: Installer-owned links | Discovery links for new packaged skills come from `uv run gnd install --symlink --project --force`, never by hand (AGENTS.md). |

Each phase spec binds every rule above and every rule in
`.codex/skills/process-phase/references/standing-rules.md`, by name or with a
one-sentence argument that it does not apply.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| CT close `007`: predicate 4, findings R3-F1, R3-F2, sweep rows CT-close-Q1, Q2, CT4-Q1 | The two questions; the once-per-generic limit; D5 as a delegated amendment |
| CT4 record `005`: D5, review F3, F10 | Why multi-valued groups are counted |
| `src/gnd/discover/types.py` at `549ebb9`: `propose` (`existing`, `match`, `skipped`, the `multi_valued` branch, the budget, `group_sizes`), `_value_digest`, `generic_declarations` | The family to extend |
| `src/gnd/discover/service.py:200,311,315,371,397`; `src/gnd/commands/discover.py:11,85-131,146-148` | Where options and the report key enter |
| `src/gnd/discover.schema.json` (`fact_type_proposals`) | The report shape that must not change |
| `src/gnd/refscheme.py` `role_player_signature` | The deterministic shape key, kept as evidence |
| `src/gnd/disclosure.py` `values_allowed`; `docs/reference/disclosure.md`; `tests/test_disclosure_mode.py` (site table, T15 case map, T26 arithmetic) | Disclosure (TS-R5) |
| `docs/reference/discover.md` "Fact-type family" and Limits | The contract to amend |
| `src/gnd/rai_import.py` (bounded `rai-orm-from-schema` dialect; admitted inline families uniqueness and mandatory) | What the dialect variant may borrow |
| `src/gnd/skills/gnd-orm-core/SKILL.md:11-13`, `gnd-model-from-code/SKILL.md:30-35`, `tests/test_public_packaged_import_skill_routes.py` | How the dialect is referenced: an import route, not authoring |
| `src/gnd/skills/gnd-orm-core/references/constraint-reference.md`, `provenance-and-modality.md`, `constraint-inference.md` | Spanning uniqueness and provenance vocabulary the skills link to |
| `src/gnd/schema/orm-meta.schema.json` `$defs.fact_type.properties.provenance` (open object) | Where an induced fact type can record its origin |
| `tests/test_packaged_skills.py` (16 names, file inventory), `test_public_agents_skill_table.py`, `test_install.py`, `test_doctor_uninstall.py`, `test_marketplace_plugins.py`, `test_skill_prose_sync.py`, `test_public_packaged_invocation_guards.py`, `test_public_packaged_command_help.py`, the skill census tests | Pins a new packaged skill moves (TS3, TS4) |
| `induction-skill` plan r3 (approved 2026-10-27, IS1 not executed) | Precedent for a packaged skill; competes for the 17th slot |
| `tests/test_rf1_cli_pins.py`, `tests/fixtures/rf1-pins/` | `discover` help and exit goldens |

The `rai-orm-from-schema` skill itself is not in this repository; GND holds
only its import (`gnd import rai-orm`). "Variant" is therefore read as a GND
packaged skill that applies that dialect's schema-to-ORM conventions to
attribute rows (TS-D3).

A `gnd coverage MODEL` census counts experiment claims; it does not show
whether a discover family or a skill exists, so none is run.

### Obligations harvested

| ID | Obligation (source) | Kind | Owner |
|---|---|---|---|
| O1 | Judge duplicates semantically, by a skill (`(o0)` 1; CT-close-Q1) | ruled | TS2, TS3 |
| O2 | Model multi-valued attributes by a skill that is a variant of the `rai-orm-from-schema` dialect skill (`(o0)` 2; CT-close-Q2) | ruled | TS2, TS4 |
| O3 | Example shape: many-to-many fact type with a spanning uniqueness (`(o0)` 2) | ruled | TS2-C5 |
| O4 | The CLI stays deterministic and supplies evidence: signatures, attribute digests, readings, row counts (brief) | requested constraint | TS1; TS-R2 |
| O5 | The deterministic family's default unchanged (brief) | requested constraint | TS-R1; TS1-C6, TS2-C8 |
| O6 | Disclosure rules kept: no raw values unless the mode allows (brief; CT-R6, CT-D13) | requested constraint | TS-R5; TS1-C4, TS2-C6, TS3-C3 |
| O7 | Follow AGENTS.md (brief) | requested constraint | §8 |
| O8 | Proposals pass `preview --policy additive` (CT-R5, CT4-C4) | inherited | TS2-C7 |
| O9 | The once-per-generic limit documented (`discover.md`) is lifted only under judgement | inherited claim | TS2, TS5 |
| O10 | CT4-Q1 salt or omit the attribute digest | carried question | not owned; TS-D7 asks whether to fold it in |
| O11 | A new packaged skill "is a decision with a plan behind it" (`test_packaged_skills.py`) | inspected pin | this plan; TS3, TS4 |
| O12 | AGENTS.md skill table names every packaged skill | inspected pin | TS3, TS4 |
| O13 | Proposal budget (CT4 F2, close R2-1) covers judged groups too | inherited | TS2-C7 |
| O14 | Redacted roles stay redacted (CT4 F4) | inherited | TS2-C5 |

## 2. Contract proposal and product behavior

### 2.1 Evidence (TS1)

`--type-evidence PATH` (needs `--families fact-type`; a usage error, 64,
otherwise) writes `gnd-type-evidence/1`, schema
`src/gnd/type-evidence.schema.json`:

- `model_sha256`, `population_sha256` (raw bytes, as the report binds them),
  `min_support`, `show_values` (as decided);
- `groups`: one entry per group, in the family's own order, keyed by
  `{generic, attribute_sha256}`. Each carries `status`, the family's
  deterministic outcome (`proposed`, `shape_match`, `multi_valued`,
  `below_support`, `mixed_type`, `over_budget`); `signature` (the role-player
  signature's canonical text); `value_primitive`; `support` (distinct
  entities); `rows` (row count); `multi` (entities with more than one distinct
  value, and the largest count); `exact_repeats`; the first 32 opaque row ids;
  `value` only when `show_values` holds;
- `candidates` per group: every existing fact type in which the group's
  entity type plays a role, with its id, readings, role names and players,
  `signature_equal` (bool), its row count in the population, and value-free
  overlap counts against the group (entities in both; (entity, value) pairs
  in both, by typed identity); and `origin`, the `{generic,
  attribute_sha256}` the fact type recorded when a judged proposal made it
  (§2.2), else `null`;
- redacted attribute roles: one entry per skipped generic fact type, with no
  group detail.

`--out` and `--report` are unchanged byte for byte. The evidence is capped at
the proposal cap (10 MiB); candidates past the cap are dropped from the tail
and counted in `truncated`.

### 2.2 Judgements and rendering (TS2)

Both files are JSON the caller (a skill) writes:

```json
{"format": "gnd-type-judgements/1", "kind": "duplicates",
 "evidence_sha256": "<raw-byte SHA-256 of the evidence file>",
 "judge": {"skill": "gnd-judge-fact-types", "agent": "<free text>"},
 "verdicts": [{"generic": "item_has_attribute", "attribute_sha256": "...",
               "verdict": "distinct", "rationale": "..."},
              {"generic": "item_has_attribute", "attribute_sha256": "...",
               "verdict": "duplicate", "of": "item_has_attribute_induced_0",
               "rationale": "..."}]}
```

`kind: "shapes"` files carry `verdict` in `functional`, `many-to-many`,
`skip`. A duplicates file judges every group whose status is `proposed` or
`shape_match`; a shapes file judges every `multi_valued` group. Rules:

- `--duplicate-judgements` and `--shape-judgements` each need
  `--families fact-type` and `--type-evidence-in EVIDENCE` (the file they
  bind); the CLI recomputes the evidence and refuses (3) when its bytes
  differ from `EVIDENCE` (stale data or model), then refuses on a digest,
  coverage or form mismatch;
- `distinct`: proposed as today, even if `signature_equal`; `duplicate`: the
  group is listed in `shape_matches` with `existing: of` and
  `judged: true`; `of` must be a candidate of that group, else 3;
- `functional` on a group with `multi > 0` exits 3 (TS-R2); `many-to-many`
  renders the binary fact type with roles `entity` and `value` and a
  uniqueness over both roles, its envelope's `support` being distinct
  (entity, value) pairs over rows, and `counterexamples` the exactly repeated
  rows' ids; `skip` counts it `judged_skip`;
- every judged proposal adds `provenance.induced_from: {generic,
  attribute_sha256}` on the fact type (the origin TS1 reads back) and
  `provenance.judgement` on the constraint (TS-R4);
- a rationale holding a raw attribute value, when values are not allowed,
  exits 3 (TS-R5); the message names the verdict index, never the value;
- the budget, id clash rule and redaction copy apply unchanged;
- without either judgements option, TS-R1 holds exactly.

### 2.3 The skills (TS3, TS4)

**`gnd-judge-fact-types`.** Inputs: the model and one evidence file. For each
`proposed` or `shape_match` group, it compares the group with its candidates
on readings, role names, `origin`, signature and overlap counts, and writes
`distinct` or `duplicate of X` with a short rationale. Decision rules in the
skill, in order: an `origin` equal to the group's key is a duplicate; high
pair overlap with a candidate is strong duplicate evidence; equal signature
alone is no evidence either way; when evidence is too thin (placeholder
readings, no origin, no overlap), it says so and asks the user, rather than
guessing. Hands off to `gnd discover --duplicate-judgements`.

**`gnd-model-multivalued`.** A variant of the `rai-orm-from-schema` dialect
conventions: as a schema importer turns a junction table into a
many-to-many fact type with a spanning uniqueness, this skill reads each
`multi_valued` group's evidence (`multi`, `exact_repeats`, support, rows) and
the model, and writes `many-to-many`, `functional` (only when the user
confirms the extra values are errors, which then routes to fixing the
population, not to a proposal) or `skip`. It names the ORM consequence of
each choice by linking `gnd-orm-core` references, and states that the
spanning uniqueness carries no functional claim. Hands off to
`gnd discover --shape-judgements`.

Both skills: route sentences in `gnd-orm-core`'s workflow index; no spec
text copied (D-07); disclosure stated as in TS-R5.

## 3. Dependencies and artifact homes

| Dependency | State | Blocks |
|---|---|---|
| PR #86 (CT, adds `discover/types.py`) | open at `549ebb9` | TS1 start (TS-D1) |
| `induction-skill` IS1 (17th packaged skill) | approved, not executed | nothing; TS3/TS4 rebase their skill counts on whichever lands first (§6) |
| MG2 additive policy, MG3 signature helper | merged (PR #83) | none |

| Artifact | Home | Lane |
|---|---|---|
| evidence builder | `src/gnd/discover/type_evidence.py` (new) | `discover` |
| judgement reader and renderer | `src/gnd/discover/type_judgements.py` (new); `types.py` gains a verdict hook | `discover` |
| evidence and judgements schemas | `src/gnd/type-evidence.schema.json`, `src/gnd/type-judgements.schema.json`; read-only copies in `gnd-orm-core/references/` held by `test_schema_sync.py` (TS-D5) | data |
| skills | `src/gnd/skills/gnd-judge-fact-types/`, `src/gnd/skills/gnd-model-multivalued/` | packaged |
| docs | `docs/reference/discover.md` (amend), `docs/reference/type-judgements.md` (new), `docs/how-to/judge-induced-fact-types.md` (new), release notes, capabilities | docs |

The order TS1 → TS2 → {TS3, TS4} → TS5 → close is acyclic. TS3 and TS4 are
independent of each other.

## 4. Phases, deliverables, named criteria and inherited residuals

### TS1: Evidence (about 220 source lines, 450 test lines)

Spec: [phase-TS1-spec.md](phase-TS1-spec.md) (draft).

- **TS1-C1:** every group the family forms appears once with its status, in
  the family's order; each `skipped` count in the report equals the count of
  that status in the evidence.
- **TS1-C2:** candidates: every fact type the entity type plays, with
  `signature_equal`, row count and both overlap counts, checked on a fixture
  with one applied induced fact type populated, one unrelated fact type and
  one fact type with equal signature but disjoint data.
- **TS1-C3:** `origin` read back from `provenance.induced_from`; `null`
  otherwise; a malformed `induced_from` exits 3.
- **TS1-C4:** disclosure: a canary attribute value absent from the evidence
  under unset-without-flag and `customer`; present under `internal` and
  unset-with-flag; `customer` with `--show-values` exits 3 as today.
- **TS1-C5:** `--type-evidence` without the family, or equal to another
  output path, exits 64; an existing file exits 11; a symlink exits 74.
- **TS1-C6:** `--out` and `--report` bytes equal with and without the
  option; the parity table without it equals the baseline except the
  `discover` usage line.
- **TS1-C7:** cap: candidates past 10 MiB dropped and counted.

### TS2: Judgements and rendering (about 300 source lines, 650 test lines)

- **TS2-C1:** binding: stale evidence (population changed), wrong digest,
  wrong `kind`, a missing, extra or repeated group, each exit 3, nothing
  written.
- **TS2-C2:** `distinct` on a `shape_match` group is proposed: the
  once-per-generic limit lifts under judgement (O9).
- **TS2-C3:** `duplicate` on a group with no equal signature is reported
  against `of`; an `of` outside the candidates exits 3.
- **TS2-C4:** `functional` on a multi-valued group exits 3.
- **TS2-C5:** `many-to-many` renders roles, spanning uniqueness, support over
  pairs, counterexamples for exact repeats, redaction copied.
- **TS2-C6:** a rationale holding the canary value exits 3 under `customer`
  and unset-without-flag, and is accepted under `internal`.
- **TS2-C7:** every rendered proposal passes `preview --policy additive`
  (0) and applies; the budget counts judged groups; `provenance.induced_from`
  and `provenance.judgement` present and recomputable.
- **TS2-C8:** no judgements option: TS-R1 parity.
- **TS2-C9:** round trip: after applying a judged proposal, a fresh
  evidence file shows the new fact type's `origin` equal to its group.

### TS3: `gnd-judge-fact-types` (about 180 skill lines, 200 test lines)

- **TS3-C1:** the skill ships, installs, appears in AGENTS.md and every pin
  (inventory set, names, marketplace, install and doctor), counts moved as
  one decision.
- **TS3-C2:** its handoff names `gnd discover ... --duplicate-judgements`
  and `gnd evolve preview`, never `apply`; route test.
- **TS3-C3:** it forbids reading the population and states the disclosure
  rule; prose test.
- **TS3-C4:** a recorded skill run (TS-D6) over the TS5 fixture yields a
  judgements file the CLI accepts and whose verdicts match the fixture's
  answer key (held apart from the skill's inputs).

### TS4: `gnd-model-multivalued` (about 180 skill lines, 200 test lines)

- **TS4-C1..C3:** as TS3-C1..C3, for `--shape-judgements`.
- **TS4-C4:** the skill states its relation to `rai-orm-from-schema` (the
  convention it borrows; that `gnd import rai-orm` is unchanged) and links
  the spanning-uniqueness reference instead of copying it.
- **TS4-C5:** a recorded run over the fixture's multi-valued attribute
  yields `many-to-many`, accepted by the CLI, preview exits 0.

### TS5: Documentation

- **TS5-C1:** dispositions over every page and skill naming the fact-type
  family, shape matches or `multi_valued`, including the CT how-to.
- **TS5-C2:** the how-to runs end to end in the tutorial runner, with the
  recorded skill outputs as fixtures (no live model in the runner).
- **TS5-C3:** `discover.md`'s once-per-generic paragraph and D5 sentence
  amended to say what holds by default and what changes under judgement.
- **TS5-C4:** docs gates exit 0.

### Milestone close (not a feature phase)

The close record, the question sweep, four close readers, the close gate
(union of phase gates), parity, the PR. Owner acceptance separate.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1 | TS2-C2, C3; TS3-C4 |
| O2 | TS2-C5; TS4-C4, C5 |
| O3 | TS2-C5 |
| O4 | TS1-C1, C2; TS-R2 |
| O5 | TS1-C6; TS2-C8 |
| O6 | TS1-C4; TS2-C6; TS3-C3; TS4-C3 |
| O7 | §8 |
| O8, O13 | TS2-C7 |
| O9 | TS2-C2; TS5-C3 |
| O10 | TS-D7 |
| O11, O12 | TS3-C1; TS4-C1 |
| O14 | TS2-C5 |

### Carried, not owned

CT-close-Q3, Q4, Q5, CT2-Q1, CT2-Q2, O18 stay with the owners the CT close
named.

## 5. Documentation, skill and compatibility surfaces

- **CLI:** four new `gnd discover` options (`--type-evidence` in TS1;
  `--type-evidence-in`, `--duplicate-judgements`, `--shape-judgements` in
  TS2), RF1 help
  and exit goldens re-pinned with the change stated.
- **Formats:** two new schemas, versioned `/1`.
- **Report:** `fact_type_proposals.shape_matches[]` gains optional
  `judged: true`; `skipped` gains `judged_skip`; both appear only under
  judgement (schema additive; old reports still validate).
- **Model:** `provenance.induced_from` on fact types; no schema change
  (provenance is an open object). `gnd validate` unchanged.
- **Disclosure:** `gnd discover` stays one `site` leaf; the new options are
  rows under the existing `option` convention; T15 and T26 updated.
- **Packaged skills:** two new skills (16 → 18, or 17 → 19 after IS1);
  route rows in `gnd-orm-core`; AGENTS.md table rows by the installer
  workflow; marketplace and install pins.
- **Python API:** none in this milestone (TS-D8).

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A skill leaks a value through its rationale | TS-R5 refusal; TS2-C6 canary |
| A skill reads the population directly | Skill prose forbids it; not enforceable by GND; stated in docs as a skill-level control |
| Stale judgements applied to new data | TS-R3; evidence recomputed and compared (TS2-C1) |
| A judge errs and a duplicate is admitted | Proposal stays `proposed`/deontic; `gnd evolve preview` and review admit; how-to shows the rejection path |
| The default family drifts | TS-R1 parity tables in TS1, TS2 and the close |
| PR #86 changes before merge | TS-D1: TS1 rebases on the merge commit and re-reads lines |
| Skill-count pins collide with IS1 | Each skill phase rebases its counts on main at spec time and records the literal it moved |
| Recorded runs need a live model (paid) | TS-D6 owner ruling before TS3; the runner uses recorded outputs only |

## 7. Out of scope

- Moving rows into an induced fact type (migration); deleting the generic
  fact type.
- Any judgement inside the CLI, heuristic or learned.
- Changing `gnd import rai-orm` or the external `rai-orm-from-schema` skill.
- Shapes beyond binary functional and many-to-many (ternaries, objectified
  attributes, entity-valued attributes); a later milestone.
- Salting the attribute digest (CT4-Q1) unless TS-D7 folds it in.
- A Python API for evidence or judgements (TS-D8).

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, owner gate,
implementation and focused tests, an independent diff review, a refactoring
review and a record. No code before recorded spec approval. Plan and close
review: proposed four local readers, as in the predecessor (TS-D2).
Declared stop rule: at most one confirmation round after round 1, restricted
to blocking themes; stop early when the self-inflicted ratio exceeds one
half. Work happens on topic branch `claude/skill-judged-type-induction`,
then a PR; merge requires the owner. Never push to main.

## 9. Per-phase verification story

| Phase | Expected result | Focused gate (exact selection in each spec) |
|---|---|---|
| TS1 | Evidence complete, value-free, outputs unchanged | `tests/test_discover_type_evidence.py` plus the CT4 gate (`tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py`) |
| TS2 | Judged rendering, refusals, preview passes | TS1 gate plus `tests/test_discover_type_judgements.py`, `tests/test_schema_sync.py` |
| TS3 | Skill ships and routes; recorded run accepted | `tests/test_packaged_skills.py`, `tests/test_public_agents_skill_table.py`, `tests/test_install.py`, `tests/test_doctor_uninstall.py`, `tests/test_marketplace_plugins.py`, `tests/test_skill_prose_sync.py`, `tests/test_judge_fact_types_skill.py` |
| TS4 | Same for the multivalued skill | TS3 pins plus `tests/test_model_multivalued_skill.py` |
| TS5 | Pages executed | `uv run python tools/run_tutorials.py`, `zensical build --strict`, `uv run python tools/check_docs.py site` |

Affected consumers: anyone parsing `fact_type_proposals` (additive keys only
under judgement); the RF1 goldens; the disclosure site table.

### Implementability sweep (author inspection, not review)

| Question | Answer |
|---|---|
| Can a fact type record its origin without a schema change? | Yes: `fact_type.provenance` is `{"type": "object"}` in `orm-meta.schema.json`. |
| Can overlap be computed value-free? | Yes: typed identities compared in memory, only counts written. |
| Can the CLI detect a value in prose? | Yes for exact substrings of each attribute value's text form; not for paraphrase or encoding. Stated as a limit. |
| Can skills be tested without a live model? | Prose and route pins, yes; behaviour needs a recorded run (TS-D6). |
| Is TS1 ready now? | No: blocked on PR #86 merging (TS-D1). Its spec is drafted against `549ebb9`. |

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| TS-D0 | Record the `(o0)` rulings | quote the owner's words at the plan gate; or accept the relayed summary | quote at the gate |
| TS-D1 | Base | (a) wait for PR #86 to merge, rebase onto it; (b) start on `claude/process-milestone-composition`: PR #86 changes would need replaying | (a); plan drafted on the branch |
| TS-D2 | Plan and close review instrument | (a) four local readers; (b) six-seat panel | (a) |
| TS-D3 | What "variant of the rai-orm skill" means | (a) a GND packaged skill borrowing the dialect's schema-to-ORM conventions; (b) a variant of the external skill, outside this repo: GND would only document the handoff | (a) |
| TS-D4 | Where verdicts enter | (a) judgement files read by `gnd discover`, which renders (this plan): the CLI keeps operation shapes, ids, budget and checks; (b) the skill writes evolve operations itself: fewer CLI options, but an agent then authors ids, envelopes and budgets that only preview checks | (a) |
| TS-D5 | Vendor the two schemas into `gnd-orm-core/references` | (a) yes, read-only copies with sync tests, so skills can link them; (b) skills cite `gnd discover --help` only | (a) |
| TS-D6 | Recorded skill runs | (a) one recorded run per skill with a named live model, paid, owner-run or owner-authorized; (b) prose pins only: TS3-C4 and TS4-C5 become "not met" | (a), ruled at the TS3 gate |
| TS-D7 | CT4-Q1 (salt or omit the digest) | (a) leave with the owner; (b) fold in: the judge's `origin` match depends on the digest form, so a later change would break recorded origins | (a), and record the dependency |
| TS-D8 | Python API | (a) none; (b) `gnd.api` wrappers: more pins | (a) |
| TS-D9 | Unjudged groups | (a) a judgements file must cover every eligible group (exit 3 otherwise); (b) unjudged groups fall back to the deterministic rule: quieter, but a forgotten group silently stays signature-judged | (a) |
| TS-D10 | Contradicted verdicts | (a) exit 3, nothing written; (b) count and skip: a judge's error stays hidden in a count | (a) |
| TS-D11 | Two skills or one | (a) two, as ruled; (b) one skill with two routes: one pin move instead of two | (a) |

| ID | Open question | Owner |
|---|---|---|
| TS-Q1 | Do candidates need readings of every role-playing fact type, or only same-entity binaries? | TS1 spec D1 |
| TS-Q2 | Should a `duplicate` verdict also carry a proposed rename of the existing fact type's placeholder reading? | TS2 spec |
