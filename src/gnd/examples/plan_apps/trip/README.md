# Trip planner

The rules in plain English (`rules.md`), the model built from them
(`model.orm.json`), the current state (`state.pop.json`), and a bot that answers
the question below with a plan of operations.

```text
python app.py rules
python app.py ask "Plan three days in Lisbon under 900 EUR." --out next.pop.json
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
| 1 | Palacio for three nights and three outings | `within_budget`: 900 for the hotel plus the outings is over 900 |
| 2 | Alfama Inn and four outings | `no_overlap`: the Sintra day trip and the Belém walk are both on 13 May in the morning |
| 3 | Alfama Inn, the Oceanarium instead of the Belém walk | accepted, and executed |

What this example exercises: aggregate sums with an arithmetic comparison, dates, uniqueness over a derived fact type.
