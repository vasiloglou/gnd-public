"""Read-only RF9 CI repair evidence and frozen-boundary assertions."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair'
BASE = 'd6f1e8aeacab902914e22b2dab799b65f879fdda'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


frozen = json.loads((OUT.parent / 'RF8/frozen-controls.json').read_text())['unchanged']
for row in frozen:
    assert digest(ROOT / row['path']) == row['sha256'], row['path']
path = '.gnd-planning/milestones/public-launch/migration/b3-files.json'
before = json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))
original = {row['path']: row for row in before['files']}
current = {row['path']: row for row in json.loads((ROOT / path).read_text())['files']}
for row in json.loads((OUT / 'manifest-adaptations.json').read_text()):
    assert row['before'] == original.get(row['path'])
    assert row['after'] == current[row['path']]
    actual = ROOT / row['path']
    assert row['after']['public_sha256'] == digest(actual)
    assert row['after']['bytes'] == actual.stat().st_size
    assert row['after']['mode'] == actual.stat().st_mode & 0o777
    if row['before']:
        for field in ('baseline_sha256', 'source_sha256', 'source_commit'):
            assert row['before'].get(field) == row['after'].get(field)
identity = json.loads((OUT / 'production-source-identity.json').read_text())
assert {row['path'] for row in identity['files']} == {p.relative_to(ROOT).as_posix() for p in (ROOT / 'src/gnd').rglob('*.py')}
for row in identity['files']:
    assert digest(ROOT / row['path']) == row['sha256'], row['path']
for name, sha in json.loads((OUT / 'final-neighbor-status.json').read_text())['file_sha256'].items():
    assert digest(ROOT / name) == sha, name
for name in ('.gnd-planning/milestones/public-launch/migration/units.json', 'tests/test_public_distribution.py'):
    assert subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT) == (ROOT / name).read_bytes()
print(f'{len(frozen)} frozen controls unchanged; exact27 adaptations; {len(identity["files"])} production files identical to733389d; current observer identities match.')
