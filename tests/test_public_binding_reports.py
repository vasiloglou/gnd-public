from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from gnd import coverage as coverage_module
from gnd import report as report_module
from gnd.cli import main
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "tests/fixtures/public-binding-reports"
REPORTS = CORPUS / "reports"
EXPECTED = json.loads((CORPUS / "answers.json").read_text(encoding="utf-8"))
REPORT_CASE_IDS = [case["case_id"] for case in EXPECTED["report_cases"]]


def _run_cli(argv: list[str], *, cwd: Path | None=None) -> tuple[int, str, str]:
    """Invoke the CLI in process and return (exit, stdout, stderr)."""
    out, err = (io.StringIO(), io.StringIO())
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            if cwd is None:
                code = main(argv)
            else:
                with contextlib.chdir(cwd):
                    code = main(argv)
    except SystemExit as error:
        code = int(error.code or 0)
    return (int(code), out.getvalue(), err.getvalue())


def _run_subprocess(argv: list[str], *, cwd: Path, environment: dict[str, str] | None=None) -> subprocess.CompletedProcess[bytes]:
    if environment is None:
        environment = dict(os.environ)
        environment['PYTHONPATH'] = str(REPO_ROOT / 'src')
    return subprocess.run([sys.executable, '-m', 'gnd', *argv], cwd=cwd, capture_output=True, check=False, env=environment)


def _corpus_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _coverage_argv(case: dict[str, Any], output_format: str) -> list[str]:
    model = _corpus_relative(CORPUS / case['model'])
    argv = ['coverage', model]
    sources = [_corpus_relative(CORPUS / source) for source in case['sources']]
    if case['flag'] == '--check-and-verify':
        argv.extend(['--check', sources[0], '--verify', sources[1]])
    else:
        for source in sources:
            argv.extend([case['flag'], source])
    argv.extend(['--format', output_format])
    return argv


def _run_coverage(case: dict[str, Any], output_format: str='json') -> tuple[int, str]:
    code, stdout, _stderr = _run_cli(_coverage_argv(case, output_format))
    return (code, stdout)


def _report_case(case_id: str) -> dict[str, Any]:
    for case in EXPECTED['report_cases']:
        if case['case_id'] == case_id:
            return case
    raise KeyError(case_id)


def _assert_message(stdout: str, answer: dict[str, Any]) -> None:
    for token in answer.get('message_contains', ()):
        assert token in stdout, f'expected {token!r} in {stdout!r}'
    for token in answer.get('message_excludes', ()):
        assert token not in stdout, f'did not expect {token!r} in {stdout!r}'


def _evidence_rows(payload: dict[str, Any]) -> int:
    return sum(len(element.get('evidence', [])) for element in payload['elements'])


@pytest.mark.parametrize('case_id', REPORT_CASE_IDS)
def test_every_report_case_reaches_its_approved_outcome(case_id: str) -> None:
    """INTENDED RED for every current-report and disclosure case."""
    case = _report_case(case_id)
    answer = case['post_phase']
    code, stdout = _run_coverage(case, 'json')
    assert code == answer['exit'], stdout
    _assert_message(stdout, answer)
    if code != 0:
        return
    payload = json.loads(stdout)
    assert payload['schema_version'] == answer['output_schema_version']
    assert len(payload['elements']) == answer['element_count']
    assert _evidence_rows(payload) == answer['evidence_rows']
    assert payload['sources']['unbound'] == answer['unbound']


@pytest.mark.parametrize('case_id', [case['case_id'] for case in EXPECTED['report_cases'] if case['post_phase'].get('unbound')])
def test_the_text_rendering_discloses_the_same_sorted_gap_rows(case_id: str) -> None:
    """INTENDED RED. A machine consumer and a reader must see the same gaps."""
    case = _report_case(case_id)
    code, rendered = _run_coverage(case, 'text')
    assert code == 0, rendered
    for row in case['post_phase']['unbound']:
        assert row['path'] in rendered
        assert row['reason'] in rendered
    order = [rendered.index(row['path']) for row in case['post_phase']['unbound']]
    assert order == sorted(order)


def test_the_report_module_publishes_the_paired_model_bound_constants() -> None:
    """INTENDED RED. Versions 3 and 4 stay frozen; 5 and 6 are added beside them."""
    constants = EXPECTED['report_wire']['constants']
    for name, value in constants.items():
        assert getattr(report_module, name, None) == value, name
    assert set(EXPECTED['report_wire']['accepted_versions']) == set(constants.values())


def test_the_model_bound_selector_exists_and_picks_by_derivation_class() -> None:
    """INTENDED RED. A check/verify-specific selector, so the two unmigrated
    commands keep their frozen report versions."""
    selector_answer = EXPECTED['report_wire']['selector']
    selector = getattr(report_module, selector_answer['function'], None)
    assert callable(selector)
    assert selector(load_model(REPORTS / 'models' / 'nonstructured.orm.yaml')) == selector_answer['nonstructured']
    assert selector(load_model(REPORTS / 'models' / 'structured.orm.yaml')) == selector_answer['structured']
    legacy = getattr(report_module, EXPECTED['report_wire']['legacy_selector']['function'])
    assert legacy(load_model(REPORTS / 'models' / 'nonstructured.orm.yaml')) == 3
    assert legacy(load_model(REPORTS / 'models' / 'structured.orm.yaml')) == 4


