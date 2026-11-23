<!-- Edited by review_tool.py sanitize: 4 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
The patch SHA-256 matches the brief. All locations below refer to head `7df6c0c`.

1. **Findings**

**F1 — Coverage check silently misses single-quoted rule IDs.**  
[tests/test_model_v2.py:506](<repo>/tests/test_model_v2.py:506)

The new regex recognizes only double-quoted literals. In memory, I replaced `_rule_op_param_ref` with a legal function emitting its existing `"semantic:op-param-ref"` and an additional `rule_id='semantic:op-extra'`. Both the rejecting-case coverage check and normative inventory check **passed**, despite the extra error having neither coverage nor documentation. Expected: rejection for the missing case. Parse the Python source with `ast`, or consume explicit rule metadata.

**F2 — The loop-rule exception substitutes its expected inventory without checking completeness.**  
[tests/test_model_validation.py:118](<repo>/tests/test_model_validation.py:118)

The `indirect` branch checks that two literal strings appear, then substitutes those two expected IDs. I supplied an in-memory `_rule_derivation_membership` that emitted IDs from:

```python
("semantic:membership-list",
 "semantic:membership-duplicate",
 "semantic:membership-extra")
```

The normative inventory test **passed**, although the third ID was undocumented. Expected: inventory mismatch. Derive and compare the complete declaration rather than checking that expected strings occur.

**F3 — Source slicing uses different line boundaries from Python’s AST.**  
[tools/build_ci_repair_successors.py:102](<repo>/tools/build_ci_repair_successors.py:102)

`str.splitlines()` counts U+2028 as a line boundary; AST line numbers do not. For this legal Python source, with an actual U+2028 inside the docstring:

```python
source = 'def example():\n    """a\u2028b"""\n    return 1\n'
```

the builder’s extraction **omitted `return 1`**. Inserting U+2028 into `_rule_anchored_role_and_recogniser`’s existing docstring caused the complete builder to raise `KeyError: '_rule_textual_alethic'`, because following definitions were sliced incorrectly. Use LF-based line boundaries consistent with AST positions.

**F4 — Informational, pre-existing: CRLF block scalars lose their final newline.**  
[src/gnd/model/_parsing.py:34](<repo>/src/gnd/model/_parsing.py:34)

`parse_model_document(b"note: |\r\n  hello\r\n", source="probe.orm.yaml")` returned `"hello"`; the YAML reader returned `"hello\n"`. The header regex misses CRLF and permits `rstrip()` to remove significant content. I reproduced the same result with the base parser, so this is inherited rather than introduced.

2. **What I checked and found true**

- The ten moved guarded definitions and `parse_model_document` are verbatim; the re-exports retain identity. `_validation.py` has 4,989 lines.
- All **232 RF6 body/pickle controls**, **422 RF4 algorithm controls**, and **ten retargeted scalar mutation controls** passed.
- The successor builder reproduced both committed records exactly, with writes redirected into memory.
- All four `filtered` and thirteen `any_of` snapshot guarded rows were excluded from both target sets. The RF1 assurance golden passed unchanged.
- The guarded scope splits correctly handled membership in `any_of[11]` with an existential local variable.
- Parser matcher probes passed for LF block scalars and quoted `>`; CRLF failed as described above.

3. **What I could not check**

I did not run the complete default lane or reproduce every synthesis/measurement golden: those workflows create files, which the brief forbids. C1 and the entirety of C4 therefore remain unverified. Execution used PR sources loaded from Git into memory; no repository files were changed.

VERDICT: CHANGES_REQUESTED