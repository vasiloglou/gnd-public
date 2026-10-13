"""SDK aggregate feasibility only; no application acceptance claim."""
import json,runpy
from pathlib import Path
from relationalai.semantics.std import aggregates
for label in ['baseline','currency','repeated','zero','empty']:
    name='currency' if label=='currency' else 'baseline'
    r=runpy.run_path(name+'.py');seed=json.loads(Path(name+'.json').read_bytes())
    if label=='repeated':
        for row in seed['facts']['expense_has_amount']:row['amount']=60
    if label=='zero':
        seed['facts']['expense_is_approved']=[];seed['facts']['expense_approved_by_chain']=[]
    if label=='empty':seed['facts']={key:[] for key in seed['facts']}
    o=r['ApplicationOracle'](r['admit_model'](r['_parse_document'](r['MODEL_TEXT'])),seed,config=r['local_config']())
    e=o.refs('expense_submitted_by_employee')['expense'];a=o.refs('expense_has_amount')['amount']
    q=o.m.where(o.pattern('expense_submitted_by_employee',{'expense':e}),o.pattern('expense_has_amount',{'expense':e,'amount':a}))
    totals=o._rows(q.select(aggregates.count(e),aggregates.sum(e,a)))
    approved=o._rows(o.m.where(o.pattern('expense_is_approved',{'expense':e})).select(aggregates.count(e)))
    grouped=None
    if label=='currency':
        c=o.refs('expense_has_currency')['currency']
        grouped=o._rows(q.where(o.pattern('expense_has_currency',{'expense':e,'currency':c})).select(c,aggregates.sum(e,a).per(c)))
    print(json.dumps({'scenario':label,'native_totals_rows':totals,'native_approved_rows':approved,'native_currency_rows':grouped},sort_keys=True))
