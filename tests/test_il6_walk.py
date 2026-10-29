"""IL6: the learners walk, its shipped learner outputs and the generated comparison table.

T1 runs the ``learners`` commands page. T2 pins the SHA-256 of every file it
writes under two hash seeds. T3 checks each shipped learner output against its
evidence file and scans the page and the shipped files. T4 regenerates the
comparison table and compares it with the golden and with ``ilp-bridge.md``.
T5 ties each row's import result to the walk's block and the phase's
``outcome.json``. T6 checks the reference pages name what the milestone shipped.
Spec: ``.gnd-planning/milestones/ilp-learners/notes/phase-IL6-spec.md`` §8.
"""

import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".gnd-planning/milestones/ilp-learners/evidence"
EXAMPLES = ROOT / "src/gnd/examples"
IL6 = ROOT / "tests/fixtures/ilp_learners/il6"
IL4 = ROOT / "tests/fixtures/ilp_learners/il4"
PAGE = ROOT / "docs/how-to/compare-ilp-learners.md"
BRIDGE = ROOT / "docs/reference/ilp-bridge.md"
# Each shipped learner output and the evidence (or fixture) file it copies byte for byte (IL6-D2).
SHIPPED = {
    "refunds/learners/popper/program.pl": EVIDENCE / "IL1/live/invocation-3/program.pl",
    "refunds/learners/popper/run.json": EVIDENCE / "IL1/live/invocation-3/run.json",
    "refunds/learners/ilasp/hypothesis.las": EVIDENCE / "IL2/live/invocation-1/hypothesis.las",
    "refunds/learners/ilasp/run.json": EVIDENCE / "IL2/live/invocation-1/run.json",
    "refunds/learners/llm/answer.json": EVIDENCE / "IL5/live/invocation-1/answer.json",
    "refunds/learners/llm/run.json": EVIDENCE / "IL5/live/invocation-1/run.json",
    "refunds/learners/rules/ruleset.txt": EVIDENCE / "IL3/live/invocation-1/ruleset.txt",
    "refunds/learners/rules/run.json": EVIDENCE / "IL3/live/invocation-1/run.json",
    "staffing/model.orm.yaml": IL4 / "model.orm.yaml",
    "staffing/population.yaml": IL4 / "population.yaml",
    "staffing/learners/amie/rules.txt": EVIDENCE / "IL4/live/invocation-1/rules.txt",
    "staffing/learners/amie/reported.json": EVIDENCE / "IL4/live/invocation-1/reported.json",
    "staffing/learners/amie-2/rules.txt": EVIDENCE / "IL4/live/invocation-2/rules.txt",
    "staffing/learners/amie-2/reported.json": EVIDENCE / "IL4/live/invocation-2/reported.json",
}
# The learner directory an import block reads, and the table row it replays.
REPLAYS = {"popper": ("popper", 3), "ilasp": ("ilasp", 1), "llm": ("llm", 1), "rules": ("rules", 1),
           "amie": ("amie", 1), "amie-2": ("amie", 2)}
OUTCOMES = {("popper", 1): "IL1/live/invocation-1", ("popper", 2): "IL1/live/invocation-2",
            ("popper", 3): "IL1/live/invocation-3", ("ilasp", 1): "IL2/live/invocation-1",
            ("llm", 1): "IL5/live/invocation-1", ("rules", 1): "IL3/live/invocation-1",
            ("amie", 1): "IL4/live/invocation-1", ("amie", 2): "IL4/live/invocation-2"}
WRITTEN = [
    "export/popper/export.json",
    "export/ilasp/export.json",
    "export/neutral/export.json",
    "export/rules/export.json",
    "export/amie/export.json",
    "popper.proposal.json",
    "llm.proposal.json",
    "rules.proposal.json",
    "amie-2.proposal.json",
]
# SHA-256 of the downstream application names this public repository never prints.
DOWNSTREAM = {
    "056383fda2d7ac0404a022ddbc187ebea369e6fdd0ffb479de7322366dd871eb",
    "615617073e571553aab0eb7edefdfd68284bf02966692afeff82a451f1b7a4e5",
}
ABSOLUTE = [r"/Users/", r"/home/", r"/private/", r"/tmp/", r"/var/folders/", r"/opt/", r"~/",
            r"\b[A-Za-z]:[\\/]"]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = _load("run_tutorials", ROOT / "tools/run_tutorials.py")


def _comparison():
    return _load("ilp_comparison", ROOT / "tools/ilp_comparison.py")


def _golden() -> dict:
    return json.loads((IL6 / "comparison.json").read_text(encoding="utf-8"))


def _rows() -> dict[tuple[str, int], dict]:
    doc = _golden()
    return {(row["adapter"], row["invocation"]): row for row in doc["labelled"] + doc["unlabelled"]}


