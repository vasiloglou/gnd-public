# Plan review over r2 (Codex), retained

- Instrument: one reviewer in a different tool, selected by the owner (RF-D0, "Approve as proposed", 2026-11-07). One reviewer is one reviewer; the project's plan-review bar is the maintained panel.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, 133,266 tokens, exit 0.
- Reviewed bytes: notes/report-output-fidelity-plan.md r2 sha256 dfc559bce6fcfa2d347d6ce1e332db3ff9499bfbe30e1299bcb110705e578fb1 and notes/phase-ROF1-spec.md r1 sha256 f576b349df4426bdf9c1b636b12d62bf391821bcb0bd79d25350ed42da5c2c0d, at commit f5ad4290.
- The reviewer could not run the test suite; its conclusions are by reading source (its own closing sentence says so).
- What is retained: the reviewer's final answer, below, unedited. Its tool-call transcript (about 440 KB, which contains the operator's absolute paths) is not retained.

## Reviewer output (verbatim)

DISPOSITION: block

ID: P1  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:146  
QUOTE: “no emission in this milestone (ROF5 withdrawn; issue 111 closes on ‘a caller can recompute and GND accepts it’, with the report-side gap recorded)”  
PROBLEM: Reports would still emit the legacy digest (`checking_service.py:595-630`, `payloads.py:204-205`). An external caller still cannot independently recompute the `model_digest` in a report, which is the stated issue 111 defect. Recording that gap does not close it.  
FIX: Keep issue 111 open as partially addressed, or give canonical report emission a mandatory, versioned phase and gate.

ID: P2  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:109  
QUOTE: “This is the shape `reference_model_digest` already uses (version 1), extended to every model”  
PROBLEM: The proposed version 2 excludes `operations`; version 1 for reference-bearing models does not (`values.py:201-213`). A reference wrapper has a version-1 binding and no separate operations digest (`checking_service.py:766-779`). Accepting a version-2 digest there would weaken an existing binding on an operations-only model change. The “same excluded fields” description is false for that class.  
FIX: Define and test the reference-bearing case explicitly, including an operations-only mutation and the intended wrapper binding.

ID: P3  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:235  
QUOTE: “every site in section 1 ‘consumers’ calls it”  
PROBLEM: The list mixes model matching with exact coherence and copying. `assurance/transport.py:115` requires a receipt digest to equal the digest in the exact report whose bytes it authenticates; `model/__init__.py:627` checks an in-process bound context. Neither should accept two different strings. `export/souffle_runtime.py:513` copies a binding rather than comparing it. The generated Pyrel plan has only an embedded `MODEL_DIGEST` constant and compares inside standalone generated code (`export/pyrel_rules.py:1609,2212`), so it cannot simply call a GND runtime helper.  
FIX: Classify each site by contract. Retain exact coherence checks; specify how standalone plans receive both accepted identities.

ID: P4  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:82  
QUOTE: “`witness/io.py`, … `measure/service.py:170` and `measure/report.py:218`”  
PROBLEM: The witness comparison is a whole binding-dictionary equality in `witness/kernel.py:305-314`, not a digest comparison in `witness/io.py`. Measurement first validates each sidecar against the model, then rejects a corpus containing both valid spellings because it counts distinct digest strings (`measure/report.py:218-231`). It may also emit whichever spelling appears in the sidecars (`:308`), contrary to the promise that existing reports keep the legacy digest.  
FIX: Add the witness replay site and compare only its model field through the helper while retaining exact checks on other fields. Normalize accepted sidecar identities before the mixed-corpus check and pin the emitted report identity.

ID: P5  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/phase-ROF1-spec.md:79  
QUOTE: “then render_check_rows(payload)”  
PROBLEM: `_print_projected_text` is shared by check, validate, transition, and export verification (`commands/checking.py:111,218,289`; `export/verification_service.py:220`). ROF1 changes it, while ROF2 owns the latter routes. The proposed row renderer reads snapshot fields only; it cannot reproduce the plain transition’s PRE-STATE, FRAME, and POST-STATE sections (`output.py:273-310`) or verification’s extraction line (`export/verification_service.py:526-533`). ROF1 therefore changes routes whose behavior and gates are deferred.  
FIX: Limit ROF1’s dispatch to check and validate while retaining the existing renderer for other routes, or move all affected route behavior and tests into ROF1.

