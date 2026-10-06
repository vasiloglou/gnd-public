"""Saved external opinions: byte binding and separate admission/repair policy."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from decimal import Decimal, localcontext
from pathlib import Path

from gnd.admission_validation import validate_admission_payload
from gnd.artifacts import (
    ArtifactError,
    _open_root,
    canonical_json_bytes,
    read_regular_bounded_at,
    sha256_hex,
)
from gnd.json_input import JsonInputRefusal, bounded_json, validate_json_value
from gnd.manifest_paths import manifest_path_issue
from gnd.model import load_model_bytes
from gnd.population import load_population_bytes

MAX_JUDGMENT_WORK = 100000
JUDGMENT_WALL_SECONDS = 10
VERDICTS = {"approve", "reject", "abstain"}
SEMANTICS = {"distribution-concentration", "provider-defined", "estimated-verdict-correctness"}


class JudgmentInputError(ValueError):
    def __init__(self, reason, message):
        self.reason = reason
        super().__init__(message[:256])


def refuse(reason="shape", message="invalid saved judgment input"):
    raise JudgmentInputError(reason, message)


def obj(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys.split()):
        refuse()


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        refuse()


def text(value, cap=256):
    if not isinstance(value, str) or not value or len(value.encode()) > cap:
        refuse()


def digest(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        refuse()


def path(value):
    text(value, 4096)
    if manifest_path_issue("source", value, "judgment"):
        refuse("binding", "unsafe evidence path")


def number(value, unit=True):
    if type(value) not in (int, float, Decimal):
        refuse()
    value = Decimal(str(value))
    if not value.is_finite() or (unit and not 0 <= value <= 1):
        refuse()
    return value


def cap(value, maximum, reason="shape"):
    if value > maximum:
        refuse(reason, "saved judgment resource ceiling exceeded")


def parse(raw, maximum):
    try:
        return bounded_json(raw, max_bytes=maximum)
    except JsonInputRefusal as error:
        refuse(
            "shape" if error.reason == "limit" and len(raw) <= maximum else error.reason,
            "invalid bounded judgment JSON",
        )


def floor(value):
    if value is None:
        return
    obj(value, "metric semantics minimum")
    if value["metric"] not in {"reported-confidence", "verdict-probability"}:
        refuse()
    if value["semantics"] not in SEMANTICS | {"mapped-verdict-probability"}:
        refuse()
    if (
        value["metric"] == "verdict-probability"
        and value["semantics"] != "mapped-verdict-probability"
    ) or (value["metric"] == "reported-confidence" and value["semantics"] not in SEMANTICS):
        refuse()
    number(value["minimum"])


def policy_shape(doc):
    obj(doc, "schema_version policy_id trust_mode judges targets admission repair trusted_receipts")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        refuse("unsupported", "unsupported judgment version")
    text(doc["policy_id"])
    if doc["trust_mode"] not in {"consumer-pinned", "self-asserted"}:
        refuse()
    for key, maximum in [("judges", 32), ("targets", 1024), ("trusted_receipts", 8192)]:
        if not isinstance(doc[key], list):
            refuse()
        cap(len(doc[key]), maximum)
    if not doc["judges"] or not doc["targets"]:
        refuse()
    cap(len(doc["judges"]) * len(doc["targets"]), 4096)
    for judge in doc["judges"]:
        text(judge)
    if len(set(doc["judges"])) != len(doc["judges"]):
        refuse()
    targets = set()
    for target in doc["targets"]:
        obj(target, "fact_type index")
        text(target["fact_type"])
        integer(target["index"])
        key = target["fact_type"], target["index"]
        if key in targets:
            refuse()
        targets.add(key)
    for action, count in [("admission", "minimum_approvals"), ("repair", "minimum_rejections")]:
        obj(doc[action], count + " evidence_floor")
        integer(doc[action][count], 1)
        if doc[action][count] > len(doc["judges"]):
            refuse()
        floor(doc[action]["evidence_floor"])
    pins = set()
    for pin in doc["trusted_receipts"]:
        obj(pin, "judge_id receipt_sha256")
        digest(pin["receipt_sha256"])
        key = pin["judge_id"], pin["receipt_sha256"]
        if pin["judge_id"] not in doc["judges"] or key in pins:
            refuse("trust", "invalid consumer pin catalog")
        pins.add(key)
    if doc["trust_mode"] == "self-asserted" and pins:
        refuse("trust", "self assertion cannot carry consumer pins")


def answer_shape(a):
    base = "kind value confidence confidence_semantics"
    kind = a.get("kind") if isinstance(a, dict) else None
    obj(
        a,
        base
        + (
            " probabilities"
            if kind == "choice"
            else " probabilities legend"
            if kind == "score"
            else ""
        ),
    )
    if kind not in {"choice", "score", "binary-probability", "verdict-confidence"}:
        refuse("unsupported", "unsupported answer primitive")
    if a["confidence"] is not None:
        number(a["confidence"])
        if a["confidence_semantics"] not in SEMANTICS:
            refuse()
    elif a["confidence_semantics"] is not None:
        refuse()
    if kind in {"choice", "score"} and a["confidence_semantics"] not in {
        None,
        "distribution-concentration",
    }:
        refuse()
    if kind == "binary-probability" and (
        a["confidence"] is not None or a["confidence_semantics"] is not None
    ):
        refuse()
    if kind == "verdict-confidence" and (
        a["confidence"] is None
        or a["confidence_semantics"] not in {"provider-defined", "estimated-verdict-correctness"}
    ):
        refuse()
    if kind == "binary-probability":
        number(a["value"])
    elif kind == "verdict-confidence":
        if a["value"] not in VERDICTS:
            refuse()
    elif kind == "choice":
        text(a["value"])
    else:
        number(a["value"], False)
    if kind not in {"choice", "score"}:
        return 0
    probs = a["probabilities"]
    if not isinstance(probs, list) or not probs:
        refuse()
    if len(probs) > 64:
        refuse("shape", "unsupported answer arity")
    keys = set()
    total = Decimal(0)
    with localcontext() as context:
        context.prec = 512
        for p in probs:
            k = "label" if kind == "choice" else "level"
            obj(p, k + " probability")
            text(p[k]) if kind == "choice" else number(p[k], False)
            if p[k] in keys:
                refuse()
            keys.add(p[k])
            total += number(p["probability"])
        if abs(total - 1) > Decimal("0.000001"):
            refuse()
    if kind == "choice" and a["value"] not in keys:
        refuse()
    if kind == "score":
        if not isinstance(a["legend"], list) or not a["legend"]:
            refuse()
        cap(len(a["legend"]), 64)
        levels, labels = set(), set()
        for row in a["legend"]:
            obj(row, "label level")
            text(row["label"])
            number(row["level"], False)
            if row["label"] in labels or row["level"] in levels:
                refuse()
            labels.add(row["label"])
            levels.add(row["level"])
        if (
            [r["level"] for r in a["legend"]] != sorted(levels)
            or levels != keys
            or not min(levels) <= a["value"] <= max(levels)
        ):
            refuse()
    return len(probs)


def receipt_shape(r):
    obj(r, "receipt_id judge_id verdict trust subject sources external_evidence")
    text(r["receipt_id"])
    text(r["judge_id"])
    if r["verdict"] not in VERDICTS or r["trust"] not in {"self-asserted", "consumer-pinned"}:
        refuse()
    s = r["subject"]
    obj(s, "model_sha256 population_sha256 reference_identity fact_type index fact_sha256")
    for k in ("model_sha256", "population_sha256", "fact_sha256"):
        digest(s[k])
    text(s["fact_type"])
    integer(s["index"])
    if s["reference_identity"] is not None:
        obj(s["reference_identity"], "identity_version references")
        if (
            type(s["reference_identity"]["identity_version"]) is not int
            or s["reference_identity"]["identity_version"] != 1
        ):
            refuse()
        if not isinstance(s["reference_identity"]["references"], list):
            refuse()
        for ref in s["reference_identity"]["references"]:
            obj(ref, "id sha256")
            text(ref["id"])
            digest(ref["sha256"])
    if not isinstance(r["sources"], list) or not r["sources"]:
        refuse()
    cap(len(r["sources"]), 8)
    for source in r["sources"]:
        obj(source, "path sha256 quote")
        path(source["path"])
        digest(source["sha256"])
        if source["quote"] is not None:
            q = source["quote"]
            obj(q, "start end sha256")
            integer(q["start"])
            integer(q["end"])
            digest(q["sha256"])
            if q["start"] >= q["end"]:
                refuse("binding", "invalid evidence byte slice")
    e = r["external_evidence"]
    if e is None:
        return 0
    obj(e, "producer normalization_contract answer calibration_claim")
    obj(e["producer"], "system model version")
    text(e["producer"]["system"])
    for k in ("model", "version"):
        if e["producer"][k] is not None:
            text(e["producer"][k])
    if e["calibration_claim"] not in {"unspecified", "provider-reported"}:
        refuse()
    obj(e["normalization_contract"], "path sha256")
    path(e["normalization_contract"]["path"])
    digest(e["normalization_contract"]["sha256"])
    return answer_shape(e["answer"])


@dataclass(frozen=True)
class JudgmentPolicy:
    raw: bytes
    doc: dict


@dataclass(frozen=True)
class JudgmentReceipt:
    raw: bytes
    doc: dict

    def __post_init__(self):
        try:
            validate_json_value(self.doc)
            receipt_shape(self.doc)
        except JsonInputRefusal:
            refuse()


def read_judgment_policy(raw):
    doc = parse(raw, 1024 * 1024)
    policy_shape(doc)
    return JudgmentPolicy(raw, doc)


def read_judgment_receipts(raw):
    doc = parse(raw, 10 * 1024 * 1024)
    obj(doc, "schema_version receipts")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        refuse("unsupported", "unsupported receipt version")
    if not isinstance(doc["receipts"], list):
        refuse()
    cap(len(doc["receipts"]), 4096)
    paths, cells = set(), 0
    for r in doc["receipts"]:
        cells += receipt_shape(r)
        cap(cells, 100000, "limit")
        paths.update(s["path"] for s in r["sources"])
        cap(len(paths), 128)
    return tuple(JudgmentReceipt(raw, r) for r in doc["receipts"])


def judgment_receipt_digest(receipt):
    try:
        validate_json_value(receipt)
        receipt_shape(receipt)
        return sha256_hex(canonical_json_bytes(receipt, exact_numbers=True))
    except JsonInputRefusal:
        refuse()


def judgment_fact_digest(fact_type, index, roles):
    text(fact_type)
    integer(index)
    try:
        validate_json_value(roles)
        if not isinstance(roles, dict):
            refuse()
        return sha256_hex(
            canonical_json_bytes(
                {"fact_type": fact_type, "index": index, "roles": roles}, exact_numbers=True
            )
        )
    except (JsonInputRefusal, ValueError):
        refuse()


def normalized(r, sources):
    e = r["external_evidence"]
    if e is None:
        return None
    n = e["normalization_contract"]
    if not any(s["path"] == n["path"] and s["sha256"] == n["sha256"] for s in r["sources"]):
        refuse("binding", "normalization is not bound source evidence")
    doc = parse(sources[n["path"]], 1024 * 1024)
    a = e["answer"]
    kind = a["kind"]
    extra = (
        " mapping"
        if kind == "choice"
        else ""
        if kind == "verdict-confidence"
        else " approve_at_or_above reject_at_or_below"
    )
    obj(doc, "schema_version kind" + extra)
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1 or doc["kind"] != kind:
        refuse()
    mapping = None
    if kind == "choice":
        mapping = doc["mapping"]
        if (
            not isinstance(mapping, dict)
            or set(mapping) != {p["label"] for p in a["probabilities"]}
            or any(v not in VERDICTS for v in mapping.values())
        ):
            refuse()
        verdict = mapping[a["value"]]
    elif kind == "verdict-confidence":
        verdict = a["value"]
    else:
        hi, lo = (
            number(doc["approve_at_or_above"], kind == "binary-probability"),
            number(doc["reject_at_or_below"], kind == "binary-probability"),
        )
        if lo >= hi:
            refuse()
        verdict = "approve" if a["value"] >= hi else "reject" if a["value"] <= lo else "abstain"
    if verdict != r["verdict"]:
        refuse("binding", "normalized verdict differs")
    probability = None
    with localcontext() as context:
        context.prec = 512
        if kind == "binary-probability":
            probability = (
                number(a["value"])
                if verdict == "approve"
                else 1 - number(a["value"])
                if verdict == "reject"
                else None
            )
        elif kind in {"choice", "score"}:
            probability = Decimal(0)
            for p in a["probabilities"]:
                mapped = (
                    mapping[p["label"]]
                    if kind == "choice"
                    else "approve"
                    if p["level"] >= hi
                    else "reject"
                    if p["level"] <= lo
                    else "abstain"
                )
                if mapped == verdict:
                    probability += number(p["probability"])
    return a["confidence"], a["confidence_semantics"], probability


def qualification(verdict, expected, floor_value, evidence):
    if verdict == "missing":
        return "missing"
    if verdict != expected:
        return "not-applicable"
    if floor_value is None:
        return "qualified"
    if evidence is None:
        return "evidence-unavailable"
    value, semantics = (
        (evidence[0], evidence[1])
        if floor_value["metric"] == "reported-confidence"
        else (evidence[2], "mapped-verdict-probability")
    )
    if value is None or semantics != floor_value["semantics"]:
        return "evidence-unavailable"
    return (
        "qualified" if number(value) >= number(floor_value["minimum"]) else "below-evidence-floor"
    )


def evaluate_judgments(
    policy,
    receipts,
    *,
    model,
    candidate,
    mechanical_report,
    model_bytes,
    population_bytes,
    trusted_root,
    references=None,
):
    started = time.monotonic()
    if (
        not isinstance(policy, JudgmentPolicy)
        or not isinstance(receipts, tuple)
        or any(not isinstance(r, JudgmentReceipt) for r in receipts)
    ):
        refuse()
    checked = read_judgment_policy(policy.raw)
    if checked.doc != policy.doc:
        refuse("binding", "policy retained bytes differ")
    raw = (
        receipts[0].raw if receipts else canonical_json_bytes({"schema_version": 1, "receipts": []})
    )
    retained = parse(raw, 10 * 1024 * 1024)
    obj(retained, "schema_version receipts")
    cap(len(receipts), 4096)
    if (
        type(retained["schema_version"]) is not int
        or retained["schema_version"] != 1
        or retained["receipts"] != [r.doc for r in receipts]
        or any(r.raw != raw for r in receipts)
    ):
        refuse("binding", "receipt retained bytes differ")
    cap(len({s["path"] for r in receipts for s in r.doc["sources"]}), 128)
    cap(
        sum(
            len(r.doc["external_evidence"]["answer"].get("probabilities", []))
            for r in receipts
            if r.doc["external_evidence"]
        ),
        100000,
        "limit",
    )
    p = policy.doc
    try:
        loaded = load_model_bytes(model_bytes, source="model.orm.yaml")
        supplied = load_population_bytes(population_bytes, source="candidate.pop.json", model=model)
        if (
            loaded.model_dump() != model.model_dump()
            or supplied.facts != candidate.facts
            or not candidate.matches_validation_marker(model)
        ):
            refuse("binding", "raw subject differs from validated objects")
        validate_admission_payload(
            mechanical_report, model=model, candidate=candidate, references=references
        )
    except (ValueError, TypeError, AttributeError) as error:
        if isinstance(error, JudgmentInputError):
            raise
        refuse("binding", "invalid bound mechanical input")
    inner = mechanical_report.get("report", mechanical_report)
    identity = mechanical_report.get("reference_binding")
    admitted = {
        (r["fact_ref"]["fact_type"], r["fact_ref"]["index"]) for r in inner["admission"]["admitted"]
    }
    targets = {(t["fact_type"], t["index"]) for t in p["targets"]}
    supplied_types = {
        ft["id"] for ft in model.fact_types if ft.get("derivation", "supplied") == "supplied"
    }
    for ft, index in targets:
        if (
            ft not in supplied_types
            or ft in (references._owners if references else {})
            or index >= len(candidate.facts.get(ft, []))
        ):
            refuse("binding", "target is not a supplied candidate occurrence")
    work = (
        len(targets) * len(p["judges"])
        + len(receipts)
        + len(p["trusted_receipts"])
        + sum(len(r.doc["sources"]) for r in receipts)
    )
    cap(work, MAX_JUDGMENT_WORK, "limit")
    if time.monotonic() - started >= JUDGMENT_WALL_SECONDS:
        refuse("limit", "judgment deadline exhausted")
    pins = {(pin["judge_id"], pin["receipt_sha256"]) for pin in p["trusted_receipts"]}
    source_bytes = {}
    cells = {}
    ids = set()
    total = 0
    try:
        fd = _open_root(Path(trusted_root))
        try:
            for retained in receipts:
                r = retained.doc
                s = r["subject"]
                key = (s["fact_type"], s["index"])
                judge = r["judge_id"]
                if (
                    key not in targets
                    or judge not in p["judges"]
                    or r["receipt_id"] in ids
                    or (key, judge) in cells
                ):
                    refuse("binding", "duplicate or unexpected judgment")
                ids.add(r["receipt_id"])
                if (
                    s["model_sha256"] != sha256_hex(model_bytes)
                    or s["population_sha256"] != sha256_hex(population_bytes)
                    or s["reference_identity"] != identity
                    or s["fact_sha256"]
                    != judgment_fact_digest(*key, candidate.facts[key[0]][key[1]])
                ):
                    refuse("binding", "stale judgment subject")
                for source in r["sources"]:
                    name = source["path"]
                    if name not in source_bytes:
                        data, _ = read_regular_bounded_at(fd, name, max_bytes=1024 * 1024)
                        total += len(data)
                        cap(total, 16 * 1024 * 1024, "limit")
                        source_bytes[name] = data
                    data = source_bytes[name]
                    q = source["quote"]
                    if sha256_hex(data) != source["sha256"] or (
                        q is not None
                        and (
                            q["end"] > len(data)
                            or sha256_hex(data[q["start"] : q["end"]]) != q["sha256"]
                        )
                    ):
                        refuse("binding", "evidence bytes differ")
                rd = sha256_hex(canonical_json_bytes(r, exact_numbers=True))
                if r["trust"] != p["trust_mode"] or (
                    p["trust_mode"] == "consumer-pinned" and (judge, rd) not in pins
                ):
                    refuse("trust", "receipt is outside consumer authority")
                evidence = normalized(r, source_bytes)
                cells[key, judge] = (r, rd, evidence)
                if time.monotonic() - started >= JUDGMENT_WALL_SECONDS:
                    refuse("limit", "judgment deadline exhausted")
        finally:
            os.close(fd)
    except (ArtifactError, OSError) as error:
        refuse(
            "limit" if any(w in str(error) for w in ("cap", "exceed", "over")) else "binding",
            "source is unavailable or unstable",
        )
    results = []
    review = False
    for target in p["targets"]:
        key = target["fact_type"], target["index"]
        rows = []
        approvals = rejections = 0
        missing = False
        for judge in p["judges"]:
            cell = cells.get((key, judge))
            r, rd, e = cell if cell else (None, None, None)
            verdict = r["verdict"] if r else "missing"
            aq = qualification(verdict, "approve", p["admission"]["evidence_floor"], e)
            rq = qualification(verdict, "reject", p["repair"]["evidence_floor"], e)
            approvals += aq == "qualified"
            rejections += rq == "qualified"
            missing |= r is None
            review |= aq in {"missing", "below-evidence-floor", "evidence-unavailable"} or rq in {
                "missing",
                "below-evidence-floor",
                "evidence-unavailable",
            }
            rows.append(
                {
                    "judge_id": judge,
                    "receipt_id": r["receipt_id"] if r else None,
                    "receipt_sha256": rd,
                    "verdict": verdict,
                    "trust": r["trust"] if r else None,
                    "external_evidence": r["external_evidence"] if r else None,
                    "admission_qualification": aq,
                    "repair_qualification": rq,
                }
            )
        opinion = not missing and approvals >= p["admission"]["minimum_approvals"]
        results.append(
            {
                **target,
                "opinion_admission": opinion,
                "admitted": opinion and key in admitted,
                "repair": not missing and rejections >= p["repair"]["minimum_rejections"],
                "judgments": rows,
            }
        )
    return {
        "assurance": "none",
        "policy_id": p["policy_id"],
        "policy_sha256": sha256_hex(policy.raw),
        "receipts_sha256": sha256_hex(raw),
        "verification_contract": "consumer-pinned-bytes-v1"
        if p["trust_mode"] == "consumer-pinned"
        else "self-asserted",
        "admission": all(r["admitted"] for r in results),
        "repair": any(r["repair"] for r in results),
        "review_required": review,
        "targets": results,
    }


def redact_policy(result):
    import copy

    result = copy.deepcopy(result)
    result["policy_id"] = "[redacted]"
    for t in result["targets"]:
        for row in t["judgments"]:
            row.update(
                judge_id="[redacted]", receipt_id=None, receipt_sha256=None, external_evidence=None
            )
    return result
