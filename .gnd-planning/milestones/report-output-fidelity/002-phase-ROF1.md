---
milestone: report-output-fidelity
station: phase-ROF1
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-ROF1
date: 2026-11-07
gate:
  command: "uv run pytest -q tests/test_rof1_projected_text.py tests/test_rf1_semantic_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf6_query_policy.py tests/test_rf6_moves.py tests/test_v62_phase6_redaction.py tests/test_v6_phase6_transport.py tests/test_public_redaction_reports.py tests/test_public_emitter21_controls.py tests/test_public_report_redaction_metadata.py"
  exit: 0
  output: "525 passed in 48.77s"
  note: >-
    The focused gate at 57b25270, run with the worktree's own virtualenv (see
    I1 in the spec: a worktree run without it imports main's source). Lint,
    the component index (V6) and the sharded full default suite against main
    12daa5b7 (V1/V3) are in the body.
evidence:
  - path: src/gnd/output.py
    sha256: 5577e87dc837d79d03e692bc0252489df13eb3c5a2cee1a597de4d291818e323
  - path: src/gnd/commands/checking.py
    sha256: d28ec58fd322d292858e70b48b8e0f50275844801790e48841ca3d0414f67735
  - path: tests/test_rof1_projected_text.py
    sha256: fe49c1e6a9fa949ad0fae92bc1c5a3c844ad1ff0802dde9c1e601f4a94060fc3
  - path: tests/fixtures/rof1-projected-text/README.md
    sha256: 67dba60e89c70ba4853b932272193a90b2a8dbf5c782f5e78ffafe18a83a6103
  - path: tests/fixtures/rof1-projected-text/expected/exits.json
    sha256: 01129579c4b0a4a83d868a9bd1990ab4c5796d557d2e0b9c76c2fc7c25f98ba1
  - path: .gnd-planning/milestones/report-output-fidelity/notes/phase-ROF1-spec.md
    sha256: 23ff952855f42a2374120d5288b93a0317560008e95dbc18ea45be77f1d1ece9
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF1/codex-review.md
    sha256: 3ab0560ac79547df3553550e6c6a7d0f5ea87d71501a7dda14bc059289477546
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF1/full-suite-main-12daa5b7.txt
    sha256: 5b1573a294c053260bdfd2bd85caae6fe7e188f325f6fd0ce85e7bbf4b6f6197
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/ROF1/full-suite-rof1-57b25270.txt
    sha256: da1e309bc6290005f28f675fa94855830d04530bcca3924ffad86a7df67e7c73
---

# Claim

