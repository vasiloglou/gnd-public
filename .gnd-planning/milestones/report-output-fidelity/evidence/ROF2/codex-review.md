# Diff review of ROF2 (Codex), retained

- Instrument: one reviewer in a different tool (plan section 8). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -o <scratch>/codex-final.md -`, prompt on stdin (`review-prompt.txt`), exit 0.
- Reviewed bytes: commit 099ba22c, `git diff 7c485778 099ba22c`.
- The reviewer could not run the suite; its conclusions are by reading (its closing sentence says so).
- Retained: the reviewer's final answer, unedited. Its tool-call transcript (which contains the operator's absolute paths) is not retained.
- Disposition `block`, 6 findings. Triage: spec section "Implementation findings", I8.

## Reviewer output (verbatim)

DISPOSITION: block

ID: P1  
SEVERITY: blocking  
LOCATION: src/gnd/output.py:275  
QUOTE: `constraint_ref=ref if isinstance(ref, (str, int)) else _text(ref)`  
PROBLEM: The walk renderer is not total over arbitrary mappings. A failing pre-snapshot verdict with `constraint_ref=10**5000` reaches `_constraint_verdict_line`; `path_segment` calls `str()` on that integer and raises `ValueError`. T11 puts its huge integer in a frame verdict’s `verdict` field, which takes the safe `_text` path.  
FIX: Normalize snapshot `constraint_ref` through `_text` before passing it to `path_segment`.

ID: P2  
SEVERITY: blocking  
LOCATION: src/gnd/output.py:379  
QUOTE: `rows = [row for row in _rows(payload.get("issues")) if isinstance(row, Mapping)]`  
PROBLEM: The claimed cap is applied after reading every issue into a new list. An envelope with millions of issues consumes memory proportional to all of them. With one issue and `issues_total=10**5000`, `_issue_lines` also raises `ValueError` while formatting the elision count. Both walk and verify use this preamble.  
FIX: Slice the raw issue list before building views, and safely bound or format `issues_total`.

ID: P3  
SEVERITY: hardening  
LOCATION: src/gnd/output.py:487  
QUOTE: `for step in _rows(block.get("steps")):`  
PROBLEM: There is no output bound for arbitrary mappings: an N-step payload produces at least N STEP lines, and one computed-post string can make `_json_line` allocate and print an arbitrarily large line. T16 establishes linear time, not bounded output; T11 has no size assertion.  
FIX: Set a documented projected-output row and byte limit with an elision line, while preserving the plain adapter’s valid-report output.

ID: P4  
SEVERITY: hardening  
LOCATION: src/gnd/output.py:466  
QUOTE: `except (TypeError, ValueError, RecursionError): return "<non-text>"`  
PROBLEM: Plain printer behavior changes for a direct `TransitionReport()` call with `computed_post={"x": float("nan")}`. The base printer prints `PRE-STATE` and `COMPUTED POST`, then raises from `json.dumps(..., allow_nan=False)`; the new adapter prints `<non-text>` and continues through `POST-STATE`. This is a direct-printer counterexample; I did not establish that the CLI admits such a computed post.  
FIX: Keep the old serialization behavior for the plain adapter and use the placeholder only for projected rendering.

ID: P5  
SEVERITY: completeness  
LOCATION: tests/test_rof2_projected_text.py:47  
QUOTE: `"transition-full-unredacted": set()` and `assert UNREDACTED_SECRETS[case] <= set(SECRET.findall(text))`  
PROBLEM: The unredacted-secret assertion for this case is always true, even with empty output. It cannot establish T10’s stated unredacted presence check for the full walk.  
FIX: Use a full-walk case that prints a secret value, or narrow T10’s claim and remove this vacuous parameter.

ID: P6  
SEVERITY: completeness  
LOCATION: dev/components/COMPONENTS.md:2530  
QUOTE: `Text for a declaration-bearing or temporal route (check, validate, walks, check --admission, verify) is rendered from the projected payload only`  
PROBLEM: This overstates the implementation. Temporal-only admission is excluded from `_project_result`’s temporal set; temporal-only verify uses the plain `_print_report(report)` route. The approved spec explicitly names both boundaries.  
FIX: Say that temporal-only projection applies to check, validate and walks; admission and verify require active redaction.

CONFIRMED: By code reading, the normal generated walk, admission and verify payloads reach their intended text printers; those printers read projected payload fields, and I found no path that reintroduces a value removed by projection. The D3 reason suffix is applied to projected walk verdict rows and omitted on the plain route. Valid plain walk fields retain the old section order. The RF5 successor changes and RF6 successor chain describe the intended code moves; the RF6 predecessor digest matches. I did not run the test suite.