# Phase CT4: fact-type proposals in discover

**Status: r1, delegated approval (auto=true) 2026-11-04 `(d1)`.**
Implementation follows this approval and the CT3 record.

`(d1)` **Delegated approval (auto=true)**, 2026-11-04. Authorization: the
owner's "Yes, run it auto" in this session, invoking `process-milestone
composition-and-type-induction auto`. An agent ruling under that delegation,
not the owner's personal reading. Approved bytes: SHA-256
`c5e4d509e0329c8de211a49ff55b878a5a841f459b573715ab027f2358eedfe3` (before this tag), after the implementability sweep at `4584415`:
`gnd.refscheme.role_player_signature` (MG3), the additive policy (MG2),
`gnd.disclosure.values_allowed`, `support.identity` and
`docs/reference/discover.md` exist; `_cmd_discover` already maps
`ArtifactError` to 66/74 (IKE-Q3 D1-A), so O16 is a pin, not a change.
Rulings: D1 (a), D2 (a) (re-argues the plan's "co-proposed" clause on its
real cost, as the plan gate allows), D3 (a), D4 (a). Budget: about 260
source, 30 schema and 450 test lines; no paid calls. Compatibility: without
`fact-type`, every discover output unchanged (CT-R1, T6); `gnd discover`
moves from every-mode to a `site` disclosure row (CT-D13). Diff review
instrument: one local reviewer agent.

## Provenance

- Plan: [composition-and-type-induction-plan.md](composition-and-type-induction-plan.md)
  r3, approved `(a1)` 2026-11-03: §2.4, §3, §4 CT4, §9 CT4 row, §10 CT-D7,
  CT-D8, CT-D9 (ruled `(p1)` (b')), CT-D10, CT-D13 (ruled `(a1)` (a)).
- Source: [issue #77](https://github.com/vasiloglou/gnd-public/issues/77)
  (GR-T14).
- Prerequisites: MG2 (additive policy) and MG3 (`role_player_signature`,
  shape report), merged with PR #83 at `f6d02e9`; CT4 needs nothing from
  CT1 to CT3.
- Inspection baseline: `a2e44f8` plus CT1 to CT3 on the branch.
- Authority: the owner's "Yes, run it auto" (2026-11-04). **This spec's
  bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #77, plan O6 | Propose a fact type from a declared generic fact type's rows sharing an attribute name with a consistent value type, above a support threshold | family `fact-type`; T1, T2 |
| #77, plan O7 | Report the rows that would migrate | migration report; T3 |
| #77, plan O8, CT-R5 | Emit `induced`, `proposed`, `deontic`; nothing moves; admission is a reviewed apply | envelope; T4 |
| Plan CT-R6 | No population value in the model or report without a ruling | opaque ids; digests; `--show-values` per CT-D13; T3 |
| Plan CT-R7, CT-D13 (a) | `gnd discover` becomes a `site` leaf deciding `--show-values` with `values_allowed`; every other discover output unchanged in every mode | disclosure table; T3 |
| Plan CT-R1 | Without the family, every discover output and the seven-family default are unchanged | T6 table |
| Plan O15 | Induced alethic proposals only warn | the family emits deontic only |
| Plan O16 (IKE-Q3) | Discover lets a raw `ArtifactError` escape | already resolved at `a2e44f8` (`_cmd_discover` maps it to 66/74, "IKE-Q3 D1-A"); T7 pins it |
| Plan CT-R8 | Homes, layering, RF6, anonymity | T8 |

## Standing rules bound to this phase

1. **Totality:** an invalid `provenance.generic` declaration is exit 3
   naming the fact type, never a traceback.
2. **Input cap bounds the algorithm:** grouping is one pass over each generic
   fact type's rows into a dictionary keyed by the attribute value's identity,
   so the family is linear in rows; it adds its row visits to discover's
   `work` counters and ceiling.
3. **Validation order:** generic declarations are checked after the model and
   population load and before any candidate is generated.
4. **One walk:** one pass groups rows; support, type consistency and the
   migration rows read that grouping.
5. **One home:** `docs/reference/discover.md` gains the family's section; the
   report schema describes the new optional key.
6. **Measurement over argument:** CT-R1 is a recorded before/after table
   over the discover fixtures (T6).

**Plan rules:** CT-R1 (T6), CT-R2 to CT-R4 not applicable (no anchors or
composition), CT-R5 (T4), CT-R6 (T3), CT-R7 (T3, disclosure table), CT-R8
(T8).

## Goal

`gnd discover MODEL POP --families fact-type ...` on a model with a declared
generic fact type proposes, for every attribute value whose rows cover at
least `--min-support` distinct entities with one primitive, an `ADD` of a
binary fact type (entity, value) with an opaque id and a placeholder reading,
plus a deontic induced uniqueness on its entity role. The proposal passes
`gnd evolve preview --policy additive`. The report's new `fact_type_proposals`
key lists, per proposed fact type, the opaque row ids that would migrate and
the attribute value's SHA-256; the raw value appears only as `values_allowed`
decides. Without `fact-type` in `--families`, every output is byte-identical
to `a2e44f8` (T6). The CT4 gate exits 0.

## Design

### Declaring a generic fact type (CT-D7 (a))

```yaml
- id: item_has_attribute
  reading: "{Item} has attribute {AttributeName} with value {AttributeValue}"
  roles: [...]
  provenance:
    generic: {entity: item, attribute: name, value: value}
