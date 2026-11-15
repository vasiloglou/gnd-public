"""LI1: the literature regression corpus meets its floors and keeps its answers apart.

Criteria C1 and C6, with T1-T5 of
.gnd-planning/milestones/literature-identity/notes/phase-LI1-spec.md. These cases
read committed bytes only; they need no harness.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/literature"
BUILD = ROOT / "tools/build_literature_example.py"
CORPUS = EXAMPLE / "corpus/corpus.json"
KEY = EXAMPLE / "answers/answer-key.json"
ASSERTION_TYPE = "method_builds_on_method"
FLOORS = {
    "supported_chains": 3, "cross_domain_supported_chains": 1, "false_chains": 5,
    "reuse": {"real": 4, "generic-word": 2, "homonym": 2}, "assertions": 12,
    "identity": {"same": 3, "different": 3}, "names": {"homonym": 2, "synonym": 1, "family": 1},
}
NAMED_FALSE_STORIES = {"whale", "dollar-pinn-chain", "dollar-pinn-loop", "boltz-1-as-ancestry", "contrast-as-builds-on"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def floor_failures(key: dict) -> list[str]:
    """Every C1 floor the key misses. Empty means C1 holds."""
    failures = []
    chains = key["chains"]
    supported = [c for c in chains if c["label"] == "supported"]
    if len(supported) < FLOORS["supported_chains"]:
        failures.append("supported chains")
    if sum(c["domains"] == "cross" for c in supported) < FLOORS["cross_domain_supported_chains"]:
        failures.append("cross-domain supported chain")
    false = [c for c in chains if c["label"] == "false"]
    if len(false) < FLOORS["false_chains"] or not NAMED_FALSE_STORIES <= {c["story"] for c in false}:
        failures.append("false chains")
    for name, wanted, have in (
        ("reuse", FLOORS["reuse"], Counter(u["kind"] for u in key["reuse_cases"])),
        ("identity", FLOORS["identity"], Counter(i["label"] for i in key["identity_pairs"])),
        ("names", FLOORS["names"], Counter(n["kind"] for n in key["name_pairs"])),
    ):
        if any(have[kind] < count for kind, count in wanted.items()):
            failures.append(name)
    if len(key["assertions"]) < FLOORS["assertions"]:
        failures.append("assertions")
    return failures


# --- T1 -----------------------------------------------------------------------------


def test_counts_meet_c1_floors():
    key = _load(KEY)
    assert floor_failures(key) == []
    assert Counter(a["support"] for a in key["assertions"]) == {
        "supported": 8, "stretched": 2, "contradicted": 1, "insufficient-evidence": 1}
    # Both branches of the checker: one category below its floor is reported.
    for mutate, expected in (
        (lambda k: k["reuse_cases"].pop(), "reuse"),
        (lambda k: k["chains"].remove(next(c for c in k["chains"] if c["story"] == "whale")), "false chains"),
        (lambda k: k["assertions"].pop(), "assertions"),
        (lambda k: k["identity_pairs"].pop(0), "identity"),
    ):
        broken = copy.deepcopy(key)
        mutate(broken)
        assert expected in floor_failures(broken), expected


def test_gold_assertion_facts_are_exactly_the_supported_assertions():
    key = _load(KEY)
    supported = Counter(
        (a["passage"].split(".p")[0], json.dumps(a["fact"]["roles"], sort_keys=True))
        for a in key["assertions"] if a["support"] == "supported")
    gold = Counter()
    for path in sorted((EXAMPLE / "answers/gold").glob("*.population.json")):
        source = path.name.removesuffix(".population.json")
        for row in _load(path)["facts"].get(ASSERTION_TYPE, []):
            gold[(source, json.dumps(row, sort_keys=True))] += 1
    assert gold == supported
    assert sum(gold.values()) == 8


# --- T2 -----------------------------------------------------------------------------


def _passages() -> dict:
    corpus = _load(CORPUS)
    return {p["id"]: p for p in corpus["passages"]}, {d["id"]: d for d in corpus["documents"]}


def citations(key: dict) -> list[str]:
    refs = [a["passage"] for a in key["assertions"]] + [f["passage"] for f in key["anchored_facts"]]
    for group in ("chains", "reuse_cases", "identity_pairs", "name_pairs"):
        for item in key[group]:
            refs.extend(item["passages"])
    return refs


def unresolved_citations(key: dict, passages: dict, documents: dict) -> list[str]:
    bad = []
    for ref in citations(key):
        passage = passages.get(ref)
        if passage is None:
            bad.append(ref)
            continue
        text = (EXAMPLE / documents[passage["document"]]["path"]).read_text(encoding="utf-8")
        if not 0 <= passage["span"]["start"] < passage["span"]["end"] <= len(text):
            bad.append(ref)
    return bad


def test_every_label_cites_an_existing_passage():
    key = _load(KEY)
    passages, documents = _passages()
    assert unresolved_citations(key, passages, documents) == []
    for item in key["assertions"] + key["chains"] + key["identity_pairs"] + key["name_pairs"] + key["reuse_cases"]:
        assert item.get("passage") or item.get("passages"), item["id"]
    beyond = copy.deepcopy(passages)
    beyond["vampnet.p2"]["span"]["end"] = 10**6
    assert unresolved_citations(key, beyond, documents) == ["vampnet.p2"] * citations(key).count("vampnet.p2")
    for anchored in key["anchored_facts"]:
        assert anchored["span"] == passages[anchored["passage"]]["span"], anchored["id"]


# --- T3 -----------------------------------------------------------------------------


def test_documents_declare_paraphrase_and_identifier():
    corpus = _load(CORPUS)
    for document in corpus["documents"]:
        assert document["paraphrase"] is True
        work = document["work"]
        assert work["title"] and isinstance(work["year"], int)
        assert work["identifier"] is None or re.fullmatch(r"(arXiv:\d{4}\.\d{4,5}|doi:10\.\d{4,9}/\S+)", work["identifier"])
        raw = (EXAMPLE / document["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == document["sha256"]
        lines = raw.decode("utf-8").split("\n")
        assert lines[0].startswith("# ") and "synthetic paraphrase written for regression testing" in lines[1]
        if work["identifier"]:
            assert work["identifier"] in lines[1]


# --- T4 -----------------------------------------------------------------------------


def test_heldout_split():
    corpus = _load(CORPUS)
    key = _load(KEY)
    dev = [d for d in corpus["documents"] if d["split"] == "dev"]
    heldout = [d for d in corpus["documents"] if d["split"] == "heldout"]
    assert len(heldout) >= 3
    assert not {d["work"]["identifier"] for d in dev} & {d["work"]["identifier"] for d in heldout}
    assert not {d["work"]["title"].casefold() for d in dev} & {d["work"]["title"].casefold() for d in heldout}
    digest = (EXAMPLE / "answers/heldout.sha256").read_text(encoding="ascii").strip()
    assert re.fullmatch(r"[0-9a-f]{64}", digest) and digest != "0" * 64
    assert key["heldout"] == {"sha256": digest, "chains": {"supported": 1, "false": 2}}
    tracked = [p.name for p in EXAMPLE.rglob("*") if "heldout" in p.name and p.name != "heldout.sha256"]
    assert tracked == []
    dev_ids = {d["id"] for d in dev}
    for group in ("assertions", "anchored_facts"):
        for item in key[group]:
            assert item["passage"].split(".p")[0] in dev_ids, item["id"]
    assert {c["story"] for c in key["chains"]} >= {"whale"}


# --- T5 -----------------------------------------------------------------------------


def _generated(root: Path) -> list[str]:
    return sorted(str(p.relative_to(root)) for name in ("corpus", "answers", "runs")
                  for p in (root / name).rglob("*") if p.is_file() and p.name != "README.md")


def test_rebuild_is_byte_identical(tmp_path: Path):
    shutil.copy2(EXAMPLE / "model.orm.yaml", tmp_path / "model.orm.yaml")
    (tmp_path / "answers").mkdir()
    shutil.copy2(EXAMPLE / "answers/heldout.sha256", tmp_path / "answers/heldout.sha256")
    subprocess.run([sys.executable, str(BUILD), str(tmp_path)], check=True, capture_output=True)
    assert _generated(tmp_path) == _generated(EXAMPLE)
    for name in _generated(EXAMPLE):
        assert (tmp_path / name).read_bytes() == (EXAMPLE / name).read_bytes(), name
