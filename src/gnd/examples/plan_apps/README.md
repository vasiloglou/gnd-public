# Plan apps

Five small apps whose bots answer a question with a plan of operations. GND
checks each plan, or the PyRel program GND generates from the model does; a
refused plan goes back to the bot with the failed rule, the step and the facts.

| App | Question |
|---|---|
| [course](course/README.md) | Plan Maya's spring semester. She really wants Machine Learning. |
| [access](access/README.md) | Give Bob access to payroll; Carol approves. |
| [lease](lease/README.md) | Set up the rent schedule for this lease. |
| [clinic](clinic/README.md) | Refill Sam's prescriptions today. |
| [trip](trip/README.md) | Plan three days in Lisbon under 900 EUR. |

`core.py` is shared: the ask, check, feed back and execute loop, both
checkers, and `rules`, which prints the model's rules as PyRel requirements.

## The bot interface

A bot is any command. It reads one JSON document on stdin:
`{question, rules, operations, state, attempts: [{plan, failures}]}`.
It answers on stdout in one of these forms:

| Answer | What the app does |
|---|---|
| `{"steps": [{"op": ..., "bindings": {...}}, ...]}` | checks the plan; on refusal, sends the failures back |
| the same, plus `"note": "..."` | prints the note ("CS340 must wait"), then checks the plan |
| `{"steps": [], "reason": "..."}` | the bot declines: prints the reason and stops |
| anything else, or no answer in time | counts a failed attempt and tells the bot why |

If the checker itself fails (exit 70), the app stops: the plan was not judged,
so there is nothing to feed back.

`tools/plan_app_bot.py` puts a real model behind this interface (Claude Code,
or a small model on OpenRouter). [recordings/](recordings/README.md) holds
every run of five models on the five questions.
