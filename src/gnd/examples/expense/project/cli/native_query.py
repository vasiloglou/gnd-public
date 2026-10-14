"""Expense's native query: report counts and totals, and stage an approval.

Runs in the PyRel environment, not in GND's. The emitted program supplies
``run_app``; ``app.model`` is an ordinary PyRel model over the input facts.
No query here enforces approval limits or category caps: those rules live in
the model, and GND's policy check enforces them on the staged candidate.
"""
from __future__ import annotations

import runpy
import sys

from relationalai.semantics.std import aggregates


def calculate(app, command, expense, chain):
    has_currency = app.has('expense_has_currency')
    facts = app.source['facts']
    work = len(facts['expense_submitted_by_employee']) * max(1, len(facts['expense_has_amount']))
    if has_currency:
        work *= max(1, len(facts['expense_has_currency']))
    app.check_work(work, 'expense query')

    m = app.model
    e = app.ref('expense_submitted_by_employee', 'expense')
    a = app.ref('expense_has_amount', 'amount')
    submitted = app.rows(m.where(app.match('expense_submitted_by_employee', expense=e)).select(e))
    approved = app.rows(m.where(app.match('expense_is_approved', expense=e)).select(e))
    if has_currency:
        c = app.ref('expense_has_currency', 'currency')
        if app.rows(m.where(app.match('expense_has_currency', currency=c), c != 'EUR').select(c)):
            return app.refuse('unsupported-currency', 'only explicit EUR is supported; no currency conversion')
    if command == 'approve':
        expense = int(expense)
        if [expense] not in submitted:
            return app.refuse('unknown-expense', 'unknown expense: no submission fact')
        if [expense] in approved:
            return app.refuse('already-approved', 'already approved')

    # Count and sum submitted expenses natively.
    claims = m.where(app.match('expense_submitted_by_employee', expense=e),
                     app.match('expense_has_amount', expense=e, amount=a))
    totals = app.rows(claims.select(aggregates.count(m.distinct(e)), aggregates.sum(e, a)))
    approvals = app.rows(m.where(app.match('expense_is_approved', expense=e)).select(aggregates.count(m.distinct(e))))
    # An empty native aggregate returns no row; present its zero explicitly.
    report = {'submitted': totals[0][0] if totals else 0,
              'approved': approvals[0][0] if approvals else 0}
    if has_currency:
        grouped = app.rows(claims.where(app.match('expense_has_currency', expense=e, currency=c))
                           .select(c, aggregates.sum(e, a).per(c)))
        report['totals_by_currency'] = {currency: amount for currency, amount in grouped}
    else:
        report['total_eur'] = totals[0][1] if totals else 0

    candidate = app.candidate()
    if command == 'approve':
        # The proposed approval is recorded as given; the policy check decides if it is allowed.
        candidate['facts']['expense_is_approved'].append({'expense': expense})
        candidate['facts']['expense_approved_by_chain'].append({'expense': expense, 'chain': chain})
    app.propose(candidate, {'report': report, 'unit': 'EUR',
                            'currency_mode': 'explicit' if has_currency else 'implicit',
                            'submitted_expenses': submitted, 'approved_expenses': approved})


def main():
    runtime, seed, output, *args = sys.argv[1:]
    return runpy.run_path(runtime)['run_app'](calculate, [seed, output, *args])


if __name__ == '__main__':
    raise SystemExit(main())
