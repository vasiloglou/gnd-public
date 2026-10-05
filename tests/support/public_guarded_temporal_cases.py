"""Three explicit rejecting successors for the current temporal rule family."""
from __future__ import annotations

from copy import deepcopy


def with_duration(document):
    document["version"] = 3
    document["object_types"].append(
        {"id": "elapsed_span", "name": "ElapsedSpan", "kind": "value", "primitive": "Duration"}
    )
    document["fact_types"].append({
        "id": "expense_has_elapsed_span",
        "reading": "{Expense} has {ElapsedSpan}",
        "roles": [
            {"object_type": "expense", "role_name": "expense"},
            {"object_type": "elapsed_span", "role_name": "span"},
        ],
    })


def reject_duration_binding(document):
    with_duration(document)
    document["constraints"][0]["antecedent"].append({
        "fact_type": "expense_has_elapsed_span", "bind": {"expense": "$e", "span": "$a"},
    })


def reject_duration_comparison(document):
    with_duration(document)
    constraint = deepcopy(document["constraints"][0])
    constraint.pop("antecedent")
    constraint.pop("consequent")
    constraint.update(
        id="duration_compare", type="value-comparison",
        role_a={"fact_type": "expense_has_elapsed_span", "role": "span"},
        role_b={"fact_type": "expense_has_amount", "role": "amount"}, operator="<=",
    )
    document["constraints"].append(constraint)


def reject_legacy_duration_site(document):
    with_duration(document)
    document["version"] = 1


P3_TEMPORAL_REJECTING_CASES = [
    ("P3-duration-binding", reject_duration_binding, "semantic:guarded-binding-type"),
    ("P3-duration-comparison", reject_duration_comparison, "semantic:temporal-comparison-type"),
    ("P3-legacy-duration-site", reject_legacy_duration_site, "semantic:temporal-site"),
]
