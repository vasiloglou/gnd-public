You are the single adversarial reviewer for phase IK5 of the GND induced-knowledge milestone, in the git worktree at
/Users/nikolaosvasiloglou/github-repos/gnd-public/.claude/worktrees/recent-commits-95fa1c (branch claude/ik5-ilp-bridge).

Review the implementation diff: `git diff d0cb831 abc872a` (d0cb831 is the owner-approved corpus commit; abc872a is the implementation).
The approved design is .gnd-planning/milestones/induced-knowledge/notes/phase-IK5-spec.md (read §3-§8 and §13-§16 in full; §6 is the design, §16 lists the implementation's own findings).
The approved corpus is tests/fixtures/induced_knowledge/ik5-corpus/ (README.md tells the stories, expected.json and expected-export/ hold the answers) and tests/test_ilp_bridge.py.
The contract page is docs/reference/ilp-bridge.md.

What shipped: an ILP bridge.
- `gnd export ilp MODEL --labels MANIFEST --target popper|neutral --out DIR` writes a learner-neutral form (gnd-ilp/1) from a model plus a class-mode IK3 label manifest, the Popper rendering, and export.json whose SHA-256 is the export digest E.
- `gnd import ilp-rules MODEL CLAUSES --labels MANIFEST --reported-coverage RUN --target popper|neutral --out PROPOSAL` parses learned clauses, refuses anything outside a declared fragment by name, rewrites each clause wrong(X) :- B1..Bn into one guarded constraint (induced/proposed/deontic), re-runs the checker per population, and writes an evolve proposal only if each clause's covered example-id set equals the run record's.
- Code: src/gnd/export/ilp.py, ilp_popper.py, ilp_rewrite.py, ilp_service.py; four schemas src/gnd/ilp*.schema.json; CLI in src/gnd/commands/export.py and commands/checking.py; shared refactors in src/gnd/measure/labels.py (read_population) and src/gnd/discover/output.py (add_operations, proposal keywords).

Hunt for real defects, especially:
1. Meaning preservation (the milestone's central risk): can a clause be admitted whose guarded constraint means something different from the learned clause, while the coverage sets still agree on the corpus? Think about variable spelling collisions, repeated variables inside one atom, constants vs variables, the `$` spelling rule, anonymous `_`, boolean/integer/string typing, negative integers, the designation rule, comparison orientation and negation (e.g. constant on the left), `=` vs `!=`, and comparison predicates written as atoms vs infix.
2. The set comparison and binding checks: can a mismatched learner report be admitted? Can E, the clause digest or the learner binding be satisfied by bytes other than the ones re-checked? Does the import really recompute E from the same inputs the learner saw? Duplicate manifest entries pointing at the same file; ids repeated in reported sets.
3. Parser and loader totality over hostile input: anything reaching a traceback (exit 1) instead of a named exit 3/66/74? Try odd Unicode, escapes, deeply nested parens/not/or/aggregates in both forms, huge integers, empty files, BOMs, a CLAUSES that is a directory or FIFO, symlinked inputs, very long lines.
4. Export fidelity and determinism: facts order, Prolog quoting/escaping (could a value break out of a quoted atom or the fact syntax?), duplicate facts, entity vs value typing, PYTHONHASHSEED independence, schema validity of every written file, the redaction refusal (can a redacted value still reach the output?).
5. Synth/IK3/IK4 regressions from the shared refactors (labels.read_population, discover.output.add_operations / proposal): byte-identical behaviour for gnd measure --labels and gnd discover.
6. Work counters and bounds vs spec §6 (IK5-D14); the ceiling claims; anything the corpus could pass while being wrong (a declared branch with no case that can fail it).

Rules: reproduce each finding with a concrete command or script before reporting it, and include the reproduction. Do not edit any tracked file. Write any scratch files ONLY under
/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public--claude-worktrees-recent-commits-95fa1c/16650214-feb5-484f-a716-975b7f732cdd/scratchpad/ik5-review/ (create it), including any derived outputs (--out paths, temp corpora, copies of the source). Do not run the full test suite; targeted pytest runs are fine. Never execute or source a repository .env.

Report: a numbered list of findings, each with severity (blocking / hardening / completeness), the file:line, the reproduction and its observed output, and the expected behaviour. Then list what you checked that held. If you find nothing in an area, say what you tried.
