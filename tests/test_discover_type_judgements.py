"""TS2: ``gnd discover`` reads judgement files bound to one type-evidence file.

Spec: .gnd-planning/milestones/type-induction-skills/notes/phase-TS2-spec.md
(§8, T1-T30). Fixture: TS1's model and population, where ``size`` (g0) was
already induced into item_has_attribute_induced_0, the canary attribute (g1)
is functional and shape-matched, ``tag`` (g2) is multi-valued with one exact
repeat, and ``rare`` (g3) is below support.
"""

import copy
import hashlib
import json
import re
import subprocess
import sys
import time

import jsonschema
import pytest
from test_discover_type_evidence import CANARY, ROOT, build, discover

REPORT_SCHEMA = json.loads((ROOT / "src/gnd/discover.schema.json").read_text())
JUDGEMENTS_SCHEMA = json.loads((ROOT / "src/gnd/type-judgements.schema.json").read_text())
GENERIC = "item_has_attribute"
INDUCED = "item_has_attribute_induced_0"


def evidence_run(tmp_path, *extra, env=None, **kwargs):
    build(tmp_path, **kwargs)
    run, _out, _report, evidence = discover(tmp_path, *extra, env=env, name="first",
                                            evidence="first.evidence.json")
    assert run.returncode == 0, run.stderr
    return evidence


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def judgements(evidence_path, kind, verdicts, *, agent="test agent", digest=None):
    document = {"format": "gnd-type-judgements/1", "kind": kind,
                "evidence_sha256": digest or sha(evidence_path),
                "judge": {"skill": "gnd-judge-fact-types" if kind == "duplicates" else "gnd-model-multivalued",
                          "agent": agent},
                "verdicts": copy.deepcopy(verdicts)}
    jsonschema.validate(document, JUDGEMENTS_SCHEMA)  # T30: every fixture the tests write is schema-valid
    return document


def verdict(group, word, rationale="judged from readings and overlap", **extra):
    return {"group": group, "generic": GENERIC, "verdict": word, "rationale": rationale, **extra}


DUPLICATES = [verdict("g0", "duplicate", of=INDUCED), verdict("g1", "distinct")]
SHAPES = [verdict("g2", "many-to-many")]


def judged(tmp_path, *extra, duplicates=None, shapes=None, env=None, raw=None, name="judged"):
    """Write the judgements given and run the judged discover; ``raw`` overrides a file's bytes."""
    options = []
    for kind, document, option in (("duplicates", duplicates, "--duplicate-judgements"),
                                   ("shapes", shapes, "--shape-judgements")):
        if document is None and not (raw and kind in raw):
            continue
        path = tmp_path / f"{kind}.judgements.json"
        path.write_bytes(raw[kind] if raw and kind in raw else json.dumps(document).encode())
        options += [option, path.name]
    run, out, report, _ = discover(tmp_path, *extra, "--type-evidence-in", "first.evidence.json", *options,
                                   env=env, name=name, evidence=None)
    return run, out, report


def family(report):
    document = json.loads(report.read_text())
    jsonschema.validate(document, REPORT_SCHEMA)  # T30: every written report validates
    return document["fact_type_proposals"]


def operations(out):
    return json.loads(out.read_text())["operations"]


def fact_types(out):
    return {op["after"]["id"]: op["after"] for op in operations(out)
            if op["locator"]["locator_kind"] == "element" and op["locator"]["collection"] == "fact_types"}


def constraints(out):
    return {op["locator"]["host_id"]: op["after"] for op in operations(out)
            if op["locator"]["locator_kind"] == "constraint"}


def nothing_written(tmp_path, name="judged"):
    return not (tmp_path / f"{name}.proposal.json").exists() and not (tmp_path / f"{name}.report.json").exists()


@pytest.fixture
def shown(tmp_path):
    evidence = evidence_run(tmp_path, "--show-values")
    return tmp_path, evidence


# --- T1: usage ---------------------------------------------------------------


@pytest.mark.parametrize("extra", [
    ["--duplicate-judgements", "d.json"],
    ["--type-evidence-in", "first.evidence.json"],
    ["--type-evidence-in", "first.evidence.json", "--duplicate-judgements", "d.json", "--type-evidence", "x.json"],
])
def test_t1_usage(shown, extra):
    tmp_path, evidence = shown
    (tmp_path / "d.json").write_text(json.dumps(judgements(evidence, "duplicates", DUPLICATES)))
    run, *_ = discover(tmp_path, "--show-values", *extra, name="judged", evidence=None)
    assert run.returncode == 64, run.stderr
    assert nothing_written(tmp_path)


def test_t1_usage_without_the_family(shown):
    tmp_path, evidence = shown
    (tmp_path / "d.json").write_text(json.dumps(judgements(evidence, "duplicates", DUPLICATES)))
    run, *_ = discover(tmp_path, "--type-evidence-in", "first.evidence.json", "--duplicate-judgements", "d.json",
                       name="judged", evidence=None, families="uniqueness")
    assert run.returncode == 64 and "need --families fact-type" in run.stderr


