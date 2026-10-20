---
milestone: incremental-evaluation
station: milestone-close
skill: process-milestone -- repository development, not a gnd-solve station over a domain model
scope: milestone-close
date: 2026-10-20
gate:
  command: "UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline python .gnd-planning/milestones/incremental-evaluation/evidence/close/audit.py"
  exit: 0
  output: "runtime unchanged since final measurement; data-only audit exit 0"
  note: "Close identity/provenance/sanitation audit; runtime execution gates are the separately retained phase outputs below."
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection or separately configured CI
  reason: affected current gates and bounded installed candidate selected; broad historical/native/provider/certification lanes unselected
evidence:
  - path: .gnd-planning/milestones/incremental-evaluation/001-plan-gate.md
    sha256: a313752da6f5b30fa2a569afeabb0aca76e8b3f05653ba1a2f9b39a1fdff7ea7
  - path: .gnd-planning/milestones/incremental-evaluation/002-execution-delegation.md
    sha256: 7f776af776a3713f2ed2a71a7eb02dc8654b2d3e6e7b52668392e159494530fd
  - path: .gnd-planning/milestones/incremental-evaluation/003-phase-IE0.md
    sha256: de134aeb35b382308aa1ea6ad503c99a224e490f2095ad1671ceb7998bc03eb8
  - path: .gnd-planning/milestones/incremental-evaluation/004-phase-IE1.md
    sha256: 7d9a0e0e7b4a64c55ac9e5ef323b1fee7df84b909c3d10ce5bd00d469fee0008
  - path: .gnd-planning/milestones/incremental-evaluation/005-phase-IE2.md
    sha256: 5517d4b8478899ed23b7a4d4aeeb4cd33e82232581d20212488b2d40ddb2ec63
  - path: .gnd-planning/milestones/incremental-evaluation/006-phase-IE3.md
    sha256: 104f520c84ff4498b65a65c352000e45763c22ac5e2485501c7961bc10d71880
  - path: .gnd-planning/milestones/incremental-evaluation/007-phase-IE4.md
    sha256: a2adde0c2211f0c4c2599570d9743ebfef39e7915d0212339cc197387b2aae89
  - path: .gnd-planning/milestones/incremental-evaluation/008-phase-IE5.md
    sha256: 30435297ec1d6843e5fa28ce60d2c5616d209741e41bd5b1bb639b96e52e511b
  - path: .gnd-planning/milestones/incremental-evaluation/notes/incremental-evaluation-plan.md
    sha256: be624dc874f0328b4a5b4167ddb3ca0a7f31f6258cd3ef69cb55470b47fc5428
  - path: .gnd-planning/milestones/incremental-evaluation/notes/close-question-sweep.md
    sha256: a7081284c13e51a79656cc48d41f9a6a060a28e0f68290907b894f8a3e475161
  - path: .gnd-planning/milestones/incremental-evaluation/README.md
    sha256: 4c1663b977c29e43b6c52ea248a60a145b03e2dc67aa66c5659516f959d8fdcf
  - path: .gnd-planning/PROJECT.md
    sha256: 24550f3f1bb7357943896e5e00838dd0e999c0a97f5c732971e80f4cb7262a4a
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/audit.py
    sha256: edfcc84e01fef1c318c5e52f2f7e38c40d72a8eec53901f23ed1bf128c6247e6
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/audit.txt
    sha256: f093e4dc9a83098cd71dbf11c4f906778affe664bd855460bb44e5921d868bc6
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/correctness.md
    sha256: 70f257d21b16ca2deb726abdcfa658931b871f515c86eeb96388f09030638a37
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/disposition.md
    sha256: 741e14b27f67eb1d68f76003867364a1734fbeef6e47be7de63f4043cef869d7
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/measurement.md
    sha256: 87783eda63fad7c60bbf3a6b2da967d413ae7b4a9e6a334104423113e8010f1f
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/protocol.md
    sha256: 805284e5f36769b00f49d17118d0948104db5ff5ba7d278791f212ce0de57961
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/sanitation.json
    sha256: 5fe13099a9b550e1d26824102344fd0eb09ec4ae22c7d9cdafd896181c7b506b
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/close/structure.md
    sha256: 45f7508245107216ae0ca8eac96f8f48bad28a7f0644dd7c9fe700a0caee8dc8
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/acceptance.json
    sha256: 81cb7b28c87be9558e1a4a3a162f043ef0d98c869fbe8758bf2fd213babea54e
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/final-identities.json
    sha256: c83917d4ab7d8cc605b3c7cf3a413d2ef595005157e46fcb9c78441958d90903
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/measurement.json
    sha256: 299d649a3cd0ba800e0eaf143522acf5d54e954c4bb9ea2f1706c003f4e13186
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/measurement-stdout.txt
    sha256: 1a33c7b8ca764a8ee2d901e6f12c9d10a4ab9d50a4546efd2593aa1c69f5280e
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/wheel-manifest.json
    sha256: 630cf29ea2298d77760b9f2fd71b8c459698311379ad53e64afbe31ac5d89363
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/installed-smoke.txt
    sha256: b6227a2830a32bc835cbad9dfced11b1ec0da14d0f61f7b1788d27e0acb3ebdb
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE5/installed-cli-check.json
    sha256: e8f91f958b4a9330abeb2b5fc9c3e87181c8af23564df4d1a221f351e2056a08
  - path: .gnd-planning/milestones/incremental-evaluation/notes/phase-IE0-codex-review.md
    sha256: 9d1300d5902a623dbd8db3ef7619541ce0076d20a1b46595b5183937e21734b4
  - path: .gnd-planning/milestones/incremental-evaluation/evidence/IE3/corpus-red.txt
    sha256: 8b8ab56b1ab1ae983508f0b440274adafffe1afcba14e59c08c421656cd1a864
