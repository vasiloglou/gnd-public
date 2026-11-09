---
milestone: unattended-model-growth
station: "phase-UG3a"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-UG3a
date: 2026-11-09
gate:
  command: "uv run pytest -q -p no:cacheprovider <99 modules: both UG3 files, the plan §9 UG1 gate, RF1 CLI pins and harness, layering, arch, RF6 packages and query policy, disclosure, packaged-skill pins, documentation tutorials, unattended mode, and every test module importing gnd.evolve, the RF6 successor chain, the report schema or the validate API> --tb=short --junitxml=<scratch>/ug3-junit.xml"
  exit: 0
  output: "4007 passed, 42 deselected in 469.54s (0:07:49)"
  base: "5c6a0c5f (main after PR 147)"
selection:
  - {obligation: "G-phase (part A): corpus A1 to A6b, A10, A10b, successor cases A7 to A13, review regressions R1, R2, R4", disposition: run, command: "uv run pytest -q -p no:cacheprovider tests/test_unattended_span_coverage.py --tb=short", exit: 0, note: "26 passed in 3.11s"}
  - {obligation: "G-unattended, G-ug1, G-ug2, G-rf1, G-layers, G-arch, G-packages, G-rf6, G-evolve-consumers, G-report-schema, G-disclosure, G-skills, G-docs (spec §8 ledger)", disposition: run, command: "the gate above", exit: 0}
  - {obligation: "A14: RF1 CLI pins under 3.11, 3.13 and 3.14", disposition: run, command: "uv run --isolated --python 3.11|3.13 pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py; 3.14 in the gate", exit: 0, note: "119 passed under each"}
  - {obligation: "G-lint", disposition: run, command: "uv run ruff check src/gnd/api.py src/gnd/commands/checking.py src/gnd/model src/gnd/evolve <the changed test files>", exit: 0, note: "All checks passed!"}
  - {obligation: "G-components", disposition: run, command: "python3 scripts/components_index.py changed --base main --strict", exit: 0, note: "42 files differ; 0 to fix, 0 warnings, 9 to reread (seven subsystem summaries, evolve.command, model.loading: each reread and still accurate)"}
  - {obligation: "G-anon", disposition: run, note: "UG1's digest-set method (tests/test_why_not_anonymity.py FORBIDDEN, CONTROL, _hits) over 44 inputs: every file changed since 5c6a0c5f, the untracked new files and the commit messages; 0 hits; positive control found"}
  - {obligation: "phase-diff review", disposition: run, note: "one reviewer, Codex CLI, over both parts; notes/phase-UG3-codex-review.md"}
  - {obligation: "full default lane; -m 'evidence or census'; distribution lane; certification", disposition: cadence, note: "not selected (verification-selection: no explicit owner request)"}
evidence:
  - {path: src/gnd/model/_unattended.py, sha256: 1de7005d9abb6e98160c9142a1db24c31f506525f24243401ca78b3e6c6766ce}
  - {path: src/gnd/commands/checking.py, sha256: 9f3935720c5c827ad33e1800ed6e83888442c547507bcec656eae3900a36c852}
  - {path: src/gnd/api.py, sha256: 9ef2f6a3d51a37aa39a2fa72b16aae939a687fae43e2fd73b0744b090f99d300}
  - {path: tests/test_unattended_span_coverage.py, sha256: 30960fc14d3e342ab4deb1e4e0c06a03517a9cf816b7efa197763800a9a0a8d9}
  - {path: tests/fixtures/unattended-model-growth/ug3/expected.json, sha256: a46dc7dcdc702aa4c361024990d10e8f97179345a38099ab03ac9e0feebd7358, note: "the approved answer key, unchanged since its approval"}
  - {path: tests/fixtures/unattended-model-growth/ug3/parity-baseline.json, sha256: 6b84dfb57a5475dbf21d6cacbf60bbc6b10a3634e2fc9c31c596106bc4957035, note: "captured on 5c6a0c5f before the first source edit"}
  - {path: tests/fixtures/validate-documents-cli/expected.json, sha256: f3944e4768dc72b8175aadbba5b7f9eede2aff903ad53799585a7765ef43ff67}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/UG3a/dynamic-query-successor.json, sha256: d2c6971063971fd3ba22d96896dd5c2e9166b9ed7799f0fc70d89828600c0b3b}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG3-codex-review.md, sha256: 3b7b6921a8685ceeaaf215f2e7728d7a16559c8eb96b992e11e45674eab2bf34}
  - {path: "junit report of the gate run (scratch, not committed)", sha256: 24fd15464cb7ddc1934769a850ad495b32e20b8da8f67845d2f2bafaf0787eaa}
---

# Claim

