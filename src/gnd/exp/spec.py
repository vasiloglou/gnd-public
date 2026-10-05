"""The closed ``SPEC.md`` record — what an experiment DECLARES (plan 03-01).

``SPEC.md`` is untrusted committed metadata, so this module adopts
``gnd.extract.manifest``'s posture verbatim (RESEARCH Security Domain): the
byte-capped read lives in :func:`~gnd.exp.frontmatter.read_frontmatter`,
``extra="forbid"`` makes an unknown field a load-time rejection so a
schema-drifted or swapped file can never read as valid, every id and text field
is :data:`NonEmptyString`, and the experiment kind is a CLOSED ``Literal``
rejected at load rather than at use.

The record's job is to make the close gate's arithmetic well-defined. That gate
(plan 03-07) is a difference of two SETS — ``declared`` question ids from here,
``resolved`` question ids from ``CONCLUSIONS.md`` — and it FAILS when either
difference is non-empty (RESEARCH §6.4). Two declarations refused here follow
directly from that:

- a DUPLICATE question id makes ``declared`` a multiset, and ``declared -
  resolved`` can then no longer distinguish "answered once" from "declared twice
  and answered once";
- ZERO questions makes both differences empty, so an experiment that asked
  nothing closes having established nothing — a gate that cannot fail.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from gnd.exp.frontmatter import FrontmatterError, read_frontmatter
from gnd.model import ValidationIssue, issues_from_validation_error

__all__ = [
    "CLOSE_OBLIGATIONS",
    "EXPERIMENT_DIR_PATTERN",
    "KIND_POLICY",
    "CoversEntry",
    "ExperimentKind",
    "ExperimentSpec",
    "KindPolicy",
    "Question",
    "SpecError",
    "read_spec",
]

#: The experiment id, which IS the directory name on disk. Constrained here
#: rather than at the filesystem call: an id is used to build a path, so the
#: shapes that are dangerous as paths (``..``, absolute forms, separators) must
#: be unrepresentable as ids. ``EXP-`` + three digits + a lowercase slug is the
#: whole vocabulary — the ``.planning/phases/NN-slug/`` convention this
#: repository already reads and writes by hand.
EXPERIMENT_DIR_PATTERN = re.compile(r"^EXP-\d{3}-[a-z0-9][a-z0-9-]*$")

#: The CLOSED experiment vocabulary. A kind outside this set is rejected at
#: load, not at use (the DistractorKind discipline, manifest.py:65-67): "codegen"
#: is an experiment whose conclusion is gated on model-code conformance,
#: "roundtrip" one measured through render/extract fidelity, "analysis" one whose
#: evidence is committed artifacts alone, and "data-driven" one whose bounded
#: agent attempt is accepted only by its closed case contract. Widening this
#: tuple is a decision, and forcing it to be one is the point of closing it.
ExperimentKind = Literal["codegen", "analysis", "roundtrip", "data-driven", "work"]

#: The shipped non-empty idiom (manifest.py:68): strips FIRST, so ``"   "`` is
#: empty rather than a three-character id.
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

#: The rule id every issue from this module carries, so ``gnd exp validate`` maps
#: failures into its output without re-deriving messages.
SPEC_RULE_ID = "experiment:spec-invalid"


class CloseObligation(StrEnum):
    """Closed vocabulary of per-kind close gates."""

    complete_conclusions = "complete-conclusions"
    resolving_evidence = "resolving-evidence"
    conformance = "conformance"
    recorded_launch = "recorded-launch"
    latest_sessions_accepted = "latest-sessions-accepted"


CLOSE_OBLIGATIONS = CloseObligation


@dataclass(frozen=True)
class KindPolicy:
    """The three policy decisions every experiment kind must make."""

    session_runnable: bool
    expectation_authorable: bool
    close_obligations: frozenset[CloseObligation]


_BASE_CLOSE = frozenset(
    {
        CloseObligation.complete_conclusions,
        CloseObligation.resolving_evidence,
    }
)

# The one home for kind policy. Consumers index this table; they do not restate
# allowed-kind sets or a singled-out gated kind.
KIND_POLICY: Mapping[ExperimentKind, KindPolicy] = MappingProxyType(
    {
        "codegen": KindPolicy(
            session_runnable=False,
            expectation_authorable=False,
            close_obligations=_BASE_CLOSE | {CloseObligation.conformance},
        ),
        "analysis": KindPolicy(False, False, _BASE_CLOSE),
        "roundtrip": KindPolicy(False, False, _BASE_CLOSE),
        "data-driven": KindPolicy(True, True, _BASE_CLOSE),
        "work": KindPolicy(
            session_runnable=True,
            expectation_authorable=True,
            close_obligations=_BASE_CLOSE
            | {
                CloseObligation.recorded_launch,
                CloseObligation.latest_sessions_accepted,
            },
        ),
    }
)


class SpecError(Exception):
    """A ``SPEC.md`` failed to read, parse, or validate.

    Carries ``issues`` (:class:`~gnd.model.ValidationIssue` records) so the CLI
    maps the failure verbatim. ONE exception type covers a bad fence, bad YAML
    and a bad schema alike: ``gnd exp validate`` maps all three to band 3
    (ill-formed — the shipped meaning of the band, the same claim ``load_model``
    makes), and leaking two exception types would make that one mapping two
    branches that can drift apart.
    """

    def __init__(self, message: str, issues: list[ValidationIssue] | None = None):
        super().__init__(message)
        self.issues: list[ValidationIssue] = issues or [
            ValidationIssue(path="", message=message, rule_id=SPEC_RULE_ID)
        ]


class Question(BaseModel):
    """One declared question. Closed, because the nested record is where an
    ``answer:`` key would otherwise be silently accepted — a spec that carried
    its own answers would make the conclusions document optional."""

    model_config = ConfigDict(extra="forbid")

    id: NonEmptyString
    text: NonEmptyString


class CoversEntry(BaseModel):
    """One explicit model-element address covered by a work experiment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    operation: NonEmptyString | None = None
    constraint: NonEmptyString | None = None
    fact_type: NonEmptyString | None = None
    derivation: NonEmptyString | None = None

    @model_validator(mode="after")
    def _has_exactly_one_address(self) -> CoversEntry:
        populated = sum(
            value is not None
            for value in (
                self.operation,
                self.constraint,
                self.fact_type,
                self.derivation,
            )
        )
        if populated != 1:
            raise ValueError(
                "covers entry must declare exactly one of operation, constraint, "
                "fact_type, or derivation"
            )
        return self


