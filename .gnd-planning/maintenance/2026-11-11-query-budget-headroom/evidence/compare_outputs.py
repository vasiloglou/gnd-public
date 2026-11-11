"""Digest the outputs of the directly callable converted functions over every loadable model.

Run once with the base source tree first on sys.path and once with the head tree; the two
JSON files must be equal.  usage: python -I compare_outputs.py SRC_DIR REPO_ROOT OUT.json
An exception is an output too: its type and message are digested.
"""
import hashlib
import json
import sys
from pathlib import Path

src, root, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, src)

import gnd

assert Path(gnd.__file__).resolve().is_relative_to(Path(src).resolve()), gnd.__file__

from gnd.codegen.emit import render_skill_document
from gnd.coverage import _element_universe
from gnd.diff import _structured
from gnd.extract.projection import project
from gnd.model import load_model
from gnd.synth.frontier import frontier_codes_for
from gnd.vocabulary import render_verbalization

CALLS = {
    'diff._structured': _structured,
    'synth.frontier.frontier_codes_for': frontier_codes_for,
    'vocabulary.render_verbalization': render_verbalization,
    'extract.projection.project': project,
    'coverage._element_universe': _element_universe,
    'codegen.emit.render_skill_document': lambda m: render_skill_document(
        m, model_path='m.orm.yaml', package='pkg', stem='m'),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()


result, outcomes = {}, {name: {'value': 0, 'error': 0} for name in CALLS}
paths = sorted([*root.glob('examples/**/*.orm.yaml'), *root.glob('tests/fixtures/**/*.orm.yaml')])
for path in paths:
    try:
        model = load_model(path)
    except Exception:  # noqa: BLE001, S112 -- deliberately invalid fixtures are not models
        continue
    for name, call in CALLS.items():
        try:
            value, kind = call(model), 'value'
        except Exception as error:  # noqa: BLE001 -- the exception is the compared output
            value, kind = [type(error).__name__, str(error)], 'error'
        outcomes[name][kind] += 1
        result[f'{path.relative_to(root).as_posix()}::{name}'] = f'{kind}:{digest(value)}'
out.write_text(json.dumps({'outcomes': outcomes, 'digests': result}, indent=1, sort_keys=True) + '\n')
print(json.dumps(outcomes))
