from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from gnd import api
from gnd.extract.anchors import AnchorError, bind_anchors, read_anchor_sidecar
from gnd.model import load_model
from gnd.population import load_population

FIXTURE = Path(__file__).parent / "fixtures/v70-phase5"

CASES = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))

ANSWERS = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))

CASE_IDS = tuple(row["id"] for row in CASES["cases"])

WITNESS_IDS = tuple(row["id"] for row in CASES["witnesses"])

def test_models_populations_and_anchor_sidecars_are_loader_valid() -> None:
    for stem in ("public", "private"):
        model = load_model(FIXTURE / f"{stem}.orm.yaml")
        population_path = FIXTURE / f"{stem}.pop.json"
        population = load_population(population_path, model=model)
        sidecar = read_anchor_sidecar(str(population_path) + ".anchors.json")
        source = bind_anchors(
            sidecar, model, population_path.read_bytes(),
            (FIXTURE / f"{stem}-source.txt").read_bytes(), population,
        )
        assert source
        dirty = replace(sidecar, document_sha256="0" * 64)
        with pytest.raises(AnchorError, match="binding-mismatch"):
            bind_anchors(
                dirty, model, population_path.read_bytes(),
                (FIXTURE / f"{stem}-source.txt").read_bytes(), population,
            )
    public_model = load_model(FIXTURE / "public.orm.yaml")
    assert load_model(FIXTURE / "bad-inverse.orm.yaml")
    for stem in ("public-shuffled", "public-empty"):
        load_population(FIXTURE / f"{stem}.pop.json", model=public_model)
    public = json.loads((FIXTURE / "public.pop.json").read_text())
    assert public["facts"]["b_pair"][1] == public["facts"]["b_pair"][2]
    assert type(public["facts"]["c_amount"][0]["amount"]) is float
    assert type(public["facts"]["c_amount"][1]["amount"]) is int

@pytest.mark.parametrize("case_id", CASE_IDS)
@pytest.mark.parametrize("fmt", ("text", "jsonl"))
def test_runtime_case_is_red_until_the_lane_exists(case_id: str, fmt: str) -> None:
    assert callable(getattr(api, "verbalize", None)), "Phase 5 API lane is not implemented"
    case = next(row for row in CASES["cases"] if row["id"] == case_id)
    answer = ANSWERS["cases"][case_id]
    command = [
        sys.executable, "-m", "gnd", "verbalize", "population",
        str(FIXTURE / case["model"]), str(FIXTURE / case["population"]),
        "--format", fmt,
    ]
    if "anchors" in case:
        command.extend(("--anchors", str(FIXTURE / case["anchors"])))
    if "document" in case:
        command.extend(("--document", str(FIXTURE / case["document"])))
    if case.get("unredacted"):
        command.append("--unredacted")
    result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
    assert result.returncode == answer["exit"], (case_id, fmt, result.stderr[:500])
    assert result.stdout == answer[fmt], (case_id, fmt, result.stdout[:500])
    assert "Traceback" not in result.stderr

@pytest.mark.parametrize("witness_id", WITNESS_IDS)
def test_witness_case_is_red_until_the_lane_exists(witness_id: str) -> None:
    module = importlib.import_module("gnd.verbalize_population")
    case = next(row for row in CASES["witnesses"] if row["id"] == witness_id)
    model = load_model(FIXTURE / case["model"])
    answer = ANSWERS["witnesses"][witness_id]
    if "sentence" in answer:
        assert module.render_witness(model, case["fact_type"], case["binding"]) == answer["sentence"]
    else:
        with pytest.raises(module.PopulationVerbalizationError, match=answer["error"]):
            module.render_witness(model, case["fact_type"], case["binding"])

