---
milestone: code-refactoring
station: "phase-RF1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF1
date: 2026-10-05
gate:
  command: "uv run pytest -q tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py"
  exit: 0
  output: "395 passed, 16 xfailed"
  base: "e834c6e (src/gnd byte-identical to the RF0 base 19b131b)"
  note: >-
    Also exit 0 under Python 3.11 and 3.13; the RF1-C1 mutation run, tool
    tests, reused-support consumers, lint, planning links and the two scope
    checks are listed in the body.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "RF1 changes no imported product code; its new default-lane load is the selected gate above"
selection:
  - {obligation: "RF1 pins green at base (RF-R3)", disposition: run, command: "the gate command", exit: 0}
  - {obligation: "same under the CI interpreters (D2)", disposition: run, command: "the gate command under uv run --python 3.11 and 3.13", exit: 0}
  - {obligation: "RF1-C1 seeded mutations", disposition: run, command: "uv run python tools/rf1_pins.py mutate --out <scratch> --jobs 6", exit: 0}
  - {obligation: "tool behavior (RF0-OQ2)", disposition: run, command: "uv run pytest -q tests/test_gnd_arch.py", exit: 0}
  - {obligation: "consumers of the imported test builders", disposition: run, command: "ledger.txt row 2 (10 files)", exit: 0}
  - {obligation: "lint", disposition: run, command: "uv run ruff check tools/rf1_pins.py tools/gnd_arch.py tests/support/rf1_pins.py tests/test_rf1_*.py tests/test_gnd_arch.py", exit: 0}
  - {obligation: "planning links", disposition: run, command: "uv run pytest -q tests/test_development_scaffold.py", exit: 0}
  - {obligation: "RF-R1 and RF-R7: no src/gnd or public-launch change", disposition: run, command: "git diff --quiet e834c6e -- src/gnd .gnd-planning/milestones/public-launch", exit: 0}
  - {obligation: "RF1-C2 path scope", disposition: run, command: "git diff --name-only e834c6e | grep -v -E '^(tests/|tools/|.gnd-planning/milestones/code-refactoring/)'", exit: 1, note: "1 means no path outside the scope"}
  - {obligation: "full default lane", disposition: cadence, note: "not selected; see slow_cadence"}
  - {obligation: "distribution lane", disposition: cadence, note: "vasiloglou/gnd-public#8 owns the whole-tree retirement"}
