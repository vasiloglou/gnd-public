"""Run from the frozen repository root; emit the T51 program baseline."""
import hashlib
import json
from pathlib import Path

from gnd.export.emit import render_pyrel

path = Path('src/gnd/examples/rule_check/model.orm.yaml')
runtime = Path('src/gnd/export/pyrel_runtime.py')
print(json.dumps({'source_commit': '459ca8d2', 'source_model': path.as_posix(),
    'model_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'runtime_sha256': hashlib.sha256(runtime.read_bytes()).hexdigest(),
    'duckdb_path': ':memory:', 'connection': None,
    'program_sha256': hashlib.sha256(render_pyrel(path).encode()).hexdigest()}, indent=2))
