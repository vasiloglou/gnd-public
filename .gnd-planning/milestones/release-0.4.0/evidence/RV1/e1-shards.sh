#!/usr/bin/env bash
# Run with bash on beast-3. Preserve the six per-shard logs and exits.
set -euo pipefail
export LC_ALL=C
export PATH="$HOME/.local/bin:$PATH"
scratch=$(mktemp -d /private/tmp/gnd-rv1-e1.XXXXXX)
printf 'E1 scratch directory: %s\n' "$scratch"
uv --version
sw_vers
git clone --quiet https://github.com/vasiloglou/gnd-public.git "$scratch/source"
cd "$scratch/source"
git checkout --quiet --detach cc4c8bf0
git rev-parse HEAD
test -z "$(git status --porcelain)"
python3 - <<'PY'
from pathlib import Path

paths = {
    "pyproject.toml": ('version = "0.3.1"', 'version = "0.4.0"'),
    "uv.lock": ('name = "get-nick-done"\nversion = "0.3.1"', 'name = "get-nick-done"\nversion = "0.4.0"'),
}
for name in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/marketplace.json"):
    paths[name] = ('"version": "0.3.1"', '"version": "0.4.0"')
for name, (old, new) in paths.items():
    path = Path(name)
    contents = path.read_text()
    if contents.count(old) != 1:
        raise SystemExit(f"{name}: expected one exact release field")
    path.write_text(contents.replace(old, new))
PY
git diff --check
git diff --name-only
uv sync --locked --group dev --python 3.13.18
uv run --no-sync python --version
files=(tests/test_*.py)
pids=()
for ((shard=0; shard<6; shard++)); do
    shard_files=()
    for ((index=shard; index<${#files[@]}; index+=6)); do
        shard_files+=("${files[index]}")
    done
    (
        set +e
        uv run --no-sync pytest -q --tb=line -p no:cacheprovider "${shard_files[@]}" >"$scratch/shard-$shard.log" 2>&1
        code=$?
        printf '%s\n' "$code" >"$scratch/shard-$shard.exit"
    ) &
    pids+=("$!")
done
for pid in "${pids[@]}"; do
    wait "$pid"
done
for ((shard=0; shard<6; shard++)); do
    printf '\nShard %s exit %s\n' "$shard" "$(cat "$scratch/shard-$shard.exit")"
    awk '/^(FAILED|ERROR|=+ .* (passed|failed|errors|skipped|deselected))/ { print }' "$scratch/shard-$shard.log"
    tail -n 1 "$scratch/shard-$shard.log"
done
