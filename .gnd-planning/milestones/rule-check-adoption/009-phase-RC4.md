---
milestone: rule-check-adoption
station: phase-RC4
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RC4
date: 2026-11-06
gate:
  command: "uv run pytest -q tests/test_rc4_allow_vacuous.py tests/test_rc3_baseline.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider"
  exit: 0
  output: "150 passed"
  note: >-
    The plan section 9 RC4 row (V2), at d8519b04. The impact closure (V4),
    lint (V5), the component index check (V6) and the sharded full default
    suite against main 4713fc8a (V1/V3) are in the body.
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "RC4 changes no historical artifact; the full default suite and the guard suites cover the changed paths"
evidence:
  - path: src/gnd/checker/_reports.py
    sha256: 6c9a3ae8dd4e65e78594cd3be1074793490f75432002602f4366d5550e6b6714
  - path: src/gnd/checking_service.py
    sha256: dbfe523bf1eb7c98faea55d985bb7c82aa66817bb8d8d940413671dda4dd1a44
  - path: src/gnd/payloads.py
    sha256: eebd9968cabcd65953c14cb5d402cd2c597fc3446201437dccc567e06fc8bc80
  - path: src/gnd/output.py
    sha256: eadcd0538d6488aee7469112ed9d5a209ac212732373fec756b9488a9333737f
  - path: src/gnd/commands/checking.py
    sha256: 2ca0404014f6f6fdd0c633aad942267cfe4feee53f1fa7bd8a4585c12eb9797c
  - path: src/gnd/commands/_output.py
    sha256: ebdad506d5cf996eca662e2eef2ece2ea9a61dab361eb8b226f059ff0182b75f
  - path: tests/test_rc4_allow_vacuous.py
    sha256: 8a338bcddf1a67928a3e14040e0122db9974b09ffaed6822aa8eb05402bfa883
  - path: tests/test_rf1_cli_pins.py
    sha256: 7a8af8b356d7d92170357edec5a4b9c495c074ff359fc420c98ae9fd7f579595
  - path: tests/fixtures/allow-vacuous-cli/expected.json
    sha256: a1a7a9d7bb18aa22479d5c535773e479a4badc43f279ebde3f81230d6146870e
  - path: tests/fixtures/rc4-allow-vacuous/README.md
    sha256: b3669b98754eb907e2d481beaf115bbcb7b56629a6da00c7419724ec5272f691
  - path: tests/fixtures/rc4-allow-vacuous/expected/README.md
    sha256: 26812c180fdd6bb339167ac4c75431c56823796fe2c45015b80fdf261f4e7682
  - path: tests/fixtures/rc4-allow-vacuous/expected/vacuous-only.json
    sha256: 3841adb4643298ba2fe69da10207ec80cd38bd2a0073c2a757930927f40e1195
  - path: tests/fixtures/rc4-allow-vacuous/expected/vacuous-only.txt
    sha256: 4f125c36cc37b40812d9e771d9b1229555b4872c53b9328ee6dd6a0b2e2f5e36
  - path: tests/fixtures/rc4-allow-vacuous/expected/exits.json
    sha256: 1c83a95c9c67af7a27e22432a2a48f46299d4a49a8d09ea44e1c76117f34db77
  - path: .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/source-successors.json
    sha256: 35cdc2b02c7c27f9783af972d587a3a8c12877617fdbfa39dc5d63088a4049ce
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC4/dynamic-query-successor.json
    sha256: be6078874045ab7eba331410fc763cfa52d65065d3b060a213b9f45a7195e2c7
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC4/full-suite-main-4713fc8a.txt
    sha256: 6e41f522bd97319dc606cd8395e74090fbe60712e5ef80820a1def383e757fd8
  - path: .gnd-planning/milestones/rule-check-adoption/evidence/RC4/full-suite-rc4-745507dc.txt
    sha256: 9b7abb71e5e5c7eb2c0ad2d6f509ec63614fcbf0ce77cb21c443fd4a38991ebf
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC4-spec.md
    sha256: e517d9e9416a73348f15fbf2750e35b172d0c49f15ebf3e74a83789f15306be6
  - path: .gnd-planning/milestones/rule-check-adoption/notes/phase-RC4-codex-review.md
    sha256: 6f26fc7dd00a7d306db4b1a556d7608c814e56704432a74dbecbc4770cccdd06
---

# Claim

At 745507dc (code) and d8519b04 (tests), `gnd check ... --allow-vacuous`
exits 0 when vacuous rules are the only shortfall, still lists them, and
records `allow_vacuous: true` in version 15, alone or with `--baseline`,
as the owner-approved corpus specifies; a failure or an undecided must-hold
rule still decides the band. V2 exited 0 (150 passed), V4 exited 0 (5178
passed), and the sharded full default suite adds no failure to main 4713fc8a.

## What shipped

- **M1** `band(report, baseline=None, allow_vacuous=False)`: a computed 2
  becomes 0, after the branch events are recorded; still the one band
  implementation.
