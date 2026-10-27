"""The ILP bridge's learner registry (ilp-learners IL1).

One entry per ``--target``, in declaration order; later adapters are appended.
The export and import services consult this table and name no learner
themselves (IL-R3). The command modules keep literal ``choices=`` tuples, so no
registry import happens at parser construction (RF5); a test pins them, and the
two schema ``target`` enums, to the tuples below. Spec:
``.gnd-planning/milestones/ilp-learners/notes/phase-IL1-spec.md`` §6.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gnd.export import ilp, ilp_asp, ilp_popper

__all__ = ["EXPORT_TARGETS", "IMPORT_TARGETS", "LEARNERS", "Learner", "learner"]


@dataclass(frozen=True)
class Learner:
    """One adapter of the bridge."""

    #: The ``--target`` spelling.
    target: str
    #: The run record's required ``learner.name``; ``None`` accepts any name.
    learner: str | None
    #: The IK2 ``method`` token written into ``provenance.induction``.
    method: str
    #: Whether ``gnd export ilp`` accepts this target.
    exports: bool
    #: Neutral form to the adapter's files; ``None`` writes ``neutral.json`` only.
    render: Callable[[dict[str, Any]], dict[str, bytes]] | None
    #: The learner's printed output to ``gnd-ilp-clauses/1``; ``None`` reads that JSON.
    parse: Callable[[str], dict[str, Any]] | None
    #: ``labelled-clauses`` is what ``gnd import ilp-rules`` accepts.
    contract: str
    #: ``export.json``'s ``adapter_version`` for this target.
    adapter_version: str
    #: Whether check 9 reads a ``"true"``/``"false"`` string on a boolean role as
    #: the boolean; ASP spells booleans bare, so ILASP's quoted ones are refused (IL2-D13).
    boolean_strings: bool = True


LEARNERS: dict[str, Learner] = {
    "popper": Learner(target="popper", learner="popper", method="ilp-popper", exports=True,
                      render=ilp_popper.render, parse=ilp_popper.parse_program,
                      contract="labelled-clauses", adapter_version=ilp_popper.ADAPTER_VERSION),
    "neutral": Learner(target="neutral", learner=None, method="ilp-neutral", exports=True,
                       render=None, parse=None, contract="labelled-clauses",
                       adapter_version=ilp.ADAPTER_VERSION),
    "ilasp": Learner(target="ilasp", learner="ilasp", method="ilp-ilasp", exports=True,
                     render=ilp_asp.render, parse=ilp_asp.parse_hypothesis,
                     contract="labelled-clauses", adapter_version=ilp_asp.ADAPTER_VERSION,
                     boolean_strings=False),
}
EXPORT_TARGETS = tuple(target for target, entry in LEARNERS.items() if entry.exports)
IMPORT_TARGETS = tuple(target for target, entry in LEARNERS.items()
                       if entry.contract == "labelled-clauses")


def learner(target: str) -> Learner:
    """The entry for ``target``; argparse has already refused an unknown one."""
    return LEARNERS[target]
