# Public-interface app regression recipe

Runtime candidate: 6cff353e7bc25a8e5bab3952cfb9d137611ced45.
Docs candidate: 47e9071 (descendant containing the same runtime).
Use the eventual merged commit for the app owner's M3 acceptance; neither
candidate nor these portable tests assert that the external M3 gate ran.

From this repository after installing its development dependencies:

```sh
uv run pytest -q tests/test_compiled_snapshot_obligations.py --tb=short
uv run gnd check tests/fixtures/compiled-snapshot/model.orm.json tests/fixtures/compiled-snapshot/nonnumeric.pop.json --compiled-operations --format json
uv run gnd check tests/fixtures/compiled-snapshot/model.orm.json tests/fixtures/compiled-snapshot/numeric.pop.json --compiled-operations --format json
```

Expected CLI exits: nonnumeric 1, numeric 2 (other constraints are vacuous).
The invalid case must name filter_compare.pre_numeric via the generated
reference $.operations[id=filter_compare].compiled[2]; derivation failures
remain zero. Python and batch consumers explicitly select the same mode:

```python
from gnd import api
result = api.check(model, population, compiled_operations=True)
```

```sh
uv run gnd check MODEL --populations DIR --compiled-operations --format json
```

Compare public exit_code, counts and failing_constraints; batch does not expose
all passing/warning rows. Use the single report for witnesses. A snapshot
cannot prove intermediate states or frames; retain the walk gate separately.
