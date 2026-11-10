# Unattended model growth

r1.2 (rulings recorded and plan-review round 1 applied, 2026-11-07). **Approved at the plan gate, 2026-11-07** ([001-plan.md](../001-plan.md); approved bytes are r1.2 at `314dc019`, sha256 `f099eb2a…`; later edits are status wording only: this line, the status paragraph, one "Ready" sentence in UG1 and the revision history). Milestone:
`unattended-model-growth`. Phase prefix `UG`. `auto=false`.
Sources: GitHub issues 104, 74, 75, 76.
Inspection baseline: `12daa5b7` (main after PR 121), the tip this branch was
cut from.

**Status line.** The owner has ruled UG-D0 to UG-D9 (§10, "Owner ruling" column;
relayed 2026-11-07), and then approved this plan (r1.2) at the plan gate
("approved all", relayed 2026-11-07; see [001-plan.md](../001-plan.md)). That
approves the plan only, not UG1's spec or any phase's spec. UG-Q6 and UG-Q7
remain open. Plan review round 1 ran on 2026-11-07 (UG-D1 (a), four local readers) over
r1.1 (SHA-256 `b2678c57…`); its disposition is in
[plan-review-r1-disposition.md](plan-review-r1-disposition.md) and this r1.2
applies the accurate repairs. The review is advisory evidence, not approval,
and r1.2 has not itself been re-read. No phase has a spec approval. No code is written, no
issue is closed or commented on. Plan authorship is not approval or
publication authority. Anonymity: downstream applications are not named; the
issues' author is "a host pipeline" throughout.

## Finding that shapes the plan: most of the four issues is already on main

All four issues are still open, but the asks they carry were built by two
merged changes, and the plan starts from that, not from the issue titles.

| Issue | Ask (short) | On main at `12daa5b7` | Where (observed) |
|---|---|---|---|
| 74 | spans on every fact and constraint | **met**, one stated deviation: a `common-sense` constraint cites `library_entry` instead of a span (U5), spans it does carry are checked | `src/gnd/model/_unattended.py`; `representation-format.md` "Unattended source"; MG5 record `006-phase-MG5.md` |
| 74 | nothing auto-`confirmed`; sources and `deontic` default kept | **met** (U2, U3, U8; skill prose) | same |
| 74 | header records mode, no reviewer, source digests | **met** (U1: `mode`, `reviewer: none`, `documents[{sha256,label}]`) | same |
| 74 | validation rejects `confirmed` or `user-supplied` | **met** (U2 any element with `status: confirmed`, U3 constraint `source: explicit`/`user-supplied`) | same |
| 104 / 74 | a growth round adds elements citing its own new document, through `evolve`, under `--policy additive` | **open (not asked for in the issues; needed by the loop)**: the round's document must be declared in the model before the round; declaring it inside the proposal exits 3 | scratch probe described below; UG-D9 |
| 75 | `--policy additive` refuses rename, delete, change, replaced reference scheme, new or stronger constraint on a populated fact type | **met** (matrix and strengthening list) | `src/gnd/evolve/policy.py`; evolution contract "Additive policy"; `docs/reference/evolve-policy.md`; MG2 record `003-phase-MG2.md` |
| 75 | refusal names the operations, in the preview claim, so `apply` cannot publish them | **met** (`policy_issues` with operation index and cell, exit 3; apply repeats `--policy`/`--populated` and re-runs the policy on the bytes it publishes) | same |
| 76 | deterministic report of existing fact types with the same role-player signature, reference modes and readings; structural only | **met** (`--shape-report`, `shape_matches`, never changes an exit) | `src/gnd/evolve/shapes.py`; evolution contract "Shape report"; MG3 record `004-phase-MG3.md` |
| 104 | items 1 to 4: steps 3 to 7 unattended, a round and a consolidation round, the many-document checks, one reply shape | **met** by PR 106 (`97e9f4ac`): `gnd-model-from-text/references/unattended-growth.md`, guarded by `tests/test_unattended_growth_guidance.py`. Item 2's question is answered: `--policy additive` admits a new supertype and a new subtype, **not** `subtype_of` on an existing object type (`object_types.modify`) | PR 106; the reference |
| 104 | item 5, first option: propose a fact type's constraints in the round that adds it | **met** (documented) | the reference, "Constraints travel with their fact type" |
| 104 | item 5, second option: a policy admitting a new `proposed` + `deontic` constraint over a populated fact type when `gnd check` is clean | **open**. PR 106 says so and routes it to a reviewed non-additive proposal | the reference, last section; PR 106 "Not done" |

**A second gap, found while planning, in the document-by-document loop.** A
round that cites a *new* document must declare it in `source.documents`
(U1, U7). `gnd evolve` has no locator for the `source` header (the closed
locator kinds are element, role, constraint, model-identity with only
`version` and `model_id`, artifact, project), and replay equality refuses any
other top-level difference. Observed 2026-11-07 on `12daa5b7` with a scratch
probe over `tests/fixtures/unattended/conforming.orm.yaml` (not committed): a
proposal whose candidate adds one object type citing a new document **and**
appends that document to `source.documents` fails preview with
`declared operations do not equal the canonical candidate model` (exit 3);
the same element addition passes `--policy additive` with no issues when the
document was already declared in the model *before* the round, including after an earlier round was applied and finalized (second probe, service level). So today a
host must declare each document in the model file out of band before its
round, and nothing in `unattended-growth.md` or the skill says so. That edit
is not audited by `evolve`. This does not contradict the issues' text (none
asks for it), but it is what an unattended pipeline hits on document two.
Owner decision UG-D9; phase UG3.

**So issue 104 is not wholly satisfied.** Items 1 to 4 and item 5's first option
are satisfied; item 5's second option is a code change nobody has made. Issues
74, 75 and 76 read as satisfied on main. They are open because the
model-growth-guardrails close is merged (PR 83) but "owner acceptance … pending"
([009-owner-merge.md](../../model-growth-guardrails/009-owner-merge.md)); no
record closes them.

Evidence status, so "met" is not over-read: the rows above come from reading
the code, contract and docs, plus one planning-time run on `12daa5b7`:
`tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py
tests/test_unattended_mode.py tests/test_unattended_growth_guidance.py`,
**203 passed in 37.99s**. Those tests prove each mechanism alone. Nothing yet
shows the whole loop the issues describe (several documents, one round each,
validate, preview, apply, refusals along the way), and nothing yet maps each
ask to an executable result. UG1 supplies that, and is what lets the issues be
dispositioned on evidence rather than on this table.

