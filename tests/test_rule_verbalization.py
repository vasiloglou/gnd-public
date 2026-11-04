"""MG1: public rendering of derivation rules (model-growth-guardrails MG1 spec).

Test ids T1..T13 follow the spec's test table.
"""

from __future__ import annotations

import copy
import json
import typing
from pathlib import Path

import jsonschema
import pytest

import gnd.model_verbalization as mv
from gnd import api
from gnd.model import ModelValidationError, load_model
from gnd.model_index import ModelIndex
from gnd.model_verbalization import (
    RuleVerbalization,
    VerbalizationError,
    render_model_verbalization,
    render_rule_verbalizations,
)

ROOT = Path(__file__).resolve().parents[1]
BOOKREC = ROOT / "src/gnd/examples/bookrec/complete.orm.yaml"
AGGREGATES = ROOT / "tests/fixtures/v62-phase4/models/aggregates.orm.yaml"
PROSE = ROOT / "tests/fixtures/derivation-evaluation/cases/obligation-opaque-mixed-listed/model.orm.yaml"
CLINIC = ROOT / "tests/fixtures/pyrel-rules-calendar/clinic.orm.json"
ORDERS = ROOT / "tests/fixtures/pyrel-rules-derivations/orders.orm.json"
SCHEMA = json.loads((ROOT / "src/gnd/rule-verbalization.schema.json").read_text())
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)
DERIVED = "This fact type is derived: "
SUCCESSORS = (" Admission depends on ", " Values of every role are redacted", " reading=")
BLOCKED = 6  # book_is_blocked_for in bookrec


def _corpus() -> list[tuple[Path, object]]:
    paths = sorted({
        path for root in (ROOT / "src/gnd/examples", ROOT / "tests")
        for pattern in ("*.orm.yaml", "*.orm.json") for path in root.rglob(pattern)
    })
    loaded = []
    for path in paths:
        try:
            loaded.append((path, load_model(str(path))))
        except Exception:  # noqa: BLE001, S112 -- not a valid model; outside the corpus
            continue
    return loaded


@pytest.fixture(scope="module")
def corpus() -> list[tuple[Path, object]]:
    return [(path, model) for path, model in _corpus()
            if any(item.get("derivation_rule") is not None for item in model.fact_types)]


def _document(path: Path) -> dict:
    return load_model(str(path)).model_dump(exclude={"warnings"}, exclude_none=True)


def _write(tmp_path: Path, document: dict, name: str = "model.orm.json") -> Path:
    target = tmp_path / name
    target.write_text(json.dumps(document), encoding="utf-8")
    return target


def _line(text: str, fact_type: str) -> str:
    prefix = f"[fact-type:{fact_type}] "
    return next(line for line in text.splitlines() if line.startswith(prefix))


def _parity(line: str, text: str) -> bool:
    marker = DERIVED + text
    at = line.find(marker)
    return at >= 0 and any(line.startswith(successor, at + len(marker)) for successor in SUCCESSORS)


# T1, T1b


def test_t1_bookrec_loaded() -> None:
    payload = api.verbalize_rules(load_model(str(BOOKREC)))
    VALIDATOR.validate(payload)
    assert payload["exit_code"] == 0
    assert [rule["fact_type"] for rule in payload["rules"]] == ["book_is_blocked_for", "book_is_eligible"]
    assert all(rule["status"] == "rendered" for rule in payload["rules"])


@pytest.mark.parametrize("path", [BOOKREC, AGGREGATES])
def test_t1b_path_input_equals_loaded(path: Path) -> None:
    loaded = load_model(str(path))
    assert render_model_verbalization(str(path)) == render_model_verbalization(loaded)
    assert api.verbalize_rules(str(path)) == api.verbalize_rules(loaded)


# T2, T3, T3b


