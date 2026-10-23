# Verbalization Patterns

Halpin-style controlled natural language (CNL) templates for rendering an ORM 2 model as readable text. Used by GND authoring skills to verbalize constraint proposals as they emerge and to verbalize the full model for stakeholder review; the same templates are the basis for the `gnd` checker's violation messages. The verbalization is the primary review surface for stakeholders who never read YAML.

Output goes to `model.verbalization.txt`.

This file merges the schema-recovery base patterns with the text-first additions into one document. Rows that only apply to schema/code recovery (DDL-derived provenance prefixes, schema antipattern call-outs, introspection headers) are **marked "reserved — Phase 4 from-code recovery skill"** rather than deleted; no current GND skill emits them.

Cross-references:
- Per-constraint vocabulary → [constraint-reference.md](constraint-reference.md)
- YAML structure being verbalized → [representation-format.md](representation-format.md)
- Provenance taxonomy and modality semantics → [provenance-and-modality.md](provenance-and-modality.md)

## Halpin-grounded design

ORM 2's CNL principle: every model element should have a natural-language reading that a domain expert can validate **without seeing the diagram or the YAML**. The verbalization is the model's externalised meaning.

Each verbalization pattern below is grounded in Halpin's published examples, paraphrased to avoid copyright reproduction. Examples are ours.

Discipline:
- One sentence per claim. Compound sentences obscure where the burden of validation lies.
- Use object-type names verbatim from the YAML (PascalCase). The user matches them against their domain vocabulary.
- Provenance prefixes on inferred / proposed constraints — the user knows immediately which claims came from their own statements and which are inferred.

## Verbalization document structure

The full-model verbalization has the following sections in order:

```
=== Header ===
Designed via CSDP on <date>, <N> dialogue turns, mode=<guided|one-shot>.

=== Object Types ===
<one paragraph per object type>

=== Fact Types ===
<one paragraph per fact type, including its inline constraints and sample facts>

=== Top-level Constraints ===
<one paragraph per top-level constraint>

=== Operations ===
<v2 only; one line per operation, then one per precondition, dynamic rule,
 effect, and the frame — each under its own stable locator>

=== Antipattern Flags ===
<call-outs grouped by code>

=== Appendix: Rejected Proposals ===
<list with reasons>
```

Each section is a sequence of CNL paragraphs. Provenance prefixes mark non-explicit constraints. Empty sections are omitted — which is why a v1 model, and a `version: 2` model declaring no operations, render exactly as they did before v2 existed.

The `=== Operations ===` section belongs to the **review** verbalization only (`gnd.model_verbalization`). The constraint-blind rendering seed (`gnd.extract.vocabulary`, R-08″) emits operation READINGS and parameter phrases and nothing else: no preconditions, no dynamic rules, no effects, no frame, no modality word anywhere. An operation's obligations are exactly the kind of rule recital that teaches an extractor to emit the population the checker wants rather than the one the document contains.

*(Reserved — Phase 4 from-code recovery skill: the introspection-style header "Model from `<schema>`, introspected at `<timestamp>` via `<kind>`." for `sql`/`ddl-file`/`csv` source kinds.)*

## Object types

### Entity type with popular reference

Pattern:
> *{Name} is identified by {value-type-name}.*

Example:
> *Customer is identified by CustomerId.*

When the value type is not a primitive but another named entity (rare with `popular`):
> *{Name} is identified by its {value-type-name}.*

### Entity type with unit-based reference

Pattern:
> *{Name} is identified by a value in {unit} ({measure-type}).*

Example:
> *Height is identified by a value in cm (Length).*

### Entity type with general reference

Pattern:
> *{Name} is identified by {value-type-name}.* (same as popular)

Halpin distinguishes `general` from `popular` notationally; verbalization is the same since both abbreviate an injective binary fact type.

### Entity type with external (composite) reference

Pattern:
> *{Name} is identified by the combination of {role-1-CNL} and {role-2-CNL} ... .*

Example:
> *Enrolment is identified by the combination of student enrolment and course enrolment.*

The role CNLs come from the fact types referenced by the external UC.

### Value type

Pattern:
> *{Name} is a value of type {primitive}.*

Example:
> *EmailAddress is a value of type String.*

For `Number(p, s)`:
> *{Name} is a value of type Number with precision {p} and scale {s}.*

### Subtype

Pattern (with inherited reference / dashed arrow):
> *{Name} is a kind of {Supertype}, inheriting the reference of {Supertype}. {Derivation rule, if derived}.*

Pattern (with own reference / solid arrow):
> *{Name} is a kind of {Supertype}, identified by {value-type-name}. {Derivation rule, if derived}.*

