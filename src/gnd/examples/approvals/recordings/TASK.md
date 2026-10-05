# Task

Ada's team dinner is expense 41 (EUR 90). Reimburse it: Workday submission id
`WD-8041`, approver `alice`, amount 90, paid on 2026-10-05.

Write `steps.json` in the current directory (the candidate directory): a plan
that GND can walk from `input/state.pop.yaml` using the operations declared in
`model.orm.yaml`. Use only declared operations and bind exactly their parameters.
Values keep their declared types (an expense id is a JSON number).

Format:

```json
{"steps_schema": 1,
 "model": "../model.orm.yaml",
 "model_digest": "<model_digest below>",
 "operations_digest": "<operations_digest below>",
 "steps": [{"op": "<operation id>", "bindings": {"<parameter>": <value>}}]}
```

Digests to copy exactly:

- `model_digest`: `sha256:278b20b244428f78a095c7824b12b6ae9c120ce70a16a485f612f878a077588f`
- `operations_digest`: `sha256:cafc5788f0badcc78a9a10e4facd83a4f6b67d3208a749f78e32c6b9d9f20a25`

If you can run commands, check the plan with
`gnd check ../model.orm.yaml --pre ../input/state.pop.yaml --steps steps.json`.
Edit nothing outside the candidate directory.
