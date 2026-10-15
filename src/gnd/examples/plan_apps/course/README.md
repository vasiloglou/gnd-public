# Course planner

A registrar's rules (`rules.md`), the model built from them (`model.orm.json`),
Maya's record and the spring catalogue (`state.pop.json`), and a bot that
answers "plan this student's term" with a plan of `enroll` steps.

```text
python app.py ask "Plan Maya's spring semester. She really wants Machine Learning." --out next.pop.json
python app.py ask "..." --backend pyrel --out next.pop.json   # needs GND_PYREL_PYTHON
python app.py check plans/attempt-1.steps.json
```

`ask` runs the loop:
1. The bot proposes a plan.
2. GND, or the PyRel program GND generates, checks every step.
3. A refused plan goes back to the bot, with the failed rule or precondition,
   the step and the facts.
4. An accepted plan is executed: the state after it is written to `--out`.

`stand_in_bot.py` is a scripted bot, so this runs without a model provider. It
makes the documented three attempts:

| Attempt | Plan | Checker says |
|---|---|---|
| 1 | Machine Learning, Linear Algebra, Probability | `prerequisites_first`: Maya needs MATH220 and STAT210 passed first (states 1–3) |
| 2 | Linear Algebra, Probability, Databases | `pre_offered` fails at step 3: Databases isn't offered in spring |
| 3 | Linear Algebra, Probability, Logic | accepted, and executed |

The same model, with the PL15 corpus id, is
`tests/fixtures/pyrel-rules-plans/registrar.orm.json`.
