"""Reject a legacy helper mutation; no evaluator execution or timing."""
import importlib.util
import sys
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('comparison_under_test', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='ie6-identity-negative-') as temp:
    root = Path(temp)
    (root/'tools').mkdir()
    (root/'pyproject.toml').write_text('')
    (root/'uv.lock').write_text('')
    (root/'tools/measure_incremental_evaluation.py').write_text('')
    helper = (root/'src/gnd/examples/plan_apps/course/model.orm.json'
              if '--course' in sys.argv else root/'tools/measure_transition_cost.py')
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text('original = 1\n')
    before = module.identity(root)
    helper.write_text('changed = 2\n')
    assert before != module.identity(root), 'runtime input mutation escaped identity map'
print('runtime-input mutation rejected')
