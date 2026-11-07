---
milestone: rule-check-adoption
station: phase-RC3
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RC3
date: 2026-11-06
gate:
  command: "uv run pytest -q tests/test_rc3_baseline.py tests/test_rc2_acyclic_extent.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider"
  exit: 0
  output: "124 passed"
  note: >-
    The plan section 9 RC3 row (V2), at a7cdbd2e. The impact closure (V4),
    lint (V5), the component index check (V6) and the sharded full default
    suite against main eac81cf8 (V1/V3) are in the body.
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "RC3 changes no historical artifact; the full default suite and the guard suites cover the changed paths"
evidence:
  - path: src/gnd/baseline.py
    sha256: d7e6fcc580d57815efdb1303221c879babc4597289cfea6f837ae5ce610e47d8
  - path: src/gnd/checker/_reports.py
    sha256: 9f468837142f53c03e2d6a4370d30cf35a93fad27b358ec0411acf2e0b8d1071
  - path: src/gnd/checking_service.py
    sha256: d4175bee9f044361b3ec90eec24bed6214cd274a7763d5ce4c4fe5b6721e108c
  - path: src/gnd/payloads.py
    sha256: 06d1458711a0535cc75f11cb8560d188688b21e5a1973bf5b721e105a30e2e3d
  - path: src/gnd/output.py
    sha256: 0862644a23870a37cff13a1e570d873a8f8f98d02b1e47b5a7c5f5cf0cf515b6
  - path: src/gnd/commands/checking.py
    sha256: 30ac9ba6536f414706f494d53ae8b07e4022b2c0a1bbbcc91e91ff506d01b4a9
  - path: src/gnd/commands/_output.py
    sha256: f5d3c9760dc2db065eae514eb00e2182043e4bd09677db4014f130512dfe27f4
  - path: src/gnd/population.py
    sha256: 729531a2f732a3ad41b6193288dbbe830bf77030d228061e6e65565700754325
  - path: tools/gnd_layers.json
    sha256: be5a7e9218016ee6adee63afe3b7d51d0e98226b44717bf5e5ac0a05ebb18ebb
  - path: tests/test_rc3_baseline.py
    sha256: 217ec17e09bd9b40cdfb01c65219e118778005fc18703f69754169729bd6da99
  - path: tests/test_rf1_cli_pins.py
    sha256: a790934d11f3a819aca76546d5be67e253bb6b3d79a8ebeaedc6d31bf287214d
  - path: tests/fixtures/baseline-cli/expected.json
    sha256: c5efb232bd5ad9e39cc2adf434bcd6c518f4b56269dfa5eca54adbea911423ac
  - path: tests/fixtures/rc3-baseline/README.md
    sha256: 2dcd4c4db3aa5d79311af45b66e70a6cc15aad816529290a4f8ee9594a335ba0
  - path: tests/fixtures/rc3-baseline/expected/README.md
    sha256: 554988d022651cd075678d170df6a469d747a6d89f5dc9f959e95a0e85c9788e
  - path: tests/fixtures/rc3-baseline/expected/mixed.json
    sha256: 8e7f702bf7fe8d1d83c398f25780b98301a9d650d2691b53350d9205e49fbed3
  - path: tests/fixtures/rc3-baseline/expected/mixed.txt
    sha256: 21cbf0a77b05732f091c7680bfba7b4595035e2206c32598ef145df046ab8ef4
  - path: tests/fixtures/rc3-baseline/expected/standing-only.json
    sha256: ac065541d4d5f5fffb38f3c943003e5a76622a9f77f95b2cfadf182a5bb1da22
  - path: tests/fixtures/rc3-baseline/expected/refusals.json
    sha256: 7f39e26c28ed26bf079455bc78a5364ff030ff8d14e49b6e6f64d68ab8842a0b
  - path: tests/fixtures/rc3-baseline/expected/exits.json
    sha256: b4acf0dc5c21620794d8ae9b4aa023839f33a6d4ec88a2385505463d9c284309
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: 279814be3f862a653310ba9a748a2ea56bf769b9d54c15fe3cebf15bd638d5ae
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC3/dynamic-query-successor.json
    sha256: 06b84d2900eadc39a9edb07bdddb15f05ab127c41d459d4799fff3bda4d12417
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC3/full-suite-main-eac81cf8.txt
    sha256: cf38f42df61960d506dfe2856067cf68ae12729175a0e684f5642305be83cc91
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC3/full-suite-rc3-a7cdbd2e.txt
    sha256: 0dba23116432fca21552908e75b8a1aae6554f7252e13aafeae0233e309e8f87
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC3-spec.md
    sha256: 278c2f4e56156abdb187927934e180ef4c314cf0ced90fd0642b1532cb626058
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC3-codex-review.md
    sha256: c4b5c87a5cc77eb1631f767eef2afba096cbc7c943da7f0aa41ee05fd2acce76
  - path: dev/components/COMPONENTS.md
    sha256: f8bb0596470fe836035a0850900de6fdc83785c6f66b624e90077ecb91ef06cb
