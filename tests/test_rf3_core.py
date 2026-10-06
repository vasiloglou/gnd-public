"""RF3 core predicates and controls that can refute each new boundary."""
from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import test_rf1_layering as layering
from test_rf1_semantic_pins import RESOLVER_VALUES, _resolver_model

import gnd.model._validation as validation_home
from gnd import applicability, checker, documents, extensions, model, population, universe
from gnd import semantic_registry as registry
from gnd.errors import UnvalidatedPopulationError, ValidationIssue

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / '.gnd-planning/milestones/code-refactoring/evidence'


def core_modules(metrics):
    original = json.loads((EVIDENCE / 'metrics-RF3-base.json').read_text())
    return set(next(s for s in original['sccs']['runtime'] if 'gnd.model' in s)) | {r['new'].rsplit('.', 1)[0] for r in json.loads((EVIDENCE / 'RF3-moves.json').read_text())}


def assert_core(metrics):
    core = core_modules(metrics)
    assert not [s for s in metrics['sccs']['runtime'] if len(s) > 1 and set(s) & core]
    assert not [e for e in metrics['layering']['wrong_way'] if e['from'] in core]
    assert not layering._layer_map()['allow_list']
    original = json.loads((EVIDENCE / 'metrics-RF3-base.json').read_text())
    cohort = {m['module'] for m in original['modules'] if m['layer'] in layering.SCOPE}
    assert sum(p['from'] in cohort for p in original['private_imports']) == 64
    assert sum(p['from'] in cohort for p in metrics['private_imports']) <= 60


def test_full_current_and_original_core():
    measured = layering.arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')
    assert_core(measured)
    assert any(e['from'] == 'gnd.semantic_spec' and e['to'] == 'gnd.terms'
               and e['kind'] == 'dynamic' for e in measured['edges'])
    original_layer_core = {m['module'] for m in json.loads((EVIDENCE / 'metrics-RF3-base.json').read_text())['modules']
                           if m['layer'] in layering.SCOPE}
    assert not [e for e in measured['layering']['wrong_way'] if e['from'] in original_layer_core]



def test_core_guard_rejects_a_new_lazy_cycle(monkeypatch):
    original = Path.open
    visited = []

    def dirty(path, *args, **kwargs):
        if path == ROOT / 'src/gnd/universe.py':
            visited.append(path)
            with original(path, *args, **kwargs) as stream:
                return io.BytesIO(stream.read() + b'\ndef rf3_dirty():\n    import gnd.model\n')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', dirty)
    measured = layering.arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')
    assert visited
    with pytest.raises(AssertionError):
        assert_core(measured)


def test_map_rejects_an_unmapped_home(tmp_path):
    mapping = layering._layer_map()
    del mapping['modules']['gnd.universe']
    path = tmp_path / 'layers.json'
    path.write_text(json.dumps(mapping))
    with pytest.raises(layering.arch.ToolError, match='misses modules'):
        layering.arch.measure(ROOT, path)


def resolve_owner(owner):
    module, name = owner.rsplit('.', 1)
    resolved = getattr(importlib.import_module(module), name)
    assert inspect.isfunction(resolved), owner
    return resolved


def test_every_registry_owner_resolves_to_a_function():
    assert len(registry.REGISTRY) > 100
    for row in registry.REGISTRY:
        resolve_owner(row.production_owner)


def test_unknown_owner_is_rejected():
    with pytest.raises(AttributeError):
        resolve_owner('gnd.checker.rf3_nonexistent_owner')
    with pytest.raises(AssertionError):
        resolve_owner('gnd.checker.Model')


@pytest.mark.parametrize('flag', [*RESOLVER_VALUES, 'absent'])
def test_explicit_resolver_variants_preserve_flags(flag):
    types, built = _resolver_model(flag)
    by_id = {t['id']: t for t in types}
    expected_truthy = 'String' if flag != 'absent' and RESOLVER_VALUES[flag] else None
    expected_strict = 'String' if flag == 'true' else None
    assert universe.primitive_for('Child', by_id, variant='truthy') == expected_truthy
    assert universe.primitive_for('Child', by_id, variant='strict') == expected_strict
    assert model._resolved_primitive('Child', by_id) == expected_truthy
    assert universe.resolve_primitive('Child', built) == expected_strict


@pytest.mark.parametrize('variant', ['truthy', 'strict'])
@pytest.mark.parametrize('shape', ['missing', 'cycle', 'ambiguous', 'unanimous'])
def test_resolver_failure_and_agreement_routes(variant, shape):
    types = {'x': {'id': 'x', 'kind': 'entity', 'inherits_reference': True, 'subtype_of': ['a', 'b']},
             'a': {'id': 'a', 'kind': 'value', 'primitive': 'String'},
             'b': {'id': 'b', 'kind': 'value', 'primitive': 'Integer'}}
    if shape == 'missing':
        types.pop('x')
    elif shape == 'cycle':
        types['x']['subtype_of'] = ['x']
    elif shape == 'unanimous':
        types['b']['primitive'] = 'String'
    assert universe.primitive_for('x', types, variant=variant) == ('String' if shape == 'unanimous' else None)


