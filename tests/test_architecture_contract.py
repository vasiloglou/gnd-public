from __future__ import annotations

import json
import os
import random
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / 'tests' / 'fixtures' / 'architecture'
CASES_DIR = CORPUS / 'cases'
ANSWER_KEY = json.loads((CORPUS / 'expected.json').read_text(encoding='utf-8'))
CASES: list[dict[str, Any]] = ANSWER_KEY['cases']
CASES_BY_ID = {str(case['id']): case for case in CASES}
MATRIX_FLOOR = 36
REQUIRED_BRANCHES = frozenset({'load:explicit-empty', 'load:full', 'shape:contract-version', 'document:malformed-yaml', 'document:multiple-documents', 'document:alias', 'shape:nonmapping-root', 'shape:extra-root-key', 'shape:extra-nested-key', 'shape:module-type', 'shape:symbol-type', 'shape:artifact-type', 'shape:entry-point-type', 'shape:exit-type', 'shape:smoke-type', 'path:posix-absolute', 'path:drive-root', 'path:unc-root', 'path:parent', 'path:backslash', 'path:doubled-separator', 'path:dot-component', 'path:nul', 'path-field:module', 'path-field:artifact', 'path-field:required-by', 'semantic:entry-point-duplicate', 'semantic:smoke-id-duplicate', 'semantic:smoke-entry-point-unknown', 'semantic:smoke-exit-undeclared', 'shape:exit-below-band', 'shape:exit-above-band', 'shape:exit-boolean', 'substitution:tmp', 'substitution:other-name', 'substitution:conversion', 'substitution:format-specifier', 'substitution:escaped-brace', 'substitution:unmatched-brace'})

def _case_path(case: dict[str, Any]) -> Path:
    return CORPUS / str(case['path'])

