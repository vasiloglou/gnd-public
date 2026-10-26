"""Host label manifests for ``gnd measure --labels`` (IK3).

A label manifest (``gnd-labels/1``, ``src/gnd/labels.schema.json``, closed) lets
a host measure the checker over populations it labelled itself, instead of over
``gnd synth`` output and its sidecars. Contract page:
``docs/reference/measure-labels.md``.

The reader is total over arbitrary input. Every refusal is a :class:`LabelError`
carrying its exit code, raised before any population is scored:

- the manifest is missing (66) or a symbolic link (74);
- it is over :data:`MANIFEST_CAP` bytes, is not RF7 JSON (depth over 64, a
  duplicate key, a non-finite number), or fails the schema (3);
- it names another model, an unknown ``id``, a positional ref to a constraint
  that has an ``id``, or a ref past the end; it leaves a constraint unlabelled
  in expected-state mode (IK3-D4); or a label contradicts the cell table (3).

Populations are then resolved one at a time under the manifest's directory: an
escape or a missing file is 3, a symbolic link is 74, a digest mismatch is 3,
and a population that fails to load is 5. Each is read once, so the bytes that
were digested are the bytes that are checked.
"""

from __future__ import annotations

import errno
import hashlib
import os
import stat
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gnd import input_policy as _rf7_input
from gnd.checker import CheckReport
from gnd.exits import EXIT_GENERATOR, EXIT_ILL_FORMED, EXIT_IO, EXIT_NO_INPUT
from gnd.model_index import ModelIndex
from gnd.synth.provenance import ExpectedState

__all__ = [
    "MANIFEST_CAP",
    "LabelError",
    "LabelManifest",
    "LabelledPopulation",
    "RefTable",
    "bind_manifest",
    "read_label_manifest",
    "read_population",
    "score_populations",
]

#: IK3-D5: the manifest byte cap. It dominates the schema's 10,000-population
#: bound, which stays as defence in depth (corpus finding C-F3).
MANIFEST_CAP = 1024 * 1024
LABELS_SCHEMA_VERSION = "gnd-labels/1"


