# Amendment A2 review four — plan and repository compatibility

Date: 2026-10-13
Instrument: owner-selected independent local reviewer (read-only)
Subject: `notes/plan-amendment-a2.md`, SHA-256 `555a0e76ed41364bb05c9db34897727c85a556640171de01e363b07b6589c3d1`

**Verdict: fail** (one blocking).

1. **Blocking.** "PA6 reruns its unchanged gates" is false: committed PA6 code (1d6c0c6, 81ae7bb) pins
   the learning-path shape `(7,52,2)`/`(4,34,3)` (tools/accept_pyrel_applications_install.py:67), page paths
   (:179), counts (tests/test_pyrel_applications_install.py:61) and the native_query.py resource inventory
   (:35,44); PA6 spec prerequisite is "PA5 c9432b0/009 complete" (phase-PA6-spec.md:3,77); plan sequence §3
   (plan.md:131). Repair: PA5 → PA5R → PA6, amend §3, new delegated PA6 spec gate for harness constants,
   inventory and prerequisite; prior PA6 runs superseded but retained.
2. PA5R must re-satisfy PA5-C1..C6 in full: six graphics placed, rebound and re-reviewed.
3. D3 must not weaken PA5-C1/PA6-C1: shown output includes disposition, rule and witness for refusal/repair;
   pytest extracts commands from the page blocks.
4. A shipped lower-cap model is outside the frozen corpus; prefer the chapter 3 evolve path or a recorded corpus ruling.
5. D1 rules: no layer-map entry needed; GND-free seam API test; emitted-program digest change recorded as a new
   intentional expectation; RF1/RF2 private-name pins (tests/test_rf1_helper_pins.py:401,455) unchanged.
6. Record inconsistency: effectiveness via a delegated gate record; D1 relocation marked a delegated adjustment of O3.
7. No review budget: copy A1's; PA5R uses the selected Claude phase reviewer; junior read is an extra reading by it.
8. Jargon ban may rename but not remove unknown/vacuous/warning and completion-vs-acceptance distinctions.

Orchestrator reproduction 2026-10-13: finding 1 checked at the cited lines.
