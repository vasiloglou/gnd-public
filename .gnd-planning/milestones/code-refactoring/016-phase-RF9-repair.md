---
milestone: code-refactoring
station: phase-RF9-repair
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF9-repair
date: 2026-10-06
source_base: 26dbff6abe53d020d6a933e48d99915089f52054
source_subject: 21487ab1711fb7781d106deefd40243666d904b4
gate:
  command: "PATH=\"$PWD/.venv/bin:$PATH\" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_rf9_repairs.py tests/test_rf8_structure.py tests/test_rf8_sessions.py tests/test_exp_close_work_gate.py tests/test_exp_close.py tests/test_exp_session_store.py tests/test_v71_phase4_successors.py tests/test_public_v71_judgment_successor_guards.py --tb=short -p no:cacheprovider"
  exit: 0
  output: "257 passed, 1 warning in 28.67s"
  note: "Current final-clause and affected-consumer gate; earlier gates and scoped evidence are retained below."
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Broad default/historical/evidence/census/provider-oracle/proof/distribution/certification work is outside these approved target repairs."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/014-phase-RF8.md, sha256: 6b8ae1618922138d8beaed414c461ac075540cf237cdba48ae1ebbb0062f8b13}
  - {path: .gnd-planning/milestones/code-refactoring/015-phase-RF9.md, sha256: 1331d4c83755e319e54b1c1af37d3e101a28eaf32203881f4732b04918c1c295}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/frozen-controls.json, sha256: 633603f69199c82cde226e4adef6da1d10018ba27b85a9cd9da8ce5b416703ba}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/R1-replay-impact.txt, sha256: d9a9ec2b1c349954659298b40393169c314a2c3a0cbda343b3deb606155ae6e5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/approval.json, sha256: 152bcf5e600a080f2a9eec0c52b9e6d78a741dee676232fcb5e028a98fb01842}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/budget.json, sha256: eb086035d02580a8172dcc784e019c677cd9f6d8894a6ec84ccfde93e74a3dab}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/ci-status.json, sha256: 222e9175c9bfa82f2ecc08f8449dfc0fc275841f3355ae02e99bd8f77f51b610}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/cli-homes.json, sha256: eae7b3769161708167a56320c6d683046004d4c9ad20fbc1c5b599bd3072675c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/compat-impact.txt, sha256: 5dd7bb8fd32d7f5e9b0f6f9f2b6c1bb6d97594bc1c86c366747d24ead7a6d66a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/consumer-impact.txt, sha256: 4857dfb692c862bf57cb738aa58b5d9847b5215c0ab29104b69c07b304213485}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/coverage-base-red.txt, sha256: d87840378b3b3499559bab8af19f42838058c106898d81bba67cec56e65c1481}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/current-gate.txt, sha256: ef08cf7419eafe38bb9f174738b8681f94f7daf5a2aceb59fc8094861bf7907a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/direct-complete.txt, sha256: 844e369311462621e62cc7a1eb642a1ff7987369fbb239a020f86438abdf56c6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/direct-final.txt, sha256: 9b87637453dcc26c4d39c37fa8a592a85c24e9607a3931019750389e4bc0af63}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/direct.txt, sha256: 08d840c944f19a9e1c7ec73789ab66894cfa0191e53381bf4639b41e1e061433}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/dynamic-query-candidates.json, sha256: 5ee422365202e3c12082cd62f6b4a7666cd867d86c220a3e1a63400bc0844531}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/env-graph-final.txt, sha256: f5e4a55f64c3b4e64818479ef6486abef644abd3a11fb7369bfd2c8f2f70337b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/environment-base-red.txt, sha256: 8b71796e34e9038958d66593a92286a1c65464aed96d0d787b5ece75f7596df5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/equality-red.txt, sha256: 1a0197ebc50e6f853157ffda820bdc0a6af1a6a89977c7766e8f00a747c21ffb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/extra.txt, sha256: fbd618c1ddc2d6d5e48db88c701ef7dae40a6df50e2a3cc6142de402b4243fe6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/feedback-branch-base-red.txt, sha256: 59559d5ab5eee20db512c9902b3eb5aed5063663ef058ae868beddc4253289ce}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/feedback-branch-current.txt, sha256: cca5c773d307f0f1714721d1265f5cbfd2e0ede6b49b8db6da058f61326c2b59}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/feedback-branch-instrument-error.txt, sha256: ea1307715c637cd82dd3e0df2204f4a5dc4db1a6d18b40faf1e000d1c5cb5e13}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/gates.json, sha256: 9418b959a8dd91779653513a294d1faef42f8fb53180b3ee1f3d8f80ded215f8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/lint.txt, sha256: df9347c1ce13c50286886cff5c1678b2255e92d109115d3d8153cb5f7699d6ad}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/manifest-adaptations.json, sha256: c1cd27af6439eb1313107fcbbc91726f9fc6a7c217ba128fe66fd4bed33b1387}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/metadata.json, sha256: 794d2cf6348db9d70d4a6a54331bca073815379dce536bf2349b95d3123a41a8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/metadata.txt, sha256: 78f241a5956988758e74d8e986fad790ae06fc29f82cd93de465f549ea3a1111}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/metadata_checks.py, sha256: 2695dcd73fde2b1ce54c7a6bfd4cd822fbc719e0c6c224729ddc19dbf19837ef}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/native311-current.txt, sha256: 9dab9c6d93f832c59677b9a07424206eaa1fecd48a56f5ef3835ae7449095ecb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/native313-current.txt, sha256: 921d700fa1a3d341540ceb3dbb2fb3987a462fd648ce5fe316494793bea98c86}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/no-best-base-red.txt, sha256: 7f1b23c531128d9ee567017c5107d8b3dce4dc635d31bd3442799da45f1a5524}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/no-best.txt, sha256: 8979e37c6d6e08241b13552aaf293b8360de8fb5859334d4a7752b2ff6f999e7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/output-bindings.json, sha256: 3ad4d189c25e8d476d474aa92e1ada77b0aca488fbdce07fbb37b45c59269ae6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/parent-edge-base-red.json, sha256: 22527f5664133616887f65873d78615ce6f9f7560092f923a629e017d214f3e4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/provider-status.json, sha256: 264e1df9ade7dda45e46da8fc8ce645273586acdfd67fa8c1aa07448c4dcc68a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/py311.txt, sha256: f437e24ab81d1314492cb53fd5f47265b18dbac010e17911d03353bc3fcf33d3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/py313.txt, sha256: 3b981196dd8167d3d5418c98a4892b2c9b295185d15aa3a226e49410e40aa5ff}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/query-allow-list.json, sha256: ac347d7d615dc81da050d19dfd8a77ea0322291ba484253d91c67d3aeaa3752e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/reconstruct-successor.json, sha256: 3effef9c5591c89031225f8858871aa5fe82e0e08e075ded07a9839427b5fb65}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/red.txt, sha256: 27adf17df20728947749626134f06e93a0a3ad181730cc859375d5a6fb908e07}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/repair-review-prompt.txt, sha256: f75bb9e2d084d568b20099f39e294455c952f389fd0053ced0f9669e2e526a15}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/review-R1-green.txt, sha256: c889317714dad925839817c45f0e01cc0a11786cd013baa0e7b0cc3a45918f42}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/review-R1-red.txt, sha256: 0dc7f55c302acb670014db70b16d94da04b1db440a706ee9e08e86af0dfcfb32}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/review-R3-verification.txt, sha256: b422ad228ee362cfb3007c302ac2f4dcafc89531d9857c18664065a3a83a91c0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/review-metadata.txt, sha256: ba2a40af2b2eea55fe7a05ab765d9154c3c95cfc26db793d90bdb0be50658398}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/review-prompt.txt, sha256: 0fdc08cd71e8356c1afba5173fb79b6564e8b8bb814cfd172961d66a717ebaa1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/session-current.txt, sha256: a91e63a84609461233a581bcd93204d47c488d848d95352fc23e3b9fa5d93e8a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/session-impact.txt, sha256: 171bcf2f9139210e2d40768ca0f937347d5631f5369e6b29c9e397c2d50da8f2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/session-pins-final.txt, sha256: 732aeb54341afc4f40c2d586590c2da48e4e9d431539f71cb490d05fedfadc97}
  - {path: .gnd-planning/milestones/code-refactoring/notes/code-refactoring-plan.md, sha256: 06508743abf6c039390171e1d85a09f6383da75f43f1993f5e1303d087976d20}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-repair-codex-repair-review.md, sha256: 0bf0a5ad048e79c2342a0cb78988705e5e21d7bfc06981d4f3afb1479b89b36e}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-repair-codex-review.md, sha256: b4b7e4c098175fba3d1d1e665b44b65d79e86c38b37f5be54721c41e6d084c1d}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-repair-spec.md, sha256: 78076924214ccb1deca215d2dc4a16cd0d0e39d368534ca21a3a520961af26b4}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-repair-status.md, sha256: d5d834fd9f2c9a4a0155503e34cccf8ccbc108c715535f216504fbe9053d8f41}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF9-review.md, sha256: 8c41ceb2257523304f3afa188f380765af68ecaabd81bd4c76e5ce629d54279b}
  - {path: .gnd-planning/milestones/public-launch/migration/b3-files.json, sha256: f9bd54fb3c5af60e00feceb00d33ebaa5004944d72398f621e7684d857a86f31}
  - {path: src/gnd/exp/session_replay.py, sha256: 680be236c9320eefc5287f834da7f5f7ac141efd6c89a698b34c3f7c051317a6}
  - {path: src/gnd/output.py, sha256: eccabb9e15fe7ef64d0d108074de06f0c94d9315dc572809e2d57d579be89401}
  - {path: tests/test_rf9_repairs.py, sha256: 4ccd94b92c394535ae742e2b613bb45ada9ee9b93cb244d3baf05d8635c2fd59}
  - {path: tools/gnd_arch.py, sha256: d4bf1eef1e349c1aa051f05b448a98df52476bd2ff4208e0afae2e1b57b2cbad}
  - {path: tools/gnd_layers.json, sha256: 37680b17a57ff576bd065aa981bd7614d19532b676578270c4fa55b62196331d}
