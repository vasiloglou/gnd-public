---
milestone: pyrel-applications
station: phase-PA0
skill: process-phase
scope: phase-PA0
date: 2026-10-13
source_base: ac3ad34
gate:
  command: ".venv/bin/python -m pytest -q tests/test_pyrel_application_corpus.py tests/test_pyrel_application_driver.py --tb=short"
  exit: 0
  output: "151 passed in 4.79s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately scoped CI
  reason: bounded corpus/driver change; production source unchanged
evidence:
  - {path: .gnd-planning/milestones/pyrel-applications/notes/phase-PA0-spec.md, sha256: 5a81bce34fe021a55bf39330ed3271b6d1f1cb48f90f11d9265cd92afc31381a}
  - {path: .gnd-planning/milestones/pyrel-applications/notes/phase-review-authorization.md, sha256: a71c167c1faf2b0a154b6526f6a478ae80a1fce7c006b9a29a74151a375d9907}
  - {path: .gnd-planning/milestones/pyrel-applications/notes/phase-PA0-claude-review.md, sha256: 6c6e27874a8784076bd7265e7148ee7ff8b36c455072097390d04db9259b9f43}
  - {path: .gnd-planning/milestones/pyrel-applications/notes/phase-PA0-claude-repair-review.md, sha256: 94ca801199adf677e39f2cba191442c86ac658eba0618d1bf5d4d0a51c62e6dc}
  - {path: .gnd-planning/milestones/pyrel-applications/notes/plan-amendment-a1.md, sha256: f1f79833476921fdbfd4a04e6360739b6f67d733f7cf2dcac4e9cf488245f698}
  - {path: .gnd-planning/milestones/pyrel-applications/003-plan-amendment.md, sha256: 4df3c0d85715596a62b6f0a136e75f528f27b11d1f2ab2c3577b4df16e49ac1c}
  - {path: tests/fixtures/pyrel_applications/matrix.json, sha256: 4fbb82a5188d60ff27f10d0cba462744e0cc6cce050eb8a9e5733862ca3ba57c}
  - {path: tests/fixtures/pyrel_applications/answers.json, sha256: db902a387cbbae4b1c87bf0bafed03e66f27b9741439d980e808a716998a00ba}
  - {path: tests/fixtures/pyrel_applications/approval.json, sha256: b380a31b92297a00d66997ad87da790ee51868bb4a33b984d525c15a36f735b7}
  - {path: tests/fixtures/pyrel_applications/README.md, sha256: b307a40da8c9d26b454f5e804d263b60c37849a8514d4dbc7580e1bdbe04b578}
  - {path: tools/measure_pyrel_applications.py, sha256: 81243d946c7e0960057d3f06272002889c46fd1ce7e7d24da0de9a19adeb4c43}
  - {path: tests/test_pyrel_application_corpus.py, sha256: dd867b21bdbf16aa20e1e10377d747c76b93e15ddd8ff3fe1b551b760e54d769}
  - {path: tests/test_pyrel_application_driver.py, sha256: 03c131acf7e6327631cda7c5aad2609962ff6353125bf273031a354b9fe024ec}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-current.json, sha256: 8f7361dd9706919425289a530d73de48cd65117a3b1bdb900c2a803707a3545a}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-current.txt, sha256: b57d491fed7cd638c59e7d7d14dd24a538d6ed1efa6bbcc095533b2b9aba7ba4}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-r2.json, sha256: 85a050b30ef670f684cf855a85eda0da54cc42ef480c808ab7ce2470bee0854e}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-r2.txt, sha256: da0b1e12ccabbfc0122928ab6babd3523dcd68039fabb191999b96f0306b2535}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline.json, sha256: 30db3e4b1ad546eb8821978c509953c0e3b531fc8656110de0d6ed4d214d65d2}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/completion-final.txt, sha256: 3d82c6ceb36c767415fa5eb2f688885f05745a38091097c99f7ee61bf2889209}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/completion-green.txt, sha256: 9140f9f67b8064596dbd431fec7edfb6badd9eba3cb09a1c84f32f7feb5e827c}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/completion-lint.txt, sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/corpus-final.txt, sha256: 9efeca6427873987dba3485ba3cd30ecdb4aaa0a004c24d0bd2c77dada76d2e3}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/corpus-green.txt, sha256: af21b79d7c7835f30eae514e441f5b20a1552c94b27fb252b1e465dc6eb3b7b9}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/corpus-r2/answers.json, sha256: db902a387cbbae4b1c87bf0bafed03e66f27b9741439d980e808a716998a00ba}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/corpus-r2/matrix.json, sha256: b102ac2dcb19a2b7dc5c6a43b14cb436f8f043e7c503e9607f4ac8806d381c09}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/legacy-green.txt, sha256: f19ef5a3c071f9357ee0457bb85664abb11362754c27bb0c48c6b8a594d06928}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/lint.txt, sha256: 82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/native-additions.json, sha256: 5f1f2e984863335aa76625e7bfd4d63d56f5e40b71ab5f580aae8aec89a3753a}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/native-additions.txt, sha256: 1771fb950bc1907877145c7e3a267772b58360f79ce3fa69233a0b641aafbc94}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/pre-F3-checker.py, sha256: 8f427cc1c28a00a4f5858c9cde51b56022a94bf14b687ca027555b96926bc57a}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/reference-isolated.txt, sha256: 30c0a18111db6dc7738e04991bc22c2360a36fe0125861094d989cc0e3d51e97}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/review-corpus-final.txt, sha256: 82a9b1efee2d2d9df5c648e7aad74ff0bf1ef2f3b1b3e7810d9c67cfb9376ae3}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/review-corpus-green.txt, sha256: c6725d161493d9f6472880ad2ea238fbf62f151c6897f21015bfc3b67d44a909}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/review-driver-red.txt, sha256: ddd7f5cd67484c564b020f9d16c9580a3e2e302ecbf2fc6fe8b4364ee764689c}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/review-legacy-green.txt, sha256: a14493e7cc0f54a22e6435401cb87b3165188b2570cb43457c5d034de9feead6}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/review-witness-red.txt, sha256: ade7a2223eeac65cebd11f083f7e715f111d3c174a94fd9261158743cf86e0d0}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/row-placement-pre-fix.json, sha256: 25777fe48760ee207c9765bc2fe714f1ecfa472853732220ff68b52bc3065af5}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-r2-red.json, sha256: 999735d9216b6b9eb6dfab2543740606966b498be5018653cdebf0b920a7175d}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-r2-red.txt, sha256: b5d666c3a1bf632dae333a0ed316d80fbd5b5626306fa4b486bf9852a697bc8b}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-red.json, sha256: 51b9e2ba6882ae3aebd1e3fd7f997b49c3d795c653cbafc2074940c3b71799b0}
  - {path: .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-red.txt, sha256: ec22428035ce9220b8fbf60e412eeb9fefcff8eaa2ca1b24c2e49f6a6db69cf9}
