import ast
from types import SimpleNamespace

from support.json_input_cases import raw

CHARACTERIZE = SimpleNamespace(raw=raw)
import json
import subprocess
import sys
from pathlib import Path

import pytest

from gnd.artifacts import sha256_hex

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('owner', ['gnd.json_input', 'gnd.exp.session_patch'])
def test_aliased_work_is_bounded(owner):
    code = f"from {owner} import validate_json_value; x=0\nfor _ in range(28): x=[x,x]\nvalidate_json_value(x)\nprint('done')"
    completed = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=2, check=False, cwd=ROOT)
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout == 'done\n'

@pytest.mark.parametrize('variant', ['deeper-reuse', 'cycle'])
def test_memoized_value_walk_keeps_depth_refusal(variant):
    from gnd.json_input import JsonInputRefusal, validate_json_value
    shared = []
    if variant == 'cycle':
        shared.append(shared)
        doc = shared
    else:
        deep = shared
        for _ in range(64):
            deep = [deep]
        doc = [deep, shared]
    with pytest.raises(JsonInputRefusal, match='depth') as refused:
        validate_json_value(doc)
    assert refused.value.reason == 'shape'

@pytest.mark.parametrize('version', [[], {}], ids=['list', 'object'])
@pytest.mark.parametrize('entry', ['direct', 'file'])
def test_review_malformed_version_maps_to_public_error(version, entry, tmp_path):
    from pydantic import ValidationError

    from gnd.exp.session_contract import (
        DataDrivenContract,
        SessionContractError,
        read_session_contract,
    )
    raw = json.dumps({'schema_version': version}).encode()
    if entry == 'direct':
        with pytest.raises(ValidationError) as refused:
            DataDrivenContract.model_validate_json(raw)
        assert refused.value.errors()[0]['loc'] == ('schema_version',)
    else:
        path = tmp_path / 'contract.json'
        path.write_bytes(raw)
        with pytest.raises(SessionContractError) as refused:
            read_session_contract(path, experiment_root=tmp_path, experiment_id='invalid-version')
        assert refused.value.issues[0].path == 'schema_version'

def test_review_giant_fact_index_refuses_with_public_error():
    from gnd.judgments import JudgmentInputError, judgment_fact_digest
    with pytest.raises(JudgmentInputError) as refused:
        judgment_fact_digest('work', 10 ** 5000, {})
    assert refused.value.reason == 'shape'

@pytest.mark.parametrize('digits', [129, 4300])
def test_review_fact_index_keeps_existing_encodable_range(digits):
    from gnd.judgments import judgment_fact_digest
    token = '1' + '0' * (digits - 1)
    expected_raw = ('{"fact_type":"work","index":' + token + ',"roles":{}}\n').encode()
    assert judgment_fact_digest('work', 10 ** (digits - 1), {}) == sha256_hex(expected_raw)

@pytest.mark.parametrize('variant', ['duplicate', 'depth65', 'scalar4097', 'nonfinite', 'digits129', 'bytes-over'])
def test_core_refusal_controls_discriminate_disabled_policy(variant, monkeypatch):
    from gnd import json_input
    maximum = 32 if variant == 'bytes-over' else json_input.MAX_JSON_BYTES
    payload = CHARACTERIZE.raw(variant)
    with pytest.raises(json_input.JsonInputRefusal):
        json_input.bounded_json(payload, max_bytes=maximum)
    monkeypatch.setattr(json_input, '_refuse', lambda *args: None)
    assert json_input.bounded_json(payload, max_bytes=maximum) is not None

def test_neutral_owner_and_fresh_import_direction():
    target = ROOT / 'src/gnd/json_input.py'
    tree = ast.parse(target.read_text())
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    imports |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert imports <= {'__future__', 'json', 'math', 'decimal'}
    code = "import json,sys; import gnd.json_input; print(json.dumps(sorted(n for n in sys.modules if n.startswith('gnd'))))"
    completed = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=10, check=True, cwd=ROOT)
    assert json.loads(completed.stdout) == ['gnd', 'gnd.json_input']
    wrappers = ast.parse((ROOT / 'src/gnd/exp/session_patch.py').read_text())
    for node in wrappers.body:
        if isinstance(node, ast.FunctionDef) and node.name in {'bounded_json', 'validate_json_value'}:
            assert not any(isinstance(child, (ast.For, ast.While, ast.ListComp)) for child in ast.walk(node))
            calls = [child for child in ast.walk(node) if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)]
            assert any(isinstance(call.func.value, ast.Name) and call.func.value.id == 'json_input' and (call.func.attr == node.name) for call in calls)
