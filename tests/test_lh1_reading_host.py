"""LH1: a caller's producer drives the reading stages over a caller's root."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import time
from pathlib import Path

import pytest
from support.recorded_version import tree_as_recorded

from gnd.artifacts import ArtifactError, canonical_json_bytes, read_regular_bounded, sha256_hex
from gnd.examples.literature import reading
from gnd.examples.literature.reading import ReadingLimits

FIXTURES = Path(__file__).parent / "fixtures/lh1-reading"
CALLER = FIXTURES / "caller"
PACKAGED = FIXTURES / "packaged"
RECORDED_AT = "0.4.0"
P3 = {
    "full": "ee67e13c082c340052cd37b09c77f2feb90c124b633738b8863bcd3d22b8fd1c",
    "unavailable": "d4010f94712aa9bd46bf6f62f148a05f22e7f88acf9bc82d7c736d4cb9ba6ddf",
    "budget-0": "7dcf43ecab3a6c7d3a1d0b8dbe3b503a28e698fed170506469cad4820a37a071",
}
ANSWERS = {
    "a-opening": {"outcome": "accepted", "proposal_keys": [],
                  "facts": {"paper_title": [{"paper": "paper-a", "title": "Graph sampling at scale"}]}},
    "a-methods": {"outcome": "accepted", "proposal_keys": ["method"],
                  "facts": {"paper_method": [{"paper": "paper-a", "value": "stratified sampling over 40 graphs"}]}},
    "a-results": {"outcome": "accepted", "proposal_keys": [],
                  "facts": {"paper_finding": [{"paper": "paper-a", "value": "sampling cuts cost by half"}]}},
    "b-opening": {"outcome": "accepted", "proposal_keys": [],
                  "facts": {"paper_title": [{"paper": "paper-b", "title": "Sparse retrieval revisited"}]}},
    "b-methods": {"outcome": "empty", "facts": {}, "proposal_keys": []},
}
PACKAGED_NAMES = ("study-methods", "alanine", "approximation", "alternative_integrator", "subject_label",
                  "saved-public-fixture")


class Producer:
    """A host's producer: only ``produce``, and its own record of every call."""

    def __init__(self, answers=None):
        self.answers = answers if answers is not None else ANSWERS
        self.seen = []

    def produce(self, call):
        self.seen.append(call)
        return copy.deepcopy(self.answers[call.section])


class Forbidden:
    def produce(self, call):
        pytest.fail(f"producer called for {call.section}")


class Reviewer:
    def __init__(self, decision="supported"):
        self.decision = decision

    def review(self, call):
        if self.decision == "list":
            return ["supported"]
        return {"decision": self.decision, "basis": f"the excerpt states it ({call.section})"}


def _root(tmp_path, *, declared=False, profile=None, name="root"):
    root = tmp_path / name
    shutil.copytree(CALLER, root)
    if declared:
        shutil.copyfile(root / "profile-declared.json", root / "profile.json")
    if profile is not None:
        (root / "profile.json").write_bytes(canonical_json_bytes(profile))
    return root


def _profile(**changes):
    value = json.loads((CALLER / "profile.json").read_bytes())
    value.update(changes)
    return value


def _edit(root, name, change):
    value = json.loads((root / name).read_bytes())
    change(value)
    (root / name).write_bytes(canonical_json_bytes(value))


def _refuses(out, call, match=None):
    with pytest.raises((reading.ExampleError, ArtifactError), match=match):
        call()
    assert not out.exists()


def _files(folder):
    return {path.relative_to(folder).as_posix(): path.read_bytes()
            for path in sorted(folder.rglob("*")) if path.is_file()}


@pytest.fixture(scope="module")
def plain(tmp_path_factory):
    base = tmp_path_factory.mktemp("lh1")
    producer = Producer()
    out = base / "run"
    report = reading.run(out, fixture=CALLER, producer=producer)
    return out, report, producer


@pytest.fixture(scope="module")
def packaged_run(tmp_path_factory):
    base = tmp_path_factory.mktemp("lh1-packaged")
    reading.run(base / "full")
    return base / "full"


