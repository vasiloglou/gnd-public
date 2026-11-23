"""Replay a bounded literature reading run with typed coverage and fidelity."""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Protocol

from gnd.artifacts import ArtifactError, canonical_json_bytes, read_regular_bounded, sha256_hex
from gnd.input_policy import MAX_BYTES as JSON_READ_LIMIT
from gnd.process import ProcessLimits

from .depth import FIXTURE as DEPTH_FIXTURE
from .depth import INPUT_LIMIT, PROCESS_LIMITS, ExampleError, _command, _decode, _read

FIXTURE = Path(__file__).parent / "reading_fixture"
STAGES = (
    "inventory", "broad-extraction", "selection", "targeted-extraction", "review", "recheck",
)
PURPOSES = (
    "Identify available source versions and sections",
    "Read opening material and retain unanswered questions",
    "Select available ranges for unresolved questions",
    "Recover targeted facts and identify earlier material to revisit",
    "Resolve source coverage and review reported assertions",
    "Check affected facts and measure held-back fidelity",
)
INPUTS = (
    "roster.json", "producer-pin.json", "reviews.json", "gold.json", "calibration.json",
    "calibration.txt", "conflict.json", "conflict.txt", "scope.json", "closure.json", "reading.orm.json",
)
EVIDENCE = (
    "coverage.json", "scope.json", "closure.json", "fidelity-high.json", "fidelity-low.json",
    "reported-conflict.population.json", "reported-conflict.source.txt", "broad.population.json",
    "targeted.population.json", "producer-output-table.json",
)
FILES = (*EVIDENCE, *(f"stage-{i}.json" for i in range(6)), *(f"payload-{i}.json" for i in range(6)))
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
SCENARIOS = ("full", "unavailable")
DEFAULT_BUDGET = 4096
MAX_BUDGET = 1 << 20
ROSTER_LIMIT = 128
CALIBRATION_FACTS = frozenset({"approximation", "alternative_integrator"})
COVERAGE_STATES = (
    "supported", "explicitly-denied", "inspected-not-found", "unavailable",
    "not-applicable", "omitted", "producer-refused", "empty-extraction",
)
SUBJECT = "alanine-in-vacuum"
LABEL = {"subject": SUBJECT, "label": "Alanine dipeptide observation"}

RUN_FORMAT = "literature-reading-run/1"
CALLER_RUN_FORMAT = "literature-reading-run/2"
PROFILE = "profile.json"
PROFILE_FORMAT = "literature-reading-profile/1"
PROFILE_KEYS = frozenset({
    "format", "model", "includes", "producer_label", "base_facts", "review", "calibration", "conflict", "absence",
})
MODEL_NAME = re.compile(r"[a-z][a-z0-9-]{0,63}\.orm\.json\Z")
PRODUCER_LABEL = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
MAX_MODEL_FILES = 17
JSON_DEPTH = 8
LIMIT_CEILINGS = {"roster": 4096, "max_budget": 1 << 26, "input_bytes": 8 << 20,
                  "response_bytes": 1 << 20, "route_seconds": 600,
                  "route_output_bytes": 16 << 20, "retained_bytes": JSON_READ_LIMIT}
RETAINED_FLOOR = 128 * 1024
ROW_OVERHEAD = 1024
CALLER_EXITS = (0, 1, 2, 4)
STEPS = ("review", "calibration", "conflict", "absence")


def _need(condition: bool, reason: str) -> None:
    if not condition:
        raise ExampleError(reason)


@dataclass(frozen=True)
class ReadingLimits:
    """The caps of a caller run; each default is today's constant or effective bound."""

    roster: int = ROSTER_LIMIT
    max_budget: int = MAX_BUDGET
    input_bytes: int = INPUT_LIMIT
    response_bytes: int = 128 * 1024
    route_seconds: int = 30
    route_output_bytes: int = 1 << 20
    retained_bytes: int | None = None


def _checked_limits(limits: object) -> ReadingLimits:
    _need(isinstance(limits, ReadingLimits), "invalid reading limits")
    for item in fields(ReadingLimits):
        value = getattr(limits, item.name)
        if item.name == "retained_bytes" and value is None:
            continue
        _need(type(value) is int and 1 <= value <= LIMIT_CEILINGS[item.name],
              f"invalid reading limit {item.name}")
    return limits


def _route_limits(limits: ReadingLimits) -> ProcessLimits:
    return ProcessLimits(
        timeout_seconds=limits.route_seconds, terminate_grace_seconds=1, stdin_limit_bytes=0,
        stdout_limit_bytes=limits.route_output_bytes, stderr_limit_bytes=INPUT_LIMIT,
        total_output_limit_bytes=limits.route_output_bytes,
    )


@dataclass(frozen=True)
class ProducerCall:
    """One section offered to a producer, with its bytes and the open questions on it."""

    stage: str
    section: str
    source: str
    source_version: str
    kind: str
    start: int
    end: int
    excerpt: bytes
    excerpt_sha256: str
    questions: tuple[dict, ...]


class Producer(Protocol):
    def produce(self, call: ProducerCall) -> dict: ...


@dataclass(frozen=True)
class ReviewCall:
    """One accepted response offered to a reviewer."""

    section: str
    excerpt: bytes
    excerpt_sha256: str
    facts: dict
    facts_sha256: str


class Reviewer(Protocol):
    def review(self, call: ReviewCall) -> dict: ...


@dataclass(frozen=True)
class Profile:
    """What a root binds the loop to: the packaged constants, or a caller's profile.json."""

    model: str
    includes: tuple[str, ...]
    producer_label: str
    base_facts: dict
    review: bool
    calibration: dict | None
    conflict: dict | None
    absence: bool
    exits: tuple[int, ...]
    caller: bool

    def steps(self) -> dict:
        return {name: "ran" if getattr(self, name) not in (False, None) else "skipped" for name in STEPS}


PACKAGED_PROFILE = Profile(
    model="reading.orm.json", includes=("vocabulary.orm.json",), producer_label="saved-public-fixture",
    base_facts={"subject_label": [LABEL]}, review=True,
    calibration={"section": "study-methods", "section_facts": ["approximation"],
                 "held_back_facts": ["alternative_integrator"], "renderer_label": "authored-public-fixture",
                 "case_names": ["run-methods", "held-back-predicate"]},
    conflict={"fact_type": "subject_label", "role": "label"}, absence=True, exits=(0,), caller=False,
)


def _plain(value: object, what: str) -> None:
    """Refuse anything that is not plain JSON, without recursion, before it is serialized."""
    stack = [(value, 0)]
    while stack:
        item, level = stack.pop()
        _need(level <= JSON_DEPTH, f"{what} nests too deeply")
        if isinstance(item, dict):
            for key, child in item.items():
                _need(type(key) is str, f"{what} has a non-string key")
                stack.append((child, level + 1))
        elif isinstance(item, list):
            stack.extend((child, level + 1) for child in item)
        elif type(item) is float:
            _need(math.isfinite(item), f"{what} has a non-finite number")
        else:
            _need(item is None or type(item) in (str, int, bool), f"{what} is not JSON")


def _canonical(value: object, what: str) -> bytes:
    """Serialize an untrusted value, refusing what canonical JSON cannot carry."""
    try:
        return canonical_json_bytes(value)
    except (ValueError, TypeError, RecursionError, UnicodeError) as error:
        raise ExampleError(f"{what} is not serializable JSON") from error


def _utf8(raw: bytes, what: str) -> None:
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ExampleError(f"{what} is not UTF-8 text") from error


SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SOURCE_KEYS = frozenset({"id", "version", "path", "sha256"})
SECTION_KEYS = frozenset({"id", "source", "kind", "selection", "keys", "span", "reason"})
QUESTION_KEYS = frozenset({"id", "section", "fact", "required", "superseded_by", "denial"})


def _fact_rows(value: object, what: str) -> dict:
    """The one row validator: fact-type names mapped to rows of role names and scalar values."""
    _need(isinstance(value, dict), f"invalid {what}")
    for name, rows in value.items():
        _need(isinstance(name, str) and isinstance(rows, list), f"invalid {what}")
        for row in rows:
            _need(isinstance(row, dict) and all(
                isinstance(role, str) and (type(item) in (str, int, bool)
                                           or type(item) is float and math.isfinite(item))
                for role, item in row.items()), f"invalid {what} row")
    return value


def _rows_by_id(rows: list, limit: int = ROSTER_LIMIT) -> dict:
    _need(isinstance(rows, list) and 0 < len(rows) <= limit, "invalid reading roster size")
    indexed = {}
    for row in rows:
        id_ = row.get("id") if isinstance(row, dict) else None
        _need(isinstance(id_, str) and IDENTIFIER.fullmatch(id_) is not None and id_ not in indexed,
              "invalid or duplicate reading roster ID")
        indexed[id_] = row
    return indexed


def _profile(raw: bytes, limits: ReadingLimits) -> Profile:
    value = _decode(raw, max_bytes=limits.input_bytes)
    _plain(value, "reading profile")
    _canonical(value, "reading profile")
    _need(set(value) == PROFILE_KEYS and value["format"] == PROFILE_FORMAT, "invalid reading profile keys")
    model, includes = value["model"], value["includes"]
    _need(isinstance(includes, list) and len(includes) < MAX_MODEL_FILES
          and all(isinstance(name, str) and MODEL_NAME.fullmatch(name) for name in (model, *includes))
          and len({model, *includes}) == len(includes) + 1, "invalid reading profile model files")
    label = value["producer_label"]
    _need(isinstance(label, str) and PRODUCER_LABEL.fullmatch(label) is not None, "invalid producer label")
    _fact_rows(value["base_facts"], "profile base facts")
    _need(type(value["review"]) is bool and type(value["absence"]) is bool, "invalid reading profile steps")
    calibration = value["calibration"]
    if calibration is not None:
        _need(isinstance(calibration, dict) and set(calibration) == {
            "section", "section_facts", "held_back_facts", "renderer_label", "case_names"}, "invalid calibration step")
        lists = calibration["section_facts"], calibration["held_back_facts"]
        cases = calibration["case_names"]
        _need(isinstance(calibration["section"], str)
              and all(isinstance(names, list) and names and all(isinstance(n, str) for n in names) for names in lists)
              and not set(lists[0]) & set(lists[1])
              and isinstance(calibration["renderer_label"], str)
              and PRODUCER_LABEL.fullmatch(calibration["renderer_label"]) is not None
              and isinstance(cases, list) and len(cases) == 2 and cases[0] != cases[1]
              and all(isinstance(n, str) and IDENTIFIER.fullmatch(n) for n in cases), "invalid calibration step")
    conflict = value["conflict"]
    _need(conflict is None or isinstance(conflict, dict) and set(conflict) == {"fact_type", "role"}
          and all(isinstance(conflict[key], str) for key in ("fact_type", "role")), "invalid conflict step")
    _need(not value["absence"] or calibration is not None, "the absence step needs calibration")
    return Profile(model=model, includes=tuple(includes), producer_label=label, base_facts=value["base_facts"],
                   review=value["review"], calibration=calibration, conflict=conflict, absence=value["absence"],
                   exits=CALLER_EXITS, caller=True)


def _has_profile(root: Path) -> bool:
    return os.path.lexists(root / PROFILE)


