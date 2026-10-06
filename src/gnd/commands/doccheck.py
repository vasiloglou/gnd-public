from __future__ import annotations

import gnd.fidelity.doccheck_service as _handler_fidelity_doccheck_service


def _register_doccheck(subparsers):
    doccheck_parser = subparsers.add_parser(
        "doccheck",
        help="validate a rendered document's manifest against its renderer obligations (DATA-02)",
        description=(
            "Discharge the gnd-render-doc skill's obligations by CODE over the "
            "document manifest (skill prose explains, validators discharge). "
            "Four obligations: (1) binding — document_sha256, "
            "source_population_sha256 and applicable_sha256 match the actual "
            "file bytes; (2) rendering — every role filler of every APPLICABLE "
            "fact type in the source population is mentioned in the document "
            "under lexical normalization, direct fillers as their value and "
            "composite fillers via their identifying component values; "
            "inapplicable fact types are exempt BY the published "
            "applicable-set artifact, never by leniency; (3) distractors — at "
            "least one of each kind (out-of-model, near-miss-entity, "
            "absent-fact), every distractor text present in the document, and "
            "every absent-fact distractor genuinely absent from the source "
            "population; (4) renderer identity fields non-empty. Exits 0 when "
            "every obligation holds, 3 on any violation (one line each), 64 on "
            "usage errors, 66 when the applicable-set artifact or any "
            "manifest-named file is missing (fail closed — an obligation that "
            "cannot be checked is never skipped)."
        ),
    )
    doccheck_parser.add_argument("model", help="path to the model file")
    doccheck_parser.add_argument(
        "manifest", help="path to the document manifest (paths resolve beside it)"
    )
    doccheck_parser.add_argument(
        "--artifacts",
        required=True,
        help="the gnd extract bundle directory holding <stem>.applicable.json",
    )

    return {'doccheck_parser': doccheck_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'doccheck':
        selected = _register_doccheck(subparsers)
        parsers.update(selected)
        selected['doccheck_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "doccheck":
        return _handler_fidelity_doccheck_service._cmd_doccheck(args.model, args.manifest, args.artifacts)

    raise ValueError(f"unsupported command: {args.command}")

