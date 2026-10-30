"""The Boolean rule-set adapter: a feature table out, a rule set back (ilp-learners IL3).

``render`` writes ``rules/features.json`` (``gnd-ilp-features/1``): one row per
example, one 0/1 column per feature. A feature is one integer argument position of
an exported predicate crossed with one of Popper's threshold rows, so both adapters
offer the same thresholds. Each column's name spells its clause, arity included
(IL3-F2 (o)), so ``parse_ruleset`` needs no export. The reader takes wittgenstein's
printed rule set and applies the polarity table: a single true feature becomes its
clause; a false feature, a conjunction, an empty rule and a rule list are refused by
name. Spec: ``.gnd-planning/milestones/ilp-learners/notes/phase-IL3-spec.md`` §6
(r1, approved 2026-10-28).
"""

from __future__ import annotations

import re
from typing import Any

from gnd.exits import EXIT_ILL_FORMED
from gnd.export.ilp import IlpError, canonical_bytes
from gnd.export.ilp_popper import threshold_rows

__all__ = ["ADAPTER_VERSION", "EXPORT_REFUSALS", "FALSE_SPELLINGS", "IMPORT_REFUSALS", "MAX_CELLS",
           "MAX_FEATURES", "REFUSALS", "TRUE_SPELLINGS", "check_columns", "extract_ruleset",
           "parse_ruleset", "render"]

ADAPTER_VERSION = "1"
FEATURES_SCHEMA_VERSION = "gnd-ilp-features/1"
#: IL3-D5: bounds fixed before results.
MAX_FEATURES = 4096
MAX_CELLS = 4_000_000
MAX_RULES = 32
MAX_CONDITIONS = 16
MAX_NAME = 160
#: An atom's argument cap in ilp-clauses.schema.json; bounds the clause a name builds (review 1).
MAX_ARITY = 64
MAX_DIGITS = 32
#: The condition spellings the reader reads as a true or a false feature (IL3-D7).
TRUE_SPELLINGS = ("=1", "=1.0", "=True", ">0.5")
FALSE_SPELLINGS = ("=0", "=0.0", "=False", "<=0.5")
#: The export's refusals.
EXPORT_REFUSALS = ("no-features", "too-many-features", "too-large", "column-name")
#: The reader's own refusals, in the order it applies them; ``unparsable`` aside.
REFUSALS = ("ordered-rule-list", "empty-antecedent", "negation-as-failure", "propositional-conjunction")
#: The import's adapter check (IH0 finding A), after the run record's bindings.
IMPORT_REFUSALS = ("off-threshold",)

_COLUMN = re.compile(r"([a-z][a-z0-9_]*?)__([1-9][0-9]*)__([1-9][0-9]*)__"
                     r"((?:gt|lt)_t_[A-Za-z0-9_]+?)__(m?)([0-9]+)")
_NAME_CHARS = re.compile(r"[A-Za-z0-9_]*")
_RULE_LIST = re.compile(r"\s*if\s", re.IGNORECASE)
_PREFIX = "RULESET "
#: The neutral-form keys a column projects; the neutral form is not the model.
_ROLES = "roles"


def _refuse(name: str, detail: str) -> IlpError:
    return IlpError(EXIT_ILL_FORMED, f"{name}: {detail}")


def _suffix(value: int) -> str:
    return f"m{-value}" if value < 0 else str(value)


def _columns(neutral: dict[str, Any]) -> list[dict[str, Any]]:
    rows = threshold_rows(neutral)
    columns = []
    for predicate in neutral["predicates"]:
        arity = len(predicate["types"])
        for position in range(1, arity):
            for row_name, type_name, _holds in rows:
                if type_name != predicate["types"][position]:
                    continue
                comparison, _, spelled = row_name.rpartition("__")
                threshold = -int(spelled[1:]) if spelled.startswith("m") else int(spelled)
                name = f"{predicate['name']}__{position}__{arity}__{row_name}"
                if len(name) > MAX_NAME or _column(name) != (
                        predicate["name"], position, arity, comparison, threshold):
                    # A name the reader would refuse or misread is never written (reviews 2, 3).
                    raise _refuse("column-name", f"column {name!r} is over {MAX_NAME} characters, "
                                  "has a threshold over the digit cap, or does not read back as itself")
                columns.append({"name": name, "predicate": predicate["name"], "position": position,
                                "arity": arity, "role": predicate[_ROLES][position - 1],
                                "type": type_name, "comparison": comparison,
                                "operator": ">" if comparison.startswith("gt") else "<",
                                "threshold": threshold})
    return columns


