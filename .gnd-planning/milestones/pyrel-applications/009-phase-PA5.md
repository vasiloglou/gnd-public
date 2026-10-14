---
milestone: pyrel-applications
station: phase-PA5
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PA5
date: 2026-10-13
source_base: bcf9126
gate:
  command: ".venv/bin/python -m pytest -q tests/test_pyrel_tutorial_experience.py tests/test_external_runtime_tutorials.py tests/test_documentation_tutorials.py -k 'not documented_learning_path or bookrec or expense'"
  exit: 0
  output: "119 passed, 13 deselected in 22.33s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately scoped CI
  reason: selected application/tutorial/runtime/docs consumers; broad exclusions preserved
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/accessible-desc-final.json", "sha256": "3581fc4df74a546c16fcea8d29a40597cd4fc66fb3277b78919a6e4705109598"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-bound-steps.json", "sha256": "a9c04a8b3e0ff982acccd890acd3ebcc5ab43569c9c5e99e072cc4dc159b3549"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-completion-steps.json", "sha256": "80cc070a8fd742a8e5a11b3ff9e5a17b4f7e97856ae20b89f1459ff54e45100e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-desktop-initial.png", "sha256": "b2af55ec744f2a8d26b57c42928c5dad8acac0290fb3029d58ef5ad028f6e3b9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-final-steps.json", "sha256": "e63f2afdfe012fa32e056ef7ff9f349c0349e1765eb90a54f24c355f94d46f8b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-native-bound.txt", "sha256": "13b1cc33ddd4e4aa54981738907b15146c6de05b791c5c13462acd2e4040b81e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-native-completion.txt", "sha256": "13b1cc33ddd4e4aa54981738907b15146c6de05b791c5c13462acd2e4040b81e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-native-final.txt", "sha256": "13b1cc33ddd4e4aa54981738907b15146c6de05b791c5c13462acd2e4040b81e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-native.txt", "sha256": "13b1cc33ddd4e4aa54981738907b15146c6de05b791c5c13462acd2e4040b81e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-offline-bound-steps.json", "sha256": "81e260d28c90ad57b541e51592ad9ecbf76d226333e669c391bfb9efe3958f6b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-offline-bound.txt", "sha256": "a98e675c722657275867c5a27b0b4cdc287188e58bbdcfb104fc606fdb291afe"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-offline-steps.json", "sha256": "11482613e40fd132b1d596d37eac45e94fef8eee7ec53354ebeca8b4e50cc7b5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-offline.txt", "sha256": "a98e675c722657275867c5a27b0b4cdc287188e58bbdcfb104fc606fdb291afe"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/bookrec-steps.json", "sha256": "cf7636b37a6d4f2adb589b0778eb924c57232cafd37ae93d07595b2adf7138c3"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/completion-focused-final.txt", "sha256": "35b3ca5b02b8647560aebe8d9b5adff8de45aa4d67c30786836dbfdacee21485"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/completion-focused.txt", "sha256": "98b1bd4e294b23abde3b71b4447496365348bc3919fe00d2dd048d2cfcd36f9f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/completion-lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/completion-owned-focused.txt", "sha256": "cc4d6e57b075097634ce09b678b25c1e9fe21e670ca6252455373063f18671e6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/completion-owned-lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/contrast.json", "sha256": "f82b6cae81c2e55b2b9c0b451395adb17fb0f60c3ccdc95fb25087456bf68ff3"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/demo-timings-final.json", "sha256": "3f5b9025b3754880ecb0f7ce402930d16fae8cb17c17f7baf9e6164c25d2f098"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/demo-timings.json", "sha256": "97745f90db04a910fa693a75c98e208268a06c95f1c502df5f9611a63603dfd4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/direct-repaired.txt", "sha256": "382697b0d3bd60b48f739f251185e2c58a3751faa7d269e9733d4e22e7b39680"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-bound-steps.json", "sha256": "e9d6432deff1b927366cd93fcce66d2eae8ab93fa50ca84f48ff6317a4807b07"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-completion-steps.json", "sha256": "f132c6ccecc438d79c3682982e9887f4a8df7f305d031a46a8b4f4fd9572e9c8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-final-steps.json", "sha256": "ceb0a6969a24e8769c2c77f40fba38bf15c83926ac59e624b9f7e69d3be1b937"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-native-bound.txt", "sha256": "2a1b18b9806a95ba9c3342d2a98df0a0075468c693db2951d87a1fd4bb293706"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-native-completion.txt", "sha256": "2a1b18b9806a95ba9c3342d2a98df0a0075468c693db2951d87a1fd4bb293706"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-native-final.txt", "sha256": "2a1b18b9806a95ba9c3342d2a98df0a0075468c693db2951d87a1fd4bb293706"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-native.txt", "sha256": "0b422ff377bf2fba94c0106fa165ac703fb52fb53319e9a729c5dd025446ecd4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-offline-bound-steps.json", "sha256": "855453fcc5ffb2250168037def460b0fbe379d5ed11d2df27392c41307dafa22"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-offline-bound.txt", "sha256": "729804bf27cd276e1d30dba7a55ef1a4932970303414032117216b5dab926756"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-offline-steps.json", "sha256": "35a1832506f16f5d020b089d99cb85dcd90a4a05cfdb0952e3034f0e5801b9b4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-offline.txt", "sha256": "729804bf27cd276e1d30dba7a55ef1a4932970303414032117216b5dab926756"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/expense-steps.json", "sha256": "eb40996ad4e7b839f36d3333709352f178479e7654b24aeffc9ede614948f4c1"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/experience-green.txt", "sha256": "0acf2c70be5a3b4b1d5c4d5252018b6444c3b093480c58ed4c0a68bdffb0e618"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/experience-red.txt", "sha256": "bfec83d09c9ac75df37248f483044e51e116091d68a19a513f043bc333437a39"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/final-assets-green.txt", "sha256": "4a965d9dc02536c542c280cea54aec5dc774809528ec5010beb43d114e50a36b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/final-owned-green.txt", "sha256": "3df1c9a99346f0f6b7a1e15f362f257eaf61db7a92336350206a8cd8ae2930a0"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/final-source-bindings.json", "sha256": "9678c1facecb25dce141d423e37b1d4b269091d09779c7e5b3ded4621950d14f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/final-text-enum-red.txt", "sha256": "b370371636858d9e2c0d901e5b78af48c980a7ee2c3d09e895439844e2599a25"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/focused-final.txt", "sha256": "44054aca47ced6e8458a27cdc2f921e384ea4c686ac3736cd9780f4e3d7bc718"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/focused-repaired.txt", "sha256": "5c8c50338efaf6c6faec98521374cb3ce97fddefb82f550d697b01e487943dc1"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/graphic-binding-green.txt", "sha256": "306c0e6b70fc3478d15e92f5d52d1321f3d9a0defd879ec737dacfdf08895678"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/graphic-binding-red.txt", "sha256": "70cb1d2a9c58c1d144ddad57e563968ffc010559b1181f8e8f3750af90365a09"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/interpreter-selection-red.txt", "sha256": "3a836dcb15b0c31b2812c70cc6ec6008ee496308e463f834b6a693f0abd450c4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/keyboard-neighbor-green.json", "sha256": "e8288c3c6ef9928cee13c82b68ead5c1b73a148b91081fc613abf162e07b0b8e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/keyboard-neighbor-red.json", "sha256": "c369e701a3f50cb0c480dfb305b91697565afcb4ce043da8ef18919bd50a04d9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/keyboard-scroll-green.json", "sha256": "f3abb834afd404cb17173f77d6ad968e266889521ede83277815ef2e2a9d4147"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/keyboard-scroll-red.json", "sha256": "a88152303f435f2c9f37a1851e62f8926105073e7327e8f272ddfc02eda3705a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/lint-final.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/mobile-accessibility-red.txt", "sha256": "6d69c9ef9409aba59a0da77a8476b1b6d3a7614b4c5855ee68d5b26af882f110"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/native-path-red.txt", "sha256": "32b305c1b8473631e8d41b6ae4c1198d0701a1e49efe134d1d04e055ff6f0f14"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/reader-prose-red.txt", "sha256": "35878b341471197bc2cbf0f2b25494b7833271ef31089714094ce834b2c4a706"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/receipt-path-red.txt", "sha256": "ec0ceceeaeca8710b2038db65a31b6321f3fb86fd38d00863a7a7c74f45549f6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/receipt-shape-red.txt", "sha256": "43d6aa6a8964c3f0af421adab155d62a251232f53f764ca1f9eb713c7c54b383"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/render/manifest.json", "sha256": "13d105dc52ba74c8fcd9c5df07d6a30df18a090af68edcc0ab88bd565d0734f2"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/render-final/manifest.json", "sha256": "61f75c8590687545e1749f3f312eb17ae157ad26d165f15f55d906a56fb2cb6f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/render-observations.json", "sha256": "e538724fd8eb1115bba8a698a14bb7c2d9bb5519c21be7a864470926a6b42da3"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/sanitization.json", "sha256": "ba4311e791694c9b12562d89d7d44e70104e53a0d87d12add1bda84a828e0bdb"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-build-accessible.txt", "sha256": "617a4a74e27d401ffc4f0b3e4693b54c81b385554426ac34822f5f9700bc9f34"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-build-final.txt", "sha256": "4998f958bbc37f264f84932869770b6f93a0ec7740adf1b3e069db5f83f61752"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-build-owned-final.txt", "sha256": "41b54ca16f6b66709212e9b754d8896a5b72ecc92627a365d0ba424ae1a961c2"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-build-repaired.txt", "sha256": "e485e80daf463b14442639685ac40c805f53f704c25986dd087c25d7bfc7bc6e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-build.txt", "sha256": "df4fa98f1b0956cd53ca8994fa88a6dd5567d0515a9981f62db35ba4e54daa84"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-initial.txt", "sha256": "45797cebe8fac95062bae816e0f19ed5edd35749922e954d5c5a0ec7b5fd2593"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-links-owned-final.txt", "sha256": "80d20527fba46ed686f90209a5d4f206d0cb2a82af9d7bee7672b9a8828b9e69"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-links-repaired.txt", "sha256": "80d20527fba46ed686f90209a5d4f206d0cb2a82af9d7bee7672b9a8828b9e69"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/site-links.txt", "sha256": "1b610b3236c279920b5c5ad4c153d097e326c25d77f8361be650c31bbe3e0712"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5/snippet-prefix-red.txt", "sha256": "b3643a37f981ed1b1f39d9704c99cda25bf447b4cfec33e05a284da7ece21ccb"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5-claude-repair-review.md", "sha256": "ad5a11f3f82174afa0f6efbb5ba5d6ca9f2fe542cf121a55fd455ccfe3efc8a1"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5-claude-review.md", "sha256": "07d2a208420381cde9fd4df080ac48a3a1e3d7cc2b7bd5d32259070fe7aa6cd0"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5-repair-review-prompt.md", "sha256": "6e08f165f00427f91b0e6feebacb8e4e8d036b634f4227d7cf2ca49b35b11194"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5-review-prompt.md", "sha256": "3a7bf8445de55c7b484705e2e5f86009f52857538b731575378399d625015856"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5-spec.md", "sha256": "ebd5505fb995d938919cae4198092eead1701ba154bf0d5fd71109015b412db3"}
  - {"path": "docs/assets/application-diagrams.js", "sha256": "6fea77ac9858e08be1156f09e63ffd502d767357dcae86424f038ae3745ae843"}
  - {"path": "docs/assets/applications/bookrec-eligibility.svg", "sha256": "66a76ca2c6f3bdd2b9c5b0f7a51465a0ef1fe38daac399abd4474ce82115bd79"}
  - {"path": "docs/assets/applications/bookrec-evolution.svg", "sha256": "9354fdfed8e538b1ebc8a9a98ea0c84d11ecd082d5ff34df96cf0af508dc2616"}
  - {"path": "docs/assets/applications/bookrec-flow.svg", "sha256": "cbb4d607b6c96b22684e98b749e11836b7363a44e9d06236ea7a8890055d03fd"}
  - {"path": "docs/assets/applications/bookrec-native-query.txt", "sha256": "0a27b63fda9d2a2160551e36cabb14a79a5bc87bc8ec5b5052ada0a1b25b4ba3"}
  - {"path": "docs/assets/applications/expense-currency.svg", "sha256": "70cc75b5f585af923782dc0c30953a570353d449af65a16f3515709cb2d0a1bf"}
  - {"path": "docs/assets/applications/expense-flow.svg", "sha256": "4654889be5a9726ba9368d8a7acc0632e70f08f807fa9aa601b3104e25a427d5"}
  - {"path": "docs/assets/applications/expense-limits.svg", "sha256": "df4b69c12854c612552df966112d91fd9a72891804da74220682e58653749943"}
  - {"path": "docs/assets/applications/expense-native-query.txt", "sha256": "51393f24d7ad3d1864525a1aa59835c0ef1536abc975becc7ba49414e627fc18"}
  - {"path": "docs/assets/styles.css", "sha256": "e008c90acc02bde97983ec4fc706e887d708009196cd18009346def29cd4e8ed"}
  - {"path": "docs/bookrec/06-evolution.md", "sha256": "30538c18e15688d31ec7567a006777afb9aa3b1f63e88d78553f1e4a09bd67f2"}
  - {"path": "docs/bookrec/07-native.md", "sha256": "91853e9633eb2f2467d4a3bd75909cae6194389bf7dcdb51e8e6e43251f205d0"}
  - {"path": "docs/expense/03-evolution.md", "sha256": "52336aa7521847fa324f150b7b80ecd458ede6af4f644453b0e503556684e271"}
  - {"path": "docs/expense/04-native.md", "sha256": "9aa92aeb9e0335900deb826093370ea023108a33120e8c0e1eda211020ef8923"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/adult-refusal.input.json", "sha256": "9d9f9bd989a34a3ea722c2a33ddddb365bc5dae0bb671b1220e9bae967369e62"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/adult-refusal.json", "sha256": "eb7dad17ed7c34238fac748070c14e5464adb40ef3067b7ac80a01bea8fe0c3e"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/advisory.candidate.json", "sha256": "34a162839ed39ae3bfa0ec9d8037fdebc3a81cadc7ed6e4b330fcf41a754d305"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/advisory.json", "sha256": "167b663325b3fe73317f746cecc20ca4ddf3471da78029bbf9fcba6d1d91ce70"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/already-read-refusal.input.json", "sha256": "75ebd4ea8b0403f783f69c30a260b7e1f0ef8821a24b727a75dc189fc91c778f"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/already-read-refusal.json", "sha256": "2a01d4b18473fd7e94b2ea9f6c73029910340629014d33fb420f1cb42b04b588"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/complete.candidate.json", "sha256": "0d8617807ed9ecf395a0de1a1b2473cf57d356e1e11398a52468a57b80de7a99"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/complete.json", "sha256": "e92da3ea9cb4e32ccc5027ffdc37cd0d7de773002d3d8bf5d7a478dcf7f26a1e"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/omission-refusal.input.json", "sha256": "be5ce520195f10368f7b51bd73a9b852990f4192f7e67b162c807484e2fdb679"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/omission-refusal.json", "sha256": "954dd3f85aa4859fc1e1651609d1fe85b425daa8a1dc41e9d203c38b9ffb00cc"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/preferred.candidate.json", "sha256": "1e6f53d90b15abb43a85c55388df99d35d5e4057d5fd7a38a833ac4227cb3b0c"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/preferred.json", "sha256": "c4621dfc0974bcceccaa23f5914ce4ab86dd72c8d835e9f819add6a4f36019cc"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/checkpoints/strict.json", "sha256": "6528b160f86889f041c90da642d28b0fe3aeb2b45cbd4c6df43d872b2611df24"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/eligibility.svg", "sha256": "66a76ca2c6f3bdd2b9c5b0f7a51465a0ef1fe38daac399abd4474ce82115bd79"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/evolution.svg", "sha256": "9354fdfed8e538b1ebc8a9a98ea0c84d11ecd082d5ff34df96cf0af508dc2616"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/flow.svg", "sha256": "cbb4d607b6c96b22684e98b749e11836b7363a44e9d06236ea7a8890055d03fd"}
  - {"path": "src/gnd/examples/bookrec/tutorial-assets/sources.json", "sha256": "1d5621bb901adfa54b6b6e5ccd4db4276859adc57832204a5735d8cfcaf5e1b1"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/baseline.json", "sha256": "edf70cc6abacf023edb0667a722e95d891472d7b0faa07b389e1fbde59fbd106"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/chain-limit.json", "sha256": "568665f82bc4c6ad511806c7b74c5eb0dcf64cc5999bf13ea957bf5a6145bc85"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/currency-explicit.json", "sha256": "e6343586719e32833dfb4133a8bc127d389c6d5cbd96a1a7d69fbf8d8073dbab"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/currency-missing.json", "sha256": "3374c7aadba325ed07c4c157934ba9f015467d84f4257ae0fb464397fa6fce1e"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/finance.json", "sha256": "20a57d196195eca8d9006b01473fb66a279ac9b7a1da1587d1cffa533bc529fb"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/meal-cap.json", "sha256": "57903e38c567631505bfbf0f069694ad686b4894d7963f52294f13fc0bab7463"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/team-lead.json", "sha256": "4482caae3bf1efa965abb5ad27c22332c0c43cfcb232cece072cfca6abfda1b5"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/usd.input.json", "sha256": "e39648eef481c6912a85addced101e0eb38bbf5d4ea5d05e77700bb707c7a561"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/checkpoints/usd.json", "sha256": "e5d70edbd238d2c6724717e061afa0fef9a05c87c054bedfdae8466e74e46565"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/currency.svg", "sha256": "70cc75b5f585af923782dc0c30953a570353d449af65a16f3515709cb2d0a1bf"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/flow.svg", "sha256": "4654889be5a9726ba9368d8a7acc0632e70f08f807fa9aa601b3104e25a427d5"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/limits.svg", "sha256": "df4b69c12854c612552df966112d91fd9a72891804da74220682e58653749943"}
  - {"path": "src/gnd/examples/expense/tutorial-assets/sources.json", "sha256": "2813ed9462508a92d376d36e4c5b575b6f45a41dbde7f8e06cf885bd4aa6192b"}
  - {"path": "tests/test_documentation_tutorials.py", "sha256": "457cc4ee1f66a23bd238f1fe168838fc9a849de7c85016d7c3159d259cf15432"}
  - {"path": "tests/test_external_runtime_tutorials.py", "sha256": "ea839abc7c9263555334b067b9751ed54578d549f5d22057ec952b3b66b4aa6a"}
  - {"path": "tests/test_pyrel_tutorial_experience.py", "sha256": "ef34046ab3f4ee4b4cfd26c5f31e0bd5402bd22c30e5d81cd4209a17de2ad144"}
  - {"path": "tools/run_tutorials.py", "sha256": "9c1f16d90f33c55678a3725cc50db25f4c3796def561af7050b49f3cb7de18c0"}
  - {"path": "zensical.toml", "sha256": "bf341e884ba5e28267e79fa0c6f17107564577eb423e964518ae0b2629130ff2"}
