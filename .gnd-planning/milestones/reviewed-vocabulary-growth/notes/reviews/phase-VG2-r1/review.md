<!-- Edited by review_tool.py sanitize: 4 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All nine SHA-256 hashes match the brief.

1. **Findings**

   - **F1 — Forbidden combinations exit 70 instead of 3.** [service.py:473](<repo>/src/gnd/evolve/service.py:473) introduces a refusal absent from the CLI’s exit classifier. Reproduced all six forbidden combinations on the ordinary policy fixture: each prints `EVOLUTION PREVIEW REFUSED (70)`. Minimal reproduction: pass `EvolutionError("new sample and common-sense constraints must be proposed/deontic (D-12)")` to `_evolve_service_exit`; it returns `70`. T2 checks the exception text without checking the public exit.

   - **F2 — Existing constraints gain admission, violating C3.** [service.py:469](<repo>/src/gnd/evolve/service.py:469) handles changed constraints alongside new ones. Reproduction: on the policy fixture’s unpopulated `order_has_amount`, start with a proposed/deontic sample uniqueness constraint over `order`, then modify its roles to `[amount]`. Preview refuses with exit 3 using the base predicate; the current predicate admits it with no policy issues. Reproduced the same result for `common-sense`. The baseline table misses this because it contains no changed-constraint case.

   - **F3 — C2’s named-refusal guarantee also fails on unattended models.** [test_vg2_evolve_sources.py:207](<repo>/tests/test_vg2_evolve_sources.py:207) explicitly accepts U8 instead. Reproduction: take T1’s proposal and independently set either constraint to `confirmed` or `alethic`. Candidate validation refuses at U2/U8, exit 3, before D-12 runs. All six forbidden combinations reproduced this. This is an existing validation-order constraint that contradicts the brief’s “on any model” claim; that guarantee needs reconciliation.

   - **F4 — The documentation guard misreads legal Markdown.** [test_vg2_evolve_sources.py:144](<repo>/tests/test_vg2_evolve_sources.py:144) selects sections using substring offsets, including headings inside fenced examples. Reproduced entirely in memory: prepend a fenced copy of the expected D-12 section, then change the actual sample rule to confirmed/alethic. T3 still passes because it reads the fenced example. Documentation disagreement can therefore escape the claimed guard.

2. **Checked and found true**

   - 51 focused, read-only tests passed, including the baseline table and induced-provenance admission controls.
   - Guide-shaped growth proposals, including `source-document` additions, preview successfully with both new sources.
   - All 30 resulting source spans re-hashed successfully, with none unchecked.
   - The actual three documents agree on the new proposed/deontic combinations.
   - Ruff passed for the changed Python files.

3. **Not checked**

   Apply/finalize and filesystem-writing test lanes were not executed because the brief requires read-only work. Preview probes supplied synthetic inputs in memory; no files were changed or credentials opened.

VERDICT: CHANGES_REQUESTED