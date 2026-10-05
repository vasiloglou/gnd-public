from __future__ import annotations

import ast
import builtins
import importlib
import json
import runpy
import subprocess
import sys
import time
import tomllib
from pathlib import Path

import pytest
from pyrel_export_support import (
    ANSWERS,
    BASICS,
    POPULATION,
    REPO,
    RUNTIME,
    cli,
    export,
    require_export,
)


def test_export_header_compile_and_determinism(tmp_path: Path) -> None:
    program = export(tmp_path)
    source = program.read_text()
    assert source.startswith((ANSWERS / 'header.txt').read_text())
    compile(source, str(program), 'exec')
    program.unlink()
    assert export(tmp_path).read_bytes() == source.encode()
    assert RUNTIME.read_text() in source
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            assert all(a.name.split('.')[0] != 'gnd' for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert not node.level and (node.module or '').split('.')[0] != 'gnd'

def test_export_is_offline_and_importable_without_rai(tmp_path: Path, monkeypatch) -> None:
    require_export()
    original_import = builtins.__import__

    def restricted(name, *args, **kwargs):
        assert name.split('.')[0] != 'relationalai', 'export imported relationalai'
        return original_import(name, *args, **kwargs)

    def no_process(*args, **kwargs):
        raise AssertionError('export started a subprocess')
    monkeypatch.setattr(builtins, '__import__', restricted)
    monkeypatch.setattr(subprocess, 'Popen', no_process)
    emitter = importlib.import_module('gnd.export.emit')
    source = emitter.render_pyrel(BASICS)
    compile(source, 'export.py', 'exec')
    project = tomllib.loads((REPO / 'pyproject.toml').read_text())
    assert len(project['project']['dependencies']) == 3
    assert 'relationalai' not in (REPO / 'uv.lock').read_text()

@pytest.mark.parametrize('occupant', ['file', 'symlink', 'directory', 'model'])
def test_export_refuses_occupied_output(tmp_path: Path, occupant: str) -> None:
    require_export()
    target = tmp_path / 'output.py'
    marker = tmp_path / 'owner.txt'
    marker.write_text('owner bytes\n')
    if occupant == 'file':
        target.write_text('owner bytes\n')
    elif occupant == 'symlink':
        target.symlink_to(marker)
    elif occupant == 'directory':
        target.mkdir()
    else:
        target.write_bytes(BASICS.read_bytes())
    model = target if occupant == 'model' else BASICS
    before = target.read_bytes() if target.is_file() else None
    result = cli(str(model), '--out', str(target), cwd=tmp_path)
    assert result.returncode == 11, result.stderr
    assert marker.read_text() == 'owner bytes\n'
    if before is not None:
        assert target.read_bytes() == before
    if occupant == 'symlink':
        assert target.is_symlink()
    if occupant == 'directory':
        assert target.is_dir()

@pytest.mark.parametrize('case,expected', [('missing', 66), ('malformed', 3), ('options', 64), ('write', 70)])
def test_export_error_exits(tmp_path: Path, case: str, expected: int) -> None:
    require_export()
    model = tmp_path / 'model.yaml'
    model.write_bytes(BASICS.read_bytes())
    target = tmp_path / 'out.py'
    options = []
    if case == 'missing':
        model.unlink()
    elif case == 'malformed':
        model.write_text('[not a model]')
    elif case == 'options':
        options = ['--duckdb-path', 'db', '--connection', 'named']
    else:
        parent_file = tmp_path / 'not-a-directory'
        parent_file.write_text('owner')
        target = parent_file / 'out.py'
    result = cli(str(model), '--out', str(target), *options, cwd=tmp_path)
    assert result.returncode == expected, result.stderr
    assert not target.exists()
    assert 'Traceback' not in result.stderr

@pytest.mark.parametrize('kind', ['nonmapping', 'syntax', 'nonfinite', 'huge', 'deep', 'cap'])
def test_public_reader_rejects_hostile_bytes(tmp_path: Path, kind: str) -> None:
    require_export()
    runtime = runpy.run_path(str(RUNTIME))
    payloads = {'nonmapping': '[]', 'syntax': '{[', 'nonfinite': '{x: .nan}', 'huge': '{"x": ' + '1' * 10000 + '}', 'deep': '{"x":' + '[' * 2000 + '0' + ']' * 2000 + '}', 'cap': ' ' * (16777216 + 1)}
    source = tmp_path / 'hostile.yaml'
    source.write_text(payloads[kind])
    with pytest.raises(runtime['ExportInputError']):
        runtime['load_document'](source)

def test_public_reader_yaml12_and_bounded_read(tmp_path: Path) -> None:
    require_export()
    runtime = runpy.run_path(str(RUNTIME))
    source = tmp_path / 'document.yaml'
    source.write_text('on: true\nname: "on"\n')
    assert runtime['load_document'](source) == {'on': True, 'name': 'on'}
    with pytest.raises(runtime['ExportInputError']):
        runtime['load_document'](source, max_bytes=3)
    source.write_text('{"facts": {}, "instances": {}}')
    assert runtime['load_document'](source) == {'facts': {}, 'instances': {}}

def test_embedded_model_is_data_and_standalone(tmp_path: Path) -> None:
    require_export()
    document = tmp_path / 'model.yaml'
    text = BASICS.read_text()
    document.write_text(text + '\n# """; raise RuntimeError("injected") #\n')
    program = export(tmp_path, document)
    document.unlink()
    namespace = runpy.run_path(str(program))
    assert callable(namespace['program_main'])
    assert not (tmp_path / 'build').exists()

def test_export_and_admission_time_budget(tmp_path: Path) -> None:
    require_export()
    probe = tmp_path / 'timing.py'
    probe.write_text('import json, runpy, sys, time\nfrom pathlib import Path\nfrom ruamel.yaml import YAML\nfrom gnd.export.emit import render_pyrel\nbase, runtime_path, dest = map(Path, sys.argv[1:])\nruntime = runpy.run_path(str(runtime_path))\nmodel = YAML(typ="safe").load(base.read_text())\nstart = time.monotonic()\nfor count in (100, 1000):\n    document = dict(model)\n    prototype = model["fact_types"][0]\n    document["fact_types"] = [dict(prototype, id=f"ft_{i}") for i in range(count)]\n    document["constraints"] = []\n    path = dest / "scale.json"\n    path.write_text(json.dumps(document))\n    compile(render_pyrel(path), "scale.py", "exec")\npop = dest / "population.json"\npop.write_text(json.dumps({"facts": {"ft_0": [{"student": i, "nickname": "a"}\n                                         for i in range(10000)]}}))\nassert len(runtime["load_document"](pop)["facts"]["ft_0"]) == 10000\nassert time.monotonic() - start < 10\n')
    started = time.monotonic()
    result = subprocess.run([sys.executable, str(probe), str(BASICS), str(RUNTIME), str(tmp_path)], capture_output=True, text=True, timeout=10, check=False)
    assert result.returncode == 0, result.stderr
    assert time.monotonic() - started < 10

def test_population_role_shape_is_not_silently_dropped(tmp_path: Path) -> None:
    program = export(tmp_path)
    namespace = runpy.run_path(str(program))
    population = tmp_path / 'bad-population.json'
    population.write_text(json.dumps({'facts': {'student_has_nickname': [{'student': 1}]}}))
    assert namespace['program_main']([str(population), '--out', str(tmp_path / 'report.json')]) == 3

def test_require_refuses_before_rai_construction(tmp_path: Path, monkeypatch) -> None:
    program = export(tmp_path, BASICS, '--connection', 'not-configured')
    namespace = runpy.run_path(str(program))
    original_import = builtins.__import__

    def deny_rai(name, *args, **kwargs):
        assert name.split('.')[0] != 'relationalai', 'require reservation reached RAI'
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', deny_rai)
    out = tmp_path / 'require.json'
    assert namespace['program_main']([str(POPULATION), '--out', str(out), '--mode', 'require']) == 0
    verdicts = json.loads(out.read_text())['verdicts']
    assert len(verdicts) == 7
    assert all(v['status'] == 'unsupported' and v['reason'] == 'require-mode-needs-lqp-runtime' for v in verdicts)

@pytest.mark.parametrize('shape,expected', [('inherited', 0), ('ambiguous', 3)])
def test_reference_resolution_shapes(tmp_path: Path, shape: str, expected: int) -> None:
    from ruamel.yaml import YAML
    require_export()
    document = YAML(typ='safe').load(BASICS.read_text())
    subtype = {'id': 'senior', 'name': 'Senior', 'kind': 'entity', 'subtype_of': ['student'], 'inherits_reference': True}
    if shape == 'ambiguous':
        document['object_types'].append({'id': 'other', 'name': 'Other', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'nickname'}})
        subtype['subtype_of'].append('other')
    document['object_types'].append(subtype)
    model = tmp_path / 'model.json'
    model.write_text(json.dumps(document))
    out = tmp_path / 'program.py'
    result = cli(str(model), '--out', str(out), cwd=tmp_path)
    assert result.returncode == expected, result.stderr
    assert out.exists() == (expected == 0)
