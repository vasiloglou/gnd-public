---
milestone: why-not-near-misses
station: phase-NM2
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-NM2
date: 2026-11-01
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_disclosure_mode.py tests/test_public_api.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py"
  exit: 0
  output: "892 passed in 58.59s"
  note: >-
    The plan section 9 NM2 row with the files the spec named. The consumer,
    docs-runner, Python 3.11/3.13 RF1 and ruff runs are in the body;
    evidence/NM2/final-gate.txt holds each command and exit.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "every changed path is covered by the selected consumer suites; the broad lane is outside NM2's impact closure"
evidence:
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM2-spec.md
    sha256: 7c950659e2dc509f6ff7e0eceb3c8f06f2dd530801472148ce96616c81a1c616
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM2-claude-review.md
    sha256: 2c504b3f9020a6a3ef64c61fa15b64b021b39b5d51d89b2542c370c4827a3b7b
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM2/final-gate.txt
    sha256: df221c4b2c9d6bc2a417423661d7916f6c45a790d6c26a80841c8ee94cf73ba1
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM2/dynamic-query-successor.json
    sha256: 16a20550809d4acf8d64853c3595eab11c3b9830ba24eb359f6585ec503f8df9
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: 2f191c415aebda1911f67025fa1d91cca9544eaf7d103a44014dc82b2dcfd43d
  - path: src/gnd/disclosure.py
    sha256: d529046c82fb0964fdabbf1e027b1a5c70b3d8cd8b7c64e3bf5952d644118cf2
  - path: src/gnd/cli.py
    sha256: 29f63bad901cb5b32f0b60f7cb10994e7b2e3e62c1502135bb5b346f75921808
  - path: src/gnd/api.py
    sha256: 37b3d8f299e6b3f0f02fa5aa1db38eb3f92490aa217486e6ae157d06fbc7b3ef
  - path: src/gnd/witness/service.py
    sha256: 731e035a0202a8918c2cf68b983f6c1cde20ca67be4fe800585ec64db808793f
  - path: src/gnd/witness/cli.py
    sha256: 62d9f51f18232270af35e399d2d738065a18f199e5af0ebae543945d08d6d477
  - path: src/gnd/export/service.py
    sha256: a531b8ac6b82d8b2b3111b4fdc59f8761725b5c665b1a7672d04814dd280d598
  - path: src/gnd/process.py
    sha256: ce296ecb63b5d421113e3672cc1c230646275a2e37a0b74c290301a92c7ebb0a
  - path: src/gnd/agents.py
    sha256: d7bc6ead5e8f69a902628520b29ac78b2b639b05bb922063aae2005e04b412f1
  - path: src/gnd/declared_adapter.py
    sha256: e90e9b19bbebbf94f53653bcd910a442aef0bb2bc41635b7350f3b3392fd9a22
  - path: src/gnd/exp/session.py
    sha256: 8e85fc33a2566e36bac1f07cbe2bed031f53e7b6eda5252e2175d823d1682b73
  - path: src/gnd/review/adapters.py
    sha256: ea1e960290ccb94a18d1ffb251b79544322fdc0cf9f43d4cafbc90bb02715bd9
  - path: src/gnd/solve.py
    sha256: a0e9cb637edab87094901b6acf60b79940ebcfff2033cdb678c10aeeea4e7595
  - path: tests/test_disclosure_mode.py
    sha256: 6f63abbf23938473c2fade9f7aa9f51bc7eeb15baf589a14b04d1dda1ebecca2
  - path: tests/conftest.py
    sha256: 67afa8f19981a5cdc802e49f956c4121be256bcbc004b4d6b8ddf7734e21e9c1
  - path: tools/gnd_layers.json
    sha256: 7b3be1d64b8bb4c1875bad4d78a60d93877cd32a00488c86f86366542122ef3b
  - path: tools/gnd_entrypoints.json
    sha256: d7c96f4522dccd4de620fa807d0a89492abe8523a77380b899e72750bd395071
  - path: tools/run_tutorials.py
    sha256: 7519a91af8e5d72f15455a99ed0efd699ccc0507e9ba1bf41ce5df4999c61edb
  - path: tests/fixtures/rf1-pins/goldens.sha256
    sha256: d9d5f9d5cbf5940af871e73108601693ac0b49a0815f53021adb5eabd181187d
  - path: tests/test_rf1_pin_harness.py
    sha256: ce6581c11bf40cafb10d03c407bd1a4eae83cdba6d1f7ef89ba9f54d7025ac85
  - path: src/gnd/examples/disclosure/model.orm.yaml
    sha256: c09380b30a38c64927cd53bc359dd930a12087302a23702b249e6dbf7bf54b00
  - path: src/gnd/examples/disclosure/population.json
    sha256: a07f972cbb4a32962d6a76e8a2022da74fe4db13794e54f95615f04979b2d929
