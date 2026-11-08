# Phase FU3: Codex review of the diff

- Instrument: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only`, prompt on stdin.
- Subject: `git diff 1e63aeb5 9662812e`. One reviewer is one reviewer.
- Exit 0. Disposition: **revise**, one hardening and four completeness findings.

## Dispositions

| ID | Reproduced | Disposition |
|---|---|---|
| R1 | yes, by reading `correspondence.py:1298-1312`: `acyclic-intransitive` appends intransitivity witnesses after the in-group edges | **recorded**: spec I1 scopes C1 to `acyclic`; the combined variant over a derived fact type is a record boundary |
| R2 | yes: with a successor case `self-loop`, the old oracle's T2 was red (1 failed, 19 passed) | **fixed**: T2's oracle is plain reachability, independent of `gnd.graphs`; successor case `self-loop`; 20 passed, the C3 mutant still 2 red |
| R3 | yes: `add-disjoint` derives eight edges | **fixed**: the corpus README names the cases that derive more or none |
| R4 | yes | **fixed**: milestone README status, links and next action |
| R5 | yes: no FU3-O1 row existed | **fixed**: the row is in the record |

## Review output (verbatim)

    DISPOSITION: revise
    
    ID: R1
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU3-spec.md:155
    QUOTE: “The checker and `acyclic_extents` both build their view through it, so they read the same pairs.”
    PROBLEM: The pair sets agree, but that does not make every extent row an in-group edge. For `acyclic-intransitive`, `src/gnd/correspondence.py:1298-1312` appends intransitivity witnesses. Reproducible in-memory probe: load the FU3 model with `variant: acyclic-intransitive`; load `agree.pop.yaml` with an additional asserted `leads` fact `{from: 1, to: 3}`; call `check(model, population)` and `acyclic_extents(model, population, [verdict.constraint_ref])`. The checker fails. The extent returns four in-group edges plus triples `[1,2,3]` and `[2,1,3]`. This is outside FU3-C1’s stated `acyclic` scope, but answers the broader variant question.
    FIX: State this combined-variant boundary alongside C1; keep the FU3 claim scoped to `acyclic`.
    
    ID: R2
    SEVERITY: hardening
    LOCATION: tests/test_fu3_derived_ring.py:73
    QUOTE: “if len(component) > 1”
    PROBLEM: T2’s oracle omits singleton self-loops, which `src/gnd/semantic_spec.py:1458-1477` correctly includes. An in-memory `agree` population with matching hop and leads facts for `9 -> 9` produces an extent containing `[9,9]`, while T2’s expected list would omit it. T2 also imports the same `strongly_connected_components` function used by production (`src/gnd/semantic_spec.py:13,1470`), so its graph oracle is not independent of that dependency.
    FIX: Use an independent small reachability oracle that includes self-loops, and add an exact-term derived self-loop case.
    
    ID: R3
    SEVERITY: completeness
    LOCATION: tests/fixtures/fu3-derived-ring/README.md:28
    QUOTE: “In every case the hops derive the same six edges”
    PROBLEM: `add-disjoint.pop.yaml:10-11` adds hops deriving `20 -> 21` and `21 -> 20`; its expected report also shows the derivation passing. No test asserts the README’s six-edge claim, and it is false for this declared case.
    FIX: Say which cases derive six edges and that `add-disjoint` derives two more.
    
    ID: R4
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/README.md:8
    QUOTE: “FU3 decisions ruled; corpus awaiting approval.”
    PROBLEM: The FU3 spec at line 3 records corpus approval and test-only implementation. The milestone index’s status, spec label at line 19, and next action at line 23 are stale.
    FIX: Update the index to the approved, implemented state and name the remaining review or record step.
    
    ID: R5
    SEVERITY: completeness
    LOCATION: .gnd-planning/milestones/rule-check-followups/notes/phase-FU3-spec.md:71
    QUOTE: “Open-questions row FU3-O1 records it for the close.”
    PROBLEM: No FU3-O1 row exists in the milestone’s Markdown records. The stated close carryover is therefore not recorded.
    FIX: Add the promised row or remove the claim until it exists.
    
    Summary: For the scoped `acyclic` route, the checker and extent use the same derivation view; read-only probes covered derived, uncovered, semiderived, deontic, and unavailable-term cases. The five expected reports match their case outcomes apart from the README error above. T1 and T6 pin bytes; T3–T5 have falsifiable assertions. The local FU2 merge commit is consistent with its recorded ruling. I did not run the focused tests: `uv` could not initialize its cache in the read-only environment.