## Problem and completion predicates

A host pipeline grows one model over many documents with no reviewer. It needs
(a) proposals that never overstate evidence, (b) rounds that never invalidate
admitted facts, (c) a warning when a proposal restates an existing shape, and
(d) a procedure that does more than elementary fact types. (a) to (d) exist
except one hole: a constraint the text only reveals after its fact type is
populated has no unattended route (item 5, second option).

The milestone is complete when:

1. **Every ask of issues 74, 75, 76 and 104 has a row in an acceptance matrix**
   (UG1 record) with a verdict `met`, `met with deviation` or `open`, and each
   `met` cites an executable result, not prose. A three-round replay through the
   shipped CLI passes, and its refusal cases exit as the contract says.
2. **Issue 104 item 5, second option, is built (owner ruling UG-D2 (b))**
   (UG2): a policy path that admits a `proposed` + `deontic` constraint
   over a populated fact type only when the supplied population is clean, with
   apply re-checking, and a case that fails it when the population violates.
3. **A growth round can declare its own document through `evolve` (UG-D9 (b)),
   and unattended validation can fail closed on spans it did not check
   (UG-D3 (c))** (UG3), with the defaults unchanged. Either way the
   current behavior is stated in one home (UG4).
4. **Documentation and the skill say the final state in one home each** (UG4),
   including how a host acts on a shape match.
5. **Each issue has a drafted, evidence-citing disposition** for the owner to
   post or close. The agent closes nothing (UG-D0).
6. Focused gates, independent reviews, refactoring reviews and records exist per
   phase; the close has its own gate. Owner acceptance is separate.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| UG-R1: Defaults do not move | Without the new option(s), every `gnd evolve preview`/`apply` result and every `gnd validate` result over the corpus is byte-identical to `12daa5b7`, **except** the single carve-out the owner's UG-D3 (c) ruling forces: a `--document` run that leaves a span unchecked may add one `warnings` entry (§2.3 (ii)); a `--document` run with every span checked, and a run without `--document`, stay byte-identical. Parity is a recorded before/after table over the evolve fixtures and the `validate --document` cases, captured with the model-growth-guardrails close scripts (`evidence/close/parity-*.json` there are the precedent). |
| UG-R2: Nothing confirms | No new path writes or admits `status: confirmed`, `source: explicit` or `source: user-supplied`. Any population-checked admission (UG2) requires `status: proposed` and `modality: deontic`, so it is advisory by construction. |
| UG-R3: Evidence licenses, a human admits | A clean population is evidence, not review. A path that admits a constraint on clean data says so in the preview and never relabels the constraint. |
| UG-R4: One walk, one home | The additive policy stays one walk over all operation kinds (`additive_policy_issues`); UG2 extends its populated cells, it does not add a parallel checker. The evolution contract "Additive policy" stays the policy's one normative home; the reference, the how-to and the docs cite it. |
| UG-R5: Digest-bound | Any population UG2 reads is bound into the preview by SHA-256 of its raw bytes; `apply` repeats the option, recomputes, and the service re-runs the check on the bytes it publishes. A different or missing population exits as the existing mismatch bands do (3 for option mismatch, 11 for a stale preview). The population is read **once**; the hashed bytes are the checked bytes (no second read); the path resolves beneath the workspace through `safefs`, a regular file, no symlink, cap applied at the read. The preview records ordinals and digests, never the operator's path. |
| UG-R6: Disclosure | No population value appears in any message, issue detail or preview field (the MG-R5 rule): digests, counts, row indices, ids from the model. The checker's own message and `offending_facts` carry entity values; they are never relayed, only counts. The per-disclosure-mode behavior of the new option (including roles declared `redact: true`, where a count is itself a yes/no oracle) is a UG2 spec obligation. |
| UG-R7: Totality and cost | Each new reader of untrusted bytes (a population file, a `--document` list) is total over arbitrary JSON/bytes with a hostile-input test, applies its cap at the read, and ships a time-bound test over the layer it adds. |
| UG-R8: Layering and query policy | New code stays in its lane in `tools/gnd_layers.json` with zero new allowances (the evolve lane importing the checker is answered by inspection: allowed with zero allowances, see UG-Q1); model reads go through `ModelIndex`; RF6 counted reads stay under their ceiling, measured in the spec. |
| UG-R9: Installer-owned links | Discovery links for any packaged-skill change come from `uv run gnd install --symlink --project --force`; never by hand (AGENTS.md). |
| UG-R10: Anonymity | No downstream application is named in any file, issue comment, PR or record. |
| UG-R11: Approval and protection | `auto=false`. Owner approval precedes implementation. Topic branch plus PR; never push to main; merge only on the owner's explicit authorization; no release, publication or certification. |

Each phase spec binds every rule above and the six standing design rules in
`.codex/skills/process-phase/references/project.md` (totality; cap bounds the
document not the algorithm; validation order pinned per boundary; one walk for
N kinds; normative prose has one home; contested representation by
measurement), by name or with a one-sentence argument.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| Issues 104, 74, 75, 76 (`gh issue view`, read 2026-11-07; no comments on any) | The asks |
| `.gnd-planning/milestones/model-growth-guardrails/` plan, records `002`–`009`, close sweep | What MG built for 74, 75, 76; deferred rows MG3-Q2, MG5-Q3 |
| PR 106, commit `97e9f4ac`; `src/gnd/skills/gnd-model-from-text/{SKILL.md,references/unattended-growth.md}`; `tests/test_unattended_growth_guidance.py` | What 104 items 1 to 4 already are |
| `src/gnd/evolve/{policy,service,shapes,cli_service}.py`, `src/gnd/commands/evolve.py`; `gnd-model-evolve/references/evolution-contract.md` "Additive policy", "Shape report"; `docs/reference/evolve-policy.md` | The policy UG2 would extend |
| `src/gnd/model/_unattended.py`; `gnd-orm-core/references/representation-format.md` "Unattended source" | The mode UG3 would harden |
| `composition-and-type-induction`, `type-induction-skills` closed milestones | Checked for overlap: they cover `gnd discover` fact-type induction and the `gnd-judge-fact-types` / `gnd-model-multivalued` skills, which judge discover evidence, not evolve proposals. No work here repeats them; see UG-D6 |
| `.codex/skills/process-phase/references/project.md`, `standing-rules.md`, `spec-note-contract.md` | Protocol |
| `tools/gnd_layers.json`, `tests/test_evolve_additive_policy.py` (helpers), `tests/test_growth_example.py`, `src/gnd/examples/growth/` | Reuse for UG1/UG2 |

