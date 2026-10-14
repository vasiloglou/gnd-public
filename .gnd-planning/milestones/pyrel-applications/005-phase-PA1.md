---
milestone: pyrel-applications
station: phase-PA1
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PA1
date: 2026-10-13
source_base: 04ebec9
gate:
  command: ".venv/bin/python -m pytest -q tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_review_regressions.py tests/test_pyrel_application_corpus.py tests/test_pyrel_application_driver.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_public_pyrel_export_runtime_optional.py tests/test_public_pyrel_export_runtime_support.py tests/test_external_runtime_tutorials.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf2_pre_move_pins.py::test_standalone_pyrel_output_bytes tests/test_rf1_semantic_pins.py::test_resolver 'tests/test_rf1_semantic_pins.py::test_datetime_site[export.pyrel_runtime._valid_temporal]' 'tests/test_rf1_helper_pins.py::test_helper[yaml_guard|gnd.export.pyrel_runtime:_load_yaml]' 'tests/test_rf1_helper_pins.py::test_helper[safe_filesystem|gnd.export.pyrel_runtime:write_new]' tests/test_rf7_consumers.py::test_primitive_nonboolean_inheritance --tb=short"
  exit: 0
  output: "358 passed, 22 deselected in 31.56s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately scoped CI
  reason: direct profile and affected consumers selected; configured broad exclusions preserved
