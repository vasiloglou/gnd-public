---
milestone: compiled-snapshot-obligations
station: ci-repair
skill: n/a -- owner-selected local CI follow-up
scope: ci-repair
date: 2026-10-13
---

# Claim

Reproduced CI failures have bounded repairs: default measurement scope retains
its predecessor denominator; additive API pins accept the approved keyword;
witness timing accounts for defining-module reference validation without
changing its ten-second threshold. This is supplementary to the closed phases.

## Evidence and gates

The owner's request selects local CI explicitly. Initial clean full regressions
at 5c2813b ran in separate temporary git clones after the workspace's nested
historical worktree caused an unrelated reference-closure failure. Full runs and
installed acceptance were still in flight at this repair commit; no green full
CI claim is made here.

The exact frontier and checker-signature controls reproduced red (two failed).
Another API signature pin reproduced red (one failed, 28 passed). Default
measurement reproduction failures share the broadened-denominator cause; their
complete 17-test payload group now passes byte-for-byte without editing fixtures.
The deterministic timing control reproduced 17 simulated seconds with only 15
accounted; adding the defining-module lookup accounts for all time. The profiler
and Ubuntu CI identified repeated inherited schema validation, not witness
inference, in the measured interval. Profiling overhead is not a native timing
acceptance result. Existing timing thresholds remain unchanged.

    264 passed in 302.08s (0:05:02)
    264 passed in 280.46s (0:04:40)
    93 passed in 14.97s
    93 passed in 14.44s
    17 passed in 22.10s
    All checks passed!

The 264-test commands were uv run pytest -q tests/test_witness_timing_measurement.py
tests/test_public_v71_witness_corpus.py --tb=short on Python 3.11 and 3.13.
The 93-test commands selected measure_derivation, the exact failed coverage and
negative-control nodes, v61_phase2_api, witness_timing_measurement,
compiled_snapshot_obligations and rf1_layering. The 17-test command selected
public_measure_corpus and public_measurement_publication. Logs are retained.
Ruff and whitespace checks exited 0. Existing default frontier exact-member
controls are unchanged; no new opt-in coverage is claimed for synth or measure.

## Review and refactoring

One local reader reviewed the repairs and deterministic control and found no
blocker. One reviewer is one reviewer; notes/ci-followup-review-one.md retains
the opinion. Its documentation suggestion is applied to the frontier docstring.
None needed beyond the actual lookup seam and explicit inactive-lane boundary;
no new source refactor, shim retirement or authority transfer occurred.

## Boundary and open questions

No complete green local/cloud CI or final installed candidate claim at this
record. Final acceptance of repaired committed bytes belongs to the subsequent
CI completion record. The existing cloud macOS instability is a measured
runner-stability refusal and passed locally; no threshold has been relaxed.
Original app acceptance and admission support carryovers remain with their
owners. No certification, release or merge is established by these gates.

## Artifact identities
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/api-pin-red.log: d03e58c7effc5a63ec987da9dbae94ae94fc802cd7836aa4565c28c74624b1fb
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/corrected-controls-3.11.log: 9ae232cd57f92df1f4ccdcdf513f60193f3decc90f833a79d10de9bda05ffaca
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/corrected-controls-3.13.log: 044d95b2cd45adfb8ecf596ea3b2007887ce2633a663715998c5366f2831bae2
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/measure-controls-red.log: 1d604bfaffa9d288cf7afda0d147a114da0fa5cb301a72a57b8ed3300297f4bc
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/measure-payload-corrected.log: bf748531ec0085a97bd3b79bca2ef3ea3887d0fe8748ea4ebac037e5da373c45
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/timing-control-red.log: f5c7dc39e95fc413888a1516fdf0d3017ae880a4f3599ab8145aed0355052bd8
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/witness-corrected-3.11.log: 997ae24a164550210ab06d6b51ef3a9b31c3490f2df36049fb3a43a493279e98
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/witness-corrected-3.13.log: 169b163807708dc3160ea684b91693ecd2e85c406a27920c474b44e57e0bd5e6
- .gnd-planning/milestones/compiled-snapshot-obligations/notes/ci-followup-review-one.md: 0a58d3832c0f79e4b22a8d9f325fe90f8e7bd4b5498b76b9c4c5db716beab0ab
