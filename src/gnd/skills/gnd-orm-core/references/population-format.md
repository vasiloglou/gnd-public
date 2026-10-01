# Population Format

**The normative spec** for GND population files (CORE-02) — the universal interchange every population flows through, whether it is an **agent output**, a **synthetic dataset**, or an **eval fixture**. One format, one loader, one checker.

Normative machine spec: [`population.schema.json`](population.schema.json) in this skill's references directory (vendored byte-identically in the `gnd` package at `src/gnd/schema/population.schema.json`, sync-tested). The prose here is explanatory; where prose and schema disagree, the schema wins.

Cross-references:
- The model the population is checked against → [representation-format.md](representation-format.md)
- Per-family checkability and CNL messages → [constraint-reference.md](constraint-reference.md)
- Source-anchor sidecar binding and matching → [constraint-reference.md#source-anchoring-v70](constraint-reference.md#source-anchoring-v70)
- Alethic vs deontic verdict severity → [provenance-and-modality.md](provenance-and-modality.md)

## File shape (D-10)

A population file is YAML or JSON with three parts: a `population` header, an optional `instances` section, and a `facts` section. A root `format_version` may select version 2; absent and explicit 1 use the original scalar-only grammar.

```yaml
# population file — YAML or JSON, same loader
population:
  model: model.orm.yaml            # reference to the model this population belongs to
  model_id: urn:example:movies@3   # optional: the model's own model_id, cross-checked
  source: synthetic                # agent-output | synthetic | fixture  (REQUIRED)
  label: violating                 # optional: conforming | boundary | violating
  covers: [movie_has_title, movie_directed_by_director]   # declared fact-type coverage

instances:                         # optional explicit object-type rosters (closed-world extension)
  movie: [1, 2, 3]

facts:                             # keyed by fact_type id; each fact keyed by role_name
  movie_has_title:
    - { movie: 1, title: "The Departed" }
    - { movie: 1, title: "Also The Departed" }   # violates uniqueness on [movie]
  movie_directed_by_director: []   # declared covered but empty → vacuous
```

### Header fields

- **`model`** (required): a reference — path or identifier — to the `model.orm.yaml` this population is checked against. **The loader never opens this reference**; it is declarative metadata. The caller passes the model separately to the checker, which may cross-check the reference for reporting.
- **`model_id`** (optional): the model's own top-level `model_id`, restated here so the file can say *which* model it was written for. It is **compared as an opaque string and never dereferenced** — nothing is resolved to a path, opened, parsed as a URN, or normalised (two ids differing only in case or a trailing slash are different ids). Three outcomes, and only three:
  - model and population both declare one, and they **differ** → **error, exit 3** (`population:model-id-mismatch`). The population was written for a different model.
  - the model declares one and the population **omits** it → **warning** (`population:model-id-absent`). The cross-check is skipped; acceptance is **not** withheld, because the field is optional for backward compatibility and every population written before it existed omits it.
  - **neither** declares one → no check at all. (A population that declares an id against a model that declares none is also no check: there is no model identity for the claim to disagree with.)

  This is belt-and-braces. The load-bearing guarantee that a population was validated against *this* model is a runtime marker the loader stamps and the checker demands — an id an agent writes into its own output can always be made to match.
- **`source`** (required): `agent-output` | `synthetic` | `fixture`. All three producers use this same format and the same loader — the field records which producer wrote the file, nothing more. No format behavior varies by source.
- **`label`** (optional): `conforming` | `boundary` | `violating`. The expected-outcome class for labeled datasets (synthetic generation and verifier evaluation use it; agent outputs normally omit it).
- **`covers`** (optional list): the fact-type ids the population **claims completeness for**. Declaring a fact type in `covers` means "this file is asserting the full population of that fact type" — which is what makes vacuity detectable (see below). An omitted `covers` claims completeness for nothing.

#### Deterministic document-extraction `covers`

For a deterministic document-extraction header, the scope classes are:
**included = `asserted`, `legacy-opaque`; excluded = `structured-derived`**.
Accordingly, `covers` contains every asserted fact type and every fact type
whose `derivation_rule` is the legacy opaque string arm, and excludes every
fact type whose `derivation_rule` is the structured object arm. The extractor
never authors this list; it copies the emitted header template verbatim.

Excluding a structured-derived fact type means that the extracted population
makes no claim about its computed extension. Its derivation obligation is
therefore `unchecked` with `derivation-not-covered`; when the obligation is
alethic, the round trip is honestly **Band 4 (`indeterminate`)**, not a failed
claim and not acceptance. Structured-rule syntax, evaluation, and complete
claim-comparison semantics remain solely in
[representation-format.md](representation-format.md#orm--derived-fact-types).

### `facts` section

- Keyed by **fact-type id** (must match `fact_types[].id` in the model).
- Each entry is a list of fact instances; each fact instance is a mapping from **role_name** (as declared on the fact type's roles) to a scalar value. Under root `format_version: 2`, a fact-role value may instead be the exact marker `{"$opaque":"<nonempty label>"}`. No other keys or nested markers are allowed. Rosters in `instances` remain scalar-only.

An opaque marker says the value is present but unreadable. Its label identifies the source location for the author; it is never treated as a value, compared for equality, or emitted as a witness. A constraint that reads the marker is `unchecked` with `opaque-value`; an alethic unchecked result contributes band 4 unless a definite failure takes precedence. The marker is legal in any declared fact role whose primitive type would otherwise be checked. A version-1 marker is a layer-1 input error at band 3.
- Unary fact types have single-key facts; ternary+ fact types have one key per role.

For a fact type with a **structured** `derivation_rule`, rows in `facts` are a
claim about its extension, not asserted input to the rule evaluator. The
checker recomputes the extension without publishing it. Listing the fact type
in `population.covers` makes the claim complete and creates one comparison
obligation. Omitting it means no claim was made: stored rows do not become
assertions and the derivation obligation is `unchecked` with
`derivation-not-covered`. For `derived`, claimed and computed sets must be
equal. For `semiderived`, the computed set must be contained in the claim;
claimed surplus is legal for comparison but is inert to higher rules and
constraints. The full evaluation and scalar-identity semantics have one home
in [representation-format.md](representation-format.md#evaluation-and-claim-comparison).

### Entity references

Entity values in facts use the entity's **reference-scheme value** — the value of its identifying value type. `movie: 1` means the Movie whose MovieId is 1; a Director identified by name appears as `director: "Martin Scorsese"`. Ordinary values are scalars (string, number, boolean); the version-2 opaque marker above is the sole nested role-value form.

## One loader (D-11)

`gnd.population.load_population()` is the **only** entry point for reading population files — for agent outputs, synthetic data, and eval fixtures alike. It accepts:

- **YAML** (`.yaml` / `.yml`) — parsed with safe loading; no arbitrary-object construction.
- **JSON** (`.json`) — parsed with the stdlib and fed through the *same* construction path.

Both frontends produce identical objects for equivalent documents. No consumer may parse population files directly; if any code outside the loader reads population YAML/JSON, that is a bug.

**Size cap:** files larger than **10 MB** are rejected before parsing (load error, exit 3). Agent outputs are untrusted input; the cap bounds parser exposure. The byte cap alone does not bound YAML alias amplification, so YAML **anchors/aliases are rejected** by a parse-event pre-scan before any node construction (aliases are a YAML-only construct; rejecting them also preserves YAML/JSON parity). The same 10 MB cap applies to model files.

**Validation on load** happens in two layers, in this order:

1. **Layer 1 — syntax**, against `population.schema.json`. Model-independent: it cannot know whether `movie_has_title` is a fact type or which roles it declares.
2. **Layer 2 — model-relative conformance**, run whenever the loader is given a model. This is the section below.

Both layers emit the same `json_path`-addressed issue records, and both fail at **exit 3**.

## Model-relative conformance (CORE-04)

> A population that is *syntactically* valid can still be nonsense *against a particular model*. This layer is what makes "the checker evaluated your output" mean something.

**Why it exists.** A fact that omits one of its fact type's roles used to be silently filtered out before evaluation — so a file whose two facts both omitted a mandatory, uniquely-constrained role reported `pass=2 fail=0 unchecked=0 vacuous=0` and **exit 0**. It did not merely miss the violation; it affirmatively stated that both constraints were satisfied. Every rule below closes a variant of that shape.

The rule set is **strict structural conformance**. A fact must supply *exactly* the role set its fact type declares; every id must resolve; every value must match its primitive.

| Rule id | Severity | What it rejects |
|---|---|---|
| `population:unknown-fact-type` | error | A key of `facts:` that is not a fact type in the model. |
| `population:unknown-object-type` | error | A key of `instances:` that is not an object type in the model. |
| `population:unknown-covers` | error | A `covers` entry that is not a fact type in the model — the completeness claim would be unverifiable. |
| `population:duplicate-covers` | error | The same fact type listed in `covers` more than once. |
| `population:missing-role` | error | A fact that omits a role its fact type declares. |
| `population:extra-role` | error | A fact that supplies a role name the fact type does not declare. |
| `population:type-mismatch` | error | A fact value, or an `instances:` roster entry, whose type does not match the primitive its object type resolves to. |
| `population:model-id-mismatch` | error | Header `model_id` present on both sides and different (see above). |
| `population:model-id-absent` | **warning** | Model declares `model_id`, population omits it. Never blocks acceptance. |

**Rules collect; none aborts.** Exit 3 is where a retry loop most needs feedback, so every rule runs and every issue is reported — a loop that got one issue per round trip would need N rounds. Where one rule already owns a key, later rules skip it (an undeclared fact type has no role set to compare against; an undeclared role has no object type and therefore no primitive).

**A missing role is exit 3, not exit 1.** Shape is not a rule. "Your output isn't shaped like the model" and "your output breaks a business rule" are different feedback and must not be conflated.

**There is no bypass.** No `--lax`, no `--no-strict`, no environment variable. Populations that *violate constraints* on purpose (labeled `violating`) are a different axis entirely: they are well-shaped files that fail their rules, and they need no escape hatch.

### Primitive type conformance — resolve or skip, never guess

Each role's value is checked against the primitive its object type resolves to:

- a `kind: value` object type yields its `primitive` directly;
- an entity type resolves through `reference.value_type`;
- an entity **subtype** declaring `inherits_reference: true` resolves through its supertypes, and only when every resolvable ancestor agrees on exactly one primitive.

| Primitive | Accepts |
|---|---|
| `String` | a string |
| `Integer` | a whole number — **not** `true`/`false` |
| `Float`, `Number` | a whole *or* fractional number — **not** `true`/`false`. `1` is accepted for a `Float` role: YAML and JSON both load `1` as an integer, so rejecting it would make validity depend on a rendering accident |
| `Boolean` | `true` / `false` — **not** `1`/`0` |
| `Date` | an ISO-8601 calendar date, `YYYY-MM-DD`. Format-checked, because the checker orders dates by *lexical string comparison*: `"01/02/2026"` would compare wrongly and silently |
| `DateTime` | an ISO-8601 datetime, e.g. `2026-01-01T12:30:00Z` — optional seconds, fractional seconds and `Z`/±hh:mm offset |
| `Binary` | a string; no encoding format is imposed |

When **no primitive is resolvable**, the role is simply **not type-checked**, and nothing is reported — no error and no warning. This is deliberate: a skipped check is honest, an invented one is not. Resolution legitimately fails for `unit-based` and `external` reference modes, for a subtype declaring `inherits_reference: false` with no reference of its own, and for multiple inheritance whose ancestors disagree on a primitive.

One consequence worth stating plainly: type validation is also what keeps ill-typed data out of the checker's ordering comparisons. Before it existed, a string in a numerically-constrained role crashed the checker and exited **70** — reporting bad *data* as a tool *bug*.

## Closed-world object-type population semantics

ORM constraints like `mandatory` quantify over "every instance of the object type" — but a population file contains *facts*, not instance rosters. GND defines:

> The population of object type T = all values playing any role typed T across all facts in the file, **plus** any values listed under the optional `instances:` section for T (explicit rosters that **extend** the derived set).

The `instances:` extension exists to declare instances that play no facts — which is what makes `mandatory` violations detectable (an instance observed anywhere that lacks its mandatory role → fail) and lets populations exercise `independent: true` semantics. Without it, an object type's population is exactly the fact-derived set.

Subtype membership is observable the same way: via `instances:` rosters for the subtype or via subtype-typed roles played in facts. Membership that exists only through a derivation rule is not observable — the checker reports those subtype constraints `unchecked`.

**Reference schemes populate value types.** Because an entity value in a fact *is* the entity's identifying value (see "Entity references" above), the population of a **value type** V additionally contains every value playing a role typed to any entity type whose reference scheme resolves to V — through `reference.value_type`, following `inherits_reference` up `subtype_of`, exactly as the loader's type check does. `movie: 999999` puts `999999` into MovieId's population; if MovieId carries a `value` range or a `cardinality` bound, that value is checked against it.

This is not an optional refinement. The loader resolves `movie → movie_id` in order to *type-check* `999999` as an Integer MovieId, and rejects the population at exit 3 when it is not one. A checker that then declined to range-check the same value as a MovieId would be asserting that one value is a MovieId for typing and not a MovieId for constraints. Left un-collected, an alethic `value` or `cardinality` constraint on a reference value type reported `pass` — *"— satisfied"* — at **exit 0** over a population that visibly contained violating values, and the cardinality wording said so out loud: *"is at most 2 — satisfied (0 observed)"* over a population holding four. The widening runs in one direction only: a value type collects the values that denote entities; an entity type never collects anything from the value types it is identified by.

## Vacuity (D-12)

Vacuity is first-class: an empty or evasive population must never produce a clean pass. A constraint verdict is **`vacuous`** when any clause holds:

1. **Empty-subject vacuity.** All of the constraint's subject fact types carry **zero facts** in the population — whether or not they are declared in `covers`. A covered-but-empty fact type is vacuous by declaration; an omitted-and-empty fact type is vacuous too — it never yields a silent pass. **Guarded constraints use the stricter ANY-empty form:** if even one antecedent fact type carries zero facts, the guarded constraint is vacuous, because its conjunctive antecedent can have no observable binding. Other families retain the ALL-empty rule.
2. **Coverage-omission vacuity.** A **mandatory-relevant** constraint (`mandatory`, `mandatory-disjunctive`) whose subject fact type is **omitted from `covers`** is vacuous even when facts for it are present — the population does not claim completeness for that fact type, so "every instance plays the role" cannot be affirmed. Other constraint families over an uncovered-but-populated fact type still evaluate.
3. **No-observable-subjects vacuity.** An **object-type-scoped** constraint (`value`, `cardinality`, `subtype-partition` in their object-type form) whose object type has **no population at all** — no fact type gives it one and no `instances:` roster supplies one — is vacuous rather than `pass`. This is the same state as clause 1 reached by a different route: a subject fact type that is present but empty, versus no subject fact type in the model at all. Reporting the first as `vacuous` at exit 2 and the second as `pass` at exit 0 was an inconsistency, and it is what let an unevaluated constraint reach `acceptance_ready: true`.

   Clause 3 is bounded by design, and the boundary is normative:
   - An `instances:` roster **does** supply subjects, so a roster-only population is evaluated, not called vacuous. The test is on the object type's *population*, never on whether some fact type happens to mention it.
   - It can only ever overturn a `pass`. A **lower bound violated by a count of zero** — `cardinality { min: 1 }` over an empty universe — is *decided*: the count is the evidence. That stays `fail` at exit 1.
   - It never applies to a family reported `unchecked`, which is decided earlier in the resolution order. An alethic `textual` constraint stays **indeterminate at exit 4**, not vacuous at exit 2.

4. **Zero-row-joined-subject vacuity.** A **join-scoped** constraint whose subject role sequence(s) span **more than one fact type** and whose **join yields zero rows** is `vacuous` rather than `pass`, **even when every referenced fact type is individually populated** — the join, not the scope, is the universe. Two fully-populated fact types whose shared anchor values are disjoint join to nothing, and a constraint over that empty join has no subjects to affirm satisfaction over (this is F-05: the same defect as clause 3 one relation over — the checker had tested the *scope*, whether the fact types are empty, never the *universe*, whether the join produced rows).

   The per-family rule is by quantifier, and it matches the checker's `_JOIN_SUBJECT_SEQS` table exactly:
   - **ANY** (external `uniqueness`, external `frequency`, cross-fact `value-comparison`): the constraint has one joined subject sequence, so it is vacuous when that join is empty. Cross-fact `value-comparison` is one *combined* join of `[role_a, role_b]`, evaluated once — not two independent single-ref projections.
   - **ALL** (`equality`, `exclusion`): the constraint has two sides, so it is vacuous only when **both** joins are empty. One non-empty side keeps it decided — `only_b` non-empty makes `equality` a `fail`; `∅ ∩ X = ∅` makes `exclusion` a correct `pass`.

   Two families are **deliberately excluded**, and the exclusion is normative:
   - `subset`: `∅ ⊆ X` is a **decided `pass`**, ratified against Halpin — an empty subset side is genuinely contained in any superset. Only the *superset* side joining to zero rows while the subset side has members is a decision, and that stays `fail`. `subset` is therefore never downgraded to vacuous by this clause.
   - `exclusive-or`: its multi-role branch returns `unchecked` before it can reach `pass`, and its single-role branch quantifies over an object-type universe rather than a join, so no zero-row join can reach a `pass` for it.

   Like clause 3, this clause can only ever overturn a `pass` — a `fail` over a zero-row join (a subset member with no superset) is a real decision and stays at exit 1 — and it never applies to a family reported `unchecked`.

Verdict resolution order (normative, encoded once in the checker): **vacuous (clauses 1–2) → unchecked → evaluate (alethic violation = `fail`, deontic violation = `warning`) → `pass`, downgraded to vacuous when the universe is empty — by clause 3 when the object-type universe is empty, and by clause 4 when the joined universe is empty even though the referenced fact types are populated**.

Consequences worth internalizing:

- An entirely empty population produces **zero passes** — every constraint is vacuous. A checker run that reports all-pass on an empty file is broken.
- `covers: []` (or an omitted `covers`) makes every mandatory-relevant constraint vacuous and every other constraint vacuous-or-evaluated per clause 1.
- Vacuity is a *population inadequacy* signal, distinct both from a constraint violation and from an **indeterminate** run (a constraint the checker never mechanically evaluated) — the exit-code bands keep all three distinguishable. Vacuous is a *decided* state: the constraint was evaluated and had no subjects. Indeterminate means the machinery never ran at all.

## Exit-code bands

`gnd check <model> <population>` exits with:

| Exit code | `outcome` | Meaning |
|---|---|---|
| **0** | `accepted` | Pass — no alethic failures, no unevaluated alethic constraint, and no vacuity. Deontic `warning`s and **deontic** `unchecked` verdicts are allowed; an **alethic** `unchecked` verdict is not (see band 4). |
| **1** | `violated` | Any alethic **`fail`** — a hard constraint is violated. Takes precedence over indeterminacy and vacuity. |
| **2** | `inadequate` | Any **`vacuous`** verdict (and nothing higher) — the population is inadequate rather than violating. |
| **3** | `ill_formed` | Model or population **load / validation error** — the check never ran. |
| **4** | `indeterminate` | Any **alethic** constraint carries an **`unchecked`** verdict — the checker never mechanically evaluated a rule that *is* the acceptance contract, so acceptance cannot be claimed. An unchecked **deontic** constraint never affects the band. |

Band precedence is **3 > 1 > 4 > 2 > 0**: a definite failure is the most actionable signal, and indeterminate outranks vacuous because vacuous is a *decided* state while indeterminate means the machinery never ran. `acceptance_ready` is true **only** at exit 0.

The bands keep "constraint violated" (1), "population inadequate" (2) and "could not decide" (4) mechanically distinguishable for retry loops and eval harnesses. A caller can always tell *accepted* from *could not decide*.

Two non-band exit codes exist so that tool-level failures can never masquerade as band verdicts: **64** (EX_USAGE) for a malformed invocation (argparse usage error — previously argparse's default exit 2 collided with the vacuous band), and **70** (EX_SOFTWARE) for an internal checker error (previously an uncaught traceback's exit 1 collided with the alethic-fail band). Retry loops keying on the bands should treat 64/70 as harness errors, not model/population signals. Exit 64 deliberately emits no `--format json` payload; every band (0/1/2/3/4) and 70 do.

## Annotated example

```yaml
population:
  model: model.orm.yaml           # declarative reference; loader never opens it
  source: fixture                 # this file is an eval fixture
  label: violating                # expected outcome: the checker should find failures
  covers:                         # completeness claimed for exactly these two fact types
    - movie_has_title
    - movie_directed_by_director

instances:
  movie: [1, 2, 3]                # Movie #3 plays no facts below — a mandatory
                                  # constraint on movie roles will catch it

facts:
  movie_has_title:
    - { movie: 1, title: "The Departed" }
    - { movie: 1, title: "Also The Departed" }  # duplicate movie → uniqueness [movie] FAILS
    - { movie: 2, title: "Inception" }
  movie_directed_by_director: []  # covered but empty → constraints over it are VACUOUS
```

Checked against a model with a uniqueness UC on `movie_has_title.[movie]` (alethic) and any constraint on `movie_directed_by_director`, this file yields at least one `fail` and at least one `vacuous` verdict — exit code 1 (fail beats vacuous).

The same document as JSON loads identically:

```json
{
  "population": { "model": "model.orm.yaml", "source": "fixture", "label": "violating",
                  "covers": ["movie_has_title", "movie_directed_by_director"] },
  "instances": { "movie": [1, 2, 3] },
  "facts": {
    "movie_has_title": [
      { "movie": 1, "title": "The Departed" },
      { "movie": 1, "title": "Also The Departed" },
      { "movie": 2, "title": "Inception" }
    ],
    "movie_directed_by_director": []
  }
}
```

## What this format deliberately excludes

By decision, the population format carries **no** Phase 3+ hooks:

- **No experiment-directory fields.** Populations don't know what experiment they belong to; experiment conventions are a later-phase concern layered *around* population files, never inside them.
- **No retry metadata.** Attempt counts, loop iterations, and feedback history belong to the loop driver, not the interchange format.
- **No extractor provenance.** How an agent output was converted into a population (extraction method, confidence) is the Phase 2 extractor's concern; the population file records only `source: agent-output`.

Every field must justify its existence; a population file is data plus the minimal metadata needed to check it. If a future phase needs more, it wraps the file — it does not extend this format.


### Duration populations (v7.1)

Duration roles use JSON integers under the model's declared primitive, following
[calendar-day terms](representation-format.md#calendar-day-terms-v71).
Population format versions remain unchanged. The existing version-2 opaque
cell represents unknown Duration as it represents unknown Date; labels are
never numeric values. Extraction and document checking currently refuse a
model using this temporal fragment.


## Candidate and reference origins

A version-4 model's `reference_populations` declares disjoint fixed ownership.
Reference files use this same format and are checked for structure, typed values
and model identity. A candidate must omit every reference-owned facts key,
including empty keys. Checking uses the validated combined view; fixed rows and
instances never increase candidate fact counts or candidate admission partitions.
Repeated asserted rows retain separate local occurrence indices. Report version
12 records each asserted occurrence's candidate or reference origin; derived
rows do not become asserted reference rows. Reference sources are bound by their
exact bytes, not by the population header's declarative model path.

For explicitly selected candidate-occurrence opinions, see the [judgment contract](../../gnd-dev-session/references/judgment-contract.md).
