---
milestone: derivation-why-not
station: phase-WN2
skill: "n/a -- repository development via process-phase under process-milestone auto=true, not a gnd-solve station over a domain model"
scope: phase-WN2
date: 2026-10-30
gate:
  command: "uv run pytest -q -p no:cacheprovider <the WN1 gate files> tests/test_public_why_not.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_reference_signatures.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_documentation_tutorials.py tests/test_public_acceptance_runner.py"
  exit: 0
  output: "2379 passed, 33 deselected in 951.93s (0:15:51)"
  note: >-
    The plan §9 WN2 gate plus tests/test_rf1_pin_harness.py, whose manifest
    digest WN2 moves. The python-api tutorial group ran separately with
    tools/run_tutorials.py --group api: 9 tutorial blocks passed. The RF1 CLI
    pins and harness also ran under Python 3.11 and 3.13 scratch environments:
    156 passed each. Ruff check is clean over the changed files.
slow_cadence:
  command: "uv run pytest -q tests/test_public_built_inventory.py tests/test_public_runtime.py"
  trigger: "explicit owner selection"
  reason: "distribution lanes (plan §9); their pin edits (VENDORED_SCHEMAS, the runtime __all__ tuple) are not executed here"
evidence:
  - path: .gnd-planning/milestones/derivation-why-not/notes/phase-WN2-spec.md
    sha256: 1613a7bc30c33d2cfaea210750efa2388c6fb85807630715eb7d0006ca33a6de
  - path: .gnd-planning/milestones/derivation-why-not/notes/phase-WN2-claude-review.md
    sha256: 72b7a6f1f2fc685b7d5e0c4787c6113b9b9b4870db1542443331ed61da63ca21
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN2/build_inputs.py
    sha256: 703117cc8746a80d98b7cb8b7be796892ca018cc6537a1ae9f92341ee8baf541
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN2/build_goldens.py
    sha256: b37cf9440de40fa04256cc1f5b92296b581cd18cff0b3e1cdc8221e778615a8d
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN2/corpus-red.txt
    sha256: 9de8e6c7203695de1a35686b8a3f8889255ebe5d197cc2ccdd451ed920fc687a
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN2/dynamic-query-successor.json
    sha256: 3e2fb1d020c734aa1297db57725aeae0caae67b4f6831afa0087654ee2062754
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN2/final-gate.txt
    sha256: 214114cc0934d84bf57e8324e3196f4aa0bc3117f0c048986dba17f1d7d8a869
  - path: src/gnd/why-not.schema.json
    sha256: 8df1cbf99d6f1682dada527cd5e809f05d351ae1c5665978a69286333c68c3be
  - path: src/gnd/witness/service.py
    sha256: efd0362f38a19d23427aa8c90ae7315a0d18a64db6001b5a7631d0b29822f82e
  - path: src/gnd/witness/view.py
    sha256: 24be1af6695ad3624dcaa852d7bec102259f0ef4d69b90b0279f645d35c41ec5
  - path: src/gnd/witness/cli.py
    sha256: 5ebd0512260a83d8b71b42b50020a2bb8295c9c3a3af2964d9d06ea852269033
  - path: tests/test_public_why_not.py
    sha256: 921e235f862e1f68973185bd246a75ace21859762c5b64ea59139d350d1be7c0
  - path: tests/fixtures/why_not/cases.json
    sha256: c8b2223a791b6250f7f35a7a1031d8f363404fd91b71e8aa86a9fbd6074fecc3
  - path: docs/reference/why-not.md
    sha256: dab632f0bcdad9baf206af10fae0d8015ac44f798afc2fd32d127b21109d3fe5
---

# Phase WN2 -- `gnd why-not`, `gnd.api.why_not`, schema, pins and docs

Spec: [phase-WN2-spec.md](notes/phase-WN2-spec.md), r1, with its gate recorded
as a **delegated approval (auto=true)** under the owner's
`/process-milestone derivation-why-not auto` request (SHA-256 `8665b031…9e27`,
sweep S1-S7). Per WN-D10 the corpus went in first and red: commit `f456930`,
43 failed and 1 passed before any WN2 code (`evidence/WN2/corpus-red.txt`).

## What shipped

- **`gnd why-not MODEL POPULATION --fact-type ID [--row REQUEST]
  [--reference-root DIR] [--raw]`** and **`gnd.api.why_not(model_path,
  population_path, fact_type, *, row_path=None, reference_root=None)`**,
  through the witness input lane (`src/gnd/witness/service.py`). The row file
  is a witness request holding exactly one target for `--fact-type`. Inputs
  are re-read through `intake` under `_why_not_intake_limits()`, the why-not
  ceilings projected onto `WitnessLimits` with `targets=1`.
- **Envelope `gnd-why-not/1`** with `status` `blocked`/`derived` (exit 0),
  `unsupported` (2), `refused` input-invalid (3), `unavailable` or `refused`
  work-limit (4).
- **Redacted view** (`src/gnd/witness/view.py`, `why_not_view`): a closed
  selection by key name. Samples, constant roles and unavailable bindings read
  `"redacted"`. The CLI adds `view: redacted|raw`.
- **Schema** `src/gnd/why-not.schema.json`, vendored. After review it pins
  each band to its status and reason, and ties `view: redacted` to redacted
  fields.
