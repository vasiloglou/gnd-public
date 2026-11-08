# Triage of the Codex review of plan r2 (driving agent, 2026-11-07)

Every finding was read against the cited code. None relitigates an owner
ruling except where noted. All ten are applied in plan r3 / ROF1 spec r2.
**r3 and spec r2 were not re-reviewed.**

| ID | Verified by | Disposition |
|---|---|---|
| P1 reports still emit the legacy digest, so 111 is not closed | read `checking_service.py`, `payloads.py` | applied: issue 111 stays open as partially addressed unless ROF5 delivers (plan predicates 4, 5, section 2.3). D3 is unchanged (ruled: no emission now); only my wording that 111 "closes" was wrong |
| P2 version 2 excludes `operations`; version 1 (reference-bearing) includes it | read `values.py:201-213` | applied: version 2 is defined only for a model without `reference_populations`; reference-bearing models keep version 1; operations-only mutation test. **This narrows D4's ruled wording**; flagged in the D4 row for the plan gate |
| P3 sites differ by contract; generated Pyrel plans cannot call a helper | read `assurance/transport.py:115`, `model/__init__.py:627`, `export/souffle_runtime.py:513`, `export/pyrel_rules.py:1609,2212` | applied: section 1 classification; ROF4-C1 scope; new owner decision D7 (open) |
| P4 witness compares a whole binding dict; measure counts distinct digest strings and emits the sidecar's | read `witness/kernel.py:305-314`, `measure/report.py:218-231,308` | applied: ROF4-C2 cases, plan section 2.8 |
| P5 `_print_projected_text` is shared; ROF1 would change ROF2's routes | read `commands/checking.py:111,218,289`, `export/verification_service.py:220` | applied: ROF1 adds `_print_projected_check_text` and leaves the shared function alone; ROF2 estimate raised to about 140/220 |
| P6 `validate` has no `--rule-ids`; validate success layout undefined | read parser registration (`--rule-ids` only on `check`), `commands/checking.py:123-125` | applied: ROF1-C1 corrected; validate success text specified (M1 item 4); T15, T16 |
| P7 test table lacks branch cases and exits | read against spec-note-contract section 8 | applied: T3b, T3c, T4b, T4c, T13-T17; every row has an expected exit |
| P8 spec provenance stale, D2 ruling not carried | read | applied: spec r2 provenance; D2 row carries the ruling |
| P9 census not reproducible from the plan | accepted | applied: `evidence/census-r2/` (script, roster, canonical-form probe); ROF4-C3 by artifact class |
| P10 `validate --trace` / `--document` print from the model | read `commands/checking.py:54-111` | applied: boundary stated in plan section 2 and spec M1; canaries T13, T14. Not a demonstrated leak (neither prints a population value) |
