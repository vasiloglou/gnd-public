# GA3 · Typed constants in AMIE mined rules

## 2. Provenance

[Plan r2](guarded-rule-authoring-plan.md), its
[review disposition](plan-review-disposition.md), [GA2](../005-phase-GA2.md),
[GR-D11](https://github.com/vasiloglou/gnd-public/issues/182), and the
[historical GW1 draft](../../guarded-rule-workflows/notes/phase-GW1-spec.md).
The [ILP bridge reference](../../../../docs/reference/ilp-bridge.md)
owns the AMIE wire, mapping and counting contract.

## 3. Obligations

| Criterion | Verification |
|---|---|
| C1 | Map typed constants in all four positions and import the issue's shared-predicate category rule. Keep the variable-only recursion refusal. |
| C2 | Check canonical spelling, type, reserved prefix, deduplicated exact support, full confidence and bounded all-or-nothing refusal. |
| C3 | Preserve existing export/import controls, preview the proposal, and smoke all three authoring routes from one locally installed wheel. |

## 4. Standing rules

Use one decoder for every operand position. Keep captured byte binding,
capped reads and refusal order. Never execute miner text. Charge a
command-wide recount budget before enumerating joins. Keep the old
variable-only and export observation pins. Use one normative mapping
table and an independent population fixture.

## 5. Goal

Import an AMIE-formatted rule containing typed literals as an induced
guarded constraint when the bound population confirms its reported support.

## 6. Design

Decode the role's existing family prefix before the first colon. Decode
text using the inverse export escapes, canonical signed decimal integers
within the interpreter's bounded decimal representation, and exact boolean
`true` or `false`. Validate the decoded primitive and require an exact
round-trip through the unchanged export spelling. Bad constants remain
`constant-atom`. A decoded dollar-prefixed string is `constant-spelling`.
The existing printable ASCII token grammar remains the import boundary.

Only parsed `?a` through `?z` are variables. Literals do not bind or connect
variable sites. A single fully ground body atom is connected. Keep the
mapping refusal order. Allow an asserted body relation also to occur as the
head predicate when the head has a typed literal, provided the exact head
atom does not occur in the body. Retain variable-only recursion refusal.
Recognize constant-first rule rows in AMIE stdout extraction.

Filter a body constant against the identical exported token. Fill head
constants directly and deduplicate projected head pairs. Keep the
1,000,000-row per-rule product guard. Before any count, charge a
10,000,000-unit aggregate budget across all rules for join prefix work,
projected head pairs, head membership and head provenance scans.
Use `too-large` for both caps. Keep all-mappings-before-count and the
existing support/refusal sequence. Require positive recomputed support,
reported support equality and full recomputed confidence. The existing
checker confirmation remains mandatory before publication.

## 7. Decisions

| Decision | Contract |
|---|---|
| A | Existing triple bytes and role-family spelling define the literal transport. |
| B | Same-predicate admission is restricted to the typed literal-head case with no exact head atom in the body. |
| C | Aggregate and per-rule limits are charged before joins. Failure leaves the proposal absent. |

## 8. Gates

The committed [capture-format rule rows](../corpus/GA3/rules.tsv) are
fixture data and do not claim an AMIE run. Export facts for that model
and population, bind the three SHA-256s in a run record, import and
preview. The architecture rule reaches two body bindings but one head
pair. The ground rules pin all four slots, numeric and Boolean types.
Exercise malformed, dollar, same-head and variable-only refusals,
wrong support, false head pairs and both work limits.

Run `pytest -q tests/test_ilp_amie_constants.py tests/test_ilp_amie.py tests/test_ih1_counting.py tests/test_ih2_ownref.py tests/test_ilp_learners.py`
and affected compatibility and component gates. Install a locally built
wheel in an isolated environment and verify GA1, GA2 and GA3 public routes.
Use an isolated GA1 repeated-variable control for target attribution.

## 9. Out of scope

Live AMIE execution, general recursion, new rule syntax or export changes.

## 10. Size

One mapping/counting change, a narrow service budget, public-route fixtures
and an installed smoke.

## 11. Approval instrument

Delegated under the [plan gate](../001-plan-gate.md), 2026-11-11.
GA2 evidence precedes this gate. Phase diff review and the standard
milestone close panel remain separate gates.
