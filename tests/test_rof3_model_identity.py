"""ROF3 (report-output-fidelity): the canonical model identity and its producer (issue 111).

The corpus under tests/fixtures/rof3-model-identity is the phase's approval instrument;
its README tells each case and expected/ holds the vectors. Written before the
implementation: the cases that need ``model_identity`` or ``gnd validate --identity``
fail until ROF3 lands; the legacy pins and the corpus self-check pass now.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys

import pytest
from support.repository import REPO_ROOT

from gnd.model import load_model
from gnd.values import model_digest

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rof3-model-identity"
EXPECTED = CORPUS / "expected"
VECTORS = json.loads((EXPECTED / "vectors.json").read_text())
IDENTIFIED = sorted(case for case, row in VECTORS.items() if row["identity"] is not None)


def _values_function(name: str):
    function = getattr(importlib.import_module("gnd.values"), name, None)
    assert function is not None, f"gnd.values.{name} does not exist yet"
    return function


def _model(case: str):
    return load_model(CORPUS / VECTORS[case]["model"])


def _validate_identity(case: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", "validate", VECTORS[case]["model"], "--identity"],
        cwd=CORPUS, capture_output=True, check=False,
    )


@pytest.mark.parametrize("case", IDENTIFIED)
def test_identity_bytes_match_the_vector(case: str) -> None:
    model = _model(case)
    assert _values_function("model_identity_bytes")(model) == (EXPECTED / f"{case}.identity.json").read_bytes()
    assert _values_function("model_identity")(model) == (EXPECTED / f"{case}.digest").read_text().strip()


@pytest.mark.parametrize("case", sorted(VECTORS))
def test_legacy_digest_is_unchanged(case: str) -> None:
    assert model_digest(_model(case)) == (EXPECTED / f"{case}.legacy").read_text().strip()


@pytest.mark.parametrize("case", IDENTIFIED)
def test_producer_prints_the_digest_and_the_document(case: str) -> None:
    result = _validate_identity(case)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (EXPECTED / f"{case}.stdout.txt").read_bytes()
    first, document = result.stdout.decode("utf-8").splitlines()
    # A caller with hashlib alone recomputes the digest from the printed document.
    recomputed = "sha256:" + hashlib.sha256((document + "\n").encode("utf-8")).hexdigest()
    assert first.split()[2] == recomputed


def test_surrogate_model_is_refused_not_crashed() -> None:
    model = _model("surrogate")
    error = _values_function("ModelIdentityError")
    with pytest.raises(error) as raised:
        _values_function("model_identity")(model)
    assert raised.value.rule_id == "model:identity-unrepresentable"
    result = _validate_identity("surrogate")
    assert result.returncode == 3
    assert result.stdout.decode("utf-8", "replace").rstrip().endswith("[model:identity-unrepresentable]")
    assert b"Traceback" not in result.stderr


def test_operations_only_change_keeps_a_plain_identity_and_moves_a_reference_one() -> None:
    assert VECTORS["operations-a"]["identity"] == VECTORS["operations-b"]["identity"]
    assert VECTORS["reference"]["identity"] != VECTORS["reference-operations"]["identity"]
    identity = _values_function("model_identity")
    assert identity(_model("operations-a")) == identity(_model("operations-b"))
    assert identity(_model("reference")) != identity(_model("reference-operations"))


def test_versions_are_defined_only_where_the_definition_says() -> None:
    identity = _values_function("model_identity")
    error = _values_function("ModelIdentityError")
    reference, plain = _model("reference"), _model("plain-small")
    assert identity(reference, 1) == VECTORS["reference"]["identity"]
    assert identity(plain, 2) == VECTORS["plain-small"]["identity"]
    for model, version in ((reference, 2), (plain, 1), (plain, 3)):
        with pytest.raises(error):
            identity(model, version)


def test_corpus_lists_every_case_once() -> None:
    models = {path.relative_to(CORPUS).as_posix() for path in (CORPUS / "models").rglob("*.orm.*")}
    assert models == {row["model"] for row in VECTORS.values()}
    for case, row in VECTORS.items():
        assert (EXPECTED / f"{case}.legacy").is_file()
        has_vector = (EXPECTED / f"{case}.identity.json").is_file()
        assert has_vector == (row["identity"] is not None)
    assert {row["identity_version"] for row in VECTORS.values() if row["identity"]} == {1, 2}


# --- the rest of the spec's section 8 (written with the implementation) -------------------


def _independent_identity(model) -> str:
    """The definition re-implemented here, without gnd's canonical helpers (T1)."""
    import datetime

    def plain(value):
        if isinstance(value, dict):
            return {key: plain(item) for key, item in value.items()}
        if isinstance(value, list):
            return [plain(item) for item in value]
        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return value.isoformat()
        return value

    if model.reference_populations:
        declarations = [dict(d, fact_types=sorted(d["fact_types"])) for d in model.reference_populations]
        document = {
            "identity_version": 1,
            "model": plain(model.model_dump(exclude={"warnings", "reference_populations"})),
            "reference_populations": sorted(declarations, key=lambda d: d["id"]),
        }
    else:
        document = {
            "identity_version": 2,
            "model": plain(model.model_dump(exclude={"warnings", "operations", "reference_populations"})),
        }
    text = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return "sha256:" + hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()


