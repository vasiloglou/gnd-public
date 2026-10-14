---
milestone: pyrel-applications
station: phase-PA5R
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PA5R
date: 2026-10-13
source_base: 50eba83
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pyrel_learning_path.py tests/test_tutorial_output_blocks.py tests/test_pyrel_tutorial_experience.py tests/test_pyrel_proposal_check.py tests/test_rf2_pre_move_pins.py tests/test_documentation_tutorials.py -k 'not documented_learning_path or bookrec or expense'"
  exit: 0
  output: "158 passed, 20 deselected in 23.86s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately scoped CI
  reason: selected application/tutorial/runtime/docs consumers; broad exclusions preserved
evidence:
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-desktop-dark-eligibility.jpg", "sha256": "42ee1d5fdf2a35ba41a6cdc7d0d197d4adb3b97712683e97666a68abdbddccc3"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-desktop-dark-rule.jpg", "sha256": "e17b627ba8e904ca5a0be93a1b1d1e318ca1cb48ccc71795655309ee930dcd06"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-desktop-light.jpg", "sha256": "02129d0be98ba872c7b7380dea2dcf961cc7cd6e3e66a57f4a76ad8c300219f3"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-mobile-light.jpg", "sha256": "e82627bd6479187143556ab3867bd3ad7f725dbdc25c068d2065d704a0792210"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-offline-closing-steps.json", "sha256": "7863986ed834237acfb7f6966706268b8009d2dc6cea432c67ac3544a90788f2"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-offline-closing.txt", "sha256": "2a80ccdbf1a6eca592a4541f9f209944e990d3a5bb9fbb719cb8a8d61fc6438e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-offline-final-steps.json", "sha256": "feb74bd455e4149665e786aa23209ad2611662eb3d1dc575b6ab070035d63818"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-offline-final.txt", "sha256": "2a80ccdbf1a6eca592a4541f9f209944e990d3a5bb9fbb719cb8a8d61fc6438e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-offline-steps.json", "sha256": "e46032399c2afcb4fad85338027ccd0886764bd0f5dd9a7dd041605cadf75d6e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-offline.txt", "sha256": "2a80ccdbf1a6eca592a4541f9f209944e990d3a5bb9fbb719cb8a8d61fc6438e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-pyrel-closing-steps.json", "sha256": "b2ff0122bb214870ba1404cc1e9b37076e25eaf0206dfc15af341eb4611cca78"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-pyrel-closing.txt", "sha256": "55962ab445e631b92b21a5228440a565aaa79a14c79e90679bc6bafc52603801"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-pyrel-final-steps.json", "sha256": "1c42024b2fa867eca9b990d75c31531c3b3887c8f1ae207b260ad782089c9b00"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-pyrel-final.txt", "sha256": "55962ab445e631b92b21a5228440a565aaa79a14c79e90679bc6bafc52603801"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-pyrel-steps.json", "sha256": "1cf194ea2be426571d63e92911b74f094e6f2676d93dd1ead572b2e456ddc13b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/bookrec-pyrel.txt", "sha256": "55962ab445e631b92b21a5228440a565aaa79a14c79e90679bc6bafc52603801"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/check-docs-closing.txt", "sha256": "5443c27f536e23884aa08f3e756c2b7c18b5cd138eaf00b7181874cda35ded3b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/check-docs-final.txt", "sha256": "5443c27f536e23884aa08f3e756c2b7c18b5cd138eaf00b7181874cda35ded3b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/check-docs.txt", "sha256": "d95775044275b34c168b2bded49131dd85af3dab63c34a6a126f52dce76d01ca"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/claude-repair-review-raw.md", "sha256": "e9f9f3cf900dc03bd0538aafd8768676551ee41662a07ad8c0f829e12afb0f98"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/claude-repair-review-stderr.txt", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/claude-review-raw.md", "sha256": "005ed291aac62cf362cb395b244bbde744466682f13de4e933c7fc693a91362b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/claude-review-stderr.txt", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-desktop-light-limits.jpg", "sha256": "d94cf6ebaaace15a2d8e22dc69f6a6526541e372ae83b35bfb719b5e2b7c89b6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-mobile-dark-table.jpg", "sha256": "d2911707b59577817b90c998ef403a3b9033829ab305b23465a2cfaa8d1716a8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-mobile-dark-top.jpg", "sha256": "cfc02f4c51dbc24ebfac002a07bcb7397945fbddfcf7385d26d90d7a3df6b4f9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-mobile-dark-troubleshooting.jpg", "sha256": "3cb4df5d1e2f535dbdb61ba439c01ef1c9ea3ae94352ee118346e1ec8e17713a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-offline-closing-steps.json", "sha256": "dfe1f666d08f28ae36e7b6251a24ca361c2c7628e249b5693be8d6056a5df38c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-offline-closing.txt", "sha256": "e4c3d0034e99a60fd4e88dc79155a22c6fd3e4426b3139db0b9c0ce587f6bb56"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-offline-final-steps.json", "sha256": "b6ce365986cef316b6121654e2906a7349bb2f8b248329acc5a7958f4a7011d7"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-offline-final.txt", "sha256": "e4c3d0034e99a60fd4e88dc79155a22c6fd3e4426b3139db0b9c0ce587f6bb56"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-offline-steps.json", "sha256": "8b5c0617bfdd612f8c9e8cb8304c03c7427c0d3db74a2471b441be2f54362ca0"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-offline.txt", "sha256": "8777f275f35ee38880d5e4fe48ef3b0f3499b304c70057ba82770a7561ec0382"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-pyrel-closing-steps.json", "sha256": "decd3afb7b499607cf197d1c877f855c95d4f16238154ed851c1db374edcacc1"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-pyrel-closing.txt", "sha256": "586bbb18652195419d6f63f0ebc33927746f353b03fa52420a7062aa8c743cb9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-pyrel-final-steps.json", "sha256": "b5138befd93be2627f2ab89494757d1c07666bbb3dfa7ff830111299c3e7d54b"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-pyrel-final.txt", "sha256": "586bbb18652195419d6f63f0ebc33927746f353b03fa52420a7062aa8c743cb9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-pyrel-steps.json", "sha256": "a10c7b51095ae75c42893373babe5f25e6e60c5a108c7c13f0a40ba09b84b9e7"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/expense-pyrel.txt", "sha256": "25e75e848f98e950f450f908cbf6e523d0d90150d13d35c55c58d9ae12c18f04"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/bookrec-desktop-dark.jpg", "sha256": "5a1b339acaa6867ad5e8e64e298af9751c1a58de2733f8a0efdbaaf71468e589"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/bookrec-desktop-light.jpg", "sha256": "e5e7d3b5ff65a4b8b1ab1bac075cc69c1ae38664ef5c8bc527fe90cceae8de7f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/bookrec-mobile-dark.jpg", "sha256": "b5e58da76746f44eebddcbca4164de357efdb5a1a7d75a36d553c49e3286b418"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/bookrec-mobile-light.jpg", "sha256": "4e59651023167a19bbe13a8971aeafe7fe459e0c2c9e01ea89f592f0400ba85e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/expense-desktop-dark.jpg", "sha256": "5c210b5ae7cfe30a2dbc605f4592a49230c95f815a09385a8807ca5c0db3e951"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/expense-desktop-light.jpg", "sha256": "71fcf16ec7650904c8ad572358902979e3229c9703bbab33b3fc419d0b0dc59f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/expense-mobile-dark.jpg", "sha256": "10ba7ce3a784127f46a5865bbf1ac7e06b90fa7ea593aa2f53efb0d4a437b795"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/expense-mobile-light.jpg", "sha256": "6b6c0fe47a6a5e0b6df4d5e960311e3892434b03215907fdd2cafd729893f983"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/overview-desktop-dark.jpg", "sha256": "94a60de431e23448781ba66a00edb12fd63a67c3d73bb844fdd27baaa04e3d36"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/overview-desktop-light.jpg", "sha256": "db1633c313bcf34e090448743f1115f484cf2f6e911d7f74e1fb2f46171df463"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/overview-mobile-dark.jpg", "sha256": "65c1d85f930e544c37e5779cb53941ec7779766b47723a2403ec41049c282573"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/final-views/overview-mobile-light.jpg", "sha256": "31b618a13f639b7a33294713d9064e54d312ef29ee374fd7aee68a940dd579ba"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/focused-default-closing.txt", "sha256": "d6fb456ba8005dad0e768dc49d2d322cff3ab6c76ada407dac7a3c1773f5ffb9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/focused-default-final.txt", "sha256": "24fe7e2509e361700cd912ebb3c762b05060687e975b6fece451fa9c0e03b34a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/focused-default.txt", "sha256": "42851efb61941ca2c97ef9e68f2096aa4228ba1b3e3cda770b3a7ffb79e8dc5f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/focused-pyrel-closing.txt", "sha256": "34e2464aa2476bea65391fab34cc80235c09aa42d2c2bc1ed4bffbdb02d62404"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/focused-pyrel-final.txt", "sha256": "c6a099cb558983ccfb53cb5628190e0b53d3e37483b065e13db4b745157add72"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/focused-pyrel.txt", "sha256": "9a31918f91a0f16c9d72bd5ba895601bb9ff17530920b78e320e4a34e817fb50"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/gate.txt", "sha256": "598eb09206130ec3cde200c0cb362827c4422d9d31d38fa851fe7c0bed8833bb"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/learning-path-red.txt", "sha256": "c1ac2f8ec8deb155cc63aab76c939b26feb4c976433b9faa7bcd35d2cc85f8a6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/lint-closing.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/lint-final.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/output-blocks-red.txt", "sha256": "b4d9e7dde5bf4234b1b8cd7049db22418cb52507e2f89f30c01472581f5f8083"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/overview-desktop-dark.jpg", "sha256": "a5ad8ef0fe9fdf510f49d0d20c2d9ce241d45dbf6a73866fb73710cc6fa812a8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/overview-mobile-light.jpg", "sha256": "0fdb4771f34b4e11fd13f74f1ed42c2f75d3d8d001cc7cc7dc4e772cce89e710"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/preexisting-failures-head-transcript.txt", "sha256": "9daa66bdb8d40baff0213f4e57e9f68edda95fa32e5d11f9170fab63f2095d87"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/preexisting-failures.txt", "sha256": "806f0c8a4957cd35da31eab8316f1b4fd4dbcf1490acfcb726dbfb53d8a06466"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/proposal-red.txt", "sha256": "1a0a5094d442fd0e82c69bf01e0f72dfdd518e37b0ed5d151ff5e17a9d313ce5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/pyrel-successor.json", "sha256": "e8f81f848e44c7ba6a503587f511b20374fce6b2db682a8683eb77f3b711c482"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/repair-red.txt", "sha256": "450901508794f0f91f420d785b1adcf8745b0aa00d08448df0eba548c29ad138"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/rf7-all-offenders.txt", "sha256": "b19096262255aaac42d5dcba6aa12c1cbaaaee5ac8533227ae7d58e2b584fa49"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/seam-red.txt", "sha256": "b187355d9d80ed916113b380880c172e53f8a893ad0e4bdae869387e0fb631ba"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/selection.txt", "sha256": "ebe823101a6f3a09db0bf965ad725754156a82ab43b86cfdc88c71adf803af6a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/site-build-closing.txt", "sha256": "113cd0823d385bd29c0e6a7b9a628bd86d36261972aaf7da3105466cb7ba79bd"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/site-build-final.txt", "sha256": "113cd0823d385bd29c0e6a7b9a628bd86d36261972aaf7da3105466cb7ba79bd"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA5R/site-build.txt", "sha256": "3376cb89c7888a79d6f5f6b9de0622577f2b03b31423e50d1380cb5b5da3e011"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5R-spec.md", "sha256": "124f6107d016edda3608839f8903ad1811c8d250e109c583b7a51453ee10e894"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5R-review-prompt.md", "sha256": "f09b32025c8242a2fff918681298057895dad4fffba64df3bcd065559205cca8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5R-claude-review.md", "sha256": "19bd2a82eefa91b620568d3e766087346530eff7cb88ae71398057c9ecd9e3d4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5R-repair-review-prompt.md", "sha256": "11df9f595fb316804bff1ffc3f6b5b9d0c4e58c47c685e0a0c6581d1f5240758"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA5R-claude-repair-review.md", "sha256": "b1c94c294964220d580be6d8a2427c9c3c8ca359fa5bf815843f9b2faa6084e7"}
---
# PA5R -- Junior-first PyRel learning path, public query seam, honest claims

