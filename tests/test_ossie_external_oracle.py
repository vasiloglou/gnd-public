"""Explicitly selected external Ossie validation against the OS0 pin."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from gnd.errors import ModelValidationError
from gnd.export.ossie import render_ossie
from tools.ossie_oracle import OssieOracle

pytestmark = pytest.mark.ossie_oracle
ROOT = Path(__file__).resolve().parents[1]
CENSUS = (
    (ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS0/revised/census.txt")
    .read_text()
    .splitlines()
)


@pytest.fixture(scope="module")
def oracle():
    raw = os.environ.get("GND_OSSIE_ORACLE_ROOT")
    if not raw:
        pytest.fail("set GND_OSSIE_ORACLE_ROOT to the pinned scratch oracle environments")
    result = OssieOracle(Path(raw).resolve())
    result.check_pins()
    return result


INCLUDE_ROOTS = {
    "src/gnd/examples/expense/teams/engineering.orm.json",
    "src/gnd/examples/expense/teams/sales-v2.orm.json",
    "src/gnd/examples/expense/teams/sales.orm.json",
}


@pytest.mark.parametrize("relative", CENSUS)
def test_external_census(oracle, tmp_path, relative):
    if relative in INCLUDE_ROOTS:
        with pytest.raises(ModelValidationError, match="include:unsupported-route"):
            render_ossie(ROOT / relative, output_format="yaml")
        return
    bundle = render_ossie(ROOT / relative, output_format="yaml")
    path = tmp_path / "ontology.yaml"
    path.write_bytes(bundle.document)
    for read in (oracle.validate, oracle.parse):
        result = read(path)
        assert result.returncode == 0, result.stdout + result.stderr


def test_external_refusal_is_live(oracle, tmp_path):
    document = {
        "version": "0.3.0.dev0",
        "name": "BadReference",
        "ontology": [
            {
                "concept": "A",
                "type": "EntityType",
                "relationships": [
                    {
                        "name": "rel",
                        "roles": [{"concept": "Missing"}],
                        "verbalizes": ["{A} relates {Missing}"],
                    }
                ],
            }
        ],
    }
    path = tmp_path / "unknown.json"
    path.write_text(json.dumps(document))
    for read in (oracle.validate, oracle.parse):
        result = read(path)
        assert result.returncode == 1
        assert "Missing" in result.stdout + result.stderr


def test_yaml_role_name_is_a_string_in_both_upstream_readers(oracle, tmp_path):
    model = tmp_path / "source.json"
    model.write_text(
        json.dumps(
            {
                "version": 1,
                "object_types": [
                    {"id": "a", "name": "A", "kind": "value", "primitive": "String"},
                    {"id": "b", "name": "B", "kind": "value", "primitive": "String"},
                ],
                "fact_types": [
                    {
                        "id": "paired",
                        "reading": "{A} pairs {B}",
                        "roles": [
                            {"object_type": "a", "role_name": "first"},
                            {"object_type": "b", "role_name": "on"},
                        ],
                    }
                ],
            }
        )
    )
    output = tmp_path / "ontology.yaml"
    output.write_bytes(render_ossie(model, output_format="yaml").document)
    for read in (oracle.validate, oracle.parse):
        result = read(output)
        assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("scope", ("ontology", "concept", "relationship", "derivation"))
def test_pinned_parser_accepts_exported_os2_corpus(oracle, tmp_path, scope):
    source = (
        ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r2/model.orm.json"
    )
    result = render_ossie(source, output_format="json")
    path = tmp_path / "ontology.json"
    path.write_bytes(result.document)
    for read in (oracle.validate, oracle.parse):
        accepted = read(path)
        assert accepted.returncode == 0, accepted.stdout + accepted.stderr

    document = json.loads(result.document)
    concepts = document["ontology"]
    relationships = [rel for concept in concepts for rel in concept.get("relationships", ())]
    targets = {
        "ontology": document["requires"],
        "concept": next(concept["requires"] for concept in concepts if "requires" in concept),
        "relationship": next(rel["requires"] for rel in relationships if "requires" in rel),
        "derivation": next(rel["derived_by"] for rel in relationships if "derived_by" in rel),
    }
    targets[scope][0] = "COUNT[Account >"
    path.write_text(json.dumps(document))
    refused = oracle.parse(path)
    assert refused.returncode == 1 and "Unable to parse" in refused.stderr


def test_pinned_formula_keywords_are_case_sensitive(oracle, tmp_path):
    from tests.test_ossie_formulas import SOURCE

    document = json.loads(SOURCE.read_bytes())
    balance = document["fact_types"][0]
    balance["roles"][1]["role_name"] = "count"
    document["constraints"][0]["antecedent"][0]["bind"]["count"] = (
        document["constraints"][0]["antecedent"][0]["bind"].pop("balance")
    )
    for constraint in document["constraints"]:
        for key in ("role_seq_a", "role_seq_b"):
            for role in constraint.get(key, ()):
                if role["fact_type"] == "account_active":
                    role["fact_type"] = "exists"
    document = json.loads(json.dumps(document).replace('"account_active"', '"exists"'))
    source = tmp_path / "source.orm.json"
    source.write_text(json.dumps(document))
    ontology = json.loads(render_ossie(source, output_format="json").document)
    account = ontology["ontology"][0]
    assert account["relationships"][0]["requires"] == ["count <= 100"]
    assert any(
        "Account.exists" in rel.get("requires", ()) for rel in account["relationships"]
    )
    path = tmp_path / "ontology.json"
    path.write_text(json.dumps(ontology))
    accepted = oracle.parse(path)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr

    relationship = account["relationships"][0]
    relationship["roles"][0]["name"] = "COUNT"
    relationship["verbalizes"][0] = relationship["verbalizes"][0].replace(":count", ":COUNT")
    relationship["requires"] = ["COUNT <= 100"]
    path.write_text(json.dumps(ontology))
    refused = oracle.parse(path)
    assert refused.returncode == 1 and "Unable to parse" in refused.stderr


def _consumer_scopes(document):
    scopes = [("", document)]
    for i, concept in enumerate(document["ontology"]):
        pointer = f"/ontology/{i}"
        scopes.append((pointer, concept))
        scopes.extend(
            (f"{pointer}/relationships/{j}", rel)
            for j, rel in enumerate(concept.get("relationships", ()))
        )
    return scopes


def _consumer_formulas(document):
    return [
        {"pointer": f"{pointer}/{field}/{i}", "field": field, "formula": formula}
        for pointer, scope in _consumer_scopes(document)
        for field in ("requires", "derived_by")
        for i, formula in enumerate(scope.get(field, ()))
    ]


def _consumer_compare(oracle, root, name, document, gnd_model=None, *, checkout=None):
    import hashlib
    from subprocess import TimeoutExpired

    from gnd.errors import ModelLoadError, ModelValidationError
    from gnd.export.pyrel_rules import render as render_rules
    from gnd.export.pyrel_runtime import ExportInputError
    from tools.ossie_consumer import call_counts, ontology_declarations, pyrel_declarations
    from tools.ossie_oracle import convert_offline

    root.mkdir()
    path = root / "ontology.json"
    source = root / "consumer.py"
    path.write_bytes(document)
    authored = json.loads(document)
    formulas = _consumer_formulas(authored)
    result = {
        "case": name,
        "ontology_sha256": hashlib.sha256(document).hexdigest(),
        "formulas": formulas,
        "limitations": [],
    }
    if gnd_model is not None:
        try:
            rules = render_rules(gnd_model, "lqp").encode()
        except (ExportInputError, ModelLoadError, ModelValidationError) as error:
            result["gnd_rules"] = {"target": "lqp", "refused": str(error)}
        else:
            result["gnd_rules"] = {
                "target": "lqp",
                "require": call_counts(rules)["require"],
                "sha256": hashlib.sha256(rules).hexdigest(),
            }

    try:
        conversion = convert_offline(oracle, path, source, checkout=checkout)
    except TimeoutExpired:
        result.update(exit=124, diagnostics=["ossie-oracle: converter timed out"])
        return result
    if (
        "ossie-oracle: socket guard self-test passed" not in conversion.stdout.splitlines()
        or "ossie-oracle: network attempt after setup" in conversion.stderr.splitlines()
    ):
        result.update(exit=3, diagnostics=["ossie-oracle: socket guard verification failed"])
        return result
    result["socket_guard"] = "self-test-passed-no-audited-network-attempt"
    result["exit"] = conversion.returncode
    result["diagnostics"] = [
        line.replace(str(oracle.root), "$ORACLE").replace(str(root), "$CASE")
        for line in conversion.stderr.splitlines()
        if "Warning:" in line or line.startswith((
            "ValueError:", "NotImplementedError:", "KeyError:", "AssertionError:",
            "TypeError:", "RuntimeError:", "[Invalid identify_by]",
        ))
    ]
    if conversion.returncode != 0:
        if not result["diagnostics"]:
            result["diagnostics"] = [conversion.stderr.splitlines()[-1].strip()] if conversion.stderr else []
        return result

    try:
        generated = source.read_bytes()
        counts = call_counts(generated)
        observed = pyrel_declarations(generated)
    except (OSError, SyntaxError, TypeError, ValueError) as error:
        result.update(exit=3, diagnostics=[f"ossie-oracle: invalid generated source ({type(error).__name__})"])
        return result
    result["pyrel_sha256"] = hashlib.sha256(generated).hexdigest()
    result["calls"] = {
        name: counts[name]
        for name in ("Concept", "Property", "Relationship", "identify_by", "define", "where", "require", "not_")
    }
    result["declaration_difference"] = ontology_declarations(authored).difference(observed)
    if counts["require"] == 0:
        result["limitations"].extend(
            {**formula, "reason": "no-require-in-emitted-source"}
            for formula in formulas if formula["field"] == "requires"
        )
    return result


def _consumer_isolate(oracle, root, name, document, field, owners=None):
    projection = json.loads(document)
    removed = []
    for pointer, scope in _consumer_scopes(projection):
        if field in scope and (owners is None or scope.get("concept") in owners):
            removed.append({"pointer": f"{pointer}/{field}", "value": scope.pop(field)})
    assert removed
    result = _consumer_compare(oracle, root, name, json.dumps(projection).encode())
    result["isolation_removed"] = removed
    return result


def test_offline_consumer_census_and_formula_controls(oracle, tmp_path):
    import hashlib

    from tools.ossie_oracle import CONVERTERS_COMMIT, OSSIE_COMMIT

    os0 = ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS0"
    wheel = "relationalai-1.39.0-py3-none-any.whl"
    expected = json.loads((os0 / "pins.json").read_bytes())["relationalai_wheels_sha256"][wheel]
    assert hashlib.sha256((oracle.root / wheel).read_bytes()).hexdigest() == expected

    composition = "src/gnd/examples/composition/model.orm.yaml"
    library = "src/gnd/skills/gnd-model-from-text/examples/library_with_subtypes.orm.yaml"
    known = {
        composition: ("consumer-derivation-codegen", "should be bound by a type-membership Lookup"),
        library: ("consumer-inherited-identifier", "[Invalid identify_by] Property LibraryItem.gnd_reference"),
    }
    cases = []
    isolated = []
    for i, relative in enumerate(CENSUS):
        if relative in INCLUDE_ROOTS:
            continue
        model = ROOT / relative
        bundle = render_ossie(model, output_format="json")
        result = _consumer_compare(oracle, tmp_path / f"case-{i}", relative, bundle.document, model)
        if relative in known:
            reason, diagnostic = known[relative]
            if result["exit"] == 1 and any(diagnostic in line for line in result["diagnostics"]):
                result["limitations"].append({"reason": reason})
            field = "derived_by" if relative == composition else "identify_by"
            owners = None if relative == composition else {"BookItem", "PeriodicalItem"}
            isolated.append(_consumer_isolate(
                oracle, tmp_path / f"isolated-{i}", relative, bundle.document, field, owners,
            ))
        cases.append(result)
    assert len(cases) == 38

    corpus_path = (
        ROOT / ".gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r2/model.orm.json"
    )
    corpus = render_ossie(corpus_path, output_format="json").document
    full_corpus = _consumer_compare(
        oracle, tmp_path / "formula-corpus", "reviewed-formula-corpus", corpus, corpus_path,
    )
    if full_corpus["exit"] == 1 and any(
        "should be bound by a type-membership Lookup" in line for line in full_corpus["diagnostics"]
    ):
        full_corpus["limitations"].append({"reason": "consumer-derivation-codegen"})
    requires_control = _consumer_isolate(
        oracle, tmp_path / "requires-control", "requires-only-corpus", corpus, "derived_by",
    )
    controls = []
    for operator, formula in {
        "OR": "Account.account_active OR Account.account_registered",
        "EXISTS": "EXISTS(Account.account_active)",
    }.items():
        mutated = json.loads(corpus)
        for concept in mutated["ontology"]:
            for relationship in concept.get("relationships", ()):
                relationship.pop("derived_by", None)
                if relationship["name"] == "account_flagged":
                    relationship["derived_by"] = [formula]
        controls.append(_consumer_compare(
            oracle, tmp_path / operator, operator, json.dumps(mutated).encode(),
        ))

    evidence = {
        "schema": "gnd-ossie-consumer-observations/1",
        "ossie_commit": OSSIE_COMMIT,
        "converter_commit": CONVERTERS_COMMIT,
        "relationalai_version": "1.39.0",
        "relationalai_wheel_sha256": expected,
        "cases": cases,
        "full_formula_corpus": full_corpus,
        "isolations": isolated,
        "requires_control": requires_control,
        "refusal_controls": controls,
    }
    out = os.environ.get("GND_OSSIE_CONSUMER_OUTPUT")
    if out:
        Path(out).write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")

    failures = [row for row in cases if row["exit"] or row["declaration_difference"]]
    assert {row["case"] for row in failures} == known.keys(), failures
    for case in failures:
        assert {"reason": known[case["case"]][0]} in case["limitations"], case
    for case in [*isolated, requires_control]:
        assert case["exit"] == 0 and not case["declaration_difference"], case
    for case in cases:
        if case["exit"] == 0:
            assert case["calls"]["require"] == 0, case
    assert {"reason": "consumer-derivation-codegen"} in full_corpus["limitations"], full_corpus
    assert requires_control["calls"]["require"] == 0
    assert len(requires_control["limitations"]) == len(requires_control["formulas"]) > 0
    assert full_corpus["gnd_rules"]["require"] > 0
    for case in controls:
        assert case["exit"] != 0
        assert any("NotImplementedError:" in line and case["case"] in line for line in case["diagnostics"]), case
