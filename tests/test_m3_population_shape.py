"""Positive shape acceleration never broadens the authoritative schema."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator
from gnd import population
from gnd.errors import ValidationIssue
from gnd.model import load_model

FIXTURES=Path(__file__).parent/'fixtures/skeleton'
def document():
    return json.loads((FIXTURES/'population.good.json').read_text())
def accept(doc,schema=None):
    from gnd.population_shape import accepts_shape
    return accepts_shape(doc, population._prepared_population_schema(population._load_population_schema()) if schema is None else schema)
def issues(doc,schema):
    return [ValidationIssue(path=e.json_path,message=e.message,rule_id=f'jsonschema:{e.validator}')
            for e in sorted(Draft202012Validator(schema).iter_errors(doc),key=lambda e:e.json_path)]

def test_valid_population_avoids_python_schema_walk(monkeypatch):
    def unwanted(*args,**kwargs):
        raise AssertionError('valid document repeated Draft iter_errors')
    model=load_model(FIXTURES/'model.orm.yaml')
    monkeypatch.setattr(Draft202012Validator,'iter_errors',unwanted)
    loaded=population.load_population(FIXTURES/'population.good.json',model=model)
    assert loaded.matches_validation_marker(model)

@pytest.mark.parametrize('version',[None,1,2,2.0,True])
@pytest.mark.parametrize('value',['original',None,{'$opaque':'existing marker'},{'$opaque':''},{'$opaque':'x','extra':1}])
def test_conditional_and_errors_match_original(version,value):
    doc=document()
    if version is not None: doc['format_version']=version
    doc['facts']['movie_has_title'][0]['title']=value
    schema=population._load_population_schema()
    expected=issues(doc,schema)
    assert not accept(doc) or not expected
    assert population._schema_issues(doc)==expected

@pytest.mark.parametrize('version',[None,1,2])
def test_supported_good_cases_and_instances_policy(version):
    doc=document()
    if version is not None: doc['format_version']=version
    assert accept(doc)
    if version==2:
        doc['facts']['movie_has_title'][0]['title']={'$opaque':'existing marker'}
        assert accept(doc)
    doc['instances']['movie']=[{'$opaque':'existing marker'}]
    assert not accept(doc)
    assert population._schema_issues(doc)==issues(doc,population._load_population_schema())

def test_original_document_retains_types_and_identity():
    doc=document()
    doc['facts']['movie_released_in_year'][0]['year']=2006.0
    doc['facts']['movie_has_title'][0]['title']='é😊'
    before=copy.deepcopy(doc); row=doc['facts']['movie_released_in_year'][0]
    assert accept(doc)
    assert doc==before and row is doc['facts']['movie_released_in_year'][0]
    assert type(row['year']) is float

def test_schema_content_change_and_loader_seam(monkeypatch):
    doc=document(); schema=population._load_population_schema(); calls=[]
    def loader(): calls.append(True); return schema
    monkeypatch.setattr(population,'_load_population_schema',loader)
    assert population._schema_issues(doc)==[]
    schema['properties']['population']['properties']['model']['minLength']=1000
    assert population._schema_issues(doc)==issues(doc,schema)
    assert len(calls)==2

@pytest.mark.parametrize('schema',[
    {'type':'string','pattern':'^blocked$'},
    {'type':'number','minimum':100},
    {'$ref':'https://example.invalid/schema'},
    {'if':{'type':'integer'},'then':{'const':1},'else':{'const':2}},
    {'type':'object','$id':'nested'},
    {'type':'string','minLength':True},
    {'type':'array','items':[]},
    {'type':'object','required':'key'},
])
def test_unsupported_schema_falls_back(schema):
    assert not accept('permitted only by ignored constraint',schema)

@pytest.mark.parametrize('schema,doc',[
    ({'type':'integer','enum':[1,2]},True),
    ({'type':'integer','enum':[1,2]},2.0),
    ({'enum':['x']},1),
    ({'type':'string','minLength':2},'😊'),
    ({'type':'array','items':{'type':'string'}},('x',)),
    ({'anyOf':[{'type':'string'},{'type':'integer'}]},False),
])
def test_scalar_algorithm_rejections(schema,doc):
    assert not accept(doc,schema)

def test_compilation_bounds_and_cycles():
    cycle={'type':'array'}; cycle['items']=cycle
    assert not accept([],cycle)
    node={'type':'array'}; deep=node
    for _ in range(60):
        child={'type':'array'}; deep['items']=child; deep=child
    assert not accept([],node)
    assert not accept({}, {'type':'object','properties':{str(i):{'type':'string'} for i in range(5000)}})
    assert not accept('x',{'type':'string','description':'x'*(1024*1024+1)})

def test_patched_draft_lookup_dispatch_is_preserved(monkeypatch):
    seen=[]
    def spy(schema): seen.append(schema); return Draft202012Validator(schema)
    monkeypatch.setattr(population,'Draft202012Validator',spy)
    assert population._schema_issues(document())==[]
    assert len(seen)==1


@pytest.mark.parametrize('schema,doc', [
    ({'type': 'string', 'pattern': '^blocked$'}, 'wrong'),
    ({'type': 'number', 'minimum': 100}, 1),
])
def test_unsupported_constraint_with_matching_base_type(schema, doc):
    assert not accept(doc, schema)
    assert issues(doc, schema)


def test_loaded_unknown_constraint_cannot_be_ignored(monkeypatch):
    schema = population._load_population_schema()
    schema['properties']['population']['properties']['model']['pattern'] = '^never$'
    monkeypatch.setattr(population, '_load_population_schema', lambda: schema)
    assert population._schema_issues(document()) == issues(document(), schema)
    assert population._schema_issues(document())


def test_compilation_cache_is_bounded_and_content_owned():
    from gnd.population_shape import _prepared
    _prepared.cache_clear()
    schema = {'type': 'string', 'minLength': 1}
    assert accept('x', schema)
    schema['minLength'] = 2
    assert not accept('x', schema)
    for n in range(12):
        assert accept('x' * 20, {'type': 'string', 'minLength': n})
    assert _prepared.cache_info().currsize <= 8


def test_numeric_protocol_object_is_not_a_json_number():
    class Convertible:
        def __float__(self):
            return 1.0
    assert not accept(Convertible(), {'type': 'number'})


@pytest.mark.parametrize('schema,doc', [
    ({'type': 'object', 'minLength': True}, {}),
    ({'type': 'string', 'items': []}, 'x'),
    ({'type': 'array', 'properties': []}, []),
])
def test_incompatible_sibling_operands_fall_back(schema, doc):
    assert not accept(doc, schema)


@pytest.mark.parametrize('schema,doc', [
    ({'type': None, 'enum': ['x']}, 'x'),
    ({'type': 'array', 'items': None}, []),
    ({'type': ['string', 'string']}, 'x'),
])
def test_malformed_type_and_items_operands_fall_back(schema, doc):
    assert not accept(doc, schema)


def test_oversized_schema_string_refused_before_serialization(monkeypatch):
    from gnd import population_shape
    calls = []
    original = population_shape.json.dumps
    def spy(*args, **kwargs):
        calls.append(True)
        return original(*args, **kwargs)
    monkeypatch.setattr(population_shape.json, 'dumps', spy)
    assert not accept('x', {'type': 'string', 'description': 'x' * (1024 * 1024 + 1)})
    assert calls == []


def test_aggregate_schema_strings_refused_before_serialization(monkeypatch):
    from gnd import population_shape
    def unwanted(*args, **kwargs):
        raise AssertionError('aggregate schema exceeded budget before serialization')
    monkeypatch.setattr(population_shape.json, 'dumps', unwanted)
    schema = {'type': 'string', 'title': 'x' * 600000, 'description': 'y' * 600000}
    with pytest.raises(population_shape._Unsupported):
        population_shape._bounded(schema)


@pytest.mark.parametrize('schema', [
    {'type': 'object', 'properties': {'x' * 1100000: {'type': 'string'}}},
    {'type': 'string', 'enum': ['x' * 600000, 'x' * 600000]},
    {'enum': [1 << (8 * 1024 * 1024)]},
])
def test_schema_keys_repetitions_and_integer_size_are_preallocation_bounded(schema, monkeypatch):
    from gnd import population_shape
    def unwanted(*args, **kwargs):
        raise AssertionError('serialization reached before schema byte refusal')
    monkeypatch.setattr(population_shape.json, 'dumps', unwanted)
    with pytest.raises(population_shape._Unsupported):
        population_shape._bounded(schema)


def conditional_schema(constant):
    return {
        'if': {'properties': {'v': {'const': constant}}, 'required': ['v']},
        'then': {'properties': {'p': {'type': 'string'}}, 'required': ['p']},
        'else': {'properties': {'p': {'type': 'integer'}}, 'required': ['p']},
    }


def test_unmasked_numeric_condition_observes_integral_float():
    schema = conditional_schema(2)
    assert not accept({'v': 2.0, 'p': 7}, schema)
    assert accept({'v': 2.0, 'p': 'then'}, schema)
    assert accept({'v': 1, 'p': 7}, schema)
    assert accept({'p': 7}, schema)


def test_unmasked_boolean_condition_does_not_equal_integer():
    schema = conditional_schema(1)
    assert not accept({'v': True, 'p': 'then'}, schema)
    assert accept({'v': True, 'p': 7}, schema)
    assert accept({'v': 1, 'p': 'then'}, schema)


def test_standalone_enum_does_not_admit_boolean():
    assert accept(1, {'enum': [1]})
    assert not accept(True, {'enum': [1]})
