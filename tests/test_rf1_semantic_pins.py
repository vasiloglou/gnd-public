"""RF1 lane L-SEM: resolver, datetime sites, checker, verbalize, extract, diff,
assurance and the synth oracle (spec 6.5)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main, run_process
from support.rf1_pins import (
    LARGE_RESULT_BYTES,
    assert_golden,
    encode,
    inputs,
    load_cases,
    observe,
    scrub,
    sha256_hex,
)

from gnd import (
    assurance,
    checker,
    model,
    model_verbalization,
    population,
    popvalidate,
    semantic_adapter,
)
from gnd.export import pyrel_runtime
from gnd.extract import vocabulary
from gnd.synth import assemble, boundary, mutate

ROOT = Path(__file__).resolve().parents[1]
CASES = load_cases()
CORPUS = CASES["corpus"]
META = ROOT / "src/gnd/schema/orm-meta.schema.json"


def _id(path: str) -> str:
    return path.replace("src/gnd/examples/", "ex/").replace("tests/fixtures/", "fx/")


def _run(argv: list[str]) -> dict:
    result = run_main(argv, cwd=ROOT)
    return {"argv": argv, "exit": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}


# --- T-SEM-RESOLVER ----------------------------------------------------------

RESOLVER_VALUES = {
    "true": True, "false": False, "one": 1, "zero": 0, "yes": "yes", "empty-string": "", "none": None,
}


def _resolver_model(flag) -> tuple[list[dict], model.Model]:
    child = {"id": "Child", "kind": "entity", "name": "Child", "subtype_of": ["Base"]}
    if flag != "absent":
        child["inherits_reference"] = RESOLVER_VALUES[flag]
    object_types = [
        {"id": "Code", "kind": "value", "name": "Code", "primitive": "String"},
        {"id": "Base", "kind": "entity", "name": "Base", "reference": {"mode": "popular", "value_type": "Code"}},
        child,
    ]
    built = model.Model.model_construct(object_types=object_types, fact_types=[], constraints=[])
    return object_types, built


def _resolver_row(flag: str) -> dict:
    object_types, built = _resolver_model(flag)
    by_id = {item["id"]: item for item in object_types}
    doc = {"object_types": object_types, "fact_types": []}
    return {
        "popvalidate.resolve_primitive": observe(popvalidate.resolve_primitive, "Child", built),
        "popvalidate.resolve_reference_value_type": observe(popvalidate.resolve_reference_value_type, "Child", built),
        "model._resolved_primitive": observe(model._resolved_primitive, "Child", by_id),
        "pyrel_runtime.ModelIndex.primitive": observe(lambda: pyrel_runtime.ModelIndex(doc).primitive("Child")),
        "pyrel_runtime.ModelIndex.reference_value_type": observe(
            lambda: pyrel_runtime.ModelIndex(doc).reference_value_type("Child")
        ),
        "extract.vocabulary._object_type_sentence": observe(
            vocabulary._object_type_sentence, by_id["Child"], by_id, built
        ),
        "model_verbalization._object_type_cnl": observe(
            model_verbalization._object_type_cnl, by_id["Child"], object_types=by_id, model=built
        ),
    }


def test_resolver():
    observed = {flag: _resolver_row(flag) for flag in [*RESOLVER_VALUES, "absent"]}
    assert_golden("sem", "resolver", observed)


# --- T-SEM-DATETIME ----------------------------------------------------------

BOUND = "2024-01-01T00:00:00Z"
DATETIME_SITES = {
    "model._temporal_literal_valid": lambda v: model._temporal_literal_valid(v, "DateTime"),
    "checker._typed_comparison_values": lambda v: checker._typed_comparison_values(v, BOUND, "DateTime", "DateTime"),
    "semantic_adapter.canonical_scalar": lambda v: semantic_adapter.canonical_scalar(v, "DateTime"),
    "synth.boundary.boundary_neighbour": lambda v: boundary.boundary_neighbour(v, "DateTime", 1),
    "synth.assemble._instant_pair": lambda v: assemble._instant_pair(v, "2024-01-01T00:00:00+00:00", "DateTime"),
    "export.pyrel_runtime._valid_temporal": lambda v: pyrel_runtime._valid_temporal(v, "DateTime"),
}


@pytest.mark.parametrize("site", sorted(DATETIME_SITES))
def test_datetime_site(site):
    observed = {name: observe(DATETIME_SITES[site], value) for name, value in inputs("iso_datetime")}
    assert_golden("sem-datetime", site, observed)


# --- T-SEM-CHK, T-SEM-CHK-COV ------------------------------------------------

EXCLUDED_VERDICT_FIELDS = ("scope_id", "fact_refs")


def _check_case(model_path: str, population_path: str) -> dict:
    loaded = model.load_model(ROOT / model_path)
    observed: dict = {"in_process": observe(lambda: _report(loaded, population_path))}
    observed["cli_text"] = _run(["check", model_path, population_path])
    observed["cli_json"] = _run(["check", model_path, population_path, "--format", "json"])
    observed["cli_admission_json"] = _run(["check", model_path, population_path, "--admission", "--format", "json"])
    return observed


def _report(loaded: model.Model, population_path: str) -> dict:
    report = checker.check(loaded, population.load_population(ROOT / population_path, model=loaded))
    return {
        "wire": report.model_dump(mode="json"),
        "excluded": [
            {field: encode(getattr(verdict, field, None)) for field in EXCLUDED_VERDICT_FIELDS}
            for verdict in report.verdicts
        ],
    }


PAIR_IDS = [f"{_id(m)}|{_id(p)}" for m, p in CORPUS["checker_pairs"]]


@pytest.mark.parametrize("pair", CORPUS["checker_pairs"], ids=PAIR_IDS)
def test_check(pair):
    assert_golden("sem-check", f"{_id(pair[0])}|{_id(pair[1])}", _check_case(*pair))


def test_check_transition():
    spec = CORPUS["transition"]
    observed = {
        steps: _run(
            ["check", spec["model"], "--pre", spec["pre"], "--steps", steps, "--post", spec["post"], "--format", "json"]
        )
        for steps in spec["steps"]
    }
    assert_golden("sem-check", "transition", observed)


def test_check_batch(tmp_path):
    batch = tmp_path / "batch"
    batch.mkdir()
    for _model_path, population_path in CORPUS["checker_pairs"][4:10]:
        shutil.copy(ROOT / population_path, batch / Path(population_path).name)
    # The batch arm writes to sys.stdout.buffer, so it runs as a real process
    # (an in-process StringIO capture has no buffer; RF1 finding F6).
    argv = ["check", "tests/fixtures/checker/setfam.orm.yaml", "--populations", str(batch), "--format", "json"]
    result = run_process([sys.executable, "-m", "gnd", *argv], cwd=ROOT)
    observed = {"argv": argv, "exit": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()}
    assert_golden("sem-check", "batch", scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"}))


def _constraint_types() -> set[str]:
    schema = json.loads(META.read_text())
    found: set[str] = set()

    def walk(node, inside_type=False):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "type" and isinstance(value, dict) and isinstance(value.get("const"), str):
                    found.add(value["const"])
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema.get("$defs", schema).get("constraint", schema))
    return found


# Constraint types the corpus cannot drive to an outcome, with the measured reason.
COVERAGE_EXEMPT: dict[tuple[str, str], str] = {
    ("textual", "satisfied"): "the checker reports every textual constraint as unchecked",
    ("textual", "violated"): "the checker reports every textual constraint as unchecked",
}
ANCHORED = ROOT / "tests/fixtures/v70-phase1"


def _anchored_cases() -> dict[str, dict]:
    """The v70-phase1 anchored corpus, and its date-suffix mutation (a bound anchor fails)."""
    import hashlib
    from dataclasses import replace

    from gnd import api
    from gnd.extract.anchors import read_anchor_sidecar

    raw = (ANCHORED / "document.txt").read_bytes()
    mutated = raw.replace(b"2024-02-29,", b"2024-02-29-", 1)
    sidecar = read_anchor_sidecar(ANCHORED / "population.pop.json.anchors.json")
    cases = {"original": (sidecar, raw), "date-suffix": (replace(sidecar, document_sha256=hashlib.sha256(mutated).hexdigest()), mutated)}
    return {
        name: api.check(ANCHORED / "model.orm.yaml", ANCHORED / "population.pop.json", anchors=anchors, document=document)
        for name, (anchors, document) in cases.items()
    }


def test_check_anchored():
    assert_golden("sem-check", "anchored", {name: encode(result) for name, result in _anchored_cases().items()})


def _outcome(verdict: str) -> str | None:
    return "satisfied" if verdict == "pass" else "violated" if verdict in {"fail", "warning"} else None


def test_check_coverage():
    """T-SEM-CHK-COV: each constraint type has a satisfied and a violated verdict."""
    seen: set[tuple[str, str]] = set()
    for model_path, population_path in CORPUS["checker_pairs"]:
        loaded = model.load_model(ROOT / model_path)
        report = checker.check(loaded, population.load_population(ROOT / population_path, model=loaded))
        for verdict in report.verdicts:
            if outcome := _outcome(verdict.verdict):
                seen.add((verdict.constraint_type, outcome))
    for result in _anchored_cases().values():
        for row in result["verdicts"]:
            if outcome := _outcome(row["verdict"]):
                seen.add((row["constraint_type"], outcome))
    missing = sorted(
        (kind, outcome)
        for kind in _constraint_types()
        for outcome in ("satisfied", "violated")
        if (kind, outcome) not in seen and (kind, outcome) not in COVERAGE_EXEMPT
    )
    assert missing == []


# --- T-SEM-VERB, T-SEM-EXTRACT -----------------------------------------------


@pytest.mark.parametrize("pair", CORPUS["checker_pairs"], ids=PAIR_IDS)
def test_verbalize_population(pair):
    observed = {
        fmt: _run(["verbalize", "population", pair[0], pair[1], "--format", fmt]) for fmt in ("text", "jsonl")
    }
    assert_golden("sem-verbalize", f"{_id(pair[0])}|{_id(pair[1])}", observed)


def _tree_text(root: Path) -> dict:
    """Every written file; one over LARGE_RESULT_BYTES is recorded by sha256 and size."""
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            key = path.relative_to(root).as_posix()
            if len(data) > LARGE_RESULT_BYTES:
                files[key] = {"sha256": sha256_hex(data), "bytes": len(data)}
            else:
                files[key] = data.decode("utf-8", "replace")
    return files


@pytest.mark.parametrize("model_path", CORPUS["models"], ids=[_id(m) for m in CORPUS["models"]])
def test_extract(model_path, tmp_path):
    out = tmp_path / "out"
    observed = _run(["extract", model_path, "--out", str(out)])
    observed["files"] = _tree_text(out) if out.is_dir() else None
    assert_golden("sem-extract", _id(model_path), scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"}))


# --- T-SEM-DIFF --------------------------------------------------------------


@pytest.mark.parametrize("pair", CORPUS["diff_pairs"], ids=[f"{_id(a)}|{_id(b)}" for a, b in CORPUS["diff_pairs"]])
def test_diff(pair, tmp_path):
    observed = {fmt: _run(["diff", pair[0], pair[1], "--format", fmt]) for fmt in ("text", "json")}
    pops = tmp_path / "pops"
    pops.mkdir()
    for model_path, population_path in CORPUS["checker_pairs"]:
        if model_path == pair[0]:
            shutil.copy(ROOT / population_path, pops / Path(population_path).name)
    observed["with_populations"] = _run(["diff", pair[0], pair[1], "--populations", str(pops), "--format", "json"])
    assert_golden("sem-diff", f"{_id(pair[0])}|{_id(pair[1])}", scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"}))


# --- T-SEM-ASSURANCE ---------------------------------------------------------


def test_assurance_blocks():
    """The band to decision map and the wire block per decision. The per-case
    assurance block is pinned inside every T-SEM-CHK JSON report."""
    observed = {
        str(band): {
            "decision": observe(assurance.semantic_decision_for_band, band),
            "block": observe(lambda b=band: assurance.AssuranceBlockV1(assurance.semantic_decision_for_band(b)).as_dict()),
        }
        for band in (0, 1, 2, 3, 4, 5, 6, 64, 66, 70, 74)
    }
    observed["phase3_scope_ids"] = observe(assurance.phase3_scope_ids)
    assert_golden("sem-assurance", "blocks", observed)


def test_assurance_inheritance_comparison():
    import copy

    from support.public_inherited_comparison_input import retained

    from gnd import assurance_inheritance

    prior = retained("phase5")
    observations = copy.deepcopy(prior["observations"])
    mutations = copy.deepcopy(prior["mutations"])
    observed = {
        "retained": observe(assurance_inheritance.compare_observations, "phase5", prior, observations, mutations, None),
        "one-mutation-dropped": observe(
            assurance_inheritance.compare_observations, "phase5", prior, observations, mutations[1:], None
        ),
    }
    assert_golden("sem-assurance", "inheritance-comparison", observed)


# --- T-SEM-ORACLE ------------------------------------------------------------


def _doc(path: str) -> dict:
    return YAML(typ="safe").load((ROOT / path).read_text(encoding="utf-8"))


def _oracle(model_path: str, population_path: str) -> dict:
    loaded = model.load_model(ROOT / model_path)
    doc = _doc(population_path)
    children = assemble._direct_subtypes(loaded)
    states = {
        ref: observe(mutate.expected_state, constraint, ft, doc, loaded, children)
        for ref, constraint, ft in assemble._constraint_iter_with_ref(loaded)
    }
    return {
        "expected_state": states,
        "predict_boundary": observe(boundary.predict_boundary, loaded, doc),
        "build_expectations": observe(assemble._build_expectations, loaded, doc, children),
    }


ORACLE_PAIRS = [pair for pair in CORPUS["checker_pairs"] if pair[0].startswith("tests/fixtures/checker/")]


@pytest.mark.parametrize("pair", ORACLE_PAIRS, ids=[f"{_id(m)}|{_id(p)}" for m, p in ORACLE_PAIRS])
def test_oracle(pair):
    assert_golden("sem-oracle", f"{_id(pair[0])}|{_id(pair[1])}", _oracle(*pair))


VIOLATION_PAIRS = [
    ("tests/fixtures/checker/misc.orm.yaml", "population.misc_pass.yaml", "population.misc_fail.yaml"),
    ("tests/fixtures/checker/ring.orm.yaml", "population.ring_pass.yaml", "population.ring_fail.yaml"),
    ("tests/fixtures/checker/setfam.orm.yaml", "population.setfam_pass.yaml", "population.setfam_fail.yaml"),
]


@pytest.mark.parametrize("triple", VIOLATION_PAIRS, ids=[t[0].rsplit("/", 1)[1] for t in VIOLATION_PAIRS])
def test_predict_violations(triple):
    model_path, baseline, mutated = triple
    loaded = model.load_model(ROOT / model_path)
    base = f"tests/fixtures/checker/{baseline}"
    bad = f"tests/fixtures/checker/{mutated}"
    observed = observe(mutate.predict_violations, loaded, _doc(base), _doc(bad))
    assert_golden("sem-oracle", f"predict-violations|{_id(model_path)}", observed)


@pytest.mark.parametrize("model_path", CORPUS["models"], ids=[_id(m) for m in CORPUS["models"]])
def test_synth(model_path, tmp_path):
    out = tmp_path / "synth"
    observed = _run(["synth", model_path, "--class", "all", "--seed", "0", "--out", str(out), "--format", "json"])
    # A synth corpus is hundreds of files; each is pinned by digest and size, while
    # the oracle's expected states are pinned in full by test_oracle.
    observed["files"] = (
        {path.relative_to(out).as_posix(): {"sha256": sha256_hex(path.read_bytes()), "bytes": path.stat().st_size}
         for path in sorted(out.rglob("*")) if path.is_file()}
        if out.is_dir() else None
    )
    assert_golden("sem-synth", _id(model_path), scrub(observed, {str(tmp_path.resolve()): "<tmp>", str(tmp_path): "<tmp>"}))