def test_resolver_preserves_direct_reference_policy_and_seen():
    types = {'e': {'id': 'e', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 0}},
             '0': {'id': '0', 'kind': 'value', 'primitive': 'Integer'}}
    assert universe.primitive_for('e', types, variant='truthy') is None
    assert universe.primitive_for('e', types, variant='strict') == 'Integer'
    assert universe.primitive_for('0', types, variant='truthy', seen={'0'}) is None
    with pytest.raises(ValueError, match='unknown primitive resolver variant'):
        universe.primitive_for('e', types, variant='invalid')
    with pytest.raises(TypeError):
        universe.primitive_for('e', types)


def test_old_resolver_signatures_use_explicit_entry(monkeypatch):
    calls = []
    monkeypatch.setattr(universe, 'primitive_for', lambda *args, **kwargs: calls.append(kwargs) or 'tag')
    types, built = _resolver_model('one')
    assert model._resolved_primitive('Child', {t['id']: t for t in types}) == 'tag'
    assert universe.resolve_primitive('Child', built) == 'tag'
    assert [c['variant'] for c in calls] == ['truthy', 'strict']


def predecessor_view(m, p):
    # Frozen policy from the verbatim applicability body at 4415327.
    if not any(isinstance(ft.get('derivation_rule'), dict) for ft in m.fact_types):
        return p
    opaque = any(isinstance(v, dict) and set(v) == {'$opaque'}
                 for rows in p.facts.values() for fact in rows for v in fact.values())
    if opaque:
        rows, _ = extensions._evaluate_derivations_dispatch(m, p)
        calculated = extensions._ExtensionResult(rows, 0)
    elif extensions._model_uses_exact_derivations(m):
        calculated = extensions._exact_extension_calculator(m, extensions._base_relations(m, p))
    else:
        calculated = extensions._python_extension_calculator(m, extensions._base_relations(m, p))
    return extensions._constraint_view_dispatch(m, p, calculated.extensions)


@pytest.mark.parametrize('kind', ['plain', 'ordinary', 'exact', 'opaque'])
def test_effective_view_branches_use_the_expected_calculator(kind, monkeypatch):
    m = SimpleNamespace(fact_types=[] if kind == 'plain' else [{'derivation_rule': {}}])
    p = SimpleNamespace(facts={'f': [{'r': {'$opaque': 'x'} if kind == 'opaque' else 1}]},
                        matches_validation_marker=lambda actual: actual is m)
    reached = []
    monkeypatch.setattr(extensions, '_model_uses_exact_derivations', lambda actual: kind == 'exact')
    monkeypatch.setattr(extensions, '_base_relations', lambda *args: 'base')
    for name, tag in [('_python_extension_calculator', 'ordinary'), ('_exact_extension_calculator', 'exact')]:
        def tagged(*args, tag=tag):
            reached.append(tag)
            return SimpleNamespace(extensions=tag)
        monkeypatch.setattr(extensions, name, tagged)
    monkeypatch.setattr(extensions, '_evaluate_derivations_dispatch', lambda *args: (reached.append('opaque') or 'opaque', []))
    monkeypatch.setattr(extensions, '_constraint_view_dispatch', lambda m, p, rows: rows)
    assert checker.effective_view is extensions.effective_view
    assert extensions.effective_view(m, p) == (p if kind == 'plain' else kind)
    assert reached == ([] if kind == 'plain' else [kind])


@pytest.mark.parametrize('model_path,pop_path', [
    ('tests/fixtures/derivation-evaluation/cases/obligation-semiderived-surplus/model.orm.yaml',
     'tests/fixtures/derivation-evaluation/cases/obligation-semiderived-surplus/population.yaml'),
    ('tests/fixtures/derivation-evaluation/cases/obligation-opaque-mixed-listed/model.orm.yaml',
     'tests/fixtures/derivation-evaluation/cases/obligation-opaque-mixed-listed/population.yaml'),
    ('tests/fixtures/v62-phase3/models/exact-terms.orm.yaml', 'tests/fixtures/v62-phase3/populations/term-input.pop.yaml'),
])
def test_effective_view_on_real_validated_inputs(model_path, pop_path):
    m = model.load_model(ROOT / model_path)
    p = population.load_population(ROOT / pop_path, model=m)
    expected = predecessor_view(m, p)
    actual = checker.effective_view(m, p)
    assert actual.facts == expected.facts
    assert actual.instances == expected.instances
    assert actual.covers == expected.covers
    assert actual.lineages == expected.lineages


