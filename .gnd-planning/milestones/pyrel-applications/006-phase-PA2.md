---
milestone: pyrel-applications
station: phase-PA2
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PA2
date: 2026-10-13
source_base: 3bf57ca
gate:
  command: ".venv/bin/python -m pytest -q tests/test_pyrel_application_derivations.py tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_review_regressions.py tests/test_pyrel_application_corpus.py tests/test_pyrel_application_driver.py tests/test_pyrel_derivation_contract.py tests/test_bookrec_tutorial.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf2_pre_move_pins.py::test_standalone_pyrel_output_bytes --tb=short"
  exit: 0
  output: "355 passed, 16 deselected in 32.97s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately scoped CI
  reason: focused integration and affected consumers selected; broad exclusions preserved
evidence:
  - {"path": "src/gnd/export/pyrel_runtime.py", "sha256": "1ff982e08fe41c0623ad6d62436ba205a6a490046c5e47112ac314689a2f76b8"}
  - {"path": "tools/measure_pyrel_applications.py", "sha256": "301d7a3a45da27ddbf34c4fdb999281efd23bb0125295524704d239c79162053"}
  - {"path": "tests/test_pyrel_application_derivations.py", "sha256": "abcdd239d8a8126329ce74e309e3dd2a57a33d79f0b4710fe9827987b0806d25"}
  - {"path": "tests/test_pyrel_application_driver.py", "sha256": "6b44f9add376fa0ef8ddb3bc099181f6ca7f294e90cef076c9b22a6cd4ea785b"}
  - {"path": "tests/support/pyrel_application_successors.py", "sha256": "9d18338515d63893d0271e415c4b479652a404c4b8d63d8d7f1c80aabf9ad1de"}
  - {"path": "tests/test_rf6_query_policy.py", "sha256": "77dc9e0e4f90536c8d7ce8e41bfd8b6d60021fd7bce3ccd2d4012ce450324444"}
  - {"path": "tests/test_rf2_pre_move_pins.py", "sha256": "75b46973f6c6257625dd0c557002f4862d28bbc0e484f52d0b016e7db362455f"}
  - {"path": "tools/gnd_layers.json", "sha256": "324635e4880ee68ef83c84a0e65f3ce07952908150c9f412a2f74319b7f7c4df"}
  - {"path": "tests/fixtures/pyrel_applications/matrix.json", "sha256": "4fbb82a5188d60ff27f10d0cba462744e0cc6cce050eb8a9e5733862ca3ba57c"}
  - {"path": "tests/fixtures/pyrel_applications/answers.json", "sha256": "db902a387cbbae4b1c87bf0bafed03e66f27b9741439d980e808a716998a00ba"}
  - {"path": "tests/fixtures/pyrel_applications/approval.json", "sha256": "b380a31b92297a00d66997ad87da790ee51868bb4a33b984d525c15a36f735b7"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/005-phase-PA1.md", "sha256": "e728e40ae1e1eb26c1e03b26abc1150c24597240902b0bfd6c5baf2722b490b5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA2-spec.md", "sha256": "47285d98f18dc177f6cb696118b0776a3769f48e42435f2b80b2def1f028ef12"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA2-review-prompt.md", "sha256": "38847cbd03eb1a461e574ac78b9cce98d0888409085b3f7109db1d1f967530ef"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA2-repair-review-prompt.md", "sha256": "6dcb8e68025e94b1e6e7bd0008962b3674354481da8720385448d6338687403e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA2-claude-review.md", "sha256": "04212dd1fd223a0b1a45e3bed1ed91e5e45eea6aedede59749f8dfeb71bb20de"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA2-claude-repair-review.md", "sha256": "b8034bcf32ca950ba2f32e1c0620c2bf2bf8151b9621562f5f26682e92a4a459"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/plan-amendment-a1.md", "sha256": "f1f79833476921fdbfd4a04e6360739b6f67d733f7cf2dcac4e9cf488245f698"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/agreement-exit-red.txt", "sha256": "610762f6613f3efc9d28824603d80761717695a11ae2275afdfd96056244f60e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/agreement-green.txt", "sha256": "3605abb09038ce24e90d81df8f7c0d87bb6f647a5e016bf461d8a8fcb408f6e9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/agreement-red.txt", "sha256": "7585503bb6bdcc91f457c645f9c54aa68d84188d254a745b6f8840cfca7f21dc"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/completion-byte-bindings.json", "sha256": "b44e9645913fbd01236ab7e5f168f9f536979a80ae032777f30a99fcc0e1d3bd"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/completion-focused.txt", "sha256": "9ec57a1710edd604c866a4404139e3a83cc2d1f7ad5bd3ee9e5f067361b110f0"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/completion-lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/completion-native-direct.txt", "sha256": "f354fcdedc66e6103f7a3866843d430efe9c447bf3526ce7f6445cf6290c2f4f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/computed-key-green.txt", "sha256": "c513a336404899b0e4e59540faac60f730d81e38e236b1b942334605c26575ed"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/computed-key-red.txt", "sha256": "139e275913299da916263679a0cad2738623c5ddb781ecd956f57979fcfcfe82"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/computed-verifier-green.txt", "sha256": "775b7aa27d0c17f48b3feff20c836f14b6ed8ebcb90ec7e0b76d2a13c579268a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/computed-verifier-red.txt", "sha256": "661dae1c777ec847da773eb96f32a3f56dd1876ac21e48cfedb1a30aa7010917"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/current-byte-bindings.json", "sha256": "6c869e716716c04de0ff3433867a5cecb73f89317633d02b6dfbbf08d20f5242"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/derived-key-duplicate-green.txt", "sha256": "d907fec0e0445cfe67a7272e864304e81194b234052d6bdfcb6ec87c0b123e62"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/derived-key-duplicate-red.txt", "sha256": "68c9eb25f3012527a9aaae26a4dcc297f7046c63b22c93daacaffb36b303e540"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/direct-red.txt", "sha256": "16ef8f15e644843d5cc2e8aa3ba78242a8f7916346754403ebf572294f8a2a54"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/driver-green.txt", "sha256": "0b7ede8c8682c95da8ee490cf24dab3160596fde2b4a9c8da2658980b3dec7fc"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/duplicate-import-format-recheck.txt", "sha256": "3b4ad3097d7020cd8b172384869bd1db1102ffc4c9316bde31fef1b3bcacf9c6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/dynamic-query-successor.json", "sha256": "fcd7530a3e85056817bdede703a173088fe1e3be11896fc4ca247c7fb1213169"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/entity-cache-green.txt", "sha256": "2d412f3df16c5f709b619806707a68d21250dfb6c6e59c369f9eabfb89f7c42c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/entity-cache-red.txt", "sha256": "3bf8c237aece744e53bb0844f54a3f4767a0fb3da0b140d866e4563cbad9ef32"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/focused-initial.txt", "sha256": "0c6d6c23948dd5cbe6c2abf1c96262151c555a185feabd572bf5796577f3d561"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/focused-repaired.txt", "sha256": "32cb9ad66b441565808d019d1bdec5c20b93c7bf05b664cba59a9616e18062ff"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/initial-native.txt", "sha256": "949d56309270ec1f14aa83dfc36285ae62fa93c9645ec0286faf5c73c48d8835"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/initial-parent.txt", "sha256": "40321a5e5ec9d76e6e5e26a41cfb7f4077bd34ddd597d3bac5dfa63f275f68da"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/legacy-definition-identity.json", "sha256": "d79f34ecde63b19471a66e1c550dd804d95e58971460fd211931fefded632375"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/lint-repaired.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-all-direct.txt", "sha256": "7fd875749cba899b75799120c57d52f2d3b36dfcde185a7e192f595b16015b32"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-direct-initial.txt", "sha256": "540c1a78f54816d583dad098691ff08a176f1fc0fd9302bf8cf90eedb021ac0b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-direct-repaired.txt", "sha256": "8c25c8d8773d1ebbe3cf1ae0fda1ba1172e96566d4ecbd1b95d5f496a10d1670"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-final.json", "sha256": "657b04d0fcec0315305dc3b01eead39a560e51a8962e42fe8497d54bf4937195"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-final.txt", "sha256": "33127fb34557a54b560e25eb94d226cfd6c2636c5181ddbe3e50468406bae6d4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-initial.json", "sha256": "4e5a72d3f465902c1cbdcc4bcf25ee381197e627bcac6360a2f9c0f85e345403"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-initial.txt", "sha256": "33127fb34557a54b560e25eb94d226cfd6c2636c5181ddbe3e50468406bae6d4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-red.txt", "sha256": "e9c0478d462b69683eb483b8b85b47b306d9e76e6ef9ef32e82f4d051842e092"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-repaired.json", "sha256": "b5f3927432039250c20ce30f98f93b6297d38d906947b4a809ad9f463540bfbb"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native-repaired.txt", "sha256": "33127fb34557a54b560e25eb94d226cfd6c2636c5181ddbe3e50468406bae6d4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native.json", "sha256": "6448e5bd7c20e151e888ff58f28b3f62791da13f3e097bb63dba6d3f25883bc6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/native.txt", "sha256": "33127fb34557a54b560e25eb94d226cfd6c2636c5181ddbe3e50468406bae6d4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/pre-cache-runtime-reconstructed.py", "sha256": "4e8abdd6784c086613ba86e1d823b1fb195d25bd7048331f7c4d7546b28a311b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/provenance-negative.txt", "sha256": "3b4ad3097d7020cd8b172384869bd1db1102ffc4c9316bde31fef1b3bcacf9c6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/pyrel-successor.json", "sha256": "2740e2c03a800078d665eec430ff294fbde5e1b417f07045452544fcf0afaa9a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/query-successor.json", "sha256": "dcad8b16564ca1e271ae76a0d1cae6d1cbccc60d186acf8294cd215c64266ae9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA2/successors-green.txt", "sha256": "8b087e94ee14554792620a00bd9bc646870a106bd10af70aff2d16cb6bbe22e6"}
