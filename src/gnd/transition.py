"""Transition evaluation -- the loader half (Phase 2, lane 1).

``gnd check MODEL --pre PRE --steps STEPS --post POST`` audits a WALK: an
ordered list of operation invocations claimed to have carried a population from
one state to another. This module owns everything that happens BEFORE any
evaluation -- reading the walk, verifying the three digests, validating the
steps against the model, and refusing a population whose declared coverage
cannot support a frame comparison.

Every refusal here is exit 3, and exit 3 means REFUSED BEFORE EVALUATION BEGAN.
That sentence is load-bearing: the band function never sees 3, and a payload
carrying ``evaluated: false`` means exactly this module said no. A condition
discovered mid-walk is a verdict, never a rejection -- see the spec's
``intermediate-unloadable``, which is graded ``unchecked`` for that reason.

Validation order is normative (``phase-2-spec.md`` section 4) and each stage is
pinned by a corpus walk carrying TWO defects, so an implementation that runs
them out of order reports the wrong one and fails:

1. read and parse the walk, then layer 1 against ``steps.schema.json``
   (``order`` is unobservable here: a document that is not an object has no
   digests to check) -- ``transition:steps-shape``
2. the digests -- ``order-digest-before-shape`` proves this precedes stage 3
3. the walk's semantics against the model: known operation, exact parameter
   set, per-value primitive type -- ``order-shape-before-gate`` proves this
   precedes stage 4
4. the frame-coverage gate -- ``order-gate-before-evaluation`` proves this
   precedes any evaluation at all

The identity semantics of values is NOT decided here. ``patterns.py`` is handed
a callable and this module owns the single import of the checker's private one,
so exactly one identity exists in the process (spec D1).
"""

from __future__ import annotations

import copy
import datetime as _datetime
import json
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator
from pydantic import BaseModel, Field, model_serializer, model_validator

from gnd import artifacts, patterns, transition_kernel

# D1: THE single import of the checker's private helpers, in this module and
# nowhere else. `patterns.py` is handed `_identity_key` as a callable instead of
# importing it, so its stdlib-only isolation is literally true while exactly one
# identity semantics exists in the process. A behaviour test over these three
# names ships with the phase, so a rename in checker.py fails loudly here rather
# than silently changing what "the same fact" means.
from gnd.checker import (
    CheckReport,
    Verdict,
    _descendant_closure,
    _identity_key,
    _partial_compatible,
    _Wildcard,
    check,
    derivation_claims_against,
    structured_extension_view,
)
from gnd.checker import band as checker_band
from gnd.model import (
    Model,
    ValidationIssue,
    derivation_classifications,
    dynamic_subject_is_functional,
)
from gnd.population import Population, _model_digest, load_population_bytes
from gnd.popvalidate import resolve_primitive
from gnd.semantic_registry import UnregisteredBranchError, branch, record_branch

#: The untrusted-input posture population.py already takes, applied to the one
#: other document a caller hands us. A cap bounds the DOCUMENT, never the
#: algorithm (design rule 2).
MAX_STEPS_BYTES = 10 * 1024 * 1024

_SCHEMA_PATH = Path(__file__).parent / "schema" / "steps.schema.json"

#: Non-JSON scalars the YAML loader can legitimately produce inside a model.
#: A date in a provenance note is not an error -- it is a date -- so the digest
#: canonicalizes it rather than raising, and refuses only what it cannot name.
_ISO_TYPES = (_datetime.datetime, _datetime.date, _datetime.time)


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


def _refuse(path: str, message: str, rule_id: str, supplied: dict[str, Any] | None = None):
    raise TransitionLoadError(
        [ValidationIssue(path=path, message=message, rule_id=rule_id)],
        supplied=supplied,
    )


# --------------------------------------------------------------------------- #
# Digests -- three of them, on three bases, and the reasons differ
# --------------------------------------------------------------------------- #


