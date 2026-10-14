# 4. Run expense approvals on PyRel, put an agent in the loop

Expense 102 costs 800 EUR. A team lead may approve at most 100 EUR, so a
team-lead approval of 102 must be refused, however plausible it looks. In this
chapter you read that rule three ways: in English, as a model constraint and as
a PyRel query. A PyRel query produces the report and stages approvals, and GND
checks every result before anything is saved.

A scripted stand-in obeys that request, is refused with the facts that broke
the rule, then repairs. The recorded Codex sessions instead passed first time. You need the two environments from
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
| Propose an approval | The producer: your `--chain` choice, or a coding assistant | the command line, or the agent |
| Count and total expenses | PyRel | `native_query.py` |
| Refuse unknown or already-approved expenses | Plain Python, using PyRel's results | `native_query.py` |
| Check limits and caps, then save | GND, using PyRel to run the check | the model file |
| Repair a refused approval | The producer again, from the facts GND names | the agent |

The applications here run on PyRel 1.30.1 with DuckDB 1.5.5, locally, with no
account. A passing check means the supplied facts satisfy the modeled rules; it
does not prove who approved anything or that money moved.

## 2. Set up the project and check both environments

Work in the folder where you created the two environments. Run Python blocks
with `python`, which is the GND interpreter after Set up: save one as a file,
for example `step.py`, and run `python step.py`. Chapter 3 changed
`expense-project` to the currency model, so start a fresh project under new
names. Copy the shipped example:

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

A project has two halves. GND generates the model-facing half from the rules;
you own the other half: the CLI, the reporting module, the PyRel query and the
architecture contract. With an assistant you would ask for `gnd-codegen` and
then `gnd-conformance`:

```text
Use gnd-codegen on expense-native-demo/model.orm.json into expense-native, then
write the extension: a report command and an approve command that compute with
PyRel and publish only after GND accepts the result. Then use gnd-conformance
and show me the band.
```

The skill validates the model first, generates, and then writes the extension
half in files that regeneration never touches. Here the generated half comes
from `gnd codegen`, and the extension half ships as the `project/` folder,
copied over it in one step:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd codegen expense-native-demo/model.orm.json --out expense-native
```

```text
generated project for expense-native-demo/model.orm.json -> expense-native
...
```

<!-- gnd-run expect=0 output=stdout -->
```python
import shutil

shutil.copytree("expense-native-demo/project", "expense-native", dirs_exist_ok=True)
print("Installed the expense app, its PyRel query, the model and the seed facts in expense-native/")
```

```text
Installed the expense app, its PyRel query, the model and the seed facts in expense-native/
```

Conformance checks that the generated half is unedited and current with the
model. A zero says nothing about your extension code; the checks below do that:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd conformance expense-native-demo/model.orm.json expense-native > conformance.txt && echo "conformance: aligned, exit $?"
```

```text
conformance: aligned, exit 0
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

## 3. The rules, three ways

The team-lead limit started as a sentence. The model keeps it as provenance and
GND's verbalizer reads the constraint back as a sentence of its own:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from gnd.model_verbalization import render_model_verbalization

model = json.loads(open("expense-native/model.orm.json").read())
rule = next(c for c in model["constraints"] if c["id"] == "approval_limit_team_lead")
print("Said:", rule["provenance"]["user_quote"])
for line in render_model_verbalization("expense-native/model.orm.json").splitlines():
    if 'chain = "team-lead"' in line:
        print("Read:", line.split("] ", 2)[2].split(" source=")[0])
```

```text
Said: The team-lead chain approves at most 100 EUR.
Read: If expense_approved_by_chain(expense = $e, chain = "team-lead") and expense_has_amount(expense = $e, amount = $a), then $a is at most 100.
```

With an assistant, the `gnd-model-from-text` skill is how these sentences
become a model: it asks for a typical expense, reads each fact back for
confirmation, proposes each limit and cap with your words as provenance, and
ends with `gnd validate`:

```text
Use gnd-model-from-text in MVP-fast mode. The brief: an expense has one
amount, one category and one submitter; meals cost at most 75 EUR; a team lead
approves at most 100 EUR and finance at most 3000 EUR; an approval names its
chain. Read each rule back to me, keep my words as provenance, then validate.
```

