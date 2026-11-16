"""Replay a bounded literature reading run with typed coverage and fidelity."""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

from gnd.artifacts import ArtifactError, canonical_json_bytes, sha256_hex

from .depth import FIXTURE as DEPTH_FIXTURE
from .depth import ExampleError, _command, _decode, _read

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


def _need(condition: bool, reason: str) -> None:
    if not condition:
        raise ExampleError(reason)


def _rows_by_id(rows: list) -> dict:
    _need(isinstance(rows, list) and 0 < len(rows) <= ROSTER_LIMIT, "invalid reading roster size")
    indexed = {}
    for row in rows:
        id_ = row.get("id") if isinstance(row, dict) else None
        _need(isinstance(id_, str) and IDENTIFIER.fullmatch(id_) is not None and id_ not in indexed,
              "invalid or duplicate reading roster ID")
        indexed[id_] = row
    return indexed


class ReadingInputs:
    """Read and validate the declared source, section and question inventories."""

    def __init__(self, root: Path, *, retained_responses: bytes | None = None,
                 vocabulary_fixture: Path = DEPTH_FIXTURE) -> None:
        self.raw = {name: _read(root, name) for name in INPUTS}
        responses = _read(root, "responses.json") if retained_responses is None else retained_responses
        producer_pin = _decode(self.raw["producer-pin.json"])
        _need(producer_pin == {"sha256": sha256_hex(responses)}, "saved producer table differs from its pin")
        self.raw["responses.json"] = responses
        roster = _decode(self.raw["roster.json"])
        _need(roster.get("format") == "literature-reading-roster/1", "invalid reading roster format")
        self.sources = _rows_by_id(roster.get("sources"))
        self.sections = _rows_by_id(roster.get("sections"))
        self.questions = _rows_by_id(roster.get("questions"))
        self.responses = _decode(self.raw["responses.json"])
        self.reviews = _decode(self.raw["reviews.json"])
        self.documents = {}
        for name, source in self.sources.items():
            _need(source.get("path") == f"{name}.txt" and isinstance(source.get("version"), str),
                  "invalid reading source location")
            document = _read(root, source["path"])
            _need(sha256_hex(document) == source.get("sha256"), "stale reading source")
            document.decode("utf-8")
            self.documents[name] = document
            self.raw[source["path"]] = document
        last_end: dict[str, int] = {}
        response_sections = set()
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
                self.documents[source][span[0]:span[1]].decode("utf-8")
                last_end[source] = span[1]
                response_sections.add(section["id"])
            keys = section.get("keys")
            _need(isinstance(keys, list) and all(isinstance(key, str) for key in keys),
                  "invalid section dependency keys")
        _need(set(self.responses) == response_sections, "saved response roster differs")
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
        self.raw["vocabulary.orm.json"] = _read(vocabulary_fixture, "vocabulary.orm.json")
        self.input_pins = {name: sha256_hex(raw) for name, raw in self.raw.items()}

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

    def produce(self, stage: str, section: str) -> dict:
        self.calls[stage] += 1
        return self.responses[section]


def affected_sections(sections: dict, changed_keys: set[str]) -> list[str]:
    """Return available earlier section IDs sharing a changed dependency key."""
    return [name for name, row in sections.items()
            if row["span"] is not None and changed_keys.intersection(row["keys"])]


def _inspect(inputs, stage, selected, remaining, producer, retained):
    attempts, omitted = [], []
    for name in selected:
        row = inputs.sections[name]
        excerpt = inputs.source_range(row)
        if len(excerpt) > remaining:
            omitted.append(name)
            continue
        if producer is not None:
            response = producer.produce(stage, name)
        else:
            response = retained.get(name)
            _need(response == inputs.responses[name], "retained producer response differs")
        outcome = response.get("outcome") if isinstance(response, dict) else None
        facts = response.get("facts") if isinstance(response, dict) else None
        proposed = response.get("proposal_keys") if isinstance(response, dict) else None
        _need(isinstance(proposed, list) and all(isinstance(key, str) and key in inputs.revisit_keys for key in proposed),
              "invalid vocabulary proposal")
        _need(outcome in ("accepted", "empty", "refused") and isinstance(facts, dict)
              and bool(facts) == (outcome == "accepted"), "invalid saved producer response")
        first, last = row["span"]
        attempts.append({
            "section": name, "source": row["source"], "start": first, "end": last,
            "source_version": inputs.sources[row["source"]]["version"],
            "excerpt_sha256": sha256_hex(excerpt), "response_sha256": sha256_hex(canonical_json_bytes(response)),
            "outcome": outcome, "response": response,
        })
        remaining -= len(excerpt)
    return {"attempts": attempts, "omitted": omitted, "original_producer_calls": len(attempts)}, remaining


