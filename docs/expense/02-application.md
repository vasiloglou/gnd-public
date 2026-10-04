# 2. Build an approval application

The model describes valid expense facts. Your application still needs to read
inputs, choose a proposed change, present a report and decide when to write an
output. Here we generate the model-facing project, install a small supplied
extension and exercise both acceptance and refusal.

Continue in the working directory from [chapter 1](01-model.md). No live agent
call is needed: the extension is included as a reviewed checkpoint.

## Generate the project and identify ownership

<!-- gnd-run expect=0 -->
```sh
gnd codegen expense-demo/model.orm.json --out expense-project
```

GND emits `model_orm/tools.py`, projection and verbalization artifacts, and a
skill describing how an agent can use the model. Its `.gnd-codegen.json` manifest
records the generated files and their digests.

| File group | Who changes it? | Purpose |
|---|---|---|
| `model_orm/`, `artifacts/`, generated `SKILL.md` | GND codegen | Model-derived function shapes and extraction resources |
| `cli/expense_cli.py`, `cli/reporting.py` | Application developer | Approval flow and reporting behavior |
| `architecture.contract.yaml` | Application developer | Declared extension modules, inputs, outputs and smoke cases |
| `references/`, `pyproject.toml` | Application developer | Domain notes and project dependencies |

Codegen supplies a model-facing scaffold, not a completed expense system. The
following checkpoint supplies the CLI and reporting logic, plus its architecture
declaration. Open the copied files to read the whole implementation:

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
import shutil

source = Path("expense-demo")
project = Path("expense-project")
(project / "cli").mkdir()
(project / "cli/__init__.py").write_text("")
for origin, target in [
    ("extension.py", "cli/expense_cli.py"),
    ("reporting.py", "cli/reporting.py"),
    ("architecture.contract.yaml", "architecture.contract.yaml"),
    ("model.orm.json", "model.orm.json"),
    ("seed.population.json", "seed.population.json"),
]:
    shutil.copy2(source / origin, project / target)
print("Installed the developer-owned approval and reporting extension.")
```

Check conformance before relying on the generated project:

<!-- gnd-run expect=0 -->
```sh
gnd conformance expense-demo/model.orm.json expense-project
```

Conformance checks generated-file integrity, currency with the model, structural
agreement and the declared architecture. A green result does not execute the
application or prove its behavior. The commands below test that behavior.

## Report the current state

<!-- gnd-run expect=0 -->
```sh
(cd expense-project && python -m cli.expense_cli report --model model.orm.json --population seed.population.json)
```

Expected application output:

```json
{"approved": 1, "submitted": 3, "total_eur": 2260}
```

Every report first calls `gnd.api.check`; an invalid population does not become a
plausible-looking total. This is an application decision to require a clean
check before producing a business result.

<!-- gnd-run expect=0 -->
```python
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "cli.expense_cli", "report", "--model", "model.orm.json",
     "--population", "seed.population.json"],
    cwd="expense-project", capture_output=True, text=True, check=True,
)
assert json.loads(result.stdout) == {"approved": 1, "submitted": 3, "total_eur": 2260}
```

## Propose, check, then publish an approval

Expense 101 is a 60 EUR meal. Both the meal cap and the team-lead limit permit
its approval:

<!-- gnd-run expect=0 -->
```sh
(cd expense-project && python -m cli.expense_cli approve --model model.orm.json --population seed.population.json --expense 101 --chain team-lead --output approved-101.json)
```

The application reads the input, builds a separate candidate, adds both approval
facts and writes that candidate temporarily. It calls `gnd.api.check` on those
exact bytes, then publishes them to the requested output only if the check
returns zero. The input checkpoint is preserved.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd.api import check

actual = json.loads(Path("expense-project/approved-101.json").read_text())
expected = json.loads(Path("expense-demo/approved.population.json").read_text())
assert actual == expected
assert check("expense-demo/model.orm.json", "expense-project/approved-101.json")["exit_code"] == 0
assert json.loads(Path("expense-project/seed.population.json").read_text())["facts"]["expense_is_approved"] == [{"expense": 103}]
print("101 approved; the original checkpoint still contains only approval 103.")
```

Now try to approve expense 102, an 800 EUR trip, through the team lead:

<!-- gnd-run expect=1 -->
```sh
(cd expense-project && python -m cli.expense_cli approve --model model.orm.json --population seed.population.json --expense 102 --chain team-lead --output blocked-102.json)
```

The CLI prints a refusal and the failed constraint reference. It does not publish
the candidate. The supplied invalid checkpoint lets you inspect the same bad
post-state independently of the application's control flow:

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
from gnd.api import check

assert not Path("expense-project/blocked-102.json").exists()
report = check("expense-demo/model.orm.json", "expense-demo/invalid-chain.population.json", unredacted=True)
assert report["exit_code"] == 1
failures = [row for row in report["verdicts"] if row["verdict"] == "fail"]
assert len(failures) == 1
assert failures[0]["offending_facts"] == [{"$e": 102, "$a": 800}]
print("The candidate violates the team-lead limit; it was never published.")
```

Choose finance to repair the proposed approval:

<!-- gnd-run expect=0 -->
```sh
(cd expense-project && python -m cli.expense_cli approve --model model.orm.json --population approved-101.json --expense 102 --chain finance --output approved-all.json)
```

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path
from gnd.api import check

population = json.loads(Path("expense-project/approved-all.json").read_text())
assert {row["expense"] for row in population["facts"]["expense_is_approved"]} == {101, 102, 103}
assert {tuple(row.values()) for row in population["facts"]["expense_approved_by_chain"]} == {
    (103, "finance"), (101, "team-lead"), (102, "finance"),
}
assert check("expense-demo/model.orm.json", "expense-project/approved-all.json")["exit_code"] == 0
```

Approving the same expense twice is a command refusal:

<!-- gnd-run expect=1 -->
```sh
(cd expense-project && python -m cli.expense_cli approve --model model.orm.json --population approved-all.json --expense 101 --chain team-lead --output duplicate.json)
```

This application checks **post-state invariants**. It does not prove who invoked
the command or whether every historical step was permitted. A system needing
preconditions, operation effects or frame checks should model operations and use
[`gnd.api.transition`](../reference/python-api.md), then retain the appropriate
before/after evidence. Choosing a chain string is not authentication.

## Explicit agent handoffs and exercise

To generate your own version, select **gnd-codegen** after approving the model:

> Generate expense-demo/model.orm.json into expense-project. Explain which files
> are derived. Implement an approval/report CLI in extension files. Call the
> stable gnd.api.check on the input and candidate, publish only a zero-exit
> candidate, preserve input checkpoints and retain the model's policy as the
> single rule evaluator. Declare the extension architecture and concrete smoke
> cases, including an unknown expense refusal.

When ready, explicitly select **gnd-conformance**:

> Check expense-project against expense-demo/model.orm.json. Explain each
> assertion and any drift. Do not regenerate as part of this check.

**Exercise:** Try unknown expense 999 and chain `fast-track`. The first should
be a command refusal, the second a modeled value-constraint failure. In both
cases verify that the requested output is absent and the input is unchanged.
Explain why a successful conformance check alone cannot establish either result.

Next: [evolve the model to require a currency](03-evolution.md).
