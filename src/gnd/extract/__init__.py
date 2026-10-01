"""The extraction lane: per-model artifacts derived offline from ``model.orm.yaml``.

**Offline by construction — R-04‴'s artifact boundary.** This package derives
and validates; it never calls a provider. The executing agent running the
``gnd-extract`` skill IS the LLM call, and the handoff in both directions is a
file on disk: this package emits the shape-only projection, the
constraint-blind verbalization, and the applicable-set artifact that the skill
consumes, and ``gnd verify`` later ingests what the skill wrote. An embedded
provider client — or any network library — anywhere in this lane would collapse
the boundary that keeps published fidelity numbers computable offline from
committed artifacts (D-20/D-22).
``tests/test_measure_offline.py::test_no_network_library_is_reachable_from_the_extraction_lane``
fails the suite on any network-library import reachable from this package — a
closure walk over source, not a convention. It is the fourth, separately-named
scan (scans 1-3 keep their owner-decided scopes; re-scoping a guard without a
decision is forbidden, G-3).

Why a package rather than folding into ``measure/``: R-03's hard rule is that
no single output carries both a per-run verdict and a fidelity rate, and the
module boundary is the cheapest structural enforcement of it — the extraction
lane produces artifacts and per-run inputs, the measurement lane aggregates,
and neither imports the other's emitters.
"""

from __future__ import annotations

__all__: list[str] = []
