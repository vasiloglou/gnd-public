# Phase MG2: additive policy on evolve

**Status: r1, approved by the owner 2026-11-04 `(s1)`.** Implementation
follows this approval.

`(s1)` Owner approval, 2026-11-04, quoted: "Approve MG2 spec", in answer to
"Approve the MG2 spec r1 with D1–D8 as proposed?". Approved bytes: SHA-256
`f04f2cf6c88275e627f81127524c4260bd5e34545ac1d127d16b59fdfd75449d` (before
this tag). Rulings: approval instrument prose (D1 (b)); no spec review panel;
D2 (a), D3 (a), D4 (a), D5 as stated, D6 (a), D7 (a), D8 (a) as proposed.

## Provenance

- Plan: [model-growth-guardrails-plan.md](model-growth-guardrails-plan.md) r3,
  approved `(a1)` 2026-11-03: §2.2, §4 MG2, §9 MG2 row, §10 MG-D2..D5, D12,
  D17.
- Source: [issue #75](https://github.com/vasiloglou/gnd-public/issues/75)
  (GR-T12).
- Inspection baseline: `d5f6e9e` (main after PR #81, MG1 merged). The evolve
  package is unchanged since `1446f90`, so the plan's line pointers hold.
- Plan review: themes D, F `(p1)` and R2-A, R2-B settled the apply path and
  the matrix; see the [round-2 disposition](plan-review-r2-disposition.md).
  **This spec's bytes carry no review opinion.**
- Prior record: [002-phase-MG1.md](../002-phase-MG1.md). Its open questions
  (MG1-Q3 `api.py` handlers, MG1-Q4 revalidation cost) do not touch evolve.
  Its boundary leaves nothing to MG2.
- Code survey of 2026-11-04 (one local reader, read-only) supplied the line
  citations below; each was spot-checked against the tree.

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #75, plan O4 | Refuse rename, delete, change of existing object types, fact types, roles | Matrix cells; T1 |
| #75, plan O5 | Refuse a replaced reference scheme | An object-type MODIFY whose diff touches `reference` is refused (allow-list); T1 (object-type MODIFY, `reference` row) |
| #75, plan O6 | Refuse an added or stronger constraint on a populated fact type | Matrix constraint rows; T1, T2 |
| #75, plan O7 | Name the rejected operations in the preview claim so `apply` cannot publish them | `policy_issues`; T3 service re-run; T3 CLI |
| Plan §4 MG2-C1 | One case per matrix cell not pre-empted, refused or admitted, each failing under the opposite verdict, on fixtures with no operation referencing the subject; role ADD on an existing fact type in a model with no operations (3); two-fault case pins 18 before 3 | T1, T1b, T1c |
| Plan §4 MG2-C2 | One case per strengthening item; weakening and rationale-only admitted; object-type description-only admitted against description plus `primitive` refused; fact-type MODIFY adding a mandatory inside the element on a populated fact type refused; `objectified_as` changed refused; model-hosted constraint spanning one populated and one unpopulated fact type refused; one case per populated source plus an unpopulated control | T2, T2b, T2c |
| Plan §4 MG2-C3 `(r2-A)` | CLI: preview with `--policy`, apply without (3, names the option); preview without, apply with (3); different `--populated` (3); `policy_issues` removed and digest recomputed, applied with matching options (11); matching options and no issues (0); a preview made with `--policy` and `--shape-report` applies (0). Service: `apply` on a preview whose `policy_issues` were removed (3, names operation index and cell), mutation control disabling the re-run applies (0) | T3, T3b, T3c; the `--shape-report` clause is deferred to MG3 (below) |
| Plan §4 MG2-C4 | Recorded before/after table: every evolve fixture previewed and applied without the options gives identical bytes and exits | T4 |
| Plan §9 MG2 row | "One case per matrix cell; apply re-check; recorded parity"; the focused gate command | Verification selection; T1, T3, T4 |
| Plan MG-R1 | Existing digests do not move | Omission in the serializer and the digest body; T4; the two byte pins in T5 |
| Plan MG-R2 | One home per policy | `additive_policy_issues` called by preview and apply; T3c mutation control |
| Plan MG-R3 | A gate never trusts a document it can be handed | Apply re-runs the policy on its own bytes; T3, T3b |
| Plan MG-R4 | Advice never gates | Not applicable: MG2 adds no advice; the policy is a gate by design |
| Plan MG-R5 | Disclosure | The `gnd evolve preview` and `gnd evolve apply` leaf rows already exist; issue text never quotes values; T6 |
| Plan MG-R6 | Layering and query policy | `gnd.evolve.policy` joins lane `evolve`, layer `lanes`; model reads through `ModelIndex`; T7 |
| Plan MG-R7 | Approval, evidence, anonymity | `auto=false`; T8 |
| Plan MG-R8 | Provenance never overstated | The policy writes no provenance; it refuses `proposed`→`confirmed` on populated fact types (`(p1)` F) |
| Plan §6 risks | Bypass by editing the preview; optional fields move old bytes; "strengthening" ambiguity; "populated" undecidable; RF1 goldens drift; names leak | T3, T4/T5, T2 (one closed list), the populated definition (preview's inputs only), T9, T8 |
| Plan O18 | API and CLI pins | T9 (RF1 goldens), T10 (exit map unchanged) |
| Plan O19 | Docs and release notes | Docs section; T11 |
| Plan O23 `(r1-V)` | RF1 goldens do not reproduce from a fresh capture | T9 recaptures under the three interpreters and records the manifest digest |
| Plan §10 MG-D2 | Version scheme | **Ruled `(p1)` D (iii):** optional v3 fields, omitted when unset |
| Plan §10 MG-D3, D4, D5, D12 | Strengthening list; populated; description edits; exit 3 | Accepted at the plan gate `(a1)` as written; bound below |
| Plan §10 MG-D17 | Model-hosted constraint populated when any named fact type is | **Ruled `(a1)` (a)** |
| Plan §5 | `gnd-model-evolve` skill and the evolution contract; RF1 goldens for `evolve preview` and `evolve apply`; Unreleased note | Docs section |
| Plan §7 | Out of scope | Below |

## Standing rules bound to this phase

1. **Totality:** `additive_policy_issues` consumes `EvolutionOperation.before`
   and `after` dicts that the proposal reader already validated as closed
   models (`evolve/models.py:285-357`) and that `_apply_declared_operations`
   has checked equal to the actual elements (`service.py:916-918`) before the
   policy runs (order below). The policy is still total over any dict pair:
   a key that is not a string, a value that is not a list where the family
   expects one, or an unknown constraint `type` yields a `neither` verdict
   (refused on a populated fact type), never a traceback. T12 feeds hostile
   `before`/`after` pairs directly.
2. **Input cap bounds the algorithm:** one walk over the proposal's
   operations; per operation, a diff of two element dicts and at most one
   lookup in the populated set. T13 runs 2,000 operations against a model
   with 2,000 populated fact types and asserts fact-type visits ≤ 2,000 and one
   `ModelIndex` construction.
3. **Validation order:** per boundary, below, pinned by T1c (18 before 3) and
   T1d (D-12 message before a policy issue).
4. **One walk:** the policy is one function over all four locator kinds and
   all four operation kinds; the matrix is a lookup table inside it, not four
   per-kind functions. T3c's mutation control proves preview and apply share
   it.
5. **One home:** the matrix and the strengthening list are normative in one
   document (D3 decides which); the other pages cite it. The `PolicyIssue.cell`
   literal is the implementation's spelling and T14 asserts the schema enum,
   the contract table and the implementation's map cover the same set.
6. **Measurement over argument:** T4 is a recorded digest table; T5 keeps the
   two existing byte pins.

MG-R4 does not apply (no advice surface). MG-R8 applies only through `(p1)` F,
bound above.

## Goal

`gnd evolve preview MODEL PROPOSAL ... --policy additive [--populated FT ...]`
exits 0 and writes a schema-3 preview carrying `policy`, `populated_args`,
`populated` and `policy_issues: []` when every operation is admitted; exits 3
and still writes the preview, with one `policy_issues` entry per refused
operation naming its index, locator reference and matrix cell, otherwise.
`gnd evolve apply ... --policy additive [--populated FT ...]` exits 3 when its
options differ from the reviewed preview's, 11 when the preview it is handed
differs from the one it rebuilds, 3 when the service's re-run finds an issue,
and otherwise behaves as at `1446f90`. Without `--policy`, every preview and
apply over every evolve fixture is byte-identical to `1446f90` and exits the
same.

## Design

### `src/gnd/evolve/policy.py` (new, about 220 lines; lane `evolve`, layer `lanes`)

```python
POLICY_ADDITIVE: Final = "additive"
PolicyName = Literal["additive"]

PolicyCell = Literal[
    "object_types.modify", "object_types.rename", "object_types.delete",
    "fact_types.modify", "fact_types.rename", "fact_types.delete",
    "role.add", "role.modify", "role.rename", "role.delete",
    "constraint.populated.add", "constraint.populated.modify",
    "model_identity.modify",
]

class PolicyIssue(_ClosedFrozenModel):          # same base as the preview models
    operation_index: int                          # position in proposal.operations
    operation_id: str
    reference: str                                # locator.reference()
    cell: PolicyCell
    detail: str                                   # ids and key names only; never a value

def effective_populated(
    before: Model, proposal: EvolutionProposal, *, populated_args: Iterable[str]
) -> frozenset[str]

def additive_policy_issues(
    before: Model, proposal: EvolutionProposal, *, populated: frozenset[str]
) -> tuple[PolicyIssue, ...]
```

**`effective_populated`** returns the union of: fact types whose
`sample_population` has at least one row (`ModelIndex.iter_fact_types_shared`);
fact types named by `before.reference_populations[*].fact_types`
(`documents.py:45`); fact types named by a `proposal.artifacts` entry of
`artifact_kind: "population"` through its `references` of the form
`fact_types[ID]` (`models.py:387-424`; the path is never opened, as today);
and `populated_args`. An argument naming no fact type of the before model is
an error (D4). The result is what the preview writes as `populated`.

**`additive_policy_issues`** walks `proposal.operations` once, in order. For
each, the verdict is the matrix cell for (locator kind, operation kind), with
these allow-lists and sub-rules; "existing" means the id is in the before
model, "same-proposal" means an earlier ADD in this proposal introduced it:

| Locator | ADD | MODIFY | RENAME | DELETE |
|---|---|---|---|---|
| `object_types` | admitted | admitted iff `diff_keys(before, after) ⊆ {description, provenance.rationale}`; else `object_types.modify` | `object_types.rename` | `object_types.delete` |
| `fact_types` | admitted | admitted iff `diff_keys ⊆ {provenance.rationale}`; else `fact_types.modify` | `fact_types.rename` | `fact_types.delete` |
| `operations` | admitted (the gate owns it) | pre-empted, exit 18 (`service.py:612-627`) | pre-empted | pre-empted |
| role | admitted iff `fact_type_id` is same-proposal; else `role.add` | `role.modify` | `role.rename` | `role.delete` |
| constraint, subject not populated | admitted | admitted | pre-empted: a constraint cannot be renamed (`models.py:344`, exit 3 at proposal read) | admitted |
| constraint, subject populated | `constraint.populated.add` | admitted iff every differing key is a weakening item or `rationale`; else `constraint.populated.modify` | pre-empted (3) | admitted |
| model identity | — | `model_identity.modify` | — | — |

The **subject** of a constraint is its host fact type (`host == "fact_type"`)
or, for `host == "model"`, the set of `fact_type` values of every
`role_ref`-shaped dict (keys `fact_type` and `role`,
`orm-meta.schema.json:618`) reachable in the constraint by one recursive
walk over its values. The walk is family-agnostic, so `role_refs`,
`subset_role_seq`, `superset_role_seq` and a single `role_ref` are all
covered without a per-family list, and it reads no key RF6 counts.
(`ModelIndex.constraint_roles`, `model_index.py:187`, returns role *names* of
a fact-type-hosted constraint and does not serve here.) A model-hosted
constraint is populated when **any** subject is (MG-D17 (a)). A subject that
is a same-proposal fact type is never populated.

`diff_keys` is the set of dotted paths at which two dicts differ, descending
into nested dicts; lists are compared whole, so a changed `roles`,
`constraints` or `sample_population` list is one differing key and refused.

**Strengthening and weakening** (the closed list of §2.2, MG-D3 (a), `(p1)`
F), per differing key of a constraint MODIFY:

| Key | Strengthening | Weakening |
|---|---|---|
| `roles` (uniqueness, internal and external) | proper subset of before | proper superset |
| `allowed` (value) | proper subset | proper superset |
| `range.min` / `ranges[*].min` | raised, or `min_inclusive` true→false | lowered, or false→true |
| `range.max` / `ranges[*].max` | lowered, or `max_inclusive` true→false | raised, or false→true |
| `bound.min` (frequency, cardinality) | raised, or added | lowered, or removed |
| `bound.max` | lowered, or added | raised, or removed |
| `modality` | `deontic`→`alethic` | `alethic`→`deontic` |
| `status` | `proposed`→`confirmed` | `confirmed`→`proposed` |
| `rationale` | — (admitted) | — (admitted) |

Any other differing key (`type`, `role`, `role_ref`, `object_type`,
`subset_role_seq`, `source`, `owner`, `allowed`↔`range`, `status`→`rejected`,
a `ranges` list whose length changes, an unknown key) is **neither** and is
refused on a populated subject. A MODIFY is admitted only when every differing
key is weakening or `rationale`. "New mandatory" from the plan's list is the
`constraint.populated.add` cell, since a mandatory constraint is a new element.

`detail` is built from ids, key names and the verdict word only (for example
`"fact_types[orders].constraints[value:...:0]: allowed narrowed"`); it never
interpolates an `allowed`, `range` or sample value (MG-R5; T6).

### `src/gnd/evolve/models.py` (about +25 lines)

`EvolutionPreview` and `_EvolutionPreviewV3` gain, after
`accepted_blast_radius_sha256`:

```python
policy: Literal["additive"] | None = None
populated_args: tuple[NonEmptyString, ...] | None = None   # sorted, unique
populated: tuple[NonEmptyString, ...] | None = None        # sorted, unique
policy_issues: tuple[PolicyIssue, ...] | None = None
```

`_serialize_wire_version` (`:783-787`) pops each of the four keys whose value
is `None`. `_bindings_match` (`:789-821`) adds: the four are all `None` or none
is; `populated_args ⊆ populated`; both sorted and unique. Because
`model_dump(mode="json")` runs the serializer, the recomputed digest at `:818`
agrees with the written bytes. `accepted_blast_radius_sha256` keeps writing
`null`. V1 and V2 readers are untouched.

Serialized, with the policy:

```json
{
  "schema_version": 3, "...": "...",
  "accepted_blast_radius_sha256": null,
  "policy": "additive",
  "populated_args": ["work_item_has_title"],
  "populated": ["orders", "work_item_has_title"],
  "policy_issues": [
    {"operation_index": 1, "operation_id": "rename-title", "reference": "object_types[title]",
     "cell": "object_types.rename", "detail": "object_types[title]: rename refused"}
  ],
  "preview_sha256": "..."
}
```

Without the policy the document has no `policy*` or `populated*` key.

### `src/gnd/evolve/service.py` (about +45 lines)

```python
class EvolutionPolicyRefusedError(EvolutionError):   # mapped to 3 by type
    issues: tuple[PolicyIssue, ...]

def preview(self, proposal, *, accepted_blast_radius_sha256=None,
            policy: PolicyName | None = None,
            populated: Sequence[str] = ()) -> EvolutionPreview
```

Order inside `preview`, the normative order with one home (this function):
pending check (11) → stale identity (11) → load before (3) → **operations gate
(18)** → candidate validation (3) → declared operations equal the candidate
(3) → D-12 (3) → **policy** → verbalizations → blast radius → accepted digest
(11) → build. The policy step, only when `policy` is given: `populated_set =
effective_populated(...)`, `issues = additive_policy_issues(...)`; the four
fields enter `values` and `digest_body` only then. `preview` does **not**
raise on issues: it returns the preview carrying them, so the document can be
written for review (D2). `populated` given without `policy` raises
`EvolutionError` (3).

`apply` (`:1554`), right after the gate re-run at `:1576-1579`: when
`preview.policy` is set, recompute `populated` from the preview's
`before_model` text and `populated_args`, re-run `additive_policy_issues`,
and raise `EvolutionPolicyRefusedError` on any issue (3), message
`"additive policy refused operation {index} ({cell})"`. The preview's own
`policy_issues` list is not consulted (MG-R3): a stripped list is recomputed.
When the recomputed set differs from `preview.populated`, raise
`EvolutionError("populated set changed before apply")` (11, through the
`stale_markers` arm by the words "changed before apply").

### `src/gnd/commands/evolve.py` and `src/gnd/evolve/cli_service.py` (about +70 lines)

Options on `preview` and `apply`: `--policy {additive}` (default `None`) and
`--populated FT` (`action="append"`, metavar `FACT_TYPE`, default `None`).
`--populated` without `--policy` is refused at the handler with exit 3,
message naming both options. `handle` passes them positionally as today.

`_cmd_evolve_preview`: `service.preview(proposal, policy=..., populated=...)`;
publish the document as today; emit the claim; return 3 when
`preview.policy_issues` is non-empty, else 0. Text mode adds `policy:` and
one `policy_issue:` line per issue only when the policy is set.

`_cmd_evolve_apply`, inserted after step 4 (same proposal) and before the
retry branch at `:620`: compare `(policy, sorted(set(populated)))` from the
arguments with `(reviewed.policy, reviewed.populated_args)`. Any difference,
including present in one and absent in the other, is `_EvolutionCLIError(3)`
naming `--policy` or `--populated`. Both `service.preview` calls (`:643`,
`:661`) receive the options, so the fresh/reviewed equality (11) covers a
tampered `policy_issues` list. `_evolve_error_exit` maps
`EvolutionPolicyRefusedError` to 3 by type, before the generic arm.

MG3's `--shape-report` clause of C3 cannot be written here: the option does
not exist. MG3 inherits that case (open question MG2-Q1).

### Docs (about 120 lines)

- `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md`: the
  `EvolutionPreview` prose (`:176-196`) names the four optional fields and
  their omission; a new subsection carries the matrix and the strengthening
  table **if D3 chooses the contract as the home**; §7 exit bands gains the
  policy refusal under 3.
- `docs/reference/evolve-policy.md` (new) with a `zensical.toml` Reference nav
  entry after "Rule verbalization": options, the guarantee's condition (apply
  must repeat `--policy`), what a stripped preview does, exits; cites or hosts
  the matrix per D3.
- `docs/reference/cli.md:41-42`: the option forms.
- `src/gnd/skills/gnd-model-evolve/SKILL.md`: one subsection after "ORM+ v2
  operations" stating the policy, that `apply` repeats the options, and exit 3.
  Prose pins (`tests/test_skill_prose_sync.py:121`,
  `tests/test_public_binding_prose.py:8`, `tests/test_il6_skill_census.py:95`)
  are run; counts measured at execution.
- `docs/release-notes.md`: an Unreleased entry.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Approval instrument | (a) corpus-first: `tests/fixtures/evolve-policy/` with one narrated case per matrix cell and strengthening item, answer key split out; a station-0 session before code; the default for an exit-code contract per `review-convergence.md`; (b) this prose: the matrix and strengthening tables above are the narrated outcomes, and T1/T2 are generated from one before model, as MG1's T4b/T4c were | (b), because every case is a one-key mutation of one fixture and the two tables already enumerate the answers; the burden of argument is noted |
| D2 | A preview with issues | (a) writes its document and exits 3, as the plan says; `--out` is write-once, so a retry with a corrected proposal under the same path exits 11 unless the path changes; (b) refuses without writing, as every exit-3 preview does today: the issues then exist only on stderr and O7 ("in the preview claim") is unmet | (a) |
| D3 | Normative home of the matrix and strengthening list | (a) the packaged evolution contract, which already owns the preview format and ships with the package; the docs page cites it; (b) the docs page; the contract cites a URL | (a) |
| D4 | `--populated` id not in the before model | (a) exit 3 naming the id: a typo would otherwise silently weaken the guarantee; (b) ignored and recorded in `populated_args` only | (a) |
| D5 | Constraint RENAME cells | The matrix marks them refused; a constraint cannot be renamed at all (`models.py:344`), so the proposal is refused at read with 3 and the policy never sees it. Record as a refuted premise; the cells become pre-empted with a read-time case | as stated |
| D6 | D-12 versus the policy | (a) D-12 first: a preview that is written for review is otherwise valid, and both exit 3; (b) policy first: the issue list is complete even for a D-12-invalid proposal, but the preview cannot be written | (a) |
| D7 | `apply --populated` when the preview carries `populated_args: []` | (a) an empty argument set equals an absent one, so `--policy additive` alone matches a preview made with `--policy additive`; (b) distinguish `[]` from absent | (a) |
| D8 | Counted RF6 reads | `before.reference_populations[*]["fact_types"]` is one counted read (ceiling 365, now 363). (a) take it, record a `query-successor.json`; (b) route through a `ModelIndex` accessor added in this phase | (a) unless implementation finds an existing exempt accessor |

## Tests

New file `tests/test_evolve_additive_policy.py` unless noted. Fixture: a
before model `tests/fixtures/evolve-policy/base.orm.yaml` with no
`operations`; object types `customer`, `order`, `amount`; fact types
`customer_places_order` (populated: two `sample_population` rows; inline
uniqueness, value, frequency constraints, `modality: deontic`, `status:
proposed`) and `order_has_amount` (unpopulated, same constraint shapes); one
model-hosted `subset` constraint naming both. Cases build proposals with the
builders of `tests/test_model_evolution.py:64` and `discover/output.py:62,87`.

| # | Case | Expected |
|---|---|---|
| T1 | One case per non-pre-empted matrix cell, on the fixture: object-type and fact-type ADD, MODIFY (confined), RENAME, DELETE; role ADD on existing, role ADD on same-proposal fact type, role MODIFY/RENAME/DELETE; constraint ADD/MODIFY/DELETE on `order_has_amount` and on a same-proposal fact type; constraint ADD/DELETE on `customer_places_order`; model-identity MODIFY | admitted cells: `policy_issues == []`, exit 0; refused cells: exactly one issue with the cell name, index and reference, exit 3, document written |
| T1a | Each refused cell's **opposite verdict**: a mutant policy that admits the cell (scratch plugin) makes the case fail; each admitted cell fails when the mutant refuses it | asserted per cell |
| T1b | Object-type MODIFY allow-list: `description` only (admitted); `provenance.rationale` only (admitted); `description` plus `primitive` (refused); `reference` changed (refused, O5); fact-type MODIFY `provenance.rationale` only (admitted); `objectified_as` changed (refused); a mandatory added inside the element on the populated fact type (refused, cell `fact_types.modify`); `sample_population` row added (refused) | as stated |
| T1c | Two-fault: a proposal with a RENAME on a fact type an existing operation references, under `--policy additive`, on `tests/fixtures/models/v2_operations.orm.yaml` | exit 18; no preview written |
| T1d | A proposal failing D-12 and the policy | exit 3 with the D-12 message; no preview written (D6) |
| T1e | Pre-empted cells: a constraint RENAME; an `operations` MODIFY | 3 at proposal read; 18 (D5) |
| T2 | One case per strengthening item on `customer_places_order`'s inline constraints and on the model-hosted constraint: `roles` narrowed, `allowed` narrowed, `range.min` raised, `range.max` lowered, `min_inclusive` true→false, `bound.min` raised, `bound.max` lowered, `bound.max` added, deontic→alethic, proposed→confirmed | each refused (`constraint.populated.modify`) |
| T2a | Each item reversed (weakening), and `rationale` only | each admitted |
| T2b | Neither: `type` changed; `role` changed; `allowed`→`range`; `status`→`rejected`; two keys where one strengthens and one weakens | refused |
| T2c | Populated sources: sample rows (fixture); reference-owned (`tests/fixtures/reference-corpus/dispatch`); a `population` artifact locator naming `fact_types[order_has_amount]`; `--populated order_has_amount`; and the unpopulated control (`order_has_amount` with none of these) | the same constraint ADD is refused under each source and admitted in the control; `populated` lists the union, `populated_args` only the argument |
| T2d | Model-hosted `subset` spanning populated and unpopulated: ADD under the fixture (refused, MG-D17 (a)); the same ADD after `customer_places_order`'s rows are removed (admitted) | as stated |
| T2e | `--populated no_such` | exit 3 naming the id (D4) |
| T3 | CLI (`support.cli_runner.run_main`): preview with `--policy`, apply without (3, names `--policy`); preview without, apply with (3); different `--populated` (3, names `--populated`); `policy_issues` deleted and `preview_sha256` recomputed, applied with matching options (11); matching options, no issues (0, then finalize 0); `--populated` without `--policy` on preview (3) | as stated |
| T3a | Apply's option check runs before the retry branch: a staged pending transaction plus mismatched `--policy` | 3, not the retry path |
| T3b | Service: `EvolutionService.apply` on a preview whose `policy_issues` were removed (built with `model_copy` and a recomputed digest so `_bindings_match` passes) | `EvolutionPolicyRefusedError`; message names the operation index and cell |
| T3c | Mutation control: with the re-run in `apply` disabled (scratch plugin), T3b's preview applies (0) | proves the re-run is the guard |
| T4 | Before/after `(r1-R)`: for every evolve fixture (`phase4_reference/evolution.json` four cases, `ik5-corpus`, `reference-corpus/dispatch`, `ik4-corpus`, `bookrec/genre-proposal.json`, `course/credit-cap-proposal.json`, `v2_operations`) run `gnd evolve preview` and, where it applies today, `apply` without the options at `d5f6e9e` and after; record `evidence/MG2/parity-{before,after}.json` with digests and exits | identical bytes (modulo the documented `<WS>` normalization) and exits |
| T5 | `tests/test_evolve_references.py::test_t6_reference_free_previews_are_unchanged` and `tests/test_object_type_description.py::test_t7_evolve_preview_equals_the_base_commit` | exit 0 unchanged |
| T6 | `detail` never contains a value: a value constraint with `allowed: ["SECRET-A", ...]` narrowed | the issue's `detail` and the whole preview text outside `candidate_model`/`before_model`/`verbalization` do not contain `SECRET-A`; `tests/test_disclosure_mode.py` and `test_disclosure_docs.py` exit 0 with no table change |
| T7 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py` | exit 0; `gnd.evolve.policy` in the map; zero allowances; successor files recorded if a counted or dynamic read is added |
| T8 | Anonymity scan over files added since `d5f6e9e` | exit 0 |
| T9 | RF1 goldens: `tools/rf1_pins.py capture` under py311, py313, py314, then `merge`; `MANIFEST_SHA256` in `tests/test_rf1_pin_harness.py:29` updated; `tests/test_rf1_cli_pins.py` | exit 0; `EXPECTED_PARSERS` stays 57; diff confined to `gnd_evolve_{preview,apply}` help and exit-probe files, `tree.json` and the manifest |
| T10 | `tests/test_rf1_cli_pins.py::test_cli_exit_map`, `tests/test_exp_bands.py`, `tests/test_verification_fixes.py` | exit 0: no new exit |
| T11 | `uv run python tools/run_tutorials.py`, `uv run --group docs zensical build --strict`, `uv run python tools/check_docs.py site`, the skill prose pins | exit 0 |
| T12 | Hostile `before`/`after` pairs to `additive_policy_issues` directly: non-string keys, `roles: "x"`, `bound: 3`, unknown `type`, `allowed: None` | a `neither` verdict (refused when populated); no exception |
| T13 | 2,000 generated populated fact types, 2,000 constraint MODIFY operations | fact-type visits ≤ 2,000; one `ModelIndex` construction; under 5 s |
| T14 | The `PolicyCell` literal, the contract's table and the implementation's dispatch map cover the same set; a preview whose `cell` is outside the literal fails to read | as stated |

Every refused cell has its admitted mutant (T1a); every admitted cell has its
refusing mutant; every strengthening item has its weakening reverse (T2, T2a);
every populated source has the unpopulated control (T2c); the model-hosted
"any" reading has its "every" discriminator (T2d).

### Verification selection `(r1-N)`

| Obligation | Disposition | Command or evidence | Input boundary | Invalidation |
|---|---|---|---|---|
| Plan §9 MG2 row | run | `uv run pytest -q tests/test_evolve_additive_policy.py tests/test_model_evolution.py tests/test_evolution_conformance.py tests/test_evolve_loading.py tests/test_evolve_references.py tests/test_public_evolution_drift_readers.py tests/test_public_evolution_legacy_readers.py tests/test_public_evolution_version_graph.py tests/test_public_legacy_evolution.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py`, exit 0 | the evolve package, `commands/evolve.py`, the fixtures named in T4, RF1 goldens | any change to those |
| Impact closure | run | plus `tests/test_object_type_description.py tests/test_model_v2.py tests/test_exp_bands.py tests/test_verification_fixes.py tests/test_rf1_pin_harness.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_public_binding_prose.py tests/test_il6_skill_census.py tests/test_packaged_skills.py tests/test_measure_offline.py tests/test_conformance_payload.py`, exit 0 | the second byte pin, the exit registry, the manifest digest, skill prose, the handler source scan | same |
| Docs | run | T11's three commands, exit 0 | docs, nav, skill text | same |
| Parity | run | T4's capture at `d5f6e9e` and after, recorded under `evidence/MG2/` | the fixtures named in T4 | same |
| Broad lanes | cadence | `uv run pytest -q -m "evidence or census"` on explicit owner request | — | — |

## Out of scope for this phase

- `--shape-report` and `shape_matches` (MG3); the C3 clause that pairs them
  with the policy moves to MG3 (MG2-Q1).
- Any policy other than `additive`; a policy on `finalize`; a `--force`.
- Migrating facts, or checking a population against the candidate: "populated"
  is a set of ids, not a population read.
- Changing exit 18's meaning or adding an exit.
- How-to text beyond the reference page (MG6).

## Size

About 365 source lines (`policy.py` 220, `models.py` 25, `service.py` 45,
`cli_service.py` 55, `commands/evolve.py` 20), 650 test lines, one fixture
model, one reference page, two contract sections, RF1 golden recapture.

## Approval instrument

Per D1: this prose, unless the owner selects corpus-first.

## Open questions raised at spec time

| ID | Question | Target |
|---|---|---|
| MG2-Q1 | C3's "preview made with `--policy` and `--shape-report` applies (0)" needs MG3's option | MG3 spec, T-list |
| MG2-Q2 | Constraint RENAME cells are pre-empted by proposal validation (D5), a refuted premise of the plan's matrix | plan repair at milestone close |

## Implementation findings

Recorded as found, 2026-11-04. The approved text above is not edited.

- **F1, refutes the matrix's constraint RENAME cells (spec D5 anticipated
  it).** `EvolutionOperation` refuses a constraint RENAME at read
  (`models.py:344`), so the cells are pre-empted with exit 3. T1e pins the
  read-time refusal; the policy never sees one.
- **F2, narrows the reachable strengthening and weakening items.** D-12
  (`service.py:404-418`) admits a changed constraint only as
  llm-inferred/proposed/deontic, user-supplied/confirmed, or a reviewed
  induced confirmation. So `confirmed`→`proposed` is pre-empted by D-12 at
  the service level (T2a pins the pre-emption), and validation itself refuses
  `user-supplied` with `status: proposed` (`semantic:status-source`). The
  `proposed`→`confirmed` strengthening is reachable only through an induced
  constraint carrying `provenance.reviewed_in`; the fixture holds one (a
  guarded rule spanning the populated fact type). The policy function still
  classes both transitions by the table (T12 direct cases).
- **F3, a design repair found by the fixture.** The confirm transition adds
  `provenance.reviewed_in` beside `status`; under the approved table that key
  is "neither" and would refuse the MODIFY for the wrong reason. The
  implementation admits `provenance.reviewed_in` as neutral, exactly the key
  D-12's `_without_review` strips, so the transition is judged by `status`.
  The contract table says so. Also found: a model-hosted guarded rule names
  its subject fact types in `antecedent[*].fact_type` (no `role` key beside
  it), so the subject walk collects every string `fact_type` value, not only
  `role_ref`-shaped dicts, as the spec's Design first said.
- **F4, deviates from T13's bound.** `effective_populated` and
  `additive_policy_issues` each walk the before model's fact types once (two
  linear walks), so T13 asserts visits ≤ 2 × N and one `ModelIndex`
  construction, not ≤ N. Merging the walks would couple the two functions'
  signatures; recorded as MG2-Q3.
- **F5, pre-empted "neither" item.** A constraint `type` change is refused at
  proposal read ("constraint family must match the stable locator"), so T2b's
  service-level row is replaced by a direct `constraint_change` assertion.
- **F6, role ADD and role DELETE are pre-empted by candidate validation.** A
  fact type's reading must have one placeholder per role, so a role ADD or
  DELETE alone never yields a valid candidate; the realistic proposal is a
  fact-type MODIFY (refused by the allow-list). The `role.add` and
  `role.delete` cells are judged by the policy function directly in T1 (the
  `reach` column), and T1 also pins that the service refuses those proposals
  with the validation message (3). A role ADD on a fact type the same
  proposal adds is reached by adding the fact type with that role (admitted,
  T1 "role.add on a fact type added with that role").
- **F7, the proposal reader freezes operation dicts** (`_freeze_json`,
  `models.py:67-71`): lists arrive as tuples. The subset test and the subject
  walk accept both; found by T2 ("roles narrowed" reported `neither`).
- **F8, element allow-lists are prefix-closed.** `description` is a dict, so
  its diff path is `description.summary`; a path beneath an admitted key is
  admitted (found by T1 "object_types.modify (confined)").
- **F9, the IL6 skill census.** `tests/test_il6_skill_census.py` credits an
  uncommitted packaged-skill edit to `IL6`, so its three T7 cases fail while
  the `gnd-model-evolve` SKILL.md edit is uncommitted and pass once the MG2
  commit lands (a non-IL scope matches no census phase). Verified after the
  commit; not part of the gate command.
- **F10, RF6 census.** One counted read (`entry.get('fact_types')` in
  `effective_populated`, D8 (a)): `evidence/MG2/query-successor.json`, 295
  rows / 364 occurrences against the ceiling 365, original metric 309 against
  310. Dynamic-read syntax rows: `evidence/MG2/dynamic-query-successor.json`,
  32 rows / 37 occurrences added, none removed (6,933 rows / 8,663
  occurrences). No allow-list row.

## Open questions raised at implementation

| ID | Question | Target |
|---|---|---|
| MG2-Q3 | Merge `effective_populated` and `additive_policy_issues`'s two walks of the before model into one, or expose the known-id set from the first to the second | MG3, which touches the same preview path |
| MG2-Q4 | The RF6 headroom is now one counted read (364 of 365) and one on the original metric (309 of 310); MG3's signature helper must read through `ModelIndex` only | MG3 spec |

## Review dispositions

One local reviewer, verdict reject, seven findings
([phase-MG2-claude-review.md](phase-MG2-claude-review.md)). Each finding was
reproduced before it was fixed; each fix carries a regression test that was
shown to fail against the pre-fix code.

| Finding | Class | Disposition | Regression |
|---|---|---|---|
| R-F1, hosted MODIFY subjects from `before` only | blocking | Fixed: subjects are the union of `before` and `after`. A post-fix mutant that drops the `before` side survived the first regression, so a second case pins that direction | `test_review_f1_hosted_modify_retargeted_onto_a_populated_fact_type_is_refused`, `test_review_f1_hosted_modify_moved_off_a_populated_fact_type_is_refused` |
| R-F2, `roles` superset classed weakening for frequency | blocking | Fixed: the `roles` subset rule applies to uniqueness only; any other family's `roles` change is "neither". `constraint_change` takes the family; contract and docs say so | `test_review_f2_frequency_roles_widened_is_refused` |
| R-F3, empty `sample_population` unpinned | hardening | Case added | `test_review_f3_an_empty_sample_population_is_not_populated` |
| R-F4, bool bounds and `ranges` elementwise unpinned | hardening | Cases added | `test_review_f4_ranges_elementwise_and_bool_bounds` |
| R-F5, dead `subjects -= added_fact_types` | completeness | Line removed with a comment saying why none is needed | none: equivalent by construction |
| R-F6, "before anything else" overstated | completeness | Contract and docs now say "before the retry branch and the fresh/reviewed equality" | T3a already pins the order |
| R-F7, MODIFY of a same-proposal fact type refused | completeness | Kept conservative; one contract sentence says so | T1 matrix row |

Mutants re-run on the fixed bytes: M8, M9, M11, the `before`-side variant of
M14 and the R-F2 reversion are each killed. M3 is gone with the line it
mutated. M24 stays equivalent: the CLI already refuses differing options
before it rebuilds the preview.
