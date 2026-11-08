"""How expected/ was derived (run from the corpus directory, with the ROF3 base source importable).

The identity is defined over the LOADED model (the spec's section 6, M3 item 1), so
this script loads each model with gnd's own loader and takes ``model_dump()``. Everything
after that is written here from the definition, without gnd's canonical helpers
(``gnd.values.canonical``, ``gnd.artifacts.canonical_json_bytes``) or the function ROF3 adds:

- version 2 (no reference populations): {"identity_version": 2, "model": <dump without
  warnings, operations, reference_populations>};
- version 1 (reference-bearing): {"identity_version": 1, "model": <dump without warnings
  and reference_populations; operations kept>, "reference_populations": <declarations,
  each with its fact_types sorted, sorted by id>};
- bytes: dates as ISO text, then json.dumps(sort_keys=True, separators=(",", ":"),
  ensure_ascii=False, allow_nan=False) + "\\n", UTF-8 (a string that is not encodable is a
  refusal);
- digest: "sha256:" + hex.

The legacy digest pinned in ``<case>.legacy`` is the existing ``gnd.values.model_digest``
(it is not new code; ROF3 must leave it unchanged).
"""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

from gnd.model import load_model
from gnd.values import model_digest as legacy_digest

CASES = {
    "plain-small": "models/plain-small.orm.yaml",
    "floats": "models/floats.orm.yaml",
    "float-spellings": "models/float-spellings.orm.json",
    "negative-zero": "models/negative-zero.orm.json",
    "dates-and-text": "models/dates-and-text.orm.yaml",
    "operations-a": "models/operations-a.orm.yaml",
    "operations-b": "models/operations-b.orm.yaml",
    "reference": "models/reference/model.orm.yaml",
    "reference-operations": "models/reference-operations/model.orm.yaml",
    "surrogate": "models/surrogate.orm.json",
}


def plain(value):
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    return value


def envelope(model) -> dict:
    if model.reference_populations:
        declarations = [dict(d, fact_types=sorted(d["fact_types"])) for d in model.reference_populations]
        return {
            "identity_version": 1,
            "model": plain(model.model_dump(exclude={"warnings", "reference_populations"})),
            "reference_populations": sorted(declarations, key=lambda d: d["id"]),
        }
    return {
        "identity_version": 2,
        "model": plain(model.model_dump(exclude={"warnings", "operations", "reference_populations"})),
    }


def main() -> None:
    out = Path("expected")
    summary = {}
    for case, path in CASES.items():
        model = load_model(path)
        document = envelope(model)
        (out / f"{case}.legacy").write_text(legacy_digest(model) + "\n")
        text = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        try:
            data = (text + "\n").encode("utf-8")
        except UnicodeEncodeError:
            summary[case] = {"model": path, "identity": None, "refusal": "model:identity-unrepresentable"}
            continue
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        (out / f"{case}.identity.json").write_bytes(data)
        (out / f"{case}.digest").write_text(digest + "\n")
        (out / f"{case}.stdout.txt").write_bytes(
            f"MODEL IDENTITY {digest} (identity_version {document['identity_version']})\n".encode() + data
        )
        summary[case] = {"model": path, "identity": digest, "identity_version": document["identity_version"]}
    (out / "vectors.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")


main()
