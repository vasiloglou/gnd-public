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