class ReadingInputs:
    """Read and validate the declared source, section and question inventories."""

    def __init__(self, root: Path, *, retained_responses: bytes | None = None,
                 vocabulary_fixture: Path = DEPTH_FIXTURE, limits: ReadingLimits | None = None,
                 live: bool = False, live_review: bool = False, unavailable: Iterable[str] = (),
                 retained_reviews: bytes | None = None) -> None:
        self.limits = limits if limits is not None else ReadingLimits()
        if _has_profile(root):
            self._caller(root, retained_responses, live, live_review, unavailable, retained_reviews)
        else:
            self._packaged(root, retained_responses, vocabulary_fixture)
        self.by_section = {}
        for name, question in self.questions.items():
            if question["superseded_by"] is None:
                self.by_section.setdefault(question["section"], []).append(
                    {"id": name, "fact": question["fact"], "denial": question["denial"]})
        self.input_pins = {name: sha256_hex(raw) for name, raw in self.raw.items()}

    def _packaged(self, root, retained_responses, vocabulary_fixture):
        self.profile = PACKAGED_PROFILE
        self.raw = {name: _read(root, name) for name in INPUTS}
        responses = _read(root, "responses.json") if retained_responses is None else retained_responses
        producer_pin = _decode(self.raw["producer-pin.json"])
        _need(producer_pin == {"sha256": sha256_hex(responses)}, "saved producer table differs from its pin")
        self.raw["responses.json"] = responses
        roster = _decode(self.raw["roster.json"])
        self.responses = _decode(self.raw["responses.json"])
        self.reviews = _decode(self.raw["reviews.json"])
        self._roster(roster, lambda path: _read(root, path), ROSTER_LIMIT)
        _need(set(self.responses) == self.response_sections, "saved response roster differs")
        self.raw["vocabulary.orm.json"] = _read(vocabulary_fixture, "vocabulary.orm.json")
        self._steps(PROCESS_LIMITS.stdout_limit_bytes)

    def _caller(self, root, retained_responses, live, live_review, unavailable, retained_reviews):
        cap = self.limits.input_bytes
        kept = self.limits.retained_bytes or LIMIT_CEILINGS["retained_bytes"]

        def read(name):
            return read_regular_bounded(root, name, max_bytes=cap)[0]

        self.raw = {PROFILE: read(PROFILE)}
        self.profile = profile = _profile(self.raw[PROFILE], self.limits)
        self.raw["roster.json"] = read("roster.json")
        roster = _decode(self.raw["roster.json"], max_bytes=cap)
        _canonical(roster, "reading roster")
        self._roster(roster, read, self.limits.roster)
        _need(all(isinstance(name, str) and name in self.sections for name in unavailable),
              "unknown unavailable section")
        for name in (profile.model, *profile.includes):
            self.raw[name] = read(name)
        needed = (("gold.json", "calibration.json", "calibration.txt") if profile.calibration else ()) + (
            ("conflict.json", "conflict.txt") if profile.conflict else ()) + (
            ("scope.json", "closure.json") if profile.absence else ())
        for name in needed:
            self.raw[name] = read(name)
        self._steps(cap)
        if profile.calibration is not None:
            section = self.sections.get(profile.calibration["section"])
            _need(section is not None and section["selection"] == "targeted", "invalid calibration section")
        if profile.absence:
            scope = _decode(self.raw["scope.json"], max_bytes=cap)
            _need(isinstance(scope.get("questions"), list) and scope["questions"]
                  and all(isinstance(q, str) and q in self.questions
                          and self.questions[q]["fact"] == scope.get("predicate") for q in scope["questions"]),
                  "invalid absence scope")
            self.predicate = scope["predicate"]
        self.responses = None
        if live and retained_responses is not None:
            self.responses = _decode(retained_responses, max_bytes=kept)
            _canonical(self.responses, "retained responses")
        if not live:
            responses = read("responses.json") if retained_responses is None else retained_responses
            self.raw["producer-pin.json"] = read("producer-pin.json")
            _need(_decode(self.raw["producer-pin.json"], max_bytes=cap) == {"sha256": sha256_hex(responses)},
                  "saved producer table differs from its pin")
            self.raw["responses.json"] = responses
            self.responses = _decode(responses, max_bytes=cap)
            _canonical(self.responses, "saved responses")
            _need(set(self.responses) == self.response_sections, "saved response roster differs")
        _need(profile.review or not live_review, "a reviewer needs the review step")
        self.reviews = None
        if profile.review and (not live_review or retained_reviews is not None):
            if live_review:
                self.reviews = _decode(retained_reviews, max_bytes=kept)
            else:
                self.raw["reviews.json"] = read("reviews.json")
                self.reviews = _decode(self.raw["reviews.json"], max_bytes=cap)
            _canonical(self.reviews, "saved reviews")
            for name, receipt in self.reviews.items():
                _need(name in self.response_sections and isinstance(receipt, dict)
                      and set(receipt) == {"basis", "decision", "excerpt_sha256", "facts_sha256"}
                      and all(isinstance(item, str) for item in receipt.values())
                      and len(canonical_json_bytes(receipt)) <= self.limits.response_bytes,
                      "invalid saved reviews")
                _need(receipt["decision"] == "supported" and bool(receipt["basis"])
                      and receipt["excerpt_sha256"] == sha256_hex(self.source_range(self.sections[name]))
                      and SHA256.fullmatch(receipt["facts_sha256"]) is not None,
                      "stale semantic reading review")

    def _roster(self, roster, read, limit):
        _need(roster.get("format") == "literature-reading-roster/1", "invalid reading roster format")
        self.sources = _rows_by_id(roster.get("sources"), limit)
        self.sections = _rows_by_id(roster.get("sections"), limit)
        self.questions = _rows_by_id(roster.get("questions"), limit)
        for rows, keys in ((self.sources, SOURCE_KEYS), (self.sections, SECTION_KEYS),
                           (self.questions, QUESTION_KEYS)):
            _need(all(keys <= set(row) for row in rows.values()), "incomplete reading roster row")
        self.documents = {}
        for name, source in self.sources.items():
            _need(source.get("path") == f"{name}.txt" and isinstance(source.get("version"), str),
                  "invalid reading source location")
            document = read(source["path"])
            _need(sha256_hex(document) == source.get("sha256"), "stale reading source")
            _utf8(document, "reading source")
            self.documents[name] = document
            self.raw[source["path"]] = document
        last_end: dict[str, int] = {}
        self.response_sections = set()
        for section in self.sections.values():
            source, span, selection = section.get("source"), section.get("span"), section.get("selection")
            _need(isinstance(source, str) and source in self.documents
                  and section.get("kind") in ("section", "equation", "table"),
                  "invalid source section")
            if span is None:
                _need(selection is None and section.get("reason") in ("unavailable", "not-applicable"),
                      "invalid unavailable section")
            else:
                _need(isinstance(span, list) and len(span) == 2 and all(type(x) is int for x in span)
                      and last_end.get(source, 0) <= span[0] < span[1] <= len(self.documents[source])
                      and selection in ("opening", "targeted"), "invalid reading span")
                _utf8(self.documents[source][span[0]:span[1]], "reading span")
                last_end[source] = span[1]
                self.response_sections.add(section["id"])
            keys = section.get("keys")
            _need(isinstance(keys, list) and all(isinstance(key, str) for key in keys),
                  "invalid section dependency keys")
        for question in self.questions.values():
            section = question.get("section")
            successor = question.get("superseded_by")
            _need(isinstance(section, str) and section in self.sections
                  and isinstance(question.get("fact"), str) and type(question.get("required")) is bool
                  and type(question.get("denial")) is bool,
                  "invalid question evidence selector")
            _need(successor is None or isinstance(successor, str) and successor in self.questions,
                  "unknown superseding question")
        settled = set()
        for question in self.questions:
            seen = set()
            successor = question
            while successor is not None and successor not in settled:
                _need(successor not in seen, "cyclic question supersession")
                seen.add(successor)
                successor = self.questions[successor]["superseded_by"]
            settled.update(seen)
        keys = roster.get("revisit_keys")
        _need(isinstance(keys, list) and all(isinstance(key, str) for key in keys), "invalid revisit keys")
        self.revisit_keys = set(keys)

    def _steps(self, cap):
        """Decode the files of the declared steps; one home for both kinds of root."""
        profile = self.profile
        self.gold = self.calibration = self.conflict_facts = None
        if profile.calibration is not None:
            gold = _fact_rows(_decode(self.raw["gold.json"], max_bytes=cap), "held-back gold")
            _canonical(gold, "held-back gold")
            wanted = {*profile.calibration["section_facts"], *profile.calibration["held_back_facts"]}
            _need(set(gold) == wanted, "invalid held-back gold roster")
            calibration = _decode(self.raw["calibration.json"], max_bytes=cap)
            _need(set(calibration) == {"high", "low"}, "invalid calibration candidates")
            for kind in ("high", "low"):
                _fact_rows(calibration[kind], "calibration candidate")
            _canonical(calibration, "calibration candidates")
            self.gold, self.calibration = gold, calibration
        if profile.conflict is not None:
            document = self.raw["conflict.txt"]
            conflict = _decode(self.raw["conflict.json"], max_bytes=cap)
            facts = _fact_rows(conflict.get("facts"), "reported conflict facts")
            _canonical(facts, "reported conflict facts")
            rows, role = facts.get(profile.conflict["fact_type"]), profile.conflict["role"]
            _need(conflict.get("document_sha256") == sha256_hex(document)
                  and isinstance(rows, list) and len(rows) == 2
                  and all(isinstance(row.get(role), str) and row[role].encode() in document for row in rows),
                  "stale reported conflict extraction")
            self.conflict_facts = facts

    def selection(self, kind: str) -> list[str]:
        return [name for name, section in self.sections.items() if section["selection"] == kind]

    def source_range(self, section: dict) -> bytes:
        first, last = section["span"]
        return self.documents[section["source"]][first:last]

    def pins(self) -> dict:
        return dict(self.input_pins)



class SavedProducer:
    """Local saved-response adapter with observed invocation counts."""

    def __init__(self, responses: dict) -> None:
        self.responses = responses
        self.calls = dict.fromkeys((STAGES[1], STAGES[3]), 0)

    def produce(self, call: ProducerCall) -> dict:
        self.calls[call.stage] += 1
        return self.responses[call.section]


def affected_sections(sections: dict, changed_keys: set[str]) -> list[str]:
    """Return available earlier section IDs sharing a changed dependency key."""
    return [name for name, row in sections.items()
            if row["span"] is not None and changed_keys.intersection(row["keys"])]


