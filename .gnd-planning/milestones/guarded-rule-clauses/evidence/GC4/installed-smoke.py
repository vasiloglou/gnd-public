"""Exercise the guarded issue scenarios using only an installed GND CLI."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys


GUARDS = (
    "active_means_a_or_s", "shipped_over_raw_code",
    "delivered_two_forms", "exclude_test_accounts",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retail_population(status, delivery, *, shipped, confirmed, internal):
    model = "retail-model.json"
    uses = []
    if shipped:
        uses.append({"fact_type": "Order_is_shipped"})
    if confirmed:
        uses.append({"fact_type": "Carrier_confirmation"})
    excludes = [{"fact_type": "Customer_is_test"}]
    if internal:
        excludes.append({"fact_type": "Customer_is_internal"})
    facts = {
        "question_mentions_phrase": [
            {"phrase": phrase} for phrase in ("active customers", "delivered", "exclude test accounts")
        ],
        "filter_on": [
            {"filter": "customer-status", "concept": "Customer", "role": "status"},
            {"filter": "order-state", "concept": "Order", "role": "state_code"},
            {"filter": "order-delivery", "concept": "Order", "role": "status"},
        ],
        "filter_literal": [
            {"filter": "customer-status", "literal": status},
            {"filter": "order-state", "literal": "S"},
            {"filter": "order-delivery", "literal": delivery},
        ],
        "plan_uses_unary": uses,
        "plan_negates_unary": excludes,
    }
    return {"population": {"model": model, "source": "fixture", "covers": list(facts)}, "facts": facts}


def run(command, cwd, expected):
    result = subprocess.run(
        [sys.executable, "-I", "-m", "gnd", *command], cwd=cwd, capture_output=True,
        encoding="utf-8", timeout=40, check=False,
    )
    if result.returncode != expected:
        raise AssertionError((command, result.returncode, result.stdout, result.stderr))
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("scratch", type=Path)
    parser.add_argument("receipt", type=Path)
    opts = parser.parse_args()
    opts.scratch.mkdir()
    fixture = Path(__file__).with_name("retail-model.json")
    model = opts.scratch / fixture.name
    model.write_bytes(fixture.read_bytes())
    model_arg = model.name
    fixture_shas = {model.name: digest(model)}
    validate = json.loads(run(["validate", model_arg, "--format", "json"], opts.scratch, 0))
    assert validate["issues"] == []
    cases = {
        "all-violations": (
            retail_population("C", "P", shipped=False, confirmed=False, internal=False),
            ("warning", "warning", "warning", "warning"), 0,
        ),
        "via-d": (
            retail_population("A", "D", shipped=True, confirmed=False, internal=True),
            ("pass", "vacuous", "pass", "pass"), 2,
        ),
        "via-p-confirmed": (
            retail_population("S", "P", shipped=True, confirmed=True, internal=True),
            ("pass", "vacuous", "pass", "pass"), 2,
        ),
    }
    checked = {}
    for name, (population, expected, band) in cases.items():
        fixture_path = opts.scratch / f"{name}.population.json"
        fixture_path.write_text(json.dumps(population, indent=2) + "\n")
        fixture_shas[fixture_path.name] = digest(fixture_path)
        args = ["check", model_arg, fixture_path.name]
        report = json.loads(run([*args, "--rule-ids", "--format", "json"], opts.scratch, band))
        assert report["schema_version"] == 15
        assert [item["address"] for item in report["verdicts"]] == [f"constraint:{key}" for key in GUARDS]
        assert tuple(item["verdict"] for item in report["verdicts"]) == expected
        diagnostics = json.loads(run([*args, "--guarded-diagnostics", "--format", "json"], opts.scratch, band))
        assert diagnostics["schema_version"] == 17
        if name == "all-violations":
            row = diagnostics["verdicts"][2]
            [failed] = row["guarded_alternatives"]
            assert failed["alternatives"] == [
                {"index": 0, "reason": "missing-exists-atom", "fact_types": ["filter_literal"], "atom_indexes": [1]},
                {"index": 1, "reason": "missing-exists-atom", "fact_types": ["plan_uses_unary"], "atom_indexes": [2]},
            ]
        checked[name] = {"exit": band, "verdicts": dict(zip(GUARDS, expected, strict=True))}
        if name == "all-violations":
            checked[name]["delivery_diagnostics"] = diagnostics["verdicts"][2]["guarded_alternatives"]
        else:
            shipped = diagnostics["verdicts"][1]["guarded_antecedent"]
            assert shipped == {"binding_count": 0, "first_empty_atom_index": None}
            checked[name]["shipped_antecedent"] = shipped

    run(["synth", model_arg, "--guarded-cases", "--seed", "195", "--out", "generated"], opts.scratch, 0)
    manifest = json.loads((opts.scratch / "generated/guarded-cases.json").read_text())
    synthesized = {}
    for row in manifest["rules"]:
        rule = row["rule_id"]
        if rule == "shipped_over_raw_code":
            assert row["reason"] == "no-passing-case"
            assert not row["cases"]
        else:
            assert row["reason"] is None
            assert {case["verdict"] for case in row["cases"]} == {"warning", "pass"}
            assert all(case["binding_count"] > 0 for case in row["cases"])
        synthesized[rule] = {"reason": row["reason"], "cases": row["cases"]}
    assert set(synthesized) == set(GUARDS)

    import gnd
    from gnd import api

    assert Path(gnd.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())

    sentences = {}
    for line in api.verbalize_model(model).splitlines():
        if " If " not in line or " canonical=" not in line:
            continue
        prose, canonical = line.split(" canonical=", 1)
        rule = json.loads(canonical)["id"]
        sentence = "If " + prose.split(" If ", 1)[1].split(" source=", 1)[0]
        assert sentence.count(".") == 1
        sentences[rule] = sentence
    assert set(sentences) == set(GUARDS)
    assert "is one of" in sentences[GUARDS[0]]
    assert "unless" in sentences[GUARDS[1]]
    assert "at least one of" in sentences[GUARDS[2]]
    assert "joint assignment" in sentences[GUARDS[3]]
    receipt = {
        "installed_version": importlib.metadata.version("get-nick-done"),
        "wheel_sha256": digest(opts.wheel),
        "lock_sha256": digest(Path(__file__).resolve().parents[5] / "uv.lock"),
        "input_sha256": fixture_shas,
        "checked": checked,
        "synthesized": synthesized,
        "verbalization": sentences,
    }
    opts.receipt.write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
