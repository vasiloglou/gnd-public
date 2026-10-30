"""IH0: regressions for the findings of the ilp-learners source review.

Spec: .gnd-planning/milestones/ilp-import-hardening/notes/phase-IH0-spec.md
(r2). The findings and their reproductions are in notes/phase-IH0-triage.md;
each test below was red against the fix's parent commit (evidence/IH0/red.txt).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
REFUNDS = REPO_ROOT / "src" / "gnd" / "examples" / "refunds"
TOOL = REPO_ROOT / "tools" / "ilp_comparison.py"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _import(tmp_path: Path, target: str, text: str, learner: str, clauses: int = 1,
            binds: str | None = None):
    """Import TEXT through TARGET with a well-shaped run record; the coverage is never reached."""
    export = tmp_path / "export"
    assert run_main(["export", "ilp", str(REFUNDS / "model.orm.yaml"), "--labels",
                     str(REFUNDS / "labels.json"), "--target", binds or target,
                     "--out", str(export)]).returncode == 0
    source = tmp_path / "clauses"
    source.write_text(text, encoding="utf-8")
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": learner, "version": "0"},
        "export_sha256": _sha((export / "export.json").read_bytes()),
        "clauses_sha256": _sha(source.read_bytes()),
        "coverage": [{"clause": k, "covered": []} for k in range(clauses)]}))
    out = tmp_path / "proposal.json"
    result = run_main(["import", "ilp-rules", str(REFUNDS / "model.orm.yaml"), str(source),
                       "--labels", str(REFUNDS / "labels.json"), "--reported-coverage", str(run),
                       "--target", target, "--out", str(out)])
    return result.returncode, result.stderr.decode(), out


# ---------------------------------------------------------------------------
# T1 (findings A, B): rules and Popper refuse a threshold their export never
# offered. 450 is offered for refunds; 451 is not. The LLM half of A is held
# for the owner's batched ruling (IH0-D4): it would move IL5's case i13.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(("target", "learner", "text", "clauses", "binds", "clause"), [
    ("rules", "wittgenstein", "[[f_refund_amount__2__3__gt_t_amount__451=1]]", 1, None, 0),
    ("rules", "wittgenstein", ("[[f_refund_amount__2__3__gt_t_amount__450=1] V "
                               "[f_refund_amount__2__3__gt_t_amount__451=1]]"), 2, None, 1),
    ("popper", "popper", "wrong(V0):- f_refund_amount(V0,V1,V2),ge_t_amount__451(V2).\n", 1, None, 0),
    ("popper", "popper", "wrong(V0):- f_refund_amount(V0,V1,V2),le_t_amount__451(V2).\n", 1, None, 0),
], ids=["rules", "rules-second", "popper-ge", "popper-le"])
def test_t1_an_unoffered_threshold_is_refused(tmp_path, target, learner, text, clauses, binds, clause):
    code, stderr, out = _import(tmp_path, target, text, learner, clauses, binds)
    assert code == 3, stderr
    assert stderr.startswith(f"clause {clause}: off-threshold:"), stderr
    assert not out.exists()


@pytest.mark.parametrize(("target", "learner", "text", "binds"), [
    ("rules", "wittgenstein", "[[f_refund_amount__2__3__gt_t_amount__450=1]]", None),
    ("popper", "popper", "wrong(V0):- f_refund_amount(V0,V1,V2),gt_t_amount__500(V2).\n", None),
], ids=["rules", "popper"])
def test_t1_an_offered_threshold_passes_the_vet(tmp_path, target, learner, text, binds):
    code, stderr, _out = _import(tmp_path, target, text, learner, 1, binds)
    # The vet passes, so the import reaches the set comparison with the empty coverage.
    assert code == 3 and "coverage-mismatch" in stderr, stderr


def test_t1_the_rules_adapter_names_its_import_refusal():
    from gnd.export import ilp_learners, ilp_rules

    assert ilp_rules.IMPORT_REFUSALS == ("off-threshold",)
    assert ilp_learners.learner("rules").vet is ilp_rules.check_columns


# ---------------------------------------------------------------------------
# T2, T3 (findings C and D): the comparison tool names an un-indexed refusal,
# counts what it never reached, and refuses evidence its reader cannot read.
# ---------------------------------------------------------------------------

def _tool_module() -> Any:
    spec = importlib.util.spec_from_file_location("ilp_comparison", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)  # type: ignore[union-attr]
    return tool


def _copy_evidence(tmp_path: Path, tool: Any) -> Path:
    for relative in (tool.EVIDENCE, tool.STAFFING, tool.GOLDEN, tool.BRIDGE):
        source, target = REPO_ROOT / relative, tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if source.is_dir() else shutil.copy)(source, target)
    return tmp_path


TWO_CLAUSES = ("wrong(V0):- f_refund_amount(V0,V1,V2),gt_t_amount__500(V2).\n"
               "wrong(V0):- f_refund_amount(V0,V1,V2),gt_t_amount__450(V2).\n")


@pytest.mark.parametrize(("stderr", "refusal", "not_evaluated"), [
    ("export-mismatch: the run record binds export a, not b\n", {"name": "export-mismatch", "index": None}, 2),
    ("invalid model: the candidate fails validation\n", None, None),
    ("clause 1: off-threshold: gt_t_amount__451 is not rendered\n", {"name": "off-threshold", "index": 1}, 2),
    ("clause 0: recursion: the body calls wrong\n", {"name": "recursion", "index": 0}, 1),
], ids=["binding", "unnamed", "vet", "fragment"])
def test_t2_the_first_refusal_and_what_it_left_unevaluated(tmp_path, stderr, refusal, not_evaluated):
    tool = _tool_module()
    root = _copy_evidence(tmp_path, tool)
    live = root / tool.EVIDENCE / "IL1/live/invocation-3"
    (live / "program.pl").write_text(TWO_CLAUSES, encoding="utf-8")
    (live / "import-stderr.txt").write_text(stderr, encoding="utf-8")
    outcome = json.loads((live / "outcome.json").read_text(encoding="utf-8"))
    (live / "outcome.json").write_text(json.dumps({**outcome, "import_exit": 3}), encoding="utf-8")
    row = tool.labelled_row(root, "popper", 3, "IL1/live/invocation-3", "program.pl")
    assert row["first_refusal"] == refusal
    assert row["clauses_not_evaluated"] == not_evaluated


@pytest.mark.parametrize(("adapter", "directory", "output", "text", "stderr", "refusal"), [
    ("rules", "IL3/live/invocation-1", "ruleset.txt", "[[f_refund_amount__2__3__gt_t_amount__500=0]]",
     "clause 0: negation-as-failure: the rule requires a feature to be false\n",
     {"name": "negation-as-failure", "index": 0}),
    ("popper", "IL1/live/invocation-3", "program.pl", "wrong(V0):- f_refund_amount(V0,V1,V2)) .\n",
     "unparsable: line 1, column 39: x\n", {"name": "unparsable", "index": None}),
], ids=["rules-polarity", "popper-syntax"])
def test_t2_output_the_import_refused_at_its_reader_is_a_row(tmp_path, adapter, directory, output,
                                                              text, stderr, refusal):
    tool = _tool_module()
    root = _copy_evidence(tmp_path, tool)
    live = root / tool.EVIDENCE / directory
    (live / output).write_text(text, encoding="utf-8")
    (live / "import-stderr.txt").write_text(stderr, encoding="utf-8")
    outcome = json.loads((live / "outcome.json").read_text(encoding="utf-8"))
    (live / "outcome.json").write_text(json.dumps({**outcome, "import_exit": 3}), encoding="utf-8")
    invocation = int(directory.rsplit("-", 1)[1])
    row = tool.labelled_row(root, adapter, invocation, directory, output)
    assert row["first_refusal"] == refusal
    assert row["clauses_proposed"] is None and row["clauses_not_evaluated"] is None


def test_t2_an_unindexed_refusal_is_shown_without_an_index():
    tool = _tool_module()
    assert tool._refusal({"name": "export-mismatch", "index": None}, "clause") == "`export-mismatch`"


def test_t3_labelled_evidence_the_reader_refuses_fails_the_tool_loudly(tmp_path):
    tool = _tool_module()
    root = _copy_evidence(tmp_path, tool)
    live = root / tool.EVIDENCE / "IL1/live/invocation-3"
    (live / "program.pl").write_text("wrong(V0):- f_refund_amount(V0,V1,V2),gt_t_amount__0500(V2).\n",
                                     encoding="utf-8")
    completed = subprocess.run([sys.executable, str(TOOL), "--root", str(root)], capture_output=True,
                               text=True, timeout=300, check=False, cwd=REPO_ROOT)
    assert completed.returncode == 2, completed.stderr
    assert "IL1/live/invocation-3: unparsable:" in completed.stderr
    assert "Traceback" not in completed.stderr


# ---------------------------------------------------------------------------
# T4 (finding H): an ILASP aggregate reaches the fragment table's own refusal.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("aggregate", [
    "#sum+{ V2 : f_refund_amount(X,V1,V2) } > 3",
    "#count{ " + "; ".join(f"V{k} : f_refund_by(V1,V{k})" for k in range(2, 20)) + " } > 3",
], ids=["sum-plus", "seventeen-elements"])
def test_t4_an_aggregate_is_refused_by_name(tmp_path, aggregate):
    text = f"wrong :- f_refund_amount(V1,V2), {aggregate}.\n"
    code, stderr, out = _import(tmp_path, "ilasp", text, "ilasp")
    assert code == 3, stderr
    assert stderr.startswith("clause 0: aggregate:"), stderr
    assert not out.exists()


# ---------------------------------------------------------------------------
# T5 (IH-R4): each new adapter refusal is named in its adapter's section.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("section", ["Import", "Boolean rule sets"])
def test_t5_off_threshold_is_named_where_the_adapter_is_documented(section):
    import re

    text = (REPO_ROOT / "docs" / "reference" / "ilp-bridge.md").read_text(encoding="utf-8")
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    sections = {parts[k].strip(): parts[k + 1] for k in range(1, len(parts), 2)}
    assert "`off-threshold`" in sections[section]


# ---------------------------------------------------------------------------
# T6 (fix review, finding 1): a column of another integer type the export did
# not write is refused, even where a value subtype lets the join through.
# ---------------------------------------------------------------------------

_FEE = """  - id: fee
    name: Fee
    kind: value
    primitive: Integer
    subtype_of: [amount]
    inherits_reference: true
