---
milestone: pyrel-agent-loop
station: phase-PL6-preparation
skill: process-milestone
scope: phase-PL6-preparation
date: 2026-10-14
status: installed-checked-review-pending
source_base: 1495ba2f61eb5f8524b35589b14dc5cd07707b21
gate:
  command: ".venv/bin/python tools/accept_pyrel_applications_install.py --out <acceptance>"
  exit: 0
  output: "fresh wheel target-only application acceptance complete"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately selected CI
  reason: prior full run classified in 007; no new broad replay selected
evidence:
  - path: .gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL6-spec.md
    sha256: 9b43c1c858b40c95c0f78b1c469babaf8c1df70162390c8e8c5965a919811476
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/acceptance.txt
    sha256: 52d6d0b561e4d2a9df67a7959609fc314f408f0a567dd4a931bb3fad91381d61
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/bookrec-offline-steps.json
    sha256: 90a786d24b1ac061d171d725571990cd350d06ac689ce6203fcbfddc3ae374ed
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/bookrec-pyrel-steps.json
    sha256: 1b293c34d9bae0e58cdedf703be86ceeea994097d6310bfb242072e72a2e4a71
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/expense-offline-steps.json
    sha256: 8121136d70e179cc69ff8005e14e2beb5dabe357e842ef14fef71dc52bc7fd1e
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/expense-pyrel-steps.json
    sha256: e6cb24c647e0ea3b25da2c5846389076aff39d6fb2cb2c7093c2163d175e031e
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/gnd-corpus.json
    sha256: 45c355f07e1f0b764c81779d5d7a212c94547538b7ebb4d23c7b5890dc7759fe
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/native-corpus.json
    sha256: 6623b00b16c01e5290e7cd32cca0da4a9dd1a09c801b4cf7025e63cd1660afa4
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/receipt.json
    sha256: 6823a52ddc23195e71809df92d3edb288cfb4e63f9891f3bd3d2c0d77093fca9
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6/retention.json
    sha256: 4678a5ff16cef28e6d0e366281ed66130713eb8e97beedb798b496b3dc14e411
---
# Installed acceptance completed; PL6 review and close remain pending

The fresh-wheel harness exited 0 on the resumed page bytes, before committing
this checkpoint. It records base commit 1495ba2 and exact source hashes including
the then-uncommitted changes. All source hashes were rechecked against the
checkout and all 804 retained artifact digests were verified after the run.
This is a source-content-bound preparation result, not a claim that HEAD alone
already contained the pages. The checkpoint commit preserves those same inputs.

## Gate output and measurements

Command (machine-local root rendered as a placeholder):

    .venv/bin/python tools/accept_pyrel_applications_install.py --out <acceptance>
    fresh wheel target-only application acceptance complete

Exit: 0. All 16 child commands exited 0.

| Control | Measured result |
|---|---|
| Installed BookRec offline | 61 passed; 10 native blocks explicitly omitted |
| Installed BookRec PyRel | 71 passed; all 10 native blocks executed |
| Installed Expense offline | 46 passed; 11 native blocks explicitly omitted |
| Installed Expense PyRel | 57 passed; all 11 native blocks executed |
| Installed GND corpus | 137 verdict/witness/exit controls matched |
| Native corpus | 137/137 cases; 2321/2321 comparable rows; exactly two retained A1 differences |
| Native origin | Python 3.13.12, PyRel 1.30.1, DuckDB 1.5.5; gnd absent |
| Generated standalone import probes | BookRec and Expense passed |
| Base environment | Python 3.11.15; wheel installed outside checkout |
| Wheel resource inventory | 123 source-byte-matched resources |
| Installed docs | strict build; 8284 local links/assets/anchors checked |
| Artifact bindings | 804 files verified by SHA-256 |

## Retention and provenance

The original acceptance root and a 4,660,215-byte raw artifact archive remain
local under the resume scratch directory. retention.json records the archive's
SHA-256 and the raw and retained digests for each copied receipt. Committed
copies substitute only the documented machine-local path prefixes; artifact
hash values remain the original hashes. The local archive contains raw generated
outputs, receipt and wheel. It is not a committed portable environment.

The harness's source identity omits build metadata. retention.json separately
binds pyproject.toml, uv.lock, README.md and corpus approval.json on these exact
accepted bytes. This does not repair or expand the harness's general contract.
Unrelated untracked files and the old PA6 artifact archive are excluded.

## Verification selection

Run: installed acceptance, current install-control tests (within 007's focused
command), strict build, links and source/artifact digest verification. Invalidate
on any changed input hash. Inherit with limits: prior full-suite summary and
current baseline classification from 007. Cadence: further broad historical
runs require explicit selection. No live agent, external account, model key,
Snowflake backend or production publisher was exercised by the install check.

## Review and readiness

PL6-C1 is measured. PL6-C2 is classified in 007. PL6-C3 awaits the draft PR.
PL5 independent review, independent coverage of PL4 tools and the four-reader
close review remain outstanding. No review opinion is inferred from green
execution; one reviewer is one reviewer, and no successful review ran during
this continuation. The explicit gpt-6-sol review authorization remains pending.

## Refactoring review

None needed: only count constants changed in the existing install harness and
its tests. Source-identity coverage and shared corpus-key maintenance stay with
the already named native-install-harness-maintenance backlog, not a hidden new
runtime change in this documentation milestone.

## Boundary

Finite installed acceptance of these source bytes. Base/docs transitive packages
are measured installed resolution, not a locked reproducibility claim. This does
not establish a real Claude recording, independent review, complete milestone
acceptance, universal equivalence, release, publication or merge authority.
The seven main-inherited refactoring failures remain open. PL4-Q1 and the
literal Claude-session completion criterion need an owner disposition.

## Open questions

- PL5-Q1: independent review permission and result, owned by the owner/reviewer.
- PL6-Q1: independent close readings including PL4 recorder/wrapper, after PL5.
- PL4-Q1: Claude recording or explicit Codex-only scope acceptance, owned by owner.
- Seven inherited failures: GND maintainers' existing refactoring follow-up.
- Harness maintenance: native-install-harness-maintenance, already named backlog.
