# Check and repair a shipping request

Use Python 3.11 or newer. The current package is a preparation build; obtain the
selected local wheel from the release operator. No public-index release is
claimed. Install the wheel into a fresh environment (replace the one wheel
filename with the artifact supplied):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install /path/to/get_nick_done-0.1.0-py3-none-any.whl
```

After installation this exercise needs no API key, network or native compiler.
Copy the complete packaged inputs into a new directory, without template edits:

```sh
.venv/bin/python - <<'PYCODE'
from importlib.resources import files
from shutil import copytree
copytree(str(files('gnd') / 'examples' / 'dispatch'), 'dispatch-demo')
PYCODE
.venv/bin/gnd validate dispatch-demo/model.orm.json --format json
.venv/bin/gnd check dispatch-demo/model.orm.json dispatch-demo/seed.pop.json --admission --format json
```

Validation exits 0. The seed check deliberately exits **1**: its only failed
verdict has `constraint_ref: constraints[1]`, corresponding to model constraint
`dispatch_deadline`. Its three-day window exceeds the supplied deadline. This
is a semantic violation, not a parse error. Inspect `report.verdicts` in JSON.
Use the supplied repair; keep the fixed reference catalog alongside the model:

```sh
.venv/bin/gnd check dispatch-demo/model.orm.json dispatch-demo/repaired.pop.json --admission --format json
```

The repair exits **0**. Missing or modified reference data exits **3**. These
facts are authored synthetic inputs, not a live shipping system or provider
judgment. A five-minute first run is a target, not measured user evidence.

The same integration through Python:

```python
from gnd import api
result = api.check('dispatch-demo/model.orm.json',
                   'dispatch-demo/seed.pop.json', admission=True)
assert result['exit_code'] == 1
for verdict in result['report']['verdicts']:
    if verdict['verdict'] == 'fail':
        print(verdict['constraint_ref'], verdict['message'])
```

## Software release and dependencies

Copy `files('gnd') / 'examples' / 'release'` into `release-demo` with the same
Python block. Run the same validate/check commands replacing `dispatch-demo`
with `release-demo`. The catalog supplies allowed dependency nodes and edges;
the model checks the claimed reachable dependency relation. The seed's
`release_deadline` (`constraints[1]`) fails (exit 1), the supplied repair passes
(exit 0), and losing the reference catalog refuses (exit 3). This example checks
a declared dependency graph and release deadline; it does not deploy software.
