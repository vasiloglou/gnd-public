# Phase FU2: Codex review of the diff

- Instrument: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only`, prompt on stdin.
- Subject: `git diff 12daa5b7 10265ddf`. One reviewer is one reviewer.
- Exit 0. Disposition: **revise**, one hardening and one completeness finding.

## Dispositions

| ID | Reproduced | Disposition |
|---|---|---|
| R1 | yes: `model_copy(update={'producer': ['x']})` on a `tool-output` population returned a list producer | **fixed**: the validator requires a non-`None` producer to be a string before its length is checked; successor case T1 (e), red before the fix (1 failed, 12 passed), green after |
| R2 | yes: the README still said approval and implementation were pending | **fixed**: README status, links and next action |

## Review output (verbatim)

    DISPOSITION: revise
    
    ID: R1
    SEVERITY: hardening
    LOCATION: src/gnd/population.py:176
    QUOTE: copy._producer_names_tool_output()
    PROBLEM: The reused validator checks the producer’s length but not its type (src/gnd/population.py:164). A read-only probe showed that model_copy(update={"producer": ["x"]}) returns a Population whose producer is a list, although the schema requires a string (src/gnd/schema/population.schema.json:19). Construction rejects the same value. T1 has no non-string producer case.
    FIX: Check that a non-None producer is a string before checking its length, and add a copy test using a one-element list.
    
    ID: R2
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/README.md:20
    QUOTE: Next action: owner approval of the FU2 red tests, then implementation.
    PROBLEM: The README still presents approval and implementation as pending, while the FU2 spec records both as complete (.gnd-planning/milestones/rule-check-followups/notes/phase-FU2-spec.md:5).
    FIX: Update the README status, link text, and next action.
    
    The BaseModel.model_copy parameters match; the source Population callers update facts only. Read-only probes confirmed that a plain copy keeps its validation marker and a deep copy fails the marker check. I found no other bound-population label loss or recorded digest movement in the traced paths. Every declared T1–T8 case has an assertion that can fail. I did not run pytest; uv could not initialize its cache in this read-only environment.