---

# Local milestone close with explicit carryovers

All six mandatory phases IE0–IE5 are accepted within their recorded gates.
The close data audit exited0. Four distinct independent local close readers return
close-with-carryovers. The complete question sweep and PR33 discharge the remaining
close artifacts; separate delegated approval is recorded in
`evidence/close/acceptance.json` after this record's exact final digest is computed.
This is delegated approval under002, not an assertion of the owner's personal
reading. PR: https://github.com/vasiloglou/gnd-public/pull/33, topic branch
`codex/incremental-evaluation`, base main. No merge is authorized or performed.

## Completion predicates and impact closure

|Approved predicate|Disposition and evidence|
|---|---|
|1 Baseline and differential oracle|003: frozen old reporter, packaged course and localized walks; real corruption/liveness negatives; exact baseline denominator4878 retained.|
|2 Conservative invalidation|004: independent current model scope, typed ordered fingerprints, dependency closure, live authority, unsupported fresh fallback, isolation/rollback/caps.|
|3 Component/finding reuse and public session|005–006: complete component envelopes, selected safe finding reuse, original dispatch and final aggregation, explicit EvaluationSession with ordinary check/transition orchestration. IE5 repairs unknown-hook and evaluator retry fallbacks.|
|4 Counted work and parity|005–008: two-independent-component/no-op controls avoid eligible unaffected bodies/evaluators. Final reporter B4878/C179 bodies, strictly lower with denominator unchanged. Full payload/exit/branches and B/C ordered complete logical requests match. Reporter constraint primitives1365/1365 remain fresh, not a claimed broad saving.|
|5 Observation and feedback|007: validated whole-relation host replacements, detached population, atomic attempt/generation commit, strict bounded separate in-process feedback; persistent experiment wires unchanged.|
|6 Integration, lifetime and documentation|008: check→transition→observed check→next transition; installed source-bound wheel smoke, invalidation/error/receipt detachment, bounded retention, ABC/BCA/CAB timings and fallback denominators, five changed documentation surfaces.|
|7 Gates/reviews/records/close|001–008 retain approved spec/amendment history, focused gates, one independent CLI phase reader plus at most one confirmation, refactoring dispositions. Four fresh close responses, final sweep, PR33 and separate exact delegated close ruling complete the local close.|