def test_t1_caller_run_drives_six_stages(plain, packaged_run):
    out, report, _ = plain
    manifest = json.loads((out / "run.json").read_bytes())
    assert manifest["format"] == "literature-reading-run/2"
    assert [row["stage"] for row in report["stages"]] == list(reading.STAGES)
    assert report["public_routes"]["broad"] == {"verify": 0, "check": 0}
    assert report["public_routes"]["targeted"] == {"verify": 0, "check": 0}
    for index in range(6):
        ours = json.loads((out / f"stage-{index}.json").read_bytes())
        theirs = json.loads((packaged_run / f"stage-{index}.json").read_bytes())
        assert set(ours) == set(theirs)
    attempts = json.loads((out / "payload-1.json").read_bytes())["attempts"]
    packaged_attempts = json.loads((packaged_run / "payload-1.json").read_bytes())["attempts"]
    assert {frozenset(row) for row in attempts} == {frozenset(row) for row in packaged_attempts}
    coverage = json.loads((out / "coverage.json").read_bytes())["rows"]
    packaged_coverage = json.loads((packaged_run / "coverage.json").read_bytes())["rows"]
    assert {frozenset(row) for row in coverage} == {frozenset(row) for row in packaged_coverage}
    for name, raw in _files(out).items():
        for word in PACKAGED_NAMES:
            assert word.encode() not in raw, (name, word)


def test_t2_calls_carry_the_section_bytes(plain):
    _, report, producer = plain
    roster = json.loads((CALLER / "roster.json").read_bytes())
    sections = {row["id"]: row for row in roster["sections"]}
    attempts = {row["section"]: row for row in report["inspections"]}
    for call in producer.seen:
        document = (CALLER / f"{call.source}.txt").read_bytes()
        start, end = sections[call.section]["span"]
        assert call.excerpt == document[start:end]
        assert call.excerpt_sha256 == sha256_hex(call.excerpt) == attempts[call.section]["excerpt_sha256"]
    seen = {stage: sum(call.stage == stage for call in producer.seen)
            for stage in ("broad-extraction", "targeted-extraction")}
    assert report["producer_calls"] == seen
    method = next(call for call in producer.seen if call.section == "a-methods")
    assert {question["id"] for question in method.questions} == {"a-method", "a-baseline"}


def test_t3_live_responses_and_receipts_are_retained(tmp_path):
    root = _root(tmp_path, profile=_profile(review=True))
    out = tmp_path / "run"
    reading.run(out, fixture=root, producer=Producer(), reviewer=Reviewer())
    manifest = json.loads((out / "run.json").read_bytes())
    table = json.loads((out / "producer-output-table.json").read_bytes())
    assert table == {name: ANSWERS[name] for name in table}
    assert set(table) == {"a-opening", "a-methods", "a-results", "b-opening", "b-methods"}
    receipts = json.loads((out / "reviews.json").read_bytes())
    assert set(receipts) == {"a-opening", "a-methods", "a-results", "b-opening"}
    assert all(row["decision"] == "supported" for row in receipts.values())
    for name in ("producer-output-table.json", "reviews.json"):
        assert manifest["artifacts"][name] == sha256_hex((out / name).read_bytes())
    assert manifest["settings"]["reviewer"] == "live"


def test_t4_undeclared_steps_are_skipped(plain):
    out, report, _ = plain
    assert report["steps"] == dict.fromkeys(("review", "calibration", "conflict", "absence"), "skipped")
    assert report["fidelity"] is None
    assert report["absence"] == {"status": "skipped", "below_floor_status": "skipped"}
    assert report["public_routes"]["reported-conflict"] == "skipped"
    payload = json.loads((out / "payload-5.json").read_bytes())
    assert payload["fidelity"] is None and payload["absence"] == {"high": "skipped", "low": "skipped"}
    assert json.loads((out / "payload-4.json").read_bytes())["semantic_reviews"] == []
    names = set(_files(out))
    assert not names & {"fidelity-high.json", "fidelity-low.json", "reported-conflict.population.json",
                        "reported-conflict.source.txt", "scope.json", "closure.json", "reviews.json"}


def test_t5_declared_steps_run_on_the_callers_files(tmp_path):
    root = _root(tmp_path, declared=True)
    report = reading.run(tmp_path / "run", fixture=root, producer=Producer(), reviewer=Reviewer())
    assert report["steps"] == dict.fromkeys(("review", "calibration", "conflict", "absence"), "ran")
    high, low = report["fidelity"]["high"], report["fidelity"]["low"]
    assert high[0] == high[1] and low[0] < low[1] == high[1]
    assert report["public_routes"]["reported-conflict"] == {"verify": 1, "check": 1}
    assert report["absence"] == {"status": "qualified", "below_floor_status": "unavailable"}
    population = json.loads((tmp_path / "run/broad.population.json").read_bytes())
    assert population["facts"]["paper_venue"] == [{"paper": "paper-a", "value": "Host workshop"}]


@pytest.mark.parametrize("missing", ["gold.json", "calibration.json", "calibration.txt", "conflict.json",
                                     "conflict.txt", "scope.json", "closure.json"])
