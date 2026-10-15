# Pharmacy refills

The rules in plain English (`rules.md`), the model built from them
(`model.orm.json`), the current state (`state.pop.json`), and a bot that answers
the question below with a plan of operations.

```text
python app.py rules
python app.py ask "Refill Sam's prescriptions today." --out next.pop.json
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
| 1 | statin, warfarin and aspirin today | `refill_not_early`: the statin's 30 days have not passed (20 February + 30 days = 21 March) |
| 2 | statin on 21 March, warfarin and aspirin today | `no_interacting_refills`: warfarin and aspirin interact |
| 3 | statin on 21 March, warfarin today | accepted, and executed |

What this example exercises: dates and durations (`date_add`), a multi-clause derived rule (an interaction either way round), a guideline (deontic) rule, a textual rule listed as not checked.
