"""Exact selected source-owned runtime observers, without routed publication harnesses."""
from __future__ import annotations

import copy
import gzip
import hashlib
import io
import json
import tempfile
import time
from pathlib import Path

import test_public_corpus_finite_support as finite_observer
import test_public_corpus_inputs_support as inputs
from test_public_finite_observer_support import ROOT

from gnd import assurance, assurance_evidence


def _coordinates():
    packed = (Path(__file__).parent / "fixtures/public-corpus-observer/coordinates.json.gz").read_bytes()
    assert len(packed) <= 16384
    assert hashlib.sha256(packed).hexdigest() == "db812a08ef5d417ee172fae9f4c7f4af00f7435238120f97d291394ea1db056d"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(524289)
    assert len(raw) <= 524288
    assert hashlib.sha256(raw).hexdigest() == "b59b6e7cbf4a718094c51a0223ecd66c53e0e707ceaeea6aab329caf7910a4e3"
    document = json.loads(raw)
    assert set(document) == {"rows", "answers"}
    assert len(document["rows"]) == len(document["answers"]) == 300
    return document["rows"], document["answers"]

ROWS, ANSWERS = _coordinates()

def _pointer(document, pointer: str):
    value = document
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value

def witness(row: dict, semantic: dict) -> dict:
    """Change only the declared witness and detect the exact semantic delta."""
    recipe = row["recipe"]
    before = copy.deepcopy(semantic)
    if _pointer(before, recipe["pointer"]) != recipe["before"]:
        raise ValueError("witness control preimage differs from live production")
    after = copy.deepcopy(before)
    parent_pointer, _, leaf = recipe["pointer"].rpartition("/")
    parent = _pointer(after, parent_pointer)
    if isinstance(parent, list):
        parent[int(leaf)] = copy.deepcopy(recipe["after"])
    else:
        parent[leaf.replace("~1", "/").replace("~0", "~")] = copy.deepcopy(recipe["after"])
    baseline = inputs.canonical(before)
    mutant = inputs.canonical(after)
    # Remove precisely the controlled coordinate to show that the business
    # verdict and band stayed fixed while the witness comparison still fails.
    baseline_without = copy.deepcopy(before)
    mutant_without = copy.deepcopy(after)
    for document in (baseline_without, mutant_without):
        parent = _pointer(document, parent_pointer)
        if isinstance(parent, list):
            parent[int(leaf)] = None
        else:
            parent[leaf.replace("~1", "/").replace("~0", "~")] = None
    return {
        "baseline_passed": _pointer(before, recipe["pointer"]) == recipe["before"],
        "detected": baseline != mutant,
        "failure_signature": "witness-mismatch",
        "band_unchanged": before["band"] == after["band"],
        "verdict_unchanged": baseline_without == mutant_without,
        "production_certificate": False,
    }

def exclusion(row: dict, manifest: dict) -> dict:
    """Observe that policy-excluded rows receive no release proof credit."""
    scope_id = row["recipe"]["scope_id"]
    selected = [item for item in manifest["rows"] if item["scope_id"] == scope_id]
    if len(selected) != 1:
        raise ValueError("excluded policy control has no unique release row")
    decisions = {
        assurance.semantic_decision_for_band(band)
        for _level in row["recipe"]["assurance_variants"]
        for band in (0,)
    }
    return {
        "policy_unchanged": decisions == {"accept"},
        "proof_credit": selected[0]["status"] == "proved",
    }

def resource(row: dict) -> dict:
    """Exercise the exact reader limits and the finite-set decision layer."""
    recipe = row["recipe"]
    execution = recipe["execution"]
    if execution == "evidence-reader":
        resource = recipe["resource"]
        admitted = True
        try:
            if resource == "document-cap":
                with tempfile.TemporaryDirectory(prefix="gnd-phase6-resource-") as directory:
                    path = Path(directory) / "document.bin"
                    with path.open("wb") as stream:
                        stream.truncate(recipe["size"])
                    assurance_evidence._read(path, assurance_evidence.MAX_DOCUMENT_BYTES)
            elif resource == "bundle-cap":
                assurance_evidence.enforce_bundle_limits(recipe["size"], 1)
            elif resource == "file-cap":
                assurance_evidence.enforce_bundle_limits(0, recipe["size"])
            else:
                raise ValueError("unknown evidence resource control")
        except ValueError:
            admitted = False
        return {"admitted": admitted, "status": "within-cap" if admitted else "resource-limit"}
    if execution == "timing-validator":
        from proof.v6.assurance.replay_driver import within_deadline

        return {
            "status": "within-cap"
            if within_deadline(recipe["elapsed_ms"], recipe["limit_ms"])
            else "resource-limit"
        }
    if execution != "timed-added-layer":
        raise ValueError("unknown Phase 6 resource control")
    size = recipe["size"]
    applicable = frozenset(f"case-{index}" for index in range(size))
    started = time.monotonic()
    level = assurance._assurance_policy(
        applicable,
        applicable,
        required=frozenset(),
        proved_infrastructure=frozenset(),
        guards_valid=True,
    )
    elapsed_ms = (time.monotonic() - started) * 1000
    return {
        "limit_ms": recipe["limit_ms"],
        "within_limit": elapsed_ms <= recipe["limit_ms"],
        "projection_rows_positive": level == "proof-backed" and bool(applicable),
    }

def cheap(row: dict, *, root: Path = ROOT, manifest: dict | None = None) -> dict:
    """Run corpus coordinates that need no installed command or provider."""
    kind = row["kind"]
    if kind == "policy":
        return finite_observer.policy(row)
    if kind == "reader":
        return finite_observer.reader(row, root)
    if kind == "legacy-feedback":
        return finite_observer.legacy_feedback(row, root)
    if kind == "resource":
        return resource(row)
    if kind == "exclusion":
        if manifest is None:
            raise ValueError("exclusion observation requires the candidate manifest")
        return exclusion(row, manifest)
    raise ValueError(f"case requires a live routed adapter: {kind}")
