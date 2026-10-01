"""The exit bands shared by more than one module — one home, by construction.

``gnd/cli.py`` owns the CLI's vocabulary and ``gnd/solve.py`` owns the station
harness, and both must speak the same bands. Because ``cli`` imports ``solve``,
``solve`` cannot import ``cli`` back, so before this module existed the harness
restated ``64``, ``66``, ``70``, ``74`` and ``17`` as private literals. That is
two homes for a normative value, and **nothing guarded them**: had one drifted,
no test would have noticed, because the registries in ``tests/test_exp_bands.py``
and ``tests/test_verification_fixes.py`` iterate ``vars(cli)`` and never saw the
harness's copies at all.

Only the bands with more than one consumer live here. The rest stay in
``cli.py`` beside the justification prose that explains each allocation — moving
a constant away from its reasoning is its own kind of second home.

``cli.py`` re-imports these names, so ``cli.EXIT_USAGE`` and friends keep
resolving for the forty-two test modules and three source modules that use them.
The registries that iterate ``vars(cli)`` are unaffected: an imported name is in
the importing module's namespace.
"""

from __future__ import annotations

__all__ = [
    "EXIT_EXPERIMENT_OPEN",
    "EXIT_INTERNAL",
    "EXIT_IO",
    "EXIT_NO_INPUT",
    "EXIT_USAGE",
    "EXIT_WALK_HALTED",
    "SOLVE_CONTROL_PLANE_EXITS",
]

#: EX_USAGE — outside the normative 0-4 band contract.
EXIT_USAGE = 64

#: EX_NOINPUT — a required artifact is missing; fail closed.
#:
#: Not a new allocation: 66 has been in use since 01.2/D-22 and phase 02.1, but
#: only ever as a RAW INTEGER LITERAL at five sites. Naming it is what makes the
#: shipped disjointness-proof idiom — grep the ``EXIT_* =`` assignments — sound;
#: without the name that grep misses 66, and a future phase could allocate it to
#: a new command while doccheck and fidelity were already returning it.
EXIT_NO_INPUT = 66

#: EX_SOFTWARE — outside the normative 0-4 band contract.
EXIT_INTERNAL = 70

#: EX_IOERR — target unreadable/unwritable, or a path the guard refused.
EXIT_IO = 74

#: An experiment's declared obligations remain open. Shared by CLI and close.
EXIT_EXPERIMENT_OPEN = 14

#: A gated station walk halted before completing its own selection (v2.0 phase 4).
#:
#: NOT a verdict about the work. The station's own exit is recorded verbatim in
#: the walk log and interpreted by nobody, and a station exiting 11 must not make
#: ``gnd solve`` claim ``EXIT_COLLISION`` about itself. It is not 15 (that names
#: a session's acceptance, which is one station's business) and not 14 (an
#: experiment's obligations); this code says only "the walk did not finish".
EXIT_WALK_HALTED = 17

#: Ordered help-text data for the solve harness. Keeping the control-plane
#: numbers beside their named allocations means ``gnd solve --help`` cannot
#: retain a hand-written numeric copy when one of these constants changes.
SOLVE_CONTROL_PLANE_EXITS: tuple[tuple[int, str], ...] = (
    (0, "a completed walk or informational action"),
    (EXIT_WALK_HALTED, "a walk that halted at a station"),
    (EXIT_USAGE, "usage"),
    (EXIT_NO_INPUT, "a missing path"),
    (EXIT_INTERNAL, "an internal defect"),
    (EXIT_IO, "an I/O refusal"),
)