evidence:
  - {"path": "src/gnd/export/pyrel_runtime.py", "sha256": "e91b4c7b62f995d9c3630393edfa8154f807e232b3c3a665018a874b543bd803"}
  - {"path": "tests/test_pyrel_application_acceptance.py", "sha256": "074082ab1663cafab9d90d973ac42ede1c5148180e314fea928be498f0ad8225"}
  - {"path": "tests/test_pyrel_application_native.py", "sha256": "14bf90db55c11b211d0679196ef2e798f1a7fcfebb3e65e175386c96f030628a"}
  - {"path": "tests/test_pyrel_application_review_regressions.py", "sha256": "350f5da5d9d1fb9308c28d0ff2aaacfb7f16e076ecea0dd1225c074033b5769a"}
  - {"path": "tests/support/pyrel_application_successors.py", "sha256": "4c5f980e54e2fe38c1ce753b127820d3ecc957e3aee7d45a3cf648f7d0cdc917"}
  - {"path": "tests/test_rf6_query_policy.py", "sha256": "77dc9e0e4f90536c8d7ce8e41bfd8b6d60021fd7bce3ccd2d4012ce450324444"}
  - {"path": "tests/test_rf2_pre_move_pins.py", "sha256": "75b46973f6c6257625dd0c557002f4862d28bbc0e484f52d0b016e7db362455f"}
  - {"path": "tools/measure_pyrel_applications.py", "sha256": "81243d946c7e0960057d3f06272002889c46fd1ce7e7d24da0de9a19adeb4c43"}
  - {"path": "tools/gnd_layers.json", "sha256": "324635e4880ee68ef83c84a0e65f3ce07952908150c9f412a2f74319b7f7c4df"}
  - {"path": "tests/fixtures/pyrel_applications/approval.json", "sha256": "b380a31b92297a00d66997ad87da790ee51868bb4a33b984d525c15a36f735b7"}
  - {"path": "tests/fixtures/pyrel_applications/matrix.json", "sha256": "4fbb82a5188d60ff27f10d0cba462744e0cc6cce050eb8a9e5733862ca3ba57c"}
  - {"path": "tests/fixtures/pyrel_applications/answers.json", "sha256": "db902a387cbbae4b1c87bf0bafed03e66f27b9741439d980e808a716998a00ba"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/004-phase-PA0.md", "sha256": "03cc65cfea0a3fe1246d76334d204f20622498bc3fb1e62aa5c7cd6c19918630"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA1-spec.md", "sha256": "61464ad8153ed73e8a7ad090106b0bae98d8ce1e63158b5fcd353ccd7fb7257b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-review-authorization.md", "sha256": "a71c167c1faf2b0a154b6526f6a478ae80a1fce7c006b9a29a74151a375d9907"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA1-review-prompt.md", "sha256": "85e78990d4796a1ed1f058a1715a31a87610f3ec1fe9c52ebe0be9fc0de6e065"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA1-repair-review-prompt.md", "sha256": "60fd071ce1ff7492bf6cc1ac98f6a75cf8e0db07d1ced6874acfc365cb8f87a9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA1-claude-review.md", "sha256": "be4719216306e11ea92dd8421e7f61df9bc9156f5b132b26f3fa38894cd971eb"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA1-claude-repair-review.md", "sha256": "3cf5378e9064e045ba25871918e3d25b4ed787e3bb627199313a97827200ef14"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/L1-green.txt", "sha256": "09229b326b028651d725fa47cd1bae9fd8e0145ff8779bdb84ae2762c00ab737"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/L1-red.txt", "sha256": "c3bc06fa875ec91acdc923da255d2d789ed4e4ad08206c842adff6d59ab96dca"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/admission-final.txt", "sha256": "018bdb93b015d02ca7d3bbe274f589d61841c05d3133770807b8735299930b33"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/completion-byte-bindings.json", "sha256": "383dcd9ab6de7df8f7be180d9bda8e3e12114201be449d8ce95f8049ae3cc3c8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/completion-focused.txt", "sha256": "ab6d70fd51ae38fef2814ee83f492e90bf19ff30f3e93dd254aac92389dc8945"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/completion-legacy-identity.json", "sha256": "e828a78e7cfcc8a4dfe1fc1d3c9f4b85868d0df27cf622ef745e1b230329e8cf"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/completion-lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/completion-native-direct.txt", "sha256": "17d6e49016ed7d50b02326836a506d1314f294a17effbc13fb9ba931dafb53c8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/current-byte-bindings.json", "sha256": "39ee3c7f51ebe4d5b2616af6e493801d76db37bb4724bd8d157e1f8f9c2f8860"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/direct-red.txt", "sha256": "9fde0a46e75e00f0a210faefd432dcea62a906a05d2a5d4e25236c77af15d0ca"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/dynamic-query-successor.json", "sha256": "45e516b1f21ec7efaae9773cc8e90a2a9eef882ad9fffde4fa48bbc5caa670b5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/empty-constraint-pre-fix.txt", "sha256": "15d482a07b515974d04d323358b0f88b0883e6493283f3fcaf34fd2c1dcc6629"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/focused-initial.txt", "sha256": "56cafa2e8583361c03b29ef728eccedd55f8fdc12e6af9f367de98d361e39d62"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/focused.txt", "sha256": "7a9603babb5ccac9de7ce49ad87948f095dbbb7ca45bec2012a912787b58fb89"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/legacy-definition-identity-final.json", "sha256": "c7dca4047b9b6de68b7a0211fb0f5b73c7bc34704b1652018c9118f39f94a2ef"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/legacy-definition-identity.json", "sha256": "7acb70ceb57d4c334b728d5d772703e560c4ec3541beaec21035839b1720d045"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-branches-expanded.txt", "sha256": "c50fbfb8ade905a662e4c2b5aec45c293565d9330109d1d191868d25fd4ac331"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-branches-initial.txt", "sha256": "cbae50349a118dfd1ca9f7441bca07e8a93d6187748f40e1ff90d3370ea49254"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-branches.txt", "sha256": "c972b257d505bb1ba3c12af07677ae6c33fd74cacb2197f641d9529df3f962dc"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-direct.txt", "sha256": "818ae35adfb3571d482597167ef7982dea90ef3f742f5c586ef67965d3a3a365"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-final.json", "sha256": "e9d53cf72778d311f3201a55b1175aa4d3f377a81dd5c92bcf20e4d7dac644ae"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-final.txt", "sha256": "2c246e043037e6bc7ec560e2f8f1eb60e0be0a6f3f536c40d725434dc7f2257f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-initial.json", "sha256": "9828bb79027ebad7b3173a243c906a5de180f5b4058b4f2cc071f0ecb216d922"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-initial.txt", "sha256": "2c246e043037e6bc7ec560e2f8f1eb60e0be0a6f3f536c40d725434dc7f2257f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-isolation.json", "sha256": "0a897af3086447770e8168e95b4c78b91b794a11b749113e0061b88f6a671f3e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-repaired.json", "sha256": "2b592412b3e79cd59ebf39bdae718b81e31e101d0bf90b493f31d32b63b89376"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native-repaired.txt", "sha256": "2c246e043037e6bc7ec560e2f8f1eb60e0be0a6f3f536c40d725434dc7f2257f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native.json", "sha256": "de485694a4e9ef2f3e938e2ef2a283f00f82e04437a585b0a39c2e2a3fe09f78"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/native.txt", "sha256": "2c246e043037e6bc7ec560e2f8f1eb60e0be0a6f3f536c40d725434dc7f2257f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/pre-review-runtime.py", "sha256": "51674b423de40b6d270e35e8f1af0dbf820a57f6b39a868490f20a44389d2210"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/pyrel-successor.json", "sha256": "eee901a2511f645e30cb2aeed6cd55ec231279cc4d84a4bdbf0fc56a0ab31309"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/query-successor.json", "sha256": "4fe66e4c713a6b85b9d952cab768c39a1f5e6643cd550ed0b82e1d088d4b921f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/repaired-focused.txt", "sha256": "7a38c750d75a18d7fa4cc4606c08b74c38325aa0350e264816a2f878331b2ef4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/repaired-lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-admitted-red.txt", "sha256": "3a2d2f221f0ada13b613bc5cc373c1cf18390246edea4a0bb8a40e416040771c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-confirmed-red.txt", "sha256": "1ff1aa64c28e3c71f9457ffdab01f72baef77b24a7a0cd99e81bcb5887ac4ba4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-final-red.txt", "sha256": "e9d1b6f9280562cd0098a7ce739b49da25482da2932392cc98a3ba3c4f743ebf"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-final.txt", "sha256": "7ccd332b99e7f21a8fed89cb3da154e7375ada93ff318b50d9b29819ad08c709"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-green.txt", "sha256": "fd95651aafe3417f5269275b70dcb2549493c68369101fe6d64f9666d2cc52f8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-red.txt", "sha256": "9244c329ce95ce84d803142f9c07036c09478c459cc6e25c717afa93d42cba92"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-reproduced-red.txt", "sha256": "c9ef78edfb568af37d5dad8e91ffd4f78005409a6d601e434492e0ae887b1e12"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-native-valid-red.txt", "sha256": "9a33619ae074438257a3ef2c08f87741654124aa13eaa3504110191a51a8d286"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-parent-expanded-red.txt", "sha256": "fd07332bf59dd4668ed7cd281337fbb130e16af48898827029f2886e37d0eb35"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-parent-final.txt", "sha256": "6b53bed6ee0cff6126b58d8efbf19f7578a3fadcc342570da6474aa66504f690"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-parent-green.txt", "sha256": "0fbbf9d0d18e9c832de6c1280fe1f05129a8fafe64eefc776ba81635e815ec64"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA1/review-parent-red.txt", "sha256": "babd111b60c83a2c137e6120a34e5d39fe3647382430e6e38ec4fd9424f111b6"}
