---
milestone: incremental-evaluation
station: phase-IE3
skill: n/a -- repository development via process-phase
scope: phase-IE3
date: 2026-10-20
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_incremental_sessions.py tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_incremental_extensions.py tests/test_incremental_extensions_review.py tests/test_tp3_check_receipts.py tests/test_public_api.py tests/test_public_reference_signatures.py tests/test_public_correspondence_runtime.py tests/test_public_correspondence_projection.py tests/test_public_semantic_applicability.py tests/test_public_semantic_counting.py tests/test_public_semantic_mandatory_union.py tests/test_public_semantic_guarded_join.py tests/test_compiled_snapshot_obligations.py tests/test_compiled_snapshot_boundaries.py tests/test_public_transition_contract.py tests/test_public_transition_api_guards.py tests/test_public_transition_review_controls.py tests/test_rf1_layering.py tests/test_rf3_core.py tests/test_rf3_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_rf9_ci_repairs.py tests/test_m3_extension_preparation.py tests/test_incremental_baseline_review.py tests/test_incremental_session_replay.py"
  exit: 0
  output: "1079 passed in 210.38s (0:03:30)"
  note: "Final string-hook repair additionally verified by the 68-test affected command below."
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately selected CI
  reason: broad historical/native/provider lanes unselected; focused current affected controls ran
evidence:
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/amendment-approval.json
    sha256: 8fbb438a793fddbf82657f8587c7d8028299c7e37493c71004c52a0f2de118a8
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/approval.json
    sha256: 097ede68d42b67da6195f006334dd54a92cbc6ff569713c7067c5b228880648b
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/confirmation-red.txt
    sha256: c48dcfdf7dd56c60d9f1aeb9f4567d940b21af85fbcdceb152f379efe61e5654
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/confirmation.md
    sha256: 34ed08dc05a11f229f5312e2f653e66ba7c03dd5ad822fc13e9e68c047023ee6
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/corpus-red.txt
    sha256: a907173ee94617bd7c8d18178862acb1296eae70053ddf22d0d2854f1f2112c3
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/coverage-mutants.txt
    sha256: a57f6806e9db82d580b538d1c3808c3d978d96008cc846ac26548d8833b248ff
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/dynamic-query-successor.json
    sha256: 50ef3b70c3898321033a0e77d80e7d360f924a9341bf6a83684b80f58a7366ba
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/final-gate.txt
    sha256: 9aa247e46b84e5ecb4a84d9465f7ae0b1e3f291be2007d6ad156363ba6d39d35
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/final-identities.json
    sha256: 20047645f8855a6494e74b8ec924a7db34a8af75703e1a71406b66f9c3f647cf
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/final-repair-gate.txt
    sha256: 1203c5f38910ef87f5e6745914b27e97f56765c5b324e89a4fbcc2cc747cb53f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/lint.txt
    sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/mint-failure-red.txt
    sha256: f6016ba56588d8974a0b09507eeb790093698f9f5735373fd241ecd1ca29dbf4
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/query-successor.json
    sha256: cf45348bb4039b6fa1bc7de5296b9256912ae7d7edda97150b25b43db3426100
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/review-red.txt
    sha256: 26159a21564a0d58b1f42bfdc90549cd31a705d5aef2bc1552d2a9e060363330
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/review.md
    sha256: 57bc8e0318807c769ec70bd1026f2ea2c47b1067b1086925b787000c5b439030
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/witness-rows-red.txt
    sha256: 1bf88496a85b2ccdc6a59b898dbfbeaeb3dcdaf531041eec6bbd9dbf9cbe3742
  - path: .gnd-planning/milestones/incremental-evaluation/notes/phase-IE3-spec.md
    sha256: 01e7ca1c7eceb6e5456f00a108b4c16f26ef66b835d07614237b56b6c11fb1d0

---

# IE3 — accepted under delegated approval

IE3 spec/corpus gate committed in baf7472 before runtime. Named owner auto
execution delegation and explicit Codex CLI phase-review transfer authorization
remain scoped here. This is delegated approval, not personal owner inspection.
Original approval and amended exact identities are in evidence/IE3/approval.json
and amendment-approval.json; final-identities.json records current runtime/test
SHA256s. These manifests and the retained gate/review files are the evidence homes.

## What shipped / measured criteria

C1: one extracted constraint evaluator preserves the original family dispatch,
refusal order, branch evidence, witnesses and final composition. Inline uniqueness
keys complete selected metadata and ordered rows; other eligible findings key the
complete typed semantic snapshot. Reference work, guarded/anchored/clock modes
compute fresh. Existing bounded fingerprint supports trusted GND dataclasses;
unsupported/cyclic/oversized keys fall back. Configuration includes direct and
string-resolved hooks at defining namespaces. Report aggregation remains fresh.