def test_t1_repeated_path_and_service_guards(shown):
    tmp_path, evidence = shown
    (tmp_path / "d.json").write_text(json.dumps(judgements(evidence, "duplicates", DUPLICATES)))
    run, *_ = discover(tmp_path, "--type-evidence-in", "first.evidence.json", "--duplicate-judgements",
                       "first.evidence.json", name="judged", evidence=None)
    assert run.returncode == 64 and "different paths" in run.stderr
    from datetime import UTC, datetime

    from gnd.discover import service

    common = {"out": str(tmp_path / "o.json"), "report": str(tmp_path / "r.json"), "actor": "t",
              "requested_at": datetime(2026, 11, 5, tzinfo=UTC), "max_values": 20, "max_pairs": 256,
              "output_format": "json"}
    model, population = str(tmp_path / "model.orm.yaml"), str(tmp_path / "items.population.json")
    assert service._cmd_discover(model, population, families=("uniqueness",), type_evidence_in=str(evidence),
                                 duplicate_judgements=str(tmp_path / "d.json"), **common) == 64
    assert service._cmd_discover(model, population, families=("fact-type",),
                                 duplicate_judgements=str(tmp_path / "d.json"), **common) == 64


def test_t1_missing_judgements_file(shown):
    tmp_path, _evidence = shown
    run, *_ = discover(tmp_path, "--type-evidence-in", "first.evidence.json", "--duplicate-judgements",
                       "absent.json", name="judged", evidence=None)
    assert run.returncode == 66 and nothing_written(tmp_path)


# --- T2: hostile judgements (standing rule 1) ---------------------------------


def _hostile(evidence):
    good = judgements(evidence, "duplicates", DUPLICATES)
    deep = b"[" * 100_000 + b"]" * 100_000
    return {
        "not json": b"{not json",
        "nan": json.dumps(good).replace('"g0"', '"g0", "x": NaN').encode(),
        "duplicate key": json.dumps(good).replace('"kind": "duplicates"',
                                                  '"kind": "duplicates", "kind": "duplicates"').encode(),
        "long integer": json.dumps({**good, "n": 0}).replace('"n": 0', '"n": ' + "9" * 10_000).encode(),
        "deep": deep,
        "over the cap": b" " * (10 * 1024 * 1024 + 1),
        "extra key": json.dumps({**good, "extra": 1}).encode(),
        "wrong format": json.dumps({**good, "format": "gnd-type-judgements/2"}).encode(),
        "not utf-8": b"\xff\xfe{}",
        "a list": b"[]",
    }


@pytest.mark.parametrize("case", [
    "not json", "nan", "duplicate key", "long integer", "deep", "over the cap", "extra key", "wrong format",
    "not utf-8", "a list"])
def test_t2_hostile_judgements(shown, case):
    tmp_path, evidence = shown
    run, *_ = judged(tmp_path, raw={"duplicates": _hostile(evidence)[case]})
    assert run.returncode == 3, (case, run.stderr)
    assert "Traceback" not in run.stderr and nothing_written(tmp_path)


def test_t2_schema_message_never_echoes_the_rationale(shown):
    tmp_path, evidence = shown
    bad = judgements(evidence, "duplicates", DUPLICATES)
    bad["verdicts"][1]["rationale"] = CANARY * 400  # over 2,000 characters
    run, *_ = judged(tmp_path, duplicates=bad)
    assert run.returncode == 3 and CANARY not in run.stderr


# --- T3-T8: binding and coverage (TS2-C1) -------------------------------------


def test_t3_wrong_digest(shown):
    tmp_path, evidence = shown
    run, *_ = judged(tmp_path, duplicates=judgements(evidence, "duplicates", DUPLICATES, digest="0" * 64))
    assert run.returncode == 3 and "evidence_sha256" in run.stderr and nothing_written(tmp_path)


def test_t4_stale_population(shown):
    tmp_path, evidence = shown
    document = judgements(evidence, "duplicates", DUPLICATES)
    population = tmp_path / "items.population.json"
    data = json.loads(population.read_text())
    data["facts"][GENERIC].append({"item": "I-99", "name": "size", "value": "s99"})
    population.write_text(json.dumps(data))
    run, *_ = judged(tmp_path, "--show-values", duplicates=document)
    assert run.returncode == 3 and "population_sha256 differs" in run.stderr and nothing_written(tmp_path)


def test_t5_other_settings(shown):
    tmp_path, evidence = shown
    document = judgements(evidence, "duplicates", DUPLICATES)
    run, *_ = judged(tmp_path, "--show-values", "--min-support", "3", duplicates=document)
    assert run.returncode == 3 and "min_support differs" in run.stderr
    run, *_ = judged(tmp_path, duplicates=document, env={"GND_DISCLOSURE": "customer"})
    assert run.returncode == 3 and "show_values differs" in run.stderr and nothing_written(tmp_path)


