"""The measurement lane: labelled populations -> per-constraint false-pass /
false-fail / undecided rates (VER-03).

This package turns the checker's verdicts into a *measurement*. It reads the
populations ``gnd synth`` wrote, joins each against the ground truth the sidecar
recorded (the constructive witness, never the verdict — C1), and scores every
(constraint, population) observation into exactly one of six disjoint outcome
cells. The six cells PARTITION the evidence — ``correct + false_pass +
false_fail + undecided + masked_by_vacuity + tool_defect == n`` for every
per-constraint row — and that invariant is enforced in production code by
:class:`gnd.measure.score.PartitionError`, not only in a test, because a metric
that cannot come out badly is this phase's declared failure mode and the
accounting is exactly where it would hide.

**Offline by construction (owner's two-lane correction).** Nothing in this
package imports a provider or network module: published numbers are computed
offline from committed artifacts. ``tests/test_measure_offline.py`` fails the
suite on any provider/network import reachable from ``gnd.measure`` — a
regex-over-source test, not a convention. The rule is scoped to the metrics
lane; it deliberately does NOT police ``gnd.synth``, whose development lane may
be live and nondeterministic.
"""

from __future__ import annotations

__all__: list[str] = []
