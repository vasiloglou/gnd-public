# Phase PL13b review (one Claude subagent, same model family)

Retained verbatim as delivered in the session on 2026-10-14. The reviewer was
read-only on `src/`, `tests/` and `docs/` and could not write this file itself.
Reviewed bytes: `src/gnd/export/pyrel_rules.py` sha256
`fb6feeb7c9e19abc290c25a6a40c58319547f243647266d46ccbdd61ffc1d6cf`, on HEAD
2bc86f5 plus uncommitted changes. Scratch reproductions:
`scratchpad/pl13b-review/` in the session.

---

REVISE. I found three blocking problems: two give wrong verdicts with no error, and one crashes on a common, supported join. Most other scenarios agree with GND.

Setup for every repro:
- Scratch directory S=/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public/fd814110-b392-4c16-8294-2db75ff438c9/scratchpad/pl13b-review
- `$S/mk.py` builds models and populations. `$S/m_*.py` writes each scenario.
- `$S/cmp.py MODEL POP...` renders the duckdb program into `$S/progs/`, runs it with `-I` under tutorials/runtimes/.venv/bin/python, and compares it with `gnd.api.check(..., unredacted=True)`. The comparison uses the suite's own `_assert_agrees`, `_as_verdicts` and `_ids` and prints AGREE or DISAGREE.
- `$S/exact.py MODEL POP OUT` fills each covered derived head's claim with GND's computed rows. It loops on GND's own findings.
- Every model below passes `uv run gnd validate`. Repo commands run from the repo root with `uv run`.
- Sanity check: `uv run pytest tests/test_pyrel_rules_derivations.py -m pyrel_oracle` gives 42 passed, and the default lane gives 19 passed.

**F1. Blocking: a ring `acyclic` witness on a semiderived head is built from the claims, not the computed rows.**
- Where: src/gnd/export/pyrel_rules.py:1141, in `judge`: `cycle_witness([... for row in facts.get(info['fact'], [])])`. The requirement rows come from the computed relation, but the witness reads the raw population.
- This breaks §5.3 and standing rule 5 (one home for the relation each constraint reads).
- Repro: `cd $S && uv run --project <repo> python m_ring.py`, then `uv run python $S/cmp.py $S/ring.orm.json $S/ring-*.population.json`. The model has `edge`, and a semiderived `reach` defined as the closure of `edge`, with `acyclic` on `reach`. The edges are n1→n2 and n2→n1.

| Population | GND `reach_acyclic` | Program `reach_acyclic` | Derivation verdict |
|---|---|---|---|
| claim empty | `[["n1","n1"]]` | `[[]]` | agrees |
| claim with its own cycle m1→m2 | `[["n1","n1"]]` | `[["m1","m2","m1"]]` | agrees |
| uncovered | `[["n1","n1"]]`, exit 1 | `[[]]`, exit 1 | — |

- The plain `derived` variant (ringd) agrees, because there the claims are what the constraint reads.
- Fix: build the cycle witness from the relation the constraint reads. Emit a listing of `h` (the computed relation for semiderived heads) and use it instead of `facts`. Better still, have one function return the facts each constraint reads.

**F2. Blocking: exact-tier arithmetic on Float values is evaluated in binary64, but GND uses exact rationals.**
- Where: `_FN` and `_expr` (pyrel_rules.py:898) and the `where` lowering (:973).
- §6.3 lists add, sub, mul, neg and abs as supported. representation-format.md says they are "evaluated with exact rational arithmetic internally", and a float contributes its exact `as_integer_ratio()`.
- Repro 1 (`m_fl.py`): stock(pen, qty=1); `tenth` is derived where `add($q, 0.1) = 1.1`.
  - Run `uv run python $S/cmp.py $S/fl.orm.json $S/fl-p.population.json`.
  - GND: exit 0, `derivation:tenth` pass.
  - Program: exit 1, `derivation:tenth violated [{"missing": {"item": "pen"}}]`.
  - Python agrees with the explanation: `1+0.1==1.1` is True, but `Fraction(1)+Fraction(0.1)==Fraction(1.1)` is False.
- Repro 2 (`m_num.py`, `num-base`):
  - `add($a,1) = $a` with a=1e16: GND pass, program `missing big`.
  - `mul($a,3) = 0.30000000000000004` with a=0.1: GND pass, program `missing tenth`.
- Fix: refuse by name any function term that touches a Float-typed variable or a non-integer literal, in a `where` or a head. The alternative is to scale to exact integers, which is not available in PyRel. Integer-only arithmetic agreed in every case I tried.

