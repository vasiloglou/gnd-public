---
milestone: incremental-evaluation
station: phase-IE4
skill: n/a -- repository development via process-phase
scope: phase-IE4
date: 2026-10-20
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_incremental_observations.py tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_incremental_sessions.py tests/test_popvalidate.py tests/test_public_session_wire_guards.py tests/test_public_session_version_relabel.py tests/test_exp_session_evidence_compat.py tests/test_exp_feedback_derivation.py tests/test_rf8_sessions.py tests/test_public_retained_session_results.py tests/test_packaged_skills.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_rf9_ci_repairs.py"
  exit: 0
  output: "614 passed in 50.63s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately configured CI
  reason: current affected local consumers selected; broad historical/native/provider lanes unselected
evidence:
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/amendment-approval.json
    sha256: b2f9ee28826a625111be2cbce99a6160d8eff7cd25634fd360acb2019c978f93
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/approval.json
    sha256: 19a81b48a4ab5bb421426ed2a07333accdef5962ceb71c81bfed4e4ec89c6e63
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/complete-gate.txt
    sha256: 86e2bbfb6ee005bd861053dcbe923c85e0588492b3c9dda3611515c37fc236b5
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/confirmation.md
    sha256: fb375a6ba3796cc05153050065299bb636a0d6013bbd2735f00fade28ef85ede
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/corpus-red.txt
    sha256: 8b29f91d353f510f566f4efb221760c7e021f166446f9f80bf392bedc8352af0
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/doc-example.txt
    sha256: c5b521a1287a658fca8ee8d867394a8648ed185f5241086d5264383fdbc8737c
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/dynamic-query-successor.json
    sha256: f580f46064aaf9671b3d82d518ee5e479ec1732d2b26d849e15edfd700fa6714
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/expanded-red.txt
    sha256: a5ab68d1ae8de0335e6631ea82ac9f8bb19031d66ed8befcaf0902ac72a9b7ff
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/final-direct.txt
    sha256: 51912774091d1ad21acd2b4cef0ecf9a8cc3143ee3a86d961b8a27e9c9b2f4e8
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/final-identities.json
    sha256: e656356022ecd2ad464b70f52b82220091f11487894c126f0a3ba3358e0b4333
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/lint.txt
    sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/loader-gate.txt
    sha256: 2c763dad066d579015dc46cf7309dd431ede48b770ea86de232d029cfa25d687
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/repair-gate.txt
    sha256: ebc7eedd896bb60c9a9df8a179556b3f962d5a691de01c04d3f20663b29d01fe
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/review-red.txt
    sha256: ad21c1cf9f0adc240bd0a14da4bcc3e509f5a1d621719c27422032349a37d69f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/review-repair-approval.json
    sha256: 9726ce6c71784178de09be4c3892fdd02b888d02b3562ab035cd41e817e7382f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/review.md
    sha256: c381d5014a1c3d2680761d806557e191ffa41906453cb875872080a1bf57c2ae
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE4/skill-census.json
    sha256: ef15fa60626c8ae5ed781861207755e85b056b61b8916baa72a6db100ecf9e6e
  - path: .gnd-planning/milestones/incremental-evaluation/notes/phase-IE4-spec.md
    sha256: aca956efd586905dd6c12d6ac26ac1afa15231c18b9e83e99044bf89f5181603

---

# IE4 — accepted under delegated approval

Exact spec/corpus approved and committed in1ac6d7f; corpus observed8failures before
runtime. Corpus-driven amendment20e7d90 and review-repair gate89606cc preserve
prior gates. Owner named auto delegation covers those agent rulings, not personal
inspection. Approved spec is notes/phase-IE4-spec.md; exact approval manifests,
final-identities.json and retained evidence are in evidence/IE4.

## What shipped / criterion audit

C1: EvaluationSession.observe replaces whole ordered relations through normal
population bytes/schema/model-relative validation. Known IDs only, omitted unchanged,
[] deletes, duplicates retained. Base must carry a current marker; input and result
containers detach through serialization. Bad/stale/busy/closed observations cannot
publish cache/attempt progress. Successful observation also discards staging;
next check independently detects current changes. No unverified truth injection.

