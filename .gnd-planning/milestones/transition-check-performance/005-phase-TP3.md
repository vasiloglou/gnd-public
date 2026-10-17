---
milestone: transition-check-performance
station: phase-TP3
skill: n/a -- repository development, not a gnd-solve station
scope: phase-TP3
date: 2026-10-17
gate:
  command: "uv run pytest -q tests/test_tp3_check_receipts.py tests/test_tp2_shared_fact_types.py tests/test_tp1_index_scope.py tests/test_transition_cost_workload.py tests/test_public_api.py tests/test_public_reference_signatures.py tests/test_v61_phase2_api.py tests/test_public_runtime.py tests/test_public_transition_contract.py tests/test_public_transition_trace.py"
  exit: 0
  output: "110 passed, 14 deselected (3.14.3 in 174.65s, 3.11.15 in 211.55s, 3.13.12 in 185.08s)"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner selection
  reason: focused gate plus 855 affected-consumer tests cover the touched homes
---

# Claim

TP3 is complete under the owner-approved spec ([spec](notes/phase-TP3-spec.md), "approve
TP3", 2026-10-17). Codex CLI implemented it, as the owner selected. The session resolved
two spec gaps that Codex reported, fixed the reviewer's blocking finding and a consumer
regression, and ran every gate.

**New public API:**

- `api.check_with_receipt(model, population)` returns the `api.check` payload and an
  opaque, in-process `api.CheckReceipt`.
- `api.transition(..., pre_receipt=...)` reuses that check for the pre-state.
- `api.ReceiptRefused` names the reason for each refusal (8 reasons).

**Results:**

- Reporter replay with receipts: 25 → 19 checker runs, with all 13 payload digests
  identical.
- Without receipts, every TP0 digest is unchanged.

## Gates

- **Focused gate (frontmatter):** exit 0 on three interpreters.
- **Affected consumers:** RF and layering pins, 291 passed; transition, preparation,
  batch and runtime suites, 564 passed with 16 deselected.
- **Lint:** All checks passed!
- **Receipt replay** (`evidence/TP3/receipt_replay.json`): 25 versus 19 checker runs;
  `payloads_identical: true`.
- **Default path:** `evidence/TP3/digests.json` equals the TP0 file.

## Measurements

| Reporter replay | Checker runs | Median (same process, sequential) |
|---|---|---|
| without receipts | 25 | 2.53 s |
| with receipts | 19 | 2.28 s (−10%) |

Earlier runs today measured −6.8% and −9%. Wall time is evidence only.

## Independent review

One local reader ([notes](notes/phase-TP3-claude-review.md)). **One reviewer is one
reviewer.** The reader could not get a wrong pre-state accepted. Every refusal fires
before evaluation (0 checker runs), in the spec's order. 12 of 12 validation mutants
were killed.

- **B1 (blocking):** fixed. The mint's assurance-certification trace lacked the
  checker's branch ids. The regression test is killed by the pre-fix code.
- **H1, H2, C1:** accepted as boundaries (spec finding 6).

A consumer-gate regression, the `pre_receipt` keyword passed on every call, was found
and fixed (spec finding 5).

## Refactoring review

**None needed.** The change adds one opt-in path. The transition change is 15 lines that
skip only the pre-check. The review showed that `_run_check_raw` ignores its `evaluator`
hook on the anchored route. TP3 works around that without editing `checking_service.py`.
Making the hook honoured there would be a refactor of the anchored route, with no current
need, so it is left as an open question for close.

## Boundary and open questions

- **Receipts are narrow by design:** in-process only, default options only, and never for
  intermediate or post checks.
- **Open for milestone close:**
  - H1: `receipt.report` is mutable;
  - H2: a pre-run that raises leads to two checker attempts;
  - C1: there is no reference-population receipt test;
  - the anchored-route `evaluator` hook;
  - F3 from TP2: the name of the internal accessor.
- **Next:** milestone close, with four local readers, the open-questions sweep and
  carryovers (request 4 / TP4 to a successor milestone; downstream acceptance to the
  reporter).

## Evidence hashes

[
  {"path": "src/gnd/api.py", "sha256": "e6b878926a681ab3708860f46f3a59d6ec4c88cf2544b00fa1b364cc8c875d9e"},
  {"path": "src/gnd/transition.py", "sha256": "d3883314bfe0101cbd8925d9efd32d6d79d1cdf8abe8894c5302d3c2f47a5302"},
  {"path": "tools/measure_transition_cost.py", "sha256": "0a2d74e9fc47d5a1abf6ce6d7c9e2687be214d27ed4e014c24b1bb3edf42645f"},
  {"path": "tests/test_tp3_check_receipts.py", "sha256": "26b57adcca1ac7c2e4765de9daec6312c2c2e20506f5cd2bd99e84dc0e187e39"},
  {"path": "tests/test_public_api.py", "sha256": "e09f653be150e3719ecf8d429a8c2b653119311b46ffb4152a0ebaf9aafbc11c"},
  {"path": "tests/test_public_reference_signatures.py", "sha256": "e1be0fa2c90e34a9c6fe31b3f68bdcf1e725538f0e7f8f87b46b17864900fbf4"},
  {"path": "tests/test_v61_phase2_api.py", "sha256": "d4983daedf24d7582d708da31dfee94374994ac296058809061831e7936de9fd"},
  {"path": "tests/test_public_runtime.py", "sha256": "5070379de83f04cde9858311f21f164799e5c21883171b1351a50b0cc03963c9"},
  {"path": "docs/reference/python-api.md", "sha256": "de0f815e85ffa45f03e020b190b7886810171253906e9b67f5fdfdaf1dd7cd30"},
  {"path": "docs/reference/capabilities.md", "sha256": "efbbed94a6db54fb0f2dbfe979f4cbf8edf4d25b3d15c80de66cbe0ffa27550f"},
  {"path": "docs/release-notes.md", "sha256": "54de7ec2248be9fd31223dda9fbae0c963eaea30faa77fe8946fa4a040a8e307"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP3-spec.md", "sha256": "32ad1d44a591fd752b1cb1dd404c058a5dbe6e134b426a655582fddd31ca7aa3"},
  {"path": ".gnd-planning/milestones/transition-check-performance/notes/phase-TP3-claude-review.md", "sha256": "a318a469e8e8a6130cc1b23be7016e39082faaaf4005c42160bf2d84013e950f"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/consumers-1.txt", "sha256": "383a04c970ad5fd1a738833139c9430b595400af425775e6db5c2690cc7846ba"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/consumers-2.txt", "sha256": "d5c7122ef5199ee4a64aab0e1fa7a407bbaf64a8ea45106962239ad885764178"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/counters.json", "sha256": "8754858f42cd2824a6e3887002d52e6b2f9c96ef6187c05c2087b0a7ce76a4f9"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/digests.json", "sha256": "d736d4d75fd82b7c5fd42102515d6b43eb21946326eaa3ebfd6a5223a1d4ca1c"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/gate-py3.11.txt", "sha256": "bf0ab0b06f169c01049616adceb392829cb9e3739b13aa5dbf7e3d714f013973"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/gate-py3.13.txt", "sha256": "2e3f239a983fc6dcba98f3e10ee9cdc2dce1ab61501f773964c826cd6b17a7df"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/gate-py3.14.txt", "sha256": "4c0491cd606d80170d7fa83bebc19b569a2b8ac379b686f4aed2494e3ca34aec"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/lint.txt", "sha256": "82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/receipt_replay.json", "sha256": "731714fd72242f25df2d340cfa74ac6583a56c9804f7cee5b4350e2b30af4d39"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/receipt_replay.py", "sha256": "3f1308a7cd8a363a30475678613c826c7fc9d13dd76906917382b5f0a9dd9455"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/review-mutants.txt", "sha256": "7be3b08523fe2be03f3c6c93dc13e5ece527c6d2892a4297564448d46ecc56cc"},
  {"path": ".gnd-planning/milestones/transition-check-performance/evidence/TP3/timings.json", "sha256": "8216ced83dfc081925082d37be27ed45d91c85b9f900855da6571007cfe3a22d"}
]
