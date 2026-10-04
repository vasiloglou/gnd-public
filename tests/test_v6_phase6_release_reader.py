"""A synthetic trusted release exercises authentication guards, not a solver claim."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from gnd.assurance_evidence import (
    RUNTIME_DEPENDENCIES,
    _load,
    production_roster,
    roster_digest,
    runtime_identity,
)
from gnd.semantic_registry import REGISTRY

SOURCE = Path(__file__).resolve().parents[1] / "src/gnd"


def synthetic_release(tmp_path):
    package = tmp_path / "gnd"
    for entry in production_roster(SOURCE):
        relative = Path(entry["path"]).relative_to("src/gnd")
        destination = package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / relative, destination)
    bundle = package / "_assurance_evidence"
    bundle.mkdir()
    files = [
        {"role": "schema" if row["path"].endswith(".schema.json") else "source", "address": row}
        for row in production_roster(package)
    ]

    def add(name, role, data):
        (bundle / name).write_bytes(data)
        address = {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        files.append({"role": role, "address": address})
        return address

    scope = add(
        "scope.json",
        "scope",
        json.dumps({"scope_ids": sorted(row.scope_id for row in REGISTRY)}).encode(),
    )
    semantics = add("semantics.md", "semantics", b"Synthetic release, no proved rows.\n")
    tools = add("tools.json", "toolchain", b'{"synthetic":true}')
    result = add("result.json", "proof-result", b'{"status":"passed","synthetic":true}')
    excluded = sorted(
        row.scope_id
        for row in REGISTRY
        if row.family == "oracle-verdict"
        or (row.surface == "experiment-feedback" and row.family in {"attempt", "case", "contract"})
    )
    manifest = {
        "schema_version": 1,
        "scope_digest": scope["sha256"],
        "semantics_digest": semantics["sha256"],
        "toolchain_digest": tools["sha256"],
        "proof_digest": roster_digest([result]),
        "production_roster_digest": roster_digest(production_roster(package)),
        "runtime_domain": runtime_identity(list(RUNTIME_DEPENDENCIES)),
        "files": files,
        "excluded_policy_scope_ids": excluded,
        "assumptions": ["synthetic-release-test"],
        "rows": [
            {
                "scope_id": row.scope_id,
                "status": "excluded" if row.scope_id in excluded else "uncovered",
                "normative": semantics,
                "production_owners": [row.production_owner],
                "provider": None,
                "theorems": [],
                "proof_inputs_digest": None,
                "result_digest": None,
                "assumptions": [],
            }
            for row in REGISTRY
        ],
    }
    publish(package, manifest)
    return package, manifest


def publish(package, manifest):
    raw = json.dumps(manifest, sort_keys=True).encode()
    (package / "_assurance_evidence/manifest.json").write_bytes(raw)
    (package / "_assurance_evidence/anchor.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "release_id": "synthetic-test-only",
                "manifest_sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    )


def test_a_current_complete_release_can_authenticate_without_claiming_coverage(tmp_path):
    package, _ = synthetic_release(tmp_path)
    result = _load(package)
    assert result.available and result.digests is not None
    assert not result.covered_scope_ids
    assert len(result.declared_scope_ids) == len(REGISTRY)


@pytest.mark.parametrize(
    "mutation",
    [
        "source",
        "missing-source",
        "omitted-roster",
        "extra-source",
        "runtime",
        "proof-digest",
        "scope-digest",
        "claim-without-proof",
    ],
)
def test_dirty_release_is_rejected_at_its_identity_boundary(tmp_path, mutation):
    package, manifest = synthetic_release(tmp_path)
    if mutation == "source":
        with (package / "assurance.py").open("a") as stream:
            stream.write("\n# changed\n")
    elif mutation == "missing-source":
        (package / "assurance.py").unlink()
    elif mutation == "omitted-roster":
        manifest["files"] = [
            r for r in manifest["files"] if r["address"]["path"] != "src/gnd/assurance.py"
        ]
    elif mutation == "extra-source":
        (package / "added.py").write_text("extra = True\n")
    elif mutation == "runtime":
        manifest["runtime_domain"]["dependencies"] = []
    elif mutation == "claim-without-proof":
        row = next(row for row in manifest["rows"] if row["status"] == "uncovered")
        row.update(
            status="proved",
            provider="nagini",
            theorems=["invented"],
            proof_inputs_digest="a" * 64,
            result_digest="b" * 64,
        )
    else:
        manifest[mutation.replace("-", "_")] = "a" * 64
    publish(package, manifest)
    with pytest.raises((OSError, ValueError)):
        _load(package)


@pytest.mark.parametrize("kind", ["file", "symlink-directory"])
def test_unlisted_bundle_content_is_not_a_hashing_exemption(tmp_path, kind):
    package, _ = synthetic_release(tmp_path)
    extra = package / "_assurance_evidence/unlisted"
    if kind == "file":
        extra.write_text("not in the approved publication DAG")
    else:
        extra.symlink_to(package / "_assurance_evidence", target_is_directory=True)
    with pytest.raises(ValueError, match="bundle"):
        _load(package)


def test_matching_artifact_hashes_do_not_establish_a_proof_input_graph(tmp_path):
    package, manifest = synthetic_release(tmp_path)
    data = b"{}"
    (package / "_assurance_evidence/empty-inputs.json").write_bytes(data)
    input_address = {
        "path": "empty-inputs.json",
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    manifest["files"].append({"role": "proof-source", "address": input_address})
    result_address = next(
        row["address"] for row in manifest["files"] if row["role"] == "proof-result"
    )
    row = next(row for row in manifest["rows"] if row["status"] == "uncovered")
    row.update(
        status="proved",
        provider="nagini",
        theorems=["invented"],
        proof_inputs_digest=input_address["sha256"],
        result_digest=result_address["sha256"],
    )
    publish(package, manifest)
    with pytest.raises(ValueError, match="proof"):
        _load(package)
