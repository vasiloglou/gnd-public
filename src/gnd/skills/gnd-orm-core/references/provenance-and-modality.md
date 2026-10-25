# Provenance and Modality

**The single normative statement** of GND's constraint provenance taxonomy and modality policy (D-03). Every GND skill and the `gnd` runtime defer to this document; no other file restates the policy — they link here.

Cross-references:
- Where these fields sit in the YAML → [representation-format.md](representation-format.md) (normative machine spec: [orm-meta.schema.json](orm-meta.schema.json))
- How the checker maps modality to verdicts per constraint family → [constraint-reference.md](constraint-reference.md)

## The seven-source taxonomy

Every constraint carries a `source` recording *where the claim came from*. There are exactly seven values:

| `source` | Meaning | Typical origin |
|---|---|---|
| `explicit` | The user stated it directly | A dialogue statement ("each customer has one email") |
| `sample` | Visible in a small sample population | The user's Step-1 examples; a data probe |
| `common-sense` | Matched a typed library entry | The constraint-inference library / ring matcher |
| `llm-inferred` | Proposed by the LLM from world knowledge | The bounded LLM tier of constraint inference |
| `user-supplied` | The user added the rule deliberately during review | A review-step addition |
| `imported` | Carried in verbatim from another framework's artifact | A migration from a prior planning framework's requirements document |
| `induced` | Proposed from labelled examples by an inducer, under a recorded induction block | `gnd discover`, an ILP learner, or a host's gold-answer labels |

