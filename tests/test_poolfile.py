"""The pool artifact gate: schema rejection, coherence rejection with the full
failure list, resolve-or-skip on unresolvable primitives, sha256 stability, and
Faker-pool shape identity.

The seam's whole value is that an LLM-proposed pool and a Faker-built pool are the
same artifact, admitted by the same two gates. These tests prove the gate can
REJECT (a gate that cannot fail is worse than none) and that the builder's output
round-trips its own gate (a builder and validator that disagree would be the
two-implementations drift this project keeps removing).
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from gnd.cli import main
from gnd.model import Model, load_model
from gnd.synth.poolfile import (
    Pool,
    PoolValidationError,
    _distinctness_demand,
    _join_key_types,
    build_faker_pool,
    load_pool,
    write_pool,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_GND = REPO_ROOT / "src" / "gnd"
FULL_VOCAB = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"
RING = REPO_ROOT / "tests" / "fixtures" / "checker" / "ring.orm.yaml"
SETFAM = REPO_ROOT / "tests" / "fixtures" / "checker" / "setfam.orm.yaml"

FIXTURE_MODELS = [FULL_VOCAB, RING, SETFAM]


def _valid_payload(model: Model, seed: int = 4242) -> dict:
    """A freshly built, gate-passing pool as a mutable payload dict."""
    pool = build_faker_pool(model, seed)
    return {
        "object_types": copy.deepcopy(pool.object_types),
        "value_types": copy.deepcopy(pool.value_types),
        "provenance": copy.deepcopy(pool.provenance),
    }


def _write(tmp_path: Path, payload: dict, name: str = "pool.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# 1. the builder round-trips its own gate
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("model_path", FIXTURE_MODELS, ids=lambda p: p.stem)
def test_build_faker_pool_round_trips_load_pool(model_path: Path, tmp_path: Path) -> None:
    """build_faker_pool output passes load_pool clean for every fixture model —
    including full_vocabulary's salary (unit-based) and assignment (external),
    whose primitives are unresolvable and are admitted by resolve-or-skip."""
    model = load_model(model_path)
    pool = build_faker_pool(model, 20260812)
    path = tmp_path / "built.pool.json"
    write_pool(pool, path)

    loaded = load_pool(path, model)
    assert loaded.sha256 == pool.sha256, (
        "the builder's own output did not survive its own gate unchanged — builder "
        "and validator disagree about what a valid pool is."
    )
    assert loaded.provenance["source"] == "faker"


def test_full_vocabulary_admits_the_two_unresolvable_types(tmp_path: Path) -> None:
    """salary (unit-based) and assignment (external) resolve to no primitive, and
    the gate performs NO invented type check for them — a value that no single
    primitive predicate would accept is still admitted (D-05)."""
    model = load_model(FULL_VOCAB)
    payload = _valid_payload(model)
    # Deliberately heterogeneous, non-primitive-typed opaque identifiers: a free
    # string AND a number in the same list. No primitive predicate accepts both.
    payload["object_types"]["salary"] = ["a free-text salary token", 999]
    payload["object_types"]["assignment"] = ["assignment#alpha", "assignment#beta"]
    path = _write(tmp_path, payload)

    loaded = load_pool(path, model)  # must NOT raise
    assert loaded.object_types["salary"] == ["a free-text salary token", 999], (
        "the gate invented a primitive check for an unresolvable type; resolve-or-"
        "skip requires it to accept any interchange scalar (C10)."
    )


# --------------------------------------------------------------------------- #
# 2. schema rejection
# --------------------------------------------------------------------------- #


def test_schema_rejects_extra_top_level_property(tmp_path: Path) -> None:
    model = load_model(RING)
    payload = _valid_payload(model)
    payload["surprise"] = {"not": "allowed"}
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("schema" in f for f in exc.value.failures)


def test_schema_rejects_wrong_type_for_identifier_list(tmp_path: Path) -> None:
    model = load_model(RING)
    payload = _valid_payload(model)
    payload["object_types"]["node"] = "not-an-array"
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("schema" in f for f in exc.value.failures)


def test_schema_rejects_unknown_provenance_property(tmp_path: Path) -> None:
    model = load_model(RING)
    payload = _valid_payload(model)
    payload["provenance"]["forged_field"] = "nope"
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("schema" in f for f in exc.value.failures)


def test_schema_rejects_missing_required_section(tmp_path: Path) -> None:
    model = load_model(RING)
    payload = _valid_payload(model)
    del payload["value_types"]
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("schema" in f for f in exc.value.failures)


# --------------------------------------------------------------------------- #
# 3. coherence rejection — the FULL enumerated list, never the first
# --------------------------------------------------------------------------- #


def test_three_seeded_defects_produce_three_enumerated_failures(tmp_path: Path) -> None:
    """A pool with three coherence defects is rejected whole, with all three
    named — a truncated list would starve a proposer's repair loop."""
    model = load_model(FULL_VOCAB)
    payload = _valid_payload(model)

    # Defect 1: an out-of-enum sample for gender (allowed M/F/X).
    payload["value_types"]["gender"] = ["M", "Z"]
    # Defect 2: an under-sized identifier list for employee (uniqueness demands 2).
    payload["object_types"]["employee"] = [1]
    # Defect 3: a missing object type — drop salary entirely.
    del payload["object_types"]["salary"]

    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)

    failures = exc.value.failures
    assert len(failures) == 3, f"expected 3 enumerated failures, got {failures}"
    blob = "\n".join(failures)
    assert "gender" in blob and "enum" in blob
    assert "employee" in blob and "distinct" in blob
    assert "salary" in blob and "no entry" in blob


