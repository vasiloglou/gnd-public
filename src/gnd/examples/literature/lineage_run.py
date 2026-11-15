"""Assemble admitted contextual sources and score named lineage paths."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from itertools import pairwise
from pathlib import Path
from typing import Any

from gnd import api
from gnd.anchors import read_regular_path, strict_json, vocabulary_digest
from gnd.artifacts import (
    ArtifactError,
    canonical_json_bytes,
    publish_directory_once,
    read_regular_file_bytes,
    sha256_hex,
)
from gnd.composition import (
    MAX_RECORD_BYTES,
    CompositionError,
    compose,
    parse_record,
    verify_composition,
)
from gnd.judgments import JudgmentInputError, judgment_fact_digest, judgment_receipt_digest
from gnd.model import ModelLoadError, load_model_bytes

from .assertion_admission import ABSENT_CONDITIONS, PASSAGE, ROLES, STATEMENT, WORK, admit
from .assurance_report import Refusal

INPUT_SCHEMA = "literature-lineage-input/1"
SCORE_SCHEMA = "literature-lineage-score/1"
PARTICIPANT = "participant_name"
CAP = 4 << 20
MODEL_CAP = 10 << 20
DOCUMENT_CAP = 1 << 20
ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
DECISION_FIELDS = {"decision", "keys"}
SOURCE_FIELDS = {"id", "document", "sha256", "work", "statements"}
STATEMENT_FIELDS = ROLES - {"work"} | {"start", "end", "disposition"}


def _require(ok: bool, reason: str = "input:lineage-shape") -> None:
    if not ok:
        raise Refusal(reason)


def _shape(value: Any, fields: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == fields


def _text(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 1024 and bool(value.strip())


def _read(path: Path, cap: int = CAP) -> bytes:
    return read_regular_path(path, label="lineage input", max_bytes=cap)


def _decode(raw: bytes, cap: int = CAP) -> Any:
    return strict_json(raw, max_bytes=cap, too_large="input:lineage-cap")


def _inputs(raw: bytes, example: Path, rubric: dict) -> tuple[list[tuple[dict, bytes]], list[dict]]:
    data = _decode(raw)
    _require(_shape(data, {"schema", "sources", "decisions"}) and data["schema"] == INPUT_SCHEMA)
    sources, decisions = data["sources"], data["decisions"]
    _require(isinstance(sources, list) and 1 <= len(sources) <= 32)
    _require(isinstance(decisions, list) and len(decisions) <= 128)
    loaded, ids, passages = [], set(), set()
    for source in sources:
        _require(_shape(source, SOURCE_FIELDS))
        identifier = source["id"]
        _require(isinstance(identifier, str) and ID.fullmatch(identifier) is not None and identifier not in ids)
        ids.add(identifier)
        _require(_text(source["work"]) and _text(source["document"]))
        doc = read_regular_file_bytes(example, source["document"], label="lineage document", max_bytes=DOCUMENT_CAP)
        _require(sha256_hex(doc) == source["sha256"], "input:document-digest")
        doc.decode("utf-8")
        rows = source["statements"]
        _require(isinstance(rows, list) and 1 <= len(rows) <= 32)
        for row in rows:
            _require(_shape(row, STATEMENT_FIELDS) and all(_text(row[key]) for key in STATEMENT_FIELDS - {"start", "end"}))
            left, right = row["start"], row["end"]
            _require(type(left) is int and type(right) is int and 0 <= left < right <= len(doc))
            doc[left:right].decode("utf-8")
            _require(row["passage"] not in passages and row["disposition"] in {*rubric, "missing"})
            passages.add(row["passage"])
        loaded.append((source, doc))
    for item in decisions:
        _require(_shape(item, DECISION_FIELDS) and item["decision"] in ("same", "different"))
        keys = item["keys"]
        _require(isinstance(keys, list) and len(keys) == 2)
        for key in keys:
            _require(_shape(key, {"source", "value"}) and _text(key["source"]) and _text(key["value"])
                     and key["source"] in ids)
        _require(keys[0]["source"] != keys[1]["source"])
    return loaded, decisions


def _authority(source: dict, document: bytes, model_id: str, model_raw: bytes, rubric: dict, folder: Path) -> Path:
    folder.mkdir()
    evidence = folder / "evidence"
    evidence.mkdir()
    (evidence / "document.txt").write_bytes(document)
    statements, places, works = [], [], []
    for original in source["statements"]:
        work, passage = source["work"], original["passage"]
        identifier = source["id"] + "#" + passage
        row = {key: original[key] for key in ROLES - {"work"}} | {"work": work}
        for arm in ("condition", "regime"):
            if row[arm].strip().casefold() in ABSENT_CONDITIONS:
                row[arm] = "unspecified"
        statements.append(row)
        places.append({"assertion": identifier, "passage": passage})
        works.append({"assertion": identifier, "work": work})
    subject = canonical_json_bytes({
        "population": {"model": "model.orm.yaml", "model_id": model_id, "source": "fixture",
                       "covers": [STATEMENT, PASSAGE, WORK]},
        "instances": {}, "facts": {STATEMENT: statements, PASSAGE: places, WORK: works},
    })
    (folder / "raw.population.json").write_bytes(subject)
    judge = "corpus-author"
    model_hash, pop_hash, doc_hash = map(sha256_hex, (model_raw, subject, document))
    receipts = []
    for index, row in enumerate(source["statements"]):
        if row["disposition"] == "missing":
            continue
        start, end = row["start"], row["end"]
        receipts.append({
            "receipt_id": f"{source['id']}-{index}", "judge_id": judge,
            "verdict": rubric[row["disposition"]], "trust": "consumer-pinned",
            "subject": {"model_sha256": model_hash, "population_sha256": pop_hash, "reference_identity": None,
                        "fact_type": STATEMENT, "index": index,
                        "fact_sha256": judgment_fact_digest(STATEMENT, index, statements[index])},
            "sources": [{"path": "document.txt", "sha256": doc_hash,
                         "quote": {"start": start, "end": end, "sha256": sha256_hex(document[start:end])}}],
            "external_evidence": None,
        })
    (folder / "receipts.json").write_bytes(canonical_json_bytes({"schema_version": 1, "receipts": receipts}))
    (folder / "policy.json").write_bytes(canonical_json_bytes({
        "schema_version": 1, "policy_id": source["id"], "trust_mode": "consumer-pinned",
        "judges": [judge], "targets": [{"fact_type": STATEMENT, "index": i} for i in range(len(statements))],
        "admission": {"minimum_approvals": 1, "evidence_floor": None},
        "repair": {"minimum_rejections": 1, "evidence_floor": None},
        "trusted_receipts": [{"judge_id": judge, "receipt_sha256": judgment_receipt_digest(item)}
                             for item in receipts],
    }))
    return evidence


def _resolution(decisions: list[dict], admitted: dict[str, bytes]) -> bytes:
    coordinates = {}
    input_hashes = {source: sha256_hex(raw) for source, raw in admitted.items()}
    for source, raw in admitted.items():
        for row_index, row in enumerate(_decode(raw, MODEL_CAP)["facts"][STATEMENT]):
            for role in ("actor", "object"):
                coordinates.setdefault((source, row[role]), (row_index, role))
    result = []
    for decision in decisions:
        evidence, keys, digests = [], [], {}
        for position, key in enumerate(decision["keys"]):
            source, value = key["source"], key["value"]
            coordinate = coordinates.get((source, value))
            _require(coordinate is not None, "input:unadmitted-resolution-key")
            row, role = coordinate
            evidence.append({"key": position, "source": source, "fact_type": STATEMENT, "fact_index": row, "role": role})
            keys.append({**key, "object_type": PARTICIPANT})
            digests[source] = input_hashes[source]
        result.append({"decision": decision["decision"], "keys": keys, "evidence": evidence, "input_sha256": digests,
                       "producer": {"kind": "reviewer", "id": "corpus-author"}, "placeholders": None})
    return canonical_json_bytes({"schema": "gnd-resolution/1", "object_types": [PARTICIPANT], "decisions": result})


def assemble(example: Path, model: Path, annotations: Path, out: Path) -> None:
    """Build a no-replace run from accepted contextual statements and verified identities."""
    model_raw = _read(model, MODEL_CAP)
    model_doc = load_model_bytes(model_raw, source=model)
    rubric = _decode(_read(example / "assertions/rubric.json"))["mapping"]
    sources, decisions = _inputs(_read(annotations), example, rubric)
    out = out.absolute()
    _require(not (out.exists() or out.is_symlink()), "output:exists")
    with tempfile.TemporaryDirectory(prefix="gnd-lineage-") as scratch:
        root = Path(scratch).resolve()
        snapshot = root / "model.orm.yaml"
        snapshot.write_bytes(model_raw)
        composed_root = root / "sources"
        composed_root.mkdir()
        (root / "opinions").mkdir()
        (root / "admissions").mkdir()
        admitted = {}
        vocabulary = vocabulary_digest(model_doc)
        for source, document in sources:
            identifier = source["id"]
            folder = root / "opinions" / identifier
            evidence = _authority(source, document, model_doc.model_id, model_raw, rubric, folder)
            destination = root / "admissions" / identifier
            admit(snapshot, folder/"raw.population.json", folder/"policy.json", folder/"receipts.json",
                  evidence, destination)
            population = _read(destination/"admitted.population.json", MODEL_CAP)
            admitted[identifier] = population
            member = composed_root / identifier
            member.mkdir()
            (member/"document.txt").write_bytes(document)
            (member/"population.json").write_bytes(population)
            (member/"population.json.anchors.json").write_bytes(canonical_json_bytes({
                "schema_version": 2, "population_sha256": sha256_hex(population), "vocabulary_digest": vocabulary,
                "document_sha256": sha256_hex(document), "anchors": [],
            }))
        resolution = _resolution(decisions, admitted)
        (composed_root/"resolution.json").write_bytes(resolution)
        (composed_root/"manifest.json").write_bytes(canonical_json_bytes({
            "schema": "gnd-composition-manifest/1", "sources": list(admitted), "renamings": [], "scope_tags": [],
            "deduplications": "identical-rows", "resolution": {"path": "resolution.json", "sha256": sha256_hex(resolution)},
        }))
        result = compose(model_doc, model_raw, composed_root)
        files = {path.relative_to(root).as_posix(): path.read_bytes()
                 for path in root.rglob("*") if path.is_file()}
        files["composed.population.json"] = result.population_bytes
        files["composition.json"] = result.record_bytes
        publish_directory_once(out.parent, out.name, files, manifest_name="composition.json",
                               max_file_bytes=MAX_RECORD_BYTES, max_total_bytes=64 << 20)


def _claim(relation: str, descendant: str, ancestor: str) -> dict:
    return {"fact_type": relation, "tuple": [{"primitive": "String", "value": v} for v in (descendant, ancestor)]}


def _chains(data: Any) -> list[dict]:
    _require(isinstance(data, dict) and data.get("schema") == "literature-answer-key/1")
    rows = data.get("chains")
    _require(isinstance(rows, list) and 0 < len(rows) <= 64)
    seen = set()
    for row in rows:
        _require(isinstance(row, dict) and _text(row.get("id")) and row["id"] not in seen
                 and row.get("label") in ("supported", "false"))
        path = row.get("path")
        _require(isinstance(path, list) and 2 <= len(path) <= 16 and all(map(_text, path)))
        seen.add(row["id"])
    return rows


def score(model: Path, run: Path, answer_key: Path) -> dict:
    """Grade exact directed paths through the public witness route."""
    answer_raw = _read(answer_key)
    chains = _chains(_decode(answer_raw))
    model_raw = _read(model, MODEL_CAP)
    population = run / "composed.population.json"
    record = run / "composition.json"
    pop_raw, record_raw = _read(population, MODEL_CAP), _read(record, MAX_RECORD_BYTES)
    checked_model = load_model_bytes(model_raw, source=model)
    verify_composition(checked_model, model_raw, pop_raw, parse_record(record_raw), run/"sources")
    counts = {"supported": [0, 0], "excluded": [0, 0]}
    results = []
    with tempfile.TemporaryDirectory(prefix="gnd-lineage-score-") as scratch:
        snapshot = Path(scratch).resolve()
        frozen_model, frozen_population, frozen_record = (
            snapshot/"model.orm.yaml", snapshot/"composed.population.json", snapshot/"composition.json"
        )
        for path, raw in ((frozen_model, model_raw), (frozen_population, pop_raw), (frozen_record, record_raw)):
            path.write_bytes(raw)
        target = snapshot/"targets.json"
        for row in chains:
            path = row["path"]
            claims = [_claim("lineage_arc", child, parent) for parent, child in dict.fromkeys(pairwise(path))]
            claims.append(_claim("lineage_ancestor", path[-1], path[0]))
            target.write_bytes(canonical_json_bytes({"version": 1, "targets": claims}))
            witness = api.witness(frozen_model, frozen_population, target, composition=frozen_record)
            exit_code = witness["exit_code"]
            _require(exit_code in (0, 2), "witness:refused")
            kind = "supported" if row["label"] == "supported" else "excluded"
            correct = exit_code == (0 if kind == "supported" else 2)
            counts[kind][0] += correct
            counts[kind][1] += 1
            results.append({"id": row["id"], "witness_exit": exit_code, "correct": correct})
    return {"schema": SCORE_SCHEMA, "exit_code": int(any(a != b for a, b in counts.values())),
            "model_sha256": sha256_hex(model_raw), "composition_sha256": sha256_hex(record_raw),
            "answers_sha256": sha256_hex(answer_raw), "counts": counts, "paths": results}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="route", required=True)
    build = sub.add_parser("assemble")
    for field in ("example", "model", "annotations", "out"):
        build.add_argument(field, type=Path)
    judge = sub.add_parser("score")
    for field in ("model", "run", "answer_key"):
        judge.add_argument(field, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.route == "assemble":
            assemble(args.example, args.model, args.annotations, args.out)
            result = {"exit_code": 0}
        else:
            result = score(args.model, args.run, args.answer_key)
    except Refusal as error:
        result = {"exit_code": 3, "reason": error.reason}
    except (ArtifactError, CompositionError, JudgmentInputError, ModelLoadError, OSError, ValueError,
            KeyError, TypeError, UnicodeError, RecursionError):
        result = {"exit_code": 3, "reason": "lineage:invalid-input"}
    print(json.dumps(result, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
