from __future__ import annotations

import sys
from pathlib import Path

from gnd.exits import EXIT_COLLISION, EXIT_INTERNAL, EXIT_NO_INPUT


def _cmd_export_pyrel(
    model_path: str, out_path: str, *, duckdb_path: str = ":memory:", connection: str | None = None
) -> int:
    from gnd.export.emit import render_pyrel
    from gnd.export.pyrel_runtime import ExportInputError, write_new

    try:
        source = render_pyrel(Path(model_path), duckdb_path=duckdb_path, connection=connection)
    except FileNotFoundError as error:
        print(f"missing input: {error}", file=sys.stderr)
        return EXIT_NO_INPUT
    except ExportInputError as error:
        print(f"invalid model: {error}", file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"export failed: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    try:
        write_new(Path(out_path), source)
    except FileExistsError as error:
        print(f"output exists: {error}", file=sys.stderr)
        return EXIT_COLLISION
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"output failure: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    print(f"Exported PyRel program to {out_path}")
    return 0

_cmd_export_pyrel.__module__ = "gnd.cli"
