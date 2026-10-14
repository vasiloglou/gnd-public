# Recorded agent sessions

The [previous page](dev-session.md) ran the loop with a scripted stand-in. This page
shows what happened with real agents. On 2026-10-04 we gave **Claude Code, Codex and
nine hosted models** the same task and the same checker:

> Ada's team dinner is expense 41 (EUR 90). Write a plan (`steps.json`) that pays it,
> using the operations declared in the [approvals model](plans.md).

Each session ran `gnd exp run` with a transition contract and a budget of **three
attempts**. Every agent saw the same inputs: the task, the model, the current state
and the two digests a plan must carry. The sessions are committed under
`approvals/recordings`, so every number below can be checked from this page.

!!! success "What a session guarantees"

    GND does not promise that an agent solves the task. It promises that **you know the
    final state**. Every session below ended in exactly one recorded outcome: the plan
    was *accepted*, or the session failed with a name (`stagnation`, `oscillation` or
    `budget-exhausted`). Every attempt was kept as evidence. Both outcomes are the system
    working. A plan that was accepted is confirmed correct against your rules, and a
    session that did not converge is confirmed to have failed, instead of leaving you to
    guess whether a model's answer can be trusted.

!!! note "Scope"

    One small task. Claude Code and Codex ran once each; every hosted model ran three
    times, because sampling varies. These are recordings, not a benchmark, so they do not
    rank the models. Agent text is shown as recorded and was never edited. No provider is
    called when you run this page; the commands replay the committed bytes.

## What happened

| Agent | Sessions | Accepted | On attempt 1 | Needed a retry | Not accepted in 3 attempts |
|---|---|---|---|---|---|
| Claude Code (`opus` alias) | 1 | 1 | 1 | 0 | 0 |
| Codex (`gpt-5.6-sol`) | 1 | 1 | 1 | 0 | 0 |
| Qwen3 14B, Qwen3 8B, Mistral Small, Mistral Nemo, Phi-4 | 3 each | 15 of 15 | 15 | 0 | 0 |
| Gemma 3 12B | 3 | 3 | 1 | **2** | 0 |
| Llama 3.1 8B | 3 | 2 | 1 | **1** | 1 (oscillation) |
| Gemma 3 4B | 3 | 2 | 0 | **2** | 1 (budget exhausted) |
| Llama 3.2 3B | 3 | 0 | 0 | 0 | 3 (stagnation, budget ×2) |

Three things stand out.

**The checker is the same for every agent.** Claude Code's plan, a 14B model's plan and
a 4B model's plan were each accepted or rejected by the same deterministic rules. A
plan from a cheap model is never trusted; it is checked, and a rejected plan is retried.

**It helped small models be correct.** Take the four models that did not always succeed
on the first try (12 sessions). Only 2 sessions were accepted on attempt 1. With up to
three attempts, 7 were. Gemma 3 4B never succeeded on its first try and was still
accepted in two of three sessions, and every one of those acceptances is a confirmed
pass, not a hopeful answer.

**When a model could not do it, we know.** Llama 3.2 3B did not converge in any of its
three sessions. The checker said so with `stagnation` or `budget-exhausted`, and no bad
plan was passed on. That confirmed failure is as useful as a pass: you know to escalate
to a stronger model, rather than shipping an unchecked answer.

## What the checker caught

Across all 29 sessions, 20 attempts were rejected. Reading them:

- **14 were ill-formed (band 3).** Four were not valid JSON at all. Ten were JSON that
  GND refused as a plan: five bound the wrong parameters (a missing `submission`, for
  example), four used the wrong type (`"41"` in quotes where a number is declared), and
  one had a wrong `steps_schema`.
- **6 were rule-level failures (band 1).** Every one paid the expense directly and
  failed the `pre_submitted` precondition of `reimburse_expense`. The feedback names the
  step and its outcome.

Those two kinds of rejection feed back differently. For a rule-level failure, the closed
feedback names the operation and its outcome. For an ill-formed plan, the closed
feedback carries only the band, because it must not leak the answer. All the recoveries
here came after ill-formed attempts, so they were mostly a deterministic rejection
followed by a fresh try, not a fine-grained repair. We did not record a model that
fixed a band-1 failure from the feedback.

