"""Build the composition how-to's sources over src/gnd/examples/composition/model.orm.yaml.

    uv run python tools/build_composition_example.py src/gnd/examples/composition

Two contracts arrive as two documents. Each is written as a source folder
(document, population, version-2 anchor sidecar) of a composition directory:

    composition/           contract B says the party is based in Lyon, as A does
    composition-conflict/  the same, except that B says Zurich

contract-a names the party twice, so its party role carries two anchors.
Every digest is computed here; nothing is pasted. The anchors bind values to
ranges of text and claim nothing about truth. Deterministic: fixed texts,
canonical key order, two-space JSON.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import unicodedata
from pathlib import Path

from gnd.anchors import vocabulary_digest
from gnd.model import load_model

MODEL_ID = "composition-contracts"

DOCUMENT_A = """Agreement C-1

Agreement C-1 is entered into by Acme Corp. as the supplier.
The supplier, Acme Corp., is based in Lyon.
"""

DOCUMENT_B = """Addendum C-2

Addendum C-2 is signed by ACME CORP. as the supplier.
ACME CORP. is based in Lyon.
"""

# Each source also claims the derived answer its own document supports.
# Each anchor: (fact type, row, role, occurrence of the value in the document).
# The span is the line (one sentence) that holds that occurrence.
SOURCES = {
    "contract-a": {
        "document": DOCUMENT_A,
        "facts": {"contract_has_party": [{"contract": "C-1", "party": "Acme Corp."}],
                  "party_is_based_in_city": [{"party": "Acme Corp.", "city": "Lyon"}],
                  "contract_is_in_city": [{"contract": "C-1", "city": "Lyon"}]},
        "anchors": [("contract_has_party", 0, "party", 0), ("contract_has_party", 0, "party", 1),
                    ("party_is_based_in_city", 0, "city", 0)],
    },
    "contract-b": {
        "document": DOCUMENT_B,
        "facts": {"contract_has_party": [{"contract": "C-2", "party": "ACME CORP."}],
                  "party_is_based_in_city": [{"party": "ACME CORP.", "city": "Lyon"}],
                  "contract_is_in_city": [{"contract": "C-2", "city": "Lyon"}]},
        "anchors": [("contract_has_party", 0, "party", 0), ("party_is_based_in_city", 0, "city", 0)],
    },
}

MANIFEST = {
    "schema": "gnd-composition-manifest/1",
    "sources": ["contract-a", "contract-b"],
    "renamings": [
        {"source": "contract-b", "fact_type": "contract_has_party", "role": "party",
         "from": "ACME CORP.", "to": "Acme Corp."},
        {"source": "contract-b", "fact_type": "party_is_based_in_city", "role": "party",
         "from": "ACME CORP.", "to": "Acme Corp."},
    ],
    "deduplications": "identical-rows",
    "scope_tags": [{"source": "contract-a", "tag": "agreement"}, {"source": "contract-b", "tag": "addendum"}],
}

TARGETS = {"version": 1, "targets": [{"fact_type": "contract_is_in_city", "tuple": [
    {"primitive": "String", "value": "C-2"}, {"primitive": "String", "value": "Lyon"}]}]}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _dump(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _sentence_span(text: str, value: str, occurrence: int) -> tuple[int, int]:
    position = -1
    for _ in range(occurrence + 1):
        position = text.index(value, position + 1)
    start = text.rfind("\n", 0, position) + 1
    end = text.index("\n", position + len(value))
    return start, end


def _anchors(text: str, source: dict) -> list[dict]:
    anchors = []
    for fact_type, row, role, occurrence in source["anchors"]:
        roles = source["facts"][fact_type][row]
        start, end = _sentence_span(text, roles[role], occurrence)
        anchors.append({"fact_key": {"fact_type": fact_type, "roles": roles}, "role": role,
                        "span": {"start": start, "end": end}, "occurrence": occurrence,
                        "excerpt_sha256": _sha(text[start:end].encode("utf-8"))})
    return anchors


def write_source(folder: Path, source: dict, vocabulary: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    document = source["document"].encode("utf-8")
    (folder / "document.txt").write_bytes(document)
    population = _dump({"population": {"model": "model.orm.yaml", "model_id": MODEL_ID, "source": "agent-output",
                                       "covers": sorted(source["facts"])},
                        "instances": {}, "facts": source["facts"]})
    (folder / "population.json").write_bytes(population)
    text = unicodedata.normalize("NFC", source["document"])
    (folder / "population.json.anchors.json").write_bytes(_dump({
        "schema_version": 2, "population_sha256": _sha(population), "vocabulary_digest": vocabulary,
        "document_sha256": _sha(document), "anchors": _anchors(text, source)}))


def write_directory(directory: Path, sources: dict, vocabulary: str) -> None:
    if directory.exists():
        shutil.rmtree(directory)
    for source_id, source in sources.items():
        write_source(directory / source_id, source, vocabulary)
    (directory / "manifest.json").write_bytes(_dump(MANIFEST))


def conflict_sources() -> dict:
    sources = json.loads(json.dumps(SOURCES))
    contract_b = sources["contract-b"]
    contract_b["document"] = DOCUMENT_B.replace("Lyon", "Zurich")
    contract_b["facts"]["party_is_based_in_city"][0]["city"] = "Zurich"
    contract_b["facts"]["contract_is_in_city"][0]["city"] = "Zurich"
    contract_b["anchors"] = [tuple(anchor) for anchor in contract_b["anchors"]]
    return sources


def main(directory: str) -> None:
    root = Path(directory)
    vocabulary = vocabulary_digest(load_model(root / "model.orm.yaml"))
    write_directory(root / "composition", SOURCES, vocabulary)
    write_directory(root / "composition-conflict", conflict_sources(), vocabulary)
    (root / "targets.json").write_bytes(_dump(TARGETS))


if __name__ == "__main__":
    main(sys.argv[1])
