"""Pure admission and temporary-directory publication guards only."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/v62-phase8"

JSON_DEPTH_LIMIT = 64

JSON_STRING_BYTE_LIMIT = 1024 * 1024

JSON_INTEGER_DIGIT_LIMIT = 4300

def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _integer(value: str) -> int:
    digits = value.removeprefix("-")
    if len(digits) > JSON_INTEGER_DIGIT_LIMIT:
        raise ValueError("JSON integer exceeds its digit limit")
    return int(value)


def _nonfinite(token: str) -> None:
    raise ValueError(f"non-finite JSON number: {token}")


def _walk(value: Any, depth: int = 0) -> None:
    if depth > JSON_DEPTH_LIMIT:
        raise ValueError("JSON document exceeds its depth limit")
    if isinstance(value, str) and len(value.encode("utf-8")) > JSON_STRING_BYTE_LIMIT:
        raise ValueError("JSON string exceeds its byte limit")
    if isinstance(value, dict):
        for key, item in value.items():
            _walk(key, depth + 1)
            _walk(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _walk(item, depth + 1)


def load_json(path: Path, *, byte_limit: int) -> Any:
    size = path.stat().st_size
    if size > byte_limit:
        raise ValueError("JSON document exceeds its byte limit")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_int=_integer,
            parse_constant=_nonfinite,
        )
    except UnicodeDecodeError as error:
        raise ValueError("JSON document is not UTF-8") from error
    except (json.JSONDecodeError, RecursionError) as error:
        raise ValueError("JSON document is malformed or too deeply nested") from error
    _walk(value)
    return value


def load(path: str | Path) -> Any:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    return json.loads(resolved.read_text(encoding="utf-8"))


ANSWER_BYTE_LIMIT = 32 * 1024 * 1024

V62_CORPUS = "tests/fixtures/v62-phase8"

V61_SURFACE_FIXTURES = {
    "phase1-matrix": "v61-phase1",
    "phase2-api-matrix": "v61-phase2",
    "phase3-plan-session-matrix": "v61-phase3",
    "phase4-redaction-matrix": "v61-phase4",
    "phase5-walk-floor-matrix": "v61-phase5",
    "phase6-open-adapter-matrix": "v61-phase6",
}

V62_CLASS_LEVELS = {"L": "proof-backed", "M": "partial", "N": "partial"}

def validate_v62_assurance_observation(
    observation: dict[str, Any],
    *,
    case_class: str,
    mode: str = "final",
    expected_level: str | None = None,
) -> bool:
    """A live observation must match its class; not-current evidence proves nothing."""
    level = observation.get("assurance_level")
    not_current = observation.get("evidence_not_current")
    if type(not_current) is not bool:
        raise ValueError("v6.2 assurance observation omits evidence currency")
    if mode == "baseline":
        expected = ("none", True)
    elif mode in {"final", "relocated"}:
        expected = (expected_level or V62_CLASS_LEVELS[case_class], False)
    else:
        raise ValueError(f"unknown v6.2 assurance mode: {mode}")
    if (level, not_current) != expected:
        raise ValueError(
            f"v6.2 class {case_class} {mode} assurance is {level}/not-current={not_current}"
        )
    return True


def _without_assurance(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_assurance(child)
            for key, child in value.items()
            if key not in {"accepted", "proof_credit", "scope_id_present", "wheel", "exit_code"}
            and "assurance" not in key
            and "evidence-not-current" not in key
            # Drivers also spell evidence currency with underscores.
            and "evidence_not_current" not in key
        }
    if isinstance(value, list):
        return [_without_assurance(child) for child in value]
    return value


def _v62_functional(row: dict[str, Any]) -> Any:
    """The functional projection compared across baseline and final wheels."""
    payload = row["result"]["payload"]
    if row["operation"] in V61_SURFACE_FIXTURES:
        return _without_assurance(payload)
    return {key: payload[key] for key in ("accepted", "observations") if key in payload}


def _admit_v62_probe(
    payload: dict[str, Any], *, mode: str, module_origin: str, repository_root: Path = ROOT
) -> bool:
    """Live class assurance from both installed surfaces, against the frozen answers."""
    if payload.get("module") != module_origin:
        raise ValueError("v6.2 assurance probe did not run the installed wheel")
    cases = load_json(
        repository_root / V62_CORPUS / "class-cases.json", byte_limit=ANSWER_BYTE_LIMIT
    )
    expected = {row["case_id"]: row for row in cases["cases"]}
    if set(payload["cases"]) != set(expected):
        raise ValueError("v6.2 assurance probe omitted a class case")
    for case_id, row in payload["cases"].items():
        if row["cli"] != row["api"]:
            raise ValueError(f"v6.2 CLI and API assurance disagree: {case_id}")
        validate_v62_assurance_observation(
            row["api"],
            case_class=row["class"],
            mode=mode,
            expected_level=expected[case_id]["final_assurance_level"],
        )
        if mode in {"final", "relocated"} and (
            row["api"]["uncovered_count"] != expected[case_id]["uncovered_new_count"]
            or row["api"]["uncovered_sha256"] != expected[case_id]["uncovered_new_sha256"]
        ):
            raise ValueError(f"v6.2 final uncovered list differs from the frozen answer: {case_id}")
    return True


def _assurance_values(value: Any) -> list[tuple[str, Any]]:
    if isinstance(value, dict):
        own = [
            (key, item)
            for key, item in value.items()
            if key in {"assurance_level", "evidence_not_current"}
        ]
        return own + [pair for item in value.values() for pair in _assurance_values(item)]
    if isinstance(value, list):
        return [pair for item in value for pair in _assurance_values(item)]
    return []


def _v62_runs_pass(baseline: dict[str, Any], final: dict[str, Any]) -> bool:
    """Every run exits 0 and is accepted, except that a v6.1 driver written for
    not-current evidence may reject a final wheel solely for being recertified."""
    for before, after in zip(baseline["operations"], final["operations"], strict=True):
        for run in (before["result"], after["result"]):
            if run["exit_code"] == 0 and run["payload"].get("accepted") is not False:
                continue
            payload, prior = run["payload"], before["result"]["payload"]
            recertified = set(_assurance_values(payload))
            if not (
                run is after["result"]
                and after["operation"] in V61_SURFACE_FIXTURES
                and _without_assurance(payload) == _without_assurance(prior)
                and recertified
                and recertified
                <= {("assurance_level", "proof-backed"), ("evidence_not_current", False)}
                and recertified != set(_assurance_values(prior))
            ):
                return False
    return True


def _v62_surface_summary(surfaces: dict[str, Any], final_wheel: dict[str, Any]) -> dict[str, Any]:
    baseline, final = surfaces["baseline"], surfaces["final"]
    relocated = surfaces.get("relocated")
    compared = (baseline, final) if relocated is None else (baseline, final, relocated)
    runs = [row["result"] for mode in compared for row in mode["operations"]]
    return {
        "artifact_origin": all(
            final["artifact"][key] == final_wheel[key] for key in ("size_bytes", "sha256")
        ),
        "isolated": all(run["isolated"] for run in (*runs, *(mode["probe"] for mode in compared))),
        "functional_equal": [_v62_functional(row) for row in baseline["operations"]]
        == [_v62_functional(row) for row in final["operations"]]
        and _v62_runs_pass(baseline, final)
        and (
            relocated is None
            or [_v62_functional(row) for row in relocated["operations"]]
            == [_v62_functional(row) for row in final["operations"]]
        ),
        "live_assurance": all(mode["live_assurance"] is True for mode in compared),
        "surface_operations": [row["operation"] for row in final["operations"]],
    }


def _install_bundle(source: Path, destination: Path, admitted, finalize=None) -> None:
    """Replace destination with source; restore the predecessor on any failure."""
    holding = Path(tempfile.mkdtemp(dir=destination.parent))
    predecessor = holding / "predecessor"
    rejected = holding / "rejected"
    success = False
    try:
        if destination.exists():
            shutil.move(destination, predecessor)
        try:
            shutil.copytree(source, destination)
            if not admitted():
                raise ValueError("this checkout's reader refuses the development-profile bundle")
            if finalize is not None:
                finalize()
            success = True
        except BaseException:
            if destination.exists():
                destination.rename(rejected)
            if predecessor.exists():
                predecessor.rename(destination)
            raise
    finally:
        if success or not predecessor.exists():
            shutil.rmtree(holding)

