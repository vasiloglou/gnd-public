# Codex review of the rule-check-followups close

Reviewer: Codex (gpt-6-sol, xhigh, read-only, prompt on stdin), selected by
the owner ("One reviewer (Codex)", 2026-11-08). Subject: the uncommitted
close draft (007-milestone-close.md, plan §3 and §11, close evidence, one
regenerated component page) on branch claude/rule-check-followups-close
over main 859b852d. One reviewer is one reviewer.

## Triage

| ID | Accurate? | Class | Disposition |
|---|---|---|---|
| K1 | yes, reproduced: `model_construct(...).model_copy()` keeps `fixture x` | blocking | **fixed in the record**: predicate 2 qualified; proposed plan §11 row |
| K2 | yes | blocking | **fixed in the record**: predicate 6 qualified; proposed plan §11 row; issue 112 not reopened |
| K3 | yes | blocking | **fixed**: plan §11 and the record call the amendments proposed, taking effect with the owner's close ruling (the merge) |
| K4 | yes | completeness | **fixed**: each phase boundary has its own sweep row |
| K5 | yes | completeness | **fixed**: README status, next action and close link |
| K6 | yes (the reviewer had no GitHub access) | hardening | **fixed**: issue states retained in evidence/close/issue-states.txt |

## Review output (verbatim)

    DISPOSITION: revise
    
    ID: K1  
    SEVERITY: blocking  
    LOCATION: .gnd-planning/milestones/rule-check-followups/007-milestone-close.md:73  
    QUOTE: “yes, for `model_copy`; `model_construct` is unvalidated (FU2 boundary)”  
    PROBLEM: Predicate 2 says no copy can carry an invalid producer/source pair. A `Population.model_construct(model="m", source="fixture", producer="x", facts={}).model_copy()` does exactly that: `model_copy` skips the validator when `update` is empty. I reproduced it in the local virtualenv. The phase’s decision to leave `model_construct` unvalidated does not make the absolute predicate true.  
    FIX: Qualify the predicate to copies of validated populations through a ruled plan amendment, or record it as unmet. Keep the `model_construct` exception explicit; this finding does not require extending FU2’s code scope.
    
    ID: K2  
    SEVERITY: blocking  
    LOCATION: .gnd-planning/milestones/rule-check-followups/007-milestone-close.md:77  
    QUOTE: “yes, in its own terms”  
    PROBLEM: Plan predicate 6 says issues 111 **and 112 stay open** on main after merge. This row says 112 was closed by another milestone. The milestone did not close it, but the stated predicate does not hold.  
    FIX: Record the open-state clause as superseded by the external closure and amend the plan with provenance and an owner ruling. Do not reopen issue 112.
    
    ID: K3  
    SEVERITY: blocking  
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:214  
    QUOTE: “Applied at the milestone close (2026-11-08) under the close ruling; the”  
    PROBLEM: The draft records rulings on the review instrument, FU1-O1, and the RF5 failure, but no owner ruling approving the amended plan or the close. With `auto=false`, “under the close ruling” asserts authority that the record does not yet show.  
    FIX: Mark the amendment as proposed pending the owner’s close ruling; after that ruling, record its scope and the amended plan digest.
    
    ID: K4  
    SEVERITY: completeness  
    LOCATION: .gnd-planning/milestones/rule-check-followups/007-milestone-close.md:150  
    QUOTE: “Phase boundaries (FU2 `model_construct`; FU3 combined variants; FU4 unmeasured loads, quadratic-only guard; FU5 third-module re-export)”  
    PROBLEM: This sweep omits recorded boundaries: FU2 does not revalidate other field types on copy; FU3 has no cases for derivations over derivations, clause or fixpoint rules, or `semiderived` rings; FU4 has no case for an erroring process listing; and FU5 can break users of the three private imports. The phase records state these limits, but the close does not dispose them individually.  
    FIX: Name these boundaries in the sweep and record their residual disposition. No additional implementation is implied.
    
    ID: K5  
    SEVERITY: completeness  
    LOCATION: .gnd-planning/milestones/rule-check-followups/README.md:8  
    QUOTE: “FU5 complete, PR open”  
    PROBLEM: PR 134 is merged at `0e093158`. The README also says the next action is to merge FU5 and has no close-record link, so milestone navigation contradicts the draft close.  
    FIX: Update the status and next action, and link `007-milestone-close.md`.
    
    ID: K6  
    SEVERITY: hardening  
    LOCATION: .gnd-planning/milestones/rule-check-followups/007-milestone-close.md:147  
    QUOTE: “resolved: all six closed on GitHub, each pointing to its phase”  
    PROBLEM: The local history verifies the listed PR merges, but the cited evidence does not establish GitHub issue states or the claimed phase pointers. GitHub was unreachable from this review environment, so this part of predicate 7 remains unverified.  
    FIX: Retain dated issue-state and phase-pointer evidence, or narrow the claim to what the local records establish.
