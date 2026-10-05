"""The exit bands shared by more than one module — one home, by construction.

``gnd/cli.py`` owns the CLI's vocabulary and ``gnd/solve.py`` owns the station
harness, and both must speak the same bands. Because ``cli`` imports ``solve``,
``solve`` cannot import ``cli`` back, so before this module existed the harness
restated ``64``, ``66``, ``70``, ``74`` and ``17`` as private literals. That is
two homes for a normative value, and **nothing guarded them**: had one drifted,
no test would have noticed, because the registries in ``tests/test_exp_bands.py``
and ``tests/test_verification_fixes.py`` iterate ``vars(cli)`` and never saw the
harness's copies at all.

All runtime exit allocations live here with their allocation rationale.
Consumer modules retain their old names through imports and aliases.

``cli.py`` re-imports these names, so ``cli.EXIT_USAGE`` and friends keep
resolving for the forty-two test modules and three source modules that use them.
The registries that iterate ``vars(cli)`` are unaffected: an imported name is in
the importing module's namespace.
"""

from __future__ import annotations

__all__ = [
    "EXIT_CHECKER_DEFECT",
    "EXIT_COLLISION",
    "EXIT_DRIFT",
    "EXIT_EVOLUTION_OPERATIONS_GATED",
    "EXIT_EXPERIMENT_OPEN",
    "EXIT_GENERATOR",
    "EXIT_ILL_FORMED",
    "EXIT_INTERNAL",
    "EXIT_IO",
    "EXIT_MODEL_CODE_DRIFT",
    "EXIT_NO_INPUT",
    "EXIT_NO_INSTALL",
    "EXIT_OK",
    "EXIT_QUARANTINE",
    "EXIT_REVIEW_INCONCLUSIVE",
    "EXIT_SESSION_NOT_ACCEPTED",
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


# Generator vocabulary (Phase 2). 5-9 were reserved as verdict-band headroom in
# STATE.md; the synthetic-data generator is the first user of that headroom.
# 5 = a generator invariant failed (a constructive witness could not be
# established, a re-admission rejection, an oscillating repair). 6 = a C1
# quarantine — the checker disagreed with the constructive witness (a candidate
# checker false-fail), so the case is RETAINED under <out>/quarantine/ rather than
# discarded. Plan 04 wires 6 into the measurement layer (checker_defects[]); this
# plan is its first user at the generation layer. 7-9 remain unallocated.
EXIT_GENERATOR = 5  # a generator invariant failed — GeneratorError
EXIT_QUARANTINE = 6  # checker/witness disagreement quarantined (C1)
# 6 has two context-specific NAMES for one MEANING — "the checker disagreed with
# independent ground truth". At the generation layer (plan 03) it is a quarantined
# witness discrepancy; at the measurement layer (plan 04) it is a promoted
# checker_defects[] entry (an alethic false pass, an alethic false fail, or an
# impossible tool_defect cell — direction-agnostic, C9/D-01). Same value, same
# meaning, so the exit-code space is not double-allocated. 7-9 stay unallocated.
EXIT_CHECKER_DEFECT = 6  # measurement found a deterministic checker defect (C9)

# Lifecycle vocabulary — see the module docstring for each code's "would
# masquerade as X" justification. 5-9 stay unallocated as verdict-band headroom.
EXIT_DRIFT = 10  # assets stale / missing / modified — doctor's verdict, never install's
EXIT_COLLISION = 11  # an unmanaged file blocked a write; nothing was destroyed
EXIT_NO_INSTALL = 12  # no manifest at any resolved target root
EXIT_MODEL_CODE_DRIFT = 13  # the generated code no longer matches its model
# EXIT_EXPERIMENT_OPEN (14) is imported from gnd.exits for gnd.exp.close.
EXIT_SESSION_NOT_ACCEPTED = 15  # a session ended without exact contract acceptance


EXIT_REVIEW_INCONCLUSIVE = 16  # a completed panel had fewer than three successes
# 17 is the solve harness's walk halt: a gated station walk stopped before the
# end of its own selection. It is NOT a verdict about the work -- the station's
# own exit is recorded verbatim in the walk log and interpreted by nobody, and a
# station exiting 11 must not make `gnd solve` claim EXIT_COLLISION about itself.
# It is not 15 (that names a session's acceptance, one station's business) and not
# 14 (an experiment's obligations); this code says only "the walk did not finish".
# EXIT_WALK_HALTED (17) is imported from gnd.exits -- see the note above.
# 18 is the ORM+ v2 evolve gate: the proposal is WELL
# FORMED and refused on policy, which no band above says. It is not 3 (that is
# "malformed or digest-mismatched input", and a gated proposal is neither), not
# 11 (that is "a write was refused, nothing was destroyed" — true here, but 11
# is already the stale/collision band and merging the two would make "retry
# after refreshing the model" the wrong advice for half of it), and not 13/14/15
# (each names a different artifact's obligations). Nothing is written on this
# path either, so the "nothing was destroyed" half of 11 still holds.
EXIT_EVOLUTION_OPERATIONS_GATED = 18  # a v2 operation delta gnd evolve does not own
# EXIT_IO (74) is imported from gnd.exits -- see the note above.


EXIT_OK = 0
EXIT_ILL_FORMED = 3
