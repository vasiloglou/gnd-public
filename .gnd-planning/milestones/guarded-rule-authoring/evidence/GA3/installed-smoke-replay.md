# Installed authoring smoke

Build and install a local wheel offline from the recorded source commit.
The installed Python runs the smoke from scratch directories with isolated
module loading. The receipt records the wheel, lock and input digests,
each public command's exit and streams, and the output artifact digests.

```sh
candidate=$(mktemp -d)
uv build --wheel --offline --out-dir "$candidate/dist"
uv export --locked --offline --no-dev --no-emit-project --extra synth --format requirements-txt \
  --output-file "$candidate/runtime.txt" --quiet
uv venv --offline "$candidate/venv"
set -- "$candidate"/dist/*.whl
ga_wheel=$1
uv pip install --offline --python "$candidate/venv/bin/python" \
  --constraints "$candidate/runtime.txt" "${ga_wheel}[synth]"
env -u PYTHONPATH "$candidate/venv/bin/python" -I \
  .gnd-planning/milestones/guarded-rule-authoring/evidence/GA3/installed-smoke.py \
  "$PWD" "$ga_wheel" "$candidate/runs" "$candidate/receipt.json"
```

GA1 exercises the shipped model and an isolated repeated-variable guard.
GA2 discovers and previews a directed proposal on the shared architecture
fixture. GA3 exports facts, binds the capture-format rule rows to those facts,
imports the typed rules and previews the proposal. The fixture does not
claim a live AMIE invocation.
