# GND · Get Nick Done

**Build agentic data apps that check themselves.**

*Inspired by the success of [GSD (Get Shit Done)](https://github.com/gsd-build/get-shit-done)
for traditional software development, GND is its lighter sibling, built specifically
for agentic data apps.*

GND turns requirements into an **executable ontology**: an
[Object-Role Modeling (ORM)](https://www.orm.net/) model of facts, rules and constraints. That
model is the intermediate representation for the verifier, the synthetic data, the
generated code and the exports. Your agent emits **structured output** (populations
and operation plans, not paragraphs), and GND checks it with its own deterministic
engine, which is lightweight, portable native Python. When you need more, GND hands the same model to
[Soufflé](https://souffle-lang.github.io/), [Lean](https://lean-lang.org/) or
[PyRel](https://pypi.org/project/relationalai/). If your team already works in PyRel,
GND exports its rules as an ordinary PyRel program you can read and run. These
programs run locally on DuckDB; Snowflake execution is not yet supported by gnd export.
**GND is agent skills plus Python code.**

![Animated: an agent proposes a payment plan, GND names the failed precondition, the agent adds the missing steps, and the revised plan is accepted.](docs/assets/hero.svg)

Because the checker is deterministic, a cheaper model is safe to try: a wrong plan is
rejected and retried inside a bounded session, never trusted. In our
[recorded sessions](docs/agents/recorded-sessions.md) on one task, a 4B model that
never succeeded on its first try was still accepted in two of three bounded sessions,
and the checker confirmed the failure when a 3B model did not converge, so you know the
final state either way.

> **Coming from GSD?** GND keeps GSD's discipline (plan, execute, verify, record)
> and its skills-in-your-agent packaging. It replaces the requirements document with an
> executable model, so a phase is done when the model's checker says so. Already
> have a GSD project? The `gnd-adopt` skill migrates your `.planning/` requirements into
> a GND model, with every requirement accounted for
> ([how](docs/guides/evolution-and-recovery.md#adopt-a-gsd-project)).

## Install from PyPI

Requires Python 3.11 or newer. With [uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv tool install get-nick-done==0.1.0
uv tool update-shell
```

Open a new shell and run `gnd --help`. For a pip virtual-environment installation,
see the [installation guide](docs/installation.md).

### Claude Code plugin

Inside Claude Code:

```text
/plugin marketplace add vasiloglou/gnd-public
/plugin install gnd@gnd-marketplace
```

### Codex plugin

In your terminal:

```sh
codex plugin marketplace add vasiloglou/gnd-public --ref main
codex plugin add gnd@gnd-marketplace
```

Start a new agent session after installing. The marketplace commands require the
plugin entries on repository `main` and GitHub access while the repository is
private. See [plugin installation](docs/marketplace-plugins.md) for details.

Alternatively, install skill files directly from the Python package in your
working project, choosing this route instead of a plugin:

```sh
gnd install --project          # Claude Code and Codex
gnd doctor --project
```

Then ask your agent, for example: *"Use gnd-model-from-text to model our expense
approval policy, then validate it."* See
[Work with an agent](docs/agents/index.md) for every skill and the artifacts it produces.

## Start with something that runs

- **[Run a check in 60 seconds](docs/quickstart.md):** find a shipping deadline
  violation, inspect the changed facts and verify the repair. No API key needed.
- **[Build BookRec](docs/bookrec/01-model.md):** a recommender with hard rules,
  advisory warnings and checked output publication.
- **[Build expense approvals](docs/expense/01-model.md):** a workflow that rejects an
  invalid state and adds currencies through model evolution.
- **[Verify at scale with PyRel, Soufflé and Lean](docs/runtimes/scenario.md):** audit
  releases, trace vulnerable dependencies and prove finite approval policies.

After the quickstart copies its inputs, a Python integration can check both candidates:

<!-- gnd-run expect=0 -->
```python
from gnd import api

bad = api.check("dispatch-demo/model.orm.json", "dispatch-demo/seed.pop.json", admission=True)
good = api.check("dispatch-demo/model.orm.json", "dispatch-demo/repaired.pop.json", admission=True)
print(bad["exit_code"], good["exit_code"])  # 1 0: deadline failure, then passing repair
assert bad["exit_code"] == 1 and good["exit_code"] == 0
```

## What GND does

- **Checks agent output against the model.** Each constraint either passes, fails with
  the offending facts, warns (deontic advice) or reports *cannot decide*. Nothing is guessed.
- **Checks plans, not only states.** An operation walk is checked step by step, and the
  frame check catches side effects no operation declared.
- **Runs agents in a bounded loop.** Session contracts, closed answer-free feedback and
  explicit terminal outcomes (accepted, stagnation, oscillation, budget exhausted).
- **Derives facts.** Derived fact types with stratified negation, recursion, aggregates,
  calendar dates and fixed reference data.
- **Tests the tester.** `gnd synth` generates conforming, boundary and violating
  populations; `gnd measure` reports the checker's false-pass and false-fail rates.
- **Keeps code and model aligned.** Code generation with derived and extension files,
  conformance checks, and model evolution with a blast-radius preview.
- **Round-trips documents.** Render a document from facts with planted distractors,
  extract facts back, and check both directions.
- **Exports to other engines.** Soufflé Datalog, Lean definitions with explicit proof
  obligations, PyRel programs, and independently replayable witnesses.
- **Gets a second opinion.** A six-seat review panel across Claude, Codex, Qwen, Gemini,
  Kimi and GLM that retains every dissent.

The [capabilities tour](docs/tour.md) shows each one with a motivating example.

## What a passing check means

A passing check means the supplied facts satisfy the modeled rules. GND verifies the
output, never the producer; you still choose the rules and establish that the facts
describe the world. Public builds report assurance as `unavailable`. Base checks and
the application tutorials run locally without model-provider keys.

## Contribute

See [CONTRIBUTING](CONTRIBUTING.md) and [preview the documentation site](docs/development/documentation.md).
The distribution is `get-nick-done`; import and command names are `gnd`.
Owned code is Apache-2.0; third-party attribution is in [NOTICE](NOTICE).
[Support](docs/support.md) · [Compatibility](docs/compatibility.md) · [Release notes](docs/release-notes.md).

The bundled [zero-install model validator](src/gnd/skills/gnd-model-from-text/scripts/validate_model.py)
is a limited fallback for agents running without the package. It does not implement
layer-2 semantic model rules, performs no population checking of any kind, offers no
model-relative population validation, cannot return exit band 4 (indeterminate), and
provides neither `--format json` nor `acceptance_ready`. Install GND for those features.
