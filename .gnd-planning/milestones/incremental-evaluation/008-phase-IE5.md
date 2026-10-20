---
milestone: incremental-evaluation
station: phase-IE5
skill: n/a -- repository development via process-phase
scope: phase-IE5
date: 2026-10-20
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_incremental_prepared_policy.py tests/test_incremental_session_measurement.py tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_incremental_extensions.py tests/test_incremental_extensions_review.py tests/test_incremental_sessions.py tests/test_incremental_observations.py tests/test_incremental_baseline.py tests/test_incremental_baseline_review.py tests/test_tp3_check_receipts.py tests/test_incremental_session_replay.py tests/test_public_api.py tests/test_public_reference_signatures.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf4_peripheral.py::test_current_successor_body_and_import_controls_are_live tests/test_rf4_review_regressions.py::test_transition_source_guard_visits_the_defining_payload_module"
  exit: 0
  output: "455 passed in 279.37s (0:04:39)"
  note: "Last tool-only observer-cost repair additionally passed19 direct controls and final source-stable integrated measurement."
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection or separately configured CI
  reason: current affected runtime/CLI/batch/exp/source/installed surfaces selected; broad historical/native/provider/certification lanes unselected
evidence:
  - path: .gnd-planning/milestones/incremental-evaluation/006-phase-IE3.md
    sha256: 104f520c84ff4498b65a65c352000e45763c22ac5e2485501c7961bc10d71880
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/amendment-approval.json
    sha256: d14cef35b1909bcf44b045da080482a6ea771b8d11711ee578c7590e306684d1
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/approval.json
    sha256: 546ec589d00a48b8ffc932a1827de882fbebf104f7bddbea711cb1132ed0035a
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/confirmation-red.txt
    sha256: 7957c63a7d14d1dd5a6872191f287c62656e730db95fb63b6fc30f8f85919d39
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/confirmation-repair-approval.json
    sha256: baf3e2ce5e059697e62b32d94f5ffb61c3821ae46e4d722da33b9f5db169deb9
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/confirmation.md
    sha256: 448736147a70322ba7ebd9e3cc8dbf47c880f86a5326232c4aeac6ad971aa56a
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/corpus-red.txt
    sha256: e8b549abecab719004167cd8b2cba71748df20d3e77ff81761e0c5ab878e3c27
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/doc-gate.txt
    sha256: 786b493e290582ff456045dc5a4eaa819162ba5164f9a2306d01c86f4d15f3fc
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/doc-links.txt
    sha256: fb97bdfae7bc70b57b371d84af0392ce9305202b468654f973799bf558d81c8d
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/dynamic-query-successor.json
    sha256: f1987551652fb572b2dd3e23778e894d2838d20de89e4b8d4d60373c04b3686a
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/exploratory-profile.txt
    sha256: 845fbb2cddefd76fab991baac50b0c54142f0e3a0eed871f2813ae13c676787b
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/fallback-error-red.txt
    sha256: b48daa30b0499a0e119b8bf9e87b1426059fd4d97edf5407e670924fd650581b
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/final-counter-gate.txt
    sha256: 58a883b5056c9085c66bf9c8e97ed1ffd74104a28161dd424fff7eaf153f4dce
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/final-focused-gate.txt
    sha256: 3fe75b2e7881a55cacd21de7916748842cf4123278c93a7c88a77bb7ff01608b
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/final-identities.json
    sha256: c83917d4ab7d8cc605b3c7cf3a413d2ef595005157e46fcb9c78441958d90903
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/installed-cli-check.json
    sha256: e8f91f958b4a9330abeb2b5fc9c3e87181c8af23564df4d1a221f351e2056a08
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/installed-dependencies.json
    sha256: 5cc2e9aeeaaa2f3f791adc5aa98ef8e63ea49ea764fe6e58e5d0ad67d05dfbdf
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/installed-smoke.txt
    sha256: b6227a2830a32bc835cbad9dfced11b1ec0da14d0f61f7b1788d27e0acb3ebdb
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/invalidated-measurement.txt
    sha256: da9fa8d36f3e2274f677837372de129a3723de35d481f900504f36464ca3476f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/lint.txt
    sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/main-gate.txt
    sha256: a63067933ac16cca4b9670f255b6ea2a9190ccabb7c71ea4585c389071dba62e
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/measurement-stdout.txt
    sha256: 1a33c7b8ca764a8ee2d901e6f12c9d10a4ab9d50a4546efd2593aa1c69f5280e
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/measurement.json
    sha256: 299d649a3cd0ba800e0eaf143522acf5d54e954c4bb9ea2f1706c003f4e13186
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/observer-red.txt
    sha256: a170f8801ccadc59cabc4ec933234b91549118949d18285e7bf8a24f7b1e4887
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/ordered-replay-gate.txt
    sha256: be16c68fcb1e519ae3a57278e1ba20d26a349cf197398f4f2569eeec7b8135e5
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/prepared-profile.txt
    sha256: 8bfa7a962a76a659beb1daa263a9f7cc3f2aaa1e3046f66ac3cefc22cc90d166
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/receipt-replay-gate.txt
    sha256: 47138349632b7a72c65574ca3a33776cb882c6c4df4b034a57c2b05cca4a1b2a
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/reference-receipt-gate.txt
    sha256: 0e27e07e1cb358f2352909c611a268125c66bb35062f47057f54fbc156ffc036
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/review-red.txt
    sha256: 8d0859f95d85494341d928c98403ec20cbe272e4a0fb722c5523c9df2fe3991c
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/review-repair-approval.json
    sha256: 16b20766aa34926db24e89501c08fd426945f0918509bb502386807b4d397412
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/review-repair-gate.txt
    sha256: 8e806de1321e34869ebeb7dbd0e5793d9724e9396f58ea1969a34b49b2ec5331
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/review.md
    sha256: 8a478a0e9397fba19c1d998f6895386e531d7a0f183b2c5ac4456631c5ac89a1
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/wheel-manifest.json
    sha256: 630cf29ea2298d77760b9f2fd71b8c459698311379ad53e64afbe31ac5d89363
  - path: .gnd-planning/milestones/incremental-evaluation/notes/phase-IE5-spec.md
    sha256: 4f93da3749f6aa68b10c6c29d9c8203f3f02ac1f1a45d9726ab5f5dd0dde8e9a

