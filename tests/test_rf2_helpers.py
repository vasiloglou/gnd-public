"""RF2 structural and behavior controls, separate from frozen RF1 answers."""
from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import TypeAdapter, ValidationError

from gnd import artifacts, cli, exits, model
from gnd.exp import conclusions, spec
from gnd.extract import manifest
from gnd.review import request

ROOT = Path(__file__).resolve().parents[1]
MILESTONE = ROOT / ".gnd-planning/milestones/code-refactoring"
GROUPS = {
    "f4d89086": "sha256_hex",
    "2f5a20a1": "canonical_report_text",
    "5bebc70e": "reject_json_constant",
    "d9f0cf8e": "reject_json_duplicate_pairs",
    "dcbdd645": "reject_json_duplicate_pairs_result",
}
EXIT_VALUES = {
    "EXIT_GENERATOR": 5, "EXIT_QUARANTINE": 6, "EXIT_CHECKER_DEFECT": 6,
    "EXIT_DRIFT": 10, "EXIT_COLLISION": 11, "EXIT_NO_INSTALL": 12,
    "EXIT_MODEL_CODE_DRIFT": 13, "EXIT_SESSION_NOT_ACCEPTED": 15,
    "EXIT_REVIEW_INCONCLUSIVE": 16, "EXIT_EVOLUTION_OPERATIONS_GATED": 18,
}


def signature_hash(node):
    node = ast.parse(ast.unparse(node)).body[0]
    node.name = "_"
    if (node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
        node.body = node.body[1:]
    return hashlib.sha256(ast.dump(node).encode()).hexdigest()


def group_counts(sources):
    references = json.loads((ROOT / "tests/fixtures/rf2-pins/group-bodies.json").read_text())
    runtime_hashes = {signature_hash(ast.parse(row["body"]).body[0]): prefix
                      for prefix, row in references.items()}
    counts = dict.fromkeys(GROUPS, 0)
    for source in sources:
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.FunctionDef):
                prefix = runtime_hashes.get(signature_hash(node))
                if prefix in counts:
                    counts[prefix] += 1
    return counts


def assert_one_definition(sources):
    counts = group_counts(sources)
    assert counts == dict.fromkeys(GROUPS, 1), counts


def test_one_definition_per_promoted_group():
    sources = [p.read_text() for p in (ROOT / "src/gnd").rglob("*.py")
               if "skills" not in p.parts and "examples" not in p.parts]
    assert_one_definition(sources)
    for name in GROUPS.values():
        assert callable(getattr(artifacts, name))


def test_known_dirty_duplicate_fails():
    source = inspect.getsource(artifacts)
    assert_one_definition([source])
    duplicate = inspect.getsource(artifacts.sha256_hex).replace("def sha256_hex", "def duplicate")
    with pytest.raises(AssertionError):
        assert_one_definition([source, duplicate])


@pytest.mark.parametrize("hook", [artifacts.reject_json_duplicate_pairs,
                                  artifacts.reject_json_duplicate_pairs_result])
def test_strict_hook_variants_and_outer_errors(hook):
    assert hook([]) == {}
    assert hook([("a", 1), ("b", {"c": 2})]) == {"a": 1, "b": {"c": 2}}
    with pytest.raises(ValueError, match="^duplicate JSON key 'a'$" ):
        hook([("a", 1), ("a", 2)])
    with pytest.raises(ValueError, match="^duplicate JSON key 'a'$" ):
        json.loads('{"z":{"a":1,"a":2}}', object_pairs_hook=hook)
    assert artifacts.reject_json_duplicate_pairs is not artifacts.reject_json_duplicate_pairs_result


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_strict_constant_refusals(token):
    with pytest.raises(ValueError, match=f"^non-finite JSON number {token!r} is forbidden$"):
        artifacts.reject_json_constant(token)


@pytest.mark.parametrize("value", ["a" * 64, b"a" * 64, "A" * 64, "a" * 63,
                                   "sha256:" + "a" * 64, None, 0, "a" * 64 + "\n"])
def test_digest_type_variants_preserved(value):
    baseline = TypeAdapter(artifacts.Sha256)
    for path in ("gnd.recovery.report", "gnd.exp.session_eval", "gnd.exp.session_store"):
        alias = importlib.import_module(path).Sha256
        assert alias is artifacts.Sha256
        try:
            expected = baseline.validate_python(value)
        except ValidationError:
            with pytest.raises(ValidationError):
                TypeAdapter(alias).validate_python(value)
        else:
            assert TypeAdapter(alias).validate_python(value) == expected
    if isinstance(value, bytes):
        assert baseline.validate_python(value) == value.decode()
        with pytest.raises(ValidationError):
            TypeAdapter(request.Sha256).validate_python(value)


def validation_error():
    return ValidationError.from_exception_data("RF2", [
        {"type": "string_type", "loc": (), "input": 0},
        {"type": "int_parsing", "loc": ("cases", 1, "count"), "input": "bad"},
        {"type": "missing", "loc": ("tail",), "input": {}},
    ])


def test_issue_conversion_preserves_order_and_rule_id():
    error = validation_error()
    for rule_id in ("rf2:first", "rf2:second"):
        converted = model.issues_from_validation_error(error, rule_id)
        assert [x.model_dump() for x in converted] == [
            {"path": ".".join(map(str, entry["loc"])), "message": entry["msg"],
             "rule_id": rule_id, "severity": "error"} for entry in error.errors()]
        assert manifest._validation_issues(error, rule_id) == converted
    assert spec._validation_issues(error) == model.issues_from_validation_error(error, spec.SPEC_RULE_ID)
    assert conclusions._validation_issues(error) == model.issues_from_validation_error(error, conclusions.CONCLUSIONS_RULE_ID)


