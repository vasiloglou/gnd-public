# RW2: what the published 0.4.0 does on each planned probe

Measured on 2026-11-25 on the planning machine for the RW2 spec. These are
rehearsals. They are not acceptance evidence: that comes from the retained
candidate on beast-3.

- **Old**: the wheel PyPI serves for 0.4.0, `get_nick_done-0.4.0-py3-none-any.whl`,
  SHA-256 `36288e7a918b17d14ea307b6492acfbad741755e1e83818641836452cee9ea5c`
  (the digest in the 0.4.0 release records), installed in its own
  environment with Python 3.11. `python -I -m gnd --version` printed
  `gnd 0.4.0`.
- **New**: this tree at `8dcfe0e7`, installed editable; it declares 0.5.0.
- Every command ran as `PYTHON -I -m gnd ...` in a scratch folder outside
  the checkout. Inputs were copied out of the new package with
  `importlib.resources`, or written by
  `python -I -m gnd.examples.literature.interop run --out interop`.
- Scripts: [rehearse.py](rehearse.py) for P1, P2, P4 and P5, and
  [rehearse-p3.sh](rehearse-p3.sh) for P3. P6 and the single controls below
  were run by hand with the same interpreters.

## P1 judging an include root

| Command | New | Old |
|---|---|---|
| `gnd judgments check checking.orm.json composed.population.json --policy policy.json --receipts receipts.json --trusted-root . --format json` | exit 0; `outcome` 0, `error` null, `judgment_policy.admission` true | exit 3; `error` `{"message": "include:unsupported-route", "reason": "include:unsupported-route"}` |
| the same after adding an object type to `vocabulary/chronology.orm.json` without a new pin | exit 3; `error` `{"message": "include:hash-mismatch", "reason": "binding"}` | not run |

## P2 `gnd flatten`

| Command | New | Old |
|---|---|---|
| `gnd flatten checking.orm.json --out flat` | exit 0; writes `checking.orm.flat.orm.json` and `checking.orm.flattening.json`; the record's `format` is `gnd-flattening/1`, its `includes` are `literature` and `chronology`, its `flat_model_sha256` is the flat file's SHA-256 | exit 64; `invalid choice: 'flatten'`; no folder created |
| the same again | exit 11; `output exists: flat/checking.orm.flat.orm.json` | not run |
| `gnd flatten extraction.orm.json --out flat` | exit 0; the same two files for that root | not run |

Also seen: `gnd check flat/checking.orm.flat.orm.json composed.population.json`
exits 3, because reference paths in the flat model stay relative to the
root model's folder, as the command's note says. No probe uses it.

## P3 PyRel export

`gnd export pyrel MODEL --rules MODE --out FILE`, and with no `--rules` for
the default mode. Exit codes; the old message is the last line of standard
error.

| Model | Mode | New | Old |
|---|---|---|---|
| `assertions/model.orm.yaml` | duckdb, lqp | 0 | 3: `constraints_0: external uniqueness is a later phase of the rules programs` |
| `model.orm.yaml` | duckdb, lqp | 0 | 3: `work_introduces_method#0: family 'anchored' is a later phase of the rules programs` |
| `depth_fixture/decimal.orm.json` | duckdb, lqp | 0 | 3: `primitive 'Number' is not supported by the rules programs yet` |
| `quantity_fixture/time.orm.yaml` | duckdb, lqp | 0 | 3: `time_step#0: family 'anchored' is a later phase of the rules programs` |
| `lineage/model.orm.yaml` | duckdb, lqp | 0 | 3: `constraints_0: external uniqueness is a later phase of the rules programs` |
| each of those five | default | 0 | 0 |
| `interop/checking.orm.json` | duckdb, lqp | 0 | 3: `include:unsupported-route: pyrel_rules:2267` |
| `interop/checking.orm.json` | default | 3: `PyRel export does not support temporal models in Phase 1` | 3: `include:unsupported-route: export.pyrel` |
| `interop/extraction.orm.json` | default, duckdb, lqp | 0 | 3: `include:unsupported-route` |
| `tests/fixtures/pyrel-rules-coverage/rp4/range.orm.json` | duckdb | 0 | 3: `graded: role-scoped value constraints are a later phase` |
| `tests/fixtures/pyrel-rules-coverage/rp4/any-named.orm.json` | duckdb | 0 | 3: `graded: role-scoped value constraints are a later phase` |
| `tests/fixtures/pyrel-rules-coverage/rp4/fact.orm.json` | duckdb | 0 | 3: `has_grade#0: family 'value' is a later phase of the rules programs` |
| `tests/fixtures/pyrel-rules-families/review/refuse-external-frequency.orm.json` | duckdb, lqp | 3: `ef: external frequency is a later phase of the rules programs` | lqp: the same; duckdb not run |

