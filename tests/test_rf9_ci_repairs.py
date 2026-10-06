"""RF9 CI repair corpus: compatibility state and strict pool refusals."""
import json

import pytest

from gnd import model
from gnd.model import _validation
from gnd.synth.poolfile import PoolValidationError, load_pool


@pytest.mark.parametrize('name', ['_DERIVATION_WORK', '_DERIVATION_ATOM_VISITS', '_DERIVATION_CLASSIFICATION_WORK'])
def test_model_counter_lookup_is_live(monkeypatch, name):
    before = getattr(_validation, name)
    monkeypatch.setattr(_validation, name, before + 173)
    assert getattr(model, name) == before + 173


def test_unknown_model_lookup_refuses():
    with pytest.raises(AttributeError):
        _ = model._rf9_unknown_counter


@pytest.mark.parametrize('raw', ['{"x": NaN}', '{"x": 1e999}', '{"x": 1, "x": 2}'])
def test_pool_shared_policy_refusal_keeps_boundary(tmp_path, raw):
    path = tmp_path / 'pool.json'
    path.write_text(raw)
    with pytest.raises(PoolValidationError):
        load_pool(path, None)


def test_pool_malformed_json_keeps_decoder_exception(tmp_path):
    path = tmp_path / 'pool.json'
    path.write_text('{')
    with pytest.raises(json.JSONDecodeError):
        load_pool(path, None)


def test_compatibility_site_accounting_does_not_hide_new_or_missing_edges():
    import json

    from support.rf9_ci_sources import EVIDENCE, coupling_sites

    aliases = json.loads((EVIDENCE / 'compatibility-private-sites.json').read_text())['sites']
    assert coupling_sites({'private_imports': aliases}) == []
    duplicate = dict(aliases[0], line=99999)
    assert coupling_sites({'private_imports': [*aliases, duplicate]}) == [duplicate]
    unknown = dict(duplicate, name='_rf9_uninventoried')
    assert coupling_sites({'private_imports': [*aliases, unknown]}) == [unknown]
    with pytest.raises(AssertionError):
        coupling_sites({'private_imports': aliases[1:]})


@pytest.mark.parametrize('kind,old,name,home', [
    ('RF4', 'gnd.install', '_reject_unsafe_relpath', 'gnd.safefs'),
    ('RF4', 'gnd.install', 'safe_destination', 'gnd.safefs'),
    ('RF4', 'gnd.assurance_evidence', '_json', 'gnd.assurance._wire'),
    ('RF4', 'gnd.synth.assemble', '_instant_pair', 'gnd.synth.oracle.constructive'),
    ('RF4', 'gnd.synth.assemble', '_object_types_by_id', 'gnd.synth.oracle.constructive'),
    ('RF4', 'gnd.synth.assemble', '_role_object', 'gnd.synth.oracle.constructive'),
    ('RF4', 'gnd.api', '_witness_inputs', 'gnd.witness.service'),
    ('RF6', None, '_resolved_primitive', 'gnd.model_queries'),
    ('RF6', None, '_resolve_reference', 'gnd.model_queries'),
    ('RF6', None, 'primitive_for', 'gnd.model_queries'),
])
def test_body_successors_reject_changed_bodies(monkeypatch, kind, old, name, home):
    import ast
    from pathlib import Path

    import test_rf4_peripheral as rf4
    import test_rf6_moves as rf6

    def control():
        if kind == 'RF4':
            row = next(row for row in rf4.MOVES['names'] if row['old'] == old and row['name'] == name)
            rf4.test_moved_algorithm_preserves_base_body(row)
        else:
            rf6.test_primitive_move_aliases_and_bodies()

    control()
    actual = Path.read_text
    path = rf4.ROOT / ('src/' + home.replace('.', '/') + '.py')
    def dirty(current, *args, **kwargs):
        source = actual(current, *args, **kwargs)
        if current == path:
            node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)
            lines = source.splitlines(keepends=True)
            lines.insert(node.end_lineno, '    raise RuntimeError("RF9 dirty successor")\n')
            source = ''.join(lines)
        return source
    monkeypatch.setattr(Path, 'read_text', dirty)
    with pytest.raises(AssertionError):
        control()


def test_portable_ast_dump_retains_semantic_differences():
    import ast

    from support.rf8_sources import portable_dump

    empty = ast.parse('def f():\n    return []').body[0]
    dirty = ast.parse('def f():\n    return [1]').body[0]
    assert portable_dump(empty) != portable_dump(dirty)
    source = ast.dump(empty, include_attributes=False)
    portable_dump(empty)
    assert ast.dump(empty, include_attributes=False) == source


def test_compatibility_metric_refuses_a_renamed_alias(monkeypatch):
    import json
    from pathlib import Path

    from support.rf9_ci_sources import EVIDENCE, coupling_sites

    aliases = json.loads((EVIDENCE / 'compatibility-private-sites.json').read_text())['sites']
    actual = Path.read_bytes
    def dirty(path):
        raw = actual(path)
        if path.as_posix().endswith('src/gnd/checker/__init__.py'):
            return raw.replace(b'_COMPARATORS as _COMPARATORS', b'_COMPARATORS as _rf9_not_compat')
        return raw
    monkeypatch.setattr(Path, 'read_bytes', dirty)
    with pytest.raises(AssertionError):
        coupling_sites({'private_imports': aliases})