---
# Claim

PA0 completes its approved bounded contract/corpus work: 61 obligations, 137
addressed controls, full native expectation/acceptance verifier and preserved
GND observations. Native current-behavior baselines and a genuinely red successor
are retained. Independent phase review and owned hardening dispositions are
recorded; PA1 is now ready to implement the new profile.

## What shipped and criterion audit

- C1: exact five-model matrix exhausts every constraint and both derived heads;
  137 controls include duplicate and distinct-value uniqueness, every guarded
  positive/violation or warning, derived missing/extra and joint omission.
  Cross-links, modality/identity, stories and independent complete-source
  expectations have live dirty controls. Entries may share input bytes.
- C2: original 124 actual native legacy runs show 48 guarded unsupported targets
  and six absent derivation targets; 70 supported targets matched. Revised native
  measurements run the seven original baseline/forged controls and all 13 added
  inputs. Twelve distinct-value targets violate natively; joint claims have no
  derivation verdict. Current successor uses --accept and is red because the
  new interface is absent. It does not falsely claim this new red is evidence
  of all old guarded omissions; those have their own actual legacy receipts.
- C3: spec fixes grammar, profile/schema/exits, known versus unknown coverage,
  modality, raw byte binding, conservative limits, optional local runtime and
  explicit comparable-row normalization. A1/003 repairs two demonstrated GND
  computed-versus-claimed completeness disagreements; every native row remains
  mandatory and both bad populations must be rejected. Exact frozen native key
  and exclusion list are hash-checked before execution and by corpus controls.
- C4: public CLI export, isolated pinned native interpreter, explicit DuckDB,
  bounded reads/timeout, pre/post input identity checks and process/schema/error
  checks. Expanded consumers include rendered-byte/RF1 semantic/helper/manifest,
  primitive ambiguity, registry, oracle isolation, runtime copy and layer homes.
  Production source and historical goldens remain unchanged in PA0.

## Gate output (verbatim)

.venv/bin/python -m pytest -q tests/test_pyrel_application_corpus.py tests/test_pyrel_application_driver.py --tb=short

    151 passed in 4.79s
    Exit: 0

.venv/bin/python -m pytest -q tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_public_pyrel_export_runtime_optional.py tests/test_external_runtime_tutorials.py tests/test_public_pyrel_oracle_isolation.py tests/test_rf2_pre_move_pins.py::test_standalone_pyrel_output_bytes --tb=short

    77 passed, 13 deselected in 11.40s
    Exit: 0

.venv/bin/ruff check tools/measure_pyrel_applications.py tests/test_pyrel_application_corpus.py tests/test_pyrel_application_driver.py --output-format concise

    All checks passed!
    Exit: 0

.venv/bin/python tools/measure_pyrel_applications.py --mode baseline --out .gnd-planning/milestones/pyrel-applications/evidence/PA0/baseline-r2.json

    Exit: 0

