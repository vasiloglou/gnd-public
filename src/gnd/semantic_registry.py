"""Production branch identities; no proof claim follows from registration.

This source-owned inventory describes decision branches, including branches whose
semantics are not formalized yet. It never reads a proof declaration or corpus.
Tracing is optional, context-local, and absent from public report serialization.
"""

from __future__ import annotations

import re  # noqa: F401 -- compatibility export
from collections.abc import Iterator  # noqa: F401 -- compatibility export
from contextlib import contextmanager  # noqa: F401 -- compatibility export
from contextvars import ContextVar  # noqa: F401 -- compatibility export
from dataclasses import dataclass  # noqa: F401 -- compatibility export
from typing import TYPE_CHECKING

from gnd.applicability import applicable_scope_ids  # noqa: F401 -- compatibility export
from gnd.branches import BY_ID as _BY_ID
from gnd.branches import (
    IR_DIMENSIONS,  # noqa: F401 -- compatibility export
    OBLIGATION_KINDS,  # noqa: F401 -- compatibility export
    OUTCOMES,  # noqa: F401 -- compatibility export
    REGISTRY,
    SURFACES,  # noqa: F401 -- compatibility export
    WITNESS_KINDS,  # noqa: F401 -- compatibility export
    Branch,  # noqa: F401 -- compatibility export
    UnregisteredBranchError,  # noqa: F401 -- compatibility export
    branch,  # noqa: F401 -- compatibility export
    capture_branches,  # noqa: F401 -- compatibility export
    constraint_variant,  # noqa: F401 -- compatibility export
    is_registered,  # noqa: F401 -- compatibility export
    record_branch,  # noqa: F401 -- compatibility export
    snapshot_branch,  # noqa: F401 -- compatibility export
    time_relative_operand,  # noqa: F401 -- compatibility export
    violated_branch,  # noqa: F401 -- compatibility export
)
from gnd.branches import SNAPSHOT as _SNAPSHOT  # noqa: F401 -- compatibility export
from gnd.branches import (
    TIME_RELATIVE as _TIME_RELATIVE,  # noqa: F401 -- compatibility export
)
from gnd.branches import TRACES as _TRACES  # noqa: F401 -- compatibility export
from gnd.branches import UNIVERSE as _UNIVERSE  # noqa: F401 -- compatibility export
from gnd.branches import (
    applicability_rows as _applicability_rows,  # noqa: F401 -- compatibility export
)
from gnd.branches import (
    assurance_rows as _assurance_rows,  # noqa: F401 -- compatibility export
)
from gnd.branches import (
    composition_rows as _composition_rows,  # noqa: F401 -- compatibility export
)
from gnd.branches import (
    derivation_rows as _derivation_rows,  # noqa: F401 -- compatibility export
)
from gnd.branches import (
    feedback_rows as _feedback_rows,  # noqa: F401 -- compatibility export
)
from gnd.branches import (
    projection_rows as _projection_rows,  # noqa: F401 -- compatibility export
)
from gnd.branches import row as _row  # noqa: F401 -- compatibility export
from gnd.branches import (
    snapshot_rows as _snapshot_rows,  # noqa: F401 -- compatibility export
)
from gnd.branches import (
    transition_rows as _transition_rows,  # noqa: F401 -- compatibility export
)
from gnd.semantic_ir import ADAPTER_REFUSALS  # noqa: F401 -- compatibility export

if TYPE_CHECKING:
    from gnd.population import Population  # noqa: F401 -- compatibility export


# A descriptor is (family, variants, arity, violating witness, owner, inputs).
# Variants follow the evaluator's input selectors, not the fixture labels.


if len(_BY_ID) != len(REGISTRY):
    raise RuntimeError("duplicate production scope id")