Examples:
> *PhysicalProduct is a kind of Product, inheriting the reference of Product. Each PhysicalProduct is a Product whose Type is 'PHYSICAL'.*
> *Student is a kind of Person, identified by StudentNumber.*

### Independent flag

Append to any object type's verbalization when `independent: true`:
> *(Independent — instances may exist without playing any elementary fact roles.)*

## Fact types

### Binary fact type

Pattern (uniqueness on left role — 1:n):
> *{Reading-with-roles-instantiated-as-types}. Each {Left} {predicate-CNL} at most one {Right}.*

Example (`Customer has email EmailAddress` with UC on customer):
> *Customer has email EmailAddress. Each Customer has at most one EmailAddress.*

Pattern (m:n — spanning UC):
> *{Reading}. Each combination of {Left} and {Right} occurs at most once.*

Example:
> *OrderItem tagged with Tag. Each combination of OrderItem and Tag occurs at most once.*

Pattern (1:1 — UCs on both roles):
> *{Reading}. Each {Left} {predicate-CNL} at most one {Right}, and each {Right} {reverse-predicate-CNL} at most one {Left}.*

Example:
> *Person has nationalId NationalId. Each Person has at most one NationalId, and each NationalId is held by at most one Person.*

### Mandatory enrichment

When a role has a mandatory constraint, add an "at least one" sentence:
> *Each {ObjectType} has at least one {OtherType}.*

Combined with uniqueness:
> *Each Customer has exactly one EmailAddress.* (mandatory + uniqueness on the Customer role)

### Unary fact type

Pattern:
> *Each {Type} {predicate}.* — when mandatory.
> *Some {Type}s {predicate}.* — when not mandatory.

Examples:
> *Some Persons smoke.*
> *Each Order is rush-priority.* (when mandatory + Boolean-flag-style unary)

### Ternary+ fact type

Pattern:
> *{Reading-with-all-roles-instantiated}. Each combination of {role-tuple} {uniqueness-clause}.*

Example (with UC on `(person, sport)`):
> *Person played Sport for Country. Each combination of Person and Sport played one Country.*

### Self-referential fact type

Pattern:
> *{Reading} (with two roles on {Type}, named {role-name-1} and {role-name-2}).*

Example:
> *Person is parent of Person (with two roles on Person, named parent and child).*

The role-name annotation is essential — without it, the user can't tell which role is which.

### Objectified fact type

Pattern:
> *{Reading}. This is objectified as {Junction-name}{, which is independent if so}.*

Example:
> *Student enrolled in Course. This is objectified as Enrolment, which is independent (an Enrolment may exist before the grade is recorded).*

### Derived fact type

Pattern:
> *{Reading}. This fact type is derived: {derivation-rule}.*

Example:
> *Person speaks NrLanguages languages. This fact type is derived: For each Person, nrLanguages = count(languageSpoken).*

## Sample-population rendering

Text-first fact types carry `sample_population:` arrays — the user's actual examples from CSDP Step 1. Rendering them in the verbalization makes the population check visible.

### Pattern (canonical, in `audit` style)

```
Person was born in Country.
Each Person was born in exactly one Country. [from user statement, confirmed; turn 4]

Sample facts (user-provided at Step 1):
  John was born in Australia.
  Mary was born in Greece.
  Carlos was born in Spain.
```

### Pattern (summary style)

```
Person was born in Country.
Each Person was born in exactly one Country.

Sample facts: 3 examples confirmed (John/Australia, Mary/Greece, Carlos/Spain).
```

### When to expand vs compress

- **Expand fully** when sample size ≤ 5. The user can scan all examples.
- **Compress** when sample size > 5. Show first 3 + count. Available in full in the YAML's `sample_population`.

### Rendering rules

- Sample facts use the fact type's `reading`, with each role filled in by the sample value.
- Entity values render via the entity's reference-scheme identifier (e.g., a Customer's name if reference mode is `popular` with a name value type); primitive values render directly.
- Quote-style: single quotes around string values; integers/dates are bare.

## Constraints — by type

Each constraint's CNL pattern is also documented in [constraint-reference.md](constraint-reference.md). The patterns below are the canonical full-model verbalizations.

### Internal uniqueness

Inline within the fact type's paragraph (already covered by the fact-type pattern above).

### External uniqueness

Pattern:
> *Each combination of {role-1-CNL} and {role-2-CNL} ... identifies at most one {EntityType}.*

When `preferred: true`, append:
> *This is the preferred reference scheme of {EntityType}.*

### Mandatory

Inline with the fact-type paragraph (already covered).

