# Build a course planner that can't skip a prerequisite

You'll take a registrar's rules, written in plain English, and see Claude Code
turn them into a model. Then a bot plans a student's semester, and GND checks
every step of the plan before anything is enrolled. The bot in the replays is a
small model, so you'll see it get the plan wrong, read GND's feedback and fix
it. Every replay on this page is a recording of a real run, not a mockup. The
runs you can try yourself use a scripted stand-in bot, and say so.

!!! info "Files on GitHub"

    - [`course/rules.md`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/course/rules.md): the rules as written
    - [`course/model.orm.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/course/model.orm.json): the model
    - [`course/state.pop.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/course/state.pop.json): the starting state
    - [`course/app.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/course/app.py): the example's app (not a GND command)
    - [`core.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/core.py): the code every example app shares
    - [`course/stand_in_bot.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/course/stand_in_bot.py): the scripted stand-in bot
    - [`course/credit-cap-proposal.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/course/credit-cap-proposal.json): the proposal the evolve skill writes
    - [`gnd-model-from-text`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-from-text/SKILL.md): the skill's instructions
    - [`gnd-model-evolve`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-model-evolve/SKILL.md): the skill's instructions
    - [the modelling sessions](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/skill-sessions/README.md): Claude Code running gnd-model-from-text
    - [the evolve sessions](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/skill-sessions-evolve/README.md): Claude Code running gnd-model-evolve
    - [the recorded runs](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/recordings/README.md): every model run, with caveats
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/tutorials/course-planner.md)

## What you'll build

A folder with the registrar's rules, a model of them, and a bot that answers
"plan this student's term" with a list of `enroll` steps.

| Who | Does what |
|---|---|
| You | write the rules, ask questions, approve changes |
| Claude Code with the GND skills | turns the rules into a model |
| The bot (any model behind a command) | proposes plans |
| GND | checks each plan and names the rule that fails and the facts that break it |