def test_out_of_range_sample_is_rejected(tmp_path: Path) -> None:
    model = load_model(FULL_VOCAB)
    payload = _valid_payload(model)
    payload["value_types"]["hours"] = [500, 5000]  # 5000 > declared max 1000
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("hours" in f and "range" in f for f in exc.value.failures)


@pytest.mark.parametrize(
    ("allowed", "candidate", "accepted"),
    [
        (True, 1, False),
        (1, True, False),
        (False, 0, False),
        (0, False, False),
        (1, 1.0, True),
        (1.0, 1, True),
    ],
)
def test_pool_enum_coherence_uses_normative_scalar_identity(
    tmp_path: Path, allowed: object, candidate: object, accepted: bool
) -> None:
    model = Model(
        version=1,
        object_types=[{"id": "opaque", "kind": "entity", "reference": {"mode": "external"}}],
        fact_types=[],
        constraints=[
            {"type": "value", "scope": "object", "object_type": "opaque", "allowed": [allowed]}
        ],
    )
    payload = {
        "object_types": {"opaque": [candidate]},
        "value_types": {},
        "provenance": {"source": "llm-proposed"},
    }

    if accepted:
        load_pool(_write(tmp_path, payload), model)
    else:
        with pytest.raises(PoolValidationError, match="allowed enum"):
            load_pool(_write(tmp_path, payload), model)


def test_pool_numeric_renderings_count_as_one_distinct_identifier():
    from gnd.synth.poolfile import _distinct_count

    assert _distinct_count([1, 1.0]) == 1
    assert _distinct_count([True, 1]) == 2
    assert _distinct_count([False, 0]) == 2


def _constrained_number_model(*constraints: dict) -> Model:
    return Model(
        version=1,
        object_types=[{"id": "number", "kind": "value", "primitive": "Number"}],
        fact_types=[],
        constraints=[
            {
                "type": "value",
                "object_type": "number",
                "modality": "alethic",
                **constraint,
            }
            for constraint in constraints
        ],
    )


def test_pool_applies_all_object_value_constraints_conjunctively(tmp_path: Path) -> None:
    model = _constrained_number_model(
        {"allowed": [1, 2]},
        {"allowed": [2, 3]},
    )
    payload = {
        "object_types": {},
        "value_types": {"number": [1]},
        "provenance": {"source": "llm-proposed"},
    }

    with pytest.raises(PoolValidationError, match="allowed enum"):
        load_pool(_write(tmp_path, payload), model)

    payload["value_types"]["number"] = [2]
    assert load_pool(_write(tmp_path, payload), model).value_types["number"] == [2]


