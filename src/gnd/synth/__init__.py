"""Synthetic value generation and the pool-artifact seam (Phase 2, DATA-01).

This package is the value/label source layer that sits BELOW population assembly
(D-04): it produces scalars that satisfy the population loader's own primitive
predicates and a pool artifact that any proposer — Faker today, an LLM skill
tomorrow (D-19/D-20) — emits in one shape. It never assembles populations and
never checks population-level constraints (uniqueness, frequency, ring, subset,
exclusion, joins); that is plan 03's assembly layer.

Importing this package must NOT require the optional ``synth`` extra: faker is
imported lazily inside the functions that need it (see ``values.make_value``), so
``gnd check`` on a machine without the extra is entirely unaffected.
"""

from __future__ import annotations

#: The generator identity every synthetic population's sidecar records (D-07).
#: BUMP THIS whenever generation output changes for a fixed seed — a new
#: primitive branch, a changed faker draw, a reordered build. A measured rate
#: that cannot be regenerated is not a measurement (D-07/D-07′), and the sidecar
#: pins reproduction on the tuple ``(pool_sha256, rng_seed, generator_version,
#: model_id)``. The string is opaque and monotonic; readers compare, never parse.
GENERATOR_VERSION = "gnd-synth/1"

__all__ = ["GENERATOR_VERSION"]
