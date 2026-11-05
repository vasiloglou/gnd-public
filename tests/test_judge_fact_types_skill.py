"""TS3: the gnd-judge-fact-types skill, its fixture and its recorded run (spec phase-TS3-spec.md section 8)."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
from test_ik6_walk import ABSOLUTE, DOWNSTREAM

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src/gnd/skills"
SKILL = SKILLS / "gnd-judge-fact-types/SKILL.md"
FIXTURE = ROOT / "tests/fixtures/type-judgements/round-two"
RECORDING = ROOT / ".gnd-planning/milestones/type-induction-skills/evidence/TS3/recording"
KEY = json.loads((FIXTURE / "answer-key.json").read_text(encoding="utf-8"))["groups"]
CANARIES = ("dim-k4p1", "hue-k4p2", "mass-k4p3", "tint-k4p4")
COMMON = ["--families", "fact-type", "--actor", "test", "--requested-at", "2026-11-05T00:00:00+00:00"]

sys.path.insert(0, str(ROOT / "tools"))
import record_judge_sessions as recorder


def text() -> str:
    return re.sub(r"\s+", " ", SKILL.read_text(encoding="utf-8").replace("*", ""))


def packaged_texts():
    for path in sorted(SKILLS.rglob("*.md")):
        yield path, re.sub(r"\s+", " ", path.read_text(encoding="utf-8").replace("*", ""))


# --- T8-T10: the prose (TS3-C2, C3) ----------------------------------------

HANDOFF = ["--type-evidence-in EVIDENCE --duplicate-judgements JUDGEMENTS", "gnd evolve preview MODEL proposal.json",
           "--policy additive", "never applies a proposal", "never runs `gnd evolve apply`"]


@pytest.mark.parametrize("sentence", HANDOFF)
def test_t8_the_handoff_names_discover_and_preview_and_never_apply(sentence):
    assert sentence in text()


def fenced_gnd_lines(source: str) -> list[str]:
    lines, inside = [], False
    for line in source.splitlines():
        if line.strip().startswith("```"):
            inside = not inside
        elif inside and line.strip().startswith("gnd "):
            lines.append(line.strip())
    return lines


def test_t8_no_fenced_command_applies_and_a_seeded_one_is_found():
    lines = fenced_gnd_lines(SKILL.read_text(encoding="utf-8"))
    assert [line.split()[1] for line in lines] == ["discover", "evolve"]
    assert not [line for line in lines if " apply" in line]
    seeded = SKILL.read_text(encoding="utf-8") + "\n```sh\ngnd evolve apply MODEL proposal.json\n```\n"
    assert [line for line in fenced_gnd_lines(seeded) if " apply" in line]


RULES = ["R1 — same origin.", "R2 — shared facts.", "R3 — no shared facts.", "R4 — ask.",
         "No file is written until every eligible group has a verdict.",
         "An equal role-player signature (`signature_equal`) is evidence neither way."]


def homes(sentence, texts):
    return [path.relative_to(SKILLS).as_posix() for path, body in texts if sentence in body]


@pytest.mark.parametrize("sentence", RULES)
def test_t9_each_decision_rule_has_one_home(sentence):
    assert homes(sentence, packaged_texts()) == ["gnd-judge-fact-types/SKILL.md"]


def test_t9_a_seeded_second_copy_fails_by_name():
    texts = list(packaged_texts())
    texts.append((SKILLS / "gnd-orm-core/SKILL.md", RULES[0]))
    assert homes(RULES[0], texts) == ["gnd-judge-fact-types/SKILL.md", "gnd-orm-core/SKILL.md"]


DISCLOSURE = ["Never open, list, search or ask for the population",
              "never write them into the judgements file",
              "the evidence's `format` is not `gnd-type-evidence/1`",
              "its `model_sha256` is not the SHA-256 of the model file",
              "its `truncated_groups` is above 0",
              "never of a re-serialized copy"]


@pytest.mark.parametrize("sentence", DISCLOSURE)
def test_t10_the_population_rule_and_the_refusals_are_stated(sentence):
    assert sentence in text()


# --- T13: the fixture agrees with its answer key ----------------------------

@pytest.fixture(scope="module")
def evidence(tmp_path_factory):
    return recorder.build_evidence(tmp_path_factory.mktemp("evidence"))


def test_t13_the_fixture_gives_the_four_cases_the_key_names(evidence):
    document = json.loads(evidence.read_text(encoding="utf-8"))
    assert document["show_values"] is False and document["truncated_groups"] == 0
    groups = {g["group"]: g for g in document["groups"]}
    assert sorted(groups) == sorted(KEY) and {g["status"] for g in groups.values()} == {"shape_match"}

    def candidate(group, fact_type):
        return next(c for c in groups[group]["candidates"] if c["fact_type"] == fact_type)

    induced, colour = "item_has_attribute_induced_0", "item_has_colour"
    assert candidate("g0", induced)["origin"]["same_attribute"] is True                 # R1
    assert not candidate("g1", induced)["origin"]["same_attribute"]                     # R2
    assert candidate("g1", colour)["overlap"]["pairs"] == groups["g1"]["rows"]
    assert all(c["overlap"]["pairs"] == 0 for c in groups["g2"]["candidates"])          # R3
    assert 0 < candidate("g3", colour)["overlap"]["pairs"] < 0.9 * groups["g3"]["rows"]  # R4
    assert not any(c["origin"] and c["origin"]["same_attribute"] for g in ("g1", "g2", "g3")
                   for c in groups[g]["candidates"])


def test_t13_no_canary_is_in_the_model_or_the_evidence(evidence):
    for body in ((FIXTURE / "model.orm.yaml").read_text(encoding="utf-8"), evidence.read_text(encoding="utf-8")):
        assert not [c for c in CANARIES if c in body]


# --- T14, T15: the committed recording (TS3-C4) -----------------------------

def results():
    return json.loads((RECORDING / "results.json").read_text(encoding="utf-8"))


def test_t14_every_recorded_check_holds():
    row = results()["run"]
    assert recorder.passed(row["checks"]), row["checks"]
    assert set(row["checks"]) == {"written", "schema_valid", "discover_exit", "verdicts_match_key", "preview_exit",
                                  "asked_before_writing", "only_judgements_new", "no_apply_call",
                                  "no_population_access", "no_canary"}


def test_t14_the_manifest_binds_the_kept_files_and_their_sources():
    manifest = json.loads((RECORDING / "manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((RECORDING / name).read_bytes()).hexdigest() == digest, name
    assert set(manifest["sources"]) >= {"src/gnd/skills/gnd-judge-fact-types/SKILL.md",
                                         "tests/fixtures/type-judgements/round-two/answer-key.json"}


def recorded_judgements() -> Path:
    return RECORDING / "run-1" / results()["run"]["judgements"]


def test_t14_the_recorded_file_binds_this_evidence_and_the_cli_accepts_it(evidence, tmp_path):
    judgements = recorded_judgements()
    document = json.loads(judgements.read_text(encoding="utf-8"))
    jsonschema.validate(document, json.loads((ROOT / "src/gnd/type-judgements.schema.json").read_text()))
    assert document["evidence_sha256"] == hashlib.sha256(evidence.read_bytes()).hexdigest()
    assert document["kind"] == "duplicates" and document["judge"]["skill"] == "gnd-judge-fact-types"
    for name in ("model.orm.yaml", "items.population.json"):
        shutil.copyfile(FIXTURE / name, tmp_path / name)
    shutil.copyfile(evidence, tmp_path / "evidence.json")
    shutil.copyfile(judgements, tmp_path / "judgements.json")
    run = subprocess.run([sys.executable, "-m", "gnd", "discover", "model.orm.yaml", "items.population.json",
                          *COMMON, "--type-evidence-in", "evidence.json", "--duplicate-judgements", "judgements.json",
                          "--out", "proposal.json", "--report", "report.json"], cwd=tmp_path, capture_output=True,
                         text=True, check=False, env=recorder._environment())
    assert run.returncode == 0, run.stdout + run.stderr
    preview = subprocess.run([sys.executable, "-m", "gnd", "evolve", "preview", "model.orm.yaml", "proposal.json",
                              "--workspace", ".", "--records", "records", "--out", "preview.json", "--policy",
                              "additive"], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert preview.returncode == 0, preview.stdout + preview.stderr


def verdicts_match(document) -> bool:
    got = {v["group"]: (v["verdict"], v.get("of")) for v in document["verdicts"]}
    return got == {g: (k["verdict"], k.get("of")) for g, k in KEY.items()}


def test_t14_the_verdicts_equal_the_key_and_a_flipped_verdict_does_not():
    document = json.loads(recorded_judgements().read_text(encoding="utf-8"))
    assert verdicts_match(document)
    flipped = json.loads(json.dumps(document))
    flipped["verdicts"][2] = {**flipped["verdicts"][2], "verdict": "duplicate", "of": "item_has_colour"}
    assert not verdicts_match(flipped)


def kept_texts():
    return [(p, p.read_text(encoding="utf-8", errors="replace")) for p in sorted(RECORDING.rglob("*")) if p.is_file()]


def test_t15_no_canary_and_no_population_or_apply_call_in_the_recording():
    assert not [str(p.relative_to(RECORDING)) for p, body in kept_texts() if any(c in body for c in CANARIES)]
    calls = recorder.tool_calls(RECORDING / "run-1")
    assert calls, "the recording kept no tool call; the scan below would check nothing"
    assert not [c for c in calls if "evolve apply" in c or "population" in c]
    workspace = json.loads((RECORDING / "run-1/workspace.json").read_text(encoding="utf-8"))
    assert sorted(set(workspace["after"]) - set(workspace["before"])) == [results()["run"]["judgements"]]


def test_t15_a_seeded_canary_is_found(tmp_path):
    seeded = tmp_path / "turn-99.jsonl"
    seeded.write_text(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "input": {"command": f"echo {CANARIES[1]}"}}]}}) + "\n")
    assert any(CANARIES[1] in call for call in recorder.tool_calls(tmp_path))


# --- T17: anonymity and paths ------------------------------------------------

def public_texts():
    paths = [SKILL, *sorted(FIXTURE.iterdir()), *sorted(p for p in RECORDING.rglob("*") if p.is_file())]
    return [(p, p.read_text(encoding="utf-8", errors="replace")) for p in paths]


@pytest.mark.parametrize("pattern", ABSOLUTE)
def test_t17_no_absolute_path_in_the_skill_fixture_or_recording(pattern):
    assert [str(p.relative_to(ROOT)) for p, body in public_texts() if re.search(pattern, body)] == []


def test_t17_no_downstream_name():
    leaked = [str(p.relative_to(ROOT)) for p, body in public_texts()
              for token in set(re.findall(r"[a-z][a-z0-9_-]+", body.lower()))
              if hashlib.sha256(token.encode()).hexdigest() in DOWNSTREAM]
    assert leaked == []