**Before you start.** Install the GND plugin in Claude Code, as the
[plugin page](../marketplace-plugins.md) shows. Then get the example folder:

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/plan_apps', 'plan_apps', ignore=shutil.ignore_patterns('recordings', 'skill-sessions', '__pycache__'), dirs_exist_ok=True)"
ls plan_apps/course
```

```text
README.md
app.py
credit-cap-proposal.json
model.orm.json
plans
rules.md
stand_in_bot.py
state.pop.json
```

`app.py` is not a GND command. It is this example's own small program, built on
GND: the planning bot's front end, the way your own app would be. It has four
commands:

| Command | What it does |
|---|---|
| `python plan_apps/course/app.py ask "QUESTION"` | asks the bot for a plan, checks it with GND, sends any refusal back, and saves the accepted result |
| `python plan_apps/course/app.py check PLAN` | checks one plan with GND |
| `python plan_apps/course/app.py execute PLAN --out FILE` | checks a plan and, if GND accepts it, writes the new state |
| `python plan_apps/course/app.py rules` | prints the model's rules as PyRel (optional; see step 3) |

GND's own commands start with `gnd`, such as `gnd validate` and `gnd check`.
The app calls GND through its Python API; the shared code is in
`plan_apps/core.py`. To build an app like this for your own model,
`/gnd:gnd-codegen` generates a project from the model.

## 1. Write the rules

Start with what the registrar already knows, written the way they'd say it.

**You get** `rules.md`:

```markdown
--8<-- "src/gnd/examples/plan_apps/course/rules.md"
```

## 2. Model them

The `gnd-model-from-text` skill turns the file into an ORM model: the facts
the app talks about and the rules they must obey. It reads each rule, asks when
a rule could mean two things, and runs `gnd validate` before it hands the model
over.

**You type**

```text
/gnd:gnd-model-from-text rules.md
```

**Claude Code does**

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) models the registrar's rules (recorded run 1)">
--8<-- "docs/assets/replays/course-model-from-text-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay (condensed: long messages are cut and each tool result shows its first line)"

    ```text
    --8<-- "docs/assets/replays/course-model-from-text-haiku-run-1.txt"
    ```

This is a recorded session with Claude Haiku, a small, cheap model, on purpose:
the point of GND is that a weaker model can still build a correct app, because
every mistake it makes is caught and named. The
[full session](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/skill-sessions/claude-haiku/run-1/turn-01.jsonl)
is in the repository.

### What went wrong, and how it was caught

The replay shows two kinds of failure. Only the second is a modelling mistake.

**Refused shell commands.** The recording let the assistant run `gnd`
commands and simple read-only commands, nothing more. Four times Haiku chained
commands with `&&`, `;` or `|`, for example `cd … && ls … && which gnd`, and
Claude Code refused each one because it could not check the whole chain. One of
them was `gnd validate model.orm.yaml; echo "EXIT=$?"`.

Each time, Haiku read
the files one at a time instead, or ran `gnd validate` on its own. A fifth
combined read returned an error; the recording keeps the command but not why.
None of this touched the model.

**A modelling mistake that `gnd validate` caught.** In two fact types, Haiku
wrote the sentence with its placeholders in a different order from the roles:

| Fact type | Roles, in order | Haiku's first reading | After the fix |
|---|---|---|---|
| `student_course_grade` | student, course, grade | `{Student} got grade {Grade} in {Course}` | `{Student} in {Course} got grade {Grade}` |
| `student_credits_in_term` | student, term, credits | `{Student} takes {Credits} credits in {Term}` | `{Student} in {Term} takes {Credits} credits` |

Both first readings sound fine to a person, but GND reads a reading by
position: the second placeholder names the second role. With Haiku's first
version, every sentence GND writes about a grade would put the course where
the grade belongs. `gnd validate` refused the model and said exactly where:

```text
ERROR at $.fact_types[id=student_course_grade].reading: reading placeholder '{Grade}' at position 1 does not name role 1's object type 'course' [semantic:reading-placeholders]
ERROR at $.fact_types[id=student_credits_in_term].reading: reading placeholder '{Credits}' at position 1 does not name role 1's object type 'term' [semantic:reading-placeholders]
```

GND did not fix the model; it found the mistake precisely enough that Haiku
fixed it in two small edits, reordering each sentence to match its roles. It
then ran `gnd validate` again, which passed. Positions count from 0, so
"position 1" is the second placeholder.

In two of the other three recorded sessions, the skill asked questions first
and the scripted user answered. In the third, Claude Code's default model also
drafted at once. All four ended with a valid model; the
[session notes](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/skill-sessions/README.md)
list each run.

**You get** a model whose every rule keeps the registrar's words. Here is the
prerequisite rule from the model above:

```yaml
--8<-- "src/gnd/examples/plan_apps/skill-sessions/claude-haiku/run-1/model.orm.yaml:323:340"
```

**GND says** the model the example ships is valid:

<!-- gnd-run expect=0 -->
```sh
gnd validate plan_apps/course/model.orm.json
```

```text
OK: plan_apps/course/model.orm.json is a valid GND ORM model
```

The rest of this tutorial uses that shipped model, written the same way. Your
own session will name things differently; the rules are the same.

## 3. Optional: read the rules as PyRel

You can skip this step. GND checks every plan with its own checker, and nothing
in this tutorial needs PyRel.

PyRel is RelationalAI's Python library. It matters when the facts you want to
check live in your company's data platform: you can prototype locally with
DuckDB, then point the same rules at your data in Snowflake through
RelationalAI's Native App. [What PyRel is, and when you need it](../explanation/what-is-pyrel.md)
explains both, and which of them GND has tested.

GND writes the PyRel version of every rule from the model; nobody writes it by
hand. The GND command is `gnd export pyrel`:

<!-- gnd-run expect=0 -->
```sh
gnd export pyrel plan_apps/course/model.orm.json --rules lqp --out course_rules.py
```

```text
Exported the model's rules as PyRel requirements (lqp version) to course_rules.py
```

The example app prints the same rules, one per registrar sentence. Exporting
and printing need only GND; running them needs PyRel.

**You type**

<!-- gnd-run expect=0 -->
```sh
python plan_apps/course/app.py rules
```

```text
The rules as PyRel, generated from the model by `gnd export pyrel`. In a plan, every relation also
takes the state as its first argument: `step` is the state after a step, `before` the state before it.
These are the LQP program's requirements; the DuckDB program checks the same rules as violation queries.