C2: receipt minting stores a private deep report copy; consumption copies again,
so public report or direct transition-result mutation cannot alter future use.
Clone failure is nonreusable/fresh fallback. Existing refusal order and eligibility
remain. A reproduced duplicate failed-mint check now routes its first failure and
branches through the ordinary payload builder once. Caps charge witness rows too.

C3: api.EvaluationSession explicitly wraps normal loaded-input check, receipt and
transition orchestration. Declared post/reference parameters forward through real
public paths. Error/uncheckable results discard candidates; IE1 lock, current
model binding, ownership/cancellation and resource limits remain. Export assertions
include the new surface; serialization is refused. No-op executes zero derivation
bodies/evaluators; localized independent constraint executes no right evaluator.
Complete typed reporter replay compares all13 payloads, exits, branch sets and
extension metadata/lineage/unavailable/logical-work projections.
**Correction, 2026-10-20:** that historical test compared sets of complete
envelopes; it did not establish ordered request multiplicity. IE5 /008 supplies
the stronger outermost-request ordered proof and its deletion/duplication/permutation
negative controls. The historical gate output remains unchanged. Actual bodies
are strictly below frozen4878 full-with-receipts denominator, all13 exits2.
The integrated test supplies the threshold proof; no elapsed-time gain asserted.

## Verification output

Main selected command above: `1079 passed in 210.38s (0:03:30)`.
Final repair command:
`UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_incremental_sessions.py tests/test_public_semantic_counting.py tests/test_public_correspondence_runtime.py tests/test_rf6_query_policy.py`
returned `68 passed in 21.75s`. It covers the last string-resolved configuration
repair after the larger gate imported its earlier runtime bytes. Unaffected
receipt/transition/extension controls are supplied by that larger gate.
Ruff on all changed runtime/tests/helper/tool paths: `All checks passed!`.
Retained stdout files: final-gate.txt, final-repair-gate.txt, lint.txt.

## Independent review and convergence

One independent authorized xhigh CLI reader plus one bounded confirmation,
not a panel. Retained review.md and confirmation.md declare machine-path edits
and static-only verification limits. Initial two findings: callable default
configuration produced actual stale accepted vs fresh violated; missing declared
post/real reference controls were coverage gaps. Added real controls kill both
post-drop and reference-drop mutants. The direct default repair passed; bounded
confirmation found its string-resolved analogue, also reproduced RED and repaired.
One of one confirmation findings concerns repair-created policy code (ratio1/1).
No third review; amended final bytes carry no invented further reviewer opinion.
Retained RED and mutant outputs support delegated disposition. A replaced context
fails registry identity first; this is binding refusal, not isolated digest proof.

## Refactoring review

EXECUTED: one original constraint body extracted into its defining helper;
central fingerprint extended instead of second serializer; original FAMILIES
registry/lookup namespaces retained; receipt payload/error builder reused.
No new runtime module or layer allowance. Typed IR query owner moves and one added
metadata read have exact authenticated successors, original308<310 ceiling.
Dynamic AST successor follows IE2. checking_service definitions were untouched;
no stale service-body successor claimed. Actual runtime delta:319 insertions,
148 deletions across four existing files. No other structural refactor needed:
cache ownership stays in IE1, calculators IE2, facade above checker. Policy-key
bookkeeping optimization remains explicitly owned by IE5 pending measurements.

## Boundaries / open questions

IE4 observation/feedback, final IE5 integrated timings/memory/fallback accounting,
docs and installed candidate remain owed. Small-fixture bookkeeping can exceed
fresh evaluation cost; no wall-time saving claimed here. Unit stats count lookup
events, not a whole-call eligibility rate. No new547 workload, downstream acceptance,
delivery date, broad historical/native/provider acceptance, certification,
publication or merge. Retained-size accounting bounds cache content, not RSS.
Historical source-bound records stay historical. Four independent close reviews
and question sweep remain mandatory after all six phases.

## Refuted premises

Function/code identity misses mutable default configuration, including hooks
resolved from registry strings. Python payload equality misses Bool/int metadata;
typed complete oracle is used. A test title mentioning declared post does not
establish forwarding; a matching implicit reference context cannot discriminate
argument dropping. Raw steps lists are not supported public inputs. Stored public
receipt report mutation and repeated failed-mint evaluation were reproduced and
repaired, with original historical evidence preserved.
