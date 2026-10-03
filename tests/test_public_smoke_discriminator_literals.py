from __future__ import annotations

import pytest

from gnd.codegen.emit import smoke_module_relpath
from gnd.codegen.identifiers import smoke_discriminator


@pytest.mark.parametrize(
    ("model_id", "expected"),
    [
        ("urn:gnd-example:bookrec@2", "bookrec"),
        ("urn:gnd-example:expense-tracker@1", "expense_tracker"),
        ("urn:gnd-fixture:phase3-consumers:legacy-derived@1", "legacy_derived"),
        ("gnd-fixture-library-v1", "gnd_fixture_library_v1"),
        ("urn:x:Mixed.Case+Chars@10", "mixed_case_chars"),
        ("bare", "bare"),
    ],
)
def test_the_discriminator_slugs_the_model_id(model_id: str, expected: str) -> None:
    assert smoke_discriminator(model_id, package="model") == expected
    assert smoke_module_relpath(smoke_discriminator(model_id, package="model")) == (
        f"test_architecture_smoke_{expected}.py"
    )


def test_the_version_suffix_is_stripped_so_evolution_never_restales_the_file() -> None:
    """Were @N kept, every `gnd model-evolve` bump would rename a create-once
    file and trigger the refusal -- churn for no reader benefit."""
    assert smoke_discriminator("urn:gnd-example:bookrec@2", package="model") == (
        smoke_discriminator("urn:gnd-example:bookrec@3", package="model")
    )
