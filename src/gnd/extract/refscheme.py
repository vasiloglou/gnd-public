"""Three-path reference-scheme resolution and the applicable-set artifact (R-10′).

The extractor's matcher needs every entity to have a printable identity — and
measured on the primary model, a third of its fact types touch an entity that
has none directly (``reference.mode`` ``unit-based``/``external`` yield no
``reference.value_type``). This module answers with THREE paths instead of one,
because the alternative is five fact types silently vanishing from every
denominator — the flattered number this phase exists to prevent:

1. **Direct** — ``popular``/``general`` modes and subtypes via
   ``inherits_reference``: :func:`reference_identity` CALLS
   ``popvalidate.resolve_reference_value_type`` — never a second
   reference-scheme walk (``synth/pool.py:16-17`` states the in-repo rule).
2. **Composite** — an ``external``-mode entity whose top-level external
   ``uniqueness`` constraint anchors on it. The identifying sequence lives in
   ``role_refs`` — the research prototype read ``constraint.get("roles")`` and
   silently matched nothing (the PANEL-5-named bug). Each referenced role's
   object type must itself resolve (recursively, cycle-safe with a ``seen``
   set — subtype cycles are not rejected by model validation, T-01.1-07).
3. **Unmatchable** — declared, with a MECHANISM string in
   ``measure/coverage.py:126-136``'s register: what makes the identity
   underivable, never a bare label.

Every disposition is derived from the model document — never a hand-maintained
exclusion list (coverage.py ``_applicability``'s governing rule): a hard-coded
``{"salary"}`` would miss ``booking`` on the next model and mislabel the first
model that widens its pool.

:func:`applicable_set` publishes the result as the first-class JSON artifact
``gnd extract`` writes (``<stem>.applicable.json``) and that doccheck/fidelity
consume fail-closed: an unmeasurable fact type reads as unmeasurable with its
mechanism, never as coverage.
"""

from __future__ import annotations

from gnd.refscheme import (
    __all__,  # noqa: F401 -- compatibility export
    applicable_set,  # noqa: F401 -- compatibility export
    reference_identity,  # noqa: F401 -- compatibility export
)
from gnd.refscheme import anchors_on as _anchors_on  # noqa: F401 -- compatibility export
from gnd.refscheme import (
    fact_types_by_id as _fact_types_by_id,  # noqa: F401 -- compatibility export
)
from gnd.refscheme import (
    object_types_by_id as _object_types_by_id,  # noqa: F401 -- compatibility export
)
from gnd.refscheme import (
    referenced_object_type as _referenced_object_type,  # noqa: F401 -- compatibility export
)
from gnd.refscheme import (
    unmatchable_reason as _unmatchable_reason,  # noqa: F401 -- compatibility export
)
from gnd.universe import resolve_reference_value_type  # noqa: F401 -- compatibility export


