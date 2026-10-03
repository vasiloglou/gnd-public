from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from gnd.model import Model, load_model
from gnd.population import Population, load_population

_SOURCE = {'kind': 'text-conversation', 'confidence': 'standard', 'mode': 'guided'}

def _write(path: Path, doc: dict[str, Any]) -> Path:
    with path.open('w', encoding='utf-8') as handle:
        YAML().dump(doc, handle)
    return path

def _entity(object_id: str, name: str, value_type: str) -> dict[str, Any]:
    return {'id': object_id, 'name': name, 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': value_type}}

def _value_type(object_id: str, name: str, primitive: str='String') -> dict[str, Any]:
    return {'id': object_id, 'name': name, 'kind': 'value', 'primitive': primitive}

def _subtype(object_id: str, name: str, supertypes: list[str]) -> dict[str, Any]:
    return {'id': object_id, 'name': name, 'kind': 'entity', 'subtype_of': supertypes, 'inherits_reference': True, 'derivation': 'asserted'}

def _binary(fact_type_id: str, reading: str, roles: list[tuple[str, str]]) -> dict[str, Any]:
    return {'id': fact_type_id, 'reading': reading, 'roles': [{'object_type': object_type, 'role_name': role_name} for object_type, role_name in roles]}

def _model(tmp_path: Path, object_types: list[dict[str, Any]], fact_types: list[dict[str, Any]], constraints: list[dict[str, Any]] | None=None) -> Model:
    doc: dict[str, Any] = {'version': 1, 'source': dict(_SOURCE), 'object_types': object_types, 'fact_types': fact_types}
    if constraints:
        doc['constraints'] = constraints
    return load_model(_write(tmp_path / 'model.orm.yaml', doc))

def _population(tmp_path: Path, model: Model, *, covers: list[str] | None=None, facts: dict[str, list[dict[str, Any]]] | None=None, instances: dict[str, list[Any]] | None=None) -> Population:
    header: dict[str, Any] = {'population': {'model': 'model.orm.yaml', 'source': 'fixture', 'label': 'conforming'}}
    if covers is not None:
        header['population']['covers'] = covers
    header['facts'] = facts if facts is not None else {}
    if instances is not None:
        header['instances'] = instances
    return load_population(_write(tmp_path / 'population.yaml', header), model=model)
VEHICLE_TYPES = [_entity('vehicle', 'Vehicle', 'vehicle_id'), _value_type('vehicle_id', 'VehicleId'), _value_type('plate', 'Plate'), _value_type('colour', 'Colour'), _subtype('car', 'Car', ['vehicle'])]
VEHICLE_FACTS = [_binary('car_has_colour', '{Car} has colour {Colour}', [('car', 'car'), ('colour', 'colour')]), _binary('vehicle_has_plate', '{Vehicle} has plate {Plate}', [('vehicle', 'vehicle'), ('plate', 'plate')])]