def _response(value, inputs, covers, limits):
    """Validate a producer's answer and return the parsed copy the loop retains."""
    _plain(value, "producer response")
    outcome = value.get("outcome") if isinstance(value, dict) else None
    facts = value.get("facts") if isinstance(value, dict) else None
    proposed = value.get("proposal_keys") if isinstance(value, dict) else None
    _need(isinstance(proposed, list) and all(isinstance(key, str) and key in inputs.revisit_keys for key in proposed),
          "invalid vocabulary proposal")
    _need(set(value) == {"outcome", "facts", "proposal_keys"} and outcome in ("accepted", "empty", "refused")
          and isinstance(facts, dict) and bool(facts) == (outcome == "accepted") and all(facts.values()),
          "invalid saved producer response")
    _fact_rows(facts, "producer facts")
    _need(covers is None or set(facts) <= covers, "producer fact type outside the model")
    raw = _canonical(value, "producer response")
    _need(len(raw) <= limits.response_bytes, "producer response exceeds its cap")
    return _decode(raw, max_bytes=limits.response_bytes)


def _inspect(inputs, stage, selected, remaining, producer, retained, *,
             documents=None, covers=None, counts=None):
    attempts, omitted = [], []
    for name in selected:
        row = inputs.sections[name]
        excerpt = inputs.source_range(row)
        left = documents.get(row["source"]) if documents is not None else None
        if len(excerpt) > remaining or left is not None and len(excerpt) > left:
            omitted.append(name)
            continue
        first, last = row["span"]
        if producer is not None:
            call = ProducerCall(
                stage=stage, section=name, source=row["source"],
                source_version=inputs.sources[row["source"]]["version"], kind=row["kind"], start=first, end=last,
                excerpt=excerpt, excerpt_sha256=sha256_hex(excerpt),
                questions=tuple(dict(question) for question in inputs.by_section.get(name, ())),
            )
            if counts is not None:
                counts[stage] += 1
            try:
                answer = producer.produce(call)
            except Exception as error:
                raise ExampleError(f"producer failed at {stage} {name}") from error
            response = _response(answer, inputs, covers, inputs.limits)
        else:
            response = retained.get(name)
            _need(response is not None and response == inputs.responses.get(name),
                  "retained producer response differs")
            response = _response(response, inputs, covers, inputs.limits)
        attempts.append({
            "section": name, "source": row["source"], "start": first, "end": last,
            "source_version": inputs.sources[row["source"]]["version"],
            "excerpt_sha256": sha256_hex(excerpt), "response_sha256": sha256_hex(canonical_json_bytes(response)),
            "outcome": response["outcome"], "response": response,
        })
        remaining -= len(excerpt)
        if left is not None:
            documents[row["source"]] = left - len(excerpt)
    return {"attempts": attempts, "omitted": omitted, "original_producer_calls": len(attempts)}, remaining


def _review_attempts(inputs, attempts, reviewer=None):
    verified, receipts = [], {}
    if not inputs.profile.review:
        return verified, receipts
    for row in attempts:
        if row["outcome"] != "accepted":
            continue
        name = row["section"]
        facts_sha256 = sha256_hex(canonical_json_bytes(row["response"]["facts"]))
        if reviewer is None:
            receipt = inputs.reviews.get(name)
            receipts[name] = receipt
        else:
            call = ReviewCall(section=name, excerpt=inputs.source_range(inputs.sections[name]),
                              excerpt_sha256=row["excerpt_sha256"],
                              facts=_decode(canonical_json_bytes(row["response"]["facts"])),
                              facts_sha256=facts_sha256)
            try:
                answer = reviewer.review(call)
            except Exception as error:
                raise ExampleError(f"reviewer failed at {name}") from error
            _plain(answer, "review receipt")
            _need(isinstance(answer, dict) and set(answer) == {"decision", "basis"}, "invalid review receipt")
            receipt = {**answer, "excerpt_sha256": row["excerpt_sha256"], "facts_sha256": facts_sha256}
            _need(len(_canonical(receipt, "review receipt")) <= inputs.limits.response_bytes,
                  "invalid review receipt")
            receipts[name] = receipt
        _need(isinstance(receipt, dict) and receipt.get("decision") == "supported"
              and receipt.get("excerpt_sha256") == row["excerpt_sha256"]
              and receipt.get("facts_sha256") == facts_sha256
              and isinstance(receipt.get("basis"), str) and bool(receipt["basis"]),
              "stale semantic reading review")
        verified.append({"section": name, **receipt})
    return verified, receipts


def _outcomes(inputs, attempted, unavailable):
    coverage, questions = [], []
    for name, question in inputs.questions.items():
        successor = question["superseded_by"]
        if successor is not None:
            questions.append({"id": name, "outcome": "superseded", "target": successor})
            continue
        section = question["section"]
        observation = attempted.get(section)
        facts = observation["response"]["facts"] if observation else {}
        if section in unavailable:
            state = "unavailable"
        elif inputs.sections[section]["span"] is None:
            state = inputs.sections[section]["reason"]
        elif observation is None:
            state = "omitted"
        elif observation["outcome"] == "refused":
            state = "producer-refused"
        elif observation["outcome"] == "empty":
            state = "empty-extraction"
        elif facts.get(question["fact"]):
            state = "explicitly-denied" if question["denial"] else "supported"
        else:
            state = "inspected-not-found"
        inspected = observation is not None
        coverage.append({"question": name, "source": inputs.sections[section]["source"],
                         "section": section, "state": state, "inspected": inspected})
        resolved = state in ("explicitly-denied", "supported")
        questions.append({"id": name, "outcome": "resolved" if resolved else "retained", "reason": state})
    return coverage, questions


def _combined(attempts, base=PACKAGED_PROFILE.base_facts):
    facts = {name: list(rows) for name, rows in base.items()}
    for row in attempts:
        for name, assertions in row["response"]["facts"].items():
            facts.setdefault(name, []).extend(assertions)
    return facts


def _population(header, facts):
    return canonical_json_bytes({"population": header, "facts": facts})


@dataclass(frozen=True)
class _Work:
    """The extracted model a run checks against, in its own temporary folder."""

    folder: Path
    index: dict
    stem: str
    route: ProcessLimits
    profile: Profile

    @property
    def header(self) -> dict:
        return self.index["header_template"]

    @property
    def covers(self) -> frozenset:
        return frozenset(self.header["covers"])


def _extract(inputs, folder):
    profile = inputs.profile
    route = _route_limits(inputs.limits) if profile.caller else PROCESS_LIMITS
    for name in (profile.model, *profile.includes):
        (folder / name).write_bytes(inputs.raw[name])
    _route(folder, "extract", profile.model, "--out", "bundle", limits=route)
    stem = profile.model.removesuffix(".json")
    if profile.caller:
        raw = read_regular_bounded(folder, f"bundle/{stem}.artifacts.json",
                                   max_bytes=inputs.limits.route_output_bytes)[0]
        index = _decode(raw, max_bytes=inputs.limits.route_output_bytes)
    else:
        index = _decode(_read(folder, f"bundle/{stem}.artifacts.json"))
    return _Work(folder=folder, index=index, stem=stem, route=route, profile=profile)


def _extraction_sidecar(work, document, raw, document_name, population_name):
    header, index = work.header, work.index
    return {
        "schema_version": 1, "model": header["model"], "model_sha256": index["model"]["sha256"],
        "population": population_name, "population_sha256": sha256_hex(raw),
        "document": document_name, "document_sha256": sha256_hex(document),
        "projection_sha256": index["artifacts"][f"{work.stem}.projection.schema.json"]["sha256"],
        "skill": "gnd-extract", "skill_version": "1", "executing_model": work.profile.producer_label,
    }


def _route(folder, *arguments, exits=(0,), limits=PROCESS_LIMITS):
    result = _command(folder, *arguments, limits=limits)
    _need(result.return_code in exits, f"{arguments[0]} exited {result.return_code}")
    return result


