import json, tempfile
from pathlib import Path
from gnd import api
from gnd.model import load_model
from gnd.population import load_population
from gnd import checker
root=Path('tests/fixtures/compiled-snapshot')
raw=json.loads((root/'model.orm.json').read_text())
for ft in raw['fact_types']:
    if ft['id']=='var_filtered_compare':
        for role in ft['roles']: role['redact']=True
with tempfile.TemporaryDirectory() as td:
    mp=Path(td)/'redacted.orm.json'; mp.write_text(json.dumps(raw))
    red=api.check(mp,root/'nonnumeric.pop.json',compiled_operations=True)
    plain=api.check(mp,root/'nonnumeric.pop.json',compiled_operations=True,unredacted=True)
    selected=lambda p:[r for r in p['verdicts'] if r['constraint_type']=='compiled-subset' and r['verdict']=='fail']
    rr,pp=selected(red),selected(plain)
    assert rr and pp
    assert all(set(r['offending_facts'][0]) == {'redacted','roles'} for r in rr) 
    assert all('redacted' not in r['offending_facts'][0] for r in pp)
    assert red['assurance']['assurance_level']=='none'
    assert plain['assurance']['assurance_level']=='none'
    print(json.dumps({'redaction_probe':'pass','redacted_failure_rows':len(rr),'assurance':'none'}))
raw=json.loads((root/'model.orm.json').read_text())
for ft in raw['fact_types']:
    if ft['id']=='var_filtered_compare':
        ft.setdefault('constraints',[]).append({'type':'anchored','role':'var','source':'explicit','status':'confirmed','modality':'alethic','provenance':{'user_quote':'v1'}})
with tempfile.TemporaryDirectory() as td:
    mp=Path(td)/'anchored.orm.json'; mp.write_text(json.dumps(raw))
    payload=api.check(mp,root/'nonnumeric.pop.json',compiled_operations=True)
    assert payload['exit_code']==1, payload
    assert any(r['constraint_type']=='compiled-subset' and r['verdict']=='fail' for r in payload['verdicts'])
    assert any(r['constraint_type']=='anchored' for r in payload['verdicts'])
    assert payload['assurance']['assurance_level']=='none'
    print(json.dumps({'anchor_route_probe':'pass','compiled_fail_survives':True}))
