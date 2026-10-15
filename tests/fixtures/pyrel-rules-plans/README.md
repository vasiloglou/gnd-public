# PyRel rules: plan corpus (PL15)

`expected.json` holds GND's own plan walks, produced by
`gnd.api.transition(model, pre, steps, unredacted=True)`. For each plan it
records:
- the exit code;
- the pre-snapshot verdicts and derivations;
- the compiled precondition obligations;
- per step, the failing step checks with their locators and the intermediate
  snapshot verdicts.

| Model | What it exercises |
|---|---|
| `registrar` (version 2) | Operations: `enroll` (with a precondition), `drop`, `drop_term` (wildcard retract), `record_grade`, `change_grade` (retract plus assert, and a dynamic rule that a grade never changes), `admit` (create). Invariants per state: a guarded rule over a recursive derived chain, an exclusion, frequency, a credit cap over a derived sum, and uniqueness |
| `registrar-nonfunctional` | The same model without the grade uniqueness rule, so GND leaves the dynamic rule unchecked |
| `registrar-semiderived` | The chain is semiderived. Its claim is compared at state 0 only |

The tutorial bot's three attempts are `attempt-1-prerequisites`,
`attempt-2-not-offered` and `attempt-3-accepted`. The other plans each target
one step check or state rule.

## GND behaviour these cases pin

1. **Step order.** Preconditions are read on the state before a step. Effects
   follow the transition equation: every retract reads the state before, all
   retracts come before all asserts, and an asserted fact takes a retracted
   fact's place. A failed step still applies, and every later step is
   evaluated.
2. **Derived facts across states.** State 0 compares derived claims. Later
   states use computed facts and keep no instance rosters (GND re-loads them
   from facts alone).
3. **Step checks.** Only failing ones are listed, at GND's locators.
   - A redundant assert is a deontic warning, even when the same step first
     retracts the fact.
   - A create fails if the value already appears in a fact of that type, or if
     another create in the same step mints it.
   - A dynamic rule is unchecked when no uniqueness rule makes its subject
     single-valued, and vacuous when there is no old or new value.
4. **Compiled obligations.** `enroll`'s precondition compiles to "every
   `enrolls` fact has a matching `offered` fact", judged on the pre-state
   (`pre-enrolled-not-offered`).

## review/

These are the PL15 independent review's reproductions, compared live:
- two creates of one value in a step (`lab3`);
- a dynamic rule whose subject binds its own value role (`dynbind`);
- a role and a parameter named `step` (`steps`, `steps2`);
- the coverage gates (`lab` with `h2`, and `i1` on the registrar).

`refused-dispatch-ops/` is a v4 model with operations and a derived head over
reference facts. GND's plan walk computes that head empty in later states (a
checker bug), so the export refuses it.
