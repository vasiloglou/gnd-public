# IKE-Q3 — independent agent review and disposition

**Reviewer:** one general-purpose agent, given the diff and the approved spec,
read-only on the repository. Its outputs stayed in the session scratchpad.
**Verdict:** no blocking defect, no should-fix item. Five notes.

## What the reviewer reproduced

- **Red on the base.** On a base-source copy, Q1..Q5 and the four ruled H3 rows
  fail, 11 failures in all. Each fails because `ArtifactError` escapes, which
  is the intended reason.
- **CLI cases on scratch copies of the dispatch fixture:**
  - **66:** a missing leaf file, or a missing `references/` directory.
  - **74:** a `references` path that is a regular file; a leaf or directory with
    no read permission; a dangling symlink; a symlinked `references/`
    directory; a FIFO; an 11 MiB reference.
  - **3:** a changed digest.
- **Probes:**
  - **One source.** Nothing else in `discover()` raises `ArtifactError`.
  - **Precedence** is unchanged.
  - **judgments.** `api.judgments` swallows nothing that used to propagate on
    purpose: its other `ArtifactError` sources already become
    `JudgmentInputError`.
  - **H3.** The override replaces exactly the four rows that raised.

## Disposition

| # | Note | Disposition |
|---|---|---|
| N1 | discover checked only the direct `__cause__`; evolve walks the chain | **Fixed:** the catch walks the cause chain for `FileNotFoundError` |
| N2 | an over-cap reference in judgments is outcome 3 "binding", while its own over-cap inputs are 4 "limit" | **Recorded, not changed:** D2-A rules "binding" for missing and linked files, and the spec adds no new reason. The over-cap asymmetry is unruled (record 015, open question IKE-Q5) |
| N3 | a model under a symlinked ancestor (macOS `/tmp`) exits 74 "could not read input", even with an intact reference | **Pre-existing, unchanged by this diff:** recorded as a boundary item in record 015 |
| N4 | the doc's 74 row was narrower than the behaviour | **Fixed:** the row names a linked file or directory, a non-regular file, an unreadable file and an over-cap file |
| N5 | Q5 could not tell the binding refusal from the probe policy's later "shape" refusal | **Fixed:** Q5 runs with `--format json` and asserts reason "binding" |