def test_t6_a_declared_file_that_is_missing_refuses(tmp_path, missing):
    root = _root(tmp_path, declared=True)
    (root / missing).unlink()
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden(), reviewer=Reviewer()))


def test_t7_a_document_budget_ends_one_document(tmp_path):
    report = reading.run(tmp_path / "run", fixture=CALLER, producer=Producer(), document_budget=72)
    documents = {row["source"]: row for row in report["documents"]}
    assert "a-methods" in report["omitted"]
    assert {row["section"] for row in report["inspections"]} >= {"a-opening", "a-results"}
    assert documents["survey-a"]["stop"] == "budget-exhausted" and documents["survey-a"]["omitted"] == 1
    assert documents["survey-b"]["omitted"] == 0 and documents["survey-b"]["attempted"] == 2
    assert documents["survey-b"]["stop"] == "available-evidence-exhausted"
    assert report["stop"] == "budget-exhausted"
    assert sum(row["reading_bytes"] for row in documents.values()) == report["reading_bytes"]


def test_t7_a_source_with_nothing_required_is_complete(tmp_path):
    root = _root(tmp_path)

    def relax(roster):
        for question in roster["questions"]:
            if question["id"].startswith("b-"):
                question["required"] = False

    _edit(root, "roster.json", relax)
    report = reading.run(tmp_path / "run", fixture=root, producer=Producer(), document_budget=72)
    documents = {row["source"]: row for row in report["documents"]}
    assert documents["survey-b"]["stop"] == "required-coverage-completed"


def test_t7_resolved_required_questions_do_not_end_a_document(tmp_path):
    root = _root(tmp_path)

    def relax(roster):
        next(row for row in roster["questions"] if row["id"] == "a-method")["required"] = False

    _edit(root, "roster.json", relax)
    report = reading.run(tmp_path / "run", fixture=root, producer=Producer())
    documents = {row["source"]: row for row in report["documents"]}
    assert documents["survey-a"]["stop"] == "required-coverage-completed"
    assert {"a-methods", "a-results"} <= {row["section"] for row in report["inspections"]}


def test_t8_lowered_limits_are_honoured(tmp_path):
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Forbidden(), limits=ReadingLimits(roster=2)))
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Forbidden(), budget=5000,
                                      limits=ReadingLimits(max_budget=4096)))


def test_t8_a_raised_input_cap_admits_a_large_source(tmp_path):
    root = _root(tmp_path)
    path = root / "survey-a.txt"
    path.write_bytes(path.read_bytes() + b"x" * (200 * 1024))

    def repin(roster):
        roster["sources"][0]["sha256"] = sha256_hex(path.read_bytes())

    _edit(root, "roster.json", repin)
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))
    limits = ReadingLimits(input_bytes=1 << 20)
    reading.run(out, fixture=root, producer=Producer(), limits=limits)
    settings = json.loads((out / "run.json").read_bytes())["settings"]
    assert settings["limits"]["input_bytes"] == 1 << 20
    assert settings["limits"]["roster"] == reading.ROSTER_LIMIT


@pytest.mark.parametrize("field", sorted(reading.LIMIT_CEILINGS))
def test_t8_a_limit_above_its_ceiling_refuses(tmp_path, field):
    out = tmp_path / "run"
    limits = ReadingLimits(**{field: reading.LIMIT_CEILINGS[field] + 1})
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Forbidden(), limits=limits))


@pytest.mark.parametrize("value", [0, True, 1.5])
def test_t8_a_limit_must_be_a_positive_int(tmp_path, value):
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Forbidden(),
                                      limits=ReadingLimits(roster=value)))


def _deep(depth):
    value = []
    for _ in range(depth):
        value = [value]
    return value


