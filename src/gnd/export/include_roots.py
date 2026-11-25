"""Export an include root through its flat model (include-root-routes IR3).

Both PyRel renderers, the default checker program (``emit.render_pyrel``) and
the rules programs (``pyrel_rules.render``), call ``flatten_for_export``. It
cannot live in ``pyrel_runtime.py``, which is embedded verbatim in every
default program, nor in ``emit.py``, which ``pyrel_rules`` would then import
in a cycle.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gnd.documents import Model


@dataclass(frozen=True)
class FlatExport:
    """An include root's flat model, as ``gnd flatten`` would write it."""

    model_bytes: bytes
    record_sha256: str
    includes: tuple
    model: Model


def flatten_for_export(model_path: Path, raw: bytes):
    """The flat model to export for an include root, or None for any other model.

    A model that declares no includes keeps its one-read path: nothing is
    loaded here. An include root is composed by the loader ``gnd check`` uses
    and flattened; every refusal becomes ``ExportInputError`` (exit 3).
    """
    from gnd.errors import ModelLoadError, ModelValidationError, ReferenceInputError
    from gnd.model._includes import bytes_declare_includes

    from .pyrel_runtime import ExportInputError

    if not bytes_declare_includes(raw, source=str(model_path)):
        return None
    import gnd.model
    from gnd.model.flattening import FlatteningError, flatten_model

    try:
        model = gnd.model.load_model(Path(model_path))
        if model._authored_sha256 != hashlib.sha256(raw).hexdigest():
            raise ExportInputError("include:hash-mismatch: the root changed while it was read")
        flat = flatten_model(model)
    except ExportInputError:
        raise
    except ModelValidationError as error:
        raise ExportInputError(model_validation_message(error)) from error
    # ValueError covers UnicodeError from an include path that cannot be encoded;
    # gnd check and gnd flatten refuse the same root with exit 3.
    except (ModelLoadError, ReferenceInputError, FlatteningError, OSError, ValueError) as error:
        raise ExportInputError(str(error)) from error
    return FlatExport(
        model_bytes=flat.model_bytes,
        record_sha256=hashlib.sha256(flat.record_bytes).hexdigest(),
        includes=tuple((entry.id, entry.path, entry.sha256) for entry in model._included),
        model=flat.model,
    )


def model_validation_message(error) -> str:
    ids = dict.fromkeys(i.rule_id for i in error.issues)
    code = next((i.rule_id for i in error.issues if i.rule_id.startswith("include:")), None)
    if code is not None and "flattening:re-entry" not in ids:
        return code
    return f"{error} [{', '.join(ids)}]"


def flattening_constants(flat) -> str:
    """The two program lines that record an exported flattening; empty for None."""
    if flat is None:
        return ""
    return (f"FLATTENING_RECORD_SHA256 = {flat.record_sha256!r}\n"
            f"MODEL_INCLUDES = {flat.includes!r}\n")
