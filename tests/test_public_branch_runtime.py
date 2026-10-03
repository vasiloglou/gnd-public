"""Current checker branch controls over reviewed generic inputs.
Frozen decisions are compared with ordinary current runtime observations.
"""
from __future__ import annotations

import atexit
import copy
import gzip
import hashlib
import io
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import pytest

from gnd.checker import band, check
from gnd.model import Model, load_model
from gnd.population import load_population
from gnd.proof_kernel import decide_phase1_assurance


def _public_corpus():
    path = Path(__file__).parent / "fixtures/public-branch-runtime/corpus.json.gz"
    assert path.is_file() and not path.is_symlink()
    with path.open("rb") as stream:
        packed = stream.read(131073)
    assert len(packed) <= 131072
    assert hashlib.sha256(packed).hexdigest() == "a5704aa04514aca474c770406baaa995693a3d11b62b1d712625383574d1fa28"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(1048577)
    assert len(raw) <= 1048576
    documents = json.loads(raw)
    assert isinstance(documents, dict) and len(documents) == 85
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-branches-")
    root = Path(temporary.name)
    for name, text in documents.items():
        parts = Path(name).parts
        assert not Path(name).is_absolute() and ".." not in parts
        assert name.startswith(("proof/v6/phase1/corpus/fixtures/", "proof/v6/scope/corpus/", "tests/fixtures/adversarial/", "tests/fixtures/checker/", "tests/fixtures/guarded/"))
        assert isinstance(text, str) and len(text.encode("utf-8")) <= 131072
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
    return temporary, root

_TEMPORARY, REPO_ROOT = _public_corpus()
atexit.register(_TEMPORARY.cleanup)
CORPUS = REPO_ROOT / "proof" / "v6" / "scope" / "corpus"
CASES: dict[str, Any] = json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))
EXECUTION_ROUTES = json.loads((CORPUS / "execution-routes.json").read_text())["overrides"]
EXPECTED: dict[str, Any] = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
ROUTE_CASES = json.loads((CORPUS / "route-cases.json").read_text())
ROUTE_EXPECTED = json.loads((CORPUS / "route-expected.json").read_text())
ROUTE_BY_ID = {row["id"]: row for row in ROUTE_CASES["cases"]}


CASE_BY_ID = {row["id"]: row for row in CASES["cases"]}


BUILD_BY_ID = {**CASE_BY_ID, **ROUTE_BY_ID}


CASE_IDS = tuple(CASE_BY_ID)


def _load_yaml(path: Path) -> dict[str, Any]:
    from ruamel.yaml import YAML

    return YAML(typ="safe").load(path.read_text(encoding="utf-8"))


_TOKEN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\[([^\]]+)\])?$")


def _descend(node: Any, token: str) -> tuple[Any, Any]:
    """Resolve one path token to (container, key) without creating anything."""
    match = _TOKEN.match(token)
    assert match is not None, f"bad patch token {token!r}"
    name, key = match.group(1), match.group(2)
    if key is None:
        if isinstance(node, dict) and name not in node:
            return node, name  # a set may create the final key
        return node, name
    container = node[name]
    if isinstance(container, list):
        if key.isdigit():
            return container, int(key)
        for index, item in enumerate(container):
            if isinstance(item, dict) and item.get("id") == key:
                return container, index
        raise KeyError(f"no list member with id {key!r} under {name}")
    return container, key


def _apply(document: dict[str, Any], patches: list[dict[str, Any]]) -> dict[str, Any]:
    document = copy.deepcopy(document)
    for patch in patches:
        tokens = patch["path"].split(".")
        node: Any = document
        for token in tokens[:-1]:
            container, key = _descend(node, token)
            node = container[key]
        container, key = _descend(node, tokens[-1])
        if patch.get("delete"):
            del container[key]
        elif "append" in patch:
            target = container[key]
            assert isinstance(target, list), patch
            target.append(patch["append"])
        else:
            container[key] = patch["value"]
    return document


def _documents(case_id: str):
    row = BUILD_BY_ID[case_id]
    model_doc = _load_yaml(REPO_ROOT / row["model"])
    population_doc = _load_yaml(REPO_ROOT / row["population"])
    if row.get("model_patch"):
        model_doc = _apply(model_doc, row["model_patch"])
    if row.get("population_patch"):
        population_doc = _apply(population_doc, row["population_patch"])
    return model_doc, population_doc


