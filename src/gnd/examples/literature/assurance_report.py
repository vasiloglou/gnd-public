"""The staged assurance report over the literature corpus (phase LI1).

    python -m gnd.examples.literature.assurance_report CORPUS ANSWERS RUN [--out PATH]

CORPUS is the example root, the directory that holds ``corpus/corpus.json``.
ANSWERS is an answer key, with its ``gold/`` and ``render/`` folders beside it.
RUN is a ``literature-run/1`` directory. The report goes to stdout as one
canonical JSON line (and to PATH with ``--out``), and the process exits with
the report's exit code: 0 when every active stage passes, 1 when any fails,
3 for a refused input.

The formats are defined in this example's README, section "Formats". The
rules are in .gnd-planning/milestones/literature-identity/notes/phase-LI1-spec.md
(§6.3-§6.5) and its corpus-gate amendments A1-A5 (§13). The harness reads
gnd only through the CLI, over the four routes in ``ROUTES``. It never takes a
number from ``gnd measure --labels``.

``score`` is total. Every input it is given ends in a report, never an
exception.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from bisect import bisect_right
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

SCHEMA = "literature-assurance-report/1"
DOCUMENT_CAP = 4 * 1024 * 1024
COMPOSITION_RECORD_CAP = 16 * 1024 * 1024
ROUTE_CAP = 64 * 1024 * 1024
MAX_DEPTH = 64
MAX_DIGITS = 128
WORKERS = 8
STAGES = ("model-population-validity", "source-binding", "semantic-support", "identity-decisions",
          "derivation", "coverage", "freshness")
DORMANT = {"coverage": "literature-depth LD3"}
UNITS = {
    "model-population-validity": "run source population",
    "source-binding": "anchored fact role",
    "semantic-support": "assertion with a support label",
    "identity-decisions": "cross-source key pair with an identity label",
    "derivation": "derived row, claimed or recomputed",
    "coverage": "inspected document section",
    "freshness": "evidence binding",
}
# Floors as exact fractions. A key ending in _max is an upper bound on its metric.
FLOORS = {
    "model-population-validity": {"agreement": (1, 1)},
    "source-binding": {"precision": (1, 1), "recall": (1, 1)},
    "semantic-support": {"precision": (9, 10), "recall": (9, 10), "abstention_max": (1, 5)},
    "identity-decisions": {"precision": (1, 1), "recall": (9, 10), "abstention_max": (1, 5)},
    "derivation": {"precision": (1, 1), "recall": (1, 1), "abstention_max": (0, 1)},
    "freshness": {"precision": (1, 1), "recall": (1, 1)},
}
# The only argv the harness ever builds (spec §6.4). Never --allow-vacuous or
# --baseline, and never --composition with --anchors, --document or --populations.
ROUTES = {
    "R1": ("check", "{model}", "{population}", "--format", "json"),
    "R2": ("check", "{model}", "{population}", "--anchors", "{anchors}", "--document", "{document}",
           "--format", "json"),
    "R3": ("fidelity", "{model}", "--cases", "{cases}", "--artifacts", "{artifacts}", "--format", "json"),
    "R4": ("check", "{model}", "{composed}", "--composition", "{record}", "--sources", "{sources}",
           "--format", "json"),
}
SUPPORT = {"supported", "stretched", "contradicted", "insufficient-evidence"}
LABELS_NOTE = "Labels are not independent expert ground truth unless the answer key says otherwise."
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


class Refusal(Exception):
    """A harness refusal: exit 3 with a value-free reason code."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