Component index (searched by plan reader 3, 2026-11-07, `python3
scripts/components_index.py search`): the index is `dev/components/` and
`scripts/components_index.py` (`project.md`, last section; its "Repository
specifics" list says there is none, a contradiction recorded as UG-Q6).
Decision for reuse: **reuse** `model.population_loading` (population loading and
layer-2 validation against a model) and `check.service` / `gnd.checker.check`
(the verdict), **reject** a new population reader or a new checker. UG1 adds no
module, so `components_index.py changed --base main --strict` is vacuous there;
it is part of the UG2, UG3 and close gates. No
`gnd coverage` census is run: this is framework work, and an experiment-claim
census does not show whether an evolve policy or a skill exists.

### Obligations harvested

| ID | Obligation (source) | Kind | Status at baseline | Owner |
|---|---|---|---|---|
| O1 | Steps 3 to 7 unattended, each with a cited, `proposed`, `deontic` proposal (104-1) | requested | met (PR 106) | UG1 verifies; UG4 |
| O2 | Round and consolidation round; whether `--policy additive` admits a supertype with links (104-2) | requested | met; answer: new supertype and new subtype yes, link on existing type no | UG1 pins; UG-D7 |
| O3 | Many-document checks adapted from `rai-ontology-design` (104-3) | requested | met as prose; not machine-checkable | UG1 inspects; UG4 |
| O4 | One reply shape (104-4) | requested | met as documented shape plus a test-only translator; no schema file | UG-D5 |
| O5 | Constraints travel with their fact type (104-5, first option) | requested | met | UG1 |
| O6 | Admit a clean-population constraint over a populated fact type (104-5, second option) | requested (alternative) | **open** | UG-D2, UG2 |
| O7 | Every fact and constraint cites a span (74) | requested | met, `common-sense` deviation | UG1 |
| O8 | Nothing auto-`confirmed`; sources kept; `deontic` default (74) | requested | met | UG1 |
| O9 | Header records mode, no human, source digests (74) | requested | met | UG1 |
| O10 | Validation rejects `confirmed`/`user-supplied` (74) | requested | met | UG1 |
| O11 | `--policy additive` refusals (75) | requested | met | UG1 |
| O12 | Refusal named in the preview claim; apply cannot publish (75) | requested | met | UG1 |
| O13 | Structural duplicate-shape report, caller judges (76) | requested | met | UG1 |
| O14 | Spans over a declared document that was not supplied are not re-hashed (MG5-Q3, R3-4): an unattended gate can pass having checked nothing | inherited, deferred to the owner | open | UG-D3, UG3 |
| O15 | A proposal of only ADD/DELETE pairs fails `BlastRadiusReport` (MG3-Q2) | inherited | not owned: additive rounds contain no DELETE; recorded, not fixed here | carried |
| O16 | A subtype link has no `status`/`modality`, so it cannot be kept `proposed` (PR 106) | inherited limitation | open | UG-D4 |
| O17 | How a host acts on a shape match (76 "caller's judgment") | derived gap | `unattended-growth.md` says only "the host's" | UG4 |
| O18 | Issue dispositions are the owner's | AGENTS.md; brief | | UG-D0, UG4 |
| O19 | Later wave (73, 77, 78, 95) is out | brief | | §7 |
| O20 | A round cannot declare a new document through `evolve` (found at planning, see above); the loop needs it declared first, and no document says so | derived gap | open | UG-D9, UG3; UG1 pins the current behavior; UG4 |

## 2. Contract proposal and product behavior

The owner's decision rulings (§10) select the shapes below; the exact option
and flag names, schema impact and layering remain proposals until each phase
spec is approved. Nothing here is plan-gate or spec approval.

### 2.1 UG1: acceptance replay (no product change)

A test-only phase. A three-document replay drives the shipped CLI
(`validate --document`, `evolve preview --policy additive --shape-report`,
`evolve apply`) round by round, with the refusals each issue promises, and an
acceptance matrix that maps every row of the table above to a passing test or
an honest `open`. The phase changes no source file. A failing case is an
implementation finding, recorded and routed to the owner, not fixed inside UG1.

### 2.2 UG2: population-checked constraint admission (ruled UG-D2 (b); shape is a proposal for the UG2 spec)

Today the additive policy refuses `constraint.populated.add` and strengthening
`constraint.populated.modify` whenever any subject fact type is populated,
whether or not the population satisfies the constraint, and the policy never
sees a population (it sees `--populated` ids). Proposed shape:

- `gnd evolve preview … --policy additive --check-population PATH` (repeatable;
  `apply` takes the same option). Name provisional (UG-Q2). UG-Q3 asks first
  whether the population should instead arrive as the existing
  `population`-kind artifact locator (already digest-bound by
  `proposal_sha256`, already read by `effective_populated`), which would need
  no new option on `apply`.
- For each operation the matrix refuses with `constraint.populated.add` or
  `constraint.populated.modify` **strengthening** (a modify that changes a key
  outside the strengthening list stays refused), **and** whose constraint after
  is `status: proposed` and `modality: deontic`, the service checks the
  candidate model over the supplied population with `gnd.checker.check` and
  passes the verdict to `additive_policy_issues` (which stays free of I/O).
  **"Clean" is defined, not assumed:** the issue is cleared only when that
  constraint's own `ConstraintVerdict` is `pass`. `warning` (a deontic
  violation is a `warning`, not `fail`: `checker/_core.py`), `fail`,
  `unchecked` and `vacuous` leave the refusal, and so does a constraint the
  checker's refusal ledger declined to certify. The `gnd check` exit band is
  never used (it ignores deontic warnings). The spec decides: how an
  operation maps to its verdict (constraints have no stable id; the operation
  reference `HOST.constraints[family:new:0]` and the positional verdict ref
  must be matched, as `PolicyIssue` does by `operation_index`); what covers a
  populated subject the supplied population does not mention (refuse as
  `vacuous`, or require facts for every populated subject); whether inline
  `sample_population` rows join the checked population (the policy counts them
  as populated, `check` does not see them); and whether several files are
  checked as one composed input (two files each clean can violate in union; the
  checker has a composition path). An unreadable population exits by the
  contract's input bands (66 missing, 74 link or unreadable, 3 malformed,
  oversize or refused), and the refusal names the constraint by operation
  index and reference with a count only (UG-R6).
