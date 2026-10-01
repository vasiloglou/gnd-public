---
milestone: public-launch
station: "phase-1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-1
date: 2026-10-01
gate:
  command: "python -m pytest -q -p no:cacheprovider tests/test_development_scaffold.py tests/test_review_credential_launcher.py"
  exit: 0
  output: "41 passed in 0.22s"
slow_cadence:
  command: "Not selected"
  trigger: "Explicit owner request or separately scoped CI selection"
  reason: "P1 scaffold only; no broad, native, provider or certification selection"
evidence:
  - path: .claude/skills/plan-review-panel/SKILL.md
    sha256: 97460b6dc090588af3e221998fdd0c7d7de6986cdcb163386ea9231922037a29
  - path: .claude/skills/process-phase/SKILL.md
    sha256: 06b19b5dee6172b12dd590fe7febf2fec22dbb382dbe753926e51ded6639fe31
  - path: .claude/skills/process-phase/references/agent-delegation.md
    sha256: 760bb8bb83791055e1b6288794a79ce87b5034b25a7a11f81cd580dfd4df9f44
  - path: .claude/skills/process-phase/references/architect-overrides.md
    sha256: 46c3cc7077e4643ebe62d1da73a11b6125d55da50aaab6d63a538e03b6dd6a29
  - path: .claude/skills/process-phase/references/review-and-record.md
    sha256: 15be674738becd6ccc21ad4fec0ea4d30471eafb3b266f2df9835ed5f6f0ed17
  - path: .claude/skills/process-phase/references/review-convergence.md
    sha256: fc552bb42d6fe4adf3d6198a73e46cf4ef7dd49cab1f692a3625deb0e533de25
  - path: .claude/skills/process-phase/references/spec-note-contract.md
    sha256: 442aa984f9bcd581e6803f6682401f792516921af429239777502dc3613ad8d7
  - path: .claude/skills/process-phase/references/standing-rules.md
    sha256: 7b73dd55a268def9734d2f5149d4881f6a6efada44785d4aa8e3ba7909d2e956
  - path: .claude/skills/process-phase/references/verification-selection.md
    sha256: b88ee79d4fc3a044d7a03b48f704a75fc5721fca15efdc93edb53a2e34bb4a54
  - path: .codex/skills/plan-review-panel/SKILL.md
    sha256: 97460b6dc090588af3e221998fdd0c7d7de6986cdcb163386ea9231922037a29
  - path: .codex/skills/process-phase/SKILL.md
    sha256: 06b19b5dee6172b12dd590fe7febf2fec22dbb382dbe753926e51ded6639fe31
  - path: .codex/skills/process-phase/references/agent-delegation.md
    sha256: 760bb8bb83791055e1b6288794a79ce87b5034b25a7a11f81cd580dfd4df9f44
  - path: .codex/skills/process-phase/references/architect-overrides.md
    sha256: 46c3cc7077e4643ebe62d1da73a11b6125d55da50aaab6d63a538e03b6dd6a29
  - path: .codex/skills/process-phase/references/review-and-record.md
    sha256: 15be674738becd6ccc21ad4fec0ea4d30471eafb3b266f2df9835ed5f6f0ed17
  - path: .codex/skills/process-phase/references/review-convergence.md
    sha256: fc552bb42d6fe4adf3d6198a73e46cf4ef7dd49cab1f692a3625deb0e533de25
  - path: .codex/skills/process-phase/references/spec-note-contract.md
    sha256: 442aa984f9bcd581e6803f6682401f792516921af429239777502dc3613ad8d7
  - path: .codex/skills/process-phase/references/standing-rules.md
    sha256: 7b73dd55a268def9734d2f5149d4881f6a6efada44785d4aa8e3ba7909d2e956
  - path: .codex/skills/process-phase/references/verification-selection.md
    sha256: b88ee79d4fc3a044d7a03b48f704a75fc5721fca15efdc93edb53a2e34bb4a54
  - path: .github/workflows/development.yml
    sha256: af43e3d35763ef8eb928361589399c7402eb1afefe5e4516e6354abc93e15646
  - path: .gitignore
    sha256: 6f7117bb5ac9898c72b2fec52ce75f6797f05a2095ef446e5370e5538844bc5d
  - path: .gnd-planning/PROJECT.md
    sha256: b92bf222f101ca35c81bb03e57639406b45a6e579cc2469192023276bcf92b36
  - path: .gnd-planning/milestones/public-launch/migration/b1-files.json
    sha256: 7e2bcccd41671743fdcedad2a856c78b59da7265256c0955256964554bb29c87
  - path: .gnd-planning/milestones/public-launch/migration/coverage.md
    sha256: d241eb5463bf6287222b04c1845e798bf041c3a631e4d132834bec027c20bbae
  - path: .gnd-planning/milestones/public-launch/migration/decisions.md
    sha256: 5223100c034c2a8164baafc6fd78fa0a476ccd688d500aee1a92e5a1e2fe8fad
  - path: .gnd-planning/milestones/public-launch/migration/history-map.md
    sha256: 5c0fac922c1ba1f6272ca6de75be5550afa847942c4242170f74047dc3d4b297
  - path: .gnd-planning/milestones/public-launch/migration/obligations.md
    sha256: 56e4c7272d4a28efe0dfc64b2b2aea7697b2ab467a9a8c9e0eedef4532551f53
  - path: .gnd-planning/milestones/public-launch/migration/units.json
    sha256: 8a4d3a8b90c39ecac613af69723cc82ee75b8a1d8b70709a5481c31ab97c7650
  - path: .gnd-planning/milestones/public-launch/notes/owner-rulings.md
    sha256: 31bfd40b5391a4a934c6d5d822324e237bdd5c2777b1cfaeacac34427b921a36
  - path: .gnd-planning/milestones/public-launch/notes/phase-0-summary.md
    sha256: 6e250479bf571acf2891bc30e1775ade7eaa463146fe268a6647780b5a9b1187
  - path: .gnd-planning/milestones/public-launch/notes/phase-1-spec.md
    sha256: fab5b1eb0905cc05b8838b75120f997253c1bc7adc69cc3c051de6f877d1cff2
  - path: .gnd-planning/milestones/public-launch/notes/public-launch-manifesto-and-plan.md
    sha256: 857f113944db0307489132859a296a81a7e8a43c2c041a64d51ffa948261de7e
  - path: .gnd-planning/milestones/public-launch/notes/public-launch-plan-r2-amendments.md
    sha256: 76bafe0ac26d0daec6c0449009bcd1ff2b333d38bb965eaf1dd96e90f0970470
  - path: .gnd-planning/milestones/public-launch/notes/review-summary.md
    sha256: 13105eec65b81f095ebde2d920c5843e900c8aeee44eb06669fbf488fea5f4fa
  - path: .gnd-planning/open-questions.md
    sha256: e3544d58715b4920e601a910a63c33fc7853d032d7dc0da993f8f79dde90abe7
  - path: AGENTS.md
    sha256: db3e24b35d15cc6f997e65ebb2666142d1c0e306721d06d44e00306fe2f1b8ea
  - path: CONTRIBUTING.md
    sha256: bf00c14334b5822a495c22f57c02a10f77adc49d27f63dff0bdbdfe137a6f2b4
  - path: LICENSE
    sha256: 62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a
  - path: NOTICE
    sha256: 487d6e44fff99229619c02e9b05b979ae865bd900b0b046d0837cf85fab05b40
  - path: README.md
    sha256: 32924937e5977d802a73ace83a0422fbecc27b87504aa047aaa2775f27f6db2c
  - path: SECURITY.md
    sha256: d0cd05a9d46348df73661d03f61cf15d216c80a472183520bd69aa0bc325fc99
  - path: docs/development/bootstrap.md
    sha256: 7001197e09b50ee77a3b10261033006c460ef60ab5652ce27558665cca21f5da
  - path: docs/development/examples/phase-record.md
    sha256: 9ccde9fd2385a29fbd6853a424c17ec41d58c4e52b03dc91d0d24315a67043b3
  - path: docs/development/examples/phase-spec.md
    sha256: daf39ccc602c0443b7ea364f64dbda2264b8a455ddff56c7fa4a7560a6cc9424
  - path: requirements-dev.txt
    sha256: 93c4ab5f175d24229e46ec70a8ecaeb6db8b36e3f54d8005808044c060acbc92
  - path: src/gnd/skills/gnd-adopt/SKILL.md
    sha256: acff4dc97170eeff69e4c42c4f30bde73e6f643014280c4fb4f1867c30682e7d
  - path: src/gnd/skills/gnd-adopt/references/gsd-environment-cleanup.md
    sha256: 365e0a0e436f1110b8cc4c831520b22b3a1bdd6479b820499bab9c439f4efa3f
  - path: src/gnd/skills/gnd-adopt/references/gsd-mapping.md
    sha256: d28743e481611b2456eeb6cce9685a1bdcb96b0999a40756e8173f7b8e45aaf7
  - path: src/gnd/skills/gnd-codegen/SKILL.md
    sha256: a22bbee300f800efc577d357748b61fc9910bfcfb5d5ebbea8336790a7c5dc42
  - path: src/gnd/skills/gnd-codegen/references/architecture-contract.md
    sha256: 39404f214b048eb94b7c602539125f61b9b00089d2b7f2f92d0fecb89b51c3fb
  - path: src/gnd/skills/gnd-codegen/references/codegen-contract.md
    sha256: d5065310f96af8407a26b616871c8602ae911a4dbede1355f2eab6fc093b83da
  - path: src/gnd/skills/gnd-conformance/SKILL.md
    sha256: 1a7f19003e9ca58e2da87a56f631de8a128ee7fa05cf3ff70e2954e5e805355a
  - path: src/gnd/skills/gnd-conformance/references/conformance-contract.md
    sha256: dcfaedb886f61810c66bd6ffef3af975b95e0b7f02467d11027ebcc2559f4b2a
  - path: src/gnd/skills/gnd-dev-session/SKILL.md
    sha256: 5862b3450c793599186aadc30e5a366e1213cbb96ff7d3b59ca772b5d4cf287d
  - path: src/gnd/skills/gnd-dev-session/references/judgment-contract.md
    sha256: 5f46027bb1ae8591b77f5082012af6002a6ad59a18bad8230f252707b283360b
  - path: src/gnd/skills/gnd-dev-session/references/session-v7-contract.md
    sha256: e0038cbe1bf51b5072ee85a0ba419c5d82104f0f3baa3910871f315be5bb1c6a
  - path: src/gnd/skills/gnd-export/SKILL.md
    sha256: 40016cb5813a17592e015885319cb4329ad4406e5ae55f1889c32fed55a475c6
  - path: src/gnd/skills/gnd-export/references/export-contract.md
    sha256: d0c0cb3d32d8059beff10be7c83d0aeec933213b10fff8025c0e0702602f1ff4
  - path: src/gnd/skills/gnd-export/references/witness-contract.md
    sha256: cfbbc8fa3cca2fa22f85ec59d92a4ad730ef0dfe48258ed485b7ce4f80772b55
  - path: src/gnd/skills/gnd-export/references/witness.schema.json
    sha256: 52e120fdb56dae1ce114d2c3a600c719057381adc3ccfe8eb88f17656a1b0345
  - path: src/gnd/skills/gnd-extract/SKILL.md
    sha256: 0115c3c0e7d4183520a215ee17ccfda8b0ed1e68d69f50d91cce47db348bc46f
  - path: src/gnd/skills/gnd-extract/references/extraction-contract.md
    sha256: 78296c4a80b0655085fe3423d07cab128d15ba90444c4dfa7e356f86a17090b3
  - path: src/gnd/skills/gnd-model-evolve/SKILL.md
    sha256: e818c3e66d5bbbfa7802ab5bd4509c4eb3bc2dd31e0316b473e375a456d7e572
  - path: src/gnd/skills/gnd-model-evolve/references/evolution-contract.md
    sha256: f30e6b2d946c1472e6450a793df67f0b11a14a562350403c28f2a2fad7111442
  - path: src/gnd/skills/gnd-model-from-code/SKILL.md
    sha256: 74270e4d10c277724cc5081b30ee99788ce2885e2c60a5085c47dedc456f85f5
  - path: src/gnd/skills/gnd-model-from-code/references/recovery-contract.md
    sha256: 0383e695bd47efb214f06be04f6fd2897a643b0cca4a5d2f517e4a729fd6d641
  - path: src/gnd/skills/gnd-model-from-text/SKILL.md
    sha256: ad156002a528eed796db1c8f9eeeb14d12bdb4c1f7150939381973fa3e5ee18b
  - path: src/gnd/skills/gnd-model-from-text/examples/library_with_subtypes.dialogue.md
    sha256: e6b4df87518fa54ea40fa55929ffd062fcc7e9c1bfaf35deedf4e487ff36a807
  - path: src/gnd/skills/gnd-model-from-text/examples/library_with_subtypes.orm.yaml
    sha256: adb509e8f267a884f00f8b1f0f1c04e3646a435963fcba8d72d4e8042a61b3c5
  - path: src/gnd/skills/gnd-model-from-text/examples/movie_catalog.dialogue.md
    sha256: b9ccee069f5a210f1971766c1d9ec1fe049e70de60bcdba6b336e051f3dcd047
  - path: src/gnd/skills/gnd-model-from-text/examples/movie_catalog.orm.yaml
    sha256: 19e49d6b8e78361b95203367fd060e7daac6eac9a38e3b621790c1c93ce563b3
  - path: src/gnd/skills/gnd-model-from-text/examples/objectification_in_enrollment.dialogue.md
    sha256: 0a1c3595df369cfca11e5f7b1b3266ad4bcb42c2c19a9adcf226747bf262c7aa
  - path: src/gnd/skills/gnd-model-from-text/examples/objectification_in_enrollment.orm.yaml
    sha256: fe775a5b01288c2ee11149334f9876120db1a79878274b55571d6f9034add78e
  - path: src/gnd/skills/gnd-model-from-text/examples/reference_scheme_elicitation.dialogue.md
    sha256: 6ad69c69808e2064e5c2c06a19e8209d35ec5481faa549248ebfed7e965f0a56
  - path: src/gnd/skills/gnd-model-from-text/examples/reference_scheme_elicitation.orm.yaml
    sha256: 36cf4f5fb6243af4aaf195e4595f5fc02f420664a826258cd4b1c95c5d3e672a
  - path: src/gnd/skills/gnd-model-from-text/references/csdp-workflow.md
    sha256: b08aed291efb73b5d2116a08a27a232c3cac859f3b4ce62feecaaef737f6f834
  - path: src/gnd/skills/gnd-model-from-text/references/dialogue-patterns.md
    sha256: e1f6752cf12f9848ef776227ea9d9f7bf8b7d36fa5c4306b15db7f500b58b6a6
  - path: src/gnd/skills/gnd-model-from-text/scripts/validate_model.py
    sha256: 8c92e8140146da438e452482649d50c56a38c3c146d4f6f66443f0be7ca95c79
  - path: src/gnd/skills/gnd-new-project/SKILL.md
    sha256: 1537847880226817373717cb33077cce0ec866c571097bdb3e42510538d68598
  - path: src/gnd/skills/gnd-orm-core/SKILL.md
    sha256: 57d868a5046bb88236db9fcff7adbb7b127470161daecaa3b2b5375bcb590b7b
  - path: src/gnd/skills/gnd-orm-core/references/constraint-inference.md
    sha256: 954643cc68f6f8dad798f4d426543d660ddb4c6d1276189ab37b1813e63a9dfc
  - path: src/gnd/skills/gnd-orm-core/references/constraint-reference.md
    sha256: f9949f570804d100e890f8e0e4c51222ee8fd7474a4ac1e187226291a3e27fbc
  - path: src/gnd/skills/gnd-orm-core/references/coverage-and-element-addressing.md
    sha256: 2b4a8ee8205297aadbe47fcfb9ba688eb534ee0e2dcfd9a18147b42a16eebd20
  - path: src/gnd/skills/gnd-orm-core/references/halpin-posture.md
    sha256: ad0accef061eea27ec8697a32bb6462ad2f7eeb7bd9aff0a352953f14b9ec50d
  - path: src/gnd/skills/gnd-orm-core/references/milestone-record-format.md
    sha256: bfe007b9cd86ee7cf55926da094a39760b080c4694977b8e62cd2bcbe869b154
  - path: src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json
    sha256: 462d541a6db48eceb63b9d5b456599def4db923319b1edb3e8fcf1bd3cbc856c
  - path: src/gnd/skills/gnd-orm-core/references/population-format.md
    sha256: ef32264891567816903973ceee31f81266066fff2683f2cb459e31a0fb9d3170
  - path: src/gnd/skills/gnd-orm-core/references/population.schema.json
    sha256: 2dfc51df0713b9888c38604fc61e313f9f6b4a84c2bd0cf036547adca015b333
  - path: src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md
    sha256: 58b65f33badc3356c19bea9362c4dca06891efeed45087dfb8faeb1aa5d8ad29
  - path: src/gnd/skills/gnd-orm-core/references/representation-format.md
    sha256: 475d6a418e08dc8cc2b766b5e43751590d8c3541d25d941dfabfe638b388708a
  - path: src/gnd/skills/gnd-orm-core/references/verbalization-patterns.md
    sha256: 25c9bc7411d5aec5a6294d6f99dc1e140a9aad1cd8096c897307c7cba2bf3859
  - path: src/gnd/skills/gnd-render-doc/SKILL.md
    sha256: e39f059c6b45ded9e80234d619599b3ef12aff9444b0119b2b24c6756b627393
  - path: src/gnd/skills/gnd-render-doc/references/rendering-contract.md
    sha256: 0a35eba25b346f7d19b20f6cac03994187a632dde0e3a64f853bafb12fe49c07
  - path: src/gnd/skills/gnd-review-panel/SKILL.md
    sha256: bb9a8dc5eeeec32d4caaad5bcdf38a7e9e4c223d78a0317276eb5f38ad8e9bd1
  - path: src/gnd/skills/gnd-review-panel/references/review-contract.md
    sha256: 01d8057acf896882b49c0e482f229d0fc5ffd901f221db895248e07ebedd3691
  - path: src/gnd/skills/gnd-review-panel-light/SKILL.md
    sha256: 77284d6f7f411dc1e6e43c85597a3953c966ff3c90e0f8d7be7b6cc76fa3e4a3
  - path: src/gnd/skills/gnd-solve/SKILL.md
    sha256: ec67f5a1b9c1813278996c89e2e6589c5c48797b81166e638966a449ef74520a
  - path: src/gnd/skills/gnd-update-review-panel/SKILL.md
    sha256: 9868d6ad405dd475f1a8e21b5e184fc03a9f018b96c5b9d300eaafc13affdd4d
  - path: tests/test_development_scaffold.py
    sha256: ebfc81869fc8fa33e2449e84505015fd34225806a96396b47bb57ade5114b544
  - path: tests/test_review_credential_launcher.py
    sha256: a83e640850f9532631194942665326660065c1fd7f46032515255b96ed75ab0a
  - path: tools/run_gnd_review_panel.py
    sha256: 90d8ff1f1a6f054b4d740ec8ee001e066e78bef9e9b6e8eae0d0f6da4f282faf