---

# Claim

PA5 completes both executable learning paths and six source-grounded accessible
SVGs. Actual native runs pass52 BookRec and34 Expense blocks; offline paths pass
50/31 and explicitly skip2/3 native blocks. A local expense model-only50 EUR cap
variant rejects the old60 EUR meal and accepts a45 EUR repair with2245 EUR total,
without rewriting queries. Execution timings do not measure human authoring.

## What shipped and criteria

PA5-C1/C2: existing groups include BookRec07/Expense04. Fresh installed-resource
copies use distinct explicit GND/native interpreters. Native steps assert exact
selected/complete pairs, preserved Ben/night, advisory/strict witnesses, unread
post-proposal failure/repair, counts/totals, approval-chain witness, currency
missing101/102 and USD application guard. Missing/wrong/relative/same-as-base
native paths refuse before execution. Offline omission is explicitly skipped.

PA5-C3: queries/calculation, model policy, independent audit and publication have
separate reader-visible responsibilities. Actual owned query source snippets are
byte-pinned copies, not drifting substitutes. Prior chapters execute generation,
managed evolution and conformance. The50 EUR variant is an isolated teaching
copy with updated provenance, not publication of a shared model. Counts and rule
checking remain separate, no Python policy fallback or actor authority.

PA5-C4–C6: three canonical SVGs per app ship under tutorial-assets with compact
source/checkpoint manifests; docs copies are byte-identical. Six diagrams show
flows, actual reader/book/genre exclusions and complete pairs, advisory/strict
rules, expense amounts/caps/chains and currency evolution. Native PA2 refusal
reports/input bytes and PA3/PA4 final checkpoints are retained and source-bound;
new USD guard is actually measured. Raw model/source bindings and exact candidate/
refused input hashes are verified; visible numeric templates resolve source JSON
paths, including complete EUR-only list. No successful result is invented.

