"""PA5R: checking a supplied (agent) proposal with PyRel, and the human summary."""
import hashlib
import inspect
import json
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'


@pytest.mark.parametrize('result', [{}, {'policy': 'x'}, {'policy': {'verdicts': [1, None, {'status': 'violated'}]}},
                                    {'policy': {'verdicts': [{'status': 'warning', 'id': 'r', 'witnesses': 'w'}]}},
                                    {'calculation': {'selected_pairs': [{'user': 1}]}, 'exit_code': 'zero'},
                                    {'calculation': {'report': {'submitted': 'x'}}, 'accepted': True},
                                    {'application_refusal': 7, 'reason': None}, [], None, 'text'])
def test_format_result_is_total(result):
    from gnd.export.applications import format_result

    lines = format_result(result)
    assert isinstance(lines, list) and all(isinstance(line, str) for line in lines)
    assert any(line.startswith('Policy check:') for line in lines)


def test_format_result_reports_rejection_witness_and_no_publication():
    from gnd.export.applications import format_result

    result = {'exit_code': 1, 'accepted': False, 'published': False, 'calculation': None,
              'proposal': [{'user': 'ada', 'book': 'night'}],
              'policy': {'status': 'rejected', 'verdicts': [
                  {'id': 'age_appropriate', 'status': 'violated', 'witnesses': [{'$u': 'ada', '$b': 'night'}]},
                  {'id': 'unread_only', 'status': 'satisfied', 'witnesses': []}]}}
    assert format_result(result) == [
        "Checking the agent's proposal: ada/night",
        'Policy check: REJECTED',
        '  violated    age_appropriate {"$u": "ada", "$b": "night"}',
        'Nothing was published.']


def test_format_result_accepted_report_and_warning():
    from gnd.export.applications import format_result

    report = {'exit_code': 0, 'accepted': True, 'published': False,
              'report': {'submitted': 3, 'approved': 1, 'total_eur': 2260},
              'policy': {'status': 'accepted', 'verdicts': []}}
    assert format_result(report) == ['Report: 3 submitted, 1 approved, 2260 EUR total', 'Policy check: ACCEPTED']
    warned = {'exit_code': 0, 'accepted': True, 'published': True, 'output': 'advisory.json',
              'calculation': {'selected_pairs': [{'user': 'ada', 'book': 'cosmos'}, {'user': 'ada', 'book': 'map'}]},
              'policy': {'status': 'accepted_with_warnings', 'verdicts': [
                  {'id': 'preferred_genre', 'status': 'warning', 'witnesses': [{'$u': 'ada', '$b': 'cosmos', '$g': 'science'}]}]}}
    assert format_result(warned) == [
        'Proposed for ada: cosmos, map', 'Policy check: ACCEPTED with 1 warning',
        '  warning     preferred_genre {"$u": "ada", "$b": "cosmos", "$g": "science"}',
        'Published: advisory.json']


def test_check_proposal_validation_order_is_pinned():
    from gnd.export import applications

    source = inspect.getsource(applications.check_proposal)
    order = ['output already exists', 'explicit native interpreter', '_capture(proposal_path',
             '_preserve_source(', '_check_and_publish(']
    positions = [source.index(marker) for marker in order]
    assert positions == sorted(positions)


def _bookrec(tmp_path):
    home = tmp_path / 'bookrec'
    shutil.copytree(str(files('gnd').joinpath('examples', 'bookrec')), home)
    return home


@pytest.mark.pyrel_oracle
def test_agent_proposal_is_rejected_by_pyrel_checker(tmp_path):
    from gnd.export.applications import check_proposal

    home = _bookrec(tmp_path)
    proposal = home / 'adult-for-minor.population.json'
    output = tmp_path / 'published.json'
    before = (home / 'seed.population.json').read_bytes()
    result = check_proposal(home / 'model.orm.yaml', home / 'seed.population.json', proposal, output,
                            native_python=NATIVE, owned_relations=('recommendation',))
    assert result['exit_code'] == 1 and not result['accepted'] and not output.exists()
    rule = next(v for v in result['policy']['verdicts'] if v['id'] == 'age_appropriate')
    assert rule['status'] == 'violated' and {'$u': 'ada', '$b': 'night'} in rule['witnesses']
    assert result['calculation'] is None
    assert result['source_binding']['proposal_sha256'] == hashlib.sha256(proposal.read_bytes()).hexdigest()
    assert (home / 'seed.population.json').read_bytes() == before


