"""Exact approved BookRec population publication and current runtime checks."""
from __future__ import annotations

import copy
import gzip
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from gnd.model import load_model
from gnd.population import load_population
from gnd.report import load_report_schema

_FIXTURE = Path(__file__).parent / "fixtures/public-book-population-publish/inputs.json.gz"
assert _FIXTURE.is_file() and not _FIXTURE.is_symlink()
with _FIXTURE.open("rb") as _stream:
    _raw = _stream.read(32769)
assert len(_raw) <= 32768 and hashlib.sha256(_raw).hexdigest() == '1328438068390ec44134c4498137c8b3f77d523fa4e8445f93f52ef9c7e2137c'
with gzip.GzipFile(fileobj=io.BytesIO(_raw)) as _stream:
    _expanded = _stream.read(524289)
assert len(_expanded) <= 524288
_rows = json.loads(_expanded)
assert isinstance(_rows, list) and len(_rows) == 27
_holder = TemporaryDirectory(prefix="gnd-public-book-population-")
REPO_ROOT = Path(_holder.name)
_seen = set()
_total = 0
for _row in _rows:
    assert set(_row) == {"path", "bytes", "sha256", "mode", "utf8"}
    _path = PurePosixPath(_row["path"])
    assert _path.parts and not _path.is_absolute() and ".." not in _path.parts
    assert _path.as_posix() == _row["path"] and str(_path) not in _seen
    assert _path.suffix in {".json", ".yaml"} and _row["mode"] in {384, 420}
    _seen.add(str(_path))
    _data = _row["utf8"].encode("utf8")
    assert len(_data) == _row["bytes"] <= 131072
    assert hashlib.sha256(_data).hexdigest() == _row["sha256"]
    _total += len(_data)
    assert _total <= 262144
    _target = REPO_ROOT / _path
    _target.parent.mkdir(parents=True, exist_ok=True)
    _target.write_bytes(_data)
    _target.chmod(_row["mode"])
assert _total == 161298
CORPUS = REPO_ROOT / "tests/fixtures/v5-phase4-bookrec"
CENSUS_PATH = CORPUS / "census/phase4-census.json"
CENSUS_ANSWER_PATH = CORPUS / "answers/phase4-census.expected.json"
EVOLVED_FACT_TYPES = ("book_is_blocked_for", "book_is_eligible")
REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding='utf-8'))
    assert isinstance(value, dict), path
    return value

def _run(arguments: Sequence[str], *, timeout: float=60.0, cwd: Path=REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(part) for part in arguments], cwd=cwd, check=False, capture_output=True, text=True, timeout=timeout)

def _constraint_id_by_ref(model: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for index, constraint in enumerate(model.constraints):
        result[f'constraints[{index}]'] = str(constraint['id'])
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type['id'])
        for index, constraint in enumerate(fact_type.get('constraints') or []):
            result[f'fact_types[{fact_type_id}].constraints[{index}]'] = str(constraint.get('id') or f'{fact_type_id}:{index}')
    return result

def _adult_minor_projection(payload: Mapping[str, Any], model_path: Path) -> dict[str, Any]:
    model = load_model(model_path)
    ids = _constraint_id_by_ref(model)
    verdict = next(verdict for verdict in payload['verdicts'] if ids[str(verdict['constraint_ref'])] == 'recommendation_excludes_adult_books_for_minors')
    return {key: copy.deepcopy(verdict[key]) for key in ('verdict', 'modality', 'reason_code', 'offending_facts')}
CENSUS = _read_json(CENSUS_PATH)
CENSUS_ANSWER = _read_json(CENSUS_ANSWER_PATH)
POST_EVOLUTION_POPULATION_ROWS = [(row_id, answer) for row_id, answer in CENSUS_ANSWER["rows"].items() if answer["disposition"] == "re-record-with-evolution"]