MALFORMED = {
    "not-a-mapping": ["accepted"],
    "key-missing": {"outcome": "empty", "facts": {}},
    "outcome": {"outcome": "maybe", "facts": {}, "proposal_keys": []},
    "accepted-empty": {"outcome": "accepted", "facts": {}, "proposal_keys": []},
    "empty-with-facts": {"outcome": "empty", "facts": {"paper_title": []}, "proposal_keys": []},
    "facts-list": {"outcome": "accepted", "facts": [], "proposal_keys": []},
    "fact-not-list": {"outcome": "accepted", "facts": {"paper_title": {}}, "proposal_keys": []},
    "row-not-mapping": {"outcome": "accepted", "facts": {"paper_title": ["x"]}, "proposal_keys": []},
    "nested-row-value": {"outcome": "accepted", "facts": {"paper_title": [{"paper": {"id": "a"}}]},
                         "proposal_keys": []},
    "nan": {"outcome": "accepted", "facts": {"paper_title": [{"paper": float("nan")}]}, "proposal_keys": []},
    "object": {"outcome": "accepted", "facts": {"paper_title": [{"paper": object()}]}, "proposal_keys": []},
    "integer-key": {"outcome": "accepted", "facts": {1: [{"paper": "a"}]}, "proposal_keys": []},
    "deep": {"outcome": "empty", "facts": {}, "proposal_keys": _deep(100_000)},
    "oversized": {"outcome": "accepted", "proposal_keys": [],
                  "facts": {"paper_title": [{"paper": "a", "title": "x" * (128 * 1024)}]}},
    "proposal-not-string": {"outcome": "empty", "facts": {}, "proposal_keys": [1]},
    "proposal-outside-roster": {"outcome": "empty", "facts": {}, "proposal_keys": ["unknown"]},
    "fact-type-outside-covers": {"outcome": "accepted", "facts": {"paper_author": [{"paper": "a"}]},
                                 "proposal_keys": []},
}


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_t9_a_malformed_response_refuses(tmp_path, case):
    answers = {**ANSWERS, "a-opening": MALFORMED[case]}
    out = tmp_path / "run"
    with pytest.raises(reading.ExampleError):
        reading.run(out, fixture=CALLER, producer=Producer(answers))
    assert not out.exists()


def test_t10_a_raising_producer_refuses_naming_the_section(tmp_path):
    class Raising(Producer):
        def produce(self, call):
            if len(self.seen) == 1:
                raise RuntimeError("provider down")
            return super().produce(call)

    out = tmp_path / "run"
    with pytest.raises(reading.ExampleError, match="producer failed at broad-extraction b-opening") as caught:
        reading.run(out, fixture=CALLER, producer=Raising())
    assert isinstance(caught.value.__cause__, RuntimeError)
    assert not out.exists()


@pytest.mark.parametrize(("name", "args"), [
    ("full", {}), ("unavailable", {"scenario": "unavailable"}), ("budget-0", {"budget": 0}),
])
def test_t11_packaged_runs_keep_their_bytes(tmp_path, name, args):
    out = tmp_path / name
    reading.run(out, **args)
    recorded = _files(PACKAGED / name)
    assert tree_as_recorded(_files(out), RECORDED_AT) == recorded
    assert sha256_hex(recorded["run.json"]) == P3[name]


def _wide_root(tmp_path, count, *, chain=False, span=1, response_sections=None):
    """A caller root with ``count`` sources, sections and questions, one section each."""
    root = tmp_path / f"wide-{count}"
    root.mkdir()
    for name in ("survey.orm.json", "terms.orm.json"):
        shutil.copyfile(CALLER / name, root / name)
    (root / "profile.json").write_bytes(canonical_json_bytes(_profile()))
    sources, sections, questions = [], [], []
    for index in range(count):
        document = b"x" * span
        (root / f"s{index}.txt").write_bytes(document)
        sources.append({"id": f"s{index}", "version": "1", "path": f"s{index}.txt", "sha256": sha256_hex(document)})
        eligible = response_sections is None or index < response_sections
        sections.append({"id": f"c{index}", "source": f"s{index}", "kind": "section",
                         "selection": "opening" if eligible else None, "keys": [],
                         "span": [0, span] if eligible else None, "reason": None if eligible else "unavailable"})
        questions.append({"id": f"q{index}", "section": f"c{index}", "fact": "paper_finding", "required": True,
                          "superseded_by": f"q{index + 1}" if chain and index + 1 < count else None,
                          "denial": False})
    roster = {"format": "literature-reading-roster/1", "sources": sources, "sections": sections,
              "questions": questions, "revisit_keys": ["k" * 1000]}
    (root / "roster.json").write_bytes(canonical_json_bytes(roster))
    return root


def test_t12_inputs_at_each_roster_ceiling_load_in_time(tmp_path):
    root = _wide_root(tmp_path, 4096, chain=True)
    limits = ReadingLimits(roster=4096, input_bytes=8 << 20)
    started = time.monotonic()
    inputs = reading.ReadingInputs(root, limits=limits, live=True)
    assert time.monotonic() - started < 10
    assert len(inputs.sources) == len(inputs.sections) == len(inputs.questions) == 4096
    assert reading._terminal(inputs.questions)["q0"] == "q4095"


