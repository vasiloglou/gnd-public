"""Original independent identity/disposition and dev dependency guards."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import duckdb
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DISPOSITIONS = {"evaluator-bug", "encoding-bug", "spec-gap", "oracle-defect"}
BLOCKING_DISPOSITIONS = {"evaluator-bug", "spec-gap"}

def _oracle_identity_token(value: Any, primitive: str | None) -> str:
    """Independent implementation of the normative typed scalar table."""
    if primitive == "Boolean":
        if not isinstance(value, bool):
            raise TypeError("Boolean requires bool")
        payload: list[Any] = ["boolean", value]
    elif primitive in {"Integer", "Float", "Number"}:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{primitive} requires a number")
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError("non-finite number")
            numerator, denominator = value.as_integer_ratio()
        else:
            numerator, denominator = value, 1
        common = math.gcd(numerator, denominator)
        numerator //= common
        denominator //= common
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        payload = ["number", [numerator, denominator]]
    elif primitive in {"String", "Date", "DateTime", "Binary", None}:
        if not isinstance(value, str):
            if primitive is None and isinstance(value, bool):
                payload = ["boolean", value]
            elif primitive is None and isinstance(value, (int, float)):
                if isinstance(value, float) and not math.isfinite(value):
                    raise ValueError("non-finite number")
                numerator, denominator = value.as_integer_ratio()
                payload = ["number", [numerator, denominator]]
            else:
                raise TypeError(f"{primitive} requires a string")
        else:
            payload = ["string", value]
    else:
        raise ValueError(f"unknown primitive {primitive}")
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


@pytest.mark.parametrize(
    ("value", "primitive", "expected"),
    [
        ("λ", "String", '["string","λ"]'),
        (1, "Integer", '["number",[1,1]]'),
        (1.0, "Float", '["number",[1,1]]'),
        (-0.0, "Number", '["number",[0,1]]'),
        ("2026-08-31", "Date", '["string","2026-08-31"]'),
        ("2026-08-31T10:00:00Z", "DateTime", '["string","2026-08-31T10:00:00Z"]'),
        (True, "Boolean", '["boolean",true]'),
        ("AA==", "Binary", '["string","AA=="]'),
    ],
)
def test_independent_codec_goldens(value: Any, primitive: str, expected: str) -> None:
    assert _oracle_identity_token(value, primitive) == expected


def test_boolean_and_number_are_distinct_but_integer_and_float_merge() -> None:
    assert _oracle_identity_token(True, "Boolean") != _oracle_identity_token(1, "Integer")
    assert _oracle_identity_token(1, "Integer") == _oracle_identity_token(1.0, "Float")
    huge = 10**1000
    assert _oracle_identity_token(huge, None) == f'["number",[{huge},1]]'


def _receipt_row_is_admissible(
    row: dict[str, Any],
    *,
    backend: str,
    current: dict[str, str],
) -> bool:
    if not _receipt_row_is_bound(row, backend=backend, current=current):
        return False
    result = row["results"][backend]
    if result.get("digest") != current["backend"]:
        return False
    if "version" in current and result.get("version") != current["version"]:
        return False
    if result["status"] == "matched":
        return True
    return result["disposition"] not in BLOCKING_DISPOSITIONS


def _receipt_row_is_bound(
    row: dict[str, Any],
    *,
    backend: str,
    current: dict[str, str],
) -> bool:
    if row.get("model_sha256") != current["model"]:
        return False
    if row.get("population_sha256") != current["population"]:
        return False
    if row.get("production_sha256") != current["production"]:
        return False
    result = row.get("results", {}).get(backend)
    if not isinstance(result, dict) or set(result) != {
        "status",
        "version",
        "digest",
        "disposition",
    }:
        return False
    if result["status"] == "matched":
        return (
            isinstance(result["version"], str)
            and result["digest"] == current["production"]
            and result["disposition"] is None
        )
    if result["status"] == "skipped":
        return (
            result["version"] is None and result["digest"] is None and result["disposition"] is None
        )
    return (
        result["status"] == "mismatched"
        and isinstance(result["version"], str)
        and isinstance(result["digest"], str)
        and result["digest"] != current["production"]
        and result["disposition"] in DISPOSITIONS
    )


def test_backend_disposition_scope_staleness_and_blocking_classes() -> None:
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
                "digest": "d" * 64,
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
    for disposition in ("encoding-bug", "oracle-defect"):
        row = json.loads(json.dumps(base))
        row["results"]["duckdb"]["disposition"] = disposition
        assert _receipt_row_is_admissible(row, backend="duckdb", current=current)
    changed_backend = json.loads(json.dumps(base))
    changed_backend["results"]["duckdb"]["disposition"] = "oracle-defect"
    changed_backend["results"]["duckdb"]["digest"] = "0" * 64
    assert not _receipt_row_is_admissible(
        changed_backend,
        backend="duckdb",
        current=current,
    )
    for disposition in ("evaluator-bug", "spec-gap", "unknown"):
        row = json.loads(json.dumps(base))
        row["results"]["duckdb"]["disposition"] = disposition
        assert not _receipt_row_is_admissible(row, backend="duckdb", current=current)
    deleted = json.loads(json.dumps(base))
    assert not _receipt_row_is_admissible(deleted, backend="duckdb", current=current)
    stale = json.loads(json.dumps(base))
    stale["results"]["duckdb"]["disposition"] = "oracle-defect"
    stale["model_sha256"] = "0" * 64
    assert not _receipt_row_is_admissible(stale, backend="duckdb", current=current)
    cross_backend = json.loads(json.dumps(base))
    cross_backend["results"]["souffle"]["disposition"] = "oracle-defect"
    assert not _receipt_row_is_admissible(
        cross_backend,
        backend="duckdb",
        current=current,
    )
    assert _receipt_row_is_admissible(
        cross_backend,
        backend="souffle",
        current={**current, "backend": "e" * 64},
    )


def test_duckdb_is_exact_pinned_and_absent_from_production() -> None:
    assert duckdb.__version__ == "1.5.5"
    project = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"duckdb==1.5.5"' in project
    assert "not derivation_oracle" in project
    checker_source = (REPO_ROOT / "src" / "gnd" / "checker.py").read_text(encoding="utf-8")
    assert "import duckdb" not in checker_source

