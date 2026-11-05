"""CT2: compose several anchored populations, with a value-free lineage record."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path
from unittest.mock import patch

import jsonschema
import pytest

from gnd import api
from gnd.anchors import vocabulary_digest
from gnd.composition import CompositionError, compose, parse_manifest, parse_record
from gnd.model import load_model

ROOT = Path(__file__).resolve().parents[1]
CANARY = "CANARY-7f3a"

MODEL = """version: 2
model_id: urn:gnd-fixture:ct2-contracts@1
source: {kind: text-conversation, confidence: standard, mode: one-shot}
object_types:
  - {id: contract, name: Contract, kind: value, primitive: String}
  - {id: party, name: Party, kind: value, primitive: String}
  - {id: city, name: City, kind: value, primitive: String}
fact_types:
  - id: contract_has_party
    reading: "{Contract} has party {Party}"
    roles: [{object_type: contract, role_name: contract}, {object_type: party, role_name: party}]
    constraints:
      - {type: anchored, role: party, source: explicit, status: confirmed, modality: %(anchored)s, provenance: {user_quote: x}}
  - id: party_is_based_in_city
    reading: "{Party} is based in {City}"
    roles: [{object_type: party, role_name: party}, {object_type: city, role_name: city}]
    constraints:
      - {type: uniqueness, roles: [party], source: explicit, status: confirmed, modality: %(modality)s, provenance: {user_quote: x}}