def test_t2_corpus_floors(corpus) -> None:
    clauses = {"body": 0, "negate": 0, "where": 0, "aggregate": 0}
    rules = prose = with_clauses = 0
    texts = []
    for _path, model in corpus:
        for result in render_rule_verbalizations(model):
            rules += 1
            prose += result.status == "unsupported"
            if result.text:
                texts.append(result.text)
        for item in model.fact_types:
            rule = item.get("derivation_rule")
            if isinstance(rule, dict):
                with_clauses += "clauses" in rule
                for clause in mv.iter_derivation_clauses(rule):
                    for key in clauses:
                        clauses[key] += bool(clause.get(key))
    assert len(corpus) >= 118 and rules >= 301 and prose >= 19 and with_clauses >= 97
    assert clauses["body"] >= 408 and clauses["negate"] >= 117
    assert clauses["where"] >= 81 and clauses["aggregate"] >= 41
    for marker in ("no ", " fact holds", "; or ", "aggregate ", "group by "):
        assert any(marker in text for text in texts), marker
    assert any(any(op in text for op in (" > ", " < ", " = ", " != ", " >= ", " <= ")) for text in texts)


def test_t3_parity_and_t3b_mutation_control(corpus) -> None:
    checked = 0
    for _path, model in corpus:
        full = render_model_verbalization(model)
        for result in render_rule_verbalizations(model):
            if result.status != "rendered":
                continue
            line = _line(full, result.fact_type)
            assert _parity(line, result.text), result.fact_type
            assert not _parity(line, result.text[:-1]), result.fact_type
            checked += 1
    assert checked >= 282


def test_t3c_control_character_in_variable(tmp_path: Path) -> None:
    document = _document(BOOKREC)
    rule = document["fact_types"][BLOCKED]["derivation_rule"]
    raw = "$u\u0007"
    rule["body"][1]["bind"]["user"] = raw
    rule["head"]["user"] = raw
    model = load_model(str(_write(tmp_path, document)))
    [result] = render_rule_verbalizations(model, fact_types=["book_is_blocked_for"])
    assert "\\x07" in result.text and "\u0007" not in result.text
    assert _parity(_line(render_model_verbalization(model), "book_is_blocked_for"), result.text)


@pytest.mark.parametrize(("change", "successor"), [
    (lambda item: item.__setitem__("depends_on", ["book_rated_adult"]), " Admission depends on "),
    (lambda item: item.__setitem__("redact", True), " Values of every role are redacted"),
])
def test_t3d_other_successors(tmp_path: Path, change, successor: str) -> None:
    document = _document(BOOKREC)
    change(document["fact_types"][BLOCKED])
    model = load_model(str(_write(tmp_path, document)))
    [result] = render_rule_verbalizations(model, fact_types=["book_is_blocked_for"])
    line = _line(render_model_verbalization(model), "book_is_blocked_for")
    assert line.find(DERIVED + result.text + successor) >= 0
    assert _parity(line, result.text)


# T4, T4b, T4c


def test_t4_prose_rule() -> None:
    payload = api.verbalize_rules(str(PROSE), fact_types=["legacy_result"])
    VALIDATOR.validate(payload)
    assert payload["rules"] == [{
        "fact_type": "legacy_result", "status": "unsupported",
        "reason": "prose-rule", "path": "/derivation_rule",
    }]


def _bookrec_rule(document: dict) -> dict:
    return document["fact_types"][BLOCKED]["derivation_rule"]


def _clinic_rule(document: dict) -> dict:
    return document["fact_types"][6]["derivation_rule"]