- Every other cell is unchanged. Rename, delete, modify of an element,
  replaced reference scheme and a non-proposed/non-deontic constraint stay
  refused; the option can only clear the two populated-constraint cells.
- The preview records the SHA-256 of each population's raw bytes by ordinal, not
  the paths (UG-R5). `apply` repeats the options, recomputes, and re-runs the
  check on the bytes it publishes, after the before-model load, in the same
  order the policy re-runs; the same option comparison sits beside the
  `--populated` comparison so the candidate-already-live retry branch is covered.
  "Belongs to the candidate model" means layer-2 validity of the population
  against the candidate (`load_population(path, model=candidate)`) plus the
  header `model_id` cross-check, which is optional and warning-only when either
  side omits it; there is no model-digest field. The spec decides whether the
  option makes `model_id` mandatory. The D-13 evolution record carries the
  population digests so it can show what an admission rested on.
- Because the admitted constraint is `proposed` + `deontic`, a later
  violating fact is a reported violation, not an uninterpretable one. The
  contract must say this plainly: the additive guarantee then holds relative to
  the supplied populations, and the constraint stays advisory.

The readings the owner did not choose (decline; own-reference-population only) are in UG-D2.

### 2.3 UG3: the unattended source header across rounds (ruled UG-D9 (b) and UG-D3 (c); shape is a proposal for the UG3 spec)

Two independent pieces, each separately ruled by the owner.

**(i) Declare a document in a round (UG-D9, ruled (b)).** A new,
append-only operation locator for `source.documents` entries
(`{sha256, label}`), admitted by `--policy additive` because it only adds a
declaration, refused when it changes or removes one (the spec defines
"modified" as a changed `sha256` or `label`, and "removed", "reordered" and
"duplicate"). The operation `StableLocator` union has four members (element,
role, constraint, model-identity); `ArtifactLocator` and `ProjectLocator` are
not operation locators. Sites a new locator touches: `StableLocator`
(`evolve/models.py`), the operation validator, `_operation_references` and
`_apply_declared_operations` replay and `_operation_target` (`service.py`),
the policy walk, the blast-radius entry builder, the contract's "Stable
locators" list, and `gnd.discover.output.candidate_document`, which calls the
same replay. Three traps found in review: `additive_policy_issues` admits any
locator kind it has no branch for (the new kind needs an explicit branch and a
fail-closed default); `BlastRadiusReport.entries` has `min_length=1`, so a
declaration-only proposal needs an entry as `model.identity` has; and
`EvolutionProposal.schema_version` is `Literal[1, 2, 3]` with closed preview
readers, so the schema-version decision is real (UG-Q5). Old proposals stay
byte-identical, but old GND readers refuse new ones, which is a
forward-incompatibility the release note must state in UG3's own deliverables. The declined reading (a) (no code; state the
out-of-band step) is kept only as UG1's pin of today's behavior and as the
documented step for any release before UG3 (i) ships.

**(ii) Fail closed on unchecked spans (UG-D3).** `gnd validate --document`
re-hashes spans only over documents that were supplied. Owner ruling: counts plus an opt-in strict flag (name provisional) that exits 3
when any span was left unchecked; the counts are spans re-hashed and spans over
declared documents that were not supplied. Plan review round 1 constrains the shape: the validate payload is
framed (`build_validate_payload` is documented as frozen; the report schema's
variants set `additionalProperties: false`, and a `counts` key already means
verdict counts), so new top-level count keys would need a report version
bump. Preferred design for the UG3 spec: counts ride as one
`unattended:spans-unchecked` entry in the existing `warnings` list, present only
when at least one span is unchecked, so a fully checked run and a run with no
`--document` stay byte-identical (the UG-R1 carve-out); with the strict flag
the same condition exits 3. If the owner's "counts always reported" cannot be met
without a report-version bump, the spec returns to the owner with that cost
rather than choosing. Counts cover element spans, constraint spans and
`sample_spans` (what `_iter_unattended_spans` yields), and the spec defines how
malformed, undeclared-document and supplied-but-undeclared spans are counted.
The strict flag with **no** `--document` at all exits 3 for an unattended model
with any span (omitting `--document` is the main hole); against a model without
the mode it is a no-op that the spec pins.

### 2.4 UG4: documentation

One home per statement. Contract text lands in the evolution contract (UG2) and
in `representation-format.md` (UG3). The reference
`unattended-growth.md` gains the final item-5 answer, the shape-match procedure
and, if UG2/UG3 ship, the commands. How-to, evolve-policy page, agents page and
release notes cite; they do not restate.

## 3. Dependencies and artifact homes

