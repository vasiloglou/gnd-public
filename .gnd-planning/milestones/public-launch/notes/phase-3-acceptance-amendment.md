# Phase 3 acceptance amendment — awaiting owner decision

Date: 2026-10-03. This is a proposed bounded amendment, not a completion claim.
The approved resumption spec remains authoritative until this decision clears.
PR 1 and main protection remain in effect. No publication or runtime change is
proposed here.

## Evidence and business meaning

The first complete hosted macOS diagnostic run returned 10 failed, 11291 passed,
400 deselected, 1 warning in 1675.32s. Seven failures were missing documentation
already repaired and included in current final attempt 2. Three further issues:

1. An offline Souffle proof-depth test patched output but still located a real
   executable. Reproduced on Python 3.13 with PATH limited to /usr/bin:/bin:
   1 failed, 3 passed in 3.61s. The local two-line fixture repair explicitly uses
   the existing fake tool; all ten neighboring tests pass in 1.97s under that
   same PATH. Original proof-depth expectations stay unchanged; no runtime edit.
2. The direct-parent-exit process test requires only timed-out for a descendant
   retaining output pipes. Controlled scheduling reproduced two current outcomes:
   no scheduling delay gives timed-out; an 0.08-second scheduling delay gives
   failed. Both terminate the process group, report cleaned=true, and prevent
   the descendant marker write. The implementation explicitly classifies early
   forced cleanup as failed and deadline expiry as timed-out. This is a result
   label distinction, not evidence of an escaped descendant.
3. The guarded three-atom join benchmark observed t10k=0.08564866699998674 and
   t20k=0.23862479199999598, failing t20k <= max(2*t10k, 0.2). Four isolated local
   Python 3.13 measurements retain the exact bound and pass (t20k about 0.114s).
   The hosted failure remains real and unresolved; local passes do not erase it.

## Decisions proposed

A1 — Accept the two legitimate failure labels for the orphan-pipes case when
all lifecycle guarantees hold: process_group_cleaned must be true, termination
must be terminated or killed, and the delayed marker must remain absent.
Keep the detached-stream case's exact failed expectation. Add bounded scheduling
controls exercising both early-detection and deadline paths, preserving the
original 0.2-second deadline and 0.05-second termination grace. This changes an
expected-result set and therefore needs explicit owner acceptance. Do not alter
runtime classification or silently treat the old assertion as having passed.

A2 — Permit two additional final candidate-validation attempts (four total),
with focused diagnosis/repairs between them. Diagnose the guarded benchmark on
the declared profiles while preserving its input sizes, exact numerical bounds,
three-sample minimum, and expected verdict/binding count. No skip/xfail, marker
reclassification, threshold relaxation, or runtime semantic change is authorized.
If a runtime repair or a changed performance contract is necessary, present its
concrete design and impact rather than accepting an unresolved failure.

Keep the reviewer budget exhausted at two calls; final fixture repairs carry
reproduced controls and neighbor evidence, not a third independent review.
The incremental authored ceiling remains 800 lines plus the completion record.
Additional hosted runs must remain bounded by the existing workflow ceilings.

## Work already completed within the existing approval

The fake-tool repair is reviewable in tests/test_public_souffle_successors.py
in the target working tree. It is not pushed and has not triggered another
candidate run. Both approved final attempts have been launched: attempt 1 was
canceled after known defects; attempt 2 remains running at d7f3acb. The current
run cannot include the newly reproduced fixture repair. Its outcomes remain
separate evidence, with no third attempt before this amendment is approved.

## Proposed verification and boundary

Run the new scheduling controls red against the old expected-result contract,
then the full agent lifecycle module and existing fake-tool module with the exact
bounds and cleanup assertions. Inspect the benchmark's actual hot path and
record focused profile results; final full-suite acceptance must still pass.
Re-run the retained-candidate checks and both required hosted profiles after
repairs within A2's attempt budget. Retain every failure.

The remaining phase, PR-only, source ownership, publication, certification and
candidate sign-off boundaries stay unchanged. No phase-completion record is due
while any required gate fails or is pending.
