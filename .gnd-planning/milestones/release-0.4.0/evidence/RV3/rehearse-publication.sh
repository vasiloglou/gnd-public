#!/usr/bin/env bash
# Rehearse publication text only in the supplied disposable clone.
set -euo pipefail
checkout=$1
supplement=$2
expected=648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a
test "$(git -C "$checkout" rev-parse HEAD)" = "$expected"
test -z "$(git -C "$checkout" status --porcelain)"
cd "$checkout"
printf 'Frozen source: %s\nRehearsal date: 2026-11-17\n' "$expected"
printf '%s\n' "uv run --no-sync python tools/release_text.py publish --date 2026-11-17 --built 648cc6e0 --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10'"
tool_exit=0
uv run --no-sync python tools/release_text.py publish --date 2026-11-17 --built 648cc6e0 \
    --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10' || tool_exit=$?
printf 'Tool-only publish exit: %s\n' "$tool_exit"
test "$tool_exit" = 1

guides=(docs/bookrec/08-guarded-rules.md docs/bookrec/09-suggested-rules.md docs/expense/05-receipts.md)
marker='are not in a published package yet'
for path in "${guides[@]}"; do
    printf 'Negative control, prepared marker remains in %s: ' "$path"
    rg -n "$marker" "$path"
done
git apply --check "$supplement"
printf 'git apply --check <supplement>: exit 0\n'
git apply "$supplement"
for path in "${guides[@]}" docs/marketplace-plugins.md; do
    if rg -n "$marker|prepared and not published" "$path"; then
        exit 1
    fi
    printf 'Prepared marker absent: %s\n' "$path"
done
uv run --no-sync python tools/release_text.py check
printf 'uv run --no-sync python tools/release_text.py check: exit 0\n'
release_tests=(tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py)
printf 'uv run --no-sync pytest -q %s --tb=short\n' "${release_tests[*]}"
uv run --no-sync pytest -q "${release_tests[@]}" --tb=short
printf 'Release tests exit: 0\n'
uv run --no-sync --group docs zensical build --strict
printf 'uv run --no-sync --group docs zensical build --strict: exit 0\n'
uv run --no-sync python tools/check_docs.py site
printf 'uv run --no-sync python tools/check_docs.py site: exit 0\n'
git diff --check
printf 'Scratch publication diff SHA-256: '
git diff --binary HEAD -- | shasum -a 256 | awk '{ print $1 }'
