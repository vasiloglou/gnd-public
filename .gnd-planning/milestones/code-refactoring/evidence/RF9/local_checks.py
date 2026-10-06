"""RF9 current graph and frozen-source checks; no production mutations."""
import ast
import importlib
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).parent
arch = runpy.run_path(str(ROOT / 'tools/gnd_arch.py'))
metrics = arch['measure'](ROOT, ROOT / 'tools/gnd_layers.json')
assert not metrics['sccs']['runtime']
assert not metrics['sccs']['module_only']
assert not metrics['layering']['wrong_way']
assert not metrics['entrypoints']['violations']
assert not subprocess.check_output(['git', 'diff', 'd440b2e', '--', 'src', 'tests', 'tools'], cwd=ROOT)
frozen = json.loads((OUT.parent / 'RF8/frozen-controls.json').read_text())['unchanged']
for row in frozen:
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
bindings = []
for name in ('gnd.model', 'gnd.checker', 'gnd.agent_cli', 'gnd.assurance',
             'gnd.assurance_claims', 'gnd.assurance_evidence',
             'gnd.assurance_inheritance', 'gnd.assurance_transport',
             'gnd.exp.session', 'gnd.exp.session_store', 'gnd.exp.session_v7',
             'gnd.artifacts'):
    old_path = 'src/' + name.replace('.', '/') + '.py'
    source = subprocess.check_output(['git', 'show', 'f5a8318:' + old_path], cwd=ROOT, text=True)
    names = set()
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name) and not t.id.startswith('__'))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    current = importlib.import_module(name)
    missing = sorted(n for n in names if not hasattr(current, n))
    assert not missing, (name, missing)
    bindings.append({'module': name, 'checked': len(names), 'names': sorted(names), 'missing': missing})
result = {'subject': 'd440b2e37449ef46647d18c491c46d9bb8d3e851',
          'module_count': len(metrics['modules']), 'sccs': metrics['sccs'],
          'layering': metrics['layering'], 'entrypoints': metrics['entrypoints'],
          'frozen_controls': len(frozen),
          'source_unchanged': True, 'predecessor_bindings': bindings,
          'largest_modules': sorted(metrics['modules'], key=lambda row: row.get('lines', row.get('loc', 0)), reverse=True)[:10]}
(OUT / 'local-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print('Graph: %d modules, zero SCC/wrong-way/entry violations; %d frozen controls unchanged; production unchanged.' % (len(metrics['modules']), len(frozen)))
print('Bindings: %d definitions/constants in %d selected modules remain importable; existence only.' % (sum(r['checked'] for r in bindings), len(bindings)))