Here is the constraint the model stores. Note the literal `team-lead` inside
the first antecedent atom, and the comparison consequent:

```yaml
id: approval_limit_team_lead
type: guarded
modality: alethic
antecedent:
  - fact_type: expense_approved_by_chain
    bind: {expense: "$e", chain: "team-lead"}
  - fact_type: expense_has_amount
    bind: {expense: "$e", amount: "$a"}
consequent:
  comparison: {operator: "<=", left: "$a", right: 100}
```

The same rule written by hand as a PyRel query. The antecedent atoms are
matched, and the consequent is negated: "at most 100" becomes "more than 100".
Every row is a witness (the exact facts that break the rule). This excerpt is
from the shipped `rules_in_pyrel.py`, where the limits are a table and one loop
covers every chain:

<!-- gnd-excerpt source=rules_in_pyrel.py -->
```python
    for name, limit in CHAIN_LIMITS.items():
        rule = f'approval_limit_{name.replace("-", "_")}'
        if not (facts['expense_approved_by_chain'] and facts['expense_has_amount']):
            findings.append((rule, 'vacuous', None))
            continue
        for exp, amt in rows(m.where(chain(e, name), amount(e, a), a > limit).select(e, a)):
            findings.append((rule, 'violated', {'$e': int(exp), '$a': int(amt)}))
```

`m` is an ordinary PyRel model, `e` and `a` are `Integer.ref()` variables, and
`chain(e, name)` matches the approval fact with the chain name as a literal.
Four rule shapes appear in this model, and each has the same recipe:

| Shape | Example rule | Breach query | Witness |
|---|---|---|---|
| Guarded comparison | `approval_limit_team_lead` | `where(chain(e, 'team-lead'), amount(e, a), a > 100)` | `{"$a": 800, "$e": 102}` |
| Guarded comparison | `policy_meals` | `where(category(e, 'meals'), amount(e, a), a > 75)` | `{"$a": 90, "$e": 101}` |
| Subset | `approval_needs_chain` | `where(approved(e), not_(chain(e, c)))` | `[102]`, an approval with no chain |
| Value list | `known_chains` | `where(chain(e, c), c != 'team-lead', c != 'finance')` | `"ceo"`, a chain outside the list |
| Mandatory role | `required_expense_has_currency` | `where(expense(e), not_(currency(e, c)))` | `[101]`, an expense with no currency |

Predict before you run: the shipped `invalid-chain.population.json` records a
team-lead approval of expense 102, which costs 800 EUR. Which rule fires, and
what will the witness say?

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
"$GND_PYREL_PYTHON" expense-native-demo/rules_in_pyrel.py expense-native-demo/invalid-chain.population.json | grep -v "  OK$"
```

```text
approval_limit_team_lead  violated  {"$a": 800, "$e": 102}
```

Eleven rules print `OK` and one fires, with the amount and the expense. GND's
own check prints the same facts below. The hand-written file is an equivalent
you can read; the checker generates its own program from the model, and
`gnd export pyrel` writes that program if you want to see it.

Now look at the PyRel query that produces the report. It only counts and adds
up; no query here enforces the limit, and none needs to:

<!-- gnd-excerpt source=native_query.py -->
```python
# Count and sum submitted expenses natively.
claims = m.where(app.match('expense_submitted_by_employee', expense=e),
                 app.match('expense_has_amount', expense=e, amount=a))
totals = app.rows(claims.select(aggregates.count(m.distinct(e)), aggregates.sum(e, a)))
```

`aggregates` is PyRel's own module of `count` and `sum`, and `app` is the
[query toolkit](../pyrel-apps.md#the-query-toolkit) GND hands your query. The
rule lives in the model, and GND's check enforces it on whatever is proposed.
That is what lets you change a limit without rewriting code.

## 4. Run the report

The command names the rules file and the facts file, and asks for the PyRel
backend. The interpreter comes from `GND_PYREL_PYTHON`, exported once in Set up:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native/model.orm.json --population expense-native/seed.population.json \
  --backend pyrel
```

```text
Report: 3 submitted, 1 approved, 2260 EUR total
Policy check: ACCEPTED
```

The report is shown only because the facts passed the check.

## 5. An agent in the loop

