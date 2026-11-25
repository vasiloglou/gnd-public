"""Issue 286: a map keyed by role name is a container, whatever its roles are called.

`gnd validate` read a sample row with a role named `date` or `duration_days` as a
temporal term and refused the model (`semantic:temporal-site`). The walk behind that
rule decided which maps hold role names by the text of their path. It now decides by
the key that holds them (`bind`, `head`, `sample_population`), so the same walk also
finds a date term held by a head role named like a skipped key (`source`, `provenance`)
or like a container key (`bind`, `head`), which it used to miss.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gnd import api
from gnd.terms import is_temporal_node, temporal_nodes, uses_temporal

ROOT = Path(__file__).resolve().parents[1]
COUNT = ROOT / "tests/fixtures/v71/phase6/dispatch/count/model.orm.json"
DATE_TERM = {"fn": "date_add", "args": ["$x", {"duration_days": 1}]}


def poster(role: str, version: int = 3) -> dict:
    """The model of issue 286, with its second role named ROLE."""
    return {
        "version": version,
        "model_id": "urn:example:poster@1",
        "object_types": [
            {"id": "poster", "kind": "value", "name": "PosterName", "primitive": "String"},
            {"id": "poster_date", "kind": "value", "name": "PosterDate", "primitive": "String"},
        ],
        "fact_types": [{
            "id": "poster_is_scheduled",
            "reading": "{PosterName} is scheduled on {PosterDate}",
            "roles": [{"role_name": "poster", "object_type": "poster"},
                      {"role_name": role, "object_type": "poster_date"}],
            "sample_population": [{"poster": "D2P", role: "Tuesday, July 7th"}],
        }],
        "constraints": [],
    }


def validate(tmp_path: Path, model: dict) -> dict:
    path = tmp_path / "model.orm.json"
    path.write_text(json.dumps(model), encoding="utf-8")
    return api.validate(path)


@pytest.mark.parametrize("role", ["date", "duration_days", "fn", "day"])
@pytest.mark.parametrize("version", [2, 3])
def test_a_sample_row_is_data_whatever_its_roles_are_called(tmp_path, role, version):
    model = poster(role, version)
    result = validate(tmp_path, model)
    assert result["exit_code"] == 0, result
    assert not uses_temporal(model)


def test_a_temporal_term_outside_a_comparison_is_still_refused(tmp_path):
    """Control: the rule the issue tripped still holds where it applies."""
    model = poster("day")
    model["object_types"][1]["description"] = "the day"
    model["constraints"] = [{
        "id": "c0", "type": "value", "object_type": "poster_date",
        "values": [{"date": "2026-07-07"}],
        "source": "explicit", "status": "confirmed", "modality": "alethic",
    }]
    result = validate(tmp_path, model)
    assert result["exit_code"] == 3, result
    assert uses_temporal(model)


@pytest.mark.parametrize("role", ["source", "provenance", "bind", "head", "date", "count"])
def test_a_date_term_in_a_head_is_found_whatever_the_role_is_called(tmp_path, role):
    """A head maps roles to terms. A date term there is found and refused under any role name."""
    model = json.loads(COUNT.read_text(encoding="utf-8"))
    rule = next(item["derivation_rule"] for item in model["fact_types"] + model["object_types"]
                if isinstance(item.get("derivation_rule"), dict) and "head" in item["derivation_rule"])
    rule["head"] = {role: copy.deepcopy(DATE_TERM)}
    found = [path for path, node in temporal_nodes(model) if is_temporal_node(node)]
    assert any(path.endswith(f".head.{role}") for path in found), found
    assert uses_temporal(model)
    result = validate(tmp_path, model)
    assert result["exit_code"] == 3
    assert "semantic:temporal-site" in json.dumps(result)


def test_skipped_keys_are_skipped_only_where_they_are_structure():
    """`source` and `provenance` hold no syntax on an element; as role names they are roles."""
    element = {"provenance": {"user_quote": {"date": "2026-01-01"}}, "source": {"date": "x"}}
    assert [path for path, node in temporal_nodes(element) if is_temporal_node(node)] == []
    assert not uses_temporal({"object_types": [element], "fact_types": [], "constraints": [], "operations": []})


@pytest.mark.parametrize("extra", [
    {"head": {"source": {"date": "2026-07-07"}}},       # review r1: was refused once head became a role map
    {"bind": {"day": {"duration_days": 1}}},
    {"sample_population": [{"date": "2026-07-07"}]},    # review r1: was hidden once rows became role maps
    {"when": {"date": "2026-07-07"}},
])
def test_a_description_is_never_read_as_syntax(tmp_path, extra):
    """Descriptions are never checked (representation-format.md): their extras are carried unchanged,
    so a key that names a syntax container there is just a key."""
    model = poster("day")
    model["object_types"][0]["description"] = {"summary": "A poster name.", "extra": extra}
    assert [path for path, node in temporal_nodes(model) if ".description" in path] == []
    assert not uses_temporal(model)
    result = validate(tmp_path, model)
    assert result["exit_code"] == 0, result


@pytest.mark.parametrize("value", [
    {"head": {"source": {"date": "2026-07-07"}}},       # review r2: a nested head in a sample value
    {"bind": {"source": {"date": "2026-07-07"}}},
    {"date": "2026-07-07"},
    {"fn": "date_add", "args": [{"date": "2026-07-07"}, {"duration_days": 1}]},
])
def test_a_sample_row_value_is_data_whatever_it_holds(tmp_path, value):
    """A sample row is data, as a population's facts are: nothing in it is read as syntax."""
    model = poster("day")
    model["fact_types"][0]["sample_population"] = [{"poster": "D2P", "day": value}]
    assert [path for path, node in temporal_nodes(model) if ".sample_population" in path] == []
    assert not uses_temporal(model)
    result = validate(tmp_path, model)
    assert result["exit_code"] == 0, result

