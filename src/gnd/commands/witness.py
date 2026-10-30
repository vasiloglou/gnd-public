from __future__ import annotations


def _register_witness(subparsers):
    from gnd.witness.cli import add_parsers as add_witness_parsers

    add_witness_parsers(subparsers)

    return {name: subparsers.choices[name] for name in ('witness', 'replay', 'witness-view', 'why-not')}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'witness':
        selected = _register_witness(subparsers)
        parsers.update(selected)
        selected['witness'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
        selected['replay'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
        selected['witness-view'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
        selected['why-not'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command in {"witness", "replay", "witness-view", "why-not"}:
        from gnd.witness.cli import run as run_witness

        return run_witness(args)

    raise ValueError(f"unsupported command: {args.command}")

