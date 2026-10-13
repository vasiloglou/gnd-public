# Phase12 Astra/high R1

Retained reviewer response; edited only to sanitize absolute paths.

No blocking false-positive acceptance defect demonstrated. Two hardening findings remain; the declared branch controls are incomplete. These are source-level findings—I executed no tests.

1. **Aggregate size enforcement occurs after allocation.** At [population_shape.py:48](<GND_WORKTREE>/src/gnd/population_shape.py:48), `json.dumps` materializes the entire schema before checking the 1 MiB limit.

   Concrete input:
   ```python
   {"type": "string", "title": "x" * 600000, "description": "y" * 600000}
   ```
   Both strings pass the individual checks, so serialization processes over-budget content. Repeated strings can amplify this substantially; dictionary-key lengths also escape the preliminary string check. Eventual fallback remains sound, but the byte limit does not bound serialization allocation.

   Reproduction: the newly added [aggregate-size control:179](<GND_WORKTREE>/tests/test_m3_population_shape.py:179) replaces `json.dumps` with a sentinel. Against the reviewed source, `_bounded` reaches that sentinel instead of first raising `_Unsupported`. Run that single test when execution is authorized; I did not run it.

2. **Condition and enum safety controls are masked by earlier rejection.** The [version matrix:30](<GND_WORKTREE>/tests/test_m3_population_shape.py:30) sends `2.0` and `True` through the bundled root integer constraint. They fall back before exercising the conditional predicate. The only test schema containing `then` has an unsupported predicate, so it cannot exercise the implemented [then branch:254](<GND_WORKTREE>/src/gnd/population_shape.py:254). Likewise, the [numeric enum cases:85](<GND_WORKTREE>/tests/test_m3_population_shape.py:85) include an integer type guard that masks enum-specific Boolean admission errors.

   A focused condition control should use:
   ```python
   schema = {
       "if": {"properties": {"v": {"const": 2}}, "required": ["v"]},
       "then": {"properties": {"p": {"type": "string"}}, "required": ["p"]},
       "else": {"properties": {"p": {"type": "integer"}}, "required": ["p"]},
   }
   doc = {"v": 2.0, "p": 7}
   ```
   Draft selects `then` and rejects. A deliberately faulty strict-integer predicate would select `else` and accept. Add the corresponding Boolean collision case using `const: 1`, plus standalone `{"enum": [1]}` against `True`. These are proposed controls, **not claims that the current implementation misvalidates those inputs**. Prove the controls fail their targeted mutants before claiming coverage.

By source inspection against the bundled schema and installed Draft implementation, I verified:

- Unknown keywords and malformed supported operands trigger fallback; every `anyOf` branch is compiled.
- Absent/version-1 facts remain scalar-only; version 2 permits valid opaque facts; instances remain scalar-only.
- Intersections and conditions receive their original input, and core outputs are discarded.
- Strict scalar admission, finite-number configuration, Unicode length handling, object requirements/extras, and homogeneous items have sound admission logic for the reviewed subset.
- Schema content is serialized anew before the bounded eight-entry cache lookup, preventing sequential mutation from reusing stale compiled policy.
- The loader seam, patched Draft constructor dispatch, and sorted diagnostic construction remain intact. Parsing, layer 2, markers, and public signatures are unchanged.
- The new module is assigned to the same layer with an empty allowance list. No population/evaluator cache was added.

The retained RED reports **45 failed, 2 passed**. I found no retained phase12 green/focused/lint logs; the available phase11 logs do not validate these bytes. The timing artifact explicitly records baseline instrumentation, not current-byte performance. Native 3+3 and app90 results remain unverified here.

Reviewed accelerator SHA-256: `dda4de8abbb03bcfd797dc8d6ec188d4842d41490dfb34bfefbfd37cd294d415`.

One reviewer is one reviewer. No files were changed, credentials read, providers called, or historical/certification replay performed. Keep the two-round limit; defer completeness work. Final 109-development agreement and successful 29-heldout median ≤15s remain unmet. This review establishes neither milestone closure nor source merge authorization.