def test_t6_kind_must_match_its_option(shown):
    tmp_path, evidence = shown
    run, *_ = judged(tmp_path, "--show-values", shapes=judgements(evidence, "duplicates", DUPLICATES))
    assert run.returncode == 3 and "expected 'shapes'" in run.stderr


@pytest.mark.parametrize("verdicts, message", [
    ([verdict("g0", "duplicate", of=INDUCED)], "group g1 has no verdict"),
    ([*DUPLICATES, verdict("g9", "distinct")], "g9 is not in the evidence"),
    ([*DUPLICATES, verdict("g1", "distinct")], "judged twice"),
    ([*DUPLICATES, verdict("g3", "distinct")], "status below_support"),
    ([verdict("g0", "duplicate", of=INDUCED), {**verdict("g1", "distinct"), "generic": "other"}],
     "another generic"),
])
def test_t7_coverage(shown, verdicts, message):
    tmp_path, evidence = shown
    run, *_ = judged(tmp_path, "--show-values", duplicates=judgements(evidence, "duplicates", verdicts))
    assert run.returncode == 3 and message in run.stderr, run.stderr
    assert nothing_written(tmp_path)


def test_t8_truncated_groups(tmp_path, monkeypatch):
    from gnd.discover import type_judgements

    evidence = {"truncated_groups": 2, "truncated": 0, "groups": []}
    with pytest.raises(type_judgements.TypeJudgementError, match="2 groups were left out"):
        type_judgements.bind(evidence, {"duplicates": {"verdicts": []}})


# --- T9-T13: duplicate verdicts (TS2-C2, C3, D4) -------------------------------


def test_t9_distinct_lifts_the_once_per_generic_limit(shown):
    tmp_path, evidence = shown
    run, out, report = judged(tmp_path, "--show-values", duplicates=judgements(evidence, "duplicates", DUPLICATES))
    assert run.returncode == 0, run.stderr
    found = family(report)
    [entry] = found["proposed"]
    assert entry["value"] == CANARY and entry["judged"] is True and "shape" not in entry
    assert entry["fact_type"] in fact_types(out)
    assert constraints(out)[entry["fact_type"]]["roles"] == ["entity"]


def test_t10_distinct_on_proposed_and_over_budget_groups(tmp_path, monkeypatch):
    from gnd.discover import service, type_evidence, type_judgements, types

    model, population = build(tmp_path, induced=False)
    monkeypatch.setattr(service, "MAX_EVOLUTION_PROPOSAL_BYTES",
                        service.BUDGET_MARGIN + 2 * len(model.read_bytes()) + 4000)
    result = service.discover(model, population, families=("fact-type",), max_values=20, max_pairs=256)
    document = type_evidence.build_evidence(
        result["view"], result["type_proposals"], model_sha256="0" * 64, population_sha256="0" * 64,
        min_support=20, show_values=True, show_digests=True, redacted_generics=[])
    assert [g["status"] for g in document["groups"][:2]] == ["proposed", "over_budget"]
    found = type_judgements.bind(document, {"duplicates": {"verdicts": [
        verdict("g0", "distinct"), verdict("g1", "distinct")]}})
    judged_ = types.propose(**result["type_arguments"], verdicts=found, judgement={
        "evidence_sha256": "0" * 64, "duplicates": {"sha256": "1" * 64, "skill": "s"}, "shapes": None})
    # The budget still decides: a judged group carries its provenance, so at
    # most the one that fitted before fits now; the rest are over budget.
    proposed = judged_.report["proposed"]
    assert all(entry["judged"] for entry in proposed) and len(proposed) <= 1
    assert len(proposed) + judged_.report["skipped"]["over_budget"] == 2
    roomy = types.propose(**{**result["type_arguments"], "budget": None}, verdicts=found, judgement={
        "evidence_sha256": "0" * 64, "duplicates": {"sha256": "1" * 64, "skill": "s"}, "shapes": None})
    assert [entry["judged"] for entry in roomy.report["proposed"]] == [True, True]


def test_t11_duplicate_without_an_equal_signature(shown):
    tmp_path, evidence = shown
    document = judgements(evidence, "duplicates", [verdict("g0", "duplicate", of=INDUCED),
                                                   verdict("g1", "duplicate", of="item_is_on_shelf_at")])
    run, out, report = judged(tmp_path, "--show-values", duplicates=document)
    assert run.returncode == 0, run.stderr
    found = family(report)
    assert found["proposed"] == [] and not out.exists()
    assert {(m["existing"], m.get("judged")) for m in found["shape_matches"]} == {
        (INDUCED, True), ("item_is_on_shelf_at", True)}


