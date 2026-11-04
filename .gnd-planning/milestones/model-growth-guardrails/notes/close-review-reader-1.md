Retained text of the reader's report. Local paths read `<repo>`, `<scratch>`.

# Close review, reader 1: additive policy (MG2) and shape report (MG3)

Subject: branch `claude/process-milestone-model-growth-4cac43` at `2ed15f8`, read-only.
Lens: plan §2.2, §2.3, completion predicates 2 and 3, MG-R1/R3/R4.

## Verdict

**approve-with-fixes.** Preview and apply share one policy implementation. The CLI option checks, the fresh/reviewed equality and the service re-run all behave as the contract says. The shape report never changed an exit or a flag-free digest in any probe. But one hole in the policy breaks the guarantee the policy itself states: object-scoped constraints get past it (F1). The code matches the letter of the plan's matrix, so predicate 2 as written is met. What fails is the contract's own claim that "no constraint on a populated fact type is added or strengthened" and that every admitted fact stays interpretable. An owner ruling is needed, then a small fix in `policy.py`.

## Findings

### F1 (blocking): object-scoped model-hosted constraints get past the additive policy

`additive_policy_issues` (`src/gnd/evolve/policy.py:340-352`) sets a model-hosted constraint's subjects to the `fact_type` values reachable in it. Three families name only object types and carry no `role_ref`:
- `value` with `object_type` only
- `cardinality` with `scope: object`
- `subtype-partition`

For these the subject set is empty, so the constraint counts as "not populated" and every ADD or MODIFY of one is admitted. The checker applies them to every value of the object type in the population (constraint-reference.md, "Object-type value constraint" and "Cardinality — object"). So a constraint can be added or narrowed even when the object type plays a role in a populated fact type, which is exactly what the policy exists to stop.

Reproduction. The fixture is `tests/fixtures/evolve-policy/base.orm.yaml`, where `customer_places_order` is populated with two sample rows. Each proposal adds one model-hosted constraint and goes through `EvolutionService.preview(policy="additive")` and then `apply`:

| Added constraint | Preview `policy_issues` | apply | `gnd check` on the two sample rows (before → after) |
|---|---|---|---|
| `{type: value, object_type: channel, allowed: [phone]}` | `()` | published | exit 2 → **exit 1**, `[fail] … Each channel value must be one of ['phone'] — violated: 'web', 'web'` |
| `{type: value, object_type: order_id, range: {min: 100, max: 200}}` (the reference value type of `order`) | `()` | published | exit 2 → **exit 1**, `order_id … violated: '10', '11' out of range` |
| `{type: cardinality, scope: object, object_type: order, bound: {max: 1}}` | `()` | published | exit 2 → **exit 1**, `number of order instances is at most 1 — violated: 2 observed` |
| control: `{type: value, object_type: channel, role_ref: {fact_type: customer_places_order, role: channel}, allowed: [phone]}` | `constraint.populated.add` | — | — |

Probe scripts: `probes/p1_ot_value.py`, `p2_apply.py`, `p5_card.py`, `p8_refvalue.py`. The population is `probes/pop.yaml`. All are in the scratchpad `close/probes/` directory beside this report. Candidate validation and D-12 both pass. The published model validates with exit 0, even though the model's own `sample_population` rows now fail.

Inferred, not reproduced: a MODIFY that narrows an existing object-scoped `value` or `cardinality` constraint is admitted the same way. So is a new `subtype-partition` over a supertype that plays a populated role. Both go through the same empty-subject path.

