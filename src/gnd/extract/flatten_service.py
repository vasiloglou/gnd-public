"""``gnd flatten``: write an include root's flat model and its flattening record.

The two files are the ones ``gnd extract`` writes beside its bundle
(``<stem>.flat.orm.json`` and ``<stem>.flattening.json``, format
``gnd-flattening/1``), for any include root, temporal or not, and without the
bundle or its index. Their one normative home is the representation format's
"Extraction flattening record" section.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from gnd.exits import EXIT_COLLISION, EXIT_ILL_FORMED, EXIT_IO, EXIT_NO_INPUT, EXIT_OK


def flatten_to(model_path: str, out_dir: str, *, output_format: str = "text") -> int:
    """Flatten MODEL_PATH into OUT_DIR, both files or neither; return the exit code."""
    from gnd.artifacts import canonical_json_bytes, sha256_hex
    from gnd.errors import ModelLoadError, ModelValidationError, ReferenceInputError
    from gnd.extract.bundle import bundle_stem
    from gnd.extract.service import _flattening_names
    from gnd.model import load_model
    from gnd.model.flattening import FlatteningError, flatten_model
    from gnd.output import _print_issues
    from gnd.safefs import InstallPathError
    from gnd.synth.paths import safe_output_path

    # The model is loaded and flattened before any output check, so an invalid
    # model reports 3 even when an output file is also in the way.
    try:
        model = load_model(model_path)
    except FileNotFoundError as error:
        print(f"missing input: {error}", file=sys.stderr)
        return EXIT_NO_INPUT
    except ModelValidationError as error:
        _print_issues(error.issues)
        return EXIT_ILL_FORMED
    except (ModelLoadError, ReferenceInputError, OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return EXIT_ILL_FORMED
    if not model.includes:
        print("ERROR at $: flatten needs a model that declares includes [include:declaration]")
        return EXIT_ILL_FORMED
    try:
        flat = flatten_model(model)
    except FlatteningError as error:
        print(f"ERROR: {error}")
        return EXIT_ILL_FORMED

    names = _flattening_names(bundle_stem(model_path))
    out_root = Path(out_dir)
    try:
        flat_path = safe_output_path(out_root, names["flat_model"])
        record_path = safe_output_path(out_root, names["record"])
        pairs = ((flat_path, flat.model_bytes), (record_path, flat.record_bytes))
        taken = [path for path, _ in pairs if path.exists() or path.is_symlink()]
        if out_root.exists() and not out_root.is_dir():
            raise NotADirectoryError(f"output directory is not a directory: {out_root}")
    except (InstallPathError, OSError, ValueError) as error:
        # A refused, unrepresentable or non-directory output path: band 74.
        print(f"output refused: {error}", file=sys.stderr)
        return EXIT_IO
    if taken:
        print(f"output exists: {taken[0]}", file=sys.stderr)
        return EXIT_COLLISION
    try:
        _publish_pair(out_root, pairs)
    except _LinkCollision as error:
        print(f"output exists: {error}", file=sys.stderr)
        return EXIT_COLLISION
    except OSError as error:
        print(f"output failure: {error}", file=sys.stderr)
        return EXIT_IO

    model_dir = Path(model_path).absolute().parent
    if model.reference_populations and out_root.absolute().resolve() != model_dir.resolve():
        print(f"note: reference paths in {flat_path} stay relative to {model_dir}", file=sys.stderr)
    record_sha = sha256_hex(flat.record_bytes)
    if output_format == "json":
        summary = {
            "command": "flatten",
            "model": {"path": str(model_path), "sha256": model._authored_sha256},
            "flat_model": {"path": str(flat_path), "sha256": sha256_hex(flat.model_bytes)},
            "record": {"path": str(record_path), "sha256": record_sha},
        }
        print(canonical_json_bytes(summary).decode())
    else:
        print(f"Flattened {model_path} to {flat_path} and {record_path} "
              f"(record sha256 {record_sha})")
    return EXIT_OK


class _LinkCollision(Exception):
    """A destination appeared between the existence check and the link."""


def _publish_pair(out_root: Path, pairs) -> None:
    """Stage both files beside their destinations, then link them in without replacing.

    PAIRS is a sequence of (destination, bytes). A failure after the first
    link removes it, so the directory ends with both files or neither.
    """
    out_root.mkdir(parents=True, exist_ok=True)
    linked = []
    with tempfile.TemporaryDirectory(prefix=".gnd-flatten-", dir=out_root) as staging_name:
        staged = []
        for destination, data in pairs:
            path = Path(staging_name) / destination.name
            with path.open("wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((path, destination))
        try:
            for path, destination in staged:
                try:
                    os.link(path, destination)  # refuses an existing destination
                except FileExistsError:
                    raise _LinkCollision(str(destination)) from None
                linked.append(destination)
        except BaseException:
            for destination in linked:
                destination.unlink(missing_ok=True)
            raise
