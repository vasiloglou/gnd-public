"""CNL verbalization templates for checker verdict messages.

Every verdict message the checker emits is rendered here, in Halpin-style
controlled natural language. Fact values are always interpolated inside quotes
as inert data — never concatenated as instructions (mitigates T-01-04
prompt-injection echo into future agent feedback).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

#: C0/C1 control characters and the two Unicode separator codepoints rendered
#: as escape sequences rather than emitted raw (CR-05 / CR-01). ``\n``, ``\r``
#: and ``\t`` get their conventional spellings; everything else in
#: U+0000..U+001F plus U+007F..U+009F becomes ``\xNN``. U+2028/U+2029 use their
#: ``\uNNNN`` spellings. NEL and both separators are line boundaries under
#: ``str.splitlines()``, so leaving any of them raw permits line forgery.
#: Built once at import: ``str.translate`` takes a codepoint->replacement map.
_CONTROL_ESCAPES: dict[int, str] = {codepoint: f"\\x{codepoint:02x}" for codepoint in range(0x20)}
_CONTROL_ESCAPES.update({codepoint: f"\\x{codepoint:02x}" for codepoint in range(0x7F, 0xA0)})
_CONTROL_ESCAPES[0x2028] = "\\u2028"
_CONTROL_ESCAPES[0x2029] = "\\u2029"
_CONTROL_ESCAPES[0x09] = "\\t"
_CONTROL_ESCAPES[0x0A] = "\\n"
_CONTROL_ESCAPES[0x0D] = "\\r"

#: Cap on ONE rendered datum. Fact-type keys, roster keys and role names are
#: agent-supplied and may be megabytes inside a 10 MB population; a single such
#: key would otherwise produce a single multi-megabyte message. The elision is
#: reported, never silent, and the cap is per-datum — the number of ISSUES is
#: bounded separately by ``report.MAX_POPULATION_ISSUES`` (WR-01).
MAX_RENDERED_VALUE_CHARS = 512

# Render order and labels of an object-type description's core keys, read by
# every renderer of descriptions (IK1). Any other key is an extra and is never prose.
DESCRIPTION_CORE_KEYS = ("summary", "row", "source", "notes")
DESCRIPTION_LABELS = {
    "summary": "Description",
    "row": "Row",
    "source": "Source",
    "notes": "Notes",
}


def neutralize_text(value: Any) -> str:
    """Escape untrusted text exactly as _neutralize does, without the length cap.

    Steps 1 and 2 of :func:`_neutralize`. Object-type descriptions are rendered
    in full, so they use this form; their length is bounded by the schema.
    """
    rendered = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return rendered.translate(_CONTROL_ESCAPES)


def description_lines(description: Any) -> list[tuple[str, str]]:
    """``(label, escaped text)`` for each present core key, in render order.

    The one walk every prose renderer of an object-type description uses, so
    order, labels and escaping cannot drift apart; extras are never returned.
    """
    if not isinstance(description, Mapping):
        return []
    return [
        (DESCRIPTION_LABELS[key], neutralize_text(description[key]))
        for key in DESCRIPTION_CORE_KEYS
        if key in description
    ]


def _neutralize(value: Any) -> str:
    """Render untrusted data so it can neither escape a quote nor forge a line.

    Three transformations, and all three are load-bearing (WR-06 / CR-05 /
    T-01-04). Verdict and issue messages are echoed into future agent feedback
    loops and into logs, so a population-supplied byte must never leave the
    delimiters or alter the output's LINE STRUCTURE:

    1. ``\\`` and ``'`` are escaped, so a value cannot close the quote.
    2. Newlines, carriage returns, tabs, C0/C1 controls and Unicode line/paragraph
       separators become escape sequences. Escaping only ``\\`` and ``'`` was an
       incomplete instantiation of the requirement: a fact-type key containing
       embedded newlines forged both an ``OK:`` line and a verdict-tally line
       into the text renderer's output — the verifier's own acceptance
       vocabulary, spoken by the population.
    3. The result is capped at :data:`MAX_RENDERED_VALUE_CHARS` with the
       elision stated, so one hostile key cannot produce one enormous message.
    """
    rendered = neutralize_text(value)
    if len(rendered) > MAX_RENDERED_VALUE_CHARS:
        elided = len(rendered) - MAX_RENDERED_VALUE_CHARS
        rendered = f"{rendered[:MAX_RENDERED_VALUE_CHARS]}… (+{elided} more characters)"
    return rendered


def _quote(value: Any) -> str:
    """Render a fact value as clearly delimited, inert data.

    See :func:`_neutralize` for what "inert" means and why each part of it is
    required.
    """
    return f"'{_neutralize(value)}'"


def path_segment(value: Any) -> str:
    """Neutralize an untrusted identifier for use inside a ``ValidationIssue.path``.

    ``path`` is JSONPath-ish and structural, so it carries no quotes of its own —
    which is exactly why it needed this (CR-05). ``popvalidate`` built it by raw
    f-string interpolation of agent-chosen keys (``path=f"$.facts.{key}"``) with
    no escaping at all, and ``cli._print_issues`` prints
    ``f"ERROR at {issue.path}: …"`` verbatim, so a key containing newlines forged
    additional lines into the text output.

    The same neutralizer as :func:`_quote`, minus the surrounding delimiters:
    one escaping rule for both channels, because two rules are how one of them
    drifts. Public (unlike ``_quote``) because ``popvalidate`` is its caller and
    the module boundary is the point — no ``path=`` may be assembled without it.
    """
    return _neutralize(value)


def line_text(value: Any) -> str:
    """Keep trusted renderer text on one terminal line.

    Messages contain deliberate quotes and backslashes, so applying
    :func:`_neutralize` to the whole sentence would double-escape its trusted
    syntax. This boundary neutralizes only line/control structure; individual
    untrusted values are still quoted through :func:`_quote` or
    :func:`path_segment` before interpolation.
    """
    return str(value).translate(_CONTROL_ESCAPES)


def constraint_message(
    constraint_type: str,
    verdict: str,
    *,
    fact_type_id: str | None = None,
    detail: str = "",
) -> str:
    """Generic CNL message for verdicts without a family-specific template."""
    scope = f" on fact type {_quote(fact_type_id)}" if fact_type_id else ""
    body = f" — {detail}" if detail else ""
    return f"Constraint {_quote(constraint_type)}{scope}: {verdict}{body}."


def uniqueness_message(
    subject_roles: list[str],
    fact_type_id: str,
    offending_groups: list[tuple[tuple[Any, ...], int]],
) -> str:
    subject = " and ".join(subject_roles)
    head = f"Each {subject} plays {_quote(fact_type_id)} with at most one combination of the other roles"
    if not offending_groups:
        return f"{head} — satisfied."
    violations = "; ".join(
        f"{subject} {', '.join(_quote(v) for v in key)} has {count} facts"
        for key, count in offending_groups
    )
    return f"{head} — violated: {violations}."


def mandatory_message(
    object_type_id: str,
    role_name: str,
    fact_type_id: str,
    missing_instances: list[Any],
) -> str:
    head = f"Each {object_type_id} must play the {_quote(role_name)} role in {_quote(fact_type_id)}"
    if not missing_instances:
        return f"{head} — satisfied."
    missing = ", ".join(_quote(v) for v in missing_instances)
    return f"{head} — violated: {missing} plays no such fact."


def _value_subject(object_type_id: str, role_ref: tuple | None) -> str:
    """Name the values a value constraint restricts: the whole type, or one role."""
    if role_ref is None:
        return f"Each {object_type_id} value"
    fact_type_id, role_name = role_ref
    return f"Each {object_type_id} value playing the {_quote(role_name)} role in {_quote(fact_type_id)}"


def value_enum_message(
    object_type_id: str,
    allowed: list[Any],
    offending: list[Any],
    *,
    role_ref: tuple | None = None,
) -> str:
    allowed_rendered = ", ".join(_quote(v) for v in allowed)
    head = f"{_value_subject(object_type_id, role_ref)} must be one of [{allowed_rendered}]"
    if not offending:
        return f"{head} — satisfied."
    values = ", ".join(_quote(v) for v in offending)
    return f"{head} — violated: {values}."


def value_range_message(
    object_type_id: str,
    minimum: Any,
    maximum: Any,
    offending: list[Any],
    *,
    role_ref: tuple | None = None,
) -> str:
    head = f"{_value_subject(object_type_id, role_ref)} must be between {_quote(minimum)} and {_quote(maximum)}"
    if not offending:
        return f"{head} — satisfied."
    values = ", ".join(_quote(v) for v in offending)
    return f"{head} — violated: {values} out of range."


def _render_tuple(values: tuple) -> str:
    """Render a role-sequence tuple; 1-tuples flatten to the bare quoted value."""
    if len(values) == 1:
        return _quote(values[0])
    return "(" + ", ".join(_quote(v) for v in values) + ")"


def uniqueness_external_message(
    role_labels: list[str],
    offending: list[tuple[tuple, int]],
) -> str:
    combination = ", ".join(role_labels)
    head = f"Each combination of ({combination}) occurs at most once"
    if not offending:
        return f"{head} — satisfied."
    violations = "; ".join(f"{_render_tuple(key)} occurs {count} times" for key, count in offending)
    return f"{head} — violated by: {violations}."


def mandatory_disjunctive_message(
    object_type_id: str,
    role_labels: list[str],
    missing: list,
) -> str:
    roles = ", ".join(role_labels)
    head = f"Each {object_type_id} plays at least one of the roles ({roles})"
    if not missing:
        return f"{head} — satisfied."
    instances = ", ".join(_quote(v) for v in missing)
    return f"{head} — violated: {instances} play none of them."


def disjunctive_subject_type_message(role_labels: list[str], object_types: list[str]) -> str:
    roles = ", ".join(_quote(label) for label in role_labels)
    types = ", ".join(_quote(value) for value in object_types)
    return (
        f"Disjunctive roles ({roles}) do not declare one common subject type "
        f"({types}) — reported as unchecked because declaration order cannot choose "
        "the quantified universe."
    )


def frequency_message(
    subject: str,
    minimum: Any,
    maximum: Any,
    offending: list[tuple[tuple, int]],
) -> str:
    if minimum is not None and maximum is not None:
        bound = f"at least {minimum} and at most {maximum} times"
    elif maximum is not None:
        bound = f"at most {maximum} times"
    else:
        bound = f"at least {minimum} times"
    head = f"Each occurrence of ({subject}) appears {bound}"
    if not offending:
        return f"{head} — satisfied."
    violations = "; ".join(f"{_render_tuple(key)} occurs {count} times" for key, count in offending)
    return f"{head} — violated: {violations}."


def subset_message(
    subset_labels: list[str],
    superset_labels: list[str],
    offending: list[tuple],
) -> str:
    subset_side = ", ".join(subset_labels)
    superset_side = ", ".join(superset_labels)
    head = f"If a tuple appears in ({subset_side}), then it also appears in ({superset_side})"
    if not offending:
        return f"{head} — satisfied."
    tuples = ", ".join(_render_tuple(t) for t in offending)
    return f"{head} — violated by: {tuples}."


def equality_message(
    labels_a: list[str],
    labels_b: list[str],
    only_a: list[tuple],
    only_b: list[tuple],
) -> str:
    side_a = ", ".join(labels_a)
    side_b = ", ".join(labels_b)
    head = f"The populations of ({side_a}) and ({side_b}) are equal"
    if not (only_a or only_b):
        return f"{head} — satisfied."
    parts = []
    if only_a:
        parts.append(", ".join(_render_tuple(t) for t in only_a) + " only in the first")
    if only_b:
        parts.append(", ".join(_render_tuple(t) for t in only_b) + " only in the second")
    return f"{head} — violated: {'; '.join(parts)}."


def exclusion_message(
    labels_a: list[str],
    labels_b: list[str],
    overlap: list[tuple],
) -> str:
    side_a = ", ".join(labels_a)
    side_b = ", ".join(labels_b)
    head = f"No tuple appears in both ({side_a}) and ({side_b})"
    if not overlap:
        return f"{head} — satisfied."
    tuples = ", ".join(_render_tuple(t) for t in overlap)
    return f"{head} — violated by: {tuples}."


def exclusive_or_message(
    object_type_id: str,
    seq_labels: list[str],
    both: list,
    neither: list,
) -> str:
    alternatives = "; ".join(f"({label})" for label in seq_labels)
    head = f"Each {object_type_id} plays exactly one of {alternatives}"
    if not (both or neither):
        return f"{head} — satisfied."
    parts = []
    if both:
        parts.append(", ".join(_quote(v) for v in both) + " plays more than one")
    if neither:
        parts.append(", ".join(_quote(v) for v in neither) + " plays none")
    return f"{head} — violated: {'; '.join(parts)}."


def exclusive_or_exclusion_violated_message(
    seq_labels: list[str],
    overlap: list[tuple],
) -> str:
    """The EXCLUSION half of a multi-role exclusive-or, violated.

    Deliberately NOT ``exclusive_or_message``'s "plays exactly one of … —
    violated" form. Only one of the constraint's two components was decided
    here, and a message phrased over the whole constraint would over-claim in
    the opposite direction to the ``pass`` it replaces.
    """
    alternatives = "; ".join(f"({label})" for label in seq_labels)
    tuples = ", ".join(_render_tuple(t) for t in overlap)
    return (
        f"No tuple appears in more than one of {alternatives} — violated by: "
        f"{tuples}. This is the EXCLUSION half of the exclusive-or; its "
        f"disjunctive half has no universe over multi-role sequences and was "
        f"not evaluated, but a tuple appearing in two sequences violates the "
        f"constraint whichever way that half would have gone."
    )


def exclusive_or_multirole_unchecked_message(seq_labels: list[str]) -> str:
    """A multi-role exclusive-or whose exclusion half is clean (D-15 as revised
    by 01.1-CONTEXT.md Amendment B).

    Opens with "was NOT evaluated" for the same reason the D-14 templates do:
    the defect this replaces was an AFFIRMATIVE claim of satisfaction, so a
    message that merely stops counting a pass while still reading as
    reassurance has not fixed anything. It names which half was decided, which
    was not, and why no universe exists for it.
    """
    alternatives = "; ".join(f"({label})" for label in seq_labels)
    return (
        f"Whether each tuple plays exactly one of {alternatives} was NOT "
        f"evaluated — reported as unchecked. The EXCLUSION half WAS evaluated "
        f"and found no tuple in more than one sequence; the DISJUNCTIVE half "
        f"(that every candidate tuple plays at least one) has no universe to "
        f"quantify over. ORM 2 defines disjunctive-mandatory over a set of "
        f"roles played by ONE object type, never over multi-role sequences, so "
        f"no set of candidate tuples is defined here — and a position-wise "
        f"product of the object-type populations would assert that every "
        f"combination must appear, which is strictly stronger and almost "
        f"always false. Declare single-role sequences if the disjunctive half "
        f"must be decided."
    )


def cardinality_message(
    subject: str,
    minimum: Any,
    maximum: Any,
    count: int,
    violated: bool,
) -> str:
    if minimum is not None and maximum is not None:
        bound = f"between {minimum} and {maximum}"
    elif maximum is not None:
        bound = f"at most {maximum}"
    else:
        bound = f"at least {minimum}"
    head = f"The number of {subject}s is {bound}"
    if not violated:
        return f"{head} — satisfied ({count} observed)."
    return f"{head} — violated: {count} observed."


def value_ranges_message(
    object_type_id: str,
    ranges: list[dict],
    offending: list[Any],
    *,
    role_ref: tuple | None = None,
) -> str:
    rendered = " or ".join(
        f"between {_quote(bounds.get('min'))} and {_quote(bounds.get('max'))}" for bounds in ranges
    )
    head = f"{_value_subject(object_type_id, role_ref)} must be {rendered}"
    if not offending:
        return f"{head} — satisfied."
    values = ", ".join(_quote(v) for v in offending)
    return f"{head} — violated: {values} outside every range."


_RING_HEADS = {
    "irreflexive": "no {ot} relates to itself",
    "asymmetric": "if a relates to b, then b does not relate back to a",
    "intransitive": "if a relates to b and b to c, then a does not relate to c",
    "antisymmetric": "mutual relating implies identity",
    "acyclic": "no chain of relatings returns to its start",
    "symmetric": "a relates to b if and only if b relates to a",
    "purely-reflexive": "each {ot} relates only to itself",
    "reflexive": "every {ot} relates to itself",
    "transitive": "if a relates to b and b to c, then a relates to c",
}


def ring_message(
    variant: str,
    fact_type_id: str,
    violations: list[tuple[str, tuple]],
) -> str:
    head = f"The relation {_quote(fact_type_id)} is {variant}"
    if not violations:
        return f"{head} — satisfied."
    parts = []
    for component, witness in violations:
        if component == "acyclic":
            chain = " -> ".join(_quote(v) for v in witness)
            parts.append(f"cycle through {chain}")
        else:
            parts.append(f"{component} broken by {_render_tuple(witness)}")
    return f"{head} — violated: {'; '.join(parts)}."


def unresolved_role_message(role_name: str, fact_type_id: str) -> str:
    return (
        f"Constraint references role {_quote(role_name)}, which does not exist on "
        f"fact type {_quote(fact_type_id)} — reported as unchecked; validation "
        f"rejects this shape (semantic:string-ref)."
    )


def join_disconnected_message(fact_type_ids: list[str]) -> str:
    listed = ", ".join(_quote(f) for f in fact_type_ids)
    return (
        f"Role references span fact types {listed} that share no anchor object "
        f"type — the shared-entity join is undefined (it would degrade to a "
        f"cross join), so the constraint is reported as unchecked, never "
        f"silently evaluated. Reference roles so that the remaining (anchor) "
        f"roles of the fact types share an object type."
    )


def join_ambiguous_message(fact_type_id: str, object_type_id: str, role_names: list[str]) -> str:
    roles = ", ".join(_quote(role_name) for role_name in role_names)
    return (
        f"Shared-entity join is ambiguous: fact type {_quote(fact_type_id)} supplies "
        f"multiple {_quote(object_type_id)} anchor roles ({roles}) — reported as "
        "unchecked until an explicit join mapping selects one."
    )


def ring_not_binary_message(variant: str, fact_type_id: str, role_count: int) -> str:
    return (
        f"Ring constraint {_quote(variant)} on {_quote(fact_type_id)} is unchecked: "
        f"ring semantics require a binary fact type, but {role_count} role(s) are "
        f"declared — validation rejects this shape (semantic:ring-binary)."
    )


_OPERATOR_WORDS = {
    "<": "is less than",
    "<=": "is at most",
    "=": "equals",
    ">=": "is at least",
    ">": "is greater than",
    "!=": "is not equal to",
}


def value_comparison_message(
    label_a: str,
    operator: str,
    label_b: str,
    offending: list[tuple],
) -> str:
    relation = _OPERATOR_WORDS.get(operator, operator)
    head = f"In each fact, {label_a} {relation} {label_b}"
    if not offending:
        return f"{head} — satisfied."
    pairs = "; ".join(f"{_quote(a)} versus {_quote(b)}" for a, b in offending)
    return f"{head} — violated by: {pairs}."


def _typed(value: Any) -> str:
    """A value as inert quoted data, followed by its Python type.

    The type is what makes an unchecked comparison actionable: 'could not
    compare 5 with cap' invites a shrug, while '5 (int) with cap (str)' names
    the repair.
    """
    return f"{_quote(value)} ({type(value).__name__})"


def values_not_comparable_message(
    label_a: str,
    operator: str,
    label_b: str,
    undecidable: list[tuple],
    offending: list[tuple],
) -> str:
    """D-14: an ordering comparison whose operands admit no order.

    Deliberately opens with "was NOT evaluated". CONTEXT.md's note that "the
    failure mode is affirmative" cuts both ways: a message that merely stops
    counting a pass while still reading as reassurance has not fixed anything.
    """
    relation = _OPERATOR_WORDS.get(operator, operator)
    pairs = "; ".join(f"{_typed(a)} versus {_typed(b)}" for a, b in undecidable)
    also = ""
    if offending:
        violated = "; ".join(f"{_quote(a)} versus {_quote(b)}" for a, b in offending)
        also = (
            f" Separately, these pairs did compare and violated it: {violated} — "
            f"but the constraint as a whole is not decided."
        )
    return (
        f"Whether in each fact {label_a} {relation} {label_b} was NOT evaluated — "
        f"reported as unchecked: {pairs} admit no ordering across their types. "
        f"Ordering by {_quote(operator)} requires two numbers or two strings; "
        f"comparing them as text instead would produce a confident wrong answer "
        f"rather than an answer (D-14).{also}"
    )


def bound_type_mismatch_message(
    object_type_id: str,
    ranges: list[dict],
    undecidable: list[Any],
    offending: list[Any],
) -> str:
    """D-13 clause 4: a value that cannot be ordered against its range bound."""
    bounds = " or ".join(
        f"between {_quote(bound.get('min'))} and {_quote(bound.get('max'))}" for bound in ranges
    )
    values = ", ".join(_typed(value) for value in undecidable)
    also = ""
    if offending:
        out_of_range = ", ".join(_quote(value) for value in offending)
        also = (
            f" Separately, {out_of_range} did compare and fell outside — but the "
            f"constraint as a whole is not decided."
        )
    return (
        f"Whether each {object_type_id} value lies {bounds} was NOT evaluated — "
        f"reported as unchecked: {values} cannot be ordered against the bound. "
        f"Model-relative type validation normally rejects such a value at load "
        f"(population:type-mismatch); this path remains only where the object "
        f"type has no resolvable primitive, so the value is deliberately never "
        f"type-checked (D-05).{also}"
    )


def value_comparison_unchecked_message(operand: str) -> str:
    return (
        f"Value-comparison against the current-time operand {_quote(operand)} is "
        f"unchecked — a reference clock is out of scope this phase."
    )


def value_comparison_literal_unchecked_message(literal: Any, primitive: str | None) -> str:
    return (
        f"Value-comparison literal {_quote(literal)} cannot be interpreted in the "
        f"compared role's resolved primitive {_quote(primitive)} — reported as "
        "unchecked rather than guessing from its spelling."
    )


def _guarded_binding(binding: dict[str, Any]) -> str:
    return (
        "{"
        + ", ".join(f"{_quote(variable)}: {_quote(value)}" for variable, value in binding.items())
        + "}"
    )


def guarded_message(
    consequent_kind: str,
    binding_count: int,
    offending: list[dict[str, Any]],
) -> str:
    """Summarize a decided guarded consequent without exposing raw fact text."""
    head = f"Guarded {consequent_kind} consequent evaluated over bindings={binding_count}"
    if not offending:
        return f"{head} — satisfied."
    rendered = "; ".join(_guarded_binding(binding) for binding in offending)
    return f"{head} — violated by bindings: {rendered}."


def guarded_zero_bindings_message(consequent_kind: str) -> str:
    return (
        f"Guarded {consequent_kind} consequent evaluated over bindings=0 — "
        "satisfied because the populated antecedent relations matched no binding."
    )


def guarded_not_comparable_message(
    operator: str,
    binding_count: int,
    undecidable: list[dict[str, Any]],
    offending: list[dict[str, Any]],
) -> str:
    undecidable_text = "; ".join(_guarded_binding(binding) for binding in undecidable)
    also = ""
    if offending:
        offending_text = "; ".join(_guarded_binding(binding) for binding in offending)
        also = (
            f" Other bindings violated the comparison: {offending_text}; the guarded "
            "constraint as a whole remains undecided."
        )
    return (
        f"Guarded comparison over bindings={binding_count} was NOT fully evaluated — "
        f"operator {_quote(operator)} cannot compare values for bindings: "
        f"{undecidable_text}.{also}"
    )


def guarded_literal_unchecked_message(
    literal: Any, primitive: str | None, binding_count: int
) -> str:
    return (
        f"Guarded comparison over bindings={binding_count} was NOT evaluated: literal "
        f"{_quote(literal)} cannot be interpreted in the borrowed primitive "
        f"{_quote(primitive)} — reported as unchecked rather than guessed."
    )


def subtype_partition_message(
    supertype: str,
    subtypes: list[str],
    both: list,
    neither: list,
) -> str:
    listed = ", ".join(subtypes)
    head = f"Every {supertype} is partitioned over: {listed}"
    if not (both or neither):
        return f"{head} — satisfied."
    parts = []
    if both:
        parts.append(", ".join(_quote(v) for v in both) + " is in more than one subtype")
    if neither:
        parts.append(", ".join(_quote(v) for v in neither) + " is in no subtype")
    return f"{head} — violated: {'; '.join(parts)}."


def subtype_partition_no_assertion_message(supertype: str, subtypes: list[str]) -> str:
    """CR-02: a ``subtype-partition`` asserting neither exclusion nor totality.

    Opens with "was NOT evaluated" for the same reason the D-14/D-15 templates
    do: the defect this replaces was an affirmative "— satisfied" over a
    constraint whose every component had been switched off, so a message that
    merely stops counting a pass while still reading as reassurance has not
    fixed anything.
    """
    listed = ", ".join(subtypes)
    return (
        f"Whether every {supertype} is partitioned over {listed} was NOT "
        f"evaluated — reported as unchecked: this constraint sets neither "
        f"'exclusive' nor 'exhaustive', and so asserts nothing to check. In "
        f"ORM 2 a subtype partition IS the conjunction of subtype exclusion and "
        f"subtype totality (Halpin, Information Modeling and Relational "
        f"Databases 2e §6.5); the three defined readings are full partition, "
        f"exclusive only, and exhaustive only. There is no 'neither' reading, "
        f"so a 'pass' verdict is not a defined outcome for this shape. Set "
        f"'exclusive: true', 'exhaustive: true', or both. Model validation "
        f"normally rejects this at load (semantic:partition-asserts-nothing); "
        f"this path remains only for a Model constructed in process."
    )


def partition_asserts_nothing_message(supertype: str, subtypes: list[str]) -> str:
    """semantic:partition-asserts-nothing (CR-02) — the AUTHORING-time twin.

    Same defect, stated to the model author rather than to the population
    author, so it names the file to edit rather than the verdict withheld.
    """
    listed = ", ".join(_quote(s) for s in subtypes) if subtypes else "(none)"
    return (
        f"subtype-partition over {_quote(supertype)} (subtypes: {listed}) sets "
        f"neither 'exclusive: true' nor 'exhaustive: true', so it asserts "
        f"nothing. In ORM 2 a subtype partition is the conjunction of subtype "
        f"exclusion and subtype totality (Halpin 2e §6.5) and has exactly three "
        f"readings — full partition, exclusive only, exhaustive only. A "
        f"constraint with no reading cannot be satisfied or violated, and the "
        f"checker previously reported it as satisfied while evaluating nothing. "
        f"Set 'exclusive: true', 'exhaustive: true', or both — or delete the "
        f"constraint."
    )


def subtype_partition_unchecked_message(subtype: str, derivation_rule: str) -> str:
    return (
        f"Subtype {_quote(subtype)} membership is only derivable via the opaque "
        f"derivation rule {_quote(derivation_rule)} — reported as unchecked; the "
        f"rule text is quoted data and is never evaluated."
    )


def textual_unchecked_message(expression: str) -> str:
    return (
        f"Textual constraint {_quote(expression)} is not mechanically checkable "
        f"— reported as unchecked; the expression is quoted data and is never "
        f"evaluated."
    )


def unchecked_message(constraint_type: str) -> str:
    return (
        f"Constraint type {_quote(constraint_type)} is not implemented by this checker "
        f"— reported as unchecked, never silently passed."
    )


def vacuous_message(fact_type_ids: list[str]) -> str:
    subjects = ", ".join(_quote(f) for f in fact_type_ids)
    return (
        f"Fact type(s) {subjects} contain no facts in this population "
        f"— constraint is vacuous, not evaluated."
    )


def no_observable_subjects_message(object_type_id: str) -> str:
    """The other empty-subject shape (F-02): the constraint's object type has no
    population at all, rather than a subject fact type that is present but
    empty. Same epistemic state as :func:`vacuous_message`, so the same verdict
    and the same closing clause — reporting the first as `vacuous` at exit 2 and
    the second as `pass` at exit 0 was the inconsistency. The middle clause names
    both routes a population could have arrived by, so a retry loop is told what
    to supply."""
    return (
        f"Object type {_quote(object_type_id)} has no instances in this population "
        f"— no fact type gives it a population and no instances: roster supplies one "
        f"— constraint is vacuous, not evaluated."
    )


def no_joined_rows_message(seq_labels: list[str]) -> str:
    """The third empty-subject shape (F-05): a join-scoped constraint whose subject
    role sequence(s) span more than one fact type and whose JOIN produced zero rows,
    even when every referenced fact type is individually populated. Same epistemic
    state as :func:`vacuous_message` and :func:`no_observable_subjects_message` —
    decided, no subjects — so the same verdict and the same closing clause.

    It must NOT say the constraint was satisfied: there were no joined tuples to
    evaluate it over. Structural labels are neutralized through
    :func:`path_segment` (CR-05 / T-02-01), never raw-interpolated — a new message
    is a new place for a population-supplied identifier to forge a line."""
    joined = "; ".join(f"({path_segment(label)})" for label in seq_labels)
    return (
        f"The joined subject {joined} produced no rows in this population "
        f"— the referenced fact types share no matching anchor values, so the join "
        f"is empty — constraint is vacuous, not evaluated."
    )


# --- CORE-06 / D-20 layer-2 MODEL validation (gnd.model semantic rules) ---
#
# Model-defect messages, kept here with every other CNL template rather than
# inlined in the rule functions, so the one place a reader looks for GND's
# wording is the one place it lives. Model-supplied text (ids, role names,
# textual expressions) goes through `_quote` for the same reason population
# values do: it is untrusted input echoed into agent-facing output (WR-06).


def role_seq_arity_message(
    constraint_type: str,
    lengths: list[tuple[str, int]],
) -> str:
    """semantic:role-seq-arity — set-comparison sequences of unequal length.

    Halpin, ORM 2 TechReport §2.8: subset, equality, exclusion and the
    exclusion half of exclusive-or are defined over COMPATIBLE role sequences,
    and compatibility presupposes equal arity — a (person, course) pair has no
    defined containment relation to a bare (person).
    """
    observed = ", ".join(f"{_quote(label)} has {count}" for label, count in lengths)
    return (
        f"{_quote(constraint_type)} constraint compares role sequences of "
        f"different lengths ({observed}); ORM set-comparison constraints "
        f"require compatible role sequences of equal arity."
    )


def role_seq_type_compat_message(
    constraint_type: str,
    position: int,
    ref_a: tuple[str, str, str],
    ref_b: tuple[str, str, str],
) -> str:
    """semantic:role-seq-type-compat — position-wise incompatible sequences.

    Each ``ref`` is ``(fact_type_id, role_name, object_type_id)``. Equal length
    is necessary but not sufficient: the constraint asserts the same tuple
    appears in both projections, which is meaningless when the values at a
    position are drawn from disjoint populations.
    """
    fact_type_a, role_a, object_type_a = ref_a
    fact_type_b, role_b, object_type_b = ref_b
    return (
        f"{_quote(constraint_type)} constraint compares position {position} of "
        f"its role sequences, but {_quote(f'{fact_type_a}.{role_a}')} is typed "
        f"{_quote(object_type_a)} and {_quote(f'{fact_type_b}.{role_b}')} is "
        f"typed {_quote(object_type_b)}, which share no common supertype."
    )


def textual_alethic_message(constraint_type: str, expression: str | None) -> str:
    """semantic:textual-alethic (D-20) — WARNING severity, never error.

    Surfaces permanent indeterminacy at AUTHORING time rather than leaving it
    to be discovered at check time. The expression is quoted data and is never
    evaluated here, exactly as in ``textual_unchecked_message``.
    """
    subject = (
        f"the {_quote(constraint_type)} constraint {_quote(expression)}"
        if expression
        else f"this {_quote(constraint_type)} constraint"
    )
    return (
        f"{subject} carries modality 'alethic', but its family can never be "
        f"mechanically evaluated — so this model can never reach exit 0 for "
        f"ANY population: an unverifiable HARD constraint means acceptance "
        f"cannot be mechanically claimed, and the run is permanently "
        f"indeterminate (exit 4). Write 'modality: deontic' unless permanent "
        f"indeterminacy is what you intend (D-20)."
    )


# --- CORE-04 layer-2 population validation (gnd.popvalidate) ---
#
# These describe an ILL-FORMED population (exit 3), not a broken business rule
# (exit 1). None of them may reuse the "— satisfied." tail of the checker's pass
# messages: the defect this layer closes was affirmative acceptance, so a
# rejection message must never read like reassurance. Each names the rule that
# produced it, because PopulationValidationError's summary string joins only
# `path: message` and would otherwise lose the rule_id.
#
# Every datum interpolated here originates in an untrusted population document
# and therefore goes through _quote (WR-06 / T-01-04) — fact-type keys, roster
# keys, coverage entries and role names are all agent-supplied strings.


def population_unknown_fact_type_message(fact_type_id: Any, declared: list[str]) -> str:
    listed = ", ".join(_quote(f) for f in declared) if declared else "(none)"
    return (
        f"The population declares facts for {_quote(fact_type_id)}, which is not a "
        f"fact type in this model. Declared fact types are: {listed} "
        f"(population:unknown-fact-type)."
    )


def population_unknown_object_type_message(object_type_id: Any) -> str:
    return (
        f"The population declares an instance roster for {_quote(object_type_id)}, "
        f"which is not an object type in this model "
        f"(population:unknown-object-type)."
    )


def population_unknown_covers_message(fact_type_id: Any) -> str:
    return (
        f"Coverage is declared for {_quote(fact_type_id)}, which is not a fact type "
        f"in this model, so the completeness claim cannot be verified "
        f"(population:unknown-covers)."
    )


def population_duplicate_covers_message(fact_type_id: Any, first_index: int) -> str:
    return (
        f"Fact type {_quote(fact_type_id)} is declared in coverage more than once "
        f"(already at index {first_index}) — a fact type is either covered or it is "
        f"not (population:duplicate-covers)."
    )


def population_uncovered_structured_derived_facts_message(
    fact_type_id: Any, fact_count: int
) -> str:
    noun = "fact" if fact_count == 1 else "facts"
    return (
        f"Fact type {_quote(fact_type_id)} supplies {fact_count} {noun}, but the "
        "population omits that type from coverage and therefore declares it "
        "unexamined. Facts cannot be asserted while the population declares "
        "their structured-derived type unexamined "
        "(population:uncovered-structured-derived-facts)."
    )


def population_missing_role_message(
    fact_type_id: Any,
    fact_index: int,
    role_name: Any,
    declared_roles: list[str],
) -> str:
    listed = ", ".join(_quote(r) for r in declared_roles)
    return (
        f"Fact {fact_index} of {_quote(fact_type_id)} omits role {_quote(role_name)}; "
        f"an instance of {_quote(fact_type_id)} fills all {len(declared_roles)} of its "
        f"roles ({listed}). A fact missing a role is not a partial fact "
        f"(population:missing-role)."
    )


def population_extra_role_message(
    fact_type_id: Any,
    fact_index: int,
    role_name: Any,
    declared_roles: list[str],
) -> str:
    listed = ", ".join(_quote(r) for r in declared_roles)
    return (
        f"Fact {fact_index} of {_quote(fact_type_id)} supplies role {_quote(role_name)}, "
        f"which {_quote(fact_type_id)} does not declare; its roles are ({listed}) "
        f"(population:extra-role)."
    )


def _non_finite_note(value: Any) -> str:
    """CR-04: why a ``float`` can still fail a ``Float`` role.

    Without this clause the type-mismatch message reads "supplies 'nan' (float)
    … an object type whose values are 'Float'", which states the opposite of the
    reason. A retry loop reading that would try harder to emit a float.
    """
    if isinstance(value, float) and not math.isfinite(value):
        return (
            " A non-finite float is not a value of any numeric type here: "
            "IEEE 754-2019 §5.11 makes every ordered comparison involving NaN "
            "unordered, so a NaN is neither inside nor outside a range and "
            "cannot be checked against one, and RFC 8259 §6 permits no NaN or "
            "Infinity literal in the JSON report this tool emits."
        )
    return ""


def population_type_mismatch_message(
    fact_type_id: Any,
    fact_index: int,
    role_name: Any,
    object_type_id: Any,
    primitive: Any,
    value: Any,
) -> str:
    return (
        f"Fact {fact_index} of {_quote(fact_type_id)} supplies {_quote(value)} "
        f"({type(value).__name__}) for role {_quote(role_name)}, which is typed "
        f"{_quote(object_type_id)} — an object type whose values are "
        f"{_quote(primitive)}. A value of the wrong primitive is not a value of "
        f"that type (population:type-mismatch).{_non_finite_note(value)}"
    )


def population_roster_type_mismatch_message(
    object_type_id: Any,
    index: int,
    primitive: Any,
    value: Any,
) -> str:
    return (
        f"Entry {index} of the {_quote(object_type_id)} instance roster is "
        f"{_quote(value)} ({type(value).__name__}), but {_quote(object_type_id)} "
        f"is an object type whose values are {_quote(primitive)}. A value of the "
        f"wrong primitive is not a value of that type "
        f"(population:type-mismatch).{_non_finite_note(value)}"
    )


def population_model_id_mismatch_message(population_model_id: Any, model_model_id: Any) -> str:
    return (
        f"This population declares model_id {_quote(population_model_id)}, but the "
        f"model declares {_quote(model_model_id)} — it was written for a different "
        f"model (population:model-id-mismatch)."
    )


def population_model_id_absent_message(model_model_id: Any) -> str:
    return (
        f"The model declares model_id {_quote(model_model_id)}; this population "
        f"declares none, so the header cross-check was skipped "
        f"(population:model-id-absent)."
    )


def coverage_omission_message(omitted_fact_type_ids: list[str]) -> str:
    omitted = ", ".join(_quote(f) for f in omitted_fact_type_ids)
    return (
        f"Population coverage omits fact type(s) {omitted}, which carry a "
        f"mandatory-relevant constraint — vacuous: the population does not "
        f"claim completeness for them (D-12)."
    )


def derivation_incomplete_message(fact_type: str, witness: str) -> str:
    """Render the one normative incomplete-extension finding."""

    return f"The derived extension of '{fact_type}' is incomplete — missing {witness}."


def derivation_unsound_message(fact_type: str, witness: str) -> str:
    """Render the one normative unsound-extension finding."""

    return f"The derived extension of '{fact_type}' is unsound — offending fact {witness}."


def temporal_guarded_message(consequent_kind: str, offending: list[dict[str, Any]]) -> str:
    """Render a temporal decision without repeating the bounded join."""
    head = f"Guarded temporal {consequent_kind} consequent"
    if not offending:
        return f"{head} — satisfied."
    rendered = "; ".join(_guarded_binding(binding) for binding in offending)
    return f"{head} — violated by bindings: {rendered}."
