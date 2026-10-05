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

## Owner approval — 2026-10-03

The owner said “go with your recommendations” after the business explanation.
A1 and A2 are approved, including two legitimate cleanup failure labels and
four total final validation attempts. Performance thresholds and runtime
semantics remain unchanged. Approval binds proposal SHA-256
`ff1555916b3846de54d8f18eb79a51f03d1cd57e192b7ec3beda2344763974ca`. No further reviewer is authorized.

## A2 implementation finding — first join stage, 2026-10-03

Attempt 3 preflight returned one timing failure and 86 passes on each platform.
macOS measured 0.103165792s / 0.216924292s against 0.206331584s; Ubuntu measured
0.166367904s / 0.349950274s against 0.332735808s. Isolation did not suffice.
No threshold or expected verdict changes. Attempt 3 is canceled after these
conclusive failures; one approved final attempt remains.

Concrete behavior-preserving repair under A2's diagnosis/repair authorization:
keep _indexed_guarded_bindings(constraint, snapshot, work=None) unchanged at its
interface. After validating and constructing first-atom candidates, use them
directly as the initial bindings rather than indexing an empty shared key and
merging each with an all-None seed. Charge work once per candidate exactly as
the existing merge does. Preserve candidate multiplicity, order, literal and
repeated-variable checks, malformed-input refusals, later joins and final
canonicalization. No new cache, scalar ordering, public output or semantic rule.
This is a reproduced runtime performance repair to the original zero-runtime
estimate, within the approved requirement to preserve runtime semantics.

Focused parity against the unchanged semantic oracle must cover first-atom
variables/literals/repetition/empty matches, subsequent joins, and exact work
limits. Keep the original timing test as the pre-fix red. Check downstream
correspondence/witness/reference consumers and retain candidate rebuilds and
source-delta disposition. No further reviewer or candidate attempt is implied.

The first-stage change alone improved local time only slightly. A bounded probe
found repeated canonical scalar construction (one repeated string converted six
times) and measured about 20% lower time with invocation-local reuse. Extend the
behavior-preserving repair to adapt_snapshot: cache only exact builtin scalar
inputs by (Python type, value, primitive), share frozen Scalar values across
relations/rosters, and discard the cache on return. Opaque/hostile non-builtins
use the original conversion path. Preserve every occurrence, origin path and
raw admitted value; no global state or cross-invocation cache. _roster/universe_of
receive an optional internal converter, defaulting to their original behavior.
A pre-fix control observes six conversions; exact snapshot/observation equality
and three distinct origins must survive one conversion after repair.

The remaining join repair reuses a binding when an indexed match introduces no
new variable, and copies only newly introduced positions otherwise. Shared-key
identity already equals scalar_identical; all candidate cells were validated
before indexing. Preserve one output occurrence and one work charge per match,
including duplicate candidates. This reduces allocation without changing keys,
join order, canonicalization or malformed-input checks. Parity against the
unchanged reference evaluator and exact 100000-work boundary cover this path.
