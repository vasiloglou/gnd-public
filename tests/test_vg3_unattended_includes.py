"""VG3 (reviewed-vocabulary-growth): an unattended root that includes a reviewed vocabulary.

Issue 222. The spec is
``.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG3-spec.md``;
the test names are its section 8 rows. The fixture cases live in
``tests/vg3_cases.py``; T7 and T10 compare against outputs captured before
the first VG3 edit (``tests/fixtures/vg3/base-outputs.json``).
"""
from __future__ import annotations

import copy
import json
import tempfile
import time
from pathlib import Path

import pytest
import vg3_cases as cases
from support.cli_runner import run_main

from gnd.documents import ElementOrigin
from gnd.errors import ValidationIssue
from gnd.model import load_model, remap_issues
from gnd.model._unattended import _INCLUDED, _rule_unattended

BASE = json.loads((Path(__file__).parent / "fixtures" / "vg3" / "base-outputs.json").read_text())["outputs"]
ROOT_DOC = ("--document",)


def _documented(root: Path, *extra: str) -> tuple[int, str]:
    return cases.validate(root, "--document", str(root.parent / cases.DOC), "--require-documents", *extra)


def _issues(root: Path, *extra: str) -> tuple[int, list[tuple[str, str]]]:
    code, out = _documented(root, *extra, "--format", "json")
    payload = json.loads(out)
    return code, [(issue["rule_id"], issue["path"]) for issue in payload["issues"]]


def _span(quote: str) -> dict:
    return cases.span(quote)


def _owned_value(identifier: str, quote: str) -> dict:
    return {"id": identifier, "kind": "value", "primitive": "String", "provenance": {"spans": [_span(quote)]}}


def _inferred(**changes) -> dict:
    constraint = {"type": "mandatory", "role": "work", "source": "llm-inferred", "status": "proposed",
                  "modality": "deontic", "rationale": "r",
                  "provenance": {"rationale_world_fact": "w", "spans": [_span("Each version belongs to one work")]}}
    constraint.update(changes)
    return constraint


def _top_level(**changes) -> dict:
    """A top-level constraint the root owns: a value constraint on the included value type."""
    constraint = _inferred(**changes)
    constraint.pop("role")
    constraint.update(type="value", object_type="work", allowed=["w1"])
    return constraint


# --- T1: issue 222's root validates ------------------------------------------


def test_T1_issue_222_root_validates_with_its_documents(tmp_path):
    code, out = _documented(cases.write(tmp_path))
    assert code == 0, out
    assert out.endswith("OK: <case>/root.orm.json is a valid GND ORM model\n")


def test_T1_control_the_same_root_without_the_include_exemption_is_refused(tmp_path, monkeypatch):
    """The exemption is what admits it: with no origin set, U2-U5 fire on the included elements."""
    from gnd.model import _includes

    monkeypatch.setattr(_includes, "included_rows", lambda document, origins: frozenset())
    code, issues = _issues(cases.write(tmp_path))
    assert code == 3
    assert {rule for rule, _ in issues} == {f"semantic:unattended-u{n}" for n in (2, 3, 4, 5)}
    assert all(path.startswith("includes[seed]:") for _, path in issues), issues


# --- T2, T3: root-owned defects keep every rule -------------------------------


ROOT_DEFECTS = {
    "confirmed-constraint": ({"constraints": [_top_level(status="confirmed")]}, "semantic:unattended-u2"),
    "explicit-constraint": ({"constraints": [_top_level(source="explicit", status="confirmed",
                                                        provenance={"user_quote": "q",
                                                                    "spans": [_span("An author writes works")]})]},
                            "semantic:unattended-u3"),
    "object-type-without-span": ({"object_types": [{"id": "author", "kind": "value", "primitive": "String"}]},
                                 "semantic:unattended-u4"),
    "sample-row-without-span": ({"object_types": [_owned_value("author", "An author writes works")],
                                 "fact_types": [{"id": "author_writes_work", "reading": "{Author} writes {Work}",
                                                 "roles": [{"object_type": "author", "role_name": "author"},
                                                           {"object_type": "work", "role_name": "work"}],
                                                 "sample_population": [{"author": "a", "work": "w"}],
                                                 "provenance": {"spans": [_span("An author writes works")],
                                                                "sample_spans": []}}]},
                                "semantic:unattended-u6"),
    "undeclared-document": ({"object_types": [{"id": "author", "kind": "value", "primitive": "String",
                                               "provenance": {"spans": [dict(_span("An author writes works"),
                                                                             document_sha256="0" * 64)]}}]},
                            "semantic:unattended-u7"),
}