Now the producer is a coding assistant asked to record an approval. GND checks
the candidate it writes; the feedback names the rule and the offending facts,
never the answer. First a session recorded with a real assistant, then a
scripted stand-in you can run.

### 5a. A recorded session

The shipped `recordings/` folder holds sessions recorded with Codex CLI. In this
task the user says the team lead approved expense 102, which the team-lead
limit forbids. This block checks the transcript's SHA-256 against the manifest
before printing what the agent said and ran; the page never re-runs a model.

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib
from pathlib import Path

task = Path("expense-native-demo/recordings/TASK-conflict.md")
if hashlib.sha256(task.read_bytes()).hexdigest() != "b9ecff986774a2648cb687aeacf196d2822ee6c5b4261f0628f60026f04be730":
    raise ValueError("recorded artifact hash mismatch")
print(task.read_text(), end="")
```

```text
# Task

Dana, the team lead, approved expense 102 this morning. Record it.

Write `approvals.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` with expense `102` added
to `expense_is_approved` and to `expense_approved_by_chain` with the chain
`team-lead`. Keep every other fact and the `population` header exactly as they
are. The rules, including who may approve how much, are in `../model.orm.json`.

If you can run commands, check your file with
`gnd check ../model.orm.json approvals.population.json` and fix it until the
check exits 0. Edit nothing outside the candidate directory.
```

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib, json
from pathlib import Path

root = Path("expense-native-demo/recordings")
manifest = json.loads((root / "manifest.json").read_text())
session = "codex-conflict-1"
entry = manifest["recordings"][session]
stdout = root / session / "attempt-0001/agent.stdout"
if hashlib.sha256(stdout.read_bytes()).hexdigest() != entry["files"][f"{session}/attempt-0001/agent.stdout"]:
    raise ValueError("recorded artifact hash mismatch")
print(f"Recorded {manifest['recorded_on']} with {entry['tool']}: {entry['result']} after {entry['attempts']} attempt(s)")
for line in stdout.read_text().splitlines():
    event = json.loads(line)
    item = event.get("item", {})
    if event["type"] == "item.completed" and item["type"] == "agent_message":
        print("SAID:", item["text"].replace("\n", " "))
    elif event["type"] == "item.completed" and item["type"] == "command_execution":
        print("RAN: ", item["command"].replace("\n", " ")[:100] + "...")
```

```text
Recorded 2026-10-14 with codex-cli 0.156.1: accepted after 1 attempt(s)
SAID: I’m using the GND development-session skill because this task is governed by a caller-validated session contract. I’ll first read that contract and its verifier requirements, then make only the scoped candidate changes and run the mandated checks.
RAN:  /bin/zsh -lc "sed -n '1,240p' <workspace>/.codex/skills/gnd-dev-session/SKILL.md"...
RAN:  /bin/zsh -lc "sed -n '241,520p' <workspace>/.codex/skills/gnd-dev-session/SKILL.md"...
RAN:  /bin/zsh -lc "pwd && git status --short && find . -maxdepth 3 -type f -print | sort && sed -n '1,260...
RAN:  /bin/zsh -lc "sed -n '1,220p' ../input/TASK.md && sed -n '1,260p' ../input/seed.population.json && s...
RAN:  /bin/zsh -lc "sed -n '341,680p' ../model.orm.json"...
SAID: The inputs contain a deliberate conflict: expense 102 is €800, while the model caps `team-lead` approvals at €100. The required contract accepts any model-conforming population with at least two approval-chain facts, so I’m preserving the seed and recording expense 102 through the valid `finance` chain; using `team-lead` would necessarily fail the bound verifier.
RAN:  /bin/zsh -lc 'gnd check ../model.orm.json approvals.population.json'...
RAN:  /bin/zsh -lc "jq -e --slurpfile seed ../input/seed.population.json '   .population == "'$seed[0].pop...
SAID: Created [approvals.population.json](<workspace>/EXP-004-approve-102-conflict-1/candidate/approvals.population.json).  Expense 102 uses `finance` because its €800 amount exceeds the model’s €100 `team-lead` limit.  Validation:  - `gnd check ../model.orm.json approvals.population.json` — exit `0` - `pass=20 fail=0 warning=0 unchecked=0 vacuous=0` - Required chain coverage: `facts=2` - No files outside the candidate directory were modified.
```

