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
    texts = [element.text for element in tree.findall('{http://www.w3.org/2000/svg}text')]
    for file, digest in manifest['sources'].items():
        assert hashlib.sha256((home / file).read_bytes()).hexdigest() == digest
    for binding in manifest['bindings']:
        model_sha = hashlib.sha256((home / binding['model']).read_bytes()).hexdigest()
        input_sha = hashlib.sha256((home / binding['input']).read_bytes()).hexdigest()
        assert model_sha == binding['model_sha256'] and input_sha == binding['input_sha256']
        report = json.loads((home / binding['report']).read_text())
        if report['policy'] is not None:
            assert report['policy']['binding']['model_sha256'] == model_sha
        if 'candidate' in binding:
            candidate_sha = hashlib.sha256((home / binding['candidate']).read_bytes()).hexdigest()
            assert candidate_sha == binding['candidate_sha256']
            assert report['policy']['binding']['population_sha256'] == candidate_sha
        if binding.get('audit_input'):
            assert report['policy']['binding']['population_sha256'] == input_sha
        if 'source_binding' in report:
            assert report['source_binding'] == {'model_sha256': model_sha, 'input_sha256': input_sha}
    for value_label in row.get('value_labels', []):
        value = json.loads((home / value_label['file']).read_text())
        for part in value_label['path']:
            value = value[part]
        assert value == value_label['expected']
        if isinstance(value, list):
            assert len(value) == 1
            value = value[0]
        assert value_label['template'].format(value=value) in texts
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
    native=tmp_path/'native-python';native.symlink_to(sys.executable)
    monkeypatch.setenv('GND_TUTORIAL_PYREL_PYTHON',str(native))
    page = tmp_path / 'lesson.md'
    page.write_text('<!-- gnd-run expect=0 lane=pyrel -->\n```python\n'
                    f'import os,sys\nassert os.environ["GND_TUTORIAL_GND_PYTHON"] == {sys.executable!r}\nassert sys.executable == {str(native)!r}\n```')
    monkeypatch.setattr(runner, 'require_runtime', lambda *a: None)
    records = []
    assert runner.run_pages([page], tmp_path / 'work', Path(sys.executable), 'pyrel', receipts=records) == 1
    assert records[0]['lane'] == 'pyrel' and records[0]['status'] == 'passed'
    assert records[0]['base_python']==sys.executable and records[0]['block_python']==str(native)


def test_failed_step_cannot_produce_passed_receipt(tmp_path):
    page = tmp_path / 'lesson.md'
    page.write_text('<!-- gnd-run expect=0 -->\n```python\nraise SystemExit(1)\n```')
    records = []
    with pytest.raises(AssertionError, match='expected 0, got 1'):
        runner.run_pages([page], tmp_path / 'work', Path(sys.executable), receipts=records)
    assert not any(r['status'] == 'passed' for r in records)


@pytest.mark.parametrize('domain,source', [('bookrec','src/gnd/examples/bookrec/extension/bookrec/native_query.py'), ('expense','src/gnd/examples/expense/native_query.py')])
def test_rendered_query_snippet_matches_owned_source(domain, source):
    assert (ROOT / source).read_bytes() == (ROOT / 'docs/assets/applications' / (domain + '-native-query.txt')).read_bytes()


@pytest.mark.parametrize('domain,page', [('bookrec','07-native.md'),('expense','04-native.md')])
def test_mobile_scroll_regions_are_keyboard_accessible(domain,page):
    source=(ROOT/'docs'/domain/page).read_text()
    assert source.count('tabindex="0"') == 3
    assert source.count('role="region"') == 3
    assert 'scroll horizontally' in source


@pytest.mark.parametrize('value',[{}, 1, 'receipt'])
def test_receipt_container_is_checked_before_work(tmp_path,value):
    with pytest.raises(AssertionError,match='receipts must be a list or None'):
        runner.run_pages([],tmp_path/'absent',Path(sys.executable),receipts=value)
    assert not (tmp_path/'absent').exists()


@pytest.mark.parametrize('existing',[True,False])
def test_invalid_receipt_destination_refuses_before_execution(tmp_path,monkeypatch,existing):
    receipt=tmp_path/'receipt.json' if existing else tmp_path/'absent'/'receipt.json'
    if existing: receipt.write_text('prior evidence')
    monkeypatch.setattr(sys,'argv',['run_tutorials','--group','bookrec','--receipt',str(receipt)])
    monkeypatch.setattr(runner,'run_pages',lambda *a,**k:pytest.fail('executed before receipt validation'))
    with pytest.raises(SystemExit) as error: runner.main()
    assert error.value.code==2
    if existing: assert receipt.read_text()=='prior evidence'


