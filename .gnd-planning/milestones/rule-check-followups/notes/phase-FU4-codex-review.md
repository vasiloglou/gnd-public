# Phase FU4: Codex review of the diff

- Instrument: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only`, prompt on stdin.
- Subject: `git diff df5753bf f598ba61`. One reviewer is one reviewer.
- Exit 0. Disposition: **revise**, two blocking, one hardening and four completeness findings.

## Dispositions

| ID | Reproduced | Disposition |
|---|---|---|
| R1 | yes: marker `grandchild[alive]+(1)`, the `pgrep -f` check and a leader-only kill: the test passed while the grandchild ran | **fixed** (spec I2): a literal substring over `ps -axww`; the regex-hostile marker name is the regression case, red against the `pgrep` check under the mutant, green unmutated, red under the mutant after the fix |
| R2 | by reading: `check=False` and stdout only | **fixed** (spec I2): `ps` runs with `check=True`; structural, no separate case |
| R3 | by arithmetic: n log n about 4.7, n^1.5 about 8 pass bound 10 | **recorded** (spec I3): the test comment and the record boundary call it a quadratic-regression guard |
| R4 | no: `beast-3:~/rc2-shards/final/shard3.out:43` holds the failure | **not reproduced** (spec I4); the raw excerpts are now retained |
| R5 | yes: the probe recorded no grandchild PID | **recorded** (spec I5): F1's claim is qualified; T5 is the independent check |
| R6 | yes: the unloaded figures were not retained | **fixed** (spec I6): re-run and retained with scripts; the new figures are quieter and recorded beside the old |
| R7 | yes | **fixed**: milestone README |

## Review output (verbatim)

    DISPOSITION: revise
    
    ID: R1
    SEVERITY: blocking
    LOCATION: tests/test_public_session_driver.py:390
    QUOTE: ["pgrep", "-f", str(marker)]
    PROBLEM: `pgrep -f` treats the path as an extended regular expression. A temp root containing `[1]`, for example, will not match those literal characters in a surviving grandchild’s argv; regex metacharacters can also widen the match to unrelated processes. The empty result can make a leader-only kill pass.
    FIX: Escape the marker path as a literal `pgrep` pattern and cover a temp path containing regex metacharacters.
    
    ID: R2
    SEVERITY: blocking
    LOCATION: tests/test_public_session_driver.py:390
    QUOTE: check=False, capture_output=True, text=True
    PROBLEM: The test inspects stdout but ignores `pgrep`’s exit status. An invalid pattern or process-list error can return no stdout, so the survivor assertion passes without checking any process.
    FIX: Assert that `pgrep` returned its “no matches” status; report stderr for any other status.
    
    ID: R3
    SEVERITY: hardening
    LOCATION: tests/test_v51_phase2_extraction_scope.py:80
    QUOTE: assert large < 10 * small, {'small': small, 'large': large}
    PROBLEM: This still rejects the cited quadratic mutant (about 18×), but it does not establish the test name’s linear-scaling claim. At these sizes, an n log n walk is about 4.65× and an n^1.5 walk is 8×; both pass the approved bound. The old bound also admitted n log n.
    FIX: Keep D2’s bound and describe this as a quadratic-regression guard, or add a separate structural check if linearity is required.
    
    ID: R4
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU4-spec.md:40
    QUOTE: Every recorded failure of the driver test on beast-3
    PROBLEM: The listed `rc2-shards/final` run has no driver failure in the retained RC2 final summary. The retained shard summaries identify failed tests but do not contain the asserted line-390 message, so they cannot verify the claim that every listed failure had that assertion.
    FIX: Remove the RC2 final run from the failure list and retain the raw failure output, or limit the assertion claim to runs with available detail.
    
    ID: R5
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU4-spec.md:55
    QUOTE: In all 60 rounds the driver's own leader and grandchild were gone when checked,
    PROBLEM: The retained probe records the leader PID but no grandchild PID. Its `mine` and `own_group` fields inspect only processes already returned by the broad `pgrep` (probe lines 53–58). They cannot independently establish that an omitted grandchild was gone.
    FIX: Qualify the claim as “none appeared among the `pgrep` matches,” or retain an independent grandchild-PID check.
    
    ID: R6
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU4-spec.md:63
    QUOTE: 200 rounds, median of 7 runs, median ratio
    PROBLEM: `evidence/FU4/` retains the 60-round load probe only. It does not retain the cited 200-round laptop results, fastest-of-seven results, quadratic-mutant measurements, or the claimed accompanying six-shard result. Those figures cannot be checked from the retained files.
    FIX: Retain the measurements and invocation details, or label these figures as unretained author observations.
    
    ID: R7
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/README.md:8
    QUOTE: FU4 spec drafted, awaiting the owner gate.
    PROBLEM: The added spec says D1–D3 were approved; the README still calls it a draft and says the next action is the owner ruling.
    FIX: Update the FU4 status and next action.
    
    The retained 60-round JSON does support its reported count, checksum, timing range, and one unrelated-process match. For ordinary temp paths, both spawned Python command lines contain the marker, so a leader-only kill should leave a detectable grandchild when `pgrep` works. `ps` is used only by the probe and cannot truncate the test’s assertion. The 5-second ceiling still catches walks whose fastest of seven runs exceeds it. I ran no builds or test suites.
