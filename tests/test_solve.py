from __future__ import annotations

import ast
import copy
import hashlib
import io
import json
import os
import re
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO

import pytest
from support.rf5_sources import cli_source_paths

from gnd import cli, exits, solve

REPO_ROOT = Path(__file__).resolve().parent.parent
SOLVE_SOURCE = REPO_ROOT / 'src' / 'gnd' / 'solve.py'
CLI_SOURCE = REPO_ROOT / 'src' / 'gnd' / 'cli.py'
FIXED_NOW = datetime(2026, 8, 24, 12, 34, 56, 987654, tzinfo=UTC)
GND_PREFIX = (sys.executable, '-m', 'gnd')
LOCKED_STATIONS = ('validate', 'synth', 'codegen', 'exp-run', 'conformance')
FORBIDDEN_AGGREGATE_KEYS = frozenset({'passed', 'ok', 'verdict', 'result', 'status'})
FLAG_KEYS = ('from', 'until', 'skip', 'auto', 'adapter', 'adapter_explicit', 'experiment', 'test_argv', 'station_timeout')
RECORD_KEYS = {'walk': ('record', 'walk_id', 'schema_version', 'model', 'selected', 'flags', 'started'), 'gate': ('record', 'walk_id', 'station', 'argv', 'authorized_by'), 'station': ('record', 'walk_id', 'station', 'exit', 'evidence', 'halt')}
AUTHORIZED_BY_RE = re.compile('^(?P<source>stdin|auto) (?P<reply>"(?:[^"\\\\\\x00-\\x1f]|\\\\(?:["\\\\/bfnrt]|u[0-9A-Fa-f]{4}))*") (?P<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z)$')
B5_MAX_BYTES = 8 * 1024 * 1024
B5_MAX_LINES = 10000
B5_MAX_DEPTH = 64
ALL_B5_FAILURES = frozenset(range(1, 9))

def _json_depth_at_most(text: str, maximum: int=B5_MAX_DEPTH) -> bool:
    depth = 0
    in_string = False
    escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == '\\':
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character in '[{':
            depth += 1
            if depth > maximum:
                return False
        elif character in ']}':
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and (not in_string) and (not escaped)

def _bounded_jsonl_objects(raw: bytes) -> list[dict[str, Any]] | None:
    try:
        if not isinstance(raw, bytes) or not raw or len(raw) > B5_MAX_BYTES:
            return None
        if b'\x00' in raw or not raw.endswith(b'\n'):
            return None
        lines = raw.split(b'\n')
        if lines[-1] != b'':
            return None
        lines.pop()
        if not lines or len(lines) > B5_MAX_LINES or any(not line for line in lines):
            return None
        records: list[dict[str, Any]] = []
        for line in lines:
            text = line.decode('utf-8', errors='strict')
            if not _json_depth_at_most(text):
                return None
            value = json.loads(text)
            if not isinstance(value, dict):
                return None
            records.append(value)
        return records
    except Exception:  # noqa: BLE001 -- preserve predecessor refusal contract
        return None

