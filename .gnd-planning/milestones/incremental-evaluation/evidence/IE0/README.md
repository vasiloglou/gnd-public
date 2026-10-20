# IE0 baseline — evidence interpretation

Current baseline collection uses the locked editable package on Python 3.11.15
and uv 0.10.10. Machine/source/fixture/config identities are in environment.json.
The old reporter workload is 13 public calls (7 checks, 6 one-step transitions).
Course controls replay all three attempts as complete walks, including refusals.

Measured before optimization:

| Reporter mode | Checker runs | Executed derivation bodies | Constraint evaluations | Fingerprint nodes |
|---|---|---|---|---|
| full | 25 | 4,878 | 1,796 | 1,438,732 |
| receipts | 19 | 4,878 | 1,365 | 1,119,220 |

The receipt-only path saves no counted derivation bodies in this fixture. It
saves precheck dispatch/constraint work and some fingerprint traversal. The
reporter uses exact recursive stratification and 65 structured derived heads,
so an acyclic-only optimization cannot meet its acceptance target.

`targets.json` freezes the receipt baseline denominator and strict work-reduction
target before optimization. No performance target is inferred from wall medians.
`work.json` includes per-call evaluation counts and separately the whole replay;
loading/driver overhead can therefore be distinguished from public calls.
`parity.json` covers two independent full evaluations of each local discriminator,
including complete extension rows/lineage, unavailable and possible state.
Reporter full/receipt payload digests are also compared. No CLI/batch branch
trace is claimed from these in-process observations.

Timings use A=full, B=receipts, C=independent full, rotating ABC/BCA/CAB.
`public_evaluation_samples` time only public calls; `loading_and_driver_samples`
is the residual total including loading and driver overhead, not a pure parser
microbenchmark. Measurements are uninstrumented and informational.

The first exploratory run overlapped focused tests and was superseded by a final
serial collection after tool/identity repairs. Do not compare that exploratory
wall time to a later candidate. Final identities must match the retained source
when this phase is recorded.

## Eligibility and planning estimate

The family census deliberately marks unresolved reuse as fresh. IE1 must prove
input classification; IE2 must retain recursive lineage and unavailable state;
IE3 must preserve constraint/order/reference behavior. Public controls establish
that the full evaluator discriminates these cases, not that reuse is safe yet.
The receipt report is mutable; IE3 owns the integration prerequisite fix.

Provisional remaining effort estimate (agent judgment, not a measured delivery
promise): five implementation phases, with most uncertainty in IE2's complete
recursive envelope and IE3's constraint integration. Budget approximately 1–2
focused engineering days each for IE1, IE2 and IE3, and 1–2 days combined for IE4,
IE5 and close, assuming the public fixture is representative and no new semantic
counterexample forces redesign. This estimate has no committed calendar date;
new-workload acceptance remains unavailable until the reporter supplies it.

No SQL, private data, question text, 547-program census, native lane, publication
or certification was run. Current runtime bytes are unchanged in IE0.

## Final acceptance

The final serial collection exited 0 on the matched public-precheck course
driver. Its identity map matches final source/test inputs. Full/receipt/fresh-full
semantic and branch checks pass. Course has three walk results / six public
API calls per mode: 18 full checker runs vs 15 receipt runs, and 93 body
evaluations in either mode. Earlier unmatched-course results were refused and
are retained only as a refuted experiment, with no passing acceptance claim.
The new reporter-dependencies census lists each observed fact delta and the
transitive structured heads it affects; these are feasibility data, not a
claim that an incremental implementation already works.
