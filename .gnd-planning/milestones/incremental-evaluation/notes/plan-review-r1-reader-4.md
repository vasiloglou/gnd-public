# Reader 4 — measurement design

Reader 4 verdict: **approve-with-fixes**. No blocking finding survived this bounded static review.

Reviewed subjects:

- `.gnd-planning/milestones/incremental-evaluation/notes/incremental-evaluation-plan.md`: SHA256 `34b1004e9d7e5e60f3162dae423e78b3d42bf98678edcccc0ad358517f086de1`
- `.gnd-planning/milestones/incremental-evaluation/notes/phase-IE0-spec.md`: SHA256 `d49a5bcc4f06b5f1b500bd231637d54dcedc2bd9778976ba5817edb6a9ba19da`

Inspection HEAD: `058874965c54c19c4a4c34855cc9ca1b789394bf`.

Lens: measurement design, denominators, counter liveness, fair baselines, reproducibility, performance claims and IE0 feasibility. Read AGENTS.md, both complete drafts, existing measurement tool/test/fixture provenance, TP0 evidence record, prior close record and reader-4 close review, plus relevant extension calculation/preparation code. No files edited; no tests, benchmarks, providers or credential access.

## R4-F1 — define the timing schedule for all three declared modes and supported repeat counts

Class: hardening. Severity: medium.

Citations:

- `.gnd-planning/milestones/incremental-evaluation/notes/phase-IE0-spec.md:99–100` permits `--repeat` 1 through 7.
- Same file, `166–169`, declares three modes—full stateless, receipt-only and a second fresh full control—but specifies two-arm `AB / BA / AB`.
- Same file, `218`, makes exact `AB/BA/AB` the timing-order test.

Observable consequence: the schedule and acceptance test can pass while the third declared control is omitted from paired measurements or consistently runs last. Implementations can also disagree about whether `--repeat 1` means one pair, the fixed three-pair schedule, or three-mode sampling. That weakens reproducibility of the timing deliverable, even though timings correctly remain nongating.

Evidence: this is a direct inconsistency between the declared mode count, CLI range and prescribed schedule. The predecessor tool does not resolve it: `tools/measure_transition_cost.py:309–317` measures one replay mode repeatedly without an interleaving scheduler. The prior close explicitly carries this measurement-tool gap at `.gnd-planning/milestones/transition-check-performance/006-milestone-close.md:131`.

Minimal remedy: name each timing arm and define either explicit two-arm comparisons with their full control, or a three-arm rotating schedule. Specify how its first `repeat` rounds are generated for every accepted repeat value; update T7 to assert mode membership, sample counts, order and absence of instrumentation.

Other assessment:

- Reporter denominator is concrete: 13 public calls, with fresh verification of the historical 25/19 checker counts. Counter totals remain separate from public payload parity.
- Body/evaluator counters require actual lookup owners and deliberate inert-counter negatives. Missing required comparison surfaces fail acceptance.
- Existing course replay only uses attempt 3 (`tools/measure_transition_cost.py:190–198`); implementing the spec must also use its existing attempts-1/2 surfaces (`173–180`) to satisfy the draft’s explicit failing-attempt requirement. This is already required by the draft, so no separate finding.
- Static source inspection supports IE0 feasibility without runtime edits: calculator/body helpers, work records and fingerprint traversal provide plausible tool-side observation points. This does not establish implementation effort or measured runtime.
- Receipt-only comparison is present in the planned acceptance matrix. Final reporting should attribute incremental savings using that measured arm as well as full stateless evaluation.
- New-workload absence, timing limitations, conservative fallback, frozen targets and the prohibition on extrapolating to all 547 programs are handled explicitly. Historical results are appropriately treated as motivation rather than fresh verification.

Supporting reviewed identities: measurement tool SHA256 `0a2d74e9fc47d5a1abf6ce6d7c9e2687be214d27ed4e014c24b1bb3edf42645f`; measurement tests `e620f7a3f662e49bed479e95b7b82564237c35ae1bd9d67db77dffdf3aa68480`; fixture call manifest `d843ec0261700d213b0090b4182f6883dff2e322171ae0f121f237f87e83e39a`; prior close `1a119f68700beb557f24a58075d41f547966ad70b06fccbfe79b37cd51f35ae1`.
