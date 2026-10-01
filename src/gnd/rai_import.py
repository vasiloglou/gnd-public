"""Deterministic import of the bounded ``rai-orm-from-schema`` dialect."""

from __future__ import annotations

import hashlib
import json
import math
import re
import stat
import tempfile
from collections import deque
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from importlib.resources import files
from io import StringIO
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from ruamel.yaml.events import AliasEvent, DocumentStartEvent

from gnd.artifacts import (
    ArtifactError,
    canonical_json_bytes,
    publish_directory_once,
    read_regular_bounded,
)
from gnd.model import MAX_MODEL_BYTES, MAX_YAML_EVENTS, ModelValidationError, load_model

MAX_RAI_MODEL_BYTES = MAX_MODEL_BYTES
RAI_ALIAS_SCHEMA_VERSION = 1
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
_CAMEL_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
_CAMEL_2 = re.compile(r"([a-z0-9])([A-Z])")


class RaiImportError(Exception):
    """A named, input-caused import refusal."""

    def __init__(self, rule_id: str, pointer: str, message: str):
        self.rule_id = rule_id
        self.pointer = pointer
        self.message = message
        super().__init__(f"{rule_id} at {pointer}: {message}")


class RaiImportCollision(RaiImportError):
    """The create-once output directory already exists."""


class RaiImportIO(RaiImportError):
    """A bounded input read or descriptor-bound publication failed."""


class RaiImportMissing(RaiImportError):
    """A required import input is missing."""


@dataclass(frozen=True)
class RaiImportRequest:
    model_path: Path
    output_dir: Path
    source_artifact: str
    source_commit: str | None


@dataclass(frozen=True)
class RaiImportResult:
    model_bytes: bytes
    alias_bytes: bytes
    input_sha256: str
    output_sha256: str
    rewrites: tuple[str, ...]


def _refuse(rule: str, pointer: str, message: str) -> RaiImportError:
    return RaiImportError(f"rai-import:{rule}", pointer, message)


def _caused_by(error: BaseException, kind: type[BaseException]) -> bool:
    current: BaseException | None = error
    while current is not None:
        if isinstance(current, kind):
            return True
        current = current.__cause__ or current.__context__
    return False


def _guard_scalar(value: Any, *, depth: int = 0) -> None:
    if depth > 128:
        raise _refuse("parse", "$", "document nesting exceeds the 128-level import cap")
    if isinstance(value, float) and not math.isfinite(value):
        raise _refuse("parse", "$", "non-finite numbers are not admitted")
    if isinstance(value, int) and len(str(abs(value))) > 1_000:
        raise _refuse("parse", "$", "integer token exceeds the 1,000-digit import cap")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _guard_scalar(key, depth=depth + 1)
            _guard_scalar(child, depth=depth + 1)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _guard_scalar(child, depth=depth + 1)


def parse_rai_model_bytes(data: bytes, *, source: str) -> MutableMapping[str, Any]:
    """Parse one plain UTF-8 YAML mapping or raise a named total refusal."""

    try:
        text = data.decode("utf-8")
        yaml = YAML(typ="rt")
        yaml.preserve_quotes = True
        documents = 0
        for count, event in enumerate(yaml.parse(text), start=1):
            if count > MAX_YAML_EVENTS:
                raise _refuse("parse", "$", "YAML event cap exceeded")
            if isinstance(event, AliasEvent):
                raise _refuse("parse", "$", "YAML aliases are not admitted")
            if isinstance(event, DocumentStartEvent):
                documents += 1
        if documents != 1:
            raise _refuse("parse", "$", "exactly one YAML document is required")
        document = yaml.load(text)
        if not isinstance(document, MutableMapping):
            raise _refuse("parse", "$", "the document root must be a mapping")
        _guard_scalar(document)
        return document
    except RaiImportError:
        raise
    except Exception as error:
        raise _refuse("parse", "$", f"{type(error).__name__}: {error}") from error