| Artifact | Home |
|---|---|
| Plan | `.gnd-planning/milestones/unattended-model-growth/notes/unattended-model-growth-plan.md` |
| Specs | `notes/phase-<ID>-spec.md` |
| Records | `NNN-plan-gate.md`, `NNN-phase-<ID>.md`, `NNN-milestone-close.md` (this repository's names, `project.md`) |
| UG1 tests | `tests/test_unattended_model_growth_acceptance.py` (new); helpers reused from `tests/test_evolve_additive_policy.py` and `tests/test_unattended_growth_guidance.py` |
| UG2 code (ruled) | `src/gnd/evolve/policy.py` (verdict input only, no I/O), `src/gnd/evolve/service.py`, `src/gnd/evolve/cli_service.py`, `src/gnd/commands/evolve.py`, `src/gnd/evolve/models.py` (`PolicyCell`, preview classes, `_POLICY_FIELDS`, `_OPTIONAL_PREVIEW_FIELDS`, so a policy-free preview keeps its digest), `src/gnd/evolve/__init__.py`, `tools/gnd_layers.json` only if a new module is created; contract in `gnd-model-evolve/references/evolution-contract.md` (which also says "evolution does not discover, open, rewrite, or regenerate the artifact", amended by UG2) |
| UG3 code (ruled) | (ii) `src/gnd/model/_unattended.py` (must stay there: it is exempt from the RF6 query scan by path and `model/` has per-file ceilings), `src/gnd/commands/checking.py`; (i) the sites listed in §2.3 |

Phase dependencies (acyclic): UG1 → UG2, UG1 → UG3, {UG1, UG2, UG3} → UG4
→ close. UG2 and UG3 are logically independent but **land serially**: each source
phase appends to the one RF6 dynamic-candidate hash chain
(`evidence/UGn/dynamic-query-successor.json` and the `DYNAMIC_SUCCESSORS` list in
`tests/support/pyrel_application_successors.py`), to `MANIFEST_SHA256` and
`goldens.sha256`, so each is rebased and re-chained on the one before. Landing
order: UG2, then UG3 (ii), then UG3 (i) unless the specs say otherwise. The
owner ruled all three in (UG-D2 (b), UG-D3 (c), UG-D9 (b)); each still needs its own approved spec, and if a spec
returns to the owner with a blocking finding, UG4 documents whatever shipped
and the unbuilt part is dispositioned openly.

## 4. Phases, deliverables, named criteria and inherited residuals

### UG1: Acceptance replay and issue disposition (test-only; about 0 source lines, 550 to 650 test lines)

Ready: needs no owner ruling beyond the plan gate (given, 2026-11-07) and the spec gate.
Deliverables: the acceptance matrix; the replay test; fixture documents;
drafted issue dispositions (text only, not posted). First draft spec:
[phase-UG1-spec.md](phase-UG1-spec.md).

Named criteria: UG1-C1 the three-round replay exits 0 at every step and the
final model validates with `--document` over all three documents; UG1-C2 each
refusal case exits as the contract says and names what it refuses; UG1-C3 the
matrix has one row per ask with an evidence reference that resolves; UG1-C4 a
case discriminates "any" from "every" populated subject for a spanning
constraint; UG1-C5 no source file changed; UG1-C6 drafted dispositions cite
the matrix and name nothing downstream; UG1-C7 the document-declaration
behavior of O20 is pinned both ways (refused when declared in the round's
candidate, admitted when declared before the round); UG1-C8 every refusal
assertion names the cell and operation index (an exit 3 alone is vacuous:
candidate-validation failures also exit 3), and a rename or delete `apply` is
driven with the preview's `blast_radius.report_sha256` on stdin because a
breaking `apply` otherwise prompts for it (exit 11 on EOF, 74 under capture, a
hang on a tty). UG1 may also pin golden proposal bytes and digests now, so
UG3's "old proposals keep their digest" has a baseline.

### UG2: Population-checked constraint admission (about 400 to 650 source lines, 800 to 1000 test lines, by the MG2 precedent of about 650 and 1016) — ruled UG-D2 (b); ready to spec after UG1

Ruled (b). UG-Q1 (layering) is answered by inspection in the spec, before any
code; the spec still needs its own owner gate. If inspection shows the lane
edge cannot be had with zero allowances, the spec returns to the owner rather than adding one.
UG2 touches, beyond §3: the RF1 goldens for `gnd evolve preview` and `apply`
(`cli-help` and `cli-exit` for each of the three interpreters 3.11, 3.13, 3.14),
`cli/tree.json`, `goldens.sha256`, `MANIFEST_SHA256` in
`tests/test_rf1_pin_harness.py`, `docs/reference/cli.md`, and the RF6
dynamic-candidate successor evidence (§3). Named criteria (proposed): UG2-C1 a
population whose constraint verdict is `pass` clears the two populated cells;
UG2-C2 each of a violating population (verdict `warning`), a population with no
rows for a subject of the constraint (`vacuous`), an `unchecked` verdict, a
population violating only a different pre-existing constraint (the spec states
the rule, then tests it) and a population of the wrong model leaves the
refusal, naming the operation index and reference with a count only; UG2-C3 a
non-proposed or non-deontic constraint, and a modify outside the strengthening
list, is not cleared; UG2-C4 apply without the option, or with the option on
only one side, exits 3; the same option with different bytes at the same path
exits 11 (the spec pins one exit per case); UG2-C5 flag-free parity (UG-R1); UG2-C6 no population value in
any output (UG-R6), shown with canary values in the population and an
exclusion list for the model-carrying preview keys, and the per-disclosure-mode
behavior is stated; UG2-C7 hostile population cases and a time-bound test that
counts operations with spies for linearity rather than a wall clock (UG-R7);
UG2-C8 layering and RF6 gates green.

### UG3: The unattended source header across rounds (about 80 to 150 source lines for (ii), about 150 to 300 for (i); about 300 to 500 test lines) — ruled UG-D3 (c) and UG-D9 (b); ready to spec after UG1

Both pieces are ruled in; they are independent and may be specced and landed
separately (UG3a = (ii) counts and flag, UG3b = (i) locator) if the spec finds
that cleaner.
UG3 (ii) also re-pins the `gnd validate` help and exit goldens, `tree.json`,
`goldens.sha256` and `MANIFEST_SHA256` (MG5 precedent). Named criteria
(proposed): (ii) UG3-C1 counts reported with documents supplied and not
supplied, with one unchecked-span case for each span location (element spans,
constraint spans, `sample_spans`); UG3-C2 the opt-in flag exits 3 on an unchecked span, including when no
`--document` is given, and 0 when all are covered; UG3-C3 flag-free parity: default output equals the `12daa5b7` baseline except the single carved-out `warnings` entry on a run that leaves a span unchecked; UG3-C4 no
document text in output (MG-R5). (i) UG3-C5 a round that appends a
declaration and adds elements citing it previews and applies under
`--policy additive` with exit 0; UG3-C6 a modified or removed declaration is
refused with a named cell; UG3-C7 a proposal without the new locator keeps its
bytes and digest, compared to golden bytes captured before the change
(UG1 pins them). The release-note entry, including the forward-incompatibility
of old readers, ships with UG3, not only UG4.

### UG4: Documentation, skill and dispositions (docs and skill prose only)

Deliverables: the final text in each home (§5), including the step "declare
the round's document in the model before the round's preview" only as the
behavior before UG3 (i) ships (the final text describes the shipped locator), release notes, the drafted
issue dispositions updated to the shipped state, docs gates. Named criteria:
UG4-C1 every statement has one home and the other pages cite it; UG4-C2 docs
gates exit 0; UG4-C3 packaged-skill pins pass (`test_packaged_skills.py`, `test_skill_prose_sync.py`; the milestone-scoped `test_ik6`/`test_il6` censuses cannot see UG changes and do not discharge this); UG4-C5 a grep finds no unqualified "keeps every fact interpretable" wording left once UG2 weakens the guarantee to "relative to the supplied populations"; UG4-C4 each
drafted disposition matches the matrix.

### Milestone close (not a feature phase)

Close record, question sweep, close review (instrument per UG-D1), close gate
(union of phase gates), parity table, PR. Owner acceptance is separate, and
issue closure is the owner's.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1–O5, O7–O13 | UG1-C1 to C3 |
| O6 | UG-D2; UG2-C1 to C8 |
| O14 | UG-D3; UG3-C1 to C4 |
| O15 | carried, not owned |
| O16 | UG-D4; UG4-C1 (stated) |
| O17 | UG4-C1 |
| O18 | UG-D0; UG1-C6, UG4-C4 |
| O20 | UG1-C7; UG-D9; UG3-C5 to C7; UG4-C1 |
| O19 | §7 |
| UG-R1 | UG2-C5, UG3-C3, close parity |

### Carried, not owned

MG3-Q2 (O15). MG-close-Q3 and Q4 and the other model-growth-guardrails sweep
rows not named above stay with the owners that close assigned.

## 5. Documentation, skill and compatibility surfaces

| Surface | Change | Phase |
|---|---|---|
| `gnd-model-evolve/references/evolution-contract.md` ("Additive policy") | UG2: the population-checked cells, normative | UG2 |
| `gnd-orm-core/references/representation-format.md` ("Unattended source") | UG3: coverage counts and flag; the declaration step | UG3 |
| `gnd-model-evolve/references/evolution-contract.md` ("Stable locators") | UG3 (i) only: a source-document locator | UG3 |
| `gnd-model-from-text/references/unattended-growth.md` | the final item-5 answer; the shape-match procedure; commands if shipped | UG4 |
| `gnd-model-from-text/SKILL.md` (Unattended mode) | pointer text only if commands ship | UG4 |
| `docs/reference/evolve-policy.md`, `docs/how-to/grow-a-model.md`, `docs/agents/model-from-text.md`, `docs/agents/evolve.md`, `gnd-model-evolve/SKILL.md` (lines restating the policy and guarantee) | cite, do not restate; today several restate the guarantee and the preview fields, and UG2 weakens that guarantee, so each is qualified or yields. Where two homes disagree the contract wins | UG4 (and UG2/UG3 for what they change) |
| `docs/reference/cli.md` | exact flag syntax, read by `test_documentation_tutorials.py` | UG2, UG3 |
| `docs/release-notes.md` | currently says the clean-population policy "remains open"; each source phase adds its entry (UG2, UG3 incl. forward-incompatibility), UG4 reconciles | UG2, UG3, UG4 |
| CLI help and RF1 goldens for `gnd evolve` / `gnd validate` | only if an option ships; re-pinned with the change stated | UG2, UG3 |
| Disclosure (`docs/reference/disclosure.md`, `tests/test_disclosure_mode.py`) | the table is keyed per command and `evolve` already sits in "emits no population values"; no row or count moves. What is added is the UG-R6 canary test and the stated per-mode behavior | UG2, UG3 |
| Packaged-skill pins (`test_packaged_skills.py`, `test_skill_prose_sync.py`, `test_ik_close.py`, `test_public_binding_prose.py`, install/doctor tests) | prose edits are free; counts move only when a packaged file or a relative link is added (PR 106 added a file). Named in the UG2 and UG3 gates so the spec measures it | UG2, UG3, UG4 |
| `AGENTS.md` skill table | unchanged: no skill is added | — |

## 6. Risks and required controls

| Risk | Control |
|---|---|
| Closing issues on a table rather than on evidence | UG1 makes every `met` an executable result; the owner closes (UG-D0) |
| A clean-today population is read as a durable guarantee | UG-R3; the contract text says the admitted constraint is `proposed`/`deontic` and advisory (§2.2) |
| Population bytes are untrusted | UG-R7: capped at the read, total over arbitrary JSON, time-bound test |
| A population for the wrong model or a stale one | UG-R5 digest binding of the bytes; the check runs against the candidate model with layer-2 validation; the header carries only an optional `model_id` (a mismatch is refused, an absence is a warning), no model digest, so the spec decides whether the option requires it |
| The evolve lane gains a checker dependency | Answered by inspection (two readers, `arch.measure`): `gnd.evolve` is layer `lanes` (rank 4), `gnd.checker` is `checking` (rank 2), the edge is downward and not wrong-way, `allow_list` stays `[]`. `policy.py` stays free of I/O; the service loads and checks and passes the verdict |
| `evolve/service.py` is 2221 lines | No test bounds `evolve/service.py`. The live constraints are the RF6 dynamic-candidate inventory (a hash chain: each source phase ships `evidence/UGn/{dynamic-,}query-successor.json` and edits `DYNAMIC_SUCCESSORS`) and the per-file ceilings on `model/` and `checker/` (`checker/_core.py` has about 13 lines of headroom): UG2 must not need a checker-core change, UG3 (ii) stays in `model/_unattended.py`. New logic lives beside `policy.py` |
| A new option moves RF1 goldens in unrelated commands | Only the two touched leaves are re-pinned; MG3-Q1 says a fresh RF1 capture drifts about 60 unrelated goldens, so each phase takes only its own |
| Disclosure leak through a violation message or a count | UG-R6; a canary-value test; the per-mode behavior (a count over a `redact: true` role is a yes/no oracle) is a UG2 spec obligation |
| Drifting normative prose | UG-R4: one home; UG4 checks every other page cites |
| Declaring documents out of band is unaudited by `evolve` | UG-D9 is ruled (b), so UG3 (i) closes this; until it ships, UG1 pins the out-of-band step as an unaudited append-only header edit and shows a round passing only because of it; `gnd validate --document` still checks every cited span against the declared digest |
| A new locator widens the closed proposal contract | UG3 (i) spec states the schema-version decision (UG-Q5) and proves old proposals parse and digest unchanged (UG-R1) |
| Scope creep into the later wave | §7 |

## 7. Out of scope

- Issues 73, 77, 78, 95 (a later wave). Note for that wave: the model-growth-
  guardrails records say MG4 delivered extraction guidelines for issue 78, and
  issue 78 is still open. This milestone neither confirms nor dispositions it.
- Admitting `subtype_of`/`inherits_reference` on an existing object type under
  `--policy additive` (UG-D7 proposes to keep it a reviewed proposal).
- A shipped JSON Schema or translator for the host reply shape (UG-D5).
- Giving subtype links their own `status`/`modality` (a model-schema change,
  UG-D4).
- Any change to `gnd extract`, `gnd discover`, the discover fact-type judges or
  `gnd-model-from-text` Steps 1 to 7 as dialogue.
- Fixing MG3-Q2.
- Posting issue comments or closing issues without an explicit owner request.
- Certification or recertification (explicit owner request only); merge,
  release, publication.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, owner gate,
implementation with focused tests, one independent diff review, a refactoring
review, and a record. No code before recorded spec approval. UG1 changes no
source and still has its spec gate. Plan and close review: the project's bar is
the maintained panel (`project.md`); the predecessor ran four local readers by
owner ruling (UG-D1 asks again). Stop rule: at most one confirmation round after
round 1, restricted to blocking themes; stop early when most findings are
self-inflicted. Findings are unproved until reproduced. Work on topic branch
`claude/plan-unattended-model-growth-f116c3` for planning, then one branch per
implementation phase; PR each; merge on the owner's authorization only. Never
push to main.

## 9. Per-phase verification story

| Phase | Expected result | Focused gate (exact selection fixed in each spec) |
|---|---|---|
| UG1 | Replay and refusals pass; matrix complete; no source diff | `uv run pytest -q tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_growth_guidance.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_growth_example.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_digest_helpers.py --tb=short`; `uv run ruff check` on the new test |
| UG2 | As UG2-C1..C8 | UG1 gate plus `tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_rf6_packages.py tests/test_gnd_arch.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py tests/test_ik_close.py tests/test_public_binding_prose.py tests/test_documentation_tutorials.py`, a new `tests/test_evolve_population_check.py`, and `python3 scripts/components_index.py changed --base main --strict` — exact list fixed in the spec |
| UG3 | As UG3-C1..C7 | `tests/test_unattended_mode.py`, RF1 pins and harness, disclosure tests, packaged-skill pins as in UG2, the locator tests (`test_model_identity.py`, `test_model_evolution.py`), `components_index.py changed`, a new case file — exact list fixed in the spec |
| UG4 | Pages executed, pins pass | `uv run python tools/run_tutorials.py`; `uv run --group docs zensical build --strict`; `uv run python tools/check_docs.py site`; `tests/test_packaged_skills.py` and the install/doctor/skill-census tests — exact list at spec time |

Affected consumers: anyone parsing the evolve preview JSON (additive keys only
under the new option); anyone parsing `gnd validate --document` output (one
carved-out `warnings` entry, UG-R1); older GND readers of evolve proposals (a
new locator is forward-incompatible); the RF1 goldens and their harness
manifest; the packaged skill file inventory and prose pins.

### Implementability sweep (author inspection, not review)

| Question | Answer |
|---|---|
| Can UG1 run today? | Yes: it uses only shipped commands; helpers exist in two test files; the planning-time run of the related tests was green (203 passed). |
| Does the evolve preview have a population to check? | No: `--policy` sees `--populated` ids, sample rows, reference populations and `population` artifact locators, never fact rows (`effective_populated`). UG2 adds the input; it cannot be a re-use. |
| Can the checker be run on a candidate model plus a population from the evolve lane? | Yes, with zero allowances (UG-Q1 answered by inspection and an `arch.measure` probe by two readers). |
| Is a falsifiable end-to-end result named for each promised capability? | 74/75/76: UG1-C1/C2. 104-5: UG2-C1/C2 or the UG-D2 (a) disposition. Span coverage: UG3-C2. |
| Can a document-by-document loop run through `evolve` today? | Only if each round's document is declared in the model file before the round (scratch probe, 2026-11-07, above). UG1 turns the probe into a test. |
| Can a host keep an admitted constraint `proposed`? | Yes for constraints; no for subtype links (UG-D4). |

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Proposal | Owner ruling (relayed `(o1)`; the plan-gate record must carry the owner's verbatim message and re-confirm UG-D2, UG-D3, UG-D9) |
|---|---|---|---|---|
| UG-D0 | Who closes issues 74, 75, 76 and 104 | (a) the owner, from drafted dispositions after merge; (b) an agent closes on the owner's explicit instruction per issue; an unprompted close is outward-facing and not reversible in effect | (a) | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "Approve all as proposed (Recommended)"** → (a). A decision ruling, not a plan-gate approval. |
| UG-D1 | Plan and close review instrument | (a) four local readers, as MG-D1/TS-D2 ruled; (b) the maintained six-seat panel, the project's stated bar, needs the parent credentials and costs more | (a), with the project's bar stated at the gate; the owner rules | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "Approve all as proposed (Recommended)"** → (a) four local readers, with the maintained panel stated as the project's bar. |
| UG-D2 | Issue 104 item 5, second option | (a) decline: keep "reviewed non-additive proposal" as the route and say so; no code, 104 closes on items 1 to 5-first-option; (b) build the population-checked admission (§2.2): a new option on two commands, a new input to digest-bind, a lane edge; unattended hosts finally have a route for late-discovered constraints; (c) a narrower build: admit only when the supplied population is the model's own declared reference population (no new input): smaller, but hosts keep extracted facts outside the model, so it would not help them | (b). It is the only reading that closes the hole the issue reports. Cost: UG2 | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "(b) Build it (Recommended)"** → UG2 is to be built; it is still subject to its own spec gate. |
| UG-D9 | How a growth round declares its document (O20) | (a) document the out-of-band step and pin the refusal: no code, but an unaudited header edit stays in the loop; (b) an append-only `source.documents` locator that `--policy additive` admits: the declaration becomes part of the reviewed, digest-bound proposal, at the cost of a contract and schema change; (c) declare the whole corpus's digests up front: no code, but the header then names documents no round has read | (b) if the owner wants the loop fully inside `evolve`; otherwise (a). (c) is a host choice, not a GND ruling | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "(b) Add it to evolve (Recommended)"** → an append-only `source.documents` locator admitted by `--policy additive`; UG3 (i) is to be built, subject to its spec gate and UG-Q5. |
| UG-D3 | Fail closed on unchecked spans (MG5-Q3) | (a) leave as deferred: an unattended gate that omits `--document` checks structure only; (b) report counts only, exit unchanged; (c) counts plus an opt-in `--require-documents`-style flag that exits 3 on any unchecked span | (c); (b) if the owner prefers no new flag | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "(c) Counts + strict flag (Recommended)"** → counts always reported, opt-in flag exits 3 on any unchecked span; UG3 (ii) is to be built, subject to its spec gate. |
| UG-D4 | Subtype links carry no `status`/`modality` | (a) keep, as documented: the span, rationale and a reviewed consolidation are the controls; (b) add provenance status to subtype links: a model-schema change with migration and version cost, out of this wave | (a) | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "Approve all as proposed (Recommended)"** → (a). |
| UG-D5 | Host reply shape | (a) documented shape plus a test-only translator, as now (the issue allows "or the skill says the request must cover all of them"); (b) ship a JSON Schema in `gnd-orm-core/references`: pins, sync tests, and a promise nothing in GND reads | (a) | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "Approve all as proposed (Recommended)"** → (a). |
| UG-D6 | Pointing hosts at a duplicate judge | (a) UG4 text: act on a shape match by reusing the existing id, recording the doubt in `open_questions`, or keeping both with a stated reason; (b) also route to `gnd-judge-fact-types`, which is bound to discover evidence files and would need adapting | (a) | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "Approve all as proposed (Recommended)"** → (a). |
| UG-D7 | Extend `--policy additive` to admit `subtype_of` on an existing object type | (a) no: it can change inherited roles, constraints and the reference scheme, so facts may stop being interpretable; consolidation stays a reviewed proposal; (b) admit the narrow case of a subtype with no `inherits_reference` and a supertype with no constraint on a populated fact type: a measured design of its own | (a), as PR 106 and the contract already say | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "Approve all as proposed (Recommended)"** → (a). |
| UG-D8 | Phase 1 | UG1 first, ahead of any code, so dispositions and UG2/UG3 design rest on measured behavior (and so the O20 probe becomes a committed, falsifiable test) | as drafted | **(o1) Ruled 2026-11-07 (relayed by the session that put the questions to the owner): "Approve all as proposed (Recommended)"** → as drafted. |

| ID | Open question | Resolves in |
|---|---|---|
| UG-Q1 | Can the evolve lane call the checker under `tools/gnd_layers.json` with zero allowances? **Answered by plan review round 1: yes**, see §6. The UG2 spec re-runs `tests/test_rf1_layering.py` and `tests/test_gnd_arch.py` to confirm | answered; confirmed in the UG2 spec |
| UG-Q2 | Option and flag names (`--check-population`, `--require-documents` are placeholders) | UG2/UG3 specs |
| UG-Q3 | How does the population arrive: the existing `population`-kind artifact locator (already digest-bound, no new `apply` option), or a new option; and one composed input or several files (two clean files can violate in union)? | UG2 spec |
| UG-Q5 | UG-D9 is ruled (b): which of proposal `schema_version` 1, 2 and 3 carry the new locator (the contract says readers select one complete closed nested graph and mixed embeddings fail), and what do old readers do with a new proposal? | UG3 (i) spec |
| UG-Q4 | Does any census pin the `tests/` directory listing? **Answered by plan review round 1: no default-lane test does** (PR 106 and MG2 each added a test file with no census edit). `tests/test_digest_helpers.py` bans local functions named `_sha256`, `_sha256_bytes`, `_sha256_file` in any `tests/test_*.py`; the new file uses `support.digests.sha256_bytes` | answered |
| UG-Q6 | `project.md` says there is no component index (line 25) and also that it lives in `dev/components/` with a pre-PR `changed --strict` run (last section). Which governs? The plan applies the second | owner / maintainer |
| UG-Q7 | The issues carry downstream tracker labels (`GR-T…`). The plan and README cite issue numbers only; should the labels be restored anywhere? | owner |

## Close note `(c1)`, 2026-11-09 (plan repairs at the milestone close)

Raised by the phase records and the close review ([007-close.md](../007-close.md)). The text
above is kept as approved; each row below amends it, with the earlier wording quoted.

| Section | Earlier wording | Amendment | Raised by |
|---|---|---|---|
| Status line | "No phase has a spec approval. No code is written, no issue is closed or commented on." | Every phase UG1 to UG4 has an approved spec, a record and a merged PR (123, 147, 149, 151). Issues 74, 75 and 76 are closed (2026-11-08); 104 is open | close reader 4 (R4-F13) |
| §0 UG-R1 | parity "byte-identical to `12daa5b7`" | About twenty unrelated pull requests merged after `12daa5b7`. Parity is measured between `6d7b5327` (main just before PR 147, the first code PR) and `ad454305` (main after PR 149, the last); only this milestone's PRs lie between them. UG4 changed no code | the close parity table |
| §0 UG-R1 carve-out | one `warnings` entry on a `--document` run with an unchecked span | A second, corrective difference: a `--document` refusal (exit 3) on a model with a redaction policy or reference populations now carries the projected report its other results carry (UG3 review finding 1). Stated in the release notes | close reader 2 (R2-F5) |
| §2.2 and the contract's "Populated" paragraph | the contract defined subjects for a model-hosted constraint only; the code took a fact-type-hosted constraint's subject to be its host alone | A constraint's subjects are its host fact type, when it has one, plus the fact types its role references and rule atoms name, plus every fact type played by an object type it ranges over without a role. Repaired in code and contract at the close | close reader 1 (R1-F1, blocking) |
| §4 UG2, §5, §6 (RF1 goldens "re-pinned") | re-pin the RF1 goldens | Each phase added a successor fixture and left the historical goldens and `MANIFEST_SHA256` unchanged (UG2 F-i4, UG3-D13) | UG2 and UG3 specs |
| §4 UG2 size "400 to 650 source lines" | estimate | 747 added; the estimate omitted apply plumbing and review fixes | 003-phase-UG2.md |
| §8 "UG-D1 asks again" | the close instrument is asked again | UG-D1 (a) governed the close: four local readers, the maintained panel stated as the project's bar | the close |
| §9 UG4 row (full `run_tutorials.py`) | full run per phase | UG4 ran the growth group; the full run (310 blocks) ran in the close gate | 006-phase-UG4.md |

## Revision history

- r1, 2026-11-07: first draft by a planning session. Not reviewed. Not approved.
- r1.1, 2026-11-07: owner decision rulings recorded in §10 (relayed, tagged `(o1)`), conditional text made definite. Not reviewed. Not approved.
- r1.2, 2026-11-07: plan review round 1 (four local readers over r1.1) applied; see [plan-review-r1-disposition.md](plan-review-r1-disposition.md). Not re-read after the repairs.
- r1.2 approved, 2026-11-07: owner approval at the plan gate ("approved all", relayed), recorded in [001-plan.md](../001-plan.md). Status wording only; no other byte changed. No confirmation review round was run.
- close note `(c1)`, 2026-11-09: plan repairs at the milestone close, above. No other byte changed.