ID: P6  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:197  
QUOTE: “`check --format text` and `validate --format text` (with and without `--unredacted`, with and without `--rule-ids`) print verdict lines”  
PROBLEM: `validate` has no `--rule-ids` option (`commands/checking.py:616-650`; it is registered on check at `:744-748`). A successful validate has no check verdicts: its payload starts with empty verdicts and counts (`payloads.py:207-220`), and its current text is `OK: … is a valid GND ORM model` (`commands/checking.py:123-125`). Part of the criterion cannot be invoked, and the proposed validate success layout is undefined.  
FIX: Remove `--rule-ids` from the validate matrix and specify exact validate success text separately from check verdict text.

ID: P7  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/phase-ROF1-spec.md:156  
QUOTE: “Every declared layout branch … has a case that fails it.”  
PROBLEM: T1–T4 cover a blocking verdict, a temporal run, and an issue refusal. No named fixture requires advisory, derivation findings, coverage formatting, warnings, or an error-only envelope to render correctly. T3 allows “exit 0 or 1,” T5b says canaries “may appear,” and T5–T12 omit expected exits. That fails the spec-note contract’s per-entry expected-exit and per-branch requirements (`spec-note-contract.md:86-98`).  
FIX: Add discriminating fixtures and exact text and exit expectations for every declared branch, including both redaction modes.

ID: P8  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/phase-ROF1-spec.md:11  
QUOTE: “Plan r1 §4 ROF1”  
PROBLEM: The reviewed plan is r2, and its D2 ruling to omit the empty temporal header is recorded at plan line 312, while the spec still marks D2 open at line 134. The spec does state that its bytes have not been reviewed; its provenance and decision table nevertheless no longer describe the current governing plan.  
FIX: Refresh the spec’s r2 provenance and carry the dated D2 ruling into its decision row before the owner gates the spec.

ID: P9  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:83  
QUOTE: “167 tracked files record at least one of 58 model digests … 306 load”  
PROBLEM: The 371 tracked `*.orm.yaml`/`*.orm.json` file count is reproducible from `git ls-files`. The plan supplies neither the census script nor the 306-model, 58-digest, and 167-file rosters, so those figures and ROF4-C3’s “all 167 … verify” gate cannot be independently checked from the plan. The stated 167 also includes historical `.gnd-planning` evidence, which is retained evidence rather than a verifier input.  
FIX: Commit the read-only census command and roster, then name executable compatibility gates by artifact class; retain historical files as byte-preservation checks.

ID: P10  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md:25  
QUOTE: “`gnd check`, `gnd validate`, … with `--format text` … rendered from the projected tree only”  
PROBLEM: `validate --trace` prints from the unprojected model before projected text (`commands/checking.py:109-111`, `output.py:37-109`). `validate --document` can return early and print `result.warnings` and newly built issues without the projected payload (`commands/checking.py:90-93,54-78`). The spec’s T8 source assertion checks only the projected branches, so it cannot establish this route-wide claim. This is a projection bypass found by reading, not a demonstrated secret leak.  
FIX: Define the boundary for trace and document output explicitly; route any covered text through a projected representation and add focused canary cases.

CONFIRMED:

- The ordinary model digest uses `repr`, while reference-bearing models use the version-1 canonical digest (`values.py:179-213`).
- Projection is selected for active redaction and for temporal check/transition/plan routes (`checking_service.py:645-650`); the current projected text renderer prints JSON (`output.py:113-132`).
- Codegen and conformance compare raw model-file bytes, a distinct digest contract (`codegen/manifest.py:257-259`, `conformance/currency.py:29-41`).
- Existing digest schema fields accept the same `sha256:<64 hex>` string shape, so accept-both alone does not require a new value pattern.

No test suite was run. The behavioral conclusions above are source-reading conclusions; the 306/273/58/167 census figures and runtime compatibility outcomes remain unverified.

codex exit=0
