<!-- Sanitized 2026-11-24 under the project.md rule on retained reviewer output: absolute paths
     replaced by <worktree>, <scratch>, <tmp> or <home>. Nothing else was changed. See SANITIZATION.md. -->
All 18 supplied hashes matched before and after review. No files were changed.

1. **Findings**

   **F1 — Medium: four existing input-policy tests regress.**  
   [input_policy.py:105](<worktree>/src/gnd/input_policy.py:105) captures `MAX_BYTES` in default arguments. Existing RF7 controls lower that constant to 8, but `loads("[12345678]")` now accepts the input; the baseline refuses it. `load()` also reads against the lowered constant while decoding against the captured default, changing the refusal diagnostic.

   Reproduce:
   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -s -p no:cacheprovider tests/test_rf7_input_policy.py -k 'json_byte_cap_before_decode or stream_read_is_bounded'
   ```
   Result: **4 failed**. Adapt these controls to the explicit-bound API or preserve their previous behavior. The normal 10 MiB default still works.

   **F2 — Low: the required normative size-bound documentation is missing.**  
   [representation-format.md:2132](<worktree>/src/gnd/skills/gnd-orm-core/references/representation-format.md:2132) still states that import and export have fixed 10 MiB limits. Neither new flag appears there, and their help text does not cite that section. This leaves the documented contract inconsistent with successful raised-bound operations and misses spec §4.5’s explicit requirement.

   Reproduce by comparing that paragraph with an export of the supplied large fixture using `--max-output-bytes 33554432`: its **10,953,229-byte** loss report succeeds.

2. **Checked and found true**

   - **C1:** Independently rendered all **82 baseline entries** using the exporter from `1926e895` and the working tree; both match the supplied baseline.
   - **C2:** For each artifact as the largest, one byte below its size refuses with exit 3 before publication; exact size succeeds. Strict refusal precedes size refusal.
   - **C3:** Invalid bounds exit 64 with zero model-read calls, including a 5,000-digit integer.
   - **C4:** The large fixture round-trips in JSON and YAML at 32 MiB. Separate ontology inputs above 10 MiB pass their respective parsing caps with raised bounds. Loss-size refusal and its accepting boundary also passed; the restored-model cap remains enforced.
   - **C5:** `loads`, `JSONDecoder.decode`, and `raw_decode` accept exactly 10 MiB and refuse 10 MiB + 1 by default.
   - Matcher probes passed: integer conversion with alternate legal spellings; JSON scanning with escaped quotes, Unicode, nesting, whitespace and nonzero offsets; loss-report partitioning with Unicode, escaped pointers and embedded newlines.
   - Focused tests: **127 passed, 4 failed**. CLI pins and RF7 structure: **72 passed**. Repository Ruff check passed.

3. **Could not check**

   - Full filesystem publication tests and the complete guard suite require temporary files, which the read-only environment prohibits. Publication probes used mocks; large inputs used in-memory streams.
   - Approval provenance is unconfirmed: the supplied spec itself says “Draft r2 … awaiting owner review.”

VERDICT: CHANGES_REQUESTED