# Run the two-team expense example

These are the commands behind [Two teams, one expense form](../tutorials/shared-expense-policies.md).
The example extends the shipped expense demo with two policies and receipt facts.
Use a checkout of this draft branch for the unreleased feature; see
[development setup](../installation.md).

!!! info "Files on GitHub"

    - [The shared model and both policies](https://github.com/vasiloglou/gnd-public/tree/codex/model-composition-docs-draft/src/gnd/examples/expense/teams)
    - [The original expense demo](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/expense)

## Copy and inspect the files

<!-- gnd-run expect=0 -->
```sh
python -c 'import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / '"'"'examples/expense/teams'"'"', '"'"'expense-teams'"'"')'
```

| File | Contains |
|---|---|
| `shared/expense-v1.orm.json` | Finance's shared definitions and 15 common rules |
| `engineering.orm.json` | The original six spending/approval limits and an advisory receipt rule |
| `sales.orm.json` | Six limits, with a higher meal/team-lead limit, and a blocking receipt rule |
| `TEAM-STATE.population.json` | The same facts under each team's model identity |
| `shared/expense-v2.orm.json` | Proposed next edition for the update walkthrough, still planned |

The policies contain no object or fact definitions. The new receipt relation
is shared; whether it is mandatory belongs to the team. All data is synthetic.
Real projects keep a local versioned copy beneath each including model's directory.
The file-format rules live in the
[model includes reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#model-includes-version-5).

Verify that the paired populations really contain the same facts:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c 'import json, pathlib; p=pathlib.Path('"'"'expense-teams'"'"'); states=('"'"'seed'"'"','"'"'dinner'"'"','"'"'approval'"'"','"'"'missing-receipt'"'"'); assert all(json.loads((p/f'"'"'engineering-{s}.population.json'"'"').read_text())['"'"'facts'"'"']==json.loads((p/f'"'"'sales-{s}.population.json'"'"').read_text())['"'"'facts'"'"'] for s in states); print('"'"'Same facts for both teams in all four states.'"'"')'
```

```text
Same facts for both teams in all four states.
```

## Validate the shared model and both policies

The next edition can exist alongside edition 1 without moving either team.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate expense-teams/shared/expense-v1.orm.json
```

```text
OK: expense-teams/shared/expense-v1.orm.json is a valid GND ORM model
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate expense-teams/shared/expense-v2.orm.json
```

```text
OK: expense-teams/shared/expense-v2.orm.json is a valid GND ORM model
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate expense-teams/engineering.orm.json
```

```text
OK: expense-teams/engineering.orm.json is a valid GND ORM model
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd validate expense-teams/sales.orm.json
```

```text
OK: expense-teams/sales.orm.json is a valid GND ORM model
```

## Read back each complete model

These commands write the complete model text for review. The source files show
which rules each owner contributes; the renderer's header identifies the shared
model but does not label every sentence's owner.

<!-- gnd-run expect=0 -->
```sh
gnd verbalize model expense-teams/engineering.orm.json > engineering-review.txt
```

<!-- gnd-run expect=0 -->
```sh
gnd verbalize model expense-teams/sales.orm.json > sales-review.txt
```

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c 'import json, pathlib; p=pathlib.Path('"'"'expense-teams'"'"'); expected={'"'"'engineering'"'"':(75,100,'"'"'receipt_expected'"'"'),'"'"'sales'"'"':(120,1000,'"'"'receipt_required'"'"')}; models={t:json.loads((p/f'"'"'{t}.orm.json'"'"').read_text()) for t in expected}; assert models['"'"'engineering'"'"']['"'"'includes'"'"']==models['"'"'sales'"'"']['"'"'includes'"'"']; checks=[(t,{r['"'"'id'"'"']:r for r in models[t]['"'"'constraints'"'"']},limits) for t,limits in expected.items()]; assert all(r['"'"'policy_meals'"'"']['"'"'consequent'"'"']['"'"'comparison'"'"']['"'"'right'"'"']==limits[0] and r['"'"'approval_limit_team_lead'"'"']['"'"'consequent'"'"']['"'"'comparison'"'"']['"'"'right'"'"']==limits[1] and limits[2] in pathlib.Path(f'"'"'{t}-review.txt'"'"').read_text() and '"'"'[fact-type:expense_has_receipt]'"'"' in pathlib.Path(f'"'"'{t}-review.txt'"'"').read_text() for t,r,limits in checks); print('"'"'Both complete reviews contain the shared receipt relation and the correct team policy.'"'"')'
```

```text
Both complete reviews contain the shared receipt relation and the correct team policy.
```

## Check the same facts under each policy

The excerpts below keep findings, remedies and totals. `...` stands for omitted
passing-rule and coverage lines; the tutorial runner checks the retained lines
and every command's result.

### The original three expenses, with receipts

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check expense-teams/engineering.orm.json expense-teams/engineering-seed.population.json --rule-ids
```

```text
...
pass=22 fail=0 warning=0 unchecked=0 vacuous=0
...
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check expense-teams/sales.orm.json expense-teams/sales-seed.population.json --rule-ids
```

```text
...
pass=22 fail=0 warning=0 unchecked=0 vacuous=0
...
```

### Expense 101 claims a 90 EUR meal

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check expense-teams/engineering.orm.json expense-teams/engineering-dinner.population.json --rule-ids
```

```text
...
  [fail] constraint:policy_meals (constraints[0]): Guarded comparison consequent evaluated over bindings=1 — violated by bindings: {'$e': '101', '$a': '90'}.
...
pass=21 fail=1 warning=0 unchecked=0 vacuous=0
...
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check expense-teams/sales.orm.json expense-teams/sales-dinner.population.json --rule-ids
```

```text
...
pass=22 fail=0 warning=0 unchecked=0 vacuous=0
...
```

### Expense 102 is approved by a team lead

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check expense-teams/engineering.orm.json expense-teams/engineering-approval.population.json --rule-ids
```

```text
...
  [fail] constraint:approval_limit_team_lead (constraints[4]): Guarded comparison consequent evaluated over bindings=1 — violated by bindings: {'$e': '102', '$a': '800'}.
...
pass=21 fail=1 warning=0 unchecked=0 vacuous=0
...
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check expense-teams/sales.orm.json expense-teams/sales-approval.population.json --rule-ids
```

```text
...
pass=22 fail=0 warning=0 unchecked=0 vacuous=0
...
```

### Expense 102 has no receipt

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check expense-teams/engineering.orm.json expense-teams/engineering-missing-receipt.population.json --rule-ids
```

```text
...
  [warning] constraint:receipt_expected (fact_types[expense_has_receipt].constraints[1]): Each expense must play the 'expense' role in 'expense_has_receipt' — violated: '102' plays no such fact.
    remedy: Attach the receipt if it turns up.
...
pass=21 fail=0 warning=1 unchecked=0 vacuous=0
...
```

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check expense-teams/sales.orm.json expense-teams/sales-missing-receipt.population.json --rule-ids
```

```text
...
  [fail] constraint:receipt_required (fact_types[expense_has_receipt].constraints[1]): Each expense must play the 'expense' role in 'expense_has_receipt' — violated: '102' plays no such fact.
    remedy: Add the receipt, then check again.
...
pass=21 fail=1 warning=0 unchecked=0 vacuous=0
...
```

## Refuse a changed shared file

Use a scratch copy, so the example's edition 1 stays untouched. A whitespace-only
edit is enough to change its exact bytes:

<!-- gnd-run expect=0 -->
```sh
python -c 'import pathlib, shutil; shutil.copytree('"'"'expense-teams'"'"', '"'"'tampered-teams'"'"'); p=pathlib.Path('"'"'tampered-teams/shared/expense-v1.orm.json'"'"'); p.write_bytes(p.read_bytes()+b'"'"' '"'"')'
```

<!-- gnd-run expect=3 output=stdout -->
```sh
gnd check tampered-teams/sales.orm.json tampered-teams/sales-seed.population.json
```

```text
ERROR at $.includes[0]: include:hash-mismatch [include:hash-mismatch]
```

GND refuses before checking the expenses. The original example remains unchanged.

## Planned: review edition 2

Edition 2 replaces the receipt relation with a supporting-document relation.
The final walkthrough will show an update preview naming `receipt_required`,
then the combined edition/rule change and a successful check. No update or
publication command is presented as runnable in this checkpoint.
