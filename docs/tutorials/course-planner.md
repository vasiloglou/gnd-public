# Build a course planner that can't skip a prerequisite

You'll take a registrar's rules, written in plain English, and see Claude Code
turn them into a model. Then a bot plans a student's semester, and GND checks
every step of the plan before anything is enrolled. The bot in the replays is a
small model, so you'll see it get the plan wrong, read GND's feedback and fix
it. Every replay on this page is a recording of a real run, not a mockup. The
runs you can try yourself use a scripted stand-in bot, and say so.

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

This is a recorded session with Claude Haiku; the
[full session](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/skill-sessions/claude-haiku/run-1/turn-01.jsonl)
is in the repository. The skill read its own reference
pages, saw that `rules.md` was complete, and chose its one-shot mode.

Its first
model failed `gnd validate`: a reading named the wrong object type. It fixed
the model and validated again. In two of the other three recorded sessions,
the skill asked questions first and the scripted user answered. In the third,
Claude Code's default model also drafted at once. All four ended with a valid
model; the [session notes](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/examples/plan_apps/skill-sessions/README.md)
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

## 3. Read the rules as PyRel

Each rule in the model becomes a PyRel requirement. GND generates them from
the model; nobody writes them by hand.

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
the facts breaking them. That one ran every recorded plan on this page, and GND's
own checker gives each of those plans the same verdict.

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
step. In the recording the checker was the DuckDB program GND generates; the
commands you run below use GND's checker, which agrees.

It reports `prerequisites_first violated`, once for MATH220 and once for STAT210. Each
witness (the facts that break the rule) names the student, the course and the
prerequisite she has not passed.

The bot gets the rule's name, where it broke
and the facts: never the answer. The PyRel line under the failure is printed
for you, not sent to the bot.

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
student.
In Claude Code you would ask `/gnd:gnd-model-evolve` for the change. Here the
proposal it would write ships with the example, so you can preview it and
apply it yourself:

<!-- gnd-run expect=0 -->
```sh
cd plan_apps/course
gnd evolve preview model.orm.json credit-cap-proposal.json --workspace . --records records --out preview.json > /dev/null
gnd evolve apply model.orm.json credit-cap-proposal.json --preview preview.json --workspace . --records records > /dev/null && echo "applied"
```

```text
applied
```

The plan GND accepted in step 7 now breaks the new rule:

<!-- gnd-run expect=1 -->
```sh
python plan_apps/course/app.py check plan_apps/course/plans/attempt-3.steps.json
```

```text
gnd check: exit 1
  state 2  credit_cap  violated  [{"$student": "maya", "$total": 7, "$term": "spring"}]
  state 3  credit_cap  violated  [{"$student": "maya", "$total": 10, "$term": "spring"}]
```

Nobody edited the checker or the bot. The rule changed in one place, the
model, and the next check used it.

## What you did

| Step | What happened | Who checked it |
|---|---|---|
| 1-2 | rules in English became a model | `gnd validate` |
| 3 | each rule became a PyRel requirement | generated, not written |
| 4-6 | a small model's plan was refused, with the rule and the facts | GND, before anything ran |
| 7 | the repaired plan ran and wrote a new record | GND accepted it first |
| 8 | one rule changed; the old plan is now refused | the same check, new model |

## Next steps

- [All recorded runs](../how-to/model-runs.md): five models, five apps, every
  run kept.
- [PyRel: approval audits](../runtimes/pyrel.md): the generated programs, and
  what they refuse.
