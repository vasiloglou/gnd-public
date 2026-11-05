"""The packaged composition example stays consistent with its model.

Every sidecar binds the model's vocabulary digest and raw-byte digests of its
population and document; rebuilding must reproduce the shipped bytes, so an
edit without a rebuild fails here rather than in the how-to.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/composition"
BUILD = ROOT / "tools/build_composition_example.py"
GENERATED = ("composition", "composition-conflict", "targets.json")


def _files(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for name in GENERATED
                  for path in ([root / name] if (root / name).is_file() else (root / name).rglob("*"))
                  if path.is_file())


def test_sources_rebuild_byte_identically(tmp_path: Path) -> None:
    shutil.copy2(EXAMPLE / "model.orm.yaml", tmp_path / "model.orm.yaml")
    subprocess.run([sys.executable, str(BUILD), str(tmp_path)], check=True)
    assert _files(tmp_path) == _files(EXAMPLE)
    for name in _files(EXAMPLE):
        assert (tmp_path / name).read_bytes() == (EXAMPLE / name).read_bytes(), name


def test_the_model_validates_and_both_directories_compose() -> None:
    from gnd import api

    model = str(EXAMPLE / "model.orm.yaml")
    assert api.validate(model)["exit_code"] == 0
    for directory in ("composition", "composition-conflict"):
        assert api.compose(model, str(EXAMPLE / directory))["exit_code"] == 0, directory


def test_the_witness_reaches_a_span_in_each_document(tmp_path: Path) -> None:
    # Close review: follow every base node's sources through their own
    # sidecars and check the answer reaches both documents.
    import json

    from gnd import api
    from gnd.artifacts import canonical_json_bytes

    model = str(EXAMPLE / "model.orm.yaml")
    directory = EXAMPLE / "composition"
    composed = api.compose(model, str(directory))
    population, record = tmp_path / "composed.population.json", tmp_path / "composition.json"
    population.write_bytes(canonical_json_bytes(composed["population"]))
    record.write_bytes(canonical_json_bytes(composed["record"]))
    result = api.witness(model, str(population), str(EXAMPLE / "targets.json"), composition=str(record))
    assert result["exit_code"] == 0
    reached = {}
    for node in result["certificate"]["nodes"]:
        for entry in node.get("sources", []):
            folder = directory / entry["source"]
            row = json.loads((folder / "population.json").read_text())["facts"][entry["fact_type"]][entry["fact_index"]]
            anchors = json.loads((folder / "population.json.anchors.json").read_text())["anchors"]
            text = (folder / "document.txt").read_text()
            spans = [text[a["span"]["start"]:a["span"]["end"]] for a in anchors if a["fact_key"]["roles"] == row]
            assert spans, entry
            reached.setdefault(entry["source"], []).extend(spans)
    assert sorted(reached) == ["contract-a", "contract-b"]
    assert any("ACME CORP." in span for span in reached["contract-b"])
