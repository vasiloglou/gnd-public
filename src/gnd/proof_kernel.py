"""The v6.0 Phase 1 proof slice -- the whole of the bounded semantic kernel.

The clauses N1-N9 this module implements have exactly one home, and it is not
this file: `.gnd-planning/milestones/v6.0/notes/phase-1-spec.md` section 5.1, as
amended by its section 14. Code here cites clause identifiers and restates none
of them.

**Every definition in this file is inside the subset the pinned verifier can
translate**, and that is the point: frozen dataclasses, tuples, strings,
integers and booleans, with no `Any`, no mapping, no third-party type, and no
`from __future__ import annotations` (measured: Nagini 1.3.1 does not translate
it). Section 5.7 admits a generated contract-carrying copy only when erasing its
contract-only calls returns it to THIS file's executable AST, statement for
statement -- so a definition that cannot be translated cannot live here at all.
The two admitted-value bridges that used to sit at the bottom of this module are
in `gnd.proof_bridge`, and each is gated by a verified function above: no value
reaches production from either bridge unless a proved predicate in this file
accepted it.

Nothing in this module imports a proof tool, and nothing outside the standard
library is imported at all. The proof lane reads these bytes; it never ships
with them.
"""

from dataclasses import dataclass
from typing import Literal

SliceFamily = Literal["mandatory", "frequency", "textual-refusal"]
SliceModality = Literal["alethic", "deontic"]
#: The five-state verdict lattice, as DATA rather than as a type. A14/A15: the
#: pinned verifier crashes on any Literal of five or more members (measured:
#: four verify, five and six abort Viper's chopper with `union_type_5`), so the
#: closed vocabulary is carried by this tuple and by the contracts and tests that
#: quantify over it, and the annotation below is the widest type that translates.
#: Meaning is unchanged: no value outside this tuple is constructible by
#: `evaluate_phase1_slice`, and `test_v6_phase1_kernel.py` enumerates all five.
SLICE_VERDICT_NAMES = ("pass", "fail", "warning", "unchecked", "vacuous")
SliceVerdictName = str
#: The same measured reason as SLICE_VERDICT_NAMES, and a sharper one. A
#: postcondition over a Literal-TYPED result is accepted and proves nothing:
#: measured, a function annotated `-> Literal["proof-backed", "partial", "none"]`
#: that returns "proof-backed" where its contract demands "partial" VERIFIES,
#: while the same body annotated `-> str` is rejected. Only the M05 mutation gate
#: exposed it. So every value these vocabularies name is carried as data and the
#: annotations are the widest type the verifier reasons about; the vocabularies
#: are closed by contract, by the tests that enumerate them, and by the report
#: schema, not by an annotation that silently disables the proof.
SLICE_DECISIONS = ("accept", "refuse", "indeterminate")
SLICE_ASSURANCES = ("proof-backed", "partial", "none")
SliceDecision = str
SliceAssurance = str

#: A14.4 ratified these two closed vocabularies. They are data, not prose: a
#: reason the kernel can emit is a member of the first, and a reason the
#: evidence lane records for a refusal to certify is a member of the second.
SLICE_REASON_CODES = ("coverage-omission", "empty-subject", "textual-not-mechanical")
REFUSAL_REASON_CODES = (
    "out-of-scope-family",
    "out-of-scope-cardinality",
    "evidence-not-current",
)

#: The admitted bound, section 5.2 as amended by A14.1. It is load-bearing, not
#: decorative: every witness below is computed by bounded case analysis over
#: exactly these limits, so a slice one element wider is refused rather than
#: silently evaluated by an unbounded loop.
MAX_SLICE_CONSTRAINTS = 3
MAX_UNIVERSE_MEMBERS = 2
MAX_PLAYER_IDENTITIES = 2
MAX_FREQUENCY_GROUPS = 2
MAX_GROUP_COUNT = 3


@dataclass(frozen=True)
class SliceGroup:
    key: tuple[str, ...]
    count: int