def _review_attempts(inputs, attempts):
    verified = []
    for row in attempts:
        if row["outcome"] != "accepted":
            continue
        name = row["section"]
        receipt = inputs.reviews.get(name)
        _need(isinstance(receipt, dict) and receipt.get("decision") == "supported"
              and receipt.get("excerpt_sha256") == row["excerpt_sha256"]
              and receipt.get("facts_sha256") == sha256_hex(canonical_json_bytes(row["response"]["facts"]))
              and isinstance(receipt.get("basis"), str) and bool(receipt["basis"]),
              "stale semantic reading review")
        verified.append({"section": name, **receipt})
    return verified


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
        elif question["fact"] in facts:
            state = "explicitly-denied" if question["denial"] else "supported"
        else:
            state = "inspected-not-found"
        inspected = observation is not None
        coverage.append({"question": name, "source": inputs.sections[section]["source"],
                         "section": section, "state": state, "inspected": inspected})
        resolved = state in ("explicitly-denied", "supported")
        questions.append({"id": name, "outcome": "resolved" if resolved else "retained", "reason": state})
    return coverage, questions


def _combined(attempts):
    facts = {"subject_label": [LABEL]}
    for row in attempts:
        for name, assertions in row["response"]["facts"].items():
            facts.setdefault(name, []).extend(assertions)
    return facts


def _population(header, facts):
    return canonical_json_bytes({"population": header, "facts": facts})


def _extraction_sidecar(header, index, document, raw, document_name, population_name):
    return {
        "schema_version": 1, "model": header["model"], "model_sha256": index["model"]["sha256"],
        "population": population_name, "population_sha256": sha256_hex(raw),
        "document": document_name, "document_sha256": sha256_hex(document),
        "projection_sha256": index["artifacts"]["reading.orm.projection.schema.json"]["sha256"],
        "skill": "gnd-extract", "skill_version": "1", "executing_model": "saved-public-fixture",
    }


def _route(folder, *arguments, exits=(0,)):
    result = _command(folder, *arguments)
    _need(result.return_code in exits, f"{arguments[0]} exited {result.return_code}")
    return result


def _checked(folder, stem, header, index, document, facts):
    raw = _population(header, facts)
    document_name = stem + ".txt"
    name = stem + ".population.json"
    (folder / name).write_bytes(raw)
    (folder / document_name).write_bytes(document)
    (folder / (stem + ".population.extraction.json")).write_bytes(canonical_json_bytes(
        _extraction_sidecar(header, index, document, raw, document_name, name)
    ))
    verify = _route(folder, "verify", header["model"], name, "--artifacts", "bundle",
                    "--format", "json", exits=(0, 1))
    check = _route(folder, "check", header["model"], name, "--format", "json", exits=(0, 1))
    return raw, {"verify": verify.return_code, "check": check.return_code}


