# Access requests

The rules in plain English (`rules.md`), the model built from them
(`model.orm.json`), the current state (`state.pop.json`), and a bot that answers
the question below with a plan of operations.

```text
python app.py rules
python app.py ask "Give Bob access to payroll; Carol approves." --out next.pop.json
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
| 1 | grant Bob payroll | `pre_approved` fails at step 1: access needs an approval first |
| 2 | Carol approves, then grant | `approver_outside_the_chain`: Carol manages Bob through Dana (the chain is a recursive rule) |
| 3 | Erin approves, then grant | accepted, and executed |

What this example exercises: recursion (the management chain), an exclusion over a derived fact type, a ring rule, a guarded comparison, a precondition.
