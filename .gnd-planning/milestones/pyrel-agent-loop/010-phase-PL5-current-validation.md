---
milestone: pyrel-agent-loop
station: phase-PL5-current-validation
skill: process-phase
scope: phase-PL5-current-validation
date: 2026-10-14
source_base: 1165b814e0407ad94d0ee66075eabb1c477d0fca
status: documentation-validated-milestone-open
gate:
  command: ".venv/bin/python tools/accept_pyrel_applications_install.py --out <acceptance>"
  exit: 0
  output: "fresh wheel target-only application acceptance complete"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately selected CI
  reason: seven inherited failures classified in 007; focused current-byte checks suffice for these repairs
evidence:
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/acceptance.txt
    sha256: fee792b41dd1cdbc40612f9bd6c65011ff4c1220b5ed270aaa1ba344ee4e80f1
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/bookrec-offline-steps.json
    sha256: 9d87a45e7afe1d46725f394c666b6a3cdf4d939e5dc9c8485bb22981be3c9555
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/bookrec-pyrel-steps.json
    sha256: aa5ad0aac917237f21c50d3bd8df5eceef927ae35f6a2c5f8412a4b34e68fa7d
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/expense-offline-steps.json
    sha256: 82376c3b503e66a29026b40d2d7566ecd62d498dbad9e48a6f9e3806957e8a18
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/expense-pyrel-steps.json
    sha256: 7176913d83417a46859a69cc08e53070d4805ee3e5876fa9bcd7db254c130e4f
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/gnd-corpus.json
    sha256: 45c355f07e1f0b764c81779d5d7a212c94547538b7ebb4d23c7b5890dc7759fe
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/native-corpus.json
    sha256: 6623b00b16c01e5290e7cd32cca0da4a9dd1a09c801b4cf7025e63cd1660afa4
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/receipt.json
    sha256: c1553c8f59476bb47005bba0f431b1ee6f20ef0d550295e6ef036e931dcf0147
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL6-review/retention.json
    sha256: 8aaa80ba1deae1828d96c971e2afa80378dc402ddf9b322e865c3ac5b22db8dc
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/repair-final-focused.log
    sha256: 5127d8451a8c1ad8ee990738ff62ed7afad4b9d90239293d4f387bc7692c6d2a
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/review-source-identity.json
    sha256: e261fb075239a2e070abbc8edfa68d3920222a0326d01299becf80c85f3cfe73
---
# Reviewed documentation pushed and validated from a fresh wheel

The user approved the independent Codex review, then explicitly requested the
latest documentation be pushed for review on GitHub. Commit 1165b81 is pushed
on codex/pyrel-agent-loop in [draft PR22](https://github.com/vasiloglou/gnd-public/pull/22).
The complete reviewed documentation and this final acceptance result are ready
for owner review; this is not milestone close, scope acceptance or merge.

## Current-byte gates

Fresh-wheel command, machine-local output root rendered as a placeholder:

    .venv/bin/python tools/accept_pyrel_applications_install.py --out <acceptance>
    fresh wheel target-only application acceptance complete

Exit 0. All 16 child commands exited 0. The recorded source commit is 1165b81.
All 611 accepted source hashes were compared against the checkout afterward;
all 806 artifact digests were rechecked, and all 123 wheel resources match source.

| Gate | Observed |
|---|---|
| BookRec offline / native | 61 / 71 passed blocks (10 explicitly omitted offline) |
| Expense offline / native | 48 / 59 passed blocks (11 explicitly omitted offline) |
| Installed GND comparison | 137 verdict/witness/exit cases matched |
| Native comparison | 137/137 cases; 2321/2321 comparable rows; exactly two retained A1 differences |
| Both standalone import-isolation probes | passed |
| Native runtime | Python 3.13.12, PyRel 1.30.1, DuckDB 1.5.5; gnd absent |
| Base Python | 3.11.15 |
| Installed strict site and links | passed; 8316 local links/assets/anchors checked |

Final focused command:

    .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pyrel_learning_path.py tests/test_meal_cap_proposal.py tests/test_tutorial_output_blocks.py tests/test_pyrel_tutorial_experience.py tests/test_documentation_tutorials.py tests/test_pyrel_applications_install.py tests/test_recording_tools.py tests/test_pyrel_recordings.py tests/test_pyrel_stand_in_sessions.py
    224 passed, 4 deselected in 48.94s

Exit 0. This discharges 009's final two replay-control follow-up. Changed-file
ruff checks pass. The local strict build also passes. No further broad suite was
selected; the previous seven main-inherited failures and local nested-worktree
reference scan remain classified in 007.

## Evidence inheritance and retention

This fresh receipt supersedes 008 as installed acceptance for the reviewed bytes;
008 remains immutable historical evidence. The 009 initial and bounded review
reports remain their own opinions. No third reading ran, and the two hardening
repairs made after the bounded reading are established by local controls and this
installed run, not by a reviewer approval that did not occur.

retention.json declares raw and retained receipt hashes and substitutions for
machine-local paths. The original receipt, wheel and generated artifacts remain
in a local raw archive of 4678250 bytes, SHA-256
14aa775a21519c035d42ed55eabb5122d10aaa511a8bc8ae51fdf5b2c1265628. Committed receipt copies alter only documented
path prefixes. The build-input hashes are separately retained because the harness
itself still omits them from its general source-identity contract.

Fresh Expense screenshots at desktop/mobile widths and both themes show the full
recorded task and linked-project drift/regeneration. Their hashes and changed
source hashes are in review-source-identity.json. Author visual reading confirms
readable prose and horizontally scrollable code without page-width overflow;
these screenshots are not independent review evidence.

## Refactoring review

None additionally needed: final validation introduced no runtime or query change.
The ordered-excerpt check and canonical tracked-roster reuse are recorded in 009.
The seven refactoring failures and the broader agents-page prose gate remain
named maintenance work, not quietly absorbed into this documentation phase.

## Boundary and open questions

Documentation implementation, independent phase review, reproduced repairs,
focused tests and finite installed acceptance are recorded. The initial review
had two blockers; the bounded repair reading had zero blockers and two existing
hardening items, subsequently fixed. This is one reviewer across two readings.
A four-reader milestone-close review has not run.

Claude Code is still not recorded. The user approved review and push, not the
Codex-only scope exception. The literal Claude recording criterion therefore
remains open to the owner: accept the documented Codex-only boundary or supply
separate authorization/access to record Claude. No new key-bearing call is
inferred from review permission. PR22 remains a draft for that decision and
milestone-close readiness. No merge, release, site publication or certification.
