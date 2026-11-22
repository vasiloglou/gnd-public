---
milestone: include-root-routes
station: "phase-IR3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-IR3
date: 2026-11-21
gates:
  - command: "uv run pytest -q tests/test_ir3_pyrel_includes.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_pyrel_rules.py tests/test_pyrel_rules_calendar.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_rf1_cli_pins.py tests/test_pyrel_learning_path.py tests/test_ir1_judgments_includes.py tests/test_ir2_flatten.py --tb=short"
    exit: 0
  - command: "uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_release_text.py --tb=short"
    exit: 0
  - command: "uv run ruff check src tests tools"
    exit: 0
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
evidence:
  - path: src/gnd/export/include_roots.py
    commit: 6aacb928
    sha256: 4805aac86434ebe002a33b24bf2d40e45702bc35a9bc987416b0524b0ebe6229
  - path: src/gnd/export/emit.py
    commit: 6aacb928
    sha256: 3a6a6eb9033fa199f11f2b2dc626d33226a110d5b76b2b3c5f081e29841cec2e
  - path: src/gnd/export/pyrel_rules.py
    commit: 6aacb928
    sha256: 27c51fe372df1b3d8971ce80b87ccb7b29458ec20cc55c6f43b47889e0942d69
  - path: tests/test_ir3_pyrel_includes.py
    commit: 6aacb928
    sha256: 2ff4b1a2b03ca7e84c14a77c16faf3521a37e35c76ce974b47830a12300fd5dc
  - path: tests/test_mc1_guards.py
    commit: 1c5c0f66
    sha256: 1ac45ba1c065ce1d11f474f56619425cc054d11b7b2db161c2bb9b93e5a082fa
  - path: tests/test_mc1_review_regressions.py
    commit: 1c5c0f66
    sha256: 32067a50c3b48c207e40c6ac5114c378d118c7a998bfe28c1374add5a3f29d2c
  - path: tests/fixtures/ir3/default-extraction-flat.py.txt
    commit: 1c5c0f66
    sha256: a1d9b01633fb179724eeb92964d6684385580e7a5e269be8fe41de938aae41f9
  - path: tests/fixtures/ir3/duckdb-small-flat.py.txt
    commit: 1c5c0f66
    sha256: 5abbde75fe1f92e0cb56fc996b1bcb803623bab0f247a2044122f6e6891c6010
  - path: tests/fixtures/ir3/lqp-small-flat.py.txt
    commit: 1c5c0f66
    sha256: 4e5fecff818b41f39e10b709c247d37dba30452b141f463ee1b92ed8807e7b2f
  - path: docs/runtimes/pyrel.md
    commit: 6aacb928
    sha256: ec5ab52d556ba6edd4171d366b1152c449b294f69ed75ae821ceac0f46d6fca2
  - path: dev/components/COMPONENTS.md
    commit: 6aacb928
    sha256: 067b4d5f853a8c60202422281323e1474e7aa6a2f6e258cd7b3d33e684dd3d58
  - path: .gnd-planning/milestones/include-root-routes/notes/phase-IR3-spec.md
    commit: 6aacb928
    sha256: a8dc0e50c6aa804d3145f7ce124ef0dd54374dbc0b12800e9d75439618b5bb6c
  - path: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.md
    sha256: 67e289bf6d02361d4cf1b0c6b6269809dc2a1009b9967cd3342d61a508dd4bbd
  - path: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/FINDINGS.md
    sha256: aabf83377fa344c5e0467843e7282342865cfc7ecce25a68570a9de119d10e7a
---

# Claim

`gnd export pyrel` exports an include root through its flat model in the
default mode and under `--rules duckdb` and `--rules lqp`: the IR3 focused
lane exited 0 (388 passed, 81 deselected by the default lane filter) and the
guard block exited 0 (712 passed).

## Gate output (verbatim)

Focused lane:

    388 passed, 81 deselected in 29.65s
    exit=0

Guard block, plus `tests/test_release_text.py`:

    712 passed, 2 deselected in 95.86s (0:01:35)
    exit=0

Lint:

    All checks passed!
    exit=0