---

# Claim

RF9-repair implements the nine owner-selected RF9 findings on the existing topic
branch. Source subject 21487ab contains the production fixes and reproduced native R1/R3
terminal acceptance/reference repairs. The current affected gate reports 257 passed with
one warning; six adjacent v7/v8 replay pins pass. Earlier 480/278/28 and native
minor 4+4 controls retain their stated source boundaries and unchanged coverage.
The native assessments and triage are bound below. These gates establish
the selected repair criteria at their stated boundaries, not release acceptance or certification.

## What shipped and authorization

The owner said "you have my approval to fix the issues" and "continue"; the
separate corpus-first successor spec/RED commit2759da3 preceded production edits.
The original plan and review015 remain historical. The initial approval artifact
binds the initial spec SHA; its delegated instrument corrections and additional
branch cases are recorded in the current spec. All nine findings are within the
named repair scope; no RF10 or milestone-close work was inferred.

- session_replay binds terminal version, attempt count and best identity to the
  reconstructed chain. Terminal/operator acceptance agrees in both directions;
  accepted terminal disposition additionally requires the final contract
  evaluation. This deliberately uses the
  last attempt; its named terminal manifest reference is also checked against
  the final attempt bytes. Honest custom ranking may choose an earlier failed
  best with a different manifest. The
  refusal precedes cache publication. close guards missing reconstructed best.
