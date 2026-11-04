# Model growth guardrails

r3, 2026-11-03. **Approved by the owner `(a1)`** ([gate record](../001-plan-gate.md)).
Milestone: `model-growth-guardrails`.
Sources: [issue #72](https://github.com/vasiloglou/gnd-public/issues/72) (GR-T9),
[#74](https://github.com/vasiloglou/gnd-public/issues/74) (GR-T11),
[#75](https://github.com/vasiloglou/gnd-public/issues/75) (GR-T12),
[#76](https://github.com/vasiloglou/gnd-public/issues/76) (GR-T13),
[#78](https://github.com/vasiloglou/gnd-public/issues/78) (GR-T15), and the
owner's direction of 2026-11-03 to plan these five as one milestone and
[#73](https://github.com/vasiloglou/gnd-public/issues/73) and
[#77](https://github.com/vasiloglou/gnd-public/issues/77) as a successor
([composition-and-type-induction](../../composition-and-type-induction/notes/composition-and-type-induction-plan.md)).
Inspection baseline: `1446f90` (main after PR #79).
Plan authorship is not approval. No phase has a spec approval; no code is
written.

**Revision history and owner rulings.**

- **r1:** first draft. Reviewed in plan review round 1 (four local readers) as
  SHA-256 `32a851f0e7e935e149b14b3999e7ba303a3c770ed72d90c9a76169451681759c`
  (MG1 spec `d44bf94e68556bc4095d3291175bafb89b75f55343e27d8d40b8cafc8cd73dc6`);
  see the [round-1 disposition](plan-review-r1-disposition.md).
- **`(o1)` 2026-11-03:** asked "How should the plans be reviewed?" with the
  options "Four local readers" (offered first) and "Six-seat panel", the owner
  replied, quoted: "Four local readers". This rules MG-D1 (a) for plan review,
  and the successor's CT-D1 (a). It is provisional for the close review until
  confirmed at the plan gate. It approves no plan or spec bytes.
- **`(p1)` 2026-11-03:** asked "Apply all eight proposed rulings as r2 and run
  the confirmation round?" with the options "Yes, as proposed" (offered first)
  and "Let me change some", the owner replied, quoted: "Yes, as proposed". This
  rules the eight questions of the round-1 disposition as proposed: B (fix the
  path crash in MG1), D (optional v3 preview fields; `apply` repeats the
  policy), E (`--shape-report`), F (confirming an existing constraint is a
  strengthening), G (unattended scope and strictness), J (CT-D4 (b), in the
  successor), S (guideline digest recorded, not verified), U (CT-D9 (b'), in
  the successor). It directs r2 and one confirmation round. It approves no
  plan or spec bytes.
- **r2:** applies all round-1 themes A–W. Sites carry `(r1-X)` tags naming
  the theme. Reviewed in the confirmation round as SHA-256
  `b0294807cb4268afb188d084414e418d75ca8338960ae1283ebefdb44d7f63df` (MG1 spec
  `553724f84783b224b71bb9f9f26362f46271151f5059737c0abfdb8b782ce4cf`); see the
  [round-2 disposition](plan-review-r2-disposition.md). The self-inflicted
  ratio was 36/43, so the declared stop rule ended plan review.
- **r3:** applies round-2 themes R2-A..R2-H without another round. Sites carry
  `(r2-X)` tags. Four points are proposed for the plan gate (§10, MG-D15..D18).
  **r3 bytes carry no review opinion.**
- **`(a1)` 2026-11-03:** asked "Approve both r3 plans, with the five open
  points as proposed?", the owner replied, quoted: "Approve as proposed".
  Approved bytes: SHA-256
  `96777e9a4fcf21d4ca77689ee92f460495896fe5585c3a90e177d98f9f908aad` (before
  this tag). Rules MG-D16, D17, D18 and CT-D13 as proposed; accepts the other
  §10 proposals as written. It does not approve the MG1 spec.

## Problem and completion predicates

A downstream application grows a domain model per task, without a human in
the loop: an LLM proposes the model from document passages, extracts facts
into it, writes derivation rules over the facts, and adds to the model as new
questions need it. Each of the five requests closes a gap where that
application keeps its own copy of a check GND should own:

| Request | Gap today | Application's workaround |
|---|---|---|
| #72 | Rule text exists (`_derivation_cnl`) but not on the public API | mirrors the grammar host-side |
| #75 | `gnd evolve` publishes any add, modify, rename or delete | its own "additions only" check before preview |
| #76 | Preview does not flag a new fact type shaped like an existing one | compares role signatures itself |
| #78 | The extract bundle carries names and shapes, not what roles mean | renders its own guidelines from the model |
| #74 | `gnd-model-from-text` assumes a human confirms; the model cannot say nobody did | adapts the skill in prompts; keeps the "no human" record outside the model |

**Outcome.** Each check moves into GND, with one home, deterministic output
and the refusal and exit conventions GND already uses.

The milestone can close when:

1. `gnd.api.verbalize_rules` renders every structured rule in the corpus with
   text that the full model verbalization contains at the rule's position, and
   reports every prose rule as `unsupported`; every other fallback is shown
   unreachable through validation; `render_model_verbalization(path)` no
   longer crashes (MG1).
2. `gnd evolve preview --policy additive` refuses every cell §2.2's matrix
   marks refused and admits every cell it marks admitted. `apply` must repeat
   the same `--policy` and `--populated`, refuses when they differ from the
   preview's, and re-runs the policy on its own bytes. Without the new options,
   every preview and apply is byte-identical to `1446f90` by a recorded
   before/after table (MG2). `(r1-D, r1-F, r1-R)`
3. `gnd evolve preview --shape-report` lists, for each added fact type, the
   existing fact types with the same role-player signature, deterministically
   and without refusing; without the option the preview is unchanged (MG3).
   `(r1-E)`
4. `gnd extract --guidelines` adds a guideline artifact built only from model
   content, recorded with its digest in `artifacts.json`; without the option
   the bundle is byte-identical; the constraint-blind pin still holds (MG4).
   `(r1-S)`
5. A model declaring `source.mode: unattended` is refused by `gnd validate`
   when it breaks any rule in §2.5's matrix; every corpus model validates
   exactly as at `1446f90` by a recorded table. `gnd-model-from-text`
   documents the mode (MG5). `(r1-G)`
6. Every page and packaged skill reference naming these surfaces has a
   recorded disposition and the docs gates exit 0 (MG6).
7. Focused gates, independent diff reviews, the question sweep and a PR are
   recorded. Owner acceptance is separate.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| MG-R1: Existing digests do not move | Full model verbalizations, evolve previews, extract bundles and validation results for inputs that do not use a new option are byte-identical to `1446f90`, shown by a recorded before/after digest table in each phase's evidence `(r1-R)`. The one stated exception: inputs that crash at `1446f90` (MG1, theme B). Any other phase that cannot keep this lists the exception and stops for an owner ruling. |
| MG-R2: One home per grammar and policy | Rule text stays in `_derivation_cnl`. The additive policy is one function shared by preview and apply. The role-player signature is one helper shared by MG3 and MG4, and later by CT4. The guideline text has one generator. Docs cite these; they do not restate them. |
| MG-R3: A gate never trusts a document it can be handed | Preview records the policy for review, but `apply` takes the policy and the populated set from its own arguments, refuses when they differ from the preview's, and re-runs the policy on the bytes it publishes `(r1-D)`. Anyone can recompute `preview_sha256` (`evolve/models.py:817-819`), so a digest check alone cannot stand in for the re-run. |
| MG-R4: Advice never gates | The shape report (MG3) never changes an exit, `breaking`, the blast radius, or any digest of a preview made without `--shape-report`. Whether two readings mean the same thing stays the caller's call. |
| MG-R5: Disclosure | Every new public callable and CLI option has a row in `gnd.disclosure`'s total site table. Guideline text is model content (`value-free`); none of these phases emits population values. |
| MG-R6: Layering and query policy | New code joins existing homes in `tools/gnd_layers.json` with zero new allowances. Model reads go through `ModelIndex` (`iter_fact_types_shared`, `role_object_types`, `primitive`), so the RF6 allow-list gains no row `(r1-O)`. |
| MG-R7: Approval, evidence, anonymity | `auto=false`. Downstream applications are not named in committed artifacts; each phase record runs the anonymity scan over files added since `1446f90`. |
| MG-R8: Provenance is never overstated | No phase marks anything `confirmed` on a machine's behalf. The unattended mode (MG5) refuses such claims; the guideline (MG4) never presents a constraint as fact. |

Each phase spec binds every rule above and every rule in
`.codex/skills/process-phase/references/standing-rules.md`, by name or with a
one-sentence argument that it does not apply.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| Issues #72, #74, #75, #76, #78 | Requests, use cases, workarounds |
| Owner directions `(o1)`, `(p1)` | Rulings |
| `src/gnd/model_verbalization.py:176-226` (`_derivation_cnl`), `:117-124`, `:569-574` (fact-type line), `:27` (`__all__`) | Rule rendering (MG1) |
| `src/gnd/api.py:124` (`__all__`, approved stable order), `:775,818,862` (`exit_code`), `:817` (`failure` closure); exact pins `tests/test_public_api.py:16`, `tests/test_v61_phase2_api.py:38-39`, `tests/test_public_runtime.py:52`, `tests/test_why_not_near_misses_public.py:225` | Public surface (MG1) |
| `src/gnd/evolve/models.py:219-223` (operation kinds), `:226-282` (locators), `:545` (proposal schema 3), `:740-760` (`EvolutionPreview`; optional `accepted_blast_radius_sha256` written as `null`), `:792` (preview and proposal versions must match), `:817-819` (`preview_sha256`); `evolve/service.py:592-673` (operations gate, exit 18), `:609,629-641` (a role added to a fact type is gated only when an existing operation references it, exit 18 `(r2-B)`), `cli_service.py:618-647` (apply's retry branch, then a fresh preview compared with the reviewed one, exit 11) `(r2-A)`, `:426-437` (`_evolve_same_review_identity`), `service.py:915-916` (an element MODIFY replaces the whole element), `:1251-1367` (preview), `:1263-1267`, `:1557-1561` (both accept only the current version), `:1319-1320` (declared operations equal the candidate), `:1336-1340` (`breaking`), `:1574-1577` (apply re-runs the gate), `:1819-1821` (finalize asserts equal versions) | Additive policy and shape report (MG2, MG3) `(r1-D)` |
| `src/gnd/model_index.py:204` (`iter_fact_types_shared`), `:213` (`role_object_types`), `:264` (`supertype_closure`), `:276` (`primitive(..., variant=)`); `src/gnd/refscheme.py:97` (`reference_identity`, layer `model`) | Role-player signature (MG3, MG4) `(r1-L)` |
| `src/gnd/extract/service.py:137-172` (bundle and `artifacts.json`), `:39-87`, `:67-82` (`_artifact_index_issue` checks only required artifacts); `extract/vocabulary.py:3-17`; `tests/test_extract_vocabulary.py:65`; `codegen/emit.py:945-950,769-783`; `tests/test_fidelity_stub_gate.py:38`, `tests/test_public_legacy_codegen_pins.py:24`; `src/gnd/skills/gnd-extract/SKILL.md:41,63` | Guideline artifact (MG4) |
| `src/gnd/verbalize.py:39,58` (`DESCRIPTION_CORE_KEYS`, `description_lines`), `:22-28,125-134` (`line_text`) | Description text and escaping (MG4) |
| `src/gnd/schema/orm-meta.schema.json:26-28` (`source`, free-form), `:735-746` (`source_kind`), `:748+` (`provenance_policy`), `$defs.object_type` and `$defs.fact_type` (no `source`; `additionalProperties: false`; fact-type `sample_population` an array of objects); twin `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`, pinned by `tests/test_schema_sync.py` and others; `model/_validation.py:884` (`semantic:status-source`), `:1384-1420` (D-03, a warning, llm-inferred and common-sense only) | Unattended mode (MG5) `(r1-G, r1-L)` |
| `src/gnd/skills/gnd-model-from-text/SKILL.md:27,96,101,257,284`; `scripts/validate_model.py` (schema-only); `gnd-orm-core/references/representation-format.md:18-25,612-622` | Skill modes, `source.mode`, text provenance (MG5) |
| `src/gnd/anchors.py:49-137,218-251`; `recovery/report.py:251-314` | Span and excerpt-digest precedents (MG5) |
| `src/gnd/disclosure.py:76-134`; `tests/test_disclosure_mode.py` | Site table (MG-R5) |
| `docs/reference/python-api.md:9` ("nine functions"); `docs/release-notes.md` | Counts and notes `(r1-N)` |
| Induced-knowledge close `012-milestone-close.md` "Open questions carried forward"; why-not-near-misses close `005`; follow-up record `014` | Inherited rows (§10) `(r1-V)` |

A `gnd coverage MODEL` census counts experiment claims; it says nothing about
whether a public renderer, an evolve policy or an extract artifact exists, so
no census is run for this framework milestone.

### Obligations harvested

| ID | Obligation (source) | Kind | Owner |
|---|---|---|---|
| O1 | Public, deterministic rule rendering (#72) | requested | MG1 |
| O2 | Cover body, negation, comparisons, clauses, aggregates, head (#72) | requested | MG1-C2 |
| O3 | Report what cannot be rendered; never render partially (#72) | requested | MG1-C3 |
| O4 | Refuse rename, delete, change of existing types and roles (#75) | requested | MG2-C1 |
| O5 | Refuse a replaced reference scheme (#75) | requested | MG2-C1 |
| O6 | Refuse an added or stronger constraint on a populated fact type (#75) | requested | MG2-C1, C2 |
| O7 | Name rejected operations in the preview claim so `apply` cannot publish them (#75) | requested | MG2-C3 |
| O8 | For each proposed fact type, existing ones with same arity, role players, compatible reference modes, and their readings (#76) | requested | MG3 |
| O9 | Structural only; meaning stays the caller's (#76) | requested constraint | MG-R4 |
| O10 | Optional guideline artifact: readings, descriptions, value constraints as text, reference mode (#78) | requested | MG4; value constraints per MG-D6 |
| O11 | No constraint that would push an extractor to hide violating facts (#78) | requested constraint | MG4-C2; MG-R8 |
| O12 | Guideline digest-bound in `artifacts.json` (#78) | requested | MG4-C1 (recorded; no verifier, `(p1)` S) |
| O13 | Unattended mode: every fact and constraint cites a span (#74) | requested | MG5-C1, C2 |
| O14 | Nothing auto-confirmed; sources and `deontic` default kept (#74) | requested | MG5-C2 |
| O15 | Header records mode, absence of reviewer, source digests (#74) | requested | MG5-C1 |
| O16 | Validation refuses `confirmed` or `user-supplied` in this mode (#74) | requested | MG5-C2 |
| O17 | Existing digests unchanged | cross-cutting | MG-R1; each phase's recorded table |
| O18 | API and CLI pins, disclosure rows | cross-cutting | each phase; MG-R5 |
| O19 | Docs and release notes (`docs/compatibility.md:7-9`) | cross-cutting | each phase's reference page and Unreleased entry; MG6 |
| O20 | Description restating a constraint, undocumented (IK1 boundary) | inherited | MG4-C3; MG6 |
| O21 | A description or reading can forge a role line (IK1-Q4) | inherited `(r1-V)` | MG4-C4 |
| O22 | `apply` rewrites the model as one-line JSON, dropping comments (IK close, reader four) | inherited `(r1-V)` | MG6-C3 notes it in the how-to |
| O23 | RF1 goldens do not reproduce from a fresh capture (NM2-Q3) | inherited `(r1-V)` | each phase that changes RF1 goldens recaptures and records |
| O24 | `render_model_verbalization(path)` crashes on structured aggregates (round 1, R2-F2) | found | MG1, ruled `(p1)` B |
| O25 | Downstream anonymity | owner constraint | MG-R7 |
| O26 | Visible checkpoints before work is complete, docs early | owner preference | MG6 checkpoints |
| O27 | Reporter acceptance in its own pipeline | carried | the reporter, after merge |

## 2. Contract proposal and product behavior

Rulings are marked; everything else is proposed.

### 2.1 Rule rendering (MG1)

`gnd.api.verbalize_rules(model, *, fact_types=None) -> dict`, schema
`gnd-rule-verbalization/1`, payload key `exit_code` `(r1-K)`. One entry per
derived fact type in stable id order: `rendered` with `text` equal to
`line_text(_derivation_cnl(rule, model))`, or `unsupported` with reason
`prose-rule`. Every other fallback in the renderer is refused by validation
(measured; MG1 spec), and a `Model` passed in memory is re-validated with
`validate_model_object` first, as `_run_verbalize` does, so a mutated
in-memory model returns `exit_code` 3 instead of a partial rendering
`(r2-C)`. A malformed `fact_types` raises `TypeError`, as other `gnd.api`
functions do; a bad model or unknown id returns `exit_code` 3. API only. `render_model_verbalization(path)` is fixed to pass the loaded model
down `(p1)`. Detail: [phase-MG1-spec.md](phase-MG1-spec.md).

### 2.2 Additive policy (MG2) `(r1-D, r1-F)`

**Options.** `gnd evolve preview --policy additive [--populated FT ...]` and
`gnd evolve apply --policy additive [--populated FT ...]`. Without
`--policy`, nothing changes.

**Which operations are refused** `(r2-B)`. Rows are locator kinds
(`evolve/models.py:226-282`); columns are operation kinds. "Existing" means
present in the before-model; "populated" is defined below. **An element
MODIFY replaces the whole element** (`service.py:915-916`), embedded roles,
constraints and sample rows included, so element MODIFY cells are
**allow-lists**: admitted only when the before/after diff is confined to the
keys named; any other difference is refused.

| Locator | ADD | MODIFY | RENAME | DELETE |
|---|---|---|---|---|
| Element `object_types` | admitted (new id) | admitted iff the diff is confined to `description` and `provenance.rationale`; otherwise refused | refused | refused |
| Element `fact_types` | admitted (new id) | admitted iff the diff is confined to `provenance.rationale` (fact types have no `description`); otherwise refused, including constraints or sample rows changed inside the element | refused | refused |
| Element `operations` | as today's operations gate | pre-empted: the gate exits 18 first; no policy case | pre-empted (18) | pre-empted (18) |
| Role | refused on an existing fact type **by the policy itself** (3); today's gate refuses only fact types an existing operation references (`service.py:609,629-641`), which exit 18 first; admitted on a fact type the same proposal adds | refused | refused | refused |
| Constraint on a fact type the proposal adds, or not populated | admitted | admitted | admitted | admitted |
| Constraint on a populated fact type | refused | admitted iff it weakens or the diff is confined to `rationale`; refused otherwise, including every **strengthening** (below) and any change of type or role set | refused | admitted (removing a constraint cannot invalidate an admitted fact) |
| Constraint hosted on the model (`ConstraintLocator.host == "model"`) | as the two rows above, where it counts as populated when **any** fact type one of its `role_ref`s names is populated (MG-D17, proposed) | same | same | same |
| ModelIdentity | — | refused | — | — |

**Strengthening** (MG-D3 (a), plus `(p1)` F): a new mandatory; a new or
narrower uniqueness; a narrowed value set or range; a frequency `min` raised
or `max` lowered; `deontic`→`alethic`; and `proposed`→`confirmed` on an
existing constraint. **Weakening** is the reverse of an item on that list. A
constraint MODIFY that is neither (a type change, a different role set) is
refused on a populated fact type. MG-D5 is narrowed so that a provenance
edit is admitted only for `rationale` text; a `status` change is never
"provenance only". Policy-cell fixtures carry no operation that references
the subject, so the operations gate cannot pre-empt them.

**Populated** (MG-D4 (a)+(b)): a fact type with `sample_population` rows,
owned by a reference population, named by a supplied population artifact
locator, or named by `--populated`.

**Order.** The operations gate runs first (exit 18), then the policy. A
proposal violating both exits 18, pinned by a two-fault case.

**Verdict and exit.** One function `additive_policy_issues(before,
proposal, *, populated) -> tuple[PolicyIssue, ...]` in
`src/gnd/evolve/policy.py`. Each issue names the operation index, locator and
matrix cell. Preview with issues writes its document (for review) and exits 3,
following NM-D10's choice of 3 for a valid request refused by policy
(MG-D12).

**Version scheme** (`(p1)` D, reading (iii)). Schema 3 stays current. The
preview gains four optional fields: `policy` (`"additive"`), `populated_args`
(the sorted `--populated` ids), `populated` (the sorted effective set: the
arguments plus sample rows, reference ownership and population artifacts) and
`policy_issues` `(r2-A)`. Each is **omitted from the serialized document when
unset**, not written as `null` the way `accepted_blast_radius_sha256` is
(`fixtures/induced_knowledge/ik4-q2-preview-at-b.json:2`). The omission lives
in the preview serializer (`_serialize_wire_version`, `models.py:786`), and
the V3 reader declares the fields, so `_bindings_match`'s recomputation from
`model_dump` (`models.py:815-819`) agrees with the written bytes. A preview
made without `--policy` has the same bytes and `preview_sha256` as at
`1446f90`. No proposal, state or finalize version changes.

**Apply** `(r2-A)`. `gnd evolve apply` builds a fresh preview and refuses any
difference from the reviewed one with exit 11, before the service runs
(`cli_service.py:643-647`). The policy therefore works at two levels:

1. **CLI.** `_cmd_evolve_apply` first compares apply's `--policy` and
   `--populated` with the reviewed preview's `policy` and `populated_args`,
   before the retry branch (`:618-641`) and before the fresh/reviewed
   equality. Present in one and absent in the other, or a different argument
   set, refuses with exit 3, and the message names the option. Then the fresh
   preview is built with apply's options, and with `--shape-report` exactly
   when the reviewed preview carries `shape_matches`. A reviewed preview whose
   `policy_issues` were removed and whose digest was recomputed then differs
   from the fresh one and is refused by the existing equality (11).
2. **Service.** `EvolutionService.apply` re-runs `additive_policy_issues` on
   the before-model and proposal it is about to publish whenever the preview
   names the policy, and refuses (3) on any issue, with the message naming
   the operation index and matrix cell. On this path the re-run is the only
   guard (MG-R3).

The additive guarantee holds when the caller repeats `--policy additive` at
apply. A preview stripped of every policy field, digest recomputed, and
applied without `--policy` publishes as a policy-free preview. The reference
page and the MG6 how-to say so `(r2-A)`.

### 2.3 Duplicate-shape report (MG3) `(r1-E, r1-Q, r1-U)`

`gnd evolve preview --shape-report` adds an optional `shape_matches` field
(omitted when the option is absent, as in §2.2): for every `ADD` of a fact
type, each existing fact type, and each other fact type added by the same
proposal, whose **role-player signature** equals the new one's, with its id
and reading.

The signature is the **multiset of role-player object-type ids** `(r2-E)`.
Role order does not matter, and supertypes do not match subtypes. Equal ids
imply equal reference schemes, so #76's "compatible reference modes" is read
as **the same object types** and adds no separate test (MG-D7). Each match
reports the reference mode of its entity role players, from
`refscheme.reference_identity`, so the caller can see them. The report is
advice (MG-R4). Apply rebuilds it only to keep the fresh/reviewed equality
(§2.2) and never refuses on it.

### 2.4 Guideline artifact (MG4) `(r1-S)`

`gnd extract --guidelines` writes `<stem>.guidelines.md` and records its
SHA-256 in `artifacts.json`. Without the flag the bundle is byte-identical.
No consumer verifies the guideline digest; the claim is that it is
**recorded** (`(p1)` S).

For each fact type, the guideline gives:

- its readings;
- per role: the role name, the object type, the object type's description
  core keys (`summary`, `row`, `source`, `notes`), its reference mode, and
  the value type's primitive.

Value constraints are omitted (MG-D6 (a)). Descriptions and readings pass
through the guideline's own escaping, so no description can start a line
that parses as a role or fact-type heading. A structure test pins this (O21).
`gnd-extract/SKILL.md:41,63` is amended to name the optional fourth file.

### 2.5 Unattended mode (MG5) `(r1-G)`, ruled `(p1)` G

A model whose `source` object holds `mode: unattended` must also hold
`reviewer: none` and `documents: [{sha256, label}]` (at least one). A span is
`{document_sha256, start, end, excerpt_sha256}` naming a declared document,
with `0 ≤ start < end`. **Units** `(r2-D)`, as for anchors
(`anchors.py:209-215`): the document is the NFC normalization of its strict
UTF-8 decoding (`canonical_document_text`); `start` and `end` count its code
points; `excerpt_sha256` is the SHA-256 of the UTF-8 encoding of that slice;
`documents[].sha256` is the SHA-256 of the raw file bytes. Validation in this
mode refuses (rule ids `semantic:unattended-u1` … `-u8`):

| # | Rule | Branches, one case each |
|---|---|---|
| U1 | header incomplete | `reviewer` absent; `reviewer` not `none`; `documents` absent; `documents` empty; a `documents` entry malformed |
| U2 | any constraint or operation with `status: confirmed` | constraint; operation |
| U3 | any constraint with `source: explicit` or `user-supplied` | **subsumed** by U2 and by `semantic:status-source` (`_validation.py:884`), which apply in every mode; kept as a named rule id with no separate case `(r2-D)` |
| U4 | an element without `provenance.spans` (at least one span), whatever its provenance | object type; fact type |
| U5 | a constraint without `provenance.spans`, for **every source except `common-sense`**, which keeps `library_entry` (MG-D16, proposed) | `sample`; `llm-inferred`; `induced`; `imported`; `common-sense` without `library_entry` |
| U6 | a fact type with `sample_population` rows whose `provenance.sample_spans` (a list of `{row, span}`) does not cover every row index | no `sample_spans`; two rows with one covered |
| U7 | a bad span | undeclared document; `start ≥ end` |
| U8 | an `alethic` constraint with source `sample`, `llm-inferred`, `common-sense` or `induced` (D-03 becomes an error in this mode and extends to `sample`) | one per source |

`gnd validate --document PATH` (repeatable, optional) re-hashes every span
whose document is supplied: an excerpt digest that differs, or `end` beyond
the document, exits 3 (MG-D9). Without `mode: unattended`, validation is
unchanged. The skill gains an Unattended mode distinct from One-shot (MG-D10)
and routes to `gnd validate`, because `scripts/validate_model.py` is
schema-only.

## 3. Dependencies and artifact homes

MG1, MG2, MG4 and MG5 are independent. MG3 follows MG2: both add optional
preview fields under the same rule. MG4 uses MG3's signature helper; if MG4
runs first it creates the helper and MG3 reuses it. MG6 follows all five; its
first checkpoint needs only the approved plan. Close follows MG6. The
successor's CT4 needs MG2 and MG3 merged.

| Artifact | Home |
|---|---|
| Plan, specs, records, reviews | `.gnd-planning/milestones/model-growth-guardrails/` |
| Rule renderer | `src/gnd/model_verbalization.py`; wrapper in `src/gnd/api.py`; `src/gnd/rule-verbalization.schema.json` (MG1) |
| Additive policy | `src/gnd/evolve/policy.py` (new, lane `evolve`), called from `evolve/service.py` preview and apply; options in `commands/evolve.py` and `evolve/cli_service.py` (MG2) |
| Role-player signature | `src/gnd/refscheme.py` (layer `model`), which may import `gnd.model_index`; not `model_queries.py`, which `model_index.py:29` imports, so a helper there would create an import cycle `(r2-E)` (MG3 or MG4, whichever runs first) |
| New schema files | each one registered in `tests/support/runtime_schema_inventory.py` and `tests/test_public_built_inventory.py`, checked by `tests/test_conformance_payload.py` `(r2-H)` |
| Shape report | `src/gnd/evolve/service.py`, preview model in `evolve/models.py` (MG3) |
| Guideline generator | `src/gnd/extract/guidelines.py` (new, lane `extract`); option in `commands/extract.py`; codegen does not mirror it (MG-D11) (MG4) |
| Unattended validation | `src/gnd/model/_validation.py` (one rule family `semantic:unattended-*`); `$defs.source_span` in `src/gnd/schema/orm-meta.schema.json` **and its twin** `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json` (MG5) `(r1-L)` |
| Skill text | `src/gnd/skills/gnd-model-from-text/SKILL.md`; `gnd-orm-core/references/representation-format.md`; `gnd-extract/SKILL.md`; `gnd-model-evolve/SKILL.md` |
| Docs | each phase's reference page and Unreleased release-note entry; MG6 everything else |

## 4. Phases

### MG1: Public rule rendering (#72; about 85 source lines, 350 test lines)

Spec: [phase-MG1-spec.md](phase-MG1-spec.md), r3, **approved `(s1)` 2026-11-03**;
recorded in [002-phase-MG1.md](../002-phase-MG1.md).

- **MG1-C1:** `verbalize_rules` and `render_rule_verbalizations` as §2.1; the
  four test `__all__` pins and `tools/run_public_acceptance.py:373` updated
  (the last is stale at `1446f90`, missing `DisclosureRefused`; recorded)
  `(r2-H)`; the new schema registered in the schema inventories.
- **MG1-C1b:** an in-memory `Model` mutated through each fallback row returns
  `exit_code` 3 with no partial text `(r2-C)`.
- **MG1-C2:** corpus parity with asserted floors (118 models with rules, 301
  rules, 19 prose at `1446f90`) and a truncation mutation control `(r1-A, r1-M)`.
- **MG1-C3:** `prose-rule` case; every other fallback refused by `load_model`
  (a falsifiable mutation case each) `(r1-C)`.
- **MG1-C4:** the path-input fix; recorded before/after table (MG-R1).

### MG2: Additive policy on evolve (#75; about 260 source lines, 600 test lines)

- **MG2-C1:** one case per matrix cell not marked pre-empted, refused or
  admitted, each failing under the opposite verdict, on fixtures with no
  operation referencing the subject; a role ADD on an existing fact type in a
  model with no operations (3); a two-fault case pins exit 18 before 3
  `(r2-B)`.
- **MG2-C2:** one case per strengthening item; a weakening and a
  rationale-only edit on a populated fact type (admitted); an object-type
  description-only edit (admitted) against description plus `primitive`
  (refused); a fact-type MODIFY that adds a mandatory constraint inside the
  element on a populated fact type (refused); `objectified_as` changed
  (refused); a model-hosted constraint spanning one populated and one
  unpopulated fact type (refused under "any"); one case per populated
  source plus an unpopulated control.
- **MG2-C3** `(r2-A)`: CLI: preview with `--policy`, apply without (3, names
  the option); preview without, apply with (3); different `--populated` (3);
  a preview whose `policy_issues` were removed and digest recomputed, applied
  with matching options (11, the fresh/reviewed equality); matching options
  and no issues (0); a preview made with `--policy` and `--shape-report`
  applies (0). Service: `EvolutionService.apply` on a preview whose
  `policy_issues` were removed (3, message names the operation index and
  cell), with a mutation control that disables the re-run and applies (0).
- **MG2-C4:** recorded before/after table: every evolve fixture previewed
  and applied without the options gives identical bytes and exits.

### MG3: Duplicate-shape report (#76; about 110 source lines, 300 test lines)

- **MG3-C1:** the signature helper, with cases for role order, (A,A,B)
  against (A,B,B), a subtype that does not match its supertype, two value
  types with the same primitive that do not match `(r2-E)`, and two identical
  ADDs in one proposal (they match each other).
- **MG3-C2:** `shape_matches` with readings and reference modes, stable
  order, only under `--shape-report`.
- **MG3-C3:** with and without the option, exit, `breaking`, blast radius and
  `report_sha256` are equal (MG-R4); a `--shape-report` preview applies with
  exit 0 `(r2-A)`; a recorded before/after table shows previews without the
  option unchanged `(r2-H)`.
- **MG3-C4:** 5,000 fact types and a proposal adding 500: signature
  comparisons counted through a bucket index, ≤ 5,500 bucket probes.

### MG4: Extraction guidelines (#78; about 160 source lines, 350 test lines)

- **MG4-C1:** `--guidelines` writes the artifact and records its digest;
  without the flag, a recorded before/after table over every extract fixture
  shows identical bundles; each `_artifact_index_issue` consumer
  (`export/verification_service.py:272`, `fidelity/service.py:100`,
  `fidelity/doccheck_service.py:68`) runs on a bundle with the extra file.
- **MG4-C2:** `test_vocabulary_is_constraint_blind` passes; a new injection
  test adds one constraint of every kind, value constraints included, and
  shows the guideline bytes do not change.
- **MG4-C3:** the docs state that a description can restate a constraint and
  that the guideline repeats descriptions (O20).
- **MG4-C4:** a description holding a newline followed by a heading-shaped
  line is escaped; the structure test parses the guideline and finds exactly
  one section per fact type (O21).

### MG5: Unattended model-from-text (#74; about 200 source lines, 500 test lines, skill text)

- **MG5-C1:** `$defs.source_span` in the schema and its twin
  (`tests/test_schema_sync.py` passes; it treats the skill copy as the
  canonical one, so the edit lands there first and is copied) `(r2-H)`; the
  `source` keys of §2.5.
- **MG5-C2:** one refusing case per branch in §2.5's table, each asserting
  its `semantic:unattended-*` id and each passing when the mode is absent;
  an unattended model meeting every rule exits 0 `(r2-D)`.
- **MG5-C3:** `gnd validate --document`: a matching span (0); an excerpt
  mismatch (3); `end` past the document (3); a document not declared (3); a
  document with combining characters, so code-point and byte offsets differ
  (0 with code-point offsets, 3 with byte offsets).
- **MG5-C4:** recorded before/after table: every corpus model validates with
  identical output. Round-1 reader 4 counted 112 corpus models carrying
  `source.mode` (guided or one-shot) and 16 one-shot models carrying
  `confirmed` or `user-supplied`; the MG5 spec re-measures these as the
  table's discriminating rows.
- **MG5-C5:** the skill's Unattended section, the representation reference,
  and `EXPECTED_SKILL_FILES` if a file is added.

### MG6: Documentation

- **MG6-C1:** disposition table over every page and skill reference naming
  the API surface, evolve preview and apply, the extract bundle or
  model-from-text modes, and the function count in `python-api.md:9`.
- **MG6-C2:** checkpoint DC1 (illustrative drafts after plan approval,
  uncommitted) and DC2 (real runs after MG5), shown to the owner (O26).
- **MG6-C3:** one how-to: growing a model by additions with GND checking each
  round. It covers preview and apply with `--policy additive`, the shape
  report, extraction with guidelines, and rule read-back. It notes that
  `apply` rewrites the model as one-line JSON (O22). Registered with the docs
  runner and executed.
- **MG6-C4:** one Unreleased release-note entry for the milestone; docs gates
  exit 0.
- **MG6-C5:** one independent docs reviewer against the shipped behavior.

### Milestone close (not a feature phase)

Final parity tables, the close review (MG-D1), the question sweep, carryover
O27 to the reporter, and a PR.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1, O2, O3 | MG1-C1..C3 |
| O4, O5 | MG2-C1 |
| O6 | MG2-C1, C2 |
| O7 | MG2-C3 |
| O8 | MG3-C1, C2 |
| O9 | MG-R4; MG3-C3 |
| O10, O12 | MG4-C1 |
| O11 | MG4-C2 |
| O13, O15 | MG5-C1..C3 |
| O14, O16 | MG5-C2 |
| O17 | MG-R1; MG1-C4, MG2-C4, MG4-C1, MG5-C4 |
| O18 | each phase's pin and disclosure cases |
| O19 | each phase; MG6-C4 |
| O20 | MG4-C3 |
| O21 | MG4-C4 |
| O22 | MG6-C3 |
| O23 | each phase changing RF1 goldens |
| O24 | MG1-C4 |
| O25 | MG-R7 |
| O26 | MG6-C2 |
| O27 | close carryover |

## 5. Documentation, skill and compatibility surfaces

- New: one `gnd.api` callable and its payload schema (MG1); two evolve
  options on preview and apply, one more on preview, three optional preview
  fields (MG2, MG3); one extract option and artifact (MG4); one validate
  option, one schema `$def` in two sync-pinned files, and one skill mode (MG5).
- **Without the new options:** model verbalization, evolve previews and
  applies, extract bundles and validation are unchanged (MG-R1), by recorded
  tables. Unavoidable changes: `gnd.api.__all__` grows by one name; the
  `python-api.md` count becomes ten; root help and the RF1 CLI help goldens
  for `gnd evolve preview`, `gnd evolve apply`, `gnd extract` and `gnd
  validate` list the new options (recaptured per O23); each phase adds to one
  Unreleased release-note entry.
- Packaged skills: `gnd-model-from-text` (MG5), `gnd-model-evolve` (MG2, MG3),
  `gnd-extract` (MG4). The skill directories are installer-managed links; the
  sync-pinned copies are the schema twins named in §3.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A rule text change moves digest-bound verbalizations | MG-R1; MG1 changes no wording; recorded table |
| The additive policy is bypassed by editing or stripping the preview | MG-R3: apply takes the policy from its own arguments and re-runs it; MG2-C3 |
| Optional preview fields change old preview bytes | Omitted when unset; MG2-C4 table |
| "Strengthening" means different things to the caller and to GND | One closed list (§2.2); each item has a case |
| "Populated" is undecidable from preview's inputs | Restricted to what preview reads plus `--populated` |
| The shape report is read as "these are duplicates" | MG-R4; named `shape_matches`; docs say candidate |
| The guideline reintroduces constraint bias | MG-D6 (a); MG4-C2 injection of every kind |
| A description forges guideline structure | MG4-C4 |
| Unattended mode breaks existing models | Rules apply only under `mode: unattended`; MG5-C4 table |
| One-shot and Unattended are confused | Distinct names; the skill contrasts them |
| Spans cite documents that do not exist | U7; optional re-hash (MG5-C3) |
| RF1 goldens drift on recapture | O23: recapture and record per phase |
| Downstream names leak | MG-R7 |
| Repair rounds introduce defects | §8 stop rule; r2 bytes carry no opinion |

## 7. Out of scope

- Composing populations and anchors across documents; proposing types from a
  population (successor milestone).
- Changing any rule's wording; a CLI for rule rendering.
- Semantic duplicate detection (synonym readings, embeddings); refusing on a
  shape match; reference modes that differ but convert.
- Migrating facts between fact types; any evolve operation beyond the four
  kinds.
- Verifying the guideline digest in a consumer (`(p1)` S).
- Value constraints in the guideline (#78 asks for them; MG-D6 (a) omits them
  to keep the bundle constraint-blind; confirmed at the plan gate, MG-D18)
  `(r2-H)`.
- Spans on `common-sense` constraints in unattended mode (#74 asks for a span
  on every constraint; library knowledge has no document span, so it cites
  `library_entry`; confirmed at the plan gate, MG-D18) `(r2-D)`.
- Running `gnd-model-from-text` unattended inside GND (GND validates the
  result; the host runs the LLM).
- Publication, release, certification.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, owner gate,
implementation and focused tests, an independent diff review, a refactoring
review and a record. No code before recorded spec approval. Plan and close
review: four local readers (MG-D1, `(o1)`).

**Stop rule, declared before round 2** (`review-convergence.md`): at most one
more plan round after round 1, a confirmation round over r2 restricted to the
blocking themes A–J. Stop after it. Stop early, and apply any repairs without
another round, when the self-inflicted ratio (round-2 findings attacking text
r2 created, over all round-2 findings) exceeds one half, or when the same
seat's finding count does not fall from round 1 to round 2 while severity
falls. Work happens on a topic branch, then a PR; merge requires the owner.

## 9. Per-phase verification story `(r1-N)`

| Phase | Expected result | Focused gate |
|---|---|---|
| MG1 | Corpus parity; reasons; pins; path fix | the command in the MG1 spec §Tests (lists every file) |
| MG2 | One case per matrix cell; apply re-check; recorded parity | `uv run pytest -q tests/test_evolve_additive_policy.py tests/test_model_evolution.py tests/test_evolution_conformance.py tests/test_evolve_loading.py tests/test_evolve_references.py tests/test_public_evolution_drift_readers.py tests/test_public_evolution_legacy_readers.py tests/test_public_evolution_version_graph.py tests/test_public_legacy_evolution.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py` |
| MG3 | Signature cases; report; no gate change | MG2 gate plus `tests/test_evolve_shape_matches.py` |
| MG4 | Artifact and digest; flag-off parity; injection; structure | `uv run pytest -q tests/test_extract_guidelines.py tests/test_extract_applicable.py tests/test_extract_cli.py tests/test_extract_manifest.py tests/test_extract_projection.py tests/test_extract_vocabulary.py tests/test_public_extract_boundary.py tests/test_public_extract_controls.py tests/test_public_extraction_prose_policy.py tests/test_v51_phase2_extraction_controls.py tests/test_v51_phase2_extraction_scope.py tests/test_fidelity_stub_gate.py tests/test_public_legacy_codegen_pins.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py` plus the layering trio |
| MG5 | U1–U8; re-hash; corpus parity; schema twin | `tests/test_unattended_mode.py`, `tests/test_schema_sync.py`, `tests/test_rf1_cli_pins.py`, the layering trio, and the validation test files the MG5 spec lists by name |
| MG6 | Pages executed; checkpoints seen | `uv run python tools/run_tutorials.py`, `zensical build --strict`, `uv run python tools/check_docs.py site` |

The broad suite runs on explicit owner selection.

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Ruling or proposal |
|---|---|---|---|
| MG-D1 | Plan and close review instrument | (a) four local readers; (b) six-seat panel: needs provider credentials, slower | **Ruled `(o1)`: (a)** for plan review; close review confirmed at the plan gate |
| MG-D2 | Preview document change for MG2 and MG3 | (i) proposal v4 carrying the policy: a new proposal version through preview, apply and finalize (`models.py:792`, `service.py:1819-1821`), about +150 lines; (ii) separate preview and proposal versions: rewrites three version checks; (iii) optional v3 preview fields omitted when unset, `apply` repeats the options: about +40 lines, no version change | **Ruled `(p1)` D: (iii)** |
| MG-D3 | What counts as strengthening | (a) the closed list in §2.2; (b) any `MODIFY` of a constraint on a populated fact type: refuses harmless rationale edits | (a), with the confirm transition **ruled `(p1)` F** as strengthening |
| MG-D4 | What "populated" means | (a) sample rows, reference-owned, or named by a population artifact; (b) also `--populated`; (c) every existing fact type: refuses any new constraint on an existing type | (a)+(b) |
| MG-D5 | Description and provenance edits on existing elements | (a) admitted for `description` and provenance `rationale` text only; (b) refused as a `MODIFY`: an author could not fix a typo in a description without breaking the additive guarantee, so every documentation fix would need the policy off | (a), narrowed by `(p1)` F |
| MG-D6 | Value constraints in the guideline | (a) omit them; (b) a second flag including them, excluded from fidelity measurement; (c) include by default: breaks the constraint-blind principle (`extract/vocabulary.py:3-17`) | (a) |
| MG-D7 | Signature match rule | (a) role-order-free multiset of role-player object-type ids, no supertype matching; reference modes reported, not compared `(r2-E)`; (b) also through supertypes: a fact type over a subtype would be reported against every same-shaped fact type over each supertype, so the report grows with hierarchy depth, and a deliberately specialized fact type is always flagged | (a) |
| MG-D8 | Which elements need spans in unattended mode | **Ruled `(p1)` G:** every object type and fact type, and every sample row; `explicit` and `user-supplied` refused; D-03 an error including `sample`. **Proposed, not ruled** `(r2-D)`: spans on constraints of every source except `common-sense` (MG-D16); the `common-sense` exemption (MG-D18) | partly ruled |
| MG-D9 | Span re-hash | (a) optional `gnd validate --document`; (b) mandatory documents: validation would need them wherever the model goes | (a) |
| MG-D10 | Skill mode | (a) a new Unattended mode, One-shot unchanged; (b) change One-shot: changes current users' results | (a) |
| MG-D11 | Codegen bundle mirror | (a) codegen does not emit the guideline; (b) mirror it: more pins, no requested use | (a) |
| MG-D12 | Exit for a policy refusal | (a) 3, as NM-D10 chose for a valid request refused by policy; (b) 18: today it names one specific delta class (`exits.py:128-132`), so sharing it blurs what the code means; (c) a new code: a new band in `exits.py` and every exit table | (a) |
| MG-D13 | Path-input crash (theme B) | **Ruled `(p1)` B:** fix in MG1 | ruled |
| MG-D14 | Guideline digest | **Ruled `(p1)` S:** recorded, not verified | ruled |
| MG-D15 | `gnd discover --show-values` disclosure (successor CT4; listed here because it is the round-2 question set) | See CT-D13 in the successor plan | ruled there `(a1)` |
| MG-D16 | Spans for `induced` and `imported` constraints in unattended mode `(r2-D)` | (a) spans required for every source except `common-sense`; (b) refuse `induced` and `imported` in this mode: an unattended pipeline could not use `gnd discover` proposals; (c) leave them unspanned: contradicts #74's "every constraint cites a span" | **Ruled `(a1)`: (a)** |
| MG-D17 | When a model-hosted constraint counts as populated `(r2-B)` | (a) any fact type it names is populated: refuses a new subset constraint that could invalidate one populated side; (b) every named fact type populated: admits a constraint that invalidates admitted facts on the populated side | **Ruled `(a1)`: (a)** |
| MG-D18 | Scoping against the issues `(r2-D, r2-H)` | Confirm two departures from the issue text: #78's value constraints are left out of the guideline (MG-D6 (a)); #74's `common-sense` constraints cite `library_entry` instead of a span | **Ruled `(a1)`: both confirmed** |

| ID | Open question | Owner |
|---|---|---|
| MG1-Q1 | Reachability of the other fallbacks | **Closed in r2:** each is refused by `load_model` (MG1 spec) |
| MG1-Q2 | Root `aggregate` with `clauses` | **Closed in r2:** valid; evaluated per clause (`extensions.py:1651`); text unchanged (MG1 spec D6) |

Inherited rows `(r1-V)`: IK1 boundary (O20), IK1-Q4 (O21), IK close reader
four (O22), NM2-Q3 (O23). IKE-Q3 belongs to the successor's CT4.

## Close note `(c1)`, 2026-11-04

Appended at milestone close; the approved r3 text above is not edited.
**Delegated approval (auto=true)** under the owner's "process-milestone
model-growth-guardrails auto" (2026-11-04), which switched MG3 to the close
from `auto=false` to delegated rulings. These are agent rulings, not the
owner's reading; each repairs a premise a phase or the close review refuted.

| Site | Repair | Evidence |
|---|---|---|
| §8, MG-R7 "`auto=false`" | MG1 and MG2 ran `auto=false` with owner gates; MG3 to the close ran under the delegation above | records 004–008 |
| §2.2 matrix, constraint RENAME cells | pre-empted: proposal validation refuses a constraint RENAME (exit 3) | MG2-Q2, record 003 |
| §2.2 "Populated" for model-hosted constraints (MG-D17) | the subjects also include, for a `value` or `cardinality` constraint with `object_type` and no `role_ref` and for a `subtype-partition`, every fact type with a role played by that object type, a subtype of it or an entity it identifies | close review R1-F1, record 008 |
| §2.3 layout | one group per signature, linear in the model; same content | MG3 amendment `(d2)`, record 004 |
| §2.4 | the guideline also prints each entity's reference mode and marks derived fact types | close review R2-1, R2-5 |
| §2.5 U8 | applies to every provenance-bearing element (operations and obligations too), as D-03 does | close review R3-2 |
| §2.5 / MG-R1 | `spans` on induced provenance is admitted by the schema and refused outside the mode by U7, so no model's exit changes; no MG-R1 exception remains | close review R4-F1 |
| §4 MG5-C4 counts | 349 model files; 163 one-shot with `confirmed`/`user-supplied` | MG5 `(d1)` |
| §4 MG2-C4, MG3-C3 baseline | `d5f6e9e` stands in for `1446f90`; the evolve package is unchanged between them | record 003 |
| O22 | refuted: `apply` publishes the proposal's candidate text as given | record 007 |
| MG6-C2 | DC1 was missed; DC2 retained, owner viewing pending | record 007 |
