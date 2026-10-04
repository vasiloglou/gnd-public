from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.digests import sha256_bytes
from test_public_transition_walks import CORPUS

from gnd import api
from gnd.api import _run_transition_raw, transition
from gnd.assurance import derive_assurance_scope
from gnd.checker import check
from gnd.model import load_model
from gnd.population import load_population
from gnd.report import load_report_schema
from gnd.semantic_registry import REGISTRY, applicable_scope_ids, capture_branches
from tests.support.v62_phase1_corpus import ANSWERS as PHASE1_ANSWERS
from tests.support.v62_phase1_corpus import FIXTURE, document, population, steps

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = {**PHASE1_ANSWERS, **json.loads((ROOT / 'tests/fixtures/public-emitter21/answers.json').read_text())}
SCOPE = 'composition:derivation-view:static:applied'


def _payload() -> dict[str, object]:
    return transition(FIXTURE / 'models/static.orm.yaml', population('pre_clean'), steps(), population('post_exact'))


def test_assurance_case_a02_scope_is_composition_specific() -> None:
    payload = _payload()
    assert SCOPE in payload['assurance']['uncovered_applicable_scope_ids']

def test_assurance_case_a03_never_proof_backed() -> None:
    payload = _payload()
    assert payload['transition']['evaluated'] is True
    assert SCOPE in payload['assurance']['uncovered_applicable_scope_ids']
    assert payload['assurance']['assurance_level'] != ANSWERS['A03']['forbidden_assurance']

def test_derivation_only_check_neither_applies_nor_traces_static_composition(tmp_path) -> None:
    doc = document('base')
    doc['operations'] = []
    model_path = tmp_path / 'derivation-only.orm.yaml'
    with model_path.open('w', encoding='utf-8') as stream:
        YAML().dump(doc, stream)
    model = load_model(model_path)
    population_doc = YAML(typ='safe').load(population('pre_clean').read_text(encoding='utf-8'))
    population_doc['population']['model'] = model_path.name
    population_path = tmp_path / 'pre.pop.yaml'
    with population_path.open('w', encoding='utf-8') as stream:
        YAML().dump(population_doc, stream)
    loaded = load_population(population_path, model=model)
    with capture_branches() as trace:
        check(model, loaded)
    assert SCOPE not in trace
    assert SCOPE not in applicable_scope_ids(model, loaded)


