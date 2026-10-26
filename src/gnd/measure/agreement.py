"""The class-mode agreement scorer for ``gnd measure --labels`` (IK3, D10 (o)).

This docstring is the one home of the cell definitions; the contract page
``docs/reference/measure-labels.md`` cites it.

A class-mode manifest tags each population ``positive`` or ``negative`` and says,
for each rule R, which class it should fire on (``fires_on: F``). Over the
populations, for each R:

- **Fired:** the checker's verdict for R is ``warning`` or ``fail``.
- **Silent:** the verdict is ``pass``.
- **Decided** means fired or silent. ``vacuous`` and ``unchecked`` are counted on
  their own, never folded into a cell or a denominator, and the host never
  supplies them.
- ``fired_on_<class>`` and ``silent_on_<class>``: populations of that class where
  R fired (or was silent) / that class's populations where R's verdict is
  decided.
- ``vacuous`` and ``unchecked``: populations where R had that verdict / all
  populations.

The agreeing cells are ``fired_on_F`` and ``silent_on_<not F>``; the row carries
``fires_on`` so a reader can see which. Nothing here computes an aggregate,
accuracy or F1 (D-01 style), and disagreement is evidence, not a failure:
class mode exits 0 (IK3-D6).
"""

from __future__ import annotations

from typing import Any

from gnd.measure.score import PartitionError

__all__ = ["CELL_KEYS", "FIRED", "agreement_rows"]

CLASSES = ("negative", "positive")
FIRED = frozenset({"warning", "fail"})
CELL_KEYS = (
    "fired_on_negative",
    "fired_on_positive",
    "silent_on_negative",
    "silent_on_positive",
    "vacuous",
    "unchecked",
)


def _fraction(numerator: int, denominator: int) -> dict[str, int]:
    return {"numerator": numerator, "denominator": denominator}


def agreement_rows(
    rules: dict[str, str],
    constraints: dict[str, dict[str, Any]],
    populations: list[Any],
) -> list[dict[str, Any]]:
    """One row per rule, in ref order. ``populations`` carry ``class_`` and a
    checker ``report``; every rule must have exactly one verdict per population,
    or the run is an internal fault (exit 70), never a narrowed denominator."""
    rows = []
    for ref, fires_on in sorted(rules.items()):
        counts = {f"{kind}_{label}": 0 for kind in ("fired", "silent", "decided") for label in CLASSES}
        vacuous = unchecked = 0
        for population in populations:
            verdicts = [v.verdict for v in population.report.verdicts if v.constraint_ref == ref]
            if len(verdicts) != 1:
                raise PartitionError(
                    f"rule {ref} drew {len(verdicts)} verdicts on population "
                    f"{population.id!r}; expected exactly one"
                )
            (verdict,) = verdicts
            label = population.class_
            if verdict in FIRED:
                counts[f"fired_{label}"] += 1
            elif verdict == "pass":
                counts[f"silent_{label}"] += 1
            elif verdict == "vacuous":
                vacuous += 1
                continue
            elif verdict == "unchecked":
                unchecked += 1
                continue
            else:
                raise PartitionError(f"rule {ref} drew an unknown verdict {verdict!r}")
            counts[f"decided_{label}"] += 1
        decided = sum(counts[f"decided_{label}"] for label in CLASSES)
        if decided + vacuous + unchecked != len(populations):
            raise PartitionError(f"rule {ref}: the agreement cells do not partition the populations")
        cells = {
            f"{kind}_on_{label}": _fraction(counts[f"{kind}_{label}"], counts[f"decided_{label}"])
            for kind in ("fired", "silent")
            for label in CLASSES
        }
        cells["vacuous"] = _fraction(vacuous, len(populations))
        cells["unchecked"] = _fraction(unchecked, len(populations))
        constraint = constraints[ref]
        rows.append(
            {
                "ref": ref,
                "constraint_type": str(constraint.get("type") or ""),
                "modality": str(constraint.get("modality") or ""),
                "source": constraint.get("source"),
                "status": constraint.get("status"),
                "fires_on": fires_on,
                "cells": {key: cells[key] for key in CELL_KEYS},
            }
        )
    return rows
