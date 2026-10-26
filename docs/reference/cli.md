# Find the right command

Use this page as a task index. The installed `--help` is the complete argument
reference for your version. Uppercase names below are placeholders for files
you have authored; these forms are contextual, not a script to paste as a unit.
For complete runnable examples, start with [BookRec](../bookrec/01-model.md),
[expenses](../expense/01-model.md), or the [quickstart](../quickstart.md).

## Models and facts

| Command form | Result |
|---|---|
| `gnd validate MODEL --format json` | Structural and semantic model validation |
| `gnd validate MODEL --trace` | Text report of transition digests and obligations, without evaluating a walk |
| `gnd check MODEL POPULATION --format json` | Snapshot constraint and derivation findings |
| `gnd check MODEL POPULATION --admission --format json` | The check plus an asserted-occurrence admission partition |
| `gnd check MODEL --populations DIR` | Batch checking of population files |
| `gnd check MODEL --pre PRE --steps STEPS --post POST --format json` | Audit of a declared operation walk |
| `gnd verbalize population MODEL POPULATION --format jsonl` | Deterministic sentences for supplied facts |
| `gnd diff MODEL_A MODEL_B --populations DIR --format json` | Bounded comparisons over a shared vocabulary |
| `gnd coverage MODEL --check REPORT --format json` | Model-element claims and cited evidence; flags select evidence families |

Use `--anchors PATH --document PATH` for snapshot source anchoring.
Check-family reports normally apply declared redaction; `--unredacted` requests
the value-bearing view. `validate --trace` is a text surface: JSON validation
does not add trace fields.

## Project generation and change

| Command form | Result |
|---|---|
| `gnd codegen MODEL --out DIR` | Derived project files and initial extension structure |
| `gnd conformance MODEL DIR --format json` | Static integrity, currency, structure and architecture findings |
| `gnd evolve preview MODEL PROPOSAL --workspace ROOT --records DIR --out PREVIEW` | Immutable proposal preview for review |
| `gnd evolve apply MODEL PROPOSAL --preview PREVIEW --workspace ROOT --records DIR` | Model publication and linked-project rechecks |
| `gnd evolve finalize MODEL PENDING --workspace ROOT --records DIR` | Completion of an interrupted published evolution |
| `gnd discover MODEL POPULATION --out PROPOSAL --report REPORT --actor ID --requested-at 2026-10-24T12:00:00+00:00` | Candidate constraints observed in one population, as a reviewable evolve proposal plus a report ([contract](discover.md)) |
| `gnd recovery inventory ROOT --source SRC --tests TESTS --out INVENTORY` | Bounded static census of explicitly selected roots |
| `gnd recovery verify ROOT REPORT` | Recheck a recovered-model bundle and source evidence |
| `gnd import rai-orm RAI_MODEL --out DIR` | Import of the supported RAI ORM input profile and evidence |

Model authoring and recovery interpretation are agent/human workflows, not
automatic side effects of validation. See [evolution and recovery](../guides/evolution-and-recovery.md).

## Data and documents

| Command form | Result |
|---|---|
| `gnd synth MODEL --out CORPUS --class all --seed 17` | Supported labeled synthetic populations and provenance |
| `gnd measure MODEL --populations CORPUS --format json` | Per-constraint false-pass, false-fail and undecided rates |
| `gnd extract MODEL --out ARTIFACTS` | Offline schema/vocabulary bundle for a separate extraction workflow |
| `gnd verify MODEL POPULATION --artifacts ARTIFACTS --format json` | Bound extraction-handoff validation followed by checking |
| `gnd verify MODEL POPULATION --no-extraction --format json` | Explicitly check directly authored, unextracted facts |
| `gnd doccheck MODEL MANIFEST --artifacts ARTIFACTS` | Validation of a rendered document's obligations |
| `gnd fidelity MODEL --cases CASES --artifacts ARTIFACTS --format json` | Per-fact-type extraction fidelity over retained cases |

## Experiments, review, and orchestration

| Command form | Result |
|---|---|
| `gnd exp init EXP-001-example --out DIR --kind data-driven --question Q1=TEXT` | New experiment spec with a named question |
| `gnd exp validate EXPERIMENT` | Structural validation of its spec |
| `gnd exp author-expectation ...` | Author and bind an exact expected output; see command help before use |
| `gnd exp run EXPERIMENT --adapter codex` | A legacy-adapter session under the authored contract |
| `gnd exp run EXPERIMENT --adapter-policy POLICY` | A declared-policy session under the authored contract |
| `gnd exp close EXPERIMENT` | Completeness gate for questions/evidence and kind-specific obligations |
| `gnd judgments check MODEL POPULATION --policy POLICY --receipts RECEIPTS --trusted-root ROOT --format json` | Evaluate saved external opinions and evidence floors |
| `gnd review panel ...` / `gnd review panel-light ...` | Explicit advisory reviewer run; inspect help for the selected artifact kind |
| `gnd review finalize ...` | Validate and render a supplied synthesis against retained reviewer evidence |
| `gnd solve MODEL --workspace DIR ...` | Gated selected CLI station sequence and walk log |

A session adapter may invoke a configured external tool or provider. Those
prerequisites and credentials are separate from deterministic tutorial runs.

## Proofs, exports, and skill installation

| Command form | Result |
|---|---|
| `gnd witness MODEL POPULATION --targets REQUEST` | Redacted finite-witness result |
| `gnd witness MODEL POPULATION --targets REQUEST --raw --out CERTIFICATE` | Explicit new raw certificate |
| `gnd replay MODEL POPULATION CERTIFICATE --json` | Independent finite inference replay |
| `gnd witness-view CERTIFICATE --json` | Non-replayable presentation of a certificate |
| `gnd export souffle ...` / `gnd export lean ...` / `gnd export pyrel ...` | Selected bounded export profile |
| `gnd install --project` | Copy packaged skills to project discovery roots |
| `gnd doctor --project` | Diagnose installed skills and shadowing across scopes |
| `gnd install --sync` | Refresh standard roots with existing installation receipts |
| `gnd uninstall --project` | Remove managed skills while preserving user edits |

## Interpret exits in the command's context

Snapshot check and verify bands are `0` pass, `1` alethic failure, `2` vacuous,
`3` invalid input, and `4` indeterminate. A witness band `2` instead means
missing, unknown, or unsupported targets. A session band `15` means
nonacceptance; conformance band `13` means drift; closure band `14` means
incomplete obligations; solve band `17` means a halted walk.

General command refusals may use `64` for usage, `66` for missing inputs,
`70` for internal faults, or `74` for I/O. Consult the command report/help
rather than assigning one universal meaning to every nonzero exit.

The authoritative parser lives in
[cli.py](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/cli.py).
CLI composition does not enlarge the seven-function stable
[Python API](python-api.md).