def walk_digests(cwd: Path) -> dict[str, str]:
    """Run the learners page in cwd and return each written file's digest, the run directory normalized."""
    python = Path(os.environ.get("GND_TUTORIAL_PYTHON", sys.executable)).absolute()
    assert runner.run_pages(runner.groups(ROOT)["learners"], cwd, python) > 0
    return {name: hashlib.sha256(runner.without_run_dir((cwd / name).read_bytes(), cwd)).hexdigest()
            for name in WRITTEN}


# -- T1, T2: the walk runs and writes the golden files ----------------------

def test_t1_t2_the_walk_writes_the_golden_files_under_two_hash_seeds(tmp_path, monkeypatch):
    golden = json.loads((IL6 / "walk-goldens.json").read_text(encoding="utf-8"))
    runs = []
    for seed in ("0", "1"):
        monkeypatch.setenv("PYTHONHASHSEED", seed)
        runs.append(walk_digests(tmp_path / f"seed-{seed}"))
    assert runs[0] == runs[1]
    assert runs[0] == golden["files"]


def test_t2_the_goldens_name_exactly_the_written_files():
    assert sorted(json.loads((IL6 / "walk-goldens.json").read_text(encoding="utf-8"))["files"]) == sorted(WRITTEN)


def test_t1_the_learners_group_is_the_page_alone():
    assert runner.groups(ROOT)["learners"] == [PAGE]


# -- T3: shipped outputs and privacy ----------------------------------------

@pytest.mark.parametrize("shipped", sorted(SHIPPED))
def test_t3_a_shipped_output_equals_its_evidence(shipped):
    assert (EXAMPLES / shipped).read_bytes() == SHIPPED[shipped].read_bytes()