evidence:
  - {path: tools/rf1_pins.py, sha256: 17c8d0695b95aa6ee48a424d6f0814e55937aee6a71a5d617da5398beebf4d38}
  - {path: tools/gnd_arch.py, sha256: 2756267ab7d3a82771445e8654b94aeb5b642a4fa91d890e2b07df6d20376923}
  - {path: tests/support/rf1_pins.py, sha256: bc8d818edd867c2fd86c03fd99aaad8ae96a7815ee4a3a1b1627cbcbefc70c1e}
  - {path: tests/test_rf1_cli_pins.py, sha256: 0b18622807da10ca73c9913311a0fd84c04665afb3f585f7f6c7ba4a7d22c733}
  - {path: tests/test_rf1_helper_pins.py, sha256: ff11d0215e4e70a57aa872c5f02349656b5e7dd18d44aa8d36aeb982fc45112c}
  - {path: tests/test_rf1_semantic_pins.py, sha256: 6d115a8edb75aed6fd0459c735fd0c02390aad04670456cb42306168ea744963}
  - {path: tests/test_rf1_agent_cli_pins.py, sha256: 05948b70561e7ec6ddcbf64df89b6b8eb68e67f0e87bf61c55bf5b61ea6fb785}
  - {path: tests/test_rf1_session_pins.py, sha256: 9bbe345c93be679a99239f6e7d50b7fec4f61dd9eef3533108972190fb60db15}
  - {path: tests/test_rf1_layering.py, sha256: 4c43b9ee9602805f3982e6eb9c1da73330e96b3b21c1a47b550d82bb2433ec82}
  - {path: tests/test_rf1_pin_harness.py, sha256: 99caaa424f55b08b9719017d6a0377525593183ff9529227ecf0db9d6429a593}
  - {path: tests/fixtures/rf1-pins/goldens.sha256, sha256: 68d9163ee30f32fc03f59294b94c709e52ac569168ac6ecc773eb5dd22a36444}
  - {path: tests/fixtures/rf1-pins/cases.json, sha256: 9ae4960dba5ce401fa3336d9057c586b2f992911e720753738817aa9d9d60fe3}
  - {path: tests/fixtures/rf1-pins/mutations.json, sha256: 4ea6c54df017f46806a0f6e00ea2939def98e6e2399f76b197289dc318faac22}
  - {path: tests/fixtures/rf1-pins/inventory.json, sha256: 65cb89e019ed7aa7a1cb1a547a7cdb67ce1ca3c49bbca44ede405057af5a9ad5}
  - {path: tests/fixtures/rf1-pins/README.md, sha256: ccab99d8e3675fe562fa33829c9e7b6639f2b880e10bd4ed971bf54e726f2c89}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF1-base.json, sha256: fdecd3715518437831c009ecd7af4b8ac32b4f1cf3d5eeb20188b4e235b4fc80}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/mutation-report.json, sha256: 2b9763a44b22527dce8af436eca82599195960cc9deed3a81746c725616dcfef}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/mutation-run.txt, sha256: bb4189707c62a4cab5cda1f22ce468463b19aafcb615f2a88d0d6ac22bd38d4d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/control.txt, sha256: c80ea0e10bd6de5e2cebede2935285b8e35b35615e4d0a51b8210d6832341ad2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/pins-three-interpreters.txt, sha256: 2329cefa31dad48eb51f27bcd8b7ec596b29af1b4ef5ca5c8bcc7af77bb22a76}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/ledger.txt, sha256: 706a058e985df85504b64478621bc1070ad55a3abd9f893e229d80dd11600e6a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/harness-red.txt, sha256: fd0d9d12dbe68c4c2fcabeb6cdea51a7365b6970ddbfdfd977a4aea92de26e7e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/review-regressions-red.txt, sha256: 75f9bed914e6735a06ea9a6c95484f6894baba914127a19cd6aac274ea704e6d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF1/alias-scope-red.txt, sha256: 6dc861516f34f3caaf07866788f8d1f77390861e7025e8e701b3e7cb802962eb}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF1-spec.md, sha256: ca5ac9338f6321ca5e32b681ef12260b15bac35af421e691374fff1cab0e7d87}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF1-codex-review.md, sha256: babec06365157d2777dec0df77cca12fecd655c7bffee72423875231dfa943b3}
---

# Claim

At base `e834c6e`, with no `src/gnd` byte changed, the seven RF1 test files
exit 0 under Python 3.14, 3.11 and 3.13 (395 passed, 16 strict xfails each),
and `tools/rf1_pins.py mutate` exits 0: the unmutated control passes on all
350 pinned nodes and every one of 167 seeded mutations turns the nodes it names
red.

## Gate output (verbatim)

    $ uv run pytest -q <the seven RF1 files>
    395 passed, 16 xfailed in 61.30s (0:01:01)
    $ UV_PROJECT_ENVIRONMENT=<venv311> uv run --python 3.11 python -m pytest -q <the seven RF1 files>
    395 passed, 16 xfailed in 63.57s (0:01:03)
    $ UV_PROJECT_ENVIRONMENT=<venv313> uv run --python 3.13 python -m pytest -q <the seven RF1 files>
    395 passed, 16 xfailed in 62.50s (0:01:02)
    $ uv run python tools/rf1_pins.py mutate --out <scratch> --jobs 6
    rows: 167  killed: 167  not killed: 0
    exit=0 elapsed_seconds=94
    $ uv run pytest -q tests/test_gnd_arch.py
    47 passed in 4.70s
    $ uv run pytest -q <10 consumer files, ledger.txt row 2>
    892 passed, 2 deselected in 138.54s (0:02:18)
    $ uv run ruff check <RF1 files>
    All checks passed!
    $ uv run pytest -q tests/test_development_scaffold.py
    14 passed, 1 deselected in 3.85s
    $ git diff --quiet e834c6e -- src/gnd .gnd-planning/milestones/public-launch
    (exit 0)
    $ git diff --name-only e834c6e | grep -v -E '^(tests/|tools/|\.gnd-planning/milestones/code-refactoring/)'
    (no output, exit 1)

Before any golden existed (`4ef5747`), the same seven files reported
`346 failed, 38 passed, 16 xfailed` ([harness-red.txt](evidence/phase-RF1/harness-red.txt)).

