"""Every fixture and example model, for the tests that run over all of them (OB3-Q6)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RMAP_CASES = ROOT / "tests/fixtures/rmap/cases"


def all_model_paths() -> list[Path]:
    """Every `*.orm.yaml` and `*.orm.json` under src/gnd and tests/fixtures, and the Rmap
    corpus models, which are named `model.yaml` (OB2 A13, A14)."""
    found: set[Path] = set()
    for base in (ROOT / "src/gnd", ROOT / "tests/fixtures"):
        for pattern in ("*.orm.yaml", "*.orm.json"):
            found.update(base.rglob(pattern))
    found.update(RMAP_CASES.glob("*/model.yaml"))
    return sorted(found)