---

# Claim

At a7cdbd2e, `gnd check MODEL HEAD --baseline BASE` judges both
populations under MODEL, marks each failing verdict and offending row `new`
or `standing`, counts resolved rows, and takes its exit band from new
violations only, refusing "no new violations" when either run leaves a
must-hold rule undecided, as the owner-approved corpus specifies. The
focused gate V2 exited 0, the impact closure V4 exited 0 (5148 passed over
88 files), and the sharded full default suite adds no failure to main
eac81cf8.

## What shipped

- **M1** `band(report, baseline=None)`: with a comparison, 1 from new alethic
  failures, else 4 from an alethic verdict unchecked in either run, else 2
  from the head's vacuous verdicts, else 0; without it unchanged. Still the
  one band implementation.
- **M2** `src/gnd/baseline.py` (layer `checking`; component `check.baseline`):
  `baseline_key` (rule address plus canonical JSON of the row, values
  compared by identity; a row-less failure keyed by its address) and
  `compare` (novelty, row novelty, the five counts, the band's two inputs).
- **M3** service: `--baseline` implies `--rule-ids`; structured-derivation
  models refused `check:baseline-unsupported` after the RC1 refusal and before
  either population; the base read once (`population.read_population_bytes`,
  split unchanged out of `load_population`), digested and loaded; base issues
  and warnings named `baseline:`; the base checked with the same evaluator and
  RC2 extents; a failing base evaluation returns exit 70.
- **M4** payload: `novelty`, `row_novelty` and the `baseline` block filled;
  exit, outcome and `acceptance_ready` follow the baseline band.
- **M5** assurance under `--baseline`: the uncertified block for the baseline
  band (D5).
- **M6** CLI `--baseline BASE` (conflicts exit 64); text marks `[fail, new]` /
  `[fail, standing]` and prints a `BASELINE` summary with the RC-D9 warning.
  CLI help successor `tests/fixtures/baseline-cli/expected.json` (one added
  option, diff checked).
- Guard bookkeeping: RF4 rows `_run_check_raw`, `_run_check`,
  `build_check_payload`; RF5 rows `_cmd_check`, `_print_report`; RF6b row
  `band`; RC3 dynamic query delta (static policy unchanged).

## Gate output (verbatim)

V1, focused, at the base eac81cf8 before any source edit:

    uv run pytest -q tests/test_rc2_acyclic_extent.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider
    96 passed in 8.07s
    V1 exit=0

V2, focused gate (plan §9 row), at a7cdbd2e:

    uv run pytest -q tests/test_rc3_baseline.py tests/test_rc2_acyclic_extent.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider
    124 passed in 11.27s
    V2 exit=0

V4, impact closure, at a7cdbd2e: RC2's V4 list plus `tests/test_rf1_cli_pins.py`,
`tests/test_v6_phase6_report.py`, `tests/test_public_branch_runtime.py`,
`tests/test_v6_phase2_registry.py`, every test file that calls `band(` and the
population-loader tests (89 files; the exact list is the sorted union in the
command below, built by `grep -l "band(" tests/test_*.py` and
`ls tests/test_*population*.py tests/test_popvalidate*.py`):

    uv run pytest -q tests/test_rc3_baseline.py <the 88 files> --tb=line -p no:cacheprovider
    5148 passed, 215 deselected in 335.33s (0:05:35)
    V4 exit=0

V5, lint, at a7cdbd2e:

    uv run ruff check <the Python files changed since eac81cf8>
    All checks passed!

V6, component index, at a7cdbd2e:

    python3 scripts/components_index.py changed --base eac81cf8 --strict
    changed against eac81cf8 (eac81cf): 48 file(s) differ; 0 to fix, 0 warning(s), 6 to reread

Edited with the code: `check.baseline` (new), and search verbs on
`checker.reports` and `model.population_loading`. The 6 reread entries
(`subsystem.check`, `infra.output`, `cli.checking_command`, `check.service`,
`infra.report_payloads`, `infra.text_output`) were read beside the diff and
still describe their code.

V1 (main eac81cf8) and V3 (a7cdbd2e), full default lane, sharded on
beast-3, same layout and setup as RC2's record (6 round-robin shards, each in
its own clone, `uv sync --locked --group dev`, `uv run gnd install --symlink
--project --force`, `~/.local/bin` on PATH):

    V1 main eac81cf8: 17637 passed, 1 failed, 2 errors; shards exit 0,0,0,1,0,0
    V3 rc3 a7cdbd2e:  17666 passed, 2 errors; shards exit 0,0,0,1,0,0
    comm -13 (only in V3): empty
    comm -23 (only in V1): tests/test_public_session_driver.py::test_driver_kills_the_whole_process_group_on_timeout
    sha256 of the sorted failing-id lists: V1 76a2cba1…6d21b, V3 8261732b…9c20a

