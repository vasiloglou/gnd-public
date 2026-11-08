#!/bin/sh
# Stale release-state text check (rule-check-release RR3, M4). Run from the
# repository root. Exits 1 and prints every hit of the RR3 search, and every
# release-state phrase in the release notes' opening, that is not allowlisted.
# The allowlist holds the text that is right once 0.2.0 is published, or is
# historical; it is matched by exact file:line-text, not line number.
set -u
PATTERN='0\.1\.0|0\.2\.0|next release|not published|not signed off|until 0\.2\.0|newer than|first pypi release|after phase 3'
ALLOW=$(mktemp); HITS=$(mktemp); trap 'rm -f "$ALLOW" "$HITS"' EXIT
cat > "$ALLOW" <<'LIST'
README.md:uv tool install get-nick-done==0.2.0
docs/compatibility.md:Distribution `get-nick-done`, import and CLI `gnd` remain stable. Versions 0.1.0
docs/compatibility.md:and 0.2.0 are published (0.2.0 on PUBLICATION_DATE). For the next version,
docs/development/candidate.md:The artifact is `get_nick_done-0.1.0-py3-none-any.whl`. Its uncompressed payload
docs/index.md:uv tool install get-nick-done==0.2.0
docs/installation.md:uv tool install get-nick-done==0.2.0
docs/installation.md:python -m pip install get-nick-done==0.2.0
docs/installation.md:repository is private, access requires GitHub authentication. The `v0.2.0` tag
docs/installation.md:[v0.2.0 release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.2.0).
docs/installation.md:python -m pip install /path/to/get_nick_done-0.2.0-py3-none-any.whl
docs/marketplace-plugins.md:uv tool install get-nick-done==0.2.0
docs/marketplace-plugins.md:commands above work. The `v0.2.0` tag contains both the Python release and these
docs/releasing.md:were validated. This is how 0.1.0 was published.
docs/support.md:| Ubuntu, Python 3.11, uv 0.10.10 | Observed in Phase 3 acceptance of 0.1.0 |
docs/support.md:| macOS, Python 3.13, uv 0.10.10 | Observed in Phase 3 acceptance of 0.1.0 |
docs/support.md:| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.2.0 candidate built from `7c0f4d0e` |
LIST
git grep -i -E "$PATTERN" -- README.md docs ':!docs/release-notes.md' > "$HITS"
sed -n '1,10p' docs/release-notes.md | grep -i -E 'not published|prepared' | sed 's|^|docs/release-notes.md:|' >> "$HITS"
UNEXPECTED=$(grep -v -x -F -f "$ALLOW" "$HITS")
if [ -n "$UNEXPECTED" ]; then
  printf 'stale release-state text:\n%s\n' "$UNEXPECTED"
  exit 1
fi
echo "no stale release-state text ($(wc -l < "$HITS" | tr -d ' ') allowlisted hits)"