def _write_fidelity_case(case_root, header, index, document, gold, facts):
    case_root.mkdir(parents=True)
    source = _population({**header, "source": "fixture"}, gold)
    candidate = _population(header, facts)
    sidecar = _extraction_sidecar(header, index, document, candidate, "document.md", "extracted.population.json")
    document_manifest = {
        "schema_version": 1, "model": header["model"], "model_sha256": index["model"]["sha256"],
        "source_population": "source.population.json", "source_population_sha256": sha256_hex(source),
        "document": "document.md", "document_sha256": sha256_hex(document),
        "applicable_sha256": index["artifacts"]["reading.orm.applicable.json"]["sha256"],
        "renderer_skill": "gnd-render-doc", "renderer_skill_version": "1",
        "executing_model": "authored-public-fixture", "distractors": [],
    }
    for name, raw in (
        ("document.md", document), ("source.population.json", source),
        ("extracted.population.json", candidate),
        ("extracted.population.extraction.json", canonical_json_bytes(sidecar)),
        ("document.manifest.json", canonical_json_bytes(document_manifest)),
    ):
        (case_root / name).write_bytes(raw)


def _calibrate(folder, inputs, header, index, targeted):
    calibration = _decode(inputs.raw["calibration.json"])
    gold = _decode(inputs.raw["gold.json"])
    _need(set(gold) == CALIBRATION_FACTS, "invalid held-back gold roster")
    methods = next((row for row in targeted if row["section"] == "study-methods"), None)
    facts = methods["response"]["facts"] if methods is not None else {}
    observed = {name: facts[name] for name in ("approximation",) if name in facts}
    measured = {}
    for kind in ("high", "low"):
        _write_fidelity_case(folder / kind / "run-methods", header, index,
                             inputs.source_range(inputs.sections["study-methods"]),
                             {"approximation": gold["approximation"]}, observed)
        _write_fidelity_case(folder / kind / "held-back-predicate", header, index,
                             inputs.raw["calibration.txt"], {"alternative_integrator": gold["alternative_integrator"]},
                             calibration[kind])
        report = _route(folder, "fidelity", header["model"], "--cases", kind,
                        "--artifacts", "bundle", "--format", "json").stdout
        measured[kind] = report, _recall(report)
    return measured


def _recall(raw):
    value = _decode(raw)
    rows = [row for row in value["per_fact_type"] if row["id"] in CALIBRATION_FACTS]
    _need(value["cases"]["ran"] == 2 and value["cases"]["failed"] == value["cases"]["skipped"] == 0
          and len(rows) == len(CALIBRATION_FACTS) and {row["id"] for row in rows} == CALIBRATION_FACTS,
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


def absence_status(artifacts, pins):
    """Qualify the declared fixture claim from four independently bound inputs."""
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
            and bool(scoped) and scoped <= observed and _recall(artifacts["fidelity.json"]) == [2, 2]
            and scope["predicate"] == "alternative_integrator"
            and closure["scope_sha256"] == pins["scope.json"] and closure["sections"] == scope["sections"]
        )
    except (ValueError, KeyError, TypeError):
        return "unavailable"
    return "qualified" if ready else "unavailable"


def _public_results(inputs, broad, targeted):
    with tempfile.TemporaryDirectory(prefix="gnd-reading-") as temporary:
        folder = Path(temporary).resolve()
        for name in ("reading.orm.json", "vocabulary.orm.json"):
            (folder / name).write_bytes(inputs.raw[name])
        _route(folder, "extract", "reading.orm.json", "--out", "bundle")
        index = _decode(_read(folder, "bundle/reading.orm.artifacts.json"))
        header = index["header_template"]
        results, artifacts = {}, {}
        for name, attempts in (("broad", broad), ("targeted", targeted)):
            document = b"\n".join(inputs.source_range(inputs.sections[row["section"]]) for row in attempts)
            raw, results[name] = _checked(folder, name, header, index, document, _combined(attempts))
            _need(results[name] == {"verify": 0, "check": 0}, f"{name} extraction is unverified")
            artifacts[name + ".population.json"] = raw
        document = inputs.raw["conflict.txt"]
        conflict = _decode(inputs.raw["conflict.json"])
        facts = conflict["facts"]
        labels = facts.get("subject_label")
        _need(conflict.get("document_sha256") == sha256_hex(document)
              and isinstance(labels, list) and len(labels) == 2
              and all(isinstance(row, dict) and isinstance(row.get("label"), str)
                      and row["label"].encode() in document for row in labels),
              "stale reported conflict extraction")
        raw, results["reported-conflict"] = _checked(folder, "reported-conflict", header, index, document, facts)
        _need(results["reported-conflict"] == {"verify": 1, "check": 1},
              "the reported conflict was not preserved")
        artifacts["reported-conflict.population.json"] = raw
        artifacts["reported-conflict.source.txt"] = document
        fidelity = _calibrate(folder, inputs, header, index, targeted)
        return results, artifacts, fidelity


