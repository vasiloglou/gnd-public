---
milestone: literature-depth
station: phase-LD1-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LD1-spec-gate
date: 2026-11-15
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld1_competency_examples.py --tb=short"
    exit: 1
    output: "5 errors in 0.11s; the literature depth example module is absent"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD1-spec.md sha256 911da3e7312c5524e6165c16317e21d5bfd707a907838807e206822511b11d6a"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-depth/002-plan-gate.md
    sha256: 74dcb67460626f7d7e5a5a39b8659b37aee5f73d2905fd69d16dceb597393d75
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD1-spec.md
    sha256: 911da3e7312c5524e6165c16317e21d5bfd707a907838807e206822511b11d6a
  - path: tests/fixtures/ld1-competency/README.md
    sha256: c041e18443436cba77b3b191e45643691084d006d5e26e8aedd63322703ce993
  - path: tests/fixtures/ld1-competency/expected.json
    sha256: fd7de6ec831ca4c42f44252140af51cc611612d6521fcbc6c13ac623ad66e225
  - path: tests/test_ld1_competency_examples.py
    sha256: 838a18151e27957a551f85810af68f2e4138d7aff627c65dd777c70b10703e1a
---

# LD1 spec and corpus gate

ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD1-spec.md sha256 911da3e7312c5524e6165c16317e21d5bfd707a907838807e206822511b11d6a

Delegated approval under the owner's `process-milestone literature-depth
auto` invocation. This phase uses the corpus-first instrument. The red
corpus observes the packaged entry point, the question and comparison rows,
and the three numeric probes. Its expected-outcome file is separate.
The selected initial implementation and independent phase diff review each
still owe their own verification. No optional spec panel was selected.
The authorized plan panel evaluated r2 and is recorded in [001](001-panel.md).

## Implementability sweep

The intended GND routes already support rooted includes, saved extraction
sidecars and checked populations. The 86 prerequisite tests over LX1, LI4
and LX4 passed on the plan base. A separate fixture review can bind positive
answer values and source locators before the example runs. Each comparison
field can vary independently with a retained baseline. Existing numeric
fixtures can exercise each observed capability, and a named refusal is an
observation for LD2. Each expected unknown has a separately documented
scope and a nonempty evidence record. A public checker negative fixture
can violate the one-label constraint without changing the identity scheme.

## Decisions

- Use source-specific facts over a shared experiment vocabulary, and keep
  synthetic controls separate from reported science.
- Freeze the decision order for comparison and record evidence for all
  three quantity probes before selecting the conditional scope.
- Part 10 remains deferred.
