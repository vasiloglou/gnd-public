"""Trusted local policies for schema-v6 declared adapters.

Committed session contracts select a policy id and an optional model only. The
caller supplies this separate local document at run time; it is hashed exactly
but never copied into session evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
from pathlib import Path
from typing import Annotated, Any, Literal, Self
from urllib.parse import urlsplit, urlunsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    StringConstraints,
    TypeAdapter,
    model_validator,
)

from gnd.artifacts import reject_json_constant, reject_json_duplicate_pairs_result
from gnd.exp.session_contract import AdapterDeclaration

__all__ = [
    "MAX_ADAPTER_POLICY_BYTES",
    "AdapterPolicy",
    "AdapterPolicyError",
    "CommandAdapterPolicy",
    "OpenAICompatiblePolicy",
    "ResolvedAdapterPolicy",
    "read_adapter_policy",
]

MAX_ADAPTER_POLICY_BYTES = 256 * 1024
MAX_POLICY_ARGV_WORDS = 4096
MAX_POLICY_ENVIRONMENT_NAMES = 1024
MAX_POLICY_STRING_BYTES = 64 * 1024
MAX_HTTP_CREDENTIAL_BYTES = 16 * 1024
_ENVIRONMENT_NAME = re.compile(r"^[A-Z_][A-Z0-9_]*$")
_CREDENTIAL_TOKENS = frozenset({"KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "AUTH"})

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
PolicyId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$",
    ),
]


class AdapterPolicyError(ValueError):
    """A trusted local policy could not be read or resolved safely."""

    def __init__(self, message: str, *, kind: Literal["invalid", "missing", "io"] = "invalid"):
        self.kind = kind
        super().__init__(message)


def _credential_name(name: str) -> bool:
    return bool(_CREDENTIAL_TOKENS.intersection(name.split("_")))


def _bounded_text(value: str, *, label: str) -> str:
    if "\x00" in value or len(value.encode("utf-8")) > MAX_POLICY_STRING_BYTES:
        raise ValueError(f"{label} contains NUL or exceeds the byte cap")
    return value


class CommandAdapterPolicy(BaseModel):
    """A caller-trusted exact argv template and minimal environment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1]
    policy_id: PolicyId
    kind: Literal["command"]
    executable: NonEmptyString
    argv: tuple[str, ...] = Field(max_length=MAX_POLICY_ARGV_WORDS)
    version_argv: tuple[str, ...] = Field(min_length=1, max_length=MAX_POLICY_ARGV_WORDS)
    prompt_transport: Literal["argv", "stdin"]
    environment_allowlist: tuple[str, ...] = Field(max_length=MAX_POLICY_ENVIRONMENT_NAMES)

    @model_validator(mode="after")
    def _template_is_closed(self) -> Self:
        _bounded_text(self.executable, label="executable")
        if not self.argv:
            raise ValueError("command argv must contain at least one argument word")
        prompt_count = 0
        model_count = 0
        for label, words in (("argv", self.argv), ("version_argv", self.version_argv)):
            for word in words:
                _bounded_text(word, label=label)
                if ("{" in word or "}" in word) and (
                    label == "version_argv" or word not in {"{prompt}", "{model}"}
                ):
                    raise ValueError(
                        "template braces are allowed only as whole {prompt}/{model} argv words"
                    )
                if word == "{prompt}":
                    prompt_count += 1
                elif word == "{model}":
                    model_count += 1
        required_prompt_count = 1 if self.prompt_transport == "argv" else 0
        if prompt_count != required_prompt_count:
            raise ValueError(
                f"{self.prompt_transport} transport requires {required_prompt_count} "
                "{prompt} argv words"
            )
        if model_count > 1:
            raise ValueError("{model} may occur at most once")
        if len(set(self.environment_allowlist)) != len(self.environment_allowlist):
            raise ValueError("environment allowlist names must be unique")
        for name in self.environment_allowlist:
            if not _ENVIRONMENT_NAME.fullmatch(name):
                raise ValueError(f"invalid environment name {name!r}")
            if _credential_name(name):
                raise ValueError(f"credential environment name {name!r} is forbidden")
        return self


class OpenAICompatiblePolicy(BaseModel):
    """One caller-trusted OpenAI-compatible endpoint and credential name."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1]
    policy_id: PolicyId
    kind: Literal["openai-compatible"]
    base_url: NonEmptyString
    credential_env: NonEmptyString

    @model_validator(mode="after")
    def _endpoint_is_closed(self) -> Self:
        _bounded_text(self.base_url, label="base_url")
        if not _ENVIRONMENT_NAME.fullmatch(self.credential_env):
            raise ValueError("credential_env is not a valid environment name")
        if not _credential_name(self.credential_env):
            raise ValueError("credential_env must be recognizably credential-shaped")
        split = urlsplit(self.base_url)
        if split.scheme not in {"http", "https"}:
            raise ValueError("base_url must use HTTP or HTTPS")
        if not split.hostname or split.username is not None or split.password is not None:
            raise ValueError("base_url requires a host and forbids userinfo")
        try:
            port = split.port
        except ValueError as error:
            raise ValueError("base_url port is invalid") from error
        if port is not None and port == 0:
            raise ValueError("base_url port must be between 1 and 65535")
        if split.query or split.fragment:
            raise ValueError("base_url forbids query and fragment")
        if split.scheme == "http" and split.hostname not in {"127.0.0.1", "::1"}:
            raise ValueError("cleartext HTTP is allowed only for an IP-literal loopback host")
        return self

    @property
    def request_url(self) -> str:
        split = urlsplit(self.base_url)
        path = split.path.rstrip("/") + "/chat/completions"
        return urlunsplit((split.scheme, split.netloc, path, "", ""))


AdapterPolicy = Annotated[
    CommandAdapterPolicy | OpenAICompatiblePolicy,
    Field(discriminator="kind"),
]


class ResolvedAdapterPolicy(BaseModel):
    """Validated policy identity with process-local private values."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy: AdapterPolicy
    policy_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    model: str | None

    _environment: dict[str, str] = PrivateAttr(default_factory=dict)
    _credential_value: str | None = PrivateAttr(default=None)
    _executable_path: str | None = PrivateAttr(default=None)

    @property
    def environment(self) -> dict[str, str]:
        return dict(self._environment)

    @property
    def credential_value(self) -> str | None:
        return self._credential_value

    @property
    def executable_path(self) -> str | None:
        return self._executable_path


