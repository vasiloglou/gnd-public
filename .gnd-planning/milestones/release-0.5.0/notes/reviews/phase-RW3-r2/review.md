<!-- Edited by review_tool.py sanitize: 4 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 13 files match the brief’s SHA-256 hashes. Four findings remain.

1. **F1 — Act 3 continues after temporary-directory creation fails.** [dossier.md:167](<repo>/.gnd-planning/milestones/release-0.5.0/evidence/RW3/dossier.md:167) uses `scratch=$(mktemp -d) && cd "$scratch"`. `set -e` does not stop on failure of the left operand of `&&`.

   In a simulation preserving the shell commands, with external operations stubbed and `mktemp` returning 23, the block continued through installation and examples and exited **0**. It should stop and return nonzero. Following this failure, real installation commands would run in the retained directory rather than a fresh scratch directory.

2. **F2 — One wrapped statement is reported twice.** [release_text.py:237](<repo>/tools/release_text.py:237) reports individual lines independently of the spanning-match pass at line 244. Add this to `docs/page.md` in the existing `PAGES` fixture:

   ```text
   This development
   checkout is not published.
   ```

   `problems()` returns both:

   ```text
   stale: docs/page.md: checkout is not published.
   stale: docs/page.md: This development checkout is not published.
   ```

   The unwrapped sentence produces one finding. Wrapping therefore violates C1’s “exactly once” requirement.

3. **F3 — Whitespace-only blank lines are discarded instead of separating paragraphs.** [release_text.py:235](<repo>/tools/release_text.py:235), together with `_paragraphs()` splitting only on `"\n\n"`, joins across legal Markdown paragraph boundaries.

   Reproduce with the page content `"This section is not\n \t\npublished.\n"`. The result is:

   ```text
   stale: docs/page.md: This section is not published.
   ```

   Markdown separates these into two paragraphs; neither contains the stale phrase. Expected: no finding.

4. **F4 — Standing guidance still becomes stale under other ordinary reflows.** [release_text.py:239](<repo>/tools/release_text.py:239) checks standing entries on individual lines, while line 248 checks only a stale phrase’s spanning lines.

   In the existing fixture, this produces two stale findings:

   ```text
   GND 0.2.0 and
   later can be used for unreleased examples.
   ```

   This produces one:

   ```text
   GND 0.2.0 and later can be used for
   unreleased
   examples.
   ```

   The same sentence unwrapped produces none. Both reflows should retain its standing classification. The round-1 F1 regression passes, but the broader reflow problem remains.

What checked successfully:

- **49 existing release-text cases passed**, invoking the test functions with test-tree writes held in memory.
- **C2:** 112 two- and three-line layouts passed, including spaces/tabs and matches at the paragraph’s beginning, end and interior. The start/end indexes selected the actual covered lines.
- `STALE` accepted bare/backticked `main`, uppercase wording and `a`/`any`; negative controls `After 2 runs` and `on main` were rejected.
- The token-route `STANDING` matcher accepted multi-digit versions and rejected extra suffixes and the wrong verb.
- All seven dossier shell blocks passed `bash -n`. A simulated comparison failure stopped act 3 with exit 19. The round-1 checkout-directory repair is correct by inspection.

I did not rerun the filesystem-writing rehearsal, full release suite or docs build. The capture-dependent command test was excluded. Publication, installation and remote operations were not executed; shell behavior was simulated with external operations stubbed.

VERDICT: CHANGES_REQUESTED