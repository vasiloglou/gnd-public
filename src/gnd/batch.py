from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from ruamel.yaml.error import YAMLError

from gnd.artifacts import ArtifactError, LeafSnapshot, canonical_json_bytes, read_regular_bounded
from gnd.checker import band as checker_band
from gnd.checker import check
from gnd.model import MAX_MODEL_BYTES, ModelValidationError, ValidationIssue, load_model
from gnd.population import PopulationLoadError, PopulationValidationError, load_population

BATCH_SCHEMA_VERSION = 1
BATCH_EXIT_PRECEDENCE = (3, 1, 4, 2, 0)
_OUTCOMES = {
    0: "accepted",
    1: "violated",
    2: "inadequate",
    3: "ill_formed",
    4: "indeterminate",
}
_EMPTY_COUNTS = {"pass": 0, "fail": 0, "warning": 0, "unchecked": 0, "vacuous": 0}
_SUFFIXES = {".json", ".yaml", ".yml"}


class BatchError(Exception):
    pass


class BatchUsageError(BatchError):
    pass


class BatchMissingError(BatchError):
    pass


class BatchIOError(BatchError):
    pass


class BatchInternalError(BatchError):
    pass


@dataclass(frozen=True)
class BatchRow:
    population: str
    exit_code: Literal[0, 1, 2, 3, 4]
    outcome: Literal["accepted", "violated", "inadequate", "ill_formed", "indeterminate"]
    counts: dict[str, int]
    failing_constraints: tuple[str, ...]
    issues: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class BatchResult:
    model_filename: str
    model_digest: str
    rows: tuple[BatchRow, ...]
    aggregate_exit: Literal[0, 1, 2, 3, 4]
    issues: tuple[dict[str, Any], ...]


def _issue_records(issues: list[ValidationIssue]) -> tuple[dict[str, Any], ...]:
    return tuple(issue.model_dump(mode="json") for issue in issues[:200])


def _load_error_issue(
    error: BaseException, *, rule_id: str, private_path: Path | None = None, public_path: str = ""
) -> dict[str, Any]:
    message = str(error)
    if private_path is not None:
        message = message.replace(str(private_path), public_path or private_path.name)
    return {
        "path": "$",
        "message": message,
        "rule_id": rule_id,
        "severity": "error",
    }


def _validate_population_root(root: Path) -> None:
    if root.is_symlink():
        raise BatchIOError(f"population root is not a real directory: {root}")
    if not root.exists():
        raise BatchMissingError(f"population directory does not exist: {root}")
    if not root.is_dir():
        raise BatchIOError(f"population root is not a real directory: {root}")


def _population_paths(root: Path) -> list[Path]:
    _validate_population_root(root)
    candidates: list[Path] = []
    try:
        for path in root.rglob("*"):
            if path.suffix.lower() not in _SUFFIXES:
                continue
            if path.is_symlink():
                raise BatchIOError(f"population tree contains a symlink: {path}")
            if not path.is_file():
                raise BatchIOError(f"population candidate is not a regular file: {path}")
            candidates.append(path)
    except OSError as error:
        raise BatchIOError(f"population directory could not be read: {error}") from error
    candidates.sort(key=lambda path: path.relative_to(root).as_posix())
    if not candidates:
        raise BatchUsageError("population directory contains no .json/.yaml/.yml files")
    return candidates


def _model_failure(
    model_path: Path, digest: str, issues: tuple[dict[str, Any], ...]
) -> BatchResult:
    return BatchResult(model_path.name, digest, (), 3, issues)


def _confirm_model_snapshot(model_path: Path, snapshot: LeafSnapshot) -> None:
    try:
        read_regular_bounded(
            model_path.parent,
            model_path.name,
            max_bytes=MAX_MODEL_BYTES,
            expected=snapshot,
        )
    except ArtifactError as error:
        raise BatchIOError(f"model changed while it was loaded: {error}") from error


