# IK5 approval corpus -- the ILP bridge

Owner ruling IK5-D1 (corpus-first): these cases and their hand-written answers
are the approval instrument for `gnd export ilp` and `gnd import ilp-rules`.
- **Inputs:** [cases.json](cases.json).
- **Answers:** [expected.json](expected.json), plus the hand-written export
  files under [expected-export/](expected-export/).
- **Harness:** `tests/test_ilp_bridge.py`.

The files were written by
`.gnd-planning/milestones/induced-knowledge/evidence/IK5/build_ik5_corpus.py`,
which fills in real digests. The answers in it are written by hand from spec r1
(§6, §8). The existing `gnd check` was used only to confirm the verdict each
learned rule draws in each population.

**No learner ran (ruling IK5-D13 (a)).** Every learner output here is
hand-authored in Popper's printed syntax. The learner is recorded as
`popper 0.0.0+authored`, a version token that says so.

## The model and its six examples

[orders.orm.yaml](orders.orm.yaml) has orders with an integer amount and a
customer, plus two unary facts: an order is flagged, and a customer is
blocked. Its one declared rule, "an order has one customer", exists because a
class-mode manifest must name a rule; IK5 binds it and otherwise ignores it.

[m.labels.json](m.labels.json) labels six populations. Under IK5-D3, `negative`
is what the learned predicate `wrong` should cover.

| Example | Class | What is in it |
|---|---|---|
| `n1` | negative | order 2 is large (150) |
| `n2` | negative | order 3 is large (200); order 4 is small but flagged |
| `n3` | negative | one small order (10), flagged |
| `p1` | positive | two ordinary orders (30, 90) |
| `p2` | positive | one order exactly at 100, from a blocked customer |
| `v1` | positive | no orders at all |

## The three learned rules

The learner's printed program, [i2.popper.pl](i2.popper.pl), holds three
rules:

| Clause | Popper prints | GND writes (guarded) | GND covers | v1 |
|---|---|---|---|---|
| A (0) | `wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,100).` | when order `$v_b` has amount `$v_c`, then `$v_c <= 100` | n1, n2 | vacuous |
| B (1) | `wrong(A):- f_order_amount(A,B,C),f_order_flagged(A,B).` | when order `$v_b` has amount `$v_c`, then `$v_b` is **not** flagged | n2, n3 | vacuous |
| C (2) | `wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,80).` | when order `$v_b` has amount `$v_c`, then `$v_c <= 80` | n1, n2, p1, p2 | vacuous |

- **Rule A:** the comparison moves into the consequent, negated (`>` becomes
  `<=`).
- **Rule B:** has no comparison. The flagged atom is the last atom whose
  variables all appear elsewhere, so it becomes an absence.
- **Rule C:** is noisy. It also fires on two positive examples, so its support
  is 2 of 4 with counterexamples `p1` and `p2`.
- **v1:** has no amounts, so every rule is vacuous there. That counts as not
  covered, and the report lists `v1` under `vacuous` for each clause.

Each rule becomes an `induced`/`proposed`/`deontic` constraint. Its induction
block is computed by GND:
- `examples`: the covered negatives;
- `counterexamples`: the covered positives;
- `support`: covered negatives over all covered examples (IK5-D10);
- `evidence`: the digests of the export, the clauses and the run record.

## Export (criterion C1)

- **X1 -- the Popper export.** It writes exactly the files under
  `expected-export/popper/`:
  - `neutral.json`, the learner-neutral form;
  - `popper/bk.pl`, the facts with each one tagged by its example, then the
    four comparison definitions;
  - `popper/exs.pl`, `pos` for each negative population and `neg` for each
    positive one;
  - `popper/bias.pl`, the modes, one per fact type plus the four amount
    comparisons;
  - `export.json`, which lists each file's digest. Its own digest is the
    export digest E, which the command prints.

  The harness also runs it under two hash seeds and expects identical bytes.
- **X2 -- the neutral export** (`--target neutral`): only `neutral.json` and
  `export.json`. This target is not in spec r1 (finding C-F2).
- **XE1:** an expected-state manifest has no classes: exit 3, `expected-state`.
- **XE2:** a population with a hidden (opaque) amount cannot be rendered: exit
  3, `opaque`.
- **XE3:** the output directory already exists: exit 11.
- **XE4:** the manifest is missing: exit 66.
- **XE5:** a population path is a symbolic link: exit 74.

## Import, admitted (criteria C2, C3)

- **I1:** the three rules in the neutral clause form
  ([i1.clauses.json](i1.clauses.json)). Every reported set matches GND's, so
  the proposal adds the three constraints in `expected.json`: exit 0. The
  method is `ilp-neutral`.
- **I2:** the same rules as Popper prints them. The constraints are the same
  except for the method (`ilp-popper`) and the evidence digests.
- **I3:** `gnd evolve preview` of I1's proposal exits 0.
- **I4:** the proposal path already exists: exit 11.

## Import, refused on coverage (criterion C3) -- exit 3

- **M1:** rule A is reported as covering n1 and n3. That is the same count as
  GND's n1 and n2, but a different set: `coverage-mismatch`, clause 0.
- **M2:** rule A is reported as also covering v1, where GND finds it vacuous:
  `coverage-mismatch`, clause 0.
- **M3:** a reported example, `zz`, is not in the manifest:
  `unknown-example`.
- **M4:** a rule (amount > 1000) that covers nothing, reported as covering
  nothing: `covers-nothing`.

## Import, refused on the run record's binding (criterion C4) -- exit 3

- **B1:** the run record names a different export: `export-mismatch`.
- **B2:** the run record names different clause bytes: `clauses-mismatch`.
- **B3:** a Popper import whose run record names another learner:
  `learner-mismatch`.
- **B4:** the run record leaves clause 1 out: `coverage-shape`.
- **B5:** the run record lists clause 0 twice: `coverage-shape`.

## Import, refused by the fragment (criterion C2) -- exit 3, clause 0

There is one case per refusal name in spec §6. The plan's four named
constructs are given both as Popper text and in the neutral form.

| Case | Refusal | The clause |
|---|---|---|
| F01 | `head-shape` | `wrong(A,B)`: the head has two arguments |
| F02 / F03 | `negation-as-failure` | `\+ f_order_flagged(A,B)` / a neutral `not` |
| F04 / F05 | `disjunction` | `( … ; … )` / a neutral `or` |
| F06 / F07 | `aggregate` | `aggregate_all(count, …)` / a neutral `aggregate` |
| F08 | `unknown-predicate` | `f_order_total`, which the export never declared |
| F09 | `arity` | `f_order_amount(A,B)`, one role short |
| F10 | `recursion` | `wrong(A)` in its own body |
| F11 | `example-variable` | `f_order_amount(B,A,C)`: the first argument is not the example |
| F12 | `multiple-comparisons` | `> 100` and `< 500` together |
| F13 | `comparison-type` | `C > 'c1'` over customer codes |
| F14 | `non-ground-absence` | two atoms that share no variable |
| F15 | `empty-antecedent` | `f_order_flagged(A,8)` alone |
| F16 | `disconnected-body` | an amount and a blocked customer, not joined |
| F17 | `unbound-comparison` | a comparison over `D`, which no atom binds |
| F18 | `constant-spelling` | the constant `'$x'`, which guarded would read as a variable |
| F19 | `invalid-guarded` | an amount compared with the string `'x'`; the validator refuses it |
| F20 | `unparsable` | a missing comma; no clause index |