@dataclass(frozen=True)
class SliceInput:
    constraint_ref: str
    family: SliceFamily
    modality: SliceModality
    covered: bool
    subject_has_facts: bool
    universe: tuple[str, ...]
    players: tuple[str, ...]
    groups: tuple[SliceGroup, ...]
    minimum: int | None
    maximum: int | None


@dataclass(frozen=True)
class SliceVerdict:
    constraint_ref: str
    family: SliceFamily
    modality: SliceModality
    verdict: SliceVerdictName
    reason_code: str | None
    witness: tuple[tuple[str, ...], ...]


# --- the pure core -------------------------------------------------------


def phase1_in_scope(value: SliceInput) -> bool:
    """Total over every `SliceInput`, including malformed ones (O7).

    Returns False rather than raising for every unsupported family or form, so
    trusted admission is never the only thing standing between an unsupported
    construct and a proof-backed claim.
    """
    if value.family not in ("mandatory", "frequency", "textual-refusal"):
        return False
    if value.modality not in ("alethic", "deontic"):
        return False
    if not isinstance(value.constraint_ref, str) or value.constraint_ref == "":
        return False
    if not isinstance(value.covered, bool) or not isinstance(value.subject_has_facts, bool):
        return False
    if not _canonical_identities(value.universe, MAX_UNIVERSE_MEMBERS):
        return False
    if not _canonical_identities(value.players, MAX_PLAYER_IDENTITIES):
        return False
    if len(value.groups) > MAX_FREQUENCY_GROUPS:
        return False
    index = 0
    while index < len(value.groups):
        group = value.groups[index]
        if not isinstance(group, SliceGroup):
            return False
        if not isinstance(group.count, int) or isinstance(group.count, bool):
            return False
        # N4 groups OCCURRING values, so a zero-count group misdescribes an
        # impossible observation. Finding F11: while zero was admitted here, a
        # never-observed key with count zero passed the two-way canonicalization
        # check (0 == its occurrence count) and fabricated an alethic failure
        # whose witness named a value no fixture contains.
        if group.count < 1 or group.count > MAX_GROUP_COUNT:
            return False
        if len(group.key) != 1 or not isinstance(group.key[0], str):
            return False
        other = 0
        while other < index:
            if value.groups[other].key[0] == group.key[0]:
                return False
            other = other + 1
        index = index + 1

    if value.family == "frequency":
        if value.universe != () or value.players != ():
            return False
        return _bounds_in_scope(value.minimum, value.maximum)
    if value.minimum is not None or value.maximum is not None:
        return False
    if value.groups != ():
        return False
    if value.family == "mandatory":
        return _players_come_from_the_universe(value.universe, value.players)
    # N6 admits the ALETHIC textual refusal only. A deontic textual constraint
    # is ordinary production output and takes the refusal branch here, which is
    # why it has no verdict row of its own to leave uncovered.
    return (
        value.modality == "alethic"
        and value.universe == ()
        and value.players == ()
        and value.covered
        and value.subject_has_facts
    )


def phase1_decide(value: SliceInput) -> SliceVerdict | None:
    """Refuse, or decide -- the one entry point production calls.

    The scope check and the evaluation are joined HERE, inside the verified
    world, so `evaluate_phase1_slice`'s bounded-domain precondition is
    discharged by a proof rather than by a caller nobody verified. Returning
    None is the refusal-to-certify branch, and it is a decision the evidence
    lane records, never an absence.
    """
    if not phase1_in_scope(value):
        return None
    return evaluate_phase1_slice(value)