# --- Reading -------------------------------------------------------------------------


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_capped(path: Path, cap: int = DOCUMENT_CAP) -> bytes:
    """Read at most cap+1 bytes. The cap is applied to the read, not after it."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read(cap + 1)
    except OSError as error:
        raise Refusal("input:unreadable") from error
    if len(raw) > cap:
        raise Refusal("input:too-large")
    return raw


def _no_constant(name: str):
    raise ValueError("non-JSON constant")


def _bounded_int(text: str) -> int:
    if len(text.lstrip("-")) > MAX_DIGITS:
        raise ValueError("integer literal too long")
    return int(text)


def _depth_ok(value: Any) -> bool:
    stack = [(value, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > MAX_DEPTH:
            return False
        if isinstance(node, dict):
            stack.extend((child, depth + 1) for child in node.values())
        elif isinstance(node, list):
            stack.extend((child, depth + 1) for child in node)
    return True


def parse_json(raw: bytes) -> Any:
    """Strict JSON: UTF-8, no NaN or infinities, bounded integer digits, depth at most 64."""
    try:
        value = json.loads(raw.decode("utf-8"), parse_constant=_no_constant, parse_int=_bounded_int)
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        raise Refusal("input:not-json") from error
    if not _depth_ok(value):
        raise Refusal("input:not-json")
    return value


def read_json(path: Path, cap: int = DOCUMENT_CAP) -> tuple[Any, bytes]:
    raw = read_capped(path, cap)
    return parse_json(raw), raw


def _try_json(path: Path) -> Any:
    """Best-effort read of a run file. A file that cannot be read is simply absent."""
    try:
        return read_json(path)[0]
    except Refusal:
        return None


# --- Shapes (validation step 2) --------------------------------------------------------


def _need(condition: bool) -> None:
    if not condition:
        raise Refusal("input:schema")


def _is_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _span_ok(span: Any) -> bool:
    return (isinstance(span, dict) and set(span) == {"start", "end"}
            and all(type(span[k]) is int for k in span) and 0 <= span["start"] <= span["end"])


def _relative_ok(path: Any) -> bool:
    return _is_str(path) and not path.startswith(("/", "\\")) and ".." not in Path(path).parts


def check_corpus_shape(corpus: Any) -> None:
    _need(isinstance(corpus, dict) and corpus.get("schema") == "literature-corpus/1")
    _need(_relative_ok(corpus.get("model")) and _is_str(corpus.get("model_sha256")))
    artifacts = corpus.get("artifacts")
    _need(isinstance(artifacts, dict) and _relative_ok(artifacts.get("path"))
          and _is_str(artifacts.get("applicable_sha256")) and _is_str(artifacts.get("projection_sha256")))
    documents, passages = corpus.get("documents"), corpus.get("passages")
    _need(isinstance(documents, list) and isinstance(passages, list))
    for document in documents:
        _need(isinstance(document, dict) and _SAFE_ID.fullmatch(str(document.get("id"))) is not None)
        _need(_relative_ok(document.get("path")) and _is_str(document.get("sha256")))
        _need(_is_str(document.get("domain")) and document.get("split") in {"dev", "heldout"})
    ids = [d["id"] for d in documents]
    _need(len(ids) == len(set(ids)))
    for passage in passages:
        _need(isinstance(passage, dict) and _is_str(passage.get("id")) and passage.get("document") in ids
              and _span_ok(passage.get("span")))


def _fact_ok(fact: Any) -> bool:
    return isinstance(fact, dict) and _is_str(fact.get("fact_type")) and isinstance(fact.get("roles"), dict)


def _identity_key_ok(key: Any) -> bool:
    if not isinstance(key, dict) or set(key) != {"source", "object_type", "value"}:
        return False
    value = key["value"]
    return (_is_str(key["source"]) and _is_str(key["object_type"])
            and (isinstance(value, (str, bool, int)) or isinstance(value, float) and math.isfinite(value)))


def check_key_shape(key: Any) -> None:
    _need(isinstance(key, dict) and key.get("schema") == "literature-answer-key/1")
    _need(_is_str(key.get("corpus_sha256")) and isinstance(key.get("labeller"), dict))
    for group in ("assertions", "anchored_facts", "populations", "chains", "reuse_cases",
                  "identity_pairs", "name_pairs"):
        _need(isinstance(key.get(group), list))
    for item in key["assertions"]:
        _need(isinstance(item, dict) and _is_str(item.get("id")) and _is_str(item.get("passage"))
              and item.get("support") in SUPPORT and _fact_ok(item.get("fact")))
    for item in key["anchored_facts"]:
        _need(isinstance(item, dict) and _is_str(item.get("id")) and _is_str(item.get("source"))
              and _fact_ok(item.get("fact")) and _is_str(item.get("role")) and _span_ok(item.get("span")))
    for item in key["populations"]:
        _need(isinstance(item, dict) and _is_str(item.get("source")) and type(item.get("expected_check_exit")) is int)

    for item in key["identity_pairs"]:
        _need(isinstance(item, dict) and _is_str(item.get("id")) and item.get("label") in ("same", "different")
              and _identity_key_ok(item.get("left")) and _identity_key_ok(item.get("right")))


def check_run_shape(run: Any) -> None:
    _need(isinstance(run, dict) and run.get("schema") == "literature-run/1" and _is_str(run.get("corpus_sha256")))
    sources, abstentions = run.get("sources"), run.get("abstentions", [])
    _need(isinstance(sources, list) and isinstance(abstentions, list))
    _need(all(isinstance(s, str) and _SAFE_ID.fullmatch(s) for s in sources) and len(sources) == len(set(sources)))
    _need(all(_is_str(a) for a in abstentions))


# --- Passages and anchors -------------------------------------------------------------


def passage_index(passages: list[dict]) -> dict[str, tuple[list[int], list[dict]]]:
    """Per document, the passages sorted by start, for containment lookups."""
    grouped: dict[str, list[dict]] = {}
    for passage in passages:
        grouped.setdefault(passage["document"], []).append(passage)
    return {doc: ([p["span"]["start"] for p in rows], rows)
            for doc, rows in ((d, sorted(r, key=lambda p: p["span"]["start"])) for d, r in grouped.items())}


def anchors_in_passages(index: dict, anchors: list[dict]) -> list[str | None]:
    """For each anchor ({document, span}), the id of the passage that contains it, or None.

    Linear in anchors times log passages; passages in one document never overlap.
    """
    found = []
    for anchor in anchors:
        starts, rows = index.get(anchor["document"], ([], []))
        position = bisect_right(starts, anchor["span"]["start"]) - 1
        hit = None
        if position >= 0:
            span = rows[position]["span"]
            if span["start"] <= anchor["span"]["start"] and anchor["span"]["end"] <= span["end"]:
                hit = rows[position]["id"]
        found.append(hit)
    return found


# --- Status: the one function for every stage ------------------------------------------


def failed_floors(metrics: dict, floors: dict) -> list[str]:
    failed = []
    for name, (num, den) in floors.items():
        metric = name.removesuffix("_max")
        have, total = metrics.get(metric, (0, 0))
        too_high = name.endswith("_max") and have * den > num * total
        too_low = not name.endswith("_max") and have * den < num * total
        if total == 0 or too_high or too_low:
            failed.append(metric)
    return failed


def stage_status(*, active: bool, route_present: bool, metrics: dict, floors: dict, refused: int = 0) -> str:
    """Spec §6.5 status rules, in order: dormant, route missing, floors and refusals, pass."""
    if not active or not route_present:
        return "not-measured"
    if refused or failed_floors(metrics, floors):
        return "fail"
    return "pass"


def _metric(pair: tuple[int, int]) -> dict:
    num, den = pair
    return {"numerator": num, "denominator": den, "rate": (num / den) if den else None}


# --- Routes ----------------------------------------------------------------------------


def _argv(route: str, **paths: str) -> list[str]:
    return [part.format(**paths) for part in ROUTES[route]]


def run_route(gnd: tuple[str, ...], route: str, paths: dict, shown: dict) -> dict:
    """Run one route. Returns its exit, its parsed payload (or None) and argv for display."""
    display = _argv(route, **shown)
    try:
        done = subprocess.run([*gnd, *_argv(route, **paths)], capture_output=True, check=False, timeout=600)
    except (OSError, subprocess.SubprocessError):
        return {"argv": display, "exit": None, "payload": None}
    payload = None
    if len(done.stdout) <= ROUTE_CAP:
        try:
            payload = parse_json(done.stdout)
        except Refusal:
            payload = None
    return {"argv": display, "exit": done.returncode, "payload": payload if isinstance(payload, dict) else None}


def _public(result: dict) -> dict:
    return {"argv": result["argv"], "exit": result["exit"]}


def _unreported(result: dict | None) -> bool:
    """The route ran but produced no report this harness can read (review finding R2)."""
    return result is not None and (result["exit"] is None or result["payload"] is None)


def _refused(result: dict | None) -> bool:
    return result is None or result["exit"] not in (0, 1, 2, 4) or result["payload"] is None


def _error_message(result: dict | None) -> str:
    payload = (result or {}).get("payload") or {}
    error = payload.get("error") if isinstance(payload, dict) else None
    return str(error.get("message", "")) if isinstance(error, dict) else ""


# --- Scoring ---------------------------------------------------------------------------


def _key(fact: dict, role: str | None = None) -> str:
    return json.dumps([fact["fact_type"], fact["roles"], role], sort_keys=True, ensure_ascii=False)


class Inputs:
    """Everything validated in steps 1-4, with the run's files located."""

    def __init__(self, corpus_root: Path, answers: Path, run_dir: Path):
        self.root, self.answers_dir, self.run_dir = corpus_root, answers.parent, run_dir
        corpus_path = corpus_root / "corpus" / "corpus.json"
        # Step 1: read every input document, in order.
        self.corpus, self.corpus_raw = read_json(corpus_path)
        self.key, self.key_raw = read_json(answers)
        self.run, self.run_raw = read_json(run_dir / "run.json")
        # Step 2: shapes. A field of the wrong type (an unhashable split, say) is
        # a schema refusal too, never an internal one (review finding R3).
        try:
            check_corpus_shape(self.corpus)
            check_key_shape(self.key)
            check_run_shape(self.run)
        except (TypeError, KeyError, AttributeError) as error:
            raise Refusal("input:schema") from error
        # Step 3: digests.
        corpus_sha = _sha(self.corpus_raw)
        if self.key["corpus_sha256"] != corpus_sha:
            raise Refusal("corpus:digest-mismatch")
        self.model_path = corpus_root / self.corpus["model"]
        if _sha(read_capped(self.model_path)) != self.corpus["model_sha256"]:
            raise Refusal("corpus:digest-mismatch")
        self.documents = {d["id"]: d for d in self.corpus["documents"]}
        self.document_bytes = {}
        for doc_id, document in self.documents.items():
            raw = read_capped(corpus_root / document["path"])
            if _sha(raw) != document["sha256"]:
                raise Refusal("corpus:digest-mismatch")
            self.document_bytes[doc_id] = raw
        if self.run["corpus_sha256"] != corpus_sha:
            raise Refusal("run:corpus-mismatch")
        # Step 4: run consistency.
        self.sources = list(self.run["sources"])
        self.abstentions = set(self.run.get("abstentions", []))
        if any(s not in self.documents for s in self.sources):
            raise Refusal("run:unknown-source")
        for source in self.sources:
            path = self.source_dir(source) / "document.txt"
            try:
                same = path.is_file() and read_capped(path) == self.document_bytes[source]
            except Refusal:
                same = False
            if not same:
                raise Refusal("run:document-mismatch")
        self.passages = {p["id"]: p for p in self.corpus["passages"]}
        if any(a not in self.passages for a in self.abstentions):
            raise Refusal("run:unknown-passage")
        self.anchors = {s: self._anchors(s) for s in self.sources}
        abstained = [self.passages[a] for a in sorted(self.abstentions)]
        index = passage_index(abstained)
        located = [{"document": s, "span": a["span"]}
                   for s, rows in self.anchors.items() for a in (rows or []) if _span_ok(a.get("span"))]
        if any(hit is not None for hit in anchors_in_passages(index, located)):
            raise Refusal("run:abstained-passage-asserted")

    def source_dir(self, source: str) -> Path:
        return self.run_dir / "composition" / source

    def _anchors(self, source: str) -> list[dict] | None:
        sidecar = _try_json(self.source_dir(source) / "population.json.anchors.json")
        if not isinstance(sidecar, dict) or not isinstance(sidecar.get("anchors"), list):
            return None
        return [a for a in sidecar["anchors"] if isinstance(a, dict)]


