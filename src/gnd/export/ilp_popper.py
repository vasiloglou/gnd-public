"""The Popper adapter of the ILP bridge (IK5, D4 (o)): render and parse.

``render`` writes the neutral form as Popper's three inputs (``bk.pl``,
``exs.pl``, ``bias.pl``). ``parse_program`` reads Popper's printed program into
the neutral clause form ``gnd-ilp-clauses/1``. It is a closed tokenizer and
recursive-descent parser over a bounded input: anything outside its grammar is
:class:`~gnd.export.ilp.IlpError` ``unparsable`` with a line and column, and no
clause text is ever evaluated (IK-R5). Negation, disjunction and aggregates are
*parsed*, so that the fragment checker refuses them by name.

The rendering is adapter version 3 (IL1-A1 (o), IL1-A2 (o)), for Popper v5.0.1,
which has no magic values and so cannot bind a comparison's constant: each
comparison against an observed value is its own unary *threshold* predicate,
written as its extension over the exported values, ``gt_t_amount__120(150).``
and so on, so that Popper's clingo grounding and its unbound calls see it. ``parse_program`` maps a threshold atom back to the
binary comparison atom the neutral form declares.
"""

from __future__ import annotations

import re
from typing import Any

from gnd.exits import EXIT_ILL_FORMED
from gnd.export.ilp import COMPARISON_NAME, IlpError, observed_integers

__all__ = ["ADAPTER_VERSION", "AGGREGATES", "MAX_THRESHOLDS", "SOLUTION_BANNER", "extract_program",
           "parse_program", "quote", "render", "thresholds"]

#: ``export.json``'s ``adapter_version`` for the Popper target (IL1-A1 (o)).
ADAPTER_VERSION = "3"
#: Threshold values per integer type, fixed before results (IL1-A1-D3 (o)).
MAX_THRESHOLDS = 32
#: The comparison operators rendered as thresholds (IL1-A1-D2 (o)).
_THRESHOLD_OPERATORS = (">", "<")
#: A threshold atom: a comparison name, ``__`` and the value, negative as ``m``;
#: the value follows the last ``__``. ``ge`` and ``le`` are read, not rendered.
_THRESHOLD = re.compile(rf"({COMPARISON_NAME})__(m?)([0-9]+)")

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
    r"|(?P<int>-?[0-9]+)|(?P<quoted>'(?:[^'\\\n]|\\x[0-9a-fA-F]{1,6}\\|\\[0-7]+\\|\\.)*')"
)
#: SWI-Prolog 10.0.2 writeq writes code points 7-13 as these letters and every
#: other control as ``\xN\`` (IL1 spec §6; recorded in the IL1 review, finding 7).
_ESCAPES = {"\\": "\\", "'": "'", "n": "\n", "t": "\t", "a": "\a", "b": "\b", "v": "\v",
            "f": "\f", "r": "\r"}
MAX_DEPTH = 4
#: Longer than the clause schema's integer bound (2^53 - 1) and far below
#: Python's int-string conversion limit, so conversion never raises.
MAX_INT_DIGITS = 32
#: SWI writes a code point as a backslash, 1 to 7 octal digits and a backslash
#: (IK5-Q2). The tokenizer takes any digit count, so a longer escape reaches
#: :func:`_unquote` and is refused there with the octal message (IL1 spec §6).
MAX_OCTAL_DIGITS = 7
#: Popper v5.0.1 (commit 578a4e2) logs its solution to stderr: this banner, a
#: scores line, one rule per line, then a closing rule of stars. Each line
#: carries an elapsed-seconds prefix such as ``12.3s `` (IL1 spec §14, IL1-F4).
SOLUTION_BANNER = "*" * 10 + " SOLUTION " + "*" * 10
_ELAPSED = re.compile(r"^\d+(?:\.\d+)?s ")
_RULE = re.compile(r"wrong\(.*\.")


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


