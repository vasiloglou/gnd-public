# M3 phase10: Index witness origins without changing projection

## Harvested obligations

| Source | Obligation | Discharge |
|---|---|---|
| M3 required follow-up; phase09 boundary | remove repeated origin scans before final05 | single_origin_walk/native public report parity |
| correspondence.py current public projection | exact object first unused, exact reuse, then unambiguous canonical fallback | spelling_order/canonical_ambiguity/role_filter |
| source provenance/evidence controls | admitted/derived admissibility and coordinates differ intentionally | provenance_coordinates/derived controls |
| phase08/09 boundaries | no model/source reduction, same native facts, completed report parity | normal repeated native candidate checks |
| public dispatch consumers | same project_finding/project_snapshot signatures; two-argument patched dispatch | dispatch_seam/context_reset |
| source governance | RED first, focused controls, independent CLI review, typed module layer | corpus_first/layer_gate/review/record |

Measured phase09 baseline profiling (diagnostic, not normal timing) has40,614,912
coordinate-generator calls and329 value lookups scanning the entire42782-fact
origin list. Complete answer still120s. No final agreement/latency waiver.

## Exact implementation contract

New small typed gnd.semantic_origins module, checking layer, zero import allowances.
OriginIndex(origins) retains strong references and builds ordered admissible buckets
by exact scalar object identity and canonical (identity_kind,token), with wildcard
and exact source-role buckets; coordinates index ALL matching object origins even
if provenance is inadmissible or role mismatched. Store coordinate paths and cast
only selected paths, preserving previous malformed-unused-path behavior.
OriginSelection(index,used).value(scalar,witness_key) returns (found,raw_value).
Per-finding cursor skips consumed indices; exact first-unused then first-exact reuse
wins even when canonical spellings differ. Canonical fallback requires one raw
(type name,json.dumps ensure_ascii=False) spelling across ALL role-matching
admissible candidates, including consumed candidates, then first-unused or first
reuse. Lazy spelling sets computed once per bucket. Keys None and $variables are
wildcard; ordinary roles match last path component. No value coercion, canonical
new serialization or sorting. Scalars/paths are existing typed IR, no new JSON
consumer; scalar units are algorithm controls, not new domain datasets.

project_snapshot installs a scoped ContextVar index for that observation, invokes
existing project_finding(row,observation) two-argument seam, resets in finally.
project_finding reuses only an index whose origins is the exact source sequence,
otherwise builds a local one; a fresh selection and used set per finding shared
across all witness rows/cells. _origin_value signature/name and _MISSING remain
wrappers at original home; scoped selection reused only for matching origins/used.
Direct calls remain correct without snapshot context. ContextVar tokens restored
on nested calls and errors. No persistent population cache, global cross-call
memoization, public API or checker semantic change. All result fields byte equal.
Coordinates sorted as before. O(origins + bucket/output work) projection; no
all-origins-per-value/per-finding scans in a snapshot. Full reporting still emits
all existing fields. Refusal scope/subject occurrence path stays unchanged.

## Corpus-first criteria and verification selection

New tests/test_m3_origin_index.py using scalar/origin algorithm units and existing
public origin controls, no new domain models/populations. Preserve exact int/float
spelling sequence and object reuse; canonical ambiguity incl consumed candidates;
ordinary-role and $wildcard filtering; admissible admitted/derived cases, missing
origin refusal; coordinate inclusion independent of admissibility/role; sorted
coordinates and used reset per finding; two-argument dispatch; nested/error context
reset/different observation; None/False values and keyed arity. Counting sequence
tripwire demonstrates <=1 full origin iteration for a multi-finding snapshot;
old code must fail. Existing frozen projection corpus retains exact public output.

Focused source: uv run pytest -q tests/test_m3_origin_index.py
 tests/test_public_evidence_origins.py tests/test_public_correspondence_projection.py
 tests/test_public_correspondence_runtime.py tests/test_v61_phase4_projection.py
 tests/test_m3_compiled_work.py tests/test_compiled_snapshot_obligations.py
 tests/test_public_transition_contract.py tests/test_public_transition_trace.py
 tests/test_public_transition_api_guards.py tests/test_rf1_layering.py.
Ruff affected code/tests; default historical/proof exclusions retained.
App90 affected overlay repeats; no pin adoption. Own independent read-only Codex
CLI xhigh review stdin, one reviewer is one reviewer, cost0, no provider panel.
Native same real candidate, baseline fde2495 and candidate three serial unprofiled
public compiled checks cap60; full reports byte identical, warnings/counts unchanged,
actual normal medians reported without microbenchmark CI thresholds. Complete
cap8/top3/workers1/wall120 tuning probe once after measurements. No held-out or
sealed test access. Final all cap8 candidates/109questions and successful29-heldout
median<=15s remain final05 gates. If needed scope further work before runtime edits.

## Standing rules and implementability

Totality: no new arbitrary document consumer, typed existing origins only; unused
malformed coordinate remains unvisited. Input cap versus algorithm: single origin
walk tripwire plus bounded native60s measurement, ordered buckets/cursors.
Validation order: admissibility→exact→reuse→canonical ambiguity, unchanged refusals.
One policy walk: shared typed origin preparation for all findings; wrappers keep
one selector policy. Normative prose: current projection remains authority, this
spec specifies its preservation. Representation by measurement: exact spelling
unit controls, existing frozen projection corpus and full native report parity.
Implementability sweep: index can preserve origin order, raw values, distinct
coordinate eligibility and call seam; scoped contexts allow exception/nesting
restoration with no persistent state. No criterion requires optional later work.

## Delegated ruling and boundaries

Standing M3auto/make fixes part of M3/go ahead applies; corpus-first instrument,
optional spec panel omitted, budget0, no new domain data. Spec/test hashes recorded
before runtime edits. Source PR/explicit owner merge preserved; app directmain.
No release/certification/source merge authority, acceptance claim or changed gate.
Phase10 required before05; prior completed records retain their original scope.
