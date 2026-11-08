# Codex review of the RR2 implementation diff (part one)

Reviewer: Codex (`gpt-6-sol`, `model_reasoning_effort=xhigh`, `--sandbox read-only`, prompt on stdin), 2026-11-08, over `git diff a000f8c1 ea236619 -- docs tests`. Dispositions are in the RR2 spec, §14. Verbatim output follows.

```text
DISPOSITION: revise

ID: I1  
SEVERITY: blocking  
LOCATION: tests/test_release_acceptance.py:229  
QUOTE: `DECLARED = tomllib.loads((ROOT / 'pyproject.toml').read_text(...))`  
PROBLEM: The new module-level read accesses the source checkout before the sandboxed installed fixture runs. This refutes RR2-C7’s claim that the acceptance run does not read the source checkout.  
FIX: Read the declared version from the fixture’s archived checkout or a retained candidate artifact outside the source checkout.

ID: I2  
SEVERITY: blocking  
LOCATION: tests/test_release_acceptance.py:338  
QUOTE: `cycle[0] == cycle[-1] and set(cycle) <= {'api', 'auth', 'search', 'util'}`  
PROBLEM: The version-7 control accepts a closed walk containing nonexistent import edges, such as `api → search → api`. T2 compares a different, normalized input, so it does not compare this T1 cycle’s exact value with 0.1.0 as the spec says.  
FIX: Assert that every adjacent pair is an import edge and compare the T1 cycle with the specified expected cycle or a control using the same input.

ID: I3  
SEVERITY: blocking  
LOCATION: tests/test_release_acceptance.py:354  
QUOTE: `zip(marked[a]['offending_facts'], marked[a]['row_novelty'])`  
PROBLEM: `zip` silently drops unmatched entries. A baseline report with an extra offending row and no matching novelty still passes the expected row comparison, leaving the required one-to-one row novelty assertion unproved.  
FIX: Assert equal lengths for each verdict before pairing rows and novelty values.

ID: I4  
SEVERITY: hardening  
LOCATION: tests/test_release_acceptance.py:377  
QUOTE: `assert check(... expected=3)['issues']`  
PROBLEM: Any load issue makes the producer mutant pass. The test does not establish that `source: fixture` is accepted with the same model when `producer` is removed, so an implementation that rejects fixture sources for another reason could pass this control.  
FIX: Add that same-model, no-producer control and require it to load successfully.

CHECKED AND FOUND TRUE

- Every new `gnd` subprocess uses the installed fixture’s sandbox prefix; the calls pass `tmp_path` as cwd.
- The 0.1.0 wheel’s SHA-256 is checked before installation.
- The diff changes no existing acceptance-test lines except imports. The file parses with Python 3.11 grammar.
- `release.yml` and `tests/test_release_preparation.py` are unchanged.
- The FU2 bullet is in the 0.2.0 section and matches the merge’s first-parent source diff. There is no `## Unreleased` heading.

COULD NOT DO

- Run T1 or T2 against retained candidate artifacts: this review is read-only and occurs before the candidate build.
codex exit=0
```
