# Phase RW2: candidate build and installed acceptance

## 1. Status

**r1, draft. No ruling; no implementation.** Written on 2026-11-25 against
main `8dcfe0e7`, the merge of the RW1 pull request (282) on the owner's word.
The [plan](release-0.5.0-plan.md) is r5. No review has read this spec. The
phase has two owner gates of its own beside this spec's ruling: the merge of
the acceptance-probes pull request, and the two choices in §7 that the plan
left to the owner (D2 and D4).

## 2. Provenance

This spec derives from plan §2, §4 (RW2), §9, §11 ("Panel fixes") and §14,
from the [RW1 record](../002-phase-RW1.md), and from the predecessor phase
[RV2](../../release-0.4.0/008-phase-RV2.md) with
[its spec](../../release-0.4.0/notes/phase-RV2-spec.md), whose recipe it
repeats. Two things differ from the plan's outline, both because main
changed after the plan was written:

- the release carries three more milestones than the plan's four probes
  cover (growth from a reviewed vocabulary, the literature examples from a
  host, and the Ossie relational files);
- one existing regression, Q1 of `test_installed_0_3_0_regressions`, asserts
  that `gnd export ossie` writes three files. On 0.5.0 it writes five.

Every 0.4.0 result below was measured on 2026-11-25 with the wheel PyPI
serves for 0.4.0 (SHA-256
`36288e7a918b17d14ea307b6492acfbad741755e1e83818641836452cee9ea5c`, the
digest the 0.4.0 release records hold), installed in its own environment,
against this tree at `8dcfe0e7` installed editable. The
[measurement](../evidence/RW2/controls-0.4.0.md) has the commands and
outputs. These are rehearsals; acceptance evidence comes only from the
retained candidate.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RW2-C0 | before any build: the notes cover every change on the freeze commit; 0.5.0 is free on PyPI; the six-shard default lane at the freeze commit has no failure RW1's run lacks | plan §4 | step 3; T6 |
| RW2-C1 | the acceptance probes reach main through an owner-merged pull request | plan §4, §11 "One candidate commit" | step 2 |
| RW2-C2 | a build and a second build from the same named main commit, compared by hash | plan §4 | step 4; T7 |
| RW2-C3 | acceptance over the retained files, with `SOURCE_COMMIT` and `SHA256SUMS` verified on the receiving host before the run | plan §4 | step 5; T8 |
| RW2-C4 | the probes, each with its 0.4.0 availability control and its candidate behavior control; the 0.3.0 control retired | plan §2, §11 | M1, §6 "Probes" |
| RW2-C5 | `uvx --from <wheel> gnd --version` prints `gnd 0.5.0` | plan §4 | T9 |
| RW2-C6 | the observed profile is recorded and no other is claimed | plan §4 | the record |
| RW2-C7 | `pytest -m pyrel_oracle` at the freeze commit, selected by the owner on 2026-11-23 | plan §4, §11 RW-D8 | T10 |
| probe coverage | each user-visible change since `v0.4.0` maps to an installed probe with its 0.4.0 control, or to a stated reason for none | plan §11 | §6 "Coverage" |
| retired controls | the table of plan §11, with line numbers at the base | plan §11 (R11) | §6 "Retired" |
| oracle environment | the tutorials runtime environment is checked before the freeze; if absent, C7 does not run and is not reported as run | plan §11 | step 3 |
| plan §14 | `ossie_oracle` at the freeze is the owner's choice; a fifth probe is proposed | plan §14 | D2, D4 |
| structure guards | RW2 changes a test, so the guards run | plan §11 "§9", `project.md` | T4 |
| RW1 open question | issue links for the Ossie bullets | RW1 record | D6 |

## 4. The standing rules, bound to this phase

- Plan rule 1: nothing is uploaded, tagged or released. The two builds make
  local files only.
- Plan rule 3: the install pins stay at 0.4.0.
- Plan rule 5 and `docs/releasing.md`: a rebuilt candidate is a new
  candidate; its own acceptance run is its evidence.