def test_the_report_schema_carries_four_closed_arms() -> None:
    """INTENDED RED. One arm per version, each closed over model_digest and
    derivations exactly as the approved table says."""
    schema = report_module.load_report_schema()
    assert EXPECTED['report_wire']['model_digest_pattern'] in json.dumps(schema)
    digest_key = EXPECTED['report_wire']['model_digest_key']
    from jsonschema import Draft202012Validator
    validator = Draft202012Validator(schema)
    for name, valid in (('legacy-v3.json', True), ('legacy-v4.json', True), ('current-v5-valid.json', True), ('current-v6-valid.json', True), ('current-v5-missing-digest.json', False), ('current-v5-malformed-digest.json', False)):
        document = json.loads((REPORTS / name).read_text(encoding='utf-8'))
        errors = list(validator.iter_errors(document))
        assert (errors == []) is valid, f'{name}: {[error.message for error in errors]}'
    frozen = json.loads((REPORTS / 'legacy-v3.json').read_text(encoding='utf-8'))
    frozen[digest_key] = EXPECTED['report_wire']['model_digests']['nonstructured']
    assert list(validator.iter_errors(frozen)) != [], 'version 3 must forbid model_digest'


def _scratch_report_workspace(tmp_path: Path) -> Path:
    """Materialize the corpus models and populations outside the tracked tree."""
    documents = json.loads((REPORTS / 'populations' / 'documents.json').read_text(encoding='utf-8'))['documents']
    root = tmp_path / 'reports'
    root.mkdir()
    for name in ('nonstructured', 'structured'):
        shutil.copy(REPORTS / 'models' / f'{name}.orm.yaml', root / f'{name}.orm.yaml')
    for name, document in documents.items():
        (root / name).write_text(json.dumps(document, indent=2, sort_keys=True) + '\n', 'utf-8')
    return root


def test_the_model_digest_is_emitted_immediately_after_the_model_key(tmp_path: Path) -> None:
    """INTENDED RED. Placement is part of the approved wire, and it is what makes
    the rebaseline's byte delta exactly two keys wide."""
    root = _scratch_report_workspace(tmp_path)
    done = _run_subprocess(['check', 'nonstructured.orm.yaml', 'nonstructured.population.json', '--format', 'json'], cwd=root)
    assert done.returncode == 0, done.stderr
    keys = list(json.loads(done.stdout).keys())
    digest_key = EXPECTED['report_wire']['model_digest_key']
    anchor = EXPECTED['report_wire']['model_digest_emitted_after']
    assert digest_key in keys
    assert keys.index(digest_key) == keys.index(anchor) + 1


