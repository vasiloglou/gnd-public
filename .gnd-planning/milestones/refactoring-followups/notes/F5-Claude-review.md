All 11 files match the SHA-256 values in the brief.

The answer to the question is yes. The historical readers, refusal contracts, shared version dispatch and the new portable prompt evidence all keep the specified behavior. The one thing that fails is a gate the spec names: lint fails on the new test file.

## 1. Findings

**F1 — The lint gate fails on the new test file** (`tests/test_refactoring_session_contracts.py:2`)
- **What's wrong:** ruff reports `I001 Import block is un-sorted or un-formatted` for the import block on lines 2–16. The spec lists "lint" as a required check. The four changed source files pass ruff.
- **What you'd see:** `ruff check` exits non-zero on the change as it stands.
- **How to reproduce:** `uv run --offline ruff check tests/test_refactoring_session_contracts.py`. `ruff --fix` would sort it.

**F2 — The terminal-evidence test checks less than the spec asks** (`tests/test_refactoring_session_contracts.py:58-69`). This is test coverage, not a behavior defect.
- **What's wrong:** the spec says to "measure exit bands, residual evidence bytes and new paths". The test only checks that the exit code is not 0 and that the files under `run/` are unchanged. It does not pin the exit band, and it does not look for new directories or paths outside `run/`.
- **What I measured** (my own probe, checking paths under the whole experiment root):

| Version | `result.json` present | `result.json` removed |
|---|---|---|
| v2 | exit 74, "terminal runs cannot resume" | exit 74, "persisted feedback is inconsistent with the supplied contract" |
| v3 | exit 74 (exact message not captured) | exit 74, `[Errno 17] File exists` when creating the run directory |
| v7, v8 | exit 74, "terminal runs cannot resume" | exit 74, "retained run has exhausted its controller budget" |

- No version created a new path, and the retained bytes did not change, so the behavior holds.
- **Caveat:** the v3 and v2 refusals with the file removed come from something else failing (a directory collision, a mismatch check), not from a terminal-run guard. A regression that changed the band, or wrote outside `run/`, would still pass this test.

**F3 — Portable prompts are tested only for v6.** This is test coverage.
- `test_portable_session_prompt_identity` builds only v6, though the spec covers v6 through v8.
- My probe found v7 and v8 work: each exited 0, and the recorded `base_prompt_sha256` matched the portable prompt.

## 2. What I checked and found true

- **Focused tests:** `tests/test_refactoring_session_contracts.py` and `tests/test_rf1_session_pins.py` pass, 42 tests. That covers the legacy pins for versions 1–8, including the default absolute-locator prompt at `test_rf1_session_pins.py:103`.
- **Selector is closed for old versions:** adding `"prompt_format":"portable-v1"` to v1, v2, v3, v4 or v5 is refused with exit 3 ("Extra inputs are not permitted"). v6, v7 and v8 accept it.
- **Bad values are refused:** `"Portable-v1"` exits 3 with a literal error. An explicit `"absolute-v1"` is accepted and dropped when the contract is written back out. So historical contract dumps, and the session policy SHA in `session_control.py:115`, are unchanged for the default.
- **Digest comes from one read:** `_read_contract_document` hashes the same bytes it parses, from one bounded no-follow descriptor read. The two later `contract_path.read_bytes()` re-reads in `commands/exp.py` were removed. `read_session_contract` keeps its public signature by wrapping `read_session_contract_with_digest`.
- **The fixed locator is correct, not fitted to the tests:**
  - `../session.contract.json` is a literal, but the CLI always uses `root / "session.contract.json"` and `root / "candidate"` (`commands/exp.py:168-169`).
  - Every agent invoker runs with `cwd=candidate_path` (`session.py:924/949/962`), so from the agent's directory the locator points at the real contract.
  - With the same input in two different roots, the prompt hashes were identical. With one byte of whitespace changed, all three hashes differed (the test checks this, and I re-ran it).
- **Shared JSON dispatch:** `SessionEvidenceJson` comes first in the inheritance order of `AttemptFeedback`, `AttemptRecord` and `SessionResult`. It turns a `bytearray` into bytes, decodes with the same bounded decoder as the three removed copies, and passes extra arguments through to each class's own version dispatcher. The test's `Probe` subclass shows that. The contract reader still has its own stricter decoder, as the spec requires.
- **Matchers I tried:**
  - The locator f-string and the `prompt_format == "portable-v1"` branch: tried a mixed-case value and an explicit default (results above).
  - `'"wall_seconds"' in text` and `'"schema_version"' in text` in `session_contract.py`: both existed before this change, and the change does not alter them.
  - No new regular expression, split or slice was added.

## 3. What I could not check

- I did not run the full test suite or the component-inventory checker, so I can't confirm the regenerated line numbers in `dev/components/*.md` match the code.
- I did not test live Claude or Codex adapters; the probes used the stub agent from the pin helpers.
- Side effect: `uv run` created a `.venv` in the checkout. It is gitignored and does not appear in `git status`. My probe scripts are in `/tmp/f5probe`, outside the repository.

VERDICT: CHANGES_REQUESTED
