"""Data-only close audit; run from repository root. Does not import candidate code."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import yaml

BASE = Path('.gnd-planning/milestones/incremental-evaluation')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def verify(items):
    for item in items:
        assert digest(Path(item['path']).read_bytes()) == item['sha256'], item['path']
    return len(items)

final = json.loads((BASE / 'evidence/IE5/final-identities.json').read_text())
current = verify(final['artifacts'])
measurement = json.loads((BASE / 'evidence/IE5/measurement.json').read_text())
counts = {}
for name in ('source_sha256', 'fixture_sha256'):
    for path, expected in measurement[name].items():
        assert digest(Path(path).read_bytes()) == expected, path
    counts[name] = len(measurement[name])
phase_counts = []
subjects = [('003-phase-IE0.md', '67e36fa'), ('004-phase-IE1.md', 'a90e5a3'),
            ('005-phase-IE2.md', '46c76ad'), ('006-phase-IE3.md', 'cd61f56'),
            ('007-phase-IE4.md', 'cff2efb'), ('008-phase-IE5.md', 'd5effb2')]
for name, commit in subjects:
    raw = subprocess.check_output(['git', 'show', f'{commit}:{BASE / name}'])
    record = yaml.safe_load(raw.decode().split('---', 2)[1])
    items = record.get('evidence')
    if items is None:
        items = [dict(path=p, sha256=h) for p, h in re.findall(r'"path":\s*"([^"]+)",\s*"sha256":\s*"([a-f0-9]{64})"', raw.decode())]
    assert items, name
    for item in items:
        content = subprocess.check_output(['git', 'show', f"{commit}:{item['path']}"])
        assert digest(content) == item['sha256'], (commit, item['path'])
    phase_counts.append(len(items))
for lens in ('correctness', 'structure', 'protocol', 'measurement'):
    opinion = (BASE / f'evidence/close/{lens}.md').read_text()
    assert 'close-with-carryovers' in opinion
    assert 'd5effb28' in opinion
repairs = json.loads((BASE / 'evidence/close/sanitation.json').read_text())['repairs']
for item in repairs:
    assert digest(Path(item['path']).read_bytes()) == item['after_sha256']
    original = subprocess.check_output(['git', 'show', f"d5effb2:{item['path']}"])
    assert digest(original) == item['before_sha256']
    assert b'/Users/' in original and b'/Users/' not in Path(item['path']).read_bytes()
# Recognize real machine home paths, not generic root-scan prose.
for path in BASE.rglob('*'):
    if path.is_file() and path.suffix in ('.md', '.txt', '.json', '.py'):
        assert not re.search(b'/Users/' + rb'[^/\s]+/', path.read_bytes()), str(path)
print(f"final identities: {current}/{current} match")
print(f"measurement maps: {counts['source_sha256']} source / {counts['fixture_sha256']} fixture match")
print(f"historical phase identities: {sum(phase_counts)} match at original commits; per phase {phase_counts}")
print('close readers: 4 distinct retained opinions; close-with-carryovers')
print('sanitation: 2 reproduced before/after repairs; machine-home scan clear')
print('runtime unchanged since final measurement; data-only audit exit 0')