Suggested fix (needs an owner ruling, since it extends the plan's subject rule MG-D17): the subjects of a constraint naming `object_type`, `supertype` or `subtypes` should include every before-model fact type with a role played by that object type. It should also cover the entities that type identifies when it is a reference value type, and that type's subtypes and supertypes. Alternatively, the policy could treat any constraint naming an object type as populated whenever any fact type is populated. Add T1/T2-style cases for the three families, each with a `gnd check` before/after control like R-F2's, and add a line to the contract's "Populated" paragraph.

### F2 (completeness): wrong `operation_index` for an id added, deleted and added again

`_added_fact_types` (`src/gnd/evolve/shapes.py:35-52`) keeps the *first* ADD of an id. The signature and reading come from the candidate, which holds the *last* ADD's shape. Reproduction (`probes/p7_readd.py`): op0 adds `x_ft` as (order, memo), op1 deletes it, op2 adds `x_ft` as (order, amount). The report gives `[(0, 'x_ft', '{Order} has {Amount}')]` in the (amount, order) group. Op 0 never added that shape. The reader validator accepts this because op 0 is an ADD of `x_ft`.

This is advice only and no exit is affected. Fix: keep the last ADD per id (or skip ids that are also deleted), and add a case.

### F3 (completeness, no action required): parity baseline is `d5f6e9e`, not `1446f90`

Predicate 2 and MG-R1 name `1446f90`. The MG2 and MG3 parity tables were captured at `d5f6e9e` (main after MG1). The spec says why: the evolve package is unchanged since `1446f90`, and MG1's verbalization change is the one allowed exception. I re-ran `evidence/MG3/capture_parity.py` at HEAD and the output is byte-identical (`8abffb5b…`) to MG2 before/after and MG3 before/after. So MG4-MG6 did not move evolve previews either. The close record should say in one line that `d5f6e9e` stands in for `1446f90` on this surface.

## Checked and found sound

- **Preview and apply share one function.** `EvolutionService._policy_values` is called from both `preview` and `apply` (`service.py:1361`, `:1702-1709`). The apply re-run happens before candidate validation. The retry branch returns before the re-run, but the CLI only reaches it after the reviewed and staged identities match with the policy fields included (`_evolve_same_review_identity` excludes only `shape_matches` and the acceptance and digest fields).
- **CLI option agreement.** `--policy` and `--populated` are compared before the retry branch and before the fresh/reviewed equality. `--populated` without `--policy` exits 3, and the populated arguments are normalized to a sorted set on both sides.
- **Operation-by-operation bypasses I tried** all fail for the attacker:
  - weaken then strengthen in sequence: each step is judged on its own before/after, and each before must match the replayed document (`_apply_declared_operations`)
  - DELETE then ADD on a populated host
  - re-pointing a hosted constraint (R-F1, pinned)
  - a `ranges` list changing length (judged neither)
  - an inclusive flag added against its default (judged neither, which is conservative)
- I also probed constraints hosted on an unpopulated fact type whose `role_ref` points at a populated one, and a mandatory on an unpopulated fact type. The policy admits both. `gnd check` reports them vacuous over the populated rows, so they invalidate nothing and are not findings (`probes/p3_cross_host.py`, `p4_apply_check.py`).
- **Serialization.** The optional fields are omitted only when `None`. An empty `shape_matches` is written as `[]`, consistently in both the document and the digest body.
- **MG-R4 over the tracked corpus** (`probes/p6_shape_fuzz.py`). For all 255 tracked `*.orm.yaml` files I built a proposal adding duplicates of up to three fact types and previewed it with and without `--shape-report`:
  - 109 models preview on both sides with the same `breaking` and `report_sha256`, at least one group each, and the shape preview reads back equal to itself.
  - 144 fail on both sides with the same exception class.
  - 2 have no fact types.
  - In 0 cases did the exit or a digest differ.

## What I ran

- `uv run pytest -q -p no:cacheprovider tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py` → 112 passed.
- Probes p1 to p8 (service-level preview and apply in temp workspaces), plus `gnd check` and `gnd validate` on the published models.
- `capture_parity.py` at HEAD, writing to scratch.

## What I did not run

- The full MG2 or MG3 focused gates, the docs builds, the IL6 census, mutation testing, or RF1 pin recapture.
- A CLI-level (`gnd evolve preview/apply`) run of F1. I reproduced it through `EvolutionService`, which the CLI calls unchanged.
- The subtype-partition variant of F1 and the MODIFY-narrowing variant. Both are inferred from the same code path.

No repository file was modified. Every probe wrote only under the scratchpad.