Current render-final captures6x2themesx2viewports,12 mobile right views and8
normal-page navigation views. Desktop1440x1000; mobile390x844. Body never
horizontal-overflows; diagrams intentionally scroll at560px minimum for16/18px
labels. All labels are reachable by touch/keyboard, no intrinsic SVG glyph
clipping. Color is redundant with words/shapes. Fixed SVG text contrast is
12.9 or greater, above4.5. Alt/desc/prose and unique named focus regions provide
accessible equivalents. Cropped graphic capture hides sticky header/floating TOC
only, as disclosed; separate normal-page navigation views retain actual chrome.
Contact/initial captures remain prior evidence, never current acceptance sources.

## Gate output (verbatim)

Frontmatter focused command exits0:

```text
119 passed, 13 deselected in 22.33s
```

Command: .venv/bin/python -m pytest -q tests/test_pyrel_tutorial_experience.py
Exit0 (after accessible-desc-only final asset update):

```text
32 passed in 0.13s
```

Commands: GND_TUTORIAL_PYREL_PYTHON=<absolute pinned native> .venv/bin/python tools/run_tutorials.py --group bookrec|expense --lane pyrel --python <absolute base> --receipt <fresh completion receipt>
Both exit0:

```text
Native lanes executed: pyrel
52 tutorial blocks passed
Native lanes executed: pyrel
34 tutorial blocks passed
```

