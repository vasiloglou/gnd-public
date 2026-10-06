"""Compatibility assurance surface over the ordered package."""

from gnd.assurance._wire import (
    CorrespondenceDigests as CorrespondenceDigests,
)
from gnd.assurance.core import (
    PHASE2_TRUST_ASSUMPTIONS as PHASE2_TRUST_ASSUMPTIONS,
)
from gnd.assurance.core import (
    REGISTRY as REGISTRY,
)
from gnd.assurance.core import (
    AdaptedSnapshot as AdaptedSnapshot,
)
from gnd.assurance.core import (
    AssuranceBlock as AssuranceBlock,
)
from gnd.assurance.core import (
    AssuranceBlockV1 as AssuranceBlockV1,
)
from gnd.assurance.core import (
    AssuranceConsumer as AssuranceConsumer,
)
from gnd.assurance.core import (
    AssuranceLevel as AssuranceLevel,
)
from gnd.assurance.core import (
    AssuranceScope as AssuranceScope,
)
from gnd.assurance.core import (
    AssuranceSurface as AssuranceSurface,
)
from gnd.assurance.core import (
    AuthenticatedExecution as AuthenticatedExecution,
)
from gnd.assurance.core import Branch as Branch
from gnd.assurance.core import (
    CorrespondenceEvidence as CorrespondenceEvidence,
)
from gnd.assurance.core import (
    ExtractionRoute as ExtractionRoute,
)
from gnd.assurance.core import (
    Literal as Literal,
)
from gnd.assurance.core import (
    SemanticDecision as SemanticDecision,
)
from gnd.assurance.core import (
    SnapshotDecision as SnapshotDecision,
)
from gnd.assurance.core import (
    ValidatedScopeWalk as ValidatedScopeWalk,
)
from gnd.assurance.core import (
    assurance_outcome as _assurance_outcome,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    assurance_policy as _assurance_policy,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    assurance_prerequisites as assurance_prerequisites,
)
from gnd.assurance.core import (
    certify_result as certify_result,
)
from gnd.assurance.core import (
    certify_snapshot as certify_snapshot,
)
from gnd.assurance.core import (
    currency_valid as _currency_valid,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    dataclass as dataclass,
)
from gnd.assurance.core import (
    derive_assurance_scope as derive_assurance_scope,
)
from gnd.assurance.core import (
    internal_value as _internal_value,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    is_registered as is_registered,
)
from gnd.assurance.core import (
    is_sha256_hex as is_sha256_hex,
)
from gnd.assurance.core import (
    mint_execution as _mint_execution,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    phase3_scope_ids as phase3_scope_ids,
)
from gnd.assurance.core import (
    phase3_target as _phase3_target,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    record_branch as record_branch,
)
from gnd.assurance.core import (
    result_obligation as _result_obligation,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    semantic_decision_for_band as semantic_decision_for_band,
)
from gnd.assurance.core import (
    semantic_spec as semantic_spec,
)
from gnd.assurance.core import (
    sorted_set as _sorted_set,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    unique_sorted as _unique_sorted,  # noqa: F401 -- compatibility surface
)
from gnd.assurance.core import (
    walk_snapshot_scope as walk_snapshot_scope,
)
