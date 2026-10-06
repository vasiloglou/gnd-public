from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gnd import input_policy as _rf7_input


class IndexValidationError(ValueError):
    """The synthesis corpus manifest is not a supported closed document."""

_INDEX_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["populations", "not_derivable"],
    "properties": {
        "populations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "population",
                    "sidecar",
                    "seed",
                    "band",
                    "class",
                    "case_kind",
                ],
                "properties": {
                    "population": {"type": "string", "minLength": 1},
                    "sidecar": {"type": "string", "minLength": 1},
                    "seed": {"type": "integer"},
                    "band": {"type": "integer", "minimum": 0, "maximum": 4},
                    "class": {
                        "enum": [
                            "conforming",
                            "boundary",
                            "violating",
                            "no-subjects",
                            "unchecked",
                        ]
                    },
                    "case_kind": {
                        "enum": [
                            "conforming",
                            "boundary",
                            "violating",
                            "no-subjects",
                            "unchecked",
                        ]
                    },
                    "operator": {"type": "string", "minLength": 1},
                    "boundary_side": {"type": "string", "minLength": 1},
                    "epsilon": {"type": ["number", "string", "null"]},
                    "target": {"type": "string", "minLength": 1},
                    "predicted_verdict": {
                        "enum": ["pass", "warning", "fail", "vacuous", "unchecked"]
                    },
                    "violates_target": {"type": "string", "minLength": 1},
                    "violates": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "uniqueItems": True,
                    },
                    "isolating": {"type": "boolean"},
                    "isolation_verified": {"type": "boolean"},
                    "baseline_seed": {"type": "integer"},
                },
            },
        },
        "not_derivable": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["constraint_ref", "family", "operator", "mechanism"],
                "properties": {
                    "constraint_ref": {"type": "string"},
                    "family": {"type": "string"},
                    "operator": {"type": ["string", "null"]},
                    "mechanism": {"type": "string"},
                    "case_kind": {"type": "string"},
                    "side": {"type": "string"},
                },
            },
        },
    },
}

_INDEX_VALIDATOR = Draft202012Validator(_INDEX_SCHEMA)

