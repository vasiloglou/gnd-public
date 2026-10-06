"""Observed-red regressions for the two RF5 independent-review findings."""
import copy
import json
import shutil

import pytest
from support.repository import REPO_ROOT as ROOT
from test_rf5_commands import architecture


def policy():
    return json.loads((ROOT / 'tools/gnd_entrypoints.json').read_text())


def test_entrypoint_rejects_another_commands_domain_service():
    arch = architecture()
    metrics = arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')
    altered = copy.deepcopy(metrics)
    altered['edges'].append({'from': 'gnd.commands.verify', 'to': 'gnd.synth.service',
                             'kind': 'module', 'line': 1})
    assert len(arch.entrypoint_rule(altered, policy())['violations']) == 1


def test_entrypoint_rejects_unused_exception_permission():
    arch = architecture()
    metrics = arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')
    altered = policy()
    row = {'source': 'gnd.commands.exp', 'target': 'gnd.solve',
           'reason': 'RF5 countercheck: this unneeded edge must not be authorized'}
    if row['source'] not in {entry['source'] for entry in altered['exceptions']
                            if entry['target'] == row['target']}:
        altered['exceptions'].append(row)
    with pytest.raises(ValueError, match='unused entry-point exception'):
        arch.entrypoint_rule(metrics, altered)


@pytest.mark.parametrize('keep_policy', [True, False], ids=['policy-present', 'policy-absent'])
def test_measure_rejects_missing_group_even_without_the_old_marker(tmp_path, keep_policy):
    arch = architecture()
    mapping = json.loads((ROOT / 'tools/gnd_layers.json').read_text())
    clone = tmp_path / 'countercheck'
    # Copy only actual mapped Python files. No imports/native processes execute.
    for relative in arch.discover_modules(ROOT, mapping['excluded']).values():
        target = clone / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    (clone / 'src/gnd/commands/checking.py').unlink()
    del mapping['modules']['gnd.commands.checking']
    (clone / 'tools').mkdir()
    layers = clone / 'tools/gnd_layers.json'
    layers.write_text(json.dumps(mapping))
    if keep_policy:
        shutil.copyfile(ROOT / 'tools/gnd_entrypoints.json', clone / 'tools/gnd_entrypoints.json')
    with pytest.raises(arch.ToolError) as refusal:
        arch.measure(clone, layers)
    assert refusal.value.code == 3