def _assemble_cases(inputs: Inputs, sources: list[str], folder: Path) -> list[str]:
    """Write gnd fidelity cases for the sources that have every piece; return those sources."""
    gold, render = inputs.answers_dir / "gold", inputs.answers_dir / "render"
    made = []
    for source in sources:
        src = inputs.source_dir(source)
        pieces = {"document.md": inputs.root / inputs.documents[source]["path"],
                  "source.population.json": gold / f"{source}.population.json",
                  "document.manifest.json": render / f"{source}.manifest.json",
                  "extracted.population.json": src / "population.json",
                  "extracted.population.extraction.json": src / "population.json.extraction.json"}
        if not all(path.is_file() for path in pieces.values()):
            continue
        case = folder / source
        case.mkdir(parents=True)
        for name, path in pieces.items():
            shutil.copyfile(path, case / name)
        made.append(source)
    return made


def _fidelity_counts(payload: dict | None, fact_types: set[str]) -> dict | None:
    if not isinstance(payload, dict) or not isinstance(payload.get("per_fact_type"), list):
        return None
    totals = {"tp": 0, "extracted_total": 0, "missed": 0, "unmatched": 0, "unresolved": 0}
    for row in payload["per_fact_type"]:
        if isinstance(row, dict) and row.get("id") in fact_types and isinstance(row.get("matched"), dict):
            for name in totals:
                value = row["matched"].get(name, 0)
                totals[name] += value if type(value) is int else 0
    failed = set()
    cases = payload.get("cases") or {}
    for reason in cases.get("reasons") or [] if isinstance(cases, dict) else []:
        if isinstance(reason, dict) and reason.get("state") == "failed":
            failed.add(reason.get("case"))
    totals["failed_cases"] = failed
    return totals


