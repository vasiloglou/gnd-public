"""Developer-owned local PyRel report for the supplied synthetic snapshots."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


def report(snapshot: dict) -> dict:
    from relationalai.config import Config
    from relationalai.semantics import Field, Model, String, count, not_

    config = Config(connections={'local': {'type': 'duckdb', 'path': ':memory:'}},
                    default_connection='local',
                    deployment={'schema': 'release_governance', 'auto_deploy': True})
    model = Model('release_governance', config=config)

    def relation(name, fields, rows):
        rel = model.Relationship(fields=[Field(field, String) for field in fields], short_name=name)
        if rows:
            model.define(*[rel(*row) for row in rows])
        return rel

    request = relation('Request', ['release', 'service', 'requester'], snapshot['requests'])
    approval = relation('Approval', ['release', 'reviewer'], snapshot['approvals'])
    owner = relation('Owner', ['service', 'person'], snapshot['owners'])
    authorized = relation('Authorized', ['person'], [[p] for p in snapshot['authorized_reviewers']])
    release, service, requester, reviewer, service_owner, other = [String.ref() for _ in range(6)]

    def rows(query):
        return sorted([list(row) for row in query.to_df().itertuples(index=False, name=None)])

    joined = rows(model.where(request(release, service, requester),
                              approval(release, reviewer), owner(service, service_owner))
                  .select(release, service, requester, reviewer, service_owner))
    self_approval = rows(model.where(request(release, service, requester),
                                     approval(release, reviewer), requester == reviewer)
                         .select(release, reviewer))
    conflicts = rows(model.where(approval(release, reviewer), approval(release, other),
                                  reviewer != other).select(release))
    unauthorized = rows(model.where(approval(release, reviewer), not_(authorized(reviewer)))
                        .select(release, reviewer))
    workload = rows(model.where(approval(release, reviewer)).select(reviewer, count(release).per(reviewer)))
    return {'joined_approvals': joined, 'self_approval': self_approval,
            'conflicting_releases': conflicts, 'unauthorized': unauthorized,
            'reviewer_workload': [[p, int(n)] for p, n in workload]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    with args.snapshot.open('rb') as handle:
        raw = handle.read(65537)
    if len(raw) > 65536:
        parser.error('tutorial snapshot exceeds 64 KiB')
    snapshot = json.loads(raw)
    with tempfile.TemporaryDirectory(prefix='release-pyrel-') as directory:
        # Explicit local build state; no discovery of a remote connection/config.
        os.environ['RAI_BUILD_DIR'] = directory
        result = report(snapshot)
    with args.out.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
