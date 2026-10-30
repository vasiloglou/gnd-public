from __future__ import annotations

import inspect

from gnd import api


def test_phase2_public_context_signatures() -> None:
    for name in ("validate", "check", "transition", "diff"):
        parameter = inspect.signature(getattr(api, name)).parameters["references"]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is None
    assert (
        inspect.signature(api.diff).parameters["references_b"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )



def test_receipt_keyword_signature() -> None:
    parameter = inspect.signature(api.transition).parameters["pre_receipt"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is None
    assert tuple(inspect.signature(api.check_with_receipt).parameters) == (
        "model", "population", "unredacted")


def test_why_not_keyword_signature() -> None:
    parameters = inspect.signature(api.why_not).parameters
    assert tuple(parameters) == (
        "model_path", "population_path", "fact_type", "row_path", "reference_root")
    for name in ("row_path", "reference_root"):
        assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert parameters[name].default is None
