"""Original fake-tool admission guard; never discovers or runs real engines."""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import duckdb
import pytest
from support.digests import sha256_file as _sha256
from test_public_derivation_parity_corpus import (
    CODEC_VERSION,
    DISPOSITIONS,
    PARITY_CASES,
    PYREL_VERSION,
    RECEIPT,
    _canonical_digest,
    _case_paths,
    _duckdb_extensions,
    _nonempty_case,
    _oracle_identity_token,
    _production_digest,
)

from gnd.model import load_model
from gnd.population import load_population
from gnd.popvalidate import resolve_primitive

REPO_ROOT = Path(__file__).resolve().parents[1]
PYREL_OUTPUT_LIMIT = 4 * 1024 * 1024

def _bounded_command(
    argv: list[str], *, timeout: int, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run one foreign seat command and kill its whole process group on timeout."""
    process = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)

def _pyrel_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate keys before JSON decoding can discard their evidence."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"PyRel output repeats JSON key {key!r}")
        result[key] = value
    return result

def _pyrel_validate_token(token: Any, primitive: str | None) -> None:
    assert isinstance(token, str), "PyRel identity token must be a JSON string"
    value = json.loads(token, object_pairs_hook=_pyrel_json_object)
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("PyRel identity token must contain a tag and payload")
    tag, payload = value
    valid = False
    if tag == "string":
        valid = isinstance(payload, str)
    elif tag == "boolean":
        valid = isinstance(payload, bool)
    elif tag == "number":
        valid = (
            isinstance(payload, list)
            and len(payload) == 2
            and all(type(part) is int for part in payload)
            and payload[1] > 0
            and math.gcd(*payload) == 1
        )
    if not valid:
        raise ValueError("PyRel identity token has an invalid tag or payload")
    expected_tag = (
        "boolean"
        if primitive == "Boolean"
        else "number"
        if primitive in {"Integer", "Float", "Number"}
        else "string"
        if primitive in {"String", "Date", "DateTime", "Binary"}
        else None
    )
    if expected_tag is not None and tag != expected_tag:
        raise ValueError(f"PyRel identity token tag {tag!r} is not valid for {primitive}")
    if token != json.dumps(value, ensure_ascii=False, separators=(",", ":")):
        raise ValueError("PyRel identity token is not canonical JSON")

def _pyrel_extensions(
    model: Path,
    population: Path,
    *,
    executable: str | None = None,
) -> dict[str, tuple[tuple[str, ...], ...]]:
    """Run the isolated foreign seat on raw inputs, then validate its output."""
    executable = executable or shutil.which("uv")
    if executable is None:
        raise RuntimeError("uv executable absent; PyRel derivation seat unavailable")
    script = REPO_ROOT / "tests" / "oracles" / "pyrel_derivation_oracle.py"
    with tempfile.TemporaryDirectory(prefix="gnd-pyrel-derivation-") as directory:
        scratch = Path(directory)
        output = scratch / "result.json"
        process = _bounded_command(
            [
                executable,
                "run",
                "--locked",
                "--script",
                str(script),
                str(model),
                str(population),
                "--out",
                str(output),
            ],
            timeout=120,
            env={**os.environ, "RAI_BUILD_DIR": str(scratch / "build")},
        )
        if process.returncode != 0:
            raise RuntimeError(
                f"PyRel derivation process exited {process.returncode}: {process.stderr}"
            )
        with output.open("rb") as stream:
            raw = stream.read(PYREL_OUTPUT_LIMIT + 1)
        if len(raw) > PYREL_OUTPUT_LIMIT:
            raise ValueError("PyRel derivation output exceeds the 4 MiB read limit")
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=_pyrel_json_object)
    if not isinstance(document, dict) or set(document) != {
        "schema_version",
        "backend",
        "version",
        "extensions",
    }:
        raise ValueError("PyRel derivation output has an invalid envelope")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("PyRel derivation output requires schema_version 1")
    if document["backend"] != "pyrel" or document["version"] != PYREL_VERSION:
        raise ValueError("PyRel derivation output has the wrong backend or package version")
    # GND validates the response boundary only; the child receives the original
    # paths and independently reads, orders, and evaluates their declarations.
    loaded_model = load_model(model)
    heads = {
        str(fact["id"]): tuple(
            resolve_primitive(str(role["object_type"]), loaded_model) for role in fact["roles"]
        )
        for fact in loaded_model.fact_types
        if isinstance(fact.get("derivation_rule"), dict)
    }
    extensions = document["extensions"]
    if not isinstance(extensions, dict) or set(extensions) != set(heads):
        raise ValueError("PyRel derivation output has missing or unexpected heads")
    result: dict[str, tuple[tuple[str, ...], ...]] = {}
    for head, primitives in heads.items():
        rows = extensions[head]
        assert isinstance(rows, list), f"PyRel head {head} rows must be an array"
        checked = []
        for row in rows:
            if not isinstance(row, list) or len(row) != len(primitives):
                raise ValueError(f"PyRel head {head} row has wrong shape or arity")
            for token, primitive in zip(row, primitives, strict=True):
                _pyrel_validate_token(token, primitive)
            checked.append(tuple(row))
        if len(checked) != len(set(checked)):
            raise ValueError(f"PyRel head {head} contains duplicate rows")
        if checked != sorted(checked):
            raise ValueError(f"PyRel head {head} rows are not in canonical order")
        result[head] = tuple(checked)
    return result

def _souffle_version(executable: str) -> str:
    completed = _bounded_command(
        [executable, "--version"],
        timeout=120,
    )
    completed.check_returncode()
    match = re.search(r"^Version:\s*(\S+)", completed.stdout + completed.stderr, re.MULTILINE)
    if match is None:
        raise AssertionError("souffle --version did not report a Version field")
    return match.group(1)

def _souffle_extensions(model, population, executable):
    """Transport the shared production emitter, retaining independent tokens."""
    from gnd.export import souffle
    from gnd.export.souffle_io import write_souffle_bundle
    from gnd.export.souffle_runtime import run_souffle

    document = model.model_dump(mode="json", exclude={"warnings"}, exclude_unset=True)
    # This historical seat receives a combined population. Project its current
    # fixed context back to candidate/reference inputs; do not mutate the model.
    context = getattr(population, "_reference_context", None)
    refs = tuple((o.id, raw) for o, _, raw in context._snapshots) if context else ()
    from gnd.witness.io import population_wire

    pop = population_wire(population)
    if context:
        owners = {fid for fid, _ in context._owners}
        pop["facts"] = {k: v for k, v in pop["facts"].items() if k not in owners}
        pop["population"]["covers"] = [k for k in pop["population"]["covers"] if k not in owners]
    # Combined/evaluator rows are claims, never Souffle base assertions.
    derived = {f["id"] for f in model.fact_types if f.get("derivation")}
    pop["facts"] = {k: v for k, v in pop["facts"].items() if k not in derived}
    pop["population"]["covers"] = [k for k in pop["population"]["covers"] if k not in derived]
    result = souffle.render_souffle(
        json.dumps(document).encode(),
        json.dumps(pop).encode(),
        model_format="json",
        reference_inputs=refs,
    )
    assert result.exit_code == 0, result.reason
    with tempfile.TemporaryDirectory(prefix="gnd-souffle-") as directory:
        out = Path(directory) / "bundle"
        assert write_souffle_bundle(result, out, raw=True).exit_code == 0
        native = run_souffle(out, executable=executable)
        assert native["exit_code"] == 0, "Souffle produced no output: " + str(native["reason"])
        return {
            fid: tuple(
                sorted(
                    {
                        tuple(
                            _oracle_identity_token(cell["value"], cell["primitive"]) for cell in row
                        )
                        for row in rows
                    }
                )
            )
            for fid, rows in native["extensions"].items()
        }

def _recorded_disposition(
    recorded: dict[str, Any],
    *,
    case_id: str,
    backend: str,
    model_digest: str,
    population_digest: str,
    production_digest: str,
    backend_digest: str,
) -> str | None:
    rows = {row.get("case_id"): row for row in recorded.get("cases", [])}
    row = rows.get(case_id)
    if not isinstance(row, dict):
        return None
    if (
        row.get("model_sha256") != model_digest
        or row.get("population_sha256") != population_digest
        or row.get("production_sha256") != production_digest
    ):
        return None
    result = row.get("results", {}).get(backend, {})
    disposition = result.get("disposition")
    if result.get("digest") != backend_digest or disposition not in DISPOSITIONS:
        return None
    return str(disposition)

def _build_receipt(
    *,
    souffle_executable: str | None,
    pyrel_executable: str | None = None,
) -> dict[str, Any]:
    recorded = json.loads(RECEIPT.read_text(encoding="utf-8")) if RECEIPT.is_file() else {}
    souffle_version = (
        _souffle_version(souffle_executable) if souffle_executable is not None else None
    )
    rows = []
    for case in PARITY_CASES:
        model_path, population_path = _case_paths(case)
        model = load_model(model_path)
        population = load_population(population_path, model=model)
        production = _production_digest(model, population)
        oracle = _canonical_digest(model, _duckdb_extensions(model, population))
        model_digest = _sha256(model_path)
        population_digest = _sha256(population_path)
        duckdb_status = "matched" if oracle == production else "mismatched"
        duckdb_disposition = (
            None
            if duckdb_status == "matched"
            else _recorded_disposition(
                recorded,
                case_id=str(case["id"]),
                backend="duckdb",
                model_digest=model_digest,
                population_digest=population_digest,
                production_digest=production,
                backend_digest=oracle,
            )
        )
        if pyrel_executable is None:
            pyrel_result = {
                "status": "skipped",
                "version": None,
                "digest": None,
                "disposition": None,
            }
        else:
            pyrel_digest = _canonical_digest(
                model,
                _pyrel_extensions(
                    model_path,
                    population_path,
                    executable=pyrel_executable,
                ),
            )
            pyrel_status = "matched" if pyrel_digest == production else "mismatched"
            pyrel_result = {
                "status": pyrel_status,
                "version": PYREL_VERSION,
                "digest": pyrel_digest,
                "disposition": (
                    None
                    if pyrel_status == "matched"
                    else _recorded_disposition(
                        recorded,
                        case_id=str(case["id"]),
                        backend="pyrel",
                        model_digest=model_digest,
                        population_digest=population_digest,
                        production_digest=production,
                        backend_digest=pyrel_digest,
                    )
                ),
            }
        if souffle_executable is None:
            souffle_result = {
                "status": "skipped",
                "version": None,
                "digest": None,
                "disposition": None,
            }
        else:
            souffle_digest = _canonical_digest(
                model,
                _souffle_extensions(model, population, souffle_executable),
            )
            souffle_status = "matched" if souffle_digest == production else "mismatched"
            souffle_result = {
                "status": souffle_status,
                "version": souffle_version,
                "digest": souffle_digest,
                "disposition": (
                    None
                    if souffle_status == "matched"
                    else _recorded_disposition(
                        recorded,
                        case_id=str(case["id"]),
                        backend="souffle",
                        model_digest=model_digest,
                        population_digest=population_digest,
                        production_digest=production,
                        backend_digest=souffle_digest,
                    )
                ),
            }
        rows.append(
            {
                "case_id": case["id"],
                "model_sha256": model_digest,
                "population_sha256": population_digest,
                "production_sha256": production,
                "results": {
                    "duckdb": {
                        "status": duckdb_status,
                        "version": duckdb.__version__,
                        "digest": oracle,
                        "disposition": duckdb_disposition,
                    },
                    "pyrel": pyrel_result,
                    "souffle": souffle_result,
                },
            }
        )
    return {
        "schema_version": 1,
        "identity_codec_version": CODEC_VERSION,
        "cases": rows,
    }

def test_simulated_souffle_present_and_absent_are_both_visible(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    absent = _build_receipt(souffle_executable=None)
    assert all(
        row["results"]["souffle"]
        == {
            "status": "skipped",
            "version": None,
            "digest": None,
            "disposition": None,
        }
        for row in absent["cases"]
    )

    fake = tmp_path / "souffle"
    fake.write_text(
        '#!/bin/sh\nif [ "$1" = "--version" ]; then printf "Version: 2.5\\n"; fi\nexit 0\n',
        encoding="utf-8",
    )
    os.chmod(fake, 0o755)
    monkeypatch.setattr(shutil, "which", lambda _name: str(fake))
    assert shutil.which("souffle") == str(fake)
    model, population = _nonempty_case()
    with pytest.raises(AssertionError, match="produced no output"):
        _souffle_extensions(model, population, str(fake))
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    assert shutil.which("souffle") is None
