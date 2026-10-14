"""Frozen hand-narrated policy controls, separately from native execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gnd.api import check

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/pyrel_applications"
MATRIX = json.loads((CORPUS / "matrix.json").read_text())
ANSWERS = json.loads((CORPUS / "answers.json").read_text())


def test_matrix_exhausts_exact_models_and_controls():
    actual = set()
    metadata = {}
    for name in MATRIX["models"]:
        model = ROOT / "src/gnd/examples" / name
        doc = json.loads(model.read_text())
        entries = [f"fact_types[{f['id']}].constraints[{i}]"
                   for f in doc["fact_types"] for i, _ in enumerate(f.get("constraints", []))]
        entries += [f"constraints[{i}]" for i, _ in enumerate(doc.get("constraints", []))]
        entries += ["derivation:" + f["id"] for f in doc["fact_types"]
                    if f.get("derivation") == "derived"]
        actual.update((name, ref) for ref in entries)
        for f in doc['fact_types']:
            for i, c in enumerate(f.get('constraints', [])):
                ref = f"fact_types[{f['id']}].constraints[{i}]"
                metadata[name, ref] = (c['type'], c.get('modality', 'alethic'), c.get('id', ref))
            if f.get('derivation') == 'derived':
                metadata[name, 'derivation:' + f['id']] = ('derivation', 'alethic', f['id'])
        for i, c in enumerate(doc.get('constraints', [])):
            ref = f'constraints[{i}]'
            metadata[name, ref] = (c['type'], c.get('modality', 'alethic'), c.get('id', ref))
    assert actual == {(r["model"], r["ref"]) for r in MATRIX["obligations"]}
    assert len(actual) == MATRIX["obligation_count"] == 61
    assert len(MATRIX["cases"]) == MATRIX["case_count"] == 137
    assert set(ANSWERS) == set(MATRIX["cases"])
    for row in MATRIX["obligations"]:
        model = ROOT / "src/gnd/examples" / row["model"]
        assert hashlib.sha256(model.read_bytes()).hexdigest() == row["model_sha256"]
        assert ANSWERS[row["positive"]]["expected"] == "pass"
        assert ANSWERS[row["negative"]]["expected"] in {"fail", "warning"}
        assert MATRIX["cases"][row["negative"]]["story"]
        assert (row['kind'], row['modality'], row['id']) == metadata[row['model'], row['ref']]
        for lane in ['positive', 'negative', 'extra', 'distinct']:
            if lane not in row:
                continue
            name = row[lane]
            case, answer = MATRIX['cases'][name], ANSWERS[name]
            assert case['target'] == answer['target'] == row['ref']
            assert case['model'] == 'src/gnd/examples/' + row['model']
            assert case['expected'] == answer['expected']


@pytest.mark.parametrize("name", MATRIX["cases"])
def test_frozen_story_matches_public_gnd_report(name):
    case, answer = MATRIX["cases"][name], ANSWERS[name]
    report = check(ROOT / case["model"], ROOT / case["population"], unredacted=True)
    observed = {r["constraint_ref"]: r["verdict"] for r in report["verdicts"]}
    observed.update({r["derivation_ref"]: r["verdict"] for r in report.get("derivations") or []})
    assert observed[case["target"]] == case["expected"]
    assert observed == answer["observed_gnd_verdicts"]
    assert report["exit_code"] == answer["observed_gnd_exit"]
    assert {r['constraint_ref']: r['offending_facts'] for r in report['verdicts']
            if r['constraint_type'] == 'guarded'} == answer['guarded_witnesses']


def test_declared_consumer_paths_and_runtime_copies_exist():
    for consumer in MATRIX["consumers"]:
        assert (ROOT / consumer).exists(), consumer
    packaged = ROOT / "src/gnd/examples/release_governance/runtime-environment"
    for name in ["pyproject.toml", "uv.lock"]:
        assert (ROOT / "tutorials/runtimes" / name).read_bytes() == (packaged / name).read_bytes()


def test_inventory_checker_rejects_omitted_obligation(monkeypatch):
    monkeypatch.setitem(MATRIX, "obligations", MATRIX["obligations"][:-1])
    with pytest.raises(AssertionError):
        test_matrix_exhausts_exact_models_and_controls()


def test_inventory_checker_rejects_changed_model_identity(monkeypatch):
    changed = [dict(row) for row in MATRIX["obligations"]]
    changed[0]["model_sha256"] = "0" * 64
    monkeypatch.setitem(MATRIX, "obligations", changed)
    with pytest.raises(AssertionError):
        test_matrix_exhausts_exact_models_and_controls()


def test_gnd_witness_key_cannot_drift(monkeypatch):
    name = 'm0-r4-negative'
    changed = dict(ANSWERS[name])
    changed['guarded_witnesses'] = dict(changed['guarded_witnesses'])
    changed['guarded_witnesses']['constraints[2]'] = []
    monkeypatch.setitem(ANSWERS, name, changed)
    with pytest.raises(AssertionError):
        test_frozen_story_matches_public_gnd_report(name)


def test_inventory_checker_rejects_metadata_and_cross_links(monkeypatch):
    for key, value in [('kind', 'invented'), ('modality', 'deontic'),
                       ('id', 'invented'), ('negative', 'm0-r1-negative')]:
        changed = [dict(row) for row in MATRIX['obligations']]
        changed[0][key] = value
        with monkeypatch.context() as patch:
            patch.setitem(MATRIX, 'obligations', changed)
            with pytest.raises(AssertionError):
                test_matrix_exhausts_exact_models_and_controls()


def assert_distinct_controls(matrix):
    for row in matrix['obligations']:
        if row['kind'] != 'uniqueness':
            continue
        model = json.loads((ROOT / 'src/gnd/examples' / row['model']).read_text())
        ft = row['ref'].split('fact_types[')[1].split(']')[0]
        fact = next(f for f in model['fact_types'] if f['id'] == ft)
        index = int(row['ref'].rsplit('[', 1)[1].removesuffix(']'))
        roles = fact['constraints'][index]['roles']
        if len(roles) < len(fact['roles']):
            assert 'distinct' in row
            case = matrix['cases'][row['distinct']]
            population = json.loads((ROOT / case['population']).read_text())
            tuples = population['facts'][ft]
            assert any(a != b and all(a[r] == b[r] for r in roles)
                       for a in tuples for b in tuples)


def test_business_uniqueness_controls_and_missing_sibling_liveness():
    assert_distinct_controls(MATRIX)
    changed = dict(MATRIX)
    changed['obligations'] = [{k: v for k, v in row.items() if k != 'distinct'}
                              for row in MATRIX['obligations']]
    with pytest.raises(AssertionError):
        assert_distinct_controls(changed)


def test_approved_native_key_and_only_two_disagreements():
    approved = json.loads((CORPUS / 'approval.json').read_text())
    assert approved['matrix_sha256'] == hashlib.sha256((CORPUS / 'matrix.json').read_bytes()).hexdigest()
    assert approved['answers_sha256'] == hashlib.sha256((CORPUS / 'answers.json').read_bytes()).hexdigest()
    listed = {name: a['intentional_disagreements'] for name, a in ANSWERS.items()
              if a['intentional_disagreements']}
    assert listed == approved['intentional_disagreements']
    assert set(listed) == {'m2-book_is_eligible-extra', 'm2-eligible-joint-omission'}
    normalization = {'pass': 'satisfied', 'fail': 'violated', 'warning': 'warning',
                     'vacuous': 'vacuous', 'unchecked': 'incomplete'}
    for answer in ANSWERS.values():
        expected = answer['expected_native_verdicts']
        assert set(expected) == set(answer['observed_gnd_verdicts'])
        disagreements = {ref for ref, status in answer['observed_gnd_verdicts'].items()
                         if normalization[status] != expected[ref]}
        assert disagreements == set(answer['intentional_disagreements'])
        states = set(expected.values())
        code = 2 if states & {'incomplete', 'unsupported', 'vacuous'} else 1 if 'violated' in states else 0
        status = 'incomplete' if code == 2 else 'rejected' if code == 1 else 'accepted_with_warnings' if 'warning' in states else 'accepted'
        assert answer['expected_acceptance'] == {'accepted': code == 0, 'exit_code': code, 'status': status}
    row = next(r for r in MATRIX['obligations'] if r['id'] == 'all_eligible')
    assert set(row['source_disagreements']) == set(listed)


def test_complete_native_answers_use_asserted_facts_not_claims():
    for name, case in MATRIX['cases'].items():
        if not case['model'].endswith('complete.orm.yaml'):
            continue
        facts = json.loads((ROOT / case['population']).read_text())['facts']
        blocked = {(b['book'], u['user']) for b in facts['book_rated_adult'] for u in facts['user_is_minor']}
        rated = {(r['book'], r['user']) for r in facts['user_rated_book']}
        eligible = {(b['book'], u['user']) for b in facts['book_has_genre'] for u in facts['user_prefers_genre']
                    if b['genre'] == u['genre'] and (b['book'], u['user']) not in blocked | rated}
        recommended = {(r['book'], r['user']) for r in facts['recommendation']}
        missing = eligible - recommended
        answer = ANSWERS[name]
        assert answer['expected_native_verdicts']['constraints[3]'] == ('violated' if missing else 'satisfied')
        expected_witnesses = [{'$b': b, '$u': u} for b, u in sorted(missing)]
        assert answer['expected_native_guarded_witnesses']['constraints[3]'] == expected_witnesses
        for head, computed in [('book_is_blocked_for', blocked), ('book_is_eligible', eligible)]:
            claimed = {(r['book'], r['user']) for r in facts[head]}
            expected = {'missing': [{'book': b, 'user': u} for b, u in sorted(computed - claimed)],
                        'extra': [{'book': b, 'user': u} for b, u in sorted(claimed - computed)]}
            assert answer['expected_native_derivations']['derivation:' + head] == expected
