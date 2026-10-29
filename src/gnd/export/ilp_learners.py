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

from gnd.export import ilp, ilp_amie, ilp_asp, ilp_popper, ilp_prompt, ilp_rules

__all__ = ["EXPORT_TARGETS", "IMPORT_TARGETS", "LEARNERS", "MINED_TARGETS", "Learner", "learner"]


@dataclass(frozen=True)
class Learner:
    """One adapter of the bridge."""

    #: The ``--target`` spelling.
    target: str
    #: The run record's required ``learner.name``, or any of a tuple of names
    #: (IL5-D2); ``None`` accepts any name.
    learner: str | tuple[str, ...] | None
    #: The IK2 ``method`` token written into ``provenance.induction``.
    method: str
    #: Whether ``gnd export ilp`` accepts this target.
    exports: bool
    #: Neutral form to the adapter's files; ``None`` writes ``neutral.json`` only. An
    #: ``unlabelled-horn`` entry renders one population instead (IL4).
    render: Callable[..., dict[str, bytes]] | None
    #: The learner's printed output to ``gnd-ilp-clauses/1``; ``None`` reads that JSON.
    #: An ``unlabelled-horn`` entry reads to mined rules instead (IL4).
    parse: Callable[[str], Any] | None
    #: ``labelled-clauses`` is what ``gnd import ilp-rules`` accepts;
    #: ``unlabelled-horn`` what ``gnd import mined-rules`` accepts (IL4).
    contract: str
    #: ``export.json``'s ``adapter_version`` for this target.
    adapter_version: str
    #: Whether check 9 reads a ``"true"``/``"false"`` string on a boolean role as
    #: the boolean; ASP spells booleans bare, so ILASP's quoted ones are refused (IL2-D13).
    boolean_strings: bool = True
    #: The target whose export a run record binds; ``None`` is this entry's own.
    #: A non-exporting entry binds another's, so the import never builds an
    #: export no command can write (IL5-D1, IL1-Q2).
    binds: str | None = None
    #: The import's adapter check of the parsed clauses and their text against
    #: the export's neutral form, after the run record's bindings and before the
    #: rewrite; ``None`` checks nothing more (IL2-Q3).
    vet: Callable[[dict[str, Any], dict[str, Any], str], None] | None = None


LEARNERS: dict[str, Learner] = {
    "popper": Learner(target="popper", learner="popper", method="ilp-popper", exports=True,
                      render=ilp_popper.render, parse=ilp_popper.parse_program,
                      contract="labelled-clauses", adapter_version=ilp_popper.ADAPTER_VERSION,
                      vet=ilp_popper.check_thresholds),
    "neutral": Learner(target="neutral", learner=None, method="ilp-neutral", exports=True,
                       render=None, parse=None, contract="labelled-clauses",
                       adapter_version=ilp.ADAPTER_VERSION),
    "ilasp": Learner(target="ilasp", learner="ilasp", method="ilp-ilasp", exports=True,
                     render=ilp_asp.render, parse=ilp_asp.parse_hypothesis,
                     contract="labelled-clauses", adapter_version=ilp_asp.ADAPTER_VERSION,
                     boolean_strings=False, vet=ilp_asp.check_thresholds),
    # The agent adapter ids of gnd.agents.AgentAdapterId, pinned by a test (IL5-D2).
    "llm": Learner(target="llm", learner=("claude", "codex"), method="ilp-llm", exports=False,
                   render=None, parse=None, contract="labelled-clauses",
                   adapter_version=ilp_prompt.PROMPT_VERSION, binds="neutral"),
    "rules": Learner(target="rules", learner="wittgenstein", method="ilp-rules", exports=True,
                     render=ilp_rules.render, parse=ilp_rules.parse_ruleset,
                     contract="labelled-clauses", adapter_version=ilp_rules.ADAPTER_VERSION),
    "amie": Learner(target="amie", learner="amie", method="ilp-amie", exports=True,
                    render=ilp_amie.render, parse=ilp_amie.parse_rules,
                    contract="unlabelled-horn", adapter_version=ilp_amie.ADAPTER_VERSION),
}
EXPORT_TARGETS = tuple(target for target, entry in LEARNERS.items() if entry.exports)
IMPORT_TARGETS = tuple(target for target, entry in LEARNERS.items()
                       if entry.contract == "labelled-clauses")
MINED_TARGETS = tuple(target for target, entry in LEARNERS.items()
                      if entry.contract == "unlabelled-horn")


def learner(target: str) -> Learner:
    """The entry for ``target``; argparse has already refused an unknown one."""
    return LEARNERS[target]