Amendment A2 (010) phase. Spec notes/phase-PA5R-spec.md, delegated approval
(auto=true) at spec SHA-256 f20de63e363394a703b9296a5247d0213ccf45d2a06ee63daaf53119d21fa7bf,
with recorded findings F1-F11, triage and repair dispositions appended after it.

## What changed

- D0: Snowflake execution claims removed from README.md, docs/index.md (two
  places), docs/tour.md, docs/agents/export-and-review.md, docs/agents/index.md.
- D1: public seam NativeApp/open_app/run_app in src/gnd/export/pyrel_runtime.py;
  both native_query.py files use only it plus relationalai. Twelve checkpoint
  comparisons are identical before and after (F1).
- D6: check_proposal and the BookRec `check --proposal` command check a supplied
  candidate with the generated PyRel checker; the checker stage is one shared
  helper. format_result and `--format text` give a short summary.
- D3: runner output= blocks with normalization and ellipsis; receipts decide
  status after both checks.
- D4/D5: docs/pyrel-apps.md (pitch, setup, query toolkit, next steps) and rewritten
  docs/bookrec/07-native.md and docs/expense/04-native.md.
- D7: tests/test_pyrel_learning_path.py readability and claim gate.

## Gates (verbatim, final tree)

- Frontmatter gate: exit 0, "158 passed, 20 deselected in 23.86s".
- Learning paths, tools/run_tutorials.py with explicit base and native interpreters:
  bookrec pyrel exit 0 "59 tutorial blocks passed"; expense pyrel exit 0
  "45 tutorial blocks passed"; bookrec offline exit 0 "51 tutorial blocks passed";
  expense offline exit 0 "35 tutorial blocks passed" (native lanes reported skipped).
