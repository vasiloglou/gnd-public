"""P3-MU-1..2 (T3.4, D-P3.6): the expectation engine declares no claim.

``gnd synth`` refuses a structured-derivation model upstream (T3.3), so the
pipeline can never hand :func:`predict_violations` one — but the function is a
public API a direct caller can reach. D-P3.6's ruling: an explicit named
stand-down (the guarded-family pattern at ``mutate.py``'s operator level),
never a silent prediction that omits the derivation outcome.

Committed red: at commit time ``predict_violations`` silently returns a map
that makes no claim about the derivation verdict a mutated asserted fact would
flip.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from gnd.model import load_model
from gnd.synth.assemble import GeneratorError
from gnd.synth.mutate import (
    _direct_subtypes,
    _subtype_partition_witness,
    expected_state,
    predict_violations,
)

CORPUS = Path(__file__).parent / "fixtures" / "phase3-consumers"


def _doc(eligible: list[dict]) -> dict:
    return {
        "population": {
            "model": "eligibility.orm.yaml",
            "model_id": "urn:gnd-fixture:phase3-consumers:eligibility@1",
            "source": "fixture",
            "label": "conforming",
            "covers": ["book_listed", "book_blocked", "book_is_eligible"],
        },
        "instances": {},
        "facts": {
            "book_listed": [{"book": "alpha"}, {"book": "beta"}],
            "book_blocked": [{"book": "beta"}],
            "book_is_eligible": eligible,
        },
    }


def test_predict_violations_refuses_a_structured_derivation_model() -> None:
    """P3-MU-1: a named GeneratorError, never a silent no-claim map."""

    model = load_model(CORPUS / "eligibility.orm.yaml")
    baseline = _doc([{"book": "alpha"}])
    mutated = _doc([])
    with pytest.raises(GeneratorError) as caught:
        predict_violations(model, baseline, mutated)
    message = str(caught.value)
    assert "structured derivation" in message
    assert "book_is_eligible" in message
    assert "no claim" in message


def test_predict_violations_is_unchanged_for_legacy_string_models() -> None:
    """The A10 boundary: a legacy-string rule does not trip the stand-down."""

    model = load_model(CORPUS / "legacy-derived.orm.yaml")
    doc = {
        "population": {
            "model": "legacy-derived.orm.yaml",
            "model_id": "urn:gnd-fixture:phase3-consumers:legacy-derived@1",
            "source": "fixture",
            "label": "conforming",
            "covers": ["item_seeded", "item_ranked"],
        },
        "instances": {},
        "facts": {"item_seeded": [{"item": "a"}], "item_ranked": []},
    }
    assert predict_violations(model, doc, doc) == {}


def test_the_subtype_derivation_hardcode_is_still_correct() -> None:
    """P3-MU-2: subtypes keep subtype-derivation-only — the D6/T1.9 boundary."""

    subtype_model = load_model(
        Path(__file__).parent / "fixtures" / "models" / "library.orm.yaml"
    )
    assert any(
        entry.get("derivation") == "derived" for entry in subtype_model.object_types
    ), "the library fixture must keep its derived subtype (T1.9 guard)"
    partition = next(
        constraint
        for constraint in subtype_model.constraints
        if constraint.get("type") == "subtype-partition"
    )
    children = _direct_subtypes(subtype_model)
    doc = {"instances": {}, "facts": {}}
    assert _subtype_partition_witness(partition, doc, subtype_model, children) is None
    state = expected_state(partition, None, doc, subtype_model, children)
    assert state is not None
    assert state.ground_truth == "satisfied"
    assert state.expected_verdict == "unchecked"
    assert state.reason == "subtype-derivation-only"