# (label, source, mutation of the rule, control applied to the rule or None)
MUTATIONS = [
    ("non-dict-atom", BOOKREC, lambda r: r["body"].__setitem__(0, "x"), None),
    ("bind-missing", BOOKREC, lambda r: r["body"][0].pop("bind"), None),
    ("bind-string", BOOKREC, lambda r: r["body"][0].__setitem__("bind", "x"), None),
    ("bind-empty", BOOKREC, lambda r: r["body"][0].__setitem__("bind", {}), None),
    ("aggregate-string", ORDERS, lambda r: r.__setitem__("aggregate", "sum"), None),
    ("term-dict", BOOKREC,
     lambda r: r.__setitem__("where", [{"left": {"x": 1}, "operator": "!=", "right": "$b"}]),
     lambda r: r.__setitem__("where", [{"left": "$u", "operator": "!=", "right": "$b"}])),
    ("term-list", BOOKREC,
     lambda r: r.__setitem__("where", [{"left": [1], "operator": "!=", "right": "$b"}]),
     lambda r: r.__setitem__("where", [{"left": "$u", "operator": "!=", "right": "$b"}])),
    ("where-item-string", BOOKREC, lambda r: r.__setitem__("where", ["x"]),
     lambda r: r.__setitem__("where", [{"left": "$u", "operator": "!=", "right": "$b"}])),
    ("date-add", CLINIC,
     lambda r: r.__setitem__("where", [{"operator": ">", "left": "$r",
                                        "right": {"fn": "date_add", "args": ["$last", {"duration_days": 30}]}}]),
     None),
    ("head-string", BOOKREC, lambda r: r.__setitem__("head", "x"), None),
    ("head-missing", BOOKREC, lambda r: r.pop("head"), None),
]


def _rule_index(source: Path) -> int:
    return {BOOKREC: BLOCKED, CLINIC: 6, ORDERS: 3}[source]