- Plan rule 7: `release.yml`, the publisher configuration and the
  dependencies are not edited.
- `project.md` rules 1 to 4: the phase adds no consumer of untrusted input,
  no validation boundary and no policy walk. It adds tests.
- AGENTS.md, "General solutions, not pattern-matched ones": the probes read
  JSON with `json`, YAML with the wheel's own YAML library through the
  existing `YAML_TO_JSON` helper, and exported programs by the constants the
  export writes (`RULES`, `UNCHECKED`, `FLATTENING_RECORD_SHA256`), parsed
  with `ast`, never by a pattern over program text.
- `docs/releasing.md`, "Release acceptance keeps one negative control": the
  control is the release before the candidate, 0.4.0.

## 5. Goal

On beast-3, with Python 3.11 and uv 0.10.10, at the freeze commit:

- `GND_CANDIDATE_DIR=<retained> uv run --no-sync pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short`
  exits 0 over the retained candidate, for the release wheel and the
  comparison wheel;
- an independent build of the same commit has the same three SHA-256
  digests;
- `uvx --from <retained wheel> gnd --version` prints `gnd 0.5.0`;
- the six-shard default lane lists no failing test id that RW1's lane at
  `4a73af2e` lacks.

## 6. Design

The phase builds no product capability. Its one reuse decision: every probe
uses the helpers `tests/test_release_acceptance.py` already has (`installed`,
`gnd`, `gnd_json`, `copy_packaged`, `edit`, `published_wheel`,
`declared_version`), and adds none that duplicates them.

### Order of work

1. This spec is ruled (§7).
2. **The probes pull request.** M1 and M2 on a topic branch; the editable
   rehearsal of each new probe function against the 0.4.0 wheel; the
   focused checks of §8; one independent reviewer in a different tool. The
   owner merges it.
3. **The freeze (RW2-C0).** The resulting main commit is the freeze commit.
   At it: the reconciliation table gains the rows RW1's table lacks; PyPI is
   read again; the six-shard default lane runs; the tutorials runtime
   environment is checked for `relationalai` and `duckdb`. If main moves
   before the build, the freeze is void and this step runs again.
4. **Two builds (RW2-C2).** RV2's [build.sh](../../release-0.4.0/evidence/RV2/build.sh)
   with its scratch name changed: the wheel and sdist from a clean archive of
   the freeze commit, and a comparison wheel from that sdist, on the planning
   machine; the same again on beast-3; `SHA256SUMS` compared.
5. **Acceptance (RW2-C3 to C5).** RV2's
   [accept-beast3.sh](../../release-0.4.0/evidence/RV2/accept-beast3.sh)
   with the version strings moved on: the retained bundle is verified on
   beast-3 before anything runs, then the acceptance file, then `uvx`.
6. **The oracle lanes (RW2-C7, D4).** `pyrel_oracle` at the freeze commit;
   `ossie_oracle` only if the owner selects it.
7. The record, with the candidate's commit, both file sets, the stage exits
   and the profile. Its pull request holds planning files only.

### Probes

Each runs in its own pytest scratch directory, on the release wheel and the
comparison wheel, with Python `-I` and the macOS source-checkout denial the
`installed` fixture already applies. "0.4.0" below is the measured result of
the same command on the published 0.4.0 wheel.

