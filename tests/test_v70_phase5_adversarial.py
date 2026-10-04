from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

import pytest

from gnd import api, cli, redaction, verbalize_population
from gnd.extract.anchors import AnchorSidecar, read_anchor_sidecar, vocabulary_digest
from gnd.model import load_model
from gnd.population import load_population, load_population_bytes

FIXTURE = Path(__file__).parent / "fixtures/v70-phase5"

@pytest.mark.parametrize(
    ("model", "population", "extra", "expected"),
    (
        ("missing.orm.yaml", "public.pop.json", (), 3),
        ("public.orm.yaml", "missing.pop.json", (), 3),
        ("public.orm.yaml", "private.pop.json", (), 3),
        ("public.orm.yaml", "public.pop.json", ("--anchors", "public.pop.json.anchors.json", "--document", "public-source-mutated.txt"), 3),
        ("public.orm.yaml", "public.pop.json", ("--anchors", "public.pop.json.anchors.json"), 64),
        ("public.orm.yaml", "public.pop.json", ("--document", "public-source.txt"), 64),
        ("public.orm.yaml", "public.pop.json", ("--format", "json"), 64),
    ),
)
def test_refusals_never_emit_a_success_row(
    model: str, population: str, extra: tuple[str, ...], expected: int,
) -> None:
    command = [
        sys.executable, "-m", "gnd", "verbalize", "population",
        str(FIXTURE / model), str(FIXTURE / population),
    ]
    for part in extra:
        command.append(str(FIXTURE / part) if part in {"public.pop.json.anchors.json", "public-source-mutated.txt", "public-source.txt"} else part)
    result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    assert result.returncode == expected
    assert result.stdout == ""
    assert "Traceback" not in result.stderr

def test_in_memory_population_marker_is_checked() -> None:
    model = load_model(FIXTURE / "public.orm.yaml")
    population = load_population(FIXTURE / "public.pop.json", model=model)
    assert api.verbalize(model, population)["exit_code"] == 0
    population.facts["b_pair"][0]["left"] = "changed after validation"
    assert api.verbalize(model, population) == {
        "rows": [], "exit_code": 3,
        "error": {"kind": "input", "message": "invalid model, population, anchors, or document"},
    }