@pytest.mark.parametrize('domain,page',[('bookrec','07-native.md'),('expense','04-native.md')])
def test_reader_prose_separates_words_and_numbers(domain,page):
    import re
    prose=re.sub(r'```.*?```','',(ROOT/'docs'/domain/page).read_text(),flags=re.DOTALL)
    assert not re.search(r'[A-Za-z][0-9]',prose)


@pytest.mark.parametrize('domain,mutation',[('expense','currency-model'),('expense','currency-enum-expanded'),('expense','limit-label'),('bookrec','refusal-input')])
def test_graphic_binding_mutations_fail(tmp_path,monkeypatch,domain,mutation):
    import shutil
    home=tmp_path/'src/gnd/examples'/domain
    shutil.copytree(ROOT/'src/gnd/examples'/domain,home)
    target=tmp_path/'docs/assets/applications';target.mkdir(parents=True)
    for source in (ROOT/'docs/assets/applications').glob(domain+'-*.svg'):shutil.copy2(source,target/source.name)
    monkeypatch.setitem(globals(),'ROOT',tmp_path)
    name='currency' if mutation in {'currency-model','currency-enum-expanded'} else 'limits' if mutation=='limit-label' else 'eligibility'
    if mutation=='currency-enum-expanded':
        p=home/'currency.orm.json';data=json.loads(p.read_text());data['constraints'][12]['allowed'].append('USD');p.write_text(json.dumps(data))
        manifest=home/'tutorial-assets/sources.json';data=json.loads(manifest.read_text());data['sources']['currency.orm.json']=hashlib.sha256(p.read_bytes()).hexdigest();manifest.write_text(json.dumps(data))
    elif mutation=='currency-model':
        p=home/'currency.orm.json';p.write_text(p.read_text().replace('"EUR"','"USD"'))
    elif mutation=='refusal-input':
        p=home/'tutorial-assets/checkpoints/adult-refusal.input.json';p.write_text('{}')
    else:
        p=home/'tutorial-assets/limits.svg';p.write_text(p.read_text().replace('category 75','category 70'))
        shutil.copy2(p,target/'expense-limits.svg')
        manifest=home/'tutorial-assets/sources.json';data=json.loads(manifest.read_text())
        data['graphics']['limits']['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();manifest.write_text(json.dumps(data))
    with pytest.raises(AssertionError):verify_graphic(domain,name)


def test_pyrel_selection_requires_explicit_native_interpreter(tmp_path,monkeypatch):
    monkeypatch.delenv('GND_TUTORIAL_PYREL_PYTHON',raising=False)
    with pytest.raises(AssertionError,match='required explicit native interpreter'):
        runner.require_runtime('pyrel',Path(sys.executable),{'PATH':'/bin'})


def test_receipt_race_preserves_other_writer(tmp_path,monkeypatch):
    receipt=tmp_path/'receipt.json'
    monkeypatch.setattr(sys,'argv',['run_tutorials','--group','bookrec','--receipt',str(receipt)])
    def race(*args,**kwargs):
        receipt.write_text('other writer')
        return 0
    monkeypatch.setattr(runner,'run_pages',race)
    with pytest.raises(SystemExit) as error:runner.main()
    assert error.value.code==2 and receipt.read_text()=='other writer'


def test_page_mutation_refuses_bound_run(tmp_path):
    page=tmp_path/'lesson.md'
    page.write_text('<!-- gnd-run expect=0 -->\n```python\nfrom pathlib import Path\n'
                    f'Path({str(page)!r}).write_text("changed")\n```')
    with pytest.raises(AssertionError,match='page changed during execution'):
        runner.run_pages([page],tmp_path/'work',Path(sys.executable))


@pytest.mark.parametrize('name',['flow','limits','currency'])
def test_svg_accessible_and_visible_text_spacing(name):
    import re
    tree=ET.fromstring((ROOT/'src/gnd/examples/expense/tutorial-assets'/(name+'.svg')).read_bytes())
    for element in list(tree.findall('{http://www.w3.org/2000/svg}text'))+[tree.find('{http://www.w3.org/2000/svg}desc')]:
        assert not re.search(r'[A-Za-z][0-9]|[:;·+=][0-9]',element.text)


@pytest.mark.parametrize('native',['relative/python',sys.executable])
def test_native_path_contract_refuses_before_probe(monkeypatch,native):
    monkeypatch.setattr(runner.subprocess,'run',lambda *a,**k: type('Result',(),{'returncode':0,'stdout':'PyRel 1.30.1\nDuckDB 1.5.5','stderr':''})())
    with pytest.raises(AssertionError,match='absolute separate native interpreter'):
        runner.require_runtime('pyrel',Path(sys.executable),{'PATH':'/bin','GND_TUTORIAL_PYREL_PYTHON':native})
