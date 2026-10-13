# 3. Add currency through a reviewed model change

The application currently treats every amount as EUR by convention. A new
requirement makes that convention explicit: **every expense must state its
currency**. The fictional policy still permits EUR only. Supporting USD would
also require deciding how category caps, approval limits and conversions work;
a currency label alone would not solve that problem.

This chapter uses an additive proposal, previews its impact, applies it with a
linked-project conformance check, then updates the generated and developer-owned
parts explicitly. Continue from [chapter 2](02-application.md).

## Inspect the proposed model

The supplied `currency.orm.json` adds a `Currency` value type and this fact:

```text
Expense is denominated in Currency
```

The fact requires exactly one currency for every expense. A value constraint
allows `EUR`. New requirements carry `user-supplied`, `confirmed`, `alethic`
provenance from the synthetic exercise brief. Existing constraints and their
provenance are retained byte-for-byte as model values.

For your own project, select **gnd-model-evolve** explicitly and review the
proposal before applying it:

> Add an explicit currency requirement to expense-demo/model.orm.json. Preserve
> the current EUR limits and every unchanged constraint's provenance. Every
> expense must name one currency; support EUR only until I approve a conversion
> policy. Link expense-project for downstream conformance. Prepare and preview
> the complete additive proposal; explain data migration and generated-code
> impact before publication.

The checkpoint helper below prepares that specific proposal. It binds the exact
model bytes, complete candidate, three additive operations and a declared roster
of generated-project and extension files. It uses versioned evolution support
contracts; application code continues to use only the stable `gnd.api` surface.
The helper does not apply or accept a change.

<!-- gnd-run expect=0 -->
```sh
python expense-demo/prepare_currency.py --model expense-demo/model.orm.json --candidate expense-demo/currency.orm.json --project expense-project --output expense-demo/currency.proposal.json
```

## Preview the impact without changing the model

<!-- gnd-run expect=0 -->
```sh
gnd evolve preview expense-demo/model.orm.json expense-demo/currency.proposal.json --workspace . --records expense-demo/evolution-records --out expense-demo/currency.preview.json
```

The preview contains the candidate validation, whole-model verbalization, exact
digests and complete blast-radius entries. Read `expense-demo/currency.preview.json`.
For this bounded tutorial there are no renamed or deleted elements, so the
protocol's `breaking` flag is false. An additive mandatory requirement can still
make old populations inadequate or invalid; that flag does not promise data
compatibility.

<!-- gnd-run expect=0 -->
```python
import hashlib
import json
from pathlib import Path

preview = json.loads(Path("expense-demo/currency.preview.json").read_text())
assert preview["breaking"] is False
assert len(preview["proposal"]["operations"]) == 3
assert all(operation["kind"] == "add" for operation in preview["proposal"]["operations"])
assert preview["before_model"]["sha256"] == hashlib.sha256(Path("expense-demo/model.orm.json").read_bytes()).hexdigest()
assert preview["candidate_model"]["sha256"] == hashlib.sha256(Path("expense-demo/currency.orm.json").read_bytes()).hexdigest()
for entry in preview["blast_radius"]["entries"]:
    print(entry["change"], entry["reference"])
```

The listed impact includes currency roles, mandatory/uniqueness/value constraints,
provenance and verbalization. The linked project roster intentionally excludes
interpreter caches and approval output files; it includes the manifest, derived
files, application modules, declared architecture, model and seed checkpoint.
GND does not discover additional dependent applications for you.

## Apply the reviewed proposal

In this exercise you have inspected a supplied additive change. Run the explicit
apply command when ready to publish it into your local tutorial model:

<!-- gnd-run expect=13 -->
```sh
gnd evolve apply expense-demo/model.orm.json expense-demo/currency.proposal.json --preview expense-demo/currency.preview.json --workspace . --records expense-demo/evolution-records
```

**Expected exit: `13`, published with drift.** The model was changed and the
transaction record completed, but the linked generated project still describes
the previous model. This is a recorded downstream finding, not an automatic
regeneration or an uncommitted proposal. Keep the record; a later clean result
will not rewrite what this check observed.

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

