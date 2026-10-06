"""Seeded primitive -> value dispatch that cannot emit loader-invalid data.

Every value this module produces is, by construction and by test
(``tests/test_synth_values.py``), a value the population loader accepts: each
branch is measured against ``gnd.popvalidate``'s OWN ``_is_*`` predicate for its
primitive, never against a second, drift-prone notion of validity. That is the
whole point of the layer — a generator that can silently emit data the loader
rejects would poison every downstream measurement (D-01).

Two properties refuted Polyfactory on measurement (D-17): it drew 0 of 8 ages
inside a declared ``18..65`` range, and 8 of 8 distinct entity values, forcing
zero-row joins. This module makes range- and enum-honouring a *measured* property
of GND's own dispatch (see the range test's stated 0-of-8 baseline).

``faker`` is imported LAZILY, inside :func:`make_value`, so importing
``gnd.synth`` on a machine without the ``synth`` extra does not explode and
``gnd check`` is unaffected. Its absence raises :class:`SynthDependencyError`
with a remediation string — never a bare ``ImportError`` traceback (modelled on
01.2's lifecycle-code discipline).
"""

from __future__ import annotations

import base64
import json  # noqa: F401 -- historical compatibility binding
import math
from datetime import date, datetime, timedelta
from importlib.resources import files
from random import Random
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import popvalidate

__all__ = ["PRIMITIVES", "SynthDependencyError", "make_value"]

#: Fixed absolute anchors for Date/DateTime generation. Deliberately NOT
#: "today"/"now": a wall-clock reference makes generation depend on when it runs,
#: which breaks the byte-for-byte reproducibility a measured rate rests on (D-07).
#: Naive (tz-free) on purpose — the ORM ``Date``/``DateTime`` primitives are
#: rendered as offset-free ISO-8601, matching ``popvalidate._is_datetime``.
_DATE_ANCHOR_START = date(1990, 1, 1)
_DATE_ANCHOR_END = date(2020, 12, 31)
_DATETIME_ANCHOR_START = datetime(1990, 1, 1, 0, 0, 0)  # noqa: DTZ001
_DATETIME_ANCHOR_END = datetime(2020, 12, 31, 23, 59, 59)  # noqa: DTZ001


class SynthDependencyError(RuntimeError):
    """The optional ``synth`` extra (faker) is required but absent.

    Carries the exact remediation string rather than letting an ``ImportError``
    traceback escape and be mapped to an internal-error exit band.
    """

    REMEDIATION = (
        "the synthetic-value generator needs the optional 'synth' extra. "
        "Install it with `pip install get-nick-done[synth]`, or "
        "`uv sync --extra synth` in a checkout."
    )

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.REMEDIATION)


def _load_primitives() -> tuple[str, ...]:
    """The primitive names the meta-schema allows — derived, never re-typed.

    A hand-copied list is how a newly added primitive becomes silently
    ungenerable (and how the generator and the loader would drift). Reading the
    enum from the vendored meta-schema keeps this in lockstep with
    ``popvalidate._PRIMITIVE_PREDICATES`` by construction.
    """
    schema_text = files("gnd").joinpath("schema/orm-meta.schema.json").read_text(encoding="utf-8")
    schema = _rf7_input.loads(schema_text)
    enum = schema["$defs"]["object_type"]["properties"]["primitive"]["enum"]
    return tuple(enum)


#: The meta-schema's ``primitive`` enum, in declaration order. Derived from the
#: schema itself so a new primitive cannot be added to the model layer without
#: this generator noticing (the conformance test iterates this tuple).
PRIMITIVES: tuple[str, ...] = _load_primitives()


def _require_faker() -> Any:
    """Import faker lazily, translating its absence into a clean domain error."""
    try:
        from faker import Faker
    except ImportError as exc:  # pragma: no cover - exercised via sys.modules block
        raise SynthDependencyError() from exc
    return Faker


def _seeded_faker(rng: Random) -> Any:
    """A faker instance seeded FROM ``rng`` (D-07: one seed threads the whole
    generator). Seeding faker from a second independent seed would let two
    streams interleave differently across runs; drawing the seed from ``rng``
    advances the same stream every other numeric draw uses."""
    Faker = _require_faker()
    fake = Faker()
    fake.seed_instance(rng.getrandbits(64))
    return fake


