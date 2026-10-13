# CS1 independent local review — seat four

2026-10-13. Reviewed the current runtime diff against `b57046f`, including the
new untracked `src/gnd/compiled_obligations.py`. Scope: witness redaction,
assurance, single/batch and anchored forwarding, and admission refusal.
No production changes, provider calls or certification were performed.
Reviewed evaluator SHA-256:
`dea4c7d3c3e24c4d831fb21886c1a76c2f8fcdca44f0bbac2fb8297d3c8fa875`.
Retained probe SHA-256:
`9d08085962edf1fda79a84de7f9ea7d06943962999346e596afcd9d46ecfbfda`.

## Result

No reproduced blocker in this review's scope. The two integration hazards from
the earlier plan review are addressed:

- `src/gnd/redaction.py:351` maps compiler locators to the asserted relation's
  effective redaction roles and derivation lineage; `:387` consumes that map.
  A public API probe marks every `var_filtered_compare` role redacted and checks
  the issue's failing compiled witness. The applied payload contains a marker,
  while the explicitly unredacted control retains the witness. Both retain
  assurance level `none`.
- `src/gnd/checking_service.py:307` composes after ordinary or anchored checking.
  A second public API probe adds an anchored constraint to the portable model.
  The anchored route still produces the named compiled failure and exit 1.
  The new option does not have to be accepted by the internal anchored helper
  for this public route to work.
- `src/gnd/checking_service.py:333` explicitly withholds certification and an
  execution capability for the expanded mode. This matches the scope boundary;
  the probes and issue regression confirm public assurance level `none`.
- API admission combinations are rejected before evaluation, while CLI
  admission and transition combinations return usage 64. The selected issue
  suite exercises both refusals. No appended compiled row enters admission's
  strict verdict/finding zip.
- `src/gnd/batch.py:222` forwards the keyword only when activated. Public issue
  tests compare single/API/batch failure references and full counts for both
  the string-role failure and numeric control.

## Reproduction evidence

From the repository root:

```text
uv run pytest -q tests/test_compiled_snapshot_obligations.py tests/test_public_redaction_reports.py tests/test_v62_phase3_redaction.py --tb=short
21 passed in 4.81s

.venv/bin/python .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CS1/review-four-probe.py
{"redaction_probe": "pass", "redacted_failure_rows": 1, "assurance": "none"}
{"anchor_route_probe": "pass", "compiled_fail_survives": true}
```

The retained probe creates bounded temporary model variants from the committed
portable issue fixture, calls the public API, and deletes those variants on
completion. Its redaction assertion distinguishes applied and unredacted output;
its anchor assertion requires both an anchored verdict and a compiled failure.
The temporary model variants do not alter the fixture or production files.

An initial probe used the nonexistent ID `var_filter_cmp` and therefore did not
activate redaction. That probe assertion failed; correcting it to the fixture's
actual `var_filtered_compare` ID produced the passing retained probe. This was a
review-driver error, not a runtime defect. A separate `uv run python` invocation
encountered a sandbox cache-access failure; the existing `.venv` interpreter ran
the retained probe without external credentials or network access.

## Limits and disposition

This review does not claim complete compiler soundness, join-limit coverage,
bound-reference agreement, or distribution acceptance. Those belong to the
other selected CS1 controls. The anchored probe establishes route forwarding
without constructing a valid evidence sidecar; it does not revalidate every
anchored evidence branch. No residual actionable finding is asserted here.

## Follow-up — current declaration recompilation

Rechecked the repair using `compiled_entries` as the shared current-declaration
inventory. Evaluator SHA-256:
`04d87141eed7f90c45cb07f3c891bfe4a3eba725ca8b0088551f71dfe5aaab62`;
redaction SHA-256:
`47352b833c421173c36033af2ea8ce3dbec861025cdf135cb7bbad82fe265dbe`.
`src/gnd/compiled_obligations.py:42` recomputes the sole-asserter index and
compiles current declarations without modifying the loaded side table.
`src/gnd/redaction.py:358` now obtains its locator inventory from that same
function, so activation and redaction observe the same renamed operation.

Reran the retained redaction/anchor probe: both assertions passed and assurance
remained `none`. A new retained public API probe,
`evidence/CS1/review-four-mutation-probe.py`, changes `filter_compare` to
`renamed_compare` after loading a model with redacted asserted roles. It verifies
that failure locators use the new operation name, witness values remain masked,
assurance is `none`, and the historical compilation side table is unchanged.
The probe passed using `.venv/bin/python`.

Reran `.venv/bin/python -m pytest -q tests/test_compiled_snapshot_obligations.py
tests/test_public_redaction_reports.py tests/test_v62_phase3_redaction.py
--tb=short`: **42 passed in 5.18s**. This expanded issue suite includes the new
bound-reference and trace activation controls. No reproduced repair-neighbor
failure or new actionable finding.
