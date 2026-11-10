"""Reproduced independent MC1 findings; every case is observed red pre-fix."""
from __future__ import annotations

import copy
import importlib
import json
from types import SimpleNamespace

import pytest
from test_mc1_guards import session_case
from test_mc1_model_includes import ROOT, proposed_ring, save, vocabulary, write_case

from gnd.errors import ModelValidationError
from gnd.model import load_model, retained_root

FIXTURE=ROOT/'tests/fixtures/mc1-includes'


def test_R1_public_batch():
    from support.cli_runner import run_gnd_text
    result=run_gnd_text('check',str(FIXTURE/'project.orm.yaml'),'--populations',str(FIXTURE),'--format','json')
    assert result.returncode==3,result.stderr
    payload=json.loads(result.stdout)
    assert payload['summary']['aggregate_exit']==3
    assert any(i['rule_id']=='include:unsupported-route' for i in payload['issues'])
    assert payload['rows']==[]


@pytest.mark.parametrize('kind',['api','text','json'])
def test_R2_composition_adapter(kind):
    from support.cli_runner import run_main

    from gnd.api import check
    path,pop=FIXTURE/'project.orm.yaml',FIXTURE/'clean.pop.json'
    if kind=='api':
        result=check(path,pop,composition='absent',sources='absent')
        assert result['exit_code']==3
        assert 'include:unsupported-route' in str(result)
    else:
        result=run_main(['check',str(path),str(pop),'--composition','absent','--sources','absent','--format',kind])
        assert result.returncode==3
        assert b'include:unsupported-route' in result.stdout+result.stderr


@pytest.mark.parametrize('kind',['lean','souffle'])
def test_R3_include_free_refusal_stays_frozen(tmp_path,kind):
    path=tmp_path/'plain.orm.json';path.write_text('{"version":4,"object_types":[],"fact_types":[],"unknown":1}')
    pop=tmp_path/'pop.json';pop.write_text('{}')
    function=getattr(importlib.import_module(f'gnd.export.{kind}_io'),f'export_{kind}')
    result=function(path,pop,**({'toolchain':'leanprover/lean4:v4.19.0'} if kind=='lean' else {}))
    assert (result.exit_code,result.reason)==(3,'input-invalid')


def test_R4_deep_direct_compose(tmp_path):
    from gnd.model._includes import compose
    path,own,_=write_case(tmp_path)
    nested={}
    for _ in range(500):nested={'nested':nested}
    own['source']=nested
    with retained_root(tmp_path) as fd,pytest.raises(ModelValidationError):
        compose(own,descriptor=fd,source=path)


@pytest.mark.parametrize('mode',['warning','error'])
def test_R5_include_id_model_is_not_own(tmp_path,mode):
    doc=vocabulary();doc['fact_types'][0]['constraints']=[proposed_ring('shared_warning')]
    path,own,_=write_case(tmp_path,doc)
    own['includes'][0]['id']='model'
    if mode=='error':
        own['source']={'kind':'prose','mode':'unattended','reviewer':'none','documents':[{'sha256':'0'*64,'label':'source'}]}
    save(path,own)
    if mode=='warning':
        model=load_model(path)
        assert all(o.origin!='model' for o in model._provenance)
        assert any(w.path.startswith('includes[model]:') for w in model.warnings)
    else:
        with pytest.raises(ModelValidationError) as caught:load_model(path)
        assert any(i.path.startswith('includes[model]:') for i in caught.value.issues)


@pytest.mark.parametrize('kind',['lean','souffle'])
def test_R6_raw_export_reason(kind):
    function=getattr(importlib.import_module(f'gnd.export.{kind}'),f'render_{kind}')
    result=function((FIXTURE/'project.orm.yaml').read_bytes(),(FIXTURE/'clean.pop.json').read_bytes(),
                    **({'toolchain':'leanprover/lean4:v4.19.0','model_format':'yaml'} if kind=='lean' else {}))
    assert (result.exit_code,result.reason)==(3,'include:unsupported-route')


@pytest.mark.parametrize('kind',['replay','case-models','copy'])
def test_R7_guard_precedes_explicit_hash(tmp_path,monkeypatch,kind):
    import gnd.exp.session_replay as replay
    from gnd.exp import session
    _,_,contract=session_case(tmp_path);case=contract.cases[0]
    def forbidden(*args):pytest.fail('explicit route hash ran before include guard')
    if kind=='replay':monkeypatch.setattr(replay,'_sha',forbidden)
    else:monkeypatch.setattr(session,'hashlib',SimpleNamespace(sha256=forbidden))
    with pytest.raises(ModelValidationError,match='include:unsupported-route'):
        if kind=='replay':replay._model(case,tmp_path)
        elif kind=='case-models':session._case_models(contract,tmp_path)
        else:session._copy_bound_model(case,tmp_path,tmp_path/'view')


def test_R7_guard_precedes_temporal_classification(tmp_path,monkeypatch):
    from gnd import terms
    from gnd.export.emit import render_pyrel
    from gnd.export.pyrel_runtime import ExportInputError
    path,own,_=write_case(tmp_path)
    own['object_types']=[{'id':'build_duration','name':'BuildDuration','kind':'value','primitive':'Duration'}]
    save(path,own);load_model(path)
    def forbidden(*args):pytest.fail('temporal classification ran before include guard')
    monkeypatch.setattr(terms,'uses_temporal',forbidden)
    with pytest.raises(ExportInputError,match='include:unsupported-route'):render_pyrel(path)


def test_R8_own_selector_is_preserved(tmp_path):
    path,own,_=write_case(tmp_path)
    ft=copy.deepcopy(vocabulary()['fact_types'][0]);ft['id']='own_uses';ft['constraints']=[proposed_ring('own_warning')]
    own['fact_types']=[ft];save(path,own)
    model=load_model(path)
    assert any(w.path=='$.fact_types[id=own_uses].constraints[0]' for w in model.warnings)


def test_R9_digest_newline_schema_parity(tmp_path):
    from jsonschema import Draft202012Validator

    from gnd.model._includes import parse_declarations
    from gnd.model._validation import _load_meta_schema
    _,own,_=write_case(tmp_path);own['includes'][0]['sha256']+='\n'
    assert not Draft202012Validator(_load_meta_schema()).is_valid(own)
    with pytest.raises(ModelValidationError):parse_declarations(own)


@pytest.mark.parametrize('kind',['lean','souffle'])
def test_raw_export_include_free_errors_stay_frozen(kind):
    function=getattr(importlib.import_module(f'gnd.export.{kind}'),f'render_{kind}')
    kwargs={'toolchain':'leanprover/lean4:v4.19.0'} if kind=='lean' else {}
    raw=b'{"version":4,"object_types":[],"fact_types":[],"unknown":1}'
    result=function(raw,b'{}',model_format='json',**kwargs)
    assert (result.exit_code,result.reason)==(3,'input-invalid')


def test_guard_keeps_raw_type_refusal_in_legacy_adapter():
    from gnd.export.souffle import render_souffle
    result=render_souffle('{"version":4,"object_types":[],"fact_types":[]}',b'{}',model_format='json')
    assert (result.exit_code,result.reason)==(3,'input-invalid')
