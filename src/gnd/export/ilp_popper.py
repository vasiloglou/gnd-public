"""The Popper adapter of the ILP bridge (IK5, D4 (o)): render and parse.

``render`` writes the neutral form as Popper's three inputs (``bk.pl``,
``exs.pl``, ``bias.pl``). ``parse_program`` reads Popper's printed program into
the neutral clause form ``gnd-ilp-clauses/1``. It is a closed tokenizer and
recursive-descent parser over a bounded input: anything outside its grammar is
:class:`~gnd.export.ilp.IlpError` ``unparsable`` with a line and column, and no
clause text is ever evaluated (IK-R5). Negation, disjunction and aggregates are
*parsed*, so that the fragment checker refuses them by name.

Whether a real Popper accepts this rendering is not established here (IK5-D13).
"""

from __future__ import annotations

import re
from typing import Any

from gnd.exits import EXIT_ILL_FORMED
from gnd.export.ilp import IlpError

__all__ = ["AGGREGATES", "parse_program", "quote", "render"]

AGGREGATES = frozenset({"findall", "bagof", "setof", "aggregate_all", "count", "sum", "max", "min"})
_OPERATORS = {">": ">", "<": "<", ">=": ">=", "=<": "<=", "=:=": "=", "=\\=": "!=", "=": "=",
              "\\=": "!="}
_SETTINGS = "max_vars(6).\nmax_body(5).\nmax_clauses(4).\n"
_TOKEN = re.compile(
    r"(?P<space>[ \t\r\n]+)|(?P<comment>%[^\n]*)"
    r"|(?P<neck>:-)|(?P<naf>\\\+)"
    r"|(?P<op>=:=|=\\=|\\=|>=|=<|>|<|=)"
    r"|(?P<punct>[(),.;])"
    r"|(?P<var>[A-Z_][A-Za-z0-9_]*)|(?P<name>[a-z][A-Za-z0-9_]*)"
    r"|(?P<int>-?[0-9]+)|(?P<quoted>'(?:[^'\\\n]|\\x[0-9a-fA-F]{1,6}\\|\\.)*')"
)
_ESCAPES = {"\\": "\\", "'": "'", "n": "\n", "t": "\t"}
MAX_DEPTH = 4
#: Longer than the clause schema's integer bound (2^53 - 1) and far below
#: Python's int-string conversion limit, so conversion never raises.
MAX_INT_DIGITS = 32


def quote(text: str) -> str:
    """A single-quoted Prolog atom; ``\\``, ``'`` and control characters escaped."""
    out = []
    for character in text:
        if character in "\\'":
            out.append("\\" + character)
        elif ord(character) < 32 or ord(character) == 127:
            out.append(f"\\x{ord(character):x}\\")
        else:
            out.append(character)
    return "'" + "".join(out) + "'"


