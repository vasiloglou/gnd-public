"""A labelled reference set for the reading stages, and its scorer.

The set is an overlay on the literature regression corpus: the twelve
development documents as sectioned sources, the corpus model as JSON, and
the answer key's gold facts as labels. ``build_root`` writes it from the
packaged corpus, which it never changes. ``score`` compares a reading run's
produced facts with the labels. The rule is in ``reference_fixture/README.md``.
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from gnd.artifacts import canonical_json_bytes, read_regular_bounded
from gnd.model import parse_model_document

from .depth import ExampleError, _decode

HERE = Path(__file__).resolve().parent
ROOT = HERE / "reference_fixture"
LABELS_FORMAT = "literature-reference-labels/1"
SCORE_FORMAT = "literature-reference-score/1"
SOURCE_VERSION = "corpus-1"
PRODUCER_LABEL = "claude-sonnet-5-5"
QUESTION_FACT = "method_builds_on_method"
MODEL = "corpus.orm.json"
STAGE_PAYLOADS = (("broad", "payload-1.json"), ("targeted", "payload-3.json"))
READ_LIMIT = 1 << 20
LICENCE = ("Synthetic paraphrases of public works, written for this repository's regression tests; "
           "no document is the text of its work (see the corpus README).")


def _json(path: Path) -> dict:
    return _decode(read_regular_bounded(path.parent, path.name, max_bytes=READ_LIMIT)[0], max_bytes=READ_LIMIT)


def _section_id(passage: str) -> str:
    document, _, number = passage.rpartition(".")
    if not document or not number.startswith("p") or not number[1:].isdigit():
        raise ExampleError(f"unexpected corpus passage id {passage!r}")
    return f"{document}-{number}"


def _byte_offset(text: str, index: int) -> int:
    return len(text[:index].encode("utf-8"))


def build(corpus_root: Path = HERE) -> dict[str, bytes]:
    """The reference root's files, by name, built from the packaged corpus."""
    corpus = _json(corpus_root / "corpus" / "corpus.json")
    key = _json(corpus_root / "answers" / "answer-key.json")
    model_path = corpus_root / "model.orm.yaml"
    model = parse_model_document(read_regular_bounded(corpus_root, model_path.name, max_bytes=READ_LIMIT)[0],
                                 source=model_path)
    documents = [row for row in corpus["documents"] if row["split"] == "dev"]
    files: dict[str, bytes] = {MODEL: canonical_json_bytes(model)}
    sources, sections, questions, section_of = [], [], [], {}
    for document in documents:
        raw = read_regular_bounded(corpus_root, document["path"], max_bytes=READ_LIMIT)[0]
        text = unicodedata.normalize("NFC", raw.decode("utf-8"))
        if text.encode("utf-8") != raw:
            raise ExampleError(f"corpus document {document['id']} is not NFC")
        name = document["id"]
        files[f"{name}.txt"] = raw
        sources.append({"id": name, "version": SOURCE_VERSION, "path": f"{name}.txt",
                        "sha256": document["sha256"]})
        passages = [row for row in corpus["passages"] if row["document"] == name]
        for index, passage in enumerate(passages):
            section = _section_id(passage["id"])
            section_of[passage["id"]] = section
            start = 0 if index == 0 else _byte_offset(text, passage["span"]["start"])
            end = _byte_offset(text, passage["span"]["end"])
            sections.append({"id": section, "source": name, "kind": "section",
                             "selection": "opening" if index == 0 else "targeted", "keys": [],
                             "span": [start, end], "reason": None})
            if index:
                questions.append({"id": f"q-{section}", "section": section, "fact": QUESTION_FACT,
                                  "required": False, "superseded_by": None, "denial": False})
    files["roster.json"] = canonical_json_bytes({
        "format": "literature-reading-roster/1", "sources": sources, "sections": sections,
        "questions": questions, "revisit_keys": [],
    })
    files["profile.json"] = canonical_json_bytes({
        "format": "literature-reading-profile/1", "model": MODEL, "includes": [], "producer_label": PRODUCER_LABEL,
        "base_facts": {}, "review": False, "calibration": None, "conflict": None, "absence": False,
    })
    anchored: dict[tuple, set] = {}
    for row in key["anchored_facts"]:
        fact = row["fact"]
        identity = (fact["fact_type"], tuple(sorted(fact["roles"].items())))
        anchored.setdefault(identity, set()).add(section_of[row["passage"]])
    derived = {row["id"] for row in model["fact_types"] if row.get("derivation") is not None}
    labels = []
    for document in documents:
        gold = _json(corpus_root / "answers" / "gold" / f"{document['id']}.population.json")
        for fact_type in sorted(set(gold["facts"]) - derived):
            for roles in gold["facts"][fact_type]:
                identity = (fact_type, tuple(sorted(roles.items())))
                labels.append({"document": document["id"], "fact_type": fact_type, "roles": roles,
                               "sections": sorted(anchored.get(identity, ()))})
    counts = Counter(label["fact_type"] for label in labels)
    files["labels.json"] = canonical_json_bytes({
        "format": LABELS_FORMAT, "corpus_sha256": key["corpus_sha256"], "licence": LICENCE,
        "derived_fact_types_left_out": sorted(derived),
        "counts": dict(sorted(counts.items())), "facts": labels,
    })
    return files