Offline commands: .venv/bin/python tools/run_tutorials.py --group bookrec|expense --lane offline --receipt <fresh bound receipt>
Exit0: Native lanes not executed: pyrel;50 and31 tutorial blocks passed.
Exact page/code/interpreter/version/group/exit/time/output hashes are in receipts.
Per-probe versions are parsed from actual SDK metadata output, not assigned pins.

Command: uv run --isolated --group docs zensical build --strict
Exit0: No issues found; Build finished in0.45s (see actual retained build stream
for verbatim duration). Command: .venv/bin/python tools/check_docs.py site
Exit0:7426 local links/assets/anchors checked.
Command: .venv/bin/python -m ruff check tools/run_tutorials.py tests/test_pyrel_tutorial_experience.py tests/test_external_runtime_tutorials.py tests/test_documentation_tutorials.py
Exit0: All checks passed!

Timing receipt binds observed completion: BookRec20.031005s total/12.875349s native;
Expense38.643452s total/33.242689s native, including deliberate failures/repairs.
These are shipped-command timings on one machine, excluding installation, human
model design/authoring and review. They support reproducibility, not a claimed
productivity rate. No broad replay or fresh-wheel acceptance is claimed here.

## Review and reproduced dispositions

One reviewer is one reviewer: initial and bounded repair Claude readings retained,
read-only/no Python/native execution, changing-tree limits initial and stable
hashes second. No third reading. Four local close reviews remain later scope.

