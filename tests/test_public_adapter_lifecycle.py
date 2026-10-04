from __future__ import annotations

import atexit
import hashlib
import importlib.util
import tempfile
from pathlib import Path

import pytest

PUBLIC = Path(__file__).parent / 'fixtures'
CONTRACT = {'driver': 'tests/fixtures/v61-phase6/installed/driver.py', 'required_observations': ['contract-v6', 'launch-v2', 'attempt-v8', 'feedback-v4', 'result-v2', 'command-argv-accepted', 'command-stdin-accepted', 'http-accepted', 'http-redirect-refused', 'http-cap-refused', 'http-request-count', 'credential-absent', 'policy-refusal', 'legacy-replay', 'evidence-not-current']}
ANSWERS = {'http_request_count': 3}
BINDINGS = {'skeleton/model.orm.yaml': {'target': 'tests/fixtures/skeleton/model.orm.yaml', 'bytes': 3067, 'sha256': '5865807314537b1241f86adfaf04b6129cccb8d0cc880a362450a2fc83df06b3', 'limit': 8192}, 'skeleton/population.good.yaml': {'target': 'tests/fixtures/skeleton/population.good.yaml', 'bytes': 576, 'sha256': 'c54c41028dacf4e4af42fb35cc588fee08ad60575d367edb0a43996302654fe2', 'limit': 8192}, 'skeleton/population.bad.yaml': {'target': 'tests/fixtures/skeleton/population.bad.yaml', 'bytes': 670, 'sha256': '074ef152c5170b7d6d8db7bc3fb734ef2a9b03d842f1666ba25ca1b5f5edbe9c', 'limit': 8192}, 'public-walk-floor/session/model.orm.yaml': {'target': 'tests/fixtures/v61-phase5/session/model.orm.yaml', 'bytes': 2174, 'sha256': '0f63a6d97778d55322a303977494e3f999d86ac69cb1d85dd9f93a63f7e29f5c', 'limit': 8192}, 'public-walk-floor/session/input/pre.pop.yaml': {'target': 'tests/fixtures/v61-phase5/session/input/pre.pop.yaml', 'bytes': 224, 'sha256': '721b02fc5a6e047d1da2c0a9f4b116398a217213b9b90ccc4c1d0dd2c14974dc', 'limit': 8192}, 'public-walk-floor/session/contract-v5.json': {'target': 'tests/fixtures/v61-phase5/session/contract-v5.json', 'bytes': 2053, 'sha256': '4daa5d64d486e7640643912a5de9c498afd1c4f47816c6a2ebb05273ea6e02a1', 'limit': 8192}, 'public-walk-floor/session/candidate/steps.json': {'target': 'tests/fixtures/v61-phase5/session/candidate/steps.json', 'bytes': 460, 'sha256': '16bcf394a717693a6b5ec5a455754266dd63d2bbfee7996fb756573b2a4b576f', 'limit': 8192}, 'public-local-adapter-policy/contracts/command.json': {'target': 'tests/fixtures/v61-phase6/contracts/command.json', 'bytes': 837, 'sha256': 'dcc59432be6c3c2fe4817120440f2c0663b45c3025c882442e02c10836558db3', 'limit': 8192}, 'public-walk-floor/runner.py': {'target': 'tests/fixtures/v61-phase5/installed/driver.py', 'bytes': 6013, 'sha256': 'a60f1bb36c284644bd86c1a69e8d1a8ca5f72a5b79cf4cf7d12c9fc31b6ebf8e', 'limit': 32768}, 'public-walk-floor/adapter-runner.py': {'target': 'tests/fixtures/v61-phase6/installed/driver.py', 'bytes': 12693, 'sha256': 'f4350a64f3154b23550b254de7ac17bac156a906b9c574818dd8c815f85d4d3e', 'limit': 32768}}

def _materialize():
    temporary = tempfile.TemporaryDirectory(prefix='gnd-public-adapter-lifecycle-')
    root = Path(temporary.name)
    total = 0
    for relative, expected in BINDINGS.items():
        source = PUBLIC / relative
        assert source.is_file() and not source.is_symlink()
        with source.open('rb') as stream:
            data = stream.read(expected['limit'] + 1)
        assert len(data) == expected['bytes'] <= expected['limit']
        assert hashlib.sha256(data).hexdigest() == expected['sha256']
        total += len(data)
        assert total <= 65536
        path = root / expected['target']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o644)
    return temporary, root

_TEMPORARY, ROOT = _materialize()
atexit.register(_TEMPORARY.cleanup)


def _load_driver():
    driver_path = ROOT / CONTRACT['driver']
    spec = importlib.util.spec_from_file_location('v61_phase6_installed_driver', driver_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_installed_driver_observes_all_routes_and_predecessor_replay() -> None:
    observations = _load_driver().observe(ROOT)
    assert set(observations) == set(CONTRACT['required_observations'])
    assert observations['contract-v6'] == 6
    assert observations['launch-v2'] == 2
    assert observations['attempt-v8'] == 8
    assert observations['feedback-v4'] == 4
    assert observations['result-v2'] == 2
    for name in ('command-argv-accepted', 'command-stdin-accepted', 'http-accepted', 'credential-absent', 'policy-refusal', 'legacy-replay'):
        assert observations[name] is True
    assert observations['http-request-count'] == ANSWERS['http_request_count']
    assert observations['http-redirect-refused'] is True
    assert observations['http-cap-refused'] is True

def test_installed_answer_negative_control_rejects_changed_request_count() -> None:
    observations = _load_driver().observe(ROOT)
    dirty = dict(observations)
    dirty['http-request-count'] = 2
    with pytest.raises(AssertionError):
        assert dirty['http-request-count'] == ANSWERS['http_request_count']
