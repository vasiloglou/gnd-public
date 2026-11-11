# Phase RN2: candidate build and installed acceptance

## 1. Status

**Awaiting owner review, 2026-11-11.** Draft r1. D5 is ruled (the Ossie oracle
lane is not run for 0.3.0); D1 to D4 and D6 are open, and the spec itself is
not approved.
No implementation file is created or edited, and nothing is built.

## 2. Provenance

Derives from [the plan](release-0.3.0-plan.md) r2 §2 and §4 (RN2-C0 to C6),
its ruled decisions RN-D2, RN-D5, RN-D6, RN-D8 and RN-D9, the records of
[RN0](../002-phase-RN0.md) and [RN1](../003-phase-RN1.md), and the predecessor
phase [RR2](../../rule-check-release/003-phase-RR2.md) with its
[spec](../../rule-check-release/notes/phase-RR2-spec.md), whose build steps
and test surface this phase reuses. Baseline: main `f9f502d9` (the PR 163
merge). No review has run over these bytes.

Every expected value in §6 was observed in this session on 2026-11-11: on the
0.3.0 tree at `f9f502d9`, and on the retained 0.2.0 wheel (sha256
`e323c19e…69e4`, the published file) installed in a scratch environment. Each
is also traced to a source that is not the output under test.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RN2-C0 | before any build, the notes cover every change on the candidate commit, PR 160 and PR 161 included; 0.3.0 is still free on PyPI | plan §4 | V1 |
| RN2-C1 | from `git archive` of the named main commit, the two `uv build` commands of `release.yml` give wheel, sdist and comparison wheel; `SHA256SUMS` verifies; tool versions recorded | plan §4 | M3, V2 |
| RN2-C2 | a second independent build is compared by hash; a difference is explained and does not block | plan §4, RL-D7 as inherited | M3 (B2), V3 |
| RN2-C3 | `GND_CANDIDATE_DIR=... uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short`, verbatim summary | plan §4, RN-D8 | V4 |
| RN2-C4 | the five probes of plan §2, each with a 0.2.0 availability control and a named candidate behavior control; complete commands with named inputs | plan §2 (as repaired after review P4, P5), RN-D9 | M2, T1, T2 |
| RN2-C5 | `uvx --from <wheel> gnd --version` prints `gnd 0.3.0` | plan §4 | V5 |
| RN2-C6 | the observed profile is recorded; no other is claimed | plan §4 | V4, record |
| R5 | the wheel carries the Ossie schema files | plan §6; RN0 boundary | T1 probe Q1 and its artifact row |
| R6 | a probe must not pass on 0.2.0 too | plan §6 | T2 |
| RN1 boundary | whether 0.3.0 is still free on a later day | `003-phase-RN1.md` | V1, V7 |
| RN1 open question D7 | the Ossie oracle lane before the candidate is built | `phase-RN1-spec.md` D7 | D5 |
| Predecessor accepted residual | the 0.1.0 control downloads from PyPI on every run | `rule-check-release/005-milestone-close.md` | D3: the 0.2.0 control does the same |
| Plan rule 1 | no upload, tag, release or workflow edit | plan §0 | §9, V8 |
| Plan rule 7 | `release.yml`, its pinned test and the dependency freeze are not edited | plan §0 | §9 |
| RN0 and RN1 lesson | run the planning-link test after the last planning file is written | their records | V9 |

## 4. The standing rules, bound to this phase

- Plan rule 1 (prepare, never publish): M3 builds and retains files; nothing
  is uploaded. V8 lists remote tags, releases and workflow runs.
- Plan rule 4 (evidence belongs to exact bytes): every result names the
  candidate commit and the file hashes; B2 is a comparison only and never
  replaces B1.
- Plan rule 5 (carrying is shown by running): Q1 to Q5 run from the installed
  wheel, outside the checkout, under the file's existing sandbox.
- Plan rule 6 and `project.md` rule 6 (measure): §6's values were observed
  before this spec; T3 shows the new test red on 0.2.0 before the candidate is
  built.
- Plan rule 7 (frozen surfaces): `tests/test_release_acceptance.py` is the
  file the prepare job runs and is edited by addition only; the workflow and
  `tests/test_release_preparation.py` are not touched.
- `project.md` rule 5 (one home): the probes assert behavior whose normative
  text is the representation format, the evolve policy reference and the two
  answer keys; the test cites them and adds no rule.
- `project.md` rules 1 to 4: no source changes; no new consumer of untrusted
  input.

## 5. Goal

A candidate directory built from one named main commit holds a wheel, an
sdist and a comparison wheel whose `SHA256SUMS` verifies, and over it the
command of RN2-C3 exits 0 with the two new tests among its passed cases, on a
recorded profile.

## 6. Design

### Modules

