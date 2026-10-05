from __future__ import annotations

import copy
import json
import time
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from gnd import api
from gnd.diff import DiffError, compare_constraints, diff_models
from gnd.model import load_model

FIXTURE = Path(__file__).parent / "fixtures/v70-phase6"

def _models(stem: str = "range"):
    return (load_model(FIXTURE / f"{stem}-{side}.orm.yaml") for side in ("a", "b"))

def _pair(family: str, left: dict, right: dict) -> list[dict]:
    a, b = _models()
    a.fact_types[0]["constraints"] = [{"type": family, "modality": "alethic", **left}]
    b.fact_types[0]["constraints"] = [{"type": family, "modality": "alethic", **right}]
    return compare_constraints(a, b)

def test_catalogue_decisions_and_refusals() -> None:
    assert [row["result"] for row in _pair("uniqueness", {"roles": ["invoice"]}, {"roles": ["invoice", "amount"]})] == ["implies", "undecided"]
    assert [row["result"] for row in _pair("mandatory", {"role": "invoice"}, {"role": "invoice"})] == ["implies", "implies"]
    assert [row["result"] for row in _pair("mandatory", {"role": "invoice"}, {"role": "amount"})] == ["undecided", "undecided"]
    seq = [{"fact_type": "invoice_amount", "role": "invoice"}]
    other = [{"fact_type": "invoice_amount", "role": "amount"}]
    assert all(row["result"] == "implies" for row in _pair("subset", {"subset_role_seq": seq, "superset_role_seq": other}, {"subset_role_seq": seq, "superset_role_seq": other}))
    assert all(row["result"] == "undecided" for row in _pair("subset", {"subset_role_seq": seq, "superset_role_seq": other}, {"subset_role_seq": other, "superset_role_seq": seq}))
    assert all(row["result"] == "implies" for row in _pair("exclusion", {"role_seq_a": seq, "role_seq_b": other}, {"role_seq_a": seq, "role_seq_b": other}))
    assert all(row["result"] == "undecided" for row in _pair("exclusion", {"role_seq_a": seq, "role_seq_b": other}, {"role_seq_a": other, "role_seq_b": seq}))
    antecedent = [{"fact_type": "invoice_amount", "bind": {"invoice": "$i"}}]
    consequent = {"comparison": {"operator": "<=", "left": "$i", "right": 20}}
    assert all(row["result"] == "implies" for row in _pair("guarded", {"antecedent": antecedent, "consequent": consequent}, {"antecedent": antecedent, "consequent": consequent}))
    renamed_antecedent = [{"fact_type": "invoice_amount", "bind": {"invoice": "$j"}}]
    renamed_consequent = {"comparison": {"operator": "<=", "left": "$j", "right": 20}}
    assert all(row["result"] == "implies" for row in _pair("guarded", {"antecedent": antecedent, "consequent": consequent}, {"antecedent": renamed_antecedent, "consequent": renamed_consequent}))
    assert all(row["result"] == "undecided" for row in _pair("guarded", {"antecedent": antecedent, "consequent": consequent}, {"antecedent": [], "consequent": consequent}))
    early = {"comparison": {"operator": "<=", "left": "$i", "right": "2024-01-01T01:00:00+02:00"}}
    late = {"comparison": {"operator": "<=", "left": "$i", "right": "2024-01-01T00:00:00Z"}}
    assert all(row["result"] == "undecided" for row in _pair("guarded", {"antecedent": antecedent, "consequent": early}, {"antecedent": antecedent, "consequent": late}))
    assert all(row["result"] == "undecided" for row in _pair("ring", {"ring": "acyclic"}, {"ring": "acyclic"}))

def test_range_endpoints_and_modality_are_conservative() -> None:
    base = {"object_type": "amount", "role_ref": {"fact_type": "invoice_amount", "role": "amount"}}
    left = base | {"range": {"min": 10, "max": 20, "min_inclusive": False, "max_inclusive": False}}
    right = base | {"range": {"min": 10, "max": 20, "min_inclusive": True, "max_inclusive": True}}
    assert [row["result"] for row in _pair("value", left, right)] == ["implies", "undecided"]
    assert all(row["result"] == "undecided" for row in _pair("value", base | {"range": {"min": 1, "max": 2}}, base | {"range": {"min": "1", "max": "2"}}))
    a, b = _models()
    b.fact_types[0]["constraints"][0]["modality"] = "deontic"
    assert compare_constraints(a, b)[0]["reason"] == "different-modality"

