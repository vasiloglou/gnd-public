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


def _cmd_export_pyrel_rules(model_path: str, out_path: str, *, target: str) -> int:
    """Write the model's rules as a readable PyRel program of requirements (duckdb or lqp)."""
    from gnd.export.emit import render_pyrel_rules
    from gnd.export.pyrel_runtime import ExportInputError, write_new

    try:
        source = render_pyrel_rules(Path(model_path), target)
    except FileNotFoundError as error:
        print(f"missing input: {error}", file=sys.stderr)
        return EXIT_NO_INPUT
    except ExportInputError as error:
        print(f"cannot write the rules program: {error}", file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- same refusal contract as the checker export
        print(f"export failed: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    try:
        write_new(Path(out_path), source)
    except FileExistsError as error:
        print(f"output exists: {error}", file=sys.stderr)
        return EXIT_COLLISION
    except OSError as error:
        print(f"output failure: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    print(f"Exported the model's rules as PyRel requirements ({target} version) to {out_path}")
    return 0




def _register_export(subparsers):
    export_parser = subparsers.add_parser("export", help="export an optional standalone artifact")
    export_targets = export_parser.add_subparsers(dest="export_target", required=True)
    from gnd.export.souffle_cli import add_parsers
    add_parsers(export_targets)
    from gnd.export.lean_cli import add_parsers as add_lean_parsers

    add_lean_parsers(export_targets)
    pyrel_parser = export_targets.add_parser("pyrel", help="export a standalone PyRel program")
    pyrel_parser.add_argument("model", help="path to the model file")
    pyrel_parser.add_argument("--out", required=True, help="new Python program path")
    connection_group = pyrel_parser.add_mutually_exclusive_group()
    connection_group.add_argument("--duckdb-path", default=":memory:")
    connection_group.add_argument("--connection", help="reserved named Snowflake connection")
    pyrel_parser.add_argument(
        "--rules", choices=("duckdb", "lqp"),
        help="write the model's rules as a readable PyRel program of requirements instead of the checker: "
             "'lqp' enforces them with require on a RelationalAI engine; 'duckdb' checks the same "
             "requirements locally through their violation queries",
    )

    ilp_parser = export_targets.add_parser(
        "ilp",
        help="export background facts, examples and modes for an ILP learner (IK5)",
        description=(
            "Write the learner-neutral ILP form (gnd-ilp/1) of MODEL and a class-mode "
            "label manifest, plus the named adapter's rendering, into a new directory. "
            "Examples are the manifest's populations; the learned predicate wrong/1 "
            "covers the negative class. Prints the export digest, the SHA-256 of "
            "export.json. Exits 0 on success, 3 on an invalid manifest, model or "
            "population or a value the export cannot render, 5 when a population fails "
            "to load, 11 when --out exists, 64 on a usage error, 66 on a missing input, "
            "74 on a refused path."
        ),
    )
    ilp_parser.add_argument("model", help="path to the model file")
    ilp_parser.add_argument("--labels", required=True, help="class-mode label manifest (gnd-labels/1)")
    ilp_parser.add_argument(
        "--target", required=True, choices=("popper", "neutral", "ilasp", "rules"),
        help="learner adapter: popper (neutral form plus bk.pl, exs.pl, bias.pl), neutral, "
             "ilasp (neutral form plus ilasp/task.las), or rules (neutral form plus "
             "rules/features.json)",
    )
    ilp_parser.add_argument("--out", required=True, help="new directory for the export")

    return {'export_parser': export_parser, 'pyrel_parser': pyrel_parser, 'ilp_parser': ilp_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'export':
        selected = _register_export(subparsers)
        parsers.update(selected)
        selected['export_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "export":
        if args.export_target == "ilp":
            from gnd.export.ilp_service import _cmd_export_ilp

            return _cmd_export_ilp(args.model, args.labels, target=args.target, out=args.out)
        if args.export_target.startswith("lean"):
            from gnd.export.lean_cli import dispatch as lean_dispatch

            return lean_dispatch(args)
        if args.export_target != "pyrel":
            from gnd.export.souffle_cli import dispatch
            return dispatch(args)
        if args.rules is not None:
            if args.connection is not None or args.duckdb_path != ":memory:":
                parsers["pyrel_parser"].error("--rules writes a standalone program; --connection and "
                                              "--duckdb-path apply only to the checker export")
            return _cmd_export_pyrel_rules(args.model, args.out, target=args.rules)
        return _cmd_export_pyrel(
            args.model, args.out, duckdb_path=args.duckdb_path, connection=args.connection
        )

    raise ValueError(f"unsupported command: {args.command}")

