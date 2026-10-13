import copy,json,tempfile
from pathlib import Path
from gnd import api
from gnd.model import load_model
from gnd.population import load_population
root=Path('tests/fixtures/compiled-snapshot')
doc=json.loads((root/'model.orm.json').read_text())
for ft in doc['fact_types']:
    if ft['id']=='var_filtered_compare':
        for role in ft['roles']:role['redact']=True
with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'model.orm.json';path.write_text(json.dumps(doc))
    model=load_model(path)
    cached=copy.deepcopy(model._compiled)
    pop=load_population(root/'nonnumeric.pop.json',model=model)
    for op in model.operations:
        if op['id']=='filter_compare':op['id']='renamed_compare'
    result=api.check(model,pop,compiled_operations=True)
    failed=[r for r in result['verdicts'] if r['constraint_type']=='compiled-subset' and r['verdict']=='fail']
    assert result['exit_code']==1 and failed,result
    assert all('renamed_compare' in r['constraint_ref'] for r in failed)
    assert all(set(r['offending_facts'][0])=={'redacted','roles'} for r in failed)
    assert result['assurance']['assurance_level']=='none'
    assert cached==model._compiled
    print('renamed operation: fresh redacted locator, unchanged side table, assurance none')
