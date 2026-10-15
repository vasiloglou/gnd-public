# Phase PL15 review (one Claude subagent, same model family)

Retained verbatim as delivered in the session on 2026-10-14. The reviewer was
read-only on `src/`, `tests/` and `docs/`. The file changed during the review
(two fixes landed concurrently). The reviewer re-ran every reproduction against
the final bytes. Start sha256 `ae91011655437f7036d2554164778565c98ceb3871bfa54f91eb2aaae8e60320`,
final sha256 `7300eff72da74acd49ca63d2254ae33953436e2636a44a582ad9d23bc8cf752a`.
Scratch reproductions: `scratchpad/pl15-review/` in the session.

---

## PL15 adversarial review: REVISE

**The file changed while I was reviewing it.**
- At the start, `src/gnd/export/pyrel_rules.py` had sha256 `ae91011655437f7036d2554164778565c98ceb3871bfa54f91eb2aaae8e60320`.
- At the end it has sha256 `7300eff72da74acd49ca63d2254ae33953436e2636a44a582ad9d23bc8cf752a`.
- The edit made two changes:
  - `apply_step` and `plan_states` no longer carry instance rosters, and `create` no longer adds to one.
  - Create freshness now reads the new `_present` relation.
- That fixed two findings I had reproduced, F1 and F2 (described at the end). I re-ran every repro against the final sha; everything below is stated against it.

**Setup.** Everything is in the scratchpad at `.../scratchpad/pl15-review/`.
- `cmp.py MODEL PRE STEPS` renders a fresh program, runs it with `--pre`/`--steps`, runs `gnd.api.transition(..., unredacted=True)`, and compares the two with the test's own `_assert_plan_agrees`.
- With `NORM=1`, `cmp.py` sorts GND's uniqueness witnesses first (see H2).
- `run.sh` builds a steps document with digests.
- Test models: `lab.orm.json`, `lab3.orm.json`, `card.orm.json`, `dynbind.orm.json`, `semi.orm.json`, `steps.orm.json`, `steps2.orm.json`, and `ref/model.orm.json`. Their generators are `mk*.py`. Every repro's `.pre.json` and `.steps.json` is kept there.
- Each repro below is one `cmp.py` run with the files named in its heading.

### Blocking

**F3. A double create in one step is not detected.**
- Location: `_plan_checks`, the create branch at about line 1933.
- GND's `_evaluate_step` fails a create whose value another create in the same step also mints. The program only checks the state before the step.
- Repro: `lab3.orm.json`, `l3.pre.json`, `l3.steps.json`. Operation `pair(a,b)` creates a and b and asserts a tag for each; the plan binds a=b=p2.
  - Program: exit 0, no step verdict.
  - GND: exit 1, `$.steps[1].effects[1].create` fail.
- Fix: add a static same-step check. For each pair of create effects on one object type, report a failure at the later effect's locator when their bound values are equal.

**F4. A dynamic rule whose subject binds its own value role.**
- Location: `_functional` (about line 1864) and `subject_atom` (about line 1956, `bind = {**subject.get("bind", {}), role: value}`).
- GND's `dynamic_subject_is_functional` removes the value role from the bound roles. `_subject_value` then matches the bound value (for example `level: "$l"`), so the old value is missing unless a fact (p, l) already exists.
- The program counts the value role as bound when testing functionality, and overwrites the value role's binding, so it drops that restriction.
- Repro: `dynbind.orm.json`, `f2.pre.json`, `f2.steps.json`. Operation `setl2` has subject bind `{person: $p, level: $l}` and `op: ">"`; the pre has level 5 and the step sets 2.
  - Program: exit 1, `violated [{"old": 5, "new": 2}]`.
  - GND: exit 2, `vacuous`.
- Fix:
  - Compute functionality over `bind − {value_role}`.
  - Keep the bound value as an equality condition on both the old and the new atom (old = bound value, and likewise for new).

**F5. GND's coverage gates are not reproduced.**
- Location: `read_steps` and `main`.
- GND's `api` runs three gates and refuses with exit 3: `assert_frame_coverage`, `assert_static_derivation_coverage` and `assert_dynamic_derivation_coverage`. The program has none of them.
- Repro (a): `lab.orm.json`, `h2.pre.json`, `h2.steps.json`. The pre's covers omit `person_level`, which `init_level` asserts.
  - Program: exit 4.
  - GND: exit 3, `transition:frame-coverage`.
