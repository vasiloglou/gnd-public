from __future__ import annotations

import gnd.codegen.service as _handler_codegen_service


def _register_codegen(subparsers):
    codegen_parser = subparsers.add_parser(
        "codegen",
        help="emit a plain-Python agent project derived from the model (GEN-01)",
        description=(
            "Turn model.orm.yaml into a plain-Python project with the GND "
            "shape: <package>/tools.py (one derived function per fact type, "
            "named and parameterized through the published model-id to "
            "Python-symbol mapping, with docstrings derived from the model's "
            "readings), the four-file extraction artifact bundle under "
            "artifacts/, a code-emitted SKILL.md the terminal agent runs, and "
            "create-once extension files (pyproject.toml, references/) that "
            "regeneration never rewrites. No provider SDK and no network "
            "library is emitted, so the generated project is CI-runnable with "
            "zero network and no API key — the agent running the generated "
            "SKILL.md is the only place a model is ever called. Every emitted "
            "Python module is parsed before any byte reaches disk. "
            "Re-running over an existing generated project is idempotent: an "
            "unchanged model performs ZERO writes and leaves every hash "
            "identical. A derived file you hand-edited, and an unmanaged file "
            "sitting at a derived path, are REFUSED rather than overwritten; "
            "--force overwrites them and still never touches an extension "
            "file. Exits 0 when the tree is written or already current, 3 when "
            "the model is invalid, two of its ids sanitize to one Python "
            "symbol (rename one), or the existing manifest is unreadable, 11 "
            "when a write was refused and nothing was destroyed, 64 on usage "
            "errors, 70 when an emitter invariant breaks over an already-valid "
            "model, 74 when the output path is refused or unwritable."
        ),
    )
    codegen_parser.add_argument("model", help="path to the model file")
    codegen_parser.add_argument(
        "--out",
        required=True,
        help="output directory for the generated project",
    )
    codegen_parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "overwrite hand-edited derived files and adopt unmanaged files at "
            "derived paths. Extension files (pyproject.toml, references/) are "
            "NEVER overwritten, with or without this flag, and no path outside "
            "the generated layout is ever touched."
        ),
    )

    return {'codegen_parser': codegen_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'codegen':
        selected = _register_codegen(subparsers)
        parsers.update(selected)
        selected['codegen_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "codegen":
        return _handler_codegen_service._cmd_codegen(args.model, args.out, force=args.force)

    raise ValueError(f"unsupported command: {args.command}")