def _canonical(value: Any, path: str) -> Any:
    """Everything JSON can carry, unchanged; dates as ISO text; nothing else.

    Totality belongs to the function (design rule 1). ``json.dumps`` refuses the
    ``datetime.date`` the YAML loader returns for an unquoted ISO date, and a
    model carrying one in a provenance note VALIDATES AT EXIT 0 -- so the
    digest, which every steps.json is required to carry, would raise an
    uncaught TypeError on a legal model and no walk against it could be
    authored. Two consequences, both deliberate:

    * quoted and unquoted spellings of one date produce the SAME digest, so the
      value identifies operations up to scalar spelling, and re-quoting a
      comment does not invalidate existing steps files;
    * anything outside the closed set is REFUSED with a rule id rather than
      crashing. Every input gets an answer, including "no".
    """
    if isinstance(value, dict):
        for key in value:
            if not isinstance(key, str):
                _refuse(
                    path,
                    f"mapping key {key!r} is a {type(key).__name__}, not a string; "
                    f"quote it in the model. Coercing it would let two different "
                    f"sections hash identically",
                    "transition:operations-digest-unrepresentable",
                )
        return {str(k): _canonical(v, f"{path}.{k}") for k, v in value.items()}
    if isinstance(value, list):
        return [_canonical(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, bool) or value is None or isinstance(value, (str, int, float)):
        return value
    if isinstance(value, _ISO_TYPES):
        return value.isoformat()
    _refuse(
        path,
        f"value of type '{type(value).__name__}' cannot be represented in the "
        f"operations digest; quote it in the model or remove it",
        "transition:operations-digest-unrepresentable",
    )
    return None  # pragma: no cover - _refuse always raises


def operations_digest(operations: list[dict[str, Any]] | None) -> str:
    """The digest of exactly the ``operations`` section, as loaded.

    Separate from ``model_digest`` because that one deliberately EXCLUDES
    operations (A8): a model can be byte-identical in every other respect while
    its operations changed under a walk's feet. ``[]`` for a v1 document and for
    an absent or empty section, so all three share one value.

    Canonical JSON rather than ``repr``: this value crosses a process boundary
    and an external client must be able to reproduce it, which Python's quote
    style, bool spelling and float formatting would prevent. The canonical form
    itself is ``artifacts.canonical_json_text`` -- the same one every recorded
    ``*_sha256`` in this repository is taken over -- rather than a second
    ``json.dumps`` call with the same four keyword arguments and no guarantee
    they stay the same four.
    """
    payload = artifacts.canonical_json_text(_canonical(operations or [], "$.operations"))
    return "sha256:" + artifacts.sha256_hex(payload.encode("utf-8"))


def model_digest(model: Model) -> str:
    """The same function ``population.py`` uses, called from a second place.

    Not a second digest that happens to share a word: identical bytes, so a
    population and a walk agree by construction about what "this model" means.
    """
    return "sha256:" + _model_digest(model)


def population_file_digest(path: str | Path) -> str:
    """sha256 over the population FILE BYTES as read.

    Provenance, not equivalence -- the question ``pre_digest`` answers is "is
    this the artifact the walk was authored against", and for that question
    "you reformatted the file" is a legitimate no. Reproducible with
    ``sha256sum`` by a client that has never seen this code, which the private
    ``repr``-based content digest is not.
    """
    return "sha256:" + artifacts.sha256_hex(Path(path).read_bytes())


# --------------------------------------------------------------------------- #
# The walk document
# --------------------------------------------------------------------------- #


def _refuse_json_constant(token: str) -> Any:
    raise ValueError(f"{token} is not valid JSON")


def _load_schema() -> dict[str, Any]:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _json_pointer(error: Any) -> str:
    """An error's location as `$.steps[2].bindings.expense`, not a deque."""
    out = "$"
    for part in error.absolute_path:
        out += f"[{part}]" if isinstance(part, int) else f".{part}"
    return out


def read_steps_document(path: str | Path) -> dict[str, Any]:
    """Read and layer-1 validate a walk. TOTAL over arbitrary bytes.

    The caller supplies these bytes and no layer 1 has run over them anywhere
    else in the process, so every malformed shape -- a top-level array, a string
    where an object belongs, wrong types at every level -- must produce a
    refusal rather than a TypeError from deep inside the evaluator.
    """
    source = Path(path)
    try:
        # ONE byte past the cap, so the cap bounds what is READ rather than
        # reporting on what was already read. The reviewed version called
        # read_bytes() first, which is not a cap -- an unbounded file or a FIFO
        # is fully consumed before the check can fire.
        with source.open("rb") as handle:
            raw = handle.read(MAX_STEPS_BYTES + 1)
    except OSError as error:
        _refuse(str(source), f"steps file could not be read: {error}", "transition:steps-shape")
    if len(raw) > MAX_STEPS_BYTES:
        _refuse(
            str(source),
            f"steps file is over the {MAX_STEPS_BYTES}-byte cap for untrusted input",
            "transition:steps-too-large",
        )
    try:
        document = json.loads(
            raw.decode("utf-8"),
            # NaN and Infinity are not JSON. Python writes and reads them by
            # default, so a walk could carry a value no other parser accepts and
            # no comparison behaves sanely over.
            parse_constant=_refuse_json_constant,
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        # ValueError, not JSONDecodeError: the integer-digit limit raises the
        # base class, and a caller-supplied 5000-digit number is exactly the
        # sort of input this loader exists to refuse rather than crash on.
        _refuse(str(source), f"steps file is not valid JSON: {error}", "transition:steps-shape")

    return _validate_steps_shape(document)


def validate_steps_document(document: Mapping[str, Any]) -> dict[str, Any]:
    """Copy and validate an already-loaded steps document through layer 1."""
    try:
        copied = copy.deepcopy(dict(document))
        json.dumps(copied, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as error:
        _refuse("$", f"steps document is not valid JSON: {error}", "transition:steps-shape")
    return _validate_steps_shape(copied)


def _validate_steps_shape(document: Any) -> dict[str, Any]:
    validator = Draft202012Validator(_load_schema())
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    if errors:
        raise TransitionLoadError(
            [
                ValidationIssue(
                    path=_json_pointer(error),
                    message=error.message,
                    rule_id="transition:steps-shape",
                )
                for error in errors
            ],
            supplied=_supplied_digests(document),
        )
    return document


def _supplied_digests(document: Any) -> dict[str, Any]:
    """The three digests as the caller wrote them, or nulls.

    Deliberately tolerant of a document that failed validation: a refused walk
    still gets a payload, and "the digests you sent" is exactly the field a
    caller needs to see when told one of them is wrong.
    """
    if not isinstance(document, dict):
        return {"model_digest": None, "operations_digest": None, "pre_digest": None}
    return {
        key: document.get(key) if isinstance(document.get(key), str) else None
        for key in ("model_digest", "operations_digest", "pre_digest")
    }


def verify_digests(document: dict[str, Any], model: Model, pre_path: str | Path | None) -> None:
    """Stage 2. Each mismatch has its own rule id, so a caller is never left
    guessing WHICH claim about the world stopped being true."""
    supplied = _supplied_digests(document)
    expected_model = model_digest(model)
    if supplied["model_digest"] != expected_model:
        _refuse(
            "$.model_digest",
            f"model_digest does not match this model: steps say "
            f"{supplied['model_digest']}, model is {expected_model}",
            "transition:model-digest-mismatch",
            supplied,
        )
    expected_ops = operations_digest(model.operations)
    if supplied["operations_digest"] != expected_ops:
        _refuse(
            "$.operations_digest",
            f"operations_digest does not match this model's operations: steps say "
            f"{supplied['operations_digest']}, model is {expected_ops}. model_digest "
            f"excludes operations, so it cannot carry this claim",
            "transition:operations-digest-mismatch",
            supplied,
        )
    if supplied["pre_digest"] is not None:
        if pre_path is None:
            _refuse(
                "$.pre_digest",
                "pre_digest cannot be verified for an already-loaded pre-population",
                "transition:pre-digest-unverifiable",
                supplied,
            )
        expected_pre = population_file_digest(pre_path)
        if supplied["pre_digest"] != expected_pre:
            _refuse(
                "$.pre_digest",
                f"pre_digest does not match the supplied pre-population: steps say "
                f"{supplied['pre_digest']}, file is {expected_pre}",
                "transition:pre-digest-mismatch",
                supplied,
            )


# --------------------------------------------------------------------------- #
# The walk against the model
# --------------------------------------------------------------------------- #


def _operations_by_id(model: Model) -> dict[str, dict[str, Any]]:
    return {str(op.get("id")): op for op in model.operations}


def operation_binding_issues(
    model: Model,
    *,
    declared: Mapping[str, dict[str, Any]],
    operation_id: str,
    bindings: Mapping[str, Any],
    operation_path: str,
    bindings_path: str,
    subject: str,
    require_exact: bool,
) -> list[ValidationIssue]:
    """Validate one operation plus either exact bindings or a binding subset.

    Transition steps require the complete declared parameter set.  Session
    walk floors use the same operation and primitive-type rules, but may name
    only the parameters relevant to the floor.  Keeping both callers here
    prevents the declaration layer from growing a second model type system.
    """
    from gnd.popvalidate import _PRIMITIVE_PREDICATES

    operation = declared.get(operation_id)
    if operation is None:
        return [
            ValidationIssue(
                path=operation_path,
                message=(
                    f"{subject} names operation '{operation_id}', which this model does not declare"
                ),
                rule_id="transition:unknown-operation",
            )
        ]

    parameters = {
        str(parameter.get("name")): str(parameter.get("object_type"))
        for parameter in operation.get("parameters") or []
    }
    missing = sorted(set(parameters) - set(bindings)) if require_exact else []
    extra = sorted(set(bindings) - set(parameters))
    if missing or extra:
        return [
            ValidationIssue(
                path=bindings_path,
                message=(
                    f"{subject} binds {sorted(bindings)} for operation '{operation_id}', "
                    f"which declares {sorted(parameters)}"
                    + (f"; missing {missing}" if missing else "")
                    + (f"; unexpected {extra}" if extra else "")
                ),
                rule_id="transition:bindings-mismatch",
            )
        ]

    issues: list[ValidationIssue] = []
    for name in sorted(bindings):
        primitive = resolve_primitive(parameters[name], model)
        predicate = _PRIMITIVE_PREDICATES.get(str(primitive))
        if primitive is None or predicate is None:
            continue
        value = bindings[name]
        if not predicate(value):
            issues.append(
                ValidationIssue(
                    path=f"{bindings_path}.{name}",
                    message=(
                        f"{subject} binds {value!r} to parameter '{name}' of "
                        f"'{operation_id}', declared '{parameters[name]}' whose values "
                        f"are {primitive}"
                    ),
                    rule_id="transition:binding-type",
                )
            )
    return issues


def validate_steps(document: dict[str, Any], model: Model) -> list[dict[str, Any]]:
    """Stage 3. Every step names a declared operation and binds exactly its
    declared parameters, each value of the parameter's own primitive.

    ONE type discipline: the predicate table is ``popvalidate``'s, the same one
    that decides whether a value may sit in a population, so a walk cannot bind
    a value the checker would refuse in the data. Its honest failure mode comes
    along too -- when an object type's primitive is genuinely unresolvable, the
    check is SKIPPED SILENTLY rather than invented.
    """
    supplied = _supplied_digests(document)
    declared = _operations_by_id(model)
    issues: list[ValidationIssue] = []
    steps = document["steps"]
    for index, step in enumerate(steps, start=1):
        op_id = str(step["op"])
        issues.extend(
            operation_binding_issues(
                model,
                declared=declared,
                operation_id=op_id,
                bindings=step["bindings"],
                operation_path=f"$.steps[{index}].op",
                bindings_path=f"$.steps[{index}].bindings",
                subject=f"step {index}",
                require_exact=True,
            )
        )
    if issues:
        raise TransitionLoadError(issues, supplied=supplied)
    return list(steps)


def touched_fact_types(model: Model, steps: list[dict[str, Any]]) -> set[str]:
    """Every fact type any step's operation asserts into or retracts from.

    A ``create`` contributes NOTHING: it names an object type and a parameter and
    no fact type at all. The consequence is stated rather than hidden -- an
    instance created and never used in an asserted fact is invisible to the
    frame check, since per-fact-type grading has no way to express an undeclared
    instance. Every create in a well-formed operation reaches this union through
    the assert that uses it.
    """
    declared = _operations_by_id(model)
    union: set[str] = set()
    for step in steps:
        operation = declared.get(str(step["op"]))
        for effect in (operation or {}).get("effects") or []:
            for verb in ("assert", "retract"):
                atom = effect.get(verb) if isinstance(effect, dict) else None
                if isinstance(atom, dict) and atom.get("fact_type"):
                    union.add(str(atom["fact_type"]))
    return union


def assert_frame_coverage(
    union: set[str],
    populations: dict[str, Population],
    supplied: dict[str, Any] | None = None,
) -> None:
    """Stage 4. A population whose declared coverage omits a touched fact type
    is REFUSED, never silently degraded.

    The frame check asks whether the declared post differs from what the
    operations produce. Over a fact type the population does not claim
    completeness for, "it differs" and "you did not tell me about it" are
    indistinguishable, and answering anyway is how an incomplete cover used to
    produce a partial green.
    """
    for label, population in populations.items():
        covered = set(population.covers or [])
        gaps = sorted(union - covered)
        if gaps:
            _refuse(
                f"$.{label}.covers",
                f"the {label}-population does not cover {gaps}, which this walk's "
                f"operations touch; a frame comparison over a fact type the "
                f"population does not claim completeness for cannot be sound",
                "transition:frame-coverage",
                supplied,
            )


def assert_static_derivation_coverage(
    model: Model,
    steps: list[dict[str, Any]],
    populations: dict[str, Population],
    supplied: dict[str, Any] | None = None,
) -> None:
    """Require complete asserted inputs for static derivations used by the walk."""
    declared = _operations_by_id(model)
    read_fact_types: set[str] = set()

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            fact_type = value.get("fact_type")
            if isinstance(fact_type, str):
                read_fact_types.add(fact_type)
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    for step in steps:
        operation = declared.get(str(step.get("op")))
        if operation is not None:
            collect(operation.get("preconditions") or [])

    required: set[str] = set()
    consumers: dict[str, set[str]] = {}
    for classification in derivation_classifications(model.model_dump()):
        if classification.stability == "static" and classification.fact_type in read_fact_types:
            required.update(classification.asserted_dependencies)
            for dependency in classification.asserted_dependencies:
                consumers.setdefault(dependency, set()).add(classification.fact_type)

    for label, population in populations.items():
        gaps = sorted(required - set(population.covers or []))
        if gaps:
            affected = sorted(
                {fact_type for dependency in gaps for fact_type in consumers.get(dependency, set())}
            )
            _refuse(
                f"$.{label}.covers",
                f"the {label}-population does not cover {gaps}, which are asserted "
                f"dependencies of static derivation(s) {affected} read by this walk",
                "transition:static-derivation-coverage",
                supplied,
            )


def assert_dynamic_derivation_coverage(
    model: Model,
    steps: list[dict[str, Any]],
    populations: dict[str, Population],
    supplied: dict[str, Any] | None = None,
) -> None:
    """Require selected/read dynamic heads and every transitive asserted leaf."""
    declared = _operations_by_id(model)
    classifications = {
        row.fact_type: row
        for row in derivation_classifications(model.model_dump())
        if row.stability == "dynamic"
    }
    selected: set[str] = set()

    def collect_reads(value: Any) -> None:
        if isinstance(value, dict):
            fact_type = value.get("fact_type")
            if isinstance(fact_type, str) and fact_type in classifications:
                selected.add(fact_type)
            for child in value.values():
                collect_reads(child)
        elif isinstance(value, list):
            for child in value:
                collect_reads(child)

    for step in steps:
        operation = declared[str(step["op"])]
        selected.update(_dynamic_heads_for_step(model, operation))
        collect_reads(operation.get("preconditions") or [])
        collect_reads(operation.get("dynamic_rules") or [])
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        if fact_type_id in classifications and fact_type.get("constraints"):
            selected.add(fact_type_id)
        collect_reads(fact_type.get("constraints") or [])
    collect_reads(model.constraints)

    required_by_head = {
        head: {head, *classifications[head].asserted_dependencies} for head in selected
    }
    for label, population in populations.items():
        covered = set(population.covers or [])
        for head in sorted(required_by_head):
            if label == "post" and head not in covered:
                continue
            gaps = sorted(required_by_head[head] - covered)
            if not gaps:
                continue
            _refuse(
                f"$.{label}.covers",
                f"the {label}-population omits {gaps} required for dynamic "
                f"derivation '{head}'; selected/read heads and their complete "
                "asserted dependency closure must be covered",
                "transition:dynamic-derivation-coverage",
                supplied,
            )


# --------------------------------------------------------------------------- #
# The report -- four families, deliberately unmerged
# --------------------------------------------------------------------------- #


class TransitionVerdict(BaseModel):
    """One finding about one walk.

    Two iff invariants are ENFORCED here rather than described, because a prose
    rule a type does not enforce is a rule that is not enforced.
    """

    scope_id: str = Field(exclude=True)
    family: Literal["pre_snapshot", "step", "frame", "post_snapshot"]
    locator: str
    kind: Literal[
        "precondition",
        "create-freshness",
        "retract-target",
        "assert-redundant",
        "dynamic-rule",
        "compiled-subset",
        "frame-delta",
        "intermediate-unloadable",
    ]
    modality: str
    verdict: Verdict
    message: str
    reason_code: str | None = None
    offending_facts: list[Any] = Field(default_factory=list)
    #: Frame-only: which direction the undeclared delta went.
    direction: Literal["undeclared-assert", "undeclared-retract"] | None = None
    #: The fact type this finding is ABOUT, where it is about exactly one.
    #: Null for create-freshness (which concerns an object type) and for
    #: intermediate-unloadable (which concerns the whole state).
    fact_type: str | None = None
    #: The precondition or dynamic-rule id the finding came from. Parsing it
    #: back out of `locator` would be inventing an encoding.
    obligation: str | None = None
    #: The offending bound value, for create-freshness: the identifier a step
    #: minted twice. `offending_facts` cannot carry it -- when freshness fails
    #: there is no fact to point at yet.
    value: Any | None = None

    @model_validator(mode="after")
    def _iff_invariants(self) -> TransitionVerdict:
        if (self.reason_code is not None) != (self.verdict == "unchecked"):
            raise ValueError(
                "reason_code is non-null if and only if verdict == 'unchecked' "
                f"(verdict={self.verdict!r}, reason_code={self.reason_code!r})"
            )
        if (self.direction is not None) != (self.family == "frame"):
            raise ValueError(
                "direction is non-null if and only if family == 'frame' "
                f"(family={self.family!r}, direction={self.direction!r})"
            )
        row = branch(self.scope_id)
        if (row.surface, row.family) != ("transition", self.kind):
            raise UnregisteredBranchError("transition branch names another finding kind")
        if row.modality != "any" and row.modality != self.modality:
            raise UnregisteredBranchError("transition branch names another modality")
        if row.reason_code != self.reason_code:
            raise UnregisteredBranchError("transition reason disagrees with its branch")
        if self.kind == "frame-delta" and row.variant != self.direction:
            raise UnregisteredBranchError("transition branch names another frame direction")
        record_branch(self.scope_id, outcome=self.verdict)
        return self


class DerivedChange(BaseModel):
    """One changed computed extension, observational and never banded."""

    fact_type: str
    added: list[dict[str, Any]] = Field(default_factory=list)
    removed: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def _nonempty_delta(self) -> DerivedChange:
        if not self.added and not self.removed:
            raise ValueError("a derived change must add or remove at least one row")
        return self


class StepResult(BaseModel):
    """One step: what it was asked to do, what was found, and the state after."""

    index: int
    operation: str
    bindings: dict[str, Any]
    verdicts: list[TransitionVerdict] = Field(default_factory=list)
    derived_changes: list[DerivedChange] = Field(
        default_factory=list,
        exclude_if=lambda rows: not rows,
    )
    #: The ordinary constraint check over S(i). Empty when S(i) could not be
    #: re-loaded, which its own `intermediate-unloadable` verdict records.
    intermediate: CheckReport = Field(default_factory=CheckReport)


class FrameGrading(BaseModel):
    """How one touched fact type is graded, and by whose declaration."""

    fact_type: str
    modality: str
    reason: Literal["all-alethic", "deontic-toucher"]
    operations: list[str] = Field(default_factory=list)


class TransitionReport(BaseModel):
    """Four claim families, never merged into an aggregate.

    There is no `passed` field and no summary verdict, deliberately: a walk can
    be clean in three families and broken in the fourth, and a single boolean is
    the shape that loses exactly that.
    """

    pre_snapshot: CheckReport = Field(default_factory=CheckReport)
    pre_snapshot_verdicts: list[TransitionVerdict] = Field(default_factory=list)
    steps: list[StepResult] = Field(default_factory=list)
    frame_grading: list[FrameGrading] = Field(default_factory=list)
    frame_verdicts: list[TransitionVerdict] = Field(default_factory=list)
    post_snapshot: CheckReport = Field(default_factory=CheckReport)

    @model_serializer(mode="wrap")
    def _serialize_with_derivation_claims(self, handler):
        """Transition snapshots expose their structured-claim obligations."""
        dumped = handler(self)
        structured = any(
            report.derivations
            for report in (
                self.pre_snapshot,
                self.post_snapshot,
                *(step.intermediate for step in self.steps),
            )
        )
        if not structured:
            return dumped

        def add(report: CheckReport, target: dict[str, Any]) -> None:
            target["derivations"] = [row.model_dump(mode="json") for row in report.derivations]

        add(self.pre_snapshot, dumped["pre_snapshot"])
        add(self.post_snapshot, dumped["post_snapshot"])
        for step, target in zip(self.steps, dumped["steps"], strict=True):
            add(step.intermediate, target["intermediate"])
        return dumped

    def all_verdicts(self) -> list[TransitionVerdict]:
        return [
            *self.pre_snapshot_verdicts,
            *[v for step in self.steps for v in step.verdicts],
            *self.frame_verdicts,
        ]

    def embedded_reports(self) -> list[CheckReport]:
        return [self.pre_snapshot, *[s.intermediate for s in self.steps], self.post_snapshot]


@dataclass(frozen=True, slots=True)
class ComputedTransition:
    """A transition report paired with the final population it computed."""

    report: TransitionReport
    post: Population | None
    computed_post: dict[str, Any]


def band(report: TransitionReport) -> int:
    """Verdicts -> exit band, precedence 1 > 4 > 2 > 0, jointly over all four families.

    3 is deliberately absent. Every load, digest and gate rejection raises
    `TransitionLoadError` before a report exists, so a branch for it here would
    be a branch no case could exercise -- and this phase's whole premise is that
    a declared branch nothing can reach is a defect.

    The embedded CheckReports are graded by `checker.band`, not re-derived: one
    owner for the snapshot rule, and this function combines rather than
    duplicates.
    """
    verdicts = report.all_verdicts()
    bands = {checker_band(embedded) for embedded in report.embedded_reports()}
    result = transition_kernel.transition_band(
        any(v.verdict == "fail" for v in verdicts) or 1 in bands,
        any(v.verdict == "unchecked" and v.modality == "alethic" for v in verdicts) or 4 in bands,
        any(v.verdict == "vacuous" for v in verdicts) or 2 in bands,
    )
    if result == 1:
        record_branch("composition:band:transition:fail")
        return 1
    if result == 4:
        record_branch("composition:band:transition:unchecked")
        return 4
    if result == 2:
        record_branch("composition:band:transition:vacuous")
        return 2
    record_branch("composition:band:transition:clean")
    return 0


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #

#: A state between steps: fact type id -> list of ground facts.
State = dict[str, list[dict[str, Any]]]


class UnknownComparisonError(ValueError):
    """A dynamic rule named an operator the evaluator does not implement.

    Unreachable through a loaded model -- layer 1 restricts `op` to the
    meta-schema's enum -- and deliberately LOUD rather than quiet. The reviewed
    version folded this case into the violated-comparison branch, so a rule
    written with the schema's own spelling of equality reported a FAILURE on
    every walk that satisfied it: a missing implementation wearing the costume
    of a finding about someone's data.
    """


#: One entry per operator in `$defs.dynamic_rule.properties.op`, and a test
#: asserts the two sets agree. `=` is the schema's spelling of equality; `==`
#: was this map's, which is exactly how the two drifted apart.
_COMPARISONS: dict[str, Any] = {
    ">": lambda new, old: new > old,
    ">=": lambda new, old: new >= old,
    "<": lambda new, old: new < old,
    "<=": lambda new, old: new <= old,
    "!=": lambda new, old: new != old,
    "=": lambda new, old: new == old,
}


def _compare_values(op: str, new: Any, old: Any) -> bool:
    compare = _COMPARISONS.get(op)
    if compare is None:
        raise UnknownComparisonError(
            f"dynamic rule operator {op!r} is not implemented; the meta-schema "
            f"admits {sorted(_COMPARISONS)}"
        )
    result = bool(compare(new, old))
    if (
        isinstance(new, int)
        and not isinstance(new, bool)
        and isinstance(old, int)
        and not isinstance(old, bool)
    ):
        kernel_result = transition_kernel.comparison_dispatch(op, new, old)
        if result != kernel_result:
            raise AssertionError("transition comparison kernel disagrees with admitted values")
    return result


_MISSING = object()


def _fact_key(fact: dict[str, Any]) -> tuple[Any, ...]:
    """Identity of a ground fact: its role map under the checker's own key.

    Sets, never multisets: a population carrying one ground fact twice
    contributes one member, so a duplicate-count difference is not a frame
    delta. Sorting by role name makes the key order-independent.
    """
    return tuple(sorted((role, _identity_key(value)) for role, value in fact.items()))


def _verdict_for(modality: str) -> Verdict:
    """THE modality-to-verdict rule, for every class that grades from a declared
    modality. Alethic obligations fail; deontic ones warn."""
    return transition_kernel.modality_verdict(modality == "alethic")  # type: ignore[return-value]


def _state_of(population: Population) -> State:
    return {
        fact_type: [dict(fact) for fact in facts]
        for fact_type, facts in (population.facts or {}).items()
    }


def _effective_static_state(
    model: Model,
    asserted: State,
    extensions: Mapping[str, tuple[Mapping[str, Any], ...]],
) -> State:
    """Overlay checker-computed static extensions for one evaluation step."""
    effective = copy.deepcopy(asserted)
    static_ids = {
        row.fact_type
        for row in derivation_classifications(model.model_dump())
        if row.stability == "static"
    }
    if not static_ids:
        return effective
    for fact_type_id in static_ids:
        effective[fact_type_id] = [dict(fact) for fact in extensions.get(fact_type_id, ())]
    record_branch("composition:derivation-view:static:applied")
    return effective


def _restore_asserted_state(model: Model, before: State, evaluated: State) -> State:
    """Discard the internal extension overlay while preserving ordinary effects."""
    restored = copy.deepcopy(evaluated)
    classifications = derivation_classifications(model.model_dump())
    for row in classifications:
        fact_type_id = row.fact_type
        if row.derivation == "semiderived" and fact_type_id in before:
            restored[fact_type_id] = copy.deepcopy(before[fact_type_id])
        else:
            restored.pop(fact_type_id, None)
    return restored


def _touched_by(operation: dict[str, Any]) -> set[str]:
    touched: set[str] = set()
    for effect in operation.get("effects") or []:
        asserted = effect.get("assert") if isinstance(effect, dict) else None
        retracted = effect.get("retract") if isinstance(effect, dict) else None
        if transition_kernel.fact_type_touched(
            isinstance(asserted, dict), isinstance(retracted, dict)
        ):
            atom = asserted if isinstance(asserted, dict) else retracted
            if isinstance(atom, dict) and atom.get("fact_type"):
                touched.add(str(atom["fact_type"]))
    return touched


def _instance_keys(object_type_id: str, model: Model, state: State) -> set[Any]:
    """Identity keys of every instance of an object type present in a STATE.

    The role-to-object-type mapping and the subtype closure come from the
    checker's own helpers, so "what counts as an instance" has one owner; only
    the source of the facts differs. `_instances_of` needs a validated
    Population, and an intermediate state that failed to re-load is not one --
    but the walk continues over it, and a freshness check that goes quiet
    exactly when the state got hard to validate is a check that stops working
    when it matters.
    """
    wanted = _descendant_closure(object_type_id, model)
    keys: set[Any] = set()
    for fact_type in model.fact_types:
        roles = [
            str(role.get("role_name"))
            for role in fact_type.get("roles") or []
            if str(role.get("object_type")) in wanted
        ]
        if not roles:
            continue
        for fact in state.get(str(fact_type.get("id")), []):
            for role in roles:
                if role in fact:
                    keys.add(_identity_key(fact[role]))
    return keys


def _subject_value(subject: dict[str, Any], state: State, bindings: dict[str, Any]) -> Any:
    """The subject's current value, or ``_MISSING`` when it has none."""
    fact_type_id, roles = patterns.ground_atom(subject, bindings)
    value_role = str(subject.get("value_role"))
    for fact in state.get(fact_type_id, []):
        if patterns.matches(fact, roles, identity=_identity_key) and value_role in fact:
            return fact[value_role]
    return _MISSING


def _evaluate_step(
    index: int,
    step: dict[str, Any],
    operation: dict[str, Any],
    model: Model,
    state: State,
    population: Population | None,
) -> tuple[StepResult, State]:
    """One step: judge it against S(i-1), then produce S(i).

    NO STEP ABORTS. A failed precondition is reported and the effects still
    apply, so one pass reports every finding the walk contains and the computed
    final state corresponds to the trace as logged. The cost is stated rather
    than hidden: the computed state can contain a fact a precondition declared
    unreachable, so one report can describe an impossible world. That is
    coherent for an audit -- `gnd check` reads a log, it does not execute a
    program and has nothing to roll back.
    """
    bindings = dict(step["bindings"])
    op_id = str(operation.get("id"))
    verdicts: list[TransitionVerdict] = []

    def add(**kwargs: Any) -> None:
        verdicts.append(TransitionVerdict(family="step", **kwargs))

    # --- preconditions, against S(i-1) ------------------------------------
    for obligation in operation.get("preconditions") or []:
        modality = str(obligation.get("modality", ""))
        for atom in obligation.get("require") or []:
            fact_type_id, _ = patterns.ground_atom(atom, bindings)
            holds = patterns.holds(
                atom, state.get(fact_type_id, []), bindings, identity=_identity_key
            )
            decision = transition_kernel.precondition_verdict(holds, modality == "alethic")
            if decision == "pass":
                continue
            add(
                locator=f"$.steps[{index}].preconditions[id={obligation.get('id')}]",
                kind="precondition",
                modality=modality,
                verdict=decision,  # type: ignore[arg-type]
                fact_type=fact_type_id,
                obligation=str(obligation.get("id")),
                message=(
                    f"step {index} ({op_id}) requires {fact_type_id} to hold for "
                    f"{patterns.ground_atom(atom, bindings)[1]}, and it does not"
                ),
                scope_id=f"transition:precondition:n-a:violated:{modality}",
            )
            break  # one verdict per obligation: the conjunction failed, once
        else:
            record_branch("transition:precondition:n-a:clean")

    # --- create freshness, over S(i-1) UNION this step's own creates -------
    minted: dict[str, set[Any]] = {}
    for position, effect in enumerate(operation.get("effects") or []):
        create = effect.get("create") if isinstance(effect, dict) else None
        if not isinstance(create, dict):
            continue
        param = str(create.get("param"))
        object_type = str(create.get("object_type"))
        value = bindings.get(param)
        key = _identity_key(value)
        # From the STATE, which always exists -- not from a Population, which
        # does not when the previous intermediate could not be re-loaded. The
        # reviewed version treated an absent Population as "nothing exists", so
        # a re-minted identifier after a large intermediate reported only band 4
        # and lost the band-1 collision entirely.
        existing = key in _instance_keys(object_type, model, state)
        created_earlier = key in minted.get(object_type, set())
        freshness = transition_kernel.freshness_verdict(existing, created_earlier)
        if freshness != "pass":
            add(
                locator=f"$.steps[{index}].effects[{position}].create",
                kind="create-freshness",
                # Fixed alethic: a re-minted identifier makes the walk's own
                # bindings incoherent, which no frame modality should excuse.
                modality="alethic",
                verdict="fail",
                value=value,
                message=(
                    f"step {index} ({op_id}) creates '{object_type}' as {value!r}, which "
                    + (
                        "already denotes an instance"
                        if existing
                        else "another create in the same step also mints"
                    )
                ),
                scope_id="transition:create-freshness:"
                + ("preexisting" if existing else "same-step")
                + ":violated:alethic",
            )
        else:
            record_branch("transition:create-freshness:n-a:clean")
        minted.setdefault(object_type, set()).add(key)

    # --- apply the effect set (r3 section 1's transition equation) ---------
    # Written order is NOT semantic. Every retract selector evaluates against
    # S(i-1), all retracts apply before all asserts, so a fact both retracted
    # and asserted in one step is PRESENT in S(i) -- which is what makes
    # retract+assert a replace and why no `replace` primitive exists.
    after: State = {fact_type: list(facts) for fact_type, facts in state.items()}
    doomed: dict[str, set[int]] = {}
    for position, effect in enumerate(operation.get("effects") or []):
        atom = effect.get("retract") if isinstance(effect, dict) else None
        if not isinstance(atom, dict):
            continue
        fact_type_id, roles = patterns.ground_atom(atom, bindings)
        hits = patterns.select(atom, state.get(fact_type_id, []), bindings, identity=_identity_key)
        target_verdict = transition_kernel.retract_target_verdict(bool(hits))
        if target_verdict != "pass":
            add(
                locator=f"$.steps[{index}].effects[{position}].retract",
                kind="retract-target",
                # D2, closed strict by the owner: the language already lets an
                # operation REQUIRE its target with an explicit precondition, so
                # deleting without checking is a claim the target exists.
                modality="alethic",
                verdict=target_verdict,  # type: ignore[arg-type]
                fact_type=fact_type_id,
                message=(
                    f"step {index} ({op_id}) retracts {fact_type_id} matching {roles}, "
                    f"and no fact matches"
                ),
                scope_id="transition:retract-target:n-a:violated:alethic",
            )
        else:
            record_branch("transition:retract-target:n-a:clean")
        doomed.setdefault(fact_type_id, set()).update(hits)
    for fact_type_id, indices in doomed.items():
        after[fact_type_id] = [
            fact
            for position, fact in enumerate(after.get(fact_type_id, []))
            if position not in indices
        ]
    replacement_slots = {fact_type_id: sorted(indices) for fact_type_id, indices in doomed.items()}
    for position, effect in enumerate(operation.get("effects") or []):
        atom = effect.get("assert") if isinstance(effect, dict) else None
        if not isinstance(atom, dict):
            continue
        fact_type_id, roles = patterns.ground_atom(atom, bindings)
        was_present = patterns.holds(
            atom, state.get(fact_type_id, []), bindings, identity=_identity_key
        )
        redundant_verdict = transition_kernel.assert_redundant_verdict(was_present)
        if redundant_verdict != "pass":
            add(
                locator=f"$.steps[{index}].effects[{position}].assert",
                kind="assert-redundant",
                # Deliberately NOT the mirror of retract-target. A retract
                # matching nothing means the state contradicts the walk; a
                # redundant assert means the state confirms it, and the
                # post-state is exactly what the operation intended.
                modality="deontic",
                verdict=redundant_verdict,  # type: ignore[arg-type]
                fact_type=fact_type_id,
                message=(
                    f"step {index} ({op_id}) asserts {fact_type_id} {roles}, which is "
                    f"already present"
                ),
                scope_id="transition:assert-redundant:n-a:violated:deontic",
            )
        else:
            record_branch("transition:assert-redundant:n-a:clean")
        present = {_fact_key(fact) for fact in after.get(fact_type_id, [])}
        if not transition_kernel.effect_membership(
            _fact_key(roles) in present, False, False
        ):  # duplicate asserts collapse
            facts = after.setdefault(fact_type_id, [])
            slots = replacement_slots.get(fact_type_id, [])
            if slots:
                facts.insert(min(slots.pop(0), len(facts)), dict(roles))
            else:
                facts.append(dict(roles))
            record_branch("transition:assert-effect:n-a:inserted")
        else:
            record_branch("transition:assert-effect:n-a:duplicate-collapsed")

    # --- dynamic rules, over (S(i-1), S(i)) --------------------------------
    touched = _touched_by(operation)
    for rule_index, rule in enumerate(operation.get("dynamic_rules") or []):
        subject = rule.get("subject")
        if not isinstance(subject, dict):
            continue
        subject_type = str(subject.get("fact_type"))
        modality = str(rule.get("modality", ""))
        # THE GATE (ledger 14): a dynamic rule judges only transitions its own
        # operation makes. If no effect touches the subject, there is no
        # transition to judge and no verdict is produced -- the author is told
        # at load time instead, by semantic:op-dynamic-untouched.
        is_touched = subject_type in touched
        functional = dynamic_subject_is_functional(subject, model.fact_types)
        if (
            transition_kernel.dynamic_verdict(
                is_touched, functional is not False, True, True, True, modality == "alethic"
            )
            == "pass"
            and not is_touched
        ):
            record_branch("transition:dynamic-rule:n-a:untouched")
            continue
        locator = f"$.steps[{index}].dynamic_rules[{rule_index}]"
        common = {
            "locator": locator,
            "kind": "dynamic-rule",
            "modality": modality,
            "fact_type": subject_type,
            "obligation": str(rule.get("id")),
        }
        if (
            transition_kernel.dynamic_verdict(
                True, functional is not False, True, True, True, modality == "alethic"
            )
            == "unchecked"
        ):
            add(
                **common,
                verdict="unchecked",
                reason_code="transition:dynamic-subject-not-functional",
                message=(
                    f"step {index} ({op_id}) cannot compare old and new values of "
                    f"'{subject.get('value_role')}' on {subject_type}: no internal "
                    f"uniqueness constraint proves the subject functional"
                ),
                scope_id="transition:dynamic-rule:n-a:unchecked-nonfunctional",
            )
            continue
        old = _subject_value(subject, state, bindings)
        new = _subject_value(subject, after, bindings)
        old_present = old is not _MISSING
        new_present = new is not _MISSING
        if (
            transition_kernel.dynamic_verdict(
                True, True, old_present, new_present, True, modality == "alethic"
            )
            == "vacuous"
        ):
            add(
                **common,
                verdict="vacuous",
                message=(
                    f"step {index} ({op_id}): dynamic rule '{rule.get('id')}' has "
                    + (
                        "no old value to compare against"
                        if old is _MISSING
                        else "no new value -- the subject was removed"
                    )
                ),
                scope_id="transition:dynamic-rule:"
                + ("no-old" if old is _MISSING else "no-new")
                + ":vacuous",
            )
            continue
        comparison_holds = _compare_values(str(rule.get("op")), new, old)
        dynamic_decision = transition_kernel.dynamic_verdict(
            True, True, True, True, comparison_holds, modality == "alethic"
        )
        if dynamic_decision != "pass":
            add(
                **common,
                verdict=dynamic_decision,  # type: ignore[arg-type]
                offending_facts=[{"old": old, "new": new}],
                message=(
                    f"step {index} ({op_id}): dynamic rule '{rule.get('id')}' requires "
                    f"new {rule.get('op')} old, and {new!r} {rule.get('op')} {old!r} "
                    f"does not hold"
                ),
                scope_id=f"transition:dynamic-rule:comparison:violated:{modality}",
            )
        else:
            record_branch("transition:dynamic-rule:comparison:clean")

    return StepResult(index=index, operation=op_id, bindings=bindings, verdicts=verdicts), after


def _load_intermediate(
    state: State, model: Model, covers: list[str], index: int
) -> tuple[Population | None, TransitionVerdict | None]:
    """S(i) as a REAL, re-validated population -- or an honest refusal to grade it.

    Each intermediate state goes back through the public loader, which runs
    layer 2 and stamps the marker `checker.check` requires. No private stamping
    helper is called, so "there is no bypass" stays true rather than becoming a
    thing this module quietly does. `covers` is the pre-population's verbatim:
    the coverage gate already refused any pre-population not covering the
    touched union, so widening it here would be dead code.

    A state that cannot be re-loaded -- for ANY reason layer 2 gives, the 10 MB
    cap included -- is `unchecked` at band 4, never exit 3. Exit 3 means refused
    before evaluation began, and this is mid-walk. It is also the honest
    verdict: the state was not found illegal, it was not examined.
    """
    # `source` must be one of the three the population schema allows, and
    # "synthetic" is the accurate one: this state was GENERATED by applying an
    # effect set, not produced by an agent and not committed as a fixture. It
    # never leaves the process -- there is no file, and nothing downstream reads
    # the field -- but a synthesized document that could not itself load would
    # make every intermediate check report `unchecked` for a reason that has
    # nothing to do with the walk, which is exactly what a first draft did.
    document = {
        "population": {
            "model": "<intermediate state>",
            "source": "synthetic",
            "covers": covers,
        },
        "facts": state,
    }
    detail = "the transition kernel rejected the admitted state"
    try:
        payload = artifacts.canonical_json_bytes(document)
        population = load_population_bytes(
            payload, source=f"<intermediate state after step {index}>", model=model
        )
    except Exception as error:  # noqa: BLE001 - any refusal is one unchecked verdict
        population = None
        detail = str(error)
    if transition_kernel.intermediate_verdict(population is not None) != "pass":
        return None, TransitionVerdict(
            family="step",
            locator=f"$.steps[{index}].intermediate",
            kind="intermediate-unloadable",
            modality="alethic",
            verdict="unchecked",
            reason_code="transition:intermediate-state-unloadable",
            message=(
                f"the state after step {index} could not be re-loaded, so its "
                f"constraints were not checked: {detail}"
            ),
            scope_id="transition:intermediate-unloadable:n-a:unchecked",
        )
    record_branch("transition:intermediate-state:n-a:loaded")
    return population, None


_PHASE4_LEGACY_LOAD_INTERMEDIATE = _load_intermediate


def _load_intermediate_dispatch(
    state: State, model: Model, covers: list[str], index: int,
) -> tuple[Population | None, TransitionVerdict | None]:
    """Use the loader's v2 marker only when a generated state has opaque cells."""
    if not any(isinstance(value, dict) and set(value) == {"$opaque"}
               for rows in state.values() for row in rows for value in row.values()):
        return _PHASE4_LEGACY_LOAD_INTERMEDIATE(state, model, covers, index)
    document = {
        "format_version": 2,
        "population": {
            "model": "<intermediate state>", "model_id": model.model_id,
            "source": "synthetic", "covers": covers,
        },
        "facts": state,
    }
    detail = "the transition kernel rejected the admitted state"
    try:
        population = load_population_bytes(
            artifacts.canonical_json_bytes(document),
            source=f"<intermediate state after step {index}>", model=model,
        )
    except Exception as error:  # noqa: BLE001 - an intermediate refusal stays a verdict
        population = None
        detail = str(error)
    if transition_kernel.intermediate_verdict(population is not None) != "pass":
        return None, TransitionVerdict(
            family="step", locator=f"$.steps[{index}].intermediate",
            kind="intermediate-unloadable", modality="alethic", verdict="unchecked",
            reason_code="transition:intermediate-state-unloadable",
            message=(f"the state after step {index} could not be re-loaded, so its "
                     f"constraints were not checked: {detail}"),
            scope_id="transition:intermediate-unloadable:n-a:unchecked",
        )
    record_branch("transition:intermediate-state:n-a:loaded")
    return population, None


_load_intermediate = _load_intermediate_dispatch


def _frame_grading(model: Model, steps: list[dict[str, Any]]) -> list[FrameGrading]:
    """Per FACT TYPE, never per walk.

    A fact type touched only by alethic-framed operations grades alethic: an
    undeclared delta on it is a hard failure. One touched by ANY deontic-framed
    operation grades deontic, and the report names the operations responsible,
    so a reader can see whose declaration bought the leniency.

    Grading is TOTAL because `frame` is required on every operation by the
    meta-schema and never defaulted -- there is no un-graded touched fact type
    and therefore no default-modality branch to write.
    """
    declared = _operations_by_id(model)
    touchers: dict[str, list[str]] = {}
    modalities: dict[str, set[str]] = {}
    for step in steps:
        operation = declared.get(str(step["op"]))
        if operation is None:
            continue
        modality = str((operation.get("frame") or {}).get("modality", ""))
        for fact_type_id in _touched_by(operation):
            names = touchers.setdefault(fact_type_id, [])
            if operation["id"] not in names:
                names.append(str(operation["id"]))
            modalities.setdefault(fact_type_id, set()).add(modality)
    grading: list[FrameGrading] = []
    for fact_type_id in sorted(touchers):
        deontic = [
            op
            for op in touchers[fact_type_id]
            if str((declared[op].get("frame") or {}).get("modality", "")) == "deontic"
        ]
        selected_modality = transition_kernel.frame_modality(bool(deontic))
        grading.append(
            FrameGrading(
                fact_type=fact_type_id,
                modality=selected_modality,
                reason="deontic-toucher" if deontic else "all-alethic",
                operations=deontic or sorted(touchers[fact_type_id]),
            )
        )
    return grading


def _frame_verdicts(
    grading: list[FrameGrading], computed: State, declared_post: Population
) -> list[TransitionVerdict]:
    """Declared post versus computed final, per touched fact type, both directions.

    The comparison universe is the touched union ONLY, and that is a stated
    soundness limit rather than an oversight: the frame check answers "did the
    declared operations do anything they did not declare", not "did anything at
    all change". A delta on a fact type no operation in the walk names produces
    no verdict in either direction -- the post-snapshot check still catches it
    if it violates a constraint, as a constraint violation.
    """
    verdicts: list[TransitionVerdict] = []
    for entry in grading:
        expected = {_fact_key(fact): fact for fact in computed.get(entry.fact_type, [])}
        actual = {
            _fact_key(fact): fact for fact in (declared_post.facts or {}).get(entry.fact_type, [])
        }
        for direction, missing in (
            ("undeclared-assert", set(actual) - set(expected)),
            ("undeclared-retract", set(expected) - set(actual)),
        ):
            if direction == "undeclared-assert":
                decision = transition_kernel.frame_assert_verdict(
                    bool(missing), entry.modality == "alethic"
                )
            else:
                decision = transition_kernel.frame_retract_verdict(
                    bool(missing), entry.modality == "alethic"
                )
            if decision == "pass":
                record_branch(f"transition:frame-delta:{direction}:clean")
                continue
            facts = [
                (actual if direction == "undeclared-assert" else expected)[key]
                for key in sorted(missing, key=repr)
            ]
            verdicts.append(
                TransitionVerdict(
                    family="frame",
                    locator=f"$.post.facts.{entry.fact_type}",
                    kind="frame-delta",
                    modality=entry.modality,
                    verdict=decision,  # type: ignore[arg-type]
                    direction=direction,
                    fact_type=entry.fact_type,
                    offending_facts=facts,
                    message=(
                        f"the declared post-state {'contains' if direction == 'undeclared-assert' else 'is missing'} "
                        f"{len(facts)} {entry.fact_type} fact(s) that no operation in this "
                        f"walk {'asserts' if direction == 'undeclared-assert' else 'retracts'}"
                    ),
                    scope_id=f"transition:frame-delta:{direction}:violated:{entry.modality}",
                )
            )
    return verdicts


def _compiled_verdicts(model: Model, pre: Population) -> list[TransitionVerdict]:
    """Compiled obligations, evaluated against the PRE-state.

    These are the standing claims trace compilation derived -- "every reimbursed
    expense was submitted" -- so they are checkable against data at rest and
    they belong to the pre-snapshot family, not to any step. A walk can be
    entirely correct and still surface one, which is the point: the defect was
    already in the data before anyone walked anywhere.

    EVERY operation's obligations are evaluated, not just those of the
    operations this walk happens to use. The claim is about the data, not about
    the walk -- "every reimbursed expense has an approver" is either true of a
    population or it is not, and whether today's walk reimburses anything has
    nothing to do with it. A first draft scoped this to the walk's operations
    and silently missed a pre-state defect the corpus was built to catch.

    An obligation whose fact types the pre-population does not COVER is skipped,
    not reported: absence in an uncovered fact type carries no information, and
    reporting one would be the same partial-green the coverage gate exists to
    prevent.
    """
    verdicts: list[TransitionVerdict] = []
    covered = set(pre.covers or [])
    for operation in model.operations:
        for entry in model.compiled_obligations(str(operation.get("id"))):
            subset = entry.get("subset")
            compiled = bool(subset)
            if transition_kernel.compiled_subset_verdict(compiled, True, False, True) != "pass":
                raise AssertionError("compiled transition kernel rejects a clean obligation")
            if not compiled:
                record_branch("transition:compiled-subset:n-a:uncompiled")
                continue
            is_covered = not ({str(subset["of"]), str(subset["in"])} - covered)
            coverage_decision = transition_kernel.compiled_subset_verdict(
                True, is_covered, False, True
            )
            if not is_covered and coverage_decision == "pass":
                record_branch("transition:compiled-subset:n-a:uncovered")
                continue
            of_facts = (pre.facts or {}).get(str(subset["of"]), [])
            in_facts = (pre.facts or {}).get(str(subset["in"]), [])
            offending = [
                fact
                for fact in of_facts
                if not any(
                    all(
                        _identity_key(fact.get(of_role)) == _identity_key(other.get(in_role))
                        for of_role, in_role in entry["role_pairs"]
                    )
                    for other in in_facts
                )
            ]
            modality = str(entry.get("modality", ""))
            decision = transition_kernel.compiled_subset_verdict(
                True, True, bool(offending), modality == "alethic"
            )
            if decision == "pass":
                record_branch("transition:compiled-subset:n-a:clean")
                continue
            verdicts.append(
                TransitionVerdict(
                    family="pre_snapshot",
                    locator=str(entry.get("locator")),
                    kind="compiled-subset",
                    modality=modality,
                    verdict=decision,  # type: ignore[arg-type]
                    fact_type=str(subset["of"]),
                    obligation=str(entry.get("obligation")),
                    offending_facts=offending,
                    message=(
                        f"'{entry.get('obligation')}' compiles to: every {subset['of']} "
                        f"fact has a matching {subset['in']} fact. {len(offending)} "
                        f"do not"
                    ),
                    scope_id=f"transition:compiled-subset:n-a:violated:{modality}",
                )
            )
    return verdicts


def _effective_extension_state(
    model: Model,
    asserted: State,
    extensions: Mapping[str, tuple[Mapping[str, Any], ...]],
    unavailable: Collection[str] = (),
) -> State:
    """Overlay every computed structured extension for read-only evaluation."""
    effective = copy.deepcopy(asserted)
    structured_ids = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    }
    if any(row.stability == "static" for row in derivation_classifications(model.model_dump())):
        record_branch("composition:derivation-view:static:applied")
    for fact_type_id in structured_ids:
        effective[fact_type_id] = (
            []
            if fact_type_id in unavailable
            else [dict(row) for row in extensions.get(fact_type_id, ())]
        )
    return effective


def _unavailable_precondition_verdicts(
    index: int,
    operation: Mapping[str, Any],
    unavailable: Mapping[str, Any],
) -> tuple[dict[str, Any], list[TransitionVerdict]]:
    """Suppress reads of unavailable relations and retain one explicit finding."""
    pinned = copy.deepcopy(operation)
    verdicts: list[TransitionVerdict] = []
    kept: list[dict[str, Any]] = []
    for obligation in operation.get("preconditions") or []:
        dependency = next(
            (
                str(atom.get("fact_type"))
                for atom in obligation.get("require") or []
                if str(atom.get("fact_type")) in unavailable
            ),
            None,
        )
        if dependency is None:
            kept.append(copy.deepcopy(obligation))
            continue
        origin = unavailable[dependency]
        reason = str(origin.reason)
        if reason not in {
            "term:mod-zero",
            "term:exact-value-too-wide",
            "term:dependency-unavailable",
            "term:div-zero",
            "term:sqrt-negative",
            "term:haversine-coordinate-range",
            "term:float-overflow",
        }:
            reason = "term:dependency-unavailable"
        event = {
            "term:mod-zero": "unchecked-mod-zero",
            "term:exact-value-too-wide": "unchecked-exact-value-too-wide",
            "term:dependency-unavailable": "unchecked-dependency-unavailable",
            "term:div-zero": "unchecked-div-zero",
            "term:sqrt-negative": "unchecked-sqrt-negative",
            "term:haversine-coordinate-range": "unchecked-haversine-coordinate-range",
            "term:float-overflow": "unchecked-float-overflow",
        }[reason]
        modality = str(obligation.get("modality"))
        verdicts.append(
            TransitionVerdict(
                family="step",
                locator=f"$.steps[{index}].preconditions[id={obligation.get('id')}]",
                kind="precondition",
                modality=modality,
                verdict="unchecked",
                reason_code=reason,
                fact_type=dependency,
                obligation=str(obligation.get("id")),
                message=(
                    f"step {index} ({operation.get('id')}) cannot evaluate precondition "
                    f"'{obligation.get('id')}': relation '{dependency}' is unavailable "
                    f"because {origin.reason}; binding={dict(origin.binding)!r}."
                ),
                scope_id=f"transition:precondition:n-a:{event}",
            )
        )
    pinned["preconditions"] = kept
    return pinned, verdicts


def _unknown_precondition_verdicts(
    index: int,
    operation: Mapping[str, Any],
    model: Model,
    state: State,
    possible: Mapping[str, tuple[tuple[Any, ...], ...]],
    bindings: Mapping[str, Any],
) -> tuple[dict[str, Any], list[TransitionVerdict]]:
    """Leave definite misses to the ordinary evaluator and defer possible reads."""
    pinned = copy.deepcopy(operation)
    retained = []
    verdicts = []
    fact_types = {str(row.get("id")): row for row in model.fact_types}
    for obligation in operation.get("preconditions") or []:
        unknown = False
        definite_miss = False
        for atom in obligation.get("require") or []:
            head, ground = patterns.ground_atom(atom, bindings)
            if patterns.holds(atom, state.get(head, []), bindings, identity=_identity_key):
                continue
            roles = [str(row.get("role_name")) for row in fact_types[head].get("roles") or []]
            if any(
                all(role not in ground or _partial_compatible(ground[role], row[roles.index(role)])
                    for role in roles)
                for row in possible.get(head, ())
            ):
                unknown = True
            else:
                definite_miss = True
                break
        if definite_miss or not unknown:
            retained.append(copy.deepcopy(obligation))
            continue
        modality = str(obligation.get("modality"))
        verdicts.append(TransitionVerdict(
            family="step",
            locator=f"$.steps[{index}].preconditions[id={obligation.get('id')}]",
            kind="precondition",
            modality=modality,
            verdict="unchecked",
            reason_code="derived-unknown",
            fact_type=str((obligation.get("require") or [{}])[0].get("fact_type")),
            obligation=str(obligation.get("id")),
            message=f"step {index} ({operation.get('id')}) has a possible-only precondition.",
            scope_id="transition:precondition:n-a:unchecked-derived-unknown",
        ))
    pinned["preconditions"] = retained
    return pinned, verdicts


def _compiled_verdicts_for_dynamic_walk(
    model: Model,
    pre: Population,
) -> list[TransitionVerdict]:
    """Standing PRE compilation excludes obligations read after dynamic refresh."""
    dynamic_heads = {
        row.fact_type
        for row in derivation_classifications(model.model_dump())
        if row.stability == "dynamic"
    }
    dynamic_locators: set[str] = set()
    for operation in model.operations:
        dynamic_obligations = {
            str(obligation.get("id"))
            for obligation in operation.get("preconditions") or []
            if any(
                isinstance(atom, dict) and str(atom.get("fact_type")) in dynamic_heads
                for atom in obligation.get("require") or []
            )
        }
        dynamic_locators.update(
            str(entry.get("locator"))
            for entry in model.compiled_obligations(str(operation.get("id")))
            if str(entry.get("obligation")) in dynamic_obligations
        )
    return [
        verdict
        for verdict in _compiled_verdicts(model, pre)
        if verdict.locator not in dynamic_locators
    ]


def _dynamic_heads_for_step(
    model: Model,
    operation: Mapping[str, Any],
) -> tuple[str, ...]:
    """Dynamic heads selected by this operation's asserted dependency touch."""
    touched = _touched_by(dict(operation))
    selected = {
        row.fact_type
        for row in derivation_classifications(model.model_dump())
        if row.stability == "dynamic" and touched.intersection(row.asserted_dependencies)
    }
    return tuple(
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if str(fact_type.get("id")) in selected
    )


def _derived_changes(
    model: Model,
    old: Mapping[str, tuple[Mapping[str, Any], ...]],
    new: Mapping[str, tuple[Mapping[str, Any], ...]],
    selected: set[str] | frozenset[str],
) -> list[DerivedChange]:
    """Canonical identity-set deltas for selected structured heads."""
    result: list[DerivedChange] = []
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        if fact_type_id not in selected:
            continue
        old_rows = {_fact_key(dict(row)): dict(row) for row in old.get(fact_type_id, ())}
        new_rows = {_fact_key(dict(row)): dict(row) for row in new.get(fact_type_id, ())}
        added = [new_rows[key] for key in sorted(set(new_rows) - set(old_rows))]
        removed = [old_rows[key] for key in sorted(set(old_rows) - set(new_rows))]
        if not added and not removed:
            continue
        if added:
            record_branch("transition:derived-change:added:projected")
        if removed:
            record_branch("transition:derived-change:removed:projected")
        result.append(DerivedChange(fact_type=fact_type_id, added=added, removed=removed))
    return result


def _evaluate_derived_dynamic_rules(
    index: int,
    operation: Mapping[str, Any],
    bindings: Mapping[str, Any],
    model: Model,
    old_view: State,
    new_view: State,
    dependency_touched: frozenset[str],
    changed_heads: frozenset[str],
    old_possible: Mapping[str, tuple[tuple[Any, ...], ...]],
    new_possible: Mapping[str, tuple[tuple[Any, ...], ...]],
) -> list[TransitionVerdict]:
    """Grade structured dynamic subjects after their computed view refreshes."""
    classifications = {row.fact_type: row for row in derivation_classifications(model.model_dump())}
    op_id = str(operation.get("id"))
    verdicts: list[TransitionVerdict] = []
    for rule_index, rule in enumerate(operation.get("dynamic_rules") or []):
        subject = rule.get("subject")
        if not isinstance(subject, dict):
            continue
        subject_type = str(subject.get("fact_type"))
        classification = classifications.get(subject_type)
        if classification is None:
            continue
        modality = str(rule.get("modality", ""))
        if not dependency_touched.intersection(classification.asserted_dependencies):
            record_branch("transition:dynamic-rule:derived-untouched:refused")
            continue
        old = _subject_value(subject, old_view, dict(bindings))
        new = _subject_value(subject, new_view, dict(bindings))
        _fact, ground = patterns.ground_atom(subject, bindings)
        names = [str(role.get("role_name")) for role in next(
            ft for ft in model.fact_types if ft.get("id") == subject_type
        ).get("roles") or []]
        uncertain = any(
            any(isinstance(value, _Wildcard) for value in row)
            and all(role not in ground or _partial_compatible(ground[role], row[names.index(role)])
                    for role in names)
            for patterns_for_state in (old_possible, new_possible)
            for row in patterns_for_state.get(subject_type, ())
        )
        same_grounded_subject = (old is _MISSING and new is _MISSING) or (
            old is not _MISSING and new is not _MISSING and _identity_key(old) == _identity_key(new)
        )
        if not uncertain and (subject_type not in changed_heads or same_grounded_subject):
            record_branch("transition:dynamic-rule:derived-no-delta:refused")
            continue
        common = {
            "family": "step",
            "locator": f"$.steps[{index}].dynamic_rules[{rule_index}]",
            "kind": "dynamic-rule",
            "modality": modality,
            "fact_type": subject_type,
            "obligation": str(rule.get("id")),
        }
        functional = dynamic_subject_is_functional(subject, model.fact_types)
        if functional is False:
            verdicts.append(
                TransitionVerdict(
                    **common,
                    verdict="unchecked",
                    reason_code="transition:dynamic-subject-not-functional",
                    message=(
                        f"step {index} ({op_id}) cannot compare old and new values of "
                        f"'{subject.get('value_role')}' on {subject_type}: no internal "
                        "uniqueness constraint proves the subject functional"
                    ),
                    scope_id="transition:dynamic-rule:derived-nonfunctional:unchecked",
                )
            )
            continue
        if uncertain:
            verdicts.append(TransitionVerdict(
                **common,
                verdict="unchecked",
                reason_code="derived-unknown",
                message=f"step {index} ({op_id}) has a possible-only dynamic subject.",
                scope_id="transition:dynamic-rule:derived-unknown:unchecked",
            ))
            continue
        if old is _MISSING or new is _MISSING:
            no_old = old is _MISSING
            verdicts.append(
                TransitionVerdict(
                    **common,
                    verdict="vacuous",
                    message=(
                        f"step {index} ({op_id}): dynamic rule '{rule.get('id')}' has "
                        + (
                            "no old value to compare against"
                            if no_old
                            else "no new value -- the subject was removed"
                        )
                    ),
                    scope_id=(
                        "transition:dynamic-rule:derived-no-old:vacuous"
                        if no_old
                        else "transition:dynamic-rule:derived-no-new:vacuous"
                    ),
                )
            )
            continue
        comparison_holds = _compare_values(str(rule.get("op")), new, old)
        decision = transition_kernel.dynamic_verdict(
            True,
            True,
            True,
            True,
            comparison_holds,
            modality == "alethic",
        )
        if decision == "pass":
            record_branch("transition:dynamic-rule:derived-comparison:clean")
            continue
        verdicts.append(
            TransitionVerdict(
                **common,
                verdict=decision,  # type: ignore[arg-type]
                offending_facts=[{"old": old, "new": new}],
                message=(
                    f"step {index} ({op_id}): dynamic rule '{rule.get('id')}' requires "
                    f"new {rule.get('op')} old, and {new!r} {rule.get('op')} {old!r} "
                    "does not hold"
                ),
                scope_id=f"transition:dynamic-rule:derived-comparison:violated:{modality}",
            )
        )
    return verdicts


def _unavailable_dynamic_rule_verdicts(
    index: int,
    operation: Mapping[str, Any],
    model: Model,
    unavailable: Mapping[str, Any],
) -> list[TransitionVerdict]:
    verdicts: list[TransitionVerdict] = []
    classifications = {row.fact_type: row for row in derivation_classifications(model.model_dump())}
    touched = _touched_by(dict(operation))
    for rule_index, rule in enumerate(operation.get("dynamic_rules") or []):
        subject = rule.get("subject") if isinstance(rule, Mapping) else None
        subject_type = str(subject.get("fact_type")) if isinstance(subject, Mapping) else ""
        if subject_type not in unavailable:
            continue
        classification = classifications.get(subject_type)
        if classification is None or not touched.intersection(classification.asserted_dependencies):
            record_branch("transition:dynamic-rule:derived-untouched:refused")
            continue
        origin = unavailable[subject_type]
        reason = str(origin.reason)
        if reason not in {
            "term:mod-zero",
            "term:exact-value-too-wide",
            "term:dependency-unavailable",
            "term:div-zero",
            "term:sqrt-negative",
            "term:haversine-coordinate-range",
            "term:float-overflow",
        }:
            reason = "term:dependency-unavailable"
        event = {
            "term:mod-zero": "unchecked-mod-zero",
            "term:exact-value-too-wide": "unchecked-exact-value-too-wide",
            "term:dependency-unavailable": "unchecked-dependency-unavailable",
            "term:div-zero": "unchecked-div-zero",
            "term:sqrt-negative": "unchecked-sqrt-negative",
            "term:haversine-coordinate-range": "unchecked-haversine-coordinate-range",
            "term:float-overflow": "unchecked-float-overflow",
        }[reason]
        verdicts.append(
            TransitionVerdict(
                family="step",
                locator=f"$.steps[{index}].dynamic_rules[{rule_index}]",
                kind="dynamic-rule",
                modality=str(rule.get("modality")),
                verdict="unchecked",
                reason_code=reason,
                fact_type=subject_type,
                obligation=str(rule.get("id")),
                message=(
                    f"step {index} ({operation.get('id')}) cannot evaluate dynamic rule "
                    f"'{rule.get('id')}': relation '{subject_type}' is unavailable "
                    f"because {origin.reason}; binding={dict(origin.binding)!r}."
                ),
                scope_id=f"transition:dynamic-rule:derived-unavailable:{event}",
            )
        )
    return verdicts


def _without_derivation_claims(report: CheckReport) -> CheckReport:
    """Synthetic intermediate states make no claimed-extension assertion."""
    return report.model_copy(update={"derivations": []})


def _population_from_asserted_state(
    model: Model,
    state: State,
    covers: list[str],
    index: int,
) -> Population:
    document = {
        "population": {
            "model": "<dynamic asserted state>",
            "source": "synthetic",
            "covers": covers,
        },
        "facts": state,
    }
    if any(isinstance(value, dict) and set(value) == {"$opaque"}
           for rows in state.values() for row in rows for value in row.values()):
        document["format_version"] = 2
        document["population"]["model_id"] = model.model_id
    return load_population_bytes(
        artifacts.canonical_json_bytes(document),
        source=f"<dynamic asserted state after step {index}>",
        model=model,
    )


def _evaluate_to_state(
    model: Model,
    pre: Population,
    steps: list[dict[str, Any]],
) -> tuple[TransitionReport, State, Population | None]:
    """Evaluate the shared pre/step spine and return its admitted final state."""
    fixed_facts = {}
    if model.reference_populations:
        from gnd.references import bind_population, resolve_context

        context = resolve_context(model)
        view = bind_population(model, pre, references=context)
        fixed_facts = {
            ft: rows for ft, rows in view.combined.facts.items() if ft in dict(context._owners)
        }
    declared = _operations_by_id(model)
    report = TransitionReport(
        pre_snapshot=check(model, pre),
        pre_snapshot_verdicts=_compiled_verdicts_for_dynamic_walk(model, pre),
    )
    covers = list(pre.covers or [])
    state = _state_of(pre)
    population: Population | None = pre
    extension_view = structured_extension_view(model, pre)
    extensions = extension_view.facts
    unavailable = extension_view.unavailable
    possible = extension_view.possible
    structured_ids = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    }
    # A refusal to refresh is only an event for models that have something to refresh.
    dynamic_heads = any(
        row.stability == "dynamic" for row in derivation_classifications(model.model_dump())
    )
    for index, step in enumerate(steps, start=1):
        operation = declared[str(step["op"])]
        effective_state = _effective_extension_state(model, state, extensions, unavailable)
        effective_state.update(fixed_facts)
        pinned_operation, unavailable_verdicts = _unavailable_precondition_verdicts(
            index, operation, unavailable
        )
        pinned_operation, unknown_verdicts = _unknown_precondition_verdicts(
            index, pinned_operation, model, effective_state, possible, step["bindings"]
        )
        pinned_operation["dynamic_rules"] = [
            rule if str((rule.get("subject") or {}).get("fact_type")) not in structured_ids else {}
            for rule in operation.get("dynamic_rules") or []
        ]
        result, evaluated_state = _evaluate_step(
            index,
            step,
            pinned_operation,
            model,
            effective_state,
            population,
        )
        result.verdicts.extend([*unavailable_verdicts, *unknown_verdicts])
        state = _restore_asserted_state(model, state, evaluated_state)
        state = {ft: rows for ft, rows in state.items() if ft not in fixed_facts}
        try:
            asserted_population = _population_from_asserted_state(model, state, covers, index)
        except Exception:  # noqa: BLE001 - normative intermediate owns unchecked
            asserted_population = None
        selected = _dynamic_heads_for_step(model, operation)
        old_extensions = extensions
        old_possible = possible
        old_unavailable = unavailable
        if selected and asserted_population is not None:
            refreshed = structured_extension_view(
                model,
                asserted_population,
                previous=extensions,
                previous_unavailable=unavailable,
                previous_possible=possible,
                refresh=selected,
            )
            extensions = refreshed.facts
            unavailable = refreshed.unavailable
            possible = refreshed.possible
            record_branch("composition:dynamic-refresh:selected:projected")
        elif not selected and dynamic_heads:
            record_branch("composition:dynamic-refresh:no-touch:refused")
        changes = _derived_changes(
            model,
            old_extensions,
            extensions,
            frozenset(selected) - set(old_unavailable) - set(unavailable),
        )
        result.derived_changes = changes
        new_effective_state = _effective_extension_state(model, state, extensions, unavailable)
        result.verdicts.extend(
            _evaluate_derived_dynamic_rules(
                index,
                operation,
                step["bindings"],
                model,
                effective_state,
                new_effective_state,
                frozenset(_touched_by(operation)),
                frozenset(change.fact_type for change in changes),
                old_possible,
                possible,
            )
        )
        result.verdicts.extend(
            _unavailable_dynamic_rule_verdicts(index, operation, model, unavailable)
        )
        intermediate_view = new_effective_state
        population, unloadable = _load_intermediate(intermediate_view, model, covers, index)
        if unloadable is not None:
            result.verdicts.append(unloadable)
        elif population is not None:
            result.intermediate = _without_derivation_claims(check(model, population))
        report.steps.append(result)
    report.frame_grading = _frame_grading(model, steps)
    final_asserted = None
    if population is not None:
        try:
            final_asserted = _population_from_asserted_state(model, state, covers, len(steps))
        except Exception:  # noqa: BLE001 - final intermediate already records band 4
            final_asserted = None
    return report, state, final_asserted


def evaluate(
    model: Model,
    pre: Population,
    post: Population,
    steps: list[dict[str, Any]],
) -> TransitionReport:
    """The whole declared-post walk, in the normative evaluation order."""
    report, state, computed_final = _evaluate_to_state(model, pre, steps)
    report.frame_verdicts = _frame_verdicts(report.frame_grading, state, post)
    # The declared POST snapshot is deliberately last. A walk first establishes
    # its PRE obligations, each complete intermediate state, and the frame delta
    # between computed and declared final facts. Only then do ordinary snapshot
    # constraints grade the declared POST. This order is observable even when
    # the final collection of verdicts is otherwise identical.
    own_post = check(model, post)
    if computed_final is not None:
        dynamic_heads = {
            row.fact_type
            for row in derivation_classifications(model.model_dump())
            if row.stability == "dynamic"
        }
        if dynamic_heads:
            computed_claims = {
                row.fact_type: row for row in derivation_claims_against(model, post, computed_final)
            }
            own_post = own_post.model_copy(
                update={
                    "derivations": [
                        computed_claims.get(row.fact_type, row)
                        if row.fact_type in dynamic_heads
                        else row
                        for row in own_post.derivations
                    ],
                    "snapshot_projection": None,
                }
            )
    report.post_snapshot = own_post
    return report


def evaluate_plan(
    model: Model,
    pre: Population,
    steps: list[dict[str, Any]],
) -> ComputedTransition:
    """Apply a walk and return its computed post without a frame comparison."""
    report, state, _ = _evaluate_to_state(model, pre, steps)
    loadable_document = {
        "population": {
            "model": pre.model,
            **({"model_id": pre.model_id} if pre.model_id is not None else {}),
            "source": "synthetic",
            "covers": list(pre.covers or []),
        },
        "facts": state,
    }
    if any(isinstance(value, dict) and set(value) == {"$opaque"}
           for rows in state.values() for row in rows for value in row.values()):
        loadable_document["format_version"] = 2
    canonical = artifacts.canonical_json_bytes(loadable_document)
    computed_document = json.loads(canonical)
    computed_document["population"]["model_id"] = pre.model_id
    try:
        computed = load_population_bytes(canonical, source="<computed post>", model=model)
    except Exception:  # noqa: BLE001 - the final intermediate already records band 4
        computed = None
    if computed is not None:
        effective_post = _effective_extension_state(
            model,
            state,
            structured_extension_view(model, computed).facts,
        )
        effective_document = copy.deepcopy(loadable_document)
        effective_document["facts"] = effective_post
        effective_population = load_population_bytes(
            artifacts.canonical_json_bytes(effective_document),
            source="<computed post evaluation view>",
            model=model,
        )
        report.post_snapshot = check(model, effective_population)
    return ComputedTransition(
        report=report,
        post=computed,
        computed_post=computed_document,
    )


def frame_modalities(model: Model) -> dict[str, tuple[str, list[str]]]:
    """`{fact_type: (modality, operations)}` over EVERY operation in the model.

    What `validate --trace` reports, and deliberately not the same thing as
    `_frame_grading`: that one grades the fact types ONE WALK touches, this one
    shows what the model would produce before any walk narrows it. A fact type
    touched by any deontic-framed operation grades deontic and the deontic
    operations are named, because those are the declarations that bought the
    leniency; otherwise it grades alethic and every toucher is named.
    """
    touchers: dict[str, list[str]] = {}
    for operation in model.operations:
        op_id = str(operation.get("id"))
        for fact_type_id in _touched_by(operation):
            touchers.setdefault(fact_type_id, []).append(op_id)
    grading: dict[str, tuple[str, list[str]]] = {}
    declared = _operations_by_id(model)
    for fact_type_id, names in touchers.items():
        deontic = [
            name
            for name in names
            if str((declared[name].get("frame") or {}).get("modality", "")) == "deontic"
        ]
        grading[fact_type_id] = (
            "deontic" if deontic else "alethic",
            sorted(deontic or names),
        )
    return grading
