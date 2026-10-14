# PyRel + GND: from rules to a checked app

You write the business rules once, as a GND model. Your app computes with
ordinary PyRel queries. Whatever proposes a result (a query, a script, or a
coding assistant such as Claude Code or Codex) hands it to GND, and nothing is
saved unless the model's rules pass. Bad proposals come back with the exact
facts that broke a rule, and the assistant repairs from that.

## Why PyRel users pair it with GND

If your team already models its ontology in PyRel, GND gives your agents a
gatekeeper: rules written once as a model and checked by a PyRel program
generated from it. The query stays small and readable, because it only
computes. The rules stay in one model, so changing a limit is a model change,
not a code change. And the assistant that writes the query or proposes the
result is checked the same way a person's work is.

| Step | Who does it |
|---|---|
| Propose a result | The candidate producer: a PyRel query, a script, or a coding assistant |
| Compute | PyRel, in your own `native_query.py` |
| Sort, limit, present | Plain Python |
| Check the rules, then save | GND, using a generated PyRel program |
| Repair a refused proposal | The producer again, from the facts GND names |

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
export PATH="$PWD/gnd-env/bin:$PATH"
```

Then the pinned PyRel environment, from the project GND ships:

```sh
python -c "from importlib.resources import files; import shutil; shutil.copytree(str(files('gnd').joinpath('examples', 'release_governance', 'runtime-environment')), 'pyrel-env')"
uv sync --project pyrel-env --locked --only-group tutorial-runtimes --python 3.13
export GND_PYREL_PYTHON="$PWD/pyrel-env/.venv/bin/python"
```

Keep both `export` lines in your shell and stay in this folder: every chapter's
commands run from here. After the first line, `python` and `gnd` mean the GND
environment. The PyRel interpreter is never on your path; the applications read
it from `GND_PYREL_PYTHON`. Each chapter starts by checking that both
environments answer.

## How a rule becomes a PyRel check

A rule in the model is a sentence with a shape. GND reads the shape and builds
one PyRel query for it. The query asks PyRel for the facts that break the rule,
so an empty answer means the rule holds and every row is a witness (the exact
facts that break the rule).

| Rule shape in the model | What the check asks PyRel | A row means |
|---|---|---|
| Guarded rule with an `absence` consequent | match the antecedent atoms, and the forbidden atom | the forbidden fact is present |
| Guarded rule with an `atom` consequent | match the antecedent atoms, and `not_` the required atom | the required fact is missing |
| Guarded rule with a `comparison` | match the antecedent atoms, and the negated comparison, so `<= 100` becomes `> 100` | the amount breaks the limit |
| Mandatory role | every object of the type, and `not_` the fact that must mention it | an object with no such fact |
| Value list | the fact, and `!=` for every allowed value | a value outside the list |
| Subset | the left-hand fact, and `not_` the right-hand fact | a tuple on the left only |

Take BookRec's age rule. The person who wrote it said:

```text
Never recommend an adult-rated book to a minor.
```

The model stores that sentence as provenance and the rule as a guarded
constraint: two antecedent atoms and an absence consequent.

```yaml
id: age_appropriate
type: guarded
modality: alethic
antecedent:
  - fact_type: recommendation
    bind: {user: "$u", book: "$b"}
  - fact_type: user_is_minor
    bind: {user: "$u"}
consequent:
  absence:
    fact_type: book_rated_adult
    bind: {book: "$b"}
```

Written by hand as a PyRel query, the breach is the three atoms together:

```python
m.where(recommendation(u, b), user_is_minor(u), book_rated_adult(b)).select(u, b)
```

A row `ada, night` is the witness `{"$b": "night", "$u": "ada"}`. The query
computes; the check witnesses. The chapters show every rule this way, run the
hand-written queries, and compare their rows with what GND prints. The query a
reader writes is an equivalent of what the checker generates, not the generated
program itself; `gnd export pyrel` writes that program if you want to read it.

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
program with `runpy.run_path` and calls it with your `calculate` function. See
the full BookRec and Expense queries at the end of each chapter.

## Where the coding assistant fits

GND is built to be used with a coding assistant. The assistant proposes; GND
checks; the feedback names the rule and the offending facts, never the answer.
The packaged skills tell the assistant what to produce at each step, and each
chapter shows the prompt beside the checkpoint it produces, what the skill
makes the assistant do, and the `gnd` command that checks the result.

| Chapter step | You ask the assistant to use | It produces | GND checks it with |
|---|---|---|---|
| The rules, three ways | `gnd-model-from-text` | `model.orm.yaml` with your words as provenance | `gnd validate` |
| Set up the project | `gnd-codegen`, then `gnd-conformance` | the generated project and your extension | `gnd conformance` |
| An agent in the loop | `gnd-dev-session` | a session contract, attempts, feedback, a close record | `gnd exp run`, `gnd exp close` |
| Change a rule | `gnd-model-evolve` | a proposal, a preview, an applied model | `gnd evolve preview`, `gnd evolve apply` |

Both chapters replay a deterministic stand-in agent so the loop runs on your
machine without a model, and both show sessions recorded with a real coding
assistant: the task it was given, what it read and ran, what it wrote, and how
GND judged it. Recorded sessions are labelled with their date and tool version
and are never re-run by the page. See
[skills and Python: who does what](agents/index.md) and
[recorded agent sessions](agents/recorded-sessions.md).

## Where to start

New to GND? Start with [BookRec chapter 1](bookrec/01-model.md), where the rules
are written, and follow it through. Already finished the earlier chapters? Go
straight to the PyRel chapters:

- [BookRec on PyRel](bookrec/07-native.md): a scripted stand-in recommends an
  adult-only book to a minor, and the check refuses it.
- [Expense approvals on PyRel](expense/04-native.md): a team lead approves 800
  EUR against a 100 EUR limit, and the check refuses it.

## Next steps

- Write rules for your own domain with [gnd-model-from-text](agents/model-from-text.md).
- Drive your own coding assistant against a model and checker. That is a separate
  session contract you write for [`gnd exp run`](agents/dev-session.md); the
  chapters show the contract and the stand-in that plays the agent.

These examples are small on purpose. They show how the pieces fit together, not
ranking quality, permissions, storage or concurrent writers.
