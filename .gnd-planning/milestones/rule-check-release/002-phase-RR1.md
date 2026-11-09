---
milestone: rule-check-release
station: "phase-RR1"
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RR1
date: 2026-11-07
gates:
  - command: "uv run pytest -q tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_induced_provenance.py tests/test_fidelity_payload.py --tb=short"
    exit: 0
    output: "228 passed, 1 deselected"
  - command: "uv lock --check"
    exit: 0
    output: "Resolved 32 packages"
  - command: "git diff --stat origin/main -- .github"
    exit: 0
    output: "(empty)"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "61 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "ruff check over the 12 changed .py files"
    exit: 0
    output: "All checks passed!"
  - command: "~/e1/rr1.sh (the six-shard full default lane, copy of close-shards.sh) on beast-3 at 15ea4265"
    exit: "1 (the 2 known tests/test_public_optional.py errors only)"
    output: "17851 passed, 0 failed, 2 errors; main 1e63aeb5: 17830 passed, 2 failed (timing tests, pass alone), 2 errors"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "ruled excluded for RR1 (spec D6, owner 2026-11-07): the opt-in lanes are outside this phase's selection"
evidence:
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR1-spec.md
    sha256: a2550ea4215e1eb0c421d7ae36021fccf627a63876d9d1780fd33730e219f12f
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR1-codex-review.md
    sha256: 2bd01e9e3b70021ef108a24c70e11caa34477bbcc06d0e72e92e4cd20bc104c7
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR1/red-before-implementation.txt
    sha256: 54b615049c961404e9d135c2acac102e3a9a5eaa38d19d242676b9b1a14cc1a0
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR1/red-review-findings-F2-F3.txt
    sha256: 923ad638677b1b6eff523a0cdcc2a692ff5da9d08bef11477d81408dde4a3f29
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR1/full-lane-main-and-final.txt
    sha256: febb3a72ba5277806377aab54e10ef4e9b8644d40f976bf2983ea97c91461a5d
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR1/focused-gates.txt
    sha256: 43fa0b68c2f5b35ecd2fc4ca0c74c596d129e37007a645e83d64592839f6f63c
  - path: .gnd-planning/milestones/rule-check-release/evidence/e1/moved-digests.md
    sha256: 28d576e84b581a94ed5a4f3e34e4967af5fe1eb0572a481f46bed7d9e7fd22ce
  - path: tests/test_release_version.py
    sha256: d0a9f9f5903177d8c1faa7c8193c0657d218ca38e095cae733abaf302ac6fa62
  - path: tests/support/rf1_pins.py
    sha256: 7f340a46c5fabefaeac7efcad200d23ad06b523afb634ee08ae9d409bc97620b
  - path: docs/release-notes.md
    sha256: 19976f5fa5a2ac4e5a04066d1b48cd7640fe3f88818799fcff700210a2a92282
  - path: docs/compatibility.md
    sha256: 8bc523469f3e460aea704148ba6d27c11527056a7c0075fb974169993f8bdb84
  - path: docs/support.md
    sha256: c71155188219c07bb8439650c96c1cfe6c42d2a8cfa3b8fdf2d186101f084934
  - path: docs/marketplace-plugins.md
    sha256: ce1aa5fd4cfa338051bc5744c568b2e22a5ed8bc1b342852014a788da76dab18
  - path: pyproject.toml
    sha256: 46a71960af3a83e716b3d565f9124a09d0d2aafa963b735a902639bc76901e0a
---

# Claim

At 15ea4265 the repository declares version 0.2.0 in `pyproject.toml`, the lock
entry and the three plugin manifests, `tests/test_release_version.py` fails when
any of them or the release-notes heading drifts, the release notes, the
compatibility page and the support page say 0.2.0 is prepared and not published,
and the six-shard default lane has no failure: 17,851 passed and the 2
`tests/test_public_optional.py` errors that main also has. README and install
pins still name 0.1.0. Nothing is published.

## What shipped