---

# Phase 1 focused scaffold checks exited 0

## What shipped

Fresh private target `vasiloglou/gnd-public`, verified private with owner/admin
access before content commit. Explicit planning scaffold import, contributor
shell, owned Apache-2.0 license/notices, both real process-phase skill roots and
full normative references, owned plan-review-panel compatibility entry, safe
maintained launcher and target-local synthetic controls. The complete transitive
canonical record-resource closure is 53 early files, including one linked helper;
it is not the complete framework runtime. No installer-owned links are created.
All 12 units and all 218 question IDs/states remain source-owned. No publisher.

Approval instrument: source P1 spec SHA-256
`80af3337d97218599a12237c0ef5abe9b8bd9933ed0c30d8b9f7a563fc963f57`, owner
“approve” on 2026-10-01. Accepted source planning commit
`9b3da000aaf938435d700d16a1f23597d9e77645`; original runtime pin
`ac4be67afdddde0b2b2095a6cd383bc13852758c`, no affected source delta.
Public-safe spec/plan adaptations are identified in the batch manifest. Original
source human gates/raw review/inventory remain private; public summaries identify
that availability limit without claiming to contain full review dispositions.

## Gate output (verbatim)

Public-safe command below replaces the isolated environment’s absolute Python
executable path with `python`; arguments/output are unchanged. The source retains
the exact invocation. CPython 3.13.12 / pytest 9.1.1; no installed `gnd`:
`python -m pytest -q -p no:cacheprovider tests/test_development_scaffold.py tests/test_review_credential_launcher.py`
Exit: 0

