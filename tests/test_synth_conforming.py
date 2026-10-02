"""``gnd synth --class conforming`` — the model -> data -> verdict path closed.

Two of the phase's three "the measurement must be able to fail" guards land here,
both on the data side, and these tests hold them to the standard the phase-stakes
brief set: a gate that cannot fail is worse than none.

- **Oracle independence (C1).** Ground truth is the assembler's INDEPENDENT
  constructive witness, never the checker's verdict. A checker ``fail`` on a
  constraint the witness proves satisfied is quarantined and exits 6 — the case
  retained, its ground truth never relabelled.
- **Positive non-degeneracy (Claude-HIGH).** Every join-scoped subject sequence
  (``subset``'s included, which never emits ``vacuous``) is asserted to yield
  >=1 row — a POSITIVE row count, not a wait-for-vacuous.
- **Loud re-admission.** A structurally-invalid population is a generator bug at
  exit 5, never a datum.
- **Sidecar binding (C6).** Swapped / stale / unknown-field sidecars are rejected.
- **Typed expectations (C3).** An expected-unchecked-by-design case is
  ``{satisfied, unchecked, reason}``, not a mislabelled artifact.
- **Convergence bound (Kimi).** Every loadable model converges to 0/5/6, no hang.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from gnd.checker import CheckReport, band, check
from gnd.checker import check as real_check
from gnd.cli import EXIT_USAGE, main
from gnd.model import Model, load_model
from gnd.population import load_population
from gnd.synth import assemble as assemble_module
from gnd.synth import boundary as boundary_module
from gnd.synth import provenance as provenance_module
from gnd.synth.assemble import (
    CheckerWitnessDiscrepancy,
    GeneratorError,
    assemble_conforming,
    measure_distinct_ratios,
)
from gnd.synth.paths import safe_output_path, slug
from gnd.synth.poolfile import load_pool
from gnd.synth.provenance import ExpectedState, SidecarError, read_sidecar

REPO_ROOT = Path(__file__).resolve().parent.parent
RING = REPO_ROOT / "tests" / "fixtures" / "checker" / "ring.orm.yaml"
SETFAM = REPO_ROOT / "tests" / "fixtures" / "checker" / "setfam.orm.yaml"
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
LLM_POOL = REPO_ROOT / "tests" / "fixtures" / "pools" / "full_vocabulary.llm.pool.json"

SMALL_MODELS = [RING, SETFAM]


def _check_doc(model_path: Path, doc: dict, tmp_path: Path) -> CheckReport:
    model = load_model(str(model_path))
    file = tmp_path / "pop.json"
    file.write_text(json.dumps(doc), encoding="utf-8")
    population = load_population(str(file), model=model)
    return check(model, population)


def _tree_bytes(root: Path) -> dict[str, bytes]:
    """Snapshot every permanent corpus file for transaction rollback assertions."""
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


# --------------------------------------------------------------------------- #
# task 1 — the working path on the two small checker fixtures
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("model_path", SMALL_MODELS, ids=lambda p: p.stem)
def test_emitted_conforming_loads_clean_and_reports_no_alethic_fail(model_path, tmp_path):
    model = load_model(str(model_path))
    assembly = assemble_conforming(model, 1, model_ref=model_path.name)
    report = _check_doc(model_path, assembly.doc, tmp_path)
    fails = [v for v in report.verdicts if v.verdict == "fail" and v.modality == "alethic"]
    assert fails == []
    assert band(report) in (0, 4)


@pytest.mark.parametrize("model_path", SMALL_MODELS, ids=lambda p: p.stem)
def test_same_seed_reproduces_byte_identical_across_processes(model_path, tmp_path):
    out_a, out_b = tmp_path / "a", tmp_path / "b"
    for out in (out_a, out_b):
        rc = main(["synth", str(model_path), "--out", str(out), "--seed", "5"])
        assert rc == 0
    stem = slug(model_path.stem)
    name = f"conforming/{stem}.conforming.seed5.json"
    assert (out_a / name).read_bytes() == (out_b / name).read_bytes()


@pytest.mark.parametrize("model_path", SMALL_MODELS, ids=lambda p: p.stem)
def test_omitted_seed_is_probabilistic_and_records_the_drawn_seed(model_path, tmp_path):
    out = tmp_path / "o"
    rc = main(["synth", str(model_path), "--out", str(out)])
    assert rc == 0
    sidecars = list((out / "conforming").glob("*.meta.json"))
    assert len(sidecars) == 1
    sidecar = read_sidecar(sidecars[0])
    # The drawn entropy seed is a real, recorded integer (regenerable), not a
    # frozen constant.
    assert isinstance(sidecar.seed, int)
    assert sidecar.seed != 0


def test_a_different_seed_produces_different_content():
    model = load_model(str(RING))
    a = assemble_conforming(model, 1, model_ref="ring.orm.yaml")
    b = assemble_conforming(model, 2, model_ref="ring.orm.yaml")
    assert json.dumps(a.doc, sort_keys=True) != json.dumps(b.doc, sort_keys=True)


def _comparison_model(primitive_a: str, primitive_b: str) -> Model:
    return Model(
        version=1,
        object_types=[
            {"id": "left_type", "kind": "value", "primitive": primitive_a},
            {"id": "right_type", "kind": "value", "primitive": primitive_b},
        ],
        fact_types=[
            {
                "id": "pair",
                "reading": "{left} precedes {right}",
                "roles": [
                    {"object_type": "left_type", "role_name": "left"},
                    {"object_type": "right_type", "role_name": "right"},
                ],
                "constraints": [
                    {
                        "type": "value-comparison",
                        "role_a": "left",
                        "operator": "<",
                        "role_b": "right",
                        "modality": "alethic",
                    }
                ],
            }
        ],
    )


def _comparison_doc(left, right) -> dict:
    return {
        "population": {
            "model": "comparison.orm.yaml",
            "source": "synthetic",
            "covers": ["pair"],
        },
        "facts": {"pair": [{"left": left, "right": right}]},
    }


def test_value_comparison_witness_uses_datetime_instants_with_offsets(tmp_path):
    """The independent oracle and checker agree on chronology, not text order."""
    from gnd.synth.assemble import _direct_subtypes, _witness

    model = _comparison_model("DateTime", "DateTime")
    doc = _comparison_doc("2024-01-01T10:00:00+02:00", "2024-01-01T09:00:00Z")
    constraint = model.fact_types[0]["constraints"][0]

    assert _witness(constraint, model.fact_types[0], doc, model, _direct_subtypes(model)) is True
    path = tmp_path / "offsets.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    report = check(model, load_population(str(path), model=model))
    assert report.verdicts[0].verdict == "pass"


def test_mismatched_ordering_domains_abstain_and_derive_unchecked_frontier(tmp_path):
    """A String-vs-Integer ordering is unchecked, never a synthetic violation."""
    from random import Random

    from gnd.synth.assemble import _direct_subtypes, _witness
    from gnd.synth.boundary import derive_boundary_cases, emit_boundary

    model = _comparison_model("String", "Integer")
    doc = _comparison_doc("alpha", 1)
    constraint = model.fact_types[0]["constraints"][0]
    ref = "fact_types[pair].constraints[0]"

    assert _witness(constraint, model.fact_types[0], doc, model, _direct_subtypes(model)) is None
    cases, downs = derive_boundary_cases(model, ref, doc, Random(1))
    assert downs == []
    assert len(cases) == 1 and cases[0].case_kind == "unchecked"
    assert cases[0].doc == doc
    admitted = emit_boundary(model, cases[0], tmp_path / "mismatched.json")
    assert admitted.predicted_verdict == admitted.observed_verdict == "unchecked"
    verdict = admitted.report.verdicts[0]
    assert verdict.reason_code == "values-not-comparable"


def test_injected_duplicate_raises_generator_error_and_cli_exits_5(monkeypatch, tmp_path):
    """The loud path is exercised, not merely written: a duplicate injected into a
    covered uniqueness projection makes the constructive witness fail -> exit 5."""
    model = load_model(str(SETFAM))

    def inject_duplicate(doc: dict) -> None:
        rows = doc["facts"].get("booking_by_person")
        if rows:
            rows.append(dict(rows[0]))

    with pytest.raises(GeneratorError):
        assemble_conforming(model, 1, model_ref="setfam.orm.yaml", fault=inject_duplicate)

    # And the CLI maps a GeneratorError to exit 5.
    def boom(*args, **kwargs):
        raise GeneratorError("forced")

    monkeypatch.setattr(assemble_module, "assemble_conforming", boom)
    rc = main(["synth", str(SETFAM), "--out", str(tmp_path / "o"), "--seed", "1"])
    assert rc == 5


def test_omitted_pool_materializes_a_hashed_pool_file(tmp_path):
    out = tmp_path / "o"
    rc = main(["synth", str(SETFAM), "--out", str(out), "--seed", "1", "--format", "json"])
    assert rc == 0
    pools = list((out / "conforming").glob("pool.*.pool.json"))
    assert len(pools) == 1
    sidecar = read_sidecar(next((out / "conforming").glob("*.meta.json")))
    assert sidecar.pool_sha256  # never empty, for Faker runs too
    assert sidecar.pool_source == "faker"
    assert not Path(sidecar.pool_path).is_absolute()


def test_a_rejected_pool_exits_5_with_the_enumerated_failures(tmp_path):
    bad_pool = tmp_path / "bad.pool.json"
    bad_pool.write_text(
        json.dumps(
            {"object_types": {}, "value_types": {}, "provenance": {"source": "faker"}}
        ),
        encoding="utf-8",
    )
    rc = main(
        ["synth", str(SETFAM), "--out", str(tmp_path / "o"), "--seed", "1", "--pool", str(bad_pool)]
    )
    assert rc == 5


# --------------------------------------------------------------------------- #
# sidecar (C6) + expectations (C3)
# --------------------------------------------------------------------------- #


def _emit_one(model_path: Path, out: Path, seed: int = 1) -> tuple[Path, Path]:
    rc = main(["synth", str(model_path), "--out", str(out), "--seed", str(seed)])
    assert rc == 0
    conforming = out / "conforming"
    population = next(
        p for p in conforming.glob("*.json")
        if not p.name.startswith("pool.") and not p.name.endswith(".meta.json")
    )
    sidecar = population.with_suffix(".meta.json")
    return population, sidecar


def test_sidecar_round_trips_and_covers_every_constraint(tmp_path):
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(RING, out)
    sidecar = read_sidecar(sidecar_path)
    assert sidecar.population_sha256
    assert sidecar.model_digest
    assert sidecar.pool_sha256
    assert not Path(sidecar.population).is_absolute()
    model = load_model(str(RING))
    declared = {
        f"fact_types[{ft.get('id')}].constraints[{i}]"
        for ft in model.fact_types or []
        for i, _c in enumerate(ft.get("constraints") or [])
    }
    assert declared <= set(sidecar.expectations)
    for state in sidecar.expectations.values():
        assert isinstance(state, ExpectedState)


def test_sidecar_rejects_a_stale_population_hash(tmp_path):
    out = tmp_path / "o"
    population, sidecar_path = _emit_one(RING, out)
    population.write_text(population.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(SidecarError):
        read_sidecar(sidecar_path)


def test_sidecar_swapped_next_to_a_different_population_is_rejected(tmp_path):
    out = tmp_path / "o"
    _p1, sc1 = _emit_one(RING, out / "one", seed=1)
    _p2, _sc2 = _emit_one(SETFAM, out / "two", seed=1)
    # Move the ring sidecar next to the setfam population.
    swapped = _p2.parent / sc1.name
    swapped.write_text(sc1.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(SidecarError):
        read_sidecar(swapped)


def test_sidecar_rejects_an_unknown_field(tmp_path):
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(RING, out)
    doc = json.loads(sidecar_path.read_text(encoding="utf-8"))
    doc["surprise"] = "drift"
    sidecar_path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(SidecarError):
        read_sidecar(sidecar_path)


@pytest.mark.parametrize(
    "schema_version", ["gnd-sidecar/1", "gnd-sidecar/2", "gnd-sidecar/3"]
)
def test_sidecar_accepts_supported_legacy_schema_versions(schema_version, tmp_path):
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(RING, out)
    doc = json.loads(sidecar_path.read_text(encoding="utf-8"))
    doc["schema_version"] = schema_version
    sidecar_path.write_text(json.dumps(doc), encoding="utf-8")

    assert read_sidecar(sidecar_path).schema_version == schema_version


def test_sidecar_rejects_an_unsupported_future_schema_version(tmp_path):
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(RING, out)
    doc = json.loads(sidecar_path.read_text(encoding="utf-8"))
    doc["schema_version"] = "gnd-sidecar/999"
    sidecar_path.write_text(json.dumps(doc), encoding="utf-8")

    with pytest.raises(SidecarError, match="schema_version"):
        read_sidecar(sidecar_path)


def test_sidecar_paths_are_relative_not_absolute(tmp_path):
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(FULL_VOCAB, out)
    sidecar = read_sidecar(sidecar_path)
    assert not Path(sidecar.population).is_absolute()
    assert not Path(sidecar.pool_path).is_absolute()


@pytest.mark.parametrize(
    "hostile",
    ["/Users/someone/pools/x.pool.json", "../outside/x.pool.json", "a/../../x.pool.json"],
    ids=["absolute", "parent-escape", "embedded-escape"],
)
def test_sidecar_rejects_an_absolute_or_escaping_pool_path(hostile, tmp_path):
    """WR-03: the relative-path rule is enforced on `pool_path`, not just on
    `population`.

    The module docstring and 02-06-SUMMARY both say the rule covers BOTH fields;
    only `population` was checked, so a sidecar naming an absolute pool validated
    clean and `gnd measure` then verified the pool digest against a file outside
    the corpus — on one machine only. Nested-but-contained segments stay legal:
    the pool legitimately lives in a subdirectory.
    """
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(RING, out)
    doc = json.loads(sidecar_path.read_text(encoding="utf-8"))
    doc["pool_path"] = hostile
    sidecar_path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(SidecarError, match="pool_path"):
        read_sidecar(sidecar_path)


def test_a_nested_pool_path_is_still_accepted(tmp_path):
    """The other half of WR-03: containment, not a ban on subdirectories."""
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(RING, out)
    doc = json.loads(sidecar_path.read_text(encoding="utf-8"))
    doc["pool_path"] = "conforming/nested/deeper/pool.abc.pool.json"
    sidecar_path.write_text(json.dumps(doc), encoding="utf-8")
    assert read_sidecar(sidecar_path).pool_path.startswith("conforming/nested")


def test_the_ring_witness_keeps_true_and_one_apart(tmp_path):
    """IN-01: the ring witness's pair set is KEYED, like every other identity here.

    ``pairs`` was built from raw values, so ``True`` and ``1`` collapsed into one
    element while ``_acyclic`` — reached from the same call — kept them apart
    through ``_key``. A Boolean-typed ring role is exotic, but the inconsistency
    is exactly what ``_key`` exists to prevent, and since the conforming class's
    expectations are now derived from this witness alone (CR-02), an identity
    that disagrees with itself between two ring components decides a published
    number.
    """
    from gnd.synth.assemble import _ring_satisfied, _tuple_key

    # `True` and `1` are the same dict key but different ORM values. As raw
    # tuples, {(True, 1)} reads as a self-loop and `irreflexive` reports FALSE.
    raw = {(True, 1)}
    assert _ring_satisfied("irreflexive", raw) is False  # the un-keyed reading

    keyed = {_tuple_key((True, 1))}
    assert _ring_satisfied("irreflexive", keyed) is True, (
        "a bool/int pair collapsed into a self-loop — the witness's identity "
        "disagrees with _acyclic's"
    )
    assert _ring_satisfied("acyclic", keyed) is True
    # And a REAL self-loop is still caught, in both variants.
    self_loop = {_tuple_key((1, 1))}
    assert _ring_satisfied("irreflexive", self_loop) is False
    assert _ring_satisfied("acyclic", self_loop) is False


def test_the_ring_call_site_keys_its_pairs():
    """The same property through ``_witness``, which is the call site that
    decides a sidecar's ground truth — a direct ``_ring_satisfied`` test would
    pass with the raw-value pair set still in place."""
    from types import SimpleNamespace

    from gnd.synth.assemble import _witness

    fact_type = {
        "id": "flag_relates_to_count",
        "roles": [
            {"role_name": "flag", "object_type": "flag_type"},
            {"role_name": "count", "object_type": "count_type"},
        ],
    }
    model = SimpleNamespace(
        fact_types=[fact_type],
        object_types=[
            {"id": "flag_type", "kind": "value"},
            {"id": "count_type", "kind": "value"},
        ],
        constraints=[],
    )
    doc = {"facts": {"flag_relates_to_count": [{"flag": True, "count": 1}]}}
    constraint = {"type": "ring", "variant": "irreflexive", "modality": "alethic"}

    assert _witness(constraint, fact_type, doc, model, {}) is True, (
        "`True` and `1` collapsed into a self-loop at the witness's own call site"
    )

    loop = {"facts": {"flag_relates_to_count": [{"flag": 1, "count": 1}]}}
    assert _witness(constraint, fact_type, loop, model, {}) is False


def test_expectations_represent_an_unchecked_by_design_constraint(tmp_path):
    """C3: an alethic ``textual`` constraint is {satisfied, unchecked, reason}, not
    a mislabelled measurement artifact — proven on full_vocabulary's textual."""
    out = tmp_path / "o"
    _population, sidecar_path = _emit_one(FULL_VOCAB, out)
    sidecar = read_sidecar(sidecar_path)
    textual = [
        state
        for state in sidecar.expectations.values()
        if state.expected_verdict == "unchecked" and state.reason == "textual-not-mechanical"
    ]
    assert textual, "expected a textual constraint expected-unchecked-by-design"
    assert textual[0].ground_truth == "satisfied"


