

from __future__ import annotations

from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator
from support.v62_phase3_corpus import FIXTURE, document

from gnd.model import _load_meta_schema, load_model, semantic_validate
from gnd.redaction import RedactionPolicy


def _document() -> dict:
    return load_model(FIXTURE / "models/exact-terms.orm.yaml").model_dump(exclude={"warnings"})


def _head(document: dict, term: object) -> None:
    document["fact_types"][1]["derivation_rule"]["head"]["residue"] = term


@pytest.mark.parametrize(
    "term",
    [
        "$value",
        7,
        {"fn": "abs", "args": ["$value"]},
        {"fn": "add", "args": ["$value", 1]},
        {"fn": "abs", "args": [{"fn": "add", "args": ["$value", 1]}]},
    ],
)
def test_a01_a05_every_admitted_term_shape_passes_both_validation_layers(term: object) -> None:
    candidate = _document()
    _head(candidate, term)

    assert not list(Draft202012Validator(_load_meta_schema()).iter_errors(candidate))
    assert semantic_validate(candidate) == []


@pytest.mark.parametrize(
    ("term", "rule_id"),
    [
        ({"fn": "unknown", "args": [1, 2]}, "semantic:term-function-name"),
        ({"fn": "add", "args": [1]}, "semantic:term-function-arity"),
        ({"fn": "add", "args": ["$missing", 1]}, "semantic:term-unbound"),
        ({"fn": "add", "args": [True, 1]}, "semantic:term-argument-type"),
    ],
)
def test_local_term_failures_are_named_before_graph_rules(term: object, rule_id: str) -> None:
    document = _document()
    _head(document, term)
    issues = semantic_validate(document)
    assert issues
    assert next(issue for issue in issues if "head[residue]" in issue.path).rule_id == rule_id


def test_a06_closed_term_shapes_and_nonempty_where_are_schema_enforced() -> None:
    validator = Draft202012Validator(_load_meta_schema())
    extra = document()
    extra["fact_types"][1]["derivation_rule"]["head"]["residue"]["extra"] = True
    empty_where = document()
    empty_where["fact_types"][1]["derivation_rule"]["where"] = []

    assert list(validator.iter_errors(extra))
    assert list(validator.iter_errors(empty_where))


@pytest.mark.parametrize(
    "site",
    ["body", "negate", "precondition", "effect", "dynamic-rule"],
)
def test_function_terms_are_refused_outside_the_two_admitted_sites(site: str) -> None:
    validator = Draft202012Validator(_load_meta_schema())
    candidate = _document()
    function = {"fn": "add", "args": ["$value", 1]}
    rule = candidate["fact_types"][1]["derivation_rule"]
    operation = candidate["operations"][0]
    if site == "body":
        rule["body"][0]["bind"]["value"] = function
    elif site == "negate":
        rule["negate"] = [{"fact_type": "input", "bind": {"value": function}}]
    elif site == "precondition":
        operation["preconditions"][0]["require"][0]["bind"]["ticket"] = function
    elif site == "effect":
        operation["effects"][0]["assert"]["bind"]["status"] = function
    else:
        operation["dynamic_rules"] = [
            {
                "id": "no_term_operands",
                "subject": {
                    "fact_type": "input",
                    "value_role": "value",
                    "bind": {"ticket": function},
                },
                "op": "=",
                "modality": "alethic",
                "source": "explicit",
                "status": "confirmed",
                "provenance": {"user_quote": "No operation terms."},
            }
        ]

    assert list(validator.iter_errors(candidate))


def test_term_node_and_depth_budgets_are_layer_two_refusals() -> None:
    nodes = _document()
    _head(nodes, {"fn": "add", "args": [1, 1]})
    term = nodes["fact_types"][1]["derivation_rule"]["head"]["residue"]
    for _ in range(8):
        term = {"fn": "add", "args": [term, deepcopy(term)]}
    _head(nodes, term)
    assert "semantic:term-node-budget" in {issue.rule_id for issue in semantic_validate(nodes)}

    depth = _document()
    term = 1
    for _ in range(33):
        term = {"fn": "neg", "args": [term]}
    _head(depth, term)
    assert "semantic:term-depth-budget" in {issue.rule_id for issue in semantic_validate(depth)}


def test_non_finite_term_literals_are_statically_refused() -> None:
    document = _document()
    document["fact_types"][1]["derivation_rule"]["where"] = [
        {
            "operator": "=",
            "left": {"fn": "add", "args": [float("nan"), 1]},
            "right": 1,
        }
    ]

    assert "semantic:term-non-finite-number" in {
        issue.rule_id for issue in semantic_validate(document)
    }


def test_non_finite_bare_guarded_literals_are_statically_refused() -> None:
    document = _document()
    comparison = document["constraints"][0]["consequent"]["comparison"]
    comparison["left"] = float("nan")
    comparison["right"] = "$value"

    assert "semantic:term-non-finite-number" in {
        issue.rule_id for issue in semantic_validate(document)
    }


def test_noninteger_function_head_requires_future_rounding() -> None:
    document = _document()
    document["object_types"][1]["primitive"] = "Float"
    _head(document, {"fn": "add", "args": ["$value", 1.0]})
    issues = semantic_validate(document)
    assert "semantic:derivation-head-needs-round" in {issue.rule_id for issue in issues}


def test_function_head_must_match_its_declared_integer_role() -> None:
    document = _document()
    document["fact_types"][1]["roles"][1]["object_type"] = "ticket"
    issues = semantic_validate(document)

    assert "semantic:derivation-head-term-type" in {issue.rule_id for issue in issues}


def test_where_comparison_requires_compatible_operand_types() -> None:
    document = _document()
    document["fact_types"][1]["derivation_rule"]["where"][0]["right"] = "literal"
    issues = semantic_validate(document)
    assert "semantic:term-comparison-type" in {issue.rule_id for issue in issues}


def test_term_taint_reaches_head_columns_where_presence_and_upper_strata() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    effective = RedactionPolicy.from_model(model).effective_roles
    assert {
        ("input", "value"),
        ("residue", "ticket"),
        ("residue", "residue"),
        ("doubled_residue", "ticket"),
        ("doubled_residue", "doubled"),
        ("permitted", "ticket"),
    } <= effective