def test_t12_a_run_at_the_roster_ceiling_finishes_in_time(tmp_path):
    root = _wide_root(tmp_path, 4096, chain=True)
    limits = ReadingLimits(roster=4096, input_bytes=8 << 20, response_bytes=1024)

    class Empty:
        def produce(self, call):
            return {"outcome": "empty", "facts": {}, "proposal_keys": []}

    started = time.monotonic()
    report = reading.run(tmp_path / "run", fixture=root, producer=Empty(), limits=limits)
    assert time.monotonic() - started < 90
    assert report["producer_calls"]["broad-extraction"] == 4096


def test_t12_input_response_and_budget_ceilings_run_in_time(tmp_path):
    root = _root(tmp_path)
    path = root / "survey-a.txt"
    path.write_bytes(path.read_bytes() + b"x" * ((8 << 20) - len(path.read_bytes())))

    def repin(roster):
        roster["sources"][0]["sha256"] = sha256_hex(path.read_bytes())

    _edit(root, "roster.json", repin)
    title = "y" * ((1 << 20) - 200)
    answers = {**ANSWERS, "a-opening": {"outcome": "accepted", "proposal_keys": [],
                                        "facts": {"paper_title": [{"paper": "paper-a", "title": title}]}}}
    assert len(canonical_json_bytes(answers["a-opening"])) <= 1 << 20
    limits = ReadingLimits(input_bytes=8 << 20, response_bytes=1 << 20, max_budget=1 << 26)
    started = time.monotonic()
    report = reading.run(tmp_path / "run", fixture=root, producer=Producer(answers), limits=limits,
                         budget=1 << 26)
    assert time.monotonic() - started < 60
    assert report["public_routes"]["broad"]["verify"] in reading.CALLER_EXITS


def test_t12_a_route_held_past_its_timeout_refuses_in_time(tmp_path, monkeypatch):
    from gnd.examples.literature import depth

    real = depth.run_bounded_process

    def sleeping(argv, **kwargs):
        return real((sys.executable, "-c", "import time; time.sleep(30)"), **kwargs)

    monkeypatch.setattr(depth, "run_bounded_process", sleeping)
    out = tmp_path / "run"
    started = time.monotonic()
    with pytest.raises(reading.ExampleError, match="extract failed to finish"):
        reading.run(out, fixture=CALLER, producer=Forbidden(), limits=ReadingLimits(route_seconds=1))
    assert time.monotonic() - started < 1 + 2
    assert not out.exists()


def test_t12_route_output_at_its_ceiling_is_read_in_time(tmp_path):
    from gnd.examples.literature import depth

    limits = reading._route_limits(ReadingLimits(route_output_bytes=16 << 20))
    script = "import sys; sys.stdout.write('x' * (16 << 20))"
    started = time.monotonic()
    import asyncio

    from gnd.process import run_bounded_process
    result = asyncio.run(run_bounded_process((sys.executable, "-c", script), cwd=tmp_path, env={}, limits=limits))
    assert time.monotonic() - started < 60
    assert result.status == "succeeded" and not result.stdout_truncated and len(result.stdout) == 16 << 20
    smaller = reading._route_limits(ReadingLimits(route_output_bytes=1 << 20))
    result = asyncio.run(run_bounded_process((sys.executable, "-c", script), cwd=tmp_path, env={}, limits=smaller))
    assert result.status not in {"succeeded", "failed"} or result.stdout_truncated
    assert depth.PROCESS_LIMITS.stdout_limit_bytes == 1 << 20


def test_t13_refusals_before_any_producer_call(tmp_path):
    root = _root(tmp_path)
    _edit(root, "survey.orm.json", lambda model: model["fact_types"][0]["roles"][0].update(object_type="absent"))
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()), "extract exited")
    _refuses(out, lambda: reading.run(out, producer=Forbidden()), "need profile.json")
    for argument in ({"reviewer": Reviewer()}, {"document_budget": 10}, {"unavailable": []},
                     {"limits": ReadingLimits()}):
        _refuses(out, lambda argument=argument: reading.run(out, **argument), "need profile.json")


def test_t15_an_empty_constrained_fact_type_completes_with_exit_2(tmp_path):
    answers = {**ANSWERS,
               "a-opening": {"outcome": "empty", "facts": {}, "proposal_keys": []},
               "b-opening": {"outcome": "empty", "facts": {}, "proposal_keys": []},
               "a-methods": {"outcome": "accepted", "proposal_keys": [], "facts": {
                   **ANSWERS["a-methods"]["facts"],
                   "paper_title": [{"paper": "paper-a", "title": "Graph sampling at scale"}]}}}
    report = reading.run(tmp_path / "run", fixture=CALLER, producer=Producer(answers))
    assert report["public_routes"]["broad"] == {"verify": 2, "check": 2}
    assert report["public_routes"]["targeted"] == {"verify": 0, "check": 0}