def render(neutral: dict[str, Any]) -> dict[str, bytes]:
    """The feature table (spec §6); the bounds refuse before any cell is computed."""
    columns = _columns(neutral)
    if not columns:
        raise _refuse("no-features", "the export has no integer argument with a threshold")
    if len(columns) > MAX_FEATURES:
        raise _refuse("too-many-features", f"{len(columns)} features, over {MAX_FEATURES}")
    cells = len(columns) * len(neutral["examples"])
    if cells > MAX_CELLS:
        raise _refuse("too-large", f"{cells} cells, over {MAX_CELLS}")
    values: dict[tuple[str, str, int], list[int]] = {}
    for fact in neutral["facts"]:
        for position, value in enumerate(fact["values"], start=1):
            if isinstance(value, int) and not isinstance(value, bool):
                values.setdefault((fact["example"], fact["predicate"], position), []).append(value)
    rows = []
    for example in neutral["examples"]:
        cells_of = []
        for column in columns:
            seen = values.get((example["id"], column["predicate"], column["position"]), [])
            threshold = column["threshold"]
            hit = any(v > threshold for v in seen) if column["operator"] == ">" else any(
                v < threshold for v in seen)
            cells_of.append(int(hit))
        rows.append({"example": example["id"], "label": example["label"], "values": cells_of})
    table = {"schema_version": FEATURES_SCHEMA_VERSION, "columns": columns, "rows": rows,
             "work": {"cells": cells, "ceiling": MAX_CELLS}}
    return {"rules/features.json": canonical_bytes(table)}


def _column(name: str) -> tuple[str, int, int, str, int] | None:
    """A column name's (predicate, position, arity, comparison, threshold), or None."""
    match = _COLUMN.fullmatch(name)
    if match is None:
        return None
    predicate, position, arity, comparison, sign, digits = match.groups()
    if len(digits) > MAX_DIGITS or (len(digits) > 1 and digits[0] == "0") or (sign and digits == "0"):
        return None
    if len(arity) > 2 or int(arity) > MAX_ARITY or int(position) >= int(arity):
        return None
    return predicate, int(position), int(arity), comparison, -int(digits) if sign else int(digits)


def _clause(name: str) -> dict[str, Any]:
    column = _column(name)
    assert column is not None
    predicate, position, arity, comparison, threshold = column
    args = [{"var": "X"}] + [{"var": f"V{k}"} for k in range(1, arity)]
    return {"head": {"predicate": "wrong", "args": [{"var": "X"}]},
            "body": [{"atom": {"predicate": predicate, "args": args}},
                     {"atom": {"predicate": comparison,
                               "args": [{"var": f"V{position}"}, {"const": threshold}]}}]}


