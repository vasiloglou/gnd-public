"""The fidelity lane: source population vs extracted population -> per-fact-type
precision / recall / unresolved (SC3).

This package measures the EXTRACTOR. It never measures the checker, and the two
must not meet in one output: **R-03″'s two-lane rule** says a ``gnd verify``
payload never carries a fidelity rate and — its dual, enforced here — a
``gnd fidelity`` payload never carries a verdict, a band, or an
``acceptance_ready`` claim. A checker pass over an uncalibrated extraction is not
evidence of faithfulness (PANEL-2), so the two channels stay structurally
separate rather than separated by convention.

**No blended number (D-01).** Every rate in this lane belongs to exactly ONE
fact type and ships with its numerator AND its denominator. Nothing in this
package averages across fact types — the same rule ``gnd.measure`` holds across
constraints, one layer up. A single "extraction accuracy" figure would be
precisely the number that cannot come out badly.

**Structurally unpublishable while uncalibrated (PANEL-1, R-11′).** R-06's
cross-family delta and R-12's owner-labelled calibration set are panel-confirmed
DEFERRALS, so this lane cannot bound its own round-trip bias: the renderer
authored the ground truth the extractor is scored against. Rather than leave
that in prose, ``fidelity.schema.json`` makes ``calibration.state``
``"uncalibrated"`` and ``publishable`` ``false`` REQUIRED constants and closes
every object, so no interval or confidence field can exist in a payload at all.

**Offline by construction.** ``tests/test_measure_offline.py``'s scan 4 is rooted
at this package as well as ``gnd.extract`` — the fidelity number is computed from
committed case directories, never from a live call.
"""

from __future__ import annotations

__all__: list[str] = []
