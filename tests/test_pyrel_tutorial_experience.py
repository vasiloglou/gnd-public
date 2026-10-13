"""Source bindings and observed tutorial steps, independent of visual opinions."""
import hashlib
import importlib.util
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('experience_runner', ROOT / 'tools/run_tutorials.py')
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)


def verify_graphic(domain, name):
    home = ROOT / 'src/gnd/examples' / domain
    assets = home / 'tutorial-assets'
    manifest = json.loads((assets / 'sources.json').read_text())
    row = manifest['graphics'][name]
    svg = (assets / (name + '.svg')).read_bytes()
    assert hashlib.sha256(svg).hexdigest() == row['sha256']
    assert svg == (ROOT / 'docs/assets/applications' / (domain + '-' + name + '.svg')).read_bytes()
    tree = ET.fromstring(svg)
    assert tree.find('{http://www.w3.org/2000/svg}title').text
    assert tree.find('{http://www.w3.org/2000/svg}desc').text
    text = ' '.join(tree.itertext())
    for label in row['labels']:
        assert label in text
    for check in row['checks']:
        source = (home / check['file']).read_bytes()
        assert hashlib.sha256(source).hexdigest() == check['sha256']
        value = json.loads(source)
        for part in check['path']:
            value = value[part]
        assert value == check['expected']
    return row


@pytest.mark.parametrize('domain,name', [('bookrec', 'flow'), ('bookrec', 'eligibility'),
    ('bookrec', 'evolution'), ('expense', 'flow'), ('expense', 'limits'), ('expense', 'currency')])
def test_graphic_sources_and_doc_twins(domain, name):
    assert verify_graphic(domain, name)['checks']


def test_observed_steps_include_skips_and_elapsed_time(tmp_path, monkeypatch):
    page = tmp_path / 'lesson.md'
    page.write_text('<!-- gnd-run expect=0 -->\n```python\nprint("ready")\n```\n'
                    '<!-- gnd-run expect=0 lane=pyrel -->\n```python\nraise RuntimeError()\n```')
    records = []
    assert runner.run_pages([page], tmp_path / 'work', Path(sys.executable), receipts=records) == 1
    assert [r['status'] for r in records] == ['passed', 'skipped']
    assert records[0]['actual_exit'] == 0 and records[0]['elapsed_seconds'] >= 0
    assert len(records[0]['stdout_sha256']) == 64
    assert 'elapsed_seconds' not in records[1]


def test_native_block_receives_explicit_base_python(tmp_path, monkeypatch):
    page = tmp_path / 'lesson.md'
    page.write_text('<!-- gnd-run expect=0 lane=pyrel -->\n```python\n'
                    'import os\nassert os.environ["GND_TUTORIAL_GND_PYTHON"]\n```')
    monkeypatch.setattr(runner, 'require_runtime', lambda *a: None)
    records = []
    assert runner.run_pages([page], tmp_path / 'work', Path(sys.executable), 'pyrel', receipts=records) == 1
    assert records[0]['lane'] == 'pyrel' and records[0]['status'] == 'passed'


def test_failed_step_cannot_produce_passed_receipt(tmp_path):
    page = tmp_path / 'lesson.md'
    page.write_text('<!-- gnd-run expect=0 -->\n```python\nraise SystemExit(1)\n```')
    records = []
    with pytest.raises(AssertionError, match='expected 0, got 1'):
        runner.run_pages([page], tmp_path / 'work', Path(sys.executable), receipts=records)
    assert not any(r['status'] == 'passed' for r in records)
