#!/bin/zsh
set -u
W=$1; C=$2
cd $W
E=.gnd-planning/milestones/rule-check-release/evidence/RR3
CHK() { sh $W/$E/stale-text-check.sh "$@"; }
reset() { git checkout -q --detach $C && git reset -q --hard $C && git clean -q -fd -- README.md docs tests; }
applyall() { for p in post-publication post-publication-tag post-publication-release-files; do git apply $E/$p.patch || echo "apply $p failed"; done; }
fill() { sed -i '' 's/PUBLICATION_DATE/2026-11-09/g' docs/release-notes.md docs/compatibility.md; }
PYT() { uv run --quiet pytest -q -o addopts='' -p no:cacheprovider "$@" 2>&1 | grep -E '^(FAILED|[0-9]+ (passed|failed))' ; }
run() { echo "\$ stale-text-check.sh $*"; CHK "$@" 2>&1; echo "exit $?"; }
reset
echo "RR3 checks at $C ($(date -u +%FT%TZ)), scratch worktree."
echo; echo "### T1 git apply --check, each patch alone"
for p in post-publication post-publication-tag post-publication-release-files; do git apply --check $E/$p.patch; echo "$p: exit $?"; done
echo; echo "### T6 the RR3 tree"; PYT tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py
echo; echo "### T5 liveness: the RR3 tree (expect exit 1, printing the stale hits)"; run token
echo; echo "### T5 usage and search errors (expect exit 2)"; run; run workflow 7c0f4d0; cd /; echo "\$ (outside any repository) stale-text-check.sh token"; sh $W/$E/stale-text-check.sh token 2>&1; echo "exit $?"; cd $W
applyall
echo; echo "### T5 all three patches, PUBLICATION_DATE kept (expect exit 1, J3)"; run token
fill
echo; echo "### T2 all three patches, date 2026-11-09 filled in"; PYT tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py
echo; echo "### T5 all three patches, date filled, route token (expect exit 0)"; run token
echo; echo "### T5 same tree, route workflow with another build (expect exit 1 on the 7c0f4d0e row, J5)"; run workflow 25f58b5e
sed -i '' 's/built from `7c0f4d0e`/built from `25f58b5e`/' docs/support.md
echo; echo "### T5 support row reworded for that build (expect exit 0)"; run workflow 25f58b5e
reset; applyall; fill
python3 - <<'PY'
p='docs/release-notes.md'; t=open(p).read()
t=t.replace('Version 0.2.0, published on 2026-11-09, is the latest release; 0.1.0 was the\nfirst.','Version 0.1.0 is the latest release.',1)
open(p,'w').write(t)
PY
echo; echo "### T5 J4 mutant: notes opening reverted to name 0.1.0, heading kept (expect exit 1)"; run token
reset; applyall; fill; sed -i '' 's/^## 0\.2\.0 (2026-11-09)$/## 0.2.0/' docs/release-notes.md
echo; echo "### T5 J4 mutant: undated 0.2.0 heading (expect exit 1)"; run token
reset; git apply $E/post-publication.patch; fill
echo; echo "### T5 main patch only, date filled (expect exit 1, the tag and release-file lines)"; run token
reset; git apply $E/post-publication.patch $E/post-publication-tag.patch; fill; sed -i '' 's/get-nick-done==0\.2\.0/get-nick-done==0.1.0/' README.md
echo; echo "### T3b one pin left at 0.1.0 after publication (README)"; PYT tests/test_release_version.py
reset; git apply $E/post-publication.patch; fill
python3 - <<'PY'
p='tests/test_release_version.py'; t=open(p).read()
t=t.replace('RELEASED = {"0.1.0", "0.2.0"}','RELEASED = {"0.1.0"}',1); open(p,'w').write(t)
PY
echo; echo "### T3 main patch without the RELEASED hunk"; PYT tests/test_release_version.py
reset; applyall
echo; echo "### T4 placeholder left in place"; PYT tests/test_release_version.py
reset; git show 12daa5b7:docs/releasing.md > docs/releasing.md
echo; echo "### T7 mutant: base releasing.md restored"; PYT tests/test_release_docs.py
reset; echo; echo "final status lines: $(git status --porcelain | wc -l | tr -d ' ')"
