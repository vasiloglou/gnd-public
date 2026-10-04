# Phase 4.1 review dispositions

R1, blocking documentation defect: the documented rai command returned usage
exit 64. A new test executes each of the CLI table's 46 command routes with
--help, using the actual documented token sequence. Pre-fix result: that route
failed, other routes passed. Corrected to rai-orm RAI_MODEL. This proves route
existence, not execution of every contextual operation or provider workflow.

R2, misleading scope explanation: the snapshot model has no operations; a
supplied approved snapshot passes without any chronology input. Removing its
recorded submission fails mandatory/subset constraints. This reproducible
semantic probe refutes the overview's event-order implication. README and home
now say approval without a recorded submission. No runtime change or artificial
phrase-presence assertion was added: the approved plan explicitly calls for
meaningful behavioral checks instead of prose keyword pins. The expense chapter
and transition guide already explain the distinction.

R3, hardening of this phase's own gate: current wheel hashes matched, but the
validator did not enforce that relationship. A controlled main() test supplies
matching versus different valid ZIP payloads while stubbing external build and
install processes. Before repair, the different-payload case failed with DID
NOT RAISE AssertionError. The new equality assertion refuses before writing a
success results.json; both controls now pass. Real direct/sdist-built wheels
still match and separately execute 100 documented blocks.

S1, blocking final-example gap from the criterion coverage audit: BookRec's
evolved contract expected the old default command to succeed. Its declared
smoke returned 1 rather than 0. The exact executable smoke block was inserted
in chapter 6 and the tutorial test observed red before fixing the declaration.
A preceding block now updates only the developer-owned success row with
--preferred-only; the unknown-user refusal stays intact. The smoke block uses
GND's existing versioned runner, checks outcome.passed (including startup), and
gives each row a separate scratch directory. A final conformance command checks
the amended contract. These blocks execute in every installed learning path.

Initial independent terminal review: 3 findings; 2 blocking documentation
issues and 1 in-scope gate hardening. Supplemental coverage audit: 1 blocking
example gap. All four reproduced and addressed. No follow-up model review was
run; the repairs were small and their observable consequences were tested.
No panel or independent external-user trial is claimed.