---
# Claim

PA1 completes guarded checking and explicit applications-v1 acceptance for the
four admitted BookRec/expense models. The frozen117scenario controls match full
native verdict/witness/modality/binding/status/exit expectations. Complete-model
support remains refused until PA2. This is bounded native application checking,
not a GND-validity certificate or universal ORM equivalence.

## What shipped

The existing standalone runtime adds ApplicationOracle, typed guarded grammar,
closed coverage/profile/work admission, explicit status composition and --accept.
It computes positive/negative/literal comparison fragments in native PyRel and
binds exact embedded-model/population UTF8 bytes at the CLI. Unsupported shape,
coverage, work, unexpected status, vacuity and native error cannot accept.
Modality preserves advisory warnings and strict rejection. Legacy ModelIndex,
PyrelOracle and23existing top-level definitions remain AST-identical; program_main
adds only the opt-in branch. Two one-shot legacy reports match old goldens.

The native profile is local in-memory DuckDB, pinned PyRel1.30.1/DuckDB1.5.5.
Unsupported execution settings produce bound incomplete reports after input
admission. Early raw-size refusal emits stderr reason without a report or partial
hash; API structural JSON caps and caller-owned raw hashes are explicit limits.
The supported subset fragment requires identical declared object types; inline
only uniqueness/mandatory are admitted. No shipped fixture was narrowed.

