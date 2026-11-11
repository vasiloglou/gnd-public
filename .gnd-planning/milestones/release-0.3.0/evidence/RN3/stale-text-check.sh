#!/bin/sh
# Stale release-state text check (release-0.3.0 RN3, M3), adapted from
# rule-check-release/evidence/RR3/stale-text-check.sh. Run from the repository
# root after applying the three post-publication patches and replacing
# PUBLICATION_DATE:
#
#   sh .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh token
#
# `token` is the ruled route: the retained 4c07c0e6 files, uploaded by the owner.
#
# Exit 0: every hit of the search is allowlisted, the release notes open with
# the published 0.3.0 state, and the notes' opening, the notes' heading and
# the compatibility page give the same publication date. Exit 1: stale text,
# a PUBLICATION_DATE left in place, a missing or competing published-state
# line, or dates that disagree; each is printed. Exit 2: usage or search
# error. The allowlist holds the text that is right once 0.3.0 is published,
# or is historical; it is matched by exact file:line-text, not line number,
# with any ISO date read as <DATE>.
set -u
usage() { echo "usage: $0 token" >&2; exit 2; }
[ $# -eq 1 ] && [ "$1" = token ] || usage
BUILT='4c07c0e6'
PATTERN='0\.1\.0|0\.2\.0|0\.3\.0|next release|not published|not signed off|prepared 0|newer than|unreleased (feature|example)|development checkout'
NOTES=docs/release-notes.md
COMPAT=docs/compatibility.md
ALLOW=$(mktemp) && RAW=$(mktemp) && HITS=$(mktemp) && PROBLEMS=$(mktemp) || exit 2
trap 'rm -f "$ALLOW" "$RAW" "$HITS" "$PROBLEMS"' EXIT
[ -r "$NOTES" ] && [ -r "$COMPAT" ] || { echo "cannot read $NOTES or $COMPAT" >&2; exit 2; }
cat > "$ALLOW" <<'LIST'
README.md:uv tool install get-nick-done==0.3.0
docs/compatibility.md:Distribution `get-nick-done`, import and CLI `gnd` remain stable. Versions 0.1.0,
docs/compatibility.md:0.2.0 and 0.3.0 are published (0.3.0 on <DATE>). For the next version,
docs/development/candidate.md:The artifact is `get_nick_done-0.1.0-py3-none-any.whl`. Its uncompressed payload
docs/explanation/ossie.md:GND supports Ossie ontology version `0.3.0.dev0`. The export schema and
docs/how-to/shared-expense-policies-commands.md:The feature is in GND 0.3.0 and later. Install it with pip in an activated
docs/index.md:uv tool install get-nick-done==0.3.0
docs/installation.md:uv tool install get-nick-done==0.3.0
docs/installation.md:python -m pip install get-nick-done==0.3.0
docs/installation.md:[v0.3.0 release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.3.0).
docs/installation.md:python -m pip install /path/to/get_nick_done-0.3.0-py3-none-any.whl
docs/marketplace-plugins.md:uv tool install get-nick-done==0.3.0
docs/marketplace-plugins.md:commands above work. The `v0.3.0` tag contains both the Python release and these
docs/marketplace-plugins.md:not register the development checkout in the user's marketplace configuration.
docs/releasing.md:were validated. This is how 0.1.0 was published.
docs/support.md:| Ubuntu, Python 3.11, uv 0.10.10 | Observed in Phase 3 acceptance of 0.1.0 |
docs/support.md:| macOS, Python 3.13, uv 0.10.10 | Observed in Phase 3 acceptance of 0.1.0 |
docs/support.md:| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.2.0 candidate built from `7c0f4d0e` |
docs/tutorials/shared-expense-policies.md:**Before you start.** Install GND 0.3.0 or later with pip in an activated virtual environment, as the
LIST
# The new support row names the build that was published.
printf '%s\n' "docs/support.md:| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.3.0 candidate built from \`$BUILT\` |" >> "$ALLOW"

# Each search is captured to a file and its own status is read: a search that
# fails part way must not pass as a clean one. git grep exits 1 for no match.
search() {  # search <output> <git grep arguments...>
  out=$1; shift
  git grep "$@" > "$out"
  status=$?
  [ $status -le 1 ] || { echo "search error ($status): git grep $*" >&2; exit 2; }
}

# A placeholder date is never published text; it is checked before dates are normalised.
search "$RAW" -n -F 'PUBLICATION_DATE' -- README.md docs
sed 's/^/placeholder left in place: /' "$RAW" >> "$PROBLEMS"

# The published state must be stated: without the 0.3.0 pin the patches are missing.
search "$RAW" -n -F 'get-nick-done==0.3.0' -- README.md
[ -s "$RAW" ] || echo "missing: README.md has no 0.3.0 install pin (are the post-publication patches applied?)" >> "$PROBLEMS"

# Hits outside the notes: every one must be allowlisted.
search "$RAW" -i -E "$PATTERN" -- README.md docs ':!docs/release-notes.md'
[ -s "$RAW" ] || { echo "the search found nothing" >&2; exit 2; }
cp "$RAW" "$HITS"
# The notes: the opening lines must not carry the prepared state, and no
# section may still require a checkout.
sed -n '1,14p' "$NOTES" | grep -i -E 'not published|prepared|not in any published' | sed "s|^|$NOTES:|" >> "$HITS"
grep -i -E 'requires the development checkout' "$NOTES" | sed "s|^|$NOTES:|" >> "$HITS"

# One publication date, taken from the notes' opening, which must be the
# first paragraph (line 3) and the only "latest release" statement there.
OPENING=$(sed -n '3p' "$NOTES")
DATE=$(printf '%s\n' "$OPENING" | sed -n -E 's/^Version 0\.3\.0, published on ([0-9]{4}-[0-9]{2}-[0-9]{2}), is the latest release; 0\.2\.0 and$/\1/p')
if [ -z "$DATE" ]; then
  echo "missing: $NOTES line 3 is not 'Version 0.3.0, published on <DATE>, is the latest release; 0.2.0 and'" >> "$PROBLEMS"
else
  [ "$(sed -n '1,7p' "$NOTES" | grep -c -i 'latest release')" -eq 1 ] ||
    echo "competing: more than one 'latest release' statement in the opening of $NOTES" >> "$PROBLEMS"
  [ "$(grep -c -E '^## 0\.3\.0 \(' "$NOTES")" -eq 1 ] && grep -q -x -F "## 0.3.0 ($DATE)" "$NOTES" ||
    echo "missing: exactly one '## 0.3.0 ($DATE)' heading in $NOTES (the opening's date)" >> "$PROBLEMS"
  grep -q -F "0.2.0 and 0.3.0 are published (0.3.0 on $DATE)." "$COMPAT" ||
    echo "missing: $COMPAT does not give the opening's date, $DATE, for 0.3.0" >> "$PROBLEMS"
fi

# Dates are normalised only for the allowlist comparison, after the date checks above.
sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/<DATE>/g' "$HITS" > "$RAW"
grep -v -x -F -f "$ALLOW" "$RAW" | sed 's/^/stale: /' >> "$PROBLEMS"

if [ -s "$PROBLEMS" ]; then
  echo 'stale release-state text:'
  cat "$PROBLEMS"
  exit 1
fi
echo "no stale release-state text ($(wc -l < "$RAW" | tr -d ' ') allowlisted hits, route $1, build $BUILT, published $DATE)"