def _observed(parser: Callable[..., Any], error_type: type[BaseException], case: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    try:
        parser(_case_path(case).read_bytes(), source=str(case['path']))
    except error_type as error:
        issues = getattr(error, 'issues', ())
        return ('refuse', tuple(str(issue.rule_id) for issue in issues))
    return ('load', ())

def _assert_case(parser: Callable[..., Any], error_type: type[BaseException], case: dict[str, Any]) -> None:
    outcome, rule_ids = _observed(parser, error_type, case)
    assert outcome == case['outcome']
    if case['rule_id'] is not None:
        assert rule_ids, f"{case['id']} refused without a structured issue"
        assert rule_ids[0] == case['rule_id']

@pytest.mark.parametrize('case', CASES, ids=[str(case['id']) for case in CASES])
def test_every_committed_case(case: dict[str, Any]) -> None:
    assert len(CASES) >= MATRIX_FLOOR
    assert ANSWER_KEY['matrix_floor'] == MATRIX_FLOOR
    from gnd.architecture import ArchitectureContractError, parse_architecture_contract_bytes
    _assert_case(parse_architecture_contract_bytes, ArchitectureContractError, case)

def _actual_branches(cases: list[dict[str, Any]]) -> frozenset[str]:
    return frozenset(str(branch) for case in cases for branch in case['branches'])

def test_answer_key_and_glob_name_exactly_the_same_cases() -> None:
    ids = [str(case['id']) for case in CASES]
    assert len(ids) == len(set(ids)) == MATRIX_FLOOR
    keyed = {_case_path(case).resolve() for case in CASES}
    globbed = {path.resolve() for path in CASES_DIR.glob('*.contract.yaml')}
    assert keyed == globbed

def test_branch_table_is_complete_against_an_independent_literal() -> None:
    assert _actual_branches(CASES) == REQUIRED_BRANCHES

def test_branch_completeness_oracle_has_a_negative_control() -> None:
    edited = json.loads(json.dumps(CASES))
    edited[0]['branches'] = []
    assert REQUIRED_BRANCHES - _actual_branches(edited) == {'load:explicit-empty'}
_TOKEN = re.compile('\\{[^{}\\s]+\\}|[A-Za-z_][A-Za-z0-9_.-]*|-?[0-9]+|[][{},:]')

def _tokens(path: Path) -> list[str]:
    return _TOKEN.findall(path.read_text(encoding='utf-8'))

def _token_delta(left: Path, right: Path) -> int:
    return sum((a != b for a, b in zip_longest(_tokens(left), _tokens(right))))

def test_every_accepting_case_has_one_named_one_token_refusal() -> None:
    accepting = [case for case in CASES if case['outcome'] == 'load']
    assert {str(case['id']) for case in accepting} == {'C-01', 'C-02', 'S-08'}
    for case in accepting:
        sibling_id = str(case['mutation'])
        sibling = CASES_BY_ID[sibling_id]
        assert sibling['outcome'] == 'refuse'
        assert sibling['mutation_of'] == case['id']
        assert _token_delta(_case_path(case), _case_path(sibling)) == 1
    mutation_targets = [str(case['mutation']) for case in accepting]
    assert len(mutation_targets) == len(set(mutation_targets))

@dataclass(frozen=True)
class _FakeIssue:
    rule_id: str

class _FakeError(ValueError):

    def __init__(self, *rule_ids: str) -> None:
        self.issues = tuple(_FakeIssue(rule_id) for rule_id in rule_ids)

def test_harness_negative_control_is_live() -> None:
    dirty_parser = lambda data, *, source: object()
    with pytest.raises(AssertionError):
        _assert_case(dirty_parser, _FakeError, CASES_BY_ID['P-01'])

def _padded_empty_contract(size: int) -> bytes:
    base = _case_path(CASES_BY_ID['C-01']).read_bytes()
    remaining = size - len(base)
    assert remaining >= 2
    return base + b'#' + b'x' * (remaining - 2) + b'\n'

def test_malformed_utf8_uses_the_declared_error_surface() -> None:
    from gnd.architecture import ArchitectureContractError, parse_architecture_contract_bytes
    with pytest.raises(ArchitectureContractError) as caught:
        parse_architecture_contract_bytes(b'\xff', source='generated-invalid-utf8')
    assert caught.value.issues[0].rule_id == 'architecture:decode'

def test_exact_cap_reaches_parse_and_cap_plus_one_refuses_before_parse() -> None:
    from gnd.architecture import (
        MAX_ARCHITECTURE_CONTRACT_BYTES,
        ArchitectureContractError,
        parse_architecture_contract_bytes,
    )
    exact = _padded_empty_contract(MAX_ARCHITECTURE_CONTRACT_BYTES)
    assert len(exact) == MAX_ARCHITECTURE_CONTRACT_BYTES
    parse_architecture_contract_bytes(exact, source='generated-exact-cap')
    with pytest.raises(ArchitectureContractError) as caught:
        parse_architecture_contract_bytes(exact + b'x', source='generated-over-cap')
    assert caught.value.issues[0].rule_id == 'architecture:document-too-large'

@pytest.mark.parametrize(('case_id', 'data', 'rule_id'), [('deep-nesting', b'[' * 20000 + b']' * 20000, 'architecture:yaml'), ('huge-integer', b'contract_version: ' + b'9' * 100000 + b'\nmodules: []\nartifacts: []\nentry_points: []\nsmoke: []\n', 'architecture:yaml'), ('alias-amplification', b'contract_version: 1\nmodules: &m []\nartifacts: []\nentry_points: []\nsmoke: *m\n', 'architecture:yaml-alias')], ids=['deep-nesting', 'huge-integer', 'alias-amplification'])
def test_hostile_yaml_is_total(case_id: str, data: bytes, rule_id: str) -> None:
    from gnd.architecture import ArchitectureContractError, parse_architecture_contract_bytes
    with pytest.raises(ArchitectureContractError) as caught:
        parse_architecture_contract_bytes(data, source=f'generated-{case_id}')
    assert caught.value.issues[0].rule_id == rule_id

def test_deterministic_arbitrary_byte_sweep_is_total() -> None:
    from gnd.architecture import ArchitectureContractError, parse_architecture_contract_bytes
    generator = random.Random(230828)
    for length in (0, 1, 2, 3, 7, 16, 31, 64, 255, 1024, 4096):
        for iteration in range(8):
            data = generator.randbytes(length)
            try:
                parse_architecture_contract_bytes(data, source=f'generated-random-{length}-{iteration}')
            except ArchitectureContractError:
                pass

def test_contract_read_is_bounded_regular_and_no_follow(tmp_path: Path) -> None:
    from gnd.architecture import (
        ARCHITECTURE_CONTRACT_FILENAME,
        ArchitectureContractError,
        load_architecture_contract,
    )
    target = tmp_path / 'target.yaml'
    target.write_bytes(_case_path(CASES_BY_ID['C-01']).read_bytes())
    (tmp_path / ARCHITECTURE_CONTRACT_FILENAME).symlink_to(target)
    with pytest.raises(ArchitectureContractError) as caught:
        load_architecture_contract(tmp_path)
    assert caught.value.issues[0].rule_id == 'architecture:read'
    (tmp_path / ARCHITECTURE_CONTRACT_FILENAME).unlink()
    (tmp_path / ARCHITECTURE_CONTRACT_FILENAME).mkdir()
    root_fd = os.open(tmp_path, os.O_RDONLY)
    try:
        with pytest.raises(ArchitectureContractError) as caught_at:
            load_architecture_contract(tmp_path, root_fd=root_fd)
    finally:
        os.close(root_fd)
    assert caught_at.value.issues[0].rule_id == 'architecture:read'

def test_missing_contract_has_its_distinct_error(tmp_path: Path) -> None:
    from gnd.architecture import ArchitectureContractNotFoundError, load_architecture_contract
    with pytest.raises(ArchitectureContractNotFoundError):
        load_architecture_contract(tmp_path)

@pytest.mark.slow
def test_legal_near_cap_flat_contract_loads_under_five_seconds() -> None:
    from gnd.architecture import MAX_ARCHITECTURE_CONTRACT_BYTES, parse_architecture_contract_bytes
    data = _padded_empty_contract(MAX_ARCHITECTURE_CONTRACT_BYTES - 1)
    started = time.perf_counter()
    parse_architecture_contract_bytes(data, source='generated-near-cap')
    assert time.perf_counter() - started < 5.0

def test_validation_order_is_the_rule_roster_order() -> None:
    from gnd.architecture import ArchitectureContractError, parse_architecture_contract_bytes
    data = b"contract_version: 1\nmodules:\n  - path: /absolute.py\n    symbols: []\nartifacts: []\nentry_points:\n  - module: duplicate.ep\n    subcommands: []\n    flags: []\n    consumes: []\n    produces: []\n    exits: []\n  - module: duplicate.ep\n    subcommands: []\n    flags: []\n    consumes: []\n    produces: []\n    exits: []\n  - module: valid.ep\n    subcommands: []\n    flags: []\n    consumes: []\n    produces: []\n    exits:\n      - code: 0\n        meaning: success\nsmoke:\n  - id: duplicate-smoke\n    entry_point: missing.ep\n    argv: []\n    expect_exit: 0\n  - id: duplicate-smoke\n    entry_point: valid.ep\n    argv: []\n    expect_exit: 1\n  - id: bad-substitution\n    entry_point: valid.ep\n    argv: ['{cwd}/out.json']\n    expect_exit: 0\n"
    with pytest.raises(ArchitectureContractError) as caught:
        parse_architecture_contract_bytes(data, source='generated-order')
    first_seen = tuple(dict.fromkeys(issue.rule_id for issue in caught.value.issues))
    assert first_seen == ('architecture:path-invalid', 'architecture:entry-point-duplicate', 'architecture:smoke-id-duplicate', 'architecture:smoke-entry-point-unknown', 'architecture:smoke-exit-undeclared', 'architecture:smoke-substitution')
