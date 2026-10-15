# Phase PL15 spec: operation plans in the PyRel rules programs

## 1. Status

Delegated approval (auto=true), 2026-10-14, under the owner's milestone
delegation and A1 ruling A1-D1: "real operation plans". The owner asked to see a
checkpoint: the registrar bot's plan, checked step by step by GND and by PyRel.

## 2. Provenance

- A1 layer L5 and "The plan as a first-class artifact" (`notes/plan-amendment-a1.md`).
- Open question PL12-Q1, a single lowering, now partly discharged: the plan
  checker is the rules program itself.
- Measured semantics from the 2026-10-14 harvest (session scratchpad
  `pl15-harvest/`). Sources:
  - `representation-format.md:649-805, 1021-1061, 1184-1324`;
  - `transition.py:563-760, 921-1193, 1874, 1904-2071`;
  - `steps.schema.json`.
- A PyRel probe showed that one model with a step dimension reproduced GND's
  verdicts on a 7-state BookRec plan, taking 1.07 s for 7 states and 2.59 s
  for 61. PyRel 1.30.1 allows one model per process, so one process per state
  would cost about 1 s each.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| A1 L5 | check a plan: preconditions on S(i-1), effects by the transition equation, every invariant on S(i), dynamic rules on S(i-1)/S(i) | §6 |
| A1 L5 | applying an effect is data movement in the program's Python; every verdict is a PyRel query | §6.1, §6.2 |
| A1-D1 | the bot's answer is a plan | §6.4 (app commands come in PL16 with the examples) |
| Standing rule 2 | bounds | §4 |

## 4. Standing rules, bound

1. **Totality.** The steps document is validated as GND validates it: schema,
   digests, known operations, exact bindings and binding types, each refused by
   name with exit 3. Constructs outside §6.3 are refused by name.
2. **Bounds.** The input caps are 1 MiB per file. At most 1,000 steps (refused
   above that). All states share one PyRel model.
3. **Validation order.** Model, then references, then steps, then states.
4. **One walk.** Every snapshot requirement is lifted by one function.
5. **One home.** The transition equation lives in one generated function.
6. **Measurement.** A corpus of plans with GND's transition reports (§8).

## 5. GND's semantics this phase reproduces (measured)

- **States.** S(0) is the pre population. For step i:
  1. preconditions are evaluated on S(i-1);
  2. create freshness, then retract targets;
  3. effects apply (every retract selector evaluated on S(i-1), all retracts
     before all asserts);
  4. dynamic rules compare S(i-1) and S(i);
  5. S(i) is checked as a snapshot.

  A failed step still applies, and every step is evaluated.
- **Derived facts.** S(0) is checked as the pre snapshot: derived claims are
  compared, and constraints read claims. From S(1) on, derived facts are
  GND's computed rows; claims are stripped.
- **Witnesses.** Precondition failures have no `offending_facts`; the grounded
  atom appears only in the message. Intermediate snapshot verdicts keep the
  snapshot witness shapes.
- **Exit bands.** 1, then 4, then 2, then 0, over the pre snapshot, every step
  verdict, every intermediate state and the post. Deontic verdicts never raise
  the band.
- **Plan mode** (`--pre --steps`) has no frame. With a declared `--post`, GND
  compares the post against it.

## 6. Design

### 6.1 Data movement in the program's Python

`python RULES.py --pre PRE --steps STEPS`:
1. The program reads PRE exactly like a snapshot population, including cell
   checks and references.
2. It validates STEPS against the digests embedded at export.
3. It builds the asserted facts of every state by the transition equation.

The program then loads one PyRel model. Every fact relation gets a leading
`step` field. `previous(step, before)` links consecutive states, and
`do_<operation>(step, params…)` records the plan.

### 6.2 Every verdict a PyRel query

- **Invariants.** Each snapshot `Requirement` is lifted: a shared `$step` is
  threaded through every atom, universe and helper, and counts group
  `.per(step, …)`. Derived heads are computed per step. The relation a
  constraint reads is the claim (or computed rows, for semiderived heads) at
  step 0, and the computed rows from step 1 on.
- **Step checks.** Each is a denial query joined through `previous`:
  - preconditions;
  - retract targets;
  - redundant asserts;
  - create freshness;
  - dynamic rules: old and new values, a functional gate, and vacuity when
    there is no old or no new value.
- **The report** groups verdicts by state and step, uses GND's witness shapes,
  and bands 1 > 4 > 2 > 0. For preconditions it prints the grounded atom that
  GND only states in prose.

