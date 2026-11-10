# MC3 independent Codex CLI review

Scope: base5a083f469d0a14271c3417401c6ae2fd046a165a to candidatec93506e28d4ba98a96c85223fbad630cf250b550. One reviewer is one reviewer. Header added; the final review below is retained verbatim. The reviewer itself normalized paths to repository-relative form. No operator home appears in this retained body.

1. **Blocking — discover can overwrite its included vocabulary.** At `src/gnd/discover/service.py:214`, MC3 enables include-bearing input, but CLI output admission excludes only explicit MODEL/POPULATION inputs. Trigger: run discover on the committed project/clean population with `--report vocabulary-v1.orm.json`. With `gnd.discover.output.write` mocked, the CLI returned **0** and selected the vocabulary for a **2,701-byte report write** (`service.py:604`). The real writer uses `Path.write_bytes`, so it would truncate the pinned vocabulary and invalidate subsequent loads. This violates plan §0.4 and MC3’s input-only dependency contract. Check report destinations and inode aliases against verified includes before any output.

2. **Hardening — the model CAS destination escapes dependency exclusion.** At `src/gnd/evolve/service.py:1752`, `outputs` contains verbalization and staging leaves but omits `self._model_path`. Trigger: authenticate an overwritten historical vocabulary whose declared path equals the includer’s path, then re-pin to v2. An in-memory probe completed preview and reached the mocked model CAS; its destination equalled `before_includes[0].path`. Actual publication is inferred from reaching that writer with matching simulated live bytes. This violates the mandatory exclusion of historical include paths from output destinations. Include the model destination in the shared collision check.

Executed two focused pytest commands, both with `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -s -p no:cacheprovider` and the default marker filter:

- MC3 include-reference, hostile dependency-walk, final-verification-order nodes, plus `tests/test_mc3_source_observations.py`: **15 passed**.
- CLI tree/flag controls, `gnd.model.validate_declarations` definition pin and chain controls, live semantic/dynamic query inventories, and architecture dirty controls: **10 passed**.

Additional `.venv/bin/python -c` probes exercised corpus preview/analysis/flattening, 40 malformed include operations, captured-byte replacement, and the two writer paths above. Source-manifest hashes matched all 15 entries. Writers were mocked; no files were edited. Initial pytest capture and heredoc attempts were blocked by the read-only filesystem; subsequent probes used `-s` and `python -c`.

The supplied large gates, real disk publication/recovery, races and cap-boundary fixtures were not rerun. Paths here are normalized to repository-relative form; no retained output file was written.