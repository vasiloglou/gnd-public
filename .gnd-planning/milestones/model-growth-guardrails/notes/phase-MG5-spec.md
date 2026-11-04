# Phase MG5: unattended model-from-text

**Status: r1, delegated approval (auto=true) 2026-11-04 `(d1)`.** Implementation
follows this approval and the MG4 record.

`(d1)` **Delegated approval (auto=true)**, 2026-11-04. Authorization: the
owner's "process-milestone model-growth-guardrails auto" in this session; an
agent ruling under that delegation, not the owner's personal reading.
Approved bytes: SHA-256
`91d2657027800db1d64c41a72cc28b9d353936cfda6a12af2e118105f165e566` (before
this tag), after the implementability sweep: `_iter_constraints` covers
inline and top-level constraints; the induced provenance branch is closed
(D3 needed); `common-sense` already requires `library_entry` at layer 1 (D4);
`gnd.anchors` is layer `infrastructure`, importable from layer `model`; of
the gate's optional files only `tests/test_induced_provenance.py` exists.
The corpus re-measure (T4's discriminating rows) found 349 model files with
`source.mode` one-shot 271, guided 47, mvp-fast 2, none 29 and none
unattended; 163 one-shot files carry `confirmed` or `user-supplied` (the
plan's 112 and 16 counted a narrower set). Rulings: D1 (b) prose, no spec
panel; D2 to D7 (a). Budget: about 200 source, 450 test lines; no paid calls.
Compatibility: every model without the mode validates unchanged (MG-R1); one
new `gnd validate` option; no exit or version change. Diff review: one local
reviewer agent.

## Provenance

- Plan: [model-growth-guardrails-plan.md](model-growth-guardrails-plan.md) r3,
  approved `(a1)` 2026-11-03: §2.5, §3, §4 MG5, §9 MG5 row, §10 MG-D8,
  D9, D10, D16, D18.
- Source: [issue #74](https://github.com/vasiloglou/gnd-public/issues/74)
  (GR-T11).
- Inspection baseline: `9b069e2`. MG3 and MG4 land first on the same branch
  and touch neither validation nor the schema.
- Prior records: MG1, MG2 ([003-phase-MG2.md](../003-phase-MG2.md)), MG3,
  MG4. None leaves an open question on validation.
- Authority: the owner's `process-milestone model-growth-guardrails auto`
  (2026-11-04). **This spec's bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #74, plan O13 | Unattended mode: every fact and constraint cites a span | U4, U5, U6; T2 |
| #74, plan O14 | Nothing auto-confirmed; sources and the `deontic` default kept | U2, U8; T2 |
| #74, plan O15 | Header records the mode, the absence of a reviewer, source digests | U1; T2 |
| #74, plan O16 | Validation refuses `confirmed` or `user-supplied` in this mode | U2, U3; T2 |
| Plan §4 MG5-C1 | `$defs.source_span` in the schema and its twin (`tests/test_schema_sync.py` passes; the skill copy is canonical, so the edit lands there first and is copied); the `source` keys of §2.5 | Schema; T1 |
| Plan §4 MG5-C2 | One refusing case per branch in §2.5's table, each asserting its `semantic:unattended-*` id and each passing when the mode is absent; an unattended model meeting every rule exits 0 | T2, T2b, T2c |
| Plan §4 MG5-C3 | `gnd validate --document`: a matching span (0); an excerpt mismatch (3); `end` past the document (3); a document not declared (3); combining characters (0 with code-point offsets, 3 with byte offsets) | T3 |
| Plan §4 MG5-C4 | Recorded before/after table: every corpus model validates with identical output; re-measure the discriminating rows | T4 |
| Plan §4 MG5-C5 | The skill's Unattended section, the representation reference, `EXPECTED_SKILL_FILES` if a file is added | Docs; T7 |
| Plan §9 MG5 row | U1–U8; re-hash; corpus parity; schema twin; the named gate files | Verification selection |
| Plan MG-R1 | Validation results unchanged for every model not declaring the mode | Rules gated on the mode, appended last; T4 |
| Plan MG-R2 | One rule family, one walk | `_rule_unattended` in `_validation.py`; T2 |
| Plan MG-R3 | Not applicable: no document is handed to a gate; `--document` re-hashes bytes the caller supplies |
| Plan MG-R4 | Not applicable: the mode gates by design |
| Plan MG-R5 | `gnd validate --document` is a new option on an existing leaf (`value-free`); messages name digests, offsets and paths, never excerpt text | T5 |
| Plan MG-R6 | Layering: `_validation.py` (layer `model`) imports `gnd.anchors.canonical_document_text` (layer `infrastructure`); no new module; rules read the parsed document dict, not `Model.fact_types`, so the RF6 counted policy gains no row | T6 |
| Plan MG-R7 | Anonymity | T8 |
| Plan MG-R8 | Provenance never overstated: the mode refuses `confirmed` | U2 |
| Plan §10 MG-D8, D16, D18 | Spans for elements, sample rows and every constraint source except `common-sense` | Ruled `(p1)` G and `(a1)` |
| Plan §10 MG-D9 | Optional re-hash | `--document`, repeatable, optional |
| Plan §10 MG-D10 | A new Unattended skill mode; One-shot unchanged | Docs |
| Plan §5 | Skill text; schema twin; RF1 goldens for `gnd validate` | Docs; T7, T9 |
| Plan §6 | Breaking existing models; One-shot confused with Unattended; spans citing absent documents; RF1 drift | T4; docs contrast; U7 and T3; T9 |
| Plan §7 | Running the LLM inside GND; spans on `common-sense` constraints | Out of scope |

## Standing rules bound to this phase

1. **Totality:** `_rule_unattended` runs inside `semantic_validate`, which
   turns an escaped exception into `internal:rule-raised`; the rule still
   guards every shape itself (a non-dict `source`, a non-list `documents`, a
   span with a boolean `start`, a non-integer `row`). T2d feeds hostile
   shapes and asserts no `internal:rule-raised`.
2. **Input cap bounds the algorithm:** one walk over object types, fact
   types, constraints and provenance-bearing elements; declared documents in
   a set; sample-row coverage by one set per fact type. T10: 2,000 fact types
   with 50 rows each, under 5 s.
3. **Validation order:** the family is appended after the IK2 block of
   `_SEMANTIC_RULES`, so every existing model's issue order is unchanged; within
   the family, issues come in rule order U1..U8, then path order.
4. **One walk:** one function emits every `semantic:unattended-*` issue.
5. **One home:** the rule table is normative in
   `gnd-orm-core/references/representation-format.md` (new "Unattended
   source" section); the skill cites it.
6. **Measurement over argument:** T4 is a recorded digest table over every
   corpus model.

## Goal

`gnd validate MODEL` exits 3 with the named `semantic:unattended-uN` issue for
each §2.5 branch when `source.mode` is `unattended`, and exits 0 on an
unattended model meeting every rule. `gnd validate MODEL --document PATH ...`
additionally exits 3 when a supplied document is undeclared, or a span over it
ends past its end or has a different excerpt digest. Every corpus model not
declaring the mode validates with byte-identical output to `9b069e2`.

## Design

### Schema, both copies (about +25 lines each)

```json
"source_span": {
  "type": "object",
  "additionalProperties": false,
  "required": ["document_sha256", "start", "end", "excerpt_sha256"],
  "properties": {
    "document_sha256": {"$ref": "#/$defs/sha256_hex"},
    "start": {"type": "integer", "minimum": 0},
    "end": {"type": "integer", "minimum": 1},
    "excerpt_sha256": {"$ref": "#/$defs/sha256_hex"}
  }
}
```

The induced provenance branch is **closed** (`additionalProperties: false`,
keys `induction`, `reviewed_in`), so MG-D16's spans on `induced` constraints
need `"spans": {"type": "array", "items": {"$ref": "#/$defs/source_span"}}`
added there (D3). Every other `provenance` is open, so the rule checks span
shape itself (U7). Edited in `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`
first, then copied byte-for-byte to `src/gnd/schema/orm-meta.schema.json`.

### `src/gnd/model/_validation.py` (about +150 lines)

```python
UNATTENDED_MODE: Final = "unattended"

def _rule_unattended(doc: dict[str, Any]) -> list[ValidationIssue]
def unattended_span_issues(doc: dict[str, Any], documents: Mapping[str, bytes]) -> list[ValidationIssue]
```

`_rule_unattended` returns `[]` unless `doc["source"]` is a mapping with
`mode == "unattended"`. Then, with rule ids spelled exactly
`semantic:unattended-u1` … `semantic:unattended-u8`:

| # | Check | Path |
|---|---|---|
| U1 | `source.reviewer == "none"`; `source.documents` a non-empty list of `{sha256: 64 lowercase hex, label: non-empty string}` with no other key | `$.source.reviewer`, `$.source.documents[i]` |
| U2 | no provenance-bearing element (`_iter_provenance_bearing`: constraints, operations, obligations) has `status: confirmed` | element path |
| U3 | no constraint has `source` `explicit` or `user-supplied` (D2: emitted, beside U2 and `semantic:status-source`) | constraint path |
| U4 | every object type and fact type has `provenance.spans`, a non-empty list | `$.object_types[i]`, `$.fact_types[i]` |
| U5 | every constraint whose `source` is not `common-sense` has `provenance.spans`, a non-empty list (`common-sense` keeps the schema's required `library_entry`) | constraint path |
| U6 | a fact type with `sample_population` rows has `provenance.sample_spans`, a list of `{row, span}` whose `row` values cover `0 … n-1` | `$.fact_types[i].provenance.sample_spans` |
| U7 | every span in U4–U6 positions is a `source_span`: the four keys, no other, digests 64 lowercase hex, integers (not booleans), `0 ≤ start < end`, `document_sha256` a declared document | span path |
| U8 | no constraint is `alethic` with `source` `sample`, `llm-inferred`, `common-sense` or `induced` | constraint path |

All issues are errors. `unattended_span_issues` is the `--document`
re-hash: for each supplied raw document, its SHA-256 must be declared
(`unattended:document-undeclared`); for each valid span naming it,
`text = canonical_document_text(raw)`, `end ≤ len(text)`
(`unattended:span-out-of-range`), and `sha256(text[start:end].encode("utf-8"))
== excerpt_sha256` (`unattended:excerpt-mismatch`). Units per §2.5: code
points of the NFC text; `documents[].sha256` over raw bytes.

### `src/gnd/commands/checking.py` and `src/gnd/api.py` (about +40 lines)

`gnd validate --document PATH` (repeatable, `action="append"`).
`_cmd_validate(..., documents=())` reads each path (`EXIT_NO_INPUT` 66 when
missing, `EXIT_IO` 74 when unreadable, as other inputs), runs validation as
today, and only when validation exits 0 calls `unattended_span_issues`; any
issue exits 3 through the same issue printing and JSON payload as a
validation issue. A model not in unattended mode declares no documents, so
any `--document` is undeclared (3).

### Docs and skill (about 90 lines)

`representation-format.md` "Unattended source" (normative table, units, the
re-hash); `gnd-model-from-text/SKILL.md` a new Unattended mode beside
One-shot (MG-D10): GND validates, the host runs the LLM, `scripts/validate_model.py`
is schema-only so the mode routes to `gnd validate`; `docs/reference/cli.md`;
an Unreleased note.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Approval instrument | (a) corpus-first: the default for a validation predicate per `review-convergence.md`; (b) this prose: the U-table enumerates every branch and its case, each a one-key mutation of one conforming fixture | (b), the burden of argument noted: each branch's fixture is a one-key edit of the conforming model and T2 asserts the exact rule id |
| D2 | U3 | (a) emit it: a direct, falsifiable rule id for #74's "refuse user-supplied", at the cost of a duplicate issue beside U2 / status-source; (b) the plan's reading: a reserved id with no case | (a): emitting adds a case that can fail; the plan's "no separate case" was a cost argument, not a contract |
| D3 | `spans` on `induced` constraints | The induced provenance schema is closed. (a) add `spans` to it (additive; no existing model carries the key, T4); (b) refuse `induced` in this mode (MG-D16 (b), already ruled against) | (a) |
| D4 | `common-sense` without `library_entry` (U5's fifth branch) | The schema already requires `library_entry` for `common-sense`, so the branch is pre-empted at layer 1 with exit 3. (a) record it as pre-empted with a case asserting the schema issue; (b) duplicate the check in U5 | (a) |
| D5 | `--document` on a model without the mode | (a) every supplied document is undeclared: exit 3; (b) ignored | (a) |
| D6 | Spans on operations and obligations | Not in §2.5. (a) out of scope; U2 still refuses `confirmed` on them | (a) |
| D7 | Re-hash failure exit | (a) 3, like a validation issue; (b) a new band | (a) |

## Tests

New file `tests/test_unattended_mode.py`. Fixture: a conforming
`tests/fixtures/unattended/conforming.orm.yaml` (two object types, two fact
types, one with two sample rows, one `llm-inferred` deontic constraint, one
`common-sense` constraint, one `sample` constraint), plus its document
`tests/fixtures/unattended/source.txt` (with a combining character).

| # | Case | Expected |
|---|---|---|
| T1 | `tests/test_schema_sync.py`; the conforming fixture against both schema copies; a span with an extra key, a negative `start`, a 63-hex digest fails layer 1 where provenance is closed (induced) | exit 0 / refused as stated |
| T2 | One case per branch, each a one-key edit of the conforming model, asserting the exact rule id and exit 3: U1 ×5 (reviewer absent, not `none`, documents absent, empty, malformed entry); U2 ×2 (constraint, operation); U3 ×2 (`explicit`, `user-supplied`); U4 ×2 (object type, fact type); U5 ×4 (`sample`, `llm-inferred`, `induced`, `imported`); U6 ×2 (no `sample_spans`; two rows, one covered); U7 ×2 (undeclared document; `start ≥ end`) plus malformed span; U8 ×4 (one per source) | as stated |
| T2b | The same edit with `source.mode` removed (or `one-shot`) | no `semantic:unattended-*` issue; the exit equals the model's exit without the family |
| T2c | The conforming model | exit 0 |
| T2d | Hostile shapes in unattended mode (`source.documents: 3`, `spans: "x"`, `start: true`, `row: "0"`) | named U-issues, no `internal:rule-raised` |
| T2e | D4: `common-sense` without `library_entry` | exit 3 with the schema issue (pre-empted) |
| T3 | `gnd validate --document`: matching (0); excerpt mismatch (3); `end` past the document (3); undeclared document (3); combining characters: code-point offsets (0), the same slice in byte offsets (3); a missing path (66); a model without the mode (3) | as stated |
| T4 | Before/after `(r1-R)`: `gnd validate --format json` over every `*.orm.yaml` / `*.orm.json` under `tests/fixtures`, `examples` and `src/gnd/skills` at `9b069e2` and after; `evidence/MG5/parity-{before,after}.json`; re-measured counts of `source.mode` values and one-shot models with `confirmed`/`user-supplied` recorded as the discriminating rows | byte-identical |
| T5 | Disclosure: a document line never appears in `--document` output; `tests/test_disclosure_mode.py`, `test_disclosure_docs.py` | exit 0 |
| T6 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py` | exit 0 |
| T7 | Skill: `tests/test_packaged_skills.py`, `tests/test_skill_prose_sync.py`; docs gates | exit 0 |
| T8 | Anonymity scan | 0 matches |
| T9 | RF1 goldens for `gnd validate` help and exit probe; `MANIFEST_SHA256` | exit 0 |
| T10 | 2,000 fact types × 50 rows in unattended mode | under 5 s |
| T11 | Mutation controls: (i) the mode gate removed kills T2b; (ii) byte offsets instead of code points kill T3's combining case; (iii) U6 checking only the first row kills its case | each mutant fails its case |

### Verification selection

| Obligation | Disposition | Command | Invalidation |
|---|---|---|---|
| Plan §9 MG5 row | run | `uv run pytest -q tests/test_unattended_mode.py tests/test_schema_sync.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_model_validation.py tests/test_model_v2.py tests/test_model_semantic.py tests/test_induced_provenance.py tests/test_imported_provenance.py`, the last three where present, exit 0 | `_validation.py`, schema copies, `commands/checking.py` | any change |
| Impact closure | run | plus `tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_public_api.py tests/test_rf3_core.py tests/test_rf4_peripheral.py` and every test file that loads the schema (measured at implementation) | same |
| Docs | run | `tools/run_tutorials.py`, `zensical build --strict`, `tools/check_docs.py site` | docs |
| Parity | run | T4 | corpus |
| Broad lanes | cadence | on explicit owner request | — |

## Out of scope for this phase

Running the LLM; spans on `common-sense` constraints (MG-D18); spans on
operations and obligations (D6); verifying `documents[].label`; fetching
documents.

## Size

About 200 source lines (plan: 200), 450 test lines, about 90 lines of skill
and reference text.

## Approval instrument

This prose (D1 (b)). No spec review panel.

## Implementation findings

Recorded as found, 2026-11-04. The approved text above is not edited.

- **F1, a registration pin.** `tests/test_model_validation.py::test_normative_semantic_rule_inventory_matches_registration_order`
  requires every rule id literally in the rule's source and in the Layer 2
  table of `representation-format.md`, in registration order. The helpers
  take their rule ids as keyword arguments from `_rule_unattended`, the pin
  lists `_rule_unattended` under its multi-id exceptions, and the table
  gains eight rows.
- **F2, a link-count pin.** `EXPECTED_RELATIVE_LINK_COUNT` moves 211 to 212:
  the Unattended section cites `representation-format.md` once more.
- **F3, issue order.** Standing rule 3 says "then path order" within the
  family; the implementation sorts stably by rule number and keeps walk
  order within a rule (U2 provenance-bearing walk, then the element walks).
  T2f pins rule order only.
- **F4, fixture.** The fixture's accents are precomposed, so it separates
  byte and code-point offsets; the combining-character (NFD) branch is the
  separate `test_t3_a_decomposed_document_normalizes_to_the_same_offsets`.
- **F5, RF6 and RF1.** No counted read; dynamic census successor
  `evidence/MG5/dynamic-query-successor.json` (five rows in
  `commands/checking.py`). `gnd validate` goldens captured under py311,
  py313 and py314, byte-equal.
- **F6, parity.** 322 of 322 pre-existing models byte-identical; the after
  table adds one row, the conforming fixture (exit 0).

## Review dispositions

One reviewer is one reviewer:
[phase-MG5-claude-review.md](phase-MG5-claude-review.md), verdict
approve-with-fixes, nothing blocking; probes in `evidence/MG5/review-probes/`.
The reviewer also re-captured parity from a `git archive 9b069e2` tree (0
differences) and flagged that in-place mutants can be fooled by stale
bytecode; every phase's mutant table (MG3, MG4, MG5) was re-run with
`PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared, all killed.

- **R-F1, fixed.** `fullmatch` for digests; regression and mutant M9.
- **R-F2, accepted as the one MG-R1 exception.** D3's `spans` on induced
  provenance is not mode-gated: a model without the mode whose induced
  constraint carries `spans` exited 3 at `9b069e2` and now exits 0. No corpus
  model carries the key (parity unchanged); the reference page states the
  exception.
- **R-F3, fixed.** A `--document` refusal keeps the model's warnings in JSON
  and text; regression and mutant M11.
- **R-F4, fixed.** A document over 10 MiB exits 3 naming the cap, before any
  hash; regression.
- **R-F5, fixed.** `sample_spans` rows must name each existing row once, and
  are checked on a fact type without rows; regressions and mutant M10.
- **R-F6, fixed.** Spans a `common-sense` constraint carries are checked.
- **R-F7, residual (MG5-Q1).** Re-hashing costs about 6.4 ms per
  full-length span over a 10 MiB document; T10 times the rule, not
  `--document`.
- **R-F8, fixed.** `unattended:document-unreadable` is documented and its
  message no longer borrows the anchor prefix.
- **R-F9, fixed in docs.** Documents are read after the model validates; 66
  and 74 for missing and unreadable paths are documented as they behave.
- **R-F10, residual (MG5-Q2).** The schema's `source` stays free-form; the
  semantic rule is the one home of the header rule.
- **R-F11, documented.** Spans over a declared, unsupplied document are not
  re-hashed; no count is reported (MG5-Q3).
- **R-F12, fixed.** The skill says every constraint this workflow emits stays
  `deontic`; an `imported` alethic constraint is outside U8 by §2.5.
- **R-F13, fixed in part.** T2b's exit is asserted
  (`test_review_f13_...`); the path-order and fixture points are F3 and F4.
- **R-F14, accepted.** Collection-level non-list shapes reach the rule only
  through a direct `semantic_validate` call (layer 1 refuses first), which
  names the raise `internal:rule-raised` as for about 20 existing rules; the
  rule's own loops now walk lists only.

## Open questions raised at implementation

| ID | Question | Target |
|---|---|---|
| MG5-Q1 | `--document` re-hash cost per full-length span | milestone close |
| MG5-Q2 | Schema for the unattended `source` keys | milestone close |
| MG5-Q3 | Report the count of spans over unsupplied documents | milestone close |
