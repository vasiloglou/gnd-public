"""Deterministic large GND models for the Ossie size-bound tests (OB1)."""

from __future__ import annotations

import json
from pathlib import Path

#: Fact types in the generated model. Measured on 2026-11-24 (OB1): the source is
#: about 1.8 MB and its JSON loss report about 10.95 MB, above the 10 MiB default
#: output bound; the sidecar is about 7.3 MB and the ontology about 0.87 MB.
LARGE_FACT_TYPES = 5000

_MODALITY = {
    "source": "explicit",
    "status": "confirmed",
    "modality": "alethic",
    "provenance": {"user_quote": "A synthetic uniqueness witness."},
}


def large_model(fact_types: int = LARGE_FACT_TYPES) -> dict:
    """Two value types and ``fact_types`` functional binaries between them."""
    return {
        "version": 3,
        "source": {"generator": "tests/support/ossie_large.py"},
        "object_types": [
            {"id": "entry", "kind": "value", "name": "Entry", "primitive": "String"},
            {"id": "elapsed", "kind": "value", "name": "Elapsed", "primitive": "Integer"},
        ],
        "fact_types": [
            {
                "id": f"f{index:06d}",
                "reading": "{Entry} has {Elapsed}",
                "inverse_reading": "belongs to",
                "roles": [
                    {"object_type": "entry", "role_name": "entry"},
                    {"object_type": "elapsed", "role_name": "elapsed"},
                ],
                "constraints": [{"type": "uniqueness", "roles": ["elapsed"], **_MODALITY}],
            }
            for index in range(fact_types)
        ],
    }


def write_large_model(path: Path, fact_types: int = LARGE_FACT_TYPES) -> Path:
    path.write_text(json.dumps(large_model(fact_types), separators=(",", ":")))
    return path
