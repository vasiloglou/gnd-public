# Rent schedule

The rules in plain English (`rules.md`), the model built from them
(`model.orm.json`), the current state (`state.pop.json`), and a bot that answers
the question below with a plan of operations.

```text
python app.py rules
python app.py ask "Set up the rent schedule for this lease." --out next.pop.json
python app.py ask "..." --backend pyrel --out next.pop.json   # needs GND_PYREL_PYTHON
```

`ask` runs the loop:
1. The bot proposes a plan.
2. GND, or the PyRel program GND generates, checks every step.
3. A refused plan goes back to the bot, with the rule, the step and the facts.
4. An accepted plan is executed.

`stand_in_bot.py` is a scripted bot that makes the documented attempts:

| Attempt | Plan | Checker says |
|---|---|---|
| 1 | six payments from 1 January | `due_after_start`: the lease starts on 1 February |
| 2 | six payments from 1 February | accepted, and executed |

What this example exercises: dates, guarded comparisons with `date_sub`, uniqueness, a guideline (deontic) rule. Reading the lease document and anchoring each extracted fact to its sentence is GND's `gnd extract` and `gnd verify`, on GND only.
