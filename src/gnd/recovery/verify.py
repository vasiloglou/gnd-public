"""Fail-closed verification of a complete code-recovery evidence bundle."""

from __future__ import annotations

import ast
import json
import os
import stat
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from pydantic import ValidationError
from ruamel.yaml import YAMLError

from gnd import input_policy as _rf7_input
from gnd.artifacts import ArtifactError, read_regular_bounded
from gnd.artifacts import sha256_hex as _sha256
from gnd.model import ModelValidationError, load_model
from gnd.model_verbalization import VerbalizationError, render_model_verbalization
from gnd.recovery.inventory import (
    RecoveryInventoryError,
    _load_yaml_static,
    _reject_json_constant,
    _validate_structured_data,
    scan_recovery_scope,
)
from gnd.recovery.report import (
    EvidenceRecord,
    JsonPointerLocator,
    LineLocator,
    PythonSymbolLocator,
    RecoveryReport,
    RecoveryVerificationResult,
    YamlPathLocator,
)

__all__ = ["verify_recovery_bundle"]

MAX_REPORT_BYTES = 8 * 1024 * 1024
MAX_MODEL_BYTES = 16 * 1024 * 1024
MAX_VERBALIZATION_BYTES = 32 * 1024 * 1024


class _VerificationFailure(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail




def _canonical_fragment(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _safe_relative(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise _VerificationFailure("parent-traversal", f"{field} is not a safe relative path")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or value.startswith(("/", "\\"))
        or "\\" in value
        or not posix.parts
        or any(part in {"", ".", ".."} for part in posix.parts)
        or posix.as_posix() != value
    ):
        raise _VerificationFailure("parent-traversal", f"{field} leaves the bundle root")
    return value


def _failed(
    code: str,
    detail: str,
    *,
    model_sha256: str | None = None,
    verbalization_sha256: str | None = None,
    report_sha256: str | None = None,
) -> RecoveryVerificationResult:
    return RecoveryVerificationResult(
        ok=False,
        errors=(f"{code}: {detail}",),
        model_sha256=model_sha256,
        verbalization_sha256=verbalization_sha256,
        report_sha256=report_sha256,
        verified_evidence_ids=(),
        verified_census_paths=(),
    )


def _read(
    root: Path,
    relative: str,
    *,
    cap: int,
    artifact_name: str,
    root_identity: tuple[int, int],
) -> bytes:
    safe = _safe_relative(relative, field=artifact_name)
    try:
        data, _ = read_regular_bounded(
            root,
            safe,
            max_bytes=cap,
            expected_root=root_identity,
        )
    except ArtifactError as error:
        message = str(error)
        code = "missing-artifact" if "No such file" in message else "unsafe-artifact"
        raise _VerificationFailure(code, f"{artifact_name} {safe}: {message}") from error
    return data


def _bind_real_directory(path: Path) -> tuple[Path, tuple[int, int]]:
    """Bind an existing directory without following any pathname component."""

    absolute = Path(os.path.abspath(os.fspath(path)))
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        current = os.open(absolute.anchor or os.path.sep, flags)
    except OSError as error:
        raise _VerificationFailure(
            "unsafe-artifact", f"bundle root could not be opened: {error}"
        ) from error
    try:
        for part in absolute.parts[1:]:
            try:
                before = os.stat(part, dir_fd=current, follow_symlinks=False)
            except OSError as error:
                raise _VerificationFailure(
                    "unsafe-artifact",
                    f"bundle root component {part!r} could not be inspected: {error}",
                ) from error
            if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
                raise _VerificationFailure(
                    "unsafe-artifact", f"bundle root component {part!r} is not a real directory"
                )
            try:
                opened = os.open(part, flags, dir_fd=current)
            except OSError as error:
                raise _VerificationFailure(
                    "unsafe-artifact",
                    f"bundle root component {part!r} could not be opened safely: {error}",
                ) from error
            actual = os.fstat(opened)
            if (actual.st_dev, actual.st_ino) != (before.st_dev, before.st_ino):
                os.close(opened)
                raise _VerificationFailure(
                    "unsafe-artifact", f"bundle root component {part!r} changed before open"
                )
            os.close(current)
            current = opened
        identity = os.fstat(current)
        return absolute, (identity.st_dev, identity.st_ino)
    finally:
        os.close(current)


def _require_root_identity(root: Path, expected: tuple[int, int]) -> None:
    _, observed = _bind_real_directory(root)
    if observed != expected:
        raise _VerificationFailure("unsafe-artifact", "bundle root identity changed")


def _json_pointer(document: Any, pointer: str, *, code: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise _VerificationFailure(code, f"JSON Pointer {pointer!r} is not absolute")
    current = document
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(current, list):
                if token == "-" or not token.isdigit():
                    raise KeyError(token)
                current = current[int(token)]
            elif isinstance(current, dict):
                current = current[token]
            else:
                raise KeyError(token)
        except (IndexError, KeyError, TypeError) as error:
            raise _VerificationFailure(
                code, f"JSON Pointer {pointer!r} does not resolve"
            ) from error
    return current


def _line_excerpt(data: bytes, start: int, end: int) -> bytes:
    lines = data.splitlines(keepends=True)
    if start < 1 or end < start or end > len(lines):
        raise _VerificationFailure(
            "unresolved-locator", f"line span {start}:{end} is outside the evidence file"
        )
    return b"".join(lines[start - 1 : end])


def _python_nodes(tree: ast.Module) -> dict[str, ast.AST]:
    found: dict[str, ast.AST] = {}

    def visit(body: list[ast.stmt], prefix: tuple[str, ...] = ()) -> None:
        for node in body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                qualname = ".".join((*prefix, node.name))
                found[qualname] = node
                if isinstance(node, ast.ClassDef):
                    for member in node.body:
                        if isinstance(member, ast.AnnAssign) and isinstance(
                            member.target, ast.Name
                        ):
                            found[f"{qualname}.{member.target.id}"] = member
                    visit(node.body, (*prefix, node.name))

    visit(tree.body)
    return found


def _resolve_locator(evidence: EvidenceRecord, data: bytes) -> bytes:
    locator = evidence.locator
    if isinstance(locator, LineLocator):
        return _line_excerpt(data, locator.line_start, locator.line_end)
    if isinstance(locator, PythonSymbolLocator):
        try:
            source = data.decode("utf-8")
            tree = ast.parse(source, filename=evidence.path)
        except (UnicodeDecodeError, SyntaxError, ValueError) as error:
            raise _VerificationFailure(
                "unresolved-locator", f"Python evidence {evidence.path} cannot be parsed"
            ) from error
        node = _python_nodes(tree).get(locator.symbol)
        if node is None:
            raise _VerificationFailure(
                "unresolved-locator", f"Python symbol {locator.symbol!r} is absent"
            )
        start = int(getattr(node, "lineno", 0))
        end = int(getattr(node, "end_lineno", start))
        if (start, end) != (locator.line_start, locator.line_end):
            raise _VerificationFailure(
                "unresolved-locator",
                f"Python symbol {locator.symbol!r} moved from its recorded line span",
            )
        return _line_excerpt(data, start, end)
    if isinstance(locator, JsonPointerLocator):
        try:
            document = _rf7_input.loads(data.decode("utf-8"), parse_constant=_reject_json_constant)
            _validate_structured_data(document)
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            OverflowError,
            RecursionError,
            TypeError,
            ValueError,
        ) as error:
            raise _VerificationFailure(
                "unresolved-locator", f"JSON evidence {evidence.path} cannot be parsed"
            ) from error
        return _canonical_fragment(
            _json_pointer(document, locator.pointer, code="unresolved-locator")
        )
    if isinstance(locator, YamlPathLocator):
        try:
            document = _load_yaml_static(data.decode("utf-8"))
        except (
            UnicodeDecodeError,
            OverflowError,
            RecursionError,
            TypeError,
            ValueError,
            YAMLError,
        ) as error:
            raise _VerificationFailure(
                "unresolved-locator", f"YAML evidence {evidence.path} cannot be parsed"
            ) from error
        current = document
        try:
            for part in locator.path:
                if (
                    isinstance(current, list)
                    and isinstance(part, int)
                    or isinstance(current, dict)
                    and isinstance(part, str)
                ):
                    current = current[part]
                else:
                    raise KeyError(part)
        except (IndexError, KeyError, TypeError) as error:
            raise _VerificationFailure(
                "unresolved-locator", f"YAML path {tuple(locator.path)!r} does not resolve"
            ) from error
        return _canonical_fragment(current)
    raise _VerificationFailure("unresolved-locator", "unknown evidence locator kind")


def _expected_model_elements(model: dict[str, Any]) -> dict[str, tuple[str, str]]:
    expected: dict[str, tuple[str, str]] = {}
    for object_index, object_type in enumerate(model.get("object_types") or []):
        expected[f"/object_types/{object_index}"] = (
            "object-type",
            f"object:{object_type.get('id')}",
        )
    for fact_index, fact_type in enumerate(model.get("fact_types") or []):
        fact_pointer = f"/fact_types/{fact_index}"
        fact_id = str(fact_type.get("id"))
        expected[fact_pointer] = ("fact-type", f"fact:{fact_id}")
        for role_index, role in enumerate(fact_type.get("roles") or []):
            expected[f"{fact_pointer}/roles/{role_index}"] = (
                "role",
                f"role:{fact_id}:{role.get('role_name')}",
            )
        for constraint_index, _ in enumerate(fact_type.get("constraints") or []):
            expected[f"{fact_pointer}/constraints/{constraint_index}"] = (
                "constraint",
                "constraint",
            )
    for constraint_index, _ in enumerate(model.get("constraints") or []):
        expected[f"/constraints/{constraint_index}"] = ("constraint", "constraint")
    return expected


def _verify_model_mapping(report: RecoveryReport, model: dict[str, Any]) -> None:
    expected = _expected_model_elements(model)
    recorded = {entry.model_pointer: entry for entry in report.modeled_elements}
    if set(recorded) != set(expected):
        missing = sorted(set(expected) - set(recorded))
        extra = sorted(set(recorded) - set(expected))
        raise _VerificationFailure(
            "invalid-model-pointer",
            f"modeled-element census differs (missing={missing}, extra={extra})",
        )
    for pointer, entry in recorded.items():
        value = _json_pointer(model, pointer, code="invalid-model-pointer")
        if not isinstance(value, dict):
            raise _VerificationFailure(
                "invalid-model-pointer", f"modeled element {entry.element_id} is not an object"
            )
        expected_kind, expected_id = expected[pointer]
        if entry.element_kind.value != expected_kind:
            raise _VerificationFailure(
                "invalid-model-pointer",
                f"modeled element {entry.element_id} has kind {entry.element_kind.value}, "
                f"expected {expected_kind}",
            )
        if expected_id != "constraint" and entry.element_id != expected_id:
            raise _VerificationFailure(
                "invalid-model-pointer",
                f"modeled element {entry.element_id} does not identify {expected_id}",
            )
        if expected_kind == "constraint":
            recorded_provenance = (
                entry.source.value if entry.source is not None else None,
                entry.status.value if entry.status is not None else None,
                entry.modality.value if entry.modality is not None else None,
            )
            loaded_provenance = (
                value.get("source"),
                value.get("status"),
                value.get("modality"),
            )
            if recorded_provenance != loaded_provenance:
                raise _VerificationFailure(
                    "invalid-model-provenance",
                    f"modeled constraint {entry.element_id} provenance differs from the model",
                )


def _verify_proposal_transitions(report: RecoveryReport, model: dict[str, Any]) -> None:
    recorded_rejections = {
        proposal.proposal_id: proposal
        for proposal in report.proposals
        if proposal.status.value == "rejected"
    }
    loaded_rejections: dict[str, dict[str, Any]] = {}
    for item in model.get("rejected_proposals") or []:
        if not isinstance(item, dict) or not isinstance(item.get("proposal_id"), str):
            raise _VerificationFailure(
                "invalid-proposal-transition",
                "recovered rejected_proposals require stable proposal_id values",
            )
        proposal_id = item["proposal_id"]
        if proposal_id in loaded_rejections:
            raise _VerificationFailure(
                "invalid-proposal-transition", "rejected proposal identities must be unique"
            )
        loaded_rejections[proposal_id] = item
    if set(recorded_rejections) != set(loaded_rejections):
        raise _VerificationFailure(
            "invalid-proposal-transition",
            "report rejection history differs from model.rejected_proposals",
        )
    for proposal_id, proposal in recorded_rejections.items():
        expected = proposal.model_dump(mode="json")
        observed = loaded_rejections[proposal_id]
        if observed != expected:
            differing = sorted(
                key
                for key in set(expected) | set(observed)
                if expected.get(key) != observed.get(key)
            )
            raise _VerificationFailure(
                "invalid-proposal-transition",
                f"rejected proposal {proposal_id} differs in immutable fields: {differing}",
            )

    modeled_elements = {entry.element_id: entry for entry in report.modeled_elements}
    for proposal in report.proposals:
        if proposal.status.value != "confirmed":
            continue
        modeled = modeled_elements.get(proposal.element_id)
        if (
            modeled is None
            or modeled.element_kind is not proposal.element_kind
            or modeled.evidence_ids != proposal.evidence_ids
        ):
            raise _VerificationFailure(
                "invalid-proposal-transition",
                f"confirmed proposal {proposal.proposal_id} is not bound to its active model element",
            )
        if modeled.element_kind.value == "constraint" and (
            modeled.source is None
            or modeled.source.value != "user-supplied"
            or modeled.status is None
            or modeled.status.value != "confirmed"
        ):
            raise _VerificationFailure(
                "invalid-proposal-transition",
                f"confirmed proposal {proposal.proposal_id} lacks owner-confirmed provenance",
            )


def _verify_exact_census(
    root: Path,
    report: RecoveryReport,
    root_identity: tuple[int, int],
) -> None:
    scope = report.inventory.scope
    _require_root_identity(root, root_identity)
    try:
        observed = scan_recovery_scope(
            root,
            scope.selected_roots,
            excluded_roots=scope.excluded_roots,
            max_file_bytes=scope.max_file_bytes,
            max_total_bytes=scope.max_total_bytes,
            max_files=scope.max_files,
            expected_root_identity=root_identity,
            require_controller_reservations=True,
        )
    except (
        ArtifactError,
        IndexError,
        KeyError,
        ModelValidationError,
        OSError,
        RecoveryInventoryError,
        TypeError,
        ValidationError,
        ValueError,
        VerbalizationError,
    ) as error:
        raise _VerificationFailure(
            "inventory-refused", f"selected roots could not be re-inventoried: {error}"
        ) from error
    _require_root_identity(root, root_identity)
    recorded = {entry.path: str(entry.disposition) for entry in report.inventory.census}
    actual = {entry.path: str(entry.disposition) for entry in observed.census}
    if set(recorded) != set(actual):
        missing = sorted(set(actual) - set(recorded))
        extra = sorted(set(recorded) - set(actual))
        raise _VerificationFailure(
            "unaccounted-selected-path",
            f"selected-path census differs (unaccounted={missing}, absent={extra})",
        )
    mismatched = sorted(path for path in actual if actual[path] != recorded[path])
    if mismatched:
        raise _VerificationFailure(
            "unaccounted-selected-path",
            f"selected-path dispositions differ for {mismatched}",
        )
    recorded_inventory = report.inventory.model_dump(mode="json")
    observed_inventory = observed.model_dump(mode="json")
    observed_inventory["scope"]["repository_root"] = recorded_inventory["scope"]["repository_root"]
    if observed_inventory != recorded_inventory:
        raise _VerificationFailure(
            "stale-inventory",
            "selected-root digests, locators, or reference identities differ from the report",
        )


def verify_recovery_bundle(
    bundle_root: str | Path,
    *,
    expected_root_identity: tuple[int, int] | None = None,
) -> RecoveryVerificationResult:
    """Verify all bundle bytes, model elements, locators, and selected paths."""

    report_digest: str | None = None
    model_digest: str | None = None
    verbalization_digest: str | None = None
    try:
        root, root_identity = _bind_real_directory(Path(bundle_root))
        if expected_root_identity is not None and root_identity != expected_root_identity:
            raise _VerificationFailure(
                "unsafe-artifact",
                "bundle root identity differs from the caller's retained authority",
            )
        report_bytes = _read(
            root,
            "model.recovery.json",
            cap=MAX_REPORT_BYTES,
            artifact_name="model.recovery.json",
            root_identity=root_identity,
        )
        report_digest = _sha256(report_bytes)
        try:
            document = _rf7_input.loads(
                report_bytes.decode("utf-8"), parse_constant=_reject_json_constant
            )
            report = RecoveryReport.model_validate(document)
        except UnicodeDecodeError as error:
            raise _VerificationFailure(
                "invalid-report", "model.recovery.json is not UTF-8"
            ) from error
        except ValidationError as error:
            message = str(error)
            code = (
                "parent-traversal"
                if any(
                    token in message.lower() for token in ("relative path", "parent", "absolute")
                )
                else "invalid-report"
            )
            raise _VerificationFailure(code, message) from error
        except (json.JSONDecodeError, OverflowError, RecursionError, ValueError) as error:
            raise _VerificationFailure(
                "invalid-report", "model.recovery.json is not JSON"
            ) from error

        outputs = {entry.path: entry for entry in report.outputs}
        model_bytes = _read(
            root,
            "model.orm.yaml",
            cap=MAX_MODEL_BYTES,
            artifact_name="model.orm.yaml",
            root_identity=root_identity,
        )
        model_digest = _sha256(model_bytes)
        if model_digest != outputs["model.orm.yaml"].sha256:
            raise _VerificationFailure("stale-digest", "model.orm.yaml digest differs from report")
        verbalization_bytes = _read(
            root,
            "model.verbalization.txt",
            cap=MAX_VERBALIZATION_BYTES,
            artifact_name="model.verbalization.txt",
            root_identity=root_identity,
        )
        verbalization_digest = _sha256(verbalization_bytes)

        with tempfile.TemporaryDirectory(prefix="gnd-recovery-verify-") as temporary:
            safe_model = Path(temporary) / "model.orm.yaml"
            safe_model.write_bytes(model_bytes)
            loaded = load_model(str(safe_model))
        if loaded.source.get("kind") != "codebase":
            raise _VerificationFailure(
                "invalid-model-origin", "recovered model source.kind must be codebase"
            )
        expected_verbalization = render_model_verbalization(loaded).encode("utf-8")
        if verbalization_bytes != expected_verbalization:
            raise _VerificationFailure(
                "incomplete-verbalization",
                "model.verbalization.txt is not the complete deterministic rendering",
            )
        if verbalization_digest != outputs["model.verbalization.txt"].sha256:
            raise _VerificationFailure(
                "stale-digest", "model.verbalization.txt digest differs from report"
            )

        model_document = loaded.model_dump(mode="json")
        _verify_model_mapping(report, model_document)
        _verify_proposal_transitions(report, model_document)

        verified_ids: list[str] = []
        for evidence in report.inventory.evidence:
            evidence_bytes = _read(
                root,
                evidence.path,
                cap=report.inventory.scope.max_file_bytes,
                artifact_name=evidence.path,
                root_identity=root_identity,
            )
            if (
                len(evidence_bytes) != evidence.byte_length
                or _sha256(evidence_bytes) != evidence.sha256
            ):
                raise _VerificationFailure(
                    "stale-digest", f"evidence {evidence.evidence_id} bytes differ from report"
                )
            excerpt = _resolve_locator(evidence, evidence_bytes)
            if _sha256(excerpt) != evidence.excerpt_sha256:
                raise _VerificationFailure(
                    "unresolved-locator",
                    f"evidence {evidence.evidence_id} excerpt digest does not match its locator",
                )
            verified_ids.append(evidence.evidence_id)

        _verify_exact_census(root, report, root_identity)
        return RecoveryVerificationResult(
            ok=True,
            errors=(),
            model_sha256=model_digest,
            verbalization_sha256=verbalization_digest,
            report_sha256=report_digest,
            verified_evidence_ids=tuple(sorted(verified_ids)),
            verified_census_paths=tuple(entry.path for entry in report.inventory.census),
        )
    except _VerificationFailure as error:
        return _failed(
            error.code,
            error.detail,
            model_sha256=model_digest,
            verbalization_sha256=verbalization_digest,
            report_sha256=report_digest,
        )
    except (
        ArtifactError,
        IndexError,
        KeyError,
        ModelValidationError,
        OSError,
        OverflowError,
        RecursionError,
        RecoveryInventoryError,
        TypeError,
        ValidationError,
        ValueError,
        VerbalizationError,
    ) as error:
        return _failed(
            "verification-error",
            str(error),
            model_sha256=model_digest,
            verbalization_sha256=verbalization_digest,
            report_sha256=report_digest,
        )
