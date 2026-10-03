# Phase 4 — independent Codex CLI review

2026-10-03; gpt-6-astra, xhigh, ephemeral read-only harness; prompt on stdin.
Retained response below is verbatim except absolute target file links were
converted to plain repository citations, other absolute target paths replaced
with <TARGET>, Markdown trailing spaces stripped, and the intentional broken-link reproducer rendered as plain text. One reviewer is one reviewer. This is not a panel or acceptance.

Found **two blocking test-closure defects and two hardening gaps**. Scope was exactly the staged diff plus `4529d58`, against baseline `40bd8958`. One reviewer is one reviewer, not a panel.

1. **Blocking — the session test depends on unstaged P3 import setup.**
   `tests/test_runtime_preparation.py:67` imports `tests.support.v71_session_cases`. The committed conftest does not add the repository root to `sys.path`; that addition exists only in the unstaged P3 conftest. Consequently, the documented `uv run pytest` console entry cannot resolve this import from the proposed committed tree.

   Read-only reproducer:
   ```sh
   .venv/bin/python -B -c 'import sys; from pathlib import Path; r=str(Path.cwd()); sys.path=[r+"/tests"]+[p for p in sys.path if p not in ("",r)]; import tests.support.v71_session_cases'
   ```
   Observed: `ModuleNotFoundError: No module named 'tests'`. Calling the indexed test under that import environment failed at the same line, before using its fixture.

   **Repair:** use the existing `support.v71_session_cases` namespace, or explicitly include the minimal required bootstrap dependency.

2. **Blocking — the alias test requires an untracked fixture.**
   `tests/test_public_alias_schema_guards.py:74` reads `tests/fixtures/v61-phase1/import/identity.source.orm.yaml`, which is absent from the index and corpus commit.

   Reproducer:
   ```sh
   git ls-files --error-unmatch tests/fixtures/v61-phase1/import/identity.source.orm.yaml
   ```
   Observed: exit **1**; Git reports the file is unknown. The working-tree copy masks this dependency. An index-only checkout cannot complete this test’s identity branch.

   **Repair:** include that specific fixture in the reviewed closure or make this small input self-contained.

3. **Hardening — the contributor checker does not validate skill references.**
   `tests/test_contributor_preparation.py:27` checks links only in CONTRIBUTING and sample documents. Skill files receive byte/mode comparisons, without reference validation.

   **Reproducer:** append an identical `Required reference -> definitely-missing-phase4-reference.md` to both process-phase twins, then call `check_current(root)`. I reproduced this through in-memory file-read overrides: **the checker accepts it**. The existing `broken_reference` mutation targets CONTRIBUTING, so it does not exercise the approved broken-*skill*-reference story.

   **Repair:** check the bounded skill-reference closure and add a mutation that preserves twin equality while breaking a required reference.

4. **Hardening — the workflow test accepts an overwriting comparison build.**
   `tests/test_release_preparation.py:23` merely requires both directory names somewhere in the YAML.

   **Reproducer:** replace the comparison command’s `--out-dir "$PWD/candidate/comparison"` with `--out-dir "$PWD/candidate/release"`, then call `test_workflow_never_publishes_and_keeps_origins_separate()`. Reproduced in memory: **it passes**, because the artifact-upload list still mentions `candidate/comparison`.

   **Repair:** assert the build commands’ actual output destinations and prove this mutation fails. The current workflow itself uses separate destinations; this finding concerns its protective test.

I also checked:

- **36 fixture-free tests passed**, with bytecode/cache writes disabled, dirty conftest bypassed, and the writing session test deselected.
- Both examples produced **0/1/0 through CLI and API**, with exactly the expected `constraints[1]` guarded deadline failure.
- **384 scanner differential cases** matched stock ruamel behavior across safe/round-trip readers, string/byte/stream inputs, line endings and comment lengths.
- Staged whitespace checks passed. Workflow inspection found manual artifact retention without production publishing. Documentation keeps version, trials, timing, service transport, support acceptance and candidate sign-off provisional or pending.

The read-only sandbox prevented rebuilding/installing wheels, copying or mutating example files, and executing tests requiring temporary files. I did **not** independently reproduce reference-removal/change exits, session execution, the reported 96-test run, or the retained pre-fix run. No provider tools, broad suite, implementation, staging or commits were performed.
## Reproduction, triage and disposition

F1/F2: blocking test-closure defects, reproduced independently before fixing.
F1 import failed with ModuleNotFoundError under console-style sys.path; existing
`support` namespace is now used. F2 index-only controls failed for the missing
512-byte identity fixture; it is now explicitly staged. F3/F4: hardening of
this phase's own guards, reproduced independently; the two added regression
cases returned “DID NOT RAISE” before fixing. Matching broken skill references
now refuse, and parsed build commands require distinct destinations. The
focused gate and 45-test index-snapshot closure pass after these fixes.

Two CLI attempts were bounded. The attempted focused follow-up entered
orchestration instead of reviewing; stopped before a nested launch, exit 1,
no complete response. Its concise failure is retained. No convergence or
second-review opinion is claimed. One complete independent reviewer remains.
Neighbor rechecks cover shared link helper imports, both skill roots, actual
workflow destinations, fixture and console namespace closure.
