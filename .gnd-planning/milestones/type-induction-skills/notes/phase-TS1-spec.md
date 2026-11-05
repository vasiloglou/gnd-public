# Phase TS1 spec: type evidence from the fact-type family

## 1. Status

**r2, awaiting owner review.** `auto=false`. Implementable once the owner
approves this spec and rules §7. No implementation file has been created.

## 2. Provenance

- Plan: [type-induction-skills-plan.md](type-induction-skills-plan.md) r1,
  approved `(a1)` 2026-11-05 without plan review
  ([gate](../001-plan-gate.md)); §2.1, §4 TS1, §9 TS1 row.
- **r1** (SHA-256 `c04210d790bbfd366dd1d9b1d1f7af12bfe44843d5b8ab03d0a8acc636dd99aa`)
  was drafted against `549ebb9` and carried no review or approval.
- **r2** (2026-11-05, this revision) re-reads every cited line on main at
  `b733b2a` (PR #86 merged as `9f87fa0`, so TS-D1 is met). Changes from r1
  are tagged `(r2)`. The main one: commit `e32cc36` applied the owner's CT4-Q1
  ruling ([008-owner-rulings.md](../../composition-and-type-induction/008-owner-rulings.md)),
  so under `customer` the family omits `attribute_sha256`. r1 keyed groups on
  that digest; r2 does not (§6.2, refuted premise P1).
- Code read at `b733b2a`: `src/gnd/discover/types.py` (`propose` `:77`,
  `show_digests` `:83`, `existing` `:99`, `skipped` `:104-105`,
  `multi_valued` `:143`, `match` `:156-159`, `drop_last` `:47-51`,
  `group_sizes` `:194`, report entry `:203-208`), `discover/service.py`
  (`discover` `:193`, `_cmd_discover` `:360`, path checks `:378-394`, the
  written-bytes `drop_last` loop `:420-431`), `commands/discover.py`
  (`:121-150`, `show_digests = resolve() != "customer"` `:132`),
  `discover.schema.json` (`attribute_sha256` optional), `disclosure.py`.
- No review has run over these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan O4, TS1-C1 | evidence of every group: status, signature, counts | §6.1, §6.2; T1, T2, T5 |
| Plan TS1-C2 | candidates with readings, `signature_equal`, row and overlap counts | §6.2; T3, T4 |
| Plan TS1-C3 | `origin` from `provenance.induced_from`; malformed exits 3 | §6.2; T7, T7b, T8 |
| Plan O6, TS-R5, TS1-C4 | value-free unless `values_allowed`; **(r2)** digest-free under `customer` (008 CT4-Q1) | §6.3; T9, T9b |
| Plan TS1-C5 | path rules and exits | §6.4; T10..T13 |
| Plan O5, TS-R1, TS1-C6 | `--out`/`--report` identical with the option; baseline parity without it | §6.4; T15..T17 |
| Plan TS1-C7 | cap and `truncated` | §6.2; T14 |
| Plan §9 TS1 row | "Evidence complete, value-free, outputs unchanged" with the listed gate | §8 ledger |
| Plan §5 | `discover` RF1 help and exit goldens; disclosure `option` sentence | §6.3, §6.4; T15 |
| Plan §6 risks | default drift; stale base | T16, T17; this revision |
| Plan §7 | out of scope | §9 |
| CT4 F4 | redacted roles | §6.3; T6 |
| CT close R2-1 | written-bytes trimming decides `over_budget` | §6.4 (evidence built after the loop at `service.py:420-431`); T14b |
| 008 CT4-Q1 **(r2)** | digest omitted under `customer` | §6.2, §6.3; T9b |
| 008 CT-close-Q1, Q2 **(r2)** | the owner's words: "semantically with a skill"; "with a skill a variant of rai-orm"; the deterministic family keeps counting `multi_valued` | cited for plan TS-D0; TS-R1 holds |

## 4. Standing rules, bound

- **TS-R1:** the evidence is built from the `TypeProposals` the run already
  holds; `--out` and `--report` are written exactly as today. T16 compares
  bytes over every fixture and mode.
- **TS-R2:** the evidence states `signature_equal` and counts; it never
  states "duplicate".
- **TS-R3:** no judgements in TS1. The evidence carries the raw-byte
  `model_sha256` and `population_sha256` the report already uses, so TS2 can
  bind to the evidence digest.
- **TS-R4:** no proposal change.
- **TS-R5:** §6.3.
- **TS-R6, TS-R8:** no skill in TS1; inapplicable.
- **TS-R7:** `gnd.discover.type_evidence` added to `tools/gnd_layers.json`,
  lane `discover`, zero allowances. Model reads through `ModelIndex`
  (`iter_fact_types_shared`, `role_object_types`) reusing the index `propose`
  builds; the RF6 count is measured before and after implementation and
  recorded; expected growth zero.
- **Standing rule 1 (totality):** `induced_from` parsing is total over any
  JSON value: malformed exits 3 via `TypeEvidenceError`, never a traceback;
  hostile-input cases in T8 (list, number, nested object, wrong digest form,
  extra key, NaN is not reachable because the model loader refuses it).
- **Standing rule 2 (algorithm bound):** overlap counting is linear in the
  rows of each candidate per group. With G groups and C candidates it is
  O(G · Σ candidate rows), which a document controls. Bound: pair sets are
  built once per candidate (not per group) and each group's lookup is
  O(group rows); T20 is a time-bound test over a population at the 10 MiB cap
  shape (many attributes, many candidates) that must finish under a stated
  ceiling.
- **Standing rule 3 (validation order):** path checks (64, 74, 11) before any
  read, then the existing input errors, then `induced_from` (3), then writes.
  Pinned by T8 ordering against T12 (an existing evidence file with a
  malformed model exits 11, not 3, as `--out` does).
- **Standing rule 4 (one walk):** disclosure decisions (`show_values`,
  `show_digests`) are taken once in `commands/discover.py` and passed down;
  the evidence writer has no own mode lookup.
- **Standing rule 5 (one home):** the evidence format's normative home is
  `src/gnd/type-evidence.schema.json` plus one section in
  `docs/reference/discover.md`; nothing else restates it.
- **Standing rule 6 (measure):** P1 was settled by reading the shipped code,
  not argued.
- **Interchange fields in Python terms:** `signature` is canonical JSON of the
  helper's output (D5); `group` ids are evidence-local strings; no Python
  `repr` crosses the boundary.

## 5. Goal

`gnd discover MODEL POP --out P --report R --families fact-type
--type-evidence E` exits 0 and writes `E` conforming to
`src/gnd/type-evidence.schema.json`, while `P` and `R` are byte-identical to
the same run without `--type-evidence`, in every disclosure mode. Every run
without the option gives the `b733b2a` outputs, exits and stdout, except the
`discover` usage text. The focused gate exits 0.

## 6. Design

### 6.1 `src/gnd/discover/types.py` (about +35 lines)

`propose(...)` gains no parameter. `TypeProposals` gains
`groups: list[GroupRecord]`, one per group formed, in iteration order:

```python
@dataclass
class GroupRecord:
    generic: str
    attribute_sha256: str          # always computed; the writer decides emission
    status: str                    # "proposed" | "shape_match" | "multi_valued" |
                                   # "below_support" | "mixed_type" | "over_budget"
    signature: str | None          # canonical JSON of role_player_signature(players);
                                   # None when the group stopped before typing
    value_primitive: str | None
    entity_object_type: str
    support: int
    rows: int
    multi_entities: int
    multi_max: int
    exact_repeats: int
    row_ids: tuple[str, ...]       # first 32
    attribute: Any                 # raw; emitted only under show_values
    fact_type: str | None          # the proposed id, when status == "proposed"
    pairs: frozenset[tuple[Any, Any]]   # typed (entity, value) identities, in memory only
```

Spellings: the evidence's `mixed_type` corresponds to `skipped.mixed_type_groups`
and `shape_match` to the `shape_matches` list; both report spellings stay as
they are and the evidence schema enumerates its own. `drop_last` sets the
dropped groups' status to `over_budget` (it already moves their counts).
Redacted attribute roles form no groups (`:110-112` skips before grouping).

### 6.2 `src/gnd/discover/type_evidence.py` (new, about 160 lines)

```python
FORMAT = "gnd-type-evidence/1"
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024

class TypeEvidenceError(ValueError):
    """A malformed provenance.induced_from (exit 3)."""

def build_evidence(
    view: PopulationView,
    proposals: TypeProposals,
    *,
    model_sha256: str,
    population_sha256: str,
    min_support: int,
    show_values: bool,
    show_digests: bool,
    redacted_generics: list[str],
) -> dict[str, Any]: ...

def evidence_bytes(document: dict[str, Any]) -> bytes:
    """canonical_json_bytes, after trimming candidates from the tail to the cap."""
```

**(r2) Group identity.** Each group has `group: "g<n>"`, its zero-based index
in the evidence. A judgements file binds the evidence's raw-byte digest
(TS-R3), so an evidence-local id is stable for every reader of that file and
needs no digest. `attribute_sha256` is emitted only when `show_digests`
(false under `customer`, 008 CT4-Q1).

Document, literal JSON, under `internal` with `--show-values`:

```json
{"format": "gnd-type-evidence/1",
 "model_sha256": "...", "population_sha256": "...",
 "min_support": 20, "show_values": true, "show_digests": true,
 "groups": [{
   "group": "g0", "generic": "item_has_attribute",
   "attribute_sha256": "...", "value": "size",
   "status": "shape_match", "fact_type": null,
   "signature": "...", "value_primitive": "String",
   "support": 24, "rows": 24, "multi": {"entities": 0, "max": 1},
   "exact_repeats": 0, "row_ids": ["ft3#0"],
   "candidates": [{
     "fact_type": "item_has_attribute_induced_0",
     "readings": ["{Item} has induced item_has_attribute attribute 0 {AttributeValue}"],
     "roles": [{"name": "entity", "object_type": "item"},
               {"name": "value", "object_type": "attribute_value"}],
     "signature_equal": true, "rows": 24,
     "overlap": {"entities": 24, "pairs": 24},
     "origin": {"generic": "item_has_attribute", "same_attribute": true,
                "attribute_sha256": "..."}
   }]
 }],
 "redacted_generics": [],
 "truncated": 0}
```

Under `customer`: no `value`, no group `attribute_sha256`, no origin
`attribute_sha256`; `same_attribute` stays (a boolean the CLI computes by
comparing digests in memory). `show_digests` and `show_values` record what
was decided.

Candidates: every fact type in which `entity_object_type` plays a role,
excluding the generic fact type itself, in `ModelIndex` order (D1).
`readings` are `reading` and `inverse_reading` when present (model text, not
population values). `overlap.entities` counts the group's entities present
in the candidate's role(s) played by the entity type; `overlap.pairs` is set
only for binary candidates whose other role's primitive kind equals the
group's, else `null` (D2).

`origin`: `provenance.induced_from` when it is an object with exactly the
string keys `generic` and `attribute_sha256` (64 lowercase hex); `null` when
absent; anything else raises `TypeEvidenceError` (exit 3). Rendered as
`{generic, same_attribute}` plus `attribute_sha256` when `show_digests` (D7).

Cap: if the bytes exceed `MAX_EVIDENCE_BYTES`, candidates are dropped from
the last group backwards and counted in `truncated`; if the groups alone
exceed it, `DiscoveryDefect` (exit 70), argued in the record from the
population cap.

### 6.3 Disclosure

`show_values` and `show_digests` are the values `commands/discover.py:131-132`
already decides; the evidence reuses both and does no mode lookup. No new
site row: `--type-evidence` is an output of the existing `gnd discover` leaf,
so T15's case map and T26's arithmetic do not change; `disclosure.md`'s
`option` paragraph gains one sentence naming the evidence file. Redacted
generic fact types appear by id only. Candidates on a redacted entity role
still appear (ids and counts only).

### 6.4 CLI and service (about +45 lines)

- `commands/discover.py`: `--type-evidence PATH`, help "fact-type family:
  also write the evidence the judgement skills read". Without
  `--families fact-type`, 64 with the existing message extended to name it.
- `discover/service.py` `_cmd_discover`: keyword
  `type_evidence: str | None = None`. The distinct-paths check (`:378-382`)
  covers five paths when it is given (64). Symlink (74) and existing file
  (11) are checked beside `--out`'s (`:387-394`), before `discover()` runs.
  The evidence is built **after** the written-bytes `drop_last` loop
  (`:420-431`) so statuses are final, and written with `output.write` after
  `--report`.
- `discover()` returns the `TypeProposals` and the view it already holds;
  `fields` (the report) is not touched.
- `discover.schema.json`: unchanged. `src/gnd/type-evidence.schema.json`:
  new, Draft 2020-12, closed objects, `attribute_sha256` and `value`
  optional. Added to the package data the wheel already includes for
  `discover.schema.json`.
- Docs (TS1 share only): one section in `docs/reference/discover.md`, one
  release-note line. The how-to belongs to TS5.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 (plan TS-Q1) | Candidate scope | (a) every fact type the entity type plays: larger file, but a judge sees fact types with other value types; (b) equal-signature binaries only: smaller, but hides the semantic duplicates whose value type differs, the case CT-close-Q1 is about | (a) |
| D2 | Overlap for non-binary or kind-mismatched candidates | (a) `pairs: null`, entities still counted; (b) omit the candidate | (a) |
| D3 | Evidence when nothing is proposed (no `--out`) | (a) still written: the multi-valued and shape-matched groups are what the skills need; (b) only with `--out`: matches "written only when something is emitted" | (a); exit 0 |
| D4 | Write order | (a) after the report, create-once; a write failure leaves the report without evidence, exit 74; (b) staged all-or-nothing: a new staging path in discover | (a), as `--out` today |
| D5 | `signature` form | (a) canonical JSON of the helper's output; (b) a hash: opaque | (a) |
| D6 **(r2)** | Group key | (a) evidence-local `g<n>`, valid because judgements bind the evidence digest: works in every mode; (b) `attribute_sha256`: absent under `customer` since 008, so customer users could not judge at all | (a) |
| D7 **(r2)** | `origin` under `customer` | (a) `same_attribute` boolean, computed in memory, digest omitted; (b) omit `origin` under `customer`: the judge loses its strongest signal | (a) |

**Open for TS2, raised here (r2).** What `provenance.induced_from` stores
when a judged proposal is rendered under `customer`: the attribute digest in
the model is a population-derived, guessable value that 008 removed from
reports. Readings: store it anyway (the model is the caller's own file, as
the composed population is under CT-R7); store nothing under `customer` (no
`origin` for later runs); store a reference to the evidence digest and
group id (not recomputable after the population changes). It does not block
TS1, which only reads `induced_from`. Recorded as plan question TS-Q3 for
the TS2 spec; the plan is repaired at the close.

## 8. Tests and verification selection

File `tests/test_discover_type_evidence.py` unless stated. Fixture: a model
with generic `item_has_attribute`; one applied induced fact type
`item_has_attribute_induced_0` with `provenance.induced_from` naming `size`
and populated with the `size` rows; one unrelated fact type the item plays;
one equal-signature binary with disjoint data. Population: `size` (24
entities, functional), `colour` (24, functional), `tag` (24, multi-valued,
plus one exact repeated row), `rare` (3 entities), `mixed` (unvalidated
view, as CT4-C2). The fixture reaches every status but `over_budget`, which
T14b reaches with a monkeypatched budget.

| # | Case | Criterion | Expect |
|---|---|---|---|
| T1 | every group once; per-status counts equal the report's `skipped` and list lengths | C1 | 0 |
| T2 | evidence order equals family order; `g<n>` contiguous | C1 | 0 |
| T3 | `size` lists all three candidates the item plays, generic excluded | C2 | 0 |
| T4 | overlaps: `size`/induced_0 pairs 24; equal-signature disjoint 0; unrelated non-binary `pairs: null` | C2 | 0 |
| T5 | `tag`: `multi`, `exact_repeats` 1 | C1 | 0 |
| T6 | redacted attribute role: generic in `redacted_generics`, no group | C4 | 0 |
| T7 | origin read back under `internal`: digest and `same_attribute` true for `size`, false for `colour` | C3 | 0 |
| T7b **(r2)** | the same under `customer`: `same_attribute` values unchanged, no digest anywhere | C3, C4 | 0 |
| T8 | malformed `induced_from`: list, string, missing key, extra key, short digest | C3 | 3, nothing written |
| T9 | canary value: absent unset-without-flag and `customer`; present `internal` and unset-with-flag; `customer` with flag | C4 | 0 / 0 / 3 |
| T9b **(r2)** | no 64-hex attribute digest in the evidence bytes under `customer` (regex over the file) | C4 | 0 |
| T10 | `--type-evidence` without the family | C5 | 64 |
| T11 | evidence path equal to `--out`, `--report`, MODEL, POPULATION | C5 | 64 |
| T12 | existing evidence file, also with a malformed model (order) | C5, rule 3 | 11, nothing written |
| T13 | symlinked evidence path | C5 | 74 |
| T14 | small monkeypatched evidence cap trims candidates and counts | C7 | 0, `truncated` > 0 |
| T14b | written-bytes `drop_last` path: dropped groups carry `over_budget` | close R2-1 | 0 |
| T15 | `tests/test_rf1_cli_pins.py`: `discover` help and usage goldens re-pinned; diff is the new option only | C6 | gate |
| T16 | `--out` and `--report` bytes equal with and without the option, every fixture, three modes | C6 | equal |
| T17 | CT4 parity script (`evidence/CT4/capture_parity.py`) over its cases and the IK4 table, without the option | C6 | equal to `b733b2a` except the usage line |
| T18 | every written evidence validates against the schema | all | valid |
| T19 | nothing proposed: evidence still written, no `--out` | D3 | 0 |
| T20 | time bound: many attributes and candidates near the population cap | rule 2 | under the stated ceiling |

### Selection ledger

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| Direct TS1 cases T1..T14b, T16, T18..T20 | run | `uv run pytest -q tests/test_discover_type_evidence.py` exit 0 | `discover/types.py`, `type_evidence.py`, `service.py`, `commands/discover.py`, the schema, the fixture | every new branch has a case | any change to those files |
| Plan §9 TS1 row (CT4 gate) | run | `uv run pytest -q tests/test_discover_fact_type_family.py tests/test_discover.py tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py` exit 0 | as above plus RF1 goldens, `tools/gnd_layers.json`, `disclosure.md` | the existing family, pins, layers, RF6 and disclosure consumers of the changed modules | changes to discover, evolve shape matching, disclosure, layer map |
| Package data | run | `uv run pytest -q tests/test_schema_sync.py` exit 0 | the new schema's packaging | the schema ships | packaging changes |
| Parity T17 | run | the CT4 capture script, compared with `evidence/CT4/parity-after.json` and the 008 rulings evidence | discover CLI | TS-R1 | any discover change |
| Docs | run | `zensical build --strict` and `uv run python tools/check_docs.py site` exit 0 | `docs/reference/discover.md`, release notes | the TS1 doc section | doc edits |
| Broad historical lanes (`evidence or census`) | cadence | milestone close or explicit owner request | n/a | outside TS1's impact closure | owner request |

### Implementability sweep

| Requirement | Can some implementation meet it? |
|---|---|
| Evidence after final statuses | Yes: `_cmd_discover` holds `types_` after the loop at `:420-431`. |
| `same_attribute` under `customer` | Yes: digests are computed in memory (`propose` computes `digest` for every group) and compared before emission. |
| Overlap counts with typed identity | Yes: `gnd.discover.support.identity` is the identity `propose` already uses. |
| Unchanged `--out`/`--report` | Yes: the evidence is built from state after both are serialised; no field in `fields` changes. |
| Time bound under the cap | Yes, with per-candidate pair sets built once (rule 2 bullet). |

## 9. Out of scope for TS1

Judgements, rendering and writing `provenance.induced_from` (TS2, with
TS-Q3); skills (TS3, TS4); the how-to (TS5); a Python API (plan TS-D8);
salting digests (settled by 008).

## 10. Size

Estimate: about 240 source lines (types +35, type_evidence 160, CLI and
service 45), a 130-line schema, and about 500 test lines.

## 11. Approval instrument

This prose (proposed). The phase is a serialized format, for which the
review-convergence reference defaults to corpus-first; the argument for
prose is that the format is read only by TS2 and the skills, both in this
milestone, and T18 validates every written file. The owner may instead ask
for a fixture corpus with narrated expected evidence first. Optional spec
review panel: proposed omitted.
