"""Owned native expense arithmetic and candidate wiring; no GND imports."""
from __future__ import annotations

import copy
import hashlib
import json
import runpy
import sys
from importlib.metadata import version
from pathlib import Path


def calculate(runtime_path, seed_path, output_path, command, expense, chain):
    runtime = runpy.run_path(str(runtime_path))
    raw = seed_path.read_bytes()
    if len(raw) > runtime['PROFILE_BYTES']:
        raise runtime['ProfileRefusal']('native input byte limit')
    source = runtime['_parse_document'](raw.decode('utf-8'))
    index = runtime['admit_model'](runtime['_parse_document'](runtime['MODEL_TEXT']))
    runtime['admit_population'](source, index)
    runtime['_profile_admit'](index, source)
    has_currency = 'expense_has_currency' in index.fact_types
    facts = source['facts']
    work = len(facts['expense_submitted_by_employee']) * max(1, len(facts['expense_has_amount']))
    if has_currency:
        work *= max(1, len(facts['expense_has_currency']))
    if work > runtime['PROFILE_WORK']:
        raise runtime['ProfileRefusal']('expense query work limit')
    if version('relationalai') != '1.30.1' or version('duckdb') != '1.5.5':
        raise RuntimeError('requires PyRel 1.30.1/DuckDB 1.5.5')
    oracle = runtime['ApplicationOracle'](index, source, config=runtime['local_config']())
    from relationalai.semantics.std import aggregates

    e = oracle.refs('expense_submitted_by_employee')['expense']
    a = oracle.refs('expense_has_amount')['amount']
    atom = oracle.pattern
    def rows(fragment):
        result = oracle._rows(fragment)
        if len(result) > runtime['PROFILE_RESULTS']:
            raise runtime['ProfileRefusal']('expense query result limit')
        return result
    binding = {'model_sha256': hashlib.sha256(runtime['MODEL_TEXT'].encode()).hexdigest(),
               'input_sha256': hashlib.sha256(raw).hexdigest()}
    def refuse(kind, reason):
        output_path.write_text(json.dumps({'schema_version': 1, 'binding': binding,
                                          'guard_refusal': {'exit_code': 1, 'kind': kind, 'reason': reason}}))
    submitted = rows(oracle.m.where(atom('expense_submitted_by_employee', {'expense': e})).select(e))
    approved = rows(oracle.m.where(atom('expense_is_approved', {'expense': e})).select(e))
    if has_currency:
        c = oracle.refs('expense_has_currency')['currency']
        unsupported = rows(oracle.m.where(atom('expense_has_currency', {'currency': c}), c != 'EUR').select(c))
        if unsupported:
            refuse('unsupported-currency', 'only explicit EUR is supported; no currency conversion')
            return
    if command == 'approve':
        expense = int(expense)
        if [expense] not in submitted:
            refuse('unknown-expense', 'unknown expense: no submission fact')
            return
        if [expense] in approved:
            refuse('already-approved', 'already approved')
            return
    query = oracle.m.where(atom('expense_submitted_by_employee', {'expense': e}),
                           atom('expense_has_amount', {'expense': e, 'amount': a}))
    totals = rows(query.select(aggregates.count(oracle.m.distinct(e)), aggregates.sum(e, a)))
    approval_count = rows(oracle.m.where(atom('expense_is_approved', {'expense': e}))
                          .select(aggregates.count(oracle.m.distinct(e))))
    # A native empty aggregate produces no scalar row. Only its mathematical
    # zero identity is presented here; populated arithmetic stays native.
    report = {'submitted': totals[0][0] if totals else 0,
              'approved': approval_count[0][0] if approval_count else 0}
    if has_currency:
        grouped = rows(query.where(atom('expense_has_currency', {'expense': e, 'currency': c}))
                       .select(c, aggregates.sum(e, a).per(c)))
        report['totals_by_currency'] = {currency: amount for currency, amount in grouped}
    else:
        report['total_eur'] = totals[0][1] if totals else 0
    candidate = copy.deepcopy(source)
    if command == 'approve':
        candidate['facts']['expense_is_approved'].append({'expense': expense})
        candidate['facts']['expense_approved_by_chain'].append({'expense': expense, 'chain': chain})
    output_path.write_text(json.dumps({'schema_version': 1, 'binding': binding, 'candidate': candidate,
                                      'calculation': {'report': report, 'unit': 'EUR',
                                                      'currency_mode': 'explicit' if has_currency else 'implicit',
                                                      'submitted_expenses': submitted, 'approved_expenses': approved}},
                                     sort_keys=True, indent=2) + '\n')


def main():
    runtime, seed, output, command, expense, chain = sys.argv[1:]
    try:
        calculate(Path(runtime), Path(seed), Path(output), command, expense, chain)
        return 0
    except ValueError as error:
        print(str(error)[:300], file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- bounded native application refusal
        print(f'{type(error).__name__}: {error}'[:300], file=sys.stderr)
        return 2 if type(error).__name__ == 'ProfileRefusal' else 70


if __name__ == '__main__':
    raise SystemExit(main())
