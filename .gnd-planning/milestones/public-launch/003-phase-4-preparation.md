---
milestone: public-launch
station: "phase-4-preparation"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-4-preparation
date: 2026-10-03
gate:
  command: "uv run pytest -q tests/test_release_examples.py tests/test_contributor_preparation.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_runtime_preparation.py tests/test_yaml_comment_neighbor.py tests/test_transition_mapping_totality.py tests/test_public_alias_schema_guards.py tests/test_review_credential_launcher.py tests/test_public_installer.py tests/test_development_scaffold.py::test_readme_reflects_current_runtime_stage --tb=short"
  exit: 0
  output: "98 passed, 1 deselected in 3.76s"
  note: "Focused preparation controls; final Phase 3 acceptance is pending."
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "Only explicit owner or separately configured CI selection"
  reason: "Historical replay, providers, native lanes and certification are outside preparation; no current-byte broad assurance is claimed."
evidence:
  - path: .github/workflows/release.yml
    sha256: ff33d56eedc145894b4066daac580ee036854f3ca7bd7463f902da119e5259a5
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/build-smoke-final.txt
    sha256: b77fcb8279324208d36daff0501fc5924a865dd90ba883048e88c36a11c21e0e
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/focused-final.txt
    sha256: 6209dad2b7412273549da342ed760edf3be8a1adfc5d2694a32fe3cfee7d4a36
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/followup-attempt.txt
    sha256: 89bab49a454b0a73d81732390ae9600b9365411e245814119cd691b21b5d67bf
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/lint-final.txt
    sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/measurements.json
    sha256: 8fcacafa868d88c1d81b7c32654600c5c8b47aba2bbe85026813154cb2eab70c
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/pre-fix-controls.txt
    sha256: 8bdbca49a3822b3447aa7f1d6d2182594a9e8cde388d0291aa1e3d343c071115
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/review-import-red.txt
    sha256: 083d6a6677cea8d3486e3ddd5ff4acfd4402794b901d5d246f0334f1fab140d1
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/review-regressions-red.txt
    sha256: f0a5f6bfd886c5a7434c9ca503e3116418821cd9a7b15b606f637990445131ca
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/staged-closure-before-fix.txt
    sha256: 53bfbd4758c309e843984e092d3843d6806d96b7bb007ba5cdd166be6e78afb4
  - path: .gnd-planning/milestones/public-launch/evidence/phase-4/staged-closure-controls.txt
    sha256: c732d297b42cde41e9fef833c48319520d4d4efb699ce3c0d8333d7ebf8168c6
  - path: .gnd-planning/milestones/public-launch/notes/phase-4-approval.json
    sha256: 9791e41e3c5a709403891df887e58be33b84f835b02a8775c549a2b5f0c6d257
  - path: .gnd-planning/milestones/public-launch/notes/phase-4-codex-review.md
    sha256: 519457f63967932744bbadc0565cea83b3b2f9ae27b02fb6a4dd87ee8a406e80
  - path: .gnd-planning/milestones/public-launch/notes/phase-4-execution-amendment.json
    sha256: d15548d018ed5c5fc42debd48bc5f4a3ed58e77f246cef3e5ce15c74c15ad43d
  - path: .gnd-planning/milestones/public-launch/notes/phase-4-review-amendment.json
    sha256: 1bbf21fcff90d0d47616e2ba113b1d1e3f50b81a06a103720b0462368d75df67
  - path: .gnd-planning/milestones/public-launch/notes/phase-4-spec.md
    sha256: 3bdec9f51222d202e45a7142454ee9a41ed03781fdeb7e0c6a3d6f6d014b40e7
  - path: .gnd-planning/milestones/public-launch/notes/release-dossier.md
    sha256: 0dd648c9ffc56a690108f6c6917e285df5ab03e2c590d350c4607ab237314ae5
  - path: AGENTS.md
    sha256: 12887cca1d12bf6c8a0a92a99e9d5507c0a3da36ea28ad90baca26dff2d642d8
  - path: CONTRIBUTING.md
    sha256: 823f663f13d9662a56e2e455ad2055474f14cbbc7021e7f0ce4861bb6d400e16
  - path: NOTICE
    sha256: b32db7841edaeb6e1176fc0762b93c36484fdbf6c26899cb4d912737ba8ab26e
  - path: README.md
    sha256: bbc767578161d29c07a7aea19d4abccd4b35fbc590cea1688aaacd3e61dc8848
  - path: docs/advanced.md
    sha256: 8950c591cb4ecfd584222ae337862e6bb25c7ddd27de149bb5dd6021e3791a5f
  - path: docs/compatibility.md
    sha256: 34ad050b96e7c8d71b45b4286623110039e7848318a33d58c1c5f06a414584f1
  - path: docs/demo-script.md
    sha256: c758751dae074c3b4ae8c9390f348a1d6dc479b15bb5ba407628277df3b79b2b
  - path: docs/development/bootstrap.md
    sha256: e07ecfb4bc26f6cb50ab77ed2d76b3f555264304ca7f2284f20335b402d9cae4
  - path: docs/development/examples/release-preparation/README.md
    sha256: 681903e26bb8be28eb4f44646dc91750a90bb2ae33ebbba4f34d5bcede261ff1
  - path: docs/development/examples/release-preparation/answers.json
    sha256: c9ce25264d9b914beda7ccfc9b1f4fa1071d0b6018ad99bf2aaf5e45bdcb0eb5
  - path: docs/launch-drafts.md
    sha256: 722f071a9eed7e2e68cd4882f5775feddfb0fec9a122655a5c87428bb58adb96
  - path: docs/quickstart.md
    sha256: f17cca1836b0deace874fff06ea85de10d26c6348b4cf9df3b9326a5616fdae4
  - path: docs/release-notes.md
    sha256: 73be70660a365888f90b49037a4fe6f9fc20f85fa2924784e1b0361472abf944
  - path: docs/releasing.md
    sha256: 9b98bd981ad5bf46a093361dd0ec9d3169359c9743107dbb6ed8e71c2ad02924
  - path: docs/support.md
    sha256: c6368328cb5bf4831988aabb6245c27e9f64577bde1515cd23e35e58ff1218a0
  - path: pyproject.toml
    sha256: f3288283fb1f9c8831cc30fdae2e2b72db6e942b420a365cd0e39419ff679af2
  - path: src/gnd/coverage.py
    sha256: fe2d4ff4fedb617abbabe2cf9eb3a1dece7aa54419f17d8a45516bd6d7f6be41
  - path: src/gnd/examples/dispatch/model.orm.json
    sha256: 55853a680ac28b5860adb1a586c6f7572a7540e9d6fd2788b66c396a8343bb57
  - path: src/gnd/examples/dispatch/references/catalog.pop.json
    sha256: a56ea3ba86db90da81e1bcf11eaf6703e031d73140c7543f2bd501ffcbf066c1
  - path: src/gnd/examples/dispatch/repaired.pop.json
    sha256: bfadb1f4193b1ea86d546eb8470c229d76cc439ade98aaa96529c64622190326
  - path: src/gnd/examples/dispatch/seed.pop.json
    sha256: 3a1171da63ebec6a48573a37e275fd9534aa00cef4558bd7e186686a8c7ba3af
  - path: src/gnd/examples/release/model.orm.json
    sha256: 0d5cb7d5412f46352553e9caa4dcf2871c703bfee6fe7b35eb8200869a2a506e
  - path: src/gnd/examples/release/references/catalog.pop.json
    sha256: 11abdbe28ec6cdf9863a696649da2a80f337c1c79c29bee66c29a0986d159de0
  - path: src/gnd/examples/release/repaired.pop.json
    sha256: 42543697a1576e8354acf17338579b2463fbdad0607ad68e28d168731f770e83
  - path: src/gnd/examples/release/seed.pop.json
    sha256: 2143462dd98000c1c88195eec3469ef37e74c091f47e7691693f6b263d1ee284
  - path: src/gnd/exp/session_v7.py
    sha256: 4ff85a7ac8757eceb6daf3516776ec102e3b83cf29552ae66c9ba48a5f035869
  - path: src/gnd/model.py
    sha256: 799f3d8ab6cd397e8c4e8c71b170e067a5d21787a14b7f3ee72eb3e960e8f5ad
  - path: src/gnd/population.py
    sha256: 5c5740d7038da3dc783971eac2375e11a05aea9614815198d23835d484bfa032
  - path: src/gnd/rai_import.py
    sha256: fcf874927fd602dd4c315af2967951d150ac50153edf1dec418eb8b1268bde30
  - path: src/gnd/report.py
    sha256: 48c378d192e5a3b5624273d787b9b162f8b3125aae40b045d92a374e7a5664c9
  - path: src/gnd/semantic_registry.py
    sha256: 8c9ec42ee6e4f1529255783011351d913a4cff2ec92602f53de4b4e8cef5f88f
  - path: src/gnd/yaml_comments.py
    sha256: d9eaf1505db6c3941a50f44a2e582c2238f2301489eb3a9e12c8c79e1d5ef177
  - path: tests/fixtures/v61-phase1/import/identity.source.orm.yaml
    sha256: 9f19b554ae4055ffbafb644791f913a2c75e58a749d306ee5e43998141081b75
  - path: tests/fixtures/v71/phase4/dispatch/candidate.pop.json
    sha256: 2221961db9f686ef2fb637cab75b356b8c41aebe2e525f445575bc81819db60d
  - path: tests/fixtures/v71/phase4/dispatch/contract-v7.json
    sha256: b2408ba4005aab27bb3850423b52e22e39c6387bfa723b8424b8876d6f564a87
  - path: tests/fixtures/v71/phase4/dispatch/model.orm.yaml
    sha256: 00510c38a1616f04a45e117f11b194a17cb680166871ef825bdb6bed61de4b0a
  - path: tests/fixtures/v71/phase4/dispatch/owned-model.orm.yaml
    sha256: 5977bf78477ccfec698efb108aea4eea406d1cbc4551e3832266719b3c405931
  - path: tests/fixtures/v71/phase4/dispatch/reference-model.orm.yaml
    sha256: bc5b956d3406e2d644abc052b147789674fcf2a33ef8f67702fea9e5ffff47d5
  - path: tests/fixtures/v71/phase4/dispatch/references/catalog.pop.json
    sha256: 0a0a16cffc89b1300965c44dbeaaa95f529716f6589c4a40550e94d91b309691
  - path: tests/fixtures/v71/phase4/wire-fields.json
    sha256: adeca2a5aa28f04640018a9ae674e7e389cdbd6ad81ebea3ee9d6ca3bd1ea44e
  - path: tests/support/v71_session_cases.py
    sha256: ea717aa2725a9085b4e3e872cbd99be8d17223c5c550e9656fe66b40c8fff435
  - path: tests/test_contributor_preparation.py
    sha256: 55671eeb9d5f4e496810daef4df7f9e7cc6f7a919b0269cbfb98e83b1b60d39a
  - path: tests/test_development_scaffold.py
    sha256: 7c079f01dc32c5ac30ceee060a62412d7dc4f1415540ae35b483f537b733cf6e
  - path: tests/test_public_alias_schema_guards.py
    sha256: bdaeda1e2b6534b36dee8ffc686589cad128309b7de06e082e2023e6b64eecf0
  - path: tests/test_release_docs.py
    sha256: 46116e24231d1676ac22f772f578169da9ded23d716b46dec5d70e4de5659a33
  - path: tests/test_release_examples.py
    sha256: 8078a1cfd1187b795d6988efd15e6823d6711632c24fe12b59ada814fae3f70a
  - path: tests/test_release_preparation.py
    sha256: d8204b87d9742213b1f7a2606d73163f74b59358a63083e20902abca22c329af
  - path: tests/test_runtime_preparation.py
    sha256: eb92eec55c25913528a2b7ff0c9e4e38f555ca33c74a6657ed63b373823591dc
  - path: tests/test_transition_mapping_totality.py
    sha256: 8d1c07a2e60e8d8cf4cfd43524cc017b6ae19f956893291f3385d893c5925eb5
  - path: tests/test_yaml_comment_neighbor.py
    sha256: 1c03eea72f7f6d9070faebc8fd6d32ac4bcc15a192065e6ffeaca8c2aec77024
