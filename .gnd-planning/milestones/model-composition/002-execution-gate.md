---
milestone: model-composition
station: "execution and MC1 spec gate"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: execution-gate
date: 2026-11-09
gate:
  command: "ruling: delegated (auto=true) approved notes/phase-MC1-spec.md sha256 5179c82f8e6b953d49257b4b5dd50383955de5061bd89cf0455b4f33703d0a5f"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md
    sha256: 5179c82f8e6b953d49257b4b5dd50383955de5061bd89cf0455b4f33703d0a5f
---

# Claim

Delegated approval (auto=true) admits MC1 spec r4 and D1-D8 as proposed,
with section 12's acyclic-home and census-membership amendments.

## Gate output (verbatim)

Delegated ruling, 2026-11-09: Approve MC1 spec r4, D1-D8 as proposed,
prose instrument with rationale in section 12, optional further spec review
omitted under the retained convergence stop. Budget remains 750 source and
1,425 test lines. Compatibility, independent diff review and size stop remain
binding. Authorization: current owner invocation,
`process-milestone model-composition auto`.

Owner selections, 2026-11-09 (verbatim):

    Use one Codex CLI reviewer for close (override panel requirement)
    Authorize these named baseline and candidate runs

The second selection answers the question naming the model-composition
compatibility census and full default suite on beast-3 at 459ca8d2 and again
on candidate. The first overrides the panel requirement only for this named
milestone's independent close review. No paid panel or reviewer subagent is
selected. Phase diffs retain the plan section 8 Codex CLI selection.

## Implementability sweep

Read the effective plan, retained reviews, draft spec, loader, validator,
documents, errors, schema, bounded reader and graph control. Section 12
records dependency repairs, test selection and corpus-instrument rationale.
The parser and exception moves avoid introducing an initializer cycle.
The census membership amendment preserves all original baseline observations
while allowing the new fixtures the same spec requires.

## Boundary

This is a delegated ruling, not the owner's personal reading of spec r4.
No production implementation or completed phase is established. Baseline
capture precedes production edits. One reviewer is one reviewer. Merge,
publication and certification remain outside delegation.

## Open questions

- Close: dispose the census membership refuted premise through a plan repair.
- MC4-draft still requires the owner's reaction; auto does not invent it.
- MD17 remains open until the MC4 scope is concretely specified.
