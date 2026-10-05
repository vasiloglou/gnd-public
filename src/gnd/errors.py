"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ValidationError


class ModelLoadError(Exception):
    """Raised when a model file cannot be safely read/parsed (pre-validation)."""


class ValidationIssue(BaseModel):
    """Unified error record for both validation layers."""

    path: str
    message: str
    rule_id: str
    severity: Literal["error", "warning"] = "error"


def issues_from_validation_error(
    error: ValidationError, rule_id: str
) -> list[ValidationIssue]:
    return [
        ValidationIssue(
            path=".".join(str(part) for part in entry["loc"]),
            message=entry["msg"],
            rule_id=rule_id,
        )
        for entry in error.errors()
    ]


class ModelValidationError(Exception):
    """Raised when a model file fails layer-1 or layer-2 validation."""

    def __init__(
        self,
        issues: list[ValidationIssue],
        warnings: list[ValidationIssue] | None = None,
    ):
        self.issues = list(issues)
        self.warnings = list(warnings or [])
        summary = "; ".join(f"{i.path}: {i.message}" for i in self.issues)
        super().__init__(f"model validation failed: {summary}")


class PopulationLoadError(Exception):
    """Raised when a population file cannot be loaded or is malformed."""


MAX_SUMMARY_ISSUES = 20


class PopulationValidationError(PopulationLoadError):
    """Raised when a population document fails D-10 schema validation.

    Carries the same :class:`~gnd.model.ValidationIssue` records as
    :class:`~gnd.model.ModelValidationError` — one unified error vocabulary.

    ``warnings`` carries the warning-severity issues found on the SAME layer-2
    pass (WR-05). ``load_population`` used to assemble them only AFTER the error
    check had already raised, so they were computed for a clean load and thrown
    away for a dirty one — the exact inversion of where they are useful. A
    population that both mismatched its model structurally and omitted
    ``model_id`` lost the ``population:model-id-absent`` record, which is
    precisely the diagnostic explaining the structural mismatch: "you validated
    against the wrong model." D-04 makes exit 3 the outcome where a retry loop
    most needs the full picture.
    """

    def __init__(
        self,
        issues: list[ValidationIssue],
        warnings: list[ValidationIssue] | None = None,
    ):
        self.issues = list(issues)
        self.warnings = list(warnings or [])
        head = self.issues[:MAX_SUMMARY_ISSUES]
        summary = "; ".join(f"{i.path}: {i.message}" for i in head)
        if len(self.issues) > len(head):
            summary += f"; ... (+{len(self.issues) - len(head)} more)"
        super().__init__(f"population validation failed: {summary}")


class UnvalidatedPopulationError(Exception):
    """:func:`check` was called with a population that never passed layer-2
    (model-relative) validation against *this* model object (D-02).

    Skipping CORE-04 is made structurally impossible rather than merely
    discouraged: a population whose facts do not have the shape the model
    declares makes ``_project`` filter them out, so uniqueness sees an empty
    projection and mandatory an empty universe — and the checker then
    affirmatively reports both as satisfied. Documentation could not prevent
    that; this precondition can.

    From the CLI this path is unreachable by construction (``cli.py`` always
    loads with ``model=``), so it is NOT dead code — it guards the Phase 2
    generator, the Phase 4 retry loop, and every future in-process caller. The
    CLI's existing catch-all maps it to exit 70 (EX_SOFTWARE), which is the
    right band: arriving here unvalidated is a harness/programming bug, not a
    model or population signal, and 70 never masquerades as a band verdict.
    """

    def __init__(self, population: Population, model: Model | None = None):
        if population.validated_against is None:
            state = "it was never validated (validated_against=nothing)"
        elif model is not None and population.validated_against is not model:
            state = "it was validated against a DIFFERENT model object"
        else:
            state = (
                "it WAS validated against this model, but its content has changed "
                "since — the recorded content digest no longer matches. Mutating a "
                "loaded population (assigning to a field, appending to "
                "population.facts[...], or model_copy(update={...})) re-opens the "
                "very hole layer 2 closes (CR-01); re-load or re-validate the "
                "mutated content instead"
            )
        super().__init__(
            "check() was called with a population that was not validated against "
            "this model. Load it via load_population(path, model=model), which "
            "runs layer-2 structural validation (CORE-04) and stamps the result. "
            "There is deliberately no bypass (D-18). If you deep-copied a "
            "validated population, the marker's identity was lost — re-load or "
            "re-stamp it; the copy fails closed on purpose. "
            f"(population declares model={population.model!r}; {state})"
        )


class TransitionLoadError(Exception):
    """A walk was refused before evaluation. Always exit 3.

    Carries the digests AS SUPPLIED (or ``None`` where the document could not
    be parsed far enough to have them) because ``report.schema.json`` promises a
    payload on every exit path, and the payload for a refused walk still has to
    say which model and which operations the caller claimed to be walking.
    """

    def __init__(
        self,
        issues: list[ValidationIssue],
        *,
        supplied: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(issues[0].message if issues else "transition run refused")
        self.issues = issues
        self.supplied = supplied or {}


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gnd.documents import Model
    from gnd.population import Population

ModelLoadError.__module__ = 'gnd.model'

ValidationIssue.__module__ = 'gnd.model'

issues_from_validation_error.__module__ = 'gnd.model'

ModelValidationError.__module__ = 'gnd.model'

PopulationLoadError.__module__ = 'gnd.population'

PopulationValidationError.__module__ = 'gnd.population'

UnvalidatedPopulationError.__module__ = 'gnd.checker'

TransitionLoadError.__module__ = 'gnd.transition'