```text
.........................................                                [100%]
41 passed in 0.22s
```

`git diff --cached --check`: exit 0, no output.
The eight scaffold mutation controls reject missing references, twin byte/mode
drift, dangling link, unlabeled/missing-boundary example, invented transfer and
question-state drift. Credential cases use synthetic values and mock network.
No real credential file or provider was consulted by these gates.

## Review and repairs

One full read-only Codex reviewer, exit 0, identified three blockers: overstated
accessible review evidence and two coverage gaps. All reproduced. Corrected
public r2 wording names full concerns/dispositions as private source-held and
links a counts/limits summary. For the two coverage gaps, old credential controls
still passed each broken mutant, 25 cases per mutant. New focused controls failed
the silent repository-env-read mutant and production default-redirect mutant:

```text
1 failed, 27 deselected in 0.12s
1 failed, 27 deselected in 0.04s
```

Each red gate exited 1; production launcher remains unchanged. Final target
suite exited 0, 41 cases. A narrow repair review exited 0 with no blocker. One
reviewer is one reviewer; two passes are not a panel. Reviewers read tests but did
not run them, recompute every final hash in the repair pass, or validate real
credentials/providers. Original output and red reproductions are retained in the
private source; this public-safe record summarizes them. Missing-file errors may
include a local path; retained logs are sanitized under the protocol.

