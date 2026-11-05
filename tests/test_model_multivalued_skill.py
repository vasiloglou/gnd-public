"""TS4: the gnd-model-multivalued skill, its fixture and its recorded run (spec phase-TS4-spec.md section 8)."""

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
from test_judge_fact_types_skill import fenced_gnd_lines, homes, packaged_texts

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src/gnd/skills"
SKILL = SKILLS / "gnd-model-multivalued/SKILL.md"
FIXTURE = ROOT / "tests/fixtures/type-judgements/multi-valued"
RECORDING = ROOT / ".gnd-planning/milestones/type-induction-skills/evidence/TS4/recording"
KEY = json.loads((FIXTURE / "answer-key.json").read_text(encoding="utf-8"))["groups"]
CANARIES = ("tag-m5q1", "alias-m5q2", "role-m5q3", "code-m5q4")
COMMON = ["--families", "fact-type", "--actor", "test", "--requested-at", "2026-11-05T00:00:00+00:00"]

sys.path.insert(0, str(ROOT / "tools"))
import record_judge_sessions as recorder


def text() -> str:
    return re.sub(r"\s+", " ", SKILL.read_text(encoding="utf-8").replace("*", ""))


# --- T8-T11: the prose (TS4-C2, C3, C4) ---------------------------------------

HANDOFF = ["--type-evidence-in EVIDENCE --shape-judgements JUDGEMENTS", "gnd evolve preview MODEL proposal.json",
           "--policy additive", "never applies a proposal", "never runs `gnd evolve apply`"]


@pytest.mark.parametrize("sentence", HANDOFF)
def test_t8_the_handoff_names_discover_and_preview_and_never_apply(sentence):
    assert sentence in text()


def test_t8_no_fenced_command_applies():
    lines = fenced_gnd_lines(SKILL.read_text(encoding="utf-8"))
    assert [line.split()[1] for line in lines] == ["discover", "evolve"]
    assert not [line for line in lines if " apply" in line]


def test_t8_every_sentence_naming_apply_denies_it():
    sentences = re.split(r"(?<=[.!?])\s+", text())
    named = [s for s in sentences if "evolve apply" in s]
    assert named and all("never" in s for s in named), named
    seeded = re.split(r"(?<=[.!?])\s+", text() + " Then run `gnd evolve apply MODEL proposal.json` yourself.")
    assert not all("never" in s for s in seeded if "evolve apply" in s)


RULES = ["S1 — already induced.", "S2 — already held.", "S3 — junction table.", "S4 — ask.",
         "Write nothing until every multi-valued group has a verdict.",
         "A candidate with a `null` pair overlap does not stop S3"]


@pytest.mark.parametrize("sentence", RULES)
def test_t9_each_decision_rule_has_one_home(sentence):
    assert homes(sentence, packaged_texts()) == ["gnd-model-multivalued/SKILL.md"]


CLAUSES = {
    "S1-generic": "whose `origin.generic` is the group's `generic` and whose `origin.same_attribute` is true",
    "S1-verdict": "the verdict is `skip`, naming that fact type",
    "S2": "at least 90% of the distinct pairs already holds this attribute's facts",
    "S3-truncated": "when the evidence's `truncated` is 0",
    "S3-share": "at least one entity in ten has several values",
    "S3-verdict": "the verdict is `many-to-many`",
    "S4-errors": "When the user says the extra values are errors, the verdict is `skip`",
    "eligible": "exactly those with status `multi_valued`",
    "numbers": "When `show_values` is false, put no number standing on its own",
    "skill-refusal": "If a refusal names `judge.skill`, stop and tell the user",
}


@pytest.mark.parametrize("name", sorted(CLAUSES))
def test_t9_each_rule_states_its_key_clause(name):
    assert CLAUSES[name] in text()


DISCLOSURE = ["Never open, list, search or ask for the population",
              "never write them into the judgements file",
              "the evidence's `format` is not `gnd-type-evidence/1`",
              "its `model_sha256` is not the SHA-256 of the model file",
              "its `truncated_groups` is above 0",
              "never of a re-serialized copy"]


