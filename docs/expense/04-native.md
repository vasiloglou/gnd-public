# 4. Run expense approvals on PyRel and catch a bad approval

Expense 102 costs 800 EUR. A team lead may approve at most 100 EUR, so a team-lead
approval of 102 must be refused, however plausible it looks. In this chapter a
PyRel query produces the report and stages the approval, and GND checks the
result before anything is saved. You need the two environments from
[PyRel + GND](../pyrel-apps.md#set-up).

## 1. What you'll build

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Expense reporting and approval flow">
![Three submitted expenses total 2260 EUR and one is approved. Reporting calculations and approval proposals enter a separate policy check; only accepted results are presented or published.](../assets/applications/expense-flow.svg)
</div>

*Source: shipped seed facts and native baseline/team-lead checkpoints.
Numbers and policy verdicts are separate outputs; a refused report shows no totals.*

On narrow screens, focus a diagram and scroll horizontally with arrow keys or touch.

| Step | Who does it | Where it lives |
|---|---|---|
| Propose an approval | The candidate producer: here your `--chain` choice, in your app possibly an LLM agent | the command line |
| Count and total expenses | PyRel | `native_query.py` |
| Refuse unknown or already-approved expenses | Plain Python, using PyRel's results | `native_query.py` |
| Check limits and caps, then save | GND, using PyRel to run the check | the model file |

The applications here run on PyRel 1.30.1 with DuckDB 1.5.5, locally, with no
account. A passing check means the supplied facts satisfy the modeled rules; it
does not prove who approved anything or that money moved.

## 2. Build a fresh project and check both environments

Work in the folder where you created the two environments. Run Python blocks
with `python`, which is the GND interpreter after Set up: save one as a file,
for example `step.py`, and run `python step.py`.

Chapter 3 changed `expense-project` to the currency model, so repeat chapter 2's
setup under fresh names. Copy the shipped example:

<!-- gnd-run expect=0 output=stdout -->
```python
from importlib.resources import files
import shutil

shutil.copytree(str(files("gnd").joinpath("examples", "expense")), "expense-native-demo")
print("Copied the expense example to expense-native-demo/")
```

```text
Copied the expense example to expense-native-demo/
```

Generate the project, exactly as in chapter 2:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd codegen expense-native-demo/model.orm.json --out expense-native
```

```text
generated project for expense-native-demo/model.orm.json -> expense-native
...
```

The shipped `project/` folder holds the developer-owned half: the CLI, the
reporting module, the PyRel query, the architecture contract, and copies of the
model and seed facts. Copy it over the generated project in one step:

<!-- gnd-run expect=0 output=stdout -->
```python
import shutil

shutil.copytree("expense-native-demo/project", "expense-native", dirs_exist_ok=True)
print("Installed the expense app and its PyRel query in expense-native/")
```

```text
Installed the expense app and its PyRel query in expense-native/
```

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c "import gnd; print('GND is ready')"
```

```text
GND is ready
```

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
"$GND_PYREL_PYTHON" -c "from importlib.metadata import version as v; print('PyRel', v('relationalai'), 'with DuckDB', v('duckdb'))"
```

```text
PyRel 1.30.1 with DuckDB 1.5.5
```

## 3. One rule, and the query that does not enforce it

The model's `approval_limit_team_lead` rule says: a team-lead approval covers at
most 100 EUR. Now look at the PyRel query. It only counts and adds up:

```python
# Count and sum submitted expenses natively.
claims = m.where(app.match('expense_submitted_by_employee', expense=e),
                 app.match('expense_has_amount', expense=e, amount=a))
totals = app.rows(claims.select(aggregates.count(m.distinct(e)), aggregates.sum(e, a)))
```

`m` is an ordinary PyRel model. `e` and `a` are query variables for an expense and
its amount, made with `app.ref`, and `aggregates` is PyRel's own module of
`count` and `sum`. `app` is the [query toolkit](../pyrel-apps.md#the-query-toolkit)
GND hands your query. No query here enforces the limit, and none needs to: the rule
lives in the model, and GND's check enforces it on whatever is proposed. That is
what lets you change a limit without rewriting code.

## 4. Run the report

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native/model.orm.json --population expense-native/seed.population.json --backend pyrel
```

```text
Report: 3 submitted, 1 approved, 2260 EUR total
Policy check: ACCEPTED
```

The report is shown only because the facts passed the check.

## 5. A bad approval

Play the agent: propose that a team lead approves expense 102.

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python expense-native/app.py approve --expense 102 --chain team-lead \
  --output team-lead-102.json --model expense-native/model.orm.json --population expense-native/seed.population.json --backend pyrel
```

```text
Proposed approval: expense 102 by team-lead
Policy check: REJECTED
  violated    approval_limit_team_lead {"$a": 800, "$e": 102}
Nothing was published.
```

The line under the verdict is a witness (the exact facts that break the rule):
`$e` is the expense, 102, and `$a` its amount, 800. The query staged the approval
as asked; the check refused it.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Expense category caps and approval chain limits">
![Meal 101 costs 60 EUR, below category 75 and team-lead 100. Travel 102 costs 800, within category 2000 but beyond team-lead 100, violating approval_limit_team_lead. Finance 3000 accepts 102.](../assets/applications/expense-limits.svg)
</div>

*Source: shipped category caps and native team-lead/chain-limit/finance
checkpoints. Every amount and ceiling is EUR.*

## 6. Fix it and rerun

Finance may approve up to 3000 EUR:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python expense-native/app.py approve --expense 102 --chain finance \
  --output finance-102.json --model expense-native/model.orm.json --population expense-native/seed.population.json --backend pyrel
```

```text
Proposed approval: expense 102 by finance
Policy check: ACCEPTED
Published: finance-102.json
```

The saved file is a new snapshot; `seed.population.json` is unchanged. Report on it:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native/model.orm.json --population finance-102.json --backend pyrel
```

```text
Report: 3 submitted, 2 approved, 2260 EUR total
Policy check: ACCEPTED
```

Category caps are checked too, separately from approvals. The shipped example
`invalid-meal.population.json` records a 90 EUR meal against the 75 EUR meal cap:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native/model.orm.json --population expense-native-demo/invalid-meal.population.json --backend pyrel
```

```text
Policy check: REJECTED
  violated    policy_meals {"$a": 90, "$e": 101}
Nothing was published.
```

## 7. Change a rule without touching the query

Suppose the meal cap drops from 75 to 50 EUR. In the model file, the rule
`policy_meals` stores its cap under `consequent` → `comparison` → `right`. Change
it in a private copy. For a shared model, make the change through `gnd evolve`,
as in [chapter 3](03-evolution.md); here we keep the focus on the query:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

model = json.loads(Path("expense-native/model.orm.json").read_text())
rule = next(r for r in model["constraints"] if r["id"] == "policy_meals")
old = rule["consequent"]["comparison"]["right"]
rule["consequent"]["comparison"]["right"] = 50
Path("expense-native/lower-cap.orm.json").write_text(json.dumps(model, indent=2))
print(f"policy_meals now allows meals up to 50 EUR (was {old})")
```

```text
policy_meals now allows meals up to 50 EUR (was 75)
```

The same query and the same facts now fail on the 60 EUR meal:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native/lower-cap.orm.json --population expense-native/seed.population.json --backend pyrel
```

```text
Policy check: REJECTED
  violated    policy_meals {"$a": 60, "$e": 101}
Nothing was published.
```

The query finished and computed totals, but no report is shown: a query that
finishes is not the same as a passing check.

### The currency rule from chapter 3

The currency model requires every expense to state its currency. With currency
missing on 101 and 102, the check names both:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native-demo/currency.orm.json \
  --population expense-native-demo/currency-missing.population.json --backend pyrel
```

```text
Policy check: REJECTED
  violated    required_expense_has_currency [101]
  violated    required_expense_has_currency [102]
Nothing was published.
```

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native-demo/currency.orm.json \
  --population expense-native-demo/currency.population.json --backend pyrel
```

```text
Report: 3 submitted, 1 approved, 2260 EUR total
Policy check: ACCEPTED
```

A USD expense is refused by the app itself, before any check, because this app
does not convert currencies:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native-demo/currency.orm.json \
  --population expense-native-demo/tutorial-assets/checkpoints/usd.input.json --backend pyrel
```

```text
Policy check: REFUSED by the application (only explicit EUR is supported; no currency conversion)
Nothing was published.
```

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Expense implicit and explicit currency evolution">
![Implicit EUR gives 2260. The evolved model requires expense_has_currency and allows only EUR. Missing 101/102 currency violates required_expense_has_currency; supplying EUR for all three yields labeled EUR 2260. No conversion is performed.](../assets/applications/expense-currency.svg)
</div>

*Source: shipped currency model plus missing/explicit native checkpoints. No
currency conversion is implemented.*

## 8. Recap

The producer proposed, PyRel counted and summed, and GND checked before saving.
Limits and caps stayed in the model, so changing one needed no query change.
A warning, a refusal and an unknown fact list are all different outcomes, and
only an accepted check shows a report or saves a file.

## Troubleshooting

The exit code is the number `echo $?` prints right after a command. An input's
coverage list (`covers`) names the fact lists the input vouches for; a list it
does not name is unknown, which is different from a list that is declared but empty.

| What you see | Why | What to do |
|---|---|---|
| `--backend pyrel needs the PyRel interpreter` | `GND_PYREL_PYTHON` is not exported in this shell | Export it again as in [Set up](../pyrel-apps.md#set-up), or pass `--pyrel-python` |
| `NOT RUN` mentioning the interpreter or `requires PyRel 1.30.1` | Wrong environment | Rebuild it as in [Set up](../pyrel-apps.md#set-up) |
| `NOT ACCEPTED (some rules could not be decided)`, exit code 2 | A rule needs a fact list the input does not cover | Cover that list, or leave it out on purpose and accept the refusal |
| `NOT RUN (...)`, exit code 3 | The input is malformed, or an approval changed facts it does not own | Fix the file and rerun |
| `NOT RUN (output already exists)` | Outputs are never overwritten | Choose a new `--output` path |
| `FileExistsError` at the copy step | You ran the chapter before in this folder | Start again in a new empty folder |
| `gnd: command not found` | `gnd-env/bin` is not on your `PATH` | Add it, or type `gnd-env/bin/gnd` |

## Next steps

- Write rules for your own domain with
  [gnd-model-from-text](../agents/model-from-text.md), then build the same kind of app.
- Drive a real LLM agent against the same model and checker. That is a separate
  session contract you write for [`gnd exp run`](../agents/dev-session.md); it
  does not run this CLI.
- Running against Snowflake is outside this tutorial and outside the
  applications runtime, which refuses non-local connections.

A checked approval does not establish who the approver is or that they may act.

## The whole query

??? note "Read the shipped native query source"

    ```python
    --8<-- "docs/assets/applications/expense-native-query.txt"
    ```
