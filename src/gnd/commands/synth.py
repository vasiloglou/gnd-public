from __future__ import annotations

import gnd.synth.service as _handler_synth_service
from gnd.commands._arguments import _add_format_argument, _positive_int


def _register_synth(subparsers):
    synth_parser = subparsers.add_parser(
        "synth",
        help="generate labelled synthetic populations from a model (DATA-01)",
        description=(
            "Generate labelled synthetic populations, each with a provenance "
            "SIDECAR. --class conforming builds populations the checker accepts; "
            "--class violating mutates a conforming baseline, one population per "
            "(constraint, operator) pair, each admitted only after the real checker "
            "confirms the model-derived typed prediction (D-05'); --class all does "
            "both. The development lane is probabilistic by default: --seed omitted "
            "draws OS entropy per population and records it, so data is fresh yet "
            "regenerable; --seed N is the deterministic variant-regeneration path. "
            "--pool consumes an admitted pool artifact; an omitted --pool builds "
            "and materialises a Faker pool beside the corpus. Exits 5 on a "
            "generator invariant failure, 6 on a quarantined checker/witness or "
            "prediction/observation disagreement (C1)."
        ),
    )
    synth_parser.add_argument("model", help="path to the model file")
    synth_parser.add_argument(
        "--out", default=".gnd/synth", help="output root for populations (default: .gnd/synth)"
    )
    synth_parser.add_argument(
        "--class",
        dest="synth_class",
        choices=("conforming", "boundary", "violating", "all"),
        default="conforming",
        help=(
            "the population class to generate: conforming, boundary, violating, or "
            "all. `boundary` derives cases from the constraints' own declared bounds "
            "(D-06) and includes the `no-subjects` and `unchecked` frontier kinds"
        ),
    )
    synth_parser.add_argument(
        "--pool",
        default=None,
        help="path to an admitted pool artifact (default: build a Faker pool)",
    )
    synth_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed (omitted: draw OS entropy, the probabilistic development default)",
    )
    synth_parser.add_argument(
        "--baseline-seed",
        type=int,
        default=None,
        help=(
            "seed of the conforming baseline a violating run mutates (recorded in "
            "every violating sidecar so each case is traceable to what it mutated; "
            "default: --seed, else OS entropy)"
        ),
    )
    synth_parser.add_argument(
        "--seeds",
        type=_positive_int,
        default=1,
        help=(
            "number of independent seed variants to generate for every requested "
            "class (default 1, the lightweight dev lane). --seeds 30 is the "
            "publication/degeneracy invocation: 30 clean seeds give 95%% confidence "
            "(rule of three) that fewer than 10%% of the GENERATOR's runs are "
            "degenerate"
        ),
    )
    _add_format_argument(synth_parser)

    return {'synth_parser': synth_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'synth':
        selected = _register_synth(subparsers)
        parsers.update(selected)
        selected['synth_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "synth":
        return _handler_synth_service._cmd_synth(
            args.model,
            args.out,
            args.synth_class,
            args.pool,
            args.seed,
            args.seeds,
            args.format,
            args.baseline_seed,
        )

    raise ValueError(f"unsupported command: {args.command}")

