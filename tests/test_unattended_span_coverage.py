"""UG3 part A: source-span counts on gnd validate --document, and --require-documents.

Spec: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG3-spec.md
(§6.1, §6.2, §8 part A, §11). Approval instrument: corpus-first (UG3-D14 (a)).
The corpus is tests/fixtures/unattended-model-growth/ug3/: README.md narrates
each case without its outcome, expected.json is the answer key ("part_a"),
parity-baseline.json ("part_a") was captured on 5c6a0c5f before the first
source edit.

The corpus cases (A1 to A6b) are red until part A lands: the counts and
`--require-documents` do not exist on the base. The parity test (A10) is green
on the base and must stay green. Set GND_UG3_CAPTURE=1 to rewrite the baseline;
only ever on the base commit named above.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "tests" / "fixtures" / "unattended-model-growth" / "ug3"
EXPECTED = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))["part_a"]
BASELINE_PATH = CORPUS / "parity-baseline.json"
RULE = "unattended:spans-unchecked"
FLAG = "--require-documents"


def _workspace(root: Path) -> Path:
    """A copy of the corpus's models and documents, so paths in the output are the test's own."""
    shutil.copytree(CORPUS / "models", root / "models")
    shutil.copytree(CORPUS / "documents", root / "documents")
    return root


def _validate(root: Path, model: str, documents: list[str], flags: list[str], fmt: str = "json") -> Any:
    argv = ["validate", str(root / "models" / model), "--format", fmt]
    for name in documents:
        argv += ["--document", str(root / "documents" / name)]
    return run_main([*argv, *flags])


def _normalized(stdout: bytes, root: Path) -> str:
    return stdout.decode("utf-8").replace(str(root), "<ws>")


# --- the corpus: A1 to A6b, judged against expected.json ---------------------


@pytest.mark.parametrize("case_id", sorted(EXPECTED))
def test_corpus_case(tmp_path: Path, case_id: str) -> None:
    case = EXPECTED[case_id]
    root = _workspace(tmp_path / "ws")
    result = _validate(root, case["model"], case["documents"], case["flags"])
    assert result.returncode == case["exit"], (result.returncode, result.stderr.decode())
    if case.get("same_as_without_flag"):
        without = [flag for flag in case["flags"] if flag != FLAG]
        assert FLAG in case["flags"]  # the comparison is not vacuous
        control = _validate(root, case["model"], case["documents"], without)
        assert (result.returncode, result.stdout, result.stderr) == (control.returncode, control.stdout,
                                                                     control.stderr)
        return
    payload = json.loads(result.stdout)
    assert payload["warnings"] == case["warnings"]
    assert [issue for issue in payload["issues"] or [] if issue["rule_id"] == RULE] == case["issues"]
    assert (payload["issues"] or []) == case["issues"]


def test_answer_key_is_split_from_the_narration() -> None:
    """Every case is narrated, and the narration gives no outcome (spec §11)."""
    readme = (CORPUS / "README.md").read_text(encoding="utf-8").lower()
    narrated = {line.split()[1] for line in readme.splitlines() if line.startswith("### ")}
    expected = json.loads((CORPUS / "expected.json").read_text(encoding="utf-8"))
    assert narrated == {case.lower() for case in (*expected["part_a"], *expected["part_b"])}
    for word in ("exit", "refuse", "admit", "warning", "error", "pass", "unchecked", "re-hashed", "fail"):
        assert word not in readme, word


# --- A10: flag-free parity (UG-R1), green on the base and after part A -------

PARITY_MODELS = ("span-element.orm.yaml", "span-constraint.orm.yaml", "span-sample.orm.yaml", "plain.orm.yaml")
PARITY_DOCUMENTS = ((), ("ledger.txt",), ("ledger.txt", "annex.txt"))


def _parity_rows(tmp_path: Path) -> list[dict[str, Any]]:
    root = _workspace(tmp_path / "parity")
    rows = []
    for model in PARITY_MODELS:
        for documents in PARITY_DOCUMENTS:
            for fmt in ("json", "text"):
                result = _validate(root, model, list(documents), [], fmt)
                # The one carve-out (UG-R1, UG3-D3): an unattended model whose
                # --document run leaves its annex span unchecked.
                carve_out = model != "plain.orm.yaml" and documents == ("ledger.txt",)
                rows.append({"model": model, "documents": list(documents), "format": fmt,
                             "exit": result.returncode, "stdout": _normalized(result.stdout, root),
                             "stderr": _normalized(result.stderr, root), "carve_out": carve_out})
    return rows


def _baseline_rows() -> list[dict[str, Any]]:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["part_a"]["rows"]


def _paired(tmp_path: Path) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    rows, base_rows = _parity_rows(tmp_path), _baseline_rows()
    assert len(rows) == len(base_rows) == 24
    for row, base in zip(rows, base_rows, strict=True):
        assert (row["model"], row["documents"], row["format"]) == (base["model"], base["documents"], base["format"])
    return list(zip(rows, base_rows, strict=True))


def test_a10_capture_or_compare_the_flag_free_baseline(tmp_path: Path) -> None:
    """Every run outside the carve-out is byte-identical to the base (green on the base)."""
    if os.environ.get("GND_UG3_CAPTURE"):
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8")) if BASELINE_PATH.exists() else {}
        baseline["part_a"] = {"base": "5c6a0c5f", "rows": _parity_rows(tmp_path)}
        BASELINE_PATH.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return
    pairs = _paired(tmp_path)
    assert sum(base["carve_out"] for _row, base in pairs) == 6
    for row, base in pairs:
        assert (row["exit"], row["stderr"]) == (base["exit"], base["stderr"]), row
        if not base["carve_out"]:
            assert row["stdout"] == base["stdout"], row


def test_a10b_the_carve_out_adds_exactly_one_entry(tmp_path: Path) -> None:
    """The carved-out runs equal the base plus one entry, nothing else (red until part A)."""
    entry = {"path": "$.source.documents", "rule_id": RULE, "severity": "warning",
             "message": "1 of 10 source spans were not re-hashed; supply every declared document with --document"}
    for row, base in _paired(tmp_path):
        if not base["carve_out"]:
            continue
        if row["format"] == "json":
            expected = json.loads(base["stdout"])
            expected["warnings"] = [*expected["warnings"], entry]
            assert json.loads(row["stdout"]) == expected
        else:
            line = f"WARNING at {entry['path']}: {entry['message']} [{RULE}]\n"
            assert row["stdout"] == line + base["stdout"], row


# --- A7 to A13: the spec's successor cases beyond the approved corpus --------
#
# These are implementation cases (spec §8), not corpus answers: they pin the
# usage error, both text routes, the absence of document text, the order of
# entries, the payload schema, the counting table at the function, and the
# single pass.

LEDGER_SPAN = "excerpt_sha256: 21eb2153dd1483cd67a621fb2c7b2f65b2ca46c64a49e49be4b939a1f0c844f8"
ENTRY_LINE = ("WARNING at $.source.documents: 1 of 10 source spans were not re-hashed; "
              "supply every declared document with --document [unattended:spans-unchecked]\n")


def _variant(root: Path, name: str, old: str, new: str) -> str:
    """A copy of the element-span model with one textual edit, under ``models/``."""
    text = (root / "models" / "span-element.orm.yaml").read_text(encoding="utf-8")
    assert text.count(old) == 1, old
    (root / "models" / name).write_text(text.replace(old, new), encoding="utf-8")
    return name


def test_a7_require_documents_with_identity_is_a_usage_error(tmp_path: Path) -> None:
    root = _workspace(tmp_path / "ws")
    result = run_main(["validate", str(root / "models" / "span-element.orm.yaml"), "--identity", FLAG])
    assert result.returncode == 64
    assert b"not combined with --require-documents" in result.stderr
    assert result.stdout == b""


def test_a8_both_text_routes_print_the_entry(tmp_path: Path) -> None:
    root = _workspace(tmp_path / "ws")
    plain = _validate(root, "span-element.orm.yaml", ["ledger.txt"], [], "text")
    assert plain.returncode == 0
    assert plain.stdout.decode().startswith(ENTRY_LINE)
    # The projected route: a redacted fact type turns the redaction projection on.
    projected = _variant(root, "projected.orm.yaml", "- id: order_placed_by_customer\n",
                         "- id: order_placed_by_customer\n  redact: true\n")
    result = _validate(root, projected, ["ledger.txt"], [], "text")
    assert result.returncode == 0, result.stderr
    assert ENTRY_LINE in result.stdout.decode()
    as_json = json.loads(_validate(root, projected, ["ledger.txt"], [], "json").stdout)
    report = as_json.get("report", as_json)
    assert "redaction" in report  # the route under test really is the projected one
    assert [warning["rule_id"] for warning in report["warnings"]] == [RULE]


def test_a9_no_document_text_reaches_the_output(tmp_path: Path) -> None:
    canaries = {"ledger.txt": "Café Lumière keeps", "annex.txt": "Annex to the ledger"}
    for name, canary in canaries.items():  # positive control: the canary is in the document
        assert canary in (CORPUS / "documents" / name).read_text(encoding="utf-8")
    root = _workspace(tmp_path / "ws")
    runs = [_validate(root, case["model"], case["documents"], case["flags"]) for case in EXPECTED.values()]
    runs += [_validate(root, "span-element.orm.yaml", ["ledger.txt"], flags, "text") for flags in ([], [FLAG])]
    for result in runs:
        for stream in (result.stdout, result.stderr):
            for canary in canaries.values():
                assert canary.encode("utf-8") not in stream


def test_a11_existing_issues_come_first_then_the_unchecked_entry(tmp_path: Path) -> None:
    root = _workspace(tmp_path / "ws")
    broken = _variant(root, "broken.orm.yaml", LEDGER_SPAN, "excerpt_sha256: " + "a" * 64)
    result = _validate(root, broken, ["ledger.txt"], [FLAG])
    assert result.returncode == 3
    payload = json.loads(result.stdout)
    assert [(issue["rule_id"], issue["severity"]) for issue in payload["issues"]] == [
        ("unattended:excerpt-mismatch", "error"), (RULE, "error")]
    # Without the flag the same entry rides in warnings instead.
    plain = json.loads(_validate(root, broken, ["ledger.txt"], []).stdout)
    assert [issue["rule_id"] for issue in plain["issues"]] == ["unattended:excerpt-mismatch"]
    assert [warning["rule_id"] for warning in plain["warnings"]] == [RULE]


def test_a12_the_payload_fits_the_report_schema(tmp_path: Path) -> None:
    from jsonschema import Draft202012Validator

    from gnd.report_schema import load_report_schema

    validator = Draft202012Validator(load_report_schema())
    root = _workspace(tmp_path / "ws")
    for flags in ([], [FLAG]):
        payload = json.loads(_validate(root, "span-element.orm.yaml", ["ledger.txt"], flags).stdout)
        assert RULE in json.dumps(payload)
        assert list(validator.iter_errors(payload)) == []


def _digest(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _span_doc(spans: list[Any], declared: str) -> dict[str, Any]:
    return {
        "source": {"kind": "prose", "mode": "unattended", "reviewer": "none",
                   "documents": [{"sha256": declared, "label": "d.txt"}]},
        "object_types": [{"id": f"o{index}", "provenance": {"spans": [span]}} for index, span in enumerate(spans)],
    }


def test_a12b_malformed_and_undeclared_spans_count_as_unchecked() -> None:
    from gnd.model import unattended_span_coverage

    text = "an order has one placing customer"
    declared, other = _digest(text), "e" * 64
    good = {"document_sha256": declared, "start": 0, "end": 8, "excerpt_sha256": _digest(text[:8])}
    spans = [good, "not a mapping", {"document_sha256": declared, "start": 0}, {**good, "document_sha256": other}]
    coverage = unattended_span_coverage(_span_doc(spans, declared), {"d.txt": text.encode("utf-8")})
    assert (coverage.total, coverage.rehashed, coverage.unchecked) == (4, 1, 3)
    entry = coverage.issue(severity="warning")
    assert entry is not None and entry.message.startswith("3 of 4 ")
    # Not the mode: no counts at all.
    assert unattended_span_coverage({"object_types": []}, {}) is None


@pytest.mark.parametrize("count", [1, 10, 100])
def test_a13_the_walk_is_one_linear_pass(count: int, monkeypatch: pytest.MonkeyPatch) -> None:
    import gnd.model._unattended as unattended

    text = "an order has one placing customer"
    declared = _digest(text)
    span = {"document_sha256": declared, "start": 0, "end": 8, "excerpt_sha256": _digest(text[:8])}
    calls = {"walk": 0, "span": 0}
    original_walk, original_span = unattended._iter_unattended_spans, unattended._span_issue

    def walk(doc: dict[str, Any]):
        calls["walk"] += 1
        return original_walk(doc)

    def span_issue(*args: Any, **kwargs: Any):
        calls["span"] += 1
        return original_span(*args, **kwargs)

    monkeypatch.setattr(unattended, "_iter_unattended_spans", walk)
    monkeypatch.setattr(unattended, "_span_issue", span_issue)
    coverage = unattended.unattended_span_coverage(_span_doc([span] * count, declared), {"d.txt": text.encode()})
    assert (coverage.total, coverage.rehashed) == (count, count)
    assert calls == {"walk": 1, "span": count}


# --- review regressions (notes/phase-UG3-codex-review.md) --------------------

REDACTED = ("- id: order_placed_by_customer\n", "- id: order_placed_by_customer\n  redact: true\n")


@pytest.mark.parametrize(("documents", "flags", "exit_code", "rule"), [
    ([], [FLAG], 3, RULE),                              # the UG3 strict route
    (["round.txt"], [], 3, "unattended:document-undeclared"),  # MG5's refusal route, same rebuild
    (["ledger.txt"], [], 0, RULE),                      # the warning route
])
def test_r1_a_redacted_model_keeps_its_projected_report(tmp_path: Path, documents: list[str], flags: list[str],
                                                        exit_code: int, rule: str) -> None:
    """Review finding 1: the walk's result is projected like any validate result."""
    from jsonschema import Draft202012Validator

    from gnd.report_schema import load_report_schema

    root = _workspace(tmp_path / "ws")
    model = _variant(root, "redacted.orm.yaml", *REDACTED)
    result = _validate(root, model, documents, flags)
    assert result.returncode == exit_code, result.stderr
    payload = json.loads(result.stdout)
    assert "redaction" in payload.get("report", payload)
    assert list(Draft202012Validator(load_report_schema()).iter_errors(payload)) == []
    entries = [*(payload["issues"] or []), *payload["warnings"]]
    assert rule in [entry["rule_id"] for entry in entries]
    text = _validate(root, model, documents, flags, "text")
    assert text.returncode == exit_code
    assert f"[{rule}]" in text.stdout.decode()


