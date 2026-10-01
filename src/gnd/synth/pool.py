"""``EntityPool`` — per-object-type identifier universes drawn from a pool artifact.

The single load-bearing choice here is **sampling WITH replacement**. Independent
draws — one fresh identifier per role occurrence — give 8 distinct entities across
8 facts, so EVERY cross-fact-type join is zero-row and the whole join frontier
reports 0% error while being completely untested. That is the exact degeneracy
Polyfactory was measured producing (D-17) and the property this class exists to
defeat: recurrence of the SAME identifier across fact types is what gives a join
rows to check. :meth:`EntityPool.draw` therefore samples with replacement from a
FIXED universe, and the universe comes from an admitted :class:`poolfile.Pool`
artifact (the D-19 seam) — ``EntityPool`` never mints an identifier itself.

Value-typed roles draw from the pool's ``value_types`` samples where the pool
carries them (its coherence gate has already checked those), falling back to
``values.make_value`` under the model's declared range / enum for a value type the
pool does not sample. Primitives are resolved by the loader's OWN
:func:`popvalidate.resolve_primitive` walk — never a second reference-scheme walk.
"""

from __future__ import annotations

from random import Random
from typing import Any

from gnd import popvalidate
from gnd.model import Model
from gnd.synth.poolfile import Pool
from gnd.synth.value_domain import (
    draw_value_for_constraints,
    object_value_constraints,
)

__all__ = ["EntityPool"]


class EntityPool:
    """Fixed identifier universes over an admitted pool, sampled with replacement.

    ``pool`` is a gate-passed :class:`poolfile.Pool`. The pool's ``object_types``
    map (entity id -> identifier list) is the universe :meth:`draw` and
    :meth:`universe` serve; ``value_types`` backs :meth:`draw_value`.
    """

    def __init__(self, model: Model, pool: Pool, rng: Random) -> None:
        self._model = model
        self._pool = pool
        self._rng = rng
        self._object_types = pool.object_types
        self._value_types = pool.value_types
        self._value_constraints = object_value_constraints(model)

    def universe(self, object_type_id: str) -> list[Any]:
        """The pool's fixed identifier list for ``object_type_id`` (never mints).

        Empty when the pool does not carry the type — a caller that needs an
        identifier for an unpooled type is a generator bug the assembler surfaces,
        not a place to invent one.
        """
        return list(self._object_types.get(str(object_type_id), []))

    def draw(self, object_type_id: str) -> Any:
        """One identifier for ``object_type_id``, sampled WITH REPLACEMENT.

        Recurrence across fact types is the entire point — the same identifier
        may (and must, for joins to have rows) come back on a later draw. Raises
        :class:`KeyError` when the pool has no universe for the type, because
        minting one here is the very degeneracy this class forbids.
        """
        universe = self._object_types.get(str(object_type_id))
        if not universe:
            raise KeyError(
                f"pool has no identifier universe for object type "
                f"{object_type_id!r}; EntityPool never mints identifiers (D-19)."
            )
        return self._rng.choice(universe)

    def draw_value(self, object_type_id: str) -> Any:
        """One value for a value-typed role.

        Prefers the pool's own ``value_types`` samples (already coherence-checked)
        and falls back to :func:`values.make_value` under any object-scope
        ``value`` constraint (range / enum) for a type the pool does not sample.
        """
        samples = self._value_types.get(str(object_type_id))
        if samples:
            return self._rng.choice(samples)
        primitive = popvalidate.resolve_primitive(str(object_type_id), self._model)
        if primitive is None:
            raise KeyError(
                f"value type {object_type_id!r} is neither sampled by the pool nor "
                f"resolvable to a primitive; EntityPool cannot draw for it."
            )
        constraints = self._value_constraints.get(str(object_type_id), [])
        return draw_value_for_constraints(
            str(primitive), self._rng, constraints
        )
