---
milestone: model-composition
station: phase-MC1
skill: n/a -- repository development, not a gnd-solve station over a domain model
scope: phase-MC1
date: '2026-11-10'
gates:
- command: uv run pytest -q tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_schema_sync.py tests/test_model_validation.py tests/test_model_identity.py tests/test_model_v2.py tests/test_compiled_snapshot_obligations.py tests/test_reference_population_corpus.py tests/test_public_reference_budget.py tests/test_evolve_loading.py tests/test_rf8_structure.py tests/test_pyrel_export.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py tests/test_rf8_sessions.py 'tests/test_rf5_commands.py::test_historical_cli_name_is_the_defining_object[_cmd_check_batch]' 'tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_cmd_check_batch]' --tb=short
  exit: 0
  output: 1017 passed, 3 deselected in 274.53s (0:04:34)
  note: Executed with this checkout's .venv/bin/pytest and locked dependencies; uv 0.10.10 launcher is the canonical spelling. Default exclusions preserved.
- command: uv run ruff check src tests
  exit: 1
  output: Found 13 errors.
  note: Exactly the baseline's 13 code/path/line/column findings, independently reproduced on beast-3 at 459ca8d2. Not a green lint gate.
- command: uv tool run --from uv==0.10.10 uv run pytest -q --tb=short
  exit: 1
  output: 6 failed, 18392 passed, 799 deselected, 1 warning in 2324.31s (0:38:44)
  note: Frozen separately executed beast-3 baseline459ca8d2.
- command: uv tool run --from uv==0.10.10 uv run pytest -q --tb=short
  exit: 1
  output: 6 failed, 18609 passed, 801 deselected, 1 warning in 3941.86s (1:05:41)
  note: Corrected candidate64a42f12, beast-3; same six named failures as the independently executed baseline.
- command: python3 .gnd-planning/milestones/model-composition/evidence/MC1/full-comparison.py .gnd-planning/milestones/model-composition/evidence/MC1/baseline-full-default.txt .gnd-planning/milestones/model-composition/evidence/MC1/candidate-corrected-full-default.txt
  exit: 0
  note: Retained full-comparison.json contains exact observed failure-set equality; both suites remain nonzero
- command: python3 scripts/components_index.py changed --base a7c7cf46 --strict
  exit: 0
  note: Zero failures/warnings;44 unchanged descriptions reread and still accurate; final catalog ownership corrected separately.
- command: python3 scripts/components_index.py --check --strict
  exit: 1
  note: 'Initial finalization check: pre-existing checker/_composed.py assignment missing; reproduced on base, then corrected in catalog only.'
- command: python3 scripts/components_index.py --check --strict
  exit: 0
  note: Final after catalog-only ownership correction and regeneration.
- command: git diff --check
  exit: 0
- command: 'ruling: delegated (auto=true) approved .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md sha256 ce2a8d42a10ca15fbfbba918eb5f000cef08386e1adaedc8c5c798f0d97b0f57'
  exit: n/a -- ruling
slow_gate:
  command: uv tool run --from uv==0.10.10 uv run pytest -q -s -m "evidence or census" tests/test_mc1_census.py --tb=short
  exit: 0
  output: 2 passed in 15.26s
  note: Explicit owner-selected MC1 comparison,400 original members plus3 additions; no other excluded lane selected.
evidence:
- path: .gnd-planning/milestones/model-composition/006-MC1-candidate.md
  sha256: eefc00c3e247c993a825009aebe5132495a14c04c014295cb829e4793d1b8e96
- path: .gnd-planning/milestones/model-composition/007-MC1-followup-gate.md
  sha256: 295f1bf100026b941c29fbd998e6526cad3f518b92a4c7f4f8aefd661a219ad4
- path: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md
  sha256: ce2a8d42a10ca15fbfbba918eb5f000cef08386e1adaedc8c5c798f0d97b0f57
- path: .gnd-planning/milestones/model-composition/evidence/MC1/completion-evidence-manifest.json
  sha256: 4b009dfaa891589937ce5d67b28d25fcf6e8a131414eb66ae97006d5704d9533