### Mandatory-disjunctive

Pattern:
> *Each {ObjectType} {predicate-1} or {predicate-2}{ or … }.*

Example:
> *Each Visitor has Passport or has DriverLicence.*

### Object-type value (enumeration)

Pattern:
> *{ObjectType} must take one of: {v1}, {v2}, …, {vn}.*

Example:
> *Status must take one of: 'PENDING', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED'.*

### Object-type value (range)

Pattern (closed):
> *{ObjectType} must be between {min} and {max} (inclusive of {min}, {inclusive/exclusive} of {max}).*

Pattern (open above):
> *{ObjectType} must be at least {min}.*

Pattern (open below):
> *{ObjectType} must be at most {max}.*

Pattern (multi-range):
> *{ObjectType} must be in one of the ranges: {range-1}, {range-2}, ….*

### Role value (value constraint with `role_ref`)

A value constraint scoped by `role_ref` restricts only the values playing that
role, so its sentence names the role rather than the whole object type.

Pattern:
> *{ObjectType} playing role {fact_type}:{role} must take one of: {v1}, {v2}, …, {vn}.*

Example:
> *Text playing role building_has_type:type must take one of: ACADEMIC, RESIDENT, SERVICE.*

Checker verdict messages use the same scope: *Each text value playing the 'type' role
in 'building_has_type' must be one of ['ACADEMIC', 'RESIDENT', 'SERVICE']*.

### Subset

Pattern:
> *If {predicate-subset}, then {predicate-superset}.*

Example:
> *If a Person smokes, then that Person is cancer-prone.*

### Equality

Pattern:
> *A {ObjectType} {predicate-a} if and only if it {predicate-b}.*

Example:
> *A Patient has systolic-BP recorded if and only if it has diastolic-BP recorded.*

### Exclusion

Pattern:
> *No {ObjectType} {predicate-a} and {predicate-b}.*

Example:
> *No Person is married and widowed.*

### Exclusive-or

Pattern:
> *Each {ObjectType} either {predicate-a} or {predicate-b} (not both).*

For partition:
> *Each {ObjectType} is exactly one of: {Subtype-1}, {Subtype-2}, …, {Subtype-n}.*

### Frequency (internal)

Pattern (range):
> *Each {Reading-with-roles-fixed} appears at least {min} and at most {max} times.*

Pattern (exact):
> *Each {Reading-with-roles-fixed} appears exactly {n} times.*

Example:
> *Each panel that includes an expert includes at least 4 and at most 7 experts.*

### Frequency (external)

Pattern:
> *Each combination of {role-1-CNL}, {role-2-CNL} occurs at most {max} times.*

### Ring constraints

One sentence per variant (per the multi-variant policy).

| Variant | CNL pattern |
|---|---|
| `irreflexive` | *No {ObjectType} {predicate} itself.* |
| `asymmetric` | *If {a} {predicate} {b}, then not {b} {predicate} {a}.* |
| `intransitive` | *If {a} {predicate} {b} and {b} {predicate} {c}, then not {a} {predicate} {c}.* |
| `antisymmetric` | *If {a} {predicate} {b} and {b} {predicate} {a}, then {a} = {b}.* |
| `acyclic` | *{Reading} is acyclic — no chain of {predicate-instances} returns to its start.* |
| `symmetric` | *{a} {predicate} {b} if and only if {b} {predicate} {a}.* |
| `transitive` | *If {a} {predicate} {b} and {b} {predicate} {c}, then {a} {predicate} {c}.* |
| `purely-reflexive` | *Every {ObjectType} {predicate} itself (and nothing else).* |
| `reflexive` | *Every {ObjectType} {predicate} itself (other pairings allowed).* |

For combined named variants (e.g., `asymmetric-intransitive`) or multiple independent ring entries on one fact type, emit one sentence per component — one per assertion.

### Value-comparison

Pattern:
> *For each {ObjectType}, {role-a-CNL} is {comparison-natural} {role-b-CNL}.*

Comparison natural-language:
- `<` → "less than"
- `<=` → "less than or equal to"
- `=` → "equal to"
- `>=` → "greater than or equal to"
- `>` → "greater than"
- `!=` → "not equal to" (GND extension; see constraint-reference.md)

Example:
> *For each Project, end-date is greater than or equal to start-date.*

### Cardinality (object)

Pattern (exact):
> *There is exactly one {ObjectType}.*

Pattern (upper):
> *There are at most {max} {ObjectType}s.*

Pattern (lower):
> *There are at least {min} {ObjectType}s.*

Pattern (range):
> *There are at least {min} and at most {max} {ObjectType}s.*

