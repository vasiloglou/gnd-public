# RW1: what 0.4.0 did on two inputs the notes name

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
