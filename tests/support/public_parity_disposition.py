from __future__ import annotations

from typing import Any

DISPOSITIONS = {"evaluator-bug", "encoding-bug", "spec-gap", "oracle-defect"}


BLOCKING_DISPOSITIONS = {"evaluator-bug", "spec-gap"}


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
