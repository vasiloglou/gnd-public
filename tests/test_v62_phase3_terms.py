"""Direct exact-term and production-calculator gates for v6.2 Phase 3."""

from __future__ import annotations

import json
from copy import deepcopy
from fractions import Fraction

import pytest
from support.v62_phase3_corpus import FIXTURE

from gnd.checker import (
    band,
    check,
    exact_extension_envelope,
    structured_extension_facts,
    structured_extension_view,
)
from gnd.model import Model, load_model, semantic_validate
from gnd.population import load_population, load_population_bytes
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import IROperand
from gnd.semantic_spec import guarded_operand_value
from gnd.terms import (
    ExactTermLimits,
    analyze_term,
    compare_terms,
    evaluate_term,
    materialize_scalar,
)
from gnd.transition import band as transition_band
from gnd.transition import evaluate_plan, read_steps_document, validate_steps


@pytest.mark.parametrize(
    ("term", "expected"),
    [
        ({"fn": "add", "args": [1, 2]}, Fraction(3)),
        ({"fn": "sub", "args": [1, 2]}, Fraction(-1)),
        ({"fn": "mul", "args": [2, 3]}, Fraction(6)),
        ({"fn": "neg", "args": [2]}, Fraction(-2)),
        ({"fn": "abs", "args": [-2]}, Fraction(2)),
        ({"fn": "mod", "args": [-1, 30]}, Fraction(29)),
        ({"fn": "mod", "args": [1, -30]}, Fraction(-29)),
    ],
)
def test_exact_function_table(term, expected) -> None:
    result = evaluate_term(term, {})
    assert result.reason is None
    assert result.value == expected


def test_native_truncating_remainder_mutation_disagrees_with_floor_mod() -> None:
    left, right = 1, -30
    truncating_remainder = left - right * int(left / right)
    exact = evaluate_term({"fn": "mod", "args": [left, right]}, {})

    assert truncating_remainder == 1
    assert exact.value == -29
    assert truncating_remainder != exact.value


def test_zero_divisor_is_named_unavailable_for_literal_and_binding() -> None:
    literal = evaluate_term({"fn": "mod", "args": [7, 0]}, {})
    bound = evaluate_term({"fn": "mod", "args": ["$x", "$d"]}, {"x": 7, "d": 0})
    assert literal.reason == bound.reason == "term:mod-zero"
    assert bound.binding == {"x": 7, "d": 0}


def test_recursive_analysis_and_comparison_are_exact() -> None:
    term = {"fn": "abs", "args": [{"fn": "sub", "args": ["$x", 3]}]}
    analysis = analyze_term(term, {"x": "Integer"})
    assert (analysis.primitive, analysis.variables, analysis.issue) == (
        "Integer",
        ("x",),
        None,
    )
    result = compare_terms("=", term, 5, {"x": -2})
    assert result.value is True


def test_non_integer_fraction_never_materializes_as_a_wire_scalar() -> None:
    with pytest.raises(ValueError):
        materialize_scalar(Fraction(1, 3))


def test_runtime_value_width_budget_is_named_unavailable() -> None:
    result = evaluate_term(
        {"fn": "mul", "args": [16, 16]},
        {},
        limits=ExactTermLimits(max_value_bits=8),
    )
    assert result.reason == "term:exact-value-too-wide"

    over_cap_operand = evaluate_term(
        {"fn": "mul", "args": [1 << 9, 1 << 9]},
        {},
        limits=ExactTermLimits(max_value_bits=8),
    )
    assert over_cap_operand.reason == "term:exact-value-too-wide"
    assert over_cap_operand.operations == 0
    assert over_cap_operand.max_value_bits == 9


def test_clean_story_computes_floor_mod_and_upper_stratum() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    population = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=model)
    extensions = structured_extension_facts(model, population)
    assert extensions["residue"] == (
        {"ticket": "SECRET-TERM-314159", "residue": 29},
        {"ticket": "negative", "residue": 29},
        {"ticket": "negative-divisor", "residue": -29},
    )
    assert {tuple(row.items()) for row in extensions["doubled_residue"]} == {
        (("ticket", "SECRET-TERM-314159"), ("doubled", 58)),
        (("ticket", "negative"), ("doubled", 58)),
        (("ticket", "negative-divisor"), ("doubled", -58)),
    }
    report = check(model, population)
    assert band(report) == 0
    assert [item.verdict for item in report.derivations] == ["pass", "pass", "pass"]


