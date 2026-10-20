"""Data-only IE6 identity/parity/privacy audit; never imports candidate GND."""
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path.cwd().resolve()
HOME = ROOT / '.gnd-planning/milestones/incremental-evaluation'
E = HOME / 'evidence/IE6'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subjects(mapping, root):
    for relative, expected in mapping.items():
        path = (root / relative).resolve()
        assert path.is_relative_to(root) and not Path(relative).is_absolute()
        assert digest(path) == expected, relative


def self_test():
    with tempfile.TemporaryDirectory(prefix='ie6-audit-negative-') as temp:
        root = Path(temp).resolve()
        (root/'probe').write_text('real')
        subjects({'probe': digest(root/'probe')}, root)
        try:
            subjects({'probe': '0'*64}, root)
        except AssertionError:
            pass
        else:
            raise AssertionError('corrupt identity accepted')
    print('identity corruption negative live')


def main():
    self_test()
    accepted = json.loads((E/'acceptance.json').read_text())
    subjects(accepted['subjects'], ROOT)
    m = json.loads((E/'measurement.json').read_text())
    subjects(m['source_sha256'], ROOT)
    subjects(m['fixture_sha256'], ROOT)
    expected = {'reporter': [2]*13, 'course': [1,1,0], 'localized': [1]*6}
    for name, values in expected.items():
        modes = m['workloads'][name]['modes']
        for mode in 'ABC':
            assert [r['exit'] for r in modes[mode]['calls']] == values
        for a,b,c in zip(*(modes[x]['calls'] for x in 'ABC'), strict=True):
            for key in ('payload','exit','branches'):
                assert a[key] == b[key] == c[key]
            assert b['calculations'] == c['calculations']
    reporter = m['workloads']['reporter']['modes']
    assert reporter['B']['actual_work']['derivation_body_evaluations'] == 4878
    assert reporter['C']['actual_work']['derivation_body_evaluations'] == 179
    life = m['lifetime']
    assert all(value == 0 for value in life['body_deltas'][1:])
    assert all(life['after_close'][key] == 0 for key in ('entries','rows','bytes'))
    comparison = json.loads((E/'revision-comparison.json').read_text())
    subjects(comparison['identities']['candidate'], ROOT)
    subjects(comparison['identities']['baseline'], Path('/private/tmp/ie6-baseline').resolve())
    assert comparison['driver_sha256'] == digest(E/'compare_revisions.py')
    for name,data in comparison['workloads'].items():
        assert len(data['observations']) == 9
        for observation in data['observations']:
            assert observation['driver_sha256'] == comparison['driver_sha256']
            assert observation['exits'] == expected[name]
    wheel = json.loads((E/'wheel-manifest.json').read_text())
    archive = Path(wheel['wheel_path'])
    assert digest(archive) == wheel['wheel_sha256']
    with zipfile.ZipFile(archive) as z:
        assert {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith('/')} == wheel['members_sha256']
    old = subprocess.run(['git','show','d0ffd9a:.gnd-planning/milestones/incremental-evaluation/009-milestone-close.md'], check=True, capture_output=True).stdout
    assert old == (HOME/'009-milestone-close.md').read_bytes()
    prefix = '/' + 'Users' + '/'
    for relative in accepted['subjects']:
        path = ROOT / relative
        assert prefix not in path.read_text(), relative
    print(f"phase identities: {len(accepted['subjects'])} match; current measurement maps verified")
    print('complete ordered parity and frozen bodies 4878/179 verified; close clears retained state')
    print('both revision maps/driver identities match; all timed census/exits valid')
    print('wheel archive manifest verified; historical009 unchanged; machine-home scan clear')
    if '--close' in sys.argv:
        close = json.loads((HOME/'evidence/IE6-close/acceptance.json').read_text())
        subjects(close['subjects'], ROOT)
        assert len(close['reviewers']) == len(set(close['reviewers'])) == 4
        print('renewed close: four distinct retained opinions and exact acceptance subjects verified')
    print('data-only IE6 audit exit 0')


if __name__ == '__main__':
    main()
