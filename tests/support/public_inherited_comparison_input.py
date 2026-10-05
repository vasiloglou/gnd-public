"""Independently synthetic comparison input; no retained release or proof claim."""
from pathlib import Path

from support.public_migration import strict_json


def retained(family):
    if family != "phase5":
        raise ValueError("unknown synthetic comparison family")
    path = Path(__file__).resolve().parents[1] / "fixtures/public-inherited-comparison.json"
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    if len(raw) > 1048576:
        raise ValueError("oversize synthetic comparison input")
    return strict_json(raw.decode("utf-8"))