RF6 exact counted direct/dynamic and RF2 generated-byte successor chains add
current-byte evidence while retaining every historical predecessor. Direct reads
356<=365; original attribute/get metric301<=310. Runtime source stays in its
existing layer home, allowance count0. No shim retirement or skill edits.

## Gate output (verbatim)

Command: .venv/bin/python -m pytest -q tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_review_regressions.py tests/test_pyrel_application_corpus.py tests/test_pyrel_application_driver.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_public_pyrel_export_runtime_optional.py tests/test_public_pyrel_export_runtime_support.py tests/test_external_runtime_tutorials.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf2_pre_move_pins.py::test_standalone_pyrel_output_bytes tests/test_rf1_semantic_pins.py::test_resolver 'tests/test_rf1_semantic_pins.py::test_datetime_site[export.pyrel_runtime._valid_temporal]' 'tests/test_rf1_helper_pins.py::test_helper[yaml_guard|gnd.export.pyrel_runtime:_load_yaml]' 'tests/test_rf1_helper_pins.py::test_helper[safe_filesystem|gnd.export.pyrel_runtime:write_new]' tests/test_rf7_consumers.py::test_primitive_nonboolean_inheritance --tb=short

```text
358 passed, 22 deselected in 31.56s
```

Exit: 0.

Command: .venv/bin/python -m pytest -q -m pyrel_oracle tests/test_pyrel_application_native.py tests/test_pyrel_application_review_regressions.py --tb=short

```text
19 passed, 24 deselected in 21.18s
```

Exit: 0.

Command: .venv/bin/python -m ruff check src/gnd/export/pyrel_runtime.py tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_native.py tests/test_pyrel_application_review_regressions.py tests/support/pyrel_application_successors.py tests/test_rf6_query_policy.py tests/test_rf2_pre_move_pins.py

```text
All checks passed!
```

Exit: 0.

Command: .venv/bin/python tools/measure_pyrel_applications.py --mode acceptance --stage guarded --out .gnd-planning/milestones/pyrel-applications/evidence/PA1/native-final.json

Exit: 0. Full117line console output is native-final.txt. Native JSON records
`"denominator": 117` and `"matched": 117`; every case has matches=true.
Completion-byte-bindings.json re-renders all4programs through public CLI and
asserts equality with every recorded program SHA, binding current runtime bytes
to that execution receipt. Native isolation records gnd_importable=false.


## Independent review, reproduction and dispositions

Claude Code was the explicitly selected distinct read-only phase harness. One
reviewer is one reviewer. Both outputs are retained with sanitization headers;
the reviewer disclosed prohibited read-only/no-op Python commands, executed no
project tests/native tools, and credited no unexecuted gates. Those limitations
remain. The first pass returned8findings; the sole repair pass refuted none of
7repair claims and returned1Low admission finding, no blocker. No third round.

F1's claimed value-vacuity premise was disproved by actual public GND checks:
allowed roster values pass. No erroneous value semantic repair was made. Actual
empty-host mandatory and invalid inline shape controls led to bounded refusals.
F2 repeated-call mandatory/subset ambiguity reproduced and new-profile overrides
use the specific model. F3 malformed selectors/missing role, F5 output66 and F6
unexpected-status acceptance were red before fixes. F4/F8 exit/report details
have explicit delegated contract amendments; F7 counts consequent multiplicity.
All owned regression fixes have pre-fix red receipts; exact pre-review source
bytes are retained. Initial fixture-authoring errors are separately named and
not defect evidence; confirmed/admitted red receipts are the actual reproduction.

