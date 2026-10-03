














from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

from gnd.cli import main
from gnd.conformance.structural import check_structural, expected_surface
from gnd.model import load_model

CORPUS = Path(__file__).parent / "fixtures" / "phase3-consumers"


def _generate(out: Path) -> None:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.chdir(CORPUS):
        code = main(["codegen", "eligibility.orm.yaml", "--out", str(out)])
    assert code == 0, stdout.getvalue()


def _run_conformance(model: Path, project: Path) -> tuple[int, dict]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        code = main(["conformance", str(model), str(project), "--format", "json"])
    return int(code), json.loads(stdout.getvalue())


def test_expected_surface_omits_structured_derived_fact_types() -> None:


    model = load_model(CORPUS / "eligibility.orm.yaml")
    tools, findings = expected_surface(model)
    assert findings == ()
    assert [tool.fact_type_id for tool in tools] == ["book_listed", "book_blocked"]


def test_a_regenerated_structured_project_conforms_at_zero(tmp_path: Path) -> None:


    project = tmp_path / "project"
    _generate(project)
    code, payload = _run_conformance(CORPUS / "eligibility.orm.yaml", project)
    assert code == 0, payload.get("findings")
    assert payload["findings"] == []
    satisfied = sorted(row["fact_type_id"] for row in payload["satisfied"])
    assert satisfied == ["book_blocked", "book_listed"]


def test_a_missing_asserted_tool_still_reds(tmp_path: Path) -> None:


    project = tmp_path / "project"
    _generate(project)
    tools_path = project / "eligibility" / "tools.py"
    source = tools_path.read_text(encoding="utf-8")
    mutated = source.replace("def book_listed(book):", "def book_listed_gone(book):")
    assert mutated != source
    tools_path.write_text(mutated, encoding="utf-8")

    model = load_model(CORPUS / "eligibility.orm.yaml")
    result = check_structural(
        model, project, model_path=CORPUS / "eligibility.orm.yaml"
    )
    kinds = {finding.kind for finding in result.findings}
    assert "fact-type-unimplemented" in kinds
    targets = {
        finding.target
        for finding in result.findings
        if finding.kind == "fact-type-unimplemented"
    }
    assert targets == {"book_listed"}


def test_a_constructor_present_for_a_computed_fact_type_reds(tmp_path: Path) -> None:


    project = tmp_path / "project"
    _generate(project)
    tools_path = project / "eligibility" / "tools.py"
    source = tools_path.read_text(encoding="utf-8")
    tools_path.write_text(
        source + "\n\ndef book_is_eligible(book):\n    return {'book': book}\n",
        encoding="utf-8",
    )

    model = load_model(CORPUS / "eligibility.orm.yaml")
    result = check_structural(
        model, project, model_path=CORPUS / "eligibility.orm.yaml"
    )
    constructed = [
        finding
        for finding in result.findings
        if finding.kind == "derived-fact-type-constructed"
    ]
    assert [finding.target for finding in constructed] == ["book_is_eligible"]
    assert "tools.py" in constructed[0].message
    assert not any(
        finding.kind == "orphan-tool-symbol" and finding.target == "book_is_eligible"
        for finding in result.findings
    )


def test_an_extension_file_constructor_for_a_computed_fact_type_reds(
    tmp_path: Path,
) -> None:


    project = tmp_path / "project"
    _generate(project)
    helper = project / "helpers.py"
    helper.write_text(
        "def book_is_eligible(book):\n    return {'book': book}\n", encoding="utf-8"
    )

    model = load_model(CORPUS / "eligibility.orm.yaml")
    result = check_structural(
        model, project, model_path=CORPUS / "eligibility.orm.yaml"
    )
    constructed = [
        finding
        for finding in result.findings
        if finding.kind == "derived-fact-type-constructed"
    ]
    assert [finding.target for finding in constructed] == ["book_is_eligible"]
    assert "helpers.py" in constructed[0].message


def test_a_sanitized_collision_does_not_red_the_asserted_constructor(
    tmp_path: Path,
) -> None:






    model_text = """\
version: 1
model_id: urn:gnd-fixture:phase3-consumers:collision@1
source: { kind: text-conversation, confidence: standard, mode: one-shot }
object_types:
  - { id: item, name: Item, kind: value, primitive: String }
fact_types:
  - id: import_
    reading: "{Item} is imported"
    roles: [{ object_type: item, role_name: item }]
  - id: import
    reading: "{Item} is auto-imported"
    roles: [{ object_type: item, role_name: item }]
    derivation: derived
    derivation_rule:
      body: [{ fact_type: import_, bind: { item: "$i" } }]
      head: { item: "$i" }
constraints: []
rejected_proposals: []
"""
    model_path = tmp_path / "collision.orm.yaml"
    model_path.write_text(model_text, encoding="utf-8")
    out = tmp_path / "generated"
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.chdir(tmp_path):
        code = main(["codegen", "collision.orm.yaml", "--out", str(out)])
    assert code == 0, stdout.getvalue()
    tools = (out / "collision" / "tools.py").read_text(encoding="utf-8")
    assert "def import_(item):" in tools

    model = load_model(model_path)
    result = check_structural(model, out, model_path=model_path)
    assert not any(
        finding.kind == "derived-fact-type-constructed" for finding in result.findings
    ), [finding.message for finding in result.findings]
    assert [row.fact_type_id for row in result.satisfied] == ["import_"]