```

`entity`, `attribute` and `value` name three distinct roles of a ternary fact
type. Anything else (a missing or extra key, an unknown or repeated role, a
non-ternary fact type) is exit 3: `fact type <id>: invalid generic
declaration`. A fact type without the declaration is never grouped, whatever
its shape (T1).

### Family `fact-type` (`src/gnd/discover/types.py`, new, about 170 lines)

Opt-in: `FAMILIES` keeps its seven members and the default; the parser accepts
`fact-type` in `--families` as an eighth name. For each eligible generic fact
type:

1. If `(generic, attribute)` is a redacted role, the fact type is skipped and
   counted (`skipped.redacted_attribute_roles`, CT-R6).
2. Group rows by the attribute value's checker identity (`support.identity`).
3. A group is a candidate when its **support**, the number of distinct entity
   identities, is at least `--min-support` (default 20, at least 1; CT-D10),
   and every value-role cell has the same primitive identity kind. A mixed
   group is counted (`skipped.mixed_type_groups`) and not proposed.
4. The proposed fact type, numbered `n` from 0 in the order groups are first
   seen, is `<generic>_induced_<n>` with roles `entity` (the generic entity
   role's object type) and `value`. Its value object type is the generic value
   role's object type when that type's primitive equals the group's; otherwise
   a new value type `<generic>_induced_<n>_value` with that primitive is added.
   The reading is the placeholder `{Entity} has induced attribute <n> {Value}`
   written with the two object types' names (CT-D9 (b')): no population value.
5. **Shape check (MG3):** when an existing fact type has the same role-player
   signature (`gnd.refscheme.role_player_signature`), the group is reported
   under `fact_type_proposals.shape_matches` with that fact type's id, and not
   proposed. Groups proposed in the same run share a signature by
   construction (same entity, same primitive), so they are not compared with
   each other (D2).
6. The induced envelope (CT-D8 (a)) sits on a uniqueness constraint added on
   the new fact type's entity role: `source: induced`, `status: proposed`,
   `modality: deontic`, and `provenance.induction` as the other families write
   it, with `support` = entities with exactly one row in the group over all
   entities in the group, and `examples`/`counterexamples` as opaque row ids.

The operations are `ADD` object type (when needed), `ADD` fact type and `ADD`
constraint, in group order, appended to the other families' operations in one
schema-3 proposal. Nothing moves (CT-R5).

### Report (`gnd-discover/1`, one optional key)

With the family, the report gains `fact_type_proposals`:

```json
{"min_support": 20,
 "proposed": [{"fact_type": "item_has_attribute_induced_0", "generic": "item_has_attribute",
               "attribute_sha256": "...", "support": {"numerator": 24, "denominator": 25},
               "rows": ["ft3#0", "ft3#7"], "value": "colour"}],
 "shape_matches": [{"generic": "item_has_attribute", "attribute_sha256": "...", "existing": "item_has_colour"}],
 "skipped": {"redacted_attribute_roles": 0, "mixed_type_groups": 0, "below_support": 3}}
