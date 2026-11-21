<!-- Edited by review_tool.py sanitize: 3 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 18 SHA-256 hashes match the brief.

1. **F1 — Wrong exit for an unusable output directory.** [flatten_service.py:68](<repo>/src/gnd/extract/flatten_service.py:68) treats every publication `FileExistsError` as an artifact collision. Reproduced with `gnd flatten src/gnd/examples/literature/interop_fixture/checking.orm.json --out pyproject.toml`: it returns **11**, although neither output exists. The documented exit for an unusable output directory is **74**.

2. **F2 — Another command’s output changes.** [terms.py:127](<repo>/src/gnd/terms.py:127) adds the hint for every consumer. Reproduced with `gnd synth` on the temporal checking root: both versions exit 3, but the current message appends the flatten hint. The baseline message does not. The i1 amendment explicitly broadens this behavior, contradicting the brief’s requirement that other commands remain unchanged. Restricting the hint to `consumer == "extract"` would preserve that requirement.

3. **F3 — Invalid output strings escape refusal handling.** [flatten_service.py:56](<repo>/src/gnd/extract/flatten_service.py:56) catches only `InstallPathError` during path validation. Calling `flatten_to(valid_root, "bad\0output")` raises an uncaught `ValueError` instead of returning 74. This breaks the stated service totality contract; the reproduction uses the Python entry point because OS command arguments cannot contain NUL.

**Checked and found true:** 414 selected tests passed; focused Ruff checks passed. Read-only probes confirmed temporal and non-temporal output-byte parity, required include refusal codes, missing-input exit 66, collision handling, JSON digests, retained origins and temporal rule, unchanged include-free temporal extract goldens, and root/flat verdict parity. The CLI successor rejects mutated help independently. The 1,000-type probe took **0.279 seconds**.

**Limits:** Publication, collision, rollback, and timing probes used in-memory filesystem substitutes. I did not run fixture-writing suites or the exact generated `composed.population.json` parity case because the brief prohibits creating files.

VERDICT: CHANGES_REQUESTED