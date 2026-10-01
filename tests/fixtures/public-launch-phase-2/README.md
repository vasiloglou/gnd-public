# Phase 2 approval corpus — unexecuted

Read this entry point and the fixture bytes before the separate answer key.
These fixtures are proposed contracts for relocation, not executed results or
new GND semantics. No application data or historical certificate is included.

| ID | Input / action | Question for the reader |
|---|---|---|
| C0 | Validate model.orm.yaml; check clean.population.json | Can both CLI and API accept the declared facts? |
| C1 | Check violation.population.json | What happens to a title outside the allowed set? |
| C2 | Check empty.population.json | Is an empty evaluation scope a clean result? |
| C3 | Validate invalid.orm.yaml | Does a structurally plausible but nonexistent role load? |
| C4 | Check clean.population.json against textual.orm.yaml | Can a textual obligation be mechanically verified? |
| C5 | Check violation.population.json against textual.orm.yaml | Which decision wins when violation and unchecked coexist? |
| C6 | Invoke gnd --definitely-not-an-option | How is command usage refused? |
| C7 | Check C0 in the wheel with no _assurance_evidence | Is semantic acceptance also an assurance claim? |
| C8 | Authenticate a synthetic uncovered bundle; then alter its production roster | Does the reader accept stale evidence? |
| C9 | Same accepting synthetic control; then change runtime_domain.version and rebind its manifest anchor | Is a matching anchor sufficient after runtime identity changes? |
| C10 | Corrupt that accepting synthetic bundle's manifest bytes without rebinding anchor | Can corrupted evidence survive digest authentication? |
| C11 | Remove a required package resource from an isolated artifact copy | Does a resource audit fail loudly? |
| C12 | Supply source checkout on PYTHONPATH, prove that contamination, then scrub it | Does the installed probe really exclude checkout imports? |
| C13 | Add an unlisted B2 path / modify one retained B1 resource in scratch copies | Can the curated-diff check detect either mismatch? |
| C14 | Break a generated link / alter one unmanaged twin in scratch copies | Can discovery and twin checks detect either mismatch? |

C8–C10 use the bounded synthetic_release/publish recipe at the accepted source
pin in tests/test_v6_phase6_release_reader.py, selecting only its helper closure.
All rows are uncovered or excluded, release_id is synthetic-test-only, and no
solver, proof provider or certification runs. The helper must be adapted to the
installed package root; no private historical Git or conftest is required.
C9 changes runtime_domain.version to a value unequal to the measured control,
then recomputes manifest_sha256 using the existing helper. If reader ordering
prevents the intended branch, amend the case before claiming coverage.

No checker or harness is authored here. Execution starts after the owner gate.