`gnd validate MODEL --document DOC` on a model with `source.mode: unattended` now says how many
source spans it did not re-hash: one `unattended:spans-unchecked` warning at `$.source.documents`,
"N of M source spans were not re-hashed; supply every declared document with --document" (issue
74, UG-D3 (c)). A span counts as re-hashed only when its document was supplied and decoded and its
shape is valid. `--require-documents` makes the same entry an error (exit 3), listed after the
walk's other issues, and also runs the walk with no `--document`. A run in which every span is
re-hashed, a run without `--document`, and a model without the mode are unchanged: the 18
flag-free runs outside the carve-out are byte-identical to `5c6a0c5f` (A10), and the six carved-out
runs equal the base plus exactly one entry (A10b). The flag is a no-op outside the mode and a
usage error with `--identity` (64).

Authority: spec r1 approved `(o)` 2026-11-09 ("approved", all of UG3-D1 to D14 as proposed);
corpus approved `(o)` the same day ("Approve the corpus"). `auto=false`. Not merged; merge needs
the owner.

## Gate output

`4007 passed, 42 deselected in 469.54s` over 99 modules, exit 0; the part A file alone `26 passed`;
RF1 pins `119 passed` on 3.11 and 3.13; ruff `All checks passed!`; components 0 to fix. The ten
part A corpus cases give their approved answers, and the answer key's digest is unchanged since
approval.

## Review

Instrument: one reviewer in a different tool (Codex CLI, `gpt-6.1-sol`, reasoning `xhigh`,
read-only sandbox, prompt on stdin), over both parts at once. **One reviewer is one reviewer;
this is not a panel.** Of its six findings, three are part A's, all reproduced and fixed with a
regression test shown failing on `2dea8a81`:

- **1 (blocking):** a refusal rebuilt the payload by hand, so a redacted or reference-bearing
  model got a report without its projection. The defect predates UG3 (MG5's `--document`
  refusal); the strict flag added a route to it. Fixed by building the walk's result through the
  validate pipeline (`gnd.api._run_validate_with_documents`), which also retired the post-hoc
  payload edit.
- **2 (blocking):** `--require-documents` alone crashed on a valid plain model whose
  `provenance.spans` is not a list (layer one does not check it outside the mode). Fixed: the
  flag alone walks only a model in the mode, and the span iterator is total.
- **4 (hardening):** a non-string span digest raised `TypeError` in the coverage function. Fixed:
  type before lookup.

Dispositions and the verbatim output: [phase-UG3-codex-review.md](notes/phase-UG3-codex-review.md).
The fixes were not re-reviewed; the gate above runs over them.

## Refactoring review

Refactors EXECUTED, behaviour-preserving behind the same gates:

- **One span walk** (`_span_walk`) returns both the MG5 issues and the counts;
  `unattended_span_issues` keeps its signature and behaviour.
- **One validate pipeline** for the `--document` outcome: the result is built, projected and
  reference-wrapped like `_run_validate`'s own, replacing the hand-built refusal payload and the
  payload patch (review finding 1).

Seen and deferred: the CLI calls `unattended_span_issues` and `unattended_span_coverage` and so
walks twice (F-i1; UG3-Q3 below). The document read failures keep MG5's unprojected error payload
(UG3-Q1).

## Size

Estimate (spec §10): about 300 source lines and 700 test lines for both parts. Part A measured:
160 source lines added and 37 removed (`_unattended.py` 57, `checking.py` 65, `api.py` 35), 200
test lines added after the corpus commit, 20 normative doc lines. Within the estimate.

## Departures from the spec, each recorded in the spec's findings

- F-c1: a usage error exits 64, not 2 (A7).
- F-i1: two walks in the CLI, to keep §6.1's two signatures.
- F-i6 (review): §6.2 step 5 rebuilt an unprojected payload; the walk's result now goes through
  the validate pipeline, for the MG5 refusals as well.

## Boundary

- Part A only. Part B is [005-phase-UG3b.md](005-phase-UG3b.md); neither record claims the other's
  cases. UG4 (`unattended-growth.md`, the skill pointer, retiring the out-of-band step) is not done.
- Issue 74 is not commented on or closed.
- The counts say how many spans were re-hashed, not that the model is right about its text.
- Not merged, released or certified.

## Open questions

| ID | Question | Target |
|---|---|---|
| UG3-Q1 | A `--document` that cannot be read (66, 74, oversize 3) on a redacted or reference-bearing model still emits MG5's unprojected error payload | the milestone close sweep |
| UG3-Q3 | `gnd validate --document` walks an unattended model's spans twice (issues, then counts) | refactoring candidate, the milestone close sweep |
| UG2-Q2, UG-Q6, UG-Q7 | carried | as recorded |