---
# Claim

PA2 integrates structured derivations into standalone PyRel application acceptance.
The final 137 native scenarios match the frozen key on all 2,323 obligation rows.
All 2,321 comparable GND/native rows agree; exactly the two reviewed A1 source
interpretation differences remain separately enumerated. Both engines reject
those populations. This is the selected finite agreement, not universal ORM
semantics, source validity or a certification.

## What shipped

The existing runtime validates and orders the acyclic v2 body/head/negation
fragment, computes native projection relations, and loads computed tuples with
unique ordinals. Supplied derived rows remain claims and never seed premises.
Computed facts feed dependent rules, universes and constraints. Every head has
computed/null, missing/extra, identity, status and reason fields. Overall status
includes derivations even when there are no constraints. Unknown coverage,
unsupported grammar, cycles, join/result limits and native errors fail closed.

This is integration of an existing GND/native parity capability into the shipped
export path, not a new universal compiler or hard-coded BookRec implementation.
Generic unrelated relation names, reversed order, negative chains, empty results,
literals, duplicate claims and computed key multiplicity are actually executed.
No GND evaluator or test-oracle import exists in native execution.

The measurement instrument checks computed values and identities, exact row
inventories, native key outcomes, actual finite business exits, two permitted
exclusions and all comparable statuses. Negative controls refute missing/extra
exclusions, unlisted mismatch, missing/duplicate rows/cases, wrong exits, wrong
computed identity/values/reason, missing computed expectations and changed runtime.
Frozen expected files remain unchanged. Expected computed tuples are determined
from the approved claim/missing/extra relation, not the implementation.