| Probe | Candidate commands and expected result | Behavior control (candidate) | 0.4.0 control (measured) |
|---|---|---|---|
| P1 judging an include root | `python -I -m gnd.examples.literature.interop run --out interop`. A program run by the installed interpreter writes a two-judge consumer-pinned policy and approving receipts for fact 0 of `paper_names_parent_method`, using the installed `judgment_fact_digest` and `canonical_json_bytes`. `gnd judgments check checking.orm.json composed.population.json --policy policy.json --receipts receipts.json --trusted-root . --format json` exits 0 with `outcome` 0, `error` null and `judgment_policy.admission` true | One object type is added to `vocabulary/chronology.orm.json` without a new pin. The same command exits 3 with `error` `{"message": "include:hash-mismatch", "reason": "binding"}` | The same command on the same folder exits 3 with `error.reason` `include:unsupported-route` |
| P2 `gnd flatten` | In the interop folder, `gnd flatten checking.orm.json --out flat` exits 0 and writes exactly `checking.orm.flat.orm.json` and `checking.orm.flattening.json`; the same for `extraction.orm.json`. Each record's `format` is `gnd-flattening/1` and its `includes` name `literature` and `chronology`; its `flat_model_sha256` is the SHA-256 of its flat model file | A second run into `flat` exits 11, and both files keep their bytes | `gnd flatten` exits 64: the command does not exist. No output folder is created |
| P3 PyRel rules export | From a copy of the packaged `examples/literature`: `gnd export pyrel MODEL --rules MODE --out FILE` exits 0 for `duckdb` and `lqp` on `assertions/model.orm.yaml` (external uniqueness), `model.orm.yaml` (anchored), `depth_fixture/decimal.orm.json` (`Number`) and `quantity_fixture/time.orm.yaml` (role-scoped value rules). On the interop roots it exits 0 in both rules modes for `checking.orm.json` and `extraction.orm.json`, and in the default mode for `extraction.orm.json`. Content, read from each program's constants: `RULES` of the assertions program has an entry with `info.external` true and the two `refs`; `UNCHECKED` of the anchored program lists `work_introduces_method#0` with a reason that starts `source anchor:`; `RULES` of the time program has `time_step#1` with family `value`; each include-root program has `FLATTENING_RECORD_SHA256` equal to the SHA-256 of the record P2 wrote for that root and `MODEL_INCLUDES` naming both includes | The default mode on the temporal root `checking.orm.json` exits 3 with `PyRel export does not support temporal models`. The tracked `tests/fixtures/pyrel-rules-families/review/refuse-external-frequency.orm.json` exits 3 with `external frequency is a later phase of the rules programs` in both rules modes | Exit 3 in both rules modes for each: `external uniqueness is a later phase of the rules programs`; `family 'anchored' is a later phase of the rules programs`; `primitive 'Number' is not supported by the rules programs yet`; `include:unsupported-route` for both roots in all three modes. For role-scoped value rules the packaged model is refused for its anchored rule first, so the control uses the tracked `tests/fixtures/pyrel-rules-coverage/rp4/range.orm.json`: 0.4.0 exits 3 with `role-scoped value constraints are a later phase`, the candidate exits 0 |
| P4 COUNT certificates | From a copy of the packaged `examples/literature/count_fixture`, the five commands of its README each exit 0. `replay-count` prints `count` 2 and `status` `complete` for `group.json`, and `count` 0 and `status` `empty-group` for `empty-group.json`; the empty certificate has `members` `[]` | `replay-count` of the `flow` certificate against the population with row 2 of `observation` removed exits 3 with `reason` `binding-stale` | `gnd witness-count` exits 64: the command does not exist. The packaged directory is absent |
| P5 Ossie relational files | From the packaged `examples/refunds/model.orm.yaml`: `gnd export ossie model.orm.yaml --out o.yaml` exits 0 and writes five files, the two new ones `o.yaml.semantic_model.yaml` and `o.yaml.mapping.yaml`. The semantic model's dataset names are those `gnd.rmap.map_model` returns for the model, asked of the installed package. `--ontology-only --out t.yaml` writes three files whose bytes equal the first three of the five-file run. With the packaged `physical-binding.json`, `--physical-binding` exits 0 and writes five files | A file already at `c.yaml.mapping.yaml` stops `--out c.yaml` with exit 11 and no other `c.yaml*` file is written. `--physical-binding` with `--ontology-only` exits 64. `--max-output-bytes 1` exits 3 with `ossie:output-size` | The plain export exits 0 and writes three files, with the same bytes as the candidate's first three. `--ontology-only` exits 64: the option does not exist |
| P6 seeded growth (D2) | From a copy of the packaged `examples/seeded_growth`, the eight commands of its README each exit 0, and the first `gnd validate` prints one `INCLUDE seed` line | None of its own: the growth refusals are in the default lane, and P1 holds the include control | `gnd validate root.orm.yaml` on the same copy exits 3 with rule id `semantic:unattended-u5`. The packaged directory is absent |