The data-only audit authenticates115 historical phase artifact identities at their
original record commits, not against later changed source. All30 IE5 final identity
subjects,238 source entries and346 fixture/configuration entries match current
bytes. Source/runtime/tools did not change during close. No gate rerun is implied
by reviewing retained execution output. Phase selections overlap and must not be
summed as unique tests.

## Gate output (verbatim)

Close command is in frontmatter, exit0:

```
final identities: 30/30 match
measurement maps: 238 source / 346 fixture match
historical phase identities: 115 match at original commits; per phase [10, 16, 20, 17, 18, 34]
close readers: 4 distinct retained opinions; close-with-carryovers
sanitation: 2 reproduced before/after repairs; machine-home scan clear
runtime unchanged since final measurement; data-only audit exit 0
```

Current affected runtime gates are retained at008 and their own exact paths and
commands. Their verbatim summaries are:

```
1211 passed in 67.72s (0:01:07)
455 passed in 279.37s (0:04:39)
19 passed in 1.44s
All checks passed!
```

These are distinct historical executions, not a new combined test run. The1211
selection covers compiled/transition/correspondence, API/reference, batch,
persistent exp wire/profile, skills and affected RF1/RF3/RF6/RF7/RF9 controls.
The455 focused selection follows ordered/lookup repair; the final19 follow the
last observer-accounting-only repair.008 also retains the real-reference receipt
control, receipt/replay/RF4 gate, docs/link checks and scoped lint command.

Final stable measurement command, exit0:

`UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline python tools/measure_evaluation_sessions.py --out /private/tmp/ie5-measurement-final-source.json`

Verbatim summary:

```
{"parity": true, "reporter_full_bodies": 4878, "reporter_session_bodies": 179, "reporter_timing_medians": {"A": 6.447771791135892, "B": 5.830629916861653, "C": 6.788488249992952}}
```

The final candidate was built and installed offline into a fresh temporary venv,
then exercised outside checkout without PYTHONPATH.008 retains exact build/install/
smoke commands and output.273 wheel Python members match source; wheel SHA-256
`43eeb26ea59d7d038d5db59291b8f9767c19ad93237141220b3b7e4ff645b5e4`.
The fourth reader separately hashed the available archive's995 members and four
installed module files without importing them. The wheel binary and venv live
outside Git; the manifest and smoke outputs are committed, so future verification
of those temporary bytes depends on their continued availability. This is bounded
installed candidate evidence, not a production release or certification.

## Measured criteria and limits

Reporter13-call replay: full+receipts B19 checker runs/4878 bodies, session C19
checker runs/179 bodies (96.33% fewer). C4414hits/4485lookups,71misses and0bypasses;
misses/bypasses overlap generally and lookups is the denominator. Reporter684/684
constraint routes remain fresh. Logical work, findings, witnesses and projection
are not invented from cached diagnostics. Conservative unknown external hooks,
reference/anchored/guarded/unsupported modes retain their normal full route.

Uninstrumented interleaved medians(s), same environment:

|Workload|Full A|Receipt B|Session C|
|---|---|---|---|
|Reporter|6.4478|5.8306|6.7885|
|Course|0.6089|0.5830|1.8722|
|Localized|0.2496|0.2546|0.4213|

All measured session timings regress. Reporter C/B≈1.1643; no elapsed gain is
established. Approved D7 keeps timings informational and counted/parity predicates
hard; no target was weakened. IE-Q1 names future bookkeeping/guard/fingerprint/
clone performance work owned by the framework maintainer. This milestone stops
here rather than extending implementation to force a timing gain.

