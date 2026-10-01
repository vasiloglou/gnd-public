---
name: gnd-model-from-text
description: Builds an ORM 2 conceptual model (model.orm.yaml with full constraint provenance — explicit / sample / common-sense / llm-inferred / user-supplied, alethic vs deontic modality on every constraint) from a natural-language domain description by walking the user through Halpin's Conceptual Schema Design Procedure (CSDP), then validates the result with gnd. Use when asked to "build a conceptual model", "model this domain", "design an ORM model from a description", or to produce a model.orm.yaml for a new GND project. Not for validating an existing model (use `gnd validate`), checking populations (`gnd check`), or format/spec reference (see the gnd-orm-core skill). Not for changing a model that already exists — that is gnd-model-evolve — and not for recovering one from an existing codebase — that is gnd-model-from-code.
---

# GND Model From Text

## Summary

**What:** Conceptual Schema Design Procedure (CSDP) — a dialogue-driven workflow (Steps 0–7) that takes a natural-language domain description (with optional sample facts and user dialogue), builds an ORM 2 conceptual model with full constraint provenance, verbalizes it for stakeholder review, and validates the committed model. Output is `model.orm.yaml` + `model.verbalization.txt`.

CSDP is Halpin's canonical forward-design methodology. The user provides examples and answers questions, the skill verbalizes elementary facts back to the user for confirmation, and the model emerges step by step.

**When to use:**
- Greenfield ORM design when no schema or data exists yet (requirements documents, domain descriptions, conversations with stakeholders)
- Building a fact-based conceptual model from elementary facts and sample populations
- Producing a stakeholder-reviewable intermediate artifact (the YAML) where a domain expert validates the model by reading verbalized facts rather than diagrams
- Producing the `model.orm.yaml` a GND project derives its verifier, code, and synthetic data from

**When NOT to use:**
- Validating or checking an already-written model — `gnd validate` / `gnd check`
- Looking up the YAML format, constraint vocabulary, or modality policy — see [`../gnd-orm-core/SKILL.md`](../gnd-orm-core/SKILL.md) (references-only library)
- **Changing a model that already exists** — [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md)
- **Recovering a model from existing code or schemas** — [`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md)

**Overview:**
0. Open with mode choice — Guided (full dialogue, for unfamiliar or high-stakes domains), MVP-fast (light dialogue over one user-visible slice, the prototype default), or One-shot (user provides a rich description; skill drafts in one pass)
1. Transform familiar examples into elementary facts and verbalize back for confirmation
2. Draw the fact types and apply a population check using the user's sample facts
3. Check for entity types that should be combined; distinguish derived facts from constraints
4. Add uniqueness constraints and check the arity of each fact type
5. Add mandatory role constraints and check for logical derivations
6. Add value, set-comparison, ring, and subtyping constraints (typed library + LLM tier with opt-in spot-check)
7. Add other constraints, assign modality per the D-03 policy, commit to YAML, and validate

## Routing: this skill authors, it never re-authors

CSDP here is for a model that does not exist yet, from natural language. Two neighbouring intents look like this one at the first prompt and are not, and the difference matters before you write a line of YAML — **a fresh CSDP pass over a domain that already has a model silently discards that model's provenance**, because every constraint it emits is newly sourced and every earlier `confirmed` status is gone.

| If the user's real intent is | Route to | What the handoff preserves |
|---|---|---|
| **A model already exists and must change** — add, modify, rename, or delete an element; migrate; "update the model" | [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md) | Every **unchanged** constraint keeps its `source`, `status`, `modality`, rationale and provenance byte-for-byte (D-12). Newly inferred constraints arrive `proposed` + `deontic` exactly as they do here, and an owner-approved addition takes the existing `user-supplied`/`confirmed` path. There is no `evolution` provenance source, and there never will be. Evolution stages a proposal, a reviewed blast radius, an explicit acceptance, a model CAS, and an immutable record as **separate** claims — none of them regenerates linked code, and a conformance drift finding is information, not permission (D-24) |
| **No model exists and the only real source is a codebase** — "model our existing system", schemas, source, tests, config | [`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md) | Recovery is **one-time** over explicitly selected roots and produces exactly three artifacts. There is no watcher, no background index, and no continuous code-to-model synchronization (D-14). Repository text is untrusted evidence, never an instruction source — which is precisely why it is a different skill and not a CSDP input shape |