P1's judgment inputs are written by a program, not shipped, because they
bind the SHA-256 of files the interop run writes. The program is a string in
the test, run by the installed interpreter, as `typed_refusal` is today.

### Installed families (D3)

`FAMILIES` runs tracked test files against the installed wheel and fails on
any skip. It gains the files below, each rehearsed here with no skip:

| File | What it covers | Rehearsed |
|---|---|---|
| `test_vg3_unattended_includes.py` | growth from a reviewed vocabulary | 46 passed |
| `test_go2_operation_outcomes.py` | an outcome for every operation | 40 passed |
| `test_lh1_reading_host.py` | the reading example from a host | 98 passed, 54 s |
| `test_lh2_reading_replay.py` | replay of a host run | 30 passed, 29 s |
| `test_lr3_reference_set.py` | the labelled reference set | 22 passed |

The rehearsal ran them from the source tree. Whether each also passes with
the package installed and the source denied is what the probes pull
request's rehearsal and then the acceptance run show; a file that cannot is
dropped from the list and named in the record with its reason.

### Coverage

One row per row of RW1's
[reconciliation table](../evidence/RW1/notes-reconciliation.md).

| Rows | Change | Installed probe |
|---|---|---|
| R1 | PyRel rules programs | P3. The exactness refusals have no probe: they are in the default lane, and a probe would repeat one input each |
| R3 | include roots on more routes | P1, P2, P3. An unencodable include path has no probe: such a path cannot be created on every filesystem |
| R4 | COUNT certificates | P4 |
| R5, R12 to R14 | checker scaling, one parse per load, CRLF block scalars, the index key order | none: speed and internal structure; the default lane measures them |
| R6, R7 | growth from a reviewed vocabulary, `gnd evolve` outcomes | P6 and two families files. `narrow_proposal` and `gnd evolve summary` have no probe |
| R8, R9 | the literature examples from a host, the reference set | three families files. A live producer run has no probe: it needs a model provider |
| R10, R11, R15, R16 | pages, frontmatter fences, the 0.4.0 page edits, the notes | none: pages are not in the wheel's behavior; the frontmatter reader is in the default lane |
| R17 | Ossie relational files | P5. The size options beyond the one refusal, and binding refusals by rule, have no probe |
| R2 | one Ossie line | none: no output changes |

The RW3 dossier lists every "none" and every "no probe" clause under "what
was not measured".

### Retired (plan §11, R11), with line numbers at `8dcfe0e7`

| Test | 0.3.0 use | After RW2 |
|---|---|---|
| `test_installed_rv2_guarded_membership` (565) | 591 to 596 | removed; the three verdict cases stay |
| `test_installed_rv2_composition_and_catalog` (599) | 601, 628 to 635 | removed; the candidate's alias compose, the missing-decision, changed-catalog and manifest checks stay |
| `test_installed_rv2_literature_assurance` (674) | 698 to 701 | removed; the report comparison and the mutated population stay |
| `test_installed_rv2_expense_receipts` (704) | 723 to 725 | removed; the findings and the missing-decision refusal stay |

With them go the `published_0_3_0` fixture (432 to 436) and the 0.3.0 entry
of `PUBLISHED_WHEEL_SHA256` (244), which nothing else uses.

### Modules