def test_where_false_filters_before_projection_and_source_order_controls_undefinedness() -> None:
    original = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    document = deepcopy(original.model_dump(exclude={"warnings"}))
    rule = document["fact_types"][1]["derivation_rule"]
    false_comparison = {"operator": "=", "left": 0, "right": 1}
    undefined_comparison = {
        "operator": "=",
        "left": {"fn": "mod", "args": [1, 0]},
        "right": 0,
    }

    rule["where"] = [false_comparison, undefined_comparison]
    filtered_model = Model.model_validate(document)
    assert semantic_validate(document) == []
    population = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=filtered_model)
    filtered = exact_extension_envelope(filtered_model, population)
    assert filtered["relations"]["residue"] == []
    assert filtered["unavailable"] == {}

    rule["where"] = [undefined_comparison, false_comparison]
    unavailable_model = Model.model_validate(document)
    population = load_population(
        FIXTURE / "populations/term-clean.pop.yaml", model=unavailable_model
    )
    unavailable = exact_extension_envelope(unavailable_model, population)
    assert unavailable["relations"] == {}
    assert unavailable["unavailable"]["residue"]["reason"] == "term:mod-zero"


def test_computed_rows_are_set_deduplicated() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    original = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=model)
    population_document = {
        "population": {
            "model": original.model,
            "model_id": original.model_id,
            "source": original.source,
            "covers": original.covers,
        },
        "instances": original.instances,
        "facts": deepcopy(original.facts),
    }
    population_document["facts"]["input"].append(deepcopy(population_document["facts"]["input"][0]))
    population = load_population_bytes(
        json.dumps(population_document).encode(), source="duplicate.pop.json", model=model
    )

    extensions = structured_extension_facts(model, population)
    assert len(extensions["residue"]) == 3
    assert len(extensions["doubled_residue"]) == 3


@pytest.mark.parametrize(
    ("head", "expected"),
    [
        ("$value", {"negative": -1, "negative-divisor": 1, "SECRET-TERM-314159": 89}),
        (7, {"negative": 7, "negative-divisor": 7, "SECRET-TERM-314159": 7}),
        (
            {"fn": "mod", "args": ["$value", 30]},
            {"negative": 29, "negative-divisor": 1, "SECRET-TERM-314159": 29},
        ),
    ],
)
def test_variable_literal_and_function_heads_use_existing_scalar_roles(
    head: object, expected: dict[str, int]
) -> None:
    document = deepcopy(
        load_model(FIXTURE / "models/exact-terms.orm.yaml").model_dump(exclude={"warnings"})
    )
    document["fact_types"][1]["derivation_rule"]["head"]["residue"] = head

    assert semantic_validate(document) == []
    model = Model.model_validate(document)
    population = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=model)
    rows = structured_extension_facts(model, population)["residue"]
    assert {row["ticket"]: row["residue"] for row in rows} == expected


def test_float_literal_head_preserves_its_existing_wire_scalar() -> None:
    original = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    document = deepcopy(original.model_dump(exclude={"warnings"}))
    document["object_types"].append(
        {"id": "float", "name": "Float", "kind": "value", "primitive": "Float"}
    )
    residue = document["fact_types"][1]
    residue["reading"] = "{Ticket} has float residue {Float}"
    residue["roles"][1]["object_type"] = "float"
    residue["derivation_rule"]["head"]["residue"] = 1.5
    residue["constraints"] = []
    document["fact_types"] = document["fact_types"][:2]
    document["constraints"] = []
    document["operations"] = []

    assert semantic_validate(document) == []
    model = Model.model_validate(document)
    source = load_population(FIXTURE / "populations/term-clean.pop.yaml")
    population = load_population_bytes(
        json.dumps(
            {
                "population": {
                    "model": "memory",
                    "model_id": str(model.model_id),
                    "source": "fixture",
                    "covers": ["input", "residue"],
                },
                "facts": {"input": source.facts["input"]},
            }
        ).encode(),
        source="float-literal.pop.json",
        model=model,
    )

    view = structured_extension_view(model, population)
    assert view.unavailable == {}
    assert {row["residue"] for row in view.facts["residue"]} == {1.5}
    assert all(type(row["residue"]) is float for row in view.facts["residue"])