- Focused default selection (evidence/PA5R/selection.txt): exit 1,
  "1 failed, 650 passed, 95 deselected"; the one failure is pre-existing (below).
- Focused pyrel_oracle selection: exit 0, "75 passed, 202 deselected".
- uv run --group docs zensical build --strict: exit 0. tools/check_docs.py site:
  exit 0, "7561 local links/assets/anchors checked". ruff on touched files: exit 0.
- Rendered review: 3 pages x desktop/mobile x light/dark (evidence/PA5R/final-views).

## Reviews

One Claude Code initial review and one bounded repair review; one reviewer is
one reviewer. Initial: five blocking findings, all reproduced and repaired with
red-first regression tests (evidence/PA5R/repair-red.txt). Repair reading: code
repairs hold, no new blocking defect; its evidence and record-accuracy findings
were corrected without a third reading.

## Refactoring review

Refactors EXECUTED: the checker stage of execute_application was factored into
_check_and_publish, shared by check_proposal, behavior-preserving under the
twelve checkpoint identity tests and the existing driver/acceptance/publication
suites. Deferred, as open questions: shared PyRel-backend CLI plumbing between the
two example CLIs; the rf7 routing test stops at its first offender.

## Boundary

PyRel 1.30.1 with DuckDB 1.5.5, local only. No Snowflake execution, LLM agent,
model/corpus/answer change, checker-semantics change, release, merge or
certification. A passing check means the supplied facts satisfy the modeled rules.
PA6's committed install harness still pins the PA5 shape and is expected red until
its new spec gate (A2 sequence).

