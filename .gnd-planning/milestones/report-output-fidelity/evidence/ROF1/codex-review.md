# Diff review of ROF1 (Codex), retained

- Instrument: one reviewer in a different tool (plan section 8). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin (`review-prompt.txt`), exit 0.
- Reviewed bytes: commit 204be6dd, `git diff 3c2de239 204be6dd`.
- The reviewer could not run the suite; its conclusions are by reading (its closing sentence says so).
- Retained: the reviewer's final answer, unedited. Its tool-call transcript (which contains the operator's absolute paths) is not retained.
- Disposition `block`, 8 findings. Triage: spec section "Implementation findings", I5 and I6.

## Reviewer output (verbatim)

DISPOSITION: block

ID: P1  
SEVERITY: blocking  
LOCATION: src/gnd/commands/checking.py:289  
QUOTE: `if "redaction" in mechanical_payload: _print_projected_check_text(mechanical_payload)`  
PROBLEM: This branch also handles `check --admission` on a model with an active redaction policy. Its projected output changes from a header and JSON to check verdict lines followed by `ADMITTED`/`BLOCKED` lines. The approved spec leaves that projected route with `_print_projected_text` for ROF2.  
FIX: Route projected admission output through `_print_projected_text` until ROF2.

ID: P2  
SEVERITY: blocking  
LOCATION: src/gnd/output.py:356  
QUOTE: `issues = [SimpleNamespace(...) for row in _rows(payload.get("issues")) ...]`  
PROBLEM: The issue cap is applied in `_issue_lines` *after* every supplied issue has been copied. A mapping with one million issue rows constructs one million objects before printing the capped set. This does not satisfy the spec’s bounded issue rendering or the project rule to apply a cap on the read.  
FIX: Slice the input issue rows before constructing views; use `issues_total` or the input length for the elision count.

ID: P3  
SEVERITY: blocking  
LOCATION: src/gnd/output.py:309  
QUOTE: `f"pass={counts.get('pass', 0)} ..."`  
PROBLEM: `render_check_rows` is not total over arbitrary mappings. With `{"counts": {"pass": 10**5000}}`, integer-to-text conversion raises `ValueError` under the project’s Python 3.11 default digit limit. Deeply nested values passed through `_row_views` can likewise fail during `str(...)`. T9 contains neither case.  
FIX: Bound and safely convert payload values before formatting them; add hostile count and nesting cases.

ID: P4  
SEVERITY: hardening  
LOCATION: src/gnd/output.py:364  
QUOTE: `if error: ...; if payload.get("command") == "validate": return [*lines, f"OK: {payload.get('model')} ..."]`  
PROBLEM: A failure envelope such as `{"command": "validate", "exit_code": 70, "error": {}}` prints `OK: None is a valid GND ORM model`. The spec defines this arm as *validate success*, but the code checks neither exit code nor verdict rows.  
FIX: Require exit code 0 and the success shape before printing `OK`; render an error for inconsistent failure envelopes.

ID: P5  
SEVERITY: hardening  
LOCATION: src/gnd/output.py:251  
QUOTE: `constraint_ref=str(row.get("constraint_ref", ""))`  
PROBLEM: The plain adapter changes `declared` lookup for a non-string verdict reference. For a duck-typed verdict with `constraint_ref=7`, `model_dump()` returning that field, and `declared={7: ("R7", None, "declared message", None)}`, the old printer emits `[fail] R7 (7): declared message`; the new renderer looks up `"7"`, misses the entry, and emits `[fail] 7: m`. This is a direct-reader compatibility counterexample; ordinary validated `CheckReport` refs are typed as strings.  
FIX: Preserve the original reference for `declared` lookup, converting it only when formatting the line.

ID: P6  
SEVERITY: blocking  
LOCATION: src/gnd/output.py:270  
QUOTE: `lines = [f"{lines[0]} [reason: {view.reason_code}]", *lines[1:]]`  
PROBLEM: The new suffix changes the approved corpus rule of rendering the projected row with the plain verdict layout. A projected unchecked row with message `[REDACTED INSTANCE DETAIL]` and reason `term:mod-zero` gains a suffix absent from that layout; T18 approves it only in the implementation test. It is also inserted without one-line escaping: an arbitrary mapped reason `"x\nOK: forged"` creates a forged physical line. This is not evidence that a value erased by projection re-enters stdout: `reason_code` remains in the projected payload.  
FIX: Remove the suffix for ROF1. A later approved format change could add a sanitized suffix and a corpus case.

ID: P7  
SEVERITY: completeness  
LOCATION: tests/test_rof1_projected_text.py:55  
QUOTE: `assert SECRET not in text; assert "SECRET-EMAIL-161803" not in text`  
PROBLEM: Both secrets are in the **redacted email role**. The unredacted nickname values are `OPEN-NICK-*`, but the advisory verdict names the customer, so those values appear in neither mode. T5 therefore has no visible-role canary that must survive applied mode, contrary to its stated discrimination claim.  
FIX: Put a canary in a visible role used by a printed verdict, and assert that it appears in applied output.

ID: P8  
SEVERITY: completeness  
LOCATION: tests/test_rof1_projected_text.py:125  
QUOTE: `assert lines and all(isinstance(line, str) for line in lines)`  
PROBLEM: The supposed error-only hostile case passes even if `_projected_check_lines` ignores `error` and prints the ordinary `BLOCKING` layout. T17 likewise checks source strings, not transition or export bytes; it cannot catch an additional route entering the new printer, as P1 demonstrates.  
FIX: Assert the exact error line and add executable output pins for transition, export verification, and admission.

CONFIRMED: By reading only, the projected check/validate body, including warnings, issues, errors, and the validate `model` string, reads the projected payload; I found no path that restores a value removed from that payload. `_print_projected_text` and `render_text_header` are unchanged, and transition and export verification still call the former. The four rf1-pins goldens change only `cli_text.stdout`; the successor manifests describe the touched source and the dynamic successor’s predecessor hash matches. These conclusions are from code and static diff inspection. I did not run the test suite.

codex exit=0