def _version_constants(value: object) -> set[int]:
    found: set[int] = set()
    if isinstance(value, dict):
        if isinstance(value.get('const'), int):
            found.add(value['const'])
        for child in value.values():
            found.update(_version_constants(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_version_constants(child))
    return found

def test_versions_3_through_8_and_no_declaration_goldens_are_exact() -> None:
    assert set(ANSWERS['predecessor_versions']['report']) == set(range(3, 9))
    assert set(range(3, 9)) <= _version_constants(load_report_schema())
    answer = ANSWERS['no_declaration_control']
    completed = subprocess.run([sys.executable, '-m', 'gnd', *answer['command']], cwd=ROOT, capture_output=True, check=False)
    assert completed.returncode == answer['exit']
    payload = json.loads(completed.stdout)
    assurance = payload.pop('assurance')
    assert assurance['assurance_level'] == 'none'
    assert assurance['uncovered_applicable_scope_ids']
    without_assurance = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    assert sha256_bytes(without_assurance) == 'b62ae83b96f4b310708030d49663f2cfb3c24288aea32470851f51bd95eb8d7d'
    assert len(completed.stderr) == answer['stderr_bytes']
    assert sha256_bytes(completed.stderr) == answer['stderr_sha256']

STATIC = ROOT / "tests/fixtures/v62-phase1"
DYNAMIC = ROOT / "tests/fixtures/v62-phase2"

NOT_CURRENT = 'applicability:refusal:n-a:evidence-not-current'
R_DYN = frozenset(row.scope_id for row in REGISTRY if (row.surface, row.family) in {('composition', 'dynamic-refresh'), ('transition', 'derived-change'), ('report', 'transition-derived-changes')})
R_SUBJ = frozenset(row.scope_id for row in REGISTRY if row.surface == 'transition' and row.family == 'dynamic-rule' and row.variant.startswith('derived-'))
SCOPED = R_DYN | R_SUBJ
R_DYN_CHECK = frozenset(scope_id for scope_id in R_DYN if not scope_id.startswith('transition:'))

def _applicable(payload: dict) -> frozenset[str]:
    return frozenset(payload['assurance']['uncovered_applicable_scope_ids']) - {NOT_CURRENT}

def _walk(model, pre, steps, post=None):
    with capture_branches() as trace:
        payload = api.transition(model, pre, steps, post, unredacted=True)
    return (payload, frozenset(trace))

def test_k04_static_composition_owes_no_dynamic_row():
    model = STATIC / 'models/static.orm.yaml'
    pre = STATIC / 'populations/pre-clean.pop.yaml'
    assert not _applicable(api.check(model, pre, unredacted=True)) & SCOPED
    payload, trace = _walk(model, pre, STATIC / 'walks/activate.steps.json')
    assert not _applicable(payload) & SCOPED
    assert not trace & SCOPED

def test_k05_dynamic_composition_keeps_its_rows():
    model = DYNAMIC / 'models/dynamic.orm.yaml'
    pre = DYNAMIC / 'populations/pre-open.pop.yaml'
    assert R_DYN_CHECK <= _applicable(api.check(model, pre, unredacted=True))
    payload, trace = _walk(model, pre, DYNAMIC / 'walks/ticket.steps.json', DYNAMIC / 'populations/post-resolved.pop.yaml')
    applicable = _applicable(payload)
    assert R_DYN <= applicable
    assert trace & SCOPED
    assert trace & SCOPED <= applicable


def decided_label(applicable, trace, proved, execution: tuple[str, bool]) -> str:
    """The label derive_assurance_scope and certify_result reach, over frozen coverage."""
    from gnd.assurance import _assurance_policy, assurance_prerequisites
    from gnd.semantic_registry import REGISTRY
    surface, complete = execution
    required = frozenset(assurance_prerequisites(surface, 'report'))
    infrastructure = frozenset(row.scope_id for row in REGISTRY if row.family == 'assurance')
    return _assurance_policy(applicable, applicable & proved, required=required, proved_infrastructure=proved & infrastructure, guards_valid=complete and trace - {NOT_CURRENT} <= applicable | required)


def test_rh7_the_predictor_applies_productions_finite_set_guards():
    from gnd.assurance import assurance_prerequisites
    required = frozenset(assurance_prerequisites('snapshot', 'report'))
    leaked = next(iter(required))
    label = decided_label(frozenset({leaked}), frozenset(), frozenset(required), ('snapshot', True))
    assert label == 'none'


def test_operations_only_walk_neither_applies_nor_traces_static_composition() -> None:
    root = Path('tests/fixtures/transition/expense')
    walk = root / 'walks/clean-walk'
    result = _run_transition_raw(root / 'v2_expense.orm.yaml', walk / 'pre.pop.yaml', walk / 'steps.json', walk / 'post.pop.yaml')
    scope = derive_assurance_scope(result.execution, consumer='report')
    assert SCOPE not in result.execution.trace
    assert SCOPE not in scope.applicable_scope_ids

@pytest.fixture(autouse=True)
def _owned_operations_only_fixture(request, tmp_path, monkeypatch):
    if request.node.name != 'test_operations_only_walk_neither_applies_nor_traces_static_composition':
        return
    root = tmp_path / 'tests/fixtures/transition/expense'
    for relative in ('v2_expense.orm.yaml', 'walks/clean-walk/pre.pop.yaml', 'walks/clean-walk/post.pop.yaml', 'walks/clean-walk/steps.json'):
        source = CORPUS / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o644)
    monkeypatch.chdir(tmp_path)

EXPENSE = CORPUS

@pytest.mark.parametrize('walk', sorted(path.name for path in (EXPENSE / 'walks').iterdir() if path.is_dir()))
@pytest.mark.parametrize('mode', ['audit', 'plan'])
def test_k03_legacy_walk_owes_no_composition_row(walk, mode):
    folder = EXPENSE / 'walks' / walk
    post = folder / 'post.pop.yaml' if mode == 'audit' else None
    if post is not None and (not post.exists()):
        pytest.skip('walk has no declared post')
    payload, trace = _walk(EXPENSE / 'v2_expense.orm.yaml', folder / 'pre.pop.yaml', folder / 'steps.json', post)
    if payload.get('assurance') is None:
        pytest.skip('walk refused before assurance')
    assert not _applicable(payload) & SCOPED
    assert not trace & SCOPED