def test_t1_every_tracked_model_matches_an_independent_implementation() -> None:
    from gnd import values

    tracked = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    paths = [line for line in tracked.stdout.splitlines() if line.endswith((".orm.yaml", ".orm.yml", ".orm.json"))]
    versions = {1: 0, 2: 0}
    for path in paths:
        try:
            model = load_model(REPO_ROOT / path)
        except Exception:  # noqa: BLE001, S112 -- a file that does not load has no identity to compare
            continue
        try:
            expected = _independent_identity(model)
        except UnicodeEncodeError:
            with pytest.raises(values.ModelIdentityError):
                values.model_identity(model)
            continue
        assert values.model_identity(model) == expected, path
        versions[1 if model.reference_populations else 2] += 1
    assert versions[1] >= 10 and versions[2] >= 250, versions


def _loaded(tmp_path, name: str = "m.orm.json", mutate=None):
    document = json.loads((CORPUS / "models" / "negative-zero.orm.json").read_text())
    if mutate is not None:
        mutate(document)
    path = tmp_path / name
    path.write_text(json.dumps(document))
    return load_model(path)


@pytest.mark.parametrize("value", [{7: "seven"}, {"set": {1, 2}}, {"decimal": __import__("decimal").Decimal("1.5")}, {"bytes": b"x"}])
def test_t4_t6_unrepresentable_values_are_refused_with_the_rule(tmp_path, value) -> None:
    from gnd import values

    model = load_model(CORPUS / "models" / "plain-small.orm.yaml")
    provenance = model.fact_types[0]["constraints"][0]["provenance"]
    provenance.update(value)
    with pytest.raises(values.ModelIdentityError) as raised:
        values.model_identity(model)
    assert raised.value.rule_id == "model:identity-unrepresentable"
    assert raised.value.path.startswith("$.fact_types")
    assert values.model_digest(model)  # the legacy digest stays total


def test_t5_a_lone_surrogate_loads_and_is_refused_while_legacy_answers() -> None:
    from gnd import values

    model = _model("surrogate")
    assert values.model_digest(model) == (EXPECTED / "surrogate.legacy").read_text().strip()
    with pytest.raises(values.ModelIdentityError):
        values.model_identity_bytes(model)


def test_t7_nesting_the_loader_accepts_has_an_identity_and_deeper_objects_are_refused(tmp_path) -> None:
    from ruamel.yaml import YAML

    from gnd import values

    document = YAML(typ="safe").load((CORPUS / "models" / "plain-small.orm.yaml").read_text())
    node = deep = {}
    for _ in range(40):
        node["n"] = {}
        node = node["n"]
    document["fact_types"][0]["constraints"][0]["provenance"]["deep"] = deep
    path = tmp_path / "deep.orm.json"
    path.write_text(json.dumps(document))
    loaded = load_model(path)
    kept, depth = loaded.fact_types[0]["constraints"][0]["provenance"]["deep"], 0
    while kept:
        kept, depth = kept["n"], depth + 1
    assert depth == 40  # the nesting survived loading
    assert values.model_identity(loaded).startswith("sha256:")
    model = load_model(CORPUS / "models" / "plain-small.orm.yaml")
    node = deep = {}
    for _ in range(5000):
        node["n"] = {}
        node = node["n"]
    model.fact_types[0]["constraints"][0]["provenance"]["deep"] = deep
    with pytest.raises(values.ModelIdentityError):
        values.model_identity(model)


def test_t7_absent_and_empty_reference_populations_give_one_identity(tmp_path) -> None:
    from gnd import values

    source = (CORPUS / "models" / "plain-small.orm.yaml").read_text().replace("version: 2\n", "version: 4\n")
    absent = tmp_path / "absent.orm.yaml"
    absent.write_text(source)
    empty = tmp_path / "empty.orm.yaml"
    empty.write_text(source.rstrip("\n") + "\nreference_populations: []\n")
    empty_model = load_model(empty)
    assert not empty_model.reference_populations
    assert values.model_identity(load_model(absent)) == values.model_identity(empty_model)
    assert values.model_identity(empty_model, 2)