def _valid_model_bytes(data: bytes) -> bool:
    with tempfile.TemporaryDirectory(prefix="gnd-rai-identity-") as directory:
        path = Path(directory) / "model.orm.yaml"
        path.write_bytes(data)
        try:
            load_model(path)
        except Exception:  # noqa: BLE001 - false means the dialect arm classifies it
            return False
    return True


def _snake(value: str, pointer: str) -> str:
    if not value or not value.isascii():
        raise _refuse("role-name", pointer, "role name must be non-empty ASCII")
    converted = _CAMEL_2.sub(r"\1_\2", _CAMEL_1.sub(r"\1_\2", value)).lower()
    if not _IDENTIFIER.fullmatch(converted):
        raise _refuse("role-name", pointer, f"{value!r} has no admitted snake-case form")
    return converted


def _insert_before(mapping: MutableMapping[str, Any], before: str, key: str, value: Any) -> None:
    if hasattr(mapping, "insert") and before in mapping:
        mapping.insert(list(mapping).index(before), key, value)
    else:
        mapping[key] = value


def _default_modality(constraint: Mapping[str, Any], pointer: str) -> str:
    source = constraint.get("source")
    status = constraint.get("status")
    if (source, status) in {("explicit", "confirmed"), ("user-supplied", "confirmed")}:
        return "alethic"
    if source in {"sample", "common-sense", "llm-inferred", "imported"}:
        if status == "proposed":
            return "deontic"
        if status == "confirmed":
            if source == "imported" and not isinstance(constraint.get("provenance"), Mapping):
                raise _refuse(
                    "modality", pointer, "imported/confirmed requires reviewed provenance"
                )
            if source == "imported" and not constraint["provenance"].get("reviewed_in"):
                raise _refuse("modality", pointer, "imported/confirmed requires reviewed_in")
            return "alethic"
    raise _refuse(
        "modality",
        pointer,
        f"no D-03 default exists for source/status {source!r}/{status!r}",
    )


def _rewrite_reference_node(
    node: Any,
    role_maps: Mapping[str, Mapping[str, str]],
    *,
    context_fact: str | None,
) -> None:
    if isinstance(node, MutableMapping):
        fact = node.get("fact_type") if isinstance(node.get("fact_type"), str) else context_fact
        mapping = role_maps.get(str(fact), {}) if fact is not None else {}
        if isinstance(node.get("role"), str) and node["role"] in mapping:
            node["role"] = mapping[node["role"]]
        if isinstance(node.get("roles"), list):
            node["roles"] = [
                mapping.get(value, value) if isinstance(value, str) else value
                for value in node["roles"]
            ]
        for key, value in list(node.items()):
            if key != "roles":
                _rewrite_reference_node(value, role_maps, context_fact=context_fact)
    elif isinstance(node, list):
        for child in node:
            _rewrite_reference_node(child, role_maps, context_fact=context_fact)


def _rewrite_reading(reading: str, mapping: Mapping[str, str]) -> str:
    pattern = re.compile(r"\{([^{}:]+):([^{}]+)\}")
    return pattern.sub(
        lambda match: "{" + match[1] + ":" + mapping.get(match[2], match[2]) + "}", reading
    )