def test_effective_view_refuses_unvalidated_population():
    m = documents.Model.model_construct(object_types=[], fact_types=[])
    p = population.Population(model='model', source='fixture', facts={})
    with pytest.raises(UnvalidatedPopulationError):
        checker.effective_view(m, p)


def test_applicability_uses_the_public_effective_view(monkeypatch):
    from test_public_applicability_obligations import _mandatory_inputs
    m, pops = _mandatory_inputs()
    seen = []
    original = extensions.effective_view
    monkeypatch.setattr(extensions, 'effective_view', lambda *args: seen.append(args) or original(*args))
    applicability.applicable_scope_ids(m, pops[0])
    assert seen == [(m, pops[0])]


def test_shared_context_cache_identity_and_reset(monkeypatch):
    assert model._DERIVATION_TERM_CACHE is universe.DERIVATION_TERM_CACHE
    assert extensions.analyze_declared_aggregate is model.analyze_declared_aggregate
    context = universe.DERIVATION_TERM_CACHE
    prior = context.get()
    doc = {'object_types': [], 'fact_types': []}
    calls = []
    monkeypatch.setattr(validation_home, '_derivation_head_term_issues', lambda d: calls.append(d) or [
        ValidationIssue(path='$', message='tag', rule_id='semantic:term-function-name')])
    token = context.set({'document': doc})
    try:
        assert len(model._filter_derivation_term_issues(doc, rule_id='semantic:term-function-name')) == 1
        assert model._filter_derivation_term_issues(doc, rule_id='other') == []
        assert calls == [doc]
        model._filter_derivation_term_issues(dict(doc), rule_id='other')
        assert len(calls) == 2  # identical content is not identical document identity
    finally:
        context.reset(token)
    assert context.get() is prior


def test_remaining_document_moves_are_verbatim_and_aliased():
    rows = json.loads((EVIDENCE / 'RF3-document-moves.json').read_text())
    for row in rows:
        old_module, old_name = row['old'].rsplit('.', 1)
        new_module, new_name = row['new'].rsplit('.', 1)
        assert getattr(importlib.import_module(old_module), old_name) is getattr(importlib.import_module(new_module), new_name)
        if row['kind'] == 'FunctionDef':
            source = inspect.getsource(getattr(documents, new_name))
            assert hashlib.sha256(source.encode()).hexdigest() == row['body_sha256']
    assert model._DERIVATION_TERM_CACHE.name == 'gnd_intake_term_issues'


def test_duplicate_checker_function_rebinding_is_absent():
    paths = set((ROOT / 'src/gnd/checker').rglob('*.py'))
    assert paths == {ROOT / 'src/gnd/checker' / name for name in ('__init__.py', '_core.py', '_reports.py')}
    names = [n.name for path in paths for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef)]
    assert len(names) == len(set(names))


def test_validation_resets_shared_context_after_a_rule_raises(monkeypatch):
    cache = universe.DERIVATION_TERM_CACHE
    prior = {'document': object()}
    token = cache.set(prior)
    doc = {'object_types': [], 'fact_types': []}

    def raises(actual):
        assert cache.get()['document'] is actual is doc
        raise ValueError('dirty control')

    monkeypatch.setattr(validation_home, '_SEMANTIC_RULES', (raises,))
    try:
        issues = model.semantic_validate(doc)
        assert [issue.rule_id for issue in issues] == ['internal:rule-raised']
        assert cache.get() is prior
    finally:
        cache.reset(token)


@pytest.mark.parametrize('variant', ['truthy', 'strict'])
@pytest.mark.parametrize('mode', ['popular', 'general', 'unit', 'external'])
def test_resolver_reference_modes(variant, mode):
    by_id = {'e': {'id': 'e', 'kind': 'entity',
                   'reference': {'mode': mode, 'value_type': 'v'}},
             'v': {'id': 'v', 'kind': 'value', 'primitive': 'String'}}
    expected = 'String' if mode in ('popular', 'general') else None
    assert universe.primitive_for('e', by_id, variant=variant) == expected
    del by_id['v']
    assert universe.primitive_for('e', by_id, variant=variant) is None


def test_plain_view_preserves_population_identity():
    from test_public_applicability_obligations import _mandatory_inputs
    m, pops = _mandatory_inputs()
    assert not any(isinstance(f.get('derivation_rule'), dict) for f in m.fact_types)
    assert checker.effective_view(m, pops[0]) is pops[0]


def test_analysis_reaches_the_shared_validation_cache():
    assert extensions.analyze_declared_aggregate.__globals__['_DERIVATION_TERM_CACHE'] is universe.DERIVATION_TERM_CACHE
