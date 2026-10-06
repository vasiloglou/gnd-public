"""RF7 actual consumer observations, distinct from historical RF1 answers."""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from gnd import safefs


@pytest.mark.parametrize('name', ['./a', 'a//b', 'a/./b', 'a\\b', ' a', 'a ', 'a/'])
def test_path_spelling_refused(name):
    with pytest.raises(safefs.InstallPathError):
        safefs.reject_unsafe_relpath(name, source='rf7')


def test_path_parents_and_leaf_policy(tmp_path):
    (tmp_path / 'file').write_text('x')
    with pytest.raises(safefs.InstallPathError):
        safefs.safe_destination(tmp_path, 'file/missing/leaf')
    (tmp_path / 'directory').mkdir()
    assert safefs.safe_destination(tmp_path, 'directory/leaf') == tmp_path / 'directory/leaf'
    (tmp_path / 'link').symlink_to(tmp_path / 'file')
    assert safefs.safe_destination(tmp_path, 'link') == tmp_path / 'link'


@pytest.mark.parametrize('flag', [1, 'yes', 'true', [], False, None])
def test_primitive_nonboolean_inheritance(flag):
    from gnd.model_queries import primitive_for
    types = {'value': {'id': 'value', 'kind': 'value', 'primitive': 'String'},
             'entity': {'id': 'entity', 'kind': 'entity', 'inherits_reference': flag, 'subtype_of': ['value']}}
    for variant in ('truthy', 'strict'):
        assert primitive_for('entity', types, variant=variant) is None
    types['entity']['inherits_reference'] = True
    for variant in ('truthy', 'strict'):
        assert primitive_for('entity', types, variant=variant) == 'String'


@pytest.mark.parametrize('which', ['evolve', 'souffle'])
def test_yaml_alias_actual_reader_refuses(which):
    raw = 'x: &a [1]\ny: *a\n'
    if which == 'evolve':
        from gnd.evolve.service import EvolutionError, _parse_model_text
        with pytest.raises(EvolutionError, match='alias'):
            _parse_model_text(raw)
    else:
        from gnd.export.souffle import parse
        with pytest.raises(ValueError, match='alias'):
            parse(raw.encode(), 'yaml')


@pytest.mark.parametrize('which', ['population', 'adapter', 'store'])
def test_json_actual_reader_overflow_refuses(which):
    raw = b'{"x":1e999}'
    if which == 'population':
        from gnd.population import PopulationLoadError, _parse_document_bytes
        with pytest.raises(PopulationLoadError):
            _parse_document_bytes(raw, suffix='.json', source='rf7')
    elif which == 'adapter':
        from gnd.exp.adapter_policy import _strict_document
        with pytest.raises(ValueError):
            _strict_document(raw)
    else:
        from gnd.exp.session_store import _strict_object_bytes
        with pytest.raises(ValueError):
            _strict_object_bytes(raw, label='rf7')


@pytest.mark.parametrize('site', ['gnd.synth.provenance:_sha256_file', 'gnd.measure.promote:_digest', 'gnd.transition:population_file_digest'])
def test_fifo_refused_with_deadline(site, tmp_path):
    path = tmp_path / 'fifo'
    os.mkfifo(path)
    module, name = site.split(':')
    code = f'''from pathlib import Path
from {module} import {name} as digest
try:
    digest(Path({str(path)!r}))
except (OSError, ValueError):
    pass
else:
    raise AssertionError('FIFO accepted')
'''
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, '-c', code], env={**os.environ, 'PYTHONPATH': str(root / 'src')}, capture_output=True, text=True, timeout=2, check=False)
    assert result.returncode == 0, result.stdout + result.stderr


def test_regular_file_digest_adapters(tmp_path):
    import hashlib
    raw = b'RF7\n'
    path = tmp_path / 'value'
    path.write_bytes(raw)
    expected = hashlib.sha256(raw).hexdigest()
    for module, name, prefix in [('gnd.synth.provenance', '_sha256_file', ''), ('gnd.measure.promote', '_digest', ''), ('gnd.transition', 'population_file_digest', 'sha256:')]:
        assert getattr(importlib.import_module(module), name)(path) == prefix + expected


def test_population_datetime_strict_and_synth_agree():
    from gnd.popvalidate import _is_datetime
    from gnd.synth.values import _parse_datetime
    for value in ('2024-02-29 00:00:00', '20240229T000000', '2024-02-29T00:00:00+0130'):
        assert not _is_datetime(value)
        with pytest.raises(ValueError):
            _parse_datetime(value, 'rf7', {})


def test_unknown_version_includes_eight():
    from gnd.exp.session_contract import DataDrivenContract
    with pytest.raises(ValueError) as error:
        DataDrivenContract.model_validate({'schema_version': 9})
    assert 'or 8' in str(error.value)


def test_model_json_refusal_cannot_fall_back_to_yaml():
    from gnd.errors import ModelLoadError
    from gnd.model import load_model_bytes
    with pytest.raises(ModelLoadError, match='JSON'):
        load_model_bytes(b'{"x":1e999}', source='rf7.json')


def test_digest_change_refusal_closes_descriptor(tmp_path, monkeypatch):
    path = tmp_path / 'changing'
    path.write_bytes(b'first')
    read = os.read
    close = os.close
    closed = []
    changed = False

    def mutate(fd, limit):
        nonlocal changed
        chunk = read(fd, limit)
        if not changed:
            changed = True
            with path.open('ab') as handle:
                handle.write(b'second')
        return chunk

    def observe_close(fd):
        closed.append(fd)
        close(fd)

    monkeypatch.setattr(os, 'read', mutate)
    monkeypatch.setattr(os, 'close', observe_close)
    with pytest.raises(ValueError, match='changed while reading'):
        safefs.file_sha256(path)
    assert len(closed) == 1
    with pytest.raises(OSError):
        os.fstat(closed[0])