The 2 errors on both sides are the `tests/test_public_optional.py` uv-version
pins RC2's record names (V3's list is byte-identical to RC2's). The
session-driver timeout failed only on main, under load; it failed once before
in RC2's first run and passed locally both times. The 29 extra passes are
RC3's 28 tests and that test. Per-shard summaries and lists:
`evidence/RC3/full-suite-*.txt`. A first full run at 4fffa84d was stopped
after the review fixes landed; it is superseded, not reported.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| RC3-C1 | corpus `mixed`; T1 | standing, new and resolved as the oracle says |
| RC3-C2 | corpus `standing-only` | exit 0, `accepted`, `acceptance_ready: true`, standing counted |
| RC3-C3a | corpus `refuse-temporal` | exit 3 `check:rule-ids-unsupported`, no population read |
| RC3-C3b | corpus `refuse-derivation`; RC1's `derivation-plain` still green | exit 3 `check:baseline-unsupported`, no population read; `--rule-ids` alone accepted |
| RC3-C3 | corpus `bad-base`, `base-unchecked`; T5; B2 | base named; exit 4 (1 with a new alethic failure); `undecided` counted |
| RC3-C4a | T6; B1 | keys survive reordering, unrelated facts, and a number's spelling |
| RC3-C4b | T7; corpus `text-mixed` | declared key stable, positional key moves, warning printed |
| RC3-C5 | T8; T9 | order pinned; 2,000 rows a side well under 0.5 s |
| RC3-C6 | corpus `rowless-new`, `mixed`, `standing-only` | as specified |
| harvest | spec §6 survey; T10 | rows are values only; rule 8 did not fire |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only), over
`git diff eac81cf8 4fffa84d -- src tests tools`, disposition `revise`, 3
findings, all reproduced and fixed with regressions observed red: B1 (one
number spelled `1` and `1.0` counted new and resolved), B2 (base warnings
dropped), B3 (a failing base evaluation raised). Retained verbatim with the
triage in [phase-RC3-codex-review.md](notes/phase-RC3-codex-review.md). The
fixes (a7cdbd2e) were not re-reviewed.

## Refactoring review

Refactors EXECUTED (behind V2, V4 and V3):
- `population.read_population_bytes` split unchanged out of `load_population`,
  so the base is read once and digested over the parsed bytes.
- `checking_service._baseline_named`: one helper names the base's issues and
  warnings.

None further needed: the comparison is one new module with one key function,
and the band stays one function with one optional argument.

## Boundary: what this phase does NOT establish

- One reviewer read the diff; the fixes were not re-reviewed.
- The base is judged under the head's MODEL; a base written for an older
  model revision is compared only through declared ids (positional keys
  move, with the warning).
- A reported row still shows the spelling the checker projected (for
  example `1.0`); only the comparison is by identity.
- `--allow-vacuous` is RC4's: a head-vacuous run exits 2 here.
- The broad lanes did not run (`slow_cadence`); two host-environment errors
  are present on both sides of V1/V3.
- No live caller ran against this build.

## Open questions

- **Unused cycle helpers** in `checker/_core.py` (RC2 F2) and **component
  index drift** (RC2 I5) carry forward. Target: milestone close.
- **Session-driver timeout flake** under parallel load on beast-3 (seen at
  RC2's cbcd0e86 and RC3's main base). Target: its own issue if it recurs at
  close.

## Refuted premises

- Plan §3 put the baseline comparison under `src/gnd/checker/`; a guard
  pins that package to four files, so it lives at `src/gnd/baseline.py`
  (spec I1).