```

`rows` are opaque ids `ft<position of the generic fact type in the model>#<row
index>`. `value` is present only when `values_allowed(--show-values)` is true:
with the flag under an unset mode, always under `internal`; under `customer`
the flag is refused with `DisclosureRefused` (exit 3). Without the family the
key is absent, so the report bytes are unchanged (T6).
`src/gnd/discover.schema.json` gains the optional key.

### CLI, disclosure

- `--families` accepts `fact-type`; `--min-support N` (default 20) and
  `--show-values` are new; `--show-values` or a non-default `--min-support`
  without `fact-type` is a usage error (64).
- `gnd discover` moves from the every-mode rows to a `site` row deciding
  `--show-values` (CT-D13 (a)); `test_disclosure_mode.py`'s T26 arithmetic and
  `docs/reference/disclosure.md` follow.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Value object type | (a) reuse the generic value role's type when its primitive matches, else add one; (b) always add one: duplicates every reused type and defeats the shape check | (a) |
| D2 | Shape check among co-proposed groups (plan §2.4 "existing or co-proposed") | (a) only against existing fact types: groups of one generic share entity and primitive by construction, so the co-proposed comparison would let one group per primitive through, against O6; (b) as the plan says | (a), re-argued on its real cost as the plan gate allows |
| D3 | Where the migration report lives | (a) an optional key in the discovery report; (b) a third output file: another path to refuse, collide and document | (a) |
| D4 | Support numerator | (a) entities with exactly one row in the group (the uniqueness the envelope sits on); (b) all rows: not a uniqueness measure | (a) |

## Tests

New file `tests/test_discover_fact_type_family.py` unless noted. Fixture: a
generic `item_has_attribute` over 25 items, attribute `colour` on 25 items
(one item twice), `size` on 19, `weight` on 20 with one non-numeric value.

| # | Case | Expected |
|---|---|---|
| T1 | Declaration: valid; each invalid form; an undeclared ternary with the generic shape and high support | ok; exit 3 naming the fact type; no proposal |
| T2 | Grouping: `colour` (25) proposed; `size` at 19 below the default 20 and proposed at `--min-support 19`; a group of 20 rows over 19 entities not proposed; `weight` mixed, counted | as stated |
| T3 | Canary: attribute and value strings absent from the proposal bytes and the report without `--show-values` (unset mode); `value` present with the flag; present under `internal` without it; `customer` with it exits 3 with the `DisclosureRefused` message | as stated |
| T4 | The proposal passes `gnd evolve preview --policy additive` (exit 0); the uniqueness carries `induced`/`proposed`/`deontic` and the support | as stated |
| T5 | Shape: an existing binary fact type over (Item, the value type) makes that group a `shape_matches` entry while another group in the run is proposed; redacted attribute role skipped and counted | as stated |
| T6 | Before/after: every discover fixture run without the family at `a2e44f8` and after, digests of report, proposal, stdout and exit in `evidence/CT4/parity-*.json` | identical |
| T7 | A reference population path that cannot be read (IKE-Q3) | 66 or 74 as at `a2e44f8`, no traceback |
| T8 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py`; anonymity scan | exit 0 |
| T9 | Pins: RF1 goldens for `discover --help` and its exit probe and `tree.json`; `test_disclosure_mode.py` T26; `discover.schema.json` validation of a family report | updated and passing |

### Verification selection

```
uv run pytest -q tests/test_discover_fact_type_family.py $(ls tests/test_*discover*.py) \
  tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py \
  tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py \
  tests/test_disclosure_docs.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py \
  tests/test_gnd_arch.py tests/test_conformance_payload.py
```

plus T6's recorded table.

## Out of scope for this phase

- Object types, relation names (plan §7, `(r1-U)`); moving rows; structural
  detection of generic fact types; constraints beyond the one uniqueness.

## Size

About 260 source lines, 30 schema lines, 450 test lines.
