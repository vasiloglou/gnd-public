"""Current model identity rejection and exact frozen sibling semantics."""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

import test_public_book_runtime as _runtime
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

from gnd.report import legacy_report_projection, load_report_schema

JsonObject = dict[str, Any]
REPORT_VALIDATOR = Draft202012Validator(load_report_schema())
def _public_identity_workspace():
    archive = Path(__file__).parent / "fixtures/public-book-identity/workspace.json.gz"
    assert archive.is_file() and not archive.is_symlink()
    with archive.open("rb") as stream: packed = stream.read(16 * 1024 + 1)
    assert len(packed) <= 16 * 1024 and hashlib.sha256(packed).hexdigest() == '7c0b80e350018b713bc59959502f5b9ddb623a30acab6f30651e671a0758adf9'
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream: expanded = stream.read(32 * 1024 + 1)
    assert len(expanded) <= 32 * 1024
    document = json.loads(expanded)
    assert document["schema_version"] == 1 and len(document["members"]) == 3
    holder = tempfile.TemporaryDirectory(prefix="gnd-public-book-identity-")
    root = Path(holder.name)
    members = {}
    for name, member in document["members"].items():
        relative = PurePosixPath(name)
        assert relative.parts and not relative.is_absolute() and ".." not in relative.parts and name == relative.as_posix()
        raw = base64.b64decode(member["data"], validate=True)
        assert len(raw) <= 16 * 1024 and hashlib.sha256(raw).hexdigest() == member["sha256"]
        target = root.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        members[name] = raw
    current = _runtime._MEMBERS["examples/bookrec/model.orm.yaml"]
    assert len(current) <= 64 * 1024
    destination = root / "examples/bookrec/model.orm.yaml"
    destination.write_bytes(current)
    return holder, root, members
_HOLDER, REPO_ROOT, _FROZEN = _public_identity_workspace()
MODEL_PATH = REPO_ROOT / "examples/bookrec/model.orm.yaml"
P001_HISTORY_COMMIT = "8caad962ba6c2d613a1a9ed295f912aecfb7fc98"
P001_RECORD_RELPATH = "examples/bookrec/records/p001-promote-genre"
P001_PROMOTION_POPULATION_RELPATH = "examples/bookrec/populations/promotion.population.json"
POST_PROMOTION_MODEL_PATH = REPO_ROOT / P001_RECORD_RELPATH / "candidate.orm.yaml"
def _git_blob(commit: str, relative: str) -> bytes:
    assert commit == P001_HISTORY_COMMIT and relative in _FROZEN
    return _FROZEN[relative]

def _json_object_from_bytes(value: bytes, *, label: str) -> JsonObject:
    """Parse one pinned JSON object without consulting a moving workspace path."""
    parsed = json.loads(value)
    assert isinstance(parsed, dict), label
    return parsed


def _p001_frozen_blob(relative: str) -> bytes:
    """Return a p001-era blob and prove its retained workspace copy is unchanged."""
    pinned = _git_blob(P001_HISTORY_COMMIT, relative)
    assert (REPO_ROOT / relative).read_bytes() == pinned, relative
    return pinned


def _p001_frozen_json(relative: str) -> JsonObject:
    """Read retained p001 evidence only after binding it to the history commit."""
    return _json_object_from_bytes(_p001_frozen_blob(relative), label=relative)


def _read_model(path: Path = MODEL_PATH) -> JsonObject:
    """Read a model as the YAML mapping used by the independent helper."""
    value = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _run_gnd_json(*args: str) -> tuple[int, JsonObject]:
    """Run GND through the required subprocess interface and parse stdout."""
    completed = subprocess.run(
        [sys.executable, "-m", "gnd", *args, "--format", "json"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert completed.stdout, completed.stderr
    payload = json.loads(completed.stdout)
    assert isinstance(payload, dict)
    return completed.returncode, payload


def test_frozen_at1_population_is_refused_by_at2_before_semantics(
    tmp_path: Path,
) -> None:
    """P4-ID-2. The opaque identity gate runs before semantic evaluation.

    The same frozen population has a retained semantic failure with its @1
    sibling. Pairing it with today's @2 model must instead emit only the exact
    model-id mismatch at band 3: no verdict, derivation, or coverage result may
    imply that semantic evaluation ran first.
    """
    frozen_population = tmp_path / "promotion.population.json"
    frozen_bytes = _git_blob(P001_HISTORY_COMMIT, P001_PROMOTION_POPULATION_RELPATH)
    frozen_population.write_bytes(frozen_bytes)
    frozen = _json_object_from_bytes(frozen_bytes, label="frozen p001 population")
    assert frozen["population"]["model_id"] == "urn:gnd-example:bookrec@1"
    assert _read_model(MODEL_PATH)["model_id"] == "urn:gnd-example:bookrec@2"

    mismatch_exit, mismatch = _run_gnd_json(
        "check",
        str(MODEL_PATH),
        str(frozen_population),
    )
    REPORT_VALIDATOR.validate(mismatch)
    assert mismatch_exit == 3
    # A current-behaviour assertion: exit 3 fires after the model loads, so the
    # payload is on the bound wire and names the model that refused.
    assert legacy_report_projection(mismatch, 6) == {
        "schema_version": 6,
        "model_digest": (
            "sha256:df8a5c9319072b4c156fb92aab28f0ea465247afe7ebcde363dd81743fa8e175"
        ),
        "tool": "gnd",
        "command": "check",
        "outcome": "ill_formed",
        "exit_code": 3,
        "acceptance_ready": False,
        "model": str(MODEL_PATH),
        "population": str(frozen_population),
        "counts": {
            "pass": 0,
            "fail": 0,
            "warning": 0,
            "unchecked": 0,
            "vacuous": 0,
        },
        "verdicts": [],
        "derivations": [],
        "coverage": {},
        "extraction": {},
        "issues": [
            {
                "path": "$.population.model_id",
                "message": (
                    "This population declares model_id "
                    "'urn:gnd-example:bookrec@1', but the model declares "
                    "'urn:gnd-example:bookrec@2' — it was written for a "
                    "different model (population:model-id-mismatch)."
                ),
                "rule_id": "population:model-id-mismatch",
                "severity": "error",
            }
        ],
        "issues_total": 1,
        "issues_truncated": False,
        "warnings": [],
        "error": None,
        "transition": None,
    }

    frozen_model_relative = f"{P001_RECORD_RELPATH}/candidate.orm.yaml"
    assert POST_PROMOTION_MODEL_PATH.read_bytes() == _p001_frozen_blob(
        frozen_model_relative
    )
    assert _read_model(POST_PROMOTION_MODEL_PATH)["model_id"] == (
        "urn:gnd-example:bookrec@1"
    )
    sibling_exit, sibling = _run_gnd_json(
        "check",
        str(POST_PROMOTION_MODEL_PATH),
        str(frozen_population),
    )
    REPORT_VALIDATOR.validate(sibling)
    historical = _p001_frozen_json(
        "examples/bookrec/evidence/post-promotion-check.json"
    )
    historical["model"] = str(POST_PROMOTION_MODEL_PATH)
    historical["population"] = str(frozen_population)
    assert sibling_exit == 1
    # Historical evidence stays the pin; the current wire is projected to v3.
    bound = legacy_report_projection(sibling, 3)
    assert bound == historical
    assert sibling["counts"] == {
        "pass": 5,
        "fail": 1,
        "warning": 0,
        "unchecked": 0,
        "vacuous": 0,
    }
    assert [
        verdict["constraint_ref"]
        for verdict in sibling["verdicts"]
        if verdict["verdict"] == "fail"
    ] == ["constraints[2]"]

