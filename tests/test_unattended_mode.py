"""MG5: the unattended source mode and gnd validate --document.

Spec: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG5-spec.md
(§Tests T1-T11). Fixture: tests/fixtures/unattended/conforming.orm.yaml, an
unattended model meeting every rule, and its source document source.txt.
Each refusing case is a one-key edit of the conforming model.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import time
import unicodedata
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "unattended"
CONFORMING = FIXTURES / "conforming.orm.yaml"
SOURCE = FIXTURES / "source.txt"
EVOLVE_BASE = REPO_ROOT / "tests" / "fixtures" / "evolve-policy" / "base.orm.yaml"


def _doc(path: Path = CONFORMING) -> dict[str, Any]:
    return YAML(typ="safe").load(path.read_text(encoding="utf-8"))


def _write(document: dict[str, Any], path: Path) -> Path:
    buffer = io.StringIO()
    YAML().dump(document, buffer)
    path.write_text(buffer.getvalue(), encoding="utf-8")
    return path


def _validate(document: dict[str, Any], tmp_path: Path, *extra: str) -> tuple[int, list[str], dict[str, Any]]:
    path = _write(document, tmp_path / "model.orm.yaml")
    result = run_main(["validate", str(path), "--format", "json", *extra])
    payload = json.loads(result.stdout)
    return result.returncode, [issue["rule_id"] for issue in payload.get("issues") or []], payload


def _fact(document: dict[str, Any], fact_type_id: str = "order_placed_by_customer") -> dict[str, Any]:
    return next(item for item in document["fact_types"] if item["id"] == fact_type_id)


def _constraint(document: dict[str, Any], source: str) -> dict[str, Any]:
    return next(c for c in _fact(document)["constraints"] if c["source"] == source)


def _object(document: dict[str, Any], object_type_id: str = "customer") -> dict[str, Any]:
    return next(item for item in document["object_types"] if item["id"] == object_type_id)


def _span(phrase: str, raw: bytes | None = None) -> dict[str, Any]:
    raw = SOURCE.read_bytes() if raw is None else raw
    text = unicodedata.normalize("NFC", raw.decode("utf-8"))
    start = text.index(phrase)
    end = start + len(phrase)
    return {"document_sha256": hashlib.sha256(raw).hexdigest(), "start": start, "end": end,
            "excerpt_sha256": hashlib.sha256(text[start:end].encode("utf-8")).hexdigest()}


# --- T1: the schema --------------------------------------------------------------


def test_t1_schema_twins_and_the_conforming_model(tmp_path: Path) -> None:
    canonical = REPO_ROOT / "src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json"
    shipped = REPO_ROOT / "src/gnd/schema/orm-meta.schema.json"
    assert canonical.read_bytes() == shipped.read_bytes()
    definition = json.loads(canonical.read_text(encoding="utf-8"))["$defs"]["source_span"]
    assert definition["required"] == ["document_sha256", "start", "end", "excerpt_sha256"]
    assert definition["additionalProperties"] is False
    exit_code, rule_ids, _payload = _validate(_doc(), tmp_path)
    assert (exit_code, rule_ids) == (0, [])


def test_t1b_spans_on_an_induced_constraint_pass_layer_one(tmp_path: Path) -> None:
    """D3: the closed induced provenance admits `spans`; a bad span there is refused by the schema."""
    document = _doc(EVOLVE_BASE)
    induced = next(c for c in document["constraints"] if c.get("source") == "induced")
    induced["provenance"]["spans"] = [_span("customers")]
    (tmp_path / "ok").mkdir()
    assert _validate(document, tmp_path / "ok")[0] == 0
    for bad in ({**_span("customers"), "extra": 1}, {**_span("customers"), "start": -1},
                {**_span("customers"), "excerpt_sha256": "a" * 63}):
        induced["provenance"]["spans"] = [bad]
        (tmp_path / "bad").mkdir(exist_ok=True)
        exit_code, rule_ids, _payload = _validate(document, tmp_path / "bad")
        assert exit_code == 3 and rule_ids and not any(r.startswith("semantic:unattended") for r in rule_ids)


# --- T2: one case per branch -------------------------------------------------------


def _edit(fn: Callable[[dict[str, Any]], None]) -> Callable[[], dict[str, Any]]:
    def build() -> dict[str, Any]:
        document = _doc()
        fn(document)
        return document
    return build


def _pop(mapping: dict[str, Any], key: str) -> None:
    mapping.pop(key)


BRANCHES: list[tuple[str, Callable[[], dict[str, Any]], str]] = [
    ("u1-reviewer-absent", _edit(lambda d: _pop(d["source"], "reviewer")), "semantic:unattended-u1"),
    ("u1-reviewer-not-none", _edit(lambda d: d["source"].update(reviewer="alice")), "semantic:unattended-u1"),
    ("u1-documents-absent", _edit(lambda d: _pop(d["source"], "documents")), "semantic:unattended-u1"),
    ("u1-documents-empty", _edit(lambda d: d["source"].update(documents=[])), "semantic:unattended-u1"),
    ("u1-document-malformed", _edit(lambda d: d["source"]["documents"][0].update(url="x")), "semantic:unattended-u1"),
    ("u2-constraint-confirmed", _edit(lambda d: _constraint(d, "llm-inferred").update(status="confirmed")),
     "semantic:unattended-u2"),
    ("u3-explicit", _edit(lambda d: _constraint(d, "llm-inferred").update(
        source="explicit", status="confirmed", provenance={"user_quote": "q", "spans": [_span("customers")]})),
     "semantic:unattended-u3"),
    ("u3-user-supplied", _edit(lambda d: _constraint(d, "llm-inferred").update(
        source="user-supplied", status="confirmed", provenance={"user_quote": "q", "spans": [_span("customers")]})),
     "semantic:unattended-u3"),
    ("u4-object-type", _edit(lambda d: _pop(_object(d)["provenance"], "spans")), "semantic:unattended-u4"),
    ("u4-fact-type", _edit(lambda d: _pop(_fact(d, "customer_listed")["provenance"], "spans")),
     "semantic:unattended-u4"),
    ("u4-empty-spans", _edit(lambda d: _object(d)["provenance"].update(spans=[])), "semantic:unattended-u4"),
    ("u5-sample", _edit(lambda d: _pop(_constraint(d, "sample")["provenance"], "spans")), "semantic:unattended-u5"),
    ("u5-llm-inferred", _edit(lambda d: _pop(_constraint(d, "llm-inferred")["provenance"], "spans")),
     "semantic:unattended-u5"),
    ("u6-no-sample-spans", _edit(lambda d: _pop(_fact(d)["provenance"], "sample_spans")), "semantic:unattended-u6"),
    ("u6-one-row-uncovered", _edit(lambda d: _fact(d)["provenance"]["sample_spans"].pop()), "semantic:unattended-u6"),
    ("u7-undeclared-document", _edit(lambda d: _object(d)["provenance"]["spans"][0].update(
        document_sha256="0" * 64)), "semantic:unattended-u7"),
    ("u7-start-not-before-end", _edit(lambda d: _object(d)["provenance"]["spans"][0].update(start=9, end=9)),
     "semantic:unattended-u7"),
    ("u7-malformed-span", _edit(lambda d: _object(d)["provenance"]["spans"][0].update(page=1)),
     "semantic:unattended-u7"),
    ("u8-sample", _edit(lambda d: _constraint(d, "sample").update(modality="alethic")), "semantic:unattended-u8"),
    ("u8-llm-inferred", _edit(lambda d: _constraint(d, "llm-inferred").update(modality="alethic")),
     "semantic:unattended-u8"),
    ("u8-common-sense", _edit(lambda d: _constraint(d, "common-sense").update(modality="alethic")),
     "semantic:unattended-u8"),
]


@pytest.mark.parametrize(("name", "build", "rule_id"), BRANCHES, ids=[row[0] for row in BRANCHES])
def test_t2_each_branch_refuses_with_its_rule_id(tmp_path: Path, name: str, build: Any, rule_id: str) -> None:
    exit_code, rule_ids, _payload = _validate(build(), tmp_path)
    assert exit_code == 3
    assert rule_id in rule_ids, rule_ids


@pytest.mark.parametrize(("name", "build", "rule_id"), BRANCHES, ids=[row[0] for row in BRANCHES])
def test_t2b_the_same_edit_without_the_mode_raises_no_unattended_issue(
        tmp_path: Path, name: str, build: Any, rule_id: str) -> None:
    for mode in (None, "one-shot"):
        document = build()
        if mode is None:
            document["source"].pop("mode")
        else:
            document["source"]["mode"] = mode
        _exit_code, rule_ids, _payload = _validate(document, tmp_path)
        assert not any(r.startswith("semantic:unattended") for r in rule_ids), (mode, rule_ids)


def _direct(document: dict[str, Any]) -> list[str]:
    from gnd.model._validation import _rule_unattended

    return [issue.rule_id for issue in _rule_unattended(document)]


def test_t2_branches_unreachable_through_this_fixture_at_the_rule() -> None:
    """U2 on an operation; U5 and U8 on induced and imported constraints.

    Building a valid model with an operation, an induction block or an import
    record is out of proportion to the branch, so the rule itself is called on
    a parsed document, as the semantic layer calls it."""
    document = _doc()
    document["operations"] = [{"id": "op", "status": "confirmed", "source": "llm-inferred"}]
    assert "semantic:unattended-u2" in _direct(document)
    for source in ("induced", "imported"):
        document = _doc()
        _fact(document)["constraints"].append({"type": "mandatory", "role": "customer", "source": source,
                                               "status": "proposed", "modality": "deontic", "provenance": {}})
        assert "semantic:unattended-u5" in _direct(document)
    document = _doc()
    _fact(document)["constraints"].append({"type": "mandatory", "role": "customer", "source": "induced",
                                           "status": "proposed", "modality": "alethic",
                                           "provenance": {"spans": [_span("customers")]}})
    assert _direct(document) == ["semantic:unattended-u8"]
    without = copy.deepcopy(document)
    without["source"].pop("mode")
    assert _direct(without) == []


def test_t2c_the_conforming_model_exits_0(tmp_path: Path) -> None:
    assert _validate(_doc(), tmp_path)[:2] == (0, [])
    assert _direct(_doc()) == []


def test_t2c_common_sense_needs_no_span(tmp_path: Path) -> None:
    assert "spans" not in _constraint(_doc(), "common-sense")["provenance"]


@pytest.mark.parametrize("hostile", [
    lambda d: d["source"].update(documents=3),
    lambda d: _object(d)["provenance"].update(spans="x"),
    lambda d: _object(d)["provenance"]["spans"][0].update(start=True),
    lambda d: _fact(d)["provenance"]["sample_spans"][0].update(row="0"),
    lambda d: _fact(d)["provenance"].update(sample_spans=[3, None]),
    lambda d: _object(d).update(provenance="x"),
    lambda d: d.update(source={"mode": "unattended", "reviewer": None, "documents": [None]}),
])
def test_t2d_hostile_shapes_are_named_issues_never_a_raised_rule(hostile: Any) -> None:
    from gnd.model._validation import semantic_validate

    document = _doc()
    hostile(document)
    rule_ids = [issue.rule_id for issue in semantic_validate(document)]
    assert "internal:rule-raised" not in rule_ids
    assert any(r.startswith("semantic:unattended") for r in rule_ids)


def test_t2e_common_sense_without_library_entry_is_pre_empted_by_the_schema(tmp_path: Path) -> None:
    document = _doc()
    _constraint(document, "common-sense")["provenance"] = {"spans": [_span("customers")]}
    exit_code, rule_ids, _payload = _validate(document, tmp_path)
    assert exit_code == 3 and rule_ids and not any(r.startswith("semantic:unattended") for r in rule_ids)


def test_t2f_issues_come_in_rule_order() -> None:
    document = _doc()
    _constraint(document, "sample").update(modality="alethic")
    _pop(_object(document)["provenance"], "spans")
    document["source"]["reviewer"] = "alice"
    ids = _direct(document)
    assert ids == sorted(ids, key=lambda r: int(r[-1]))


# --- T3: --document -------------------------------------------------------------------


def _with_document(tmp_path: Path, document: dict[str, Any], *paths: Path) -> tuple[int, str]:
    model = _write(document, tmp_path / "model.orm.yaml")
    args = ["validate", str(model), "--format", "json"]
    for path in paths:
        args += ["--document", str(path)]
    result = run_main(args)
    return result.returncode, result.stdout.decode("utf-8")


def test_t3_matching_spans_exit_0(tmp_path: Path) -> None:
    assert _with_document(tmp_path, _doc(), SOURCE)[0] == 0


def test_t3_an_excerpt_mismatch_exits_3(tmp_path: Path) -> None:
    document = _doc()
    _object(document)["provenance"]["spans"][0]["excerpt_sha256"] = "1" * 64
    exit_code, stdout = _with_document(tmp_path, document, SOURCE)
    assert exit_code == 3 and "unattended:excerpt-mismatch" in stdout


def test_t3_end_past_the_document_exits_3(tmp_path: Path) -> None:
    document = _doc()
    span = _object(document)["provenance"]["spans"][0]
    span["end"] = 10_000
    exit_code, stdout = _with_document(tmp_path, document, SOURCE)
    assert exit_code == 3 and "unattended:span-out-of-range" in stdout


def test_t3_an_undeclared_document_exits_3(tmp_path: Path) -> None:
    other = tmp_path / "other.txt"
    other.write_text("another document\n", encoding="utf-8")
    exit_code, stdout = _with_document(tmp_path, _doc(), other)
    assert exit_code == 3 and "unattended:document-undeclared" in stdout


def test_t3_code_points_not_bytes(tmp_path: Path) -> None:
    """The accented letters before every span make byte and code-point offsets differ."""
    raw = SOURCE.read_bytes()
    text = unicodedata.normalize("NFC", raw.decode("utf-8"))
    assert len(raw) != len(text)
    document = _doc()
    phrase = "customers"
    byte_start = raw.index(phrase.encode("utf-8"))
    assert byte_start != text.index(phrase)
    _object(document)["provenance"]["spans"][0].update(start=byte_start, end=byte_start + len(phrase))
    exit_code, stdout = _with_document(tmp_path, document, SOURCE)
    assert exit_code == 3 and "unattended:excerpt-mismatch" in stdout


def test_t3_a_decomposed_document_normalizes_to_the_same_offsets(tmp_path: Path) -> None:
    """NFC: a document written with combining characters keeps the composed offsets."""
    decomposed = unicodedata.normalize("NFD", SOURCE.read_text(encoding="utf-8")).encode("utf-8")
    assert decomposed != SOURCE.read_bytes()
    path = tmp_path / "nfd.txt"
    path.write_bytes(decomposed)
    old, new = hashlib.sha256(SOURCE.read_bytes()).hexdigest(), hashlib.sha256(decomposed).hexdigest()
    text = _write(_doc(), tmp_path / "x.yaml").read_text(encoding="utf-8").replace(old, new)
    document = YAML(typ="safe").load(text)
    assert _with_document(tmp_path, document, path)[0] == 0


def test_t3_a_missing_document_exits_66(tmp_path: Path) -> None:
    assert _with_document(tmp_path, _doc(), tmp_path / "absent.txt")[0] == 66


def test_t3_a_model_without_the_mode_declares_no_document(tmp_path: Path) -> None:
    document = _doc()
    document["source"].pop("mode")
    exit_code, stdout = _with_document(tmp_path, document, SOURCE)
    assert exit_code == 3 and "unattended:document-undeclared" in stdout


def test_t3_text_output(tmp_path: Path) -> None:
    document = _doc()
    _object(document)["provenance"]["spans"][0]["excerpt_sha256"] = "1" * 64
    model = _write(document, tmp_path / "model.orm.yaml")
    result = run_main(["validate", str(model), "--document", str(SOURCE)])
    assert result.returncode == 3 and b"[unattended:excerpt-mismatch]" in result.stdout


# --- T5: disclosure ---------------------------------------------------------------------


def test_t5_no_document_text_in_the_output(tmp_path: Path) -> None:
    document = _doc()
    for span in _fact(document)["provenance"]["spans"]:
        span["excerpt_sha256"] = "1" * 64
    exit_code, stdout = _with_document(tmp_path, document, SOURCE)
    assert exit_code == 3
    for phrase in ("Lumière", "ledger", "placed by a customer"):
        assert phrase not in stdout


# --- T10: cost --------------------------------------------------------------------------


def test_t10_two_thousand_fact_types_with_fifty_rows() -> None:
    from gnd.model._validation import _rule_unattended

    document = _doc()
    span = _span("customers")
    template = _fact(document)
    document["fact_types"] = []
    for i in range(2000):
        fact_type = copy.deepcopy(template)
        fact_type["id"] = f"f{i}"
        fact_type["sample_population"] = [{"order": n, "customer": n} for n in range(50)]
        fact_type["provenance"] = {"spans": [span], "sample_spans": [{"row": n, "span": span} for n in range(50)]}
        document["fact_types"].append(fact_type)
    started = time.perf_counter()
    assert _rule_unattended(document) == []
    assert time.perf_counter() - started < 5.0


# --- review regressions -------------------------------------------------------------------


def test_review_f1_a_digest_with_a_trailing_newline_is_refused(tmp_path: Path) -> None:
    document = _doc()
    document["source"]["documents"][0]["sha256"] += "\n"
    assert "semantic:unattended-u1" in _direct(document)
    document = _doc()
    _object(document)["provenance"]["spans"][0]["excerpt_sha256"] += "\n"
    assert "semantic:unattended-u7" in _direct(document)


def _textual_warning(document: dict[str, Any]) -> None:
    """An imported textual alethic constraint: admitted by the mode, warned by semantic:textual-alethic."""
    document["constraints"] = [{
        "type": "textual", "expression": "Every order is shipped eventually.", "source": "imported",
        "status": "proposed", "modality": "alethic",
        "provenance": {"framework": "gsd", "artifact": "REQ.md", "commit": "a" * 40, "sha256": "b" * 64,
                       "anchor": "R1", "spans": [_span("customers")]}}]


def test_review_f3_a_document_refusal_keeps_the_models_warnings(tmp_path: Path) -> None:
    document = _doc()
    _textual_warning(document)
    exit_code, _ids, payload = _validate(document, tmp_path)
    assert exit_code == 0 and payload["warnings"]
    _object(document)["provenance"]["spans"][0]["excerpt_sha256"] = "1" * 64
    exit_code, stdout = _with_document(tmp_path, document, SOURCE)
    assert exit_code == 3 and json.loads(stdout)["warnings"] == payload["warnings"]
    model = _write(document, tmp_path / "model.orm.yaml")
    text = run_main(["validate", str(model), "--document", str(SOURCE)])
    assert text.returncode == 3 and b"WARNING at" in text.stdout


def test_review_f4_a_document_over_the_cap_is_refused_before_hashing(tmp_path: Path) -> None:
    from gnd.anchors import MAX_DOCUMENT_BYTES

    big = tmp_path / "big.txt"
    big.write_bytes(b"a" * (MAX_DOCUMENT_BYTES + 1))
    exit_code, stdout = _with_document(tmp_path, _doc(), big)
    assert exit_code == 3 and "document cap" in stdout and "undeclared" not in stdout


@pytest.mark.parametrize("rows", [[0, 0, 1], [0, 1, 2], [-1, 0, 1]], ids=["duplicate", "out-of-range", "negative"])
def test_review_f5_sample_span_rows_must_name_each_row_once(rows: list[int]) -> None:
    document = _doc()
    span = _span("Order 10 was placed by customer 1.")
    _fact(document)["provenance"]["sample_spans"] = [{"row": row, "span": span} for row in rows]
    assert "semantic:unattended-u6" in _direct(document)


def test_review_f5_sample_spans_without_rows_are_still_checked() -> None:
    document = _doc()
    _fact(document, "customer_listed")["provenance"]["sample_spans"] = [{"row": 0, "span": {"bad": 1}}]
    ids = _direct(document)
    assert "semantic:unattended-u6" in ids and "semantic:unattended-u7" in ids


def test_review_f6_a_span_on_a_common_sense_constraint_is_checked() -> None:
    document = _doc()
    _constraint(document, "common-sense")["provenance"]["spans"] = [{"bad": 1}]
    assert "semantic:unattended-u7" in _direct(document)


def test_review_f13_without_the_mode_the_exit_follows_the_other_rules(tmp_path: Path) -> None:
    for _name, build, _rule_id in BRANCHES:
        document = build()
        document["source"].pop("mode")
        exit_code, rule_ids, _payload = _validate(document, tmp_path)
        assert exit_code == (3 if rule_ids else 0), (_name, rule_ids)
