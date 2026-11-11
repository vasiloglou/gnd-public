# Unattended growth: CSDP steps 3 to 7 without a user, one document at a time

Load this when a host pipeline grows one model over many documents with no person to
answer ([SKILL.md](../SKILL.md), "Unattended mode"). The skill's Steps 3 to 7 are written
as questions to a user. This file says what an unattended host does at each of them. The
rules the validator enforces (`semantic:unattended-u1` to `-u8`, span units, refusals) stay
in [representation-format.md](../../gnd-orm-core/references/representation-format.md#unattended-source);
nothing here relaxes them.

A host that stops after Steps 1 and 2 produces a model of elementary facts and nothing
else: every value type a `String`, no subtypes, no uniqueness or mandatory rule, and entity
types that are kinds of one another modelled apart, so a fact about an insurer never joins
with a fact about a party. The rest of this file is what prevents that.

## Ground rules

- **Evidence licenses a proposal; it never confirms one.** Every constraint is `proposed` and
  `deontic`. No `explicit` or `user-supplied` source (U3), no `alethic` for `sample`,
  `llm-inferred` or `common-sense` (U8). Nobody reviewed anything.
- **Every proposal cites a span.** The reply carries a verbatim `quote`; the host locates it
  and computes the span (see [the reply shape](#the-reply-shape)). A quote that is absent or
  ambiguous drops the proposal; offsets are never guessed.
- **A cue is a reason to propose, not proof.** Read the sentence. "The insurer must notify the
  broker within 30 days" is a duty a party may breach, and a recorded breach is still a valid
  fact. It is not a rule that every insurer has a notification fact. Say so in `rationale`
  or leave the proposal out, and put the doubt in `open_questions`.
- **Read the model before proposing.** Reuse existing object type and fact type ids. A new
  element that restates an existing one is the failure this file exists to prevent.
- **Never emit an inferred operation.** Operations are commitments about side effects; an
  unattended host does not guess them.

## What one round is

One round is one document, in four moves.

1. **Steps 1 and 2** for the new document: elementary facts, object types, fact types, sample
   rows, each citing a span.
2. **Steps 3 to 6 on the round's new types and facts only.** Walk the evidence tables below
   for the fact types and object types this round introduces. Do not revisit earlier rounds
   here; that is the consolidation round.
3. **Emit the reply** ([shape](#the-reply-shape)), and have the host write the candidate model
   and a proposal. When the round's document is new to the model, the proposal opens with one
   `source-document` `add` (the SHA-256 of the document's raw bytes and a label), before the
   elements whose spans cite it. Declare each document once: a document already in
   `source.documents` is not declared again, and a digest declared twice makes a later change
   to it ambiguous. The operation's rules are in the
   [evolution contract](../../gnd-model-evolve/references/evolution-contract.md#stable-locators). (Before the operation existed the host edited
   `source.documents` by hand before the round; a declaration that appears in the candidate
   with no operation is still refused.)
4. **Gate.** `gnd validate MODEL --document DOC ... --require-documents`, supplying every declared
   document, so a span left unchecked fails the round instead of passing silently (the counts
   are in [representation-format.md](../../gnd-orm-core/references/representation-format.md#unattended-source)).
   Then `gnd evolve preview --policy additive --shape-report`, adding `--check-population FILE`
   when the round adds a constraint on a fact type that already holds facts
   ([below](#constraints-on-fact-types-that-already-hold-facts)), then `apply` repeating
   `--policy additive` and any `--populated` and `--check-population` options. `--shape-report`
   is a preview option only; `apply` rejects it (exit 64). The shape report is advice: for each added fact type it lists existing fact types
   over the same role players. Deciding that two readings mean the same thing is the host's
   ([acting on a shape match](#acting-on-a-shape-match)).

### Acting on a shape match

For each existing fact type the report names beside an added one, the host does one of three
things and logs which:

- **Reuse the existing id.** The two readings say the same thing: drop the added fact type and
  write its facts against the existing one.
- **Keep both, with the reason.** The readings differ ("is returned via" is not "arrives via"):
  say why in the added fact type's `provenance.rationale`.
- **Keep both, and record the doubt** in `open_questions`, for the consolidation round to
  settle.

Never merge, rename or delete in the round. A merge is a rename or delete of something that
exists, so it belongs to the consolidation round's reviewed proposal.

**Constraints travel with their fact type.** Under `--policy additive` a new constraint over a
fact type that already holds facts is refused (`constraint.populated.add`, exit 3) unless a
clean population clears it ([below](#constraints-on-fact-types-that-already-hold-facts)), and a
fact type the same proposal adds is never populated. So propose a fact type's uniqueness, mandatory,
value and ring constraints in the round that adds it, before its facts are extracted. A
constraint that spans fact types, or a `value` constraint on an object type, is populated if
**any** fact type it touches is, so without that population it is admitted only when every one
of them is new or empty.
A population held outside the model (extracted facts in a separate file) is invisible to the
policy unless the host passes `--populated FACT_TYPE` for it; leave that out and the policy
admits constraints it should have refused. The policy protects the facts it can see, and only
those. The cells are in the
[evolution contract](../../gnd-model-evolve/references/evolution-contract.md#additive-policy).

## Evidence for Steps 3 to 7

For each step: the text that licenses a proposal, what to propose, and what does not license
one. `basis` is how the host sets `source`: `text-cue` is `llm-inferred` with
`rationale_world_fact` restating the cue, `rows` is `sample`, `library` is `common-sense`
citing `library_entry`. Library-basis constraints need no span (U5) but may carry one.

### Step 3: combine entity types; derived or constrained

| Evidence | Propose | Not evidence |
|---|---|---|
| A definition equating two names: "the Insured (the Policyholder)", "X means Y", "also called" | Do not create two types. Use one id and put the other name in `description`. | Two names that merely co-occur in a sentence |
| Two types already in the model that the no-overlap test (below) flags | A consolidation proposal ([below](#the-consolidation-round)), never an in-round merge | |
| A defined term computed from other facts: "an eligible policy is one that is in force and unclaimed" | A structured derived fact type, only if the rule grammar in `representation-format.md` can express it | Arithmetic or aggregation: record it in `open_questions`; do not write an opaque rule |

### Step 4: uniqueness and arity

| Cue in the text | Proposal | Basis |
|---|---|---|
| "the sole", "exactly one", "a single", "only one", "at most one" | `uniqueness` on the role of the thing that has one | `text-cue` |
| "each X has one Y" with sample rows showing no repeats | same, if the text states it; if only the rows show it | `text-cue`, else `rows` |
| Plural or open phrasing: "one or more", "any number of", "each of the", "may have several" | none; this is evidence against | |

Choose the constrained role from the sentence: in "each policy has exactly one expiry date" the
unique role is the policy's. Then run the arity checks below on any fact type with three or
more roles.

### Step 5: mandatory roles

| Cue | Proposal | Basis |
|---|---|---|
| "each X must have Y", "every X has Y", "X shall be", "exactly one" (also unique) | `mandatory` on X's role | `text-cue` |
| "may", "if any", "where applicable", "optionally", "at its option" | none | |
| A duty of a party rather than a property of the record | see [ground rules](#ground-rules) | |

### Step 6: value, set-comparison, ring and subtyping

**6a. Typed primitives.** Declare a value type with the narrowest primitive the text supports,
not `String`: an ISO date (`2025-12-31`) is `Date` (sample values must be `YYYY-MM-DD`); a
date and time is `DateTime`; a length of time in days, months or years is `Duration` (the
calendar-day fragment, model version 3: [calendar-day terms](../../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71));
an amount of money or a percentage is `Number` or `Float`. A text that gives a date in prose
("1 March 2024") the host cannot normalise reliably stays `String` with the doubt in
`open_questions`. Then name the value type so the typed library fires: `Money` or `Amount`,
`Percentage`, `Duration`, `Date` and the rest match by name, and each hit is a
`common-sense` proposal ([constraint-inference.md](../../gnd-orm-core/references/constraint-inference.md)).
A `String` value type that already exists is not retyped in a round: changing a primitive is a
non-additive edit, so queue it for the consolidation round.

**6b. Ring patterns** for a binary fact type whose two roles have the same player: the ring
library, basis `library`.

**6c. Value constraints.**

| Cue | Proposal |
|---|---|
| A closed list: "one of", "either A or B", "means (a), (b) or (c)", "only the following", "is limited to" | `value` with `allowed`, on the value type, basis `text-cue` |
| An open list: "such as", "including", "e.g.", "for example", "and the like" | none |
| A numeric bound stated in the text: "not less than 10", "up to 30 days" | `value` with `range`, `text-cue` |

Propose the enumeration in the round that introduces the value type; against an existing
populated one it is refused (the constraint ranges over every fact type the value type plays in).

**Enumeration or subtype.** A closed list of categories that carry no roles of their own is an
enumeration (`value` with `allowed`). A category whose instances play roles the others do not
is a subtype. When in doubt, take the enumeration: it can be promoted to subtypes in a
consolidation round, and a wrong subtype cannot be taken back additively.

**6d. Subtypes.** The text licenses a subtype link when a defined term names a kind of another:
"X, as the insurer", "an Insurer is a Party that…", "the insuring party (the Insurer)". Apply the
role-based test in [csdp-workflow.md](csdp-workflow.md) ("Subtype check"): does the subtype
play a role the supertype does not? If not, it is a role or a value of the supertype. A link is
recorded as `subtype_of` and `inherits_reference` on the subtype's object type, with the
defining sentence appended to that object type's `provenance.spans` and the doubt in
`provenance.rationale`. **A subtype link is structural: it has no `status` or `modality`, so it
cannot be kept `proposed` the way a constraint is.** Its only controls are the span, the
`rationale`, and the fact that a link over existing entity types is applied through the
consolidation round, where an owner sees a preview. In a round, link only a subtype that is new
in the same round.

**Subtype completeness.** Declare it with a `subtype-partition` constraint only when the text
states it: "exactly one of" or "is either" gives `exclusive` and `exhaustive`; "may also be"
gives neither and no constraint; "or other kinds" says not exhaustive. A partition with neither
flag asserts nothing and fails validation. Because the constraint ranges over the supertype and
every subtype, it is refused additively when any of them already plays a role in a populated
fact type.

### Step 7: other constraints, modality, commit, validate

| Cue | Constraint family |
|---|---|
| "only if", "unless", "before", "no later than", a stated order of two dates | `value-comparison`, or a `subset` between two roles when one fact presupposes another |
| "at least two", "no more than three" per entity | `frequency` |
| "a P is never also a Q" | `exclusion` |

All `proposed` and `deontic`; Step 7a to 7e collapse to nothing (nobody to review). Step 7f runs
as written, with `gnd validate --document` as the gate. Rejected proposals go to
`rejected_proposals` so the next round does not re-propose them.

## The consolidation round

Per-round growth cannot see across documents, so a model grown by rounds alone drifts toward
many types that are kinds of one another. Run a consolidation round over the **whole** model
periodically. Every ten documents is a reasonable default, and sooner when the shape report
flags several fact types over the same role players or an entity type count outgrows the
fact type count. The cadence is the host's.

A consolidation round is Step 3's combining of entity types and Step 6's subtypes, run over
every object type and fact type, using the checks below. It produces a **proposal for review,
not an auto-applied change**:

- **`--policy additive` does not admit it.** A new supertype alone is an added object type and
  is admitted, but it adds nothing until the existing entity types point at it, and adding
  `subtype_of` or `inherits_reference` to an existing object type is an `object_types.modify`
  outside the admitted keys (`description`, `provenance.rationale`). It is refused whether or
  not the fact types are populated. Nothing existing is renamed, so "adds meaning without
  renaming anything" is true of the result and not of what the policy can admit.
- **Run the consolidation preview without `--policy additive`.** Adding subtype links is a
  `modify`, which needs no breaking acceptance but carries a digest-bound blast radius.
  Merging two names into one is a rename or delete, which is breaking: the owner must accept the
  exact report digest ([gnd-model-evolve](../../gnd-model-evolve/SKILL.md)). A host stops at the
  written preview and hands it over, unless the owner has delegated that apply in terms.
- A subtype partition over populated fact types is a non-additive constraint too; propose it in
  the same consolidation proposal.

## Checks for a model built from many documents

Adapted from RelationalAI's `rai-ontology-design` skill (rai-agent-skills). Apply them in the
round to new types and in the consolidation round to all of them. Each ends in a proposal or
an `open_questions` entry, never in a silent edit.

| Check | Test | If it fails |
|---|---|---|
| **No overlap** | Two object types whose instances are always the same set: every A is a B and every B is an A (same reference, same roles in the same kinds of facts) | They are one type. Consolidate. Two names for one entity set is not two types |
| **Not a property group** | An entity type that only bundles values of another, has no identity of its own and is referenced by nothing else | Make its values roles of the parent. Exception: it is shared by several parents or has its own lifecycle (an address two customers share) |
| **Hidden intermediate type** | Several fact types hang off one entity with the same join to another entity, and each carries a different attribute of that other entity ("policy has broker name", "policy has broker city") | The other entity is missing. Add it and move the attributes to it |
| **Subtype completeness** | A set of subtypes of one supertype | Declare it exclusive, exhaustive or a partition, per the evidence above, or declare none |
| **Subtype or subset constraint** | The filtered set has roles or reference of its own | Subtype. If it is only a condition on the supertype with no roles of its own, use a constraint and no new type. A set reused in three or more places is worth naming |
| **Irreducibility** | A fact type of three or more roles that can be said as two independent facts without losing information ("Supplier supplies Part in Quantity", where supply and quantity do not depend on each other) | Split it |
| **Minimum key span** | In an n-ary fact type, the smallest unique role set spans at least n-1 roles; a single role alone determining the rest means the fact is compound | Split it |
| **Enumeration or subtype** | Closed list of categories | See [6c](#step-6-value-set-comparison-ring-and-subtyping) |

Irreducibility and minimum key span apply to the round's new fact types of three or more
roles, in the round. The other checks need the whole model and run in the consolidation round.

## The reply shape

A host's request must ask for every part below. A reply covering fact types only is the
failure this file exists to prevent. The reply is a proposal the host translates, with no
offsets and no provenance fields of the model's: the host owns the mapping, GND does not
read the reply, and `gnd validate --document` is the only gate.

```json
{
  "document": "policy.txt",
  "object_types": [
    {"id": "policy", "name": "Policy", "kind": "entity",
     "reference": {"mode": "popular", "value_type": "policy_no"}, "quote": "Policy P-17"}
  ],
  "fact_types": [
    {"id": "policy_expires_on_expiry_date", "reading": "{Policy} expires on {ExpiryDate}",
     "roles": [{"object_type": "policy", "role_name": "policy"},
               {"object_type": "expiry_date", "role_name": "expiry_date"}],
     "quote": "Policy P-17 expires on 2025-12-31",
     "rows": [{"values": {"policy": "P-17", "expiry_date": "2025-12-31"},
               "quote": "Policy P-17 expires on 2025-12-31"}]}
  ],
  "subtype_links": [
    {"subtype": "insurer", "supertype": "party", "inherits_reference": true,
     "quote": "An insurer is a kind of party", "rationale": "A defined term naming a kind of party."}
  ],
  "constraints": [
    {"host": "policy_expires_on_expiry_date", "basis": "text-cue",
     "constraint": {"type": "uniqueness", "roles": ["policy"]},
     "cue": "exactly one", "quote": "Each policy has exactly one expiry date",
     "rationale": "The text gives each policy one expiry date."}
  ],
  "derived_fact_types": [
    {"id": "policy_is_dated", "reading": "{Policy} is dated",
     "roles": [{"object_type": "policy", "role_name": "policy"}],
     "derivation": "derived", "storage": "computed",
     "derivation_rule": {
       "body": [{"fact_type": "policy_expires_on_expiry_date", "bind": {"policy": "$p", "expiry_date": "$d"}}],
       "head": {"policy": "$p"}},
     "quote": "A dated policy is a policy that has an expiry date",
     "rationale": "A defined term computed from a fact the model already holds."}
  ],
  "open_questions": [
    {"step": 6, "note": "The text gives a limit in prose that was not typed.", "quote": "within the notice period"}
  ]
}
```

| Field | Rule |
|---|---|
| `quote` | A verbatim excerpt of the document. The host searches the NFC text; no match, or more than one without a `quote_occurrence` (0-based), drops the entry and logs it |
| `object_types`, `fact_types` | The model's own element shapes, ids that already exist are reused, `quote` becomes `provenance.spans` |
| `rows` | One entry per sample row; `quote` becomes the row's `sample_spans` entry (U6 needs every row named once) |
| `subtype_links` | Sets `subtype_of` and `inherits_reference` on the subtype, appends the span to its `provenance.spans`, puts `rationale` in `provenance.rationale` |
| `constraints` | `host` is a fact type id, or `model` for a top-level constraint. `constraint` is the constraint body as the [constraint reference](../../gnd-orm-core/references/constraint-reference.md) gives it, without `source`, `status`, `modality` or `provenance`. The host writes those: `text-cue` is `llm-inferred` with `rationale_world_fact` set to `cue`, `rows` is `sample`, `library` is `common-sense` with `library_entry`; always `proposed` and `deontic` |
| `derived_fact_types` | The model's fact type shape with `derivation: derived`, `storage: computed` and a structured `derivation_rule`, the object form that `representation-format.md` defines under derived fact types. `quote` is the sentence that defines the term and becomes `provenance.spans`; `rationale` goes to `provenance.rationale`. No `rows`: its facts follow from the rule, so it holds no sample. A rule the grammar cannot express is an `open_questions` entry, never a string rule |
| `open_questions` | Anything the evidence does not settle. Not written to the model; kept in the host's log for the owner |

## Constraints on fact types that already hold facts

The procedure above prevents this by proposing constraints with the fact type. For a constraint
the text reveals only later, pass the population to the policy: `gnd evolve preview --policy
additive --check-population FILE`, and `apply` with the same options. The policy admits a new
constraint, or a change to one whose differing keys all strengthen, weaken or are admitted, when it is `proposed` and `deontic`, `FILE`
holds facts for every populated fact type it ranges over and none of them has sample rows, and
the constraint's own verdict over `FILE` is `pass`. The admission holds relative to `FILE`: the
constraint stays `proposed` and `deontic`, so it is advisory if a later population breaks it.
The rules are in the [evolution contract](../../gnd-model-evolve/references/evolution-contract.md#population-check). Anything else (a constraint
the population violates, or one over a fact type with sample rows) goes through a reviewed
non-additive proposal (`gnd evolve preview` without `--policy`).

---
*Checks adapted from the rai-agent-skills ORM skills (branch an-orm-skill) and `rai-ontology-design`.*