- path: .gnd-planning/milestones/model-composition/evidence/MC1/followup-runtime-manifest.json
  sha256: 3c12780a65ff33f6d1f7c6f1ca7b707920f6e43da244a9c86a547de76cf5f286
- path: .gnd-planning/milestones/model-composition/evidence/MC1/candidate-corrected-full-default.txt
  sha256: 64adfa030c3a9cdb267d568c76a73c7cdad5c44ae8fb8952c92af6890d19444c
- path: .gnd-planning/milestones/model-composition/evidence/MC1/full-comparison.json
  sha256: e7ed4923d64e372314d20a2237ef0983d1ab7bc3b543cf3478e3785b1398486d
- path: .gnd-planning/milestones/model-composition/evidence/MC1/candidate-corrected-census.txt
  sha256: 5c47cbb42665605d74ce452fff57da65d890eea89ccc9c84c75b4fe60b26b388
- path: .gnd-planning/milestones/model-composition/evidence/MC1/final-size.json
  sha256: ceec493434e7148bb0551acb7c725f67584657c570073f46e3c5d93f035b7da3
- path: .gnd-planning/milestones/model-composition/notes/phase-MC1-codex-confirmation.md
  sha256: ab08d3e130ce1b558c94aaed6033ee429e4b515be7ceda8e4bfec033b5edb021
- path: .gnd-planning/milestones/model-composition/notes/phase-MC1-harness-review.md
  sha256: ba95adfe9474db4a3222aa7fdd7d9c646c03d03e721371c673c9e5cdd4b15341
---

# Claim

The MC1 focused selection exited0 and its marked compatibility census exited0. The full candidate default suite exited 1; its observed failure set equals the six frozen baseline failures exactly, with no added or removed failure. The lint gate exited1 with exactly13 frozen baseline errors. These remain separate observations.

## What shipped

The rooted loader resolves depth-one confined, pinned version-5 vocabulary includes, composes own declarations before included declarations, and appends owned inline rules to included fact types. Private structural provenance retains authored warning/error coordinates without changing serialized identity surfaces. The new explicit-root bytes entry point binds references under the same retained root; unrooted bytes still refuse includes as unresolved.

Schema and synchronized skill schema admit the envelope, attachments, references and temporal version5 features. One wrapping serializer omits empty include fields from both dump entry points. Acyclic shared parser, exception and path homes retain identity/module aliases and zero architecture allowances. Existing identity functions and embedded PyRel runtime are unchanged.

Every inventoried unsupported direct-byte, copy, hash/currency and raw export admission refuses before work through shared guards. Existing closed adapters retain their wire shapes. Refused batch metadata contains an authentic raw captured-byte hash after refusal and never a positive freshness claim. Independently authored include/twin and population fixtures exercise actual validate/check text and JSON behavior.

## Criteria audit

| Criterion | Measured evidence |
|---|---|
| MC1-C1 | T2/T4/T32/T33 committed hand-flattened twins: clean0, cyclic/self1, both commands and formats; non-allowlisted fields equal and allowlisted identities independently calculated |
| MC1-C2/C3 | Direct and CLI refusal matrix; compound-fault ordering spies; value-free distinct include reason IDs, exact hash/schema spelling parity;17 reproduced review regressions |
| MC1-C4 | T22 merge-layer medians:16k/4k ratio4.322745525305249 <=6; quadratic mutant15.180779585637014 >6 |
| MC1-C5 | beast-3 marked census2 passed:400 baseline members,3 added; each frozen load/dump/dump_json/digest/identity/validate observation compared independently, including refusals |
| MC1-C6 | T25/T26 unrooted include refusal and rooted composition/reference binding |
| MC1-C7 | T27/T28/T29 version5 reference ownership and operation write refusal |
| MC1-C8 | T32/T33 attached acyclic/mandatory rules on included facts; T18 own/unknown target refusal |
| MC1-C9 | Branch matrix: own operations/derivations/subtypes/history, notes order, source direction, anonymous provenance, own selector preservation |
| MC1-C10 | Separate actual consumer admission controls R1–R32, with explicit standalone script and untouched runtime boundaries; full default affected-consumer suites and regression controls |
| MC1-C11 | T40/T47 plain version5 temporal and T48 included temporal versions3/4 |