def test_exact_work_counters_observe_bounded_term_cost() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    population = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=model)
    work = structured_extension_view(model, population).work

    assert work.term_nodes_visited > 0
    assert work.term_operations > 0
    assert 0 < work.max_exact_value_bits <= 65_536


def test_guarded_terms_ignore_authored_semiderived_surplus() -> None:
    original = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    document = deepcopy(original.model_dump(exclude={"warnings"}))
    residue = document["fact_types"][1]
    residue["derivation"] = "semiderived"
    residue["constraints"] = []
    term = {"fn": "mod", "args": [1, "$residue"]}
    document["constraints"] = [
        {
            "id": "surplus_must_be_inert",
            "type": "guarded",
            "modality": "alethic",
            "source": "explicit",
            "status": "confirmed",
            "antecedent": [
                {
                    "fact_type": "residue",
                    "bind": {"ticket": "$ticket", "residue": "$residue"},
                }
            ],
            "consequent": {"comparison": {"operator": "=", "left": term, "right": term}},
            "provenance": {"user_quote": "Computed rows only."},
        }
    ]
    document["operations"] = []
    assert semantic_validate(document) == []
    model = Model.model_validate(document)
    source = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=model)
    population_document = {
        "population": {
            "model": source.model,
            "model_id": source.model_id,
            "source": source.source,
            "covers": source.covers,
        },
        "facts": deepcopy(source.facts),
    }
    population_document["facts"]["residue"].append({"ticket": "surplus", "residue": 0})
    population = load_population_bytes(
        json.dumps(population_document).encode(),
        source="surplus.pop.json",
        model=model,
    )

    verdict = next(
        row for row in check(model, population).verdicts if row.constraint_ref == "constraints[0]"
    )
    assert (verdict.verdict, verdict.reason_code) == ("pass", None)


def test_product_and_optimized_guarded_paths_emit_identical_exact_scalar_bytes() -> None:
    operand = IROperand(
        kind="function",
        function="abs",
        arguments=(
            IROperand(
                kind="function",
                function="sub",
                arguments=(
                    IROperand(kind="variable", variable="x", primitive="Integer"),
                    IROperand(
                        kind="literal", literal=canonical_scalar(3, "Integer"), primitive="Integer"
                    ),
                ),
                primitive="Integer",
            ),
        ),
        primitive="Integer",
    )
    binding = canonical_scalar(-2, "Integer")
    assert binding is not None
    optimized = guarded_operand_value(operand, ("x",), (binding,))
    product = evaluate_term({"fn": "abs", "args": [{"fn": "sub", "args": [-2, 3]}]}, {})
    assert product.available
    assert optimized == canonical_scalar(materialize_scalar(product.value), "Integer")


def test_zero_divisor_marks_relation_and_dependents_unavailable() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    population = load_population(FIXTURE / "populations/term-input.pop.yaml", model=model)
    report = check(model, population)
    assert band(report) == 4
    assert [(item.fact_type, item.reason_code) for item in report.derivations] == [
        ("residue", "term:mod-zero"),
        ("doubled_residue", "term:mod-zero"),
        ("permitted", "term:mod-zero"),
    ]
    assert [(item.constraint_ref, item.reason_code) for item in report.verdicts] == [
        ("fact_types[residue].constraints[0]", "term:mod-zero"),
        ("constraints[0]", "term:mod-zero"),
    ]


