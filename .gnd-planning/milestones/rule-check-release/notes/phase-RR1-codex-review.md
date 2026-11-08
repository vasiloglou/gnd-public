# Codex review of the RR1 diff (one reviewer is one reviewer)

Reviewer: Codex CLI 0.163.0, model gpt-6-sol, reasoning effort xhigh, read-only
sandbox, prompt on stdin. Reviewed bytes: branch tip aebe047c (the diff against origin/main
without planning files). The output below is verbatim and unedited. The reviewer
could not run the test suite (stated at its end), so its checks of the tests are by
reading and by small probes.

## Dispositions (recorded by the implementing session, 2026-11-07)

| Finding | Reproduced? | Class | Disposition |
|---|---|---|---|
| F1 plugin page: runtime pin before the unpublished-version route | yes: the first install block pairs the 0.1.0 runtime with the plugin from main and the route sat under Updates | hardening | fixed in 15ea4265: a paragraph before the first command and a checkout route under Updates; the 0.1.0 pin is unchanged (RL-D4) |
| F2 publication guard misses an installability claim | yes: "9.9.9 is installable from PyPI." passed (red run retained) | hardening | fixed in 15ea4265 with a mutant that was red first |
| F3 version mask matches a key that ends in gnd_version | yes: a harness test changing only prior_gnd_version passed (red run retained) | hardening | fixed in 15ea4265 with a negative control that was red first |

The fixes carry no review opinion: this was one round and the repaired bytes were
not re-reviewed.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: F1  
SEVERITY: blocking  
LOCATION: docs/marketplace-plugins.md:10  
QUOTE: `uv tool install get-nick-done==0.1.0`  
PROBLEM: After this change reaches `main`, the first-time instructions pair the 0.1.0 runtime with a 0.2.0 plugin from `main`. The correction appears only under “Updates.” Its linked tutorial clones the default branch without checking out the plugin’s commit, so it does not demonstrate the promised version match.  
FIX: Put the unpublished-version route before the first install command. Show how to identify and check out the plugin commit, then install the runtime from that checkout; retain the 0.1.0 pin for the published-runtime route.

ID: F2  
SEVERITY: hardening  
LOCATION: tests/test_release_version.py:84  
QUOTE: `(?:published|released|available on)`  
PROBLEM: The publication guard misses an installability claim. I added `Version 0.2.0 is installable from PyPI.` to its compatibility input while keeping the unpublished control; `assert_no_publication_claim` passed. The named heading, compatibility and support mutants do reach the helper and fail, but they do not cover this forbidden wording.  
FIX: Detect PyPI installability claims and add a mutant for one.

ID: F3  
SEVERITY: hardening  
LOCATION: tests/support/rf1_pins.py:143  
QUOTE: `re.compile(rb'(gnd_version\\?"\s*:\s*\\?")[^"\\]*')`  
PROBLEM: The pattern has no key boundary. It also masks `prior_gnd_version`: changing that unrelated field from `"bad"` to `"good"` produced equal normalized bytes in a direct probe. The current 16 version-bearing extract goldens match the pattern, but the shared comparator can conceal a future non-version regression.  
FIX: Match the complete `gnd_version` key, including its opening quote or escape, and add a negative control for a suffix-named field.

CHECKED AND FOUND TRUE

- The version diff changes only the requested pyproject value, editable lock entry and three manifest values. No `.github/`, `README.md`, installation pin or `src/gnd` file changed; the commit log shows no publication or tag.
- The four drift mutants reach the agreement function and are refused; its unmutated control passes. The heading, compatibility, support and missing-heading publication mutants are refused with a passing control. Both pin mutants are refused; all four real pin files yield 0.1.0.
- The twelve former notes sections retain their order and exact bodies. Their headings were demoted and capitalized. The rule-check block agrees with the main-branch reference pages and inspected implementation; the notes do not claim PyPI availability.
- All 31 old and new file hashes in `moved-digests.md` match the trees. Changed decoded gzip members retain their member sets and differ only in version text and digest values under the mechanical comparison. Test-file pin edits change digests, with no pin deleted. The RF2 reason has its separately documented sentence addition.
- `tests/test_public_distribution.py` reads the declared version and still asserts artifact names and metadata `Version`. Remaining 0.1.0 hits are published install pins, historical or retained evidence, a generated project’s own version, or the unrelated `gravis` dependency.

COULD NOT DO: I could not run pytest: system Python lacks pytest and this workspace is read-only. `uv lock --check` could not initialize its cache; the offline, no-cache attempt was also denied temporary-file creation. I therefore verified the lock’s narrow diff, but cannot attest that the command passes.
codex exit=0
