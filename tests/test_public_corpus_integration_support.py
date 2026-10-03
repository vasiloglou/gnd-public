"""Exact bounded in-memory integration and narrative readers; no routed harnesses."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from test_public_assurance_inputs_support import contained

from gnd.assurance_evidence import _json, _read

inputs = SimpleNamespace(_json=_json, _read=_read, contained=contained)

def _unpublished_installed_route(*_args, **_kwargs):
    raise RuntimeError("The runtime-only support does not publish the unconsumed installed-cli branch.")

public_observer = SimpleNamespace(invoke=_unpublished_installed_route)

def _materialize():
    packed = (Path(__file__).parent / "fixtures/public-corpus-integration/closure.json.gz").read_bytes()
    assert len(packed) <= 8192
    assert hashlib.sha256(packed).hexdigest() == "c5d0c40372f4e83a5964f16896ff97febce44780eaea1d410c7545e3b10052ae"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(65537)
    assert len(raw) <= 65536
    assert hashlib.sha256(raw).hexdigest() == "1891c7d372a2a1cea0bbda9c6ac10f37736a3e22a4a1eebee7ffe9035e08b8e6"
    documents = json.loads(raw)
    assert set(documents) == {'coordinates.json', 'tests/fixtures/v6-assurance/cases/expense-approval/conforming/model.orm.yaml', 'tests/fixtures/v6-assurance/narratives.json', 'tests/fixtures/v6-assurance/cases/expense-approval/conforming/population.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-corpus-integration-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    coordinates = json.loads((root / "coordinates.json").read_text())
    assert len(coordinates["rows"]) == len(coordinates["answers"]) == 7
    return temporary, root, coordinates["rows"], coordinates["answers"]

_TEMPORARY, ROOT, ROWS, ANSWERS = _materialize()
atexit.register(_TEMPORARY.cleanup)

def narratives(root: Path = ROOT) -> dict[str, dict]:
    rows = inputs._json(inputs._read(root / "tests/fixtures/v6-assurance/narratives.json"))["cases"]
    result = {row["case_id"]: row for row in rows}
    if len(result) != 35:
        raise ValueError("Phase 6 narrative census changed")
    return result

def integration(
    row: dict,
    *,
    python: Path | None = None,
    working: Path | None = None,
    out: Path | None = None,
    root: Path = ROOT,
) -> dict:
    """Exercise installed exit envelopes and the required-seat outcome algebra."""
    from proof.v6.derivation.seats import classify_outcome

    recipe = row["recipe"]
    execution = recipe["execution"]
    if execution == "installed-cli":
        if python is None or working is None or out is None:
            raise ValueError("installed integration case requires command paths")
        result, payload = public_observer.invoke(python, recipe["argv"], working, out, 30, root)
        if result["exit"] == 64:
            return {"band": 64, "stdout": ""}
        return {
            "band": result["exit"],
            "level": payload["assurance"]["assurance_level"],
            "report_schema_version": payload["schema_version"],
            "semantic_decision": payload["assurance"]["semantic_decision"],
        }
    if execution == "cli-error-injection":
        from gnd import cli

        case = narratives(root)["expense-approval:conforming"]
        captured = io.StringIO()
        with (
            patch.object(
                cli,
                "check",
                side_effect=RuntimeError(recipe["message"]),
            ),
            redirect_stdout(captured),
        ):
            band = cli._cmd_check(case["model"], case["population"], "json")
        payload = json.loads(captured.getvalue())
        return {
            "band": band,
            "level": payload["assurance"]["assurance_level"],
            "report_schema_version": payload["schema_version"],
            "semantic_decision": payload["assurance"]["semantic_decision"],
        }
    if execution == "required-seat-validator":
        mutation = recipe["mutation"]
        state = {
            "none": (False, True, True, True),
            "remove-one-required-seat": (False, False, False, False),
            "remove-one-supported-result": (False, True, False, False),
            "change-one-verdict": (False, True, True, False),
            "timeout-after-start": (True, True, False, False),
            "change-one-tool-digest": (False, False, False, False),
        }[mutation]
        return {
            "status": classify_outcome(
                timed_out=state[0], available=state[1], complete=state[2], matched=state[3]
            )
        }
    raise ValueError(f"integration case needs another bounded supervisor: {execution}")
