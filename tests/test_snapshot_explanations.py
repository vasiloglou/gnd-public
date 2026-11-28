import json

from test_checked_extensions import fixture

from gnd import api
from gnd.model import load_model
from gnd.population import load_population


def snapshot(folder, *, covered=True, blocked=("b",), candidates=("a", "b")):
    model, pop = fixture(folder, input_id="candidate", heads=("eligible",), rows=candidates)
    doc = json.loads(model.read_text())
    rule = next(f for f in doc["fact_types"] if f["id"] == "eligible")["derivation_rule"]
    doc["fact_types"].append({"id": "blocked", "reading": "{Item} is blocked",
                               "roles": [{"role_name": "id", "object_type": "item"}]})
    rule["negate"] = [{"fact_type": "blocked", "bind": {"id": "$x"}}]
    model.write_text(json.dumps(doc))
    population = json.loads(pop.read_text())
    if covered:
        population["facts"]["blocked"] = [{"id": s} for s in blocked]
        population["population"]["covers"].append("blocked")
    pop.write_text(json.dumps(population))
    return model, pop


def target(value):
    return {"fact_type": "eligible", "tuple": [{"primitive": "String", "value": value}]}


def write_request(folder, targets):
    path = folder / "request.json"
    path.write_text(json.dumps({"version": 1, "targets": targets}))
    return path


def test_ordered_batch_shares_preparation_and_isolates_walks(tmp_path, monkeypatch):
    from gnd import checker
    path, pop = snapshot(tmp_path)
    model = load_model(path)
    loaded = load_population(pop, model=model)
    singles = [api.why_not(model, loaded, "eligible", targets=[target(s)]) for s in ("b", "a")]
    calls = []
    real = checker._evaluate_stratified_extensions
    def counted(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)
    monkeypatch.setattr(checker, "_evaluate_stratified_extensions", counted)
    report = api.why_not(model, loaded, "eligible", targets=[target(s) for s in ("b", "a", "b")])
    assert calls == [1]
    assert [r["status"] for r in report["results"]] == ["blocked", "derived", "blocked"]
    for index, item in enumerate(report["results"]):
        assert item["request_index"] == index
        assert item["clauses"] == singles[index % 2]["clauses"]
    rev = api.why_not(path, pop, "eligible", row_path=write_request(tmp_path, [target("a"), target("b")]))
    assert [r["status"] for r in rev["results"]] == ["derived", "blocked"]
    bounded = api.why_not(model, loaded, "eligible", targets=[target("b"), target("a")],
                          limits={"joins": 1, "probes": 1})
    assert [r["status"] for r in bounded["results"]] == ["refused", "derived"]


def test_covered_absence_and_replay(tmp_path):
    path, pop = snapshot(tmp_path)
    request = write_request(tmp_path, [target("a")])
    witness = api.witness(path, pop, request)
    assert witness["exit_code"] == 0
    cert = tmp_path / "cert.json"
    cert.write_text(json.dumps(witness["certificate"]))
    assert api.replay(path, pop, cert)["exit_code"] == 0
    snapshot(tmp_path, blocked=("a", "b"))
    assert api.replay(path, pop, cert)["exit_code"] != 0
    assert api.witness(path, pop, request)["results"][0]["status"] == "missing"
    snapshot(tmp_path, covered=False)
    assert api.witness(path, pop, request)["results"][0]["status"] == "uncovered"
    assert api.why_not(path, pop, "eligible", row_path=request)["reason"] == "negative-relation-not-covered"


def test_configured_scalar_bound_and_batch_projection(tmp_path, monkeypatch):
    long_id = "x" * 5000
    path, pop = snapshot(tmp_path, candidates=(long_id, "a"), blocked=(long_id,))
    monkeypatch.setenv("GND_DISCLOSURE", "customer")
    request = [target(long_id), target("a")]
    assert api.why_not(path, pop, "eligible", targets=request)["exit_code"] == 3
    result = api.why_not(path, pop, "eligible", targets=request, limits={"scalar_bytes": 6000})
    assert result["exit_code"] == 0 and long_id not in json.dumps(result)
    assert api.why_not(path, pop, "eligible", targets=request, limits={"scalar_bytes": 65537})["exit_code"] == 3


def test_correlated_negative_checks_the_whole_tuple_on_replay(tmp_path):
    path, pop = snapshot(tmp_path)
    doc = json.loads(path.read_text())
    for fact in doc["fact_types"]:
        fact["roles"].append({"role_name": "zone", "object_type": "item"})
        fact["reading"] = "{Item:id} is associated with {Item:zone}"
        if rule := fact.get("derivation_rule"):
            rule["body"][0]["bind"]["zone"] = "$z"
            rule["negate"][0]["bind"]["zone"] = "$z"
            rule["head"]["zone"] = "$z"
    path.write_text(json.dumps(doc))
    population = json.loads(pop.read_text())
    population["facts"].update(candidate=[{"id": "a", "zone": "east"}],
                               blocked=[{"id": "a", "zone": "west"}, {"id": "b", "zone": "east"}])
    pop.write_text(json.dumps(population))
    pair = target("a")
    pair["tuple"].append({"primitive": "String", "value": "east"})
    request = write_request(tmp_path, [pair])
    original = api.witness(path, pop, request)
    assert original["exit_code"] == 0
    cert = tmp_path / "proof.json"
    cert.write_text(json.dumps(original["certificate"]))
    assert api.replay(path, pop, cert)["exit_code"] == 0
    population["facts"]["blocked"].append({"id": "a", "zone": "east"})
    pop.write_text(json.dumps(population))
    latest = api.witness(path, pop, request)
    assert latest["results"][0]["status"] == "missing"
    original["certificate"]["binding"] = latest["certificate"]["binding"]
    cert.write_text(json.dumps(original["certificate"]))
    assert api.replay(path, pop, cert)["results"][0]["status"] == "invalid"
