from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import resolve_version
from gnd import safefs as install_module
from gnd.exits import EXIT_INTERNAL, EXIT_IO, EXIT_NO_INPUT
from gnd.model import ModelValidationError, load_model
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

def _artifact_index_issue(
    model_path: str,
    artifacts_dir: str,
    required_artifacts: tuple[str, ...],
) -> tuple[int, str] | None:
    """Validate the bundle index and every artifact this consumer will read."""
    import hashlib as _hashlib

    root = Path(artifacts_dir)
    index_path = root / f"{_extract_stem(model_path)}.artifacts.json"
    if not index_path.is_file():
        return (
            EXIT_NO_INPUT,
            f"the extraction bundle index at {index_path} does not exist",
        )
    try:
        if index_path.stat().st_size > 1024 * 1024:
            return (3, f"the extraction bundle index at {index_path} exceeds 1 MiB")
        index = _rf7_input.loads(index_path.read_text(encoding="utf-8"))
        model_actual = _hashlib.sha256(Path(model_path).read_bytes()).hexdigest()
        model_recorded = str(index["model"]["sha256"])
        if model_recorded != model_actual:
            return (
                3,
                (
                    f"the bundle index records model sha256 {model_recorded} but "
                    f"the model bytes hash to {model_actual}"
                ),
            )
        for rel in required_artifacts:
            artifact_path = root / rel
            if not artifact_path.is_file():
                return (
                    EXIT_NO_INPUT,
                    f"the indexed extraction artifact at {artifact_path} is missing",
                )
            recorded = str(index["artifacts"][rel]["sha256"])
            actual = _hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            if recorded != actual:
                return (
                    3,
                    (
                        f"the bundle index records {rel} sha256 {recorded} but "
                        f"the artifact bytes hash to {actual}"
                    ),
                )
    except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as error:
        return (3, f"the extraction bundle index is not verifiable ({error})")
    return None

def _cmd_extract(model_path: str, out_dir: str) -> int:
    """``gnd extract MODEL --out DIR`` — the per-model artifact bundle.

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
        model = load_model(model_path)
        from gnd.terms import require_non_temporal

        require_non_temporal(model, "extract")
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

    out_root = Path(out_dir)
    index_rel = f"{stem}.artifacts.json"
    digests: dict[str, str] = {}
    try:
        model_bytes = Path(model_path).read_bytes()
        # Every write routes through the ONE traversal guard (cli.py's synth
        # precedent): output paths come from argv only, never from model or
        # response content (T-02.1-03).
        destinations: dict[str, Path] = {}
        for rel in [*artifacts, index_rel]:
            destinations[rel] = _paths.safe_output_path(out_root, rel)
        artifact_bytes = {rel: text.encode("utf-8") for rel, text in artifacts.items()}
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
                "sha256": _hashlib.sha256(model_bytes).hexdigest(),
            },
            "artifacts": {rel: {"sha256": digest} for rel, digest in digests.items()},
            "header_template": header_template,
        }
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
            for rel in artifacts:
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