---

# Phase 4 preparation — focused gates exit 0

Preparation completed under the owner's `process-phase 4 auto` and `continue`.
This part does not close Phase 4. Phase 3 remains paused; Phase 4 candidate
sign-off pending. Effective order is r3: preparation → P3 acceptance → P4
sign-off → P5. P0–P2 completion records retain their original boundaries.

## What shipped

Target product/test preparation commit: `5059dba88764cbf4be0e5a661a1fe9187a1657e8`; corpus-first red
commit: `4529d58`. Execution began from target `40bd8958d1df24c0751051e2412535cec53746ce` and source
`3131a974e5e58b4f6d7766ec4ddf82b5df6dbd6a`, with pre-existing dirty P3 work.
Only explicitly selected adaptations and their focused fixture closure were
committed; unrelated P3 changes/deletions remain outside this phase.

- Eight bundled dispatch/release model/population/reference files, CLI/API
  tutorial and exact deadline failure/repair/reference-refusal controls.
- Existing coverage, derivation, session, registry, YAML-scanner and transition
  witness adaptations, identical in source/target at inspection, retained under
  focused positive/refusal/non-mutation tests. MIT attribution ships in scanner
  source and NOTICE. Source runtime changes remain uncommitted there; unit
  authority does not transfer through this preparation commit.
