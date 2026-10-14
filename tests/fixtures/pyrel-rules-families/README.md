# PyRel rules — constraint-family agreement corpus (PL13a)

Pins exactly how `gnd.api.check(model, population, unredacted=True)` reports
eight constraint families, so a PyRel generator can be compared witness for
witness. `expected.json` was produced by running GND (not by hand); each entry
has `exit_code`, `outcome`, `counts`, the ids that passed, and for every
non-pass verdict: `id` (mapped from `constraint_ref`), `constraint_type`,
`modality`, `verdict`, `reason_code`, `offending_facts` (verbatim), `note`
(witness shape), and GND's `message`.

`constraint_ref` is `constraints[i]` for top-level constraints and
`fact_types[<fact_type_id>].constraints[j]` (fact-type **id**, not index) for
inline ones.

One model per family (all `version: 1`, all pass `gnd validate`), so each
population exercises only its family and the exit code is attributable.

| Model | Constraints |
|---|---|
| `mandatory-disjunctive` | `md_passport_or_licence` over `person_has_passport.person`, `person_has_licence.person` (+ `person_has_nick` to introduce persons playing neither) |
| `value` | `v_score_0_to_100_excl` range `[0,100)`; `v_level_multi` ranges `[1,3]` and `(10,20]`; `v_age_gt_18` open-ended `(18,∞)`, **deontic** |
| `equality` | `eq_sbp_dbp` (single role), `eq_visits_likes` (two-role) |
| `exclusion` | `ex_married_widowed` (single role), `ex_owns_rents` (two-role) |
| `exclusive-or` / `exclusive-or-multi` | `xor_teach_or_take` single-role; `xor_multi_teach_take` two-role sequences |
| `frequency` | internal: `f_panel_2_to_3` {2..3}, `f_team_min_2` {min 2}, `f_club_max_2` {max 2, **deontic**}, `f_committee_exactly_3` {3..3}, `f_reviewer_paper_max_2` (two roles of a ternary, max 2) |
| `ring` | one fact type per variant, all 13 variants (`r_<variant>`); `r_symmetric_irreflexive` is **deontic** |
| `cardinality` | `card_country_1_to_3` (object), `card_person_id_max_4` (object on a reference value type, **deontic**), `card_head_max_1` (role), `card_resident_min_2` (role) |

## Populations

Named `<family>-<case>.population.json`. Every population sets `model`,
`model_id`, `source: fixture`, and `covers` = every fact type of its model,
except the `*uncovered*` cases (covers omitted or partial).

- `*-pass`, `*-pass-at-bounds`: everything satisfied, bounds hit exactly (frequency counts 2 and 3, min-only 2, max-only 2, exact 3; cardinality 3 countries, 1 head, resident count 2).
- `*-fail`, `*-fail-*`: violations; `*-fail-order` uses unsorted input and ids like `p10`/`p9` to pin witness order.
- `*-vacuous`: subject fact types empty (but covered).
- `*-one-side-empty`: equality/exclusion with one side empty; mandatory-disjunctive with one role empty.
- `value-boundary-excluded-endpoint`: 100 for `[0,100)`, 10 for `(10,20]`, 18 for `(18,∞)`; inclusive ends 0 and 20 pass.
- `value-deontic-only-violation`: only the deontic constraint violated.
- `ring-boundary-*`: self-loop for acyclic; two disjoint cycles; reflexive with `(n1,n1),(n1,n2)` (range-only n2) and `(n1,n2),(n2,n2)` (domain n1 lacking its loop); intransitive self-loop; transitive `(n1,n2),(n2,n1)`; acyclic-intransitive with both components violated; a single pair `(n1,n2)` for every variant.
- `mandatory-disjunctive-fail-roster`: an `instances:` roster member playing neither role.
- `cardinality-roster-only`: no facts, `instances: {country: [...]}` only; `cardinality-role-vacuous`: one role fact type empty.
- `exclusive-or*-fail-both`, `-fail-neither`, `-fail-both-and-neither`, `-uncovered`.
- `<family>-uncovered-fail`: the `-fail` facts with `covers` omitted.

## Observed GND behaviour (some of it surprising)

Exit bands: 1 = any alethic `fail`; 4 = alethic `unchecked`; 2 = `vacuous`; 0 =
clean. Deontic violations are `warning` and do not move the band
(`value-deontic-only-violation` exits 0).

1. **`reflexive` is domain-only, contradicting constraint-reference.md.** The
   doc says GND checks domain ∪ range (so `(1,2)` also needs `(2,2)`). The
   checker (`semantic_spec.ring_component_witness`) only checks first-role
   values: `ring-boundary-reflexive-range-only` passes, and `ring-fail`'s
   `(n1,n1),(n1,n2),(n3,n2)` reports only `["n3"]`.
