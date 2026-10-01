"""Owner-approved migration instrument cases; synthetic identities only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

CORPUS = Path(__file__).parent / "fixtures/public-launch-phase-3"
CASES = json.loads((CORPUS / "inputs.json").read_text())["cases"]
ANSWERS = {row["id"]: row for row in json.loads((CORPUS / "answers.json").read_text())["cases"]}


@pytest.mark.parametrize("case", CASES, ids=lambda row: row["id"])
def test_approved_instrument_case(case):
    try:
        from support.public_migration import MigrationRefusal, validate_acceptance_packet
    except ModuleNotFoundError:
        pytest.fail("P3 migration instrument is absent")
    answer = ANSWERS[case["id"]]
    try:
        validate_acceptance_packet(case["packet"])
        observed = (0, None)
    except MigrationRefusal as error:
        observed = (1, error.reason)
    assert observed == (answer["exit"], answer["reason"])


@pytest.mark.parametrize("bad", [None, [], True, 1, "text", {"rows": []}])
def test_hostile_packet_roots_refuse_without_traceback(bad):
    from support.public_migration import MigrationRefusal, validate_acceptance_packet
    with pytest.raises(MigrationRefusal, match="invalid-packet-shape"):
        validate_acceptance_packet(bad)


@pytest.mark.parametrize("field,bad", [
    ("originals", []), ("originals", {"x": []}), ("collected", [[]]),
    ("rows", None), ("surfaces", None), ("expected_surfaces", [[]]),
    ("private_dependencies", [{}]), ("acceptance_passed", 1),
    ("handoff_requested", "yes"), ("source_delta_accounted", None),
])
def test_hostile_packet_fields_refuse(field, bad):
    import copy

    from support.public_migration import MigrationRefusal, validate_acceptance_packet
    packet = copy.deepcopy(CASES[0]["packet"])
    packet[field] = bad
    with pytest.raises(MigrationRefusal):
        validate_acceptance_packet(packet)


@pytest.mark.parametrize("field,bad", [
    ("source_node", []), ("source_node", "../escape.py::test_x"),
    ("source_sha256", {}), ("disposition", []), ("selection", {}),
    ("claim", ""), ("target_nodes", ["/private/file.py::test_x"]),
    ("target_nodes", [{}]), ("changed_boundary", None),
])
def test_hostile_row_fields_refuse(field, bad):
    import copy

    from support.public_migration import MigrationRefusal, validate_acceptance_packet
    packet = copy.deepcopy(CASES[0]["packet"])
    packet["rows"][0][field] = bad
    with pytest.raises(MigrationRefusal):
        validate_acceptance_packet(packet)


def test_loader_admits_exact_cap_and_refuses_one_over_before_parse(tmp_path, monkeypatch):
    from support import public_migration as module
    data = b'{"value": 1}\n'
    path = tmp_path.resolve() / "rows.jsonl"
    path.write_bytes(data)
    assert module.load_case_map(path, max_bytes=len(data)) == ({"value": 1},)
    monkeypatch.setattr(module, "strict_json", lambda _: pytest.fail("oversize reached parser"))
    with pytest.raises(module.MigrationRefusal, match="oversize-map"):
        module.load_case_map(path, max_bytes=len(data) - 1)


def test_compressed_admitted_bytes_and_expansion_cap(tmp_path):
    import gzip

    from support.public_migration import MigrationRefusal, load_case_map
    path = tmp_path.resolve() / "rows.jsonl.gz"
    data = (b'{"x": "' + b'x' * 1000 + b'"}\n')
    path.write_bytes(gzip.compress(data))
    assert load_case_map(path, max_bytes=len(data)) == ({"x": "x" * 1000},)
    with pytest.raises(MigrationRefusal, match="oversize-map"):
        load_case_map(path, max_bytes=100)


@pytest.mark.parametrize("raw", [
    b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'\xff',
    b'{"x":' + b'9' * 5000 + b'}', b'[' * 2000 + b']' * 2000,
    b'[]', b'\x1f\x8bbad gzip',
], ids=["duplicate-key", "nan", "infinity", "invalid-utf8", "oversize-integer",
        "deep-json", "nonobject-row", "bad-gzip"])
def test_hostile_serializations_refuse(tmp_path, raw):
    from support.public_migration import MigrationRefusal, load_case_map
    path = tmp_path.resolve() / "bad.jsonl"
    path.write_bytes(raw)
    with pytest.raises(MigrationRefusal):
        load_case_map(path)


def test_symlink_and_fifo_maps_refuse(tmp_path):
    import os

    from support.public_migration import MigrationRefusal, load_case_map
    root = tmp_path.resolve()
    original = root / "map.jsonl"
    original.write_bytes(b'{"x":1}\n')
    link = root / "alias.jsonl"
    link.symlink_to(original)
    with pytest.raises(MigrationRefusal, match="symlink-map"):
        load_case_map(link)
    fifo = root / "fifo.jsonl"
    os.mkfifo(fifo)
    with pytest.raises(MigrationRefusal, match="nonregular-map"):
        load_case_map(fifo)


def test_fixed_denominator_validation_has_bounded_cost():
    import copy
    import time

    from support.public_migration import validate_case_map
    template = CASES[0]["packet"]["rows"][0]
    rows = []
    originals = {}
    for i in range(5331):
        row = copy.deepcopy(template)
        row["source_node"] = f"source-case-{i:05d}"
        rows.append(row)
        originals[row["source_node"]] = row["source_sha256"]
    start = time.monotonic()
    validate_case_map(tuple(rows), originals=originals, collected={"tests/current.py::test_current"})
    assert time.monotonic() - start < 60


def test_approval_instrument_rejects_constant_accept_and_constant_refuse():
    accepted = [row for row in ANSWERS.values() if row["exit"] == 0]
    refused = [row for row in ANSWERS.values() if row["exit"] == 1]
    assert len(accepted) == 4 and len(refused) == 15
    assert all((0, None) != (row["exit"], row["reason"]) for row in refused)
    assert all((1, "always-refuse") != (row["exit"], row["reason"]) for row in accepted)