class _Reader:
    """wittgenstein's ``str(ruleset)``, one line, read once (spec §6 grammar)."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.at = 0

    def fail(self, detail: str) -> IlpError:
        return _refuse("unparsable", f"column {self.at + 1}: {detail}")

    def expect(self, literal: str) -> None:
        if not self.text.startswith(literal, self.at):
            raise self.fail(f"expected {literal!r}")
        self.at += len(literal)

    def ruleset(self) -> list[list[tuple[str, bool]] | None]:
        self.expect("[")
        rules: list[list[tuple[str, bool]] | None] = []
        if self.text.startswith("]", self.at):
            raise self.fail("an empty rule set holds no rule to import")
        while True:
            if len(rules) == MAX_RULES:
                raise self.fail(f"more than {MAX_RULES} rules")
            rules.append(self.rule())
            if self.text.startswith(" V ", self.at):
                self.at += 3
                continue
            break
        self.expect("]")
        if self.at != len(self.text):
            raise self.fail("text after the rule set")
        return rules

    def rule(self) -> list[tuple[str, bool]] | None:
        if self.text.startswith("[True]", self.at):
            self.at += len("[True]")
            return None
        self.expect("[")
        conditions = []
        while True:
            if len(conditions) == MAX_CONDITIONS:
                raise self.fail(f"more than {MAX_CONDITIONS} conditions in one rule")
            conditions.append(self.condition())
            if self.text.startswith("^", self.at):
                self.at += 1
                continue
            break
        self.expect("]")
        return conditions

    def condition(self) -> tuple[str, bool]:
        start = self.at
        name = _NAME_CHARS.match(self.text, self.at).group(0)
        if len(name) > MAX_NAME:
            raise self.fail(f"a column name longer than {MAX_NAME} characters")
        digits = name.rpartition("__")[2].lstrip("m")
        if len(digits) > MAX_DIGITS:
            raise self.fail(f"a threshold longer than {MAX_DIGITS} digits")
        if _column(name) is None:
            raise self.fail(f"{name!r} is not a column name the renderer writes")
        self.at += len(name)
        for spellings, value in ((TRUE_SPELLINGS, True), (FALSE_SPELLINGS, False)):
            for spelling in spellings:
                end = self.at + len(spelling)
                if self.text.startswith(spelling, self.at) and (
                        end == len(self.text) or self.text[end] in "]^"):
                    self.at = end
                    return name, value
        self.at = start + len(name)
        raise self.fail(f"{name} has a value that is not a binary spelling")


def parse_ruleset(text: str) -> dict[str, Any]:
    """A learned rule set as a ``gnd-ilp-clauses/1`` document, or a named refusal."""
    if _RULE_LIST.match(text):
        raise _refuse("ordered-rule-list", "a rule list is ordered; GND admits unordered rules only")
    rules = _Reader(text).ruleset()
    clauses = []
    for index, rule in enumerate(rules):
        if rule is None:
            raise _refuse(f"clause {index}: empty-antecedent", "the rule has no condition")
        if not all(value for _name, value in rule):
            raise _refuse(f"clause {index}: negation-as-failure", "the rule requires a feature to be false")
        if len(rule) > 1:
            raise _refuse(f"clause {index}: propositional-conjunction",
                          f"the rule conjoins {len(rule)} features")
        clauses.append(_clause(rule[0][0]))
    return {"schema_version": "gnd-ilp-clauses/1", "clauses": clauses}


def check_columns(document: dict[str, Any], neutral: dict[str, Any], text: str = "") -> None:
    """Refuse a rule whose column the feature table does not hold (IH0 finding A).

    wittgenstein only sees the columns of ``features.json``, so a column the
    export did not write is no rule it could have learned; the clause is refused
    ``off-threshold`` by index, as Popper's and ILASP's imports refuse an
    unoffered threshold. Every column of a declared ``gt``/``lt`` comparison
    at an integer position of a predicate of that arity is checked, whatever
    the two types, since a value subtype can let a cross-type join through the
    fragment table (IH0 fix review, finding 1). Any other is left to the
    fragment table, which names it (IL3's approved corpus). Every clause is :func:`_clause`'s
    shape, so its column name is spelled back from it; the TEXT is not needed."""
    written = {column["name"] for column in _columns(neutral)}
    arities = {row["name"]: row["types"] for row in neutral["predicates"]}
    comparisons = {row["name"]: row["type"] for row in neutral["comparisons"]
                   if row["operator"] in (">", "<")}
    integers = {row["type"] for row in neutral["comparisons"]}
    for index, clause in enumerate(document["clauses"]):
        fact, comparison = clause["body"][0]["atom"], clause["body"][1]["atom"]
        variable, constant = comparison["args"][0]["var"], comparison["args"][1]["const"]
        position, types = int(variable[1:]), arities.get(fact["predicate"])
        if types is None or len(types) != len(fact["args"]) or \
                comparison["predicate"] not in comparisons or types[position] not in integers:
            continue
        name = (f"{fact['predicate']}__{position}__{len(fact['args'])}__"
                f"{comparison['predicate']}__{_suffix(constant)}")
        if name not in written:
            raise IlpError(EXIT_ILL_FORMED, f"clause {index}: off-threshold: {name} is not a "
                           "column the export writes")


def extract_ruleset(stdout: str) -> str:
    """The one ``RULESET`` line's text, or ``""`` for none, several or an empty set."""
    found = [line.removesuffix("\r")[len(_PREFIX):] for line in stdout.split("\n")
             if line.startswith(_PREFIX)]
    if len(found) != 1 or found[0] == "[]":
        return ""
    return found[0]