class ExperimentSpec(BaseModel):
    """What an experiment declares before it runs."""

    model_config = ConfigDict(extra="forbid")

    id: NonEmptyString
    kind: ExperimentKind
    title: NonEmptyString
    #: At least one: see the module docstring — zero questions closes vacuously.
    questions: list[Question] = Field(min_length=1)
    #: G-14's one reference field, flat like a PLAN's ``depends_on:``. Richer
    #: shapes (a reason string per reference) were available and declined: G-14
    #: buys "one field and one check", and this spends exactly that.
    follows: list[NonEmptyString] = Field(default_factory=list)
    covers: list[CoversEntry] = Field(default_factory=list)
    covers_exemption: Literal["tests-only"] | None = None
    #: Codegen experiments use these experiment-relative references to rerun
    #: conformance at close time. They are optional for the other experiment
    #: kinds and paired so a half-bound subject is never accepted.
    model: NonEmptyString | None = None
    project: NonEmptyString | None = None

    @field_validator("id")
    @classmethod
    def _id_is_a_legal_directory_name(cls, value: str) -> str:
        if not EXPERIMENT_DIR_PATTERN.match(value):
            raise ValueError(
                f"{value!r} is not a legal experiment id; the id IS the directory "
                f"name, so it must match {EXPERIMENT_DIR_PATTERN.pattern} — a "
                f"separator or a '..' in an id would be a path, not a name"
            )
        return value

    @model_validator(mode="after")
    def _question_ids_are_unique(self) -> ExperimentSpec:
        seen: set[str] = set()
        duplicates: list[str] = []
        for question in self.questions:
            if question.id in seen and question.id not in duplicates:
                duplicates.append(question.id)
            seen.add(question.id)
        if duplicates:
            raise ValueError(
                f"duplicate question id(s) {', '.join(sorted(duplicates))}; the "
                f"close gate is a difference of two SETS (declared vs resolved), "
                f"and a duplicate declaration makes that difference ambiguous — "
                f"it can no longer tell 'answered once' from 'declared twice, "
                f"answered once'"
            )
        if (self.model is None) != (self.project is None):
            raise ValueError(
                "model and project must be declared together; a codegen "
                "conformance subject cannot be half-bound"
            )
        return self


def _validation_issues(error: ValidationError) -> list[ValidationIssue]:
    return issues_from_validation_error(error, SPEC_RULE_ID)


def read_spec(path: str | Path) -> ExperimentSpec:
    """Load an :class:`ExperimentSpec` strictly, or raise :class:`SpecError`.

    The ``manifest.py:_load`` skeleton with the frontmatter reader in the JSON
    reader's place: the byte cap and the alias guard run inside
    :func:`~gnd.exp.frontmatter.read_frontmatter` BEFORE the block is parsed, and
    the closed pydantic model runs before any field is used.
    """
    file_path = Path(path)
    try:
        mapping, _ = read_frontmatter(file_path)
    except FrontmatterError as error:
        raise SpecError(
            f"{file_path} is not a readable SPEC.md: {error}",
            [ValidationIssue(path=str(file_path), message=str(error), rule_id=SPEC_RULE_ID)],
        ) from error
    try:
        return ExperimentSpec.model_validate(mapping)
    except ValidationError as error:
        raise SpecError(
            f"{file_path} is not a valid ExperimentSpec:\n{error}",
            _validation_issues(error),
        ) from error
