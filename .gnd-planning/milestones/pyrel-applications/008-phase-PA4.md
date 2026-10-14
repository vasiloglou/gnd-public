---
milestone: pyrel-applications
station: phase-PA4
skill: "n/a -- repository development, not a gnd-solve station"
scope: phase-PA4
date: 2026-10-13
source_base: b4bbf4f
gate:
  command: ".venv/bin/python -m pytest -q tests/test_pyrel_application_guards.py tests/test_pyrel_application_publication.py tests/test_expense_tutorial.py tests/test_bookrec_tutorial.py tests/test_pyrel_application_acceptance.py tests/test_pyrel_application_derivations.py tests/test_pyrel_application_driver.py tests/test_pyrel_application_corpus.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf2_pre_move_pins.py -k 'not measure'"
  exit: 0
  output: "365 passed, 10 deselected in 23.40s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately scoped CI
  reason: affected application/export/docs/layer controls selected; broad exclusions preserved
evidence:
  - {"path": "src/gnd/export/applications.py", "sha256": "64b564236978fb0c369464c483ab93193e5d912d20121990f8105e30430098fc"}
  - {"path": "src/gnd/examples/expense/extension.py", "sha256": "1a6ed43cb676ad77cac6a14820b193e7083eea5aa8a2f65fcbe0a99d4c309eb2"}
  - {"path": "src/gnd/examples/expense/native_query.py", "sha256": "51393f24d7ad3d1864525a1aa59835c0ef1536abc975becc7ba49414e627fc18"}
  - {"path": "src/gnd/examples/expense/README.md", "sha256": "56961b3cdcdf8db10601d03b9acd20136e1441d8268875f2c6ee8181c31e3545"}
  - {"path": "src/gnd/examples/expense/architecture.contract.yaml", "sha256": "cee7c9589a00d6fe6d7ba11df29b48e5b8e5fb6fd0bcb3052c860a2b3a379045"}
  - {"path": "src/gnd/examples/expense/currency.architecture.contract.yaml", "sha256": "c7dae2f6b212f2d7dd0927237bb32a118206a04655c81d01786024d0ebb5867a"}
  - {"path": "tests/test_expense_pyrel_application.py", "sha256": "82978bd2db4a6b53bc270509031a47d602ae637a30d38260670f9d8f8ce71011"}
  - {"path": "tests/test_pyrel_application_guards.py", "sha256": "9d98e8e1fe64f47f42f8f6e3a37a872313d810a2d4a8d416f3afdb49c812fd34"}
  - {"path": "tests/support/pyrel_application_successors.py", "sha256": "9d2226efc90a354c335cc865f71f948bba89dad4213eb8d870babd6d67bfa244"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/aggregate-feasibility.py", "sha256": "9505871064f2f57b6ca94eb19d732d7125db3820b532cd50dcf275defdd88142"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/aggregate-feasibility.txt", "sha256": "4e876522d0c33bfb6436b28b687f59239b1df5c47fa26b9294eef7b0f7c74bbe"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/approval-output-red.txt", "sha256": "a691f669439bd6d42c35669586a759f4206dd5d8377d93e77e1cd421d7293867"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/bookrec-native-regression.txt", "sha256": "da0af8c9ffb61c83be2493dcdbd6fc87256d9da5e50387b092644d8a1bc0df1f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/capture-figure-source.py", "sha256": "a7492ba1b337139c22a271e69c924f22206c2f163feeed29a407fd9d315b6717"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/capture-final-figure-source.py", "sha256": "69b3d04aa4287445750d695b343145f38ca062b30695e2744d4fe065d7183a63"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/completion-bindings.txt", "sha256": "c25ff63dd0c16d79c0a38174c3ff390a3f5f166b5110dea319a50816fde8f291"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/completion-command.json", "sha256": "64b1d85739b0ceb6db3fdd398d0a5e8f33faabad839cd74f703de460811b91ff"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/completion-focused.txt", "sha256": "c5f3b8e9111c1204bf63f4d810dba254b60df8f61871dc76656f013f3ff880aa"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/completion-lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/contract-default-green.txt", "sha256": "a797b2d66be1d3489359b41b4c74e1ee7f965a93cc8f9504b5d9bd92a1bc3c39"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/currency-measured.txt", "sha256": "37a0d731f202f6cca71f6fe42fb04f6dae4a12fde0d0392f9f28f062cc3471cc"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/dynamic-query-successor.json", "sha256": "352cea9d83c324a37ddd66673ee9b60269a2648e2f3514e74aac4793172dd6e5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/baseline.population.json", "sha256": "abd190e872e1acf0524ce94557ae7f10233154dec33d5814c3fb9180f85d1be5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/baseline.report.json", "sha256": "10cec9d6e4076a25fc00992f71b58e374b52a410cf762afb44cbaa9e9cdaea1f"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/chain-limit.report.json", "sha256": "49ab7ca1bed0042e00adeea2c89d9f55cab91b9ee560ae07243349eb5703c2cb"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/currency-explicit.population.json", "sha256": "84608300d0a2aabeb25596ab42ac22f8810343e04e2463caa8e77d8ce643f174"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/currency-explicit.report.json", "sha256": "3a297287c4992a706ad55f54dab88646fa6627984c92814fad7e33ca5c01189a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/currency-missing.report.json", "sha256": "187dc246b54ba1f8e770a70442441fff9d023b23e605e96545b68bbf371f0aa4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/finance.population.json", "sha256": "8d966310b97fcf7c42acfa71b91f857bfc05e4f81ca9fb6219fcc97aeab695b6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/finance.report.json", "sha256": "7cab1130cae4eaabceb10ffc6a02ab8c03491b37d126196278601a00572016e8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/meal-cap.report.json", "sha256": "96564eecd0d489f35fbcbbcb62874afb4630a9257f77ae53e925f0945d91efb6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/team-lead.population.json", "sha256": "43b6e477b1c9da59587ae3bc264b8cc9f60330412e9cdd3e553f48714611d3fa"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source/team-lead.report.json", "sha256": "774f662877069405389b04d8b13e78cd654bf68e05136099eac147a4542ca036"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/baseline.population.json", "sha256": "abd190e872e1acf0524ce94557ae7f10233154dec33d5814c3fb9180f85d1be5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/baseline.report.json", "sha256": "edf70cc6abacf023edb0667a722e95d891472d7b0faa07b389e1fbde59fbd106"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/chain-limit.report.json", "sha256": "568665f82bc4c6ad511806c7b74c5eb0dcf64cc5999bf13ea957bf5a6145bc85"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/currency-explicit.population.json", "sha256": "84608300d0a2aabeb25596ab42ac22f8810343e04e2463caa8e77d8ce643f174"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/currency-explicit.report.json", "sha256": "e6343586719e32833dfb4133a8bc127d389c6d5cbd96a1a7d69fbf8d8073dbab"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/currency-missing.report.json", "sha256": "3374c7aadba325ed07c4c157934ba9f015467d84f4257ae0fb464397fa6fce1e"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/finance.population.json", "sha256": "8d966310b97fcf7c42acfa71b91f857bfc05e4f81ca9fb6219fcc97aeab695b6"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/finance.report.json", "sha256": "20a57d196195eca8d9006b01473fb66a279ac9b7a1da1587d1cffa533bc529fb"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/meal-cap.report.json", "sha256": "57903e38c567631505bfbf0f069694ad686b4894d7963f52294f13fc0bab7463"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/team-lead.population.json", "sha256": "43b6e477b1c9da59587ae3bc264b8cc9f60330412e9cdd3e553f48714611d3fa"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final/team-lead.report.json", "sha256": "4482caae3bf1efa965abb5ad27c22332c0c43cfcb232cece072cfca6abfda1b5"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-final.txt", "sha256": "9fc4dd19ba5945c68376b9a6135c3d62ade5776d1b584c02a56c0d5aa862ae1c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source-initial.json", "sha256": "c6d6f717e4edaf44508eb9523a625e958f43c18d7b5de1f845d36cf5744601a9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source.json", "sha256": "5d0368567b064421a7678f92e04d8495e2c227de127878cef4e425eac24bfdb7"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/figure-source.txt", "sha256": "9fc4dd19ba5945c68376b9a6135c3d62ade5776d1b584c02a56c0d5aa862ae1c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/focused-initial.txt", "sha256": "22b0da103a413fbf515648b6b637d97054eb890280911c3a51817e3b0a92ac8c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/focused-measured.txt", "sha256": "d68bb45c439abf4b59c718745948f1c1d7ef413ede2bb6be5c5235ddba60d9ca"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/focused-repaired.txt", "sha256": "54ff2276ea7d2d701c70fdc4fdf16bc1b54237d98f85ecd72a3493312bd52859"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/framework-inheritance.json", "sha256": "6b7b3b4ee2387b04eecf3b9a7a5109b862b83999e37cd690f2905c679f8576c4"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/guard-coverage.txt", "sha256": "d1b49b4e145b440820b1067e499d65d1ec1b66f0397e579dace0ae4a69ba20d8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/guard-red.txt", "sha256": "8c59954ec3a043f48e0fa4ba2f70965f2361255ebd886fe60ca07293accd1eab"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/lint-initial.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/lint-repaired.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/native-initial.txt", "sha256": "c942728c37276e9405ab052c8abf82d9cfe664ee6d3fc56748e2e6ecd06d8d37"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/native-measured.txt", "sha256": "94454464511e76a33accfc511d6e1568b99782f095395ff892ac88aa71521b79"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/native-red-expanded.txt", "sha256": "4b657ac8290042c50cef522d767d98b8da7852d44d712ad29cf53745c6ec5ce8"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/native-red.txt", "sha256": "42d026e5978ab471e623cdf50c23817501e471fa9a63e1a9ef0b920fab90d0f9"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/native-repaired.txt", "sha256": "fa9f844d4719cab3b6aea10fe244cfbd2c2d342a1be23a41703f745827dcc0e1"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/parent-figure-initial.py", "sha256": "7ebe05dcf70f6e4229497b3507b8ba6b214aaa74a245fc2337177aa2a1950ad0"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/parent-initial.txt", "sha256": "6d7268a20923eeaf4c0d148939367d53303df6088d942dd6a5e16a08d89c39ec"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/pyrel-successor.json", "sha256": "9b7730b4763dd9eec00fd2d10032c8f047a6f5610fe77cbb2814288a294af34a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/query-figure-initial.py", "sha256": "51393f24d7ad3d1864525a1aa59835c0ef1536abc975becc7ba49414e627fc18"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/query-successor.json", "sha256": "e2e7faaf407633e27a543c390489038ef5a123e8bb564740eee1fccbef0d1612"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/readme-table-green.txt", "sha256": "87ac2f20f44d40c8610ae26676d7898f0590b6b03f07583d5da1fffaae4a3075"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/readme-table-red.txt", "sha256": "70af695db39747206ea751d1e1ac1447308ea78d740432ed805fc5f31f07a59a"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/review-native-green.txt", "sha256": "83fe6c1f55b01e9b484d11bb22eb526d77706c1159763ae8023b461dead56934"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/review-parent-green.txt", "sha256": "7ddfd4eb396abd05e1b2ecbaf8865f83644395058d2ac8e7f71ccba973d2deda"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/review-policy-measured.txt", "sha256": "1145d58df7d69ae3a90a19ce56f3f3c4c9005e94356a9d75a50ba1d69870f068"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/evidence/PA4/source-binding-red.txt", "sha256": "cfba63cb1ea8e51190f9494df1f53b1eb48c0060904d1cdf3bbb182c9b7d0f91"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA4-claude-repair-review.md", "sha256": "04360bd527f90eefcbd01583130d7e9aeaa59991cfceaa234aceeb7d1ca4c8f2"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA4-claude-review.md", "sha256": "426d67511c2951961f741a777ad62bf18f2b11eb119906b8a6a57c4720cebd57"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA4-repair-review-prompt.md", "sha256": "d224ae17d613d4c9a89d1f298b81549071c4303841c3b7b3c270ec4f8031f71c"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA4-review-prompt.md", "sha256": "ec108999c45cb3496abb183fbc023c3f37194fea11d7230a5a167d6243fcd011"}
  - {"path": ".gnd-planning/milestones/pyrel-applications/notes/phase-PA4-spec.md", "sha256": "27678193f8e2ddaea46dc4025795e08e467eb28b00736a0953dfdd342139f9e7"}
---

# Claim

PA4 completes native expense reporting and approval candidates using the shared
BookRec export/check/publication path. Query-specific code is103 lines and the
CLI grows25 lines, demonstrating reuse rather than a second compiler or checker.
This is a shipped-code footprint, not a measured human authoring-time claim.

## What shipped and criteria

PA4-C1: native distinct submitted/approved counts and identity-bearing sum give
3 submissions,1 approval and2260 EUR; three distinct expenses of60 give180 EUR.
Native empty aggregate rows are displayed as mathematical0, never counted or
summed in Python. Zero approvals and wholly empty populations retain the inherited
vacuous/incomplete2 policy disposition, so the CLI withholds accepted arithmetic.

PA4-C2: optional --backend pyrel and explicit --pyrel-python preserve the default
GND path. Native enumeration plus Python result-presence orchestration checks
unknown/already-approved expenses. Valid101/team-lead and102/finance produce
checked static candidates. Approval owns only approval/chain facts. Separate
model policy enforces category limits, chain ceilings, enums, positive amounts,
submitter requirements and uniqueness. Named post-proposal faults reach the
checker and repairs recheck; guard filtering is not credited as policy coverage.

PA4-C3: baseline implicit EUR and evolved explicit EUR both total2260. One missing
currency and shipped missing101/102 yield required_expense_has_currency witnesses.
USD source facts trigger a separately labeled EUR-only application guard; a
separate library caller that owns currency exercises supported_currency through
a post-proposal USD edit. The ordinary CLI has no currency-edit feature. Expanding
the model enum alone does not implement multicurrency totals, limits or conversion.

PA4-C4: shared parent validates bounded declared guard kinds and exact, mutually
exclusive source-bound refusal envelopes. A valid guard artifact from exit0 is
nonaccepted1; a process crash1, even with leftover refusal bytes, remains70.
Default BookRec permits no guard kind. Results add raw model/input SHA binding;
independent policy remains bound to captured candidate bytes. CLI drops internal
pre-approval calculation; accepted report exposes only checked arithmetic and
published=false after its private snapshot is removed. Source preservation,
process limits and fresh no-clobber publication remain in the single PA3 parent.

PA4-C5: seven actual native figure checkpoints bind source/model/input/candidate/
report/runtime/query/parent bytes and EUR units. Initial receipts and matching
source snapshots remain immutable predecessors; figure-source.json is the final
measured successor. PA5 owes the rendered graphics, not this record.

## Gate output (verbatim)

The frontmatter command exits0 with:

```text
365 passed, 10 deselected in 23.40s
```

Command: .venv/bin/python -m pytest -q -m pyrel_oracle tests/test_expense_pyrel_application.py
Exit0:

```text
29 passed in 107.20s (0:01:47)
```

Command: .venv/bin/python -m pytest -q -m pyrel_oracle tests/test_bookrec_pyrel_application.py
Exit0:

```text
24 passed in 52.62s
```

Command: .venv/bin/python -m ruff check src/gnd/export/applications.py src/gnd/examples/expense/extension.py src/gnd/examples/expense/native_query.py tests/test_expense_pyrel_application.py tests/test_pyrel_application_guards.py tests/support/pyrel_application_successors.py
Exit0: All checks passed!

Command: .venv/bin/python .gnd-planning/milestones/pyrel-applications/evidence/PA4/capture-final-figure-source.py
Exit0: seven native figure-source checkpoints measured.
Completion-bindings.txt retains verified current source/result and inherited
framework hashes. The unchanged PA2 runtime/matrix/137-case native receipt is
inherited, not rerun here. Direct query accesses362<=365, original307<=310;
exact successors retain immutable PA3 predecessors. Layer allowance count0.

## Review and reproduced dispositions

One reviewer is one reviewer: one initial Claude Code reading and one bounded
repair reading, retained with reading limits and sanitization disclosure. Initial
review disclosed an accidental no-op Python invocation, no native/project run;
repair used only read/search/git and no Python. No third review is claimed.

F1/F6 coverage gaps were located and added with exact rule/witness controls,
including missing submitter101 while approving102, duplicate approval,
nonpositive amount, shipped missing currency and declared guard failure shapes.
These test correct existing boundaries and are not claimed as pre-fix defects.
Currency-edit requires explicitly extended ownership in the separate test caller;
otherwise source preservation rejects3 before policy. F2's literal EUR guard is
retained as an application feature boundary; overbroad successor prose was
corrected at its original site and the scope decision is in the spec. F7 native
membership enumeration and Python orchestration are disclosed rather than
claimed as an all-native presence predicate.

F3 refuted the expected hard1 on completely empty covered currency. First run
20/22 passed; the unchanged runtime refuses2 with vacuous/incomplete rather than
native mandatory1. Ordinary ORM mandatory interpretation would diagnose missing
currency; this conservative bounded residual has a named future owner/target.
Single-row and shipped partial omissions prove actual mandatory witnesses. No
framework or frozen answer changed and no success is manufactured.

F4/F5 were actually red before repairs: approval exposed source pre-approval
calculation; root lacked raw input binding. Repairs remove CLI calculation and
return exact capture hashes. F8 retained streams remove only operator paths with
headers/digests where altered. F9 SDK ValueError/operational diagnostic refinement
remains the PA3 future diagnostics item, with no accepted failure path.
Repair R1 README rows were located outside the table and reproduced in a before/
after structural receipt, then moved back before prose. No runtime code changed
after the final29-case run; final documentation relocation is owned, no third
review. Reviewer did not verify digests or run tests; producer completion checks
supply those observations. Original22 native and9 guard corpus cases were red
before production (interface absence); later controls are explicitly identified
as expansion or actual pre-fix red fixes rather than that original corpus.

## Refactoring review

Refactors EXECUTED: both applications reuse the one export parent for capture,
source fidelity, bounded children, independent acceptance and atomic publication.
Generic bound guard artifacts extend that seam without expense predicates in the
parent. The source-query access is counted, the existing export home remains
mapped, shims/historical evidence stay unchanged. A shared native query bootstrap
would remove roughly30 repeated setup/result-guard lines across both owned
queries; defer under native-query-bootstrap, owner GND application maintainers,
to avoid a premature child-runtime/public package contract in this milestone.

## Standing rules and boundaries

Totality: strict artifact schemas and declaration shapes, negative guard kinds,
reason bounds and crash leftovers; arbitrary query/interpreter code remains
trusted local code. Algorithmic bounds: inherited1MiB input,100k work,10k rows,
60s bounded children and stream limits. Validation order: declared guard options,
source capture/admission, native proposal, source fidelity, exact independent
check, source stability, fresh publication. Complete traversal: one unchanged
framework walk includes every rule/head. Normative home: model policy remains
model/runtime; EUR-only application support is explicitly distinct. Measurement:
actual numeric duplicates, empty observations, named faults/repairs and source
bindings, rather than implementation self-agreement.

No actor permission, reimbursement, concurrent ledger transaction, currency
conversion, source truth, host sandbox, certificate, merge or remote release is
established. Report arithmetic and rejected library calculation are separate
from accepted CLI output. Budgets parent245/600, query103+25/300, tests318/400.
Source models/corpus/locks/runtime are unchanged. Detached host processes remain
outside PA3 process-group isolation; conservative joins may refuse small-shaped
inputs. No broad historic replay or new model/API assurance claim.

## Open questions and delegated completion

Inherited legacy/entity-concept maintenance, native-query-budget-optimization
and native-application-diagnostics retain GND maintainers/application maintainers
as recorded owners. New native-empty-mandatory-semantics is owned by GND
maintainers; native-expense-multicurrency and native-query-bootstrap by GND
application maintainers. All are named future targets with conservative behavior
and no blocked acceptance predicate within this finite EUR/static scope.
PA5 owns six accessible source-grounded graphics and timed executed learning
paths; PA6 owns fresh wheel/target-only acceptance and full finite agreement.

Delegated completion (auto=true): named milestone delegation persists. Accept
PA4 for the specification's bounded decisions and final evidence digests, after
implementability/branch/impact/review/refactoring sweeps. This is delegated
acceptance, not a claim of the owner's personal reading. Continue PA5; merge,
release and certification remain separately authorized actions.