def test_t8_identity_is_linear_near_the_input_cap(tmp_path) -> None:
    import time

    from ruamel.yaml import YAML

    from gnd import values

    document = YAML(typ="safe").load((CORPUS / "models" / "plain-small.orm.yaml").read_text())
    index = 0
    while len(json.dumps(document)) < 9_000_000:
        for _ in range(2000):
            document["object_types"].append(
                {"id": f"code_{index}", "name": f"Code{index}", "kind": "value", "primitive": "String"}
            )
            document["fact_types"].append({
                "id": f"has_code_{index}",
                "reading": "{CustomerCode} has code " + f"{{Code{index}}} " + "x" * 200,
                "roles": [
                    {"object_type": "customer_code", "role_name": "customer"},
                    {"object_type": f"code_{index}", "role_name": f"code_{index}"},
                ],
            })
            index += 1
    path = tmp_path / "big.orm.json"
    path.write_text(json.dumps(document))
    model = load_model(path)
    started = time.perf_counter()
    values.model_identity(model)
    assert time.perf_counter() - started < 4.0


def test_t11_the_normative_text_has_one_home_and_quotes_the_vectors() -> None:
    text = (REPO_ROOT / "src/gnd/skills/gnd-orm-core/references/representation-format.md").read_text()
    assert text.count("### Model identity (canonical, versions 1 and 2)") == 1
    for case in ("plain-small", "floats", "reference"):
        assert VECTORS[case]["identity"] in text
    assert "model:identity-unrepresentable" in text
    formats = (REPO_ROOT / "docs/reference/formats.md").read_text()
    assert "Model identity (canonical, versions" in formats
    assert "1e-05" in text and "0.30000000000000004" in text