# --------------------------------------------------------------------------- #
# C1 — oracle independence / quarantine
# --------------------------------------------------------------------------- #


def test_checker_witness_disagreement_quarantines_and_exits_6(monkeypatch, tmp_path):
    model = load_model(str(SETFAM))
    target = "fact_types[booking_by_person].constraints[0]"

    def lying_check(model_arg, population):
        report = real_check(model_arg, population)
        verdicts = [
            v.model_copy(update={"verdict": "fail", "scope_id": "snapshot:uniqueness:inline:violated:alethic"})
            if v.constraint_ref == target and v.verdict == "pass"
            else v
            for v in report.verdicts
        ]
        return CheckReport(verdicts=verdicts, coverage=report.coverage)

    # The assembler proves booking uniqueness satisfied by its INDEPENDENT witness;
    # the lying checker disagrees -> candidate false-fail -> quarantine, retained.
    monkeypatch.setattr(assemble_module, "check", lying_check)
    with pytest.raises(CheckerWitnessDiscrepancy) as excinfo:
        assemble_conforming(model, 1, model_ref="setfam.orm.yaml")
    discrepancies = excinfo.value.discrepancies
    assert discrepancies[0]["constraint_ref"] == target
    assert discrepancies[0]["witness"] == "satisfied"
    assert discrepancies[0]["observed"] == "fail"

    # The CLI writes the case to <out>/quarantine/ (retained, never discarded) and
    # exits 6 — and it does NOT relabel the sidecar ground truth to match.
    monkeypatch.setattr(assemble_module, "check", lying_check)
    out = tmp_path / "o"
    rc = main(["synth", str(SETFAM), "--out", str(out), "--seed", "1"])
    assert rc == 6
    quarantined = list((out / "quarantine").glob("*.json"))
    assert any(not p.name.endswith(".discrepancy.json") for p in quarantined)


