"""CT1: several anchors per fact role in a version-2 anchor sidecar."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import typing
import unicodedata
from pathlib import Path
from unittest.mock import patch

import jsonschema
import pytest

from gnd.anchors import (
    MAX_SIDECAR_BYTES,
    AnchorError,
    AnchorSidecar,
    _canonical,
    lexical_ranges,
    parse_anchor_sidecar,
    recognition_index,
    vocabulary_digest,
)
from gnd.api import check
from gnd.checker._core import _anchored_verdicts
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/v70-phase1"
SIDECAR = json.loads((FIXTURE / "population.pop.json.anchors.json").read_text())
SOURCE = unicodedata.normalize("NFC", (FIXTURE / "document.txt").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "src/gnd/anchor-sidecar.schema.json").read_text())
LABEL = next(a for a in SIDECAR["anchors"] if a["fact_key"]["fact_type"] == "record_has_label")
QUANTITY = next(a for a in SIDECAR["anchors"] if a["fact_key"]["fact_type"] == "invoice_has_quantity")


def _excerpt(start: int, end: int, source: str = SOURCE) -> str:
    return hashlib.sha256(source[start:end].encode("utf-8")).hexdigest()


def _anchor(template: dict, start: int, end: int, occurrence: int = 0, source: str = SOURCE) -> dict:
    anchor = copy.deepcopy(template)
    anchor["span"] = {"start": start, "end": end}
    anchor["occurrence"] = occurrence
    anchor["excerpt_sha256"] = _excerpt(start, end, source)
    return anchor


def _sidecar(extra: list[dict], *, version: int = 2, replace: dict | None = None) -> dict:
    data = copy.deepcopy(SIDECAR)
    data["schema_version"] = version
    anchors = [a for a in data["anchors"] if replace is None or a["fact_key"]["fact_type"] not in replace]
    data["anchors"] = anchors + extra
    return data


def _raw(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


def _write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "population.pop.json.anchors.json"
    path.write_bytes(_raw(data))
    return path


def _check(tmp_path: Path, data: dict) -> dict:
    return check(FIXTURE / "model.orm.yaml", FIXTURE / "population.pop.json",
                 anchors=_write(tmp_path, data), document=FIXTURE / "document.txt", unredacted=True)


def _label_verdict(report: dict) -> dict:
    return next(v for v in report["verdicts"] if "record_has_label" in v["constraint_ref"])


GOOD_WIDE = _anchor(LABEL, 0, 38)
BAD_A = _anchor(LABEL, 40, 60)
BAD_B = _anchor(LABEL, 60, 80)


# T1
def test_two_valid_anchors_on_one_role_pass(tmp_path):
    data = _sidecar([LABEL, GOOD_WIDE], replace={"record_has_label"})
    assert len(parse_anchor_sidecar(_raw(data)).anchors) == len(SIDECAR["anchors"]) + 1
    report = _check(tmp_path, data)
    assert report["exit_code"] == 0
    assert _label_verdict(report)["verdict"] == "pass"
    cli = subprocess.run([sys.executable, "-m", "gnd", "check", str(FIXTURE / "model.orm.yaml"),
                          str(FIXTURE / "population.pop.json"), "--anchors", str(tmp_path / "population.pop.json.anchors.json"),
                          "--document", str(FIXTURE / "document.txt")], capture_output=True, text=True, check=False)
    assert cli.returncode == 0, cli.stdout + cli.stderr


# T2
def _refusal(raw: bytes) -> str:
    with pytest.raises(AnchorError) as caught:
        parse_anchor_sidecar(raw)
    message = str(caught.value)
    assert message.startswith("anchor:sidecar-invalid")
    return message


def _deep(level: int):
    node: object = 0
    for _ in range(level):
        node = [node]
    return node


HOSTILE = {
    "P2-start-equals-end": lambda: _raw(_sidecar([dict(_anchor(LABEL, 0, 38), span={"start": 5, "end": 5})])),
    "P3-over-1MiB": lambda: b" " * (MAX_SIDECAR_BYTES + 1),
    "P4-duplicate-key": lambda: _raw(_sidecar([])).replace(b'"schema_version": 2', b'"schema_version": 2, "schema_version": 2', 1),
    "P5-nan": lambda: _raw(_sidecar([])).replace(b'"record": "R-1"', b'"record": NaN', 1),
    "P6-19-digit-integer": lambda: _raw(_sidecar([dict(_anchor(LABEL, 0, 38), occurrence=10**18)])),
    "P7-depth-33": lambda: _raw(dict(_sidecar([]), anchors=[_deep(33)])),
    "P8-integer-valued-float": lambda: _raw(_sidecar([])).replace(b'"start": 27', b'"start": 27.0', 1),
    "P9-invalid-utf8": lambda: _raw(_sidecar([])).replace(b"Caf\xc3\xa9", b"Caf\xff", 1),
    "non-object-anchor": lambda: _raw(_sidecar(["anchor"])),
}


def test_repeated_identity_and_version_refusals():
    assert "duplicate anchor" in _refusal(_raw(_sidecar([LABEL])))
    other_excerpt = dict(copy.deepcopy(LABEL), excerpt_sha256="0" * 64)
    assert "duplicate anchor" in _refusal(_raw(_sidecar([other_excerpt])))
    # Same span, a different occurrence, names a different range.
    parse_anchor_sidecar(_raw(_sidecar([_anchor(LABEL, 27, 37, occurrence=1)])))
    assert "duplicate fact-role anchor" in _refusal(_raw(_sidecar([GOOD_WIDE], version=1)))
    assert "unsupported sidecar version" in _refusal(_raw(_sidecar([], version=3)))
    # Two faults: the version check runs before the per-anchor duplicate rule.
    assert "unsupported sidecar version" in _refusal(_raw(_sidecar([LABEL], version=3)))


def test_3500_anchors_on_one_role_parse_under_the_cap():
    anchors = [_anchor(LABEL, 27, 37 + k, source=SOURCE + "x" * 3500) for k in range(3500)]
    payload = dict(_sidecar(anchors, replace={"record_has_label"}))
    raw = _canonical(payload) + b"\n"
    assert len(raw) < MAX_SIDECAR_BYTES
    assert len(parse_anchor_sidecar(raw).anchors) == 3500 + len(SIDECAR["anchors"]) - 1


@pytest.mark.parametrize("case", sorted(HOSTILE))
def test_parser_only_rules_refuse(case):
    _refusal(HOSTILE[case]())


# T3, T4
@pytest.mark.parametrize("order", ("bad-first", "bad-last"))
def test_every_anchor_must_bind_and_the_row_is_reported_once(tmp_path, order):
    extra = [BAD_A, BAD_B, LABEL] if order == "bad-first" else [LABEL, BAD_A, BAD_B]
    report = _check(tmp_path, _sidecar(extra, replace={"record_has_label"}))
    assert report["exit_code"] == 1
    verdict = _label_verdict(report)
    assert verdict["verdict"] == "fail"
    assert verdict["offending_facts"] == [{"fact_type": "record_has_label", "roles": {"record": "R-1", "label": "Café Alpha"}}]


def test_bad_anchor_order_gives_identical_output(tmp_path):
    first = _check(tmp_path, _sidecar([BAD_A, BAD_B, LABEL], replace={"record_has_label"}))
    last = _check(tmp_path, _sidecar([LABEL, BAD_A, BAD_B], replace={"record_has_label"}))
    assert first == last


# T5
def test_recogniser_limit_is_the_maximum_occurrence(tmp_path):
    later = _anchor(QUANTITY, QUANTITY["span"]["start"], QUANTITY["span"]["end"], occurrence=1)
    data = _sidecar([later, QUANTITY], replace={"invoice_has_quantity"})
    with patch("gnd.anchors.recognition_index", wraps=recognition_index) as index:
        report = _check(tmp_path, data)
    limits = index.call_args.kwargs["limits"]["integer"]
    assert max(limits.values()) == 1
    # The second occurrence of 1234 does not exist, so that anchor fails the role.
    verdict = next(v for v in report["verdicts"] if "invoice_has_quantity" in v["constraint_ref"])
    assert verdict["verdict"] == "fail"


# T8, T8b
class _Counted(dict):
    reads: typing.ClassVar[dict[str, int]] = {}

    def __getitem__(self, key):
        _Counted.reads[key] = _Counted.reads.get(key, 0) + 1
        return super().__getitem__(key)


def _synthetic(tmp_path: Path, rows: int, document: str):
    model_path = tmp_path / "model.orm.yaml"
    model_path.write_text(
        "version: 2\nmodel_id: urn:gnd-fixture:ct1-scale@1\n"
        "source: {kind: text-conversation, confidence: standard, mode: one-shot}\n"
        "object_types:\n  - {id: record, name: Record, kind: value, primitive: String}\n"
        "  - {id: label, name: Label, kind: value, primitive: String}\n"
        "fact_types:\n  - id: record_has_label\n    reading: \"{Record} has label {Label}\"\n"
        "    roles: [{object_type: record, role_name: record}, {object_type: label, role_name: label}]\n"
        "    constraints:\n      - {type: anchored, role: label, source: explicit, status: confirmed, modality: alethic, provenance: {user_quote: x}}\n"
        "constraints: []\nrejected_proposals: []\n")
    population_path = tmp_path / "population.pop.json"
    population_path.write_text(json.dumps({
        "population": {"model": "model.orm.yaml", "model_id": "urn:gnd-fixture:ct1-scale@1", "label": "conforming",
                       "source": "fixture", "covers": ["record_has_label"]},
        "instances": {},
        "facts": {"record_has_label": [{"record": f"R-{i:04d}", "label": f"L{i:04d}X"} for i in range(rows)]},
    }))
    return load_model(model_path), load_population(population_path), document.encode("utf-8")


def _counted_sidecar(anchors: list[dict]) -> AnchorSidecar:
    counted = []
    for anchor in anchors:
        record = _Counted(anchor)
        dict.__setitem__(record, "fact_key", {"fact_type": anchor["fact_key"]["fact_type"], "roles": dict(anchor["fact_key"]["roles"])})
        counted.append(record)
    return AnchorSidecar(2, "0" * 64, "0" * 64, "0" * 64, tuple(counted))


def test_1000_rows_times_3_anchors_evaluate_each_anchor_once(tmp_path):
    lines = [f"Record R-{i:04d} bears label L{i:04d}X.\n" for i in range(1000)]
    document = "".join(lines) + "end\n"
    model, population, raw = _synthetic(tmp_path, 1000, document)
    anchors, offset = [], 0
    for i, line in enumerate(lines):
        start, end = offset, offset + len(line) - 1
        template = {"fact_key": {"fact_type": "record_has_label", "roles": {"record": f"R-{i:04d}", "label": f"L{i:04d}X"}},
                    "role": "label", "span": {}, "occurrence": 0, "excerpt_sha256": ""}
        anchors += [_anchor(template, start, end, source=document), _anchor(template, start, end + 1, source=document),
                    _anchor(template, start + 1, end, source=document)]
        offset += len(line)
    _Counted.reads = {}
    with patch("gnd.anchors.lexical_ranges", wraps=lexical_ranges) as lexical:
        verdicts = _anchored_verdicts(model, population, _counted_sidecar(anchors), raw)
    assert [v.verdict for v in verdicts.values()] == ["pass"]
    assert _Counted.reads["span"] == 3000
    assert lexical.call_count == 1


def test_anchors_asking_for_different_occurrences_all_bind(tmp_path):
    # The lexical index serves the union of the occurrences the anchors request.
    document = "First L0000X here. Then L0000X again.\n"
    model, population, raw = _synthetic(tmp_path, 1, document)
    template = {"fact_key": {"fact_type": "record_has_label", "roles": {"record": "R-0000", "label": "L0000X"}},
                "role": "label", "span": {}, "occurrence": 0, "excerpt_sha256": ""}
    first, second = document.index("L0000X"), document.rindex("L0000X")
    anchors = [_anchor(template, first, first + 6, occurrence=0, source=document),
               _anchor(template, second, second + 6, occurrence=1, source=document)]
    for ordered in (anchors, anchors[::-1]):
        verdict = next(iter(_anchored_verdicts(model, population, _counted_sidecar(ordered), raw).values()))
        assert verdict.verdict == "pass"


@pytest.mark.parametrize("last_bad", (False, True))
def test_3500_anchors_on_one_row_role(tmp_path, last_bad):
    document = "Record R-0000 bears label L0000X." + " pad" * 1000 + "\n"
    model, population, raw = _synthetic(tmp_path, 1, document)
    template = {"fact_key": {"fact_type": "record_has_label", "roles": {"record": "R-0000", "label": "L0000X"}},
                "role": "label", "span": {}, "occurrence": 0, "excerpt_sha256": ""}
    anchors = [_anchor(template, 0, 33 + k, source=document) for k in range(3500)]
    if last_bad:
        anchors[-1] = _anchor(template, 34, 33 + 3500, source=document)
    _Counted.reads = {}
    verdicts = _anchored_verdicts(model, population, _counted_sidecar(anchors), raw)
    verdict = next(iter(verdicts.values()))
    assert _Counted.reads["span"] == 3500
    # One read per anchor building the lexical index, one per evaluation.
    assert _Counted.reads["occurrence"] == 7000
    assert len(verdict.offending_facts) == (1 if last_bad else 0)


# T11
FIXTURE_SIDECARS = sorted((ROOT / "tests/fixtures").rglob("*.anchors.json"))


def _schema_accepts(raw: bytes) -> bool | None:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        return None
    try:
        jsonschema.validate(value, SCHEMA)
    except jsonschema.ValidationError:
        return False
    return True


def _parser_accepts(raw: bytes) -> bool:
    try:
        parse_anchor_sidecar(raw)
    except AnchorError:
        return False
    return True


def test_schema_and_parser_agree_on_fixture_and_t2_inputs():
    agreed = {
        **{f"fixture:{p.name}": p.read_bytes() for p in FIXTURE_SIDECARS},
        "t1": _raw(_sidecar([LABEL, GOOD_WIDE], replace={"record_has_label"})),
        "v1-fixture-as-v2": _raw(_sidecar([])),
        "version-3": _raw(_sidecar([], version=3)),
        "occurrence-differs": _raw(_sidecar([_anchor(LABEL, 27, 37, occurrence=1)])),
        "non-object-anchor": HOSTILE["non-object-anchor"](),
        # Nesting can only sit where the closed schema refuses it as well.
        "P7-depth-33": HOSTILE["P7-depth-33"](),
    }
    for name, raw in agreed.items():
        assert _schema_accepts(raw) == _parser_accepts(raw), name
    parser_only = {
        "P1-duplicate": _raw(_sidecar([LABEL])),
        "P1-v1-duplicate": _raw(_sidecar([GOOD_WIDE], version=1)),
        **{case: HOSTILE[case]() for case in HOSTILE if case.startswith("P") and case != "P7-depth-33"},
    }
    for name, raw in parser_only.items():
        assert _schema_accepts(raw) in (True, None), name
        assert not _parser_accepts(raw), name


# T12
def test_population_verbalization_shows_distinct_excerpts(tmp_path):
    def run(extra):
        path = _write(tmp_path, _sidecar(extra, replace={"record_has_label"}))
        return subprocess.run([sys.executable, "-m", "gnd", "verbalize", "population", str(FIXTURE / "model.orm.yaml"),
                               str(FIXTURE / "population.pop.json"), "--anchors", str(path),
                               "--document", str(FIXTURE / "document.txt"), "--format", "jsonl", "--unredacted"],
                              capture_output=True, text=True, check=False)
    two = run([LABEL, GOOD_WIDE])
    same = run([LABEL, _anchor(LABEL, 27, 37, occurrence=1)])
    assert two.returncode == 0 and same.returncode == 0, two.stderr + same.stderr
    def label_excerpts(stdout):
        for line in stdout.splitlines():
            row = json.loads(line)
            if row["fact_ref"]["fact_type"] == "record_has_label":
                return row["excerpt"]
        raise AssertionError(stdout)
    assert label_excerpts(two.stdout) == f"label: '{SOURCE[27:37]}'; label: '{SOURCE[0:38]}'"
    assert label_excerpts(same.stdout) == f"label: '{SOURCE[27:37]}'"


def test_export_verification_reads_a_v2_sidecar(tmp_path):
    from test_v70_phase1_surfaces import _verified_anchor_bundle

    model_path, population_path, _document, artifacts = _verified_anchor_bundle(tmp_path)
    sidecar_path = Path(str(population_path) + ".anchors.json")
    data = json.loads(sidecar_path.read_text())
    data["schema_version"] = 2
    data["anchors"].append(GOOD_WIDE)
    sidecar_path.write_text(json.dumps(data))
    run = subprocess.run([sys.executable, "-m", "gnd", "verify", str(model_path), str(population_path),
                          "--artifacts", str(artifacts), "--format", "json"], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    assert [row["verdict"] for row in json.loads(run.stdout)["verdicts"]] == ["pass"] * 7


# T13
def test_customer_mode_redacts_a_v2_failure(tmp_path):
    path = _write(tmp_path, _sidecar([LABEL, BAD_A, BAD_B], replace={"record_has_label"}))
    run = subprocess.run([sys.executable, "-m", "gnd", "check", str(FIXTURE / "model.orm.yaml"),
                          str(FIXTURE / "population.pop.json"), "--anchors", str(path),
                          "--document", str(FIXTURE / "document.txt"), "--format", "json"],
                         capture_output=True, text=True, check=False, env={**os.environ, "GND_DISCLOSURE": "customer"})
    assert run.returncode == 1, run.stdout + run.stderr
    assert "Café Alpha" not in run.stdout and "Café Alpha" not in run.stderr


def test_vocabulary_digest_is_unchanged_by_version():
    model = load_model(FIXTURE / "model.orm.yaml")
    assert vocabulary_digest(model) == SIDECAR["vocabulary_digest"]