def _read_retained(run):
    raw_manifest = _read(run, "run.json")
    manifest = _decode(raw_manifest)
    _need(raw_manifest == canonical_json_bytes(manifest), "noncanonical reading manifest")
    roster = manifest.get("artifacts")
    _need(manifest.get("format") == "literature-reading-run/1"
          and isinstance(roster, dict) and set(roster) == set(FILES), "incomplete stage roster")
    artifacts = {}
    predecessor = None
    for index, stage in enumerate(STAGES):
        name = f"stage-{index}.json"
        raw = _read(run, name)
        stage_record = _decode(raw)
        _need(sha256_hex(raw) == roster[name] and stage_record.get("stage") == stage
              and stage_record.get("predecessor_sha256") == predecessor
              and stage_record.get("payload_sha256") == roster[f"payload-{index}.json"],
              "stale retained reading stage")
        artifacts[name] = raw
        predecessor = sha256_hex(raw)
    for name in FILES:
        if name in artifacts:
            continue
        raw = _read(run, name)
        _need(sha256_hex(raw) == roster[name], "stale retained reading output")
        artifacts[name] = raw
    retained = {}
    for stage_index in (1, 3):
        payload = _decode(artifacts[f"payload-{stage_index}.json"])
        retained.update({row["section"]: row["response"] for row in payload["attempts"]})
    return manifest, artifacts, retained