def _checked(work, stem, document, facts):
    folder, header = work.folder, work.header
    exits = CALLER_EXITS if work.profile.caller else (0, 1)
    raw = _population(header, facts)
    document_name = stem + ".txt"
    name = stem + ".population.json"
    (folder / name).write_bytes(raw)
    (folder / document_name).write_bytes(document)
    (folder / (stem + ".population.extraction.json")).write_bytes(canonical_json_bytes(
        _extraction_sidecar(work, document, raw, document_name, name)
    ))
    verify = _route(folder, "verify", header["model"], name, "--artifacts", "bundle",
                    "--format", "json", exits=exits, limits=work.route)
    check = _route(folder, "check", header["model"], name, "--format", "json", exits=exits, limits=work.route)
    return raw, {"verify": verify.return_code, "check": check.return_code}


def _write_fidelity_case(case_root, work, document, gold, facts):
    header, index = work.header, work.index
    case_root.mkdir(parents=True)
    source = _population({**header, "source": "fixture"}, gold)
    candidate = _population(header, facts)
    sidecar = _extraction_sidecar(work, document, candidate, "document.md", "extracted.population.json")
    document_manifest = {
        "schema_version": 1, "model": header["model"], "model_sha256": index["model"]["sha256"],
        "source_population": "source.population.json", "source_population_sha256": sha256_hex(source),
        "document": "document.md", "document_sha256": sha256_hex(document),
        "applicable_sha256": index["artifacts"][f"{work.stem}.applicable.json"]["sha256"],
        "renderer_skill": "gnd-render-doc", "renderer_skill_version": "1",
        "executing_model": work.profile.calibration["renderer_label"], "distractors": [],
    }
    for name, raw in (
        ("document.md", document), ("source.population.json", source),
        ("extracted.population.json", candidate),
        ("extracted.population.extraction.json", canonical_json_bytes(sidecar)),
        ("document.manifest.json", canonical_json_bytes(document_manifest)),
    ):
        (case_root / name).write_bytes(raw)


def _calibrate(work, inputs, targeted):
    step = work.profile.calibration
    gold, calibration = inputs.gold, inputs.calibration
    section_facts, held_back = step["section_facts"], step["held_back_facts"]
    methods = next((row for row in targeted if row["section"] == step["section"]), None)
    facts = methods["response"]["facts"] if methods is not None else {}
    observed = {name: facts[name] for name in section_facts if name in facts}
    measured = {}
    cap = inputs.limits.route_output_bytes if work.profile.caller else PROCESS_LIMITS.stdout_limit_bytes
    for kind in ("high", "low"):
        _write_fidelity_case(work.folder / kind / step["case_names"][0], work,
                             inputs.source_range(inputs.sections[step["section"]]),
                             {name: gold[name] for name in section_facts}, observed)
        _write_fidelity_case(work.folder / kind / step["case_names"][1], work,
                             inputs.raw["calibration.txt"], {name: gold[name] for name in held_back},
                             calibration[kind])
        report = _route(work.folder, "fidelity", work.header["model"], "--cases", kind,
                        "--artifacts", "bundle", "--format", "json", limits=work.route).stdout
        measured[kind] = report, _recall(report, frozenset(gold), max_bytes=cap)
    return measured


def _recall(raw, facts=CALIBRATION_FACTS, *, max_bytes=PROCESS_LIMITS.stdout_limit_bytes):
    value = _decode(raw, max_bytes=max_bytes)
    rows = [row for row in value["per_fact_type"] if row["id"] in facts]
    _need(value["cases"]["ran"] == 2 and value["cases"]["failed"] == value["cases"]["skipped"] == 0
          and len(rows) == len(facts) and {row["id"] for row in rows} == facts,
          "invalid fidelity census")
    counts = [sum(row["recall"][key] for row in rows) for key in ("numerator", "denominator")]
    _need(all(type(count) is int for count in counts) and 0 <= counts[0] <= counts[1],
          "invalid fidelity denominator")
    return counts


def read_coverage_rows(folder: Path, expected_sha256: str) -> list[dict]:
    """Read a run's optional coverage artifact using its external digest."""
    try:
        raw = _read(folder, "coverage.json")
    except (ArtifactError, OSError) as error:
        raise ExampleError("unreadable coverage evidence") from error
    _need(sha256_hex(raw) == expected_sha256, "stale coverage evidence")
    document = _decode(raw)
    _need(document.get("format") == "literature-reading-coverage/1"
          and isinstance(document.get("rows"), list), "invalid coverage evidence")
    return document["rows"]


def absence_status(artifacts, pins, *, facts=CALIBRATION_FACTS, predicate="alternative_integrator",
                   floor=(2, 2)):
    """Qualify the declared absence claim from four independently bound inputs."""
    names = ("scope.json", "closure.json", "coverage.json", "fidelity.json")
    if any(name not in artifacts or name not in pins or sha256_hex(artifacts[name]) != pins[name]
           for name in names):
        return "unavailable"
    try:
        scope, closure, coverage = (_decode(artifacts[name]) for name in names[:3])
        observed = {(row["question"], row["section"]) for row in coverage["rows"]
                    if row["state"] == "inspected-not-found" and row["inspected"] is True}
        scoped = set(zip(scope["questions"], scope["sections"], strict=True))
        ready = (
            scope["format"] == "literature-reading-scope/1"
            and closure["format"] == "literature-reading-closure/1"
            and coverage["format"] == "literature-reading-coverage/1"
            and bool(scoped) and scoped <= observed and _recall(artifacts["fidelity.json"], facts) == list(floor)
            and scope["predicate"] == predicate
            and closure["scope_sha256"] == pins["scope.json"] and closure["sections"] == scope["sections"]
        )
    except (ValueError, KeyError, TypeError):
        return "unavailable"
    return "qualified" if ready else "unavailable"


def _public_results(inputs, broad, targeted, work):
    profile = work.profile
    results, artifacts = {}, {}
    for name, attempts in (("broad", broad), ("targeted", targeted)):
        document = b"\n".join(inputs.source_range(inputs.sections[row["section"]]) for row in attempts)
        raw, results[name] = _checked(work, name, document, _combined(attempts, profile.base_facts))
        _need(profile.caller or results[name] == {"verify": 0, "check": 0}, f"{name} extraction is unverified")
        artifacts[name + ".population.json"] = raw
    if profile.conflict is None:
        results["reported-conflict"] = "skipped"
    else:
        document = inputs.raw["conflict.txt"]
        raw, results["reported-conflict"] = _checked(work, "reported-conflict", document, inputs.conflict_facts)
        _need(results["reported-conflict"] == {"verify": 1, "check": 1}, "the reported conflict was not preserved")
        artifacts["reported-conflict.population.json"] = raw
        artifacts["reported-conflict.source.txt"] = document
    fidelity = _calibrate(work, inputs, targeted) if profile.calibration is not None else {}
    return results, artifacts, fidelity