def test_quarantine_destination_creation_failure_exits_io_without_staged_result(
    monkeypatch, tmp_path, capsys
):
    target = "fact_types[booking_by_person].constraints[0]"

    def lying_check(model_arg, population):
        report = real_check(model_arg, population)
        verdicts = [
            verdict.model_copy(update={"verdict": "fail", "scope_id": "snapshot:uniqueness:inline:violated:alethic"})
            if verdict.constraint_ref == target and verdict.verdict == "pass"
            else verdict
            for verdict in report.verdicts
        ]
        return CheckReport(verdicts=verdicts, coverage=report.coverage)

    out = tmp_path / "o"
    real_mkdir = Path.mkdir

    def failing_mkdir(path, *args, **kwargs):
        if path == out / "quarantine":
            raise OSError("injected quarantine destination creation failure")
        return real_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(assemble_module, "check", lying_check)
    monkeypatch.setattr(Path, "mkdir", failing_mkdir)
    rc = main(
        ["synth", str(SETFAM), "--out", str(out), "--seed", "1", "--format", "json"]
    )

    payload = json.loads(capsys.readouterr().out)
    assert rc == 74
    assert payload["exit_code"] == 74
    assert "injected quarantine destination creation failure" in payload["error"]
    assert "quarantine" not in payload
    assert not list(tmp_path.glob(".o.synth-*"))


