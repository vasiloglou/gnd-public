# Drive an agent against the verifier

A single `gnd check` tells you whether one answer is acceptable. A **development
session** turns that into a loop. The agent attempts the task, GND checks the result,
and closed feedback goes back for the next attempt. The loop stops at an explicit
outcome. Every attempt is kept as evidence.

This is where a deterministic checker pays for itself. The agent does not have to be
right the first time; it only has to *converge* within a budget. A wrong plan from a
cheap model is rejected and retried, never trusted, and the feedback never contains the
expected answer. [Recorded sessions](recorded-sessions.md) show how this played out for
real models on one task.

The `gnd-dev-session` skill guides your agent through authoring the contract, running
the session and closing the experiment. Below, the same steps run by hand. A scripted
stand-in plays the agent so that the page runs offline.

## Declare the question

Copy the [plan-checking example](plans.md) and open an experiment:

<!-- gnd-run expect=0 -->
```python
from importlib.resources import files
from shutil import copytree
copytree(str(files("gnd") / "examples" / "approvals"), "approvals")
```

<!-- gnd-run expect=0 -->
```sh
gnd exp init EXP-001-pay-dinner --out . --kind data-driven --question "Q1=Can the agent produce a plan that pays expense 41 and passes every precondition?"
```

`SPEC.md` now records the question. An experiment is closed only when every declared
question is answered or explicitly left unanswered with a reason.

## Write the session contract

The contract fixes everything before the agent starts: the inputs (bound by SHA-256),
the model, the verifier, what counts as acceptance, and the budget. This one says the
agent must write `steps.json` and that the walk must pass a transition check from the
current state, within three attempts:

<!-- gnd-run expect=0 -->
```python
import hashlib, json, shutil
from pathlib import Path

experiment = Path("EXP-001-pay-dinner")
(experiment / "input").mkdir()
(experiment / "candidate").mkdir()
shutil.copy("approvals/model.orm.yaml", experiment / "model.orm.yaml")
state = Path("approvals/state.pop.yaml").read_text().replace(
    "model: model.orm.yaml", "model: ../model.orm.yaml")
(experiment / "input/state.pop.yaml").write_text(state)

def bound(path):
    data = (experiment / path).read_bytes()
    return {"path": path, "media_type": "application/yaml", "encoding": "utf-8",
            "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}

contract = {
    "schema_version": 6,
    "experiment_id": "EXP-001-pay-dinner",
    "max_attempts": 3,
    "wall_seconds": 60.0,
    "adapter": {"policy_id": "local-command", "parameters": {"model": None}},
    "cases": [{
        "case_id": "pay-expense-41",
        "role": "required",
        "inputs": [bound("input/state.pop.yaml")],
        "acceptance": {"mode": "transition", "walk": None},
        "verify": {"command": "transition", "model": bound("model.orm.yaml"),
                   "pre": "input/state.pop.yaml", "steps": "steps.json", "post": None},
    }],
}
(experiment / "session.contract.json").write_text(json.dumps(contract, indent=2))
```

<!-- gnd-run expect=0 -->
```sh
gnd exp validate EXP-001-pay-dinner
```

Other acceptance modes cover other tasks: *exact bytes* when one answer is correct,
*constraint satisfaction* (with minimum fact counts) when many populations are
acceptable, *sealed tests* when the agent writes code, and *transition* walks with
required and forbidden operations. See [experiment sessions](../guides/experiments.md).

