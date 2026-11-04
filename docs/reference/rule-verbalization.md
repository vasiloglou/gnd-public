# Rule verbalization

`gnd.api.verbalize_rules(model, *, fact_types=None)` renders derived fact
types' rules in GND's controlled language. It reads the model only: no
population, no checker run, no LLM call.

## The payload

On success, `exit_code` is 0, and the payload is
`{"schema": "gnd-rule-verbalization/1", "exit_code": 0, "model_id": ..., "rules": [...]}`.
The shipped schema is `rule-verbalization.schema.json` in the `gnd` package.

Each entry in `rules` is one of:

- `{"fact_type", "status": "rendered", "text"}`. `text` is the sentence the
  full model verbalization prints after `This fact type is derived:` for that
  fact type, with the same escaping of control characters. The grammar's one
  home is the renderer in `gnd.model_verbalization`; this page does not restate
  it.
- `{"fact_type", "status": "unsupported", "reason": "prose-rule", "path": "/derivation_rule"}`
  for a rule written as prose rather than as a structured rule. The text is not
  rendered.

Entries come in fact-type id order. `fact_types` selects ids; duplicates are
ignored and `[]` returns no entries. `exit_code` stays 0 when some rules are
unsupported.

## Refusals

- A `fact_types` that is not a list or tuple of strings, or a model argument
  that is neither a path nor a loaded `Model`, raises `TypeError`.
- A model that does not load or validate, an in-memory `Model` that no longer
  validates, an id that names no fact type, or one that names a fact type
  without a rule, returns
  `{"schema": "gnd-rule-verbalization/1", "exit_code": 3, "error": {"kind": "input", "message": ...}}`.

A validated model never produces a partial rendering: every construct the
renderer cannot express is refused by validation first.

## Disclosure

Rules are model content, not population values, so the function emits the
same text in every disclosure mode (a `value-free` row in the
[disclosure table](disclosure.md)).
