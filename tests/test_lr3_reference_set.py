"""LR3: the literature reference set, its recorded Sonnet run and its score.

The recorded run replays with zero producer calls; every gate here calls no
model. The producer adapter is tested against a fake ``claude``.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.examples.literature import reading, reference_set
from gnd.examples.literature.depth import ExampleError

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = reference_set.ROOT
CORPUS = ROOT / "src" / "gnd" / "examples" / "literature"
RUN = FIXTURE / "run"
PAGE = ROOT / "docs" / "literature" / "index.md"


def _load_tool():
    spec = importlib.util.spec_from_file_location("record_lr3_reference_run", ROOT / "tools" / "record_lr3_reference_run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TOOL = _load_tool()


def _record() -> dict:
    return json.loads((FIXTURE / "run-record.json").read_bytes())


# --- T1: the root is the corpus overlay, built and unchanged ---------------------------------

def test_t1_the_committed_root_is_the_build_and_the_corpus_is_untouched() -> None:
    built = reference_set.build()
    for name, raw in built.items():
        assert (FIXTURE / name).read_bytes() == raw, name
    corpus = json.loads((CORPUS / "corpus" / "corpus.json").read_bytes())
    dev = [row for row in corpus["documents"] if row["split"] == "dev"]
    assert len(dev) == 12
    for row in dev:
        assert (FIXTURE / f"{row['id']}.txt").read_bytes() == (CORPUS / row["path"]).read_bytes()
    labels = json.loads(built["labels.json"])
    assert labels["counts"] == {"method_builds_on_method": 8, "method_is_used_in_field": 12,
                                "work_introduces_method": 11}
    assert labels["derived_fact_types_left_out"] == ["work_builds_on_method"]
    assert labels["licence"] and all(fact["sections"] for fact in labels["facts"])


# --- T2, T3: the recorded run replays and scores byte for byte -------------------------------

def test_t2_the_recorded_run_replays_with_zero_producer_calls() -> None:
    record = _record()
    replayed = reading.replay(RUN, fixture=FIXTURE, expected_evidence_sha256=record["evidence_sha256"])
    assert replayed["evidence_sha256"] == record["evidence_sha256"]
    assert replayed["read_denominator"] == record["reading"]["read_denominator"]


def test_t3_the_score_and_the_record_name_what_produced_the_figures() -> None:
    assert canonical_json_bytes(reference_set.score(RUN, FIXTURE)) == (FIXTURE / "score.json").read_bytes()
    record = _record()
    assert record["producer"]["model"] == "claude-sonnet-5-5"
    assert record["producer"]["models_seen"] == ["claude-sonnet-5-5"]
    assert record["budget"]["ceiling_usd"] == 50.0
    assert 0 < record["budget"]["spent_usd"] <= 50.0
    assert record["reading"]["read_denominator"]["attempted"] == 46
    score = json.loads((FIXTURE / "score.json").read_bytes())
    assert set(score["stages"]) == {"broad", "targeted"}
    assert score["gold_facts"] == 31


# --- T4: the scoring rule ----------------------------------------------------------------------

def _root_with_labels(tmp_path: Path, facts: list[dict]) -> Path:
    root = tmp_path / "root"
    root.mkdir()
    shutil.copyfile(FIXTURE / "roster.json", root / "roster.json")
    labels = json.loads((FIXTURE / "labels.json").read_bytes())
    labels["facts"] = facts
    (root / "labels.json").write_bytes(canonical_json_bytes(labels))
    return root


def _run_with(tmp_path: Path, broad: list[dict], targeted: list[dict]) -> Path:
    run = tmp_path / "run"
    run.mkdir(parents=True)
    for name, attempts in (("payload-1.json", broad), ("payload-3.json", targeted)):
        (run / name).write_bytes(canonical_json_bytes({"attempts": attempts}))
    return run


def _attempt(section: str, facts: dict) -> dict:
    return {"section": section, "response": {"outcome": "accepted" if facts else "empty", "facts": facts,
                                             "proposal_keys": []}}


GOLD = {"document": "vampnet", "fact_type": "method_builds_on_method",
        "roles": {"method": "VampNet", "base_method": "bidirectional transformer"}, "sections": ["vampnet-p2"]}


def test_t4_found_wrong_predicate_and_wrong_section_are_told_apart(tmp_path: Path) -> None:
    root = _root_with_labels(tmp_path, [GOLD])
    right = {"method_builds_on_method": [{"method": "vampnet", "base_method": "Bidirectional  Transformer"}]}
    swapped = {"method_is_used_in_field": [{"method": "VampNet", "field": "bidirectional transformer"}]}
    run = _run_with(tmp_path, [_attempt("vampnet-p1", right)],
                    [_attempt("vampnet-p2", swapped), _attempt("vampnet-p3", right)])
    score = reference_set.score(run, root)
    assert score["stages"]["broad"] == {"produced": 1, "found": 0, "wrong_predicate": 0,
                                        "outside_gold_scope": 1, "precision": [0, 1]}
    assert score["stages"]["targeted"]["wrong_predicate"] == 1
    assert score["stages"]["targeted"]["found"] == 0
    assert score["recall_after"] == {"broad": [0, 1], "targeted": [0, 1]}
    found = _run_with(tmp_path / "b", [], [_attempt("vampnet-p2", right)])
    assert reference_set.score(found, root)["recall_after"]["targeted"] == [1, 1]


def test_t4_a_gold_fact_counts_once_and_every_row_counts_in_precision(tmp_path: Path) -> None:
    root = _root_with_labels(tmp_path, [GOLD])
    right = {"method_builds_on_method": [{"method": "VampNet", "base_method": "bidirectional transformer"}] * 2}
    score = reference_set.score(_run_with(tmp_path, [], [_attempt("vampnet-p2", right)]), root)
    assert score["stages"]["targeted"]["precision"] == [2, 2]
    assert score["recall_after"]["targeted"] == [1, 1]


# --- T6, T7: what changes the figure, what refuses -------------------------------------------

def test_t6_a_changed_gold_fact_changes_the_figure(tmp_path: Path) -> None:
    labels = json.loads((FIXTURE / "labels.json").read_bytes())
    found = reference_set.score(RUN, FIXTURE)["recall_after"]["targeted"][0]
    if found == 0:
        pytest.skip("the recorded run found no gold fact to change")
    original = reference_set.score(RUN, FIXTURE)
    for index in range(len(labels["facts"])):
        changed = json.loads(json.dumps(labels))
        role = min(changed["facts"][index]["roles"])
        changed["facts"][index]["roles"][role] += " (changed)"
        root = tmp_path / f"r{index}"
        root.mkdir()
        shutil.copyfile(FIXTURE / "roster.json", root / "roster.json")
        (root / "labels.json").write_bytes(canonical_json_bytes(changed))
        if reference_set.score(RUN, root) != original:
            return
    pytest.fail("no single changed gold fact changed the score")


def _copy_run(tmp_path: Path) -> tuple[Path, Path]:
    root, run = tmp_path / "root", tmp_path / "root" / "run"
    shutil.copytree(FIXTURE, root)
    return root, run


def test_t7_a_changed_response_refuses_replay(tmp_path: Path) -> None:
    root, run = _copy_run(tmp_path)
    table = json.loads((run / "producer-output-table.json").read_bytes())
    section = min(table)
    table[section] = {"outcome": "refused", "facts": {}, "proposal_keys": []}
    (run / "producer-output-table.json").write_bytes(canonical_json_bytes(table))
    with pytest.raises(ExampleError):
        reading.replay(run, fixture=root, expected_evidence_sha256=_record()["evidence_sha256"])


def test_t7_a_changed_source_byte_refuses_replay(tmp_path: Path) -> None:
    root, run = _copy_run(tmp_path)
    source = root / "vampnet.txt"
    raw = bytearray(source.read_bytes())
    raw[-2] = ord("X") if raw[-2] != ord("X") else ord("Y")
    source.write_bytes(bytes(raw))
    with pytest.raises(ExampleError):
        reading.replay(run, fixture=root, expected_evidence_sha256=_record()["evidence_sha256"])


# --- T8: hostile score inputs -------------------------------------------------------------------

@pytest.mark.parametrize("payload", [b"not json", b"[]", b'{"attempts": 3}', b'{"attempts": [{"section": "nope"}]}',
                                     b'{"attempts": [{"section": "vampnet-p2", "response": {"facts": {"x": [1]}}}]}'])
def test_t8_a_malformed_run_refuses(tmp_path: Path, payload: bytes) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "payload-1.json").write_bytes(payload)
    (run / "payload-3.json").write_bytes(b'{"attempts": []}')
    with pytest.raises(ExampleError):
        reference_set.score(run, FIXTURE)


# --- T9: the producer adapter, against a fake claude -------------------------------------------

def _fake_claude(tmp_path: Path, output: dict, *, code: int = 0, cost: float = 0.01,
                 models: tuple[str, ...] = ("claude-sonnet-5-5",)) -> tuple[str, ...]:
    script = tmp_path / "claude"
    reply = {"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": cost,
             "modelUsage": {model: {} for model in models}, "structured_output": output}
    script.write_text(f"import json, sys\nsys.stdin.read()\nprint(json.dumps({reply!r}))\nsys.exit({code})\n")
    return (sys.executable, str(script))


def _call() -> reading.ProducerCall:
    text = (FIXTURE / "vampnet.txt").read_bytes()[:60]
    return reading.ProducerCall(stage="broad-extraction", section="vampnet-p1", source="vampnet",
                                source_version="corpus-1", kind="section", start=0, end=60, excerpt=text,
                                excerpt_sha256="0" * 64, questions=())


def _producer(command: tuple[str, ...], ceiling: float = 50.0):
    model = json.loads((FIXTURE / reference_set.MODEL).read_bytes())
    return TOOL.ClaudeCliProducer(model, command=command, ceiling=ceiling)


def test_t9_no_facts_is_empty_and_foreign_rows_are_dropped(tmp_path: Path) -> None:
    output = {"facts": {"work_builds_on_method": [{"work": "w", "method": "m"}], "nope": [{"a": "b"}],
                        "method_is_used_in_field": [{"method": "VampNet"}]}}
    answer = _producer(_fake_claude(tmp_path, output)).produce(_call())
    assert answer == {"outcome": "empty", "facts": {}, "proposal_keys": []}


def test_t9_kept_rows_are_accepted(tmp_path: Path) -> None:
    row = {"method": "VampNet", "field": "music"}
    answer = _producer(_fake_claude(tmp_path, {"facts": {"method_is_used_in_field": [row]}})).produce(_call())
    assert answer == {"outcome": "accepted", "facts": {"method_is_used_in_field": [row]}, "proposal_keys": []}


def test_t9_a_cli_error_another_model_or_the_ceiling_raises(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        _producer(_fake_claude(tmp_path, {"facts": {}}, code=1)).produce(_call())
    with pytest.raises(RuntimeError):
        _producer(_fake_claude(tmp_path, {"facts": {}}, models=("claude-haiku-5-5",))).produce(_call())
    with pytest.raises(TOOL.SpendError):
        _producer(_fake_claude(tmp_path, {"facts": {}}), ceiling=0.5).produce(_call())


# --- T5: the page shows the measured figures, the rule and the comparison ----------------------

def test_t5_the_page_shows_the_recorded_figures_beside_issue_226() -> None:
    page = " ".join(PAGE.read_text(encoding="utf-8").split())
    score = json.loads((FIXTURE / "score.json").read_bytes())
    gold = score["gold_facts"]
    broad, targeted = score["stages"]["broad"], score["stages"]["targeted"]
    assert f"| This set, after the broad pass | {score['recall_after']['broad'][0]} of {gold} | " \
           f"{broad['precision'][0]} of {broad['precision'][1]} |" in page
    assert f"| This set, after the targeted pass | {score['recall_after']['targeted'][0]} of {gold} | " \
           f"{targeted['precision'][0]} of {targeted['precision'][1]} (targeted rows) |" in page
    assert "**A figure here is a measurement of one run.**" in page
    assert "29 of 101" in page and "30 of 100" in page
    assert "reference_fixture/README.md#the-scoring-rule" in page
    readme = (FIXTURE / "README.md").read_text(encoding="utf-8")
    assert readme.count("## The scoring rule") == 1
    assert f"USD {_record()['budget']['spent_usd']:.2f}" in readme