def test_t15_a_violated_constraint_completes_with_exit_1(tmp_path):
    answers = {**ANSWERS, "a-results": {"outcome": "accepted", "proposal_keys": [], "facts": {
        "paper_title": [{"paper": "paper-a", "title": "Sampling graphs at scale"}]}}}
    report = reading.run(tmp_path / "run", fixture=CALLER, producer=Producer(answers))
    assert report["public_routes"]["targeted"] == {"verify": 1, "check": 1}


def test_t15_an_unchecked_rule_completes_with_exit_4(tmp_path):
    root = _root(tmp_path)

    def textual(model):
        model["constraints"] = [{"id": "host_note", "type": "textual", "source": "explicit", "status": "confirmed",
                                 "modality": "alethic", "provenance": {"user_quote": "host_note"},
                                 "expression": "every finding is reproducible"}]

    _edit(root, "survey.orm.json", textual)
    report = reading.run(tmp_path / "run", fixture=root, producer=Producer())
    assert report["public_routes"]["targeted"]["check"] == 4
    assert reading.CALLER_EXITS == (0, 1, 2, 4)


def test_t15_any_other_route_exit_refuses(tmp_path, monkeypatch):
    original = reading._command

    def exit_five(out, *args, limits=None):
        result = original(out, *args, limits=limits)
        return result.model_copy(update={"return_code": 5}) if args[0] == "check" else result

    monkeypatch.setattr(reading, "_command", exit_five)
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Producer()), "check exited 5")


PROFILE_DEFECTS = {
    "not-an-object": ["profile"],
    "key-missing": {key: value for key, value in _profile().items() if key != "review"},
    "extra-key": {**_profile(), "stop": "never"},
    "format": _profile(format="literature-reading-profile/2"),
    "model-slash": _profile(model="sub/survey.orm.json"),
    "include-is-model": _profile(includes=["survey.orm.json"]),
    "seventeen-includes": _profile(includes=[f"t{index}.orm.json" for index in range(17)]),
    "absence-without-calibration": _profile(absence=True),
    "calibration-not-targeted": _profile(calibration={
        "section": "a-opening", "section_facts": ["paper_method"], "held_back_facts": ["paper_baseline"],
        "renderer_label": "r", "case_names": ["one", "two"]}),
    "calibration-overlap": _profile(calibration={
        "section": "a-methods", "section_facts": ["paper_method"], "held_back_facts": ["paper_method"],
        "renderer_label": "r", "case_names": ["one", "two"]}),
    "base-fact-outside-covers": _profile(base_facts={"paper_author": [{"paper": "a"}]}),
}


@pytest.mark.parametrize("case", sorted(PROFILE_DEFECTS))
def test_t16_a_defective_profile_refuses(tmp_path, case):
    root = _root(tmp_path)
    (root / "profile.json").write_bytes(json.dumps(PROFILE_DEFECTS[case]).encode())
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))


def test_t16_a_profile_over_the_input_cap_refuses(tmp_path):
    root = _root(tmp_path)
    (root / "profile.json").write_bytes(canonical_json_bytes(_profile()) + b" " * (128 * 1024))
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))


def _saved(root):
    raw = canonical_json_bytes(ANSWERS)
    (root / "responses.json").write_bytes(raw)
    (root / "producer-pin.json").write_bytes(canonical_json_bytes({"sha256": sha256_hex(raw)}))


def test_t17_the_saved_route_on_a_caller_root(tmp_path):
    root = _root(tmp_path)
    _saved(root)
    report = reading.run(tmp_path / "run", fixture=root)
    assert report["settings"]["producer"] == "saved"
    (root / "producer-pin.json").write_bytes(canonical_json_bytes({"sha256": "0" * 64}))
    out = tmp_path / "again"
    _refuses(out, lambda: reading.run(out, fixture=root), "saved producer table differs from its pin")


def test_t18_review_is_a_check_not_a_filter(tmp_path):
    root = _root(tmp_path, profile=_profile(review=True))
    reading.run(tmp_path / "ok", fixture=root, producer=Producer(), reviewer=Reviewer())
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Producer(), reviewer=Reviewer("unsupported")),
             "stale semantic reading review")
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Producer(), reviewer=Reviewer("list")))
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))
    plain_root = _root(tmp_path, name="plain-root")
    _refuses(out, lambda: reading.run(out, fixture=plain_root, producer=Forbidden(), reviewer=Reviewer()))


