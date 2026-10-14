# Local plan review two

Reviewed 2026-10-13. Independent local reviewer two; publication/acceptance,
security, limits and compatibility scope. No paid calls.

Subject: `.gnd-planning/milestones/pyrel-applications/notes/pyrel-applications-plan.md`

Reviewed SHA-256: `a001e5b87eaf55d4bc6763b918a5ec8f90a9a34d2c6655905cd420ea9f6ea735`

## Verdict

**Accept for the plan gate in this review scope. No actionable plan findings.**
This is advisory review of the draft bytes, not owner acceptance, implementation
approval or a claim that native applications already work. PA0's schema, grammar,
limits and compatibility decisions remain required owner-gated work.

## Evidence and disposition

The whole plan was read, including all phase criteria, risk controls, exclusions,
verification selections and open decisions. The following existing gaps have
explicit plan obligations; they are not defects left unaddressed by the plan:

| Concern | Current seam and observable consequence | Plan disposition |
|---|---|---|
| Audit exit mistaken for acceptance | `src/gnd/export/pyrel_runtime.py:1206` labels zero as report completion; `:1231` returns zero for non-error violated/unsupported verdicts. `tests/test_public_pyrel_export_runtime_optional.py:33` deliberately tests flipped, declined and dropped verdict reports with zero completion exits. An application using that exit as acceptance would publish invalid or incomplete candidates. | Plan `:68` requires preserved legacy exits and a separate explicit acceptance interface; `:122` requires distinct accepted/warning/rejected/incomplete/failure results; `:188` pins unknown/error refusal and legacy exits. PA0 must finalize it before implementation. |
| Candidate publication and refusal preservation | `src/gnd/examples/bookrec/extension/bookrec/cli.py:17` stages the candidate before checking; `:31` checks both exit and acceptance readiness. Expense `src/gnd/examples/expense/extension.py:17` currently uses the GND exit, with staging at `:69` and replacement at `:81`. Reusing a PyRel completion exit here would be incorrect. | Plan `:69`, `:221`, `:225` and `:247` require checking exact staged bytes, input/model binding, injected post-proposal rejection, and preserved input/existing output on refusal. These requirements cover the observable publication risk. |
| Independent checking versus filtered proposal | BookRec `src/gnd/examples/bookrec/extension/bookrec/library.py:8` filters candidates using Python predicates; `:43` calculates derived claims in the proposer. Successful filtered output alone cannot expose a missing checker. | Plan `:65` forbids Python/GND policy fallback in native checks; `:195` requires independent derived computation and supplied-claim comparison; `:221` and `:223` require bad injected candidates and forged/missing derived claims to fail. |
| Local configuration, credentials and budgets | Runtime `src/gnd/export/pyrel_runtime.py:1135` constructs explicit local DuckDB configuration; `:955` bounds document reads and `:932` bounds expanded document work. Query result materialization at `:286` is not by itself a work/time ceiling. `tools/run_tutorials.py:63` inherits most environment variables and `:85` uses a wall timeout with captured output. Current seams alone do not prove the requested bounded, credential-free application execution. | Plan `:70` expressly requires no ambient remote discovery/credentials, input/query/time limits and honest refusal; `:151` selects existing bounded process/filesystem seams; `:170`, `:185` and `:206` require pinned ceilings and budget/work-limit refusal controls. `src/gnd/process.py:34` supplies explicit timeout and stream/aggregate retention limits. PA0 must make these obligations concrete, including the environment boundary. |
| Optional runtime and downstream compatibility | `src/gnd/export/emit.py:31` copies the independent runtime into a standalone artifact. `tutorials/runtimes/pyproject.toml:8` pins PyRel 1.30.1 and DuckDB 1.5.5; `tools/run_tutorials.py:36` explicitly selects/verifies native runtimes. Installing the foreign runtime into the base interpreter or changing report exits would break declared boundaries. | Plan `:70`, `:126`, `:142`, `:190`, and PA6 require optional isolated runtime, retained report clients, byte-gated resource copies, GND-free generated execution and installed target-only evidence. PA-D4 requires compatibility evidence for any upgrade. |
| Currency and authority claims | `src/gnd/examples/expense/currency.orm.json` admits EUR only, with integer amounts and EUR-denominated policy caps. Existing snapshot approval facts are not payment or actor authorization. | Plan `:107`, `:109`, `:245` and `:248` require labeled per-currency totals, independent arithmetic checks, unsupported-currency refusal and explicit snapshot scope. Release/deployment/merge authority is excluded at `:92`. |

Suggested plan fix: none. Do not turn the listed current-code gaps into passes;
retain the plan's required discriminating controls and resolve the named PA0
contract decisions in its spec.

## Scope limits

Static inspection only. No native PyRel execution, product tests, dependency
installation, site rendering, wheel build, credential reads, external API calls
or paid reviewer invocation occurred. Reviewed the relevant exporter/runtime,
BookRec proposer/publisher, expense approval/reporting, complete/currency models,
tutorial runtime/runner and bounded process/filesystem public seam references.
This review does not independently establish current PyRel package/API behavior,
the final admitted grammar, normative equivalence outside the finite corpus,
concurrent filesystem security, or implementation compliance. Those require the
planned gated specs and measured execution. No plan or product code was edited.
