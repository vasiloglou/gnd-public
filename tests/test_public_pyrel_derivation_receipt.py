"""Red approval corpus for Phase 3's additive, backend-scoped receipt contract.

These controls first require the new seat, so absence of the implementation can
never masquerade as a successful rejection. They never launch a foreign runtime.
"""

from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path
from typing import Any

import pytest
import test_public_derivation_parity_corpus as parity
from support.public_pyrel_receipt_binding import bind_original_receipt_builder

bind_original_receipt_builder(parity)

BACKENDS = ("duckdb", "pyrel", "souffle")


def _three_seat_receipt() -> dict[str, Any]:
    receipt = json.loads(parity.RECEIPT.read_text(encoding="utf-8"))
    assert receipt["cases"], "the Phase 3 receipt must not be empty"
    assert all(set(row["results"]) == set(BACKENDS) for row in receipt["cases"]), (
        "Phase 3 must add pyrel to every receipt row before these controls can pass"
    )
    return receipt


def _write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def test_pyrel_receipt_has_exact_case_order_and_backend_surface() -> None:
    receipt = _three_seat_receipt()
    assert receipt["schema_version"] == 1
    ids = [row["case_id"] for row in receipt["cases"]]
    assert len(ids) == len(set(ids)) == 75
    assert ids == [case["id"] for case in parity.PARITY_CASES]
    for row in receipt["cases"]:
        assert set(row["results"]["pyrel"]) == {"status", "version", "digest", "disposition"}
        current = {
            "model": row["model_sha256"],
            "population": row["population_sha256"],
            "production": row["production_sha256"],
        }
        assert parity._receipt_row_is_bound(row, backend="pyrel", current=current)
        result = row["results"]["pyrel"]
        if result["status"] != "skipped":
            assert result["version"] == "1.30.1"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-pyrel",
        "extra-backend",
        "model",
        "population",
        "production",
        "pyrel-digest",
        "pyrel-version",
        "reordered",
        "missing-case",
        "duplicate-case",
    ],
)
def test_pyrel_receipt_currency_rejects_dirty_evidence(
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    receipt = _three_seat_receipt()
    # Two genuine cases exercise order while avoiding ten full 75-case reruns.
    receipt["cases"] = receipt["cases"][:2]
    monkeypatch.setattr(parity, "PARITY_CASES", parity.PARITY_CASES[:2])
    target = tmp_path / "receipt.json"
    monkeypatch.setattr(parity, "RECEIPT", target)
    _write_receipt(target, receipt)
    parity.test_oracle_receipt_is_canonical_and_current()
    row = receipt["cases"][0]
    if mutation == "missing-pyrel":
        del row["results"]["pyrel"]
    elif mutation == "extra-backend":
        row["results"]["invented"] = copy.deepcopy(row["results"]["pyrel"])
    elif mutation in {"model", "population", "production"}:
        row[f"{mutation}_sha256"] = "0" * 64
    elif mutation == "pyrel-digest":
        row["results"]["pyrel"]["digest"] = "0" * 64
    elif mutation == "pyrel-version":
        row["results"]["pyrel"]["version"] = "0.0.0"
    elif mutation == "reordered":
        receipt["cases"].reverse()
    elif mutation == "missing-case":
        receipt["cases"].pop()
    elif mutation == "duplicate-case":
        receipt["cases"][1] = copy.deepcopy(row)
    _write_receipt(target, receipt)
    with pytest.raises(AssertionError):
        parity.test_oracle_receipt_is_canonical_and_current()


@pytest.mark.parametrize("backend", BACKENDS)
def test_pyrel_disposition_policy_is_scoped_and_bound_for_every_seat(backend: str) -> None:
    _three_seat_receipt()
    current = {
        "model": "a" * 64,
        "population": "b" * 64,
        "production": "c" * 64,
        "backend": "d" * 64,
        "version": "test",
    }
    base = {
        "case_id": "control",
        "model_sha256": current["model"],
        "population_sha256": current["population"],
        "production_sha256": current["production"],
        "results": {
            name: {
                "status": "mismatched",
                "version": "test",
                "digest": current["backend"],
                "disposition": None,
            }
            for name in BACKENDS
        },
    }
    for disposition, admitted in (
        ("encoding-bug", True),
        ("oracle-defect", True),
        ("evaluator-bug", False),
        ("spec-gap", False),
        ("unknown", False),
        (None, False),
    ):
        row = copy.deepcopy(base)
        row["results"][backend]["disposition"] = disposition
        assert (
            parity._receipt_row_is_admissible(
                row,
                backend=backend,
                current=current,
            )
            is admitted
        )
    allowed = copy.deepcopy(base)
    allowed["results"][backend]["disposition"] = "oracle-defect"
    for binding in ("model", "population", "production", "backend", "version"):
        assert not parity._receipt_row_is_admissible(
            allowed,
            backend=backend,
            current={**current, binding: "stale"},
        )
    for other in set(BACKENDS) - {backend}:
        cross = copy.deepcopy(base)
        cross["results"][other]["disposition"] = "oracle-defect"
        assert not parity._receipt_row_is_admissible(cross, backend=backend, current=current)
        assert parity._receipt_row_is_admissible(cross, backend=other, current=current)
    matched = copy.deepcopy(base)
    matched["results"][backend].update(status="matched", digest=current["production"])
    assert parity._receipt_row_is_admissible(
        matched,
        backend=backend,
        current={**current, "backend": current["production"]},
    )
    skipped = copy.deepcopy(base)
    skipped["results"][backend] = {
        "status": "skipped",
        "version": None,
        "digest": None,
        "disposition": None,
    }
    assert parity._receipt_row_is_bound(skipped, backend=backend, current=current)
    assert not parity._receipt_row_is_admissible(skipped, backend=backend, current=current)
    skipped["results"][backend]["disposition"] = "oracle-defect"
    assert not parity._receipt_row_is_bound(skipped, backend=backend, current=current)
    del skipped["results"][backend]
    assert not parity._receipt_row_is_bound(skipped, backend=backend, current=current)


@pytest.mark.parametrize("selected", [False, True], ids=["explicit-absence", "selected-seat"])
def test_pyrel_receipt_builder_selects_only_the_explicit_seat(
    selected: bool,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    assert "pyrel_executable" in inspect.signature(parity._build_receipt).parameters, (
        "Phase 3 receipt builder must expose explicit PyRel selection"
    )
    assert callable(getattr(parity, "_pyrel_extensions", None))
    case = parity.PARITY_CASES[0]
    monkeypatch.setattr(parity, "PARITY_CASES", [case])
    monkeypatch.setattr(parity, "RECEIPT", tmp_path / "absent.json")
    monkeypatch.setattr(parity, "_production_digest", lambda *_args: "c" * 64)
    monkeypatch.setattr(parity, "_canonical_digest", lambda *_args: "c" * 64)
    monkeypatch.setattr(parity, "_duckdb_extensions", lambda *_args: {})
    calls = []

    def fake_pyrel(
        model: Path, population: Path, *, executable: str | None = None
    ) -> dict[str, Any]:
        calls.append((model, population, executable))
        assert selected, "an explicitly absent PyRel seat must not execute"
        return {}

    monkeypatch.setattr(parity, "_pyrel_extensions", fake_pyrel)
    receipt = parity._build_receipt(
        souffle_executable=None,
        pyrel_executable="/selected/uv" if selected else None,
    )
    assert receipt["schema_version"] == 1
    assert len(receipt["cases"]) == 1
    assert set(receipt["cases"][0]["results"]) == set(BACKENDS)
    assert calls == (
        [(*parity._case_paths(case), "/selected/uv")] if selected else []
    )
    assert receipt["cases"][0]["results"]["pyrel"] == {
        "status": "matched" if selected else "skipped",
        "version": "1.30.1" if selected else None,
        "digest": "c" * 64 if selected else None,
        "disposition": None,
    }
    assert receipt["cases"][0]["results"]["duckdb"] == {
        "status": "matched",
        "version": parity.duckdb.__version__,
        "digest": "c" * 64,
        "disposition": None,
    }
    assert receipt["cases"][0]["results"]["souffle"] == {
        "status": "skipped",
        "version": None,
        "digest": None,
        "disposition": None,
    }


def test_direct_duckdb_parity_honors_a_bound_nonblocking_disposition(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The direct lane must not contradict the receipt policy it publishes."""
    case = next(
        case
        for case in parity.PARITY_CASES
        if any(
            rows
            for rows in parity._duckdb_extensions(
                parity.load_model(parity._case_paths(case)[0]),
                parity.load_population(
                    parity._case_paths(case)[1],
                    model=parity.load_model(parity._case_paths(case)[0]),
                ),
            ).values()
        )
    )
    model_path, population_path = parity._case_paths(case)
    model = parity.load_model(model_path)
    population = parity.load_population(population_path, model=model)
    changed = dict(parity._duckdb_extensions(model, population))
    head = next(name for name, rows in changed.items() if rows)
    changed[head] = changed[head][1:]
    production = parity._production_digest(model, population)
    observed = parity._canonical_digest(model, changed)
    assert observed != production
    receipt = {
        "cases": [
            {
                "case_id": case["id"],
                "model_sha256": parity._sha256(model_path),
                "population_sha256": parity._sha256(population_path),
                "production_sha256": production,
                "results": {
                    "duckdb": {
                        "status": "mismatched",
                        "version": parity.duckdb.__version__,
                        "digest": observed,
                        "disposition": "encoding-bug",
                    }
                },
            }
        ]
    }
    target = tmp_path / "receipt.json"
    _write_receipt(target, receipt)
    monkeypatch.setattr(parity, "RECEIPT", target)
    monkeypatch.setattr(parity, "_duckdb_extensions", lambda *_args: changed)
    parity.test_duckdb_matches_production(case)


def test_mismatch_status_cannot_carry_the_production_digest() -> None:
    current = {
        "model": "a" * 64,
        "population": "b" * 64,
        "production": "c" * 64,
        "backend": "c" * 64,
        "version": "test",
    }
    row = {
        "model_sha256": current["model"],
        "population_sha256": current["population"],
        "production_sha256": current["production"],
        "results": {
            "pyrel": {
                "status": "mismatched",
                "version": "test",
                "digest": current["production"],
                "disposition": "oracle-defect",
            }
        },
    }
    assert not parity._receipt_row_is_bound(row, backend="pyrel", current=current)
