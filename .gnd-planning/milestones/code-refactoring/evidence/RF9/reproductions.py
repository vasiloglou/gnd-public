"""RF9 retained counterexamples; exit zero confirms the observed finding."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'tests'))


def contract_equality():
    from test_exp_session_contract import _v2_exact_contract_document

    from gnd.exp.session_contract import DataDrivenContract

    old = types.ModuleType('rf9_previous_contract')
    old.__file__ = str(ROOT / 'src/gnd/exp/session_contract.py')
    sys.modules[old.__name__] = old
    source = subprocess.check_output(
        ['git', 'show', 'de4eed6:src/gnd/exp/session_contract.py'], cwd=ROOT, text=True)
    exec(compile(source, '<de4eed6:session_contract>', 'exec'), old.__dict__)  # noqa: S102 -- fixed-revision repository source, isolated namespace
    observations = {}
    with tempfile.TemporaryDirectory(prefix='rf9-equality-') as directory:
        wire = _v2_exact_contract_document(Path(directory))
        for label, cls in [('RF7 predecessor', old.DataDrivenContract), ('RF8 final', DataDrivenContract)]:
            parsed = cls.model_validate(wire)
            fields = {name: getattr(parsed, name) for name in cls.model_fields}
            first, second = cls(**fields), cls(**fields)
            before = first == second
            first_dump = first.model_dump(mode='json')
            after_one = first == second
            second_dump = second.model_dump(mode='json')
            observations[label] = {'equal_before': before, 'equal_after_serializing_one': after_one,
                                   'equal_after_serializing_both': first == second,
                                   'serialized_bytes_equal': first_dump == second_dump}
    assert observations['RF7 predecessor']['equal_after_serializing_one'] is True
    assert observations['RF8 final']['equal_before'] is True
    assert observations['RF8 final']['equal_after_serializing_one'] is False
    assert observations['RF8 final']['serialized_bytes_equal'] is True
    return {'source': 'src/gnd/exp/session_contract.py:1085',
            'expected': 'serialization preserves equality of two equal valid frozen contracts',
            'observed': observations,
            'comparison_boundary': 'isolated predecessor contract module with current unchanged dependency interfaces; not full historical-suite execution'}


def annotation_resolution():
    import typing

    from gnd import population
    old = types.ModuleType('rf9_previous_population')
    old.__file__ = str(ROOT / 'src/gnd/population.py')
    sys.modules[old.__name__] = old
    source = subprocess.check_output(['git', 'show', 'f5a8318:src/gnd/population.py'], cwd=ROOT, text=True)
    exec(compile(source, '<f5a8318:population>', 'exec'), vars(old))  # noqa: S102 -- fixed-revision repository source, isolated namespace
    rows = {}
    for name in ('_content_digest', '_model_digest'):
        prior = typing.get_type_hints(getattr(old, name))
        assert 'return' in prior
        try:
            typing.get_type_hints(getattr(population, name))
        except NameError as error:
            rows[name] = {'baseline_resolves': True, 'current_error': str(error)}
        else:
            raise AssertionError('expected unresolved annotation')
    return rows


def literal_getattr_inventory():
    import ast

    import test_rf6_query_policy as guard
    all_sources = guard.sources()
    original = guard.reads(all_sources)
    dynamic = guard.dynamic_reads(all_sources)
    dirty = dict(all_sources)
    dirty['src/gnd/rf9_in_memory.py'] = 'def injected(model):\n    return getattr(model, "fact_types", ())\n'
    altered = guard.reads(dirty)
    altered_dynamic = guard.dynamic_reads(dirty)
    assert altered == original and altered_dynamic == dynamic
    guard.assert_policy(altered, json.loads(guard.POLICY.read_text()))
    rows = json.loads((OUT.parent / 'RF8/dynamic-query-candidates.json').read_text())['rows']
    guard.assert_dynamic_inventory(altered_dynamic, rows)
    missed = []
    for path, source in all_sources.items():
        for node in ast.walk(ast.parse(source)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == 'getattr' and len(node.args) > 1
                    and isinstance(node.args[1], ast.Constant) and node.args[1].value == 'fact_types'):
                prior = subprocess.check_output(['git', 'show', 'f5a8318:' + path], cwd=ROOT, text=True)
                expression = ast.unparse(node)
                existed = any(isinstance(n, ast.Call) and ast.unparse(n) == expression
                              for n in ast.walk(ast.parse(prior)))
                missed.append({'path': path, 'line': node.lineno, 'expression': expression,
                               'same_expression_in_base': existed})
    assert len(missed) == 4
    assert all(row['same_expression_in_base'] for row in missed)
    return {'injected_read_count_delta': 0, 'injected_dynamic_count_delta': 0,
            'both_policy_assertions_passed': True, 'existing_omitted_reads': missed}


def early_cache_observer():
    import ast
    import copy
    import hashlib

    from support.rf8_sources import predecessor_body
    path = ROOT / 'src/gnd/exp/session_replay.py'
    node = next(n for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == 'reconstruct')
    dirty = copy.deepcopy(node)
    index = next(i for i, n in enumerate(dirty.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'identity' for t in n.targets))
    dirty.body.insert(index + 1, ast.parse('store._best_identity = identity').body[0])
    assert ast.dump(dirty) != ast.dump(node)
    normalized = hashlib.sha256(predecessor_body(copy.deepcopy(node)).encode()).hexdigest()
    altered = hashlib.sha256(predecessor_body(copy.deepcopy(dirty)).encode()).hexdigest()
    rows = json.loads((OUT.parent / 'RF8/reader-base.json').read_text())['functions']
    approved = next(r['ast_sha256'] for r in rows if r['function'] == 'reconstruct')
    assert altered == normalized == approved
    control = copy.deepcopy(node)
    control.body.insert(index + 1, ast.parse('store._rf9_other = identity').body[0])
    assert hashlib.sha256(predecessor_body(control).encode()).hexdigest() != approved
    return {'raw_ast_changed': True, 'recorded_hash': approved,
            'early_cache_assignment_hash': altered, 'unrelated_assignment_detected': True,
            'scope': 'moved-body predicate only; no claim that every test accepts this mutant'}


def offline_import_guard():
    import ast

    import pytest
    import test_measure_offline as guard
    target = ROOT / 'src/gnd/exp/session_runtime.py'
    original_read = Path.read_text
    original_source = original_read(target)
    visited = []
    mutation = '\ndef rf9_network_probe():\n    from urllib import request\n    return request.urlopen("https://example.invalid")\n'
    def altered(path, *args, **kwargs):
        if path == target:
            visited.append(str(path.relative_to(ROOT)))
            return original_source + mutation
        return original_read(path, *args, **kwargs)
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(Path, 'read_text', altered)
        guard.test_no_network_library_is_reachable_from_the_generation_lane()
    assert visited
    assert guard._forbidden_hit('from urllib import request', guard._NETWORK_LIBS) == []
    assert guard._forbidden_hit('import urllib.request', guard._NETWORK_LIBS) == ['urllib.request']
    old = subprocess.check_output(['git', 'show', 'f5a8318:tests/test_measure_offline.py'], cwd=ROOT, text=True)
    old_tree = ast.parse(old)
    old_regex = next(ast.unparse(n) for n in old_tree.body if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == '_IMPORT_RE' for t in n.targets))
    current_tree = ast.parse(original_read(ROOT / 'tests/test_measure_offline.py'))
    current_regex = next(ast.unparse(n) for n in current_tree.body if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == '_IMPORT_RE' for t in n.targets))
    assert old_regex == current_regex
    return {'mutated_source_visited': len(visited), 'generation_scan_passed': True,
            'literal_import_sibling_detected': True, 'regex_identical_to_base': True,
            'network_executed': False, 'classification': 'pre-existing source-owned test debt'}


def parent_package_edges():
    import ast
    import os
    import runpy
    arch = runpy.run_path(str(ROOT / 'tools/gnd_arch.py'))
    metrics = arch['measure'](ROOT, ROOT / 'tools/gnd_layers.json')
    layers = json.loads((ROOT / 'tools/gnd_layers.json').read_text())['modules']
    edges = {(r['from'], r['to']) for r in metrics['edges']}
    hidden = []
    for row in metrics['modules']:
        if row['layer'] != 'lanes':
            continue
        tree = ast.parse((ROOT / row['path']).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == 'gnd.commands._output':
                assert (row['module'], 'gnd.commands._output') in edges
                assert (row['module'], 'gnd.commands') not in edges
                hidden.append({'from': row['module'], 'to': 'gnd.commands',
                               'source': row['path'], 'line': node.lineno})
    assert len(hidden) == 7
    assert layers['gnd.commands']['layer'] == 'entry'
    assert not metrics['layering']['wrong_way']
    initializer = ast.parse((ROOT / 'src/gnd/commands/__init__.py').read_text())
    assert all(isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
               and isinstance(n.value.value, str) for n in initializer.body)
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    probe = subprocess.check_output([sys.executable, '-c',
        'import sys; import gnd.codegen.service; print("gnd.commands" in sys.modules)'],
        cwd=ROOT, env=env, text=True).strip()
    assert probe == 'True'
    return {'hidden_lane_to_parent_edges': hidden, 'fresh_codegen_import_loads_entry_parent': True,
            'reported_wrong_way_edges': 0, 'parent_initializer_only_docstring': True,
            'consequence': 'incomplete runtime-edge guarantee; no current command failure demonstrated'}


def terminal_acceptance():
    import contextlib
    import copy
    import io
    import os

    import pytest
    from test_rf1_session_pins import _contract, build_v7, run_main

    from gnd.artifacts import canonical_json_bytes
    from gnd.exp import close
    from gnd.exp.session_eval import contract_accepts
    from gnd.exp.session_replay import reconstruct
    from gnd.exp.session_store import SessionStore
    from gnd.exp.spec import read_spec

    previous = types.ModuleType('rf9_previous_close')
    previous.__file__ = str(ROOT / 'src/gnd/exp/close.py')
    sys.modules[previous.__name__] = previous
    old_source = subprocess.check_output(['git', 'show', 'f5a8318:src/gnd/exp/close.py'], cwd=ROOT, text=True)
    exec(compile(old_source, '<f5a8318:close>', 'exec'), vars(previous))  # noqa: S102 -- fixed-revision repository source, isolated namespace
    with tempfile.TemporaryDirectory(prefix='rf9-terminal-') as directory, pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv('PATH', str(ROOT / '.venv/bin') + os.pathsep + os.environ['PATH'])
        with contextlib.redirect_stdout(io.StringIO()):
            built = build_v7(Path(directory), monkeypatch)
        spec_path = built.root / 'SPEC.md'
        spec_text = spec_path.read_text()
        assert 'kind: data-driven' in spec_text
        spec_path.write_text(spec_text.replace('kind: data-driven', 'kind: work'))
        spec = read_spec(spec_path)
        assert spec.kind == 'work'
        policy = json.loads(Path(built.argv[built.argv.index('--adapter-policy') + 1]).read_text())
        plan_path = Path(policy['argv'][1])
        plan = json.loads(plan_path.read_text())
        plan[1] = copy.deepcopy(plan[0])
        plan_path.write_text(json.dumps(plan))
        run_result = run_main(built.argv, cwd=Path(directory))
        run = built.root / 'runs/run-0001'
        path = run / 'result.json'
        original = json.loads(path.read_text())
        contract = _contract(built)
        store = SessionStore(run, run_id=run.name, contract_id=contract.experiment_id)
        reconstruct(store, contract, allow_terminal=True)
        assert contract_accepts(contract, store.best_record().evaluation) is False
        before = [f.kind for f in close._work_findings(spec, spec_path)]
        assert 'unaccepted-session' in before
        changed = dict(original, disposition='accepted', terminal_reason='all required cases accepted')
        path.write_bytes(canonical_json_bytes(changed))
        assert close._accepted_disposition(path.read_bytes())[0] is True
        current_findings = [f.kind for f in close._work_findings(spec, spec_path)]
        old_findings = [f.kind for f in previous._work_findings(spec, spec_path)]
        assert current_findings == old_findings == []
        # Reader-invalid extra metadata remains refused: initial draft probe used
        # the tests-lane `reason` field, which is not a session-result field.
        malformed = {**changed, 'reason': 'not a session-result field'}
        try:
            close._accepted_disposition(canonical_json_bytes(malformed))
        except ValueError:
            malformed_refused = True
        else:
            raise AssertionError('invalid extra field unexpectedly accepted')
        # Exercise a real empty reconstruction, retaining only the forged terminal
        # claim. Move temporary artifacts aside without changing repository bytes.
        (run / 'attempts').rename(Path(directory) / 'removed-attempts')
        (run / 'best.json').rename(Path(directory) / 'removed-best.json')
        (run / 'launches').rename(Path(directory) / 'removed-launches')
        empty_store = SessionStore(run, run_id=run.name, contract_id=contract.experiment_id)
        reconstruct(empty_store, contract, allow_terminal=True)
        assert empty_store.best_record() is None
        outer_empty_findings = [f.kind for f in close._work_findings(spec, spec_path)]
        assert outer_empty_findings
        missing_best = {'outer_empty_run_findings': outer_empty_findings,
                        'boundary': 'direct declared-case helper; outer work gate refuses this empty-launch fixture'}
        for label, module in [('current', close), ('pre_refactor', previous)]:
            try:
                module._declared_case_findings(
                    module._SessionRun(1, run, path, False), built.root, path.read_bytes(),
                    experiment_id=contract.experiment_id)
            except (AttributeError, TypeError) as error:
                missing_best[label] = type(error).__name__ + ': ' + str(error)
            else:
                raise AssertionError('expected missing-best gate to raise')
        return {'genuine_run_exit': run_result.returncode, 'genuine_disposition': original['disposition'],
                'no_best_gate_crash': missing_best,
                'best_attempt_meets_contract': False, 'original_gate_findings': before,
                'tampered_fields': ['disposition', 'terminal_reason'],
                'current_gate_findings_after_tamper': current_findings,
                'pre_refactor_close_gate_findings_after_tamper': old_findings,
                'invalid_extra_reason_field_refused': malformed_refused,
                'comparison_boundary': 'old close module with current compatibility dependencies; original and final replay omit disposition revalidation',
                'classification': 'pre-existing acceptance integrity defect; not an RF8-introduced regression'}


def architecture_comparison():
    import io
    import runpy
    import tarfile
    arch = runpy.run_path(str(ROOT / 'tools/gnd_arch.py'))
    layer_map = ROOT / 'tools/gnd_layers.json'
    def summarize(metrics):
        return {'modules': len(metrics['modules']), 'runtime_sccs': metrics['sccs']['runtime'],
                'module_only_sccs': metrics['sccs']['module_only'],
                'wrong_way_edges': len(metrics['layering']['wrong_way']),
                'entry_violations': len(metrics['entrypoints']['violations']) if 'entrypoints' in metrics else None,
                'private_import_count': len(metrics['private_imports']),
                'ast_identical_groups': len(metrics['duplicates']['ast_identical']),
                'largest_modules': [{'module': r['module'], 'lines': r['lines']}
                                    for r in sorted(metrics['modules'], key=lambda r: r['lines'], reverse=True)[:5]]}
    archive = subprocess.check_output(['git', 'archive', 'f5a8318', 'src/gnd', 'tools/gnd_layers.json'], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix='rf9-architecture-base-') as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as content:
            content.extractall(directory, filter='data')
        before = summarize(arch['measure'](Path(directory), Path(directory) / 'tools/gnd_layers.json'))
    after = summarize(arch['measure'](ROOT, layer_map))
    result = {'base': 'f5a83186f7c2215ac2b2afb0a010c2294eaa433a',
              'head': 'd440b2e37449ef46647d18c491c46d9bb8d3e851',
              'instrument': 'current tools/gnd_arch.py with each source revision own layer map',
              'before': before, 'after': after,
              'boundary': 'explicit AST edges only; implicit parent execution omitted; private count includes compatibility imports and duplicate groups are heuristic candidates'}
    assert before['modules'] == 148 and after['modules'] == 227
    assert len(before['runtime_sccs']) == 5 and not after['runtime_sccs']
    (OUT / 'architecture-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    results = {'subject': 'd440b2e37449ef46647d18c491c46d9bb8d3e851',
               'command': 'PYTHONDONTWRITEBYTECODE=1 .venv/bin/python .gnd-planning/milestones/code-refactoring/evidence/RF9/reproductions.py',
               'primary_contract_equality': contract_equality(),
               'A_annotation_resolution': annotation_resolution(),
               'D_literal_getattr_inventory': literal_getattr_inventory(),
               'D_early_cache_observer': early_cache_observer(),
               'D_offline_import_guard': offline_import_guard(),
               'B_parent_package_edges': parent_package_edges(),
               'C_terminal_acceptance': terminal_acceptance(),
               'B_architecture_comparison': architecture_comparison()}
    (OUT / 'reproductions.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