**F3. Blocking: in a semiderived recursive group, the "is it empty" query runs before the group's other rules are defined.**
- Where: `_derivations`, pyrel_rules.py:929-939. The query `found['computed:<head>'] = rows(...)` is emitted right after that head's own clauses.
- A PyRel query only compiles the rules defined so far. In a recursive group with two or more heads, a semiderived head's computed relation is therefore read before the group's other clauses exist.
- The report uses that value to decide vacuity (`empty = [not found.get('computed:'+ref) ...]`).
- Repro (`m_scc.py`): `alpha` (semiderived) = base ∪ beta; `beta` (semiderived) = alpha; uniqueness on beta.person; base = ann/1 and ann/2. Run `uv run python $S/cmp.py $S/scc.orm.json $S/scc-p.population.json $S/scc-x.population.json`.

| Population | GND | Program |
|---|---|---|
| empty claims | exit 1, `beta_unique` fail | exit 1, `beta_unique vacuous` |
| exact claims | exit 1, `beta_unique` fail `[{ann,1},{ann,2}]` | exit 2, `beta_unique vacuous` |

- The generated program defines `beta` and queries `computed:beta` at line 104, but `alpha`'s clauses only come at lines 105-112.
- Fix: emit every head's clauses first. Then emit the semiderived `h` definitions and all `computed:` queries, for example at the start of the rules section.

**F4. Blocking: a positive body that joins a relation with itself, swapped, crashes the program on every population.**
- Where: `_clause_lines` (pyrel_rules.py:~955).
- The generator already knows about this PyRel 1.30.1 bug. It works around it for ring constraints with the `<fact>_reverse` helper, but not for derivation bodies.
- Repro (`m_rec.py`, then a single-head split `rec_swap`): `swap(x,y) :- edge(x,y), edge(y,x)`. Run `uv run python $S/cmp.py $S/rec_swap.orm.json $S/rec_swap-x.population.json`.
  - GND: exit 0.
  - Program: exit 70, `AssertionError: _rewrite_aggregate_dependencies: reordering loop did not reach a fixpoint ... Please report this as a PyRel bug`.
- Non-linear recursion `tc(x,z), tc(z,y)` and swapped self-recursion `sym(x,y) :- sym(y,x)` both agree.
- The failure is safe (70, never read as a violation). I still rate it blocking because it is a natural supported construct and standing rule 1 requires a refusal by name.
- Fix: read the second occurrence through a generated reverse relation, or refuse the construct by name.

**F5. Hardening: two distinct variables can get the same Python name.**
- Where: `_Names.var` (pyrel_rules.py:708) calls `_ident(name, self.taken)`, and `taken` holds relation names only. So `$takes` becomes `takes_` (because a fact type `takes` exists), and `$takes_` also becomes `takes_`.
- Repro (`m_names3.py`): derived `same` with body `takes(m: $takes, found: $takes_)`. The generated code reads `takes_, takes_ = String.ref(), String.ref()` and `m.where(takes(takes_, takes_)).define(same_derived(takes_, takes_))`.
  - `names3-empty`: GND exit 1 with `derivation:same` missing a/b; the program exits 2 with `derivation:same OK`.
  - `names3-exact`: the program reports `derivation:same violated [{"extra": ...}]` and `found_mand vacuous`, while GND says pass and fail.
- The mechanism predates this phase (guarded rules), but derivation clauses widen it.
- Fix: map `$` names per statement and suffix on collision with any other variable in the same scope as well as with relations.
- Note: role names `m`, `found`, `h_x`, `std_math`, `aggregates`, `facts`, `h_row` and a fact type named `rows` all render and work once this collision is avoided (names2/names3).

**F6. Hardening: comparing a Float variable with an Integer variable in `where` crashes with exit 70.**
- Repro (`m_misc.py`): `where: $x < $n`, with x Float and n Integer. Run `uv run python $S/cmp.py $S/misc.orm.json $S/misc-p.population.json`.
  - GND: exit 1 with findings.
  - Program: exit 70, `[Unground Variables]` at `m.where(v_(s, n, x), x < n)`.
- `add($x,$n) > 1` and `$n > 2.5` work. Without that rule (misc2), everything agrees.
- Fix: refuse by name, or cast explicitly.

**F7. Hardening: Integer results wider than DECIMAL(38) crash with exit 70; GND computes them exactly.**
- Repro (`m_ovf.py`): head `mul(mul($q,$q),$q)` with q = 2^63-1.
  - GND: exit 1, missing qty=7846377...943.
  - Program: exit 70, `Overflow in multiplication of DECIMAL(38)`.
  - With q = 3e12 the two agree.
- Fix: state the bound and refuse by name (standing rule 2), or test values against it before running.

