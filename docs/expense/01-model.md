# 1. Model an expense approval policy

An expense report looks like a list of numbers until somebody asks, “Who can
approve this one?” In this tutorial you will build a small Python application
that can answer that question using a model checked by GND. By the end you will
have a reporting CLI, an approval command that withholds invalid output, and a
reviewed change introducing an explicit currency requirement.

This is a fictional policy with synthetic data. The application is useful as an
integration pattern; it does not connect to a bank, employee directory or
expense system. All commands run locally without a model-provider account.

## The requirements

Our fictional team submits expenses in whole EUR. Each expense has exactly one
submitter, amount and category. An approval must refer to a submitted expense
and name exactly one known approval chain.

| Category | Maximum amount |
|---|---:|
| Meals | 75 EUR |
| Training | 1,500 EUR |
| Travel | 2,000 EUR |
| Equipment | 3,000 EUR |

The **team-lead** chain can approve up to 100 EUR. The **finance** chain can
approve up to 3,000 EUR. Both the category cap and chain limit must hold. A
finance approval cannot turn a 90 EUR meal into a compliant expense.

The word *chain* here names an approval route. We do not model multi-step
signatures or identify the real person issuing a command. Those would need
additional facts, authentication and operation rules.

## Get the complete inputs

Use the Python environment from [installation guide](../installation.md),
with `python` and `gnd` on its PATH. Work in a new empty directory. Keep the same
working directory through all three chapters; later commands refer to
`expense-demo/` and `expense-project/` explicitly.

Copy the resources from the installed package:

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from pathlib import Path

source = files("gnd").joinpath("examples", "expense")
destination = Path("expense-demo")
destination.mkdir()
for resource in source.iterdir():
    if resource.is_file() and resource.name != "__init__.py":
        (destination / resource.name).write_bytes(resource.read_bytes())
print("Copied the complete synthetic expense example to expense-demo/")
```

Read `expense-demo/README.md` for checkpoint provenance and the full resource
inventory. `model.orm.json` is JSON, which GND accepts as a YAML representation;
using JSON here makes the copy-and-inspect Python snippets simple.

The seed includes three expenses:

| Expense | Employee | Category | Amount | Current approval |
|---|---|---|---:|---|
| 101 | Ari | Meals | 60 EUR | Pending |
| 102 | Bea | Travel | 800 EUR | Pending |
| 103 | Ari | Equipment | 1,400 EUR | Finance |

The existing approval gives us a nonempty approval relation to check. A constraint
with no relevant facts may report **vacuous**, which does not count as a clean
acceptance. We revisit coverage when adding currency in chapter 3.

## Read the model as facts and rules

The `Expense` entity is identified by an integer `ExpenseId`. Its submitter,
amount and category are distinct fact types, rather than columns whose meaning
is implicit in application code:

```text
Expense is submitted by Employee
Expense has Amount
Expense is in Category
Expense is approved
Expense is approved by Chain
```

The model has mandatory roles for the three input facts and uniqueness
constraints to prevent, for example, two amounts for the same expense. Subset
constraints connect the approval facts to submissions and require the approval
marker and chain assignment to agree.

A guarded constraint binds the expense and amount from facts, then compares the
amount to the category limit. This abbreviated excerpt is taken from the full
model:

```yaml
id: policy_meals
type: guarded
antecedent:
  - fact_type: expense_in_category
    bind: {expense: "$e", category: meals}
  - fact_type: expense_has_amount
    bind: {expense: "$e", amount: "$a"}
consequent:
  comparison: {operator: "<=", left: "$a", right: 75}
```

The complete constraint also records source, confirmation, modality and the
requirement it implements. These are **alethic** rules: violations block
acceptance. The synthetic brief confirms them explicitly. The
[capability reference](../reference/capabilities.md) explains the difference
between blocking rules and deontic advice.

## Validate the model, then check data

Model validation and population checking answer different questions. Validation
checks that the model is well formed; checking asks whether these facts agree
with that valid model.

<!-- gnd-run expect=0 -->
```sh
gnd validate expense-demo/model.orm.json
```

<!-- gnd-run expect=0 -->
```sh
gnd check expense-demo/model.orm.json expense-demo/seed.population.json
```

Now check a meal above the cap. This command deliberately exits `1`:

<!-- gnd-run expect=1 -->
```sh
gnd check expense-demo/model.orm.json expense-demo/invalid-meal.population.json
```

Inspect the exact violation through the stable Python API. We opt into raw values
only because these are known synthetic teaching inputs:

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd.api import check

model = Path("expense-demo/model.orm.json")
report = check(model, "expense-demo/invalid-meal.population.json", unredacted=True)
assert report["exit_code"] == 1
failed = [row for row in report["verdicts"] if row["verdict"] == "fail"]
assert len(failed) == 1
assert failed[0]["offending_facts"] == [{"$e": 101, "$a": 90}]
print("Blocked: expense 101 has a 90 EUR meal; the limit is 75 EUR.")

repaired = json.loads(Path("expense-demo/invalid-meal.population.json").read_text())
repaired["facts"]["expense_has_amount"][0]["amount"] = 60
Path("expense-demo/repaired-meal.population.json").write_text(json.dumps(repaired))
assert check(model, "expense-demo/repaired-meal.population.json")["exit_code"] == 0
print("Repaired amount: 60 EUR; all modeled checks pass.")
```

The rule is evaluated by GND. The Python snippet changes the input to demonstrate
a repair; it does not reproduce the policy evaluator.

## Agent handoff and exercise

The checkpoints above require no agent. If you want an agent to author an
alternative model, explicitly select **gnd-model-from-text** and supply this
prompt:

> Build a model for the fictional policy in expense-demo/README.md. Keep the
> category limits and chain limits as separately checkable rules. Record the
> brief's explicit requirements as provenance; identify assumptions for my
> review. Supply one conforming population, a 90 EUR meal and an 800 EUR
> team-lead approval. Stop after model validation and explain each constraint.

Review that result before selecting **gnd-codegen** in the next chapter; model
authoring does not silently start application generation.

**Exercise:** Add a training expense for exactly 1,500 EUR, then one for 1,501 EUR.
Check both populations. At the boundary, finance can approve the first; the
second must fail the category rule even with finance approval. Also try removing
its amount fact and explain which requirement becomes unsatisfied.

Next: [build and run the approval application](02-application.md).