**M1. Release notes at the freeze (RN2-C0).** Expected to need no edit: the
0.3.0 section was written at RN1 and no source change has merged since. V1
checks this by listing `git log f9f502d9..C -- src docs` for the candidate
commit `C`; any entry is reconciled into the 0.3.0 section before the build.

**M2. `tests/test_release_acceptance.py` (about 190 added lines) and
`tests/fixtures/release-acceptance/0.3.0/` (new, about 12 small files).**
Additions only.

```python
PUBLISHED_WHEEL_SHA256 = {..., '0.2.0': 'e323c19e303f3b7fe9cbe7528e68021d271589ce0b91fd54bd76b2b919a069e4'}

@pytest.fixture(scope='module')
def published_0_2_0(tmp_path_factory)    # as published_0_1_0: fetch, check the hash, install outside the checkout

def copy_packaged(python, prefix, env, work, relative) -> Path
    """Copy one file or directory of the installed gnd package into work (sandboxed)."""
def copy_fixture(name, work) -> Path
    """Copy tests/fixtures/release-acceptance/0.3.0/<name> into work (done by the test process)."""

def test_installed_0_3_0_carries(candidate, installed, tmp_path)            # T1, both wheels
def test_published_0_2_0_lacks_0_3_0_features(installed, published_0_2_0, tmp_path)   # T2
```

The fixture directory holds inputs the wheel does not carry, each a copy of
an existing tracked file, with a README naming its origin and sha256:

| File | Origin |
|---|---|
| `q4/model.orm.yaml`, `q4/model.verbalization.txt` | `tests/fixtures/unattended-model-growth/ug2/base.orm.yaml`; the one-line verbalization the UG2 harness writes |
| `q4/proposal.json` | the UG2 corpus case C01 proposal, written once by the UG2 harness's own `_workspace` function |
| `q4/populations/clean.json`, `q4/populations/violating.json` | the same corpus |
| `q5/model.orm.yaml`, `q5/ledger.txt`, `q5/annex.txt` | `ug3/models/span-element.orm.yaml`, `ug3/documents/` |

**Expected values, T1 (candidate).** `W` is the test's own directory outside
the checkout. Sources: F = `gnd-orm-core` representation format; P =
`docs/reference/evolve-policy.md`; K2, K3 = the UG2 and UG3 answer keys
(`expected.json`); H = `docs/how-to/share-an-ossie-ontology.md`.

