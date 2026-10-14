# Phase13 Astra/high round1

Retained reviewer response; edited only to sanitize absolute paths.

**Round 1: no demonstrated runtime regression; one hardening finding in the scope-boundary test.**

**H1 — The owner test does not exercise selected dynamic refresh.** At [test_m3_transition_preparation.py:99](<GND_WORKTREE>/tests/test_m3_transition_preparation.py:99), every non-PRE view is labelled `"refresh"`. This includes the final computed-post view at [transition.py:2101](<GND_WORKTREE>/src/gnd/transition.py:2101).

The concrete input is the existing `recursive` fixture plus `visit.steps.json`: `visit` changes only `visited`, while `reaches` depends on `edge`. Consequently, the selected-refresh call at [transition.py:1975](<GND_WORKTREE>/src/gnd/transition.py:1975) is not reached. The assertion at test line 116 therefore establishes step/post-view ownership, but not selected-refresh ownership.

A focused reproduction is to record `kwargs.get("refresh")` in that observer and require a nonempty selected-refresh observation: this fixture cannot satisfy it. I did not execute that reproduction. The gap is demonstrated by the fixture and dispatch logic; it is **not evidence of incorrect runtime output**. Harden this phase’s boundary control using the existing dynamic aggregate scenario at [test_v62_phase4_composition.py:43](<GND_WORKTREE>/tests/test_v62_phase4_composition.py:43), asserting that an actual selected refresh occurs after the initial owner has ended.

Claims verified by inspection:

- The sole runtime change is the imported scope and wrapper at [transition.py:1920](<GND_WORKTREE>/src/gnd/transition.py:1920). Reference binding and operation lookup precede it; initial preparation retains its statement order; steps, refreshes and intermediate loads follow its exit.
- Standing compiled verdicts still consume raw `pre.facts`. Neither checker nor structured-view dispatch was replaced.
- Existing owner identity checks, `finally` restoration, full-content/exact/partial/limits/helper keys, aggregate bounds, result cloning and branch replay remain unchanged.
- Reference-bound checker populations receive their own scope when identity differs. Opaque filtering is distinguished by relation contents; the low-level decorator does **not** independently check population identity.
- Selective/prior/observer/witness/reference-work fallback remains intact. No public API/schema, compiled-budget, cross-call or effective-post cache change was introduced. Layer allowances remain zero.
- The principal regression compares the complete public report, captured branch set and complete initial `StructuredExtensionView`, including work, **before** asserting zero repeated initial body calls. RED evidence shows those parity assertions passed before the expected `3 != 0` failure.

The spec/test hashes match approval; reviewed runtime/test hashes also match `phase-13-review-approval.json`. Retained evidence reports **9 direct passes, 120 focused passes and lint green**. I read those results; I did not execute them. The green logs alone do not identify exact invocation selections or bind runtime hashes.

Current-byte native **3+3 root/report parity**, body-count diagnostics, **app90**, and the complete-question probe remain unestablished here. Phase12 timing does not establish phase13 performance. Original **all-cap8/109 agreement** and **successful 29-heldout median ≤15s** remain unmet.

**One reviewer is one reviewer.** Read-only review against `35af996`, including RED commit `50f64db`; no tests, mutations, credentials, provider tools or broad replay. No merge or milestone-closure authority is implied.
