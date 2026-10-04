"""Bounded controls for the P1 fixed scaffold, not a public evidence validator."""
import collections
import hashlib
import json
import os
import re
import shutil
import stat
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MILESTONE = Path('.gnd-planning/milestones/public-launch')
REQUIRED = ['README.md', 'LICENSE', 'NOTICE', 'AGENTS.md', 'CONTRIBUTING.md',
            'SECURITY.md', '.gitignore', '.github/workflows/development.yml',
            'docs/development/bootstrap.md', '.gnd-planning/PROJECT.md',
            '.gnd-planning/open-questions.md',
            'src/gnd/skills/gnd-orm-core/references/milestone-record-format.md']


def check_references(root):
    for path in REQUIRED:
        assert (root / path).is_file(), path
    for path in root.rglob('*.md'):
        if any(part in {'.git', '.venv', '__pycache__'} for part in path.parts):
            continue
        for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in href or href.startswith('#'):
                continue
            assert (path.parent / href.split('#')[0]).exists(), (path, href)
    boot = (root / 'docs/development/bootstrap.md').read_text()
    assert 'No source-checkout bootstrap is required' in boot
    assert 'historical' in boot and 'Phase 3' in boot


def check_twins(root):
    left = root / '.codex/skills'
    right = root / '.claude/skills'
    for name in ['process-phase', 'plan-review-panel']:
        assert (left / name).is_dir() and not (left / name).is_symlink()
        assert (right / name).is_dir() and not (right / name).is_symlink()
        a = {p.relative_to(left / name) for p in (left / name).rglob('*') if p.is_file()}
        b = {p.relative_to(right / name) for p in (right / name).rglob('*') if p.is_file()}
        assert a == b and a
        for rel in a:
            p, q = left / name / rel, right / name / rel
            assert not p.is_symlink() and not q.is_symlink()
            assert p.read_bytes() == q.read_bytes()
            assert stat.S_IMODE(p.stat().st_mode) == stat.S_IMODE(q.stat().st_mode)
    names = {p.parent.name for p in (root/'src/gnd/skills').glob('*/SKILL.md')}
    assert len(names) == 16
    for base in [left, right]:
        links = {p.name:p for p in base.iterdir() if p.is_symlink()}
        assert set(links) == names
        for name, path in links.items():
            assert path.exists(), path
            target = root/'src/gnd/skills'/name
            assert path.resolve() == target.resolve(), path
            assert os.readlink(path) == os.path.relpath(target,path.parent), path


def check_exercise(root):
    for name in ['phase-spec.md', 'phase-record.md']:
        text = (root / 'docs/development/examples' / name).read_text()
        assert 'non-authoritative' in text and 'UNEXECUTED' in text
        assert 'owner approval' in text
        for heading in (['Provenance', 'Obligations', 'Standing rules', 'Goal', 'Design',
                         'Decisions', 'Tests', 'Out of scope', 'Size', 'Approval instrument']
                        if name == 'phase-spec.md' else
                        ['What shipped', 'Gate output', 'Evidence', 'Refactoring review',
                         'Boundary', 'Open questions']):
            assert '## ' + heading in text
    record = (root / 'docs/development/examples/phase-record.md').read_text()
    for field in ['milestone:', 'station:', 'skill:', 'scope:', 'date:', 'gate:',
                  'slow_cadence:', 'evidence:']:
        assert field in record
    assert not list((root / MILESTONE).glob('*example*'))


