You are the single adversarial reviewer for phase IL1 of the GND ilp-learners milestone, in the git worktree at
<repo> (branch claude/il1-learner-registry).

Review the implementation diff: `git diff 5576a4e ed54e65` (5576a4e is the owner-approved IL1 corpus, committed red; ed54e65 is the implementation including amendment IL1-A1). The phase began from 45c8603 on main.
The approved design is .gnd-planning/milestones/ilp-learners/notes/phase-IL1-spec.md: read §4-§8 and §13-§15 in full (§6 is the design, §14 and the end of §15 list the implementation's own findings IL1-F1..F9, §15 is the approved amendment IL1-A1).
The IL1 corpus is tests/fixtures/ilp_learners/il1/ (escapes.json, joins.json, stories inline) and tests/test_ilp_learners.py. The IK5 corpus whose goldens IL1-A1 moved is tests/fixtures/induced_knowledge/ik5-corpus/ with tests/test_ilp_bridge.py. The contract page is docs/reference/ilp-bridge.md.

What shipped:
- A learner registry, src/gnd/export/ilp_learners.py: one entry per --target (popper, neutral) with render, parse, the run record's learner name, the provenance method token, and a per-target adapter_version. ilp_service.py consults it and names no learner itself.
- Check 9b, type-confused-join, in src/gnd/export/ilp_rewrite.py: a named variable's sites (atom positions, and the declared type of a comparison predicate it is an operand of) must have pairwise-intersecting ancestor closures (gnd.export.ilp.type_closures, from ModelIndex.supertype_closure plus the type itself).
- SWI octal escapes \NNN\ in the Popper parser (ilp_popper._TOKEN, _unquote, _octal), and extract_program, which reads Popper v5.0.1's stderr log.
- Amendment IL1-A1, Popper adapter 2: bk.pl grouped by predicate; each comparison against an observed integer value is a unary threshold predicate gt_<type>__<v>(A) :- integer(A), A > v. (lt likewise, negative values spelled m<digits>); at most 32 thresholds per integer type by ranked selection (ilp_popper.thresholds); bias.pl lists them and no binary comparison or magic_value_type; the parser maps a one-argument threshold atom back to the declared binary comparison atom with the decoded constant.
- Evidence: .gnd-planning/milestones/ilp-learners/evidence/IL1/run_popper.py and live/invocation-1, invocation-2 (two real Popper runs; T9 replays both).

Hunt for real defects, especially:
1. Meaning preservation through the threshold mapping: can a Popper program be admitted whose guarded constraint means something different from what Popper's threshold predicate computed (operator direction, negation in the consequent, the m-prefix, leading zeros, the last-__ decoding, a type name containing __, ge/le names that were never rendered, a threshold atom whose comparison is not declared, a threshold name colliding with a fact predicate)? Does the rewrite still treat the mapped atom with the comparison's declared type, so check 9b and comparison-type apply?
2. Check 9b: can a type-confused join be admitted (supertypes, subtypes, value types, the comparison's declared type, anonymous _, a variable used only in comparisons), or a legitimate join refused? Is the check's work bounded?
3. Parser totality over hostile input: anything reaching a traceback (exit 1) instead of a named exit 3? Octal escapes of every length and value, surrogates, threshold names with huge digit strings, deep nesting, extract_program on adversarial logs (several banners, interleaved lines, prefixes).
4. Rendering fidelity and determinism: fact grouping order, threshold selection (rank formula, duplicates, extremes, negative values, booleans vs integers, empty types), byte identity under PYTHONHASHSEED, the adapter_version per target, schema validity of every written file.
5. The registry: is any learner name still hard-coded in the service? Do the CLI choices and the schema enums agree with the registry? Does a target that does not export or has no parser behave as declared?
6. Golden movement: IL1-A1 claims only the inventoried IK5 goldens moved and no exit or refusal changed. Check that claim against the diff.
7. The evidence script and the replay test T9: does T9 test anything that could fail? Is the recorded outcome consistent with the raw logs? Is any home path, user name or scratch path left in committed evidence?
8. Anything a test passes while the code is wrong: a declared branch with no case that can fail it.

Rules: reproduce each finding with a concrete command or script before reporting it, and include the reproduction. Do not edit any tracked file. Write any scratch files ONLY under
<scratch>/il1-review/ (create it), including any derived outputs (--out paths, temp corpora, copies of the source). Do not run the full test suite; targeted pytest runs are fine. Do not run Popper or install anything. Never execute or source a repository .env.

Report: a numbered list of findings, each with severity (blocking / hardening / completeness), the file:line, the reproduction and its observed output, and the expected behaviour. Then list what you checked that held. If you find nothing in an area, say what you tried.
