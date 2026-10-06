"""RED time-bound classification-layer contract for v6.2 Phase 1."""

from __future__ import annotations

import time

from support.public_classification_fixture import document

from gnd import model as model_module
from gnd.model import _validation as validation_module


def _long_dag(size: int = 160) -> dict[str, object]:
    doc = document("base")
    doc["fact_types"] = doc["fact_types"][:2] + [doc["fact_types"][4]]
    previous = "evidence"
    for index in range(size):
        identifier = f"derived_{index}"
        doc["fact_types"].append(
            {
                "id": identifier,
                "reading": "{Item} is derived",
                "roles": [{"object_type": "item", "role_name": "item"}],
                "derivation": "derived",
                "derivation_rule": {
                    "body": [{"fact_type": previous, "bind": {"item": "$item"}}],
                    "head": {"item": "$item"},
                },
            }
        )
        previous = identifier
    return doc


def test_classification_work_is_linear() -> None:
    classify = model_module.derivation_classifications
    validation_module._DERIVATION_CLASSIFICATION_WORK = 0
    start = time.monotonic()
    rows = classify(_long_dag())
    elapsed = time.monotonic() - start
    assert len(rows) == 160
    assert validation_module._DERIVATION_CLASSIFICATION_WORK <= 8 * 160
    assert elapsed < 2.0


def test_reverse_declared_deep_dag_does_not_use_python_recursion() -> None:
    doc = _long_dag(1_200)
    doc["fact_types"] = list(reversed(doc["fact_types"]))
    rows = model_module.derivation_classifications(doc)
    assert len(rows) == 1_200


def test_many_heads_and_operations_use_an_indexed_intersection() -> None:
    size = 3_200
    doc = _long_dag(1)
    prototype = doc["fact_types"][-1]
    doc["fact_types"] = doc["fact_types"][:-1]
    for index in range(size):
        row = {
            **prototype,
            "id": f"wide_{index}",
            "derivation_rule": {
                "body": [{"fact_type": "evidence", "bind": {"item": "$item"}}],
                "head": {"item": "$item"},
            },
        }
        doc["fact_types"].append(row)
    doc["operations"] = [
        {
            "id": f"operation_{index}",
            "effects": [{"assert": {"fact_type": f"unrelated_{index}"}}],
        }
        for index in range(size)
    ]
    validation_module._DERIVATION_CLASSIFICATION_WORK = 0
    start = time.monotonic()
    rows = model_module.derivation_classifications(doc)
    elapsed = time.monotonic() - start
    assert len(rows) == size
    assert validation_module._DERIVATION_CLASSIFICATION_WORK <= 8 * size + 20
    assert elapsed < 1.0