def _strict_document(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise AdapterPolicyError(f"adapter policy is not UTF-8: {error}") from error



    try:
        document = json.loads(
            text,
            parse_constant=reject_json_constant,
            object_pairs_hook=reject_json_duplicate_pairs_result,
        )
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise AdapterPolicyError(f"adapter policy is not strict JSON: {error}") from error
    if not isinstance(document, dict):
        raise AdapterPolicyError("adapter policy must contain a JSON object")
    return document


def _read_policy_bytes(path: str | Path) -> bytes:
    policy_path = Path(path)
    descriptor = -1
    try:
        before = policy_path.lstat()
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
            raise AdapterPolicyError("adapter policy must be a real regular file", kind="io")
        if before.st_size > MAX_ADAPTER_POLICY_BYTES:
            raise AdapterPolicyError("adapter policy exceeds the 256 KiB cap")
        descriptor = os.open(policy_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise AdapterPolicyError("adapter policy changed before it opened")
        chunks: list[bytes] = []
        remaining = MAX_ADAPTER_POLICY_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > MAX_ADAPTER_POLICY_BYTES:
            raise AdapterPolicyError("adapter policy exceeds the 256 KiB cap")
        after = policy_path.lstat()
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
        ):
            raise AdapterPolicyError("adapter policy changed while it was read")
        return raw
    except AdapterPolicyError:
        raise
    except FileNotFoundError as error:
        raise AdapterPolicyError(
            f"adapter policy could not be found: {error}", kind="missing"
        ) from error
    except OSError as error:
        raise AdapterPolicyError(f"adapter policy could not be read: {error}", kind="io") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _credential_shaped_word(word: str, environment: dict[str, str]) -> bool:
    if word.startswith("Bearer "):
        return True
    name, separator, _ = word.partition("=")
    if separator and _ENVIRONMENT_NAME.fullmatch(name) and _credential_name(name):
        return True
    return any(value and len(value) >= 4 and value in word for value in environment.values())


def read_adapter_policy(
    path: str | Path,
    *,
    declaration: AdapterDeclaration,
) -> ResolvedAdapterPolicy:
    """Read and resolve one trusted local policy against a v6 declaration."""

    raw = _read_policy_bytes(path)
    try:
        parsed = TypeAdapter(AdapterPolicy).validate_python(_strict_document(raw))
    except AdapterPolicyError:
        raise
    except Exception as error:
        raise AdapterPolicyError(f"adapter policy shape is invalid: {error}") from error
    if parsed.policy_id != declaration.policy_id:
        raise AdapterPolicyError(
            f"adapter policy id {parsed.policy_id!r} does not match contract policy id "
            f"{declaration.policy_id!r}"
        )
    model = declaration.parameters.model
    environment: dict[str, str] = {}
    credential_value: str | None = None
    executable_path: str | None = None
    if isinstance(parsed, CommandAdapterPolicy):
        has_model_word = "{model}" in parsed.argv
        if has_model_word != (model is not None):
            raise AdapterPolicyError("command {model} use must agree with the contract model")
        environment = {
            name: os.environ[name] for name in parsed.environment_allowlist if name in os.environ
        }
        executable_path = shutil.which(
            parsed.executable,
            path=environment.get("PATH", ""),
        )
        if executable_path is None:
            raise AdapterPolicyError(
                f"trusted adapter executable {parsed.executable!r} was not found",
                kind="missing",
            )
        live_credentials = {
            name: value for name, value in os.environ.items() if _credential_name(name)
        }
        for word in (*parsed.argv, *parsed.version_argv):
            if _credential_shaped_word(word, live_credentials):
                raise AdapterPolicyError("command argv contains credential-shaped content")
    else:
        if model is None:
            raise AdapterPolicyError("openai-compatible policy requires a contract model")
        credential_value = os.environ.get(parsed.credential_env)
        if not credential_value:
            raise AdapterPolicyError(
                f"required credential environment variable {parsed.credential_env!r} is missing",
                kind="missing",
            )
        if len(credential_value.encode("utf-8")) > MAX_HTTP_CREDENTIAL_BYTES:
            raise AdapterPolicyError("HTTP credential exceeds the credential byte cap")
    resolved = ResolvedAdapterPolicy(
        policy=parsed,
        policy_sha256=hashlib.sha256(raw).hexdigest(),
        model=model,
    )
    resolved._environment = environment
    resolved._credential_value = credential_value
    resolved._executable_path = executable_path
    return resolved
