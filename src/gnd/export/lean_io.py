"""Descriptor-bound Lean input snapshots and exact bundle reconstruction."""

import os
from pathlib import Path

from gnd import artifacts
from gnd.model import load_model_bytes
from gnd.references import bind_references

from . import lean
from .lean_types import DEFAULT_LIMITS, LeanLimits, checked_limits, refused
from .souffle_io import read_file


def export_lean(
    model_path,
    population_path,
    *,
    toolchain,
    reference_root=None,
    out=None,
    raw=False,
    limits=DEFAULT_LIMITS,
):
    try:
        checked_limits(limits)
        if out is not None and (not raw or os.path.lexists(out)):
            return refused()
        mr, pr = (
            read_file(model_path, limits.document_bytes),
            read_file(population_path, limits.document_bytes),
        )
        mf = "json" if Path(model_path).suffix == ".json" else "yaml"
        pf = "json" if Path(population_path).suffix == ".json" else "yaml"
        # Parse both candidate documents before fragment classification/binding.
        lean.parse(mr, mf, limits)
        lean.parse(pr, pf, limits)
        model = load_model_bytes(mr, source=model_path)
        ctx = (
            bind_references(model, root=reference_root or Path(model_path).parent)
            if model.reference_populations
            else None
        )
        refs = tuple((o.id, b) for o, _, b in ctx._snapshots) if ctx else ()
        result = lean.render_lean(
            mr,
            pr,
            toolchain=toolchain,
            model_format=mf,
            candidate_format=pf,
            reference_inputs=refs,
            limits=limits,
        )
        if result.exit_code or out is None:
            return result
        try:
            p = Path(out)
            artifacts.publish_directory_once(
                p.parent,
                p.name,
                result.files,
                manifest_name="manifest.json",
                max_files=2048,
                max_file_bytes=limits.document_bytes,
                max_total_bytes=limits.bundle_bytes,
                max_depth=2,
            )
        except (artifacts.ArtifactError, OSError, ValueError):
            return refused() if os.path.lexists(out) else refused(4, "write-failed")
        return result
    except (artifacts.ArtifactError, *lean.INPUT_ERRORS):
        return refused()


def verify_lean_bundle(bundle_path, *, limits=DEFAULT_LIMITS):
    try:
        checked_limits(limits)
        fd = artifacts._open_root(Path(bundle_path))
        try:
            inventory = artifacts._inventory_tree_fd(
                fd,
                max_files=2048,
                max_file_bytes=limits.document_bytes,
                max_total_bytes=limits.bundle_bytes,
                max_depth=2,
            )
            files = {
                entry.path: artifacts.read_regular_bounded_at(
                    fd, entry.path, max_bytes=limits.document_bytes
                )[0]
                for entry in inventory.files
            }
        finally:
            os.close(fd)
        manifest = lean.parse(files["manifest.json"], "json", DEFAULT_LIMITS)
        if (
            type(manifest["version"]) is not int
            or manifest["version"] != 1
            or set(manifest["limits"]) != set(vars(DEFAULT_LIMITS))
        ):
            raise ValueError("manifest version/limits")
        original = checked_limits(LeanLimits(**manifest["limits"]))
        refs = tuple(
            (r["id"], files[f"inputs/reference-{n}.json"])
            for n, r in enumerate(manifest["binding"]["references"])
        )
        kwargs = {
            "toolchain": manifest["toolchain"],
            "model_format": manifest["input_formats"]["model"],
            "candidate_format": manifest["input_formats"]["candidate"],
            "reference_inputs": refs,
        }
        result = lean.render_lean(
            files["inputs/model.json"], files["inputs/candidate.json"], limits=original, **kwargs
        )
        if result.exit_code or result.files != files:
            raise ValueError("bundle does not reproduce")
        # Caller ceilings still apply even to correctly signed original ceilings.
        current = lean.render_lean(
            files["inputs/model.json"], files["inputs/candidate.json"], limits=limits, **kwargs
        )
        if current.exit_code:
            return current
        result.status = "verified"
        return result
    except (artifacts.ArtifactError, *lean.INPUT_ERRORS, AttributeError):
        return refused()
