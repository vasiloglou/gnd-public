"""Judgement files for the fact-type family, ``gnd-type-judgements/1`` (TS2).

A judgement skill reads one ``gnd-type-evidence/1`` file and writes verdicts:
``distinct`` or ``duplicate`` for the groups a signature decides today, and
``many-to-many`` or ``skip`` for the multi-valued ones. This module reads such
a file, binds it to the evidence by the evidence's raw-byte digest, and checks
every verdict against facts the evidence already states. It decides nothing:
a verdict the data contradicts is refused, never repaired. Schema:
``src/gnd/type-judgements.schema.json``; the rules live in the "Type
judgements" section of ``docs/reference/discover.md``.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gnd import input_policy as _rf7_input
from gnd.json_input import JsonInputRefusal, bounded_json

FORMAT = "gnd-type-judgements/1"
MAX_JUDGEMENTS_BYTES = 10 * 1024 * 1024
OPTIONS = {"duplicates": "--duplicate-judgements", "shapes": "--shape-judgements"}
VERDICTS = {"duplicates": ("distinct", "duplicate"), "shapes": ("many-to-many", "skip")}
# Which evidence statuses each kind judges (coverage, plan TS-D9).
ELIGIBLE = {"duplicates": ("proposed", "shape_match", "over_budget"), "shapes": ("multi_valued",)}
_GROUP = re.compile(r"g(0|[1-9][0-9]*)")
_TOKEN = re.compile(r"\w+|\s+|[^\w\s]")
_WORD = re.compile(r"\w+")


class TypeJudgementError(ValueError):
    """A judgements file that is unreadable, unbound, incomplete or contradicted (exit 3)."""


@dataclass(frozen=True)
class Verdict:
    group: int
    verdict: str
    of: str | None
    kind: str


def _schema() -> Draft202012Validator:
    text = files("gnd").joinpath("type-judgements.schema.json").read_text(encoding="utf-8")
    return Draft202012Validator(_rf7_input.loads(text))


def read(path: Path, *, kind: str) -> tuple[dict[str, Any], str]:
    """One schema-valid judgements file of ``kind`` and the SHA-256 of its bytes.

    Total over any bytes: the cap is applied to the read, and every refusal is
    a ``TypeJudgementError`` whose message names a location, never a value.
    """
    option = OPTIONS[kind]
    with path.open("rb") as handle:
        raw = handle.read(MAX_JUDGEMENTS_BYTES + 1)
    if len(raw) > MAX_JUDGEMENTS_BYTES:
        raise TypeJudgementError(f"{option}: the file exceeds {MAX_JUDGEMENTS_BYTES} bytes")
    try:
        document = bounded_json(raw, max_bytes=MAX_JUDGEMENTS_BYTES)
    except JsonInputRefusal as error:
        reason = str(error).replace("proposal", "file")
        raise TypeJudgementError(f"{option}: {reason}") from None
    errors = sorted(_schema().iter_errors(document), key=lambda e: list(e.absolute_path))
    if errors:
        # The instance may hold a rationale; name only where and which rule.
        raise TypeJudgementError(f"{option}: {errors[0].json_path} fails the schema ({errors[0].validator})")
    if document["kind"] != kind:
        raise TypeJudgementError(f"{option}: kind is {document['kind']!r}, expected {kind!r}")
    return document, hashlib.sha256(raw).hexdigest()


def check_binding(document: dict[str, Any], *, kind: str, evidence_sha256: str) -> None:
    if document["evidence_sha256"] != evidence_sha256:
        raise TypeJudgementError(f"{OPTIONS[kind]}: evidence_sha256 is not the digest of --type-evidence-in")


def bind(evidence: dict[str, Any], documents: dict[str, dict[str, Any]], *,
         induced: dict[int, list[str]] | None = None) -> dict[int, Verdict]:
    """Every verdict, checked for coverage and against the evidence (TS-R2).

    ``induced`` maps a group's position to the fact types whose
    ``induced_from`` names its attribute. The caller computes it from the
    whole model, so D4 holds also for a group whose candidates the evidence
    cap left out (review F1); the listed candidates are checked as well.
    """
    if evidence["truncated_groups"]:
        raise TypeJudgementError(
            f"--type-evidence-in: {evidence['truncated_groups']} groups were left out under the evidence cap, "
            "so they cannot be judged")
    groups = evidence["groups"]
    found: dict[int, Verdict] = {}
    for kind, document in documents.items():
        option = OPTIONS[kind]
        for index, entry in enumerate(document["verdicts"]):
            where = f"{option} verdict {index}"
            match = _GROUP.fullmatch(entry["group"])
            number = None if match is None else int(match.group(1))
            if number is None or number >= len(groups):
                raise TypeJudgementError(f"{where}: group {entry['group']} is not in the evidence")
            group = groups[number]
            if entry["generic"] != group["generic"]:
                raise TypeJudgementError(f"{where}: group {entry['group']} is of another generic fact type")
            if group["status"] not in ELIGIBLE[kind]:
                raise TypeJudgementError(
                    f"{where}: group {entry['group']} has status {group['status']}, which {option} does not judge")
            if number in found:
                raise TypeJudgementError(f"{where}: group {entry['group']} is judged twice")
            verdict = entry["verdict"]
            if verdict not in VERDICTS[kind]:
                raise TypeJudgementError(f"{where}: {verdict!r} is not a {kind} verdict")
            candidates = {candidate["fact_type"]: candidate for candidate in group["candidates"]}
            of = entry.get("of")
            if (verdict == "duplicate") != (of is not None):
                raise TypeJudgementError(f"{where}: 'of' goes with a duplicate verdict, and only with one")
            if verdict == "duplicate" and of not in candidates:
                raise TypeJudgementError(
                    f"{where}: 'of' is not a candidate of group {entry['group']} in the evidence"
                    + (" (candidates were truncated)" if evidence["truncated"] else ""))
            if verdict in ("distinct", "many-to-many"):
                # D4: the attribute was already induced into that fact type.
                already = list((induced or {}).get(number, []))
                already += [candidate["fact_type"] for candidate in candidates.values()
                            if candidate["origin"] is not None and candidate["origin"]["generic"] == group["generic"]
                            and candidate["origin"]["same_attribute"]]
                if already:
                    raise TypeJudgementError(
                        f"{where}: group {entry['group']} was already induced as {min(already)}")
            found[number] = Verdict(group=number, verdict=verdict, of=of, kind=kind)
        missing = [f"g{n}" for n, group in enumerate(groups)
                   if group["status"] in ELIGIBLE[kind] and n not in found]
        if missing:
            raise TypeJudgementError(f"{option}: group {missing[0]} has no verdict ({len(missing)} missing)")
    return found


def _tokens(text: str) -> list[str]:
    """Case-folded tokens: a word run, a whitespace run (as one space) or one other character.

    A non-word token is tagged with whether a word character touches it on
    the left and on the right, so equal token sequences match exactly where
    the characters on either side of a text are not letters, digits or ``_``
    (review F3). A pattern is tokenised alone, so its own edges are untouched.
    """
    pieces = [" " if piece.isspace() else piece for piece in _TOKEN.findall(text.casefold())]
    words = [_WORD.fullmatch(piece) is not None for piece in pieces]
    tokens = []
    for index, piece in enumerate(pieces):
        if words[index]:
            tokens.append(piece)
            continue
        left = index > 0 and words[index - 1]
        right = index + 1 < len(pieces) and words[index + 1]
        # A word token is all word characters, so a tagged one never equals it.
        tokens.append(f"{int(left)}{int(right)}{piece}")
    return tokens


class _Matcher:
    """Aho–Corasick over token sequences: one pass per text, whatever the pattern count."""

    def __init__(self, patterns: list[tuple[str, ...]]):
        self.goto: list[dict[str, int]] = [{}]
        self.ends: list[int | None] = [None]
        for number, pattern in enumerate(patterns):
            node = 0
            for token in pattern:
                following = self.goto[node].get(token)
                if following is None:
                    following = len(self.goto)
                    self.goto[node][token] = following
                    self.goto.append({})
                    self.ends.append(None)
                node = following
            if self.ends[node] is None:
                self.ends[node] = number
        self.fail = [0] * len(self.goto)
        # The nearest proper suffix node that ends a pattern.
        self.link: list[int | None] = [None] * len(self.goto)
        queue = list(self.goto[0].values())
        for node in queue:
            for token, following in self.goto[node].items():
                queue.append(following)
                back = self.fail[node]
                while back and token not in self.goto[back]:
                    back = self.fail[back]
                target = self.goto[back].get(token, 0)
                self.fail[following] = target if target != following else 0
                parent = self.fail[following]
                self.link[following] = parent if self.ends[parent] is not None else self.link[parent]

    def _states(self, tokens: Iterable[str]) -> Iterable[int]:
        node = 0
        for token in tokens:
            while node and token not in self.goto[node]:
                node = self.fail[node]
            node = self.goto[node].get(token, 0)
            yield node

    def found(self, tokens: Iterable[str]) -> set[int]:
        """Every pattern that occurs; each node's suffix chain is walked once."""
        seen: set[int] = set()
        hits: set[int] = set()
        for node in self._states(tokens):
            current: int | None = node
            while current is not None and current not in seen:
                seen.add(current)
                if self.ends[current] is not None:
                    hits.add(self.ends[current])
                current = self.link[current]
        return hits

    def occurs(self, tokens: Iterable[str]) -> bool:
        return any(self.ends[node] is not None or self.link[node] is not None for node in self._states(tokens))


def scan_free_text(documents: dict[str, dict[str, Any]], forbidden: Iterable[str], model_text: str) -> None:
    """Refuse a rationale or agent text that names a hidden population text (TS-R5, D10).

    Texts that are whole tokens of the model are exempt: the judge reads the
    model. Exact text only; a paraphrase or an encoding is not caught.
    """
    patterns = sorted({tokens for text in forbidden
                       for tokens in [tuple(_tokens(text.strip()))] if tokens})
    if not patterns:
        return
    exempt = _Matcher(patterns).found(_tokens(model_text))
    remaining = [pattern for number, pattern in enumerate(patterns) if number not in exempt]
    if not remaining:
        return
    matcher = _Matcher(remaining)
    for kind, document in documents.items():
        option = OPTIONS[kind]
        # The skill name is copied into the model's provenance (review F2).
        for field in ("agent", "skill"):
            if matcher.occurs(_tokens(document["judge"][field])):
                raise TypeJudgementError(f"{option}: judge.{field} names a population value")
        for index, entry in enumerate(document["verdicts"]):
            if matcher.occurs(_tokens(entry["rationale"])):
                raise TypeJudgementError(f"{option} verdict {index}: rationale names a population value")
