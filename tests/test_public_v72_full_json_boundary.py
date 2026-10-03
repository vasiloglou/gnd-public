"""Complete original154-case public JSON intake boundary regression."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

import pytest
import test_public_v72_status as _status

from gnd.artifacts import sha256_hex


def _materialize_public_fixture():
    path = Path(__file__).parent / "fixtures/public-v72-full-json-boundary/closure.json.gz"
    packed = path.read_bytes()
    assert len(packed) <= 32768
    assert hashlib.sha256(packed).hexdigest() == '57034cb398d70a3ebf4e1f78fb9c2935518c22e287860bbc10dd82982a78f6f4'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(262145)
    assert len(raw) <= 262144
    assert hashlib.sha256(raw).hexdigest() == 'c25e8de799a9a0e16bb52024e2046393b215b0d23eda2f3b769dd72437463373'
    documents = json.loads(raw)
    assert set(documents) == {'tests/fixtures/v71/phase3/dispatch/direct.witness.json', 'tests/fixtures/v71/phase2/dispatch/candidate.pop.json', 'tests/fixtures/v71/phase2/dispatch/model.orm.yaml', 'tests/fixtures/v72/phase4/inputs.json', 'tests/fixtures/v71/phase2/dispatch/references/catalog.pop.json', 'evidence/baseline-before.json', 'tests/fixtures/v71/phase4/legacy-contracts.json', 'tests/fixtures/v71/phase5/dispatch/receipts.json', 'tests/fixtures/v71/phase2/release/model.orm.yaml', 'tests/fixtures/v71/phase2/release/candidate.pop.json', 'evidence/author-baseline.py', 'tests/fixtures/v71/phase5/dispatch/policy.json', 'tests/fixtures/v72/phase4/answers.json', 'tests/fixtures/v71/phase3/release/direct.witness.json', 'tests/fixtures/v71/phase2/release/references/catalog.pop.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-v72-json-boundary-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return temporary, root


_TEMPORARY, ROOT = _materialize_public_fixture()
atexit.register(_TEMPORARY.cleanup)
sys.modules["test_v72_phase2_status"] = _status
CORPUS = ROOT / "tests/fixtures/v72/phase4"
INPUT_BYTES = (CORPUS / "inputs.json").read_bytes()
ANSWER_BYTES = (CORPUS / "answers.json").read_bytes()
assert sha256_hex(INPUT_BYTES) == "be502f420d027d84c873b71d19f9c32f1cd6ed256124133b3173b80cf9c600df"
assert sha256_hex(ANSWER_BYTES) == "d19536fe85692097ffe3a7198c317bbbad8e9749f76fb3f266755cfe3668d656"
CASES = json.loads(INPUT_BYTES)["cases"]
ANSWERS = {row["id"]: row["expected"] for row in json.loads(ANSWER_BYTES)["cases"]}
INSTRUMENT = ROOT / "evidence/author-baseline.py"
SPEC = importlib.util.spec_from_file_location("public_v72_json_baseline", INSTRUMENT)
CHARACTERIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHARACTERIZE)
BEFORE = {row["id"]: row["observation"] for row in json.loads(INSTRUMENT.with_name("baseline-before.json").read_bytes())["cases"]}


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_json_input_boundary(case, tmp_path, monkeypatch):
    actual = CHARACTERIZE.observe(case, tmp_path, monkeypatch, after=True)
    expected = ANSWERS[case["id"]]
    before = BEFORE[case["id"]]
    if expected == "accepted":
        assert actual["kind"] == "accepted", actual
        if case["consumer"] != "dependency":
            assert actual["value"] == before["value"]
    else:
        assert actual["kind"] == "refused", actual
        kind = case["consumer"]
        expected_type = (
            "JsonInputRefusal"
            if kind.startswith("neutral")
            else "PatchRefusal"
            if kind.startswith("patch")
            else "JudgmentInputError"
            if kind in {"fact-digest", "policy", "receipts", "receipt-init", "receipt-digest"}
            else expected
        )
        assert actual["type"] == expected_type, actual
        if expected in {"shape", "limit"}:
            assert actual["reason"] == expected, actual
        if case["variant"] != "giant-int":
            assert actual["message"] == before["message"]
            assert actual["reason"] == before["reason"]
    if case["consumer"].endswith("-work"):
        assert actual["seconds"] < 10

