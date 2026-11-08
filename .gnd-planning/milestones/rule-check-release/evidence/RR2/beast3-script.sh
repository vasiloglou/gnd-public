#!/bin/zsh
# RR2 B2 and V4 on beast-3 (spec D5). Writes run.log and a done marker.
R=$HOME/gnd-release/0.2.0/7c0f4d0e
C=7c0f4d0e320ff7976296d785077280d180ea688e
cd $R || exit 1
exec > run.log 2>&1
set -x
date -u +%FT%TZ; sw_vers; uname -m
# uv 0.10.10 (the workflow's pin), isolated: only the uv binary goes on PATH
$HOME/.local/bin/uv venv -q uv01010 && $HOME/.local/bin/uv pip install -q --python uv01010/bin/python uv==0.10.10
mkdir -p uvbin && ln -sf $R/uv01010/bin/uv uvbin/uv
export PATH=$R/uvbin:$PATH
uv --version
git clone -q -b rr2-candidate c.bundle checkout/gnd-public && git -C checkout/gnd-public checkout -q --detach $C || { echo 'CLONE FAILED'; touch $R/done; exit 1; }
test "$(git -C checkout/gnd-public rev-parse HEAD)" = $C || { echo 'HEAD IS NOT C'; touch $R/done; exit 1; }
echo "porcelain lines: $(git -C checkout/gnd-public status --porcelain | wc -l)"
# B2
mkdir -p b2/src && git -C checkout/gnd-public archive $C | tar -x -C b2/src
( cd b2/src && uv build --out-dir ../candidate/release && mkdir -p ../candidate/source \
  && tar -xzf ../candidate/release/*.tar.gz -C ../candidate/source \
  && uv build --wheel ../candidate/source/* --out-dir "$PWD/../candidate/comparison" \
  && rm -f ../candidate/release/.gitignore ../candidate/comparison/.gitignore \
  && echo $C > ../candidate/SOURCE_COMMIT && { python3 --version; uv --version; } > ../candidate/BUILD_PROFILE \
  && cd ../candidate && shasum -a 256 release/* comparison/* > SHA256SUMS && shasum -a 256 -c SHA256SUMS )
echo "B2 exit=$?"
test -e b2/candidate/SHA256SUMS || { echo 'B2 FAILED'; touch $R/done; exit 1; }
cat b2/candidate/SHA256SUMS b2/candidate/BUILD_PROFILE
echo "B1 vs B2:"; diff candidate-b1/SHA256SUMS b2/candidate/SHA256SUMS && echo "SHA256SUMS identical"
# V4 over B1's files, from a clean checkout at C, Python 3.11
cd checkout/gnd-public
uv sync --locked --group dev --python 3.11 || { echo 'SYNC FAILED'; touch $R/done; exit 1; }
uv run python --version
date -u +%FT%TZ
GND_CANDIDATE_DIR=$R/candidate-b1 uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short
echo "V4 exit=$?"
date -u +%FT%TZ
touch $R/done