def _term(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return quote(value)


def render(neutral: dict[str, Any]) -> dict[str, bytes]:
    lines = [f"{fact['predicate']}({quote(fact['example'])},"
             f"{','.join(_term(v) for v in fact['values'])}).\n" for fact in neutral["facts"]]
    prolog = {">=": ">=", ">": ">", "<=": "=<", "<": "<"}
    lines += [f"{row['name']}(A,B) :- A {prolog[row['operator']]} B.\n"
              for row in neutral["comparisons"]]
    examples = [f"{example['label']}(wrong({quote(example['id'])})).\n"
                for example in neutral["examples"]]
    bias = ["head_pred(wrong,1).\n", "type(wrong,(ex,)).\n"]
    for predicate in neutral["predicates"]:
        bias.append(f"body_pred({predicate['name']},{len(predicate['types'])}).\n")
        bias.append(f"type({predicate['name']},({','.join(predicate['types'])})).\n")
    for row in neutral["comparisons"]:
        bias.append(f"body_pred({row['name']},2).\n")
        bias.append(f"type({row['name']},({row['type']},{row['type']})).\n")
    bias += [f"magic_value_type({row['name']}).\n" for row in neutral["types"]
             if row["primitive"] == "integer"]
    bias.append(_SETTINGS)
    return {"popper/bk.pl": "".join(lines).encode("utf-8"),
            "popper/exs.pl": "".join(examples).encode("utf-8"),
            "popper/bias.pl": "".join(bias).encode("utf-8")}


class _Parser:
    def __init__(self, text: str) -> None:
        self.tokens: list[tuple[str, str, int, int]] = []
        line, start, position = 1, 0, 0
        while position < len(text):
            match = _TOKEN.match(text, position)
            if match is None:
                self._fail(line, position - start + 1, f"unexpected {text[position]!r}")
            kind = match.lastgroup
            value = match.group()
            if kind not in ("space", "comment"):
                self.tokens.append((kind, value, line, position - start + 1))
            newlines = value.count("\n")
            if newlines:
                line += newlines
                start = position + value.rindex("\n") + 1
            position = match.end()
        self.tokens.append(("end", "", line, position - start + 1))
        self.index = 0

    @staticmethod
    def _fail(line: int, column: int, detail: str) -> None:
        raise IlpError(EXIT_ILL_FORMED, f"unparsable: line {line}, column {column}: {detail}")

    def peek(self) -> tuple[str, str, int, int]:
        return self.tokens[self.index]

    def take(self, kind: str, value: str | None = None) -> str:
        token = self.peek()
        if token[0] != kind or (value is not None and token[1] != value):
            self._fail(token[2], token[3], f"expected {value or kind}, found {token[1] or 'end'!r}")
        self.index += 1
        return token[1]

    def at(self, kind: str, value: str | None = None) -> bool:
        token = self.peek()
        return token[0] == kind and (value is None or token[1] == value)

    def program(self) -> dict[str, Any]:
        clauses = []
        while not self.at("end"):
            clauses.append(self.clause())
        return {"schema_version": "gnd-ilp-clauses/1", "clauses": clauses}

    def clause(self) -> dict[str, Any]:
        predicate = self.take("name")
        args = self.arguments(goals=False) if self.at("punct", "(") else []
        body: list[Any] = []
        if self.at("neck"):
            self.take("neck")
            body = self.disjunction(0)
        self.take("punct", ".")
        return {"head": {"predicate": predicate, "args": args}, "body": body}

    def disjunction(self, depth: int) -> list[Any]:
        branches = [self.conjunction(depth)]
        while self.at("punct", ";"):
            self.take("punct", ";")
            branches.append(self.conjunction(depth))
        if len(branches) == 1:
            return branches[0]
        self.deep(depth + 1)
        return [{"or": branches}]

    def conjunction(self, depth: int) -> list[Any]:
        literals = self.literal(depth)
        while self.at("punct", ","):
            self.take("punct", ",")
            literals += self.literal(depth)
        return literals

    def deep(self, depth: int) -> None:
        if depth > MAX_DEPTH:
            token = self.peek()
            self._fail(token[2], token[3], f"nesting deeper than {MAX_DEPTH}")

    def literal(self, depth: int) -> list[Any]:
        if self.at("naf"):
            self.take("naf")
            self.deep(depth + 1)
            inner = self.literal(depth + 1)
            return [{"not": inner[0] if len(inner) == 1 else {"or": [inner]}}]
        if self.at("punct", "("):
            self.take("punct", "(")
            self.deep(depth + 1)
            inner = self.disjunction(depth + 1)
            self.take("punct", ")")
            return inner
        if self.at("name") and self.tokens[self.index + 1][:2] == ("punct", "("):
            name = self.take("name")
            if name == "not":
                self.take("punct", "(")
                self.deep(depth + 1)
                inner = self.disjunction(depth + 1)
                self.take("punct", ")")
                return [{"not": inner[0] if len(inner) == 1 else {"or": [inner]}}]
            if name in AGGREGATES:
                self.deep(depth + 1)
                return [{"aggregate": {"name": name,
                                       "args": self.arguments(goals=True, depth=depth + 1)}}]
            return [{"atom": {"predicate": name, "args": self.arguments(goals=False)}}]
        left = self.term()
        token = self.peek()
        if token[0] != "op":
            self._fail(token[2], token[3], f"expected a literal, found {token[1] or 'end'!r}")
        operator = _OPERATORS[self.take("op")]
        return [{"compare": {"operator": operator, "left": left, "right": self.term()}}]

    def arguments(self, *, goals: bool, depth: int = 0) -> list[Any]:
        self.take("punct", "(")
        args = [self.argument(goals, depth)]
        while self.at("punct", ","):
            self.take("punct", ",")
            args.append(self.argument(goals, depth))
        self.take("punct", ")")
        return args

    def argument(self, goals: bool, depth: int) -> Any:
        if not goals:
            return self.term()
        # An aggregate's goal may be an atom, a negation, a parenthesized
        # conjunction or a comparison; each parses as a literal so the
        # aggregate is refused by name, never as unparsable (IK5-Q3).
        compound = self.at("naf") or self.at("punct", "(")
        if compound or (self.at("name") and self.tokens[self.index + 1][:2] == ("punct", "(")):
            inner = self.literal(depth)
            return inner[0] if len(inner) == 1 else {"or": [inner]}
        left = self.term()
        if not self.at("op"):
            return left
        operator = _OPERATORS[self.take("op")]
        return {"compare": {"operator": operator, "left": left, "right": self.term()}}

    def term(self) -> dict[str, Any]:
        kind, value, line, column = self.peek()
        self.index += 1
        if kind == "var":
            return {"var": value}
        if kind == "name":
            return {"const": value}
        if kind == "int":
            if len(value.lstrip("-")) > MAX_INT_DIGITS:
                self._fail(line, column, f"an integer longer than {MAX_INT_DIGITS} digits")
            return {"const": int(value)}
        if kind == "quoted":
            return {"const": _unquote(value, line, column)}
        self._fail(line, column, f"expected a term, found {value or 'end'!r}")
        raise AssertionError  # pragma: no cover


def _unquote(token: str, line: int, column: int) -> str:
    out, body, position = [], token[1:-1], 0
    while position < len(body):
        character = body[position]
        if character != "\\":
            out.append(character)
            position += 1
            continue
        following = body[position + 1]
        if following in _ESCAPES:
            out.append(_ESCAPES[following])
            position += 2
            continue
        match = re.match(r"x([0-9a-fA-F]{1,6})\\", body[position + 1:])
        if match is None:
            raise IlpError(EXIT_ILL_FORMED, f"unparsable: line {line}, column {column}: "
                           "an unknown escape in a quoted atom")
        code = int(match.group(1), 16)
        if code > 0x10FFFF or 0xD800 <= code <= 0xDFFF:
            raise IlpError(EXIT_ILL_FORMED, f"unparsable: line {line}, column {column}: "
                           "an escape outside Unicode scalar values")
        out.append(chr(code))
        position += 1 + match.end()
    return "".join(out)


def parse_program(text: str) -> dict[str, Any]:
    """Popper's printed program as a ``gnd-ilp-clauses/1`` document (unvalidated)."""
    return _Parser(text).program()