class LabelError(Exception):
    """A refused manifest, binding, ref or population, with its exit code."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class LabelManifest:
    """A schema-valid manifest, its path and the digest of its bytes."""

    path: Path
    sha256: str
    document: dict[str, Any]

    @property
    def mode(self) -> str:
        return str(self.document["mode"])


@dataclass(frozen=True)
class LabelledPopulation:
    """One scored population: the measure report's row and defect builders read
    ``population_path``, ``report`` and ``sidecar``. A host label has no sidecar,
    so the synth-only views (wrong attribution, set-attributed evidence, the
    defect row's ``sidecar`` and ``seed``) are absent (corpus findings C-F1, C-F2)."""

    id: str
    population_path: str
    population_sha256: str
    report: CheckReport
    expectations: dict[str, ExpectedState] = field(default_factory=dict)
    class_: str | None = None
    sidecar: None = None
    sidecar_path: None = None


@dataclass(frozen=True)
class RefTable:
    """The model's constraints keyed by the forms a manifest may use (D5 (o))."""

    positional: tuple[str, ...]
    by_id: dict[str, str]
    id_bearing: frozenset[str]
    constraints: dict[str, dict[str, Any]]

    @classmethod
    def for_model(cls, model: Any) -> RefTable:
        positional: list[str] = []
        by_id: dict[str, str] = {}
        constraints: dict[str, dict[str, Any]] = {}
        for ref, constraint, _fact_type in ModelIndex.for_model(model).iter_constraints():
            positional.append(ref)
            constraints[ref] = constraint
            identifier = constraint.get("id")
            if isinstance(identifier, str) and identifier:
                if identifier in by_id:
                    raise LabelError(
                        EXIT_ILL_FORMED,
                        f"constraint id {identifier!r} is declared twice in the model; "
                        "an id ref would be ambiguous",
                    )
                by_id[identifier] = ref
        return cls(tuple(positional), by_id, frozenset(by_id.values()), constraints)

    def resolve(self, ref: str) -> str:
        """The checker's positional ref for one manifest ref, or exit 3 naming it."""
        if ref.startswith("id:"):
            identifier = ref[3:]
            if identifier not in self.by_id:
                raise LabelError(EXIT_ILL_FORMED, f"ref {ref!r}: no constraint has id {identifier!r}")
            return self.by_id[identifier]
        if ref not in self.constraints:
            raise LabelError(EXIT_ILL_FORMED, f"ref {ref!r} names no constraint in the model")
        if ref in self.id_bearing:
            identifier = self.constraints[ref]["id"]
            raise LabelError(
                EXIT_ILL_FORMED,
                f"ref {ref!r} is positional but that constraint has an id; write 'id:{identifier}'",
            )
        return ref


def _schema() -> Draft202012Validator:
    text = files("gnd").joinpath("labels.schema.json").read_text(encoding="utf-8")
    return Draft202012Validator(_rf7_input.loads(text))


def _strings(document: dict[str, Any]) -> list[tuple[str, str]]:
    """Every pattern-governed string, for the whitespace check the schema's
    ``$`` cannot make (it matches before a final newline; IK2 S1)."""
    out = [("model_sha256", document["model_sha256"])]
    for index, population in enumerate(document["populations"]):
        base = f"populations[{index}]"
        out.extend((f"{base}.{key}", population[key]) for key in ("id", "path", "sha256"))
        out.extend((f"{base}.expectations", ref) for ref in population.get("expectations", {}))
    out.extend(("rules", ref) for ref in document.get("rules", {}))
    return out


def read_label_manifest(path: Path) -> LabelManifest:
    """Read, decode and schema-validate one manifest; the caller binds it later."""
    if path.is_symlink():
        raise LabelError(EXIT_IO, f"refusing label manifest {path}: it is a symbolic link")
    try:
        # Non-blocking and no-follow, so a FIFO or a swapped-in link cannot hang
        # or redirect the read (IK3 review R1).
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
    except FileNotFoundError:
        raise LabelError(EXIT_NO_INPUT, f"label manifest {path} does not exist") from None
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise LabelError(EXIT_IO, f"refusing label manifest {path}: it is a symbolic link") from None
        raise LabelError(EXIT_ILL_FORMED, f"could not read label manifest {path}: {error}") from None
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise LabelError(EXIT_ILL_FORMED, f"label manifest {path} is not a regular file")
        chunks: list[bytes] = []
        remaining = MANIFEST_CAP + 1
        while remaining > 0:
            chunk = os.read(descriptor, remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
    except OSError as error:
        raise LabelError(EXIT_ILL_FORMED, f"could not read label manifest {path}: {error}") from None
    finally:
        os.close(descriptor)
    if len(data) > MANIFEST_CAP:
        raise LabelError(
            EXIT_ILL_FORMED, f"label manifest {path} exceeds the {MANIFEST_CAP}-byte cap"
        )
    try:
        document = _rf7_input.loads(data)
    except (ValueError, TypeError) as error:
        raise LabelError(EXIT_ILL_FORMED, f"label manifest {path} is not valid JSON: {error}") from None
    errors = sorted(_schema().iter_errors(document), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        where = "/".join(str(part) for part in first.absolute_path) or "(root)"
        raise LabelError(
            EXIT_ILL_FORMED, f"label manifest {path} fails {LABELS_SCHEMA_VERSION} at {where}: {first.message}"
        )
    for where, value in _strings(document):
        if any(character.isspace() for character in value):
            raise LabelError(EXIT_ILL_FORMED, f"label manifest {path}: {where} contains whitespace")
    seen: set[str] = set()
    for population in document["populations"]:
        if population["id"] in seen:
            raise LabelError(
                EXIT_ILL_FORMED, f"label manifest {path}: population id {population['id']!r} repeats"
            )
        seen.add(population["id"])
    return LabelManifest(path, hashlib.sha256(data).hexdigest(), document)


@dataclass(frozen=True)
class BoundManifest:
    """A manifest bound to one model: every ref resolved to its positional form."""

    manifest: LabelManifest
    table: RefTable
    expectations: tuple[dict[str, ExpectedState], ...]
    rules: dict[str, str]


def bind_manifest(manifest: LabelManifest, model: Any, model_sha256: str) -> BoundManifest:
    """Bind the manifest to the model before any population is read (§4 rule 3)."""
    from gnd.measure.score import CellLookupError, classify

    digest = model_sha256
    if manifest.document["model_sha256"] != digest:
        raise LabelError(
            EXIT_ILL_FORMED,
            f"label manifest {manifest.path} was written for model sha256 "
            f"{manifest.document['model_sha256']}, not this model ({digest})",
        )
    table = RefTable.for_model(model)
    expectations: list[dict[str, ExpectedState]] = []
    rules: dict[str, str] = {}
    if manifest.mode == "class":
        for ref, rule in manifest.document["rules"].items():
            positional = table.resolve(ref)
            if positional in rules:
                raise LabelError(EXIT_ILL_FORMED, f"rules name {positional} twice")
            rules[positional] = rule["fires_on"]
        return BoundManifest(manifest, table, (), dict(sorted(rules.items())))
    declared = set(table.positional)
    for population in manifest.document["populations"]:
        bound: dict[str, ExpectedState] = {}
        for ref, label in population["expectations"].items():
            positional = table.resolve(ref)
            if positional in bound:
                raise LabelError(
                    EXIT_ILL_FORMED, f"population {population['id']!r} labels {positional} twice"
                )
            state = ExpectedState(**label)
            modality = str(table.constraints[positional].get("modality") or "alethic")
            try:
                classify(state, state.expected_verdict, modality)
            except CellLookupError as error:
                raise LabelError(
                    EXIT_ILL_FORMED,
                    f"population {population['id']!r}, ref {ref!r}: {error}",
                ) from None
            bound[positional] = state
        missing = sorted(declared - set(bound))
        if missing:
            raise LabelError(
                EXIT_ILL_FORMED,
                f"population {population['id']!r} leaves {missing} unlabelled; "
                "expected-state mode labels every constraint (IK3-D4)",
            )
        expectations.append(bound)
    return BoundManifest(manifest, table, tuple(expectations), {})


def _population_bytes(root: Path, relative: str) -> tuple[Path, bytes]:
    """Read one population beneath the manifest's directory, never through a link.

    Each component is inspected without following links first, so a symbolic
    link anywhere on the path is a named refusal (74) and a FIFO or directory is
    refused before any open (IK3 review R1, R2). The read itself goes through
    the no-follow, regular-only descriptor reader, so a link swapped in after
    the inspection is refused too (3)."""
    from gnd.artifacts import ArtifactError
    from gnd.population import MAX_POPULATION_BYTES
    from gnd.safefs import read_regular_bounded

    current = root
    parts = relative.split("/")
    for position, part in enumerate(parts):
        current = current / part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            raise LabelError(EXIT_ILL_FORMED, f"population {relative!r} does not exist") from None
        except OSError as error:
            raise LabelError(EXIT_ILL_FORMED, f"could not read population {relative!r}: {error}") from None
        if stat.S_ISLNK(info.st_mode):
            raise LabelError(EXIT_IO, f"refusing population {relative!r}: it passes through a symbolic link")
        leaf = position == len(parts) - 1
        if not leaf and not stat.S_ISDIR(info.st_mode):
            raise LabelError(EXIT_ILL_FORMED, f"population {relative!r} does not exist")
    if not stat.S_ISREG(info.st_mode):
        raise LabelError(EXIT_ILL_FORMED, f"population {relative!r} is not a regular file")
    if info.st_size > MAX_POPULATION_BYTES:
        raise LabelError(
            EXIT_GENERATOR, f"population {relative!r} exceeds the {MAX_POPULATION_BYTES}-byte cap"
        )
    try:
        data, _snapshot = read_regular_bounded(root, relative, max_bytes=MAX_POPULATION_BYTES)
    except (ArtifactError, OSError) as error:
        raise LabelError(
            EXIT_ILL_FORMED, f"population {relative!r} could not be read safely: {error}"
        ) from None
    return current, data


def read_population(manifest: LabelManifest, entry: dict[str, Any], model: Any) -> Any:
    """One manifest population, resolved, digest-checked and loaded against
    ``model`` from the bytes that were digested. The one population reader for
    ``gnd measure --labels`` and the ILP bridge (IK5)."""
    from gnd.population import load_population_bytes

    relative = entry["path"]
    candidate, data = _population_bytes(manifest.path.parent, relative)
    digest = hashlib.sha256(data).hexdigest()
    if digest != entry["sha256"]:
        raise LabelError(
            EXIT_ILL_FORMED,
            f"population {relative!r} has sha256 {digest}, not the manifest's {entry['sha256']}",
        )
    try:
        return load_population_bytes(data, source=candidate, model=model)
    except Exception as error:  # noqa: BLE001 -- a load failure is exit 5, as on the synth path
        raise LabelError(EXIT_GENERATOR, f"population {relative!r} failed to load: {error}") from None


def score_populations(bound: BoundManifest, model: Any) -> tuple[list[LabelledPopulation], int]:
    """Load and check every population, in manifest order; returns them and the
    number of checker runs. Identical bytes at one path are checked once (the
    checker is deterministic over (model, bytes)), so the count is the work
    actually done, not the manifest's length (IK3 review R5)."""
    from gnd.checker import check

    reports: dict[tuple[str, str], CheckReport] = {}
    scored: list[LabelledPopulation] = []
    checked = 0
    for index, population in enumerate(bound.manifest.document["populations"]):
        relative = population["path"]
        key = (relative, population["sha256"])
        if key not in reports:
            reports[key] = check(model, read_population(bound.manifest, population, model))
            checked += 1
        scored.append(
            LabelledPopulation(
                id=population["id"],
                population_path=relative,
                population_sha256=population["sha256"],
                report=reports[key],
                expectations=bound.expectations[index] if bound.expectations else {},
                class_=population.get("class"),
            )
        )
    return scored, checked
