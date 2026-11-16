from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gnd import artifacts as wire
from gnd import input_policy as _rf7_input
from gnd import resolve_version
from gnd import safefs as install_module
from gnd.documents import Model
from gnd.errors import ModelLoadError
from gnd.exits import EXIT_INTERNAL, EXIT_IO, EXIT_NO_INPUT
from gnd.model import ModelValidationError, load_model
from gnd.model._validation import MAX_MODEL_BYTES
from gnd.output import _print_issues


def _extract_stem(model_path: str) -> str:
    """The slugged filename stem the bundle's four files share.

    Thin alias over :func:`gnd.extract.bundle.bundle_stem`, kept because five
    call sites in this module read better with the local name. The RULE has one
    owner (plan 03-04): it used to live here and be re-implemented by hand in
    ``codegen/emit.py``, which is the third-copy outcome G-03′ names.
    """
    from gnd.extract.bundle import bundle_stem

    return bundle_stem(model_path)

def _extraction_header_template(model_path: str, model: Any) -> dict[str, Any]:
    """The extraction population header — see :func:`gnd.extract.bundle.header_template`.

    Alias, not a second implementation. ``codegen/emit.py`` used to import THIS
    private name from ``gnd.cli``, inverting the layering and pulling the whole
    package into the generation lane's offline-scan closure (measured: 21
    modules -> 45). It imports ``gnd.extract.bundle`` directly now.
    """
    from gnd.extract.bundle import header_template

    return header_template(model_path, model)

def _flattening_names(stem: str) -> dict[str, str]:
    return {"flat_model": f"{stem}.flat.orm.json", "record": f"{stem}.flattening.json"}


class ExtractionBundleError(ValueError):
    """An indexed extraction input could not be authenticated."""

    def __init__(self, message: str, code: int = 3) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class _VerifiedBundle:
    model: Model | None
    root_sha256: str
    artifact_digests: dict[str, str]


def _bounded_bytes(path: Path, *, cap: int) -> bytes:
    resolved = path.resolve(strict=True)
    return wire.read_regular_file_bytes(resolved.parent, resolved.name, label=str(path), max_bytes=cap)


def _verify_artifact_index(
    model_path: str,
    artifacts_dir: str,
    required_artifacts: tuple[str, ...],
) -> _VerifiedBundle:
    """Authenticate required bundle bytes and retain a resolved include snapshot."""
    root = Path(artifacts_dir)
    stem = _extract_stem(model_path)
    index_path = root / f"{stem}.artifacts.json"
    if not index_path.is_file():
        raise ExtractionBundleError(f"the extraction bundle index at {index_path} does not exist", EXIT_NO_INPUT)

    try:
        index = _rf7_input.loads(_bounded_bytes(index_path, cap=1024 * 1024))
        root_bytes = _bounded_bytes(Path(model_path), cap=MAX_MODEL_BYTES)
        model_actual = wire.sha256_hex(root_bytes)
        model_recorded = str(index["model"]["sha256"])
        if model_recorded != model_actual:
            raise ExtractionBundleError(
                f"the root model sha256 in the bundle is {model_recorded} but the bytes hash to {model_actual}"
            )

        model = None
        expected: dict[str, bytes] = {}
        if "flattening" in index:
            from gnd.model.flattening import flatten_model

            names = _flattening_names(stem)
            if index["flattening"] != names:
                raise ExtractionBundleError("invalid flattening artifact names")
            model = load_model(model_path)
            if model._authored_sha256 != model_actual:
                raise ExtractionBundleError("the root model does not match the resolved include snapshot")
            flat = flatten_model(model)
            expected = {names["flat_model"]: flat.model_bytes, names["record"]: flat.record_bytes}
        else:
            from gnd.model._includes import guard_bytes

            guard_bytes(root_bytes, source=model_path, route="extraction bundle without a flattening binding")

        digests = {}
        for rel in (*expected, *required_artifacts):
            artifact_path = root / rel
            if rel in expected:
                label = "flat model" if rel.endswith(".flat.orm.json") else "flattening record"
                try:
                    raw, _ = wire.read_regular_bounded(root, rel, max_bytes=MAX_MODEL_BYTES)
                    recorded = index["artifacts"][rel]["sha256"]
                except (OSError, wire.ArtifactError, ValueError, KeyError, TypeError) as error:
                    raise ExtractionBundleError(f"the {label} binding could not be read: {error}") from error
                if raw != expected[rel]:
                    raise ExtractionBundleError(f"the {label} does not match the resolved include snapshot")
            else:
                if not artifact_path.is_file():
                    raise ExtractionBundleError(
                        f"the indexed extraction artifact at {artifact_path} is missing", EXIT_NO_INPUT
                    )
                if model is None:
                    raw = artifact_path.read_bytes()
                else:
                    raw, _ = wire.read_regular_bounded(root, rel, max_bytes=MAX_MODEL_BYTES)
                recorded = str(index["artifacts"][rel]["sha256"])
            actual = wire.sha256_hex(raw)
            if actual != recorded:
                raise ExtractionBundleError(
                    f"the bundle index records {rel} sha256 {recorded} but the artifact bytes hash to {actual}"
                )
            digests[rel] = actual
    except ExtractionBundleError:
        raise
    except (OSError, wire.ArtifactError, ValueError, KeyError, TypeError, RuntimeError,
            ModelLoadError, ModelValidationError) as error:
        raise ExtractionBundleError(f"the extraction bundle index is not verifiable ({error})") from error
    return _VerifiedBundle(model, model_actual, digests)


