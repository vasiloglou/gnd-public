"""Build the LI2 resolution fixtures under src/gnd/examples/literature/resolution/.

    uv run python tools/build_resolution_fixtures.py src/gnd/examples/literature/resolution

Spec: .gnd-planning/milestones/literature-identity/notes/phase-LI2-spec.md (§6.6).
Every document here is a synthetic fixture text, not a paraphrase of a work.
The whale texts spell VampNet and WHAM identically in both documents on
purpose: that is the host's case-folding failure the fixtures reconstruct.

Each case is a self-contained composition directory under cases/<id>/. Its
expected outcome (an exit code, and for a refusal the exact message) is in
cases.json, which the corpus gate approves. Every byte is computed here.
Deterministic: fixed texts, canonical key order, two-space JSON.
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

from gnd.anchors import canonical_document_text, lexical_ranges, vocabulary_digest
from gnd.extract.identity import anchor_normalize
from gnd.model import load_model

MODEL_FILE = "model.orm.yaml"
MODEL_ID = "urn:gnd-example:literature-resolution@1"
BUILDS = "method_builds_on_method"
ANCHORED = {BUILDS: ("method", "base_method"), "mention_has_surface_text": ("surface",)}
PRODUCER = {"kind": "reviewer", "id": "corpus-author"}

# --- Sources: a title line, then one passage per line ---------------------------------
# Each fact is (fact type, roles, passage line number counted from 1 after the title).

SOURCES = {
    "whale-a": {
        "title": "Notes A: a Koopman method and a pose model (synthetic fixture)",
        "lines": ["VampNet builds on DMD.", "OpenCap Monocular builds on WHAM."],
        "facts": [(BUILDS, {"method": "VampNet", "base_method": "DMD"}, 1),
                  (BUILDS, {"method": "OpenCap Monocular", "base_method": "WHAM"}, 2)],
    },
    "whale-b": {
        "title": "Notes B: a music model and a whale model (synthetic fixture)",
        "lines": ["WHAM builds on VampNet."],
        "facts": [(BUILDS, {"method": "WHAM", "base_method": "VampNet"}, 1)],
    },
    "whale-c": {
        "title": "Notes C: the music model again (synthetic fixture)",
        "lines": ["VampNet builds on masked token modelling."],
        "facts": [(BUILDS, {"method": "VampNet", "base_method": "masked token modelling"}, 1)],
    },
    "mv-a": {
        "title": "Notes on a method (synthetic fixture)",
        "lines": ["Boltz-steering builds on Boltz-1."],
        "facts": [(BUILDS, {"method": "Boltz-steering", "base_method": "Boltz-1"}, 1)],
    },
    "mv-b": {
        "title": "Notes on a version, which the extractor spelled as its method (synthetic fixture)",
        "lines": ["PoseX builds on Boltz-1, in its Boltz-1x version."],
        "facts": [(BUILDS, {"method": "PoseX", "base_method": "Boltz-1"}, 1)],
    },
    "alias-a": {
        "title": "Notes on a benchmark (synthetic fixture)",
        "lines": ["PoseX builds on AlphaFold3."],
        "facts": [(BUILDS, {"method": "PoseX", "base_method": "AlphaFold3"}, 1)],
    },
    "alias-b": {
        "title": "Notes that abbreviate the same model (synthetic fixture)",
        "lines": ["AF3 builds on Evoformer.", "Boltz-1 builds on AF3."],
        "facts": [(BUILDS, {"method": "AF3", "base_method": "Evoformer"}, 1),
                  (BUILDS, {"method": "Boltz-1", "base_method": "AF3"}, 2)],
    },
    "hom-a": {
        "title": "Notes on a tracker (synthetic fixture)",
        "lines": ["TRACE builds on Kalman filtering."],
        "facts": [(BUILDS, {"method": "TRACE", "base_method": "Kalman filtering"}, 1)],
    },
    "hom-b": {
        "title": "Notes on an interpretability method of the same name (synthetic fixture)",
        "lines": ["TRACE builds on attention."],
        "facts": [(BUILDS, {"method": "TRACE", "base_method": "attention"}, 1)],
    },
}

MENTIONS = {
    "title": "Two senses, one spelling (synthetic fixture)",
    "lines": ["VampNet, the Koopman method, is not VampNet, the music model.",
              "VampNet builds on DMD."],
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _dump(value) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def text_of(source: dict) -> str:
    return "\n".join([f"# {source['title']}", *source["lines"]]) + "\n"


def line_spans(text: str) -> list[tuple[int, int]]:
    spans, start = [], 0
    for number, line in enumerate(text.split("\n")[:-1]):
        if number >= 1:
            spans.append((start, start + len(line)))
        start += len(line) + 1
    return spans


def occurrence(text: str, value: str, span: tuple[int, int]) -> int:
    key = anchor_normalize(value)
    for index, (start, end) in enumerate(lexical_ranges(text, {key})[key]):
        if span[0] <= start and end <= span[1]:
            return index
    raise ValueError(f"{value!r} not in span {span}")


def facts_of(source: dict) -> dict:
    facts: dict[str, list] = {}
    for fact_type, roles, _ in source["facts"]:
        facts.setdefault(fact_type, []).append(dict(roles))
    return {k: facts[k] for k in sorted(facts)}


def population_bytes(facts: dict) -> bytes:
    return _dump({"population": {"model": MODEL_FILE, "model_id": MODEL_ID, "source": "agent-output",
                                 "covers": sorted(facts)}, "instances": {}, "facts": facts})


def anchors_of(source: dict, text: str) -> list[dict]:
    spans = line_spans(text)
    anchors = []
    for fact_type, roles, line in source["facts"]:
        for role in ANCHORED.get(fact_type, ()):
            start, end = spans[line - 1]
            anchors.append({"fact_key": {"fact_type": fact_type, "roles": dict(roles)}, "role": role,
                            "span": {"start": start, "end": end},
                            "occurrence": occurrence(text, roles[role], (start, end)),
                            "excerpt_sha256": _sha(text[start:end].encode("utf-8"))})
    return anchors


def evidence(source_id: str, key: int, value: str, *, skip: int = 0) -> dict:
    """The first asserted coordinate in a source whose method role holds value (after skip hits)."""
    source = SOURCES[source_id]
    text = text_of(source)
    spans = line_spans(text)
    rows: dict[str, int] = {}
    hits = 0
    for fact_type, roles, line in source["facts"]:
        index = rows.get(fact_type, 0)
        rows[fact_type] = index + 1
        for role in ("method", "base_method"):
            if roles.get(role) == value:
                if hits == skip:
                    start, end = spans[line - 1]
                    return {"key": key, "source": source_id, "fact_type": fact_type, "fact_index": index,
                            "role": role, "span": {"start": start, "end": end}}
                hits += 1
    raise ValueError(f"{value!r} not asserted in {source_id}")


def decision(kind: str, left: tuple[str, str], right: tuple[str, str], placeholders=None) -> dict:
    keys = [{"source": s, "object_type": "method", "value": v} for s, v in (left, right)]
    return {"decision": kind, "keys": keys,
            "evidence": [evidence(left[0], 0, left[1]), evidence(right[0], 1, right[1])],
            "producer": dict(PRODUCER),
            "input_sha256": {s: _sha(population_bytes(facts_of(SOURCES[s]))) for s in sorted({left[0], right[0]})},
            "placeholders": placeholders}


def renaming(source: str, role: str, old: str, new: str, cites: int | None, fact_type: str = BUILDS) -> dict:
    entry = {"source": source, "fact_type": fact_type, "role": role, "from": old, "to": new}
    if cites is not None:
        entry["decision"] = cites
    return entry


def resolution(decisions: list[dict]) -> dict:
    return {"schema": "gnd-resolution/1", "object_types": ["method"], "decisions": decisions}


# --- The cases --------------------------------------------------------------------------
# Each: sources, renamings, resolution (None = no resolution entry), edits, expected outcome.

W_RESOLVED = {
    "renamings": [renaming("whale-b", "base_method", "VampNet", "VampNet [music]", 0),
                  renaming("whale-b", "method", "WHAM", "WhAM [whale]", 1)],
    "resolution": resolution([decision("different", ("whale-a", "VampNet"), ("whale-b", "VampNet")),
                              decision("different", ("whale-a", "WHAM"), ("whale-b", "WHAM"))]),
}
A_ALIAS = [decision("same", ("alias-a", "AlphaFold3"), ("alias-b", "AF3"))]
H_UNRESOLVED = [decision("unresolved", ("hom-a", "TRACE"), ("hom-b", "TRACE"), ["TRACE#1", "TRACE#2"])]
P = "composition:invalid: "


def _edit(path: list, value):
    def apply(case):
        node = case["resolution"]
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = value
    return apply


CASES = {
    "W-flat": {"story": "The whale, composed flat: identical spellings join, so the false chain OpenCap Monocular ... DMD is derivable.",
               "sources": ["whale-a", "whale-b"], "renamings": [], "resolution": None, "exit": 0},
    "W-resolved": {"story": "The whale with two different decisions and two separating renamings: four senses stay distinct, the three edges survive, and the false chain is gone.",
                   "sources": ["whale-a", "whale-b"], **copy.deepcopy(W_RESOLVED), "exit": 0},
    "R-uncovered": {"story": "A resolution with no decisions: VampNet is joined across the two notes with no same decision (rule 1).",
                    "sources": ["whale-a", "whale-b"], "renamings": [], "resolution": resolution([]), "exit": 3,
                    "message": P + "keys at whale-a method_builds_on_method#0.method and whale-b method_builds_on_method#0.base_method (object type method) are joined without a same decision"},
    "R-wrong-decision": {"story": "A renaming cites a decision about another key (rule 6).",
                         "sources": ["whale-a", "whale-b"], **copy.deepcopy(W_RESOLVED), "exit": 3,
                         "renaming_decisions": [1, 1],
                         "message": P + "renaming 0 cites decision 1, which does not name its key"},
    "R-no-decision-field": {"story": "With a resolution present, a renaming that cites no decision is refused.",
                            "sources": ["whale-a", "whale-b"], **copy.deepcopy(W_RESOLVED), "exit": 3,
                            "renaming_decisions": [None, 1],
                            "message": P + "renaming 0 cites no decision"},
    "R-transitive": {"story": "VampNet is same across a-b and b-c, but a and c are recorded different: a transitive merge across different (rule 3).",
                     "sources": ["whale-a", "whale-b", "whale-c"], "renamings": [],
                     "resolution": resolution([decision("same", ("whale-a", "VampNet"), ("whale-b", "VampNet")),
                                               decision("same", ("whale-b", "VampNet"), ("whale-c", "VampNet")),
                                               decision("different", ("whale-a", "VampNet"), ("whale-c", "VampNet"))]),
                     "exit": 3, "message": P + "decision 2 (different) keys are connected through same decisions"},
    "R-evidence-fact": {"story": "Decision 0's first coordinate points at a fact whose role holds another value.",
                        "sources": ["whale-a", "whale-b"], **copy.deepcopy(W_RESOLVED), "exit": 3,
                        "edits": [_edit(["decisions", 0, "evidence", 0, "fact_index"], 1)],
                        "message": P + "decision 0 evidence 0 (source whale-a, method_builds_on_method#1.method) does not hold key 0"},
    "R-evidence-span": {"story": "Decision 0's first coordinate cites a span no anchor has.",
                        "sources": ["whale-a", "whale-b"], **copy.deepcopy(W_RESOLVED), "exit": 3,
                        "edits": [_edit(["decisions", 0, "evidence", 0, "span", "start"], 1)],
                        "message": P + "decision 0 evidence 0 (source whale-a, method_builds_on_method#0.method) has no anchor at its span"},
    "R-stale-input": {"story": "Decision 0 was made over another version of whale-b's population.",
                      "sources": ["whale-a", "whale-b"], **copy.deepcopy(W_RESOLVED), "exit": 3,
                      "edits": [_edit(["decisions", 0, "input_sha256", "whale-b"], "0" * 64)],
                      "message": P + "decision 0 input digest for source whale-b differs from its population"},
    "R-digest-and-uncovered": {"story": "A wrong resolution digest and an uncovered pair: the digest (step 2) is reported, not the pair (step 5).",
                               "sources": ["whale-a", "whale-b"], "renamings": [], "resolution": resolution([]),
                               "manifest_sha256": "0" * 64, "exit": 3,
                               "message": P + "resolution digest differs from the manifest"},
    "R-evidence-and-uncovered": {"story": "A bad coordinate on decision 0 and an uncovered WHAM pair: the evidence (step 3) is reported, not the pair (step 5).",
                                 "sources": ["whale-a", "whale-b"],
                                 "renamings": [renaming("whale-b", "base_method", "VampNet", "VampNet [music]", 0)],
                                 "resolution": resolution([decision("different", ("whale-a", "VampNet"), ("whale-b", "VampNet"))]),
                                 "edits": [_edit(["decisions", 0, "evidence", 0, "fact_index"], 1)], "exit": 3,
                                 "message": P + "decision 0 evidence 0 (source whale-a, method_builds_on_method#1.method) does not hold key 0"},
    "MV-joined-no-same": {"story": "A method key and a version key spelled alike are joined with no same decision (R2, rule 1).",
                          "sources": ["mv-a", "mv-b"], "renamings": [], "resolution": resolution([]), "exit": 3,
                          "message": P + "keys at mv-a method_builds_on_method#0.base_method and mv-b method_builds_on_method#0.base_method (object type method) are joined without a same decision"},
    "MV-distinct": {"story": "The same pair recorded different, with mv-b's value renamed to its version: two values.",
                    "sources": ["mv-a", "mv-b"],
                    "renamings": [renaming("mv-b", "base_method", "Boltz-1", "Boltz-1x", 0)],
                    "resolution": resolution([decision("different", ("mv-a", "Boltz-1"), ("mv-b", "Boltz-1"))]), "exit": 0},
    "A-alias": {"story": "An evidenced alias: AF3 is AlphaFold3, renamed in both roles where alias-b uses it (R3).",
                "sources": ["alias-a", "alias-b"],
                "renamings": [renaming("alias-b", "method", "AF3", "AlphaFold3", 0),
                              renaming("alias-b", "base_method", "AF3", "AlphaFold3", 0)],
                "resolution": resolution(copy.deepcopy(A_ALIAS)), "exit": 0},
    "A-same-not-applied": {"story": "A same decision the manifest never applies (rule 5).",
                           "sources": ["alias-a", "alias-b"], "renamings": [],
                           "resolution": resolution(copy.deepcopy(A_ALIAS)), "exit": 3,
                           "message": P + "decision 0 (same) keys are not joined"},
    "A-split": {"story": "The existing one-value-one-entity refusal still fires with a resolution present: AF3 renamed in one role only.",
                "sources": ["alias-a", "alias-b"],
                "renamings": [renaming("alias-b", "method", "AF3", "AlphaFold3", 0)],
                "resolution": resolution(copy.deepcopy(A_ALIAS)), "exit": 3,
                "message": P + "renaming 0 splits a value of source alias-b: method_builds_on_method.base_method still uses the old value; rename it there too"},
    "H-no-decision": {"story": "A same-domain homonym with no decision: TRACE is joined, and refused (R3).",
                      "sources": ["hom-a", "hom-b"], "renamings": [], "resolution": resolution([]), "exit": 3,
                      "message": P + "keys at hom-a method_builds_on_method#0.method and hom-b method_builds_on_method#0.method (object type method) are joined without a same decision"},
    "H-different": {"story": "The homonym recorded different, with hom-b renamed to a sense id: two values (R3).",
                    "sources": ["hom-a", "hom-b"],
                    "renamings": [renaming("hom-b", "method", "TRACE", "TRACE [attention]", 0)],
                    "resolution": resolution([decision("different", ("hom-a", "TRACE"), ("hom-b", "TRACE"))]), "exit": 0},
    "H-unresolved": {"story": "The homonym left unresolved: both keys take their placeholders and stay apart (R7).",
                     "sources": ["hom-a", "hom-b"],
                     "renamings": [renaming("hom-a", "method", "TRACE", "TRACE#1", 0),
                                   renaming("hom-b", "method", "TRACE", "TRACE#2", 0)],
                     "resolution": resolution(copy.deepcopy(H_UNRESOLVED)), "exit": 0},
    "H-unresolved-wrong": {"story": "An unresolved key renamed to something other than its placeholder (rule 4).",
                           "sources": ["hom-a", "hom-b"],
                           "renamings": [renaming("hom-a", "method", "TRACE", "TRACE#1", 0),
                                         renaming("hom-b", "method", "TRACE", "TRACE [attention]", 0)],
                           "resolution": resolution(copy.deepcopy(H_UNRESOLVED)), "exit": 3,
                           "message": P + "decision 0 (unresolved) key 1 does not take its placeholder"},
}


def write_source(folder: Path, source_id: str, vocabulary: str) -> None:
    source = SOURCES[source_id]
    folder.mkdir(parents=True)
    text = text_of(source)
    document = text.encode("utf-8")
    population = population_bytes(facts_of(source))
    (folder / "document.txt").write_bytes(document)
    (folder / "population.json").write_bytes(population)
    (folder / "population.json.anchors.json").write_bytes(_dump({
        "schema_version": 2, "population_sha256": _sha(population), "vocabulary_digest": vocabulary,
        "document_sha256": _sha(document), "anchors": anchors_of(source, canonical_document_text(document))}))


def write_case(root: Path, case_id: str, case: dict, vocabulary: str) -> dict:
    folder = root / "cases" / case_id
    case = copy.deepcopy(case)
    for source_id in case["sources"]:
        write_source(folder / source_id, source_id, vocabulary)
    renamings = case["renamings"]
    for index, cites in enumerate(case.get("renaming_decisions", [])):
        if cites is None:
            renamings[index].pop("decision", None)
        else:
            renamings[index]["decision"] = cites
    manifest = {"schema": "gnd-composition-manifest/1", "sources": case["sources"], "renamings": renamings,
                "deduplications": "identical-rows", "scope_tags": []}
    if case["resolution"] is not None:
        for edit in case.get("edits", []):
            edit(case)
        raw = _dump(case["resolution"])
        (folder / "resolution.json").write_bytes(raw)
        manifest["resolution"] = {"path": "resolution.json", "sha256": case.get("manifest_sha256", _sha(raw))}
    (folder / "manifest.json").write_bytes(_dump(manifest))
    entry = {"id": case_id, "directory": f"cases/{case_id}", "story": case["story"], "exit": case["exit"]}
    if "message" in case:
        entry["message"] = case["message"]
    return entry


def write_mentions(root: Path, vocabulary: str) -> None:
    """Fixture M: one document, two VampNet mentions with two senses (spec §6.5)."""
    folder = root / "mentions"
    folder.mkdir(parents=True)
    text = "\n".join([f"# {MENTIONS['title']}", *MENTIONS["lines"]]) + "\n"
    document = text.encode("utf-8")
    first = line_spans(text)[0]
    ranges = lexical_ranges(text, {anchor_normalize("VampNet")})[anchor_normalize("VampNet")]
    words = [(s, e) for s, e in ranges if first[0] <= s and e <= first[1]]
    mentions = [f"mentions@{s}-{e}" for s, e in words]
    senses = ["Koopman operator method", "music generation model"]
    second = line_spans(text)[1]
    facts = {
        BUILDS: [{"method": "VampNet", "base_method": "DMD"}],
        "method_has_ancestor_method": [{"method": "VampNet", "ancestor": "DMD"}],
        "mention_denotes_sense": [{"mention": m, "sense": s} for m, s in zip(mentions, senses, strict=True)],
        "mention_has_surface_text": [{"mention": m, "surface": "VampNet"} for m in mentions],
    }
    population = population_bytes(facts)
    anchors = [{"fact_key": {"fact_type": "mention_has_surface_text", "roles": {"mention": m, "surface": "VampNet"}},
                "role": "surface", "span": {"start": s, "end": e},
                "occurrence": occurrence(text, "VampNet", (s, e)),
                "excerpt_sha256": _sha(text[s:e].encode("utf-8"))} for m, (s, e) in zip(mentions, words, strict=True)]
    for role in ("method", "base_method"):
        row = facts[BUILDS][0]
        anchors.append({"fact_key": {"fact_type": BUILDS, "roles": dict(row)}, "role": role,
                        "span": {"start": second[0], "end": second[1]},
                        "occurrence": occurrence(text, row[role], second),
                        "excerpt_sha256": _sha(text[second[0]:second[1]].encode("utf-8"))})
    (folder / "document.txt").write_bytes(document)
    (folder / "population.json").write_bytes(population)
    (folder / "population.json.anchors.json").write_bytes(_dump({
        "schema_version": 2, "population_sha256": _sha(population), "vocabulary_digest": vocabulary,
        "document_sha256": _sha(document), "anchors": anchors}))


def main(directory: str) -> None:
    root = Path(directory)
    vocabulary = vocabulary_digest(load_model(root / MODEL_FILE))
    for name in ("cases", "mentions"):
        if (root / name).exists():
            shutil.rmtree(root / name)
    entries = [write_case(root, case_id, case, vocabulary) for case_id, case in CASES.items()]
    write_mentions(root, vocabulary)
    (root / "cases.json").write_bytes(_dump({"schema": "li2-resolution-cases/1", "model": MODEL_FILE,
                                             "cases": entries,
                                             "mentions": {"directory": "mentions", "check_exit": 0}}))


if __name__ == "__main__":
    main(sys.argv[1])
