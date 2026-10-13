"""Bounded compiled matching reuses existing reviewed numeric fixture rows."""
import copy
import json
from pathlib import Path

import pytest

from gnd import api, compiled_obligations as implementation
from gnd.model import load_model

CORPUS = Path(__file__).parent / "fixtures/compiled-snapshot"


def inputs():
    model = load_model(CORPUS / "model.orm.json")
    facts = json.loads((CORPUS / "numeric.pop.json").read_text())["facts"]
    entries = [entry for _,entry in implementation.compiled_entries(model)]
    return facts, entries


def test_empty_subset_spends_no_required_role_work():
    facts, entries = inputs()
    entry = next(e for e in entries if not facts.get(e["subset"]["of"])
                 and facts.get(e["subset"]["in"]))
    budget = implementation.WorkBudget(0)
    assert implementation.offending_rows(entry, facts, budget) == []
    assert budget.visits == 0


def test_required_projection_is_prepared_once():
    facts, entries = inputs()
    active = [e for e in entries if facts.get(e["subset"]["of"])]
    first, second = next((a,b) for a in active for b in active
                         if a is not b and a["subset"]["in"] == b["subset"]["in"]
                         and [p[1] for p in a["role_pairs"]] == [p[1] for p in b["role_pairs"]])
    roles = len(first["role_pairs"])
    expected = roles * (len(facts[first["subset"]["in"]])
                        +len(facts[first["subset"]["of"]])
                        +len(facts[second["subset"]["of"]]))
    budget = implementation.WorkBudget(expected)
    prepared = implementation._PreparedSubsetRows(facts, budget)
    assert prepared.offending_rows(first) == []
    assert prepared.offending_rows(second) == []
    assert budget.visits == expected


def test_right_role_order_has_separate_projection():
    facts, entries = inputs()
    entry = next(e for e in entries if facts.get(e["subset"]["of"])
                 and len(e["role_pairs"]) == 2)
    reversed_entry = copy.deepcopy(entry)
    reversed_entry["role_pairs"].reverse()
    expected = 4 * (len(facts[entry["subset"]["of"]])+len(facts[entry["subset"]["in"]]))
    budget = implementation.WorkBudget(expected)
    prepared = implementation._PreparedSubsetRows(facts,budget)
    assert prepared.offending_rows(entry) == prepared.offending_rows(reversed_entry) == []
    assert budget.visits == expected


def test_active_budget_remains_enforced():
    facts, entries = inputs()
    entry = next(e for e in entries if facts.get(e["subset"]["of"]))
    with pytest.raises(implementation.CompiledWorkLimit):
        implementation.offending_rows(entry,facts,implementation.WorkBudget(0))


def test_public_numeric_fixture_fits_actual_work_budget(monkeypatch):
    monkeypatch.setattr(implementation,"MAX_COMPILED_WORK",64)
    report = api.check(CORPUS / "model.orm.json",CORPUS / "numeric.pop.json",
                       compiled_operations=True)
    assert report["exit_code"] == 2
    assert not any(r.get("reason_code") == "compiled-obligation-work-limit"
                   for r in report["verdicts"])
