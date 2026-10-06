"""Public input and publication boundaries added while implementing the corpus."""
from __future__ import annotations

import copy
import os
from pathlib import Path

import pytest

BASICS = Path(__file__).parent / "fixtures" / "pyrel-oracle" / "basics.orm.yaml"

from gnd.export.pyrel_runtime import ExportInputError, admit_model, load_document, write_new


@pytest.mark.parametrize("change", ["kind", "reference", "role", "cycle"])
def test_malformed_consumed_model_fields_are_input_errors(change: str) -> None:
    document = copy.deepcopy(load_document(BASICS))
    if change == "kind":
        document["object_types"][0]["kind"] = []
    elif change == "reference":
        document["object_types"][0]["reference"]["value_type"] = []
    elif change == "role":
        document["fact_types"][0]["roles"][0]["object_type"] = []
    else:
        obj = document["object_types"][0]
        obj.pop("reference")
        obj.update(inherits_reference=True, subtype_of=[obj["id"]])
    with pytest.raises(ExportInputError):
        admit_model(document)


def test_recursive_yaml_alias_is_refused(tmp_path: Path) -> None:
    source = tmp_path / "cycle.yaml"
    source.write_text("loop: &loop [*loop]\n")
    with pytest.raises(ExportInputError, match="recursive"):
        load_document(source)


def test_nonregular_input_refused_without_opening(tmp_path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO probe requires POSIX")
    source = tmp_path / "pipe"
    os.mkfifo(source)
    with pytest.raises(ExportInputError, match="regular"):
        load_document(source)


def test_failed_write_removes_own_partial_file(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "program.py"
    original = Path.open

    class BrokenWriter:
        def __init__(self, handle):
            self.handle = handle

        def fileno(self):
            return self.handle.fileno()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.handle.close()

        def write(self, text):
            self.handle.write(text[:4])
            self.handle.flush()
            raise OSError("injected write failure")

    def broken_open(path, *args, **kwargs):
        handle = original(path, *args, **kwargs)
        return BrokenWriter(handle) if path == target and args == ("x",) else handle

    monkeypatch.setattr(Path, "open", broken_open)
    with pytest.raises(OSError, match="injected"):
        write_new(target, "not all bytes can be written")
    assert not target.exists()


def test_require_output_failure_is_not_a_missing_named_connection(tmp_path: Path, monkeypatch) -> None:
    from gnd.export import pyrel_runtime as runtime

    monkeypatch.setattr(runtime, "MODEL_TEXT", BASICS.read_text())
    monkeypatch.setattr(runtime, "MODEL_NAME", "model.yaml")
    monkeypatch.setattr(runtime, "EXPORT_CONFIG", {"duckdb_path": ":memory:", "connection": "named"})
    population = BASICS.parent / "population.basics_pass.yaml"
    assert runtime.program_main([str(population), "--out", str(tmp_path / "missing/report.json"),
                                 "--mode", "require"]) == 70


@pytest.mark.parametrize("change", ["mandatory-number", "uniqueness-number", "unknown-role", "reference-mode"])
def test_review_malformed_consumed_fields_are_rejected(change: str) -> None:
    document = copy.deepcopy(load_document(BASICS))
    if change == "reference-mode":
        document["object_types"][0]["reference"]["mode"] = "bogus"
    else:
        constraint = {
            "mandatory-number": {"type": "mandatory", "role": 42},
            "uniqueness-number": {"type": "uniqueness", "roles": [42]},
            "unknown-role": {"type": "mandatory", "role": "absent"},
        }[change]
        document["fact_types"][0]["constraints"] = [constraint]
    with pytest.raises(ExportInputError):
        admit_model(document)


@pytest.mark.parametrize("primitive,value", [
    ("Date", "not-a-date"), ("Date", "2026-99-99"),
    ("Date", "2026-02-29"), ("Date", "20260904"),
    ("DateTime", "not-a-datetime"), ("DateTime", "2026-09-04T25:00"),
    ("DateTime", "2026-09-04"),
    ("DateTime", "2026-09-04 12:30-0400"), ("DateTime", "2026-09-04t12:30z"),
])
def test_review_invalid_temporal_population_is_rejected(primitive, value) -> None:
    from gnd.export.pyrel_runtime import admit_population

    index = admit_model({"object_types": [{"id": "temporal", "kind": "value", "primitive": primitive}],
                         "fact_types": []})
    with pytest.raises(ExportInputError):
        admit_population({"instances": {"temporal": [value]}}, index)


@pytest.mark.parametrize("primitive,value", [
    ("Date", "2024-02-29"), ("DateTime", "2026-09-04T12:30:01.25Z"),
    ("DateTime", "2026-09-04T12:30-04:00"),
])
def test_valid_temporal_population_remains_admitted(primitive, value) -> None:
    from gnd.export.pyrel_runtime import admit_population

    index = admit_model({"object_types": [{"id": "temporal", "kind": "value", "primitive": primitive}],
                         "fact_types": []})
    admit_population({"instances": {"temporal": [value]}}, index)
