All 18 files match the SHA-256 values in the brief, so I reviewed the bytes the brief names. `git diff 67f2c0ae` of the working tree is identical to `diff.patch`.

## 1. Findings

**F1: `docs/expense/05-receipts.md:22`. A prepared-state sentence is classed as historical, and the publication check won't catch it.**
- **What is wrong:** The page says the receipts example's models "are on `main` after 0.3.1. They are not in a published package yet." The inventory marks this file as historical and to be kept (`evidence/RV1/version-inventory.txt:167`). But this text describes 0.4.0 before it's published, and the 0.4.0 notes now list this walkthrough ("Other changes").
- **Why the check misses it:** In `tools/release_text.py`, the stale-wording pattern matches "not published" but not "not in a published". The older-version test only looks at versions in `RELEASED`, and 0.3.1 is a tag only, so it never gets there.
- **Consequence:** After 0.4.0 is published, the walkthrough will still tell readers it isn't in a published package and that they must install from a checkout. `release_text.py check` will report nothing about it.
- **Reproduced:** I copied `README.md`, `docs/`, `pyproject.toml` and `tests/test_release_version.py` into a `mktemp -d` directory, then ran `uv run --frozen python tools/release_text.py --root $T publish --date 2027-01-02 --built 0123abcd --profile "macOS 27 arm64, Python 3.11, uv 0.10.10"`.
  - It exited 1 and flagged `bookrec/08-guarded-rules.md`, `bookrec/09-suggested-rules.md` (twice) and `marketplace-plugins.md`.
  - It did not flag `expense/05-receipts.md`, which still contained "after 0.3.1".
  - The bookrec pages are flagged only because they name 0.3.0. The inventory also calls them historical, which is wrong too, but the tool catches them.

**F2: `docs/release-notes.md:130`. A change from 0.3.1 is listed as new in 0.4.0.**
- **What is wrong:** The bullet "Guarded-case synthesis reports when the optional `synth` extra is missing" comes from commit `618141de`. `git merge-base --is-ancestor 618141de v0.3.1` succeeds, so the change is already in the v0.3.1 tag, and no `src/gnd/synth` commit after v0.3.1 does this. The reconciliation table itself puts it in the v0.3.0→v0.3.1 range.
- **Consequence:** Anyone on the 0.3.1 tag reads it as new in 0.4.0. The heading pointer at line 11 already sends PyPI 0.3.0 users to the 0.3.1 notes, which is the right place for it.
- **Reproduced:** by the ancestry check above (read only).

**F3 (style, no observable consequence):**
- `docs/release-notes.md:5` runs past the paragraph's 80-column wrap.
- `docs/compatibility.md:5-7` leaves "For the next version," on a short line of its own.
- At publication, `publish` regenerates both paragraphs, so this has no effect.

## 2. Checked and found true

- **C1:** `pyproject.toml`, the editable `uv.lock` entry and the three manifests all say 0.4.0. `uv lock --check` passes. The four pin files keep `==0.3.0`. The compatibility, support, plugin and notes pages say 0.4.0 is prepared and not published.
- **C2:** The two rebuild tests now use `tree_as_recorded`, which changes only `gnd_version` / inducer-version fields and SHA-256 digests that point to files that moved. The tests still compare the full file sets and every other byte.
  - The assurance golden first checks that the live version is emitted, then normalises and compares the whole document. The harness-hash check is unchanged.
  - No recorded file under `src/` changed.
- **C3:** All ten stale-page mutations remain. Each one runs a clean-copy control first, then expects its error. The publication test still expects exactly the two hand-written stale lines.
  - The reconciliation covers v0.3.0→v0.3.1 and v0.3.1→`cc4c8bf0`, including LI3–LI5, LD4–LD5 and GC1–GC4.
- **Spec gates:** The full selection passed: 168 tests across the release-version, release-text, recorded-version, marketplace, release-docs, package-description, expense receipts and two li1 test files. `tools/release_text.py check` exits 0 with "0.4.0 is not in RELEASED…".
- **Spec match:** Opening the diff file by file, only the files the spec names (M1–M9 plus the four M5 tests) changed.

## 3. Could not check, and why

- **The six-shard default lane (T7) on beast-3:** I have no access to that machine.
- **The strict docs build, structure guards and ruff:** not run.
- **Python version:** my run used CPython 3.14.3, not the recorded 3.13.18.
- **The availability check on the package index dated 2026-11-17:** this would need an external request.
- **Coverage gap that explains F1:** no test runs `publish` against the live pages any more. While 0.4.0 is prepared, `test_no_page_describes_the_state_before_publication` passes trivially, so only my manual simulation exercised the real-page path.

Side effect: `uv run` created an untracked `.venv/` in the checkout. Nothing tracked was changed.

VERDICT: CHANGES_REQUESTED