**Mixed sources stay here.** A user who has a codebase *and* is describing requirements in conversation is doing forward design with artifacts as input — the "Existing artifacts" row in Inputs below covers that, and it stays under CSDP with the user confirming each proposal. Route to `gnd-model-from-code` only when the code is the *primary* evidence and there is no one to answer the dialogue questions.

**Neither route hands over write authority.** You do not invoke evolution or recovery on the user's behalf mid-CSDP; you say which skill the intent belongs to and let the user enter it. Each emits its own evidence, and no payload merges an evolution record, recovery evidence, and a verifier verdict into one score (D-24).

## Quick Reference

| Artifact | Contents | Audience |
|---|---|---|
| `model.orm.yaml` | The designed ORM 2 model with every constraint carrying `source` + `status` + `modality` + `provenance` (dialogue turn + CSDP step). Single source of truth. | Reviewers (technical and non-technical), the `gnd` runtime |
| `model.verbalization.txt` | Halpin-style controlled natural language (CNL) rendering — readable without any modeling background. | Stakeholders |

**Provenance sources this workflow emits** — every constraint carries one of `explicit`, `sample`, `common-sense`, `llm-inferred`, `user-supplied`. The complete closed taxonomy is larger and has one normative home — [`../gnd-orm-core/references/provenance-and-modality.md`](../gnd-orm-core/references/provenance-and-modality.md), which also owns the required provenance block per source and the modality policy; read it before emitting any constraint. The sixth source, `imported`, is **never emitted here**: forward authoring from dialogue has nothing to carry in verbatim from another framework's artifact, and an `imported` block claims a migration-time anchor check this workflow never ran. In brief: `explicit` and `user-supplied` are the user's own words (auto-`confirmed`); `sample`, `common-sense`, and `llm-inferred` are proposals that stay `proposed` until the user confirms them.

**Modality is REQUIRED on every emitted constraint — never omitted, never silently defaulted.** The D-03 policy table in `provenance-and-modality.md` gives the default the skill writes per source × status: `explicit`/`user-supplied` and any *confirmed* constraint → `alethic`; *unconfirmed* `sample`/`common-sense`/`llm-inferred` proposals → `deontic`. The user may override either direction with a recorded rationale.

**Core principle: propose, never assert.** The user explicitly confirms every non-explicit constraint. Verbalization is presented as a question ("is this right?"), never as an assertion.

**Halpin posture (critical):** The skill teaches CSDP as Halpin meant it — atomic facts, no attributes, populate-then-constrain. Slipping into ER vocabulary (table/column/relationship type) leaks ER mental models. Use Halpin's terms: fact type, role, object type, reference scheme, objectification. See [`../gnd-orm-core/references/halpin-posture.md`](../gnd-orm-core/references/halpin-posture.md).

**Model-size guidance (prototypes):** GND targets experimental systems. For a prototype, aim for **~15 fact types or fewer** — enough to drive a verifier and synthetic data without over-modeling. Do not emit enterprise-grade constraint sets for throwaway experiments; unconfirmed inferred constraints stay `proposed` + `deontic` so they can never hard-fail a loop the user hasn't reviewed.

## Inputs and Outputs

**Inputs (any combination):**

