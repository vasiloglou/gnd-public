from __future__ import annotations

import argparse
import ast
import inspect
import json
import shutil
from pathlib import Path

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd import cli, coverage
from gnd.cli import main
from gnd.exits import EXIT_IO, EXIT_NO_INPUT, EXIT_USAGE

FIXTURES = Path(__file__).parent / 'fixtures' / 'coverage'

def _run(arguments: list[str], *, cwd: Path | None=None) -> tuple[int, str, str]:
    result = run_main(arguments, cwd=cwd)
    return (result.returncode, result.stdout.decode('utf-8', errors='surrogatepass'), result.stderr.decode('utf-8', errors='surrogatepass'))

def test_experiment_scan_selects_experiments_from_a_mixed_root(tmp_path: Path) -> None:
    root = tmp_path / 'mixed-root'
    root.mkdir()
    shutil.copytree(FIXTURES / 'mixed/experiments/EXP-501-corroborated', root / 'EXP-501-corroborated')
    (root / 'SPEC.md').write_text('unrelated example spec\n', encoding='utf-8')
    (root / 'evidence').mkdir()
    (root / 'evidence/check.json').write_text('{}\n', encoding='utf-8')
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    code, stdout, stderr = _run(['coverage', str(model), '--experiments', str(root), '--format', 'json'])
    assert code == 0, (stdout, stderr)
    payload = json.loads(stdout)
    claims = [claim for element in payload['elements'] for claim in element['claims']]
    assert {claim['experiment'] for claim in claims} == {'EXP-501-corroborated'}

def test_experiment_scan_refuses_a_malformed_selected_directory(tmp_path: Path) -> None:
    root = tmp_path / 'mixed-root'
    root.mkdir()
    (root / 'evidence').mkdir()
    (root / 'EXP-999-missing-spec').mkdir()
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    code, stdout, stderr = _run(['coverage', str(model), '--experiments', str(root), '--format', 'json'])
    assert code == 3, (stdout, stderr)
    assert 'required experiment document' in stdout
    assert 'EXP-999-missing-spec/SPEC.md is missing' in stdout

class _ParserCaptured(Exception):
    pass

def _capture_parser(monkeypatch: pytest.MonkeyPatch) -> argparse.ArgumentParser:
    captured: list[argparse.ArgumentParser] = []

    def capture(parser: argparse.ArgumentParser, _args=None, _namespace=None):
        captured.append(parser)
        raise _ParserCaptured
    monkeypatch.setattr(cli._BandSafeParser, 'parse_args', capture)
    with pytest.raises(_ParserCaptured):
        main([])
    return captured[0]

def _coverage_input_violations(parser: argparse.ArgumentParser) -> list[str]:
    subparser_action = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    assert list(subparser_action.choices).count('coverage') == 1
    violations: list[str] = []
    for name, subparser in subparser_action.choices.items():
        if name == 'coverage':
            continue
        for action in subparser._actions:
            help_text = str(action.help or '').lower()
            if str(action.dest).startswith('coverage') or any(phrase in help_text for phrase in ('coverage output', 'coverage payload', 'coverage report')):
                violations.append(f'{name}:{action.dest}')
    return violations

def _assert_no_coverage_inputs(parser: argparse.ArgumentParser) -> None:
    assert _coverage_input_violations(parser) == []

def test_only_the_coverage_subparser_can_name_the_coverage_output(monkeypatch: pytest.MonkeyPatch) -> None:
    parser = _capture_parser(monkeypatch)
    _assert_no_coverage_inputs(parser)
    subparser_action = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    subparser_action.choices['check'].add_argument('--coverage', help='read a coverage output')
    with pytest.raises(AssertionError):
        _assert_no_coverage_inputs(parser)
    for path in (REPO_ROOT / 'src/gnd').rglob('*.py'):
        if path.name in {'coverage.py', 'cli.py'}:
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'))
        assert not any(isinstance(node, ast.Constant) and node.value == 'coverage.schema.json' for node in ast.walk(tree)), f'{path} loads the coverage output contract'

def test_v1_model_computes_without_operations_or_failure_vocabulary() -> None:
    tree = FIXTURES / 'positional'
    answer = json.loads((tree / 'expected.json').read_text())
    code, stdout, stderr = _run(['coverage', *answer['arguments'], '--format', 'json'], cwd=tree)
    assert code == 0, stderr
    payload = json.loads(stdout)
    assert payload['census']['operation']['in_model'] == 0
    assert all(element['addressing'] == 'positional' for element in payload['elements'] if element['class'] == 'constraint')
    assert not {'failed', 'failure', 'passed'} & set(_all_keys(payload))

def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)

def test_missing_named_source_is_66_and_existence_precedes_the_guard(tmp_path: Path) -> None:
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    missing = tmp_path / 'missing.json'
    code, stdout, _ = _run(['coverage', str(model), '--check', str(missing), '--format', 'json'])
    assert code == EXIT_NO_INPUT
    assert 'MISSING' in stdout
    source = inspect.getsource(coverage.guard_named_source)
    assert source.index('path.stat()') < source.index('_refuse_symlink_components(path)')