def _guard_dialect_shape(document: Mapping[str, Any]) -> None:
    """Make the admitted rewrite arm total before any structural traversal."""

    for key in ("object_types", "fact_types", "constraints"):
        value = document.get(key)
        if not isinstance(value, list):
            raise _refuse("unsupported", f"/{key}", f"{key} must be an array")

    for object_index, object_type in enumerate(document["object_types"]):
        if not isinstance(object_type, MutableMapping):
            raise _refuse(
                "unsupported",
                f"/object_types/{object_index}",
                "object type must be a mapping",
            )

    for fact_index, fact in enumerate(document["fact_types"]):
        pointer = f"/fact_types/{fact_index}"
        if not isinstance(fact, MutableMapping):
            raise _refuse("unsupported", pointer, "fact type must be a mapping")
        if not isinstance(fact.get("roles"), list):
            raise _refuse("unsupported", f"{pointer}/roles", "roles must be an array")
        for role_index, role in enumerate(fact["roles"]):
            if not isinstance(role, MutableMapping):
                raise _refuse(
                    "unsupported",
                    f"{pointer}/roles/{role_index}",
                    "role must be a mapping",
                )
        inline_constraints = fact.get("constraints", [])
        if not isinstance(inline_constraints, list):
            raise _refuse(
                "unsupported",
                f"{pointer}/constraints",
                "constraints must be an array",
            )
        for constraint_index, constraint in enumerate(inline_constraints):
            if not isinstance(constraint, MutableMapping):
                raise _refuse(
                    "unsupported",
                    f"{pointer}/constraints/{constraint_index}",
                    "constraint must be a mapping",
                )

    for constraint_index, constraint in enumerate(document["constraints"]):
        if not isinstance(constraint, MutableMapping):
            raise _refuse(
                "unsupported",
                f"/constraints/{constraint_index}",
                "constraint must be a mapping",
            )


def _all_constraints(
    document: Mapping[str, Any],
) -> list[tuple[MutableMapping[str, Any], str, str | None]]:
    rows: list[tuple[MutableMapping[str, Any], str, str | None]] = []
    for fact_index, fact in enumerate(document.get("fact_types") or []):
        fact_id = str(fact.get("id"))
        for constraint_index, constraint in enumerate(fact.get("constraints") or []):
            if isinstance(constraint, MutableMapping):
                rows.append(
                    (
                        constraint,
                        f"/fact_types/{fact_index}/constraints/{constraint_index}",
                        fact_id,
                    )
                )
    for index, constraint in enumerate(document.get("constraints") or []):
        if isinstance(constraint, MutableMapping):
            rows.append((constraint, f"/constraints/{index}", None))
    return rows


def _render_model(document: Mapping[str, Any]) -> bytes:
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.width = 100
    stream = StringIO()
    yaml.dump(document, stream)
    lines = [line.rstrip(" \t") for line in stream.getvalue().splitlines()]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _validate_target(data: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="gnd-rai-target-") as directory:
        path = Path(directory) / "model.orm.yaml"
        path.write_bytes(data)
        try:
            load_model(path)
        except ModelValidationError as error:
            first = error.issues[0] if error.issues else None
            detail = f"{first.path}: {first.message}" if first else str(error)
            raise _refuse("target-invalid", "$", detail) from error
        except Exception as error:
            raise _refuse("target-invalid", "$", f"{type(error).__name__}: {error}") from error


def _stable_artifact(value: str) -> bool:
    if not value or "\\" in value or PureWindowsPath(value).is_absolute():
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in value.split("/"))


def _substring_counts(text: str, needles: set[str]) -> dict[str, int]:
    edges: list[dict[str, int]] = [{}]
    failure = [0]
    terminals: dict[str, int] = {}
    for needle in needles:
        state = 0
        for character in needle:
            state = edges[state].setdefault(character, len(edges))
            if state == len(edges):
                edges.append({})
                failure.append(0)
        terminals[needle] = state
    order: list[int] = []
    queue = deque(edges[0].values())
    while queue:
        state = queue.popleft()
        order.append(state)
        for character, target in edges[state].items():
            fallback = failure[state]
            while fallback and character not in edges[fallback]:
                fallback = failure[fallback]
            failure[target] = edges[fallback].get(character, 0)
            queue.append(target)
    visits = [0] * len(edges)
    state = 0
    for character in text:
        while state and character not in edges[state]:
            state = failure[state]
        state = edges[state].get(character, 0)
        visits[state] += 1
    for state in reversed(order):
        visits[failure[state]] += visits[state]
    return {needle: visits[state] for needle, state in terminals.items()}


