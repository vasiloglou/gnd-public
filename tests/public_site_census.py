"""Current construction-site observer; authenticated-copy refusal, no certificates."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath

from support.rf5_sources import HOMES

from gnd import semantic_registry


class InputError(Exception):
    """Evidence input is missing, unreadable, malformed or outside its bounds."""


def read_capped(path: Path, *, limit: int) -> bytes:
    """Bound the read itself, including files that grow after a metadata read."""
    if limit < 0:
        raise InputError("a byte cap must be nonnegative")
    try:
        with path.open("rb") as handle:
            raw = handle.read(limit + 1)
    except OSError as error:
        raise InputError(f"{path}: {error}") from error
    if len(raw) > limit:
        raise InputError(f"{path}: exceeds the {limit}-byte cap")
    return raw


MAX_EVIDENCE_MEMBER_BYTES = 10 * 1024 * 1024


def _read_member(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("installed evidence member is not a regular file")
    try:
        return read_capped(path, limit=MAX_EVIDENCE_MEMBER_BYTES)
    except InputError as error:
        raise ValueError("installed evidence member exceeds its read bound") from error


def _pairs(values):
    result = {}
    for key, value in values:
        if key in result:
            raise ValueError("duplicate evidence key")
        result[key] = value
    return result


def _relative(value: str) -> tuple[str, ...]:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or "\\" in value
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise ValueError("unsafe evidence path")
    return path.parts


@lru_cache(maxsize=8)
def _index(root_text: str, anchor_digest: str, manifest_digest: str):
    root = Path(root_text)
    bundle = root / "src/gnd/_assurance_evidence"
    anchor_raw = _read_member(bundle / "anchor.json")
    manifest_raw = _read_member(bundle / "manifest.json")
    if hashlib.sha256(anchor_raw).hexdigest() != anchor_digest:
        raise ValueError("release anchor changed during authentication")
    if hashlib.sha256(manifest_raw).hexdigest() != manifest_digest:
        raise ValueError("release manifest changed during authentication")
    anchor = json.loads(anchor_raw, object_pairs_hook=_pairs)
    manifest = json.loads(manifest_raw, object_pairs_hook=_pairs)
    if (
        set(anchor) != {"schema_version", "release_id", "manifest_sha256"}
        or anchor["schema_version"] != 1
        or anchor["manifest_sha256"] != manifest_digest
        or manifest.get("schema_version") != 1
        or not isinstance(manifest.get("files"), list)
    ):
        raise ValueError("installed evidence metadata is not authenticated")
    result = {
        "src/gnd/_assurance_evidence/anchor.json": {
            "bytes": len(anchor_raw),
            "sha256": anchor_digest,
        },
        "src/gnd/_assurance_evidence/manifest.json": {
            "bytes": len(manifest_raw),
            "sha256": manifest_digest,
        },
    }
    for row in manifest["files"]:
        address = row["address"]
        parts = _relative(address["path"])
        if parts[:2] == ("src", "gnd"):
            continue
        relative = "src/gnd/_assurance_evidence/" + address["path"]
        if relative in result:
            raise ValueError("duplicate installed evidence member")
        result[relative] = {
            "bytes": address["bytes"],
            "sha256": address["sha256"],
        }
    return result


def authenticated_copy(path: str, root: Path) -> bool:
    """Return true only for a listed current bundle member with matching bytes."""
    if not path.startswith("src/gnd/_assurance_evidence/"):
        return False
    try:
        root = root.resolve()
        bundle = root / "src/gnd/_assurance_evidence"
        anchor_raw = _read_member(bundle / "anchor.json")
        manifest_raw = _read_member(bundle / "manifest.json")
        index = _index(
            str(root),
            hashlib.sha256(anchor_raw).hexdigest(),
            hashlib.sha256(manifest_raw).hexdigest(),
        )
        expected = index.get(path)
        candidate = root / path
        if expected is None or candidate.is_symlink() or not candidate.is_file():
            return False
        raw = _read_member(candidate)
        return (
            len(raw) == expected["bytes"]
            and hashlib.sha256(raw).hexdigest() == expected["sha256"]
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return False


@dataclass(frozen=True, order=True)
class Site:
    path: str
    owner: str
    line: int
    end: int


_FORWARDERS = {
    "gnd.checker.ConstraintVerdict._registered_branch": "self.scope_id",
    "gnd.checker.DerivationVerdict._closed_shape": "self.scope_id",
    "gnd.transition.TransitionVerdict._iff_invariants": "self.scope_id",
}


def _owner(module: str, name: str) -> str:
    """Resolve defining modules to the unchanged semantic registry identities."""
    if HOMES.get(name.split(".")[0]) == module:
        module = "gnd.cli"
    if module.endswith('.__init__'):
        module = module.removesuffix('.__init__')
    module = {"gnd.payloads": "gnd.report", "gnd.extensions": "gnd.checker",
              "gnd.checker._reports": "gnd.checker", "gnd.checker._core": "gnd.checker",
              "gnd.model._validation": "gnd.model",
              "gnd.model._operations": "gnd.model"}.get(module, module)
    return module + "." + name


def _aggregate_revalidation(frame) -> bool:
    owner = _owner(frame.f_globals.get("__name__", ""), frame.f_code.co_qualname)
    if _FORWARDERS.get(owner) != "self.scope_id":
        return False
    caller = frame.f_back
    if caller is None or caller.f_globals.get("__name__") != "pydantic.main":
        return False
    if caller.f_code.co_qualname != "BaseModel.__init__":
        return False
    container = type(caller.f_locals.get("self"))
    return (container.__module__, container.__qualname__) in {
        ("gnd.checker", "CheckReport"),
        ("gnd.transition", "StepResult"),
        ("gnd.transition", "TransitionReport"),
    }


def _scope_arguments(node: ast.Call) -> list[ast.expr]:
    function = node.func
    # Findings carry the already-recorded branch identifier as data.  Treating
    # that constructor as a second producer creates a phantom, unexecuted site.
    if isinstance(function, ast.Name) and function.id == "CorrespondedFinding":
        return []
    values = [keyword.value for keyword in node.keywords if keyword.arg == "scope_id"]
    if (isinstance(function, ast.Name) and function.id == "record_branch") or (
        isinstance(function, ast.Attribute) and function.attr == "record_branch"
    ):
        values.extend(node.args[:1])
    # The transition wrapper owns the assurance projection selected at this
    # exact shared-helper call. Its runtime record_branch executes inside the
    # helper, while the registry intentionally names the selecting wrapper.
    if isinstance(function, ast.Name) and function.id == "build_check_payload":
        values.extend(
            keyword.value
            for keyword in node.keywords
            if keyword.arg == "_assurance_surface"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value == "transition"
        )
    for expression in node.args:
        for child in ast.walk(expression):
            if isinstance(child, ast.Dict):
                values.extend(
                    value
                    for key, value in zip(child.keys, child.values, strict=True)
                    if isinstance(key, ast.Constant) and key.value == "scope_id"
                )
    return values


def inventory(root: Path, *, replacements: dict[str, str] | None = None) -> tuple[Site, ...]:
    """Walk all production modules, including sites without a registered owner.

    Replacements are an in-memory mutation seam used by the counterchecks;
    they cannot add a file to the inventory or write production bytes.
    """
    result = []
    forwarded = set()
    for path in sorted((root / "src/gnd").rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        if authenticated_copy(relative, root):
            continue
        source = (replacements or {}).get(relative, path.read_text())
        module = ".".join(path.relative_to(root / "src").with_suffix("").parts)

        def visit(node, names, *, module=module, relative=relative):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names = (*names, node.name)
            if isinstance(node, ast.Call) and (arguments := _scope_arguments(node)):
                owner = _owner(module, ".".join(names))
                expected = _FORWARDERS.get(owner)
                if (
                    expected is not None
                    and len(arguments) == 1
                    and ast.unparse(arguments[0]) == expected
                ):
                    assert owner not in forwarded, f"duplicate scope forwarder: {owner}"
                    forwarded.add(owner)
                else:
                    result.append(Site(relative, owner, node.lineno, node.end_lineno))
            for child in ast.iter_child_nodes(node):
                visit(child, names)

        visit(ast.parse(source, filename=relative), ())
    assert forwarded == _FORWARDERS.keys(), "scope forwarder changed or disappeared"
    return tuple(result)


class ExecutionSites(set):
    """A trace recipient collecting producer locations without global profiling."""

    def __init__(self, root: Path, sites: tuple[Site, ...], registry):
        super().__init__()
        self.root = root
        self.registry = {row.scope_id: row for row in registry}
        self.sites = sites
        self.observed: dict[str, set[Site]] = {}
        self.forwarded = 0

    def add(self, scope_id):
        super().add(scope_id)
        frame = sys._getframe(1)  # record_branch calls the current trace recipient
        assert frame.f_code is semantic_registry.record_branch.__code__
        row = self.registry[scope_id]
        frame = frame.f_back
        if frame is not None and _aggregate_revalidation(frame):
            self.forwarded += 1
            return
        while frame is not None:
            if _owner(frame.f_globals.get("__name__", ""), frame.f_code.co_name) == row.production_owner:
                relative = (
                    Path(frame.f_code.co_filename).resolve().relative_to(self.root).as_posix()
                )
                matches = [
                    site
                    for site in self.sites
                    if site.path == relative
                    and site.owner == row.production_owner
                    and site.line <= frame.f_lineno <= site.end
                ]
                if matches:
                    site = min(matches, key=lambda item: item.end - item.line)
                    self.observed.setdefault(scope_id, set()).add(site)
                    return
                raise AssertionError(
                    f"no static producer call for {scope_id} at {relative}:{frame.f_lineno} "
                    f"(definition starts {frame.f_code.co_firstlineno})"
                )
            frame = frame.f_back
        raise AssertionError(f"no producer owner frame for {scope_id}")


@contextmanager
def capture_sites(root: Path, sites: tuple[Site, ...], registry):
    trace = ExecutionSites(root.resolve(), sites, registry)
    token = semantic_registry._TRACES.set((*semantic_registry._TRACES.get(), trace))
    try:
        yield trace
    finally:
        semantic_registry._TRACES.reset(token)


def audit(sites: tuple[Site, ...], observed: dict[str, set[Site]], registry) -> tuple[str, ...]:
    """No registry row, executed id or static producer site may be orphaned."""
    rows = {row.scope_id: row for row in registry}
    owners = {row.production_owner for row in registry}
    findings = []
    for scope_id, row in rows.items():
        locations = observed.get(scope_id, set())
        if len(locations) != 1:
            findings.append(f"row-site-count:{scope_id}:{len(locations)}")
        elif next(iter(locations)).owner != row.production_owner:
            findings.append(f"wrong-owner:{scope_id}")
    for scope_id in observed.keys() - rows.keys():
        findings.append(f"unregistered-execution:{scope_id}")
    reached = {site for locations in observed.values() for site in locations}
    for site in sites:
        if site.owner not in owners:
            findings.append(f"unregistered-owner:{site.owner}:{site.line}")
        if site not in reached:
            findings.append(f"unexecuted-site:{site.path}:{site.line}")
    for site in reached - set(sites):
        findings.append(f"nonstatic-site:{site.path}:{site.line}")
    return tuple(sorted(findings))
