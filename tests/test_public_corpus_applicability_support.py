"""Original live execution minter and pure fail-closed applicability controls."""
from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import tempfile
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from test_public_assurance_inputs_support import contained

from gnd import assurance
from gnd.assurance_evidence import _json, _read
from gnd.semantic_registry import capture_branches

inputs = SimpleNamespace(_json=_json, _read=_read, contained=contained)

def _materialize():
    packed = (Path(__file__).parent / "fixtures/public-corpus-applicability/closure.json.gz").read_bytes()
    assert len(packed) <= 8192
    assert hashlib.sha256(packed).hexdigest() == "7438904dae86762578cc48e263bec050433146365adb45df1725d74a31e9f323"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(65537)
    assert len(raw) <= 65536
    assert hashlib.sha256(raw).hexdigest() == "685b57ce99e80e2429a464f845e50467ca86f6a84042af932b10c3f8598cebf8"
    documents = json.loads(raw)
    assert set(documents) == {'tests/fixtures/v6-assurance/cases/separation-of-duties/conforming/model.orm.yaml', 'tests/fixtures/v6-assurance/narratives.json', 'tests/fixtures/v6-assurance/cases/separation-of-duties/conforming/post.json', 'tests/fixtures/v6-assurance/cases/separation-of-duties/conforming/steps.json', 'coordinates.json', 'tests/fixtures/v6-assurance/cases/separation-of-duties/conforming/pre.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-corpus-applicability-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    coordinates = json.loads((root / "coordinates.json").read_text())
    assert len(coordinates["rows"]) == len(coordinates["answers"]) == 7
    return temporary, root, coordinates["rows"], coordinates["answers"]

_TEMPORARY, ROOT, ROWS, ANSWERS = _materialize()
atexit.register(_TEMPORARY.cleanup)

def narratives(root: Path = ROOT) -> dict[str, dict]:
    rows = inputs._json(inputs._read(root / "tests/fixtures/v6-assurance/narratives.json"))["cases"]
    result = {row["case_id"]: row for row in rows}
    if len(result) != 35:
        raise ValueError("Phase 6 narrative census changed")
    return result

def live_execution(case: dict, root: Path = ROOT):
    """Mint the same immutable execution capability as a live CLI evaluation."""
    from gnd import checker, report, transition
    from gnd.model import load_model
    from gnd.population import load_population

    model = load_model(inputs.contained(root, case["model"]))
    steps = None
    with capture_branches() as trace:
        if case["kind"] == "transition":
            populations = [
                load_population(inputs.contained(root, case[name]), model=model)
                for name in ("pre", "post")
            ]
            document = transition.read_steps_document(inputs.contained(root, case["steps"]))
            transition.verify_digests(document, model, inputs.contained(root, case["pre"]))
            steps = transition.validate_steps(document, model)
            result = transition.evaluate(model, *populations, steps)
            band = transition.band(result)
            report.build_transition_payload(
                band,
                "model.orm.yaml",
                evaluated=True,
                supplied_digests=document,
                transition_report=result,
                schema_version=7,
            )
        else:
            populations = [load_population(inputs.contained(root, case["population"]), model=model)]
            result = checker.check(model, populations[0])
            band = checker.band(result)
            report.build_check_payload(
                band,
                "model.orm.yaml",
                "population.json",
                report=result,
                schema_version=7,
                structured=case["kind"] == "derivation",
            )
    execution = assurance._mint_execution(model, populations, result, band, trace, steps=steps)
    if not execution.complete:
        raise ValueError("live applicability baseline is incomplete")
    return execution

def applicability(row: dict, execution, evidence) -> dict:
    """Corrupt one declared execution boundary and observe fail-closed policy."""
    mutation = row["recipe"]["mutation"]
    fields = asdict(execution)
    if mutation == "extra-unregistered":
        fields["trace"] = execution.trace | {"phase6:unregistered:control"}
    elif mutation == "omitted-applicable":
        fields["input_scope_ids"] = frozenset()
        fields["complete"] = False
    elif mutation in {
        "omitted-finding",
        "omitted-trace",
        "omitted-nested-snapshot",
        "omitted-deontic",
        "duplicate-declaration",
    }:
        # These controls fail at capability admission: a duplicate cannot be
        # represented by the canonical frozenset, and each omission changes
        # an input/result/trace relation checked by the live minter.
        fields["complete"] = False
    else:
        raise ValueError("unknown applicability control")
    changed = assurance._internal_value(assurance.AuthenticatedExecution, **fields)
    scope = assurance.derive_assurance_scope(changed, consumer="report")
    block = assurance.certify_result(changed, scope=scope, evidence=evidence)
    return {
        "band": changed.band,
        "error": "unauthenticated-applicability" if not scope.valid else None,
        "level": block.assurance_level,
    }