def _build(case_id: str, tmp_path: Path, *, negative=False):
    """The admitted pair, optionally with its single controlled input change."""
    row = BUILD_BY_ID[case_id]
    model_doc, population_doc = _documents(case_id)
    if negative:
        control = {**CASES["negative_controls"], **ROUTE_CASES["negative_controls"]}[case_id]
        if control["document"] == "model":
            model_doc = _apply(model_doc, [control["patch"]])
        else:
            assert control["document"] == "population"
            population_doc = _apply(population_doc, [control["patch"]])
    model_path = tmp_path / f"{case_id}.model.orm.yaml"
    model_path.write_text(json.dumps(model_doc), encoding="utf-8")
    if row.get("admission") == "unvalidated":
        model = Model.model_validate({**model_doc, "warnings": []})
    else:
        model = load_model(model_path)
    population_path = tmp_path / f"{case_id}.population.json"
    population_path.write_text(json.dumps(population_doc), encoding="utf-8")
    return model, load_population(population_path, model=model)


def _normalize(offending: list[Any]) -> list[str]:
    """One comparable rendering per witness element, order-insensitive."""
    rendered: list[str] = []
    for element in offending:
        value = element if isinstance(element, (list, dict)) else [element]
        rendered.append(json.dumps(value, sort_keys=True, ensure_ascii=False))
    return sorted(rendered)


def _observe(case_id: str, tmp_path: Path) -> dict[str, Any]:
    model, population = _build(case_id, tmp_path)
    report = check(model, population)
    observed: dict[str, Any] = {"band": band(report)}
    ref = BUILD_BY_ID[case_id]["ref"]
    if ref is not None:
        verdict = next(v for v in report.verdicts if v.constraint_ref == ref)
        observed.update(
            scope_id=verdict.scope_id,
            verdict=verdict.verdict,
            reason_code=verdict.reason_code,
            witness=_normalize(verdict.offending_facts),
        )
        refusals = dict(getattr(report, "phase1_refusals", ()) or ())
        observed["refusal"] = refusals.get(ref)
    return observed


def _agrees(answer: dict[str, Any], observed: dict[str, Any]) -> list[str]:
    """Every field on which the answer and the observation differ."""
    findings: list[str] = []
    if "band" in answer and observed["band"] != answer["band"]:
        findings.append(f"band {observed['band']} != {answer['band']}")
    if "verdict" in observed:
        if observed["verdict"] != answer["verdict"]:
            findings.append(f"verdict {observed['verdict']} != {answer['verdict']}")
        if observed["reason_code"] != answer["reason_code"]:
            findings.append(f"reason {observed['reason_code']} != {answer['reason_code']}")
        if observed["witness"] != _normalize(answer["witness"]):
            findings.append(f"witness {observed['witness']} != {_normalize(answer['witness'])}")
        if "refusal" in answer and observed["refusal"] != answer["refusal"]:
            findings.append(f"refusal {observed['refusal']} != {answer['refusal']}")
    return findings


def _edit_count(before, after) -> int:
    """A scalar replacement or one inserted/deleted observation is one edit."""
    if type(before) is not type(after):
        return 1
    if isinstance(before, dict):
        common = before.keys() & after.keys()
        return len(before.keys() ^ after.keys()) + sum(
            _edit_count(before[k], after[k]) for k in common
        )
    if isinstance(before, list):
        if len(before) == len(after):
            return sum(_edit_count(a, b) for a, b in zip(before, after, strict=True))
        shorter, longer = (before, after) if len(before) < len(after) else (after, before)
        if len(longer) == len(shorter) + 1:
            return (
                1 if any(longer[:i] + longer[i + 1 :] == shorter for i in range(len(longer))) else 2
            )
        return 2
    return int(before != after)


@pytest.mark.parametrize("case_id", tuple(CASES["negative_controls"]))
def test_controlled_input_change_stops_accepting(case_id, tmp_path):
    model, population = _build(case_id, tmp_path, negative=True)
    report = check(model, population)
    verdict = next(v for v in report.verdicts if v.constraint_ref == CASE_BY_ID[case_id]["ref"])
    assert verdict.verdict == EXPECTED["negative_controls"][case_id], case_id


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_the_answer_holds_against_the_current_checker(case_id: str, tmp_path: Path) -> None:
    """The Phase 2 answer remains observable after the Phase 3 authority handoff.

    Historical ``production_disagreement`` blocks describe the retired
    evaluator and are retained as evidence; the current checker now agrees
    with the frozen semantic answer.  The two repr-order rows use Phase 3's
    separately approved canonical witness order.
    """
    answer = EXPECTED["answers"][case_id]
    observed = _observe(case_id, tmp_path)
    assert _agrees(answer, observed) == [], (case_id, observed)