@pytest.mark.parametrize("of", ["item_has_attribute", "no_such_fact_type"])
def test_t12_of_must_be_a_listed_candidate(shown, of):
    tmp_path, evidence = shown
    document = judgements(evidence, "duplicates", [verdict("g0", "duplicate", of=of), verdict("g1", "distinct")])
    run, *_ = judged(tmp_path, "--show-values", duplicates=document)
    assert run.returncode == 3 and "is not a candidate" in run.stderr and of not in run.stderr


def test_t12_a_truncated_candidate_cannot_be_named():
    from gnd.discover import type_judgements

    evidence = {"truncated_groups": 0, "truncated": 1, "groups": [
        {"generic": GENERIC, "status": "shape_match", "candidates": []}]}
    with pytest.raises(type_judgements.TypeJudgementError, match="candidates were truncated"):
        type_judgements.bind(evidence, {"duplicates": {"verdicts": [verdict("g0", "duplicate", of=INDUCED)]}})


def test_t13_an_already_induced_attribute_is_not_distinct(shown):
    tmp_path, evidence = shown
    document = judgements(evidence, "duplicates", [verdict("g0", "distinct"), verdict("g1", "distinct")])
    run, *_ = judged(tmp_path, "--show-values", duplicates=document)
    assert run.returncode == 3 and f"already induced as {INDUCED}" in run.stderr


# --- T14-T18: shape verdicts (TS2-C4, C5) -------------------------------------


def test_t14_many_to_many(shown):
    tmp_path, evidence = shown
    run, out, report = judged(tmp_path, "--show-values", shapes=judgements(evidence, "shapes", SHAPES))
    assert run.returncode == 0, run.stderr
    found = family(report)
    [entry] = found["proposed"]
    assert entry["value"] == "tag" and entry["shape"] == "many-to-many" and entry["judged"] is True
    assert entry["support"] == {"numerator": 25, "denominator": 26}
    fact = fact_types(out)[entry["fact_type"]]
    assert [role["role_name"] for role in fact["roles"]] == ["entity", "value"]
    constraint = constraints(out)[entry["fact_type"]]
    assert constraint["roles"] == ["entity", "value"]
    assert (constraint["source"], constraint["status"], constraint["modality"]) == ("induced", "proposed", "deontic")
    induction = constraint["provenance"]["induction"]
    assert induction["support"] == {"numerator": 25, "denominator": 26}
    # The exact repeat (I-01, t1) is the second row of its pair.
    assert induction["counterexamples"] == ["ft0#73"] and len(induction["examples"]) == 25
    assert "ft0#73" not in induction["examples"]
    assert found["skipped"]["multi_valued"] == 0 and found["skipped"]["judged_skip"] == 0


def test_t15_skip(shown):
    tmp_path, evidence = shown
    run, out, report = judged(tmp_path, "--show-values",
                              shapes=judgements(evidence, "shapes", [verdict("g2", "skip")]))
    assert run.returncode == 0, run.stderr
    found = family(report)
    assert found["proposed"] == [] and found["skipped"]["judged_skip"] == 1
    assert found["skipped"]["multi_valued"] == 0 and not out.exists()


def test_t16_redaction_is_copied(tmp_path):
    model, _ = build(tmp_path)
    text = model.read_text().replace("{object_type: item, role_name: item}\n      - {object_type: attribute_name",
                                     "{object_type: item, role_name: item, redact: true}\n      - {object_type: attribute_name",
                                     1)
    model.write_text(text)
    run, _out, _report, evidence = discover(tmp_path, "--show-values", name="first",
                                            evidence="first.evidence.json")
    assert run.returncode == 0, run.stderr
    run, out, _report = judged(tmp_path, "--show-values", shapes=judgements(evidence, "shapes", SHAPES))
    assert run.returncode == 0, run.stderr
    [fact] = fact_types(out).values()
    assert fact["roles"][0].get("redact") is True and "redact" not in fact["roles"][1]


@pytest.mark.parametrize("kind, verdicts", [
    ("shapes", [verdict("g2", "functional")]),
    ("shapes", [verdict("g2", "distinct")]),
    ("duplicates", [verdict("g0", "many-to-many"), verdict("g1", "distinct")]),
    ("duplicates", [verdict("g0", "duplicate"), verdict("g1", "distinct")]),
    ("duplicates", [verdict("g0", "duplicate", of=INDUCED), verdict("g1", "distinct", of=INDUCED)]),
])
def test_t17_contradicted_or_foreign_verdicts(shown, kind, verdicts):
    tmp_path, evidence = shown
    document = {"format": "gnd-type-judgements/1", "kind": kind, "evidence_sha256": sha(evidence),
                "judge": {"skill": "s", "agent": "a"}, "verdicts": verdicts}
    run, *_ = judged(tmp_path, "--show-values", **{kind: document})
    assert run.returncode == 3, run.stderr
    assert nothing_written(tmp_path)