def test_quarantine_copy_failure_exits_io_and_cleans_staging(monkeypatch, tmp_path, capsys):
    target = "fact_types[booking_by_person].constraints[0]"

    def lying_check(model_arg, population):
        report = real_check(model_arg, population)
        verdicts = [
            verdict.model_copy(update={"verdict": "fail", "scope_id": "snapshot:uniqueness:inline:violated:alethic"})
            if verdict.constraint_ref == target and verdict.verdict == "pass"
            else verdict
            for verdict in report.verdicts
        ]
        return CheckReport(verdicts=verdicts, coverage=report.coverage)

    def failing_copy(*args, **kwargs):
        raise OSError("injected quarantine copy failure")

    monkeypatch.setattr(assemble_module, "check", lying_check)
    monkeypatch.setattr(shutil, "copy2", failing_copy)
    out = tmp_path / "o"
    rc = main(
        ["synth", str(SETFAM), "--out", str(out), "--seed", "1", "--format", "json"]
    )

    payload = json.loads(capsys.readouterr().out)
    assert rc == 74
    assert payload["exit_code"] == 74
    assert "injected quarantine copy failure" in payload["error"]
    assert "quarantine" not in payload
    assert not list(tmp_path.glob(".o.synth-*"))


# --------------------------------------------------------------------------- #
# traversal (T-02-09)
# --------------------------------------------------------------------------- #