**Everything in this document applies to ORM+ v2 operations too.** An operation, each of its preconditions, and each of its dynamic rules carry `source`, `status` and `provenance` under exactly these rules — the meta-schema references one `$defs/provenance_policy` from all of them rather than keeping a second copy. Modality is the one asymmetry, and it is stated in [Frames are never defaulted](#frames-are-never-defaulted) below.

### Required provenance block per source

Each source requires a `provenance` block of a specific shape. The meta-schema enforces the requireds; the remaining fields are recommended.

**`explicit`** — `provenance` block REQUIRED:

```yaml
provenance:
  csdp_step: 4                # which authoring step elicited it
  dialogue_turn: 12           # turn number in the conversation
  user_quote: "One email per customer, always."   # recommended — the evidence
```

**`sample`** — `rationale` AND `provenance` REQUIRED:

```yaml
provenance:
  sample_size: 5              # how many facts were observed
  observed_values: ["G", "PG", "PG-13"]   # for enumerations
  observed_range: { min: 0, max: 9999 }   # for ranges
```

Sample-derived constraints stay `proposed` until user confirmation — Halpin sample populations are deliberately too small to auto-confirm anything.

**`common-sense`** — `rationale` REQUIRED (restating the matched pattern in user-facing language):

```yaml
provenance:
  library_entry: ring-parent-of           # entry id in constraint-inference.md
  matched_pattern: "self-referential binary with parent/child role names"
  assumptions: ["Biological parenthood; not adoptive."]
```

**`llm-inferred`** — `rationale` AND `provenance.rationale_world_fact` (non-empty) REQUIRED:

```yaml
provenance:
  llm_prompt_id: returns-must-reference-delivered-orders
  rationale_world_fact: "Returns presuppose receipt; only DELIVERED orders have receipts."
```

The world-fact citation is mandatory. A proposal without it is rejected at emission time — this is the single structural defense against hallucination, and the meta-schema enforces it.

**`user-supplied`** — `provenance` block REQUIRED:

```yaml
provenance:
  added_at_step: 7d           # when in the workflow the user added this
  user_quote: "Cap it at fifty line items."      # recommended
  user_note: "Confirmed verbally during review."  # optional
```

**`imported`** — `provenance` block REQUIRED, with five fields that must all be present and non-blank, plus a sixth once confirmed:

```yaml
provenance:
  framework: gsd                                  # which framework the claim came from
  artifact: .planning/REQUIREMENTS.md             # repo-relative path within that framework
  commit: 9622e8e4c1…                             # the commit the artifact was read at
  sha256: 3f0c…                                   # that artifact's digest at that commit
  anchor: "An expense over EUR 500 needs a second approver."   # VERBATIM in those bytes
  reviewed_in: .gnd-planning/milestones/v2.0/001-adopt.md      # REQUIRED once confirmed
```

The `anchor` is the load-bearing field: it must appear **verbatim** in the artifact's bytes at that commit, so an import can always be resolved back to the sentence it came from. A blank anchor makes the import unverifiable while still looking sourced, which is strictly worse than an honest `llm-inferred` — hence `semantic:imported-provenance` (error) rejects a missing or whitespace-only value in any of the five.

`reviewed_in` names the record in which an owner accepted the import. It is required exactly when `status: confirmed`, enforced twice: the meta-schema requires the field, and `semantic:imported-confirmed-reviewed` (error) additionally rejects a present-but-blank one. The reason is the D-03 table below — confirmation is what flips an imported claim from advisory to hard-fail, and an unreviewed import may not present itself as confirmed.

**`induced`** — `provenance` block REQUIRED and **closed**: it holds exactly `induction` and, once confirmed, `reviewed_in`. **Constraints only** — an operation, precondition or dynamic rule may not carry `source: induced` (the D-12 evolve gate reads constraints only, so an induced operation would bypass review).

```yaml
provenance:
  induction:
    inducer: {name: gnd-discover, version: 0.4.0}    # who proposed it
    method: gnd-discover                              # free token; a gold-answer origin is `gold-answer`
    manifest_sha256: 3f0c…                            # the label manifest it read
    examples: [case-0001, case-0002]                  # opaque or manifest-relative ids of supporting examples
    support: {numerator: 41, denominator: 42}
    counterexamples: [case-0017]
    evidence:
      - {ref: populations/p1.json, sha256: 9a1e…}     # manifest-relative ref, digest of its bytes
    confidence: {value: 0.97, formula: "numerator / denominator"}   # optional; only for methods that define it
  reviewed_in: .gnd-planning/milestones/demo/003-review.md          # REQUIRED once confirmed
```

Bounds (fixed by the IK2 spec; changed only by owner amendment):

| Field | Bound |
|---|---|
| `inducer.name`, `inducer.version`, `method` | 1–64 characters, `^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$` |
| each example and counterexample id | 1–64 characters, `^[A-Za-z0-9][A-Za-z0-9._:#-]{0,63}$` |
| `examples` | at most 256, unique, and no more than `support.numerator` |
| `counterexamples` | at most 32, unique, no more than `denominator − numerator`, and disjoint from `examples` |
| `support` | integers, `0 ≤ numerator ≤ denominator`, `1 ≤ denominator ≤ 2^53 − 1` |
| `evidence` | 1–32 items; `ref` manifest-relative, at most 256 characters, no leading `/`, no `\`, `:`, whitespace or dot-leading segment; `sha256` 64 lowercase hex |
| `confidence` | optional `{value, formula}`; `value` finite in `[0, 1]`, `formula` 1–256 characters |
| `reviewed_in` | 1–256 characters, not whitespace-only |

**Induction evidence never persists host data.** Ids are opaque or manifest-relative and digests stand in for values; a host path or raw value is refused by the grammars above. One residual is stated rather than hidden: a raw value that is itself a single token (`alice`, `42`) cannot be told apart from an opaque id. **The block is a recorded claim.** The loader checks its shape, bounds and arithmetic (`semantic:induced-provenance`), not its truth — a model file carries no population to recompute it from. Commands that write induction blocks compute what they write and say so.

GND ships no command that re-verifies an anchor against artifact bytes; the `verify_migration.py` script bundled with the adoption skill does that at migration time. Nothing re-checks it afterwards, so an `imported` provenance block is a record of a check that was made, not a check that is continuously made.

### Source ↔ status consistency

`status` records the review state: `proposed` | `confirmed` (and `rejected`, which lives only in `rejected_proposals`). The semantic validator (`semantic:status-source`) enforces:

- `explicit` and `user-supplied` constraints are `confirmed` — the user's own words are not proposals.
- `imported` constraints may be either. An import starts `proposed` (and therefore deontic); an owner review moves it to `confirmed`, which requires `reviewed_in`.
- `induced` constraints may be either. They start `proposed` and deontic; an owner review moves them to `confirmed`, which requires a non-blank `reviewed_in` (`semantic:induced-confirmed-reviewed`).
- `common-sense` and `llm-inferred` constraints start `proposed`; they become `confirmed` only when the user accepts them, or move to `rejected_proposals` when the user rejects them.
- `sample` constraints stay `proposed` until user confirmation.

## Modality semantics

Every **active** constraint carries a `modality` — and the meta-schema **REQUIRES it, never defaulted**. The two values:

| `modality` | Meaning | Checker behavior on violation | Checker behavior when NOT evaluable |
|---|---|---|---|
| `alethic` | Hard constraint — cannot be violated in a valid population ("must") | Verdict `fail`; CLI exit code 1 | Verdict `unchecked`; CLI exit code **4 — indeterminate** |
| `deontic` | Advisory rule — may be violated; violation is noteworthy ("should") | Verdict `warning`; exit code unaffected | Verdict `unchecked`; exit code unaffected |

The checker prints alethic results in the BLOCKING section and deontic results in the ADVISORY section. Deontic constraints are feedback-only by design: they steer agents and reviewers without gating.

**Modality is what makes exit band 4 meaningful (D-07).** An alethic constraint *is* the acceptance contract, so failing to evaluate one means acceptance cannot be claimed — the run is **indeterminate** (exit 4), never accepted (exit 0). A deontic constraint is feedback-only, so failing to evaluate one cannot withhold acceptance and leaves the band unaffected. Every `unchecked` verdict carries a machine-readable `reason_code` (e.g. `textual-not-mechanical`, `family-unimplemented`, `no-reference-clock`) naming *why* it could not be evaluated.

### Permanent indeterminacy: alethic constraints in a never-checkable family (D-20)

A `textual` constraint holds a natural-language expression that GND stores as quoted data and **never** parses. It is not "unchecked for now" — it is unimplementable in principle, so no future phase decides it.

Combine that with the table above and the consequence is exact: **a model carrying an alethic `textual` constraint can never exit 0, for any population, ever.** The alethic constraint is part of the acceptance contract; the checker cannot evaluate it; so acceptance can never be mechanically claimed and every run lands on exit 4.

**This is accepted as correct, not worked around.** An unverifiable *hard* constraint genuinely does mean the population cannot be certified. Exempting `textual` from band 4 was considered and **rejected**: that is precisely the "we decided not to look, so we will call it fine" reasoning that produces false passes.

What GND does instead is move the discovery from check time to **authoring time**:

- **`semantic:textual-alethic` (severity: warning)** fires at model load for any `textual` constraint carrying `modality: alethic`. It states the consequence and names the remedy. The model still **loads**, and `gnd validate` still **exits 0** — the rule must never become an error, or every model already carrying such a constraint would be rejected outright.
- **Authoring guidance:** write `modality: deontic` on `textual` constraints **unless permanent indeterminacy is what you intend**. A deontic textual constraint still appears in the ADVISORY section and still steers agents and reviewers; it simply does not withhold acceptance for a rule nothing can verify.

Choosing alethic deliberately is legitimate — "this rule is hard, and I would rather no population be auto-accepted than have this go unverified" is a coherent position. Record it in `rationale`, and expect exit 4 on every run.

The `rejected_proposals` list is the one exception to required modality: entries there are archived proposals, not active constraints, and are schema-light.

### Frames are never defaulted

An ORM+ v2 operation carries **no modality of its own**. Modality lives on each of its obligations — every precondition, every dynamic rule, and the `frame:` block — because that is where a verdict attaches. There is no such thing as "this operation failed"; there is only "this obligation of this operation failed".

**The `frame:` block is REQUIRED and its `modality` is never defaulted**, under exactly the rule this document states for constraints and for exactly the same reason: an omitted frame would have to default to something, and whichever value were chosen, a model that never said whether an undeclared state change is a hard failure or a warning would be silently assigned an answer. An omitted `frame`, or an omitted `modality` inside one, is a layer-1 rejection at exit 3.

The frame grades **per fact type**, not per walk: a fact type touched only by alethic-framed operations has its undeclared deltas graded alethic; a fact type touched by any deontic-framed operation has them graded deontic. One deontic operation therefore cannot downgrade another operation's alethic fact types.

`semantic:op-modality-policy` (warning) extends the D-03 guard below to operation obligations: an unconfirmed `llm-inferred` or `common-sense` precondition or dynamic rule claiming `alethic` gets the same warning its constraint counterpart gets.

## The D-03 defaulting policy (authoring time)

The modality field is always *written explicitly* by whoever emits the YAML. What D-03 governs is **which value the authoring skill writes by default**, per source and status — the over-modeling defense: an inferred constraint must not silently become a hard-fail gate.

### Default modality table (source × status)

| `source` | `status: proposed` | `status: confirmed` |
|---|---|---|
| `explicit` | n/a (explicit is always confirmed) | **alethic** |
| `user-supplied` | n/a (user-supplied is always confirmed) | **alethic** |
| `sample` | **deontic** | **alethic** |
| `common-sense` | **deontic** | **alethic** |
| `llm-inferred` | **deontic** | **alethic** |
| `imported` | **deontic** | **alethic** (and `reviewed_in` is then required) |
| `induced` | **deontic** | **alethic** (and `reviewed_in` is then required) |

Reading the table:

- **`explicit` / `user-supplied` → alethic.** The user said it; the domain enforces it. Hard-fail by default.
- **`imported` → deontic until confirmed.** Another framework's document said it; that is evidence about what someone once wrote, not a decision that it gates this model. Confirmation — recorded in `reviewed_in` — is what makes it a hard rule here.
- **`induced` → deontic until confirmed.** Labelled examples supported the rule; that is evidence, not a decision. Confirmation — recorded in `reviewed_in` — may make it alethic.
- **`llm-inferred` / `common-sense` (and `sample`) → deontic until confirmed.** Inferred and library-matched constraints are advisory — feedback-only — while unconfirmed. **Confirmation flips the default**: when the user confirms the constraint at review, the authoring skill rewrites it as `alethic`.
- **The author may override the default in either direction, with a recorded rationale.** A user may confirm a common-sense constraint but keep it deontic ("true in general, but we have exceptions") or demand alethic on a proposed constraint; either way the skill records why in `rationale` (or `user_note`).

### Enforcement

Two mechanical guards keep the policy honest:

1. **The meta-schema requires `modality` on every active constraint.** An omitted modality is a validation error (exit 3), not a silent default. This is a deliberate GND divergence from the source spec, which defaulted omitted modality to alethic — exactly the failure D-03 exists to prevent, where an unreviewed `llm-inferred` guess silently becomes a hard-fail gate.
2. **The semantic validator warns on policy violations.** Rule `semantic:modality-policy` (severity: warning) fires when an **unconfirmed** (`status: proposed`) `llm-inferred`, `common-sense` or `induced` constraint carries `modality: alethic`. The model still loads — the policy is advisory at load time — but the warning is printed by `gnd validate` and rides on the loaded model's warnings channel, so no consumer can miss it.
3. **The semantic validator warns on permanent indeterminacy.** Rule `semantic:textual-alethic` (severity: warning) fires when a `textual` constraint carries `modality: alethic` — see [Permanent indeterminacy (D-20)](#permanent-indeterminacy-alethic-constraints-in-a-never-checkable-family-d-20) above. Same channel, same never-an-error posture.

## Evolve admission (D-12)

`gnd evolve` (preview, apply and finalize) admits a constraint that is new or changed relative to the current model only under these rules; an unchanged constraint keeps its complete canonical metadata. This is the one home of the lifecycle; the gnd-model-evolve evolution contract cites it.

- A new `llm-inferred` constraint is `proposed` and `deontic`.
- A new `user-supplied` constraint is `confirmed`, with modality assigned by the D-03 table.
- A new `induced` constraint is `proposed` and `deontic` and carries no `reviewed_in`. Output from discovery or an ILP import is always new, so it can never arrive already reviewed.
- An `induced` constraint becomes `confirmed` only as a **reviewed status change**: the candidate equals an existing `proposed` `induced` constraint except for `status`, `modality` and an added non-blank `provenance.reviewed_in`. Each proposed predecessor can be confirmed once. Any other change to a confirmed induced constraint returns it to `proposed`.
- `provenance.induction` is refused under every source other than `induced`.
- Every other source is refused; operation audit actor, origin and time never enter constraint provenance.

The named refusals, all exit 3:

| Refusal | When |
|---|---|
| `provenance.induction is allowed only under source induced (D-12)` | an induction block under another source |
| `new induced constraints cannot carry provenance.reviewed_in (D-12)` | a new proposed induced constraint names a review |
| `induced constraints become confirmed only as a reviewed status change of an existing proposed induced constraint (D-12)` | a confirmed induced constraint with no claimable predecessor or no review record |
| `new induced constraints must be proposed/deontic (D-12)` | any other status/modality on a new induced constraint |

An owner may still rewrite an induced rule as `user-supplied`/`confirmed` without its induction block; that drops the marker, and the reviewed status change is the path that keeps it.

## Worked examples

An explicit constraint — user's words, hard-fail:

```yaml
- type: uniqueness
  roles: [movie]
  source: explicit
  status: confirmed
  modality: alethic
  provenance:
    csdp_step: 4
    dialogue_turn: 18
    user_quote: "Each Movie has one canonical title in our catalog."
```

An unconfirmed LLM inference — advisory until the user weighs in:

```yaml
- type: subset
  subset_role_seq: [{ fact_type: return_references_order, role: order }]
  superset_role_seq: [{ fact_type: order_is_delivered, role: order }]
  source: llm-inferred
  status: proposed
  modality: deontic
  rationale: "Returns should reference orders that have been delivered."
  provenance:
    llm_prompt_id: returns-must-reference-delivered-orders
    rationale_world_fact: "Returns presuppose receipt; only DELIVERED orders have receipts."
```

The same constraint after the user confirmed it at review — the default flips:

```yaml
  source: llm-inferred
  status: confirmed
  modality: alethic
```

A confirmed constraint the user deliberately kept advisory — override with recorded rationale:

```yaml
- type: frequency
  scope: internal
  roles: [order]
  bound: { max: 50 }
  source: common-sense
  status: confirmed
  modality: deontic
  rationale: "Usually true, but bulk B2B orders legitimately exceed 50 items — keep as a warning."
  provenance:
    library_entry: count-non-negative
    matched_pattern: "role name containing 'quantity'"
    assumptions: ["Retail-scale orders"]
```