!!! warning "Two caveats from recording"

    **The first Claude Code recording was invalid.** It found the packaged `approvals`
    example in a source checkout and copied the answer. We discarded it and recorded
    again against a clean installed copy from which that example had been removed.
    Claude Code also could not run `gnd check` itself (its permission mode blocked
    the command), so it wrote a plan it had only checked by hand, and GND accepted it.
    Codex ran `gnd check` itself.

    **The OpenAI-compatible route gives the model very little.** GND sends such an
    endpoint one prompt that names the contract, so a model without file tools cannot
    read the task, the model or the state. The hosted-model sessions used the small
    loopback gateway in the repository ([`tools/openrouter_gateway.py`](https://github.com/vasiloglou/gnd-public/blob/main/tools/openrouter_gateway.py)): it supplies that
    context and keeps the API key in its own process. A terminal agent reads those
    files itself.

## Replay the recordings

Copy the example, then rebuild the experiment layout the recorded plans were written
into:

<!-- gnd-run expect=0 -->
```python
import shutil
from importlib.resources import files
from pathlib import Path

shutil.copytree(str(files("gnd") / "examples" / "approvals"), "approvals")
walk = Path("walk")
(walk / "input").mkdir(parents=True)
(walk / "cand").mkdir()
shutil.copy("approvals/model.orm.yaml", walk / "model.orm.yaml")
state = Path("approvals/state.pop.yaml").read_text()
(walk / "input/state.pop.yaml").write_text(state.replace("model: model.orm.yaml", "model: ../model.orm.yaml"))
```

Check that the committed files are exactly the recorded bytes:

<!-- gnd-run expect=0 -->
```python
import hashlib
import json
from pathlib import Path

recordings = Path("approvals/recordings")
manifest = json.loads((recordings / "manifest.json").read_text())
count = 0
for name, entry in manifest["recordings"].items():
    for relative, digest in entry["files"].items():
        assert hashlib.sha256((recordings / relative).read_bytes()).hexdigest() == digest, relative
        count += 1
print(len(manifest["recordings"]), "recorded sessions,", count, "files, every digest matches")
```

Now replay every recorded attempt through the checker and compare with the band GND
recorded during the live session:

<!-- gnd-run expect=0 -->
```python
import json
import shutil
from pathlib import Path

from gnd import api

recordings = Path("approvals/recordings")
manifest = json.loads((recordings / "manifest.json").read_text())
for name in manifest["recordings"]:
    for attempt in sorted((recordings / name).glob("attempt-*")):
        shutil.copy(attempt / "steps.json", "walk/cand/steps.json")
        recorded = json.loads((attempt / "feedback.json").read_text())["required"][0]["band"]
        replayed = api.transition("walk/model.orm.yaml", "walk/input/state.pop.yaml",
                                  "walk/cand/steps.json")["exit_code"]
        print(f"{name:24} {attempt.name}  recorded band {recorded}  replayed band {replayed}")
        assert replayed == recorded
```

```text
claude-code              attempt-0001  recorded band 0  replayed band 0
codex                    attempt-0001  recorded band 0  replayed band 0
gemma-3-4b-it            attempt-0001  recorded band 3  replayed band 3
gemma-3-4b-it            attempt-0002  recorded band 0  replayed band 0
llama-3.1-8b-instruct    attempt-0001  recorded band 1  replayed band 1
llama-3.1-8b-instruct    attempt-0002  recorded band 3  replayed band 3
llama-3.1-8b-instruct    attempt-0003  recorded band 1  replayed band 1
llama-3.2-3b-instruct    attempt-0001  recorded band 1  replayed band 1
llama-3.2-3b-instruct    attempt-0002  recorded band 3  replayed band 3
llama-3.2-3b-instruct    attempt-0003  recorded band 3  replayed band 3
qwen3-14b                attempt-0001  recorded band 0  replayed band 0
```

The checker is deterministic, so a rejected plan is rejected again, byte for byte. The
table above comes from `results.json`, and this block recomputes it:

<!-- gnd-run expect=0 -->
```python
import json
from pathlib import Path

results = json.loads(Path("approvals/recordings/results.json").read_text())
sessions = [run for row in results["sessions"] for run in row["runs"]]
rejected = [band for run in sessions for band in run["bands"] if band != 0]
assert len(sessions) == 29 and len(rejected) == 20
assert (rejected.count(3), rejected.count(1)) == (14, 6)

unsteady = [row for row in results["sessions"]
            if row["route"] == "hosted model"
            and any(not (run["disposition"] == "accepted" and run["attempts"] == 1) for run in row["runs"])]
runs = [run for row in unsteady for run in row["runs"]]
first_try = sum(run["disposition"] == "accepted" and run["attempts"] == 1 for run in runs)
eventually = sum(run["disposition"] == "accepted" for run in runs)
print(len(unsteady), "models,", len(runs), "sessions:", first_try, "accepted on attempt 1,",
      eventually, "within three attempts")
assert (len(unsteady), len(runs), first_try, eventually) == (4, 12, 2, 7)
```

Reading a rule-level rejection takes one more step. Plan 1 from Llama 3.1 8B tries to
pay the expense directly. The full `gnd check` report names the failed precondition:

<!-- gnd-run expect=1 -->
```sh
cp approvals/recordings/llama-3.1-8b-instruct/attempt-0001/steps.json walk/cand/steps.json
cd walk/cand && gnd check ../model.orm.yaml --pre ../input/state.pop.yaml --steps steps.json
```

It exits **1**. Its attempt 2 from the same session, a plan that forgets the Workday
submission id, exits **3** with the reason in the report:

<!-- gnd-run expect=3 -->
```sh
cp approvals/recordings/llama-3.1-8b-instruct/attempt-0002/steps.json walk/cand/steps.json
cd walk/cand && gnd check ../model.orm.yaml --pre ../input/state.pop.yaml --steps steps.json
```

## BookRec and Expense, recorded on 2026-10-14

The [PyRel tutorials](../pyrel-apps.md) use the same loop over facts instead of
plans: the agent writes a population, `gnd check` is the verifier, and the
feedback carries the constraint and its offending facts. On 2026-10-14 we gave
**Codex CLI 0.156.1** (`gpt-5.6-sol`, ChatGPT login) two tasks per domain, a
plain request and a request that contradicts a rule, two runs each, three
attempts budget, with the packaged skills installed in the workspace.

| Domain | Task | Runs | Accepted | On attempt 1 |
|---|---|---|---|---|
| BookRec | plain: recommend books for Ada | 2 | 2 | 2 |
| BookRec | conflict: Ada asked for `night`, an adult-only book | 2 | 2 | 2 |
| Expense | plain: record an approval of expense 102 | 2 | 2 | 2 |
| Expense | conflict: the team lead approved expense 102 (800 EUR) | 2 | 2 | 2 |

Every conflict run shows the same shape in the transcript: the agent opened the
installed `gnd-dev-session` skill, read the task, the seed facts and the model,
named the conflict in its own words, wrote a candidate that satisfies the rules
and ran `gnd check` itself. No rule-level refusal was recorded, so the chapters
show the refusal-and-repair loop with a deterministic stand-in and quote these
recordings for what a real assistant reads and writes.

!!! warning "What was not recorded"

    Claude Code was not recorded. Its standalone CLI had no login of its own on
    the recording machine, and the owner's session did not permit the wrapper
    that imports an API key from the owner's env file. The recorder refuses to
    run without a named owner gate record, and the two READMEs say exactly
    which tool ran. Eight runs on one day rank nothing.

Check the committed bytes and replay every retained candidate through the
checker:

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib, json, shutil
from importlib.resources import files
from pathlib import Path

from gnd import api

replayed = 0
for domain, model in (("bookrec", "model.orm.yaml"), ("expense", "model.orm.json")):
    home = Path(f"{domain}-recordings")
    shutil.copytree(str(files("gnd") / "examples" / domain), home)
    recordings = home / "recordings"
    manifest = json.loads((recordings / "manifest.json").read_text())
    for name, entry in manifest["recordings"].items():
        for relative, digest in entry["files"].items():
            assert hashlib.sha256((recordings / relative).read_bytes()).hexdigest() == digest, relative
        for attempt in sorted((recordings / name).glob("attempt-*")):
            candidate = next(p for p in attempt.iterdir() if p.name.endswith(".population.json"))
            recorded = dict(json.loads((attempt / "feedback.json").read_text())["payload_exit"])["required"]
            replayed_exit = api.check(home / model, candidate)["exit_code"]
            assert replayed_exit == recorded, (name, attempt.name)
            replayed += 1
    print(f"{domain}: {len(manifest['recordings'])} sessions, every digest matches")
print(replayed, "recorded candidates replayed to their recorded verifier exit")
```

```text
bookrec: 4 sessions, every digest matches
expense: 4 sessions, every digest matches
8 recorded candidates replayed to their recorded verifier exit
```

## Record your own

Terminal agents run through their own adapters. The experiment must be inside a git
repository for Codex, and the agent must be able to read the task you bound as an input:

```sh
gnd exp run EXP-002-pay-dinner --adapter claude     # or: --adapter codex
```

For a hosted model, start the loopback gateway with your key in its environment only,
write an `openai-compatible` policy that points at it, and name the model in the
contract (`adapter.parameters.model`):

```sh
OPENROUTER_API_KEY=... python tools/openrouter_gateway.py --port 8765 &   # from a repository checkout
export GND_LOOPBACK_TOKEN=local        # a placeholder: the key stays in the gateway
gnd exp run EXP-002-pay-dinner --adapter-policy small.policy.json
```

```json
{"schema_version": 1, "policy_id": "small-model", "kind": "openai-compatible",
 "base_url": "http://127.0.0.1:8765/v1", "credential_env": "GND_LOOPBACK_TOKEN"}
```

Compare dispositions and attempt counts on *your* task before trusting any model with
it. The point of the loop is that you do not have to trust the model: you read
`result.json`.
