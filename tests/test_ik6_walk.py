"""IK6: the refunds walk's written files, its privacy and the stand-in learner's determinism.

T2 runs the commands page twice, with different PYTHONHASHSEED values, and pins
the SHA-256 of every file the walk writes. T3 checks the example and both pages
for absolute paths, downstream names and non-opaque induction ids. T8 runs the
stand-in learner twice on one export and requires byte-identical output.
"""

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/refunds"
GOLDENS = ROOT / "tests/fixtures/induced_knowledge/ik6-walk/goldens.json"
PAGES = [ROOT / "docs/tutorials/learn-rules.md", ROOT / "docs/how-to/learn-rules-commands.md"]
WRITTEN = [
    "measure.json",
    "discovered.json",
    "discover-report.json",
    "ilp/export.json",
    "learned/learned.clauses.json",
    "learned/learned.run.json",
    "learned.proposal.json",
    "discovered.preview.json",
    "learned.preview.json",
    "model.orm.yaml",
    "model.verbalization.txt",
]
# SHA-256 of the downstream application names this public repository never prints.
DOWNSTREAM = {
    "056383fda2d7ac0404a022ddbc187ebea369e6fdd0ffb479de7322366dd871eb",
    "615617073e571553aab0eb7edefdfd68284bf02966692afeff82a451f1b7a4e5",
}