@pytest.mark.parametrize("sentence", DISCLOSURE)
def test_t10_the_population_rule_and_the_refusals_are_stated(sentence):
    assert sentence in text()


CONVENTION = ["`rai-orm-from-schema` dialect", "`gnd import rai-orm` is unchanged", "It imports nothing",
              "uniqueness spanning both roles", "It states nothing functional",
              "(../gnd-orm-core/references/constraint-reference.md#internal-uniqueness-uc)"]


@pytest.mark.parametrize("sentence", CONVENTION)
def test_t11_the_convention_is_stated_and_the_uniqueness_linked(sentence):
    assert sentence in text()


def test_t11_the_spanning_uniqueness_is_linked_not_copied():
    reference = (SKILLS / "gnd-orm-core/references/constraint-reference.md").read_text(encoding="utf-8")
    assert "## Internal uniqueness (UC)" in reference
    assert "Combination unique; neither alone unique" in reference
    assert "Combination unique" not in SKILL.read_text(encoding="utf-8")


# --- T13: the fixture agrees with its answer key -------------------------------

@pytest.fixture(scope="module")
def evidence(tmp_path_factory):
    return recorder.build_evidence(tmp_path_factory.mktemp("evidence"), FIXTURE)


def test_t13_the_fixture_gives_the_four_cases_the_key_names(evidence):
    document = json.loads(evidence.read_text(encoding="utf-8"))
    assert document["show_values"] is False and document["truncated_groups"] == document["truncated"] == 0
    groups = {g["group"]: g for g in document["groups"]}
    assert sorted(groups) == sorted(KEY) and {g["status"] for g in groups.values()} == {"multi_valued"}

    def candidate(group, fact_type):
        return next(c for c in groups[group]["candidates"] if c["fact_type"] == fact_type)

    def distinct(group):
        return groups[group]["rows"] - groups[group]["exact_repeats"]

    induced, label = "item_has_attribute_induced_0", "item_has_label"
    assert candidate("g0", induced)["origin"]["same_attribute"] is True                   # S1
    assert not candidate("g1", induced)["origin"]["same_attribute"]                       # S2
    assert candidate("g1", label)["overlap"]["pairs"] >= 0.9 * distinct("g1")
    for group in ("g2", "g3"):                                                            # S3, S4: no shared pair
        assert all(c["overlap"]["pairs"] == 0 for c in groups[group]["candidates"])
    assert groups["g2"]["multi"]["entities"] * 10 >= groups["g2"]["support"]              # S3
    assert groups["g2"]["exact_repeats"] > 0
    assert groups["g3"]["multi"]["entities"] * 10 < groups["g3"]["support"]               # S4
    assert not any(c["signature_equal"] for g in groups.values() for c in g["candidates"])


def test_t13_no_canary_is_in_the_model_or_the_evidence(evidence):
    for body in ((FIXTURE / "model.orm.yaml").read_text(encoding="utf-8"), evidence.read_text(encoding="utf-8")):
        assert not [c for c in CANARIES if c in body]


def test_t13_the_recorder_entry_matches_this_fixture():
    entry = recorder.SKILLS["model-multivalued"]
    assert entry["fixture"] == FIXTURE and entry["canaries"] == CANARIES
    assert entry["option"] == "--shape-judgements"


# --- T14, T15: the committed recording (TS4-C5) --------------------------------

def results():
    return json.loads((RECORDING / "results.json").read_text(encoding="utf-8"))


def test_t14_every_recorded_check_holds():
    row = results()["run"]
    assert results()["skill"] == "gnd-model-multivalued" and results()["fixture"] == "multi-valued"
    assert recorder.passed(row["checks"]), row["checks"]
    assert set(row["checks"]) == {"written", "schema_valid", "discover_exit", "verdicts_match_key", "preview_exit",
                                  "asked_before_writing", "only_judgements_new", "no_apply_call",
                                  "no_population_access", "no_canary"}


