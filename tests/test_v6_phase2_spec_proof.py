"""Runtime mutation data only; this module has no formal verification tests.
The complete authored mutation tuples and patch helper are retained verbatim.
No original proof-module migration or verification claim is made.
"""
import ast

VALUE_MUTATIONS = (
    (
        "cursor-object-selection",
        "value_cursor",
        "snapshot_roster_index(snapshot, constraint.object_type)",
        "snapshot_roster_index(snapshot, constraint.fact_type)",
    ),
    (
        "cursor-role-column",
        "value_cursor",
        "return 2, relation_position, column",
        "return 2, relation_position, 0",
    ),
    (
        "cursor-witness-omission",
        "value_cursor_witness",
        "while index < count:",
        "while index < count - 1:",
    ),
    (
        "cursor-witness-duplication",
        "value_cursor_witness",
        "append_value_witness(witness, value)",
        "append_value_witness(witness, value)\n                append_value_witness(witness, value)",
    ),
    (
        "cursor-witness-reorder",
        "value_cursor_witness",
        "append_value_witness(witness, value)",
        "witness.insert(0, value)",
    ),
    (
        "cursor-unknown-to-fail",
        "value_occurrence_state",
        "if value is None:\n        return -1",
        "if value is None:\n        return 0",
    ),
)


MUTATIONS = (
    (
        "value-reference-empty",
        "_value_member_reference",
        "if index == len(allowed):\n        return False",
        "if index == len(allowed):\n        return True",
    ),
    (
        "value-enum-state",
        "value_cell_state",
        "if scalar_member(value, constraint.allowed):\n            return 1",
        "if scalar_member(value, constraint.allowed):\n            return 0",
    ),
    (
        "value-range-flags",
        "value_cell_state",
        "if len(constraint.flags) < 4:",
        "if len(constraint.flags) < 3:",
    ),
    (
        "value-range-inclusivity",
        "value_cell_state",
        "value, constraint.minimum, constraint.maximum, constraint.flags[2], constraint.flags[3]",
        "value, constraint.minimum, constraint.maximum, constraint.flags[3], constraint.flags[2]",
    ),
    (
        "value-ranges-state",
        "value_cell_state",
        "return scalar_ranges_state(value, constraint.ranges)",
        "return 0",
    ),
    (
        "snapshot-roster-index-tail",
        "snapshot_roster_index",
        "while index < len(snapshot.rosters):",
        "while index < len(snapshot.rosters) - 1:",
    ),
    (
        "snapshot-fact-index-tail",
        "snapshot_fact_index",
        "while index < len(snapshot.fact_types):",
        "while index < len(snapshot.fact_types) - 1:",
    ),
    (
        "snapshot-relation-index-tail",
        "snapshot_relation_index",
        "while index < len(snapshot.relations):",
        "while index < len(snapshot.relations) - 1:",
    ),
    (
        "fact-role-index-tail",
        "fact_role_index",
        "while index < len(fact.roles):",
        "while index < len(fact.roles) - 1:",
    ),
    (
        "projection-tail",
        "project_optional_column",
        "while index < len(rows):",
        "while index < len(rows) - 1:",
    ),
    (
        "projection-cell-omission",
        "append_projected_cell",
        "values.append(rows[index][column])",
        "values.append(None)",
    ),
    (
        "projection-wrong-column",
        "append_projected_cell",
        "values.append(rows[index][column])",
        "values.append(rows[index][0])",
    ),
    (
        "projection-refusal",
        "project_optional_column",
        "return False, refused",
        "return True, refused",
    ),
    ("identity", "scalar_identical", "left.token == right.token", "left.num == right.num"),
    ("order", "scalar_order", "if a < b:", "if a > b:"),
    (
        "range-min-inclusivity",
        "scalar_range_state",
        "min_inclusive and scalar_identical(value, minimum)",
        "not min_inclusive and scalar_identical(value, minimum)",
    ),
    (
        "range-max-inclusivity",
        "scalar_range_state",
        "max_inclusive and scalar_identical(value, maximum)",
        "not max_inclusive and scalar_identical(value, maximum)",
    ),
    (
        "range-min-order-equality",
        "scalar_range_state",
        "lower > 0 or (min_inclusive and scalar_identical(value, minimum))",
        "lower >= 0 or (min_inclusive and scalar_identical(value, minimum))",
    ),
    (
        "range-max-order-equality",
        "scalar_range_state",
        "upper < 0 or (max_inclusive and scalar_identical(value, maximum))",
        "upper <= 0 or (max_inclusive and scalar_identical(value, maximum))",
    ),
    (
        "range-incomparability",
        "scalar_range_state",
        "if lower == -2 or upper == -2:",
        "if lower == -2 and upper == -2:",
    ),
    (
        "ranges-tail",
        "scalar_ranges_state",
        "while index < len(ranges):",
        "while index < len(ranges) - 1:",
    ),
    (
        "ranges-inclusion-precedence",
        "scalar_ranges_state",
        "if state == -1:\n            result = -1",
        "if state == -1:\n            return -1",
    ),
    ("aggregate-row-omission", "pack_witness_row", "return [values]", "return []"),
    (
        "scalar-membership-tail",
        "scalar_member",
        "while index < len(values):",
        "while index < len(values) - 1:",
    ),
    (
        "scalar-prefix-bound",
        "scalar_member_before",
        "while index < len(values) and index < end:",
        "while index < len(values) and index <= end:",
    ),
    (
        "row-identity-tail",
        "row_identical",
        "while index < len(left):",
        "while index < len(left) - 1:",
    ),
    (
        "row-membership-tail",
        "row_member",
        "while index < len(rows):",
        "while index < len(rows) - 1:",
    ),
    (
        "missing-duplicates",
        "missing_identities",
        "not scalar_list_member(\n            universe[index], result\n        )",
        "True",
    ),
    (
        "missing-present-player",
        "missing_identities",
        "not scalar_member(universe[index], players)",
        "True",
    ),
    (
        "missing-omission",
        "append_absent_value",
        "result.append(value)",
        "pass",
    ),
    (
        "missing-prefix-advance",
        "advance_missing_prefix",
        "return index + 1",
        "return index",
    ),
    (
        "list-membership-tail",
        "scalar_list_member",
        "while cursor < len(values):",
        "while cursor < len(values) - 1:",
    ),
    (
        "decision",
        "decision_of",
        'if band == 1:\n        return "refuse"',
        'if band == 1:\n        return "accept"',
    ),
    ("assurance", "assurance_of", "if current == applicable:", "if current <= applicable:"),
    (
        "authentication",
        "assurance_for_route",
        " or (extraction_required and not authenticated)",
        "",
    ),
    (
        "band-precedence",
        "band_of",
        'elif result != 1 and modality == "alethic" and verdict == "unchecked":',
        'elif modality == "alethic" and verdict == "unchecked":',
    ),
)


def _mutated_source(source, function, before, after):
    """Apply the control only inside its named executable definition."""
    definitions = [
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == function
    ]
    assert len(definitions) == 1, function
    selected = definitions[0]
    lines = source.splitlines(keepends=True)
    start, end = selected.lineno - 1, selected.end_lineno
    body = "".join(lines[start:end])
    assert body.count(before) == 1, (function, before)
    return "".join(lines[:start]) + body.replace(before, after) + "".join(lines[end:])

