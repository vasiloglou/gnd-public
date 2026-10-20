Evidence sanitation correction at milestone close, 2026-10-20: edited only the remaining machine repository root to <REPO>; retained prior content otherwise. Pre-correction SHA-256: 2d20591d0c8c2a4766a5fd5db9361381e83865f05f9e73836029b8a7521df369. Historical record digests remain scoped to original commits.

# IE0 independent Codex CLI review

Retained response; absolute repository paths in Markdown links were sanitized
to repository-relative code citations. No other substantive edits. One reviewer
is one reviewer, not a panel. Read-only review; no tests were run by this reader.
Authorization: execution delegation 002, including explicit provider-transfer approval.
Review examined the developing uncommitted diff from 94f4113; some corrections
were made while it was reading, so findings distinguish reviewed/stale snapshots
in the disposition. Repaired bytes receive no implied opinion.

Findings survived. These are static findings; the regression cases below were not executed.

1. **Blocking — the constraint counter measures finding labels, not evaluator execution.** `tools/measure_incremental_evaluation.py:44` counts `_finding_scope`, which runs after verdict computation and also labels vacuous/refused findings. Additional evaluator work is invisible. **Minimal regression:** invoke `_inline_uniqueness_result` twice while producing one finding; require two evaluator events. Conversely, calling `_finding_scope` on an existing verdict should add zero evaluator events.

2. **Blocking — constant counters survive the liveness controls.** `tests/test_incremental_baseline.py:68` checks positivity, then removes the registry entry before its negative and zero controls. **Minimal regression:** initialize registered counters to `1` at tool line 80 and suppress increments at line 90. The body/constraint liveness assertions still succeed, including the direct alias assertion of `1`. Add a real no-derivation check with instrumentation enabled and an exact multiple-execution assertion.

3. **Blocking — acceptance does not enforce liveness or 13/25/19.** `tools/measure_incremental_evaluation.py:278` checks counter names, not values, call counts, or the reporter denominators. **Minimal regression:** take an otherwise accepted document, zero every mandatory counter, and change reporter `calls` to `1`. `validate_evidence` still returns true. The separate replay test does not enforce the CLI’s acceptance contract.

4. **Blocking — measured reporter/course runs lack the full semantic comparison.** `tools/measure_incremental_evaluation.py:228` compares only synthetic check observations. Reporter/course replay comparison at line 319 retains payload digests; recorded branches are ignored by acceptance, and transition extensions/origins are absent. **Minimal regression:** change only the reporter receipt-mode branch set while preserving payloads; require rejection. Add an equivalent transition-lineage corruption case.

5. **Blocking — the partial/possible discriminator is empty.** `tools/measure_incremental_evaluation.py:103` evaluates outside `PARTIAL_OPAQUE`; `observation` also calls default `api.check`. The opaque dispatch therefore removes affected extensions instead of exposing possible patterns, and missing metadata becomes `{}`. `tests/test_incremental_baseline.py:104` merely checks that a case named `partial` exists. **Minimal regression:** require nonempty possible patterns for the opaque recursive control, then alter only a wildcard coordinate and require a `possible` mismatch.

6. **Blocking — equal operational failures count as parity.** `tools/measure_incremental_evaluation.py:235` accepts matching error payloads without checking expected fresh behavior. Saved `.gnd-planning/milestones/incremental-evaluation/evidence/IE0/parity.json:185` and line 200 show both negation controls returning internal-error exit `70`, with empty mismatch lists. **Minimal regression:** supply identical exit-70 observations on both sides; require measurement failure with the case named, rather than baseline acceptance.

7. **Blocking — input identities omit executed inputs.** `tools/measure_incremental_evaluation.py:254` omits `measure_transition_cost.py`, course model/state/plans, recursive fixtures, aggregate fixtures, and runtime JSON schemas. It also records no dirty-path inventory. **Minimal regression:** edit the course state or aggregate population without changing HEAD; require its recorded input identity to change. Currently the manifest remains identical.

8. **Blocking — saved evidence belongs to different implementation bytes.** `.gnd-planning/milestones/incremental-evaluation/evidence/IE0/environment.json:304` records test/tool SHA-256 prefixes `2fa4d06e` / `bac03530`; current read-only hashing produced `29f7cfea` / `b9e62430`. Saved work also lacks the current per-call records. **Minimal regression:** compare evidence hashes and required emitted fields against the reviewed files; reject this evidence until regenerated.

9. **Blocking — required discriminator stories remain unimplemented.** `tools/measure_incremental_evaluation.py:194` adds an alternate recursive support but never deletes a support while retaining the alternative. Reference/options changes have only a prose pointer in `tests/fixtures/incremental_evaluation/stories.json:7`. **Minimal regressions:** delete `B→C` from `{A→B,B→C,A→C}` and assert `A→C` survives with correct origins; separately change a bound reference and a check option and assert their specified fresh outcomes.

10. **Hardening — partial join work is silently omitted.** `tools/measure_incremental_evaluation.py:91` samples join deltas only around `_clause_bindings`. Partial execution indexes candidates through `_partial_bindings`, without entering that function. **Minimal regression:** evaluate an opaque recursive two-atom join under partial mode; require positive partial join work whenever its `JoinWork.join_candidates_indexed` increases.

11. **Blocking — B is not receipt-only for two advertised workloads.** [tools/measure_incremental_evaluation.py:140](<REPO>/tools/measure_incremental_evaluation.py:140) ignores `receipts` for localized and course replay. Their B samples execute the same full route as A/C. **Minimal regression:** spy on receipt minting and consumption during each workload’s B replay; require the declared receipt behavior, or explicitly mark that arm unavailable.

12. **Blocking — timing boundaries are not separated.** `tools/measure_incremental_evaluation.py:175` emits only elapsed replay totals. There are no uninstrumented loading/evaluation samples; `instrumented_seconds` cannot supply that missing split. **Minimal regression:** add controlled loader delay and require only the loading component and total to increase, while retaining raw evaluation samples.

13. **Hardening — the receipt probe never demonstrates its stated consequence.** `tools/measure_incremental_evaluation.py:243` mutates a report and returns a literal consequence without invoking a transition. Its initial fixture exits `1`, so that receipt is non-reusable. **Minimal regression:** mint a reusable receipt, mutate its report, consume it through `api.transition`, and compare with a fresh control. The current probe would still pass after consumption was repaired.

Checked: counter owners/liveness, 13-call structure, 25/19 enforcement, seven semantic surfaces, timing arms and rotations, input identities, all seven story groups, receipt probing, and runtime-edit scope. The reporter’s 7-check/6-transition structure, rotation formula, and fresh loading per replay are consistent by inspection. No runtime-source or legacy-fixture edits appeared against `94f4113`.

Limits: no tests or benchmarks run; no files modified; no credentials, providers, networking, or panel used. Saved execution artifacts were inspected, not treated as fresh verification.
