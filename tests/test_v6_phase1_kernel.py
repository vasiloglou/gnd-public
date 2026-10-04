












from __future__ import annotations

import itertools
from typing import Any

import pytest

from gnd import proof_kernel
from gnd.proof_kernel import SliceGroup, SliceInput

MODALITIES = ("alethic", "deontic")
BOOLEANS = (False, True)
                                                                              
ATOMS = ("a1", "b2")


def _slice(**overrides: Any) -> SliceInput:
    base: dict[str, Any] = {
        "constraint_ref": "constraints[0]",
        "family": "mandatory",
        "modality": "alethic",
        "covered": True,
        "subject_has_facts": True,
        "universe": (),
        "players": (),
        "groups": (),
        "minimum": None,
        "maximum": None,
    }
    base.update(overrides)
    return SliceInput(**base)


def test_normative_clause_roster_is_exact() -> None:

    assert proof_kernel.SLICE_VERDICT_NAMES == ("pass", "fail", "warning", "unchecked", "vacuous")
    assert proof_kernel.SLICE_DECISIONS == ("accept", "refuse", "indeterminate")
    assert proof_kernel.SLICE_ASSURANCES == ("proof-backed", "partial", "none")
    assert proof_kernel.SLICE_REASON_CODES == (
        "coverage-omission",
        "empty-subject",
        "textual-not-mechanical",
    )
    assert proof_kernel.REFUSAL_REASON_CODES == (
        "out-of-scope-family",
        "out-of-scope-cardinality",
        "evidence-not-current",
    )
                                                                              
    assert proof_kernel.MAX_SLICE_CONSTRAINTS == 3
    assert proof_kernel.MAX_UNIVERSE_MEMBERS == 2
    assert proof_kernel.MAX_PLAYER_IDENTITIES == 2
    assert proof_kernel.MAX_FREQUENCY_GROUPS == 2
    assert proof_kernel.MAX_GROUP_COUNT == 3


def _canonical_tuples(limit: int) -> list[tuple[str, ...]]:

    return [
        tuple(sorted(chosen))
        for size in range(limit + 1)
        for chosen in itertools.combinations(ATOMS, size)
    ]


def test_mandatory_exhaustive_bounded_enumeration() -> None:


    checked = 0
    for universe in _canonical_tuples(2):
        for players in _canonical_tuples(2):
            if not set(players) <= set(universe):
                continue
            for covered, has_facts, modality in itertools.product(
                BOOLEANS, BOOLEANS, MODALITIES
            ):
                value = _slice(
                    modality=modality,
                    covered=covered,
                    subject_has_facts=has_facts,
                    universe=universe,
                    players=players,
                )
                assert proof_kernel.phase1_in_scope(value) is True
                verdict = proof_kernel.evaluate_phase1_slice(value)
                checked += 1
                if not covered:
                    assert (verdict.verdict, verdict.reason_code) == (
                        "vacuous",
                        "coverage-omission",
                    )
                    assert verdict.witness == ()
                    continue
                if not has_facts:
                    assert (verdict.verdict, verdict.reason_code) == ("vacuous", "empty-subject")
                    assert verdict.witness == ()
                    continue
                missing = tuple((atom,) for atom in sorted(set(universe) - set(players)))
                assert verdict.witness == missing
                assert verdict.reason_code is None
                if missing == ():
                    assert verdict.verdict == "pass"
                else:
                    assert verdict.verdict == ("fail" if modality == "alethic" else "warning")
    assert checked == 9 * 8                                                           


def _admitted_bounds() -> list[tuple[int | None, int | None]]:
    ends: tuple[int | None, ...] = (None, 0, 1, 2, 3)
    return [
        (minimum, maximum)
        for minimum, maximum in itertools.product(ends, ends)
        if not (minimum is None and maximum is None)
        and (minimum is None or maximum is None or minimum <= maximum)
    ]


