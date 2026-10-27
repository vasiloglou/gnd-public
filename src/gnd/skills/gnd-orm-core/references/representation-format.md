# YAML Representation Format

The schema spec for `model.orm.yaml` — the single interchange format every GND skill and the `gnd` runtime library read and write. Every other reference in this skill cites this file for YAML shape. Load when emitting, validating, or interpreting any part of the YAML.

Grounded in Halpin's ORM 2 vocabulary — the goal is models a Halpin-trained reader recognises as orthodox.

**Normative machine spec:** [`orm-meta.schema.json`](orm-meta.schema.json) in this skill's references directory is the normative Draft 2020-12 meta-schema. The prose in this file is explanatory; where prose and schema disagree, the schema wins. The `gnd` package vendors a byte-identical copy (`src/gnd/schema/orm-meta.schema.json`) guarded by a sync test — edit the canonical copy here and regenerate the vendored one.

The inline `anchored` family uses the common constraint fields plus an optional declared `role` and optional role-specific `recognise` list. Its matching and sidecar contract live in [constraint-reference.md#source-anchoring-v70](constraint-reference.md#source-anchoring-v70).

## Top-level structure

```yaml
version: 1                                    # mandatory; first field. 1, 2, 3 or 4 (calendar terms and references below).

model_id: urn:example:movies@3                # optional; stable opaque identifier for this model

source:                                       # how the model was derived; metadata for audit
  kind: text-conversation                     # text-conversation | codebase | sql | ddl-file | csv
  session_id: csdp_2026_05_14_movies          # optional dialogue identifier (text-conversation)
  artifacts:                                  # optional pointers to user-provided files
    - "user-prompt.md"
  started_at: "2026-05-14T10:00:00Z"
  confidence: standard                        # standard | low
  mode: guided                                # guided | one-shot

object_types:                                 # list of entity / value types
  - …

fact_types:                                   # list of fact types with their inline constraints
  - …

constraints:                                  # model-level (cross-fact-type or object-type-scope) constraints
  - …

operations:                                   # v2/v3/v4: named state transitions; requires version 2, 3 or 4
  - …

rejected_proposals:                           # constraints the user rejected; preserved so future runs don't re-propose
  - …

deontic_notes:                                # optional textual notes that don't fit any constraint type
  - text: "…"
    rationale: "…"
```

**`model_id` (optional):** a stable identifier for this model — any non-empty string; a URN, a slug, or a slug plus a version are all fine. Its one purpose is the population header cross-check: a population file may restate the same value under `population.model_id`, and when both are present and **differ**, the population was written for a different model and is rejected at load with exit 3. When the model declares one and the population omits it, the cross-check is skipped with a **warning** and acceptance is not withheld. When neither declares one, there is no check.

It is **optional for backward compatibility** — models authored before the field existed keep validating unchanged, and no tool requires it. It is **compared as an opaque string and never dereferenced**: nothing resolves it to a path, opens it, parses it as a URN, or normalises it, so two ids differing only in case or a trailing slash are different ids. If you change a model in a way that invalidates existing populations, bump the `model_id`; formatting-only edits should leave it alone (the field is deliberately not a content hash, which would be brittle across cosmetic changes). See [population-format.md](population-format.md) for the population side.

**`source.kind` values in GND today:** the text authoring skill (`gnd-model-from-text`) produces `kind: text-conversation`; conservative static recovery from an explicitly selected repository produces `kind: codebase`. `codebase` is the model's coarse origin only. The selected `source`, `test`, `docs`, `config`, and `schema` roots, exclusions, exact path census, evidence locators, ambiguities, and unmodeled frontier live in the sibling `model.recovery.json` report rather than being collapsed into `source`. The `sql`, `ddl-file`, and `csv` kinds and their specific fields (`dialect`, `connection_id`, `scope`, `introspected_at`) remain reserved.

### Codebase recovery provenance

Recovery does not add a constraint provenance source. The source values and their machine rules remain those in [provenance-and-modality.md](provenance-and-modality.md). Within a `source.kind: codebase` model:

- `explicit` is reserved for a mechanically declarative static invariant with digest-bound repository evidence.
- Test, fixture, or example observations use `sample`; semantic interpretation from names, prose, or structure uses `llm-inferred`. Both remain `proposed` and `deontic` until owner review, and neither is promoted from repetition or apparent sample saturation.
- An owner confirmation is recorded as a new `user-supplied`, `confirmed` constraint tied to the prior proposal identity in `model.recovery.json`. The original proposal retains its source and evidence there; rejected proposals are likewise retained instead of disappearing.

Every modeled object type, fact type, role, and constraint, plus every proposal, must resolve to concrete digest-bound evidence in that report. This mapping records what the selected static inputs support; it is not a claim that the repository was fully modeled.

**Two design rules govern every YAML:**

1. **Single source of truth per construct.** Every fact type has exactly one entry in `fact_types`; every constraint exactly one entry (inline or top-level by the scope rule below). No duplication.
2. **Constraint scope decides placement.** Constraints scoped to a single fact type live inline in `fact_types[].constraints`. Constraints that span fact types or are scoped to an object type live top-level in `constraints`.

| Constraint type | Scope | Placement |
|---|---|---|
| `uniqueness` (internal UC) | One fact type | inline |
| `mandatory` (single role) | One fact type | inline |
| `value` (role-scope) | One fact type | inline |
| `ring` | One fact type | inline |
| `frequency` scope=internal | One fact type | inline |
| `value-comparison` (intra-fact-type) | One fact type | inline |
| `uniqueness` scope=external | Multiple fact types | top-level |
| `mandatory-disjunctive` | Multiple fact types | top-level |
| `value` (object-type-scope) | Object type | top-level |
| `value` (role-scope hybrid: `object_type` is a primitive + `role_ref` narrows to a specific role) | One specific role of one fact type | top-level (kept with the other range proposals for grouping) |
| `subset`, `equality`, `exclusion`, `exclusive-or` | Multiple fact types | top-level |
| `frequency` scope=external | Multiple fact types | top-level |
| `value-comparison` (cross-fact-type) | Multiple fact types | top-level |
| `cardinality` (object or role) | Object type / role | top-level |
| `subtype-partition` | Object type | top-level |
| `textual` | Anywhere | top-level |

## Object types

```yaml
object_types:
  # Entity type with popular reference (single identifying value type)
  - id: customer
    name: Customer
    kind: entity
    reference:
      mode: popular                           # popular | unit-based | general | external
      value_type: customer_id                 # id of a value-kind object_type
    independent: false                        # "!" marker — instances may exist without playing roles

  # Entity type with unit-based reference
  - id: height
    name: Height
    kind: entity
    reference:
      mode: unit-based
      unit: cm                                # the unit string Halpin shows in the diagram
      measure_type: Length                    # the measurement category

  # Entity type with general reference (referenced by an injective binary)
  - id: book
    name: Book
    kind: entity
    reference:
      mode: general
      value_type: isbn

  # Entity type identified externally (composite identifier)
  - id: enrolment
    name: Enrolment
    kind: entity
    reference:
      mode: external                          # the external UC lives in top-level constraints

  # Value type (self-identifying primitive)
  - id: customer_id
    name: CustomerId
    kind: value
    primitive: Integer                        # String | Integer | Float | Number | Date | DateTime | Boolean | Binary | Duration
    # For Number with scale > 0:
    # primitive: Number
    # precision: 10
    # scale: 2

  # Subtype with derivation rule
  - id: male_person
    name: MalePerson
    kind: entity
    subtype_of: [person]                      # list — multi-supertype allowed
    inherits_reference: true                  # true = dashed arrow (inherits supertype's identifier); false = solid arrow (own identifier)
    derivation: derived                       # asserted | derived | semiderived
    derivation_rule: "Each MalePerson is a Person who is of Gender 'M'."
    storage: computed                         # stored | computed (default)
```

### Field-level rules

- **`id`**: required, lowercase, snake_case, unique across `object_types` and `fact_types` (enforced by `semantic:id-unique`). Used by fact types and constraints to reference this object type.
- **`name`**: PascalCase, the user-facing name. Shown in verbalizations.
- **`kind`**: required.
- **`reference`**: required for `kind: entity` unless the entity is a subtype (subtypes may inherit their supertype's reference). Absent for `kind: value`. The four `mode` values map directly to Halpin's reference-mode notations:
  - `popular` — Halpin's `Country(.code)` shorthand for an injective binary fact type with a primitive value type.
  - `unit-based` — `Height(cm:)` / `Salary(USD: Money)`. Carries `unit` and `measure_type`.
  - `general` — `Book(ISBN)`. Carries `value_type` only.
  - `external` — composite identifier; the actual external UC lives in top-level `constraints` and is cross-checked by `semantic:external-ref-uc`.
  - `value_type` must resolve to a value-kind object type (`semantic:reference-value-type`).
- **`primitive`**: required for `kind: value`. One of `String | Integer | Float | Number | Date | DateTime | Boolean | Binary | Duration`. For `Number` with non-zero scale, record `precision` and `scale`.
- **`independent`**: optional, default `false`. `true` means the object type's instances may exist without playing any elementary fact roles (Halpin's `!` marker).
- **`subtype_of`**: optional list. Empty / absent means the object type is not a subtype. Targets must resolve (`semantic:subtype-ref`).
- **`inherits_reference`**: required when `subtype_of` is non-empty. Maps to Halpin's solid (false) vs dashed (true) subtype arrow.
- **`derivation`**: optional, defaults to `asserted`. When `derived` or `semiderived`, `derivation_rule` is required. On an **object type** the rule is always an **opaque string** — no GND tool interprets or executes it, and the checker reports derivation-dependent constraints as `unchecked`. A *structured* rule on an object type is refused (`semantic:derivation-structured-on-object-type`): derived subtypes and computed rosters are out of scope in this version. Fact types are different — see [ORM++ — derived fact types](#orm--derived-fact-types).
- **`storage`**: optional, defaults to `computed` for derived. Set to `stored` for materialized derivations (Halpin's `**`/`++` notation).
- **`description`**: optional JSON object explaining what one instance of the object type is. GND renders it and never interprets it; no checker, synthesis or projection reads it.
  - **A description must not restate a constraint.** Descriptions are never checked, so a rule written there ("a refund is at most 500") is not enforced, and nothing reports when it disagrees with the model's real constraints. It is also rendered into the constraint-blind extraction vocabulary, where it would hand an extractor the rule that vocabulary leaves out. State each rule as a constraint, and keep the description to what one instance is.
  - Core keys, each a non-empty string of at most 4,096 characters: `summary` (required: what one instance is), `row` (what one fact or record about an instance means), `source` (where the knowledge came from) and `notes` (anything else a reader should know).
  - Any other key is an **extra**: any JSON value, carried unchanged in the model, in the verbalization's `canonical=` field, in `gnd diff` annotations and on the evolve `annotation` surface, and never rendered as prose. A misspelled optional core key (say `note`) is therefore an extra and is silently not rendered; a misspelled `summary` still fails, because `summary` is required.
  - A value with no JSON form is refused at layer 1 (exit 3): a YAML timestamp or date anywhere in the object, and NaN or infinity anywhere in it. Quote such values to keep them as strings.
  - Containers nest at most **64 levels** inside a description, the description object itself being level 1; a deeper one is refused at layer 1 (exit 3, `jsonschema:maxDepth`). JSON model files stop earlier, at whole-document depth 64. `gnd evolve` proposals cap their own JSON at depth 64 and carry an object type a few levels down, so a description in roughly the deepest five levels that validates may still be refused by an evolve proposal.
  - Rendering: the model verbalization appends the present core keys to the object type's sentence (`Description:`, `Row:`, `Source:`, `Notes:`), and the constraint-blind extraction vocabulary emits one indented line per present core key, both escaped and untruncated. Generated tool docstrings append ` — <summary>` to each role line whose object type has a description. Core keys always render in the order `summary`, `row`, `source`, `notes`.
  - The whole object, extras included, is included in the full model digest but excluded from source-anchor vocabulary digests. A sidecar therefore stays bound when only a description changes, and the vocabulary digest does not identify the rendered vocabulary text.

## Fact types

```yaml
fact_types:
  # Binary, functional (1:n via uniqueness on one role)
  - id: customer_has_email
    reading: "{Customer} has email {EmailAddress}"
    inverse_reading: "is email of"             # optional; corresponds to Halpin's reverse reading
    redact: true                                # optional shorthand: redact every role in reports
    roles:
      - object_type: customer                 # references object_types[].id
        role_name: customer
      - object_type: email_address
        role_name: email
        redact: true                            # optional: redact only this role in reports
    constraints:
      - type: uniqueness
        roles: [customer]
        preferred: false
        source: explicit
        status: confirmed
        modality: alethic                     # REQUIRED on every active constraint — see below
        provenance: { csdp_step: 4, dialogue_turn: 12, user_quote: "One email per customer." }
      - type: mandatory
        role: customer
        source: explicit
        status: confirmed
        modality: alethic
        provenance: { csdp_step: 5, dialogue_turn: 13, user_quote: "Every customer has an email." }

  # Binary m:n (spanning uniqueness)
  - id: order_item_tagged_with
    reading: "{OrderItem} tagged with {Tag}"
    roles:
      - { object_type: order_item, role_name: orderItem }
      - { object_type: tag, role_name: tag }
    constraints:
      - type: uniqueness
        roles: [orderItem, tag]               # spanning UC — neither alone unique
        preferred: true
        source: explicit
        status: confirmed
        modality: alethic
        provenance: { csdp_step: 4, dialogue_turn: 20, user_quote: "A tag applies to an item once." }

  # Objectified binary
  - id: student_enrolled_in_course
    reading: "{Student} enrolled in {Course}"
    roles:
      - { object_type: student, role_name: student }
      - { object_type: course, role_name: course }
    objectified_as: enrolment                 # references object_types[].id (entity, reference.mode: external)
    objectification_independent: true         # Halpin's "!" — Enrolment may exist before grades recorded

  # Self-referential — distinct role names disambiguate
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
        modality: deontic                     # unconfirmed common-sense defaults deontic (D-03)
        rationale: "Parenthood is acyclic by structural assumption."
        provenance: { library_entry: ring-parent-of, matched_pattern: "self-referential parent/child roles" }

  # Unary
  - id: person_smokes
    reading: "{Person} smokes"
    arity: 1                                  # explicit; default = len(roles)
    roles:
      - { object_type: person, role_name: person }

  # Ternary with functional dependency
  - id: person_played_sport_for_country
    reading: "{Person} played {Sport} for {Country}"
    roles:
      - { object_type: person, role_name: person }
      - { object_type: sport, role_name: sport }
      - { object_type: country, role_name: country }
    constraints:
      - type: uniqueness
        roles: [person, sport]                # functional: each (person, sport) → exactly one country
        source: explicit
        status: confirmed
        modality: alethic
        provenance: { csdp_step: 4, dialogue_turn: 30, user_quote: "One country per person per sport." }

  # Derived fact type
  - id: person_speaks_n_languages
    reading: "{Person} speaks {NrLanguages} languages"
    roles:
      - { object_type: person, role_name: person }
      - { object_type: nr_languages, role_name: nrLanguages }
    derivation: derived
    derivation_rule: "For each Person, nrLanguages = count(languageSpoken)."
    storage: computed
```

### Field-level rules

- **`id`**: required, lowercase, snake_case, unique (shared id space with object types — `semantic:id-unique`). Used by cross-fact-type role references in top-level constraints.
- **`reading`**: required. Halpin-style mixfix template. Object placeholders `{Type}` or `{Type:role}` map to roles by position; placeholder count must equal `len(roles)`, and each label before an optional `:role` suffix must match that role's object-type `id` or `name`. Matching case-folds and removes non-alphanumeric separators, so `{EmailAddress}` matches `email_address` while swapped or unrelated labels fail (`semantic:reading-placeholders`).
- **`inverse_reading`**: optional. The reverse-direction reading; Halpin notates these with `/` separators in the diagram.
- **`redact`**: optional boolean on a fact type. `true` selects every declared
  role of that fact type for report redaction; absent and `false` select none.
- **`depends_on`**: optional unique list of declared fact-type ids. It names upstream fact types for the requested occurrence-admission projection. An upstream and downstream occurrence connect only when they share a canonical identifying value in compatible reference roles; cycles are legal. This declaration is included in the full model digest but excluded from source-anchor vocabulary digests, which describe document-recognition vocabulary rather than admission policy.
- **`roles`**: required, ordered list. Order corresponds to placeholder order in `reading`.
  - **`object_type`**: required, must reference an existing `object_types[].id` (`semantic:role-ref`).
  - **`role_name`**: **required on every role** (GND divergence from the source spec's "optional unless ambiguous") — cross-references and the checker key on it. Role names must be **distinct within a fact type**, whatever the roles' object types (`semantic:role-names-distinct`) — the population loader compares a fact's supplied keys against the fact type's declared role-name set, so two roles sharing one name would shrink that set and make a fact filling only one of them structurally conformant.
  - **`redact`**: optional boolean. `true` selects this role for report
    redaction; absent and `false` select none. A role-level `false` never
    overrides a fact-type `true`. Redundant fact-type and role declarations are
    retained as declarations while their effective role coordinates are
    deduplicated.
- **`arity`**: optional. Defaults to `len(roles)`. Setting it explicitly is a cross-check that the reading and roles agree.
- **`objectified_as`**: optional. References an `object_types[].id`. The referenced object type should be an entity with `reference.mode: external`.
- **`objectification_independent`**: optional, default `false`. Maps to Halpin's `!` on the objectification.
- **`derivation` / `derivation_rule` / `storage`**: a fact-type rule takes **either** an opaque string (never interpreted, exactly as before) **or** the structured object arm. The structured arm, its named refusals, its stratification and its verify-the-claim stance have one normative home: [ORM++ — derived fact types](#orm--derived-fact-types).
- **`sample_population`**: optional array of role_name-keyed fact instances confirmed by the user (text-first extension, see below).
- **`constraints`**: optional list. Only constraint types from the inline set in the placement table above. Cross-fact-type constraints belong top-level.

### Self-referential and same-type fact types

Whenever the same object type appears in two or more roles of a single fact type, the (always-required) `role_name` values must be semantically distinct — `parent`/`child`, `manager`/`employee`, `stock1`/`stock2` — never mechanical duplicates. The role names disambiguate the roles in:

- The `reading` template (placeholder positions must agree with role order).
- Constraint `roles:` lists.
- Cross-fact-type role references.
- Checker output and population files (facts are keyed by role_name).

## Constraints — top-level (cross-fact-type and object-type scope)

```yaml
constraints:
  # External uniqueness (composite identifier across binary fact types)
  - type: uniqueness
    scope: external
    role_refs:
      # Reference the country and code roles so the SHARED State entity is the
      # anchor role of both fact types — the checker joins on shared anchor
      # object types; disjoint anchors would make the join undefined (unchecked).
      - { fact_type: state_in_country, role: country }
      - { fact_type: state_has_code, role: code }
    preferred: true                           # double-bar — this composite is the entity's preferred identifier
    source: explicit
    status: confirmed
    modality: alethic
    provenance: { csdp_step: 4, dialogue_turn: 22, user_quote: "Country plus state code identifies a state." }

  # Mandatory-disjunctive (inclusive-or)
  - type: mandatory-disjunctive
    role_refs:
      - { fact_type: visitor_has_passport, role: visitor }
      - { fact_type: visitor_has_license, role: visitor }
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Visitors must present at least one identity document."
    provenance: { library_entry: identity-document-required, matched_pattern: "visitor identity alternatives" }

  # Object-type value constraint (enumeration)
  - type: value
    object_type: gender
    allowed: ['M', 'F']
    source: explicit
    status: confirmed
    modality: alethic
    provenance: { csdp_step: 6, dialogue_turn: 25, user_quote: "Gender is recorded as M or F." }

  # Object-type value constraint (single range)
  - type: value
    object_type: age
    range:
      min: 0
      min_inclusive: true
      max_inclusive: false                    # max omitted → open-ended above
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Ages are non-negative."
    provenance: { library_entry: non-negative-age, matched_pattern: "Age value type" }

  # Object-type value constraint (multiple disjoint ranges)
  - type: value
    object_type: latitude_offset
    ranges:                                   # list form for multiple disjoint ranges
      - { min: -100, max: -20, min_inclusive: true, max_inclusive: true }
      - { min:   40, max: 100, min_inclusive: true, max_inclusive: true }
    source: user-supplied
    status: confirmed
    modality: alethic
    provenance: { added_at_step: 7d }

  # Role-scope value constraint (hybrid `object_type` + `role_ref` form)
  # Use when a generic primitive value type (e.g., Integer) appears in multiple
  # roles that each want different bounds. The `object_type` names the primitive
  # being constrained; `role_ref` narrows the scope to a specific role.
  - type: value
    object_type: integer                      # the primitive being constrained
    role_ref: { fact_type: inventory_quantity_on_hand, role: quantityOnHand }
    range: { min: 0, min_inclusive: true }
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Quantities on hand are non-negative."
    provenance: { library_entry: non-negative-count, matched_pattern: "quantityOnHand role" }

  # Subset
  - type: subset
    subset_role_seq:
      - { fact_type: person_smokes, role: person }
    superset_role_seq:
      - { fact_type: person_is_cancer_prone, role: person }
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Smoking implies cancer risk."
    provenance: { library_entry: smoking-cancer-risk, matched_pattern: "smoker and cancer-prone roles" }

  # Equality
  - type: equality
    role_seq_a:
      - { fact_type: patient_has_systolic_bp, role: patient }
    role_seq_b:
      - { fact_type: patient_has_diastolic_bp, role: patient }
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Blood-pressure readings come in pairs."
    provenance: { library_entry: paired-blood-pressure, matched_pattern: "systolic/diastolic role pair" }

  # Exclusion
  - type: exclusion
    role_seq_a:
      - { fact_type: person_is_married, role: person }
    role_seq_b:
      - { fact_type: person_is_widowed, role: person }
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Marital statuses are mutually exclusive."
    provenance: { library_entry: exclusive-marital-status, matched_pattern: "married/widowed role pair" }

  # Exclusive-or — partition over a population (inclusive-or + exclusion)
  - type: exclusive-or
    role_seqs:
      - [{ fact_type: academic_is_male, role: academic }]
      - [{ fact_type: academic_is_female, role: academic }]
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Recorded as exactly one of the two."
    provenance: { library_entry: binary-recorded-gender, matched_pattern: "male/female classification roles" }

  # External frequency
  - type: frequency
    scope: external
    role_refs:
      - { fact_type: student_enrolled_in_course, role: student }
      - { fact_type: student_enrolled_in_course, role: course }
    bound: { min: 1, max: 2 }
    source: user-supplied
    status: confirmed
    modality: alethic
    provenance: { added_at_step: 7d }

  # Value-comparison across fact types
  - type: value-comparison
    operator: ">="                            # < | <= | = | >= | > | !=
    role_a: { fact_type: project_ended, role: date }
    role_b: { fact_type: project_started, role: date }
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Projects end no earlier than they start."
    provenance: { library_entry: ordered-start-end, matched_pattern: "project start/end date roles" }

  # Object cardinality
  - type: cardinality
    scope: object
    object_type: president
    bound: { min: 1, max: 1 }
    source: user-supplied
    status: confirmed
    modality: alethic
    provenance: { added_at_step: 7d }

  # Role cardinality
  - type: cardinality
    scope: role
    role_ref: { fact_type: politician_is_president, role: politician }
    bound: { max: 1 }
    source: user-supplied
    status: confirmed
    modality: alethic
    provenance: { added_at_step: 7d }

  # Subtype partition (xor + exhaustive)
  - type: subtype-partition
    supertype: product
    subtypes: [physical_product, digital_product, subscription_product]
    exclusive: true
    exhaustive: true
    source: common-sense
    status: proposed
    modality: deontic
    rationale: "Product categories partition the catalog."
    provenance: { library_entry: product-category-partition, matched_pattern: "catalog product subtypes" }

  # Textual constraint (catch-all)
  - type: textual
    expression: "Each Employee who has Rank 'NonExec' uses at most one CompanyCar."
    formal_language: natural                  # natural | forml2
    formal_expression: null                   # optional FORML 2 syntax if available
    source: user-supplied
    status: confirmed
    modality: alethic
    provenance: { added_at_step: 7d }
```

### Cross-fact-type role references

The `{ fact_type: <id>, role: <role_name> }` tuple is the canonical cross-reference. Both fields are required. The combination must resolve — `semantic:cross-ref` checks that the referenced `fact_type.id` exists and that one of its roles has the matching `role_name`.

For self-referential or multi-occurrence fact types where the role name disambiguates two roles of the same object type, the role reference must use the disambiguating name (not the object-type name).

## Guarded constraints

`guarded` is GND's top-level conditional constraint family. Its `antecedent`
is a non-empty conjunction of positive atoms. Every atom binds exactly the
roles declared by its fact type; a bind value is either a scalar literal or a
`$`-prefixed variable. The consequent is exactly one of four shapes: `atom`
requires a fact, `comparison` compares two terms with `<`, `<=`, `=`, `>=`,
`>`, or `!=`, `absence` requires that a fact be absent, and `exists` requires
a conjunction of positive atoms with a joint witness assignment. An exists-only
variable must occur in a positive exists atom. Every `exists.where` variable
must be bound by an antecedent or positive exists atom, and comparison operands
must have compatible resolved primitive types.

```yaml
- id: policy_limit_travel
  type: guarded
  modality: alethic
  source: explicit
  status: confirmed
  antecedent:
    - fact_type: expense_in_category
      bind: {expense: $e, category: "travel"}
    - fact_type: expense_has_amount
      bind: {expense: $e, amount: $a}
  consequent:
    comparison: {operator: "<=", left: $a, right: 2000}
```

The `atom` and `absence` consequent values use the same `{fact_type, bind}`
shape as each antecedent item. The comparison's `left` and `right` fields use
the recursive exact term shape defined under ORM++ derivations; atom bindings
remain scalar literals or variables. An `exists` consequent is an object with
non-empty `atoms` and optional non-empty `where`, whose items reuse the atom
and exact term-comparison shapes.

Evaluation enumerates the antecedent's variable bindings. A literal must match
by scalar identity; a variable repeated within one atom or across atoms must
carry the same identity at every site. Multi-atom antecedents are joined by
shared variables using indexed joins. Their atom graph must be one connected
component; a disconnected graph is never cross-joined and reports `unchecked`
with reason `join-disconnected`. If any antecedent fact type is empty, the
constraint is `vacuous`. If all antecedent fact types are populated but no
binding matches, the constraint is a decided `pass` whose message says
`bindings=0`. Consequent evaluation, including literal interpretation and
undecidability, is per produced binding: with zero bindings no operand is
interpreted, so this decided pass takes precedence over consequent-level
`unchecked` outcomes.

For each binding, an `atom` consequent holds when a matching grounded fact is
present, and an `absence` consequent holds when none is present. Both use the
population as a closed world regardless of `covers`; this intentionally differs
from the coverage-omission rule for mandatory constraints. An `exists`
consequent first passes when there are zero antecedent bindings. Otherwise,
every exists relation must be listed in the source population's `covers`; an
omitted relation makes the result `unchecked`, never an assumed empty relation.
Each antecedent binding must have one joint assignment satisfying every exists
atom and every `where` comparison. Disconnected exists components are
conjunctions evaluated under the named work ceiling, not refused as
`join-disconnected`. A reached candidate whose exact term is undefined makes
the whole result `unchecked`, even if another candidate satisfies the clause.
If no undefined term is reached, missing witnesses are reported using only
the antecedent binding variables.

A `comparison` consequent resolves variables from the binding, interprets a
literal in the opposite variable's resolved primitive domain, and uses the
checker's normal typed comparison semantics. A pair that cannot be ordered
reports `unchecked` with `values-not-comparable`; a literal whose borrowed
primitive cannot be resolved reports `unchecked` with
`literal-type-ambiguous`.

Any undecidable binding makes the whole guarded constraint `unchecked` and
takes precedence over otherwise violating bindings. Otherwise, violating
bindings produce `fail` for an alethic constraint or `warning` for a deontic
constraint; each is emitted as an ordered object in `offending_facts`, keyed by
the model's `$`-spelled variable names in first-introduction order. With no
violations the verdict is `pass`. Every non-vacuous guarded verdict message
includes the binding count.

## Provenance and modality — every constraint carries

Every **active** constraint entry — inline or top-level — carries the same metadata fields. The `provenance` block's shape varies by `source`.

```yaml
- type: <constraint-type>
  # constraint-specific fields …
  source: explicit                            # explicit | sample | common-sense | llm-inferred | user-supplied | imported
  status: confirmed                           # proposed | confirmed
  modality: alethic                           # alethic | deontic — REQUIRED, never defaulted
  rationale: "Free-text explanation."         # optional for explicit; required for non-explicit sources
  provenance: { … }                           # source-specific structured pointer
```

**`modality` is REQUIRED on every active constraint.** This is a deliberate GND divergence from the source spec, which defaulted `modality: alethic` when omitted. In GND an omitted modality is a schema validation error — a model that doesn't say whether a constraint hard-fails (alethic) or warns (deontic) is ill-formed. Authoring-time *defaults by source* (which modality the authoring skill should **write**) are governed by the D-03 policy in [provenance-and-modality.md](provenance-and-modality.md) — that document is the single normative statement of the six-source taxonomy, the per-source provenance block shapes, and the modality-defaulting policy. The semantic validator warns (`semantic:modality-policy`) when an unconfirmed `llm-inferred` or `common-sense` constraint carries `modality: alethic`.

The only exception is `rejected_proposals`: entries there are archived proposals, not active constraints, and are schema-light — `modality` is NOT required on them.

Per-source provenance block shapes (summarized; normative statement in [provenance-and-modality.md](provenance-and-modality.md)):

- **`explicit`** — a `provenance` block is required. In text-conversation models it carries `csdp_step`, `dialogue_turn`, and (recommended) `user_quote`. The schema-recovery block shapes (`table`, `column`, `constraint_type`, `fk`, `check_expression`) are reserved for the Phase 4 recovery skill.
- **`sample`** — `rationale` and `provenance` required (e.g. sample size, observed values). Sample-derived constraints in text-first models stay `proposed` until user confirmation — Halpin populations are too small to auto-confirm.
- **`common-sense`** — `rationale` required (restating the matched library pattern in user-facing language); `provenance` carries `library_entry`, `matched_pattern`, `assumptions`.
- **`llm-inferred`** — `rationale` AND `provenance.rationale_world_fact` (non-empty) required. Without the world-fact citation the proposal is rejected at emission time.
- **`user-supplied`** — a `provenance` block is required (e.g. `added_at_step`, optional `user_note` / `user_quote`).
- **`imported`** (v2) — a claim carried in from another framework's artifact. `provenance` requires `framework`, `artifact`, `commit`, `sha256` and a verbatim `anchor`, and `reviewed_in` in addition once `status: confirmed`. The same block, and the same requirement, applies to an operation and to each of its obligations.

The `type`/`source`/`status`/`modality`/`rationale`/`provenance` block above is shared: an operation's preconditions and dynamic rules carry exactly these fields under exactly these per-source rules (`$defs/provenance_policy` in the meta-schema, referenced from both places rather than copied).

## Text-first extensions (text-conversation source.kind)

When `source.kind: text-conversation` — the kind GND's authoring skill produces — `provenance` blocks may include fields that trace each construct back to a dialogue turn:

```yaml
provenance:
  csdp_step: 1                                # which CSDP step emitted this (0-7, plus 7a-7f)
  dialogue_turn: 4                            # turn number in the conversation
  user_quote: "Each Movie has one canonical title in our catalog."   # the user's actual words
```

The `user_quote` field is recommended for `source: explicit` and `source: user-supplied` constraints; it makes the YAML auditable in dialogue terms.

Fact types in text-first YAMLs may also carry a `sample_population:` array — Halpin-style sample fact instances confirmed by the user at CSDP Step 1:

```yaml
fact_types:
  - id: person_born_in_country
    reading: "{Person} was born in {Country}"
    roles: [{ object_type: person, role_name: person }, { object_type: country, role_name: country }]
    sample_population:                        # 5-20 sample facts; keys are role names
      - { person: "John", country: "Australia" }
      - { person: "Mary", country: "Greece" }
    provenance: { csdp_step: 1, dialogue_turn: 4 }
```

The sample_population is rendered in the verbalization (see [verbalization-patterns.md](verbalization-patterns.md)) but is *not* used to auto-confirm sample-derived constraints — they stay `proposed` until user confirmation.

Note that `sample_population` (authoring-time examples embedded in the model) is distinct from a **population file** (a standalone document checked against the model) — the latter is specified in [population-format.md](population-format.md).

## `rejected_proposals` — kept so future runs don't re-propose

Same shape as a regular constraint, but with `status: rejected` and two added fields. Schema-light: `modality` is not required (archived proposals, not active constraints).

```yaml
rejected_proposals:
  - type: ring
    fact_type: order_precedes_order
    variant: acyclic
    source: common-sense
    status: rejected
    rationale: "Library entry: precedes-acyclic."
    provenance: { library_entry: ring-precedes-acyclic, matched_pattern: "self-referential predecessor roles" }
    rejection_reason: "Domain explicitly allows reissues that point back to predecessors."
    rejected_at: "2026-05-04"
```

A future authoring run on the same domain reads `rejected_proposals` first and excludes those proposals from re-emission. The exclusion match is `(type, fact_type or object_type, variant or roles)` — exact rematch, not fuzzy.

## ORM+ v2 — operations

Version 2 adds exactly one optional top-level section, `operations:`, and changes nothing else. It exists so the conceptual model can also be the *requirements* document: an operation is a named state transition, and a feature is an operation.

**Version rule.** `version:` accepts `1`, `2`, `3` or `4`. A document carrying `operations:` MUST declare version 2, 3 or 4 (a root `if/then` in the meta-schema; violating it is exit 3). Version 3 adds calendar terms; version 4 adds the reference populations described below. A `version: 2` document that declares no operations is behaviourally a v1 document — and every consumer feature-detects on `model.operations` being non-empty, never on `model.version`, so it stays one. Migration from v1 is: change `version: 1` to `version: 2`. Nothing else.

**Default snapshot mode ignores operations entirely.** `gnd check` over a population reads object types, fact types and constraints, exactly as it did before v2 existed. A v2 model's operations produce no verdict, no coverage entry, and no change to any exit band. Transition checking is a separate CLI arm. Explicit `--compiled-operations` snapshot activation is defined under [Compiled obligations](#compiled-obligations).

### The construct

```yaml
version: 2
operations:
  - id: <identifier>                # joins the ONE id namespace (below)
    reading: "…{Type}…{Type:param}…"
    parameters:                     # at least one; names distinct
      - { name: <identifier>, object_type: <object-type-id> }
    preconditions:                  # optional; conjunctive POSITIVE atoms only
      - id: <identifier>
        require: [ { fact_type: <id>, bind: { <role>: "$param" | <literal> } } ]
        source: … ; status: … ; modality: …          # all three REQUIRED
        provenance: { … }                            # per-source, as for constraints
    effects:                        # at least one; each exactly one of the three
      - create:  { object_type: <id>, param: <parameter-name> }
      - assert:  { fact_type: <id>, bind: { … } }    # EVERY role bound
      - retract: { fact_type: <id>, bind: { … } }    # omitted role = wildcard
    dynamic_rules:                  # optional; old-versus-new value comparison
      - id: <identifier>
        subject: { fact_type: <id>, value_role: <role>, bind: { … } }
        op: "<" | "<=" | "=" | ">=" | ">" | "!="     # new op old
        source: … ; status: … ; modality: …          # all three REQUIRED
    frame: { modality: alethic | deontic }           # REQUIRED, never defaulted
    source: … ; status: …           # the operation's own provenance; NO modality
    provenance: { … }
```

**Atoms are positive and conjunctive, and that is the whole language.** There is no negation, no comparison, no arithmetic, no aggregation and no disjunction. A `bind` value is either a literal scalar or `$param`, a reference to a declared parameter. Constraints that need more than this — a value-conditioned precondition like `amount <= limit`, or an absence precondition like "not already submitted" — cannot be written **as an operation precondition**; that is a stated limitation of this grammar, not an oversight. From v3 they have a home as top-level [`guarded` constraints](#guarded-constraints), whose consequent may be a comparison or an absence and which `gnd check` evaluates mechanically. Two caveats a reader reaching for that home needs: a guarded constraint states what must hold of a **population**, not what must hold before a step; and its absence consequent must be **ground**, so "no fact of this type mentions this subject, whatever its other roles hold" is still not expressible — carry the existence claim in its own fact type instead. Before v3 such rules remained advisory `textual` constraints, which is what earlier revisions of this paragraph said.

**Modality lives on obligations, never on the operation.** Each precondition, each dynamic rule, and the frame carries its own REQUIRED `modality`, because that is where a verdict attaches. The operation itself carries `source`, `status` and `provenance` but no modality: there is no such thing as "this operation failed", only "this obligation of this operation failed". An omitted `frame` block, or an omitted `modality` on any obligation, is a layer-1 rejection at exit 3 — the same never-defaulted rule [provenance-and-modality.md](provenance-and-modality.md) states for constraints.

**The frame grades per FACT TYPE.** A fact type touched in a walk only by operations declaring `frame: { modality: alethic }` has its undeclared deltas graded alethic; a fact type touched by any operation declaring `frame: { modality: deontic }` has them graded deontic, and the report names the responsible operation. There is no walk-level downgrade.

### Effect atomicity — why there is no `replace`

**A step's effects apply as a SET, and the intermediate invariant is checked afterwards.** No invariant is evaluated between two effects of one step. **Written order is not semantic**, and the equation below decides every case where two effects overlap. An earlier revision of this file stated an ordering rule that contradicted the equation and produced the opposite verdict on the same walk; the equation is the one normative account, and it lives here.

**The transition equation.** "As a set" decides nothing on its own, so the rule is stated in full:

1. **Every `retract` selector evaluates against S(i-1)**, never against a partially updated state, so effects within one step cannot observe each other and the order they are written in does not matter.
2. **All retracts apply before all asserts.** A fact both retracted and asserted in one step is therefore **PRESENT** in S(i) — which is exactly what makes retract+assert a replace, and why no `replace` primitive exists.
3. **Duplicate asserts and duplicate retracts collapse.** Asserting one ground fact twice yields one fact; two retracts selecting the same fact remove it once. Neither is an error.
4. **`create` mints nothing on its own** — it names an object type and a parameter, and the value comes from the step's bindings like every other parameter. Two creates of one object type in a single step must carry distinct values, and freshness is judged against S(i-1) **together with the step's own earlier creates**.
5. **No step aborts.** A failed precondition is reported and the step's effects still apply, so one pass reports every finding a walk contains and the computed final state corresponds to the trace as logged. The cost is real and stated: a computed state can contain a fact a precondition declared unreachable. `gnd check` audits a log; it does not execute a program and has nothing to roll back.

The consequence is the reason no `replace` primitive exists: a `retract` and an `assert` over the same fact type *within one step* already is a replace. Retracting `expense_has_status(expense=$e)` and asserting `expense_has_status(expense=$e, status="submitted")` in the same step never leaves the mandatory `expense` role unfilled, because there is no point at which the invariant is checked and only the retract has happened.

This rule was implicit before, and a reviewer reading the specification's own worked example — which retracted with no compensating assert — concluded the language was broken when only the example was. Hence the pin below.

### The worked example (pinned)

These bytes are the `operations:` section of `tests/fixtures/models/v2_worked_example.orm.yaml`, and `tests/test_model_v2.py` fails if the two ever differ or if `gnd validate` stops exiting 0 on that fixture. A specification example that cannot drift from the implemented language is worth more than a specification example that reads well.

```yaml
operations:
  - id: submit_expense_to_workday
    reading: "{Expense} is submitted to Workday as {WorkdaySubmission}"
    parameters:
      - { name: expense,    object_type: expense }
      - { name: submission, object_type: workday_submission }
      - { name: chain,      object_type: approval_chain }
    preconditions:                      # conjunctive POSITIVE atoms only
      - id: pre_approved
        require:
          - { fact_type: expense_has_status,
              bind: { expense: "$expense", status: "approved" } }   # literal binding OK
        modality: alethic
        source: explicit
        status: confirmed
        provenance: { csdp_step: 7, dialogue_turn: 44,
                      user_quote: "Nothing reaches Workday before approval." }
    effects:                            # applied as a SET, then the invariant is checked
      - create: { object_type: workday_submission, param: submission }  # caller mints the id
      - assert: { fact_type: expense_submitted_to_workday,              # every role ground
                  bind: { expense: "$expense", submission: "$submission" } }
      - retract: { fact_type: expense_has_status,                       # wildcards allowed
                   bind: { expense: "$expense" } }
      - assert:  { fact_type: expense_has_status,                       # the compensating
                   bind: { expense: "$expense", status: "submitted" } } # half of the replace
    dynamic_rules:                      # old-vs-new functional value comparison
      - id: status_must_change          # the subject must be a fact type THIS
        subject: { fact_type: expense_has_status,    # operation touches, or the
                   value_role: status,               # rule can never fire and
                   bind: { expense: "$expense" } }   # op-dynamic-untouched warns
        op: "!="                        # new op old; in < <= = >= > !=
        modality: deontic
        source: user-supplied
        status: confirmed
        provenance: { added_at_step: 7d }
    frame: { modality: deontic }        # REQUIRED, never defaulted. Grading is per FACT
                                        # TYPE: this operation's deontic frame makes the
                                        # fact types IT touches deontic, and never
                                        # downgrades another operation's alethic ones.
    source: explicit
    status: confirmed
    provenance: { csdp_step: 7, dialogue_turn: 44 }
```

Note `chain`: it is declared as a parameter even though the reading does not mention it, because the dynamic rule binds `$chain`. An operation reading is a sentence, not a role tuple — see the placeholder rule below.

### One id namespace

Object type ids, fact type ids, operation ids, and the OPTIONAL `id:` a constraint may now carry all live in **one** namespace, checked by `semantic:id-unique`. A duplicate across any two of them is exit 3.

```yaml
constraints:
  - id: one_email_per_customer          # optional, but stable
    type: uniqueness
    scope: external
    role_refs: [ … ]
    source: explicit
    status: confirmed
    modality: alethic
    provenance: { … }
```

Constraint ids are optional so no existing model breaks. A constraint without one is still addressable by position, and `gnd coverage` reports a positional address as **unstable** — position changes whenever a constraint is inserted above it, so a `covers:` entry naming one is a claim about a moving target.

### The `operations` reading rule

An operation's `reading` is a stakeholder sentence, not a verbalization of its complete parameter tuple. `semantic:op-reading-placeholders` therefore requires that every `{…}` placeholder resolve to exactly one declared parameter, and that no parameter be claimed twice — but it does NOT require that every parameter appear. This is deliberately weaker than the fact-type rule (`semantic:reading-placeholders`, a strict bijection with the role list), because a fact type's reading verbalizes the whole fact and an operation's does not.

A placeholder may name a parameter by the parameter's own name, by its object type's id, or by that object type's `name`; `{Type:param}` disambiguates when two parameters share an object type, exactly as `{Type:role}` does for fact types. **Both halves of the qualified form are checked**: `{Wrong:note}` is rejected even though `note` is a parameter, because a type label that does not name that parameter's object type is a claim about a different parameter, not a comment.

Resolution is by index, not by scanning the parameter list per placeholder. A model under the 10 MB input cap can declare tens of thousands of parameters and as many placeholders, and the scan made that document quadratic to load.

### What `population._model_digest` covers (A8)

`gnd.population._model_digest` is `sha256(repr(model.model_dump(exclude=MODEL_DIGEST_EXCLUDED_FIELDS)))` over the **loaded model object**, not over the YAML bytes. Two fields are excluded, and the exclusion set is a named constant in `gnd/population.py` so this statement and the code cannot drift:

| Field | Excluded because |
|---|---|
| `warnings` | Validation OUTPUT, attached after layer 2 ran. No checker verdict depends on it. |
| `operations` | **Default snapshot checking never reads it.** This digest's contract is "everything layer 2 validated *and the checker reads*", and a section outside that contract does not belong in it. |

Everything else — `version`, `model_id`, `source`, `object_types`, `fact_types`, `constraints`, `rejected_proposals`, `deontic_notes` — is covered, including nested content, so mutating a model in place after loading invalidates any population's validation marker against it.

Three consequences, each intended:

- **A v1 model's digest is unchanged by the existence of v2.** Adding `operations` to the loaded model without excluding it here would have changed the digest of every model ever authored, and every committed sidecar that records one.
- **Editing an operation does not invalidate a population.** Correct, because that population was never checked against the operation: default snapshot mode ignored it. Opted-in operation checks must be rerun when the operations change. A population and an operation make claims about different things.
- **A transition run needs a different claim over different bytes** — "these steps were authored against these operations" — and Phase 2's `steps.json` carries its own `operations_digest` for it, under the same exit-3 mismatch guard, rather than overloading this one.

Separately, the digest is *excluded from a report's constraint verdicts*, so "a v2 model with operations produces a byte-identical snapshot `CheckReport` to the same model with `operations` stripped" holds for default checking: nothing inside that default verdict body varies with it.

It is no longer private, though. `src/gnd/report.schema.json` has four closed arms. Report `schema_version` 3 and 4 are frozen and forbid `model_digest` — a report written before model binding existed must keep the bytes it was written with. Versions 5 and 6 require it: `gnd.transition.model_digest` over the loaded model, emitted immediately after `model` in every version 5 or 6 payload. A `validate` payload and any `check`/`verify` payload emitted before the model loads stay on a frozen version and carry none. One published identity, in one place, so a consumer never has to decide which of two spellings it is looking at.

The reason is that a path is a coordinate, not an identity. Two different models can occupy one path over time, and one model can be read from two paths, so a report naming only `model` cannot answer "which model produced this". A digest can, and a consumer comparing digests can refuse evidence about the wrong model instead of quietly aggregating it.

## ORM++ — derived fact types

**This section is the one normative home for structured derivation rules.** The
loader implements it (`semantic:derivation-*` in `src/gnd/model/_validation.py`); the plan
and the skills cite it; nothing restates it.

An **asserted** fact type holds what somebody claimed. A **derived** fact type
holds what *follows* from other facts. Before v5.0 the model could only
*mention* a derivation — `derivation_rule` was an opaque string no tool ever
interpreted, and it still may be. v5.0 adds a second, machine-shaped arm.

### The two arms

`derivation_rule` takes **either** a string **or** an object:

- **string** — the pre-v5 opaque form. Never interpreted, never executed. Its
  meaning is unchanged, and a rule needing something the object arm has no
  syntax for (disjunction, window functions, or unsupported aggregate forms)
  stays a string and stays
  opaque. This is the honest outcome, not a silent one.
- **object** — the structured form below.

```yaml
- id: book_is_eligible
  reading: "{Book} is eligible for {Person}"
  roles:
    - { object_type: book, role_name: book }
    - { object_type: person, role_name: person }
  derivation: derived            # or semiderived
  storage: computed              # a structured rule computes; `stored` contradicts it
  derivation_rule:
    body:                        # conjunction of POSITIVE atoms
      - { fact_type: person_likes_genre, bind: { person: "$p", genre: "$g" } }
      - { fact_type: book_has_genre, bind: { book: "$b", genre: "$g" } }
      - { fact_type: book_has_score, bind: { book: "$b", score: "$score" } }
    negate:                      # optional; negation as failure
      - { fact_type: book_flagged, bind: { book: "$b" } }
    where:                       # optional; exact comparisons
      - { operator: ">=", left: { fn: abs, args: ["$score"] }, right: 1 }
    head:                        # this fact type's OWN declared roles
      book: "$b"
      person: "$p"
```

`body`, `negate`, `where`, and `head` are the base keys; Phase 4 also admits
`aggregate` as described below. Atoms reuse the same
shape guarded constraints use, and variables the same `$name` spelling — there
is no second atom language and no second variable notation. A `where` item has
`operator`, `left`, and `right`; the operator is one of `<`, `<=`, `=`, `>=`,
`>`, or `!=`.

From v7.0, a structured rule may instead declare nonempty `clauses`. Each
clause has a nonempty positive `body`, optional `negate` and `where`, and a
head. There are two exclusive spellings: one root `head` shared by all clauses,
or a `head` in every clause. A per-clause head may use different terms but
must cover the same declared roles and bind each variable in its own positive
body. Root `body` and `negate` cannot accompany `clauses`, and mixed head
placement is refused. Root `where` and `aggregate`, when present, apply to
each clause independently. The legacy single-clause object is unchanged.
Every clause projects separately; its canonical tuples are then unioned.

The recursive term shape is shared by derivation `where` operands, derivation
head values, and guarded-comparison operands. A term is a scalar literal, a
`$variable`, or `{fn: <name>, args: [...]}`. The closed function table has two
tiers. The **exact tier** (Phase 3): `add(a,b)`, `sub(a,b)`, `mul(a,b)`,
`neg(a)`, `abs(a)`, and `mod(a,b)`, evaluated with exact rational arithmetic
internally. `mod(a,b)` is floor-mod, defined as `a - b * floor(a / b)`, so
`mod(-1,30) = 29` and `mod(1,-30) = -29`. The **float tier** (Phase 5):
`div(a,b)`, `sqrt(a)`, `round(a,digits)`, `floor(a)`, `ceil(a)`, and
`haversine(lat1,lon1,lat2,lon2)`, evaluated with IEEE-754 binary64 semantics.
`haversine` uses mean earth radius 6371.0088 km and returns kilometres.
Booleans are never numeric.

A function-valued head must be statically Integer-valued **or** wrapped in an
outer `round(term, digits)` call; `floor` and `ceil` are the one exception,
because their range is always exactly Integer-representable and may bind a
head directly with no `round` wrapper. `round`'s stored value is the binary64
nearest the rounded decimal — correctly rounded, ties to even. No rational or
decimal wire scalar is added; a float head is carried as an ordinary binary64
scalar, identity-tokened the same way any other number is.

Every function has a named undefined case rather than an exception or a
silent value: `mod` by zero (`term:mod-zero`), `div` by zero
(`term:div-zero`), `sqrt` of a negative operand (`term:sqrt-negative`), a
`haversine` coordinate outside `[-90,90]`/`[-180,180]`
(`term:haversine-coordinate-range`), an exact value past the evaluator's
node/width budget (`term:exact-value-too-wide`), and a value that would
overflow binary64 during a float-tier conversion or arithmetic step
(`term:float-overflow`). Each reports the relation `unchecked` with the exact
reason and binding, never a crash, a null, or a silently fabricated value.

### Exact aggregates in derivation bodies

A structured derivation may additionally carry one `aggregate` object:

```yaml
aggregate: { fn: sum, of: "$rb", over: ["$sample"], as: "$sum" }
```

`fn` is one of `count`, `sum`, `min`, `max`, or `avg`; `of` is the same exact
term language; `over` is a non-empty, ordered list of positive body variables;
and `as` is a fresh result variable. The group key is exactly the set of
positive variables read by the head other than `as`. A contribution is distinct
by the ordered `over` binding paired with its evaluated `of` value. Thus two
different `over` bindings with equal values both contribute, while duplicate
proof paths for one pair do not.

Only non-empty body groups exist. `count` is Integer and accepts any scalar
`of`; `sum`, `min`, `max`, and `avg` require an Integer-valued `of`. `count`,
`sum`, `min`, and `max` materialize as Integer; `avg` is an exact rational,
usable directly in a post-aggregate `where` comparison, and admitted into a
head only through an outer `round(term, digits)` call (Phase 5) — a bare
`avg` result in any head shape, wrapped or not, is refused
(`semantic:aggregate-head-needs-round`). Runtime order is body join,
negation, aggregate, `where`, head, then relation publication. An unavailable
`of` makes the whole relation unavailable; it never drops only that group.

The normative aggregate order is:

1. Join positive body atoms over asserted-plus-computed facts.
2. Apply the rule's negated atoms to those bindings.
3. Evaluate `of` exactly and read the ordered `over` tuple for each survivor.
4. Form each group key from the variables read by the head other than `as`.
5. Within each group, deduplicate by `(ordered over tuple, evaluated of value)`.
6. Apply the named aggregate to those distinct contributions.
7. Bind `as`, retain only group variables plus `as`, then evaluate post-aggregate
   `where` comparisons in written order.
8. Evaluate the head and publish the relation once.

For example, two samples with equal resource-block values still add twice when
their `over` sample identities differ. A non-injective `of` such as
`mod($rb, 2)` likewise retains two different sample identities even if both
evaluate to zero; duplicate proof paths for one sample/value pair add once.
An empty body produces no group and never a fabricated `count: 0` row. To
describe scenarios with no samples, derive a lower-stratum
`scenario_has_sample` relation from observations, then derive
`zero_sample_scenario` from a catalog body with `negate` on
`scenario_has_sample`.

`mod(x,0)` makes the entire derived relation unavailable with
`term:mod-zero`; it never drops one row or substitutes null. Every upper
stratum and consumer is also `unchecked`. The evaluator caps a term at 256
nodes, depth 32, and 65,536 numerator or denominator bits. Structural cap
violations are model refusals; an evaluated value over the bit cap is
`term:exact-value-too-wide`.

### What is refused, and why

**The object arm is CLOSED in the meta-schema**, because a published schema
must not accept what the product refuses: third parties author models against
this file, and a rule it calls valid must be one GND loads. An unknown key, a
missing `body` or `head`, and a malformed term are refused
at layer 1 — and the loader **enriches that `oneOf` failure with the offending
key**, so the message still names the construct rather than reporting only that
the value matched neither arm.

The layer-2 rules own everything a schema cannot express — safety, range
restriction, type compatibility, acyclicity — and run in a fixed **precedence:
reference errors, then shape errors, then graph errors**, so a document
carrying two defects reports the one that explains the other first. Those of
them that duplicate a schema check remain as **defense in depth** for callers
that build a document in process and never pass layer 1.

| rule id | refuses |
|---|---|
| `semantic:derivation-term-ref` | an atom naming an undeclared fact type, or a role its fact type does not declare — head roles included |
| `semantic:derivation-rule-shape` | an unadmitted key (including `sum` and `or`), a missing/empty/non-list body, a non-mapping atom or comparison, a non-mapping or empty head, a rule on `derivation: asserted`, `storage: stored`, or a fact type with no roles |
| `semantic:aggregate-shape` | a malformed aggregate object, `over`, result variable, or value term |
| `semantic:aggregate-function` | an aggregate function outside the closed `count`, `sum`, `min`, `max`, and `avg` set |
| `semantic:aggregate-of-unbound` | an `of` term that reads a variable not bound by the positive body |
| `semantic:aggregate-over-unbound` | an `over` variable not bound by the positive body |
| `semantic:aggregate-over-duplicate` | a duplicate variable in the ordered `over` contribution identity |
| `semantic:aggregate-as-not-fresh` | an `as` result variable already used by the body, `over`, or `of` term |
| `semantic:aggregate-input-type` | a non-Integer input to `sum`, `min`, `max`, or `avg` |
| `semantic:aggregate-where-scope` | a post-aggregate comparison reading outside the group key and aggregate result |
| `semantic:aggregate-head-scope` | a head term reading outside the group key and aggregate result, including an unbound group variable |
| `semantic:aggregate-head-needs-round` | an `avg` result read by a head term whose outer function is not `round` — bare or nested alike |
| `semantic:derivation-structured-on-object-type` | a structured rule on an **object type** — derived subtypes and computed rosters are out of scope in this version |
| `semantic:derivation-role-claim` | an atom omitting a declared role of its fact type |
| `semantic:derivation-head-role-claim` | a head omitting a declared role of the fact type it derives |
| `semantic:term-function-name` | an unknown function, from either tier |
| `semantic:term-function-arity` | a function with the wrong arity, or `round`'s digit argument not statically Integer |
| `semantic:term-argument-type` | a nonnumeric function argument |
| `semantic:term-non-finite-number` | a non-finite numeric literal that evaluation cannot represent |
| `semantic:term-node-budget` | a recursive term exceeding the fixed node budget |
| `semantic:term-depth-budget` | a recursive term exceeding the fixed depth budget |
| `semantic:term-shape` | a term mapping outside the closed `{fn,args}` shape |
| `semantic:term-unbound` | a nested head variable not bound by the positive body |
| `semantic:derivation-head-term-type` | a head term incompatible with its declared role |
| `semantic:derivation-head-needs-round` | a non-Integer computed head whose outer function is an **exact-tier** function (add/sub/mul/neg/abs/mod) and is not `round` |
| `semantic:derivation-float-head-unquantized` | a non-Integer computed head whose outer function is a **float-tier** function (div/sqrt/floor/ceil/haversine) and is not `round` — `floor`/`ceil` are exempt, since their range is always Integer |
| `semantic:derivation-term-unbound` | an unbound `where` variable |
| `semantic:term-comparison-type` | incompatible `where` comparison operands |
| `semantic:derivation-head-unbound` | **range restriction**: a head variable no positive body atom binds |
| `semantic:derivation-negate-unbound` | **safety**: a negated variable no positive body atom binds |
| `semantic:derivation-body-component-unused` | a connected body component binding no head variable |
| `semantic:derivation-term-type` | a variable joining roles whose object types share no ancestor — the same compatibility predicate `semantic:op-term-type-compat` uses |
| `semantic:derivation-opaque-dependency` | a structured rule reading a fact type whose derivation is an opaque string |
| `semantic:derivation-unstratified` | a negative or aggregate dependency edge inside an SCC; the finding names that edge and cycle |
| `semantic:derivation-recursive-value-invention` | a computed function-valued head inside a positive recursive SCC |
| `semantic:derivation-effect-on-derived` | an operation effect asserting or retracting a structured `derived` fact type — a fully derived extension is a computed view, never operation-owned state |
| `semantic:derivation-effect-on-semiderived` | an operation effect asserting or retracting a structured `semiderived` fact type — Phase 2 preserves authored surplus but does not let an operation mutate that claim surface |
| `semantic:derivation-dynamic-dependency-incomplete` | a structured extension whose transitive asserted dependency closure cannot be classified completely — selective refresh fails closed rather than guessing |

### Disconnected bodies are legal — deliberately

A guarded *antecedent* refuses disconnection at evaluation time
(`join-disconnected`), because a disconnected antecedent is almost always an
authoring slip. A rule *body* is different: "a minor person and a flagged book"
is a genuine cross product and a genuine business rule, and the head's own arity
is what makes it well-formed. What is refused is weaker and more precise — every
component must **feed the head**. A component whose variables never reach the
head is an "if anything exists anywhere" guard, not part of the derived fact.

### Structured derivations during transitions

For each structured fact type, GND follows positive and negated rule
dependencies transitively to asserted leaves. A complete extension is
**static** when no operation can touch a leaf and **dynamic** otherwise. An
incomplete closure is refused before evaluation. Effects may name neither a
structured `derived` nor a structured `semiderived` fact type.

A transition's durable state remains asserted facts only. Let `A(i)` be that
durable state and `E(i)` the computed structured view. Initial `E(0)` is
computed once. For each step `i`, this order is normative:

1. evaluate preconditions against `A(i-1) + E(i-1)`;
2. apply effects to produce `A(i)` and grade asserted-subject dynamic rules;
3. select every dynamic head whose complete asserted dependency closure
   intersects the operation's touched set;
4. refresh exactly those heads in dependency order, retaining every other row
   from `E(i-1)`, to produce `E(i)`;
5. report the identity-set delta `E(i-1) -> E(i)` as per-step
   `derived_changes`;
6. grade structured-subject dynamic rules only when their dependency closure
   was touched and their grounded old/new subject differs;
7. re-load and check the synthetic intermediate `A(i) + E(i)` without treating
   its computed rows as a claimed extension; and
8. retain only `A(i)` as durable state for the next step.

Static heads are never refreshed. A later step reads the prior step's refreshed
view. Plan-mode `computed_post` contains ordinary asserted facts plus preserved
authored semiderived surplus, never generated derived rows. A declared post's
dynamic derivation claims are compared with the extension computed from the
validated asserted final state, so changing only the declared post's dependency
cannot self-justify its claim. Static post claims retain their independent
snapshot behavior.

Before evaluation, every selected or read dynamic head and every asserted leaf
in its transitive closure must appear in the supplied populations' `covers`.
An incomplete cover is refused as `transition:dynamic-derivation-coverage`.

The cost is stated rather than hidden: such a rule's computed extension is the
product of its component sizes, and the bound is over **intermediate component
joins**, not over the projected output.

### Scalar and tuple identity

Evaluation uses the `gnd-identity-json/1` identity codec. This table is the one
normative definition; implementations and independent oracles cite it rather
than restating it.

| Declared primitive | Admitted runtime value | Canonical token payload |
|---|---|---|
| `String` | `str` | `["string", value]` |
| `Integer` | `int`, excluding booleans | `["number", [numerator, denominator]]` |
| `Float` | finite integer or float, excluding booleans | the same reduced numeric payload |
| `Number` | finite integer or float, excluding booleans | the same reduced numeric payload |
| `Date` | validated ISO date string | `["string", value]` |
| `DateTime` | validated ISO datetime string | `["string", value]` |
| `Boolean` | boolean | `["boolean", value]` |
| `Binary` | validated string | `["string", value]` |

The denominator is positive and the fraction is reduced. A float contributes
its exact `as_integer_ratio()` value, so `1`, `1.0`, and positive or negative
zero share numeric identity while `true` remains distinct from `1`. The token
is UTF-8 JSON with `ensure_ascii=false` and separators `(',', ':')`. Tuple
identity is the ordered JSON array of scalar token payloads. Rows sort by those
UTF-8 bytes, which makes projection deduplication and witnesses independent of
Python hash order. Null, NaN, and infinities are not population scalars and
have no token.

### Stratification

Edges run **body/negate → head** and retain their positive, negative, or
aggregate polarity per clause. The graph is condensed into strongly connected
components (SCCs). A positive SCC is admitted, including a self-loop. A
negative or aggregate edge within its own SCC is refused as unstratified;
those edges may read only a completed lower SCC. SCCs are evaluated dependency
first, with stable fact-type-id ties. Inside a positive SCC, computed relations
start empty and all clauses repeatedly read the preceding complete relation
snapshot. Newly projected canonical tuples are unioned until no tuple is added:
this is the least fixpoint. Every head variable is bound by its own positive
body, and recursive computed head functions are refused, keeping the active
domain finite. An upper SCC reads the completed lower extension, never its
supplied claim.

Negation is **negation as failure** under the absolute closed world this
document already describes for the guarded family's `absence` consequent.

### Evaluation and claim comparison

> **The checker verifies a claimed derived extension. It does not become a
> generator.**

A population's rows for a structured derived fact type are a **claim**. The
checker first freezes asserted relations, evaluates structured rules in the
dependency-first order above, and never publishes the computed relations.
Positive atoms use identity joins; disconnected body components form their
declared product; safe negated atoms use closed-world non-existence; the head
projects in declared role order and deduplicates by tuple identity.

Every structured extension is computed even when its fact type is absent from
`population.covers`, because a higher stratum can still read it. Higher rules
always read computed lower structured extensions, for both `derived` and
`semiderived`; a claimed surplus never feeds an upper rule.

Comparison is one alethic obligation per fact type:

| Kind and coverage | Required relation | Result |
|---|---|---|
| listed `derived` | claimed set equals computed set | missing rows are `derived-extension-incomplete`; surplus rows are `derived-extension-unsound` |
| listed `semiderived` | computed set is a subset of the claim | missing rows are incomplete; claimed surplus is legal |
| unlisted structured rule | no claim was made | `unchecked`, reason `derivation-not-covered` |
| listed opaque string rule in a mixed structured model | no extension can be computed | `unchecked`, reason `derivation-rule-opaque` |

#### Opaque cells in structured derivations (v7.0 Phase 4)

A loader-admitted version-2 opaque cell denotes an unknown value of its role's
declared primitive. Its label is an explanation, never a scalar identity or an
equality key. The evaluator retains its source coordinate internally as a
finite wildcard. It computes two relations in each SCC of the stratification
above: **must** tuples proved by definite evidence, and **may** patterns that
can match some admitted completion. Definite membership takes priority over
possible membership. A tuple outside all may patterns is **out**; a tuple in
may but not must is **unknown**. The same SCC loop grows both relations to a
fixpoint. No scalar is invented to stand in for the unread cell.

A positive join involving a wildcard may provide a possible proof, but never a
definite equality proof. A negated lower relation is definite only when its
possible relation has no compatible tuple; it is possibly satisfied when its
definite relation has no matching tuple. An uncertain aggregate contribution,
group key, comparison operand, or computed head remains possible rather than
becoming a definite scalar. An exact term failure remains a distinct
unavailability reason.

For a covered `derived` head, a definite unclaimed tuple is incomplete, a
claimed tuple outside may is unsound, and a claimed unknown tuple is
`derived-extension-unresolved`. For `semiderived`, definite missing tuples are
incomplete and out surplus is legal; the owner-approved Phase 4 contract still
reports a claimed unknown tuple as unresolved. One verdict may carry definite
incomplete, definite unsound, and unresolved findings in that order. A verdict
with a definite finding is `fail`; unresolved alone is `unchecked` with reason
`derived-unknown`. Unknown tuples with no claim create no finding. A definite
failure takes band 1 before any unresolved band 4 result.

The exact unresolved finding and reason are emitted only by an
admission-requested schema-10 check. No-admission schema 7/9 retains its
coarse `opaque-value` projection. A constraint that actually depends on an
unknown derived row is unchecked unless a definite failure already decides
it. A grounded walk precondition with possible-only membership is unchecked
with `derived-unknown`; audit effects still apply, and dynamic refresh carries
the possible relation to the next step.

Coverage dispatches before rule-arm dispatch. Empty computed plus empty listed
claim is `pass`, never `vacuous`. A row can carry both findings, always
incomplete before unsound, but remains one obligation. Alethic failure selects
band 1; an unchecked derivation selects band 4 unless band 1 already wins.

Constraints run exactly once, after every extension and comparison, in their
original model order. They read a separately allocated view: listed structured
`derived` fact types expose their claims; unlisted structured `derived` fact
types expose an empty relation; structured `semiderived` fact types expose the
computed relation. Opaque and asserted fact types retain their population rows.
Thus a bad derived claim remains visible to constraints, while an unlisted
stored row and a legal semiderived surplus cannot satisfy one.

## Walks — `steps.json` and transition evaluation

A model's operations describe what MAY happen. A **walk** claims what DID: an ordered list of
operation invocations that carried a population from a pre-state to a post-state.

    gnd check MODEL --pre PRE --steps STEPS.json --post POST

This is the one normative account of the format and the evaluation. The schema lives beside this
file as `steps.schema.json`, vendored byte-identically into `src/gnd/schema/`.

### The document

```json
{ "steps_schema": 1,
  "model": "model.orm.yaml",
  "model_digest": "sha256:…",
  "operations_digest": "sha256:…",
  "pre_digest": "sha256:…",
  "steps": [ { "op": "approve_expense",
               "bindings": { "expense": 41, "approver": "alice" } } ] }
```

Step identity is the **1-based index**. Bindings supply **exactly** the operation's declared
parameters — no more, no fewer — and each value is type-checked against its parameter's object
type by the same predicate table that decides whether a value may sit in a population. One type
discipline: a walk cannot bind a value the checker would refuse in the data.

### Three digests, three bases, and why they differ

| field | basis | reason |
|---|---|---|
| `model_digest` | the loaded model object, as `population._model_digest` computes it | the same function a population's validation marker uses, so a population and a walk agree by construction about what "this model" means |
| `operations_digest` | canonical JSON over the raw `operations` section, before compilation | `model_digest` deliberately EXCLUDES operations (A8), so it cannot carry the claim "these steps were authored against THESE operations". A model can be identical in every other respect while its operations changed under a walk's feet |
| `pre_digest` (optional) | sha256 over the pre-population FILE BYTES | provenance, not equivalence: the question is whether this is the artifact the walk was written against, and for that question "you reformatted the file" is a legitimate no |

**No one should compute these by hand.** `gnd validate MODEL --trace` prints the first two, and a
`pre_digest` mismatch prints the value the tool computed, so repairing a pin is copy-paste.

`operations_digest` is `[]`'s digest for a v1 document, for an absent section and for an empty
one — all three mean "this model declares no operations". It canonicalizes dates to ISO text
(so a date in a provenance note cannot make the digest raise, and quoting style does not change
the value) and REFUSES anything outside that closed set with
`transition:operations-digest-unrepresentable` rather than crashing.

### Evaluation order (normative)

1. Load the model, load both populations, read and layer-1 validate the walk.
2. Verify `model_digest`, `operations_digest`, and `pre_digest` if present.
3. Validate the walk against the model: every `op` names a declared operation, every step binds
   exactly the declared parameters, every value matches its parameter's primitive.
4. **The frame-coverage gate.** Compute the touched union — every fact type any `assert` or
   `retract` of any operation in the walk names. A `create` contributes none: it names an object
   type, not a fact type. A pre- or post-population whose `covers` omits any of that union is
   REFUSED, never silently degraded.
5. **The structured-derivation coverage gate.** Every selected/read dynamic
   head and every asserted leaf in its complete transitive closure must be
   covered by the supplied populations.
6. Pre-state snapshot check, plus compiled obligations that do not depend on a
   later dynamic refresh.
7. Per step, apply the exact `A(i)` / `E(i)` order in “Structured derivations
   during transitions” above.
8. The frame check.
9. Declared-post snapshot check, replacing dynamic claims with comparison
   against the computed final asserted state.

**Steps 1 through 5 are the only ones that can refuse.** Exit 3 means the walk was refused BEFORE
evaluation began; anything discovered later is a verdict. An intermediate state that cannot be
re-loaded — for any reason, the 10 MB cap included — is `unchecked` at band 4, because it was not
found illegal, it was not examined.

### The frame check, and what it does not claim

Grading is **per fact type, never per walk**. A fact type touched only by alethic-framed operations
grades alethic: an undeclared delta on it is a hard failure. One touched by ANY deontic-framed
operation grades deontic, and the report names the operations whose declaration bought the
leniency. Grading is total because `frame` is required on every operation and never defaulted.

The comparison is declared-post against computed-final, per touched fact type, in both directions
(`undeclared-assert`, `undeclared-retract`). Fact equality is the checker's identity key over the
role map; the comparison is over SETS after that collapse, so a population carrying one ground fact
twice is not a delta; a fact type id is taken literally and `covers` names do not expand through
the subtype hierarchy.

**The comparison universe is the touched union only, and that is a stated soundness limit.** A
declared post differing on a fact type no operation in the walk names produces NO verdict, in
either direction. The frame check answers *"did the declared operations do anything they did not
declare"*, not *"did anything at all change"*. Step 8 still catches such a delta if it violates a
constraint — as a constraint violation, never as a frame finding.

### Compiled obligations

Some preconditions imply something durable. "Reimbursing requires the expense to have reached
Workday" plus "reimbursing records that it was reimbursed" gives *every reimbursed expense was
submitted* — a claim about data at rest, checkable with no walk at all. Deriving it is what
compilation means, and `gnd validate --trace` reports what compiled and what did not.

Only one shape compiles: a **literal-free, single-atom precondition sharing at least one parameter
with an asserted fact type**, where **exactly one operation in the model asserts that fact type**.
The second condition is what makes the claim follow: it generalizes over facts of the asserted
type, which is only sound if this operation is the only way such facts arise. Everything else is
retained as `transition-only` with the reason — retained is not skipped, it is evaluated per step
in the ordinary way.

Compiled obligations are evaluated against the PRE-state, for every operation the model declares
rather than only those a given walk uses: the claim is about the population, not about the walk.
They live in memory, never on `Model.constraints`, never in YAML, and never on the operation dicts
themselves — writing them there would move `operations_digest`, which is taken over exactly that
section.

### Opt-in compiled snapshot checks

`api.check(..., compiled_operations=True)` and `gnd check ... --compiled-operations`
evaluate compiler-eligible standing role-projection subsets without a walk. The
flag also applies to `--populations DIR --format json`. The caller asserts that
these operational implications are standing obligations of this population;
GND does not infer its operational provenance. Defaults continue to exclude
operations, and generated obligations stay outside authored `Model.constraints`.

Every eligible entry is evaluated against the normal effective constraint view:
semiderived relations use computed extensions, while derived relations use
covered claims whose derivation consistency is checked separately. Dynamic-derived
entries are instantaneous implications here; they do not establish dynamic step
rules or belong to walk agreement where the walk excludes them. Missing coverage,
unavailable/possible-only derived inputs or opaque participants produce explicit
unchecked results. Covered empty antecedents are vacuous. Matching uses typed
identity and every shared role pair. A global ceiling of 100,000 projected
role-cell visits yields unchecked `compiled-obligation-work-limit` on exhaustion.
Unknown participants are conservatively unchecked even when some known rows match.

Reports identify each generated obligation by its full compiler source locator,
with `constraint_type: compiled-subset`; messages name operation and precondition.
Alethic violations fail, deontic violations warn, and existing band precedence
applies. Single and batch reports use the same failure identifiers and counts.
Opted-in reports do not inherit proof-backed assurance from ordinary snapshots.
Occurrence admission (`--admission` / `admission=True`) and transition arguments
cannot be combined with this mode; they are explicitly refused.

Transition-only preconditions, dynamic step rules, effects, frame conditions and
intermediate-state constraints still require a walk. A snapshot result cannot
replace full-walk correctness, and `validate --trace` describes compiler
eligibility, not an assertion that default snapshots evaluate operations.

## Validation — two layers

A model is validated by `gnd.model.load_model()` in two deterministic layers. Both emit the same error-record shape (`json_path`-style location, message, `rule_id`).

### Layer 1 — structural (jsonschema, Draft 2020-12)

The normative meta-schema ([`orm-meta.schema.json`](orm-meta.schema.json)) enforces: required fields, enums (`source`, `status`, `modality`, ring `variant`, reference `mode`, `primitive`), the oneOf-discriminated per-family constraint shapes, per-source provenance if/then requirements, typo catching via `unevaluatedProperties: false`, and **required `modality` on every active constraint**.

### Layer 2 — semantic (plain Python; rules jsonschema cannot express)

| rule_id | Severity | Enforces |
|---|---|---|
| `semantic:id-unique` | error | ids unique across object_types + fact_types + operations + the optional `id:` a constraint carries — ONE namespace |
| `semantic:role-ref` | error | `roles[].object_type` resolves |
| `semantic:cross-ref` | error | every `{fact_type, role}` reference resolves to a declared fact type and role_name |
| `semantic:role-seq-arity` | error | a set-comparison constraint (`subset`, `equality`, `exclusion`, `exclusive-or`) compares role sequences of equal length — compatibility presupposes equal arity |
| `semantic:role-seq-type-compat` | error | at every position, the compared roles are played by compatible object types (same type, or types sharing a common supertype) |
| `semantic:disjunctive-subject-type` | error | single-role mandatory-disjunctive and exclusive-or constraints reference one declaration-order-neutral subject object type |
| `semantic:join-anchor-ambiguous` | error | inferred cross-fact joins do not have multiple candidate anchor roles of the same object type |
| `semantic:reading-placeholders` | error | `{Type}` placeholder count equals `len(roles)`, and normalized labels identify the roles' object types in declared order |
| `semantic:fact-type-arity` | error | an explicit fact-type `arity` equals the number of declared roles |
| `semantic:role-names-distinct` | error | every role of a fact type carries a distinct role_name, whatever its object type — a shared name shrinks the fact type's declared role set, so a fact filling only one of the two colliding roles would be structurally conformant |
| `semantic:subtype-ref` | error | `subtype_of` targets resolve |
| `semantic:external-ref-uc` | error | `reference.mode: external` implies a top-level external UC whose role_refs' fact types all play a role of the entity |
| `semantic:reference-value-type` | error | `reference.value_type` resolves to a value-kind object type |
| `semantic:value-range-type` | error | value-range endpoints match the constrained object type's resolved primitive |
| `semantic:value-range-order` | error | each fully bounded numeric, string, Date, or DateTime range has `min <= max` after temporal normalization |
| `semantic:count-bound-order` | error | frequency and cardinality count intervals have `min <= max` |
| `semantic:status-source` | error | explicit/user-supplied ⇒ confirmed; status `rejected` only in rejected_proposals. Applies to every provenance-bearing element — constraints, v2 operations, and each operation obligation |
| `semantic:string-ref` | error | WR-01: every plain-string reference resolves — inline `roles`/`role` against the host fact type, `object_type`/`supertype`/`subtypes[]`/`objectified_as` against declared object-type ids, and inline value-comparison operands |
| `semantic:ring-binary` | error | a `ring` constraint's host fact type is binary with both roles played by compatible object types (Halpin's ring precondition) |
| `semantic:partition-asserts-nothing` | error | a `subtype-partition` sets `exclusive: true`, `exhaustive: true`, or both — an ORM 2 partition is the conjunction of subtype exclusion and subtype totality (Halpin 2e §6.5) and has exactly the three readings [constraint-reference.md](constraint-reference.md) lists; a constraint with neither flag asserts nothing and cannot be satisfied or violated |
| `semantic:modality-policy` | warning | D-03: llm-inferred/common-sense + proposed + alethic ⇒ warn (deontic until user-confirmed) |
| `semantic:textual-alethic` | warning | D-20: a `textual` constraint carrying `modality: alethic` makes the model permanently indeterminate — see [provenance-and-modality.md](provenance-and-modality.md) |
| `semantic:op-param-ref` | error | every operation parameter's `object_type` resolves |
| `semantic:op-param-names-distinct` | error | no operation declares one parameter name twice |
| `semantic:op-reading-placeholders` | error | every `{…}` in an operation reading resolves to exactly one unclaimed parameter — a subset rule, not the fact-type bijection |
| `semantic:op-atom-ref` | error | every atom's `fact_type` resolves, and every `bind` key (plus a dynamic rule's `value_role`) names a role of it |
| `semantic:op-term-ref` | error | every `$var` — in a precondition, an effect, or a dynamic subject — names a declared parameter of its own operation |
| `semantic:op-term-type-compat` | error | a parameter bound to a role can play it (same compatibility predicate as `semantic:ring-binary`) |
| `semantic:op-effect-ground` | error | an `assert` effect binds EVERY declared role of its fact type; `retract` may still wildcard |
| `semantic:op-create-param` | error | `create.param` is a declared parameter of that parameter's own type, created once, and not referenced by any precondition |
| `semantic:op-create-ref-mode` | error | `create` targets an entity type that resolves to an identifying value type — reference mode `popular` or `general`, its own or inherited through `inherits_reference` — since nothing else has a caller-suppliable identifier |
| `semantic:op-obligation-ids-distinct` | error | precondition and dynamic-rule ids are distinct within one operation |
| `semantic:imported-provenance` | error | an `imported` claim's `framework`, `artifact`, `commit`, `sha256` and `anchor` are present and non-blank |
| `semantic:imported-confirmed-reviewed` | error | an `imported` claim with `status: confirmed` names a non-blank `reviewed_in` |
| `semantic:op-dynamic-functional` | warning | a dynamic rule's subject is not proven functional by an internal uniqueness constraint over its non-value roles — the rule will evaluate `unchecked` |
| `semantic:op-dynamic-untouched` | warning | a dynamic rule's subject is a fact type NO effect of its own operation touches, so the rule can never fire — the evaluator judges only transitions a step actually makes, and reports nothing for such a rule |
| `semantic:op-modality-policy` | warning | D-03 extended to operation obligations: llm-inferred/common-sense + proposed + alethic ⇒ warn |
| `semantic:guarded-term-ref` | error | every guarded atom's `fact_type` resolves, and every `bind` key names a declared role of that fact type |
| `semantic:guarded-role-claim` | error | every guarded atom binds exactly the roles declared by its fact type; missing roles are refused |
| `semantic:guarded-consequent-ground` | error | every `$`-variable in an atom, absence, or comparison consequent is introduced by an antecedent bind |
| `semantic:guarded-comparison-type` | error | guarded comparison operands have compatible primitive types after variable-role and literal resolution |
| `semantic:guarded-exists-range` | error | variables nested in exists.where exact functions are antecedent-bound or bound by a positive exists atom |
| `semantic:guarded-exists-where-bound` | error | every exists.where variable is bound by the antecedent or a positive exists atom |
| `semantic:guarded-exists-where-type` | error | exists.where operands have compatible resolved primitive types |
| `semantic:derivation-term-ref` | error | every structured derivation atom names a declared fact type and only roles that fact type declares, head roles included |
| `semantic:derivation-rule-shape` | error | the structured rule admits only `body`, `negate`, `aggregate`, `where` and `head`, with a non-empty list body of mapping atoms, mapping comparisons, and a non-empty mapping head, on a `derived`/`semiderived` fact type that declares roles and does not claim `storage: stored` |
| `semantic:aggregate-shape` | error | an aggregate has the closed object shape, a non-empty ordered `over`, and variable-shaped `over` and `as` entries |
| `semantic:aggregate-function` | error | aggregate functions come from the closed `count`, `sum`, `min`, `max`, and `avg` table |
| `semantic:aggregate-of-unbound` | error | every variable read by the aggregate `of` term is positively bound |
| `semantic:aggregate-over-unbound` | error | every aggregate `over` variable is positively bound |
| `semantic:aggregate-over-duplicate` | error | aggregate `over` variables are unique while retaining their declared order |
| `semantic:aggregate-as-not-fresh` | error | the aggregate `as` variable is fresh with respect to the body, `over`, and `of` term |
| `semantic:aggregate-input-type` | error | `sum`, `min`, `max`, and `avg` receive Integer-valued inputs; `count` accepts any admitted scalar |
| `semantic:aggregate-where-scope` | error | post-aggregate comparisons read only group variables and the aggregate result |
| `semantic:aggregate-head-scope` | error | aggregate heads read only positively bound group variables and the aggregate result |
| `semantic:aggregate-head-needs-round` | error | an `avg` result reaches a head only through an outer `round(term, digits)` call |
| `semantic:derivation-structured-on-object-type` | error | a structured rule on an object type is refused: derived subtypes and computed rosters are out of scope in this version |
| `semantic:derivation-role-claim` | error | every structured derivation atom binds every role its fact type declares |
| `semantic:derivation-head-role-claim` | error | the head binds every role of the fact type it derives |
| `semantic:term-function-name` | error | exact functions come from the closed table |
| `semantic:term-function-arity` | error | every exact function uses its declared arity |
| `semantic:term-argument-type` | error | exact functions receive numeric arguments |
| `semantic:term-non-finite-number` | error | every exact numeric literal is finite |
| `semantic:term-node-budget` | error | recursive terms stay within the fixed node budget |
| `semantic:term-depth-budget` | error | recursive terms stay within the fixed depth budget |
| `semantic:term-shape` | error | every term mapping has exactly the closed `{fn,args}` shape |
| `semantic:term-unbound` | error | every nested head variable is positively bound |
| `semantic:derivation-head-term-type` | error | every head term matches its declared role |
| `semantic:derivation-head-needs-round` | error | an exact-tier computed head is Integer-valued or wrapped in `round` |
| `semantic:derivation-float-head-unquantized` | error | a float-tier computed head is `round`-wrapped, or is `floor`/`ceil` (always Integer-valued) |
| `semantic:derivation-term-unbound` | error | every `where` variable is positively bound |
| `semantic:term-comparison-type` | error | both `where` operands have compatible types |
| `semantic:derivation-head-unbound` | error | range restriction: every head variable is bound by a positive body atom |
| `semantic:derivation-negate-unbound` | error | safety: every negated variable is bound by a positive body atom |
| `semantic:derivation-body-component-unused` | error | every connected component of the body binds at least one head variable |
| `semantic:derivation-term-type` | error | a variable may not join roles whose object types share no ancestor closure |
| `semantic:derivation-opaque-dependency` | error | a structured rule may not read a fact type whose derivation is an opaque string |
| `semantic:derivation-unstratified` | error | negative and aggregate edges do not occur inside their own SCC |
| `semantic:derivation-recursive-value-invention` | error | a positive recursive head does not compute a new value |
| `semantic:derivation-effect-on-derived` | error | operation effects may not assert or retract a structured `derived` fact type; fully derived facts are computed views |
| `semantic:derivation-effect-on-semiderived` | error | operation effects may not assert or retract a structured `semiderived` fact type; authored surplus survives but is not operation-owned state |
| `semantic:derivation-dynamic-dependency-incomplete` | error | a dynamic extension's transitive positive-or-negated asserted dependency closure must be complete before selective refresh is admitted |
| `semantic:anchored-invalid` | error | an inline anchor selects a declared role, and each role recogniser fits that role's resolved primitive |
| `semantic:induced-provenance` | error | an `induced` claim's induction block is consistent: support numerator ≤ denominator, listed examples ≤ numerator, counterexamples ≤ denominator − numerator, no id in both lists, and no whitespace in a token, id, ref or digest |
| `semantic:induced-confirmed-reviewed` | error | an `induced` claim with `status: confirmed` names a non-blank `reviewed_in` |

Errors abort the load with a pointed message naming the offending element; warnings ride on the loaded model and are printed by `gnd validate` (exit 0 when only warnings exist).

The table lists every entry of `gnd.model._SEMANTIC_RULES`, in registration order. Adding a rule without adding a row here leaves the normative reference describing a loader that no longer exists — the failure mode phase 01.1 was created to remove.

## What this format does NOT capture in v1

- **Multi-language readings.** English only.
- **Visual / layout metadata.** No coordinates, colors, diagram positions. The YAML is the conceptual model, not a diagram.
- **Opaque multi-rule derivation chain validation.** For *opaque string* rules,
  chain consistency is not validated and derivation-dependent constraints are
  reported `unchecked`. Structured fact-type rules are chain-validated at load
  and their extensions are evaluated and compared as defined above.
- **FORML 2 parsing.** Textual constraints are stored verbatim; no formal-language interpretation. The checker reports `textual` constraints as `unchecked`.

These are documented gaps, not bugs.

---
*Adapted from the rai-agent-skills ORM skills (branch an-orm-skill).*


## Calendar-day terms (v7.1)

Model `version: 3` opts into `primitive: Duration` and temporal guarded
comparison operands. Versions 1 and 2 refuse these constructs; version 3
retains the version-2 operations grammar. Duration is an integer calendar-day
count from 0 through 1,000,000 inclusive. Booleans, floating point values and
strings are invalid. Duration and Integer are distinct domains: Duration roles
may compare with Duration roles or tagged Duration literals, but cannot unify
with Integer roles or accept numeric arithmetic.

The exact literals are `{"duration_days": 2}` and `{"date": "2024-02-29"}`.
No extra keys are admitted. Dates must be real Gregorian days in the exact
YYYY-MM-DD format, years 0001 through 9999. The only functions are
`{"fn": "date_add", "args": ["$day", {"duration_days": 2}]}` and
`{"fn": "date_sub", "args": ["$day", "$allowance"]}`. Both have type
Date × Duration → Date. They advance or retreat integral calendar days,
including leap days and zero; they define no timezone, timestamp, month,
business-day or Date-minus-Date arithmetic.

Tags and date functions are admitted only in guarded consequent comparison
operands. Derivation heads/filters, operation bindings and guarded exists
filters refuse them. Duration value ranges use untagged integer endpoints in
the declared Duration domain. All terms retain the shared depth-32 and
256-node budgets. Each guarded constraint evaluates at most 10,000 temporal
function applications using a streaming join. Empty antecedents remain vacuous;
only reached operands are evaluated.

A reached opaque operand yields `term:opaque-date-operand`; an unrepresentable
result date yields `term:date-out-of-range`; exceeding the application budget
yields `term:temporal-work-limit`. These are unchecked findings, with existing
alethic/deontic band precedence and unknown precedence inside a constraint.
Malformed input dates or durations fail validation instead.

Temporal ordinary checks and transitions select report version 11, with the
fixed version-9 keys and no admission field. Temporal admission is refused
at exit 3. Synth, measure, codegen, conformance, diff, extraction, document
checking and the existing PyRel exporter refuse temporal models at exit 3
before publishing output. Model validation, population loading and ordinary
check/transition support this fragment; no new assurance is claimed.


## Fixed reference populations (version 4)

A version-4 model may declare fixed input populations alongside candidate facts:

```yaml
reference_populations:
  - id: catalog
    path: references/catalog.pop.json
    sha256: <64 lowercase hexadecimal digits of the exact file bytes>
    fact_types: [catalog_pair]
```

Each declaration has exactly these four fields. IDs are unique, nonempty and at
most 128 characters. Ownership is disjoint across declarations and covers only
existing base fact types. Candidate populations cannot mention owned fact types,
even with an empty list. Operations may read them but cannot assert or retract
them. References use ordinary population formats 1/2 and assert only their owned
fact types; they cannot include further references.

Paths are confined POSIX relative paths beneath the explicit model parent, with
no symlink in the root, ancestors or leaf. At most 32 files, 32 MiB in total,
10 MiB per input, 32 path components and 4096 path characters are admitted.
The combined view admits at most 100000 asserted rows and 100000 instance entries,
counted separately; reference container depth is at most 64. Reached attempted
combined join work is capped at 100000 before materialization and deduplication.
Input refusal is band 3; exceeded evaluation work is unchecked, band 4 unless
an independent definite violation establishes band 1.

Model and reference bytes bind once per invocation. A loaded model retains its
context; `load_model_bytes` requires `bind_references(model, root=...)` and an
explicit matching `references=` context at use. The combined view supplies fixed
facts to constraints and derivations. Candidate counts and admission contain
only candidate occurrences. Reference-bearing reports use the closed version-12
wrapper with a binding roster and asserted occurrence origins; embedded reports
retain their existing mechanical version. Reference identity binds normalized
model content plus sorted declarations, including path, ownership and expected
raw hash. `model_id` remains a separate opaque identifier. Versions 1–3 reject
this field; a feature-free version 4 retains the ordinary wire and behavior.

Check, batch, transition and diff consume bound references. Synth, codegen and
older session contracts refuse reference-bearing inputs before publishing
artifacts or invoking an adapter. Conformance can report changed model identity;
it never regenerates code. Extraction projects candidate-owned fact types only.

## Repair annotations

Every constraint may carry `owner: candidate | reference | host` and an optional
unique `allowed_fixes` list drawn from `add-fact`, `replace-fact`, `delete-fact`
and `replace-artifact` (at most four). Missing owner means candidate. These
annotations describe repair responsibility; they do not change evaluation,
modality, provenance, coverage floors or acceptance. Verbalization preserves
them as metadata and does not invent a rule. Session behavior lives in
[the v7 contract](../../gnd-dev-session/references/session-v7-contract.md).

For explicitly selected saved opinion evidence, see the [judgment contract](../../gnd-dev-session/references/judgment-contract.md).
