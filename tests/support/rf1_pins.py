"""Shared machinery for the RF1 characterization pins (code-refactoring milestone).

Spec: .gnd-planning/milestones/code-refactoring/notes/phase-RF1-spec.md, sections
6.2 and 6.7. One comparison function serves every lane and one normalizer serves
every session evidence file (standing rule 4).

Goldens live under tests/fixtures/rf1-pins/goldens/<lane>/<key>.json. A golden
whose bytes depend on the interpreter is stored as <key>.py311.json, .py313.json
and .py314.json instead (decision D2). Capture mode is selected by the
GND_RF1_CAPTURE environment variable, which only ``tools/rf1_pins.py capture``
sets: it writes into a fresh directory and never into the fixture tree.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import os
import re
import sys
from collections.abc import Callable, Iterable, Mapping
from decimal import Decimal
from pathlib import Path, PurePath
from typing import Any

import pytest

PINS_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "rf1-pins"
GOLDENS = PINS_ROOT / "goldens"
MINORS = ("py311", "py313", "py314")
CAPTURE_ENV = "GND_RF1_CAPTURE"
_KEY_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def minor_tag() -> str:
    return f"py{sys.version_info.major}{sys.version_info.minor}"


def key_file(key: str) -> str:
    """The file stem for a golden key; distinct keys must map to distinct stems."""
    return _KEY_UNSAFE.sub("_", key).strip("_")


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=1, allow_nan=False) + "\n").encode()


def encode(value: Any) -> Any:
    """A JSON-able, interpreter-neutral rendering of an observed value."""
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return {"float": repr(value)}
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"hex": bytes(value).hex()}
    if isinstance(value, Decimal):
        return {"decimal": str(value)}
    if isinstance(value, enum.Enum):
        return {"enum": f"{type(value).__name__}.{value.name}", "value": encode(value.value)}
    if isinstance(value, PurePath):
        return {"path": str(value)}
    if isinstance(value, Mapping):
        items = {}
        for key, item in value.items():
            name = key if isinstance(key, str) else f"<{type(key).__name__}>{key!r}"
            items[name] = encode(item)
        return items
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return {"set": sorted((encode(item) for item in value), key=lambda item: canonical(item))}
    if isinstance(value, BaseException):
        return raised(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            "dataclass": type(value).__name__,
            "fields": {item.name: encode(getattr(value, item.name)) for item in dataclasses.fields(value)},
        }
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        return {"model": type(value).__name__, "data": encode(dump(mode="json"))}
    return {"repr": repr(value), "type": type(value).__name__}


def raised(error: BaseException) -> dict:
    cls = type(error)
    return {"raises": f"{cls.__module__}.{cls.__qualname__}", "message": str(error)}


LARGE_RESULT_BYTES = 64 * 1024
# Declared scrubs for random names that GND itself generates inside messages.
RANDOM_TOKENS = ((re.compile(r"\.gnd-tmp-[0-9a-f]+"), ".gnd-tmp-<random>"),)


def _scrub_random(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False)
    for pattern, placeholder in RANDOM_TOKENS:
        text = pattern.sub(placeholder, text)
    return json.loads(text)


def observe(function: Callable[..., Any], *args: Any, **kwargs: Any) -> dict:
    """Call and record either the result or the exception.

    A result whose canonical form exceeds LARGE_RESULT_BYTES is recorded by
    sha256 and size, so goldens stay small without losing byte identity.
    """
    try:
        value = encode(function(*args, **kwargs))
    except RecursionError as error:
        return {"raises": "builtins.RecursionError", "message": type(error).__name__}
    except Exception as error:  # noqa: BLE001 -- characterization records every refusal
        return _scrub_random(raised(error))
    data = canonical(value)
    if len(data) > LARGE_RESULT_BYTES:
        return {"ok_digest": {"sha256": sha256_hex(data), "bytes": len(data)}}
    return {"ok": _scrub_random(value)}


def _capture_dir() -> Path | None:
    value = os.environ.get(CAPTURE_ENV)
    return Path(value) if value else None


def golden_path(lane: str, key: str) -> Path | None:
    """The golden for this interpreter, or None when only other minors have one."""
    stem = key_file(key)
    plain = GOLDENS / lane / f"{stem}.json"
    if plain.is_file():
        return plain
    keyed = GOLDENS / lane / f"{stem}.{minor_tag()}.json"
    if keyed.is_file():
        return keyed
    if any((GOLDENS / lane / f"{stem}.{tag}.json").is_file() for tag in MINORS):
        return None
    raise AssertionError(f"RF1 golden missing: {lane}/{stem}.json")


def assert_golden(lane: str, key: str, observed: Any) -> None:
    """Compare an observation with its committed golden (never writes the fixture tree)."""
    data = canonical(observed)
    capture = _capture_dir()
    if capture is not None:
        target = capture / lane / f"{key_file(key)}.json"
        if target.exists():
            raise AssertionError(f"RF1 capture key collision: {lane}/{key_file(key)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return
    path = golden_path(lane, key)
    if path is None:
        pytest.skip(f"no RF1 golden for {lane}/{key} under {minor_tag()} (decision D2)")
    expected = path.read_bytes()
    if data != expected:
        import difflib

        diff = "".join(
            difflib.unified_diff(
                expected.decode().splitlines(True), data.decode().splitlines(True), "golden", "observed", n=2
            )
        )
        raise AssertionError(f"RF1 pin changed: {lane}/{key}\n{diff[:6000]}")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- Session evidence normalization (spec 6.7, rules N1-N6) -----------------

_HEX64 = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
MONOTONIC_FIELDS = ("started_monotonic", "ended_monotonic", "decided_monotonic")
SECONDS_FIELDS = ("elapsed_seconds", "accounted_wall_seconds")


class NormalizationError(AssertionError):
    pass


def evidence_tree(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


# N7 (RF1 implementation finding): the session prompt embeds the absolute
# contract path (cli.py, "caller-validated contract at ..."), so every prompt
# digest varies with the temporary root; N4 amended: the receipt nonce is
# published inside attempt.json. Both are replaced by field-keyed placeholders.
KEYED_FIELDS = {
    "base_prompt_sha256": "<prompt-sha256>",
    "controller_prompt_sha256": "<prompt-sha256>",
    "effective_prompt_sha256": "<prompt-sha256>",
    "prompt_sha256": "<prompt-sha256>",
    "nonce": "<nonce>",
}
_PROMPT_TOKEN = re.compile(r"<prompt:sha256=[0-9a-f]{64}>")
_RESULT_SHA = re.compile(r'\\?"result_sha256\\?"\s*:\s*\{[^{}]*\}')


def normalize_text(
    text: str,
    *,
    own: str | None,
    by_digest: Mapping[str, str],
    tokens: Mapping[str, str],
    clock_injected: bool,
) -> str:
    """One text through N3, N7, N5 and (without an injected clock) N1/N2."""
    for needle, placeholder in sorted(tokens.items(), key=lambda item: -len(item[0])):
        if needle:
            text = text.replace(needle, placeholder)
    for name, placeholder in KEYED_FIELDS.items():
        text = re.sub(rf'(\\?"{name}\\?"\s*:\s*\\?")[0-9a-f]{{64}}', rf"\g<1>{placeholder}", text)
    text = _PROMPT_TOKEN.sub("<prompt:sha256>", text)
    # N8: digests of a tests-mode results file, which pytest writes with its own
    # timing attributes, are placeholders.
    text = _RESULT_SHA.sub(lambda m: _HEX64.sub("<junit-sha256>", m.group(0)), text)

    def digest(match: re.Match[str]) -> str:
        target = by_digest.get(match.group(0))
        if target is None or target == own:
            return match.group(0)
        return f"<sha256:{target}>"

    text = _HEX64.sub(digest, text)
    if not clock_injected:
        # A value is either a bare JSON number or an encode() float wrapper.
        value = r'(?:-?[0-9.eE+-]+|\{\\?"float\\?"\s*:\s*\\?"[^"\\]*\\?"\})'
        for field in MONOTONIC_FIELDS:
            text = re.sub(rf'(\\?"{field}\\?"\s*:\s*){value}', r'\1"<monotonic>"', text)
        for field in SECONDS_FIELDS:
            text = re.sub(rf'(\\?"{field}\\?"\s*:\s*){value}', r'\1"<seconds>"', text)
    return text


def tree_digests(files: Mapping[str, bytes], inputs: Mapping[str, bytes] | None = None) -> dict[str, str]:
    """Digest -> name for N5: evidence files, plus declared input files outside the run."""
    found = {sha256_hex(data): f"input:{name}" for name, data in (inputs or {}).items()}
    found.update({sha256_hex(data): name for name, data in files.items()})
    return found


def normalize_tree(
    files: Mapping[str, bytes],
    *,
    tokens: Mapping[str, str],
    forbidden: Iterable[str] = (),
    clock_injected: bool = True,
    inputs: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    """Apply N3, N4, N5 and (when the clock is not injected) N1/N2 to every file.

    ``tokens`` maps an absolute string (temporary root, interpreter, agent path)
    to its placeholder. ``forbidden`` strings must not occur in any file (N4).
    N5 replaces a 64-hex digest only after checking it equals the sha256 of
    another file's raw bytes, so a broken digest chain still fails the pin.
    """
    by_digest = tree_digests(files, inputs)
    result: dict[str, Any] = {}
    for name, data in files.items():
        for needle in forbidden:
            if needle and needle.encode() in data:
                raise NormalizationError(f"N4: forbidden token present in {name}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            result[name] = {"sha256": sha256_hex(data), "bytes": len(data)}
            continue
        result[name] = {
            "text": normalize_text(text, own=name, by_digest=by_digest, tokens=tokens, clock_injected=clock_injected)
        }
    return result


def normalize_json_text(text: str, *, tokens: Mapping[str, str]) -> Any:
    """Normalize a JSON document's text (N3) and parse it; non-JSON fails the pin."""
    for needle, placeholder in sorted(tokens.items(), key=lambda item: -len(item[0])):
        if needle:
            text = text.replace(needle, placeholder)
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise NormalizationError(f"N: not a JSON document: {error}") from None