def test_t17_many_to_many_on_an_induced_attribute(tmp_path):
    from gnd.discover import type_judgements

    evidence = {"truncated_groups": 0, "truncated": 0, "groups": [
        {"generic": GENERIC, "status": "multi_valued", "candidates": [
            {"fact_type": "x", "origin": {"generic": GENERIC, "same_attribute": True}}]}]}
    with pytest.raises(type_judgements.TypeJudgementError, match="already induced as x"):
        type_judgements.bind(evidence, {"shapes": {"verdicts": [verdict("g0", "many-to-many")]}})


def test_t18_both_files(shown):
    tmp_path, evidence = shown
    run, out, report = judged(tmp_path, "--show-values", duplicates=judgements(evidence, "duplicates", DUPLICATES),
                              shapes=judgements(evidence, "shapes", SHAPES))
    assert run.returncode == 0, run.stderr
    found = family(report)
    assert sorted(entry["value"] for entry in found["proposed"]) == sorted([CANARY, "tag"])
    assert found["judgements"]["duplicates_sha256"] == sha(tmp_path / "duplicates.judgements.json")
    assert found["judgements"]["shapes_sha256"] == sha(tmp_path / "shapes.judgements.json")
    assert found["judgements"]["evidence_sha256"] == sha(evidence)
    assert "fact-type verdicts from duplicates.judgements.json, shapes.judgements.json" in json.loads(
        out.read_text())["rationale"]


# --- T19-T20: free text (TS2-C6, D10) ----------------------------------------


MODES = {"unset": {}, "customer": {"GND_DISCLOSURE": "customer"}, "internal": {"GND_DISCLOSURE": "internal"}}


@pytest.mark.parametrize("mode", ["unset", "customer", "internal"])
@pytest.mark.parametrize("leak", ["attribute", "value", "agent"])
def test_t19_a_rationale_that_names_a_value(tmp_path, mode, leak):
    env = MODES[mode]
    evidence = evidence_run(tmp_path, env=env)
    rationale = {"attribute": f"The {CANARY} attribute differs.", "value": "values such as T-Extra differ"}
    verdicts = [verdict("g0", "duplicate", of=INDUCED),
                verdict("g1", "distinct", rationale.get(leak, "fine"))]
    document = judgements(evidence, "duplicates", verdicts, agent="model c7 run" if leak != "agent" else CANARY)
    run, *_ = judged(tmp_path, duplicates=document, env=env)
    if mode == "internal":
        assert run.returncode == 0, run.stderr
    else:
        assert run.returncode == 3, run.stderr
        assert "names a population value" in run.stderr and CANARY not in run.stderr
        assert nothing_written(tmp_path)


def test_t19_a_digest_under_customer(tmp_path):
    env = {"GND_DISCLOSURE": "customer"}
    evidence = evidence_run(tmp_path, env=env)
    from test_discover_type_evidence import digest_of

    verdicts = [verdict("g0", "duplicate", of=INDUCED), verdict("g1", "distinct", f"digest {digest_of(CANARY)}")]
    run, *_ = judged(tmp_path, duplicates=judgements(evidence, "duplicates", verdicts), env=env)
    assert run.returncode == 3 and "verdict 1: rationale names a population value" in run.stderr


def test_t20_model_text_and_longer_words_are_not_leaks():
    from gnd.discover import type_judgements

    documents = {"duplicates": {"judge": {"agent": "a", "skill": "s"}, "verdicts": [
        {"rationale": "It sits on a Shelf, unlike colour-7f3a2 or xcolour-7f3a."}]}}
    # "shelf" is a population value here but also model text (D10); the canary
    # only occurs inside longer tokens.
    type_judgements.scan_free_text(documents, ["shelf", CANARY], "reading: '{Item} is on {Shelf}'")
    with pytest.raises(type_judgements.TypeJudgementError):
        type_judgements.scan_free_text(documents, ["shelf"], "nothing")
    multi = {"duplicates": {"judge": {"agent": "a", "skill": "s"}, "verdicts": [{"rationale": "from New   York, it says"}]}}
    with pytest.raises(type_judgements.TypeJudgementError):
        type_judgements.scan_free_text(multi, ["new york"], "")


def test_t20_overlapping_patterns():
    # Aho-Corasick suffix links: a pattern found only through a failure link.
    from gnd.discover import type_judgements

    text = {"duplicates": {"judge": {"agent": "a", "skill": "s"}, "verdicts": [{"rationale": "a b c d"}]}}
    with pytest.raises(type_judgements.TypeJudgementError):
        type_judgements.scan_free_text(text, ["a b c x", "b c d"], "")
    with pytest.raises(type_judgements.TypeJudgementError):
        type_judgements.scan_free_text(text, ["a b c x", "c"], "")
    type_judgements.scan_free_text(text, ["a b c x", "c d e"], "")


# --- T21-T24: admission and the round trip (TS2-C7, C9, D3) -----------------


