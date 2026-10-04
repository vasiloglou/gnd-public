"""Test-only observation/matching of the separately authored Phase 4 answers.

This does not compute transition semantics, publish proof evidence, or modify
production. Population bytes are interpreted only by the production loader.
"""

from __future__ import annotations

import atexit
import contextlib
import copy
import datetime
import gzip
import hashlib
import inspect
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from test_public_transition_walks import CORPUS as WALK_CORPUS

import gnd
from gnd import checker, transition
from gnd.cli import main
from gnd.model import ModelValidationError, load_model
from gnd.population import load_population
from gnd.report import build_transition_payload, legacy_report_projection
from gnd.semantic_registry import capture_branches


def _materialize():
    packed = (Path(__file__).parent / "fixtures/public-phase4-transition/tables.json.gz").read_bytes()
    assert len(packed) <= 16384
    assert hashlib.sha256(packed).hexdigest() == "c2ea8bb5a9857c19c0dc45b34cd59508d3fc99bd9f2145b2db6993faeedebd33"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(131073)
    assert len(raw) <= 131072
    assert hashlib.sha256(raw).hexdigest() == "1255b59024cf17e1186ca2d518c9753746f0f3c3aed3bf83cf4753dd32b7fd32"
    tables = json.loads(raw)
    assert set(tables) == {"cases.json", "expected.json"}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-phase4-transition-")
    root = Path(temporary.name).resolve()
    corpus = root / "tests/fixtures/v6-transition-correspondence"
    corpus.mkdir(parents=True)
    for name, text in tables.items():
        (corpus / name).write_text(text, encoding="utf-8")
    base = root / "tests/fixtures/transition/expense"
    base.mkdir(parents=True)
    shutil.copyfile(WALK_CORPUS / "v2_expense.orm.yaml", base / "v2_expense.orm.yaml")
    for directory in (WALK_CORPUS / "walks").iterdir():
        target = base / "walks" / directory.name
        target.mkdir(parents=True)
        for member in ("pre.pop.yaml", "post.pop.yaml", "steps.json"):
            shutil.copyfile(directory / member, target / member)
    schema = root / "src/gnd/schema/orm-meta.schema.json"
    schema.parent.mkdir(parents=True)
    shutil.copyfile(Path(gnd.__file__).resolve().parent / "schema/orm-meta.schema.json", schema)
    return temporary, root, corpus

