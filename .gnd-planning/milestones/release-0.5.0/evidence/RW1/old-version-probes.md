# RW1: what 0.4.0 did on inputs the notes name

Run on 2026-11-24 on the planning machine, to back two sentences of the
0.5.0 notes ("0.4.0's DuckDB program accepted the first and the last and
reported a uniqueness rule satisfied where `gnd check` reports a failure").
This is a measurement for the notes, not a release probe: RW2's installed
probes are separate.

Inputs:

- the model `tests/fixtures/pyrel-rules-coverage/rp3/float.orm.json` (one
  fact type `run_has_score`, a `Float` score, uniqueness on `run`);
- `beyond`: `tests/fixtures/pyrel-rules-coverage/rp3/beyond.population.json`
  with its `population.model` field renamed to `float.orm.json`: two rows for
  run `a`, with scores 9007199254740993 and 9007199254740992;
- `equal`: the same population with the rows `{"run": "a", "score": 1}` and
  `{"run": "a", "score": 1.0}`.

Commands, with `old` = `uvx --from get-nick-done==0.4.0 gnd` (it printed
`gnd 0.4.0`) and `new` = `uv run gnd` at `cfe5f00e`; the programs were run
by the tutorials runtime interpreter with `-I`:

```text
GND export pyrel float.orm.json --rules duckdb --out float.py
PYTHON -I float.py POPULATION
```

| Input | 0.4.0 program | Program at `cfe5f00e` | `gnd check` at `cfe5f00e` |
|---|---|---|---|
| `beyond` | exit 0, `one_score  OK` | exit 3: `run_has_score.score is 9007199254740993, an integer beyond 2**53, which a Float here (a binary float) cannot hold exactly; GND keeps it exact` | exit 1, `fail=1` |
| `equal` | exit 0, `one_score  OK` | exit 3: `duplicate rows in run_has_score: PyRel relations are sets, so repeated facts cannot be checked here; GND reports them` | exit 1, `fail=1` |

Not measured on 0.4.0: a non-finite number, a `Number` cell (0.4.0 refuses
`Number` at export), and the export-time refusals. The notes make no claim
about what 0.4.0 did with those.

## Added 2026-11-25: an Integer result written into a Float role

The RW1 review (finding F1) named a model that 0.4.0 exported and this tree
refuses. Reproduced on the planning machine, with `old` as above and `new` =
`uv run gnd` at `cc8cdb65`.

Input: `tests/fixtures/pyrel-rules-coverage/rp3/sum-into-number.orm.json`
with `object_types[1].primitive` changed from `Number` to `Float` and the
aggregate function of `fact_types[1].derivation_rule` set to `sum`, `min` or
`max` in turn. Command: `GND export pyrel MODEL --rules MODE --out FILE`.

| Aggregate | Mode | 0.4.0 | At `cc8cdb65` |
|---|---|---|---|
| `min` | `duckdb`, `lqp` | exit 0, program written | exit 3 |
| `max` | `duckdb`, `lqp` | exit 0, program written | exit 3 |
| `sum` | `duckdb`, `lqp` | exit 0, program written | exit 3 |

The refusal at `cc8cdb65`, for `min` with `--rules duckdb`: `cannot write
the rules program: run_scores_big: $total is an Integer value written into
the Float or Number role 'score'; PyRel would round it beyond 2**53, so the
rules programs refuse it`.

Still not measured on 0.4.0: the other export-time refusals (an integer
beyond 2**53 among a model's literals, arithmetic next to a `Float` value, a
float literal compared with an `Integer` value). The notes say this tree
refuses them and make no claim about 0.4.0 for them.

## Added 2026-11-25: a count written into a Float or Number role

The second review round (finding F1) said the repaired sentence refused too
much. Reproduced at `1d8536de`:
`tests/fixtures/pyrel-rules-coverage/rp3/count-into-number.orm.json` exports
with exit 0 under `--rules duckdb` and `--rules lqp`. The same model with
its `Number` destination changed to `Float` exports with exit 0 in both
modes on this tree and on 0.4.0. A count is accepted; the notes now say so.
