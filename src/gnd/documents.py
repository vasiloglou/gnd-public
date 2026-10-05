"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from gnd.errors import ValidationIssue


class DeonticNote(BaseModel):
    """A retained top-level deontic note from the ORM document."""

    text: str
    rationale: str | None = None


class Model(BaseModel):
    """A loaded, validated ORM conceptual model."""

    # Attribute assignment is the common mutation path and should fail
    # immediately. Nested dictionaries/lists remain mutable, so Population's
    # validation marker also binds a digest of current model content.
    model_config = ConfigDict(frozen=True, extra="forbid")

    version: int
    #: D-06: a stable, OPAQUE identifier for this model. Optional for backward
    #: compatibility — every model authored before the field existed has None,
    #: and the population header cross-check simply does not run for those. It
    #: is never resolved to a path and never opened (T-01.1-01); the
    #: unforgeable runtime proof that a population was validated against THIS
    #: model is ``Population.validated_against`` (D-02), not this string.
    model_id: str | None = None
    source: dict[str, Any] = Field(default_factory=dict)
    object_types: list[dict[str, Any]]
    fact_types: list[dict[str, Any]]
    constraints: list[dict[str, Any]] = Field(default_factory=list)
    #: ORM+ v2 state transitions, raw dicts like every other section. A v1
    #: document loads with ``operations: []`` and is byte-identical to what it
    #: loaded before v2 existed. Every downstream consumer feature-detects on
    #: THIS list being non-empty, never on ``version``: a ``version: 2``
    #: document that declares no operations must behave exactly like a v1 one,
    #: and a version test would silently make it behave differently.
    operations: list[dict[str, Any]] = Field(default_factory=list)
    reference_populations: list[dict[str, Any]] = Field(default_factory=list)
    _references: Any = PrivateAttr(default=None)
    rejected_proposals: list[dict[str, Any]] = Field(default_factory=list)
    #: Trace-compiled obligations, keyed by operation id (B2). A SIDE TABLE
    #: rather than an ``operation["compiled"]`` key, which is what the plan and
    #: the phase spec first described.
    #:
    #: The attachment was tried and reproduced a defect: ``operations_digest``
    #: is taken over the operations section, so writing into those dicts moved
    #: the digest and every committed steps.json stopped matching its own model.
    #: Stripping the key back out before hashing would have worked only if no
    #: author could ever write one -- and ``$defs.operation`` does not set
    #: ``additionalProperties: false``, so an authored ``compiled:`` key is legal
    #: YAML that the digest would then silently ignore. A private attribute has
    #: neither problem: the loaded section stays exactly as authored, and there
    #: is nothing for a key to collide with.
    _compiled: dict[str, list[dict[str, Any]]] = PrivateAttr(default_factory=dict)

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        document = super().model_dump(*args, **kwargs)
        if not self.reference_populations:
            document.pop("reference_populations", None)
        return document

    def compiled_obligations(self, operation_id: str) -> list[dict[str, Any]]:
        """The compiled and retained obligations of one operation, in order."""
        return self._compiled.get(str(operation_id), [])

    deontic_notes: list[DeonticNote] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)


DeonticNote.__module__ = 'gnd.model'

Model.__module__ = 'gnd.model'


MAX_YAML_EVENTS = 1_000_000  # parse-event budget for untrusted YAML


def structured_derivation_ids(model: Model) -> tuple[str, ...]:
    """Ids of fact types whose ``derivation_rule`` is the structured object
    form, in declared order.

    The ONE published home for the "does this fact type carry a machine-shaped
    rule" predicate (v5.0 Phase 3, standing rule 4): the report-version
    selector, codegen's constructor non-emission, conformance's expected
    surface and synth's refusal all consume this function, never a private
    ``isinstance`` copy. A legacy free-text ``derivation_rule`` string is NOT
    structured -- it keeps every pre-v5 behaviour (r2 A10), and this predicate
    is where that boundary is drawn exactly once.
    """

    return tuple(
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    )


structured_derivation_ids.__module__ = "gnd.model"
