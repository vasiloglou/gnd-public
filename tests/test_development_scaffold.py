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

NM_HOME = Path('.gnd-planning/milestones/why-not-near-misses')
MG_HOME = Path('.gnd-planning/milestones/model-growth-guardrails')
CT_HOME = Path('.gnd-planning/milestones/composition-and-type-induction')

# These links identify the original operator's retained, external run evidence.
# The historical report is immutable; their presence on a fresh checkout is not
# part of reference closure. Exempt only its enumerated targets, not arbitrary
# absolute paths or every link under evidence/.
RETAINED_EXTERNAL_REFERENCES = {
    # Verbatim reviewer output quoting test code and a mutant input; neither is a document link.
    Path('.gnd-planning/milestones/release-0.3.0/notes/phase-RN1-codex-review.md'): {
        '{link}', 'explanation/ossie.md'},
    # Verbatim close-review output quoting one table row of the close record, whose link is
    # relative to that record's directory.
    Path('.gnd-planning/milestones/release-0.3.0/notes/close-codex-review.md'): {
        '004-phase-RN2.md'},
    Path('.gnd-planning/milestones/code-refactoring/evidence/RF9-ci-repair/baseline-report.md'): {
        '/private/tmp/gnd-local-ci-20261006-d6f1e8a/' + name
        for name in (
            'status.json', 'followup-status.json', 'confirmed-failures.json',
            'failed-nodes.json', 'regression-311.log', 'regression-313.log',
            'failed-corrected-311.log', 'failed-corrected-313.log',
            'installed-corrected-311.log', 'installed-corrected-313.log',
            'corrected-artifact-hashes.log',
        )
    },
    # The IL6 reviewer's verbatim report quotes a README line in grep output.
    Path('.gnd-planning/milestones/ilp-learners/notes/phase-IL6-agent-review.md'): {
        'notes/phase-IL6-spec.md',
    },
    # The RC6 reviewer's verbatim report quotes two docs/reference/cli.md rows.
    Path('.gnd-planning/milestones/rule-check-adoption/notes/phase-RC6-codex-review.md'): {
        'rule-check-report.md', '../how-to/adopt-rules-with-a-baseline.md',
    },
    # The FU5 reviewer's verbatim report links two files by absolute worktree path.
    Path('.gnd-planning/milestones/rule-check-followups/notes/phase-FU5-codex-review-impl.md'): {
        ('/Users/nikolaosvasiloglou/github-repos/gnd-public/.claude/worktrees/intelligent-pasteur-df4027/'
        '.gnd-planning/milestones/code-refactoring/notes/shim-inventory.md:755'),
        ('/Users/nikolaosvasiloglou/github-repos/gnd-public/.claude/worktrees/intelligent-pasteur-df4027/'
        '.gnd-planning/milestones/rule-check-followups/notes/phase-FU5-spec.md:122'),
    },
    # The RR3 spec's D6 row quotes proposed docs text with an elided link target.
    Path('.gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md'): {'…'},
    # The NM4 DC2 draft quotes new text for several docs pages, links as written.
    NM_HOME / 'checkpoints/DC2/changes.md': {
        'disclosure.md', 'disclosure.md#who-customer-mode-protects',
        'disclosure.md#what-customer-mode-refuses', 'why-not.md',
        '../reference/disclosure.md', 'reference/disclosure.md',
    },
    # Verbatim Fable draft's proposed placeholder; final pages cite the format home.
    Path('.gnd-planning/milestones/model-composition/notes/phase-MC4-fable-draft.md'): {
        '../reference/model-includes.md'},
}

