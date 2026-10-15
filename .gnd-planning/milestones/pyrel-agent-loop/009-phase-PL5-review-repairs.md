---
milestone: pyrel-agent-loop
station: phase-PL5-review-repairs
skill: process-phase
scope: phase-PL5-review-repairs
date: 2026-10-14
source_base: 2eb91afe73400d39225daa4e0bb92ff020fd5052
status: review-repairs-implemented-install-acceptance-pending
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pyrel_learning_path.py tests/test_meal_cap_proposal.py tests/test_tutorial_output_blocks.py"
  exit: 0
  output: "67 passed in 3.26s"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately selected CI
  reason: inherited failures classified in 007; focused current controls selected
evidence:
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/repair-expense-offline.log
    sha256: d6c482383b67973db6083c93351bb9487de6c354f1457711939649e593c4c7db
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/repair-final-build.log
    sha256: 2eadab701c5898885baddffa37614fc0a2ee66bccd082d1d54a8bc5245ad035a
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/repair-final-links.log
    sha256: b42f36d945f8e95eff0cf8e19caa382af54692b959f33cb9577370359a412941
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/repair-focused.log
    sha256: 3240d31ed65d17c0dccf2890fc99f5b01413f19a280b53332b5b561c8408f29a
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/repair-full-focused.log
    sha256: 6e9708f7c5ad645ce14849c5671eb78a12064e70467e1de636cf36bf76119271
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/replay-green.txt
    sha256: 4205e48b430f23bf32953f892a275827e2613e221c6cff8ecf605e8ecd063bc5
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/replay-red.txt
    sha256: a9cb3f983a0d163f5c8b1138709223dbf6396e9dbfd2f3b8305ef27a76097f5b
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/review-boundaries-red.txt
    sha256: 3987ab426d584a6a3a05f4b68dd5920933a080e35bacd543c4ab0a87c1993f41
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/review-helper-red.txt
    sha256: 3747fd0262281b0a5cb7cc3bce6390272c59122cbe21fa2ea0d4779f8426f862
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5-review/review-red.txt
    sha256: ee57840ab6f6f928850fa690075625dde4bc3ba785ad031533dca80061fbee2e
  - path: .gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL5-codex-review.md
    sha256: aa30fc3b26fe03fe5fd05dd1559f4381e9b1954de78112309665ea5fde9fd558
  - path: .gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL5-codex-repair-review.md
    sha256: 8e0979149fcf520732c89ad3522e5568dfbf3b43aa700fdff34bf131a830bad7
---
# Independent review and reproduced repairs

Owner explicitly approved the independent Codex review in chat on 2026-10-14.
That discharges the permission question in 007/008, without waiving the missing
Claude recording or authorizing merge. The installed Codex CLI ran gpt-6-sol at
xhigh effort, read-only, prompt on stdin, in one initial reading and one bounded
repair reading. One reviewer is one reviewer; no four-reader close claim.

## Findings and disposition

| Finding | Class | Result |
|---|---|---|
| Initial F1 incomplete Expense task | blocking | Print the entire hash-pinned task; observed truncation test red, then green |
| Initial F2 green aggregate with no linked project | blocking | Link generated Expense project with tracked roster, evolve external model, observe drift 13, regenerate, run standalone conformance 0 |
| Initial F3 scripted/recorded confusion | hardening | Clarify openings and replace an unsupported statement about real repair behavior |
| Initial F4 optimized hash checks | hardening | Explicit ValueError refusals; eight -O tamper cases red before repair |
| Initial F5 meal-cap widening | hardening | Refuse caps outside 1..old_cap-1, and require the linked project |
| Initial F6 reader-shell pipelines | hardening | Direct evolve commands; four fake-executable failure controls red before repair, then preserve exit 42 |
| Initial F7 entire agents-page prose gate | completeness | Deferred to GND maintainers' tutorial-maintenance backlog; inherited generic pages retain explicit scope limit |
| Initial F8 source line order | hardening | Ordered source walk; two reversed-excerpt controls red before repair |
| Repair reading BookRec opening | hardening, pre-existing | Clarified scripted refusal versus first-try recorded acceptance after reading |
| Repair reading optimized replay comparison | hardening, pre-existing neighbor | Two checker-drift controls red under -O, then explicit ValueError comparisons |

The initial reviewer returned revise with two blockers. The bounded repair
reader returned revise with zero blockers and two pre-existing hardening items;
both were fixed afterward and receive local controls, not a fabricated second
review approval. No third reading runs under the declared budget.

| Round | Seats | Per-seat findings | New due to repair / total | Blocking / total | Ceiling |
|---|---|---|---|---|---|
| Initial | 1 | 8 | n/a, no prior independent repair round | 2/8 | high |
| Bounded repair | 1 | 2 | 0/2 | 0/2 | medium |

## Measured controls

- Initial excerpt regressions: 9 failed, 8 passed (hidden task plus eight -O cases).
- Ordering/shell controls: 6 failed before repair.
- Linked-project helper/validation controls: 5 failed before new interface.
- Repair focus: 67 passed. Broader focused run: 222 passed, 4 deselected.
- Subsequent replay-drift controls: 2 failed before repair; 2 passed afterward.
- Expense offline: 48 blocks; native inventory becomes 59 total / 11 native.
- Strict site build and links pass: 8316 local links/assets/anchors checked.
- Lint passes for changed helper, tests and install harness.

## Refactoring review

Executed within tests: excerpt grounding uses an ordered walk rather than a
set. The helper reuses snapshot_tracked_roster and EvolutionProposal, matching
the existing currency example instead of introducing another snapshot primitive.
No new core module or layer assignment. Wider recording-display consolidation
stays deferred as in 007.

## Boundary and next gate

The old installed receipt in 008 describes pre-review bytes and is unavailable
as acceptance for these changed pages/helper. Fresh-wheel acceptance is next;
its completion will be recorded separately. The full focused run with the last
two replay controls is still in progress at this checkpoint. PR22 remains a
draft. No new Claude recording, four-reader close, milestone acceptance, merge,
release or publication occurred. Reviewer hashes are claims, not authority: the
malformed initial dev-session hash is retained and its corrected value appears
in the repair reading.

## Open questions

- PL4-Q1: Claude recording or explicit Codex-only scope acceptance, owner decision.
- Four-reader close review once mandatory phase/recording criteria are ready.
- Seven inherited refactoring failures, existing GND-maintainer follow-up.
- Whole agents-page prose coverage, tutorial-maintenance backlog (F7).