- session_contract removes the contract's private lazy-profile cache, returning
  the existing immutable version-table entry. Equality, copies and wire state
  stay stable. values imports the concrete Model leaf and uses a module-qualified
  Population ForwardRef for the historical digest API, avoiding a runtime cycle.
- The stale RF6 lookup assertion now agrees with RF7's literal-True rule. The
  live query observer counts literal getattr fact_types/roles; its expanded exact
  successor policy gives all four existing cases a reason. Historical metrics
  and original policy evidence remain identifiable and unchanged.
- RF8's body observer normalizes only a single exact cache write at reconstruct's
  validated return tail. Early, moved and repeated writes stay detectable. The
  intentional integrity change has an exact successor AST hash; historical
  moved-body evidence is not rewritten as a current unchanged-body claim.
- The322-line output helper body moved byte-for-byte from the commands package to
  gnd.output. The old module explicitly aliases all25 historical bindings; old
  qualifications are preserved. Seven service imports use the new home. Physical
  source scans, CLI home map, dynamic inventory and shim inventory move atomically
  with it. Patch effects and omission negatives are checked at the defining home.
- Architecture measurement now exposes package-parent initializer edges and uses
  them for layering. The historical explicit SCC object retains its keys; combined
  package-initialization SCCs are a separate diagnostic. Offline guards use one AST
  Import/ImportFrom parser for aliases, child names, nested/lazy and relative local
  imports. Syntax errors refuse rather than report clean; original roots/policies
  remain fixed. Dynamic import resolution remains outside the static guarantee.