def _stage(name: str, *, metrics: dict, floors: dict, route_present: bool, refused: int = 0,
           route_refused: bool = False, sample_size: int = 0, disagreements: dict | None = None,
           routes: list | None = None, unresolved: int = 0, label_disagreements: int = 0,
           extra: dict | None = None) -> dict:
    if route_refused:
        status, failed = "fail", ["route-refused"]
    else:
        status = stage_status(active=True, route_present=route_present, metrics=metrics, floors=floors,
                              refused=refused)
        failed = (failed_floors(metrics, floors) + (["refused"] if refused else [])) if status == "fail" else []
    stage = {"stage": name, "active": True, "owner": None if route_present else "run", "status": status,
             "failed_floors": failed, "unit": UNITS[name], "sample_size": sample_size, "exclusions": [],
             "unresolved": unresolved, "disagreements": disagreements or {"count": 0, "units": []},
             "label_disagreements": label_disagreements, "refused_units": refused,
             "floor": {k: list(v) for k, v in floors.items()}, "routes": routes or []}
    if route_refused:
        stage["route_refused"] = True
    if route_present and not route_refused:
        stage.update({m: _metric(pair) for m, pair in metrics.items()})
    stage.update(extra or {})
    return stage


def _validity(inputs: Inputs, r1: dict) -> dict:
    agree, units, refused = 0, [], 0
    for item in inputs.key["populations"]:
        result = r1.get(item["source"])
        if _unreported(result):
            refused += 1
            units.append(item["source"])
        elif result is not None and result["exit"] == item["expected_check_exit"]:
            agree += 1
        else:
            units.append(item["source"])
    return _stage("model-population-validity", metrics={"agreement": (agree, len(inputs.key["populations"]))},
                  floors=FLOORS["model-population-validity"], route_present=bool(r1), refused=refused,
                  sample_size=len(inputs.key["populations"]),
                  disagreements={"count": len(units), "units": units},
                  routes=[_public(r) for r in r1.values()])


