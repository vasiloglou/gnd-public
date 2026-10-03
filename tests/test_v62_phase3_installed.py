from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.v62_phase3_corpus import FIXTURE

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.distribution

def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=180, check=False)

def test_w01_w03_installed_wheel_contract_receipt(tmp_path: Path) -> None:
    if shutil.which('uv') is None:
        pytest.skip('uv is required for installed-wheel replay')
    dist = tmp_path / 'dist'
    built = _run(['uv', 'build', '--wheel', '--out-dir', str(dist)], cwd=ROOT)
    assert built.returncode == 0, built.stdout + built.stderr
    wheels = list(dist.glob('*.whl'))
    assert len(wheels) == 1
    environment = tmp_path / 'venv'
    created = _run(['uv', 'venv', str(environment)], cwd=tmp_path)
    assert created.returncode == 0, created.stdout + created.stderr
    python = environment / 'bin/python'
    installed = _run(['uv', 'pip', 'install', '--python', str(python), f'{wheels[0]}[synth]'], cwd=tmp_path)
    assert installed.returncode == 0, installed.stdout + installed.stderr
    gnd = environment / 'bin/gnd'
    model = FIXTURE / 'models/exact-terms.orm.yaml'
    clean = FIXTURE / 'populations/term-clean.pop.yaml'
    unavailable = FIXTURE / 'populations/term-input.pop.yaml'
    validate = _run([str(gnd), 'validate', str(model), '--format', 'json'], cwd=tmp_path)
    clean_check = _run([str(gnd), 'check', str(model), str(clean), '--format', 'json'], cwd=tmp_path)
    unavailable_check = _run([str(gnd), 'check', str(model), str(unavailable), '--format', 'json'], cwd=tmp_path)
    assert (validate.returncode, clean_check.returncode, unavailable_check.returncode) == (0, 0, 4)
    unavailable_payload = json.loads(unavailable_check.stdout)
    assert {row['reason_code'] for row in unavailable_payload['derivations']} == {'term:mod-zero'}
    walk_probe = '\nimport sys\nfrom gnd.model import load_model\nfrom gnd.population import load_population\nfrom gnd.transition import band, evaluate_plan, read_steps_document, validate_steps\nmodel = load_model(sys.argv[1])\npopulation = load_population(sys.argv[2], model=model)\nsteps = validate_steps(read_steps_document(sys.argv[3]), model)\nraise SystemExit(band(evaluate_plan(model, population, steps).report))\n'
    walk = _run([str(python), '-c', walk_probe, str(model), str(unavailable), str(FIXTURE / 'walks/approve.steps.json')], cwd=tmp_path)
    assert walk.returncode == 4, walk.stdout + walk.stderr
    synth = _run([str(gnd), 'synth', str(model), '--class', 'conforming', '--seed', '7', '--out', str(tmp_path / 'synth'), '--format', 'json'], cwd=tmp_path)
    assert synth.returncode == 5, synth.stdout + synth.stderr
    synth_payload = json.loads(synth.stdout)
    assert synth_payload['exit_code'] == 5
    assert 'generator invariant failed' in synth_payload['error']
    yaml = YAML(typ='safe')
    measurable_document = yaml.load(model.read_text(encoding='utf-8'))
    measurable_document['constraints'] = []
    measurable_document['operations'] = []
    measurable_model = tmp_path / 'installed-measurable.orm.yaml'
    with measurable_model.open('w', encoding='utf-8') as stream:
        YAML().dump(measurable_document, stream)
    corpus = tmp_path / 'installed-corpus'
    supported_synth = _run([str(gnd), 'synth', str(measurable_model), '--class', 'conforming', '--seed', '7', '--out', str(corpus), '--format', 'json'], cwd=tmp_path)
    assert supported_synth.returncode == 0, supported_synth.stdout + supported_synth.stderr
    measurement = _run([str(gnd), 'measure', str(measurable_model), '--populations', str(corpus), '--format', 'json'], cwd=tmp_path)
    assert measurement.returncode == 0, measurement.stdout + measurement.stderr
    unmutated = json.loads(measurement.stdout)['coverage_summary']['unmutated_derivations']
    assert {row['derivation_ref'] for row in unmutated} == {'derivation:doubled_residue', 'derivation:permitted', 'derivation:residue'}
    assert {row['reason'] for row in unmutated} == {'structured-derivation-mutation-unsupported'}