def test_t19_unavailable_sections_on_a_caller_root(tmp_path):
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Forbidden(), scenario="unavailable"))
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Forbidden(), unavailable=["absent"]))
    producer = Producer()
    report = reading.run(out, fixture=CALLER, producer=producer, unavailable=["a-methods"])
    assert "a-methods" not in {call.section for call in producer.seen}
    states = {row["question"]: row["state"] for row in report["coverage"]}
    assert states["a-method"] == "unavailable"
    assert report["settings"]["unavailable"] == ["a-methods"]


def test_t20_a_bound_over_a_given_retained_cap_refuses(tmp_path):
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Forbidden(),
                                      limits=ReadingLimits(retained_bytes=200 * 1024)), "retained-file cap")


def test_t20_a_derived_cap_over_the_ceiling_refuses(tmp_path):
    root = _wide_root(tmp_path, 4096)
    limits = ReadingLimits(roster=4096, input_bytes=8 << 20, response_bytes=1 << 20)
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden(), limits=limits),
             "retained-file ceiling")


def test_t20_a_run_at_the_response_ceiling_reads_back(tmp_path):
    root = _wide_root(tmp_path, 9)
    key = "k" * 1000
    padding = [key] * ((1 << 20) // 1003 - 2)

    class Padded:
        def produce(self, call):
            return {"outcome": "empty", "facts": {}, "proposal_keys": padding}

    assert len(canonical_json_bytes(Padded().produce(None))) <= 1 << 20
    limits = ReadingLimits(response_bytes=1 << 20)
    out = tmp_path / "run"
    started = time.monotonic()
    report = reading.run(out, fixture=root, producer=Padded(), limits=limits)
    assert time.monotonic() - started < 60
    cap = report["settings"]["limits"]["retained_bytes"]
    assert cap <= reading.LIMIT_CEILINGS["retained_bytes"]
    sizes = {name: len(raw) for name, raw in _files(out).items()}
    assert max(sizes.values()) > 8 << 20
    for name in sizes:
        read_regular_bounded(out, name, max_bytes=cap)


def test_t20_default_limits_derive_a_cap_above_today(plain):
    out, report, _ = plain
    assert report["settings"]["limits"]["retained_bytes"] > reading.RETAINED_FLOOR
    assert json.loads((out / "run.json").read_bytes())["settings"] == report["settings"]


class Empty:
    def produce(self, call):
        return {"outcome": "empty", "facts": {}, "proposal_keys": []}


def _reads_back(out, report):
    cap = report["settings"]["limits"]["retained_bytes"]
    for name, raw in _files(out).items():
        assert len(raw) <= cap, (name, len(raw), cap)


def test_r1_long_roster_strings_stay_under_the_recorded_cap(tmp_path):
    root = _root(tmp_path)
    _edit(root, "roster.json", lambda roster: roster["sources"][0].update(version="v" * 200_000))
    limits = ReadingLimits(roster=7, input_bytes=1 << 20, response_bytes=1024)
    out = tmp_path / "run"
    report = reading.run(out, fixture=root, producer=Empty(), limits=limits)
    _reads_back(out, report)


def test_r1_a_padded_saved_table_stays_under_the_recorded_cap(tmp_path):
    root = _root(tmp_path)
    raw = canonical_json_bytes(ANSWERS) + b" " * (2 << 20)
    (root / "responses.json").write_bytes(raw)
    (root / "producer-pin.json").write_bytes(canonical_json_bytes({"sha256": sha256_hex(raw)}))
    out = tmp_path / "run"
    report = reading.run(out, fixture=root, limits=ReadingLimits(input_bytes=4 << 20))
    _reads_back(out, report)


@pytest.mark.parametrize("kind", ["surrogate", "huge-int"])
def test_r2_an_unserializable_answer_refuses(tmp_path, kind):
    value = chr(0xD800) if kind == "surrogate" else 10**5000
    answers = {**ANSWERS, "a-opening": {"outcome": "accepted", "proposal_keys": [],
                                        "facts": {"paper_title": [{"paper": "paper-a", "title": value}]}}}
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=CALLER, producer=Producer(answers)))


def test_r2_an_unserializable_receipt_refuses(tmp_path):
    class Surrogate:
        def review(self, call):
            return {"decision": "supported", "basis": chr(0xD800)}

    root = _root(tmp_path, profile=_profile(review=True))
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Producer(), reviewer=Surrogate()))


