#!/usr/bin/env bash
# Build the release artifacts and sdist-derived comparison wheel from one commit.
set -euo pipefail
checkout=$1
commit=$2
target=$3
python=$4
test ! -e "$target"
test "$(git -C "$checkout" rev-parse "$commit^{commit}")" = "$commit"
git -C "$checkout" merge-base --is-ancestor "$commit" origin/main
test "$(uv --version | cut -d' ' -f2)" = 0.10.10
"$python" -c 'import sys; assert sys.version_info[:2] == (3, 11), sys.version'
scratch=$(mktemp -d /private/tmp/gnd-rv2-build.XXXXXX)
mkdir "$scratch/source" "$scratch/comparison"
git -C "$checkout" archive "$commit" | tar -x -C "$scratch/source"
mkdir -p "$(dirname "$target")"
candidate=$(mktemp -d "$target.build.XXXXXX")
(
    cd "$scratch/source"
    uv build --python "$python" --out-dir "$candidate/release"
)
tar -xzf "$candidate"/release/*.tar.gz -C "$scratch/comparison"
uv build --python "$python" --wheel "$scratch"/comparison/* --out-dir "$candidate/comparison"
rm -f "$candidate/release/.gitignore" "$candidate/comparison/.gitignore"
printf '%s\n' "$commit" > "$candidate/SOURCE_COMMIT"
{
    sw_vers
    uname -m
    "$python" --version
    uv --version
} > "$candidate/BUILD_PROFILE"
cd "$candidate"
shasum -a 256 release/* comparison/* > SHA256SUMS
shasum -a 256 -c SHA256SUMS
cat SOURCE_COMMIT BUILD_PROFILE SHA256SUMS
cd "$(dirname "$target")"
test ! -e "$target"
mv "$candidate" "$target"
