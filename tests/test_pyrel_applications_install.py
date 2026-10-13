"""Red-first fresh-install resource and origin boundaries."""
import importlib.util
import zipfile
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]


def tool():
    path=ROOT/'tools/accept_pyrel_applications_install.py'
    assert path.exists(),'fresh-install acceptance harness is absent'
    spec=importlib.util.spec_from_file_location('pa_install',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def wheel(tmp_path,omit=None,change=None):
    target=tmp_path/'candidate.whl'
    with zipfile.ZipFile(target,'w') as archive:
        for file in (ROOT/'src/gnd').rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts:
                name=file.relative_to(ROOT/'src').as_posix()
                if name==omit:continue
                archive.writestr(name,b'changed' if name==change else file.read_bytes())
    return target


def test_candidate_resources_match_source(tmp_path):
    assert tool().verify_wheel_resources(wheel(tmp_path),ROOT)['resources']


@pytest.mark.parametrize('name',['gnd/examples/bookrec/tutorial-assets/eligibility.svg',
    'gnd/examples/expense/tutorial-assets/currency.svg','gnd/examples/expense/native_query.py',
    'gnd/examples/bookrec/tutorial-assets/checkpoints/omission-refusal.input.json'])
def test_missing_required_resource_refuses(tmp_path,name):
    with pytest.raises(ValueError,match='missing'):
        tool().verify_wheel_resources(wheel(tmp_path,omit=name),ROOT)


def test_changed_resource_refuses(tmp_path):
    with pytest.raises(ValueError,match='changed'):
        tool().verify_wheel_resources(wheel(tmp_path,change='gnd/examples/expense/native_query.py'),ROOT)


def test_malformed_wheel_refuses(tmp_path):
    path=tmp_path/'bad.whl';path.write_text('not zip')
    with pytest.raises(ValueError,match='wheel'):
        tool().verify_wheel_resources(path,ROOT)


def test_origin_rejects_checkout_and_sibling(tmp_path):
    module=tool();venv=tmp_path/'venv';checkout=tmp_path/'source'
    module.verify_origin(venv/'lib/gnd/__init__.py',venv,checkout)
    for origin in [checkout/'src/gnd/__init__.py',tmp_path/'venv-sibling/lib/gnd/__init__.py']:
        with pytest.raises(ValueError,match='origin'):
            module.verify_origin(origin,venv,checkout)