Reporter retains65entries/999charged rows/11904099projected bytes. Separate32-call
localized probe stabilizes at4entries/9rows/638097projected bytes and close clears
all three. Its instrumented Python allocation peak14055614bytes includes driver
cost and is not reporter RSS. Caps100000rows/32MiB apply to projected retained
cache content, not caller-owned inputs, returned objects or observer storage.

## Independent close review and record corrections

Four responses and disposition are retained in evidence/close. Each read the
committed runtime subject d5effb28 and identified draft artifacts; their exact
reviewed identities and static limits are in their responses. No close reader ran
candidate tests, benchmarks, providers or credentials. No phase reviewer is
relabeled as a close panel. All four are separate local agents, selected by the
owner. One initial round, no confirmation round, no implied review of final009 or
amended navigation/acceptance bytes.

Protocol sanitation findings were reproduced before repair; `sanitation.json`
retains old/new identities and each edited file declares the modification. Gate
semantics and runtime bytes are unchanged. Stale IE5 draft status was corrected.

This009 explicitly owns the correction of006's overclaim: original006 at cd61f56
SHA-256 `509ba981ed3ec8936a8daf75e22eb6bddf668f3cea759565c69760e29869f5cc`;
corrected current006 SHA-256
`104f520c84ff4498b65a65c352000e45763c22ac5e2485501c7961bc10d71880`.
006 was edited in place during IE5 under process-phase's instruction to correct
reasoning at its original site; that differs from the generic append-only record
format. This exception is disclosed, not presented as unchanged record history.
The old set-envelope check did not prove ordered multiplicity;008 independently
supplies stronger outermost-request ordered proof and deletion/duplicate/permutation
negatives. The historical gate output is not widened. Original TP3 records and
prior milestone close remain byte-stable.

## Open-questions sweep and refactoring review

`notes/close-question-sweep.md` dispositions all18 inherited rows, IE-Q1..Q10 and
D1–D9. No orphan question is silently closed. Deferred framework maintenance names
anchored-hook structure, accessor/shim naming, standalone caller-held scope lifetime,
receipt ergonomics and signal classification. The reporter owns supplying/admitting
the offered547-program bundle and downstream acceptance. No date follows from local
fixtures. Broader lanes/merge/publication/certification remain owner decisions.

Refactors EXECUTED are documented per phase: independent ModelIndex scope,
complete component reuse, extracted original single-constraint evaluator with
unchanged registered-family dispatch, private receipt copies, strict feedback home,
one atomic committed record, one bounded prepared-policy walk and shared outermost
measurement oracle. Their recorded focused gates preserve the named behavior.
Close needs no further runtime refactor: its changes are sanitation, provenance,
dispositions and navigation. Every deferred structural item has a named owner/
target in the sweep; bookkeeping overhead stays explicit performance debt.

## Refuted premises

Cached body savings do not imply elapsed speedup. Unknown hook function/default
identity does not cover mutable globals. Setup fallback must not retry actual
evaluator errors. Sets of complete results do not establish ordered multiplicity.
Matching errors do not prove workload acceptance. Misses+bypasses do not form a
lookup denominator. Instrument observer cost is not runtime fingerprint work.
003–008 retain the discriminating RED/GREEN evidence; this close changes none of
those tests or their scope.

## Boundary -- what this result did NOT establish

No supplied547-program acceptance, general elapsed speedup, proportional row-delta
recursion, arbitrary Python purity proof, persistent/portable cache, default session
activation, all-Python-work-zero claim, reporter RSS bound, broad historical/native/
provider acceptance, certification, production publication or PR merge. Admission,
validation, adaptation, final report composition and compatibility evidence remain
fresh. Primitive counts name the authoritative snapshot metric, not every legacy
compatibility trace instruction. Final annotations and delegated acceptance have
no invented independent review opinion. Four opinions and green gates are evidence;
002 named delegation separately supplies authority for this local close ruling.