def test_model_validation_finishes_before_any_source_is_touched(tmp_path: Path) -> None:
    model = tmp_path / 'broken.orm.yaml'
    model.write_text('not: a model\n', encoding='utf-8')
    missing = tmp_path / 'also-missing.json'
    code, stdout, _ = _run(['coverage', str(model), '--check', str(missing)])
    assert code == 3
    assert 'also-missing' not in stdout

def test_symlinked_source_and_escaping_experiment_child_are_74(tmp_path: Path) -> None:
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    real = FIXTURES / 'mixed/evidence/check.json'
    linked = tmp_path / 'check.json'
    linked.symlink_to(real)
    assert _run(['coverage', str(model), '--check', str(linked)])[0] == EXIT_IO
    experiments = tmp_path / 'experiments'
    experiments.mkdir()
    outside = tmp_path / 'outside'
    shutil.copytree(FIXTURES / 'mixed/experiments/EXP-501-corroborated', outside)
    (experiments / 'EXP-501-corroborated').symlink_to(outside, target_is_directory=True)
    assert _run(['coverage', str(model), '--experiments', str(experiments)])[0] == EXIT_IO

def test_over_cap_source_is_3_without_reading_it(tmp_path: Path) -> None:
    source = tmp_path / 'large.json'
    with source.open('wb') as handle:
        handle.truncate(coverage.MAX_EVIDENCE_BYTES + 1)
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    code, stdout, _ = _run(['coverage', str(model), '--check', str(source)])
    assert code == 3
    assert 'over the' in stdout

@pytest.mark.parametrize('raw', (b'9' * 10000, ('[' * 2000 + '0' + ']' * 2000).encode(), b'{"schema_version":3,"value":NaN}', b'[]', b'', b'\xff'), ids=('long-integer', 'deep-nesting', 'nan', 'array', 'empty', 'non-utf8'))
def test_hostile_json_exits_3_without_a_traceback(tmp_path: Path, raw: bytes) -> None:
    source = tmp_path / 'hostile.json'
    source.write_bytes(raw)
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    code, stdout, stderr = _run(['coverage', str(model), '--check', str(source)])
    assert code == 3
    assert 'Traceback' not in stdout + stderr

def test_inconsistent_transition_exits_3_without_a_traceback(tmp_path: Path) -> None:
    document = json.loads((FIXTURES / 'refused/evidence/transition-refused.json').read_text(encoding='utf-8'))
    document['transition']['evaluated'] = True
    source = tmp_path / 'inconsistent-transition.json'
    source.write_text(json.dumps(document), encoding='utf-8')
    model = FIXTURES / 'refused/v2_worked_example.orm.yaml'
    code, stdout, stderr = _run(['coverage', str(model), '--transition', str(source), '--format', 'json'])
    assert code == 3
    assert 'evaluated true requires' in stdout
    assert 'Traceback' not in stdout + stderr

def test_hostile_experiment_yaml_exits_3_without_a_traceback(tmp_path: Path) -> None:
    experiment = tmp_path / 'experiments' / 'EXP-999-hostile'
    experiment.mkdir(parents=True)
    (experiment / 'SPEC.md').write_text(f"---\nid: EXP-999-hostile\nkind: analysis\ntitle: Hostile integer\nquestions:\n  - id: Q1\n    text: Does malformed YAML fail closed?\nfollows: []\ncovers: []\nbomb: {'9' * 10000}\n---\n\n# Hostile\n", encoding='utf-8')
    model = FIXTURES / 'refused/v2_worked_example.orm.yaml'
    code, stdout, stderr = _run(['coverage', str(model), '--experiments', str(experiment.parent), '--format', 'json'])
    assert code == 3
    assert 'unparseable frontmatter' in stdout
    assert 'Traceback' not in stdout + stderr

@pytest.mark.parametrize(('flag', 'source'), (('--check', 'mixed/evidence/conformance.json'), ('--conformance', 'mixed/evidence/check.json')))
def test_payload_shape_must_match_its_flag(flag: str, source: str) -> None:
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    assert _run(['coverage', str(model), flag, str(FIXTURES / source)])[0] == 3

@pytest.mark.parametrize('flag', ('--gate', '--out', '--output'))
def test_coverage_has_no_gate_or_output_path(flag: str) -> None:
    model = FIXTURES / 'mixed/v2_operations.orm.yaml'
    code, _, _ = _run(['coverage', str(model), flag, 'x'])
    assert code == EXIT_USAGE

def test_coverage_modules_allocate_no_exit_band() -> None:
    for filename in ('coverage.py', 'address.py'):
        tree = ast.parse((REPO_ROOT / 'src/gnd' / filename).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = [target.id for target in targets if isinstance(target, ast.Name)]
                value = node.value
                assert not (any('EXIT' in name or 'BAND' in name for name in names) and isinstance(value, ast.Constant) and isinstance(value.value, int))