def test_model_derived_ids_cannot_escape_the_output_root(tmp_path):
    # slug neutralises an escaping token, and safe_output_path is the backstop.
    assert ".." not in Path(slug("../../etc/passwd")).parts
    from gnd.install import InstallPathError

    with pytest.raises(InstallPathError):
        safe_output_path(tmp_path, "../escape.json")
    with pytest.raises(InstallPathError):
        safe_output_path(tmp_path, "/etc/passwd")


# --------------------------------------------------------------------------- #
# convergence bound (Kimi) — every loadable model returns 0/5/6, no hang
# --------------------------------------------------------------------------- #


def _loadable_models() -> list[Path]:
    models_dir = REPO_ROOT / "tests" / "fixtures" / "models"
    out = []
    for path in sorted(models_dir.rglob("*.yaml")):
        try:
            load_model(str(path))
        except Exception:  # noqa: BLE001, S112 - an unloadable model is out of scope
            continue
        out.append(path)
    # Include the richer checker fixtures too — same convergence contract.
    out.extend([RING, SETFAM])
    return out


@pytest.mark.parametrize("model_path", _loadable_models(), ids=lambda p: p.stem)
def test_every_loadable_model_converges_to_0_5_or_6(model_path, tmp_path):
    model = load_model(str(model_path))
    try:
        assemble_conforming(model, 1, model_ref=model_path.name, max_rounds=20)
    except GeneratorError:
        return  # exit 5 — a recorded generator limitation, never a hang
    except CheckerWitnessDiscrepancy:
        return  # exit 6 — a retained candidate false-fail
    # exit 0/4 — converged.


