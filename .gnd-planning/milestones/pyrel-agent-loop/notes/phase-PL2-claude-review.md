# Phase PL2 review: the rules written in PyRel

reviewer = one Claude subagent (same model family as the author); independent,
adversarial, read-only except this file
date = 2026-10-14
HEAD = ad85288d918a28bc6281b600b003384511431d34 (branch codex/pyrel-agent-loop;
reviewed files are untracked on top of it)
PyRel interpreter = tutorials/runtimes/.venv/bin/python (relationalai 1.30.1, DuckDB 1.5.5)

Reviewed bytes (`shasum -a 256`):

```
e1e604e4c94ea1137be3fc1a7e91608159d7add127f93b39114900ee5b839f10  src/gnd/examples/bookrec/rules_in_pyrel.py
6f3f725fa89760ae9a847b0c9d80d96d52f3ab305a6a7a10bddd8d222a342322  src/gnd/examples/expense/rules_in_pyrel.py
e1e604e4c94ea1137be3fc1a7e91608159d7add127f93b39114900ee5b839f10  docs/assets/applications/bookrec-rules-in-pyrel.txt
6f3f725fa89760ae9a847b0c9d80d96d52f3ab305a6a7a10bddd8d222a342322  docs/assets/applications/expense-rules-in-pyrel.txt
e31e60810fa36e290f07cef71001c0654b9357cd8b537f884fe57e01559b45ce  tests/test_rules_in_pyrel.py
ea69b02913331b17556dbf79bde7e593dd89a834ea98e9c4e82ce39237c0be85  tests/test_rf7_structure.py  (allowlist lines 25-26, committed in PL1)
```

## Verdict: revise

