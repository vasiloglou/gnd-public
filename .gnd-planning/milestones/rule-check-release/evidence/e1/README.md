# E1: what the 0.2.0 version bump moves (run 2026-11-07)

Experiment E1 of [the RR1 spec](../../notes/phase-RR1-spec.md), run as the spec
recorded it before running. The files here are the retained outputs; home-directory
paths in failure ids were replaced by `<scratch>` (edited, declared here).

- **Base ref.** main `12daa5b7`, untouched (`e1-base`).
- **Bumped ref.** `12daa5b7` plus exactly M1 to M3: `pyproject.toml`, the three
  plugin/marketplace manifests and a one-line edit of the `get-nick-done` entry
  of `uv.lock` (`e1-bumped`). `uv lock --check` passes on it.
- **Instrument.** A copy of the rule-check-adoption close script
  (`close-shards.sh`, six round-robin shards over the sorted `tests/test_*.py`,
  `uv sync --locked --group dev`, `uv run pytest -q --tb=line -p no:cacheprovider`)
  with the bundle path changed, on beast-3 (18 cores), the two runs one after the
  other. Default lane only.
- **Result.** Base: 17,819 passed, 0 failed, 2 errors (the known pre-existing
  `tests/test_public_optional.py` pair, [failed-base.txt](failed-base.txt)).
  Bumped: 17,772 passed, 47 failed, the same 2 errors
  ([failed-bumped.txt](failed-bumped.txt)). All 47 failures are new at the bump;
  none is in the base. Per-shard lines: [summary.txt](summary.txt).
- **Liveness.** The earlier scratch probe's 12 cases (plan O9) are among the 47.
- **Inventory.** [inventory-0.1.0-at-12daa5b7.txt](inventory-0.1.0-at-12daa5b7.txt):
  the 57 tracked files outside planning and `uv.lock` that name `0.1.0` at the base.
- **Not covered (stated first, as recorded).** The opt-in lanes (`evidence`,
  `census`, `distribution`, and the others the default `addopts` excludes), and
  anything that needs a network, a paid tool or a reserved split.