| ID | Path | Change | Lines (estimate) |
|---|---|---|---|
| M1 | `tests/test_release_acceptance.py` | `PUBLISHED_WHEEL_SHA256` holds 0.4.0 and a `published_0_4_0` fixture asserts `gnd 0.4.0`; the four retirements; the guard fixture (557 to 562) requires 0.5.0; Q1 (487) expects five files; probes P1 to P6; the `FAMILIES` additions | about 230 added, about 30 removed |
| M2 | `docs/release-notes.md` | the two corrections of D5 | about 4 |
| M3 | `.gnd-planning/milestones/release-0.5.0/evidence/RW2/` | the build and acceptance scripts, their summaries, the retained `SHA256SUMS`, `SOURCE_COMMIT` and `BUILD_PROFILE`, the freeze lane, the reconciliation rows | evidence |

No input folder `tests/fixtures/release-acceptance/0.5.0/` is created: every
probe input is packaged, written by the interop run, or an existing tracked
fixture.

### Normative order

None is added. `docs/releasing.md` stays the one home of the procedure.

## 7. Decisions

| ID | Question | Readings and cost | Ruling |
|---|---|---|---|
| D1 | The `addopts` override (plan RW-D7) | `-o addopts=''` for `tests/test_release_acceptance.py` on beast-3, which selects its `distribution` and network use. Without it the file is deselected and RW2 has no acceptance | open; proposed: yes, for that file and lane only |
| D2 | Probes beyond the plan's four | (a) P5 and P6 and the families files, as §6; (b) P5 only; (c) the plan's four. (c) leaves the three milestones the owner held the release for unexercised from a wheel. Each added probe is about 25 test lines and under a minute per wheel; the two reading files add about 90 seconds per wheel | **the owner's** (plan §14); proposed: (a) |
| D3 | Which families files | the five of §6, or fewer | open; proposed: the five, less any that cannot run installed |
| D4 | `ossie_oracle` at the freeze commit | (a) run it without the consumer test, as the Ossie milestone did at `98344052` (91 passed); it needs that milestone's scratch oracle environments on this machine. (b) not run, stated in the dossier: the release then advertises the relational files on the Ossie milestone's own run, which predates three clean-ups | **the owner's** (plan §14); proposed: (a) if the environments still exist, else (b) |
| D5 | Notes corrections found while measuring | (1) The PyRel block says 0.4.0 refused "the first three" of four model features by name. 0.4.0 also refused role-scoped value constraints by name (`role-scoped value constraints are a later phase`). Proposed text: "0.4.0 refused each of them by name". (2) The `gnd flatten` bullet says `<stem>.flat.orm.json`; for `checking.orm.json` the file is `checking.orm.flat.orm.json`. That bullet was moved under D6 of RW1 and its wording is another phase's; proposed: leave it and record it as an open question for the include-roots owner | open; proposed: (1) fixed in the probes pull request, (2) recorded |
| D6 | Issue links 276 to 280 in the Ossie bullets (RW1 open question) | add them in the probes pull request, or leave the moved bullets as written | the owner's; proposed: leave |
| D7 | The reviewer for the probes diff | one reviewer in a different tool through the review helper, as RW1 | open; proposed: yes |
| D8 | Where the builds run | the planning machine and beast-3, uv 0.10.10 and Python 3.11 on both, as RV2 | open; proposed: yes |