- **M2** service: `allow_vacuous` implies `rule_ids`, reaches `band()` on the
  plain and baseline routes, and gives an uncertified assurance block when it
  accepted a vacuous run (D2).
- **M3** payload: `allow_vacuous` set from the option in version 15.
- **M4** CLI `--allow-vacuous` (joins the `--rule-ids` conflict set) and the
  text closing line `vacuous accepted: N rules have nothing to judge yet
  (--allow-vacuous).` (D3, wording as approved). CLI help successor
  `tests/fixtures/allow-vacuous-cli/expected.json` (one added option).
- Guard rows: RF4 `_run_check_raw`, `_run_check`, `build_check_payload`; RF5
  `_cmd_check`; RF6b `band` extended; RC4 dynamic query delta (one
  annotation).

## Gate output (verbatim)

V1, focused, at the base 4713fc8a before any source edit:

    uv run pytest -q tests/test_rc3_baseline.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider
    98 passed in 6.34s
    V1 exit=0

V2, focused gate (plan §9 row), at d8519b04:

    uv run pytest -q tests/test_rc4_allow_vacuous.py tests/test_rc3_baseline.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider
    150 passed in 10.31s

V4, impact closure, at 745507dc: RC3's 89-file list (guards, every `band(`
caller, population-loader tests) plus the RC4 tests:

    uv run pytest -q tests/test_rc4_allow_vacuous.py tests/test_rc3_baseline.py <the 88 files> --tb=line -p no:cacheprovider
    5178 passed, 215 deselected in 338.00s (0:05:38)
    V4 exit=0

V5, lint, at d8519b04:

    uv run ruff check <the Python files changed since 4713fc8a>
    All checks passed!

V6, component index, at 745507dc:

    python3 scripts/components_index.py changed --base 4713fc8a --strict
    changed against 4713fc8a (4713fc8): 36 file(s) differ; 0 to fix, 0 warning(s), 5 to reread

Edited with the code: search verbs on `checker.reports` and
`infra.text_output`. The 5 reread entries (the check subsystem, CLI, service,
payload and output-shim entries) were read beside the diff and still describe
their code.

V1 (main 4713fc8a) and V3 (745507dc), full default lane, sharded on beast-3
as in RC2's and RC3's records:

    V1 main 4713fc8a: 17665 passed, 1 failed, 2 errors; shards exit 0,0,0,1,0,0
    V3 rc4 745507dc:  17696 passed, 2 errors; shards exit 0,0,0,1,0,0
    comm -13 (only in V3): empty
    comm -23 (only in V1): tests/test_public_session_driver.py::test_driver_kills_the_whole_process_group_on_timeout
    sha256 of the sorted failing-id lists: V1 76a2cba1…6d21b, V3 8261732b…9c20a

The 2 errors are the `tests/test_public_optional.py` uv-version pins (V3's
list is byte-identical to RC2's and RC3's). The session-driver timeout
failed on main only, under load, as in RC3's record. d8519b04 changed tests
only, so V3 covers the final code. Evidence: `evidence/RC4/full-suite-*.txt`.

## Criteria

| Criterion | Evidence | Result |
|---|---|---|
| RC4-C1 | corpus `vacuous-only`, `vacuous-only-plain` | 0 with the option, 2 without |
| RC4-C2 | corpus `fail-and-vacuous`, `unchecked-and-vacuous`; T1 (35 cases) | 1 and 4 stand; only a 2 changes |
| RC4-C3 | every golden; T3 (clean and failing runs) | `allow_vacuous` recorded; vacuous verdicts listed; no other byte changes |
| RC4-C4 | corpus `baseline-head-vacuous`, `baseline-base-vacuous`; RC3's `head-vacuous` still 2 | 0 with the option; base rows resolved or none |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only), over
`git diff 4713fc8a 745507dc -- src tests tools`, disposition `revise`, 2
findings, both test gaps (no defect): V1 (T3's input was not clean) and V2
(T1's baseline flags tied to the head). Both closed in d8519b04; the
strengthened T1 fails 9 cases against a mutant that also clears band 4.
Retained verbatim with the triage in
[phase-RC4-codex-review.md](notes/phase-RC4-codex-review.md). The test
changes were not re-reviewed.

## Refactoring review

None needed: RC4 adds one argument to `band()` and one key to the payload,
along the routes RC3 already gave a single home (the uncertified assurance
route, the `commands/_output.py` binding list, the CLI conflict set). No
duplication was introduced or found in the touched code.

## Boundary: what this phase does NOT establish

- One reviewer read the diff; the test changes were not re-reviewed.
- The option is run-wide; per-rule vacuous control is out of scope (RC-D7).
- The closing line keeps the approved wording ("1 rules").
- The broad lanes did not run (`slow_cadence`).
- No live caller ran against this build.

## Open questions

- Carried: unused cycle helpers (RC2 F2), component index drift (RC2 I5),
  the session-driver timeout flake under load (RC3). Target: milestone
  close.