@pytest.mark.parametrize("case", sorted(VECTORS))
def test_t12_validate_text_trace_and_json_are_unchanged(case: str) -> None:
    # The full byte pins are the existing validate/trace suites (gate); here: no new
    # line on the other outputs, and the report still carries the legacy digest.
    from support.cli_runner import run_main

    model = VECTORS[case]["model"]
    for argv in (["validate", model], ["validate", model, "--trace"]):
        assert b"MODEL IDENTITY" not in run_main(argv, cwd=CORPUS).stdout
    payload = json.loads(run_main(["validate", model, "--format", "json"], cwd=CORPUS).stdout)
    legacy = "sha256:" + (EXPECTED / f"{case}.legacy").read_text().strip()

    def digests(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "model_digest":
                    yield item
                yield from digests(item)
        elif isinstance(value, list):
            for item in value:
                yield from digests(item)

    found = [value for value in digests(payload) if value is not None]
    # A plain version-3 validate payload carries no model_digest at all (frozen arm).
    assert all(value == legacy for value in found)
    if VECTORS[case]["identity"] is not None and VECTORS[case]["identity_version"] == 2:
        assert VECTORS[case]["identity"] not in json.dumps(payload)


def test_t9b_identity_is_not_combined_with_other_outputs() -> None:
    for extra in (["--trace"], ["--document", "x.md"], ["--format", "json"]):
        result = subprocess.run(
            [sys.executable, "-m", "gnd", "validate", VECTORS["plain-small"]["model"], "--identity", *extra],
            cwd=CORPUS, capture_output=True, check=False,
        )
        assert result.returncode == 64, extra
        assert result.stdout == b""


def test_t9c_a_model_that_does_not_load_gets_the_ordinary_refusal(tmp_path) -> None:
    broken = tmp_path / "broken.orm.yaml"
    broken.write_text("version: 2\nmodel_id: x\n")
    result = subprocess.run(
        [sys.executable, "-m", "gnd", "validate", str(broken), "--identity"], capture_output=True, check=False
    )
    plain = subprocess.run([sys.executable, "-m", "gnd", "validate", str(broken)], capture_output=True, check=False)
    assert result.returncode == plain.returncode == 3
    assert result.stdout == plain.stdout


def test_t13_one_walk_and_one_byte_form() -> None:
    import inspect

    from gnd import values

    parts = inspect.getsource(values._identity_parts)
    assert "_canonical(" in parts and "_reference_identity_document(" in parts
    assert "canonical_json_bytes(" in parts
    assert "json.dumps" not in parts
    assert "_identity_parts(" in inspect.getsource(values.model_identity_document)
    assert "_identity_parts(" in inspect.getsource(values.model_identity_bytes)
    assert "_reference_identity_document(" in inspect.getsource(values.reference_model_digest)


# --- review findings (Codex, ROF3 diff review of 3b0dbcc1) ---------------------------------


def test_p1_a_version_one_declaration_is_walked_and_refuses_a_non_string_key() -> None:
    from gnd import values

    model = _model("reference")
    model.reference_populations[0]["extra"] = {7: "seven"}
    with pytest.raises(values.ModelIdentityError) as raised:
        values.model_identity(model)
    assert raised.value.path.startswith("$.reference_populations")


def test_p2_a_malformed_declaration_is_refused_not_a_type_error() -> None:
    from gnd import values

    model = _model("reference")
    model.reference_populations[0]["fact_types"] = [1, "dispatch_catalog_allows"]
    with pytest.raises(values.ModelIdentityError):
        values.model_identity(model)


def test_p3_the_producer_writes_utf8_whatever_the_terminal_encoding() -> None:
    import os

    result = subprocess.run(
        [sys.executable, "-m", "gnd", "validate", VECTORS["dates-and-text"]["model"], "--identity"],
        cwd=CORPUS, capture_output=True, check=False, env={**os.environ, "PYTHONIOENCODING": "ascii"},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == (EXPECTED / "dates-and-text.stdout.txt").read_bytes()


def test_p4_the_document_function_refuses_what_cannot_be_written() -> None:
    from gnd import values

    with pytest.raises(values.ModelIdentityError):
        values.model_identity_document(_model("surrogate"))


def _with_provenance(tmp_path, value_yaml: str):
    source = (CORPUS / "models" / "plain-small.orm.yaml").read_text()
    old = 'provenance: { user_quote: "Each customer has at most one email address." }'
    path = tmp_path / "m.orm.yaml"
    path.write_text(source.replace(old, f'provenance: {{ user_quote: "q", at: {value_yaml} }}', 1))
    return load_model(path)


@pytest.mark.parametrize(
    ("value_yaml", "spelled"),
    [
        ("2025-01-01", '"at":"2025-01-01"'),
        ('"2025-01-01"', '"at":"2025-01-01"'),
        ("2025-01-01T00:00:00Z", '"at":"2025-01-01T00:00:00+00:00"'),
        ('"2025-01-01T00:00:00Z"', '"at":"2025-01-01T00:00:00Z"'),
        ("2025-01-01T10:20:30.5+02:00", '"at":"2025-01-01T10:20:30.500000+02:00"'),
        ("2025-01-01 10:20:30", '"at":"2025-01-01T10:20:30"'),
    ],
)
def test_p5_date_and_datetime_spellings_follow_the_normative_text(tmp_path, value_yaml, spelled) -> None:
    from gnd import values

    assert spelled in values.model_identity_bytes(_with_provenance(tmp_path, value_yaml)).decode("utf-8")


# Hand-written from the normative text, not from an encoder (P8): each value, set in a
# provenance field of a loaded model, must appear in the canonical bytes exactly so.
P8_VECTORS = [
    (1e16, '"v":1e+16'),
    (1e15, '"v":1000000000000000.0'),
    (0.0001, '"v":0.0001'),
    (0.00001, '"v":1e-05'),
    (5e-324, '"v":5e-324'),
    (-0.0, '"v":-0.0'),
    (3.0, '"v":3.0'),
    (3, '"v":3'),
    (12345678901234567890, '"v":12345678901234567890'),
    ("tab\there", '"v":"tab\\there"'),
    ("bell\x07", '"v":"bell\\u0007"'),
    ("quote\"back\\slash", '"v":"quote\\"back\\\\slash"'),
    ("del\x7fé€😀", '"v":"del\x7fé€😀"'),
    ("line sep", '"v":"line sep"'),
]


@pytest.mark.parametrize(("value", "spelled"), P8_VECTORS)
def test_p8_hand_written_byte_vectors(value, spelled) -> None:
    from gnd import values

    model = _model("plain-small")
    model.fact_types[0]["constraints"][0]["provenance"]["v"] = value
    assert spelled in values.model_identity_bytes(model).decode("utf-8")


def test_p8_keys_sort_by_code_point_not_by_utf16_unit() -> None:
    from gnd import values

    model = _model("plain-small")
    # U+FF5E sorts before U+1F600 by code point, after it by UTF-16 unit.
    model.fact_types[0]["constraints"][0]["provenance"]["k"] = {"\U0001f600": 1, "～": 2}
    assert '"k":{"～":2,"\U0001f600":1}' in values.model_identity_bytes(model).decode("utf-8")