def test_r3_a_malformed_saved_review_refuses_before_any_call(tmp_path):
    root = _root(tmp_path, profile=_profile(review=True))
    (root / "reviews.json").write_bytes(canonical_json_bytes({"a-opening": []}))
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))


def test_r4_a_superseded_required_question_stays_with_its_own_source(tmp_path):
    root = _root(tmp_path)

    def cross(roster):
        for question in roster["questions"]:
            question["required"] = question["id"] == "a-title"
            if question["id"] == "a-title":
                question["superseded_by"] = "b-title"

    _edit(root, "roster.json", cross)
    report = reading.run(tmp_path / "run", fixture=root, producer=Empty())
    documents = {row["source"]: row["stop"] for row in report["documents"]}
    assert documents == {"survey-a": "available-evidence-exhausted", "survey-b": "required-coverage-completed"}


def _saved_review(root, **changes):
    roster = json.loads((root / "roster.json").read_bytes())
    span = next(row["span"] for row in roster["sections"] if row["id"] == "a-opening")
    excerpt = (root / "survey-a.txt").read_bytes()[span[0]:span[1]]
    facts = ANSWERS["a-opening"]["facts"]
    receipt = {"basis": "the opening names the title", "decision": "supported",
               "excerpt_sha256": sha256_hex(excerpt), "facts_sha256": sha256_hex(canonical_json_bytes(facts))}
    receipt.update(changes)
    (root / "reviews.json").write_bytes(canonical_json_bytes({"a-opening": receipt}))


ONLY_TITLE = {**{name: {"outcome": "empty", "facts": {}, "proposal_keys": []} for name in ANSWERS},
              "a-opening": ANSWERS["a-opening"]}


def test_r5_a_long_saved_receipt_refuses_before_any_call(tmp_path):
    root = _root(tmp_path, profile=_profile(review=True))
    _saved_review(root, basis="b" * 200_000)
    out = tmp_path / "run"
    limits = ReadingLimits(roster=7, input_bytes=1 << 20, response_bytes=1024)
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden(), limits=limits))


@pytest.mark.parametrize("change", [{"basis": ""}, {"excerpt_sha256": "not-a-digest"},
                                    {"decision": "unsupported"}, {"facts_sha256": "x"}])
def test_r6_a_saved_receipt_knowably_wrong_refuses_before_any_call(tmp_path, change):
    root = _root(tmp_path, profile=_profile(review=True))
    _saved_review(root, **change)
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))


def test_r6_a_correct_saved_receipt_runs(tmp_path):
    root = _root(tmp_path, profile=_profile(review=True))
    _saved_review(root)
    report = reading.run(tmp_path / "run", fixture=root, producer=Producer(ONLY_TITLE))
    assert report["settings"]["reviewer"] == "saved"


@pytest.mark.parametrize("case", ["invalid-byte", "split-character"])
def test_r7_a_source_that_is_not_utf8_refuses(tmp_path, case):
    root = _root(tmp_path)
    path = root / "survey-a.txt"
    if case == "invalid-byte":
        path.write_bytes(b"\xff" + path.read_bytes()[1:])
    else:
        path.write_bytes("é".encode() + path.read_bytes()[2:])

    def repin(roster):
        roster["sources"][0]["sha256"] = sha256_hex(path.read_bytes())
        if case == "split-character":
            roster["sections"][0]["span"] = [0, 1]

    _edit(root, "roster.json", repin)
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))


@pytest.mark.parametrize(("kind", "key"), [("questions", "superseded_by"), ("sections", "selection"),
                                           ("sources", "version"), ("sections", "reason")])
def test_r8_a_roster_row_missing_a_key_refuses(tmp_path, kind, key):
    root = _root(tmp_path)
    _edit(root, "roster.json", lambda roster: roster[kind][-1].pop(key))
    out = tmp_path / "run"
    _refuses(out, lambda: reading.run(out, fixture=root, producer=Forbidden()))


def test_r9_the_retained_ceiling_is_the_json_read_cap():
    from gnd import input_policy

    assert reading.LIMIT_CEILINGS["retained_bytes"] == input_policy.MAX_BYTES
    with pytest.raises(ValueError):
        input_policy.loads(b"[" + b" " * input_policy.MAX_BYTES + b"]")


def test_r10_an_empty_fact_list_is_not_support(tmp_path):
    answers = {**ANSWERS, "a-opening": {"outcome": "accepted", "proposal_keys": [], "facts": {"paper_title": []}}}
    out = tmp_path / "run"
    with pytest.raises(reading.ExampleError, match="invalid saved producer response"):
        reading.run(out, fixture=CALLER, producer=Producer(answers))
    assert not out.exists()