def test_pool_treats_plural_ranges_as_a_union_inside_one_constraint(
    tmp_path: Path,
) -> None:
    model = _constrained_number_model(
        {"ranges": [{"min": -10, "max": -5}, {"min": 5, "max": 10}]}
    )
    payload = {
        "object_types": {},
        "value_types": {"number": [-7, 7]},
        "provenance": {"source": "llm-proposed"},
    }
    assert load_pool(_write(tmp_path, payload), model).value_types["number"] == [-7, 7]

    payload["value_types"]["number"] = [0]
    with pytest.raises(PoolValidationError, match="range domain"):
        load_pool(_write(tmp_path, payload), model)


def test_pool_builder_detects_an_empty_constraint_intersection() -> None:
    model = _constrained_number_model({"allowed": [1]}, {"allowed": [2]})

    with pytest.raises(PoolValidationError, match="empty intersection"):
        build_faker_pool(model, 7)


@pytest.mark.parametrize("bucket", ["object_types", "value_types"])
@pytest.mark.parametrize(
    "non_finite",
    [float("nan"), float("inf"), float("-inf")],
    ids=("nan", "positive-infinity", "negative-infinity"),
)
def test_load_pool_rejects_non_finite_values_in_every_bucket(
    tmp_path: Path, bucket: str, non_finite: float
) -> None:
    model = load_model(FULL_VOCAB)
    payload = _valid_payload(model)
    key = "salary" if bucket == "object_types" else next(iter(payload[bucket]))
    payload[bucket][key] = [non_finite]

    with pytest.raises(PoolValidationError, match="non-finite"):
        load_pool(_write(tmp_path, payload), model)


@pytest.mark.parametrize("bucket", ["object_types", "value_types"])
@pytest.mark.parametrize(
    "non_finite",
    [float("nan"), float("inf"), float("-inf")],
    ids=("nan", "positive-infinity", "negative-infinity"),
)
def test_pool_writers_refuse_non_finite_values(
    tmp_path: Path, bucket: str, non_finite: float
) -> None:
    from gnd.synth.poolfile import _canonical_bytes

    model = load_model(FULL_VOCAB)
    payload = _valid_payload(model)
    key = "salary" if bucket == "object_types" else next(iter(payload[bucket]))
    payload[bucket][key] = [non_finite]
    pool = Pool(
        object_types=payload["object_types"],
        value_types=payload["value_types"],
        provenance=payload["provenance"],
        sha256="not-written",
    )
    destination = tmp_path / f"{bucket}.pool.json"

    with pytest.raises(PoolValidationError, match="non-finite"):
        _canonical_bytes(payload)
    with pytest.raises(PoolValidationError, match="non-finite"):
        write_pool(pool, destination)
    assert not destination.exists()


def _entity(oid: str, value_type: str) -> dict:
    return {"id": oid, "kind": "entity", "reference": {"mode": "popular", "value_type": value_type}}


def _value(oid: str, primitive: str) -> dict:
    return {"id": oid, "kind": "value", "primitive": primitive}


def test_frequency_min_demand_is_computed_and_named(tmp_path: Path) -> None:
    """A frequency {min: 3} places a distinctness demand of 3; an under-sized list
    is rejected with that specific demand named."""
    model = Model(
        version=1,
        object_types=[_entity("w", "wid"), _value("wid", "Integer"), _value("x", "String")],
        fact_types=[
            {
                "id": "ft",
                "reading": "{W} has {X}",
                "roles": [
                    {"object_type": "w", "role_name": "wr"},
                    {"object_type": "x", "role_name": "xr"},
                ],
                "constraints": [
                    {"type": "frequency", "scope": "internal", "roles": ["wr"], "bound": {"min": 3}}
                ],
            }
        ],
    )
    payload = {
        "object_types": {"w": [1, 2]},  # 2 distinct < 3
        "value_types": {"wid": [1], "x": ["a"]},
        "provenance": {"source": "llm-proposed"},
    }
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("'w'" in f and "frequency {min: 3}" in f for f in exc.value.failures), (
        exc.value.failures
    )


def test_cardinality_min_demand_is_computed_and_named(tmp_path: Path) -> None:
    model = Model(
        version=1,
        object_types=[_entity("d", "did"), _value("did", "String"), _value("x", "String")],
        fact_types=[
            {
                "id": "ft",
                "reading": "{D} has {X}",
                "roles": [
                    {"object_type": "d", "role_name": "dr"},
                    {"object_type": "x", "role_name": "xr"},
                ],
            }
        ],
        constraints=[
            {"type": "cardinality", "scope": "object", "object_type": "d", "bound": {"min": 3}}
        ],
    )
    payload = {
        "object_types": {"d": ["only-one"]},  # 1 distinct < 3
        "value_types": {"did": ["k"], "x": ["a"]},
        "provenance": {"source": "faker"},
    }
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("'d'" in f and "cardinality {min: 3}" in f for f in exc.value.failures), (
        exc.value.failures
    )


