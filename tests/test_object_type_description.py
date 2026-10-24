"""IK1: optional object-type descriptions (induced-knowledge milestone).

Spec: .gnd-planning/milestones/induced-knowledge/notes/phase-IK1-spec.md. Test
ids T1-T14 are that spec's section 8; IK1-D6 is its gate amendment (section 12).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS = REPO_ROOT / "tests" / "fixtures" / "models"
LIBRARY = MODELS / "library.orm.yaml"
BASELINE = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik1-baseline.json"
EVOLUTION_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "phase4_reference" / "evolution.json"
L = 4096
MARKER = "ZZ-EXTRA-MARKER-7f3a"
HOSTILE = "'" + "'''" + "\n" + " " + "\\"


def _library_document() -> dict[str, Any]:
    return YAML(typ="safe").load(LIBRARY.read_text(encoding="utf-8"))


def _write_model(tmp_path: Path, description: Any, *, name: str = "model.orm.yaml") -> Path:
    """The library fixture with ``description`` on its first object type.

    JSON is a YAML subset, so the model is written as JSON and every value is
    exactly the Python value given.
    """
    document = _library_document()
    document["object_types"][0]["description"] = description
    path = tmp_path / name
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return path


def _write_yaml_description(tmp_path: Path, line: str) -> Path:
    """Insert one raw YAML ``description:`` line, for values JSON cannot spell."""
    lines = LIBRARY.read_text(encoding="utf-8").splitlines(keepends=True)
    index = next(i for i, text in enumerate(lines) if text.strip() == "name: Borrower")
    lines.insert(index + 1, f"    {line}\n")
    path = tmp_path / "raw.orm.yaml"
    path.write_text("".join(lines), encoding="utf-8")
    return path


def _validate_exit(path: Path, capsys: pytest.CaptureFixture[str]) -> int:
    from gnd.cli import main

    code = main(["validate", str(path)])
    capsys.readouterr()
    return code


# --- T1 schema twins ---------------------------------------------------------


def test_t1_description_defs_exist_in_both_schema_twins() -> None:
    for path in (
        REPO_ROOT / "src" / "gnd" / "schema" / "orm-meta.schema.json",
        REPO_ROOT / "src" / "gnd" / "skills" / "gnd-orm-core" / "references" / "orm-meta.schema.json",
    ):
        schema = json.loads(path.read_text(encoding="utf-8"))
        description = schema["$defs"]["object_type"]["properties"]["description"]
        assert description["required"] == ["summary"]
        assert set(description["properties"]) == {"summary", "row", "source", "notes"}
        assert schema["$defs"]["description_text"]["maxLength"] == L
        assert "description_extra" in schema["$defs"]


# --- T2 boundary exits -------------------------------------------------------


EVERY_JSON_EXTRA = {
    "summary": "s",
    "text": "t",
    "number": 1.5,
    "integer": 7,
    "flag": False,
    "nothing": None,
    "list": [1, "two", None, {"three": [3]}],
    "nested": {"a": {"b": [True]}},
}


@pytest.mark.parametrize(
    "description",
    [
        {"summary": "x"},
        {key: "y" * L for key in ("summary", "row", "source", "notes")},
        EVERY_JSON_EXTRA,
    ],
    ids=["summary-of-one", "all-core-at-cap", "extras-of-every-json-type"],
)
def test_t2_accepted_descriptions_exit_0(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], description: Any
) -> None:
    assert _validate_exit(_write_model(tmp_path, description), capsys) == 0


@pytest.mark.parametrize(
    "description",
    [
        "A string description (the r3 form).",
        {},
        {"row": "no summary"},
        {"summary": ""},
        {"summary": 3},
        {"summary": "s", "notes": "n" * (L + 1)},
    ],
    ids=["string", "empty-object", "missing-summary", "empty-summary", "non-string-summary", "notes-over-cap"],
)
def test_t2_refused_descriptions_exit_3(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], description: Any
) -> None:
    assert _validate_exit(_write_model(tmp_path, description), capsys) == 3


@pytest.mark.parametrize(
    "line",
    [
        "description: {summary: s, when: 2026-10-24T10:00:00Z}",
        "description: {summary: s, deep: {a: [1, 2026-10-24]}}",
        "description: {summary: s, n: .nan}",
        "description: {summary: s, deep: [.inf]}",
        "description: {summary: s, n: -.inf}",
    ],
    ids=["timestamp", "nested-date", "nan", "nested-inf", "negative-inf"],
)
def test_t2_ik1_d6_values_without_a_json_form_exit_3(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], line: str
) -> None:
    # IK1-D6 (owner, 2026-10-24): exit 3, as for any typed field at B.
    assert _validate_exit(_write_yaml_description(tmp_path, line), capsys) == 3


def test_t2_non_finite_numbers_outside_descriptions_are_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The IK1-D6 screen is scoped to descriptions; elsewhere B's behaviour holds.
    from gnd.model._validation import _layer1_structural

    document = _library_document()
    document["object_types"][0]["precision"] = float("nan")
    assert [issue.rule_id for issue in _layer1_structural(document)] == ["jsonschema:type"]
    assert "non-finite" not in _layer1_structural(document)[0].message


# --- T3-T6, T14 renderers ----------------------------------------------------


def _renders(path: Path) -> tuple[str, str, str]:
    from gnd.codegen.docstrings import tool_docstring
    from gnd.model import load_model
    from gnd.model_verbalization import render_model_verbalization
    from gnd.vocabulary import render_verbalization

    model = load_model(path)
    fact_types = [
        fact
        for fact in model.fact_types
        if any(role.get("object_type") == "borrower" for role in fact.get("roles") or [])
    ]
    docstrings = "\n".join(tool_docstring(model, fact) for fact in fact_types)
    return render_model_verbalization(path), render_verbalization(model), docstrings


def _borrower_sentence(verbalization: str) -> str:
    """The prose part of the borrower line, before its machine fields."""
    line = next(text for text in verbalization.splitlines() if text.startswith("[object-type:borrower]"))
    return line.split(" reference=", 1)[0].split(" canonical=", 1)[0]


@pytest.mark.parametrize(
    "text",
    ["p" * L, ("'\n " * L)[:L]],
    ids=["plain-at-cap", "escapable-at-cap"],
)
def test_t3_core_keys_render_in_full(tmp_path: Path, text: str) -> None:
    from gnd.verbalize import neutralize_text

    description = {key: text for key in ("summary", "row", "source", "notes")}
    verbalization, vocabulary, docstrings = _renders(_write_model(tmp_path, description))
    escaped = neutralize_text(text)
    sentence = _borrower_sentence(verbalization)
    for label in ("Description", "Row", "Source", "Notes"):
        assert f" {label}: '{escaped}'." in sentence
        assert f"  {label}: '{escaped}'" in vocabulary
    assert f" — {escaped}" in docstrings
    for rendered in (sentence, vocabulary, docstrings):
        assert "more characters)" not in rendered


def test_t4_codegen_docstring_carries_summary_inside_delimiter(tmp_path: Path) -> None:
    from gnd.cli import main

    model = _write_model(tmp_path, {"summary": "Holds a library card."})
    out = tmp_path / "project"
    assert main(["codegen", "--out", str(out), str(model)]) == 0
    tools = next(out.rglob("tools.py")).read_text(encoding="utf-8")
    docstring = re.search(r"'''(.*?)'''", tools[tools.index("Borrower (String) — Holds") - 400 :], re.DOTALL)
    assert docstring is not None
    assert "Borrower (String) — Holds a library card." in docstring.group(1)


def test_t5_hostile_core_value_cannot_break_delimiters_or_forge_lines(tmp_path: Path) -> None:
    hostile = (HOSTILE * L)[:L]
    description = {"summary": hostile, "notes": hostile}
    plain_verbalization, plain_vocabulary, plain_docstrings = _renders(
        _write_model(tmp_path, {"summary": "s", "notes": "n"}, name="plain.orm.yaml")
    )
    verbalization, vocabulary, docstrings = _renders(_write_model(tmp_path, description))
    # Line structure is the renderer's: the hostile value adds no line.
    assert len(verbalization.splitlines()) == len(plain_verbalization.splitlines())
    assert len(vocabulary.splitlines()) == len(plain_vocabulary.splitlines())
    assert len(docstrings.splitlines()) == len(plain_docstrings.splitlines())
    assert "'''" not in docstrings
    for rendered in (verbalization, vocabulary, docstrings):
        assert " " not in rendered
    # Every quote the value contributed is escaped, so only the renderer's own
    # delimiters remain unescaped in the borrower sentence.
    sentence = _borrower_sentence(verbalization)
    assert len(re.findall(r"(?<!\\)'", sentence.replace("\\\\", ""))) == 4


def test_t6_vocabulary_has_core_key_lines_and_stays_constraint_blind(tmp_path: Path) -> None:
    from gnd.model import load_model
    from gnd.vocabulary import render_verbalization

    path = _write_model(tmp_path, {"summary": "A card holder.", "source": "Branch intake form."})
    text = render_verbalization(load_model(path))
    block = text.split("=== Object Types ===\n", 1)[1].split("\n\n", 1)[0].splitlines()
    borrower = next(i for i, line in enumerate(block) if line.startswith("Borrower "))
    assert block[borrower + 1 : borrower + 3] == ["  Description: 'A card holder.'", "  Source: 'Branch intake form.'"]
    # Non-regression guards only (spec T6): the projection is unchanged by a
    # description and inside its allowlist, and an added constraint still
    # leaves the vocabulary text unchanged.
    from gnd.extract.projection import audit_allowlist, project

    schema = project(load_model(path))
    assert audit_allowlist(schema) == []
    assert schema == project(load_model(LIBRARY))
    document = json.loads(path.read_text(encoding="utf-8"))
    document["fact_types"][0].setdefault("constraints", []).append(
        {"type": "mandatory", "role": document["fact_types"][0]["roles"][0]["role_name"],
         "source": "explicit", "status": "confirmed", "modality": "alethic",
         "provenance": {"user_quote": "Injected."}}
    )
    constrained = tmp_path / "constrained.orm.yaml"
    constrained.write_text(json.dumps(document), encoding="utf-8")
    assert render_verbalization(load_model(constrained)) == text


def test_t14_extras_are_carried_but_never_rendered_as_prose(tmp_path: Path) -> None:
    from gnd.model import load_model

    path = _write_model(tmp_path, {"summary": "s", "marker": MARKER, "nested": {"m": [MARKER]}})
    verbalization, vocabulary, docstrings = _renders(path)
    assert MARKER not in _borrower_sentence(verbalization)
    assert MARKER not in vocabulary
    assert MARKER not in docstrings
    line = next(text for text in verbalization.splitlines() if text.startswith("[object-type:borrower]"))
    assert MARKER in line.split(" canonical=", 1)[1]
    loaded = load_model(path).object_types[0]["description"]
    assert loaded["marker"] == MARKER and loaded["nested"] == {"m": [MARKER]}


# --- T13 neutralizer identity ------------------------------------------------


@pytest.mark.parametrize(
    "value",
    ["", "plain", "it's", "a\\b", "line\nbreak", "\r\t\x00\x1f\x7f\x85", "  ", "x" * 512, "'" * 300, "y" * 5000, 42, None],
)
def test_t13_neutralize_is_capped_neutralize_text(value: Any) -> None:
    from gnd.verbalize import MAX_RENDERED_VALUE_CHARS, _neutralize, neutralize_text

    full = neutralize_text(value)
    expected = full
    if len(full) > MAX_RENDERED_VALUE_CHARS:
        expected = f"{full[:MAX_RENDERED_VALUE_CHARS]}… (+{len(full) - MAX_RENDERED_VALUE_CHARS} more characters)"
    assert _neutralize(value) == expected


# --- T8, T10, T11 diff and digest --------------------------------------------


def _diff(tmp_path: Path, before: Any, after: Any, *extra: str) -> tuple[int, dict[str, Any]]:
    left = _write_model(tmp_path, before, name="left.orm.yaml") if before is not None else LIBRARY
    right = _write_model(tmp_path, after, name="right.orm.yaml") if after is not None else LIBRARY
    process = subprocess.run(
        [sys.executable, "-m", "gnd", "diff", "--format", "json", *extra, str(left), str(right)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": "0"},
        check=False,
    )
    return process.returncode, json.loads(process.stdout)


def _diff_schema() -> dict[str, Any]:
    return json.loads((REPO_ROOT / "src" / "gnd" / "diff.schema.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("before", "after"),
    [
        (None, {"summary": "added"}),
        ({"summary": "old"}, {"summary": "new"}),
        ({"summary": "removed"}, None),
        ({"summary": "same", "extra": 1}, {"summary": "same", "extra": 2}),
    ],
    ids=["add", "change", "remove", "extra-only"],
)
def test_t8_description_only_diff_is_v2_with_one_annotation(tmp_path: Path, before: Any, after: Any) -> None:
    identical_exit, identical = _diff(tmp_path, None, None)
    assert identical["schema_version"] == "gnd-diff/1"
    assert "annotations" not in identical
    code, payload = _diff(tmp_path, before, after)
    assert code == identical_exit
    assert payload["schema_version"] == "gnd-diff/2"
    assert payload["annotations"] == [{"object_type": "borrower", "before": before, "after": after}]
    Draft202012Validator(_diff_schema()).validate(payload)
    # Applied redaction (the default mode) passes annotations through unedited.
    assert {key: value for key, value in payload.items() if key not in {"schema_version", "annotations", "model_a_digest", "model_b_digest"}} == {
        key: value for key, value in identical.items() if key not in {"schema_version", "model_a_digest", "model_b_digest"}
    }


def test_t8_diff_schema_refuses_mismatched_version_and_annotations() -> None:
    validator = Draft202012Validator(_diff_schema())
    process = subprocess.run(
        [sys.executable, "-m", "gnd", "diff", "--format", "json", str(LIBRARY), str(LIBRARY)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    v1 = json.loads(process.stdout)
    annotation = [{"object_type": "borrower", "before": None, "after": {"summary": "s"}}]
    assert validator.is_valid(v1)
    assert not validator.is_valid({**v1, "schema_version": "gnd-diff/2"})
    assert not validator.is_valid({**v1, "annotations": annotation})
    assert not validator.is_valid({**v1, "schema_version": "gnd-diff/2", "annotations": []})
    assert validator.is_valid({**v1, "schema_version": "gnd-diff/2", "annotations": annotation})


def test_t10_embedded_diff_schema_matches_its_source() -> None:
    report = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text(encoding="utf-8"))
    embedded = report["$defs"]["diff_reference_report"]
    source = _diff_schema()
    strip = lambda schema: {key: value for key, value in schema.items() if key not in {"$id", "title"}}
    assert strip(embedded) == strip(source)
    payload = {
        "schema_version": "gnd-diff/2", "command": "diff",
        "model_a_digest": "sha256:" + "0" * 64, "model_b_digest": "sha256:" + "1" * 64,
        "vocabulary_digest": "2" * 64, "seed": 0, "assurance": "none",
        "entailment": [], "populations": [], "not_derivable": [],
        "annotations": [{"object_type": "borrower", "before": {"summary": "a"}, "after": None}],
    }
    Draft202012Validator(embedded).validate(payload)


def test_t11_vocabulary_digest_ignores_descriptions(tmp_path: Path) -> None:
    from gnd.anchors import vocabulary_digest
    from gnd.extract.anchors import vocabulary_digest as extract_vocabulary_digest
    from gnd.model import load_model

    # Intended consequence (D11): the digest no longer identifies the rendered
    # vocabulary text, so an extraction sidecar stays bound when only a
    # description changes.
    plain = vocabulary_digest(load_model(LIBRARY))
    described = load_model(_write_model(tmp_path, {"summary": "s", "extra": {"x": [1]}}))
    assert vocabulary_digest(described) == plain
    assert extract_vocabulary_digest(described) == plain
    document = _library_document()
    document["object_types"][0]["name"] = "Renamed"
    renamed = tmp_path / "renamed.orm.yaml"
    renamed.write_text(json.dumps(document), encoding="utf-8")
    assert vocabulary_digest(load_model(renamed)) != plain


# --- T12 RF1 mutation anchor -------------------------------------------------


def test_t12_diff_schema_mutation_anchor_still_matches_once() -> None:
    mutations = json.loads((REPO_ROOT / "tests" / "fixtures" / "rf1-pins" / "mutations.json").read_text(encoding="utf-8"))
    row = next(item for item in mutations["rows"] if item["id"] == "M-SEM-diff-schema")
    source = (REPO_ROOT / row["file"]).read_text(encoding="utf-8")
    assert source.count(row["old"]) == 1


# --- T9 evolve surface -------------------------------------------------------


def _evolution_preview(tmp_path: Path, describe: bool) -> dict[str, Any]:
    from gnd.artifacts import sha256_hex
    from gnd.cli import main
    from gnd.evolve import (
        CommittedText,
        ElementLocator,
        EvolutionOperation,
        EvolutionOperationAudit,
        EvolutionOperationKind,
        EvolutionProposal,
    )

    fixture = json.loads(EVOLUTION_FIXTURE.read_text(encoding="utf-8"))
    case = next(row for row in fixture["cases"] if row["name"] == "evolution-safe-additive")
    before_text = case["inputs"]["before_model"]["text"]
    before = json.loads(before_text)
    candidate = json.loads(before_text)
    target = candidate["object_types"][0]
    if describe:
        target["description"] = {"summary": "One unit of tracked work.", "origin": "fixture"}
    else:
        target["name"] = "Task"
    candidate_text = json.dumps(candidate, separators=(",", ":"), ensure_ascii=False) + "\n"
    workspace = tmp_path.resolve() / "workspace"
    workspace.mkdir()
    model = workspace / "model.orm.yaml"
    model.write_text(before_text, encoding="utf-8")
    proposal = EvolutionProposal(
        proposal_id="proposal-description",
        expected_model_sha256=sha256_hex(before_text.encode("utf-8")),
        candidate_model=CommittedText.from_text(candidate_text, media_type="application/yaml"),
        operations=(
            EvolutionOperation(
                operation_id="modify-work-item",
                kind=EvolutionOperationKind.MODIFY,
                locator=ElementLocator(collection="object_types", element_id=target["id"]),
                before=before["object_types"][0],
                after=target,
            ),
        ),
        rationale="Describe what one work item is.",
        audit=EvolutionOperationAudit(
            actor_id="owner:fixture",
            origin="ik1-test",
            requested_at=datetime(2026, 10, 24, 12, 0, tzinfo=UTC),
        ),
    )
    proposal_path = workspace / "proposal.json"
    proposal_path.write_text(
        json.dumps(proposal.model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    preview = workspace / "review" / "preview.json"
    argv = [
        "evolve", "preview", str(model), str(proposal_path),
        "--workspace", str(workspace), "--records", str(workspace / "records"),
        "--out", str(preview), "--format", "json",
    ]
    assert main(argv) == 0
    return json.loads(preview.read_text(encoding="utf-8"))


def _entries(preview: Any) -> list[dict[str, Any]]:
    found = []
    pending = [preview]
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            if "surface" in value and "reference" in value:
                found.append(value)
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
    return found


def test_t9_description_change_is_an_annotation_surface(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from gnd.evolve.models import BlastRadiusEntry

    preview = _evolution_preview(tmp_path, describe=True)
    capsys.readouterr()
    annotations = [entry for entry in _entries(preview) if entry["surface"] == "annotation"]
    assert [entry["reference"] for entry in annotations] == ["object_types[work_item].description"]
    assert annotations[0]["change"] == "added"
    BlastRadiusEntry.model_validate(annotations[0])


def test_t9_model_without_descriptions_lists_no_annotation_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    preview = _evolution_preview(tmp_path, describe=False)
    capsys.readouterr()
    assert _entries(preview)
    assert not [entry for entry in _entries(preview) if entry["surface"] == "annotation"]


# --- T7 base-commit byte identity --------------------------------------------


def _run(argv: list[str]) -> tuple[int, bytes]:
    env = {**os.environ, "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "0"}
    process = subprocess.run(argv, cwd=REPO_ROOT, env=env, capture_output=True, check=False)
    return process.returncode, process.stdout


def _sha(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def _capture(stem: str) -> dict[str, str]:
    """Rows 1-6 of the IK1 spec section 6 table, normalized as declared."""
    fixture = f"tests/fixtures/models/{stem}.orm.yaml"
    gnd = [sys.executable, "-m", "gnd"]
    rows: dict[str, str] = {}
    rows["1"] = _sha(_run([sys.executable, "-c", "from gnd.model_verbalization import render_model_verbalization as r; import sys; sys.stdout.write(r(sys.argv[1]))", fixture])[1])
    rows["2"] = _sha(_run([sys.executable, "-c", "from gnd.model import load_model; from gnd.vocabulary import render_verbalization as r; import sys; sys.stdout.write(r(load_model(sys.argv[1])))", fixture])[1])
    with tempfile.TemporaryDirectory() as raw:
        temp = str(Path(raw).resolve())
        assert _run([*gnd, "extract", "--out", f"{temp}/x", fixture])[0] == 0
        rows["3"] = _sha((Path(temp) / "x" / f"{stem}.projection.schema.json").read_bytes())
        assert _run([*gnd, "codegen", "--out", f"{temp}/p", fixture])[0] == 0
        rows["4"] = _sha((Path(temp) / "p" / ".gnd-codegen.json").read_bytes().replace(temp.encode(), b"<T>"))
        code, out = _run([*gnd, "conformance", "--format", "json", fixture, f"{temp}/p"])
        assert code == 0
        out = re.sub(rb'("gnd_version"\s*:\s*)"[^"]*"', rb'\1"<V>"', out.replace(temp.encode(), b"<T>"))
        rows["5"] = _sha(out)
    rows["6"] = _sha(_run([*gnd, "diff", "--format", "json", fixture, fixture])[1])
    return rows


@pytest.mark.parametrize("stem", ["full_vocabulary", "library", "keywords", "v2_worked_example"])
def test_t7_outputs_without_descriptions_equal_the_base_commit(stem: str) -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert baseline["base_commit"] == "1d6eee0"
    assert _capture(stem) == baseline["sha256"][stem]


def test_t7_evolve_preview_equals_the_base_commit(tmp_path: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    import test_model_evolution as evolution

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    temp = tmp_path.resolve()
    paths = evolution._write_cli_workspace(temp, case_name="evolution-safe-additive")
    code, _ = _run([sys.executable, "-m", "gnd", *evolution._preview_argv(paths)])
    assert code == 0
    data = Path(paths["preview"]).read_bytes().replace(str(temp).encode(), b"<T>")
    assert _sha(data) == baseline["sha256"]["evolve_preview"]