Initial F1 word/number gluing was observed red and repaired; second M1 found SVG
desc/punctuation gaps, reproduced by stronger SVG controls and fixed in visible
and accessible text. Initial F2/F11 source gaps were reproduced by currency-model,
regenerated wrong cap label and refusal-input mutations. Compact source hashes,
raw bindings/value-level labels/model pins repair them; final expanded-enum
regenerate mutation also red before full EUR-only assertion. F3 adds exact real
witness assertions, not a claimed runtime bug. F4 existing/parentless receipt and
bad container reds precede early validation; atomic no-clobber publication reuses
public safefs with race-writer controls. Group/page/code/interpreter/version
identities bind runs. Failed runs do not publish; prior evidence is preserved.
Source-page changes refuse completed receipt. F5 explicit-native-path red and
actual separate-path test double strengthen selection; same/relative paths have
separate pre-fix red controls. Runtime version/prerequisite mocks reach their
intended branches, not earlier failures. F6 actual scroll0/max202 red led to a
bounded helper; green records120/82/0/202 across all12 region/theme cases.

Final L2's modified keys and desktop no-overflow prevention were reproduced red
in actual cancelable browser events, then fixed/green; normal mobile keys still
work. F7 min560 decision supersedes480 draft; F8 unique regions; F9 genres,
preferences, Ben/read and accurate arrows caption; F10 source-snippet controls
replayed red against bcf9126 while explicitly disclosed as later authorship.
Second M2's stale frames are renamed/segregated as prior; current focused/native/
render evidence follows final owned changes. A final desc-only clarification
changes accessible text, not pixels; current XML/source controls cover it.
Sanitization.json records raw/retained digests and path-only edits in each stream
or JSON header. No user .agents/skills or .playwright-mcp snapshot is committed.
Coverage additions for correct preexisting boundaries are not mislabeled bugs;
owned final fixes have no third reviewer opinion and current gates are explicit.