def test_r2_the_flag_is_a_no_op_on_a_model_with_unchecked_span_metadata(tmp_path: Path) -> None:
    """Review finding 2: outside the mode `provenance.spans` is not checked, so the walk must be total."""
    root = _workspace(tmp_path / "ws")
    text = (root / "models" / "plain.orm.yaml").read_text(encoding="utf-8")
    head, rest = text.split("object_types:\n", 1)
    first_line, tail = rest.split("\n", 1)
    (root / "models" / "odd.orm.yaml").write_text(
        f"{head}object_types:\n{first_line}\n  provenance: {{spans: 3}}\n{tail}", encoding="utf-8")
    control = _validate(root, "odd.orm.yaml", [], [])
    assert control.returncode == 0
    flagged = _validate(root, "odd.orm.yaml", [], [FLAG])
    assert (flagged.returncode, flagged.stdout, flagged.stderr) == (control.returncode, control.stdout, control.stderr)
    with_document = _validate(root, "odd.orm.yaml", ["ledger.txt"], [])
    assert with_document.returncode == 3
    issues = json.loads(with_document.stdout)["issues"]
    assert [issue["rule_id"] for issue in issues] == ["unattended:document-undeclared"]


def test_r4_a_digest_of_the_wrong_type_counts_as_unchecked() -> None:
    """Review finding 4: shape before lookup."""
    from gnd.model import unattended_span_coverage

    text = "an order has one placing customer"
    declared = _digest(text)
    for digest in ([], {}, 7):
        span = {"document_sha256": digest, "start": 0, "end": 2, "excerpt_sha256": declared}
        coverage = unattended_span_coverage(_span_doc([span], declared), {"d.txt": text.encode("utf-8")})
        assert (coverage.total, coverage.rehashed) == (1, 0)
