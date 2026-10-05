from __future__ import annotations

import json

from support import public_parity_disposition as derivation_parity


def test_p06_p10_dispositions_are_bound_blocking_and_backend_scoped() -> None:
    current = {
        "model": "a" * 64,
        "population": "b" * 64,
        "production": "c" * 64,
        "backend": "d" * 64,
        "version": "test",
    }
    base = {
        "model_sha256": current["model"],
        "population_sha256": current["population"],
        "production_sha256": current["production"],
        "results": {
            "duckdb": {
                "status": "mismatched",
                "version": "test",
                "digest": current["backend"],
                "disposition": None,
            },
            "souffle": {
                "status": "mismatched",
                "version": "test",
                "digest": "e" * 64,
                "disposition": None,
            },
        },
    }

    for disposition in ("evaluator-bug", "spec-gap", "unknown"):
        row = json.loads(json.dumps(base))
        row["results"]["duckdb"]["disposition"] = disposition
        assert not derivation_parity._receipt_row_is_admissible(
            row, backend="duckdb", current=current
        )
    for disposition in ("encoding-bug", "oracle-defect"):
        row = json.loads(json.dumps(base))
        row["results"]["duckdb"]["disposition"] = disposition
        assert derivation_parity._receipt_row_is_admissible(row, backend="duckdb", current=current)
    stale = json.loads(json.dumps(base))
    stale["results"]["duckdb"]["disposition"] = "oracle-defect"
    stale["model_sha256"] = "0" * 64
    assert not derivation_parity._receipt_row_is_admissible(
        stale, backend="duckdb", current=current
    )
    cross_backend = json.loads(json.dumps(base))
    cross_backend["results"]["souffle"]["disposition"] = "oracle-defect"
    assert not derivation_parity._receipt_row_is_admissible(
        cross_backend, backend="duckdb", current=current
    )
