"""The ILASP adapter of the ILP bridge (ilp-learners IL2).

``render`` writes one ILASP learning task, ``ilasp/task.las``, from the neutral
form; ``parse_hypothesis`` reads the learned hypothesis back into the clause
form, as the exact inverse of that rendering, and hands it to the shared
fragment checker. Spec: ``.gnd-planning/milestones/ilp-learners/notes/phase-IL2-spec.md``
§6 (r1, approved 2026-10-27).

The reader is closed, capped and total (standing rule 1): ILASP's output is
untrusted text (IL-R6), never evaluated. A construct the clause form cannot
carry is refused by name here; ``not`` and aggregates are carried, so that the
fragment checker refuses them under its own names.
"""

from __future__ import annotations

import re
from typing import Any

from gnd.exits import EXIT_ILL_FORMED
from gnd.export.ilp import IlpError
from gnd.export.ilp_popper import thresholds

__all__ = ["ADAPTER_VERSION", "REFUSALS", "context_fact", "extract_hypothesis",
           "parse_hypothesis", "render", "split_task"]

ADAPTER_VERSION = "1"

#: The comparisons rendered, as IL1-A1-D2 (o) chose for Popper.
_OPERATORS = {">": "gt", "<": "lt"}
#: The rendered bias bounds (IL2-D5 (o)).
_BIAS = "#maxv(4).\n"
_PREDICATE_RECALL = 2
_COMPARISON_RECALL = 1

#: Every construct the reader refuses by name (spec §6, "Reader").
REFUSALS = ("asp-constraint", "choice-rule", "weak-constraint", "classical-negation",
            "arithmetic-term", "interval-or-pool", "directive", "builtin-comparison",
            "empty-body", "disjunction", "head-shape")

MAX_RULES = 32
MAX_LITERALS = 16
MAX_DEPTH = 4
MAX_INT_DIGITS = 32
#: clingo's integers are 32-bit; a wider one would mean something else to it.
_INT_RANGE = range(-2**31, 2**31)
#: A comparison atom is copied as is; every other body atom takes the example variable.
_COMPARISON = re.compile(r"(?:gt|lt|ge|le)_t_[A-Za-z0-9_]+")
#: The comparisons the task defines; ge and le are declared but never rendered.
_RENDERED_COMPARISON = re.compile(r"(?:gt|lt)_t_[A-Za-z0-9_]+")
#: clingo reads an identifier that starts with underscores and then a lowercase letter as a constant.
_UNDERSCORE_CONSTANT = re.compile(r"_+[a-z]")
_COMPARE_OPS = frozenset({"<", "<=", "=", "==", "!=", "<>", ">=", ">"})
_ARITHMETIC = frozenset({"+", "-", "*", "/", "\\", "**", "&", "?", "^"})
_AGGREGATES = frozenset({"count", "sum", "sum+", "min", "max"})
_ESCAPES = {"\\": "\\", '"': '"', "n": "\n"}
_TOKEN = re.compile(r"""
    (?P<space>[ \t\r\n]+)
  | (?P<comment>%[^\n]*)
  | (?P<string>"(?:[^"\\\n]|\\.)*")
  | (?P<open_string>")
  | (?P<int>[0-9]+)
  | (?P<var>[A-Z_][A-Za-z0-9_']*)
  | (?P<name>[a-z][A-Za-z0-9_']*)
  | (?P<hash>\#[a-z_]+\+?)
  | (?P<op>:-|:~|\.\.|<=|>=|!=|<>|==|\*\*|[.,;:|(){}\[\]@<>=+\-*/\\])
""", re.VERBOSE)


# ---------------------------------------------------------------------------
# Rendering.
# ---------------------------------------------------------------------------

