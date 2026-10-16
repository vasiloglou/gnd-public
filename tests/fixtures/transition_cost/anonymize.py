"""Import the reporter's issue #24 workload bundle with the approved neutral transform.

Usage: python anonymize.py SOURCE_DIR [--out DIR]

The transform (TP0 spec D7) overwrites fields rather than matching strings, so this file
spells no downstream name:

1. ``model_id`` becomes ``urn:gnd-fixture:steps@1`` in the model and every population.
2. Every provenance ``user_note`` becomes ``Sealed step programs.``
3. Each step document's ``model`` becomes ``steps.orm.json``; its ``model_digest`` and
   ``operations_digest`` are verified against the source model first, then recomputed.

It prints a JSON map of every file's SHA-256 before and after, for PROVENANCE.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from gnd.model import load_model
from gnd.transition import operations_digest, transition_model_identity

MODEL_ID = "urn:gnd-fixture:steps@1"
USER_NOTE = "Sealed step programs."
MODEL_FILE = "steps.orm.json"


def _neutral(value):
    if isinstance(value, dict):
        return {
            key: (USER_NOTE if key == "user_note" else _neutral(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_neutral(item) for item in value]
    return value


def _write(path: Path, document) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    source, out = args.source.resolve(), args.out.resolve()
    names = sorted(p.name for p in source.glob("*.json"))
    before = {name: _sha(source / name) for name in names}

    original = load_model(source / MODEL_FILE)
    expected = (transition_model_identity(original), operations_digest(original.operations))
    for name in names:
        if name.endswith("-steps.json"):
            document = json.loads((source / name).read_text(encoding="utf-8"))
            found = (document["model_digest"], document["operations_digest"])
            if found != expected:
                raise SystemExit(f"{name}: digests do not match the source model")

    for name in names:
        document = _neutral(json.loads((source / name).read_text(encoding="utf-8")))
        if name == MODEL_FILE:
            document["model_id"] = MODEL_ID
        elif "population" in document:
            document["population"]["model_id"] = MODEL_ID
        _write(out / name, document)

    model = load_model(out / MODEL_FILE)
    digests = {
        "model_digest": transition_model_identity(model),
        "operations_digest": operations_digest(model.operations),
    }
    for name in names:
        if name.endswith("-steps.json"):
            document = json.loads((out / name).read_text(encoding="utf-8"))
            document.update(model=MODEL_FILE, **digests)
            _write(out / name, document)

    after = {name: _sha(out / name) for name in names}
    print(json.dumps({"before": before, "after": after}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
