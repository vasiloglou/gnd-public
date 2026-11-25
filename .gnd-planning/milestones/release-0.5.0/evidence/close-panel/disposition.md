# Close panel: dispositions

The standard GND panel read [007-close-candidate.md](../../007-close-candidate.md)
at SHA-256 `039e7ab5dff0c30a241ad0ee6f67e4bfc262059699bd1cc064bbe9a31adf6376` (commit `d1da80bf`), from a disposable clone of
that commit. Five of six seats returned schema-valid responses at effort xhigh:
claude, codex, qwen, gemini and glm. Kimi's seat exited nonzero and gives no
opinion. Verdicts: codex `block`; claude, qwen, gemini and glm `revise`. The
[report](PANEL-REVIEW.md) accounts for all fourteen concerns in three agreed
groups and seven single-seat concerns. Each concern was checked against the
cited bytes before it was dispositioned.

| Concern | Seats | Class | Reproduced | Disposition |
|---|---|---|---|---|
| RC07-prepublication-owner-check | codex | blocking | yes: the plan (RW-D12) and the dossier's act 1 put the owner's content and history review before the upload; 006 records it as not stated | **settled by the owner**: asked at the close, the owner answered "Review done" ([receipt](../close/owner-statements.txt)). The close records that the answer has no date, so whether the review preceded the upload is not shown |
| act 3 credited to the owner's words (agreed) | claude, glm | completeness | yes: 006 says act 3 ran without a separate request | **fixed**: the publication row and the authority bullet say so; the sweep records it as Q20, accepted |
| unreviewed bytes understated (agreed) | claude, glm | completeness | yes: the status file lists fifteen paths; the candidate named four kinds | **fixed**: close-results lists all fifteen with the predicate each supports and the instrument in place of review |
| owner words not pinned (agreed) | claude, qwen (two concerns) | hardening | yes: owner-statements.txt was cited and not pinned; the close request and the words behind 0.5.1 had no receipt | **fixed**: a close receipt quotes them whole; both receipts are pinned in the candidate |
| lane errors and RC-02 beside the lane | qwen | completeness | yes: the candidate gave the errors without their disposition or the skips' cause | **fixed**: RC-02's carried disposition and the 13 skips (`tests/test_guarded_clause_exports.py` without `GND_PYREL_PYTHON`) are stated beside the lanes |
| freeze lane without error and skip counts | qwen | completeness | yes | **fixed**: the RW2 row gives them |
| contradictory Python profile | gemini | completeness | yes: the limits named one profile, the lanes ran on another | **fixed**: the limits name all three profiles |
| R1 amendment authority | qwen | hardening | partly: the repairs named their raising records and not the clause that authorizes them | **fixed**: the candidate states that close-found repairs fall under the close ruling (process-milestone); 008 cites the plan digest with that ruling |
| predicates 4, 5, 6 and 8 unmapped | qwen | completeness | yes | **fixed**: a predicate-to-evidence table in the candidate |
| RW-D0 closed prospectively | claude | completeness | yes | **fixed**: the sweep says record 008 closes it |

## What the repairs change, and what no reviewer read

The repairs touch the candidate, close-results, the sweep and the close
receipt. No panel round read the repaired bytes; one round was run, as for the
0.4.0 close. The one blocking concern was settled by the owner's answer, not by
a change to the evidence.