def _retained_files(read, roster, files, max_bytes):
    """Read a run's files: the stage chain first, then the rest, each against the manifest's digest."""
    artifacts = {}
    predecessor = None
    for index, stage in enumerate(STAGES):
        name = f"stage-{index}.json"
        raw = read(name)
        stage_record = _decode(raw, max_bytes=max_bytes)
        _need(sha256_hex(raw) == roster[name] and stage_record.get("stage") == stage
              and stage_record.get("predecessor_sha256") == predecessor
              and stage_record.get("payload_sha256") == roster[f"payload-{index}.json"],
              "stale retained reading stage")
        artifacts[name] = raw
        predecessor = sha256_hex(raw)
    for name in files:
        if name in artifacts:
            continue
        raw = read(name)
        _need(sha256_hex(raw) == roster[name], "stale retained reading output")
        artifacts[name] = raw
    retained = {}
    for stage_index in (1, 3):
        payload = _decode(artifacts[f"payload-{stage_index}.json"], max_bytes=max_bytes)
        rows = payload.get("attempts")
        _need(isinstance(rows, list) and all(isinstance(row, dict) and isinstance(row.get("section"), str)
                                             and "response" in row for row in rows), "invalid retained payload")
        retained.update({row["section"]: row["response"] for row in rows})
    return artifacts, retained


def _read_retained(run):
    raw_manifest = _read(run, "run.json")
    manifest = _decode(raw_manifest)
    _need(raw_manifest == canonical_json_bytes(manifest), "noncanonical reading manifest")
    _need(manifest.get("format") != CALLER_RUN_FORMAT, "a caller run replays against its own root")
    roster = manifest.get("artifacts")
    _need(manifest.get("format") == RUN_FORMAT
          and isinstance(roster, dict) and set(roster) == set(FILES), "incomplete stage roster")
    artifacts, retained = _retained_files(lambda name: _read(run, name), roster, FILES,
                                          PROCESS_LIMITS.stdout_limit_bytes)
    return manifest, artifacts, retained


def _read_run_file(folder: Path, name: str, max_bytes: int) -> bytes:
    """Read one file of a caller run under the retained-file cap the run recorded."""
    return read_regular_bounded(folder, name, max_bytes=max_bytes)[0]


def _caller_files(steps: dict) -> set:
    names = {"coverage.json", "broad.population.json", "targeted.population.json", "producer-output-table.json",
             *(f"stage-{i}.json" for i in range(6)), *(f"payload-{i}.json" for i in range(6))}
    for step, files in (("review", ("reviews.json",)), ("calibration", ("fidelity-high.json", "fidelity-low.json")),
                        ("conflict", ("reported-conflict.population.json", "reported-conflict.source.txt")),
                        ("absence", ("scope.json", "closure.json"))):
        if steps[step] == "ran":
            names.update(files)
    return names


def _caller_settings(manifest: dict) -> tuple[ReadingLimits, dict, dict]:
    """Check a caller run's recorded settings and steps before any of its files is read."""
    settings, steps = manifest.get("settings"), manifest.get("steps")
    _need(isinstance(settings, dict) and set(settings) == {
        "document_budget_bytes", "unavailable", "limits", "producer", "reviewer"}
          and isinstance(steps, dict) and set(steps) == set(STEPS)
          and all(value in ("ran", "skipped") for value in steps.values()), "invalid caller run settings")
    recorded = settings["limits"]
    _need(isinstance(recorded, dict) and set(recorded) == {item.name for item in fields(ReadingLimits)}
          and recorded["retained_bytes"] is not None, "invalid caller run settings")
    limits = _checked_limits(ReadingLimits(**recorded))
    budget, unavailable = settings["document_budget_bytes"], settings["unavailable"]
    _need((budget is None or type(budget) is int and 0 <= budget <= limits.max_budget)
          and isinstance(unavailable, list) and all(isinstance(name, str) for name in unavailable)
          and settings["producer"] in ("live", "saved") and settings["reviewer"] in ("live", "saved", "none")
          and type(manifest.get("budget_bytes")) is int and 0 <= manifest["budget_bytes"] <= limits.max_budget
          and manifest.get("scenario") == "full", "invalid caller run settings")
    return limits, settings, steps


def _read_caller_retained(run):
    ceiling = LIMIT_CEILINGS["retained_bytes"]
    raw_manifest = read_regular_bounded(run, "run.json", max_bytes=ceiling)[0]
    manifest = _decode(raw_manifest, max_bytes=ceiling)
    _need(raw_manifest == canonical_json_bytes(manifest), "noncanonical reading manifest")
    _need(manifest.get("format") != RUN_FORMAT, "a packaged run replays against the packaged root")
    _need(manifest.get("format") == CALLER_RUN_FORMAT, "incomplete stage roster")
    limits, settings, steps = _caller_settings(manifest)
    roster = manifest.get("artifacts")
    files = _caller_files(steps)
    _need(isinstance(roster, dict) and set(roster) == files, "incomplete stage roster")
    cap = limits.retained_bytes
    artifacts, retained = _retained_files(lambda name: _read_run_file(run, name, cap), roster,
                                          sorted(files), cap)
    return manifest, artifacts, retained, limits, settings


def _retained_cap(inputs, work, unavailable, live):
    """An upper bound on every file a caller run retains, from what is known before the first call.

    Roster strings, input pins and saved files are measured; each answer and receipt counts at the
    response cap; identifiers are at most 64 characters, so a coverage or question row fits in 512 bytes.
    """
    limits, profile = inputs.limits, inputs.profile
    response = limits.response_bytes
    eligible = [name for name in inputs.sections if name in inputs.response_sections]

    def attempt(name):
        section = inputs.sections[name]
        stub = {"section": name, "source": section["source"], "start": section["span"][0],
                "end": section["span"][1], "source_version": inputs.sources[section["source"]]["version"],
                "excerpt_sha256": "0" * 64, "response_sha256": "0" * 64, "outcome": "accepted", "response": None}
        return len(canonical_json_bytes(stub)) + response

    ids = (len(inputs.sections) + len(inputs.questions)) * (64 + 4) + ROW_OVERHEAD
    rows = len(inputs.questions) * 512
    receipts = len(eligible) * (response + 300)
    header = len(canonical_json_bytes(work.header))
    bounds = [
        sum(attempt(name) for name in eligible) + ids,
        len(inputs.raw["responses.json"]) if not live else receipts,
        header + len(canonical_json_bytes(profile.base_facts)) + len(eligible) * response + ROW_OVERHEAD,
        len(canonical_json_bytes({"sources": list(inputs.sources.values()),
                                  "sections": list(inputs.sections.values()), "unavailable": sorted(unavailable)})),
        rows + receipts + len(canonical_json_bytes(sorted(inputs.revisit_keys))) + ids,
        len(canonical_json_bytes(inputs.input_pins)) + ids + ROW_OVERHEAD,
    ]
    if profile.review:
        bounds.append(len(inputs.raw["reviews.json"]) if "reviews.json" in inputs.raw else receipts)
    if profile.conflict is not None:
        bounds += [len(inputs.raw["conflict.txt"]),
                   header + len(canonical_json_bytes(inputs.conflict_facts)) + ROW_OVERHEAD]
    if profile.absence:
        bounds += [len(inputs.raw["scope.json"]), len(inputs.raw["closure.json"])]
    if profile.calibration is not None:
        bounds.append(limits.route_output_bytes)
    bound = max(bounds)
    if limits.retained_bytes is not None:
        _need(bound <= limits.retained_bytes, "retained files would exceed the retained-file cap")
        return limits.retained_bytes
    cap = max(RETAINED_FLOOR, bound)
    _need(cap <= LIMIT_CEILINGS["retained_bytes"], "retained files would exceed the retained-file ceiling")
    return cap


