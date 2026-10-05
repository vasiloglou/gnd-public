from __future__ import annotations

import json
from pathlib import Path

from support.cli_runner import run_main
from test_v70_phase2_recursion import _write_model, _write_population

from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_adapter import adapt_snapshot


def test_exact_term_clause_model_is_explicitly_refused_by_synth(tmp_path: Path) -> None:
    model = _write_model(tmp_path, "exact_recursive")
    out = tmp_path / "synth-exact"
    result = run_main(
        ["synth", str(model), "--class", "conforming", "--seed", "7", "--out", str(out), "--format", "json"],
        capture_stderr=False,
    )
    assert result.returncode == 5
    assert json.loads(result.stdout)["error"].startswith("synth-derivation-unsupported:")
    assert not out.exists() or not any(out.iterdir())

def test_adapter_retains_each_recursive_clause(tmp_path: Path) -> None:
    model = load_model(_write_model(tmp_path, "base"))
    population = load_population(_write_population(tmp_path, "base"), model=model)
    rows = [
        rule for rule in adapt_snapshot(model, population).derivations
        if rule.fact_type == "reaches"
    ]
    assert len(rows) == 2
    assert [atom.fact_type for atom in rows[0].body] == ["edge"]
    assert [atom.fact_type for atom in rows[1].body] == ["edge", "reaches"]