def check_population_directory(model_path: Path, populations_dir: Path, *,
                               compiled_operations: bool = False) -> BatchResult:
    if not isinstance(compiled_operations, bool):
        raise TypeError('compiled_operations must be a boolean')
    _validate_population_root(populations_dir)
    if model_path.is_symlink():
        raise BatchIOError(f"model is not a real regular file: {model_path}")
    if not model_path.exists():
        raise BatchMissingError(f"model does not exist: {model_path}")
    if not model_path.is_file():
        raise BatchIOError(f"model is not a real regular file: {model_path}")
    try:
        model_bytes, snapshot = read_regular_bounded(
            model_path.parent, model_path.name, max_bytes=MAX_MODEL_BYTES
        )
    except ArtifactError as error:
        raise BatchIOError(str(error)) from error
    model_digest = hashlib.sha256(model_bytes).hexdigest()
    try:
        model = load_model(model_path)
    except ModelValidationError as error:
        _confirm_model_snapshot(model_path, snapshot)
        return _model_failure(model_path, model_digest, _issue_records(error.issues))
    except FileNotFoundError as error:
        raise BatchMissingError(str(error)) from error
    except OSError as error:
        raise BatchIOError(str(error)) from error
    except Exception as error:  # noqa: BLE001 - malformed model is a band-3 envelope
        _confirm_model_snapshot(model_path, snapshot)
        return _model_failure(
            model_path,
            model_digest,
            (_load_error_issue(error, rule_id="model:load", private_path=model_path),),
        )
    _confirm_model_snapshot(model_path, snapshot)
    paths = _population_paths(populations_dir)
    rows: list[BatchRow] = []
    for path in paths:
        relative = path.relative_to(populations_dir).as_posix()
        try:
            population = load_population(path, model=model)
            if model.reference_populations:
                from gnd.references import bind_population, resolve_context

                population = bind_population(
                    model, population, references=resolve_context(model)
                ).combined
        except PopulationValidationError as error:
            rows.append(
                BatchRow(
                    relative,
                    3,
                    "ill_formed",
                    dict(_EMPTY_COUNTS),
                    (),
                    _issue_records(error.issues),
                )
            )
            continue
        except OSError as error:
            raise BatchIOError(f"population could not be read: {relative}: {error}") from error
        except (
            PopulationLoadError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            YAMLError,
            RecursionError,
            ValueError,
        ) as error:
            rows.append(
                BatchRow(
                    relative,
                    3,
                    "ill_formed",
                    dict(_EMPTY_COUNTS),
                    (),
                    (
                        _load_error_issue(
                            error,
                            rule_id="population:parse",
                            private_path=path,
                            public_path=relative,
                        ),
                    ),
                )
            )
            continue
        except Exception as error:
            raise BatchInternalError(f"population loader failed for {relative}: {error}") from error
        try:
            report = (check(model, population, compiled_operations=True)
                      if compiled_operations else check(model, population))
            exit_code = checker_band(report)
        except Exception as error:
            raise BatchInternalError(f"checker failed for {relative}: {error}") from error
        failing: list[str] = []
        seen_failing: set[str] = set()
        for verdict in report.verdicts:
            if verdict.verdict == "fail" and verdict.constraint_ref not in seen_failing:
                seen_failing.add(verdict.constraint_ref)
                failing.append(verdict.constraint_ref)
        rows.append(
            BatchRow(
                relative,
                exit_code,
                _OUTCOMES[exit_code],
                report.counts(),
                tuple(failing),
                (),
            )
        )
    exits = {row.exit_code for row in rows}
    aggregate = next(code for code in BATCH_EXIT_PRECEDENCE if code in exits)
    return BatchResult(model_path.name, model_digest, tuple(rows), aggregate, ())


def build_batch_payload(result: BatchResult) -> dict[str, Any]:
    outcomes = {name: 0 for name in _OUTCOMES.values()}
    rows: list[dict[str, Any]] = []
    for row in result.rows:
        outcomes[row.outcome] += 1
        rows.append(
            {
                "population": row.population,
                "outcome": row.outcome,
                "exit_code": row.exit_code,
                "counts": row.counts,
                "failing_constraints": list(row.failing_constraints),
                "issues": list(row.issues),
            }
        )
    if result.rows:
        exits = {row.exit_code for row in result.rows}
        expected = next(code for code in BATCH_EXIT_PRECEDENCE if code in exits)
        if expected != result.aggregate_exit:
            raise BatchInternalError("aggregate exit disagrees with row precedence")
    return {
        "schema_version": BATCH_SCHEMA_VERSION,
        "tool": "gnd",
        "command": "check-batch",
        "model": {"filename": result.model_filename, "sha256": result.model_digest},
        "issues": list(result.issues),
        "rows": rows,
        "summary": {
            "projections": len(rows),
            "outcomes": outcomes,
            "aggregate_exit": result.aggregate_exit,
        },
    }


def canonical_batch_bytes(payload: dict[str, Any]) -> bytes:
    return canonical_json_bytes(payload)
