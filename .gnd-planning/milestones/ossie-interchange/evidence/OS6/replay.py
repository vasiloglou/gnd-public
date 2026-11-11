"""Replay the OS4 instrument against a separately committed upstream branch."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))

from gnd.export.ossie import render_ossie
from tests.test_ossie_external_oracle import (
    CENSUS,
    INCLUDE_ROOTS,
    _consumer_compare,
    _consumer_formulas,
    _consumer_scopes,
)
from tools.ossie_oracle import CONVERTERS_COMMIT, OssieOracle

MILESTONE = Path(__file__).resolve().parents[2]


def _variant(corpus, selected):
    document = json.loads(corpus)
    for pointer, scope in _consumer_scopes(document):
        requires = scope.pop("requires", ())
        scope.pop("derived_by", None)
        for i, formula in enumerate(requires):
            if selected is not None and selected["pointer"] == f"{pointer}/requires/{i}":
                scope["requires"] = [formula]
    return json.dumps(document).encode()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--checkout", type=Path, required=True)
    cli.add_argument("--oracle", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    args = cli.parse_args()
    checkout = args.checkout.resolve()
    oracle = OssieOracle(args.oracle.resolve())
    oracle.check_pins()

    def git(*command):
        return subprocess.check_output(["git", "-C", str(checkout), *command], text=True, timeout=15).strip()

    commit = git("rev-parse", "HEAD")
    assert commit != CONVERTERS_COMMIT and not git("status", "--porcelain")
    git("merge-base", "--is-ancestor", CONVERTERS_COMMIT, commit)

    corpus_model = MILESTONE / "evidence/OS2/corpus-r2/model.orm.json"
    corpus = render_ossie(corpus_model, output_format="json").document
    formulas = [formula for formula in _consumer_formulas(json.loads(corpus)) if formula["field"] == "requires"]
    with TemporaryDirectory(prefix="ossie-os6-", dir=oracle.root) as work:
        scratch = Path(work)
        cases = []
        for i, relative in enumerate(CENSUS):
            if relative in INCLUDE_ROOTS:
                continue
            model = ROOT / relative
            document = render_ossie(model, output_format="json").document
            cases.append(_consumer_compare(
                oracle, scratch / f"case-{i}", relative, document, model, checkout=checkout,
            ))
        baseline = _consumer_compare(
            oracle, scratch / "formula-baseline", "no-formulas",
            _variant(corpus, None), checkout=checkout,
        )
        assert baseline["exit"] == 0 and not baseline["declaration_difference"]
        controls = []
        for i, formula in enumerate(formulas):
            result = _consumer_compare(
                oracle, scratch / f"formula-{i}", formula["pointer"],
                _variant(corpus, formula), checkout=checkout,
            )
            result["original_formula"] = formula
            if "metamodel_require_tasks" in result:
                result["added_require_tasks"] = (
                    result["metamodel_require_tasks"] - baseline["metamodel_require_tasks"]
                )
            if result.get("added_require_tasks") == 1 and result.get("calls", {}).get("require") == 0:
                result["source_omission"] = "RelationalAI 1.39.0 omits this value-only tuple requirement"
            controls.append(result)

    args.out.write_text(json.dumps({
        "schema": "gnd-ossie-contribution-observations/1",
        "base_converter_commit": CONVERTERS_COMMIT,
        "local_converter_commit": commit,
        "relationalai_version": "1.39.0",
        "census": cases,
        "isolation_baseline": baseline,
        "isolated_formulas": controls,
    }, indent=2, sort_keys=True) + "\n")
    assert len(cases) == 38 and len(controls) == 8
    assert all(not row.get("declaration_difference") for row in [*cases, *controls])
    reviewed = json.loads((MILESTONE / "evidence/OS4/reviewed/consumer-limitations.json").read_bytes())
    baseline_failures = {row["case"]: row for row in reviewed["cases"] if row["exit"]}
    actual_failures = {row["case"]: row for row in cases if row["exit"]}
    assert actual_failures.keys() == baseline_failures.keys()
    for name, failed in actual_failures.items():
        assert failed["exit"] == baseline_failures[name]["exit"]
        assert set(baseline_failures[name]["diagnostics"]) <= set(failed["diagnostics"])
    assert all(row["exit"] == 0 for row in controls)
    assert all(row["calls"]["require"] == 0 for row in controls)
    expected_refusals = {
        "COUNT[Account] <= 2": "ontology-level requires are not supported",
        "Category == 'Retail' OR Category == 'Business'": "needs a finite instance relation",
    }
    refused = set()
    for row in controls:
        formula = row["original_formula"]["formula"]
        if formula in expected_refusals:
            assert row["added_require_tasks"] == 0
            assert any(expected_refusals[formula] in warning for warning in row["diagnostics"])
            refused.add(formula)
        else:
            assert row["added_require_tasks"] == 1
            assert not row["diagnostics"]
    assert refused == expected_refusals.keys()


if __name__ == "__main__":
    main()
