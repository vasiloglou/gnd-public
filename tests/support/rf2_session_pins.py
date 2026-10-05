"""Owner-approved RF2 successors; original RF1 answers remain immutable."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from support.rf1_pins import assert_golden, canonical, golden_path, minor_tag

from gnd import api, artifacts, assurance
from gnd.assurance_evidence import production_identity
from gnd.exp import session

ROOT = Path(__file__).resolve().parents[2]
ANSWERS = ROOT / "tests/fixtures/rf2-pins/session-successors.json"


def independent_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def capture_mint(records):
    mint = assurance._mint_execution
    encoder = artifacts.canonical_json_bytes
    producer = production_identity()

    def wrapped(*args, **kwargs):
        inputs = []
        def encode(value, **options):
            raw = encoder(value, **options)
            if inspect.currentframe().f_back.f_code is mint.__code__:
                assert raw == independent_bytes(value), "mint encoder differs from independent encoder"
                inputs.append(copy.deepcopy(value))
            return raw
        with patch.object(artifacts, "canonical_json_bytes", encode):
            execution = mint(*args, **kwargs)
        assert len(inputs) == 1, "mint input capture is ambiguous"
        identity_input = inputs[0]
        digest = hashlib.sha256(independent_bytes(identity_input)).hexdigest()
        assert execution.identity == digest, "mint digest does not bind the complete input"
        assert identity_input["production_roster_digest"] == producer, "stale mint producer"
        records.append({"identity": digest, "input": identity_input})
        return execution

    return wrapped


def child_capture(destination):
    records = []
    api._mint_execution = capture_mint(records)
    # Flush records only after the real CLI evaluation has completed.
    return records


def install_capture(monkeypatch):
    records = []
    original = session.run_bounded_process
    temporary = tempfile.TemporaryDirectory(prefix="rf2-mint-inputs-")
    destination = Path(temporary.name) / "mint.jsonl"
    source_root = str(Path(assurance.__file__).resolve().parents[1])
    tests_root = str(ROOT / "tests")

    async def run(argv, **kwargs):
        if tuple(argv[:4]) != (sys.executable, "-I", "-m", "gnd"):
            return await original(argv, **kwargs)
        # -I remains; explicitly select the same source as the parent and add
        # the test-only capture hook. Payload and receipt generation stay real.
        program = (
            "import sys,json; from pathlib import Path; "
            f"sys.path[:0] = {[source_root, tests_root]!r}; "
            "from support.rf2_session_pins import child_capture; "
            f"records=child_capture({str(destination)!r}); "
            "from gnd.cli import main; "
            f"code=main({list(argv[4:])!r}); "
            f"Path({str(destination)!r}).open('a').write(''.join(json.dumps(r,ensure_ascii=False)+'\\n' for r in records)); "
            "raise SystemExit(code)"
        )
        result = await original((sys.executable, "-I", "-c", program), **kwargs)
        if destination.exists():
            records[:] = [json.loads(line) for line in destination.read_text().splitlines()]
        return result

    # Keep the temporary directory alive for the monkeypatch's lifetime.
    run._temporary = temporary
    monkeypatch.setattr(session, "run_bounded_process", run)
    return records


def project_input(data, tokens):
    """Pin raw declared text, retaining whitespace and escaped path spelling."""
    replacements = {}
    for needle, replacement in tokens.items():
        if needle:
            replacements[needle] = replacement
            replacements[json.dumps(needle, ensure_ascii=False)[1:-1]] = json.dumps(
                replacement, ensure_ascii=False)[1:-1]
    decoded = data.decode("utf-8")
    for needle, replacement in sorted(replacements.items(), key=lambda row: -len(row[0])):
        decoded = decoded.replace(needle, replacement)
    return {"text": decoded}


def prepare(observed, records, built, run, tmp_path, tokens):
    producer = production_identity()
    indexed = {}
    for row in records:
        data = row["input"]
        assert data["production_roster_digest"] == producer, "stale mint producer"
        digest = hashlib.sha256(independent_bytes(data)).hexdigest()
        assert row["identity"] == digest, "bad captured mint digest"
        assert digest not in indexed or indexed[digest] == data, "ambiguous mint digest"
        indexed[digest] = data
    answer = copy.deepcopy(observed)
    section = "evidence" if "evidence" in answer else "evidence_after"
    executions = {}
    evidence = answer[section]
    for leaf in sorted(evidence):
        if not leaf.startswith("attempts/") or not leaf.endswith("/attempt.json"):
            continue
        original_text = evidence[leaf]["text"]
        document = json.loads(original_text)
        for i, receipt in enumerate(document["assurance_receipts"]):
            digest = receipt["process_receipt"]["execution"]["identity"]
            assert digest in indexed, "execution occurrence has no authenticated mint input"
            location = f"{section}/{leaf}/assurance_receipts/{i}/process_receipt/execution/identity"
            data = copy.deepcopy(indexed[digest])
            data["production_roster_digest"] = "<production-identity>"
            executions[location] = data
            quoted = json.dumps(digest)
            assert original_text.count(quoted) == 1, "ambiguous execution occurrence"
            original_text = original_text.replace(quoted, json.dumps(f"<RF2-execution:{location}>"), 1)
        evidence[leaf]["text"] = original_text
    assert len(executions) == 2, f"expected two bound attempt occurrences: {list(executions)}; files: {list(evidence)}"
    inputs = {name: project_input(data, tokens) for name, data in built.inputs(run).items()}
    return {"observation": answer, "executions": executions, "declared_inputs": inputs}


def assert_successor(key, observed, records, built, run, tmp_path, tokens):
    assert not (os.environ.get("GND_RF2_SUCCESSOR_CAPTURE") and os.environ.get("GND_RF1_CAPTURE")), "dual RF1/RF2 capture forbidden"
    historical = golden_path("session", key)
    if historical is None:
        assert_golden("session", key, observed)  # Preserve RF1 unsupported-minor skip.
    assert historical is not None
    historical_digest = hashlib.sha256(historical.read_bytes()).hexdigest()
    answer = prepare(observed, records, built, run, tmp_path, tokens)
    answer["original_golden_sha256"] = historical_digest
    capture = os.environ.get("GND_RF2_SUCCESSOR_CAPTURE")
    if capture:
        # Capture is admissible only if the entire original answer is green.
        assert canonical(observed) == historical.read_bytes(), "original golden comparison failed before capture"
        target = Path(capture) / f"{key}.json"
        assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(answer, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    else:
        expected = json.loads(ANSWERS.read_text())[minor_tag()][key]
        assert answer == expected, f"RF2 successor changed: {key}"