def evaluate_phase1_slice(value: SliceInput) -> SliceVerdict:
    """The only evaluator for an in-scope constraint (N3-N6).

    Its precondition is the bounded domain, and `phase1_decide` is what
    establishes it; every branch below is reachable from the corpus, and the
    witness is computed by bounded case analysis rather than by an unbounded
    search.
    """
    if value.family == "textual-refusal":
        return SliceVerdict(
            value.constraint_ref,
            value.family,
            value.modality,
            "unchecked",
            "textual-not-mechanical",
            (),
        )
    if value.family == "mandatory":
        if not value.covered:
            return _decided(value, "vacuous", "coverage-omission", ())
        if not value.subject_has_facts:
            return _decided(value, "vacuous", "empty-subject", ())
        witness = _mandatory_witness(value.universe, value.players)
        if witness == ():
            return _decided(value, "pass", None, ())
        return _decided(value, _violation(value.modality), None, witness)
    if not value.subject_has_facts:
        return _decided(value, "vacuous", "empty-subject", ())
    witness = _frequency_witness(value.groups, value.minimum, value.maximum)
    if witness == ():
        return _decided(value, "pass", None, ())
    return _decided(value, _violation(value.modality), None, witness)


def compose_phase1_band(verdicts: tuple[SliceVerdict, ...]) -> int:
    """N7, as ONE walk over every verdict -- never a per-family copy."""
    has_alethic_fail = False
    has_alethic_unchecked = False
    has_vacuous = False
    index = 0
    while index < len(verdicts):
        verdict = verdicts[index]
        alethic = verdict.modality == "alethic"
        if alethic and verdict.verdict == "fail":
            has_alethic_fail = True
        if alethic and verdict.verdict == "unchecked":
            has_alethic_unchecked = True
        if verdict.verdict == "vacuous":
            has_vacuous = True
        index = index + 1
    return _band_of(has_alethic_fail, has_alethic_unchecked, has_vacuous)


def _band_of(
    has_alethic_fail: bool, has_alethic_unchecked: bool, has_vacuous: bool
) -> int:
    """N7's precedence, as a decision with its own proved home.

    Separated from the walk above deliberately. While the rule lived inside the
    scan, its only statable postcondition was the RANGE of the result, and a
    mutation that swapped two precedence arms satisfied that range and survived
    the proof gate (M04). A decision over three booleans can be constrained
    exactly, so the swap now has a contract to break.
    """
    if has_alethic_fail:
        return 1
    if has_alethic_unchecked:
        return 4
    if has_vacuous:
        return 2
    return 0


def decide_phase1_assurance(
    *, band: int, applicable: int, current: int, in_scope: bool
) -> tuple[SliceDecision, SliceAssurance]:
    """N9. Semantic decision and proof coverage are orthogonal (r2 D8)."""
    return _decision_of(band), _assurance_of(applicable, current, in_scope)


def _decision_of(band: int) -> SliceDecision:
    """N9's semantic half. Band 0 accepts, band 1 refuses, 2 and 4 decide
    nothing."""
    if band == 1:
        return "refuse"
    if band == 0:
        return "accept"
    return "indeterminate"


def _assurance_of(applicable: int, current: int, in_scope: bool) -> SliceAssurance:
    """N9's coverage half, orthogonal to the decision (r2 D8).

    Separated for the same measured reason as `_band_of`: a postcondition over
    one element of a returned TUPLE did not constrain that element at all, and
    the mutation that widened this conjunction to a disjunction survived the
    proof gate (M05). A scalar result can be constrained, so it is one.
    """
    if current <= 0 or applicable <= 0:
        return "none"
    if current >= applicable and in_scope:
        return "proof-backed"
    return "partial"


# --- bounded helpers, all inside the verifiable subset -------------------


def _violation(modality: SliceModality) -> SliceVerdictName:
    """N5. Modality decides fail versus warning and nothing else."""
    if modality == "alethic":
        return "fail"
    return "warning"


def _decided(
    value: SliceInput,
    verdict: SliceVerdictName,
    reason_code: str | None,
    witness: tuple[tuple[str, ...], ...],
) -> SliceVerdict:
    return SliceVerdict(
        value.constraint_ref, value.family, value.modality, verdict, reason_code, witness
    )


