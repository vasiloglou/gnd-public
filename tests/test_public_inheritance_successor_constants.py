from gnd.assurance import inheritance as inheritance  # noqa: PLC0414 -- compatibility surface

SUCCESSORS = {
    "P5-024": {
        "layer2_diagnostic": None,
        "layer2_path_contains": None,
        "proof_credit": False,
        "public_exit": 3,
    },
    "P5-025": {
        "layer2_diagnostic": None,
        "layer2_path_contains": None,
        "proof_credit": False,
        "public_exit": 0,
    },
}


RETIRED = {"IN-024", "PR-024", "IN-025", "PR-025"}


def test_named_successors_are_the_production_constants():
    assert inheritance.PHASE5_SUCCESSOR_OBSERVATIONS == SUCCESSORS
    assert inheritance.PHASE5_RETIRED_MUTATIONS == RETIRED
    assert inheritance.COUNTS["phase5"] == (26, 69)
