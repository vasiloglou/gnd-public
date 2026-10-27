#!/bin/bash
# The docs/pyrel-apps.md setup commands, verbatim except the clone source (local repo at HEAD).
set -euo pipefail
F="$1"; mkdir -p "$F"; cd "$F"
set -x
git clone -q <repo> gnd-public
git -C gnd-public log --oneline -1
uv venv gnd-env --python 3.13
uv pip install --python gnd-env/bin/python ./gnd-public
export GND_TUTORIAL_GND_PYTHON="$(pwd)/gnd-env/bin/python"
"$GND_TUTORIAL_GND_PYTHON" -c "from importlib.resources import files; import shutil; shutil.copytree(str(files('gnd').joinpath('examples', 'release_governance', 'runtime-environment')), 'pyrel-env')"
uv sync --project pyrel-env --locked --only-group tutorial-runtimes --python 3.13
export GND_TUTORIAL_PYREL_PYTHON="$(pwd)/pyrel-env/.venv/bin/python"
"$GND_TUTORIAL_GND_PYTHON" -c "import gnd; print('GND is ready')"
"$GND_TUTORIAL_PYREL_PYTHON" -c "from importlib.metadata import version as v; print('PyRel', v('relationalai'), 'with DuckDB', v('duckdb'))"
set +x
for g in bookrec expense; do
  PATH="$F/gnd-env/bin:$PATH" "$GND_TUTORIAL_GND_PYTHON" gnd-public/tools/run_tutorials.py --root gnd-public --group $g --lane pyrel --python "$GND_TUTORIAL_GND_PYTHON" 2>&1 | tail -2
done
