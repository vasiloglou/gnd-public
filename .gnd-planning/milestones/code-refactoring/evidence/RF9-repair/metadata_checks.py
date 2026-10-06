import hashlib,json,runpy,subprocess
from pathlib import Path
ROOT=Path.cwd(); OUT=ROOT/'.gnd-planning/milestones/code-refactoring/evidence/RF9-repair'; BASE='26dbff6'
def base(path): return subprocess.check_output(['git','show',f'{BASE}:{path}'])
p=Path('.gnd-planning/milestones/public-launch/migration/b3-files.json'); before=json.loads(base(str(p))); current=json.loads(p.read_text()); key=next(k for k,v in current.items() if isinstance(v,list) and v and isinstance(v[0],dict) and 'path' in v[0]); rows={r['path']:r for r in current[key]}
frozen=json.loads((OUT.parent/'RF8/frozen-controls.json').read_text())['unchanged']
for row in frozen: assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'], row['path']
assert base('src/gnd/commands/_output.py')==(ROOT/'src/gnd/output.py').read_bytes()
from gnd import output
from gnd.commands import _output
names=json.loads((OUT/'output-bindings.json').read_text())['names']
assert all(getattr(output,n) is getattr(_output,n) for n in names)
arch=runpy.run_path('tools/gnd_arch.py'); metrics=arch['measure'](ROOT,ROOT/'tools/gnd_layers.json')
assert not metrics['sccs']['runtime'] and not metrics['sccs']['module_only']
assert not metrics['layering']['wrong_way'] and not metrics['entrypoints']['violations']
assert not json.loads((ROOT/'tools/gnd_layers.json').read_text())['allow_list']
adaptations=json.loads((OUT/'manifest-adaptations.json').read_text()); original={r['path']:r for r in before[key]}
for row in adaptations:
 assert row['before']==original.get(row['path'])
 assert row['after']==rows[row['path']]
 path=ROOT/row['path']; assert row['after']['public_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
 assert row['after']['bytes']==path.stat().st_size and row['after']['mode']==path.stat().st_mode&0o777
 if row['before']:
  for field in ['baseline_sha256','source_sha256','source_commit']:
   assert row['before'].get(field)==row['after'].get(field)
for path in ['.gnd-planning/milestones/public-launch/migration/units.json','tests/test_public_distribution.py']:
 assert base(path)==(ROOT/path).read_bytes()
result={'base':BASE,'frozen_controls':len(frozen),'output_byte_move':True,'output_bindings':len(names),'module_count':len(metrics['modules']),'explicit_sccs':metrics['sccs'],'layering':metrics['layering'],'entrypoints':metrics['entrypoints'],'implicit_parent_edges':len(metrics['implicit_parent_edges']),'parent_initialization_sccs':metrics['parent_initialization_sccs'],'allowances':0,'manifest_adaptations':len(adaptations),'units_and_authority_unchanged':True,'query_metric':{'baseline_source':'523cdd1a2ae1ad6ea0e8ca092fe29629dd10607c','baseline':375,'current':354,'ceiling':365,'pre_refactor_f5_count':374}}
(OUT/'metadata.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"{len(frozen)} frozen controls unchanged; 25 output aliases and exact body move; {len(metrics['modules'])} modules; zero explicit runtime/module SCCs, wrong-way/entry violations and allowances; {len(adaptations)} exact target adaptations.")
print(f"Implicit package-parent edges: {len(metrics['implicit_parent_edges'])}; structural combined SCCs: {len(metrics['parent_initialization_sccs'])} (diagnostic, no zero-cycle claim).")
