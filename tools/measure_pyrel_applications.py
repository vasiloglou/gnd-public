"""Execute the frozen application corpus through public standalone PyRel exports."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'tests/fixtures/pyrel_applications'


def read_bounded(path: Path, limit: int = 1048576) -> bytes:
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError(f'input exceeds {limit}-byte cap')
    return raw


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def approved_corpus() -> tuple[bytes, bytes]:
    matrix = read_bounded(CORPUS / 'matrix.json')
    answers = read_bounded(CORPUS / 'answers.json')
    approved = json.loads(read_bounded(CORPUS / 'approval.json'))
    if approved.get('matrix_sha256') != sha(matrix) or approved.get('answers_sha256') != sha(answers):
        raise ValueError('corpus differs from the explicitly approved snapshot')
    return matrix, answers


def read_native_report(path: Path) -> tuple[object, list[str]]:
    try:
        return json.loads(read_bounded(path, 4 * 1024 * 1024)), []
    except (OSError, ValueError, UnicodeError) as error:
        return {}, ['report-read:' + type(error).__name__]


def canonical_rows(rows: list) -> list[str]:
    return sorted(json.dumps(row, sort_keys=True, separators=(',', ':')) for row in rows)


def check_acceptance(report: dict, process_exit: int, answer: dict, model: dict,
                     model_sha: str, population_sha: str) -> list[str]:
    """Check the complete declared profile, never only a target row."""
    failures = []
    if not isinstance(report, dict):
        return ['report-not-object']
    for key, value in {'schema_version': 1, 'profile': 'applications-v1',
                       'backend': 'duckdb-local', **answer['expected_acceptance']}.items():
        if type(report.get(key)) is not type(value) or report.get(key) != value:
            failures.append('envelope:' + key)
    if process_exit != answer['expected_acceptance']['exit_code']:
        failures.append('process-exit')
    if report.get('binding') != {'model_sha256': model_sha, 'population_sha256': population_sha}:
        failures.append('binding')
    observed = {}
    modalities = {f"fact_types[{f['id']}].constraints[{i}]": c.get('modality', 'alethic')
                  for f in model['fact_types'] for i, c in enumerate(f.get('constraints', []))}
    modalities.update({f'constraints[{i}]': c.get('modality', 'alethic')
                       for i, c in enumerate(model.get('constraints', []))})
    metadata = {f"fact_types[{f['id']}].constraints[{i}]": c
                for f in model['fact_types'] for i, c in enumerate(f.get('constraints', []))}
    metadata.update({f'constraints[{i}]': c for i, c in enumerate(model.get('constraints', []))})
    guarded = answer['expected_native_guarded_witnesses']
    for field, refkey in [('verdicts', 'constraint_ref'), ('derivations', 'derivation_ref')]:
        rows = report.get(field)
        if not isinstance(rows, list):
            failures.append('missing:' + field)
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get(refkey), str):
                failures.append('malformed-row')
                continue
            ref = row[refkey]
            if (ref.startswith('derivation:')) != (field == 'derivations'):
                failures.append('row-placement:' + ref)
            if ref in observed:
                failures.append('duplicate:' + ref)
            observed[ref] = row.get('status')
            if field == 'verdicts' and row.get('modality') != modalities.get(ref):
                failures.append('modality:' + ref)
            if field == 'verdicts':
                constraint = metadata.get(ref, {})
                if row.get('id') != constraint.get('id', ref) or row.get('constraint_type') != constraint.get('type'):
                    failures.append('identity:' + ref)
                if not isinstance(row.get('witnesses'), list):
                    failures.append('witness-format:' + ref)
                if 'reason' not in row or (row['reason'] is not None and not isinstance(row['reason'], str)):
                    failures.append('reason-format:' + ref)
            if ref in guarded:
                witnesses = row.get('witnesses')
                if not isinstance(witnesses, list) or canonical_rows(witnesses) != canonical_rows(guarded[ref]):
                    failures.append('witnesses:' + ref)
            if ref in answer['expected_native_derivations']:
                if row.get('fact_type') != ref.split(':', 1)[1] or row.get('reason', 'missing') is not None:
                    failures.append('derivation-identity:' + ref)
                computed = row.get('computed')
                expected_computed = answer.get('expected_native_computed', {}).get(ref)
                if expected_computed is None:
                    failures.append('derivation-computed-key:' + ref)
                elif (not isinstance(computed, list)
                      or canonical_rows(computed) != canonical_rows(expected_computed)):
                    failures.append('derivation-computed:' + ref)
                for key in ['missing', 'extra']:
                    tuples = row.get(key)
                    expected = answer['expected_native_derivations'][ref][key]
                    if not isinstance(tuples, list) or canonical_rows(tuples) != canonical_rows(expected):
                        failures.append('derivation-' + key + ':' + ref)
    if observed != answer['expected_native_verdicts']:
        failures.append('complete-verdict-inventory')
    return failures


def agreement(records: list[dict], answers: dict, approved: dict) -> dict:
    """Finite row agreement; no unlisted mismatch can shrink the denominator."""
    names = [record['case'] for record in records]
    if len(set(names)) != len(names) or set(names) != set(answers):
        raise ValueError('agreement case inventory differs')
    required = {name: answer['intentional_disagreements'] for name, answer in answers.items()
                if answer['intentional_disagreements']}
    selected = {name: exclusions for name, exclusions in approved.items() if name in answers}
    if selected != required:
        raise ValueError('agreement exclusion inventory differs')
    normalization = {'pass': 'satisfied', 'fail': 'violated', 'warning': 'warning'}
    total = compared = matches = 0
    disagreements = []
    for record in records:
        name, report = record['case'], record['report']
        answer = answers[name]
        if record['process_exit'] != answer['observed_gnd_exit']:
            raise ValueError('business exits differ in the selected finite corpus')
        observed = {}
        for field, key in [('verdicts', 'constraint_ref'), ('derivations', 'derivation_ref')]:
            for row in report[field]:
                ref = row[key]
                if ref in observed:
                    raise ValueError('duplicate agreement row')
                observed[ref] = row['status']
        if set(observed) != set(answer['observed_gnd_verdicts']):
            raise ValueError('agreement row inventory differs')
        for ref, native in observed.items():
            total += 1
            gnd = answer['observed_gnd_verdicts'][ref]
            if gnd not in normalization:
                raise ValueError('unmapped GND agreement status')
            if ref in required.get(name, {}):
                if normalization[gnd] == native:
                    raise ValueError('listed disagreement is no longer a disagreement')
                if record['process_exit'] != 1 or answer['observed_gnd_exit'] != 1:
                    raise ValueError('listed disagreement did not reject in both engines')
                disagreements.append({'case': name, 'constraint_ref': ref, 'gnd': gnd,
                                       'native': native, 'reason': required[name][ref],
                                       'population_sha256': record['population_sha256']})
            else:
                compared += 1
                if normalization[gnd] != native:
                    raise ValueError('unlisted disagreement:' + name + ':' + ref)
                matches += 1
    return {'normalization': normalization, 'native_obligation_rows': total,
            'comparable_rows': total - len(disagreements), 'compared_rows': compared,
            'matches': matches, 'intentional_disagreements': disagreements,
            'business_rejections_agree': True,
            'boundary': 'Only the selected frozen rows and listed exclusions; not universal ORM agreement.'}


def measure(mode: str, python: Path, stage: str = 'all') -> dict:
    runtime_source = ROOT / 'src/gnd/export/pyrel_runtime.py'
    runtime_raw = read_bounded(runtime_source)
    tool_raw = read_bounded(Path(__file__))
    matrix_raw, answer_raw = approved_corpus()
    matrix, answers = json.loads(matrix_raw), json.loads(answer_raw)
    if mode == 'baseline':
        names = [next(n for n, c in matrix['cases'].items()
                      if c['model'] == 'src/gnd/examples/' + m) for m in matrix['models']]
        names += [n for n in matrix['cases'] if n.endswith('-extra')]
        if stage == 'additions':
            names = [n for n in matrix['cases'] if n.endswith('-distinct') or n == 'm2-eligible-joint-omission']
    else:
        names = [n for n, c in matrix['cases'].items()
                 if stage != 'guarded' or not c['model'].endswith('complete.orm.yaml')]
    records = []
    with tempfile.TemporaryDirectory(prefix='pa-native-') as directory:
        scratch = Path(directory)
        env = {k: v for k, v in os.environ.items() if k in {'PATH', 'HOME', 'TMPDIR', 'SYSTEMROOT'}}
        env['RAI_BUILD_DIR'], env['PYTHONUTF8'] = str(scratch / 'build'), '1'
        versions = subprocess.run(
            [str(python), '-c', ("from importlib.metadata import version; import json,sys; "
             "print(json.dumps({'python':sys.version.split()[0],"
             "'relationalai':version('relationalai'),'duckdb':version('duckdb')}))")],
            cwd=scratch, env=env, capture_output=True, text=True, timeout=30, check=True)
        runtime = json.loads(versions.stdout)
        if runtime.get('relationalai') != '1.30.1' or runtime.get('duckdb') != '1.5.5':
            raise ValueError('incorrect native runtime versions')
        programs = {}
        for name in names:
            case, answer = matrix['cases'][name], answers[name]
            model, population = ROOT / case['model'], ROOT / case['population']
            model_raw, population_raw = read_bounded(model), read_bounded(population)
            model_sha, population_sha = sha(model_raw), sha(population_raw)
            if case['model'] not in programs:
                program = scratch / f'audit-{len(programs)}.py'
                subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', case['model'],
                                '--out', str(program)], cwd=ROOT, env=env, capture_output=True,
                               text=True, timeout=30, check=True)
                programs[case['model']] = program
            program = programs[case['model']]
            output = scratch / f'{name}.json'
            argv = [str(python), str(program), str(population), '--out', str(output)]
            if mode != 'baseline':
                argv.append('--accept')
            result = subprocess.run(argv, cwd=scratch, env=env, capture_output=True,
                                    text=True, timeout=60, check=False)
            report, diagnostics = read_native_report(output)
            if isinstance(report, dict):
                report.pop('model', None)
                report.pop('population', None)
            stable = read_bounded(model) == model_raw and read_bounded(population) == population_raw
            if mode == 'baseline':
                failures = [] if result.returncode == 0 and isinstance(report, dict) and isinstance(report.get('verdicts'), list) else ['audit-not-complete']
                if isinstance(report, dict) and any(v.get('status') == 'error' for v in report.get('verdicts', [])):
                    failures.append('audit-error')
            else:
                expected_computed = {}
                population_doc = json.loads(population_raw)
                for ref, delta in answer['expected_native_derivations'].items():
                    head = ref.split(':', 1)[1]
                    values = {json.dumps(value, sort_keys=True): value
                              for value in population_doc['facts'][head] + delta['missing']}
                    for value in delta['extra']:
                        values.pop(json.dumps(value, sort_keys=True), None)
                    expected_computed[ref] = [values[key] for key in sorted(values)]
                comparison = {**answer, 'expected_native_computed': expected_computed}
                failures = check_acceptance(report, result.returncode, comparison,
                                            json.loads(model_raw), model_sha, population_sha)
            failures.extend(diagnostics)
            if not stable:
                failures.append('input-changed-during-run')
            records.append({'case': name, 'target': case['target'], 'matches': not failures,
                            'mismatches': failures, 'process_exit': result.returncode, 'report': report,
                            'model_sha256': model_sha, 'population_sha256': population_sha,
                            'program_sha256': sha(read_bounded(program, 4 * 1024 * 1024)),
                            'gnd_observed_exit': answer['observed_gnd_exit'],
                            'intentional_disagreements': answer['intentional_disagreements']})
            print(f'{name}: exit={result.returncode} matches={not failures}', flush=True)
    if read_bounded(runtime_source) != runtime_raw or read_bounded(Path(__file__)) != tool_raw:
        raise ValueError('runtime or measurement tool changed during execution')
    compared = None
    if mode == 'acceptance' and all(record['matches'] for record in records):
        approved = json.loads(read_bounded(CORPUS / 'approval.json'))['intentional_disagreements']
        compared = agreement(records, {name: answers[name] for name in names}, approved)
    return {'schema_version': 2, 'mode': mode, 'stage': stage, 'runtime': runtime,
            'agreement': compared,
            'runtime_source_sha256': sha(runtime_raw), 'measurement_tool_sha256': sha(tool_raw),
            'matrix_sha256': sha(matrix_raw), 'answers_sha256': sha(answer_raw),
            'lock_sha256': sha(read_bounded(ROOT / 'tutorials/runtimes/uv.lock')),
            'cases': records, 'matched': sum(r['matches'] for r in records), 'denominator': len(records)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('baseline', 'successor', 'acceptance'), required=True)
    parser.add_argument('--stage', choices=('all', 'guarded', 'additions'), default='all')
    parser.add_argument('--python', type=Path, default=ROOT / 'tutorials/runtimes/.venv/bin/python')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.out.is_symlink():
        parser.error('output already exists; select a fresh receipt path')
    result = measure(args.mode, args.python.absolute(), args.stage)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write('\n')
    if args.mode == 'baseline' and not any(
        v.get('status') == 'unsupported' for c in result['cases']
        for v in (c['report'].get('verdicts', []) if isinstance(c['report'], dict) else [])
    ):
        raise ValueError('baseline omission no longer present')
    return 0 if result['matched'] == result['denominator'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
