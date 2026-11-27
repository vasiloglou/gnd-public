No out-of-occurrence citation passes, and the receipt no longer claims the code infers direction. I found no blocking problem. What remains is one hardening gap inside the selected occurrence and one style note.

All four files match the SHA-256 values in the brief.

The preceding review's findings are not kept in the repository: `phase-GC2-occurrence/FINDINGS.md` is an empty template, and `phase-GC2-close` holds a different F1–F3. So I checked the question's two concerns directly, plus the span convention that C1 names, and could not match each one to an original F-number.

## 1. Findings

**F1 (hardening, not blocking). Citations inside the selected occurrence are only checked for matching text.** `src/gnd/examples/seeded_growth/README.md:83-88`. `supports_binding` now requires each cited span to sit inside the selected occurrence and to read exactly the bound value. It never requires the two roles to cite different, whole tokens. I ran the README code on a fresh copy of the example and called it with these inputs:
- `{"work":"W-1","version":"W-1"}`, with both roles citing `[start, start+3]`: returned **True**. It should be False, because one token cannot fill both roles.
- `{"work":"W","version":"1"}`, citing `[start, start+1]` and `[end-1, end]`: returned **True**. Both values are fragments of identifiers.
- `{"work":"has","version":"V-1"}`: returned **True**, binding the verb to a role.
- The reversed binding with the citations swapped as well: returned **True**.

The last case is what the new receipt describes: the agent decides direction, and the code only checks consistency. But `reversed_binding_supported: False` (README line 110), and the line "Direct, retry, defer and reversal verified" in `close-replay.md:21`, mean only that the reversal contradicts the agent's own citations.
- **What someone would see:** a record that reuses with nonsense bindings (the same span for both roles, or partial tokens) passes the example's check.
- **To reproduce:** append these calls after line 96 of the README code and run it from a copy of the example.
- **Possible fix:** require the role spans to be disjoint and to align with token boundaries.

**F2 (style, no observable consequence). The fixture never exercises the span convention.** `round-2.document.txt` is pure ASCII. Decoding it with `read_text()` gives the same offsets as NFC-normalised strict UTF-8, so neither the README nor the test (`tests/test_growth_view.py:67`) would catch code that ignored the convention. The code does follow it.

## 2. What I checked and found true

- **No out-of-occurrence pass.**
  - The bounds check `start <= left < right <= end` turned down citations of `W-2` in the second clause (False), even when mixed with an in-occurrence `V-1`.
  - It also turned down a span running one character past `end` (False).
  - The README's own W-2/V-2 assertion (line 96) runs, and fails the test if it ever stops holding.
  - The test checks independently that every recorded role span lies inside the decision span, and that the roles and bindings have the same keys (`tests/test_growth_view.py:69-72`).
- **The receipt.** `close-replay.md:28` now says "The agent interprets the direction; the executable check verifies that the role values match its citations." I searched the milestone records, the notes and `unattended-growth.md` for wording such as "which direction", "direction the text supports" or "infers direction" and found none still current. The remaining mentions are plan or panel history, or wording like "check role direction", which does not claim inference.
- **C1, judged on its three parts.**
  - **Rejects the second occurrence:** true.
  - **Uses the project span convention:** true. Both the README and the test now use `normalize("NFC", bytes.decode("utf-8"))`, which is strict decoding; see F2 for why the fixture cannot tell.
  - **Attributes semantic judgment to the agent:** true, in the README comments at lines 77-78 and in the receipt.
- **Replay.**
  - The wheel built from the working tree has SHA-256 `159165900c59…ae6da3c`, the value in the receipt.
  - The installed `verify_install.py` printed exactly the recorded lines: 229 pairs, 497 bytes with SHA-256 `b3be49…6bb23`, and 8 commands.
  - The replay pytest set gave `142 passed` (3.07s here, against 11.19s recorded; only the timing differs).
  - `tests/test_growth_view.py` alone gave `6 passed`.
- **Standing check (code fitted to its examples).**
  - The diff adds `source.index("W-2", end)` and `+3` offsets. These are literals in the worked fixture, not a matcher over structured input. They match their own document, and I found no breaking input.
  - The test's `readme.split("```python\n")` extraction was there before this change.
  - No new regular expressions were added.

## 3. What I could not check

I could not compare against the preceding review's actual F1–F3 reproductions, because they are not in the repository. I matched them to the question's stated concerns instead.

One side effect: `uv run` created `.venv` in the repository. It is gitignored, and `git status` is unchanged.

VERDICT: APPROVE
