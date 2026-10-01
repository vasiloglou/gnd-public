"""The closed ``CONCLUSIONS.md`` record — what an experiment RESOLVED (plan 03-02).

``SPEC.md`` declares questions; this document resolves them. Together they are
the two operands of the close gate's subtraction (:mod:`gnd.exp.close`,
RESEARCH §6.4), so this module's whole job is to make the ``resolved`` side of
that arithmetic well-defined and to make two documents *unrepresentable* rather
than merely refused somewhere downstream:

- **a conclusion that cites nothing.** ``evidence`` is :data:`NonEmptyString`,
  so ``""`` and ``"   "`` die at load. RESEARCH §6.3 reproduced the vector: an
  empty pointer resolves to the experiment directory, which exists, so a
  validator written with ``.exists()`` accepts an uncited conclusion as cited.
  :mod:`gnd.exp.paths` refuses it again lexically and structurally, but *typing
  the field* removes the vector one whole layer earlier — before any pointer is
  ever handed to a filesystem call.
- **a non-answer that does not say why.** ``unanswered`` and ``invalidated``
  require a non-empty ``reason``.

That second rule is the record-level half of G-12's asymmetry, and the comment
on :data:`Outcome` below is where a future reader learns the asymmetry is
deliberate. State it once more here because it is the thing most likely to be
"corrected" by someone being helpful:

    **An honest ``unanswered`` with a reason is a PASSING shape, not a degraded
    one.** The gate this record feeds enforces COMPLETENESS and HONESTY, never a
    positive result. A gate that demanded success would pay for lying, and would
    reproduce on GND's own process layer precisely the error every prior phase
    has been correcting — an artifact reporting a state nobody established.

Consequently there is **no field recording whether the experiment succeeded**,
and its absence is the design, not an omission. ``extra="forbid"`` on the nested
record is what keeps a well-meaning ``passed: true`` from being silently
accepted and then read by somebody as a verdict the gate never computed.

Two shape decisions worth their sentences:

- ``resolves`` is REQUIRED but carries no ``min_length``. ``ExperimentSpec``
  needs ``min_length=1`` on ``questions`` because zero questions makes BOTH set
  differences empty — a gate that cannot fail. The mirror does not apply here:
  zero resolutions leaves ``declared - resolved`` equal to every declared id, so
  an empty ``resolves:`` is exactly what the gate is built to catch and it is
  better caught there (band 14, naming each forgotten question) than as a schema
  error (band 3, naming a document that parsed fine).
- ``id`` is validated against :data:`~gnd.exp.spec.EXPERIMENT_DIR_PATTERN` and
  is compared to the spec's id by the close gate. A field nobody reads is a
  field that lies; if this record is going to carry an id, something has to
  check it, or a CONCLUSIONS.md copied from another experiment reads as this
  one's.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from gnd.exp.frontmatter import FrontmatterError, read_frontmatter
from gnd.exp.spec import EXPERIMENT_DIR_PATTERN
from gnd.model import ValidationIssue

__all__ = [
    "CONCLUSIONS_RULE_ID",
    "ConclusionsError",
    "ExperimentConclusions",
    "Outcome",
    "Resolution",
    "read_conclusions",
]

#: The CLOSED outcome vocabulary, rejected at load rather than at use (the
#: ``DistractorKind`` discipline, ``manifest.py:65-67``). Three members, and the
#: set is closed so that widening it has to be a decision somebody makes on
#: purpose.
#:
#: **Why the set is closed and why ``unanswered`` is a PASSING value.** These
#: three are outcomes, not grades. ``answered`` and ``unanswered`` are equally
#: valid states for a closed experiment, and ``invalidated`` — the run did not
#: bear on the declared question at all — is a third. The close gate never reads
#: this field to decide pass or fail (G-12); it reads it only to decide whether a
#: ``reason`` is obligatory, and that obligation is discharged in
#: :class:`Resolution`'s own validator before the gate ever runs.
#:
#: A fourth member meaning "succeeded"/"failed" does not belong here and would be
#: the beginning of a gate that pays for lying. If a future phase needs to record
#: whether the experiment's SUBJECT passed, that is a different claim about a
#: different artifact and it gets its own field in its own record (G-15's rule
#: applied one layer up: no single payload carries two claim families).
Outcome = Literal["answered", "unanswered", "invalidated"]

#: The shipped non-empty idiom (``manifest.py:68``): strips FIRST, so ``"   "``
#: is empty rather than a three-character pointer.
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

#: The rule id every issue from this module carries, so ``gnd exp close`` maps
#: failures into its output without re-deriving messages.
CONCLUSIONS_RULE_ID = "experiment:conclusions-invalid"

#: The outcomes that are themselves an answer, and therefore need no ``reason``.
#: The honesty rule below is stated as the COMPLEMENT of this set rather than as
#: a list of the outcomes that need one, so a member added to :data:`Outcome`
#: later is obligated to explain itself by default. Written the other way round,
#: a new member would arrive silently exempt — a rule that stops covering the
#: case it was widened for is a rule that cannot fail.
_ANSWERING_OUTCOMES: frozenset[str] = frozenset({"answered"})


class ConclusionsError(Exception):
    """A ``CONCLUSIONS.md`` failed to read, parse, or validate.

    Carries ``issues`` (:class:`~gnd.model.ValidationIssue` records) so the CLI
    maps the failure verbatim. ONE exception type covers a bad fence, bad YAML
    and a bad schema alike — the :class:`~gnd.exp.spec.SpecError` contract, for
    the same reason: ``gnd exp close`` maps all three to band 3 (ill-formed), and
    leaking two exception types would make that one mapping two branches that can
    drift apart.
    """

    def __init__(self, message: str, issues: list[ValidationIssue] | None = None):
        super().__init__(message)
        self.issues: list[ValidationIssue] = issues or [
            ValidationIssue(path="", message=message, rule_id=CONCLUSIONS_RULE_ID)
        ]


class Resolution(BaseModel):
    """One declared question, resolved.

    Closed (``extra="forbid"``), because the nested record is where a
    ``passed: true`` would otherwise be silently accepted — and a field that
    looks like a verdict, sitting beside outcomes the gate deliberately ignores,
    is how somebody comes to believe the gate checked it.
    """

    model_config = ConfigDict(extra="forbid")

    #: Must equal a question id declared in ``SPEC.md``. The gate reports this
    #: value verbatim when the id is an orphan, so it is untouched here.
    id: NonEmptyString
    outcome: Outcome
    #: A pointer to ONE raw artifact inside the experiment directory — D-22 made
    #: structural (G-13). Typed :data:`NonEmptyString` rather than ``str``: see
    #: the module docstring. Its *resolvability* is checked by
    #: :func:`~gnd.exp.paths.resolve_evidence_path` at gate time, because that
    #: needs a directory and this record does not have one.
    evidence: NonEmptyString
    #: Obligatory when the outcome is not an answer. Defaults to empty because an
    #: ``answered`` resolution's reason is its evidence.
    reason: str = ""

    @model_validator(mode="after")
    def _a_non_answer_says_why(self) -> Resolution:
        if self.outcome not in _ANSWERING_OUTCOMES and not self.reason.strip():
            raise ValueError(
                f"resolution {self.id!r} has outcome {self.outcome!r} but no "
                f"reason; the close gate demands COMPLETENESS and HONESTY, never "
                f"a positive result — an {self.outcome} outcome is a perfectly "
                f"valid way to close, and the price of that is saying why it is a "
                f"non-answer rather than leaving the question silently open"
            )
        return self


class ExperimentConclusions(BaseModel):
    """What an experiment resolved. The ``resolved`` side of the gate's subtraction."""

    model_config = ConfigDict(extra="forbid")

    id: NonEmptyString
    #: Required, but deliberately unbounded below — see the module docstring: an
    #: empty ``resolves:`` is the gate's business (band 14, naming every
    #: forgotten question), not the schema's.
    resolves: list[Resolution]

    @field_validator("id")
    @classmethod
    def _id_is_a_legal_experiment_id(cls, value: str) -> str:
        if not EXPERIMENT_DIR_PATTERN.match(value):
            raise ValueError(
                f"{value!r} is not a legal experiment id; conclusions declare the "
                f"experiment they belong to, and that id IS a directory name — it "
                f"must match {EXPERIMENT_DIR_PATTERN.pattern}"
            )
        return value

    @model_validator(mode="after")
    def _resolution_ids_are_unique(self) -> ExperimentConclusions:
        seen: set[str] = set()
        duplicates: list[str] = []
        for resolution in self.resolves:
            if resolution.id in seen and resolution.id not in duplicates:
                duplicates.append(resolution.id)
            seen.add(resolution.id)
        if duplicates:
            raise ValueError(
                f"duplicate resolution id(s) {', '.join(sorted(duplicates))}; the "
                f"close gate is a difference of two SETS (declared vs resolved), "
                f"and a duplicate resolution makes 'resolved' a multiset — the "
                f"mirror of the spec's duplicate-question refusal, on the other "
                f"side of the same subtraction"
            )
        return self


