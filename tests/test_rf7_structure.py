"""Current RF7 parser routing and architecture controls, with dirty siblings."""
import ast
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def parser_sources():
    return {p.relative_to(ROOT).as_posix(): p.read_text() for p in (ROOT / 'src/gnd').rglob('*.py')}


def assert_routing(sources):
    inventory = json.loads((ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF7/json-routing.json').read_text())
    expected = set(inventory if isinstance(inventory, list) else inventory['files'])
    assert expected <= set(sources)
    for path, source in sources.items():
        if path in {
            'src/gnd/examples/expense/extension.py',
            'src/gnd/examples/expense/project/cli/expense_cli.py',
            'src/gnd/examples/expense/rules_in_pyrel.py',
            'src/gnd/examples/bookrec/rules_in_pyrel.py',
            'src/gnd/examples/bookrec/stand_in_agent.py',
            'src/gnd/examples/expense/stand_in_agent.py',
            'src/gnd/examples/expense/prepare_currency.py',
            'src/gnd/examples/expense/prepare_meal_cap.py',
            'src/gnd/examples/release_governance/prepare_facts.py',
            'src/gnd/examples/release_governance/pyrel_queries.py',
            'src/gnd/examples/approvals/stand_in_agent.py',
            'src/gnd/examples/plan_apps/core.py',
            'src/gnd/examples/plan_apps/course/stand_in_bot.py',
            'src/gnd/examples/plan_apps/access/stand_in_bot.py',
            'src/gnd/examples/plan_apps/clinic/stand_in_bot.py',
            'src/gnd/examples/plan_apps/lease/stand_in_bot.py',
            'src/gnd/examples/plan_apps/trip/stand_in_bot.py',
            'src/gnd/examples/bookrec/extension/bookrec/cli.py',
            'src/gnd/examples/refunds/stand_in_learner.py',
            'src/gnd/skills/gnd-adopt/scripts/verify_migration.py',
            'src/gnd/skills/gnd-model-from-text/scripts/validate_model.py',
            'src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py',
        }:
            continue  # Standalone skill/example executables, outside GND module readers.
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == 'json'
                    and node.func.attr in ('loads', 'load', 'JSONDecoder')):
                assert path == 'src/gnd/export/souffle_runtime.py' and node.func.attr == 'JSONDecoder', path


def test_complete_routing_and_dirty_controls():
    sources = parser_sources()
    assert_routing(sources)
    for changed in ('missing', 'unrouted'):
        dirty = dict(sources)
        if changed == 'missing':
            del dirty['src/gnd/population.py']
        else:
            dirty['src/gnd/new_reader.py'] = 'import json\ndef read(raw):\n    return json.loads(raw)\n'
        with pytest.raises(AssertionError):
            assert_routing(dirty)


def assert_graph(result):
    layers = json.loads((ROOT / 'tools/gnd_layers.json').read_text())
    assert {row['module'] for row in result['modules']} == set(layers['modules'])
    assert not result['layering']['wrong_way']
    assert not layers['allow_list']
    assert not result['entrypoints']['violations']
    assert not any('gnd.input_policy' in cycle for cycle in result['sccs']['runtime'])


def test_current_graph_and_dirty_controls():
    spec = importlib.util.spec_from_file_location('rf7_arch', ROOT / 'tools/gnd_arch.py')
    arch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arch)
    metrics = arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')
    assert_graph(metrics)
    for key in ('layer', 'cycle', 'entry', 'unmapped'):
        dirty = copy.deepcopy(metrics)
        if key == 'layer':
            dirty['layering']['wrong_way'].append({'from': 'gnd.input_policy', 'to': 'gnd.cli'})
        elif key == 'cycle':
            dirty['sccs']['runtime'].append(['gnd.input_policy', 'gnd.population'])
        elif key == 'entry':
            dirty['entrypoints']['violations'].append({'from': 'gnd.commands.checking', 'to': 'gnd.model'})
        else:
            dirty['modules'].append({'module': 'gnd.missing'})
        with pytest.raises(AssertionError):
            assert_graph(dirty)
