# Phase PL13a spec: the remaining constraint families as PyRel requirements

## 1. Status

Delegated approval (auto=true), 2026-10-14, under the owner's rulings in
[`012-owner-decisions-a1.md`](../012-owner-decisions-a1.md). Implementable once
the agreement corpus (§8, row 1) is committed.

## 2. Provenance

- Plan amendment A1, PyRel layer L1, and PL12's open question PL12-Q1.
- Probes run 2026-10-14 with PyRel 1.30.1 and DuckDB 1.5.5, in
  `scratchpad/pl13a`:
  - **Counts.** Per-group counts (`aggregates.count(c, t).per(s)`), whole-type
    counts and inline count comparisons all run.
  - **Recursion.** A recursive `define` reaches its fixpoint.
  - **Requirements with aggregates.** `require` containing an aggregate compiles.
  - **PyRel bug, with a workaround.** A self-join with swapped arguments,
    `where(r(x, y), r(y, x))`, fails with "reordering loop did not reach a
    fixpoint". Joining against a defined reverse relation, `r_reverse(y, x)`,
    works. Every ring variant that needs the reverse uses that helper.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Owner: implement all five examples | families used by course, clinic, access, trip and lease | §6 |
| A1 L1 | admit families only after agreement with GND | §8, row 1 |
| PL12 standing rule | one `Requirement` list renders both programs | §6.1 |
| PL12 boundary | refuse what isn't reproduced | §6.3 |

## 4. Standing rules, bound

1. **Totality.** New lowering functions validate every key they read and refuse by
   name.
2. **Bounds.** Recursive closure is bounded by the input row cap (1 MiB of JSON);
   a time-bound test runs on a 500-edge chain.
3. **Validation order.** Unchanged.
4. **One walk.** One family table in `requirements()`.
5. **One home.** The family table.
6. **Measurement.** The corpus.

## 5. Goal

Both programs cover these families, and the DuckDB version agrees with
`gnd.api.check` on status, witness and exit for every population in
`tests/fixtures/pyrel-rules-families/`. The LQP version compiles one `Require`
per requirement statement.

## 6. Design

### 6.1 Helper relations and grouped reporting

- New helper relations, rendered once each:
  - `<fact>_reverse(b, a)`;
  - `<fact>_closure(a, b)`, recursive;
  - `<id>_allowed(v)`, now defined from value lists and from ranges;
  - `<id>_plays(x)` for inclusive-or.
- A constraint may lower to several requirements that share one `constraint`
  id. Examples:
  - equality is two subsets;
  - exclusive-or is inclusive-or plus exclusion;
  - reflexive is two checks;
  - frequency is a min check and a max check.

  The DuckDB report merges them into one verdict per constraint, in GND's
  witness shape (§6.2).

### 6.2 Family table (finalized against the corpus)

| Family | Requirement(s) |
|---|---|
| mandatory-disjunctive | domain `<type>_any(x)`; check `<id>_plays(x)` |
| value range or ranges | domain `<type>_any(x)`; check `<id>_allowed(x)` (helper defined per range) |
| equality | subset a→b and subset b→a |
| exclusion | domain sequence a; check `not_(sequence b)` |
| exclusive-or, single-role | inclusive-or, plus exclusion for each pair; multi-role refused (GND: exclusion half only, `unchecked`) |
| frequency, internal | domain the fact; checks `count(other roles).per(keys) >= min` and `<= max` |
| ring | irreflexive `x != y`; asymmetric `not_(reverse)`; antisymmetric `x == y` over `fact, reverse`; symmetric `reverse`; intransitive / transitive over a two-step chain; acyclic `x != y` over the closure; purely-reflexive `x == y`; reflexive `fact(x, x)` and `fact(y, y)`; combined variants as their components |
| cardinality, object or role | domain the universe or the role's players; checks on `aggregates.count(x)` |

### 6.3 Still refused by name

External uniqueness and external frequency, subtype partition, multi-role
exclusive-or, textual constraints (GND reports them unchecked; the programs list
them as not checked), derived fact types (PL13b), operations (PL15).

## 7. Decisions

| # | Question | Ruling |
|---|---|---|
| D1 | Swapped-argument self-joins | always go through `<fact>_reverse` (measured PyRel bug) |
| D2 | Acyclic witness | match GND's shape if the corpus shows it is reproducible; otherwise compare the set of nodes on a cycle, documented in the program |
| D3 | Cardinality minimum with an empty universe | follow the corpus |

## 8. Tests

| Case | Expected |
|---|---|
| 1. Agreement on every corpus population (oracle) | statuses, witnesses and exits equal |
| 2. LQP `--compile` count per model (oracle) | expected count |
| 3. Single source for every family | pass |
| 4. Refusals for §6.3 | exit 3 |
| 5. Time bound: acyclic over a 500-edge chain under 60 s (oracle) | pass |
| 6. Mutants for each new family | killed or argued equivalent |

## 9. Out of scope

Derived facts, recursion in user derivations and aggregates in derivations
(PL13b); calendar terms (PL14); plans (PL15).

## 10. Size

About 350 source lines and 250 test lines, plus the corpus.

## 11. Approval instrument

The corpus, `expected.json` generated by GND, plus this prose.