def _alias_document(
    request: RaiImportRequest,
    input_sha: str,
    output_sha: str,
    roles: list[dict[str, str]],
    constraints: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": RAI_ALIAS_SCHEMA_VERSION,
        "dialect": "rai-orm",
        "source": {
            "artifact": request.source_artifact,
            "commit": request.source_commit,
            "sha256": input_sha,
        },
        "output": {"filename": "model.orm.yaml", "sha256": output_sha},
        "roles": sorted(roles, key=lambda row: (row["source_pointer"], row["output_pointer"])),
        "constraints": sorted(
            constraints, key=lambda row: (row["source_pointer"], row["output_pointer"])
        ),
    }


def plan_rai_import(request: RaiImportRequest) -> RaiImportResult:
    """Read, classify, rewrite and validate without touching ``output_dir``."""

    if not _stable_artifact(request.source_artifact):
        raise _refuse("provenance", "$", "source artifact must be a stable relative POSIX path")
    if request.source_commit is not None and not request.source_commit:
        raise _refuse("provenance", "$", "source commit must be non-empty when supplied")
    try:
        data, _snapshot = read_regular_bounded(
            request.model_path.parent,
            request.model_path.name,
            max_bytes=MAX_RAI_MODEL_BYTES,
        )
    except ArtifactError as error:
        if _caused_by(error, FileNotFoundError):
            raise RaiImportMissing("rai-import:missing", "$", str(error)) from error
        rule = "size" if "byte cap" in str(error) else "io"
        cls = RaiImportIO
        raise cls(f"rai-import:{rule}", "$", str(error)) from error
    input_sha = hashlib.sha256(data).hexdigest()
    if _valid_model_bytes(data):
        alias = _alias_document(request, input_sha, input_sha, [], [])
        alias_bytes = canonical_json_bytes(alias)
        Draft202012Validator(
            json.loads(files("gnd").joinpath("rai-alias.schema.json").read_text(encoding="utf-8"))
        ).validate(alias)
        return RaiImportResult(data, alias_bytes, input_sha, input_sha, ())

    document = parse_rai_model_bytes(data, source=str(request.model_path))
    _guard_dialect_shape(document)
    if "unsupported" in document or any(
        isinstance(row, Mapping) and "dialect_extension" in row for row in document["object_types"]
    ):
        raise _refuse("unsupported", "$", "document contains an unadmitted dialect shape")

    rewrites: list[str] = []
    role_aliases: list[dict[str, str]] = []
    constraint_aliases: list[dict[str, str]] = []
    original_constraints = _all_constraints(document)

    # 1. Missing modality on the two admitted inline families.
    modality_changed = False
    for constraint, pointer, fact_id in original_constraints:
        if fact_id is None or constraint.get("type") not in {"uniqueness", "mandatory"}:
            continue
        modality = _default_modality(constraint, pointer)
        if "modality" not in constraint:
            before = "rationale" if "rationale" in constraint else "provenance"
            _insert_before(constraint, before, "modality", modality)
            modality_changed = True
        elif constraint["modality"] != modality:
            raise _refuse("modality", pointer, "existing modality conflicts with D-03")
    if modality_changed:
        rewrites.append("modality")

    # 2. Fact-scoped role declarations and every admitted reference site.
    role_maps: dict[str, dict[str, str]] = {}
    role_changed = False
    for fact_index, fact in enumerate(document["fact_types"]):
        if not isinstance(fact, MutableMapping) or not isinstance(fact.get("roles"), list):
            raise _refuse("unsupported", f"/fact_types/{fact_index}", "invalid fact shape")
        fact_id = str(fact.get("id"))
        mapping: dict[str, str] = {}
        unnamed_types = [
            str(role.get("object_type"))
            for role in fact["roles"]
            if isinstance(role, Mapping) and "role_name" not in role
        ]
        if len(unnamed_types) != len(set(unnamed_types)):
            raise _refuse(
                "role-name",
                f"/fact_types/{fact_index}/roles",
                "repeated unnamed object types are ambiguous",
            )
        produced: set[str] = set()
        for role_index, role in enumerate(fact["roles"]):
            if not isinstance(role, MutableMapping):
                raise _refuse(
                    "role-name",
                    f"/fact_types/{fact_index}/roles/{role_index}",
                    "role must be a mapping",
                )
            source_pointer = f"/fact_types/{fact_index}/roles/{role_index}/role_name"
            if "role_name" in role:
                old = str(role["role_name"])
                new = _snake(old, source_pointer)
            else:
                old = str(role.get("object_type"))
                new = _snake(old, f"/fact_types/{fact_index}/roles/{role_index}")
                source_pointer = f"/fact_types/{fact_index}/roles/{role_index}"
            if new in produced:
                raise _refuse("role-name", source_pointer, f"normalized role {new!r} collides")
            produced.add(new)
            mapping[old] = new
            if role.get("role_name") != new:
                role["role_name"] = new
                role_changed = True
                role_aliases.append(
                    {
                        "source_pointer": source_pointer,
                        "source_name": old,
                        "output_pointer": f"/fact_types/{fact_index}/roles/{role_index}/role_name",
                        "output_name": new,
                    }
                )
        role_maps[fact_id] = mapping
    for fact in document["fact_types"]:
        fact_id = str(fact.get("id"))
        mapping = role_maps[fact_id]
        if isinstance(fact.get("reading"), str):
            fact["reading"] = _rewrite_reading(fact["reading"], mapping)
        for constraint in fact.get("constraints") or []:
            _rewrite_reference_node(constraint, role_maps, context_fact=fact_id)
    for constraint in document["constraints"]:
        _rewrite_reference_node(constraint, role_maps, context_fact=None)
    if role_changed:
        rewrites.append("role-name")

    # 3. Relocate top-level rings to their declared binary fact type.
    facts_by_id = {
        str(fact.get("id")): (index, fact) for index, fact in enumerate(document["fact_types"])
    }
    retained: list[Any] = []
    ring_changed = False
    for source_index, constraint in enumerate(document["constraints"]):
        if not isinstance(constraint, MutableMapping) or constraint.get("type") != "ring":
            retained.append(constraint)
            continue
        target_id = constraint.get("fact_type")
        allowed = {
            "id",
            "type",
            "variant",
            "fact_type",
            "source",
            "status",
            "modality",
            "rationale",
            "provenance",
        }
        if set(constraint) - allowed or "variant" not in constraint:
            raise _refuse(
                "ring-placement",
                f"/constraints/{source_index}",
                "ring carries an incompatible dialect shape",
            )
        if not isinstance(target_id, str):
            raise _refuse(
                "ring-placement",
                f"/constraints/{source_index}/fact_type",
                "ring target must be a fact-type identifier",
            )
        if target_id not in facts_by_id:
            raise _refuse(
                "ring-placement", f"/constraints/{source_index}", "ring target does not exist"
            )
        fact_index, target = facts_by_id[str(target_id)]
        if len(target.get("roles") or []) != 2:
            raise _refuse(
                "ring-placement", f"/constraints/{source_index}", "ring target is not binary"
            )
        constraint.pop("fact_type")
        target.setdefault("constraints", []).append(constraint)
        output_index = len(target["constraints"]) - 1
        constraint_aliases.append(
            {
                "source_pointer": f"/constraints/{source_index}",
                "output_pointer": f"/fact_types/{fact_index}/constraints/{output_index}",
                "rewrite": "ring-placement",
            }
        )
        ring_changed = True
    if ring_changed:
        document["constraints"] = retained
        rewrites.append("ring-placement")

    # 4. Every missing-provenance constraint uses an exact source-byte anchor.
    provenance_changed = False
    text = data.decode("utf-8")
    missing_by_fact: dict[str, list[str]] = {}
    for constraint, pointer, fact_id in original_constraints:
        if "provenance" not in constraint and fact_id is not None:
            missing_by_fact.setdefault(fact_id, []).append(pointer)
    ambiguous_fact = next(
        ((fact_id, pointers) for fact_id, pointers in missing_by_fact.items() if len(pointers) > 1),
        None,
    )
    if ambiguous_fact is not None:
        fact_id, pointers = ambiguous_fact
        raise _refuse(
            "provenance",
            pointers[0],
            f"fact {fact_id!r} has multiple missing-provenance constraints and no "
            "unambiguous admitted anchor",
        )
    anchors = {
        f"- id: {fact_id}" if fact_id is not None else str(constraint.get("rationale"))
        for constraint, _pointer, fact_id in original_constraints
        if "provenance" not in constraint
    }
    anchor_counts = _substring_counts(text, anchors)
    for constraint, pointer, fact_id in original_constraints:
        if "provenance" in constraint:
            continue
        if constraint.get("type") not in {"mandatory", "mandatory-disjunctive"}:
            raise _refuse(
                "provenance", pointer, "missing provenance is outside the admitted corpus classes"
            )
        if (
            constraint.get("source"),
            constraint.get("status"),
            constraint.get("modality"),
        ) not in {
            ("explicit", "confirmed", "alethic"),
            ("user-supplied", "confirmed", "alethic"),
        }:
            raise _refuse(
                "provenance", pointer, "missing provenance has an unapproved source tuple"
            )
        if not request.source_commit:
            raise _refuse("provenance", pointer, "--source-commit is required")
        anchor = f"- id: {fact_id}" if fact_id is not None else constraint.get("rationale")
        if not isinstance(anchor, str) or not anchor or anchor_counts.get(anchor) != 1:
            raise _refuse("provenance", pointer, "no unique verbatim source anchor exists")
        constraint["source"] = "imported"
        constraint["status"] = "proposed"
        constraint["modality"] = "deontic"
        constraint["provenance"] = {
            "framework": "rai-orm-from-schema",
            "artifact": request.source_artifact,
            "commit": request.source_commit,
            "sha256": input_sha,
            "anchor": anchor,
        }
        provenance_changed = True
    if provenance_changed:
        rewrites.append("provenance")

    model_bytes = _render_model(document)
    try:
        _validate_target(model_bytes)
    except RaiImportError as error:
        if not rewrites:
            raise _refuse(
                "unsupported", "$", "document differs outside the four admitted rewrites"
            ) from error
        raise
    output_sha = hashlib.sha256(model_bytes).hexdigest()
    alias = _alias_document(request, input_sha, output_sha, role_aliases, constraint_aliases)
    schema = json.loads(files("gnd").joinpath("rai-alias.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(alias)
    return RaiImportResult(
        model_bytes,
        canonical_json_bytes(alias),
        input_sha,
        output_sha,
        tuple(rewrites),
    )


def publish_rai_import(request: RaiImportRequest, result: RaiImportResult) -> None:
    """Publish the validated pair create-once, with the alias map last."""

    try:
        parent_info = request.output_dir.parent.lstat()
    except OSError as error:
        raise RaiImportIO("rai-import:io", "/out", str(error)) from error
    if not stat.S_ISDIR(parent_info.st_mode):
        raise RaiImportIO("rai-import:io", "/out", "output parent is not a real directory")
    try:
        output_info = request.output_dir.lstat()
    except FileNotFoundError:
        output_info = None
    except OSError as error:
        raise RaiImportIO("rai-import:io", "/out", str(error)) from error
    if output_info is not None:
        if stat.S_ISDIR(output_info.st_mode):
            raise RaiImportCollision(
                "rai-import:collision", "/out", "output directory already exists"
            )
        raise RaiImportIO("rai-import:io", "/out", "output leaf is not a real directory")
    try:
        publish_directory_once(
            request.output_dir.parent,
            request.output_dir.name,
            {"model.orm.yaml": result.model_bytes, "aliases.json": result.alias_bytes},
            manifest_name="aliases.json",
        )
    except (ArtifactError, OSError) as error:
        if isinstance(error, ArtifactError) and "artifact publication collision:" in str(error):
            raise RaiImportCollision(
                "rai-import:collision", "/out", "output directory already exists"
            ) from error
        raise RaiImportIO("rai-import:io", "/out", str(error)) from error