def test_all_exit_allocations_have_one_home_and_old_aliases():
    for name, value in EXIT_VALUES.items():
        assert getattr(exits, name) == getattr(cli, name) == value
        assert name in exits.__all__
    complete = {**EXIT_VALUES, "EXIT_OK": 0, "EXIT_ILL_FORMED": 3,
                "EXIT_USAGE": 64, "EXIT_NO_INPUT": 66, "EXIT_INTERNAL": 70,
                "EXIT_IO": 74, "EXIT_EXPERIMENT_OPEN": 14, "EXIT_WALK_HALTED": 17}
    assert {name: value for name, value in vars(exits).items() if name.startswith("EXIT_")} == complete
    assert exits.EXIT_OK == 0
    assert exits.EXIT_ILL_FORMED == 3
    allocations = []
    for path in (ROOT / "src/gnd").rglob("*.py"):
        if "skills" in path.parts or "examples" in path.parts:
            continue
        tree = ast.parse(path.read_text())
        imported = {alias.asname or alias.name for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module == "gnd.exits"
                    for alias in node.names}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and target.id.startswith(("EXIT_", "_EXIT_")):
                        if isinstance(node.value, ast.Name) and node.value.id in imported:
                            continue  # Only aliases from the actual allocation home.
                        if target.id == "_EXIT_PRECEDENCE" and isinstance(node.value, ast.Dict):
                            continue  # Existing priority ordering, not an integer code.
                        allocations.append((path.relative_to(ROOT).as_posix(), target.id))
    assert allocations and {path for path, name in allocations} == {"src/gnd/exits.py"}


def test_three_digest_renames_preserve_meaning_and_inputs(tmp_path):
    from gnd import transition
    from gnd.conformance import currency
    from gnd.synth import provenance
    source = ROOT / "tests/fixtures/models/full_vocabulary.orm.yaml"
    loaded = model.load_model(source)
    assert currency.model_digest is currency.model_file_sha256
    assert currency.model_file_sha256(source) == hashlib.sha256(source.read_bytes()).hexdigest()
    altered = tmp_path / "model.yaml"
    altered.write_bytes(source.read_bytes() + b"\n")
    assert currency.model_file_sha256(altered) != currency.model_file_sha256(source)
    assert provenance.model_digest is provenance.validated_model_sha256
    assert transition.model_digest is transition.transition_model_identity
    assert provenance.validated_model_sha256(loaded) == importlib.import_module("gnd.population")._model_digest(loaded)
    assert transition.transition_model_identity(loaded) == "sha256:" + provenance.validated_model_sha256(loaded)
    # A changed renamed function must affect the consumer's actual lookup.
    from gnd.conformance import service
    assert service.model_digest is currency.model_file_sha256
    assert "model_file_sha256(model_path)" in inspect.getsource(service.run_conformance)


def resolve(name):
    module_name, symbol = name.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), symbol)


def test_shim_inventory_covers_moves_and_patch_effects():
    text = (MILESTONE / "notes/shim-inventory.md").read_text()
    rows = [line.split("|")[1:5] for line in text.splitlines() if line.startswith("| gnd.") and line.split("|")[3].strip() == "RF2"]
    assert len(rows) == 34
    for old, new, phase, retirement in rows:
        old, new = old.strip(), new.strip().split(" (")[0]
        assert phase.strip() == "RF2" and retirement.strip() == "RF-D5"
        before, after = resolve(old), resolve(new)
        if old in {"gnd.exp.spec._validation_issues", "gnd.exp.conclusions._validation_issues"}:
            assert callable(before) and callable(after)
        else:
            assert before is after or before == after
    for name in EXIT_VALUES:
        assert f"| gnd.cli.{name} |" in text
    for name in GROUPS.values():
        assert name in text or name == "reject_json_constant"


def test_diverged_encoder_source_unchanged():
    rows = json.loads((ROOT / "tests/fixtures/rf2-pins/variant-encoders.json").read_text())
    assert len(rows) == 14
    for row in rows:
        source = (ROOT / row["path"]).read_text()
        moved = {("src/gnd/extract/anchors.py", "_canonical"): "gnd.anchors",
                 ("src/gnd/transition.py", "_canonical"): "gnd.values"}
        if (row["path"], row["name"]) in moved:
            source = inspect.getsource(getattr(importlib.import_module(moved[(row["path"], row["name"])]), row["name"]))
        found = [node for node in ast.walk(ast.parse(source))
                 if isinstance(node, ast.FunctionDef) and node.name == row["name"]]
        assert len(found) == 1
        raw = ast.get_source_segment(source, found[0]).encode()
        assert hashlib.sha256(raw).hexdigest() == row["sha256"], row


def test_affected_scan_scopes_cover_moved_definitions():
    # Observe the actual retained guards rather than constructing their scope.
    import test_measure_offline as scans
    original = Path.read_text
    visited = set()
    def observe(path, *args, **kwargs):
        visited.add(path)
        return original(path, *args, **kwargs)
    with patch.object(Path, "read_text", observe):
        scans.test_no_network_library_is_reachable_from_the_measure_lane()
        assert {ROOT / "src/gnd/artifacts.py", ROOT / "src/gnd/model.py"} <= visited
        visited.clear()
        scans.test_no_provider_client_anywhere_in_the_package()
        assert {ROOT / "src/gnd" / name for name in
                ("artifacts.py", "model.py", "exits.py", "checker.py", "verbalize.py")} <= visited
    # Imported dependency closure is tested by test_measure_offline; here pin
    # the absence of dynamic evaluators in the moved helper bodies themselves.
    for function in [getattr(artifacts, name) for name in GROUPS.values()]:
        nodes = ast.walk(ast.parse(inspect.getsource(function)))
        assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                       and n.func.id in {"eval", "exec", "compile"} for n in nodes)