def _term(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    out = []
    for character in value:
        if character in '\\"':
            out.append("\\" + character)
        elif character == "\n":
            out.append("\\n")
        elif ord(character) < 32 or ord(character) == 127:
            raise IlpError(EXIT_ILL_FORMED, f"unrepresentable: {value!r} holds a control "
                           "character an ASP string cannot escape")
        else:
            out.append(character)
    return '"' + "".join(out) + '"'


def context_fact(fact: dict[str, Any]) -> str:
    """One context line: the fact without its example argument."""
    return f"{fact['predicate']}({','.join(_term(v) for v in fact['values'])}).\n"


def _domains(neutral: dict[str, Any]) -> list[tuple[str, list[str], list[int], list[dict[str, Any]]]]:
    """``(type, dom rules, thresholds, comparisons)`` per rendered integer type, by name."""
    types = {row["name"]: row["types"][1:] for row in neutral["predicates"]}
    observed: dict[str, set[int]] = {}
    for fact in neutral["facts"]:
        for type_name, value in zip(types[fact["predicate"]], fact["values"], strict=True):
            if isinstance(value, int) and not isinstance(value, bool):
                observed.setdefault(type_name, set()).add(value)
    rows = []
    for type_name in sorted(observed):
        comparisons = sorted((row for row in neutral["comparisons"]
                              if row["type"] == type_name and row["operator"] in _OPERATORS),
                             key=lambda row: row["name"])
        if not comparisons:
            continue
        rules = []
        for predicate in neutral["predicates"]:
            argument_types = predicate["types"][1:]
            for position, argument_type in enumerate(argument_types):
                if argument_type == type_name:
                    args = ["V" if i == position else "_" for i in range(len(argument_types))]
                    rules.append(f"dom_{type_name}(V) :- {predicate['name']}({','.join(args)}).\n")
        rows.append((type_name, rules, thresholds(observed[type_name]), comparisons))
    return rows


def render(neutral: dict[str, Any]) -> dict[str, bytes]:
    domains = _domains(neutral)
    lines: list[str] = []
    # The background holds the comparison definitions only (plan §2). dom_t
    # binds X from the context's own facts and thr_t binds C from ground
    # facts, so a learner that grounds the background sees every comparison
    # atom (IL1 refuted premise 4).
    for type_name, rules, values, comparisons in domains:
        lines += rules
        lines += [f"thr_{type_name}({value}).\n" for value in values]
        lines += [f"{row['name']}(X, C) :- dom_{type_name}(X), thr_{type_name}(C), "
                  f"X {row['operator']} C.\n" for row in comparisons]
    lines.append("\n")
    for type_name, _rules, values, _comparisons in domains:
        lines += [f"#constant({type_name}, {value}).\n" for value in values]
    lines.append("\n#modeh(wrong).\n")
    for predicate in neutral["predicates"]:
        args = ", ".join(f"var({t})" for t in predicate["types"][1:])
        lines.append(f"#modeb({_PREDICATE_RECALL}, {predicate['name']}({args})).\n")
    for type_name, _rules, _values, comparisons in domains:
        lines += [f"#modeb({_COMPARISON_RECALL}, {row['name']}(var({type_name}), "
                  f"const({type_name}))).\n" for row in comparisons]
    lines.append(_BIAS)
    by_example: dict[str, list[dict[str, Any]]] = {}
    for fact in sorted(neutral["facts"], key=lambda fact: fact["predicate"]):
        by_example.setdefault(fact["example"], []).append(fact)
    for index, example in enumerate(neutral["examples"], 1):
        lines.append(f"\n#{example['label']}(e{index}, {{wrong}}, {{}}, {{\n")
        lines += [context_fact(fact) for fact in by_example.get(example["id"], [])]
        lines.append("}).\n")
    return {"ilasp/task.las": "".join(lines).encode("utf-8")}


def split_task(task: str) -> tuple[str, list[str]]:
    """The rendered background, and each example's context, in example order."""
    background = task.split("\n\n", 1)[0] + "\n"
    contexts = re.findall(r"^#(?:pos|neg)\(e\d+, \{wrong\}, \{\}, \{\n(.*?)^\}\)\.$",
                          task, re.MULTILINE | re.DOTALL)
    return background, contexts


# ---------------------------------------------------------------------------
# The hypothesis extractor and reader.
# ---------------------------------------------------------------------------

def extract_hypothesis(log: str) -> str:
    """The learned hypothesis in ILASP's output, one rule per line; ``""`` if none.

    ILASP 4.4.1 prints its ``%%`` timing block first and the hypothesis after
    it (the IL2-D4 probe, IL2-F5). The hypothesis is the first maximal run of
    non-blank lines after the last line that starts with ``%%``, whatever
    their heads, so the reader refuses a learned constraint by name; a line
    that is exactly ``UNSATISFIABLE`` means none, although ILASP still exits 0."""
    lines = [line.strip() for line in log.splitlines()]
    if "UNSATISFIABLE" in lines:
        return ""
    banners = [index for index, line in enumerate(lines) if line.startswith("%%")]
    program: list[str] = []
    for line in lines[banners[-1] + 1 if banners else 0:]:
        if line:
            program.append(line)
        elif program:
            break
    return "".join(f"{line}\n" for line in program)


def refusal_name(message: str) -> str:
    """The refusal name in an import's exit-3 message: ``clause K: <name>: ...`` or ``<name>: ...``."""
    return message.split(": ")[1] if message.startswith("clause ") else message.split(":")[0]


def _unparsable(line: int, column: int, detail: str) -> IlpError:
    return IlpError(EXIT_ILL_FORMED, f"unparsable: line {line}, column {column}: {detail}")


class _Reader:
    def __init__(self, text: str) -> None:
        self.tokens: list[tuple[str, str, int, int]] = []
        line, start, position = 1, 0, 0
        while position < len(text):
            match = _TOKEN.match(text, position)
            column = position - start + 1
            if match is None:
                raise _unparsable(line, column, f"unexpected {text[position]!r}")
            kind, value = match.lastgroup, match.group()
            if kind == "open_string":
                raise _unparsable(line, column, "an unterminated string")
            if kind == "comment" and value.startswith("%*"):
                raise _unparsable(line, column, "a block comment")
            if kind in ("var", "name") and "'" in value:
                raise _unparsable(line, column, "a primed identifier")
            if kind == "var" and _UNDERSCORE_CONSTANT.match(value):
                raise _unparsable(line, column, "an underscore-prefixed constant")
            if kind not in ("space", "comment"):
                self.tokens.append((kind, value, line, column))
            newlines = value.count("\n")
            if newlines:
                line += newlines
                start = position + value.rindex("\n") + 1
            position = match.end()
        self.tokens.append(("end", "", line, position - start + 1))
        self.index = 0
        self.rule = 0

    # -- tokens --------------------------------------------------------------

    def peek(self, ahead: int = 0) -> tuple[str, str, int, int]:
        return self.tokens[min(self.index + ahead, len(self.tokens) - 1)]

    def at(self, kind: str, value: str | None = None, ahead: int = 0) -> bool:
        token = self.peek(ahead)
        return token[0] == kind and (value is None or token[1] == value)

    def take(self, kind: str, value: str | None = None) -> str:
        token = self.peek()
        if token[0] != kind or (value is not None and token[1] != value):
            raise _unparsable(token[2], token[3], f"expected {value or kind}, found {token[1] or 'end'!r}")
        self.index += 1
        return token[1]

    def refuse(self, name: str, detail: str) -> IlpError:
        token = self.peek()
        return IlpError(EXIT_ILL_FORMED, f"clause {self.rule}: {name}: line {token[2]}, "
                        f"column {token[3]}: {detail}")

    def deep(self, depth: int) -> None:
        if depth > MAX_DEPTH:
            token = self.peek()
            raise _unparsable(token[2], token[3], f"nesting deeper than {MAX_DEPTH}")

    # -- rules ---------------------------------------------------------------

    def hypothesis(self) -> dict[str, Any]:
        clauses = []
        while not self.at("end"):
            if len(clauses) == MAX_RULES:
                token = self.peek()
                raise _unparsable(token[2], token[3], f"more than {MAX_RULES} rules")
            self.rule = len(clauses)
            clauses.append(self.statement())
        return {"schema_version": "gnd-ilp-clauses/1", "clauses": clauses}

    def statement(self) -> dict[str, Any]:
        kind, value = self.peek()[:2]
        if kind == "hash":
            raise self.refuse("directive", f"{value} is a directive")
        if (kind, value) == ("op", ":-"):
            raise self.refuse("asp-constraint", "a rule without a head")
        if (kind, value) == ("op", ":~"):
            raise self.refuse("weak-constraint", "a weak constraint")
        if kind == "int" or (kind, value) == ("op", "{"):
            raise self.refuse("choice-rule", "a choice head")
        if (kind, value) == ("op", "-"):
            raise self.refuse("classical-negation", "a classically negated head")
        predicate = self.take("name")
        args = self.arguments(0) if self.at("op", "(") else None
        if self.at("op", "|") or self.at("op", ";"):
            raise self.refuse("disjunction", "a disjunctive head")
        if predicate != "wrong" or args is not None:
            raise self.refuse("head-shape", "the head must be wrong, with no arguments")
        if self.at("op", "."):
            raise self.refuse("empty-body", "a rule without a body")
        self.take("op", ":-")
        body = [self.literal(0)]
        while self.at("op", ","):
            self.take("op", ",")
            if len(body) == MAX_LITERALS:
                token = self.peek()
                raise _unparsable(token[2], token[3], f"more than {MAX_LITERALS} body literals")
            body.append(self.literal(0))
        self.take("op", ".")
        return _thread(body)

    def literal(self, depth: int) -> dict[str, Any]:
        self.deep(depth)
        kind, value = self.peek()[:2]
        if (kind, value) == ("name", "not"):
            self.take("name")
            return {"not": self.literal(depth + 1)}
        if (kind, value) == ("op", "-") and self.at("name", ahead=1):
            raise self.refuse("classical-negation", "a classically negated literal")
        if kind == "hash":
            if value[1:] not in _AGGREGATES:
                raise self.refuse("directive", f"{value} in a body")
            return self.aggregate(depth + 1)
        if kind == "name":
            line, column = self.peek()[2:]
            name = self.take("name")
            args = self.arguments(depth) if self.at("op", "(") else []
            self.no_comparison()
            if _COMPARISON.fullmatch(name):
                _rendered_comparison(name, args, line, column)
            return {"atom": {"predicate": name, "args": args}}
        self.term(depth)
        self.no_comparison()
        token = self.peek()
        raise _unparsable(token[2], token[3], f"expected a literal, found {token[1] or 'end'!r}")

    def no_comparison(self) -> None:
        if self.peek()[0] == "op" and self.peek()[1] in _COMPARE_OPS:
            raise self.refuse("builtin-comparison", "an infix comparison (IL2-D6)")

    def aggregate(self, depth: int) -> dict[str, Any]:
        self.deep(depth)
        name = self.take("hash")[1:]
        self.take("op", "{")
        args: list[Any] = []
        while not self.at("op", "}"):
            args.append(self.term(depth))
            while self.at("op", ","):
                self.take("op", ",")
                args.append(self.term(depth))
            if self.at("op", ":"):
                self.take("op", ":")
                args.append(self.literal(depth + 1))
                while self.at("op", ","):
                    self.take("op", ",")
                    args.append(self.literal(depth + 1))
            if not self.at("op", ";"):
                break
            self.take("op", ";")
        self.take("op", "}")
        # The guard is not represented: the fragment checker refuses any
        # aggregate by name (check 2), whatever its bound.
        if self.peek()[0] == "op" and self.peek()[1] in _COMPARE_OPS:
            self.take("op")
            self.term(depth)
        return {"aggregate": {"name": name, "args": args}}

    def arguments(self, depth: int) -> list[Any]:
        self.take("op", "(")
        args = [self.term(depth)]
        while self.at("op", ","):
            self.take("op", ",")
            args.append(self.term(depth))
        if self.at("op", ";"):
            raise self.refuse("interval-or-pool", "a pool")
        self.take("op", ")")
        return args

    def term(self, depth: int) -> dict[str, Any]:
        kind, value, line, column = self.peek()
        if (kind, value) == ("op", "-"):
            if not self.at("int", ahead=1):
                raise self.refuse("arithmetic-term", "a unary minus")
            self.take("op")
            term = self.integer(negative=True)
        elif kind == "int":
            term = self.integer(negative=False)
        elif kind == "var":
            term = {"var": self.take("var")}
        elif kind == "name":
            self.take("name")
            if self.at("op", "("):
                raise _unparsable(line, column, "a function term")
            term = {"const": {"true": True, "false": False}.get(value, value)}
        elif kind == "string":
            self.take("string")
            term = {"const": _unquote(value, line, column)}
        elif (kind, value) == ("op", "("):
            raise self.refuse("arithmetic-term", "a parenthesized term")
        else:
            raise _unparsable(line, column, f"expected a term, found {value or 'end'!r}")
        if self.at("op", ".."):
            raise self.refuse("interval-or-pool", "an interval")
        if self.peek()[0] == "op" and self.peek()[1] in _ARITHMETIC:
            raise self.refuse("arithmetic-term", f"the operator {self.peek()[1]!r}")
        return term

    def integer(self, *, negative: bool) -> dict[str, Any]:
        _kind, digits, line, column = self.peek()
        if len(digits) > MAX_INT_DIGITS:
            raise _unparsable(line, column, f"an integer longer than {MAX_INT_DIGITS} digits")
        if len(digits) > 1 and digits[0] == "0":
            raise _unparsable(line, column, "a leading zero")
        self.take("int")
        value = -int(digits) if negative else int(digits)
        if value not in _INT_RANGE:
            raise _unparsable(line, column, "outside clingo's 32-bit integer range")
        return {"const": value}


def _rendered_comparison(name: str, args: list[Any], line: int, column: int) -> None:
    """A comparison atom has the one shape the task defines: ``gt_t(var, threshold)``, or ``lt_t``."""
    if not _RENDERED_COMPARISON.fullmatch(name):
        raise _unparsable(line, column, "a comparison the renderer never writes")
    if (len(args) != 2 or "var" not in args[0] or "const" not in args[1]
            or type(args[1]["const"]) is not int):
        raise _unparsable(line, column, "a comparison must be (variable, integer)")


def _unquote(token: str, line: int, column: int) -> str:
    out, body, position = [], token[1:-1], 0
    while position < len(body):
        character = body[position]
        if character == "\\":
            following = body[position + 1]
            if following not in _ESCAPES:
                raise _unparsable(line, column, "an unknown escape in a string")
            out.append(_ESCAPES[following])
            position += 2
        else:
            out.append(character)
            position += 1
    return "".join(out)


def _variables(node: Any) -> set[str]:
    if isinstance(node, dict):
        found = {node["var"]} if "var" in node else set()
        for value in node.values():
            found |= _variables(value)
        return found
    if isinstance(node, list):
        return set().union(*(_variables(value) for value in node)) if node else set()
    return set()


def _threaded(literal: Any, example: dict[str, str]) -> Any:
    if "atom" in literal:
        atom = literal["atom"]
        if _COMPARISON.fullmatch(atom["predicate"]):
            return literal
        return {"atom": {"predicate": atom["predicate"], "args": [example, *atom["args"]]}}
    if "not" in literal:
        return {"not": _threaded(literal["not"], example)}
    if "aggregate" in literal:
        aggregate = literal["aggregate"]
        return {"aggregate": {"name": aggregate["name"], "args": [
            _threaded(arg, example) if "atom" in arg or "not" in arg else arg
            for arg in aggregate["args"]]}}
    return literal


def _thread(body: list[dict[str, Any]]) -> dict[str, Any]:
    """``wrong :- body.`` as ``wrong(X) :- body'``, X fresh: the rendering's inverse."""
    used = _variables(body)
    name = next(n for n in ["X", *(f"X{i}" for i in range(len(used) + 1))] if n not in used)
    example = {"var": name}
    return {"head": {"predicate": "wrong", "args": [example]},
            "body": [_threaded(literal, example) for literal in body]}


def parse_hypothesis(text: str) -> dict[str, Any]:
    """ILASP's printed hypothesis as a ``gnd-ilp-clauses/1`` document (unvalidated)."""
    return _Reader(text).hypothesis()
