# Census of recorded model digests (plan r2, review P9)

Read-only. `census.py` loads every tracked `*.orm.yaml|json|yml`, computes
the legacy digest (`gnd.values.model_digest`), and counts the tracked files
whose text contains any of those digests.

Run at main `12daa5b7` (2026-11-07), from the repository root with the
repository's own Python environment and `PYTHONPATH=src`:

    python census.py recorded-files.json

Result: 371 model files, 306 load (65 do not load; not examined),
273 distinct digests, 58 of them recorded in tracked files, 167 files
recording at least one (`recorded-files.txt`: 140 under `tests/fixtures`,
15 under `src/gnd/examples/approvals`, 12 under `.gnd-planning`).

Limits: an undercount (models built inside tests and reference-population
digests are not seen); the 65 unloadable models are not digested. 
`canonical-form.py` computes the proposed canonical form (the existing
`values.canonical` walk and `artifacts.canonical_json_bytes`, same exclusions
as the legacy digest, no envelope) over the 306: 0 refusals, 273 distinct
values, one-to-one with the legacy digest. It measures the feasibility of the
walk only; it is not the version-2 definition (no `identity_version`
envelope).