---

# Phase NM2 -- the disclosure mode

Spec: [phase-NM2-spec.md](notes/phase-NM2-spec.md), r1, approved by the owner
on 2026-11-01 `(s2)` (SHA-256 `76d594e3…9717` at approval). The rulings were
D1 (b), D2 (a), D3 (a), D4 (a), D5 (a), D6 (a) and D7 (a), with no spec review
panel. The red refusal harness was committed first (`2f96c17`, 29 failing), as
D7 requires. The implementation findings F1–F13 were appended after approval
and carry no review opinion.

## What shipped

- **`src/gnd/disclosure.py`** (new, layer `checking`, 146 lines):
  - `resolve()`: a malformed `GND_DISCLOSURE` is refused, and customer from the
    context or the environment wins.
  - `values_allowed(requested, option)`: the one API decision.
  - `forward()`: what a child receives; only customer is passed on.
  - `invocation(mode)`: sets the context variable and resets the token.
  - `DisclosureRefused(ValueError)`.
  - `SURFACES`: the disclosure table, with every CLI leaf (48), every public
    `gnd.api` callable and `EvaluationSession` method, `gnd.export.service`, and
    the 13 output kinds.
- **`gnd.cli`**:
  - The root option `--disclosure {internal,customer}` (`_StoreOnce`, so a bad
    or repeated value exits 64).
  - One walk after parsing, on disclosure-bearing leaves only, in this order:
    1. a malformed environment is refused;
    2. a loosening option is refused;
    3. under customer, a raw or unredacted dest is refused (exit 3, empty
       stdout, one stderr line);
    4. under internal, every such dest is set to true.
  - The handler runs with the mode set (`_disclosed`, F2). An enclosing
    customer context holds (F13).
- **`gnd.api`**:
  - The public check-family functions call `_values_allowed` first.
  - `check`'s body is now `_check_unresolved`, which `judgments`' internal
    checks and `check_with_feedback` (applied in every mode) call.
  - No public signature changed.
- **`gnd.witness.service`** (D1 (b)):
  - The raw bodies are `witness_result`, `replay_result` and `why_not_result`,
    and the CLI calls those.
  - The public `witness`, `replay` and `why_not` keep their identity, names,
    signatures and docstrings. Under customer they return the value-free view
    or the redacted why-not view.
- **`gnd.export.service`**: the four raw-taking functions resolve `raw`.
- **Children** (D4, D5):
  - `run_bounded_process` and `_result` gain `disclosed_names`; the default
    masks everything, as before.
  - `invoke_agent` gains `extra_environment` and `disclosed_names` (F11).
  - These forward under customer: the legacy session path, the declared
    command adapter (schema v6–v8), the reviewer seats and `solve`.
  - `verifier_environment()` is untouched.
- **Table correction (F10, review R1):** `gnd doccheck` is every-mode.
- **Evidence and maps:**
  - nine current source-successor rows (F3);
  - an RF6 census successor (19 rows, 1 moved);
  - `gnd.disclosure` in the layer map;
  - one entry-point exception (`gnd.cli → gnd.disclosure`);
  - 16 RF1 goldens patched to add the root option (15 copied from a
    three-interpreter capture, plus `cli/tree.json` with one inserted action),
    `goldens.sha256` (16 lines) and `MANIFEST_SHA256`.