constraints: []
rejected_proposals: []
"""

SOURCES = {
    "contract-a": {
        "document": "Contract C-1 is signed by Acme Corp. Acme Corp. is based in Lyon. Note CANARY-7f3a.\n",
        "facts": {"contract_has_party": [{"contract": "C-1", "party": "Acme Corp."}],
                  "party_is_based_in_city": [{"party": "Acme Corp.", "city": "Lyon"}]},
    },
    "contract-b": {
        "document": "Contract C-2 names ACME CORP. as a party. ACME CORP. is based in Lyon. Witness CANARY-7f3a.\n",
        "facts": {"contract_has_party": [{"contract": "C-2", "party": "ACME CORP."},
                                         {"contract": "C-9", "party": CANARY}],
                  "party_is_based_in_city": [{"party": "ACME CORP.", "city": "Lyon"}]},
    },
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _anchors(model, facts, text):
    anchors = []
    for fact_type, rows in facts.items():
        if fact_type != "contract_has_party":
            continue
        for row in rows:
            start = text.index(row["party"])
            end = start + len(row["party"])
            anchors.append({"fact_key": {"fact_type": fact_type, "roles": row}, "role": "party",
                            "span": {"start": start, "end": end}, "occurrence": 0,
                            "excerpt_sha256": _sha(text[start:end].encode("utf-8"))})
    return anchors


def build(tmp_path: Path, *, modality="alethic", anchored="alethic", sources=None, renamings=None, tags=None, order=None) -> tuple[Path, Path]:
    sources = copy.deepcopy(SOURCES if sources is None else sources)
    model_path = tmp_path / "model.orm.yaml"
    model_path.write_text(MODEL % {"modality": modality, "anchored": anchored})
    model = load_model(model_path)
    directory = tmp_path / "composition"
    directory.mkdir()
    for source_id, source in sources.items():
        folder = directory / source_id
        folder.mkdir()
        document = source["document"].encode("utf-8")
        (folder / "document.txt").write_bytes(document)
        population = {"population": {"model": "model.orm.yaml", "model_id": "urn:gnd-fixture:ct2-contracts@1",
                                     "source": "agent-output", "covers": sorted(source["facts"])},
                      "instances": {}, "facts": source["facts"]}
        population_raw = json.dumps(population, ensure_ascii=False).encode("utf-8")
        (folder / "population.json").write_bytes(population_raw)
        text = unicodedata.normalize("NFC", source["document"])
        sidecar = {"schema_version": 2, "population_sha256": _sha(population_raw),
                   "vocabulary_digest": vocabulary_digest(model), "document_sha256": _sha(document),
                   "anchors": source.get("anchors") or _anchors(model, source["facts"], text)}
        (folder / "population.json.anchors.json").write_text(json.dumps(sidecar, ensure_ascii=False))
    manifest = {"schema": "gnd-composition-manifest/1", "sources": order or list(sources),
                "renamings": renamings if renamings is not None else [
                    {"source": "contract-b", "fact_type": "contract_has_party", "role": "party", "from": "ACME CORP.", "to": "Acme Corp."},
                    {"source": "contract-b", "fact_type": "party_is_based_in_city", "role": "party", "from": "ACME CORP.", "to": "Acme Corp."}],
                "deduplications": "identical-rows",
                "scope_tags": tags if tags is not None else [{"source": "contract-a", "tag": "2024-agreement"}]}
    (directory / "manifest.json").write_text(json.dumps(manifest))
    return model_path, directory


def gnd(*argv, env=None):
    return subprocess.run([sys.executable, "-m", "gnd", *map(str, argv)], capture_output=True, text=True,
                          check=False, env={**os.environ, **(env or {})})


def composed(tmp_path, **kwargs):
    model_path, directory = build(tmp_path, **kwargs)
    out, record = tmp_path / "composed.population.json", tmp_path / "composition.json"
    run = gnd("compose", model_path, directory, "--out", out, "--record", record)
    return model_path, directory, out, record, run


def check(model_path, out, record, directory, *extra, env=None):
    return gnd("check", model_path, out, "--composition", record, "--sources", directory, "--format", "json", *extra, env=env)


# T1
def _manifest(**changes):
    base = {"schema": "gnd-composition-manifest/1", "sources": ["a", "b"], "renamings": [],
            "deduplications": "identical-rows", "scope_tags": []}
    base.update(changes)
    return json.dumps(base).encode()


@pytest.mark.parametrize("raw", [
    b"[]", b'{"schema": 1}', _manifest(schema="other"), _manifest(sources=[]), _manifest(sources=["a", "a"]),
    _manifest(sources=["../x"]), _manifest(sources=["a", "A"]), _manifest(sources=["a"], renamings=[{"source": "z", "fact_type": "f", "role": "r", "from": "x", "to": "y"}]),
    _manifest(scope_tags=[{"source": "z", "tag": "t"}]), _manifest(scope_tags=[{"source": "a", "tag": "t" * 129}]),
    _manifest(renamings=[{"source": "a", "fact_type": "f", "role": "r", "from": "x", "to": 1}]),
    _manifest(deduplications="none"),
    _manifest(renamings=[{"source": "a", "fact_type": "f", "role": "r", "from": "x", "to": "y"}] * 2),
    _manifest(extra=1), b'{"schema": "a", "schema": "b"}', b'{"sources": NaN}', b"\xff",
])
def test_manifest_refusals(raw):
    with pytest.raises(CompositionError, match="^composition:invalid"):
        parse_manifest(raw)


def test_manifest_accepts_the_plan_example():
    assert parse_manifest(_manifest()).sources == ("a", "b")


# T2
def test_record_refusals(tmp_path):
    *_, record, run = composed(tmp_path)
    assert run.returncode == 0, run.stderr
    good = json.loads(record.read_text())
    parse_record(record.read_bytes())
    for mutate in (
        lambda r: r.update(schema="x"), lambda r: r.update(model_sha256="0"), lambda r: r.update(sources=[]),
        lambda r: r["sources"][0].update(id="../x"), lambda r: r["facts"][0].update(sources=[]),
        lambda r: r["facts"][0].update(renamings=[-1]), lambda r: r["facts"][0]["sources"][0].update(fact_index=1.0),
        lambda r: r.update(extra=1),
    ):
        bad = copy.deepcopy(good)
        mutate(bad)
        with pytest.raises(CompositionError):
            parse_record(json.dumps(bad).encode())


# T3, T4, T7
def test_compose_renames_deduplicates_and_records_lineage(tmp_path):
    model_path, directory, out, record_path, run = composed(tmp_path)
    assert run.returncode == 0, run.stderr
    population = json.loads(out.read_text())
    record = json.loads(record_path.read_text())
    assert population["facts"]["contract_has_party"] == [
        {"contract": "C-1", "party": "Acme Corp."}, {"contract": "C-2", "party": "Acme Corp."},
        {"contract": "C-9", "party": CANARY}]
    assert population["facts"]["party_is_based_in_city"] == [{"party": "Acme Corp.", "city": "Lyon"}]
    lineage = {(f["fact_type"], f["index"]): f for f in record["facts"]}
    city = lineage[("party_is_based_in_city", 0)]
    assert city["sources"] == [{"source": "contract-a", "fact_type": "party_is_based_in_city", "fact_index": 0},
                               {"source": "contract-b", "fact_type": "party_is_based_in_city", "fact_index": 0}]
    assert city["renamings"] == [1]
    assert lineage[("contract_has_party", 0)]["renamings"] == []
    assert lineage[("contract_has_party", 1)]["renamings"] == [0]
    assert record["scope_tags"] == [{"source": "contract-a", "tag": "2024-agreement"}]
    assert record["model_sha256"] == _sha(model_path.read_bytes())
    assert record["manifest_sha256"] == _sha((directory / "manifest.json").read_bytes())
    assert record["population_sha256"] == _sha(out.read_bytes())
    for source in record["sources"]:
        folder = directory / source["id"]
        assert source == {"id": source["id"], "population_sha256": _sha((folder / "population.json").read_bytes()),
                          "sidecar_sha256": _sha((folder / "population.json.anchors.json").read_bytes()),
                          "document_sha256": _sha((folder / "document.txt").read_bytes())}
    jsonschema.validate(record, json.loads((ROOT / "src/gnd/composition.schema.json").read_text()))
    jsonschema.validate(json.loads((directory / "manifest.json").read_text()),
                        json.loads((ROOT / "src/gnd/composition-manifest.schema.json").read_text()))


# T5
def test_composition_is_deterministic_and_ordered(tmp_path):
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    (tmp_path / "swap").mkdir()
    first = composed(tmp_path / "one")
    second = composed(tmp_path / "two")
    swapped = composed(tmp_path / "swap", order=["contract-b", "contract-a"])
    assert first[2].read_bytes() == second[2].read_bytes()
    assert first[3].read_bytes() == second[3].read_bytes()
    assert first[2].read_bytes() != swapped[2].read_bytes()
    assert json.loads(first[3].read_text())["facts"] != json.loads(swapped[3].read_text())["facts"]


# T6
def test_fifty_sources_of_2000_facts_are_linear(tmp_path):
    from gnd import composition as module

    sources = {}
    for s in range(50):
        rows = [{"contract": f"C-{s}-{i}", "party": "Acme Corp."} for i in range(2000)]
        sources[f"s{s:02d}"] = {"document": "Acme Corp. signs.\n", "facts": {"contract_has_party": rows},
                                "anchors": []}
    model_path, directory = build(tmp_path, sources=sources, renamings=[], tags=[])
    model = load_model(model_path)
    visits = {"rows": 0, "probes": 0}
    real_key = module._row_key

    def counted_key(row):
        visits["rows"] += 1
        return real_key(row)

    class CountingDict(dict):
        def get(self, key, default=None):
            visits["probes"] += 1
            return super().get(key, default)

    with patch.object(module, "_row_key", counted_key), patch.object(module, "_positions_factory", CountingDict):
        result = compose(model, model_path.read_bytes(), directory)
    assert len(result.record["facts"]) == 100_000
    assert visits["rows"] == 100_000
    assert visits["probes"] == 100_000


# T8, T13
@pytest.mark.parametrize("modality", ("alethic", "deontic"))
def test_check_names_both_source_facts_of_a_conflict(tmp_path, modality):
    sources = copy.deepcopy(SOURCES)
    sources["contract-b"]["facts"]["party_is_based_in_city"] = [{"party": "ACME CORP.", "city": "Paris"}]
    sources["contract-b"]["document"] = sources["contract-b"]["document"].replace("Lyon", "Paris")
    model_path, directory, out, record, run = composed(tmp_path, modality=modality, sources=sources)
    assert run.returncode == 0, run.stderr
    result = check(model_path, out, record, directory)
    payload = json.loads(result.stdout)
    assert result.returncode == (1 if modality == "alethic" else 0), result.stdout
    lineage = {(f["fact_type"], f["index"]): f["sources"] for f in payload["composition"]["lineage"]}
    assert lineage == {
        ("party_is_based_in_city", 0): [{"source": "contract-a", "fact_type": "party_is_based_in_city", "fact_index": 0}],
        ("party_is_based_in_city", 1): [{"source": "contract-b", "fact_type": "party_is_based_in_city", "fact_index": 0}],
    }
    text = gnd("check", model_path, out, "--composition", record, "--sources", directory)
    assert "lineage party_is_based_in_city#1: contract-b:party_is_based_in_city#0" in text.stdout


def test_unedited_composition_checks_clean(tmp_path):
    model_path, directory, out, record, _run = composed(tmp_path)
    result = check(model_path, out, record, directory)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["composition"]["lineage"] == []
    assert payload["composition"]["record_sha256"] == _sha(record.read_bytes())
    anchored = [v for v in payload["verdicts"] if v["constraint_type"] == "anchored"]
    assert [v["verdict"] for v in anchored] == ["pass"]


# T9, T11
def _edit_json(path, change):
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


EDITS = {
    "record": lambda d, o, r: _edit_json(r, lambda x: x["scope_tags"].append({"source": "contract-a", "tag": "x"})),
    "population": lambda d, o, r: o.write_bytes(o.read_bytes() + b" "),
    "document": lambda d, o, r: (d / "contract-b" / "document.txt").write_text("changed\n"),
    "manifest": lambda d, o, r: _edit_json(d / "manifest.json", lambda x: x["scope_tags"].clear()),
    "lineage": lambda d, o, r: _edit_json(r, lambda x: x["facts"][0]["sources"].reverse() or x["facts"][0]["sources"].append(x["facts"][0]["sources"][0])),
    "missing-source-file": lambda d, o, r: (d / "contract-a" / "population.json").unlink(),
}


@pytest.mark.parametrize("edit", sorted(EDITS))
def test_check_refuses_each_kind_of_drift(tmp_path, edit):
    model_path, directory, out, record, _run = composed(tmp_path)
    EDITS[edit](directory, out, record)
    result = check(model_path, out, record, directory)
    assert result.returncode == 3, (edit, result.stdout)
    assert "composition:invalid" in result.stdout
    assert CANARY not in result.stdout + result.stderr


# T10, T11
def test_compose_refusals_name_no_value(tmp_path):
    cases = {
        "unused": {"renamings": [{"source": "contract-a", "fact_type": "contract_has_party", "role": "party", "from": "Nobody", "to": "X"}]},
        "undeclared-role": {"renamings": [{"source": "contract-a", "fact_type": "contract_has_party", "role": "city", "from": "x", "to": "y"}]},
    }
    for name, kwargs in cases.items():
        (tmp_path / name).mkdir()
        *_, out, record, run = composed(tmp_path / name, **kwargs)
        assert run.returncode == 3, (name, run.stderr)
        assert "composition:invalid" in run.stderr and CANARY not in run.stderr
        assert not out.exists() and not record.exists()
    (tmp_path / "reference").mkdir()
    model_path, directory = build(tmp_path / "reference")
    model = load_model(model_path).model_copy(update={"reference_populations": [{"id": "r"}]})
    with pytest.raises(CompositionError, match="reference populations"):
        compose(model, model_path.read_bytes(), directory)


def test_record_bytes_carry_no_role_value(tmp_path):
    *_, record, run = composed(tmp_path)
    assert run.returncode == 0
    raw = record.read_text()
    for value in (CANARY, "Acme", "ACME", "Lyon", "C-1"):
        assert value not in raw


# T12
def test_api_mirrors_the_cli(tmp_path):
    model_path, directory, out, record, _run = composed(tmp_path)
    payload = api.compose(model_path, directory)
    assert payload["exit_code"] == 0
    assert payload["record"] == json.loads(record.read_text())
    assert payload["population"] == json.loads(out.read_text())
    cli = json.loads(check(model_path, out, record, directory).stdout)
    assert api.check(model_path, out, composition=record, sources=directory) == cli
    assert api.check(model_path, out, composition=json.loads(record.read_text()), sources=directory) == cli
    with pytest.raises(ValueError):
        api.check(model_path, out, composition=record)
    with pytest.raises(TypeError):
        api.compose(load_model(model_path), directory)


# T14
@pytest.mark.parametrize("extra", (["--composition", "r.json"], ["--sources", "d"],
                                   ["--composition", "r.json", "--sources", "d", "--anchors", "a", "--document", "b"]))
def test_option_conflicts_are_usage_errors(tmp_path, extra):
    model_path, directory = build(tmp_path)
    result = gnd("check", model_path, directory / "contract-a" / "population.json", *extra)
    assert result.returncode == 64


# T15
def test_renamed_value_is_checked_against_its_own_source(tmp_path):
    (tmp_path / "good").mkdir()
    good = composed(tmp_path / "good")
    assert check(good[0], good[2], good[3], good[1]).returncode == 0
    bad_sources = copy.deepcopy(SOURCES)
    text = bad_sources["contract-b"]["document"]
    row = bad_sources["contract-b"]["facts"]["contract_has_party"][0]
    start = text.index("as a party")
    bad_sources["contract-b"]["anchors"] = [
        {"fact_key": {"fact_type": "contract_has_party", "roles": row}, "role": "party",
         "span": {"start": start, "end": start + 10}, "occurrence": 0,
         "excerpt_sha256": _sha(text[start:start + 10].encode())},
        *[a for a in _anchors(None, bad_sources["contract-b"]["facts"], text) if a["fact_key"]["roles"] != row],
    ]
    (tmp_path / "bad").mkdir()
    model_path, directory, out, record, run = composed(tmp_path / "bad", sources=bad_sources)
    assert run.returncode == 0, run.stderr
    result = check(model_path, out, record, directory)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["composition"]["lineage"] == [
        {"fact_type": "contract_has_party", "index": 1,
         "sources": [{"source": "contract-b", "fact_type": "contract_has_party", "fact_index": 0}]}]
    customer = check(model_path, out, record, directory, env={"GND_DISCLOSURE": "customer"})
    assert customer.returncode == 1
    assert json.loads(customer.stdout)["composition"] == payload["composition"]


# Review fixes (CT2 review F1..F8, F11)
def test_api_refuses_population_bytes_with_a_composition(tmp_path):
    model_path, directory, out, record, _run = composed(tmp_path)
    with pytest.raises(ValueError):
        api.check(model_path, out, population_bytes=out.read_bytes(), composition=record, sources=directory)
    nan = json.loads(record.read_text())
    nan["scope_tags"] = [{"source": "contract-a", "tag": float("nan")}]
    assert api.check(model_path, out, composition=nan, sources=directory)["exit_code"] == 3


def test_a_row_without_lineage_fails_its_anchored_constraint(tmp_path):
    from gnd.checker import check_with_composed_anchors
    from gnd.composition import lineage_index
    from gnd.population import load_population

    model_path, directory, out, _record_path, _run = composed(tmp_path)
    model = load_model(model_path)
    population = load_population(out, model=model)
    derived = compose(model, model_path.read_bytes(), directory)
    lineage = lineage_index(derived.record)
    del lineage[("contract_has_party", 0)]
    report = check_with_composed_anchors(model, population, sources=derived.sources, lineage=lineage)
    anchored = next(v for v in report.verdicts if v.constraint_type == "anchored")
    assert anchored.verdict == "fail"
    assert anchored.fact_refs == [{"fact_type": "contract_has_party", "index": 0}]


def test_a_renaming_also_renames_the_sources_instances(tmp_path):
    sources = copy.deepcopy(SOURCES)
    model_path, directory = build(tmp_path, sources=sources)
    population_path = directory / "contract-b" / "population.json"
    data = json.loads(population_path.read_text())
    data["instances"] = {"party": ["ACME CORP."]}
    population_path.write_text(json.dumps(data, ensure_ascii=False))
    sidecar_path = directory / "contract-b" / "population.json.anchors.json"
    sidecar = json.loads(sidecar_path.read_text())
    sidecar["population_sha256"] = _sha(population_path.read_bytes())
    sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False))
    result = compose(load_model(model_path), model_path.read_bytes(), directory)
    assert json.loads(result.population_bytes)["instances"] == {"party": ["Acme Corp."]}


def _with_instances(directory, source_id, instances):
    population_path = directory / source_id / "population.json"
    data = json.loads(population_path.read_text())
    data["instances"] = instances
    population_path.write_text(json.dumps(data, ensure_ascii=False))
    sidecar_path = directory / source_id / "population.json.anchors.json"
    sidecar = json.loads(sidecar_path.read_text())
    sidecar["population_sha256"] = _sha(population_path.read_bytes())
    sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False))


def _renaming(fact_type, source="contract-b", old="ACME CORP.", new="Acme Corp."):
    return {"source": source, "fact_type": fact_type, "role": "party", "from": old, "to": new}


@pytest.mark.parametrize("renamings, message", [
    # Close review: a renaming that only hits an instance matches no row.
    ([_renaming("contract_has_party"), _renaming("party_is_based_in_city"),
      _renaming("contract_has_party", old="Ghost")], "renaming 2 matches no row"),
    # One value of one object type cannot become two values.
    ([_renaming("contract_has_party"), _renaming("party_is_based_in_city", new="Acme Inc.")],
     "renamings 0 and 1 rename one value to different values"),
    # Renaming an instance that another fact type still uses would split it.
    ([_renaming("contract_has_party")], "another role of that source still uses unrenamed"),
])
def test_instance_renamings_are_never_inferred_past_the_rows(tmp_path, renamings, message):
    model_path, directory = build(tmp_path, renamings=renamings)
    _with_instances(directory, "contract-b", {"party": ["ACME CORP.", "Ghost"]})
    with pytest.raises(CompositionError, match=message):
        compose(load_model(model_path), model_path.read_bytes(), directory)


@pytest.mark.parametrize("outputs", ("same", "inside", "model"))
def test_compose_refuses_unsafe_outputs(tmp_path, outputs):
    model_path, directory = build(tmp_path)
    before = model_path.read_bytes()
    out = directory / "x.json" if outputs == "inside" else tmp_path / "x.json"
    record = {"same": tmp_path / "x.json", "model": model_path}.get(outputs, tmp_path / "r.json")
    run = gnd("compose", model_path, directory, "--out", out, "--record", record)
    assert run.returncode == 64
    assert not out.exists()
    assert model_path.read_bytes() == before


def test_compose_writes_neither_output_when_one_target_is_a_directory(tmp_path):
    model_path, directory = build(tmp_path)
    out, record = tmp_path / "x.json", tmp_path / "adir"
    out.write_text("old")
    record.mkdir()
    run = gnd("compose", model_path, directory, "--out", out, "--record", record)
    assert run.returncode == 74
    assert out.read_text() == "old"


def test_compose_outputs_take_the_umask_mode(tmp_path):
    _model_path, _directory, out, record, run = composed(tmp_path)
    assert run.returncode == 0
    umask = os.umask(0)
    os.umask(umask)
    assert {out.stat().st_mode & 0o777, record.stat().st_mode & 0o777} == {0o666 & ~umask}


def test_compose_refuses_a_record_over_its_cap(tmp_path, monkeypatch):
    from gnd import composition as module

    model_path, directory = build(tmp_path)
    monkeypatch.setattr(module, "MAX_RECORD_BYTES", 100)
    with pytest.raises(CompositionError, match="16 MiB"):
        compose(load_model(model_path), model_path.read_bytes(), directory)


def test_admission_is_excluded(tmp_path):
    model_path, directory, out, record, _run = composed(tmp_path)
    assert check(model_path, out, record, directory, "--admission").returncode == 64


@pytest.mark.parametrize("field", ("sources", "manifest_sha256", "scope_tags", "facts", "model_sha256"))
def test_verify_compares_every_record_field(tmp_path, field):
    from gnd.composition import verify_composition

    model_path, directory, out, record_path, _run = composed(tmp_path)
    record = json.loads(record_path.read_text())
    forged = {
        "sources": lambda r: r["sources"][0].update(sidecar_sha256="0" * 64),
        "manifest_sha256": lambda r: r.update(manifest_sha256="0" * 64),
        "scope_tags": lambda r: r["scope_tags"].clear(),
        "facts": lambda r: r["facts"][0]["sources"].append(r["facts"][0]["sources"][0]),
        "model_sha256": lambda r: r.update(model_sha256="0" * 64),
    }
    forged[field](record)
    with pytest.raises(CompositionError, match=field.split("_")[0] if field != "facts" else "facts"):
        verify_composition(load_model(model_path), model_path.read_bytes(), out.read_bytes(), record, directory)


def test_verify_compares_the_composed_bytes(tmp_path):
    from gnd.composition import verify_composition

    model_path, directory, out, record_path, _run = composed(tmp_path)
    record = json.loads(record_path.read_text())
    edited = out.read_bytes().replace(b"Lyon", b"Lyom")
    record["population_sha256"] = _sha(edited)
    with pytest.raises(CompositionError, match="bytes differ"):
        verify_composition(load_model(model_path), model_path.read_bytes(), edited, record, directory)


def test_covers_are_the_ordered_union(tmp_path):
    sources = copy.deepcopy(SOURCES)
    del sources["contract-a"]["facts"]["party_is_based_in_city"]
    model_path, directory = build(tmp_path, sources=sources, renamings=[
        {"source": "contract-b", "fact_type": "contract_has_party", "role": "party", "from": "ACME CORP.", "to": "Acme Corp."}])
    result = compose(load_model(model_path), model_path.read_bytes(), directory)
    assert json.loads(result.population_bytes)["population"]["covers"] == ["contract_has_party", "party_is_based_in_city"]


def _anchored_after(tmp_path, sources, **kwargs):
    model_path, directory, out, record, run = composed(tmp_path, sources=sources, **kwargs)
    assert run.returncode == 0, run.stderr
    payload = json.loads(check(model_path, out, record, directory).stdout)
    return next(v for v in payload["verdicts"] if v["constraint_type"] == "anchored"), payload


def _bad_anchor(source, row):
    text = source["document"]
    start = text.index("CANARY")
    return {"fact_key": {"fact_type": "contract_has_party", "roles": row}, "role": "party",
            "span": {"start": start, "end": start + 6}, "occurrence": 0,
            "excerpt_sha256": _sha(text[start:start + 6].encode())}


def test_a_failing_second_source_fails_a_deduplicated_fact(tmp_path):
    sources = copy.deepcopy(SOURCES)
    shared = {"contract": "C-1", "party": "Acme Corp."}
    sources["contract-b"]["document"] += "Contract C-1 also binds Acme Corp. here.\n"
    sources["contract-b"]["facts"]["contract_has_party"].append(shared)
    good = [a for a in _anchors(None, sources["contract-b"]["facts"], sources["contract-b"]["document"]) if a["fact_key"]["roles"] != shared]
    sources["contract-b"]["anchors"] = [*good, _bad_anchor(sources["contract-b"], shared)]
    verdict, payload = _anchored_after(tmp_path, sources)
    assert verdict["verdict"] == "fail"
    lineage = {(f["fact_type"], f["index"]): f["sources"] for f in payload["composition"]["lineage"]}
    assert [s["source"] for s in lineage[("contract_has_party", 0)]] == ["contract-a", "contract-b"]


@pytest.mark.parametrize("anchored", ("alethic", "deontic"))
def test_a_failing_anchor_fails_or_warns_by_modality(tmp_path, anchored):
    sources = copy.deepcopy(SOURCES)
    row = sources["contract-b"]["facts"]["contract_has_party"][0]
    sources["contract-a"]["anchors"] = [{"fact_key": {"fact_type": "contract_has_party", "roles": r}, "role": "party",
                                         "span": {"start": 0, "end": 5}, "occurrence": 0,
                                         "excerpt_sha256": _sha(sources["contract-a"]["document"][:5].encode())}
                                        for r in sources["contract-a"]["facts"]["contract_has_party"]]
    sources["contract-b"]["anchors"] = [_bad_anchor(sources["contract-b"], row),
                                        *[a for a in _anchors(None, sources["contract-b"]["facts"], sources["contract-b"]["document"]) if a["fact_key"]["roles"] != row]]
    verdict, _ = _anchored_after(tmp_path, sources, anchored=anchored)
    assert verdict["verdict"] == ("fail" if anchored == "alethic" else "warning")


def test_an_empty_composed_fact_type_is_vacuous(tmp_path):
    sources = copy.deepcopy(SOURCES)
    for source in sources.values():
        source["facts"]["contract_has_party"] = []
        source["anchors"] = []
    verdict, _ = _anchored_after(tmp_path, sources, renamings=[
        {"source": "contract-b", "fact_type": "party_is_based_in_city", "role": "party", "from": "ACME CORP.", "to": "Acme Corp."}])
    assert verdict["verdict"] == "vacuous"


def test_a_reserialized_record_is_refused(tmp_path):
    # Close review: one record has one identity, so a re-indented record is
    # refused rather than checked under one digest and witnessed under another.
    model_path, directory, out, record, run = composed(tmp_path)
    assert run.returncode == 0
    record.write_text(json.dumps(json.loads(record.read_text()), indent=2))
    with pytest.raises(CompositionError, match="canonical form"):
        parse_record(record.read_bytes())
    assert check(model_path, out, record, directory).returncode == 3


def test_compose_compares_outputs_by_identity(tmp_path):
    # Close re-review: a case variant of the model or the directory is the same
    # file on a case-insensitive filesystem, so it is refused everywhere for the
    # model and wherever the filesystem folds case for the directory.
    model_path, directory = build(tmp_path)
    before = model_path.read_bytes()
    run = gnd("compose", model_path, directory, "--out", tmp_path / "x.json", "--record", tmp_path / "MODEL.ORM.YAML")
    assert run.returncode == 64 and model_path.read_bytes() == before
    if (tmp_path / "COMPOSITION").exists():
        run = gnd("compose", model_path, directory, "--out", tmp_path / "x.json",
                  "--record", tmp_path / "COMPOSITION" / "r.json")
        assert run.returncode == 64 and not (directory / "r.json").exists()