def _evaluate(inputs, budget, scenario, *, producer=None, retained=None, retained_pins=None):
    _need(type(budget) is int and 0 <= budget <= MAX_BUDGET and scenario in SCENARIOS, "invalid reading settings")
    retained = retained or {}
    unavailable = {"study-methods"} if scenario == "unavailable" else set()
    broad, left = _inspect(inputs, STAGES[1], inputs.selection("opening"), budget, producer, retained)
    opened = {row["section"]: row for row in broad["attempts"]}
    needed = {row["section"] for row in inputs.questions.values() if row["superseded_by"] is None
              and row["fact"] not in opened.get(row["section"], {}).get("response", {}).get("facts", {})}
    planned_targeted = [name for name in inputs.selection("targeted") if name in needed]
    selected = [name for name in planned_targeted if name not in unavailable]
    targeted, left = _inspect(inputs, STAGES[3], selected, left, producer, retained)
    recorded_calls = {STAGES[1]: broad["original_producer_calls"], STAGES[3]: targeted["original_producer_calls"]}
    _need(producer is None or producer.calls == recorded_calls, "producer call counts disagree with captured attempts")
    attempts = [*broad["attempts"], *targeted["attempts"]]
    attempted = {row["section"]: row for row in attempts}
    judgments = _review_attempts(inputs, attempts)
    coverage, questions = _outcomes(inputs, attempted, unavailable)
    resolved = {row["id"] for row in questions if row["outcome"] == "resolved"}
    required = set()
    for key, question in inputs.questions.items():
        if not question["required"]:
            continue
        while inputs.questions[key]["superseded_by"] is not None:
            key = inputs.questions[key]["superseded_by"]
        required.add(key)
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
    routes, artifacts, fidelity = _public_results(inputs, broad["attempts"], attempts)
    coverage_doc = {"format": "literature-reading-coverage/1", "rows": coverage}
    artifacts.update({
        "coverage.json": canonical_json_bytes(coverage_doc),
        "scope.json": inputs.raw["scope.json"], "closure.json": inputs.raw["closure.json"],
        "producer-output-table.json": inputs.raw["responses.json"],
        **{f"fidelity-{name}.json": result[0] for name, result in fidelity.items()},
    })
    absence = {}
    for kind, (raw, _counts) in fidelity.items():
        scoped = {name: artifacts[name] for name in ("scope.json", "closure.json", "coverage.json")}
        scoped["fidelity.json"] = raw
        source_pins = inputs.pins()
        pins = {"scope.json": source_pins["scope.json"], "closure.json": source_pins["closure.json"]}
        if retained_pins is None:
            pins.update({"coverage.json": sha256_hex(artifacts["coverage.json"]), "fidelity.json": sha256_hex(raw)})
        else:
            pins.update({"coverage.json": retained_pins["coverage.json"],
                         "fidelity.json": retained_pins[f"fidelity-{kind}.json"]})
        absence[kind] = absence_status(scoped, pins)
    payloads = (
        {"sources": list(inputs.sources.values()), "sections": list(inputs.sections.values()), "unavailable": sorted(unavailable)},
        broad, {"selected": selected, "unresolved": sorted(needed)}, targeted,
        {"coverage": coverage, "questions": questions, "semantic_reviews": judgments,
         "vocabulary_proposals": sorted(proposed_keys), "revisit": revisit},
        {"public_routes": routes, "fidelity": {name: val[1] for name, val in fidelity.items()}, "absence": absence},
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
    manifest = {"format": "literature-reading-run/1", "scenario": scenario, "budget_bytes": budget,
                "inputs": inputs.pins(), "artifacts": {name: sha256_hex(raw) for name, raw in artifacts.items()}}
    broad_facts, final_facts = _combined(broad["attempts"]), _combined(attempts)
    report = {
        "format": "literature-reading-report/1", "stop": stop, "stages": stages,
        "producer_calls": producer.calls if producer is not None else dict.fromkeys((STAGES[1], STAGES[3]), 0),
        "coverage": coverage, "questions": questions, "revisit": revisit,
        "inspections": [{key: value for key, value in row.items() if key != "response"} for row in attempts],
        "reading_bytes": budget - left, "attempt_counts": {kind: sum(row["outcome"] == kind for row in attempts)
                                                            for kind in ("accepted", "empty", "refused")},
        "omitted": broad["omitted"] + targeted["omitted"],
        "read_denominator": {
            "scheduled": len(inputs.selection("opening")) + len(selected) + len(unavailable_reads),
            "attempted": len(attempts),
            "omitted": len(broad["omitted"]) + len(targeted["omitted"]),
            "unavailable": len(unavailable_reads),
        },
        "broad_fact_types": sorted(broad_facts),
        "targeted_fact_types": sorted(final_facts),
        "public_routes": routes, "fidelity": payloads[-1]["fidelity"],
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
    return manifest, artifacts, report


def run(out: Path, *, budget=DEFAULT_BUDGET, scenario="full", fixture: Path = FIXTURE) -> dict:
    """Run the saved-response workflow and retain its complete evidence."""
    _need(not out.exists() and not out.is_symlink(), "reading output already exists")
    inputs = ReadingInputs(fixture)
    manifest, artifacts, report = _evaluate(inputs, budget, scenario, producer=SavedProducer(inputs.responses))
    out.mkdir()
    for name, raw in artifacts.items():
        (out / name).write_bytes(raw)
    (out / "run.json").write_bytes(canonical_json_bytes(manifest))
    return report


def replay(folder: Path, *, fixture: Path = FIXTURE, vocabulary_fixture: Path = DEPTH_FIXTURE) -> dict:
    """Re-derive the reading result from retained evidence without invoking producers."""
    manifest, artifacts, retained = _read_retained(folder)
    inputs = ReadingInputs(fixture, retained_responses=artifacts["producer-output-table.json"],
                           vocabulary_fixture=vocabulary_fixture)
    _need(manifest.get("inputs") == inputs.pins(), "stale reading input")
    observed, actual, report = _evaluate(inputs, manifest.get("budget_bytes"),
                                         manifest.get("scenario"), retained=retained,
                                         retained_pins=manifest["artifacts"])
    _need(manifest == observed and artifacts == actual, "re-derived reading evidence differs")
    return report


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
