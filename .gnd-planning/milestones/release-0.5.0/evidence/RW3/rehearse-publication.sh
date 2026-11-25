#!/usr/bin/env bash
# Rehearse the publication text in a disposable clone: rehearse-publication.sh CHECKOUT SUPPLEMENT COMMIT
# Nothing here uploads, tags or releases. The date below is a rehearsal date.
set -euo pipefail
checkout=$1
supplement=$2
expected=$3
test "$(git -C "$checkout" rev-parse HEAD)" = "$expected"
test -z "$(git -C "$checkout" status --porcelain)"
cd "$checkout"
printf 'Rehearsal source: %s\nRehearsal date: 2026-11-25\n' "$expected"
printf '%s\n' "uv run python tools/release_text.py publish --date 2026-11-25 --built 85d076ba --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10'"
tool_exit=0
uv run python tools/release_text.py publish --date 2026-11-25 --built 85d076ba \
    --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10' || tool_exit=$?
printf 'Tool-only publish exit: %s\n' "$tool_exit"
test "$tool_exit" = 1

git apply --check "$supplement"
printf 'git apply --check <supplement>: exit 0\n'
git apply "$supplement"
uv run python tools/release_text.py check
printf 'uv run python tools/release_text.py check: exit 0\n'
release_tests=(tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py)
printf 'uv run pytest -q %s --tb=short\n' "${release_tests[*]}"
uv run pytest -q "${release_tests[@]}" --tb=short -p no:cacheprovider
printf 'Release tests exit: 0\n'
uv run --group docs zensical build --strict
printf 'uv run --group docs zensical build --strict: exit 0\n'
uv run python tools/check_docs.py site
printf 'uv run python tools/check_docs.py site: exit 0\n'
git diff --check
printf 'Files changed by the publication edits:\n'
git diff --stat HEAD -- | cat
printf 'Scratch publication diff SHA-256: '
git diff --binary HEAD -- | shasum -a 256 | awk '{ print $1 }'