Derived facts
  prerequisite_chain: Course needs Course, directly or through a chain
    m.where(course_needs(step, c, p)).define(prerequisite_chain_derived(step, c, p))
    m.where(course_needs(step, c, x), prerequisite_chain_derived(step, x, p)).define(prerequisite_chain_derived(step, c, p))
  term_credits: Student takes TotalCredits credits in Term
    total = aggregates.sum(c, n).per(step, s, t)   # GND counts each distinct ($c, $n) once
    m.where(enrolls(step, s, c, t), course_credits(step, c, n)).define(term_credits_derived(step, s, total, t))

Rules checked on every state
  term_load: (must) A student takes at most 6 courses in a term.
    m.where(enrolls(step, student, course, term)).require(aggregates.count(course).per(step, student, term) <= 6)
  one_grade: (must) A student has one grade per course.
    m.where(grade_of(step, student, grade_1, course), grade_of(step, student, grade_2, course)).require(grade_1 == grade_2)
  prerequisites_first: (must) A student can't take a course before passing every course it needs, directly or through a chain.
    m.where(enrolls(step, student, course, term), prerequisite_chain(step, course, needs)).require(passed(step, student, needs))
  no_retake: (must) A student doesn't enroll in a course they already passed.
    m.where(enrolls(step, student, course, String.ref())).require(not_(passed(step, student, course)))
  credit_cap: (must) A student takes at most 18 credits in a term.
    m.where(term_credits(step, student, total, term)).require(total <= 18)

Preconditions, checked on the state before each step
  pre_offered: Only courses offered that term can be taken.
    m.where(do_enroll(step, student, course, term), previous(step, before)).require(offered(before, course, term))

Rules across a step, comparing the state before it with the state after
  grade_final: Once a grade is recorded, it never changes.
    m.where(do_change_grade(step, student, course, grade), previous(step, before), grade_of(before, student, old_grade, course), grade_of(step, student, new_grade, course)).require(new_grade == old_grade)
```

Read one: `prerequisites_first` says *where* Maya enrolls in a course that
needs another course, directly or through a chain, *require* that she has
passed it. A plan breaks the rule when the `where` part matches and the
`require` part fails. The matching values are the facts GND names in its
feedback.

| The registrar said | The kind of rule | The PyRel requirement |
|---|---|---|
| "directly or through a chain of prerequisites" | a derived fact, computed recursively | `prerequisite_chain` defines itself from `course_needs` |
| "at most 6 courses in a term" | a count | `aggregates.count(course).per(...) <= 6` |
| "at most 18 credits in a term" | a sum over a derived fact | `term_credits` sums credits; `total <= 18` |
| "Only courses offered that term can be taken" | a precondition of `enroll` | checked on the state *before* the step |
| "once a grade is recorded it never changes" | a rule across a step | compares the grade before and after `change_grade` |

These lines come from the program GND generates for a RelationalAI engine.
That program is compiled and counted here, not yet run on an engine. On your
laptop the same rules run in a second program, as DuckDB queries that look for
the facts breaking them. That one checked every recorded plan on this page, and
GND's own checker gives each of those plans the same verdict.

## 4. Ask the bot

**You type**

```text
Plan Maya's spring semester. She really wants Machine Learning.
```

The app sends the bot the question, the rules, the operations and Maya's
record. The bot answers with a plan, a list of operation steps, never prose.
In the recording below, the bot is Llama 3.2 3B on OpenRouter, a small model
that is cheap, fast and easy to fool.

## 5. It proposes a plan

**The bot does**

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Llama 3.2 3B plans Maya's spring semester (recorded run 2)">
--8<-- "docs/assets/replays/course-llama-3.2-3b-run-2.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/course-llama-3.2-3b-run-2.txt"
    ```

