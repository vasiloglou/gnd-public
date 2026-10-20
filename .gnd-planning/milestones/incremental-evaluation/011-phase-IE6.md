---
milestone: incremental-evaluation
station: phase-IE6
skill: n/a -- repository development via process-phase
scope: phase-IE6
date: 2026-10-20
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_incremental_performance.py tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_incremental_prepared_policy.py tests/test_incremental_extensions.py tests/test_incremental_extensions_review.py tests/test_incremental_sessions.py tests/test_incremental_observations.py tests/test_incremental_session_measurement.py tests/test_tp3_check_receipts.py tests/test_incremental_session_replay.py tests/test_public_correspondence_runtime.py tests/test_public_semantic_counting.py tests/test_m3_extension_preparation.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_public_api.py tests/test_public_reference_signatures.py tests/test_rf4_peripheral.py::test_current_successor_body_and_import_controls_are_live tests/test_rf4_review_regressions.py::test_transition_source_guard_visits_the_defining_payload_module"
  exit: 0
  output: "486 passed in 211.02s (0:03:31)"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection or separately configured CI
  reason: affected focused current gates selected; broad historical/native/provider/certification lanes unselected
evidence:
  - path: src/gnd/incremental_state.py
    sha256: d746e0f57be2e707e1309253da5f6cfd4ef52c33a74d75d3ec3bca6318cb499c
  - path: tests/test_incremental_performance.py
    sha256: c07a88ebdbb4ec82c25287036bc90eb01a0159edebc60d89f08fd9540d6bfb12
  - path: docs/reference/python-api.md
    sha256: 7f76e1500754147be246e7381c90744939d218ef1678d808b2a9fd2be7f71df8
  - path: docs/release-notes.md
    sha256: c2f015cf2d22acf52b473fb0b1a1437c7aec5eaeafb5ff71282cc0a795211e02
  - path: .gnd-planning/milestones/incremental-evaluation/notes/phase-IE6-spec.md
    sha256: 3bacd6d9d96635d30efdb8a2be4ea14fef2988fac0ff8f5ea6dca1fe2db8f3ca
  - path: .gnd-planning/milestones/incremental-evaluation/notes/incremental-evaluation-plan.md
    sha256: 57146d5e2dc58c663a6209e981fb1758ed981bc019afdfdef489e326d33a5a29
  - path: .gnd-planning/milestones/incremental-evaluation/notes/IE6-close-question-sweep.md
    sha256: 60b89fd51b329aaef5c7023dbc106ab9dffbacba9864ad1a2af3eb7f94197b68
  - path: .gnd-planning/milestones/incremental-evaluation/notes/phase-IE6-astra-review.md
    sha256: c54b0f5430a322bc79a8eaba025a109a50e1558bc0644abfb2f94b9a3996939c
  - path: .gnd-planning/milestones/incremental-evaluation/notes/phase-IE6-astra-confirmation.md
    sha256: c4af553ae59688b93c9afff24af99134f1677a265e2f8c468cffa018522eeecc
  - path: .gnd-planning/milestones/incremental-evaluation/010-IE6-reopening-gate.md
    sha256: fb874c5175b43b89426befc2b4af3d6a326e1765a3dfea5e542639f8075d9abf
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/approval.json
    sha256: 5cfe952e9f597898eb1a7cf45ac9d791d059eae51230e315bfb33c9ad72c1d8f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/astra-performance-review.md
    sha256: bb136b4358987d4f1dccd82394cc408d3e11817dfa8cceb35067c70432e9f815
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/audit.py
    sha256: a20fa6766c18c45ec49ac2a43badd4e6bb66f57770efe749e750bc212e5bc3d7
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/compare_revisions.py
    sha256: 4a3bd4a5f37f1de8dbf8d3da5479f36f9bfbd7ae3c34b86b2c3856e180d26ac3
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/compare_revisions_initial.py
    sha256: 49c887d7dc250d035d1cce98442a8bf45b79f343c8c4aadce8757aebd1b98b1f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/corpus-red.txt
    sha256: af04998a7ab7f56f0ad7dff6483c39d22377daf2a43dc78a9eea64cec92eaa6f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/course-identity-green.txt
    sha256: 7d203ec346a564431e8d1fa7ea6145437ea570bb5693244e9bedd9af5e7ed87d
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/course-identity-red.txt
    sha256: eedc4644b08538eeca805fbf597d4f4a701f45f0169e3021c5edd21e98ceba0d
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/descendant_mutant.py
    sha256: 762626256328c2c315afefc75553650550f0306fbc4e975ef081566f14dd3f40
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/doc-gate.txt
    sha256: e29583202aeca76366e3fdf7747cd8656b4d35e05d6b904ee8db1c9128063962
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/doc-links.txt
    sha256: 833126599ff79da37fbe1b8e153c2a07e6da36b737293b877cda640d130bc974
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/final-gate.txt
    sha256: e205993259cdec8e55e695c7e5343ee6a2becedf49064a89a2532e5fbfdc3f16
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/hashability-red.txt
    sha256: 0e5a3afe02263abb7954f1052cdba2e0b33f92b66dbd1cf6f082849adbfb2b74
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/identity-green.txt
    sha256: 6b85ce96f974ace658278f62b3dec00669ecf2fcab7c494c5e680e87d6c737e6
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/identity-red.txt
    sha256: 526f8793e09106876e2fe8c5ff3158552a844cfd596a0473c70b45d95d5ac10a
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/identity_negative.py
    sha256: 7e3b417e5d158c63219c8452fb273a6a662d05a605bcee9c6219220821532683
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/initial-install-refusal.txt
    sha256: f751b066386190cdc9de90dafd6d3c423f075d2165b9603248bdee8a4ff70676
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/initial-venv.txt
    sha256: a595456ce179c1c6e4d47b564369c7f4da85d4c788e5689c2a8739754ddf2442
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/installed-cli.json
    sha256: 814ff77a53781ae5557e9a4cf4c15276f3a578f7435d8534b522350f5db60728
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/installed-smoke.txt
    sha256: 410c9d54ab66fa29f09e7d7b4b5859ef40ecd45ae2bbbc38588ea6fc12b09587
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/installed_smoke.py
    sha256: d6f30bcfe491cbc61f76d381b691d99059fa070a37cf65827d49e9c627b4a329
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/instrument-mutant-after.txt
    sha256: b843b82d9b5aa5b6345a4a2f675cab70700108ac4c5082788c971a5e53f23a5f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/instrument-mutant-before.txt
    sha256: a18c3b900475afac2c188104bcb1373540f6580c7200ea3a3de0cffafe01816c
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/intermediate-gate-subject.json
    sha256: 70fbcc6d2cf225040c5d3b0b28e6a9de5aa7564e15392a61cf8de91a5a769297
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/intermediate-gate.txt
    sha256: 91160fd2ddd99f143a040e6793c0c81369f78a391cb8d85f1d44bed3ff97766e
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/lint.txt
    sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/measurement-sanitation.md
    sha256: 6cd38596fd7e513d5ea52d5b1674bea834167313cfcbe9cd17234ffe9baac272
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/measurement-stdout.txt
    sha256: 9d9129a963a965c2f7d34f1dcd7501745819a42ec1075659a932488eedb4a419
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/measurement.json
    sha256: 23a17c57b7c771042b3c84148b93bb3fb119a0d952bd3169b79aac47931c2405
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/metaclass-red.txt
    sha256: 459cc3afe56ffd8af967728d30bfcd38608472d59f60b65c797349f2f279ffce
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/plan-correctness.md
    sha256: 18a9319a7de83ed7868b7fefe63b07df180714c297ff6ae134138b9174f8ccf8
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/plan-measurement.md
    sha256: 5cf81e59e12cdb05712a1aa38182df93f4acf9fbc97f0fb70ea80f7eaf077280
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/plan-protocol.md
    sha256: e2e3c49705fc3ff788a4be948835162b50195a683150ed81046f443580e14951
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/plan-structure.md
    sha256: 6b2a9a38d341fba6bfb0904da450fe51f093f23d8fbd353196d2719b937b6ae4
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/query-inventory.json
    sha256: f5177c2f956165f40546975cd934eab5350e74b504e0c9f9c98bc761f8c09c02
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/raw-policy-red.txt
    sha256: 233e66603dc482f34132fe8cb713fbcce53dc6467d7e1047e28fa57336511e6f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/review-disposition.md
    sha256: 957dcc68b70c2e765571f9e40b6a9781bc9d0d7f71cdeb482f7b7336b0f0adb3
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/revision-comparison-initial-stdout.txt
    sha256: aab72896b4396a299ed41de6cfab2578da67dd3b0ee54ea71719d4ac5081f7f8
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/revision-comparison-initial.json
    sha256: cf44dd69f764d5a352adf003314d69d8ba3d0986850b4b4404134a6c141e1871
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/revision-comparison-stdout.txt
    sha256: 32d8976f619ef8a9e586ef3fbb0d3f09769fb395aecc3a13963b71a2886bc885
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/revision-comparison.json
    sha256: c56628ae2204d8f633cdbbb9fe546d1126e244487d9a7e63cd3f74d919522954
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/safety-amendment-approval.json
    sha256: d131e23ff1ba1b4f14626c1b7828a39413071edee7e40a1c504292d1537f203f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/venv.txt
    sha256: 726ee481f031d3a4aeb370b01d8ae5a6da2128f5c3f29b535c872afcd0b2a194
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/wheel-build.txt
    sha256: 5430218043b06dd3a08f7b1784824aad353505cd1f402a157909163cf0fac766
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/wheel-install.txt
    sha256: 79b06f309698ed7adb616ea6ad834d15844deb49bc7aa34be7563c471591943f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE6/wheel-manifest.json
    sha256: 02d1ad4c2f81d6c8c2b333d6c5feda4b7c17388d05d94b7dc319cae76beabaff
