"""Owned BookRec native calculation; executable without any GND imports."""
from __future__ import annotations

import copy
import hashlib
import json
import runpy
import sys
from importlib.metadata import version
from pathlib import Path


def calculate(runtime_path, seed_path, output_path, command, user, limit, preferred):
    runtime = runpy.run_path(str(runtime_path))
    parse = runtime['_parse_document']
    model = parse(runtime['MODEL_TEXT'])
    index = runtime['admit_model'](model)
    raw = seed_path.read_bytes()
    if len(raw) > runtime['PROFILE_BYTES']:
        raise runtime['ProfileRefusal']('native input byte limit')
    seed = parse(raw.decode('utf-8'))
    runtime['admit_population'](seed, index)
    ordered = runtime['_profile_derivations'](index)
    if command == 'complete' and not {'book_is_eligible', 'book_is_blocked_for'} <= set(ordered):
        raise ValueError('complete requires the complete model')
    working = copy.deepcopy(seed)
    # These are computed claims generated for the new candidate. Asserted
    # coverage is never filled in by the application.
    for name in ordered:
        working['facts'].setdefault(name, [])
        if name not in working['population']['covers']:
            working['population']['covers'].append(name)
    runtime['_profile_admit'](index, working)
    work = len(working['facts']['user_prefers_genre']) * len(working['facts']['book_has_genre'])
    work *= max(1, len(working['facts']['user_is_minor']))
    work *= max(1, len(working['facts']['book_rated_adult']))
    work *= max(1, len(working['facts']['user_rated_book']))
    if work > runtime['PROFILE_WORK']:
        raise runtime['ProfileRefusal']('bookrec query work limit')
    if version('relationalai') != '1.30.1' or version('duckdb') != '1.5.5':
        raise RuntimeError('requires PyRel 1.30.1/DuckDB 1.5.5')
    oracle = runtime['ApplicationOracle'](index, working, config=runtime['local_config']())
    string = oracle._concept_for('String')
    u, b, g, preference = [string.ref() for _ in range(4)]
    atom = oracle.pattern
    def rows(query):
        values = oracle._rows(query)
        if len(values) > runtime['PROFILE_RESULTS']:
            raise runtime['ProfileRefusal']('bookrec query result limit')
        return values
    registered = atom('user_prefers_genre', {'user': u, 'genre': preference})
    catalogue = atom('book_has_genre', {'book': b, 'genre': g})
    users = rows(oracle.m.where(registered).select(u))
    if command == 'recommend' and [user] not in users:
        raise ValueError('unknown preference-registered user')
    blocked_query = oracle.m.where(registered, catalogue,
                                   atom('user_is_minor', {'user': u}),
                                   atom('book_rated_adult', {'book': b}))
    blocked = rows(blocked_query.select(u, b))
    read = rows(oracle.m.where(registered, catalogue,
                                      atom('user_rated_book', {'user': u, 'book': b})).select(u, b))
    # Use a native relationship for the conjunction under negation. No Python
    # age/rating/genre predicate participates in selection.
    from relationalai.semantics.frontend.base import Field
    blocked_relation = oracle.m.Relationship(fields=[Field('user', string), Field('book', string)],
                                             short_name='bookrec_blocked')
    blocked_query.define(blocked_relation(u, b))
    if command == 'complete':
        fragment = oracle.m.where(atom('book_is_eligible', {'user': u, 'book': b}))
    else:
        clauses = [registered, catalogue,
                   oracle.m.not_(atom('user_rated_book', {'user': u, 'book': b})),
                   oracle.m.not_(blocked_relation(u, b))]
        if preferred:
            clauses.append(atom('user_prefers_genre', {'user': u, 'genre': g}))
        fragment = oracle.m.where(*clauses)
    eligible = sorted({tuple(row) for row in rows(fragment.select(u, b))})
    if len(eligible) > runtime['PROFILE_RESULTS']:
        raise runtime['ProfileRefusal']('native query result limit')
    # SDK ordering/limit are unavailable in this pinned local frontend. Only
    # deterministic presentation and the user/limit selection happen here.
    selected = eligible if command == 'complete' else [pair for pair in eligible if pair[0] == user][:limit]
    pairs = lambda rows: [{'user': x, 'book': y} for x, y in sorted(set(map(tuple, rows)))]
    candidate = working
    prior = [] if command == 'complete' else [row for row in candidate['facts']['recommendation'] if row['user'] != user]
    candidate['facts']['recommendation'] = prior + pairs(selected)
    for name in ordered:
        candidate['facts'][name] = oracle.computed[name]
    envelope = {'schema_version': 1,
                'binding': {'model_sha256': hashlib.sha256(runtime['MODEL_TEXT'].encode()).hexdigest(),
                            'input_sha256': hashlib.sha256(raw).hexdigest()},
                'candidate': candidate,
                'calculation': {'eligible_pairs': pairs(eligible), 'selected_pairs': pairs(selected),
                                'blocked_pairs': pairs(blocked), 'already_read_pairs': pairs(read)}}
    output_path.write_text(json.dumps(envelope, sort_keys=True, indent=2) + '\n')


def main():
    runtime, seed, output, command, user, limit, preferred = sys.argv[1:]
    if command == 'recommend' and not 1 <= int(limit) <= 100:
        print('limit must be between 1 and 100', file=sys.stderr)
        return 2
    try:
        calculate(Path(runtime), Path(seed), Path(output), command, user, int(limit), preferred == 'true')
        return 0
    except ValueError as error:
        print(str(error)[:300], file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- native application refusal boundary
        print(f'{type(error).__name__}: {error}'[:300], file=sys.stderr)
        # Profile refusal is a bounded unsupported input, not a runtime failure.
        return 2 if type(error).__name__ == 'ProfileRefusal' else 70


if __name__ == '__main__':
    raise SystemExit(main())