def _authorization_matches(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    match = AUTHORIZED_BY_RE.fullmatch(value)
    if match is None:
        return False
    try:
        reply = json.loads(match.group('reply'))
        datetime.strptime(match.group('timestamp'), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
    except (TypeError, ValueError):
        return False
    if not isinstance(reply, str):
        return False
    return match.group('source') != 'auto' or reply == 'auto'

def _expected_selected(flags: object) -> tuple[str, ...] | None:
    if not isinstance(flags, dict):
        return None
    start = flags.get('from')
    until = flags.get('until')
    skip = flags.get('skip')
    if start is not None and start not in LOCKED_STATIONS:
        return None
    if until is not None and until not in LOCKED_STATIONS:
        return None
    if not isinstance(skip, list) or any(name not in LOCKED_STATIONS for name in skip):
        return None
    lo = LOCKED_STATIONS.index(start) if start is not None else 0
    hi = LOCKED_STATIONS.index(until) if until is not None else len(LOCKED_STATIONS) - 1
    return tuple((name for position, name in enumerate(LOCKED_STATIONS) if lo <= position <= hi and name not in skip))

def _flags_satisfy_conjunct_6(header: Mapping[str, object]) -> bool:
    flags = header.get('flags')
    selected = header.get('selected')
    if not isinstance(flags, dict) or tuple(flags) != FLAG_KEYS:
        return False
    if not isinstance(selected, list) or not selected:
        return False
    if any(not isinstance(name, str) for name in selected):
        return False
    start = flags['from']
    until = flags['until']
    skip = flags['skip']
    auto = flags['auto']
    adapter = flags['adapter']
    adapter_explicit = flags['adapter_explicit']
    experiment = flags['experiment']
    test_argv = flags['test_argv']
    station_timeout = flags['station_timeout']
    if start is not None and start not in LOCKED_STATIONS:
        return False
    if until is not None and until not in LOCKED_STATIONS:
        return False
    if not isinstance(skip, list) or len(set(skip)) != len(skip):
        return False
    if any(name not in LOCKED_STATIONS for name in skip):
        return False
    if skip != sorted(skip, key=LOCKED_STATIONS.index):
        return False
    if type(auto) is not bool or type(adapter_explicit) is not bool:
        return False
    if experiment is not None and (not isinstance(experiment, str)):
        return False
    if not isinstance(test_argv, list) or any(not isinstance(word, str) for word in test_argv):
        return False
    if not isinstance(station_timeout, dict):
        return False
    if any(name not in LOCKED_STATIONS for name in station_timeout):
        return False
    if list(station_timeout) != sorted(station_timeout, key=LOCKED_STATIONS.index):
        return False
    if any(type(seconds) is not int or not 1 <= seconds <= 86400 for seconds in station_timeout.values()):
        return False
    lo = LOCKED_STATIONS.index(start) if start is not None else 0
    hi = LOCKED_STATIONS.index(until) if until is not None else len(LOCKED_STATIONS) - 1
    if lo > hi:
        return False
    if start in skip or until in skip:
        return False
    if any(not lo <= LOCKED_STATIONS.index(name) <= hi for name in skip):
        return False
    computed = _expected_selected(flags)
    if computed is None or list(computed) != selected:
        return False
    if any(name not in selected for name in station_timeout):
        return False
    exp_selected = 'exp-run' in selected
    if (experiment is not None or test_argv or adapter_explicit) and (not exp_selected):
        return False
    if (adapter is not None) != exp_selected:
        return False
    policy_token = isinstance(adapter, str) and re.fullmatch('<adapter-policy:sha256=[0-9a-f]{64}>', adapter)
    if adapter is not None and adapter not in {'claude', 'codex'} and (not policy_token):
        return False
    return not (exp_selected and (not adapter_explicit) and (adapter != 'claude'))

def b5_failures(raw: bytes) -> frozenset[int]:
    try:
        records = _bounded_jsonl_objects(raw)
        if records is None:
            return frozenset({1}) if raw == b'' else ALL_B5_FAILURES
        failures: set[int] = set()
        walk_records = [record for record in records if record.get('record') == 'walk']
        header = records[0]
        selected = header.get('selected') if isinstance(header, dict) else None
        flags = header.get('flags') if isinstance(header, dict) else None
        walk_id = header.get('walk_id') if isinstance(header, dict) else None
        expected = _expected_selected(flags)
        if len(walk_records) != 1 or header.get('record') != 'walk' or (not isinstance(selected, list)) or (expected is None) or (list(expected) != selected) or (not isinstance(walk_id, str)) or any(record.get('walk_id') != walk_id for record in records):
            failures.add(1)
        selected_names = selected if isinstance(selected, list) else []
        gate_names = [record.get('station') for record in records if record.get('record') == 'gate']
        station_names = [record.get('station') for record in records if record.get('record') == 'station']
        station_bearing = [record.get('station') for record in records if 'station' in record]
        if gate_names != selected_names or station_names != selected_names or any(name not in selected_names for name in station_bearing):
            failures.add(2)
        gate_records = [record for record in records if record.get('record') == 'gate']
        if any(not _authorization_matches(record.get('authorized_by')) for record in gate_records):
            failures.add(3)
        station_records = [record for record in records if record.get('record') == 'station']
        if any(type(record.get('exit')) is not int or record.get('halt') is not None for record in station_records):
            failures.add(4)
        accepted = {station.name: station.accepted_exits for station in solve.STATIONS}
        for record in station_records:
            exit_code = record.get('exit')
            station_name = record.get('station')
            if type(exit_code) is int and (station_name not in accepted or exit_code not in accepted[station_name]):
                failures.add(5)
                break
        if not _flags_satisfy_conjunct_6(header):
            failures.add(6)
        grammar_ok = header.get('record') == 'walk'
        pending_gate: Mapping[str, object] | None = None
        halted = False
        for record in records[1:]:
            if halted or record.get('record') == 'walk':
                grammar_ok = False
                break
            if record.get('record') == 'gate':
                if pending_gate is not None:
                    grammar_ok = False
                    break
                pending_gate = record
            elif record.get('record') == 'station':
                if pending_gate is None or pending_gate.get('station') != record.get('station'):
                    grammar_ok = False
                    break
                pending_gate = None
                halted = record.get('halt') is not None
            else:
                grammar_ok = False
                break
        if pending_gate is not None:
            grammar_ok = False
        if not grammar_ok:
            failures.add(7)
        auto = flags.get('auto') if isinstance(flags, dict) else None
        if type(auto) is not bool:
            failures.add(8)
        else:
            for record in gate_records:
                value = record.get('authorized_by')
                has_auto_source = isinstance(value, str) and value.startswith('auto ')
                if has_auto_source != auto:
                    failures.add(8)
                    break
        return frozenset(failures)
    except Exception:  # noqa: BLE001 -- preserve predecessor refusal contract
        return ALL_B5_FAILURES

def _object_has_forbidden_key(value: object) -> bool:
    if isinstance(value, dict):
        return any((key in FORBIDDEN_AGGREGATE_KEYS or _object_has_forbidden_key(child) for key, child in value.items()))
    if isinstance(value, list):
        return any(_object_has_forbidden_key(child) for child in value)
    return False

def _log_has_no_aggregate_keys(raw: bytes) -> bool:
    records = _bounded_jsonl_objects(raw)
    return records is not None and (not any(_object_has_forbidden_key(record) for record in records))

class _BinaryStdin:

    def __init__(self, payload: bytes) -> None:
        self.buffer = io.BytesIO(payload)

class FakeSpawn:

    def __init__(self, *, outcomes: Mapping[str, solve.StationOutcome] | None=None, exp_indices: tuple[int, ...]=(1,)) -> None:
        self.outcomes = dict(outcomes or {})
        self.exp_indices = exp_indices
        self.calls: list[solve.StationSpawn] = []

    def __call__(self, request: solve.StationSpawn) -> solve.StationOutcome:
        self.calls.append(request)
        name = _station_name_from_capture(request.stdout_path)
        request.stdout_path.parent.mkdir(parents=True, exist_ok=True)
        if name == 'exp-run' and len(self.exp_indices) == 1:
            request.stdout_path.write_text(json.dumps({'run_id': f'run-{self.exp_indices[0]:04d}'}) + '\n', encoding='utf-8')
        else:
            request.stdout_path.write_bytes(f'stdout:{name}\n'.encode())
        request.stderr_path.write_bytes(f'stderr:{name}\n'.encode())
        if name == 'exp-run':
            experiment_arg = request.argv[len(GND_PREFIX) + 2]
            experiment = request.cwd / experiment_arg
            for index in self.exp_indices:
                run_root = experiment / 'runs' / f'run-{index:04d}'
                run_root.mkdir(parents=True, exist_ok=True)
                (run_root / 'result.json').write_text('{}\n', encoding='utf-8')
        return self.outcomes.get(name, solve.StationOutcome(0, None))

def _station_name_from_capture(path: Path) -> str:
    match = re.search('\\.([^.]+)\\.out$', path.name)
    assert match is not None, path
    return match.group(1)

def _fixed_clock() -> datetime:
    return FIXED_NOW

def _allow(_station: solve.Station) -> str:
    return 'go'

def _fail_gate(_station: solve.Station) -> str:
    raise AssertionError('the gate must not be called')

def _fail_spawn(_request: solve.StationSpawn) -> solve.StationOutcome:
    raise AssertionError('nothing may be spawned')

def _seed_workspace(root: Path, *, experiment: bool=False) -> tuple[Path, Path, Path | None]:
    workspace = root / 'workspace'
    workspace.mkdir(parents=True)
    model = workspace / 'model.orm.yaml'
    model.write_text('object_types: []\n', encoding='utf-8')
    experiment_path: Path | None = None
    if experiment:
        experiment_path = workspace / 'EXP-TEST'
        experiment_path.mkdir()
    return (workspace, model, experiment_path)

def _run(model: Path, workspace: Path, *, experiment: Path | None=None, start: str | None=None, until: str | None=None, skip: frozenset[str]=frozenset(), auto: bool=False, adapter: str | None=None, adapter_policy: Path | None=None, test_argv: tuple[str, ...]=(), station_timeout: Mapping[str, int]={}, gate: Callable[[solve.Station], str | None]=_allow, clock: Callable[[], datetime]=_fixed_clock, spawn: Callable[[solve.StationSpawn], solve.StationOutcome] | None=None) -> int:
    return solve.run_walk(model, workspace=workspace, experiment=experiment, start=start, until=until, skip=skip, auto=auto, adapter=adapter, adapter_policy=adapter_policy, test_argv=test_argv, station_timeout=station_timeout, gate=gate, clock=clock, spawn=spawn or FakeSpawn())

def _walk_files(workspace: Path) -> list[Path]:
    return sorted((workspace / 'walks').glob('walk-*.jsonl')) if (workspace / 'walks').is_dir() else []

def _walk_file(workspace: Path) -> Path:
    files = _walk_files(workspace)
    assert len(files) == 1, files
    path = files[0]
    records = _bounded_jsonl_objects(path.read_bytes())
    if records is not None:
        assert not any(_object_has_forbidden_key(record) for record in records)
    return path

def _read_records(workspace: Path) -> list[dict[str, Any]]:
    raw = _walk_file(workspace).read_bytes()
    records = _bounded_jsonl_objects(raw)
    assert records is not None
    return records

def _encode_records(records: list[dict[str, Any]]) -> bytes:
    return b''.join(json.dumps(record, ensure_ascii=False, separators=(',', ':'), allow_nan=False, sort_keys=False).encode('utf-8') + b'\n' for record in records)

def _patch_station(monkeypatch: pytest.MonkeyPatch, name: str, *, argv: Callable[[solve.WalkPaths], tuple[str, ...]] | None=None, accepted_exits: frozenset[int] | None=None, evidence: Callable[[solve.WalkPaths], str] | None | object=...) -> None:
    changed: list[solve.Station] = []
    for station in solve.STATIONS:
        if station.name != name:
            changed.append(station)
            continue
        changed.append(replace(station, argv=station.argv if argv is None else argv, accepted_exits=station.accepted_exits if accepted_exits is None else accepted_exits, evidence=station.evidence if evidence is ... else evidence))
    monkeypatch.setattr(solve, 'STATIONS', tuple(changed))

def _station_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if record.get('record') == 'station']

def _gate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if record.get('record') == 'gate']

def test_t01_station_order_is_the_locked_literal() -> None:
    assert [station.name for station in solve.STATIONS] == ['validate', 'synth', 'codegen', 'exp-run', 'conformance']

def test_t01_shipped_station_table_matches_the_complete_literal_oracle() -> None:
    paths = solve.WalkPaths(model=Path('/fixture/workspace/model.orm.yaml'), workspace=Path('/fixture/workspace'), experiment=Path('/fixture/workspace/EXP-TEST'), walk_id='walk-0042', adapter='codex', test_argv=('-q', 'tests/test_contract.py'), run_index=7)
    actual = tuple((station.name, station.argv(paths), station.accepted_exits, station.timeout, None if station.evidence is None else station.evidence(paths)) for station in solve.STATIONS)
    expected = (('validate', (*GND_PREFIX, 'validate', 'model.orm.yaml'), frozenset({0}), 300, 'walks/walk-0042.validate.out'), ('synth', (*GND_PREFIX, 'synth', 'model.orm.yaml', '--out', 'corpus', '--class', 'all'), frozenset({0}), 300, 'corpus/'), ('codegen', (*GND_PREFIX, 'codegen', 'model.orm.yaml', '--out', 'project'), frozenset({0}), 300, 'project/.gnd-codegen.json'), ('exp-run', (*GND_PREFIX, 'exp', 'run', 'EXP-TEST', '--adapter', 'codex', '--test-argv', '-q', '--test-argv', 'tests/test_contract.py'), frozenset({0}), 3600, 'EXP-TEST/runs/run-0007/result.json'), ('conformance', (*GND_PREFIX, 'conformance', 'model.orm.yaml', 'project'), frozenset({0, 13}), 300, 'walks/walk-0042.conformance.out'))
    assert actual == expected

def test_t02_station_policy_behavior_moves_with_the_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    requested_argv = ('fixture-child', '--moved-with-table')
    _patch_station(monkeypatch, 'validate', argv=lambda _paths: requested_argv, accepted_exits=frozenset({23}))
    accepted_root = tmp_path / 'accepted'
    workspace, model, _ = _seed_workspace(accepted_root)
    accepted_spawn = FakeSpawn(outcomes={'validate': solve.StationOutcome(23, None)})
    assert _run(model, workspace, start='validate', until='validate', spawn=accepted_spawn) == 0
    assert accepted_spawn.calls[0].argv == requested_argv
    rejected_root = tmp_path / 'rejected'
    workspace, model, _ = _seed_workspace(rejected_root)
    rejected_spawn = FakeSpawn()
    assert _run(model, workspace, start='validate', until='validate', spawn=rejected_spawn) == cli.EXIT_WALK_HALTED
    assert _station_records(_read_records(workspace))[0]['exit'] == 0

