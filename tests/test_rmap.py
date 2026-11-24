"""OB2: the Halpin relational mapping (gnd.rmap) against its owner-approved corpus.

The corpus and its hand-derived answers (tests/fixtures/rmap) were approved at the
OB2 corpus gate before any gnd.rmap code existed.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/rmap"
CASES = sorted(path.name for path in (CORPUS / "cases").iterdir() if path.is_dir())
ALTERNATE = sorted(path.stem.split(".")[0] for path in (CORPUS / "answers").glob("*.alternate.json"))


def _answer(schema, dispositions):
    """The canonical answer shape of tests/fixtures/rmap/answers/README.md."""
    def table(t):
        return {
            "name": t.name,
            "subject": list(t.subject),
            "columns": [
                {"name": c.name, "datatype": c.datatype, "nullable": c.nullable, "origin": list(c.origin)}
                for c in t.columns
            ],
            "primary_key": list(t.primary_key),
            "unique_keys": [list(u) for u in t.unique_keys],
            "foreign_keys": [
                {"name": f.name, "columns": list(f.columns), "target_table": f.target_table,
                 "target_columns": list(f.target_columns)}
                for f in t.foreign_keys
            ],
        }

    return {
        "tables": [table(t) for t in schema.tables],
        "unmapped": [{"kind": u.kind, "id": u.id, "reason": u.reason, "detail": u.detail} for u in schema.unmapped],
        "dispositions": [
            {"kind": d.kind, "id": d.id, "carried_as": list(d.carried_as), "reason": d.reason}
            for d in dispositions
        ],
    }


def _map(case, variant_name):
    from gnd.model import load_model
    from gnd.rmap import RmapVariant, dispositions, map_model

    model = load_model(CORPUS / "cases" / case / "model.yaml")
    schema = map_model(model, variant=RmapVariant[variant_name])
    return _answer(schema, dispositions(model, schema))


@pytest.mark.parametrize("case", CASES)
def test_t6_halpin_matches_the_approved_answer(case):
    expected = json.loads((CORPUS / "answers" / f"{case[:2]}.json").read_text())
    assert _map(case, "HALPIN") == expected


@pytest.mark.parametrize("number", ALTERNATE)
def test_t6_alternate_matches_the_approved_answer(number):
    (case,) = [name for name in CASES if name.startswith(number)]
    expected = json.loads((CORPUS / "answers" / f"{number}.alternate.json").read_text())
    assert _map(case, "ALTERNATE") == expected


@pytest.mark.parametrize("case", sorted(set(CASES) - {c for c in CASES if c[:2] in ALTERNATE}))
def test_t6_variants_agree_where_no_alternate_answer_exists(case):
    assert _map(case, "ALTERNATE") == _map(case, "HALPIN")


def test_t8_public_surface():
    from gnd import rmap

    assert [member.name for member in rmap.RmapVariant] == ["HALPIN", "ALTERNATE"]
    assert set(rmap.UnmappedReason.__args__) == {
        "derived-computed", "uniqueness-not-confirmed", "identification-unmatchable", "spans-tables", "not-relational",
    }
    for cls in (rmap.Column, rmap.ForeignKey, rmap.Table, rmap.Unmapped, rmap.RelationalSchema, rmap.Disposition):
        assert dataclasses.is_dataclass(cls) and cls.__dataclass_params__.frozen
