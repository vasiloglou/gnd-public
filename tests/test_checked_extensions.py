import json
from copy import deepcopy

import pytest

from gnd import api, extensions
from gnd.checker import _core


def fixture(folder, *, input_id="enabled", heads=("active",), covered=True, rows=("a",), claim=None,
            protected=False):
    model = folder / "model.orm.json"
    pop = folder / "population.json"
    role = {"role_name": "id", "object_type": "item"}
    base = {"id": input_id, "reading": "{Item} is enabled", "roles": [role]}
    facts = [base]
    for target in heads:
        facts.append({"id": target, "reading": "{Item} is active", "roles": [deepcopy(role)],
                      "derivation": "derived", "derivation_rule": {
                          "body": [{"fact_type": input_id, "bind": {"id": "$x"}}], "head": {"id": "$x"}}})
    if protected:
        base["roles"][0]["redact"] = True
    model.write_text(json.dumps({"version": 1, "model_id": "active-items",
        "object_types": [{"id": "item", "name": "Item", "kind": "value", "primitive": "String"}],
        "fact_types": list(reversed(facts))}))
    asserted = {input_id: [{"id": s} for s in rows]} if covered else {}
    if claim is not None:
        asserted[heads[0]] = [{"id": s} for s in claim]
    pop.write_text(json.dumps({"population": {"model": model.name, "source": "fixture",
        "covers": list(asserted)}, "facts": asserted}))
    return model, pop


@pytest.mark.parametrize(("input_id", "target"), [("enabled", "active"), ("selected", "eligible")])
@pytest.mark.parametrize("claim", [None, [], ["a"]])
def test_rows_and_findings_from_one_check(tmp_path, monkeypatch, input_id, target, claim):
    model, pop = fixture(tmp_path, input_id=input_id, heads=(target,), claim=claim)
    expected = api.check(model, pop)
    counts = {"check": 0, "derive": 0}
    for owner, name, key in ((_core, "check_legacy", "check"),
                             (extensions, "evaluate_derivations", "derive")):
        fn = getattr(owner, name)
        def counted(*args, _key=key, _fn=fn, **kwargs):
            counts[_key] += 1
            return _fn(*args, **kwargs)
        monkeypatch.setattr(owner, name, counted)
    result = api.check_with_extensions(model, pop, fact_types=[target])
    assert result["report"] == expected
    assert result["extensions"] == [{"fact_type": target, "status": "complete", "rows": [{"id": "a"}]}]
    assert counts == {"check": 1, "derive": 1}


def test_coverage_and_output_limits(tmp_path):
    model, pop = fixture(tmp_path, heads=("active", "eligible"), rows=())
    def rows(names, cap):
        return api.check_with_extensions(model, pop, fact_types=names, max_rows=cap)["extensions"]
    assert rows(["active"], 0)[0] == {"fact_type": "active", "status": "complete", "rows": []}
    fixture(tmp_path, covered=False)
    assert rows(["active"], 10)[0] == {"fact_type": "active", "status": "unavailable"}
    fixture(tmp_path, heads=("active", "eligible"), rows=("z", "a"))
    result = rows(["eligible", "active", "absent", "enabled"], 2)
    assert [item["status"] for item in result] == ["complete", "output-limit", "unavailable", "unavailable"]
    assert {row["id"] for row in result[0]["rows"]} == {"z", "a"}
    assert "rows" not in rows(["active"], 1)[0]


def test_protected_relation_hides_cardinality_and_input_errors(tmp_path, monkeypatch):
    model, pop = fixture(tmp_path, protected=True, rows=("secret",))
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    for cap in (0, 2):
        record = api.check_with_extensions(model, pop, fact_types=["active"], max_rows=cap)
        assert record["extensions"] == [{"fact_type": "active", "status": "protected"}]
        assert "secret" not in json.dumps(record)
    with pytest.raises(api.DisclosureRefused):
        api.check_with_extensions(model, pop, fact_types=["active"], unredacted=True)
    missing = api.check_with_extensions(model, tmp_path / "absent", fact_types=["active"])
    assert missing["report"]["exit_code"] == 3 and missing["extensions"][0]["status"] == "unavailable"


@pytest.mark.parametrize("names,limit", [([], 1), (["a", "a"], 1), (["a"], True),
                                           (["a"], 10001), ("a", 0), (list(map(str, range(65))), 1)])
def test_invalid_request_before_evaluation(names, limit):
    with pytest.raises(ValueError):
        api.check_with_extensions("missing", "missing", fact_types=names, max_rows=limit)


def test_dependency_protection_uses_all_clauses(tmp_path):
    from gnd.model import load_model
    from gnd.redaction import RedactionPolicy

    path, _ = fixture(tmp_path, heads=("middle", "active"), protected=True)
    document = json.loads(path.read_text())
    facts = {fact["id"]: fact for fact in document["fact_types"]}
    rule = facts["middle"]["derivation_rule"]
    facts["middle"]["derivation_rule"] = {"clauses": [rule]}
    facts["active"]["derivation_rule"]["body"][0]["fact_type"] = "middle"
    path.write_text(json.dumps(document))
    policy = RedactionPolicy.from_model(load_model(path))
    for head in ("middle", "active"):
        assert ("enabled", "id") in policy.derivation_roles(head)
        assert (head, "id") in policy.fact_roles(head)


def test_request_counts_at_both_upper_limits(tmp_path):
    path, pop = fixture(tmp_path)
    names = ["active", *(f"other_{i}" for i in range(63))]
    result = api.check_with_extensions(path, pop, fact_types=names, max_rows=10000)
    assert len(result["extensions"]) == 64
    assert result["extensions"][0] == {"fact_type": "active", "status": "complete", "rows": [{"id": "a"}]}
