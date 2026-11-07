---
milestone: rule-check-adoption
station: phase-RC6
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RC6
date: 2026-11-06
gate:
  command: "uv run pytest -q tests/test_documentation_tutorials.py tests/test_plan_app_docs.py -p no:cacheprovider"
  exit: 0
  output: "166 passed"
  note: >-
    The plan section 9 RC6 row (V2), at 0a46d576, with the how-to style test.
    The runner group, the strict build, the link check, the installed
    example (V3, V4), the component index check (V6) and the sharded full
    default suite against main 4232d233 (V1/V5) are in the body.
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "RC6 changes documentation and adds example data only; no source file changes"
evidence:
  - path: docs/how-to/adopt-rules-with-a-baseline.md
    sha256: 3c172af33fa8bf7e106aa765c4cec2dc3e913c1ebd21f7baa0043d97f008f711
  - path: docs/reference/rule-check-report.md
    sha256: 5604120b66c951516fb8eac138763d7663f6c980f1ba5e979dfa759e265daf7d
  - path: docs/assets/applications/rule-check-baseline.svg
    sha256: 021560a07e168657a785a88a556f515d62c8d8d0a34a6a166939e43bbc638219
  - path: docs/reference/cli.md
    sha256: 8b1364e62b5a0cc61c361db84893f6247e82f3fc358a37a54fd58b8f78e734c9
  - path: docs/reference/formats.md
    sha256: fba4321c79e2abde34a25d8c3976d99d13171933395da73013f93ad0dc5543d8
  - path: zensical.toml
    sha256: df3355ee93e773fd3adead50e3e852ab10eef3ce95de50381e48e1657a882023
  - path: tools/run_tutorials.py
    sha256: fe8483a3081717b313db52c51f9b2e00d6357ff93f8307b22cee4e3cf8135f91
  - path: src/gnd/skills/gnd-orm-core/references/constraint-reference.md
    sha256: b3453e98a3b3816bec4dc40d0c985be8d57f9fbcbed42c8986250e978881b57d
  - path: src/gnd/examples/rule_check/README.md
    sha256: 1609682d3b0dbe9508c3914080123fbffeefba3788f7405d948c71e45cd6a9f9
  - path: src/gnd/examples/rule_check/model.orm.yaml
    sha256: e83fcc2bc018bd09d73212f650720b30c750e2d5a405c76b7810bc64626db53b
  - path: src/gnd/examples/rule_check/base.population.yaml
    sha256: d816aea7caf713a67837f1361c4a2676a91a5aac82ba7167bf1ef88106fd5fcd
  - path: src/gnd/examples/rule_check/head.population.yaml
    sha256: 4d6a6e2f57c6799890429b47546b3de39902cc06d660a335345f482170f5b1e0
  - path: src/gnd/examples/rule_check/fixed.population.yaml
    sha256: ae8a6a67686b02bdbe7881dfc0a179d575f6a09dd5c05fc49101867db6dc4b3e
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC6/full-suite-main-4232d233.txt
    sha256: e059446260c77e9805cd97e351591e07be2e659afa47b80e619754f25367a80d
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC6/full-suite-rc6-8da3b3f7.txt
    sha256: 0ef2621ce14902d4572d6bf4a20c23f555c13d9ae3935b2c24c300c13b870682
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC6-spec.md
    sha256: 6a1cc8b37dae7f254a542980dbc37ee95da654c85f50380d65df4d3236093577
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC6-codex-review.md
    sha256: 7146acf582fbf7e04d7fba4dab82fd9fd71870c3e4f4014f9b4e00ac3aee91d5
---

# Claim

At 0a46d576, the rule-check workflow of RC1-RC5 is documented end to end:
a how-to that adopts four rules on a project that already breaks them,
worked on a shipped synthetic component graph, whose seven runnable blocks
and their output run under `tests/test_documentation_tutorials.py`; a
field-by-field reference for report version 15; `remedy` in the constraint
reference; and the CLI and format index rows. The owner saw the rendered
pages at the checkpoint. V2 exited 0 (166 passed), and the full default
suite matches main 4232d233 apart from one load-sensitive timing test on
each side, both of which pass in isolation at the final commit.

## What shipped

- **M1** `src/gnd/examples/rule_check/`: a component graph with four rules,
  each with an `id` and a `remedy` (`no_import_loops`, acyclic;
  `no_legacy_components`; `every_component_has_an_owner`, deontic;
  `no_draft_releases`, vacuous while no release is recorded), and three
  populations (`base`, `head`, `fixed`), all `source: tool-output` with a
  `producer`. Head against base: exit 1, new 2, standing 4, resolved 2;
  fixed against base: exit 2, and 0 with `--allow-vacuous`.
- **M2** `docs/how-to/adopt-rules-with-a-baseline.md`: the story, the
  files, a figure (`rule-check-baseline.svg`, a selected view of the head
  graph marked new, standing and resolved), and seven runnable blocks, each
  output taken from a real run: rule ids and remedies; the plain check that
  fails on old violations; the baseline (text and JSON); the fix; vacuous
  acceptance; a CI template; limits.
- **M3** `constraint-reference.md`: a "Rule identity and remedy" section.
- **M4** `docs/reference/rule-check-report.md`: flags, refusals, verdict and
  report fields, the acyclic extent, exit codes with and without
  `--baseline`, text output, `gnd coverage`.
- **M5** three `cli.md` rows, a `formats.md` link, navigation in
  `zensical.toml`, and the runner group `rule-check` in
  `tools/run_tutorials.py` (I3).