class CountingClock:
    """A deterministic monotonic clock for N1: each call advances by one tick."""

    def __init__(self, start: float = 1000.0, tick: float = 0.25) -> None:
        self.value = start
        self.tick = tick

    def monotonic(self) -> float:
        self.value += self.tick
        return self.value


# --- Case manifest (tests/fixtures/rf1-pins/cases.json) ----------------------

def load_cases() -> dict:
    return json.loads((PINS_ROOT / "cases.json").read_text(encoding="utf-8"))


def build(descriptor: Mapping[str, Any]) -> Any:
    """Turn one cases.json input descriptor into the Python value a site receives."""
    import datetime as dt

    from pydantic import BaseModel

    kind, value = descriptor["kind"], descriptor["value"]
    if kind == "json":
        return value
    if kind == "float":
        return float(value)
    if kind == "float_list":
        return [float(item) if isinstance(item, str) else item for item in value]
    if kind == "decimal":
        return Decimal(value)
    if kind == "int_key_dict":
        return {int(key): item for key, item in value.items()}
    if kind == "model":

        class Rf1Sample(BaseModel):
            name: str
            count: int

        return Rf1Sample(**value)
    if kind == "tuple":
        return tuple(value)
    if kind == "set":
        return set(value)
    if kind == "date":
        return dt.date.fromisoformat(value)
    if kind == "datetime":
        return dt.datetime.fromisoformat(value)
    if kind == "bytes":
        return bytes.fromhex(value)
    if kind == "bytes_text":
        return value.encode("utf-8")
    if kind == "bytes_repeat":
        return bytes.fromhex(value[0]) * value[1]
    if kind == "nan_dict":
        return {value: float("nan")}
    if kind == "deep_json":
        return ("[" * value + "]" * value).encode()
    if kind == "yaml_list":
        return "".join(f"- {index}\n" for index in range(value))
    if kind == "surrogate":
        return "a" + chr(int(value, 16))
    raise ValueError(f"unknown case kind {kind!r}")


def inputs(group: str) -> list[tuple[str, Any]]:
    return [(name, build(descriptor)) for name, descriptor in sorted(load_cases()["inputs"][group].items())]


def scrub(observed: Any, replacements: Mapping[str, str]) -> Any:
    """Replace machine-specific strings (temporary roots) inside an observation."""
    text = json.dumps(observed, ensure_ascii=False)
    for needle, placeholder in sorted(replacements.items(), key=lambda item: -len(item[0])):
        if needle:
            text = text.replace(json.dumps(needle, ensure_ascii=False)[1:-1], placeholder)
    return json.loads(text)