# Review snapshots preserve the exact original text, including relative links.
# Validate those links from their original document home, never exempt them.
IE_HOME = Path('.gnd-planning/milestones/incremental-evaluation')
IK_HOME = Path('.gnd-planning/milestones/induced-knowledge')
MC_HOME = Path('.gnd-planning/milestones/model-composition')
OS_HOME = Path('.gnd-planning/milestones/ossie-interchange')
RETAINED_DOCUMENT_ORIGINS = {
    # release-0.3.0 RN1: two ossie-interchange spec snapshots, pinned by their phase records.
    OS_HOME / 'evidence/OS1/spec-r1.md': (
        OS_HOME / 'notes/phase-OS1-spec.md',
        'b17b774364ce381b5ff3173a0b5546b377fec7a2044275ae31c45fc39a853353'),
    OS_HOME / 'evidence/OS0/spec-r4.md': (
        OS_HOME / 'notes/phase-OS0-spec.md',
        '47b62ba0eac4edb5772e4886b5b1a360343a6cfc9a5330e24e6f4cb4b1c5eefd'),
    MC_HOME / 'notes/phase-MC4-fable-draft.md': (
        Path('docs/tutorials/shared-expense-policies.md'),
        '4a3cdd3d4cb802fc91eaa7ebb75ef3f9374c5391eae5a747483eb789b3b05ea7'),
    IE_HOME / 'evidence/plan-review-r1/incremental-evaluation-plan.md': (
        IE_HOME / 'notes/incremental-evaluation-plan.md',
        '34b1004e9d7e5e60f3162dae423e78b3d42bf98678edcccc0ad358517f086de1'),
    IE_HOME / 'evidence/plan-review-r1/phase-IE0-spec.md': (
        IE_HOME / 'notes/phase-IE0-spec.md',
        'd49a5bcc4f06b5f1b500bd231637d54dcedc2bd9778976ba5817edb6a9ba19da'),
    IE_HOME / 'evidence/plan-approval/incremental-evaluation-plan.md': (
        IE_HOME / 'notes/incremental-evaluation-plan.md',
        'b7503db4af6ab7ab5916e0c0fa8a6f7bbcbe6aab5464e9fdd99422fe53e160b1'),
    IK_HOME / 'evidence/plan-review-r1/induced-knowledge-plan.md': (
        IK_HOME / 'notes/induced-knowledge-plan.md',
        '26fa91632e5ee637b1949ad4e8dd6ba25daac57180280328e3d04c1e050a1814'),
    IK_HOME / 'evidence/plan-review-r1/phase-IK1-spec.md': (
        IK_HOME / 'notes/phase-IK1-spec.md',
        'f79d6375630e8706a9a3fe88af7669b3f0a81fcbb446ec0e1d55d4df22b8cec0'),
    IK_HOME / 'evidence/plan-review-r2/induced-knowledge-plan.md': (
        IK_HOME / 'notes/induced-knowledge-plan.md',
        'd1a40a89eecad01e7e4dc72e969beb4c548297c1967df0d268c6776c18207c85'),
    IK_HOME / 'evidence/plan-review-r2/phase-IK1-spec.md': (
        IK_HOME / 'notes/phase-IK1-spec.md',
        '4f4cb8b580c680e5523d6cf1f4a4752abe3d76099a19c713620c51e8e5d3cac1'),
    NM_HOME / 'checkpoints/DC1/disclosure.md': (
        Path('docs/reference/disclosure.md'),
        'df5b92d56b59ebe0e8af1e166ea3de6038530d05ef0e12ef97643046082f77f6'),
    NM_HOME / 'checkpoints/DC1b/disclosure-mode.md': (
        Path('docs/how-to/disclosure-mode.md'),
        '1b89b59939f21e416db8fb9fe0bf47f42924f89b3276e5a61acd858c0962f3c2'),
    NM_HOME / 'checkpoints/DC2/docs/how-to/disclosure-mode.md': (
        Path('docs/how-to/disclosure-mode.md'),
        '4e1caa9d58d5e5b5e49efaa9b2f518b4c4383d98fb7c78171f087dec78c82c89'),
    NM_HOME / 'checkpoints/DC2/docs/reference/disclosure.md': (
        Path('docs/reference/disclosure.md'),
        'e24ba07319c29019b940bfff6bd1b6513baf6c627b89058b1ef764d28ff2c527'),
    MG_HOME / 'checkpoints/DC2/docs/how-to/grow-a-model.md': (
        Path('docs/how-to/grow-a-model.md'),
        'ce7d6295166cf753462adfe67def063215163c17c81fc5c627a4df3e30e03eeb'),
    CT_HOME / 'checkpoints/DC2/docs/how-to/compose-documents.md': (
        Path('docs/how-to/compose-documents.md'),
        '47705a00acc19320e7c91899b8974d2a0c4a4de17ed4f98c42e8d55bfabee448'),
    MC_HOME / 'evidence/MC1/002-approved-spec.md': (
        MC_HOME / 'notes/phase-MC1-spec.md',
        '5179c82f8e6b953d49257b4b5dd50383955de5061bd89cf0455b4f33703d0a5f'),
    MC_HOME / 'evidence/MC1/003-approved-spec.md': (
        MC_HOME / 'notes/phase-MC1-spec.md',
        '7b471ea27b46918e25dcaacc3a558c052232eb70d29c9810b1bb9d3ea51c13ce'),
    MC_HOME / 'evidence/MC1/004-approved-spec.md': (
        MC_HOME / 'notes/phase-MC1-spec.md',
        '6483b4f8d9da57ea05c3ad6225fc94102ab4ca84dd87ec20969ebf81ea7a5c33'),
    MC_HOME / 'evidence/MC1/005-approved-spec.md': (
        MC_HOME / 'notes/phase-MC1-spec.md',
        'f06505f3194bf191d9d3318ad37f007d0dac10b80d3bb0a56fdcaf1d88ee6662'),
    MC_HOME / 'evidence/plan-review-r1/model-composition-plan.r1.md': (
        MC_HOME / 'notes/model-composition-plan.md',
        'bd661eeede495e2c3c82e9fbd81cfa6d79f7d2a8d0f77c4374f20736f6d1597a'),
    MC_HOME / 'evidence/plan-review-r1/phase-MC1-spec.r1.md': (
        MC_HOME / 'notes/phase-MC1-spec.md',
        'b6ebc5db0b9ecaba0992380ff43f05d865d05415a2dbcbebf9016200a4c06dff'),
    MC_HOME / 'evidence/plan-review-r2/model-composition-plan.r2.md': (
        MC_HOME / 'notes/model-composition-plan.md',
        '2dc91f4e4aee8279ae5feb9695face7b2820e243ccb56e3db1749b4f73bc438a'),
    MC_HOME / 'evidence/plan-review-r2/phase-MC1-spec.r2.md': (
        MC_HOME / 'notes/phase-MC1-spec.md',
        'e8f6cf85ab0d4ae988727f9143ad52fb6dc38e3f328f4acce32b7cfb6ef4a07f'),
}


