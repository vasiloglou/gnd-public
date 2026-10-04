"""Original hostile evidence reader and nonobject cache refusal only."""
from __future__ import annotations

import atexit
import json
import math
import tempfile
from pathlib import Path
from typing import Any

_TEMPORARY = tempfile.TemporaryDirectory(prefix="gnd-public-phase5-units-")
ROOT = Path(_TEMPORARY.name).resolve()
atexit.register(_TEMPORARY.cleanup)


def _unpublished_positive_cache(*_args, **_kwargs):
    raise RuntimeError("Positive correspondence cache validation is outside this runtime-only support.")

currency_sha256 = _unpublished_positive_cache
sha = _unpublished_positive_cache
RUNNER = ROOT / "unpublished-correspondence-runner"

class CorrespondenceError(ValueError):
    """A closed Phase 5 gate did not hold."""

def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise CorrespondenceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

def load_json(path: Path, *, limit: int = 10 * 1024 * 1024) -> Any:
    if path.stat().st_size > limit:
        raise CorrespondenceError(f"evidence exceeds read limit: {path}")
    raw = path.read_bytes()

    def integer(value: str) -> int:
        number = int(value)
        if not -(2**63) <= number <= 2**63 - 1:
            raise CorrespondenceError("evidence integer exceeds signed 64-bit range")
        return number

    def floating(value: str) -> float:
        number = float(value)
        if not math.isfinite(number):
            raise CorrespondenceError(f"nonfinite JSON value: {value}")
        return number

    try:
        value = json.loads(
            raw,
            object_pairs_hook=pairs,
            parse_int=integer,
            parse_float=floating,
            parse_constant=lambda value: (_ for _ in ()).throw(
                CorrespondenceError(f"nonfinite JSON value: {value}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CorrespondenceError(f"invalid JSON evidence: {path}: {error}") from error

    def depth(item: Any, level: int = 0) -> None:
        if level > 32:
            raise CorrespondenceError("evidence nesting exceeds 32 levels")
        if isinstance(item, dict):
            for child in item.values():
                depth(child, level + 1)
        elif isinstance(item, list):
            for child in item:
                depth(child, level + 1)

    depth(value)
    return value

def _cached(path: Path) -> bool:
    """Reuse only disposable receipts bound to the complete current input root."""
    if not path.is_file() or path.resolve().is_relative_to(ROOT):
        return False
    try:
        receipt = load_json(path)
        if not isinstance(receipt, dict):
            return False
        return (
            receipt.get("status") == "passed"
            and receipt.get("currency_sha256") == currency_sha256()
            and receipt.get("runner", {}).get("sha256") == sha(RUNNER)
        )
    except (AttributeError, KeyError, OSError, TypeError, CorrespondenceError):
        return False
