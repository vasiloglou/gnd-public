"""Exact legacy derived-field mutation guards over an actual current drift observation.

Only the legacy reader wire envelope is reconstructed. This fixture is no
historical publication receipt; its conformance payload is produced live by GND.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from test_model_evolution import _case, _tree_sha256

REPO_ROOT=Path(__file__).resolve().parents[1]
RETAINED_RECORD=Path("record.json")
_LEGACY_RECORD: dict[str,Any]={}


def _pre_migration_document(path: Path) -> dict[str,Any]:
    assert path==RETAINED_RECORD
    return json.loads(json.dumps(_LEGACY_RECORD))


@pytest.fixture(autouse=True)
def _bind_actual_drift(tmp_path: Path,monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.artifacts import canonical_json_bytes
    from gnd.codegen.emit import emit_project, write_project
    from gnd.codegen.manifest import build_manifest, read_manifest, render_manifest
    from gnd.conformance.service import run_conformance
    from gnd.evolve import (
        canonical_sha256,
        conformance_payload_sha256,
        read_evolution_record_document,
    )

    # Fully reviewed generic input; codegen emits files and conformance reads them,
    # with no generated-code execution, native tool or external service.
    row=_case("evolution-clean-and-drift-linked-conformance")
    model_path=tmp_path/"model.orm.yaml"
    model_path.write_text(row["inputs"]["candidate_model"]["text"],encoding="utf-8")
    assert hashlib.sha256(model_path.read_bytes()).hexdigest()==row["inputs"]["candidate_model"]["sha256"]
    project_root=tmp_path/"project"
    generated=emit_project(__import__("gnd.model",fromlist=["load_model"]).load_model(model_path),str(model_path),skill_name="project")
    write_project(generated,str(project_root),manifest_text=render_manifest(build_manifest(generated,str(model_path))))
    clean=run_conformance(model_path,project_root)
    assert clean.exit_code==0
    manifest=read_manifest(project_root/".gnd-codegen.json")
    derived=next(item for item in manifest.files if item.ownership=="derived")
    derived_path=project_root/derived.relpath
    derived_path.write_bytes(derived_path.read_bytes()+b"\n# deliberate drift\n")
    before=_tree_sha256(project_root)
    drift=run_conformance(model_path,project_root)
    after=_tree_sha256(project_root)
    assert drift.exit_code==13
    assert before==after
    assert any(item["findings"]>0 for item in drift.payload["assertions"])

    packed=(REPO_ROOT/"tests/fixtures/public-legacy-evolution/workspace.json.gz").read_bytes()
    assert len(packed)<=65536
    assert hashlib.sha256(packed).hexdigest()=='a597a55c5ff0e73538aadde9bd0bbfa4f70a355426c213560436a876a4540f6b'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw=stream.read(524289)
    assert len(raw)<=524288
    members=json.loads(raw)
    records={}
    for version in [1,2]:
        member=members[f"graphs/v{version}/record.json"]
        data=base64.b64decode(member["raw_base64"],validate=True)
        assert hashlib.sha256(data).hexdigest()==member["sha256"]
        record=json.loads(data)
        leaf=record["linked_conformance"][0]
        leaf["payload"]=drift.payload
        leaf["payload_sha256"]=conformance_payload_sha256(drift.payload)
        leaf["exit_code"]=13
        for key in ["expected_tree_sha256","before_tree_sha256","after_tree_sha256"]:
            leaf[key]=before
        if version==1:
            leaf["root"]="project"
        else:
            leaf["locator"]["path"]="project"
        record["conformance_exit_code"]=13
        record["published_with_drift"]=True
        record["record_identity_sha256"]=canonical_sha256({k:v for k,v in record.items() if k!="record_identity_sha256"})
        assert read_evolution_record_document(record).model_dump(mode="json")==record
        records[version]=record
    path=tmp_path/"record.json"
    path.write_bytes(canonical_json_bytes(records[2]))
    monkeypatch.setitem(globals(),"RETAINED_RECORD",path)
    monkeypatch.setitem(globals(),"_LEGACY_RECORD",records[1])


@pytest.mark.parametrize("schema_version", [1, 2])
@pytest.mark.parametrize(
    "mutation",
    ["expected-tree", "before-tree", "after-tree", "linked-exit", "aggregate", "drift"],
)
def test_record_readers_reject_recomputed_inconsistent_derived_fields(
    schema_version: int,
    mutation: str,
) -> None:
    from gnd.evolve import canonical_sha256, read_evolution_record_document

    record = (
        _pre_migration_document(RETAINED_RECORD)
        if schema_version == 1
        else json.loads(RETAINED_RECORD.read_text(encoding="utf-8"))
    )
    linked = record["linked_conformance"][0]
    if mutation == "expected-tree":
        linked["expected_tree_sha256"] = "0" * 64
    elif mutation == "before-tree":
        linked["before_tree_sha256"] = "0" * 64
    elif mutation == "after-tree":
        linked["after_tree_sha256"] = "0" * 64
    elif mutation == "linked-exit":
        linked["exit_code"] = 0
    elif mutation == "aggregate":
        record["conformance_exit_code"] = 0
        record["published_with_drift"] = False
    else:
        record["published_with_drift"] = False
    record["record_identity_sha256"] = canonical_sha256(
        {key: value for key, value in record.items() if key != "record_identity_sha256"}
    )

    with pytest.raises(
        ValidationError,
        match="tree equality|precedence|published_with_drift",
    ):
        read_evolution_record_document(record)