Component index, over the whole branch (IR1–IR3) against `origin/main`:

    changed against origin/main (260c433): 91 file(s) differ; 0 to fix, 0 warning(s), 12 to reread
    exit=0

The 12 `reread` entries (`subsystem.check`, `.synth`, `.codegen`,
`.conformance`, `.measure`, `.evolve`, `.recovery`, `model.loading`,
`cli.api`, `cli.dispatch`, `infra.disclosure`, `model.scalar_terms`) were
read beside the diff and still describe their code; none was edited.

Corpus, committed red before code (`1c5c0f66`): 29 cases failed; the T6
goldens and their control passed on the base, as preservation pins do.

## What the cases establish

| Criterion | Case | Result |
|---|---|---|
| IR3-C1 | T1 | exit 0; equal to the flat model's program except the constants and `MODEL_NAME` |
| IR3-C2 | T2 | exit 3, temporal message, no include code |
| IR3-C3 | T3 (2 roots × 2 modes) | exit 3, `paper_names_parent_method#0: family 'anchored'`, equal to the flat model's message (`main` at `260c4337`) |
| IR3-C4 | T4 (default; `write_case` under both `--rules`) | constants equal the record digest and pins |
| IR3-C5 | T5 | a re-pinned include changes both constants |
| IR3-C6 | T6 and its negative control | three include-free programs equal the `68e426ca` goldens |
| IR3-C7 | T7 (5 kinds × 3 modes), F1 (3 modes), one-prefix case (3 modes) | exit 3 with the include code or the encoding message, never 70 |
| rule 2 | T8 | 1,000 extra types under 5 s |
| one-read path | T9 | include-free model: `None`, loader not called |
| pins | `test_R13_pyrel_rules_renders_an_include_root`, `test_R7_composition_precedes_temporal_classification`, `test_cli_guards` without `pyrel` | green; R13 and R7 were red on the base; the CLI-guard change only removes the `pyrel` parameter, whose positive case is T1 |

## Review

One reviewer is one reviewer: Codex, read-only, through the review helper
(`notes/reviews/phase-IR3-r1/`), over the diff from `1c5c0f66`. Verdict
`CHANGES_REQUESTED`, one finding (F1, blocking), reproduced red in all three
modes and fixed in `6aacb928`; a doubled message prefix found while fixing
it was also fixed and pinned. The fixes were not re-reviewed. The reviewer
compared 12 more include-free model and mode pairs against the base and
found them equal; it ran no fixture-writing suite.

## Refuted premises

- IR3-D2 (a): `pyrel_runtime.py` cannot host the helper, because every
  default program embeds it verbatim (spec i1). `emit.py` then closed an
  import cycle (spec i3). The helper lives in `gnd.export.include_roots`.
- Plan §5 named `docs/agents/export-and-review.md` as the PyRel export page;
  the page that states the exporter's limits is `docs/runtimes/pyrel.md`
  (spec i2). Repaired at the close.

## Boundary -- what this result did NOT establish

- No exported program was run. The `pyrel_oracle` lane and the other
  deselected cases did not run; the programs are compared as text.
- IR3-C3 says what the `--rules` modes do at `260c4337`, before
  pyrel-rules-coverage RP2. After RP2 those roots are expected to export.
- A program already exported does not detect later include changes.
- The review fixes carry no review opinion. No merge or publication is
  authorized by this record.

## Open questions

- `compose` raises `UnicodeEncodeError` for an include path that cannot be
  encoded, on every route (`gnd check` reports it as an error object,
  `validate` and `flatten` print it, exit 3), where its own contract would
  give `include:path`. Rule 1 places the fix in `compose`. Carried to the
  close for a separate fix.

## Refactoring review

Refactors EXECUTED: one. `flatten_for_export` and `flattening_constants`
are one module (`gnd.export.include_roots`) that both renderers call, in
place of two copies of the compose-and-flatten step (rule 4). Behaviour-
preserving for include-free models: T6 compares whole program bytes with
the base in all three modes.

Seen and not done: `render_pyrel` (default) and `pyrel_rules.render` each
read the model file themselves and differ in how they parse it; joining
those reads would touch every export path and is not this milestone's.
Not a defect, so no row is owed.