"""
_REFUND_FEE = """  - id: refund_fee
    reading: "{Refund} has {Fee}"
    roles:
      - { object_type: refund, role_name: refund }
      - { object_type: fee, role_name: fee }
"""


def _fee_model(tmp_path: Path) -> tuple[Path, Path]:
    """Refunds plus a Fee value type, a subtype of Amount, and the fact type refund_fee."""
    root = tmp_path / "fee"
    shutil.copytree(REFUNDS, root)
    model = root / "model.orm.yaml"
    text = model.read_text(encoding="utf-8")
    text = text.replace("  - id: channel\n", _FEE + "  - id: channel\n", 1)
    text = text.replace("  - id: refund_channel\n", _REFUND_FEE + "  - id: refund_channel\n", 1)
    model.write_text(text, encoding="utf-8")
    labels = root / "labels.json"
    document = json.loads(labels.read_text(encoding="utf-8"))
    labels.write_text(json.dumps({**document, "model_sha256": _sha(model.read_bytes())}), encoding="utf-8")
    return model, labels


def test_t6_a_subtype_column_the_export_did_not_write_is_refused(tmp_path):
    model, labels = _fee_model(tmp_path)
    export = tmp_path / "export"
    assert run_main(["export", "ilp", str(model), "--labels", str(labels), "--target", "rules",
                     "--out", str(export)]).returncode == 0
    assert "gt_t_fee" not in (export / "rules" / "features.json").read_text(encoding="utf-8")
    source = tmp_path / "ruleset.txt"
    source.write_text("[[f_refund_amount__2__3__gt_t_fee__451=1]]", encoding="utf-8")
    run = tmp_path / "run.json"
    run.write_text(json.dumps({
        "schema_version": "gnd-ilp-run/1", "learner": {"name": "wittgenstein", "version": "0"},
        "export_sha256": _sha((export / "export.json").read_bytes()),
        "clauses_sha256": _sha(source.read_bytes()),
        "coverage": [{"clause": 0, "covered": ["south", "harbor", "market", "airport", "station"]}]}))
    out = tmp_path / "proposal.json"
    result = run_main(["import", "ilp-rules", str(model), str(source), "--labels", str(labels),
                       "--reported-coverage", str(run), "--target", "rules", "--out", str(out)])
    assert result.returncode == 3, result.stderr.decode()
    assert result.stderr.decode().startswith("clause 0: off-threshold:")
    assert not out.exists()


# ---------------------------------------------------------------------------
# The spec's test row: IL's private-clean check, widened to this milestone.
# ---------------------------------------------------------------------------

def test_t8_this_milestone_directory_is_private_clean():
    import getpass

    from test_ilp_learners import _private_hits

    user = getpass.getuser()
    milestone = REPO_ROOT / ".gnd-planning" / "milestones" / "ilp-import-hardening"
    files = [path for path in milestone.rglob("*") if path.is_file()]
    assert files
    offenders = {str(path.relative_to(REPO_ROOT)): hits for path in files
                 if (hits := _private_hits(path.read_text(encoding="utf-8", errors="replace"), user))}
    assert offenders == {}
