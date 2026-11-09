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