| Probe | Run (from the installed wheel) | Field | Expected | Source |
|---|---|---|---|---|
| version | `python -I -m gnd --version` | stdout | `gnd 0.3.0`, the checkout's `[project] version` | plan rule 2 |
| artifact | the wheel's `RECORD`, read by the test | entries | `gnd/schema/ossie/PINNED.json`, `gnd/schema/ossie/core-spec.json`, `gnd/schema/ossie/ontology.json`, `gnd/ossie-loss-report.schema.json` | R5; `src/gnd` tree |
| Q1 Ossie | `export ossie model.orm.yaml --out o.yaml` on the packaged refunds model copied into `W` | exit; files written | 0; `o.yaml`, `o.yaml.gnd.json`, `o.yaml.loss.json` | H table |
| | | the ontology | holds a relationship named `refund_by` with `multiplicity: ManyToOne` | H lines 31 to 41 |
| | `import ossie o.yaml --out restored.orm.json` | exit; files | 0; `restored.orm.json`, `restored.orm.json.loss.json` | H table |
| | | import report | `schema` `gnd-ossie-import-loss/1`; `source_identity_verified` `true`; `source_model_identity` equals Q2's identity of the same model | F "Ossie interchange"; H ("the same model identity") |
| Q1 control | a copy of the three export files with `refund_by` changed to `refund_bx` in the ontology only, then `import ossie` | exit; stderr; output files | 3; `ossie-import:binding`; none written | F (the sidecar binds the ontology's bytes) |
| Q2 identity | `validate model.orm.yaml --identity` (refunds) | exit; stdout | 0; two lines; line 1 is `MODEL IDENTITY sha256:<hex> (identity_version 2)` and `<hex>` is the sha256 of line 2 plus a newline, recomputed by the test | F "Model identity (canonical, versions 1 and 2)"; `gnd.output._print_model_identity` docstring |
| Q2 control | the same model with the object type name `Refund` changed to `RefundX` | line 1 | a different `<hex>`, which again equals the recomputed digest of its line 2 | F |
| Q3 includes | `validate sales.orm.json` in the packaged `examples/expense/teams` directory copied into `W` | exit; stdout | 0; `OK: sales.orm.json is a valid GND ORM model` | F "Model includes (version 5)" |
| Q3 control | a copy with the include's `sha256` replaced by 64 zeros | exit; issue | 3; `include:hash-mismatch` at `$.includes[0]` | F include refusals |
| Q4 clean data | `evolve preview model.orm.yaml proposal.json --workspace . --records records --out preview.json --format json --policy additive --populated customer_places_order --check-population populations/clean.json` | exit; preview | 0; `population_check.admitted` names operation 0; `policy_issues` is empty | K2 case C01 |
| Q4 control | the same with `populations/violating.json`, a fresh `--out` | exit; preview | 3; operation 0 is a policy issue and is not admitted | K2 case C03 |
| Q4 control | the same without `--check-population` | exit; issue cell | 3; `constraint.populated.add` | P; K2 |
| Q5 spans | `validate model.orm.yaml --document ledger.txt --require-documents` | exit; issue | 3; `unattended:spans-unchecked`, "1 of 10 source spans were not re-hashed" | K3 case A4 |
| Q5 control | the same with `--document annex.txt` added | exit | 0 | K3 case A3 |
| Q5 control | the first command without `--require-documents` | exit; warning | 0; one `unattended:spans-unchecked` warning | K3 case A2a |

**Expected values, T2 (the published 0.2.0).** Same inputs, written by the
candidate's interpreter into T2's own directory.

| Probe | 0.2.0 run | Expected (observed 2026-11-11) | What it shows |
|---|---|---|---|
| version | `--version` | `gnd 0.2.0` | the control is the published package |
| Q1 | `export ossie …`; `import ossie …` | exit 64, `invalid choice: 'ossie'`, both | the commands are new |
| Q2 | `validate model.orm.yaml --identity` | exit 64, `unrecognized arguments: --identity` | the option is new |
| Q3 | `validate sales.orm.json` | exit 3, `$.version: 5 is not one of [1, 2, 3, 4]` | the format is new; the notes' incompatibility claim holds |
| Q4 | the clean-data command | exit 64, `unrecognized arguments: --check-population` | the option is new |
| Q4 | the command without the option | exit 3, `constraint.populated.add` | the refusal the option lifts already existed |
| Q5 | the `--require-documents` command | exit 64 | the option is new |
| Q5 | `validate model.orm.yaml --document ledger.txt` | exit 0 and no `spans-unchecked` text | the count is new |

**M3. The build (commands recorded verbatim; no tracked script).** As the
predecessor's M3, with `C` the candidate commit:

```sh
mkdir src && git -C <repo> archive C | tar -x -C src
cd src && uv build --out-dir ../candidate/release
mkdir -p ../candidate/source && tar -xzf ../candidate/release/*.tar.gz -C ../candidate/source
uv build --wheel ../candidate/source/* --out-dir "$PWD/../candidate/comparison"
rm -f ../candidate/release/.gitignore ../candidate/comparison/.gitignore
echo C > ../candidate/SOURCE_COMMIT; python --version > ../candidate/BUILD_PROFILE; uv --version >> ../candidate/BUILD_PROFILE
cd ../candidate && shasum -a 256 release/* comparison/* > SHA256SUMS && shasum -a 256 -c SHA256SUMS
```

B1 (the candidate) is built on this Mac with uv 0.10.10, the workflow's pin.
B2 (the comparison) and V4 run on beast-3 with uv 0.10.10 obtained as
`uvx --from uv==0.10.10` and Python 3.11, by an adapted copy of the
predecessor's retained script (`rule-check-release/evidence/RR2/beast3-script-run2.sh`).

### Normative order

1. M2 lands on a topic branch with T3's red run; the owner merges it (D1).
2. V1 at the merge commit `C`; then B1, B2, V2 to V5.
3. The record, with `SHA256SUMS`, `SOURCE_COMMIT` and `BUILD_PROFILE`, on a
   second pull request.

## 7. Decisions

| ID | Question | Readings and cost | Recommendation |
|---|---|---|---|
| D1 | Which commit is the candidate? | (a) the main merge commit of the pull request that adds M2, so the candidate's own tree holds the tests that accept it; the phase pauses there for the owner's merge. (b) main as it is now, `f9f502d9`, with M2 merged afterwards: one pause fewer, but the candidate's tree lacks its own acceptance test, and a later prepare run on that commit could not repeat the probes | (a), as for 0.2.0 |
| D2 | Where are the candidate files kept? | (a) outside git, at `~/gnd-release/0.3.0/<C short>/` on this Mac with a copy on beast-3; the record commits `SHA256SUMS`, `SOURCE_COMMIT`, `BUILD_PROFILE`. (b) commit the files (about 6.5 MB) | (a), as for 0.2.0 |
| D3 | Where does the 0.2.0 control run? | (a) inside the acceptance file, fetching the published wheel and checking its hash, as the 0.1.0 control does; every later prepare run repeats it and needs the index. (b) a one-off recorded run | (a) |
| D4 | The existing 0.1.0 rule-check tests in the same file | (a) keep them: they still pass on the 0.3.0 candidate and still download 0.1.0. (b) retire the 0.1.0 control now that 0.2.0 is the baseline: an edit to a test the predecessor's owner accepted | (a) |
| D5 | The opt-in `ossie_oracle` lane (RN1 D7; RN0 D5 was approved as "run it once") | (a) run it on the candidate commit before B1; needs the pinned checkout's path in `GND_OSSIE_ORACLE_ROOT`, which this session does not have. (b) not run for 0.3.0: the changed exporter is covered by the default-lane Ossie tests, RN0's byte comparison over the census and Q1. The dossier then says the pinned upstream validator has not seen the 0.3.0 exporter | the owner's call; (a) if the path can be given. **Ruled (o, 2026-11-11): (b), not run for 0.3.0** ("Skip it for 0.3.0", answering the three options this session gave: supply the path, rebuild the scratch directory, or skip). The dossier (RN3) states that the pinned upstream validator and parser have not been rerun since RN0, with RN0's byte comparison as the supporting evidence. This also answers RN1's D7 |
| D6 | A review over this spec before implementation? | the owner's call; the diff gets one independent reviewer either way | none |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `test_installed_0_3_0_carries[release]`, `[comparison]` | passes every row of the T1 table |
| T2 | `test_published_0_2_0_lacks_0_3_0_features[release]`, `[comparison]` | passes every row of the T2 table |
| T3 (red first) | T1 over a candidate directory assembled from the published 0.2.0 wheel and sdist | fails at the version row or the first Q1 run (exit 64, expected 0); recorded before the real candidate is built |
| T4 | the existing tests of the file | unchanged and pass (V4) |
| T5 | `tests/test_release_version.py`, `tests/test_release_docs.py`, `tests/test_release_preparation.py`, `tests/test_development_scaffold.py` | exit 0 |

Verification steps: V1 the freeze check (M1) and the PyPI simple index; V2
`shasum -a 256 -c SHA256SUMS` on B1; V3 B1 against B2 by hash; V4 the command
of RN2-C3 on beast-3; V5 `uvx --from <wheel> gnd --version`; V6 the
hidden-input check, which is the file's own sandbox on macOS; V7 the PyPI
index again after V4; V8 `git diff --stat f9f502d9 C -- .github`, `git
ls-remote --tags origin`, `gh release list`, `gh run list --workflow
release.yml`; V9 the planning-link test after the record is written.

Branches: each probe row has an assertion that can fail it. The behavior
controls are the changed ontology (Q1), the renamed object type (Q2), the
zeroed pin (Q3), the violating population and the missing option (Q4), and
full coverage and the missing flag (Q5). T2's rows are the availability
controls. The artifact row can fail only if a schema file is absent from the
wheel, which is the case it exists for.

Verification selection: plan-mandated, V4; direct, T1 to T3; impact closure,
T5; the full default lane is not rerun in this phase unless M1 changes a
tracked docs or source file, since M2 adds one test file's cases and fixtures
that the default lane does not select (`distribution` is an opt-in lane).

## 9. Out of scope for this phase

Any upload, tag or GitHub release; dispatching `release.yml`; the dossier and
the post-publication patch (RN3); install pins and `RELEASED`; a change to
any source file; the Ubuntu profile (RN-D6: only on the owner's request);
making Ossie export honor `redact`.

## 10. Size

Estimate: about 190 test lines, about 12 fixture files copied from tracked
corpora (about 250 lines), no source lines, no docs lines unless V1 finds a
change to reconcile.

## 11. Approval instrument

This prose. The probe tables are the corpus: each row was observed and has a
source that is not the output.

## Verification commands

```bash
GND_CANDIDATE_DIR=<candidate> uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short
uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_development_scaffold.py --tb=short
```

Unresolved: the exact beast-3 script is written at implementation from the
predecessor's retained one.

## 12. Observations for this draft (2026-11-11)

- PyPI simple index at 2026-11-11T14:16:53Z: versions `0.1.0` and `0.2.0`;
  0.3.0 is free.
- The retained 0.2.0 wheel at `~/gnd-release/0.2.0/7c0f4d0e/candidate/release/`
  has sha256 `e323c19e303f3b7fe9cbe7528e68021d271589ce0b91fd54bd76b2b919a069e4`,
  the value the predecessor recorded for the published file.
- Every row of the two tables was run once, by hand, on the `f9f502d9`
  checkout's environment (`gnd 0.3.0`) and on that wheel in a scratch
  environment (`gnd 0.2.0`, Python 3.14). Not yet observed: the same rows from
  a built 0.3.0 wheel, under the sandbox, on Python 3.11.
- The refunds model's identity was
  `sha256:8aa0003dfd4f7f07ed9987b9595fdc3c3113846bac227c5fe4cdfa64a597cc4f`
  both from `--identity` and in the Ossie import report. The test compares
  the two values with each other and does not pin this literal.
