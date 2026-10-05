"""Exact abstract policy helper and previously reviewed reader exports."""
from test_public_finite_observer_support import legacy_feedback, reader

from gnd import assurance

__all__=["legacy_feedback", "policy", "reader"]

def policy(row: dict) -> dict:
    recipe = row["recipe"]
    required = frozenset(assurance.assurance_prerequisites(row["surface"], row["consumer"]))
    if required != set(recipe["required_infrastructure"]):
        raise ValueError("finite policy recipe changes the derived prerequisite census")
    applicable, covered = frozenset(recipe["applicable"]), frozenset(recipe["covered"])
    level = assurance._assurance_policy(
        applicable,
        covered,
        required=required,
        proved_infrastructure=required - set(recipe["missing_infrastructure"]),
        guards_valid=recipe["guard_failure"] is None,
    )
    return {
        "band": recipe["band"],
        "decision": assurance.semantic_decision_for_band(recipe["band"]),
        "level": level,
        "uncovered": sorted(applicable - covered),
    }
