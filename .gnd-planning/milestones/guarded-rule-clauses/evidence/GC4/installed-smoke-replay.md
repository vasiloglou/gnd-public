# Retail guarded-rules installed smoke

From the repository root, build a wheel, install its synth extra against
the lockfile, and run the public check and synthesis commands in isolation.

```sh
candidate=$(mktemp -d)
uv build --wheel --offline --out-dir "$candidate/dist"
uv export --locked --offline --no-dev --no-emit-project --extra synth --format requirements-txt \
  --output-file "$candidate/runtime.txt" --quiet
uv venv --offline "$candidate/venv"
set -- "$candidate"/dist/*.whl
wheel=$1
uv pip install --python "$candidate/venv/bin/python" \
  --constraints "$candidate/runtime.txt" "${wheel}[synth]"
env -u PYTHONPATH "$candidate/venv/bin/python" -I \
  .gnd-planning/milestones/guarded-rule-clauses/evidence/GC4/installed-smoke.py \
  "$wheel" "$candidate/runs" "$candidate/receipt.json"
```

The script checks original rule addresses, both delivery branches, raw-code
exception vacuity, existing joint account exclusion and rule wording. The
record binds the wheel, lockfile, model and populations by SHA-256.
