"""VG3 fixture cases (reviewed-vocabulary-growth): issue 222's two files and their variants.

Shared by tests/test_vg3_unattended_includes.py and by the capture of the
base outputs that T7 and T10 compare against
(``.gnd-planning/milestones/reviewed-vocabulary-growth/evidence/VG3-base/``).
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from support.cli_runner import run_main
from test_unattended_growth_guidance import _span

DOCUMENT = (
    "Each version belongs to one work.\n"
    "A work is a published piece; a version is one edition of it.\n"
    "An author writes works.\n"
)
SEED = "seed.orm.json"
ROOT = "root.orm.json"
DOC = "doc.md"


def span(quote: str) -> dict[str, Any]:
    return _span(DOCUMENT.encode(), quote)


def seed() -> dict[str, Any]:
    """Issue 222's seed: version 4, owner-reviewed, one explicit confirmed alethic constraint."""
    return {
        "version": 4,
        "model_id": "urn:example:seed@1",
        "source": {"kind": "text-conversation", "mode": "one-shot"},
        "object_types": [
            {"id": "work", "kind": "value", "name": "WorkKey", "primitive": "String"},
            {"id": "version", "kind": "value", "name": "VersionId", "primitive": "String"},
        ],
        "fact_types": [{
            "id": "work_has_version",
            "reading": "{WorkKey} has version {VersionId}",
            "roles": [{"object_type": "work", "role_name": "work"},
                      {"object_type": "version", "role_name": "version"}],
            "constraints": [{
                "id": "u1", "type": "uniqueness", "roles": ["version"], "source": "explicit",
                "status": "confirmed", "modality": "alethic", "rationale": "Each version belongs to one work.",
                "provenance": {"user_quote": "yes", "reviewed_in": "review-1"},
            }],
        }],
    }


def spanned_seed() -> dict[str, Any]:
    """Plan H30: included elements that pass U2-U8 against the root's document in 0.4.0."""
    doc = seed()
    for row in doc["object_types"]:
        quote = "A work is a published piece" if row["id"] == "work" else "a version is one edition of it"
        row["provenance"] = {"spans": [span(quote)]}
    fact = doc["fact_types"][0]
    fact["provenance"] = {"spans": [span("Each version belongs to one work")]}
    fact["constraints"] = [{
        "id": "u1", "type": "uniqueness", "roles": ["version"], "source": "llm-inferred",
        "status": "proposed", "modality": "deontic", "rationale": "One work per version.",
        "provenance": {"rationale_world_fact": "Each version belongs to one work.",
                       "spans": [span("Each version belongs to one work")]},
    }]
    return doc


def root(seed_raw: bytes, *, unattended: bool = True, **own: Any) -> dict[str, Any]:
    """Issue 222's root: version 5, unattended, one document, the include, empty own sections."""
    source: dict[str, Any] = {"kind": "prose"}
    if unattended:
        source.update(mode="unattended", reviewer="none",
                      documents=[{"sha256": hashlib.sha256(DOCUMENT.encode()).hexdigest(), "label": DOC}])
    else:
        source.update(mode="one-shot")
    doc = {"version": 5, "model_id": "urn:example:growth", "source": source,
           "includes": [{"id": "seed", "path": SEED, "sha256": hashlib.sha256(seed_raw).hexdigest()}],
           "object_types": [], "fact_types": []}
    doc.update(copy.deepcopy(own))
    return doc


def write(directory: Path, *, seed_doc: dict | None = None, unattended: bool = True, **own: Any) -> Path:
    """Write seed, root and document under DIRECTORY; return the root's path."""
    directory.mkdir(parents=True, exist_ok=True)
    seed_raw = json.dumps(seed() if seed_doc is None else seed_doc).encode()
    (directory / SEED).write_bytes(seed_raw)
    (directory / DOC).write_text(DOCUMENT, encoding="utf-8")
    path = directory / ROOT
    path.write_text(json.dumps(root(seed_raw, unattended=unattended, **own)))
    return path


def validate(model: Path, *args: str) -> tuple[int, str]:
    """(exit, stdout) of one in-process ``gnd validate``, the case directory written as <case>."""
    result = run_main(["validate", str(model), *args])
    return result.returncode, result.stdout.decode().replace(str(model.parent), "<case>")


#: The observations T7 and T10 hold equal to the base: name -> (writer, argv after the model).
def observations(directory: Path) -> dict[str, tuple[int, str]]:
    plain = write(directory / "plain", seed_doc=None, unattended=False)
    alone = directory / "alone"
    alone.mkdir(parents=True, exist_ok=True)
    (alone / SEED).write_text(json.dumps(seed()))
    (alone / DOC).write_text(DOCUMENT, encoding="utf-8")
    h30 = write(directory / "h30", seed_doc=spanned_seed())
    cases = {
        "seed-alone": (alone / SEED, ()),
        "seed-alone-document": (alone / SEED, ("--document", str(alone / DOC))),
        "include-root-without-mode": (plain, ()),
        "include-root-without-mode-document": (plain, ("--document", str(plain.parent / DOC))),
        "h30": (h30, ("--document", str(h30.parent / DOC), "--require-documents")),
        "h30-no-document": (h30, ()),
        "h30-require-only": (h30, ("--require-documents",)),
    }
    result = {}
    for name, (model, extra) in cases.items():
        for fmt in ("text", "json"):
            result[f"{name}:{fmt}"] = validate(model, *extra, "--format", fmt)
    return result