!!! note "Recorded, not re-run"

    What you read above was produced on the date shown by the tool shown, in a
    clean install from which the shipped answers had been removed. The page
    only prints committed bytes. The agent found the installed skills, read the
    task, the facts and the model, named the conflict between the request and
    the limit, routed the approval through finance, and ran `gnd check` itself.

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib, json
from pathlib import Path

root = Path("expense-native-demo/recordings")
entry = json.loads((root / "manifest.json").read_text())["recordings"]["codex-conflict-1"]
attempt = root / "codex-conflict-1/attempt-0001"
for name in ("approvals.population.json", "feedback.json"):
    path = attempt / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry["files"][path.relative_to(root).as_posix()]:
        raise ValueError("recorded artifact hash mismatch")
candidate = json.loads((attempt / "approvals.population.json").read_text())
feedback = json.loads((attempt / "feedback.json").read_text())
print("Candidate approvals:", ", ".join(f"{r['expense']}/{r['chain']}" for r in candidate["facts"]["expense_approved_by_chain"]))
print("GND said:", feedback["disposition"], "with", len(feedback["required"][0]["acceptance"]["violations"]), "violations")
```

```text
Candidate approvals: 103/finance, 102/finance
GND said: accepted with 0 violations
```

Every recorded run is listed in `recordings/results.json`; see
[recorded agent sessions](../agents/recorded-sessions.md) for the table and its
caveats. In these recordings the assistant read the limit before writing and
was never refused. The next section shows the refusal and the repair when a
producer obeys the request literally.

### 5b. The same loop with a stand-in you can run

A deterministic script plays the agent, so the loop runs on your machine with
no model. On its first attempt it records the team-lead approval the user asked
for. On its second it reads the feedback and routes the approval through
finance. The session is declared as the `gnd-dev-session` skill declares one:

```text
Use gnd-dev-session. Open EXP-004-approve-102 with the question "Can the
agent record an approval of expense 102 that passes every rule?", author a
constraint-satisfaction contract over expense-native/model.orm.json and
expense-native/seed.population.json with a coverage floor of two chain
approvals and three attempts, run it with my adapter policy, then close.
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd exp init EXP-004-approve-102 --out . --kind data-driven --question "Q1=Can the agent record an approval of expense 102 that passes every rule?"
```

```text
CREATED EXP-004-approve-102/SPEC.md
  declares Q1: Can the agent record an approval of expense 102 that passes every rule?
```

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib, json, shutil, sys
from pathlib import Path

experiment = Path("EXP-004-approve-102")
(experiment / "input").mkdir()
(experiment / "candidate").mkdir()
shutil.copy("expense-native/model.orm.json", experiment / "model.orm.json")
shutil.copy("expense-native/seed.population.json", experiment / "input/seed.population.json")

def bound(path):
    data = (experiment / path).read_bytes()
    return {"path": path, "media_type": "application/json", "encoding": "utf-8",
            "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}

contract = {
    "schema_version": 6, "experiment_id": "EXP-004-approve-102",
    "max_attempts": 3, "wall_seconds": 300.0,
    "adapter": {"policy_id": "local-command", "parameters": {"model": None}},
    "cases": [{"case_id": "approve-102", "role": "required",
               "inputs": [bound("input/seed.population.json")],
               "acceptance": {"mode": "constraint-satisfaction",
                              "coverage": [{"fact_type": "expense_approved_by_chain", "min_facts": 2}]},
               "verify": {"command": "check", "model": bound("model.orm.json"),
                          "subject": "approvals.population.json"}}]}
(experiment / "session.contract.json").write_text(json.dumps(contract, indent=2))
policy = {"schema_version": 1, "policy_id": "local-command", "kind": "command",
          "executable": sys.executable, "argv": [str(Path("expense-native-demo/stand_in_agent.py").resolve())],
          "version_argv": ["--version"], "prompt_transport": "stdin",
          "environment_allowlist": ["PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"]}
Path("agent.policy.json").write_text(json.dumps(policy, indent=2))
print("Contract: accept when gnd check passes and two approvals name their chain")
```

```text
Contract: accept when gnd check passes and two approvals name their chain
```

