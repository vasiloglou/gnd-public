"""Conformance, range/enum honouring, determinism, and the lazy-import guard.

Every value assertion here calls ``gnd.popvalidate``'s OWN predicate rather than
re-expressing it: the generator is measured against the loader's notion of
validity, never a second copy that could drift (D-01). The range test states the
refuted Polyfactory baseline as a number so "in range" is proven, not assumed.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import tomllib
from pathlib import Path
from random import Random

import pytest

from gnd import popvalidate
from gnd.model import Model
from gnd.synth.poolfile import build_faker_pool
from gnd.synth.value_domain import intersected_ranges, value_satisfies_all
from gnd.synth.values import PRIMITIVES, make_value

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"

#: Draws per primitive. 200 is enough that a branch which is right on average but
#: occasionally emits a loader-invalid value (a 3-digit year, a hand-formatted
#: date) is caught, without turning the fast lane slow.
DRAWS = 200


def test_primitives_match_the_loader_predicate_table() -> None:
    """PRIMITIVES is derived from the meta-schema, so it must cover exactly the
    predicate table ``popvalidate`` dispatches on — no more, no less. A new
    primitive added to the model layer without a generator branch fails here."""
    assert set(PRIMITIVES) == set(popvalidate._PRIMITIVE_PREDICATES), (
        f"PRIMITIVES {sorted(PRIMITIVES)} and the loader's predicate table "
        f"{sorted(popvalidate._PRIMITIVE_PREDICATES)} disagree. Both derive from "
        "the meta-schema's `primitive` enum; a divergence means one was edited by "
        "hand."
    )


@pytest.mark.parametrize("primitive", PRIMITIVES)
def test_every_draw_satisfies_the_loader_predicate(primitive: str) -> None:
    """Per-primitive conformance: 200 draws, each satisfying the loader's OWN
    predicate for that primitive. The ``2026-2-3`` failure mode is precisely a
    value that looks fine and fails the loader's anchored check — so the loader's
    predicate is called, not restated."""
    predicate = popvalidate._PRIMITIVE_PREDICATES[primitive]
    rng = Random(f"conformance-{primitive}")
    failures = []
    for _ in range(DRAWS):
        value = make_value(primitive, rng)
        if not predicate(value):
            failures.append(value)
    assert not failures, (
        f"{primitive}: {len(failures)} of {DRAWS} draws failed "
        f"popvalidate._is_* — e.g. {failures[:3]!r}. A generated value the loader "
        "rejects is exactly the silent generator bug D-01 forbids."
    )


def test_integer_range_is_honoured_beating_the_polyfactory_baseline() -> None:
    """Reproduce the Polyfactory probe as a comparison.

    MEASURED REFUTED BASELINE (D-17): polyfactory 3.3.0 drew **0 of 8** ages
    inside the model's declared ``18..65`` range. GND's dispatch must beat that —
    at 8 draws and at 200. The range is inclusive on both ends here.
    """
    value_range = {"min": 18, "max": 65, "min_inclusive": True, "max_inclusive": True}

    rng8 = Random("age-8")
    first_eight = [make_value("Integer", rng8, value_range=value_range) for _ in range(8)]
    in_range_8 = sum(1 for v in first_eight if 18 <= v <= 65)
    assert in_range_8 == 8, (
        f"GND drew {in_range_8}/8 inside 18..65; the refuted polyfactory baseline "
        f"was 0/8 and GND must beat it. Draws: {first_eight}"
    )

    rng200 = Random("age-200")
    in_range_200 = sum(
        1
        for _ in range(DRAWS)
        if 18 <= make_value("Integer", rng200, value_range=value_range) <= 65
    )
    assert in_range_200 == DRAWS, (
        f"GND drew {in_range_200}/{DRAWS} inside 18..65 — every draw must land "
        "inside a declared range (the property Polyfactory failed)."
    )


def test_integer_exclusive_bounds_in_both_directions() -> None:
    """An exclusive minimum makes the bound itself an invalid draw, and likewise
    for an exclusive maximum — the flags are read, never assumed."""
    rng = Random("exclusive-int")
    # Exclusive min: values must be strictly > 10, i.e. >= 11.
    excl_min = {"min": 10, "max": 20, "min_inclusive": False, "max_inclusive": True}
    for _ in range(DRAWS):
        v = make_value("Integer", rng, value_range=excl_min)
        assert 10 < v <= 20, f"exclusive-min draw {v} violated (10, 20]"
    # Exclusive max: values must be strictly < 20, i.e. <= 19.
    excl_max = {"min": 10, "max": 20, "min_inclusive": True, "max_inclusive": False}
    for _ in range(DRAWS):
        v = make_value("Integer", rng, value_range=excl_max)
        assert 10 <= v < 20, f"exclusive-max draw {v} violated [10, 20)"


def test_float_range_and_exclusive_bounds() -> None:
    rng = Random("float-range")
    incl = {"min": 0.0, "max": 1.0, "min_inclusive": True, "max_inclusive": True}
    for _ in range(DRAWS):
        v = make_value("Float", rng, value_range=incl)
        assert 0.0 <= v <= 1.0 and popvalidate._is_number(v)
    excl = {"min": 0.0, "max": 1.0, "min_inclusive": False, "max_inclusive": False}
    for _ in range(DRAWS):
        v = make_value("Number", rng, value_range=excl)
        assert 0.0 < v < 1.0, f"exclusive float draw {v} touched a forbidden bound"


@pytest.mark.parametrize("seed", range(20))
def test_adjacent_large_float_excludes_lower_endpoint_exactly(seed: int) -> None:
    low = 1e308
    high = math.nextafter(low, math.inf)
    value = make_value(
        "Float",
        Random(seed),
        value_range={
            "min": low,
            "max": high,
            "min_inclusive": False,
            "max_inclusive": True,
        },
    )
    assert value == high


@pytest.mark.parametrize("seed", range(20))
def test_adjacent_negative_float_excludes_upper_endpoint_exactly(seed: int) -> None:
    high = -1e308
    low = math.nextafter(high, -math.inf)
    value = make_value(
        "Number",
        Random(seed),
        value_range={
            "min": low,
            "max": high,
            "min_inclusive": True,
            "max_inclusive": False,
        },
    )
    assert value == low


def test_open_float_extremes_keep_inclusive_member_and_reject_exclusive_side() -> None:
    maximum = float.fromhex("0x1.fffffffffffffp+1023")
    minimum = -maximum
    assert make_value("Float", Random(1), value_range={"min": maximum}) == maximum
    assert make_value("Float", Random(1), value_range={"max": minimum}) == minimum
    with pytest.raises(ValueError, match="empty numeric range"):
        make_value(
            "Float",
            Random(1),
            value_range={"min": maximum, "min_inclusive": False},
        )
    with pytest.raises(ValueError, match="empty numeric range"):
        make_value(
            "Float",
            Random(1),
            value_range={"max": minimum, "max_inclusive": False},
        )


def test_both_exclusive_adjacent_floats_have_no_representable_member() -> None:
    low = 1e308
    high = math.nextafter(low, math.inf)
    with pytest.raises(ValueError, match="empty numeric range"):
        make_value(
            "Float",
            Random(1),
            value_range={
                "min": low,
                "max": high,
                "min_inclusive": False,
                "max_inclusive": False,
            },
        )


def test_enum_is_honoured() -> None:
    """Every draw under ``allowed`` is a member — the second per-instance property
    an LLM (or Faker) can hold and the pool carries."""
    allowed = ["M", "F", "X"]
    rng = Random("enum")
    for _ in range(DRAWS):
        assert make_value("String", rng, allowed=allowed) in allowed


NON_NUMERIC_RANGE_CASES = [
    pytest.param(
        "String",
        "single-point",
        [{"range": {"min": "mid", "max": "mid"}}],
        id="string-single-point",
    ),
    pytest.param(
        "String",
        "exclusive",
        [
            {
                "range": {
                    "min": "alpha",
                    "max": "omega",
                    "min_inclusive": False,
                    "max_inclusive": False,
                }
            }
        ],
        id="string-exclusive",
    ),
    pytest.param(
        "String",
        "out-of-default-anchor",
        [{"range": {"min": "zzzz-2030", "max": "zzzz-2040"}}],
        id="string-out-of-default-anchor",
    ),
    pytest.param(
        "String",
        "intersected",
        [{"range": {"min": "alpha", "max": "middle"}}, {"range": {"min": "gamma", "max": "omega"}}],
        id="string-intersected",
    ),
    pytest.param(
        "Binary",
        "single-point",
        [{"range": {"min": "TQ==", "max": "TQ=="}}],
        id="binary-single-point",
    ),
    pytest.param(
        "Binary",
        "exclusive",
        [{"range": {"min": "AA==", "max": "zz==", "min_inclusive": False, "max_inclusive": False}}],
        id="binary-exclusive",
    ),
    pytest.param(
        "Binary",
        "out-of-default-anchor",
        [{"range": {"min": "zzzz-2030", "max": "zzzz-2040"}}],
        id="binary-out-of-default-anchor",
    ),
    pytest.param(
        "Binary",
        "intersected",
        [{"range": {"min": "AA==", "max": "mm=="}}, {"range": {"min": "GG==", "max": "zz=="}}],
        id="binary-intersected",
    ),
    pytest.param(
        "Date",
        "single-point",
        [{"range": {"min": "2035-06-15", "max": "2035-06-15"}}],
        id="date-single-point",
    ),
    pytest.param(
        "Date",
        "exclusive",
        [
            {
                "range": {
                    "min": "2035-06-14",
                    "max": "2035-06-16",
                    "min_inclusive": False,
                    "max_inclusive": False,
                }
            }
        ],
        id="date-exclusive",
    ),
    pytest.param(
        "Date",
        "out-of-default-anchor",
        [{"range": {"min": "2030-01-01", "max": "2030-12-31"}}],
        id="date-out-of-default-anchor",
    ),
    pytest.param(
        "Date",
        "intersected",
        [
            {"range": {"min": "2030-01-01", "max": "2039-12-31"}},
            {"range": {"min": "2035-01-01", "max": "2040-12-31"}},
        ],
        id="date-intersected",
    ),
    pytest.param(
        "DateTime",
        "single-point",
        [{"range": {"min": "2035-06-15T12:30:00", "max": "2035-06-15T12:30:00"}}],
        id="datetime-single-point",
    ),
    pytest.param(
        "DateTime",
        "exclusive",
        [
            {
                "range": {
                    "min": "2035-06-15T12:29:59",
                    "max": "2035-06-15T12:30:01",
                    "min_inclusive": False,
                    "max_inclusive": False,
                }
            }
        ],
        id="datetime-exclusive",
    ),
    pytest.param(
        "DateTime",
        "out-of-default-anchor",
        [{"range": {"min": "2030-01-01T00:00:00", "max": "2030-12-31T23:59:59"}}],
        id="datetime-out-of-default-anchor",
    ),
    pytest.param(
        "DateTime",
        "intersected",
        [
            {"range": {"min": "2030-01-01T00:00:00", "max": "2039-12-31T23:59:59"}},
            {"range": {"min": "2035-01-01T00:00:00", "max": "2040-12-31T23:59:59"}},
        ],
        id="datetime-intersected",
    ),
]


@pytest.mark.parametrize("primitive,scenario,constraints", NON_NUMERIC_RANGE_CASES)
def test_make_value_honours_every_non_numeric_range_shape(
    primitive: str, scenario: str, constraints: list[dict]
) -> None:
    value_range = intersected_ranges(constraints)[0]
    values = [
        make_value(primitive, Random(f"{primitive}-{scenario}-{i}"), value_range=value_range)
        for i in range(16)
    ]

    assert all(popvalidate._PRIMITIVE_PREDICATES[primitive](value) for value in values)
    assert all(value_satisfies_all(value, constraints) for value in values)


@pytest.mark.parametrize("primitive,scenario,constraints", NON_NUMERIC_RANGE_CASES)
def test_faker_pool_honours_every_non_numeric_range_shape(
    primitive: str, scenario: str, constraints: list[dict]
) -> None:
    model = Model(
        version=1,
        object_types=[{"id": "sample", "kind": "value", "primitive": primitive}],
        fact_types=[],
        constraints=[
            {
                "type": "value",
                "object_type": "sample",
                "modality": "alethic",
                **constraint,
            }
            for constraint in constraints
        ],
    )

    values = build_faker_pool(model, 812, size_per_type=8).value_types["sample"]

    assert len(values) == 8
    assert all(popvalidate._PRIMITIVE_PREDICATES[primitive](value) for value in values)
    assert all(value_satisfies_all(value, constraints) for value in values)


def test_same_seed_is_byte_identical_across_processes() -> None:
    """In-process re-seeding can hide global-state leakage; a second process
    cannot. Two subprocesses with the same seed must print identical output."""
    program = (
        "import json; from random import Random; from gnd.synth.values import make_value, PRIMITIVES;"
        "rng = Random(20260812);"
        "print(json.dumps([make_value(p, rng) for p in PRIMITIVES for _ in range(5)]))"
    )
    first = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, check=True
    )
    second = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, check=True
    )
    assert first.stdout == second.stdout, (
        "two processes with the same seed produced different output — a stream is "
        "not threaded from the single rng, so no rate over this generator could be "
        f"reproduced.\nfirst:\n{first.stdout}\nsecond:\n{second.stdout}"
    )
    assert first.stdout.strip(), "the determinism probe produced no output"


def test_faker_absence_is_a_clean_domain_error_not_an_importerror() -> None:
    """Lazy-import guard, in a CLEAN subprocess with faker blocked in sys.modules.

    Proves three things at once: ``import gnd.synth`` succeeds without the extra;
    ``make_value`` on a faker-backed primitive raises ``SynthDependencyError``
    carrying the remediation string (never a bare ``ImportError``); and the
    ``gnd check`` path is entirely unaffected by faker's absence — it loads a
    model and population and reaches a verdict band.
    """
    model = REPO_ROOT / "tests" / "fixtures" / "checker" / "ring.orm.yaml"
    population = REPO_ROOT / "tests" / "fixtures" / "checker" / "population.ring_pass.yaml"
    program = f"""