## What shipped

- **Pin lanes** (`tests/test_rf1_*.py`, 353 pinned nodes): the CLI's 52
  parsers (tree, help, `--help` and unknown-flag probes, every exit constant
  and map); 88 helper-family sites, each on shared inputs; the primitive
  resolver, six datetime sites, the checker over 25 corpus pairs plus the
  transition, batch and anchored arms with a both-outcomes coverage check,
  verbalize, extract, diff, assurance blocks and the synth oracle; `agent_cli`
  run and invoke scenarios; session replays for contract versions 1–8 (fresh,
  resume, reconstruct for v7 and v8, unknown versions 0 and 9, and a
  determinism double run); 16 strict-xfail layering pairs and a no-new-pair
  ratchet.
- **Corpus** (`tests/fixtures/rf1-pins/`): stories in the README; inputs in
  `cases.json`; 425 goldens (3.16 MB) bound by `goldens.sha256`, whose own
  digest is fixed in `test_rf1_pin_harness.py`; 42 keys stored per minor
  version for runtime-caused differences.
- **Normalizer** (`tests/support/rf1_pins.py`): rules N1–N9, each
  verify-then-replace where a digest is involved, plus the timing and staging
  checks the review asked for.
- **Tool** (`tools/rf1_pins.py`): `capture`, `merge` and `mutate`.
- **RF0-OQ2**: one `_AliasScopes` in `tools/gnd_arch.py`; output unchanged.

## Criteria

| Criterion | Result |
|---|---|
| RF1-C1 every pin fails under a seeded mutation | Met for 350 nodes, 167 rows, all killed, call-phase failures only. **Narrowed**: three meta nodes (`test_helper_coverage`, `test_case_manifest_builds`, `test_cli_coverage`) sit in the table's `exempt` list with reasons; spec §6.9 excludes only the harness and layering files. Open question RF1-OQ3 |
| RF1-C2 only test, fixture and tool files | Met (scope check above) |
| RF1-C3 a pin per diverged variant | Met: T-HELP-COV maps every RF0 family and identical-candidate site to a pin, a routed pin, an owed phase, or the two trivial constructors |
| RF1-C4 later surfaces mapped to tests | Met with owed rows: 35 surfaces; 4 are owed under RF-R3 (handler byte pins for RF5 commands other than check, verbalize, extract, diff, synth and exp run, per D9; the measure and pyrel ref sites, RF2; the model and checker package-split import paths, RF6; `artifacts.directory_identity`, RF4). T-INV checks that every reference collects and that every owed row carries its anchor |

## Budgets (D10)

| Item | Ruled | Measured |
|---|---|---|
| Hand-written lines | estimate 4,350; stop 6,525 | 5,812 |
| `mutations.json` | estimate 700 | 1,705 (2.4×). Owner ruling 2026-10-05 under RF-D13: accepted |
| `test_rf1_helper_pins.py` | estimate 350 | 535 (1.5×). Owner ruling 2026-10-05: accepted |
| Goldens | at most 8 MiB | 3.16 MB |
| Default-lane runtime of RF1 files | at most 180 s | 61–64 s |
| Mutation run | at most 45 min | 94 s with 6 jobs |

## Review

One reviewer is one reviewer. A single Codex review (gpt-6-sol, xhigh,
read-only sandbox, prompt on stdin) reported 10 findings. It could not run
pytest's temporary-file fixtures or any mutation replay, so it verified the
mutation report by reading. All 10 were reproduced. Regression tests for the
fixes were red before the fixes (11 failed); RF1-07 was reproduced by a
surviving harness row. By owner ruling ("ok do 2"), RF1-01, 02, 03, 04, 06,
07 and 09 are fixed, RF1-10 is fixed in part, and RF1-05 and RF1-08 are open
questions. Dispositions: [phase-RF1-codex-review.md](notes/phase-RF1-codex-review.md).

## Boundary — what this result did NOT establish

- A characterization pin asserts that behavior did not change. It says
  nothing about whether the behavior is correct; the quirks Q1–Q5 are pinned
  as found.
- Mutation kills prove that each pin can fail. They do not prove that the
  pinned inputs reach every branch of the code under the pin.
