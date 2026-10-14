"""Reproduce bounded phase12 assertion RED controls without changing runtime."""
import importlib.util
import sys

import pytest
from pydantic_core import core_schema

case = sys.argv[1]
if case == 'r1-bound':
    spec = importlib.util.spec_from_file_location(
        'gnd.population_shape', '/private/tmp/gnd-phase12-r1-population_shape.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules['gnd.population_shape'] = module
    selection = 'aggregate_schema_strings or schema_keys_repetitions_and_integer_size'
else:
    from gnd import population_shape as shape
    if case == 'numeric-condition':
        shape._condition = lambda schema: lambda doc: (
            type(doc.get('v')) is int and doc['v'] == schema['properties']['v']['const']
        )
        selection = 'unmasked_numeric_condition'
    elif case == 'boolean-condition':
        shape._condition = lambda schema: lambda doc: (
            'v' in doc and doc['v'] == schema['properties']['v']['const']
        )
        selection = 'unmasked_boolean_condition'
    elif case == 'enum':
        shape._constant = lambda value: core_schema.literal_schema([value])
        selection = 'standalone_enum'
    else:
        raise ValueError(case)
raise SystemExit(pytest.main(['tests/test_m3_population_shape.py', '-q', '-k', selection]))
