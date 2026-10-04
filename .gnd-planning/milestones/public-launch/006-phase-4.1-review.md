---
milestone: public-launch
station: phase-4.1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-4.1-review
date: 2026-10-03
gate:
  command: ".venv/bin/python -m pytest -q tests/test_documentation_tutorials.py tests/test_bookrec_tutorial.py tests/test_expense_tutorial.py tests/test_release_docs.py tests/test_release_examples.py tests/test_public_generated_examples.py tests/test_contributor_preparation.py tests/test_development_scaffold.py::test_readme_links_to_executable_getting_started --tb=short"
  exit: 0
  output: "114 passed in 32.84s"
slow_cadence:
  command: "existing repository CI selection"
  trigger: "separately configured CI after GitHub account runner availability is restored"
  reason: "GitHub did not start the last jobs due billing/spending limits; no full local or cloud suite pass is claimed"
evidence:
  - path: 005-phase-4.1-preparation.md
    sha256: f6724b695c17502a520578d3b29335768c92dc1da5ab33786950eb13d4e3cf29
  - path: notes/phase-4.1-codex-review.md
    sha256: 7673b19cfa1c6832c2fe2797931494150b1a229e01efbbbd90f27a92c9fa8cad
  - path: evidence/phase-4.1-review/evidence-sha256.json
    sha256: 5d390392f8a3e2219b820b3574faacf2710b30b1a2f55ed7012b23e90cb51b74
  - path: evidence/phase-4.1-review/implementation-sha256.json
    sha256: 6fdf0b1e4ca9e077c572e1437f6cc0060e478d2f4f93b99f68fecfda027255df
  - path: evidence/phase-4.1-review/disposition.md
    sha256: e12807b4d83f74a6c61e1cdc5d6f45f1983c9a3105ae4712ab6e4d28381c28e1
---
# Phase 4.1 — independent review and repairs

The focused gate exited 0 after the independent terminal review and four
reproduced corrections. This record discharges the terminal-review obligation
left in 005-phase-4.1-preparation.md; that earlier record and its evidence retain
their original bytes and limits. Source counterpart is 009-phase-4.1-review.md.
The user explicitly authorized the OpenAI private-repository review by answering
“yes” to the scoped permission request. No permission blocker remains.

Phase 4.1's implementation and local review are complete. Cloud CI remains
unavailable, so this does not claim final phase acceptance or Phase 4 sign-off.

## What changed

- Corrected the RAI import command in the CLI reference; the table now has 46
  actual parser-route checks instead of relying on prose presence.
- Narrowed the overview's expense claim to the supported recorded-submission
  check. The model checks facts in a snapshot; it does not prove event order.
- Made the installed documentation validator require matching wheel bytes;
  matching/different ZIP controls exercise its actual main path.
- Completed BookRec's evolution lesson: explicitly update its authored smoke
  declaration, execute both declared rows, and recheck static conformance.
  Existing GND smoke support supplies startup/exit checking. It is labeled a
  versioned testing surface, separate from the stable application API.

No packaged example, dependency or core runtime byte changed in these repairs.
Both wheel origins and the source archive retain their previously tested hashes.
The documentation and its test/tool source have new identities in the manifest.

## Gate output (verbatim summaries)

Focused command is in the header; full output is retained in evidence.

```text
114 passed in 32.84s
```

`.venv/bin/python tools/check_installed_docs.py --out <new-candidate-directory>`:

```text
100 tutorial blocks passed
Both installed wheel origins passed the documented learning paths.
```

Each wheel separately ran 100 blocks (README/dispatch 7, release 5, BookRec 49,
expense 30, API 8, walkthrough 1). Both imported from fresh installed environments
outside the checkout. Candidate files remain locally under
/private/tmp/gnd-phase41-reviewed; their three exact digests are in candidate.json.
These are focused preparation artifacts, not promoted release artifacts.

`NO_COLOR=1 .venv/bin/zensical build --strict`:

```text
Build started
No issues found
Build finished in 0.15s
```

`.venv/bin/python tools/check_docs.py site`:

```text
3521 local links/assets/anchors checked
```

`.venv/bin/ruff check tools/run_tutorials.py tools/check_docs.py tools/check_installed_docs.py tests/test_documentation_tutorials.py tests/test_bookrec_tutorial.py tests/test_expense_tutorial.py src/gnd/examples/bookrec src/gnd/examples/expense`:

```text
All checks passed!
```

## Review and criterion coverage

The independent terminal used gpt-6-sol at xhigh, read-only, prompt on stdin.
Its final findings are retained with declared path-only sanitization. It checked
manifests/artifact hashes, API signatures, models, application behavior and
publication gates; it executed read-only CLI help and a snapshot check. It did
not rerun the broad suite or a browser survey. One reviewer is one reviewer,
not a panel. The earlier model-selection refusal remains historical evidence.

The reviewer independently explained GND's purpose and developer/agent roles
(C1). Its three findings and the supplemental coverage audit's BookRec finding
were reproduced before repair. Disposition.md retains the exact classifications,
red controls, scope correction and repair evidence. The final 114-test/100-block
runs cover C2/C3 and the new gate behavior. The strict build/link checks plus
prior desktop/mobile review support C4 locally; the unchanged ownership diagram
also received a rendered inspection during this continuation. Candidate identity
and unchanged historical acceptance support C5 as preparation. The known CI
billing refusal remains a boundary, not a hidden pass or a claimed code failure.

No second terminal round was necessary: the confirmed defects had concrete
small repairs tested directly. Their fixed bytes have local execution evidence;
this record does not retroactively attach the initial opinion to the repairs.

## Refactoring review

None needed in runtime or application structure. The phase's only instrument
change closes its own missing equality assertion. The tutorial invokes existing
GND smoke support instead of implementing another process runner, and tests
consume CLI table commands rather than duplicating their strings in fixtures.
The controlled wheel test isolates external processes only to prove the gate's
negative branch; real installed runs separately validate the actual artifacts.

## Boundary — what this result does NOT establish

No final Phase 4 sign-off, Phase 5 publication, live provider/native capability,
new runtime API, real-world source truth, application ranking quality, expense
event chronology, certification or external-user trial. No cloud CI result is
invented for jobs that did not start. The reviewed macOS/Python 3.13 local lane
does not replace the required Ubuntu/other CI evidence.

## Open questions

| Obligation | Target / next action |
|---|---|
| GitHub runner billing/spending refusal | Account owner resolves availability; rerun existing documentation and acceptance CI, then append its result |
| Phase 4.1 closure and exact candidate sign-off | Complete unavailable CI evidence, then Phase 4 sign-off |
| Publication and external trials | Phase 5 / separately selected trial scope; not activated here |

## Refuted premises

A green tutorial path did not establish every retained smoke declaration was
still executable after model evolution. The BookRec red block refutes that
premise. Matching recorded hashes did not mean the validator enforced equality;
its different-wheel negative control refutes that premise. A valid final
expense snapshot does not prove event order; the operation-free model and scope
probe refute the overview's former implication. Each is corrected at its product
site, with historical records left intact.
