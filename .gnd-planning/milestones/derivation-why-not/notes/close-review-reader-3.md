# Close review, reader 3: protocol, compatibility and anonymity

Retained text of the reader's returned report (one of four local close
readers, WN-D8). Local edits: scratch paths read `<scratch>`.

**Scope:** `fb03739..ae08200`, which is 5 commits and 160 files. I read the milestone records, specs, gate sections and commit messages. I ran `tests/test_why_not_anonymity.py`, which gave 2 passed, and `test_il6_skill_census.py`, `test_skill_prose_sync.py` and `test_packaged_skills.py` at HEAD, which gave 68 passed. Probe scripts are under `<scratch>/close-r3/`. I made no repository writes.

**Verdict:** I found nothing that blocks the close. There are six hardening and completeness findings, mostly about the commit and record protocol.

## Claims checked and found true
- **Corpus first (WN-D10):** `f456930` is an ancestor of `b1d017d`. It holds no service, view or CLI code: `service.py` has 0 `why_not` mentions at that commit. It contains the WN2 spec with its gate section, the schema, the goldens and the test.
  - After the red commit, goldens g1–g13 are byte-unchanged and `cases.json` only gained entries. G14–G18 were added later as successors, and the WN2 record says so (R3).
- **Delegated gates:** each delegated gate is labelled "delegated approval (auto=true)" and is stated not to be the owner's own reading. These are the WN1 section at `notes/phase-WN1-spec.md:384`, the WN2 section at `notes/phase-WN2-spec.md`, and the WN3 section at `notes/phase-WN3-spec.md:142`.
- **Approved bytes:** each digest matches the spec bytes above its gate section exactly:
  - WN1 `78fbfe88…3977`
  - WN2 `8665b031…9e27`
  - WN3 `df9e3342…3ede5`
  - The plan still hashes to `fb590faa…441d`, its approved value.
- **Append-only records:**
  - The plan, `001-plan-gate.md` and `002-phase-WN1.md` were not edited after their commits.
  - The WN1 spec's change in `26e36c8` is pure appends (0 removed lines).
  - The WN2 spec was not touched after `f456930`.
  - Only README navigation changed.
- **Evidence digests:** every frontmatter digest in records 002–004 matches current bytes, with one exception (C3-4).
- **Commit messages:** none of the five contains backticks or em/en dashes, and all carry the Co-Authored-By trailer.
- **Compatibility:**
  - `api.__all__` only appends `why_not`; the tuple is updated in `test_public_api`, `test_public_runtime` and `run_public_acceptance`.
  - The `commands/witness.py` and `witness/cli.py` changes are additive branches.
  - `service.py` and `view.py` have no removed lines.
  - In the witness, replay and check docs, the only changes are an added CLI-table row, an added why-not exit sentence and the dropped count-of-functions wording.
  - The RF1 root-usage goldens change only by inserting `why-not`.
  - `tools/gnd_layers.json` adds `gnd.witness.why_not` (witness/lanes).
  - The RF6 dynamic inventory is extended only through the two committed successors in `DYNAMIC_SUCCESSORS`.
  - The `.claude/` and `.codex/` `gnd-export` links point to the same target, and the twins of process-phase and process-milestone are identical.
- **Anonymity:**
  - The digest test passes.
  - My probe ran the test's own digest function over every added diff line, including modified files, plus file paths, all five commit messages and the branch name. It found 0 hits.
  - The forbidden set catches the downstream names in issue #66 in several spellings: bare, camel-cased, underscore and path forms.
  - No other repository or product name that looks private appears. Context identifiers from the reporter's request (its request numbers and pin) appear paraphrased in the plan, but they are not names.
- **Private paths:** the diff and commit messages contain no `/Users/`, `/private/tmp`, usernames or worktree paths. "scratchpad" appears only as a bare word in two review dispositions.

## C3-1 — Phase commits omit the record path and two subjects are too long (hardening, high)
- **Where:**
  - The bodies of `26e36c8`, `f456930`, `b1d017d` and `ae08200`.
  - The subjects of `f456930` (74 characters) and `ae08200` (69 characters).
