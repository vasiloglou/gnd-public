# Exports and a second opinion

Two kinds of independent evidence complement GND's own checker: **other engines**,
which evaluate the same model by different means, and **other models**, which review
a plan or an outcome.

## Hand the model to another engine

GND's engine is the portable default. `gnd export` writes standalone artifacts for
three external engines:

| Engine | Command | Use it for |
|---|---|---|
| [Soufflé](../runtimes/souffle.md) | `gnd export souffle`, `souffle-verify`, `souffle-run` | recursive derivations at scale, such as the transitive impact of a vulnerable dependency |
| [Lean](../runtimes/lean.md) | `gnd export lean`, `lean-verify`, `lean-compile` | finite definitions plus explicitly unproved obligations that you prove, or refute with a counterexample |
| [PyRel](../runtimes/pyrel.md) | `gnd export pyrel` | a standalone relational program, run locally on DuckDB or on Snowflake when your data lives there |

```text
Use gnd-export to export the approval policy model to Lean with the release population,
verify the bundle, and list the obligations it leaves unproved. Do not claim any
obligation is proved unless Lean checked a proof.
```

Exports are **evidence, not assurance**. A Soufflé run that agrees with GND locates no
disagreement. That is not a proof that either engine is right. Lean obligations stay
unproved until Lean checks a proof. The
[release governance tutorial](../runtimes/scenario.md) runs all three engines on one
model and explains what each result does and does not establish.

## Show your work: witnesses

For a derived fact, `gnd witness` produces a finite **derivation certificate**: the
grounded rule instances that justify the fact. `gnd replay` independently re-checks the
certificate against the model and population with a separate inference kernel. Values
are redacted in the default view:

```sh
gnd witness model.orm.json pop.json --targets targets.json --reference-root references
gnd replay  model.orm.json pop.json witness.json --reference-root references --json
```

See [exports and witnesses](../guides/exports.md) and the
[Python API](../reference/python-api.md) (`api.witness`, `api.replay`).

## Get a second opinion from six models

`gnd-review-panel` sends one plan, one experiment outcome, or one
spec/results/delta bundle to six reviewer seats across five CLIs: Claude Code, Codex,
Qwen Code, Gemini CLI and Kimi Code, plus a GLM seat that runs the Claude CLI against
Z.AI. The run counts only if at least **three** distinct reviews are schema-valid.

```text
Use gnd-review-panel-light on docs/PLAN.md with the rubric "Cite one concrete artifact
location for every concern; reject unbounded execution." Then synthesize the concerns
and finalize PANEL-REVIEW.md. Do not apply any fix.
```

1. The agent writes `review-request.json`, which binds each reviewed file by SHA-256 so
   that every reviewer reads the same bytes.
2. `gnd review panel` (or `panel-light`, at a lower effort) attempts all six seats and
   publishes one immutable evidence directory. Exit **16** means fewer than three valid
   reviews.
3. The agent groups the concerns into `synthesis.json`, and `gnd review finalize`
   validates it against the evidence and renders `PANEL-REVIEW.md`.

The panel is advisory. It keeps every failure and every dissent, and it never applies
a fix. Each seat needs that vendor's CLI and credentials; `gnd-update-review-panel`
maintains the roster.
