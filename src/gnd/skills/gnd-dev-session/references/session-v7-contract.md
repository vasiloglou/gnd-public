# Session contract version 7

Version 7 uses a separately dispatched closed reader. Versions 1–6 retain their
original fields and meanings. A trusted declared adapter policy is required.

An optional `candidate_edits` object declares `patch_path` and `artifacts`.
Each artifact declares a relative `path` and `collections`; each collection
names a literal `path` selector and scalar `key` fields. Only these artifacts
may change. Models, contract inputs, references and undeclared candidate files
remain protected. No shell command or inferred selector is a patch operation.

A patch has exactly `schema_version: 1`, `base_candidate_sha256` and
`operations`. `upsert` and `delete` name an artifact, collection and typed key;
`upsert` also supplies the row value. `replace-artifact` supplies the complete
artifact value. A null base is allowed only for the first complete seed of all
declared artifacts. Later proposals bind the exact preceding candidate tree.
No operations and equal upserts preserve bytes; changed JSON artifacts use
canonical bytes. Numbers compare mathematically, while bool, string and number
keys remain distinct. Duplicate operations and missing deletes refuse.

Optional `ranking` lists up to five distinct metric/direction objects. Metrics
are `accepted_required_cases`, `candidate_admitted_unique`, `alethic_failures`,
`alethic_indeterminate` and `coverage_shortfall`; direction is `min` or `max`.
Unavailable observations sort after available ones. Unique admission excludes
opaque facts and fixed references; duplicate occurrences cannot inflate it.
Ranking selects retained best evidence and never changes acceptance or floors.

Constraints may annotate `owner` as `candidate`, `reference` or `host`, and
`allowed_fixes` with `add-fact`, `replace-fact`, `delete-fact` or
`replace-artifact`. These annotations describe repair responsibility, not a new
domain rule. Missing owner means candidate. Operator feedback retains the
redacted findings; candidate feedback removes reference/host constraint
findings after mechanical evaluation. Neither stream executes fixes.

Version 7 emits feedback 8, attempt 9, result 6 and declared launch 3. Retained
proposal, original verifier transport, both feedback streams and the immutable
candidate inventory are digest-bound. Retry stdin receives the exact candidate
feedback bytes. Reconstruction rechecks bindings and semantic admission before
recomputing rank. Partial staging or a launch without its attempt refuses resume.

Patch input and reports are bounded to 10 MiB, candidates to 100 MiB and 10,000
files. A proposal permits at most 1,024 operations, 256 artifacts, 256
collections total, 16 selector segments and eight key fields. Collections
visit at most 100,000 rows; admission propagation permits one million cells.
These limits establish bounded selected work, not general throughput or
constraint completeness. A session outcome, verifier result and experiment
closure remain separate claims.

For explicitly selected saved opinion gates, see the [version-8 judgment contract](judgment-contract.md); version 7 remains frozen.

Selected reference wrappers retain the producer's copied command, outcome and
exit code. Transport validation checks structure/version, then model/reference
binding, then equality with the nested report before session evaluation or
admission. Matching fields do not establish inner semantic validity or process
exit agreement. Contradictory wrappers refuse; legitimate semantic failures
remain valid transports. Public diff reports have no copied nested status and
retain their independent outer status. No schema or supported exit band changes.

Constraint owner annotations declare repair responsibility, not the physical
origin of all participating facts. Missing owner defaults to candidate only for
constraint findings. Candidate feedback removes reference/host constraint rows
recursively; operator feedback retains them, subject to upstream role redaction.
Format issues remain unowned diagnostics in both views; runtime feedback retains
status without raw exception details. Failed protected reference binding refuses
before either view is constructed. Saved judgment summaries use their existing
same redacted policy view for both audiences, without inferring constraint owner.
Descriptive allowed_fixes never authorizes edits outside declared candidate files.
