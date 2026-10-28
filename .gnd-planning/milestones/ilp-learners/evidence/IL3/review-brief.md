You are the single adversarial reviewer for phase IL3 of the GND ilp-learners milestone, in the git worktree at
<repo> (branch claude/il3).

Review the phase diff: `git diff e30eec8 620f394` (e30eec8 is main after PR #59; 2a3d859 the draft spec; 532859b the owner gate record; 43cf428 the corpus and the tests, committed red; aa823a7 the implementation; 620f394 the live-run scripts, the probe and invocation 1).
The approved design is .gnd-planning/milestones/ilp-learners/notes/phase-IL3-spec.md: read it in full (§6 the design, §7 the decisions, §13 the owner rulings, §14 the implementation findings IL3-F1..F5, including the owner ruling on IL3-F2 that column names carry the arity). Invocation 1 is the run of record and is retained as is; IL3-F5 (RIPPER is not deterministic under random_state=0, and the disclosed diagnostic re-runs) is a recorded finding, not one to report again, though you may report consequences the author missed.
The corpus is tests/fixtures/ilp_learners/il3/ with tests/test_ilp_rules.py. The contract page is docs/reference/ilp-bridge.md ("## Boolean rule sets").

What shipped:
- src/gnd/export/ilp_rules.py (new): render(neutral) writes rules/features.json (gnd-ilp-features/1), one 0/1 column per (integer argument position, Popper threshold row), named <predicate>__<position>__<arity>__<comparison>__<threshold>; parse_ruleset(text) reads wittgenstein's printed rule set through the polarity table; extract_ruleset(stdout) is the shared extractor.
- src/gnd/ilp-features.schema.json (new); the registry entry rules (learner wittgenstein, method ilp-rules); the CLI choices; both target enums; tools/gnd_layers.json; the schema inventories; the RF6 dynamic-census delta evidence/IL3/dynamic-query-successor.json.
- Moved RF1 CLI goldens: gnd export ilp's help and exit goldens now per Python version, gnd import ilp-rules's, cli/tree.json, goldens.sha256 and MANIFEST_SHA256.
- Evidence: evidence/live_common.py (shared helper), evidence/IL3/ (learn_rules.py the driver, run_rules.py the script, probe/, live/invocation-1/, downloads.json, sdist-members.txt).

Hunt for real defects, especially:
1. The reader's totality and grammar: can parse_ruleset raise anything but IlpError, loop, or accept text outside the §6 grammar (whitespace, unicode digits, a column name the renderer cannot write, a name that parses two ways because predicate or type names contain double underscores)? Do the caps hold at exactly the bound and one over?
2. The polarity table: is each row reached in the stated order, and can any spelling map to the wrong polarity (for example =1.0 versus =10, >0.5 versus >0.50, a value followed by another character)?
3. Column names: does every name the renderer writes read back as the same feature (the round-trip check), including negative thresholds, multi-digit positions and arities, and names near the 160-character cap? Can the renderer write a name the reader refuses?
4. The feature table: is every cell the existential the spec defines, for every integer position, including booleans (excluded as integers) and predicates with several integer positions? Byte identity under two hash seeds; the bounds at exactly and one over; no-features.
5. Binding and admission: can a rule set be admitted against another export, with another learner name, or partially (IL-R11)? Does the import's coverage re-check compare the learner's per-rule sets with GND's?
6. Surfaces and goldens: registry, choices, enums, schema inventories and docs agree; only the listed RF1 goldens moved, and the manifest matches; the RF6 delta is honest (no direct-read policy widening).
7. The evidence: is outcome.json consistent with raw-stdout.txt, ruleset.txt, run.json, import-report.json and proposal.json? Does the coverage come from the learner, not GND (IL-R4)? Is any home path, user name, email or scratch path left in committed evidence? Is live_common.py's sanitizer and termination mapping the ruled one? Does T9 test anything that could fail?
8. Anything a test passes while the code is wrong: a declared branch with no case that can fail it.

Rules: reproduce each finding with a concrete command or script before reporting it, and include the reproduction. Do not edit any tracked file. Write any scratch files ONLY under
<scratch>/il3-review/ (it exists), including any derived outputs (--out paths, temp corpora, copies of the source). Do not run the full test suite; targeted pytest runs are fine. Do not run run_rules.py or learn_rules.py, and do not run the learner in any way (another run needs an owner ruling). Do not invoke any agent CLI. Do not download or install anything. Never execute or source a repository .env.

Report: a numbered list of findings, each with severity (blocking / hardening / completeness), the file:line, the reproduction and its observed output, and the expected behaviour. Then list what you checked that held. If you find nothing in an area, say what you tried.
