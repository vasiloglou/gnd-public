"""Fill @OUT@ placeholders by running each gnd-run block as tools/run_tutorials.py does."""
import os, re, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, 'tools')
import run_tutorials as rt
page = Path(sys.argv[1]); text = page.read_text()
python = Path(sys.executable).absolute()
env = os.environ.copy()
for k in ('PYTHONPATH','PYTHONHOME','PYTEST_ADDOPTS','PYTEST_PLUGINS','GND_PYREL_PYTHON','GND_DISCLOSURE'):
    env.pop(k, None)
env['PATH'] = str(python.parent) + os.pathsep + env['PATH']; env['PYTHONUTF8'] = '1'
cwd = Path(tempfile.mkdtemp())
out = {}
for m in rt.MARKER.finditer(text):
    expected, stream, lang, code = int(m.group(1)), m.group(3), m.group(4), m.group(5)
    argv = [str(python), '-c', code] if lang == 'python' else ['/bin/bash', '-euo', 'pipefail', '-c', code]
    r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    assert r.returncode == expected, (code, r.returncode, r.stdout, r.stderr)
    if stream and m.group(6) == '@OUT@':
        out[m.start(6)] = '\n'.join(rt.normalize_output(r.stdout if stream == 'stdout' else r.stderr, cwd))
for start in sorted(out, reverse=True):
    text = text[:start] + out[start] + text[start + len('@OUT@'):]
page.write_text(text); print(len(out), 'outputs filled')
