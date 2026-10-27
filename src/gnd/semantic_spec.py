"""Executable v6 snapshot specifications, separate from production correspondence.

Clause authority is proof/v6/semantics/clauses.md, including its explicit
replacement edges. Phase 2 proof providers bind the exact executable ASTs in
this module. Importing this file requires no proof tool. These interfaces are
executable specification candidates; they are not production correspondence
or production-branch coverage claims.
"""

from dataclasses import replace

from gnd.constraint_families import FAMILIES, resolve_hook
from gnd.semantic_ir import IRConstraint, IRFactType, Scalar, SnapshotIR


def scalar_identical(left: Scalar, right: Scalar) -> bool:
    """NS-IDENT-1: temporal coordinates do not change raw string identity."""
    return left.identity_kind == right.identity_kind and left.token == right.token


def scalar_order(left: Scalar, right: Scalar) -> int:
    """NS-ORDER-2: -2 denotes incomparable, otherwise -1, 0 or 1."""
    if not left.ordered or not right.ordered or left.den <= 0 or right.den <= 0:
        return -2
    if left.kind != right.kind:
        return -2
    if (
        left.kind != "number"
        and left.kind != "date"
        and left.kind != "datetime-aware"
        and left.kind != "datetime-naive"
    ):
        return -2
    a = left.num * right.den
    b = right.num * left.den
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def scalar_member(value: Scalar, values: tuple[Scalar, ...]) -> bool:
    """NS-IDENT-1 membership, independent of scalar ordering coordinates."""
    index = 0
    while index < len(values):
        if scalar_identical(value, values[index]):
            return True
        index += 1
    return False


def scalar_range_state(
    value: Scalar,
    minimum: Scalar | None,
    maximum: Scalar | None,
    min_inclusive: bool,
    max_inclusive: bool,
) -> int:
    """NF-VALUE-RANGE-1: -1 undecided, 0 outside, 1 inside the range."""
    lower = 0
    upper = 0
    if minimum is not None:
        lower = scalar_order(value, minimum)
    if maximum is not None:
        upper = scalar_order(value, maximum)
    if lower == -2 or upper == -2:
        return -1
    if minimum is not None and not (
        lower > 0 or (min_inclusive and scalar_identical(value, minimum))
    ):
        return 0
    if maximum is not None and not (
        upper < 0 or (max_inclusive and scalar_identical(value, maximum))
    ):
        return 0
    return 1


def scalar_ranges_state(
    value: Scalar, ranges: tuple[tuple[Scalar | None, Scalar | None, bool, bool], ...]
) -> int:
    """NF-VALUE-RANGES-1: a deciding inclusion outranks an undecided range."""
    index = 0
    result = 0
    while index < len(ranges):
        state = scalar_range_state(
            value,
            ranges[index][0],
            ranges[index][1],
            ranges[index][2],
            ranges[index][3],
        )
        if state == 1:
            return 1
        if state == -1:
            result = -1
        index += 1
    return result


def value_cell_state(value: Scalar, constraint: IRConstraint) -> int:
    """NF-VALUE-ENUM/RANGE/RANGES-1: classify one represented occurrence."""
    variant = constraint.variant
    if variant == "enum" or variant == "enum-role":
        if scalar_member(value, constraint.allowed):
            return 1
        return 0
    if variant == "range" or variant == "range-role":
        if len(constraint.flags) < 4:
            return -1
        return scalar_range_state(
            value, constraint.minimum, constraint.maximum, constraint.flags[2], constraint.flags[3]
        )
    if variant == "ranges" or variant == "ranges-role":
        return scalar_ranges_state(value, constraint.ranges)
    return -1


def snapshot_roster_index(snapshot: SnapshotIR, object_type: str) -> int:
    """Return the first matching IR position, or -1 when absent."""
    index = 0
    while index < len(snapshot.rosters):
        if snapshot.rosters[index].object_type == object_type:
            return index
        index += 1
    return -1


def snapshot_fact_index(snapshot: SnapshotIR, fact_type: str) -> int:
    """Return the first matching IR position, or -1 when absent."""
    index = 0
    while index < len(snapshot.fact_types):
        if snapshot.fact_types[index].id == fact_type:
            return index
        index += 1
    return -1


def snapshot_relation_index(snapshot: SnapshotIR, fact_type: str) -> int:
    """Return the first matching IR position, or -1 when absent."""
    index = 0
    while index < len(snapshot.relations):
        if snapshot.relations[index].fact_type == fact_type:
            return index
        index += 1
    return -1


def fact_role_index(fact: IRFactType, role: str) -> int:
    """Return the first matching IR position, or -1 when absent."""
    index = 0
    while index < len(fact.roles):
        if fact.roles[index].name == role:
            return index
        index += 1
    return -1


def append_projected_cell(
    values: list[Scalar | None],
    rows: tuple[tuple[Scalar | None, ...], ...],
    column: int,
    index: int,
) -> None:
    """Extend an owned projection prefix by its next represented occurrence."""
    values.append(rows[index][column])


def project_optional_column(
    rows: tuple[tuple[Scalar | None, ...], ...], column: int
) -> tuple[bool, list[Scalar | None]]:
    """Project every occurrence; retain None cells and refuse malformed rows."""
    values: list[Scalar | None] = []
    if column < 0:
        return False, values
    index = 0
    while index < len(rows):
        if column >= len(rows[index]):
            refused: list[Scalar | None] = []
            return False, refused
        append_projected_cell(values, rows, column, index)
        index += 1
    return True, values


def scalar_member_before(value: Scalar, values: tuple[Scalar, ...], end: int) -> bool:
    """Identity membership before an exclusive index; outlying ends are clipped."""
    index = 0
    while index < len(values) and index < end:
        if scalar_identical(value, values[index]):
            return True
        index += 1
    return False


def row_identical(left: tuple[Scalar, ...], right: tuple[Scalar, ...]) -> bool:
    """NS-IDENT-1 lifted to tuples, preserving arity and component order."""
    if len(left) != len(right):
        return False
    index = 0
    while index < len(left):
        if not scalar_identical(left[index], right[index]):
            return False
        index += 1
    return True


def row_member(row: tuple[Scalar, ...], rows: tuple[tuple[Scalar, ...], ...]) -> bool:
    """Identity membership of a complete tuple, including the empty tuple."""
    index = 0
    while index < len(rows):
        if row_identical(row, rows[index]):
            return True
        index += 1
    return False


def scalar_list_member(value: Scalar, values: list[Scalar]) -> bool:
    """Identity membership in an owned list without changing its contents."""
    cursor = 0
    while cursor < len(values):
        if scalar_identical(value, values[cursor]):
            return True
        cursor += 1
    return False


def append_absent_value(
    result: list[Scalar],
    value: Scalar,
    players: tuple[Scalar, ...],
    universe: tuple[Scalar, ...],
    index: int,
) -> None:
    """Append a missing identity, preserving already-established input coverage.

    The proof copy checks player exclusion and processed-prefix coverage at
    the caller. These inputs name that contract; appending is the runtime step.
    """
    result.append(value)


def advance_missing_prefix(
    index: int,
    universe: tuple[Scalar, ...],
    players: tuple[Scalar, ...],
    result: list[Scalar],
) -> int:
    """Advance after handling the current identity; the proof checks coverage."""
    return index + 1


def missing_identities(universe: tuple[Scalar, ...], players: tuple[Scalar, ...]) -> list[Scalar]:
    """NF-MAND-1 set difference, retaining first occurrence before sorting.

    This collection primitive does not establish role resolution, applicability
    or canonical witness order; the family predicate must supply those steps.
    """
    result = []  # type: list[Scalar]
    index = 0
    while index < len(universe):
        if not scalar_member(universe[index], players) and not scalar_list_member(
            universe[index], result
        ):
            append_absent_value(result, universe[index], players, universe, index)
        index = advance_missing_prefix(index, universe, players, result)
    return result


def scalar_canonical_rank(value: Scalar) -> int:
    """NS-CANON-2 scalar kind order: boolean, number, string, null."""
    if value.identity_kind == "boolean":
        return 0
    if value.identity_kind == "number":
        return 1
    if value.identity_kind == "string":
        return 2
    if value.identity_kind == "null":
        return 3
    return 4


def scalar_canonical_less(left: Scalar, right: Scalar) -> bool:
    """Strict NS-CANON-2 order over represented scalar identities."""
    left_rank = scalar_canonical_rank(left)
    right_rank = scalar_canonical_rank(right)
    if left_rank != right_rank:
        return left_rank < right_rank
    if left.identity_kind == "boolean":
        return left.token == "false" and right.token != "false"
    if left.identity_kind == "number" and left.den > 0 and right.den > 0:
        return left.num * right.den < right.num * left.den
    return left.token < right.token


def canonical_insert(values: list[Scalar], value: Scalar) -> None:
    """Insert one distinct identity into an already canonical owned list."""
    index = 0
    while index < len(values) and not scalar_canonical_less(value, values[index]):
        index += 1
    values.insert(index, value)


def canonical_distinct(values: list[Scalar]) -> list[Scalar]:
    """Return one representative per identity in NS-CANON-2 order."""
    result: list[Scalar] = []
    index = 0
    while index < len(values):
        if not scalar_list_member(values[index], result):
            canonical_insert(result, values[index])
        index += 1
    return result


def mandatory_cursor(constraint: IRConstraint, snapshot: SnapshotIR) -> tuple[int, int, int, int]:
    """Resolve host fact, role column, relation and transitive roster positions."""
    if (
        constraint.family != "mandatory"
        or constraint.variant != "inline"
        or constraint.refused != ""
        or len(constraint.roles) != 1
        or constraint.fact_type not in snapshot.covers
    ):
        return -1, -1, -1, -1
    fact_position = snapshot_fact_index(snapshot, constraint.fact_type)
    relation_position = snapshot_relation_index(snapshot, constraint.fact_type)
    if fact_position < 0 or relation_position < 0:
        return -1, -1, -1, -1
    role_position = fact_role_index(snapshot.fact_types[fact_position], constraint.roles[0])
    if role_position < 0:
        return -1, -1, -1, -1
    object_type = snapshot.fact_types[fact_position].roles[role_position].object_type
    roster_position = snapshot_roster_index(snapshot, object_type)
    if roster_position < 0:
        return -1, -1, -1, -1
    return fact_position, role_position, relation_position, roster_position