### Cardinality (role)

Pattern:
> *At most {max} {ObjectType} plays the role of {role-name-natural}.*

### Subtype-partition

Patterns:

Full partition:
> *Every {Supertype} is exactly one of: {Subtype-1}, …, {Subtype-n}.*

Exclusive only:
> *No {Supertype} is more than one of: {Subtype-1}, …, {Subtype-n}.*

Exhaustive only:
> *Every {Supertype} is at least one of: {Subtype-1}, …, {Subtype-n}.*

### Textual

Pattern:
> *[textual constraint] {expression}*

The bracketed prefix marks that this is a textual constraint, not a structured constraint type.

## Provenance prefixes

Every constraint sentence is prefixed with its provenance, so the user knows whether it came from their own words or was inferred. The text-first prefixes add dialogue-turn references so the reviewer can trace each claim back to where it came from in the conversation.

### Text-first prefix table (current GND authoring)

| `source` | `status` | Prefix template |
|---|---|---|
| `explicit` | `confirmed` | `[from user statement, confirmed; turn N]` |
| `sample` | `confirmed` | (rare in text-first — would require very high confidence; typically stays proposed) |
| `sample` | `proposed` | `[from sample population, proposed; turn N]` |
| `common-sense` | `confirmed` | `[from common-sense library, confirmed; CSDP step N]` |
| `common-sense` | `proposed` | `[from common-sense library, proposed; CSDP step N]` |
| `llm-inferred` | `confirmed` | `[from LLM inference, confirmed at Step 7b; turn N]` |
| `llm-inferred` | `proposed` | `[from LLM inference, proposed]` |
| `user-supplied` | `confirmed` | `[user-supplied at Step 7d, turn N]` |

When `modality: deontic`, append `deontic — should rule, possibly violated`:

> *[user-supplied at Step 7d, turn 42; deontic — should rule, possibly violated] Each Customer should pay within 30 days.*

### Schema-recovery prefix table *(reserved — Phase 4 from-code recovery skill)*

| Source | Status | Prefix |
|---|---|---|
| `explicit` | `confirmed` | `[from PK]`, `[from UNIQUE]`, `[from NOT NULL]`, `[from CHECK]`, `[from FK]`, `[from UNIQUE INDEX]` |
| `sample` | `confirmed` | `[from sample data, confirmed]` |
| `sample` | `proposed` | `[from sample data, proposed]` |

No current GND skill emits these; they are retained for the from-code recovery skill so the prefix vocabulary stays stable.

### When to include dialogue-turn references

- Always in the **canonical** verbalization for review (`style: audit`, the default).
- Optionally elided in a **stakeholder-summary** verbalization (`style: summary`) if the audience doesn't need audit trails.

## User-quote citation

For constraints with `source: explicit | user-supplied`, the YAML carries `provenance.user_quote` — the user's actual words. The verbalization cites the quote inline.

### Pattern

> *[from user statement at turn 4] Each Person was born in exactly one Country. (User said: "Each person has one country of birth, no exceptions.")*

The quote is in parentheses to keep the constraint sentence parseable; the trace makes the verbalization auditable in conversation terms.

### When to include the quote

- Always for **`source: explicit`** constraints — the quote is the *evidence* for the constraint.
- Always for **`source: user-supplied`** constraints — the user added the rule, the quote captures their original phrasing.
- Optionally for **`source: common-sense | llm-inferred` constraints the user confirmed** — the confirmation might have a user quote attached (e.g., "yes, that's right" or "yes but only in retail").

### Length cap

If the user quote is > 200 characters, truncate with `…` and link to the full quote in the YAML:

> *[from user statement at turn 12] Each Order has at most 50 line items. (User said: "OK so each order has at most fifty line items — we capped that in the system five years ago because…" [truncated; full quote in `model.orm.yaml`])*

## Antipattern call-outs

Antipattern flags appear in their own section (after Top-level Constraints, before the Appendix). Pattern:

> *⚠ {AntipatternCode} on {entity-or-fact-type}: {one-line description}. Default resolution: {default-resolution}. {Detail.}*

Text-first antipatterns (over-decomposition, attribute-as-subtype, redundant entity types) are documented in the authoring skill's workflow reference.

*(Reserved — Phase 4 from-code recovery skill: schema antipattern call-outs such as denormalized-address, ambiguous-junction-with-extras, encoded-enum-in-varchar.)*

## Appendix: rejected proposals

Pattern:
> *{Original-CNL-of-the-rejected-constraint}. Rejected on {date}: {reason}.*

