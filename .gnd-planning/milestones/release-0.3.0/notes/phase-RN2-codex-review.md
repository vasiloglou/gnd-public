# Phase RN2 part-one diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool (the shared default for a phase diff). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: gpt-6.1-sol (the tool's configured default).
- Reviewed bytes: `git diff f9f502d9 b8afdaa6 -- tests`, with the approved spec.
- What the reviewer could not do: write files, run the installed-wheel tests or the Ubuntu workflow, or reach PyPI (its own list at the end).
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: G1
SEVERITY: medium
LOCATION: tests/test_release_acceptance.py:570
QUOTE: assert [i['cell'] for i in violating['policy_issues']] == ['constraint.populated.add']
PROBLEM: T1’s violating-population row requires operation 0 to be a policy issue. Its operation_index is never checked. I evaluated these assertions with operation_index set to 99; they passed. C1 is false for this field.
FIX: Assert [(i['operation_index'], i['cell']) for i in violating['policy_issues']] == [(0, 'constraint.populated.add')].

ID: G2
SEVERITY: medium
LOCATION: tests/test_release_acceptance.py:528
QUOTE: concepts = json.loads((q1 / 'as-json/o.json').read_text(encoding='utf-8'))['ontology']
PROBLEM: T1 requires refund_by with ManyToOne in the ontology produced by the YAML export command. The assertion examines a separate JSON export. A YAML renderer that omits or changes multiplicity can pass: the JSON renderer remains correct, and sidecar literals retain the original uniqueness constraint for restoration.
FIX: Parse o.yaml independently and assert its refund_by multiplicity.

ID: G3
SEVERITY: medium
LOCATION: tests/test_release_acceptance.py:535
QUOTE: assert (q1 / 'restored.orm.json').is_file()
PROBLEM: Q1 never validates the restored file or measures its identity. An importer that correctly checks binding and prepares the report, but writes corrupt or incomplete model bytes, passes these assertions. source_identity_verified is trusted from the implementation being tested. The changed-ontology control does not catch this failure.
FIX: Validate restored.orm.json with --identity and assert its identity equals the original model’s identity.

ID: G4
SEVERITY: medium
LOCATION: tests/test_release_acceptance.py:502
QUOTE: assert match.group(1) == 'sha256:' + hashlib.sha256((second + '\n').encode('utf-8')).hexdigest()
PROBLEM: This proves consistency with the printed document, not that the document represents the complete model required by representation-format.md:895–900. I exercised an in-memory shared identity implementation that serializes only object-type names. It passed the hash, rename and export-identity comparisons, while changing the refund limit from 1000 to 5 left the identity unchanged. C2’s identity behavior claim is therefore too strong.
FIX: Assert an independently established canonical document or digest for the fixed refunds input. Also mutate a constraint and require the identity to change.

ID: G5
SEVERITY: medium
LOCATION: tests/test_release_acceptance.py:472
QUOTE: run(['uv', 'pip', 'install', '--python', venv / 'bin/python', wheel], outside, env)
PROBLEM: C6’s network restriction is false. Installing this local wheel also resolves and obtains its dependencies from the index. The retained, correctly hashed 0.2.0 wheel requires jsonschema, pydantic and ruamel-yaml; their transitive requirements include open ranges such as attrs>=22.2.0 and referencing>=0.28.4. This command neither uses uv.lock nor enforces offline installation. Results can depend on additional network requests and later dependency releases.
FIX: Supply pinned, hash-verified dependency artifacts locally and enforce offline installation, or narrow C6 to acknowledge this existing installation dependency.

ID: G6
SEVERITY: low
LOCATION: tests/test_release_acceptance.py:605
QUOTE: assert any(i['path'] == '$.version' and '5 is not one of' in i['message'] for i in refused['issues']), refused['issues']
PROBLEM: T2 specifies “5 is not one of [1, 2, 3, 4]”. This assertion does not check the supported-version list. I evaluated it with “5 is not one of [1]”; it passed. It is weaker than its table row, although the pinned control wheel limits practical drift.
FIX: Assert the complete expected message at $.version.

ID: G7
SEVERITY: low
LOCATION: tests/test_release_acceptance.py:534
QUOTE: assert report['schema'] == 'gnd-ossie-import-loss/1' and report['source_identity_verified'] is True
PROBLEM: C3’s independent-source claim does not hold for every literal. Neither gnd-ossie-import-loss/1 nor ossie-import:binding, asserted at line 541, appears in the five named sources. The representation reference describes identity verification and generic ossie-import:<rule> refusals, but does not specify these exact literals. The import schema literal appears in the implementation itself at src/gnd/ossie_import.py:631. I found no disagreement with the implementation; the missing piece is independent provenance.
FIX: Cite an independent contract defining these literals, or add their definitions to the normative reference.

Checked and found true

- Every T1 and T2 row has some assertion coverage; the weaknesses found are identified above.
- Q1’s binding control catches an importer that ignores the ontology-byte binding: it requires exit 3, the binding diagnostic, and absence of both requested outputs.
- Q2 catches a constant identity that ignores all model changes: the renamed type must change the digest. G4 identifies the narrower implementation that escapes.
- Q3 catches a loader that skips hash verification: the zeroed pin must produce exactly include:hash-mismatch at $.includes[0].
- Q4 catches a population checker that admits everything: the violating population must exit 3 with no admitted operation. Clean admission and flag-free refusal are also asserted.
- Q5 catches a span checker that never counts: the missing annex must produce the specified warning or error, while complete coverage must produce neither.
- The asserted UG2 C01/C03 outcomes and UG3 A2a/A3/A4 values agree with their answer keys. ManyToOne and the artifact filenames agree with the Ossie guide. The identity hashing relation, include refusal, span behavior and additive-policy behavior agree with their references.
- All eight README digests are correct. All six directly copied files equal their named origins. The verbalization equals “pre-existing\n”.
- I ran C01’s _workspace with filesystem writes intercepted in memory. Its proposal.json and verbalization bytes exactly match the committed fixtures.
- The locally retained 0.2.0 wheel matches the newly recorded SHA-256.
- New candidate commands use the installed interpreter, -I and sandbox prefix. Historical commands use the separate published-wheel interpreter with that prefix. Packaged examples come through importlib.resources; corpus inputs come from tracked fixture copies. The version assertion additionally reads the archived pyproject.toml.
- Fresh per-test directories and unchanged module-fixture environments provide no apparent wheel-order or leftover-output dependency.
- Existing acceptance code changed only through the dictionary addition. release.yml and test_release_preparation.py are untouched; the prepare job still invokes this acceptance file.
- The file parses under Python 3.11.15. No new Ubuntu-specific failure was found by inspection: sandbox-exec is selected only on macOS.

Could not check

- Full installed-wheel execution, reversed parameter order, or the Ubuntu workflow: these require filesystem writes unavailable in this read-only review.
- Actual on-disk _workspace execution: writes were intercepted; its proposal construction and serialization did execute.
- Current PyPI availability and served bytes: no live download was performed; the retained wheel’s hash was verified.
- Filesystem-level checkout denial on Ubuntu: the existing fixture supplies no Linux sandbox. Its interpreter and environment isolation do not prohibit arbitrary filesystem reads.
codex exit 0