def _artifact_index_issue(
    model_path: str,
    artifacts_dir: str,
    required_artifacts: tuple[str, ...],
) -> tuple[int, str] | None:
    """Validate the bundle index and every artifact this consumer will read."""
    try:
        _verify_artifact_index(model_path, artifacts_dir, required_artifacts)
    except ExtractionBundleError as error:
        return error.code, str(error)
    return None


def _cmd_extract(model_path: str, out_dir: str, *, guidelines: bool = False) -> int:
    """``gnd extract MODEL --out DIR`` — the per-model artifact bundle.

    With ``guidelines`` the bundle gains ``<stem>.guidelines.md`` (MG4),
    digest-recorded in the index like the other artifacts; without it the
    bundle is byte-identical to what it was before the option existed.

    Everything here is a pure offline function of ``model.orm.yaml`` (R-04'''):
    the projection, the constraint-blind verbalization, the applicable set, and
    the digest index with the PANEL-6 ``header_template``. The executing agent
    (the gnd-extract skill) is the only place a model is ever called.
    """
    import hashlib as _hashlib
    import os
    import tempfile

    from gnd.extract.projection import ProjectionGateError, project
    from gnd.extract.refscheme import applicable_set
    from gnd.extract.vocabulary import render_verbalization
    from gnd.synth import paths as _paths

    try:
        from gnd.model.flattening import flatten_model
        from gnd.terms import require_non_temporal

        model = load_model(model_path)
        require_non_temporal(model, "extract")
        flat = flatten_model(model) if model.includes else None
    except ModelValidationError as error:
        for warning in error.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        projection = project(model)
    except ProjectionGateError as error:
        # A gate violation here is OUR emitter building a leaking schema — an
        # internal invariant breach in gnd's own derivation, never the caller's
        # input (their model already loaded clean). So EXIT_INTERNAL (70): band
        # 3 would send the user to fix a valid model, and 5 (EXIT_GENERATOR)
        # belongs to the synthesis lane's invariants, not this one.
        print(f"INTERNAL ERROR: {error}")
        return EXIT_INTERNAL

    stem = _extract_stem(model_path)

    def canonical(payload: dict[str, Any]) -> str:
        # Sorted keys + no NaN, so two extracts over one model agree to the
        # byte (measure/report.py:104-110's discipline).
        return (
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False)
            + "\n"
        )

    artifacts: dict[str, str] = {
        f"{stem}.projection.schema.json": canonical(projection),
        f"{stem}.verbalization.txt": render_verbalization(model),
        f"{stem}.applicable.json": canonical(applicable_set(model)),
    }
    if guidelines:
        from gnd.extract.guidelines import GUIDELINES_SUFFIX, render_guidelines

        artifacts[f"{stem}{GUIDELINES_SUFFIX}"] = render_guidelines(model)

    out_root = Path(out_dir)
    index_rel = f"{stem}.artifacts.json"
    digests: dict[str, str] = {}
    try:
        model_sha256 = (model._authored_sha256 if flat is not None
                        else _hashlib.sha256(Path(model_path).read_bytes()).hexdigest())
        artifact_bytes = {rel: text.encode("utf-8") for rel, text in artifacts.items()}
        if flat is not None:
            names = _flattening_names(stem)
            artifact_bytes[names["flat_model"]] = flat.model_bytes
            artifact_bytes[names["record"]] = flat.record_bytes
        # Every write routes through the ONE traversal guard (cli.py's synth
        # precedent): output paths come from argv only, never from model or
        # response content (T-02.1-03).
        destinations: dict[str, Path] = {}
        for rel in [*artifact_bytes, index_rel]:
            destinations[rel] = _paths.safe_output_path(out_root, rel)
        if flat is not None:
            source = Path(model_path)
            dependencies = [
                source,
                *(source.parent / entry.path for entry in model._included),
                *(source.parent / entry["path"] for entry in model.reference_populations),
            ]
            for destination in destinations.values():
                if destination.exists() and any(destination.samefile(dep) for dep in dependencies):
                    raise install_module.InstallPathError(
                        f"output {destination} overlaps a bound model input"
                    )
        digests = {rel: _hashlib.sha256(data).hexdigest() for rel, data in artifact_bytes.items()}

        # PANEL-6 header ownership: `model`, `model_id`, `source` and `covers`
        # are set by deterministic code — the caller contract the gnd-extract
        # skill copies VERBATIM and `gnd verify` re-derives and enforces (plan
        # 03). The LLM never chooses header fields (vacuity gaming through
        # omitted coverage).
        header_template = _extraction_header_template(model_path, model)
        index_payload: dict[str, Any] = {
            "gnd_version": resolve_version(),
            "model": {
                "path": Path(model_path).as_posix(),
                "sha256": model_sha256,
            },
            "artifacts": {rel: {"sha256": digest} for rel, digest in digests.items()},
            "header_template": header_template,
        }
        if flat is not None:
            index_payload["flattening"] = names
        bundle_bytes = {
            **artifact_bytes,
            index_rel: canonical(index_payload).encode("utf-8"),
        }

        # Stage the complete bundle beside its destination. Only after every
        # file is durable do artifact replacements begin, with the index last.
        # Consumers require and validate that index, so an interruption during
        # replacement is rejected as a mixed bundle instead of being consumed.
        out_root.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=f".{out_root.name}.staging-", dir=out_root.parent
        ) as staging_name:
            staging = Path(staging_name)
            for rel, data in bundle_bytes.items():
                staged = staging / rel
                with staged.open("wb") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
            staging_fd = os.open(staging, os.O_RDONLY)
            try:
                os.fsync(staging_fd)
            finally:
                os.close(staging_fd)

            out_root.mkdir(parents=True, exist_ok=True)
            for rel in artifact_bytes:
                os.replace(staging / rel, destinations[rel])
            os.replace(staging / index_rel, destinations[index_rel])
            output_fd = os.open(out_root, os.O_RDONLY)
            try:
                os.fsync(output_fd)
            finally:
                os.close(output_fd)
    except install_module.InstallPathError as error:
        print(f"ERROR: refused output path: {error}")
        return EXIT_IO
    except OSError as error:
        print(f"ERROR: could not write the bundle under {out_dir}: {error}")
        return EXIT_IO

    print(f"extracted bundle for {model_path} -> {out_root}")
    for rel in [*digests, index_rel]:
        print(f"  {rel}")
    return 0

_extract_stem.__module__ = "gnd.cli"
_extraction_header_template.__module__ = "gnd.cli"
_artifact_index_issue.__module__ = "gnd.cli"
_cmd_extract.__module__ = "gnd.cli"