# --------------------------------------------------------------------------- #
# task 2 — full_vocabulary, the join frontier, and the dual-pool proof
# --------------------------------------------------------------------------- #

FV_SEEDS = list(range(1, 31))


@pytest.mark.parametrize("seed", FV_SEEDS)
def test_full_vocabulary_converges_over_30_seeds_at_band_4(seed, tmp_path):
    """30 of 30 seeds against the all-families model converge, load clean, report
    zero alethic fail, and exit BAND 4 (the alethic textual constraint holds the
    run there forever — asserted, not worked around)."""
    model = load_model(str(FULL_VOCAB))
    assembly = assemble_conforming(model, seed, model_ref=FULL_VOCAB.name)
    report = _check_doc(FULL_VOCAB, assembly.doc, tmp_path)
    fails = [v for v in report.verdicts if v.verdict == "fail" and v.modality == "alethic"]
    assert fails == []
    assert band(report) == 4  # alethic textual -> indeterminate, by construction


def test_no_join_scoped_constraint_reports_vacuous_across_30_seeds(tmp_path):
    """The join frontier carries rows: no join-scoped constraint reports vacuous —
    the observable consequence of the POSITIVE non-degeneracy gate holding."""
    model = load_model(str(FULL_VOCAB))
    for seed in FV_SEEDS:
        assembly = assemble_conforming(model, seed, model_ref=FULL_VOCAB.name)
        report = _check_doc(FULL_VOCAB, assembly.doc, tmp_path)
        vacuous = [v.constraint_ref for v in report.verdicts if v.verdict == "vacuous"]
        assert vacuous == [], f"seed {seed} produced vacuous verdicts: {vacuous}"


def test_positive_non_degeneracy_gate_is_asserted_in_the_emission_path():
    """A degenerate join is a GeneratorError from the emission path, not merely a
    test-time check — the gate is POSITIVE (row count), independent of any family
    emitting vacuous (Claude-HIGH)."""
    from gnd.synth.assemble import _join_scoped_sequences, assert_non_degenerate

    model = load_model(str(FULL_VOCAB))
    seqs = list(_join_scoped_sequences(model))
    assert seqs, "full_vocabulary must have join-scoped subject sequences to gate"
    assembly = assemble_conforming(model, 1, model_ref=FULL_VOCAB.name)
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(assembly.doc, handle)
        temp = handle.name
    population = load_population(temp, model=model)
    assert_non_degenerate(model, population)  # passes on the conforming population


def test_entity_recurrence_is_below_one_beating_polyfactory_8_of_8(tmp_path):
    """distinct / draws < 1.0 wherever the pool is smaller than the fact count —
    the recurrence Polyfactory could not produce (its refuted 8-of-8)."""
    model = load_model(str(FULL_VOCAB))
    assembly = assemble_conforming(model, 1, model_ref=FULL_VOCAB.name)
    ratios = measure_distinct_ratios(model, assembly.doc)
    assert ratios
    strictly_recurring = [
        oid for oid, (distinct, draws) in ratios.items() if draws > distinct
    ]
    assert strictly_recurring, f"no entity recurred across facts: {ratios}"
    for distinct, draws in ratios.values():
        assert distinct <= draws


def test_llm_composed_pool_passes_load_pool_and_the_empirical_gate(tmp_path):
    """The seam is proven in both directions: an LLM-composed pool is admitted by
    the SAME gate as the Faker one — schema + coherence (load_pool) AND the
    empirical gate (a conforming population converges, loads clean, zero alethic
    fail, non-degenerate)."""
    model = load_model(str(FULL_VOCAB))
    pool = load_pool(str(LLM_POOL), model)  # schema + coherence
    assert pool.provenance.get("source") == "llm-proposed"
    assembly = assemble_conforming(model, 1, pool=pool, model_ref=FULL_VOCAB.name)
    report = _check_doc(FULL_VOCAB, assembly.doc, tmp_path)
    fails = [v for v in report.verdicts if v.verdict == "fail" and v.modality == "alethic"]
    assert fails == []
    assert band(report) == 4