def _source_binding(inputs: Inputs, r2: dict) -> dict:
    gold = {(a["source"], _key(a["fact"], a["role"])): a for a in inputs.key["anchored_facts"]}
    run: dict[tuple[str, str], list[dict]] = {}
    refused_sources = {s for s, result in r2.items() if _refused(result)}
    for source, anchors in inputs.anchors.items():
        for anchor in anchors or []:
            fact = anchor.get("fact_key")
            if isinstance(fact, dict) and _fact_ok(fact) and isinstance(anchor.get("role"), str) and _span_ok(anchor.get("span")):
                run.setdefault((source, _key(fact, anchor["role"])), []).append(anchor["span"])
    run_positive = {k for k in run if k[0] in r2 and k[0] not in refused_sources}
    both = {k for k in run_positive if k in gold and gold[k]["span"] in run[k]}
    missing = sorted(gold[k]["id"] for k in gold if k not in both)
    refused = sum(1 for k in gold if k[0] in refused_sources)
    return _stage("source-binding",
                  metrics={"precision": (len(both), len(run_positive)), "recall": (len(both), len(gold))},
                  floors=FLOORS["source-binding"], route_present=bool(r2), refused=refused,
                  sample_size=len(gold), disagreements={"count": len(missing), "units": missing},
                  routes=[_public(r) for r in r2.values()])


def _semantic(inputs: Inputs, r3: dict | None, per_domain: list) -> dict:
    assertions = inputs.key["assertions"]
    fact_types = {a["fact"]["fact_type"] for a in assertions}
    supported = sum(1 for a in assertions if a["support"] == "supported")
    abstained = sorted(a["passage"] for a in assertions if a["passage"] in inputs.abstentions)
    label_disagreements = sum(1 for a in assertions if a.get("label_disagreement") is not None)
    common = {"sample_size": len(assertions), "label_disagreements": label_disagreements,
              "routes": [_public(r3)] if r3 else []}
    if r3 is None:
        return _stage("semantic-support", metrics={}, floors=FLOORS["semantic-support"], route_present=False, **common)
    counts = None if _refused(r3) or r3["exit"] != 0 else _fidelity_counts(r3["payload"], fact_types)
    if counts is None:
        return _stage("semantic-support", metrics={}, floors=FLOORS["semantic-support"], route_present=True,
                      route_refused=True, refused=len(assertions), **common)
    refused_docs = set(counts["failed_cases"])
    refused = sum(1 for a in assertions if inputs.passages.get(a["passage"], {}).get("document") in refused_docs)
    metrics = {"precision": (counts["tp"], counts["extracted_total"]),
               "recall": (counts["tp"], supported),
               "abstention": (len(abstained), len(assertions))}
    return _stage("semantic-support", metrics=metrics, floors=FLOORS["semantic-support"], route_present=True,
                  refused=refused, unresolved=counts["unresolved"],
                  disagreements={"count": (supported - counts["tp"]) + counts["unmatched"], "units": abstained,
                                 "note": "gnd fidelity reports counts, not which fact matched; units lists abstained passages only"},
                  extra={"per_domain": per_domain, "aggregate": "harness micro-total over the assertion fact types"},
                  **common)


def _identity_key(key: dict) -> tuple[str, str, str, str]:
    value = key["value"]
    return key["source"], key["object_type"], type(value).__name__, repr(value)


def _identity_decisions(inputs: Inputs, r4: dict | None) -> dict:
    name = "identity-decisions"
    pairs = inputs.key["identity_pairs"]
    common = {"floors": FLOORS[name], "sample_size": len(pairs), "routes": [_public(r4)] if r4 else []}
    if r4 is None or _refused(r4):
        return _stage(name, metrics={}, route_present=r4 is not None, route_refused=r4 is not None, **common)
    try:
        composition = inputs.run_dir / "composition"
        record, record_raw = read_json(inputs.run_dir / "composed" / "record.json", COMPOSITION_RECORD_CAP)
        manifest, manifest_raw = read_json(composition / "manifest.json")
        verified = r4["payload"]["composition"]["record_sha256"]
        if (_sha(record_raw) != verified or _sha(manifest_raw) != record["manifest_sha256"]):
            raise Refusal("run:composition-changed")
        binding = manifest.get("resolution")
        if binding is None:
            return _stage(name, metrics={}, route_present=False, **common)
        if not _relative_ok(binding["path"]) or "/" in binding["path"]:
            raise Refusal("run:invalid-resolution-path")
        resolution, raw = read_json(composition / binding["path"])
        if _sha(raw) != binding["sha256"] or _sha(raw) != record["resolution_sha256"]:
            raise Refusal("run:resolution-changed")
    except (Refusal, KeyError, TypeError):
        return _stage(name, metrics={}, route_present=True, route_refused=True, **common)

    parent = {}
    size = {}
    unresolved = set()

    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    for decision in resolution["decisions"]:
        left, right = map(_identity_key, decision["keys"])
        if decision["decision"] == "unresolved":
            unresolved.add(frozenset((left, right)))
        if decision["decision"] == "same":
            for key in (left, right):
                parent.setdefault(key, key)
                size.setdefault(key, 1)
            left, right = root(left), root(right)
            if left != right:
                if size[left] < size[right]:
                    left, right = right, left
                parent[right] = left
                size[left] += size[right]
    actual = expected = matched = abstentions = 0
    disagreements = []
    for pair in pairs:
        left, right = _identity_key(pair["left"]), _identity_key(pair["right"])
        positive = left in parent and right in parent and root(left) == root(right)
        gold = pair["label"] == "same"
        actual += positive
        expected += gold
        matched += positive and gold
        abstentions += frozenset((left, right)) in unresolved
        if positive != gold:
            disagreements.append(pair["id"])
    metrics = {"precision": (matched, actual), "recall": (matched, expected),
               "abstention": (abstentions, len(pairs))}
    return _stage(name, metrics=metrics, route_present=True, unresolved=abstentions,
                  disagreements={"count": len(disagreements), "units": disagreements}, **common)