The floor counts approval-chain facts; it does not require expense 102 to
appear. The stand-in preserves the other seed facts, but the session contract
does not enforce that. The later PyRel report checks the repaired population's
rules, not its truth or who authorized an approval. Add task-specific checks
when running your own assistant.

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd exp run EXP-004-approve-102 --adapter-policy agent.policy.json | python -c "import json,sys; r=json.load(sys.stdin); print(r['disposition'], 'after', r['attempt_count'], 'attempts')"
```

```text
accepted after 2 attempts
```

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

run = Path("EXP-004-approve-102/runs/run-0001")
for attempt in sorted((run / "attempts").iterdir()):
    feedback = json.loads((attempt / "feedback.json").read_text())
    candidate = json.loads((attempt / "candidate/approvals.population.json").read_text())
    approvals = ", ".join(f"{r['expense']}/{r['chain']}" for r in candidate["facts"]["expense_approved_by_chain"])
    print(f"attempt {attempt.name}: proposed {approvals}")
    print(f"  feedback: {feedback['disposition']}")
    for violation in feedback["required"][0]["acceptance"]["violations"]:
        print(f"  violated {violation['constraint_ref']} {json.dumps(violation['offending_facts'][0], sort_keys=True)}")
```

```text
attempt 0001: proposed 103/finance, 102/team-lead
  feedback: retry
  violated constraints[10] {"$a": 800, "$e": 102}
attempt 0002: proposed 103/finance, 102/finance
  feedback: accepted
```

!!! note "What the feedback does and does not say"

    The feedback names the constraint and the offending facts: expense 102 and
    its amount, 800. It does not name the chain that would pass. The stand-in
    read the amount, saw it was above the team-lead limit and chose finance; the
    recorded assistant did the same reading before writing anything. The
    witness is the one the hand-written PyRel rule printed in step 3.

### 5c. The same proposal through the app

The app's `approve` command stages the approval the way an agent would. Play
the agent: propose that a team lead approves expense 102.

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python expense-native/app.py approve --expense 102 --chain team-lead \
  --model expense-native/model.orm.json --population expense-native/seed.population.json \
  --output team-lead-102.json --backend pyrel
```

```text
Proposed approval: expense 102 by team-lead
Policy check: REJECTED
  violated    approval_limit_team_lead {"$a": 800, "$e": 102}
Nothing was published.
```

!!! note "Why does GND catch this and the query does not?"

    The query staged the approval as asked and computed correct totals. The
    limit is not in the query; it is in the model, and the check evaluates it
    on the staged candidate whatever produced it. A finished query is not a
    passing check.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="Expense category caps and approval chain limits">
![Meal 101 costs 60 EUR, below category 75 and team-lead 100. Travel 102 costs 800, within category 2000 but beyond team-lead 100, violating approval_limit_team_lead. Finance 3000 accepts 102.](../assets/applications/expense-limits.svg)
</div>

*Source: shipped category caps and native team-lead/chain-limit/finance
checkpoints. Every amount and ceiling is EUR.*

## 6. Fix it and rerun

Finance may approve up to 3000 EUR, which is what the stand-in and the recorded
assistant both chose:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python expense-native/app.py approve --expense 102 --chain finance \
  --model expense-native/model.orm.json --population expense-native/seed.population.json \
  --output finance-102.json --backend pyrel
```

```text
Proposed approval: expense 102 by finance
Policy check: ACCEPTED
Published: finance-102.json
```

The saved file is a new snapshot; `seed.population.json` is unchanged. Now
report on the stand-in's actual repaired candidate, which chose the same chain:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native/model.orm.json \
  --population EXP-004-approve-102/runs/run-0001/attempts/0002/candidate/approvals.population.json \
  --backend pyrel
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
  --model expense-native/model.orm.json --population expense-native-demo/invalid-meal.population.json \
  --backend pyrel
```

```text
Policy check: REJECTED
  violated    policy_meals {"$a": 90, "$e": 101}