def build_root(out: Path, corpus_root: Path = HERE) -> None:
    """Write the reference root's built files into ``out``."""
    out.mkdir(parents=True, exist_ok=False)
    for name, raw in build(corpus_root).items():
        (out / name).write_bytes(raw)


def _normal(value: object) -> str:
    if not isinstance(value, str):
        raise ExampleError("a scored role value is not a string")
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def _values(roles: dict) -> tuple:
    return tuple(sorted((name, _normal(value)) for name, value in roles.items()))


def _attempts(run: Path, payload: str) -> list[dict]:
    rows = _json(run / payload).get("attempts")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ExampleError(f"{payload} has no attempts list")
    return rows


def score(run: Path, root: Path = ROOT) -> dict:
    """Score a reading run over the reference root against its labels."""
    labels = _json(root / "labels.json")
    if labels.get("format") != LABELS_FORMAT or not isinstance(labels.get("facts"), list):
        raise ExampleError("invalid reference labels")
    roster = _json(root / "roster.json")
    sections = {row["id"]: row["source"] for row in roster["sections"]}
    gold = []
    for index, fact in enumerate(labels["facts"]):
        scope = set(fact["sections"]) or {name for name, source in sections.items() if source == fact["document"]}
        gold.append((index, fact["fact_type"], _values(fact["roles"]), scope))
    found: set[int] = set()
    stages, recall = {}, {}
    for stage, payload in STAGE_PAYLOADS:
        produced = hit = wrong = outside = 0
        for attempt in _attempts(run, payload):
            section = attempt.get("section")
            facts = (attempt.get("response") or {}).get("facts")
            if section not in sections or not isinstance(facts, dict):
                raise ExampleError("a scored attempt names no known section or facts")
            for fact_type, rows in facts.items():
                if not isinstance(rows, list):
                    raise ExampleError("scored facts are not a list")
                for row in rows:
                    if not isinstance(row, dict):
                        raise ExampleError("a scored fact row is not an object")
                    produced += 1
                    values = _values(row)
                    in_scope = [g for g in gold if section in g[3]]
                    match = [g[0] for g in in_scope if g[1] == fact_type and g[2] == values]
                    if match:
                        hit += 1
                        found.update(match)
                    elif any(sorted(v for _, v in g[2]) == sorted(v for _, v in values) for g in in_scope):
                        wrong += 1
                    if not in_scope:
                        outside += 1
        stages[stage] = {"produced": produced, "found": hit, "wrong_predicate": wrong,
                         "outside_gold_scope": outside, "precision": [hit, produced]}
        recall[stage] = [len(found), len(gold)]
    return {"format": SCORE_FORMAT, "gold_facts": len(gold), "stages": stages, "recall_after": recall}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    built = commands.add_parser("build", help="write the reference root's built files")
    built.add_argument("--out", type=Path, required=True)
    scored = commands.add_parser("score", help="score a reading run over the reference root")
    scored.add_argument("run", type=Path)
    scored.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            build_root(args.out)
        else:
            sys.stdout.buffer.write(canonical_json_bytes(score(args.run, args.root)) + b"\n")
    except (ExampleError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