@pytest.mark.parametrize("name", sorted(ROOT_DEFECTS))
def test_T2_a_root_owned_defect_keeps_its_rule(tmp_path, name):
    own, rule = ROOT_DEFECTS[name]
    code, issues = _issues(cases.write(tmp_path, **own))
    assert code == 3
    assert rule in {r for r, _ in issues}, issues
    assert not any(path.startswith("includes[") for r, path in issues if r == rule), issues


def test_T2_a_confirmed_root_operation_keeps_U2_at_the_rule():
    """No include can carry an operation, so every operation is the root's (plan H32)."""
    doc = cases.root(b"x")
    doc["operations"] = [{"id": "op", "status": "confirmed", "source": "llm-inferred"}]
    rules = {issue.rule_id for issue in _rule_unattended(doc)}
    assert "semantic:unattended-u2" in rules


@pytest.mark.parametrize(("changes", "rule"), [
    ({"provenance": {"rationale_world_fact": "w"}}, "semantic:unattended-u5"),
    ({"source": "sample", "modality": "alethic",
      "provenance": {"sample_size": 1, "spans": [_span("Each version belongs to one work")]}},
     "semantic:unattended-u8"),
], ids=["U5", "U8"])
def test_T3_a_constraint_attached_to_an_included_fact_type_is_the_roots(tmp_path, changes, rule):
    attached = [{"fact_type": "work_has_version", "constraints": [_inferred(**changes)]}]
    code, issues = _issues(cases.write(tmp_path, fact_type_constraints=attached))
    assert code == 3
    assert (rule, "$.fact_type_constraints[0].constraints[0]") in issues, issues


# --- T4: what stays refused ----------------------------------------------------


def test_T4_an_included_file_with_the_mode_is_still_forbidden(tmp_path):
    seed = cases.seed()
    seed["source"] = {"kind": "prose", "mode": "unattended", "reviewer": "none",
                      "documents": [{"sha256": "0" * 64, "label": "x"}]}
    code, out = _documented(cases.write(tmp_path, seed_doc=seed))
    assert code == 3 and "include:forbidden-section" in out


def test_T4_the_seed_with_the_mode_on_itself_keeps_U2_to_U5(tmp_path):
    seed = cases.seed()
    seed["source"] = {"kind": "prose", "mode": "unattended", "reviewer": "none",
                      "documents": [{"sha256": cases.root(b"")["source"]["documents"][0]["sha256"], "label": "d"}]}
    tmp_path.mkdir(exist_ok=True)
    path = tmp_path / "seed-alone.orm.json"
    path.write_text(json.dumps(seed))
    (tmp_path / cases.DOC).write_text(cases.DOCUMENT)
    result = run_main(["validate", str(path), "--format", "json"])
    rules = {issue["rule_id"] for issue in json.loads(result.stdout)["issues"]}
    assert result.returncode == 3
    assert {f"semantic:unattended-u{n}" for n in (2, 3, 4, 5)} <= rules


# --- T5: spans an included element carries (D14 (a)) ------------------------


def _counted(root: Path) -> str:
    return cases.validate(root, "--require-documents")[1]


def test_T5_an_included_span_over_the_roots_document_is_counted_and_rehashed(tmp_path):
    root = cases.write(tmp_path, seed_doc=cases.spanned_seed())
    assert "4 of 4 source spans were not re-hashed" in _counted(root)  # counted
    code, out = _documented(root)
    assert code == 0, out  # re-hashed and matching


def test_T5_an_included_span_over_another_document_is_neither_checked_nor_counted(tmp_path):
    seed = cases.spanned_seed()
    for row in seed["object_types"]:
        row["provenance"]["spans"][0]["document_sha256"] = "1" * 64
    seed["object_types"][0]["provenance"]["spans"].append("not a span")
    seed["object_types"][1]["provenance"]["spans"].append({"document_sha256": 7})
    root = cases.write(tmp_path, seed_doc=seed)
    assert "2 of 2 source spans were not re-hashed" in _counted(root)
    code, out = _documented(root)
    assert code == 0, out


def test_T5_a_root_operation_span_is_not_counted(tmp_path):
    from gnd.model._unattended import _span_walk

    doc = cases.root(b"x")
    doc["operations"] = [{"id": "op", "provenance": {"spans": [_span("An author writes works")]}}]
    assert _span_walk(doc, {})[1].total == 0