def _validation_issues(error: ValidationError) -> list[ValidationIssue]:
    return [
        ValidationIssue(
            path=".".join(str(part) for part in entry["loc"]),
            message=entry["msg"],
            rule_id=CONCLUSIONS_RULE_ID,
        )
        for entry in error.errors()
    ]


def read_conclusions(path: str | Path) -> ExperimentConclusions:
    """Load an :class:`ExperimentConclusions` strictly, or raise :class:`ConclusionsError`.

    The :func:`~gnd.exp.spec.read_spec` skeleton over the same reader, so the
    stat-cap-then-read-then-alias-guard-then-parse ordering that makes the
    untrusted-input bounds real is inherited rather than restated (T-03-03,
    T-03-04, T-03-11).
    """
    file_path = Path(path)
    try:
        mapping, _ = read_frontmatter(file_path)
    except FrontmatterError as error:
        raise ConclusionsError(
            f"{file_path} is not a readable CONCLUSIONS.md: {error}",
            [
                ValidationIssue(
                    path=str(file_path), message=str(error), rule_id=CONCLUSIONS_RULE_ID
                )
            ],
        ) from error
    try:
        return ExperimentConclusions.model_validate(mapping)
    except ValidationError as error:
        raise ConclusionsError(
            f"{file_path} is not a valid ExperimentConclusions:\n{error}",
            _validation_issues(error),
        ) from error
