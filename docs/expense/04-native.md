# 4. Reuse the native path for reporting and approvals

Expense 102 costs 800 EUR. Its travel category permits 2000 EUR, but a team-lead
approval permits only 100 EUR. A plausible total and a successful query cannot
make that approval legal. This chapter reuses BookRec's compiler, independent
policy audit and publication machinery, adding expense-specific native queries.
Continue after chapter 3; start from fresh installed resources below.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Expense reporting and approval flow">
![Three submitted expenses total 2260 EUR and one is approved. Reporting calculations and approval proposals enter a separate policy check; only accepted results are presented or published.](../assets/applications/expense-flow.svg)
</div>

*Source: shipped seed facts and native baseline/team-lead checkpoints.
The baseline is submitted 3, approved 1, total 2260 EUR. Numbers and policy verdicts
are separate outputs; failed CLI reports withhold business arithmetic.*

On narrow screens, focus a diagram and scroll horizontally with arrow keys or touch.

## A small extension on the same machinery

The shipped `native_query.py` computes native counts, sums, currency groups and
membership observations. The existing CLI supplies approval/chain claims; the
shared parent preserves all other source facts and checks exact candidate bytes.
Expense does not need a second policy compiler or publication implementation.
Category caps and approval ceilings remain in its model. For a new app, write
the domain queries and workflow against this reusable seam, then demonstrate
successful and deliberately invalid candidates.