- **M1 to M3** `pyproject.toml`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`: version 0.2.0; `uv.lock`: the one editable `get-nick-done` line (`uv lock --check` exits 0; a regeneration was refused because it also dropped an unrelated wheel line, E1).
- **M4** `tests/test_public_distribution.py` reads the version from `pyproject.toml` (4 sites); it was not run (D6).
- **M5** the pins and fixtures that carry the version, handled as ruled (D2): the RF1 helper `tests/support/rf1_pins.py` compares `gnd_version` as a placeholder (16 extract goldens), and 31 files were re-recorded: 8 synth goldens with `goldens.sha256` and its pinned digest, the IK1 baseline rows 4 and 5, the RF2 successor, the IK6 goldens, one roundtrip fixture, two measurement payloads, and seven gzip containers with their pinned digests. Every changed value is listed old and new in `evidence/e1/moved-digests.md`; applied to main after the FU2 merge, the scratch-measured edit passed unchanged.
- **M6 to M8, M10** release notes (one `## 0.2.0 (prepared, not published)` section, the rule-check block first, the twelve former Unreleased sections as `###` in order); compatibility and support pages; the plugin page's route for plugin users.
- **New test** `tests/test_release_version.py` (18 cases) and one harness test in `tests/test_rf1_pin_harness.py`. Red first: 3 failed on the unchanged tree (`evidence/RR1/red-before-implementation.txt`).
- **Review fixes** F1 to F3 (below).

## Gate output (verbatim)

Retained in `evidence/RR1/focused-gates.txt` and `evidence/RR1/full-lane-main-and-final.txt`. The full lane at 15ea4265, per shard: 3065, 2764, 3610, 3060, 2867 and 2485 passed; only shard 5 exits 1, for the two `tests/test_public_optional.py` errors that main shows too. Main at 1e63aeb5 showed `test_scope_walk_scales_linearly` and `test_timeout_escalates_term_to_kill_and_awaits_descendants` failing while the machine was loaded; each passed alone on the same tree (1 passed).

## Adversarial review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over the diff at aebe047c, disposition `revise`, 3 findings, each reproduced before it was accepted ([review](notes/phase-RR1-codex-review.md)). F1 (the plugin page's first install block did not point to the unpublished-version route), F2 (the publication guard accepted "installable from PyPI") and F3 (the version mask matched a key ending in `gnd_version`) were fixed in 15ea4265; F2 and F3 each have a test that was red before the fix (`evidence/RR1/red-review-findings-F2-F3.txt`). The repaired bytes carry no review opinion. The reviewer could not run the suite or `uv lock --check`; this record's gates did.

## Refactoring review

None executed. Argued from what the phase touched: it added one small helper to an existing test harness and one new test module; the repeated hand re-recording of 31 version-bearing files is the cost of method (b) that the owner accepted (D2), not a structure the phase could change behavior-preservingly. **Deferred, with a target:** version-bearing pins would stop moving at each release if the committed outputs were recorded version-independently. See the open question below.

## Boundary -- what this phase does NOT establish

- Nothing is built, installed or published. No wheel or sdist exists from this phase, so nothing here says the package installs, that 0.2.0 is free on the package index on any later day, or that the candidate behaves; RR2 owns the build and installed acceptance, RR3 the dossier.
- The opt-in lanes (`evidence`, `census`, `distribution`) were not run (D6). `tests/test_public_distribution.py` was edited and not executed; any version-bearing site that only an opt-in lane reads is unmeasured.
- The full default lane is one run per ref on one machine. The two timing failures on main show the lane is sensitive to load; the closing tree's green run does not make those tests deterministic.
- The release notes describe what is on main at 15ea4265. rule-check-followups FU3 is not on main, so the acyclic-extent behavior it adds is not described; RR2 reconciles the notes with whatever main holds at candidate freeze.
- One reviewer is one reviewer; it did not run the tests, and the fixes after it were not re-reviewed.
- The re-recorded pins show the committed outputs equal today's command output; they do not show the output is right.
- No claim about plugin installation by either host was exercised.

## Open questions

- RR2's spec needs its own owner gate and FU3 on main (RL-D2); T2, the distribution file's four literals, runs there (RL-D8 selects the lane).
- The release notes must be reconciled with FU3 and any other change on main before RR2 builds (plan RR2-C0).
- The publication-day patch moves `RELEASED`, the install pins in four documents and the compatibility text (RR3).
- Deferred refactor, target: the milestone that prepares the release after 0.2.0 (owner to name it): record the version-bearing fixtures independently of the version so a bump needs no re-recording; the measured cost is 31 files and 7 gzip containers.
- Two timing tests (`test_scope_walk_scales_linearly`, `test_timeout_escalates_term_to_kill_and_awaits_descendants`) failed on main under load; they pass alone. No owner for them is named.

## Refuted premises

- E1's inventory was taken to cover the version-bearing bytes; it did not read the tracked gzip archives. 12 archives name `0.1.0`, 6 of which had to move (`evidence/e1/gz-archives-naming-0.1.0.txt`, spec section 13.2).
- The one RF1 helper was taken to cover all 24 RF1 failures; it covers the 16 extract ones. The 8 synth pins hold digests of files that embed the version (spec section 13.1).
