# Clean candidate verification replay

Run from a checkout containing the milestone commits. The verification
scripts take the source checkout and output paths explicitly. The temporary
source checkout excludes later records and is clean before and after the
gates.

```sh
candidate=$(mktemp -d)
ga_sha=618141de9975c4ef30871a979532654267a15de6
ga_evidence="$PWD/.gnd-planning/milestones/guarded-rule-authoring/evidence/close"
git clone --shared "$PWD" "$candidate/source"
git -C "$candidate/source" checkout --detach "$ga_sha"
test "$(git -C "$candidate/source" rev-parse HEAD)" = "$ga_sha"
test -z "$(git -C "$candidate/source" status --porcelain --untracked-files=all)"

uv sync --project "$candidate/source" --locked --offline --extra synth
"$candidate/source/.venv/bin/python" -I "$ga_evidence/verify-union.py" \
  "$candidate/source" "$candidate/union.json" "$ga_sha"

uv build --wheel --offline --out-dir "$candidate/dist" "$candidate/source"
uv export --project "$candidate/source" --locked --offline --no-dev --no-emit-project \
  --extra synth --format requirements-txt --output-file "$candidate/runtime.txt" --quiet
uv venv --offline "$candidate/extra"
uv venv --offline "$candidate/base"
set -- "$candidate"/dist/*.whl
ga_wheel=$1
uv pip install --offline --python "$candidate/extra/bin/python" \
  --constraints "$candidate/runtime.txt" "${ga_wheel}[synth]"
uv pip install --offline --python "$candidate/base/bin/python" \
  --constraints "$candidate/runtime.txt" "$ga_wheel"
env -u PYTHONPATH "$candidate/extra/bin/python" -I "$ga_evidence/verify-installed.py" \
  "$candidate/source" "$ga_wheel" "$candidate/runs" "$candidate/installed.json" \
  "$candidate/base/bin/python" "$ga_sha"
```

The two installs use one wheel digest. The base interpreter confirms Faker
is absent and imports GND from its own environment. The added measure checks
bind the exact wrong-model sidecar diagnostic to both the full model and a
scoped-model copy with only a rationale change.

Ruff passed on Python source and test paths changed from `0ff0e9ca`, as listed
by `git diff --name-only -z 0ff0e9ca -- src tests`. The strict catalog gate was
`python3 scripts/components_index.py --no-cache changed --base 0ff0e9ca --strict`.
It reported zero entries to fix. The synth subsystem still describes
`cli.synth_command -> synth.service -> model.loading -> synth.corpus`.
The ILP service still owns admission and calls `export.mined_rules`, where
the role-typed codec and per-rule recount work are defined. Its aggregate
limit is applied at the import service before counting.
