#!/bin/sh
# Stale release-state text check (rule-check-release RR3, M4). Run from the
# repository root after applying the post-publication patches:
#
#   sh stale-text-check.sh token              # route (a): the retained 7c0f4d0e files
#   sh stale-text-check.sh workflow <sha8>    # route (b): the workflow's build of <sha8>
#
# Exit 0: every hit of the RR3 search is allowlisted and the release notes open
# with the published 0.2.0 state. Exit 1: stale text, a PUBLICATION_DATE left
# in place, or a missing published-state line; each is printed. Exit 2: usage
# or search error. The allowlist holds the text that is right once 0.2.0 is
# published, or is historical; it is matched by exact file:line-text, not line
# number, with any ISO date read as <DATE>.
set -u
usage() { echo "usage: $0 token | workflow <8-hex source commit>" >&2; exit 2; }
case "${1:-}" in
  token) [ $# -eq 1 ] || usage; BUILT='7c0f4d0e' ;;
  workflow) [ $# -eq 2 ] || usage
    printf '%s' "$2" | grep -q -x -E '[0-9a-f]{8}' || usage; BUILT=$2 ;;
  *) usage ;;
esac
PATTERN='0\.1\.0|0\.2\.0|next release|not published|not signed off|until 0\.2\.0|newer than|first pypi release|after phase 3'
ALLOW=$(mktemp) && HITS=$(mktemp) && PROBLEMS=$(mktemp) || exit 2
trap 'rm -f "$ALLOW" "$HITS" "$PROBLEMS"' EXIT
cat > "$ALLOW" <<'LIST'
README.md:uv tool install get-nick-done==0.2.0
docs/compatibility.md:Distribution `get-nick-done`, import and CLI `gnd` remain stable. Versions 0.1.0
docs/compatibility.md:and 0.2.0 are published (0.2.0 on <DATE>). For the next version,
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
LIST
# The new support row names the build that was published (J5): the retained
# candidate under the token route, the workflow's own commit under the other.
printf '%s\n' "docs/support.md:| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.2.0 candidate built from \`$BUILT\` |" >> "$ALLOW"

# A placeholder date is never published text (J3); it is checked before dates
# are normalised.
git grep -n -F 'PUBLICATION_DATE' -- README.md docs > "$PROBLEMS"
status=$?
[ $status -le 1 ] || { echo "search error ($status)" >&2; exit 2; }
[ $status -eq 1 ] || sed -i.bak 's/^/placeholder left in place: /' "$PROBLEMS"

# The search must succeed and find the expected published-state lines (J2):
# zero hits means the patches are missing or the search is wrong.
git grep -i -E "$PATTERN" -- README.md docs ':!docs/release-notes.md' > "$HITS"
status=$?
[ $status -le 1 ] || { echo "search error ($status)" >&2; exit 2; }
[ -s "$HITS" ] || { echo "the search found nothing: are the post-publication patches applied?" >&2; exit 2; }
NOTES=docs/release-notes.md
[ -r "$NOTES" ] || { echo "cannot read $NOTES" >&2; exit 2; }
sed -n '1,10p' "$NOTES" | grep -i -E 'not published|prepared|is the published release' | sed "s|^|$NOTES:|" >> "$HITS"
sed -i.bak -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/<DATE>/g' "$HITS"
grep -v -x -F -f "$ALLOW" "$HITS" | sed 's/^/stale: /' >> "$PROBLEMS"

# The notes must state the published 0.2.0 directly (J4), not merely lack
# the old words: the opening sentence, and exactly one dated 0.2.0 heading.
grep -q -E '^Version 0\.2\.0, published on [0-9]{4}-[0-9]{2}-[0-9]{2}, is the latest release; 0\.1\.0 was the$' "$NOTES" ||
  echo "missing: $NOTES opening 'Version 0.2.0, published on <DATE>, is the latest release'" >> "$PROBLEMS"
[ "$(grep -c -E '^## 0\.2\.0 \([0-9]{4}-[0-9]{2}-[0-9]{2}\)$' "$NOTES")" -eq 1 ] ||
  echo "missing: exactly one '## 0.2.0 (<DATE>)' heading in $NOTES" >> "$PROBLEMS"
rm -f "$PROBLEMS.bak" "$HITS.bak"

if [ -s "$PROBLEMS" ]; then
  echo 'stale release-state text:'
  cat "$PROBLEMS"
  exit 1
fi
echo "no stale release-state text ($(wc -l < "$HITS" | tr -d ' ') allowlisted hits, route $1, build $BUILT)"