def _derivation(inputs: Inputs, r4: dict | None) -> dict:
    if r4 is None:
        return _stage("derivation", metrics={}, floors=FLOORS["derivation"], route_present=False)
    if _refused(r4):
        return _stage("derivation", metrics={}, floors=FLOORS["derivation"], route_present=True,
                      route_refused=True, routes=[_public(r4)])
    payload = r4["payload"]
    composed = _try_json(inputs.run_dir / "composed" / "population.json") or {}
    facts = composed.get("facts") if isinstance(composed, dict) else None
    facts = facts if isinstance(facts, dict) else {}
    derivations = [d for d in payload.get("derivations") or [] if isinstance(d, dict)]
    claimed = unsound = missing = abstaining = 0
    for derivation in derivations:
        fact_type = str(derivation.get("derivation_ref", "")).removeprefix("derivation:")
        rows = facts.get(fact_type)
        claimed += len(rows) if isinstance(rows, list) else 0
        if derivation.get("verdict") in {"unchecked", "vacuous"}:
            abstaining += 1
        for finding in derivation.get("findings") or []:
            kind = finding.get("kind") if isinstance(finding, dict) else None
            unsound += kind == "derived-extension-unsound"
            missing += kind == "derived-extension-incomplete"
    both = claimed - unsound
    metrics = {"precision": (both, claimed), "recall": (both, both + missing),
               "abstention": (abstaining, len(derivations))}
    return _stage("derivation", metrics=metrics, floors=FLOORS["derivation"], route_present=True,
                  sample_size=claimed + missing,
                  disagreements={"count": unsound + missing, "units": []}, routes=[_public(r4)])


def _freshness(inputs: Inputs, r2: dict, r3: dict | None, r4: dict | None) -> dict:
    model_sha = inputs.corpus["model_sha256"]
    projection = inputs.corpus["artifacts"]["projection_sha256"]
    expected = [item["source"] for item in inputs.key["populations"]]
    units = [(s, kind) for s in expected for kind in ("anchors", "extraction")] + [("run", "composition")]
    present, fresh, stale, refused = 0, 0, [], 0
    for source, kind in units:
        if kind == "composition":
            record = _try_json(inputs.run_dir / "composed" / "record.json")
            if record is None:
                stale.append("composition:absent")
                continue
            present += 1
            if _unreported(r4):
                refused += 1
                stale.append("composition:refused")
                continue
            if not _record_covers_run(inputs, record):
                stale.append("composition:sources-differ")
                continue
            ok = isinstance(record, dict) and _record_fresh(inputs, record) and not (
                r4 is not None and _refused(r4) and "digest" in _error_message(r4))
        else:
            folder = inputs.source_dir(source)
            sidecar = _try_json(folder / f"population.json.{kind}.json")
            if sidecar is None:
                stale.append(f"{source}:{kind}:absent")
                continue
            present += 1
            # The anchor sidecar binds a vocabulary digest only R2 can check, so an
            # unreported R2 refuses it. The extraction sidecar's digests are all raw
            # bytes this harness checks itself.
            if kind == "anchors" and _unreported(r2.get(source)):
                refused += 1
                stale.append(f"{source}:{kind}:refused")
                continue
            population = _file_sha(folder / "population.json")
            document = _file_sha(folder / "document.txt")
            ok = isinstance(sidecar, dict) and sidecar.get("population_sha256") == population \
                and sidecar.get("document_sha256") == document
            if kind == "extraction":
                ok = ok and sidecar.get("model_sha256") == model_sha and sidecar.get("projection_sha256") == projection
            else:
                ok = ok and "digest differs" not in _error_message(r2.get(source))
        if ok:
            fresh += 1
        else:
            stale.append(f"{source}:{kind}")
    routes = [_public(r) for r in r2.values()] + ([_public(r3)] if r3 else []) + ([_public(r4)] if r4 else [])
    return _stage("freshness", metrics={"precision": (fresh, present), "recall": (fresh, len(units))},
                  floors=FLOORS["freshness"], route_present=present > 0, refused=refused, sample_size=len(units),
                  disagreements={"count": len(stale), "units": stale}, routes=routes)