- The18 target manifest adaptations bind current hashes, bytes and modes while
  retaining exact predecessor/source fields. Original units.json, distribution
  authority test and all432 frozen controls stay unchanged. No source-owned handoff
  or certificate is created by these target adaptations.

## Gate output (verbatim)

The exact commands, exits and verbatim summaries are retained in gates.json and
listed below. Complete stdout/stderr streams are retained in their cited files;
headers declare home/worktree/operator-temp sanitization. Intermediate failures
remain evidence of the instruments and environment, rather than quiet passing
claims. No broad default/historical/evidence/census/provider-oracle/proof or
certification replay ran.

current direct and output/graph/offline impact:
```text
Command: PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_rf9_repairs.py tests/test_rf6_index.py tests/test_rf6_query_policy.py tests/test_rf8_structure.py tests/test_gnd_arch.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf5_review_regressions.py tests/test_measure_offline.py::test_measure_lane_imports_no_provider_or_network_module tests/test_measure_offline.py::test_no_network_library_is_reachable_from_the_measure_lane tests/test_measure_offline.py::test_no_network_library_is_reachable_from_the_extraction_lane tests/test_measure_offline.py::test_no_network_library_is_reachable_from_the_generation_lane --tb=short -p no:cacheprovider
Exit: 0
480 passed in 28.91s
```

session impact current:
```text
Command: PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_exp_session_contract.py tests/test_exp_session_store.py tests/test_exp_close_work_gate.py tests/test_exp_close.py tests/test_v71_phase4_successors.py tests/test_public_v71_judgment_successor_guards.py tests/test_measure_offline.py::test_no_provider_client_anywhere_in_the_package --tb=short -p no:cacheprovider
Exit: 0
278 passed, 1 warning in 14.64s
```

legacy and successor replay pins:
```text
Command: env -u LANG -u LC_ALL -u TERM PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py --tb=short -p no:cacheprovider
Exit: 0
28 passed in 28.24s
```

metadata:
```text
Command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/metadata_checks.py
Exit: 0
432 frozen controls unchanged; 25 output aliases and exact body move; 228 modules; zero explicit runtime/module SCCs, wrong-way/entry violations and allowances; 18 exact target adaptations.
Implicit package-parent edges: 4087; structural combined SCCs: 7 (diagnostic, no zero-cycle claim).
```

lint:
```text
Command: .venv/bin/ruff check src/gnd/output.py src/gnd/commands/_output.py src/gnd/codegen/service.py src/gnd/exp/cli_service.py src/gnd/exp/close.py src/gnd/exp/session_contract.py src/gnd/exp/session_replay.py src/gnd/export/verification_service.py src/gnd/extract/service.py src/gnd/fidelity/doccheck_service.py src/gnd/fidelity/service.py src/gnd/review/service.py src/gnd/values.py tests/support/rf5_sources.py tests/support/rf8_sources.py tests/test_measure_offline.py tests/test_rf5_commands.py tests/test_rf6_index.py tests/test_rf6_query_policy.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tools/gnd_arch.py
Exit: 0
All checks passed!
```

