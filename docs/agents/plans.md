# Check an agent's plan

An agent that can act (pay, approve, file, ship) should not answer "done" in prose.
It should answer with a **plan**: a sequence of operations over your model. GND checks
that plan before anything runs. It verifies each step's preconditions, every
intermediate state, and the **frame**: no fact may change unless a declared operation
changes it.

This page is the story told by the animation on the home page, and every command below
runs. The model, the state and both plans ship with GND. The plans stand in for what an
agent emitted; no model provider is called.

## The setup

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from shutil import copytree
copytree(str(files("gnd") / "examples" / "approvals"), "approvals")
```

`approvals/model.orm.yaml` declares three operations. Each one says what must hold
before it runs and what it changes:

| Operation | Precondition | Effect |
|---|---|---|
| `approve_expense(expense, approver)` | the expense is a draft (`pre_draft`, alethic) | status becomes `approved`; the approver is recorded |
| `submit_expense_to_workday(expense, submission)` | the expense is approved (`pre_approved`, alethic) | a Workday submission is created; status becomes `submitted` |
| `reimburse_expense(expense, submission, approver, amount, on_date)` | Workday has it (`pre_submitted`, alethic); an approver is on file (`pre_has_approver`, deontic) | the reimbursement is recorded |

In `approvals/state.pop.yaml`, expense 41 (Ada's €90 team dinner) is still a draft.

<!-- gnd-run expect=0 -->
```sh
gnd validate approvals/model.orm.yaml
```

## The agent's first plan

The user asks: *"Reimburse Ada's €90 team dinner, expense 41."* The agent answers with
`plan-draft-1.steps.json`, which pays the expense directly:

```json
{"op": "reimburse_expense",
 "bindings": {"expense": 41, "submission": "WD-8041", "approver": "alice",
              "amount": 90, "on_date": "2026-10-05"}}
```

Check it in plan mode. Without `--post`, GND computes the resulting state itself:

<!-- gnd-run expect=1 -->
```sh
gnd check approvals/model.orm.yaml --pre approvals/state.pop.yaml --steps approvals/plan-draft-1.steps.json
```

The check exits **1**. Step 1 reports:

```text
[fail] $.steps[1].preconditions[id=pre_submitted]: step 1 (reimburse_expense) requires
       expense_submitted_to_workday to hold for {'expense': 41, 'submission': 'WD-8041'}, and it does not
[warning] $.steps[1].preconditions[id=pre_has_approver]: step 1 (reimburse_expense) requires
       expense_approved_by to hold for {'expense': 41, 'approver': 'alice'}, and it does not
```

The alethic precondition failed, so the plan is rejected. The deontic one is reported
as a warning. That is the feedback the agent receives: the rule, the operation, the
step and the exact binding. The feedback does not contain the answer.

## The revised plan

With that feedback the agent adds the missing steps: approve, submit to Workday, then
reimburse. That is `plan-draft-2.steps.json`:

<!-- gnd-run expect=0 -->
```sh
gnd check approvals/model.orm.yaml --pre approvals/state.pop.yaml --steps approvals/plan-draft-2.steps.json
```

Exit **0**. GND walked all three steps, found every precondition satisfied, and printed
the computed post-state, in which expense 41 is reimbursed. Only now does your
application execute the plan.

The same check from Python returns the report as a dictionary:

<!-- gnd-run expect=0 -->
```python
from gnd import api

first = api.transition("approvals/model.orm.yaml", "approvals/state.pop.yaml",
                       "approvals/plan-draft-1.steps.json")
second = api.transition("approvals/model.orm.yaml", "approvals/state.pop.yaml",
                        "approvals/plan-draft-2.steps.json")
print(first["exit_code"], second["exit_code"])  # 1 0
assert (first["exit_code"], second["exit_code"]) == (1, 0)
```

## A side effect nobody declared

Plans are not the only risk. Suppose an agent, or the application code it wrote,
approves expense 41 and reports the resulting state. In `claimed-post.pop.yaml`,
bystander expense 42 has *also* flipped from `submitted` to `rejected`. Every fact in
that state is individually legal: one status per expense, valid values, nothing
missing. No snapshot check can see the problem.

Audit the walk by supplying the claimed post-state with `--post`:

<!-- gnd-run expect=1 -->
```sh
gnd check approvals/model.orm.yaml --pre approvals/state.pop.yaml --steps approvals/approve-41.steps.json --post approvals/claimed-post.pop.yaml
```

The frame check fails it:

```text
FRAME
  expense_has_status: alethic (all-alethic; approve_expense)
  [fail] $.post.facts.expense_has_status: the declared post-state contains 1 expense_has_status
         fact(s) that no operation in this walk asserts
  [fail] $.post.facts.expense_has_status: the declared post-state is missing 1 expense_has_status
         fact(s) that no operation in this walk retracts
```

`approve_expense` declares exactly what it changes, so a change to expense 42 is an
undeclared side effect. Frame checks cover the fact types the walk touches; audit
changes outside that set separately.

## Ask your agent for plans

Have your application's skill, or your prompt, require structured plans:

```text
When asked to act on expenses, do not act directly. Write a steps.json plan using only
the operations in model.orm.yaml, run
  gnd check model.orm.yaml --pre state.pop.yaml --steps plan.steps.json --format json
and revise the plan until it exits 0. Report the final plan and the check's exit code.
```

To run that loop with a bounded number of attempts and closed feedback, use a
[development session](dev-session.md) with a transition-walk contract. The
[data and transitions guide](../guides/data-and-transitions.md#audit-a-transition) covers
the walk format, plan mode and audit mode in detail.