def test_api_projection_is_red_until_the_lane_exists() -> None:
    assert callable(getattr(api, "verbalize", None)), "Phase 5 API lane is not implemented"
    inputs = {
        "anchors": str(FIXTURE / "private.pop.json.anchors.json"),
        "document": str(FIXTURE / "private-source.txt"),
    }
    for unredacted, case_id in ((False, "R01-private-applied"), (True, "R02-private-unredacted")):
        result = api.verbalize(
            FIXTURE / "private.orm.yaml", FIXTURE / "private.pop.json",
            unredacted=unredacted, **inputs,
        )
        assert result == {
            "rows": ANSWERS["cases"][case_id]["rows"],
            "exit_code": 0,
            "error": None,
        }

import copy

ANSWERS["file_sha256"] = json.loads((FIXTURE / "public-input-sha256.json").read_text())

EXPECTED_CASE_IDS = ('P01-public', 'P02-public-anchored', 'O01-shuffled', 'Z01-empty', 'R01-private-applied', 'R02-private-unredacted', 'I01-bare-ternary-inverse', 'A01-mutated-document', 'U01-unpaired-anchors')

EXPECTED_EXITS = {'P01-public': 0, 'P02-public-anchored': 0, 'O01-shuffled': 0, 'Z01-empty': 0, 'R01-private-applied': 0, 'R02-private-unredacted': 0, 'I01-bare-ternary-inverse': 3, 'A01-mutated-document': 3, 'U01-unpaired-anchors': 64}

TEXT_SHA256 = {'P01-public': '178a38c914c7eab92586f5d059178e3363f908341a27d2c08c39d0d25e8057e7', 'P02-public-anchored': '1988a7044fe85c8509a9f2687004ee92ba74d13acb945427a81236a7f3276e6c', 'R01-private-applied': '5a8789f9aa70704c024e925f30282a30e132ccc98eef3d0e03bb5114489b0bc0', 'R02-private-unredacted': '4d9fe10ac5aa8f422dc4bdaa82c2654d19a3d45888737b2985ed3182880db2d7'}

def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def _row_text(row: dict) -> str:
    ref = row['fact_ref']
    suffix = f" | excerpt: {row['excerpt']}" if 'excerpt' in row else ''
    return f"FACT {ref['fact_type']}[{ref['index']}]: {row['sentence']}{suffix}\n"

