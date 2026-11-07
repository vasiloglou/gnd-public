# RC5 corpus: a population source for deterministic tool output

This corpus is the approval instrument for phase RC5 of the
`rule-check-adoption` milestone (spec:
`.gnd-planning/milestones/rule-check-adoption/notes/phase-RC5-spec.md`, §11).
It is committed before any implementation and fails until RC5 lands.
`tests/test_rc5_tool_output.py` runs every case from this directory as
`gnd check models/catalog.orm.yaml populations/<case>.pop.yaml --format json`.
This README tells each case's story; the answers are in
`expected/answers.json`.

## Why

A population that a script read from source code is not an agent's output,
synthetic data or a hand-written fixture, but those are the only three
labels today. RC5 adds `source: tool-output`, with an optional `producer`
naming the tool and the revision it read. The label changes nothing about
how the facts are checked.

## The model and the control

`models/catalog.orm.yaml`: components use components; no import loops.
`populations/fixture-control.pop.yaml` holds one edge, `cli -> core`, labelled
`fixture`. It passes today.

## The cases

1. **tool-output.** The control's facts labelled `tool-output`. It loads and
   checks exactly as the control does; only the population path differs in
   the report.
2. **tool-output-producer.** The same with `producer: "components-scan 1.4.0
   @ 9f3c2a1"`. It checks as the control does, and the loaded population
   keeps the producer text.
3. **producer-200.** A producer of exactly 200 characters: accepted.
4. **producer-on-fixture.** A producer on a `fixture` population: refused,
   because a producer belongs only to tool output.
5. **producer-empty.** An empty producer: refused.
6. **producer-too-long.** A producer of 201 characters: refused.
