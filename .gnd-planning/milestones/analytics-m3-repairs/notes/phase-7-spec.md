# gnd-analytics M3 phase07: indexed production subset evaluation

Status: scoped specification; execution follows recorded phase06 completion.

## Obligations and acceptance

| Source | Obligation | Control |
|---|---|---|
| M3 plan/roadmap6.5, owner make the fixes part of M3 | avoid quadratic subset identity membership and repeated decision/witness projection | subset_public_provider; native_check_before_after |
| AGENTS public boundary; roadmap7.1 | preserve exact full reports, modality and witnesses | subset_oracle_parity; source_mirror_parity; app preview |
| phase06 record | retain generated strict JSON dispatch and loader validation | generated JSON regression and transition controls |
| GND registry/layers conventions | register optimized dispatch, preserve common applicability/refusal and branch IDs | registry_binding; layer ratchet; public branch/projection controls |
| development protocol | approved spec, committed RED controls, independent review and record | red_green; separate Codex CLI review |

## Exact design and boundaries

Add Family.production: Hook | None = None in constraint_families; only subset
registers production='indexed_subset_verdict'. Existing six hooks, pure evaluator,
unknown families and extension behavior remain unchanged. Correspondence resolves
this optional hook against semantic_rows only when common applicability is evaluate,
after existing guarded/mandatory/uniqueness/string-order selections. Common opaque
refusal override, reference coverage, witness origin projection and branch recording
stay outside the hook. No new module/import-layer exception.

In semantic_rows, indexed_subset_verdict(IRConstraint, SnapshotIR) returns the
existing (verdict, reason, canonical tuple witness) contract. Validate precisely the
existing subset shape: no refusal, two sequences, single or joined variant, single
requires one fact type per sequence, joined requires at least one multi-fact
sequence. Resolve each sequence once using the existing normative role_sequence_rows.
For valid rows use existing scalar_identity (identity_kind, token) for hash membership
and existing canonical_rows for canonical witness order and first representative.
Compute left-only rows once: no repeated subset_state/subset_witness preparation.
Boolean and numeric identities stay distinct; numeric spellings share identity;
raw temporal string identity, tuple arity/order, duplicates and null identities stay
unchanged. Invalid input returns the same unchecked reason through the existing
reason provider. Empty subset passes, including an empty joined projection. Deontic
violation warns. The pure semantic_spec oracle is unchanged. Equality/exclusion are
unmodified sibling controls, not new optimized branches. Both native mirror rules
remain in the unchanged model. No context/global cache or private app imports.

## Corpus-first approval instrument and branch controls

New source tests/test_m3_indexed_subset.py uses existing frozen P2-086..091 subset
cases (pass/fail/warning/joined/empty), compares full public check payload before
and after patching the pure quadratic subset provider to reject use, and compares
production findings to the pure oracle with unchanged input. Existing frozen
refusal/applicability controls supply malformed/join/opaque/coverage semantics.
Scalar unit controls compare canonical_rows with canonical_distinct_rows using
already supported scalar literals, including bool/number, null, duplicate identity,
row arity and temporal raw spellings; these are decoder/identity unit controls,
not invented domain data. Registry test pins the optional hook and defaults.
Commit tests RED before implementation. No outcome/golden weakening.

Focused source gate: uv run pytest -q tests/test_m3_indexed_subset.py
 tests/test_m3_generated_json.py tests/test_public_branch_runtime.py
 tests/test_public_correspondence_projection.py tests/test_public_semantic_adapter.py
 tests/test_public_semantic_composition.py tests/test_rf6_registry.py
 tests/test_rf1_layering.py tests/test_public_transition_contract.py
 tests/test_transition_report.py tests/test_v70_phase4_transition.py.
Preserve configured lane exclusions. Ruff changed modules/tests. Broad historical,
proof/certification/provider lanes are not selected; separately scoped CI/owner
cadence owns those. Prior certificates do not describe changed bytes.
App preview repeats phase06 affected fast/source/budget/worker/audit/CLI selection
through the app uv candidate overlay, production pin unchanged.

Measurement declared before run: same supplied full native model/state and tuning
ID dw_5162, cap8, three serialized public single-start calls with wall cap60s,
no warmup; record each completion/time/CPU and median plus report/input hashes.
Compare reports to phase06 and baseline, normalization only .json generated labels.
An additional public full native check is measured before/after, same source.
Measure new indexed algorithm alone on the actual supplied mirror rows with a
bounded deadline, not generated large domain data; deterministic operation-bound
controls replace flaky small-input wall-time assertions in ordinary CI. The live
measurement is retained evidence, not the final held-out M3 latency gate.

## Standing rules and implementability

Totality/validation order: hook consumes typed IR after unchanged public validating
adapter and applicability; malformed shapes explicitly refuse before projection.
Input cap versus algorithm: hash membership and canonical sorting are bounded by
input rows; real native layer measurement and quadratic-provider trap enforce this.
One policy walk: shared role_sequence_rows and scalar_identity define resolution
and identity; dispatch registered once. Normative prose has one home: semantic_spec
remains the oracle. Contested representation: differential full-report/identity
controls and measured real mirrors decide it. No loader/schema/proof edits needed.

## Authorization, review and open questions

Delegated approval auto=true, 2026-10-13: owner M3 auto, make the fixes part of M3,
and go ahead. Cost0; no new synthetic domain data or upstream merge/release authority.
Source topic branch/PR/explicit owner merge rules continue; app direct main remains.
Independent source review uses own read-only Codex CLI harness, stdin prompt, one
reviewer, try to refute parity/complexity/refusals/coverage. Reproduce findings before
triage; completeness deferred by default. Refactoring review and hashed evidence
required. Phase05 owns accepted standalone dependency pin and original exhaustive
agreement/15s successful held-out median. If still slow, scoped further context
reuse is required before edits; no gate waiver. Sealed test remains unread.
