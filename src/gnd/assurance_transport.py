"""Private live verifier transport; archived JSON is never a capability.

Only the supervised fixed Python verifier gets a fresh nonce and an output
path outside its candidate view. The parent consumes that receipt once, after
process cleanup and exact report-byte checks. Ordinary JSON readers do not
call this boundary, and ordinary CLI invocations do not write a receipt.
"""

from __future__ import annotations

import hashlib
import json
import os
from contextvars import ContextVar
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gnd.assurance import AuthenticatedExecution, _internal_value
from gnd.assurance_evidence import MAX_DOCUMENT_BYTES, _json, _read

_PENDING: ContextVar[AuthenticatedExecution | None] = ContextVar(
    "gnd_assurance_execution", default=None
)
_PATH_ENV = "GND_INTERNAL_ASSURANCE_RECEIPT"
_NONCE_ENV = "GND_INTERNAL_ASSURANCE_NONCE"


def producer_identity() -> str:
    """Current installed Python source and interpreter identity for the live IPC."""
    import sys

    from gnd.assurance_evidence import production_identity

    parts = [
        production_identity(),
        hashlib.sha256(_read(Path(sys.executable), 64 * 1024 * 1024)).hexdigest(),
    ]
    return hashlib.sha256(json.dumps(parts, separators=(",", ":")).encode()).hexdigest()


def prepare_execution(execution: AuthenticatedExecution | None) -> None:
    _PENDING.set(execution)


def emit_receipt(raw: bytes) -> None:
    """An optional private output; failure never changes the semantic command."""
    execution = _PENDING.get()
    _PENDING.set(None)
    target, nonce = os.environ.get(_PATH_ENV), os.environ.get(_NONCE_ENV)
    if execution is None or target is None or nonce is None:
        return
    try:
        payload = _json(raw)
        if payload.get("schema_version") != 7 or payload.get("exit_code") != execution.band:
            return
        document = {
            "schema_version": 1,
            "nonce": nonce,
            "producer_identity": producer_identity(),
            "report_sha256": hashlib.sha256(raw).hexdigest(),
            "model_digest": payload.get("model_digest"),
            "execution": {
                key: sorted(value) if isinstance(value, frozenset) else value
                for key, value in asdict(execution).items()
            },
        }
        data = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        if len(data) > MAX_DOCUMENT_BYTES:
            return
        with Path(target).open("xb") as stream:
            stream.write(data)
    except (OSError, ValueError, TypeError):
        return


class VerifiedPayload(bytes):
    """Exact verifier output plus a process-local execution capability."""

    def __new__(cls, *_args: Any, **_kwargs: Any):
        raise TypeError("verified output requires the supervised verifier process")


def consume_receipt(path: Path, *, nonce: str, producer: str, raw: bytes, case_id: str) -> bytes:
    """Private parent boundary, called only after its fixed child is reaped."""
    raw = bytes(raw)
    try:
        document = _json(_read(path))
        if set(document) != {
            "schema_version",
            "nonce",
            "producer_identity",
            "report_sha256",
            "model_digest",
            "execution",
        }:
            return raw
        if document["schema_version"] != 1 or document["nonce"] != nonce:
            return raw
        if document["producer_identity"] != producer or producer_identity() != producer:
            return raw
        if document["report_sha256"] != hashlib.sha256(raw).hexdigest():
            return raw
        payload = _json(raw)
        if (
            document["model_digest"] != payload.get("model_digest")
            or payload.get("schema_version") != 7
        ):
            return raw
        value = dict(document["execution"])
        if set(value) != set(AuthenticatedExecution.__dataclass_fields__):
            return raw
        if (
            type(value["complete"]) is not bool
            or type(value["band"]) is not int
            or value["band"] != payload["exit_code"]
        ):
            return raw
        if value["surface"] not in {"snapshot", "derivation", "transition"}:
            return raw
        if value["extraction_route"] not in {"authenticated", "skipped", "not-applicable"}:
            return raw
        for name in ("input_scope_ids", "trace"):
            if not isinstance(value[name], list) or any(
                not isinstance(item, str) for item in value[name]
            ):
                return raw
            if value[name] != sorted(set(value[name])):
                return raw
            value[name] = frozenset(value[name])
        if (
            not isinstance(value["identity"], str)
            or len(value["identity"]) != 64
            or any(c not in "0123456789abcdef" for c in value["identity"])
        ):
            return raw
        execution = _internal_value(AuthenticatedExecution, **value)
        result = bytes.__new__(VerifiedPayload, raw)
        result.execution = execution
        result.receipt = document
        result.case_id = case_id
        return result
    except (OSError, ValueError, TypeError, KeyError):
        return raw


def bind_verified_execution(raw: bytes, evaluation: Any) -> None:
    """Private session boundary; the public report reader never invokes this."""
    if type(raw) is not VerifiedPayload or raw.case_id != evaluation.case_id:
        return
    if hashlib.sha256(raw).hexdigest() != evaluation.raw_payload_sha256:
        return
    if raw.execution.band != evaluation.payload_exit:
        return
    archive = ArchivedAssuranceReceipt(
        case_id=evaluation.case_id,
        candidate_sha256=evaluation.candidate_sha256,
        contract_sha256=evaluation.contract_sha256,
        process_receipt=ArchivedProcessReceipt.model_validate(raw.receipt),
    )
    evaluation.__pydantic_private__["_assurance_receipt"] = archive
    evaluation.__pydantic_private__["_assurance_execution"] = raw.execution
    evaluation.__pydantic_private__["_assurance_binding"] = (
        evaluation.case_id,
        evaluation.candidate_sha256,
        evaluation.contract_sha256,
        evaluation.raw_payload_sha256,
        evaluation.payload_exit,
    )


# These are archival wire types, not capability constructors. Keeping them
# distinct prevents retained JSON from taking the live consume_receipt route.


class ArchivedExecution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    production_roster_digest: str | None = Field(pattern=r"^[0-9a-f]{64}$")
    surface: Literal["snapshot", "transition", "derivation"]
    band: Literal[0, 1, 2, 3, 4, 70]
    input_scope_ids: tuple[str, ...]
    trace: tuple[str, ...]
    complete: bool
    extraction_route: Literal["not-applicable", "authenticated", "skipped"]

    @model_validator(mode="after")
    def _canonical_scope(self):
        for values in (self.input_scope_ids, self.trace):
            if values != tuple(sorted(set(values))) or len(values) > 10_000:
                raise ValueError("noncanonical archived execution scope")
        return self


class ArchivedProcessReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal[1]
    nonce: str = Field(pattern=r"^[0-9a-f]{64}$")
    producer_identity: str = Field(pattern=r"^[0-9a-f]{64}$")
    report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    execution: ArchivedExecution


class ArchivedAssuranceReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    case_id: str
    candidate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    contract_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    process_receipt: ArchivedProcessReceipt