def _preview_and_apply(tmp_path, out):
    model = tmp_path / "model.orm.yaml"
    common = ["--workspace", str(tmp_path), "--records", str(tmp_path / "records")]
    preview = tmp_path / "judged.preview.json"
    step = subprocess.run([sys.executable, "-m", "gnd", "evolve", "preview", str(model), str(out), *common,
                           "--out", str(preview), "--policy", "additive"], capture_output=True, text=True, check=False)
    assert step.returncode == 0, step.stdout + step.stderr
    applied = subprocess.run([sys.executable, "-m", "gnd", "evolve", "apply", str(model), str(out), "--preview",
                              str(preview), *common, "--policy", "additive"], capture_output=True, text=True,
                             check=False)
    assert applied.returncode == 0, applied.stdout + applied.stderr
    valid = subprocess.run([sys.executable, "-m", "gnd", "validate", str(model)], capture_output=True, text=True,
                           check=False)
    assert valid.returncode == 0, valid.stdout + valid.stderr


@pytest.mark.parametrize("mode", ["internal", "customer"])
def test_t21_to_t24_judged_proposals_apply_and_round_trip(tmp_path, mode):
    env = {"GND_DISCLOSURE": mode}
    evidence = evidence_run(tmp_path, env=env)
    duplicates = judgements(evidence, "duplicates", DUPLICATES)
    shapes = judgements(evidence, "shapes", SHAPES)
    run, out, report = judged(tmp_path, duplicates=duplicates, shapes=shapes, env=env)
    assert run.returncode == 0, run.stderr
    found = family(report)
    # T23: provenance on the fact types, recomputable from the files' bytes.
    for entry in found["proposed"]:
        fact = fact_types(out)[entry["fact_type"]]
        kind = "shapes" if entry.get("shape") else "duplicates"
        assert fact["provenance"]["judgement"] == {
            "evidence_sha256": sha(evidence), "judgements_sha256": sha(tmp_path / f"{kind}.judgements.json"),
            "kind": kind, "verdict": "many-to-many" if kind == "shapes" else "distinct",
            "skill": "gnd-model-multivalued" if kind == "shapes" else "gnd-judge-fact-types"}
        if mode == "customer":
            assert "induced_from" not in fact["provenance"]  # D3
        else:
            assert re.fullmatch("[0-9a-f]{64}", fact["provenance"]["induced_from"]["attribute_sha256"])
    # T21, T22: preview under the additive policy, apply, validate.
    _preview_and_apply(tmp_path, out)
    # T24: a fresh evidence file reads the origin back (internal) or none (customer).
    run, _out, _report, fresh = discover(tmp_path, env=env, name="second", evidence="second.evidence.json")
    assert run.returncode == 0, run.stderr
    canary_group = json.loads(fresh.read_text())["groups"][1]
    by_id = {candidate["fact_type"]: candidate for candidate in canary_group["candidates"]}
    new_id = next(entry["fact_type"] for entry in found["proposed"] if not entry.get("shape"))
    if mode == "customer":
        assert by_id[new_id]["origin"] is None
    else:
        assert by_id[new_id]["origin"]["same_attribute"] is True
        again = judgements(fresh, "duplicates", [
            verdict(g["group"], "distinct") for g in json.loads(fresh.read_text())["groups"]
            if g["status"] in ("proposed", "shape_match", "over_budget")])
        (tmp_path / "again.json").write_text(json.dumps(again))
        run, *_ = discover(tmp_path, "--type-evidence-in", "second.evidence.json", "--duplicate-judgements",
                           "again.json", env=env, name="third", evidence=None)
        assert run.returncode == 3 and "already induced" in run.stderr


# --- T26: no judgement, no change ----------------------------------------------


def test_t26_without_judgement_the_report_has_no_judgement_keys(shown):
    tmp_path, _evidence = shown
    found = family(tmp_path / "first.report.json")
    assert "judgements" not in found and "judged_skip" not in found["skipped"]
    assert all("judged" not in entry for entry in found["shape_matches"] + found["proposed"])


# --- T28: time bound (standing rule 2) -------------------------------------------


def test_t28_time_bound(tmp_path):
    groups = 20_000
    facts = [{"item": "I-00", "name": f"a{n}", "value": f"v{n}"} for n in range(groups)]
    build(tmp_path, induced=False, facts=facts)
    run, _out, _report, evidence = discover(tmp_path, "--min-support", "1", name="first",
                                            evidence="first.evidence.json")
    assert run.returncode == 0, run.stderr
    document = json.loads(evidence.read_text())
    assert document["truncated_groups"] == 0
    rationale = "the readings and the overlap counts differ from every candidate " * 6
    verdicts = [verdict(group["group"], "distinct", rationale[:380]) for group in document["groups"]
                if group["status"] in ("proposed", "shape_match", "over_budget")]
    started = time.monotonic()
    run, *_ = judged(tmp_path, "--min-support", "1", duplicates=judgements(evidence, "duplicates", verdicts))
    elapsed = time.monotonic() - started
    assert run.returncode == 0, run.stderr[-500:]
    assert elapsed < 120, elapsed


