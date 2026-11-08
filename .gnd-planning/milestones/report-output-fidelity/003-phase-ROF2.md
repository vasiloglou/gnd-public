---
milestone: report-output-fidelity
station: phase-ROF2
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-ROF2
date: 2026-11-08
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rof2_projected_text.py tests/test_rof1_projected_text.py tests/test_public_transition_walks.py tests/test_public_transition_trace.py tests/test_public_emitter_trust_controls.py tests/test_public_redaction_reports.py tests/test_v62_phase6_redaction.py tests/test_carried_defects.py tests/test_v61_phase4_review_regressions.py tests/test_v62_phase2_report.py tests/test_v63_phase2_cache.py tests/test_transition_report.py tests/test_verify_cli.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf5_review_regressions.py tests/test_rf6_index.py tests/test_rf6_moves.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py tests/test_rf6_registry.py tests/test_rf1_pin_harness.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py"
  exit: 0
  output: "1371 passed in 234.65s (0:03:54)"
  note: >-
    The focused gate at 8287d5b6 (the review repairs), run with the worktree's
    own virtualenv. Lint, layers, the component index (V6) and the sharded full
    default suite against the base (V5) are in the body.
evidence:
  - path: src/gnd/output.py
    sha256: cdae5ecf4428382a8f26240ee0959f0fa40a1864e585229a32e3a15dff74ae35
  - path: src/gnd/commands/checking.py
    sha256: c5568bce29a81a70ea894e8f51080ed44acdcd41551e4c41f0565443883fcace
  - path: src/gnd/export/verification_service.py
    sha256: 8e9e79c661c9171a226f0447b287650180cad4498b80ee15383db544c0df79b2
  - path: tests/test_rof2_projected_text.py
    sha256: 583d2903730c4730a5af21a523ca0bd36c3c15829759e26d7d42b7e1c17349ba
  - path: tests/fixtures/rof2-projected-text/README.md
    sha256: accdb3f8f048137075691d155ac194630d5262354e050ad2ed6d8ff3d82d7e62
  - path: tests/fixtures/rof2-projected-text/expected/exits.json
    sha256: ef1c89f79f592ba1915982bbb7db1cd61be07517ec0f5a9adfcde8a28fc981bc
  - path: .gnd-planning/milestones/report-output-fidelity/notes/phase-ROF2-spec.md
    sha256: c3e398099823285c49e859f9f485ab7d87f9209279b514e5fe852eacd9b2c4b9
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF2/codex-review.md
    sha256: 1f92e9c954234fd0e308a0f15925023557fe70d54c08d18875759ceed000f06f
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF2/full-suite-base-f1a57836.txt
    sha256: e262e1ed74bc591fbad9405241850309764bd78573ea0a73747b6bee0740c72e
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF2/full-suite-rof2-8287d5b6.txt
    sha256: ee5d0001397a439f4aa4ebb845efbfa44045c9d59b0ce9e096d9d1d8e38458c4
---

# Claim

