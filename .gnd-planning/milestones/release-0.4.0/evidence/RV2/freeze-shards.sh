#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export PATH="$HOME/.local/bin:$PATH"
scratch=$(mktemp -d /private/tmp/gnd-rv2-freeze.XXXXXX)
printf 'RV2 freeze scratch directory: %s\n' "$scratch"
uv --version
sw_vers
git clone --quiet https://github.com/vasiloglou/gnd-public.git "$scratch/source"
cd "$scratch/source"
git merge-base --is-ancestor '648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a' origin/main
git checkout --quiet --detach '648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a'
git rev-parse HEAD
test -z "$(git status --porcelain)"
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