def test_vocabulary_refuses_before_population_parse() -> None:
    a = load_model(FIXTURE / "range-a.orm.yaml")
    b = load_model(FIXTURE / "negation-a.orm.yaml")
    with pytest.raises(DiffError, match="diff:vocabulary-mismatch"):
        diff_models(a, b, populations=(("bad.json", b"{"),), synthesize=True)

def test_malformed_population_is_refused_and_model_id_stays_bound() -> None:
    a, b = _models()
    with pytest.raises(DiffError, match="diff:invalid-population"):
        diff_models(a, b, populations=(("bad.json", b"{"),), synthesize=False)
    b = b.model_copy(update={"model_id": "urn:changed"})
    raw = (FIXTURE / "range-a.pop.json").read_bytes()
    row = diff_models(a, b, populations=(("range-a.pop.json", raw),), synthesize=False)["populations"][0]
    assert row["a"]["state"] == "checked"
    assert row["b"]["state"] == "not_comparable"
    assert row["a_to_b"] == row["b_to_a"] == []

def test_synthesis_replays_and_exhibits_real_separator() -> None:
    a, b = _models()
    first = diff_models(a, b, seed=0)
    second = diff_models(a, b, seed=0)
    assert first == second
    assert {row["origin"] for row in first["populations"]} >= {"synth-a-conforming", "synth-b-conforming", "other-model-boundary"}
    assert any(row["origin"] == "other-model-boundary" and row["b"]["band"] == 0 and row["a"]["band"] == 1 for row in first["populations"])

def test_api_schema_redaction_and_read_only(tmp_path: Path) -> None:
    a, b = _models("negation")
    for model in (a, b):
        model.fact_types[0]["roles"][0]["redact"] = True
    raw = (FIXTURE / "negation-blocked.pop.json").read_bytes()
    (tmp_path / "blocked.json").write_bytes(raw)
    before_a = api.check(a, tmp_path / "blocked.json", admission=True, unredacted=True)
    before_b = api.check(b, tmp_path / "blocked.json", admission=True, unredacted=True)
    applied = api.diff(a, b, populations=tmp_path)
    full = api.diff(a, b, populations=tmp_path, unredacted=True)
    assert applied["assurance"] == "none"
    assert "R1" not in json.dumps(applied)
    assert "R1" in json.dumps(full)
    assert applied["populations"][0]["a"]["band"] == full["populations"][0]["a"]["band"]
    assert api.check(a, tmp_path / "blocked.json", admission=True, unredacted=True) == before_a
    assert api.check(b, tmp_path / "blocked.json", admission=True, unredacted=True) == before_b
    schema = json.loads((Path(api.__file__).parent / "diff.schema.json").read_text())
    Draft202012Validator(schema).validate(applied)
    dirty = copy.deepcopy(applied)
    del dirty["assurance"]
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(dirty)

def test_directory_refusals(tmp_path: Path) -> None:
    a, b = _models()
    source = FIXTURE / "range-a.pop.json"
    (tmp_path / "link.json").symlink_to(source)
    with pytest.raises(DiffError, match="entry-invalid"):
        api.diff(a, b, populations=tmp_path)
    (tmp_path / "link.json").unlink()
    (tmp_path / "oversize.json").write_bytes(b"x" * (10 * 1024 * 1024 + 1))
    with pytest.raises(DiffError, match="too-large"):
        api.diff(a, b, populations=tmp_path)

def test_catalogue_near_cap_is_indexed() -> None:
    a, b = _models()
    original_a = copy.deepcopy(a.fact_types[0])
    original_b = copy.deepcopy(b.fact_types[0])
    a = a.model_copy(update={"fact_types": [{**copy.deepcopy(original_a), "id": f"fact-{i}"} for i in range(200)]})
    b = b.model_copy(update={"fact_types": [{**copy.deepcopy(original_b), "id": f"fact-{i}"} for i in range(200)]})
    started = time.monotonic()
    rows = compare_constraints(a, b)
    assert len(rows) == 800
    assert time.monotonic() - started < 20
