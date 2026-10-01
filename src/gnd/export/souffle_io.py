"""Descriptor-bound bundle intake and exclusive manifest-last publication."""

import os
from pathlib import Path

from gnd import artifacts

from . import souffle
from .souffle_types import DEFAULT_LIMITS, SouffleLimits, checked_limits, refused


def read_file(path, cap):
    p = Path(path)
    return artifacts.read_regular_bounded(p.parent, p.name, max_bytes=cap)[0]


def verify_souffle_bundle(bundle_path, *, limits=DEFAULT_LIMITS):
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
        manifest = souffle.parse(files["manifest.json"], "json", limits)
        # Full deterministic reconstruction pins every closed record, key, type,
        # payload, name and hash; equality alone would admit bool == integer.
        raw_limits = manifest["limits"]
        if set(raw_limits) != set(vars(DEFAULT_LIMITS)):
            raise ValueError("limit roster")
        original_limits = checked_limits(SouffleLimits(**raw_limits))
        if type(manifest["version"]) is not int or manifest["version"] != 1:
            raise ValueError("version")
        for entry in manifest["files"]:
            if type(entry["bytes"]) is not int or entry["bytes"] < 0:
                raise ValueError("size")
        refs = tuple(
            (r["id"], files[f"inputs/reference-{n}.json"])
            for n, r in enumerate(manifest["binding"]["references"])
        )
        result = souffle.render_souffle(
            files["inputs/model.json"],
            files["inputs/candidate.json"],
            model_format=manifest["input_formats"]["model"],
            candidate_format=manifest["input_formats"]["candidate"],
            reference_inputs=refs,
            limits=original_limits,
        )
        if result.exit_code or result.files != files:
            raise ValueError("bundle does not reproduce")
        souffle.admit(
            files["inputs/model.json"],
            files["inputs/candidate.json"],
            manifest["input_formats"]["model"],
            manifest["input_formats"]["candidate"],
            refs,
            limits,
        )
        if result.counts["emission_visits"] > limits.emission_visits:
            return refused(4, "work-limit")
        result.status = "verified"
        return result
    except (artifacts.ArtifactError, *souffle.INPUT_ERRORS, AttributeError):
        return refused()


def write_souffle_bundle(payload, out, *, raw):
    if not raw:
        return refused()
    if payload.exit_code:
        return payload
    try:
        p = Path(out)
        artifacts.publish_directory_once(
            p.parent,
            p.name,
            payload.files,
            manifest_name="manifest.json",
            max_files=2048,
            max_file_bytes=DEFAULT_LIMITS.document_bytes,
            max_total_bytes=DEFAULT_LIMITS.bundle_bytes,
            max_depth=2,
        )
        return payload
    except (artifacts.ArtifactError, OSError, ValueError):
        if os.path.lexists(out):
            return refused()
        return refused(4, "write-failed")


def export_souffle(model_path, population_path, *, reference_root=None, out=None, raw=False):
    try:
        if out is not None and (not raw or os.path.lexists(out)):
            return refused()
        mr, pr = (
            read_file(model_path, DEFAULT_LIMITS.document_bytes),
            read_file(population_path, DEFAULT_LIMITS.document_bytes),
        )
        mf = "json" if Path(model_path).suffix == ".json" else "yaml"
        pf = "json" if Path(population_path).suffix == ".json" else "yaml"
        from gnd.model import load_model_bytes
        from gnd.references import bind_references

        model = load_model_bytes(mr, source=model_path)
        context = (
            bind_references(model, root=reference_root or Path(model_path).parent)
            if model.reference_populations
            else None
        )
        refs = tuple((o.id, b) for o, _, b in context._snapshots) if context else ()
        result = souffle.render_souffle(
            mr, pr, model_format=mf, candidate_format=pf, reference_inputs=refs
        )
        return write_souffle_bundle(result, out, raw=raw) if out is not None else result
    except (artifacts.ArtifactError, *souffle.INPUT_ERRORS):
        return refused()
