"""BookRec's three rules, written by hand as plain PyRel queries.

These are equivalents of what GND's checker builds from ``model.orm.yaml``; they
are not the emitted program. Each rule becomes one ``where(...)`` whose rows are
the facts that break it: the antecedent atoms are matched, and the consequent is
negated. No row means the rule holds on these facts, provided its antecedent
fact lists are not empty; an empty antecedent is reported ``vacuous``, as GND
reports it, and exits 2. Only the three top-level rules are written here; the
uniqueness and mandatory constraints on ``book_has_genre`` are left to GND.

Run in the PyRel environment: ``"$GND_PYREL_PYTHON" rules_in_pyrel.py POPULATION``
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

LIMIT = 1 << 20  # one MiB of population JSON is plenty for a tutorial


def load_facts(path: Path) -> dict:
    with path.open('rb') as handle:
        raw = handle.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError(f'population larger than {LIMIT} bytes')
    document = json.loads(raw)
    facts = document['facts']
    loaded = {name: facts.get(name, []) for name in (
        'recommendation', 'user_rated_book', 'user_is_minor', 'book_rated_adult',
        'book_has_genre', 'user_prefers_genre')}
    for name, rows in loaded.items():
        if any(not isinstance(value, str) for row in rows for value in row.values()):
            raise TypeError(f'{name}: every value in this model is a string')
    return loaded


def check(facts: dict) -> list[tuple[str, str, dict]]:
    from relationalai.config import Config
    from relationalai.semantics import Field, Model, String, not_

    config = Config(connections={'local': {'type': 'duckdb', 'path': ':memory:'}},
                    default_connection='local',
                    deployment={'schema': 'bookrec_rules', 'auto_deploy': True})
    m = Model('bookrec_rules', config=config)

    def relation(name, fields):
        rel = m.Relationship(fields=[Field(f, String) for f in fields], short_name=name)
        rows = [[row[f] for f in fields] for row in facts[name]]
        if rows:
            m.define(*[rel(*row) for row in rows])
        return rel

    # One PyRel relationship per fact type, loaded from the population.
    recommendation = relation('recommendation', ['user', 'book'])
    user_rated_book = relation('user_rated_book', ['user', 'book'])
    user_is_minor = relation('user_is_minor', ['user'])
    book_rated_adult = relation('book_rated_adult', ['book'])
    book_has_genre = relation('book_has_genre', ['book', 'genre'])
    user_prefers_genre = relation('user_prefers_genre', ['user', 'genre'])
    u, b, g = String.ref(), String.ref(), String.ref()

    def rows(query):
        return sorted(list(row) for row in query.to_df().itertuples(index=False, name=None))

    findings = []

    # unread_only (must): "Never recommend a book the user has already rated."
    # Antecedent: recommendation(u, b). Consequent: no user_rated_book(u, b).
    # Breach: the recommended pair IS a rated pair.
    if not facts['recommendation']:
        findings.append(('unread_only', 'vacuous', None))
    else:
        for user, book in rows(m.where(recommendation(u, b), user_rated_book(u, b)).select(u, b)):
            findings.append(('unread_only', 'violated', {'$u': user, '$b': book}))

    # age_appropriate (must): "Never recommend an adult-rated book to a minor."
    # Antecedent: recommendation(u, b) and user_is_minor(u). Consequent: no book_rated_adult(b).
    # Breach: the book IS adult-rated.
    if not (facts['recommendation'] and facts['user_is_minor']):
        findings.append(('age_appropriate', 'vacuous', None))
    else:
        for user, book in rows(m.where(recommendation(u, b), user_is_minor(u),
                                       book_rated_adult(b)).select(u, b)):
            findings.append(('age_appropriate', 'violated', {'$u': user, '$b': book}))

    # preferred_genre (should): "A recommendation should match a preferred genre."
    # Antecedent: recommendation(u, b) and book_has_genre(b, g). Consequent: user_prefers_genre(u, g).
    # Breach: the user does NOT prefer that genre. A should-rule warns; it never blocks.
    if not (facts['recommendation'] and facts['book_has_genre']):
        findings.append(('preferred_genre', 'vacuous', None))
    else:
        for user, book, genre in rows(m.where(recommendation(u, b), book_has_genre(b, g),
                                              not_(user_prefers_genre(u, g))).select(u, b, g)):
            findings.append(('preferred_genre', 'warning', {'$u': user, '$b': book, '$g': genre}))
    return findings


RULES = ['unread_only', 'age_appropriate', 'preferred_genre']


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print('usage: rules_in_pyrel.py POPULATION.json', file=sys.stderr)
        return 2
    try:
        facts = load_facts(Path(argv[0]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'{argv[0]}: not a readable population ({type(error).__name__})', file=sys.stderr)
        return 3
    with tempfile.TemporaryDirectory(prefix='bookrec-rules-') as directory:
        os.environ['RAI_BUILD_DIR'] = directory  # explicit local build state, no remote discovery
        findings = check(facts)
    return report(findings, RULES)


def report(findings, rules) -> int:
    """One line per rule or per witness; exit 1 on a violation, 2 if any rule was vacuous."""
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
