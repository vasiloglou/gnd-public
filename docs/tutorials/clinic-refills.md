# Refill prescriptions on a schedule

A pharmacy's rules are about time: how long since the last refill, which drugs
can't be given on the same day, when a patient is overdue. In this tutorial a
bot plans Sam's refills for a given day, and GND checks every date before
anything is dispensed. You'll also see the two kinds of rule GND treats
differently: a guideline it warns about, and a judgement it can't check at all.

It follows the [course planner tutorial](course-planner.md). Read that first if
you haven't: it shows Claude Code writing the model with
`/gnd:gnd-model-from-text`, which works the same way here.

## What you'll build

A folder with the pharmacy's rules, a model of them, Sam's prescriptions and a
bot that answers "refill this patient's prescriptions" with `refill_drug`
steps.

<!-- gnd-run expect=0 -->
```sh
python -c "import gnd, pathlib, shutil; shutil.copytree(pathlib.Path(gnd.__file__).parent / 'examples/plan_apps', 'plan_apps', ignore=shutil.ignore_patterns('recordings', 'skill-sessions', '__pycache__'), dirs_exist_ok=True)"
ls plan_apps/clinic
```

```text
README.md
app.py
model.orm.json
plans
rules.md
stand_in_bot.py
state.pop.json
```

## 1. Write the rules

**You get** `rules.md`:

```markdown
--8<-- "src/gnd/examples/plan_apps/clinic/rules.md"
```

There is no clock in this app. The date, 10 March 2024, is in `rules.md`, and
the bot writes a date into each refill step. The rules compare those dates with
the last refill, so a plan gets the same verdict whenever it is checked. Step 7
shows what this leaves open: no rule says a refill must be dated 10 March.

## 2. Model them

**You type**

```text
/gnd:gnd-model-from-text rules.md
```

