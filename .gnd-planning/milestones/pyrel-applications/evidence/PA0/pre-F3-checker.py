import json

def canonical_rows(rows):
    return sorted(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in rows)

def check_acceptance(report: dict, process_exit: int, answer: dict, model: dict, model_sha: str, population_sha: str) -> list[str]:
    """Check the complete declared profile, never only a target row."""
    failures = []
    if not isinstance(report, dict):
        return ['report-not-object']
    for key, value in {'schema_version': 1, 'profile': 'applications-v1', 'backend': 'duckdb-local', **answer['expected_acceptance']}.items():
        if type(report.get(key)) is not type(value) or report.get(key) != value:
            failures.append('envelope:' + key)
    if process_exit != answer['expected_acceptance']['exit_code']:
        failures.append('process-exit')
    if report.get('binding') != {'model_sha256': model_sha, 'population_sha256': population_sha}:
        failures.append('binding')
    observed = {}
    modalities = {f"fact_types[{f['id']}].constraints[{i}]": c.get('modality', 'alethic') for f in model['fact_types'] for i, c in enumerate(f.get('constraints', []))}
    modalities.update({f'constraints[{i}]': c.get('modality', 'alethic') for i, c in enumerate(model.get('constraints', []))})
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
            if ref in observed:
                failures.append('duplicate:' + ref)
            observed[ref] = row.get('status')
            if field == 'verdicts' and row.get('modality') != modalities.get(ref):
                failures.append('modality:' + ref)
            if ref in guarded:
                witnesses = row.get('witnesses')
                if not isinstance(witnesses, list) or canonical_rows(witnesses) != canonical_rows(guarded[ref]):
                    failures.append('witnesses:' + ref)
            if ref in answer['expected_native_derivations']:
                for key in ['missing', 'extra']:
                    tuples = row.get(key)
                    expected = answer['expected_native_derivations'][ref][key]
                    if not isinstance(tuples, list) or canonical_rows(tuples) != canonical_rows(expected):
                        failures.append('derivation-' + key + ':' + ref)
    if observed != answer['expected_native_verdicts']:
        failures.append('complete-verdict-inventory')
    return failures
