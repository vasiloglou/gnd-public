"""BookRec's native query: which books can each reader be recommended?

Runs in the PyRel environment, not in GND's. The emitted program supplies
``run_app``; ``app.model`` is an ordinary PyRel model over the input facts.
"""
from __future__ import annotations

import runpy
import sys

from relationalai.semantics import String


def calculate(app, command, user, limit, preferred):
    if command == 'complete' and not {'book_is_eligible', 'book_is_blocked_for'} <= set(app.derivations):
        raise ValueError('complete requires the complete model')
    facts = app.source['facts']
    work = len(facts['user_prefers_genre']) * len(facts['book_has_genre'])
    for name in ('user_is_minor', 'book_rated_adult', 'user_rated_book'):
        work *= max(1, len(facts[name]))
    app.check_work(work, 'bookrec query')

    m = app.model
    u, b, g, preference = String.ref(), String.ref(), String.ref(), String.ref()
    reader = app.match('user_prefers_genre', user=u, genre=preference)   # u has registered preferences
    book = app.match('book_has_genre', book=b, genre=g)                  # b is in the catalogue

    if command == 'recommend' and [user] not in app.rows(m.where(reader).select(u)):
        raise ValueError('unknown preference-registered user')

    # A minor reader and an adult-rated book: never recommend this pair.
    blocked = m.where(reader, book, app.match('user_is_minor', user=u), app.match('book_rated_adult', book=b))
    blocked_pair = app.relationship('blocked', user=String, book=String)
    blocked.define(blocked_pair(u, b))
    already_read = m.where(reader, book, app.match('user_rated_book', user=u, book=b))

    if command == 'complete':
        eligible = m.where(app.match('book_is_eligible', user=u, book=b))
    else:
        clauses = [reader, book,
                   m.not_(app.match('user_rated_book', user=u, book=b)),   # not read yet
                   m.not_(blocked_pair(u, b))]                             # not blocked
        if preferred:
            clauses.append(app.match('user_prefers_genre', user=u, genre=g))  # preferred genre only
        eligible = m.where(*clauses)

    # Python only orders the rows and applies the user/limit selection.
    pairs = sorted({tuple(row) for row in app.rows(eligible.select(u, b))})
    selected = pairs if command == 'complete' else [pair for pair in pairs if pair[0] == user][:limit]

    def as_pairs(rows):
        return [{'user': x, 'book': y} for x, y in sorted(set(map(tuple, rows)))]

    candidate = app.candidate()
    kept = [] if command == 'complete' else [r for r in candidate['facts']['recommendation'] if r['user'] != user]
    candidate['facts']['recommendation'] = kept + as_pairs(selected)
    app.propose(candidate, {'eligible_pairs': as_pairs(pairs), 'selected_pairs': as_pairs(selected),
                            'blocked_pairs': as_pairs(app.rows(blocked.select(u, b))),
                            'already_read_pairs': as_pairs(app.rows(already_read.select(u, b)))})


def main():
    runtime, seed, output, command, user, limit, preferred = sys.argv[1:]
    if command == 'recommend' and not 1 <= int(limit) <= 100:
        print('limit must be between 1 and 100', file=sys.stderr)
        return 2
    run_app = runpy.run_path(runtime)['run_app']
    return run_app(calculate, [seed, output, command, user, int(limit), preferred == 'true'])


if __name__ == '__main__':
    raise SystemExit(main())