@pytest.mark.parametrize("with_document", [True, False], ids=["document", "no-document"])
def test_T5_a_malformed_included_span_over_the_roots_document_is_U7(tmp_path, with_document):
    seed = cases.spanned_seed()
    seed["object_types"][0]["provenance"]["spans"][0]["end"] = seed["object_types"][0]["provenance"]["spans"][0]["start"]
    root = cases.write(tmp_path, seed_doc=seed)
    argv = ("--document", str(root.parent / cases.DOC)) if with_document else ()
    code, out = cases.validate(root, *argv, "--format", "json")
    issues = [(i["rule_id"], i["path"]) for i in json.loads(out)["issues"]]
    assert code == 3
    assert ("semantic:unattended-u7", "includes[seed]:$.object_types[id=work].provenance.spans[0]") in issues, issues


# --- T6: the attribution line -------------------------------------------------


def test_T6_the_attribution_line_names_the_include_and_its_counts(tmp_path):
    root = cases.write(tmp_path)
    code, out = _documented(root)
    digest = json.loads(root.read_text())["includes"][0]["sha256"]
    assert code == 0
    assert out.splitlines() == [
        (f"INCLUDE seed sha256={digest}: 2 object types, 1 fact types, 0 sample rows, 1 constraints "
         "(1 confirmed, 1 alethic, 1 explicit or user-supplied), 0 deontic notes"),
        "OK: <case>/root.orm.json is a valid GND ORM model",
    ]


def test_T6_json_output_carries_no_attribution(tmp_path):
    code, out = _documented(cases.write(tmp_path), "--format", "json")
    assert code == 0 and "INCLUDE" not in out and "attribution" not in out


# --- T7, T10: outputs equal the base -----------------------------------------


@pytest.fixture(scope="module")
def observed():
    with tempfile.TemporaryDirectory() as scratch:
        return cases.observations(Path(scratch).resolve())


@pytest.mark.parametrize("name", sorted(k for k in BASE if not k.startswith("h30")))
def test_T7_models_without_the_mode_are_byte_identical(observed, name):
    code, out = observed[name]
    assert (code, out) == (BASE[name]["exit"], BASE[name]["stdout"])


@pytest.mark.parametrize("name", sorted(k for k in BASE if k.startswith("h30")))
def test_T10_a_root_that_0_4_0_validates_keeps_its_output(observed, name):
    code, out = observed[name]
    base = BASE[name]
    assert code == base["exit"]
    if name.endswith(":json") or code != 0:
        assert out == base["stdout"]
    else:  # text, exit 0: the attribution line is the only new output
        lines = out.splitlines(keepends=True)
        assert lines[0].startswith("INCLUDE seed sha256=") and "".join(lines[1:]) == base["stdout"]


# --- T8: remapping an included object type -----------------------------------


def test_T8_remap_issues_maps_an_included_object_type_selector():
    origins = (ElementOrigin("model", "$.object_types[0]", "$.object_types[0]", "own"),
               ElementOrigin("includes[seed]", "$.object_types[1]", "$.object_types[0]", "work"))
    issues = [ValidationIssue(path="$.object_types[id=work].provenance.spans[0]", message="m", rule_id="r"),
              ValidationIssue(path="$.object_types[id=own]", message="m", rule_id="r")]
    assert [i.path for i in remap_issues(issues, origins)] == [
        "includes[seed]:$.object_types[id=work].provenance.spans[0]", "$.object_types[id=own]"]


# --- T9: U8 inside an include (D13 (a)) --------------------------------------


@pytest.mark.parametrize(("status", "expected"), [("proposed", 3), ("confirmed", 0)])
def test_T9_an_unconfirmed_inferred_alethic_included_constraint_is_U8(tmp_path, status, expected):
    seed = cases.seed()
    seed["fact_types"][0]["constraints"].append({
        "type": "mandatory", "role": "work", "source": "llm-inferred", "status": status, "modality": "alethic",
        "rationale": "r", "provenance": {"rationale_world_fact": "w"}})
    code, out = _documented(cases.write(tmp_path, seed_doc=seed), "--format", "json")
    issues = [(i["rule_id"], i["path"]) for i in json.loads(out)["issues"]]
    assert code == expected, issues
    if expected:
        assert issues == [("semantic:unattended-u8", "includes[seed]:$.fact_types[id=work_has_version].constraints[1]")]


# --- T11: span-walk diagnostics under the include ------------------------------