def test_t02_station_policy_ast_lint_is_secondary_and_deliberately_shallow() -> None:
    tree = ast.parse(SOLVE_SOURCE.read_text(encoding='utf-8'))
    source_lines = SOLVE_SOURCE.read_text(encoding='utf-8').splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        has_return_attribute = any(isinstance(operand, ast.Attribute) and operand.attr in {'returncode', 'exit', 'exit_code'} for operand in operands)
        has_integer_literal = any(isinstance(operand, ast.Constant) and type(operand.value) is int for operand in operands)
        assert not (has_return_attribute and has_integer_literal), f'station exit policy escaped STATIONS at line {node.lineno}'
    station_literal_lines = {index for index, line in enumerate(source_lines, 1) if line.lstrip().startswith('Station(')}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value in {300, 3600}:
            assert node.lineno in station_literal_lines, f'station timeout literal {node.value} escaped STATIONS at line {node.lineno}'

def _enclosing_function(tree: ast.AST, target: ast.AST) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and target in ast.walk(node):
            return node.name
    return None

def test_t03_every_child_uses_the_single_non_shell_spawn_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tree = ast.parse(SOLVE_SOURCE.read_text(encoding='utf-8'))
    popen_calls: list[ast.Call] = []
    banned_subprocess_calls = {'run', 'call', 'check_call', 'check_output'}
    banned_asyncio_calls = {'create_subprocess_exec', 'create_subprocess_shell'}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imported = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module] if node.module else []
            assert 'shlex' not in imported
            if isinstance(node, ast.ImportFrom) and node.module == 'subprocess':
                assert not {alias.name for alias in node.names} & banned_subprocess_calls
            if isinstance(node, ast.ImportFrom) and node.module == 'asyncio':
                assert not {alias.name for alias in node.names} & banned_asyncio_calls
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute):
            if isinstance(function.value, ast.Name) and function.value.id == 'subprocess' and (function.attr == 'Popen'):
                popen_calls.append(node)
            if isinstance(function.value, ast.Name) and function.value.id == 'subprocess':
                assert function.attr not in banned_subprocess_calls
            if isinstance(function.value, ast.Name) and function.value.id == 'asyncio':
                assert function.attr not in banned_asyncio_calls
            if isinstance(function.value, ast.Name) and function.value.id == 'os':
                assert function.attr not in {'system', 'popen'}
                assert not function.attr.startswith('exec')
    assert len(popen_calls) == 1
    popen = popen_calls[0]
    assert _enclosing_function(tree, popen) == '_run_child'
    shell_keywords = [keyword for keyword in popen.keywords if keyword.arg == 'shell']
    assert not shell_keywords or all(isinstance(keyword.value, ast.Constant) and keyword.value.value is False for keyword in shell_keywords)
    calls_to_run_child = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and (node.func.id == '_run_child')]
    assert len(calls_to_run_child) == 1
    assert _enclosing_function(tree, calls_to_run_child[0]) == '_spawn_station'
    captured: dict[str, object] = {}

    class Child:
        pid = 12345

        def wait(self, *, timeout: int) -> int:
            captured['timeout'] = timeout
            return 0

    def fake_popen(argv: object, **kwargs: object) -> Child:
        captured['argv'] = argv
        captured['kwargs'] = kwargs
        return Child()
    monkeypatch.setattr(solve.subprocess, 'Popen', fake_popen)
    walks = tmp_path / 'walks'
    walks.mkdir()
    request = solve.StationSpawn(argv=('fixture-child', '--one-word'), cwd=tmp_path, timeout_s=9, stdout_path=walks / 'child.out', stderr_path=walks / 'child.err')
    assert solve._spawn_station(request) == solve.StationOutcome(0, None)
    assert type(captured['argv']) is list, 'Popen must receive a list argv'
    kwargs = captured['kwargs']
    assert isinstance(kwargs, dict)
    assert kwargs.get('shell', False) is False

@pytest.mark.parametrize('escape_kind', ['dotdot', 'absolute', 'symlink'])
def test_t04_escaping_evidence_is_never_recorded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, escape_kind: str) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    outside = tmp_path / 'outside'
    outside.mkdir()
    if escape_kind == 'dotdot':
        escaping = '../escape'
    elif escape_kind == 'absolute':
        escaping = (outside / 'escape').as_posix()
    else:
        (workspace / 'linked-out').symlink_to(outside, target_is_directory=True)
        escaping = 'linked-out/escape'
    _patch_station(monkeypatch, 'validate', evidence=lambda _paths: escaping)
    assert _run(model, workspace, start='validate', until='validate') == cli.EXIT_WALK_HALTED
    raw = _walk_file(workspace).read_bytes()
    station_record = _station_records(_read_records(workspace))[0]
    assert station_record['evidence'] is None
    assert station_record['halt'] == 'evidence-ambiguous'
    assert escaping.encode() not in raw

def test_t05_record_schema_is_exact_per_kind(tmp_path: Path) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    assert _run(model, workspace, start='validate', until='validate') == 0
    records = _read_records(workspace)
    assert [record['record'] for record in records] == ['walk', 'gate', 'station']
    for record in records:
        assert tuple(record) == RECORD_KEYS[record['record']]
    extra = dict(records[0])
    extra['verdict'] = 'pass'
    missing = dict(records[1])
    missing.pop('argv')
    assert tuple(extra) != RECORD_KEYS['walk']
    assert tuple(missing) != RECORD_KEYS['gate']

def test_t06_no_log_has_an_aggregate_key_and_recursive_control_is_rejected(tmp_path: Path) -> None:
    logs: list[bytes] = []
    complete_root = tmp_path / 'complete'
    workspace, model, _ = _seed_workspace(complete_root)
    assert _run(model, workspace, start='validate', until='validate') == 0
    logs.append(_walk_file(workspace).read_bytes())
    decline_root = tmp_path / 'decline'
    workspace, model, _ = _seed_workspace(decline_root)
    assert _run(model, workspace, start='validate', until='validate', gate=lambda _station: None) == cli.EXIT_WALK_HALTED
    logs.append(_walk_file(workspace).read_bytes())
    refusal_root = tmp_path / 'refusal'
    workspace, model, _ = _seed_workspace(refusal_root)
    assert _run(model, workspace, start='codegen', until='codegen', auto=True, gate=_fail_gate, spawn=FakeSpawn(outcomes={'codegen': solve.StationOutcome(11, None)})) == cli.EXIT_WALK_HALTED
    logs.append(_walk_file(workspace).read_bytes())
    timeout_root = tmp_path / 'timeout'
    workspace, model, _ = _seed_workspace(timeout_root)
    assert _run(model, workspace, start='validate', until='validate', spawn=FakeSpawn(outcomes={'validate': solve.StationOutcome(None, 'timeout')})) == cli.EXIT_WALK_HALTED
    logs.append(_walk_file(workspace).read_bytes())
    assert all(_log_has_no_aggregate_keys(raw) for raw in logs)
    negative_control = b'{"record":"walk","walk_id":"walk-x","schema_version":1,"model":"m","selected":[],"flags":{"from":null,"until":null,"skip":[],"auto":false,"adapter":null,"adapter_explicit":false,"experiment":null,"test_argv":[],"station_timeout":{},"nested":{"deeper":{"verdict":"pass"}}},"started":"x"}\n'
    assert not _log_has_no_aggregate_keys(negative_control)

def test_t07_declined_gate_halts_before_spawn(tmp_path: Path) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    spawn = FakeSpawn()
    assert _run(model, workspace, start='validate', until='synth', gate=lambda _station: None, spawn=spawn) == cli.EXIT_WALK_HALTED
    records = _read_records(workspace)
    assert records[-1]['record'] == 'gate'
    assert records[-1]['station'] == 'validate'
    assert records[-1]['authorized_by'] is None
    assert not _station_records(records)
    assert spawn.calls == []

