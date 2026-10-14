# Plan review three

Reviewer seat: test/corpus validity, dependency order, install/native isolation,
and measurable exit predicates. Review date: 2026-10-13.

Reviewed subject: `.gnd-planning/milestones/pyrel-applications/notes/pyrel-applications-plan.md`

Reviewed SHA-256: `a001e5b87eaf55d4bc6763b918a5ec8f90a9a34d2c6655905cd420ea9f6ea735`

## Verdict

**No actionable findings in this seat's planning scope.** The plan is suitable
for owner consideration and subsequent PA0 specification. This verdict does
not approve implementation, establish native compatibility, or close any gate.

## Evidence and assessment

- Corpus validity: the plan's lines 43–51 require every applicable rule to have
  a named discriminating control and constrain agreement to an explicit finite
  corpus. Lines 166–173 require a model-addressed matrix, measured native
  baseline and genuinely red successor cases. Lines 183–209 distinguish
  guarded semantics, unknown coverage, vacuity, warning modality and independently
  recomputed derivations. The runtime omission is real:
  `src/gnd/export/pyrel_runtime.py:316` dispatches constraint families without
  `guarded`, and `src/gnd/export/pyrel_runtime.py:1141` evaluates constraint
  entries without computing BookRec derived heads. The plan does not claim
  these omissions are already fixed.
- Independence: plan lines 65–72 prohibit shared Python/GND business predicates,
  require exact staged-byte checks, and distinguish empty coverage from unknown
  coverage. Lines 225–227 and 240–246 demand query answers and report arithmetic
  independently of policy acceptance. This prevents a correct-looking query or
  filtered candidate from supplying circular checking evidence.
- Dependency order: plan line 131 orders the contract, guarded checks,
  derivations, BookRec application, expense application, executed documentation,
  and installed acceptance. BookRec's `complete.orm.yaml` defines
  `book_is_eligible` using the derived `book_is_blocked_for` relation and two
  negative premises; PA2 explicitly addresses dependency order and negative
  coverage before PA3 consumes complete eligibility. No application phase is
  scheduled before the checking capability it needs.
- Runtime isolation: plan lines 70, 142–143, 190–191 and 305–319 require an
  optional isolated runtime, maintained/packaged lock equality, GND-free
  generated execution and target-only installed paths. These requirements fit
  `tutorials/runtimes/pyproject.toml:4` and `:8`, which restrict Python and pin
  RelationalAI/DuckDB separately. Existing controls at
  `tests/test_external_runtime_tutorials.py:65` and `:106` already exercise
  interpreter selection and lock-resource equality; the plan treats these as
  starting points rather than native acceptance evidence.
- Exit predicates: plan lines 46–48 withhold output on unknown/error/forged
  states, line 68 preserves audit-completion compatibility, and lines 311–322
  require installed rejection controls and every applicable rule/derivation in
  the accepted corpus. Lines 380–398 explicitly defer exact test commands to
  owner-gated phase specs and require executed-lane/version/digest evidence.
  This is measurable at plan granularity without falsely presenting an
  unimplemented command as an available gate. Existing lane controls at
  `tests/test_external_runtime_tutorials.py:33`, `:40` and `:50` distinguish
  offline skips, explicit native selection and selected-runtime failure.

## Items to retain when specifying PA0

These are implementation/specification reminders, not findings requiring a plan
change: reuse native threshold-boundary controls for all expense comparisons,
including exact inclusive limits and positive-amount zero; retain warning
reachability and both missing/extra derived claims in the declared denominator;
verify installed import origins in both interpreters, rather than relying solely
on an unset `PYTHONPATH`. Existing category boundary and currency controls at
`tests/test_expense_tutorial.py:115` and `:134` provide concrete starting cases.
The plan's preservation and discriminating-control obligations already cover
these responsibilities.

## Scope limits

Read the entire reviewed plan and inspected the cited models, runtime dispatch,
report generation, tutorial runner, BookRec/expense tutorial controls, PyRel
export support and structural derivation/oracle isolation controls. This was a
static local review. No native PyRel process, package build, test suite, browser
render, provider API or paid reviewer was run. Current tests and historical
receipts are not fresh evidence of the proposed application's behavior. No
implementation or plan bytes were changed; only this review note was authored.