The shipped corpus agrees witness for witness and the three pinned witnesses
are printed (14/14 tests green, ruff clean, twins byte-identical). Off the
corpus I found one reproducible disagreement inside a rule the expense script
claims to implement (F1), one universe gap in the same rule (F2), and a
systematic "OK where GND says vacuous" divergence that the docstrings
contradict (F3). F1 is a two-token fix plus one corpus case; F3 and F4 are
docstring honesty. Nothing here is a safety or integrity problem; nothing
blocks the milestone, but completion predicate 3 ("print the same witness GND
prints") is false for F1 and should be made true before PL5 quotes these
scripts on a page.

## Method

Read the spec, plan §0/§2/§4, both models, all eleven corpus populations, the
reference checker (`src/gnd/checker/_core.py` vacuity rules at 1005-1055 and
exit mapping in `_reports.py` 160-180), `gnd.universe` roster handling, and
`ApplicationOracle.guarded`/`_mandatory`/`_one_direction`/`_value` in
`src/gnd/export/pyrel_runtime.py`. Built a scratch harness that runs each
script under the PyRel interpreter with `-I` and `gnd.api.check(..., unredacted=True)`
on the same population and prints both. Authored 22 new populations under the
session scratchpad (repo untouched). Harness and populations:
`/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public/fd814110-b392-4c16-8294-2db75ff438c9/scratchpad/{harness.py,gen_pops.py,pops/}`.

Baseline runs:

```
$ uv run pytest -q -m pyrel_oracle tests/test_rules_in_pyrel.py
14 passed in 13.95s
$ uv run ruff check src/gnd/examples/bookrec/rules_in_pyrel.py src/gnd/examples/expense/rules_in_pyrel.py tests/test_rules_in_pyrel.py
All checks passed!
$ cmp src/gnd/examples/{bookrec,expense}/rules_in_pyrel.py docs/assets/applications/*-rules-in-pyrel.txt   # both identical
```

## Agreement confirmed (no finding)

Populations where script and GND agree exactly on witness set, status and
exit, covering the task's requested scenarios:

| Case | Scenario | Both report |
|---|---|---|
| b1 | two minors (ada, cy) recommended adult `night`; ada also rated it (book both rated and adult); ben adult | `unread_only {$b:night,$u:ada}`; `age_appropriate` ×2 (ada, cy); `preferred_genre` warning ×2 (ben, cy); exit 1 |
| b6 | b1 with `user_prefers_genre` empty (`not_` over an undefined relation) | as b1 plus `preferred_genre` warning for ada; exit 1 |
| e1 | expense 101 in both `meals` and `travel`, amount 90 | `policy_meals {$a:90,$e:101}` (GND additionally fails `one_expense_in_category`, see F4) |
| e3 | category `gifts` on two expenses, amount 5000 | `known_categories "gifts"`; no cap rule fires in either (see F5 for multiplicity) |
| e8 | amounts 0 and -5; three team-lead approvals incl. 1400 | `positive_amount` ×2, `approval_limit_team_lead {$a:1400,$e:103}`; exit 1 |
| e12 | chain `ceo`, amount 99999 equipment | `known_chains "ceo"`, `policy_equipment`; no limit rule fires in either |
| e9 | expense 101 has EUR and USD | `supported_currency "USD"` (GND additionally fails `one_expense_has_currency`, F4) |
| e2 | id 104 only in `expense_is_approved` | both subset rules `[104]` (GND additionally fails three mandatory rules, F4) |
| corpus | all 11 cases | identical (test) |

Literal antecedent binds (`"team-lead"`, `"meals"`, ...) are matched by the
scripts' `chain(e, name)` / `category(e, name)` patterns; the consequent
operators are correctly negated (`<=` → `>`, `>` → `<=`, atom → `not_`,
absence → positive atom); deontic `preferred_genre` is reported `warning` and
does not affect the exit code. Guarded vacuity (any antecedent list empty →
no witness) matches GND's `empty-subject-any` rule at the witness level.
Subset vacuity: the scripts skip when the subset side is empty; GND reports
`pass` (∅ ⊆ X) when only that side is empty and `vacuous` when both are; no
witness in any case, so witness sets agree.

## Findings

### F1. Mandatory rule fires where GND is vacuous — `src/gnd/examples/expense/rules_in_pyrel.py:107-110`

Scenario: a population under `currency.orm.json` whose `covers` lists
`expense_has_currency` but whose `expense_has_currency` fact list is empty
(a reader deletes all currency facts to "see the rule fire"). GND's D-12
empty-subject rule makes the mandatory constraint `vacuous` (checker
`_core.py:1046-1053`, scope = subject fact type) and exits 2. The script
guards only on `if ids:` and reports every expense as violating.

Reproduction (`e5-currency-empty.json` = corpus `currency.population.json`
with `"expense_has_currency": []`):

```
--- SCRIPT exit=1
required_expense_has_currency  violated  [101]
required_expense_has_currency  violated  [102]
required_expense_has_currency  violated  [103]
--- GND exit=2
one_expense_has_currency  vacuous  []
required_expense_has_currency  vacuous  []
supported_currency  vacuous  []
```

Severity: medium. Class: blocking for completion predicate 3 (direct witness
disagreement in a covered rule); the fix is `if ids and facts['expense_has_currency']:`
(then the residual is only F3's `OK`-vs-`vacuous` labelling) plus adding this
population to `CASES` with expected exit — which exposes F3 immediately, since
the test asserts `native_exit == gnd_exit` and GND returns 2.

### F2. Closed-world `expense` relation ignores the `instances` roster — `expense/rules_in_pyrel.py:62-66`

GND's universe for an entity type is every value playing one of its roles
across all facts **plus** `population.instances[T]` (`gnd/universe.py:303-334`).
The script builds `expense` from the six fact lists only, as its comment
says. An id present only in `expense_has_currency` IS in the script's
universe (e4 confirms `required_expense_has_currency` passes for 105 in
both), so that part agrees; the roster does not.

Reproduction (`e6-instances-roster.json` = corpus currency population plus
`"instances": {"expense": [106]}`):

```
--- SCRIPT exit=0            (all rules OK)
--- GND exit=1
required_expense_submitted_by_employee  fail  [106]
required_expense_has_amount  fail  [106]
required_expense_in_category  fail  [106]
required_expense_has_currency  fail  [106]
```

Severity: low (no tutorial population carries a roster). Class: hardening.
Either extend `ids` with `document.get('instances', {}).get('expense', [])`
or state in the docstring that the hand-written universe is the fact lists.

### F3. `OK` and exit 0 where GND reports `vacuous` and exit 2 — both scripts, `main()`; docstrings bookrec:4-6, expense:5

Any empty antecedent list (guarded), both-empty subset sides, empty value
universe: GND verdict `vacuous`, exit 2 (`_reports.py:164,171`). The scripts
print `<rule>  OK` and exit 0. This is spec-conformant (§6: "or `{rule}  OK`";
exit 1 only on violation) but the bookrec docstring says "No row means the
rule holds on these facts", which is exactly the claim GND refuses to make
for an empty antecedent. The agreement test would fail on any corpus case
with an empty list because it asserts exit equality.

Reproduction (`b2-empty-minors.json`, `user_is_minor: []`; `b5-missing-key.json`
with the key absent; `e11-empty-approvals.json`):

```
b2: SCRIPT exit=0  age_appropriate  OK          | GND exit=2  age_appropriate  vacuous  []
e11: SCRIPT exit=0 (12 OK lines)                | GND exit=2  7 constraints vacuous (incl. approval_limit_*, known_chains)
```

Severity: low-medium. Class: hardening/honesty. Minimal: change the docstring
sentence to "No row means no breach on these facts; GND additionally reports
a rule with an empty antecedent as vacuous" or print `vacuous` when an
antecedent list is empty (and decide the exit code explicitly in the spec).

### F4. The scripts implement a subset of the model's constraints and the expense docstring does not say so — `expense/rules_in_pyrel.py:1-8`, `bookrec/rules_in_pyrel.py:1`

Not implemented: bookrec `book_has_genre` uniqueness and mandatory (2 of 5
constraints); expense `one_expense_*` uniqueness (5, or 6 with currency) and
mandatory `required_expense_submitted_by_employee`, `required_expense_has_amount`,
`required_expense_in_category` (12 of 21 implemented under `model.orm.json`,
14 of 24 under `currency.orm.json`). This is what spec §6 scoped, so it is
not a spec breach, but the title "The expense rules" and "a mandatory role
(every expense states its currency)" read as the full rule set, and
`test_hand_written_rules_agree_with_gnd` collects **every** non-pass GND
verdict, so it is green only because no corpus population trips an omitted
constraint.

Reproductions (script silent, GND fails, exit codes differ 0 vs 1):

```
e7 approved + team-lead chain, no amount:   GND required_expense_has_amount fail [104];     SCRIPT exit=0
e4 id 105 only in expense_has_currency:     GND required_expense_{submitted,has_amount,in_category} fail [105]; SCRIPT exit=0
b3 recommended book with no genre:          GND book_has_genre#1 fail ["cosmos"], book_has_genre#0 fail (two genres for map); SCRIPT exit=0
```

Severity: low. Class: completeness/honesty (PL-R4, PL-R6). One sentence in
each docstring ("the business rules; the inline uniqueness and the other
mandatory constraints are not reproduced here") and the same on the PL5 page.

### F5. Value-rule witness multiplicity differs and the test cannot see it — `tests/test_rules_in_pyrel.py:38,58`

GND lists one value witness per offending fact; PyRel `select(c)` is
set-valued. Both sides are normalised into Python sets, so the test passes
while the printed outputs differ.

Reproduction (`e3-unknown-category.json`): script prints one line
`known_categories  violated  "gifts"`; GND `offending_facts` = `["gifts", "gifts"]`.

Severity: low. Class: hardening. D2 already rules "one line per value"; say
"per distinct value" in the spec or expected output, or compare multisets.

### F6. Test normalisation notes — `tests/test_rules_in_pyrel.py:67-70`

- Line 68 `witness = [witness[0]] if len(witness) == 1 else witness` is an
  identity for every list (for length 1, `[w[0]] == w`); the comment claims
  it reshapes subset tuples. Harmless, misleading.
- Line 70 wraps scalar witnesses by **rule-name prefix** `required_`, not by
  constraint type. Bookrec's unnamed mandatory is addressed as
  `book_has_genre#1`, so it would not be wrapped; irrelevant today only
  because the scripts do not cover it (F4).
- Line 37 `assert run.stderr == '' or 'Warning' in run.stderr`: a traceback
  containing the word "Warning" anywhere would pass. Normal runs have empty
  stderr (verified), so the loophole is currently unused.
- Could normalisation make a wrong script pass? Only by multiplicity/order
  (F5). A script printing a bare `104` for a mandatory witness, string
  amounts, or a missing `$g` is caught.

### F7. Error exits collide with the "violated" code — both scripts

Malformed JSON, missing `facts`, over-cap input, and non-string/non-integer
values all leave the process with exit 1, the same code as an alethic
violation; the spec accepts "raises" for a tutorial tool, but exit 1 also
means "violated" on the same page.

Reproduction:

```
x1 '{"facts": ['            exit=1  json.decoder.JSONDecodeError: Expecting value: line 1 column 12
x2 no "facts" key           exit=1  KeyError: 'facts'
x3 1 MiB + 1 byte           exit=1  <path>: population larger than 1048576 bytes   (clean message; cap enforced on read)
x4 amount "60" (string)     exit=1  [TyperError] Type errors detected during type inference
b4 bookrec int values       exit=1  [TyperError] ...                                (GND: exit 3, input rejected)
```

Severity: low. Class: hardening. `raise SystemExit(f'...')` yields 1; use
`return 2`/`3` paths or document that a traceback is not a verdict.

### F8. Minor observations (no action required)

- Plan §2 says "prints one line per rule"; the scripts print one line per
  witness. Spec D2 rules this explicitly; the plan wording is stale.
- `e10`: currency facts present under `model.orm.json` with `covers` lacking
  `expense_has_currency` → script silently ignores them (exit 0); GND exit 3
  (unknown fact type). Expected for a tutorial tool.
- Side effects: a run with `HOME` and cwd pointed at empty scratch dirs
  created no files in either; `RAI_BUILD_DIR` is confined to the temp dir.
- Determinism: rows sorted, `sort_keys=True`, rule order fixed by `RULES`;
  repeated runs identical.
- Honesty of the negation description: the docstrings' "antecedent atoms are
  matched, the consequent is negated" matches `ApplicationOracle.guarded`
  (`pyrel_runtime.py:1550-1609`: atom → `not_`, absence → positive atom,
  comparison → `_NEGATED_OP` with a literal relation). The scripts use a
  direct literal comparison instead of a literal relation, as the spec
  measured PyRel 1.30.1 to accept; same rows.
- `tests/test_rf7_structure.py::test_complete_routing_and_dirty_controls`
  FAILS at HEAD on `src/gnd/population_shape.py` (`json.loads` outside the
  allowlist; file committed 35af996, unchanged). Pre-existing, not caused by
  PL2's allowlist lines; out of scope here but the §8 row "allowlist: pass"
  is not currently true on this branch.

## Requested changes before approve

1. F1: guard the mandatory rule on a non-empty `expense_has_currency` list and
   add the empty-currency population to the corpus (decide the exit code for
   vacuity in the spec while doing so, F3).
2. F3/F4: one sentence per docstring on vacuity and on the constraints not
   reproduced; carry the same wording to the PL5 page.
3. Optional hardening: F2 roster, F5 "per distinct value", F6 comment fix, F7
   non-1 error exits.