Chained PA2 source/query successors preserve PA1, RF9 and compiled snapshots.
Direct reads 359 <= 365; original metric 304 <= 310; allowance count zero. Legacy
classes/functions and program_main remain AST-identical to PA1; no shim is moved
or retired. All new runtime logic lives in the existing standalone home.

## Gate output (verbatim)

Command: .venv/bin/python -m pytest -q tests/test_pyrel_application_derivations.py tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_review_regressions.py tests/test_pyrel_application_corpus.py tests/test_pyrel_application_driver.py tests/test_pyrel_derivation_contract.py tests/test_bookrec_tutorial.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf2_pre_move_pins.py::test_standalone_pyrel_output_bytes --tb=short

```text
355 passed, 16 deselected in 32.97s
```

Exit: 0.

Command: .venv/bin/python -m pytest -q -m pyrel_oracle tests/test_pyrel_application_derivations.py tests/test_pyrel_application_native.py tests/test_pyrel_application_review_regressions.py --tb=short

```text
26 passed, 46 deselected in 46.84s
```

Exit: 0.

Command: .venv/bin/python -m ruff check src/gnd/export/pyrel_runtime.py tools/measure_pyrel_applications.py tests/test_pyrel_application_derivations.py tests/test_pyrel_application_driver.py tests/support/pyrel_application_successors.py

```text
All checks passed!
```

Exit: 0.

Command: .venv/bin/python tools/measure_pyrel_applications.py --mode acceptance --stage all --out .gnd-planning/milestones/pyrel-applications/evidence/PA2/native-final.json

Exit: 0. Full console output is native-final.txt; native-final.json records
`"matched": 137`, `"denominator": 137`, and agreement counts 2,323/2,321/2,321.
It contains runtime/tool SHA digests and per-program/input bindings.
Completion-byte-bindings.json re-renders all five programs through public CLI,
asserting every measured program digest equals current bytes.


## Review and reproduction

