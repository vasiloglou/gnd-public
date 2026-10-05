"""Compatibility exports for invocation-bound reference intake."""
from __future__ import annotations

from gnd.model import BOUND as _BOUND  # noqa: F401 -- compatibility export
from gnd.model import COMBINED as _COMBINED  # noqa: F401 -- compatibility export
from gnd.model import (
    MAX_BYTES,  # noqa: F401 -- compatibility export
    MAX_ENTRIES,  # noqa: F401 -- compatibility export
    MAX_SET_BYTES,  # noqa: F401 -- compatibility export
    BoundPopulationView,  # noqa: F401 -- compatibility export
    BoundReferenceContext,  # noqa: F401 -- compatibility export
    OccurrenceOrigin,  # noqa: F401 -- compatibility export
    ReferenceInputError,  # noqa: F401 -- compatibility export
    ReferenceOrigin,  # noqa: F401 -- compatibility export
    bind_population,  # noqa: F401 -- compatibility export
    bind_references,  # noqa: F401 -- compatibility export
    candidate_fact_count,  # noqa: F401 -- compatibility export
    is_bound_population,  # noqa: F401 -- compatibility export
    resolve_context,  # noqa: F401 -- compatibility export
    retained_root,  # noqa: F401 -- compatibility export
    validate_declarations,  # noqa: F401 -- compatibility export
    validate_reference_structure,  # noqa: F401 -- compatibility export
)
from gnd.model import TOKEN as _TOKEN  # noqa: F401 -- compatibility export
from gnd.model import bind_at as _bind_at  # noqa: F401 -- compatibility export
from gnd.model import relative as _relative  # noqa: F401 -- compatibility export
from gnd.values import reference_model_digest  # noqa: F401 -- compatibility export