## Refactoring review

Refactors EXECUTED: one reusable runner receipt interface serves selected/skipped/
failed observations; public safefs supplies atomic fresh publication. Compact
hash/binding manifests replace repeated full-model copies and tie numeric labels
to canonical source paths. One delegated document key helper handles all six
regions, including dynamic site navigation. Canonical SVGs and source snippets
have mechanically pinned docs copies. No policy/runtime/model refactor or new
source-owned handoff. The prior native-query-bootstrap/diagnostics targets remain
future owned work; no premature shared child SDK contract is introduced.

## Standing rules, boundaries and completion

Totality: malformed receipt containers/paths and native selection refuse before
work; trusted Markdown/artifact shapes remain explicit. Bounds: finite trusted
blocks, preflight30s,300/600s block limits, inherited child/work/result caps.
Order: fresh destination and runtime preflight, actual exit/semantic assertions,
source stability, then complete atomic receipt. All-rule walk unchanged in
runtime; model policy has one normative home. Measurement: native witness/number
controls, mutations, key-event reds/greens, current rendered source and timing.

Budgets: runner+74/-12 (under100 additions), tests206/230, chapters164/210<=220,
SVGs about15KiB<100KiB. Exact query/layer changes are absent; immutable framework,
models, corpus and runtime stay inherited from PA2–PA4. No source truth, ranking
quality, actor/reimbursement permission, production transaction, universal ORM
agreement, host sandbox, certificate, merge or site publication is established.

Delegated completion(auto=true): named milestone authority persists; accept PA5
for the final bound sources, finite tutorial outputs and current render/coverage
checks after implementability/review/refactoring/standing-rule sweeps. This is
not the owner's personal reading. Continue PA6 fresh wheel/target-only acceptance,
full137/native comparable denominator and four selected independent local close
reviewers. Existing named residual owners/targets remain live; no new blocker.