At 8287d5b6, walk text (`gnd check MODEL --pre … --steps … [--post …]`, both
post kinds), `gnd check MODEL POP --admission` and `gnd verify MODEL POP` with
`--format text`, on a model with an active redaction policy (or temporal terms,
for walks), print the layout the plain route prints (PRE-STATE / STEP /
FRAME or COMPUTED POST / POST-STATE; the check layout followed by
`ADMITTED`/`BLOCKED`; the `EXTRACTION:` line and the check layout), rendered
from the projected payload only, instead of a `REDACTION` header and the report
as JSON (issue 112, ROF2 scope). `--format json` bytes, the plain text bytes
and exit codes are unchanged. With ROF1, every route that printed projected
JSON as text now prints its layout; issue 112's text defect is closed in code
once this and PR 124 merge. The full default suite's failure list at
8287d5b6 has no failure the base lacks (82 ids, the same set ROF1's head had).

## What shipped

- `src/gnd/output.py`: `render_transition_rows` (the one walk renderer;
  `_print_transition` is now an adapter over it), `_projected_preamble`
  (warnings / issues / error, shared by every projected route; the issue cap is
  applied on the read), `_projected_transition_lines`,
  `_projected_verify_lines`, `extraction_line` (the one home of verify's
  extraction line, also used by the plain route), `_print_projected_header`,
  `_print_projected_transition_text`, `_print_projected_verify_text`, the
  row readers `_walk_views` / `_snapshot_lines` / `_derived_change_lines` /
  `_json_line`; `_print_projected_text` is a dispatcher over the route printers
  (D2).
- `src/gnd/commands/checking.py`: `_cmd_transition` calls
  `_print_projected_transition_text`; `_cmd_check --admission` calls
  `_print_projected_check_text`. `src/gnd/export/verification_service.py`:
  the projected route calls `_print_projected_verify_text`; the plain
  extraction line comes from `extraction_line`.
- Corpus `tests/fixtures/rof2-projected-text/` (7c485778, approved with
  "Approve, implement"): 14 cases; runner `tests/test_rof2_projected_text.py`,
  114 tests. ROF1's four placeholder tests replaced by named successors; the
  FIFO `--pre`/`--post` text pin in `tests/test_carried_defects.py` moved to
  the error line.
- RF5 successor rows for `_cmd_check` (chained), `_cmd_transition`,
  `_cmd_verify`, `_print_projected_text`, `_print_transition`; an RF6
  dynamic-query successor chained after ROF1's; the `infra.text_output`
  component entry. No golden file moved.

## Gate output (verbatim)

Focused gate, at 8287d5b6:

    1371 passed in 234.65s (0:03:54)

Corpus and ROF2 tests at each stage (`tests/test_rof2_projected_text.py`):

    7c485778 (corpus, base code):     29 failed, 28 passed   [57 tests]
    099ba22c (implementation):        111 passed
    099ba22c + review tests:          P1 and P2 red (P2 red once rewritten to count rows taken); P5 a test repair
    8287d5b6:                         114 passed

Lint: `ruff check` over the touched source and test files: `All checks passed!`

Layers and structure (V4): `tests/test_gnd_arch.py tests/test_rf1_layering.py
tests/test_rf8_structure.py tests/test_rf7_structure.py tests/test_rf3_core.py
tests/test_rf4_peripheral.py`: `1043 passed in 33.99s` (at 099ba22c's
source before commit; the repairs touched only `output.py` internals).

V6: `python3 scripts/components_index.py changed --base e1fb6a18 --strict`:
`changed against e1fb6a18 (e1fb6a1): 71 file(s) differ; 0 to fix, 0 warning(s), 4 to reread`.
The four rereads (`subsystem.check`, `infra.output`, `cli.checking_command`,
`export.verification`) were read beside the diff and are still accurate: none
of their capabilities changed.

V5, default lane, six round-robin shards run locally, one pytest process each:

    base f1a57836 (detached scratch worktree):  99 failed or errored ids
    rof2 8287d5b6:                              82 failed ids; head minus base = none
    base minus head = 17: 6 in test_v6_phase6_transport (the producer-identity
    artifact of a child importing another source tree, ROF1's I1), 8 in
    test_judge_fact_types_skill / test_model_multivalued_skill, and one each in
    test_guarded_corpus, test_public_collection, test_rf1_agent_cli_pins; the
    11 non-transport ones were not examined (they fail only on the base run)

The 82 are 77 in `tests/test_public_tests_mode_corpus.py` plus
`test_rf1_session_pins` [3] fresh and resume, two `test_public_book_runtime`
tests and one `test_doctor_uninstall` test: the same set ROF1's head had, not
examined. A first head run at 099ba22c is retained as
`evidence/ROF2/full-suite-rof2-099ba22c-contaminated.txt`: `output.py` was
edited (the review repairs) while its shards ran, so `inspect.getsource` read
shifted lines and 16 ids failed only there; all 16 pass at 8287d5b6.

## Criteria

| Criterion | Result |
|---|---|
| ROF2-C1 | walks (computed and declared post, failing step, failing precondition over a failing start, refused, temporal, derived changes), `--admission` and `verify` (pass, refused) print the plain layout; the derived-change summary appears once, under its STEP; no line is the report; exits equal the JSON route's (corpus, 14 cases) |
| ROF2-C2 | secret canaries absent in applied mode on every route, present unredacted where the layout prints them; public values survive applied mode (T10, P5) |
| ROF2-C3 | `validate --trace` keeps its block: ROF1's T13 passes in the gate |
| plain bytes | the plain transition and verify suites and the full suite; `_print_transition` calls `render_transition_rows` (T12) |
| changed bytes | as the census predicted: the FIFO `--pre`/`--post` text assertion and ROF1's placeholders; nothing else moved |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 7c485778 099ba22c`, disposition `block`, 6 findings:
[codex-review.md](evidence/ROF2/codex-review.md). P1 (a huge `constraint_ref`
raised) and P2 (the issue cap was applied after copying every row; a huge
`issues_total` raised) were reproduced red and fixed; both defects were in
code ROF1 introduced and also affected the check route. P5 (a vacuous
unredacted check) and P6 (the index note overstated the temporal routes) were
applied. P3 (no output cap) and P4 (a non-serializable computed post on the
direct plain printer) were not applied, with reasons in spec I8. The reviewer
could not run the suite. The repairs were not re-reviewed.

## Refactoring review

Executed: the walk layout moved out of `_print_transition` into
`render_transition_rows`, shared with the projected route; the warnings /
issues / error preamble moved out of `_projected_check_lines` into
`_projected_preamble`, shared by all three projected routes; the header rule
moved into `_print_projected_header`; the verify extraction line has one home.
All behaviour-preserving for the plain routes (plain suites and the full
suite). Seen and deferred: `_print_check_verdicts` and
`_print_derived_change_summaries` now have no caller inside `gnd`; both are
historical `gnd.cli` bindings and leave only under the shim-retirement rule
(open question ROF2-O2).

## Size

Estimate 130 source and 260 test lines. Measured (`git diff --numstat
7c485778 8287d5b6 -- src tests`, fixtures excluded): source +229 / -71 (net
+158), tests +257 / -13. By lines added the source is 1.76x the estimate,
past the 1.5x stop rule; by net change it is 1.2x. The excess is the
totality guards and the shared preamble that ROF1's code moved into; it was
not paused for, and is recorded here as a finding about the estimate.

## Boundary: what this phase does NOT establish

- Temporal `--admission` and temporal `verify` are not projected and print
  plain text; unchanged. `verify` refusals before the model loads print plain
  issue lines and are unchanged.
- The projected error line shows the message only: today's JSON text also
  showed the error's type (ROF2-O1).
- The reason suffix on walk lines has no corpus case (no corpus row carries a
  `reason_code`); T18 pins it at payload level.
- No `WARNING at` line and no derivation `[finding]` line in the corpus.
- No output-size cap on projected text (P3, declined).
- Issue 111 is untouched; no JSON output, report schema, digest or version
  changed.

## Open questions

| Row | Question | Owner / target |
|---|---|---|
| ROF2-O1 | The projected error line (`ERROR: [REDACTED INSTANCE DETAIL]`) no longer shows the error type that the JSON-as-text showed (`PopulationLoadError`). Add a ` [type: …]` suffix on projected routes, or leave it to `--format json`? | **Ruled 2026-11-08: leave it to `--format json`** (owner: "Leave to JSON", answering "Should the projected error line add the error type (ROF2-O1)?"). No change; the projected error line matches the plain route's. |
| ROF2-O2 | Retire the now-unused historical bindings `_print_check_verdicts` and `_print_derived_change_summaries` | the shim-retirement phase (RF-D5), not this milestone |
| ROF2-O3 | PR 127 is stacked on PR 124; it retargets to main when PR 124 merges | owner (merge order) |
