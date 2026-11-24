<!-- Edited by review_tool.py sanitize: 4 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
The grading totals reproduce, but the evidence has three issues requiring correction.

1. **F1 — Blindness was not enforced.** [phase-PF2-spec.md:86](<repo>/.gnd-planning/milestones/pins-and-review-check/notes/phase-PF2-spec.md:86) describes the scratch-clone arrangement as keeping the key and counterpart versions from reviewers. From the surviving `change-a` worktree, I successfully ran:
   
   ```sh
   git show change-c:tools/skill_names.py
   shasum -a 256 ../../../held/key/branch-map.json
   ```
   
   The first exposes the counterpart implementation; the second reaches the answer key and matches its committed digest. Thus reviewers could discover assignments despite neutral briefs. This does **not** establish that they accessed them. Qualify the blindness claim and include both access routes in the limits.

2. **F2 — E5 did not rerun every reported input.** [GRADING.md:3](<repo>/.gnd-planning/milestones/pins-and-review-check/evidence/PF2/GRADING.md:3) claims complete coverage, but [grade.py:32](<repo>/.gnd-planning/milestones/pins-and-review-check/evidence/PF2/grade.py:32) omits reported cases, including indented frontmatter, absent frontmatter, body horizontal rules, quoted TOML keys, Unicode escapes, and several path variants. For example, the reported input `---\n  name: demo\n---\n` returns `None` rather than `"demo"` in `change-a`; my in-memory replay confirmed it, but no retained E5 row covers it. Complete the missing reproductions and dispositions. The omissions do not overturn the four “found” grades, which already have reproducing inputs.

3. **F3 — The retained checksum command fails.** [KEY-SHA256SUMS:4](<repo>/.gnd-planning/milestones/pins-and-review-check/evidence/PF2/KEY-SHA256SUMS:4) names `gen/make_corpus.py` and `gen/run_key.py`, while both scripts were retained at the evidence root. Running `shasum -a 256 -c KEY-SHA256SUMS` there exits **1**, reporting two missing files. Their bytes match after manually translating the paths, so the digest commitment holds; the advertised verification procedure does not. Preserve the committed manifest and document the relocation or restore its directory layout.

What I checked and found true:

- All **67** brief-listed hashes match.
- All **32 grading rows** and **24 answer-key rows** reproduce in memory, including with the scratch clone’s readers.
- The grades follow §6: **four planted found, zero missed; two true control findings, zero false findings**.
- All five digest values in `36ca151e` match the retained bytes after accounting for the script relocation. Recorded review starts follow that commit.
- Briefs have the same neutral question, empty claims and notes, and no explicit planted/control labels. Names, docstrings and tests match within each pair.
- The stated sample-size, author-bias and nondeterminism limits are appropriate.

For the standing matcher check, I exercised:

- K1’s section splits and `_ID` regex with flow YAML, indentless sequences, quoted IDs and reordered sections.
- K2’s delimiter/index, `startswith` and colon split with indented mappings, quoted names containing colons, missing frontmatter and body rules.
- K3’s positional indexing, literal-parent branch and `relative_to(...).parts[0]` with nested/repeated directories and `..`.
- K4’s `_VERSION` regex with quoted keys, Unicode escapes and multiline descriptions.

These reproduce the known corpus defects. The scripts’ fixed-label splits and explicit fixture substitutions yielded no additional finding.

I could not establish whether reviewers actually accessed the key or counterparts, or reconstruct their exact historical filesystem permissions. I did not rerun full suites or execute scripts that write files. No files were changed.

VERDICT: CHANGES_REQUESTED