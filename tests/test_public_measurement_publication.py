from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE_DIR = REPO_ROOT / 'tests/fixtures/public-launch-phase-3/measurement'
COMMITTED_CORPUS = PHASE_DIR / '02-corpus'
MEASUREMENTS = PHASE_DIR / 'measurements'
CORPUS_BUDGET_BYTES = 10 * 1024 * 1024
MODEL = REPO_ROOT / 'tests/fixtures/public-launch-phase-2/model.orm.yaml'
COMMITTED_PAIRS = [('movie', 'faker', MODEL), ('movie', 'llm-proposed', MODEL)]
def test_the_committed_corpus_stays_under_its_budget():
    assert COMMITTED_CORPUS.is_dir()
    total = sum(p.stat().st_size for p in COMMITTED_CORPUS.rglob('*') if p.is_file())
    assert total <= CORPUS_BUDGET_BYTES, f'the committed corpus is {total / 1024 / 1024:.2f} MB, past the {CORPUS_BUDGET_BYTES / 1024 / 1024:.0f} MB budget'

@pytest.mark.parametrize(('name', 'pool', 'model_path'), COMMITTED_PAIRS, ids=lambda v: str(v))
def test_each_committed_payload_reproduces_byte_for_byte(name, pool, model_path, tmp_path):
    committed = MEASUREMENTS / f'{name}.{pool}.json'
    assert committed.exists(), committed
    rerun = tmp_path / 'rerun.json'
    result = subprocess.run([sys.executable, '-m', 'gnd', 'measure', str(model_path.relative_to(REPO_ROOT)), '--populations', str((COMMITTED_CORPUS / name / pool).relative_to(REPO_ROOT)), '--format', 'json', '--out', str(rerun)], capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert rerun.read_bytes() == committed.read_bytes(), f'{name}.{pool}.json did not reproduce byte-for-byte over its own subtree'

@pytest.mark.parametrize(('name', 'pool', 'model_path'), COMMITTED_PAIRS, ids=lambda v: str(v))
def test_each_payload_represents_exactly_one_model_pool_pair(name, pool, model_path):
    import hashlib
    payload = json.loads((MEASUREMENTS / f'{name}.{pool}.json').read_text())
    corpus_root = COMMITTED_CORPUS / name / pool
    assert len({entry['sidecar_sha256'] for entry in payload['corpus']}) == len(payload['corpus'])
    assert len(payload['pools']) == 1
    assert payload['model'] == str(model_path.relative_to(REPO_ROOT))
    for entry in payload['corpus']:
        path = corpus_root / entry['path']
        assert not Path(entry['path']).is_absolute(), entry['path']
        assert path.exists(), entry['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
    assert 'accuracy' not in json.dumps(payload).lower()

def test_the_d17_prime_comparison_joins_rather_than_averages():
    faker = json.loads((MEASUREMENTS / 'movie.faker.json').read_text())
    llm = json.loads((MEASUREMENTS / 'movie.llm-proposed.json').read_text())
    assert faker['pool_source'] != llm['pool_source']
    assert faker['pools'][0]['sha256'] != llm['pools'][0]['sha256'], 'the two corpora must be drawn from genuinely different pools, or the comparison is a tautology'
    a = {r['constraint_ref']: r for r in faker['per_constraint']}
    b = {r['constraint_ref']: r for r in llm['per_constraint']}
    assert set(a) == set(b), 'the join is over compatible refs only'
    deltas = [ref for ref in a if (a[ref]['false_pass_rate'], a[ref]['false_fail_rate'], a[ref]['undecided_rate']) != (b[ref]['false_pass_rate'], b[ref]['false_fail_rate'], b[ref]['undecided_rate'])]
    assert deltas == [], deltas

def test_the_measurement_markdown_states_coverage_before_rates():
    text = (PHASE_DIR / 'PUBLIC-MEASUREMENT.md').read_text(encoding='utf-8')
    assert text.index('## Coverage') < text.index('## The per-constraint rates')
    assert 'not-applicable' in text
    assert '02-corpus/' in text
    assert '```json' in text
    assert 'verifier accuracy' not in text.lower().replace('no blended "verifier accuracy"', '')

def test_every_evidence_excerpt_names_a_committed_corpus_population():
    for name, pool, _model in COMMITTED_PAIRS:
        payload = json.loads((MEASUREMENTS / f'{name}.{pool}.json').read_text())
        corpus_root = COMMITTED_CORPUS / name / pool
        assert payload['per_constraint'] and payload['corpus']
        corpus_paths = {entry['path'] for entry in payload['corpus']}
        for row in payload['per_constraint']:
            evidence = row['evidence']
            assert evidence is not None, row['constraint_ref']
            assert evidence['population'] in corpus_paths
            assert not Path(evidence['population']).is_absolute()
            assert (corpus_root / evidence['population']).exists()