def _file_sha(path: Path) -> str | None:
    try:
        return _sha(read_capped(path, ROUTE_CAP))
    except Refusal:
        return None


def _record_covers_run(inputs: Inputs, record: Any) -> bool:
    """The composition record names exactly the run's sources (review finding R1)."""
    entries = record.get("sources") if isinstance(record, dict) else None
    if not isinstance(entries, list):
        return False
    ids = [e.get("id") for e in entries if isinstance(e, dict)]
    return len(ids) == len(entries) and sorted(map(str, ids)) == sorted(inputs.sources)


def _record_fresh(inputs: Inputs, record: dict) -> bool:
    if record.get("population_sha256") != _file_sha(inputs.run_dir / "composed" / "population.json"):
        return False
    for entry in record.get("sources") or []:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or entry["id"] not in inputs.sources:
            return False
        folder = inputs.source_dir(entry["id"])
        if (entry.get("population_sha256") != _file_sha(folder / "population.json")
                or entry.get("document_sha256") != _file_sha(folder / "document.txt")
                or entry.get("sidecar_sha256") != _file_sha(folder / "population.json.anchors.json")):
            return False
    return True


def _dormant(name: str) -> dict:
    return {"stage": name, "active": False, "owner": DORMANT[name], "status": "not-measured",
            "failed_floors": [], "unit": UNITS[name], "sample_size": 0}


def _run_sha(run_dir: Path) -> str:
    listing = []
    for path in sorted(p for p in run_dir.rglob("*") if p.is_file()):
        listing.append([path.relative_to(run_dir).as_posix(), _file_sha(path)])
    return _sha(json.dumps(listing, separators=(",", ":")).encode("utf-8"))


def _gnd_version(results: dict) -> str:
    """The gnd version as the fidelity route reports it (review finding R5: CLI only)."""
    for result in results.values():
        payload = result.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("gnd_version"), str):
            return payload["gnd_version"]
    return "unknown"


def refused_report(reason: str) -> dict:
    return {"schema": SCHEMA, "exit_code": 3, "reason": reason, "stages": [], "failed_stages": [],
            "not_measured": []}


def _routes(inputs: Inputs, gnd: tuple[str, ...], work: Path):
    model, artifacts = str(inputs.model_path), str(inputs.root / inputs.corpus["artifacts"]["path"])
    shown_model = inputs.corpus["model"]
    jobs = {}
    for source in inputs.sources:
        folder = inputs.source_dir(source)
        population = folder / "population.json"
        shown = f"run/composition/{source}"
        if population.is_file():
            jobs[("R1", source)] = ({"model": model, "population": str(population)},
                                    {"model": shown_model, "population": f"{shown}/population.json"})
        anchors = folder / "population.json.anchors.json"
        if population.is_file() and anchors.is_file():
            jobs[("R2", source)] = ({"model": model, "population": str(population), "anchors": str(anchors),
                                     "document": str(folder / "document.txt")},
                                    {"model": shown_model, "population": f"{shown}/population.json",
                                     "anchors": f"{shown}/population.json.anchors.json",
                                     "document": f"{shown}/document.txt"})
    cases = _assemble_cases(inputs, inputs.sources, work / "cases")
    if cases:
        jobs[("R3", None)] = ({"model": model, "cases": str(work / "cases"), "artifacts": artifacts},
                              {"model": shown_model, "cases": "fidelity-cases", "artifacts": inputs.corpus["artifacts"]["path"]})
        domains = sorted({inputs.documents[s]["domain"] for s in cases})
        for domain in domains:
            members = [s for s in cases if inputs.documents[s]["domain"] == domain]
            folder = work / "domains" / domain
            _assemble_cases(inputs, members, folder)
            jobs[("R3", domain)] = ({"model": model, "cases": str(folder), "artifacts": artifacts},
                                    {"model": shown_model, "cases": f"fidelity-cases/{domain}",
                                     "artifacts": inputs.corpus["artifacts"]["path"]})
    composed = inputs.run_dir / "composed"
    if (composed / "population.json").is_file() and (composed / "record.json").is_file():
        jobs[("R4", None)] = ({"model": model, "composed": str(composed / "population.json"),
                               "record": str(composed / "record.json"),
                               "sources": str(inputs.run_dir / "composition")},
                              {"model": shown_model, "composed": "run/composed/population.json",
                               "record": "run/composed/record.json", "sources": "run/composition"})
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {job: pool.submit(run_route, gnd, job[0], paths, shown) for job, (paths, shown) in jobs.items()}
        return {job: future.result() for job, future in futures.items()}