## Selection and measurements

| Gate | Disposition | Boundary / reason / invalidation |
|---|---|---|
| T1/T6 | run, exit 0 | Exact B1 manifest/index/content and source delta, private target settings, byte limits; reconsider on any added/changed path, source delta or settings change |
| T2–T4/T7 | run, exit 0 | Fixed public scaffold/docs/twins/examples/ID-state/authority ledger; reconsider on references, file modes, bootstrap, records or ledger change |
| T5 | run, exit 0 | Launcher and synthetic target-local credentials/network mocks; reconsider on launcher, credential path, opener wiring, dependency or toolchain change |
| Broad/native/provider/certification | unrun; explicit-selection cadence only | Not P1 acceptance; no phase/milestone/source-change automatic trigger |
| P4-C5 | future P4 run | Fresh target wheel and source-free runtime/discovery paths; not inherited from P1 |

100 reviewed scaffold paths before this record, 1,174,851 bytes; largest blob
103,360 bytes, below 1 MiB. Planning below 2 MiB; total below 64 MiB.
No built package-size or runtime support-matrix result. Two implementation/
refinement passes used, within the approved two-pass limit. Copied reference/plan
lines and generated indices are distinguished from authored edits; final source
record retains exact line/byte measurements. CI selects credential-free scaffold
checks on Python 3.11; that hosted job has not yet been observed here.

