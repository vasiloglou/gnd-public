# Codex review of the report-output-fidelity close

Reviewer: Codex (gpt-6-sol, xhigh, read-only, prompt on stdin:
[review-prompt.txt](review-prompt.txt)). The owner selected it ("One Codex
reviewer", 2026-11-09). Subject: the draft close at d38670e9 on branch
claude/report-output-fidelity-close (PR 145), `git diff 8eb4fe60 d38670e9`.
One reviewer is one reviewer.

## Triage

Every finding was reproduced from the cited bytes before it was acted on.

| ID | Reproduced | Class | Disposition |
|---|---|---|---|
| K1 | yes: plan section 2 item 3 and ROF4 R1 both name designs (b) and (c); 154 is ROF4's inventory of files with a `model_digest` field | blocking | **fixed**: plan section 11 row 1 names both designs and calls 154 an inventory |
| K2 | yes: ROF3 spec D4 (`model:identity-unrepresentable`, flagged against plan section 2), ROF3 spec D6 (corpus pin plus census), ROF4 spec D2 (a) (legacy-only message) | blocking | **fixed**: plan section 11 rows 4-6; close record "Plan repair" |
| K3 | yes: ROF4's last full suite ran at d83e972c; its record says the suite was not rerun after merging main | blocking | **fixed**: predicate 3 marked pending at 8eb4fe60 until gates 1 and 2 |
| K4 | yes: ROF4 spec T10, 14 `steps.json` plus `recordings/TASK.md` | completeness | **fixed**: predicate 3 row; plan section 11 row 7 |
| K5 | yes: `output.py:663` is `_print_derived_change_summaries`, `:675` is `_print_check_verdicts` | hardening | **fixed** |
| K6 | yes: 003 Size (1.76x source, not paused), 004 Size (1.55x tests), 004 review P7 | completeness | **fixed**: three sweep rows |
| K7 | yes: ROF4 spec I2 and I5; PRs 135 (859b852d) and 136 (54554bf0) are ancestors of 8eb4fe60 | completeness | **fixed**: refuted premise I2; sweep row for I5 |
| K8 | yes: plan predicate 1 excepts `validate --trace` and `validate --document` | completeness | **fixed**: predicate 1 row |
| K9 | yes | completeness | **fixed**: "What the close still needs" lists the two runs |
| K10 | yes | hardening | **fixed**: the older README status is labelled as history |

The corrected record was not re-reviewed.

## Review output (verbatim)

DISPOSITION: block

ID: K1  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:390  
QUOTE: “emission needs a new report version for each live version … and moves 154 tracked fixture files”  
PROBLEM: Approved plan §2.3 and ROF4’s R1 question preserve two possible emission designs: a version per live ladder **or** one additive successor shape. The 154 figure counts files carrying `model_digest`; it does not establish that either design moves all 154. The amendment overstates the cost and narrows the choice the owner was given.  
FIX: State both designs and describe 154 as the measured inventory, not a required set of changed files.

ID: K2  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:150  
QUOTE: “Phase records named one plan repair: ROF4’s R1”  
PROBLEM: Other approved plan wording remains contrary to delivered work. Plan §2 names `transition:operations-digest-unrepresentable`, while ROF3 spec D4 explicitly rules `model:identity-unrepresentable` and flags the departure. Plan ROF3-C3 calls for a pinned 306-model legacy digest list; ROF3 spec D6 rules a smaller corpus pin plus census evidence. Plan ROF4-C2 requires a wrong-pin message naming the expected values; ROF4 spec D2(a) explicitly retains messages naming only the legacy value. Section 11 records none of these qualifications.  
FIX: Add proposed amendment rows retaining each r3 clause and citing the corresponding owner-approved spec decision.

ID: K3  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:92  
QUOTE: “pre-milestone artifacts verify … | yes”  
PROBLEM: This is stated as holding on main `8eb4fe60`, but the ROF4 record’s broad run was at `d83e972c`; it says the full suite was not rerun after that phase’s merge. Main then gained other PRs. The pending close runs are the evidence intended to establish this main-level compatibility claim, including the fixture and generated-plan classes. Their pending state is correctly disclosed elsewhere, but this unqualified “yes” depends on their results.  
FIX: Limit “yes” to what the phase evidence established and mark verification at `8eb4fe60` pending until the close runs finish.

ID: K4  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:92  
QUOTE: “the 15 shipped pins plus the new canonical example”  
PROBLEM: ROF4 spec T10 and its record distinguish **14 executable** legacy `steps.json` pins from `recordings/TASK.md`, which only quotes a digest and is checked for byte preservation. Calling all 15 verified pins obscures that difference; approved plan ROF4-C3 also incorrectly calls all 15 executable.  
FIX: Say “14 executable legacy pins, the byte-preserved TASK.md quote, and the new canonical example,” and qualify ROF4-C3 in section 11.

ID: K5  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:128  
QUOTE: “`_print_check_verdicts` and `_print_derived_change_summaries` … (`output.py:663`, `:675`)”  
PROBLEM: At main `8eb4fe60`, `output.py:663` defines `_print_derived_change_summaries`; `:675` defines `_print_check_verdicts`. The cited line numbers are reversed.  
FIX: Swap the numbers.

ID: K6  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:119  
QUOTE: “## Open-questions sweep”  
PROBLEM: The sweep omits recorded size findings: ROF2’s source additions reached 1.76 times its estimate without the plan’s required pause (`003-phase-ROF2.md:162–167`), and ROF3’s tests reached 1.55 times their estimate (`004-phase-ROF3.md:162–170`). It also omits ROF3 review P7’s proposed T8/T12 repairs, which were argued rather than applied (`004-phase-ROF3.md:147–148`). These need explicit dispositions under the requested sweep scope.  
FIX: Add rows naming the deviations and P7 limit, with their acceptance evidence or a named carry target.

ID: K7  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:156  
QUOTE: “## Refuted premises”  
PROBLEM: ROF4 spec I2 also refutes its approved T6 expectation of byte-identical mixed-sidecar output: `corpus[].sidecar_sha256` necessarily changes. ROF4 spec I5 records two crashes found during corpus authoring and routed to PRs 135 and 136; neither appears in the sweep, although both PRs are in the history of main `8eb4fe60`.  
FIX: Add I2 to refuted premises, and sweep the two crashes as closed by their respective PR merges.

ID: K8  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:90  
QUOTE: “`validate` … The body is rendered from the projected tree only.”  
PROBLEM: The approved predicate expressly qualifies `validate --trace` and `validate --document`: they print from the model or an early return, outside the projected tree (`report-output-fidelity-plan.md:34–36`; ROF1 spec §6). The table omits that qualification from its “yes.”  
FIX: State the two route exceptions in the predicate row.

ID: K9  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/report-output-fidelity/006-milestone-close.md:190  
QUOTE: “## What the close still needs”  
PROBLEM: The list names review and ruling but omits completion, retention, and comparison of the two pending beast-3 close gates. This is a missing next step in a section presented as the complete close checklist; the pending runs themselves are properly disclosed and are not a finding.  
FIX: Add the two run results and their failure-set comparison before the review and close ruling.

ID: K10  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/report-output-fidelity/README.md:12  
QUOTE: “ROF4 implemented … awaiting its PR and merge. ROF5 onward are outlines.”  
PROBLEM: The newly added status paragraph says ROF4 merged and ROF5 was withdrawn, but the older bold “Status” paragraph remains written as current.  
FIX: Mark the older paragraph as dated history, or update its status claims while retaining the chronology.

CONFIRMED: By reading commit bytes only, all eight nonpending front-matter SHA-256 values match `d38670e9`; the phase table’s focused-gate summaries, review counts, PR numbers, and merge commits match the phase records and retained issue/PR states. The identity helper, D7 documentation, and ROF2’s replacement of ROF1’s deferred projected-text work are present on main `8eb4fe60`. The record distinguishes relayed R1 and ROF4-O1 rulings from tests and review. I did not run the test suite; conclusions about behavior and gate coverage are from the records and code inspection.