---

# IE6 accepted under delegated approval

Owner explicitly reopened this named milestone to add and implement the performance phase.002 auto and CLI-review transfer authority persists;010/e897967 commits reviewed spec and RED corpus before code.3dcf4f2 explicitly supersedes unsafe one-time-hash expectation before repair. This is delegated approval, not owner personal inspection. Separate exact final acceptance is evidence/IE6/acceptance.json.

## What shipped and criterion audit

C1: complete current full/receipt/session payload, exits, branches and ordered outermost calculation requests match in the integrated oracle. Frozen full-receipt body denominator4878 remains unchanged; session bodies179.

C2/C3: incremental_state._footprint computes bounded verified immutable policy size/node/depth once, substitutes conservative summaries during both admission size walks, and still measures the actual private clone. Scalars avoid recursive setup and builtin containers avoid dataclass reflection by identity. Live full signature hashing, exact equality, mutable/code guards, current independent model/options scope, cancellation/atomic commit, private clones, caps and conservative fallback remain. Summaries are transient; full policy trees remain charged in retained entries. Cross-subtree sharing may overcount, never undercount.

Prepared work control: initial12misses rescanned the normalized root25times; current strengthened control visits it once across24misses/24hits and160descriptor children. Raw control visits320descriptor children across2admissions/4hits, without repeated admission walks on hits. Exact injected descendant rescans passed old2tests and fail current2tests. Hash-removal target was withdrawn after actual stale1/fresh2 RED, not quietly relabeled GREEN.

