"""Immutable snapshot inputs for the v6 formal specification.

These values retain input meaning; constructing them is not a proof. Relation
rows are the admitted claims, not calculated derivation extensions. Structured
rules and their dependency graph remain explicit for the later correspondence
and derivation phases. A missing scalar cell always has an explicit refusal.
Refused positions retain location and reason, not the offending value; this
representation is not injective outside the representable scalar domain.
"""

from dataclasses import dataclass, field

# Avoid the pinned verifier's unsound seven-element tuple constructor. The
# runtime vocabulary is identical; this constant is not used by proof code.
SCALAR_KINDS = tuple(  # noqa: C409 -- a literal triggers the pin's unsound constructor
    ["string", "number", "boolean", "date", "datetime-aware", "datetime-naive", "null"]
)
IDENTITY_KINDS = ("string", "number", "boolean", "null")
ADAPTER_REFUSALS = (
    "opaque-value",
    "untyped-string-ordering",
    "non-finite-number",
    "boolean-in-numeric-role",
    "unresolvable-role",
    "unregistered-family",
    "malformed-constraint",
)
OPERAND_KINDS = ("role", "variable", "literal", "clock")
CONSEQUENT_KINDS = ("comparison", "atom", "absence", "exists", "")
FLAG_NAMES = ("exclusive", "exhaustive", "min-inclusive", "max-inclusive")
RELATION_SOURCES = ("claimed", "computed-extension", "empty")


@dataclass(frozen=True)
class Scalar:
    kind: str
    token: str
    num: int
    den: int
    ordered: bool
    identity_kind: str


@dataclass(frozen=True)
class Opaque:
    """A present but unreadable role value, never a scalar identity."""

    label: str


@dataclass(frozen=True)
class IRRefusal:
    location: str
    reason: str


@dataclass(frozen=True)
class IRRole:
    name: str
    object_type: str
    primitive: str


@dataclass(frozen=True)
class IRFactType:
    id: str
    roles: tuple[IRRole, ...]
    declared: bool
    derivation: str
    structured_rule: bool
    relation_source: str
    opaque_rule: str


@dataclass(frozen=True)
class IRRelation:
    fact_type: str
    rows: tuple[tuple[Scalar | None, ...], ...]
    refusals: tuple[IRRefusal, ...]


@dataclass(frozen=True)
class IRRoster:
    object_type: str
    members: tuple[Scalar | None, ...]
    refusals: tuple[IRRefusal, ...]


@dataclass(frozen=True)
class IRObjectType:
    id: str
    kind: str
    primitive: str
    subtypes: tuple[str, ...]
    denoting: tuple[str, ...]
    derivation: str
    opaque_rule: str


@dataclass(frozen=True)
class IROperand:
    kind: str
    fact_type: str = ""
    role: str = ""
    variable: str = ""
    literal: Scalar | None = None
    raw_literal: Scalar | None = None
    primitive: str = ""
    tagged: bool = False
    valid: bool = True
    refused: str = ""
    function: str = ""
    arguments: tuple["IROperand", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class IRAtom:
    fact_type: str
    bindings: tuple[tuple[str, IROperand], ...]


@dataclass(frozen=True)
class IRDerivation:
    fact_type: str
    head: tuple[tuple[str, IROperand], ...]
    body: tuple[IRAtom, ...]
    negate: tuple[IRAtom, ...]
    dependencies: tuple[str, ...]
    components: tuple[tuple[str, ...], ...]
    refusals: tuple[IRRefusal, ...]


@dataclass(frozen=True)
class IRConstraint:
    ref: str
    family: str
    variant: str
    modality: str
    fact_type: str
    roles: tuple[str, ...]
    role_refs: tuple[tuple[str, str], ...]
    sequences: tuple[tuple[tuple[str, str], ...], ...]
    object_type: str
    subtypes: tuple[str, ...]
    flags: tuple[bool, ...]
    minimum: Scalar | None
    maximum: Scalar | None
    allowed: tuple[Scalar, ...]
    ranges: tuple[tuple[Scalar | None, Scalar | None, bool, bool], ...]
    operator: str
    literal: Scalar | None
    operands: tuple[IROperand, ...]
    consequent_kind: str
    antecedent: tuple[IRAtom, ...]
    consequent: tuple[IRAtom, ...]
    scope_fact_types: tuple[str, ...]
    expression: str
    refused: str
    exists_atoms: tuple[IRAtom, ...] = field(default_factory=tuple)
    exists_where: tuple[tuple[str, IROperand, IROperand], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SnapshotIR:
    object_types: tuple[IRObjectType, ...]
    fact_types: tuple[IRFactType, ...]
    relations: tuple[IRRelation, ...]
    rosters: tuple[IRRoster, ...]
    constraints: tuple[IRConstraint, ...]
    finite: bool
    covers: tuple[str, ...]
    explicit_rosters: tuple[IRRoster, ...]
    derivations: tuple[IRDerivation, ...]
    derivation_order: tuple[str, ...]
    refusals: tuple[IRRefusal, ...]