def mandatory_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    """NF-MAND-1: -1 unchecked, 0 violated, 1 satisfied."""
    cursor = mandatory_cursor(constraint, snapshot)
    if cursor[0] < 0:
        return -1
    role_position = cursor[1]
    relation = snapshot.relations[cursor[2]]
    roster = snapshot.rosters[cursor[3]]
    universe: list[Scalar] = []
    player_values: list[Scalar] = []
    index = 0
    while index < len(roster.members):
        value = roster.members[index]
        if value is None:
            return -1
        universe.append(value)
        index += 1
    index = 0
    while index < len(relation.rows):
        if role_position >= len(relation.rows[index]):
            return -1
        player = relation.rows[index][role_position]
        if player is None:
            return -1
        player_values.append(player)
        index += 1
    if missing_identities(tuple(universe), tuple(player_values)):
        return 0
    return 1


def mandatory_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    """True exactly when the admitted, covered mandatory predicate is satisfied."""
    return mandatory_state(constraint, snapshot) == 1


def mandatory_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[Scalar]:
    """Every distinct missing player in NS-CANON-2 order, else no witness."""
    cursor = mandatory_cursor(constraint, snapshot)
    if cursor[0] < 0:
        return []
    role_position = cursor[1]
    relation = snapshot.relations[cursor[2]]
    roster = snapshot.rosters[cursor[3]]
    universe: list[Scalar] = []
    player_values: list[Scalar] = []
    index = 0
    while index < len(roster.members):
        value = roster.members[index]
        if value is None:
            return []
        universe.append(value)
        index += 1
    index = 0
    while index < len(relation.rows):
        if role_position >= len(relation.rows[index]):
            return []
        player = relation.rows[index][role_position]
        if player is None:
            return []
        player_values.append(player)
        index += 1
    missing = missing_identities(tuple(universe), tuple(player_values))
    return canonical_distinct(missing)