Use separate interpreters as in [BookRec's native chapter](../bookrec/07-native.md)
and the [pinned runtime setup](../runtimes/pyrel.md). Set
`GND_TUTORIAL_PYREL_PYTHON` to the absolute native interpreter; the runner sets
`GND_TUTORIAL_GND_PYTHON` from its explicit base `--python`. Select the expense
group with `--lane pyrel --receipt expense-steps.json`. Offline runs label native
steps skipped. Timings measure supplied command execution on your machine,
excluding human design/authoring, installation and review; they are not a
promise of developer build duration.

For individual copy-and-run blocks, set both interpreter variables yourself:

```sh
export GND_TUTORIAL_GND_PYTHON=/absolute/base/bin/python
export GND_TUTORIAL_PYREL_PYTHON=/absolute/pinned/native/bin/python
```

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from pathlib import Path
import shutil
source = files("gnd").joinpath("examples", "expense")
shutil.copytree(str(source), "expense-native")
home = Path("expense-native")
(home/"cli").mkdir()
(home/"cli/__init__.py").write_text("")
for origin, target in [("extension.py","expense_cli.py"), ("reporting.py","reporting.py"), ("native_query.py","native_query.py")]:
    shutil.copy2(home/origin, home/"cli"/target)
```

## Report, reject a chain, then repair it

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Expense category caps and approval chain limits">
![Meal 101 costs 60 EUR, below category 75 and team-lead 100. Travel 102 costs 800, within category 2000 but beyond team-lead 100, violating approval_limit_team_lead. Finance 3000 accepts 102.](../assets/applications/expense-limits.svg)
</div>

*Source: shipped category caps and native team-lead/chain-limit/finance
checkpoints. Every amount and ceiling is EUR. A finance approval cannot waive
a category cap: the separate meal 90 fixture violates `policy_meals`.*

<!-- gnd-run expect=0 lane=pyrel -->
```python
import hashlib, json, os, subprocess
from pathlib import Path
home = Path("expense-native").resolve()
base, native = os.environ["GND_TUTORIAL_GND_PYTHON"], os.environ["GND_TUTORIAL_PYREL_PYTHON"]
source = home/"seed.population.json"
before = hashlib.sha256(source.read_bytes()).hexdigest()
def launch(command, expected=0, *extra, model="model.orm.json", population="seed.population.json"):
    argv = [base,"-m","cli.expense_cli",command,"--model",model,"--population",population,
            "--backend","pyrel","--pyrel-python",native,*extra]
    run = subprocess.run(argv,cwd=home,capture_output=True,text=True,timeout=150)
    assert run.returncode == expected, run.stdout + run.stderr
    return json.loads(run.stdout)
report = launch("report")
assert report["report"] == {"submitted":3,"approved":1,"total_eur":2260}
assert report["accepted"] and not report["published"]
bad = launch("approve",1,"--expense","102","--chain","team-lead","--output","bad.json")
rule = next(r for r in bad["policy"]["verdicts"] if r["id"] == "approval_limit_team_lead")
assert rule["status"] == "violated" and rule["witnesses"] == [{"$e":102,"$a":800}]
assert not (home/"bad.json").exists()
for expense, chain, output in [(101,"team-lead","team-lead.json"),(102,"finance","finance.json")]:
    accepted = launch("approve",0,"--expense",str(expense),"--chain",chain,"--output",output)
    assert accepted["accepted"] and accepted["published"] and "calculation" not in accepted
    after = launch("report",population=output)
    assert after["report"] == {"submitted":3,"approved":2,"total_eur":2260}
meal = launch("report",1,population="invalid-meal.population.json")
assert next(r for r in meal["policy"]["verdicts"] if r["id"]=="policy_meals")["status"] == "violated"
assert "report" not in meal
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
print("3 submitted,1 approved,2260 EUR; chain rejected; two independent repairs accepted.")
```

These are fresh static snapshots. A checked approval does not establish the
operator's identity, transition permission, a concurrent ledger or reimbursement.
The input remains unchanged and every approval output uses a fresh path.

## The same reporting query meets a currency requirement

Chapter 3's evolution machinery adds explicit currency facts and mandatory
policy. Here we exercise the shipped before/after models with the native path.
The missing fixture assigns EUR only to 103; 101/102 remain missing. Adding
explicit EUR to all three repairs the population without conversion.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Expense implicit and explicit currency evolution">
![Implicit EUR gives 2260. The evolved model requires expense_has_currency and allows only EUR. Missing 101/102 currency violates required_expense_has_currency; supplying EUR for all three yields labeled EUR 2260. No conversion is performed.](../assets/applications/expense-currency.svg)
</div>

*Source: shipped currency model plus missing/explicit native checkpoints.
`required_expense_has_currency` witnesses 101/102, followed by an accepted
`totals_by_currency` report. USD also has a separately labeled EUR-only
application refusal; changing the model enum alone does not implement conversion.*

<!-- gnd-run expect=0 lane=pyrel -->
```python
import json, os, subprocess
from pathlib import Path
home = Path("expense-native").resolve()
base, native = os.environ["GND_TUTORIAL_GND_PYTHON"], os.environ["GND_TUTORIAL_PYREL_PYTHON"]
for population, expected in [("currency-missing.population.json",1),("currency.population.json",0)]:
    run = subprocess.run([base,"-m","cli.expense_cli","report","--model","currency.orm.json",
        "--population",population,"--backend","pyrel","--pyrel-python",native],cwd=home,capture_output=True,text=True,timeout=150)
    assert run.returncode == expected, run.stdout + run.stderr
    result = json.loads(run.stdout)
    if expected:
        missing = next(r for r in result["policy"]["verdicts"] if r["id"]=="required_expense_has_currency")
        assert missing["status"] == "violated" and missing["witnesses"] == [[101],[102]]
        assert "report" not in result
    else:
        assert result["report"] == {"submitted":3,"approved":1,"totals_by_currency":{"EUR":2260}}
        assert result["accepted"] and not result["published"]
    print(population, result["policy"]["status"])
usd = json.loads((home/"currency.population.json").read_text())
usd["facts"]["expense_has_currency"][0]["currency"] = "USD"
(home/"usd.json").write_text(json.dumps(usd))
run = subprocess.run([base,"-m","cli.expense_cli","report","--model","currency.orm.json","--population","usd.json","--backend","pyrel","--pyrel-python",native],cwd=home,capture_output=True,text=True,timeout=150)
assert run.returncode == 1, run.stdout + run.stderr
guard = json.loads(run.stdout)
assert guard["application_refusal"]["kind"] == "unsupported-currency" and guard["policy"] is None
assert "report" not in guard
```

## Change one policy without rewriting the query

For this synthetic variant, the exercise owner lowers the meal cap from 75 to 50
EUR. Change only the copied model and its provenance, then rerun the same query
and CLI. The old 60 EUR meal must fail; repairing it to 45 EUR gives 2245 EUR total.
This is a local tutorial variant, separate from the baseline 75 EUR diagrams and
chapter 3's managed evolution workflow. No shared or installed model is edited.

<!-- gnd-run expect=0 lane=pyrel -->
```python
import json, os, subprocess
from pathlib import Path
home = Path("expense-native").resolve()
model = json.loads((home/"model.orm.json").read_text())
rule = next(c for c in model["constraints"] if c["id"]=="policy_meals")
rule["consequent"]["comparison"]["right"] = 50
rule["provenance"]["user_quote"] = "For this synthetic tutorial variant, meals cost at most 50 EUR."
(home/"lower-cap.orm.json").write_text(json.dumps(model))
repair = json.loads((home/"seed.population.json").read_text())
next(r for r in repair["facts"]["expense_has_amount"] if r["expense"]==101)["amount"] = 45
(home/"lower-meal.json").write_text(json.dumps(repair))
for population, expected in [("seed.population.json",1),("lower-meal.json",0)]:
    run = subprocess.run([os.environ["GND_TUTORIAL_GND_PYTHON"],"-m","cli.expense_cli","report",
        "--model","lower-cap.orm.json","--population",population,"--backend","pyrel",
        "--pyrel-python",os.environ["GND_TUTORIAL_PYREL_PYTHON"]],cwd=home,capture_output=True,text=True,timeout=150)
    assert run.returncode == expected, run.stdout + run.stderr
    result = json.loads(run.stdout)
    if expected:
        assert next(v for v in result["policy"]["verdicts"] if v["id"]=="policy_meals")["status"]=="violated"
        assert "report" not in result
    else:
        assert result["report"]=={"submitted":3,"approved":1,"total_eur":2245}
    print("50 EUR cap",population,result["policy"]["status"])
```

## Troubleshoot without weakening the policy

A missing/wrong interpreter fails native preflight; use PyRel 1.30.1/DuckDB 1.5.5
in the separate pinned environment. Copy `native_query.py` beside
`cli/expense_cli.py`. Unknown coverage must stay unknown; include the asserted
relation coverage metadata even when an observed relation is empty. A fully
empty currency relation retains the bounded profile's incomplete exit 2; partial
omissions have mandatory witnesses. Zero approvals/empty inputs can yield
mathematical zero calculation while policy evidence remains incomplete. Neither
case is an accepted CLI report. Exit 3 means malformed input and exit 70 an
operational failure; no refused run publishes.

Native aggregates preserve expense identity, so equal amounts on distinct
expenses are counted separately. Native membership results are checked by Python
orchestration for unknown/already-approved guards; model caps/enums/mandatory
rules are checked by the separate exported policy walk. Read the copied
`native_query.py` and `extension.py` to see those responsibilities in actual
shipped code. The six tutorial SVGs and their source/checkpoint manifests ship
with the installed examples, so this learning path needs no repository checkout.

??? note "Read the shipped native query source"

    ```python
    --8<-- "docs/assets/applications/expense-native-query.txt"
    ```
