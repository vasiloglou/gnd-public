# PyRel rules: derivation agreement corpus (PL13b)

Pins how `gnd.api.check(model, population, unredacted=True)` reports derived
fact types, so the generated PyRel rules programs can be compared verdict for
verdict. `expected.json` was produced by running GND, not written by hand. Each
entry has the exit code, the constraint verdicts with `offending_facts`, and
the derivation verdicts with their findings.

| Model | Derived heads and features |
|---|---|
| `registrar-derived`, `registrar-semiderived` | `prerequisite_chain`: two clauses, recursive. `missing_prerequisite`: a join with negation over an asserted fact type, reading the computed chain. The chain carries a ring rule, and a guarded rule reads it |
| `orders` | `order_total` (sum with `over`), `customer_orders` (count), `largest_line` and `smallest_line` (max and min), `big_order` (post-aggregate `where`), `line_cents` (`where` and a `mul` head), `priority` (two clauses, one reading a derived head). A uniqueness rule and a value range read derived heads |
| `mutual` | `odd_path` and `even_path`, mutually recursive |

Populations are named `<model>-<case>.population.json`. They cover:
- an exact claim;
- missing facts;
- extra facts;
- both;
- a head left out of `covers` (exit 4);
- a semiderived surplus (accepted);
- a wrong claim that a constraint then reads.

## GND behaviour these cases pin

1. One alethic verdict per structured derived head. It fails with up to two
   findings, missing then extra; a semiderived head never fails for extras.
2. Each finding shows one fact: the least missing or extra fact by GND's
   identity tokens, compared as UTF-8 bytes. So 11 comes before 2
   (`orders-numeric-witness-order`).
3. A head not in `covers` is unchecked (exit 4). Exit 1 outranks it, and it
   outranks vacuous (exit 2). Claim rows for an uncovered head make the input
   invalid (exit 3).
4. Constraints read the claim of a `derived` head (empty when not covered) and
   the computed facts of a `semiderived` head. Rules always read computed facts
   (`registrar-*-uncovered`).
5. A guarded rule is vacuous when an antecedent fact type it reads is empty,
   derived ones included.

## Left out

- A `semiderived` head with an aggregate stops GND with an internal error
  (exit 70, "derived origin lineage missing"), so there is no verdict to match.
  The programs refuse that combination by name.
- `avg`, `div`, `round`, `mod` and the other non-exact functions are refused by
  name (PL14). So is arithmetic touching a Float variable or a non-integer
  literal: GND computes `add`, `sub`, `mul`, `neg` and `abs` as exact
  rationals, while PyRel uses binary floats (`review/fl`, `review/num`). So is
  a `where` comparing a Float variable with an Integer one (`review/misc`).
- Opaque cells (`{"$opaque": ...}`) are refused by name with exit 3. GND
  evaluates them (exit 1 or 4).
- Integer results wider than DECIMAL(38) stop the program with exit 70. GND
  computes them exactly.

## review/

These are the PL13b independent review's reproductions, compared live with
`gnd.api.check`:
- an acyclic rule over a semiderived head (`ring`);
- a recursive group of two semiderived heads (`scc`);
- a body that joins a relation with itself, swapped (`rec_swap`). PyRel 1.30.1
  cannot compile that join, so the program reads the second atom through a
  reversed copy;
- variables named `$takes` and `$takes_` beside a fact type `takes` (`names3`);
- an exclusion over swapped role sequences (`xswap`);
- a Float claim in an Integer role (`der-floatclaim`, exit 3).