2. **Combined ring variants report all components**, concatenated in
   component order (asymmetric+intransitive, acyclic+intransitive,
   symmetric+irreflexive, symmetric+intransitive). The doc says "report the
   first violated one". See `ring-boundary-acyclic-intransitive-both`:
   `[["n1","n2","n3","n1"],["n1","n2","n3"]]`.
3. **acyclic reports exactly one cycle** (`[x1,...,xk,x1]`; a self-loop is
   `[a,a]`), even when there are several (`ring-boundary-acyclic-two-cycles`
   reports only the 2-cycle). The cycle is deterministic: a depth-first search
   from each node in canonical order, successors in population order
   (`semantic_spec.ring_cycle_witness`). Measured stable across seven
   `PYTHONHASHSEED` values. (The first draft of this note said the cycle came
   from Python sets and could vary; the PL13a review refuted that.)
4. **Ring witness multiplicity:** asymmetric and antisymmetric list both
   directions of a symmetric pair; asymmetric includes self-loops;
   intransitive/transitive witnesses are `[a,b,c]` triples and include
   degenerate ones (an `n1` self-loop gives `[n1,n1,n1]`; symmetric-intransitive
   on `(1,2),(2,1),(1,1)` gives four triples).
5. **Witness order:** set-like families (mandatory-disjunctive, equality,
   exclusion, xor, frequency, cardinality, ring) are sorted in GND's canonical
   order (`semantic_spec.scalar_canonical_less`): booleans, then numbers by
   value, then strings, then null; rows compare value by value, a shorter
   prefix first. With strings this is string order (`p10` < `p3` < `p9`); with
   numbers it is numeric (`2` < `9` < `10`, `review/ring-integer`). **value** is
   the exception: one entry per offending fact in population order, duplicates
   kept (`[150,120,-5,100,150]`).
6. **equality** witnesses concatenate only-in-A (sorted) then only-in-B
   (sorted), with no side marker. One empty side is `fail`, not vacuous; both
   empty is `vacuous`. **exclusion** with one empty side is `pass`.
7. **exclusive-or single-role** witnesses list "plays both" first, then "plays
   neither", as `[v]` 1-lists without marking which half. It is *not* subject
   to coverage-omission vacuity: `exclusive-or-uncovered` still fails.
8. **exclusive-or multi-role:** if there is an overlapping tuple it is `fail`
   (exit 1) with the tuple(s) as witness. Otherwise it is `unchecked`,
   `reason_code: xor-disjunctive-undefined`, exit **4**, including for an
   uncovered population. Empty is `vacuous` (exit 2).
9. **mandatory-disjunctive:** if any role fact type is omitted from
   `covers`, the result is `vacuous` even when facts are present. If **all**
   role fact types are empty, it is `vacuous` even when a covered
   `person_has_nick` contains a person playing neither role. If one role fact
   type is empty, the constraint is evaluated. Witness: flat list of ids, not
   1-lists. Roster members count.
10. **Coverage omission does not matter for** value, equality, exclusion,
    frequency, ring, cardinality or single-role xor: `*-uncovered-fail`
    evaluates exactly like `*-fail`.
11. **cardinality object scope with `min ≥ 1` and zero instances is `fail`
    (exit 1), not vacuous.** The message says "0 observed" and the witness is `[]`
    (`cardinality-vacuous`, `card_country_1_to_3`), even though the doc's
    clause 3 says no-observable-subjects is vacuous. The `max`-only deontic
    `card_person_id_max_4` over the same empty population *is* vacuous.
    Cardinality witnesses list **all** counted instances/players, not just the
    excess. A roster for `country` does not populate `person_id`.
12. **frequency** witnesses are group keys (`[g]` or `[r,p]` in `roles`
    order); the count appears only in `message`. Min applies only to
    occurring groups.
13. **value** rules are evaluated over every fact *and* the `instances`
    roster; they are vacuous only when both are empty. A roster-only value can
    fail (`review/value-roster`, exit 1) or pass (`review/value-roster-pass`,
    exit 0).
14. **textual** rules are always `unchecked` (`textual-not-mechanical`). An
    alethic one sets exit 4, which outranks vacuous (2) but not a violation (1);
    a deontic one leaves the exit unchanged (`review/textual*`).

## review/

Reproductions from the PL13a independent review
(`.gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL13a-claude-review.md`),
added after the corpus above was fixed. `tests/test_pyrel_rules_families.py`
compares them live with `gnd.api.check` rather than through `expected.json`.
The `refuse-*` models and `helper-collision` must be refused by name: external
uniqueness and frequency are later phases, and a fact type named like a
generated helper relation (`likes_reverse`) would be shadowed by it.