# --- T29: validation order (standing rule 3) -------------------------------------


def test_t29_order(shown):
    tmp_path, evidence = shown
    model = tmp_path / "model.orm.yaml"
    original = model.read_text()
    model.write_text("version: 2\nnot a model\n")
    run, *_ = judged(tmp_path, duplicates=judgements(evidence, "duplicates", DUPLICATES, digest="0" * 64))
    assert run.returncode == 3 and "evidence_sha256" in run.stderr
    model.write_text(original)
    (tmp_path / "judged.proposal.json").write_text("{}")
    run, *_ = judged(tmp_path, raw={"duplicates": b"{not json"})
    assert run.returncode == 11


def test_t29_source_order():
    from gnd.discover import service

    source = (ROOT / "src/gnd/discover/service.py").read_text()
    body = source[source.index("def _cmd_discover("):]
    steps = ["return EXIT_USAGE", "return EXIT_NO_INPUT", "return EXIT_COLLISION", "judgements.read(",
             "result = discover(", "_trimmed_proposal(result", "judgements.bind(", "scan_free_text(",
             "verdicts=verdicts", "output.write(out_path"]
    positions = [body.index(step) for step in steps]
    assert positions == sorted(positions)
    assert service.judgements.MAX_JUDGEMENTS_BYTES == 10 * 1024 * 1024


# --- Review findings (notes/phase-TS2-claude-review.md) --------------------------


def _in_process(tmp_path, monkeypatch, *, cap, **options):
    """Run discover in process, so a small evidence cap applies to both runs."""
    from datetime import UTC, datetime

    from gnd.discover import service, type_evidence

    monkeypatch.setattr(type_evidence, "MAX_EVIDENCE_BYTES", cap)
    common = {"report": str(tmp_path / "r.json"), "actor": "t", "requested_at": datetime(2026, 11, 5, tzinfo=UTC),
              "families": ("fact-type",), "max_values": 20, "max_pairs": 256, "output_format": "json",
              "show_values": True}
    model, population = str(tmp_path / "model.orm.yaml"), str(tmp_path / "items.population.json")

    def run(name, **extra):
        for suffix in ("o.json", "r.json"):
            (tmp_path / suffix).unlink(missing_ok=True)
        return service._cmd_discover(model, population, out=str(tmp_path / "o.json"),
                                     **{**common, **extra, **options})
    return run


def test_f1_an_induced_attribute_is_found_past_candidate_truncation(tmp_path, monkeypatch, capsys):
    build(tmp_path)
    run = _in_process(tmp_path, monkeypatch, cap=2600)
    assert run("first", type_evidence=str(tmp_path / "e.json")) == 0
    document = json.loads((tmp_path / "e.json").read_text())
    size = document["groups"][0]
    assert document["truncated"] > 0 and size["status"] == "shape_match"
    assert INDUCED not in {c["fact_type"] for c in size["candidates"]}
    verdicts = [verdict(g["group"], "distinct") for g in document["groups"]
                if g["status"] in ("proposed", "shape_match", "over_budget")]
    (tmp_path / "d.json").write_text(json.dumps(judgements(tmp_path / "e.json", "duplicates", verdicts)))
    capsys.readouterr()
    assert run("judged", type_evidence_in=str(tmp_path / "e.json"), duplicate_judgements=str(tmp_path / "d.json")) == 3
    assert f"already induced as {INDUCED}" in capsys.readouterr().err
    assert not (tmp_path / "o.json").exists()


def test_f2_the_skill_name_is_scanned(tmp_path):
    evidence = evidence_run(tmp_path)
    document = judgements(evidence, "duplicates", DUPLICATES)
    document["judge"]["skill"] = CANARY
    run, *_ = judged(tmp_path, duplicates=document)
    assert run.returncode == 3 and "judge.skill names a population value" in run.stderr
    assert nothing_written(tmp_path)


def test_f3_the_boundary_is_by_character():
    from gnd.discover import type_judgements

    def scan(text, hidden):
        documents = {"duplicates": {"judge": {"agent": "a", "skill": "s"}, "verdicts": [{"rationale": text}]}}
        type_judgements.scan_free_text(documents, hidden, "")

    # A letter or digit beside the value's own punctuation is no boundary.
    scan("Is this the same fact type?", ["?"])
    scan("version x-1 differs", ["-1"])
    scan("from co.uk", [".uk"])
    for text, hidden in (("Is it ? or not", ["?"]), ("a value of -1 here", ["-1"]), ("ends with -1", ["-1"]),
                         ("New-York, again", ["new-york"]), ("say (x) twice", ["(x)"])):
        with pytest.raises(type_judgements.TypeJudgementError):
            scan(text, hidden)