_TEMPORARY, ROOT, CORPUS = _materialize()
atexit.register(_TEMPORARY.cleanup)
CASES = json.loads((CORPUS / "cases.json").read_text())["cases"]
BY_ID = {case["id"]: case for case in CASES}
ANSWERS = json.loads((CORPUS / "expected.json").read_text())["cases"]
FAMILIES = (
    "pre_snapshot",
    "pre_snapshot_verdicts",
    "steps",
    "frame_grading",
    "frame_verdicts",
    "post_snapshot",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(case):
    case = BY_ID[case["base"]] if "base" in case else case
    refs = case["inputs"]
    result = {}
    for key, ref in refs.items():
        path = ROOT / ref["path"]
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError("input path escaped repository")
        if sha(path) != ref["sha256"]:
            raise ValueError(f"stale fixture: {ref['path']}")
        result[key] = path
    return result


def primitive_model(primitive, tmp_path):
    """A fully loaded, shape-valid test model, not model_construct bypass."""
    document = {
        "version": 2,
        "object_types": [{"id": "value", "name": "Value", "kind": "value", "primitive": primitive}],
        "fact_types": [
            {
                "id": "recorded",
                "reading": "{Value} is recorded",
                "roles": [{"object_type": "value", "role_name": "value"}],
            }
        ],
        "operations": [
            {
                "id": "record",
                "reading": "Record {Value}",
                "parameters": [{"name": "value", "object_type": "value"}],
                "effects": [{"assert": {"fact_type": "recorded", "bind": {"value": "$value"}}}],
                "frame": {"modality": "alethic"},
                "source": "explicit",
                "status": "confirmed",
                "provenance": {"fixture": "Phase 4"},
            }
        ],
    }
    path = tmp_path / "model.json"
    path.write_text(json.dumps(document))
    return load_model(path)


def refusal(error, model_path="<fixture>"):
    payload = build_transition_payload(
        3, model_path, evaluated=False, issues=error.issues, supplied_digests=error.supplied
    )
    return {
        "exit": 3,
        "payload": payload,
        "issues": [{"rule_id": i.rule_id, "path": i.path} for i in error.issues],
    }


def materialize_walk(case, tmp_path):
    """Materialize one walk recipe so evidence and observation share exact inputs."""
    paths = inputs(case)
    if "post_fact_patch" in case:
        model = load_model(paths["model"])
        post = load_population(paths["post"], model=model)
        facts = copy.deepcopy(post.facts)
        change = case["post_fact_patch"]
        assert facts[change["fact_type"]][change["index"]][change["role"]] == change["before"]
        facts[change["fact_type"]][change["index"]][change["role"]] = change["after"]
        doc = {
            "population": {
                "model": post.model,
                "model_id": post.model_id,
                "source": "fixture",
                "covers": post.covers,
            },
            "facts": facts,
            "instances": post.instances,
        }
        paths["post"] = tmp_path / "post.json"
        paths["post"].write_text(json.dumps(doc))
    if "step_binding_patch" in case:
        doc = json.loads(paths["steps"].read_text())
        bindings = doc["steps"][0]["bindings"]
        for key in case["step_binding_patch"]["remove"]:
            bindings.pop(key, None)
        bindings.update(case["step_binding_patch"]["set"])
        paths["steps"] = tmp_path / "steps.json"
        paths["steps"].write_text(json.dumps(doc))
    return paths


def observe_walk(case, tmp_path):
    paths = materialize_walk(case, tmp_path)
    kwargs = {}
    if case.get("injection") == "intermediate-loader-refusal":
        kwargs["load_population_bytes"] = lambda *a, **k: (_ for _ in ()).throw(
            ValueError("injected intermediate loader refusal")
        )
    out, err = io.StringIO(), io.StringIO()
    injection = patch.multiple(transition, **kwargs) if kwargs else contextlib.nullcontext()
    with (
        capture_branches() as seen,
        injection,
        contextlib.redirect_stdout(out),
        contextlib.redirect_stderr(err),
    ):
        code = main(
            [
                "check",
                str(paths["model"]),
                "--pre",
                str(paths["pre"]),
                "--post",
                str(paths["post"]),
                "--steps",
                str(paths["steps"]),
                "--format",
                "json",
            ]
        )
    payload = json.loads(out.getvalue())
    doc = json.loads(paths["steps"].read_text())
    supplied = {
        k: doc.get(k) if isinstance(doc, dict) else None
        for k in ("model_digest", "operations_digest", "pre_digest")
    }
    return {
        "exit": code,
        "payload": payload,
        "branches": sorted(seen),
        "supplied": supplied,
        "issues": [{"rule_id": i["rule_id"], "path": i["path"]} for i in payload.get("issues", [])],
    }


def observe_order(case):
    paths = inputs(case)
    model = load_model(paths["model"])
    pre = load_population(paths["pre"], model=model)
    post = load_population(paths["post"], model=model)
    steps = transition.read_steps_document(paths["steps"])["steps"]
    events, position = [], [0]
    real_check = transition.check

    def check(m, p):
        events.append("pre" if p is pre else "post" if p is post else f"snapshot:{position[0]}")
        return real_check(m, p)

    def wrap(name, label, positional_index=None):
        real = getattr(transition, name)

        def call(*args, **kwargs):
            if positional_index is None:
                events.append(label)
            else:
                position[0] = args[positional_index]
                events.append(f"{label}:{position[0]}")
            return real(*args, **kwargs)

        return call

    with patch.multiple(
        transition,
        check=check,
        _compiled_verdicts=wrap("_compiled_verdicts", "compiled"),
        _evaluate_step=wrap("_evaluate_step", "step", 0),
        _load_intermediate=wrap("_load_intermediate", "reload", 3),
        _frame_verdicts=wrap("_frame_verdicts", "frame"),
    ):
        transition.evaluate(model, pre, post, steps)
    return {"events": events}


def observe_compat(case, tmp_path):
    paths = inputs(case)
    model = load_model(paths["model"])
    raw = model.model_dump(exclude={"warnings"})
    mode = case["mode"]
    if mode == "namespace":
        raw["operations"][0]["id"] = raw["object_types"][0]["id"]
    elif mode in {"stripped", "v1", "empty"}:
        raw.pop("operations")
        if mode == "v1":
            raw["version"] = 1
        elif mode == "empty":
            raw["operations"] = []
    elif mode == "permutation":
        for op in raw["operations"]:
            op["effects"] = list(reversed(op["effects"]))
    else:
        raise ValueError(mode)
    path = tmp_path / "model.json"
    path.write_text(json.dumps(raw))
    try:
        other = load_model(path)
    except ModelValidationError as error:
        return {"exit": 3, "rule_ids": [i.rule_id for i in error.issues]}
    pre = load_population(paths["pre"], model=model)
    alt_pre = load_population(paths["pre"], model=other)
    if mode in {"stripped", "v1", "empty"}:
        return {
            "snapshot_equal": checker.check(model, pre).model_dump()
            == checker.check(other, alt_pre).model_dump(),
            "same_version_model_digest_equal": transition.model_digest(model)
            == transition.model_digest(other),
            "operations_digest_equal": transition.operations_digest(model.operations)
            == transition.operations_digest(other.operations),
        }
    steps = transition.read_steps_document(paths["steps"])["steps"]
    a = transition.evaluate(model, pre, load_population(paths["post"], model=model), steps)
    b = transition.evaluate(other, alt_pre, load_population(paths["post"], model=other), steps)

    def semantic(value):
        if isinstance(value, dict):
            return {k: semantic(v) for k, v in value.items() if k not in {"message", "locator"}}
        return [semantic(v) for v in value] if isinstance(value, list) else value

    return {
        "exit": transition.band(b),
        "semantic_equal": semantic(a.model_dump()) == semantic(b.model_dump()),
    }


def _observe(case, tmp_path):
    kind = case["kind"]
    if kind == "walk":
        return observe_walk(case, tmp_path)
    if kind == "order":
        return observe_order(case)
    if kind == "compat":
        return observe_compat(case, tmp_path)
    if kind == "dispatch":
        schema = json.loads((ROOT / "src/gnd/schema/orm-meta.schema.json").read_text())
        ref = schema["$defs"]["dynamic_rule"]["properties"]["op"]["$ref"]
        return {
            "operators": sorted(transition._COMPARISONS),
            "schema_operators": sorted(schema["$defs"][ref.removeprefix("#/$defs/")]["enum"]),
        }
    if kind in {"binding", "comparison"}:
        model = primitive_model(case["primitive"], tmp_path)
        values = [case["value"]] if kind == "binding" else [case["old"], case["new"]]
        for value in values:
            try:
                transition.validate_steps(
                    {"steps": [{"op": "record", "bindings": {"value": value}}]}, model
                )
            except transition.TransitionLoadError as error:
                return refusal(error)
        if kind == "binding":
            return {"exit": 0}
        try:
            return {"holds": transition._compare_values(case["operator"], case["new"], case["old"])}
        except transition.UnknownComparisonError:
            return {"raises": "UnknownComparisonError"}
    if kind == "canonical":
        value = (
            {1: "a"}
            if case["recipe"] == "nonstring-key"
            else {1}
            if case["recipe"] == "set"
            else datetime.date(2026, 9, 13)
        )
        try:
            return {"value": transition._canonical(value, "$.operations")}
        except transition.TransitionLoadError as error:
            return refusal(error)
    if kind == "reader":
        recipe, value = case["recipe"], case["value"]
        path = tmp_path / "steps.json"
        raw = None
        if recipe == "hex":
            raw = bytes.fromhex(value)
        elif recipe == "text":
            raw = value.encode()
        elif recipe in {"repeat-space", "repeat-nine"}:
            raw = (b" " if recipe == "repeat-space" else b"9") * value
        elif recipe == "nested-array":
            raw = b"[" * value + b"0" + b"]" * value
        elif recipe != "missing":
            raise ValueError(recipe)
        if raw is not None:
            path.write_bytes(raw)
        prior_limit = sys.getrecursionlimit()
        try:
            if recipe == "nested-array":
                sys.setrecursionlimit(1000)
            transition.read_steps_document(path)
        except transition.TransitionLoadError as error:
            result = refusal(error)
            for issue in result["issues"]:
                if issue["path"] == str(path):
                    issue["path"] = "@steps"
            return result
        finally:
            sys.setrecursionlimit(prior_limit)
        return {"exit": 0}
    raise ValueError(f"unknown case kind: {kind}")


def observe(case, tmp_path):
    sites = set()
    real_refuse, real_issue = transition._refuse, transition.ValidationIssue

    def refuse(*args, **kwargs):
        sites.add(inspect.currentframe().f_back.f_lineno)
        return real_refuse(*args, **kwargs)

    def issue(*args, **kwargs):
        caller = inspect.currentframe().f_back
        if caller.f_code.co_filename == transition.__file__ and caller.f_code.co_name != "_refuse":
            sites.add(caller.f_lineno)
        return real_issue(*args, **kwargs)

    with patch.multiple(transition, _refuse=refuse, ValidationIssue=issue):
        result = _observe(case, tmp_path)
    result["emission_sites"] = sorted(sites)
    return result


def verdicts(block, wanted):
    """Reuse the established golden matcher without copying its answer key."""
    from test_transition_corpus import _candidates

    return _candidates(block, wanted)


def assert_answer(actual, expected):
    from test_transition_corpus import _matches

    for key in (
        "exit",
        "holds",
        "raises",
        "value",
        "snapshot_equal",
        "same_version_model_digest_equal",
        "operations_digest_equal",
        "semantic_equal",
        "events",
    ):
        if key in expected:
            assert actual.get(key) == expected[key], (
                f"{key}: {actual.get(key)!r} != {expected[key]!r}"
            )
    if "operators" in expected:
        assert actual["operators"] == actual["schema_operators"] == expected["operators"]
    if "issues" in expected:
        assert actual["issues"] == expected["issues"], "exact admission issue mismatch"
    if "rule_id" in expected:
        assert expected["rule_id"] in actual["rule_ids"]
    payload = actual.get("payload")
    if payload is None:
        return
    if payload["schema_version"] == 7:
        version = 6 if payload.get("derivations") is not None else 5
        payload = legacy_report_projection(payload, version)
    block = payload["transition"]
    assert payload["population"] is None
    assert all(k in block for k in FAMILIES)
    assert "assurance" not in payload and "assurance_level" not in block
    if actual["exit"] == 3:
        assert block["evaluated"] is False
        assert all(block[k] is None for k in FAMILIES)
    else:
        assert block["evaluated"] is True
    if "supplied" in actual:
        assert {k: block[k] for k in actual["supplied"]} == actual["supplied"]
    for wanted in expected.get("must", []):
        if "issue" in wanted:
            assert wanted["issue"] in [i["rule_id"] for i in payload["issues"]]
        elif "frame_grading" in wanted:
            assert any(
                all(g.get(k) == v for k, v in wanted["frame_grading"].items())
                for g in block["frame_grading"]
            )
        else:
            assert any(_matches(v, wanted) for v in verdicts(block, wanted)), (
                f"missing verdict: {wanted}"
            )
    for unwanted in expected.get("must_not", []):
        assert not any(_matches(v, unwanted) for v in verdicts(block, unwanted)), (
            f"forbidden verdict: {unwanted}"
        )
    for wanted in expected.get("exact_verdicts", []):
        selected = [{k: v[k] for k in wanted} for v in verdicts(block, wanted)]
        assert wanted in selected, f"exact witness/identity mismatch: {wanted}"


def corrupt_answer(expected):
    """One-field negative control on the matcher, never a production proof."""
    wrong = copy.deepcopy(expected)
    for key in ("exit", "holds", "value", "events", "operators", "snapshot_equal", "raises"):
        if key in wrong:
            wrong[key] = {"deliberately": "wrong"}
            return wrong
    raise ValueError("no discriminating expected field")