- Metadata/license/project links, target-only contributor instructions, both
  discovery roots, support/version/advanced guides, release/launch/demo drafts,
  correction runbook and a build-only manual release workflow. Release wheel
  and sdist are built once; sdist comparison wheel uses a distinct output path.
- Exact small session/RAI fixture dependencies carried with current tests,
  without copying compressed historical test closures or resuming accounting.

D1–D7 were approved as recommended by **delegated approval (auto=true)**, with
exact spec/corpus identities recorded before implementation. This was not a
human reading. Changed-reference and scanner parity controls are identified
successors, retaining all approved expected answers. The initial eight example
cases returned `8 failed in 0.39s` before package data existed (exit 1); later
runs verified the expected exits rather than replacing them.

## Gate output (verbatim)

From target, default exclusions preserved:

```text
uv run pytest -q tests/test_release_examples.py tests/test_contributor_preparation.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_runtime_preparation.py tests/test_yaml_comment_neighbor.py tests/test_transition_mapping_totality.py tests/test_public_alias_schema_guards.py tests/test_review_credential_launcher.py tests/test_public_installer.py tests/test_development_scaffold.py::test_readme_reflects_current_runtime_stage --tb=short
98 passed, 1 deselected in 3.76s
exit 0

uv run pytest -q -o addopts='' tests/test_release_preparation.py::test_two_wheel_build_import_smoke -s --tb=short
Preparation wheel payload: release 5594547 bytes
Preparation wheel payload: sdist-wheel 5594547 bytes
Preparation artifact identities: [('release', 'b5b7e67dbabe957db7a8cbc2aee992c203457fd2c161e0aaaff00bd3354e3072'), ('sdist-wheel', 'b5b7e67dbabe957db7a8cbc2aee992c203457fd2c161e0aaaff00bd3354e3072'), ('sdist', '323825b0544b9389e083b2b55405afb84b57ceb59920de35d6a667ddd480651d')]
.
1 passed in 3.97s
exit 0

python3 /tmp/gnd-p4-snapshot-check.py
45 passed in 3.41s
EXIT 0

uv sync --locked --group dev
Resolved 22 packages in 3ms
Checked 20 packages in 2ms
exit 0

uv run ruff check src/gnd/coverage.py src/gnd/exp/session_v7.py src/gnd/model.py src/gnd/population.py src/gnd/rai_import.py src/gnd/report.py src/gnd/semantic_registry.py src/gnd/yaml_comments.py tests/test_release_examples.py tests/test_release_preparation.py tests/test_contributor_preparation.py tests/test_release_docs.py tests/test_runtime_preparation.py tests/test_yaml_comment_neighbor.py tests/test_transition_mapping_totality.py tests/test_public_alias_schema_guards.py tests/support/v71_session_cases.py tests/test_development_scaffold.py
All checks passed!
exit 0

git diff --cached --check
(no output)
exit 0
```

