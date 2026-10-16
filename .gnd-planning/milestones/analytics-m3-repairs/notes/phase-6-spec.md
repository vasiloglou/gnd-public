# M3 phase06 source execution supplement

Status: owner-decided2026-10-13 under explicit M3 auto, make the fixes part of M3,
and go ahead. Canonical app contract: downstream-apps/.downstream-app/milestones/M3/phase-06-spec.md
at8d9cfac; this supplement binds source execution, not a new GND milestone plan.
Source basefa926ae; topic codex/m3-performance-fixes. Source ownership/PR/explicit
merge governance retained. Cost0; no new domain data, provider panel or certification.

## Decisions, provenance and obligations

D6A delegated(auto=true): preserve the existing public byte-loader signature, pinned
by tests/test_transition_report.py::test_the_public_population_loader_signature_is_unchanged.
Use consistent .json suffixes for every generated canonical-JSON source label in
transition.py, including legacy/v2 asserted/intermediate/computed/effective-post.
Source descriptions change only by .json suffix; population headers/rules/facts,
strict decoder guards, validation order/markers and report semantics unchanged.
This is the alternative allowed by the canonical phase06 spec; no bypass or new API.
Estimated production changes5 call sites (~10 lines), acceptance~70 lines.

Corpus-first instrument: new tests/test_m3_generated_json.py with named existing
legacy clean-walk and v70 T01 opaque-walk inputs; answers.json binds exits0/4,
non-null computed-post and generated JSON dispatch for both paths. Existing clean
walk steps are rebound to the actual current model/operations identities; no fact,
operation, binding or semantic expected answer changed. Initial red tests must
fail because generated JSON selects YAML, not because a stale digest refuses it.

Standing rules: totality/validation order are retained by unchanged population
loader and current hostile-input/cap controls; input cap vs algorithm requires
normal3-repeat full-state start measurements and decoder-dispatch guard; one policy
walk audits every canonical JSON loader caller; normative prose stays in existing
population loader and canonical app spec; representation choice measured by prior
identical-byte/fact1.90s vs7.97s control. No new serialization format or schema.

## Verification selection

Run direct tests/test_m3_generated_json.py. Run canonical selected tests:
test_population_load.py; test_public_transition_api_guards.py;
test_public_transition_ir_immutability.py; test_public_transition_contract.py;
test_public_transition_trace.py; test_transition_report.py. Add current opaque/v2
successors test_v70_phase4_transition.py and test_public_population_paths.py if
present/affected. Preserve default exclusions; no historical/proof/census replay.
Run selected lint and existing runtime layer checks for the two-module import boundary.
Full default/history/certification lanes cadence: separately authorized CI/owner;
not selected by this source fix. Changed-byte old certificates unavailable.
App candidate preview: approved canonical source/fast/budget/worker/audit/CLI selection,
installed candidate overlay in the app's uv workspace with pin unchanged.

Experiment before run: normal serialized public single-start transition on the
same full native model/state at cap8, tuning IDdw_5162,3 repetitions; record all
exits/completions/times, model/state/source/split/candidate/interpreter identity.
No timing-only correctness assertion or M3 latency/held-out claim. Baseline53.793s.
Semantic report comparison before/after retained; source-label decoration reviewed.

Review: independent codex exec ephemeral read-only harness using existing ChatGPT
login, prompt on stdin, high reasoning, bounded source diff and criteria. Same-tree
subagent harvest is not claimed as the formal source reviewer. Stop after demonstrated
blocking defects repaired and direct controls pass; completeness deferred. One
reviewer is one reviewer. Record no formal proof/recertification.
