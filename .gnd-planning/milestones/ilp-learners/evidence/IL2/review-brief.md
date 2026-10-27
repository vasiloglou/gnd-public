You are the single adversarial reviewer for phase IL2 of the GND ilp-learners milestone, in the git worktree at
<repo> (branch claude/il2).

Review the phase diff: `git diff 65fd6df bf15642` (65fd6df is main after the IL1 merge; 7d7fc94 is the owner-approved IL2 corpus, committed red; e6af17a is the adapter; 4599b1d and bf15642 are the extractor fix, the live-run script and invocation 1).
The approved design is .gnd-planning/milestones/ilp-learners/notes/phase-IL2-spec.md: read §4-§8 and §12-§14 in full (§6 is the design, §8 the tests, §13 the gate record, §14 the implementation's own findings IL2-F1..F7, the IL2-D12 ruling and invocation 1). The owner ruled that invocation 1 is recorded as is, and that IL2-F7 (ILASP's lone-comparison rule, refused as empty-antecedent) is a recorded result, not a defect to report.
The IL2 corpus is tests/fixtures/ilp_learners/il2/ with tests/test_ilp_asp.py; the IL1 and IK5 tests are tests/test_ilp_learners.py and tests/test_ilp_bridge.py. The contract page is docs/reference/ilp-bridge.md.

What shipped:
- src/gnd/export/ilp_asp.py (new): render(neutral) writes ilasp/task.las (background: per integer type dom_/thr_/gt_/lt_ rules over ilp_popper.thresholds; #constant, #modeh(wrong), #modeb per predicate with the example argument dropped and per comparison, #maxv(4); one #pos/#neg example per labelled example with its context facts). extract_hypothesis reads ILASP's stdout. parse_hypothesis is a closed, capped reader of ASP rules back to gnd-ilp-clauses/1, with an 11-name refusal table and caps (32 rules, 16 literals, depth 4, 32-digit integers, 1 MiB).
- The registry entry ilasp in src/gnd/export/ilp_learners.py; the CLI choices; the two schema enums; tools/gnd_layers.json.
- IL2-D8 in src/gnd/export/ilp_popper.py: threshold names with leading zeros, m0 or m0-prefixed digits are unparsable.
- Moved RF1 CLI goldens (help, exit, tree.json) and the RF6 successor delta evidence/IL2/dynamic-query-successor.json.
- Evidence: .gnd-planning/milestones/ilp-learners/evidence/IL2/ (download.json, probe/, run_ilasp.py, live/invocation-1/); T9 replays invocation 1.

Hunt for real defects, especially:
1. Meaning preservation through the reader: can an ASP hypothesis be admitted whose GND clause means something different from what ILASP's rule means over the rendered task (variable threading of the example argument X and its freshness, comparison atoms copied with their argument order, gt/lt/ge/le names never rendered, constants: strings, negative integers, true/false versus the export's booleans, bare names versus quoted strings, anonymous variables, a rule head other than wrong, a body atom whose predicate or arity is not in the mode declarations)?
2. Reader totality over hostile input: anything reaching a traceback (exit 1) instead of a named exit 3? Escapes, unterminated strings and comments, deep nesting, cap boundaries (exactly at and one over), huge integers, empty input, CRLF, non-ASCII, extract_hypothesis on adversarial stdout (several %% blocks, UNSATISFIABLE text inside a rule, interleaved lines).
3. Rendering fidelity and determinism: escaping in _term (the export's strings with quotes, backslashes, newlines, other control characters), example ordering, fact sorting, thresholds for negative values and booleans, empty types, byte identity under PYTHONHASHSEED, the adapter_version, and whether the rendered task is valid ILASP input that means what the neutral export means (would clingo, over background plus a context, derive the same facts GND's import evaluates?).
4. The registry and surfaces: CLI choices, schema enums and the registry agree; the docs' refusal and constants tables match the code (T12 can fail?).
5. Golden movement: check that only the inventoried RF1 goldens moved and that tree.json changed only in the target actions; check that the RF6 delta is honest (rows added only for ilp_asp).
6. The evidence script and T9: does T9 test anything that could fail? Is outcome.json consistent with raw-stdout.txt, hypothesis.las, run.json and import-stderr.txt? Is the null process record accepted only under the IL2-F6 note? Does run_ilasp.py's environment split now keep PYTHONHOME away from the evaluator? Is any home path, user name or scratch path left in committed evidence?
7. Anything a test passes while the code is wrong: a declared branch (each refusal name, each constants row, each cap) with no case that can fail it.

Rules: reproduce each finding with a concrete command or script before reporting it, and include the reproduction. Do not edit any tracked file. Write any scratch files ONLY under
<scratch>/il2-review/ (create it), including any derived outputs (--out paths, temp corpora, copies of the source). Do not run the full test suite; targeted pytest runs are fine. Do not run ILASP, download or install anything. You may use the existing scratch clingo read-only: <scratch>/il1-live/venv/bin/python -m clingo (it exits 0; read its --outf=2 JSON Result). Never execute or source a repository .env.

Report: a numbered list of findings, each with severity (blocking / hardening / completeness), the file:line, the reproduction and its observed output, and the expected behaviour. Then list what you checked that held. If you find nothing in an area, say what you tried.