Rulings are appended below this line, each with its date, source and the
SHA-256 of the spec bytes it covers.

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | each new probe function, rehearsed on the editable tree with the hash-checked 0.4.0 wheel as the old interpreter and an empty sandbox prefix | each passes; a control run with the 0.4.0 interpreter in the candidate's place fails each probe, shown once per probe in the record |
| T2 | `uv run pytest -q --collect-only -o addopts='' tests/test_release_acceptance.py` | collects; no import error. This measures selection only |
| T3 | the default-lane tests of the features the probes use: `tests/test_ir1_judgments_includes.py tests/test_ir2_flatten.py tests/test_ir3_pyrel_includes.py tests/test_rp5_literature_rules.py tests/test_ossie_relational.py tests/test_ossie_docs.py tests/test_vg5_seeded_growth_example.py tests/test_count_certificates.py`, with the five families files | exit 0. Each file exists at `8dcfe0e7` |
| T4 | the structure guards of `project.md`; `uv run ruff check`; `python3 scripts/components_index.py changed --base origin/main --strict` | exit 0, apart from the scaffold guard's known local failure, which the clean-clone lane settles |
| T5 | `tests/test_release_version.py tests/test_release_docs.py tests/test_release_text.py tests/test_ossie_docs.py`, the strict docs build and the site link check, because M2 edits the notes | exit 0 |
| T6 | six-shard default lane on beast-3 at the freeze commit | failing ids are only those of RW1's lane at `4a73af2e`: none, and the two RC-02 errors |
| T7 | `diff` of the two `SHA256SUMS` | no difference |
| T8 | the acceptance command of §5 on beast-3 | exit 0; the summary line is recorded |
| T9 | `uvx --python 3.11 --from <retained wheel> gnd --version` in scratch outside the checkout | `gnd 0.5.0` |
| T10 | the `pyrel_oracle` command of the pyrel-rules-coverage close record, at the freeze commit | exit 0; the summary line is recorded. If the environment is absent, not run and reported as not run |

### Verification selection

| Kind | Selection |
|---|---|
| Plan-mandated | plan §9's RW2 row: the acceptance file on beast-3 and the full default lane at the freeze commit; plan §11: the structure guards |
| Direct | T1, T2, T8, T9 |
| Impact closure | T3, T5: the features the probes call, and the notes' readers |
| Broad lanes | the default lane (T6). `pyrel_oracle` on the owner's selection (T10). `ossie_oracle` only under D4. `evidence`, `census` and the others are not run |

### Implementability

- Every probe has a command that can fail: each was run on 0.4.0 and failed
  there as the table says.
- P3's content assertions need the programs' constants. `RULES` and
  `UNCHECKED` are `json.loads` of a string literal, and
  `FLATTENING_RECORD_SHA256` and `MODEL_INCLUDES` are literals, so `ast`
  reads all four without running a program. Running one needs the PyRel
  runtime, which the wheel does not install.
- P5 compares dataset names with `gnd.rmap.map_model`. Both come from the
  same code, so the comparison shows the wheel carries the library and the
  export uses it, not that the mapping is right; the mapping's correctness is
  the Ossie milestone's corpus.
- The acceptance run downloads the 0.4.0 wheel from PyPI. beast-3 needs
  network access, as it did for 0.3.0.
- RW2-C0's lane can only be run after the probes pull request merges, so
  its result is not known when the owner merges that pull request. If the
  lane then fails, the repair is a new pull request and a new freeze.

## 9. Out of scope for this phase

- The install pins, `RELEASED`, `docs/releasing.md` (RW3 and the
  publication stage).
- Any upload, tag or release, and `release.yml`.
- Any change under `src/`. A probe that fails on the candidate is a finding
  for the owner, not a repair made here.
- Rewording a bullet another phase wrote, except D5 (1), which corrects text
  RW1 wrote.

## 10. Size

About 230 test lines added and 30 removed, about 4 notes lines, two release
builds, two six-shard lanes at most (the freeze, and once more if the freeze
is void), one acceptance run of about 40 minutes for both wheels. Past 350
added test lines the phase pauses.

## 11. Approval instrument

This prose and the measured table of §6. Corpus-first is not used: the phase
changes no serialized format, exit code or validation predicate.

## Verification commands

```bash
uv run pytest -q --collect-only -o addopts='' tests/test_release_acceptance.py
uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_release_text.py tests/test_ossie_docs.py --tb=short
uv run ruff check
python3 scripts/components_index.py changed --base origin/main --strict
uv run --group docs zensical build --strict
uv run python tools/check_docs.py site
GND_CANDIDATE_DIR=<retained> uv run --no-sync pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short
```

The structure-guard command is the one in `project.md`. The builds, the
freeze lane and the acceptance run use the scripts of step 4 and step 5.