def _stops(inputs, terminal, resolved, omitted):
    """The global stop rule, applied to each source's own required questions and sections.

    A required question belongs to the source of its own section; it is answered when its last
    successor is resolved, wherever that successor points.
    """
    open_sources = {inputs.sections[question["section"]]["source"] for key, question in inputs.questions.items()
                    if question["required"] and terminal[key] not in resolved}
    short_sources = {inputs.sections[name]["source"] for name in omitted}
    return {source: "required-coverage-completed" if source not in open_sources
            else "budget-exhausted" if source in short_sources else "available-evidence-exhausted"
            for source in inputs.sources}


def _terminal(questions):
    """Each question's last successor, resolving every supersession chain once."""
    terminal = {}
    for key in questions:
        path = []
        while key not in terminal and questions[key]["superseded_by"] is not None:
            path.append(key)
            key = questions[key]["superseded_by"]
        end = terminal.get(key, key)
        terminal.update(dict.fromkeys((*path, key), end))
    return terminal


def _evaluate(inputs, budget, scenario, *, producer=None, retained=None, retained_pins=None,
              reviewer=None, document_budget=None, unavailable=(), live=False, live_review=False):
    profile = inputs.profile
    _need(type(budget) is int and 0 <= budget <= inputs.limits.max_budget and scenario in SCENARIOS,
          "invalid reading settings")
    retained = retained or {}
    if profile.caller:
        _need(scenario == "full", "a caller run names its unavailable sections")
        unavailable = set(unavailable)
    else:
        unavailable = {"study-methods"} if scenario == "unavailable" else set()
    with tempfile.TemporaryDirectory(prefix="gnd-reading-") as temporary:
        work = _extract(inputs, Path(temporary).resolve())
        covers = work.covers if profile.caller else None
        cap = None
        if profile.caller:
            _need(set(profile.base_facts) <= work.covers, "profile base fact outside the model")
            cap = _retained_cap(inputs, work, unavailable, live)
        counts = dict.fromkeys((STAGES[1], STAGES[3]), 0)
        documents = dict.fromkeys(inputs.sources, document_budget) if document_budget is not None else None
        opening = [name for name in inputs.selection("opening") if name not in unavailable]
        broad, left = _inspect(inputs, STAGES[1], opening, budget, producer, retained,
                               documents=documents, covers=covers, counts=counts)
        opened = {row["section"]: row for row in broad["attempts"]}
        needed = {row["section"] for row in inputs.questions.values() if row["superseded_by"] is None
                  and row["fact"] not in opened.get(row["section"], {}).get("response", {}).get("facts", {})}
        planned_targeted = [name for name in inputs.selection("targeted") if name in needed]
        selected = [name for name in planned_targeted if name not in unavailable]
        targeted, left = _inspect(inputs, STAGES[3], selected, left, producer, retained,
                                  documents=documents, covers=covers, counts=counts)
        attempts = [*broad["attempts"], *targeted["attempts"]]
        attempted = {row["section"]: row for row in attempts}
        judgments, receipts = _review_attempts(inputs, attempts, reviewer)
        coverage, questions = _outcomes(inputs, attempted, unavailable)
        resolved = {row["id"] for row in questions if row["outcome"] == "resolved"}
        terminal = _terminal(inputs.questions)
        required = {terminal[key] for key, question in inputs.questions.items() if question["required"]}
        unavailable_reads = unavailable | {
            row["section"] for row in coverage if row["state"] == "unavailable"
        }
        if required <= resolved:
            stop = "required-coverage-completed"
        elif broad["omitted"] or targeted["omitted"]:
            stop = "budget-exhausted"
        else:
            stop = "available-evidence-exhausted"
        proposed_keys = {key for row in targeted["attempts"] for key in row["response"]["proposal_keys"]}
        earlier = {name: row for name, row in inputs.sections.items() if name in opened}
        revisit = affected_sections(earlier, proposed_keys)
        routes, artifacts, fidelity = _public_results(inputs, broad["attempts"], attempts, work)
    coverage_doc = {"format": "literature-reading-coverage/1", "rows": coverage}
    artifacts["coverage.json"] = canonical_json_bytes(coverage_doc)
    if profile.absence:
        artifacts.update({"scope.json": inputs.raw["scope.json"], "closure.json": inputs.raw["closure.json"]})
    if not profile.caller or not live:
        artifacts["producer-output-table.json"] = inputs.raw["responses.json"]
    else:
        artifacts["producer-output-table.json"] = canonical_json_bytes(
            {row["section"]: row["response"] for row in attempts})
    if profile.caller and profile.review:
        artifacts["reviews.json"] = canonical_json_bytes(receipts) if live_review else inputs.raw["reviews.json"]
    artifacts.update({f"fidelity-{name}.json": result[0] for name, result in fidelity.items()})
    absence = {}
    for kind, (raw, _counts) in fidelity.items():
        if not profile.absence:
            break
        scoped = {name: artifacts[name] for name in ("scope.json", "closure.json", "coverage.json")}
        scoped["fidelity.json"] = raw
        source_pins = inputs.pins()
        pins = {"scope.json": source_pins["scope.json"], "closure.json": source_pins["closure.json"]}
        if retained_pins is None:
            pins.update({"coverage.json": sha256_hex(artifacts["coverage.json"]), "fidelity.json": sha256_hex(raw)})
        else:
            pins.update({"coverage.json": retained_pins["coverage.json"],
                         "fidelity.json": retained_pins[f"fidelity-{kind}.json"]})
        if profile.caller:
            gold_rows = sum(len(rows) for rows in inputs.gold.values())
            absence[kind] = absence_status(scoped, pins, facts=frozenset(inputs.gold), predicate=inputs.predicate,
                                           floor=(gold_rows, gold_rows))
        else:
            absence[kind] = absence_status(scoped, pins)
    if not profile.absence:
        absence = {"high": "skipped", "low": "skipped"}
    measured = {name: val[1] for name, val in fidelity.items()} if profile.calibration is not None else None
    payloads = (
        {"sources": list(inputs.sources.values()), "sections": list(inputs.sections.values()), "unavailable": sorted(unavailable)},
        broad, {"selected": selected, "unresolved": sorted(needed)}, targeted,
        {"coverage": coverage, "questions": questions, "semantic_reviews": judgments,
         "vocabulary_proposals": sorted(proposed_keys), "revisit": revisit},
        {"public_routes": routes, "fidelity": measured, "absence": absence},
    )
    stages = []
    predecessor = None
    for i, (stage, purpose, payload) in enumerate(zip(STAGES, PURPOSES, payloads, strict=True)):
        payload_name = f"payload-{i}.json"
        artifacts[payload_name] = raw = canonical_json_bytes(payload)
        record = {
            "stage": stage, "purpose": purpose, "inputs": inputs.pins(),
            "predecessor_sha256": predecessor, "payload_sha256": sha256_hex(raw),
            "inspected": [row["section"] for row in payload.get("attempts", [])],
            "questions": list(inputs.questions),
        }
        stages.append(record)
        artifacts[f"stage-{i}.json"] = raw = canonical_json_bytes(record)
        predecessor = sha256_hex(raw)
    manifest = {"format": RUN_FORMAT, "scenario": scenario, "budget_bytes": budget,
                "inputs": inputs.pins(), "artifacts": {name: sha256_hex(raw) for name, raw in artifacts.items()}}
    settings = None
    if profile.caller:
        limits = {item.name: getattr(inputs.limits, item.name) for item in fields(ReadingLimits)}
        limits["retained_bytes"] = cap
        settings = {"document_budget_bytes": document_budget, "unavailable": sorted(unavailable),
                    "limits": limits, "producer": "live" if live else "saved",
                    "reviewer": "none" if not profile.review else "live" if live_review else "saved"}
        manifest.update({"format": CALLER_RUN_FORMAT, "settings": settings, "steps": profile.steps()})
    broad_facts = _combined(broad["attempts"], profile.base_facts)
    final_facts = _combined(attempts, profile.base_facts)
    report = {
        "format": "literature-reading-report/1", "stop": stop, "stages": stages,
        "producer_calls": counts,
        "coverage": coverage, "questions": questions, "revisit": revisit,
        "inspections": [{key: value for key, value in row.items() if key != "response"} for row in attempts],
        "reading_bytes": budget - left, "attempt_counts": {kind: sum(row["outcome"] == kind for row in attempts)
                                                            for kind in ("accepted", "empty", "refused")},
        "omitted": broad["omitted"] + targeted["omitted"],
        "read_denominator": {
            "scheduled": len(opening) + len(selected) + len(unavailable_reads),
            "attempted": len(attempts),
            "omitted": len(broad["omitted"]) + len(targeted["omitted"]),
            "unavailable": len(unavailable_reads),
        },
        "broad_fact_types": sorted(broad_facts),
        "targeted_fact_types": sorted(final_facts),
        "public_routes": routes, "fidelity": measured,
        "absence": {"status": absence["high"], "below_floor_status": absence["low"]},
        "evidence_sha256": sha256_hex(canonical_json_bytes(manifest)),
    }
    report["supported_fact_gain"] = sum(
        len({canonical_json_bytes(row) for row in rows}
            - {canonical_json_bytes(row) for row in broad_facts.get(fact, [])})
        for fact, rows in final_facts.items()
    )
    report["newly_answered"] = sum(
        row["outcome"] == "resolved" and inputs.questions[row["id"]]["section"] not in opened
        for row in questions
    )
    report["productivity"] = {
        "new_facts_per_byte": {"numerator": report["supported_fact_gain"], "denominator": budget - left},
        "new_answers_per_byte": {"numerator": report["newly_answered"], "denominator": budget - left},
    }
    if profile.caller:
        omitted = broad["omitted"] + targeted["omitted"]
        stops = _stops(inputs, terminal, resolved, omitted)
        tally = {source: {"source": source, "stop": stops[source], "reading_bytes": 0, "attempted": 0, "omitted": 0}
                 for source in inputs.sources}
        for row in attempts:
            tally[row["source"]]["reading_bytes"] += row["end"] - row["start"]
            tally[row["source"]]["attempted"] += 1
        for name in omitted:
            tally[inputs.sections[name]["source"]]["omitted"] += 1
        report.update({"settings": settings, "steps": profile.steps(), "documents": list(tally.values())})
    return manifest, artifacts, report