---

# IE5 — accepted under delegated approval

Spec/corpus gate93e6222 precedes runtime; material corpus/review repair gates
ab04e67,e00bfad,a6bb9fd retain original rulings. Owner named auto delegation
covers these agent dispositions, not personal inspection. Exact spec is
notes/phase-IE5-spec.md and approval manifests are under evidence/IE5.
final-identities.json binds current source/tests/docs; measurement.json separately
records source/fixture/configuration/environment identities before and after a
stable run. All evidence below is local, not release/certification or merge.

## What shipped / criteria

C1: frozen full A, receipt-only B and explicit session+receipt C replay the old
reporter, course and localized controls. Every arm's exact census/exits is checked:
reporter13/all2; course3outer walks/[1,1,0]; localized6/all1. A/B/C complete typed
public payloads/exits/branches match; B/C additionally match the complete ORDERED
outer calculator request results, including cached returns and multiplicity.
Keys include fact/role/codec/ordered rows/lineage/unavailable/possible/logical work.
Nested implementation/component callbacks are suppressed, not treated as logical
requests. Delete/duplicate/permutation and common-error controls discriminate.
IE3's earlier set-envelope claim is corrected in006 in place; its old gate remains
historical, not retroactively stronger.

Measured reporter B4878 vs C179 actual derivation-body executions, strict target
179<4878,96.33% fewer. Checker runs stay19 in B/C (25 in A); authoritative evaluator
primitive events stay1365 in B/C because all684 reporter constraint routes take
conservative fresh fallback. Unit lookups4485 =4414hits+71misses,0bypasses;
extension context requests69,0context refusals; final65entries/999charged rows/
11904099projected bytes. Complete equality, not a reduced finding count, gates.