@pytest.mark.parametrize(("label", "source", "mutate", "control"), MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_t4b_validation_refuses_each_fallback(tmp_path: Path, label, source, mutate, control) -> None:
    index = _rule_index(source)
    baseline = _document(source)
    if control is not None:
        control(baseline["fact_types"][index]["derivation_rule"])
    load_model(str(_write(tmp_path, baseline, "control.orm.json")))
    mutated = copy.deepcopy(baseline)
    mutate(mutated["fact_types"][index]["derivation_rule"])
    with pytest.raises(ModelValidationError) as raised:
        load_model(str(_write(tmp_path, mutated, "mutated.orm.json")))
    assert f"$.fact_types[{index}].derivation_rule" in str(raised.value)


# A well-formed date_add renders completely; validation refuses it by policy
# (temporal terms only in guarded operands). The malformed three-argument form
# is the one the renderer cannot express, so T4c uses it in place of T4b's.
IN_MEMORY = [m for m in MUTATIONS if m[0] != "date-add"] + [(
    "date-add-three-args", CLINIC,
    lambda r: r.__setitem__("where", [{"operator": ">", "left": "$r", "right": {
        "fn": "date_add", "args": ["$last", {"duration_days": 30}, {"duration_days": 1}]}}]),
    None,
)]


def test_t4c_well_formed_date_add_renders_completely() -> None:
    model = load_model(str(CLINIC))
    rule = copy.deepcopy(model.fact_types[6]["derivation_rule"])
    MUTATIONS[8][2](rule)
    model.fact_types[6]["derivation_rule"] = rule
    assert api.verbalize_rules(model)["exit_code"] == 3
    with pytest.raises(VerbalizationError):  # re-validation refuses it
        render_rule_verbalizations(model, fact_types=["recent_request"])
    fallbacks: list[str] = []
    text = mv._derivation_cnl(rule, model, fallbacks)
    assert fallbacks == [] and "(30 calendar days after $last)" in text


@pytest.mark.parametrize(("label", "source", "mutate", "control"), IN_MEMORY, ids=[m[0] for m in IN_MEMORY])
def test_t4c_in_memory_mutation_is_refused_not_rendered(label, source, mutate, control) -> None:
    index = _rule_index(source)
    model = load_model(str(source))
    item = model.fact_types[index]
    rule = copy.deepcopy(item["derivation_rule"])
    if control is not None:
        control(rule)
    mutate(rule)
    item["derivation_rule"] = rule
    payload = api.verbalize_rules(model)
    VALIDATOR.validate(payload)
    assert payload["exit_code"] == 3 and "rules" not in payload
    with pytest.raises(VerbalizationError):
        render_rule_verbalizations(model, fact_types=[str(item["id"])])


# T5


def test_t5_refusals_and_selection(tmp_path: Path) -> None:
    assert api.verbalize_rules(str(BOOKREC), fact_types=["no_such"])["exit_code"] == 3
    assert api.verbalize_rules(str(BOOKREC), fact_types=["book_has_genre"])["exit_code"] == 3
    with pytest.raises(TypeError):
        api.verbalize_rules(str(BOOKREC), fact_types="book_is_eligible")
    with pytest.raises(TypeError):
        api.verbalize_rules(str(BOOKREC), fact_types=[1])
    with pytest.raises(TypeError):
        api.verbalize_rules(5)
    assert api.verbalize_rules(str(tmp_path / "missing.orm.yaml"))["exit_code"] == 3
    invalid = _document(BOOKREC)
    invalid["fact_types"][BLOCKED]["derivation_rule"]["head"] = "x"
    assert api.verbalize_rules(str(_write(tmp_path, invalid)))["exit_code"] == 3
    mutated = load_model(str(BOOKREC))
    mutated.fact_types[BLOCKED]["derivation_rule"] = {"head": "x"}
    assert api.verbalize_rules(mutated)["exit_code"] == 3
    with pytest.raises(TypeError):  # argument type is checked before the model
        api.verbalize_rules(str(tmp_path / "missing.orm.yaml"), fact_types="x")
    order = api.verbalize_rules(str(BOOKREC), fact_types=["book_is_eligible", "book_is_blocked_for"])
    assert [rule["fact_type"] for rule in order["rules"]] == ["book_is_blocked_for", "book_is_eligible"]
    twice = api.verbalize_rules(str(BOOKREC), fact_types=("book_is_eligible", "book_is_eligible"))
    assert [rule["fact_type"] for rule in twice["rules"]] == ["book_is_eligible"]
    assert api.verbalize_rules(str(BOOKREC), fact_types=[])["rules"] == []
    for payload in (order, twice, api.verbalize_rules(str(BOOKREC), fact_types=["no_such"])):
        VALIDATOR.validate(payload)


# T11


def test_t11_linear_in_rules(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    document = _document(BOOKREC)
    template = document["fact_types"][BLOCKED]
    ids = []
    for number in range(2000):
        item = copy.deepcopy(template)
        item["id"] = f"blocked_copy_{number:04d}"
        item["reading"] = f"Book {{book}} is blocked copy {number} for User {{user}}"
        document["fact_types"].append(item)
        ids.append(item["id"])
    model = load_model(str(_write(tmp_path, document)))
    calls = {"index": 0, "rules": 0}
    original_index, original_rule = ModelIndex.for_model, mv._derivation_cnl

    def counted_index(cls, *args, **kwargs):
        calls["index"] += 1
        return original_index.__func__(cls, *args, **kwargs)

    def counted_rule(*args, **kwargs):
        calls["rules"] += 1
        return original_rule(*args, **kwargs)

    monkeypatch.setattr(ModelIndex, "for_model", classmethod(counted_index))
    monkeypatch.setattr(mv, "_derivation_cnl", counted_rule)
    everything = render_rule_verbalizations(model)
    assert calls == {"index": 1, "rules": 2002}
    calls.update(index=0, rules=0)
    chosen = render_rule_verbalizations(model, fact_types=list(reversed(ids)) + ids)
    assert calls == {"index": 1, "rules": 2000}
    assert chosen == tuple(result for result in everything if result.fact_type in set(ids))


# T12, T13


def test_t12_schema_and_reason_enum() -> None:
    reasons = SCHEMA["$defs"]["rule"]["oneOf"][1]["properties"]["reason"]["enum"]
    hints = typing.get_type_hints(RuleVerbalization)
    assert set(reasons) == set(typing.get_args(typing.get_args(hints["reason"])[0]))
    bad = api.verbalize_rules(str(PROSE), fact_types=["legacy_result"])
    bad["rules"][0]["reason"] = "unrecognized-term"
    with pytest.raises(jsonschema.ValidationError):
        VALIDATOR.validate(bad)


def test_t13_root_aggregate_with_clauses(tmp_path: Path) -> None:
    document = _document(ORDERS)
    rule = document["fact_types"][3]["derivation_rule"]
    body = rule.pop("body")
    rule["clauses"] = [{"body": body}, {"body": copy.deepcopy(body)}]
    model = load_model(str(_write(tmp_path, document)))
    [result] = render_rule_verbalizations(model, fact_types=["order_total"])
    assert result.status == "rendered"
    first, second = result.text.split("; or ")
    assert "aggregate sum of $q" in first and "aggregate sum of $q" in second
    assert _parity(_line(render_model_verbalization(model), "order_total"), result.text)


# Review regressions (phase-MG1-claude-review.md)

DIRECT = [
    ("atom-without-fact-type", lambda r: r["body"][0].pop("fact_type")),
    ("where-without-operator", lambda r: r.__setitem__("where", [{"left": "$u", "right": "$b"}])),
    ("empty-body", lambda r: r.__setitem__("body", [])),
    ("head-non-string-role", lambda r: r.__setitem__("head", {1: "$u"})),
    ("clauses-string", lambda r: r.__setitem__("clauses", "x")),
    ("unknown-key", lambda r: r.__setitem__("filter", [])),
]


@pytest.mark.parametrize(("label", "mutate"), DIRECT, ids=[d[0] for d in DIRECT])
def test_review_f1_direct_call_revalidates_model(label, mutate) -> None:
    model = load_model(str(BOOKREC))
    rule = copy.deepcopy(model.fact_types[BLOCKED]["derivation_rule"])
    mutate(rule)
    model.fact_types[BLOCKED]["derivation_rule"] = rule
    with pytest.raises(VerbalizationError):
        render_rule_verbalizations(model, fact_types=["book_is_blocked_for"])
    assert api.verbalize_rules(model)["exit_code"] == 3


COLLECTED = IN_MEMORY + [(
    "aggregate-unanalyzable", ORDERS, lambda r: r["aggregate"].__setitem__("fn", "bogus"), None,
)]


@pytest.mark.parametrize(("label", "source", "mutate", "control"), COLLECTED, ids=[c[0] for c in COLLECTED])
def test_review_f2_collector_records_each_branch(label, source, mutate, control) -> None:
    model = load_model(str(source))
    rule = copy.deepcopy(model.fact_types[_rule_index(source)]["derivation_rule"])
    if control is not None:
        control(rule)
    mutate(rule)
    fallbacks: list[str] = []
    mv._derivation_cnl(rule, model, fallbacks)
    assert fallbacks, label


def test_review_f3_model_id_and_ids_in_messages() -> None:
    assert api.verbalize_rules(str(BOOKREC))["model_id"] == "urn:gnd-tutorial:bookrec"
    for identifier in ("no_such", "book_has_genre"):
        payload = api.verbalize_rules(str(BOOKREC), fact_types=[identifier])
        assert identifier in payload["error"]["message"]


def test_review_f5_one_walk_over_fact_types(monkeypatch: pytest.MonkeyPatch) -> None:
    walks = []
    original = ModelIndex.iter_fact_types_shared

    def counted(self):
        walks.append(1)
        return original(self)

    monkeypatch.setattr(ModelIndex, "iter_fact_types_shared", counted)
    render_rule_verbalizations(load_model(str(BOOKREC)))
    assert len(walks) == 1


def test_review_f6_renderer_defect_is_not_an_input_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(*args, **kwargs):
        raise ValueError("renderer defect")

    monkeypatch.setattr(mv, "render_rule_verbalizations", broken)
    with pytest.raises(ValueError, match="renderer defect"):
        api.verbalize_rules(str(BOOKREC))
