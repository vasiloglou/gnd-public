# PyRel + GND: from rules to a checked app

You write the business rules once, as a GND model. Your app computes with
ordinary PyRel queries. Whatever proposes a result (a query, a script, an LLM
agent) hands it to GND, and nothing is saved unless the model's rules pass.
Bad proposals come back with the exact facts that broke a rule.

## Why PyRel users pair it with GND

If your team already models its ontology in PyRel, GND gives your agents a
gatekeeper: rules written once as a model and checked by a PyRel program
generated from it. The query stays small and
readable, because it only computes. The rules stay in one model, so changing a
limit is a model change, not a code change.

| Step | Who does it |
|---|---|
| Propose a result | The candidate producer: a PyRel query, a script or an LLM agent |
| Compute | PyRel, in your own `native_query.py` |
| Sort, limit, present | Plain Python |
| Check the rules, then save | GND, using a generated PyRel program |

Everything in these tutorials runs on PyRel 1.30.1 with DuckDB 1.5.5, locally,
with no account or key. Running against Snowflake is outside this tutorial and
outside the applications runtime, which refuses non-local connections. A passing
check means the supplied facts satisfy the modeled rules; it does not prove the
facts are true or that the producer is trustworthy.

## Set up

PyRel and GND need different versions of a shared library, so they live in two
Python environments. Run these setup commands once, in an empty folder, outside
the tutorials. They need [uv](https://docs.astral.sh/uv/) and a network
connection; uv fetches Python 3.13 if you do not have it.

First, an environment where GND can be imported. These chapters need a GND
newer than the 0.1.0 release on PyPI, so install it from a checkout of the
repository until the next release:

```sh
git clone https://github.com/vasiloglou/gnd-public.git
uv venv gnd-env --python 3.13
uv pip install --python gnd-env/bin/python ./gnd-public
export GND_TUTORIAL_GND_PYTHON="$(pwd)/gnd-env/bin/python"
```

Then the pinned PyRel environment, from the project GND ships:

```sh
"$GND_TUTORIAL_GND_PYTHON" -c "from importlib.resources import files; import shutil; shutil.copytree(str(files('gnd').joinpath('examples', 'release_governance', 'runtime-environment')), 'pyrel-env')"
uv sync --project pyrel-env --locked --only-group tutorial-runtimes --python 3.13
export GND_TUTORIAL_PYREL_PYTHON="$(pwd)/pyrel-env/.venv/bin/python"
```

Keep both `export` lines in your shell and stay in this folder: every chapter's
commands run from here. `gnd` itself is in `gnd-env/bin`; add that folder to
your `PATH` or type `gnd-env/bin/gnd`. Each chapter starts by checking that
both environments answer.

## The query toolkit

Your query is a plain Python file that runs in the PyRel environment. GND hands
it one object, `app`, already loaded with the input facts:

| Name | What it gives you |
|---|---|
| `app.model` | The ordinary PyRel model: use `where`, `select`, `not_`, `distinct` |
| `app.has(fact_type)`, `app.derivations` | Whether the model has a fact list, and which lists it derives |
| `app.match(fact_type, role=value)` | A match against one fact list, for use inside `where` |
| `app.ref(fact_type, role)` | A fresh query variable of the right type |
| `app.relationship(name, role=Type)` | A helper relation your query can `define` |
| `app.rows(query)` | The query's rows, sorted and size-limited |
| `app.check_work(estimate, label)` | Refuse inputs too large for the local runtime |
| `app.source`, `app.candidate()` | The input facts, and a copy to change for your proposal |
| `app.propose(candidate, calculation)` | Hand the proposal to GND's check |
| `app.refuse(kind, reason)` | Stop with a named refusal instead of a proposal |

The file ends with a short `main()` that loads `run_app` from the generated
program with `runpy.run_path` and calls it with your `calculate` function. See the full BookRec and
Expense queries at the end of each chapter.

## Where to start

New to GND? Start with [BookRec chapter 1](bookrec/01-model.md), where the rules
are written, and follow it through. Already finished the earlier chapters? Go
straight to the PyRel chapters:

- [BookRec on PyRel](bookrec/07-native.md): a faulty agent recommends an
  adult-only book to a minor, and the check refuses it.
- [Expense approvals on PyRel](expense/04-native.md): a team lead approves 800
  EUR against a 100 EUR limit, and the check refuses it.

## Next steps

- Write rules for your own domain with [gnd-model-from-text](agents/model-from-text.md).
- Drive a real LLM agent against a model and checker. That is a separate session
  contract you write for [`gnd exp run`](agents/dev-session.md).

These examples are small on purpose. They show how the pieces fit together, not
ranking quality, permissions, storage or concurrent writers.
