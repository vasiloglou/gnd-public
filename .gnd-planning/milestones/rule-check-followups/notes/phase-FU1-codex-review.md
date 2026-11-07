# Phase FU1: Codex review of the diff

- Instrument: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only`, prompt on stdin.
- Subject: `git diff 6651e5a4 9f938f48`. One reviewer is one reviewer.
- Exit 0. Disposition: **revise**, two completeness findings.

## Dispositions

| ID | Reproduced | Disposition |
|---|---|---|
| R1 | yes: a mutant that narrowed the reason inside `temporal_admission_report`'s derivation items passed all 63 cases | **fixed**: T2 now validates each report branch at every enclosing `items` location that references `derivation_verdict` or `_v9`, through the branch's own pointer. The same mutant now leaves 7 cases red; the pre-fix schema leaves 38 red |
| R2 | yes: the `derived-unknown` corpus row has empty findings, a shape `DerivationVerdict` refuses (`extensions.py:133-140`); the shape it would accept (one `derived-extension-unresolved` finding) is refused by `derivation_finding` and the unchecked `maxItems: 0`, in `derivation_verdict` and `derivation_verdict_v15` alike | **deferred, open question**: no route emits `derived-unknown` on a derivation row (it is a constraint and precondition reason, `branches.py:284`, `transition.py:1603`); the mismatch predates FU1 and v15 has it too. The approved answer is unchanged; the corpus claim is qualified in the record |

## Review output (verbatim)

    DISPOSITION: revise
    
    ID: R1
    SEVERITY: completeness
    LOCATION: tests/test_fu1_term_reasons.py:44
    QUOTE: `return ["derivation_verdict"]`
    PROBLEM: The declared legacy-reference and temporal-admission cases validate only a standalone base row. Lines 42–44 check that a branch contains a reference somewhere, then discard that branch. A broken report-level route could therefore pass T2.
    FIX: Validate representative complete reports through `legacy_reference_report` and `temporal_admission_report`, with a derivation row carrying a new reason.
    
    ID: R2
    SEVERITY: completeness
    LOCATION: tests/test_fu1_term_reasons.py:32
    QUOTE: `"findings": [],`
    PROBLEM: This makes the `derived-unknown` case pass with a row the runtime cannot emit: `src/gnd/extensions.py:133–140` requires one unresolved finding. The widened enum does not make that real shape valid under `derivation_verdict`: `src/gnd/report.schema.json:1113–1114` requires unchecked findings to be empty, and `:640–644` excludes `derived-extension-unresolved`. A read-only validation probe confirmed rejection. The same finding-shape mismatch exists in v15.
    FIX: Test `derived-unknown` with its real finding and record the finding-shape defect separately if FU1 remains limited to the ruled enum change; qualify the corpus’s claim of acceptance.
    
    The six CLI answers match 9f938f48; the focused suite passed (63 tests). Both changed enums contain the ruled set, and the term-reason rows tested here validate. The edit only adds enum members, so it cannot invalidate a previously valid report. I found no other tracked report-schema copy, current digest, or version-7 reason-list documentation that needs updating; the RC1 schema digest records historical bytes.