def mandatory_disjunctive_cursor(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[str, int, list[tuple[int, int]]]:
    """Resolve one shared subject roster and every covered role population."""
    empty: list[tuple[int, int]] = []
    if (
        constraint.family != "mandatory-disjunctive"
        or constraint.variant != "n-a"
        or constraint.refused != ""
        or len(constraint.role_refs) == 0
    ):
        return "", -1, empty
    shared_type = ""
    first = True
    positions: list[tuple[int, int]] = []
    index = 0
    while index < len(constraint.role_refs):
        fact_type = constraint.role_refs[index][0]
        role = constraint.role_refs[index][1]
        if fact_type not in snapshot.covers:
            return "", -1, empty
        fact_position = snapshot_fact_index(snapshot, fact_type)
        relation_position = snapshot_relation_index(snapshot, fact_type)
        if fact_position < 0 or relation_position < 0:
            return "", -1, empty
        role_position = fact_role_index(snapshot.fact_types[fact_position], role)
        if role_position < 0:
            return "", -1, empty
        object_type = snapshot.fact_types[fact_position].roles[role_position].object_type
        if first:
            shared_type = object_type
            first = False
        elif object_type != shared_type:
            return "", -1, empty
        positions.append((relation_position, role_position))
        index += 1
    roster_position = snapshot_roster_index(snapshot, shared_type)
    if roster_position < 0:
        return "", -1, empty
    return shared_type, roster_position, positions


def mandatory_disjunctive_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    """NF-MAND-DISJ-1: -1 unchecked, 0 violated, 1 inclusive-or satisfied."""
    cursor = mandatory_disjunctive_cursor(constraint, snapshot)
    if cursor[1] < 0:
        return -1
    roster = snapshot.rosters[cursor[1]]
    universe: list[Scalar] = []
    player_values: list[Scalar] = []
    index = 0
    while index < len(roster.members):
        value = roster.members[index]
        if value is None:
            return -1
        universe.append(value)
        index += 1
    role_index = 0
    while role_index < len(cursor[2]):
        relation = snapshot.relations[cursor[2][role_index][0]]
        role_position = cursor[2][role_index][1]
        row_index = 0
        while row_index < len(relation.rows):
            if role_position >= len(relation.rows[row_index]):
                return -1
            player = relation.rows[row_index][role_position]
            if player is None:
                return -1
            player_values.append(player)
            row_index += 1
        role_index += 1
    if missing_identities(tuple(universe), tuple(player_values)):
        return 0
    return 1


def mandatory_disjunctive_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    """True exactly when every shared-type member plays at least one named role."""
    return mandatory_disjunctive_state(constraint, snapshot) == 1


def mandatory_disjunctive_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[Scalar]:
    """Every member playing none of the named roles, in NS-CANON-2 order."""
    cursor = mandatory_disjunctive_cursor(constraint, snapshot)
    if cursor[1] < 0:
        return []
    roster = snapshot.rosters[cursor[1]]
    universe: list[Scalar] = []
    player_values: list[Scalar] = []
    index = 0
    while index < len(roster.members):
        value = roster.members[index]
        if value is None:
            return []
        universe.append(value)
        index += 1
    role_index = 0
    while role_index < len(cursor[2]):
        relation = snapshot.relations[cursor[2][role_index][0]]
        role_position = cursor[2][role_index][1]
        row_index = 0
        while row_index < len(relation.rows):
            if role_position >= len(relation.rows[row_index]):
                return []
            player = relation.rows[row_index][role_position]
            if player is None:
                return []
            player_values.append(player)
            row_index += 1
        role_index += 1
    missing = missing_identities(tuple(universe), tuple(player_values))
    return canonical_distinct(missing)


def row_list_member(row: tuple[Scalar, ...], rows: list[tuple[Scalar, ...]]) -> bool:
    """NS-IDENT-1 membership in an owned row list."""
    index = 0
    while index < len(rows):
        if row_identical(row, rows[index]):
            return True
        index += 1
    return False


def row_canonical_less(left: tuple[Scalar, ...], right: tuple[Scalar, ...]) -> bool:
    """Lexicographic NS-CANON-2 order, with a shorter equal prefix first."""
    index = 0
    while index < len(left) and index < len(right):
        if scalar_canonical_less(left[index], right[index]):
            return True
        if scalar_canonical_less(right[index], left[index]):
            return False
        index += 1
    return len(left) < len(right)


def canonical_distinct_rows(values: list[tuple[Scalar, ...]]) -> list[tuple[Scalar, ...]]:
    """Return one representative per row identity in canonical order."""
    result: list[tuple[Scalar, ...]] = []
    index = 0
    while index < len(values):
        value = values[index]
        if not row_list_member(value, result):
            position = 0
            while position < len(result) and not row_canonical_less(value, result[position]):
                position += 1
            result.insert(position, value)
        index += 1
    return result


def role_sequence_rows(
    sequence: tuple[tuple[str, str], ...], snapshot: SnapshotIR
) -> tuple[bool, list[tuple[Scalar, ...]]]:
    """NS-JOIN-1 projection or natural join for one role sequence."""
    result: list[tuple[Scalar, ...]] = []
    if len(sequence) == 0:
        return False, result
    fact_order: list[str] = []
    selected: dict[str, list[tuple[int, int]]] = {}
    fact_positions: dict[str, int] = {}
    relation_positions: dict[str, int] = {}
    slot = 0
    while slot < len(sequence):
        fact_type = sequence[slot][0]
        role = sequence[slot][1]
        fact_position = snapshot_fact_index(snapshot, fact_type)
        relation_position = snapshot_relation_index(snapshot, fact_type)
        if fact_position < 0 or relation_position < 0 or fact_type not in snapshot.covers:
            return False, result
        role_position = fact_role_index(snapshot.fact_types[fact_position], role)
        if role_position < 0:
            return False, result
        if fact_type not in selected:
            fact_order.append(fact_type)
            selected[fact_type] = []
            fact_positions[fact_type] = fact_position
            relation_positions[fact_type] = relation_position
        selected[fact_type].append((slot, role_position))
        slot += 1
    if len(fact_order) == 1:
        fact_type = fact_order[0]
        relation = snapshot.relations[relation_positions[fact_type]]
        row_index = 0
        while row_index < len(relation.rows):
            projected: list[Scalar] = []
            slot = 0
            while slot < len(sequence):
                role_position = selected[fact_type][slot][1]
                if role_position >= len(relation.rows[row_index]):
                    return False, result
                value = relation.rows[row_index][role_position]
                if value is None:
                    return False, result
                projected.append(value)
                slot += 1
            result.append(tuple(projected))
            row_index += 1
        return True, result
    anchors: dict[str, list[tuple[str, int]]] = {}
    fact_index = 0
    while fact_index < len(fact_order):
        fact_type = fact_order[fact_index]
        fact = snapshot.fact_types[fact_positions[fact_type]]
        selected_columns = [item[1] for item in selected[fact_type]]
        candidates: list[tuple[str, int]] = []
        role_index = 0
        while role_index < len(fact.roles):
            if role_index not in selected_columns:
                object_type = fact.roles[role_index].object_type
                candidate_index = 0
                while candidate_index < len(candidates):
                    if candidates[candidate_index][0] == object_type:
                        return False, result
                    candidate_index += 1
                candidates.append((object_type, role_index))
            role_index += 1
        anchors[fact_type] = candidates
        fact_index += 1
    connected = [fact_order[0]]
    remaining = fact_order[1:]
    changed = True
    while changed and remaining:
        changed = False
        index = 0
        while index < len(remaining):
            candidate = remaining[index]
            linked = False
            left_index = 0
            while left_index < len(anchors[candidate]):
                member_index = 0
                while member_index < len(connected):
                    right_index = 0
                    while right_index < len(anchors[connected[member_index]]):
                        if (
                            anchors[candidate][left_index][0]
                            == anchors[connected[member_index]][right_index][0]
                        ):
                            linked = True
                        right_index += 1
                    member_index += 1
                left_index += 1
            if linked:
                connected.append(candidate)
                remaining.pop(index)
                changed = True
            else:
                index += 1
    if remaining:
        return False, result
    initial_outputs: list[Scalar | None] = []
    slot = 0
    while slot < len(sequence):
        initial_outputs.append(None)
        slot += 1
    joined: list[tuple[dict[str, Scalar], list[Scalar | None]]] = [({}, initial_outputs)]
    fact_index = 0
    while fact_index < len(fact_order):
        fact_type = fact_order[fact_index]
        relation = snapshot.relations[relation_positions[fact_type]]
        next_joined: list[tuple[dict[str, Scalar], list[Scalar | None]]] = []
        joined_index = 0
        while joined_index < len(joined):
            row_index = 0
            while row_index < len(relation.rows):
                row = relation.rows[row_index]
                merged = dict(joined[joined_index][0])
                outputs = list(joined[joined_index][1])
                compatible = True
                anchor_index = 0
                while anchor_index < len(anchors[fact_type]):
                    object_type = anchors[fact_type][anchor_index][0]
                    column = anchors[fact_type][anchor_index][1]
                    if column >= len(row) or row[column] is None:
                        return False, result
                    anchor_value = row[column]
                    if object_type in merged and not scalar_identical(
                        merged[object_type], anchor_value
                    ):
                        compatible = False
                    else:
                        merged[object_type] = anchor_value
                    anchor_index += 1
                selected_index = 0
                while selected_index < len(selected[fact_type]):
                    output_slot = selected[fact_type][selected_index][0]
                    column = selected[fact_type][selected_index][1]
                    if column >= len(row) or row[column] is None:
                        return False, result
                    outputs[output_slot] = row[column]
                    selected_index += 1
                if compatible:
                    next_joined.append((merged, outputs))
                row_index += 1
            joined_index += 1
        joined = next_joined
        fact_index += 1
    joined_index = 0
    while joined_index < len(joined):
        projected = []  # type: list[Scalar]
        slot = 0
        while slot < len(joined[joined_index][1]):
            value = joined[joined_index][1][slot]
            if value is None:
                return False, result
            projected.append(value)
            slot += 1
        result.append(tuple(projected))
        joined_index += 1
    return True, result


def set_family_rows(
    constraint: IRConstraint, snapshot: SnapshotIR, family: str
) -> tuple[bool, list[tuple[Scalar, ...]], list[tuple[Scalar, ...]]]:
    """Resolve the two sequences shared by subset, equality and exclusion."""
    empty: list[tuple[Scalar, ...]] = []
    if constraint.family != family or constraint.refused != "" or len(constraint.sequences) != 2:
        return False, empty, empty
    if constraint.variant != "single" and constraint.variant != "joined":
        return False, empty, empty
    sequence_index = 0
    has_joined_sequence = False
    while sequence_index < len(constraint.sequences):
        fact_types: list[str] = []
        reference_index = 0
        while reference_index < len(constraint.sequences[sequence_index]):
            fact_type = constraint.sequences[sequence_index][reference_index][0]
            if fact_type not in fact_types:
                fact_types.append(fact_type)
            reference_index += 1
        if constraint.variant == "single" and len(fact_types) != 1:
            return False, empty, empty
        if len(fact_types) >= 2:
            has_joined_sequence = True
        sequence_index += 1
    if constraint.variant == "joined" and not has_joined_sequence:
        return False, empty, empty
    left_ok, left = role_sequence_rows(constraint.sequences[0], snapshot)
    right_ok, right = role_sequence_rows(constraint.sequences[1], snapshot)
    if not left_ok or not right_ok:
        return False, empty, empty
    return True, canonical_distinct_rows(left), canonical_distinct_rows(right)


def subset_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    """NF-SUBSET-1: -1 unchecked, 0 violated, 1 subset."""
    valid, subset_rows, superset_rows = set_family_rows(constraint, snapshot, "subset")
    if not valid:
        return -1
    index = 0
    while index < len(subset_rows):
        if not row_list_member(subset_rows[index], superset_rows):
            return 0
        index += 1
    return 1


def subset_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return subset_state(constraint, snapshot) == 1


def subset_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    valid, subset_rows, superset_rows = set_family_rows(constraint, snapshot, "subset")
    result: list[list[Scalar]] = []
    if not valid:
        return result
    index = 0
    while index < len(subset_rows):
        if not row_list_member(subset_rows[index], superset_rows):
            result.append(list(subset_rows[index]))
        index += 1
    return result


def equality_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    """NF-EQUALITY-1: -1 unchecked, 0 unequal, 1 equal."""
    valid, left, right = set_family_rows(constraint, snapshot, "equality")
    if not valid:
        return -1
    index = 0
    while index < len(left):
        if not row_list_member(left[index], right):
            return 0
        index += 1
    index = 0
    while index < len(right):
        if not row_list_member(right[index], left):
            return 0
        index += 1
    return 1


def equality_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return equality_state(constraint, snapshot) == 1


def equality_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    valid, left, right = set_family_rows(constraint, snapshot, "equality")
    result: list[list[Scalar]] = []
    if not valid:
        return result
    index = 0
    while index < len(left):
        if not row_list_member(left[index], right):
            result.append(list(left[index]))
        index += 1
    index = 0
    while index < len(right):
        if not row_list_member(right[index], left):
            result.append(list(right[index]))
        index += 1
    return result


def exclusion_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    """NF-EXCLUSION-1: -1 unchecked, 0 overlapping, 1 disjoint."""
    valid, left, right = set_family_rows(constraint, snapshot, "exclusion")
    if not valid:
        return -1
    index = 0
    while index < len(left):
        if row_list_member(left[index], right):
            return 0
        index += 1
    return 1


def exclusion_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return exclusion_state(constraint, snapshot) == 1


def exclusion_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    valid, left, right = set_family_rows(constraint, snapshot, "exclusion")
    result: list[list[Scalar]] = []
    if not valid:
        return result
    index = 0
    while index < len(left):
        if row_list_member(left[index], right):
            result.append(list(left[index]))
        index += 1
    return result


def exclusive_or_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """NF-XOR-SINGLE/MULTI-1 state and exact ordered witness."""
    witness: list[list[Scalar]] = []
    if (
        constraint.family != "exclusive-or"
        or constraint.refused != ""
        or len(constraint.sequences) < 2
    ):
        return -1, witness
    populations: list[list[tuple[Scalar, ...]]] = []
    sequence_index = 0
    while sequence_index < len(constraint.sequences):
        valid, rows = role_sequence_rows(constraint.sequences[sequence_index], snapshot)
        if not valid:
            return -1, witness
        populations.append(canonical_distinct_rows(rows))
        sequence_index += 1
    single_role = True
    sequence_index = 0
    while sequence_index < len(constraint.sequences):
        if len(constraint.sequences[sequence_index]) != 1:
            single_role = False
        sequence_index += 1
    if single_role and constraint.variant != "single-role":
        return -1, witness
    if not single_role and constraint.variant != "multi-role":
        return -1, witness
    if not single_role:
        combined: list[tuple[Scalar, ...]] = []
        sequence_index = 0
        while sequence_index < len(populations):
            combined.extend(populations[sequence_index])
            sequence_index += 1
        candidates = canonical_distinct_rows(combined)
        candidate_index = 0
        while candidate_index < len(candidates):
            count = 0
            sequence_index = 0
            while sequence_index < len(populations):
                if row_list_member(candidates[candidate_index], populations[sequence_index]):
                    count += 1
                sequence_index += 1
            if count >= 2:
                witness.append(list(candidates[candidate_index]))
            candidate_index += 1
        if witness:
            return 0, witness
        return -1, witness
    shared_type = ""
    sequence_index = 0
    while sequence_index < len(constraint.sequences):
        reference = constraint.sequences[sequence_index][0]
        fact_position = snapshot_fact_index(snapshot, reference[0])
        if fact_position < 0:
            return -1, witness
        role_position = fact_role_index(snapshot.fact_types[fact_position], reference[1])
        if role_position < 0:
            return -1, witness
        object_type = snapshot.fact_types[fact_position].roles[role_position].object_type
        if sequence_index == 0:
            shared_type = object_type
        elif object_type != shared_type:
            return -1, witness
        sequence_index += 1
    roster_position = snapshot_roster_index(snapshot, shared_type)
    if roster_position < 0:
        return -1, witness
    both: list[Scalar] = []
    neither: list[Scalar] = []
    member_index = 0
    while member_index < len(snapshot.rosters[roster_position].members):
        member = snapshot.rosters[roster_position].members[member_index]
        if member is None:
            return -1, []
        count = 0
        sequence_index = 0
        while sequence_index < len(populations):
            if row_list_member((member,), populations[sequence_index]):
                count += 1
            sequence_index += 1
        if count >= 2:
            both.append(member)
        elif count == 0:
            neither.append(member)
        member_index += 1
    both = canonical_distinct(both)
    neither = canonical_distinct(neither)
    member_index = 0
    while member_index < len(both):
        witness.append([both[member_index]])
        member_index += 1
    member_index = 0
    while member_index < len(neither):
        witness.append([neither[member_index]])
        member_index += 1
    if witness:
        return 0, witness
    return 1, witness


def exclusive_or_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return exclusive_or_result(constraint, snapshot)[0]


def exclusive_or_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return exclusive_or_state(constraint, snapshot) == 1


def exclusive_or_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return exclusive_or_result(constraint, snapshot)[1]


def count_bound_integer(bound: Scalar | None) -> int:
    """Return -2 for absent, -1 for invalid, or a nonnegative integer bound."""
    if bound is None:
        return -2
    if (
        bound.kind != "number"
        or bound.identity_kind != "number"
        or bound.den <= 0
        or bound.num < 0
        or bound.num % bound.den != 0
    ):
        return -1
    return bound.num // bound.den


def count_interval_state(count: int, minimum: Scalar | None, maximum: Scalar | None) -> int:
    """Classify one finite count against optional inclusive integral bounds."""
    low = count_bound_integer(minimum)
    high = count_bound_integer(maximum)
    if count < 0 or low == -1 or high == -1 or (low >= 0 and high >= 0 and low > high):
        return -1
    if low >= 0 and count < low:
        return 0
    if high >= 0 and count > high:
        return 0
    return 1


def fact_projection_rows(
    fact_type: str, roles: tuple[str, ...], snapshot: SnapshotIR
) -> tuple[bool, list[tuple[Scalar, ...]], list[tuple[Scalar, ...]]]:
    """Project complete covered facts while retaining their full source rows."""
    projected: list[tuple[Scalar, ...]] = []
    full: list[tuple[Scalar, ...]] = []
    if fact_type not in snapshot.covers or len(roles) == 0:
        return False, projected, full
    fact_position = snapshot_fact_index(snapshot, fact_type)
    relation_position = snapshot_relation_index(snapshot, fact_type)
    if fact_position < 0 or relation_position < 0:
        return False, projected, full
    fact = snapshot.fact_types[fact_position]
    columns: list[int] = []
    role_index = 0
    while role_index < len(roles):
        column = fact_role_index(fact, roles[role_index])
        if column < 0:
            return False, [], []
        columns.append(column)
        role_index += 1
    relation = snapshot.relations[relation_position]
    row_index = 0
    while row_index < len(relation.rows):
        row = relation.rows[row_index]
        if len(row) != len(fact.roles):
            return False, [], []
        complete: list[Scalar] = []
        column = 0
        while column < len(row):
            if row[column] is None:
                return False, [], []
            complete.append(row[column])
            column += 1
        key: list[Scalar] = []
        role_index = 0
        while role_index < len(columns):
            key.append(complete[columns[role_index]])
            role_index += 1
        projected.append(tuple(key))
        full.append(tuple(complete))
        row_index += 1
    return True, projected, full


def counting_projection_rows(
    constraint: IRConstraint, snapshot: SnapshotIR, family: str
) -> tuple[bool, list[tuple[Scalar, ...]], list[tuple[Scalar, ...]]]:
    """Resolve inline/internal or external counting inputs with multiplicity."""
    if constraint.family != family or constraint.refused != "":
        return False, [], []
    if (family == "uniqueness" and constraint.variant == "inline") or (
        family == "frequency" and constraint.variant == "internal"
    ):
        return fact_projection_rows(constraint.fact_type, constraint.roles, snapshot)
    if constraint.variant != "external" or len(constraint.role_refs) == 0:
        return False, [], []
    valid, rows = role_sequence_rows(constraint.role_refs, snapshot)
    return valid, rows, []


def uniqueness_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """NF-UC-INTERNAL/EXTERNAL-1 state and exhaustive witness."""
    valid, keys, facts = counting_projection_rows(constraint, snapshot, "uniqueness")
    witness: list[list[Scalar]] = []
    if not valid:
        return -1, witness
    groups = canonical_distinct_rows(keys)
    group_index = 0
    while group_index < len(groups):
        count = 0
        row_index = 0
        while row_index < len(keys):
            if row_identical(groups[group_index], keys[row_index]):
                count += 1
            row_index += 1
        if count >= 2:
            if constraint.variant == "external":
                witness.append(list(groups[group_index]))
            else:
                row_index = 0
                while row_index < len(keys):
                    if row_identical(groups[group_index], keys[row_index]):
                        witness.append(list(facts[row_index]))
                    row_index += 1
        group_index += 1
    if witness:
        return 0, witness
    return 1, witness


def uniqueness_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return uniqueness_result(constraint, snapshot)[0]


def uniqueness_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return uniqueness_state(constraint, snapshot) == 1


def uniqueness_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return uniqueness_result(constraint, snapshot)[1]


def frequency_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """NF-FREQ-INTERNAL/EXTERNAL-1 over occurring duplicate-preserving groups."""
    valid, keys, _ = counting_projection_rows(constraint, snapshot, "frequency")
    witness: list[list[Scalar]] = []
    if not valid or count_interval_state(0, constraint.minimum, constraint.maximum) == -1:
        return -1, witness
    groups = canonical_distinct_rows(keys)
    group_index = 0
    while group_index < len(groups):
        count = 0
        row_index = 0
        while row_index < len(keys):
            if row_identical(groups[group_index], keys[row_index]):
                count += 1
            row_index += 1
        if count_interval_state(count, constraint.minimum, constraint.maximum) == 0:
            witness.append(list(groups[group_index]))
        group_index += 1
    if witness:
        return 0, witness
    return 1, witness


def frequency_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return frequency_result(constraint, snapshot)[0]


def frequency_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return frequency_state(constraint, snapshot) == 1


def frequency_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return frequency_result(constraint, snapshot)[1]


def cardinality_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """NF-CARD-OBJECT/ROLE-1 distinct count and counted-member witness."""
    witness: list[list[Scalar]] = []
    rows: list[tuple[Scalar, ...]] = []
    if constraint.family != "cardinality" or constraint.refused != "":
        return -1, witness
    if constraint.variant == "object":
        roster_position = snapshot_roster_index(snapshot, constraint.object_type)
        if roster_position < 0:
            return -1, witness
        member_index = 0
        while member_index < len(snapshot.rosters[roster_position].members):
            member = snapshot.rosters[roster_position].members[member_index]
            if member is None:
                return -1, []
            rows.append((member,))
            member_index += 1
    elif constraint.variant == "role" and len(constraint.role_refs) == 1:
        valid, projected = role_sequence_rows((constraint.role_refs[0],), snapshot)
        if not valid:
            return -1, witness
        rows = projected
    else:
        return -1, witness
    distinct = canonical_distinct_rows(rows)
    state = count_interval_state(len(distinct), constraint.minimum, constraint.maximum)
    if state != 0:
        return state, witness
    row_index = 0
    while row_index < len(distinct):
        witness.append(list(distinct[row_index]))
        row_index += 1
    return 0, witness


def cardinality_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return cardinality_result(constraint, snapshot)[0]


def cardinality_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return cardinality_state(constraint, snapshot) == 1


def cardinality_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return cardinality_result(constraint, snapshot)[1]


def snapshot_object_type_index(snapshot: SnapshotIR, object_type: str) -> int:
    """Return the first matching object-type declaration position, or -1."""
    index = 0
    while index < len(snapshot.object_types):
        if snapshot.object_types[index].id == object_type:
            return index
        index += 1
    return -1


def subtype_partition_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """NF-PARTITION-2/4/5 state and ordered exhaustive witness."""
    witness: list[list[Scalar]] = []
    if (
        constraint.family != "subtype-partition"
        or constraint.refused != ""
        or len(constraint.flags) < 2
        or len(constraint.subtypes) == 0
    ):
        return -1, witness
    exclusive = constraint.flags[0]
    exhaustive = constraint.flags[1]
    expected_variant = (
        "both"
        if exclusive and exhaustive
        else "exclusive"
        if exclusive
        else "exhaustive"
        if exhaustive
        else "n-a"
    )
    if constraint.variant != expected_variant or expected_variant == "n-a":
        return -1, witness
    supertype_position = snapshot_object_type_index(snapshot, constraint.object_type)
    universe_position = snapshot_roster_index(snapshot, constraint.object_type)
    if supertype_position < 0 or universe_position < 0:
        return -1, witness
    declared_subtypes = snapshot.object_types[supertype_position].subtypes
    populations: list[list[Scalar]] = []
    subtype_index = 0
    while subtype_index < len(constraint.subtypes):
        subtype = constraint.subtypes[subtype_index]
        if subtype not in declared_subtypes:
            return -1, witness
        object_position = snapshot_object_type_index(snapshot, subtype)
        roster_position = snapshot_roster_index(snapshot, subtype)
        if object_position < 0 or roster_position < 0:
            return -1, witness
        members: list[Scalar] = []
        member_index = 0
        while member_index < len(snapshot.rosters[roster_position].members):
            member = snapshot.rosters[roster_position].members[member_index]
            if member is None:
                return -1, []
            members.append(member)
            member_index += 1
        object_type = snapshot.object_types[object_position]
        if (
            object_type.derivation in ("derived", "semiderived")
            and object_type.opaque_rule != ""
            and len(members) == 0
        ):
            return -1, witness
        populations.append(canonical_distinct(members))
        subtype_index += 1
    universe_values: list[Scalar] = []
    member_index = 0
    while member_index < len(snapshot.rosters[universe_position].members):
        member = snapshot.rosters[universe_position].members[member_index]
        if member is None:
            return -1, []
        universe_values.append(member)
        member_index += 1
    universe = canonical_distinct(universe_values)
    both: list[Scalar] = []
    neither: list[Scalar] = []
    member_index = 0
    while member_index < len(universe):
        count = 0
        subtype_index = 0
        while subtype_index < len(populations):
            if scalar_list_member(universe[member_index], populations[subtype_index]):
                count += 1
            subtype_index += 1
        if exclusive and count >= 2:
            both.append(universe[member_index])
        if exhaustive and count == 0:
            neither.append(universe[member_index])
        member_index += 1
    member_index = 0
    while member_index < len(both):
        witness.append([both[member_index]])
        member_index += 1
    member_index = 0
    while member_index < len(neither):
        witness.append([neither[member_index]])
        member_index += 1
    if witness:
        return 0, witness
    return 1, witness


def subtype_partition_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return subtype_partition_result(constraint, snapshot)[0]


def subtype_partition_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return subtype_partition_state(constraint, snapshot) == 1


def subtype_partition_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return subtype_partition_result(constraint, snapshot)[1]


def ring_pair_member(pair: tuple[Scalar, ...], pairs: list[tuple[Scalar, ...]]) -> bool:
    """Exact identity membership in a ring pair set."""
    return row_list_member(pair, pairs)


def ring_cycle_witness(pairs: list[tuple[Scalar, ...]]) -> list[Scalar]:
    """NF-RING-ACYCLIC-1 deterministic forward cycle, or empty when acyclic."""
    values: list[Scalar] = []
    pair_index = 0
    while pair_index < len(pairs):
        if len(pairs[pair_index]) != 2:
            return []
        values.append(pairs[pair_index][0])
        values.append(pairs[pair_index][1])
        pair_index += 1
    nodes = canonical_distinct(values)
    adjacency: list[list[int]] = []
    node_index = 0
    while node_index < len(nodes):
        adjacency.append([])
        node_index += 1
    pair_index = 0
    while pair_index < len(pairs):
        source = -1
        target = -1
        node_index = 0
        while node_index < len(nodes):
            if scalar_identical(pairs[pair_index][0], nodes[node_index]):
                source = node_index
            if scalar_identical(pairs[pair_index][1], nodes[node_index]):
                target = node_index
            node_index += 1
        if source < 0 or target < 0:
            return []
        adjacency[source].append(target)
        pair_index += 1
    colors: list[int] = []
    parents: list[int] = []
    node_index = 0
    while node_index < len(nodes):
        colors.append(0)
        parents.append(-1)
        node_index += 1
    start = 0
    while start < len(nodes):
        if colors[start] != 0:
            start += 1
            continue
        colors[start] = 1
        stack: list[tuple[int, int]] = [(start, 0)]
        while stack:
            node = stack[-1][0]
            successor_index = stack[-1][1]
            if successor_index >= len(adjacency[node]):
                colors[node] = 2
                stack.pop()
                continue
            successor = adjacency[node][successor_index]
            stack[-1] = (node, successor_index + 1)
            if colors[successor] == 0:
                colors[successor] = 1
                parents[successor] = node
                stack.append((successor, 0))
            elif colors[successor] == 1:
                indexes = [node]
                while indexes[-1] != successor:
                    parent = parents[indexes[-1]]
                    if parent < 0:
                        return []
                    indexes.append(parent)
                cycle: list[Scalar] = []
                index = len(indexes) - 1
                while index >= 0:
                    cycle.append(nodes[indexes[index]])
                    index -= 1
                cycle.append(nodes[successor])
                return cycle
        start += 1
    return []


def ring_component_witness(
    component: str, pairs: list[tuple[Scalar, ...]]
) -> list[tuple[Scalar, ...]]:
    """Exhaustive primitive ring witnesses, except one sound acyclic cycle."""
    violations: list[tuple[Scalar, ...]] = []
    if component == "acyclic":
        cycle = ring_cycle_witness(pairs)
        if cycle:
            violations.append(tuple(cycle))
        return violations
    if component == "reflexive":
        domain_values: list[Scalar] = []
        pair_index = 0
        while pair_index < len(pairs):
            domain_values.append(pairs[pair_index][0])
            pair_index += 1
        domain = canonical_distinct(domain_values)
        node_index = 0
        while node_index < len(domain):
            if not ring_pair_member((domain[node_index], domain[node_index]), pairs):
                violations.append((domain[node_index],))
            node_index += 1
        return violations
    pair_index = 0
    while pair_index < len(pairs):
        left = pairs[pair_index][0]
        right = pairs[pair_index][1]
        reverse = ring_pair_member((right, left), pairs)
        same = scalar_identical(left, right)
        if (
            (component == "irreflexive" and same)
            or (component == "asymmetric" and reverse)
            or (component == "antisymmetric" and not same and reverse)
            or (component == "symmetric" and not reverse)
            or (component == "purely-reflexive" and not same)
        ):
            violations.append((left, right))
        elif component == "intransitive" or component == "transitive":
            next_index = 0
            while next_index < len(pairs):
                if scalar_identical(right, pairs[next_index][0]):
                    closing = ring_pair_member((left, pairs[next_index][1]), pairs)
                    if (component == "intransitive" and closing) or (
                        component == "transitive" and not closing
                    ):
                        violations.append((left, right, pairs[next_index][1]))
                next_index += 1
        pair_index += 1
    return violations


def ring_result(constraint: IRConstraint, snapshot: SnapshotIR) -> tuple[int, list[list[Scalar]]]:
    """NF-RING primitive and NF-RING-SHAPE-2 combined result."""
    witness: list[list[Scalar]] = []
    variants = (
        "irreflexive",
        "asymmetric",
        "antisymmetric",
        "symmetric",
        "intransitive",
        "transitive",
        "acyclic",
        "purely-reflexive",
        "reflexive",
        "asymmetric-intransitive",
        "acyclic-intransitive",
        "symmetric-irreflexive",
        "symmetric-intransitive",
    )
    if (
        constraint.family != "ring"
        or constraint.variant not in variants
        or constraint.refused != ""
        or constraint.fact_type not in snapshot.covers
    ):
        return -1, witness
    fact_position = snapshot_fact_index(snapshot, constraint.fact_type)
    relation_position = snapshot_relation_index(snapshot, constraint.fact_type)
    if fact_position < 0 or relation_position < 0:
        return -1, witness
    if len(snapshot.fact_types[fact_position].roles) != 2:
        return -1, witness
    source_pairs: list[tuple[Scalar, ...]] = []
    row_index = 0
    while row_index < len(snapshot.relations[relation_position].rows):
        row = snapshot.relations[relation_position].rows[row_index]
        if len(row) != 2 or row[0] is None or row[1] is None:
            return -1, []
        source_pairs.append((row[0], row[1]))
        row_index += 1
    pairs = canonical_distinct_rows(source_pairs)
    components = (
        ("asymmetric", "intransitive")
        if constraint.variant == "asymmetric-intransitive"
        else ("acyclic", "intransitive")
        if constraint.variant == "acyclic-intransitive"
        else ("symmetric", "irreflexive")
        if constraint.variant == "symmetric-irreflexive"
        else ("symmetric", "intransitive")
        if constraint.variant == "symmetric-intransitive"
        else (constraint.variant,)
    )
    component_index = 0
    while component_index < len(components):
        violations = ring_component_witness(components[component_index], pairs)
        violation_index = 0
        while violation_index < len(violations):
            witness.append(list(violations[violation_index]))
            violation_index += 1
        component_index += 1
    if witness:
        return 0, witness
    return 1, witness


def ring_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return ring_result(constraint, snapshot)[0]


def ring_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return ring_state(constraint, snapshot) == 1


def ring_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return ring_result(constraint, snapshot)[1]


def guarded_name_index(names: tuple[str, ...], variable: str) -> int:
    """Return a guarded variable's first-introduction position."""
    index = 0
    while index < len(names):
        if names[index] == variable:
            return index
        index += 1
    return -1


def guarded_variable_names(constraint: IRConstraint) -> tuple[str, ...]:
    """NF-GUARDED-1 variable order from antecedent first introduction."""
    names: list[str] = []
    atom_index = 0
    while atom_index < len(constraint.antecedent):
        term_index = 0
        while term_index < len(constraint.antecedent[atom_index].bindings):
            term = constraint.antecedent[atom_index].bindings[term_index][1]
            if term.kind == "variable" and term.variable not in names:
                names.append(term.variable)
            term_index += 1
        atom_index += 1
    return tuple(names)


def guarded_bindings(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[bool, tuple[str, ...], list[tuple[Scalar, ...]]]:
    """Conjunctively join antecedent atoms by exact variable identity."""
    names = guarded_variable_names(constraint)
    initial: list[Scalar | None] = []
    while len(initial) < len(names):
        initial.append(None)
    bindings: list[list[Scalar | None]] = [initial]
    atom_index = 0
    while atom_index < len(constraint.antecedent):
        atom = constraint.antecedent[atom_index]
        fact_position = snapshot_fact_index(snapshot, atom.fact_type)
        relation_position = snapshot_relation_index(snapshot, atom.fact_type)
        if fact_position < 0 or relation_position < 0:
            return False, names, []
        fact = snapshot.fact_types[fact_position]
        relation = snapshot.relations[relation_position]
        if len(atom.bindings) != len(fact.roles):
            return False, names, []
        joined: list[list[Scalar | None]] = []
        binding_index = 0
        while binding_index < len(bindings):
            row_index = 0
            while row_index < len(relation.rows):
                row = relation.rows[row_index]
                if len(row) != len(fact.roles) or any(value is None for value in row):
                    return False, names, []
                candidate = list(bindings[binding_index])
                matches = True
                term_index = 0
                while term_index < len(atom.bindings):
                    role, term = atom.bindings[term_index]
                    column = fact_role_index(fact, role)
                    if column < 0 or row[column] is None or not term.valid:
                        return False, names, []
                    value = row[column]
                    if term.kind == "literal":
                        if term.literal is None or not scalar_identical(value, term.literal):
                            matches = False
                    elif term.kind == "variable":
                        position = guarded_name_index(names, term.variable)
                        if position < 0:
                            return False, names, []
                        if candidate[position] is None:
                            candidate[position] = value
                        elif not scalar_identical(candidate[position], value):
                            matches = False
                    else:
                        return False, names, []
                    term_index += 1
                if matches:
                    joined.append(candidate)
                row_index += 1
            binding_index += 1
        bindings = joined
        atom_index += 1
    rows: list[tuple[Scalar, ...]] = []
    binding_index = 0
    while binding_index < len(bindings):
        if any(value is None for value in bindings[binding_index]):
            return False, names, []
        rows.append(tuple(value for value in bindings[binding_index] if value is not None))
        binding_index += 1
    return True, names, canonical_distinct_rows(rows)


def guarded_operand_value(
    operand, names: tuple[str, ...], binding: tuple[Scalar, ...]
) -> Scalar | None:
    """Ground one comparison operand from a complete binding."""
    if not operand.valid:
        return None
    if operand.kind == "literal":
        return operand.literal
    if operand.kind == "variable":
        position = guarded_name_index(names, operand.variable)
        if 0 <= position < len(binding):
            return binding[position]
    return None


_PHASE3_LEGACY_GUARDED_OPERAND_VALUE = guarded_operand_value
guarded_operand_value = __import__(
    "gnd.terms", fromlist=["guarded_operand_evaluator"]
).guarded_operand_evaluator(_PHASE3_LEGACY_GUARDED_OPERAND_VALUE, Scalar)


def guarded_atom_state(
    atom,
    names: tuple[str, ...],
    binding: tuple[Scalar, ...],
    snapshot: SnapshotIR,
) -> int:
    """Return whether one fully grounded consequent atom is present."""
    fact_position = snapshot_fact_index(snapshot, atom.fact_type)
    relation_position = snapshot_relation_index(snapshot, atom.fact_type)
    if fact_position < 0 or relation_position < 0:
        return -1
    fact = snapshot.fact_types[fact_position]
    if len(atom.bindings) != len(fact.roles):
        return -1
    ground: list[Scalar | None] = []
    while len(ground) < len(fact.roles):
        ground.append(None)
    term_index = 0
    while term_index < len(atom.bindings):
        role, term = atom.bindings[term_index]
        column = fact_role_index(fact, role)
        if column < 0 or ground[column] is not None or not term.valid:
            return -1
        value = guarded_operand_value(term, names, binding)
        if value is None:
            return -1
        ground[column] = value
        term_index += 1
    if any(value is None for value in ground):
        return -1
    target = tuple(value for value in ground if value is not None)
    relation = snapshot.relations[relation_position]
    row_index = 0
    while row_index < len(relation.rows):
        row = relation.rows[row_index]
        if len(row) != len(target) or any(value is None for value in row):
            return -1
        represented = tuple(value for value in row if value is not None)
        if row_identical(target, represented):
            return 1
        row_index += 1
    return 0


def guarded_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """NF-GUARDED result with unknown precedence and exhaustive bindings."""
    empty: list[list[Scalar]] = []
    if (
        constraint.family != "guarded"
        or constraint.variant not in ("comparison", "atom", "absence")
        or constraint.consequent_kind != constraint.variant
        or constraint.refused != ""
        or not constraint.antecedent
    ):
        return -1, empty
    if constraint.variant == "comparison":
        if (
            len(constraint.operands) != 2
            or constraint.consequent
            or constraint.operator not in ("<", "<=", "=", ">=", ">", "!=")
        ):
            return -1, empty
    elif len(constraint.consequent) != 1 or constraint.operands:
        return -1, empty
    valid, names, bindings = guarded_bindings(constraint, snapshot)
    if not valid:
        return -1, empty
    violations: list[tuple[Scalar, ...]] = []
    undecidable = False
    binding_index = 0
    while binding_index < len(bindings):
        binding = bindings[binding_index]
        if constraint.variant == "comparison":
            left = guarded_operand_value(constraint.operands[0], names, binding)
            right = guarded_operand_value(constraint.operands[1], names, binding)
            state = (
                -1
                if left is None or right is None
                else comparison_pair_state(left, right, constraint.operator)
            )
        else:
            state = guarded_atom_state(constraint.consequent[0], names, binding, snapshot)
            if state >= 0 and constraint.variant == "absence":
                state = 1 - state
        if state < 0:
            undecidable = True
        elif state == 0:
            violations.append(binding)
        binding_index += 1
    if undecidable:
        return -1, empty
    if violations:
        result: list[list[Scalar]] = []
        violation_index = 0
        while violation_index < len(violations):
            result.append(list(violations[violation_index]))
            violation_index += 1
        return 0, result
    return 1, empty


def guarded_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return guarded_result(constraint, snapshot)[0]


def guarded_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return guarded_state(constraint, snapshot) == 1


def guarded_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return guarded_result(constraint, snapshot)[1]


def comparison_pair_state(left: Scalar, right: Scalar, operator: str) -> int:
    """NF-VC-1/NS-ORDER-2: -1 unknown, 0 violates, 1 satisfies."""
    if operator == "=":
        return 1 if scalar_identical(left, right) else 0
    if operator == "!=":
        return 0 if scalar_identical(left, right) else 1
    order = scalar_order(left, right)
    if order == -2:
        return -1
    if operator == "<":
        return 1 if order < 0 else 0
    if operator == "<=":
        return 1 if order <= 0 else 0
    if operator == ">=":
        return 1 if order >= 0 else 0
    if operator == ">":
        return 1 if order > 0 else 0
    return -1


def value_comparison_pairs(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[bool, list[tuple[Scalar, Scalar]]]:
    """Resolve NF-VC-1 inline, cross-same or connected cross-joined pairs."""
    result: list[tuple[Scalar, Scalar]] = []
    if (
        constraint.family != "value-comparison"
        or constraint.refused != ""
        or len(constraint.operands) != 2
        or constraint.operator not in ("<", "<=", "=", ">=", ">", "!=")
    ):
        return False, result
    first = constraint.operands[0]
    second = constraint.operands[1]
    if first.kind == "clock" or second.kind == "clock":
        return False, result
    if not first.valid or not second.valid:
        return False, result
    if constraint.variant == "cross-same" or constraint.variant == "cross-joined":
        if first.kind != "role" or second.kind != "role":
            return False, result
        same_fact = first.fact_type == second.fact_type
        if (constraint.variant == "cross-same") != same_fact:
            return False, result
        valid, rows = role_sequence_rows(
            ((first.fact_type, first.role), (second.fact_type, second.role)), snapshot
        )
        if not valid:
            return False, result
        row_index = 0
        while row_index < len(rows):
            if len(rows[row_index]) != 2:
                return False, []
            result.append((rows[row_index][0], rows[row_index][1]))
            row_index += 1
        return True, result
    if constraint.variant not in ("inline", "inline-literal"):
        return False, result
    literal_count = (1 if first.kind == "literal" else 0) + (1 if second.kind == "literal" else 0)
    if (constraint.variant == "inline" and literal_count != 0) or (
        constraint.variant == "inline-literal" and literal_count != 1
    ):
        return False, result
    fact_position = snapshot_fact_index(snapshot, constraint.fact_type)
    relation_position = snapshot_relation_index(snapshot, constraint.fact_type)
    if fact_position < 0 or relation_position < 0 or constraint.fact_type not in snapshot.covers:
        return False, result
    columns: list[int] = []
    operand_index = 0
    while operand_index < len(constraint.operands):
        operand = constraint.operands[operand_index]
        if operand.kind == "role":
            if operand.fact_type != constraint.fact_type:
                return False, result
            column = fact_role_index(snapshot.fact_types[fact_position], operand.role)
            if column < 0:
                return False, result
            columns.append(column)
        elif operand.kind == "literal" and operand.literal is not None:
            columns.append(-1)
        else:
            return False, result
        operand_index += 1
    relation = snapshot.relations[relation_position]
    row_index = 0
    while row_index < len(relation.rows):
        values: list[Scalar] = []
        operand_index = 0
        while operand_index < len(constraint.operands):
            operand = constraint.operands[operand_index]
            column = columns[operand_index]
            if column < 0:
                if operand.literal is None:
                    return False, []
                values.append(operand.literal)
            else:
                if column >= len(relation.rows[row_index]):
                    return False, []
                value = relation.rows[row_index][column]
                if value is None:
                    return False, []
                values.append(value)
            operand_index += 1
        result.append((values[0], values[1]))
        row_index += 1
    return True, result


def value_comparison_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """NF-VC-1 result with incomparability before violation."""
    valid, pairs = value_comparison_pairs(constraint, snapshot)
    empty: list[list[Scalar]] = []
    if not valid:
        return -1, empty
    violations: list[tuple[Scalar, ...]] = []
    undecidable = False
    pair_index = 0
    while pair_index < len(pairs):
        state = comparison_pair_state(
            pairs[pair_index][0], pairs[pair_index][1], constraint.operator
        )
        if state == -1:
            undecidable = True
        elif state == 0:
            violations.append(pairs[pair_index])
        pair_index += 1
    if undecidable:
        return -1, empty
    witness = canonical_distinct_rows(violations)
    if witness:
        result: list[list[Scalar]] = []
        pair_index = 0
        while pair_index < len(witness):
            result.append(list(witness[pair_index]))
            pair_index += 1
        return 0, result
    return 1, empty


def value_comparison_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    return value_comparison_result(constraint, snapshot)[0]


def value_comparison_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    return value_comparison_state(constraint, snapshot) == 1


def value_comparison_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[list[Scalar]]:
    return value_comparison_result(constraint, snapshot)[1]


def pack_witness_row(values: list[Scalar]) -> list[list[Scalar]]:
    """Wrap collected members in one aggregate row, including an empty row.

    Ownership of the member list passes to the result. The family predicate
    must separately establish complete membership and the violated condition.
    """
    return [values]


def decision_of(band: int) -> str:
    """NS-DECISION-2: the empty token means no semantic decision."""
    if band == 0:
        return "accept"
    if band == 1:
        return "refuse"
    if band == 2 or band == 4:
        return "indeterminate"
    return ""


def assurance_of(applicable: int, current: int, in_scope: bool) -> str:
    """NS-DECISION-2: counts of independently established applicable/current ids."""
    if not in_scope or applicable <= 0 or current <= 0 or current > applicable:
        return "none"
    if current == applicable:
        return "proof-backed"
    return "partial"


def assurance_for_route(
    applicable: int,
    current: int,
    in_scope: bool,
    admitted: bool,
    currency_valid: bool,
    extraction_required: bool,
    authenticated: bool,
) -> str:
    """r2 A2/A6: suppress assurance if any external eligibility gate fails.

    Proving this function does not authenticate extraction or establish the
    inputs' evidence currency; those facts require their own checked bridge.
    """
    if not admitted or not currency_valid or (extraction_required and not authenticated):
        return "none"
    return assurance_of(applicable, current, in_scope)


def band_of(verdicts: tuple[tuple[str, str], ...]) -> int:
    """NS-BAND-1: alethic fail > alethic unchecked > any vacuity > clean."""
    result = 0
    index = 0
    while index < len(verdicts):
        modality, verdict = verdicts[index]
        if modality == "alethic" and verdict == "fail":
            result = 1
        elif result != 1 and modality == "alethic" and verdict == "unchecked":
            result = 4
        elif result != 1 and result != 4 and verdict == "vacuous":
            result = 2
        index += 1
    return result


def optional_identical(value: Scalar | None, other: Scalar) -> bool:
    if value is None:
        return False
    return scalar_identical(value, other)


def optional_range_state(
    value: Scalar | None,
    minimum: Scalar | None,
    maximum: Scalar | None,
    min_inclusive: bool,
    max_inclusive: bool,
) -> int:
    if value is None:
        return -1
    return scalar_range_state(value, minimum, maximum, min_inclusive, max_inclusive)


def _value_member_reference(value: Scalar, allowed: tuple[Scalar, ...], index: int) -> bool:
    """Mathematical suffix definition; checking loops do not execute this."""
    if index == len(allowed):
        return False
    if scalar_identical(value, allowed[index]):
        return True
    return _value_member_reference(value, allowed, index + 1)


def _value_ranges_reference(
    value: Scalar,
    ranges: tuple[tuple[Scalar | None, Scalar | None, bool, bool], ...],
    index: int,
) -> int:
    """Mathematical suffix definition; inclusion outranks undecidability."""
    if index == len(ranges):
        return 0
    state = scalar_range_state(
        value,
        ranges[index][0],
        ranges[index][1],
        ranges[index][2],
        ranges[index][3],
    )
    if state == 1:
        return 1
    tail = _value_ranges_reference(value, ranges, index + 1)
    if tail == 1:
        return 1
    if state == -1 or tail == -1:
        return -1
    return 0


def _value_state_reference(value: Scalar | None, constraint: IRConstraint) -> int:
    """Contract reference, independent of the iterative checking route."""
    if value is None:
        return -1
    variant = constraint.variant
    if variant == "enum" or variant == "enum-role":
        if _value_member_reference(value, constraint.allowed, 0):
            return 1
        return 0
    if variant == "range" or variant == "range-role":
        if len(constraint.flags) < 4:
            return -1
        return scalar_range_state(
            value, constraint.minimum, constraint.maximum, constraint.flags[2], constraint.flags[3]
        )
    if variant == "ranges" or variant == "ranges-role":
        return _value_ranges_reference(value, constraint.ranges, 0)
    return -1


def append_value_witness(witness: list[Scalar], value: Scalar) -> None:
    """Append one selected occurrence while preserving the witness prefix."""
    witness.append(value)


def value_cursor(constraint: IRConstraint, snapshot: SnapshotIR) -> tuple[int, int, int]:
    """Resolve one immutable subject cursor: kind, source position, column."""
    variant = constraint.variant
    if variant == "enum" or variant == "range" or variant == "ranges":
        position = snapshot_roster_index(snapshot, constraint.object_type)
        if position >= 0:
            return 1, position, -1
        return 0, -1, -1
    if variant != "enum-role" and variant != "range-role" and variant != "ranges-role":
        return 0, -1, -1
    if len(constraint.role_refs) != 1:
        return 0, -1, -1
    fact_type, role = constraint.role_refs[0]
    fact_position = snapshot_fact_index(snapshot, fact_type)
    if fact_position < 0:
        return 0, -1, -1
    column = fact_role_index(snapshot.fact_types[fact_position], role)
    relation_position = snapshot_relation_index(snapshot, fact_type)
    if column < 0 or relation_position < 0:
        return 0, -1, -1
    return 2, relation_position, column


def value_occurrence_count(cursor: tuple[int, int, int], snapshot: SnapshotIR) -> int:
    """Return the immutable cursor length, or -1 for an invalid cursor."""
    if cursor[0] == 1 and 0 <= cursor[1] < len(snapshot.rosters) and cursor[2] == -1:
        return len(snapshot.rosters[cursor[1]].members)
    if cursor[0] == 2 and 0 <= cursor[1] < len(snapshot.relations) and cursor[2] >= 0:
        return len(snapshot.relations[cursor[1]].rows)
    return -1


def value_occurrence_scalar(
    cursor: tuple[int, int, int], snapshot: SnapshotIR, index: int
) -> Scalar | None:
    """Read one occurrence without allocating a projected subject sequence."""
    if (
        cursor[0] == 1
        and 0 <= cursor[1] < len(snapshot.rosters)
        and cursor[2] == -1
        and 0 <= index < len(snapshot.rosters[cursor[1]].members)
    ):
        return snapshot.rosters[cursor[1]].members[index]
    if (
        cursor[0] == 2
        and 0 <= cursor[1] < len(snapshot.relations)
        and cursor[2] >= 0
        and 0 <= index < len(snapshot.relations[cursor[1]].rows)
        and cursor[2] < len(snapshot.relations[cursor[1]].rows[index])
    ):
        return snapshot.relations[cursor[1]].rows[index][cursor[2]]
    return None


def value_occurrence_state(
    cursor: tuple[int, int, int],
    constraint: IRConstraint,
    snapshot: SnapshotIR,
    index: int,
) -> int:
    """Classify one cursor occurrence; malformed or absent cells are unknown."""
    value = value_occurrence_scalar(cursor, snapshot, index)
    if value is None:
        return -1
    return value_cell_state(value, constraint)


def value_violation_count(
    cursor: tuple[int, int, int],
    constraint: IRConstraint,
    snapshot: SnapshotIR,
    end: int,
) -> int:
    """Mathematical prefix rank used to specify ordered witness multiplicity."""
    if end == 0:
        return 0
    if _value_state_reference(value_occurrence_scalar(cursor, snapshot, end - 1), constraint) == 0:
        return value_violation_count(cursor, constraint, snapshot, end - 1) + 1
    return value_violation_count(cursor, constraint, snapshot, end - 1)


def value_cursor_state(
    cursor: tuple[int, int, int], constraint: IRConstraint, snapshot: SnapshotIR
) -> int:
    """Evaluate an immutable cursor without intermediate subject or state lists."""
    count = value_occurrence_count(cursor, snapshot)
    if count < 0:
        return -1
    result = 1
    index = 0
    while index < count:
        state = value_occurrence_state(cursor, constraint, snapshot, index)
        if state == -1:
            return -1
        if state == 0:
            result = 0
        index += 1
    return result


def value_cursor_witness(
    cursor: tuple[int, int, int], constraint: IRConstraint, snapshot: SnapshotIR
) -> list[Scalar]:
    """Collect every violating cursor occurrence in source order."""
    witness: list[Scalar] = []
    count = value_occurrence_count(cursor, snapshot)
    if count < 0 or value_cursor_state(cursor, constraint, snapshot) != 0:
        return witness
    index = 0
    while index < count:
        if value_occurrence_state(cursor, constraint, snapshot, index) == 0:
            value = value_occurrence_scalar(cursor, snapshot, index)
            if value is not None:
                append_value_witness(witness, value)
        index += 1
    return witness


def value_state(constraint: IRConstraint, snapshot: SnapshotIR) -> int:
    """Evaluate all selected value occurrences: -1 unknown, 0 violated, 1 satisfied."""
    if constraint.family != "value" or constraint.refused != "":
        return -1
    cursor = value_cursor(constraint, snapshot)
    state = value_cursor_state(cursor, constraint, snapshot)
    return state


def value_holds(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    """True exactly when the value family is evaluated and satisfied."""
    return value_state(constraint, snapshot) == 1


def value_witness(constraint: IRConstraint, snapshot: SnapshotIR) -> list[Scalar]:
    """Return the exhaustive, ordered flat witness for a decided violation."""
    empty: list[Scalar] = []
    if constraint.family != "value" or constraint.refused != "":
        return empty
    return value_cursor_witness(value_cursor(constraint, snapshot), constraint, snapshot)


def value_verdict(constraint: IRConstraint, snapshot: SnapshotIR) -> str:
    """Compose value-family state, modality, refusal, and vacuity into a verdict."""
    cursor = value_cursor(constraint, snapshot)
    count = value_occurrence_count(cursor, snapshot)
    role = (
        constraint.variant == "enum-role"
        or constraint.variant == "range-role"
        or constraint.variant == "ranges-role"
    )
    if role and count == 0:
        return "vacuous"
    if constraint.family != "value" or constraint.refused != "" or count < 0:
        return "unchecked"
    state = value_cursor_state(cursor, constraint, snapshot)
    if state == -1:
        return "unchecked"
    if state == 0:
        if constraint.modality == "deontic":
            return "warning"
        return "fail"
    if not role and count == 0:
        return "vacuous"
    return "pass"


def value_reason(constraint: IRConstraint, snapshot: SnapshotIR) -> str:
    """Return the frozen reason token for unchecked and vacuous value outcomes."""
    cursor = value_cursor(constraint, snapshot)
    count = value_occurrence_count(cursor, snapshot)
    role = (
        constraint.variant == "enum-role"
        or constraint.variant == "range-role"
        or constraint.variant == "ranges-role"
    )
    if role and count == 0:
        return "empty-subject"
    if constraint.refused == "untyped-string-ordering":
        return "bound-type-mismatch"
    if constraint.family != "value" or constraint.refused != "" or count < 0:
        return "family-unimplemented"
    state = value_cursor_state(cursor, constraint, snapshot)
    if state == -1:
        return "bound-type-mismatch"
    if state == 1 and not role and count == 0:
        return "no-observable-subjects"
    return ""


def relation_empty_state(snapshot: SnapshotIR, fact_type: str) -> int:
    """Return -1 for absent, 0 for populated, and 1 for empty relations."""
    position = snapshot_relation_index(snapshot, fact_type)
    if position < 0:
        return -1
    if len(snapshot.relations[position].rows) == 0:
        return 1
    return 0


def sequence_join_reason(sequence: tuple[tuple[str, str], ...], snapshot: SnapshotIR) -> str:
    """Classify connectedness and anchor ambiguity for one role sequence."""
    fact_order: list[str] = []
    selected: dict[str, list[int]] = {}
    reference_index = 0
    while reference_index < len(sequence):
        fact_type, role = sequence[reference_index]
        fact_position = snapshot_fact_index(snapshot, fact_type)
        if fact_position < 0:
            return "family-unimplemented"
        column = fact_role_index(snapshot.fact_types[fact_position], role)
        if column < 0:
            return "family-unimplemented"
        if fact_type not in selected:
            fact_order.append(fact_type)
            selected[fact_type] = []
        selected[fact_type].append(column)
        reference_index += 1
    if len(fact_order) < 2:
        return ""
    anchors: dict[str, list[str]] = {}
    fact_index = 0
    while fact_index < len(fact_order):
        fact_type = fact_order[fact_index]
        fact = snapshot.fact_types[snapshot_fact_index(snapshot, fact_type)]
        anchors[fact_type] = []
        role_index = 0
        while role_index < len(fact.roles):
            if role_index not in selected[fact_type]:
                object_type = fact.roles[role_index].object_type
                if object_type in anchors[fact_type]:
                    return "join-anchor-ambiguous"
                anchors[fact_type].append(object_type)
            role_index += 1
        fact_index += 1
    connected = [fact_order[0]]
    remaining = fact_order[1:]
    changed = True
    while changed and remaining:
        changed = False
        candidate_index = 0
        while candidate_index < len(remaining):
            candidate = remaining[candidate_index]
            linked = False
            anchor_index = 0
            while anchor_index < len(anchors[candidate]):
                connected_index = 0
                while connected_index < len(connected):
                    if anchors[candidate][anchor_index] in anchors[connected[connected_index]]:
                        linked = True
                    connected_index += 1
                anchor_index += 1
            if linked:
                connected.append(candidate)
                remaining.pop(candidate_index)
                changed = True
            else:
                candidate_index += 1
    if remaining:
        return "join-disconnected"
    return ""


def join_refusal_of(constraint: IRConstraint, snapshot: SnapshotIR) -> str:
    """Return the closed join refusal before family evaluation."""
    if constraint.family == "guarded" and len(constraint.antecedent) >= 2:
        atom_variables: list[list[str]] = []
        atom_index = 0
        while atom_index < len(constraint.antecedent):
            variables: list[str] = []
            term_index = 0
            while term_index < len(constraint.antecedent[atom_index].bindings):
                term = constraint.antecedent[atom_index].bindings[term_index][1]
                if term.kind == "variable" and term.variable not in variables:
                    variables.append(term.variable)
                term_index += 1
            atom_variables.append(variables)
            atom_index += 1
        connected = [0]
        remaining = list(range(1, len(atom_variables)))
        changed = True
        while changed and remaining:
            changed = False
            index = 0
            while index < len(remaining):
                candidate = remaining[index]
                linked = False
                variable_index = 0
                while variable_index < len(atom_variables[candidate]):
                    connected_index = 0
                    while connected_index < len(connected):
                        if (
                            atom_variables[candidate][variable_index]
                            in atom_variables[connected[connected_index]]
                        ):
                            linked = True
                        connected_index += 1
                    variable_index += 1
                if linked:
                    connected.append(candidate)
                    remaining.pop(index)
                    changed = True
                else:
                    index += 1
        if remaining:
            return "join-disconnected"
    sequences = constraint.sequences
    if constraint.family in ("uniqueness", "frequency") and constraint.variant == "external":
        sequences = (constraint.role_refs,)
    elif constraint.family == "value-comparison" and constraint.variant == "cross-joined":
        sequence: list[tuple[str, str]] = []
        operand_index = 0
        while operand_index < len(constraint.operands):
            operand = constraint.operands[operand_index]
            sequence.append((operand.fact_type, operand.role))
            operand_index += 1
        sequences = (tuple(sequence),)
    sequence_index = 0
    while sequence_index < len(sequences):
        reason = sequence_join_reason(sequences[sequence_index], snapshot)
        if reason:
            return reason
        sequence_index += 1
    return ""


def subject_slots_opaque(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    """True when a resolved single-subject rule is stopped only by an opaque cell.

    Covers ``mandatory``, ``mandatory-disjunctive`` and single-role
    ``exclusive-or``: the family's own cursor resolves one subject roster, and
    that roster or a role column holds an opaque cell. The adapter admits such
    a rule on purpose; without this its family's structural fallback reason
    would be reported (IK3-Q1).
    """
    if constraint.refused != "":
        return False
    columns: list[tuple[int, int]] = []
    roster_position = -1
    if constraint.family == "mandatory":
        cursor = mandatory_cursor(constraint, snapshot)
        roster_position = cursor[3]
        columns.append((cursor[2], cursor[1]))
    elif constraint.family in ("mandatory-disjunctive", "exclusive-or"):
        disjunctive = constraint
        if constraint.family == "exclusive-or":
            if constraint.variant != "single-role" or any(len(row) != 1 for row in constraint.sequences):
                return False
            # A single-role exclusive-or resolves its subject exactly as the
            # disjunctive mandatory over the same role slots does.
            disjunctive = replace(
                constraint,
                family="mandatory-disjunctive",
                variant="n-a",
                role_refs=tuple(row[0] for row in constraint.sequences),
            )
        _shared, roster_position, columns = mandatory_disjunctive_cursor(disjunctive, snapshot)
    if roster_position < 0:
        return False
    if any(value is None for value in snapshot.rosters[roster_position].members):
        return True
    return any(
        role_position < len(row) and row[role_position] is None
        for relation_position, role_position in columns
        for row in snapshot.relations[relation_position].rows
    )


def unchecked_reason_of(constraint: IRConstraint, snapshot: SnapshotIR) -> str:
    """Map an unevaluable IR constraint to the closed reason vocabulary."""
    join_reason = join_refusal_of(constraint, snapshot)
    if join_reason:
        return join_reason
    if subject_slots_opaque(constraint, snapshot):
        return "opaque-value"
    if constraint.refused == "unresolvable-role":
        return "role-unresolved"
    if constraint.refused == "unregistered-family" or constraint.refused == "malformed-constraint":
        return "family-unimplemented"
    if constraint.family == "textual":
        return "textual-not-mechanical"
    if constraint.family == "value":
        return "bound-type-mismatch"
    if constraint.family == "mandatory":
        return "role-unresolved"
    if constraint.family == "mandatory-disjunctive":
        return "subject-type-ambiguous"
    if constraint.family == "exclusive-or":
        if constraint.variant == "multi-role":
            return "xor-disjunctive-undefined"
        return "subject-type-ambiguous"
    if constraint.family == "ring":
        return "ring-not-binary"
    if constraint.family == "subtype-partition":
        if len(constraint.flags) < 2 or not constraint.flags[0] and not constraint.flags[1]:
            return "partition-asserts-nothing"
        return "subtype-derivation-only"
    if constraint.family == "value-comparison":
        if any(operand.kind == "clock" for operand in constraint.operands):
            return "no-reference-clock"
        if any(operand.kind == "literal" and not operand.valid for operand in constraint.operands):
            return "literal-type-ambiguous"
        return "values-not-comparable"
    if constraint.family == "guarded":
        if any(operand.kind == "literal" and not operand.valid for operand in constraint.operands):
            return "literal-type-ambiguous"
        if constraint.variant == "comparison":
            return "values-not-comparable"
    if constraint.family == "frequency" or constraint.family == "cardinality":
        return "bound-type-mismatch"
    return "family-unimplemented"


def snapshot_family_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[int, list[list[Scalar]]]:
    """Select one family provider from the shared registry."""
    entry = FAMILIES.get(constraint.family)
    if entry is None:
        return -1, []
    return resolve_hook(entry.evaluator, globals())(constraint, snapshot)


def sequence_spans_facts(sequence: tuple[tuple[str, str], ...]) -> bool:
    """True when a role sequence names at least two fact types."""
    fact_types: list[str] = []
    index = 0
    while index < len(sequence):
        if sequence[index][0] not in fact_types:
            fact_types.append(sequence[index][0])
        index += 1
    return len(fact_types) >= 2


def joined_pass_is_empty(constraint: IRConstraint, snapshot: SnapshotIR) -> bool:
    """NS-VACUITY-4 pass-only empty joined-universe classification."""
    if constraint.family == "uniqueness" or constraint.family == "frequency":
        if constraint.variant != "external" or not sequence_spans_facts(constraint.role_refs):
            return False
        valid, rows, _ = counting_projection_rows(constraint, snapshot, constraint.family)
        return valid and len(rows) == 0
    if constraint.family == "value-comparison" and constraint.variant == "cross-joined":
        valid, pairs = value_comparison_pairs(constraint, snapshot)
        return valid and len(pairs) == 0
    if constraint.family == "equality" or constraint.family == "exclusion":
        if not any(sequence_spans_facts(sequence) for sequence in constraint.sequences):
            return False
        valid, left, right = set_family_rows(constraint, snapshot, constraint.family)
        return valid and len(left) == 0 and len(right) == 0
    return False


def applicability_of(constraint: IRConstraint, snapshot: SnapshotIR) -> str:
    """Classify the pre-evaluation stages of NS-ORDER-OF-RESOLUTION-1."""
    subjects = constraint.scope_fact_types
    if constraint.family == "mandatory" or constraint.family == "mandatory-disjunctive":
        index = 0
        while index < len(subjects):
            if subjects[index] not in snapshot.covers:
                return "vacuous-coverage-omission"
            index += 1
    if constraint.family == "textual":
        return "unchecked-textual-not-mechanical"
    empty_count = 0
    index = 0
    while index < len(subjects):
        empty = relation_empty_state(snapshot, subjects[index])
        if empty < 0:
            return "unchecked-family-unimplemented"
        if empty == 1:
            empty_count += 1
        index += 1
    object_scoped = constraint.object_type != "" and (
        constraint.family == "value"
        and constraint.variant in ("enum", "range", "ranges")
        or constraint.family == "cardinality"
        and constraint.variant == "object"
        or constraint.family == "subtype-partition"
    )
    if subjects and not object_scoped:
        if constraint.family == "guarded" and empty_count > 0:
            return "vacuous-empty-subject"
        if constraint.family != "guarded" and empty_count == len(subjects):
            return "vacuous-empty-subject"
    if constraint.family == "anchored":
        # The pure snapshot IR carries no source bytes or sidecar. Its exact
        # answer is absence; the checker replaces this after binding input.
        return "unchecked-anchor-sidecar-absent"
    reason = unchecked_reason_of(constraint, snapshot)
    if constraint.refused != "" or join_refusal_of(constraint, snapshot):
        return "unchecked-" + reason
    if constraint.family not in (
        "mandatory",
        "mandatory-disjunctive",
        "value",
        "uniqueness",
        "frequency",
        "ring",
        "subset",
        "equality",
        "exclusion",
        "exclusive-or",
        "value-comparison",
        "cardinality",
        "subtype-partition",
        "guarded",
    ):
        return "unchecked-family-unimplemented"
    return "evaluate"


def verdict_of(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[str, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Compose applicability, one family result, modality and pass-only vacuity."""
    applicability = applicability_of(constraint, snapshot)
    if applicability.startswith("vacuous-"):
        return "vacuous", None, ()
    if applicability.startswith("unchecked-"):
        return "unchecked", applicability.removeprefix("unchecked-"), ()
    state, rows = snapshot_family_result(constraint, snapshot)
    if state < 0:
        return "unchecked", unchecked_reason_of(constraint, snapshot), ()
    witness = tuple(tuple(row) for row in rows)
    if state == 0:
        if constraint.modality == "deontic":
            return "warning", None, witness
        return "fail", None, witness
    object_scoped = constraint.object_type != "" and (
        constraint.family == "value"
        and constraint.variant in ("enum", "range", "ranges")
        or constraint.family == "cardinality"
        and constraint.variant == "object"
        or constraint.family == "subtype-partition"
    )
    if object_scoped:
        roster_position = snapshot_roster_index(snapshot, constraint.object_type)
        if roster_position >= 0 and len(snapshot.rosters[roster_position].members) == 0:
            return "vacuous", None, ()
    if joined_pass_is_empty(constraint, snapshot):
        return "vacuous", None, ()
    return "pass", None, ()

def _family_result_mandatory(constraint, snapshot):
    return mandatory_state(constraint, snapshot), [
        [value] for value in mandatory_witness(constraint, snapshot)
    ]


def _family_result_mandatory_disjunctive(constraint, snapshot):
    return mandatory_disjunctive_state(constraint, snapshot), [
        [value] for value in mandatory_disjunctive_witness(constraint, snapshot)
    ]


def _family_result_value(constraint, snapshot):
    return value_state(constraint, snapshot), [
        [value] for value in value_witness(constraint, snapshot)
    ]


def _family_result_uniqueness(constraint, snapshot):
    return uniqueness_result(constraint, snapshot)


def _family_result_frequency(constraint, snapshot):
    return frequency_result(constraint, snapshot)


def _family_result_ring(constraint, snapshot):
    return ring_result(constraint, snapshot)


def _family_result_subset(constraint, snapshot):
    return subset_state(constraint, snapshot), subset_witness(constraint, snapshot)


def _family_result_equality(constraint, snapshot):
    return equality_state(constraint, snapshot), equality_witness(constraint, snapshot)


def _family_result_exclusion(constraint, snapshot):
    return exclusion_state(constraint, snapshot), exclusion_witness(constraint, snapshot)


def _family_result_exclusive_or(constraint, snapshot):
    return exclusive_or_result(constraint, snapshot)


def _family_result_value_comparison(constraint, snapshot):
    return value_comparison_result(constraint, snapshot)


def _family_result_cardinality(constraint, snapshot):
    return cardinality_result(constraint, snapshot)


def _family_result_subtype_partition(constraint, snapshot):
    return subtype_partition_result(constraint, snapshot)


def _family_result_guarded(constraint, snapshot):
    return guarded_result(constraint, snapshot)


def _family_result_unknown(constraint, snapshot):
    return -1, []