def _validate_index_document(document: Any) -> dict[str, Any]:
    """Validate and return one synthesis ``index.json`` document.

    The index is untrusted corpus input.  Keeping this schema closed prevents a
    malformed record from becoming an ``AttributeError``/``KeyError`` whose
    process exit 1 is indistinguishable from an alethic checker failure.
    """
    errors = sorted(_INDEX_VALIDATOR.iter_errors(document), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        raise IndexValidationError(f"index.json at {location}: {error.message}")
    return document

class _SynthCorpusTransaction:
    """Build a corpus off-tree and publish it only as one directory swap."""

    def __init__(self, final_root: Path) -> None:
        import shutil
        import tempfile

        self.final_root = final_root
        self.final_root.parent.mkdir(parents=True, exist_ok=True)
        self.stage_root = Path(
            tempfile.mkdtemp(prefix=f".{final_root.name}.synth-", dir=final_root.parent)
        )
        self._active = True
        try:
            if final_root.exists():
                if not final_root.is_dir():
                    raise OSError(f"corpus root {final_root} is not a directory")
                shutil.copytree(final_root, self.stage_root, dirs_exist_ok=True)
        except Exception:
            shutil.rmtree(self.stage_root, ignore_errors=True)
            self._active = False
            raise

    def abort(self, *, publish_quarantine: bool = False) -> None:
        import shutil

        if not self._active:
            return
        try:
            if publish_quarantine:
                staged_quarantine = self.stage_root / "quarantine"
                if staged_quarantine.exists():
                    final_quarantine = self.final_root / "quarantine"
                    final_quarantine.mkdir(parents=True, exist_ok=True)
                    for source in staged_quarantine.rglob("*"):
                        if not source.is_file():
                            continue
                        relative = source.relative_to(staged_quarantine)
                        destination = final_quarantine / relative
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        if (
                            not destination.exists()
                            or destination.read_bytes() != source.read_bytes()
                        ):
                            shutil.copy2(source, destination)
        finally:
            shutil.rmtree(self.stage_root, ignore_errors=True)
            self._active = False

    def commit(self) -> None:
        import os
        import shutil

        if not self._active:
            raise OSError("synthesis transaction is no longer active")
        backup = self.stage_root.with_name(self.stage_root.name + ".backup")
        moved_existing = False
        try:
            if self.final_root.exists():
                os.replace(self.final_root, backup)
                moved_existing = True
            os.replace(self.stage_root, self.final_root)
            self._active = False
        except Exception:
            if moved_existing and backup.exists() and not self.final_root.exists():
                os.replace(backup, self.final_root)
            raise
        finally:
            if not self._active and backup.exists():
                shutil.rmtree(backup, ignore_errors=True)

def _validate_existing_synth_index(out_root: Path) -> None:
    """Fail closed on the old manifest before the transaction writes anything."""
    index_path = out_root / "index.json"
    if not index_path.exists():
        return
    try:
        document = _validate_index_document(_rf7_input.loads(index_path.read_text(encoding="utf-8")))
        _resolve_unique_index_entries(out_root, document)
    except json.JSONDecodeError as error:
        raise IndexValidationError(f"index.json is not valid JSON: {error}") from error
    except CorpusPathError as error:
        raise IndexValidationError(str(error)) from error

class CorpusPathError(Exception):
    """An ``index.json`` entry does not resolve to a file inside the corpus root.

    ``--populations DIR`` is a promise that DIR is what gets measured, so a
    stored path that is absolute, escapes the root, or names a file that is not
    there is a REFUSAL rather than a fallback. The resolver this replaces tried
    ``Path(stored)`` first — against the process working directory — and took the
    first candidate that existed: since every committed index stored repo-root-
    relative paths, a run from the repo root read the repo-root copies whatever
    ``--populations`` said. An emptied corpus directory reproduced the committed
    payload byte-for-byte, digest and all, and a corrupted population inside the
    named directory was never opened. Mapped to exit 3 (ill-formed input), the
    same band as the other C6 binding failures.
    """

def _resolve_corpus_path(populations_dir: Path, stored: str) -> Path:
    """Resolve an ``index.json`` / sidecar path STRICTLY under the corpus root.

    Three rules, in order, and none of them may be relaxed into a fallback:

    1. ``index.json`` is UNTRUSTED input — an absolute path or one containing
       ``..`` is refused outright, before it can reach the filesystem;
    2. the path is joined under ``populations_dir`` through
       :func:`gnd.synth.paths.safe_output_path`, the same containment guard the
       write side uses, so a symlinked escape is refused too;
    3. the resolved file must EXIST. A population named in the index and absent
       under the root means the corpus is incomplete, and an incomplete corpus
       publishes a rate over a denominator its reader cannot see. Skipping the
       entry and falling back to a copy elsewhere on disk are the same defect
       wearing different clothes.
    """
    from gnd.synth import paths as _paths

    rel = Path(stored)
    if rel.is_absolute() or ".." in rel.parts:
        raise CorpusPathError(
            f"index.json entry {stored!r} is absolute or escapes its directory — "
            f"refused. A measurement reads the corpus it was pointed at "
            f"({populations_dir}), and index.json is untrusted input (C6)."
        )
    try:
        resolved = _paths.safe_output_path(populations_dir, rel.as_posix())
    except Exception as error:
        # The traversal guard's own refusal type is an implementation detail of
        # gnd.install; re-raised as the corpus-level error the CLI maps to 3.
        raise CorpusPathError(
            f"index.json entry {stored!r} resolves outside {populations_dir}: {error}"
        ) from error
    if not resolved.exists():
        raise CorpusPathError(
            f"index.json entry {stored!r} does not resolve to an existing file "
            f"under {populations_dir} — the corpus is incomplete, and a "
            f"measurement must read the corpus it was pointed at (C6). Falling "
            f"back to a copy elsewhere on disk is how an EMPTY directory once "
            f"reproduced the committed payload byte-for-byte."
        )
    return resolved

def _resolve_unique_index_entries(
    populations_dir: Path, index: dict[str, Any]
) -> list[tuple[dict[str, Any], Path, Path]]:
    """Resolve index paths once and reject aliases before any case is loaded.

    Reporting preserves the manifest's order, but denominators must describe
    physical artifacts rather than records.  Two spellings or symlinks that
    resolve to the same population/sidecar are therefore duplicates, and the
    error names both record positions so the corpus can be repaired directly.
    """
    resolved_entries: list[tuple[dict[str, Any], Path, Path]] = []
    seen: dict[str, dict[Path, int]] = {"population": {}, "sidecar": {}}
    for position, entry in enumerate(index["populations"]):
        resolved: dict[str, Path] = {}
        for field in ("population", "sidecar"):
            path = _resolve_corpus_path(populations_dir, entry[field])
            if path in seen[field]:
                first = seen[field][path]
                raise CorpusPathError(
                    f"index.json populations[{position}].{field} duplicates "
                    f"populations[{first}].{field} after normalization: "
                    f"{entry[field]!r} resolves to {path}"
                )
            seen[field][path] = position
            resolved[field] = path
        expected_sidecar = resolved["population"].with_suffix(".meta.json")
        if resolved["sidecar"] != expected_sidecar:
            raise CorpusPathError(
                f"index.json populations[{position}].sidecar resolves to "
                f"{resolved['sidecar']}, but population {resolved['population']} "
                f"is bound to {expected_sidecar}"
            )
        resolved_entries.append((entry, resolved["population"], resolved["sidecar"]))
    return resolved_entries

def _corpus_relative(out_root: Path, path: str) -> str:
    """``path`` expressed relative to the corpus root, in POSIX form (CR-01).

    Every path written by ``gnd synth`` came from
    :func:`gnd.synth.paths.safe_output_path` and is therefore inside
    ``out_root``; the ``ValueError`` branch exists so a future caller that breaks
    that invariant is visible in the index rather than silently absolutised.
    """
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(out_root.resolve()).as_posix()
    except ValueError:
        return candidate.as_posix()

def _merge_index(
    out_root: Path,
    written: list[dict[str, Any]],
    not_derivable: list[dict[str, Any]] | None = None,
) -> None:
    """MERGE new entries into ``index.json`` (Gemini), union by population path,
    emitted in stable sorted order so the file is byte-reproducible (which also
    makes plan 04's D-22 'first contributing population in corpus order'
    deterministic — Claude-LOW). ``not_derivable`` records merge by
    (constraint_ref, operator) — a stand-down is an ANSWER and must survive
    re-invocation, never a silent skip.

    Paths are stored RELATIVE TO ``out_root`` (CR-01), the same rule the sidecar
    already applies to ``population`` and ``pool_path``. Storing them as written
    (cwd-relative, or absolute when ``--out`` was) is what let ``gnd measure
    --populations DIR`` resolve them against the process working directory and
    read a corpus the operator never named — and it bakes a machine path into a
    committed artifact besides.
    """
    import os
    import tempfile

    index_path = out_root / "index.json"
    existing: dict[str, dict[str, Any]] = {}
    existing_downs: dict[tuple[str, str], dict[str, Any]] = {}
    if index_path.exists():
        try:
            document = _validate_index_document(_rf7_input.loads(index_path.read_text(encoding="utf-8")))
            _resolve_unique_index_entries(out_root, document)
            for entry in document["populations"]:
                existing[entry["population"]] = entry
            for record in document["not_derivable"]:
                existing_downs[(record["constraint_ref"], str(record.get("operator")))] = record
        except json.JSONDecodeError as error:
            raise IndexValidationError(f"index.json is not valid JSON: {error}") from error
        except CorpusPathError as error:
            raise IndexValidationError(str(error)) from error
    for entry in written:
        relative = dict(entry)
        for key in ("population", "sidecar"):
            if relative.get(key):
                relative[key] = _corpus_relative(out_root, relative[key])
        existing[relative["population"]] = relative
    for record in not_derivable or []:
        existing_downs[(record["constraint_ref"], str(record.get("operator")))] = record
    merged = sorted(existing.values(), key=lambda e: e["population"])
    merged_downs = sorted(
        existing_downs.values(), key=lambda r: (r["constraint_ref"], str(r.get("operator")))
    )
    document = {"populations": merged, "not_derivable": merged_downs}
    _validate_index_document(document)
    rendered = json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n"

    out_root.mkdir(parents=True, exist_ok=True)
    staged_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            dir=out_root,
            prefix=".index.",
            suffix=".tmp",
            delete=False,
            encoding="utf-8",
        ) as handle:
            staged_path = Path(handle.name)
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staged_path, index_path)
        staged_path = None
        directory_fd = os.open(out_root, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if staged_path is not None:
            staged_path.unlink(missing_ok=True)

IndexValidationError.__module__ = "gnd.cli"
_validate_index_document.__module__ = "gnd.cli"
_SynthCorpusTransaction.__module__ = "gnd.cli"
_validate_existing_synth_index.__module__ = "gnd.cli"
CorpusPathError.__module__ = "gnd.cli"
_resolve_corpus_path.__module__ = "gnd.cli"
_resolve_unique_index_entries.__module__ = "gnd.cli"
_corpus_relative.__module__ = "gnd.cli"
_merge_index.__module__ = "gnd.cli"