spec = importlib.util.spec_from_file_location("run_tutorials", ROOT / "tools/run_tutorials.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def walk_digests(cwd: Path) -> dict[str, str]:
    """Run the commands page in cwd and return each written file's digest, the run directory normalized."""
    python = Path(os.environ.get("GND_TUTORIAL_PYTHON", sys.executable)).absolute()
    assert runner.run_pages(runner.groups(ROOT)["induced"], cwd, python) > 0
    digests = {}
    for name in WRITTEN:
        text = (cwd / name).read_bytes()
        for root in sorted({str(cwd), str(cwd.resolve())}, key=len, reverse=True):
            text = text.replace(root.encode(), b"<run>")
        digests[name] = hashlib.sha256(text).hexdigest()
    return digests


def test_t2_the_walk_writes_the_golden_files_under_two_hash_seeds(tmp_path, monkeypatch):
    golden = json.loads(GOLDENS.read_text(encoding="utf-8"))
    runs = []
    for seed in ("0", "4242"):
        monkeypatch.setenv("PYTHONHASHSEED", seed)
        runs.append(walk_digests(tmp_path / f"seed-{seed}"))
    assert runs[0] == runs[1]
    assert runs[0] == golden["files"]


def test_t2_the_goldens_name_exactly_the_written_files():
    assert sorted(json.loads(GOLDENS.read_text(encoding="utf-8"))["files"]) == sorted(WRITTEN)


def _public_texts():
    paths = sorted(p for p in EXAMPLE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return [(p, p.read_text(encoding="utf-8")) for p in paths + PAGES]


ABSOLUTE = [r"/Users/", r"/home/", r"/private/", r"/tmp/", r"/var/folders/", r"/opt/", r"~/",
            r"\b[A-Za-z]:[\\/]"]


def test_t3_the_path_patterns_match_real_paths():
    samples = ["/Users/me/x", "/home/me/x", "/private/tmp/x", "/tmp/x", "/var/folders/ab/x", "/opt/x",
               "~/x", "C:\\Users\\me", "D:/work", "C:\\\\Users"]
    assert [s for s in samples if not any(re.search(p, s) for p in ABSOLUTE)] == []


@pytest.mark.parametrize("pattern", ABSOLUTE)
def test_t3_no_absolute_path_in_the_example_or_its_pages(pattern):
    leaked = [str(p.relative_to(ROOT)) for p, text in _public_texts() if re.search(pattern, text)]
    assert leaked == []


def test_t3_the_walk_writes_no_run_directory_and_only_batch_ids(tmp_path):
    walk_digests(tmp_path)
    for name in WRITTEN:
        text = (tmp_path / name).read_text(encoding="utf-8")
        assert str(tmp_path) not in text and str(tmp_path.resolve()) not in text, name
        assert not any(re.search(p, text) for p in ABSOLUTE), name
    labels = json.loads((EXAMPLE / "labels.json").read_text(encoding="utf-8"))
    ids = {p["id"] for p in labels["populations"]}
    proposal = json.loads((tmp_path / "learned.proposal.json").read_text(encoding="utf-8"))
    blocks = [op["after"]["provenance"]["induction"] for op in proposal["operations"]]
    assert blocks and all(set(b["examples"]) <= ids for b in blocks)


def test_t3_no_downstream_name_in_the_example_or_its_pages():
    leaked = []
    for path, text in _public_texts():
        for token in set(re.findall(r"[a-z][a-z0-9_-]+", text.lower())):
            if hashlib.sha256(token.encode()).hexdigest() in DOWNSTREAM:
                leaked.append(str(path.relative_to(ROOT)))
    assert leaked == []


def test_t3_the_learned_proposal_names_batches_by_opaque_id_only(tmp_path):
    subprocess.run([sys.executable, "-m", "gnd", "export", "ilp", str(EXAMPLE / "model.orm.yaml"),
                    "--labels", str(EXAMPLE / "labels.json"), "--target", "neutral", "--out", str(tmp_path / "ilp")],
                   check=True, capture_output=True)
    subprocess.run([sys.executable, str(EXAMPLE / "stand_in_learner.py"), str(tmp_path / "ilp"), str(tmp_path / "out")],
                   check=True, capture_output=True)
    labels = json.loads((EXAMPLE / "labels.json").read_text(encoding="utf-8"))
    ids = {p["id"] for p in labels["populations"]}
    run = json.loads((tmp_path / "out/learned.run.json").read_text(encoding="utf-8"))
    covered = {e for row in run["coverage"] for e in row["covered"]}
    assert covered and covered <= ids
    assert all(re.fullmatch(r"[a-z]+", i) for i in ids)


def _learn(export: Path, out: Path, *extra: str) -> dict[str, bytes]:
    subprocess.run([sys.executable, str(EXAMPLE / "stand_in_learner.py"), str(export), str(out), *extra],
                   check=True, capture_output=True)
    return {name: (out / name).read_bytes() for name in ("learned.clauses.json", "learned.run.json")}


def test_t8_the_stand_in_learner_is_deterministic(tmp_path):
    subprocess.run([sys.executable, "-m", "gnd", "export", "ilp", str(EXAMPLE / "model.orm.yaml"),
                    "--labels", str(EXAMPLE / "labels.json"), "--target", "neutral", "--out", str(tmp_path / "ilp")],
                   check=True, capture_output=True)
    first = _learn(tmp_path / "ilp", tmp_path / "a")
    second = _learn(tmp_path / "ilp", tmp_path / "b")
    assert first == second
    faulty = _learn(tmp_path / "ilp", tmp_path / "c", "--also-claim", "north")
    assert faulty["learned.clauses.json"] == first["learned.clauses.json"]
    true_cover = json.loads(first["learned.run.json"])["coverage"][0]["covered"]
    claimed = json.loads(faulty["learned.run.json"])["coverage"][0]["covered"]
    assert sorted(claimed) == sorted(true_cover + ["north"]) and "north" not in true_cover


@pytest.mark.parametrize("argv", [
    ["--also-claim", "nort"],      # not a batch
    ["--also-claim", "harbor"],    # already covered: the claim would not be false
    ["--also-claim"],              # no value
    ["--also_claim", "north"],     # misspelt flag
])
def test_h3_a_bad_learner_argument_is_a_usage_error(tmp_path, argv):
    subprocess.run([sys.executable, "-m", "gnd", "export", "ilp", str(EXAMPLE / "model.orm.yaml"),
                    "--labels", str(EXAMPLE / "labels.json"), "--target", "neutral", "--out", str(tmp_path / "ilp")],
                   check=True, capture_output=True)
    result = subprocess.run([sys.executable, str(EXAMPLE / "stand_in_learner.py"), str(tmp_path / "ilp"),
                             str(tmp_path / "out"), *argv], capture_output=True, text=True)
    assert result.returncode == 2 and "usage:" in result.stderr
    assert not (tmp_path / "out").exists()


def test_h3_missing_arguments_are_a_usage_error():
    result = subprocess.run([sys.executable, str(EXAMPLE / "stand_in_learner.py")], capture_output=True, text=True)
    assert result.returncode == 2 and "usage:" in result.stderr


# Each number the business tutorial states, beside the commands-page output it restates.
TUTORIAL_CLAIMS = [
    ("2 of 4 (harbor, airport)", "fired_on_negative=2/4 fired_on_positive=0/4 silent_on_negative=2/4"),
    ("tries 40 simple rules", "searched 40 rules"),
    ("support 4 of 4", "covers 4 (support 4/4)"),
    ("**4 of 4** | 0 of 4", "covers harbor, market, airport, station"),
    ("ten rules held in that week", "EMITTED 10"),
    ("It left out four more", "SUPPRESSED declared=1 spanning-uniqueness=3"),
    ("neither proposal is breaking", "  breaking: false\n  breaking: false"),
    ("is at most 500", "then $v_v1 is at most 500."),
    ("**warning** on refund 601, for 750", "{'$v_v0': '601', '$v_v1': '750'}"),
]


@pytest.mark.parametrize("tutorial, commands", TUTORIAL_CLAIMS)
def test_c1_the_tutorial_numbers_match_the_commands_page(tutorial, commands):
    assert tutorial in PAGES[0].read_text(encoding="utf-8")
    assert commands in PAGES[1].read_text(encoding="utf-8")


def test_c2_south_is_never_over_500_not_under_it():
    for path in (PAGES[0], ROOT / "docs/assets/applications/refunds-weeks.svg"):
        text = path.read_text(encoding="utf-8")
        assert "under 500" not in text and "never go over 500" in text, path.name
