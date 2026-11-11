# Guarded rule authoring · plan r1

**Draft, 2026-11-11.** The owner activated GR-D8, GR-D10 and GR-D11. No
review instrument has been selected for this successor, so plan review
has yet to run. The earlier milestone's delegated gates apply to its
named scope. This milestone defaults to `auto=false`.

## Goal and completion predicates

Ship three authoring paths for guarded rules. Generate a targeted failure
and a non-vacuous pass for each supported guard, identify unserved rules
by ID, and retain case generation for supported constraints in a mixed
model. Propose two joined discovery shapes with attributable support and
counterexamples. Import typed constants in all four AMIE atom positions,
including the named-category example, with independent support verification.

Close once all three phases have checked public command results, review
records and documented boundaries. GA3 owns an installed smoke covering
the three workflows.

## 0. Binding design rules

Follow the six rules in the [project hook](../../../../.codex/skills/process-phase/references/project.md).
Use one typed identity per boundary, bound input reads and expansion,
preserve refusal precedence, and maintain independent expected-state and
support oracles. Keep ModelIndex, family dispatch and layer guards live.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| [GR-D8](https://github.com/vasiloglou/gnd-public/issues/179) and the [author’s correction](https://github.com/vasiloglou/gnd-public/issues/179#issuecomment-6805758864) | Generate rule-local fail and matched pass, per-ID reasons, mixed-model continuity. Hand-written examples and GR-D12 validation still establish intent. | GA1 A1–A3 |
| [GR-D10](https://github.com/vasiloglou/gnd-public/issues/181) | Opt-in ordered forbidden pairs and same-class implication, optional target marker, support, near-miss IDs and evolve proposals | GA2 B1–B3 |
| [GR-D11](https://github.com/vasiloglou/gnd-public/issues/182) | Typed literal mapping, reserved-dollar refusal, canonical export spelling and distinct head-pair support | GA3 C1–C3 |
| [Predecessor close](../../guarded-rule-workflows/006-milestone-close.md) | Three deferred requests are now activated. Reuse guard diagnostics and preserve edition and population comparison behavior. | All |
| [Earlier mined-rule draft](../../guarded-rule-workflows/notes/phase-GW1-spec.md) | Carry the same-predicate refusal conflict and scoped exception proposal into GA3 | GA3 C1 |
| [Open questions](../../../open-questions.md) and [CONTRIBUTING](../../../../CONTRIBUTING.md) | Existing ownership, repository gates and topic PR workflow | All |

Issue observations are grounded in GND 0.3.0. The phase records will bind
their actual source baselines. The predecessor merged as PR #184 at
`0ff0e9ca`. This framework milestone is verified with
public CLI fixtures.

## 2. Contract proposals

**GA1.** Add an opt-in guarded-case mode to `gnd synth` with a case manifest.
Each served guard has a checker-confirmed failure and a checker-confirmed
pass with at least one antecedent binding. Construct bindings by type,
preserve literals and repeated variables, and prove the target verdict
before asking the checker. Unsupported shapes, unreachable antecedents and
exhausted search have explicit per-rule reasons. Mixed-model controls
exercise mandatory and ring cases even when a guard is unserved. A
scoped ordinary-case lane must bind both the input and scoped model and
report any mismatch when a caller tries to measure against the full model.

**GA2.** Select an asserted, covered binary relation and classifying fact
type with explicit role coordinates and an optional target marker.
Forbidden-pair support counts distinct relation rows leaving the source
class. Require positive support and bound ordered pair enumeration.
For same-class implication count target-classified rows that meet the
marker condition. Record near misses and opaque counterexample IDs using
existing proposal conventions. Specify the handling of missing or ambiguous
classifications before coding, and test that mined counts agree with the
emitted guard on the covered domain.

**GA3.** Decode literals using the role's typed export spelling and preserve
the export bytes. Refuse a decoded dollar-prefixed string. Filter body rows
and fill head constants when recomputing distinct head-pair support. Admit
only matching positive support and full confidence. The issue's example
shares a body and head predicate. The earlier draft proposes a scoped
exception for an asserted rule with a literal in its head.

## 3. Dependencies and artifact homes

The phases can use the existing checker independently. GA3's smoke needs
all three. GA1 adapts `synth.service` and `synth.guarded`, reusing the value
pool, independent expectation and checker admission. GA2 adapts
`discover.service` and uses `discover.population_view` and
`discover.output` for identity and proposals. GA3 adapts
`export.mined_rules` and reuses `export.ilp_service` and typed join checks.

Consult searches covered guarded witnesses, conforming corpus generation,
joined candidates, proposal support, typed AMIE literals and mined-rule
support. The index review found 67 descriptions older than their code.
This plan uses the runtime paths and fixtures directly. A separate
component-index Review is available if the owner wants to refresh it.

## 4. Phases and criteria

| Phase | Gates |
|---|---|
| GA1 | A1 verifies both active outcomes for atom, absence, exists and comparison. A2 verifies per-ID refusals and preserved independent expectations. A3 runs a mixed-model corpus and existing synth/measure compatibility controls. |
| GA2 | B1 checks directed class-pair denominators and pair limits. B2 checks active same-class rules with and without a target marker. B3 verifies near-miss IDs, coverage refusals, bounded work and advisory proposal preview. |
| GA3 | C1 verifies all literal positions and the same-predicate example. C2 checks type, spelling, reserved prefix, independent counts and atomic refusal. C3 pins prior export/import behavior and runs the installed three-workflow smoke. |

## 5. Documentation and compatibility

Document case artifacts in the synth guide, joined discovery in the
discover reference, and AMIE mapping in the ILP bridge reference. Update
CLI and packaged guidance where affected, and regenerate component entries.

## 6. Risks and controls

Test vacuous passes, independent oracle disagreements, search exhaustion,
classifier ambiguity, reversed pairs, distinct head pairs after duplicate
body matches, and literal type/spelling collisions. Keep denial and
indeterminacy observable at each public route.

## 7. Out of scope

Automatic acceptance of discovered rules, live miner runs, dev-tools
changes, publishing, certification and vocabulary migration.

## 8. Execution and review

Use the selected project plan and close review instrument with bounded
convergence. Each phase needs its spec gate, implementation, focused
verification, independent diff review, refactoring review and record.
Keep merge authorization separate.

## 9. Verification story

GA1 exercises the shipped rule-check example and discriminating typed
guard fixtures, alongside the synth expectation and measure controls.
GA2 checks the generated guards against independent join counts and
previews the proposal. GA3 exercises a captured-format AMIE fixture
through export, import, preview and checker, then installs a wheel for
the combined smoke. Later specs select exact test commands and budgets.

## 10. Decisions

The owner selected all three issue scopes on 2026-11-11. The GA1 artifact
contract, GA2 classifier ambiguity policy, GA3 same-predicate exception
and successor review instrument remain proposed or pending.