def check_document_references(root, path):
    relative = path.relative_to(root)
    base = path.parent
    if relative in RETAINED_DOCUMENT_ORIGINS:
        original, digest = RETAINED_DOCUMENT_ORIGINS[relative]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, relative
        base = (root / original).parent
    for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' in href or href.startswith(('#', '<')):
            continue
        if href in RETAINED_EXTERNAL_REFERENCES.get(relative, ()):
            continue
        assert (base / href.split('#')[0]).exists(), (path, href)


def check_references(root):
    for path in REQUIRED:
        assert (root / path).is_file(), path
    for path in root.rglob('*.md'):
        if any(part in {'.git', '.venv', '__pycache__'} for part in path.parts):
            continue
        check_document_references(root, path)
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
    assert len(names) == 18
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


@pytest.mark.parametrize('snapshot', RETAINED_DOCUMENT_ORIGINS)
@pytest.mark.parametrize('mutation', ['none', 'changed-snapshot', 'missing-target'])
def test_retained_document_origin_still_checks_bytes_and_targets(tmp_path, snapshot, mutation):
    path = tmp_path / snapshot
    path.parent.mkdir(parents=True)
    path.write_bytes((ROOT / snapshot).read_bytes())
    original, _digest = RETAINED_DOCUMENT_ORIGINS[snapshot]
    targets = []
    for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' in href or href.startswith(('#', '<')):
            continue
        target = (tmp_path / original).parent / href.split('#')[0]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
        targets.append(target)
    assert targets
    if mutation == 'changed-snapshot':
        path.write_text(path.read_text() + '\nchanged\n')
    elif mutation == 'missing-target':
        targets[0].unlink()
    if mutation == 'none':
        check_document_references(tmp_path, path)
    else:
        with pytest.raises(AssertionError):
            check_document_references(tmp_path, path)


@pytest.mark.parametrize('case', ['retained', 'other-document', 'unknown-target', 'relative'])
def test_retained_external_reference_exception_is_bounded(tmp_path, case):
    for name in REQUIRED:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('')
    (tmp_path / 'docs/development/bootstrap.md').write_text(
        'No source-checkout bootstrap is required; historical Phase 3.\n'
    )
    report, targets = next(iter(RETAINED_EXTERNAL_REFERENCES.items()))
    target = min(targets)
    if case == 'other-document':
        report = Path('docs/current.md')
    elif case == 'unknown-target':
        target = '/private/tmp/gnd-local-ci-20261006-d6f1e8a/unknown.json'
    elif case == 'relative':
        target = 'missing.json'
    path = tmp_path / report
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'[evidence]({target})\n')
    if case == 'retained':
        check_references(tmp_path)
    else:
        with pytest.raises(AssertionError):
            check_references(tmp_path)


def test_twins_modes_and_generated_links():
    check_twins(ROOT)


def test_non_authoritative_spec_record_exercise():
    check_exercise(ROOT)


def test_source_owned_units_and_preserved_question_states():
    check_ledger(ROOT)


@pytest.mark.evidence
def test_manifest_bytes_modes_and_sizes():
    # B1 is immutable historical selection; The current batch attributes changed bytes.
    # The r3 amendment retired whole-tree attribution, so new files need no manifest row.
    from test_public_distribution import manifest
    b1_path = ROOT/MILESTONE/'migration/b1-files.json'
    assert hashlib.sha256(b1_path.read_bytes()).hexdigest() == '7e2bcccd41671743fdcedad2a856c78b59da7265256c0955256964554bb29c87'
    b1 = json.loads(b1_path.read_text())
    current = {r['path']:r for r in manifest(ROOT)['files']}
    for row in b1['files']:
        successor = current[row['path']]
        assert successor['baseline_sha256'] == row['public_sha256']
        if successor['public_sha256'] != row['public_sha256']:
            assert successor['kind'] == 'adaptation' and successor['reason']


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


def test_readme_links_to_executable_getting_started():
    from test_contributor_preparation import check_links
    check_links(ROOT / 'README.md')
    assert (ROOT / 'docs/quickstart.md').is_file()


def test_ci_uses_verified_p2_build_profile():
    from ruamel.yaml import YAML
    workflow = YAML(typ='safe').load((ROOT / '.github/workflows/development.yml').read_text())
    for job in ['candidate', 'regression', 'installed']:
        pins = [step.get('with', {}).get('version') for step in workflow['jobs'][job]['steps']
                if step.get('uses') == 'astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e']
        assert pins == ['0.10.10']
    assert set(workflow['jobs']['phase2']['needs']) == {'candidate', 'regression', 'installed'}