def run(out: Path, *, budget=DEFAULT_BUDGET, scenario="full", fixture: Path = FIXTURE,
        producer: Producer | None = None, reviewer: Reviewer | None = None,
        document_budget: int | None = None, unavailable: Iterable[str] | None = None,
        limits: ReadingLimits | None = None) -> dict:
    """Run the reading workflow over the packaged fixture or a caller's root, and retain its evidence."""
    checked = _checked_limits(limits if limits is not None else ReadingLimits())
    _need(type(budget) is int and 0 <= budget <= checked.max_budget, "invalid reading settings")
    _need(document_budget is None or type(document_budget) is int and 0 <= document_budget <= checked.max_budget,
          "invalid document budget")
    _need(not out.exists() and not out.is_symlink(), "reading output already exists")
    if not _has_profile(fixture):
        _need(all(value is None for value in (producer, reviewer, document_budget, unavailable, limits)),
              "caller arguments need profile.json")
        inputs = ReadingInputs(fixture)
        manifest, artifacts, report = _evaluate(inputs, budget, scenario, producer=SavedProducer(inputs.responses))
    else:
        _need(scenario == "full", "a caller run names its unavailable sections")
        names = list(unavailable) if unavailable is not None else []
        inputs = ReadingInputs(fixture, limits=checked, live=producer is not None,
                               live_review=reviewer is not None, unavailable=names)
        manifest, artifacts, report = _evaluate(
            inputs, budget, scenario, producer=producer if producer is not None else SavedProducer(inputs.responses),
            reviewer=reviewer, document_budget=document_budget, unavailable=names, live=producer is not None,
            live_review=reviewer is not None)
    out.mkdir()
    for name, raw in artifacts.items():
        (out / name).write_bytes(raw)
    (out / "run.json").write_bytes(canonical_json_bytes(manifest))
    return report


def replay(folder: Path, *, fixture: Path = FIXTURE, vocabulary_fixture: Path = DEPTH_FIXTURE,
           expected_evidence_sha256: str | None = None) -> dict:
    """Re-derive a reading result from retained evidence without invoking producers or reviewers.

    A root that holds profile.json replays a caller run (literature-reading-run/2) with the settings
    the run recorded; any other root replays a packaged run. Without ``expected_evidence_sha256`` a
    folder rewritten consistently from end to end replays; with it, only the run that returned it does.
    """
    if _has_profile(fixture):
        manifest, artifacts, retained, limits, settings = _read_caller_retained(folder)
        _expected(manifest, expected_evidence_sha256)
        live, live_review = settings["producer"] == "live", settings["reviewer"] == "live"
        inputs = ReadingInputs(
            fixture, retained_responses=artifacts["producer-output-table.json"], limits=limits, live=live,
            live_review=live_review, unavailable=settings["unavailable"],
            retained_reviews=artifacts.get("reviews.json") if live_review else None)
        _need(manifest["steps"] == inputs.profile.steps(), "reading steps differ from the profile")
        _need(manifest.get("inputs") == inputs.pins(), "stale reading input")
        observed, actual, report = _evaluate(
            inputs, manifest.get("budget_bytes"), manifest.get("scenario"), retained=retained,
            retained_pins=manifest["artifacts"], document_budget=settings["document_budget_bytes"],
            unavailable=settings["unavailable"], live=live, live_review=live_review)
    else:
        manifest, artifacts, retained = _read_retained(folder)
        _expected(manifest, expected_evidence_sha256)
        inputs = ReadingInputs(fixture, retained_responses=artifacts["producer-output-table.json"],
                               vocabulary_fixture=vocabulary_fixture)
        _need(manifest.get("inputs") == inputs.pins(), "stale reading input")
        observed, actual, report = _evaluate(inputs, manifest.get("budget_bytes"),
                                             manifest.get("scenario"), retained=retained,
                                             retained_pins=manifest["artifacts"])
    _need(manifest == observed and artifacts == actual, "re-derived reading evidence differs")
    return report


def _expected(manifest: dict, expected_sha256: str | None) -> None:
    _need(expected_sha256 is None or sha256_hex(canonical_json_bytes(manifest)) == expected_sha256,
          "reading evidence differs from the expected digest")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fresh = commands.add_parser("run")
    fresh.add_argument("--out", type=Path, required=True)
    fresh.add_argument("--budget-bytes", type=int, default=DEFAULT_BUDGET)
    fresh.add_argument("--scenario", choices=SCENARIOS, default="full")
    repeat = commands.add_parser("replay")
    repeat.add_argument("folder", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            result = run(args.out, budget=args.budget_bytes, scenario=args.scenario)
        else:
            result = replay(args.folder.resolve())
    except (ArtifactError, OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
        sys.stdout.buffer.write(canonical_json_bytes({"status": "incomplete", "reason": str(error)}))
        return 3
    sys.stdout.buffer.write(canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
