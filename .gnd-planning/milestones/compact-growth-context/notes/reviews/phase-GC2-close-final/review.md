The four files match the SHA-256 values in the brief. The placeholder grammar defect is gone. The receipt does name a final wheel that differs from the historical one. But the new citation check can be passed with citations from elsewhere in the document, and the receipt says more than the code checks. My verdict is changes requested.

## 1. Findings

**F1: the role citations are not tied to the occurrence being reused** (`src/gnd/examples/seeded_growth/README.md:79-87`)

- **What is wrong:** `supports_binding` only checks two things. The role names in the fact, the binding and the citations must agree, and each cited span must equal the proposed value. It never checks that a cited span falls inside the reused occurrence, `[start, end]`, which is recorded as the decision's `span`. Any other place in the document where the same text appears is accepted.
- **Input the fixtures lack:** the document at `round-2.document.txt` contains a second fact. Cite it with `role_spans = {"work": [84, 87], "version": [100, 103]}` and bindings `{"work": "W-2", "version": "V-2"}`.
- **Result:** `supports_binding` returns `True`, while the decision span is still `[59, 78]`, the "W-1 has version V-1" text. It should return `False`.
- **What someone would see:** a host that follows this example can record a reuse decision whose span cites one sentence while its bindings are taken from a different sentence.
- **Test gap:** `tests/test_growth_view.py:67-70` has the same gap. It also passes if `role_spans` is empty.
- **Reproduced:** in memory, with the predicate code taken verbatim from the README and run against the real document.

**F2: the close receipt overclaims the direction check** (`notes/close-replay.md`, first paragraph under "Close panel dispositions")

- **What is wrong:** the receipt says the example "records which direction the text supports". It actually records whether the binding agrees with the agent's own role citations. The direction is entirely the agent's claim; nothing compares it with the fact's reading (`{WorkKey} has version {VersionId}`).
- **Input:** swap the citations to `{"work": [end-3, end], "version": [start, start+3]}` and propose the reversed binding.
- **Result:** `supports_binding` returns `True`.
- **What someone would see:** with the citations fixed, the reversal assertion fails for any swap, so it tests the citations against themselves and not the text. A reader of the receipt would believe the direction was established from the text. The README comment (lines 77-78) is honest about this ("The agent attributes…"); the receipt is not.
- **Reproduced:** in memory, same method as F1.

**F3: the test does not decode the document the way the convention says** (hardening) (`tests/test_growth_view.py:68`)

- **What is wrong:** the test reads the document with `read_text()`, which uses the locale encoding and converts line endings. The declared convention, which the example follows, is strict UTF-8 decoding followed by NFC normalisation.
- **Consequence:** a document with CRLF line endings or text that is not NFC would make the test fail even though the example is correct. With today's ASCII, LF-only fixture there is no consequence, so this is hardening only.

## 2. What I checked and found true

**The placeholder defect is removed.**
- `format_map` and the lookup by object-type name are gone from the example.
- No regular expression or reading parser was added in their place.
- Role-name equality is a set comparison, so a fact where both roles have the same player works.

**Matchers I tried and the inputs I used:**
- **`supports_binding`:** swapped citations, and citations to the second occurrence (F1, F2). I ran this predicate.
- **`start + len("W-1")` and `end - len("V-1")`:** these are the agent's citations in a worked example, not a parser. They are correct for this quote. I did not try other inputs on them.
- **`verify_install.py`, which splits on fenced code blocks and keeps lines that start with `gnd `:** I only read this code; the split is unchanged in this diff, so I didn't try new inputs on it.

**The final and historical wheels are identified separately.**
- The receipt names the final wheel as `0c86af1e…`.
- The historical record `003-phase-GC2.md:48` keeps `1f388ac0…`, together with the README digest from before the close (`f28c46…`).
- The two do not conflict.
- However, the receipt never says "built at 1dc3c77a" outright; that is only implied by "finalized at 1dc3c77a". This is completeness only.

## 3. What I could not check

- **Rebuilding the wheel** to confirm `0c86af1e…`: plan mode is read-only, and a build writes output.
- **Running `verify_install.py` and the pytest command** (`142 passed`): both need writable temporary directories and an install, which read-only mode rules out. The 229 / 497 / 8 counts are taken from the receipt, not rerun.
- **The original wording of the two close-repair findings:** there is no record of them in the repository; `FINDINGS.md` has an empty table. So I judged C1 against the two questions in the brief.

VERDICT: CHANGES_REQUESTED
