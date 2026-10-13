# CS1 — Implement compiled snapshot checking

Delegated approval (auto=true), 2026-10-13, before implementation.

## Provenance and obligations

Owner delegation is recorded in CS0. Read the full plan and CS0, its red corpus,
four local reviews and RF9 carryovers. This spec discharges CS1-C1 (same public
single/batch failure), C2 (coverage/identity/multiple projections), C3 (grading,
counts, schema, redaction), C4 (defaults/compiler/digests/layers), C5 (work ceiling).
Plan CS-R1–R6, sections 5–7/9/10 and CS0's named standing rules apply unchanged.
No new certificate or broad replay is selected.

## Design and delegated rulings

Add gnd.compiled_obligations in the checking layer. Share an indexed role-pair
matching function with the walk's existing compiled evaluator. Walks keep raw
pre-state facts and existing uncovered/clean policies. Snapshot mode examines
effective facts from the current extension policies. Every compiler-eligible
entry is an instantaneous snapshot implication, including entries involving
dynamic derived heads; dynamic-rule and temporal step claims themselves remain
excluded. Such entries are excluded from any walk-agreement denominator unless
the walk actually checks them. No compiler guard changes.

Use typed identity from gnd.values, all role pairs and a common required-row
projection index. A global snapshot ceiling of 100,000 role-cell visits applies
across all entries; count key construction and antecedent probes. Exhaustion
yields unchecked reason compiled-obligation-work-limit, never partial success.
Missing coverage yields compiled-obligation-uncovered. Participating derived
relations with an unchecked derivation verdict, opaque values, or unavailable
extensions yield conservative unchecked reason compiled-obligation-unavailable.
This may refuse cases whose known rows suffice; it never infers absence from
possible-only rows. Covered empty antecedents are vacuous.

Register snapshot compiled-subset outcomes clean, vacuous, violated alethic and
deontic, and the three unchecked reasons. Preserve exact compiler locators,
source/status and original operation/precondition identity in messages.
Compose rows before band/count selection; invalidate the old snapshot projection
and Phase1 trace whenever compiled rows are added. Opt-in public results confer
no proof-backed assurance and mint no historical execution capability.

Thread compiled_operations through api.check, service, checker.check, anchored
checker and batch directory checking, with defaults false. The service's actual
evaluator/anchor route receives composition regardless of wrapper selection.
Occurrence admission is explicitly unsupported with this new mode in this slice:
API rejects with ValueError and CLI with usage exit 64. The strict occurrence
zip cannot safely represent appended obligations; this refusal is the approved
response to review 4, not silent loss. Normal admission remains unchanged.
CLI transition combinations are also usage 64 with a discriminating reason.
RedactionPolicy maps each compiled locator to the asserted relation's redacted
roles (including derivation lineage); retain original schemas and suppress its
whole witness/message through the existing projection policy.

## Tests and verification selection

Run the issue corpus and new direct controls; expected exit 0 after the red
activation corpus becomes green. Cover coverage on both sides, pass/fail/warning/
vacuity/unchecked, budget exhaustion, typed identity, repeated pairs, multiple
effects, all-operation traversal, opaque/unavailable derived sources, anchored
routing, bound references, redaction, schema validation and admission refusal.
Run focused default/digest/compiler controls, batch controls, layer-map tests,
redaction consumers and registry construction controls. No full default replay,
provider lane, distribution acceptance or certification. Exact commands/results
and artifact hashes belong in the phase record.

## Review and refactoring

Obtain an independent local diff review; reproduce findings and demonstrate
regressions on pre-fix bytes. Recheck neighbors after fixes. Shared indexed
matching replaces the walk's duplicated nested matching without policy changes.
No unrelated refactor, default-on change, compiler widening or full-walk claim.

## Size and implementability

Estimate 150–250 new evaluator lines, 100–200 integration lines and 150–250 test
lines. Existing registry/report fields carry the label and reasons; composition
invalidates incompatible evidence. The admitted two-case corpus is red for the
missing keyword; unknown inputs and occurrence admission have explicit refusals.
This spec's decisions are agent rulings under the owner's named delegation.
