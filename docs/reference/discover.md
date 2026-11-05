# Constraint discovery

`gnd discover` reads one model and one population and suggests constraints
that hold in it. **It proposes; you decide.** Every suggestion is an induced,
proposed, advisory (deontic) constraint inside an ordinary `gnd evolve`
proposal. Nothing reaches the model until you preview, review and apply that
proposal, and nothing becomes a hard rule until a review is recorded. See
[provenance and modality](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md).

This page is the one home of the command's contract. To see it end to end,
[find the rule your auditors are really using](../tutorials/learn-rules.md)
sorts one week's suggestions into sensible rules and accidents.

```
gnd discover MODEL POPULATION --out PROPOSAL --report REPORT \
             --actor ID --requested-at 2026-10-24T12:00:00+00:00 \
             [--families uniqueness,mandatory,value,frequency,subset,equality,exclusion] \
             [--max-values 20] [--max-pairs 256] [--format text|json]
gnd discover MODEL POPULATION --families fact-type [--min-support 20] [--show-values] \
             [--type-evidence EVIDENCE] ...
```

`--actor` and `--requested-at` fill the proposal's audit. They are required, so
the same inputs always produce the same bytes.

## What it looks for

By default, single-role rules of seven families. The opt-in `fact-type`
family is described in
[proposing fact types from generic rows](#proposing-fact-types-from-generic-rows).

| Family | Example | Candidates |
|---|---|---|
| uniqueness | each person is in at most one team | every proper role subset of a fact type with up to 4 roles; sizes 1–2 above that |
| mandatory | every person has a team | every role |
| value | a grade is one of g1, g2, g3 | every role with 1 to `--max-values` distinct values (the values themselves enter the model) |
| frequency | a person has at most 2 skills | every role, with the tightest observed bound; never `min: 1` alone, never `max: 1` (that is uniqueness) |
| subset | every team leader is a team member | same-typed roles in different fact types, up to `--max-pairs` unordered pairs |
| equality | the teams with leaders are exactly the teams with members | the same pairs |
| exclusion | no contractor is on payroll | the same pairs |

## What is kept

A suggestion is emitted only when all of these hold:
- one `gnd check` run over the model plus every suggestion gives it verdict
  `pass`;
- its **support** is above zero, which rules out trivial passes;
- it is neither declared in the model nor implied by a declared constraint.

**Support** counts what the rule quantifies over:

| Family | Subjects counted |
|---|---|
| uniqueness | distinct keys |
| frequency | groups |
| mandatory | roster members |
| value | occurrences |
| subset | distinct values on the subset side |
| equality, exclusion | distinct values on either side |

GND computes support from the population. It is recorded in each induction
block with up to 256 example ids, in one of two forms:
- `ft<k>#<i>` names a fact: fact type `k` in the model's order, fact `i` in
  that fact type's list in the population. Every family except mandatory uses
  it; `ft0#3` is the fourth fact of the model's first fact type.
- `ot<k>#<i>` names a roster member, which a mandatory rule counts: object type
  `k` in the model's order, member `i` in order of first appearance in the
  population. `ot2#0` is the first instance seen of the model's third object
  type.

Both counts start at 0. The ids are opaque positions, not values, so they never
carry what a redacted role holds. Its output is the same in every
[disclosure mode](disclosure.md): it never proposes values for a redacted role,
so there is nothing to withhold.

**Implied rules are counted, not suggested.** The text output prints the
nonzero counts on one line, for example
`SUPPRESSED declared=1 spanning-uniqueness=3`, and the report's `suppressed`
object holds all ten keys. Against a declared constraint, the rules apply in
this order, regardless of that constraint's modality:

| Key | Suppressed candidate |
|---|---|
| `declared` | identical to a declared constraint |
| `equality-implies-subset` | a subset that a declared equality implies |
| `frequency-max-1-is-uniqueness` | a uniqueness that a declared frequency of at most 1 implies |
| `unscoped-value-implies-scoped` | a role-scoped value domain that a declared unscoped one implies |
| `reference-scheme-implies-uniqueness` | a uniqueness or mandatory that a reference scheme implies |
| `spanning-uniqueness` | a key spanning all roles, which is trivially unique |
| `superkey` | a superset of a declared key |

Against other candidates:

| Key | Suppressed candidate |
|---|---|
| `redundant-frequency` | a frequency whose largest group is 1, which is uniqueness; counted before the check |
| `redundant-subset` | a subset absorbed by an emitted equality over the same two roles; counted after the check |
| `redundant-superkey` | a key that contains another emitted key, so only minimal keys are kept; counted after the check |

**Near-misses** are rules broken by at most 5% of their subjects, and by at most
32, which needs at least 20 subjects. They are listed in the report with their
counterexample ids and are never suggested.

## Proposing fact types from generic rows

When facts land in a generic fact type ("an item has an attribute with a
value"), a recurring attribute name often deserves its own fact type. The
opt-in family `fact-type` proposes one. It never runs by default:

```sh
gnd discover model.orm.yaml items.population.json --families fact-type --min-support 20 \
  --out proposal.json --report report.json --actor you --requested-at 2026-11-04T00:00:00+00:00
```

A fact type is generic only when its provenance declares which three roles
are the entity, the attribute name and the value:

```yaml
provenance:
  generic: {entity: item, attribute: name, value: value}
```

A malformed declaration exits 3. An undeclared fact type is never grouped,
whatever its shape.

Rows are grouped by the attribute value. A group is proposed when its
distinct entities (not rows) reach `--min-support` (default 20) and all its
values share one JSON type. The proposal adds a binary fact type
`<generic>_induced_<n>` with roles `entity` and `value` and a placeholder
reading naming the generic fact type
(`{Item} has induced item_has_attribute attribute 0 {AttributeValue}`) for a
reviewer to rename, a value type when the generic value type's primitive differs, and a
uniqueness on the entity role carrying the induced, proposed, deontic
envelope. A group in which any entity has several distinct values breaks that
uniqueness, so by default it is counted (`multi_valued`) and not proposed;
under a `shapes` judgement that calls it `many-to-many`, it is proposed with a
uniqueness spanning both roles instead ([type judgements](#type-judgements)).
An exactly repeated row is one value. A new id never
reuses one the model already has; a clash takes the next suffix
(`<generic>_induced_<n>_1`). A redacted entity or value role stays redacted
in the new fact type. Proposals that would push the evolve proposal past its
size cap are counted (`over_budget`) and left out; when the family adds groups, the cap is checked on the written
bytes and type groups are dropped from the tail, in steps, until the
proposal fits.
Nothing moves: the rows stay in the generic fact type, and admitting the
proposal is a reviewed `gnd evolve apply`. The proposal passes
`gnd evolve preview --policy additive`.

When an existing fact type already has the same role players, the group is
listed under `shape_matches` with that fact type and not proposed. A redacted
attribute role is skipped and counted. Every group from one generic fact type
has the same role players, so once one induced fact type is applied, every
later group from that generic fact type is reported, by default, as a shape
match against it rather than proposed; rename or retype the applied fact
type, or review the shape matches, to go on. Under a `duplicates` judgement
the limit lifts: a group judged `distinct` is proposed whatever its
signature matches, and one judged `duplicate` is listed against the fact
type the judge named ([type judgements](#type-judgements)). The packaged
skills `gnd-judge-fact-types` and `gnd-model-multivalued` write those
judgements; [Judge induced fact types with two skills](../how-to/judge-induced-fact-types.md)
walks both. Groups proposed in one run are not
compared with each other.

The report's `fact_type_proposals` key lists, per proposed fact type, the
opaque ids of the rows that would migrate (`ft<k>#<index>`) and the
SHA-256 of the attribute value's canonical JSON (`gnd.artifacts.canonical_json_bytes`:
sorted keys, no spaces, one trailing newline; for the string `size` that is
`"size"` and a newline), as `attribute_sha256`. Attribute names are short
and guessable, so anyone holding the report could recover a name by hashing
likely candidates; under `customer` the digest is therefore omitted from
proposals and shape matches. The value itself appears as `value` only when the
disclosure mode allows `--show-values`: with the flag when the mode is unset,
always under `internal`, and never under `customer`, where the flag exits 3.
Without the family the key is absent and every output is as before. The
family's row visits are reported as `row_visits` in its own key, not in the
report's `work` totals, so those totals mean what they meant before; the
work ceiling does not bound them, and the family is bounded instead by the
population's own size cap.
`--min-support`, `--show-values`, `--type-evidence` and the
[judgement options](#type-judgements) without `--families fact-type` are
usage errors (64).

### Type evidence

The family only counts. Whether two attributes mean the same thing, or how
a multi-valued attribute should be modelled, is a judgement it leaves to a
reader. `--type-evidence EVIDENCE` writes what that reader needs: format
`gnd-type-evidence/1`, schema
[`type-evidence.schema.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/type-evidence.schema.json).
The proposal and the report are byte for byte what the same run writes
without the option.

- **One entry per group, in the family's order,** with an id `g0`, `g1`, …
  local to the file. A reader that records judgements binds the file's own
  SHA-256, so the ids stay meaningful. Each entry carries:
  - the status the family gave it: `proposed`, `shape_match`, `multi_valued`,
    `below_support`, `mixed_type` or `over_budget`;
  - the proposed fact type id, when there is one;
  - the role-player signature it would have, once typed;
  - its value primitive, distinct entities (`support`), rows and the first
    32 row ids;
  - `multi`: how many entities have several distinct values, and the most
    any one has;
  - `exact_repeats`: rows that repeat an (entity, value) pair.
- **Candidates:** every other fact type the group's entity type plays, with
  its readings, roles, row count and whether its signature equals the
  group's. It also has two overlaps: the group's entities that play it, and,
  for a binary fact type whose other role has the group's value kind, the
  (entity, value) pairs it already holds (otherwise `null`, and always
  `null` when that role is redacted).
- **Origin:** a candidate whose provenance names the group it came from,
  `induced_from: {generic, attribute_sha256}`, carries `origin` with
  `same_attribute`, the comparison with this group's attribute. A malformed
  `induced_from` exits 3 and nothing is written.
- **Disclosure:** the attribute value appears as `value` only when
  `--show-values` is allowed, as in the report. Under `customer` no
  attribute digest appears, neither the group's nor an origin's;
  `same_attribute` is still given. The file records both decisions as
  `show_values` and `show_digests`, beside the model's and population's
  SHA-256 and `min_support`. A generic fact type whose attribute role is
  redacted forms no group and is listed by id in `redacted_generics`.
- **Size:** the file is at most 10 MiB. Groups come first, in order; when
  they alone would pass the cap, the rest are left out and counted in
  `truncated_groups`. Candidates then fill what remains, in order, and those
  left out are counted in `truncated`, so the last groups lose theirs first.
- **When it is written:** after the report, even when nothing is proposed.
  It must be a fifth distinct path (64). An existing file is refused (11)
  and a symbolic link (74), both before anything is read.

### Type judgements

A judgement skill reads one evidence file and writes its verdicts in a
judgements file, format `gnd-type-judgements/1`, schema
[`type-judgements.schema.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/type-judgements.schema.json).
`gnd discover` reads it back, checks it, and renders the verdicts. It never
chooses one:

```sh
gnd discover model.orm.yaml items.population.json --families fact-type \
  --type-evidence-in evidence.json --duplicate-judgements duplicates.json \
  --shape-judgements shapes.json \
  --out proposal.json --report report.json --actor you --requested-at 2026-11-05T00:00:00+00:00
```

- **Two kinds.** A `duplicates` file gives `distinct`, or `duplicate` with
  `of` naming a candidate, for every group with status `proposed`,
  `shape_match` or `over_budget`. A `shapes` file gives `many-to-many` or
  `skip` for every `multi_valued` group. Each verdict names its `group`
  (`g<n>`), the group's `generic` and a `rationale` of at most 2,000
  characters; `judge` names the skill and, in free text, the agent.
- **Binding.** `evidence_sha256` is the SHA-256 of the evidence file's raw
  bytes, given as `--type-evidence-in`. The run computes the evidence again,
  as `--type-evidence` would write it for this model, population,
  `min_support` and disclosure mode, and refuses when the bytes differ; the
  message names the setting that differs. `--type-evidence` cannot be given
  with `--type-evidence-in`.
- **What is refused (3, nothing written).** A file that is not schema-valid
  JSON under 10 MiB; a `kind` that does not match its option; a group that
  is missing, extra, repeated, of another generic or not of that kind; a
  verdict of the other kind (there is no `functional`); `of` on anything but
  a duplicate, or naming a fact type that is not a candidate of the group in
  the evidence; `distinct` or `many-to-many` on a group whose attribute
  some fact type's `induced_from` already names for the same generic fact
  type, whether or not the evidence lists that fact type as a candidate,
  because that attribute was already induced; evidence that left groups out
  (`truncated_groups` above 0).
- **Rendering.** `distinct` proposes the group as above, whatever its
  signature matches; when its id takes a clash suffix, its reading names the
  suffix too (`attribute 0_1`), so it never repeats an existing reading.
  `duplicate` lists it under `shape_matches` against
  `of`, with `judged: true`. `many-to-many` proposes the binary fact type
  with a uniqueness spanning both roles: its support is distinct (entity,
  value) pairs over rows, and the rows that repeat a pair are its
  counterexamples. The spanning uniqueness says each pair is recorded once;
  it states nothing functional. `skip` counts the group in
  `skipped.judged_skip`. The size budget, the id rule and redaction apply as
  to any group, and every constraint stays induced, proposed and deontic.
- **Provenance.** Each judged fact type records, in its own `provenance`,
  `judgement` (the evidence and judgements digests, the kind, the verdict
  and the skill) and, except under `customer`, `induced_from: {generic,
  attribute_sha256}`. Once applied, that origin is what the next evidence
  file reports. Under `customer` no attribute digest enters the model, so
  the next evidence shows no origin for that fact type.
- **The report** gains `judged: true` on judged entries, `shape:
  many-to-many`, `skipped.judged_skip` and `judgements` (the three
  digests). They appear only under judgement; without these options the
  outputs are as before.
- **Free text.** When values are not allowed (the mode is unset without
  `--show-values`, or `customer`), each `rationale`, `judge.agent` and
  `judge.skill` is checked for the text of any attribute or value the
  population holds, and under `customer` for any attribute digest. A match
  ignores case, counts a run of whitespace as one space, and needs the
  characters on either side not to be letters, digits or `_`; it exits 3
  naming the field, not the text. A text that is
  also a token of the model file is allowed, since the judge reads the model.
  The check catches exact text only, not a paraphrase or an encoding; the
  skills' own rule not to quote values is the main control.

## Outputs

- **`--report`:** always written. Format `gnd-discover/1`, schema
  `src/gnd/discover.schema.json`. It states:
  - the bounds used;
  - every skip by reason;
  - rejections by verdict and suppressions by rule;
  - emitted suggestions and near-misses;
  - the work counter, beside its computed ceiling. Exceeding the ceiling is an
    internal defect.
- **`--out`:** written only when something is emitted. A schema-3 evolve
  proposal of ADD constraint operations; preview it with `gnd evolve preview`.
- **`--type-evidence`:** optional, with the `fact-type` family; see
  [type evidence](#type-evidence).
- **`--type-evidence-in`, `--duplicate-judgements`, `--shape-judgements`:**
  inputs, with the `fact-type` family; see [type judgements](#type-judgements).

**What is skipped.** Everything skipped is counted in the report, never dropped
silently:
- **Fact types** that an existing operation references (evolve would refuse
  additions there), and derived or semiderived fact types.
- **Value rules on roles the model marks `redact: true`.** Their `allowed` list
  would carry the values the model hides.
- **Value rules on columns holding opaque or unrepresentable cells.**
- **Mandatory rules on object types a derived fact type plays.** Their checker
  roster excludes derived claims.
- **Candidates past the size budget.** The proposal must stay under the 10 MiB
  model and proposal caps.

## Exits

| Exit | Meaning |
|---|---|
| 0 | done, including when nothing was emitted (report only) |
| 11 | `--out` already exists; nothing was written |
| 3 | invalid model or population: over 10 MiB, written for another model, or a file name that cannot be an evidence ref; or a judgements file that is unbound, incomplete or contradicted |
| 64 | usage error |
| 66 | a missing input file, or a missing reference population file the model declares |
| 70 | internal defect |
| 74 | an output path is a symbolic link, or a write failed; or a declared reference population file (or its directory) is a symbolic link, not a regular file, unreadable or over its size cap |

**How values and references are read:**
- **Values are compared by `gnd check`'s typed identity**, so `1` and `1.0` in a
  Number role are one value, exactly as the checker sees them.
- **Reference populations** a model declares are bound as `gnd check` binds
  them, and the scan covers the combined facts. A reference file whose digest
  differs exits 3; one that is missing exits 66 and one that is linked exits 74,
  as `gnd evolve` refuses them.

**Paths and output files:**
- `--out`, `--report`, MODEL and POPULATION must be four different paths
  (exit 64).
- An existing file at `--out` is refused (exit 11) before anything is written,
  so an old proposal can never sit beside a newer report.

## Limits

- **A `gnd evolve preview` limit that predates discovery:** it cannot preview
  a model holding a YAML-only value such as an unquoted date (written as block
  YAML in the proposal). `gnd discover` handles such a model, but its proposal
  waits on evolve. Models that declare reference populations preview normally.
- **One population** of at most 10 MiB, in memory. A YAML population is also
  capped at 1,000,000 parse events, so a large population should be JSON.
- **Single-role sequences only**: no external uniqueness or frequency, and no
  multi-role subset, equality or exclusion.
- **Support is a recorded claim** tied to the population's digest. Re-run
  discovery, or check the applied model, after the data changes.