**F8. Hardening: opaque cells (format_version 2, `{"$opaque": ...}`) crash with exit 70.**
- GND gives them a defined semantics: `derivation:best unchecked opaque-value`, with exit 1 or 4.
- Repro: `uv run python $S/cmp.py $S/der.orm.json $S/der-opaque-v2.population.json $S/der-opaque-only.population.json`.
  - GND: exit 1 and exit 4.
  - Program: exit 70 in both cases, `Literal type not implemented for value type: <class 'dict'>`.
- Related, also existing before this phase: a type-mismatched claim (5.0 for an Integer role, `der-floatclaim`) gives GND exit 3 but program exit 70 (`TypeMismatch`).
- Fix: `read_population` should refuse `$opaque` cells and wrongly typed values by name, with exit 3.

**F9. Hardening, existing before this phase: an exclusion with swapped multi-role sequences crashes.**
- The trigger is the same PyRel bug as F4, but it also crashes with the HEAD version of pyrel_rules.py.
- Repro (`m_x.py`): run `uv run python $S/cmp.py $S/xswap.orm.json $S/xswap-hit.population.json`, which gives exit 70 where GND gives exit 1. The HEAD-rendered program `$S/xswap_head.py` also exits 70.
- I list it because it affects exclusions over derived heads (the names model).

**F10. Completeness: test gaps.**
- The corpus has no literals in body, `negate` or head atoms, apart from the `mul(...,150)` argument. It has no per-clause heads, no Float roles, no recursive group with several semiderived heads, and no ring `acyclic` over a semiderived head.
- Constraints over derived heads cover only uniqueness, value, ring irreflexive and guarded. Spec §8 row 1 claims constants and §5.3 coverage.
- The refusal tests cover only `avg`, `div`, `mod`, semiderived+aggregate and opaque rules. Row 3 promises every row of §6.3: sqrt, round, floor, ceil and haversine are missing. The render-time refusal "aggregate of a computed term" is untested.
- `test_lqp_cardinality_minimum_also_covers_an_empty_universe` only checks the text is present. Whether `count(...).where(..) >= 1` fails on an empty universe has not been verified on an engine.
- `test_rule_variables_have_readable_names` only rules out `k\d+` and `x_`; it would not catch F5.
- Suggested additions: F1, F2, F3 and F4 as corpus cases, plus the literal and Float cases.

**Scenarios that agree** (status, witness and exit):
- Semiderived and derived heads read by uniqueness, mandatory (including the uncovered → vacuous case), subset, exclusion, value with an instances roster, role and object cardinality, guarded, frequency, equality, exclusive-or and inclusive-or. Each was run with empty, uncovered, surplus, only-surplus, exact and empty-computed claims (models semi, der, fams, famd: 20 populations).
- Aggregates:
  - `count` where `of` is not in `over`;
  - a global `count` with no group, including over an empty body (no row);
  - `sum` with duplicate contributions removed across a join;
  - `min`/`max` with ties and negative values;
  - a group key taken from function-term heads (`add($n,1)`, `mul($m,2)`, `sub($m,1)`);
  - a post-aggregate `where` on `as` plus a `!=` on a group variable;
  - two clauses with a root aggregate, one of them with a constant head.
- Clauses:
  - per-clause heads with String and Boolean constants;
  - a constant in a body atom and in a negated atom;
  - root `where` combined with clause `where` and string `<`;
  - mutual recursion r1/r2 (one of them semiderived), with negation over a lower stratum and an upper negation of a semiderived head.
  - The cl model passed 12 random populations twice each (empty and exact claims).
- Recursion: non-linear transitive closure, swapped self-recursion, and the 500-edge chain test.
- Witness order: 8 random populations mixing String (unicode, quotes, backslash, tab, empty), negative Integers, Booleans and Floats (0.1, 1e-7, 1e16) agree on both the missing and the extra witness.
- Values: Integer vs Float claims (2 against 2.0), a Float body constant 3 matching 3.0 and 3, a Float head constant 2.5, an Integer `count` or `mul` into a Float head role, abs/neg/sub nesting, and `-0.0` and odd strings in literals.
- Covers: an uncovered head with `[]` (exit 4 on both sides), and an uncovered head with rows (exit 3 on both sides).
- Name collisions: a fact type `best_claimed` or `best_derived` beside the head `best` is refused by name.
- LQP `--compile` compiles exactly the expected number of requirements for all 11 scratch models: agg 16, cl 7, fams 13, famd 15, semi 8, der 9, ring 2, ringd 3, num 14, ovf 4, names2 6.

**Process note:** my first harness run wrote `tests/fixtures/pyrel-rules-derivations/registrar-semiderived.orm.rules.py` by mistake. I deleted it within seconds. No `.py` file remains there, and nothing else under src/, tests/ or docs/ was touched.

sha256 of src/gnd/export/pyrel_rules.py as reviewed, checked at the start and the end: fb6feeb7c9e19abc290c25a6a40c58319547f243647266d46ccbdd61ffc1d6cf
