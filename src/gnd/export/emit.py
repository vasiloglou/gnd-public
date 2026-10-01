"""Offline publication of a self-contained optional PyRel program."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from .pyrel_runtime import _parse_document, _read_text, admit_model

SCRIPT_HEADER = (
    '# /// script\n'
    '# requires-python = ">=3.11,<3.14"\n'
    '# dependencies = ["relationalai==1.30.1", "ruamel.yaml==0.19.1"]\n'
    '# ///\n'
)


def render_pyrel(
    model_path: Path, *, duckdb_path: str = ":memory:", connection: str | None = None
) -> str:
    """Render from one bounded input read; no checker or foreign-runtime import."""
    text = _read_text(model_path)
    document = _parse_document(text)
    from gnd.terms import uses_temporal

    if uses_temporal(document):
        from .pyrel_runtime import ExportInputError

        raise ExportInputError("PyRel export does not support temporal models in Phase 1")
    admit_model(document)
    runtime = files("gnd.export").joinpath("pyrel_runtime.py").read_text(encoding="utf-8")
    config = {"duckdb_path": duckdb_path, "connection": connection}
    source = (SCRIPT_HEADER + runtime + f"\nMODEL_TEXT = {text!r}\n"
              f"MODEL_NAME = {str(model_path)!r}\nEXPORT_CONFIG = {config!r}\n"
              '\nif __name__ == "__main__":\n    sys.exit(program_main())\n')
    compile(source, "<pyrel-export>", "exec")
    return source