@pytest.mark.parametrize(('command', 'model', 'population', 'expected_key'), [('check', 'nonstructured', 'nonstructured.population.json', 'nonstructured'), ('check', 'structured', 'structured.population.json', 'structured'), ('verify', 'nonstructured', 'nonstructured.population.json', 'nonstructured'), ('verify', 'structured', 'structured.population.json', 'structured')])
def test_check_and_verify_bind_every_post_load_payload_to_the_census_model(tmp_path: Path, command: str, model: str, population: str, expected_key: str) -> None:
    """INTENDED RED. Success and post-load failure alike carry one digest."""
    root = _scratch_report_workspace(tmp_path)
    selector = EXPECTED['report_wire']['selector']
    expected_version = selector['structured' if expected_key == 'structured' else 'nonstructured']
    expected_digest = EXPECTED['report_wire']['model_digests'][expected_key]
    digest_key = EXPECTED['report_wire']['model_digest_key']
    argv = [command, f'{model}.orm.yaml', population]
    if command == 'verify':
        argv.append('--no-extraction')
    done = _run_subprocess([*argv, '--format', 'json'], cwd=root)
    payload = json.loads(done.stdout)
    assert payload['schema_version'] == 7
    projected = report_module.legacy_report_projection(payload, expected_version)
    assert projected['schema_version'] == expected_version
    assert projected[digest_key] == expected_digest
    broken = json.loads((root / population).read_text(encoding='utf-8'))
    broken['facts']['item_has_tag'] = [{'item': 1, 'tag': 'alpha'}, {'item': 1, 'tag': 'beta'}]
    (root / 'broken.population.json').write_text(json.dumps(broken, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    argv = [command, f'{model}.orm.yaml', 'broken.population.json']
    if command == 'verify':
        argv.append('--no-extraction')
    failed = _run_subprocess([*argv, '--format', 'json'], cwd=root)
    failed_payload = json.loads(failed.stdout)
    assert failed.returncode != 0
    assert failed_payload['schema_version'] == 7
    failed_projected = report_module.legacy_report_projection(failed_payload, expected_version)
    assert failed_projected['schema_version'] == expected_version
    assert failed_projected[digest_key] == expected_digest


def test_a_model_load_failure_stays_on_the_frozen_version_without_a_digest(tmp_path: Path) -> None:
    """CONTROL. Before a model loads there is no model identity to claim, so the
    payload must stay on version 3 and carry no digest -- at both gates."""
    root = tmp_path / 'before-load'
    root.mkdir()
    (root / 'broken.orm.yaml').write_text('version: 1\nmodel_id: [\n', encoding='utf-8')
    (root / 'any.population.json').write_text('{"population": {}, "facts": {}}\n', 'utf-8')
    done = _run_subprocess(['check', 'broken.orm.yaml', 'any.population.json', '--format', 'json'], cwd=root)
    payload = json.loads(done.stdout)
    assert done.returncode == 3
    assert payload['schema_version'] == 7
    projected = report_module.legacy_report_projection(payload, EXPECTED['report_wire']['pre_model_load_version'])
    assert projected['schema_version'] == EXPECTED['report_wire']['pre_model_load_version']
    assert EXPECTED['report_wire']['model_digest_key'] not in projected


def test_the_experiment_session_consumer_selects_the_model_bound_versions() -> None:
    """INTENDED RED. The session verifier runs check/verify, so its expected
    versions move with them -- and only with them."""
    from gnd.exp import session as session_module
    answer = EXPECTED['report_wire']['session_consumer']
    source = Path(session_module.__file__).read_text(encoding='utf-8')
    assert answer['function'] in source
    selector_answer = EXPECTED['report_wire']['selector']
    current_selector = report_module.current_payload_schema_version.__name__
    assert current_selector in source
    for model_name, legacy_version in (('nonstructured', selector_answer['nonstructured']), ('structured', selector_answer['structured'])):
        selected = report_module.current_payload_schema_version(load_model(REPORTS / 'models' / f'{model_name}.orm.yaml'))
        assert selected == 7
        assert selected.legacy_version == legacy_version


def test_the_coverage_reader_returns_a_binding_classification() -> None:
    """INTENDED RED. One walk owns legacy-versus-bound; the indexer does not
    reimplement version logic."""
    source = Path(coverage_module.__file__).read_text(encoding='utf-8')
    assert 'SourceBindingGap' in source
    assert EXPECTED['coverage']['legacy_gap_reason'] in source
    assert EXPECTED['coverage']['mismatch_rule_name'] in source
    for value in EXPECTED['coverage']['binding_values']:
        assert value in source
    assert 'unbound_sources' in source


def test_the_coverage_output_always_carries_the_unbound_key() -> None:
    """INTENDED RED. Present and possibly empty -- never optional (r2 R2)."""
    case = _report_case('current-v5-valid')
    code, stdout = _run_coverage(case, 'json')
    assert code == 0, stdout
    payload = json.loads(stdout)
    node: Any = payload
    for step in EXPECTED['coverage']['unbound_key_path']:
        assert step in node
        node = node[step]
    assert node == []
    assert payload['schema_version'] == EXPECTED['coverage']['output_versions']['current_without_derivation_class']


def test_every_disclosed_gap_row_has_the_declared_shape_and_order() -> None:
    """INTENDED RED. The row is a closed record, sorted by kind then path."""
    case = _report_case('legacy-both-arms')
    code, stdout = _run_coverage(case, 'json')
    assert code == 0, stdout
    rows = json.loads(stdout)['sources']['unbound']
    assert rows == case['post_phase']['unbound']
    for row in rows:
        assert sorted(row) == EXPECTED['coverage']['gap_row_keys']
        assert row['reason'] == EXPECTED['coverage']['legacy_gap_reason']
    order_keys = EXPECTED['coverage']['gap_row_order']
    assert rows == sorted(rows, key=lambda row: tuple(row[key] for key in order_keys))


def test_the_indexed_evidence_of_a_legacy_source_never_moves() -> None:
    """CONTROL. Disclosure adds a row; it must not touch a single element quote."""
    case = _report_case('legacy-v3-check')
    code, stdout = _run_coverage(case, 'json')
    assert code == 0, stdout
    payload = json.loads(stdout)
    answer = EXPECTED['census_models']['nonstructured']
    assert [element['address'] for element in payload['elements']] == answer['elements']
    quotes = {element['address']: element.get('evidence', []) for element in payload['elements']}
    assert sum(len(rows) for rows in quotes.values()) == case['pre_phase']['evidence_rows']
    assert all(rows for rows in quotes.values()), 'every element must keep its quote'
    structured = _report_case('legacy-v4-check')
    code, stdout = _run_coverage(structured, 'json')
    assert code == 0, stdout
    assert [element['address'] for element in json.loads(stdout)['elements']] == EXPECTED['census_models']['structured']['elements']


def test_a_digest_bearing_report_under_the_wrong_flag_fails_on_kind_first() -> None:
    """P3R-5: a genuine two-fault order control -- this source COULD name the mismatch."""
    code, stdout = _run_coverage(_report_case('current-v5-wrong-model') | {'flag': '--verify'})
    assert code == 3, stdout
    assert 'is not verify snapshot evidence as its flag declared' in stdout
    assert 'coverage:model-digest-mismatch' not in stdout
