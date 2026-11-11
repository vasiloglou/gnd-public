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
            if selected["pointer"] == f"{pointer}/requires/{i}":
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
        controls = []
        for i, formula in enumerate(formulas):
            result = _consumer_compare(
                oracle, scratch / f"formula-{i}", formula["pointer"],
                _variant(corpus, formula), checkout=checkout,
            )
            result["original_formula"] = formula
            controls.append(result)

    args.out.write_text(json.dumps({
        "schema": "gnd-ossie-contribution-observations/1",
        "base_converter_commit": CONVERTERS_COMMIT,
        "local_converter_commit": commit,
        "relationalai_version": "1.39.0",
        "census": cases,
        "isolated_formulas": controls,
    }, indent=2, sort_keys=True) + "\n")
    assert len(cases) == 38 and len(controls) == 8
    assert all(not row.get("declaration_difference") for row in [*cases, *controls])
    assert any(row.get("calls", {}).get("require") for row in controls)


if __name__ == "__main__":
    main()
