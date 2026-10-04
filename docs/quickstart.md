# Check and repair a shipping request

A warehouse must dispatch a request before its deadline. The supplied request
claims a three-day route window that exceeds that deadline. You will identify
the violated rule, examine a repair and run the check again.

[Install GND](installation.md), activate its environment and start in an empty
working directory. All inputs below ship in the package. After installation,
this exercise needs no API key, network or native compiler.

## Get the model and facts

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from shutil import copytree
copytree(str(files("gnd") / "examples" / "dispatch"), "dispatch-demo")
```

The folder contains a model, two populations and a fixed reference catalogue.
The model specifies the rule; the populations describe requests; the catalogue
supplies reference route facts. Start by checking the model:

<!-- gnd-run expect=0 -->
```sh
gnd validate dispatch-demo/model.orm.json --format json
```

Exit **0** means the model validates. Now check the first population:

<!-- gnd-run expect=1 -->
```sh
gnd check dispatch-demo/model.orm.json dispatch-demo/seed.pop.json --admission --format json
```

This command intentionally exits **1**. In `report.verdicts`, the failed entry
has `constraint_ref: constraints[1]`, the model's `dispatch_deadline` rule.
The report is explaining a semantic violation, rather than a parsing failure.
A script should expect this exit for this example; do not hide it with `|| true`.

## Inspect the difference and apply the supplied repair

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
root = Path("dispatch-demo")
before = json.loads((root / "seed.pop.json").read_text())
after = json.loads((root / "repaired.pop.json").read_text())
for fact, rows in before["facts"].items():
    if rows != after["facts"].get(fact):
        print(fact, "before:", rows, "after:", after["facts"].get(fact))
assert before != after
```

The repair changes the declared request facts; it does not change the policy or
rewrite the fixed catalogue. Check it against the same model:

<!-- gnd-run expect=0 -->
```sh
gnd check dispatch-demo/model.orm.json dispatch-demo/repaired.pop.json --admission --format json
```

Exit **0** means this supplied repaired population passes. Removing or modifying
the required reference data instead would refuse the check with exit **3**;
that would not be a repair.

## Put the check in Python

<!-- gnd-run expect=0 -->
```python
from gnd import api
bad = api.check("dispatch-demo/model.orm.json", "dispatch-demo/seed.pop.json", admission=True)
good = api.check("dispatch-demo/model.orm.json", "dispatch-demo/repaired.pop.json", admission=True)
assert bad["exit_code"] == 1 and good["exit_code"] == 0
failed = [v for v in bad["report"]["verdicts"] if v["verdict"] == "fail"]
assert len(failed) == 1 and failed[0]["constraint_ref"] == "constraints[1]"
print(failed[0]["constraint_ref"], failed[0]["message"])
```

Your application can use this result before publishing proposed facts. GND
checks the model you supplied; deciding whether a proposed repair is the right
real-world action remains part of your application workflow.

**Exercise:** inspect the deadline rule and the two population files. Explain
why changing the facts passes while removing the catalogue refuses. Then
[build BookRec](bookrec/01-model.md) to create an application that produces its
own candidate facts, or [try release readiness](release-example.md) in another domain.