@pytest.mark.pyrel_oracle
def test_accepted_proposal_publishes_exact_checked_bytes(tmp_path):
    from gnd.export.applications import check_proposal

    home = _bookrec(tmp_path)
    proposal = home / 'tutorial-assets/checkpoints/preferred.candidate.json'
    output = tmp_path / 'published.json'
    result = check_proposal(home / 'strict.orm.yaml', home / 'seed.population.json', proposal, output,
                            native_python=NATIVE, owned_relations=('recommendation',))
    assert result['exit_code'] == 0 and result['accepted'] and result['published'], result
    assert json.loads(output.read_text()) == json.loads(proposal.read_text())


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('fault', ['exists', 'inventory', 'asserted'])
def test_proposal_refusals_happen_before_checking(tmp_path, fault):
    from gnd.export.applications import check_proposal

    home = _bookrec(tmp_path)
    proposal = tmp_path / 'proposal.json'
    document = json.loads((home / 'adult-for-minor.population.json').read_text())
    if fault == 'inventory':
        document['facts']['unexpected'] = []
    if fault == 'asserted':
        document['facts']['user_is_minor'] = []
    proposal.write_text(json.dumps(document))
    output = tmp_path / 'published.json'
    if fault == 'exists':
        output.write_text('keep')
    result = check_proposal(home / 'model.orm.yaml', home / 'seed.population.json', proposal, output,
                            native_python=NATIVE, owned_relations=('recommendation',))
    assert result['policy'] is None and not result['published']
    assert result['exit_code'] == (2 if fault == 'exists' else 3), result
    assert (output.read_text() == 'keep') if fault == 'exists' else not output.exists()


@pytest.mark.pyrel_oracle
def test_bookrec_cli_proposal_text_output(tmp_path):
    home = _bookrec(tmp_path)
    run = subprocess.run([sys.executable, '-m', 'bookrec.cli', 'check', '--model', '../model.orm.yaml',
                          '--input', '../seed.population.json', '--proposal', '../adult-for-minor.population.json',
                          '--output', '../agent.json', '--backend', 'pyrel', '--pyrel-python', str(NATIVE),
                          '--format', 'text'], cwd=home / 'extension', capture_output=True, text=True,
                         timeout=150, check=False)
    assert run.returncode == 1, run.stderr + run.stdout
    assert run.stdout.splitlines() == [
        "Checking the agent's proposal: ada/night, ben/night",
        'Policy check: REJECTED',
        '  violated    age_appropriate {"$b": "night", "$u": "ada"}',
        'Nothing was published.']
    assert not (home / 'agent.json').exists()


# Review repairs (notes/phase-PA5R-claude-review.md): each proven red before its fix.
@pytest.mark.parametrize('result', [{'calculation': {'selected_pairs': 5}}, {'policy': {'verdicts': 5}},
                                    {'policy': {'verdicts': [{'status': []}]}},
                                    {'proposal': 5}, {'proposal': {'r': 5}}])
def test_format_result_total_over_review_shapes(result):
    from gnd.export.applications import format_result

    assert all(isinstance(line, str) for line in format_result(result))


def test_format_result_reason_is_one_line():
    from gnd.export.applications import format_result

    lines = format_result({'reason': 'ProfileRefusal: coverage-not-declared\n\n'})
    assert lines[0] == 'Policy check: NOT RUN (ProfileRefusal: coverage-not-declared)'
    assert all('\n' not in line for line in lines)


def test_gnd_backend_refuses_proposal(tmp_path):
    home = _bookrec(tmp_path)
    proposal = json.loads((home / 'adult-for-minor.population.json').read_text())
    proposal['facts']['user_is_minor'] = []      # erase the fact that would refuse ada/night
    (tmp_path / 'forged.json').write_text(json.dumps(proposal))
    run = subprocess.run([sys.executable, '-m', 'bookrec.cli', 'check', '--model', '../model.orm.yaml',
                          '--input', '../seed.population.json', '--proposal', str(tmp_path / 'forged.json'),
                          '--output', str(tmp_path / 'out.json')], cwd=home / 'extension',
                         capture_output=True, text=True, timeout=120, check=False)
    # --proposal exists only to check with PyRel; the unchecked gnd path is refused outright.
    assert run.returncode == 2 and '--proposal requires --backend pyrel' in run.stderr, run.stdout + run.stderr
    assert not (tmp_path / 'out.json').exists()


def test_checker_stage_caps_candidate_bytes():
    from gnd.export import applications

    assert 'candidate exceeds native byte cap' in inspect.getsource(applications._check_and_publish)


@pytest.mark.pyrel_oracle
def test_owned_relation_absent_from_input_and_proposal_is_not_a_crash(tmp_path):
    from gnd.export.applications import check_proposal

    home = _bookrec(tmp_path)
    for name in ('seed.population.json', 'adult-for-minor.population.json'):
        document = json.loads((home / name).read_text())
        del document['facts']['recommendation']
        (tmp_path / name).write_text(json.dumps(document))
    result = check_proposal(home / 'model.orm.yaml', tmp_path / 'seed.population.json',
                            tmp_path / 'adult-for-minor.population.json', tmp_path / 'out.json',
                            native_python=NATIVE, owned_relations=('recommendation',))
    assert result['exit_code'] != 70 and 'KeyError' not in str(result.get('reason')), result
    assert not (tmp_path / 'out.json').exists() or result['accepted']
