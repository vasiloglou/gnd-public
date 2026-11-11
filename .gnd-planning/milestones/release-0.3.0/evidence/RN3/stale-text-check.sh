#!/bin/sh
# Stale release-state text check (release-0.3.0 RN3, M3), adapted from
# rule-check-release/evidence/RR3/stale-text-check.sh. Run from the repository
# root after applying the three post-publication patches and replacing
# PUBLICATION_DATE:
#
#   sh stale-text-check.sh token      # the ruled route: the retained 4c07c0e6 files
#
# Exit 0: every hit of the search is allowlisted and the release notes open
# with the published 0.3.0 state. Exit 1: stale text, a PUBLICATION_DATE left
# in place, or a missing published-state line; each is printed. Exit 2: usage
# or search error. The allowlist holds the text that is right once 0.3.0 is
# published, or is historical; it is matched by exact file:line-text, not line
# number, with any ISO date read as <DATE>.
set -u
usage() { echo "usage: $0 token" >&2; exit 2; }
[ $# -eq 1 ] && [ "$1" = token ] || usage
BUILT='4c07c0e6'
PATTERN='0\.1\.0|0\.2\.0|0\.3\.0|next release|not published|not signed off|prepared 0|newer than|unreleased (feature|example)|development checkout for'
ALLOW=$(mktemp) && HITS=$(mktemp) && PROBLEMS=$(mktemp) || exit 2
trap 'rm -f "$ALLOW" "$HITS" "$PROBLEMS" "$PROBLEMS.bak" "$HITS.bak"' EXIT
cat > "$ALLOW" <<'LIST'
README.md:uv tool install get-nick-done==0.3.0
docs/compatibility.md:Distribution `get-nick-done`, import and CLI `gnd` remain stable. Versions 0.1.0,
docs/compatibility.md:0.2.0 and 0.3.0 are published (0.3.0 on <DATE>). For the next version,
docs/development/candidate.md:The artifact is `get_nick_done-0.1.0-py3-none-any.whl`. Its uncompressed payload
docs/explanation/ossie.md:GND supports Ossie ontology version `0.3.0.dev0`. The export schema and
docs/how-to/shared-expense-policies-commands.md:The feature is in GND 0.3.0 and later; see [installation](../installation.md).
docs/index.md:uv tool install get-nick-done==0.3.0
docs/installation.md:uv tool install get-nick-done==0.3.0
docs/installation.md:python -m pip install get-nick-done==0.3.0
docs/installation.md:[v0.3.0 release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.3.0).
docs/installation.md:python -m pip install /path/to/get_nick_done-0.3.0-py3-none-any.whl
docs/marketplace-plugins.md:uv tool install get-nick-done==0.3.0
docs/marketplace-plugins.md:commands above work. The `v0.3.0` tag contains both the Python release and these
docs/releasing.md:were validated. This is how 0.1.0 was published.
docs/support.md:| Ubuntu, Python 3.11, uv 0.10.10 | Observed in Phase 3 acceptance of 0.1.0 |
docs/support.md:| macOS, Python 3.13, uv 0.10.10 | Observed in Phase 3 acceptance of 0.1.0 |
docs/support.md:| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.2.0 candidate built from `7c0f4d0e` |
docs/tutorials/shared-expense-policies.md:**Before you start.** Install GND 0.3.0 or later, as the
LIST
# The new support row names the build that was published.
printf '%s\n' "docs/support.md:| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.3.0 candidate built from \`$BUILT\` |" >> "$ALLOW"

# A placeholder date is never published text; it is checked before dates are normalised.
git grep -n -F 'PUBLICATION_DATE' -- README.md docs > "$PROBLEMS"
status=$?
[ $status -le 1 ] || { echo "search error ($status)" >&2; exit 2; }
[ $status -eq 1 ] || sed -i.bak 's/^/placeholder left in place: /' "$PROBLEMS"

# The search must succeed and find the published-state lines: without the
# 0.3.0 pins the patches are missing or the search is wrong.
git grep -i -E "$PATTERN" -- README.md docs ':!docs/release-notes.md' | sed -E 's/^([^:]+):/\1:/' > "$HITS"
[ -s "$HITS" ] || { echo "the search found nothing" >&2; exit 2; }
grep -q -F 'README.md:uv tool install get-nick-done==0.3.0' "$HITS" ||
  { echo "README.md has no 0.3.0 install pin: are the post-publication patches applied?" >&2; exit 2; }
NOTES=docs/release-notes.md
[ -r "$NOTES" ] || { echo "cannot read $NOTES" >&2; exit 2; }
sed -n '1,14p' "$NOTES" | grep -i -E 'not published|prepared|not in any published' | sed "s|^|$NOTES:|" >> "$HITS"
grep -n -i -E 'requires the development checkout' "$NOTES" | sed -E "s|^[0-9]+:|$NOTES:|" >> "$HITS"
sed -i.bak -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/<DATE>/g' "$HITS"
grep -v -x -F -f "$ALLOW" "$HITS" | sed 's/^/stale: /' >> "$PROBLEMS"

# The notes must state the published 0.3.0 directly: the opening sentence,
# and exactly one dated 0.3.0 heading.
grep -q -E '^Version 0\.3\.0, published on [0-9]{4}-[0-9]{2}-[0-9]{2}, is the latest release; 0\.2\.0 and$' "$NOTES" ||
  echo "missing: $NOTES opening 'Version 0.3.0, published on <DATE>, is the latest release'" >> "$PROBLEMS"
[ "$(grep -c -E '^## 0\.3\.0 \([0-9]{4}-[0-9]{2}-[0-9]{2}\)$' "$NOTES")" -eq 1 ] ||
  echo "missing: exactly one '## 0.3.0 (<DATE>)' heading in $NOTES" >> "$PROBLEMS"

if [ -s "$PROBLEMS" ]; then
  echo 'stale release-state text:'
  cat "$PROBLEMS"
  exit 1
fi
echo "no stale release-state text ($(wc -l < "$HITS" | tr -d ' ') allowlisted hits, route $1, build $BUILT)"
