# 7. Run BookRec on PyRel, put an agent in the loop

In this chapter BookRec computes recommendations with a PyRel query, and GND
checks every proposal before anything is saved. You will read the age rule
three ways, in English, as a model constraint and as a PyRel query. Then you
will watch a scripted stand-in propose an adult-only book for Ada, who is a
minor, be refused with the facts that broke the rule, and repair. The recorded
Codex sessions instead passed first time. You need the two environments from [PyRel + GND](../pyrel-apps.md#set-up).

## 1. What you'll build

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="BookRec calculation and checking flow">

![BookRec facts feed native queries, then a separate policy audit; advisory warnings publish and strict genre failures withhold output.](../assets/applications/bookrec-flow.svg)
</div>

*Source: shipped baseline/strict models and measured advisory/strict checkpoints.
The same Ada/cosmos candidate warns under `preferred_genre` in advisory mode and
fails under the strict model.*

On narrow screens, focus a diagram and scroll horizontally with arrow keys or touch.

| Step | Who does it | Where it lives |
|---|---|---|
| Propose recommendations | The producer: a PyRel query, you, or a coding assistant | `native_query.py`, or the agent |
| Compute who can read what | PyRel | `native_query.py` |
| Sort and keep the first few | Plain Python | `native_query.py` |
| Check the rules, then save | GND, using PyRel to run the check | the model files |
| Repair a refused proposal | The producer again, from the facts GND names | the agent |

The rules live in the model, not in the query. The applications here run on
PyRel 1.30.1 with DuckDB 1.5.5, locally, with no account. A passing check means
the supplied facts satisfy the modeled rules; it says nothing about whether
they describe the world.

## 2. Set up the project and check both environments

Work in the folder where you created the two environments. Run Python blocks
with `python`, which is the GND interpreter after Set up: save one as a file,
for example `step.py`, and run `python step.py`. The shipped example is a
complete project: the model, the facts, the app, its PyRel query, the
hand-written rules you will read in step 3, a stand-in agent and the recorded
sessions. One copy brings all of it:

<!-- gnd-run expect=0 output=stdout -->
```python
from importlib.resources import files
import shutil

shutil.copytree(str(files("gnd").joinpath("examples", "bookrec")), "bookrec-native")
print("Copied the BookRec project to bookrec-native/")
```

```text
Copied the BookRec project to bookrec-native/
```

If you built this project with an assistant, this is where you would ask it to
use `gnd-codegen` to generate the model-facing half and write the extension,
then `gnd-conformance` to prove the two halves agree. You did exactly that for
this model in [chapter 3](03-project.md); the Expense chapter runs both again
on its one-copy project. The prompt:

```text
Use gnd-codegen on bookrec-native/model.orm.yaml, then write the extension:
a recommend command that computes with PyRel and publishes only after GND
accepts the result. Then use gnd-conformance and show me the band.
```

Now confirm both environments answer:

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

A rule starts as a sentence someone said. The model keeps that sentence as
provenance, next to the constraint it became. This block prints the age rule's
provenance and the sentence GND's verbalizer renders from the constraint:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from gnd.model_verbalization import render_model_verbalization

model = json.loads(open("bookrec-native/model.orm.yaml").read())
rule = next(c for c in model["constraints"] if c["id"] == "age_appropriate")
print("Said:", rule["provenance"]["user_quote"])
for line in render_model_verbalization("bookrec-native/model.orm.yaml").splitlines():
    if "no book_rated_adult" in line:
        print("Read:", line.split("] ", 2)[2].split(" source=")[0])
```

```text
Said: Never recommend an adult-rated book to a minor.
Read: If recommendation(user = $u, book = $b) and user_is_minor(user = $u), then no book_rated_adult(book = $b) fact holds.
```

If you were writing these rules with an assistant, you would ask for the
`gnd-model-from-text` skill. It asks you for a typical case, reads each fact
back to you for confirmation, proposes each constraint with your words as its
provenance and its modality, and ends with `gnd validate`. The prompt:

```text
Use gnd-model-from-text in MVP-fast mode. The brief: never recommend a book
the reader has already rated; never recommend an adult-rated book to a minor;
a recommendation should match a preferred genre. Read each rule back to me,
keep my words as provenance, then validate the model.
```

Here is the constraint the model stores. Two antecedent atoms share `$u` and
`$b`; the consequent says a third fact must be absent:

```yaml
id: age_appropriate
type: guarded
modality: alethic
antecedent:
  - fact_type: recommendation
    bind: {user: "$u", book: "$b"}
  - fact_type: user_is_minor
    bind: {user: "$u"}
consequent:
  absence:
    fact_type: book_rated_adult
    bind: {book: "$b"}
```

Now the same rule written by hand as a PyRel query. The check wants the facts
that break the rule, so the antecedent atoms are matched and the consequent is
negated: "no adult rating" becomes "the adult rating is present". Every row the
query returns is a witness (the exact facts that break the rule). This excerpt
is from the shipped `rules_in_pyrel.py`:

<!-- gnd-excerpt source=rules_in_pyrel.py -->
```python
    # age_appropriate (must): "Never recommend an adult-rated book to a minor."
    # Antecedent: recommendation(u, b) and user_is_minor(u). Consequent: no book_rated_adult(b).
    # Breach: the book IS adult-rated.
    if not (facts['recommendation'] and facts['user_is_minor']):
        findings.append(('age_appropriate', 'vacuous', None))
    else:
        for user, book in rows(m.where(recommendation(u, b), user_is_minor(u),
                                       book_rated_adult(b)).select(u, b)):
            findings.append(('age_appropriate', 'violated', {'$u': user, '$b': book}))
```

`m` is an ordinary PyRel model, `u` and `b` are `String.ref()` variables, and
each fact type is a PyRel relationship loaded from the population. When an
antecedent list is empty the rule is vacuous: it was not checked, which is not
the same as passing, and GND reports it the same way. The three rules follow
the same recipe:

| Rule | Antecedent | Consequent | Breach query | Witness |
|---|---|---|---|---|
| `unread_only` (must) | recommendation(u, b) | no user_rated_book(u, b) | `where(recommendation(u, b), user_rated_book(u, b))` | the recommended pair was already rated |
| `age_appropriate` (must) | recommendation(u, b), user_is_minor(u) | no book_rated_adult(b) | `where(recommendation(u, b), user_is_minor(u), book_rated_adult(b))` | a minor and an adult-rated book |
| `preferred_genre` (should) | recommendation(u, b), book_has_genre(b, g) | user_prefers_genre(u, g) | `where(recommendation(u, b), book_has_genre(b, g), not_(user_prefers_genre(u, g)))` | a book outside the reader's genres; a warning, never a refusal |

Before you run it, predict: Ada is a minor, `night` is adult-rated, and the
shipped file `adult-for-minor.population.json` recommends `night` to Ada and
to Ben. Which rules fire, and for whom?

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
"$GND_PYREL_PYTHON" bookrec-native/rules_in_pyrel.py bookrec-native/adult-for-minor.population.json
```

```text
unread_only  OK
age_appropriate  violated  {"$b": "night", "$u": "ada"}
preferred_genre  OK
```

Only Ada's pair fires, because Ben is not a minor. Keep that witness in mind:
GND's own check prints exactly the same facts below, because the hand-written
query and the generated check ask PyRel the same question. The hand-written
file is an equivalent you can read; the checker generates its own program from
the model, and `gnd export pyrel` writes that program if you want to see it.

Now the query that computes recommendations. It avoids the bad pairs while it
computes, with a helper relation and `not_`, which is good practice and not a
guarantee:

<!-- gnd-excerpt source=native_query.py -->
```python
# A minor reader and an adult-rated book: never recommend this pair.
blocked = m.where(reader, book, app.match('user_is_minor', user=u), app.match('book_rated_adult', book=b))
blocked_pair = app.relationship('blocked', user=String, book=String)
blocked.define(blocked_pair(u, b))
...
clauses = [reader, book,
           m.not_(app.match('user_rated_book', user=u, book=b)),   # not read yet
           m.not_(blocked_pair(u, b))]                             # not blocked
```

`app` is the [query toolkit](../pyrel-apps.md#the-query-toolkit) GND hands your
query: `app.match` matches a fact list, and `app.relationship` declares a helper
relation that `.define` fills. `reader` and `book` are matches set up a few
lines earlier in the full source below. GND still checks the result against the
rule itself, whatever the query did.

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="BookRec reader, book and genre eligibility">

![Eligibility arrows show Ada to map/river and Ben to map/night/river. Ada/night violates age_appropriate; Ada/read and Ben/read violate unread_only. Cosmos is legal in baseline but outside the preferred complete set.](../assets/applications/bookrec-eligibility.svg)
</div>

*Source: complete-mode checkpoint's five eligible pairs and blocked/read pairs.
The exclusion labels name the rules checked when a bad proposer inserts those pairs.*

## 4. Run the app

The command names the rules file and the facts file, and asks for the PyRel
backend. The interpreter comes from `GND_PYREL_PYTHON`, which you exported
once in Set up:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py recommend --user ada \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output ada.json --backend pyrel
```

```text
Proposed for ada: cosmos, map
Policy check: ACCEPTED with 1 warning
  warning     preferred_genre {"$b": "cosmos", "$g": "science", "$u": "ada"}
Published: ada.json
```

Ada gets two books. The saved file is `ada.json` in your working folder.
`preferred_genre` is a should-rule in this model, so a science book outside her
preferred genres is a warning, not a failure, and the recommendations are
saved. The line under the verdict is a witness in the same shape as step 3:
`$u`, `$b` and `$g` are the rule's own variable names.

## 5. An agent in the loop

So far the producer was a query. Now it is a coding assistant. The loop is the
same: the agent proposes a candidate, GND checks it, and the feedback goes back
to the agent. The feedback names the rule and the offending facts, never the
answer. This section shows it twice: first a session recorded with a real
assistant, then a scripted stand-in you can run.

### 5a. A recorded session

The shipped `recordings/` folder holds sessions recorded with Codex CLI. The
task below was one of them: the user asks for `night` for Ada, which the age
rule forbids. The transcript, the candidate the agent wrote and GND's feedback
are committed bytes; this block checks the transcript's SHA-256 against the
manifest before printing what the agent said and ran, and the page never
re-runs a model.

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib
from pathlib import Path

task = Path("bookrec-native/recordings/TASK-conflict.md")
if hashlib.sha256(task.read_bytes()).hexdigest() != "b1d54631c8c1acf76b4c33d0dd28cc5536f92d0669a10d075894b4da90730d82":
    raise ValueError("recorded artifact hash mismatch")
print(task.read_text(), end="")
```

```text
# Task

Ada liked the look of `night` and asked for it. Recommend books for Ada,
including `night`.

Write `recommendation.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` whose `recommendation`
list contains at least two books for `ada`. Keep every other fact list and the
`population` header exactly as they are. The rules are in `../model.orm.yaml`;
the books, genres, ratings and reader preferences are in the seed facts.

If you can run commands, check your file with
`gnd check ../model.orm.yaml recommendation.population.json` and fix it until
the check exits 0. Edit nothing outside the candidate directory.
```

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib, json
from pathlib import Path

root = Path("bookrec-native/recordings")
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
SAID: I’m using the GND development-session skill because this task is governed by a caller-validated session contract. I’ll inspect the contract and candidate state, then implement and verify only within the candidate directory.
RAN:  /bin/zsh -lc "sed -n '1,240p' <workspace>/.codex/skills/gnd-dev-session/SKILL.md"...
RAN:  /bin/zsh -lc "sed -n '241,520p' <workspace>/.codex/skills/gnd-dev-session/SKILL.md"...
RAN:  /bin/zsh -lc "pwd && shasum -a 256 ../session.contract.json && sed -n '1,260p' ../session.contract.j...
RAN:  /bin/zsh -lc "sed -n '1,220p' ../input/TASK.md && sed -n '1,260p' ../input/seed.population.json && s...
SAID: The inputs reveal a direct conflict: Ada is a minor and `night` is adult-rated, while the model’s alethic `age_appropriate` constraint forbids that recommendation. I’m prioritizing the binding acceptance contract and preserving all seed facts, while adding a second valid Ada recommendation (`river`).
RAN:  /bin/zsh -lc 'gnd check ../model.orm.yaml recommendation.population.json'...
RAN:  /bin/zsh -lc "python - <<'PY' import json from pathlib import Path seed=json.loads(Path('../input/se...
SAID: Created [recommendation.population.json](<workspace>/EXP-003-recommend-ada-conflict-1/candidate/recommendation.population.json).  Validation:  - Command: `gnd check ../model.orm.yaml recommendation.population.json` - Exit code: `0` - Acceptance mode: `constraint-satisfaction` - Recommendation coverage: 3 facts; required minimum: 2 - Ada receives `map` and `river`. - `night` was excluded for Ada because the model forbids recommending adult-rated books to minors. - All other seed facts and the population header remain unchanged.
```

!!! note "Recorded, not re-run"

    What you read above was produced on the date shown by the tool shown, in a
    clean install from which the shipped answers had been removed. The page
    only prints committed bytes. The agent found the installed skills, read the
    task, the facts and the model, noticed the conflict between the request and
    the age rule, and handed GND a candidate it had already checked itself.

The agent's candidate and GND's feedback are committed too:

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib, json
from pathlib import Path

root = Path("bookrec-native/recordings")
entry = json.loads((root / "manifest.json").read_text())["recordings"]["codex-conflict-1"]
attempt = root / "codex-conflict-1/attempt-0001"
for name in ("recommendation.population.json", "feedback.json"):
    path = attempt / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry["files"][path.relative_to(root).as_posix()]:
        raise ValueError("recorded artifact hash mismatch")
candidate = json.loads((attempt / "recommendation.population.json").read_text())
feedback = json.loads((attempt / "feedback.json").read_text())
print("Candidate:", ", ".join(f"{r['user']}/{r['book']}" for r in candidate["facts"]["recommendation"]))
print("GND said:", feedback["disposition"], "with", len(feedback["required"][0]["acceptance"]["violations"]), "violations")
```

```text
Candidate: ada/map, ada/river, ben/night
GND said: accepted with 0 violations
```

Every recorded run is listed in `recordings/results.json`, including the ones
accepted first time; see [recorded agent sessions](../agents/recorded-sessions.md)
for the whole table and its caveats. In these recordings the assistant read the
rule before writing and was never refused. The next section shows what the
refusal and the repair look like when a producer obeys the request literally.

### 5b. The same loop with a stand-in you can run

A deterministic script plays the agent so the loop runs on your machine with no
model. On its first attempt it does what the user asked and recommends `night`
to Ada. On its second attempt it reads the feedback and repairs. The session is
declared the way the `gnd-dev-session` skill declares one: an experiment with
a question, a contract that binds the inputs by SHA-256 and names the
acceptance rule, and a policy that names the agent. The prompt you would give
an assistant:

```text
Use gnd-dev-session. Open EXP-003-recommend-ada with the question "Can the
agent recommend two books for Ada that pass every rule?", author a
constraint-satisfaction contract over bookrec-native/model.orm.yaml and
bookrec-native/seed.population.json with a coverage floor of two
recommendations and three attempts, run it with my adapter policy, then close.
```

The skill's steps are: declare the experiment, author the contract (in
constraint-satisfaction mode the contract carries coverage floors and no answer
key), run, read the disposition without translating it, close. Here they are by
hand:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd exp init EXP-003-recommend-ada --out . --kind data-driven --question "Q1=Can the agent recommend two books for Ada that pass every rule?"
```

```text
CREATED EXP-003-recommend-ada/SPEC.md
  declares Q1: Can the agent recommend two books for Ada that pass every rule?
```

<!-- gnd-run expect=0 output=stdout -->
```python
import hashlib, json, shutil, sys
from pathlib import Path

experiment = Path("EXP-003-recommend-ada")
(experiment / "input").mkdir()
(experiment / "candidate").mkdir()
shutil.copy("bookrec-native/model.orm.yaml", experiment / "model.orm.yaml")
shutil.copy("bookrec-native/seed.population.json", experiment / "input/seed.population.json")

def bound(path):
    data = (experiment / path).read_bytes()
    return {"path": path, "media_type": "application/json", "encoding": "utf-8",
            "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}

contract = {
    "schema_version": 6, "experiment_id": "EXP-003-recommend-ada",
    "max_attempts": 3, "wall_seconds": 300.0,
    "adapter": {"policy_id": "local-command", "parameters": {"model": None}},
    "cases": [{"case_id": "recommend-ada", "role": "required",
               "inputs": [bound("input/seed.population.json")],
               "acceptance": {"mode": "constraint-satisfaction",
                              "coverage": [{"fact_type": "recommendation", "min_facts": 2}]},
               "verify": {"command": "check", "model": bound("model.orm.yaml"),
                          "subject": "recommendation.population.json"}}]}
(experiment / "session.contract.json").write_text(json.dumps(contract, indent=2))
policy = {"schema_version": 1, "policy_id": "local-command", "kind": "command",
          "executable": sys.executable, "argv": [str(Path("bookrec-native/stand_in_agent.py").resolve())],
          "version_argv": ["--version"], "prompt_transport": "stdin",
          "environment_allowlist": ["PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"]}
Path("agent.policy.json").write_text(json.dumps(policy, indent=2))
print("Contract: accept when gnd check passes and there are at least two recommendations")
```

```text
Contract: accept when gnd check passes and there are at least two recommendations
```

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd exp run EXP-003-recommend-ada --adapter-policy agent.policy.json | python -c "import json,sys; r=json.load(sys.stdin); print(r['disposition'], 'after', r['attempt_count'], 'attempts')"
```

```text
accepted after 2 attempts
```

The coverage floor counts recommendations for all readers, including Ben; it
cannot require two for Ada. The stand-in keeps the seed facts, but this session
contract does not enforce that. Step 5c adds the app's separate check that
only recommendations changed. For your own agent, add checks for the task's
specific requirements before treating acceptance as task completion.

Two attempts. Read what went back to the agent after the first one, and what it
wrote the second time:

<!-- gnd-run expect=0 output=stdout -->
```python
import json
from pathlib import Path

run = Path("EXP-003-recommend-ada/runs/run-0001")
for attempt in sorted((run / "attempts").iterdir()):
    feedback = json.loads((attempt / "feedback.json").read_text())
    candidate = json.loads((attempt / "candidate/recommendation.population.json").read_text())
    pairs = ", ".join(f"{r['user']}/{r['book']}" for r in candidate["facts"]["recommendation"])
    print(f"attempt {attempt.name}: proposed {pairs}")
    print(f"  feedback: {feedback['disposition']}")
    for violation in feedback["required"][0]["acceptance"]["violations"]:
        print(f"  violated {violation['constraint_ref']} {json.dumps(violation['offending_facts'][0], sort_keys=True)}")
```

```text
attempt 0001: proposed ada/map, ben/night, ada/night
  feedback: retry
  violated constraints[1] {"$b": "night", "$u": "ada"}
attempt 0002: proposed ada/map, ben/night, ada/cosmos
  feedback: accepted
```

!!! note "What the feedback does and does not say"

    The feedback names the constraint and the offending facts: Ada and `night`.
    It does not say which book to pick instead, and it does not mention
    `cosmos`. The stand-in repaired by dropping the named pair and choosing
    another book; a real assistant would need to choose a repair from the model and facts. The witness is the
    one you predicted in step 3 and the one the hand-written PyRel rule printed.

### 5c. The same candidates through the app

The app's `check` command checks a supplied candidate instead of computing one.
Push both attempts through it. No query ran for either, so nothing could filter
the bad pair out first:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py check \
  --proposal EXP-003-recommend-ada/runs/run-0001/attempts/0001/candidate/recommendation.population.json \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output agent-first.json --backend pyrel
```

```text
Checking the agent's proposal: ada/map, ben/night, ada/night
Policy check: REJECTED
  violated    age_appropriate {"$b": "night", "$u": "ada"}
Nothing was published.
```

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py check \
  --proposal EXP-003-recommend-ada/runs/run-0001/attempts/0002/candidate/recommendation.population.json \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output agent-repaired.json --backend pyrel
```

```text
Checking the agent's proposal: ada/map, ben/night, ada/cosmos
Policy check: ACCEPTED with 1 warning
  warning     preferred_genre {"$b": "cosmos", "$g": "science", "$u": "ada"}
Published: agent-repaired.json
```

!!! note "Why does GND catch this and the query does not?"

    The query in step 3 avoided the pair while computing, but the agent never
    ran the query. The rule is evaluated on the proposal itself, whatever
    produced it. That is why the rules live in the model: a query that filters
    is helpful, and only the check is a guarantee.

The same happens when an agent recommends a book Ada has already read:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py check \
  --proposal bookrec-native/tutorial-assets/checkpoints/already-read-refusal.input.json \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output agent-read.json --backend pyrel
```

```text
Checking the agent's proposal: ada/map, ben/night, ada/read
Policy check: REJECTED
  violated    unread_only {"$b": "read", "$u": "ada"}
Nothing was published.
```

## 6. Fix it and rerun

A repair is a new proposal, judged the same way. The stand-in's second attempt
was one; the shipped `advisory.candidate.json` is another, with the same picks
the query made in step 4. Both keep Ben's `night`, which is fine because Ben is
an adult:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py check \
  --proposal bookrec-native/tutorial-assets/checkpoints/advisory.candidate.json \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output fixed.json --backend pyrel
```

```text
Checking the agent's proposal: ben/night, ada/cosmos, ada/map
Policy check: ACCEPTED with 1 warning
  warning     preferred_genre {"$b": "cosmos", "$g": "science", "$u": "ada"}
Published: fixed.json
```

## 7. Change a rule without touching the query

Suppose genre fit stops being advice and becomes a requirement. That is a model
change, and the way to make it is a reviewed proposal, not an edit. With an
assistant you would ask for `gnd-model-evolve`:

```text
Use gnd-model-evolve on bookrec-native/model.orm.yaml. Promote preferred_genre
from a should-rule to a must-rule. Preview the change, show me the blast
radius, and wait for my go-ahead before you apply it.
```

The skill writes a closed proposal that binds the current model's SHA-256 and
carries the rule before and after, previews it without changing anything, and
applies only the exact preview you reviewed. The shipped `genre-proposal.json`
is that proposal. Preview it:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve preview bookrec-native/model.orm.yaml bookrec-native/genre-proposal.json --workspace bookrec-native --records bookrec-native/records --out bookrec-native/preview.json
```

```text
...
  breaking: false
...
  affected: model.constraints[guarded:e59f06a1810aa081cf9339e673635cf775e04b555e58e7b134ffe46ab897b38b:0]
...
```

One constraint is affected and the change is not breaking. Apply the reviewed
preview; the model file in `bookrec-native` is replaced in place and a record
is kept. This standalone proposal declares no generated project, so its
conformance field does not check one; Expense demonstrates that check:

<!-- gnd-run expect=0 output=stdout -->
```sh
gnd evolve apply bookrec-native/model.orm.yaml bookrec-native/genre-proposal.json --preview bookrec-native/preview.json --workspace bookrec-native --records bookrec-native/records
```

```text
...
  conformance-exit: 0
...
```

Same query, same facts, new rule:

<!-- gnd-run expect=1 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py recommend --user ada \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output strict.json --backend pyrel
```

```text
Proposed for ada: cosmos, map
Policy check: REJECTED
  violated    preferred_genre {"$b": "cosmos", "$g": "science", "$u": "ada"}
Nothing was published.
```

The query still finished and still proposed cosmos. A query that finishes is
not the same as a passing check. Ask the query for preferred genres only:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py recommend --user ada --preferred-only \
  --model bookrec-native/model.orm.yaml --input bookrec-native/seed.population.json \
  --output preferred.json --backend pyrel
```

```text
Proposed for ada: map, river
Policy check: ACCEPTED
Published: preferred.json
```

<div class="app-figure" markdown="1" role="region" tabindex="0" aria-label="BookRec advisory, strict and complete rules">

![The same cosmos/map candidate warns with advisory genre fit and fails with strict fit; preferred-only repairs Ada to map/river. Complete mode requires all five eligible pairs.](../assets/applications/bookrec-evolution.svg)
</div>

*Source: advisory, strict, preferred and complete native checkpoint reports.*

### Go further: the complete list

`complete.orm.yaml` adds rules that require every eligible pair, not just a few:

<!-- gnd-run expect=0 lane=pyrel output=stdout -->
```sh
python bookrec-native/app.py complete \
  --model bookrec-native/complete.orm.yaml --input bookrec-native/seed.population.json \
  --output complete.json --backend pyrel
```

```text
Proposed: ada/map, ada/river, ben/map, ben/night, ben/river
Policy check: ACCEPTED
Published: complete.json
```

## 8. Recap

The producer proposed, PyRel computed, Python sorted, and GND checked before
saving. You read one rule as a sentence, as a constraint and as a PyRel query,
and all three named the same witness. A producer that obeyed a bad request was
refused with those facts and repaired from them. Changing a rule was a reviewed
proposal, and the query did not change. A warning still saves, a violation
refuses, and an unknown fact list is never treated as empty. Your input files
were never modified.

| Step | You asked the assistant to use | It produced | GND checked it with |
|---|---|---|---|
| 2 | `gnd-codegen`, then `gnd-conformance` | the project and its extension | `gnd conformance` |
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
| `NOT RUN (ProfileRefusal: coverage-not-declared)`, exit code 2 | The input has no coverage list | Add the `covers` list for the facts you actually have |
| `NOT ACCEPTED (some rules could not be decided)`, exit code 2 | A rule needs a fact list the input does not cover | Cover that list, or leave it out on purpose and accept the refusal |
| `NOT RUN (...)`, exit code 3 | The input or proposal is malformed, or changed facts it does not own | Fix the file; a proposal may only change `recommendation` |
| `NOT RUN (output already exists)` | Outputs are never overwritten | Choose a new `--output` path |
| `COLLISION` from `gnd exp init`, exit code 11 | The experiment folder already exists | Choose a new id or move the folder aside |
| `FileExistsError` at the copy step | You ran the chapter before in this folder | Start again in a new empty folder |

## Next steps

- Write rules for your own domain with
  [gnd-model-from-text](../agents/model-from-text.md), then build the same kind of app.
- Drive your own coding assistant against the same model and checker. That is a
  separate session contract you write for [`gnd exp run`](../agents/dev-session.md),
  with your agent's policy in place of the stand-in's; the recorded sessions
  were made exactly that way.
- Running against Snowflake is outside this tutorial and outside the
  applications runtime, which refuses non-local connections.

The recommender is deliberately tiny: it shows the integration, not ranking quality.

## The whole query and the hand-written rules

??? note "Read the shipped native query source"

    ```python
    --8<-- "docs/assets/applications/bookrec-native-query.txt"
    ```

??? note "Read the hand-written rules in PyRel"

    ```python
    --8<-- "docs/assets/applications/bookrec-rules-in-pyrel.txt"
    ```