def test_markdown_guard_detects_conditional_python_import(monkeypatch):
    from pathlib import Path

    import test_measure_offline as scans

    actual = Path.read_text
    def dirty(path, *args, **kwargs):
        source = actual(path, *args, **kwargs)
        if path == scans.MODEL_EVOLVE_SKILL_FILES[0]:
            source += '\n```python\nif True: import requests\n```\n'
        return source
    monkeypatch.setattr(Path, 'read_text', dirty)
    with pytest.raises(AssertionError):
        scans.test_model_evolve_skill_is_offline_and_preserves_write_authority()


def test_checker_core_producer_preserves_registered_owner(monkeypatch):
    import public_site_census as census
    from support.repository import REPO_ROOT

    from gnd import semantic_registry
    from gnd.checker import _core

    sites = census.inventory(REPO_ROOT)
    row = next(r for r in semantic_registry.REGISTRY if r.production_owner == 'gnd.checker._observe_phase1_compatibility')
    reason = row.scope_id.removeprefix('applicability:refusal:n-a:')
    monkeypatch.setattr(_core, 'adapt_phase1_slice', lambda *_: None)
    monkeypatch.setattr(_core, 'phase1_refusal_reason', lambda *_: reason)
    def run():
        with census.capture_sites(REPO_ROOT, sites, semantic_registry.REGISTRY) as trace:
            _core._observe_phase1_compatibility({}, 'rf9', None, None, None, [], [], {})
        return trace
    trace = run()
    assert row.scope_id in trace.observed
    assert {s.owner for s in trace.observed[row.scope_id]} == {row.production_owner}
    actual = census._owner
    monkeypatch.setattr(census, '_owner', lambda module, name: module + '.' + name if module == 'gnd.checker._core' else actual(module, name))
    with pytest.raises(AssertionError, match='no producer owner frame'):
        run()


def test_pool_depth_refusal_keeps_boundary(tmp_path):
    path = tmp_path / 'pool.json'
    path.write_text('[' * 65 + '0' + ']' * 65)
    with pytest.raises(PoolValidationError):
        load_pool(path, None)


def test_artifact_reader_alias_is_identical():
    from gnd import artifacts, safefs
    assert safefs.read_regular_file_bytes is artifacts.read_regular_file_bytes


@pytest.mark.parametrize('dirty', ['checksum', 'meaning', 'unknown-id', 'invalid-json', 'wrong-types', 'duplicate-id', 'over-cap', 'duplicate-json-key', 'nonfinite-json', 'rows-type', 'missing-field', 'same-snippet', 'empty-file', 'empty-snippet', 'nonstring-new'])
def test_mutation_retarget_refusals_are_named(monkeypatch, dirty):
    import json
    from pathlib import Path

    from test_rf1_pin_harness import ROOT, tool

    actual = Path.read_text
    def altered(path, *args, **kwargs):
        source = actual(path, *args, **kwargs)
        if path.name != 'mutation-retargets.json':
            return source
        if dirty == 'invalid-json':
            return '{'
        if dirty == 'over-cap':
            return ' ' * (tool.MAX_TABLE_BYTES + 1) + source
        if dirty == 'duplicate-json-key':
            return source.replace('"table_sha256":', '"table_sha256": "duplicate", "table_sha256":', 1)
        data = json.loads(source)
        if dirty == 'nonfinite-json':
            data['probe'] = float('nan')
        elif dirty == 'rows-type':
            data['rows'] = {}
        elif dirty == 'missing-field':
            del data['rows'][0]['after_file']
        elif dirty == 'same-snippet':
            data['rows'][0]['after_new'] = data['rows'][0]['after_old']
        elif dirty == 'empty-file':
            data['rows'][0]['after_file'] = ''
        elif dirty == 'empty-snippet':
            data['rows'][0]['after_old'] = ''
        elif dirty == 'nonstring-new':
            data['rows'][0]['after_new'] = 1
        elif dirty == 'checksum':
            data['table_sha256'] = '0' * 64
        elif dirty == 'meaning':
            data['rows'][0]['old'] += 'changed'
        elif dirty == 'unknown-id':
            data['rows'][0]['id'] = 'RF9-unknown-retarget'
        elif dirty == 'wrong-types':
            data['rows'][0]['after_old'] = []
        else:
            data['rows'].append(data['rows'][0])
        return json.dumps(data)
    monkeypatch.setattr(Path, 'read_text', altered)
    with pytest.raises(tool.ToolError) as refusal:
        tool.load_table(ROOT / tool.DEFAULT_TABLE)
    assert refusal.value.code == 3


@pytest.mark.parametrize('before,after', [
    ('def f():\n    return call(k=1)', 'def f():\n    return call(k=2)'),
    ('@one\ndef f():\n    pass', '@two\ndef f():\n    pass'),
    ('def f(x=[]):\n    return x', 'def f(x=[1]):\n    return x'),
    ('class C:\n    pass', 'class C(B):\n    pass'),
])
def test_portable_ast_dump_keeps_nonempty_fields(before, after):
    import ast

    from support.rf8_sources import portable_dump
    assert portable_dump(ast.parse(before)) != portable_dump(ast.parse(after))