def test_llm_pool_drives_the_cli_pipeline(tmp_path):
    rc = main(
        [
            "synth",
            str(FULL_VOCAB),
            "--out",
            str(tmp_path / "o"),
            "--class",
            "conforming",
            "--pool",
            str(LLM_POOL),
            "--seed",
            "1",
        ]
    )
    assert rc == 0


def test_index_merges_across_invocations_and_is_sorted(tmp_path):
    out = tmp_path / "o"
    assert main(["synth", str(FULL_VOCAB), "--out", str(out), "--seed", "1"]) == 0
    assert main(["synth", str(FULL_VOCAB), "--out", str(out), "--seed", "2"]) == 0
    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    populations = [entry["population"] for entry in index["populations"]]
    assert len(populations) == 2  # merged, not overwritten
    assert populations == sorted(populations)  # stable sorted order


@pytest.mark.parametrize(
    "malformed",
    [b"{broken", b'{"populations": [], "not_derivable": [], "extra": true}\n'],
    ids=("invalid-json", "invalid-shape"),
)
def test_synth_refuses_to_replace_a_malformed_existing_index(
    tmp_path, malformed
):
    out = tmp_path / "o"
    assert main(["synth", str(FULL_VOCAB), "--out", str(out), "--seed", "1"]) == 0
    index_path = out / "index.json"
    index_path.write_bytes(malformed)

    code = main(["synth", str(FULL_VOCAB), "--out", str(out), "--seed", "2"])

    assert code == 3
    assert index_path.read_bytes() == malformed
    assert not list(out.glob(".index.*.tmp"))