Constants read from the new programs with `ast`, without running them:

- the assertions program's `RULES` has `constraints_0` with `info.external`
  true and `refs` `[["assertion_names_passage", "passage"], ["assertion_names_work", "work"]]`;
- the anchored program's `UNCHECKED` lists `work_introduces_method#0` with a
  reason that starts `source anchor:`;
- the time program's `RULES` has `time_step#1` and `time_step#2` with family
  `value`;
- each include-root program's `FLATTENING_RECORD_SHA256` equals the SHA-256
  of the record `gnd flatten` wrote for that root, in every mode, and
  `MODEL_INCLUDES` names `literature` and `chronology`.

## P4 COUNT certificates

| Command | New | Old |
|---|---|---|
| `gnd check model.orm.yaml population.json` | exit 0 | exit 0 |
| `gnd witness-count ... --request group.json --raw --out flow.cert.json` | exit 0 | exit 64; `invalid choice: 'witness-count'` |
| `gnd replay-count ... flow.cert.json --request group.json --raw` | exit 0; `count` 2, `status` `complete` | not run |
| the same two for `empty-group.json` | exit 0; `count` 0, `status` `empty-group`, `members` `[]` | not run |
| `replay-count` of the `flow` certificate against the population without row 2 of `observation` | exit 3; `reason` `binding-stale` | not run |

The old package has no `examples/literature/count_fixture` folder.

## P5 Ossie relational files

| Command | New | Old |
|---|---|---|
| `gnd export ossie model.orm.yaml --out o.yaml` | exit 0; five files | exit 0; three files, each with the same bytes as the new run's first three |
| `... --out t.yaml --ontology-only` | exit 0; three files, each with the bytes of the five-file run's first three | exit 64; `unrecognized arguments: --ontology-only` |
| `... --out s.yaml --max-output-bytes 1` | exit 3; `ossie:output-size` | exit 64; `unrecognized arguments` |
| `... --out c.yaml` with a file already at `c.yaml.mapping.yaml` | exit 11; no other `c.yaml*` file | not run |
| `... --out b.yaml --physical-binding binding.json` | exit 0; five files | not run |
| the same with `--ontology-only` | exit 64; `--physical-binding cannot be used with --ontology-only` | not run |

The semantic model's dataset names for the refunds model are `refund`,
`refund_amount` and `refund_channel`, the names `gnd.rmap.map_model` returns.

## P6 seeded growth

The eight commands of the packaged README, from a copy of
`examples/seeded_growth`.

| Command | New | Old |
|---|---|---|
| `gnd validate root.orm.yaml` | exit 0; one `INCLUDE` line | exit 3; `semantic:unattended-u5` on the included constraint |
| the two `evolve preview` and two `evolve apply` commands | exit 0 each | 3, 66, 11, 66 |
| `gnd validate` with both documents and `--require-documents` | exit 0 | exit 3 |
| `gnd check root.orm.yaml population.json` | exit 0 | exit 3 |
| `gnd judgments check ...` | exit 0 | exit 3 |

The old package has no `examples/seeded_growth` folder.

## Families files, from the source tree

`uv run pytest -q tests/FILE -p no:cacheprovider`:

| File | Result |
|---|---|
| `test_vg5_seeded_growth_example.py` | 13 passed |
| `test_vg3_unattended_includes.py` | 46 passed |
| `test_lh1_reading_host.py` | 98 passed in 54 s |
| `test_lh2_reading_replay.py` | 30 passed in 29 s |
| `test_lr3_reference_set.py` | 22 passed |
| `test_go2_operation_outcomes.py` | 40 passed |
| `test_go5_round_summary.py` | 22 passed |

None skipped. Not run with the package installed and the source denied.
