"""Explicit optional export lane service wrappers."""
from __future__ import annotations


def export_souffle(model_path, population_path, *, reference_root=None, out=None, raw=False):
    """Render/publish the explicit standalone Souffle derivation fragment."""
    from gnd.export.souffle_io import export_souffle as export

    return export(
        model_path, population_path, reference_root=reference_root, out=out, raw=raw
    ).model_dump()


def verify_souffle(bundle_path):
    """Verify retained bytes and reproduce their deterministic emission."""
    from gnd.export.souffle_io import verify_souffle_bundle

    return verify_souffle_bundle(bundle_path).model_dump()


def run_souffle(bundle_path, *, executable="souffle", raw=False):
    """Run only an explicitly selected, checked foreign derivation program."""
    from gnd.export.souffle_runtime import run_souffle as run

    result = run(bundle_path, executable=executable)
    if not raw:
        result["extensions"] = None
        if result["tool"]:
            result["tool"].update(path=None, sha256=None)
    return result


def souffle_witness(bundle_path, targets_path, *, executable="souffle", raw=False, out=None):
    """Map native positive provenance and independently replay before publication."""
    from gnd import artifacts
    from gnd.export.souffle import INPUT_ERRORS, wire
    from gnd.export.souffle_io import read_file
    from gnd.export.souffle_runtime import native_witness
    from gnd.witness.io import parse_wire
    from gnd.witness.types import WitnessResult

    try:
        if out is not None and not raw:
            return WitnessResult(3, reason="input-invalid").model_dump()
        targets = parse_wire(read_file(targets_path, 10485760))
        result = native_witness(bundle_path, targets, executable=executable)
        if result.exit_code == 0 and out is not None:
            from pathlib import Path

            p = Path(out)
            artifacts.publish_leaf_atomic(p.parent, p.name, wire(result.certificate))
        report = result.model_dump()
        if not raw:
            report["certificate"] = None
            report["results"] = [
                {k: v for k, v in r.items() if k != "target"} for r in report["results"]
            ]
        return report
    except (artifacts.ArtifactError, *INPUT_ERRORS):
        return WitnessResult(3, reason="input-invalid").model_dump()


def export_lean(
    model_path, population_path, *, toolchain, reference_root=None, out=None, raw=False
):
    """Export finite definitions; no theorem or snapshot-equivalence claim."""
    from gnd.export.lean_io import export_lean as export

    return export(
        model_path,
        population_path,
        toolchain=toolchain,
        reference_root=reference_root,
        out=out,
        raw=raw,
    ).model_dump()


def verify_lean(bundle_path):
    """Verify exact deterministic reconstruction of a raw Lean bundle."""
    from gnd.export.lean_io import verify_lean_bundle

    return verify_lean_bundle(bundle_path).model_dump()


def compile_lean(bundle_path, *, executable="lake", elaborate_stubs=False):
    """Explicit compiler work; all theorem obligations remain unproved."""
    from gnd.export.lean_runtime import compile_lean as compile_bundle

    return compile_bundle(
        bundle_path, executable=executable, elaborate_stubs=elaborate_stubs
    ).model_dump()



# Historical qualifications are serialized by existing callers.
export_souffle.__module__ = 'gnd.api'
verify_souffle.__module__ = 'gnd.api'
run_souffle.__module__ = 'gnd.api'
souffle_witness.__module__ = 'gnd.api'
export_lean.__module__ = 'gnd.api'
verify_lean.__module__ = 'gnd.api'
compile_lean.__module__ = 'gnd.api'
