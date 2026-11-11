# Guarded rule authoring · plan r2

**Draft r2.** The owner invoked `process-milestone guarded-rule-authoring
auto` and selected the standard GND panel for plan and close. Round 1
reviewed r1. The amended bytes await the confirmation round and delegated
plan gate. See the [review disposition](plan-review-disposition.md).

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
pass sharing an antecedent binding with the failure. Target attribution is
by declared rule ID. Check unrelated findings separately. The acceptance
fixture includes an isolated pass and a failure that avoids collateral
mandatory and ring findings. Construct bindings by type,
preserve literals and repeated variables, and prove the target verdict
before asking the checker. Unsupported shapes, unreachable antecedents and
exhausted search have explicit per-rule reasons. GA1 proposes at most
128 candidate attempts and 100,000 oracle work units per guard, and
1,000,000 oracle work units across a run. Charge binding and witness
candidate visits. Report search exhaustion before attempting extra work. Mixed-model controls
exercise mandatory and ring cases even when a guard is unserved. A
scoped ordinary-case lane must bind both the input and scoped model and
retain an original-to-scoped constraint map. The ordinary measure
route rejects a scoped corpus used with the full model through its existing
model digest check. A3 tests that rejection.

**GA2.** Select an asserted, covered binary relation and classifying fact
type with explicit role coordinates and an optional target marker.
Forbidden-pair support counts distinct relation rows leaving the source
class. Require positive support and bound ordered pair enumeration.
For same-class implication count distinct target-classified relation rows
that meet the optional marker condition. Both counts must equal the
emitted guard's distinct antecedent bindings and be positive. Require a
covered, single-valued classification for every relation endpoint before
mining. Refuse absent or ambiguous classification with its reason.
Report near misses through the existing discover predicate and cap of
32 counterexample IDs, naming violating relation rows in population
order. Cap directed class pairs with `--max-pairs` and charge visits of
relation, classification, and candidate binding rows against an explicit
GA2 work ceiling. Pin the first candidate excluded at each limit.

**GA3.** Decode literals using the role's typed export spelling and preserve
the export bytes. Refuse a decoded dollar-prefixed string. Filter body rows
and fill head constants when recomputing distinct head-pair support. Require positive recomputed support exactly equal to AMIE's support
and zero unsupported head pairs. Deduplicate head pairs reached through
multiple body bindings. GA3 admits the asserted same-predicate example
when the head has a role-typed literal and retains refusal for a
variable-only head. Use the existing 1,000,000-row join guard per rule
and pin an aggregate recount limit in GA3. Refuse the whole import on
exhaustion.

## 3. Dependencies and artifact homes

The phases can use the existing checker independently. GA3's smoke needs
all three. GA1 adapts `synth.service` and `synth.guarded`, reusing the value
pool, independent expectation and checker admission. GA2 adapts
`discover.service` and uses `discover.population_view` and
`discover.output` for identity and proposals. The population view lives in
`src/gnd/discover/support.py`. GA3 adapts the indexed mined-rules component
in `src/gnd/export/ilp_amie.py` and reuses `export.ilp_service` and typed
join checks.

Consult searches covered guarded witnesses, conforming corpus generation,
joined candidates, proposal support, typed AMIE literals and mined-rule
support. The index review found 67 descriptions older than their code.
This plan uses the runtime paths and fixtures directly. Each phase regenerates changed entries. A repository-wide refresh is a
separate task.

## 4. Phases and criteria

| Phase | Gates |
|---|---|
| GA1 | A1 verifies a shared binding and both target outcomes for atom, absence, exists and comparison, plus isolated attribution. A2 verifies per-ID refusals, independent expectations and work limits. A3 verifies served pairs, an unserved reason and independently confirmed mandatory and ring cases in one mixed run, and a full-model measurement refusal for the scoped corpus. |
| GA2 | B1 checks directed class pairs and limits. B2 checks active same-class rules with and without a marker. Both compare independent joined counts to the emitted guards. B3 resolves each near-miss ID to a violating row, checks a candidate outside the threshold, pins coverage and work-limit refusals, previews the advisory proposal and pins non-joined discover behavior. |
| GA3 | C1 verifies all literal positions and the same-predicate example plus the variable-only refusal. C2 checks type, spelling, reserved prefix, exact distinct support, work limits and atomic refusal. C3 pins prior export/import behavior and runs the installed three-workflow smoke. |

## 5. Documentation and compatibility

GA1 owns the synth case artifact docs, GA2 the discover reference, and
GA3 the ILP bridge reference. Each phase verifies affected CLI and
packaged guidance and runs the strict component index check.

## 6. Risks and controls

Test vacuous passes, independent oracle disagreements, search exhaustion,
classifier ambiguity, reversed pairs, distinct head pairs after duplicate
body matches, and literal type/spelling collisions. Keep denial and
indeterminacy observable at each public route.

## 7. Out of scope

Automatic acceptance of discovered rules, live miner runs, dev-tools
changes, publishing, certification and vocabulary migration. A local wheel
build and install are part of the installed smoke.

## 8. Execution and review

Use the owner-selected standard GND panel for the plan and close.
The plan review budget is two rounds. Apply the project's convergence rule
to the confirmation round. Each phase needs its spec gate, implementation, focused
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

The owner selected all three issue scopes and the standard panel.
GA1's separate manifest and scoped measurement boundary, GA2's complete
functional classification requirement, and GA3's asserted literal-head
exception are proposed in r2 for confirmation under the delegated gate.
