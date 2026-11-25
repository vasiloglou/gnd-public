#!/usr/bin/env bash
# Compare independent builds and exercise the preserved original on beast-3.
set -euo pipefail
scratch=$1
commit=$2
root="$HOME/gnd-release/0.5.0/${commit:0:8}"
source_bundle="$scratch/candidate"
(
    cd "$source_bundle"
    test "$(cat SOURCE_COMMIT)" = "$commit"
    shasum -a 256 -c SHA256SUMS
)
mkdir -p "$root"
test ! -e "$root/candidate"
mv "$source_bundle" "$root/candidate"

uvbin=$("$HOME/.local/bin/uvx" --from uv==0.10.10 python -c 'import uv; print(uv.find_uv_bin())')
mkdir "$scratch/pinned"
ln -s "$uvbin" "$scratch/pinned/uv"
ln -s "$(dirname "$uvbin")/uvx" "$scratch/pinned/uvx"
export PATH="$scratch/pinned:$HOME/.local/bin:$PATH"
test "$(uv --version | cut -d' ' -f2)" = 0.10.10
test "$(uvx --version | cut -d' ' -f2)" = 0.10.10
python=$(uv python find 3.11)
git clone --quiet https://github.com/vasiloglou/gnd-public.git "$scratch/checkout"
git -C "$scratch/checkout" checkout --quiet --detach "$commit"
bash "$scratch/build.sh" "$scratch/checkout" "$commit" "$root/independent" "$python"
diff "$root/candidate/SHA256SUMS" "$root/independent/SHA256SUMS"
printf 'Independent wheel, sdist and comparison wheel match the retained SHA256SUMS.\n'

cd "$scratch/checkout"
test "$(git rev-parse HEAD)" = "$commit"
test -z "$(git status --porcelain)"
test "$(cat "$root/candidate/SOURCE_COMMIT")" = "$(git rev-parse HEAD)"
(cd "$root/candidate" && shasum -a 256 -c SHA256SUMS)
uv sync --locked --group dev --python "$python"
uv run --no-sync python --version
uv --version
date -u +%Y-%m-%dT%H:%M:%SZ
GND_CANDIDATE_DIR="$root/candidate" uv run --no-sync pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short
printf 'Installed acceptance exit 0.\n'
cd "$scratch"
output=$(uvx --python "$python" --from "$root"/candidate/release/*.whl gnd --version)
printf '%s\n' "$output"
test "$output" = "gnd 0.5.0"
date -u +%Y-%m-%dT%H:%M:%SZ
