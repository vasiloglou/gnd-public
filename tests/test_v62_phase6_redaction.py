from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

from support.v62_phase6_corpus import assert_answer, document, population_document, write_case

from gnd import transition
from gnd.api import check
from gnd.cli import main
from gnd.model import load_model
from gnd.redaction import RedactionPolicy, project_output


def test_exists_where_taint_does_not_leak(tmp_path):
    population = population_document()
    population['facts']['radio_sample'] = [row for row in population['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    population['facts']['neighbor_cell'][1]['pci'] = 987654321
    population['facts']['neighbor_cell'][1]['modulus'] = 0
    model_path, population_path = write_case(tmp_path, population_doc=population)
    payload = check(model_path, population_path)
    encoded = json.dumps(payload, sort_keys=True)
    assert 'SECRET-EXISTS-271828' not in encoded
    assert 'TOKEN-ALPHA-2' not in encoded and 'TOKEN-ALPHA-3' not in encoded
    assert '987654321' not in encoded
    assert 'alpha-1' in encoded and 'n-wrong' in encoded and ('alice' in encoded)
    assert '"redacted": true' in encoded
    text = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(model_path), str(population_path), '--format', 'text'], capture_output=True, text=True, check=False)
    assert text.returncode == 4
    assert 'SECRET-EXISTS-271828' not in text.stdout + text.stderr
    assert '987654321' not in text.stdout + text.stderr
    transition_model = document()
    transition_model['operations'] = [{'id': 'reassert_sample', 'reading': 'Record {Sample}', 'parameters': [{'name': 'sample', 'object_type': 'sample'}, {'name': 'monitor', 'object_type': 'monitor'}, {'name': 'pci', 'object_type': 'integer'}, {'name': 'token', 'object_type': 'token'}], 'effects': [{'assert': {'fact_type': 'radio_sample', 'bind': {'sample': '$sample', 'monitor': '$monitor', 'pci': '$pci', 'token': '$token'}}}], 'frame': {'modality': 'alethic'}, 'source': 'explicit', 'status': 'confirmed', 'provenance': {'user_quote': 'Reasserting a sample preserves its declared values.'}}]
    transition_population = population_document()
    transition_population['facts']['radio_sample'] = [row for row in transition_population['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    transition_population['facts']['neighbor_cell'][1]['pci'] = 987654321
    transition_population['facts']['neighbor_cell'][1]['modulus'] = 0
    transition_dir = tmp_path / 'transition'
    model_file, pre_file = write_case(transition_dir, transition_model, transition_population)
    loaded_model = load_model(model_file)
    steps_file = Path(transition_dir) / 'steps.json'
    steps_file.write_text(json.dumps({'steps_schema': 1, 'model': loaded_model.model_id, 'model_digest': transition.model_digest(loaded_model), 'operations_digest': transition.operations_digest(loaded_model.operations), 'steps': [{'op': 'reassert_sample', 'bindings': {'sample': 'alpha-1', 'monitor': 'alice', 'pci': 29, 'token': 'SECRET-EXISTS-271828'}}]}), encoding='utf-8')
    transition_json = io.StringIO()
    with contextlib.redirect_stdout(transition_json):
        transition_exit = main(['check', str(model_file), '--pre', str(pre_file), '--steps', str(steps_file), '--format', 'json'])
    transition_encoded = transition_json.getvalue()
    transition_text = io.StringIO()
    with contextlib.redirect_stdout(transition_text):
        transition_text_exit = main(['check', str(model_file), '--pre', str(pre_file), '--steps', str(steps_file)])
    transition_rendered = transition_text.getvalue()
    assert transition_exit == transition_text_exit == 4
    assert 'SECRET-EXISTS-271828' not in transition_encoded + transition_rendered
    assert '987654321' not in transition_encoded + transition_rendered
    assert 'alpha-1' in transition_encoded + transition_rendered
    assert 'n-wrong' in transition_encoded + transition_rendered
    assert_answer('E18', exit=0, secret_absent='SECRET-EXISTS-271828' not in encoded + text.stdout + text.stderr and '987654321' not in encoded + text.stdout + text.stderr, unrelated_public_value_visible='alpha-1' in encoded and 'n-wrong' in encoded, transition_exit=transition_exit, transition_secret_absent='SECRET-EXISTS-271828' not in transition_encoded + transition_rendered, transition_candidate_value_absent='987654321' not in transition_encoded + transition_rendered, transition_public_value_visible='alpha-1' in transition_encoded + transition_rendered and 'n-wrong' in transition_encoded + transition_rendered)

def test_e34_unavailable_derived_exists_binding_does_not_leak(tmp_path):
    model = document()
    source = next(row for row in model['fact_types'] if row['id'] == 'neighbor_cell')
    source['derivation'] = 'semiderived'
    source['derivation_rule'] = {'body': [{'fact_type': 'neighbor_seen', 'bind': {'sample': '$sample', 'neighbor': '$cell'}}, {'fact_type': 'radio_sample', 'bind': {'sample': '$sample', 'pci': '$pci', 'monitor': '$monitor', 'token': '$token'}}], 'where': [{'operator': '<', 'left': {'fn': 'mod', 'args': ['$pci', 0]}, 'right': 30}], 'head': {'cell': '$cell', 'pci': '$pci', 'modulus': 30}}
    population = population_document()
    population['facts'].pop('neighbor_cell')
    model_path, population_path = write_case(tmp_path, model, population)
    payload = check(model_path, population_path)
    encoded = json.dumps(payload, sort_keys=True)
    assert payload['exit_code'] == 4
    assert 'SECRET-EXISTS-271828' not in encoded
    assert 'TOKEN-ALPHA-2' not in encoded
    assert 'binding=' not in payload['verdicts'][0]['message']
    rendered = io.StringIO()
    with contextlib.redirect_stdout(rendered):
        exit_code = main(['check', str(model_path), str(population_path), '--format', 'text'])
    assert exit_code == 4
    text_output = rendered.getvalue()
    assert 'SECRET-EXISTS-271828' not in text_output
    assert 'TOKEN-ALPHA-2' not in text_output
    assert 'term:mod-zero' in text_output
    from gnd.checker import check as raw_check
    from gnd.population import load_population
    loaded_model = load_model(model_path)
    loaded_population = load_population(population_path, model=loaded_model)
    raw_report = raw_check(loaded_model, loaded_population)
    transition_envelope = project_output('plan', {'transition': {'pre_snapshot': raw_report.model_dump(mode='json'), 'post_snapshot': {'verdicts': [], 'derivations': []}, 'pre_snapshot_verdicts': [], 'frame_verdicts': [], 'steps': []}}, policy=RedactionPolicy.from_model(loaded_model), mode='applied', emitter_id='api-transition-plan')
    transition_encoded = json.dumps(transition_envelope, sort_keys=True)
    assert 'SECRET-EXISTS-271828' not in transition_encoded
    transition_message = transition_envelope['transition']['pre_snapshot']['verdicts'][0]['message']
    assert 'binding=' not in transition_message
    assert_answer('E34', exit=payload['exit_code'], api_secret_absent='SECRET-EXISTS-271828' not in encoded, text_secret_absent='SECRET-EXISTS-271828' not in text_output, transition_secret_absent='SECRET-EXISTS-271828' not in transition_encoded, dependency_reason_visible='term:mod-zero' in text_output)
