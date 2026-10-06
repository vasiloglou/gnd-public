from __future__ import annotations

import gnd.conformance.cli_service as _handler_conformance_cli_service
from gnd.commands._arguments import _add_format_argument


def _register_conformance(subparsers):
    conformance_parser = subparsers.add_parser(
        "conformance",
        help="check that a generated project still matches its model (GEN-02); temporal models refused",
        description=(
            "Ask whether a project `gnd codegen` generated still agrees with "
            "the model it came from. FOUR assertions run. Two are exact and "
            "corroborating: INTEGRITY — every code-emitted file still hashes "
            "to what the codegen manifest recorded — and CURRENCY, the "
            "manifest's model digest against the model's digest now, which IS "
            "model-code drift: the model moved and the code did not. Both are "
            "importable functions rather than CLI-only paths, so a downstream "
            "tool can invoke them without going through argv. The third is "
            "STRUCTURAL, and it is the assertion that makes a green result "
            "mean anything: the emitted surface is checked against the fact "
            "types the MODEL declares, computed from the model and the "
            "filesystem and never from the manifest or a previous generation. "
            "Without it the other two establish only that the generator agrees "
            "with itself — a project that is well-formed and empty, with every "
            "digest re-signed, passes both. The fourth is ARCHITECTURE: authored "
            "module, symbol, artifact and entry-point declarations are compared "
            "with static filesystem and AST observations without executing the "
            "project. Fully offline "
            "over committed artifacts, and the generated project is NEVER "
            "imported — this command reads bytes and hashes them, because "
            "importing a module to inspect it would execute the project's own "
            "code on every CI run. What a GREEN result does not say travels in "
            "the payload, not only in this text: every file the manifest "
            "records appears in either `examined` or `unexamined` by integrity, "
            "and extension files (pyproject.toml, references/) are not digest-gated because "
            "human- and LLM-authored text is not byte-reproducible and cannot "
            "be digest-gated, and the required `limits` block names the "
            "manifest co-edit blind spot — a manifest cannot record its own "
            "digest, so a derived file edited TOGETHER with its manifest entry "
            "is undetectable by digest comparison, exactly as in `gnd doctor`. "
            "Two runs over one unchanged project print byte-identical JSON. "
            "Exits 0 when all four assertions ran and found nothing, 13 when the "
            "generated code no longer matches its model (one band for the "
            "whole command — the payload names which assertion and which "
            "file), 3 when the codegen manifest will not parse, 64 on usage "
            "errors, 66 when the manifest or the model is missing so nothing "
            "could be compared at all (fail closed — a check that could not "
            "run must not read as one that passed), 74 when the project tree "
            "could not be read."
        ),
    )
    conformance_parser.add_argument("model", help="path to the model file")
    conformance_parser.add_argument(
        "directory", help="the generated project's root (the directory `gnd codegen --out` wrote)"
    )
    _add_format_argument(conformance_parser)

    return {'conformance_parser': conformance_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'conformance':
        selected = _register_conformance(subparsers)
        parsers.update(selected)
        selected['conformance_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "conformance":
        return _handler_conformance_cli_service._cmd_conformance(args.model, args.directory, args.format)

    raise ValueError(f"unsupported command: {args.command}")