def test_composition_rows_map_band_to_decision(tmp_path: Path) -> None:
    for case_id, answer in EXPECTED["answers"].items():
        if "decision" not in answer:
            continue
        observed = _observe(case_id, tmp_path)
        decision, _assurance = decide_phase1_assurance(
            band=observed["band"], applicable=0, current=0, in_scope=False
        )
        assert observed["band"] == answer["band"], case_id
        assert decision == answer["decision"], case_id


@pytest.mark.parametrize(
    ("case_id", "flip"),
    [
        ("P2-002", {"verdict": "pass"}),
        ("P2-013", {"witness": [[3]]}),
        ("P2-122", {"reason_code": "family-unimplemented"}),
        ("P2-193", {"band": 0}),
    ],
)
def test_one_change_to_an_answer_is_detected(
    case_id: str, flip: dict[str, Any], tmp_path: Path
) -> None:
    """The comparison's negative controls: a wrong answer must be caught."""
    answer = {**EXPECTED["answers"][case_id], **flip}
    assert _agrees(answer, _observe(case_id, tmp_path)) != []


def test_every_case_names_a_registered_branch() -> None:
    """INTENDED RED until specification section 5.3 lands."""
    try:
        from gnd import semantic_registry
    except ImportError as error:  # pragma: no cover - the intended RED path
        pytest.fail(
            "INTENDED RED -- the branch registry does not exist. Specification "
            "section 5.3 places REGISTRY, branch() and is_registered() in "
            f"src/gnd/semantic_registry.py, which is not importable: {error}"
        )
    unregistered = sorted(
        {
            row["scope_id"]
            for row in CASES["cases"]
            if not semantic_registry.is_registered(row["scope_id"])
        }
    )
    assert unregistered == [], unregistered
    ids = [entry.scope_id for entry in semantic_registry.REGISTRY]
    assert len(ids) == len(set(ids))
    assert not semantic_registry.is_registered("snapshot:invented:n-a:clean")
    for row in CASES["cases"]:
        assert semantic_registry.branch(row["scope_id"]).scope_id == row["scope_id"]


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_case_actually_reaches_its_declared_branch(case_id, tmp_path):
    from gnd import semantic_registry

    with semantic_registry.capture_branches() as reached:
        observed = _observe(case_id, tmp_path)
    scope_id = EXECUTION_ROUTES.get(case_id, CASE_BY_ID[case_id])["scope_id"]
    if case_id == "P2-084":
        scope_id = "snapshot:ring:reflexive:clean"
    elif case_id == "P2-163":
        scope_id = CASE_BY_ID[case_id]["scope_id"]
    assert scope_id in reached, (case_id, scope_id, reached)
    if scope_id.startswith("snapshot:") or (
        scope_id.startswith("applicability:") and not scope_id.startswith("applicability:refusal:")
    ):
        assert observed["scope_id"] == scope_id


@pytest.mark.parametrize("case_id", tuple(ROUTE_BY_ID))
def test_supplementary_execution_route(case_id, tmp_path):
    answer = ROUTE_EXPECTED["answers"][case_id]
    observed = _observe(case_id, tmp_path)
    assert {key: observed[key] for key in answer} == answer


def test_supplementary_answers_and_clean_control_are_closed(tmp_path):
    assert set(ROUTE_EXPECTED["answers"]) == set(ROUTE_BY_ID)
    clean = {
        key for key, answer in ROUTE_EXPECTED["answers"].items() if answer["verdict"] == "pass"
    }
    assert (
        clean == set(ROUTE_CASES["negative_controls"]) == set(ROUTE_EXPECTED["negative_controls"])
    )
    for case_id in clean:
        control = ROUTE_CASES["negative_controls"][case_id]
        model_doc, population_doc = _documents(case_id)
        document = model_doc if control["document"] == "model" else population_doc
        assert _edit_count(document, _apply(document, [control["patch"]])) == 1
        model, population = _build(case_id, tmp_path, negative=True)
        report = check(model, population)
        target = next(
            row for row in report.verdicts if row.constraint_ref == ROUTE_BY_ID[case_id]["ref"]
        )
        assert target.verdict == ROUTE_EXPECTED["negative_controls"][case_id]