| Input shape | Notes |
|---|---|
| **Natural-language domain description** | Primary case. The user describes the domain. May arrive in one prompt or unfold conversationally. |
| **Sample data** (small) | Forms, reports, spreadsheets, CSV exports. Used illustratively (Halpin's CSDP populates fact types with a handful of sample fact instances, not thousands). |
| **Existing artifacts** | Glossaries, requirements docs, business-rule catalogs, sample queries. |
| **Conversation** | The user answers Claude's questions throughout CSDP. The dialogue itself is part of the input. |

**Outputs (always emitted as the pair):**
- `model.orm.yaml` — full canonical YAML; format spec in [`../gnd-orm-core/references/representation-format.md`](../gnd-orm-core/references/representation-format.md); machine spec [`../gnd-orm-core/references/orm-meta.schema.json`](../gnd-orm-core/references/orm-meta.schema.json).
- `model.verbalization.txt` — CNL rendering; patterns in [`../gnd-orm-core/references/verbalization-patterns.md`](../gnd-orm-core/references/verbalization-patterns.md).

## Instructions

**Required references:** the shared spec library [`../gnd-orm-core/`](../gnd-orm-core/SKILL.md) holds the YAML format spec, per-constraint vocabulary, constraint-inference library, verbalization patterns, Halpin posture, and the normative provenance/modality policy. This skill links to those files and never duplicates their text.

**Halpin posture:** read [`../gnd-orm-core/references/halpin-posture.md`](../gnd-orm-core/references/halpin-posture.md) before running CSDP for the first time. The procedure is mechanical; the posture isn't.

**Working principle:** propose, never assert. Every constraint that isn't directly stated by the user is a *candidate* validated in conversation.

### Step 0 — Interaction-mode opener

Before eliciting examples, ask the user:

> *I can run CSDP in three modes:*
> - *Guided — we walk through Halpin's seven steps in conversation. I ask for examples, verbalize facts back to you, propose constraints, and we commit step by step. Best for regulated, unfamiliar, or high-blast-radius domains.*
> - *MVP-fast — same steps, batched: we model only the slice you're building now, I confirm facts in batches at step boundaries instead of one at a time, and you get one compact review at the end. Best for prototypes and MVP slices.*
> - *One-shot — you give me a detailed domain description up front; I produce a draft model in one pass; you review by editing the YAML. Caveat: text-first One-shot is significantly degraded, because there's no structured source to anchor the model. Best for fast retargeting when you already have a rich description.*
> *Which would you prefer?*

If no answer: default to **MVP-fast** when the stated goal is a prototype or an MVP slice, and to **Guided** otherwise. Record the choice in `source.mode` of the YAML.

In Guided mode CSDP pauses at three pivot points (Step 0 itself, Step 6d's LLM spot-check, Step 7's six substeps). In One-shot mode those pauses collapse — library-tier proposals auto-confirm; LLM-tier proposals stay `proposed` (and therefore `deontic`) for the user to review by editing the YAML.

**MVP-fast mode** keeps the dialogue and drops the ceremony:

- **Scope:** model only the user-visible slice being built now — the ~15-fact-type
  prototype guidance above is the ceiling, not the target. Uncertain or deferred
  domain behavior stays **visibly open**: name it in the final report, and where
  it surfaced as a constraint, leave that constraint `proposed` + `deontic`
  rather than resolving it by guess.
- **Confirmation:** batch Step 1–5 confirmations at step boundaries (one
  question listing the step's facts and constraints) instead of per fact.
  "Propose, never assert" still holds — a batch the user has not answered is
  not confirmed.
- **Inference:** skip Step 6's common-sense and LLM tiers (6a–6d) unless the
  user asks for them; emit only constraints grounded in the user's own words
  and samples.
- **Review:** one compact Step 7 pass — the whole-model verbalization with
  confirm/reject/add handled in a single exchange (7a–7e batched).
- **Validation:** unchanged and still mandatory. The gate below runs exactly
  as in every mode.

### Step 1 — Elementary facts and verbalization check

Get the user to provide concrete examples. Ask:

> *"Show me a typical case. Walk me through what a real instance looks like — a sample form, a row from a report, or just describe one concrete thing in your domain."*

For each example, verbalize it as **elementary facts** (atomic, irreducible, no compound predicates). Present each fact back to the user with explicit phrasing:

> *"From your example, I'm reading: 'John was born in Australia.' Is that an atomic fact in your domain, or is there more going on?"*

The user confirms, refines, or rejects each fact. Critical: never proceed past a fact the user hasn't explicitly confirmed.

Reference-scheme elicitation lives here too. For each entity type that emerges, ask:

> *"How is each {EntityType} identified — by name, by number, by a code?"*

Avoid attribute-thinking. The user might say "by the customer's name" — push to make this a separate reference-scheme decision: is the name a popular reference mode (e.g., `Customer(.name)`), or do customers have their own identifier?

See [`references/dialogue-patterns.md`](references/dialogue-patterns.md) for question templates that elicit examples, reference schemes, and push back on attribute thinking.

### Step 2 — Draw the fact types and apply a population check

From the elementary facts confirmed at Step 1, identify object types and predicates. Populate each fact type with the user's sample fact instances to validate the structure.

Output: `object_types` and `fact_types` sections of the YAML, populated with provenance pointing back to dialogue turns:

```yaml
fact_types:
  - id: person_born_in_country
    reading: "{Person} was born in {Country}"
    roles: [{ object_type: person, role_name: person }, { object_type: country, role_name: country }]
    sample_population:
      - { person: "John", country: "Australia" }
      - { person: "Mary", country: "Greece" }
    provenance:
      csdp_step: 1
      dialogue_turn: 4
      user_quote: "John was born in Australia, Mary was born in Greece."
```

The `sample_population` lets the user double-check the fact-type shape against their examples. **Every value type a role names must be declared in `object_types`** — the semantic validator rejects roles that reference undeclared object types.

### Step 3 — Combine entity types; choose derivation or constraint

Walk the model looking for entity types that should be merged (often surface as separate names for the same kind of thing) and facts that are computed from others.

Prompts:
- *"You mentioned 'Customer' and 'Buyer'. Are these the same kind of thing, or do they play different roles?"*
- *"Does this rule compute which facts belong to a fact type, or judge whether a population obeys an obligation?"*

A derivation computes the expected **extension of one fact type** from other fact
types. A constraint judges a population; it does not manufacture the facts it
requires. Make that authoring decision before choosing YAML. For a relational
rule that the structured grammar can express, mark the fact type
`derivation: derived`, `storage: computed`, and author the structured
`derivation_rule`. Route its grammar, validation, and exact-extension semantics
to the ORM-core `representation-format.md` reference already named under
Required references; do not restate or improvise them here.

Arithmetic and aggregation are not expressible by the current structured arm.
The legacy string arm still loads for compatibility, but GND never interprets
or checks it; label such a rule explicitly **legacy/opaque/unchecked**, never as
an executable formula. The detailed Step 3 reference contains a valid
structured relational example instead.

### Step 4 — Uniqueness constraints + check arity

For each fact type, ask: which combinations of roles can repeat, and which are unique? Verbalize the population check:

> *"In your example data, each Person was born in exactly one Country — never two. Is that always true, or could a Person have been born in multiple Countries?"*

Confirmed uniqueness becomes a `uniqueness` constraint. Verify arity — is the fact type over- or under-decomposed? Constraint YAML forms per family: [`../gnd-orm-core/references/constraint-reference.md`](../gnd-orm-core/references/constraint-reference.md).

### Step 5 — Mandatory role constraints + logical derivations

For each role, ask: must every instance of the object type play that role at least once?

> *"Is it required that every Person has a Country of birth, or could a Person exist in your model without one?"*

Confirmed mandatory → `mandatory` constraint. Logical derivations (one fact implies another) get flagged here too.

### Step 6 — Value, set-comparison, ring, and subtyping constraints

This is where the constraint-inference layer applies:

> **6a.** Typed library lookup keyed on object-type names and primitives. Library lives in [`../gnd-orm-core/references/constraint-inference.md`](../gnd-orm-core/references/constraint-inference.md). Library hit examples: `Money` → non-negative range; `Date` → valid-date; `email` → uniqueness + format; pair `start_date`/`end_date` → `start <= end`. Each emitted with `source: common-sense, status: proposed, modality: deontic`, surfacing the library entry id in provenance.
>
> **6b.** Ring-pattern matching on self-referential binary fact types (`parent-of` → acyclic + asymmetric + irreflexive; `married-to` → symmetric + irreflexive; `reports-to` → acyclic + asymmetric + irreflexive). Multi-variant policy: one `ring` entry per variant.
>
> **6c.** LLM tier — for object types/relationships the library doesn't cover, propose constraints from world knowledge. Each proposal must include `provenance.rationale_world_fact`. Without it, the proposal is rejected at emission (the meta-schema enforces this).
>
> **6d.** **LLM spot-check** (Guided mode only; opt-in). Surface Step 6c LLM-tier proposals to the user with their rationales — not library or ring proposals (those are deterministic; the user reviews them at Step 7b in context). The user can mark obvious hallucinations as `rejected` immediately so they don't pollute Step 7's whole-model verbalization. The user can also defer all decisions to Step 7b.
>
> **6e.** Verbalize all surviving Step 6 proposals back to the user as part of preparation for the whole-model verbalization in Step 7. Templates: [`../gnd-orm-core/references/verbalization-patterns.md`](../gnd-orm-core/references/verbalization-patterns.md).

Subtyping: ask the user only when their examples suggest distinct kinds with distinct roles. Push back on premature subtyping. A subtype is justified only when its instances play roles the supertype doesn't.

### Step 6f — Operations (ORM+ v2, optional)

When the domain has **actions with side effects** — submit, approve, record,
retire — offer to model them as v2 `operations` before final review. Skip
freely for a static domain; a model with no operations is a complete v1-shaped
model and nothing downstream requires them.

For each action the user names, elicit in their words: what it is called, what
it needs (parameters), what must already hold (preconditions — conjunctive
positive atoms only; negations and comparisons stay advisory `textual`
constraints), what it changes (effects: create / assert / retract, applied as
a set), and **whether an undeclared side effect is a hard failure or a
warning** — that answer is the `frame:` block's `modality`, and it is
REQUIRED, never defaulted: an unasked frame question is a layer-1 rejection at
validate time, not a default. Dynamic rules (old-versus-new comparisons like
"the status must change") are offered where a fact type is functional.
Provenance carries `csdp_step: 6` with the user's quote, like every other
elicited element; the format's one home is
[`../gnd-orm-core/references/representation-format.md`](../gnd-orm-core/references/representation-format.md).

In One-shot mode this substep runs only when the source text names actions
explicitly; inferred operations are never emitted — an operation is a
commitment about side effects, and guessing one fabricates a contract the
user never stated.

### Step 7 — Final review, modality, commit, validate

Six review substeps, then emission:

> **7a.** User reviews the whole-model verbalization (the Halpin-style CNL rendering of every fact type + every constraint + every proposed inference).
> **7b.** User confirms / rejects / escalates each proposed constraint accumulated through Steps 1–6. Library-tier and ring-pattern proposals are reviewed in context here (they weren't surfaced at 6d).
> **7c.** User addresses any flagged ambiguities (over-decomposition, weird subtypes, awkward readings).
> **7d.** User adds any constraints they know but the system missed (`source: user-supplied`, auto `status: confirmed`). Free-form natural-language input; the skill paraphrases back to the structured form for confirmation.
> **7e.** Assign modality. **Every constraint is written with an explicit `modality` — the D-03 policy table in [`../gnd-orm-core/references/provenance-and-modality.md`](../gnd-orm-core/references/provenance-and-modality.md) gives the default per source × status** (confirmed → `alethic`; unconfirmed `sample`/`common-sense`/`llm-inferred` proposals → `deontic`). Ask the user about each confirmed non-explicit constraint; record any override rationale.
> **7f.** Commit confirmed + user-supplied (and surviving `proposed` constraints, deontic) to `model.orm.yaml`; emit `model.verbalization.txt`. Rejected proposals go to `rejected_proposals` (with `status: rejected`) so future runs on the same domain don't re-propose them.
>
> **Validate before finishing (mandatory):** run `gnd validate model.orm.yaml` (two-layer: meta-schema + semantic rules). If `gnd` is not installed, fall back to the skill-bundled zero-install validator: resolve `<skill-dir>` to this skill's own directory and run `uv run <skill-dir>/scripts/validate_model.py model.orm.yaml`. The fallback does layer-1 structural validation only — its header states in full what it cannot check. The skill is not done until validation exits 0, **and the completion claim must name which validator ran and which layers it covered**. A fallback exit 0 is a layer-1 structural claim only — report it as "layer-1 structural validation passed; semantic layer unchecked (`gnd` unavailable)", never as the bare "validation exited 0", and carry the same limitation into any record. Drafting is not blocked by a missing `gnd`; overclaiming is. Fix reported issues and re-validate rather than hand the user an invalid model.

In One-shot mode, 7a–7e collapse: library-tier auto-confirms (→ `alethic`); LLM-tier and sample-tier stay `proposed` (→ `deontic` per D-03); explicit-source constraints are `confirmed` + `alethic`. In MVP-fast mode, 7a–7e run as one compact exchange, and anything left unresolved stays `proposed` + `deontic` and is named as open in the report. Every constraint still carries an explicit `modality` — there is no silent default. The validation gate still runs in every mode.

## Constraint Provenance and Validation Flow

Every constraint carries:

```yaml
- type: <constraint-type>
  # constraint-specific fields …
  source: explicit | sample | common-sense | llm-inferred | user-supplied   # set once
  status: proposed | confirmed                                              # evolves through review; rejected lives only in rejected_proposals
  modality: alethic | deontic                                               # REQUIRED — assigned per the D-03 policy
  rationale: "…"                                                            # required for non-explicit sources
  provenance:
    csdp_step: <N>
    dialogue_turn: <N>
    user_quote: "…"                                                         # the user's actual words (when applicable)
    # … plus source-specific fields (library_entry, rationale_world_fact, etc.)
```

The `csdp_step + dialogue_turn + user_quote` triple makes the YAML auditable in **dialogue terms**. A reviewer can trace each constraint back to where the user said something specific. The full rules — required provenance shape per source, status/source consistency, and the modality policy — are normative in [`../gnd-orm-core/references/provenance-and-modality.md`](../gnd-orm-core/references/provenance-and-modality.md).

## Common Pitfalls

| Mistake | Cause | Fix |
|---|---|---|
| Verbalizing a fact the user hasn't confirmed, then proceeding as if it were confirmed | Forgetting the "propose, never assert" principle | Phrase every Step-1 verbalization as a question. Wait for explicit user confirmation. |
| Asserting an inferred constraint as `confirmed` without Step 7b review | Skipping the confirmation flow in Guided mode, or assuming One-shot auto-confirms LLM-tier | LLM-tier proposals stay `proposed` always until user review. Library-tier auto-confirms only in One-shot mode. |
| Emitting a constraint without `modality` | Treating modality as optional | The meta-schema rejects it (validation exit 3). Assign per the D-03 table — no silent defaults. |
| Marking an unconfirmed inferred constraint `alethic` | Over-modeling; ignoring D-03 | Unconfirmed `sample`/`common-sense`/`llm-inferred` → `deontic`. The semantic validator warns (`semantic:modality-policy`) if you don't. |
| Letting users describe in ER terms ("tables", "columns") without redirecting | Easier to follow the user's vocabulary than to push back | Translate gently: "you said 'columns' — in ORM we'd call those the roles or the values. Let me re-verbalize..." |
| Accepting a subtype based on attribute differences only | Confusing roles with attributes | At Step 6 subtype check, ask: "Does {Subtype} play any roles {Supertype} doesn't?" If no → not a subtype. |
| Auto-confirming sample-derived constraints | Halpin samples are tiny (5–20 facts) | Text-first samples always stay `proposed` (+ `deontic`). User explicitly confirms at Step 7b. |
| Roles referencing undeclared value types (`string`, `date`, …) | Treating primitives as implicitly available | Declare every value type in `object_types` with its `primitive`; the semantic validator rejects undeclared role targets. |
| Building an enterprise-grade model for a prototype | Running CSDP exhaustively regardless of stakes | ~15 fact types is plenty for a prototype; stop when the model covers the loop you're building. |
| Asking the user to volunteer constraints at Step 6c (before they've seen the whole model) | Conflating Step 6c's LLM tier with Step 7d's user-supplied path | Step 7d is when the user adds constraints. At Step 6 they only confirm/reject what the skill proposes. |

## Examples

| Pattern | Files |
|---|---|
| Canonical small build covering elementary facts, reference schemes, uniqueness, mandatory, value constraints | [`examples/movie_catalog.dialogue.md`](examples/movie_catalog.dialogue.md) + [`.orm.yaml`](examples/movie_catalog.orm.yaml) |
| Subtyping done right vs wrong — push-back on premature subtyping | [`examples/library_with_subtypes.dialogue.md`](examples/library_with_subtypes.dialogue.md) + [`.orm.yaml`](examples/library_with_subtypes.orm.yaml) |
| When to objectify a fact type | [`examples/objectification_in_enrollment.dialogue.md`](examples/objectification_in_enrollment.dialogue.md) + [`.orm.yaml`](examples/objectification_in_enrollment.orm.yaml) |
| Reference-scheme elicitation — the most-skipped CSDP step | [`examples/reference_scheme_elicitation.dialogue.md`](examples/reference_scheme_elicitation.dialogue.md) + [`.orm.yaml`](examples/reference_scheme_elicitation.orm.yaml) |

## Reference files

| File | When to load |
|---|---|
| [`references/csdp-workflow.md`](references/csdp-workflow.md) | Detailed mechanics for any CSDP step — substeps, prompts, edge cases. Load when a step's summary above isn't enough. |
| [`references/dialogue-patterns.md`](references/dialogue-patterns.md) | Conversational patterns — eliciting examples, asking for reference schemes, handling thin answers, pushing back on premature subtyping. Load at Steps 1 / 3 / 6 (subtype check) / 7d. |
| [`../gnd-orm-core/references/halpin-posture.md`](../gnd-orm-core/references/halpin-posture.md) | The underlying mindset — atomic facts, no attributes, populate-then-constrain. Load before running CSDP for the first time. |
| [`../gnd-orm-core/references/representation-format.md`](../gnd-orm-core/references/representation-format.md) | The `model.orm.yaml` spec (structure, placement, two-layer validation). Load at Steps 2 and 7f. |
| [`../gnd-orm-core/references/constraint-reference.md`](../gnd-orm-core/references/constraint-reference.md) | Per-constraint vocabulary — YAML form + CNL template + checkability per family. Load at Steps 4–6. |
| [`../gnd-orm-core/references/constraint-inference.md`](../gnd-orm-core/references/constraint-inference.md) | Typed library + ring matcher + LLM proposal contract. Load at Step 6. |
| [`../gnd-orm-core/references/verbalization-patterns.md`](../gnd-orm-core/references/verbalization-patterns.md) | CNL templates including text-first additions (dialogue turns, sample facts, user quotes). Load at Steps 6e and 7a. |
| [`../gnd-orm-core/references/provenance-and-modality.md`](../gnd-orm-core/references/provenance-and-modality.md) | **Normative** six-source taxonomy + D-03 modality policy. Load before emitting any constraint. |
| [`scripts/validate_model.py`](scripts/validate_model.py) | Zero-install fallback for when `gnd` is not installed — layer-1 structural validation only. Resolve `<skill-dir>` to this skill's own directory and run `uv run <skill-dir>/scripts/validate_model.py model.orm.yaml`. Prefer `gnd validate`, which also runs the semantic layer. |

## Record and commit

Routine fast-lane prototype modeling needs no station record. When this run is evidence-lane work -- a model publication worth milestone evidence -- after validation exits 0, append the milestone record `NNN-model.md` and commit `feat(model): ...` with the validation exit verbatim, staging by explicit path `model.orm.yaml`, `model.verbalization.txt`, and the record, only on the user's explicit go-ahead. The record names which validator ran -- a fallback pass is recorded as layer-1-only, per Step 7f. The lane rule, record shape, staging discipline, and commit grammar have one home: [`../gnd-orm-core/references/milestone-record-format.md`](../gnd-orm-core/references/milestone-record-format.md). If `.gnd-planning/` is absent, offer [`../gnd-new-project/SKILL.md`](../gnd-new-project/SKILL.md) first. The record and the commit are the driving agent's acts; `gnd` itself never reads or writes `.gnd-planning/` and never touches git.

---
*Adapted from the rai-agent-skills ORM skills (branch an-orm-skill).*


## Calendar-day fragment (v7.1)

Follow [calendar-day terms](../gnd-orm-core/references/representation-format.md#calendar-day-terms-v71) for model version 3, Duration roles, tagged literals and guarded date functions.
Preserve declared typing and provenance. For recovery/adoption, retain ambiguous calendar evidence for owner review. Validation and ordinary checks/transitions support this fragment; consult that reference before choosing a downstream consumer.


## Fixed reference populations

When the owner supplies fixed catalogs, author version-4 `reference_populations` with explicit disjoint base-fact ownership and exact raw hashes. Candidate facts omit owned types.

The shared format is [version-4 reference populations](../gnd-orm-core/references/representation-format.md#fixed-reference-populations-version-4).

Repair ownership is separate from domain rules: optional constraint `owner` and
`allowed_fixes` annotations follow [representation-format.md](../gnd-orm-core/references/representation-format.md#repair-annotations).
Ask which party can repair a finding without changing its mechanical meaning;
annotations never authorize automatic fixes.
