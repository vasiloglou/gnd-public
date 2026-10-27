"""Regressions for the induced-knowledge milestone close (close spec §5a)."""

import re
import typing
from pathlib import Path

from gnd.evolve.models import BlastRadiusEntry

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src/gnd/skills/gnd-model-evolve/references/evolution-contract.md"


PROVENANCE = ROOT / "src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md"


def reference_d03_table() -> dict[tuple[str, str], str]:
    """The D-03 default table as its one home states it: (source, status) -> modality."""
    text = PROVENANCE.read_text(encoding="utf-8")
    block = text.split("### Default modality table (source × status)", 1)[1].split("Reading the table", 1)[0]
    table = {}
    for line in block.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        source = re.fullmatch(r"`([a-z-]+)`", cells[0])
        if len(cells) != 3 or not source:
            continue
        for status, cell in zip(("proposed", "confirmed"), cells[1:]):
            modality = re.match(r"\*\*(alethic|deontic)\*\*", cell)
            if modality:
                table[(source.group(1), status)] = modality.group(1)
    return table


def test_ik2_q2_rai_import_reads_the_one_d03_table():
    from gnd import rai_import

    assert rai_import.D03_DEFAULTS == reference_d03_table()
    assert len(rai_import.D03_DEFAULTS) == 12


def test_ik2_q2_rai_import_default_follows_every_d03_row():
    from gnd.rai_import import RaiImportError, _default_modality

    for (source, status), expected in reference_d03_table().items():
        constraint = {"source": source, "status": status, "provenance": {"reviewed_in": "r.md"}}
        assert _default_modality(constraint, "/c") == expected
    for source in ("explicit", "user-supplied"):
        try:
            _default_modality({"source": source, "status": "proposed"}, "/c")
        except RaiImportError as refused:
            assert "no D-03 default exists" in str(refused)
        else:
            raise AssertionError(f"{source}/proposed has no D-03 default")


def test_ik3_q2_a_population_path_must_match_the_on_disk_spelling(tmp_path):
    """On a case-insensitive file system an alias spelling used to be read (exit 0
    on macOS, exit 3 on Linux). It is now refused as missing on every host."""
    import pytest

    from gnd.measure.labels import LabelError, _population_bytes

    (tmp_path / "pops").mkdir()
    (tmp_path / "pops" / "ok.yaml").write_text("facts: {}\n", encoding="utf-8")
    assert _population_bytes(tmp_path, "pops/ok.yaml")[1] == b"facts: {}\n"
    for alias in ("pops/OK.yaml", "POPS/ok.yaml"):
        with pytest.raises(LabelError) as refused:
            _population_bytes(tmp_path, alias)
        assert refused.value.code == 3
        assert str(refused.value) == f"population {alias!r} does not exist"