## Refactoring review

None needed in framework runtime: no runtime behavior was changed. The owned
compatibility entry avoids duplicating panel implementation; both roots remain
mechanically identical. Historical lane adaptation and the early packaged-resource
reconciliation are assigned to P3 and P2 respectively, as explicit plan work.
No new runtime primitive or unnamed deferred refactor was introduced.

## Boundary — what this phase does NOT establish

Conditional scaffold readiness only. Live panel execution still requires the
explicit private source bootstrap; an outsider cannot run it from P1 alone.
No installed complete runtime, generated installer links, source-free wheel
workflow, current assurance, built release, supported matrix, public visibility,
package upload, announcement, unit authority transfer or source retirement.
No private application/customer content or original unverified vendor panel is
licensed or included. No broad suite, native lane, provider panel or certification
run. Copying transfers nothing; no target publisher is configured.

## Open questions

All original 218 question IDs/states preserve source owners/mints/triggers;
119 live overlaps are reviewed at first affected adaptation. Triggered obligations
must be resolved or explicitly transferred before handoff, never dropped on move.
P2 owns runtime and early-resource reconciliation, P3 owns current collection and
fixture/optional-dependency successors, P4 owns source-free wheel readiness and
bootstrap removal, P5 owns exposure/publication and release events. No inherited
question is closed by this scaffold.

## Refuted premises

Existing helper-only redirect and shell-nonexecution tests did not protect all
claimed behaviors: both faulty production mutants remained green before stronger
controls. Adapted review links overstated the linked summary contents. Reproduced
and corrected without changing the production launcher or private source claims.
