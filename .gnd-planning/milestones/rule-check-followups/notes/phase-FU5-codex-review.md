# Phase FU5: Codex review of the diff (r1)

- Instrument: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only`, prompt on stdin.
- Subject: `git diff 6ed86d90 a20b017a` (spec r1 with the D1 (b) ruling, README). One reviewer is one reviewer.
- Exit 0. Disposition: **block**, one blocking, four hardening and two completeness findings.

## Dispositions

| ID | Reproduced | Disposition |
|---|---|---|
| R1 | yes: `git ls-tree v0.1.0 src/gnd/checker/` lists `_core.py`; `git log v0.1.0` lists `a3f35a6d docs(rf6a)` and `10608c47 docs(rf6b)` | **fixed** in spec r2 (P1); D1 returned to the owner, since the r1 ruling rested on the false premise |
| R2 | yes | **fixed** (P2) |
| R3 | yes | **fixed** (P3) |
| R4 | yes: `successor_dynamic_rows`, `tests/test_rf6_query_policy.py:129-160` | **fixed** (P4, §6 M2, §10) |
| R5 | yes: plan §5 says FU5 touches the shim inventory; `test_rf2_helpers.py` reads RF2 rows only | **accepted**: the three rows are annotated with whichever D1 ruling stands |
| R6 | yes | **pending D1**: record, gates and inventory note follow the ruling |
| R7 | yes | **pending D1** |

## Review output (verbatim)

    DISPOSITION: block
    
    ID: R1
    SEVERITY: blocking
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md:49
    QUOTE: “The RF-D5 trigger is not met. The only release is `v0.1.0` (2026-10-12, source `75eda93f`, the RF1 merge); RF6 landed after it”
    PROBLEM: RF6a and RF6b are ancestors of `75eda93f`, and the `v0.1.0` tagged tree contains the RF6b checker package. The public-launch close records that tag as the published source (.gnd-planning/milestones/public-launch/010-public-launch-close.md:20-26). The plan review had already recorded that the tag follows RF6 (.gnd-planning/milestones/rule-check-followups/evidence/plan-review-r2/codex-review.md:54). RF-D5’s release condition has therefore occurred. This also invalidates FU5-O1 at spec:148-149.
    FIX: Correct the chronology and remove the “trigger not met” finding. Preserve the owner’s D1 keep ruling, stating its next-release deferral separately from RF-D5.
    
    ID: R2
    SEVERITY: hardening
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md:56
    QUOTE: “`gnd.checker._find_cycle` existed in `v0.1.0` (then a module, `src/gnd/checker.py`)”
    PROBLEM: The importability claim is sound, but the tagged tree has `src/gnd/checker/__init__.py` and `src/gnd/checker/_core.py`; it has no `src/gnd/checker.py`. The tagged `__init__.py` re-exports `_find_cycle`.
    FIX: Describe the tagged checker package and its `_core.py` definition.
    
    ID: R3
    SEVERITY: hardening
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md:60
    QUOTE: “No production caller of any of the three.”
    PROBLEM: The helpers call each other: `_find_cycle` calls `_dfs_cycle` (src/gnd/checker/_core.py:1315), and `_ring_component_violations` calls `_find_cycle` (:1377). The source scan supports the narrower claim that no production path calls into this helper cluster.
    FIX: Say that no production caller outside the three-helper cluster reaches it.
    
    ID: R4
    SEVERITY: hardening
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md:79
    QUOTE: “None of these guards has a retirement mechanism today.”
    PROBLEM: The dynamic-query guard already applies counted removals through `dynamic-query-successor.json` (tests/test_rf6_query_policy.py:129-160). Its historical inventory includes `_dfs_cycle`’s `graph.get(node, ())` (.gnd-planning/milestones/code-refactoring/evidence/RF9-repair/dynamic-query-candidates.json:3047-3051). The other named guards still need retirement handling.
    FIX: Identify the existing dynamic-query successor and state which guards lack a suitable mechanism.
    
    ID: R5
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md:151
    QUOTE: “The shim inventory needs no edit”
    PROBLEM: The approved plan explicitly says “FU5 touches the shim inventory” (.gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:161-164). Its three RF6b rows still say only “RF-D5” (.gnd-planning/milestones/code-refactoring/notes/shim-inventory.md:755-757), so they do not record D1. The cited parser is no obstacle: tests/test_rf2_helpers.py:197-203 filters for RF2 rows.
    FIX: Annotate the three inventory rows with the FU5 keep ruling and the owner’s next-release deferral.
    
    ID: R6
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md:133
    QUOTE: “the phase edits only planning text (this spec, the record, the shim inventory note) and V2 runs to show nothing moved.”
    PROBLEM: This diff contains only the spec and README. It contains no FU5 record, inventory note, or focused-gate output. The approved plan requires a record with verbatim focused-gate output, an independent reviewer, and a refactoring review for each phase (.gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md:35-37,179-195). Those remain unrecorded in the reviewed diff.
    FIX: Add the FU5 record, required review evidence, inventory note, and actual focused-gate output before presenting the phase as complete.
    
    ID: R7
    SEVERITY: hardening
    LOCATION: .gnd-planning/milestones/rule-check-followups/README.md:8
    QUOTE: “FU5 spec drafted, blocked on D1.”
    PROBLEM: The new spec records D1 as approved (notes/phase-FU5-spec.md:5-8). The README also labels its link “draft r1” (:25) and says the next action is the owner’s D1 ruling (:29).
    FIX: Update the status, link label, and next action to reflect the recorded ruling and remaining phase work.
    
    The single local release tag, public-launch close, RF6 history, helper source, and named guard code support the keep disposition and the guard categories in P4. The 15-failure total is consistent with the listed test cases, but this read-only review did not rerun the probe or find retained output that independently establishes its exact result.
