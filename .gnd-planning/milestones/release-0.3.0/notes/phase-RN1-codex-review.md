# Phase RN1 diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool (the shared default for a phase diff). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: gpt-6.1-sol (the tool's configured default).
- Reviewed bytes: `git diff d7317d25 73884f6c`, everything outside `.gnd-planning/`, with the approved spec, the moved-digest list and the re-record script.
- What the reviewer could not do: write files, regenerate the digest-only outputs, run the pytest lanes, or audit actions outside this checkout (its own list at the end).
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: F1
SEVERITY: medium
LOCATION: docs/release-notes.md:27
QUOTE: With the sidecar beside an unchanged ontology, the original model is restored and the report says whether its identity matched.
PROBLEM: An unchanged bundle does not necessarily restore the original model. I exported src/gnd/examples/growth/model.orm.yaml and passed its three artifacts directly to plan_ossie_import through an in-memory reader. Output: “original==restored: False”, “sample rows: 2 -> 0”, “identity_verified: False”. The dispatch example likewise loses reference_populations. src/gnd/export/ossie.py:373 omits population subtrees; src/gnd/ossie_import.py:677 permits import when those omissions explain the mismatch. The normative representation-format.md:1906 explicitly says “Exported omissions remain omissions on import.”
FIX: Say that import restores the retained model content, and that omitted sample and reference populations remain omitted.

ID: F2
SEVERITY: medium
LOCATION: docs/release-notes.md:44
QUOTE: ### Shared definitions, project-owned policies (issue 95)
PROBLEM: This block omits the new model format and its reader incompatibilities. src/gnd/schema/orm-meta.schema.json:18 adds version 5; includes and fact_type_constraints are new fields. I validated the shipped sales.orm.json against the schema from v0.2.0: it rejects version 5 and both fields. Include-aware evolution also adds repin-include and before_includes/candidate_includes; older readers refuse these artifacts. Those incompatibilities are documented in evolution-contract.md:621 and :642 but never flagged in the release notes. The new --previous-include option is also unnamed.
FIX: Add a short format/compatibility paragraph naming version 5, include evolution artifacts, their incompatibility with 0.2.0 readers, and --previous-include.

ID: F3
SEVERITY: medium
LOCATION: docs/release-notes.md:88
QUOTE: ### Constraints admitted on clean data (issue 104)
PROBLEM: The notes describe relaxed admission with --check-population but omit a tightening that also affects invocations without that flag. ConstraintSubjects.of now follows references beyond an inline constraint’s host (src/gnd/evolve/policy.py:344). Using the valid base model in tests/fixtures/unattended-model-growth/ug2/base.orm.yaml, I added a proposed/deontic object-scoped value constraint on order to the empty order_has_memo host, with customer_places_order marked populated. Running the policy implementation from v0.2.0 returned []; the current implementation returned ['constraint.populated.add']. Both models validated. tests/test_evolve_population_check.py:774 independently identifies this flag-free regression case.
FIX: Note that inline constraints now count every fact type they reach, so some previously admitted additive proposals are refused.

ID: F4
SEVERITY: medium
LOCATION: docs/release-notes.md:47
QUOTE: Validation, checking and model verbalization use the composed model; evolution can review a vocabulary update and repair project rules in one accepted change.
PROBLEM: The generic reference to verbalization does not announce the new public command or API. src/gnd/commands/checking.py:985 adds “gnd verbalize model MODEL”; src/gnd/api.py:1012 adds verbalize_model(). Neither name appears in the release notes. Their disclosure behavior also matters: they render the complete model, including authored samples, in every mode (src/gnd/disclosure.py:107 and :129; docs/reference/disclosure.md:126).
FIX: Add one bullet naming both entry points and their complete-model disclosure behavior.

ID: F5
SEVERITY: low
LOCATION: docs/release-notes.md:116
QUOTE: ### A growth round can declare its source document (issues 74 and 104)
PROBLEM: C5 also requires coverage of packaged skill changes. The new “Acting on a shape match” procedure is unnoted. unattended-growth.md:63 now requires the host to choose and log reuse, retention with provenance.rationale, or retention with an open question. Previously the skill left semantic matching to the host without this procedure. The source-document, population-check and span-count notes do not describe this change.
FIX: Add a sentence announcing the packaged unattended workflow’s required handling of shape matches.

ID: F6
SEVERITY: low
LOCATION: tests/test_release_version.py:270
QUOTE: assert f"]({link})" in section, f"the {version} notes do not link {link}"
PROBLEM: The helper searches the entire version section, rather than the headline block required by T9. I supplied the correct first heading, an Ossie block with no link, and a later “### Fixes” block containing [x](explanation/ossie.md). assert_notes_name_the_headline_change accepted it.
FIX: Search for the link between the headline heading and the next subsection, and add this misplaced-link mutant.

ID: F7
SEVERITY: low
LOCATION: tests/test_release_version.py:277
QUOTE: assert re.search(rf"\b{re.escape(declared)}\b[^|\n]*\|[^|\n]*[Nn]o profile is observed", support), (
PROBLEM: The page check accepts incorrect status statements. With declared=0.3.0, it accepted “| prepared 0.3.0 | no profile is observed for 0.2.0 |”. It also accepted the actual plugin page with “Version 0.3.0 is published on PyPI.” appended. The latter escapes existing publication checks because read_other_pages at tests/test_release_version.py:110 excludes docs/marketplace-plugins.md.
FIX: Require the observation clause to name the declared version. Include the plugin page in publication-claim scanning, with negative tests for both mutants.

Checked and found true

- C1: all five version declarations are 0.3.0; uv.lock has exactly the editable-entry version change.
- All 30 old/new file hashes match moved-digests.md.
- Independently decompressed all seven containers. Shapes and member sets match; changed payload content is limited to version values and digest references. Member hashes and RF1 manifest entries verify. Historical members remain unchanged.
- The eight re-recorded test files differ only in sha256 literals.
- README/docs install pins remain 0.2.0; current pages contain no affirmative package-publication claim for 0.3.0.
- The remaining Ossie filename, flag, offline-registry, pinned-commit, scope and disclosure descriptions match the inspected code. Both vendored schema hashes match PINNED.json.
- The four new fixes correspond to the cited commits and packaged role-name changes.
- The new checks reject missing headline, support and repository-route inputs. Existing guards reject a 0.3.0 install pin and scanned “0.3.0 is published” statements. Twenty-six filesystem-free release-test cases passed.
- Both paragraph splits preserve the exact whitespace-separated word sequence.
- Both snapshot digests and original-document link bases check correctly; changed-snapshot and missing-target mutants fail.
- .github/ is unchanged. No local tag names 0.3.0. The working tree remains unchanged.

Could not check

- Independently regenerate digest-only synthesis, measurement and command outputs: their capture workflows write files, prohibited by the read-only environment. Structural/hash checks do not establish every generated digest’s causal provenance.
- Full pytest lanes and fixture regeneration were not run because they require filesystem writes.
- C8’s absolute historical assertion that nothing was built, uploaded or tagged elsewhere cannot be established from this checkout. Local diffs and tags do not audit external actions. The dated package-index availability observation was not independently verified.
codex exit 0
