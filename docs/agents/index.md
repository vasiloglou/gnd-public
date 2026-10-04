# Skills + Python: who does what

**GND is skills plus Python code.** The skills tell a coding agent, such as Claude Code
or Codex, what to produce. The Python runtime checks what it produced. Neither half
trusts the other: a skill never declares its own work correct, and the checker never
writes your model or your application.

## The agent never delivers prose as the result

Every skill ends in a structured artifact that `gnd` can check:

| Artifact | What it is | Checked by |
|---|---|---|
| `model.orm.yaml` | the executable ontology: object types, fact types, constraints, operations | `gnd validate` |
| `population.json` | facts the agent produced: recommendations, extracted records, a state | `gnd check`, `gnd verify` |
| `plan.steps.json` | a sequence of operations the agent proposes to execute | `gnd check --pre --steps` |
| `session.contract.json` | what counts as acceptance for a bounded agent session | `gnd exp validate`, `gnd exp run` |
| `proposal.json` | a requested change to the model | `gnd evolve preview` |
| extraction sidecar, document manifest | provenance for facts read from, or written into, documents | `gnd verify`, `gnd doccheck` |
| generated project | model-derived tools plus your extension code | `gnd conformance` |

GND checks these with its own deterministic engine, which is portable native Python
and needs no database or service. For recursive analysis, proofs or enterprise data,
`gnd export` hands the same model to [Soufflé](../runtimes/souffle.md),
[Lean](../runtimes/lean.md) or [PyRel](../runtimes/pyrel.md). PyRel runs locally on
DuckDB or on Snowflake; the public build measures the DuckDB route.

## Every skill, by outcome

| Ask your agent to… | Skill | It writes | Then GND runs | The exit that matters |
|---|---|---|---|---|
| Model a new domain through a guided dialogue | `gnd-model-from-text` | `model.orm.yaml`, `model.verbalization.txt` | `gnd validate` | 0 valid, 3 invalid |
| Recover a model from an existing codebase | `gnd-model-from-code` | model, verbalization, `model.recovery.json` | `gnd recovery verify` | 0 every claim verified |
| Migrate a GSD project's requirements | `gnd-adopt` | recovered model + `model.migration.json` | `verify_migration.py` | 0 every requirement accounted for |
| Open GND planning in a repository | `gnd-new-project` | `.gnd-planning/PROJECT.md` | none | |
| Generate the project and write the extension | `gnd-codegen` | derived tools + extension files | `gnd codegen`, `gnd conformance` | 11 refused overwrite, 13 drift |
| Check a generated project against its model | `gnd-conformance` | `conformance.json` evidence | `gnd conformance` | 0 aligned, 13 drift |
| Run a bounded agent session until the checker accepts | `gnd-dev-session` | `SPEC.md`, `session.contract.json`, conclusions | `gnd exp run`, `gnd exp close` | 0 accepted, 15 not accepted, 14 open |
| Change a rule, rename or delete an element | `gnd-model-evolve` | `proposal.json` | `gnd evolve preview`, `apply` | 13 published but a project drifts |
| Extract facts from a document | `gnd-extract` | `extracted.population.json` + sidecar | `gnd verify` | 0–4 verdict bands |
| Render a document from facts | `gnd-render-doc` | `document.md` + manifest | `gnd doccheck` | 0 obligations met |
| Export to Soufflé or Lean, or build a witness | `gnd-export` | export bundle, witness certificate | `gnd export … -verify`, `gnd replay` | 0 replayed |
| Get an independent multi-model review | `gnd-review-panel`, `gnd-review-panel-light` | `review-request.json`, `synthesis.json` | `gnd review panel`, `finalize` | 16 below quorum |
| Walk the whole loop, station by station | `gnd-solve` | station records | `gnd solve` | 17 walk halted |
| Look up the format, constraints or verbalization | `gnd-orm-core` | none (reference library) | | |
| Update the review panel's CLIs and models | `gnd-update-review-panel` | adapter changes (maintainers) | tests | |

Each skill's `SKILL.md` is in the
[packaged skill directory](https://github.com/vasiloglou/gnd-public/tree/main/src/gnd/skills).

## Why this works with smaller models

A deterministic checker turns "is this right?" from a judgment into a lookup. A cheap
model's plan is checked exactly like a frontier model's: a wrong one is rejected and
retried within a budget you set, and never trusted. A rule-level failure comes back
with the operation, the step and the outcome; it never contains the expected answer.

We recorded this. On one task, Claude Code, Codex and five hosted models of 8B to 24B were accepted
on their first attempt. Of the four models that did not always succeed first time, only
2 of 12 sessions were accepted on attempt 1 but 7 of 12 within three attempts, and a 3B
model never converged, which the checker reported as `stagnation` and `budget-exhausted`
instead of passing a bad plan. See [recorded agent sessions](recorded-sessions.md) for
the evidence and its limits. Cost is a separate question that we did not measure.

A [development session](dev-session.md) runs that loop with explicit limits and
explicit outcomes. The agent can be Claude Code, Codex, any command you declare, or any
OpenAI-compatible endpoint, including a small hosted or local model.

## Same checks from Python

Your application calls the same checker in-process through `gnd.api`. It has seven
stable functions:

| Function | Use it to |
|---|---|
| `api.validate(model)` | reject a malformed model before use |
| `api.check(model, population)` | check facts an agent or application produced |
| `api.transition(model, pre, steps, post=None)` | check a plan, or audit a walk with its claimed post-state |
| `api.verbalize(model, population)` | turn facts into sentences for a person or an agent |
| `api.diff(model_a, model_b)` | compare two versions of the rules |
| `api.witness(...)` / `api.replay(...)` | produce and independently replay a derivation witness |

See the [Python API reference](../reference/python-api.md) for signatures and runnable
examples.

## Make each handoff explicit

A skill can recommend another skill and cite its evidence, but it does not invoke the
sibling automatically. A passing check is not permission to change a model, and a drift
finding is not permission to regenerate code. State the next action you want and the
artifact it should use. Authorization you already gave for a named scope still applies;
the workflow should not invent another gate merely because a tool returned.

`gnd solve` is a separate command harness. It runs a selected sequence of CLI stations
with its own gating and log, but it does not author the model or implement your
application. See [the station walk](../walkthrough.md).

GND verifies the output, never the producer. A live agent or review session depends on
your configured tool and credentials. The tutorials need neither. A saved transcript
demonstrates its historical run only; replaying saved data does not imply a new provider
call.
