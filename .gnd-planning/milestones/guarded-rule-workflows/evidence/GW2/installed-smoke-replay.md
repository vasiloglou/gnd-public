# Installed candidate smoke replay

The [smoke receipt](installed-smoke.json) covers both GW0 and GW2.
The build ran from clean source commit
`e02345d375b21361a5aa0633d748043d381e93fe`. The lock SHA-256 is
`2e2614c5a639652005aa48677b12c2fa93af44f3b81c8c1ecbdc7e1b3b0bd517`.
All uv steps used `--offline`. The wheel was installed under a temporary
candidate directory using the runtime dependencies exported from the lock.

```sh
uv build --wheel --offline --out-dir "$candidate/dist"
uv export --locked --offline --no-dev --no-emit-project --format requirements-txt --output-file "$candidate/runtime.txt" --quiet
uv venv --offline "$candidate/venv"
uv pip install --offline --python "$candidate/venv/bin/python" --constraints "$candidate/runtime.txt" "$candidate"/dist/*.whl
```

The generated inputs came from `_write` in
`tests/test_guarded_diagnostics.py` with the cases `antecedent_typo` and
`consequent_typo`, and `_write` in `tests/test_rule_edition_comparison.py`
with `rename=True`. Both helpers receive the temporary input directory
for their workflow.

| Input relative to the candidate | SHA-256 |
|---|---|
| `input/gw0/model.orm.yaml` | `919eacc5151d76f38a4abdefd187ca36e6b3f1f050eb6152931a9fc5595fb191` |
| `input/gw0/population.yaml` | `bbb402f4de609fe4a145d2845519ed37d4ecb5e8822da7887100fb0371d7823c` |
| `input/gw2/base.orm.yaml` | `8663a8fc34060aee0f00e221bf46b5d150951c08c69ac3cf682254e56669ebe3` |
| `input/gw2/head.orm.yaml` | `0907b607e32efc35245324c0de0558f045e8b8d92ae839c10c62925b1a041f98` |
| `input/gw2/population.yaml` | `31e861a53d00b6f98b771862d1cc13a1d7cab322d75a4c97943edbda7e9721ee` |

The harness cleared PYTHONPATH, checked `gnd.__file__` under the candidate
venv, and invoked these commands with the named current directories.
It validated every JSON report against the installed report schema.

```sh
cd "$candidate/input/gw0"
env -u PYTHONPATH "$candidate/venv/bin/python" -m gnd check model.orm.yaml population.yaml --guarded-diagnostics --format json
env -u PYTHONPATH "$candidate/venv/bin/python" -m gnd validate model.orm.yaml --format json
cd "$candidate/input/gw2"
env -u PYTHONPATH "$candidate/venv/bin/python" -m gnd check head.orm.yaml population.yaml --baseline-model base.orm.yaml --format json
```