def _int_bounds(value_range: dict[str, Any]) -> tuple[int, int]:
    """Inclusive integer ``(low, high)`` honouring the four range flags.

    An exclusive bound makes the bound itself an invalid draw, so it is stepped
    inward by one — read the flags, never assume inclusivity (the property whose
    absence sat under Polyfactory's 0-of-8 failure)."""
    lo = value_range.get("min")
    hi = value_range.get("max")
    low = int(lo) if lo is not None else 0
    high = int(hi) if hi is not None else low + 1_000_000
    if lo is not None and value_range.get("min_inclusive", True) is False:
        low += 1
    if hi is not None and value_range.get("max_inclusive", True) is False:
        high -= 1
    if low > high:
        raise ValueError(f"empty integer range after applying inclusivity flags: {value_range!r}")
    return low, high


def _float_bounds(value_range: dict[str, Any]) -> tuple[float, float]:
    """Closed finite sampling bounds for a declared floating-point range.

    An exclusive endpoint is replaced by its adjacent representable float. This
    is exact at every magnitude; a scaled epsilon can round back to the excluded
    endpoint. Open ends use the adjacent finite value on the declared side so an
    extreme inclusive singleton stays representable while an exclusive extreme
    is rejected.
    """
    lo = value_range.get("min")
    hi = value_range.get("max")
    if lo is None and hi is None:
        low, high = 0.0, 1_000_000.0
    elif lo is None:
        high = float(hi)
        low = math.nextafter(high, -math.inf)
        if not math.isfinite(low):
            low = high
    elif hi is None:
        low = float(lo)
        high = math.nextafter(low, math.inf)
        if not math.isfinite(high):
            high = low
    else:
        low, high = float(lo), float(hi)

    if not math.isfinite(low) or not math.isfinite(high):
        raise ValueError(f"numeric range has no finite sampling interval: {value_range!r}")
    if lo is not None and value_range.get("min_inclusive", True) is False:
        low = math.nextafter(low, math.inf)
    if hi is not None and value_range.get("max_inclusive", True) is False:
        high = math.nextafter(high, -math.inf)
    if not math.isfinite(low) or not math.isfinite(high) or low > high:
        raise ValueError(
            f"empty numeric range after applying representable inclusivity flags: "
            f"{value_range!r}"
        )
    return low, high


def _draw_float(rng: Random, value_range: dict[str, Any]) -> float:
    low, high = _float_bounds(value_range)
    if low == high:
        return low
    candidate = rng.uniform(low, high)
    if not math.isfinite(candidate) or not low <= candidate <= high:
        # ``uniform`` computes through a span that can overflow for two finite
        # opposite-sign extremes. Either closed endpoint is still a valid draw.
        candidate = low if rng.random() < 0.5 else high
    return candidate


def _lexical_member(rng: Random, value_range: dict[str, Any], primitive: str) -> str:
    """Draw a string in a Python/ORM lexical interval without rejection sampling."""
    low = value_range.get("min")
    high = value_range.get("max")
    if low is not None and not isinstance(low, str):
        raise ValueError(f"{primitive} range minimum must be a string: {value_range!r}")
    if high is not None and not isinstance(high, str):
        raise ValueError(f"{primitive} range maximum must be a string: {value_range!r}")
    low_inclusive = bool(value_range.get("min_inclusive", True))
    high_inclusive = bool(value_range.get("max_inclusive", True))

    def inside(candidate: str) -> bool:
        return (low is None or candidate > low or (low_inclusive and candidate == low)) and (
            high is None or candidate < high or (high_inclusive and candidate == high)
        )

    candidates: set[str] = set()
    if low is not None:
        candidates.add(low)
        # Appending U+0000 is the immediate lexical successor of a string.
        # It both proves whether an exclusive lower interval has a member and
        # gives narrow prefix intervals a member unrelated Faker words cannot hit.
        candidates.add(low + "\x00")
        for _ in range(32):
            suffix = "".join(chr(rng.randint(0, 126)) for _ in range(rng.randint(1, 4)))
            candidates.add(low + suffix)
    else:
        candidates.update(("", "a", "m", "z", "\x00"))
        for _ in range(32):
            candidates.add("".join(chr(rng.randint(0, 126)) for _ in range(rng.randint(0, 8))))

    if high is not None:
        candidates.add(high)
        if high:
            prefix, last = high[:-1], ord(high[-1])
            # A prefix is below every non-empty extension.  When the last code
            # point can be stepped down, its maximal extension supplies another
            # representable member immediately below a tight upper bound.
            candidates.add(prefix)
            if last > 0:
                candidates.add(prefix + chr(last - 1) + chr(0x10FFFF))

    valid = sorted(candidate for candidate in candidates if inside(candidate))
    if not valid:
        raise ValueError(
            f"empty or non-representable {primitive} lexical range after applying "
            f"inclusivity flags: {value_range!r}"
        )
    return rng.choice(valid)


