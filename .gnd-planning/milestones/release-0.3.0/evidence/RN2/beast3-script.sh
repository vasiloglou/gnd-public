#!/bin/zsh
# RN2 B2 and V4 on beast-3 (spec M3, D2), adapted from the predecessor's
# rule-check-release/evidence/RR2/beast3-script-run2.sh.
# Fresh directory; any failed step stops the script; status is written last.
R=$HOME/gnd-release/0.3.0/4c07c0e6
W=$R/run1
C=4c07c0e6a623263048cb675d237046ebb239cb32
test ! -e $W || { echo "run1 exists"; exit 1; }
mkdir -p $W && cd $W || exit 1
exec > run.log 2>&1
setopt ERR_EXIT PIPE_FAIL
trap 'echo "STOPPED at line $LINENO (exit $?)"; echo failed > $W/status' ZERR
set -x
date -u +%FT%TZ; sw_vers; uname -m
# uv 0.10.10, the workflow's pin: the binary of `uvx --from uv==0.10.10`, found by the uv package itself
UVBIN=$($HOME/.local/bin/uvx --from uv==0.10.10 python -c 'import uv; print(uv.find_uv_bin())')
echo "uv binary: $UVBIN"
mkdir -p uvbin && ln -s $UVBIN uvbin/uv
export PATH=$W/uvbin:$PATH
uv --version
# the retained B1 copy on this host
( cd $R/candidate-b1 && shasum -a 256 -c SHA256SUMS )
test "$(cat $R/candidate-b1/SOURCE_COMMIT)" = $C
git clone -q -b rn2-candidate $R/c.bundle checkout/gnd-public
git -C checkout/gnd-public checkout -q --detach $C
test "$(git -C checkout/gnd-public rev-parse HEAD)" = $C
test -z "$(git -C checkout/gnd-public status --porcelain)"
# B2
mkdir -p b2/src
git -C checkout/gnd-public archive $C | tar -x -C b2/src
cd b2/src
uv build --out-dir ../candidate/release
mkdir -p ../candidate/source
tar -xzf ../candidate/release/*.tar.gz -C ../candidate/source
uv build --wheel ../candidate/source/* --out-dir "$PWD/../candidate/comparison"
rm -f ../candidate/release/.gitignore ../candidate/comparison/.gitignore
echo $C > ../candidate/SOURCE_COMMIT
{ python3 --version; uv --version; } > ../candidate/BUILD_PROFILE
cd ../candidate
shasum -a 256 release/* comparison/* > SHA256SUMS
shasum -a 256 -c SHA256SUMS
cat SHA256SUMS BUILD_PROFILE
diff $R/candidate-b1/SHA256SUMS SHA256SUMS
echo "B1 and B2 SHA256SUMS identical"
# V4 over B1's files, from the clean checkout at C, Python 3.11
cd $W/checkout/gnd-public
uv sync --locked --group dev --python 3.11
uv run python --version
date -u +%FT%TZ
GND_CANDIDATE_DIR=$R/candidate-b1 uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short
echo "V4 exit=0"
# V5: the uvx form, from the retained wheel
uvx --from $R/candidate-b1/release/get_nick_done-0.3.0-py3-none-any.whl gnd --version
date -u +%FT%TZ
echo passed > $W/status