def _enum_identifier_demand_model() -> Model:
    return Model(
        version=1,
        object_types=[_entity("item", "item_id"), _value("item_id", "String")],
        fact_types=[],
        constraints=[
            {
                "type": "value",
                "object_type": "item_id",
                "allowed": ["only"],
                "modality": "alethic",
            },
            {
                "type": "cardinality",
                "scope": "object",
                "object_type": "item",
                "bound": {"min": 2},
                "modality": "alethic",
            },
        ],
    )


def test_enum_identifier_domain_smaller_than_demand_is_rejected_clearly() -> None:
    model = _enum_identifier_demand_model()
    with pytest.raises(PoolValidationError, match="declared domain cannot satisfy") as exc:
        build_faker_pool(model, 7, size_per_type=1)

    assert "only 1 distinct identifier" in str(exc.value)
    assert "requires 2" in str(exc.value)


def test_enum_identifier_domain_may_cap_the_optional_pool_size_target() -> None:
    model = Model(
        version=1,
        object_types=[_entity("item", "item_id"), _value("item_id", "String")],
        fact_types=[
            {
                "id": "item_exists",
                "roles": [{"object_type": "item", "role_name": "item"}],
            }
        ],
        constraints=[
            {
                "type": "value",
                "object_type": "item_id",
                "allowed": ["first", "second"],
                "modality": "alethic",
            }
        ],
    )

    pool = build_faker_pool(model, 7)

    assert pool.object_types["item"] == ["first", "second"]


def test_builder_runs_final_coherence_gate_even_if_a_draw_helper_drifts(monkeypatch) -> None:
    from gnd.synth import poolfile as poolfile_module

    model = _enum_identifier_demand_model()
    monkeypatch.setattr(
        poolfile_module,
        "_distinct_identifiers",
        lambda *_args, **_kwargs: ["only"],
    )

    with pytest.raises(PoolValidationError, match="needs >= 2"):
        build_faker_pool(model, 7, size_per_type=1)