def _canonical_identities(values: tuple[str, ...], limit: int) -> bool:
    """N1: distinct String-primitive identities within a bound.

    DISTINCTNESS, not sortedness. N1's equality is exact Unicode-string
    equality, which is decidable here; the canonical ASCENDING order is an
    adapter obligation checked by an executable test, because the verifier this
    phase pins defines no ordering relation on strings at all (finding F10).
    Order is preserved through this predicate, never imposed by it.
    """
    if len(values) > limit:
        return False
    index = 0
    while index < len(values):
        if not isinstance(values[index], str):
            return False
        other = 0
        while other < index:
            if values[other] == values[index]:
                return False
            other = other + 1
        index = index + 1
    return True


def _players_come_from_the_universe(
    universe: tuple[str, ...], players: tuple[str, ...]
) -> bool:
    """N2: a player is an observed identity, so it is a universe member."""
    index = 0
    while index < len(players):
        if players[index] not in universe:
            return False
        index = index + 1
    return True


def _bounds_in_scope(minimum: int | None, maximum: int | None) -> bool:
    """N4 admits an inclusive bound with at least one finite end."""
    if minimum is None and maximum is None:
        return False
    if minimum is not None and not _admitted_bound_end(minimum):
        return False
    if maximum is not None and not _admitted_bound_end(maximum):
        return False
    return minimum is None or maximum is None or minimum <= maximum


def _admitted_bound_end(end: int) -> bool:
    """One end of an inclusive bound: a non-negative integer, never a bool."""
    return isinstance(end, int) and not isinstance(end, bool) and end >= 0


def _mandatory_witness(
    universe: tuple[str, ...], players: tuple[str, ...]
) -> tuple[tuple[str, ...], ...]:
    """N3. Exactly the universe members that play no mandatory role.

    Written as bounded case analysis over the two admitted members rather than
    as a set difference, because the bound is the thing that makes this slice
    provable and an unbounded loop would quietly discard it.
    """
    if len(universe) == 0:
        return ()
    if len(universe) == 1:
        if universe[0] in players:
            return ()
        return ((universe[0],),)
    first_missing = universe[0] not in players
    second_missing = universe[1] not in players
    if first_missing and second_missing:
        return ((universe[0],), (universe[1],))
    if first_missing:
        return ((universe[0],),)
    if second_missing:
        return ((universe[1],),)
    return ()


def _frequency_witness(
    groups: tuple[SliceGroup, ...], minimum: int | None, maximum: int | None
) -> tuple[tuple[str, ...], ...]:
    """N4. Exactly the occurring groups whose count leaves the inclusive bound."""
    if len(groups) == 0:
        return ()
    if len(groups) == 1:
        if _group_violates(groups[0], minimum, maximum):
            return (groups[0].key,)
        return ()
    first_violates = _group_violates(groups[0], minimum, maximum)
    second_violates = _group_violates(groups[1], minimum, maximum)
    if first_violates and second_violates:
        return (groups[0].key, groups[1].key)
    if first_violates:
        return (groups[0].key,)
    if second_violates:
        return (groups[1].key,)
    return ()


def _group_violates(group: SliceGroup, minimum: int | None, maximum: int | None) -> bool:
    """N4's inclusive test. A `min` binds an OCCURRING group only, and every
    group here occurs by construction."""
    if minimum is not None and group.count < minimum:
        return True
    return maximum is not None and group.count > maximum


# --- the verified gates the two bridges must pass through ----------------
#
# `gnd.proof_bridge` reads an admitted `Model`, `Population` and raw constraint
# fragments, and it returns the report's `dict[str, Any]`. Neither type is
# translatable, so neither bridge can be verified as written -- which is exactly
# why the SEMANTIC content of both is here instead. The bridges compute a
# candidate and then submit it: `admit_phase1_slice` returns the candidate only
# when a proved predicate says it preserves the observation's meaning, and
# `project_one_verdict` / `phase1_counts` / `phase1_acceptance_ready` decide
# every semantic field of the public payload before any dict exists. What is
# left in the bridges is extraction and container assembly, and the phase record
# states that residual rather than calling it proved.


@dataclass(frozen=True)
class ProjectedVerdict:
    """One public verdict row, decided (A14.2/A14.3) before any dict exists."""

    constraint_ref: str
    constraint_type: str
    modality: SliceModality
    verdict: SliceVerdictName
    reason_code: str | None
    witness: tuple[tuple[str, ...], ...]
    flatten_witness: bool


