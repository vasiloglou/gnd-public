"""One source change per production-read dimension must break its bridge test.

These are executable counterchecks of the adapter tests, not correspondence
proofs. Each mutant is loaded in memory; production source is never overwritten.
"""

import inspect
import sys
import types

import pytest
from support import public_adapter_mutation_controls as controls

from gnd import semantic_adapter
from gnd.semantic_registry import IR_DIMENSIONS

_MUTATIONS = (
    (
        "identity",
        'return Scalar("string", value, 0, 1, False, "string")',
        'return canonical_scalar(int(value), None) if value.isdecimal() else Scalar("string", value, 0, 1, False, "string")',
        "test_scalar_identity_and_order_are_separate",
    ),
    (
        "order",
        "numerator, denominator = value.as_integer_ratio()",
        "numerator, denominator = ord(str(value)[0]), 1",
        "test_numeric_order_uses_value_not_text",
    ),
    (
        "role-order",
        'for role in source.get("roles", [])',
        'for role in reversed(source.get("roles", []))',
        "test_role_order_multiplicity_covers_and_explicit_instances",
    ),
    (
        "multiplicity",
        "                rows.append(tuple(converted))",
        "                if tuple(converted) not in rows:\n                    rows.append(tuple(converted))",
        "test_role_order_multiplicity_covers_and_explicit_instances",
    ),
    (
        "primitive",
        'resolve_primitive(role["object_type"], model) or "",',
        '"",',
        "test_role_order_multiplicity_covers_and_explicit_instances",
    ),
    (
        "covers",
        "tuple(population.covers),",
        "(),",
        "test_role_order_multiplicity_covers_and_explicit_instances",
    ),
    (
        "declared",
        "identity in population.covers,",
        "identity not in population.covers,",
        "test_role_order_multiplicity_covers_and_explicit_instances",
    ),
    (
        "instances",
        "for identity, values in population.instances.items()",
        "for identity, values in ()",
        "test_role_order_multiplicity_covers_and_explicit_instances",
    ),
    (
        "subtype-closure",
        "tuple(sorted(closure)),",
        'tuple(sorted(child["id"] for child in model.object_types if child["id"] == identity or identity in child.get("subtype_of", []))),',
        "test_subtype_closure_retains_grandchildren",
    ),
    (
        "reference-widening",
        "tuple(sorted(denoting)),",
        "tuple(sorted(denoting | {identity})),",
        "test_reference_universe_widens_only_from_values_to_entities",
    ),
    (
        "modality",
        "base = replace(base, modality=modality, fact_type=host)",
        'base = replace(base, modality="alethic" if modality == "deontic" else "deontic", fact_type=host)',
        "test_bound_operator_modality_and_operand_order_survive",
    ),
    (
        "bound",
        "*inclusive,",
        "True, True,",
        "test_bound_operator_modality_and_operand_order_survive",
    ),
    (
        "operator",
        "base = replace(base, operator=operator, operands=tuple(operands))",
        'base = replace(base, operator="<" if operator == "<=" else operator, operands=tuple(operands))',
        "test_guard_consequents_and_variants_remain_distinct",
    ),
    (
        "literal",
        "tagged=tagged,",
        "tagged=False,",
        "test_tagged_and_legacy_literals_keep_syntax_and_interpretation",
    ),
    (
        "variant",
        "variant=constraint_variant(source, fact_type),",
        'variant="n-a",',
        "test_guard_consequents_and_variants_remain_distinct",
    ),
    (
        "consequent",
        "consequent_kind=kind, antecedent=atoms",
        'consequent_kind="atom" if kind == "absence" else kind, antecedent=atoms',
        "test_guard_consequents_and_variants_remain_distinct",
    ),
    (
        "derivation-kind",
        'derivation = source.get("derivation", "asserted")',
        'derivation = "asserted"',
        "test_semiderived_claims_are_retained_without_computing_extensions",
    ),
    (
        "dependency-graph",
        "tuple(sorted(dependencies[identity])),",
        "(),",
        "test_dependency_graph_and_bare_dollar_literal_are_preserved",
    ),
    (
        "order:Date",
        "ordinal = date.fromisoformat(value).toordinal()",
        "ordinal = 0",
        "test_date_coordinates_preserve_calendar_order_and_leap_days",
    ),
    (
        "derivation-kind:coverage-selection",
        "if has_rule and identity not in population.covers",
        "if False",
        "test_structured_derived_relation_selection_preserves_coverage",
    ),
    (
        "order:DateTime:calendar",
        "(parsed.toordinal() - 1)",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
    (
        "order:DateTime:hour",
        "parsed.hour",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
    (
        "order:DateTime:minute",
        "parsed.minute * 60",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
    (
        "order:DateTime:second",
        "parsed.second",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
    (
        "order:DateTime:microsecond",
        "parsed.microsecond",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
    (
        "order:DateTime:offset-days",
        "offset.days * 86400",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
    (
        "order:DateTime:offset-seconds",
        "offset.seconds",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
    (
        "order:DateTime:offset-microseconds",
        "offset.microseconds",
        "0",
        "test_datetime_coordinates_retain_every_instant_component",
    ),
)


def test_mutations_cover_the_declared_production_read_dimensions():
    assert tuple(dict.fromkeys(row[0].split(":", 1)[0] for row in _MUTATIONS)) == IR_DIMENSIONS


@pytest.mark.parametrize(
    "dimension,before,after,test_name", _MUTATIONS, ids=[row[0] for row in _MUTATIONS]
)
def test_each_dimension_has_a_failing_single_source_mutant(
    dimension,
    before,
    after,
    test_name,
    tmp_path,
    monkeypatch,
):
    source = inspect.getsource(semantic_adapter)
    assert source.count(before) == 1, f"{dimension}: stale mutation site"
    control = getattr(controls, test_name)
    available = {"tmp_path": tmp_path, "monkeypatch": monkeypatch}
    arguments = {name: available[name] for name in inspect.signature(control).parameters}
    control(**arguments)
    mutant = types.ModuleType("gnd._adapter_mutant")
    monkeypatch.setitem(sys.modules, mutant.__name__, mutant)
    exec(  # noqa: S102 -- repository source plus one fixed, local mutation only
        compile(source.replace(before, after), f"<adapter mutant: {dimension}>", "exec"),
        mutant.__dict__,
    )
    monkeypatch.setattr(controls, "adapter", mutant)
    with pytest.raises(AssertionError):
        control(**arguments)