## Gate output (verbatim)

V1 at the base 4232d233 (a detached worktree, rerun at record time) and V2
at 0a46d576:

    uv run pytest -q tests/test_documentation_tutorials.py tests/test_plan_app_docs.py -p no:cacheprovider
    V1 4232d233: 160 passed in 95.55s (0:01:35)
    V2 0a46d576: 166 passed in 62.18s (0:01:02)

V3, at 0a46d576:

    uv run python tools/run_tutorials.py --group rule-check
    adopt-rules-with-a-baseline.md: selected executable blocks passed
    7 tutorial blocks passed
    exit=0
    uv run --group docs zensical build --strict
    exit=0
    uv run python tools/check_docs.py site
    15183 local links/assets/anchors checked
    exit=0

V4, the shipped example, at 0a46d576:

    uv run pytest -q tests/test_documentation_tutorials.py -k installed -p no:cacheprovider
    3 passed, 91 deselected in 0.08s
    uv build --wheel  (then unzip -l)
    gnd/examples/rule_check/{README.md, model.orm.yaml, base, head, fixed .population.yaml}

V6, component index: `python3 scripts/components_index.py changed --base
4232d233 --strict` → `20 file(s) differ; 0 to fix, 0 warning(s), 0 to
reread`, exit 0. No module was added.

V1 (main 4232d233) and V5 (8da3b3f7), full default lane, sharded on beast-3
as in the earlier records:

    V1 main 4232d233: 17743 passed, 1 failed, 2 errors; shards exit 0,0,0,1,0,0
    V5 rc6 8da3b3f7:  17749 passed, 1 failed, 2 errors; shards exit 1,0,0,1,0,0
    comm -3:  base only  test_public_session_driver.py::test_driver_kills_the_whole_process_group_on_timeout
              final only test_v51_phase2_extraction_scope.py::test_scope_walk_scales_linearly
    isolated rerun of both at 8da3b3f7, three times: 2 passed each time

The 2 errors are the `tests/test_public_optional.py` uv-version pins, as in
every earlier record. The two single failures are timing tests under the
six-shard load (the session-driver flake was already carried from RC5); RC6
changes no Python file either test reads. The 6 extra passes are the new
page's tutorial cases. The full run is at 8da3b3f7; the review fixes in
0a46d576 change only Markdown and the SVG, which V2 and V3 cover at
0a46d576. Evidence: `evidence/RC6/full-suite-*.txt`.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| completion predicate 6: documented end to end, with a worked example under a named test | V2, V3 | seven blocks, exit codes and output compared by the runner, under `tests/test_documentation_tutorials.py` |
| constraint reference (`remedy`) | M3 | added |
| report reference (version 15) | M4; review | every field, read against the code by the reviewer |
| population format (source) | RC5; M5 link | linked |
| CLI help | RC1, RC3, RC4 pinned successors; M5 rows | unchanged help; index rows added |
| example shipped like the other how-tos (D2) | V4 | in the wheel; installed-docs check passes |
| rendered checkpoint (D4) | spec, Checkpoint | owner: "Looks good, continue" |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only), over
`git diff 4232d233 8da3b3f7 -- docs src tools zensical.toml` read against
the code, disposition `revise`, 15 findings (D1-D15). All fifteen were
checked against the cited code and are accurate. Fourteen are fixed in the
pages (0a46d576); D12 is documented as current behaviour and left as an
open question. Retained verbatim with the triage in
[phase-RC6-codex-review.md](notes/phase-RC6-codex-review.md). The corrected
pages were not re-reviewed, and were committed after the owner's checkpoint.

## Refactoring review

None needed: RC6 changes no source file. The review found the RC1-RC5 code
consistent with itself; every finding was a statement on the pages that did
not match it.

## Boundary: what this phase does NOT establish

- One reviewer read the pages; the corrections were not re-reviewed, and
  the owner's checkpoint saw the pages before them (3f47cf01).
- The runner compares exit codes and the output lines shown on the page,
  not every byte of every report.
- The CI block is a template with placeholder paths; it is not run.
- No business tutorial covers the same workflow (out of scope).
- The broad lanes did not run (`slow_cadence`).

## Open questions

- **Size (plan rule 8).** Measured at 0a46d576 against 4232d233:
  documentation 461 lines (how-to 287, reference 124, figure 40, index rows
  and constraint reference 10), against the 400-line estimate (pause past
  600); example data 237 lines (spec estimate about 80; a third population,
  `fixed`, was added for step 4, and each population lists every component
  in full); tests 0 new lines (the runner's own cases) against 60. Counting
  the example as documentation, the total is 698, past the pause. **Owner
  ruling pending.**
- **D12** (review): the `--allow-vacuous` closing line is printed whenever
  the option is on and a rule is vacuous, even in a run that exits 1.
  Whether to print it only when the option changed the exit code changes
  RC4's approved text (RC4 D3). Target: the owner's ruling; a follow-up
  issue if changed.
- Carried to the milestone close: unused cycle helpers (RC2), index drift,
  the session-driver timing flake (and now the scope-walk timing test, seen
  once under load), RC5 T5 (`model_copy` can bypass the producer
  invariant), and the reference binder dropping `label` (RC5 F2).

## Refuted premises

- The spec's ledger expected the JSON block to exit with its filter's code;
  the runner runs under `pipefail`, so it exits with `gnd`'s 1 (spec I1).
