# Constraint Reference

Per-constraint vocabulary. For each ORM 2 constraint family: a short description, the ORM 2 graphical signal it corresponds to (described in words — diagrams are not reproduced; see Halpin's published work for the visual reference), the YAML form, the controlled-natural-language (CNL) verbalization template, and whether the `gnd` deterministic checker can mechanically evaluate it over a population.

Cross-references:
- YAML structural detail → [representation-format.md](representation-format.md) (normative machine spec: [orm-meta.schema.json](orm-meta.schema.json))
- CNL grammar overall → [verbalization-patterns.md](verbalization-patterns.md)
- Provenance/modality semantics → [provenance-and-modality.md](provenance-and-modality.md)
- Population semantics the checker evaluates against → [population-format.md](population-format.md)

**Checkability values used below:**
- **yes** — the checker evaluates the constraint over any population covering its subject fact types.
- **partial-observable** — the checker evaluates the constraint when the needed facts are observable in the population; otherwise it reports `unchecked` with the stated reason.
- **unchecked** — the checker never evaluates this family; every verdict is `unchecked` with the stated reason (a constraint is never silently passed).

Violated alethic constraints produce verdict `fail`; violated deontic constraints produce `warning`. See [provenance-and-modality.md](provenance-and-modality.md).

On a version-2 population, an opaque value in a role that a constraint reads yields `unchecked` with `opaque-value`; an opaque value in an unselected role does not itself change that constraint's verdict. Its label never appears as a witness. When admission is requested, the version-10 report partitions asserted fact occurrences into `admitted` and `blocked` using their `fact_type` and zero-based `index`. Typed verdict references identify asserted occurrences only; a computed derived tuple's relation position is not an asserted occurrence address. Alethic failures and unchecked verdicts block directly implicated occurrences and their typed-reference or `depends_on` descendants. An occurrence join uses only a value type named by an entity reference scheme; matching values in ordinary nonidentifying roles do not create an edge. Deontic warnings alone do not block. Admitted rows list opaque dependency locations as fact references and role names, without labels. A global unchecked verdict without a fact reference keeps its original exit band and leaves the occurrence partition unblocked. This is a report projection; it does not rewrite facts or verdicts.

## Quick reference

| Constraint family | Placement | Checkable by gnd checker |
|---|---|---|
| Internal uniqueness | inline | yes |
| External uniqueness | top-level | yes |
| Mandatory | inline | yes (closed-world instance set) |
| Mandatory-disjunctive | top-level | yes |
| Value (enum / range / ranges / role-scope hybrid) | inline + top-level | yes |
| Frequency (internal) | inline | yes |
| Frequency (external) | top-level | yes |
| Ring (all 13 variants) | inline | yes |
| Subset | top-level | yes |
| Equality | top-level | yes |
| Exclusion | top-level | yes |
| Exclusive-or | top-level | yes (multi-role sequences: exclusion component only) |
| Value-comparison | inline + top-level | yes, except current-time operands → unchecked |
| Cardinality (object / role) | top-level | yes |
| Subtype-partition | top-level | partial-observable |
| Guarded | top-level | yes — atom, comparison, and absence consequents; see [representation-format.md](representation-format.md#guarded-constraints) |
| Anchored | inline | yes with bound document and anchor sidecar; otherwise unchecked |
| Textual | top-level | unchecked |

## Source anchoring (v7.0)

An inline `anchored` constraint asks whether each populated value in its covered role has a source witness. An optional `role` selects one declared role; without it every role of the fact type is covered. `source`, `status`, `modality`, and provenance follow the common constraint fields. `recognise` is an optional nonempty list on a selected role, with the exact values `integer`, `decimal`, `percent`, and `iso-8601-date`; its members must fit the role's primitive. An empty covered string is rejected during population validation.

The anchor sidecar is version 1 JSON at `<population>.anchors.json`. It contains raw-byte SHA-256 digests of the population and document, plus `vocabulary_digest`: canonical UTF-8 JSON of the model's `object_types` and `fact_types`, omitting each object type's `description` and each fact type's `derivation_rule`, `constraints`, `sample_population`, and `depends_on` (see [representation-format.md](representation-format.md)). Each anchor has a complete fact key, role, zero-based occurrence, half-open source span, and SHA-256 digest of the NFC document slice. The span counts NFC Unicode code points. A malformed sidecar or mismatch of any digest, span, or excerpt is an input refusal at exit 3. A present sidecar always binds before value matching.

Lexical matching NFC-normalizes, casefolds, converts curly quotes and U+2010–U+2015 hyphens to their ASCII counterparts, converts nonbreaking spaces to spaces, collapses whitespace, and requires a whole-token substring. Occurrences count from zero across the whole document. The selected match must lie wholly inside the anchor span. Recognisers match exact signed numeric values or calendar-valid ISO dates; percent compares the population number directly to the percentage written in the document. No value is rewritten. A missing or nonmatching witness is `fail` for alethic and `warning` for deontic constraints. A nonlexical value without a declared recogniser is `unchecked` with `anchor-non-lexical`, unless another covered value definitely fails. An absent sidecar is `unchecked` with `anchor-sidecar-absent`; an empty fact type is `vacuous`. Alethic uncertainty exits 4.

`gnd check MODEL POPULATION --anchors PATH --document PATH` supplies bound source bytes. `gnd verify` uses the adjacent anchor sidecar with its extraction document when present. The Python API accepts path or typed sidecar and path or bytes for the document; in-memory populations require their original raw bytes to bind. The PyRel exporter and population-only synthesis and measurement lanes do not evaluate source anchoring.

## Internal uniqueness (UC)

Asserts that within a single fact type, each combination of objects in a designated role (or role sequence) appears at most once across the population.

**ORM 2 graphical signal:** a horizontal bar drawn across the role boxes covered by the UC. A double bar marks the *preferred* internal UC — the one that underlies the entity type's preferred reference scheme. A dotted line excludes a role from a spanning UC (rare).

**YAML form (inline):**
```yaml
constraints:
  - type: uniqueness
    roles: [<role_name_1>, <role_name_2>, …]    # role(s) covered by the bar
    preferred: false                            # double-bar?
    source: explicit | sample | common-sense | llm-inferred | user-supplied
    status: confirmed | proposed
    modality: alethic | deontic                 # required
```

For binaries the four standard patterns:

| Pattern | Roles covered | Reading semantics |
|---|---|---|
| 1:n (UC on left) | `[A]` | A is unique; each A pairs with at most one B |
| n:1 (UC on right) | `[B]` | B is unique; each B pairs with at most one A |
| m:n (spanning UC) | `[A, B]` | Combination unique; neither alone unique |
| 1:1 (two separate UCs) | one `[A]`, one `[B]` | Both sides unique |

For *n*-ary fact types (n>2), each UC covers at least n-1 roles.

**CNL verbalization template (per standard pattern):**
- 1:n: *"Each {Reading-with-A-fixed} involves at most one {B}."*
- n:1: *"Each {Reading-with-B-fixed} is from at most one {A}."*
- m:n: *"Each {A,B} pairing occurs at most once."*

**Checkable by gnd checker:** yes — facts are grouped by the covered role values; any group with more than one fact fails, and the message names the duplicated values.

## External uniqueness

Asserts that a tuple of objects drawn from roles across **multiple fact types** appears at most once across the joint population. Used for composite identifiers — entities identified by several binary fact types together rather than a single one.

**ORM 2 graphical signal:** a UC bar connected via dotted lines to one role on each of two or more separate fact types. Double bar marks the preferred external identifier.

**YAML form (top-level):**
```yaml
constraints:
  - type: uniqueness
    scope: external
    role_refs:
      - { fact_type: <ft_id_1>, role: <role_name> }
      - { fact_type: <ft_id_2>, role: <role_name> }
    preferred: true                             # is this the entity's preferred composite identifier?
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"Each combination of ({Role1 verbalised in its fact type}, {Role2 verbalised in its fact type}, …) identifies at most one {EntityType}."*

When `preferred: true`:
*"…and serves as the preferred reference scheme for {EntityType}."*

**Checkable by gnd checker:** yes — the checker joins the referenced fact types on their shared-object-type anchor roles (the non-referenced roles) and counts composite tuples; a duplicated composite tuple is named in the failure message.

## Mandatory role

Asserts that every instance of the object type at one end of a role plays that role at least once.

**ORM 2 graphical signal:** a filled dot on the role connector at the end of the object type that must play the role.

**YAML form (inline):**
```yaml
constraints:
  - type: mandatory
    role: <role_name>
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"Each {ObjectType} {predicate-with-other-roles}."*

For a binary fact type *Customer has email EmailAddress* with mandatory on `customer`:
*"Each Customer has at least one EmailAddress."*

**Checkable by gnd checker:** yes — relative to the closed-world instance set (every value playing a role typed by the object type across the population, plus optional explicit `instances:` rosters; see [population-format.md](population-format.md)). An instance observed anywhere that lacks its mandatory role fails. If the subject fact type is omitted from the population's declared `covers`, the verdict is `vacuous` — the population does not claim completeness for it.

## Mandatory-disjunctive (inclusive-or)

Asserts that each instance of an object type plays at least one role from a set of two or more roles, possibly across different fact types.

**ORM 2 graphical signal:** a circled dot connecting the relevant roles. Adjacent or non-adjacent roles allowed.

**YAML form (top-level):**
```yaml
constraints:
  - type: mandatory-disjunctive
    role_refs:
      - { fact_type: <ft_id_1>, role: <role_name> }
      - { fact_type: <ft_id_2>, role: <role_name> }
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"Each {ObjectType} {predicate-1} OR {predicate-2} (or both)."*

Example:
*"Each Visitor has Passport or has DriverLicence."*

**Checkable by gnd checker:** yes — an instance (from the closed-world instance set) playing none of the listed roles fails. Coverage-omission vacuity applies: if any subject fact type is omitted from `covers`, the verdict is `vacuous`.

## Object-type value constraint (enumeration)

Restricts the allowed values of an object type to a finite enumerated set.

**ORM 2 graphical signal:** brace-enclosed list adjacent to the object type — `{'M', 'F'}`.

**YAML form (top-level):**
```yaml
constraints:
  - type: value
    object_type: <ot_id>
    allowed: ['v1', 'v2', …]
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"{ObjectType} must take one of: {v1}, {v2}, …."*

**Checkable by gnd checker:** yes — membership test over every value of the object type observed in the population. "Observed" is the closed-world population of [population-format.md](population-format.md#closed-world-object-type-population-semantics), which for a **value type** includes the values that identify entities under a reference scheme — see [the note below](#a-constraint-on-a-reference-value-type-constrains-the-identifying-values-in-facts).

## Object-type value constraint (range)

Restricts the allowed values of an object type to one or more numeric / character ranges.

**ORM 2 graphical signal:** brace-enclosed range expression — `{0..100}`, `{1..7}`, `{(0..100]}`. Round bracket excludes endpoint; square bracket includes (default).

**YAML form (top-level), single range:**
```yaml
constraints:
  - type: value
    object_type: <ot_id>
    range:
      min: 0
      max: 100
      min_inclusive: true                       # default true
      max_inclusive: false
    source: …
    status: …
    modality: …
```

**Multiple disjoint ranges** use the `ranges:` list form (see [representation-format.md](representation-format.md)).

Open-ended ranges: omit `max` (or `min`).

**Role-scope hybrid form:** `object_type` names a primitive plus `role_ref` narrows the scope to a specific role — used when a generic primitive (e.g., Integer) appears in multiple roles that each want different bounds.

**CNL verbalization template:**
- Closed: *"{ObjectType} must be between {min} and {max} (inclusive of {min}, exclusive of {max})."*
- Open-ended: *"{ObjectType} must be at least {min}."*

**Checkable by gnd checker:** yes — numeric/date comparison per observed value; the role-scope hybrid narrows the checked values to those playing the referenced role.

### A constraint on a reference value type constrains the identifying values in facts

When `object_type` names a **value type that identifies an entity type**, the constraint ranges over the identifying values that appear in facts. `movie: 999999` in a fact *is* a MovieId occurrence — [population-format.md](population-format.md#entity-references): *"Entity values in facts use the entity's reference-scheme value … `movie: 1` means the Movie whose MovieId is 1"* — so a `value` range or `allowed` set on `movie_id`, and equally a `cardinality` bound on it, is evaluated against those values. No role has to be typed to `movie_id` for this to hold.

The reasoning matters more than the rule, because the opposite reading is what shipped: the loader resolves `movie → reference.value_type` in order to **type-check** `999999` as an Integer MovieId, and rejects the population at exit 3 if it is not one. Having asserted that the value *is* a MovieId, the checker cannot coherently refuse to range-check it as one — one value cannot be a MovieId for typing and not a MovieId for constraints. While it did refuse, this shape reported `pass` — *"Each movie_id value must be between '1' and '100' — satisfied."* — at **exit 0** with `acceptance_ready: true`, over a population whose only fact carried `movie: 999999`.

Direction, stated so it is not re-derived the other way: a **value** type collects the values denoting entities it identifies; an **entity** type collects nothing from its reference value type. Widening both ways would manufacture false alethic failures, which is the strictly worse error — reference values appear in facts on every conforming run.

The **role-scope hybrid** form (`object_type` + `role_ref`) is unaffected: it narrows the checked values to one role by construction and always evaluated correctly.

## Subset

Asserts that the population at one role sequence is always a subset of the population at another role sequence (compatible types).

**ORM 2 graphical signal:** a dotted arrow from the subset role sequence to the superset role sequence, marked with `⊆`.

**YAML form (top-level):**
```yaml
constraints:
  - type: subset
    subset_role_seq:
      - { fact_type: <ft_id>, role: <role_name> }
    superset_role_seq:
      - { fact_type: <ft_id>, role: <role_name> }
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"If {predicate-subset}, then {predicate-superset}."*

Example:
*"If a Person smokes, then that Person is cancer-prone."*

**Join subset:** when the projection spans a join path, the subset references multiple roles in each sequence; the checker joins multi-fact-type sequences on their shared object types before comparing.

**Checkable by gnd checker:** yes — role-sequence projection set algebra; tuples in the subset sequence missing from the superset sequence are named in the failure message.

## Equality

Asserts that two role-sequence populations are identical.

**ORM 2 graphical signal:** dotted line between the two role sequences with `=` mark.

**YAML form (top-level):**
```yaml
constraints:
  - type: equality
    role_seq_a:
      - { fact_type: <ft_id>, role: <role_name> }
    role_seq_b:
      - { fact_type: <ft_id>, role: <role_name> }
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"A {ObjectType} {predicate-a} if and only if it {predicate-b}."*

Example:
*"A Patient has systolic-BP recorded if and only if it has diastolic-BP recorded."*

**Checkable by gnd checker:** yes — set equality over the two projections; asymmetric differences are named per side.

## Exclusion

Asserts that two role-sequence populations never overlap.

**ORM 2 graphical signal:** dotted line between the two role sequences with `⊗` mark.

**YAML form (top-level):**
```yaml
constraints:
  - type: exclusion
    role_seq_a: …
    role_seq_b: …
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"No {ObjectType} {predicate-a} and {predicate-b}."*

Example:
*"No Person is married and widowed."*

**Checkable by gnd checker:** yes — set intersection over the two projections must be empty; overlapping tuples are named.

## Exclusive-or (xor — partition)

Inclusive-or + exclusion: every instance plays exactly one role from the set.

**ORM 2 graphical signal:** circled dot (mandatory-disjunctive) combined with `⊗` exclusion marker.

**YAML form (top-level):**
```yaml
constraints:
  - type: exclusive-or
    role_seqs:
      - [{ fact_type: <ft_id_1>, role: <role_name> }]
      - [{ fact_type: <ft_id_2>, role: <role_name> }]
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"Each {ObjectType} either {predicate-a} or {predicate-b}, but not both."*

**Checkable by gnd checker:** **partial — depends on sequence arity.**

- **Single-role sequences (the Halpin-typical case): yes, fully.** A real object-type population exists, so both components are decided: instances playing both roles AND instances playing neither, against the closed-world instance universe.
- **Multi-role sequences: only the exclusion component.** An ORM 2 exclusive-or is the orthogonal combination of two component constraints, and they take different argument types (Halpin, *ORM 2 Technical Report* §2.7–2.8): **exclusion** takes compatible role *sequences*, while **inclusive-or / disjunctive mandatory** takes a set of *roles played by one object type* and quantifies over that object type's instance population. There is no ORM 2 construct "disjunctive mandatory over multi-role sequences", so at arity > 1 the disjunctive half has **no universe to quantify over at all**.

  The checker therefore evaluates the exclusion half and reports the constraint as follows:

  | Exclusion half | Verdict | Exit band |
  |---|---|---|
  | A tuple appears in more than one sequence | `fail` (alethic) / `warning` (deontic) | 1 — a witness proves violation whichever way the undecidable half would have gone |
  | No overlap found | `unchecked`, `reason_code: xor-disjunctive-undefined` | 4 — indeterminate, **never `pass`** |

  A clean exclusion half is **not** a satisfied constraint: half of it was never evaluated, and reporting `pass` there would be an affirmative claim of acceptance over a component the checker cannot reach. Synthesising the missing universe as a position-wise Cartesian product of the sequences' object-type populations is **not** the fix — it would assert "every person either teaches or takes *every* course", which is strictly stronger than ORM semantics and almost always false, trading a false pass for a false fail. Declare single-role sequences if the disjunctive half must be decided.

## Frequency — internal

Restricts how many times an instance may appear in a role or role sequence within a single fact type.

**ORM 2 graphical signal:** numeric annotation above the role boxes — `12`, `4..7`, `≤5`, `≥2`, `2`. Range bounds inclusive on both ends.

**YAML form (inline):**
```yaml
constraints:
  - type: frequency
    scope: internal
    roles: [<role_name>, …]                     # the roles the bound applies to
    bound: { min: 2, max: 7 }                   # use omitted/null for open ends
    source: …
    status: …
    modality: …
```

For exact-count (`12`): `bound: { min: 12, max: 12 }`. For `≤5`: `bound: { max: 5 }`.

**CNL verbalization template:**
- Range: *"Each {Reading-with-roles-fixed} appears at least {min} and at most {max} times."*
- Exact: *"Each {Reading-with-roles-fixed} appears exactly {n} times."*
- Upper bound only: *"Each {Reading-with-roles-fixed} appears at most {max} times."*

Example: *"Each panel that includes an expert includes at least 4 and at most 7 experts."*

**Checkable by gnd checker:** yes — group counts per covered-role value vs the bound. Per Halpin semantics, the `min` bound applies to *occurring* groups (a group must appear at least min times if it appears at all).

## Frequency — external

Restricts how many times a tuple appears across multiple fact types.

**YAML form (top-level):**
```yaml
constraints:
  - type: frequency
    scope: external
    role_refs:
      - { fact_type: <ft_id>, role: <role_name> }
      - { fact_type: <ft_id>, role: <role_name> }
    bound: { min: 1, max: 2 }
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"Each combination of {role-1-CNL}, {role-2-CNL} occurs at most {max} times."*

**Checkable by gnd checker:** yes — same group-count logic over the joined tuple population.

## Ring constraints

Apply to binary fact types where both roles are hosted by the same object type (or related supertypes). ORM 2 catalogues 11 named variants plus two "considering" additions in Halpin's reference work.

**Variants and their semantics:**

| Variant | Asserts |
|---|---|
| `irreflexive` | No element relates to itself |
| `asymmetric` | If `a R b` then not `b R a` (also irreflexive) |
| `intransitive` | If `a R b` and `b R c` then not `a R c` |
| `antisymmetric` | If `a R b` and `b R a` then `a = b` |
| `acyclic` | No cycles of any length |
| `asymmetric-intransitive` | Combination of the above two |
| `acyclic-intransitive` | Combination |
| `symmetric` | `a R b` iff `b R a` |
| `symmetric-irreflexive` | Combination |
| `symmetric-intransitive` | Combination |
| `purely-reflexive` | Every participating element relates to itself **and nothing else** — the relation is a subset of identity: `∀x∀y(xRy → x = y)` |
| `reflexive` | **Locally** reflexive: `∀x∀y(xRy → xRx)` — if an element relates to *anything*, it relates to itself. Elements that play no role in the relation are **not** constrained |
| `transitive` | (Halpin "considering" addition) If `a R b` and `b R c` then `a R c` |

### `reflexive` is LOCAL, not global — and the distinction is load-bearing

Halpin, *ORM 2 Graphical Notation* (2023-10-06, p. 6), names the ORM 2 variant literally **"Reflexive (locally)"** and defines it:

> "A ring predicate R is **locally reflexive** if and only if, for all x and y, **xRy implies xRx**. E.g. 'knows' is locally but not globally reflexive."

The quantification is over the relation's **participants**, never over the object type's whole population. Halpin's own counter-example is decisive:

> "In ORM you may declare the predicate 'knows' to be locally reflexive **even when the universe of discourse includes objects like cars where the predicate does not apply at all**."

Contrast the two readings:

| Reading | Formula | Domain of quantification |
|---|---|---|
| Reflexive (**globally**) — *not* what ORM 2's `reflexive` means | `∀x xRx` | every instance of the object type |
| **Locally reflexive** — what ORM 2's `reflexive` means | `∀x∀y(xRy → xRx)` | only individuals that participate in the relation |

So a roster member that plays no role in the relation satisfies a `reflexive` ring constraint vacuously, and the checker reporting `pass` for it is **correct**, not a missed violation. This paragraph replaces an earlier unscoped wording ("every element relates to itself") that read as the *global* variant. That wording was the proximate cause of a proposal to widen the checker's element universe to `_instances_of(object_type)` — a change measured to convert a conforming in-tree fixture from `pass 13, fail 0` into `pass 11, fail 2`, i.e. two **false alethic failures**, produced by a change whose stated purpose was eliminating false passes. Do not re-derive that proposal from a looser reading of this row.

**GND's deliberate conservative reading of "participants".** Halpin's formula quantifies `xRy → xRx` over the **first** argument, so strictly only the relation's *domain* is constrained. GND derives the element set as **domain ∪ range**, so `(1,2)` requires both `(1,1)` and `(2,2)`. That is *stricter* than Halpin, and the direction of the error is a false **fail**, never a false pass — the safe side. It is a recorded choice, not an oversight: aligning to the domain-only formula is a stricter→looser change that needs a new violating fixture, and is deferred to a phase that revisits it against the primary source.

**ORM 2 graphical signal:** a distinct ring glyph adjacent to the role connector, one per variant. Deontic ring constraints use dashed lines instead of solid.

**YAML form (inline, on the binary fact type):**
```yaml
fact_types:
  - id: person_parent_of_person
    reading: "{Person} is parent of {Person}"
    roles:
      - { object_type: person, role_name: parent }
      - { object_type: person, role_name: child }
    constraints:
      - type: ring
        variant: acyclic
        source: common-sense
        status: proposed
        modality: deontic
        rationale: "Parenthood is acyclic by structural assumption."
```

**Multi-variant policy:** independent single-variant assertions like *asymmetric* + *irreflexive* are emitted as **separate `ring` entries**. The combined variants (`asymmetric-intransitive`, `acyclic-intransitive`, `symmetric-irreflexive`, `symmetric-intransitive`) exist in the vocabulary for Halpin's named combinations; the checker evaluates each component of a combined variant.

**CNL verbalization template (per variant):**
- `irreflexive`: *"No {ObjectType} {reading-with-self} itself."*
- `asymmetric`: *"If {reading}, then not {reverse-reading}."*
- `acyclic`: *"{Reading} is acyclic — no chain of {readings} returns to its start."*
- `symmetric`: *"{Reading} if and only if {reverse-reading}."*
- `transitive`: *"If {a} {predicate} {b} and {b} {predicate} {c}, then {a} {predicate} {c}."*
- `intransitive`: *"If {a} {predicate} {b} and {b} {predicate} {c}, then not {a} {predicate} {c}."*

**Checkable by gnd checker:** yes — all 13 variants. Pairwise variants use set logic over the binary fact population; `acyclic` uses cycle detection and the failure message names the full cycle (e.g., *"cycle through '3' → '1' → '2' → '3'"*); combined variants evaluate each component and report the first violated one.

## Value-comparison

Asserts a comparison between two roles using `<`, `≤`, `=`, `≥`, `>`, or `≠` (`!=`).

**ORM 2 graphical signal:** annotation `≥`, `≤`, `=`, `<`, `>` between two roles. ORM 2 has no canonical glyph for `≠`; GND emits `operator: "!="` as an extension to cover same-type "must be distinct" cases (e.g., transfer from-warehouse ≠ to-warehouse). Verbalized in CNL as *"… is not equal to …"*.

**YAML form:**

Inline (intra-fact-type):
```yaml
constraints:
  - type: value-comparison
    operator: ">="
    role_a: { role: <role_name> }
    role_b: { literal: <scalar> }
    source: …
    status: …
    modality: …
```

Tagged operands distinguish role names from literals without guessing from a
string's spelling. A literal may be any population scalar, so Boolean literals
are written as `{ literal: true }` and a String literal such as `"001"` remains
`{ literal: "001" }`. Legacy bare-string operands remain accepted for existing
models; a legacy literal is interpreted using the other operand's resolved
primitive rather than by numeric-looking spelling.

Top-level (cross-fact-type):
```yaml
constraints:
  - type: value-comparison
    operator: ">="
    role_a: { fact_type: <ft_id>, role: <role_name> }
    role_b: { fact_type: <ft_id>, role: <role_name> }
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"For each {ObjectType}, {role-a-CNL} {operator-natural} {role-b-CNL}."*

Example:
*"For each Project, end-date is greater than or equal to start-date."*

**Checkable by gnd checker:** yes for role-to-role, literal, and cross-fact-type operands — numeric or lexical (ISO-8601 date string) comparison. **Exception:** an operand referencing the current time (`NOW()`, `TODAY`, `CURRENT_DATE`, `CURRENT_TIME`, `CURRENT_TIMESTAMP` — optional parens, case-insensitive) makes the constraint `unchecked`; the checker's message states that a reference clock is out of scope this phase.

## Cardinality — object

Constrains the number of instances of an object type at any time.

**ORM 2 graphical signal:** `# = N`, `# ≤ N`, etc. adjacent to the object type.

**YAML form (top-level):**
```yaml
constraints:
  - type: cardinality
    scope: object
    object_type: <ot_id>
    bound: { min: 1, max: 1 }
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
- Exact: *"There is exactly one {ObjectType}."*
- Upper bound: *"There are at most {max} {ObjectType}s."*
- Lower bound: *"There are at least {min} {ObjectType}s."*

**Checkable by gnd checker:** yes — the closed-world derived instance count for the object type is compared against the bound. When the object type is a **reference value type**, the count includes the identifying values appearing in facts ([note above](#a-constraint-on-a-reference-value-type-constrains-the-identifying-values-in-facts)); until it did, this family printed its own blindness — *"The number of movie_id instances is at most 2 — satisfied (0 observed)"* over a population holding four.

## Cardinality — role

Constrains the number of instances playing a particular role.

**ORM 2 graphical signal:** `# ≤ N` etc. adjacent to a single role.

**YAML form (top-level):**
```yaml
constraints:
  - type: cardinality
    scope: role
    role_ref: { fact_type: <ft_id>, role: <role_name> }
    bound: { max: 1 }
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
*"At most {max} {ObjectType} plays the role of {role-name-natural}."*

**Checkable by gnd checker:** yes — the count of distinct values playing the referenced role is compared against the bound.

## Subtype-partition

Asserts a partition over a supertype's instances by a set of subtypes. Independently encodes:
- `exclusive: true` — no instance is in two subtypes (Halpin's circled X).
- `exhaustive: true` — every supertype instance is in at least one subtype (Halpin's circled dot).

Both true → full partition. Either alone → weaker constraint.

**At least one must be true.** ORM 2 defines a subtype partition as the conjunction of subtype exclusion and subtype totality (Halpin 2e §6.5), so the three verbalizations below are the only readings there are — there is no "neither" reading. A `subtype-partition` setting neither flag (or setting both to `false`) asserts nothing: it can be neither satisfied nor violated. Model validation rejects it at load with `semantic:partition-asserts-nothing` (exit 3), and the checker reports `unchecked` with reason `partition-asserts-nothing` should one reach it through an in-process `Model`. It must never report `pass` — it previously did, affirming "— satisfied" over a population carrying both an exclusion and an exhaustion violation.

**ORM 2 graphical signal:** circled X (exclusion) and/or circled dot (totality) at the supertype-subtype junction.

**YAML form (top-level):**
```yaml
constraints:
  - type: subtype-partition
    supertype: <ot_id>
    subtypes: [<ot_id_1>, <ot_id_2>, …]
    exclusive: true
    exhaustive: true
    source: …
    status: …
    modality: …
```

**CNL verbalization template:**
- Full partition: *"Every {Supertype} is exactly one of: {Subtype1}, {Subtype2}, …."*
- Exclusive only: *"No {Supertype} is more than one of: {Subtype1}, {Subtype2}, …."*
- Exhaustive only: *"Every {Supertype} is at least one of: {Subtype1}, {Subtype2}, …."*

**Checkable by gnd checker:** partial-observable — evaluated when subtype membership is observable in the population, i.e. via explicit `instances:` rosters or subtype-typed roles played in facts. When a subtype's membership exists only through an opaque `derivation_rule`, the verdict is `unchecked` and the checker's message quotes the rule verbatim as data (it is never evaluated).

## Textual

A first-order constraint that doesn't fit any of the graphical types above. Stored as natural-language text or FORML 2 syntax.

**ORM 2 graphical signal:** footnote on the diagram referencing a textual constraint listed elsewhere.

**YAML form (top-level):**
```yaml
constraints:
  - type: textual
    expression: "Each Employee who has Rank 'NonExec' uses at most one CompanyCar."
    formal_language: natural                    # natural | forml2
    formal_expression: null                     # optional formal-language string
    source: …
    status: …
    modality: …
```

**CNL verbalization template:** the `expression` itself, prefixed with `[textual]`.

**Checkable by gnd checker:** unchecked — always. The expression is an opaque string; the checker's message includes it verbatim as quoted data and states that textual constraints are not mechanically evaluable. A future LLM-judged deontic layer may cover these; the deterministic checker never will.

## Derived-extension findings

Structured fact-type derivations are reported separately from constraint
verdicts. Each fact type contributes one alethic obligation addressed as
`derivation:<fact-type-id>`. The address is the fact-type identity in report
schema v4; there is no second redundant `fact_type` string on the wire. Its
ordered findings are:

- `derived-extension-incomplete`: *"The derived extension of '{fact_type}' is
  incomplete — missing {witness}."*
- `derived-extension-unsound`: *"The derived extension of '{fact_type}' is
  unsound — offending fact {witness}."*

The witness is one canonical JSON object in declared role order. A listed
structured empty/empty comparison passes rather than becoming vacuous. An
unlisted rule or an opaque rule in a mixed structured model is `unchecked`,
using `derivation-not-covered` or `derivation-rule-opaque` respectively. The
evaluation algorithm and identity mapping are defined only in
[representation-format.md](representation-format.md#evaluation-and-claim-comparison).

## Modality reminder

Every constraint above can be alethic (must) or deontic (should), and **`modality` is required on every active constraint** — GND never defaults it. The checker maps modality to verdict severity:

- `modality: alethic` → a violated constraint yields verdict `fail` (CLI exit code 1).
- `modality: deontic` → a violated constraint yields verdict `warning` (advisory; exit code unaffected).

Modality also governs what happens when a constraint cannot be evaluated at all (D-07):

- `modality: alethic` → an `unchecked` verdict yields CLI exit code **4 — indeterminate**. The constraint is the acceptance contract, so a run that never evaluated it cannot claim acceptance.
- `modality: deontic` → an `unchecked` verdict leaves the exit code unaffected. Deontic constraints are feedback-only, so failing to evaluate one cannot withhold acceptance.

Because `textual` constraints are *never* mechanically checkable, an **alethic** textual constraint makes its model permanently indeterminate — every run over it exits 4. Prefer `modality: deontic` for textual constraints unless that is the intent.

Which modality the authoring skill should *write* for a given source/status is the D-03 policy — see [provenance-and-modality.md](provenance-and-modality.md), the single normative statement.

---
*Adapted from the rai-agent-skills ORM skills (branch an-orm-skill).*
