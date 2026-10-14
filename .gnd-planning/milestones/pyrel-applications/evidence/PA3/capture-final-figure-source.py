"""Capture fresh measured BookRec figure inputs; run from repository root."""
import hashlib
import json
from pathlib import Path
from gnd.export.applications import execute_application
root = Path.cwd()
example = root / 'src/gnd/examples/bookrec'
evidence = root / '.gnd-planning/milestones/pyrel-applications/evidence/PA3'
target = evidence / 'figure-source-final'
target.mkdir(exist_ok=False)
rows = []
for name, model, command, preferred in [('advisory', 'model.orm.yaml', 'recommend', 'false'), ('strict', 'strict.orm.yaml', 'recommend', 'false'), ('preferred', 'strict.orm.yaml', 'recommend', 'true'), ('complete', 'complete.orm.yaml', 'complete', 'true')]:
    out = target / (name + '.population.json')
    result = execute_application(example / model, example / 'seed.population.json', out, native_python=root / 'tutorials/runtimes/.venv/bin/python', query_script=example / 'extension/bookrec/native_query.py', owned_relations=('recommendation',), query_args=(command, 'ada', '2', preferred))
    path = target / (name + '.report.json')
    path.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    assert result['exit_code'] == (1 if name == 'strict' else 0), result
    rows.append({'scenario': name, 'model': (example / model).relative_to(root).as_posix(), 'model_sha256': hashlib.sha256((example / model).read_bytes()).hexdigest(), 'report': path.relative_to(root).as_posix(), 'report_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'candidate': out.relative_to(root).as_posix() if out.exists() else None, 'candidate_sha256': hashlib.sha256(out.read_bytes()).hexdigest() if out.exists() else None, 'exit_code': result['exit_code']})
previous = evidence / 'figure-source-review-repaired.json'
receipt = json.loads(previous.read_bytes())
receipt.update(scenarios=rows, parent_sha256=hashlib.sha256((root / 'src/gnd/export/applications.py').read_bytes()).hexdigest(), query_sha256=hashlib.sha256((example / 'extension/bookrec/native_query.py').read_bytes()).hexdigest(), predecessor=previous.relative_to(root).as_posix(), predecessor_sha256=hashlib.sha256(previous.read_bytes()).hexdigest(), initial_source_snapshots=['parent-figure-initial.py', 'query-figure-initial.py'])
(evidence / 'figure-source.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
print('four native scenarios measured on repaired parent/query bytes')