def _date_member(rng: Random, value_range: dict[str, Any]) -> str:
    def parse(name: str) -> date | None:
        raw = value_range.get(name)
        if raw is None:
            return None
        if not isinstance(raw, str):
            raise TypeError(f"Date range {name} must be an ISO date: {value_range!r}")
        try:
            return date.fromisoformat(raw)
        except ValueError as error:
            raise ValueError(f"Date range {name} is not a valid ISO date: {raw!r}") from error

    low = parse("min")
    high = parse("max")
    if low is None:
        assert high is not None  # value_range schema requires at least one bound
        try:
            low = min(_DATE_ANCHOR_START, high - timedelta(days=366))
        except OverflowError:
            low = date.min
    if high is None:
        try:
            high = max(_DATE_ANCHOR_END, low + timedelta(days=366))
        except OverflowError:
            high = date.max
    if value_range.get("min") is not None and not value_range.get("min_inclusive", True):
        try:
            low += timedelta(days=1)
        except OverflowError as error:
            raise ValueError(f"empty Date range: {value_range!r}") from error
    if value_range.get("max") is not None and not value_range.get("max_inclusive", True):
        try:
            high -= timedelta(days=1)
        except OverflowError as error:
            raise ValueError(f"empty Date range: {value_range!r}") from error
    if low > high:
        raise ValueError(
            f"empty Date range after applying day resolution and inclusivity flags: {value_range!r}"
        )
    return date.fromordinal(rng.randint(low.toordinal(), high.toordinal())).isoformat()


def _parse_datetime(raw: Any, name: str, value_range: dict[str, Any]) -> datetime:
    if not isinstance(raw, str):
        raise TypeError(f"DateTime range {name} must be an ISO datetime: {value_range!r}")
    try:
        return _rf7_input.parse_datetime(raw)
    except ValueError as error:
        raise ValueError(f"DateTime range {name} is not valid ISO-8601: {raw!r}") from error


def _datetime_resolution(raw: str) -> timedelta:
    """The smallest unit explicitly declared by an ISO datetime bound."""
    clock = raw.split("T", 1)[-1].split("t", 1)[-1].split(" ", 1)[-1]
    clock = clock.rstrip("Zz")
    # Remove an offset without mistaking the date's '-' characters for one.
    for marker in ("+", "-"):
        if marker in clock:
            clock = clock.split(marker, 1)[0]
            break
    if "." in clock:
        digits = len(clock.split(".", 1)[1])
        return timedelta(microseconds=10 ** max(0, 6 - min(digits, 6)))
    if clock.count(":") >= 2:
        return timedelta(seconds=1)
    return timedelta(minutes=1)