def test_t14_the_manifest_binds_the_kept_files_and_the_current_sources():
    manifest = json.loads((RECORDING / "manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((RECORDING / name).read_bytes()).hexdigest() == digest, name
    assert set(manifest["sources"]) == {"tools/record_judge_sessions.py", "src/gnd/skills/gnd-model-multivalued/SKILL.md",
                                        *(f"tests/fixtures/type-judgements/multi-valued/{name}" for name in
                                          ("model.orm.yaml", "items.population.json", "answer-key.json"))}
    for name, digest in manifest["sources"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f"{name} changed since the recording"


def recorded_judgements() -> Path:
    return RECORDING / "run-1" / results()["run"]["judgements"]


def test_t14_the_recorded_file_binds_this_evidence_and_the_cli_renders_many_to_many(evidence, tmp_path):
    judgements = recorded_judgements()
    document = json.loads(judgements.read_text(encoding="utf-8"))
    jsonschema.validate(document, json.loads((ROOT / "src/gnd/type-judgements.schema.json").read_text()))
    assert document["evidence_sha256"] == hashlib.sha256(evidence.read_bytes()).hexdigest()
    assert document["kind"] == "shapes" and document["judge"]["skill"] == "gnd-model-multivalued"
    for name in ("model.orm.yaml", "items.population.json"):
        shutil.copyfile(FIXTURE / name, tmp_path / name)
    shutil.copyfile(evidence, tmp_path / "evidence.json")
    shutil.copyfile(judgements, tmp_path / "judgements.json")
    run = subprocess.run([sys.executable, "-m", "gnd", "discover", "model.orm.yaml", "items.population.json",
                          *COMMON, "--type-evidence-in", "evidence.json", "--shape-judgements", "judgements.json",
                          "--out", "proposal.json", "--report", "report.json"], cwd=tmp_path, capture_output=True,
                         text=True, check=False, env=recorder._environment())
    assert run.returncode == 0, run.stdout + run.stderr
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))["fact_type_proposals"]
    assert [p["shape"] for p in report["proposed"]] == ["many-to-many"]
    assert report["skipped"]["judged_skip"] == 3
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
    flipped["verdicts"][3] = {**flipped["verdicts"][3], "verdict": "many-to-many"}
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
    assert all(workspace["after"][name] == digest for name, digest in workspace["before"].items())


# --- T17: anonymity and paths --------------------------------------------------

def public_texts():
    paths = [SKILL, *sorted(FIXTURE.iterdir()), *sorted(p for p in RECORDING.parent.rglob("*") if p.is_file())]
    return [(p, p.read_text(encoding="utf-8", errors="replace")) for p in paths]


@pytest.mark.parametrize("pattern", ABSOLUTE)
def test_t17_no_absolute_path_in_the_skill_fixture_or_phase_evidence(pattern):
    assert [str(p.relative_to(ROOT)) for p, body in public_texts() if re.search(pattern, body)] == []


def test_t17_no_downstream_name():
    leaked = [str(p.relative_to(ROOT)) for p, body in public_texts()
              for token in set(re.findall(r"[a-z][a-z0-9_-]+", body.lower()))
              if hashlib.sha256(token.encode()).hexdigest() in DOWNSTREAM]
    assert leaked == []


# --- the recorder's gate per entry (TS4 D1, D5) -----------------------------------

@pytest.mark.parametrize(("skill", "spec", "accepted"), [
    ("model-multivalued", "phase-TS4-spec.md", True), ("model-multivalued", "phase-TS3-spec.md", False),
    ("judge-fact-types", "phase-TS3-spec.md", True), ("judge-fact-types", "phase-TS4-spec.md", True)])
def test_the_recorder_accepts_only_the_specs_that_authorize_an_entry(skill, spec, accepted):
    body = (ROOT / ".gnd-planning/milestones/type-induction-skills/notes" / spec).read_text(encoding="utf-8")
    assert any(h in body and m in body for h, m in recorder.SKILLS[skill]["gates"]) is accepted
