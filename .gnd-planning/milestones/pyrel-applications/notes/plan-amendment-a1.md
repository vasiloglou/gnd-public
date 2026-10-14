# PyRel applications — proposed agreement amendment A1

2026-10-13. Effective only after four local reviews and a delegated auto=true gate.
Original plan r1 remains unchanged with its four opinions; this amendment changes
only the finite agreement contract and its cited completion predicates.

## Refuted premise and reproduced observations

Claude PA0 finding 1 is reproduced through public gnd.api.check:
`m2-book_is_eligible-extra` supplies Ada/night as eligible. GND reports
`all_eligible` fail on that supplied pair even though computed eligibility excludes
it. A new joint-omission sibling removes Ada/river from both recommendation and
eligible claims: GND reports derivation failure but `all_eligible` pass. The desired
PyRel implementation must instead exclude Ada/night and still require Ada/river.
The old unconditional per-rule agreement predicate cannot coexist with independently
computed completeness. Both engines must reject the forged/omitted claim populations
at the business acceptance boundary; their all_eligible verdicts intentionally differ.

## Amended predicates

Replace the original completion predicate 4, PA2-C4 and PA6-C2's unqualified
per-obligation 100% agreement with this bounded contract:

- All shipped rules and derivations remain mandatory and have discriminating native
  controls. No rule is omitted, weakened, marked optional or trusted from claims.
- Every corpus case records hand-narrated native expected dispositions and the
  original independently measured GND dispositions separately. Every native row,
  modality, guarded witness, derived discrepancy, exact byte binding and overall
  acceptance/exit must match its native answer key. Never regenerate native answers
  from the implementation or turn an audit completion exit into acceptance.
- GND/native agreement reports an explicit denominator of comparable obligation
  rows, compared rows and matches. Separately enumerate every intentional semantic
  disagreement, with both results, the exact input, reason and owner disposition.
  The comparable-row denominator must not include the listed disagreements, and
  must not exclude an unlisted mismatch. Claimed 100% agreement is only for that
  named comparable denominator, never all ORM semantics or all emitted rows.
- Initially listed disagreements are `constraints[3]` on the forged eligible-extra
  case (GND fail, native satisfied) and the joint-omission case (GND pass, native
  violated). Supplied claims still independently fail derivation checking in both.
  These are computed-versus-claimed source disagreements, not accepted-input
  exceptions. Business refusal agrees for both cases.
- Further runtime-measured disagreement needs an explicit delegated amendment
  before it can be excluded. Unknown/vacuous/warning distinctions remain visible;
  any normalization mapping is explicit and tested, not inferred from exit codes.
- Public GND behavior and its old reports/goldens are unchanged. This milestone
  does not silently fix GND, certify its evaluator, or claim universal equivalence.

## Scope, decisions and review budget

PA0 freezes separate GND observations/native expectations and the two named
source-disagreement controls; PA1/PA2 implement the independent native contract;
PA6 reports its exact comparable denominator and all separate disagreements.
PA-D5 is amended only as above. All other design rules, phases, hard dependencies,
product/evolution paths, six graphics, executed docs, installed-wheel gates and
review bars remain mandatory. Native coverage cannot shrink to achieve agreement.

Owner whole-milestone auto=true authorizes amendment rulings; four local plan
readers are already selected. Review one initial amendment round, then at most
one repair round for a reproduced blocker; before round two record convergence
and self-inflicted/total, blocking/total and same-seat counts. No paid panel.
No production edit or PA0 completion precedes the amendment's reviewed gate.