.venv/bin/python tools/measure_pyrel_applications.py --mode successor --out .gnd-planning/milestones/pyrel-applications/evidence/PA0/successor-r2-red.json

    Exit: 1

.venv/bin/python tools/measure_pyrel_applications.py --mode baseline --stage additions --out .gnd-planning/milestones/pyrel-applications/evidence/PA0/native-additions.json

    Exit: 0

The first two revised receipts bind their recovered exact r2 corpus snapshot
under evidence/PA0/corpus-r2; the final additions receipt binds the final snapshot.
Models/populations of the original 124 scenarios are unchanged. Generated
program bytes were temporary and removed; their hashes are run provenance, not
committed program artifacts. Public exporter/runtime is unchanged from 00efef2.
Versions: Python 3.13.12, relationalai 1.30.1, DuckDB 1.5.5. No credentials or
remote backend were needed for native execution.

## Review and convergence

Owner selected Claude Code read-only review for all phases. Initial expired
OAuth produced no opinion; user-authorized native login restored authentication.
No repository credential file was read/executed. Completed initial Opus/high
review retained 11 items; four blocking contract/verifier/consumer findings were
reproduced and repaired. Initial target-only fake accepted 124 corrupt reports;
the regression observed red then green. Frozen witness drift likewise reded
before the comparison was added. Findings and scope limits remain verbatim.

One bounded repair review found no blocker and independently recomputed the
complete-model native answers, two source disagreements and acceptance counts.
Its seven additional owned hardening/completeness findings were dispositioned
in the spec and covered by root controls/native measurement. Row placement was
reproduced with reconstructed pre-F3 function logic (not an original-file byte
replay); malformed report/schema/hash gates have direct corrupted controls.
Post-review hardening is root evidence, not a newly invented Claude opinion.
One reviewer is one reviewer; these two readings are not a panel. The explicit
round limit and 5/7 self-inflicted ratio stop further prose review; next
instrument is implementation. Four local A1 opinions are separate plan evidence.

## Delegated completion and measurements

Whole-milestone owner auto=true supplies this bounded completion ruling after
all PA0 criteria, reviews, reproductions and native measurements above.
This is delegated approval, not the owner's personal reading. Exact corpus and
spec hashes are in frontmatter and the spec's final snapshot ruling. No merge,
release, certificate or successor milestone is implied.

Actual driver/test lines 207/329 exceed original 200/300 estimates by 7/29;
spec records explicit delegated ceiling amendment to 240/380, with original
misses standing. Fixture data is below 15,000 lines; retained intermediate
snapshots are evidence, not extra domain scenarios.

## Refactoring review

Refactors EXECUTED: one whole-report checker replaces target-only comparison;
one bounded native report reader makes refusal recording total at that boundary;
approved corpus admission centralizes frozen hash checks. These changes strengthen
the development verifier without changing production policy semantics. Existing
legacy runtime and model-query homes stay intact. No structural debt is silently
introduced; PA1/PA2 translation remains in the standalone runtime's one home.

## Boundary -- what this result did NOT establish

No implemented applications-v1, native guarded/derived acceptance, application
publisher/query, executed new tutorials/graphics, installed-wheel acceptance,
Linux result, universal equivalence, source truth, certificate, release or merge.
The original whole-tree scaffold traversal failure is recorded in 002; isolated
reference closure passes, not a passing whole-tree run. Native baseline completion
zero is never policy acceptance. Full native acceptance is still red, as intended.
One reviewer is one reviewer; same-family plan readers are advisory, not proof.
Reconstructed pre-F3 logic is not a checkout of an original-file revision.
Historical source-owned, RF budget/architecture/retirement and compiled-operation
claims retain their original boundaries and owners.

## Open questions

- Unknown/vacuous/literal/repeated-variable/refusal/native-exception branch
  execution -> PA1 direct corpus; no PA0 coverage credit for them.
- Guarded native policy execution and acceptance -> PA1; independent complete
  derivations -> PA2; query/publication/two applications -> PA3/PA4.
- Exact comparable denominator and two separate disagreements -> PA6; further
  exclusions require explicit reviewed amendment, never silent normalization.
- Six graphics and desktop/mobile/theme/accessibility -> PA5.
- Installed-origin/wheel/resource acceptance -> PA6.
- Historical source authority, RF1-OQ2/OQ4/OQ6/OQ7, RF7-R5, RF-D5 and prior
  budget/architecture reconciliation -> their original code-refactoring owners.
- Owner merge/release/current human acceptance -> separate owner actions.

## Refuted premises

Unqualified full-row GND/native agreement would reward claim-driven completeness;
reproduced Ada/night and joint Ada/river controls motivate A1. Target-only matching
could report green despite wrong bindings and overall rejection; actual pre-fix
regression refutes it. A legacy report cannot acquire new modality/derived fields
while preserving its schema; successor is now explicitly the new profile.
Original missing consumer paths, witness-key and native-added-input coverage
claims are corrected with the retained dispositions and current measurements.
