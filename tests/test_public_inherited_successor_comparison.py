"""Pure comparison successors on synthetic observations; no release authentication."""
from __future__ import annotations

import copy

import pytest
from support.public_inherited_comparison_input import retained

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


def _current() -> tuple[dict, list[dict], list[dict]]:
    prior = retained("phase5")
    observations = copy.deepcopy(prior["observations"])
    for row in observations:
        if row["case_id"] in SUCCESSORS:
            row["actual"] = copy.deepcopy(SUCCESSORS[row["case_id"]])
    mutations = [
        copy.deepcopy(row) for row in prior["mutations"] if row["mutation_id"] not in RETIRED
    ]
    return prior, observations, mutations


def _compare(prior, observations, mutations):
    return inheritance.compare_observations("phase5", prior, observations, mutations, None)




def test_the_observed_successor_state_is_admitted():
    prior, observations, mutations = _current()
    result = _compare(prior, observations, mutations)
    assert (result["observation_count"], result["mutation_count"]) == (26, 69)


def test_the_retired_v60_answer_is_refused_for_a_successor_case():
    """The v6.2 Phase 4 override recorded this legacy value as if observed."""
    prior, observations, mutations = _current()
    legacy = next(row for row in prior["observations"] if row["case_id"] == "P5-025")
    for row in observations:
        if row["case_id"] == "P5-025":
            row["actual"] = copy.deepcopy(legacy["actual"])
    with pytest.raises(ValueError, match="successor"):
        _compare(prior, observations, mutations)


def test_a_retired_mutant_that_is_still_present_is_refused():
    prior, observations, mutations = _current()
    mutations.append(
        copy.deepcopy(next(row for row in prior["mutations"] if row["mutation_id"] == "IN-025"))
    )
    with pytest.raises(ValueError):
        _compare(prior, observations, mutations)


def test_any_other_missing_mutant_is_refused():
    prior, observations, mutations = _current()
    with pytest.raises(ValueError):
        _compare(prior, observations, mutations[1:])


def test_drift_outside_the_named_successors_is_refused():
    prior, observations, mutations = _current()
    victim = next(row for row in observations if row["case_id"] not in SUCCESSORS)
    victim["actual"] = {**victim["actual"], "public_exit": 99}
    with pytest.raises(ValueError, match="inherited semantic or consumer output changed"):
        _compare(prior, observations, mutations)
