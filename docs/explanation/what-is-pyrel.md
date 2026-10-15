# What PyRel is, and when you need it

You don't need PyRel to use GND. GND checks models, data and plans with its own
checker, which installs with `gnd` and needs no account, no database and no
extra runtime. Everything in the tutorials works that way.

PyRel is an optional extension, for when the facts you want to check live in
your company's data platform rather than in files.

!!! info "Files on GitHub"

    - [`pyrel_rules.py`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/export/pyrel_rules.py): the code that writes the PyRel programs
    - [this page's Markdown source](https://github.com/vasiloglou/gnd-public/blob/main/docs/explanation/what-is-pyrel.md)

## What PyRel is

PyRel is RelationalAI's Python library (the `relationalai` package) for writing
relational models and queries in Python. The same PyRel program can run in two
places:

| Where | What you need | What it is for |
|---|---|---|
| On your laptop, with DuckDB | the `relationalai` and `duckdb` packages; no account | prototyping: the facts are local files |
| On RelationalAI's Native App for Snowflake | a Snowflake account with the RelationalAI app | your enterprise data, where it already lives |

## What GND does with it

GND can write a PyRel program from a model, so the rules you wrote once are
checked by PyRel too. `gnd export pyrel MODEL --rules duckdb` writes a program
that runs locally on DuckDB and reports the facts that break each rule.
`gnd export pyrel MODEL --rules lqp` writes the same rules as PyRel
requirements for a RelationalAI engine.

## What has been tested

| Path | Status in GND |
|---|---|
| GND's own checker | the default; everything in the docs uses it |
| The PyRel program on DuckDB, locally | tested: it agrees with GND's checker on every recorded plan in these docs |
| The PyRel program on a RelationalAI engine, such as the Snowflake Native App | compiled and counted, not yet run; Snowflake execution is not yet supported by gnd export |

So you can prototype with GND alone, check the same rules on PyRel locally
when you want to see them as PyRel, and plan for Snowflake knowing that this
last step is not yet tested.

## Set up PyRel locally

PyRel runs in its own Python environment, separate from GND's, and GND finds it
through `GND_PYREL_PYTHON`. The [PyRel runtime page](../runtimes/pyrel.md) and
its [shared setup](../runtimes/scenario.md) show how to create that environment.
Then add `--backend pyrel` to an example app's `check` or `ask` command.

## Read more

- [How a rule becomes a PyRel check](rules-as-pyrel.md): one rule in both
  generated programs.
- [RelationalAI's documentation](https://docs.relational.ai/) for PyRel itself
  and the Snowflake Native App.
