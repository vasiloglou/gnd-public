# RV2 candidate build and installed acceptance

Base `bcc4a5287d24822c7a7d48048351eb0653d10526` is the owner-authorized
RV1 merge of PR 208. The [RV1 record](../005-phase-RV1.md) supplies the default
lane comparison and carries the publication text to RV3. The
[plan](release-0.4.0-plan.md#11-amendments-after-the-standard-panel-2026-11-17)
requires a second owner-merged PR for the acceptance code before candidate
freeze. RV-D0 and the owner's later explicit selection authorize one Claude
Code Opus reviewer for the RV2 diff.

## Obligations and order

| Criterion | Evidence |
|---|---|
| RV2-C0 | Freeze at an actual main commit containing the acceptance code. Reconcile main since RV1, inspect PR 204 if it merged, verify version 0.4.0 availability on the public index, and run six default-lane shards on beast-3 before building. Compare failure IDs to V13 and RV1. |
| RV2-C1–C3 | Use the predecessor RN2 recipe to build a wheel, sdist and comparison wheel from a clean archive of the same main commit. Preserve source identity, tool versions and file hashes. Build independently on beast-3 with uv 0.10.10 and compare all three hashes. Validate the copied original bundle before the gate. Run the acceptance file from a clean checkout of that exact main commit. |
| RV2-C4 | Retain RN2's five positive checks, replace the old availability wheel and add all five probes below on both the release wheel and the comparison wheel. |
| RV2-C5 | Run pinned `uvx --from <retained release wheel> gnd --version` in new scratch outside the checkout and assert `gnd 0.4.0`. |
| RV2-C6 | Record observed Python, macOS, uv and candidate digests. The acceptance profile is Python 3.11 and uv 0.10.10 on beast-3. The default lane retains its Python 3.13.18 and uv 0.13.7 baseline and two known optional-wheel setup errors. |

Before any release build, publish the probe changes through a topic PR, run
focused checks and complete its independent diff review. Stop for the owner's
specific authorization to merge that PR. After it lands, wait for C0 checks
to finish before creating candidate files. RV1's authorization to merge PR 208
covers that PR only. The release workflow, tags, publisher configuration and
runtime upload stay outside RV2 under RV-D5 and RV-D9.

## Acceptance code and inputs

Change `tests/test_release_acceptance.py` only. Keep RN2 positive checks as
regressions against whatever version the archived revision declares. Require
0.4.0 and `gnd --version` in the new suite before touching probe inputs. Use
the existing installed fixture, its archive, temporary directories, Python
`-I`, resource copier and macOS source-checkout denial. The 0.3.0 fixture
downloads the public wheel, verifies the whole-file SHA-256
`143890eed5e30e19619cd5c1106bddae6283c672d5c63200018fb23157c6751b`, and
installs it into its own environment. RN2 also records the 0.3.0 sdist
`5e40d9e358ef49d335a4b0cf2c0919aff73a029076efa4f7c706b30109034c42`.
The sdist digest is provenance for RN2. The installed old control uses the
wheel only.

Each new probe runs in an isolated pytest scratch directory.

| Probe | Candidate command and measured outcome | Behavior control and 0.3.0 absence control |
|---|---|---|
| P1 guarded comparison | Parse archived `tests/fixtures/models/guarded_minimal.orm.yaml` using installed YAML, retain the travel guard, add `where $a >= 100` and replace its consequent with `$a in [150, 200]`. Run `gnd validate guard.json` and `gnd check guard.json population.json --guarded-diagnostics --format json`, both exit 0 for travel amount 150 and one passing guard binding. | Amount 250 exits 1 with one failing bound guard. Amount 50 excludes the binding and yields a vacuous guard. The 0.3.0 validation exits 3 with `jsonschema:oneOf` and `jsonschema:unevaluatedProperties` at `$.constraints[0]`. |
| P2 two includes and resolution | Run `python -I -m gnd.examples.literature.interop run --out interop`. Check that the authored root has both includes, the generated manifest binds a same decision, the composition record uses decision zero, and a separate `gnd check checking.orm.json composed.population.json --composition composition.json --sources sources --format json` exits 0. | Change the only resolution decision to different, rebind its manifest digest, and run `gnd compose checking.orm.json sources --out mutant.population.json --record mutant.composition.json`. Expect exit 3 and `decision 0 (different) keys end joined`, with no output pair. A separate catalog-free LI2 `A-alias` resolution succeeds in the candidate. The same inputs on 0.3.0 exit 3 with the manifest's missing or unexpected fields diagnostic. |
| P3 catalog witness and replay | In the interop output, run `gnd witness checking.orm.json composed.population.json --targets targets.json --composition composition.json --raw --out rv2.witness.json` and `gnd replay checking.orm.json composed.population.json rv2.witness.json --composition composition.json --raw`, both exit 0. The proof has a fixed reference origin. | Append one byte to `reference/catalog.json`. Installed `bind_references(load_model(...), root=...)` must raise `ReferenceHashMismatch`; witness and replay both exit 3 with `binding-stale`. On 0.3.0, composition of the unchanged catalog case exits 3 with the specific unsupported reference populations diagnostic. |
| P4 assurance reference | Copy packaged `gnd/examples/literature` into scratch. Run `python -I -m gnd.examples.literature.assurance_report literature literature/answers/answer-key.json literature/runs/reference` at exit 0. Compare the full report against the archived reference golden using the existing recorded-version helper, verifying the live version and harness SHA against the tracked installed source first. | Remove facts from the copied composed population and rerun. Expect exit 1 and the identity-decisions, derivation and freshness failures. The 0.3.0 wheel lacks the assurance module resource. |
| P5 receipts walkthrough | Copy packaged `examples/expense/receipts`, run `gnd compose checking.orm.json claim --out claim.population.json --record claim.composition.json` and `gnd check checking.orm.json claim.population.json --composition claim.composition.json --sources claim --format json`. Assert the exact documented offending rows for the three constraints. | Use the fixture's valid `claim-missing` directory to verify exit 3 and `joined without a same decision`, with no output pair. The 0.3.0 wheel lacks the packaged receipts resource. |

Fresh editable and separately installed 0.3.0 rehearsals established the
diagnostics above, including the old guarded schema refusal, missing
resolution fields, unsupported catalog composition, the repinned decision
mutant, and the failed assurance stages. These rehearsals are implementation
controls. Acceptance evidence comes from retained files of the merged freeze.

## Verification selection and records

Before the merge, run the default-lane direct source tests for the guarded,
LI1, LI2, LX3, LX4 and receipts paths, and the repository structure guard block
and Ruff. Run the new probes in the isolated editable rehearsal and retain
its profile and exact test counts. The primary post-merge acceptance command is
`GND_CANDIDATE_DIR=<retained> uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short`
on beast-3. RV-D7 selects that file's distribution lane. Record the excluded
default markers separately. No historical or native lane is activated.

Use the existing assertion harness plus committed fixtures as the approval
instrument. E1 and the rehearsals supply discriminator evidence. This adds
tests, with no shipped parser or untrusted input contract, no new policy
walk, and no changed runtime ordering. Keep the canonical publication
procedure in `docs/releasing.md`. Preserve historical hashes and assertions.
The phase record names the precise candidate commit and both artifact sets,
the stage exits, the merge authority and the verification profile.

Budget is up to 230 net test lines and two release builds. Six default shards
run at freeze. Timeouts stay bounded by the existing acceptance helpers.
Independent diff review follows the pre-merge tests. Findings about a released
wheel are verified after freeze under this same specification.