- CI is unavailable (GitHub billing). The 3.11 and 3.13 runs are local and
  macOS-only; ubuntu behavior, notably FIFO, `O_NOFOLLOW` and `mimetypes`
  details, is unobserved.
- Command handlers other than check, verbalize, extract, diff, synth and
  exp run are pinned only at parser, help and exit-probe level (D9).
- Session evidence is normalized: monotonic and seconds values, temporary
  roots, the interpreter path, nonces, the production and producer identities
  and pytest's JUnit digests are placeholders or verified references, so a
  change confined to those values is not detected. Durations are checked only
  for sign and ordering.
- One reviewer's reading, without a mutation replay, is not a panel.

## Refactoring review

**Refactors EXECUTED:**

- RF0-OQ2: one alias resolver (`_AliasScopes`) for both visitors in
  `tools/gnd_arch.py`, behind the RF0 tool tests plus a new lexical-scope case
  that was red against the old tool; output byte-identical.
- Within the new code, session normalization had a second, regex-only seconds
  normalizer and its own token scrubber; both were folded into the single
  `normalize_text` before the goldens were captured.

**Seen and deferred** (none can be executed here, because RF1 may not edit
`src/gnd`):

- The session prompt embeds the absolute contract path (`cli.py:5436`), so
  evidence digests depend on where an experiment lives. Open question RF1-OQ4.
- Three file-digest readers block forever on a FIFO (F1). RF1-OQ5.
- Candidate media types come from the interpreter's `mimetypes` table (Q5).
  RF1-OQ6.
- The batch arm of `gnd check` writes to `sys.stdout.buffer`, bypassing the
  report emitter every other command uses (F7). Recorded for the RF5 spec.
- `tests/support/rf1_pins.py` keeps two token-replacement paths (`scrub` for
  observations and `normalize_text` for evidence) that escape differently; on
  POSIX paths they agree. RF1-OQ7.

## Open questions

- **RF1-OQ1 → RF2 to RF8 spec gates:** owed pins in `inventory.json` must
  land before the owning phase moves the surface (RF-R3): RF2 measure and
  pyrel ref sites; RF4 `artifacts.directory_identity`; RF5 handler byte pins
  (D9); RF6 package-split import paths.
  RF2 discharge annotation (2026-10-05): [007-phase-RF2.md](007-phase-RF2.md)
  supplies the measure-output, guarded-exists and standalone PyRel byte/reference
  successor pins before routing. Other owed families keep their assigned owners;
  standalone PyRel producer routing remains an explicitly approved RF2 exception.
  RF4 discharge annotation (2026-10-05): [009-phase-RF4.md](009-phase-RF4.md)
  supplies the source-base nested artifact directory-identity refusal pin and its
  observed disabling control before filesystem routing. Other owed families
  retain their named owners; RF1's original boundary remains unchanged.
  RF5 discharge annotation (2026-10-05): [010-phase-RF5.md](010-phase-RF5.md)
  supplies 43 original-source handler observations, including the 25 owed
  command surfaces, with 43 effective disabling controls before routing.
  These selected leaf observations do not establish every internal branch.
  RF6 import-path responsibilities and RF1's original boundary remain standing.
- **RF1-OQ2 → RF8 spec gate:** resume through the CLI refuses for v2, v3, v7
  and v8 after a completed run's result is removed (F12). This is pinned as
  found; RF8 should decide whether it is intended.
- **RF1-OQ3 → milestone close:** RF1-C1 is narrowed by three exempt meta
  nodes (review RF1-08).
- **RF1-OQ4 → RF8 or the successor milestone:** prompt embeds the absolute
  contract path.
- **RF1-OQ5 → successor milestone (RF7 safefs work):** FIFO-blocking digest
  readers (F1).
- **RF1-OQ6 → successor milestone:** interpreter-dependent media types (Q5).
- **RF1-OQ7 → next phase that edits the support module:** unify `scrub` and
  `normalize_text` token replacement, and bind declared-input bytes (review
  RF1-05).
- RF0-OQ4 to RF0-OQ7 remain with their named gates.

## Refuted premises

- Spec §6.5: "`gnd verbalize MODEL`". No such command exists; only
  `verbalize population` (F2).
- Spec §6.7 N4: "the receipt nonce must not appear in any published file".
  It is published in `attempt.json` (F4).
- Spec D3's estimate of about 90 mutation rows: 167 were needed (F14).