def check_ledger(root):
    ledger = json.loads((root / MILESTONE / 'migration/units.json').read_text())
    assert ledger['authority_transfer'] is False
    assert ledger['publisher_enabled'] is False
    assert len(ledger['units']) == 12
    assert all(u['authority'] == 'vasiloglou/gnd' and u['state'] == 'source-owned'
               for u in ledger['units'])
    q = ledger['question_states']
    assert len(q) == len({row['id'] for row in q}) == 218
    assert collections.Counter(row['state'] for row in q) == {
        'carried': 113, 'open': 6, 'closed': 96, 'superseded': 3}
    # Exact source ID/state list pin, not merely matching totals.
    payload = json.dumps(q, sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(payload).hexdigest() == QUESTION_PIN


def test_reference_closure_and_declared_bootstrap():
    check_references(ROOT)


def test_twins_modes_and_generated_links():
    check_twins(ROOT)


def test_non_authoritative_spec_record_exercise():
    check_exercise(ROOT)


def test_source_owned_units_and_preserved_question_states():
    check_ledger(ROOT)


@pytest.mark.evidence
def test_manifest_bytes_modes_and_sizes():
    # B1 is immutable historical selection; The current batch attributes changed bytes.
    from test_public_distribution import audit_tree, manifest
    b1_path = ROOT/MILESTONE/'migration/b1-files.json'
    assert hashlib.sha256(b1_path.read_bytes()).hexdigest() == '7e2bcccd41671743fdcedad2a856c78b59da7265256c0955256964554bb29c87'
    b1 = json.loads(b1_path.read_text())
    current = {r['path']:r for r in manifest(ROOT)['files']}
    for row in b1['files']:
        successor = current[row['path']]
        assert successor['baseline_sha256'] == row['public_sha256']
        if successor['public_sha256'] != row['public_sha256']:
            assert successor['kind'] == 'adaptation' and successor['reason']
    audit_tree(ROOT)


@pytest.mark.parametrize('mutation', ['missing-reference', 'twin-bytes', 'twin-mode',
                                   'broken-link', 'unlabeled-sample', 'missing-boundary',
                                   'fake-transfer', 'question-state'])
def test_controls_reject_isolated_mutations(tmp_path, mutation):
    staged = tmp_path / 'scaffold'
    shutil.copytree(ROOT, staged, symlinks=True, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__', '.pytest_cache', '.gnd-install.json'))
    if mutation == 'missing-reference':
        (staged / '.codex/skills/process-phase/references/standing-rules.md').unlink()
        check = check_references
    elif mutation in {'twin-bytes', 'twin-mode'}:
        p = staged / '.claude/skills/process-phase/SKILL.md'
        if mutation == 'twin-bytes':
            p.write_text(p.read_text() + 'drift\n')
        else:
            p.chmod(stat.S_IMODE(p.stat().st_mode) ^ stat.S_IXUSR)
        check = check_twins
    elif mutation == 'broken-link':
        os.symlink('missing', staged / '.codex/skills/dangling')
        check = check_twins
    elif mutation in {'unlabeled-sample', 'missing-boundary'}:
        p = staged / 'docs/development/examples/phase-record.md'
        text = p.read_text().replace('non-authoritative', 'unlabeled') if mutation == 'unlabeled-sample' else p.read_text().replace('## Boundary', '## Missing')
        p.write_text(text)
        check = check_exercise
    else:
        p = staged / MILESTONE / 'migration/units.json'
        data = json.loads(p.read_text())
        if mutation == 'fake-transfer':
            data['authority_transfer'] = True
            data['units'][0]['state'] = 'public-owned'
        else:
            data['question_states'][0]['state'] = 'closed'
        p.write_text(json.dumps(data))
        check = check_ledger
    with pytest.raises(AssertionError):
        check(staged)

QUESTION_PIN = "87a273c136ecd36e17a82e68a03babc096d6f46b03a09423ef26b3090125f447"


def test_readme_reflects_current_runtime_stage():
    text = (ROOT / 'README.md').read_text()
    assert 'Phase 3' in text and 'candidate sign-off remain pending' in text
    assert 'docs/quickstart.md' in text
    assert 'runtime migration follows' not in text


def test_ci_uses_verified_p2_build_profile():
    from ruamel.yaml import YAML
    workflow = YAML(typ='safe').load((ROOT / '.github/workflows/development.yml').read_text())
    for job in ['candidate', 'regression', 'installed']:
        pins = [step.get('with', {}).get('version') for step in workflow['jobs'][job]['steps']
                if step.get('uses') == 'astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e']
        assert pins == ['0.10.10']
    assert set(workflow['jobs']['phase2']['needs']) == {'candidate', 'regression', 'installed'}