Course B93→C24 bodies, evaluator primitives102→82; localized B24→C6 bodies,
12→6 evaluator primitives across the6mutation walk. Separate independent/no-op
controls establish0unaffected-body/evaluator work in their eligible fragment.
32 repeated localized calls retain4entries/9rows/638097projected bytes, with body
deltas[2,0,...,0]; close leaves0entries/rows/bytes. Separate instrumented localized
Python allocation peak14055614bytes, not RSS. It includes the probe/driver, not an
isolated reporter memory experiment. Retained projections, not RSS, are the cap.

Uninstrumented timings are interleaved ABC/BCA/CAB in one non-isolated shared
macOS/Python3.11.15 environment. Medians/ranges seconds:

|Workload|A full|B receipts|C session+receipts|
|---|---|---|---|
|reporter|6.4478 /0.3818|5.8306 /0.0835|6.7885 /0.1190|
|course|0.6089 /0.0174|0.5830 /0.0197|1.8722 /0.0219|
|localized|0.2496 /0.0104|0.2546 /0.0455|0.4213 /0.0237|

C is slower on all three small controls despite counted savings. Reporter C/B
median ratio1.1643; no elapsed-time gain is established. D7 makes timing
informational, not a target that can replace/relax counted parity. Bookkeeping
remains a named framework-performance follow-up; defaults stay unchanged.
Separate preloaded uninstrumented cold/noop/insert/delete/replace/reorder arrays
and per-call ACTUAL work deltas are retained. Active profiling/tracemalloc refuses
wall measurement. An edited-source exploratory run was explicitly rejected by the
source-stability guard; it is retained as a negative, not final acceptance.

C2: current public signatures/exports, CLI/batch/exp wire/profile consumers,
source/query/layer/alias controls pass. No layer allowance or raw Model-query waiver.
IE5 inventory measured0registered dynamic-row delta and records that exact result.
checking_service body pins remain unchanged; no hidden successor replacement.

A wheel built offline with uv0.10.10/uv_build was installed with12locally cached
packages into a FRESH final environment. Actual interpreter:
/private/tmp/gnd-ie5-final-venv/bin/python. Imported api/evaluation_feedback/
extensions/incremental_state all resolve under that environment's site-packages,
from outside the checkout with PYTHONPATH removed. Public host-loop, repeated
check/cache hits, receipt detachment, strict duplicate-safe feedback and close smoke
passed. Default installed CLI check exits0/schema7 with no cache diagnostics.
Wheel SHA25643eeb26ea59d7d038d5db59291b8f9767c19ad93237141220b3b7e4ff645b5e4;
273wheel Python members match current source bytes. Wheel member hashes and actual
module paths are retained. Binary/environment paths are temporary, not published
or retained in Git; source/member/installed evidence identifies the tested candidate.

C3: public API/capability/data-transition/dev-session/release docs explain eligibility,
current admission, mutation, lifetime, observations, schema/order, caps, diagnostic
denominators and measured regression. Mermaid shows dirty propagation/component
reuse. The packaged-course example is executed by installed smoke. Packaged skill
surface remains IE4's65files/211relative-link occurrences, with unchanged discovery
links and development twins. Local links in all5changed docs and selected skill
prose checks pass.

## Runtime changes and refactoring review

EXECUTED: normalize policy ONCE per original calculation context using the existing
bounded walk. Prepared records carry exact current authority plus live function-code
and combined mutable-leaf guards; expired/foreign/unsupported keys compute fresh.
Only ordinary normalized immutable signatures enter entries; accounting unchanged.
No global pool, extra history, second serializer/dependency walk or identity-only
admission. Profiles identified195repeated walks; new normalization has bounded
context lifetime. Profiles are exploratory observations, not cross-run speedups.