working-tree whitespace at original execution (committed/untracked retained evidence excluded):
```text
Command: git diff --check
Exit: 0

```

native Python 311:
```text
Command: PYTHONPATH="$PWD/src:$PWD/tests" PYTHONDONTWRITEBYTECODE=1 /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf9_repairs.py::test_contract_serialization_and_copy_preserve_equality tests/test_rf9_repairs.py::test_population_digest_annotations_resolve tests/test_rf8_sessions.py::test_profile_closed_version_table_and_copy --tb=short -p no:cacheprovider --basetemp=/private/tmp/rf9-repair-py311-current
Exit: 0
4 passed in 0.15s
```

native Python 313:
```text
Command: PYTHONPATH="$PWD/src:$PWD/tests" PYTHONDONTWRITEBYTECODE=1 /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf9_repairs.py::test_contract_serialization_and_copy_preserve_equality tests/test_rf9_repairs.py::test_population_digest_annotations_resolve tests/test_rf8_sessions.py::test_profile_closed_version_table_and_copy --tb=short -p no:cacheprovider --basetemp=/private/tmp/rf9-repair-py313-current
Exit: 0
4 passed in 0.16s
```

independent contract acceptance branch:
```text
Command: PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_rf9_repairs.py::test_accepted_feedback_cannot_replace_contract_acceptance --tb=short -p no:cacheprovider
Exit: 0
1 passed in 0.95s
```

native R1 repair direct/session/store/close/judgment impact:
```text
Command: PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_rf9_repairs.py tests/test_rf8_structure.py tests/test_rf8_sessions.py tests/test_exp_close_work_gate.py tests/test_exp_close.py tests/test_exp_session_store.py tests/test_v71_phase4_successors.py tests/test_public_v71_judgment_successor_guards.py --tb=short -p no:cacheprovider
Exit: 0
254 passed, 1 warning in 26.80s
```

R1 adjacent v7/v8 replay pins:
```text
Command: env -u LANG -u LC_ALL -u TERM PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q 'tests/test_rf1_session_pins.py::test_session_fresh[7]' 'tests/test_rf1_session_pins.py::test_session_fresh[8]' 'tests/test_rf1_session_pins.py::test_session_resume[7]' 'tests/test_rf1_session_pins.py::test_session_resume[8]' 'tests/test_rf1_session_pins.py::test_session_reconstruct[7]' 'tests/test_rf1_session_pins.py::test_session_reconstruct[8]' --tb=short -p no:cacheprovider
Exit: 0
6 passed in 5.65s
```

full-phase source/test/tool whitespace:
```text
Command: git diff --check 26dbff6 -- src tests tools
Exit: 0

```

post-R1 metadata:
```text
Command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/metadata_checks.py
Exit: 0
432 frozen controls unchanged; 25 output aliases and exact body move; 228 modules; zero explicit runtime/module SCCs, wrong-way/entry violations and allowances; 18 exact target adaptations.
Implicit package-parent edges: 4087; structural combined SCCs: 7 (diagnostic, no zero-cycle claim).
```

post-final-native R3 direct and affected consumers:
```text
Command: PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_rf9_repairs.py tests/test_rf8_structure.py tests/test_rf8_sessions.py tests/test_exp_close_work_gate.py tests/test_exp_close.py tests/test_exp_session_store.py tests/test_v71_phase4_successors.py tests/test_public_v71_judgment_successor_guards.py --tb=short -p no:cacheprovider
Exit: 0
257 passed, 1 warning in 28.67s
```

post-R3 v7/v8 adjacent replay pins:
```text
Command: env -u LANG -u LC_ALL -u TERM PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q 'tests/test_rf1_session_pins.py::test_session_fresh[7]' 'tests/test_rf1_session_pins.py::test_session_fresh[8]' 'tests/test_rf1_session_pins.py::test_session_resume[7]' 'tests/test_rf1_session_pins.py::test_session_resume[8]' 'tests/test_rf1_session_pins.py::test_session_reconstruct[7]' 'tests/test_rf1_session_pins.py::test_session_reconstruct[8]' --tb=short -p no:cacheprovider
Exit: 0
6 passed in 5.41s
```

