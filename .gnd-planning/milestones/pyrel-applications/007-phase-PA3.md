---
milestone: pyrel-applications
station: phase-PA3
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PA3
date: 2026-10-13
source_base: b217751
gate:
  command: ".venv/bin/python -m pytest -q tests/test_pyrel_application_publication.py tests/test_bookrec_tutorial.py tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_derivations.py tests/test_pyrel_application_driver.py tests/test_pyrel_application_corpus.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf2_pre_move_pins.py -k \"not measure\""
  exit: 0
  output: "336 passed, 10 deselected in 18.96s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately scoped CI
  reason: affected integration and application consumers selected; broad exclusions preserved
evidence:
  - {"path": "src/gnd/export/applications.py", "sha256": "ee7e813c3a3bd717c94090376c7d610464e51a1ac63ba53d15319b9cd5cb6090"}
  - {"path": "src/gnd/examples/bookrec/extension/bookrec/native_query.py", "sha256": "0a27b63fda9d2a2160551e36cabb14a79a5bc87bc8ec5b5052ada0a1b25b4ba3"}
  - {"path": "src/gnd/examples/bookrec/extension/bookrec/cli.py", "sha256": "69dfebf4e31ef17f4fe38405c50e23d67fa49270433e6678b2314dc67c3fefe3"}
  - {"path": "src/gnd/examples/bookrec/architecture.contract.yaml", "sha256": "2edf14e9b5f1c03f5813fdecc16af15b2bab1fbffb15cc7cf5fb39cf52cd4053"}
  - {"path": "src/gnd/examples/bookrec/README.md", "sha256": "5079f7e37b6fbf1e012a5c005ce0fb26bc362b99c6fefcb835e3d8be05e9378f"}
  - {"path": "tests/test_pyrel_application_publication.py", "sha256": "c0d4f536cdaf77913ce0b5b93d582098588d1695428754d165be37ceb70ffa3b"}
  - {"path": "tests/test_bookrec_pyrel_application.py", "sha256": "f7ca5261b61231de4d9c4c8ca7726f35b768a9881ef1fc022db5dba8aae14120"}
  - {"path": "tests/support/pyrel_application_successors.py", "sha256": "d6db9e66070ae40de4e73aa22912725b1b452d803b2abbc3f01d7b4897f8e968"}
  - {"path": "tools/gnd_layers.json", "sha256": "854d262d0b866e5e3153c24045d12502e1e9d1856696fd22ccb840b5a88c7908"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/architecture-contract-green.txt", "sha256": "bd53ab21ff93b781183babcbaec26181248ed7b9a9f3cc28aeaa4fc83151de0f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/attack-helper-green.txt", "sha256": "4f12a245c67e28c589776118232da052a572aea16e493f3baf4beeb30e1cb7ab"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/capture-figure-source.py", "sha256": "437ade26910266f750168828f79451e0c05212372bef703025738664831c4f8b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/capture-final-figure-source.py", "sha256": "9c8d9039f44570f5d7eae58457c7d32dda65fa65fd66e412927b48fcdb6559f8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/completion-focused.txt", "sha256": "dbe7f099dc79c8b7ef07d3b779b8cbb00de660d1ce6760f54d8812079146deab"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/completion-lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/completion-native-final.txt", "sha256": "c6e289320651b83115e6e6e5e30d49cdfb64042a285bf197252833f308fe0b4c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/completion-native.txt", "sha256": "df50c37e9746c23e36cde5ab5e519da8b821bdaea15f5f9f716da16424c54ec8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/computed-shape-green.txt", "sha256": "5c0349f2d3b6ebb643b6e59c8009bfbe7e7e4bc370628b83c90be52675038be6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/computed-shape-red.txt", "sha256": "4e77a47c788fa7af4a112d273ea8329abd980e95b60f4a90e26347b96313db8b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/dynamic-query-successor-initial.json", "sha256": "6fe165af1ae58379863c4ef993f84e6d0d6cb68fad86edfaf955904093f3b1ba"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/dynamic-query-successor.json", "sha256": "335d122be8be2b342c648df7b8414ff70ad78a806925173213dabc956809c2ac"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source/advisory.population.json", "sha256": "34a162839ed39ae3bfa0ec9d8037fdebc3a81cadc7ed6e4b330fcf41a754d305"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source/advisory.report.json", "sha256": "167b663325b3fe73317f746cecc20ca4ddf3471da78029bbf9fcba6d1d91ce70"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source/complete.population.json", "sha256": "0d8617807ed9ecf395a0de1a1b2473cf57d356e1e11398a52468a57b80de7a99"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source/complete.report.json", "sha256": "e92da3ea9cb4e32ccc5027ffdc37cd0d7de773002d3d8bf5d7a478dcf7f26a1e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source/preferred.population.json", "sha256": "1e6f53d90b15abb43a85c55388df99d35d5e4057d5fd7a38a833ac4227cb3b0c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source/preferred.report.json", "sha256": "c4621dfc0974bcceccaa23f5914ce4ab86dd72c8d835e9f819add6a4f36019cc"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source/strict.report.json", "sha256": "6528b160f86889f041c90da642d28b0fe3aeb2b45cbd4c6df43d872b2611df24"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final/advisory.population.json", "sha256": "34a162839ed39ae3bfa0ec9d8037fdebc3a81cadc7ed6e4b330fcf41a754d305"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final/advisory.report.json", "sha256": "167b663325b3fe73317f746cecc20ca4ddf3471da78029bbf9fcba6d1d91ce70"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final/complete.population.json", "sha256": "0d8617807ed9ecf395a0de1a1b2473cf57d356e1e11398a52468a57b80de7a99"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final/complete.report.json", "sha256": "e92da3ea9cb4e32ccc5027ffdc37cd0d7de773002d3d8bf5d7a478dcf7f26a1e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final/preferred.population.json", "sha256": "1e6f53d90b15abb43a85c55388df99d35d5e4057d5fd7a38a833ac4227cb3b0c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final/preferred.report.json", "sha256": "c4621dfc0974bcceccaa23f5914ce4ab86dd72c8d835e9f819add6a4f36019cc"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final/strict.report.json", "sha256": "6528b160f86889f041c90da642d28b0fe3aeb2b45cbd4c6df43d872b2611df24"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-final.txt", "sha256": "4b61d75fbf589f9140bc311c0fdbf49f85a791d4e4d3841430ffe966b923da08"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-initial.json", "sha256": "78ccfd368f241f5ff44d5b915efbcf2421f1864fba9699d906363af242f96f0b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired/advisory.population.json", "sha256": "34a162839ed39ae3bfa0ec9d8037fdebc3a81cadc7ed6e4b330fcf41a754d305"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired/advisory.report.json", "sha256": "167b663325b3fe73317f746cecc20ca4ddf3471da78029bbf9fcba6d1d91ce70"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired/complete.population.json", "sha256": "0d8617807ed9ecf395a0de1a1b2473cf57d356e1e11398a52468a57b80de7a99"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired/complete.report.json", "sha256": "e92da3ea9cb4e32ccc5027ffdc37cd0d7de773002d3d8bf5d7a478dcf7f26a1e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired/preferred.population.json", "sha256": "1e6f53d90b15abb43a85c55388df99d35d5e4057d5fd7a38a833ac4227cb3b0c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired/preferred.report.json", "sha256": "c4621dfc0974bcceccaa23f5914ce4ab86dd72c8d835e9f819add6a4f36019cc"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired/strict.report.json", "sha256": "6528b160f86889f041c90da642d28b0fe3aeb2b45cbd4c6df43d872b2611df24"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-repaired.txt", "sha256": "4b61d75fbf589f9140bc311c0fdbf49f85a791d4e4d3841430ffe966b923da08"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source-review-repaired.json", "sha256": "e23b03d9f795c2f137ffa6550f82679fc275c9ac330b4ff08b9016e8b1fcf5af"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/figure-source.json", "sha256": "77b58dcb908147c82aff5bbce6aae894406b154f623ecb2754b1e664f2ab0339"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/final-native-regressions-green.txt", "sha256": "5fd10206e9b62ae677341a76e7793e1e37352277372879f3e7271eb478ffc64e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/final-parent-green.txt", "sha256": "dc1b69d9507849bce7876f53786e1b696001163fbb1902852fa04f68eae23513"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/focused-current.txt", "sha256": "7b41f6ebc7f13b4a7779f15db7ee932f834c473df5f7a69bb8005404305306ee"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/focused-expanded.txt", "sha256": "96261143a6c1c9f7fcea5f5079cbd9a979c6c49ade823592633776dc6d4e9044"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/focused-initial.txt", "sha256": "d3fc88cb1f659bb46d7bda43b67f87d9087600b14c960bb2a679879a362f7b5f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/focused-repaired.txt", "sha256": "69a373d999880d354a90a5310ce4c458c219fa25f212e5ca012175c82cdbfd4c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/framework-inheritance.json", "sha256": "35f36dc062b7473af402dce37cec3cf71ecb74defc0652b8ab56787dc6cd1822"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/fresh-checker-native-green.txt", "sha256": "e6d1aec36d3cdd69c344eee54af4306b42cdece778faa2a6689c7c7d882da21b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/lint-current.txt", "sha256": "fcbc5b74f8ebfd865bc2f9deeb970c394c42b3bd7d894cdcd31d261fc83b6071"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/lint-initial.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/lint-repaired.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/metadata-type-red.txt", "sha256": "7a4f31479ab9f7a20a0a70e817b2d7a2608d6929946f872bd83dbb9e13067b9b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/model-filename-red.txt", "sha256": "0fcc92c7adc43b0fc0fc68a46d8466fd87057f4aed798f87231f4127570b5e47"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/native-current.txt", "sha256": "b643056a058a3653e632408a3110f58dfe2a90454741e6ec0c918a473822d096"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/native-expanded.txt", "sha256": "051c384fcc4f8d1157095e7824e1f236c26f0173e803db0ca8e76c840fa27792"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/native-initial.txt", "sha256": "5de450e73c3caca5469d20efb9046a6593b6a9f84ebe148f46eb795eea60deea"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/native-interface-red-sanitized.txt", "sha256": "5aab64933ea847e913ec276edc8383d2fea3089ea8f6ebcc2d4bcca06cddf2fd"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/native-red-sanitized.txt", "sha256": "d4dfb0dc0a77841565c8786b72baf660714d608e10025f2930fdc870a783bc02"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/native-repaired.txt", "sha256": "08ad29519512457c40d148b97738af3e04aac83689dd1636b294b304126cb354"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/parent-figure-initial.py", "sha256": "bc5b66b2d0851b6c35ac5514dc9d427d0fb7bc20d0b99eb550ac6b1954fbbb8d"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/parent-red.txt", "sha256": "616780dca167baec375f51f66c78e88ea25fb0f08071fbc886d79ef5f1ca32b8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/pyrel-successor.json", "sha256": "482c4f1bdaa18714bc963147cc2ad62dd8bb167d1c599f01021441398af9c01b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/query-figure-initial.py", "sha256": "e8f03ff243dd47fd7da18090691457d3114bc9f69f383864f27d8d490bfd7767"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/query-successor-initial.json", "sha256": "82afb902902e5943c4f32e21f8e7b2149e25bef586b7016a6059c147745b902d"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/query-successor.json", "sha256": "01d323688112936c742611847594c92c90ff7cfe8414ffabf0ba84a4afd8861b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/review-native-green.txt", "sha256": "c3f081891ee9187d2249ba9d5b66c9cb8d256bc89632a9d18b58ffe49e46a3a2"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/review-native-red.txt", "sha256": "1eaee43f593d92ebeffd4be120efc72867d975598d9673a8585e98f9f48142f8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/review-parent-expanded.txt", "sha256": "79d0059236333601c0358bb7b72aea5e067b9ee6edfb2a47b27c99e430a0fd8a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/review-parent-green.txt", "sha256": "9a0c283dd117c581ee0ea452ae7b648a3c0bccdf3453e6c2055563bf56152606"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/review-parent-red.txt", "sha256": "9576ef9c0d905391c118602bc82737d1015e172ae7f87ca5826178811941209c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/sanitization.json", "sha256": "c9fdba4ffe37ea1ec1a2f0c5612aadddbc15b7418b3294d5ccc15d73f9ea538d"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/unknown-metadata-green.txt", "sha256": "2caa7e859bbe8ee937b2c31ce7e235f378ccbce81626f4f25a028b9416873ffd"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA3/unknown-metadata-red.txt", "sha256": "ed9ea7c2f0b685f670dbea53bea8d8cd8eb8e9198b22b88998eec52f6b75ce19"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA3-spec.md", "sha256": "f8b871a604205459d7f93775acc974d7bf2ba0abe96028c541e0eb6d7b6da8ff"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA3-review-prompt.md", "sha256": "82977497ba239a5591a769f8cd87941def1ecb5c2e83a68cacb4822ecfd959d5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA3-repair-review-prompt.md", "sha256": "84b560cc8acf435e91762a1232b40ead6b85f41f02410e66069726b7e4ef8038"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA3-claude-review.md", "sha256": "b024759b8710e9f72e26d12087767878c4369e6e30b9e9c0a94ce1af3a451c05"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA3-claude-repair-review.md", "sha256": "e587011a9693970a903fc00844724a910a8774b937e4c508ebcf6ace0365fbae"}
---
# Claim

PA3 completes native BookRec proposal/calculation and independently checked
publication for the baseline, strict and complete models. Actual native tests
assert the full eligible pair set, selected order/limit, blocked/read pairs,
computed claims and exact named rejection witnesses. These are synthetic static
snapshots; no source truth, ranking quality or actor permission is established.

## What shipped and criteria

PA3-C1: optional --backend pyrel and explicit --pyrel-python retain the default
Python/GND CLI path. Developer-owned joins/negation compute reader/book pairs;
Python handles deterministic tuple presentation/user selection/limits only.
Advisory Ada cosmos/map publishes with genre warning; strict rejects; preferred
map/river repairs; complete produces five preferred pairs and computed claims.
Unknown reader and limits0/101 have discriminating reason assertions.

PA3-C2/C3: five post-proposal faults actually reach unread_only, age_appropriate,
preferred_genre, all_eligible and the eligible derivation. Each refuses publication
and then repairs/rechecks. Asserted coverage remains mandatory even for empty
relations; missing complete metadata refuses2 rather than crashing. Supplied
computed claims are refreshed in a proposed candidate, never trusted as premises.

PA3-C4: shared export parent captures bounded regular source/query bytes, validates
source model declarations via load_model_bytes, stages native queries through
bounded process lifecycle, and uses a fresh checker directory/build/runtime after
query group cleanup. BookRec explicitly owns recommendation; every other asserted
multiset, instance and metadata value retains captured source, with exact scalar
types. Only computed heads may be added. Full report inventories, metadata,
status/exit and model/candidate bindings precede atomic no-clobber publication of
captured checked bytes. Input/output collision, existing/symlink output, owner
race, source change, child-path mutation, malformed/missing/misbound/partial
artifacts, process timeout/truncation/spawn failure and crashes are exercised.
Private stage names are independent of model filenames. No native fallback or
GND population evaluation supplies calculation/checking in this lane.

PA3-C5: figure-source.json chains retained prior captures and contains four new
native scenarios on final parent/query bytes, model/input/candidate/report hashes
and exact source-to-figure fields. Actual graphics remain PA5 work.

## Gate output (verbatim)

Focused command is the frontmatter gate; exit0:

```text
336 passed, 10 deselected in 18.96s
```

Command: .venv/bin/python -m pytest -q -m pyrel_oracle tests/test_bookrec_pyrel_application.py
Exit0:

```text
24 passed in 50.94s
```

Completion-lint.txt retains the affected-source/test ruff command's exit0:
`All checks passed!` Architecture-contract-green.txt separately retains10
existing BookRec checks after new flags/query module declarations. Final figure
capture exits0 with four measured scenarios. Framework-inheritance.json verifies
unchanged runtime, measurement tool, frozen matrix/answers, lock and all137 model
bindings against PA2; no repeated full137 execution is claimed in PA3.
Direct source reads361<=365, original metric306<=310, layer allowances0. Historical
RF/compiled/PA1/PA2 evidence and every frozen model/corpus byte remain unchanged.

## Review and reproduced dispositions

One reviewer is one reviewer. One Claude initial and one bounded repair pass
are retained. Initial reviewer disclosed one accidental no-op Python invocation;
no project/native tests or providers were executed by it. Repair reviewer reports
read-only operations only. Working-tree changes and reading limits are disclosed
in both outputs. The final owned low fixes were not given a third reviewer pass.

Initial F1–F4 were reproduced red: query replaced the checker and forged an
accepted report; rating erasure allowed Ada/read; query crash1 became rejection1;
malformed candidate3 became missing-report70. Repairs create fresh checker files,
preserve nonowned source, map crashes70 and retain malformed-input3/diagnostic.
The additional real native replacement-attack control rejects under
age_appropriate, proving the fresh checker actually evaluates the bad candidate.
F5's collision branch was dead and removed; safefs creates missing output parents,
so that proposed missing-parent error is refuted by its located implementation.
Regular-read operational errors remain nonaccepted70 in this app interface.
F6 controls now reach named versions/intake/coverage/limit/ownership branches;
wrong-version resolver is a test double, not another installed SDK claim.
F7 environment is an allowlist; actual child denies ambient secret/RAI variables.
F8 conservative work refusal is retained/disclosed, not a promise that every
row-bounded join is admitted. F9 prior data captures are immutable predecessors,
with hash-matching source snapshots and final successor measurement.

Repair R1/R2 were reproduced red: metadata1 became true and reserved model names
collided with private artifacts. Owned final fixes compare type-exact JSON and
use a fixed private source-model name. R3 reason assertions and preservation/
ownership branches now have public-path controls. R4's unconfirmed credential
file discovery was measured: actual native query and checker succeed with open
operations for .rai/.snowflake, raiconfig files and .env denied by instrumentation.
Explicit Config and Model construction are located in the pinned SDK. HOME is
not repurposed. This is measured config independence, not a host filesystem
sandbox. R5 is settled by the single final24-case receipt and final post-edit
focused/lint/architecture/figure evidence.

The original19 parent and6 interface controls were red before production.
Later branch controls were added after initial implementation and are not
credited as pre-implementation red; individual review/owned fixes carry actual
pre-fix reds. Sanitization.json discloses path-only edits/raw digests; original
committed preparation red streams remain unchanged with sanitized successors.

## Refactoring review

Refactors EXECUTED: one shared export applications parent owns capture/process/
report/preservation/publication for both upcoming apps. It reuses gnd.process,
public safefs and existing runtime admission/inventory helpers; no second policy
translator/evaluator is introduced. Domain queries remain source-owned examples.
The explicit ownership option avoids a hard-coded BookRec source guard. Exact
query successors count new accesses without blanket exemptions or historical
recapture. New home is mapped in export lane; old lookup identities and shim
inventory are untouched. No shim retirement or source-owned handoff.

## Standing rules and boundaries

Totality: bounded regular reads, strict JSON artifacts, declaration validation and
nonaccepted exception boundaries with malformed controls. Algorithmic bounds:
1MiB inputs,4MiB artifacts,100k conservative work,10k query results,60s children,
1MiB streams, actual timeout/truncation/group-cleanup tests. Validation order:
output absence/interpreter, captured declaration admission, native proposal,
source fidelity, independent full acceptance, source stability, atomic publish.
Complete policy traversal: existing runtime inventory and exact parent report
walk include every constraint/head. One normative home: applications-v1 remains
runtime; app orchestration introduces no duplicate policy prose or predicates.
Measurement: independent pair expectations, actual SDK ordering limitation,
post-proposal faults and all reproduced review controls. No broad replay,
certificate, merge, remote publication or installed-wheel acceptance.

Query code is trusted local code, not host-sandboxed. A detached process in a
new session is outside process-group cleanup; no adversarial host isolation claim
is made. Conservative work estimates can refuse small but expensive-shaped data.
Budgets: parent228/600, example122+16/300; final tests540/560 after the recorded
bounded increase. No further review loop is authorized or claimed.

## Open questions, inheritance and next scope

PA4 owns native expense aggregates/approval guards through this shared parent.
PA5 owns six accessible source-grounded graphics and executed offline/native
learning paths. PA6 owns fresh wheel/target-only acceptance and four selected
local close reviewers. Prior legacy runtime/entity-concept maintenance residuals
remain with GND maintainers; app queries use primitive relationships instead.

Future native-query-budget-optimization, owner GND application maintainers:
conservative product estimates refuse some sub1000-row data. Future
native-application-diagnostics, same owner: regular-read operational failures use70
rather than generic GND filesystem bands. Host sandboxing is explicitly outside
this local trusted-example milestone, not an unfulfilled acceptance claim.

Delegated completion (auto=true): named milestone authority persists. Final
source/evidence digests above and approved spec amendments govern this acceptance.
PA3 is complete only for the stated finite application scope. Continue PA4 next;
PR merge, release and certification require separate current owner authorization.