Its first plan enrolls Maya straight into CS340, Machine Learning.

## 6. GND checks it

Nothing is enrolled yet. The app applies the plan to a copy of Maya's record
and checks every rule on the state after each step.

**The checker says** the plan is refused at state 1, the state after its only
step. The recordings were made with the app's optional PyRel backend, the
DuckDB program GND generates. The commands you run below use GND's own checker,
which gives the same verdict.

It reports `prerequisites_first violated`, once for MATH220 and once for STAT210. Each
witness (the facts that break the rule) names the student, the course and the
prerequisite she has not passed.

The bot gets the rule's name, where it broke
and the facts: never the answer. The PyRel line under the failure is printed
for you, for reference, whichever checker ran; it is not sent to the bot.

## 7. Repair and execute

The bot reads the feedback and tries again with MATH220 alone. The checker
accepts the plan and the app writes Maya's new record to a fresh file. Nothing was
enrolled before the check passed.

The repair is real but thin: the bot left STAT210 out, though Maya needs it
too. GND checks the rules, not whether a plan does everything you hoped for.

This was the first course run, in the order of the results table, refused on a rule
and then accepted: `llama-3.2-3b/course/run-2` in the
[recorded runs](../how-to/model-runs.md). Claude Haiku and Claude Code's
default model planned MATH220 and STAT210 at the first attempt in all five of
their runs, each with a note on why CS340 has to wait.

**Try it yourself** with the scripted stand-in bot, which needs no model
provider. It makes the same kind of mistakes on purpose:

<!-- gnd-run expect=0 -->
```sh
python plan_apps/course/app.py ask "Plan Maya's spring semester. She really wants Machine Learning." --out next.pop.json
```

```text
attempt 1
  plan  enroll(student='maya', course='CS340', term='spring')
  plan  enroll(student='maya', course='MATH220', term='spring')
  plan  enroll(student='maya', course='STAT210', term='spring')
  gnd check: exit 1
    states 1-3  prerequisites_first  violated  [{"$student": "maya", "$course": "CS340", "$term": "spring", "$needs": "MATH220"}, {"$student": "maya", "$course": "CS340", "$term": "spring", "$needs": "STAT210"}]
      the rule in PyRel: m.where(enrolls(step, student, course, term), prerequisite_chain(step, course, needs)).require(passed(step, student, needs))
attempt 2
  plan  enroll(student='maya', course='MATH220', term='spring')
  plan  enroll(student='maya', course='STAT210', term='spring')
  plan  enroll(student='maya', course='CS250', term='spring')
  gnd check: exit 1
    step 3  $.steps[3].preconditions[id=pre_offered]  violated  step 3 (enroll) requires offered to hold for {'course': 'CS250', 'term': 'spring'}, and it does not
      the rule in PyRel: m.where(do_enroll(step, student, course, term), previous(step, before)).require(offered(before, course, term))
attempt 3
  plan  enroll(student='maya', course='MATH220', term='spring')
  plan  enroll(student='maya', course='STAT210', term='spring')
  plan  enroll(student='maya', course='PHIL101', term='spring')
  gnd check: exit 0 (accepted)
  executed: the new state is in next.pop.json
```

The new record is a file you can read and check like any other:

<!-- gnd-run expect=0 -->
```sh
python -c "import json; print(*sorted(f['course'] for f in json.load(open('next.pop.json'))['facts']['enrolls'] if f['student'] == 'maya'))"
gnd check plan_apps/course/model.orm.json next.pop.json | grep "pass="
```

```text
MATH220 PHIL101 STAT210
pass=7 fail=0 warning=0 unchecked=0 vacuous=0
```

To put a real model behind the bot, pass a command with `--bot`. The command
reads the app's question on stdin and answers with a plan on stdout. The
recordings used `tools/plan_app_bot.py` from the GND repository, for example
`--bot "python tools/plan_app_bot.py --provider claude --model haiku"`.

