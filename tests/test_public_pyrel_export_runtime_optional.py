from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from test_public_pyrel_export_runtime_support import (
    ANSWERS,
    BASICS,
    POPULATION,
    REPO,
    assert_report,
    execute,
    export,
)

pytestmark = pytest.mark.pyrel_oracle

def inject_before_main(source: str, payload: str) -> str:
    """Mutate the real emitted artifact, never the assembled report data."""
    tree = ast.parse(source)
    guards = [i for i, node in enumerate(tree.body) if isinstance(node, ast.If)
              and any(isinstance(n, ast.Name) and n.id == "__name__"
                      for n in ast.walk(node.test))]
    assert len(guards) == 1, "a standalone artifact must have one main guard"
    index = guards[0]
    tree.body[index:index] = ast.parse(payload).body
    ast.fix_missing_locations(tree)
    return source[:source.index("# ///", 1) + len("# ///")] + "\n" + ast.unparse(tree) + "\n"


@pytest.mark.parametrize("fault", ["flip", "decline", "drop"])
def test_emitted_source_fault_reaches_comparator(tmp_path: Path, fault: str) -> None:
    program = export(tmp_path)
    population = REPO / "tests/fixtures/pyrel-oracle/population.basics_fail.yaml"
    expected = json.loads((ANSWERS / "basics_fail.report.json").read_text())
    control = tmp_path / "control.json"
    result = execute(program, population, control)
    assert result.returncode == 0, result.stderr
    assert_report(json.loads(control.read_text()), expected)
    payload = {
        "flip": 'PyrelOracle._decide = lambda self, rows: ("satisfied", [])',
        "decline": ('PyrelOracle.evaluate = lambda self, constraint, ft_id: '
                    '("unsupported", "seeded-decline")'),
        "drop": ('_original_evaluate_document = evaluate_document\n'
                 'def evaluate_document(*args, **kwargs):\n'
                 '    return _original_evaluate_document(*args, **kwargs)[:-1]\n'),
    }[fault]
    program.write_text(inject_before_main(program.read_text(), payload))
    dirty = tmp_path / "dirty.json"
    result = execute(program, population, dirty)
    assert result.returncode == 0, result.stderr
    with pytest.raises(AssertionError):
        assert_report(json.loads(dirty.read_text()), expected)


def test_error_rows_fail_execution_without_becoming_violations(tmp_path: Path) -> None:
    program = export(tmp_path)
    source = inject_before_main(program.read_text(),
                                'def _fault(*args, **kwargs):\n'
                                '    raise RuntimeError("seeded-evaluation-failure")\n'
                                'PyrelOracle.evaluate = _fault\n')
    program.write_text(source)
    out = tmp_path / "report.json"
    result = execute(program, POPULATION, out)
    assert result.returncode == 70, result.stderr
    rows = json.loads(out.read_text())["verdicts"]
    assert len(rows) == 7
    assert all(r["status"] == "error" and "seeded-evaluation-failure" in r["reason"] for r in rows)


@pytest.mark.parametrize("case,expected", [
    ("missing", 66), ("malformed", 3), ("mode", 64),
    ("occupied", 11), ("write", 70),
])
def test_program_exit_matrix(tmp_path: Path, case: str, expected: int) -> None:
    program = export(tmp_path)
    pop = tmp_path / "population.json"
    pop.write_bytes(POPULATION.read_bytes())
    out = tmp_path / "result.json"
    options = []
    if case == "missing":
        pop.unlink()
    elif case == "malformed":
        pop.write_text("[]")
    elif case == "mode":
        options = ["--mode", "unknown"]
    elif case == "occupied":
        out.write_text("owner bytes")
    else:
        # Non-directory parent is a real write error, independent of root/chmod.
        parent = tmp_path / "parent-file"
        parent.write_text("owner bytes")
        out = parent / "result.json"
    result = execute(program, pop, out, *options)
    assert result.returncode == expected, result.stderr
    assert "Traceback" not in result.stderr
    if case == "occupied":
        assert out.read_text() == "owner bytes"
    else:
        assert not out.exists()


def test_local_database_path_with_spaces(tmp_path: Path) -> None:
    program = export(tmp_path, BASICS, "--duckdb-path", str(tmp_path / "local database.duckdb"))
    out = tmp_path / "report.json"
    result = execute(program, POPULATION, out)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "local database.duckdb").is_file()
    assert_report(json.loads(out.read_text()), json.loads((ANSWERS / "basics_pass.report.json")
                                                        .read_text()))


@pytest.mark.parametrize("configured,expected", [(False, 66), (True, 64)])
def test_named_connection_is_an_explicit_unavailable_target(tmp_path: Path,
                                                           configured: bool,
                                                           expected: int) -> None:
    program = export(tmp_path, BASICS, "--connection", "warehouse")
    config = tmp_path / "connection config.yaml"
    if configured:
        config.write_text('connections:\n  warehouse:\n    type: snowflake\n')
    out = tmp_path / "report.json"
    result = execute(program, POPULATION, out, "--config", str(config))
    assert result.returncode == expected, result.stderr
    assert not out.exists()


def test_reference_identity_memberships(tmp_path: Path) -> None:
    from pyrel_export_support import CORPUS, require_export
    from ruamel.yaml import YAML

    require_export()
    document = YAML(typ="safe").load(BASICS.read_text())
    document["object_types"] = [
        {"id": "student", "kind": "entity", "name": "Student",
         "reference": {"mode": "popular", "value_type": "id_value"}},
        {"id": "teacher", "kind": "entity", "name": "Teacher",
         "reference": {"mode": "popular", "value_type": "id_value"}},
        {"id": "id_value", "kind": "value", "name": "Id", "primitive": "Integer"},
    ]
    document["fact_types"] = [
        {"id": "student_exists", "reading": "{Student} exists",
         "roles": [{"role_name": "student", "object_type": "student"}]},
        {"id": "teacher_exists", "reading": "{Teacher} exists",
         "roles": [{"role_name": "teacher", "object_type": "teacher"}]},
    ]
    document["constraints"] = [{
        "type": "cardinality", "scope": "object", "object_type": "student",
        "bound": {"min": 2, "max": 2}, "source": "explicit", "status": "confirmed",
        "modality": "alethic", "provenance": {"user_quote": "Exactly two students exist."},
    }]
    model = tmp_path / "identities.json"
    model.write_text(json.dumps(document))
    population = tmp_path / "identities-population.json"
    population.write_text(json.dumps({
        "population": {"model": "identities.json", "source": "fixture",
                       "covers": ["student_exists", "teacher_exists"]},
        "instances": {"student": [1, 1, 2], "teacher": [1]},
        "facts": {"student_exists": [{"student": 1}, {"student": 1}, {"student": 2}],
                  "teacher_exists": [{"teacher": 1}]},
    }))
    program = export(tmp_path, model)
    payload = (CORPUS / "identity_probe.py").read_text()
    payload += "\nprogram_main = install_identity_probe(program_main)\n"
    program.write_text(inject_before_main(program.read_text(), payload))
    result = execute(program, population, tmp_path / "report.json")
    assert result.returncode == 0, result.stderr