- **Pins:** the twelve-name `__all__` in three literals and the runtime probe
  (WN-D13); `why_not` signature assertions; `EXPECTED_PARSERS` 57; RF1 goldens
  (tree, root help and exit for three Pythons, install/doctor/uninstall exits,
  new why-not help and exit), `goldens.sha256` and `MANIFEST_SHA256`; an rf5
  handler case and answer; `VENDORED_SCHEMAS`; an RF6 successor
  (`evidence/WN2/dynamic-query-successor.json`, 2 rows, chain totals 6802 and
  8507).
- **Docs:** `docs/reference/why-not.md` (now the normative home of the step
  and blocker definition; the kernel docstring points there), a nav entry, a
  `python-api.md` section with a runnable block over the dispatch example,
  `cli.md` row and exit sentence, a `capabilities.md` row, and a release note.
  The API count lives only in `python-api.md` ("nine functions"); `tour.md`,
  `cli.md`, `bookrec/06-evolution.md` and `runtimes/decision.md` no longer
  state a number.

## Gate output (verbatim)

```
2379 passed, 33 deselected in 951.93s (0:15:51)
```

## Criteria

| Criterion | Result |
|---|---|
| WN2-C1 command and API through the witness lane; projection; hostile inputs | holds: T1 over 21 cases in both views and through the API; T3 projection; G10-G13; the intake ceilings pinned directly on both sides of each limit; the service runs intake under the projected limits; the reviewer's 24 hostile probes and 500 mutations gave no escaping exception |
| WN2-C2 schema, closed view, leak test | holds: T2 validates every golden and API payload and refuses 11 contract violations; T4 finds no fixture, reference, row or rule-constant value in any redacted output; T8 closed selection |
| WN2-C3 pins | holds: the pin files pass under Python 3.14, and the RF1 pins under 3.11 and 3.13; the distribution lanes are `slow_cadence` |
| WN2-C4 docs | holds: the route probe, the api tutorial group, the single count |
| WN2-C5 check and witness unchanged | holds: the witness corpus and the check-contract files of the WN1 gate pass unchanged |
| WN2-C6 counted bounds | holds: T8 target intake stops at the count check before any shape check; view visits each of 50 clauses once |

## Review

One local reviewer agent read the diff from `26e36c8` and ran 8 probes under
scratch. Its report is kept as
[phase-WN2-claude-review.md](notes/phase-WN2-claude-review.md). It found no
blocking defect.

| Finding | Severity | Disposition |
|---|---|---|
| WN2-R1 schema does not pin band/reason pairs or the redacted view | hardening | fixed; 11 refusal cases, red on the pre-fix schema (11 failed), green after |
| WN2-R2 the nan and deep G12 cases are refused by the loaders, not intake | hardening | fixed: ceilings pinned on `validate_witness_structure` under the projected limits with controls; a test pins that the service passes those limits; G12 says the loaders refuse first |
| WN2-R3 no constant-role, negated, comparison or head blocker in the corpus | hardening | fixed: cases G14-G18 in both views; rule constants join the leak set. The review's constant-copying mutant passed 44 before and fails 2 after |
| WN2-R4 two pages still state an API count | completeness | fixed: both now link the reference without a number |

## Refactoring review

**Executed:** the redacted view iterates the blocker's items instead of
subscripting `roles` by name, which also keeps it clear of the RF6 direct-read
policy (a why-not payload is not a model).

**Not refactored, argued:**
- **The envelope is built in the service, not the kernel.** The kernel's
  `WhyNotResult` stays a domain value without exit codes, as WN1 shipped it;
  only the service knows bands.
- **`_witness_inputs` is reused unchanged** and `intake` re-reads its output, as
  `produce_witness` does. A why-not-specific loader would duplicate it.

## Boundary -- what this phase does NOT establish

- **One reviewer is one reviewer.** The review covered the pre-fix tree; the
  R1-R4 fixes and their tests carry no review opinion.
- **The distribution lanes did not run** (`test_public_built_inventory.py`,
  `test_public_runtime.py`). Their edits are one schema name and the
  twelve-name tuple.
- **The docs site was not built** in WN2; WN3's gate builds it.
- **The depth-64 intake ceiling is not reachable from files**: the loaders
  refuse shallower nesting first. It is pinned in code only (WN2-R2).
- **The goldens' clause bodies come from the WN1 kernel.** The envelope and
  the redaction in them were written independently in
  `evidence/WN2/build_goldens.py`, before the service existed.

## Open questions

| ID | Question | Origin | Target |
|---|---|---|---|
| WN2-Q1 | Spec §4 rule 3 lists the row file after the model; the service reads it first. Same exits; amend the wording? | review | derivation-why-not close |

## Implementation findings

- **WN2-F1.** The leak scan first read row files' `fact_type` and `primitive`
  strings as population values; only cell values are. Test fixed before the
  first green run.
- **WN2-F2.** The RF1 tree golden keeps historical bytes, and the test inserts
  the `--compiled-operations` successor itself. The why-not tree golden is the
  plain capture minus that action. The capture tool's merged tree also differs
  in environment-dependent helper goldens, which were left alone.
- **WN2-F3.** Spec §6.7 named only `tour.md` and `cli.md` for the stale API
  count; two more pages carried it (WN2-R4).