post-R3 metadata:
```text
Command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .gnd-planning/milestones/code-refactoring/evidence/RF9-repair/metadata_checks.py
Exit: 0
432 frozen controls unchanged; 25 output aliases and exact body move; 228 modules; zero explicit runtime/module SCCs, wrong-way/entry violations and allowances; 18 exact target adaptations.
Implicit package-parent edges: 4087; structural combined SCCs: 7 (diagnostic, no zero-cycle claim).
```

post-R3 changed-code lint:
```text
Command: .venv/bin/ruff check src/gnd/exp/session_replay.py tests/test_rf9_repairs.py
Exit: 0
All checks passed!
```

post-R3 full-phase source/test/tool whitespace:
```text
Command: git diff --check 26dbff6 -- src tests tools
Exit: 0

```

After R1, the unchanged legacy version paths retain their previous gates; the
terminal-v7/v8 neighbors are rechecked explicitly. The original working-tree
whitespace gate is qualified in place: it excluded committed/untracked retained
evidence. The full base-to-ef0fe9f diff is reproduced exit2 for trailing spaces in
verbatim pytest output; provider-status.json retains that output. Full-phase
source/test/tool whitespace exits0. No all-artifact whitespace-clean claim is made.

The current session warning comes from the explicit invalid-model serializer
control in test_canonical_feedback_revalidates_model_copy_updates_recursively.
It accompanies a passing refusal test; the gate's exact warning stream is retained.

Initial RED observed23 failures before implementation. Equality and the parent
fixture initially had helper/lane mistakes; the corrected equality RED and exact
base parent-edge miss are separately retained. The genuine launched/no-eligible
session proves predecessor AttributeError and current structured refusal. The
independent acceptance case mutates both feedback dispositions and their byte/hash
bindings; internal replay still agrees, while terminal contract rejection must
hold. Its exact predecessor test exits1 with DID NOT RAISE, current1passes. An
initial attempt to run the nonterminal control with result.json present hit the
existing terminal-resume guard; corrected control temporarily removes then restores
that leaf. Those instrument outcomes remain retained with their corrections.

The legacy session environment mismatch is reproduced on archived exact26dbff6;
changing only LANG, LC_ALL and TERM turns the same original case green. All28
current replay pins pass in that environment. No fixture/golden expectation was
changed. Early graph failures from adding a nested SCC key were corrected by
putting the new diagnostic at a separate top-level key; original graph controls
then pass. Initial lint found seven changed service import blocks needing sorting;
current lint passes and adaptation hashes were refreshed.

## Criteria and coverage audit

| Declared branch / criterion | Positive and refusal controls |
|---|---|
| F1 final acceptance | honest custom-ranked accepted session; forged terminal acceptance; independently forged accepted feedback rejected by contract; accepted terminal downgraded to stagnation refuses |
| F1 version/count/identity/reference and publication | five mutated fields and wrong/missing/best-instead-of-final manifest references refuse; prior best identity remains unchanged |
| F7 absent best | deleted evidence and genuine producer exit2/no eligible best refuse; direct accessor-None handoff exercises the close guard itself |
| F2 inheritance | truthy and strict agree for yes,1,False,None,list,dict; literal True yields the parent type |
| F3 exact live query grammar | actual current policy passes; new literal fact_types/roles getattr refuses; missing/stale/extra/duplicate inventory controls and historical metric controls remain green |
| F4 equality/profile | direct/parsed/copy/dump equality, updated copied version, shared table identity; bounded version-table controls |
| F5 observer normalization | exact legitimate tail; early, duplicate and moved cache writes change observed body; intentionally changed integrity body is pinned separately |
| F6 output move/home | exact predecessor bytes and25 alias identities; observed checker_band patch through CLI; new home omitted from source scope refuses; seven fresh-process service imports avoid commands |
| F6 parent initializer layers | corrected synthetic entry-parent violation missed on exact base, found now; current complete map/zero allowances, original graph schema controls remain green |
| F8 annotations | concrete digest parameter/return type hints on Python3.11 and3.13 through legacy population import |
| F9 AST imports | from urllib/request, alias and comma import negatives; actual generation runtime dirty probe; malformed Python refusal, relative local-import positive and above-package relative-import refusal |
| Authority/frozen boundaries |432 frozen hashes,18 before/after adaptations, units and authority guard byte equality |