def _per_domain(inputs: Inputs, results: dict) -> list[dict]:
    assertions = inputs.key["assertions"]
    fact_types = {a["fact"]["fact_type"] for a in assertions}
    rows = []
    for (route, domain), result in sorted(results.items(), key=lambda item: str(item[0])):
        if route != "R3" or domain is None:
            continue
        mine = [a for a in assertions
                if inputs.documents.get(inputs.passages.get(a["passage"], {}).get("document"), {}).get("domain") == domain]
        counts = None if _refused(result) or result["exit"] != 0 else _fidelity_counts(result["payload"], fact_types)
        supported = sum(1 for a in mine if a["support"] == "supported")
        abstained = sum(1 for a in mine if a["passage"] in inputs.abstentions)
        row = {"domain": domain, "sample_size": len(mine), "abstention": _metric((abstained, len(mine)))}
        if counts is not None:
            row.update(precision=_metric((counts["tp"], counts["extracted_total"])),
                       recall=_metric((counts["tp"], supported)))
        rows.append(row)
    return rows


def score(corpus_root: Path, answers: Path, run_dir: Path, *,
          gnd: tuple[str, ...] = (sys.executable, "-m", "gnd")) -> dict:
    """Score RUN against ANSWERS over the corpus at CORPUS_ROOT. Never raises for its inputs."""
    try:
        # gnd's safe readers refuse a path that passes through a symlink (macOS /var is
        # one), so every path handed to a route is resolved first (LI1 finding).
        corpus_root, answers, run_dir = (Path(p).resolve() for p in (corpus_root, answers, run_dir))
        inputs = Inputs(corpus_root, answers, run_dir)
    except Refusal as refusal:
        return refused_report(refusal.reason)
    except Exception:  # noqa: BLE001 -- totality: an unforeseen input still ends in a report
        return refused_report("internal")
    try:
        with tempfile.TemporaryDirectory(prefix="literature-assurance-") as work:
            results = _routes(inputs, tuple(gnd), Path(work).resolve())
        r1 = {s: r for (route, s), r in results.items() if route == "R1"}
        r2 = {s: r for (route, s), r in results.items() if route == "R2"}
        r3, r4 = results.get(("R3", None)), results.get(("R4", None))
        stages = {
            "model-population-validity": _validity(inputs, r1),
            "source-binding": _source_binding(inputs, r2),
            "semantic-support": _semantic(inputs, r3, _per_domain(inputs, results)),
            "identity-decisions": _identity_decisions(inputs, r4),
            "derivation": _derivation(inputs, r4),
            "coverage": _dormant("coverage"),
            "freshness": _freshness(inputs, r2, r3, r4),
        }
    except Exception:  # noqa: BLE001 -- totality
        return refused_report("internal")
    ordered = [stages[name] for name in STAGES]
    failed = [s["stage"] for s in ordered if s["active"] and s["status"] != "pass"]
    labeller = inputs.key["labeller"]
    key = inputs.key
    return {
        "schema": SCHEMA,
        "exit_code": 1 if failed else 0,
        "reason": None,
        "inputs": {"corpus_sha256": _sha(inputs.corpus_raw), "answers_sha256": _sha(inputs.key_raw),
                   "run_sha256": _run_sha(run_dir), "gnd_version": _gnd_version(results),
                   "harness_sha256": _sha(Path(__file__).read_bytes())},
        "labels": {"kind": labeller.get("kind"), "independent": labeller.get("independent") is True,
                   "note": labeller.get("note") or LABELS_NOTE},
        "stages": ordered,
        "failed_stages": failed,
        "not_measured": [{"stage": s["stage"], "owner": s["owner"]} for s in ordered if s["status"] == "not-measured"],
        "unscored_labels": [{"kind": "chains", "count": len(key["chains"]), "owner": "LI5"},
                            {"kind": "reuse_cases", "count": len(key["reuse_cases"]), "owner": "LI2, LI3"},
                            {"kind": "name_pairs", "count": len(key["name_pairs"]), "owner": "LI3"}]
                           + ([{"kind": "identity_pairs", "count": len(key["identity_pairs"]), "owner": "run"}]
                              if "precision" not in stages["identity-decisions"] else []),
    }


def main(argv: list[str] | None = None) -> int:
    args = None
    try:
        parser = argparse.ArgumentParser(description="Score a literature run against an answer key.")
        parser.add_argument("corpus")
        parser.add_argument("answers")
        parser.add_argument("run")
        parser.add_argument("--out")
        args = parser.parse_args(argv)
        report = score(Path(args.corpus), Path(args.answers), Path(args.run))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 -- totality at the process boundary
        report = refused_report("internal")
    if args is not None and args.out:
        try:
            Path(args.out).write_text(json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
        except OSError:
            report = refused_report("output:unwritable")  # review finding R4
    print(json.dumps(report, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