_PRE_BINDINGS = {('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/conforming.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/conforming.population.json', 'fixture_path': 'git-before/conforming.population.json', 'sha256': '50128ceef668c93f68e25ed77f65826e002e4d1d78048d59aa6916ff0d8fa640', 'bytes': 1445}, ('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/genre-only.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/genre-only.population.json', 'fixture_path': 'git-before/genre-only.population.json', 'sha256': '3b98942662fba21b5dc34a03e0fbb63385e22e4c1371a6913387df3871fff9f9', 'bytes': 1206}, ('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/promotion.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/promotion.population.json', 'fixture_path': 'git-before/promotion.population.json', 'sha256': '96cd577a01263d5fe6e555bdafd218e4cace08fb38bc1459657d9045ad6eaba2', 'bytes': 3043}, ('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/seed.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/seed.population.json', 'fixture_path': 'git-before/seed.population.json', 'sha256': 'b453ae561aedbe9019b9e9875930b0ed289d81e3eb3eff10ce29cf6f4745e5d1', 'bytes': 2802}, ('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/tuning-v1.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/tuning-v1.population.json', 'fixture_path': 'git-before/tuning-v1.population.json', 'sha256': 'a3d5262747719f1b438ec6fbd73164871a4360d707a8be64dea9583ac5c7b90e', 'bytes': 3039}, ('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/tuning-v2.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/tuning-v2.population.json', 'fixture_path': 'git-before/tuning-v2.population.json', 'sha256': '96cd577a01263d5fe6e555bdafd218e4cace08fb38bc1459657d9045ad6eaba2', 'bytes': 3043}, ('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/violates-minor-adult.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/violates-minor-adult.population.json', 'fixture_path': 'git-before/violates-minor-adult.population.json', 'sha256': 'cb76d4500a1d827438d6153f3003b89b591bd94ecc62d7fccd9ca4d35951abe0', 'bytes': 1218}, ('public-prepopulation-fixture-coordinate-v1', 'examples/bookrec/populations/violates-rated.population.json'): {'commit': 'public-prepopulation-fixture-coordinate-v1', 'path': 'examples/bookrec/populations/violates-rated.population.json', 'fixture_path': 'git-before/violates-rated.population.json', 'sha256': 'd81781b27957572a2964b471c743b94ffc5d8944b02a9104347d515c5424d568', 'bytes': 1213}}
@lru_cache
def _git_blob(commit: str, path: str) -> bytes:
    binding = _PRE_BINDINGS[(commit, path)]
    raw = (REPO_ROOT / binding["fixture_path"]).read_bytes()
    assert len(raw) == binding["bytes"]
    assert hashlib.sha256(raw).hexdigest() == binding["sha256"]
    return raw
@pytest.mark.parametrize(('row_id', 'answer'), POST_EVOLUTION_POPULATION_ROWS, ids=[row_id.rsplit('/', 1)[-1] for row_id, _answer in POST_EVOLUTION_POPULATION_ROWS])
def test_post_evolution_population_is_published(row_id: str, answer: dict[str, Any]) -> None:
    """Each live re-recording is exactly the approved extension of its prestate."""
    assert len(POST_EVOLUTION_POPULATION_ROWS) == 8
    assert Counter((int(candidate['expected_post_exit']) for _candidate_id, candidate in POST_EVOLUTION_POPULATION_ROWS)) == Counter({0: 1, 1: 7})
    census_row = next(row for row in CENSUS['rows'] if row['row_id'] == row_id)
    population_value = str(census_row['path'])
    population_path = REPO_ROOT / population_value
    model_value = 'examples/bookrec/model.orm.yaml'
    model_path = REPO_ROOT / model_value
    approved_path = CORPUS / 'census' / 'post-evolution' / 'populations' / population_path.name
    pre = json.loads(_git_blob(str(CENSUS['base_commit']), population_value).decode('utf-8'))
    assert isinstance(pre, dict)
    approved = _read_json(approved_path)
    post = _read_json(population_path)
    assert post['instances'] == pre['instances'] == approved['instances']
    assert set(post['facts']) == set(pre['facts']) | set(EVOLVED_FACT_TYPES)
    for fact_type, facts in pre['facts'].items():
        assert approved['facts'][fact_type] == facts
        assert post['facts'][fact_type] == facts
    for fact_type in EVOLVED_FACT_TYPES:
        assert post['facts'][fact_type] == approved['facts'][fact_type]
    expected_population = copy.deepcopy(pre['population'])
    expected_population['covers'] = [*pre['population']['covers'], *EVOLVED_FACT_TYPES]
    expected_population['model'] = '../model.orm.yaml'
    expected_population['model_id'] = 'urn:gnd-example:bookrec@2'
    assert post['population'] == expected_population
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    assert model.version == 2
    assert model.model_id == 'urn:gnd-example:bookrec@2'
    assert population.matches_validation_marker(model)
    completed = _run([sys.executable, '-m', 'gnd', 'check', model_value, population_value, '--format', 'json'])
    assert completed.stdout, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    REPORT_VALIDATOR.validate(payload)
    assert answer['expected_post_exit'] in {0, 1}
    assert completed.returncode == answer['expected_post_exit']
    assert [row['derivation_ref'] for row in payload['derivations']] == [f'derivation:{fact_type}' for fact_type in EVOLVED_FACT_TYPES]
    assert {row['verdict'] for row in payload['derivations']} == {'pass'}
    observed_adult = _adult_minor_projection(payload, model_path)
    assert answer['expected_adult_minor_verdict'] == census_row['adult_minor_verdict']
    assert observed_adult == answer['expected_adult_minor_verdict']