def _datetime_member(rng: Random, value_range: dict[str, Any]) -> str:
    raw_low = value_range.get("min")
    raw_high = value_range.get("max")
    low = _parse_datetime(raw_low, "min", value_range) if raw_low is not None else None
    high = _parse_datetime(raw_high, "max", value_range) if raw_high is not None else None
    declared = [_datetime_resolution(raw) for raw in (raw_low, raw_high) if isinstance(raw, str)]
    resolution = min(declared, default=timedelta(seconds=1))
    present = low or high
    assert present is not None  # value_range schema requires at least one bound
    timezone = present.tzinfo
    if (
        low is not None
        and high is not None
        and ((low.utcoffset() is None) != (high.utcoffset() is None))
    ):
        raise ValueError(
            f"non-representable DateTime range mixes offset-aware and naive bounds: {value_range!r}"
        )
    anchor_start = _DATETIME_ANCHOR_START.replace(tzinfo=timezone)
    anchor_end = _DATETIME_ANCHOR_END.replace(tzinfo=timezone)
    if low is None:
        assert high is not None
        try:
            low = min(anchor_start, high - timedelta(days=366))
        except OverflowError:
            low = datetime.min.replace(tzinfo=timezone)
    if high is None:
        try:
            high = max(anchor_end, low + timedelta(days=366))
        except OverflowError:
            high = datetime.max.replace(tzinfo=timezone)
    if raw_low is not None and not value_range.get("min_inclusive", True):
        try:
            low += _datetime_resolution(raw_low)
        except OverflowError as error:
            raise ValueError(f"empty DateTime range: {value_range!r}") from error
    if raw_high is not None and not value_range.get("max_inclusive", True):
        try:
            high -= _datetime_resolution(raw_high)
        except OverflowError as error:
            raise ValueError(f"empty DateTime range: {value_range!r}") from error
    if low > high:
        raise ValueError(
            f"empty DateTime range after applying declared resolution and inclusivity "
            f"flags: {value_range!r}"
        )
    span_us = int((high - low).total_seconds() * 1_000_000)
    tick_us = max(1, int(resolution.total_seconds() * 1_000_000))
    moment = low + timedelta(microseconds=rng.randint(0, span_us // tick_us) * tick_us)
    timespec = (
        "microseconds"
        if tick_us < 1_000_000
        else ("seconds" if tick_us < 60_000_000 else "minutes")
    )
    return moment.isoformat(timespec=timespec)


def make_value(
    primitive: str,
    rng: Random,
    *,
    allowed: list[Any] | tuple[Any, ...] | None = None,
    value_range: dict[str, Any] | None = None,
) -> Any:
    """Return one scalar of ``primitive`` that the population loader accepts.

    ``rng`` is a :class:`random.Random`; all numeric draws and the faker seed are
    taken from it, so a single seed threads the whole generator and two processes
    with the same seed produce byte-identical output.

    ``allowed`` — when given, the value is chosen from it (the enum property).
    ``value_range`` — when given, ``min`` / ``max`` are honoured together with the
    ``min_inclusive`` / ``max_inclusive`` flags (the range property). The two
    properties Polyfactory was measured failing.

    Unconstrained ``Date`` / ``DateTime`` values use Faker between fixed anchors;
    constrained values are parsed and sampled at the interval's declared ISO
    resolution. Both paths render loader-valid ISO-8601 rather than hand-formatting.
    """
    if primitive not in PRIMITIVES:
        raise ValueError(
            f"unknown primitive {primitive!r}; the meta-schema allows {list(PRIMITIVES)}"
        )

    if allowed is not None:
        # An enum member is valid by definition of the value constraint; no
        # primitive draw is needed or wanted.
        return rng.choice(list(allowed))

    if primitive == "Duration":
        from gnd.terms import MAX_DURATION_DAYS

        domain = value_range or {}
        lower = max(0, domain.get("min", 0) + (not domain.get("min_inclusive", True)))
        upper = min(
            MAX_DURATION_DAYS,
            domain.get("max", MAX_DURATION_DAYS) - (not domain.get("max_inclusive", True)),
        )
        return rng.randint(lower, upper)
    if primitive == "Integer":
        rng_range = value_range or {"min": 0, "max": 1_000_000}
        low, high = _int_bounds(rng_range)
        return rng.randint(low, high)

    if primitive in ("Float", "Number"):
        return _draw_float(rng, value_range or {"min": 0.0, "max": 1_000_000.0})

    if primitive == "Boolean":
        return rng.choice([True, False])

    if primitive == "String":
        if value_range is not None:
            return _lexical_member(rng, value_range, primitive)
        fake = _seeded_faker(rng)
        return fake.word()

    if primitive == "Date":
        if value_range is not None:
            return _date_member(rng, value_range)
        fake = _seeded_faker(rng)
        # ABSOLUTE anchors, never "today"/"now": a wall-clock reference would make
        # two processes seeded identically disagree (measured: the determinism
        # test caught exactly this). Fixed bounds keep the draw a pure function of
        # the seed.
        value: date = fake.date_between_dates(_DATE_ANCHOR_START, _DATE_ANCHOR_END)
        return value.isoformat()

    if primitive == "DateTime":
        if value_range is not None:
            return _datetime_member(rng, value_range)
        fake = _seeded_faker(rng)
        moment: datetime = fake.date_time_between_dates(
            _DATETIME_ANCHOR_START, _DATETIME_ANCHOR_END
        )
        return moment.replace(microsecond=0).isoformat()

    if primitive == "Binary":
        if value_range is not None:
            return _lexical_member(rng, value_range, primitive)
        fake = _seeded_faker(rng)
        raw = fake.binary(length=16)
        return base64.b64encode(raw).decode("ascii")

    # Unreachable: every meta-schema primitive is handled above, and the guard at
    # the top rejects anything else. Kept as a loud failure rather than a silent
    # None so a future primitive without a branch cannot slip through.
    raise ValueError(f"no generator branch for primitive {primitive!r}")  # pragma: no cover


def predicate_for(primitive: str):
    """The population loader's OWN predicate for ``primitive`` (never a copy)."""
    return popvalidate._PRIMITIVE_PREDICATES.get(primitive)