def test_guarded_terms_pass_fail_unchecked_and_guarded_only_dispatch() -> None:
    original = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    clean = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=original)
    assert (
        next(
            row for row in check(original, clean).verdicts if row.constraint_ref == "constraints[0]"
        ).verdict
        == "pass"
    )

    failing_document = deepcopy(original.model_dump(exclude={"warnings"}))
    failing_document["constraints"][0]["consequent"]["comparison"]["right"] = 0
    failing_model = Model.model_validate(failing_document)
    failing_population = load_population(
        FIXTURE / "populations/term-clean.pop.yaml", model=failing_model
    )
    failing = next(
        row
        for row in check(failing_model, failing_population).verdicts
        if row.constraint_ref == "constraints[0]"
    )
    assert (failing.verdict, band(check(failing_model, failing_population))) == ("fail", 1)

    unavailable_population = load_population(
        FIXTURE / "populations/term-input.pop.yaml", model=original
    )
    unavailable = next(
        row
        for row in check(original, unavailable_population).verdicts
        if row.constraint_ref == "constraints[0]"
    )
    assert (unavailable.verdict, unavailable.reason_code) == ("unchecked", "term:mod-zero")

    document = deepcopy(original.model_dump(exclude={"warnings"}))
    residue_rule = document["fact_types"][1]["derivation_rule"]
    guarded_inner = document["constraints"][0]["consequent"]["comparison"]["left"]["args"][0]
    assert guarded_inner == residue_rule["head"]["residue"]
    binding = {"value": -1, "divisor": 30}
    assert evaluate_term(guarded_inner, binding) == evaluate_term(
        residue_rule["head"]["residue"], binding
    )

    residue_rule.pop("where")
    residue_rule["head"]["residue"] = "$value"
    doubled_rule = document["fact_types"][2]["derivation_rule"]
    doubled_rule["head"]["doubled"] = "$residue"
    document["fact_types"][3]["derivation_rule"].pop("where")
    guarded_only_model = Model.model_validate(document)
    guarded_population_document = {
        "population": {
            "model": unavailable_population.model,
            "model_id": unavailable_population.model_id,
            "source": unavailable_population.source,
            "covers": ["input"],
        },
        "facts": {"input": unavailable_population.facts["input"]},
    }
    guarded_only_population = load_population_bytes(
        json.dumps(guarded_population_document).encode(),
        source="guarded-only.pop.json",
        model=guarded_only_model,
    )
    guarded_only = check(guarded_only_model, guarded_only_population)
    assert band(guarded_only) == 4
    guarded_verdict = next(
        row for row in guarded_only.verdicts if row.constraint_ref == "constraints[0]"
    )
    assert (guarded_verdict.verdict, guarded_verdict.reason_code) == (
        "unchecked",
        "term:mod-zero",
    )


def test_transition_does_not_consume_an_unavailable_relation_as_empty() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    population = load_population(FIXTURE / "populations/term-input.pop.yaml", model=model)
    document = read_steps_document(FIXTURE / "walks/approve.steps.json")
    result = evaluate_plan(model, population, validate_steps(document, model))

    assert transition_band(result.report) == 4
    assert [
        (verdict.verdict, verdict.reason_code, verdict.fact_type)
        for step in result.report.steps
        for verdict in step.verdicts
        if verdict.kind == "precondition"
    ] == [
        ("unchecked", "term:mod-zero", "permitted"),
        ("unchecked", "term:mod-zero", "permitted"),
    ]
    assert result.computed_post["facts"]["ticket_status"] == [
        {"status": "approved", "ticket": "negative"},
        {"status": "approved", "ticket": "zero"},
    ]


def test_parity_envelope_separates_relations_from_unavailability() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    clean = load_population(FIXTURE / "populations/term-clean.pop.yaml", model=model)
    clean_envelope = exact_extension_envelope(model, clean)
    assert clean_envelope["unavailable"] == {}
    assert clean_envelope["relations"]["residue"] == [
        ['["string","SECRET-TERM-314159"]', '["number",[29,1]]'],
        ['["string","negative"]', '["number",[29,1]]'],
        ['["string","negative-divisor"]', '["number",[-29,1]]'],
    ]

    unavailable = load_population(FIXTURE / "populations/term-input.pop.yaml", model=model)
    envelope = exact_extension_envelope(model, unavailable)
    assert envelope["relations"] == {}
    assert envelope["unavailable"]["residue"] == {
        "reason": "term:mod-zero",
        "binding": {
            "$divisor": '["number",[0,1]]',
            "$ticket": '["string","zero"]',
            "$value": '["number",[7,1]]',
        },
        "source_relation": None,
    }
    assert envelope["unavailable"]["doubled_residue"]["source_relation"] == "residue"