Example:
> *Order precedence is acyclic. Rejected on 2026-05-04: domain explicitly allows reissues that point back to predecessors.*

The appendix lets future runs read what was already rejected, and lets reviewers see "we considered this and decided no."

## Worked snippet (text-first verbalization)

For a small movie-catalog authoring run, the canonical verbalization output reads (excerpts):

```
=== Model overview ===
Designed via CSDP on 2026-05-14, 47 dialogue turns, mode=guided.

=== Object Types ===

Movie is identified by MovieId.
[from user statement, confirmed; turn 3] Movie is identified by movie-id.
(User said: "Each movie has a unique numeric ID, we generate them on creation.")

Director is identified by DirectorName.
[from user statement, confirmed; turn 7] Director is identified by name.
(User said: "Directors are identified by their full name — we don't have an ID system for them.")

(Independent — instances may exist without playing any elementary fact roles.)
[from common-sense, confirmed at Step 7b; CSDP step 6] Director is independent.

=== Fact Types ===

Movie has title.
[from user statement, confirmed; turn 4] Each Movie has exactly one title.
(User said: "Movies have one canonical title in our catalog.")

Sample facts (user-provided at Step 1):
  Movie #1 has title 'The Departed'.
  Movie #2 has title 'Inception'.
  Movie #3 has title 'Parasite'.

Movie directed by Director.
[from user statement, confirmed; turn 5] Each Movie is directed by exactly one Director.
(User said: "Sole-director credit only in our catalog — for co-directed films we pick one.")
[from common-sense library, proposed; CSDP step 6] Each Director directs at least one Movie.

Sample facts:
  The Departed directed by Martin Scorsese.
  Inception directed by Christopher Nolan.
  Parasite directed by Bong Joon-ho.

Movie has rating Rating.
[from user statement, confirmed; turn 8] Rating must be one of: G, PG, PG-13, R, NC-17.
(User said: "MPAA ratings only — we use the five-tier system.")

=== Top-level Constraints ===

[user-supplied at Step 7d, turn 39; deontic — should rule]
Movies should be released no later than 5 years after production began. (Soft business rule for our catalog freshness; not enforced.)

=== Antipattern Flags ===

(None — clean run.)

=== Appendix: Rejected Proposals ===

[from LLM inference, rejected at Step 7b, turn 33] Each Director has at most one nationality.
Reason: "Dual citizens exist in our catalog — Christopher Nolan is British/American."
```

The verbalization is dialogue-first: every constraint traces back to a turn, and many cite the user's actual words. This is the primary review surface — a stakeholder can read it without seeing the YAML or the original conversation, and validate or challenge each claim.

## Halpin-compatibility checks

The verbalization should pass two tests:

1. **The "domain expert read-aloud" test.** Hand the verbalization to someone who knows the domain but not ORM 2 or SQL. They should be able to read each sentence and either confirm or challenge it. If a sentence references a Halpin term the reviewer doesn't know (e.g., "objectification"), simplify or add a brief inline gloss.

2. **The "round-trip" test.** Take the verbalization, hand it to an ORM-trained modeler with no access to the YAML, and ask them to reconstruct the model. The reconstructed model should match the original modulo formatting. If structure is missing (e.g., a constraint exists in the YAML but doesn't appear in the verbalization), the verbalization is incomplete.

Both tests should pass on every full-model verbalization. If they don't, fix the verbalization, not the YAML.

## What this format does NOT cover

- **Localization.** English only. Halpin's CNL extends to other languages; GND doesn't yet.
- **Verbalization editing as a guided path.** When the user wants to rewrite a reading (e.g., `"Order placed by Customer"` → `"Order is from Customer"`), they edit the YAML's `reading:` field directly.
- **Diagram rendering.** No ASCII / SVG diagram generation. Verbalization is text-only.
- **FORML 2 verbalization.** Textual constraints render as the raw `expression`; no formal-language translation.

---
*Adapted from the rai-agent-skills ORM skills (branch an-orm-skill).*


### Temporal guarded comparisons (v7.1)

Use “calendar days after” for `date_add` and “calendar days before” for
`date_sub`; retain the declared comparison operator. Use the
[calendar-day terms](representation-format.md#calendar-day-terms-v71) contract
for typing, limits, unchecked outcomes and supported consumers. A temporal
check message describes the established decision without recounting its join.


### Reference ownership

Model verbalization names each fixed reference and the base fact types it owns.
Rendered candidate facts must retain candidate provenance: supplied fixed facts
are inputs to checking, not output produced by the candidate. Consult
[representation-format.md](representation-format.md#fixed-reference-populations-version-4)
for binding, ownership and the closed origin report.
