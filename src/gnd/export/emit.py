"""Offline publication of a self-contained optional PyRel program."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from .include_roots import flatten_for_export, flattening_constants
from .pyrel_runtime import _constraint_entries, _parse_document, _read_text, admit_model

SCRIPT_HEADER = (
    '# /// script\n'
    '# requires-python = ">=3.11,<3.14"\n'
    '# dependencies = ["relationalai==1.30.1", "ruamel.yaml==0.19.1"]\n'
    '# ///\n'
)


def render_pyrel(
    model_path: Path, *, duckdb_path: str = ":memory:", connection: str | None = None
) -> str:
    """Render from one bounded input read; no checker or foreign-runtime import.

    That holds for a model without includes. An include root is first
    composed and flattened (``flatten_for_export``) and its flat model is
    rendered, with two constants recording the flattening.
    """
    text = _read_text(model_path)
    flat = flatten_for_export(model_path, text.encode("utf-8"))
    if flat is not None:
        text = flat.model_bytes.decode("utf-8")
    document = _parse_document(text)
    from gnd.errors import ModelValidationError
    from gnd.model._includes import guard_document

    from .pyrel_runtime import ExportInputError, ProfileRefusal
    try:
        guard_document(document, "export.pyrel")
    except ModelValidationError as error:
        raise ExportInputError(str(error)) from error
    from gnd.model import iter_derivation_clauses
    from gnd.terms import guarded_clause_refusal, uses_temporal, where_uses_membership

    if uses_temporal(document):
        raise ExportInputError("PyRel export does not support temporal models in Phase 1")
    admitted = admit_model(document)
    try:
        for _, constraint, _ in _constraint_entries(admitted):
            reason = guarded_clause_refusal(constraint)
            if reason is not None:
                raise ProfileRefusal(reason)
        if any(
            where_uses_membership(clause.get("where"))
            for fact in admitted.fact_types.values()
            for clause in iter_derivation_clauses(fact.get("derivation_rule"))
        ):
            raise ProfileRefusal("membership-unsupported")
    except ProfileRefusal as error:
        raise ExportInputError(str(error)) from error
    runtime = files("gnd.export").joinpath("pyrel_runtime.py").read_text(encoding="utf-8")
    config = {"duckdb_path": duckdb_path, "connection": connection}
    source = (SCRIPT_HEADER + runtime + f"\nMODEL_TEXT = {text!r}\n"
              f"MODEL_NAME = {str(model_path)!r}\n" + flattening_constants(flat)
              + f"EXPORT_CONFIG = {config!r}\n"
              '\nif __name__ == "__main__":\n    sys.exit(program_main())\n')
    compile(source, "<pyrel-export>", "exec")
    return source


def render_pyrel_rules(model_path, target):
    """The model's rules as a readable PyRel program of requirements (see ``pyrel_rules``)."""
    from .pyrel_rules import render

    return render(model_path, target)
