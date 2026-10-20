"""Serial balanced IE6 comparison; separate interpreter per arm, no profiling."""
import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path


def identity(root):
    paths = sorted((root / 'src/gnd').rglob('*.py')) + [root / 'tools/measure_incremental_evaluation.py']
    fixtures = sorted((root / 'tests/fixtures').rglob('*'))
    paths += [p for p in fixtures if p.is_file() and '__pycache__' not in p.parts]
    paths += [root/'pyproject.toml', root/'uv.lock']
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if '__pycache__' not in p.parts}


def worker(root, workload, session):
    os.chdir(root)
    sys.path[:0] = [str(root / 'tools'), str(root / 'src')]
    import tracemalloc

    import measure_incremental_evaluation as tool

    from gnd import api
    assert Path(api.__file__).resolve().is_relative_to(root/'src')
    assert sys.getprofile() is None and not tracemalloc.is_tracing()
    expected = {'reporter': [2]*13, 'course': [1,1,0], 'localized': [1]*6}[workload]
    warm = tool.replay_full(workload, receipts=True, incremental=session)
    assert [r['exit_code'] for r in warm] == expected
    start = time.perf_counter()
    result = tool.replay_full(workload, receipts=True, incremental=session)
    elapsed = time.perf_counter()-start
    exits = [r['exit_code'] for r in result]
    assert exits == expected
    return {'exits': exits, 'elapsed_s': elapsed, 'api_path': str(Path(api.__file__).resolve()),
            'workload': workload, 'session': session}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--worker', choices=['reporter','course','localized'])
    p.add_argument('--session', action='store_true')
    args=p.parse_args()
    baseline,candidate=args.baseline.resolve(),args.candidate.resolve()
    if args.worker:
        print(json.dumps(worker(candidate,args.worker,args.session)))
        return
    before={name:identity(root) for name,root in [('baseline',baseline),('candidate',candidate)]}
    # A/baseline-session, B/candidate-session, C/candidate-full-receipts.
    config={'A':(baseline,True),'B':(candidate,True),'C':(candidate,False)}
    results={}
    for workload in ('reporter','course','localized'):
        samples={arm:[] for arm in config}
        observations=[]
        for order in ('ABC','BCA','CAB'):
            for arm in order:
                root,session=config[arm]
                command=[sys.executable,str(Path(__file__).resolve()),'--baseline',str(baseline),
                         '--candidate',str(root),'--out',str(args.out),'--worker',workload]
                if session:
                    command.append('--session')
                env=dict(os.environ)
                env.pop('PYTHONPATH',None)
                run=subprocess.run(command,env=env,check=True,capture_output=True,text=True)
                row=json.loads(run.stdout)
                samples[arm].append(row['elapsed_s'])
                observations.append({'arm':arm,**row})
        results[workload]={'samples_s':samples,'medians_s':{k:statistics.median(v) for k,v in samples.items()},
                           'ranges_s':{k:max(v)-min(v) for k,v in samples.items()},'observations':observations}
        print(workload,results[workload]['medians_s'],flush=True)
    assert before == {name:identity(root) for name,root in [('baseline',baseline),('candidate',candidate)]}
    data={'arms':{'A':'d0ffd9a session+receipts','B':'IE6 session+receipts','C':'IE6 full+receipts'},
          'order':['ABC','BCA','CAB'],'environment':{'python':sys.version,'executable':sys.executable,
          'platform':sys.platform},'identities':before,'workloads':results,
          'boundary':'Shared host; serial workers each warm once then time complete replay, import/startup excluded; no profiler or counters; timings informational. Correctness is a separately executed current-byte integrated oracle.'}
    args.out.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    main()