C2: check_with_feedback returns unchanged normal payload plus separate closed
kind evaluation-session-feedback/schema_version1. Counts distinguish asserted and
computed derivations, available0/unavailable/not-evaluated/overflow. Fixed strict
fields require explicit discriminators, finite/depth/duplicate-safe shared encoded
parser and16KiB canonical bytes including newline. At most128 rows/256identifier
characters; deterministic suffix omissions explicit. Count maximum2147483647;
overflow is null/status, not exact saturation. Cells/messages/witnesses/handles
never enter feedback. Existing persistent contracts/feedback/profile axes unchanged;
legacy reader rejects new wire. Attempt is explicit sequential1..1000000;
returned error feedback consumes it, rejected construction/observation does not.
Reset preserves lifetime numbering. No prior-feedback history or serialization.

Cache and attempt sequence now publish atomically through one private committed
record/reference. All ordinary cached generation/entry/binding/size semantics stay
under the existing ownership lock. Error feedback can publish only its sequence,
retaining old cache generation. Cancellation before publication leaves both intact.
The bounded sequence integer is control-plane state, not cache-content accounting.

C3: two-attempt course control executes check -> transition -> validated host
observation -> check -> next transition, compares full/incremental payload/branches/
feedback and retains unchanged first feedback bytes. No-op observation performs0
bodies/evaluators. Example extracted from docs ran offline: checks[0,0], walks[0,1],
attempts[1,2]. Admission of observations does not approve a later plan. Source docs
and packaged dev-session scope paragraph updated; measured65files/211relative-link
occurrences/167distinct edges/16skill names, no discovery-link or development-twin
edits. New lower checking helper assigned/visited; allowances remain0.

## Gate output

Combined selected gate: `614 passed in 50.63s` (complete-gate.txt).
Earlier affected state/extension/constraint/query repair gate:
`110 passed in 32.59s` (repair-gate.txt).
Direct observation+loader gate: `111 passed in 4.02s` (loader-gate.txt).
Final supplemental direct gate adds the confirmation's pre-publication cancellation
site without changing runtime; its output is retained in final-direct.txt.
Ruff on all changed runtime/test/helper paths: `All checks passed!` (lint.txt).
Initial structure run exposed exact new annotation inventory rows; authenticated
IE4 dynamic successor now follows IE3, with no raw-query waiver. Full query, layer,
source-scan and registry controls passed after that honest metadata update.

## Independent review / convergence

One authorized independent xhigh CLI reader plus one bounded confirmation, not a
panel. Retained review.md/confirmation.md declare path edits and static-only limits.
Three findings reproduced in5RED variants: cancellation consumed an unreturned
attempt, missing discriminator tags were defaulted, duplicate versions collapsed.
All repaired with source-before-predicate amendment and regressions. Confirmation
found no additional actionable static issue, and checked atomic publication,
private bookkeeping properties/accounting, explicit tags/shared parser, wire bounds,
reset/error/partial/reference distinctions. It did not run current greens, scheduling,
installation or timing. No third review. Final added cancellation-site control
carries author verification, not an invented extra review opinion.

## Refactoring review

EXECUTED: central lower feedback/composition home shares normal loader, original
structured calculator and shared input parser; no parallel family interpreter,
serializer or persistent-session wire. Replace multi-store generation publication
with one committed state record; compatibility read properties retain bookkeeping
lookups. Remove duplicate facade attempt state. Model queries use ModelIndex;
new module has explicit layer assignment/source visitation. No other structural
change needed here. Repeated policy normalization overhead is measured and assigned
to IE5; unknown-hook global dependency falsifier is also assigned to IE5 eligibility
repair and its independent review, not silently treated as already covered.

## Boundaries / open questions

Feedback is bounded diagnostic metadata about host assertions/derivations, never
external truth or certification. Publication is the synchronous committed-record
assignment; cancellation checks concern pre-publication rollback. No persistent
cache, native/provider acceptance, new547 workload, date, release or merge.
IE5 still owes integrated work/timing/memory/fallback evidence, final public docs,
bounded installed candidate and conservative unknown-hook eligibility. Source-bound
old evidence remains historical. Four independent close readers and full question
sweep remain after all phases. One-generation retained projection is not RSS.

## Refuted premises

Defaults inventing wire tags do not implement a strict versioned reader; Pydantic
JSON parsing alone does not preserve duplicate-key evidence. A separate attempt
counter outside cache publication breaks rollback. Computed unavailability is not
empty0; asserted overflow needs its own status. Raw Population.model_dump is not
normal wire: headers/format must be reconstructed before the existing loader.
Initial direct construction of ModelIndex was invalid; use for_model. These
construction mistakes were corrected before positive claims and are not separate
framework defects.