import sys, json
sys.modules['faker'] = None  # simulate the extra being absent
import gnd.synth  # must not explode
from gnd.synth.values import make_value, SynthDependencyError
from random import Random
result = {{}}
try:
    make_value('String', Random(0))
    result['make_value'] = 'NO-ERROR'
except SynthDependencyError as exc:
    result['make_value'] = 'SynthDependencyError'
    result['message'] = str(exc)
except ImportError:
    result['make_value'] = 'BARE-IMPORTERROR'
from gnd.model import load_model
from gnd.population import load_population
from gnd import checker
m = load_model({str(model)!r})
p = load_population({str(population)!r}, model=m)
result['band'] = checker.band(checker.check(m, p))
print(json.dumps(result))
"""
    proc = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0, f"probe crashed:\n{proc.stdout}\n{proc.stderr}"
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert payload["make_value"] == "SynthDependencyError", (
        f"with faker absent, make_value returned {payload}; it must raise "
        "SynthDependencyError, never a bare ImportError."
    )
    assert "synth" in payload["message"] and "install" in payload["message"].lower(), (
        f"the error must carry the install remediation; got {payload['message']!r}"
    )
    assert payload["band"] == 0, (
        f"`gnd check` on a conforming population reached band {payload['band']} "
        "with faker absent — the check path must be unaffected by the extra (D-18)."
    )


def test_no_refuted_synthetic_dependency_is_declared() -> None:
    """polyfactory and hypothesis must appear in NO dependency list.

    D-17 dropped Polyfactory ON MEASUREMENT — 0/8 ages in a declared 18..65
    range, and 8/8 distinct entities forcing zero-row joins across the F-05 join
    frontier — and deferred Hypothesis. Neither may re-enter through the base
    set, the synth extra, or the dev group.
    """
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    project = data["project"]
    lists: list[str] = list(project.get("dependencies", []))
    for extra_deps in project.get("optional-dependencies", {}).values():
        lists.extend(extra_deps)
    for group_deps in data.get("dependency-groups", {}).values():
        lists.extend(group_deps)
    lowered = " ".join(lists).lower()
    assert "polyfactory" not in lowered, "polyfactory is refuted by measurement (D-17)"
    assert "hypothesis" not in lowered, "hypothesis is deferred, not adopted (D-17)"
