#!/usr/bin/env bash
# Start from the published plan branch base and verify the exact candidate patch.
set -euo pipefail
export LC_ALL=C
export PATH="$HOME/.local/bin:$PATH"
scratch=$1
expected_patch=$2
printf 'RV1 scratch directory: %s\n' "$scratch"
uv --version
sw_vers
actual_patch=$(shasum -a 256 "$scratch/candidate.patch" | awk '{print $1}')
test "$actual_patch" = "$expected_patch"
printf 'Candidate patch SHA-256: %s\n' "$actual_patch"
git clone --quiet https://github.com/vasiloglou/gnd-public.git "$scratch/source"
cd "$scratch/source"
git checkout --quiet --detach 9dc1d99f
test -z "$(git status --porcelain)"
git apply --index --binary "$scratch/candidate.patch"
git diff --cached --check
git -c user.name='GND release verification' -c user.email='release@example.invalid' commit --quiet -m 'RV1 verification snapshot'
printf 'Candidate Git tree: '
git rev-parse HEAD^{tree}
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