record = json.loads(Path("expense-demo/evolution-records/expense-currency/record.json").read_text())
assert record["published_with_drift"] is True
assert record["conformance_exit_code"] == 13
assert len(record["linked_conformance"]) == 1
assert Path("expense-demo/model.orm.json").read_bytes() == Path("expense-demo/currency.orm.json").read_bytes()
model = json.loads(Path("expense-demo/model.orm.json").read_text())
assert any(fact["id"] == "expense_has_currency" for fact in model["fact_types"])
print("Currency model published; its linked project needs an explicit update.")
```

## Learn what missing coverage means

First recheck the old seed, which makes no completeness claim for currency:

<!-- gnd-run expect=2 -->
```sh
gnd check expense-demo/model.orm.json expense-demo/seed.population.json
```

Exit `2` means the evidence is inadequate for acceptance. The missing currency
relation is **vacuous**, not a demonstrated pass. Treating it as clean would hide
an unfinished migration.

The next checkpoint claims currency coverage but assigns EUR only to expense
103. This gives GND enough information to identify expenses 101 and 102 as
missing required currency facts:

<!-- gnd-run expect=1 -->
```sh
gnd check expense-demo/model.orm.json expense-demo/currency-missing.population.json
```

<!-- gnd-run expect=0 -->
```python
from gnd.api import check

report = check("expense-demo/model.orm.json", "expense-demo/currency-missing.population.json", unredacted=True)
assert report["exit_code"] == 1
mandatory = [row for row in report["verdicts"] if row["constraint_type"] == "mandatory" and row["verdict"] == "fail"]
assert len(mandatory) == 1
assert "expense_has_currency" in mandatory[0]["constraint_ref"]
print(mandatory[0]["message"])

complete = check("expense-demo/model.orm.json", "expense-demo/currency.population.json")
assert complete["exit_code"] == 0
print("All three expenses explicitly carry EUR; the complete checkpoint passes.")
```

The complete population is supplied so you can reproduce the result without an
agent or a database migration. In a real application, reconstruct the currency
from trustworthy source data; do not label unknown amounts EUR just to make a
check pass.

## Update generated code and extension behavior separately

Explicitly select **gnd-codegen** if working with an agent. The local command below
refreshes the derived files. The extension modules are retained:

<!-- gnd-run expect=0 -->
```sh
gnd codegen expense-demo/model.orm.json --out expense-project
```

Now migrate this tutorial's seed checkpoint and replace the report function with
the supplied currency-aware version. Update the architecture declaration to
record its additional consumed fact type:

<!-- gnd-run expect=0 -->
```python
from pathlib import Path
import shutil

source = Path("expense-demo")
project = Path("expense-project")
for origin, target in [
    ("model.orm.json", "model.orm.json"),
    ("currency.population.json", "seed.population.json"),
    ("currency_reporting.py", "cli/reporting.py"),
    ("currency.architecture.contract.yaml", "architecture.contract.yaml"),
]:
    shutil.copy2(source / origin, project / target)
assert (project / "cli/expense_cli.py").read_bytes() == (source / "extension.py").read_bytes()
print("Derived files regenerated; currency reporting and population migration applied explicitly.")
```

The revised report exposes `totals_by_currency`, rather than leaving EUR in a
field-name convention. Its input gate ensures missing currency cannot silently
fall back to EUR. Run the application and conformance again:

<!-- gnd-run expect=0 -->
```sh
(cd expense-project && python -m cli.expense_cli report --model model.orm.json --population seed.population.json)
```

<!-- gnd-run expect=0 -->
```sh
gnd conformance expense-demo/model.orm.json expense-project
```

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
assert json.loads(result.stdout) == {
    "approved": 1, "submitted": 3, "totals_by_currency": {"EUR": 2260},
}
print("The evolved application reports three expenses totaling 2260 EUR.")
```

This migrated seed intentionally starts from chapter 1's checkpoint. Chapter 2's
approval outputs remain old evidence; they have not been silently migrated.
Their currency requirements must be handled before reuse under the changed
model.

## Exercise and next steps

**Exercise:** Remove expense 101's currency from a copy of the migrated seed,
retain its coverage declaration and run `report`. Verify that no total is
printed. Then change its currency to USD: the allowed-value rule should fail.
Explain which policies would need review before USD could become accepted.

You now have a working local reporting and approval application, a reproducible
refusal path and a completed model evolution record. To apply the pattern to
your project, identify the facts your application produces, model the rules that
must hold, and place the check before publishing its result.

Read [evolution and recovery](../guides/evolution-and-recovery.md) for model change
and brownfield workflows, or [data and transitions](../guides/data-and-transitions.md)
for operation checks that audit how a state changes. The
[agent skill guide](../agents/index.md) explains explicit handoffs between
these workflows.

[Next: native reporting and approvals](04-native.md).