## Open questions

| Question | Owner / target |
|---|---|
| B3 ruling: the Expense meal-cap exercise edits a JSON path in a private copy, overriding an A2 D2 sentence; a shipped one-operation evolve proposal remains possible | Owner, milestone close |
| Pre-existing: tests/test_rf7_structure.py routing failure (pyrel_runtime.py:1524, :1612) | Milestone close |
| Pre-existing: native vs oracle ring disagreement, rel_reflexive (tests/test_pyrel_constraint_oracle.py) | Milestone close |
| PA6 re-gate: constants (7,52,2)/(4,34,3), page paths, resource inventory, prerequisite | PA6 new spec gate |
| Shared CLI plumbing; rf7 first-offender stop | Later refactoring milestone |
| Expense candidate-byte identity (no shipped candidate files) | Milestone close |

## Refuted premises

- "The meal-cap change can use gnd evolve cheaply" -- supported, but needs a new
  proposal builder, roster and preview/apply (D2-a, B3 ruling).
- "Refusing text blocks after unchecked commands is safe" -- refuted by two
  existing agent pages (H6 declined).
- "Reviewer-ready evidence was final" -- refuted by the repair reading;
  closing transcripts regenerated.

## Addendum: local CI of the base commit (owner request, 2026-10-13)

Both workflows (.github/workflows/development.yml, docs.yml) were mirrored on a
clean worktree at 50eba83, macOS / Python 3.13 entry (evidence/PA5R/local-ci-50eba83.log):
sync, candidate build, gnd install, gnd doctor, collection, platform-sensitive tests,
all tutorials (157 blocks), strict site build and links pass. Full suite: exit 1,
"6 failed, 14376 passed, 479 deselected". The installed step first errored only on
uv's out-dir .gitignore files, which actions/upload-artifact drops by default; with
them removed it passes "10 passed" (local-ci-50eba83-installed-rerun.log).

The six failures exist before PA5R and would fail real CI on this branch:

| Failure | Cause | Owner / target |
|---|---|---|
| test_doctor_uninstall (3) | 00efef2 added process-milestone/start-milestone skill directories (branch only) without updating the pinned discovery-root entries | Milestone close |
| test_rf7_structure routing | pyrel_runtime.py:1524, :1612 json.loads (PA phases) | Milestone close |
| test_rf9_repairs query policy (2) | eight unauthenticated PA-phase attribute rows; PA5R swaps one (removes the Expense query row, adds NativeApp.has), count unchanged (rf9-rows-*.txt) | Milestone close |

## Superseded bindings (2026-10-13)

012-ci-repair.md changed evidence/PA5R/pyrel-successor.json after this record (its
hash above is the pre-repair bytes) and added PA5R query successor files this record
does not bind. See 012's addendum. The open-question row "PA6 re-gate"
is closed by c0039e4 and run E (013).