C4: serial balanced source-bound revision comparison uses A=archived d0ffd9a session, B=IE6 session, C=IE6 full receipts. Each isolated worker verifies actual module root, warms once, then times complete replay without profiling/counters; expected exits/census checked. Both complete package/tool/fixture/config identity maps stay unchanged; driver hash is checked in every worker and at completion. Initial incomplete-map comparison is retained as exploratory, superseded after actual legacy-helper negative and guard repair. Integrated tool separately uses its original A=full/B=receipts/C=session arms, counters/ordered oracle and balanced uninstrumented timings. Do not interchange these labels or chain timings across runs.

|Workload|Before session(s)|IE6 session(s)|Full receipts(s)|Session median decrease|
|---|---:|---:|---:|---:|
|reporter|9.594056|9.030647|8.496214|5.87%|
|course|2.410517|1.991713|0.855150|17.37%|
|localized|0.574453|0.540538|0.422638|5.90%|

All three session arms improve versus archived sessions but remain slower than full receipts in that comparison. Three samples per arm on shared host; raw samples/ranges retained, no universal speedup claim. Absolute timings differ from IE5; no cause for that difference is asserted.

Integrated same-current-source timing medians (separate run):

course: {"A": 0.9089222080074251, "B": 0.8374516251496971, "C": 2.0656955000013113} seconds.

localized: {"A": 0.44080704101361334, "B": 0.4072375420946628, "C": 0.5823849160224199} seconds.

reporter: {"A": 9.397427374962717, "B": 8.360566415823996, "C": 8.455186082981527} seconds.

C5: 486 passed in 211.02s (0:03:31). Current AST inventory6209distinct/7792occurrences matches exact prior chain; no new raw-query or layer allowance. Public signatures/defaults/wires unchanged. Two performance docs updated, selected doc gate retained. Fresh explicit Python3.11.15 installed wheel smoke outside checkout exercises normal CLI, session/receipt/transition/observe/feedback, strict duplicate handling, detachment and close.273wheel Python members byte-match source; wheel-manifest.json binds archive outside Git. Initial implicit3.14 environment lacked cached offline dependencies; no3.14 installation claim.

## Gate output (verbatim)

UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_incremental_performance.py tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_incremental_prepared_policy.py tests/test_incremental_extensions.py tests/test_incremental_extensions_review.py tests/test_incremental_sessions.py tests/test_incremental_observations.py tests/test_incremental_session_measurement.py tests/test_tp3_check_receipts.py tests/test_incremental_session_replay.py tests/test_public_correspondence_runtime.py tests/test_public_semantic_counting.py tests/test_m3_extension_preparation.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_public_api.py tests/test_public_reference_signatures.py tests/test_rf4_peripheral.py::test_current_successor_body_and_import_controls_are_live tests/test_rf4_review_regressions.py::test_transition_source_guard_visits_the_defining_payload_module

```
486 passed in 211.02s (0:03:31)
```

Lint: All checks passed!

Integration command (exit0): UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline python tools/measure_evaluation_sessions.py --out /private/tmp/ie6-integrated.json

```
{"parity": true, "reporter_full_bodies": 4878, "reporter_session_bodies": 179, "reporter_timing_medians": {"A": 9.397427374962717, "B": 8.360566415823996, "C": 8.455186082981527}}
```

Revision command (exit0): UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline python .gnd-planning/milestones/incremental-evaluation/evidence/IE6/compare_revisions.py --baseline /private/tmp/ie6-baseline --candidate . --out /private/tmp/ie6-revision-comparison-final.json

```
reporter {'A': 9.594055624911562, 'B': 9.030647499952465, 'C': 8.496213541831821}
course {'A': 2.4105167919769883, 'B': 1.9917128749657422, 'C': 0.8551495000720024}
localized {'A': 0.5744527501519769, 'B': 0.5405381249729544, 'C': 0.4226383750792593}
```

Build: UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv build --offline --wheel --out-dir /private/tmp/gnd-ie6-dist (exit0). Venv: UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv venv --python .venv/bin/python /private/tmp/gnd-ie6-311-venv (exit0). Install: uv pip install --offline --python /private/tmp/gnd-ie6-311-venv/bin/python /private/tmp/gnd-ie6-dist/get_nick_done-0.1.0-py3-none-any.whl (exit0). Smoke from /private/tmp/gnd-ie6-smoke: env -u PYTHONPATH /private/tmp/gnd-ie6-311-venv/bin/python smoke.py (exit0). Exact scripts/stdout/actual installed paths and wheel digest retained. CLI exit0/schema7. No source shadow.

Documentation command (exit0): UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache PYTHONPATH=.:tests uv run --offline pytest -q tests/test_release_docs.py tests/test_contributor_preparation.py::test_current_contributor_surfaces. Verbatim: 3 passed in 1.07s. Both changed reference/release link surfaces also checked. Lint command (exit0): UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline ruff check src/gnd/incremental_state.py tests/test_incremental_performance.py .gnd-planning/milestones/incremental-evaluation/evidence/IE6. Verbatim: All checks passed!

## Independent review and refactoring

Four local readers accepted the bounded plan amendment. One independent authorized Astra CLI initial phase review plus one bounded confirmation; one reviewer is one reviewer, not a panel. Three actual findings reproduced; current confirmation None survived, static-only, exact source/test hashes retained. No third round. Instrument completeness is fixed because it is this phase own performance gate; no cosmetic-only findings forced wider scope.

Refactors EXECUTED: central existing storage walk now supplies reusable conservative subtree metadata; existing _measure size/None interface and normalizers stay in one home. No new runtime module, import edge, family registry, shim retirement or skill/discovery edit. Optional constraint-policy preparation, extension planning and combined measurement/freeze remain explicit framework-maintainer performance follow-ups; live same-transaction mutation checks make them a separate scoped effort.

## Refuted premises

A normalized immutable tuple does not make borrowed class handles permanently hashable. Tuple membership does not mean identity for custom metaclasses. Counting only root visits does not prove descendant work absent. New footprint work on raw-policy hits can erase savings; it is now delayed to admission misses. RED and mutant evidence retains each premise; no elapsed threshold was lowered after results.

## Boundary and open questions

No general speedup, superiority to full receipts on these controls,547-program downstream acceptance, delivery date, default activation, row-delta recursion, persistent/portable cache, RSS bound, broad historical/native/provider acceptance, certification, publication or merge. Full admission/adaptation/report composition remain fresh; diagnostic counts are not every Python instruction. Caller/returned/observer memory is outside projected retained cache content. Transient wheel/venv/archive bytes are outside Git; retained manifests/results are checkable while those artifacts remain available. Prior001–009 claims remain historical; old close audit does not describe IE6 bytes. New sweep notes/IE6-close-question-sweep.md dispositions all changed/new questions and retains all18 prior rows and IE-Q2..Q10 by reference. Renewed four-reader close remains mandatory after this phase.

Size: runtime delta68insertions/14deletions, current state553lines; new test file237lines. Within stated primary design estimate; no optional setup refactor shipped.
