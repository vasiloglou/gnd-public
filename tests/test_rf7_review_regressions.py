"""Independently reproduced RF7 review findings and accepting siblings."""
import json

import pytest

from gnd.errors import ModelLoadError
from gnd.model import load_model_bytes
from gnd.model_queries import primitive_for


def shared_ancestor_types():
    types = {name: {'id': name, 'kind': 'value', 'primitive': primitive}
             for name, primitive in [('Q', 'Integer'), ('P', 'String'), ('Z', 'String')]}
    for name, parents in [('X', ['Q']), ('Y', ['P']), ('W', ['Z']),
                          ('A', ['X', 'Y']), ('B', ['X', 'W']), ('R', ['A', 'B'])]:
        types[name] = {'id': name, 'kind': 'entity', 'inherits_reference': True,
                       'subtype_of': parents}
    return types


@pytest.mark.parametrize('variant', ['truthy', 'strict'])
def test_shared_ancestor_cannot_hide_parent_ambiguity(variant):
    types = shared_ancestor_types()
    assert primitive_for('A', types, variant=variant) is None
    assert primitive_for('B', types, variant=variant) is None
    assert primitive_for('R', types, variant=variant) is None
    types['Q']['primitive'] = 'String'
    assert primitive_for('R', types, variant=variant) == 'String'


@pytest.mark.parametrize('token', ['NaN', 'Infinity', '-Infinity', '1e999'])
@pytest.mark.parametrize('source', ['m.orm.yaml', 'm.json'])
def test_json_policy_refusal_does_not_become_yaml_string(token, source):
    raw = ('{"version":1,"model_id":' + token + ',"object_types":[],"fact_types":[]}').encode()
    with pytest.raises(ModelLoadError, match='JSON'):
        load_model_bytes(raw, source=source)
    valid = {'version': 1, 'model_id': 'finite', 'object_types': [], 'fact_types': []}
    assert load_model_bytes(json.dumps(valid).encode(), source=source).model_id == 'finite'


def test_yaml_unquoted_flow_mapping_remains_accepted():
    raw = b'{version: 1, model_id: finite, object_types: [], fact_types: []}'
    assert load_model_bytes(raw, source='m.orm.yaml').model_id == 'finite'


def test_mutating_pairs_hook_cannot_erase_duplicate_evidence():
    from gnd.input_policy import loads

    def clear(items):
        items.clear()
        return {}

    with pytest.raises(ValueError, match='duplicate'):
        loads('{"x":1,"x":2}', object_pairs_hook=clear)
    assert loads('{"x":1}', object_pairs_hook=clear) == {}


def test_sidecar_read_is_bounded_and_maps_cap_error(tmp_path, monkeypatch):
    from io import BytesIO
    from pathlib import Path

    from gnd import input_policy
    from gnd.synth.provenance import SidecarError, read_sidecar

    reads = []

    class Stream(BytesIO):
        def read(self, size=-1):
            reads.append(size)
            return super().read(size)

    monkeypatch.setattr(input_policy, 'MAX_BYTES', 8)
    monkeypatch.setattr(Path, 'open', lambda *args, **kwargs: Stream(b' ' * 100))
    with pytest.raises(SidecarError, match='byte cap'):
        read_sidecar(tmp_path / 'sidecar.json')
    assert reads == [9]


def test_standalone_primitive_shared_ancestor_ambiguity():
    from gnd.export.pyrel_runtime import ModelIndex
    types = shared_ancestor_types()
    index = ModelIndex({'object_types': list(types.values())})
    assert index.primitive('R') is None
    types['Q']['primitive'] = 'String'
    assert ModelIndex({'object_types': list(types.values())}).primitive('R') == 'String'
