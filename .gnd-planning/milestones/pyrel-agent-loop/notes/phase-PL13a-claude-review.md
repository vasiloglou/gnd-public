# Phase PL13a: independent adversarial review

- Reviewer: one Claude subagent (same model family as the author; not an independent model family)
- Date: 2026-10-14
- HEAD: `ab766a68b24a5b451ebb4bb9249354e7b091bd4f` plus uncommitted PL13a changes
- `shasum -a 256 src/gnd/export/pyrel_rules.py`: `906bd212cdeadc1226735f39d55006e44a6af6f71cb683ae70856b830b9a6e8c`
- Also read: `tests/test_pyrel_rules_families.py` (`c0407618…`), `expected.json` (`4f1e6b29…`)
- Scratch (models, populations, harness): `<scratch>/pl13a-review/`
  - `cmp.py MODEL POP...` renders the DuckDB program, runs it with the pinned interpreter, and prints the non-pass verdicts from `gnd.api.check(..., unredacted=True)` next to the program's.
- Baseline: `uv run pytest -q -m pyrel_oracle tests/test_pyrel_rules_families.py tests/test_pyrel_rules.py::test_acyclic_over_a_long_chain_finishes_in_time` gives 64 passed (67.6 s; the 501-edge chain took 8.4 s).

## Verdict: REVISE

The corpus is reproduced, and the lowering is sound for string-typed data. Outside the corpus I found two cases where the program and GND disagree:

- F1: the witness order differs for any numeric-typed value.
- F2: the status and exit code differ for value constraints when the only data is a roster.

Two other problems:

- F3: a helper-name collision can produce a false violation.
- F4: the stated reason for normalising the acyclic witness is false. GND's cycle is deterministic and can be reproduced (ruling D2, first branch).

Fix F1 to F4. None of them needs a redesign.

## Findings

### F1. Grouped witnesses use string order; GND orders numbers numerically (high, blocking)

- Location: `src/gnd/export/pyrel_rules.py:789-796` (`canon`, `distinct_sorted`), also used at lines 813, 815 and 830.
- Docstring: "GND's canonical order: compare values as strings".
- GND's actual order is NS-CANON-2 (`semantic_spec.scalar_canonical_less`): booleans, then numbers (numeric order), then strings, then null. Rows are compared lexicographically.
- The corpus is string-only, so this was never exercised. The repository's own examples use Integer ids (for example expense `101`).
- Scenario: `scratchpad/pl13a-review/ringint` (Integer `node_id`). Reproduce with `run.sh ringint p1.population.json`:

```
GND  r_irr  fail [[2, 2], [9, 9], [10, 10]]      PRG c_irr  violated [[10, 10], [2, 2], [9, 9]]
GND  r_asym fail [[2, 10], [3, 9], [9, 3], [10, 2]]  PRG c_asym violated [[10, 2], [2, 10], [3, 9], [9, 3]]
GND  r_refl fail [[2], [10]]                     PRG c_refl violated [[10], [2]]
```

- Same result elsewhere:
  - `freq/p1`: GND `[[2, 1], [10, 1]]`, program `[[10, 1], [2, 1]]`.
  - `md/p2`: inclusive-or, GND `[3, 10]`, program `[10, 3]`.
- Status and exit code agree; witness order does not. Spec §5 promises witness agreement, and README observation 5 ("canonical string order") wrongly generalises from string data.
- Fix:
  - Port NS-CANON-2 as a sort key, `(rank, numeric value | token)`, applied per cell and lexicographically per row.
  - Correct the README's observation 5.
  - Add Integer-typed populations to the corpus for at least ring, frequency and inclusive-or.

### F2. Value constraints are declared vacuous when only an `instances` roster is present (medium, blocking for ranges; pre-existing for `allowed`)

- Location: `pyrel_rules.py:270-272`, where `vacuous_when = ("all", plays)`; applied in `report` at line 856.
- GND treats object-scoped value constraints differently. In `semantic_spec.applicability_of`, the empty-subject vacuity rule does not apply to them. They are evaluated over the roster (facts plus instances), and are vacuous only if they pass and the roster is empty.
- Reproduce in `scratchpad/pl13a-review/val`:

```
m0 (range [0.5,2.5]) + p3 instances {score:[7]}, has_score [{score:1}]   GND fail [7]   PRG violated 7   (agree)
m.orm.json + p2.population.json (no facts, instances {score:[7], grade:[5]})
   GND exit 1: v_score fail [7], v_grade fail [5]
   PRG exit 2: v_score vacuous, v_grade vacuous
m0 + p4 (no facts, instances {score:[1]})       GND exit 0 accepted   PRG exit 2 vacuous
menum (allowed [1,2]) + p5 (instances {score:[7]})  GND exit 1 fail [7]  PRG exit 2 vacuous
```

- Both status and exit code disagree, so a violation is hidden.
- The `allowed` path has the same defect from PL12. PL13a extends it to ranges.
- Fix: for value constraints, make the decision on the `<type>_any` universe (vacuous iff it is empty), not on the fact lists. Pin this with corpus cases that have a roster and no facts.

### F3. Helper relation names can collide with model fact types and silently change the verdict (medium, hardening, must-fix)

- Location: `pyrel_rules.py:108-111` (`_Model.helper`), `582-592` (`_relation_roles`, which checks helpers before facts) and `562-566` (`_Names.relation`, which maps the same string to the same Python identifier).
- Helpers are named `<fact>_reverse`, `<fact>_closure`, `<id>_plays` and `<id>_allowed`; `<type>_any` is the pre-existing case. None of these names is reserved against model ids.
- Reproduce with `scratchpad/pl13a-review/collide`. The model has fact type `likes` (asymmetric) and a real fact type `likes_reverse` (irreflexive):

```
GND exit 1: likes fail [["n1","n1"]]; likes_reverse passes
PRG exit 1: c_asym violated [["n1","n1"]]; c_irr violated [["n1","n1"]]   <- false violation
```

- The generated program redefines `likes_reverse = m.Relationship(...)`. The irreflexive rule then reads the reversed `likes` rows.
- The same collision would turn a passing population into exit 1.
- Fix: put helpers in their own namespace, for example a `__` prefix that model id syntax cannot produce, or refuse by name when a helper name equals a fact type or object type id.

### F4. The acyclic normalisation rests on a false claim; GND's cycle is deterministic (medium, completeness and honesty)

- Locations:
  - `tests/test_pyrel_rules_families.py:9-10`: "picked from Python sets, so its start node and even which cycle is reported can vary".
  - `tests/fixtures/pyrel-rules-families/README.md:63-66`: "come from graphlib".
- Measured: `api.check` returns the same cycle under `PYTHONHASHSEED` 0, 1, 2, 3, 9, 13 and 21 (`scratchpad/pl13a-review/ring_str.population.json`), always `[["b","m","c","b"]]`. The 3-cycle `x,y,z`, the 3-cycle `b,c,m` and the 2-cycle `p,q` are all present.
- With Integer nodes `30→40→50→30`, `7↔8` and `100↔200`, the result is always `[[7, 8, 7]]`.
- This matches `semantic_spec.ring_cycle_witness`: a DFS from the smallest canonical node, with adjacency in canonical pair order.
- Under ruling D2's first branch, the shape can therefore be matched. The program reports instead every node on any cycle, as one sorted list.
- D2's fallback also requires the normalisation to be "documented in the program". The generated ring program (`scratchpad/pl13a-review/ring_duck.py`) does not mention the shape anywhere.
- Fix: either
  - reproduce GND's DFS in `judge` from `facts` (Python already holds the facts), or
  - keep the node set, but correct the README and test rationale and state the shape in the program header.

### F5. LQP cardinality minimum over an empty universe never fires; GND fails (low, completeness; engine-unverified)

- Location: `pyrel_rules.py:439-445`. The LQP rule is `m.where(country_any(x)).require(aggregates.count(x) >= 1)`.
- With no `country`, the domain is empty, so the requirement is vacuously met. GND reports `fail` with witness `[]` (corpus `cardinality-vacuous`, README observation 11).
- The DuckDB version hides this: `judge` recomputes the count in Python from the `members` listing. The `::min` and `::max` denial rows are computed and then never read.
- Measured with `card/dump.py`: `c_country_min::min` is `[]` on the empty population, while the verdict is `fail`.
- As a result, for cardinality the DuckDB version does not test the requirement it prints. Its header says "each rule is evaluated in its denial form".
- Fix:
  - Have `judge` use the denial rows, with the empty-universe minimum special-cased and stated.
  - Note in the LQP header that an empty universe never trips a minimum.