The snapshot command materialized only indexed package code plus the listed
consumer/helper/fixture closure into a temporary directory, forced imports
from that package, and excluded the repository root from console-style sys.path.
It reused installed development dependencies; it is not final clean-install/CI
acceptance. The smoke installed each wheel independently in outside-root base
venvs with PYTHONPATH/PYTHONHOME/user-site contamination removed, asserted module
origin, CLI help and example API exits, and absence of Faker/pytest. Preparation
artifacts were temporary: these hashes cannot be promoted from this record.
The final candidate must be built once, retained and validated during resumed P3.

## Review and reproduced findings

One reviewer is one reviewer: gpt-6-astra/xhigh in an ephemeral read-only CLI,
stdin prompt, retained complete response in notes/phase-4-codex-review.md.
It reported two blocking closure defects and two hardening defects. All four
were reproduced and triaged before repair. F1 uses the existing support namespace;
F2 carries the exact missing identity fixture; F3 checks references even when
both twins are equally broken; F4 pins actual comparison output destinations.
Both new guard regressions returned `2 failed in 0.09s` pre-fix (exit 1), then
turned green. Initial index-only controls returned `1 failed, 44 passed in 4.02s`
for the fixture gap. Baseline coverage/model/session/report/registry module
replacements returned `21 failed, 10 passed in 0.96s` (exit 1), against current
focused consumers in an asserted isolated package. This is not a baseline suite
replay. The reviewer independently ran 36 fixture-free tests and 384 scanner
comparisons; those observations remain its bounded reading, not a certificate.