def test_t3_the_learner_directories_ship_nothing_else():
    found = {str(p.relative_to(EXAMPLES)) for d in ("refunds/learners", "staffing")
             for p in (EXAMPLES / d).rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert found == set(SHIPPED) | {"staffing/README.md"}


def _public_texts():
    paths = sorted(EXAMPLES / name for name in SHIPPED) + [EXAMPLES / "staffing/README.md", PAGE]
    return [(p, p.read_text(encoding="utf-8")) for p in paths]


@pytest.mark.parametrize("pattern", ABSOLUTE)
def test_t3_no_absolute_path_in_the_page_or_the_shipped_files(pattern):
    leaked = [str(p.relative_to(ROOT)) for p, text in _public_texts() if re.search(pattern, text)]
    assert leaked == []


def test_t3_no_downstream_name_in_the_page_or_the_shipped_files():
    leaked = []
    for path, text in _public_texts():
        for token in set(re.findall(r"[a-z][a-z0-9_-]+", text.lower())):
            if hashlib.sha256(token.encode()).hexdigest() in DOWNSTREAM:
                leaked.append(str(path.relative_to(ROOT)))
    assert leaked == []


def test_t3_the_walk_writes_no_run_directory(tmp_path):
    walk_digests(tmp_path)
    for name in WRITTEN:
        text = (tmp_path / name).read_text(encoding="utf-8")
        assert str(tmp_path) not in text and str(tmp_path.resolve()) not in text, name
        assert not any(re.search(p, text) for p in ABSOLUTE), name
    # The page says a refused import writes nothing (IL6 review R6b).
    assert not (tmp_path / "ilasp.proposal.json").exists() and not (tmp_path / "amie.proposal.json").exists()


# -- T4: the generated table ------------------------------------------------

def test_t4_the_tool_reproduces_the_golden():
    assert _comparison().build(ROOT) == _golden()


def test_t4_the_bridge_page_holds_the_generated_table():
    tool = _comparison()
    text = BRIDGE.read_text(encoding="utf-8")
    start, end = text.index(tool.START), text.index(tool.END)
    assert text[start + len(tool.START):end] == "\n" + tool.markdown(_golden()) + "\n"


def test_t4_the_table_names_every_row_once():
    tool = _comparison()
    table = tool.markdown(_golden())
    for adapter, invocation in _rows():
        assert len(re.findall(rf"^\| {adapter}\b[^|]*\| {invocation} \|", table, re.MULTILINE)) == 1, (adapter, invocation)


def _evidence_copy(root: Path) -> Path:
    """The inputs build() reads, copied under root so a test can change one of them."""
    tool = _comparison()
    for relative in (tool.EVIDENCE, tool.STAFFING):
        shutil.copytree(ROOT / relative, root / relative)
    return root / tool.EVIDENCE


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, path
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _double_operations(path: Path) -> None:
    proposal = json.loads(path.read_text(encoding="utf-8"))
    proposal["operations"] = proposal["operations"] + proposal["operations"]
    path.write_text(json.dumps(proposal), encoding="utf-8")


def _drop_last_rule(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    rules = [i for i, line in enumerate(lines) if "=>" in line]
    del lines[rules[-1]]
    path.write_text("".join(lines), encoding="utf-8")


# Each case changes one input the row is derived from; build() must report the change (IL6 review R4).
@pytest.mark.parametrize("change, section, row, field, value", [
    (lambda e: _replace(e / "IL2/live/invocation-1/import-stderr.txt", "clause 0:", "clause 1:"),
     "labelled", 3, "first_refusal", {"name": "empty-antecedent", "index": 1}),
    (lambda e: _replace(e / "IL3/live/invocation-1/outcome.json", '"import_exit": 0', '"import_exit": 2'),
     "labelled", 5, "import_exit", 2),
    (lambda e: _double_operations(e / "IL5/live/invocation-1/proposal.json"), "labelled", 4, "clauses_admitted", 2),
    (lambda e: _drop_last_rule(e / "IL4/live/invocation-2/rules.txt"), "unlabelled", 1, "rules_mined", 1),
    (lambda e: _drop_last_rule(e / "IL4/live/invocation-2/rules.txt"), "unlabelled", 1, "rules_hold", 1),
])
def test_t4_a_changed_input_changes_its_row(tmp_path, change, section, row, field, value):
    evidence = _evidence_copy(tmp_path)
    change(evidence)
    built = _comparison().build(tmp_path)
    assert built[section][row][field] == value
    assert _golden()[section][row][field] != value


# -- T5: each row agrees with the walk and its outcome.json ----------------

def _import_blocks():
    out = {}
    for language, expected, code, _lane, stream, shown in runner._parsed(PAGE):
        if language == "sh" and "gnd import" in code:
            directory = re.search(r"learners/([a-z0-9-]+)/", code).group(1)
            out[REPLAYS[directory]] = (expected, stream, shown)
    return out


def test_t5_every_imported_row_is_replayed_by_the_walk():
    imported = {key for key, row in _rows().items() if row["import_exit"] is not None}
    assert set(_import_blocks()) == imported


@pytest.mark.parametrize("key", sorted(OUTCOMES))
def test_t5_a_row_agrees_with_its_outcome_and_the_walk(key):
    row = _rows()[key]
    outcome = json.loads((EVIDENCE / OUTCOMES[key] / "outcome.json").read_text(encoding="utf-8"))
    assert (row["termination"], row["import"], row["run_of_record"]) == (
        outcome["termination"], outcome["import"], outcome["run_of_record"])
    assert row["import_exit"] == outcome.get("import_exit")
    block = _import_blocks().get(key)
    if row["import_exit"] is None:
        assert block is None
        return
    expected, stream, shown = block
    assert expected == row["import_exit"]
    if row["first_refusal"] is None:
        assert expected == 0
    else:
        assert stream == "stderr"
        first = shown.strip().splitlines()[0]
        assert first.startswith(f"{'rule' if key[0] == 'amie' else 'clause'} {row['first_refusal']['index']}: "
                                f"{row['first_refusal']['name']}: ")


# -- T6: the reference pages ------------------------------------------------

def test_t6_the_reference_pages_name_every_target_and_import():
    from gnd.export.ilp_learners import LEARNERS

    cli = (ROOT / "docs/reference/cli.md").read_text(encoding="utf-8")
    capabilities = (ROOT / "docs/reference/capabilities.md").read_text(encoding="utf-8")
    bridge = BRIDGE.read_text(encoding="utf-8")
    for target in LEARNERS:
        for name, text in (("cli.md", cli), ("capabilities.md", capabilities), ("ilp-bridge.md", bridge)):
            assert f"`{target}`" in text or f"--target {target}" in text, (name, target)
    for text in (cli, capabilities):
        assert "mined-rules" in text and "ilp-rules" in text
    assert "--population" in cli


def test_t6_one_bridge_section_per_adapter_names_its_refusals():
    from gnd.export import ilp_amie, ilp_asp, ilp_rewrite, ilp_rules, ilp_service

    bridge = BRIDGE.read_text(encoding="utf-8")
    names = (ilp_rewrite.REFUSALS + ilp_asp.REFUSALS + ilp_rules.REFUSALS + ilp_rules.EXPORT_REFUSALS
             + ilp_amie.EXPORT_REFUSALS + ilp_amie.MAPPING_REFUSALS + ilp_amie.COUNT_REFUSALS
             + ilp_service.MINED_INPUT_REFUSALS)
    assert [name for name in names if f"`{name}`" not in bridge] == []


def test_t6_no_stale_popper_caveat():
    for path in (BRIDGE, ROOT / "docs/reference/capabilities.md"):
        text = path.read_text(encoding="utf-8").lower()
        assert "not been run against a real popper" not in text, path.name
        assert "untested against a real popper" not in text, path.name


def test_t6_the_release_notes_name_the_milestone_additions():
    notes = (ROOT / "docs/release-notes.md").read_text(encoding="utf-8")
    for token in ("--target ilasp", "--target rules", "--target amie", "gnd import mined-rules", "compare-ilp-learners"):
        assert token in notes, token
