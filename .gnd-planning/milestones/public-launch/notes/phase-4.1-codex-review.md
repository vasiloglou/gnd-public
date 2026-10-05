# Phase 4.1 — independent terminal Codex review

Retained final response from one OpenAI Codex CLI reviewer, gpt-6-sol, xhigh,
ephemeral, read-only sandbox, prompt on stdin. User explicitly approved the
private-repository review in chat with “yes” after the scoped permission request.
This header was added and absolute target paths were replaced with <TARGET>;
the findings and assessment below are otherwise unedited. This is one reviewer,
not a panel or certification. See the successor phase record for reproduction
and dispositions; its fixes are not retrospectively covered by this opinion.

## Independent reader

GND lets developers express domain requirements as conceptual models, then checks supplied application facts against hard rules and advisory rules. It is useful when an application needs to reject an invalid recommendation or expense state, explain a deadline failure, or change its rules deliberately. The developer chooses and reviews the rules and writes the application behavior; a coding agent can help author models and extensions, while GND generates model-facing scaffolding and checks candidates. A pass covers only the modeled rules and supplied facts, not real-world truth or recommendation quality; the overview’s expense example is unclear about whether it checks historical order.

## Findings, in priority order

1. **Wrong command in the CLI index — definite documentation failure.** [docs/reference/cli.md:39](<TARGET>/docs/reference/cli.md:39) says `gnd import rai MODEL --out DIR`. The parser accepts `rai-orm`; the documented form exits **64** with “invalid choice: 'rai'.” Change the row to `gnd import rai-orm ...`. The tutorial runner selects marked blocks in specific pages, so this reference command is outside its 97-block check.

2. **The overview suggests an ordering check that the expense tutorial does not perform.** [README.md:10](<TARGET>/README.md:10) and [docs/index.md:20](<TARGET>/docs/index.md:20) describe approval *before* submission. The supplied expense model has no operations, and its approved population passes a snapshot check because both submission and approval facts are present. The tutorial correctly states the limit at [docs/expense/02-application.md:177](<TARGET>/docs/expense/02-application.md:177). A reader could therefore mistake a passing final state for evidence of event order. Say “approved without a recorded submission” for this example, or point explicitly to transition auditing for chronology.

3. **Wheel equality is observed but not enforced by the installed validator.** [tools/check_installed_docs.py:69](<TARGET>/tools/check_installed_docs.py:69) records each wheel’s hash and prints success after both tutorial runs, without comparing the hashes. If a later sdist rebuild yields different bytes that still pass the examples, this gate succeeds despite the candidate page’s equality claim. Add a hash equality assertion if identical wheel bytes remain a release claim. **This candidate’s two hashes do match**; this is a future gate gap, not a current artifact mismatch.

## Acceptance and limits

The retained evidence supports **C1**: the overview permits the four-sentence explanation above, subject to the ordering clarification. It supports **C2** for the tested macOS/Python 3.13 installed-wheel path: each separate wheel origin passed 97 documented blocks, and the focused tests cover hard failures, warnings, repairs, completeness, approval refusals, currency migration, and conformance drift. **C3 is partial** until the CLI command is corrected; the seven documented Python API functions match the inspected signatures and executable examples, and optional prerequisites are stated. **C4 has local support** from the strict build, 3,499 local link/asset/anchor checks, and retained sampled rendered review. **C5 is supported as candidate preparation**: I checked the retained file manifests and all three artifact hashes against the files, and the release status separates this candidate from earlier acceptance and later sign-off.

The diff changes no runtime core module. The built wheel retains the three base dependencies; Zensical is in the docs group. The workflow’s Pages deployment requires manual dispatch, a true publish input, the publication variable, and `main`. I did not rerun broad suites or conduct a new browser survey; my additional execution was limited to read-only CLI help and one expense snapshot check. GitHub Actions jobs did not start because of the recorded billing/spending-limit refusal, so there is **no CI pass**. Final Phase 4 sign-off and Phase 5 publication remain the known gates. This is one supplemental review, not a panel or certification.
