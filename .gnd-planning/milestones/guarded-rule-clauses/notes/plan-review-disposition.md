# Plan review disposition

The owner selected the Standard GND review panel for plan and close on
2026-11-15 and delegated approval rulings through the named milestone's
`auto=true` invocation. Round 1 reviewed plan r1 at `cc85b568`, plan SHA-256
`34c60d292b867fdf2f53c249b092efdef4331ea7288b759d488b2b2988f6b9e6`.

The panel and corrected finalization exited 0. The advisory result contains
five valid seats, six agreed groups, and twenty divergent concerns.
Gemini's response was malformed because it contained no JSON object.
Kimi retained all three declared concerns and one preamble line, which marked
the response incomplete. All retained concerns had anchored evidence.
[The report](../evidence/plan-review-r1/PANEL-REVIEW.md) accounts for each
concern. The immutable raw run is retained outside Git because one raw stream
contains a host path. Its canonical run digest is
`2c85153f902609f1e619d63ac66888e2d8234ab98713a65a854d93075116313b`.
The checked report and synthesis bind that digest. Round 1 describes r1 bytes.

## Disposition

| Concern | Classification | r2 decision |
|---|---|---|
| Helper differential and open-world unknowns | Blocking | §0 rule 6 limits the differential to covered and decidable populations with asserted preconditions; I2, N2/N3 and A2 exercise unknown outcomes directly. |
| Guarded negation coverage, undefined where and empty positive/filter results | Blocking | §2 GC2 specifies exclusion, unknown and vacuity, and N3 distinguishes positive-prefix diagnostics from filter-only emptiness. |
| Membership identity, incompatible kinds, numeric mixing, and term comparison coverage | Blocking | §2 GC1 defines the typed identity contract, enumerates legal sites, and separates legacy equality. GC1 I1–I3 pin the differences. |
| Pair existence and currently unsupported synthesis shapes | Blocking | I4 names reachable direct and existential cases, the existing v1 envelope, and a finite-domain refusal. N4 and A4 require reachable witnesses for the new forms. |
| Existential joint witnesses and disjunctive failure details | Blocking | §2 GC3 defines a joint-witness failure reason, witness-versus-unknown precedence and per-alternative scope. A1–A3 require corresponding fixtures. |
| Intermediate exporter compatibility | Hardening | I5 adds explicit named refusal checks for new GC1 syntax, including derivation filters. Later phases protect their own new forms. |
| Stated report version, diagnostic count and byte stability | Hardening | D3 documents v16 filter counts. D4 makes v17 conditional on a model using any_of in diagnostics mode. A3 pins existing output. |
| Negated atom reachability and stratification | Hardening | §2 GC2 allows a ground negative existence probe and pins covered derived facts and refusal of independently unstratifiable derivations. |
| Membership walk, alternative shapes and alternative-local variables | Hardening | §0 and §2 name the sites. GC1 checks each member and A1 pins refusal of cross-alternative bindings. |
| Smoke outcomes and report reader documentation | Hardening | E3 names the retail cases and requires observable expected outcomes in the GC4 spec. §5 gives version and field documentation a single home. |

The baseline term evaluator directly confirmed that Python equality makes
`true = 1` true, while guarded IR keys distinguish Boolean and number.
A Boolean domain with both values in its list demonstrates why one
membership verdict can be unreachable. The schema contains six references
to the shared term-comparison definition across guarded and derivation
locations. These checks inform the r2 contracts. Tests will determine
runtime behavior against the revised contracts.

## Confirmation budget

Two Standard panel plan rounds, with r2 as the confirmation subject. Use the
[project convergence rules](../../../../.codex/skills/process-phase/references/review-convergence.md)
and stop at the declared round budget. A plan ruling requires the project
bar of four valid seats and disposition of remaining blocking concerns.

## Confirmation

Round 2 reviewed plan r2 at `5892c71b`, SHA-256
`dc823aa2113a4bf2771cab9f4f89b673dd0887a2ffd3d27ff6be90c3147708bf`.
The panel and finalization each exited 0. The four valid seats met the
project bar. Gemini returned no JSON object. Kimi returned malformed JSON
before the response head. The four valid responses were complete. Codex's
negative-oracle concern lacked an anchored quotation and was checked against
the original I3 language and the two anchored reports on the same issue.
[The report](../evidence/plan-review-r2/PANEL-REVIEW.md) retains both agreed
groups and all sixteen divergent concerns. Raw evidence remains outside Git
because a raw stream contains a host path. The canonical run digest is
`d65d882dfbe5c33b0e63f6cba37270ffc782d3375f97e8292a17f24df559b8ba`.

| Round | Valid / attempted | Per-seat counts | On prior-repair text / total | Reviewer-reported blocking / total | Ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1 | 5 / 6 | Claude 9, Codex 5, Qwen 13, Kimi 3, GLM 6 | 0 / 36 | 13 / 36 | high | 5 revise |
| 2 | 4 / 6 | Claude 6, Codex 3, Qwen 10, GLM 2 | 10 / 21 | 6 / 21 | high | 4 revise |

Round 2's prior-repair rows are Claude's and Codex's existential-precedence
concerns, Codex's added membership-walk concern, and Qwen's membership
identity boundary, sample precondition, finite-domain scope, diagnostics
version rule, unknown aggregate, D1 table and duration granularity concerns.
The confirmation budget is exhausted.

| Remaining issue | Disposition |
|---|---|
| Guarded negation's source relation | Reproduced in extensions.constraint_view_legacy. §2 now binds GC2 to the same effective constraint view as positive guards and specifies asserted outcomes for covered consistent, covered inconsistent, and uncovered fully derived relations. Derivation consistency has its own verdict. Empty covered negative relations do not participate in positive vacuity. |
| Negative membership differential | I3 and T6 now pair positive membership with a same-domain semiderived atom and negative membership with absence of that atom. The harness asserts relevant coverage, same-domain identity and verdict diversity. |
| Existential precedence inside a disjunction | The shipped guarded exists evaluator retains an unknown if any assignment is undefined. GC3 preserves local semantics and applies true-over-unknown between alternatives. |
| Finite-domain synthesis | The completion statement limits this predicate to GC1. T7 specifies the Boolean case and the two existing named reasons. GC2's exclusion example retains an active satisfying binding. |
| Guarded temporal routing and literal-domain lint | GC1 names indexed, reference, and temporal paths. T3 pins role-resolved list-member lint and T5 pins temporal identity and legacy comparisons. |
| Exporter and diagnostic controls | The phase specs fix a per-profile expected outcome before implementation. Existing-model v16 bytes and positive-prefix semantics remain acceptance controls. GC1 preserves invalid-model refusal IDs and paths. |
| Feedback and verbalization | E3 pins business-rule IDs from the public flag. The sources table now includes the verbalization criteria. |

The plan gate will bind r3 after these targeted repairs. The confirmation
round's reviewer opinions describe r2.