def test_frequency_exhaustive_bounded_enumeration() -> None:


    group_shapes: list[tuple[SliceGroup, ...]] = [()]
    for count in range(1, 4):
        group_shapes.append((SliceGroup(("p1",), count),))
    for first, second in itertools.product(range(1, 4), range(1, 4)):
        group_shapes.append((SliceGroup(("p1",), first), SliceGroup(("q2",), second)))
    checked = 0
    for groups in group_shapes:
        for minimum, maximum in _admitted_bounds():
            for has_facts, modality in itertools.product(BOOLEANS, MODALITIES):
                value = _slice(
                    family="frequency",
                    modality=modality,
                    subject_has_facts=has_facts,
                    groups=groups,
                    minimum=minimum,
                    maximum=maximum,
                )
                assert proof_kernel.phase1_in_scope(value) is True
                verdict = proof_kernel.evaluate_phase1_slice(value)
                checked += 1
                if not has_facts:
                    assert (verdict.verdict, verdict.reason_code) == ("vacuous", "empty-subject")
                    continue
                violating = tuple(
                    group.key
                    for group in groups
                    if (minimum is not None and group.count < minimum)
                    or (maximum is not None and group.count > maximum)
                )
                assert verdict.witness == violating
                assert verdict.reason_code is None
                if violating == ():
                    assert verdict.verdict == "pass"
                else:
                    assert verdict.verdict == ("fail" if modality == "alethic" else "warning")
    assert checked == 13 * 18 * 4


def test_composition_exhaustive_verdict_tuples() -> None:

    options = [
        (name, modality)
        for name in proof_kernel.SLICE_VERDICT_NAMES
        for modality in MODALITIES
    ]
    checked = 0
    for length in range(4):
        for rows in itertools.product(options, repeat=length):
            verdicts = tuple(
                proof_kernel.SliceVerdict(f"constraints[{index}]", "mandatory", modality, name, None, ())
                for index, (name, modality) in enumerate(rows)
            )
            names = [(row.verdict, row.modality) for row in verdicts]
            if ("fail", "alethic") in names:
                expected = 1
            elif ("unchecked", "alethic") in names:
                expected = 4
            elif any(name == "vacuous" for name, _ in names):
                expected = 2
            else:
                expected = 0
            band = proof_kernel.compose_phase1_band(verdicts)
            assert band == expected, names
            decision, _ = proof_kernel.decide_phase1_assurance(
                band=band, applicable=1, current=1, in_scope=True
            )
            assert decision == {0: "accept", 1: "refuse"}.get(band, "indeterminate")
            checked += 1
    assert checked == 1 + 10 + 100 + 1000


@pytest.mark.parametrize(
    "hostile",
    [
        _slice(family="ring"),
        _slice(modality="advisory"),
        _slice(constraint_ref=""),
        _slice(universe=("a1", "a1")),
        _slice(universe=("a1", "b2", "c3")),
        _slice(players=("z9",)),
        _slice(family="frequency"),
        _slice(family="frequency", minimum=2, maximum=1),
        _slice(family="frequency", minimum=-1),
        _slice(family="frequency", minimum=True),
        _slice(family="frequency", minimum=1, groups=(SliceGroup(("p1", "p2"), 1),)),
        _slice(family="frequency", minimum=1, groups=(SliceGroup(("p1",), 4),)),
        _slice(family="frequency", minimum=1, groups=(SliceGroup(("z9",), 0),)),
        _slice(
            family="frequency",
            minimum=1,
            groups=(SliceGroup(("p1",), 1), SliceGroup(("p1",), 2)),
        ),
        _slice(family="mandatory", minimum=1),
        _slice(family="mandatory", groups=(SliceGroup(("p1",), 1),)),
        _slice(family="textual-refusal", modality="deontic"),
        _slice(family="textual-refusal", covered=False),
        _slice(family="textual-refusal", universe=("a1",)),
    ],
    ids=lambda value: "hostile",
)
def test_the_in_scope_predicate_refuses_without_raising(hostile: SliceInput) -> None:

    assert proof_kernel.phase1_in_scope(hostile) is False
    assert proof_kernel.phase1_decide(hostile) is None


def test_assurance_exhaustive_independent_enumeration() -> None:






    for applicable in range(4):
        for current in range(4):
            for in_scope in (False, True):
                _, assurance = proof_kernel.decide_phase1_assurance(
                    band=0, applicable=applicable, current=current, in_scope=in_scope
                )
                if current <= 0 or applicable <= 0:
                    expected = "none"
                elif current >= applicable and in_scope:
                    expected = "proof-backed"
                else:
                    expected = "partial"
                assert assurance == expected, (applicable, current, in_scope)
