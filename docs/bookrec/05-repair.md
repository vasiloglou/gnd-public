# 5. Use feedback to repair the right thing

A failure can mean the candidate facts are wrong, the authored algorithm is
wrong, or generated files have drifted. Those call for different repairs. This
chapter starts with an illegal recommendation and follows the report back to
one concrete fact, then demonstrates a separate conformance failure.

Continue after [chapter 4](04-application.md). Keep the original model unchanged
throughout this chapter so a passing result comes from repairing the candidate.

## Reproduce a rejected publication

A faulty producer proposes `night` for Ada. We already know which business rule
this violates. Send those same facts through the application's publication
boundary, rather than running only an isolated checker command.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("bookrec-project").resolve()))
from bookrec.cli import publish

candidate = json.loads(Path("bookrec-demo/adult-for-minor.population.json").read_text())
status = publish("bookrec-project/model.orm.yaml", candidate,
                 "bookrec-project/rejected.json")
assert status == 1
assert not Path("bookrec-project/rejected.json").exists()
assert not list(Path("bookrec-project").glob(".bookrec-*.json"))
print("The illegal candidate never became the published result.")
```

Expected: a checker failure for the age rule; no final output; no leftover
temporary candidate. The source catalogue and model are still available for
inspection. Changing Ada's minor flag to evade the check would change the
problem rather than fix the recommendation.

## Read and repair the binding

<!-- gnd-run expect=0 -->
```python
from gnd import api

report = api.check("bookrec-project/model.orm.yaml",
                   "bookrec-demo/adult-for-minor.population.json", unredacted=True)
failure = next(row for row in report["verdicts"] if row["verdict"] == "fail")
assert failure["constraint_ref"] == "constraints[1]"
assert failure["offending_facts"][0]["$u"] == "ada"
assert failure["offending_facts"][0]["$b"] == "night"
print(failure["message"])
```

The guarded rule's binding names exactly the reader and book involved. Here a
bounded repair replaces Ada's forbidden book with `map`; it does not edit the
rule, age flag, preferences, or other reader's recommendation.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
import sys
from gnd import api

sys.path.insert(0, str(Path("bookrec-project").resolve()))
from bookrec.cli import publish

candidate = json.loads(Path("bookrec-demo/adult-for-minor.population.json").read_text())
candidate["facts"]["recommendation"][0]["book"] = "map"
assert publish("bookrec-project/model.orm.yaml", candidate,
               "bookrec-project/repaired.json") == 0
report = api.check("bookrec-project/model.orm.yaml", "bookrec-project/repaired.json")
assert report["acceptance_ready"] and report["counts"]["fail"] == 0
print("Repaired recommendation accepted under the unchanged rules.")
```

A live agent may propose this repair, but GND's check does not depend on trusting
the agent's explanation. The deterministic checkpoint lets you reproduce the
same sequence without a provider. For an agent-assisted attempt, explicitly
select `gnd-dev-session`:

> Set up a data-driven session to repair the rejected BookRec population.
> Make only the recommendation facts writable. Bind the unchanged model and
> catalogue, require checker acceptance and coverage floors, and retain every
> attempt. Do not claim closure merely because one attempt is accepted.

That is a new, optional session with its own contract and outcome. It should
not be described as having happened when you only ran this chapter's commands.

## Distinguish file drift from bad recommendations

Now change a *derived* file deliberately. Adding a comment leaves its Python
syntax valid, but breaks the generated file identity recorded by codegen.

<!-- gnd-run expect=0 -->
```python
from pathlib import Path

path = Path("bookrec-project/model/tools.py")
Path("bookrec-demo/tools.backup").write_bytes(path.read_bytes())
with path.open("a") as stream:
    stream.write("\n# Deliberate tutorial drift.\n")
```

<!-- gnd-run expect=13 -->
```sh
gnd conformance bookrec-project/model.orm.yaml bookrec-project --format json
```

Expected: exit 13 with a derived-file integrity finding. This report answers a
different question from “is Ada's recommendation legal?” Restore the exact
saved bytes, then re-check the project.

<!-- gnd-run expect=0 -->
```python
from pathlib import Path

Path("bookrec-project/model/tools.py").write_bytes(Path("bookrec-demo/tools.backup").read_bytes())
```

<!-- gnd-run expect=0 -->
```sh
gnd conformance bookrec-project/model.orm.yaml bookrec-project --format json
```

**Exercise:** Explain why adding a comment to the *authored* library is a
different event. Extension bytes are yours to develop; conformance only checks
the declared structural relationship and generated artifacts. Functional tests
and output checks remain necessary.

Next: [change the rule and require complete output](06-evolution.md).