The same loop over facts instead of plans is in the PyRel tutorials. There the
contract's verifier is `gnd check`, acceptance is constraint satisfaction with a
coverage floor, and the feedback for a rule-level failure carries the constraint
and its offending facts, still without the answer. A stand-in asks for an
adult-only book for a minor, is refused with `{"$b": "night", "$u": "ada"}`, and
repairs; see [BookRec chapter 7](../bookrec/07-native.md#5-an-agent-in-the-loop)
and [Expense chapter 4](../expense/04-native.md#5-an-agent-in-the-loop).

## Choose the agent

The adapter policy names the agent. It is caller-trusted local configuration, kept out
of the experiment directory. Here the policy declares the packaged stand-in, a short
deterministic script that reads GND's prompt and feedback on stdin and writes
`steps.json`:

<!-- gnd-run expect=0 -->
```python
import json, sys
from pathlib import Path

policy = {
    "schema_version": 1,
    "policy_id": "local-command",
    "kind": "command",
    "executable": sys.executable,
    "argv": [str(Path("approvals/stand_in_agent.py").resolve())],
    "version_argv": ["--version"],
    "prompt_transport": "stdin",
    "environment_allowlist": ["PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"],
}
Path("agent.policy.json").write_text(json.dumps(policy, indent=2))
```

In real use the agent is Claude Code or Codex (`--adapter claude|codex` with older
contracts), or any command you declare, or any OpenAI-compatible endpoint. Using a
small model is covered [below](#use-a-small-model).

## Run the loop

<!-- gnd-run expect=0 -->
```sh
gnd exp run EXP-001-pay-dinner --adapter-policy agent.policy.json
```

Exit **0**: the session was accepted. The run directory records what happened:

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

run = Path("EXP-001-pay-dinner/runs/run-0001")
result = json.loads((run / "result.json").read_text())
print(result["disposition"], "after", result["attempt_count"], "attempts")
for attempt in sorted((run / "attempts").iterdir()):
    feedback = json.loads((attempt / "feedback.json").read_text())
    case = feedback["required"][0]
    steps = [(s["operation_id"], s["outcome"]) for s in case["steps"]]
    print(attempt.name, feedback["disposition"], "band", case["band"], steps)
assert result["disposition"] == "accepted" and result["attempt_count"] == 2
```

```text
accepted after 2 attempts
0001 retry band 1 [('reimburse_expense', 'violated')]
0002 accepted band 0 [('approve_expense', 'accepted'), ('submit_expense_to_workday', 'accepted'), ('reimburse_expense', 'accepted')]
```

Attempt 1 tried to pay directly and the walk was rejected at `reimburse_expense`. The
closed feedback, `feedback.json`, reports the band and each step's outcome. It carries
no prose, no file paths, no private bindings and no expected answer. Attempt 2 added
the approval and Workday steps and was accepted. Each attempt keeps its candidate,
verifier output, feedback and agent output under `attempts/NNNN/`.

## Know how a session can end

A session always ends in exactly one recorded disposition:

| Disposition | Exit | Meaning |
|---|---|---|
| `accepted` | 0 | every required case met its acceptance mode |
| `budget-exhausted` | 15 | `max_attempts` or `wall_seconds` ran out first |
| `stagnation` | 15 | the agent repeated its previous attempt: same candidate, same verdict |
| `oscillation` | 15 | the agent returned to an earlier attempt's candidate and verdict, so it is cycling |
| `agent-failure` | 15 | the agent process failed or wrote nothing usable |
| `verifier-failure` | 15 | the verifier could not produce a verdict |

Give the same task a budget of one attempt and the session ends without acceptance:

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

path = Path("EXP-001-pay-dinner/session.contract.json")
contract = json.loads(path.read_text())
contract["max_attempts"] = 1
path.write_text(json.dumps(contract, indent=2))
```

<!-- gnd-run expect=15 -->
```sh
gnd exp run EXP-001-pay-dinner --adapter-policy agent.policy.json
```

Exit **15**, and `runs/run-0002/result.json` records `budget-exhausted`. Each run gets
its own directory; earlier evidence is never overwritten.

## Close the experiment

Record the answer and cite the evidence, then let GND check that nothing declared was
left unanswered:

<!-- gnd-run expect=0 -->
```python
from pathlib import Path

Path("EXP-001-pay-dinner/CONCLUSIONS.md").write_text("""---
id: EXP-001-pay-dinner
resolves:
  - id: Q1
    outcome: answered
    evidence: runs/run-0001/result.json
---
# Conclusions

Q1: yes, within three attempts. Attempt 1 was rejected at reimburse_expense;
attempt 2 added the approval and Workday steps and was accepted. With a budget
of one attempt the same task ends budget-exhausted (runs/run-0002).
""")
```

<!-- gnd-run expect=0 -->
```sh
gnd exp close EXP-001-pay-dinner
```

`close` is a completeness gate. It refuses with exit 14 while any declared question is
unresolved. It never grades the answer.

## Use a small model

Nothing in the loop depends on which model produces the candidate. To try a small or
local model, replace the stand-in with one of these:

- **A declared command.** A short script calls your model, asks it for `steps.json`
  given the prompt and feedback it receives on stdin, and writes the file. This route
  suits small models best, because your script controls the output format.
- **An OpenAI-compatible endpoint.** The policy declares `kind: openai-compatible`, an
  HTTPS `base_url` (or an IP-literal loopback address) and the *name* of the environment
  variable that holds the key. The contract names the model in `adapter.parameters.model`.
  The model must reply with one JSON file bundle; GND sends one request per attempt,
  follows no redirects and rejects tool calls. The request carries only a prompt that
  names the contract, so a model without file tools cannot read your task. Put a small
  gateway in front of it that supplies the context. The example ships one
  ([`tools/openrouter_gateway.py`](https://github.com/vasiloglou/gnd-public/blob/main/tools/openrouter_gateway.py)), and the
  [recorded sessions](recorded-sessions.md) used it with nine hosted models.

```json
{"schema_version": 1, "policy_id": "small-model", "kind": "openai-compatible",
 "base_url": "https://openrouter.ai/api/v1", "credential_env": "OPENROUTER_API_KEY"}
```

Keep everything else the same: the contract, the checker and the budget. Compare the
dispositions and attempt counts across models on *your* task. GND records them, but it
does not promise that any particular model converges. In the
[recorded sessions](recorded-sessions.md), five of nine hosted models were accepted on
the first attempt every time, three needed retries, and one never converged.

## Ask your agent to do it

```text
Use gnd-dev-session. Declare EXP-002 with the question "Can the agent write a plan
that pays every approved expense?", author a transition contract over
approvals/model.orm.yaml and approvals/state.pop.yaml with at most 4 attempts, run it
with my adapter policy at ~/policies/small-model.json, then write CONCLUSIONS.md from
result.json and close the experiment.
```

The skill writes `SPEC.md`, `session.contract.json` and `CONCLUSIONS.md`. Every claim
it makes about the outcome comes from `result.json` and the exit codes, not from its
own judgment.