The full selected candidate suite runs the ordinary affected-consumer suites under unchanged default exclusions. Excluded historical/native lanes are not claimed as executed. The broad selection here names only the already authorized MC1 census tests.

## Gate output (verbatim)

Focused:

    1017 passed, 3 deselected in 274.53s (0:04:34)
    exit0

Frozen full/default baseline on beast-3,459ca8d293eeef79110c8def26ae7b061d5a8fd5:

    6 failed, 18392 passed, 799 deselected, 1 warning in 2324.31s (0:38:44)
    exit1

Corrected candidate full/default on beast-3,64a42f1243e55dab05ec43c19ceb882e7bee13d7:

    6 failed, 18609 passed, 801 deselected, 1 warning in 3941.86s (1:05:41)
    exit 1

Marked candidate census:

    baseline_members=400 added_members=3
    ..
    2 passed in 15.26s
    exit0

Lint:

    Found 13 errors.
    exit1

Components changed/base strict check: exit0, zero failures and warnings; retained output names every reread. Final full catalog --check --strict: exit0 after assigning the pre-existing CT2 checker/_composed.py to checker.evaluate. The initial full catalog check exited1 for this missing assignment; a complete tracked archive at a7c7cf46 reproduces it (and additionally its historical stale tools page). An earlier incomplete archive probe lacked tests/examples and is not baseline evidence. This cleanup changes only catalog assignment and its generated graph/module view; production/tests/schema remain exactly the corrected64 snapshot. No new reviewer opinion is claimed over this metadata-only cleanup. git diff --check: exit0. The canonical uv command spelling and direct local .venv launcher equivalence are retained in record006; beast-3 used pinned uv0.10.10 with locked dependencies and Python3.11.18.

## Known reds and source isolation

Frozen baseline source was checked out separately on beast-3 before implementation. Its source/test/docs/config/layer-map Git objects are identical to production phase base a7c7cf46; the intervening commits contain planning and the standalone observation producer. Both baseline and candidate source coordinates, runtime and final status are retained. Planning inputs differed between the baseline and phase base, so source-tree equality is not full test-input equivalence. Exact observed failure-set comparison is the measured claim. Ignored resource bytecode is measured separately from tracked git status; empty before/after resource cache inventories are required for this corrected run. The corrected candidate tree is detached at64a42f12 and imports its own src/gnd, not the local working tree.

Expected default failures are the grow-a-model short-prose assertion and five RF5 body pins (_cmd_evolve_apply, _cmd_evolve_preview, _cmd_validate, _evolve_emit_claim, _evolve_error_exit). The comparison instrument requires exact failure-set equality and consistent count/summary, not merely a nonzero exit. Its controls accept the unchanged six-failure baseline and refuse changed IDs, an incomplete summary and inconsistent summary counts. They do not turn either suite green. Lint's exact13 code/path/line/column findings also match the independently reproduced baseline.

## Independent review

One reviewer is one reviewer. The selected Codex CLI reviewed the diff read-only through stdin. Its first round found nine reproduced problems; disposition and scope remain in the retained output. All17 corrected regression cases were observed red pre-fix, then green after repairs;3 legacy controls also exited0. Invalid first attempts are retained and labelled rather than counted as reproductions. One bounded confirmation approved the repairs with no findings, inspecting aliases, source pins, serializer controls and frozen sample observations. It did not run the full suite or establish census acceptance; the separately selected runs provide those observations. The declared production review budget is exhausted.

The initial default run at c7fc66dd was rejected:25 failed,18564 passed,801 deselected,1 warning in2518.63s. All19 additional failures were reproduced as exact source/scan/snapshot inventory gaps or resource-cache pollution. Seven defining-body and two raw-view successors retain their exact historical predecessors, the two new loader homes enter the existing scan, and eight immutable snapshots bind to their actual original homes by digest. A narrowly scoped standalone-script test import now suppresses bytecode instead of changing the installer golden. No production/schema byte changed.

