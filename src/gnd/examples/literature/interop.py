"""Run and verify the packaged extraction-to-checking literature fixture."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator

from gnd.anchors import bind_anchors, parse_anchor_sidecar, strict_json, vocabulary_digest
from gnd.artifacts import (
    ArtifactError,
    canonical_json_bytes,
    publish_directory_once,
    read_regular_file_bytes,
    sha256_hex,
)
from gnd.disclosure import ENVIRONMENT as DISCLOSURE_ENV
from gnd.errors import ModelLoadError, ModelValidationError, PopulationLoadError
from gnd.extract.bundle import bundle_stem
from gnd.extract.service import _verify_artifact_index
from gnd.model import load_model
from gnd.population import load_population_bytes
from gnd.process import ProcessLimits, run_bounded_process

from .interop_dates import advise

FIXTURE = Path(__file__).resolve().with_name("interop_fixture")
POLICY = FIXTURE.parent / "lineage/path-policy.json"
EXTRACTION = "extraction.orm.json"
CHECKING = "checking.orm.json"
CATALOG = "reference/catalog.json"
ARTIFACTS = "artifacts"
SOURCES = "sources"
SUMMARY = "interop.json"
POPULATION = "composed.population.json"
COMPOSITION = "composition.json"
EXTRACTED = "extracted.population.json"
EXTRACTION_SIDECAR = "extracted.population.extraction.json"
ORIGINAL_ANCHORS = "extracted.population.json.anchors.json"
REBOUND = "population.json"
REBOUND_ANCHORS = "population.json.anchors.json"
DATES = "publication-dates.json"
EDGES = "candidate-edges.json"
DATE_REPORT = "dates.json"
VOCABULARY = ("vocabulary/literature.orm.json", "vocabulary/chronology.orm.json")
INPUTS = (EXTRACTION, CHECKING, *VOCABULARY, CATALOG, "targets.json", DATES, EDGES)
CAP = 10 << 20
LIMITS = ProcessLimits(
    timeout_seconds=30, terminate_grace_seconds=1, stdin_limit_bytes=0,
    stdout_limit_bytes=CAP, stderr_limit_bytes=128 << 10, total_output_limit_bytes=CAP,
)


def _read(root: Path, name: str) -> bytes:
    return read_regular_file_bytes(root, name, label=name, max_bytes=CAP)


def _write(root: Path, name: str, payload: dict) -> None:
    (root / name).write_bytes(canonical_json_bytes(payload))


def _json(raw: bytes):
    return strict_json(raw, max_bytes=CAP, too_large="integration JSON exceeds its byte ceiling")


def _digest(root: Path, name: str) -> str:
    return sha256_hex(_read(root, name))


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def _stage(root: Path, *args: str) -> bytes:
    env = {name: os.environ[name] for name in (DISCLOSURE_ENV,) if name in os.environ}
    result = asyncio.run(run_bounded_process(
        (sys.executable, "-m", "gnd", *args), cwd=root, env=env, limits=LIMITS,
        disclosed_names=frozenset(env),
    ))
    if result.status != "succeeded" or result.stdout_truncated or result.stderr_truncated:
        detail = (result.stderr or result.stdout).decode(errors="replace").strip()[-400:]
        raise ValueError(f"{args[0]} exited {result.return_code}: {detail}")
    return result.stdout


def _source_plan() -> dict:
    return _json(_read(FIXTURE, "sources.json"))


def _index_names() -> tuple[str, str, str]:
    stem = bundle_stem(EXTRACTION)
    return (f"{stem}.artifacts.json", f"{stem}.projection.schema.json", f"{stem}.applicable.json")


def _roots(run: Path):
    extraction = load_model(run / EXTRACTION)
    checking = load_model(run / CHECKING)
    pins = [[{"id": entry.id, "sha256": entry.sha256} for entry in model._included]
            for model in (extraction, checking)]
    _require(bool(pins[0]) and extraction._references is not None and checking._references is not None,
             "both roots must bind vocabulary and catalog inputs")
    catalogs = [
        [{"id": origin.id, "raw_sha256": origin.raw_sha256} for origin, _, _ in model._references._snapshots]
        for model in (extraction, checking)
    ]
    _require(pins[0] == pins[1] and vocabulary_digest(extraction) == vocabulary_digest(checking),
             "root vocabulary pins differ")
    _require(catalogs[0] == catalogs[1] and extraction._references._owners == checking._references._owners,
             "root catalog bindings differ")
    _require(extraction.model_id != checking.model_id, "the model roots must have distinct identities")
    return extraction, checking, pins[0], catalogs[0]


def _anchor_rows(facts, document):
    anchors = []
    for fact_type, rows in facts.items():
        for row in rows:
            for role, value in row.items():
                offset = document.index(value)
                anchors.append({
                    "fact_key": {"fact_type": fact_type, "roles": row}, "role": role,
                    "span": {"start": offset, "end": offset + len(value)},
                    "occurrence": 0, "excerpt_sha256": sha256_hex(value.encode()),
                })
    return anchors


def _extract_source(run: Path, name: str, model, index, projection, applicable) -> None:
    directory = run / SOURCES / name
    directory.mkdir(parents=True)
    document = _read(FIXTURE, f"{name}.md")
    facts = _json(_read(FIXTURE, f"{name}.facts.json"))
    gold = _json(_read(FIXTURE, f"{name}.gold.json"))
    (directory / "document.md").write_bytes(document)
    extracted = {"population": index["header_template"], "facts": facts}
    _require(Draft202012Validator(projection).is_valid(extracted), "saved extraction violates its schema")
    _write(directory, EXTRACTED, extracted)
    _write(directory, "source.population.json", {"population": index["header_template"], "facts": gold})
    _write(directory, EXTRACTION_SIDECAR, {
        "schema_version": 1, "model": EXTRACTION, "model_sha256": index["model"]["sha256"],
        "population": EXTRACTED, "population_sha256": _digest(directory, EXTRACTED),
        "document": "document.md", "document_sha256": sha256_hex(document),
        "projection_sha256": index["artifacts"][_index_names()[1]]["sha256"],
        "skill": "gnd-extract", "skill_version": "1", "executing_model": "saved-public-fixture",
    })
    _write(directory, "document.manifest.json", {
        "schema_version": 1, "model": EXTRACTION, "model_sha256": index["model"]["sha256"],
        "source_population": "source.population.json",
        "source_population_sha256": _digest(directory, "source.population.json"),
        "document": "document.md", "document_sha256": sha256_hex(document),
        "applicable_sha256": applicable, "renderer_skill": "gnd-render-doc",
        "renderer_skill_version": "1", "executing_model": "authored-public-fixture",
        "distractors": [],
    })
    _write(directory, ORIGINAL_ANCHORS, {
        "schema_version": 2, "population_sha256": _digest(directory, EXTRACTED),
        "document_sha256": sha256_hex(document), "vocabulary_digest": vocabulary_digest(model),
        "anchors": _anchor_rows(facts, document.decode()),
    })


def rebind(run: Path, source: str) -> dict[str, bytes]:
    """Verify the extraction and derive checking-bound files from the original."""
    _require(source in _source_plan()["sources"], "unknown example source")
    return _rebind(run, source, _roots(run))


def _rebind(run: Path, source: str, roots) -> dict[str, bytes]:
    extraction, checking, pins, catalogs = roots
    directory = run / SOURCES / source
    index_name, projection_name, applicable_name = _index_names()
    index_path = f"{ARTIFACTS}/{index_name}"
    inputs = {
        "extraction_root_sha256": extraction._authored_sha256,
        "checking_root_sha256": checking._authored_sha256,
        "artifact_index_sha256": _digest(run, index_path),
        "document_sha256": _digest(directory, "document.md"),
        "extraction_population_sha256": _digest(directory, EXTRACTED),
        "extraction_sidecar_sha256": _digest(directory, EXTRACTION_SIDECAR),
        "extraction_anchors_sha256": _digest(directory, ORIGINAL_ANCHORS),
    }
    bundle = _verify_artifact_index(str(run / EXTRACTION), str(run / ARTIFACTS), (projection_name, applicable_name))
    _require(bundle.root_sha256 == inputs["extraction_root_sha256"], "the extraction root changed")
    _stage(run, "verify", EXTRACTION, f"{SOURCES}/{source}/{EXTRACTED}", "--artifacts", ARTIFACTS,
           "--format", "json")
    original = _read(directory, EXTRACTED)
    original_anchors = _read(directory, ORIGINAL_ANCHORS)
    document = _read(directory, "document.md")
    expected_snapshots = {
        "extraction_population_sha256": original, "extraction_anchors_sha256": original_anchors,
        "document_sha256": document, "extraction_sidecar_sha256": _read(directory, EXTRACTION_SIDECAR),
        "artifact_index_sha256": _read(run, index_path),
    }
    _require(all(sha256_hex(raw) == inputs[key] for key, raw in expected_snapshots.items()),
             "extraction evidence changed during verification")
    _require((_digest(run, EXTRACTION), _digest(run, CHECKING)) ==
             (inputs["extraction_root_sha256"], inputs["checking_root_sha256"]), "a root changed during rebind")
    population = _json(original)
    population["population"].update(model=CHECKING, model_id=checking.model_id)
    rebound = canonical_json_bytes(population)
    anchors = _json(original_anchors)
    anchors.update(population_sha256=sha256_hex(rebound), vocabulary_digest=vocabulary_digest(checking))
    anchor_bytes = canonical_json_bytes(anchors)
    validated = load_population_bytes(rebound, source=REBOUND, model=checking)
    bind_anchors(parse_anchor_sidecar(anchor_bytes), checking, rebound, document, validated)
    record = canonical_json_bytes({
        "schema": "literature-rebind/1", "source": source, **inputs, "includes": pins, "references": catalogs,
        "rebound_population_sha256": sha256_hex(rebound), "rebound_anchors_sha256": sha256_hex(anchor_bytes),
    })
    return {REBOUND: rebound, REBOUND_ANCHORS: anchor_bytes, "document.txt": document, "rebind.json": record}


def _resolution(run: Path, plan: dict) -> tuple[bytes, bytes]:
    sources = plan["sources"]
    decision = plan["resolution"]
    role, relation, object_type = (decision[key] for key in ("role", "fact_type", "object_type"))
    keys, evidence, digests = [], [], {}
    for index, name in enumerate(sources):
        base = run / SOURCES / name
        candidate_raw = _read(base, REBOUND)
        rows = _json(candidate_raw)["facts"][relation]
        _require(len(rows) == 1, "each fixture source needs one catalog alias")
        fact = rows[0]
        sidecar = parse_anchor_sidecar(_read(base, REBOUND_ANCHORS))
        anchor = next(a for a in sidecar.anchors
                      if a["fact_key"] == {"fact_type": relation, "roles": fact} and a["role"] == role)
        keys.append({"source": name, "object_type": object_type, "value": fact[role]})
        evidence.append({"source": name, "key": index, "fact_type": relation, "role": role,
                         "fact_index": 0, "span": anchor["span"]})
        digests[name] = sha256_hex(candidate_raw)
    preferred = next(key["value"] for key in keys if key["source"] == decision["preferred"])
    resolution = canonical_json_bytes({
        "schema": "gnd-resolution/1", "object_types": [object_type],
        "decisions": [{"decision": "same", "keys": keys, "evidence": evidence, "input_sha256": digests,
                       "placeholders": None, "producer": {"id": "corpus-author", "kind": "reviewer"}}],
    })
    manifest = canonical_json_bytes({
        "schema": "gnd-composition-manifest/1", "sources": sources, "scope_tags": [],
        "deduplications": "identical-rows", "renamings": [
            {"source": key["source"], "fact_type": relation, "role": role, "from": key["value"],
             "to": preferred, "decision": 0}
            for key in keys if key["value"] != preferred
        ],
        "resolution": {"path": "resolution.json", "sha256": sha256_hex(resolution)},
    })
    return resolution, manifest


def _check(run: Path) -> bytes:
    return _stage(run, "check", CHECKING, POPULATION, "--composition", COMPOSITION,
                  "--sources", SOURCES, "--format", "json")


def _replay(run: Path) -> bytes:
    return _stage(run, "replay", CHECKING, POPULATION, "witness.json", "--composition",
                  COMPOSITION, "--raw")


def _fidelity(run: Path) -> bytes:
    report = _stage(run, "fidelity", EXTRACTION, "--cases", SOURCES, "--artifacts", ARTIFACTS,
                    "--format", "json")
    cases = _json(report)["cases"]
    _require(cases["ran"] == len(_source_plan()["sources"]) and cases["failed"] == cases["skipped"] == 0,
             "fidelity did not score both original extractions")
    return report


def _advice(run: Path) -> dict:
    return advise(_read(run, EDGES), _read(run, DATES), _read(POLICY.parent, POLICY.name))


def _manifest(run: Path, names: list[str], *, dates: bool) -> dict:
    stage_files = (f"{ARTIFACTS}/{_index_names()[0]}", f"{SOURCES}/resolution.json",
                   f"{SOURCES}/manifest.json", POPULATION, COMPOSITION, "check.json",
                   "witness.json", "replay.json", "fidelity.json")
    file_names = [*INPUTS, *stage_files]
    file_names.extend(
        f"{SOURCES}/{name}/{leaf}" for name in names
        for leaf in ("rebind.json", "source.population.json", "document.manifest.json")
    )
    if dates:
        file_names.append(DATE_REPORT)
    documents = sum(
        not (run / SOURCES / name / "document.md").samefile(run / SOURCES / name / "document.txt")
        for name in names
    )
    return {
        "schema": "literature-interop/1", "source_order": names, "with_dates": dates,
        "sha256": {name: _digest(run, name) for name in file_names},
        "layout": {"additional_copies": {
            "document": documents, "extraction_population": 0, "extraction_sidecar": 0,
        }, "rebound_population_files": len(names), "rebound_anchor_files": len(names)},
    }


def verify(run: Path) -> dict:
    raw = _read(run, SUMMARY)
    recorded = _json(raw)
    plan = _source_plan()
    names = plan["sources"]
    _require(isinstance(recorded, dict) and type(recorded.get("with_dates")) is bool
             and isinstance(recorded.get("sha256"), dict), "invalid integration manifest")
    dates = recorded["with_dates"]
    expected = _manifest(run, names, dates=dates)
    for path, digest in expected["sha256"].items():
        _require(recorded["sha256"].get(path) == digest, f"stale integration evidence at {path}")
    _require(raw == canonical_json_bytes(expected), "integration manifest differs from verified files")
    for name in INPUTS:
        _require(_read(run, name) == _read(FIXTURE, name), f"fixture input differs at {name}")
    roots = _roots(run)
    for name in names:
        directory = run / SOURCES / name
        _require(_read(directory, "document.md") == _read(FIXTURE, f"{name}.md"),
                 f"fixture document differs at {name}")
        for leaf, expected_facts in ((EXTRACTED, "facts"), ("source.population.json", "gold")):
            observed = _json(_read(directory, leaf))["facts"]
            _require(observed == _json(_read(FIXTURE, f"{name}.{expected_facts}.json")),
                     f"fixture facts differ at {name}/{leaf}")
        for leaf, content in _rebind(run, name, roots).items():
            _require(_read(directory, leaf) == content, f"rebind differs at {name}/{leaf}")
    resolution, manifest = _resolution(run, plan)
    _require(_read(run / SOURCES, "resolution.json") == resolution
             and _read(run / SOURCES, "manifest.json") == manifest, "source resolution differs from the fixture")
    from gnd.witness.io import load_certificate

    certificate = load_certificate(run / "witness.json")
    _require([result["target"] for result in certificate["results"]] ==
             _json(_read(run, "targets.json"))["targets"], "witness targets differ from the fixture")
    for leaf, operation in (("check.json", _check), ("replay.json", _replay), ("fidelity.json", _fidelity)):
        _require(_read(run, leaf) == operation(run), f"stage report differs at {leaf}")
    if dates:
        _require(_read(run, DATE_REPORT) == canonical_json_bytes(_advice(run)), "date advisory differs")
    return expected


def build(out: Path, *, dates: bool = False) -> None:
    plan = _source_plan()
    names = plan["sources"]
    with tempfile.TemporaryDirectory(prefix="gnd-literature-interop-") as scratch:
        run = Path(scratch).resolve()
        for name in INPUTS:
            target = run / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(_read(FIXTURE, name))
        _stage(run, "extract", EXTRACTION, "--out", ARTIFACTS)
        index_name, projection_name, applicable_name = _index_names()
        artifacts = run / ARTIFACTS
        index = _json(_read(artifacts, index_name))
        projection = _json(_read(artifacts, projection_name))
        applicable = _digest(artifacts, applicable_name)
        roots = _roots(run)
        for name in names:
            _extract_source(run, name, roots[0], index, projection, applicable)
            for leaf, raw in _rebind(run, name, roots).items():
                (run / SOURCES / name / leaf).write_bytes(raw)
        resolution, manifest = _resolution(run, plan)
        (run / SOURCES / "resolution.json").write_bytes(resolution)
        (run / SOURCES / "manifest.json").write_bytes(manifest)
        _stage(run, "compose", CHECKING, SOURCES, "--out", POPULATION, "--record", COMPOSITION)
        (run / "check.json").write_bytes(_check(run))
        if dates:
            _write(run, DATE_REPORT, _advice(run))
        _stage(run, "witness", CHECKING, POPULATION, "--targets", "targets.json",
               "--composition", COMPOSITION, "--raw", "--out", "witness.json")
        (run / "replay.json").write_bytes(_replay(run))
        (run / "fidelity.json").write_bytes(_fidelity(run))
        _write(run, SUMMARY, _manifest(run, names, dates=dates))
        files = {path.relative_to(run).as_posix(): _read(run, path.relative_to(run).as_posix())
                 for path in run.rglob("*") if path.is_file()}
        publish_directory_once(out.parent, out.name, files, manifest_name=SUMMARY, max_file_bytes=CAP)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    run = commands.add_parser("run", help="build the packaged interoperable example")
    run.add_argument("--out", required=True, type=Path)
    run.add_argument("--dates", action="store_true")
    commands.add_parser("verify", help="re-derive the evidence chain").add_argument("run", type=Path)
    dates = commands.add_parser("dates", help="report publication-order advice")
    dates.add_argument("run", type=Path)
    dates.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "run":
            build(args.out.absolute(), dates=args.dates)
        else:
            path = args.run.resolve(strict=True)
            verify(path)
            if args.action == "dates":
                raw = canonical_json_bytes(_advice(path))
                if args.out is None:
                    sys.stdout.write(raw.decode())
                else:
                    with args.out.open("xb") as destination:
                        destination.write(raw)
        return 0
    except (ArtifactError, OSError, ValueError, TypeError, KeyError, RecursionError, StopIteration,
            ModelLoadError, ModelValidationError, PopulationLoadError) as error:
        print(f"literature-interop: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
