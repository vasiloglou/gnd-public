# Amendment A1 review three

Date: 2026-10-13. Seat: finite test denominators, independent native expectations,
business rejection, and forged/joint-omission completeness disagreements.

Subject: `notes/plan-amendment-a1.md` in the `pyrel-applications` milestone.

Reviewed SHA-256: `f1f79833476921fdbfd4a04e6360739b6f67d733f7cf2dcac4e9cf488245f698`.

Original plan SHA-256: `a001e5b87eaf55d4bc6763b918a5ec8f90a9a34d2c6655905cd420ea9f6ea735`.

BookRec complete model SHA-256: `cc2d42be35d284f20d00e56bc761ff9121ee2e3c9f7c02091a6a3d2c277b232b`.

BookRec complete population SHA-256: `489c3ceaaa194f034fb997cdb0709e8040669b90dc9138ce6cfa642bc3ac0d46`.

## Verdict and findings

**No actionable findings; A1 is suitable for its delegated amendment gate in
this seat's scope.** A1 corrects a reproduced conflict between unconditional
per-rule agreement and checking completeness against independently computed
eligibility. It preserves the required native checking and business refusal.
This opinion does not enact the gate or establish native success.

## Independent reproduction

Called public `gnd.api.check(..., unredacted=True)` using `.venv/bin/python`
against the complete model and three temporary JSON populations. The two
mutations were made independently from a fresh deep copy of the shipped complete
fixture; the model and shipped fixture were unchanged.

| Population | GND `constraints[3]` | GND eligibility derivation | GND business result |
|---|---|---|---|
| Shipped complete fixture | pass; five antecedent bindings | pass | exit 0, acceptance true; eight passes |
| Append `{book: night, user: ada}` only to eligible claims | fail; witness `{$b: night, $u: ada}` | fail; `derived-extension-unsound`, witness `{book: night, user: ada}` | exit 1, acceptance false; two failures, six passes |
| Remove `{book: river, user: ada}` from both eligible claims and recommendations | pass; four antecedent bindings | fail; `derived-extension-incomplete`, witness `{book: river, user: ada}` | exit 1, acceptance false; one failure, seven passes |

This reproduces A1 lines 10–17 and 37–41. The other derived head,
`book_is_blocked_for`, passes in all three cases.

The native expectations follow from source facts and model declarations, not
from either evaluator's output: `src/gnd/examples/bookrec/complete.orm.yaml:163`
blocks adult books for minors; `:199` joins preference with genre and `:216`
subtracts blocked and already-rated pairs. The resulting `(user, book)` set is
`{(ada,map), (ada,river), (ben,map), (ben,night), (ben,river)}`. Ada/night cannot
enter that set by a forged claim. Ada/river remains in that set when only
recommendation/eligible claims are omitted. The obligation at `:345` therefore
has native expected status satisfied in the extra-claim case and violated with
Ada/river as witness in the joint-omission case. Both cases must still be
rejected for the independently measured eligibility discrepancy.

## Denominator and non-circularity assessment

A1 lines 24–30 retain all rules/derivations and require separate hand-narrated
native answer keys, including witnesses, modality, derivation discrepancies,
bindings and acceptance. Lines 31–44 require exact comparable-row accounting,
enumerated disagreement inputs/reasons/dispositions, and forbid excluding any
unlisted mismatch. Lines 50–55 freeze the two controls in PA0 and prohibit
shrinking native coverage. These provisions preserve original plan PA2's
computed-source semantics (`notes/pyrel-applications-plan.md:195`) while repairing
its old per-obligation comparison requirement (`:208`).

For illustration only, these three complete-model cases require eight obligation
rows each: six constraints and two derivations. A complete 24-row native answer
key is still required. The named agreement exclusions account for exactly two
`constraints[3]` rows, leaving 22 comparable rows; they do not remove two cases,
their derivation failures, or their business rejection checks. This is not the
whole PA0 denominator and is not a measured native agreement result. PA0 must
record the actual full matrix and PA6 must report that exact denominator.

No further fix is suggested. Applying A1 should retain the separate coverage
and acceptance gates rather than presenting agreement exclusions as permission
to omit evaluation; A1 already explicitly requires that separation.

## Limits

Read A1, the original plan and the complete BookRec model/fixture; independently
ran only the three public GND checks above. No other reviewer opinions were
read. No native PyRel execution, external API, paid call, implementation edit,
plan edit or PA0-completion claim occurred. An initial `uv run` could not use
the restricted user cache, so reproduction used the existing local interpreter
directly. Only this review note was added. The proposed native dispositions are
source-grounded expectations pending native implementation and execution.
