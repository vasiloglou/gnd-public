# GND · Get Nick Done

**Build agentic data apps that check themselves.**

GND turns requirements into an **executable ontology**: an
[Object-Role Modeling (ORM)](https://www.orm.net/) model of facts, rules and
constraints. Your agent emits structured output (populations and operation
plans, not paragraphs), and GND checks it with its own deterministic engine,
which is lightweight, portable native Python. When you need more, GND hands the
same model to [Soufflé](https://souffle-lang.github.io/),
[Lean](https://lean-lang.org/) or
[PyRel](https://pypi.org/project/relationalai/). GND is agent skills plus
Python code.

## Install

Requires Python 3.11 or newer. With
[uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv tool install get-nick-done
uv tool update-shell
```

Open a new shell and run `gnd --help`. The distribution is `get-nick-done`; the
command and the import package are both `gnd`. The
[installation guide](https://vasiloglou.github.io/gnd-public/installation/)
covers a pip virtual environment and the Claude Code plugin.

## What it does

- **Checks populations.** A verdict names the offending facts, warns or reports
  that it cannot decide. Nothing is guessed.
- **Checks plans, not only states.** An operation walk is checked step by step.
- **Runs agents in a bounded loop**, with closed answer-free feedback and
  explicit terminal outcomes.
- **Derives facts**, with stratified negation, recursion, aggregates and
  calendar dates.
- **Keeps code and model aligned**: code generation, conformance checks and
  model evolution with a blast-radius preview.
- **Shares pinned Apache Ossie ontologies**, with per-field loss reports.
- **Exports to other engines**: Soufflé Datalog, Lean definitions and PyRel
  programs.

A passing check means the supplied facts satisfy the modeled rules. GND verifies
the output, never the producer.

## Where to go next

- [Run a check in 60 seconds](https://vasiloglou.github.io/gnd-public/quickstart/)
- [Documentation](https://vasiloglou.github.io/gnd-public/)
- [Release notes](https://vasiloglou.github.io/gnd-public/release-notes/)
- [Source and issues](https://github.com/vasiloglou/gnd-public)
