# v7.1 Phase 1 temporal corpus

This is the proposed owner-marked input corpus for calendar-day Duration in guarded comparisons. `inputs.json` names each scenario, domain, public surface, exact edit to a base model or population, and a short story. The two base domains are `dispatch/` and `release/`; neither depends on wall-clock time or external services.

Read `inputs.json` and the base files first, then predict each public result. The separate `answers.json` holds expected exits, targeted verdicts and selected reason codes. `manifest.json` records file sizes and SHA-256 digests for the corpus bytes. `tests/test_v71_phase1_dates.py` is the executable harness; it checks the exact answer key, legacy controls, and all B01–B43 branch labels.

The corpus is deliberately RED against the pre-Phase-1 implementation. An unsupported model version can make several cases fail at the shared control, so a RED result alone does not establish the case's later behavior. Owner approval of these fixture and answer bytes is required before implementation.
