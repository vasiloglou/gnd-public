# Phase RN0 diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool (the shared default for a phase diff). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: gpt-6.1-sol (the tool's configured default).
- Reviewed bytes: `git diff 2490dd77 2a9bd6b8 -- src tests tools dev .gnd-planning/milestones/release-0.3.0/evidence/RN0`, with the approved spec.
- What the reviewer could not do: write files, run the full or default-lane suite or an installed wheel, or run the external Ossie oracle (its own list at the end).
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: K1
SEVERITY: high
LOCATION: src/gnd/disclosure.py:117
QUOTE: **_rows("value-free", ["gnd export ossie", "gnd import ossie"],
            note="model structure only; a model with populations is refused"),
PROBLEM: C4 is false. These rows classify existing value-bearing behavior as value-free.

Export evidence:
- In customer mode, exporting .gnd-planning/milestones/ossie-interchange/evidence/OS2/corpus-r2/model.orm.json with strict=True succeeded. The ontology contained “Category == 'Retail' OR Category == 'Business'”; the sidecar retained {"kind":"literal","value":100}.
- src/gnd/export/ossie_formulas.py:158 embeds allowed values in formulas. src/gnd/export/ossie.py:402 retains other source literals; line 295 copies description summaries.
- A validated synthetic model declaring redact:true still emitted PRIVATE-ENUM in its sidecar and PRIVATE-DESCRIPTION in its ontology. An in-memory CLI probe, mocking filesystem seams, returned EXPORT rc 0 under --disclosure customer.

Import evidence:
- A valid bound sidecar containing sample_population:[{"a":"PRIVATE-SAMPLE"}], with matching document hash and model identity, was accepted without a loss report. The same customer-mode CLI probe returned IMPORT rc 0 and retained PRIVATE-SAMPLE, PRIVATE-ENUM and PRIVATE-DESCRIPTION in the restored model.
- src/gnd/ossie_import.py:281 restores literal entries; lines 675–678 restore and validate the complete model without disclosure projection.

The population-refusal note is also inaccurate: src/gnd/export/ossie.py:373–389 marks nonempty sample_population and reference_populations fields refused, but line 418 aborts only when strict=True. Default export succeeds. The loss report records dispositions; it does not sanitize the ontology or sidecar.

FIX: Classify both commands as every-mode, document their value-bearing artifacts, and add payload-level regression coverage. This preserves the phase’s required Ossie behavior.

ID: K2
SEVERITY: low
LOCATION: .gnd-planning/milestones/release-0.3.0/evidence/RN0/query-successor.json:5
QUOTE: The exporter's thirteen direct reads from PR 160 are removed: it reads fact types and roles through ModelIndex.
PROBLEM: The C5 provenance reason misattributes the reduction. Running tests/test_rf6_query_policy.py’s reads scanner over git-show sources produced:

2490dd77: export/ossie.py=8, export/ossie_formulas.py=1, ossie_import.py=5
2a9bd6b8: export/ossie.py=0, export/ossie_formulas.py=0, ossie_import.py=1

The exporter removed nine occurrences. Consolidating five foreign-document reads into one accounts for the other four. The recorded counts are correct; the explanation is false.
FIX: State that nine exporter reads were replaced through ModelIndex and five importer reads were consolidated into one accessor.

Checked and found true

- All three successor files authenticate their recorded predecessors.
- All five command-body before-digests chain correctly; their after raw and algorithm digests match. git log -L and git show support the named historical changes.
- Both query budgets remain unchanged and full: 365 and 310. Query, dynamic-inventory, entry-point, routing, skill-link and identity mutation controls rejected their tested violations.
- The six entry-point exceptions match actual imports. Runtime layering and zero-allowance checks passed.
- The skill-link addition, VENDORED_SCHEMAS addition and updated count assertions match the current tree.
- The three packaged schemas decode identically through json.loads and input_policy.loads.
- Old/new exports matched in 164 census comparisons, including 28 refusals. Tested imports matched with and without sidecars.
- Duplicate, missing and non-string role names, and malformed uniqueness roles, were rejected before the rewritten exporter code.
- No version, dependency-lock or release-workflow change appeared. The repository remained unchanged.

Could not check

- Universal C1/C2 equivalence: finite comparisons cannot establish it; no command-level counterexample was found.
- Full pytest/default-lane and installed-wheel runs requiring filesystem writes: excluded by the read-only constraint.
- External Ossie oracle: GND_OSSIE_ORACLE_ROOT is unset.
codex exit 0
