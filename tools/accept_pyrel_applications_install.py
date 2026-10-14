"""Execute finite application acceptance from a fresh wheel outside the checkout."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAP=12*1024*1024
GRAPHICS={'bookrec':['flow','eligibility','evolution'],'expense':['flow','limits','currency']}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_origin(origin,venv,checkout):
    path=Path(origin).resolve()
    if not path.is_relative_to(Path(venv).resolve()) or path.is_relative_to(Path(checkout).resolve()):
        raise ValueError('installed origin is not isolated from checkout')


def verify_wheel_resources(wheel,source_root):
    source_root=Path(source_root)
    required={'gnd/__init__.py','gnd/api.py','gnd/export/applications.py','gnd/export/pyrel_runtime.py'}
    for domain,names in GRAPHICS.items():
        required.update(f'gnd/examples/{domain}/tutorial-assets/{name}.svg' for name in names)
        required.add(f'gnd/examples/{domain}/tutorial-assets/sources.json')
    for domain in ['bookrec','expense','release_governance/runtime-environment']:
        home=source_root/'src/gnd/examples'/domain
        required.update(p.relative_to(source_root/'src').as_posix() for p in home.rglob('*')
                        if p.is_file() and '__pycache__' not in p.parts)
    try:
        if Path(wheel).stat().st_size>CAP:raise ValueError('wheel compressed size exceeds cap')
        with zipfile.ZipFile(wheel) as archive:
            if sum(i.file_size for i in archive.infolist())>CAP:raise ValueError('wheel payload exceeds cap')
            names=archive.namelist()
            if len(names)>10000 or len(names)!=len(set(names)):raise ValueError('wheel inventory invalid')
            missing=required-set(names)
            if missing:raise ValueError('missing wheel resource: '+min(missing))
            rows={}
            for name in sorted(required):
                raw=archive.read(name)
                if raw!=(source_root/'src'/name).read_bytes():raise ValueError('changed wheel resource: '+name)
                rows[name]=hashlib.sha256(raw).hexdigest()
    except (OSError,zipfile.BadZipFile) as error:
        raise ValueError('invalid wheel: '+type(error).__name__) from error
    return {'wheel_sha256':sha(wheel),'resources':rows}


def verify_learning_paths(data,group,lane):
    if (not isinstance(group,str) or group not in {'bookrec','expense'}
            or not isinstance(lane,str) or lane not in {'offline','pyrel'}
            or not isinstance(data,dict) or type(data.get('count')) is not int
            or not isinstance(data.get('records'),list) or len(data['records'])>1000
            or any(not isinstance(r,dict) or not isinstance(r.get('page'),str)
                   or not isinstance(r.get('lane'),str) or r['lane'] not in {'offline','pyrel'}
                   or not isinstance(r.get('status'),str) or r['status'] not in {'passed','skipped','failed'}
                   for r in data['records'])):
        raise ValueError('malformed tutorial receipt')
    pages,total,native=(7,71,10) if group=='bookrec' else (4,57,11)
    rows=data['records'];passed=[r for r in rows if r['status']=='passed']
    if len(rows)!=total or len({r['page'] for r in rows})!=pages:
        raise ValueError('tutorial inventory incomplete')
    selected_native=[r for r in rows if r['lane']=='pyrel']
    if len(selected_native)!=native or any(r['status']!='passed' for r in rows if lane=='pyrel' or r['lane']=='offline'):
        raise ValueError('tutorial native steps skipped or failed')
    if lane=='offline' and any(r['status']!='skipped' for r in selected_native):
        raise ValueError('tutorial offline omission not explicit')
    if data['count']!=len(passed) or len(passed)!=(total if lane=='pyrel' else total-native):
        raise ValueError('tutorial selected count mismatch')


def source_identity():
    def git(*args):
        return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    return {'commit':git('rev-parse','HEAD'),'dirty_paths_sha256':hashlib.sha256(git('status','--porcelain').encode()).hexdigest(),
            'harness_sha256':sha(__file__),'sources':{p.relative_to(ROOT).as_posix():sha(p) for base in ['docs','overrides','src/gnd']
                for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts},
            'tools':{name:sha(ROOT/'tools'/name) for name in ['run_tutorials.py','check_docs.py','measure_pyrel_applications.py']},
            'site_config_sha256':sha(ROOT/'zensical.toml')}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();out=args.out.resolve()
    if out.exists() or out.is_relative_to(ROOT):parser.error('out must be fresh and outside checkout')
    out.mkdir(parents=True)
    identity=source_identity()
    env={k:v for k,v in os.environ.items() if k in {'PATH','HOME','TMPDIR','TMP','TEMP','LANG','LC_ALL','LC_CTYPE','SystemRoot','UV_CACHE_DIR','UV_PYTHON_INSTALL_DIR'}}
    env['PYTHONNOUSERSITE']='1';commands=[]
    def run(argv,cwd=out,timeout=600):
        argv=[str(a) for a in argv];p=subprocess.run(argv,cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout,check=False)
        commands.append({'argv':argv,'cwd':str(cwd),'exit':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr.encode()).hexdigest()})
        print(p.stdout,end='',flush=True)
        if p.returncode:raise RuntimeError(f'{argv[0]} exit{p.returncode}: {p.stderr[-2000:]}')
        return p.stdout
    run(['uv','build','--wheel','--out-dir',out/'wheel'],ROOT)
    wheel=next((out/'wheel').glob('*.whl'));inventory=verify_wheel_resources(wheel,ROOT)
    run(['uv','venv','--python',sys.executable,out/'base'])
    base=out/'base/bin/python';run(['uv','pip','install','--python',base,wheel])
    origin=run([base,'-I','-c','import gnd; print(gnd.__file__)']).strip();verify_origin(origin,out/'base',ROOT)
    package=Path(origin).parent
    # Only resource mirrors, no importable source package or editable .pth.
    for domain in ['bookrec','expense','release_governance']:
        shutil.copytree(package/'examples'/domain,out/'src/gnd/examples'/domain)
    runtime=out/'src/gnd/export/pyrel_runtime.py';runtime.parent.mkdir(parents=True);shutil.copy2(package/'export/pyrel_runtime.py',runtime)
    lock_home=package/'examples/release_governance/runtime-environment'
    shutil.copytree(lock_home,out/'tutorials/runtimes')
    run(['uv','sync','--project',out/'tutorials/runtimes','--locked','--only-group','tutorial-runtimes','--python','3.13'])
    native=out/'tutorials/runtimes/.venv/bin/python'
    isolation=json.loads(run([native,'-I','-c',"import importlib.util,json,sys;from importlib.metadata import version;assert importlib.util.find_spec('gnd') is None;print(json.dumps({'python':sys.version.split()[0],'relationalai':version('relationalai'),'duckdb':version('duckdb'),'gnd_absent':True}))"]))
    env['GND_TUTORIAL_PYREL_PYTHON']=str(native)
    shutil.copytree(ROOT/'docs',out/'docs');shutil.copytree(ROOT/'overrides',out/'overrides');shutil.copy2(ROOT/'zensical.toml',out/'zensical.toml')
    (out/'tools').mkdir()
    for name in ['run_tutorials.py','check_docs.py','measure_pyrel_applications.py']:
        shutil.copy2(ROOT/'tools'/name,out/'tools'/name)
    shutil.copytree(ROOT/'tests/fixtures/pyrel_applications',out/'tests/fixtures/pyrel_applications')
    execute=out/'tools/execute_paths.py'
    execute.write_text('''import json,os,sys
from pathlib import Path
from run_tutorials import groups,run_pages
root=Path(__file__).resolve().parents[1]
for group in ['bookrec','expense']:
 for lane in ['offline','pyrel']:
  rows=[];count=run_pages(groups(root)[group],root/(group+'-'+lane+'-work'),Path(sys.executable),lane,receipts=rows,group=group)
  (root/(group+'-'+lane+'-steps.json')).write_text(json.dumps({'count':count,'records':rows},indent=2)+'\\n')
''')
    run([base,execute])
    for group in ['bookrec','expense']:
        for lane in ['offline','pyrel']:
            verify_learning_paths(json.loads((out/(group+'-'+lane+'-steps.json')).read_text()),group,lane)
    compare=out/'tools/check_gnd_corpus.py'
    compare.write_text('''import json
from pathlib import Path
from gnd.api import check
root=Path(__file__).resolve().parents[1];corpus=root/'tests/fixtures/pyrel_applications'
matrix=json.loads((corpus/'matrix.json').read_text());answers=json.loads((corpus/'answers.json').read_text());rows=[]
import hashlib
approval=json.loads((corpus/'approval.json').read_text())
assert set(matrix['cases'])==set(answers) and len(answers)==137
assert hashlib.sha256((corpus/'matrix.json').read_bytes()).hexdigest()==approval['matrix_sha256']
assert hashlib.sha256((corpus/'answers.json').read_bytes()).hexdigest()==approval['answers_sha256']
for name,case in matrix['cases'].items():
 report=check(root/case['model'],root/case['population'],unredacted=True);answer=answers[name]
 values={r['constraint_ref']:r['verdict'] for r in report['verdicts']}
 values.update({r['derivation_ref']:r['verdict'] for r in report.get('derivations') or []})
 assert values==answer['observed_gnd_verdicts'] and report['exit_code']==answer['observed_gnd_exit'],name
 assert {r['constraint_ref']:r['offending_facts'] for r in report['verdicts'] if r['constraint_type']=='guarded'}==answer['guarded_witnesses'],name
 rows.append({'case':name,'exit':report['exit_code'],'verdicts':values})
assert len(rows)==len(answers)==137
(root/'gnd-corpus.json').write_text(json.dumps({'matched':len(rows),'denominator':len(answers),'rows':rows},indent=2)+'\\n')
print('installed GND137 verdict/witness/exit controls passed')
''')
    run([base,compare])
    run([base,out/'tools/measure_pyrel_applications.py','--mode','acceptance','--python',native,'--out',out/'native-corpus.json'],timeout=1200)
    report=json.loads((out/'native-corpus.json').read_text())
    if report['matched']!=137 or report['denominator']!=137:raise ValueError('incomplete native acceptance')
    if report['agreement']['matches']!=2321 or report['agreement']['comparable_rows']!=2321 or len(report['agreement']['intentional_disagreements'])!=2:
        raise ValueError('native agreement denominator changed')
    run([base,'-m','gnd','export','pyrel','src/gnd/examples/bookrec/model.orm.yaml','--out','isolation.py'])
    probe="import ast,runpy,sys;from pathlib import Path;p=Path('isolation.py');tree=ast.parse(p.read_text());assert not any(isinstance(n,(ast.Import,ast.ImportFrom)) and 'gnd' in ast.dump(n) for n in ast.walk(tree));sys.argv=[str(p),'src/gnd/examples/bookrec/seed.population.json','--accept','--out','isolation.json'];\ntry:runpy.run_path(str(p),run_name='__main__')\nexcept SystemExit as e:assert e.code==0\nassert not any(n=='gnd' or n.startswith('gnd.') or n.startswith('tests.') for n in sys.modules);print('generated native import isolation passed')"
    run([native,'-I','-c',probe])
    run([base,'-m','gnd','export','pyrel','src/gnd/examples/expense/model.orm.json','--out','expense-isolation.py'])
    run([native,'-I','-c',probe.replace('isolation.py','expense-isolation.py').replace('bookrec/seed.population.json','expense/seed.population.json').replace('isolation.json','expense-isolation.json')])
    run(['uv','tool','run','--from','zensical==0.0.67','zensical','build','--strict'])
    run([base,out/'tools/check_docs.py',out/'site'])
    for domain,names in GRAPHICS.items():
        for name in names:
            if (out/'site/assets/applications'/f'{domain}-{name}.svg').read_bytes()!=(package/'examples'/domain/'tutorial-assets'/f'{name}.svg').read_bytes():
                raise ValueError('installed graphic twin changed')
        page=out/'site'/domain/('07-native' if domain=='bookrec' else '04-native')/'index.html'
        if not all(f'{domain}-{name}.svg' in page.read_text() for name in names):raise ValueError('installed graphic URL missing')
    # Persistent tutorial work trees bind actual model/program/input/output leaves.
    artifacts={p.relative_to(out).as_posix():sha(p) for group in ['bookrec','expense'] for lane in ['offline','pyrel']
               for p in (out/(group+'-'+lane+'-work')).rglob('*') if p.is_file() and p.suffix in {'.json','.yaml','.py','.svg'} and '__pycache__' not in p.parts}
    artifacts.update({p.relative_to(out).as_posix():sha(p) for folder in ['docs','overrides','site','tools'] for p in (out/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts})
    artifacts.update({p.name:sha(p) for p in out.glob('*') if p.is_file()})
    final_identity=source_identity()
    if any(final_identity[key]!=identity[key] for key in ['commit','harness_sha256','sources','tools','site_config_sha256']):
        raise ValueError('source identity changed during acceptance')
    versions=json.loads(run([base,'-I','-c',"import json,sys;from importlib.metadata import distributions;print(json.dumps({'python':sys.version.split()[0],'packages':{d.metadata['Name']:d.version for d in distributions()}}))"]))
    result={'schema_version':1,'source_identity':identity,**inventory,'installed_origin':origin,'base_python':str(base),'native_python':str(native),'base_versions':versions,'runtime':isolation,'lock_sha256':sha(out/'tutorials/runtimes/uv.lock'),'native_receipt_sha256':sha(out/'native-corpus.json'),'gnd_receipt_sha256':sha(out/'gnd-corpus.json'),'agreement':report['agreement'],'artifacts':artifacts,'commands':commands,'scope':'Finite installed acceptance candidate; no release, certificate, merge or universal equivalence.'}
    from gnd.safefs import artifact_publish_leaf_atomic
    artifact_publish_leaf_atomic(out,'receipt.json',(json.dumps(result,indent=2)+'\n').encode())
    print('fresh wheel target-only application acceptance complete')


if __name__=='__main__':main()