def admit_phase1_slice(
    candidate: SliceInput,
    universe_values: tuple[str, ...],
    player_values: tuple[str, ...],
    role_values: tuple[str, ...],
) -> SliceInput | None:
    """The verified admission gate -- O6's meaning-preservation, as a checker.

    The bridge canonicalizes; this function decides whether the canonicalization
    it produced actually says what the raw observation said, and the bridge may
    return only what this function returned. Refusal is a decision the evidence
    lane records as refusal-to-certify, never an absence (O7).

    The cardinality guards run FIRST, at constant cost. Finding F12: without
    them, an observation of 1,100 occurrences crashed the recursive occurrence
    counter with a RecursionError -- an exception from the function whose whole
    obligation is totality. An observation wider than the admitted slice can
    never match an in-scope candidate, so refusing it early changes no answer.
    """
    if len(candidate.universe) > MAX_UNIVERSE_MEMBERS:
        return None
    if len(candidate.players) > MAX_PLAYER_IDENTITIES:
        return None
    if len(candidate.groups) > MAX_FREQUENCY_GROUPS:
        return None
    if len(role_values) > MAX_FREQUENCY_GROUPS * MAX_GROUP_COUNT:
        return None
    if not _identities_are_canonical(candidate.universe, universe_values):
        return None
    if not _identities_are_canonical(candidate.players, player_values):
        return None
    if not _groups_are_canonical(candidate.groups, role_values):
        return None
    if not phase1_in_scope(candidate):
        return None
    return candidate


def _identities_are_canonical(
    canonical: tuple[str, ...], raw: tuple[str, ...]
) -> bool:
    """N1 over an observation: distinct, and set-equal to what was observed.

    Set equality in BOTH directions is the whole content -- one direction alone
    admits a canonicalization that dropped an identity, and the other admits one
    that invented one. Ascending ORDER is not stated here because the pinned
    verifier defines no ordering relation on strings at all (measured: `<` is
    `undefined.comparison`); order is the separately gated obligation M12 reds.
    """
    index = 0
    while index < len(canonical):
        if not (canonical[index] in raw):
            return False
        other = 0
        while other < index:
            if canonical[other] == canonical[index]:
                return False
            other = other + 1
        index = index + 1
    position = 0
    while position < len(raw):
        if not (raw[position] in canonical):
            return False
        position = position + 1
    return True


def _occurrences(values: tuple[str, ...], key: str, start: int) -> int:
    """How many times `key` occurs in `values` at or after `start` (N4).

    Recursive and side-effect free so a contract can name it: it is the
    DEFINITION of the count a group carries, not a second implementation of it.
    """
    if start == len(values):
        return 0
    rest = _occurrences(values, key, start + 1)
    if values[start] == key:
        return rest + 1
    return rest


def _groups_are_canonical(
    groups: tuple[SliceGroup, ...], raw: tuple[str, ...]
) -> bool:
    """N4 over an observation: one key each, exact counts, and nothing lost.

    Multiplicity survives only in the count, so the count must be the observed
    one -- M13 deduplicates occurrences and dies here. Every observed value must
    also reach some group, or a whole occurrence class went missing silently.

    A conjunction of the two recursive predicates below, and deliberately not a
    loop: stating the count obligation as a quantified formula over a recursive
    counter sent the pinned solver past the approved per-call cap (measured
    twice, in two phrasings), while the same obligation stated AS the predicates
    verifies in seconds because every proof step is one definition unfold. The
    executable meaning is untouched and the bounded enumeration and admission
    refusal gates hold it.
    """
    return _groups_counted(groups, raw, 0) and _raw_reaches_groups(groups, raw, 0)


def _groups_counted(
    groups: tuple[SliceGroup, ...], raw: tuple[str, ...], start: int
) -> bool:
    """Every group from `start` on: one key, the observed count, no duplicate."""
    if start == len(groups):
        return True
    group = groups[start]
    if len(group.key) != 1:
        return False
    if group.count != _occurrences(raw, group.key[0], 0):
        return False
    if not _key_absent(groups, group.key[0], start + 1):
        return False
    return _groups_counted(groups, raw, start + 1)


