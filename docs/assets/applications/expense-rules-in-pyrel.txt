"""The expense rules, written by hand as plain PyRel queries.

These are equivalents of what GND's checker builds from ``model.orm.json`` (and
``currency.orm.json`` when the facts carry currencies); they are not the emitted
program. Each rule is one ``where(...)`` whose rows are the facts that break it.
Four rule shapes appear here: a guarded comparison (caps and limits), a subset
(an approval needs a submission), a value list (known chains), and a mandatory
role (every expense states its currency). The uniqueness constraints and the
other mandatory roles inside the fact types are left to GND. A rule whose
antecedent fact lists are empty is reported ``vacuous``, as GND reports it, and
exits 2. The closed world of expenses is every id in any fact list plus the
population's ``instances`` roster, as in GND.

Run in the PyRel environment: ``"$GND_PYREL_PYTHON" rules_in_pyrel.py POPULATION``
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

LIMIT = 1 << 20
FACT_TYPES = ('expense_submitted_by_employee', 'expense_has_amount', 'expense_in_category',
              'expense_is_approved', 'expense_approved_by_chain', 'expense_has_currency')
CATEGORY_CAPS = {'meals': 75, 'training': 1500, 'travel': 2000, 'equipment': 3000}
CHAIN_LIMITS = {'team-lead': 100, 'finance': 3000}
KNOWN_CHAINS = ['team-lead', 'finance']
KNOWN_CATEGORIES = list(CATEGORY_CAPS)


def load(path: Path) -> tuple[dict, bool]:
    with path.open('rb') as handle:
        raw = handle.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError(f'population larger than {LIMIT} bytes')
    document = json.loads(raw)
    facts = {name: document['facts'].get(name, []) for name in FACT_TYPES}
    facts['_roster'] = [{'expense': i} for i in document.get('instances', {}).get('expense', [])]
    with_currency = 'expense_has_currency' in document.get('population', {}).get('covers', [])
    return facts, with_currency


def check(facts: dict, with_currency: bool) -> list[tuple[str, str, object]]:
    from relationalai.config import Config
    from relationalai.semantics import Field, Integer, Model, String, not_

    config = Config(connections={'local': {'type': 'duckdb', 'path': ':memory:'}},
                    default_connection='local',
                    deployment={'schema': 'expense_rules', 'auto_deploy': True})
    m = Model('expense_rules', config=config)

    def relation(name, fields):
        rel = m.Relationship(fields=[Field(f, t) for f, t in fields], short_name=name)
        rows = [[row[f] for f, _ in fields] for row in facts.get(name, [])]
        if rows:
            m.define(*[rel(*row) for row in rows])
        return rel

    submitted = relation('expense_submitted_by_employee', [('expense', Integer), ('employee', String)])
    amount = relation('expense_has_amount', [('expense', Integer), ('amount', Integer)])
    category = relation('expense_in_category', [('expense', Integer), ('category', String)])
    approved = relation('expense_is_approved', [('expense', Integer)])
    chain = relation('expense_approved_by_chain', [('expense', Integer), ('chain', String)])
    currency = relation('expense_has_currency', [('expense', Integer), ('currency', String)])
    # The closed world of expenses: every id in any fact list, plus the instances roster.
    ids = sorted({row['expense'] for rows_ in facts.values() for row in rows_})
    expense = m.Relationship(fields=[Field('expense', Integer)], short_name='expense')
    if ids:
        m.define(*[expense(i) for i in ids])
    e, a, c = Integer.ref(), Integer.ref(), String.ref()

    def rows(query):
        return sorted(list(row) for row in query.to_df().itertuples(index=False, name=None))

    findings = []
    # Guarded comparisons. Antecedent atoms are matched; the consequent "a <= cap" is
    # negated to "a > cap", so every row is an amount that breaks its cap.
    for name, cap in CATEGORY_CAPS.items():
        if not (facts['expense_in_category'] and facts['expense_has_amount']):
            findings.append((f'policy_{name}', 'vacuous', None))
            continue
        for exp, amt in rows(m.where(category(e, name), amount(e, a), a > cap).select(e, a)):
            findings.append((f'policy_{name}', 'violated', {'$e': int(exp), '$a': int(amt)}))
    for name, limit in CHAIN_LIMITS.items():
        rule = f'approval_limit_{name.replace("-", "_")}'
        if not (facts['expense_approved_by_chain'] and facts['expense_has_amount']):
            findings.append((rule, 'vacuous', None))
            continue
        for exp, amt in rows(m.where(chain(e, name), amount(e, a), a > limit).select(e, a)):
            findings.append((rule, 'violated', {'$e': int(exp), '$a': int(amt)}))
    if not facts['expense_has_amount']:
        findings.append(('positive_amount', 'vacuous', None))
    else:
        for exp, amt in rows(m.where(amount(e, a), a <= 0).select(e, a)):
            findings.append(('positive_amount', 'violated', {'$e': int(exp), '$a': int(amt)}))

    # Subset rules: every tuple on the left must also appear on the right.
    if facts['expense_is_approved']:
        for (exp,) in rows(m.where(approved(e), not_(submitted(e, String.ref()))).select(e)):
            findings.append(('approval_needs_submission', 'violated', [int(exp)]))
        for (exp,) in rows(m.where(approved(e), not_(chain(e, String.ref()))).select(e)):
            findings.append(('approval_needs_chain', 'violated', [int(exp)]))
    elif not facts['expense_submitted_by_employee'] or not facts['expense_approved_by_chain']:
        for rule in ('approval_needs_submission', 'approval_needs_chain'):
            findings.append((rule, 'vacuous', None))
    if facts['expense_approved_by_chain']:
        for (exp,) in rows(m.where(chain(e, c), not_(approved(e))).select(e)):
            findings.append(('chain_needs_approval', 'violated', [int(exp)]))
    elif not facts['expense_is_approved']:
        findings.append(('chain_needs_approval', 'vacuous', None))

    # Value rules: a value outside the declared list.
    if not facts['expense_in_category']:
        findings.append(('known_categories', 'vacuous', None))
    else:
        for (value,) in rows(m.where(category(e, c), *[c != v for v in KNOWN_CATEGORIES]).select(c)):
            findings.append(('known_categories', 'violated', value))
    if not facts['expense_approved_by_chain']:
        findings.append(('known_chains', 'vacuous', None))
    else:
        for (value,) in rows(m.where(chain(e, c), *[c != v for v in KNOWN_CHAINS]).select(c)):
            findings.append(('known_chains', 'violated', value))

    # Currency model only: a mandatory role and a value list.
    if with_currency:
        if not facts['expense_has_currency']:
            # GND treats an empty subject list as vacuous rather than as every expense missing.
            findings.append(('required_expense_has_currency', 'vacuous', None))
            findings.append(('supported_currency', 'vacuous', None))
        else:
            for (exp,) in rows(m.where(expense(e), not_(currency(e, String.ref()))).select(e)):
                findings.append(('required_expense_has_currency', 'violated', [int(exp)]))
            for (value,) in rows(m.where(currency(e, c), c != 'EUR').select(c)):
                findings.append(('supported_currency', 'violated', value))
    return findings


RULES = ['positive_amount', 'policy_meals', 'policy_training', 'policy_travel', 'policy_equipment',
         'approval_limit_team_lead', 'approval_limit_finance', 'approval_needs_submission',
         'approval_needs_chain', 'chain_needs_approval', 'known_categories', 'known_chains']
CURRENCY_RULES = ['required_expense_has_currency', 'supported_currency']


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print('usage: rules_in_pyrel.py POPULATION.json', file=sys.stderr)
        return 2
    try:
        facts, with_currency = load(Path(argv[0]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'{argv[0]}: not a readable population ({type(error).__name__})', file=sys.stderr)
        return 3
    with tempfile.TemporaryDirectory(prefix='expense-rules-') as directory:
        os.environ['RAI_BUILD_DIR'] = directory  # explicit local build state, no remote discovery
        findings = check(facts, with_currency)
    return report(findings, RULES + (CURRENCY_RULES if with_currency else []))


def report(findings, rules) -> int:
    """One line per rule or per distinct witness; exit 1 on a violation, 2 if any rule was vacuous."""
    violated = vacuous = False
    for rule in rules:
        hits = [(status, witness) for name, status, witness in findings if name == rule]
        if not hits:
            print(f'{rule}  OK')
        for status, witness in hits:
            if status == 'vacuous':
                vacuous = True
                print(f'{rule}  vacuous  (an antecedent fact list is empty, so the rule was not checked)')
                continue
            violated = violated or status == 'violated'
            print(f'{rule}  {status}  {json.dumps(witness, sort_keys=True)}')
    return 1 if violated else 2 if vacuous else 0


if __name__ == '__main__':
    raise SystemExit(main())