- **Isolation:** `tests/conftest.py` pops `GND_DISCLOSURE` at import (F12), and
  `tools/run_tutorials.py` drops it from docs runs.
- **Example:** `src/gnd/examples/disclosure/`, whose email role is declared
  `redact: true`.

Size: 375 source lines added and 17 removed across 14 modules (estimate 330);
`tests/test_disclosure_mode.py` has 848 lines (estimate 650). The difference is
mostly the review regressions.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:cacheprovider tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_disclosure_mode.py tests/test_public_api.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py
892 passed in 58.59s
exit 0
$ uv run pytest -q -p no:cacheprovider tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf2_instrument.py tests/test_agent_cli.py tests/test_review_runner.py tests/test_solve.py tests/test_rf8_sessions.py tests/test_public_tests_mode_corpus.py tests/test_public_local_command_adapter_controls.py tests/test_rf4_peripheral.py tests/test_rf8_structure.py tests/test_rf2_pre_move_pins.py tests/test_public_reference_signatures.py tests/test_v61_phase2_api.py tests/test_public_runtime.py tests/test_public_redaction_reports.py tests/test_public_report_redaction_metadata.py tests/test_v62_phase1_redaction.py tests/test_v62_phase2_redaction.py tests/test_v62_phase3_redaction.py tests/test_v62_phase4_redaction.py tests/test_v62_phase5_redaction.py tests/test_v62_phase6_redaction.py tests/test_v70_phase3_redaction.py tests/test_rf3_core.py tests/test_rf6_moves.py tests/test_public_collection.py
1416 passed, 72 deselected in 108.89s (0:01:48)
exit 0
$ uv run pytest -q -p no:cacheprovider tests/test_documentation_tutorials.py -k quickstart or api
2 passed, 82 deselected in 4.32s
exit 0
$ <scratch>/venv3.11/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py
222 passed in 17.81s
exit 0
$ <scratch>/venv3.13/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_disclosure_mode.py
222 passed in 21.27s
exit 0
$ uv run ruff check src/gnd/disclosure.py src/gnd/cli.py src/gnd/api.py src/gnd/witness src/gnd/export/service.py src/gnd/process.py src/gnd/agents.py src/gnd/declared_adapter.py src/gnd/exp/session.py src/gnd/review/adapters.py src/gnd/solve.py tests/test_disclosure_mode.py tests/conftest.py tools/run_tutorials.py tests/support/pyrel_application_successors.py tests/test_rf1_pin_harness.py
All checks passed!
exit 0
```

The first block was rerun after the census row for `invoke_agent`'s new
annotation (F11) was added. The earlier run of the same command, 2 failed and
890 passed, failed only on that census row.

**RF1 goldens.** Every capture passed: 3.11.15 (scratch venv), 3.13.12 (scratch
venv) and 3.14.3 (project), 363 passed each. The full merged regeneration also
differed in files NM2 does not touch: helper and session pins, the
`--compiled-operations` overlay, and an older session-version message. Those
were left alone. Only the 15 root-usage and root-help files were copied, after
a mechanical check that each differs only in the `--disclosure` usage and help
lines. In `cli/tree.json` only the one root action was inserted.

## Adversarial review

One reviewer is one reviewer. A Claude subagent with repository access, test
runs and a mutation plugin produced
[phase-NM2-claude-review.md](notes/phase-NM2-claude-review.md), with machine
paths sanitized.

- **Findings:** 1 blocking (R1, `doccheck` leaked under customer), 4 hardening
  and 4 completeness.
- **Fixes:** all are fixed except one remainder of R7, the `fidelity` end-to-end
  run, which is deferred. Each fix has a regression test observed red before the
  fix, by a temporary revert or the reviewer's mutant:
  - R1: the value-free row;
  - R2: an extra statement in `witness_result`;
  - R3: `frozenset(extra)`;
  - R4: `mode = option or env`;
  - R5: `internal-callers-resolve` and `judgments-refuses-under-customer`;
  - R6: `validate-`, `transition-` and `diff-ignores-internal`;
  - R7: `discover-follows-mode`.
- **Confirmed true by the reviewer:**
  - every "forwards" path passes customer, and the verifier and the tests runner
    never get it;
  - the refusal order matches the spec, the token resets, and asyncio tasks
    inherit the context;
  - unset child environments, Popen kwargs and goldens are unchanged;
  - no leak on the declared CLI and API sites they ran;
  - the successor digests are correct.

**Own coverage audit against the Refusals table and the spawner table:**

- Every refusal row has a case:
  - T3 and T9 for a malformed variable;
  - T5 and T6 for exit 64;
  - T7, T10 and R4 for loosening;
  - T11 and T16 for raw requests on all 15 dests, plus the API refusals.
- Every spawner rule has a case:
  - "forwards": T30/T31 for the legacy and declared session paths, T32 for
    solve, T33 for reviewers;
  - "never": T34;
  - "unchanged": T28 plus the RF1 pins.
- Not covered end to end:
  - `fidelity` in three modes;
  - real `souffle`/`lake` runs (F8);
  - the leak run for `validate`, `transition` and `judgments` under customer,
    which is covered by the refusal test and the walk test.

## Refactoring review

**None needed**, argued from what NM2 touched:

- **Forwarding sites.** Four sites merge `forward()` into a child environment:
  the session, the declared adapter, the reviewer seats and solve. The decision
  itself lives once, in `forward()`. Each site merges into a different
  structure: a keyword pair, an allowlisted dict, a sanitized seat mapping, and
  Popen keyword arguments. A shared helper would only rename a one-line merge.
  If a fifth spawner appears, that is the trigger to extract one.
- **The per-function check in the API.** It is one identical line calling the
  single helper, which standing rule 4's one-walk requirement allows. A
  decorator would change the bodies pinned by RF4 successors again for no
  behavioural gain.
- **Seen and deferred:** the RF1 golden tree no longer reproduces from a fresh
  capture (the overlays and historical session messages above). That predates
  NM2; it is open question NM2-Q3, for a later maintenance pass.

## Boundary -- what this phase does NOT establish

- **What customer mode protects.** It protects only against requests forwarded
  through `gnd` arguments and `gnd.api` keywords. For code running inside the
  process it is a guard, not a lock (NM-R6). The raw `gnd.witness.service.*_result`
  functions are internal and not in the table.
- **Undeclared values.** Check-family values of undeclared roles are still
  emitted in every mode (NM-D12).
- **Every-mode rows.** Session kinds, `discover`, ILP export, `fidelity` and now
  `doccheck` emit values in every mode, and nothing documents that yet (NM4).
- **Untested paths.** Real `souffle`/`lake` exports under the modes were not
  run (F8). `fidelity` was not run in three modes.
- **Not run.** The broad default suite did not run.
- **One reviewer.** The adversarial review was one reviewer.
- **The why-not near-misses** are still off on every public path; that is NM3.

## Open questions

| ID | Question | Owner |
|---|---|---|
| NM2-Q1 | F10: `doccheck` joins the every-mode list. Confirm that it should stay every-mode rather than become a site. | owner, before NM4 publishes `disclosure.md` |
| NM2-Q2 | A `fidelity` end-to-end run in three modes (review R7 remainder) | milestone close |
| NM2-Q3 | A fresh RF1 capture no longer reproduces the committed goldens outside NM2's files. Rebase the goldens on a fresh capture. | a maintenance pass after this milestone |

## Refuted premises

- **H1–H5** (spec, "Corrections to the plan"):
  - 57 parsers are 48 leaves;
  - RF4 identity pins rule out `gnd.api` wrappers;
  - shared-helper resolution breaks internal callers;
  - the runner masks forwarded values;
  - Python 3.11 was in fact available (F1).
- **The spec's table row for `doccheck`** (F10).
