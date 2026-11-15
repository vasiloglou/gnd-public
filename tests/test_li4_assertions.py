"""Corpus-first LI4 admission, saved-opinion and publication controls."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

from gnd.judgments import judgment_fact_digest, judgment_receipt_digest

EXAMPLE = Path(__file__).resolve().parents[1] / "src/gnd/examples/literature/assertions"
FACT = "assertion_statement"


def read(path):
    return json.loads(path.read_bytes())


def dump(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(root, out):
    return subprocess.run([sys.executable, "-m", "gnd.examples.literature.assertion_admission",
                           str(root / "model.orm.yaml"), str(root / "raw.population.json"),
                           str(root / "policy.json"), str(root / "receipts.json"), str(root / "evidence"),
                           "--out", str(out)], check=False, capture_output=True, text=True)


def copied(tmp_path):
    root = tmp_path / "case"
    shutil.copytree(EXAMPLE, root)
    return root


def repin(root, receipts):
    policy = read(root / "policy.json")
    policy["trusted_receipts"] = [{"judge_id": rec["judge_id"], "receipt_sha256": judgment_receipt_digest(rec)}
                                  for rec in receipts["receipts"]]
    dump(root / "policy.json", policy)
    dump(root / "receipts.json", receipts)


def _rows(result, stage):
    return {row["index"]: row for row in result["stages"][stage]}


def test_contextual_assertions_and_reviewed_projection(tmp_path):
    expected = read(EXAMPLE / "case-outcomes.json")
    out = tmp_path / "admitted"
    done = run(EXAMPLE, out)
    assert done.returncode == expected["producer_exit"], done.stderr
    record = read(out / "admission.json")
    assert record["schema"] == "literature-assertion-admission/1"
    judgment = read(out / "judgment-report.json")
    assert judgment["outcome"] == expected["judgment_exit"]
    raw = read(out / "raw.population.json")
    selected = read(out / "admitted.population.json")
    assert (out / "raw.population.json").read_bytes() == (EXAMPLE / "raw.population.json").read_bytes()
    assert selected["facts"][FACT] == [raw["facts"][FACT][i] for i in expected["positive"]]
    assert len(selected["facts"]["assertion_names_passage"]) == len(expected["positive"])
    semantic = _rows(record, "semantic-support")
    positive = _rows(record, "positive-own-findings")
    assert [i for i, row in semantic.items() if row["status"] == "pass"] == expected["supported"]
    assert [i for i, row in positive.items() if row["status"] == "pass"] == expected["positive"]
    assert semantic[expected["incorrect_predicate"]["index"]]["reason"] == expected["incorrect_predicate"]["semantic_reason"]
    assert {k: semantic[int(k)]["reason"] for k in expected["review_arms"]} == expected["review_arms"]
    assert [[raw["facts"][FACT][i]["polarity"], raw["facts"][FACT][i]["attribution"]]
            for i in (3, 4, 5, 6)] == expected["non_positive"]
    assert {item["experiment"] for item in selected["facts"][FACT]} >= {"trial-a", "trial-b"}
    assert selected["facts"][FACT][0]["condition"] == expected["conditional"]["condition"]
    for field, path in (("model", EXAMPLE / "model.orm.yaml"), ("raw", out / "raw.population.json"),
                        ("policy", EXAMPLE / "policy.json"), ("receipts", EXAMPLE / "receipts.json"),
                        ("judgment_report", out / "judgment-report.json"), ("admitted", out / "admitted.population.json")):
        assert record[field + "_sha256"] == sha(path)


def test_conditional_marker_survives_condition_loss_as_a_failure(tmp_path):
    root = copied(tmp_path)
    population = root / "raw.population.json"
    doc = read(population)
    doc["facts"][FACT][0]["condition"] = "unspecified"
    dump(population, doc)
    receipts = read(root / "receipts.json")
    for receipt in receipts["receipts"]:
        subject = receipt["subject"]
        index = subject["index"]
        subject["population_sha256"] = sha(population)
        subject["fact_sha256"] = judgment_fact_digest(FACT, index, doc["facts"][FACT][index])
    repin(root, receipts)
    out = tmp_path / "admitted"
    assert run(root, out).returncode == 0
    actual = _rows(read(out / "admission.json"), "semantic-support")[0]
    assert actual["status"] == "fail" and actual["reason"] == "missing-condition"
    assert "p01" not in {item["passage"] for item in read(out / "admitted.population.json")["facts"][FACT]}


@pytest.mark.parametrize("fault", ["raw-missing", "policy-missing", "stale-subject", "stale-source",
                                   "report-instead-of-receipts", "malformed", "over-limit"])
def test_inputs_refuse_without_a_complete_publication(tmp_path, fault):
    root = copied(tmp_path)
    if fault == "raw-missing":
        (root / "raw.population.json").unlink()
    elif fault == "policy-missing":
        (root / "policy.json").unlink()
    elif fault == "stale-subject":
        with (root / "raw.population.json").open("a") as f:
            f.write(" ")
    elif fault == "stale-source":
        with (root / "evidence/passages.txt").open("a") as f:
            f.write(" ")
    elif fault == "report-instead-of-receipts":
        dump(root / "receipts.json", {"outcome": 0, "judgment_policy": {"admission": True}})
    elif fault == "malformed":
        (root / "policy.json").write_text("[")
    else:
        policy = read(root / "policy.json")
        policy["targets"] *= 103
        dump(root / "policy.json", policy)
    out = tmp_path / "admitted"
    done = run(root, out)
    assert done.returncode == read(EXAMPLE / "case-outcomes.json")["invalid_exit"], done.stderr
    assert "Traceback" not in done.stderr and not out.exists()


def test_receipt_serialization_then_verdict_change(tmp_path):
    root = copied(tmp_path)
    outs = [tmp_path / name for name in ("before", "whitespace", "rejected")]
    assert run(root, outs[0]).returncode == 0
    receipt_path = root / "receipts.json"
    with receipt_path.open("a") as f:
        f.write(" ")
    assert run(root, outs[1]).returncode == 0
    assert sha(outs[0] / "admission.json") != sha(outs[1] / "admission.json")
    assert sha(outs[0] / "admitted.population.json") == sha(outs[1] / "admitted.population.json")
    receipts = read(receipt_path)
    receipts["receipts"][0]["verdict"] = "reject"
    repin(root, receipts)
    assert run(root, outs[2]).returncode == 0
    assert sha(outs[0] / "admitted.population.json") != sha(outs[2] / "admitted.population.json")
    original_marker = (outs[0] / "admission.json").read_bytes()
    assert run(root, outs[0]).returncode == 3
    assert (outs[0] / "admission.json").read_bytes() == original_marker


def test_maximum_contextual_projection_is_bounded():
    from gnd.examples.literature.assertion_admission import project

    subject = read(EXAMPLE / "raw.population.json")
    seed = subject["facts"][FACT][0]
    subject["facts"][FACT] = [{**seed, "passage": f"q-{i}"} for i in range(1024)]
    subject["facts"]["assertion_names_passage"] = [{"assertion": f"a-{i}", "passage": f"q-{i}"} for i in range(1024)]
    subject["facts"]["assertion_names_work"] = [{"assertion": f"a-{i}", "work": seed["work"]} for i in range(1024)]
    targets = [{"fact_type": FACT, "index": i, "admitted": True, "judgments": []} for i in range(1024)]
    started = time.monotonic()
    population, _ = project(subject, targets)
    assert len(population["facts"][FACT]) == 1024
    assert time.monotonic() - started < 10
