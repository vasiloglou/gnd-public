<!-- Edited by review_tool.py sanitize: 9 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
Found eight issues. All were reproduced with read-only probes; publication calls were captured in memory.

1. **F1 — Enabling outcomes changes a validation refusal into exit 70.** [outcomes.py:169](<repo>/src/gnd/evolve/outcomes.py:169). Add an `operations` element with a missing `frame` and unexpected `roles: 1`. Without outcomes, validation refuses it with exit 3. With outcomes, `_depends_on` iterates the integer, raising `TypeError`; the CLI exits 70 and produces no outcome report.

2. **F2 — A refused embedded constraint leaves its operation `admitted`.** [outcomes.py:138](<repo>/src/gnd/evolve/outcomes.py:138), [service.py:474](<repo>/src/gnd/evolve/service.py:474). Add a fact type containing an `explicit` constraint. D-12 refuses that constraint, but the locator indexes only standalone constraint operations. Its failed lookup is ignored, so the fact-type addition is reported as `admitted`.

3. **F3 — Validation can blame the operation that created a valid host.** [outcomes.py:65](<repo>/src/gnd/evolve/outcomes.py:65). Add a valid fact type, then add a role referencing undeclared object type `missing`. The result marks the original fact-type addition `refused-by-validation` and the faulty role addition `dropped-with`. The element lookup takes precedence over the operation that introduced the invalid role. Two successive modifications of one object similarly blame the first modification when only the second introduces the error.

4. **F4 — Validation never locates added model operations.** [outcomes.py:125](<repo>/src/gnd/evolve/outcomes.py:125). Add an `operations` element without its required `frame`. Validation names `$.operations[2]`, but `_locate_path` excludes the `operations` collection. The faulty addition receives `unassessed` instead of `refused-by-validation`.

5. **F5 — Dependencies on later additions are missed.** [outcomes.py:186](<repo>/src/gnd/evolve/outcomes.py:186). Put a fact-type addition before its new role-player object addition, then omit the object’s required primitive. The object is refused, while the dependent fact remains `unassessed` instead of `dropped-with`. This ordering is supported: restoring the primitive makes the same proposal succeed.

6. **F6 — Value constraints omit their object-type dependency.** [outcomes.py:163](<repo>/src/gnd/evolve/outcomes.py:163). Add an invalid value type `region`, followed by a model-level value constraint targeting `object_type: region`. The constraint remains `unassessed`; it should be `dropped-with` because its target was refused.

7. **F7 — Include-analysis refusals bypass the requested outcome report.** [cli_service.py:697](<repo>/src/gnd/evolve/cli_service.py:697). Run the committed `mc-vocabulary/repin-only.proposal.json` case with both outcome options. The service attaches pending outcomes, but the inner `EvolutionIncludeAnalysis` handler publishes its radius and returns before the outcome-report writer runs. The requested report is absent.

8. **F8 — ID-based validation paths make the locator quadratic.** [outcomes.py:113](<repo>/src/gnd/evolve/outcomes.py:113). Each `$.object_types[id=tN]...` issue rescans the candidate collection. With matching operations and issues, 2,000 entries took 0.091 seconds; 8,000 took 1.498 seconds—approximately 16× the time for 4× the input. The committed performance test exercises numeric paths and misses this branch.

What checked out:

- All 23 pinned file digests match.
- The collecting D-12 walk matched the pre-change first refusal in **55,775 comparisons**, including induced confirmations and sample/common-sense cases.
- Twenty-five proposals produced identical outcomes-disabled preview bytes and digests against the pre-change service.
- A structural-validation CLI probe preserved exit 3 and identical stderr, publishing only the requested outcome report.
- All six verdict words were reached. Policy rows matched their policy cells.
- An outcome report was rejected by the preview reader; editing and rehashing an outcome row made it differ from a fresh preview.
- A secret placed in constraint values and provenance did not appear in outcome rows.
- Six selected tests passed.

For the standing matcher check, I exercised `_PATH_HEAD` and `_CONSTRAINT_STEP` with numeric and ID selectors, nested constraint paths, `operations` paths, and bracket/newline/Unicode identifiers. Ordinary nested paths located correctly; `operations` exposed F4. The unusual identifiers were rejected structurally and located through numeric paths. The detail truncations and gate-order slice produced no additional finding.

I could not run the full persistence/apply suite, filesystem hostile-report tests, or publication checks because the brief forbids creating or modifying files. Report publication was therefore intercepted in memory. No files were changed.

VERDICT: REQUEST CHANGES