The audit is against the declared cases, not only the reviewer's observations.
The close accessor and invalid-relative-level guards now have direct negatives;
original26dbff6 crashes/unsupported parser signature are proven RED. The first
archive scanner attempt reused pytest's current imported module and was not
accepted as baseline proof; explicit archived-module loading before collection
corrected the instrument provenance.
The guarded final evaluation refusal was given its own independent negative after
it was recognized as distinct from a forged terminal disposition. Review coverage
is limited to its inspected source subject; later record/evidence bytes do not
inherit an opinion about unrelated code.

## Measurements and budgets

RF6 base523cdd1a2ae1ad6ea0e8ca092fe29629dd10607c measures375 with expanded grammar
(371 original forms +4 literal getattr); current354 <= ceiling365 <375. Pre-refactor
f5a8318 measures374 at a different boundary and is not the375 baseline. Original
attribute/get metric is299 <=310 <320; literal subscriptions remain51. All four
getattr exemptions are reasoned exact rows. Dynamic inventory count is preserved,
with physical paths retargeted for moved output definitions.

The map covers228 modules with zero explicit runtime/module-only SCCs, zero
wrong-way/entry violations and zero allowances. It inventories4087 implicit parent
edges; seven combined SCCs from package reexports are diagnostic, not a zero-cycle
claim. Cross-lane edges retain their existing policy treatment; no zero-cross-lane
claim is inferred. Metadata checks and new home alias/patch/scan tests bind the
move; source/name existence alone is not full ABI proof.

Measured final touched paths: 77 <=80; added production including the exact 322-line move: 458 <=2000; added tests/probes: 502 <=2000; moved production 322 <=1000. Non-evidence prose count includes this completion and the checkpoint annotation, and is bound in budget.json against 1500. The initial measured estimate is retained; no original ceiling was missed or enlarged.

## Independent review and triage

One reviewer is one reviewer. Initial native gpt-6-sol/xhigh read-only assessment
of ef0fe9f exited0 and returned two observations. R1, hardening, was reproduced
with an honestly accepted result downgraded to stagnation: pre-fix DID NOT RAISE,
current bidirectional acceptance agreement refuses. It preserves the independently
failed-contract and custom-ranking siblings. R2, completeness of an evidence
argument, was reproduced as full-diff exit2 on retained output whitespace; the
literal original working-tree gate is qualified in place, and actual complete
source/test/tool checks are recorded separately. No all-artifact cleanliness claim
is substituted for retained verbatim logs.

The one bounded repair assessment of b8d7e1f exited0, confirmed R1/R2, found no
R1-introduced regression, and raised the pre-existing named terminal reference
binding gap R3 as static hardening inference. Three actual accepted custom-ranked
sessions prove wrong, missing and best-instead-of-final reference mutations pass
pre-fix and fail the refusal tests. The last one-clause repair binds the producer's
named reference to the final attempt's canonical bytes; it is current-byte locally
verified with 257 passing affected cases, six adjacent replay pins, body/metadata/
manifest/lint/whitespace controls. This last clause has no third native assessment:
the declared/authorized two-assessment budget is exhausted. The retained returns
name their actual inspected commits; no opinion is projected onto newer bytes.

Both reviewers independently matched 432 frozen controls and 18 exact adaptation
rows; initial review also recomputed the354/375/374 expanded query boundaries,
299 original metric, four reasoned getattr rows and exact output move. The repair
review independently matched the exact R1 AST successor and scoped whitespace
results. Their session/test checks were by reading retained probes/logs; neither
ran broad suites, verified CI, certified source-owned units or resolved dynamic
imports/package-init/OQ ownership. Final R3 disposition is primary reproduction
plus local verification, not independently confirmed source correctness.


