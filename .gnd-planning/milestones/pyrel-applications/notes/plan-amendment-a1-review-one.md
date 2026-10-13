# Amendment A1 review one — independent completeness and agreement

Date: 2026-10-13. Instrument: owner-selected independent local reviewer.

Reviewed subject: `notes/plan-amendment-a1.md`.
Exact amendment SHA-256: `f1f79833476921fdbfd4a04e6360739b6f67d733f7cf2dcac4e9cf488245f698`.
Original plan SHA-256: `a001e5b87eaf55d4bc6763b918a5ec8f90a9a34d2c6655905cd420ea9f6ea735`.

Verdict: **pass within the assigned scope; no actionable findings**. The amendment
defines an implementable source-disagreement boundary, preserves independently
computed completeness, and makes the restricted agreement claim honest. This
opinion is not the amendment's owner gate or a native implementation acceptance.

## Findings and evidence

No findings requiring amendment changes.

The original plan requires computed eligibility rather than supplied claims
(`notes/pyrel-applications-plan.md:195`) but also requires per-rule normalized
agreement (`:208`). A1 identifies their conflict on two concrete inputs
(`notes/plan-amendment-a1.md:10`) and replaces the agreement predicates explicitly
(`:21`), without replacing independent checking.

The supplied complete model derives eligibility by preference/genre join and
blocked/rated negation (`src/gnd/examples/bookrec/complete.orm.yaml:199`, `:216`).
Its `all_eligible` antecedent reads eligibility (`:345`). GND's legacy constraint
view selects supplied covered derived rows (`src/gnd/extensions.py:2365`), while
its derivation obligation separately compares computed and supplied identities
(`:2239`, `:2259`). Thus the source disagreement concerns the guarded input view,
not permission to accept forged claims.

I independently reproduced both A1 observations with `.venv/bin/python` and
`gnd.api.check(model, temporary_population, unredacted=True)`, using the shipped
complete model and complete population:

| Mutation | GND `constraints[3]` | Eligible derivation | Overall exit |
|---|---|---|---|
| Append `{book: night, user: ada}` to eligible claims | fail, offending Ada/night | fail, `derived-extension-unsound`, Ada/night | 1 |
| Remove Ada/river from both recommendation and eligible claims | pass | fail, `derived-extension-incomplete`, Ada/river | 1 |

Model SHA-256: `cc2d42be35d284f20d00e56bc761ff9121ee2e3c9f7c02091a6a3d2c277b232b`.
Base population SHA-256: `489c3ceaaa194f034fb997cdb0709e8040669b90dc9138ce6cfa642bc3ac0d46`.
The mutations preserve all other facts and coverage. Their observable consequence
is exactly A1's stated mismatch: computed completeness excludes the forged pair
and still requires the jointly omitted pair, while both acceptance gates reject
the erroneous derivation claims (`notes/plan-amendment-a1.md:37`).

A1 preserves all shipped rule/derivation controls (`:24`) and independently frozen
native answer keys (`:26`). Its denominator cannot exclude unlisted mismatches
(`:34`); new measured disagreements require an explicit amendment (`:42`). This
supports a direct implementation: identify comparison rows by frozen case and
obligation identity, compare every comparable row, retain both results for the
two listed rows, and require every native result to match its separate answer
key. The full emitted row inventory remains visible, so a smaller denominator
cannot conceal omitted native policy checks. GND reports remain unchanged
(`:45`) and the rest of the original gates remain mandatory (`:53`).

## Limits

Read the complete amendment and original plan; inspected the supplied complete
model, GND derived-claim/constraint-view code, and reproduced the two GND cases.
No other reviewer output was read. No PyRel execution, paid call, plan edit or
implementation edit occurred. Native outcomes above are the logically expected
computed-view outcomes, not measured native implementation results. PA0 must
freeze exact case/model/population bindings and native expectations, and PA1/PA2
must execute their discriminating controls before claiming implementation success.