The bounded follow-up CLI entered orchestration rather than returning a review;
it was stopped before nested execution, exit 1, and has no usable opinion. Two
attempts total, one complete response. No convergence or final repaired-byte
review approval is claimed. Neighbor controls and index closure were rerun.

## Measurements and budgets

Observed macOS arm64, Python 3.11.15, uv 0.10.10. Both wheels have 5,594,547
uncompressed bytes <12 MiB; they happened to hash identically, without assuming
that equality. At the measured index boundary: 11,595,847 bytes <64 MiB;
largest blob 584,130 bytes <1 MiB; authored planning prose/notes 176,941 bytes
<2 MiB. All planning Markdown/JSON is also reported separately; larger existing
generated migration manifests are not reclassified as authored prose.

Eight package example files total 12,461 bytes. Both roots have 16 managed links
and two real directories, no discovery edits. Cumulative implementation paths
include selected pre-existing adaptations/fixtures. Existing eight runtime files,
three regression files and session helper alone account for twelve pre-existing
paths, excluded from the original incremental 60-file ceiling. Runtime additions
beyond the reviewed existing adaptations: zero. Full selected test/helper diff
adds 813 lines <900. Measured authored docs/planning before record: 884 lines.
The spec records the delegated documentation ceiling amendment from 1,200 to
1,400 before authoring this record: evidence bindings/status closure need about
250 more lines. All other numerical limits stand; no test was retired to fit.

## Refactoring review

**Refactors EXECUTED.** The contributor and release-doc controls share one local
Markdown reference predicate, preventing two copies from drifting. The existing
transition witness adaptation uses one serialization helper across snapshot,
frame and step witnesses while keeping caller schemas and nonfinite refusals.
The selected gates protect both. No additional structural refactor is needed:
examples are package data, the release workflow has separate artifact origins,
and the existing scanner configuration is shared by all three readers. No
unowned or silently deferred refactor was identified in this bounded work.

## Boundary — what this phase does NOT establish

Phase 3 paused. Phase 4 candidate sign-off pending. Focused preparation is not
full regression acceptance, launch readiness, authority transfer or retirement.
One reviewer is one reviewer; the sandbox could not rebuild/install wheels or
run writing tests, and the follow-up has no complete response. Agreement between
review and implementation does not prove correctness. No broad/history/provider/
native suite or certification ran. Old certificates describe only old bytes;
changed or missing assurance is unavailable.

“a five-minute target and five trial users are targets to measure, not results
asserted by the plan.” No timing/adoption evidence is fabricated. Proposed Ubuntu
3.11/macOS 3.13 profiles remain unaccepted; the observed host does not establish
them. No production upload, TestPyPI rehearsal, announcement, access grant,
push or visibility change occurred. Version 0.1.0 remains provisional. Public
URL availability, publisher configuration and service transport remain untested.

## Open questions and handoff

P3 must be resumed separately, select concise behavior-family regression coverage
against this prepared commit, retain useful pending work and perform final
candidate/clean-install/CI/contributor/profile acceptance. Produce/retain exact
build-once wheel/sdist and separately validate its sdist wheel. P4 sign-off then
binds those tested identities without another implementation round. Rebuilds or
product changes repeat affected checks; P5 publication remains separate.

PL-D5 version/service facts, PL-D9 final profile/size checks and PL-D10 trial/launch
facts remain candidate/launch obligations. TestPyPI omission retains its untested
service boundary. OQ-PUBLIC-LAUNCH-P2-BUILD-PROFILE is narrowed to the observed
uv 0.10.10 preparation profile, not closed for the final matrix. No carried
technical registry row or v7.3 obligation changes state here.

## Refuted premises

Working-tree passes did not establish committed test closure: F1/F2 and the
index-snapshot failure refuted that premise. Identical twins did not establish
valid references, and mentioning both directories did not protect distinct
build outputs: the red guard mutations refuted those premises. Corrections are
recorded at their original spec/review sites. The initial corpus commit omitted
the required closing record-path line in its message; retained history is not
rewritten, and the implementation/completion commits use the required closing path.