def test_cli_reports_enum_identifier_demand_as_generator_error(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    model = _enum_identifier_demand_model()
    monkeypatch.setattr("gnd.synth.service.load_model", lambda _path: model)

    code = main(
        [
            "synth",
            "enum-demand.orm.yaml",
            "--out",
            str(tmp_path / "out"),
            "--format",
            "json",
        ]
    )

    assert code == 5
    payload = json.loads(capsys.readouterr().out)
    assert payload["exit_code"] == 5
    assert "declared domain cannot satisfy" in payload["error"]


def test_join_recurrence_demand_rejects_an_all_distinct_join_type(tmp_path: Path) -> None:
    """A type used in a join-scoped constraint but with too few identifiers to
    recur across the joined fact types is rejected with the join reason named —
    the coarse degeneracy the pool gate catches ahead of plan 03's empirical
    backstop. Here `j` has NO uniqueness of its own, so the demand of 2 comes
    purely from join recurrence."""
    model = Model(
        version=1,
        object_types=[
            _entity("j", "jid"),
            _value("jid", "Integer"),
            _value("x", "String"),
            _value("y", "String"),
        ],
        fact_types=[
            {
                "id": "ft1",
                "reading": "{J} one {X}",
                "roles": [
                    {"object_type": "j", "role_name": "jr"},
                    {"object_type": "x", "role_name": "xr"},
                ],
            },
            {
                "id": "ft2",
                "reading": "{J} two {Y}",
                "roles": [
                    {"object_type": "j", "role_name": "jr2"},
                    {"object_type": "y", "role_name": "yr"},
                ],
            },
        ],
        constraints=[
            {
                "type": "subset",
                "subset_role_seq": [{"fact_type": "ft1", "role": "jr"}],
                "superset_role_seq": [{"fact_type": "ft2", "role": "jr2"}],
            }
        ],
    )
    # Confirm the demand really comes from join recurrence, not uniqueness.
    assert "j" in _join_key_types(model)
    assert _distinctness_demand(model)["j"] == (2, "join recurrence")

    payload = {
        "object_types": {"j": [1]},  # 1 distinct < 2
        "value_types": {"jid": [1], "x": ["a"], "y": ["b"]},
        "provenance": {"source": "faker"},
    }
    with pytest.raises(PoolValidationError) as exc:
        load_pool(_write(tmp_path, payload), model)
    assert any("'j'" in f and "join recurrence" in f for f in exc.value.failures), (
        exc.value.failures
    )


# --------------------------------------------------------------------------- #
# 4. the seam is shape-identical in both directions
# --------------------------------------------------------------------------- #


def test_a_hand_written_llm_proposed_pool_passes_the_same_gate(tmp_path: Path) -> None:
    """A hand-written pool standing in for an LLM-composed one, with valid content
    and provenance.source: llm-proposed, passes the identical gate a Faker pool
    does — the seam is proven shape-identical in both directions (D-17′)."""
    model = load_model(FULL_VOCAB)
    payload = _valid_payload(model)
    payload["provenance"] = {"source": "llm-proposed", "proposer_model": "some-model"}
    payload["domain_narrative"] = "A small engineering firm with a handful of projects."

    loaded = load_pool(_write(tmp_path, payload), model)
    assert loaded.provenance["source"] == "llm-proposed"
    assert loaded.domain_narrative is not None


# --------------------------------------------------------------------------- #
# 5. content addressing
# --------------------------------------------------------------------------- #


def test_sha256_is_stable_across_key_ordering_and_round_trips(tmp_path: Path) -> None:
    model = load_model(SETFAM)
    pool = build_faker_pool(model, 77)

    # Write, load: the hash survives serialisation.
    path = tmp_path / "a.pool.json"
    write_pool(pool, path)
    reloaded = load_pool(path, model)
    assert reloaded.sha256 == pool.sha256

    # A byte-different file with the SAME logical content (keys reordered, compact
    # vs pretty) must hash identically — the hash is over canonical bytes.
    payload = _valid_payload(model, seed=77)
    reordered = {
        "provenance": payload["provenance"],
        "value_types": payload["value_types"],
        "object_types": payload["object_types"],
    }
    other = tmp_path / "b.pool.json"
    other.write_text(json.dumps(reordered, indent=4), encoding="utf-8")
    assert load_pool(other, model).sha256 == pool.sha256, (
        "two byte-different encodings of the same logical pool hashed differently — "
        "the content address is not canonical."
    )


def test_builder_is_deterministic_from_a_seed_across_processes() -> None:
    program = (
        "from gnd.model import load_model; from gnd.synth.poolfile import build_faker_pool;"
        f"print(build_faker_pool(load_model({str(FULL_VOCAB)!r}), 314159).sha256)"
    )
    first = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True)
    second = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True)
    assert first.stdout.strip() and first.stdout == second.stdout, (
        f"the builder is not deterministic across processes:\n{first.stdout}\n{second.stdout}"
    )


# --------------------------------------------------------------------------- #
# 6. no provider client in src/gnd/ (D-20)
# --------------------------------------------------------------------------- #


def test_no_provider_module_is_imported_anywhere_in_src_gnd() -> None:
    """D-20: the pool proposer ships as a SKILL, not an embedded API client. No
    provider SDK may be imported anywhere under src/gnd/ — asserted by a source
    scan inherited by plan 04's measure-side test."""
    provider_import = re.compile(
        r"^\s*(?:import|from)\s+(anthropic|openai|google\.generativeai|genai|cohere|"
        r"mistralai|ollama|litellm|instructor)\b",
        re.MULTILINE,
    )
    offenders: list[str] = []
    for path in SRC_GND.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if provider_import.search(text):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, (
        f"a provider SDK is imported under src/gnd/: {offenders}. The proposer is a "
        "skill (D-20) — no API client, key, or network belongs in the package."
    )


def test_pool_is_frozen() -> None:
    """The loaded artifact is immutable — its identity is its hash."""
    model = load_model(RING)
    pool = build_faker_pool(model, 1)
    assert isinstance(pool, Pool)
    with pytest.raises((AttributeError, TypeError)):
        pool.sha256 = "tampered"  # type: ignore[misc]