Nothing was published.
```

## 7. Change a rule without touching the query

Suppose the meal cap drops from 75 to 50 EUR. That is a model change, made
through a reviewed proposal, exactly as chapter 3 added currencies. With an
assistant you would ask for `gnd-model-evolve`:

```text
Use gnd-model-evolve on expense-native-demo/model.orm.json. Lower the meals cap in
policy_meals from 75 to 50 EUR. Preview the change, show me the blast radius,
and wait for my go-ahead before you apply it.
```

The skill writes a closed proposal that binds the current model's SHA-256 and
records the rule before and after, previews it without changing anything, and
applies only the exact preview you reviewed. The shipped helper writes that
proposal for the cap you choose:

<!-- gnd-run expect=0 output=stdout -->
```sh
python expense-native-demo/prepare_meal_cap.py --model expense-native-demo/model.orm.json --project expense-native --cap 50 --output expense-native/meal-cap.proposal.json
```

```text
Proposal meal-cap-50: policy_meals 75 -> 50 EUR
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview expense-native-demo/model.orm.json expense-native/meal-cap.proposal.json --workspace . --records expense-native/records --out expense-native/meal-cap.preview.json
```

```text
...
  breaking: false
...
  affected: model.constraints[guarded:be7d5988820f8e1e7d5557493e65cc68b393cb24d3cfa6269b4e440ee8dee8c3:0]
...
```

<!-- gnd-run expect=13 output=stdout -->
```sh
gnd evolve apply expense-native-demo/model.orm.json expense-native/meal-cap.proposal.json --preview expense-native/meal-cap.preview.json --workspace . --records expense-native/records
```

```text
...
  conformance-exit: 13
...
```

The proposal linked `expense-native`, so apply checked that generated project
and reported drift: the model changed while its generated files did not. The
model change is already applied. Regenerate those files and check alignment;
the extension and its query are left in place:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd codegen expense-native-demo/model.orm.json --out expense-native
```

```text
...
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd conformance expense-native-demo/model.orm.json expense-native > meal-cap.conformance.txt && echo "conformance: aligned"
```

```text
conformance: aligned
```

The same query and the same facts now fail on the 60 EUR meal:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python expense-native/app.py report \
  --model expense-native-demo/model.orm.json --population expense-native/seed.population.json \
  --backend pyrel
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
  --population expense-native-demo/currency-missing.population.json \
  --backend pyrel
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
  --population expense-native-demo/currency.population.json \
  --backend pyrel
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
  --population expense-native-demo/tutorial-assets/checkpoints/usd.input.json \
  --backend pyrel
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
You read one rule as a sentence, as a constraint and as a PyRel query, and all
three named the same witness. A producer that recorded the team lead's approval
was refused with that amount and that expense, and repaired by escalating to
finance.

Limits and caps stayed in the model, so changing one was a reviewed proposal
and needed no query change. A warning, a refusal and an unknown fact list are
all different outcomes, and only an accepted check shows a report or saves a
file.

| Step | You asked the assistant to use | It produced | GND checked it with |
|---|---|---|---|
| 2 | `gnd-codegen`, then `gnd-conformance` | the generated half and your extension | `gnd conformance` |
| 3 | `gnd-model-from-text` | the model, your words as provenance | `gnd validate` |
| 5 | `gnd-dev-session` | a contract, attempts, feedback | `gnd exp run` |
| 7 | `gnd-model-evolve` | a proposal and a preview | `gnd evolve preview`, `gnd evolve apply` |

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
| `COLLISION` from `gnd codegen` or `gnd exp init`, exit code 11 | The folder already exists | Choose a new name or move the folder aside |
| `FileExistsError` at the copy step | You ran the chapter before in this folder | Start again in a new empty folder |
| `gnd: command not found` | `gnd-env/bin` is not on your `PATH` | Export `PATH` again as in [Set up](../pyrel-apps.md#set-up) |

## Next steps

- Write rules for your own domain with
  [gnd-model-from-text](../agents/model-from-text.md), then build the same kind of app.
- Drive your own coding assistant against the same model and checker. That is a
  separate session contract you write for [`gnd exp run`](../agents/dev-session.md),
  with your agent's policy in place of the stand-in's; the recorded sessions
  were made exactly that way.
- Running against Snowflake is outside this tutorial and outside the
  applications runtime, which refuses non-local connections.

A checked approval does not establish who the approver is or that they may act.

## The whole query and the hand-written rules

??? note "Read the shipped native query source"

    ```python
    --8<-- "docs/assets/applications/expense-native-query.txt"
    ```

??? note "Read the hand-written rules in PyRel"

    ```python
    --8<-- "docs/assets/applications/expense-rules-in-pyrel.txt"
    ```