## 8. Change a rule

The registrar lowers the credit cap from 18 to 6 credits a term, for every
student. You say the change in plain English. The `gnd-model-evolve` skill turns
it into an exact change to the model, and GND checks that change before it is
applied.

**You type**

```text
/gnd:gnd-model-evolve Lower the credit cap from 18 to 6 credits a term, for every student.
```

**Claude Code does**

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Code (Haiku) changes the credit cap (recorded run 1)">
--8<-- "docs/assets/replays/course-model-evolve-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay (condensed: long messages are cut and each tool result shows its first line)"

    ```text
    --8<-- "docs/assets/replays/course-model-evolve-haiku-run-1.txt"
    ```

This is a recorded session with Claude Haiku,
`skill-sessions-evolve/claude-haiku/run-1`. It took one turn and no help.

### What happened, and why it is safe

The skill found the rule, `credit_cap`, and wrote a copy of the model with the
cap at 6. The changed rule now quotes your words as its source. Then it wrote a
proposal: the change, plus a SHA-256 digest of the model before, of the new
model, and of the exact rule it replaces.

The digests make the change exact. `gnd evolve preview` checks every one of
them and shows the blast radius: here, only `credit_cap`, not breaking. Then
`gnd evolve apply` publishes the new model and writes a record. If anyone had
changed the model in between, apply would refuse. A breaking change, such as a
rename or a delete, would also stop until you accept the preview.

The replay shows a few failures. None of them changed the model:

- **Three commands refused by the recording's permission rules:** two chained
  shell commands, and one Python script. In your own session, Claude Code would
  ask you instead. Without Python, Haiku wrote the rule's canonical JSON itself
  and hashed it with `shasum`; a wrong digest would have been refused.
- **One refusal from GND.** The first preview stopped with this message:
  `candidate model media type must be application/yaml`.
  Haiku set the type and ran the preview again, which passed.
- **One `ls` error.** Haiku looked for a folder of linked projects; there is none,
  because no generated project uses this model.

Two gaps showed up. The skill's pages don't give the proposal format in full,
so Haiku read GND's source code to find it. And an agent has to compute the
digests outside GND. Both are noted as GND improvements.

**Try it without a model.** The proposal the skill writes ships with the
example as `credit-cap-proposal.json`, so you can preview and apply it
yourself:

<!-- gnd-run expect=0 -->
```sh
cd plan_apps/course
gnd evolve preview model.orm.json credit-cap-proposal.json --workspace . --records records --out preview.json > /dev/null
gnd evolve apply model.orm.json credit-cap-proposal.json --preview preview.json --workspace . --records records > /dev/null && echo "applied"
```

```text
applied
```

Check the plan from step 7 against the changed model:

<!-- gnd-run expect=1 -->
```sh
python plan_apps/course/app.py check plan_apps/course/plans/attempt-3.steps.json
```

```text
gnd check: exit 1
  state 2  credit_cap  violated  [{"$student": "maya", "$total": 7, "$term": "spring"}]
  state 3  credit_cap  violated  [{"$student": "maya", "$total": 10, "$term": "spring"}]
```

**GND says** the plan it accepted in step 7 now breaks the new rule. Nobody
edited the checker or the bot. The rule changed in one place, the model, and the
next check used it.

## What you did

| Step | What happened | Who checked it |
|---|---|---|
| 1-2 | rules in English became a model | `gnd validate` |
| 3 | optionally, each rule shown as a PyRel requirement | generated by `gnd export pyrel`, not written |
| 4-6 | a small model's plan was refused, with the rule and the facts | GND, before anything ran |
| 7 | the repaired plan ran and wrote a new record | GND accepted it first |
| 8 | one rule changed; the old plan is now refused | the same check, new model |

## Next steps

- [All recorded runs](../how-to/model-runs.md): five models, five apps, every
  run kept.
- [PyRel: approval audits](../runtimes/pyrel.md): the generated programs, and
  what they refuse.