def test_t08_from_until_are_inclusive_and_exclusive(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    spawn = FakeSpawn()
    assert _run(model, workspace, experiment=experiment, start='synth', until='exp-run', spawn=spawn) == 0
    selected = _read_records(workspace)[0]['selected']
    spawned = [_station_name_from_capture(call.stdout_path) for call in spawn.calls]
    assert selected == ['synth', 'codegen', 'exp-run']
    assert spawned == ['synth', 'codegen', 'exp-run']
    for absent in ('validate', 'conformance'):
        assert absent not in selected
        assert absent not in spawned

def test_t09_brownfield_profile_runs_validate_and_exp_run_only(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    spawn = FakeSpawn()
    assert _run(model, workspace, experiment=experiment, skip=frozenset({'synth', 'codegen', 'conformance'}), spawn=spawn) == 0
    records = _read_records(workspace)
    assert records[0]['selected'] == ['validate', 'exp-run']
    assert [_station_name_from_capture(call.stdout_path) for call in spawn.calls] == ['validate', 'exp-run']

def test_t10_auto_halts_on_station_refusal_and_keeps_child_exit(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    spawn = FakeSpawn(outcomes={'codegen': solve.StationOutcome(11, None)})
    assert _run(model, workspace, experiment=experiment, auto=True, gate=_fail_gate, spawn=spawn) == cli.EXIT_WALK_HALTED
    records = _read_records(workspace)
    codegen = next(record for record in _station_records(records) if record['station'] == 'codegen')
    assert codegen['exit'] == 11
    spawned = [_station_name_from_capture(call.stdout_path) for call in spawn.calls]
    assert spawned == ['validate', 'synth', 'codegen']
    assert 'exp-run' not in spawned
    assert 'conformance' not in spawned

@pytest.mark.parametrize(('keyword', 'value'), [('start', 'unknown'), ('until', 'unknown'), ('skip', frozenset({'unknown'}))])
def test_t11_unknown_bounds_and_skip_refuse_before_log_or_spawn(tmp_path: Path, keyword: str, value: object) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    arguments: dict[str, object] = {keyword: value}
    assert _run(model, workspace, spawn=_fail_spawn, **arguments) == cli.EXIT_USAGE
    assert _walk_files(workspace) == []

def test_t12_help_states_all_seven_guarantee_perimeter_claims(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        cli.main(['solve', '--help'])
    assert caught.value.code == 0
    help_text = capsys.readouterr().out.lower()
    required_literals = ['sequence, gating and logging for walks that go through it', 'running the stations a la carte stays legal', 'it does not judge station-internal agent work', "a station's own exit is in the log, not in this command's exit code", 'the brownfield profile assumes recovery already completed', 'the walk log records what this harness did; it is not proof that it did it', "the outer station timeout is not the contract's inner --wall-seconds bound"]
    for literal in required_literals:
        assert literal in help_text

def test_t12_help_derives_station_order_and_exit_map_from_their_owners(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    patched_stations = (replace(solve.STATIONS[0], name='validate-mutant'), *solve.STATIONS[1:])
    patched_exits = tuple(((117, meaning) if code == exits.EXIT_WALK_HALTED else (code, meaning) for code, meaning in exits.SOLVE_CONTROL_PLANE_EXITS))
    monkeypatch.setattr(solve, 'STATIONS', patched_stations)
    monkeypatch.setattr(exits, 'SOLVE_CONTROL_PLANE_EXITS', patched_exits)
    with pytest.raises(SystemExit) as caught:
        cli.main(['solve', '--help'])
    assert caught.value.code == 0
    help_text = capsys.readouterr().out.lower()
    assert 'validate-mutant, synth, codegen, exp-run, conformance' in help_text
    assert '117 a walk that halted at a station' in help_text
    assert re.search('(?<!\\d)17 a walk that halted at a station', help_text) is None

@dataclass(frozen=True)
class B5Mutant:
    name: str
    expected: frozenset[int]
    mutate: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]

def _mutant_missing_station(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return records[:-1]

def _mutant_wrong_order(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [records[0], *records[3:5], *records[1:3]]

def _mutant_null_authorization(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = copy.deepcopy(records)
    changed[1]['authorized_by'] = None
    return changed

def _mutant_bad_exit(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = copy.deepcopy(records)
    changed[2]['exit'] = 99
    return changed

def _mutant_trailing_halt(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = copy.deepcopy(records)
    changed[-1]['halt'] = 'timeout'
    return changed

def _mutant_unselected_station(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    walk_id = records[0]['walk_id']
    stamp = '2026-08-24T12:34:56Z'
    return [*copy.deepcopy(records), {'record': 'gate', 'walk_id': walk_id, 'station': 'codegen', 'argv': ['gnd', 'codegen', 'model.orm.yaml', '--out', 'project'], 'authorized_by': f'stdin "go" {stamp}'}, {'record': 'station', 'walk_id': walk_id, 'station': 'codegen', 'exit': 0, 'evidence': 'project/.gnd-codegen.json', 'halt': None}]

def _mutant_two_headers(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    header = copy.deepcopy(records[0])
    return [header, *copy.deepcopy(records[1:3]), copy.deepcopy(header), *copy.deepcopy(records[3:5])]

def _mutant_all_skip(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    header = copy.deepcopy(records[0])
    header['selected'] = []
    header['flags']['skip'] = list(LOCKED_STATIONS)
    return [header]

def _mutant_interleaved(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [records[0], records[1], records[3], records[2], records[4]]

def _mutant_auto_stdin(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = copy.deepcopy(records)
    changed[0]['flags']['auto'] = True
    return changed

def _mutant_foreign_walk_id(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = copy.deepcopy(records)
    changed[2]['walk_id'] = 'walk-foreign'
    return changed

def _mutant_skip_outside_bounds(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    header = copy.deepcopy(records[0])
    header['selected'] = ['synth']
    header['flags']['from'] = 'synth'
    header['flags']['until'] = 'synth'
    header['flags']['skip'] = ['validate']
    return [header, *copy.deepcopy(records[3:5])]

def _mutant_header_names_unselected_station(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = copy.deepcopy(records)
    changed[0]['station'] = 'outside-selected'
    return changed

def _mutant_impossible_authorization_timestamp(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changed = copy.deepcopy(records)
    changed[1]['authorized_by'] = 'stdin "go" 2026-99-99T99:99:99Z'
    return changed
B5_MUTANTS = (B5Mutant('missing-station', frozenset({2, 7}), _mutant_missing_station), B5Mutant('wrong-station-order', frozenset({2}), _mutant_wrong_order), B5Mutant('null-authorized-by', frozenset({3}), _mutant_null_authorization), B5Mutant('exit-outside-set', frozenset({5}), _mutant_bad_exit), B5Mutant('trailing-halt', frozenset({4}), _mutant_trailing_halt), B5Mutant('unselected-station', frozenset({2}), _mutant_unselected_station), B5Mutant('two-headers', frozenset({1, 7}), _mutant_two_headers), B5Mutant('all-skip', frozenset({6}), _mutant_all_skip), B5Mutant('gate-gate-station-station', frozenset({7}), _mutant_interleaved), B5Mutant('auto-header-stdin-gates', frozenset({8}), _mutant_auto_stdin), B5Mutant('foreign-walk-id', frozenset({1}), _mutant_foreign_walk_id), B5Mutant('skip-outside-bounds', frozenset({6}), _mutant_skip_outside_bounds), B5Mutant('header-names-unselected-station', frozenset({2}), _mutant_header_names_unselected_station), B5Mutant('impossible-authorization-timestamp', frozenset({3}), _mutant_impossible_authorization_timestamp))

@pytest.mark.parametrize('mutant', B5_MUTANTS, ids=lambda mutant: mutant.name)
def test_t15_b5_reports_each_mutants_exact_conjunct_set(tmp_path: Path, mutant: B5Mutant) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    assert _run(model, workspace, start='validate', until='synth') == 0
    raw = _walk_file(workspace).read_bytes()
    assert b5_failures(raw) == frozenset()
    records = _bounded_jsonl_objects(raw)
    assert records is not None
    assert b5_failures(_encode_records(mutant.mutate(records))) == mutant.expected

@pytest.mark.parametrize('case', ['arbitrary-json', 'non-object', 'non-json', 'empty', 'over-bytes', 'over-lines', 'over-depth', 'invalid-utf8', 'nul'])
def test_t17_b5_reader_is_total_within_all_three_bounds(case: str) -> None:
    assert B5_MAX_BYTES == 8 * 1024 * 1024
    assert B5_MAX_LINES == 10000
    assert B5_MAX_DEPTH == 64
    if case == 'arbitrary-json':
        raw = b'{"unrelated":true}\n'
    elif case == 'non-object':
        raw = b'[]\n'
    elif case == 'non-json':
        raw = b'this is not json\n'
    elif case == 'empty':
        raw = b''
    elif case == 'over-bytes':
        raw = b'x' * (8 * 1024 * 1024 + 1)
    elif case == 'over-lines':
        raw = b'{}\n' * (10000 + 1)
    elif case == 'over-depth':
        raw = ('[' * 65 + '0' + ']' * 65 + '\n').encode()
    elif case == 'invalid-utf8':
        raw = b'{"record":"walk","x":"\x80"}\n'
    else:
        raw = b'{"record":"walk","x":"before\x00after"}\n'
    failures = b5_failures(raw)
    assert isinstance(failures, frozenset)
    assert failures

def test_t17_json_nesting_cap_accepts_64_and_refuses_65_before_parsing() -> None:
    assert B5_MAX_DEPTH == 64
    at_cap = '[' * 64 + '0' + ']' * 64
    over_cap = '[' * 65 + '0' + ']' * 65
    assert _json_depth_at_most(at_cap)
    assert not _json_depth_at_most(over_cap)

def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True

def test_t18_station_timeout_reaps_the_child_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    pid_file = workspace / 'sleeper.pid'
    child_script = f'import os,time,pathlib; pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(60)'
    _patch_station(monkeypatch, 'validate', argv=lambda _paths: (sys.executable, '-c', child_script))
    assert _run(model, workspace, start='validate', until='validate', station_timeout={'validate': 1}, gate=_allow, clock=_fixed_clock, spawn=solve._spawn_station) == cli.EXIT_WALK_HALTED
    station_record = _station_records(_read_records(workspace))[0]
    assert station_record['exit'] is None
    assert station_record['halt'] == 'timeout'
    pid = int(pid_file.read_text(encoding='utf-8'))
    assert not _pid_exists(pid), f'timed-out child {pid} survived the harness'

@dataclass(frozen=True)
class ExitCase:
    name: str
    expected_code: int
    expected_b5: frozenset[int] | None
EXIT_CASES = (ExitCase('completed', 0, frozenset()), ExitCase('help', 0, None), ExitCase('version', 0, None), ExitCase('unaccepted-exit', 17, frozenset({5})), ExitCase('unaccepted-exit-nonfinal', 17, frozenset({2, 5})), ExitCase('declined-gate', 17, frozenset({2, 3, 7})), ExitCase('timeout', 17, frozenset({4})), ExitCase('timeout-nonfinal', 17, frozenset({2, 4})), ExitCase('signal', 17, frozenset({4})), ExitCase('signal-nonfinal', 17, frozenset({2, 4})), ExitCase('evidence-ambiguous', 17, frozenset({4})), ExitCase('evidence-ambiguous-nonfinal', 17, frozenset({2, 4})), ExitCase('usage-stage-2', 64, None), ExitCase('missing-stage-6', 66, None), ExitCase('io-stage-7', 74, None), ExitCase('walk-file-create', 74, None), ExitCase('spawn-error', 74, frozenset({4})), ExitCase('spawn-error-nonfinal', 74, frozenset({2, 4})), ExitCase('capture-open', 74, frozenset({4})), ExitCase('first-append', 74, frozenset({1})), ExitCase('later-append', 74, frozenset({2, 7})), ExitCase('flush-after-complete-bytes', 74, frozenset()), ExitCase('close-after-complete-walk', 74, frozenset()), ExitCase('internal-record-defect', 70, frozenset({1})))

def _run_exit_case(case: ExitCase, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> tuple[int, Path | None]:
    root = tmp_path / case.name
    if case.name == 'help':
        with pytest.raises(SystemExit) as caught:
            cli.main(['solve', '--help'])
        capsys.readouterr()
        return (int(caught.value.code), None)
    if case.name == 'version':
        with pytest.raises(SystemExit) as caught:
            cli.main(['--version'])
        capsys.readouterr()
        return (int(caught.value.code), None)
    if case.name == 'io-stage-7':
        workspace = root / 'workspace'
        workspace.parent.mkdir(parents=True)
        workspace.write_text('not a directory\n', encoding='utf-8')
        model = root / 'model.orm.yaml'
        model.write_text('object_types: []\n', encoding='utf-8')
        return (_run(model, workspace, spawn=_fail_spawn), workspace)
    workspace, model, experiment = _seed_workspace(root, experiment=case.name.startswith('evidence-ambiguous'))
    if case.name == 'completed':
        code = _run(model, workspace, start='validate', until='validate')
    elif case.name in {'unaccepted-exit', 'unaccepted-exit-nonfinal'}:
        until = 'validate' if case.name == 'unaccepted-exit' else 'synth'
        code = _run(model, workspace, start='validate', until=until, spawn=FakeSpawn(outcomes={'validate': solve.StationOutcome(9, None)}))
    elif case.name == 'declined-gate':
        code = _run(model, workspace, start='validate', until='validate', gate=lambda _station: None)
    elif case.name in {'timeout', 'timeout-nonfinal', 'signal', 'signal-nonfinal'}:
        halt = 'timeout' if case.name.startswith('timeout') else 'signal'
        until = 'validate' if not case.name.endswith('nonfinal') else 'synth'
        code = _run(model, workspace, start='validate', until=until, spawn=FakeSpawn(outcomes={'validate': solve.StationOutcome(None, halt)}))
    elif case.name.startswith('evidence-ambiguous'):
        if case.name.endswith('nonfinal'):
            (workspace / 'project').mkdir()
        code = _run(model, workspace, experiment=experiment, start='exp-run', until='conformance' if case.name.endswith('nonfinal') else 'exp-run', spawn=FakeSpawn(exp_indices=()))
    elif case.name == 'usage-stage-2':
        code = _run(model, workspace, start='unknown', spawn=_fail_spawn)
    elif case.name == 'missing-stage-6':
        missing_model = workspace / 'missing.orm.yaml'
        code = _run(missing_model, workspace, spawn=_fail_spawn)
    elif case.name == 'walk-file-create':
        monkeypatch.setattr(solve, '_allocate_walk_file', lambda _directory, **_kwargs: (_ for _ in ()).throw(OSError('injected')))
        code = _run(model, workspace, start='validate', until='validate')
    elif case.name in {'spawn-error', 'spawn-error-nonfinal'}:
        code = _run(model, workspace, start='validate', until='synth' if case.name.endswith('nonfinal') else 'validate', spawn=FakeSpawn(outcomes={'validate': solve.StationOutcome(None, 'spawn-error')}))
    elif case.name == 'capture-open':
        monkeypatch.setattr(solve, '_open_capture', lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError('injected capture refusal')))
        code = _run(model, workspace, start='validate', until='validate', spawn=solve._spawn_station)
    elif case.name in {'first-append', 'later-append'}:
        fail_at = 1 if case.name == 'first-append' else 3
        original_append = solve._WalkLog.append
        calls = 0

        def fail_nth(log: object, record: Mapping[str, object]) -> None:
            nonlocal calls
            calls += 1
            if calls == fail_at:
                raise OSError('injected append refusal')
            original_append(log, record)
        monkeypatch.setattr(solve._WalkLog, 'append', fail_nth)
        code = _run(model, workspace, start='validate', until='validate')
    elif case.name == 'flush-after-complete-bytes':
        original_fsync = os.fsync
        calls = 0

        def fail_final_fsync(fd: int) -> None:
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('injected durability refusal')
            original_fsync(fd)
        monkeypatch.setattr(os, 'fsync', fail_final_fsync)
        code = _run(model, workspace, start='validate', until='validate')
    elif case.name == 'close-after-complete-walk':
        original_fdopen = os.fdopen

        class CloseFailingHandle:

            def __init__(self, handle: Any) -> None:
                self._handle = handle

            def __getattr__(self, name: str) -> Any:
                return getattr(self._handle, name)

            def close(self) -> None:
                self._handle.close()
                raise OSError('injected close refusal')

        def close_failing_fdopen(*args: object, **kwargs: object) -> CloseFailingHandle:
            return CloseFailingHandle(original_fdopen(*args, **kwargs))
        monkeypatch.setattr(os, 'fdopen', close_failing_fdopen)
        code = _run(model, workspace, start='validate', until='validate')
    else:
        original_encoder = solve.encode_record

        def reorder_then_encode(record: Mapping[str, object]) -> bytes:
            reordered = dict(reversed(tuple(record.items())))
            return original_encoder(reordered)
        monkeypatch.setattr(solve, 'encode_record', reorder_then_encode)
        code = _run(model, workspace, start='validate', until='validate')
    return (code, workspace)

@pytest.mark.parametrize('case', EXIT_CASES, ids=lambda case: case.name)
def test_t19_exit_table_is_total_with_the_literal_log_effects(case: ExitCase, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    code, workspace = _run_exit_case(case, tmp_path, monkeypatch, capsys)
    assert code == case.expected_code
    if case.expected_b5 is None:
        assert workspace is None or _walk_files(workspace) == []
    else:
        assert workspace is not None
        assert b5_failures(_walk_file(workspace).read_bytes()) == case.expected_b5
GATE_CASES = (('eof', b'', 17, None), ('257-with-newline', b'a' * 257 + b'\n', 0, 'a' * 257), ('258-with-newline', b'a' * 258 + b'\n', 17, None), ('258-without-newline', b'a' * 258, 17, None), ('invalid-utf8', b'\x80\n', 17, None), ('json-roundtrip', b'quote" slash\\ tab\t\n', 0, 'quote" slash\\ tab\t'), ('short-eof', b'fits-without-newline', 0, 'fits-without-newline'))

@pytest.mark.parametrize(('name', 'payload', 'expected_code', 'expected_reply'), GATE_CASES, ids=[case[0] for case in GATE_CASES])
def test_t20_gate_byte_boundaries_and_json_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, payload: bytes, expected_code: int, expected_reply: str | None) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    monkeypatch.setattr(sys, 'stdin', _BinaryStdin(payload))
    spawn = FakeSpawn()

    def real_gate(station: solve.Station) -> str | None:
        return solve._blocking_stdin_gate(station)
    code = _run(model, workspace, start='validate', until='validate', gate=real_gate, clock=_fixed_clock, spawn=spawn)
    assert code == expected_code, name
    gate_record = _gate_records(_read_records(workspace))[0]
    if expected_reply is None:
        assert gate_record['authorized_by'] is None
        assert spawn.calls == []
    else:
        value = gate_record['authorized_by']
        assert isinstance(value, str)
        match = AUTHORIZED_BY_RE.fullmatch(value)
        assert match is not None
        assert json.loads(match.group('reply')) == expected_reply
        assert len(spawn.calls) == 1

def test_t21_walk_file_allocation_skips_holes_and_uses_exclusive_create(tmp_path: Path) -> None:
    holes = tmp_path / 'holes'
    holes.mkdir()
    (holes / 'walk-0001.jsonl').write_bytes(b'one\n')
    (holes / 'walk-0003.jsonl').write_bytes(b'three\n')
    allocated, walk_id, handle = solve._allocate_walk_file(holes)
    handle.close()
    assert allocated.name == 'walk-0004.jsonl'
    assert walk_id == 'walk-0004'
    assert not (holes / 'walk-0002.jsonl').exists()
    exclusive = tmp_path / 'exclusive'
    exclusive.mkdir()
    existing = exclusive / 'walk-0001.jsonl'
    existing.write_bytes(b'sentinel-do-not-append\n')
    original_scan = solve._scan_indices
    stale_injections = 0

    def stale_scan(directory: Path | int, pattern: re.Pattern[str], *, entry_type: str) -> set[int] | None:
        nonlocal stale_injections
        actual = os.fstat(directory) if isinstance(directory, int) else directory.stat()
        expected = exclusive.stat()
        if (actual.st_dev, actual.st_ino) == (expected.st_dev, expected.st_ino) and stale_injections == 0:
            stale_injections += 1
            return set()
        return original_scan(directory, pattern, entry_type=entry_type)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(solve, '_scan_indices', stale_scan)
        allocated, walk_id, handle = solve._allocate_walk_file(exclusive)
    handle.close()
    assert stale_injections == 1
    assert allocated.name == 'walk-0002.jsonl'
    assert walk_id == 'walk-0002'
    assert existing.read_bytes() == b'sentinel-do-not-append\n'

def test_t21_walk_log_keeps_the_exclusively_created_descriptor(tmp_path: Path) -> None:
    walks = tmp_path / 'walks'
    walks.mkdir()
    allocated, walk_id, handle = solve._allocate_walk_file(walks)
    created = walks / 'created-by-harness.jsonl'
    allocated.rename(created)
    allocated.write_bytes(b'replacement-must-stay-untouched\n')
    log = solve._WalkLog(allocated, handle)
    record = {'record': 'gate', 'walk_id': walk_id, 'station': 'validate', 'argv': ['gnd', 'validate', 'model.orm.yaml'], 'authorized_by': 'stdin "go" 2026-08-24T12:34:56Z'}
    log.append(record)
    log.close()
    assert allocated.read_bytes() == b'replacement-must-stay-untouched\n'
    assert created.read_bytes() == solve.encode_record(record)

def test_t21_allocator_retries_above_a_concurrently_published_higher_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    walks = tmp_path / 'walks'
    walks.mkdir()
    (walks / 'walk-0005.jsonl').write_bytes(b'five\n')
    original_scan = solve._scan_indices
    scans = 0

    def publish_high_index(directory: Path, pattern: re.Pattern[str], *, entry_type: str) -> set[int] | None:
        nonlocal scans
        scans += 1
        if scans == 2:
            (walks / 'walk-9999.jsonl').write_bytes(b'concurrent\n')
        return original_scan(directory, pattern, entry_type=entry_type)
    monkeypatch.setattr(solve, '_scan_indices', publish_high_index)
    allocated, walk_id, handle = solve._allocate_walk_file(walks)
    handle.close()
    assert allocated.name == 'walk-10000.jsonl'
    assert walk_id == 'walk-10000'
    assert not (walks / 'walk-0006.jsonl').exists()

def test_f07_walk_discovery_ignores_directories_with_walk_names(tmp_path: Path) -> None:
    walks = tmp_path / 'walks'
    walks.mkdir()
    (walks / 'walk-0003.jsonl').write_bytes(b'three\n')
    (walks / 'walk-0007').mkdir()
    assert solve._scan_indices(walks, solve._WALK_STEM, entry_type='file') == {3}

def test_f07_run_discovery_ignores_regular_files_with_run_names(tmp_path: Path) -> None:
    runs = tmp_path / 'runs'
    runs.mkdir()
    (runs / 'run-0003').mkdir()
    (runs / 'run-0007').write_bytes(b'not-a-run-directory\n')
    assert solve._scan_indices(runs, solve._RUN_DIR, entry_type='directory') == {3}

def test_t22_authorized_by_matches_the_literal_regex_for_stdin_and_auto(tmp_path: Path) -> None:
    values: dict[str, str] = {}
    raws: dict[str, bytes] = {}
    for mode in ('stdin', 'auto'):
        workspace, model, _ = _seed_workspace(tmp_path / mode)
        assert _run(model, workspace, start='validate', until='validate', auto=mode == 'auto', gate=_fail_gate if mode == 'auto' else lambda _station: 'go "now"', clock=_fixed_clock, spawn=FakeSpawn()) == 0
        raw = _walk_file(workspace).read_bytes()
        value = _gate_records(_read_records(workspace))[0]['authorized_by']
        assert isinstance(value, str)
        match = AUTHORIZED_BY_RE.fullmatch(value)
        assert match is not None
        assert match.group('source') == mode
        assert match.group('timestamp') == '2026-08-24T12:34:56Z'
        values[mode] = value
        raws[mode] = raw
    assert values['stdin'] != values['auto']
    assert raws['stdin'] != raws['auto']

@pytest.mark.parametrize(('case', 'expected'), [('exp-without-experiment', 64), ('missing-experiment', 66), ('experiment-without-exp', 64), ('conformance-without-project', 64)])
def test_t23_nonderivable_station_arguments_refuse_before_spawn(tmp_path: Path, case: str, expected: int) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=case in {'experiment-without-exp', 'conformance-without-project'})
    arguments: dict[str, object]
    if case == 'exp-without-experiment':
        arguments = {'start': 'exp-run', 'until': 'exp-run'}
    elif case == 'missing-experiment':
        arguments = {'experiment': workspace / 'missing-experiment', 'start': 'exp-run', 'until': 'exp-run'}
    elif case == 'experiment-without-exp':
        arguments = {'experiment': experiment, 'start': 'validate', 'until': 'validate'}
    else:
        arguments = {'experiment': experiment, 'skip': frozenset({'codegen'})}
    assert _run(model, workspace, spawn=_fail_spawn, **arguments) == expected
    assert _walk_files(workspace) == []

def test_t23_adapter_vocabulary_is_closed_at_the_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    monkeypatch.setattr(solve, 'run_walk', lambda *args, **kwargs: pytest.fail('run_walk called'))
    with pytest.raises(SystemExit) as caught:
        cli.main(['solve', str(model), '--workspace', str(workspace), '--experiment', str(experiment), '--adapter', 'other'])
    assert caught.value.code == cli.EXIT_USAGE
    assert _walk_files(workspace) == []

def test_g05_g08_adapter_policy_is_forwarded_but_not_logged(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    assert experiment is not None
    policy = tmp_path / 'trusted.policy.json'
    policy.write_text('{"policy":"bytes"}\n', encoding='utf-8')
    spawned = FakeSpawn()
    assert _run(model, workspace, experiment=experiment, start='exp-run', until='exp-run', adapter_policy=policy, auto=True, spawn=spawned) == 0
    assert spawned.calls[0].argv[-2:] == ('--adapter-policy', str(policy))
    raw = _walk_file(workspace).read_bytes()
    assert str(policy).encode() not in raw
    assert b'<adapter-policy:sha256=' in raw
    other = tmp_path / 'both'
    other_workspace, other_model, other_experiment = _seed_workspace(other, experiment=True)
    assert _run(other_model, other_workspace, experiment=other_experiment, start='exp-run', until='exp-run', adapter='codex', adapter_policy=policy, spawn=_fail_spawn) == cli.EXIT_USAGE
    assert _walk_files(other_workspace) == []

def test_g05_g08_adapter_policy_replacement_before_spawn_is_refused(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    assert experiment is not None
    policy = tmp_path / 'trusted.policy.json'
    policy.write_text('{"policy":"first"}\n', encoding='utf-8')

    def replace_at_gate(_station: solve.Station) -> str:
        policy.write_text('{"policy":"second"}\n', encoding='utf-8')
        return 'go'
    assert _run(model, workspace, experiment=experiment, start='exp-run', until='exp-run', adapter_policy=policy, gate=replace_at_gate, spawn=_fail_spawn) == cli.EXIT_IO

def test_t23_cli_refuses_an_overlong_timeout_integer_without_int_conversion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    monkeypatch.setattr(solve, 'run_walk', lambda *args, **kwargs: pytest.fail('run_walk called'))
    code = cli.main(['solve', str(model), '--workspace', str(workspace), '--station-timeout', f"validate={'9' * 5000}"])
    captured = capsys.readouterr()
    assert code == cli.EXIT_USAGE
    assert 'traceback' not in captured.err.lower()
    assert _walk_files(workspace) == []

@pytest.mark.parametrize(('case', 'station_timeout', 'adapter'), [('timeout-zero', {'validate': 0}, None), ('timeout-over-ceiling', {'validate': 86401}, None), ('adapter-outside-vocabulary', {}, 'other')])
def test_t23_public_run_walk_enforces_typed_stage_one_rules(tmp_path: Path, case: str, station_timeout: Mapping[str, int], adapter: str | None) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path / case, experiment=adapter is not None)
    arguments: dict[str, object] = {'station_timeout': station_timeout, 'adapter': adapter, 'spawn': _fail_spawn}
    if adapter is not None:
        arguments.update(experiment=experiment, start='exp-run', until='exp-run')
    else:
        arguments.update(start='validate', until='validate')
    assert _run(model, workspace, **arguments) == cli.EXIT_USAGE
    assert _walk_files(workspace) == []

def test_t23b_exp_run_argv_never_passes_wall_seconds(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    spawn = FakeSpawn()
    assert _run(model, workspace, experiment=experiment, start='exp-run', until='exp-run', station_timeout={'exp-run': 7}, spawn=spawn) == 0
    argv = spawn.calls[0].argv
    assert argv[:5] == (*GND_PREFIX, 'exp', 'run')
    assert '--wall-seconds' not in argv

@pytest.mark.parametrize('new_index', [2, 4])
def test_t24_exp_run_evidence_is_the_single_set_difference(tmp_path: Path, new_index: int) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    assert experiment is not None
    runs = experiment / 'runs'
    for index in (1, 3):
        (runs / f'run-{index:04d}').mkdir(parents=True)
    before = {1, 3}
    spawn = FakeSpawn(exp_indices=(new_index,))
    assert _run(model, workspace, experiment=experiment, start='exp-run', until='exp-run', spawn=spawn) == 0
    after = {int(path.name.removeprefix('run-')) for path in runs.iterdir() if path.name.startswith('run-')}
    assert after - before == {new_index}
    evidence = _station_records(_read_records(workspace))[0]['evidence']
    assert evidence == f'EXP-TEST/runs/run-{new_index:04d}/result.json'

def test_d02_conformance_accepts_thirteen_and_only_conformance_does(tmp_path: Path) -> None:
    workspace, model, _ = _seed_workspace(tmp_path / 'accepted')
    (workspace / 'project').mkdir()
    assert _run(model, workspace, start='conformance', until='conformance', spawn=FakeSpawn(outcomes={'conformance': solve.StationOutcome(13, None)})) == 0
    record = _station_records(_read_records(workspace))[0]
    assert record['station'] == 'conformance'
    assert record['exit'] == 13
    assert record['halt'] is None
    for name in ('validate', 'synth', 'codegen'):
        other, other_model, _ = _seed_workspace(tmp_path / f'refused-{name}')
        assert _run(other_model, other, start=name, until=name, spawn=FakeSpawn(outcomes={name: solve.StationOutcome(13, None)})) == cli.EXIT_WALK_HALTED, f'{name} must not accept 13'
    assert solve.station_by_name('conformance').accepted_exits == frozenset({0, 13})
    for station in solve.STATIONS:
        if station.name != 'conformance':
            assert station.accepted_exits == frozenset({0}), station.name

def test_t26_exit_walk_halted_does_not_collide_with_another_exit_constant() -> None:
    sources = [*cli_source_paths(), REPO_ROOT / 'src' / 'gnd' / 'exits.py']
    values: dict[str, int] = {}
    nodes = [node for source in sources for node in ast.parse(source.read_text(encoding='utf-8')).body]
    for node in nodes:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id.startswith('EXIT_') and isinstance(node.value, ast.Constant) and (type(node.value.value) is int):
            values[target.id] = node.value.value
    assert values['EXIT_WALK_HALTED'] == 17
    assert [name for name, value in values.items() if value == 17] == ['EXIT_WALK_HALTED']

def test_t28_encoder_matches_literal_golden_bytes_and_rejects_reordered_keys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    walk_record = {'record': 'walk', 'walk_id': 'walk-0001', 'schema_version': 1, 'model': 'mödel.orm.yaml', 'selected': ['validate', 'exp-run'], 'flags': {'from': None, 'until': None, 'skip': ['synth', 'codegen'], 'auto': False, 'adapter': 'claude', 'adapter_explicit': False, 'experiment': 'EXP-TEST', 'test_argv': ['-q', 'café'], 'station_timeout': {'synth': 17, 'codegen': 23}}, 'started': '2026-08-24T12:34:56Z'}
    gate_record = {'record': 'gate', 'walk_id': 'walk-0001', 'station': 'validate', 'argv': ['gnd', 'validate', 'mödel.orm.yaml'], 'authorized_by': 'stdin "gö" 2026-08-24T12:34:56Z'}
    station_record = {'record': 'station', 'walk_id': 'walk-0001', 'station': 'validate', 'exit': 0, 'evidence': 'walks/walk-0001.validate.out', 'halt': None}
    expected_walk = b'{"record":"walk","walk_id":"walk-0001","schema_version":1,"model":"m\xc3\xb6del.orm.yaml","selected":["validate","exp-run"],"flags":{"from":null,"until":null,"skip":["synth","codegen"],"auto":false,"adapter":"claude","adapter_explicit":false,"experiment":"EXP-TEST","test_argv":["-q","caf\xc3\xa9"],"station_timeout":{"synth":17,"codegen":23}},"started":"2026-08-24T12:34:56Z"}\n'
    expected_gate = b'{"record":"gate","walk_id":"walk-0001","station":"validate","argv":["gnd","validate","m\xc3\xb6del.orm.yaml"],"authorized_by":"stdin \\"g\xc3\xb6\\" 2026-08-24T12:34:56Z"}\n'
    expected_station = b'{"record":"station","walk_id":"walk-0001","station":"validate","exit":0,"evidence":"walks/walk-0001.validate.out","halt":null}\n'
    assert solve.encode_record(walk_record) == expected_walk
    assert solve.encode_record(gate_record) == expected_gate
    assert solve.encode_record(station_record) == expected_station
    assert not expected_walk.endswith(b'\n\n')
    reordered = dict(reversed(tuple(gate_record.items())))
    with pytest.raises(solve._InternalDefect):
        solve.encode_record(reordered)
    workspace, model, _ = _seed_workspace(tmp_path)
    original_encoder = solve.encode_record

    def reorder_at_encoder(record: Mapping[str, object]) -> bytes:
        return original_encoder(dict(reversed(tuple(record.items()))))
    monkeypatch.setattr(solve, 'encode_record', reorder_at_encoder)
    assert _run(model, workspace, start='validate', until='validate') == cli.EXIT_INTERNAL

def test_t29_logical_set_and_mapping_insertion_order_cannot_change_log_bytes(tmp_path: Path) -> None:
    logs: list[bytes] = []
    constructions = [(frozenset(name for name in ['synth', 'conformance']), {'exp-run': 7, 'validate': 5, 'codegen': 6}), (frozenset(name for name in ['conformance', 'synth']), {'codegen': 6, 'validate': 5, 'exp-run': 7})]
    for index, (skip, timeouts) in enumerate(constructions):
        workspace, model, experiment = _seed_workspace(tmp_path / str(index), experiment=True)
        assert _run(model, workspace, experiment=experiment, skip=skip, test_argv=('-q', 'tests/test_contract.py'), station_timeout=timeouts, spawn=FakeSpawn()) == 0
        logs.append(_walk_file(workspace).read_bytes())
    assert logs[0] == logs[1]
    assert hashlib.sha256(logs[0]).digest() == hashlib.sha256(logs[1]).digest()

def test_t30_all_skip_is_refused_and_event_pairs_cannot_interleave(tmp_path: Path) -> None:
    refused_workspace, refused_model, _ = _seed_workspace(tmp_path / 'refused')
    assert _run(refused_model, refused_workspace, skip=frozenset(LOCKED_STATIONS), gate=_fail_gate, clock=_fixed_clock, spawn=_fail_spawn) == cli.EXIT_USAGE
    assert _walk_files(refused_workspace) == []
    workspace, model, _ = _seed_workspace(tmp_path / 'ordered')
    observations: list[list[str]] = []

    def observing_gate(_station: solve.Station) -> str:
        files = _walk_files(workspace)
        assert len(files) == 1
        records = _bounded_jsonl_objects(files[0].read_bytes())
        assert records is not None
        observations.append([record['record'] for record in records])
        return 'go'
    assert _run(model, workspace, start='validate', until='synth', gate=observing_gate, clock=_fixed_clock, spawn=FakeSpawn()) == 0
    assert observations[0] == ['walk']
    assert observations[1] == ['walk', 'gate', 'station']
    assert [record['record'] for record in _read_records(workspace)] == ['walk', 'gate', 'station', 'gate', 'station']

def test_t31_harness_emits_only_authorization_modes_coherent_with_header(tmp_path: Path) -> None:
    for auto in (False, True):
        workspace, model, _ = _seed_workspace(tmp_path / str(auto))
        assert _run(model, workspace, start='validate', until='synth', auto=auto, gate=_fail_gate if auto else _allow, clock=_fixed_clock, spawn=FakeSpawn()) == 0
        records = _read_records(workspace)
        assert records[0]['flags']['auto'] is auto
        expected_source = 'auto ' if auto else 'stdin '
        assert all(record['authorized_by'].startswith(expected_source) for record in _gate_records(records))
        assert b5_failures(_walk_file(workspace).read_bytes()) == frozenset()

def test_t32_all_five_stations_have_distinct_stdout_and_stderr_captures(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    spawn = FakeSpawn()
    assert _run(model, workspace, experiment=experiment, spawn=spawn) == 0
    for name in LOCKED_STATIONS:
        stdout = workspace / 'walks' / f'walk-0001.{name}.out'
        stderr = workspace / 'walks' / f'walk-0001.{name}.err'
        expected_stdout = b'{"run_id": "run-0001"}\n' if name == 'exp-run' else f'stdout:{name}\n'.encode()
        assert stdout.read_bytes() == expected_stdout
        assert stderr.read_bytes() == f'stderr:{name}\n'.encode()
        assert stdout.read_bytes() != stderr.read_bytes()

def test_t33_keyboard_interrupt_from_injected_gate_is_a_decline(tmp_path: Path) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)

    def interrupt(_station: solve.Station) -> str:
        raise KeyboardInterrupt
    try:
        code = _run(model, workspace, start='validate', until='validate', gate=interrupt, clock=_fixed_clock, spawn=_fail_spawn)
    except KeyboardInterrupt:
        pytest.fail('run_walk propagated KeyboardInterrupt instead of recording a decline')
    assert code == cli.EXIT_WALK_HALTED
    records = _read_records(workspace)
    assert records[-1]['record'] == 'gate'
    assert records[-1]['authorized_by'] is None
    assert not _station_records(records)

def test_t34_stage_order_makes_missing_workspace_66_in_both_selections(tmp_path: Path) -> None:
    model = tmp_path / 'model.orm.yaml'
    model.write_text('object_types: []\n', encoding='utf-8')
    for name, arguments in (('default', {}), ('conformance-with-codegen-skipped', {'skip': frozenset({'codegen'})})):
        workspace = tmp_path / name / 'missing-workspace'
        assert _run(model, workspace, gate=_fail_gate, clock=_fixed_clock, spawn=_fail_spawn, **arguments) == cli.EXIT_NO_INPUT
        assert _walk_files(workspace) == []

def test_t34_outside_and_missing_experiment_is_usage_before_nonexistence(tmp_path: Path) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    outside_missing = tmp_path / 'outside' / 'missing-experiment'
    assert _run(model, workspace, experiment=outside_missing, gate=_fail_gate, clock=_fixed_clock, spawn=_fail_spawn) == cli.EXIT_USAGE
    assert _walk_files(workspace) == []

@pytest.mark.parametrize('indices', [(), (1, 2)], ids=['zero-new', 'two-new'])
def test_t35_ambiguous_exp_run_set_differences_halt_without_guessing(tmp_path: Path, indices: tuple[int, ...]) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    assert _run(model, workspace, experiment=experiment, start='exp-run', until='exp-run', spawn=FakeSpawn(exp_indices=indices)) == cli.EXIT_WALK_HALTED
    record = _station_records(_read_records(workspace))[0]
    assert record['evidence'] is None
    assert record['halt'] == 'evidence-ambiguous'

def test_t36_non_utf8_argv_is_usage_before_walk_or_spawn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    invalid_word = b'\x80'.decode('utf-8', errors='surrogateescape')

    def must_not_run(*args: object, **kwargs: object) -> int:
        raise AssertionError('run_walk reached despite invalid UTF-8')
    monkeypatch.setattr(solve, 'run_walk', must_not_run)
    assert cli.main(['solve', str(model), '--workspace', str(workspace), '--experiment', str(experiment), '--test-argv', invalid_word]) == cli.EXIT_USAGE
    assert _walk_files(workspace) == []

def test_t37_walks_symlink_is_io_refusal_without_outside_writes(tmp_path: Path) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    outside = tmp_path / 'outside'
    outside.mkdir()
    (workspace / 'walks').symlink_to(outside, target_is_directory=True)
    assert _run(model, workspace, start='validate', until='validate', spawn=_fail_spawn) == cli.EXIT_IO
    assert list(outside.iterdir()) == []

@pytest.mark.parametrize('occupant', ['file', 'symlink'])
def test_t38_existing_capture_leaf_is_never_followed_or_truncated(tmp_path: Path, occupant: str) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    walks = workspace / 'walks'
    walks.mkdir()
    capture = walks / 'walk-0001.validate.out'
    sentinel = b'must-stay-unchanged\n'
    if occupant == 'file':
        capture.write_bytes(sentinel)
        protected = capture
    else:
        protected = tmp_path / 'outside-target'
        protected.write_bytes(sentinel)
        capture.symlink_to(protected)
    assert _run(model, workspace, start='validate', until='validate', spawn=solve._spawn_station) == cli.EXIT_IO
    assert protected.read_bytes() == sentinel
    assert capture.is_symlink() if occupant == 'symlink' else capture.is_file()
    station = _station_records(_read_records(workspace))[0]
    assert station['exit'] is None
    assert station['halt'] == 'spawn-error'

def test_t39_cli_timeout_uses_ascii_digits_and_normalizes_leading_zeroes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)
    captured: dict[str, object] = {}

    def record_walk(*_args: object, **kwargs: object) -> int:
        captured.update(kwargs)
        return 0
    monkeypatch.setattr(solve, 'run_walk', record_walk)
    assert cli.main(['solve', str(model), '--workspace', str(workspace), '--station-timeout', 'validate=000001']) == 0
    assert captured['station_timeout'] == {'validate': 1}
    assert cli.main(['solve', str(model), '--workspace', str(workspace), '--station-timeout', 'validate=²']) == cli.EXIT_USAGE
    streams = capsys.readouterr()
    assert 'traceback' not in (streams.out + streams.err).lower()

def test_t40_default_gate_read_error_is_logged_and_mapped_to_io(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, model, _ = _seed_workspace(tmp_path)

    class BrokenStdin:
        buffer: BrokenStdin

        def __init__(self) -> None:
            self.buffer = self

        def read(self, _size: int) -> bytes:
            raise OSError('injected stdin refusal')
    monkeypatch.setattr(sys, 'stdin', BrokenStdin())
    assert _run(model, workspace, start='validate', until='validate', gate=solve._blocking_stdin_gate, spawn=_fail_spawn) == cli.EXIT_IO
    records = _read_records(workspace)
    assert [record['record'] for record in records] == ['walk', 'gate']
    assert records[1]['authorized_by'] is None

def test_t41_capture_close_error_becomes_spawn_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, _, _ = _seed_workspace(tmp_path)
    walks = workspace / 'walks'
    walks.mkdir()
    original_open = solve._open_capture
    opened = 0

    class CloseFailure:

        def __init__(self, handle: BinaryIO) -> None:
            self.handle = handle

        @property
        def closed(self) -> bool:
            return self.handle.closed

        def fileno(self) -> int:
            return self.handle.fileno()

        def close(self) -> None:
            self.handle.close()
            raise OSError('injected close refusal')

    def fail_first_close(request: solve.StationSpawn, path: Path, walks_fd: int) -> BinaryIO | CloseFailure:
        nonlocal opened
        handle = original_open(request, path, walks_fd)
        opened += 1
        return CloseFailure(handle) if opened == 1 else handle
    monkeypatch.setattr(solve, '_open_capture', fail_first_close)
    outcome = solve._spawn_station(solve.StationSpawn(argv=(sys.executable, '-c', 'pass'), cwd=workspace, timeout_s=5, stdout_path=walks / 'walk-0001.validate.out', stderr_path=walks / 'walk-0001.validate.err'))
    assert outcome == solve.StationOutcome(None, 'spawn-error')

def test_t43_exp_run_claim_must_identify_the_sole_new_run(tmp_path: Path) -> None:
    workspace, model, experiment = _seed_workspace(tmp_path, experiment=True)
    assert experiment is not None

    def mismatched_claim(request: solve.StationSpawn) -> solve.StationOutcome:
        request.stdout_path.write_bytes(b'{"run_id":"run-0002"}\n')
        request.stderr_path.write_bytes(b'')
        actual = experiment / 'runs' / 'run-0001'
        actual.mkdir(parents=True)
        (actual / 'result.json').write_text('{}\n', encoding='utf-8')
        return solve.StationOutcome(0, None)
    assert _run(model, workspace, experiment=experiment, start='exp-run', until='exp-run', spawn=mismatched_claim) == cli.EXIT_WALK_HALTED
    station = _station_records(_read_records(workspace))[0]
    assert station['evidence'] is None
    assert station['halt'] == 'evidence-ambiguous'