def test_ik3_q4_a_model_changed_while_it_is_read_is_refused(tmp_path, monkeypatch):
    """The model is digested before and after loading; an edit in between is exit 3."""
    import json
    import shutil

    from support.cli_runner import run_main

    from gnd import safefs

    work = tmp_path / "refunds"
    shutil.copytree(ROOT / "src/gnd/examples/refunds", work, ignore=shutil.ignore_patterns("__pycache__"))
    model = work / "model.orm.yaml"
    argv = ["measure", str(model), "--labels", str(work / "labels.json"), "--format", "json"]
    assert run_main(argv).returncode == 0

    real, calls = safefs.file_sha256, []

    def digest_then_edit(path, *args, **kwargs):
        value = real(path, *args, **kwargs)
        if not calls and path == model:
            model.write_text(model.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
        calls.append(path)
        return value

    monkeypatch.setattr(safefs, "file_sha256", digest_then_edit)
    payload = json.loads(run_main(argv).stdout)
    assert payload["exit_code"] == 3
    assert payload["error"] == f"model {model} changed while it was being read"


AGGREGATE_GOALS = {
    "conjunction": "count((f_order_flagged(A,B), f_order_amount(A,B,C)), N)",
    "negation": r"count(\+ f_order_flagged(A,B), N)",
    "comparison": "count(C > 10, N)",
}


def test_ik5_q3_compound_aggregate_goals_parse_as_aggregates():
    from gnd.export.ilp_popper import parse_program

    for goal in AGGREGATE_GOALS.values():
        body = parse_program(f"wrong(A):- f_order_amount(A,B,C),{goal}.\n")["clauses"][0]["body"]
        assert body[1]["aggregate"]["name"] == "count"


def test_ik5_q3_compound_aggregate_goals_are_refused_by_name(tmp_path):
    from test_ilp_bridge import _popper_import

    for kind, goal in AGGREGATE_GOALS.items():
        result, out = _popper_import(tmp_path / kind, f"wrong(A):- f_order_amount(A,B,C),{goal}.\n")
        assert result.returncode == 3, result.stderr
        assert b"aggregate" in result.stderr and b"unparsable" not in result.stderr, kind
        assert not out.exists()


UNKEPT = ["a\x85b", "a\x7fb", "a b", "a﻿b", "a\U000e0001b", "a\x1fb", "plain é"]


def test_ik5_q4_candidate_text_round_trips_through_evolve_yaml():
    """Characters YAML does not keep raw are written escaped, so evolve's reader
    sees the same constants that discover checked."""
    import datetime

    from gnd.discover.output import candidate_text
    from gnd.evolve.service import _parse_model_text

    for value in UNKEPT:
        for document in ({"values": [value]}, {"values": [value], "on": datetime.date(2026, 10, 27)}):
            assert _parse_model_text(candidate_text(document)) == document, (value, document)


def test_ik5_q6_import_work_counts_candidate_reloads(tmp_path, monkeypatch):
    """Check 10 loads the model plus one clause per clause, then the model plus
    every clause twice; each load is counted and bounded by K + 2."""
    import json

    from test_ilp_bridge import BY_ID, _run

    from gnd.export import ilp_service

    real, loads = ilp_service._load_candidate, []

    def counted(*args, **kwargs):
        loads.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(ilp_service, "_load_candidate", counted)
    result, _out = _run(tmp_path, BY_ID["I1"])
    assert result.returncode == 0, result.stderr
    work = json.loads(result.stdout)["work"]
    clauses = len(json.loads(result.stdout)["clauses"])
    assert work["reloads"] == len(loads) == clauses + 2
    assert work["total"] == work["checks"] + work["verdicts"] + work["reloads"]
    assert work["ceiling"] == work["checks"] * (1 + clauses) + clauses + 2


def test_ik4_q2_q2_invalid_candidate_yaml_is_a_named_exit_3(tmp_path):
    import hashlib
    import json

    from test_evolve_references import _preview, _proposal, _text, _workspace

    from gnd.discover import output

    work = _workspace(tmp_path)
    proposal = _proposal(work)
    data = json.loads(proposal.read_text())
    text = "version: 1\nmodel_id: [unclosed\n"
    data["candidate_model"]["text"] = text
    data["candidate_model"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
    proposal.write_bytes(output.canonical_bytes(data))
    result = _preview(work, proposal)
    assert result.returncode == 3, _text(result)
    assert "candidate model is not valid YAML" in _text(result)


def _text_diff(left, right):
    import os
    import subprocess
    import sys

    process = subprocess.run([sys.executable, "-m", "gnd", "diff", str(left), str(right)], cwd=ROOT,
                             capture_output=True, text=True, check=False,
                             env={**os.environ, "PYTHONHASHSEED": "0"})
    return process.returncode, process.stdout


def test_ik1_q2_text_diff_shows_description_annotations(tmp_path):
    from test_object_type_description import LIBRARY, _write_model

    identical_exit, identical = _text_diff(LIBRARY, LIBRARY)
    assert "ANNOTATION" not in identical
    right = _write_model(tmp_path, {"summary": "a person who borrows\nbooks"}, name="right.orm.yaml")
    code, text = _text_diff(LIBRARY, right)
    assert code == identical_exit
    assert text.startswith(identical.rstrip("\n").split("\n", 1)[0].split(" ")[0])
    assert text.splitlines()[-3:] == [
        "ANNOTATION borrower description",
        "  before null",
        '  after {"summary":"a person who borrows\\nbooks"}',
    ]


def test_ik1_q5_contract_lists_every_blast_radius_surface():
    text = CONTRACT.read_text(encoding="utf-8")
    block = text.split("### BlastRadiusEntry", 1)[1].split("- `change`:", 1)[0]
    listed = set(re.findall(r"`([a-z-]+)`", block.split("- `surface`:", 1)[1]))
    declared = set(typing.get_args(BlastRadiusEntry.model_fields["surface"].annotation))
    assert listed == declared


def test_ik6_r1_the_scans_exempt_examples_by_one_rule():
    from support.scan_scope import exempt, module_sources

    sources = module_sources()
    assert not any(path.startswith("src/gnd/examples/") for path in sources)
    assert "src/gnd/model/__init__.py" in sources and "src/gnd/rai_import.py" in sources
    assert exempt("src/gnd/examples/refunds/stand_in_learner.py")
    assert not exempt("src/gnd/examples.py") and not exempt("src/gnd/skills/gnd-adopt/scripts/verify_migration.py")


def test_ik6_r1_the_runner_normalizes_text_and_bytes(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_tutorials", ROOT / "tools/run_tutorials.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    inside = f"{tmp_path}/a and {tmp_path.resolve()}/b"
    assert runner.without_run_dir(inside, tmp_path) == "<run>/a and <run>/b"
    assert runner.without_run_dir(inside.encode(), tmp_path) == b"<run>/a and <run>/b"


def test_ik4_q2_q2_parse_refusals_name_the_model_they_read():
    """Close reader two: a tagged mapping in a description extra loads, but evolve's
    safe parser refuses it, and a current model must not be called the candidate."""
    import pytest

    from gnd.evolve.service import EvolutionError, _parse_model_text

    text = "version: 1\nobject_types:\n  - {id: a, description: {summary: s, extra: !foo {a: 1}}}\n"
    with pytest.raises(EvolutionError, match=r"^current model is not valid YAML at line 3, column \d+$"):
        _parse_model_text(text, label="current model")
    with pytest.raises(EvolutionError, match=r"^candidate model is not valid YAML at line 3"):
        _parse_model_text(text)
    with pytest.raises(EvolutionError, match=r"^current model is not a mapping$"):
        _parse_model_text("- 1\n", label="current model")


# SHA-256 of the two downstream application names with every separator removed
# and lower-cased (close reader three, F4). This public repository never prints them.
DOWNSTREAM_JOINED = {
    7: "e9eb87c32c4f8d872eb8db64b994e56db871012bbec5d71736cffff54d51a020",
    12: "b9f3e817dbf9539fc43523a639eee23030afc4fc1be1eae4b42962889bea2c3a",
}


def joined_hits(text: str, digests: dict[int, str]) -> bool:
    """True when some window of ``text``, lower-cased with every non-alphanumeric
    character removed, hashes to a digest of that window's length. This catches
    any case, any separator (or none) and any affix."""
    import hashlib

    joined = re.sub(r"[^a-z0-9]", "", text.lower())
    return any(
        hashlib.sha256(joined[start:start + size].encode()).hexdigest() == digest
        for size, digest in digests.items()
        for start in range(len(joined) - size + 1)
    )


def test_close_f4_the_joined_check_catches_every_spelling():
    import hashlib

    placeholder = {7: hashlib.sha256(b"fooapps").hexdigest()}
    for spelling in ["foo-apps", "Foo_Apps", "FooApps", "foo apps", "foo.apps", "xfoo-appsy", "FOO--APPS"]:
        assert joined_hits(f"see {spelling} here", placeholder), spelling
    assert not joined_hits("foo-app", placeholder)


def test_close_f4_no_downstream_name_in_the_milestone_public_text():
    import subprocess

    roots = ["docs", "src/gnd/examples", "src/gnd/skills", ".gnd-planning/milestones/induced-knowledge",
             "tests/fixtures/induced_knowledge", "README.md"]
    listed = subprocess.run(["git", "ls-files", "--", *roots], cwd=ROOT, check=True,
                            capture_output=True, text=True).stdout.split()
    leaked = []
    for name in listed:
        try:
            text = (ROOT / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if joined_hits(text, DOWNSTREAM_JOINED):
            leaked.append(name)
    assert leaked == []
