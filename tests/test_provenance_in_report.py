from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCAB = REPO_ROOT / 'tests' / 'fixtures' / 'models' / 'full_vocabulary.orm.yaml'
SOURCE_VOCABULARY = {'explicit', 'sample', 'common-sense', 'llm-inferred', 'user-supplied', 'imported'}

def test_provenance_flows_from_model_to_payload(tmp_path):
    population = tmp_path / 'population.empty.yaml'
    population.write_text('population:\n  model: full_vocabulary.orm.yaml\n  source: fixture\nfacts: {}\n', encoding='utf-8')
    result = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(FULL_VOCAB), str(population), '--format', 'json'], capture_output=True, text=True, check=False, cwd=REPO_ROOT)
    payload = json.loads(result.stdout)
    assert payload['verdicts'], 'an empty-facts check must still emit verdicts'
    for verdict in payload['verdicts']:
        assert verdict.get('source'), f"every verdict must carry a non-empty source (R-01); {verdict['constraint_ref']} carries {verdict.get('source')!r}"
        assert verdict.get('status'), f"every verdict must carry a non-empty status (R-01); {verdict['constraint_ref']} carries {verdict.get('status')!r}"
    sources = {verdict['source'] for verdict in payload['verdicts']}
    assert len(sources) >= 2, f'full_vocabulary declares 4 distinct source values; a payload showing {sources!r} means the value is a constant, not a threaded read'
    assert sources <= SOURCE_VOCABULARY, f'payload sources must stay inside the meta-schema enum; got {sources!r}'

def test_promoted_verdicts_carry_real_provenance(monkeypatch):
    from gnd.measure import promote as promote_module
    from gnd.model import load_model
    from gnd.synth.provenance import ExpectedState, Sidecar
    model = load_model(str(FULL_VOCAB))
    expected_provenance = {'fact_types[employee_has_name].constraints[0]': ('explicit', 'confirmed'), 'fact_types[employee_reports_to_employee].constraints[1]': ('common-sense', 'proposed')}
    sidecar = Sidecar(population='p.json', population_sha256='x', **{'class': 'violating'}, seed=1, gnd_version='0', model='m', model_digest='d', pool_source='faker', pool_path='p', pool_sha256='s', pool_size=1, expectations={'fact_types[employee_has_name].constraints[0]': ExpectedState(ground_truth='violated', expected_verdict='fail'), 'fact_types[employee_reports_to_employee].constraints[1]': ExpectedState(ground_truth='violated', expected_verdict='warning')})
    captured: dict[str, object] = {}
    real_band = promote_module.band

    def capture_band(report):
        captured['report'] = report
        return real_band(report)
    monkeypatch.setattr(promote_module, 'band', capture_band)
    promote_module.expected_exit_for(model, sidecar)
    report = captured['report']
    by_ref = {verdict.constraint_ref: verdict for verdict in report.verdicts}
    assert set(by_ref) == set(expected_provenance)
    for ref, (source, status) in expected_provenance.items():
        verdict = by_ref[ref]
        assert (verdict.source, verdict.status) == (source, status), f"promotion must thread the constraint's OWN provenance (P-4): {ref} declares ({source!r}, {status!r}) but the verdict carries ({verdict.source!r}, {verdict.status!r})"