One reviewer is one reviewer. Two selected Claude Code read-only passes are
retained with disclosed interpreter-call deviations. No project tests or native
runtime were executed by the reviewer; root-produced actual controls establish
the observations. Review opinions are over their reviewed bytes only.

Round one found a cache blocker: the parent constructor snapshots entity
universes before computation. Two GND-valid mandatory/entity-enum examples
reproduced GND reject/native accept. Clearing the population cache after all
computed heads turned both controls green. The reconstructed pre-cache file
removes exactly this three-line repair; no original-file replay is claimed.

Three minor dispositions: primitive fragment typing is not full GND declaration
validity; applications must validate source models. Runtime/tool hashes plus
start/end checks and actual program re-rendering bind execution. Missing computed
expected keys now fail instead of silently bypassing comparison, with red/green
controls. A changed-runtime negative demonstrates the provenance instrument.

The sole repair review confirmed those repairs but found duplicate claimed rows
on a derived keyed relation: GND rejects its raw-row key while computed set rows
would accept. The actual GND/native red control reproduced it. Final owned
admission refuses exact duplicate supplied rows on derived heads with any inline
uniqueness, with incomplete/2 and duplicate-derived-key-claims. Duplicate claims
without a key retain the documented positive set-semantics case. Distinct native
computed tuples still exercise native key counts with unique ordinals. This is a
technical unsupported shape, not a Python key verdict labeled native.

Convergence: round one 4/4 self-inflicted, 1/4 blocking; round two 0/1
self-inflicted, 1/1 blocker-class neighbor. The declared two-pass review budget
ended; no third opinion is invented. Final owned repair is supported by its red,
green and complete current-byte gates. Native import formatting was followed by
a separate recheck of that final control. No original answer was recaptured.

## Refactoring review

Refactors EXECUTED: one guarded-work helper is reused before native execution
and after computed counts exist; one phase-successor helper authenticates each
explicit predecessor rather than rewriting historical policy. Native projection
and relation loading reuse the existing binder/types. No new production module,
second checker or exported legacy identity is introduced.

## Boundary -- what this phase does NOT establish

No app query/publication, tutorial graphics, installed-wheel acceptance, model
truth, certification, proof or transition permission is established. The standalone
admission is the declared primitive fragment and can accept GND-invalid declarations;
full GND-valid source validation is a caller prerequisite, required for PA3/PA4.
Native acceptance does not certify a model. Literal heads, recursive/disjunctive/
opaque/aggregate derivations and other outside-fragment shapes remain refused.

GND may constrain supplied head claims while native uses computed heads. Outside
the frozen corpus individual verdicts/witnesses can differ. No further exclusions
are introduced and no arbitrary model equivalence is claimed. The two A1 rows
are exact inputs, not exceptions allowing bad populations to publish.

Legacy entity_concepts is asserted-only and unused by profile checking; native
application queries use relationship/universe methods. Population caches rebuild
from computed facts. Dictionary API raw hashes remain caller-owned; CLI binds
actual bounded reads. Start/end checks cannot rule out change-and-revert; measured
program hashes plus current re-rendering supply the stronger binding here.
No broad replay, merge, release or source-owned handoff occurred.

## Open questions and inherited obligations

- PA3/PA4: explicit native calculations and independent staged-byte publication;
  validate captured model declarations before child execution.
- PA5/PA6: six grounded graphics, executed tutorials, fresh installed acceptance
  and required independent milestone-close panel.
- Future native-entity-concept-maintenance, owner GND maintainers: unused legacy
  entity_concepts does not include computed-only members; do not use it as the
  profile query surface without a separate supported implementation.
- Prior pyrel-legacy-runtime-maintenance residual remains from PA1; old global
  convenience negation was not changed. Historical source/assurance ownership
  and all RF/public-launch/compiled boundaries remain standing.

## Refuted premises

Entity universes were not automatically current after derivation; actual native
false accepts refuted that premise. Logical set equality alone was insufficient
for duplicate claims on keyed heads; the specific raw-key/native-computed mismatch
refuted it. Instrument count-only business agreement and absent computed expected
keys were too weak; executable negative controls now reject those cases.

## Delegated completion ruling (auto=true)

Record completion from the actual final gates and reproduced dispositions under
the owner's named milestone delegation. This is an agent ruling, not the owner's
personal reading. PA3's hard prerequisite is discharged; its own complete spec,
implementability sweep, delegated gate and red controls precede app source edits.

This ruling binds preceding record bytes SHA-256 d8887f901d3e0f2f3924c9092629f24c2e131e0ef65289a69471731f077fae46.