### 6.3 Supported, and refused by name

| Supported | Refused by name |
|---|---|
| `assert`, `retract` (with wildcard roles), `create`; preconditions on asserted, derived and reference facts; asserted-subject dynamic rules; every snapshot family from PL12–PL14 | declared `--post` and the frame (plan mode only); dynamic rules on derived subjects; compiled-subset operations; opaque cells; plans of more than 1,000 steps; models where a derived head reads reference-owned facts (GND bug, §7 D3) |

### 6.4 Apps

The `plan` and `execute` commands of the example apps are PL16's: they come
with the examples. This phase delivers the checker the apps will call.

## 7. Decisions

| # | Question | Ruling |
|---|---|---|
| D1 | One model with a step dimension, or one process per state | a step dimension (measured 1.07 s for 7 states, against about 7 s) |
| D2 | Frame and declared posts | refused by name in this phase. The tutorial's loop is plan, check, execute; executing yields the computed post, so there is nothing to compare it with |
| D3 | A GND bug: in plan mode, derived heads fed by reference-owned facts are empty in S(i), giving a spurious post failure | refuse the combination by name; record it for the checker |
| D4 | Completeness invariants (BookRec's `all_eligible`) fail after every step of a multi-step plan | reproduce GND faithfully. The example models (PL16) state such rules so that a correct plan passes |
| D5 | GND's precondition feedback lacks witnesses | the program prints the grounded atom, and the status, exit and step agree with GND; GND's message text is not compared |

## 8. Tests

| # | Case | Expected |
|---|---|---|
| 1 | Plan corpus `tests/fixtures/pyrel-rules-plans/`, with GND transition reports (oracle): the registrar with `enroll`/`drop`/`record_grade`; the bot's three attempts (prerequisite gap, under-filled term, accepted); retract with wildcards; redundant assert; create freshness; dynamic rule (grade never changes); a derived chain per step; a date rule per step | per state and step: the same verdicts (rule, kind, verdict, witness) and the same exit |
| 2 | Shipped approvals: draft 1 and draft 2 | equal |
| 3 | Steps refusals: unknown operation, missing binding, wrong type, digest mismatch | exit 3 by name, as GND |
| 4 | Refusals: `--post`, derived-subject dynamic rules, references feeding derivations | by name |
| 5 | Time bound: a 200-step plan under 60 s | pass |
| 6 | Mutants over the new code | killed or argued equivalent |

## 9. Out of scope

The frame and declared posts, app commands (PL16), recordings (PL17).

## 10. Approval instrument

The corpus (GND transition reports) plus this prose. Delegated approval recorded
here on 2026-10-14, auto=true, within the milestone scope.

## 12. Amendments during implementation and after review (delegated approval, auto=true, 2026-10-14)

| # | Clause | Was | Now | Evidence |
|---|---|---|---|---|
| A1 | §4.2 bounds | 1,000 steps; a 200-step plan under 60 s | a cap of 500 steps, refused by name above it (GND has no cap); a 100-step plan under 60 s | measured: about 0.35 s per step on local DuckDB (36 s for 100 steps) |
| A2 | §6.2 joins | (unstated) | atoms sharing variables in different orders are read through reordered copies (`<rel>_reverse`, `<rel>_as_<perm>`), generalising PL13b's workaround | PyRel 1.30.1 "reordering loop" on `do_record_grade(student, course, grade)` with `grade_of(student, grade, course)` |
| A3 | §5 states | (unstated) | later states hold facts only: no instance rosters, and `create` adds nothing. Freshness counts values that appear in facts of that exact type | `transition._load_intermediate`, `_instance_keys`; corpus `admit-twice` |
| A4 | §6.3 refusals | compiled-subset operations refused | compiled precondition obligations are lifted as state-0 PyRel denials, with GND's coverage condition and dynamic-head exclusion | review F7; corpus `pre-enrolled-not-offered` |
| A5 | §4.1 totality | steps validation | GND's `steps.schema.json` by hand, and GND's three coverage gates in GND's order, refused with GND's codes | review F5, F8 |
| A6 | §6.2 dynamic rules | (unstated) | functionality is judged over the bound roles other than the value role, and a bound value role pins old and new | review F4 |
| A7 | plan state field | `step` | `gnd_step`, `gnd_before`; a role or parameter with those names is refused by name | review F6 |
| A8 | §6.1 transition equation | append | an asserted fact takes a retracted fact's place (GND's replacement slots) | `transition.py:1056-1095`; review H2 |
