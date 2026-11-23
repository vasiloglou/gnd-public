"""VG5 (reviewed-vocabulary-growth): the packaged seeded-growth example runs the whole path.

The spec is ``.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG5-spec.md``;
the test names are its section 8 rows.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from support.cli_runner import run_main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/seeded_growth"
BUILD = ROOT / "tools/build_seeded_growth_example.py"
BUILT = ("round-1.proposal.json", "round-2.proposal.json", "population.json", "policy.json", "receipts.json")
DOCUMENTS = ("round-1.document.txt", "round-2.document.txt")


def _copy(tmp_path: Path) -> Path:
    work = tmp_path.resolve() / "ws"
    shutil.copytree(EXAMPLE, work)
    (work / "records").mkdir()
    return work


def _round(work: Path, n: int) -> tuple[int, int]:
    common = ["--workspace", str(work), "--records", str(work / "records"), "--policy", "additive",
              "--format", "json"]
    preview = run_main(["evolve", "preview", str(work / "root.orm.yaml"), str(work / f"round-{n}.proposal.json"),
                        "--out", str(work / f"preview-{n}.json"), *common])
    apply = run_main(["evolve", "apply", str(work / "root.orm.yaml"), str(work / f"round-{n}.proposal.json"),
                      "--preview", str(work / f"preview-{n}.json"), *common])
    return preview.returncode, apply.returncode


@pytest.fixture(scope="module")
def grown(tmp_path_factory) -> Path:
    work = _copy(tmp_path_factory.mktemp("vg5"))
    for n in (1, 2):
        assert _round(work, n) == (0, 0)
    return work


# --- T1 (VG5-C1) -------------------------------------------------------------


def test_T1_the_built_files_rebuild_byte_identically(tmp_path):
    work = tmp_path / "rebuild"
    shutil.copytree(EXAMPLE, work)
    for name in BUILT:
        (work / name).unlink()
    subprocess.run([sys.executable, str(BUILD), str(work)], check=True)
    for name in BUILT:
        assert (work / name).read_bytes() == (EXAMPLE / name).read_bytes(), name


def test_T1_both_rounds_apply_and_publish_the_built_candidate(grown):
    proposal = json.loads((EXAMPLE / "round-2.proposal.json").read_text())
    assert (grown / "root.orm.yaml").read_bytes() == proposal["candidate_model"]["text"].encode("utf-8")


def test_T1_the_starting_root_validates_without_a_document():
    assert run_main(["validate", str(EXAMPLE / "root.orm.yaml")]).returncode == 0


# --- T2 (VG5-C2) -------------------------------------------------------------


def test_T2_the_grown_root_validates_with_both_documents(grown):
    argv = ["validate", str(grown / "root.orm.yaml"), "--require-documents"]
    for name in DOCUMENTS:
        argv += ["--document", str(grown / name)]
    result = run_main(argv)
    assert result.returncode == 0, result.stdout.decode()
    assert result.stdout.decode().startswith("INCLUDE seed sha256=")


def test_T2_the_grown_root_checks_over_the_example_population(grown):
    result = run_main(["check", str(grown / "root.orm.yaml"), str(grown / "population.json"), "--format", "json"])
    report = json.loads(result.stdout)
    report = report.get("report", report)
    assert result.returncode == 0
    assert [(v["constraint_ref"], v["verdict"]) for v in report["verdicts"]] == [
        ("fact_types[work_has_version].constraints[0]", "pass"),
        ("fact_types[work_has_version].constraints[1]", "pass")]


def test_T2_the_grown_root_judges(grown):
    result = run_main(["judgments", "check", str(grown / "root.orm.yaml"), str(grown / "population.json"),
                       "--policy", str(grown / "policy.json"), "--receipts", str(grown / "receipts.json"),
                       "--trusted-root", str(grown), "--format", "json"])
    payload = json.loads(result.stdout)
    assert result.returncode == 0 and payload["outcome"] == 0, payload.get("error")
    assert payload["judgment_policy"]["admission"] is True


# --- T3 (VG5-C3): the route list against live routes --------------------------


def _route_list() -> str:
    page = (ROOT / "src/gnd/skills/gnd-orm-core/references/representation-format.md").read_text()
    start = page.index("CLI routes that resolve an include root")
    return page[start:page.index("An include path that cannot be encoded", start)]


def test_T3_the_route_list_names_coverage_and_evolve():
    routes = _route_list()
    assert "| `gnd coverage` |" in routes
    assert "| `gnd evolve` (preview, apply, finalize) |" in routes


def test_T3_coverage_and_evolve_resolve_the_example_root(tmp_path, grown):
    assert run_main(["coverage", str(grown / "root.orm.yaml"), "--format", "json"]).returncode == 0
    work = _copy(tmp_path)
    assert _round(work, 1)[0] == 0


def test_T3_a_route_outside_the_list_refuses_the_include_root(tmp_path, grown):
    result = run_main(["codegen", str(grown / "root.orm.yaml"), "--out", str(tmp_path / "out")])
    assert result.returncode != 0
    assert b"include:unsupported-route" in result.stdout + result.stderr


# --- T4 (VG5-C4): the replies --------------------------------------------------


def test_T4_one_drafted_reply_per_issue_naming_its_pull_request():
    from support.markdown_sections import markdown_section

    replies = (ROOT / ".gnd-planning/milestones/reviewed-vocabulary-growth/notes/issue-replies.md").read_text()
    headings = {line.split(":")[0][len("## Issue "):]: line for line in replies.splitlines()
                if line.startswith("## Issue ")}
    for issue, pull in (("221", "pull request 239"), ("222", "pull request 240"), ("218", "pull request 240")):
        section = markdown_section(replies, headings[issue])
        assert pull in section, issue
        assert "release" in section, issue


# --- T5: the pages cite the homes ---------------------------------------------


def test_T5_the_growth_page_and_the_agents_pages_link_the_section_and_the_homes():
    growth = (ROOT / "src/gnd/skills/gnd-model-from-text/references/unattended-growth.md").read_text()
    section = growth[growth.index("## Starting from a reviewed vocabulary"):growth.index("## Evidence for Steps 3 to 7")]
    assert "representation-format.md#an-unattended-root-that-includes-a-reviewed-model" in section
    assert "provenance-and-modality.md#evolve-admission-d-12" in section
    assert "src/gnd/examples/seeded_growth/" in section
    for page in ("docs/agents/model-from-text.md", "docs/agents/evolve.md"):
        assert "unattended-growth.md#starting-from-a-reviewed-vocabulary" in (ROOT / page).read_text(), page


# --- review round 1 (notes/reviews/phase-VG5-r1), regression cases ----------


def test_R1_F1_the_route_list_names_discover_which_resolves_an_include_root(grown):
    """F1: gnd discover resolves an include root, and the list said every unlisted route refuses."""
    from gnd.discover.service import discover

    result = discover(grown / "root.orm.yaml", grown / "population.json", families=("mandatory",),
                      max_values=20, max_pairs=256)
    assert result is not None
    assert "| `gnd discover` |" in _route_list()


def test_R1_F2_a_fenced_heading_inside_a_reply_does_not_end_its_section():
    from support.markdown_sections import markdown_section

    text = ("## Issue 221: x\n\n```markdown\n## Example output\n```\n\npull request 239; not released.\n\n"
            "## Issue 222: y\n\nother\n")
    section = markdown_section(text, "## Issue 221: x")
    assert "pull request 239" in section and "other" not in section