def verify_answer_key(cases: dict, answers: dict) -> None:
    """Check fixed input meanings, exact wire bytes, and the corpus digest map."""
    assert cases['schema_version'] == answers['schema_version'] == 1
    assert tuple(row['id'] for row in cases['cases']) == EXPECTED_CASE_IDS
    assert set(answers['cases']) == set(EXPECTED_CASE_IDS)
    assert tuple(row['id'] for row in cases['witnesses']) == ('W01-complete', 'W02-partial')
    inputs = {p.name for p in FIXTURE.iterdir() if p.is_file() and p.name not in {'answers.json', 'public-input-sha256.json'}}
    assert set(answers['file_sha256']) == inputs
    for name in inputs:
        assert answers['file_sha256'][name] == _sha((FIXTURE / name).read_bytes())
    by_id = {row['id']: row for row in cases['cases']}
    assert by_id['P01-public'] == {'id': 'P01-public', 'model': 'public.orm.yaml', 'population': 'public.pop.json'}
    assert by_id['P02-public-anchored']['anchors'] == 'public.pop.json.anchors.json'
    assert by_id['P02-public-anchored']['document'] == 'public-source.txt'
    assert by_id['O01-shuffled']['population'] == 'public-shuffled.pop.json'
    assert by_id['Z01-empty']['population'] == 'public-empty.pop.json'
    assert by_id['R01-private-applied']['model'] == 'private.orm.yaml'
    assert by_id['R01-private-applied']['document'] == 'private-source.txt'
    assert by_id['R02-private-unredacted']['unredacted'] is True
    assert by_id['I01-bare-ternary-inverse']['model'] == 'bad-inverse.orm.yaml'
    assert by_id['A01-mutated-document']['document'] == 'public-source-mutated.txt'
    assert 'document' not in by_id['U01-unpaired-anchors']
    for case_id, expected_exit in EXPECTED_EXITS.items():
        answer = answers['cases'][case_id]
        assert answer['exit'] == expected_exit
        rows = answer['rows']
        assert answer['text'] == ''.join(_row_text(row) for row in rows)
        assert answer['jsonl'] == ''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n' for row in rows)
        if expected_exit:
            assert rows == [] and answer['text'] == answer['jsonl'] == ''
        for row in rows:
            assert set(row) in ({'fact_ref', 'sentence'}, {'fact_ref', 'sentence', 'excerpt'})
            assert set(row['fact_ref']) == {'fact_type', 'index'}
            assert '\n' not in row['sentence'] and '\u2028' not in row['sentence']
    for case_id, digest in TEXT_SHA256.items():
        assert _sha(answers['cases'][case_id]['text'].encode()) == digest
    public = answers['cases']['P01-public']['rows']
    anchored = answers['cases']['P02-public-anchored']['rows']
    shuffled = answers['cases']['O01-shuffled']['rows']
    assert len(public) == len(anchored) == len(shuffled) == 14
    assert [row['sentence'] for row in shuffled] == [row['sentence'] for row in public]
    assert [row['fact_ref']['index'] for row in public if row['fact_ref']['fact_type'] == 'b_pair'] == [1, 1, 2, 2, 0, 0]
    assert [row['fact_ref']['index'] for row in shuffled if row['fact_ref']['fact_type'] == 'b_pair'] == [0, 0, 1, 1, 2, 2]
    assert [row['fact_ref']['index'] for row in public if row['fact_ref']['fact_type'] == 'd_token'] == [1, 2, 0]
    assert sum('excerpt' in row for row in anchored) == 4
    assert all('excerpt' not in row for row in public)
    assert answers['cases']['Z01-empty']['rows'] == []
    assert '\\u2028' in public[0]['sentence']
    assert '<b>{Person}</b>' in public[0]['sentence']
    assert '[opaque: a-unreadable]' in answers['cases']['P01-public']['text']
    applied = answers['cases']['R01-private-applied']['text']
    unredacted = answers['cases']['R02-private-unredacted']['text']
    assert 'SECRET-ROLE-CANARY' not in applied
    assert 'SECRET-OPAQUE-CANARY' not in applied
    assert 'SECRET-ROLE-CANARY' in unredacted
    assert 'SECRET-OPAQUE-CANARY' in unredacted
    assert all('excerpt' not in row for row in answers['cases']['R01-private-applied']['rows'])
    assert any('excerpt' in row for row in answers['cases']['R02-private-unredacted']['rows'])
    assert answers['witnesses'] == {'W01-complete': {'sentence': "'Ada' meets 'Zoe'."}, 'W02-partial': {'error': 'incomplete binding'}}

def test_answer_key_is_bound_and_discriminating() -> None:
    verify_answer_key(CASES, ANSWERS)

def test_known_dirty_answer_is_rejected() -> None:
    dirty = copy.deepcopy(ANSWERS)
    dirty['cases']['P01-public']['rows'][0]['sentence'] = 'wrong sentence'
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)
    dirty = copy.deepcopy(ANSWERS)
    dirty['cases']['R01-private-applied']['text'] += 'SECRET-ROLE-CANARY'
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)
    dirty = copy.deepcopy(ANSWERS)
    dirty['cases']['I01-bare-ternary-inverse']['exit'] = 0
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)

def test_known_dirty_input_is_rejected() -> None:
    dirty = copy.deepcopy(CASES)
    dirty['cases'][0]['population'] = 'private.pop.json'
    with pytest.raises(AssertionError):
        verify_answer_key(dirty, ANSWERS)
    dirty = copy.deepcopy(ANSWERS)
    dirty['file_sha256']['public-source.txt'] = '0' * 64
    with pytest.raises(AssertionError):
        verify_answer_key(CASES, dirty)