def test_f4_a_judged_clash_gets_its_own_reading(tmp_path):
    from test_discover_type_evidence import generic_rows

    facts = [row for row in generic_rows() if row["name"] != "size"]
    evidence = evidence_run(tmp_path, "--show-values", facts=facts)
    groups = json.loads(evidence.read_text())["groups"]
    assert groups[0]["status"] == "shape_match"
    document = judgements(evidence, "duplicates", [verdict("g0", "distinct")])
    run, out, _report = judged(tmp_path, "--show-values", duplicates=document)
    assert run.returncode == 0, run.stderr
    [fact] = fact_types(out).values()
    assert fact["id"] == f"{INDUCED}_1"
    assert fact["reading"] == "{Item} has induced item_has_attribute attribute 0_1 {AttributeValue}"


def test_f5_an_evidence_file_over_the_cap(tmp_path, monkeypatch, capsys):
    build(tmp_path)
    run = _in_process(tmp_path, monkeypatch, cap=10 * 1024 * 1024)
    assert run("first", type_evidence=str(tmp_path / "e.json")) == 0
    (tmp_path / "d.json").write_text(json.dumps(judgements(tmp_path / "e.json", "duplicates", DUPLICATES)))
    from gnd.discover import type_evidence

    monkeypatch.setattr(type_evidence, "MAX_EVIDENCE_BYTES", 100)
    capsys.readouterr()
    assert run("judged", type_evidence_in=str(tmp_path / "e.json"), duplicate_judgements=str(tmp_path / "d.json")) == 3
    assert "--type-evidence-in: the file exceeds 100 bytes" in capsys.readouterr().err


def test_f5_a_changed_model_is_named(shown):
    tmp_path, evidence = shown
    document = judgements(evidence, "duplicates", DUPLICATES)
    model = tmp_path / "model.orm.yaml"
    model.write_text(model.read_text().replace("model_id: urn:gnd-fixture:ts1-evidence@1",
                                               "model_id: urn:gnd-fixture:ts1-evidence@2"))
    run, *_ = judged(tmp_path, "--show-values", duplicates=document)
    assert run.returncode == 3 and "model_sha256 differs" in run.stderr


def test_f5_an_evidence_file_that_is_not_json(shown):
    tmp_path, _ = shown
    (tmp_path / "first.evidence.json").write_bytes(b"not json")
    document = judgements(tmp_path / "first.evidence.json", "duplicates", DUPLICATES)
    run, *_ = judged(tmp_path, "--show-values", duplicates=document)
    assert run.returncode == 3 and "is not this run's evidence" in run.stderr


def test_f5_an_origin_of_another_generic_is_no_contradiction():
    from gnd.discover import type_judgements

    evidence = {"truncated_groups": 0, "truncated": 0, "groups": [
        {"generic": GENERIC, "status": "shape_match", "candidates": [
            {"fact_type": "x", "origin": {"generic": "other_generic", "same_attribute": True}}]}]}
    found = type_judgements.bind(evidence, {"duplicates": {"verdicts": [verdict("g0", "distinct")]}})
    assert found[0].verdict == "distinct"


def test_f5_model_text_exemption_end_to_end(tmp_path):
    # "label" is a hidden attribute and a word of the model (a role name).
    facts = [{"item": f"I-{i:02d}", "name": "label", "value": f"l{i}"} for i in range(24)]
    evidence = evidence_run(tmp_path, facts=facts)
    groups = json.loads(evidence.read_text())["groups"]
    verdicts = [verdict(g["group"], "duplicate", "it reads like a label", of=INDUCED) for g in groups
                if g["status"] in ("proposed", "shape_match", "over_budget")]
    run, *_ = judged(tmp_path, duplicates=judgements(evidence, "duplicates", verdicts))
    assert run.returncode == 0, run.stderr


@pytest.mark.parametrize("failure, code", [("overflow", 70), ("write", 74)])
def test_f5_judged_path_internal_and_io_exits(tmp_path, monkeypatch, capsys, failure, code):
    from gnd.discover import output, type_evidence

    build(tmp_path)
    run = _in_process(tmp_path, monkeypatch, cap=10 * 1024 * 1024)
    assert run("first", type_evidence=str(tmp_path / "e.json")) == 0
    (tmp_path / "d.json").write_text(json.dumps(judgements(tmp_path / "e.json", "duplicates", DUPLICATES)))

    def broken(*_args, **_kwargs):
        if failure == "overflow":
            raise type_evidence.TypeEvidenceOverflow("x")
        raise OSError("disk full")

    monkeypatch.setattr(type_evidence if failure == "overflow" else output,
                        "evidence_bytes" if failure == "overflow" else "write", broken)
    assert run("judged", type_evidence_in=str(tmp_path / "e.json"),
               duplicate_judgements=str(tmp_path / "d.json")) == code