def test_projection_is_live_and_fails_closed(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    calls: list[str] = []
    original = verbalize_population.project_output

    def observed(kind, payload, **kwargs):
        calls.append(kwargs["emitter_id"])
        return original(kind, payload, **kwargs)

    monkeypatch.setattr(verbalize_population, "project_output", observed)
    result = api.verbalize(FIXTURE / "private.orm.yaml", FIXTURE / "private.pop.json")
    assert result["exit_code"] == 0
    assert "SECRET-ROLE-CANARY" not in json.dumps(result)
    assert calls == ["api-population-verbalization"]

    def broken(*_args, **_kwargs):
        raise redaction.RedactionProjectionError("SECRET-ROLE-CANARY")

    monkeypatch.setattr(verbalize_population, "project_output", broken)
    assert cli.main([
        "verbalize", "population", str(FIXTURE / "private.orm.yaml"),
        str(FIXTURE / "private.pop.json"), "--format", "jsonl",
    ]) == 70
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "SECRET-ROLE-CANARY" not in captured.err
    assert "projection failed" in captured.err

def test_witness_rejects_unknown_role_and_projects_secret() -> None:
    public = load_model(FIXTURE / "public.orm.yaml")
    with pytest.raises(verbalize_population.PopulationVerbalizationError, match="unknown role"):
        verbalize_population.render_witness(public, "b_pair", {"left": "Ada", "right": "Zoe", "invented": "x"})
    with pytest.raises(verbalize_population.PopulationVerbalizationError, match="wrong primitive"):
        verbalize_population.render_witness(public, "c_amount", {"record": "R1", "amount": "one"})
    with pytest.raises(verbalize_population.PopulationVerbalizationError, match="unsupported role value"):
        verbalize_population.render_witness(public, "d_token", {"record": "R1", "token": {"redacted": True}})
    private = load_model(FIXTURE / "private.orm.yaml")
    applied = verbalize_population.render_witness(
        private, "b_secret", {"record": "R2", "token": "SECRET-ROLE-CANARY"},
    )
    clear = verbalize_population.render_witness(
        private, "b_secret", {"record": "R2", "token": "SECRET-ROLE-CANARY"}, unredacted=True,
    )
    assert "SECRET-ROLE-CANARY" not in applied
    assert "[REDACTED INSTANCE DETAIL]" in applied
    assert "SECRET-ROLE-CANARY" in clear

def test_many_facts_and_anchors_finish_within_bound() -> None:
    model = load_model(FIXTURE / "public.orm.yaml")
    data = json.loads((FIXTURE / "public.pop.json").read_text())
    count = 2000
    data["facts"]["b_pair"] = [
        {"left": f"Ada{index:04d}", "right": "Zoe"} for index in range(count)
    ]
    raw = json.dumps(data, separators=(",", ":")).encode()
    population = load_population_bytes(raw, source="many.json", model=model)
    source = "\n".join(f"Ada{index:04d}" for index in range(count)).encode()
    anchors = []
    for index in range(count):
        value = f"Ada{index:04d}"
        start = index * 8
        anchors.append({
            "fact_key": {"fact_type": "b_pair", "roles": {"left": value, "right": "Zoe"}},
            "role": "left", "span": {"start": start, "end": start + 7},
            "occurrence": 0, "excerpt_sha256": hashlib.sha256(value.encode()).hexdigest(),
        })
    sidecar = AnchorSidecar(
        1, hashlib.sha256(raw).hexdigest(), vocabulary_digest(model),
        hashlib.sha256(source).hexdigest(), tuple(anchors),
    )
    start = time.monotonic()
    result = api.verbalize(
        model, population, anchors=sidecar, document=source, population_bytes=raw,
    )
    elapsed = time.monotonic() - start
    assert result["exit_code"] == 0, result["error"]
    assert len(result["rows"]) == 2 * count + 8
    assert result["rows"][1]["excerpt"] == "left: 'Ada0000'"
    assert elapsed < 10.0

@pytest.mark.parametrize("damage", ("population", "vocabulary", "document", "span"))
def test_bad_sidecar_bindings_refuse_all_rows(damage: str) -> None:
    model = load_model(FIXTURE / "public.orm.yaml")
    raw = (FIXTURE / "public.pop.json").read_bytes()
    population = load_population_bytes(raw, source="public.json", model=model)
    document = (FIXTURE / "public-source.txt").read_bytes()
    sidecar = read_anchor_sidecar(FIXTURE / "public.pop.json.anchors.json")
    if damage == "span":
        anchors = [dict(anchor) for anchor in sidecar.anchors]
        anchors[0]["excerpt_sha256"] = "0" * 64
        sidecar = replace(sidecar, anchors=tuple(anchors))
    else:
        sidecar = replace(sidecar, **{f"{damage}_sha256" if damage != "vocabulary" else "vocabulary_digest": "0" * 64})
    result = api.verbalize(
        model, population, anchors=sidecar, document=document, population_bytes=raw,
    )
    assert result["exit_code"] == 3
    assert result["rows"] == []

def test_surrogate_value_refuses_before_any_output(tmp_path: Path) -> None:
    data = json.loads((FIXTURE / "public.pop.json").read_text())
    data["facts"]["a_note"][0]["note"] = "\ud800"
    path = tmp_path / "surrogate.pop.json"
    path.write_text(json.dumps(data))
    result = api.verbalize(FIXTURE / "public.orm.yaml", path)
    assert result["exit_code"] == 3
    assert result["rows"] == []
    model = load_model(FIXTURE / "public.orm.yaml")
    population = load_population(path, model=model)
    with pytest.raises(verbalize_population.PopulationVerbalizationError, match="surrogate"):
        verbalize_population.verbalize_population(model, population)
    for output_format in ("text", "jsonl"):
        command = [
            sys.executable, "-m", "gnd", "verbalize", "population",
            str(FIXTURE / "public.orm.yaml"), str(path), "--format", output_format,
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        assert completed.returncode == 3
        assert completed.stdout == ""

def test_mutated_model_schema_refuses_secret_before_projection() -> None:
    model = load_model(FIXTURE / "private.orm.yaml")
    model.fact_types[1]["roles"][1]["redact"] = "yes"
    population = load_population(FIXTURE / "private.pop.json", model=model)
    result = api.verbalize(model, population)
    assert result["exit_code"] == 3
    assert result["rows"] == []
    with pytest.raises(verbalize_population.PopulationVerbalizationError, match="invalid model"):
        verbalize_population.render_witness(
            model, "b_secret", {"record": "R2", "token": "SECRET-ROLE-CANARY"},
        )

def test_in_memory_population_cannot_borrow_another_population_sidecar() -> None:
    model = load_model(FIXTURE / "public.orm.yaml")
    shuffled = load_population(FIXTURE / "public-shuffled.pop.json", model=model)
    original_raw = (FIXTURE / "public.pop.json").read_bytes()
    result = api.verbalize(
        model, shuffled, anchors=FIXTURE / "public.pop.json.anchors.json",
        document=FIXTURE / "public-source.txt", population_bytes=original_raw,
    )
    assert result["exit_code"] == 3
    assert result["rows"] == []
    data = json.loads(original_raw)
    data["facts"]["c_amount"][0]["amount"] = 1
    data["facts"]["c_amount"][1]["amount"] = 1.0
    numeric_variant = load_population_bytes(
        json.dumps(data).encode(), source="numeric-variant.json", model=model,
    )
    result = api.verbalize(
        model, numeric_variant, anchors=FIXTURE / "public.pop.json.anchors.json",
        document=FIXTURE / "public-source.txt", population_bytes=original_raw,
    )
    assert result["exit_code"] == 3
    assert result["rows"] == []

@pytest.mark.parametrize("kind", ("malformed", "oversized"))
def test_malformed_or_oversized_sidecar_refuses_all_rows(tmp_path: Path, kind: str) -> None:
    sidecar = tmp_path / "bad.anchors.json"
    raw = b"{bad" if kind == "malformed" else b"x" * ((1 << 20) + 1)
    sidecar.write_bytes(raw)
    result = api.verbalize(
        FIXTURE / "public.orm.yaml", FIXTURE / "public.pop.json",
        anchors=sidecar, document=FIXTURE / "public-source.txt",
    )
    assert result["exit_code"] == 3
    assert result["rows"] == []
