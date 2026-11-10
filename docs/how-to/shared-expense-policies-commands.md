# Run the two-team expense example

These are the commands behind [Two teams, one expense form](../tutorials/shared-expense-policies.md).
The example extends the shipped expense demo with two policies and receipt facts.
Use a development checkout for the unreleased feature; see
[development setup](../installation.md).

!!! info "Files on GitHub"

    - [The shared model and both policies](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/examples/expense/teams)
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
| `shared/expense-v2.orm.json` | Edition 2, published alongside edition 1 |

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

## Review edition 2

A vocabulary producer writes a new standalone-valid model at a new local path,
then supplies its raw file SHA-256. Keep edition 1 available while projects still
use it. Each project reviews its own update; publishing a vocabulary does not
move a project automatically. The format and confinement rules are in the
[includes reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/representation-format.md#model-includes-version-5).

The shipped `sales-repin.proposal.json` changes only the included edition.
Its candidate is invalid: Sales still requires the removed receipt relation.
This preview writes an analysis report and exits 3; it stages no publication.
All paths below stay inside the scratch workspace created by the first step.

<!-- gnd-run expect=3 -->
```sh
gnd evolve preview expense-teams/sales.orm.json expense-teams/sales-repin.proposal.json --workspace . --records expense-records --out expense-analysis.json --format json
```

Inspect the project-owned rules named by that report. The six spending and
approval limits are absent because their definitions did not change:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c 'import json; d=json.load(open("expense-analysis.json")); refs=[r["reference"] for r in d["entries"] if r["reference"].startswith("owned_constraints[")]; assert refs==["owned_constraints[receipt_required]"]; print("Affected Sales rule: receipt_required. Six limits unchanged.")'
```

```text
Affected Sales rule: receipt_required. Six limits unchanged.
```

## Repair the rule in the same change

`sales-update.proposal.json` combines the edition change with retiring
`receipt_required` and adding `document_required`. It contains the complete
authored Sales candidate, not copied Finance definitions. The new rule records
the synthetic owner's explicit instruction, “Every expense must be supported
by a document.” Review the candidate and operations before accepting them.

<!-- gnd-run expect=0 -->
```sh
gnd evolve preview expense-teams/sales.orm.json expense-teams/sales-update.proposal.json --workspace . --records expense-records --out expense-preview.json
```

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c 'import json; p=json.load(open("expense-preview.json")); assert p["breaking"] is True; print("Combined change is valid; explicit acceptance required.")'
```

```text
Combined change is valid; explicit acceptance required.
```

For this reproducible synthetic example, feed the exact reviewed report digest
from the preview to the acceptance prompt. In a real project, review that report
before entering its digest. An include re-pin requires acceptance even if only
its path or bytes changed.

<!-- gnd-run expect=0 -->
```sh
RADIUS=$(python -c 'import json; print(json.load(open("expense-preview.json"))["blast_radius"]["report_sha256"])')
printf '%s\n' "$RADIUS" | gnd evolve apply expense-teams/sales.orm.json expense-teams/sales-update.proposal.json --preview expense-preview.json --workspace . --records expense-records
```

Apply publishes the Sales file and finalizes its record. Check that it exactly
matches the shipped edition-2 candidate, that all six old limits survived, and
that neither shared edition nor Engineering was written:

<!-- gnd-run expect=0 output=stdout -->
```sh
python -c 'import gnd,json,pathlib; p=pathlib.Path("expense-teams"); original=pathlib.Path(gnd.__file__).parent/"examples/expense/teams"; actual=json.loads((p/"sales.orm.json").read_text()); assert actual==json.loads((p/"sales-v2.orm.json").read_text()); assert actual["constraints"]==json.loads((original/"sales.orm.json").read_text())["constraints"]; assert "object_types" not in actual and "fact_types" not in actual; assert all((p/n).read_bytes()==(original/n).read_bytes() for n in ["shared/expense-v1.orm.json","shared/expense-v2.orm.json","engineering.orm.json"]); print("Only the authored Sales policy changed; shared editions and Engineering are unchanged.")'
```

```text
Only the authored Sales policy changed; shared editions and Engineering are unchanged.
```

## Check expenses after the update

The edition-2 populations express the same expenses using supporting documents.
The first has one for each expense; the second omits expense 102's document.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check expense-teams/sales.orm.json expense-teams/sales-v2-seed.population.json --rule-ids
```

```text
...
pass=22 fail=0 warning=0 unchecked=0 vacuous=0
...
```

<!-- gnd-run expect=1 output=stdout -->
```sh
gnd check expense-teams/sales.orm.json expense-teams/sales-v2-missing-document.population.json --rule-ids
```

```text
...
  [fail] constraint:document_required (fact_types[expense_supported_by_document].constraints[1]): Each expense must play the 'expense' role in 'expense_supported_by_document' — violated: '102' plays no such fact.
    remedy: Add a supporting document, then check again.
...
pass=21 fail=1 warning=0 unchecked=0 vacuous=0
...
```

Engineering still checks its original receipt facts against edition 1:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd check expense-teams/engineering.orm.json expense-teams/engineering-seed.population.json
```

```text
...
pass=22 fail=0 warning=0 unchecked=0 vacuous=0
...
```

If a producer has removed edition 1, the preview route accepts an explicitly
supplied, digest-verified historical file through `--previous-include ID=PATH`.
Prefer retaining versioned paths. Historical bytes do not replace verification
of the candidate's live dependencies; see the
[evolution contract](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/references/evolution-contract.md).
