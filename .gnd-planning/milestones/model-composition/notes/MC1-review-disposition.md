# MC1 review disposition

2026-11-09. One reviewer is one reviewer. The independent Codex CLI review
returned revise with nine reproduced findings. The first complete regression
attempt used an invalid raw Lean toolchain/format for R6 and is labelled as
such. After correction, all 17 regression cases failed against pre-fix source
(`evidence/MC1/red-review-regressions.txt`). All 17 pass after the repairs;
three added include-free/raw-type controls also pass (20 total).

| Finding | Relevance | Reproduction and disposition |
|---|---|---|
| R1 batch band 70 | blocking | Public CLI report rejects None digest. Emit authentic captured-byte digest only as refusal metadata, then skip policy reload. No half-model evaluation occurs. |
| R2 composition exception escape | blocking | API and text/JSON CLI each leak ModelValidationError. Guard before initial model load and retain a defensive band-3 adapter at composition re-verification. |
| R3 legacy export reason | blocking | Both path exporters change include-free input-invalid to a schema rule. One shared include-reason helper selects only new include refusals; all other errors retain input-invalid. |
| R4 direct compose depth | blocking | A 500-level source passes structural validation and crashes deepcopy. One clone seam maps RecursionError to the existing declaration refusal, covering document and metadata copies. |
| R5 include id model | blocking | Valid id model collides with the internal own-origin sentinel. Included origins now store includes[ID]; model remains the own sentinel. No valid include ID is reserved or refused. |
| R6 raw export reason | blocking within MC1 | The review rated completeness, but direct raw public APIs demonstrably return the wrong reason under MC1-C10. Add explicit raw admission guards and preserve only include-specific errors in each adapter. Add separate inventory rows and legacy controls. |
| R7 competing checks | blocking within MC1 | The review rated completeness; stale-digest and temporal compound faults violate explicit order. Move guards before route identity and feature checks after bounded intake. Counting/failing seams prove later work did not run. |
| R8 own selectors | blocking within MC1 | The review rated completeness; an own warning changes its promised path. Preserve own authored selectors while attached constraints still remap to fact_type_constraints. |
| R9 digest newline | hardening of MC1's own deliverable | Schema accepts a value the parser refuses. Add exact min/max digest length and parity control. This belongs to the serialized envelope shipped by this phase, so repair now. |

These dispositions use observable behavior and the named phase contracts,
not finding counts as a quality metric. No additional plan review is selected.
One focused Codex confirmation over the repairs is the declared remaining
review budget; do not start an unbounded prose loop.

## Refactoring found during implementation

The first D7 wrap implementation also repeated empty-field omission inside
model_dump. Remove that duplicate policy: the single wrapping serializer
covers both dump entry points. This is behavior-preserving cleanup, verified
by the census and serializer controls; it is not labelled a reproduced
behavioral defect. The dependency-home moves remain the phase's other
executed refactors.

## Explicit boundary

The frozen default baseline finished with 6 failures, 18,392 passes,
799 deselected and 1 warning (exit 1), with a clean source tree at 459ca8d2.
The six failures are the grow-a-model prose length and five historical RF5
pins; their full output is retained. These are known reds, not phase fixes.
Candidate default comparison remains owed. The lint baseline has 13 failures
and candidate lint must introduce none. No acceptance or merge is claimed.