## Refactoring review

What did this phase's work reveal about existing structure that should change?
**Refactors EXECUTED:** shared output definitions now live outside the entry
package with explicit historical aliases; all move, patch, scan and consumer gates
pass. Contract profiles use one immutable version table rather than equality-
changing lazy state. Query, body and import observers each retain one parsing/
normalization home and exact successor evidence, reducing duplicated authority.
These behavior-preserving parts are behind the same green focused controls as
the explicit correctness changes. No extra refactor was silently added.

**Seen but deferred:** package namespace reexports generate seven combined static
SCCs. Their redesign is assigned to code-refactoring milestone-close architecture
reconciliation; the current diagnostic does not establish an import-order defect
or justify an unapproved namespace ABI change. Historical body/ownership
reconciliation, shim retirement and prior original budget misses keep their
existing close owners. Source-owned import-walk authority remains with its named
public-launch/source successor, not this target repair record.

## Boundary — what this phase does NOT establish

One reviewer is one reviewer; native same-provider review is not a maintained
panel, model-diverse consensus or proof. Reading and selected probes cannot prove
all platform, timing, dynamic-import, installed-package or release behavior. The
new digest hint control starts at the historical population API; values-only
introspection before importing Population is not claimed. Explicit SCC counts
and combined initializer SCCs have different meanings and remain separately
identified. Exact static query grammar is not arbitrary dynamic access resolution.

Focused verification follows the approved repair impact boundary. Broad default,
historical, evidence/census, provider-oracle, proof, distribution and certification
work stays on explicit owner or separately scoped CI cadence. Changed historical
opinions are unavailable on new bytes; focused successors do not recertify source-
owned/release units. Original authority units and432 frozen controls remain frozen.
No source-owned OQ transfer, current attestation, release, merge or milestone close
is authorized or established. Existing draft PR10 is the delivery surface.

The outer work-gate mutation controls are not a complete close command across all
obligations. The selected terminal checks cover version, count, best identity, acceptance
agreement/final evaluation and the named final-attempt manifest reference. Other
free-prose/arbitrary terminal metadata is not claimed fully rederived. The guards
remain defense at their declared boundaries; no numerical
rate for untested misuse is inferred. CI observations bind their stated commit/run;
account payment/spending-limit refusal before steps is no passing code gate.
Required CI and review conversations must succeed before a future merge.

## Open questions

- The selected RF9-F1–F9 target correctness observations are addressed by these
  repairs and current focused evidence. The independently launched/no-eligible
  case resolves the narrower original F7 reach uncertainty.
- Source-owned OQ-V52-P1-IMPORTWALK-1 remains open with its original owner. Repairing
  the selected target AST guard does not discharge source-owned authority.
- Prior RF1-OQ2/OQ4/OQ6/OQ7, original RF6b/RF7/RF8 budget misses, historical-body/
  ownership reconciliation and shim retirement retain their existing owners;
  code-refactoring milestone close must sweep them explicitly.
- Package-reexport combined SCC interpretation/design -> code-refactoring
  milestone-close architecture reconciliation, preserving namespace ABI evidence.
- GitHub billing/required CI -> repository owner/platform before any merge.

## Refuted premises

The predecessor terminal result and accepted feedback disposition cannot alone
establish final contract acceptance; the actual forged-result and forged-feedback
RED controls refute both. A missing best is not merely hypothetical: the genuine
producer-exit session reproduces the predecessor traceback. The original expanded
query baseline belonged to the RF6 source boundary, not f5a8318; exact measurements
correct that provenance in the spec/policy. Package-parent imports prevent a claim
of zero combined SCCs even though explicit SCCs are empty. A malformed candidate
may be an eligible verifier refusal, so it was replaced by the actual failed
producer instrument. Desktop environment differences, not new session semantics,
explain the original legacy-pin mismatch, as the exact-base paired control proves.
No original plan/phase015 history is rewritten into a retrospective passing claim.