@pytest.mark.parametrize("fmt", ["text", "json"])
def test_T11_an_included_span_with_a_wrong_excerpt_digest_is_reported_under_the_include(tmp_path, fmt):
    seed = cases.spanned_seed()
    seed["object_types"][0]["provenance"]["spans"][0]["excerpt_sha256"] = "2" * 64
    root = cases.write(tmp_path, seed_doc=seed)
    code, out = cases.validate(root, "--document", str(root.parent / cases.DOC), "--format", fmt)
    assert code == 3
    assert "includes[seed]:$.object_types[id=work].provenance.spans[0]" in out
    assert "unattended:excerpt-mismatch" in out


# --- T12: the pages -------------------------------------------------------------


def test_T12_the_pages_state_the_include_rule_in_one_home():
    page = (Path(__file__).resolve().parents[1]
            / "src/gnd/skills/gnd-orm-core/references/representation-format.md").read_text()
    unattended = page[page.index("## Unattended source"):page.index("## `rejected_proposals`")]
    includes = page[page.index("## Model includes (version 5)"):page.index("### Extraction flattening record")]
    assert "### An unattended root that includes a reviewed model" in unattended
    assert "INCLUDE <id> sha256=" in unattended
    assert "[Unattended source](#unattended-source)" in includes


# --- T13: the layer is linear --------------------------------------------------


def test_T13_validate_on_a_large_include_stays_within_the_bound(tmp_path):
    seed = cases.seed()
    seed["object_types"] += [{"id": f"x{i}", "kind": "value", "primitive": "String"} for i in range(1000)]
    seed["fact_types"] += [{"id": f"f{i}", "reading": f"{{X{i}}} pairs with {{X{(i + 1) % 1000}}}",
                            "roles": [{"object_type": f"x{i}", "role_name": "a"},
                                      {"object_type": f"x{(i + 1) % 1000}", "role_name": "b"}]}
                           for i in range(1000)]
    root = cases.write(tmp_path, seed_doc=seed)
    started = time.perf_counter()
    code, out = _documented(root)
    elapsed = time.perf_counter() - started
    assert code == 0, out[:400]
    assert elapsed < 10, elapsed


def test_the_origin_set_is_reset_after_validation(tmp_path):
    load_model(cases.write(tmp_path))
    assert _INCLUDED.get() == frozenset()
    assert copy.copy(_INCLUDED.get()) == frozenset()


# --- review round 1 (notes/reviews/phase-VG3-r1), regression cases ----------


def test_R1_F1_sample_spans_are_read_on_included_fact_types_only(tmp_path):
    """F1: U7 read sample_spans on an included object type, where no rule read them before."""
    seed = cases.spanned_seed()
    bad = dict(_span("A work is a published piece"))
    bad["end"] = bad["start"]
    seed["object_types"][0]["provenance"]["sample_spans"] = [{"row": 0, "span": bad}]
    root = cases.write(tmp_path, seed_doc=seed)
    code, out = _documented(root)
    assert code == 0, out
    assert "4 of 4 source spans were not re-hashed" in cases.validate(root, "--require-documents")[1]


def test_R1_F2_an_identifier_with_a_newline_keeps_its_include_prefix(tmp_path):
    """F2: the selector pattern stopped at a newline, so the issue lost includes[seed]:."""
    seed = cases.spanned_seed()
    seed["object_types"][0]["id"] = "work\n"
    seed["fact_types"][0]["roles"][0]["object_type"] = "work\n"
    seed["object_types"][0]["provenance"]["spans"][0]["excerpt_sha256"] = "2" * 64
    root = cases.write(tmp_path, seed_doc=seed)
    code, out = cases.validate(root, "--document", str(root.parent / cases.DOC), "--format", "json")
    paths = [issue["path"] for issue in json.loads(out)["issues"]]
    assert code == 3
    assert paths == ["includes[seed]:$.object_types[id=work\n].provenance.spans[0]"], paths


@pytest.mark.parametrize("identifier", ["a]b", "a", "x[id=y]"])
def test_R1_F2_remap_matches_the_whole_declared_identifier(identifier):
    origins = (ElementOrigin("includes[seed]", "$.object_types[0]", "$.object_types[0]", "a"),
               ElementOrigin("includes[seed]", "$.object_types[1]", "$.object_types[1]", identifier))
    issue = ValidationIssue(path=f"$.object_types[id={identifier}].provenance", message="m", rule_id="r")
    assert remap_issues([issue], origins)[0].path == f"includes[seed]:$.object_types[id={identifier}].provenance"
