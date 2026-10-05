from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

from gnd.model import MAX_MODEL_BYTES
from gnd.rai_import import RaiImportRequest, plan_rai_import

ROOT = Path(__file__).resolve().parents[1]
IMPORT = ROOT / 'tests/fixtures/v61-phase1/import'
HOSTILE = [{'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'hex', 'value': 'ff'}, 'id': 'H-INVALID-UTF8', 'input_bytes': 1, 'input_sha256': 'a8100ae6aa1940d0b663bb31cd466142ebbdbd5187131b92d93818987832eb89'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: [\n'}, 'id': 'H-MALFORMED-YAML', 'input_bytes': 11, 'input_sha256': '5e7e04f69773587ef05800714cc633797c5c9b093962b225f7f0030548935d21'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: 1\na: &a {}\nb: *a\n'}, 'id': 'H-YAML-ALIAS', 'input_bytes': 26, 'input_sha256': 'cd834de7d6efc3a78f18e04d034b3a0d1a9256d41a18fab2471d703627718d6e'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: 1\n---\nversion: 1\n'}, 'id': 'H-MULTI-DOC', 'input_bytes': 26, 'input_sha256': 'ebe69e0e230b9e69797896ef66b6c8b3a84d5fbcb94f249893a77465b8df0071'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': '- version\n- 1\n'}, 'id': 'H-NONMAPPING', 'input_bytes': 14, 'input_sha256': '7aaa111a26468c4f0e35aa0757bd9ad8ee4603227a9a4c37913306d5d7160330'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'kind': 'utf8', 'value': 'version: 1\nvalue: .nan\n'}, 'id': 'H-NONFINITE', 'input_bytes': 23, 'input_sha256': 'caacf8f28a231c5cbbbcc77a1a4081a870a62b786dc6a9ee1a12dcb930d9e16e'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'digits': 10001, 'kind': 'huge-integer'}, 'id': 'H-HUGE-INTEGER', 'input_bytes': 10020, 'input_sha256': 'ba986a465f2859558a8adc51daa63980511c77f1362722620d193b2afd277fa8'}, {'expected_exit': 3, 'expected_rule': 'rai-import:parse', 'generator': {'depth': 200, 'kind': 'deep-list'}, 'id': 'H-DEEP-NESTING', 'input_bytes': 420, 'input_sha256': '6e433d5d5011c908f2c42fe86674eb208f517187f1fe13e0d43a0e0f8c622f90'}, {'expected_exit': 3, 'expected_rule': 'rai-import:unsupported', 'generator': {'bytes': 10485760, 'kind': 'padded-unsupported'}, 'id': 'H-EXACT-CAP', 'input_bytes': 10485760, 'input_sha256': 'e3e4016a930b8a556d6fb4459ce7188aa6e68bed194bd13ac86c5b72524b6b4c'}, {'expected_exit': 74, 'expected_rule': 'rai-import:size', 'generator': {'bytes': 10485761, 'kind': 'padded-unsupported'}, 'id': 'H-OVER-CAP', 'input_bytes': 10485761, 'input_sha256': '708af4fa7362f03b98e2cc295836e5236c4a5ab8069b261557c024d20cd235bd'}]


def _assert_lane_exists(result: subprocess.CompletedProcess[str]) -> None:
    parser_refusal = "invalid choice: 'import'" in result.stderr
    assert not parser_refusal, 'expected corpus-first RED: the approved `gnd import rai-orm` production surface is still absent'

def _hostile_bytes(case: dict[str, object]) -> bytes:
    generator = case['generator']
    kind = generator['kind']
    if kind == 'hex':
        return bytes.fromhex(generator['value'])
    if kind == 'utf8':
        return generator['value'].encode()
    if kind == 'huge-integer':
        return ('version: 1\nvalue: ' + '9' * generator['digits'] + '\n').encode()
    if kind == 'deep-list':
        depth = generator['depth']
        return ('version: 1\nvalue: ' + '[' * depth + '0' + ']' * depth + '\n').encode()
    if kind == 'padded-unsupported':
        prefix = b'version: 1\nunsupported: true\n'
        return prefix + b'#' * (generator['bytes'] - len(prefix))
    raise AssertionError(f'unknown hostile generator: {kind}')

@pytest.mark.parametrize('case', HOSTILE, ids=lambda row: row['id'])
def test_hostile_import_is_total_and_named(case: dict[str, object], tmp_path: Path) -> None:
    source = tmp_path / 'input.orm.yaml'
    source.write_bytes(_hostile_bytes(case))
    output = tmp_path / 'out'
    result = subprocess.run([sys.executable, '-m', 'gnd', 'import', 'rai-orm', str(source), '--out', str(output), '--source-artifact', 'hostile/input.orm.yaml'], cwd=ROOT, capture_output=True, text=True, check=False)
    _assert_lane_exists(result)
    assert result.returncode == case['expected_exit'], result.stderr
    assert case['expected_rule'] in result.stdout + result.stderr
    assert not output.exists()


def test_legal_exact_cap_identity_completes_under_five_seconds(tmp_path: Path) -> None:
    base = (IMPORT / 'identity.source.orm.yaml').read_bytes()
    data = base + b'#' + b'x' * (MAX_MODEL_BYTES - len(base) - 2) + b'\n'
    source = tmp_path / 'near-cap.orm.yaml'
    source.write_bytes(data)
    request = RaiImportRequest(source, tmp_path / 'out', 'near-cap.orm.yaml', None)
    started = time.monotonic()
    result = plan_rai_import(request)
    assert time.monotonic() - started < 5
    assert result.model_bytes == data and result.rewrites == ()