### F6. Refusals and spec drift in §6.3 and §8 (low, hardening)

- Spec §6.3 says textual constraints are listed "as not checked". The code refuses the whole model instead.
  - `gnd export pyrel tests/fixtures/adversarial/models/textual_alethic.orm.yaml --rules duckdb` exits 3 with `None: family 'textual' is a later phase`.
  - The message names `None`, because the top-level constraint has no id. That is not refusal "by name".
- Spec §8 row 4 calls for refusal tests for every §6.3 item. Missing:
  - external uniqueness and external frequency (both refuse with exit 3, checked in `scratchpad/refuse.py`);
  - textual;
  - multi-role exclusive-or, which is tested.
- `test_later_families_are_refused_by_name` (`tests/test_pyrel_rules.py:276-285`) still appends ring and frequency as top-level constraints. It now exercises only the generic else-branch, not a real refusal.
- Spec §6.1 and §6.2 say reflexive is "two checks… `fact(y, y)`". The code (correctly, matching GND) checks the domain only. Amend the spec.
- Spec §8 row 5 says under 60 s; `tests/test_pyrel_rules.py:197` asserts under 120 s on 501 edges.

### F7. Test strength (low, hardening)

- `tests/test_pyrel_rules_families.py:132` is a tautology: line 0 is compared with its own first token.
  - The LQP count check rests only on the program's exit code.
  - That code compares compiled nodes with `RULES[*].requires`, which the generator derives itself.
  - A lowering that drops a requirement stays self-consistent.
  - Pin the expected count per model in the test, as spec §8 row 2 asks (cardinality 5, equality 4, exclusion 2, exclusive-or 2, frequency 7, mandatory-disjunctive 1, ring 17, value 3, measured above).
- Branches with no failing corpus case:
  - exclusive-or `both_i_j` with i > 0 (needs three or more roles);
  - any numeric-typed grouped family (F1);
  - value with a roster only (F2);
  - helper name collision (F3).
- I checked the first by hand, and it agrees (`xor3/p1`, `p2`):

```
GND [["p1"],["p2"],["p3"],["p0"],["p10"],["p4"]] == PRG
```

## Scenarios checked that agree (no finding)

| Scenario | Dir/pop | Result |
|---|---|---|
| exclusive-or over 3 roles; pairwise "both" including both_1_2; roster member p0; neither | xor3/p1, p2 | agree |
| frequency over 2 key roles of a ternary, min=max=2, one group below and one above | freq/p1 | status agrees; order is F1 |
| `count(others).per(keys)` counts rows (different other-role tuples, shared values) | freq2/p1 | agree (`count` is distinct over the full other-role tuple, which equals rows because duplicates are refused) |
| frequency on a fact type missing from partial covers | freq/p2 | agree (evaluated) |
| ring on a fact type missing from partial covers | ringint/p3 | agree (evaluated) |
| deontic frequency and ring plus vacuous elsewhere: exit 2; warning does not raise the band | freq2/p2 | agree |
| equality and exclusion with role sequences in a different order from the fact type's declaration | eqx/p1 | agree |
| cardinality role scope, same player in several rows (distinct count) | card/p1 | agree |
| cardinality object scope on an entity vs its reference value type; roster on `person_id` only | card/p1, p3 | agree (`person_id` counts entity players; `person` does not count `person_id`-typed roles) |
| cardinality min ≥ 1 with an empty universe: fail `[]` | card/p2 | agree |
| value range with float bounds on Integer; Float with integer bounds; reference value type ranges | val/p1_0, p1_2 | agree |
| inclusive-or with covers absent, all covered, and partly covered with roster | md/p1-3 | agree, apart from F1 order |
| LQP `--compile`: Require count equals expected for all 8 models | lqp/ | agree |

Outside PL13a, for the record: GND itself crashes (exit 70, "witness for 'snapshot:value:range:violated:alethic' has no admissible origin") on a Float value `2.0` against an exclusive max of `2` (`val/m1.orm.json` plus a population with weight `[2.0]`). The program reports it as a violation, which looks right. This is a GND checker defect, not a PL13a one.