Record007 selected one bounded independent test/inventory review; it returned approve, no findings. It executed AST/hash and in-memory chain/body controls, not pytest, lint, installer execution or tracked-archive closure. A later self-audit corrected two newly authored after.raw_sha256 observations to the predecessor's ast.get_source_segment convention. The new control was observed red first, then35 raw/chain controls passed. That correction and test are outside the review opinion's exact bytes. The invalid attempt to rebind inherited before raw observations to a newer base is retained and rejected. No additional review round is selected.

## Delegated phase ruling

Delegated approval(auto=true),2026-11-10, under the current owner request `process-milestone model-composition auto`: accept MC1's measured criteria on64a42f12 (production/schema bytes unchanged from c7fc66dd), retaining the six known default failures and13 known lint errors as explicit non-green residuals. Records002–005 and their exact approved spec snapshots retain the approval chain; this ruling is not the owner's personal reading. The selected close instrument remains one Codex CLI reviewer under the explicit current owner override of the panel requirement; that close review has not run. No criterion is waived and no additional historical suite is selected.

Owner size authority remains the explicit1100-source/1900-test stop, MC1 only. Final conservative gross additions are818 production/schema and1392 test/support lines against a7c7cf46, including moved bodies, schema twin and changed source-pin controls; net713/1386. Including173 added fixture lines gives1565 test/support/fixture additions, also below1900. This exceeds the original source estimate and records the calibration rather than changing the original estimate retrospectively.

## Refactoring review

Refactors EXECUTED: parser/exception/confined-path homes were made acyclic with explicit identity aliases and preserved defining metadata; empty-field policy was reduced to one wrapping serializer; raw export adapters share one include-reason selector. Current focused/census/alias/source-scan controls exercise these moves. No additional structure change is needed for this bounded loader/guard surface. Source-pin successors retain predecessors and exact new bodies; no blanket exemption or ModelIndex policy waiver was added.

## Refuted premises

- The plan's fixed census membership needed to admit required new fixtures while preserving all400 original observations. Record003 preserves the amendment; the candidate reports three additions explicitly. Milestone close repairs the plan wording with provenance.
- Literal guard-before-any-hash wording conflicts with trusted bounded-reader snapshots and the existing closed refused-batch report digest. Record005 clarifies authentic intake/refusal metadata versus positive currency, without weakening same-invocation dependency verification. Milestone close repairs that wording.
- The initial test-inventory and resource-cleanliness assumptions were refuted by the19 additional failures. The corrected full comparison, exact successor controls and independent test-repair review discharge this MC1 follow-up; no historical predecessor or installer golden was rewritten.
- Original size estimate did not fit the complete guard surface. The measured stop and owner exception are retained in record004 and size evidence.

## Boundary

A completed walk of these steps is not an acceptance claim beyond the stated gates. The adversarial review is one reviewer's reading, not a proof of correctness. The bounded census and timing controls do not prove compatibility over arbitrary programs or hosts. Neither default suite nor lint is green. No unsupported copy/export/currency route is enabled by this phase. MC2's verbalization/support, MC3's ownership/repin/writers, MC4's documentation and the independent milestone close remain outstanding. PR154 is a topic PR; main merge, the owner's after-merge docs reaction, issue95 closure, publication and certification remain unestablished.

## Open questions

- MC2: re-read and disposition every admission row, including R31/R32; add MD9 model headers and bounded support through the single resolver.
- MC3: owned writer/re-pin/snapshot/CAS/recovery obligations remain mandatory.
- MC4-draft: only after MC1 merges, prepare the runnable how-to and rendered owner checkpoint; record an actual reaction before MC4 continues.
- MC4: dispose MD17 explicitly before selecting the business tutorial scope.
- Close: canonical plan repairs for census membership and hash wording, exact final-source default comparison and independent Codex CLI close review under the owner's panel override; question sweep and actual on-main exit predicates.
- Repository maintenance owner: six known default reds and13 lint errors remain outside this phase; no fix or blanket waiver is silently claimed.