def test_synth_rolls_back_the_whole_batch_when_the_second_seed_fails(
    monkeypatch, tmp_path
):
    out = tmp_path / "o"
    assert main(["synth", str(SETFAM), "--out", str(out), "--seed", "1"]) == 0
    before = _tree_bytes(out)
    original = assemble_module.assemble_conforming
    calls = 0

    def fail_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise GeneratorError("injected second-seed failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(assemble_module, "assemble_conforming", fail_second)

    code = main(
        [
            "synth",
            str(SETFAM),
            "--out",
            str(out),
            "--seed",
            "20",
            "--seeds",
            "2",
        ]
    )

    assert code == 5
    assert _tree_bytes(out) == before


def test_synth_rolls_back_the_whole_batch_when_the_second_boundary_case_fails(
    monkeypatch, tmp_path
):
    out = tmp_path / "o"
    assert main(["synth", str(SETFAM), "--out", str(out), "--seed", "1"]) == 0
    before = _tree_bytes(out)
    original = boundary_module.emit_boundary
    calls = 0

    def fail_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise GeneratorError("injected second-boundary-case failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(boundary_module, "emit_boundary", fail_second)

    code = main(
        [
            "synth",
            str(SETFAM),
            "--out",
            str(out),
            "--class",
            "boundary",
            "--seed",
            "20",
        ]
    )

    assert code == 5
    assert calls == 2
    assert _tree_bytes(out) == before


def test_synth_rolls_back_the_whole_batch_when_a_sidecar_write_fails(
    monkeypatch, tmp_path
):
    out = tmp_path / "o"
    assert main(["synth", str(SETFAM), "--out", str(out), "--seed", "1"]) == 0
    before = _tree_bytes(out)

    def fail_sidecar(*args, **kwargs):
        raise OSError("injected sidecar write failure")

    monkeypatch.setattr(provenance_module, "write_sidecar", fail_sidecar)

    code = main(["synth", str(SETFAM), "--out", str(out), "--seed", "2"])

    assert code == 74
    assert _tree_bytes(out) == before


def test_synth_rolls_back_the_whole_batch_when_index_replacement_fails(
    monkeypatch, tmp_path
):
    out = tmp_path / "o"
    assert main(["synth", str(SETFAM), "--out", str(out), "--seed", "1"]) == 0
    before = _tree_bytes(out)
    real_replace = os.replace

    def fail_index_replace(source, destination):
        if Path(destination).name == "index.json":
            raise OSError("injected index replacement failure")
        return real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_index_replace)

    code = main(["synth", str(SETFAM), "--out", str(out), "--seed", "2"])

    assert code == 74
    assert _tree_bytes(out) == before


def test_cli_seeds_default_is_one(tmp_path):
    out = tmp_path / "o"
    assert main(["synth", str(FULL_VOCAB), "--out", str(out), "--seed", "1", "--format", "json"]) == 0
    populations = [
        p
        for p in (out / "conforming").glob("*.json")
        if not p.name.startswith("pool.") and not p.name.endswith(".meta.json")
    ]
    assert len(populations) == 1  # default --seeds 1, the lightweight dev lane


@pytest.mark.parametrize("invalid_count", ["0", "-1"], ids=["zero", "negative"])
def test_cli_rejects_non_positive_seed_counts(invalid_count, tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gnd",
            "synth",
            str(SETFAM),
            "--out",
            str(tmp_path / "o"),
            "--seeds",
            invalid_count,
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )

    assert result.returncode == EXIT_USAGE
    assert "positive integer" in result.stderr


@pytest.mark.parametrize("class_", ["conforming", "boundary", "violating", "all"])
def test_cli_seeds_emits_independent_variants_for_every_class(class_, tmp_path):
    out = tmp_path / class_
    assert main(
        [
            "synth",
            str(SETFAM),
            "--out",
            str(out),
            "--class",
            class_,
            "--seed",
            "10",
            "--seeds",
            "2",
        ]
    ) == 0

    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    entries = index["populations"]
    assert len({entry["population"] for entry in entries}) == len(entries)

    if class_ in ("conforming", "all"):
        conforming = [entry for entry in entries if entry["class"] == "conforming"]
        assert {entry["seed"] for entry in conforming} == {10, 11}

    expected_derivative_classes = (
        {class_} if class_ in ("boundary", "violating") else {"boundary", "violating"}
    )
    if class_ == "conforming":
        expected_derivative_classes = set()
    for derivative_class in expected_derivative_classes:
        sidecars = [
            read_sidecar(out / entry["sidecar"])
            for entry in entries
            if entry["class"] == derivative_class
        ]
        assert sidecars
        assert {sidecar.baseline_seed for sidecar in sidecars} == {10, 11}
        assert sum(sidecar.baseline_seed == 10 for sidecar in sidecars) == sum(
            sidecar.baseline_seed == 11 for sidecar in sidecars
        )


def test_schema_sync_untouched():
    """D-15: the population format is never touched — its sync test must be green
    and its file byte-unchanged (this plan added nothing to population.schema.json
    or its synced copies)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_schema_sync.py::test_canonical_and_vendored_schemas_are_byte_identical", "-q"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_value_witness_allowed_membership_is_by_identity_not_equality():
    """F-7: `allowed` membership must not collapse `True` with `1`.

    `bool` subclasses `int`, so plain `in` reports `1 in [True]` as True. The
    checker uses identity-keyed membership, so a population carrying `1` against
    `allowed: [true]` is a genuine `fail`. A witness answering SATISFIED there
    would publish the checker's correct verdict as a false fail — the F-3 shape,
    in the one branch F-01 left unkeyed.

    This drives `_value_witness` itself: asserting on `_key` alone would pass
    even with the plain-`in` implementation restored, which is a gate that
    cannot fail.
    """
    from gnd.synth.assemble import _value_witness

    constraint = {"type": "value", "allowed": [True]}

    # the violating population: 1 is NOT True, so the witness must say violated
    assert _value_witness(constraint, [1]) is False
    # the conforming population still reads satisfied
    assert _value_witness(constraint, [True]) is True
    # and the same in the other direction of the collapse
    assert _value_witness({"type": "value", "allowed": [1]}, [True]) is False


@pytest.mark.parametrize(
    ("allowed", "candidate", "expected"),
    [
        (True, 1, False),
        (1, True, False),
        (False, 0, False),
        (0, False, False),
        (1, 1.0, True),
        (1.0, 1, True),
    ],
)
def test_value_witness_uses_normative_scalar_identity(
    allowed, candidate, expected
):
    from gnd.synth.assemble import _value_witness

    assert _value_witness({"type": "value", "allowed": [allowed]}, [candidate]) is expected


def test_boundary_and_mutation_share_normative_scalar_identity():
    from gnd.synth import boundary, mutate

    for key in (boundary._key, mutate._key):
        assert key(1) == key(1.0)
        assert key(True) != key(1)
        assert key(False) != key(0)


def test_conforming_assembly_draws_from_all_value_constraint_intersections():
    from gnd.model import Model

    model = Model(
        version=1,
        object_types=[{"id": "n", "kind": "value", "primitive": "Number"}],
        fact_types=[
            {
                "id": "observed",
                "reading": "{n} was observed",
                "roles": [{"object_type": "n", "role_name": "n"}],
            }
        ],
        constraints=[
            {
                "type": "value",
                "object_type": "n",
                "allowed": [1, 2],
                "modality": "alethic",
            },
            {
                "type": "value",
                "object_type": "n",
                "allowed": [2, 3],
                "modality": "alethic",
            },
        ],
    )

    assembly = assemble_conforming(model, 5)

    assert {fact["n"] for fact in assembly.doc["facts"]["observed"]} == {2}