- **What is wrong:** `review-and-record.md:181-186` requires a subject of at most 65 characters and "the record path on its own closing line". No phase commit names its `.gnd-planning/.../00N-phase-*.md` record. The previous milestone's commits did: `ee28c50` ends `Record: .gnd-planning/...`.
- **Reproduction:** `git log --format=%B fb03739..HEAD | grep gnd-planning` returns nothing. `git log --format=%s fb03739..HEAD | awk '{print length}'` shows the lengths.
- **Fix:** history should not be rewritten. Name the record paths in the close commit or PR body, and follow the grammar in later commits.

## C3-2 — WN3 record points "below" to a census run it never records (completeness, high)
- **Where:** `004-phase-WN3.md:17-18`.
- **What is wrong:** the note says the IK6 skill census "was run after the commit (see below)". Nothing below it records that run, and neither does `evidence/WN3/final-gate.txt`. Yet the gate command lists `tests/test_il6_skill_census.py`, so it is unclear whether that file is part of the stated 2465 passed.
- **Reproduction:** `grep -n census 004-phase-WN3.md` shows only lines 8 and 17. At HEAD, my run of the census, sync and packaged files gave 68 passed.
- **Fix:** record the census command and its exit, either in a new record or in the close record.

## C3-3 — For WN1 and WN3, git history cannot show the gate came before implementation (completeness, medium)
- **Where:**
  - `26e36c8`: the WN1 gate section and the kernel are in the same commit.
  - `ae08200`: the WN3 spec, its gate and the implementation are in the same commit.
- **What is wrong:** WN2 committed its spec and gate before any code. WN1 and WN3 did not, so ordering rests on prose alone.
  - The WN3 gate's own sweep (S1–S3) ran against `src/gnd/examples/quoted_claims/*`, which is the WN3-C1 deliverable. Those files must therefore have existed before the gate was recorded.
  - Working-tree file times agree. The example files show 03:05:57 and the spec's last write 03:06:08. These times are indicative only.
- **Fix:** in the close record, state that WN1 and WN3 gate ordering cannot be checked from history. In future, commit the spec and gate first, and generate sweep inputs under scratch or evidence paths rather than `src/`.

## C3-4 — The WN1 record's digest for `why_not.py` is stale, and no later record rebinds it (completeness, high)
- **Where:** `002-phase-WN1.md` frontmatter, `src/gnd/witness/why_not.py` with digest `5f9b6a07…2f13`.
- **What is wrong:** the current file hashes to `cf406b40…0370`. The change is `b1d017d`'s one-line docstring edit, and the WN2 record mentions it in prose ("the kernel docstring points there"). The WN2 evidence list, however, does not cite the new digest.
- **Reproduction:** `shasum -a 256 src/gnd/witness/why_not.py`, then `git diff 26e36c8 b1d017d -- src/gnd/witness/why_not.py`.
- **Fix:** cite the current digest in the close record and name the edit that explains it.

## C3-5 — The anonymity test scans added files only (hardening, high)
- **Where:** `_added_files()` in `tests/test_why_not_anonymity.py` uses `--diff-filter=A`.
- **What is wrong:** WN-R8 says downstream names may not appear in any committed artifact. The test does not scan modified files (docs pages, `release-notes.md`, the skill) or commit messages, though the spec scoped it to added files. My probe found these clean today, but nothing prevents a regression.
- **Fix:** also scan the added lines of modified files over `BASE..HEAD`. Optionally scan the commit messages as well.

## C3-6 — The forbidden-token list came from a delegated gate, not from the owner (hardening, medium)
- **Where:** `001-plan-gate.md` ("the owner supplies the tokens") against WN1 gate item 2 at `notes/phase-WN1-spec.md:402-405`.
- **What is wrong:** the owner-gated plan record left the token list to the owner. The delegated gate built it from the standing rule and issue #66 instead. That gate is labelled honestly, but the owner never confirmed the list. The test's coverage claim therefore depends on the agent's choice of 4 tokens and 3 stripped forms.
- **Fix:** ask the owner at close to confirm, by digest count or privately, that the set covers every name they intend to protect, and record that confirmation.
