"""The ONE home for a model's stable, machine-independent label.

v5.1 Phase 1 §6.5 (D-P1.3, r2 A4). Two copies of this rule existed and they did
not agree — which is worse than duplication, because a reader comparing the two
payloads would have concluded the difference was in the models rather than in
the anchors:

* ``measure/report.py`` anchored on ``Path.cwd()``, the INVOCATION root. That
  was the repair made after the ``eaa672a`` detached-worktree failure.
* ``fidelity/report.py`` anchored on ``Path(__file__).resolve().parents[3]``,
  the INSTALLED checkout — while its docstring claimed to be "unchanged" from
  measure's. It was not, and that false sentence is this repair's own evidence.

**The invocation root wins (A4).** The installed location is a property of how
the reader got GND, not of what they measured; two people running the identical
command from the identical directory must get the identical label even when one
installed from a wheel and the other from a worktree. `gnd conformance` reaches
the same outcome without a third copy, by naming the file only — its model is a
caller-named argv path rather than a corpus member.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["stable_model_identifier"]


def stable_model_identifier(model_path: str) -> str:
    """A model label independent of absolute-vs-relative path spelling.

    Below the invocation directory, the useful relative label the committed
    measurement receipts already use; anywhere else, the basename alone. The
    payload names the model without naming the machine it was measured on, and
    the recorded digest remains the authoritative content identity.
    """
    resolved = Path(model_path).resolve()
    invocation_root = Path.cwd().resolve()
    try:
        return resolved.relative_to(invocation_root).as_posix()
    except ValueError:
        return resolved.name
