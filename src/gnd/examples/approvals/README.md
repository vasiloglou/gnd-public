# Expense approvals: checking an agent's plan

A small operations model. An agent that is asked to pay an expense answers with
a *plan*: a sequence of operations over the model. GND checks every step's
preconditions, every intermediate state, and the frame: no fact may change
unless a declared operation changes it.

| File | What it is |
|---|---|
| `model.orm.yaml` | Expenses, approvers, Workday submissions, reimbursements, and three operations: `approve_expense`, `submit_expense_to_workday`, `reimburse_expense` |
| `state.pop.yaml` | The current state: expense 41 (Ada's team dinner) is still a draft |
| `plan-draft-1.steps.json` | The agent's first plan: reimburse expense 41 directly |
| `plan-draft-2.steps.json` | The revised plan: approve, submit to Workday, then reimburse |
| `approve-41.steps.json` + `claimed-post.pop.yaml` | A walk that claims a post-state in which bystander expense 42 also flipped to `rejected` |
| `stand_in_agent.py` | A scripted stand-in for an agent, used by the offline session tutorial |
| `recordings/` | Real Claude Code, Codex and hosted-model sessions on one task, with their results |

```sh
gnd check model.orm.yaml --pre state.pop.yaml --steps plan-draft-1.steps.json   # exit 1
gnd check model.orm.yaml --pre state.pop.yaml --steps plan-draft-2.steps.json   # exit 0
gnd check model.orm.yaml --pre state.pop.yaml --steps approve-41.steps.json --post claimed-post.pop.yaml   # exit 1
```

The first plan fails the alethic precondition `pre_submitted` and warns on the
deontic `pre_has_approver`. The second computes the post-state and passes. The
third claims a post-state in which every fact is individually legal, so only
the frame check catches it.

The data is synthetic. The model is adapted from GND's transition test corpus.