class _MetadataAccessGuard(dict):
    """Refuse reading any fixture metadata field outside the original consumer."""
    def __init__(self, original, allowed):
        super().__init__(original)
        self.allowed = frozenset(allowed)

    def __getitem__(self, key):
        assert key in self.allowed, f"unused private metadata read: {key}"
        return super().__getitem__(key)

    def get(self, key, default=None):
        assert key in self.allowed, f"unused private metadata get: {key}"
        return super().get(key, default)

    def items(self):
        assert set(self) <= self.allowed, "unused private metadata iteration"
        return super().items()

    def values(self):
        assert set(self) <= self.allowed, "unused private metadata values"
        return super().values()


def test_authored_unused_metadata_guard_preserves_every_original_case(monkeypatch):
    selected = {row_id for row_id, _answer in POST_EVOLUTION_POPULATION_ROWS}
    assert len(CENSUS["rows"]) == len(CENSUS_ANSWER["rows"]) == 113
    assert len(selected) == 8
    assert len(CENSUS["json_classifications"]) == 134
    assert len({row["row_id"] for row in CENSUS["rows"]}) == 113
    guarded_rows = []
    for row in CENSUS["rows"]:
        allowed = {"row_id"}
        if row["row_id"] in selected:
            allowed |= {"path", "adult_minor_verdict"}
        dirty = {key: value if key in allowed else object() for key, value in row.items()}
        guarded_rows.append(_MetadataAccessGuard(dirty, allowed))
    guarded_answers = {}
    for row_id, answer in CENSUS_ANSWER["rows"].items():
        allowed = {"disposition"}
        if row_id in selected:
            allowed |= {"expected_post_exit", "expected_adult_minor_verdict"}
        dirty = {key: value if key in allowed else object() for key, value in answer.items()}
        guarded_answers[row_id] = _MetadataAccessGuard(dirty, allowed)
    dirty_census = {key: object() for key in CENSUS}
    dirty_census.update(rows=guarded_rows, base_commit=CENSUS["base_commit"])
    guarded_census = _MetadataAccessGuard(dirty_census, {"rows", "base_commit"})
    guarded = [(row_id, answer) for row_id, answer in guarded_answers.items()
               if answer["disposition"] == "re-record-with-evolution"]
    assert [row_id for row_id, _answer in guarded] == [row_id for row_id, _answer in POST_EVOLUTION_POPULATION_ROWS]
    dirty_answer_root = {key: object() for key in CENSUS_ANSWER}
    dirty_answer_root["rows"] = guarded_answers
    monkeypatch.setitem(globals(), "CENSUS_ANSWER", _MetadataAccessGuard(dirty_answer_root, {"rows"}))
    monkeypatch.setitem(globals(), "CENSUS", guarded_census)
    monkeypatch.setitem(globals(), "POST_EVOLUTION_POPULATION_ROWS", guarded)
    for row_id, answer in guarded:
        test_post_evolution_population_is_published(row_id, answer)
    # The guard is independently load-bearing on census and answer private fields.
    with pytest.raises(AssertionError, match="unused private metadata"):
        guarded_rows[0][next(key for key in guarded_rows[0] if key not in guarded_rows[0].allowed)]
    with pytest.raises(AssertionError, match="unused private metadata"):
        next(iter(guarded_answers.values()))[next(key for key in next(iter(guarded_answers.values())) if key not in next(iter(guarded_answers.values())).allowed)]


def test_authored_fixture_coordinate_refuses_unknown_prestate():
    with pytest.raises(KeyError):
        _git_blob("unknown-fixture-coordinate", "examples/bookrec/populations/seed.population.json")
    with pytest.raises(KeyError):
        _git_blob(CENSUS["base_commit"], "examples/bookrec/populations/unknown.population.json")
