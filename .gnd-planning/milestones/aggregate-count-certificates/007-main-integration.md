---
milestone: aggregate-count-certificates
station: main-integration
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: main-integration
date: 2026-11-22
gates:
  - command: "uv run pytest -q tests/test_count_certificates.py tests/test_v62_phase4_aggregate.py tests/test_li0_witness_wire.py tests/test_witness_composition.py tests/test_artifacts.py tests/test_rf1_cli_pins.py --tb=short"
    exit: 0
    output: "297 passed in 51.61s"
    note: "AC1's focused lane (295 at AC1); main's include-root-routes added two CLI pin cases"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 102.23s (0:01:42)"
  - command: "uv run pytest -q tests/test_rp5_literature_rules.py tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py tests/test_ir2_flatten.py --tb=short"
    exit: 0
    output: "328 passed, 316 deselected in 37.66s"
    note: "the lanes of the two milestones main gained, default lane only"
  - command: "uv run ruff check src tests tools"
    exit: 0
    output: "All checks passed!"
  - command: "uv run ruff check"
    exit: 1
    output: "Found 198 errors."
    note: "main's known count at 4ad0d216; the merge adds none"
  - command: "python3 scripts/components_index.py --check --strict; python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 0 to reread"
  - command: "uv build --wheel; install into a scratch virtualenv; run the COUNT fixture README commands, and gnd flatten --help"
    exit: 0
    output: "check, witness-count and replay-count (flow and empty groups), witness and replay all exit 0; replay-count reports count 2 for flow"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or CI selection
  reason: the integration changes pins, one inventory delta and generated index lines; no product code
evidence:
  - path: .gnd-planning/milestones/aggregate-count-certificates/evidence/main-integration/dynamic-query-successor.json
    sha256: fc65e04450470357bbb281bc55e7e58014a746e1cecb8d19ff967cd25b5f83bb
  - path: .gnd-planning/milestones/aggregate-count-certificates/evidence/AC1/dynamic-query-successor.json
    sha256: fa91ff3cbff2cfe6d9e903a2c3ac7ff08e21895f6b4a275f70b41e5e18d97a8b
  - path: tests/support/pyrel_application_successors.py
    sha256: b362e5c6c0cbd4a842f81998b6e7936db065fa246dc8732553d049f8dac8b284
  - path: tests/test_rf1_cli_pins.py
    sha256: 6ce6321e1de6b539b3800284909c64ea5c7bfc7082100b03ac1d860f02f2d065
  - path: tests/test_rf5_commands.py
    sha256: d60ebb3e24d55f6bf4d17764b02b015fa4c636408a4bd5ea82c7f0b9c3c35e4f
  - path: tests/test_disclosure_mode.py
    sha256: fe2a0bf99768bc5e80b5a32e38c58b29268d7fdc3dc30466de23afbbcfc1e230
  - path: dev/components/COMPONENTS.md
    sha256: 6d11355ebd0865ab60b68a25286e8f63c1f33612138abbdf0708fc2bf2b7b79d
  - path: dev/components/graph.md
    sha256: d7bcd48a9eb6b10dab2fb3bb0f2333217d40df898a14b50cd988e779a03d046e
  - path: dev/components/modules/commands.md
    sha256: 91aa0603f897e058b3e3a36d69144a492f43f77e342cd4156c04cfc43c2245bc
  - path: dev/components/modules/export.md
    sha256: 34d782a51543a88ea2f0ca145374b5a2fa274b3fd35d7670a5f52ef7e242f7ab
---

# Claim

`codex/aggregate-count-certificates` integrates `main` at `4ad0d216`, which
gained include-root-routes (PR 220) and pyrel-rules-coverage (PR 223, 224)
after this branch was cut at `a7785ffb`. No product code changed in the
integration. The merged tree passes AC1's focused lane, the guard block,
the two newer milestones' default lanes and the installed-wheel smoke.

## What the integration resolved

- **CLI pins.** Both sides added CLI leaves: `gnd flatten` on main, and
  `gnd witness-count` and `gnd replay-count` here.
  - The parser count is 64, the disclosure table has 55 `gnd` keys, and the
    value-free check covers 55 - 18 - 4 paths.
  - The COUNT tree successor now builds on the root that already lists
    `flatten`.
  - The root-usage probes for `gnd doctor`, `gnd install` and
    `gnd uninstall` carry both changes.
- **RF6 dynamic-query inventory.** AC1's successor and pyrel-rules-coverage's
  first successor both named the same predecessor. AC1's 13-row delta is
  re-chained after `pyrel-rules-coverage/evidence/close` as
  `evidence/main-integration/dynamic-query-successor.json`. The recomputed
  delta equals AC1's row for row. AC1's own file is unchanged, because
  AC1's review brief cites it by digest, and it is no longer in the chain.
- **Component index.** The conflicting `used_by` lines are generated; the
  index was regenerated. That also refreshed two module pages
  (`commands.md`, `export.md`) whose line numbers had gone stale on main
  with PR 223.

## Authority

The owner asked on 2026-11-22, in the session that merged PR 223, to fix
this pull request's conflicts and merge it. That request is the merge
decision. The integration was done by a different assistant than the one
that ran the milestone; it adds no review of AC1's product code.

## Boundary — what this integration does NOT establish

- AC1's review, close panel and close ruling describe the bytes before this
  merge. Nothing here re-reviews them.
- The `pyrel_oracle` lane and the broad `evidence or census` lanes were not
  rerun: the integration touches no code those lanes execute.
