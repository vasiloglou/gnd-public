"""WN2: `gnd why-not` and `gnd.api.why_not` against the committed golden corpus.

The goldens were committed before the command existed (WN-D10). Each is the exact
CLI stdout; `<id>.raw.json` is the `--raw` view, which is the API payload plus
`"view": "raw"`.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from gnd import api
from gnd.cli import main

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "tests/fixtures/why_not"
EX = ROOT / "src/gnd/examples/dispatch"
GOLDENS = FX / "goldens"
CASES = json.loads((FX / "cases.json").read_text())
SCHEMA = json.loads((ROOT / "src/gnd/why-not.schema.json").read_text())
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)


def resolve(argv):
    return [a.replace("<fx>", str(FX)).replace("<ex>", str(EX)) for a in argv]


def run_cli(argv, capsys):
    capsys.readouterr()
    code = main(argv)
    return code, capsys.readouterr().out


def api_call(argv):
    args = argv[1:]
    options = {}
    if "--row" in args:
        options["row_path"] = args[args.index("--row") + 1]
    return api.why_not(args[0], args[1], args[args.index("--fact-type") + 1], **options)


# -- T1: every case, both views, CLI and API ---------------------------------------

@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_t1_cli_matches_the_golden_in_both_views(case, capsys):
    argv = resolve(case["argv"])
    code, out = run_cli(argv, capsys)
    assert (code, out) == (case["exit"], (GOLDENS / f"{case['id']}.json").read_text())
    code, out = run_cli([*argv, "--raw"], capsys)
    assert (code, out) == (case["exit"], (GOLDENS / f"{case['id']}.raw.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_t1_api_returns_the_raw_payload(case):
    payload = api_call(resolve(case["argv"]))
    expected = json.loads((GOLDENS / f"{case['id']}.raw.json").read_text())
    expected.pop("view")
    assert payload == expected


# -- T2: schema ---------------------------------------------------------------------

def test_t2_schema_validates_every_golden_and_api_payload():
    VALIDATOR.check_schema(SCHEMA)
    for path in sorted(GOLDENS.glob("*.json")):
        VALIDATOR.validate(json.loads(path.read_text()))
    for case in CASES:
        VALIDATOR.validate(api_call(resolve(case["argv"])))


def test_t2_schema_refuses_a_leaked_sample_and_a_wrong_band():
    payload = json.loads((GOLDENS / "g1-rule-blocked.json").read_text())
    payload["exit_code"] = 2
    assert not VALIDATOR.is_valid(payload)
    payload = json.loads((GOLDENS / "g1-rule-blocked.raw.json").read_text())
    payload["clauses"][0]["blocker"]["samples"] = [{"work": str(i)} for i in range(6)]
    assert not VALIDATOR.is_valid(payload)


# -- T3: the intake-limit projection ------------------------------------------------

def test_t3_intake_limits_project_the_why_not_ceilings():
    from gnd.witness.service import _why_not_intake_limits
    from gnd.witness.types import DEFAULT_LIMITS, WitnessLimits
    from gnd.witness.why_not import DEFAULT_WHY_NOT_LIMITS as W

    projected = _why_not_intake_limits()
    assert isinstance(projected, WitnessLimits)
    assert (projected.bytes, projected.container_depth, projected.scalar_bytes,
            projected.numeric_digits, projected.targets) == (
        W.bytes, W.container_depth, W.scalar_bytes, W.numeric_digits, 1)
    for name in ("nodes", "edges", "binding_cells", "joins", "proof_depth", "expanded_visits"):
        assert getattr(projected, name) == getattr(DEFAULT_LIMITS, name)


# -- T4: leak ------------------------------------------------------------------------

def _scalars(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from _scalars(child)
    elif isinstance(value, list):
        for child in value:
            yield from _scalars(child)
    elif isinstance(value, str) and len(value) >= 4:
        yield value
    elif type(value) is int and value > 1000:
        yield str(value)


def _input_values():
    files = [*FX.glob("claims/*.json"), *FX.glob("rows/*.json"),
             EX / "seed.pop.json", *EX.glob("references/*.json")]
    values = set()
    for path in files:
        if path.name == "model.orm.json":
            continue
        document = json.loads(path.read_text())
        values.update(_scalars(document.get("facts", document.get("targets"))))
    return values


def test_t4_no_population_value_reaches_a_redacted_payload(capsys):
    values = _input_values()
    assert {"val-w1", "val-p1", "WH-A", "DEST-E", "1004"} <= values
    for case in CASES:
        _, out = run_cli(resolve(case["argv"]), capsys)
        assert not [v for v in values if v in out], case["id"]
    raw = (GOLDENS / "g2-row-descent.raw.json").read_text()
    assert "val-w1" in raw and "val-p1" in raw


# -- G12: hostile inputs -------------------------------------------------------------

def _population_with(tmp_path, listed):
    document = json.loads((FX / "claims/gap.pop.json").read_text())
    document["facts"]["listed"] = listed
    return document


def _write_raw(path, text):
    path.write_text(text)
    return str(path)


def _hostile_inputs(tmp_path):
    model = str(FX / "claims/model.orm.json")
    nan = json.dumps(_population_with(tmp_path, [{"work": "val-w9"}])).replace(
        '"val-w9"', "NaN")
    deep = json.loads((FX / "claims/gap.pop.json").read_text())
    nested = "val-w9"
    for _ in range(70):
        nested = [nested]
    deep["population"]["note"] = nested
    long_int = json.dumps(_population_with(tmp_path, [])).replace(
        '"points": 1004', '"points": ' + "9" * 200)
    huge = json.loads((FX / "claims/model.orm.json").read_text())
    huge["description"] = "x" * (10 * 1024 * 1024 + 1)
    return {
        "nan": (model, _write_raw(tmp_path / "nan.pop.json", nan)),
        "deep": (model, _write_raw(tmp_path / "deep.pop.json", json.dumps(deep))),
        "long-int": (model, _write_raw(tmp_path / "long.pop.json", long_int)),
        "huge-model": (_write_raw(tmp_path / "huge.orm.json", json.dumps(huge)),
                       str(FX / "claims/gap.pop.json")),
    }


@pytest.mark.parametrize("name", ["nan", "deep", "long-int", "huge-model"])
def test_g12_hostile_inputs_exit_3(name, tmp_path, capsys):
    model, population = _hostile_inputs(tmp_path)[name]
    code, out = run_cli(["why-not", model, population, "--fact-type", "claim"], capsys)
    assert (code, out) == (3, (GOLDENS / "refused-input.json").read_text())
    assert api.why_not(model, population, "claim")["reason"] == "input-invalid"


def test_g10_fact_type_must_be_a_string():
    assert api.why_not(FX / "claims/model.orm.json", FX / "claims/gap.pop.json", 7)[
        "exit_code"] == 3


# -- T8: counted bounds on intake and view --------------------------------------------

def test_t8_row_intake_stops_at_the_projected_target_ceiling(tmp_path, monkeypatch):
    from gnd.witness import io

    many = {"version": 1, "targets": [
        {"fact_type": "claim", "tuple": [{"primitive": "String", "value": f"val-w{i}"},
                                         {"primitive": "String", "value": "val-p1"}]}
        for i in range(1000)]}
    row = tmp_path / "many.json"
    row.write_text(json.dumps(many))
    shapes = []
    real = io.target_shape
    monkeypatch.setattr(io, "target_shape", lambda t: (shapes.append(1), real(t))[1])
    payload = api.why_not(FX / "claims/model.orm.json", FX / "claims/gap.pop.json", "claim",
                          row_path=row)
    assert payload["reason"] == "input-invalid"
    assert shapes == []


def test_t8_view_visits_each_clause_once(monkeypatch):
    from gnd.witness import view

    clause = json.loads((GOLDENS / "g1-rule-blocked.raw.json").read_text())["clauses"][0]
    payload = json.loads((GOLDENS / "g1-rule-blocked.raw.json").read_text())
    payload.pop("view")
    payload["clauses"] = [dict(clause, clause_index=i) for i in range(50)]
    visits = []
    real = view._why_not_clause
    monkeypatch.setattr(view, "_why_not_clause", lambda c: (visits.append(1), real(c))[1])
    out = view.why_not_view(payload)
    assert len(visits) == 50 and len(out["clauses"]) == 50
    assert all(c["blocker"]["samples"] == "redacted" for c in out["clauses"])


def test_t8_view_is_a_closed_selection():
    from gnd.witness.view import why_not_view

    payload = json.loads((GOLDENS / "g2-row-descent.raw.json").read_text())
    payload.pop("view")
    payload["extra"] = "val-leak"
    payload["clauses"][0]["blocker"]["extra"] = "val-leak"
    payload["clauses"][0]["descent"]["clauses"][0]["steps"][0]["extra"] = "val-leak"
    assert "val-leak" not in json.dumps(why_not_view(payload))