def thresholds(values: set[int]) -> list[int]:
    """The rendered thresholds of one integer type, ascending (IL1-A1-D3 (o)).

    Every distinct value up to :data:`MAX_THRESHOLDS`; above it, the values at
    ranks ``round(i * (n - 1) / 31)``, rounding half up, for i = 0..31 -- so the
    minimum and the maximum are always kept, and no rank repeats."""
    ordered = sorted(values)
    count = len(ordered)
    if count <= MAX_THRESHOLDS:
        return ordered
    span = MAX_THRESHOLDS - 1
    return [ordered[(2 * i * (count - 1) + span) // (2 * span)] for i in range(MAX_THRESHOLDS)]


def _suffix(value: int) -> str:
    return f"m{-value}" if value < 0 else str(value)


def _threshold_rows(neutral: dict[str, Any]) -> list[tuple[str, str, list[int]]]:
    """``(name, type, extension)`` per rendered threshold predicate, in render order.

    The extension is the observed values of the type the comparison holds for,
    ascending; a threshold whose extension is empty is not rendered (IL1-A2-D2 (o))."""
    observed = observed_integers(neutral)
    rows = []
    for row in neutral["comparisons"]:
        if row["operator"] in _THRESHOLD_OPERATORS:
            values = sorted(observed.get(row["type"], set()))
            for value in thresholds(set(values)):
                holds = [w for w in values if (w > value if row["operator"] == ">" else w < value)]
                if holds:
                    rows.append((f"{row['name']}__{_suffix(value)}", row["type"], holds))
    return rows


def render(neutral: dict[str, Any]) -> dict[str, bytes]:
    position = {example["id"]: index for index, example in enumerate(neutral["examples"])}
    # Grouped by predicate, so each predicate's clauses are contiguous; the
    # neutral order (example position, predicate, values) is stable within.
    facts = sorted(neutral["facts"], key=lambda fact: (fact["predicate"], position[fact["example"]]))
    lines = [f"{fact['predicate']}({quote(fact['example'])},"
             f"{','.join(_term(v) for v in fact['values'])}).\n" for fact in facts]
    rows = _threshold_rows(neutral)
    # Ground facts, not rules: Popper v5.0.1 grounds bk.pl in clingo and calls
    # predicates unbound, and a rule-defined threshold has no atoms there
    # (IL1-A2 (o), review finding 2).
    lines += [f"{name}({value}).\n" for name, _type, holds in rows for value in holds]
    examples = [f"{example['label']}(wrong({quote(example['id'])})).\n"
                for example in neutral["examples"]]
    bias = ["head_pred(wrong,1).\n", "type(wrong,(ex,)).\n"]
    for predicate in neutral["predicates"]:
        bias.append(f"body_pred({predicate['name']},{len(predicate['types'])}).\n")
        bias.append(f"type({predicate['name']},({','.join(predicate['types'])})).\n")
    for name, type_name, _holds in rows:
        bias.append(f"body_pred({name},1).\n")
        bias.append(f"type({name},({type_name},)).\n")
    bias.append(_SETTINGS)
    return {"popper/bk.pl": "".join(lines).encode("utf-8"),
            "popper/exs.pl": "".join(examples).encode("utf-8"),
            "popper/bias.pl": "".join(bias).encode("utf-8")}


def _unparsable(line: int, column: int, detail: str) -> IlpError:
    """The parser's one refusal: ``unparsable`` with a line and column (IK-R5)."""
    return IlpError(EXIT_ILL_FORMED, f"unparsable: line {line}, column {column}: {detail}")


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
        raise _unparsable(line, column, detail)

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
            line, column = self.peek()[2:]
            return [{"atom": _comparison(name, self.arguments(goals=False), line, column)}]
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


def _comparison(name: str, args: list[Any], line: int, column: int) -> dict[str, Any]:
    """An atom; a one-argument threshold atom becomes its binary comparison atom,
    so the fragment checks see the declared comparison and its type (D13 (o))."""
    match = _THRESHOLD.fullmatch(name)
    if match is None or len(args) != 1:
        return {"predicate": name, "args": args}
    comparison, sign, digits = match.groups()
    if (len(digits) > 1 and digits[0] == "0") or (sign and digits == "0"):
        # The renderer writes neither a leading zero nor m0 (IL2-D8 (o), IL1-Q3).
        raise _unparsable(line, column, f"a threshold name the renderer never writes: {name}")
    if len(digits) > MAX_INT_DIGITS:
        raise _unparsable(line, column, f"an integer longer than {MAX_INT_DIGITS} digits")
    return {"predicate": comparison, "args": [args[0], {"const": -int(digits) if sign else int(digits)}]}


def _unquote(token: str, line: int, column: int) -> str:
    out, body, position = [], token[1:-1], 0
    while position < len(body):
        character = body[position]
        if character != "\\":
            out.append(character)
            position += 1
            continue
        if position + 1 == len(body):
            # The tokenizer read a final ``\\`` pair that an octal escape
            # before it consumed half of (IL1 review, finding 1).
            raise _unparsable(line, column, "a backslash ends a quoted atom")
        following = body[position + 1]
        if following in _ESCAPES:
            out.append(_ESCAPES[following])
            position += 2
            continue
        if following in "01234567":
            out.append(_octal(body[position + 1:], line, column))
            position = body.index("\\", position + 1) + 1
            continue
        match = re.match(r"x([0-9a-fA-F]{1,6})\\", body[position + 1:])
        if match is None:
            raise _unparsable(line, column, "an unknown escape in a quoted atom")
        code = int(match.group(1), 16)
        if code > 0x10FFFF or 0xD800 <= code <= 0xDFFF:
            raise _unparsable(line, column, "an escape outside Unicode scalar values")
        out.append(chr(code))
        position += 1 + match.end()
    return "".join(out)


def _octal(rest: str, line: int, column: int) -> str:
    """The character of an octal escape whose digits start ``rest``."""
    def refuse(detail: str) -> IlpError:
        return _unparsable(line, column, f"an octal escape {detail}")

    match = re.match(r"([0-7]+)\\", rest)
    if match is None:
        raise refuse("without its closing backslash")
    digits = match.group(1)
    if len(digits) > MAX_OCTAL_DIGITS:
        raise refuse(f"longer than {MAX_OCTAL_DIGITS} digits")
    code = int(digits, 8)
    if code > 0x10FFFF or 0xD800 <= code <= 0xDFFF:
        raise refuse("outside Unicode scalar values")
    return chr(code)


def extract_program(log: str) -> str:
    """The learned program in Popper's log, one rule per line; ``""`` if none.

    The program is the first maximal run of ``wrong(...).`` lines after the last
    :data:`SOLUTION_BANNER`, each with its elapsed-seconds prefix removed. Linear
    in the log; the log itself is bounded by the run's process limits."""
    lines = [_ELAPSED.sub("", line, count=1).strip() for line in log.splitlines()]
    banners = [index for index, line in enumerate(lines) if line == SOLUTION_BANNER]
    if not banners:
        return ""
    program: list[str] = []
    for line in lines[banners[-1] + 1:]:
        if _RULE.fullmatch(line):
            program.append(line)
        elif program:
            break
    return "".join(f"{line}\n" for line in program)


def parse_program(text: str) -> dict[str, Any]:
    """Popper's printed program as a ``gnd-ilp-clauses/1`` document (unvalidated)."""
    return _Parser(text).program()