- Repro (b): registrar model, `i1.pre.json` (the attempt-3 pre without `term_credits` in its covers), `attempt-3-accepted.steps.json`.
  - Program: exit 4.
  - GND: exit 3, `transition:dynamic-derivation-coverage`.
- Fix: embed the touched fact-type union and the derivation dependency closures at export, then refuse with the same rule ids, in GND's order.

**F6. A role or parameter named `step` corrupts the plan model and gives silent wrong answers.**
- Locations: `_step_field` / `_relations` (`Field('step')` is emitted twice), `stepped()` (`dict(row, step=k)` overwrites the role's value), and the `do_` load (`dict(b, step=k)` overwrites the parameter).
- `_RESERVED` only renames Python variables, not field names or dictionary keys.
- Repro (a): `steps.orm.json`, `j1.pre.json`, `j1.steps.json`. Fact type `has_step(recipe, step)`, a guarded rule `step <= 5`, and a `>` dynamic rule.
  - Program: exit 0. It misses `small` violated in state 1, misses the dynamic-rule fail at step 2, and prints a spurious assert-redundant warning at step 2.
  - GND: exit 1.
- Repro (b): `steps2.orm.json`, `j2.pre.json`, `j2.steps.json`. Only a parameter is named `step`.
  - The program misses GND's `$.steps[1].effects[0].assert` warning.
- Fix: give the state field a collision-proof name (for example `gnd_state`), carry state separately from the dictionaries, or refuse such models by name.

**F7. Compiled-subset obligations are silently ignored.**
- Spec §6.3 says such operations are "refused by name". Instead the registrar corpus model itself compiles one: `enroll.pre_offered` compiles to "every enrolls fact has a matching offered fact" on (course, term).
- GND reports it in `pre_snapshot_verdicts`, and it raises the band.
- Repro: registrar model, `cs2.pre.json` (the attempt-3 pre plus `enrolls(maya, PHIL101, winter)` and a matching `term_credits` claim), `cs.steps.json`.
  - Program: exit 0.
  - GND: exit 1 (`$.operations[id=enroll].compiled[0]` fail).
- Fix: refuse models where `compiled_obligations` has a `subset` entry, or lift each one as a state-0 subset requirement.

**F8. Validation of the steps document is incomplete; some malformed input exits 1, which reads as "violated".**
- Location: `read_steps`, about lines 1592–1633, and the `except` at about line 1756.
- Repro: `uv run python scratchpad/pl15-review/shape.py scratchpad/pl15-review` (needs `progs/reg.py`, which is regenerated from the final sha).
- Results:

| Steps document | GND | Program |
|---|---|---|
| no `model` key | 3 `steps-shape` | 0 |
| extra top-level key | 3 | 0 |
| extra key in a step | 3 | 0 |
| `pre_digest: null` | 3 | 0 |
| `steps_schema: true` | 3 | 0 (`True == 1`) |
| a step that is `1` or a list | 3 | **1** (uncaught `AttributeError` traceback) |
| 100k-deep nested JSON (`deep.steps.json`) | 3 | **1** (uncaught `RecursionError`) |

- The same deep JSON given as a single population also exits 1. That part predates PL15.
- Fix:
  - Validate with GND's `steps.schema.json`; the PyRel venv may lack jsonschema, so hand-code `additionalProperties`, the required keys, the types and the digest pattern.
  - Catch `AttributeError` and `RecursionError` and map them to exit 3.
  - Reject booleans in `steps_schema`.

### Hardening

**H1. Dynamic-rule witnesses and status when the data breaks the functional key.**
- GND compares the first matching fact's old and new values. The program compares every pair.
- Repro: `lab.orm.json`, `c1.pre.json`, `c1.steps.json`.
  - Step 6 (`init_level` without a retract): GND warns with one pair `{3,3}`; the program warns with two pairs.
  - Step 7 (`lvl_any`, `=`): GND passes; the program reports **violated** (alethic).
- The fuzz runs `fuzz-lab.orm-{1,2,3,5}` show the same thing.
- The exit is unaffected, because the state already violates the uniqueness constraint.

**H2. Witness order diverges in plans.**
- `apply_step` appends asserted facts. GND inserts them into the retracted facts' slots (`replacement_slots`). The program also sorts uniqueness witnesses.
- Effect on uniqueness: list order differs. This also happens in snapshots, for example `u.pop.json`.
- Effect on acyclic: `cycle_witness` picks a different cycle. Fuzz `fuzz-card.orm-{1,2,4}`, for example state 11: GND `[["a","a"]]`, program `[["b","b"]]`.
- `_assert_agrees` compares these lists exactly, so the corpus passes only by luck.
- Fix: reproduce the slot insertion in `apply_step`, and either sort in the test or reproduce GND's order.

**H3. Bounds drift from the spec.**
- Spec §4.2 says 1 MiB per file and 1,000 steps. The code has `STEPS_BYTES` = 10 MiB (which matches GND) and `STEPS_LIMIT` = 500.
- GND has no step cap, so a 501-step plan is refused by the program (exit 3, with no `[transition:…]` code) and accepted by GND (exit 0).

**H4. Untracked generated programs.** These are untracked and at risk of being committed: `my_rules.py`, `rules.py` and `rules_lqp.py` at the repo root, and `src/gnd/examples/bookrec/*.population.rules.py`.

### Completeness

**C1. `--post` is not refused by name.** It returns the generic usage message, exit 64. The spec (§6.3, test 4) asks for a refusal by name, and no test covers it. Argument order is also fixed: `--steps` given before `--pre` gives exit 64, while GND accepts any order.

**C2. The time bound is not met.** Spec test 5 says a 200-step plan under 60 s. The test was weakened to 100 steps, and 200 steps measured 82 s here (under concurrent load). Command: `long200.steps.json` with `progs/reg.py`.

**C3. The corpus lacks a "date rule per step"** promised in spec test 1; the registrar model has no Date. I checked dates by hand on a reference model (below), and it agreed.

**C4. Test gaps.** No tests cover:
- F1–F8 shapes;
- reserved names;
- the coverage gates;
- compiled obligations;
- same-step creates;
- non-dict steps.

`expected.json` was current when I regenerated it, but no test guards it against drift.

### Fixed during the review (do not re-raise)

**F1. Create freshness read the instance rosters.**
- Repro: registrar model, `a1.pre.json` (roster-only student `kim`), `a1.steps.json` (`admit kim`).
  - At sha ae91: program exit 1, GND exit 0.
- Repro: registrar model, attempt-3 pre, `a2.steps.json` (`admit zoe` twice).
  - At sha ae91: program exit 1, GND exit 0.
- Both agree at the final sha.

**F2. Rosters were carried into later states.**
- Repros: `b1` (mandatory constraint), `b3` (roster growth from create, and `pid_values`), and `e1` on `card.orm.json` (cardinality).
- At sha ae91 each disagreed with GND. All three agree at the final sha.

### Scenarios that agree with GND

- The four test files' `pyrel_oracle` tests: 185 passed.
- Wildcard retract plus assert (replace), and redundant asserts.
- Preconditions:
  - over derived heads: aggregate count per step, with recursion;
  - deontic multi-atom preconditions;
  - preconditions over reference facts, on a variant of `refused-dispatch-ops` with the derived head removed.
- Dynamic rules:
  - `>`, `=` and `!=`;
  - no old value and no new value (vacuous);
  - non-functional subjects (unchecked);
  - a subject the operation leaves untouched;
  - Date `>` with `date_add` rules per state.
- Vacuity transitions across states.
- Snapshot families per state: semiderived reads, ring irreflexive and acyclic (over asserted and derived facts), frequency, and cardinality per state.
- Binding-type checks (3.0, true, "3", 1e400, int vs String), and the digest mismatches.
- LQP `--compile` counts are correct for `lab`, `card`, `dynbind` and `semi`.
- 8 random 15-step registrar fuzz plans agree, once uniqueness witnesses are sorted.

Final sha256 of `src/gnd/export/pyrel_rules.py`: `7300eff72da74acd49ca63d2254ae33953436e2636a44a582ad9d23bc8cf752a` (the start sha was `ae91011655437f7036d2554164778565c98ceb3871bfa54f91eb2aaae8e60320`).
