# Phase CT1: several anchors per fact role

**Status: r3, awaiting the owner's plan gate and this spec's gate.**
Plan approval and this spec's gate are both still open. No code is written
before the gate.

## Provenance

- Plan: [composition-and-type-induction-plan.md](composition-and-type-induction-plan.md)
  r2, §2.1 and §4 CT1.
- Source: [issue #73](https://github.com/vasiloglou/gnd-public/issues/73)
  request 3 (GR-T10).
- Inspection baseline: `1446f90`.
- r1 was read in plan review round 1 as SHA-256
  `51dd694817fee77650a1154c70865dfad0dd29ee7f339fa54a38c9813a035bb0`; see the
  [round-1 disposition](../../model-growth-guardrails/notes/plan-review-r1-disposition.md).
  r2 applies themes H, I, O, P, Q, R, W at the owner's direction `(p1)`
  (quoted in the predecessor plan's header). r2 was read in the confirmation
  round as SHA-256
  `0a31dad55a52c18a8b498c9d02e46d08fdad759d425de50e9ec303bc7f56a38b`; see the
  [round-2 disposition](../../model-growth-guardrails/notes/plan-review-r2-disposition.md).
  r3 applies theme R2-F (and R2-H's inventory rows) under the declared stop
  rule, with no further round. **r3 bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Issue #73.3 | One fact role may be supported by more than one span | v2 parse; T1 |
| Plan CT-R1 | Every v1 sidecar parses, binds and checks as at `1446f90` | version dispatch; T6, T7 |
| Plan CT-R2 | Several anchors add evidence; none proves the fact | reference page wording; no new verdict |
| Plan CT-D2 | Every anchor must bind | evaluation loop; T3, T4 |
| Plan CT-D12 | One document per sidecar in v2 | same top-level keys; T2 |
| Plan CT-Q1 | Tests asserting the duplicate refusal | none (`grep -rln 'duplicate fact-role' tests` empty at `1446f90`); the v1 message survives, T2 |
| Plan CT-R8 | Layering, query policy, anonymity | T9, T10 |
| Round 1 themes H, I, O, P, Q, R, W | repairs | tagged `(r1-X)` |

## Standing rules bound to this phase

1. **Totality:** `parse_anchor_sidecar` stays total over arbitrary bytes for
   both versions; every new branch raises `AnchorError` with
   `anchor:sidecar-invalid`. Hostile cases in T2 include 3,500 anchors on one
   role in the canonical form `write_anchor_sidecar` writes (`anchors.py:254`)
   using the v70-phase1 anchor template, the largest in the corpus. Four
   thousand anchors measured 958,077 to 1,058,077 bytes depending on the
   template, against the 1 MiB cap `MAX_SIDECAR_BYTES` (`anchors.py:70-72`)
   `(r1-H, r2-F)`. T2 also has a non-object `anchors` element.
2. **Input cap bounds the algorithm:** the v2 duplicate check keys a set, so
   it is linear. The checker evaluates each anchor once. T8 uses 1,000 rows ×
   3 anchors and counts record-dictionary lookups and per-anchor
   evaluations `(r1-Q)`; T8b puts 3,500 anchors on one (row, role) and counts
   evaluations and occurrence-set insertions `(r2-F)`.
3. **Validation order** `(r1-P)`: unchanged and stated as it is: the
   top-level key check (`_exact_keys`, `anchors.py:108`), then the version
   check (`:109`), then per-anchor checks, then the duplicate rule for the
   sidecar's version. T2's two-fault case (version 3 plus a duplicate)
   reports the version.
4. **One walk:** the grouping of records per key is built once, inline in
   `_anchored_verdicts` at the expression that builds `records` today
   (`_core.py:1911-1917`). The lexical index, the recogniser limits and the
   evaluation read that one structure. No per-version copy of the loop.
5. **One home:** the sidecar format's normative prose moves to
   `docs/reference/anchors.md`, which cites the parser as the authority and
   the new `src/gnd/anchor-sidecar.schema.json` as a description held in step
   by T11. `docs/guides/documents.md:58-72` and
   `gnd-orm-core/references/constraint-reference.md:47-51` cite it and yield
   in this phase.
6. **Measurement over argument:** v1 parity is a recorded before/after table
   (T7), not a claim about suites.

**Plan rules** `(r1-W)`:

- **CT-R1:** bound by T6 and T7.
- **CT-R2:** bound by the reference page wording.
- **CT-R3 (composition):** not applicable; CT1 composes nothing.
- **CT-R4 (digests):** applies, but no new digest is introduced. A v2
  sidecar's `population_sha256` and `document_sha256` stay raw-byte digests
  (`anchors.py:228`).
- **CT-R5, CT-R6 (induction):** not applicable.
- **CT-R7 (disclosure):** `gnd check --anchors` is already a site in the
  disclosure table. Its outputs do not change shape: a failed row is reported
  once per (row, role), as today. So the existing row and its redaction
  apply unchanged, and T13 runs the customer-mode case on a v2 sidecar.
- **CT-R8:** T9, T10. The RF6 allow-list is unchanged, because the
  `_anchored_verdicts` expressions keep their owner and count (`(r1-O)`;
  rows at `code-refactoring/evidence/RF9-repair/query-allow-list.json:142-152`).
  If an expression's count changes, the row is updated in the same commit
  and the change is recorded.

## Goal

`parse_anchor_sidecar` accepts `schema_version: 2` with several anchors per
`(fact_key, role)` and refuses a repeated `(fact_key, role, span.start,
span.end, occurrence)` with `anchor:sidecar-invalid: duplicate anchor`.
`gnd check MODEL POP --anchors S --document D` exits 0 on a v2 sidecar where
every anchor of every anchored role binds within its span. It exits 1, with
the row in the failed list once per failing role, when any one does not
(CT-D2). Every v1 input gives byte-identical output and exit to `1446f90`,
by T7's recorded table. The CT1 gate exits 0.

## Design

### `src/gnd/anchors.py` (about +40 lines)

```python
SUPPORTED_SIDECAR_VERSIONS = (1, 2)
```

`AnchorSidecar` keeps its fields; `schema_version` may be 1 or 2.

| Step | v1 (unchanged) | v2 |
|---|---|---|
| top-level keys | `{schema_version, population_sha256, vocabulary_digest, document_sha256, anchors}` | the same |
| version | `== 1`, else `unsupported sidecar version` | `in (1, 2)` |
| per-anchor keys and checks | as today | the same |
| duplicate identity | `(fact_type, roles_json, role)` → `duplicate fact-role anchor` | `(fact_type, roles_json, role, start, end, occurrence)` → `duplicate anchor` |

`excerpt_sha256`, `block_id` and `unit_id` are not part of v2 identity
(D2). Two anchors with the same identity and different `excerpt_sha256` are
refused as duplicates: one range cannot have two excerpts. `bind_anchors`
(`:218-251`) is unchanged; it already checks each anchor. The writer,
`write_anchor_sidecar` (`:254`), writes whatever version it is given; `gnd
extract` keeps producing v1 (D4) `(r1-T)`. `gnd.api` accepts `AnchorSidecar`
objects (`api.py:801`, through `gnd.extract.anchors`, a re-export), so v2
reaches the public API through the same parser.

### `src/gnd/checker/_core.py` (about +30, −8 lines)

In `_anchored_verdicts` (`:1887`), the expression that builds `records`
(`:1911-1917`) builds `dict[key, list[record]]` in sidecar order instead of
keeping the last record. Then:

- **Lexical index** (`:1918-1921`): for each record, add its `occurrence` to
  the set requested for its value `(r1-P)`. With several records for one
  value, the set is their union.
- **Recogniser limits** (`:1935-1945`): the maximum `occurrence` over all
  records for a target, as today.
- **Evaluation** (`:1974-2009`; the two `failed.append` sites at `:1983` and `:2008`): for each row and role, no records means
  failed, as today. Otherwise today's body runs for each record, and the role
  fails if **any** record fails (CT-D2). `failed.append` and
  `failed_refs.add` run **at most once per (row, role)**, matching v1, where
  each role appends at most once `(r1-P)`.

With v1, every list has length 1 and the loop does what it does today.

### `src/gnd/verbalize_population.py`, `src/gnd/export/verification_service.py`

`_excerpts` (`:126-136`) keeps **distinct** excerpt texts per role
(`if value not in bucket`), so two anchors with the same text show one excerpt
`(r1-P)`. Export verification (`:492-511`) reads through the parser. A v2
case is added for each. No code change is expected; one found is recorded as
a finding.

### `src/gnd/anchor-sidecar.schema.json` (new, about 80 lines)

JSON Schema, `oneOf` v1 and v2, describing what a schema can express. The
parser enforces nine rules the schema cannot, or that `json.loads` hides from
it `(r1-I, r2-F)`:

| Rule | Parser site (`anchors.py`) |
|---|---|
| P1 duplicate identity, version-dependent | `:133-135` |
| P2 `start < end` | `:129-130` |
| P3 the 1 MiB size cap | `:70-72` |
| P4 duplicate JSON keys | `:57-60` |
| P5 non-JSON constants (`NaN`, `Infinity`) | `:65-66` |
| P6 integers longer than 18 digits (`1e400`-style overflow included) | `:73-75` |
| P7 nesting deeper than 32 | `:79-80` |
| P8 `type(...) is int`: the schema's `integer` and `const: 1` accept `1.0`; the parser refuses it | `:109,129,131` |
| P9 invalid UTF-8 | `_parse` decode |

T2 has one case per rule (the parser refuses it). T11 asserts the schema
and parser agree on every fixture sidecar and every T2 case except P1–P9's,
where the schema accepts, or cannot see the input, and the parser refuses.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Pass rule | Plan CT-D2 | every anchor |
| D2 | v2 duplicate identity | (a) `(fact, role, start, end, occurrence)`; (b) `(fact, role, start, end)`: two occurrences of one text inside a span name different ranges, and (b) would refuse them | (a) |
| D3 | Ship a sidecar JSON Schema | (a) yes, with the parser-only rules P1–P3 listed and tested; (b) no: callers writing v2 have only prose | (a) |
| D4 | Does `gnd extract` write v2? | (a) no; (b) always: changes every extract golden for no new content | (a) |

## Tests

New file `tests/test_anchor_sidecar_v2.py` unless noted.

| # | Case | Expected |
|---|---|---|
| T1 | v2, one role with two anchors at different spans, both valid | parse ok; `gnd check` exit 0 |
| T2 | v2 repeated identity; v2 same identity with different `excerpt_sha256`; v2 same span, different `occurrence`; v1 same fact role twice; `schema_version: 3`; version 3 plus a duplicate; 3,500 anchors on one role (v2, canonical form, phase1 template); non-object anchor; one case each for P2–P9 (`start = end`, over 1 MiB, duplicate key, `NaN`, a 19-digit integer, depth 33, `"start": 1.0`, invalid UTF-8) | `duplicate anchor`; `duplicate anchor`; parse ok; `duplicate fact-role anchor`; `unsupported sidecar version`; the version message; parse ok; `anchor:sidecar-invalid`; `anchor:sidecar-invalid` each |
| T3 | v2, one role with three anchors: one in range, **two** out of range `(r1-P)` | exit 1; the row appears once for that role |
| T4 | T3 with the bad anchors first, then last | identical output |
| T5 | v2 with `recognise:`, two anchors, the maximum `occurrence` first in sidecar order `(r1-P)` | both evaluated; the recogniser limit equals that maximum |
| T6 | Unchanged with no edits: `tests/test_v70_phase1_adversarial.py`, `tests/test_v70_phase1_surfaces.py`, `tests/test_v70_phase5_adversarial.py`, `tests/test_v70_phase5_corpus.py`, `tests/test_rf1_semantic_pins.py` | exit 0 |
| T7 | Before/after `(r1-R)`: `gnd check` output digest and exit for every fixture sidecar (3 at `1446f90`) and every v70 corpus case, recorded at `1446f90` and after, in `evidence/CT1/parity.json` | identical |
| T8 | 1,000 rows × 3 anchors on one role | record-dictionary lookups = 1,000; per-anchor evaluations = 3,000; one `lexical_ranges` call |
| T8b | 3,500 anchors on one (row, role) at check time `(r2-F)` | per-anchor evaluations = 3,500; occurrence-set insertions = 3,500; the row reported at most once |
| T9 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py` | exit 0 |
| T10 | Anonymity scan over files added since `1446f90` | exit 0 |
| T11 | Schema against parser on every fixture sidecar and every T2 case | agree everywhere except the P1–P9 cases, where the schema accepts (or `json.loads` rejects before it) and the parser refuses |
| T14 | `src/gnd/anchor-sidecar.schema.json` registered in `tests/support/runtime_schema_inventory.py` and `tests/test_public_built_inventory.py` `(r2-H)` | `tests/test_conformance_payload.py` exits 0 |
| T12 | Population verbalization with a v2 sidecar whose two anchors on one role have different texts, then the same text; export verification on a v2 sidecar | two excerpts, then one; verification exit 0 |
| T13 | `GND_DISCLOSURE=customer gnd check` on T3's input | failed rows redacted as for v1; exit 1 |

### Verification selection

```
uv run pytest -q tests/test_anchor_sidecar_v2.py \
  tests/test_v70_phase1_adversarial.py tests/test_v70_phase1_surfaces.py \
  tests/test_v70_phase5_adversarial.py tests/test_v70_phase5_corpus.py \
  tests/test_rf1_semantic_pins.py tests/test_disclosure_mode.py \
  tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py \
  tests/test_conformance_payload.py tests/test_public_built_inventory.py
```

plus the population-verbalization and export-verification test files named
at implementation before the first run, and T7's recorded table.

## Out of scope for this phase

- Several documents per sidecar (CT-D12); composition (CT2); witnesses (CT3).
- Changing what `extract` writes (D4).
- Anchors with reference populations.

## Size

About 120 source lines, 90 schema lines, 550 test lines.

## Approval instrument

This prose. No fixture corpus is authored first.