At 57b25270, `gnd check` and `gnd validate --format text` on a model with an
active redaction policy or temporal terms print the plain layout (BLOCKING /
ADVISORY / DERIVATIONS / counts / COVERAGE, the `ERROR at` issue lines, or the
`OK:` line) rendered from the projected payload only, instead of the projected
JSON (issue 112, ROF1 scope). `--format json` bytes, the plain text bytes,
exit codes, and the `transition`, `check --admission` and export verification
text are unchanged. The full default suite's failure list is a subset of main's
(82 of main's 85, none new).

## What shipped

- `src/gnd/output.py`: `render_check_rows` (the one row renderer; the plain
  `_print_report` is now an adapter over it), `_projected_check_lines`,
  `_print_projected_check_text`, `_issue_lines` (the one home of the issue cap,
  shared with `_print_issues`), `_text` / `_rows` / `_row_views` (total
  payload readers), `_with_reason`.
- `src/gnd/commands/checking.py`: `_cmd_check` (non-admission) and
  `_cmd_validate` call `_print_projected_check_text`; `--admission` keeps
  `_print_projected_text`.
- Corpus `tests/fixtures/rof1-projected-text/` (3c2de239, approved by the owner
  with "Approve, implement"): 13 cases, answers derived from the JSON reports
  with the base renderer; runner `tests/test_rof1_projected_text.py`, 64 tests.
- Four temporal `rf1-pins` goldens (`cli_text.stdout`), `goldens.sha256` and
  its pinned digest; successor rows for the four RF5 bodies and a chained
  dynamic-query successor; component index entry.

## Gate output (verbatim)

Focused gate, at 57b25270:

    525 passed in 48.77s

Corpus and ROF1 tests at each stage (`tests/test_rof1_projected_text.py`):

    3c2de239 (corpus, base code):   20 failed, 17 passed   [37 tests; against main's source, I1]
    204be6dd (implementation):      51 passed
    204be6dd + review tests:         6 of 9 new tests failed (P1-P5, T8); P6 failed once made to split lines
    57b25270:                       64 passed

Lint: `ruff check` over the touched source and test files: `All checks passed!`

V6: `python3 scripts/components_index.py changed --base main --strict`:
`changed against main (12daa5b): 73 file(s) differ; 0 to fix, 0 warning(s), 3 to reread`
(the three rereads are advisory: the commands package and `infra.output`
entries, unchanged in what they claim).

V1 (main 12daa5b7) and V3 (57b25270), default lane, six round-robin shards run
locally, one pytest process each:

    V1 main 12daa5b7:  85 failed or errored ids
    V3 rof1 57b25270:  82 failed ids; head minus main = none; main minus head = 3
    main-only: test_judge_fact_types_skill::test_review_f5_..., test_public_collection::
    test_current_collection_..., test_public_session_driver::test_driver_kills_...
    (the last is the known timing test, issue 117)

The 82 are 77 in `tests/test_public_tests_mode_corpus.py` plus 5 others
(`test_rf1_session_pins`, `test_public_book_runtime`, `test_doctor_uninstall`);
they fail identically on main in this environment and were not examined.
Evidence: `evidence/ROF1/full-suite-*.txt` (shard summaries and sorted ids).
The first head run (before the review repairs) had 24 head-only failures: the
four goldens, 11 relocated-body pins (7 of them only through the worktree
artifact), 2 query-inventory rows, a redaction
answer (E34), and 6 transport tests that fail only when the child process
imports a different source tree than the parent (a worktree artifact, I1).
All were repaired or explained (spec I1-I7).

## Criteria

| Criterion | Result |
|---|---|
| ROF1-C1 | `check` (applied, unredacted, `--rule-ids` refusal, ill-formed, temporal pass/advisory/derivation) and `validate` print verdict/issue/OK lines; no JSON line; exit codes equal the JSON route's (corpus, 13 cases) |
| ROF1-C2 | secret canaries absent in applied mode, present in unredacted; a public value survives applied mode (`redacted-visible-canary`) |
| ROF1-C3 | plain bytes unchanged: every plain golden and the full suite; `_print_report` calls `render_check_rows` (T7) |
| ROF1-C4 | changed bytes: the four goldens and their manifest; nothing else moved |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 3c2de239 204be6dd`, disposition `block`, 8 findings, all verified
and applied except one deliberately: [codex-review.md](evidence/ROF1/codex-review.md).
P1 (admission scope), P2 (cap on the read), P3 (totality), P4 (OK only for
exit 0), P5 (declared lookup), P7, P8 were applied with regressions observed
red; P6's escaping was applied, but the reviewer's remedy (remove the
`[reason: ...]` suffix) was not taken because answer E34 requires the reason to
be visible (spec I5). The reviewer could not run the suite. The repairs were
not re-reviewed.

## Refactoring review

Executed: the plain `_print_report` and `_print_issues` bodies moved into the
shared `render_check_rows` and `_issue_lines`, behaviour-preserving (plain
goldens and the full suite). Not done: the shared `_print_projected_text` still
serves three routes (ROF2), and `render_text_header` still raises on an empty
declaration list for those routes.

## Boundary: what this phase does NOT establish

- `transition`, `check --admission` and export verification still print
  projected JSON (ROF2).
- The `[reason: ...]` suffix is outside the approved corpus layout (T18 only).
- `WARNING at` lines have no corpus case (no fixture model produces a model
  warning); T4c pins them at payload level.
- The slow `evidence or census` lane was not run to green: its
  `test_public_acceptance_runner` cases fail on main as well (4 failures
  reproduced on a clean checkout of 12daa5b7).
- No JSON output, report schema, digest or version changed.

## Open questions

| Row | Question | Owner / target |
|---|---|---|
| ROF1-O1 | Keep the `[reason: ...]` suffix (E34 holds) or change answer E34 and drop it? | **Ruled 2026-11-07: keep the suffix** (owner: "approve", on the recommendation to keep it). E34 stands unchanged. |
| ROF1-O2 | `dynamic-query-successor.json` is appended at the tail of `DYNAMIC_SUCCESSORS`; a sibling branch that also appends will conflict | Did not occur: FU2 (PR 126) merged first without a dynamic successor. Its `bind_population` RF5 row did conflict in `source-successors.json`; merge 207da98e keeps FU2's row and ROF1's rows (guard and ROF1 suites: 770 passed). |
| ROF1-O3 | The 77 `test_public_tests_mode_corpus` failures and four others fail on main in this environment | not this milestone |
