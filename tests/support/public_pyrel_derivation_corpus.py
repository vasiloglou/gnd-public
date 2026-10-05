"""Complete generic corpus/runtime controls; no historical Git provenance claim."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import test_public_derivation_parity_corpus as parity


def _materialize_corpus():
    packed = (Path(__file__).resolve().parents[1] / "fixtures/public-pyrel-derivation/closure.json.gz").read_bytes()
    assert len(packed) <= 65536
    assert hashlib.sha256(packed).hexdigest() == '2cc3de82d631c61643978122897619b9cec8f119b57b66cebafc17721a64bd81'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(262145)
    assert len(raw) <= 262144
    assert hashlib.sha256(raw).hexdigest() == '377e462726a0dc645f8af926bb37c1af4218917ba1d3f580c689f4e991746c1c'
    documents = json.loads(raw)
    assert set(documents) == {'inputs/relational/model.orm.yaml', 'answers/manual.json', 'inputs/relational/population.yaml', 'inputs/identity/population.yaml', 'inputs/identity/model.orm.yaml', 'answers/cases.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-pyrel-corpus-")
    root = Path(temporary.name).resolve()
    corpus = root / "tests/fixtures/v52-pyrel-derivation"
    for name, text in documents.items():
        path = corpus / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for case in parity.ANSWER_KEY["cases"]:
        for name in ("model.orm.yaml", "population.yaml"):
            source = parity.CORPUS / str(case["path"]) / name
            target = root / "tests/fixtures/derivation-evaluation" / str(case["path"]) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
    return temporary, root, corpus

_TEMPORARY, ROOT, CORPUS = _materialize_corpus()
atexit.register(_TEMPORARY.cleanup)
ANSWERS = CORPUS / "answers"
sys.modules["pyrel_derivation_corpus_support"] = sys.modules[__name__]

def cases() -> list[dict[str, Any]]:
    return json.loads((ANSWERS / "cases.json").read_text())["cases"]

def tuples(rows: dict[str, Any]) -> dict[str, tuple[tuple[str, ...], ...]]:
    return {key: tuple(tuple(row) for row in value) for key, value in rows.items()}

def assert_manifest(rows: list[dict[str, Any]]) -> None:
    expected_ids = [case["id"] for case in parity.PARITY_CASES] + ["V52-R1", "V52-R2"]
    assert len(expected_ids) == 77
    assert [case["id"] for case in rows] == expected_ids
    for case in rows:
        mp, pp = ROOT / case["model"], ROOT / case["population"]
        assert hashlib.sha256(mp.read_bytes()).hexdigest() == case["model_sha256"]
        assert hashlib.sha256(pp.read_bytes()).hexdigest() == case["population_sha256"]
        model = parity.load_model(mp)
        heads = {
            str(f["id"]): len(f["roles"])
            for f in model.fact_types
            if isinstance(f.get("derivation_rule"), dict)
        }
        assert set(case["extensions"]) == set(heads)
        for head, values in case["extensions"].items():
            assert len(values) == len(set(map(tuple, values)))
            for row in values:
                assert len(row) == heads[head]
                assert all(isinstance(token, str) for token in row)
        assert parity._canonical_digest(model, tuples(case["extensions"])) == case["digest"]

def assert_observation(case: dict[str, Any], actual: dict[str, Any]) -> None:
    """Exact manual control or current, backend-scoped existing-case disposition."""
    model_path, pop_path = ROOT / case["model"], ROOT / case["population"]
    assert hashlib.sha256(model_path.read_bytes()).hexdigest() == case["model_sha256"], (
        "model input bytes changed"
    )
    assert hashlib.sha256(pop_path.read_bytes()).hexdigest() == case["population_sha256"], (
        "population input bytes changed"
    )
    model = parity.load_model(model_path)
    population = parity.load_population(pop_path, model=model)
    current_production = parity._production_digest(model, population)
    assert current_production == case["digest"], "production no longer matches frozen corpus"
    assert set(actual) == set(case["extensions"]), "oracle omitted or invented derived heads"
    observed = parity._canonical_digest(model, actual)
    if case["id"].startswith("V52-"):
        assert actual == tuples(case["extensions"]), "oracle projection rows differ"
        assert observed == case["digest"]
        return
    parity._assert_recorded_observation(
        case_id=case["id"],
        backend="pyrel",
        model_digest=case["model_sha256"],
        population_digest=case["population_sha256"],
        production_digest=current_production,
        backend_digest=observed,
        version="1.30.1",
    )
    receipt = json.loads(parity.RECEIPT.read_text())
    row = next(row for row in receipt["cases"] if row["case_id"] == case["id"])
    if row["results"]["pyrel"]["status"] == "matched":
        assert actual == tuples(case["extensions"]), "oracle projection rows differ"