The skill works as in the [course tutorial](course-planner.md#2-model-them).
The example ships the model it would write, and GND validates it:

<!-- gnd-run expect=0 -->
```sh
gnd validate plan_apps/clinic/model.orm.json
```

```text
OK: plan_apps/clinic/model.orm.json is a valid GND ORM model
```

## 3. Optional: read the rules as PyRel

As in the course tutorial, you can skip this step: GND's own checker needs no
PyRel. PyRel matters when the facts live in your data platform; see
[What PyRel is, and when you need it](../explanation/what-is-pyrel.md). The example app prints the rules that `gnd export pyrel`
generates:

<!-- gnd-run expect=0 -->
```sh
python plan_apps/clinic/app.py rules
```

```text
The rules as PyRel, generated from the model by `gnd export pyrel`. In a plan, every relation also
takes the state as its first argument: `step` is the state after a step, `before` the state before it.
These are the LQP program's requirements; the DuckDB program checks the same rules as violation queries.

Derived facts
  interacting_pair: Drug and Drug interact, either way round
    m.where(interacts(step, a, b)).define(interacting_pair_derived(step, a, b))
    m.where(interacts(step, b, a)).define(interacting_pair_derived(step, a, b))

Rules checked on every state
  one_last_refill: (must) A patient has one last refill per drug.
    m.where(last_refill(step, patient, drug, day_1), last_refill(step, patient, drug, day_2)).require(day_1 == day_2)
  refill_not_early: (must) A refill can't be given before the drug's refill interval has passed.
    m.where(refill(step, p, d, on), last_refill(step, p, d, last), refill_interval(step, d, n)).require(on >= std_date.add(last, days(n)))
  no_interacting_refills: (must) A patient never gets two drugs that interact on the same day.
    m.where(refill(step, p, a, on), refill(step, p, b, on), interacting_pair(step, a, b)).require(a == b)
  not_too_late: (should) A patient should not go more than 60 days between refills.
    m.where(refill(step, p, d, on), last_refill(step, p, d, last)).require(on <= std_date.add(last, days(60)))

Preconditions, checked on the state before each step
  pre_prescribed: Only prescribed drugs are refilled.
    m.where(do_refill_drug(step, patient, drug, on), previous(step, before)).require(prescribed(before, patient, drug))
```

| The pharmacist said | The kind of rule | What GND does with it |
|---|---|---|
| "before the drug's refill interval has passed since the last refill" | a date rule: `std_date.add(last, days(n))` | refuses the plan |
| "whichever way round the interaction is listed" | a derived fact read both ways | refuses the plan |
| "Only prescribed drugs are refilled" | a precondition of `refill_drug` | refuses the step |
| "should not go more than 60 days" | a guideline (should) | warns and accepts |
| "the pharmacist uses judgement" | a textual rule | lists it as not checked |

The judgement rule has no PyRel line. No program can check it, so GND keeps it
in the model and reports it as not checked on every plan, instead of quietly
leaving it out.

## 4. Ask the bot

**You type**

```text
Refill Sam's prescriptions today.
```

The right answer is not "refill everything". The statin isn't due until 21
March, and warfarin and aspirin interact, so only one of them can be given
today.

## 5. It proposes a plan

**The bot does**

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Llama 3.1 8B refills Sam's prescriptions (recorded run 1)">
--8<-- "docs/assets/replays/clinic-llama-3.1-8b-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/clinic-llama-3.1-8b-run-1.txt"
    ```

This is `llama-3.1-8b/clinic/run-1`, the first clinic run refused on a rule.
Llama 3.1 8B refills aspirin and the statin. Its note says it left warfarin out
because the refill interval had not passed. That is wrong: the interval rule is
about the statin, and warfarin is due.

## 6. GND checks it

**The checker says** the plan is refused at state 2, the state after the statin
refill. The recording used the app's optional PyRel backend, the DuckDB program
GND generates; GND's own checker gives this plan the same verdict:
`refill_not_early violated`. The witness shows the dates: last refill 20
February, interval 30 days, refill on 10 March. The judgement rule is listed as
not checked, as it is on every plan.

## 7. Repair, or not

The bot's second answer declines: it says the plan broke a rule about "two
drugs from the same class of reasons", which is not one of the pharmacy's
rules. No recorded clinic run was refused on a rule and then accepted, so this
page shows the refusal as it happened and makes no claim of a repair.

The Claude models were accepted at the first attempt in all ten runs, and nine
of those plans refilled one drug on 10 March. Here is one,
`claude-haiku/clinic/run-1`, with the note it wrote for the pharmacist:

<figure class="gnd-replay" tabindex="0" role="region" aria-label="Replay: Claude Haiku refills Sam's prescriptions (recorded run 1)">
--8<-- "docs/assets/replays/clinic-claude-haiku-run-1.svg"
</figure>

??? note "Transcript of the replay"

    ```text
    --8<-- "docs/assets/replays/clinic-claude-haiku-run-1.txt"
    ```

**Try the loop yourself** with the scripted stand-in bot. It is written to make
both mistakes and repair them from the feedback, so the repair you see here is
scripted, not a model's:

<!-- gnd-run expect=0 -->
```sh
python plan_apps/clinic/app.py ask "Refill Sam's prescriptions today." --out next-clinic.pop.json
```

```text
attempt 1
  plan  refill_drug(patient='sam', drug='statin', on='2024-03-10')
  plan  refill_drug(patient='sam', drug='warfarin', on='2024-03-10')
  plan  refill_drug(patient='sam', drug='aspirin', on='2024-03-10')
  gnd check: exit 1
    states 0-3  pharmacist_judgement  not checked  a textual rule: no checker can check it, so it is listed as not checked
    states 1-3  refill_not_early  violated  [{"$p": "sam", "$d": "statin", "$on": "2024-03-10", "$last": "2024-02-20", "$n": 30}]
      the rule in PyRel: m.where(refill(step, p, d, on), last_refill(step, p, d, last), refill_interval(step, d, n)).require(on >= std_date.add(last, days(n)))
    state 3  no_interacting_refills  violated  [{"$p": "sam", "$a": "aspirin", "$on": "2024-03-10", "$b": "warfarin"}, {"$p": "sam", "$a": "warfarin", "$on": "2024-03-10", "$b": "aspirin"}]
      the rule in PyRel: m.where(refill(step, p, a, on), refill(step, p, b, on), interacting_pair(step, a, b)).require(a == b)
attempt 2
  plan  refill_drug(patient='sam', drug='statin', on='2024-03-21')
  plan  refill_drug(patient='sam', drug='warfarin', on='2024-03-10')
  plan  refill_drug(patient='sam', drug='aspirin', on='2024-03-10')
  gnd check: exit 1
    states 0-3  pharmacist_judgement  not checked  a textual rule: no checker can check it, so it is listed as not checked
    state 3  no_interacting_refills  violated  [{"$p": "sam", "$a": "aspirin", "$on": "2024-03-10", "$b": "warfarin"}, {"$p": "sam", "$a": "warfarin", "$on": "2024-03-10", "$b": "aspirin"}]
attempt 3
  plan  refill_drug(patient='sam', drug='statin', on='2024-03-21')
  plan  refill_drug(patient='sam', drug='warfarin', on='2024-03-10')
  gnd check: exit 0 (accepted)
    states 0-2  pharmacist_judgement  not checked  a textual rule: no checker can check it, so it is listed as not checked
  executed: the new state is in next-clinic.pop.json
```

The tenth, `claude-haiku/clinic/run-3`, planned for the date of the computer it
ran on, 14 October 2026, instead of 10 March 2024. The checker
accepted it with two "late" warnings. That is a gap in this example's model,
not in the checker: no rule says a refill happens on 10 March, so any date after
the interval passes. To close it, record the day as a fact, add the rule to
`rules.md` and model it again.

All the recorded clinic runs:

| Model | Accepted at the first attempt | Refused in all attempts | Declined | Format repaired |
|---|---|---|---|---|
| Claude Haiku | 5 | 0 | 0 | 0 |
| Claude Code default | 5 | 0 | 0 | 0 |
| Llama 3.1 8B | 0 | 3 | 1 | 1 |
| Gemma 3 4B | 0 | 4 | 1 | 0 |
| Llama 3.2 3B | 2 | 3 | 0 | 0 |

## 8. See what GND warns about, and what it can't check

A plan that refills aspirin on 20 March, 65 days after the last refill, breaks
only the guideline:

<!-- gnd-run expect=0 -->
```sh
printf '%s\n' '{"steps": [{"op": "refill_drug", "bindings": {"patient": "sam", "drug": "aspirin", "on": "2024-03-20"}}]}' > late.steps.json
python plan_apps/clinic/app.py check late.steps.json
```

```text
gnd check: exit 0
  states 0-1  pharmacist_judgement  not checked  a textual rule: no checker can check it, so it is listed as not checked
  state 1  not_too_late  warning  [{"$p": "sam", "$d": "aspirin", "$on": "2024-03-20", "$last": "2024-01-15"}]
```

GND accepts it and says why it is late. The judgement rule is still listed as
not checked: a person has to decide that one, and the report says so.

## What you did

| Step | What happened | Who checked it |
|---|---|---|
| 1-3 | dated rules became a model; optionally, PyRel requirements over dates | `gnd validate`; `gnd export pyrel` |
| 4-6 | a small model's plan was refused at the step that refilled too early | GND, before anything was dispensed |
| 7 | the model declined for a reason that is not a rule; Claude got it right first time | GND checked every answer |
| 8 | a late refill was accepted with a warning; the judgement rule was reported as not checked | GND |

## Next steps

- [All recorded runs](../how-to/model-runs.md).
- [The course planner tutorial](course-planner.md).
