from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gnd import api
from gnd.cli import main
from gnd.diff import DiffError, compare_constraints, diff_models
from gnd.model import load_model

FIXTURE = Path(__file__).parent / "fixtures/v70-phase6"

def _models(stem: str = "range"):
    return (load_model(FIXTURE / f"{stem}-{side}.orm.yaml") for side in ("a", "b"))

def test_error_does_not_echo_sensitive_opaque_label() -> None:
    a, b = _models("negation")
    for model in (a, b):
        model.fact_types[0]["roles"][0]["redact"] = True
    doc = json.loads((FIXTURE / "negation-blocked.pop.json").read_text())
    doc["facts"]["candidate"][0]["record"] = {"$opaque": "SECRET-ERROR-CANARY", "extra": 42}
    with pytest.raises(DiffError) as caught:
        diff_models(a, b, populations=(("bad.json", json.dumps(doc).encode()),), synthesize=False)
    assert "SECRET-ERROR-CANARY" not in str(caught.value)

def test_datetime_range_does_not_claim_false_implication() -> None:
    a, b = _models()
    for model in (a, b):
        model.object_types[1]["primitive"] = "DateTime"
    a.fact_types[0]["constraints"][1]["range"] = {"min": "2024-01-01T01:00:00+02:00"}
    b.fact_types[0]["constraints"][1]["range"] = {"min": "2024-01-01T00:00:00Z"}
    row = next(row for row in compare_constraints(a, b) if row["family"] == "value" and row["from_model"] == "a")
    assert row["result"] == "undecided"

def test_opaque_derivation_rule_is_unknown() -> None:
    a, b = _models("negation")
    b.fact_types[3]["derivation_rule"] = "opaque rule prose"
    raw = (FIXTURE / "negation-waived.pop.json").read_bytes()
    row = diff_models(a, b, populations=(("waived.json", raw),), synthesize=False)["populations"][0]
    assert row["derivations"][0]["b_status"] == "unknown"
    assert row["derivations"][0]["outcome"] == "unresolved"

def test_opaque_claim_is_not_treated_as_concrete_identity() -> None:
    a, b = _models("negation")
    doc = json.loads((FIXTURE / "negation-opaque.pop.json").read_text())
    doc["facts"]["permitted"][0]["record"] = {"$opaque": "SECRET-CLAIM"}
    row = diff_models(a, b, populations=(("opaque.json", json.dumps(doc).encode()),), synthesize=False)["populations"][0]
    assert row["a"]["band"] == 4

def test_schema_accepts_deontic_warning() -> None:
    a, b = _models()
    a.fact_types[0]["constraints"][1]["modality"] = "deontic"
    raw = (FIXTURE / "range-b-boundary.pop.json").read_bytes()
    report = diff_models(a, b, populations=(("boundary.json", raw),), synthesize=False)
    assert "warning" in {row["verdict"] for row in report["populations"][0]["a"]["verdicts"]}
    schema = json.loads((Path(api.__file__).parent / "diff.schema.json").read_text())
    Draft202012Validator(schema).validate(report)

def test_malformed_bytes_and_model_are_invalid_not_internal(capsys: pytest.CaptureFixture[str]) -> None:
    a, b = _models()
    for raw in (b"\xff", b"facts: [", b"[" * 30000):
        with pytest.raises(DiffError):
            diff_models(a, b, populations=(("bad.json", raw),), synthesize=False)
    assert main(["diff", str(Path(api.__file__).parent / "diff.py"), str(FIXTURE / "range-a.orm.yaml")]) == 3
    assert "Traceback" not in capsys.readouterr().err

def test_symlink_ancestors_are_refused(tmp_path: Path) -> None:
    (tmp_path / "linked").symlink_to(FIXTURE, target_is_directory=True)
    with pytest.raises(DiffError):
        api.diff(tmp_path / "linked" / "range-a.orm.yaml", FIXTURE / "range-b.orm.yaml")
    a, b = _models()
    with pytest.raises(DiffError):
        api.diff(a, b, populations=tmp_path / "linked")

def test_catalogue_accepts_identical_external_and_allowed_shapes() -> None:
    model = load_model(Path(__file__).parent / "fixtures/checker/setfam.orm.yaml")
    rows = compare_constraints(model, model)
    for family in ("uniqueness", "mandatory-disjunctive", "value"):
        self_rows = [row for row in rows if row["family"] == family and row["from_model"] == "a" and row["left_ref"] == row["right_ref"]]
        assert self_rows and all(row["result"] == "implies" for row in self_rows)

def test_uniqueness_only_pair_gets_real_boundary_separator() -> None:
    a, b = _models()
    for model in (a, b):
        del model.fact_types[0]["constraints"][1]
    report = diff_models(a, b)
    assert any(row["origin"] == "other-model-boundary" and row["b"]["band"] == 0 and row["a"]["band"] == 1 for row in report["populations"])

def test_top_level_pairing_indexes_subject() -> None:
    a, b = _models()
    template = copy.deepcopy(a.fact_types[0]["constraints"][1])
    constraints = [{**copy.deepcopy(template), "object_type": f"object-{i}", "role_ref": None} for i in range(40)]
    a = a.model_copy(update={"constraints": constraints})
    b = b.model_copy(update={"constraints": copy.deepcopy(constraints)})
    rows = [row for row in compare_constraints(a, b) if row["family"] == "value" and row["left_ref"].startswith("constraints")]
    assert len(rows) == 80

def test_cli_applied_and_unredacted_emitters(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    for side in ("a", "b"):
        source = (FIXTURE / f"negation-{side}.orm.yaml").read_text()
        (tmp_path / f"negation-{side}.orm.yaml").write_text(
            source.replace("role_name: record}", "role_name: record, redact: true}")
        )
    populations = tmp_path / "populations"
    populations.mkdir()
    (populations / "blocked.json").write_bytes((FIXTURE / "negation-blocked.pop.json").read_bytes())
    args = ["diff", str(tmp_path / "negation-a.orm.yaml"), str(tmp_path / "negation-b.orm.yaml"),
            "--populations", str(populations)]
    for output_format in ("json", "text"):
        assert main([*args, "--format", output_format]) == 0
        applied = capsys.readouterr().out
        assert "R1" not in applied
        assert main([*args, "--format", output_format, "--unredacted"]) == 0
        unredacted = capsys.readouterr().out
        assert "R1" in unredacted
