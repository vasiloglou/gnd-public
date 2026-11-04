"""MG1 parity capture (spec T7): render every corpus model loaded and by path.

Run from the repository root:
    uv run python .gnd-planning/milestones/model-growth-guardrails/evidence/MG1/capture_parity.py OUT.json
Writes, per corpus model, the SHA-256 of render_model_verbalization for the
loaded Model and for the path argument, or the exception class name.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from gnd.model import load_model
from gnd.model_verbalization import render_model_verbalization


def _digest(argument: object) -> str:
    try:
        return hashlib.sha256(render_model_verbalization(argument).encode("utf-8")).hexdigest()
    except Exception as error:  # noqa: BLE001 -- recorded, not raised
        return f"error:{type(error).__name__}"


def main(out: str) -> None:
    roots = [Path("src/gnd/examples"), Path("tests")]
    paths = sorted({p for root in roots for pattern in ("*.orm.yaml", "*.orm.json") for p in root.rglob(pattern)})
    rows = {}
    for path in paths:
        try:
            loaded = load_model(str(path))
        except Exception:  # noqa: BLE001 -- not a valid model; outside the corpus
            continue
        rows[str(path)] = {"loaded": _digest(loaded), "path": _digest(str(path))}
    Path(out).write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    crashed = sum(1 for row in rows.values() if row["path"].startswith("error:"))
    print(f"models={len(rows)} path_errors={crashed}")


if __name__ == "__main__":
    main(sys.argv[1])