L1 from repair round reproduced GND semantic:role-seq-type-compat ill_formed while
native accepted. A same-declared-type admission restriction fixed it; L1-red and
L1-green bind the specific control. These final four added source lines have
owned current-byte checks, not an invented third opinion. N1 adds a size-priority
control; N2 is an explicit malformed-versus-unsupported refusal distinction.

Convergence: round1,7/8self-inflicted,1/8blocking, reviewer ceilingmedium-high;
round2,0/1self-inflicted,0/1blocking, ceilingLow, non-hold. The second round was
budgeted beforehand. The final declared branch audit covers native syntax,
typed scalars, positive and zero joins, duplicates, actual result cap, all input/
declaration/work caps, constructor/evaluation errors, output/binding and mixed
precedence. Additional tests were justified by declared shipment branches.
Source420added lines<=650; direct controls/helper under850line amended budget.

## Refactoring review

None needed. The new profile uses the existing relationship/universe/binder and
constraint traversal, preserving historical evaluator identities. Model-specific
negation overrides are small compatibility seams; moving the legacy functions
would invalidate old byte contracts without helping this delivery. The profile
is one production translation home and imports no GND policy implementation.
Legacy repeated-call negation ambiguity is separately deferred below.

## Boundary -- what this phase does NOT establish

Complete derivations, application queries/publication, repaired/evolved app flows,
tutorial graphics, fresh-wheel acceptance and milestone close remain uncompleted.
The117case denominator excludes exactly20complete-model controls until PA2,
not an undisclosed semantic disagreement. A1's two computed-versus-claim rows
are not executed/credited here. Source validity, source truth, universal ORM
agreement, proof/certification and transition authorization are not established.
No broad repository replay, merge or release was requested or performed.

The dictionary API trusts caller-owned hashes and raw-byte admission; only the
CLI performs measured bounded raw reads. Known vacuity withholds acceptance;
clean zero joins among nonempty covered antecedents are satisfied. Unsupported
inline or cross-type subset shapes honestly refuse; inheritance-compatible
projected subset support is not claimed. Native is optional and isolated.
Current tests are observations over these bytes, not independent formal proof.

## Open questions and carryovers

- PA2: integrate existing structured derivation capability into the standalone
  PyRel acceptance path; compare supplied claims and computed completeness.
- PA3/PA4: actual native calculations, staged-candidate checking and safe outputs.
- PA5/PA6: executed docs/graphics/fresh wheel and explicit agreement denominator.
- Future pyrel-legacy-runtime-maintenance (owner:GNDmaintainers): untouched legacy
  library's global not_ ambiguity under repeated calls. One-shot report goldens
  remain current; the new ApplicationOracle library path is measured repeatedly.
- Existing RF/public-launch/compiled snapshots remain historical authority;
  no source-owned handoff, shim retirement or certificate transfer occurred.

## Refuted premises

The first review's roster/inline-value vacuity argument was false: public GND
returns pass. Preserve the argument and reproduction correction in the spec and
review. Earlier zero-constraint backend-error composition and unexpected-native
status acceptance were false fail-closed premises; specific red/green controls
refute and repair them without claiming universal totality from review alone.

## Delegated completion ruling (auto=true)

The owner's named whole-milestone delegation persists. Record completion from
current-byte focused/native/source-pin/compatibility controls and reproduced
review dispositions. This is an agent ruling, not the owner's personal reading.
No optional panel or new reviewer selection was inferred. PA2's hard prerequisite
is discharged; its own spec/gate/red controls precede further runtime edits.

Completion ruling binds preceding record bytes SHA-256 9fe5ae7800f726515279bd011df1a8128e5e867a807b603b7ddd1036c41c53a5.
