"""Original paired report version/digest builder refusal controls."""
import functools
from typing import Any

from gnd import report as report_module


def _refusal(callable_: Any, *arguments: Any, **keywords: Any) -> str:
    """Return the refusal text, or fail because nothing was refused."""
    try:
        callable_(*arguments, **keywords)
    except Exception as error:  # noqa: BLE001 - the refusal IS the observation
        return f"{type(error).__name__}: {error}"
    raise AssertionError("the reader accepted a document the corpus requires it to refuse")

def test_the_payload_builder_refuses_an_unpaired_version_and_digest() -> None:
    """P3R-4: the pairing is enforced where every payload is BUILT, not only at the schema."""
    build = functools.partial(report_module.build_check_payload, 0, "m.orm.yaml", "p.json")
    assert "must name the model" in _refusal(build, schema_version=5, model_digest=None)
    assert "cannot carry a model digest" in _refusal(
        build, schema_version=3, model_digest="sha256:" + "0" * 64
    )