Unknown registry hooks are fresh using actual defining namespace identity, not a
module-name claim or attempted arbitrary global traversal. Callable/string mutable
external global falsifiers are retained. Configuration is not proof of purity.
Fresh evaluator invocation now lies OUTSIDE the setup catch: an actual full70/
session0 transient failure was reproduced and repaired without retries. Full
fallback retains original error/branch behavior. A diagnostic fixture initially
assumed references force rejection on a non-reference model; ordinary API ignores
them there. Corrected lost-marker admission gives1explicit fresh call/0unit lookups.

Fixed diagnostic vocabulary and explicit lookups stay out of report/feedback.
Misses/bypasses can overlap; rates always pair numerator and denominator, null at0.
Actual fingerprint work excludes the observer's payload projection via a scoped
ContextVar; positive runtime fingerprint control remains live. Actual evaluator
metric is the frozen IE0 set of authoritative snapshot primitive entries, not
every instruction or the legacy compatibility evidence kernel. Admission,
adaptation/projection and compatibility evidence remain fresh.

Shared complete oracle/outer-request observer has one tool home; IE2/IE3 controls
reuse it. Baseline tool's existing default A/B/full-control arms stay intact;
new session measurement entry point explicitly chooses C. No broader refactor
justified. Remaining bookkeeping cost is assigned IE-Q1/framework-performance,
not hidden behind the body counter.

## Gates / independent review

Main current-behavior selection (main-gate.txt):
`1211 passed in 67.72s (0:01:07)` covering compiled/transition/correspondence,
API/reference, batch, exp wire/profile, packaged and RF1/RF3/RF6/RF7/RF9 consumers.
The focused command above after ordered/lookup repair:
`455 passed in 279.37s (0:04:39)`.
Final observer-accounting-only repair:
`UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_incremental_session_measurement.py tests/test_incremental_prepared_policy.py`
returned `19 passed in 1.44s`. Final source-stable measurement command:
`UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline python tools/measure_evaluation_sessions.py --out /private/tmp/ie5-measurement-final-source.json`
exited0 with paritytrue, bodies4878/179 and the recorded medians. Earlier ordered
reporter alone passed1 in91.62s; receipt/replay/RF4 gate13 in95.81s. Real reference
receipt completeness control passed1 (18deselected). Docs/prose3passed in0.41s;
5changed-doc local links passed; Ruff `All checks passed!`.

One authorized independent xhigh CLI reader plus one bounded confirmation, not a
panel. Initial three findings reproduced in4variants, with an additional real
nested/cached boundary RED (3vs4emissions for2requests). Ordered traces, frozen
workload and lookup denominator repaired. Confirmation checked all three and
adjacent controls; one additional observer-cost finding reproduced actual3→6
fingerprint nodes and repaired. It concerned pre-existing adjacent observer code,
not repair-created code (ratio0/1); maximum rounds still2. No third review and no
invented opinion on the final pause repair. RED/GREEN and final source-stable
replay support delegated disposition. Reviewer outputs declare path sanitation and
static-only limits; they did not execute reported gates or installed/timing claims.

## Boundaries / open questions / refuted premises

Body savings do not imply wall savings. These small fixtures are slower in C.
New547workload is absent; reporter owns downstream acceptance and no date is
promised. Peak allocation probe is localized/instrumented, not reporter RSS.
No all-Python-work-zero claim, arbitrary hook purity proof, row-delta recursion,
persistent/serialized cache, new default mode, broad historical/native/provider
acceptance, certification, production release or merge. Four independent close
readers and final question sweep still owe the separate milestone gate.

Refuted premises: function/default identity does not cover unknown mutable globals;
fresh callback inside a setup catch may retry an error into false acceptance;
unique result sets do not prove ordered/multiple logical coverage; equal errors
are not acceptance; miss+bypass totals are not lookup denominators; observer cost
is not evaluator fingerprint work. Each has actual retained RED evidence.

A separate acceptance.json binds this exact phase record and current source/measurement identities under the named delegated authority; it is excluded from its own subject digest to avoid a circular hash.