def _key_absent(groups: tuple[SliceGroup, ...], key: str, start: int) -> bool:
    """No group from `start` on carries `key` -- the distinctness half."""
    if start == len(groups):
        return True
    group = groups[start]
    if len(group.key) == 1 and group.key[0] == key:
        return False
    return _key_absent(groups, key, start + 1)


def _raw_reaches_groups(
    groups: tuple[SliceGroup, ...], raw: tuple[str, ...], start: int
) -> bool:
    """Every observed value from `start` on reached some group -- nothing lost."""
    if start == len(raw):
        return True
    if not _some_group_carries(groups, raw[start], 0):
        return False
    return _raw_reaches_groups(groups, raw, start + 1)


def _some_group_carries(groups: tuple[SliceGroup, ...], value: str, start: int) -> bool:
    """Whether an observed value reached a group at or after `start`.

    Recursive and side-effect free so a contract can name it directly: the
    quantified two-way-coverage obligations state this predicate rather than a
    nested existential, because the pinned verifier's solver diverges on the
    forall-exists form (measured: the same obligation phrased with `Exists`
    exceeded the per-call cap, and phrased with this predicate it verifies in
    seconds).
    """
    if start == len(groups):
        return False
    group = groups[start]
    if len(group.key) == 1 and group.key[0] == value:
        return True
    return _some_group_carries(groups, value, start + 1)


def phase1_counts(verdicts: tuple[SliceVerdict, ...]) -> tuple[int, ...]:
    """N8's `counts`, in `SLICE_VERDICT_NAMES` order, as ONE walk."""
    passes = 0
    fails = 0
    warnings = 0
    unchecked = 0
    vacuous = 0
    index = 0
    while index < len(verdicts):
        # Bound to a local BEFORE its attribute is read: measured, Nagini 1.3.1
        # crashes its own translator on an assignment whose right-hand side is an
        # attribute of a subscript (`verdicts[index].verdict`), and the crash is
        # a stack trace rather than a diagnostic.
        entry = verdicts[index]
        name = entry.verdict
        if name == "pass":
            passes = passes + 1
        if name == "fail":
            fails = fails + 1
        if name == "warning":
            warnings = warnings + 1
        if name == "unchecked":
            unchecked = unchecked + 1
        if name == "vacuous":
            vacuous = vacuous + 1
        index = index + 1
    return (passes, fails, warnings, unchecked, vacuous)


def _verdict_occurrences(
    verdicts: tuple[SliceVerdict, ...], name: str, start: int
) -> int:
    """The DEFINITION of a verdict-name count, for `phase1_counts` to meet."""
    if start == len(verdicts):
        return 0
    rest = _verdict_occurrences(verdicts, name, start + 1)
    if verdicts[start].verdict == name:
        return rest + 1
    return rest


def project_one_verdict(verdict: SliceVerdict) -> ProjectedVerdict:
    """N8 for one row, with A14.2's spelling and A14.3's shape decided HERE.

    The public `constraint_type` is the public family spelling, so a textual
    refusal keeps the frozen wire's `textual`; `reason_code` stays non-null only
    where production already defines it (F7); and whether the witness flattens
    is a decision about the family, not a shape the caller may choose.
    """
    return ProjectedVerdict(
        verdict.constraint_ref,
        _public_family(verdict.family),
        verdict.modality,
        verdict.verdict,
        verdict.reason_code if verdict.verdict == "unchecked" else None,
        verdict.witness,
        verdict.family == "mandatory",
    )


def _public_family(family: SliceFamily) -> str:
    """A14.2. `textual-refusal` is internal and reaches no projected field."""
    if family == "textual-refusal":
        return "textual"
    return family


def phase1_acceptance_ready(band: int) -> bool:
    """N8's last semantic field, so no caller can compute it a second way."""
    return band == 0
