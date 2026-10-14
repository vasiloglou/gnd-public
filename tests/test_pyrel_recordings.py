"""PL4: the recorded coding-assistant sessions are intact, replayable and secret-free."""
from __future__ import annotations

import hashlib
import json
import re
from importlib.resources import files
from pathlib import Path

import pytest

from gnd import api

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'
DOMAINS = {'bookrec': 'model.orm.yaml', 'expense': 'model.orm.json'}
EXTRA = {'README.md', 'TASK-conflict.md', 'TASK-plain.md', 'results.json', 'manifest.json'}
NEEDLES = ('/Users/', '/private/', '/home/', 'Bearer ', 'API_KEY=')
SECRET = re.compile(r'(?<![A-Za-z])sk-[A-Za-z0-9_-]{12,}')


def _recordings(domain):
    return Path(str(files('gnd').joinpath('examples', domain, 'recordings')))


def _manifest(domain):
    return json.loads((_recordings(domain) / 'manifest.json').read_text())


def _sessions():
    return [(domain, name) for domain in DOMAINS for name in sorted(_manifest(domain)['recordings'])]


@pytest.mark.parametrize('domain,name', _sessions())
def test_recorded_bytes_match_the_manifest(domain, name):
    entry = _manifest(domain)['recordings'][name]
    assert entry['files'], name
    for relative, digest in entry['files'].items():
        assert hashlib.sha256((_recordings(domain) / relative).read_bytes()).hexdigest() == digest, relative
    for relative in entry.get('source_stdout_sha256', {}):
        assert relative in entry['files']


@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_every_committed_file_is_in_the_manifest(domain):
    root = _recordings(domain)
    listed = {relative for entry in _manifest(domain)['recordings'].values() for relative in entry['files']}
    on_disk = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    assert on_disk - listed == EXTRA, on_disk - listed - EXTRA


@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_recordings_contain_no_paths_or_credentials(domain):
    for path in _recordings(domain).rglob('*'):
        if path.is_file():
            text = path.read_text(encoding='utf-8')
            for needle in NEEDLES:
                assert needle not in text, (path.name, needle)
            assert SECRET.search(text) is None, path.name


@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_every_retained_candidate_replays_to_its_recorded_exit(domain):
    home = Path(str(files('gnd').joinpath('examples', domain)))
    replayed = 0
    for name in _manifest(domain)['recordings']:
        for attempt in sorted((_recordings(domain) / name).glob('attempt-*')):
            feedback = json.loads((attempt / 'feedback.json').read_text())
            candidates = [p for p in attempt.iterdir() if p.name.endswith('.population.json')]
            exits = dict(feedback.get('payload_exit', []))
            if not candidates:
                assert feedback['disposition'] in {'agent-failure', 'retry'}
                continue
            report = api.check(home / DOMAINS[domain], candidates[0])
            assert report['exit_code'] == exits.get('required'), (name, attempt.name)
            replayed += 1
    assert replayed >= 1


@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_results_match_manifest(domain):
    results = json.loads((_recordings(domain) / 'results.json').read_text())
    manifest = _manifest(domain)
    recorded = {(row['variant'], row['run']): row for row in results['sessions']}
    for name, entry in manifest['recordings'].items():
        row = recorded[(entry['variant'], entry['run'])]
        assert row['disposition'] == entry['result'] and row['bands'] == entry['bands']
        assert len(row['bands']) == row['attempts'] <= results['max_attempts']
        if row['disposition'] == 'accepted':
            assert row['bands'][-1] == 0
    assert results['recorded_on'] == manifest['recorded_on']
    assert manifest['redactions'] == ['<workspace>', '<home>']


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_candidates_through_the_pyrel_app(domain, tmp_path):
    from gnd.export.applications import check_proposal, execute_application

    home = Path(str(files('gnd').joinpath('examples', domain)))
    checked = 0
    for name in _manifest(domain)['recordings']:
        for attempt in sorted((_recordings(domain) / name).glob('attempt-*')):
            candidates = [p for p in attempt.iterdir() if p.name.endswith('.population.json')]
            if not candidates:
                continue
            exits = dict(json.loads((attempt / 'feedback.json').read_text()).get('payload_exit', []))
            out = tmp_path / f'{name}-{attempt.name}.json'
            if domain == 'bookrec':
                result = check_proposal(home / DOMAINS[domain], home / 'seed.population.json', candidates[0], out,
                                        native_python=NATIVE, owned_relations=('recommendation',))
            else:
                result = execute_application(home / DOMAINS[domain], candidates[0], out, native_python=NATIVE,
                                             query_script=home / 'native_query.py', query_args=('report', '', ''))
            expected = exits.get('required')
            if expected in (0, 1):
                assert result['exit_code'] == expected, (name, attempt.name, result.get('reason'))
            else:
                assert result['exit_code'] != 0
            checked += 1
    assert checked >= 1
